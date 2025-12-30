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
from app.schemas.common import ResponseBase
from app.schemas.log import LoginLogResponse, OperationLogResponse

router = APIRouter()


@router.get("/login", response_model=ResponseBase[list[LoginLogResponse]])
async def read_login_logs(
    current_user: deps.CurrentUser,
    log_service: deps.LogServiceDep,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    获取登录日志。
    """
    logs = await log_service.get_login_logs(skip=skip, limit=limit)
    return ResponseBase(data=logs)


@router.get("/operation", response_model=ResponseBase[list[OperationLogResponse]])
async def read_operation_logs(
    current_user: deps.CurrentUser,
    log_service: deps.LogServiceDep,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    获取操作日志。
    """
    logs = await log_service.get_operation_logs(skip=skip, limit=limit)
    return ResponseBase(data=logs)
