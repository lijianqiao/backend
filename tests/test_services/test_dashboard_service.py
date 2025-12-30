"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: test_dashboard_service.py
@DateTime: 2025-12-30 22:30:00
@Docs: Dashboard Service Tests.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.dashboard import DashboardStats
from app.services.dashboard_service import DashboardService


class TestDashboardService:
    async def test_get_summary_stats(self, db_session: AsyncSession, dashboard_service: DashboardService):
        stats = await dashboard_service.get_summary_stats()

        assert isinstance(stats, DashboardStats)
        assert stats.total_users >= 0
        assert stats.total_roles >= 0
        assert stats.total_menus >= 0
        assert isinstance(stats.login_trend, list)
        assert isinstance(stats.recent_logins, list)
