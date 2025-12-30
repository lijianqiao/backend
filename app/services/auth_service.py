"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: auth_service.py
@DateTime: 2025-12-30 12:20:00
@Docs: 认证服务业务逻辑 (Authentication Business Service).
"""

from datetime import timedelta

from fastapi import Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.core.exceptions import UnauthorizedException
from app.crud.crud_user import user as user_crud
from app.models.user import User
from app.schemas.token import Token
from app.services import log_service


async def authenticate(db: AsyncSession, username_or_phone: str, password: str) -> User | None:
    """
    验证用户凭据 (用户名或手机号 + 密码)。

    Args:
        db (AsyncSession): 数据库会话。
        username_or_phone (str): 用户名或手机号。
        password (str): 明文密码。

    Returns:
        User | None: 验证成功返回用户对象，否则返回 None。
    """
    # 尝试使用用户名查找
    user = await user_crud.get_by_username(db, username=username_or_phone)
    if not user:
        # 尝试使用手机号查找
        user = await user_crud.get_by_phone(db, phone=username_or_phone)

    if not user:
        return None

    if not security.verify_password(password, user.password):
        return None

    return user


async def login_access_token(db: AsyncSession, form_data: OAuth2PasswordRequestForm, request: Request) -> Token:
    """
    用户登录并生成访问令牌 (JWT)。
    此方法会处理登录日志记录 (成功/失败)。

    Args:
        db (AsyncSession): 数据库会话。
        form_data (OAuth2PasswordRequestForm): 登录表单。
        request (Request): HTTP 请求对象。

    Returns:
        Token: 包含 access_token 的对象。

    Raises:
        UnauthorizedException: 登录失败或用户被禁用。
    """
    user = await authenticate(db, form_data.username, form_data.password)
    if not user:
        # 记录登录失败日志
        await log_service.create_login_log(
            db, username=form_data.username, request=request, status=False, msg="用户名或密码错误"
        )
        raise UnauthorizedException("用户名或密码错误")

    if not user.is_active:
        # 记录用户被禁用日志
        await log_service.create_login_log(
            db, username=form_data.username, request=request, status=False, msg="用户已被禁用"
        )
        raise UnauthorizedException("用户已被禁用")

    access_token_expires = timedelta(minutes=security.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(subject=user.id, expires_delta=access_token_expires)

    # 记录登录成功日志
    # 注意: log_service.create_login_log user_id 需要确保类型匹配。
    # User.id 是 UUID 类型，create_login_log 应该接受 UUID 或 str 并做转换。
    await log_service.create_login_log(
        db, user_id=user.id, username=user.username, request=request, status=True, msg="登录成功"
    )

    return Token(access_token=access_token, token_type="bearer")
