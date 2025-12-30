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
from app.crud.crud_menu import CRUDMenu
from app.models.rbac import Menu
from app.schemas.menu import MenuCreate, MenuUpdate


class MenuService:
    """
    菜单服务类。
    """

    def __init__(self, db: AsyncSession, menu_crud: CRUDMenu):
        self.db = db
        self.menu_crud = menu_crud

    async def get_menus(self) -> list[Menu]:
        return await self.menu_crud.get_multi(self.db, limit=1000)

    async def create_menu(self, obj_in: MenuCreate) -> Menu:
        return await self.menu_crud.create(self.db, obj_in=obj_in)

    async def update_menu(self, id: UUID, obj_in: MenuUpdate) -> Menu:
        menu = await self.menu_crud.get(self.db, id=id)
        if not menu:
            raise NotFoundException(message="菜单不存在")
        return await self.menu_crud.update(self.db, db_obj=menu, obj_in=obj_in)

    async def delete_menu(self, id: UUID) -> Menu:
        menu = await self.menu_crud.get(self.db, id=id)
        if not menu:
            raise NotFoundException(message="菜单不存在")

        deleted_menu = await self.menu_crud.remove(self.db, id=id)
        if not deleted_menu:
            raise NotFoundException(message="菜单删除失败")

        return deleted_menu
