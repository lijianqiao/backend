"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: menu_service.py
@DateTime: 2025-12-30 14:55:00
@Docs: 菜单服务业务逻辑 (Menu Service Logic).
"""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.decorator import transactional
from app.core.exceptions import NotFoundException
from app.crud.crud_menu import CRUDMenu
from app.models.rbac import Menu
from app.schemas.menu import MenuCreate, MenuResponse, MenuUpdate


class MenuService:
    """
    菜单服务类。
    """

    def __init__(self, db: AsyncSession, menu_crud: CRUDMenu):
        self.db = db
        self.menu_crud = menu_crud

    async def get_menus(self) -> list[Menu]:
        return await self.menu_crud.get_multi(self.db, limit=1000)

    async def get_menus_paginated(self, page: int = 1, page_size: int = 20) -> tuple[list[Menu], int]:
        """
        获取分页菜单列表。
        """
        return await self.menu_crud.get_multi_paginated(self.db, page=page, page_size=page_size)

    @transactional()
    async def create_menu(self, obj_in: MenuCreate) -> Menu:
        return await self.menu_crud.create(self.db, obj_in=obj_in)

    @transactional()
    async def update_menu(self, id: UUID, obj_in: MenuUpdate) -> Menu:
        menu = await self.menu_crud.get(self.db, id=id)
        if not menu:
            raise NotFoundException(message="菜单不存在")
        return await self.menu_crud.update(self.db, db_obj=menu, obj_in=obj_in)

    @transactional()
    async def delete_menu(self, id: UUID) -> MenuResponse:
        menu = await self.menu_crud.get(self.db, id=id)
        if not menu:
            raise NotFoundException(message="菜单不存在")

        deleted_menu = await self.menu_crud.remove(self.db, id=id)
        if not deleted_menu:
            raise NotFoundException(message="菜单删除失败")

        # 手动构建响应，避免访问 deleted_menu.children 触发 implicit IO (MissingGreenlet)
        # 且删除后的对象 children 应为空
        return MenuResponse(
            id=deleted_menu.id,
            title=deleted_menu.title,
            name=deleted_menu.name,
            sort=deleted_menu.sort,
            parent_id=deleted_menu.parent_id,
            path=deleted_menu.path,
            component=deleted_menu.component,
            icon=deleted_menu.icon,
            is_hidden=deleted_menu.is_hidden,
            permission=deleted_menu.permission,
            is_deleted=deleted_menu.is_deleted,
            created_at=deleted_menu.created_at,
            updated_at=deleted_menu.updated_at,
            children=[],
        )

    @transactional()
    async def batch_delete_menus(self, ids: list[UUID], hard_delete: bool = False) -> tuple[int, list[UUID]]:
        """
        批量删除菜单。
        """
        return await self.menu_crud.batch_remove(self.db, ids=ids, hard_delete=hard_delete)
