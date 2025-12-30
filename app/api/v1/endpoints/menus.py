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
from app.services import menu_service

router = APIRouter()


@router.get("/", response_model=ResponseBase[list[MenuResponse]])
async def read_menus(
    db: deps.SessionDep,
    current_user: deps.CurrentUser,
) -> Any:
    """
    获取菜单列表。
    """
    menus = await menu_service.get_menus(db)
    return ResponseBase(data=menus)


@router.post("/", response_model=ResponseBase[MenuResponse])
async def create_menu(
    *,
    db: deps.SessionDep,
    menu_in: MenuCreate,
    current_user: deps.CurrentUser,
) -> Any:
    """
    创建新菜单。
    """
    menu = await menu_service.create_menu(db, obj_in=menu_in)
    return ResponseBase(data=menu)


@router.put("/{id}", response_model=ResponseBase[MenuResponse])
async def update_menu(
    *,
    db: deps.SessionDep,
    id: UUID,
    menu_in: MenuUpdate,
    current_user: deps.CurrentUser,
) -> Any:
    """
    更新菜单。
    """
    menu = await menu_service.update_menu(db, id=id, obj_in=menu_in)
    return ResponseBase(data=menu)


@router.delete("/{id}", response_model=ResponseBase[MenuResponse])
async def delete_menu(
    *,
    db: deps.SessionDep,
    id: UUID,
    current_user: deps.CurrentUser,
) -> Any:
    """
    删除菜单。
    """
    menu = await menu_service.delete_menu(db, id=id)
    return ResponseBase(data=menu)
