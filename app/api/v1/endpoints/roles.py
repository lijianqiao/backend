"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: roles.py
@DateTime: 2025-12-30 14:20:00
@Docs: 角色 API 接口 (Roles API).
"""

from typing import Any
from uuid import UUID

from fastapi import APIRouter

from app.api import deps
from app.core.exceptions import BadRequestException
from app.crud.crud_role import role as role_crud
from app.schemas.common import ResponseBase
from app.schemas.role import RoleCreate, RoleResponse, RoleUpdate

router = APIRouter()


@router.get("/", response_model=ResponseBase[list[RoleResponse]])
async def read_roles(
    db: deps.SessionDep,
    current_user: deps.CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    获取角色列表。
    """
    roles = await role_crud.get_multi(db, skip=skip, limit=limit)
    return ResponseBase(data=roles)


@router.post("/", response_model=ResponseBase[RoleResponse])
async def create_role(
    *,
    db: deps.SessionDep,
    role_in: RoleCreate,
    current_user: deps.CurrentUser,
) -> Any:
    """
    创建新角色。
    需要超级管理员权限或相应权限。
    """
    # 简单检查 code 是否重复
    role = await role_crud.get_by_code(db, code=role_in.code)
    if role:
        raise BadRequestException(message="角色编码已存在")

    role = await role_crud.create(db, obj_in=role_in)
    return ResponseBase(data=role)


@router.put("/{id}", response_model=ResponseBase[RoleResponse])
async def update_role(
    *,
    db: deps.SessionDep,
    id: UUID,
    role_in: RoleUpdate,
    current_user: deps.CurrentUser,
) -> Any:
    """
    更新角色。
    """
    role = await role_crud.get(db, id=id)
    if not role:
        raise BadRequestException(message="角色不存在")

    role = await role_crud.update(db, db_obj=role, obj_in=role_in)
    return ResponseBase(data=role)


@router.delete("/{id}", response_model=ResponseBase[RoleResponse])
async def delete_role(
    *,
    db: deps.SessionDep,
    id: UUID,
    current_user: deps.CurrentUser,
) -> Any:
    """
    删除角色。
    """
    role = await role_crud.get(db, id=id)
    if not role:
        raise BadRequestException(message="角色不存在")

    role = await role_crud.remove(db, id=id)
    return ResponseBase(data=role)
