import pytest
from httpx import AsyncClient

from app.core.config import settings


class TestUserRestore:
    @pytest.mark.asyncio
    async def test_restore_user(self, client: AsyncClient, auth_headers: dict[str, str], db_session):
        """
        测试用户恢复功能 (创建 -> 删除 -> 恢复).
        """
        # 0. Setup
        username = "restore_user_001"
        data = {
            "username": username,
            "password": "Str0ngP@ssw0rd123",
            "email": "restore@example.com",
            "phone": "13800138022",
            "is_active": True,
        }
        res = await client.post(f"{settings.API_V1_STR}/users/", headers=auth_headers, json=data)
        assert res.status_code == 200
        user_id = res.json()["data"]["id"]

        # 1. Delete
        res = await client.request(
            "DELETE",
            f"{settings.API_V1_STR}/users/batch",
            headers=auth_headers,
            json={"ids": [user_id], "hard_delete": False},
        )
        assert res.status_code == 200

        # 2. Verify deleted in recycle bin
        res = await client.get(f"{settings.API_V1_STR}/users/recycle-bin", headers=auth_headers)
        assert res.status_code == 200
        items = res.json()["data"]["items"]
        assert any(u["id"] == user_id for u in items)

        # 3. Restore
        res = await client.post(f"{settings.API_V1_STR}/users/{user_id}/restore", headers=auth_headers)
        assert res.status_code == 200
        assert res.json()["data"]["is_deleted"] is False

        # 4. Verify NOT in recycle bin
        res = await client.get(f"{settings.API_V1_STR}/users/recycle-bin", headers=auth_headers)
        items = res.json()["data"]["items"]
        assert not any(u["id"] == user_id for u in items)

        # 5. Verify get by ID works
        res = await client.get(f"{settings.API_V1_STR}/users/{user_id}", headers=auth_headers)
        assert res.status_code == 200
        assert res.json()["data"]["username"] == username
