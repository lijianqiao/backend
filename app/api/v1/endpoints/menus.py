"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: menus.py
@DateTime: 2025-12-30 14:25:00
@Docs: 菜单 API 接口 (Menus API).
"""

from typing import Any
from uuid import UUID

from fastapi import APIRouter

from app.api import deps
from app.schemas.common import BatchDeleteRequest, BatchOperationResult, PaginatedResponse, ResponseBase
from app.schemas.menu import MenuCreate, MenuResponse, MenuUpdate

router = APIRouter()


@router.get("/", response_model=ResponseBase[PaginatedResponse[MenuResponse]], summary="获取菜单列表")
async def read_menus(
    current_user: deps.CurrentUser,
    menu_service: deps.MenuServiceDep,
    page: int = 1,
    page_size: int = 20,
) -> Any:
    """
    获取菜单列表 (分页)。

    查询系统菜单记录，支持分页。按排序字段排序。

    Args:
        current_user (User): 当前登录用户。
        menu_service (MenuService): 菜单服务依赖。
        page (int, optional): 页码. Defaults to 1.
        page_size (int, optional): 每页数量. Defaults to 20.

    Returns:
        ResponseBase[PaginatedResponse[MenuResponse]]: 分页后的菜单列表。
    """
    menus, total = await menu_service.get_menus_paginated(page=page, page_size=page_size)
    return ResponseBase(data=PaginatedResponse(total=total, page=page, page_size=page_size, items=menus))


@router.post("/", response_model=ResponseBase[MenuResponse], summary="创建菜单")
async def create_menu(
    *,
    menu_in: MenuCreate,
    current_user: deps.CurrentUser,
    menu_service: deps.MenuServiceDep,
) -> Any:
    """
    创建新菜单。

    创建新的系统菜单或权限节点。

    Args:
        menu_in (MenuCreate): 菜单创建数据 (标题, 路径, 类型等)。
        current_user (User): 当前登录用户。
        menu_service (MenuService): 菜单服务依赖。

    Returns:
        ResponseBase[MenuResponse]: 创建成功的菜单对象。
    """
    menu = await menu_service.create_menu(obj_in=menu_in)
    return ResponseBase(data=menu)


@router.delete("/batch", response_model=ResponseBase[BatchOperationResult], summary="批量删除菜单")
async def batch_delete_menus(
    *,
    request: BatchDeleteRequest,
    current_user: deps.CurrentUser,
    menu_service: deps.MenuServiceDep,
) -> Any:
    """
    批量删除菜单。

    支持软删除和硬删除。如果存在子菜单，将级联删除或校验（取决于具体实现策略）。

    Args:
        request (BatchDeleteRequest): 批量删除请求体 (包含 ID 列表和硬删除标志)。
        current_user (User): 当前登录用户。
        menu_service (MenuService): 菜单服务依赖。

    Returns:
        ResponseBase[BatchOperationResult]: 批量操作结果（成功数量等）。
    """
    success_count, failed_ids = await menu_service.batch_delete_menus(ids=request.ids, hard_delete=request.hard_delete)
    return ResponseBase(
        data=BatchOperationResult(
            success_count=success_count,
            failed_ids=failed_ids,
            message=f"成功删除 {success_count} 个菜单" if not failed_ids else "部分删除成功",
        )
    )


@router.put("/{id}", response_model=ResponseBase[MenuResponse], summary="更新菜单")
async def update_menu(
    *,
    id: UUID,
    menu_in: MenuUpdate,
    current_user: deps.CurrentUser,
    menu_service: deps.MenuServiceDep,
) -> Any:
    """
    更新菜单。

    更新指定 ID 的菜单信息。

    Args:
        id (UUID): 菜单 ID。
        menu_in (MenuUpdate): 菜单更新数据。
        current_user (User): 当前登录用户。
        menu_service (MenuService): 菜单服务依赖。

    Returns:
        ResponseBase[MenuResponse]: 更新后的菜单对象。
    """
    menu = await menu_service.update_menu(id=id, obj_in=menu_in)
    return ResponseBase(data=menu)


@router.delete("/{id}", response_model=ResponseBase[MenuResponse], summary="删除菜单")
async def delete_menu(
    *,
    id: UUID,
    current_user: deps.CurrentUser,
    menu_service: deps.MenuServiceDep,
) -> Any:
    """
    删除菜单。

    删除指定 ID 的菜单。

    Args:
        id (UUID): 菜单 ID。
        current_user (User): 当前登录用户。
        menu_service (MenuService): 菜单服务依赖。

    Returns:
        ResponseBase[MenuResponse]: 已删除的菜单对象信息。
    """
    menu = await menu_service.delete_menu(id=id)
    return ResponseBase(data=menu)
