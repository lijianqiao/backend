"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: role_service.py
@DateTime: 2025-12-30 14:50:00
@Docs: 角色服务业务逻辑 (Role Service Logic).
"""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import invalidate_cache
from app.core.decorator import transactional
from app.core.exceptions import BadRequestException, NotFoundException
from app.crud.crud_role import CRUDRole
from app.models.rbac import Role
from app.schemas.role import RoleCreate, RoleResponse, RoleUpdate


class RoleService:
    """
    角色服务类。
    """

    def __init__(self, db: AsyncSession, role_crud: CRUDRole):
        self.db = db
        self.role_crud = role_crud

        # transactional() 将在 commit 后执行这些任务（用于缓存失效等）
        self._post_commit_tasks: list = []

    def _invalidate_permissions_cache_after_commit(self) -> None:
        async def _task() -> None:
            await invalidate_cache("v1:user:permissions:*")

        self._post_commit_tasks.append(_task)

    async def get_roles(self, skip: int = 0, limit: int = 100) -> list[Role]:
        return await self.role_crud.get_multi(self.db, skip=skip, limit=limit)

    async def get_roles_paginated(self, page: int = 1, page_size: int = 20) -> tuple[list[Role], int]:
        """
        获取分页角色列表。
        """
        return await self.role_crud.get_multi_paginated(self.db, page=page, page_size=page_size)

    async def get_deleted_roles(self, page: int = 1, page_size: int = 20) -> tuple[list[Role], int]:
        """
        获取已删除角色列表 (回收站 - 分页)。
        """
        return await self.role_crud.get_multi_deleted_paginated(self.db, page=page, page_size=page_size)

    @transactional()
    async def create_role(self, obj_in: RoleCreate) -> Role:
        existing_role = await self.role_crud.get_by_code(self.db, code=obj_in.code)
        if existing_role:
            raise BadRequestException(message="角色编码已存在")

        role = await self.role_crud.create(self.db, obj_in=obj_in)
        self._invalidate_permissions_cache_after_commit()
        return role

    @transactional()
    async def update_role(self, id: UUID, obj_in: RoleUpdate) -> Role:
        role = await self.role_crud.get(self.db, id=id)
        if not role:
            raise NotFoundException(message="角色不存在")

        if obj_in.code:
            existing_role = await self.role_crud.get_by_code(self.db, code=obj_in.code)
            if existing_role and existing_role.id != id:
                raise BadRequestException(message="角色编码被占用")

        updated = await self.role_crud.update(self.db, db_obj=role, obj_in=obj_in)
        self._invalidate_permissions_cache_after_commit()
        return updated

    @transactional()
    async def delete_role(self, id: UUID) -> RoleResponse:
        role = await self.role_crud.get(self.db, id=id)
        if not role:
            raise NotFoundException(message="角色不存在")

        deleted_role = await self.role_crud.remove(self.db, id=id)
        if not deleted_role:
            raise NotFoundException(message="角色删除失败")

        self._invalidate_permissions_cache_after_commit()

        return RoleResponse(
            id=deleted_role.id,
            name=deleted_role.name,
            code=deleted_role.code,
            description=deleted_role.description,
            sort=deleted_role.sort,
            is_active=deleted_role.is_active,
            is_deleted=deleted_role.is_deleted,
            created_at=deleted_role.created_at,
            updated_at=deleted_role.updated_at,
        )

    @transactional()
    async def batch_delete_roles(self, ids: list[UUID], hard_delete: bool = False) -> tuple[int, list[UUID]]:
        """
        批量删除角色。
        """
        result = await self.role_crud.batch_remove(self.db, ids=ids, hard_delete=hard_delete)
        self._invalidate_permissions_cache_after_commit()
        return result

    @transactional()
    async def restore_role(self, id: UUID) -> Role:
        """
        恢复已删除角色。
        """
        role = await self.role_crud.restore(self.db, id=id)
        if not role:
            raise NotFoundException(message="角色不存在")

        self._invalidate_permissions_cache_after_commit()
        return role
