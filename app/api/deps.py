"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: deps.py
@DateTime: 2025-12-30 12:05:00
@Docs: FastAPI 依赖注入模块 (Database Session & Auth Dependency).
"""

from collections.abc import AsyncGenerator
from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import AsyncSessionLocal
from app.core.exceptions import ForbiddenException, NotFoundException, UnauthorizedException
from app.models.user import User
from app.schemas.token import TokenPayload

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


async def get_db() -> AsyncGenerator[AsyncSession]:
    """
    获取异步数据库会话依赖。
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


SessionDep = Annotated[AsyncSession, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


async def get_current_user(session: SessionDep, token: TokenDep) -> User:
    """
    解析 Token 并获取当前登录用户。

    Args:
        session (SessionDep): 数据库会话。
        token (TokenDep): JWT 令牌。

    Raises:
        UnauthorizedException: 认证失败。
        NotFoundException: 用户不存在。
        ForbiddenException: 用户被禁用。

    Returns:
        User: 当前用户对象。
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError) as e:
        raise UnauthorizedException(message="无法验证凭据 (Token 无效)") from e

    if token_data.sub is None:
        raise UnauthorizedException(message="无法验证凭据 (Token 缺失 sub)")

    # 直接查询数据库获取用户 (避免循环引用 Service/CRUD)
    result = await session.execute(select(User).where(User.id == token_data.sub))
    user = result.scalars().first()

    if not user:
        raise NotFoundException(message="用户不存在")
    if not user.is_active:
        raise ForbiddenException(message="用户已被禁用")

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_current_active_superuser(current_user: CurrentUser) -> User:
    """
    检查当前用户是否为超级管理员。
    """
    if not current_user.is_superuser:
        raise ForbiddenException(message="权限不足: 需要超级管理员权限")
    return current_user
