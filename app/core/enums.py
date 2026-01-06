"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: enums.py
@DateTime: 2026-01-06 00:00:00
@Docs: 枚举常量定义（用于替代魔法字符串）。
"""

from enum import Enum


class MenuType(str, Enum):
    """菜单节点类型。"""

    CATALOG = "CATALOG"
    MENU = "MENU"
    PERMISSION = "PERMISSION"
