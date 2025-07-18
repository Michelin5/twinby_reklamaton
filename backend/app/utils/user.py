from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from jwt.exceptions import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import exc, select

from app.config import DefaultSettings, get_settings
from app.database.connection import get_session
from app.schemas import RegistrationForm
from app.database.models import User, Settings, Chat

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return get_settings().PWD_CONTEXT.verify(plain_password, hashed_password)


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    query = select(User).where(User.email == email)
    return await session.scalar(query)


async def register_user(session: AsyncSession, user_data: RegistrationForm) -> bool:
    try:
        user = User(**user_data.model_dump(exclude_unset=True))
        session.add(user)
        await session.flush()

        main_chat = Chat(author_id=user.id, is_main=True, name="Ментор")
        session.add(main_chat)

        await session.commit()

        return True
    except exc.IntegrityError:
        await session.rollback()

        return False


async def authenticate_user(session: AsyncSession, email: str, password: str) -> User | None:
    user = await get_user_by_email(session, email)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=60)
    settings = get_settings()
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


async def get_current_user(
    token: Annotated[str, Depends(get_settings().OAUTH2_SCHEME)],
    session: Annotated[AsyncSession, Depends(get_session)],
    settings: Annotated[DefaultSettings, Depends(get_settings)],
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    user = await get_user_by_email(session, email)
    if user is None:
        raise credentials_exception
    return user


async def get_user_settings(current_user: User, session: AsyncSession) -> Settings:
    query = select(Settings).where(Settings.user_id == current_user.id)
    settings = await session.scalar(query)
    return settings
