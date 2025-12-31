"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: crud_menu.py
@DateTime: 2025-12-30 14:15:00
@Docs: 菜单 CRUD 操作 (Menu CRUD).
"""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.rbac import Menu
from app.schemas.menu import MenuCreate, MenuUpdate


class CRUDMenu(CRUDBase[Menu, MenuCreate, MenuUpdate]):
    async def get_tree(self, db: AsyncSession) -> list[Menu]:
        # 获取所有顶级菜单并加载子菜单
        # 注意：递归加载在异步 SQLAlchemy 中可能需要特殊处理或 explicit join。
        # 这里简化处理，前端组装或单层加载。
        # 如果使用 lazy="selectin" 在模型中配置了children，则可以自动加载一层。
        # 为了完整树，建议获取所有 flat 数据，前端组装。
        # 或者使用 CTE 递归查询。这里演示获取所有数据。
        result = await db.execute(select(Menu).order_by(Menu.sort))
        menus = result.scalars().all()
        return list(menus)

    async def count_deleted(self, db: AsyncSession) -> int:
        """
        统计已删除菜单数。
        """
        result = await db.execute(select(func.count(Menu.id)).where(Menu.is_deleted.is_(True)))
        return result.scalar_one()

    async def get_multi_deleted_paginated(
        self, db: AsyncSession, *, page: int = 1, page_size: int = 20
    ) -> tuple[list[Menu], int]:
        """
        获取已删除菜单列表 (分页)。
        """
        total = await self.count_deleted(db)
        stmt = (
            select(Menu)
            .options(selectinload(Menu.children))
            .where(Menu.is_deleted.is_(True))
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all()), total


menu = CRUDMenu(Menu)
