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


@router.get("/", response_model=ResponseBase[PaginatedResponse[UserResponse]], summary="获取用户列表")
async def read_users(
    user_service: deps.UserServiceDep,
    current_user: deps.CurrentUser,
    active_superuser: deps.User = Depends(deps.get_current_active_superuser),
    page: int = 1,
    page_size: int = 20,
) -> Any:
    """
    查询用户列表 (分页)。

    获取所有系统用户，支持分页。需要超级管理员权限。

    Args:
        user_service (UserService): 用户服务依赖。
        current_user (User): 当前登录用户。
        active_superuser (User): 超级管理员权限验证。
        page (int, optional): 页码. Defaults to 1.
        page_size (int, optional): 每页数量. Defaults to 20.

    Returns:
        ResponseBase[PaginatedResponse[UserResponse]]: 分页后的用户列表。
    """
    users, total = await user_service.get_users_paginated(page=page, page_size=page_size)
    return ResponseBase(data=PaginatedResponse(total=total, page=page, page_size=page_size, items=users))


@router.post("/", response_model=ResponseBase[UserResponse], summary="创建用户")
async def create_user(
    *,
    user_in: UserCreate,
    current_user: deps.CurrentUser,
    active_superuser: deps.User = Depends(deps.get_current_active_superuser),
    user_service: deps.UserServiceDep,
) -> Any:
    """
    创建新用户。

    注册新的系统用户。需要超级管理员权限。

    Args:
        user_in (UserCreate): 用户创建数据 (用户名, 密码, 邮箱等)。
        current_user (User): 当前登录用户。
        active_superuser (User): 超级管理员权限验证。
        user_service (UserService): 用户服务依赖。

    Returns:
        ResponseBase[UserResponse]: 创建成功的用户对象。
    """
    user = await user_service.create_user(obj_in=user_in)
    return ResponseBase(data=user)


@router.delete("/batch", response_model=ResponseBase[BatchOperationResult], summary="批量删除用户")
async def batch_delete_users(
    *,
    request: BatchDeleteRequest,
    current_user: deps.CurrentUser,
    active_superuser: deps.User = Depends(deps.get_current_active_superuser),
    user_service: deps.UserServiceDep,
) -> Any:
    """
    批量删除用户。

    支持软删除和硬删除。需要超级管理员权限。

    Args:
        request (BatchDeleteRequest): 批量删除请求体 (包含 ID 列表和硬删除标志)。
        current_user (User): 当前登录用户。
        active_superuser (User): 超级管理员权限验证。
        user_service (UserService): 用户服务依赖。

    Returns:
        ResponseBase[BatchOperationResult]: 批量操作结果（成功数量等）。
    """
    success_count, failed_ids = await user_service.batch_delete_users(ids=request.ids, hard_delete=request.hard_delete)
    return ResponseBase(
        data=BatchOperationResult(
            success_count=success_count,
            failed_ids=failed_ids,
            message=f"成功删除 {success_count} 个用户" if not failed_ids else "部分删除成功",
        )
    )


@router.get("/me", response_model=ResponseBase[UserResponse], summary="获取当前用户")
async def read_user_me(
    current_user: deps.CurrentUser,
) -> Any:
    """
    获取当前用户信息。

    返回当前登录用户的详细信息。

    Args:
        current_user (User): 当前登录用户 (由依赖自动注入)。

    Returns:
        ResponseBase[UserResponse]: 当前用户的详细信息。
    """
    return ResponseBase(data=current_user)


@router.put("/me", response_model=ResponseBase[UserResponse], summary="更新当前用户")
async def update_user_me(
    *,
    user_service: deps.UserServiceDep,
    user_in: UserUpdate,
    current_user: deps.CurrentUser,
) -> Any:
    """
    更新当前用户信息。

    用户自行修改个人资料（如昵称、邮箱、手机号等）。

    Args:
        user_service (UserService): 用户服务依赖。
        user_in (UserUpdate): 用户更新数据。
        current_user (User): 当前登录用户。

    Returns:
        ResponseBase[UserResponse]: 更新后的用户信息。
    """
    user = await user_service.update_user(user_id=current_user.id, obj_in=user_in)
    return ResponseBase(data=user)


