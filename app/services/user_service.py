"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: user_service.py
@DateTime: 2025-12-30 12:30:00
@Docs: 用户服务业务逻辑 (User Service Logic).
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.decorator import transactional
from app.core.exceptions import BadRequestException
from app.crud.crud_user import CRUDUser
from app.models.user import User
from app.schemas.user import UserCreate


class UserService:
    """
    用户服务类。
    通过构造函数注入 CRUDUser 实例，实现解耦。
    """

    def __init__(self, db: AsyncSession, user_crud: CRUDUser):
        self.db = db
        self.user_crud = user_crud

    @transactional()
    async def create_user(self, obj_in: UserCreate) -> User:
        user = await self.user_crud.get_by_username(self.db, username=obj_in.username)
        if user:
            raise BadRequestException(message="该用户名的用户已存在")

        user = await self.user_crud.get_by_phone(self.db, phone=obj_in.phone)
        if user:
            raise BadRequestException(message="该手机号的用户已存在")

        if obj_in.email:
            user = await self.user_crud.get_by_email(self.db, email=obj_in.email)
            if user:
                raise BadRequestException(message="该邮箱的用户已存在")

        return await self.user_crud.create(self.db, obj_in=obj_in)
