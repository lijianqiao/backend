"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: role.py
@DateTime: 2025-12-30 14:00:00
@Docs: 角色 Role 相关 Schema 定义。
"""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RoleBase(BaseModel):
    name: str = Field(..., description="角色名称")
    code: str = Field(..., description="角色编码")
    description: str | None = Field(None, description="描述")
    sort: int = Field(0, description="排序")


class RoleCreate(RoleBase):
    menu_ids: list[UUID] | None = Field(None, description="关联菜单ID列表")


class RoleUpdate(RoleBase):
    name: str | None = None
    code: str | None = None
    menu_ids: list[UUID] | None = Field(None, description="关联菜单ID列表")


class RoleResponse(RoleBase):
    id: UUID
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
