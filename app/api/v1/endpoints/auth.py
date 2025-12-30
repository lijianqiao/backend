"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: auth.py
@DateTime: 2025-12-30 12:35:00
@Docs: 认证模块 API 接口 (API Endpoints for Authentication).
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm

from app.api import deps
from app.schemas.common import ResponseBase
from app.schemas.token import Token
from app.schemas.user import UserResponse
from app.services import auth_service

router = APIRouter()


@router.post("/login", response_model=ResponseBase[Token])
async def login(
    db: deps.SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()], request: Request
) -> ResponseBase[Token]:
    """
    OAuth2 兼容的 Token 登录接口。

    使用用户名/手机号 + 密码获取访问令牌 (Access Token)。

    Args:
        db (AsyncSession): 数据库会话依赖。
        form_data (OAuth2PasswordRequestForm): 表单数据，包含 username 和 password。
        request (Request): HTTP 请求对象，用于获取 IP 和 User-Agent 进行日志记录。

    Returns:
        ResponseBase[Token]: 包含 Access Token 的响应对象。
    """
    token = await auth_service.login_access_token(db, form_data, request)
    return ResponseBase(data=token)


@router.post("/test-token", response_model=ResponseBase[UserResponse])
async def test_token(current_user: deps.CurrentUser) -> ResponseBase[UserResponse]:
    """
    测试 Access Token 是否有效。

    Args:
        current_user (User): 当前登录用户依赖。

    Returns:
        ResponseBase[UserResponse]: 返回当前用户信息。
    """
    return ResponseBase(data=UserResponse.model_validate(current_user))
