"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: dashboard.py
@DateTime: 2025-12-30 22:05:00
@Docs: 仪表盘 Dashboard 相关 Schema 定义。
"""

from typing import Any

from pydantic import BaseModel, ConfigDict


class LoginLogSimple(BaseModel):
    """
    简化的登录日志展示 (用于仪表盘列表).
    """

    id: Any
    username: str
    ip: str | None = None
    address: str | None = None
    browser: str | None = None
    os: str | None = None
    status: bool
    msg: str | None = None
    created_at: Any

    model_config = ConfigDict(from_attributes=True)


class DashboardStats(BaseModel):
    """
    仪表盘聚合统计数据。
    """

    # 核心计数
    total_users: int
    active_users: int
    total_roles: int
    total_menus: int

    # 今日动态
    today_login_count: int
    today_operation_count: int

    # 趋势 (近7日)
    # 格式: [{"date": "2024-01-01", "count": 10}, ...]
    login_trend: list[dict[str, Any]]

    # 最新动态
    recent_logins: list[LoginLogSimple]
