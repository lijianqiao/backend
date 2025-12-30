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
from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import AsyncSessionLocal
from app.core.exceptions import ForbiddenException, NotFoundException, UnauthorizedException
from app.core.logger import logger
from app.crud.crud_log import CRUDLoginLog, CRUDOperationLog
from app.crud.crud_log import login_log as login_log_crud_global
from app.crud.crud_log import operation_log as operation_log_crud_global
from app.crud.crud_menu import CRUDMenu
from app.crud.crud_menu import menu as menu_crud_global
from app.crud.crud_role import CRUDRole
from app.crud.crud_role import role as role_crud_global
from app.crud.crud_user import CRUDUser
from app.crud.crud_user import user as user_crud_global
from app.models.user import User
from app.schemas.token import TokenPayload
from app.services.auth_service import AuthService
from app.services.log_service import LogService
from app.services.menu_service import MenuService
from app.services.role_service import RoleService
from app.services.user_service import UserService

# -----------------------

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


async def get_current_user(request: Request, session: SessionDep, token: TokenDep) -> User:
    """
    解析 Token 并获取当前登录用户。
    """
    try:
        # 添加解码调试日志
        logger.debug(f"Decoding token: {token[:10]}...")
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError) as e:
        logger.error(f"Token validation failed: {str(e)}", error=str(e))
        raise UnauthorizedException(message="无法验证凭据 (Token 无效)") from e

    if token_data.sub is None:
        logger.error("Token missing sub subject")
        raise UnauthorizedException(message="无法验证凭据 (Token 缺失 sub)")

    # 直接查询数据库获取用户
    result = await session.execute(select(User).where(User.id == token_data.sub))
    user = result.scalars().first()

    if not user:
        logger.error(f"User not found for sub: {token_data.sub}")
        raise NotFoundException(message="用户不存在")
    if not user.is_active:
        raise ForbiddenException(message="用户已被禁用")

    # 将用户绑定到 request state，供中间件使用
    request.state.user = user
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_current_active_superuser(current_user: CurrentUser) -> User:
    """
    检查当前用户是否为超级管理员。
    """
    if not current_user.is_superuser:
        raise ForbiddenException(message="权限不足: 需要超级管理员权限")
    return current_user


# --- Repository Injectors ---
# 如果 Repository 也是类且有依赖，也应在此定义 Injector。
# 目前 Repository 是作为 Singletons 初始化的 (在 crud 模块底部)。
# 为了"Dependency Parameterization" 和 Mocking，我们可以通过依赖返回这些实例。


def get_user_crud() -> CRUDUser:
    return user_crud_global


def get_role_crud() -> CRUDRole:
    return role_crud_global


def get_menu_crud() -> CRUDMenu:
    return menu_crud_global


def get_login_log_crud() -> CRUDLoginLog:
    return login_log_crud_global


def get_operation_log_crud() -> CRUDOperationLog:
    return operation_log_crud_global


# --- Service Injectors ---
# 使用 Depends 注入 Service 和 Repositories


def get_user_service(db: SessionDep, user_crud: Annotated[CRUDUser, Depends(get_user_crud)]) -> UserService:
    return UserService(db, user_crud)


def get_log_service(
    db: SessionDep,
    login_log_crud: Annotated[CRUDLoginLog, Depends(get_login_log_crud)],
    operation_log_crud: Annotated[CRUDOperationLog, Depends(get_operation_log_crud)],
) -> LogService:
    return LogService(db, login_log_crud, operation_log_crud)


def get_role_service(db: SessionDep, role_crud: Annotated[CRUDRole, Depends(get_role_crud)]) -> RoleService:
    return RoleService(db, role_crud)


def get_menu_service(db: SessionDep, menu_crud: Annotated[CRUDMenu, Depends(get_menu_crud)]) -> MenuService:
    return MenuService(db, menu_crud)


def get_auth_service(
    db: SessionDep,
    log_service: Annotated[LogService, Depends(get_log_service)],
    user_crud: Annotated[CRUDUser, Depends(get_user_crud)],
) -> AuthService:
    return AuthService(db, log_service, user_crud)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
LogServiceDep = Annotated[LogService, Depends(get_log_service)]
RoleServiceDep = Annotated[RoleService, Depends(get_role_service)]
MenuServiceDep = Annotated[MenuService, Depends(get_menu_service)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
