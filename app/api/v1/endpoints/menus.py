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
from app.schemas.common import ResponseBase
from app.schemas.menu import MenuCreate, MenuResponse, MenuUpdate

router = APIRouter()


@router.get("/", response_model=ResponseBase[list[MenuResponse]])
async def read_menus(
    current_user: deps.CurrentUser,
    menu_service: deps.MenuServiceDep,
) -> Any:
    """
    获取菜单列表。
    """
    menus = await menu_service.get_menus()
    return ResponseBase(data=menus)


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
