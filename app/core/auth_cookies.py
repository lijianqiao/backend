"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: auth_cookies.py
@DateTime: 2026-01-08 00:00:00
@Docs: 认证 Cookie 工具（Refresh Token + CSRF）。

约定：
- Refresh Token 放 HttpOnly Cookie。
- CSRF Token 放非 HttpOnly Cookie，前端读取后在请求头 X-CSRF-Token 回传。
"""

import hashlib
import hmac
import secrets
import time
from typing import Literal

from fastapi import Response

from app.core.config import settings


def _csrf_sign(nonce: str, ts: int, subject: str | None = None) -> str:
    if subject:
        msg = f"{nonce}.{ts}.{subject}"
    else:
        msg = f"{nonce}.{ts}"
    return hmac.new(settings.SECRET_KEY.encode("utf-8"), msg.encode("utf-8"), hashlib.sha256).hexdigest()


def generate_csrf_token(subject: str | None = None) -> str:
    nonce = secrets.token_urlsafe(16)
    ts = int(time.time())
    sig = _csrf_sign(nonce, ts, subject)
    if subject:
        return f"{nonce}.{ts}.{subject}.{sig}"
    return f"{nonce}.{ts}.{sig}"


def validate_csrf_token(token: str, *, max_age_seconds: int | None = None, subject: str | None = None) -> bool:
    if not token:
        return False
    parts = token.split(".")
    if len(parts) == 4:
        nonce, ts_str, token_subject, sig = parts
        if subject and token_subject != subject:
            return False
        try:
            ts = int(ts_str)
        except Exception:
            return False
        expected = _csrf_sign(nonce, ts, token_subject)
    elif len(parts) == 3:
        nonce, ts_str, sig = parts
        if subject:
            # 需要绑定用户时，旧格式 token 不予放行
            return False
        try:
            ts = int(ts_str)
        except Exception:
            return False
        expected = _csrf_sign(nonce, ts, None)
    else:
        return False

    if not hmac.compare_digest(expected, sig):
        return False

    if max_age_seconds is not None:
        now = int(time.time())
        # 允许 60s 时钟偏差
        if ts > now + 60:
            return False
        if now - ts > int(max_age_seconds):
            return False

    return True


def _refresh_cookie_path() -> str:
    # refresh_token 不需要被前端读取，尽量缩小发送范围
    return f"{settings.API_V1_STR}/auth"


def _csrf_cookie_path() -> str:
    # csrf_token 需要被前端在任意页面读取并回传请求头，因此必须放宽到 /
    return "/"


def refresh_cookie_name() -> str:
    return getattr(settings, "AUTH_REFRESH_COOKIE_NAME", "refresh_token")


def csrf_cookie_name() -> str:
    return getattr(settings, "AUTH_CSRF_COOKIE_NAME", "csrf_token")


def csrf_header_name() -> str:
    return getattr(settings, "AUTH_CSRF_HEADER_NAME", "X-CSRF-Token")


def cookie_domain() -> str | None:
    v = getattr(settings, "AUTH_COOKIE_DOMAIN", None)
    if v is None:
        return None
    s = str(v).strip()
    if not s:
        return None
    if s.lower() in ("none", "null"):
        return None
    return s


def cookie_secure() -> bool:
    return bool(getattr(settings, "AUTH_COOKIE_SECURE", settings.ENVIRONMENT != "local"))


def cookie_samesite() -> Literal["lax", "strict", "none"]:
    v = str(getattr(settings, "AUTH_COOKIE_SAMESITE", "lax")).lower().strip()
    if v not in ("lax", "strict", "none"):
        return "lax"
    return v  # type: ignore[return-value]


def set_refresh_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key=refresh_cookie_name(),
        value=refresh_token,
        httponly=True,
        secure=cookie_secure(),
        samesite=cookie_samesite(),
        path=_refresh_cookie_path(),
        domain=cookie_domain(),
        max_age=int(settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600),
    )


def set_csrf_cookie(response: Response, csrf_token: str) -> None:
    response.set_cookie(
        key=csrf_cookie_name(),
        value=csrf_token,
        httponly=False,
        secure=cookie_secure(),
        samesite=cookie_samesite(),
        path=_csrf_cookie_path(),
        domain=cookie_domain(),
        max_age=int(settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600),
    )


def clear_auth_cookies(response: Response) -> None:
    # delete_cookie 默认会把值清掉；path/domain 必须与 set_cookie 一致
    response.delete_cookie(key=refresh_cookie_name(), path=_refresh_cookie_path(), domain=cookie_domain())
    response.delete_cookie(key=csrf_cookie_name(), path=_csrf_cookie_path(), domain=cookie_domain())
