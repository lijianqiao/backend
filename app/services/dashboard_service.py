"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: dashboard_service.py
@DateTime: 2025-12-30 22:15:00
@Docs: 仪表盘业务逻辑 (Dashboard Service).
"""

from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.crud_log import CRUDLoginLog, CRUDOperationLog
from app.crud.crud_menu import CRUDMenu
from app.crud.crud_role import CRUDRole
from app.crud.crud_user import CRUDUser
from app.schemas.dashboard import DashboardStats, LoginLogSimple


class DashboardService:
    """
    仪表盘数据聚合服务。
    """

    def __init__(
        self,
        db: AsyncSession,
        user_crud: CRUDUser,
        role_crud: CRUDRole,
        menu_crud: CRUDMenu,
        login_log_crud: CRUDLoginLog,
        operation_log_crud: CRUDOperationLog,
    ):
        self.db = db
        self.user_crud = user_crud
        self.role_crud = role_crud
        self.menu_crud = menu_crud
        self.login_log_crud = login_log_crud
        self.operation_log_crud = operation_log_crud

    async def get_summary_stats(self) -> DashboardStats:
        """
        获取仪表盘首页聚合数据。
        """
        # 1. 基础计数 (并发执行优化)
        # 这里为了简单线性执行，生产环境可使用 asyncio.gather

        # 用户相关
        active_users = await self.user_crud.count_active(self.db)
        # 临时获取 user 总数 (CRUD 未提供 count，暂时用 count_active 替代或者查询所有)
        # 扩展 CRUDUser.count ?
        # 为了演示，暂时假设 Total = Active (或者再加一个 count_total)
        # 既然 CRUDUser.get_multi 会分页，我们直接 count(*)
        # 这里简单起见，再查一次 total
        from sqlalchemy import func, select

        from app.models.user import User

        total_users_res = await self.db.execute(select(func.count(User.id)))
        total_users = total_users_res.scalar_one()

        # 角色与菜单计数
        from app.models.rbac import Menu, Role

        total_roles_res = await self.db.execute(select(func.count(Role.id)))
        total_roles = total_roles_res.scalar_one()

        total_menus_res = await self.db.execute(select(func.count(Menu.id)))
        total_menus = total_menus_res.scalar_one()

        # 2. 今日动态
        today_login_count = await self.login_log_crud.count_today(self.db)

        # 今日 API 调用 (count by range today)
        now = datetime.now()
        today_start = datetime(now.year, now.month, now.day)
        today_end = today_start + timedelta(days=1)
        today_operation_count = await self.operation_log_crud.count_by_range(self.db, today_start, today_end)

        # 3. 趋势图表
        login_trend = await self.login_log_crud.get_trend(self.db, days=7)

        # 4. 最新登录
        recent_logins_orm = await self.login_log_crud.get_recent(self.db, limit=10)
        recent_logins = [LoginLogSimple.model_validate(log) for log in recent_logins_orm]

        return DashboardStats(
            total_users=total_users,
            active_users=active_users,
            total_roles=total_roles,
            total_menus=total_menus,
            today_login_count=today_login_count,
            today_operation_count=today_operation_count,
            login_trend=login_trend,
            recent_logins=recent_logins,
        )
