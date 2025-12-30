"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: dashboard.py
@DateTime: 2025-12-30 22:20:00
@Docs: 仪表盘 API 接口.
"""

from typing import Any

from fastapi import APIRouter

from app.api import deps
from app.schemas.common import ResponseBase
from app.schemas.dashboard import DashboardStats

router = APIRouter()


@router.get("/summary", response_model=ResponseBase[DashboardStats])
async def get_dashboard_summary(
    current_user: deps.CurrentUser,
    service: deps.DashboardServiceDep,
) -> Any:
    """
    获取仪表盘统计数据。
    """
    stats = await service.get_summary_stats()
    return ResponseBase(data=stats)
