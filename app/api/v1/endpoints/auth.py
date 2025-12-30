"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: auth.py
@DateTime: 2025-12-30 11:45:00
@Docs: 认证 API 接口 (Authentication API).
"""

from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm

from app.api import deps
from app.core.rate_limiter import limiter
from app.schemas.common import ResponseBase
from app.schemas.token import Token
from app.schemas.user import UserResponse

router = APIRouter()


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login_access_token(
    request: Request,
    background_tasks: BackgroundTasks,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: deps.AuthServiceDep,
) -> Token:
    """
    OAuth2 兼容的 Token 登录接口，获取 Access Token。
    每个 IP 每分钟最多 5 次请求。
    """
    return await auth_service.login_access_token(
        form_data=form_data, request=request, background_tasks=background_tasks
    )


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
