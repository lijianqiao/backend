"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: test_menus.py
@DateTime: 2025-12-30 21:40:00
@Docs: Menu API 接口测试.
"""

from httpx import AsyncClient

from app.core.config import settings


class TestMenusRead:
    async def test_read_menus_success(self, client: AsyncClient, auth_headers: dict):
        response = await client.get(f"{settings.API_V1_STR}/menus/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "items" in data["data"]


class TestMenusCreate:
    async def test_create_menu_success(self, client: AsyncClient, auth_headers: dict):
        response = await client.post(
            f"{settings.API_V1_STR}/menus/",
            headers=auth_headers,
            json={"title": "API Menu", "name": "ApiMenu", "path": "/api-menu", "sort": 1},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["title"] == "API Menu"


class TestMenusUpdate:
    async def test_update_menu(self, client: AsyncClient, auth_headers: dict):
        # Create
        res = await client.post(
            f"{settings.API_V1_STR}/menus/", headers=auth_headers, json={"title": "To Update", "name": "ToUpdateApi"}
        )
        menu_id = res.json()["data"]["id"]

        # Update
        response = await client.put(
            f"{settings.API_V1_STR}/menus/{menu_id}", headers=auth_headers, json={"title": "Updated Title"}
        )
        assert response.status_code == 200
        assert response.json()["data"]["title"] == "Updated Title"


class TestMenusDelete:
    async def test_delete_menu(self, client: AsyncClient, auth_headers: dict):
        # Create
        res = await client.post(
            f"{settings.API_V1_STR}/menus/", headers=auth_headers, json={"title": "To Delete", "name": "ToDelApi"}
        )
        menu_id = res.json()["data"]["id"]

        # Delete
        response = await client.delete(f"{settings.API_V1_STR}/menus/{menu_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["data"]["is_deleted"] is True

    async def test_batch_delete_menus(self, client: AsyncClient, auth_headers: dict):
        # Create 2 menus
        ids = []
        for i in range(2):
            res = await client.post(
                f"{settings.API_V1_STR}/menus/", headers=auth_headers, json={"title": f"Batch {i}", "name": f"Batch{i}"}
            )
            ids.append(res.json()["data"]["id"])

        # Batch delete
        response = await client.request(
            "DELETE", f"{settings.API_V1_STR}/menus/batch", headers=auth_headers, json={"ids": ids}
        )
        assert response.status_code == 200
        assert response.json()["data"]["success_count"] == 2
