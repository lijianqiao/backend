"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: middleware.py
@DateTime: 2025-12-30 12:45:00
@Docs: 中间件：请求ID记录与日志 (Request Log Middleware).
       使用事件总线发布操作日志事件。
"""

import json
import time
from typing import Any

import uuid6
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from structlog.contextvars import bind_contextvars, clear_contextvars

from app.core.event_bus import OperationLogEvent, event_bus
from app.core.logger import access_logger
from app.core.metrics import record_request_metrics


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

        request_body: bytes = b""
        if request.method != "GET":
            try:
                request_body = await request.body()

                async def receive() -> dict[str, Any]:
                    nonlocal request_body
                    body = request_body
                    request_body = b""
                    return {"type": "http.request", "body": body, "more_body": False}

                request._receive = receive  # type: ignore[attr-defined]
            except Exception:
                request_body = b""

        start_time = time.perf_counter()

        response = await call_next(request)

        process_time = time.perf_counter() - start_time

        # Prometheus 指标
        try:
            if request.url.path not in ("/metrics", "/health"):
                record_request_metrics(request.method, request.url.path, response.status_code, process_time)
        except Exception:
            # 指标记录失败不影响主流程
            pass

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
                params = _build_request_params(request, request_body)
                response_result = _build_response_result(response)
                user_agent = request.headers.get("user-agent")
                await event_bus.publish(
                    OperationLogEvent(
                        user_id=str(request.state.user_id),
                        username=request.state.username,
                        ip=request.client.host if request.client else None,
                        method=request.method,
                        path=request.url.path,
                        status_code=response.status_code,
                        process_time=process_time,
                        params=params,
                        response_result=response_result,
                        user_agent=user_agent,
                    )
                )

        response.headers["X-Request-ID"] = request_id
        return response


_MAX_CAPTURE_BYTES = 20_000


def _is_sensitive_path(path: str) -> bool:
    lowered = path.lower()
    if "/auth/" in lowered:
        return True
    if "password" in lowered:
        return True
    return False


def _safe_json_loads(raw: bytes) -> Any | None:
    try:
        text = raw.decode("utf-8", errors="replace")
        return json.loads(text)
    except Exception:
        return None


def _build_request_params(request: Request, request_body: bytes) -> dict[str, Any] | None:
    data: dict[str, Any] = {}

    try:
        if request.query_params:
            data["query"] = dict(request.query_params)
    except Exception:
        pass

    try:
        if request.path_params:
            data["path"] = dict(request.path_params)
    except Exception:
        pass

    if request.method != "GET":
        if _is_sensitive_path(request.url.path):
            data["body"] = {"_filtered": True}
        else:
            content_type = (request.headers.get("content-type") or "").lower()
            if request_body:
                if len(request_body) > _MAX_CAPTURE_BYTES:
                    data["body"] = {"_truncated": True}
                elif "application/json" in content_type:
                    parsed = _safe_json_loads(request_body)
                    data["body"] = parsed if parsed is not None else {"_unparsed": True}
                else:
                    # 非 JSON 时不强行落全文，避免误记录敏感信息
                    data["body"] = {"_non_json": True}

    return data or None


def _build_response_result(response) -> Any | None:
    try:
        content_type = (response.headers.get("content-type") or "").lower()
        if "application/json" not in content_type:
            return None

        body = getattr(response, "body", None)
        if not body:
            return None
        if len(body) > _MAX_CAPTURE_BYTES:
            return {"_truncated": True}

        parsed = _safe_json_loads(body)
        return parsed if parsed is not None else {"_unparsed": True}
    except Exception:
        return None
