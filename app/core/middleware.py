"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: middleware.py
@DateTime: 2025-12-30 12:45:00
@Docs: 中间件：请求ID记录与日志 (Request Log Middleware).
       支持记录 API Traffic 到文件，以及 OperationLog 到数据库。
"""

import asyncio
import time

import uuid6
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from structlog.contextvars import bind_contextvars, clear_contextvars

from app.core.db import AsyncSessionLocal
from app.core.logger import access_logger, logger
from app.models.log import OperationLog


async def write_operation_log_to_db(
    user_id: str,
    username: str,
    ip: str | None,
    method: str,
    path: str,
    status_code: int,
    process_time: float,
) -> None:
    """
    异步写入操作日志到数据库。
    """
    async with AsyncSessionLocal() as session:
        try:
            # 简单的模块名提取 (例如 /api/v1/users/ -> users)
            parts = path.strip("/").split("/")
            # parts 通常是 ['api', 'v1', 'users', ...]
            module = "unknown"
            if len(parts) >= 3 and parts[0] == "api":
                module = parts[2]

            # 摘要
            summary = f"{method} {path}"

            log = OperationLog(
                user_id=user_id,
                username=username,
                ip=ip,
                module=module,
                summary=summary,
                method=method,
                path=path,
                response_code=status_code,
                duration=process_time,
            )
            session.add(log)
            await session.commit()
        except Exception as e:
            logger.error(f"Failed to write operation log: {e}")
            # 不抛出异常，以免影响主请求


class RequestLogMiddleware(BaseHTTPMiddleware):
    """
    全局请求日志中间件。

    1. 生成/传递 X-Request-ID。
    2. 绑定 Request ID 到 Structlog 上下文。
    3. 记录请求处理时间和状态码。
    4. [Audit] 如果已认证用户，记录操作日志到数据库。
    """

    async def dispatch(self, request: Request, call_next):
        clear_contextvars()
        request_id = request.headers.get("X-Request-ID", str(uuid6.uuid7()))
        bind_contextvars(request_id=request_id)

        start_time = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception as e:
            # 异常通常由 exception_handler 处理
            raise e

        process_time = time.perf_counter() - start_time

        # 记录请求完成日志 (File Log)
        if request.url.path != "/health":
            # 使用专门的 access_logger 记录流量日志
            access_logger.info(
                "API Access",
                http_method=request.method,
                url=str(request.url),
                path=request.url.path,
                query=request.url.query,
                status_code=response.status_code,
                client_ip=request.client.host if request.client else "unknown",
                latency=f"{process_time:.4f}s",
            )

            # [Audit] 数据库操作日志
            # 检查 request.state 是否有 user (由 deps.get_current_user 设置)
            # 排除 GET 请求 和 登录接口 (Login 由 AuthService 记录)
            if (
                request.method != "GET"
                and "/auth/login" not in request.url.path
                and hasattr(request, "state")
                and hasattr(request.state, "user")
            ):
                user = request.state.user
                asyncio.create_task(
                    write_operation_log_to_db(
                        user_id=user.id,
                        username=user.username,
                        ip=request.client.host if request.client else None,
                        method=request.method,
                        path=request.url.path,
                        status_code=response.status_code,
                        process_time=process_time,
                    )
                )

        response.headers["X-Request-ID"] = request_id
        return response
