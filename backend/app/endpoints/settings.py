from app.database.connection import get_session

from fastapi import APIRouter, Depends, status, HTTPException, Security
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from fastapi import APIRouter, Body, Security
from app.utils.user import get_current_user, User
from app.schemas.settings import SettingsDebug
from app.utils.settings import (
    update_email,
    update_password,
    verify_password,
    get_settings_debug,
)
from app.utils.settings import (
    EmailUpdateForm,
    PasswordUpdateForm,
    )
from uuid import UUID
api_router = APIRouter(
    prefix="/settings",
    tags=["Settings"]
)


@api_router.put(
    "/update_password",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Could not validate credentials",
        }
    },
)
async def Update_password(
    updated_password: Annotated[PasswordUpdateForm, Body()],
    session: Annotated[AsyncSession, Depends(get_session)],
    user: Annotated[User, Security(get_current_user)],
) -> str:
    
    try:
        ans  = verify_password(updated_password.oldpassword,user.password)
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="verify mistake"
        )
    if (ans):
        try:
            result = await update_password(user.id,updated_password.password, session)
            return "Password updated"
        except:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="update_pass"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wrong password"
        )
    
    
@api_router.put(
    "/update_email",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Could not validate credentials",
        }
    },
    
)
async def Update_email(
    updated_email: Annotated[EmailUpdateForm, Body()],
    session: Annotated[AsyncSession, Depends(get_session)],
    user: Annotated[User, Security(get_current_user)]
) -> str:
    ans  = verify_password(updated_email.password,user.password)
    if (ans):
        result = await update_email(user.id,updated_email.email, session)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No task with with this ID",
            )
        return {"message": "Email updated"}
    else:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wrong  password",
            )


@api_router.get(
    "/get_settings_debug",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Could not validate credentials",
        }
    },
)
async def get_user_settings_debug(session: Annotated[AsyncSession, Depends(get_session)],
                                  ) -> list[SettingsDebug]:
    result = await get_settings_debug(session)
    return result