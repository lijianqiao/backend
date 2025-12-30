"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: test_roles.py
@DateTime: 2025-12-30 21:20:00
@Docs: Role API 接口测试.
"""

from httpx import AsyncClient

from app.core.config import settings


class TestRolesRead:
    """角色查询接口测试"""

    async def test_read_roles_success(self, client: AsyncClient, auth_headers: dict):
        """测试获取角色列表"""
        response = await client.get(f"{settings.API_V1_STR}/roles/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "items" in data["data"]
        # 至少默认有初始化的角色（如果 initial_data 未运行则可能为空，但测试环境通常是空的）
        # 我们可以先创建一个
        # 但我们应该尽量让测试独立。这里只检查结构。


class TestRolesCreate:
    """角色创建接口测试"""

    async def test_create_role_success(self, client: AsyncClient, auth_headers: dict):
        """测试创建角色"""
        response = await client.post(
            f"{settings.API_V1_STR}/roles/",
            headers=auth_headers,
            json={"name": "API Role", "code": "api_role", "sort": 10},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["code"] == "api_role"

    async def test_create_role_duplicate(self, client: AsyncClient, auth_headers: dict):
        """测试创建重复角色"""
        # 先创建一个
        await client.post(
            f"{settings.API_V1_STR}/roles/", headers=auth_headers, json={"name": "Dup Role", "code": "dup_role"}
        )

        # 再创建同一个 code
        response = await client.post(
            f"{settings.API_V1_STR}/roles/", headers=auth_headers, json={"name": "Dup Role 2", "code": "dup_role"}
        )
        # Service 抛出 BadRequestException，通常映射为 400
        assert response.status_code == 400


class TestRolesUpdate:
    """角色更新接口测试"""

    async def test_update_role(self, client: AsyncClient, auth_headers: dict):
        # Setup
        res = await client.post(
            f"{settings.API_V1_STR}/roles/", headers=auth_headers, json={"name": "To Update", "code": "update_api_role"}
        )
        role_id = res.json()["data"]["id"]

        # Update
        response = await client.put(
            f"{settings.API_V1_STR}/roles/{role_id}", headers=auth_headers, json={"name": "Updated Name"}
        )
        assert response.status_code == 200
        assert response.json()["data"]["name"] == "Updated Name"


class TestRolesDelete:
    """角色删除接口测试"""

    async def test_delete_role(self, client: AsyncClient, auth_headers: dict):
        # Setup
        res = await client.post(
            f"{settings.API_V1_STR}/roles/", headers=auth_headers, json={"name": "To Delete", "code": "delete_api_role"}
        )
        role_id = res.json()["data"]["id"]

        # Delete
        response = await client.delete(f"{settings.API_V1_STR}/roles/{role_id}", headers=auth_headers)
        assert response.status_code == 200

        # Verify
        await client.get(f"{settings.API_V1_STR}/roles/{role_id}", headers=auth_headers)
        assert response.json()["data"]["is_deleted"] is True

    async def test_batch_delete_roles(self, client: AsyncClient, auth_headers: dict):
        # Setup 2 roles
        ids = []
        for i in range(2):
            res = await client.post(
                f"{settings.API_V1_STR}/roles/", headers=auth_headers, json={"name": f"Batch {i}", "code": f"batch_{i}"}
            )
            ids.append(res.json()["data"]["id"])

        response = await client.request(
            "DELETE", f"{settings.API_V1_STR}/roles/batch", headers=auth_headers, json={"ids": ids}
        )
        assert response.status_code == 200
        assert response.json()["data"]["success_count"] == 2
