"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: user_service.py
@DateTime: 2025-12-30 12:30:00
@Docs: User business logic.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException
from app.crud.crud_user import user as user_crud
from app.models.user import User
from app.schemas.user import UserCreate


async def create_user(db: AsyncSession, obj_in: UserCreate) -> User:
    user = await user_crud.get_by_username(db, username=obj_in.username)
    if user:
        raise BadRequestException(message="The user with this username already exists in the system.")

    user = await user_crud.get_by_phone(db, phone=obj_in.phone)
    if user:
        raise BadRequestException(message="The user with this phone already exists in the system.")

    if obj_in.email:
        user = await user_crud.get_by_email(db, email=obj_in.email)
        if user:
            raise BadRequestException(message="The user with this email already exists in the system.")

    return await user_crud.create(db, obj_in=obj_in)
