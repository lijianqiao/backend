"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: middleware.py
@DateTime: 2025-12-30 12:45:00
@Docs: 中间件：请求ID记录与日志 (Request Log Middleware).
       使用事件总线发布操作日志事件。
"""

import time

import uuid6
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from structlog.contextvars import bind_contextvars, clear_contextvars

from app.core.event_bus import OperationLogEvent, event_bus
from app.core.logger import access_logger


class RequestLogMiddleware(BaseHTTPMiddleware):
    """
    全局请求日志中间件。

    1. 生成/传递 X-Request-ID。
    2. 绑定 Request ID 到 Structlog 上下文。
    3. 记录请求处理时间和状态码。
    4. [Audit] 如果已认证用户，发布操作日志事件。
    """

    async def dispatch(self, request: Request, call_next):
        clear_contextvars()
        request_id = request.headers.get("X-Request-ID", str(uuid6.uuid7()))
        bind_contextvars(request_id=request_id)

        start_time = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception as e:
            raise e

        process_time = time.perf_counter() - start_time

        # 记录请求完成日志 (File Log)
        if request.url.path != "/health":
            access_logger.info(
                "API 访问",
                http_method=request.method,
                url=str(request.url),
                path=request.url.path,
                query=request.url.query,
                status_code=response.status_code,
                client_ip=request.client.host if request.client else "unknown",
                latency=f"{process_time:.4f}s",
            )

            # [Audit] 发布操作日志事件
            # 排除 GET 请求 和 登录接口 (Login 由 AuthService 记录)
            if (
                request.method != "GET"
                and "/auth/login" not in request.url.path
                and hasattr(request, "state")
                and hasattr(request.state, "user_id")
            ):
                await event_bus.publish(
                    OperationLogEvent(
                        user_id=request.state.user_id,
                        username=request.state.username,
                        ip=request.client.host if request.client else None,
                        method=request.method,
                        path=request.url.path,
                        status_code=response.status_code,
                        process_time=process_time,
                    )
                )

        response.headers["X-Request-ID"] = request_id
        return response
