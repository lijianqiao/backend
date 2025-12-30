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


@router.get("/", response_model=ResponseBase[PaginatedResponse[MenuResponse]])
async def read_menus(
    current_user: deps.CurrentUser,
    menu_service: deps.MenuServiceDep,
    page: int = 1,
    page_size: int = 20,
) -> Any:
    """
    获取菜单列表 (分页)。
    """
    menus, total = await menu_service.get_menus_paginated(page=page, page_size=page_size)
    return ResponseBase(data=PaginatedResponse(total=total, page=page, page_size=page_size, items=menus))


@router.post("/", response_model=ResponseBase[MenuResponse])
async def create_menu(
    *,
    menu_in: MenuCreate,
    current_user: deps.CurrentUser,
    menu_service: deps.MenuServiceDep,
) -> Any:
    """
    创建新菜单。
    """
    menu = await menu_service.create_menu(obj_in=menu_in)
    return ResponseBase(data=menu)


@router.delete("/batch", response_model=ResponseBase[BatchOperationResult])
async def batch_delete_menus(
    *,
    request: BatchDeleteRequest,
    current_user: deps.CurrentUser,
    menu_service: deps.MenuServiceDep,
) -> Any:
    """
    批量删除菜单。
    """
    success_count, failed_ids = await menu_service.batch_delete_menus(ids=request.ids, hard_delete=request.hard_delete)
    return ResponseBase(
        data=BatchOperationResult(
            success_count=success_count,
            failed_ids=failed_ids,
            message=f"成功删除 {success_count} 个菜单" if not failed_ids else "部分删除成功",
        )
    )


@router.put("/{id}", response_model=ResponseBase[MenuResponse])
async def update_menu(
    *,
    id: UUID,
    menu_in: MenuUpdate,
    current_user: deps.CurrentUser,
    menu_service: deps.MenuServiceDep,
) -> Any:
    """
    更新菜单。
    """
    menu = await menu_service.update_menu(id=id, obj_in=menu_in)
    return ResponseBase(data=menu)


@router.delete("/{id}", response_model=ResponseBase[MenuResponse])
async def delete_menu(
    *,
    id: UUID,
    current_user: deps.CurrentUser,
    menu_service: deps.MenuServiceDep,
) -> Any:
    """
    删除菜单。
    """
    menu = await menu_service.delete_menu(id=id)
    return ResponseBase(data=menu)
