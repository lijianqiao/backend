"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: crud_log.py
@DateTime: 2025-12-30 14:40:00
@Docs: 日志 CRUD 操作 (Log CRUD).
"""

from app.crud.base import CRUDBase
from app.models.log import LoginLog, OperationLog
from app.schemas.log import LoginLogCreate, OperationLogCreate


class CRUDLoginLog(CRUDBase[LoginLog, LoginLogCreate, LoginLogCreate]):
    pass


class CRUDOperationLog(CRUDBase[OperationLog, OperationLogCreate, OperationLogCreate]):
    pass


login_log = CRUDLoginLog(LoginLog)
operation_log = CRUDOperationLog(OperationLog)
