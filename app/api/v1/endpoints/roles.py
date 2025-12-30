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
from app.schemas.common import BatchDeleteRequest, BatchOperationResult, PaginatedResponse, ResponseBase
from app.schemas.role import RoleCreate, RoleResponse, RoleUpdate

router = APIRouter()


@router.get("/", response_model=ResponseBase[PaginatedResponse[RoleResponse]])
async def read_roles(
    role_service: deps.RoleServiceDep,
    current_user: deps.CurrentUser,
    page: int = 1,
    page_size: int = 20,
) -> Any:
    """
    获取角色列表 (分页)。
    """
    roles, total = await role_service.get_roles_paginated(page=page, page_size=page_size)
    return ResponseBase(data=PaginatedResponse(total=total, page=page, page_size=page_size, items=roles))


@router.post("/", response_model=ResponseBase[RoleResponse])
async def create_role(
    *,
    role_in: RoleCreate,
    current_user: deps.CurrentUser,
    role_service: deps.RoleServiceDep,
) -> Any:
    """
    创建新角色。
    """
    role = await role_service.create_role(obj_in=role_in)
    return ResponseBase(data=role)


@router.delete("/batch", response_model=ResponseBase[BatchOperationResult])
async def batch_delete_roles(
    *,
    request: BatchDeleteRequest,
    current_user: deps.CurrentUser,
    role_service: deps.RoleServiceDep,
) -> Any:
    """
    批量删除角色。
    """
    success_count, failed_ids = await role_service.batch_delete_roles(ids=request.ids, hard_delete=request.hard_delete)
    return ResponseBase(
        data=BatchOperationResult(
            success_count=success_count,
            failed_ids=failed_ids,
            message=f"成功删除 {success_count} 个角色" if not failed_ids else "部分删除成功",
        )
    )


@router.put("/{id}", response_model=ResponseBase[RoleResponse])
async def update_role(
    *,
    id: UUID,
    role_in: RoleUpdate,
    current_user: deps.CurrentUser,
    role_service: deps.RoleServiceDep,
) -> Any:
    """
    更新角色。
    """
    role = await role_service.update_role(id=id, obj_in=role_in)
    return ResponseBase(data=role)


@router.delete("/{id}", response_model=ResponseBase[RoleResponse])
async def delete_role(
    *,
    id: UUID,
    current_user: deps.CurrentUser,
    role_service: deps.RoleServiceDep,
) -> Any:
    """
    删除角色。
    """
    role = await role_service.delete_role(id=id)
    return ResponseBase(data=role)
