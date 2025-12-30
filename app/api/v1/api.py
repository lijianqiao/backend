from fastapi import APIRouter

from app.api.v1.endpoints import auth, logs, menus, roles, users

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Auth (认证)"])
api_router.include_router(users.router, prefix="/users", tags=["Users (用户)"])
api_router.include_router(roles.router, prefix="/roles", tags=["Roles (角色)"])
api_router.include_router(menus.router, prefix="/menus", tags=["Menus (菜单)"])
api_router.include_router(logs.router, prefix="/logs", tags=["Logs (日志)"])
