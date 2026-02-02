"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: session_service.py
@DateTime: 2026-01-07 00:00:00
@Docs: 在线会话管理服务（在线列表/强制下线）。
"""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.session_store import list_online_sessions, remove_online_session, remove_online_sessions
from app.core.token_store import (
    revoke_user_access_now,
    revoke_user_refresh,
    revoke_users_access_now,
    revoke_users_refresh,
)
from app.crud.crud_user import CRUDUser
from app.models.user import User
from app.schemas.session import OnlineSessionResponse


class SessionService:
    def __init__(self, db: AsyncSession, user_crud: CRUDUser):
        self.db = db
        self.user_crud = user_crud

    async def list_online(
        self, *, page: int = 1, page_size: int = 20, keyword: str | None = None
    ) -> tuple[list[OnlineSessionResponse], int]:
        sessions, total = await list_online_sessions(page=page, page_size=page_size, keyword=keyword)

        # 清理已注销/禁用/不存在的用户会话
        user_ids: list[UUID] = []
        for s in sessions:
            try:
                user_ids.append(UUID(str(s.user_id)))
            except Exception:
                # 不合法的 user_id 直接清理
                await remove_online_session(user_id=str(s.user_id))
                continue

        valid_status: dict[UUID, tuple[bool, bool]] = {}
        if user_ids:
            result = await self.db.execute(
                select(User.id, User.is_active, User.is_deleted).where(User.id.in_(user_ids))
            )
            valid_status = {row[0]: (bool(row[1]), bool(row[2])) for row in result.all()}

        items: list[OnlineSessionResponse] = []
        removed_count = 0
        for s in sessions:
            try:
                uid = UUID(str(s.user_id))
            except Exception:
                continue

            status = valid_status.get(uid)
            if status is None:
                # 用户不存在，清理会话并撤销
                await revoke_user_refresh(user_id=str(uid))
                await revoke_user_access_now(user_id=str(uid))
                await remove_online_session(user_id=str(uid))
                removed_count += 1
                continue

            is_active, is_deleted = status
            if not is_active or is_deleted:
                await revoke_user_refresh(user_id=str(uid))
                await revoke_user_access_now(user_id=str(uid))
                await remove_online_session(user_id=str(uid))
                removed_count += 1
                continue

            items.append(
                OnlineSessionResponse(
                    user_id=uid,
                    username=s.username,
                    ip=s.ip,
                    user_agent=s.user_agent,
                    login_at=datetime.fromtimestamp(float(s.login_at), tz=UTC),
                    last_seen_at=datetime.fromtimestamp(float(s.last_seen_at), tz=UTC),
                )
            )

        if removed_count:
            total = max(0, total - removed_count)
        return items, total

    async def kick_user(self, *, user_id: UUID) -> None:
        user = await self.user_crud.get(self.db, id=user_id)
        if not user:
            # 允许清理已注销/不存在用户的残留会话
            await revoke_user_refresh(user_id=str(user_id))
            await revoke_user_access_now(user_id=str(user_id))
            await remove_online_session(user_id=str(user_id))
            return

        await revoke_user_refresh(user_id=str(user_id))
        await revoke_user_access_now(user_id=str(user_id))
        await remove_online_session(user_id=str(user_id))

    async def kick_users(self, *, user_ids: list[UUID]) -> tuple[int, list[UUID]]:
        unique_ids = list(dict.fromkeys(user_ids))
        if not unique_ids:
            return 0, []

        # 对不存在的用户也清理残留会话，避免列表脏数据
        success: list[UUID] = []
        failed: list[UUID] = []

        for uid in unique_ids:
            user = await self.user_crud.get(self.db, id=uid)
            if not user:
                await revoke_user_refresh(user_id=str(uid))
                await revoke_user_access_now(user_id=str(uid))
                await remove_online_session(user_id=str(uid))
                success.append(uid)
            else:
                success.append(uid)

        if success:
            str_ids = [str(x) for x in success]
            await revoke_users_refresh(user_ids=str_ids)
            await revoke_users_access_now(user_ids=str_ids)
            await remove_online_sessions(user_ids=str_ids)

        return len(success), failed
