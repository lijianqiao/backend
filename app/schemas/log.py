"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: log.py
@DateTime: 2025-12-30 14:30:00
@Docs: 日志 Schema 定义。
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class LogBase(BaseModel):
    user_id: UUID | None = None
    username: str | None = None
    ip: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LoginLogResponse(LogBase):
    id: UUID
    user_agent: str | None = None
    browser: str | None = None
    os: str | None = None
    device: str | None = None
    status: bool
    msg: str | None = None


class OperationLogResponse(LogBase):
    id: UUID
    module: str | None = None
    summary: str | None = None
    method: str | None = None
    path: str | None = None
    response_code: int | None = None
    duration: float | None = None
