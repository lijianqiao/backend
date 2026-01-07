"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: test_auth_refresh.py
@DateTime: 2025-12-30 22:40:00
@Docs: Refresh Token API Tests.
"""

import asyncio

from httpx import AsyncClient

from app.core.config import settings


class TestAuthRefresh:
    async def test_login_returns_refresh_token(self, client: AsyncClient, test_user):
        response = await client.post(
            f"{settings.API_V1_STR}/auth/login",
            data={"username": "testuser", "password": "Test@123456"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        return data

    async def test_refresh_token_valid(self, client: AsyncClient, test_user):
        # 1. Login to get refresh token
        login_data = await self.test_login_returns_refresh_token(client, test_user)
        refresh_token = login_data["refresh_token"]
        old_access_token = login_data["access_token"]

        # Wait 1.1s
        await asyncio.sleep(1.1)

        # 2. Refresh
        response = await client.post(
            f"{settings.API_V1_STR}/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

        # Refresh Token Rotation：refresh 应该被轮换
        assert data["refresh_token"] != refresh_token

        # New access token should be different (validity renewed)
        # Note: In strict equality check, if generated in same second it might be same content if no jti/randomness.
        # But create_access_token typically includes exp which differs by seconds.
        assert data["access_token"] != old_access_token

        # 3. Old refresh token should be invalid now
        response2 = await client.post(
            f"{settings.API_V1_STR}/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert response2.status_code == 401

    async def test_refresh_token_invalid(self, client: AsyncClient):
        response = await client.post(
            f"{settings.API_V1_STR}/auth/refresh",
            json={"refresh_token": "invalid_token_string"},
        )
        assert response.status_code == 401
