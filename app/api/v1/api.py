"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: api.py
@DateTime: 2025-12-30 15:30:00
@Docs: 动态 API 路由注册模块 (Dynamic API discovery).
"""

import importlib
import pkgutil
from pathlib import Path
from types import ModuleType

from fastapi import APIRouter

from app.api.v1 import endpoints

api_router = APIRouter()


def auto_include_routers() -> None:
    """
    自动扫描 app.api.v1.endpoints 包下的所有模块，
    如果模块中有 'router' 属性，则注册到 api_router。
    默认前缀为模块名 (例如 auth.py -> /auth)。
    """
    package_name = endpoints.__name__
    package_path = Path(endpoints.__file__).parent

    for _, module_name, _ in pkgutil.iter_modules([str(package_path)]):
        full_module_name = f"{package_name}.{module_name}"
        try:
            module: ModuleType = importlib.import_module(full_module_name)
            if hasattr(module, "router"):
                router_instance = module.router
                # 使用模块名作为 Tag 和 Prefix
                tag_name = module_name.capitalize()
                prefix = f"/{module_name}"

                api_router.include_router(router_instance, prefix=prefix, tags=[tag_name])
        except Exception as e:
            print(f"Failed to load router from {full_module_name}: {e}")


# 执行自动注册
auto_include_routers()
