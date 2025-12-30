"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: auth_service.py
@DateTime: 2025-12-30 13:02:00
@Docs: 认证服务业务逻辑 (Authentication Service Logic) - 包含异步日志。
"""

from datetime import timedelta
from typing import Any

from fastapi import BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.core.config import settings
from app.core.exceptions import CustomException
from app.crud.crud_user import CRUDUser
from app.schemas.token import Token
from app.services.log_service import LogService


class AuthService:
    """
    认证服务类。
    依赖 LogService 和 CRUDUser。
    """

    def __init__(self, db: AsyncSession, log_service: LogService, user_crud: CRUDUser):
        self.db = db
        self.log_service = log_service
        self.user_crud = user_crud

    async def authenticate(self, username: str, password: str) -> Any:
        """
        验证用户名/密码。支持用户名或手机号。
        """
        user = await self.user_crud.get_by_username(self.db, username=username)
        if not user:
            # 尝试通过手机号查找
            user = await self.user_crud.get_by_phone(self.db, phone=username)

        if not user or not user.is_active or user.is_deleted:
            return None

        if not security.verify_password(password, user.password):
            return None

        return user

    async def login_access_token(self, form_data: Any, request: Request, background_tasks: BackgroundTasks) -> Token:
        """
        处理登录并返回 Token，异步记录日志。
        """
        user = await self.authenticate(form_data.username, form_data.password)
        if not user:
            # 记录失败日志 (异步)
            background_tasks.add_task(
                self.log_service.create_login_log,
                request=request,
                username=form_data.username,
                status=False,
                msg="用户名或密码错误",
            )
            raise CustomException(code=400, message="用户名或密码错误")

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = security.create_access_token(subject=user.id, expires_delta=access_token_expires)

        # 记录成功日志 (异步)
        background_tasks.add_task(
            self.log_service.create_login_log,
            user_id=user.id,
            username=user.username,
            request=request,
            status=True,
            msg="登录成功",
        )

        return Token(access_token=access_token, token_type="bearer")
