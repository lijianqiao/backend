"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: menu_service.py
@DateTime: 2025-12-30 14:55:00
@Docs: 菜单服务业务逻辑 (Menu Service Logic).
"""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.crud.crud_menu import menu as menu_crud
from app.models.rbac import Menu
from app.schemas.menu import MenuCreate, MenuUpdate


async def get_menus(db: AsyncSession) -> list[Menu]:
    # 可以在此实现构建树的逻辑
    return await menu_crud.get_multi(db, limit=1000)


async def create_menu(db: AsyncSession, obj_in: MenuCreate) -> Menu:
    return await menu_crud.create(db, obj_in=obj_in)


async def update_menu(db: AsyncSession, id: UUID, obj_in: MenuUpdate) -> Menu:
    menu = await menu_crud.get(db, id=id)
    if not menu:
        raise NotFoundException(message="菜单不存在")
    return await menu_crud.update(db, db_obj=menu, obj_in=obj_in)


async def delete_menu(db: AsyncSession, id: UUID) -> Menu:
    menu = await menu_crud.get(db, id=id)
    if not menu:
        raise NotFoundException(message="菜单不存在")

    deleted_menu = await menu_crud.remove(db, id=id)
    # 理论上 remove 不会返回 None (因为上面已经 check 过了，且 remove 内部也是先 get)
    # 但为了满足类型检查器，这里做非空断言或再次检查
    if not deleted_menu:
        raise NotFoundException(message="菜单删除失败")

    return deleted_menu
