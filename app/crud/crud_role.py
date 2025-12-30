"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: crud_role.py
@DateTime: 2025-12-30 14:10:00
@Docs: 角色 CRUD 操作 (Role CRUD).
"""

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.rbac import Menu, Role
from app.schemas.role import RoleCreate, RoleUpdate


class CRUDRole(CRUDBase[Role, RoleCreate, RoleUpdate]):
    async def get_by_code(self, db: AsyncSession, *, code: str) -> Role | None:
        result = await db.execute(select(Role).where(Role.code == code))
        return result.scalars().first()

    async def create(self, db: AsyncSession, *, obj_in: RoleCreate) -> Role:
        # 处理菜单关联
        menus = []
        if obj_in.menu_ids:
            # 查询所有存在的菜单
            result = await db.execute(select(Menu).where(Menu.id.in_(obj_in.menu_ids)))
            menus = list(result.scalars().all())

        db_obj = Role(name=obj_in.name, code=obj_in.code, description=obj_in.description, sort=obj_in.sort, menus=menus)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def update(self, db: AsyncSession, *, db_obj: Role, obj_in: RoleUpdate | dict[str, Any]) -> Role:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        if "menu_ids" in update_data:
            menu_ids = update_data.pop("menu_ids")
            if menu_ids is not None:
                result = await db.execute(select(Menu).where(Menu.id.in_(menu_ids)))
                menus = list(result.scalars().all())
                db_obj.menus = menus

        return await super().update(db, db_obj=db_obj, obj_in=update_data)


role = CRUDRole(Role)
