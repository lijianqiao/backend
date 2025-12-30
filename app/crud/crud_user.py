"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: crud_user.py
@DateTime: 2025-12-30 12:15:00
@Docs: User CRUD operations.
"""

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_username(self, db: AsyncSession, *, username: str) -> User | None:
        """
        根据用户名查询用户 (排除已软删除)。
        """
        result = await db.execute(select(User).where(User.username == username, User.is_deleted.is_(False)))
        return result.scalars().first()

    async def get_by_email(self, db: AsyncSession, *, email: str) -> User | None:
        """
        根据邮箱查询用户 (排除已软删除)。
        """
        result = await db.execute(select(User).where(User.email == email, User.is_deleted.is_(False)))
        return result.scalars().first()

    async def get_by_phone(self, db: AsyncSession, *, phone: str) -> User | None:
        """
        根据手机号查询用户 (排除已软删除)。
        """
        result = await db.execute(select(User).where(User.phone == phone, User.is_deleted.is_(False)))
        return result.scalars().first()

    async def count_active(self, db: AsyncSession) -> int:
        """
        统计活跃用户数。
        """
        result = await db.execute(
            select(func.count(User.id)).where(User.is_active.is_(True), User.is_deleted.is_(False))
        )
        return result.scalar_one()

    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        db_obj = User(
            username=obj_in.username,
            email=obj_in.email,
            phone=obj_in.phone,
            nickname=obj_in.nickname,
            gender=obj_in.gender,
            is_active=obj_in.is_active,
            is_superuser=obj_in.is_superuser,
            password=get_password_hash(obj_in.password),
        )
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def update(self, db: AsyncSession, *, db_obj: User, obj_in: UserUpdate | dict[str, Any]) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        if "password" in update_data and update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            update_data["password"] = hashed_password

        return await super().update(db, db_obj=db_obj, obj_in=update_data)


user = CRUDUser(User)
