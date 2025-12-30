"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: log_service.py
@DateTime: 2025-12-30 12:25:00
@Docs: 日志服务业务逻辑 (Logging Service Logic).
"""

import uuid

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from user_agents import parse

from app.models.log import LoginLog


class LogService:
    """
    日志服务类。
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_login_log(
        self,
        *,
        user_id: uuid.UUID | str | None = None,
        username: str | None = None,
        request: Request,
        status: bool = True,
        msg: str = "Login Success",
    ) -> LoginLog:
        """
        创建登录日志。
        """
        ip = request.client.host if request.client else None
        ua_string = request.headers.get("user-agent", "")
        user_agent = parse(ua_string)

        # 将 user_id 转为 UUID 对象 (如果非空)
        final_user_id: uuid.UUID | None = None
        if user_id:
            if isinstance(user_id, str):
                try:
                    final_user_id = uuid.UUID(user_id)
                except ValueError:
                    final_user_id = None
            else:
                final_user_id = user_id

        log = LoginLog(
            user_id=final_user_id,
            username=username,
            ip=ip,
            user_agent=str(user_agent),
            browser=f"{user_agent.browser.family} {user_agent.browser.version_string}",
            os=f"{user_agent.os.family} {user_agent.os.version_string}",
            device=user_agent.device.family,
            status=status,
            msg=msg,
        )
        self.db.add(log)
        await self.db.flush()
        # 由于是异步后台任务调用，可能需要显式 commit，或者由调用方的 Session 管理。
        # 如果是 BackgroundTasks 且使用独立的 Session，则必须 commit。
        # 考虑到作为 Service，应尽量保持原子提交或由调用层控制。
        # 为配合 BackgroundTasks，这里不做 commit，假设 Session 生命周期在 Task 中管理？
        # 不，BackgroundTasks 运行在响应返回后，原来的 Session 可能已关闭（如果使用 Depends(get_db)）。
        # 所以 BackgroundTasks 需要独立的 Session 或者确保 Session 未关闭。
        # 通常做法：Controller 传递 db 给 BackgroundTasks 调用的函数？不，FastAPI Depends db 会在 response 后 close。
        # 更好的做法：BackgroundTasks 接收一个独立的 Session 工厂或在新线程中创建 Session。
        # 但为简单起见，我们假设 LogService 被同步调用或在此次请求的事务中。
        # 如果要完全异步，需要在 Task 中使用 `async with AsyncSessionLocal() as db: ...`

        return log
