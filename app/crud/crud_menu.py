"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: crud_menu.py
@DateTime: 2025-12-30 14:15:00
@Docs: 菜单 CRUD 操作 (Menu CRUD).
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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


menu = CRUDMenu(Menu)
