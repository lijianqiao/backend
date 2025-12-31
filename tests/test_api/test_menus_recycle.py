import pytest
from httpx import AsyncClient

from app.core.config import settings


class TestMenuRecycle:
    @pytest.mark.asyncio
    async def test_recycle_bin(self, client: AsyncClient, auth_headers: dict[str, str], db_session):
        """
        测试菜单回收站功能 (创建 -> 删除 -> 回收站验证)。
        """
        # 0. Setup: Create a unique menu
        unique_name = "recycle_menu_001"
        data = {
            "title": "Recycle Menu",
            "name": unique_name,
            "path": "/recycle-menu",
            "component": "Layout",
            "icon": "el-icon-delete",
            "sort": 1,
            "is_hidden": False,
        }
        # Create
        res = await client.post(f"{settings.API_V1_STR}/menus/", headers=auth_headers, json=data)
        assert res.status_code == 200
        menu_id = res.json()["data"]["id"]

        # 1. Delete the menu
        res = await client.delete(f"{settings.API_V1_STR}/menus/{menu_id}", headers=auth_headers)
        assert res.status_code == 200

        # 2. List recycle bin
        res = await client.get(f"{settings.API_V1_STR}/menus/recycle-bin", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()["data"]
        assert "items" in data
        assert "total" in data

        # Ensure our deleted menu is in the list
        found = False
        for menu in data["items"]:
            if menu["name"] == unique_name:
                found = True
                assert menu["is_deleted"] is True
                assert menu["id"] == menu_id
                assert "created_at" in menu
                assert "updated_at" in menu
                break
        assert found

        # 3. Restore the menu
        res = await client.post(f"{settings.API_V1_STR}/menus/{menu_id}/restore", headers=auth_headers)
        assert res.status_code == 200
        assert res.json()["data"]["is_deleted"] is False

        # 4. Verify NOT in recycle bin
        res = await client.get(f"{settings.API_V1_STR}/menus/recycle-bin", headers=auth_headers)
        items = res.json()["data"]["items"]
        assert not any(m["id"] == menu_id for m in items)
