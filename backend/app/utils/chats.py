from fastapi import APIRouter, Depends, status, HTTPException, Body, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from typing import Annotated, Optional


from app.database.models import User, Chat
from app.schemas import ChatCreateForm


async def create_chat_utils(chat: ChatCreateForm, author: User, session: AsyncSession):
    chat = chat.model_dump()
    chat["author_id"] = author.id
    chat["is_main"] = False
    new_chat = Chat(**chat)
    session.add(new_chat)

    try:
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    return True


async def get_user_chats_utils(current_user: User, session: AsyncSession):
    query = select(Chat).where(Chat.author_id == current_user.id)
    result = await session.scalars(query)
    return result.all()