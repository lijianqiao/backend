"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: menu.py
@DateTime: 2025-12-30 14:05:00
@Docs: 菜单 Menu 相关 Schema 定义。
"""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MenuBase(BaseModel):
    title: str = Field(..., description="菜单标题")
    name: str = Field(..., description="组件名称")
    parent_id: UUID | None = Field(None, description="父菜单ID")
    path: str | None = Field(None, description="路由路径")
    component: str | None = Field(None, description="组件路径")
    icon: str | None = Field(None, description="图标")
    sort: int = Field(0, description="排序")
    is_hidden: bool = Field(False, description="是否隐藏")
    permission: str | None = Field(None, description="权限标识")


class MenuCreate(MenuBase):
    pass


class MenuUpdate(MenuBase):
    title: str | None = None
    name: str | None = None


class MenuResponse(MenuBase):
    id: UUID
    children: list["MenuResponse"] | None = None

    model_config = ConfigDict(from_attributes=True)
