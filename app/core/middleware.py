"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: middleware.py
@DateTime: 2025-12-30 12:45:00
@Docs: 中间件：请求ID记录与日志 (Request Log Middleware).
"""

import time

import uuid6
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from structlog.contextvars import bind_contextvars, clear_contextvars

from app.core.logger import logger


class RequestLogMiddleware(BaseHTTPMiddleware):
    """
    全局请求日志中间件。

    1. 生成/传递 X-Request-ID。
    2. 绑定 Request ID 到 Structlog 上下文。
    3. 记录请求处理时间和状态码。
    """

    async def dispatch(self, request: Request, call_next):
        clear_contextvars()
        request_id = request.headers.get("X-Request-ID", str(uuid6.uuid7()))
        bind_contextvars(request_id=request_id)

        start_time = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception as e:
            # 异常通常由 exception_handler 处理，但我们可以在此绑定额外上下文或重新抛出
            raise e

        process_time = time.perf_counter() - start_time

        # 记录请求完成日志
        # 排除健康检查等噪声日志
        if request.url.path != "/health":
            logger.info(
                "请求处理完成",
                http_method=request.method,
                url=str(request.url),
                status_code=response.status_code,
                latency=f"{process_time:.4f}s",
            )

        response.headers["X-Request-ID"] = request_id
        return response
