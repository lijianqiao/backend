"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: token_store.py
@DateTime: 2026-01-07 00:00:00
@Docs: Refresh Token 存储与撤销（主流方案：Redis 优先，降级内存存储）。

说明：
- 主要用于 Refresh Token 的“单端有效 + 轮换（rotation）+ 可撤销（revocation）”。
- 优先使用 Redis 以支持多进程/多实例；若 Redis 不可用则降级为进程内内存存储（仅适合本地/测试）。
"""

import asyncio
import time
from collections.abc import Iterable

from app.core.cache import redis_client
from app.core.config import settings
from app.core.logger import logger

_REVOKED_JTI = "__revoked__"


def _default_ttl_seconds() -> int:
    return int(settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600)


class RefreshTokenStore:
    async def set_current_jti(self, user_id: str, jti: str, ttl_seconds: int) -> None:
        raise NotImplementedError

    async def get_current_jti(self, user_id: str) -> str | None:
        raise NotImplementedError

    async def revoke_user(self, user_id: str) -> None:
        raise NotImplementedError

    async def revoke_users(self, user_ids: Iterable[str]) -> None:
        for uid in user_ids:
            await self.revoke_user(uid)


def _refresh_key(user_id: str) -> str:
    return f"v1:auth:refresh:{user_id}"


class RedisRefreshTokenStore(RefreshTokenStore):
    async def set_current_jti(self, user_id: str, jti: str, ttl_seconds: int) -> None:
        if redis_client is None:
            return
        key = _refresh_key(user_id)
        try:
            await redis_client.setex(key, ttl_seconds, jti)
        except Exception as e:
            logger.warning(f"refresh token 存储失败(REDIS): {e}")

    async def get_current_jti(self, user_id: str) -> str | None:
        if redis_client is None:
            return None
        key = _refresh_key(user_id)
        try:
            value = await redis_client.get(key)
            if value:
                if isinstance(value, (bytes, bytearray)):
                    return value.decode("utf-8")
                return str(value)
        except Exception as e:
            logger.warning(f"refresh token 读取失败(REDIS): {e}")
        return None

    async def revoke_user(self, user_id: str) -> None:
        if redis_client is None:
            return
        key = _refresh_key(user_id)
        try:
            await redis_client.setex(key, _default_ttl_seconds(), _REVOKED_JTI)
        except Exception as e:
            logger.warning(f"refresh token 撤销失败(REDIS): {e}")


class MemoryRefreshTokenStore(RefreshTokenStore):
    """进程内 Refresh Token 存储（仅用于本地/测试降级）。"""

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        # user_id -> (jti, expire_at)
        self._data: dict[str, tuple[str, float]] = {}

    async def set_current_jti(self, user_id: str, jti: str, ttl_seconds: int) -> None:
        expire_at = time.time() + max(1, int(ttl_seconds))
        async with self._lock:
            self._data[user_id] = (jti, expire_at)

    async def get_current_jti(self, user_id: str) -> str | None:
        now = time.time()
        async with self._lock:
            value = self._data.get(user_id)
            if not value:
                return None
            jti, expire_at = value
            if expire_at <= now:
                self._data.pop(user_id, None)
                return None
            return jti

    async def revoke_user(self, user_id: str) -> None:
        expire_at = time.time() + max(1, _default_ttl_seconds())
        async with self._lock:
            self._data[user_id] = (_REVOKED_JTI, expire_at)


_memory_store = MemoryRefreshTokenStore()
_redis_store = RedisRefreshTokenStore()


def get_refresh_token_store() -> RefreshTokenStore:
    # Redis 可用时优先；否则降级内存。
    return _redis_store if redis_client is not None else _memory_store


async def set_user_refresh_jti(*, user_id: str, jti: str, ttl_seconds: int) -> None:
    await get_refresh_token_store().set_current_jti(user_id, jti, ttl_seconds)


async def get_user_refresh_jti(*, user_id: str) -> str | None:
    return await get_refresh_token_store().get_current_jti(user_id)


async def revoke_user_refresh(*, user_id: str) -> None:
    await get_refresh_token_store().revoke_user(user_id)


async def revoke_users_refresh(*, user_ids: Iterable[str]) -> None:
    await get_refresh_token_store().revoke_users(user_ids)
