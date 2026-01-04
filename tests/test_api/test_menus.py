"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: test_menus.py
@DateTime: 2025-12-30 21:40:00
@Docs: Menu API 接口测试.
"""

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.crud.crud_menu import menu as menu_crud
from app.crud.crud_role import role as role_crud
from app.models.rbac import UserRole
from app.schemas.menu import MenuCreate
from app.schemas.role import RoleCreate


class TestMenusRead:
    async def test_read_menus_success(self, client: AsyncClient, auth_headers: dict):
        response = await client.get(f"{settings.API_V1_STR}/menus/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "items" in data["data"]


class TestMenusMe:
    async def test_get_my_menus_superuser(self, client: AsyncClient, auth_headers: dict):
        res = await client.get(f"{settings.API_V1_STR}/menus/me", headers=auth_headers)
        assert res.status_code == 200
        body = res.json()
        assert body["code"] == 200
        assert isinstance(body["data"], list)

    async def test_get_my_menus_normal_user_no_roles(self, client: AsyncClient, test_user):
        login_res = await client.post(
            f"{settings.API_V1_STR}/auth/login",
            data={"username": "testuser", "password": "Test@123456"},
        )
        assert login_res.status_code == 200
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        res = await client.get(f"{settings.API_V1_STR}/menus/me", headers=headers)
        assert res.status_code == 200
        body = res.json()
        assert body["code"] == 200
        assert isinstance(body["data"], list)

    async def test_read_menus_success_with_children(self, client: AsyncClient, auth_headers: dict):
        # 创建父菜单
        parent_res = await client.post(
            f"{settings.API_V1_STR}/menus/",
            headers=auth_headers,
            json={"title": "Parent Menu", "name": "ParentMenu", "path": "/parent", "sort": 1},
        )
        assert parent_res.status_code == 200
        parent_id = parent_res.json()["data"]["id"]

        # 创建子菜单
        child_res = await client.post(
            f"{settings.API_V1_STR}/menus/",
            headers=auth_headers,
            json={
                "title": "Child Menu",
                "name": "ChildMenu",
                "parent_id": parent_id,
                "path": "/parent/child",
                "sort": 2,
            },
        )
        assert child_res.status_code == 200

        # 读取列表：不应因 children 懒加载触发 MissingGreenlet
        response = await client.get(f"{settings.API_V1_STR}/menus/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "items" in data["data"]


class TestMenusOptions:
    async def test_get_menu_options_requires_permission_for_normal_user(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user,
    ):
        # 构造三层菜单树，确保序列化不会触发 children 懒加载
        root = await menu_crud.create(
            db_session,
            obj_in=MenuCreate(
                title="RootOpt",
                name="RootOpt",
                parent_id=None,
                path="/root-opt",
                component=None,
                icon=None,
                sort=1,
                is_hidden=False,
                permission=None,
            ),
        )
        child = await menu_crud.create(
            db_session,
            obj_in=MenuCreate(
                title="ChildOpt",
                name="ChildOpt",
                parent_id=root.id,
                path="/root-opt/child",
                component=None,
                icon=None,
                sort=2,
                is_hidden=False,
                permission=None,
            ),
        )
        await menu_crud.create(
            db_session,
            obj_in=MenuCreate(
                title="GrandChildOpt",
                name="GrandChildOpt",
                parent_id=child.id,
                path="/root-opt/child/grand",
                component=None,
                icon=None,
                sort=3,
                is_hidden=False,
                permission=None,
            ),
        )

        # 1) 创建权限点菜单（menu:options:list）
        perm_menu = await menu_crud.create(
            db_session,
            obj_in=MenuCreate(
                title="菜单-可分配选项",
                name="PermMenuOptionsListTest",
                parent_id=None,
                path=None,
                component=None,
                icon=None,
                sort=0,
                is_hidden=True,
                permission="menu:options:list",
            ),
        )

        # 2) 创建角色并绑定该权限菜单
        role = await role_crud.create(
            db_session,
            obj_in=RoleCreate(
                name="OptionsRole", code="options_role", description=None, sort=0, menu_ids=[perm_menu.id]
            ),
        )

        # 3) 绑定用户-角色
        db_session.add(UserRole(user_id=test_user.id, role_id=role.id))
        await db_session.commit()

        # 4) 用普通用户登录
        login_res = await client.post(
            f"{settings.API_V1_STR}/auth/login",
            data={"username": "testuser", "password": "Test@123456"},
        )
        assert login_res.status_code == 200
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 5) 访问 options
        res = await client.get(f"{settings.API_V1_STR}/menus/options", headers=headers)
        assert res.status_code == 200
        body = res.json()
        assert body["code"] == 200
        assert isinstance(body["data"], list)


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
