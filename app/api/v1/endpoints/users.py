"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: users.py
@DateTime: 2025-12-30 12:40:00
@Docs: User API endpoints.
"""

from typing import Any

from fastapi import APIRouter

from app.api import deps
from app.core.exceptions import ForbiddenException
from app.crud.crud_user import user as user_crud
from app.schemas.common import ResponseBase
from app.schemas.user import UserCreate, UserResponse
from app.services import user_service

router = APIRouter()


@router.get("/", response_model=ResponseBase[list[UserResponse]])
async def read_users(
    db: deps.SessionDep,
    current_user: deps.CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve users.
    """
    if not current_user.is_superuser:
        raise ForbiddenException("Not enough privileges")
    users = await user_crud.get_multi(db, skip=skip, limit=limit)
    return ResponseBase(data=users)


@router.post("/", response_model=ResponseBase[UserResponse])
async def create_user(
    *,
    db: deps.SessionDep,
    user_in: UserCreate,
    current_user: deps.CurrentUser,
) -> Any:
    """
    Create new user.
    """
    if not current_user.is_superuser:
        raise ForbiddenException("Not enough privileges")
    user = await user_service.create_user(db, obj_in=user_in)
    return ResponseBase(data=user)


@router.get("/me", response_model=ResponseBase[UserResponse])
async def read_user_me(
    current_user: deps.CurrentUser,
) -> Any:
    """
    Get current user.
    """
    return ResponseBase(data=current_user)