@router.put("/me/password", response_model=ResponseBase[UserResponse], summary="修改密码 (当前用户)")
async def change_password_me(
    *,
    user_service: deps.UserServiceDep,
    password_data: ChangePasswordRequest,
    current_user: deps.CurrentUser,
) -> Any:
    """
    修改当前用户密码。

    需要验证旧密码是否正确。

    Args:
        user_service (UserService): 用户服务依赖。
        password_data (ChangePasswordRequest): 密码修改请求 (包含旧密码和新密码)。
        current_user (User): 当前登录用户。

    Returns:
        ResponseBase[UserResponse]: 用户信息 (密码修改成功后)。
    """
    user = await user_service.change_password(
        user_id=current_user.id,
        old_password=password_data.old_password,
        new_password=password_data.new_password,
    )
    return ResponseBase(data=user, message="密码修改成功")


@router.put("/{user_id}/password", response_model=ResponseBase[UserResponse], summary="重置密码 (管理员)")
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

    强制修改指定用户的密码，不需要知道旧密码。需要超级管理员权限。

    Args:
        user_id (UUID): 目标用户 ID。
        password_data (ResetPasswordRequest): 密码重置请求 (包含新密码)。
        current_user (User): 当前登录用户。
        active_superuser (User): 超级管理员权限验证。
        user_service (UserService): 用户服务依赖。

    Returns:
        ResponseBase[UserResponse]: 用户信息 (密码重置成功后)。
    """
    user = await user_service.reset_password(user_id=user_id, new_password=password_data.new_password)
    return ResponseBase(data=user, message="密码重置成功")


@router.get("/recycle-bin", response_model=ResponseBase[PaginatedResponse[UserResponse]], summary="获取用户回收站列表")
async def get_recycle_bin(
    *,
    page: int = 1,
    page_size: int = 20,
    active_superuser: deps.User = Depends(deps.get_current_active_superuser),
    user_service: deps.UserServiceDep,
) -> Any:
    """
    获取已删除的用户列表 (回收站)。
    仅限超级管理员。
    """
    users, total = await user_service.get_deleted_users(page=page, page_size=page_size)
    return ResponseBase(data=PaginatedResponse(total=total, page=page, page_size=page_size, items=users))


@router.get("/{user_id}", response_model=ResponseBase[UserResponse], summary="获取特定用户信息")
async def read_user_by_id(
    *,
    user_id: UUID,
    active_superuser: deps.User = Depends(deps.get_current_active_superuser),
    user_service: deps.UserServiceDep,
) -> Any:
    """
    获取特定用户的详细信息 (管理员)。

    Args:
        user_id (UUID): 目标用户 ID。
        active_superuser (User): 超级管理员权限验证。
        user_service (UserService): 用户服务依赖。

    Returns:
        ResponseBase[UserResponse]: 用户详细信息。
    """
    user = await user_service.get_user(user_id=user_id)
    return ResponseBase(data=user)


@router.put("/{user_id}", response_model=ResponseBase[UserResponse], summary="更新用户信息 (管理员)")
async def update_user(
    *,
    user_id: UUID,
    user_in: UserUpdate,
    active_superuser: deps.User = Depends(deps.get_current_active_superuser),
    user_service: deps.UserServiceDep,
) -> Any:
    """
    管理员更新用户信息。

    允许超级管理员修改任意用户的资料 (昵称、手机号、邮箱、状态等)。
    不包含密码修改 (请使用重置密码接口)。

    Args:
        user_id (UUID): 目标用户 ID。
        user_in (UserUpdate): 更新的用户数据。
        active_superuser (User): 超级管理员权限验证。
        user_service (UserService): 用户服务依赖。

    Returns:
        ResponseBase[UserResponse]: 更新后的用户信息。
    """
    user = await user_service.update_user(user_id=user_id, obj_in=user_in)
    return ResponseBase(data=user, message="用户信息更新成功")
