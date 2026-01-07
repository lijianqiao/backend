"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: session_store.py
@DateTime: 2026-01-07 00:00:00
@Docs: 在线会话存储（Redis 优先，降级内存）。

说明：
- 用于“在线用户列表 / 最后活跃时间 / 强制下线”。
- 以 refresh 会话为主：登录/刷新时 touch；注销/强制下线时 remove。
"""

import asyncio
import json
import time
from collections.abc import Iterable
from dataclasses import asdict, dataclass

from app.core.cache import redis_client
from app.core.config import settings
from app.core.logger import logger


@dataclass(frozen=True, slots=True)
class OnlineSession:
    user_id: str
    username: str
    ip: str | None
    user_agent: str | None
    login_at: float
    last_seen_at: float


def _online_zset_key() -> str:
    return "v1:auth:online:zset"


def _session_key(user_id: str) -> str:
    return f"v1:auth:session:{user_id}"


def _default_online_ttl_seconds() -> int:
    return int(settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600)


class SessionStore:
    async def upsert_session(self, session: OnlineSession, ttl_seconds: int) -> None:  # pragma: no cover
        raise NotImplementedError

    async def get_session(self, user_id: str) -> OnlineSession | None:  # pragma: no cover
        raise NotImplementedError

    async def remove_session(self, user_id: str) -> None:  # pragma: no cover
        raise NotImplementedError

    async def list_online(self, *, page: int, page_size: int) -> tuple[list[OnlineSession], int]:  # pragma: no cover
        raise NotImplementedError

    async def remove_sessions(self, user_ids: Iterable[str]) -> None:  # pragma: no cover
        for uid in user_ids:
            await self.remove_session(uid)


class RedisSessionStore(SessionStore):
    async def upsert_session(self, session: OnlineSession, ttl_seconds: int) -> None:
        if redis_client is None:
            return

        now = time.time()
        zkey = _online_zset_key()
        skey = _session_key(session.user_id)

        try:
            await redis_client.zadd(zkey, {session.user_id: float(session.last_seen_at)})
            await redis_client.setex(skey, max(1, int(ttl_seconds)), json.dumps(asdict(session), ensure_ascii=False))
            # 在线 zset 本身设置一个 TTL，避免长期无人用时残留
            await redis_client.expire(zkey, max(60, int(_default_online_ttl_seconds())))
        except Exception as e:
            logger.warning(f"在线会话写入失败(REDIS): {e}")

        # 轻量清理：移除过期成员（last_seen 太久）
        try:
            cutoff = now - max(60, int(ttl_seconds))
            await redis_client.zremrangebyscore(zkey, 0, cutoff)
        except Exception:
            pass

    async def get_session(self, user_id: str) -> OnlineSession | None:
        if redis_client is None:
            return None

        skey = _session_key(user_id)
        try:
            raw = await redis_client.get(skey)
            if not raw:
                return None
            data = json.loads(raw)
            return OnlineSession(
                user_id=str(data.get("user_id")),
                username=str(data.get("username")),
                ip=data.get("ip"),
                user_agent=data.get("user_agent"),
                login_at=float(data.get("login_at")),
                last_seen_at=float(data.get("last_seen_at")),
            )
        except Exception as e:
            logger.warning(f"在线会话读取失败(REDIS): {e}")
            return None

    async def remove_session(self, user_id: str) -> None:
        if redis_client is None:
            return

        zkey = _online_zset_key()
        skey = _session_key(user_id)
        try:
            await redis_client.zrem(zkey, user_id)
            await redis_client.delete(skey)
        except Exception as e:
            logger.warning(f"在线会话删除失败(REDIS): {e}")

    async def list_online(self, *, page: int, page_size: int) -> tuple[list[OnlineSession], int]:
        if redis_client is None:
            return [], 0

        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 20
        if page_size > 100:
            page_size = 100

        zkey = _online_zset_key()

        try:
            total = int(await redis_client.zcard(zkey))
            start = (page - 1) * page_size
            end = start + page_size - 1
            user_ids = await redis_client.zrevrange(zkey, start, end)
        except Exception as e:
            logger.warning(f"在线会话列表读取失败(REDIS): {e}")
            return [], 0

        sessions: list[OnlineSession] = []
        for uid in user_ids:
            session = await self.get_session(str(uid))
            if session is not None:
                sessions.append(session)

        return sessions, total


class MemorySessionStore(SessionStore):
    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        # user_id -> (session, expire_at)
        self._data: dict[str, tuple[OnlineSession, float]] = {}

    async def upsert_session(self, session: OnlineSession, ttl_seconds: int) -> None:
        expire_at = time.time() + max(1, int(ttl_seconds))
        async with self._lock:
            self._data[session.user_id] = (session, expire_at)

    async def get_session(self, user_id: str) -> OnlineSession | None:
        now = time.time()
        async with self._lock:
            value = self._data.get(user_id)
            if not value:
                return None
            session, expire_at = value
            if expire_at <= now:
                self._data.pop(user_id, None)
                return None
            return session

    async def remove_session(self, user_id: str) -> None:
        async with self._lock:
            self._data.pop(user_id, None)

    async def list_online(self, *, page: int, page_size: int) -> tuple[list[OnlineSession], int]:
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 20
        if page_size > 100:
            page_size = 100

        now = time.time()
        async with self._lock:
            # 清理过期
            expired = [uid for uid, (_, exp) in self._data.items() if exp <= now]
            for uid in expired:
                self._data.pop(uid, None)

            items = [s for (s, _) in self._data.values()]

        items.sort(key=lambda x: x.last_seen_at, reverse=True)
        total = len(items)
        start = (page - 1) * page_size
        end = start + page_size
        return items[start:end], total


_memory_store = MemorySessionStore()
_redis_store = RedisSessionStore()


def get_session_store() -> SessionStore:
    return _redis_store if redis_client is not None else _memory_store


async def touch_online_session(
    *,
    user_id: str,
    username: str,
    ip: str | None,
    user_agent: str | None,
    ttl_seconds: int | None = None,
    login_at: float | None = None,
) -> None:
    now = time.time()
    ttl = _default_online_ttl_seconds() if ttl_seconds is None else int(ttl_seconds)

    existing = await get_session_store().get_session(user_id)
    session = OnlineSession(
        user_id=user_id,
        username=username,
        ip=ip,
        user_agent=user_agent,
        login_at=float(login_at if login_at is not None else (existing.login_at if existing else now)),
        last_seen_at=now,
    )
    await get_session_store().upsert_session(session, ttl_seconds=ttl)


async def remove_online_session(*, user_id: str) -> None:
    await get_session_store().remove_session(user_id)


async def remove_online_sessions(*, user_ids: Iterable[str]) -> None:
    await get_session_store().remove_sessions(user_ids)


async def list_online_sessions(*, page: int = 1, page_size: int = 20) -> tuple[list[OnlineSession], int]:
    return await get_session_store().list_online(page=page, page_size=page_size)
