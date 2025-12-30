"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: role_service.py
@DateTime: 2025-12-30 14:50:00
@Docs: 角色服务业务逻辑 (Role Service Logic).
"""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, NotFoundException
from app.crud.crud_role import CRUDRole
from app.models.rbac import Role
from app.schemas.role import RoleCreate, RoleUpdate


class RoleService:
    """
    角色服务类。
    """

    def __init__(self, db: AsyncSession, role_crud: CRUDRole):
        self.db = db
        self.role_crud = role_crud

    async def get_roles(self, skip: int = 0, limit: int = 100) -> list[Role]:
        return await self.role_crud.get_multi(self.db, skip=skip, limit=limit)

    async def create_role(self, obj_in: RoleCreate) -> Role:
        existing_role = await self.role_crud.get_by_code(self.db, code=obj_in.code)
        if existing_role:
            raise BadRequestException(message="角色编码已存在")

        return await self.role_crud.create(self.db, obj_in=obj_in)

    async def update_role(self, id: UUID, obj_in: RoleUpdate) -> Role:
        role = await self.role_crud.get(self.db, id=id)
        if not role:
            raise NotFoundException(message="角色不存在")

        if obj_in.code:
            existing_role = await self.role_crud.get_by_code(self.db, code=obj_in.code)
            if existing_role and existing_role.id != id:
                raise BadRequestException(message="角色编码被占用")

        return await self.role_crud.update(self.db, db_obj=role, obj_in=obj_in)

    async def delete_role(self, id: UUID) -> Role:
        role = await self.role_crud.get(self.db, id=id)
        if not role:
            raise NotFoundException(message="角色不存在")

        deleted_role = await self.role_crud.remove(self.db, id=id)
        if not deleted_role:
            raise NotFoundException(message="角色删除失败")

        return deleted_role
