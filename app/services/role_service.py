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
from app.crud.crud_role import role as role_crud
from app.models.rbac import Role
from app.schemas.role import RoleCreate, RoleUpdate


async def get_roles(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Role]:
    return await role_crud.get_multi(db, skip=skip, limit=limit)


async def create_role(db: AsyncSession, obj_in: RoleCreate) -> Role:
    role = await role_crud.get_by_code(db, code=obj_in.code)
    if role:
        raise BadRequestException(message="角色编码已存在")

    return await role_crud.create(db, obj_in=obj_in)


async def update_role(db: AsyncSession, id: UUID, obj_in: RoleUpdate) -> Role:
    role = await role_crud.get(db, id=id)
    if not role:
        raise NotFoundException(message="角色不存在")

    if obj_in.code:
        # 检查编码是否被其他角色占用
        existing_role = await role_crud.get_by_code(db, code=obj_in.code)
        if existing_role and existing_role.id != id:
            raise BadRequestException(message="角色编码被占用")

    return await role_crud.update(db, db_obj=role, obj_in=obj_in)


async def delete_role(db: AsyncSession, id: UUID) -> Role:
    role = await role_crud.get(db, id=id)
    if not role:
        raise NotFoundException(message="角色不存在")

    deleted_role = await role_crud.remove(db, id=id)
    if not deleted_role:
        raise NotFoundException(message="角色删除失败")

    return deleted_role
