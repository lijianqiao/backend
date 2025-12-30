"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: test_logs.py
@DateTime: 2025-12-30 22:00:00
@Docs: Log API 接口测试.
"""

from httpx import AsyncClient

from app.core.config import settings


class TestLogsRead:
    async def test_read_login_logs(self, client: AsyncClient, auth_headers: dict):
        """测试获取登录日志"""
        response = await client.get(f"{settings.API_V1_STR}/logs/login", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "items" in data["data"]

    async def test_read_operation_logs(self, client: AsyncClient, auth_headers: dict):
        """测试获取操作日志"""
        response = await client.get(f"{settings.API_V1_STR}/logs/operation", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "items" in data["data"]
