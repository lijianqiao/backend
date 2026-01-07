"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: sessions.py
@DateTime: 2026-01-07 00:00:00
@Docs: 在线会话 API（在线用户/强制下线/踢人）。
"""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends

from app.api import deps
from app.core.permissions import PermissionCode
from app.schemas.common import BatchOperationResult, PaginatedResponse, ResponseBase
from app.schemas.session import KickUsersRequest, OnlineSessionResponse

router = APIRouter()


@router.get(
    "/online", response_model=ResponseBase[PaginatedResponse[OnlineSessionResponse]], summary="获取在线会话列表"
)
async def list_online_sessions(
    session_service: deps.SessionServiceDep,
    current_user: deps.CurrentUser,
    _: deps.User = Depends(deps.require_permissions([PermissionCode.SESSION_LIST.value])),
    page: int = 1,
    page_size: int = 20,
) -> Any:
    items, total = await session_service.list_online(page=page, page_size=page_size)
    return ResponseBase(data=PaginatedResponse(total=total, page=page, page_size=page_size, items=items))


@router.post("/kick/{user_id}", response_model=ResponseBase[None], summary="强制下线(踢人)")
async def kick_user(
    user_id: UUID,
    session_service: deps.SessionServiceDep,
    current_user: deps.CurrentUser,
    _: deps.User = Depends(deps.require_permissions([PermissionCode.SESSION_KICK.value])),
) -> Any:
    await session_service.kick_user(user_id=user_id)
    return ResponseBase(data=None, message="已强制下线")


@router.post("/kick/batch", response_model=ResponseBase[BatchOperationResult], summary="批量强制下线")
async def kick_users(
    request: KickUsersRequest,
    session_service: deps.SessionServiceDep,
    current_user: deps.CurrentUser,
    _: deps.User = Depends(deps.require_permissions([PermissionCode.SESSION_KICK.value])),
) -> Any:
    success_count, failed_ids = await session_service.kick_users(user_ids=request.user_ids)
    return ResponseBase(
        data=BatchOperationResult(
            success_count=success_count,
            failed_ids=failed_ids,
            message=f"成功下线 {success_count} 个用户" if not failed_ids else "部分下线成功",
        )
    )
