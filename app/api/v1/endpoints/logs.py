"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: logs.py
@DateTime: 2025-12-30 14:35:00
@Docs: 日志 API 接口 (Logs API).
"""

from typing import Any

from fastapi import APIRouter
from sqlalchemy import select

from app.api import deps
from app.models.log import LoginLog, OperationLog
from app.schemas.common import ResponseBase
from app.schemas.log import LoginLogResponse, OperationLogResponse

router = APIRouter()


@router.get("/login", response_model=ResponseBase[list[LoginLogResponse]])
async def read_login_logs(
    db: deps.SessionDep,
    current_user: deps.CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    获取登录日志。
    """
    # 这里可以使用通用 crud.get_multi，但 models.log 没有在 crud 中注册通用实例
    # 直接查询或添加 crud_log
    query = select(LoginLog).order_by(LoginLog.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    logs = result.scalars().all()
    return ResponseBase(data=logs)  # type: ignore


@router.get("/operation", response_model=ResponseBase[list[OperationLogResponse]])
async def read_operation_logs(
    db: deps.SessionDep,
    current_user: deps.CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    获取操作日志。
    """
    query = select(OperationLog).order_by(OperationLog.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    logs = result.scalars().all()
    return ResponseBase(data=logs)  # type: ignore
