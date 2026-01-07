"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: test_auth_logout.py
@DateTime: 2026-01-07 00:00:00
@Docs: Logout API Tests.
"""

from httpx import AsyncClient

from app.core.config import settings


class TestAuthLogout:
    async def test_logout_revokes_refresh_token(self, client: AsyncClient, test_superuser) -> None:
        # 1) login -> get refresh
        resp = await client.post(
            f"{settings.API_V1_STR}/auth/login",
            data={"username": "admin", "password": "Admin@123456"},
        )
        assert resp.status_code == 200
        login_data = resp.json()
        refresh_token = login_data["refresh_token"]
        access_token = login_data["access_token"]

        # 2) logout
        resp2 = await client.post(
            f"{settings.API_V1_STR}/auth/logout",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert resp2.status_code == 200
        data2 = resp2.json()
        assert data2["code"] == 200

        # 3) old refresh should not work
        resp3 = await client.post(
            f"{settings.API_V1_STR}/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert resp3.status_code == 401

    async def test_logout_requires_auth(self, client: AsyncClient) -> None:
        resp = await client.post(f"{settings.API_V1_STR}/auth/logout")
        assert resp.status_code == 401
