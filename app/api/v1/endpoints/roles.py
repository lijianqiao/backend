"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: roles.py
@DateTime: 2025-12-30 14:20:00
@Docs: 角色 API 接口 (Roles API).
"""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends

from app.api import deps
from app.schemas.common import BatchDeleteRequest, BatchOperationResult, PaginatedResponse, ResponseBase
from app.schemas.role import RoleCreate, RoleResponse, RoleUpdate

router = APIRouter()


@router.get("/", response_model=ResponseBase[PaginatedResponse[RoleResponse]], summary="获取角色列表")
async def read_roles(
    role_service: deps.RoleServiceDep,
    current_user: deps.CurrentUser,
    _: deps.User = Depends(deps.require_permissions(["role:list"])),
    page: int = 1,
    page_size: int = 20,
) -> Any:
    """
    获取角色列表 (分页)。

    查询系统角色记录，支持分页。

    Args:
        role_service (RoleService): 角色服务依赖。
        current_user (User): 当前登录用户。
        page (int, optional): 页码. Defaults to 1.
        page_size (int, optional): 每页数量. Defaults to 20.

    Returns:
        ResponseBase[PaginatedResponse[RoleResponse]]: 分页后的角色列表。
    """
    roles, total = await role_service.get_roles_paginated(page=page, page_size=page_size)
    return ResponseBase(data=PaginatedResponse(total=total, page=page, page_size=page_size, items=roles))


@router.post("/", response_model=ResponseBase[RoleResponse], summary="创建角色")
async def create_role(
    *,
    role_in: RoleCreate,
    current_user: deps.CurrentUser,
    _: deps.User = Depends(deps.require_permissions(["role:create"])),
    role_service: deps.RoleServiceDep,
) -> Any:
    """
    创建新角色。

    创建新的系统角色。

    Args:
        role_in (RoleCreate): 角色创建数据 (名称, 标识, 描述等)。
        current_user (User): 当前登录用户。
        role_service (RoleService): 角色服务依赖。

    Returns:
        ResponseBase[RoleResponse]: 创建成功的角色对象。
    """
    role = await role_service.create_role(obj_in=role_in)
    return ResponseBase(data=role)


@router.delete("/batch", response_model=ResponseBase[BatchOperationResult], summary="批量删除角色")
async def batch_delete_roles(
    *,
    request: BatchDeleteRequest,
    current_user: deps.CurrentUser,
    _: deps.User = Depends(deps.require_permissions(["role:delete"])),
    role_service: deps.RoleServiceDep,
) -> Any:
    """
    批量删除角色。

    支持软删除和硬删除。

    Args:
        request (BatchDeleteRequest): 批量删除请求体 (包含 ID 列表和硬删除标志)。
        current_user (User): 当前登录用户。
        role_service (RoleService): 角色服务依赖。

    Returns:
        ResponseBase[BatchOperationResult]: 批量操作结果（成功数量等）。
    """
    success_count, failed_ids = await role_service.batch_delete_roles(ids=request.ids, hard_delete=request.hard_delete)
    return ResponseBase(
        data=BatchOperationResult(
            success_count=success_count,
            failed_ids=failed_ids,
            message=f"成功删除 {success_count} 个角色" if not failed_ids else "部分删除成功",
        )
    )


@router.put("/{id}", response_model=ResponseBase[RoleResponse], summary="更新角色")
async def update_role(
    *,
    id: UUID,
    role_in: RoleUpdate,
    current_user: deps.CurrentUser,
    _: deps.User = Depends(deps.require_permissions(["role:update"])),
    role_service: deps.RoleServiceDep,
) -> Any:
    """
    更新角色。

    更新指定 ID 的角色信息。

    Args:
        id (UUID): 角色 ID。
        role_in (RoleUpdate): 角色更新数据。
        current_user (User): 当前登录用户。
        role_service (RoleService): 角色服务依赖。

    Returns:
        ResponseBase[RoleResponse]: 更新后的角色对象。
    """
    role = await role_service.update_role(id=id, obj_in=role_in)
    return ResponseBase(data=role)


@router.get("/recycle-bin", response_model=ResponseBase[PaginatedResponse[RoleResponse]], summary="获取角色回收站列表")
async def get_recycle_bin(
    *,
    page: int = 1,
    page_size: int = 20,
    active_superuser: deps.User = Depends(deps.get_current_active_superuser),
    _: deps.User = Depends(deps.require_permissions(["role:recycle"])),
    role_service: deps.RoleServiceDep,
) -> Any:
    """
    获取已删除的角色列表 (回收站)。
    仅限超级管理员。
    """
    roles, total = await role_service.get_deleted_roles(page=page, page_size=page_size)
    return ResponseBase(data=PaginatedResponse(total=total, page=page, page_size=page_size, items=roles))


@router.delete("/{id}", response_model=ResponseBase[RoleResponse], summary="删除角色")
async def delete_role(
    *,
    id: UUID,
    active_superuser: deps.User = Depends(deps.get_current_active_superuser),
    _: deps.User = Depends(deps.require_permissions(["role:delete"])),
    role_service: deps.RoleServiceDep,
) -> Any:
    """
    删除角色 (软删除)。

    Args:
        id (UUID): 角色 ID。
        active_superuser (User): 当前登录超级用户。
        role_service (RoleService): 角色服务依赖。

    Returns:
        ResponseBase[RoleResponse]: 删除后的角色对象。
    """
    role = await role_service.delete_role(id=id)
    return ResponseBase(data=role)


@router.post("/{id}/restore", response_model=ResponseBase[RoleResponse], summary="恢复已删除角色")
async def restore_role(
    *,
    id: UUID,
    active_superuser: deps.User = Depends(deps.get_current_active_superuser),
    _: deps.User = Depends(deps.require_permissions(["role:restore"])),
    role_service: deps.RoleServiceDep,
) -> Any:
    """
    恢复已删除角色。

    从回收站中恢复指定角色。
    需要超级管理员权限。
    """
    role = await role_service.restore_role(id=id)
    return ResponseBase(data=role, message="角色恢复成功")
