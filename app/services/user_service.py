"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: user_service.py
@DateTime: 2025-12-30 12:30:00
@Docs: 用户服务业务逻辑 (User Service Logic).
"""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
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
        # 1. 检查用户名
        user = await self.user_crud.get_by_username_include_deleted(self.db, username=obj_in.username)
        if user:
            if user.is_deleted:
                raise BadRequestException(message="该用户名已被注销/删除，请联系管理员恢复")
            raise BadRequestException(message="该用户名的用户已存在")

        # 2. 检查手机号
        user = await self.user_crud.get_by_phone_include_deleted(self.db, phone=obj_in.phone)
        if user:
            if user.is_deleted:
                raise BadRequestException(message="该手机号已被注销/删除，请联系管理员恢复")
            raise BadRequestException(message="该手机号的用户已存在")

        # 3. 检查邮箱
        if obj_in.email:
            user = await self.user_crud.get_by_email_include_deleted(self.db, email=obj_in.email)
            if user:
                if user.is_deleted:
                    raise BadRequestException(message="该邮箱已被注销/删除，请联系管理员恢复")
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

    async def get_users_paginated(self, page: int = 1, page_size: int = 20) -> tuple[list[User], int]:
        """
        获取分页用户列表。

        Returns:
            (users, total): 用户列表和总数
        """
        return await self.user_crud.get_multi_paginated(self.db, page=page, page_size=page_size)

    async def get_deleted_users(self, page: int = 1, page_size: int = 20) -> tuple[list[User], int]:
        """
        获取已删除用户列表 (回收站 - 分页)。
        """
        return await self.user_crud.get_multi_deleted_paginated(self.db, page=page, page_size=page_size)

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

    @transactional()
    async def change_password(self, user_id: UUID, old_password: str, new_password: str) -> User:
        """
        用户修改自己的密码 (需验证旧密码)。
        """
        user = await self.user_crud.get(self.db, id=user_id)
        if not user:
            raise NotFoundException(message="用户不存在")

        if not security.verify_password(old_password, user.password):
            raise BadRequestException(message="旧密码错误")

        # 传递明文密码，CRUD 层会处理哈希
        return await self.user_crud.update(self.db, db_obj=user, obj_in={"password": new_password})

    @transactional()
    async def reset_password(self, user_id: UUID, new_password: str) -> User:
        """
        管理员重置用户密码 (无需验证旧密码)。
        """
        user = await self.user_crud.get(self.db, id=user_id)
        if not user:
            raise NotFoundException(message="用户不存在")

        # 传递明文密码，CRUD 层会处理哈希
        return await self.user_crud.update(self.db, db_obj=user, obj_in={"password": new_password})

    @transactional()
    async def batch_delete_users(self, ids: list[UUID], hard_delete: bool = False) -> tuple[int, list[UUID]]:
        """
        批量删除用户。

        Args:
            ids: 要删除的用户 ID 列表
            hard_delete: 是否硬删除

        Returns:
            (success_count, failed_ids): 成功数量和失败的 ID 列表
        """
        return await self.user_crud.batch_remove(self.db, ids=ids, hard_delete=hard_delete)

    @transactional()
    async def restore_user(self, id: UUID) -> User:
        """
        恢复已删除用户。
        """
        user = await self.user_crud.restore(self.db, id=id)
        if not user:
            raise NotFoundException(message="用户不存在")
        return user
