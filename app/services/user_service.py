"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: user_service.py
@DateTime: 2025-12-30 12:30:00
@Docs: 用户服务业务逻辑 (User Service Logic).
"""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.decorator import transactional
from app.core.exceptions import BadRequestException, NotFoundException
from app.crud.crud_user import CRUDUser
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


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

    async def get_user(self, user_id: UUID) -> User | None:
        """
        根据 ID 获取用户。
        """
        return await self.user_crud.get(self.db, id=user_id)

    async def get_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        """
        获取用户列表 (分页)。
        """
        return await self.user_crud.get_multi(self.db, skip=skip, limit=limit)

    @transactional()
    async def update_user(self, user_id: UUID, obj_in: UserUpdate) -> User:
        """
        更新用户信息。
        """
        user = await self.user_crud.get(self.db, id=user_id)
        if not user:
            raise NotFoundException(message="用户不存在")

        # 唯一性检查
        if obj_in.username is not None and obj_in.username != user.username:
            if await self.user_crud.get_by_username(self.db, username=obj_in.username):
                raise BadRequestException(message="用户名已存在")

        if obj_in.phone is not None and obj_in.phone != user.phone:
            if await self.user_crud.get_by_phone(self.db, phone=obj_in.phone):
                raise BadRequestException(message="手机号已存在")

        if obj_in.email is not None and obj_in.email != user.email:
            if await self.user_crud.get_by_email(self.db, email=obj_in.email):
                raise BadRequestException(message="邮箱已存在")

        return await self.user_crud.update(self.db, db_obj=user, obj_in=obj_in)
