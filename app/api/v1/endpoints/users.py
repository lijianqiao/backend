"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: users.py
@DateTime: 2025-12-30 11:55:00
@Docs: 用户 API 接口 (Users API).
"""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends

from app.api import deps
from app.schemas.common import BatchDeleteRequest, BatchOperationResult, PaginatedResponse, ResponseBase
from app.schemas.user import ChangePasswordRequest, ResetPasswordRequest, UserCreate, UserResponse, UserUpdate

router = APIRouter()


@router.get("/", response_model=ResponseBase[PaginatedResponse[UserResponse]])
async def read_users(
    user_service: deps.UserServiceDep,
    current_user: deps.CurrentUser,
    active_superuser: deps.User = Depends(deps.get_current_active_superuser),
    page: int = 1,
    page_size: int = 20,
) -> Any:
    """
    查询用户列表 (分页)。
    需要超级管理员权限。
    """
    users, total = await user_service.get_users_paginated(page=page, page_size=page_size)
    return ResponseBase(data=PaginatedResponse(total=total, page=page, page_size=page_size, items=users))


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


@router.delete("/batch", response_model=ResponseBase[BatchOperationResult])
async def batch_delete_users(
    *,
    request: BatchDeleteRequest,
    current_user: deps.CurrentUser,
    active_superuser: deps.User = Depends(deps.get_current_active_superuser),
    user_service: deps.UserServiceDep,
) -> Any:
    """
    批量删除用户。
    需要超级管理员权限。
    """
    success_count, failed_ids = await user_service.batch_delete_users(ids=request.ids, hard_delete=request.hard_delete)
    return ResponseBase(
        data=BatchOperationResult(
            success_count=success_count,
            failed_ids=failed_ids,
            message=f"成功删除 {success_count} 个用户" if not failed_ids else "部分删除成功",
        )
    )


@router.get("/me", response_model=ResponseBase[UserResponse])
async def read_user_me(
    current_user: deps.CurrentUser,
) -> Any:
    """
    获取当前用户信息。
    """
    return ResponseBase(data=current_user)


@router.put("/me", response_model=ResponseBase[UserResponse])
async def update_user_me(
    *,
    user_service: deps.UserServiceDep,
    user_in: UserUpdate,
    current_user: deps.CurrentUser,
) -> Any:
    """
    更新当前用户信息。
    """
    user = await user_service.update_user(user_id=current_user.id, obj_in=user_in)
    return ResponseBase(data=user)


@router.put("/me/password", response_model=ResponseBase[UserResponse])
async def change_password_me(
    *,
    user_service: deps.UserServiceDep,
    password_data: ChangePasswordRequest,
    current_user: deps.CurrentUser,
) -> Any:
    """
    修改当前用户密码。
    需要验证旧密码。
    """
    user = await user_service.change_password(
        user_id=current_user.id,
        old_password=password_data.old_password,
        new_password=password_data.new_password,
    )
    return ResponseBase(data=user, message="密码修改成功")


@router.put("/{user_id}/password", response_model=ResponseBase[UserResponse])
async def reset_user_password(
    *,
    user_id: UUID,
    password_data: ResetPasswordRequest,
    current_user: deps.CurrentUser,
    active_superuser: deps.User = Depends(deps.get_current_active_superuser),
    user_service: deps.UserServiceDep,
) -> Any:
    """
    管理员重置用户密码。
    需要超级管理员权限，无需验证旧密码。
    """
    user = await user_service.reset_password(user_id=user_id, new_password=password_data.new_password)
    return ResponseBase(data=user, message="密码重置成功")
