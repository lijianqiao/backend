"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: users.py
@DateTime: 2025-12-30 11:55:00
@Docs: 用户 API 接口 (Users API).
"""

from typing import Any

from fastapi import APIRouter, Depends

from app.api import deps
from app.schemas.common import ResponseBase
from app.schemas.user import UserCreate, UserResponse, UserUpdate

router = APIRouter()


@router.get("/", response_model=ResponseBase[list[UserResponse]])
async def read_users(
    user_service: deps.UserServiceDep,
    current_user: deps.CurrentUser,
    active_superuser: deps.User = Depends(deps.get_current_active_superuser),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    查询用户列表。
    需要超级管理员权限。
    """
    users = await user_service.get_users(skip=skip, limit=limit)
    return ResponseBase(data=users)


@router.post("/", response_model=ResponseBase[UserResponse])
async def create_user(
    *,
    user_in: UserCreate,
    current_user: deps.CurrentUser,
    active_superuser: deps.User = Depends(deps.get_current_active_superuser),
    user_service: deps.UserServiceDep,
) -> Any:
    """
    创建新用户。
    需要超级管理员权限。
    """
    user = await user_service.create_user(obj_in=user_in)
    return ResponseBase(data=user)


@router.put("/me", response_model=ResponseBase[UserResponse])
async def update_user_me(
    *,
    user_service: deps.UserServiceDep,
    password: str = None,  # type: ignore
    nickname: str = None,  # type: ignore
    email: str = None,  # type: ignore
    current_user: deps.CurrentUser,
) -> Any:
    """
    更新当前用户信息。
    """
    current_user_data = UserUpdate(password=password, nickname=nickname, email=email)
    user = await user_service.update_user(user_id=current_user.id, obj_in=current_user_data)
    return ResponseBase(data=user)


@router.get("/me", response_model=ResponseBase[UserResponse])
async def read_user_me(
    current_user: deps.CurrentUser,
) -> Any:
    """
    获取当前用户信息。
    """
    return ResponseBase(data=current_user)
