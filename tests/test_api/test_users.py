"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: test_users.py
@DateTime: 2025-12-30 16:50:00
@Docs: 用户 API 测试.
"""

from httpx import AsyncClient

from app.core.config import settings
from app.models.user import User


class TestUsersRead:
    """用户列表接口测试"""

    async def test_read_users_success(self, client: AsyncClient, auth_headers: dict):
        """测试获取用户列表"""
        response = await client.get(
            f"{settings.API_V1_STR}/users/",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "total" in data["data"]
        assert "items" in data["data"]

    async def test_read_users_pagination(self, client: AsyncClient, auth_headers: dict):
        """测试分页参数"""
        response = await client.get(
            f"{settings.API_V1_STR}/users/",
            headers=auth_headers,
            params={"page": 1, "page_size": 5},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["page"] == 1
        assert data["data"]["page_size"] == 5

    async def test_read_users_no_auth(self, client: AsyncClient):
        """测试无认证访问"""
        response = await client.get(f"{settings.API_V1_STR}/users/")

        assert response.status_code == 401


class TestUsersCreate:
    """创建用户接口测试"""

    async def test_create_user_success(self, client: AsyncClient, auth_headers: dict):
        """测试创建用户成功"""
        response = await client.post(
            f"{settings.API_V1_STR}/users/",
            headers=auth_headers,
            json={
                "username": "apiuser",
                "phone": "13500135000",
                "password": "Test@12345",
                "email": "api@example.com",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["username"] == "apiuser"

    async def test_create_user_weak_password(self, client: AsyncClient, auth_headers: dict):
        """测试弱密码被拒绝"""
        response = await client.post(
            f"{settings.API_V1_STR}/users/",
            headers=auth_headers,
            json={
                "username": "weakuser",
                "phone": "13500135001",
                "password": "weak",
            },
        )

        assert response.status_code == 422


class TestUsersMe:
    """当前用户接口测试"""

    async def test_read_user_me(self, client: AsyncClient, auth_headers: dict):
        """测试获取当前用户信息"""
        response = await client.get(
            f"{settings.API_V1_STR}/users/me",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["username"] == "admin"

    async def test_update_user_me(self, client: AsyncClient, auth_headers: dict):
        """测试更新当前用户信息"""
        response = await client.put(
            f"{settings.API_V1_STR}/users/me",
            headers=auth_headers,
            json={"nickname": "管理员昵称"},
        )

        assert response.status_code == 200


class TestUsersPassword:
    """密码接口测试"""

    async def test_change_password_me(self, client: AsyncClient, auth_headers: dict, test_superuser: User):
        """测试修改自己密码"""
        response = await client.put(
            f"{settings.API_V1_STR}/users/me/password",
            headers=auth_headers,
            json={
                "old_password": "Admin@123456",
                "new_password": "Admin@789012",
            },
        )

        assert response.status_code == 200
        assert response.json()["message"] == "密码修改成功"

    async def test_change_password_wrong_old(self, client: AsyncClient, auth_headers: dict):
        """测试旧密码错误"""
        response = await client.put(
            f"{settings.API_V1_STR}/users/me/password",
            headers=auth_headers,
            json={
                "old_password": "wrongpassword",
                "new_password": "New@123456",
            },
        )

        assert response.status_code == 400


class TestUsersBatchDelete:
    """批量删除接口测试"""

    async def test_batch_delete_empty_list(self, client: AsyncClient, auth_headers: dict):
        """测试空列表删除"""
        response = await client.request(
            "DELETE",
            f"{settings.API_V1_STR}/users/batch",
            headers=auth_headers,
            json={"ids": [], "hard_delete": False},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["success_count"] == 0
