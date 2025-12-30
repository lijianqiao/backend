"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: crud_log.py
@DateTime: 2025-12-30 14:40:00
@Docs: 日志 CRUD 操作 (Log CRUD).
"""

from typing import Any

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.log import LoginLog, OperationLog
from app.schemas.log import LoginLogCreate, OperationLogCreate


class CRUDLoginLog(CRUDBase[LoginLog, LoginLogCreate, LoginLogCreate]):
    async def count_today(self, db: AsyncSession) -> int:
        """
        统计今日登录次数 (SQLite/PG 通用近似实现，严格来说需根据 DB 类型处理时区，这里简化处理).
        """
        # 使用 SQLite 的 date('now')
        # 如果是 PG 需用 current_date
        sql = text("SELECT count(*) FROM sys_login_log WHERE date(created_at) = date('now')")
        try:
            result = await db.execute(sql)
            return result.scalar_one()
        except Exception:
            # Fallback
            return 0

    async def count_by_range(self, db: AsyncSession, start: Any, end: Any) -> int:
        result = await db.execute(
            select(func.count(LoginLog.id)).where(LoginLog.created_at >= start, LoginLog.created_at <= end)
        )
        return result.scalar_one()

    async def get_trend(self, db: AsyncSession, days: int = 7) -> list[dict[str, Any]]:
        """
        获取近 N 天趋势 (需要根据数据库类型编写不同的 Group By 语法).
        此处仅提供 Python 层面聚合实现作为通用 fallback，或者针对 SQLite/PG 分别写 SQL.
        为了简单通用，这里演示先拉取数据 (Limit 10000) 再 Python 聚合，或者使用简单的 date_trunc (PG) / strftime (SQLite).
        """
        # 针对 SQLite 的实现
        sql = text(
            "SELECT date(created_at) as d, count(*) as c FROM sys_login_log "
            "WHERE created_at >= date('now', :days) "
            "GROUP BY d ORDER BY d ASC"
        )
        # 注意: datetime 字段在 SQLite 中默认是字符串存储 ISO8601，使用 date() 函数截取
        # :days 参数格式如 '-6 days'
        try:
            result = await db.execute(sql, {"days": f"-{days - 1} days"})
            return [{"date": str(row[0]), "count": row[1]} for row in result.all()]
        except Exception:
            # Fallback for empty or non-SQLite (safety)
            return []

    async def get_recent(self, db: AsyncSession, limit: int = 10) -> list[LoginLog]:
        result = await db.execute(select(LoginLog).order_by(LoginLog.created_at.desc()).limit(limit))
        return list(result.scalars().all())


class CRUDOperationLog(CRUDBase[OperationLog, OperationLogCreate, OperationLogCreate]):
    async def count_by_range(self, db: AsyncSession, start: Any, end: Any) -> int:
        result = await db.execute(
            select(func.count(OperationLog.id)).where(OperationLog.created_at >= start, OperationLog.created_at <= end)
        )
        return result.scalar_one()


login_log = CRUDLoginLog(LoginLog)
operation_log = CRUDOperationLog(OperationLog)
