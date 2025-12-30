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


async def create_login_log(
    db: AsyncSession,
    *,
    user_id: uuid.UUID | str | None = None,
    username: str | None = None,
    request: Request,
    status: bool = True,
    msg: str = "Login Success",
) -> LoginLog:
    """
    创建登录日志。

    Args:
        db (AsyncSession): 数据库会话。
        user_id (Optional[Union[uuid.UUID, str]], optional): 用户 ID (UUID 或 Str)。
        username (Optional[str], optional): 用户名。
        request (Request): HTTP 请求对象，用于提取 IP 和 UA。
        status (bool, optional): 登录成功/失败状态. Defaults to True.
        msg (str, optional): 日志消息. Defaults to "Login Success".

    Returns:
        LoginLog: 创建的日志对象。
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
    db.add(log)
    await db.flush()
    # 提示: 服务层方法通常依赖外部事务提交。
    # 但对于关键的审计日志，有时我们希望它一定被记录。
    # 目前保持 flush，由 API 层的事务管理器统一 commit。

    return log
