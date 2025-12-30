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
from app.core.exceptions import BadRequestException
from app.crud.crud_menu import menu as menu_crud
from app.schemas.common import ResponseBase
from app.schemas.menu import MenuCreate, MenuResponse, MenuUpdate

router = APIRouter()


@router.get("/", response_model=ResponseBase[list[MenuResponse]])
async def read_menus(
    db: deps.SessionDep,
    current_user: deps.CurrentUser,
) -> Any:
    """
    获取菜单列表 (树形结构需前端组装或实现递归 Schema).
    """
    # 简单获取所有
    menus = await menu_crud.get_multi(db, limit=1000)
    # 可以在这里通过 utils 实现 build_tree，暂时直接返回列表
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
    menu = await menu_crud.create(db, obj_in=menu_in)
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
    menu = await menu_crud.get(db, id=id)
    if not menu:
        raise BadRequestException(message="菜单不存在")

    menu = await menu_crud.update(db, db_obj=menu, obj_in=menu_in)
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
    menu = await menu_crud.get(db, id=id)
    if not menu:
        raise BadRequestException(message="菜单不存在")

    menu = await menu_crud.remove(db, id=id)
    return ResponseBase(data=menu)
