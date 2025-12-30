"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: logs.py
@DateTime: 2025-12-30 14:35:00
@Docs: 日志 API 接口 (Logs API).
"""

from typing import Any

from fastapi import APIRouter

from app.api import deps
from app.schemas.common import PaginatedResponse, ResponseBase
from app.schemas.log import LoginLogResponse, OperationLogResponse

router = APIRouter()


@router.get("/login", response_model=ResponseBase[PaginatedResponse[LoginLogResponse]])
async def read_login_logs(
    current_user: deps.CurrentUser,
    log_service: deps.LogServiceDep,
    page: int = 1,
    page_size: int = 20,
) -> Any:
    """
    获取登录日志 (分页)。
    """
    logs, total = await log_service.get_login_logs_paginated(page=page, page_size=page_size)
    return ResponseBase(data=PaginatedResponse(total=total, page=page, page_size=page_size, items=logs))


@router.get("/operation", response_model=ResponseBase[PaginatedResponse[OperationLogResponse]])
async def read_operation_logs(
    current_user: deps.CurrentUser,
    log_service: deps.LogServiceDep,
    page: int = 1,
    page_size: int = 20,
) -> Any:
    """
    获取操作日志 (分页)。
    """
    logs, total = await log_service.get_operation_logs_paginated(page=page, page_size=page_size)
    return ResponseBase(data=PaginatedResponse(total=total, page=page, page_size=page_size, items=logs))
