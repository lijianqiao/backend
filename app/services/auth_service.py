"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: auth_service.py
@DateTime: 2025-12-30 13:02:00
@Docs: 认证服务业务逻辑 (Authentication Service Logic) - 包含异步日志。
"""

import uuid
from datetime import timedelta
from typing import Any

import jwt
from fastapi import BackgroundTasks, Request
from jwt.exceptions import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.core.config import settings
from app.core.exceptions import CustomException, UnauthorizedException
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
        refresh_token = security.create_refresh_token(subject=user.id)

        # 记录成功日志 (异步)
        background_tasks.add_task(
            self.log_service.create_login_log,
            user_id=user.id,
            username=user.username,
            request=request,
            status=True,
            msg="登录成功",
        )

        return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")

    async def refresh_token(self, refresh_token: str) -> Token:
        """
        刷新 Token。验证 Refresh Token 有效性并返回新的 Access Token。
        """
        try:
            payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=["HS256"])
            token_type = payload.get("type")
            if token_type != "refresh":
                raise UnauthorizedException(message="无效的刷新令牌 (Token 类型错误)")

            user_id = payload.get("sub")
            if user_id is None:
                raise UnauthorizedException(message="无效的刷新令牌 (缺少 sub)")

        except (InvalidTokenError, Exception) as e:
            raise UnauthorizedException(message="无效的刷新令牌") from e

        # 检查用户是否存在/激活 (可选，但推荐)
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError as e:
            raise UnauthorizedException(message="无效的刷新令牌 (用户ID格式错误)") from e

        user = await self.user_crud.get(self.db, id=user_uuid)
        if not user or not user.is_active:
            raise UnauthorizedException(message="用户不存在或已禁用")

        # 签发新的 Token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = security.create_access_token(subject=user.id, expires_delta=access_token_expires)

        # 也可以选择此时是否轮换 Refresh Token，这里简单起见只返回新的 Access，前端继续复用 Refresh
        # 如果需要轮换，则生成新的 refresh_token 并返回
        # 这里我们选择返回原来的 refresh_token (或者生成的新的，取决于策略，这里保持原样以支持 Refresh Token 长期有效)
        # 为了安全，也可以在这里签发一个新的 refresh token，实现 Refresh Token Rotation
        # 简单实现：返回新的 Access Token，Refresh Token 保持不变 (通过参数传入或重新包含在响应中)

        return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")
