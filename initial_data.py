"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: initial_data.py
@DateTime: 2025-12-30 13:05:00
@Docs: 数据初始化脚本 (支持 --reset 重置 和 --init 初始化).
"""

import argparse
import asyncio
import logging
import sys

from app.core.config import settings
from app.core.db import AsyncSessionLocal, engine
from app.crud.crud_user import user as user_crud

# 确保所有模型被导入，以便 create_all 能识别
from app.models.base import Base
from app.schemas.user import UserCreate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def reset_db() -> None:
    """
    重置数据库：删除所有表。
    """
    logger.warning("正在重置数据库 (删除所有表)...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    logger.info("数据库已重置。")


async def init_db() -> None:
    """
    初始化数据库：创建表并创建超级管理员。
    """
    logger.info("正在初始化数据库 (创建表)...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        user = await user_crud.get_by_username(db, username=settings.FIRST_SUPERUSER)
        if not user:
            logger.info(f"正在创建超级管理员: {settings.FIRST_SUPERUSER}")
            user_in = UserCreate(
                username=settings.FIRST_SUPERUSER,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                email=settings.FIRST_SUPERUSER_EMAIL,
                phone=settings.FIRST_SUPERUSER_PHONE,
                nickname="Administrator",
                is_superuser=True,
                is_active=True,
                gender="male",
            )
            await user_crud.create(db, obj_in=user_in)
            await db.commit()
            logger.info("超级管理员创建成功。")
        else:
            logger.info("超级管理员已存在，跳过创建。")


def main() -> None:
    parser = argparse.ArgumentParser(description="后台管理系统初始化脚本")
    parser.add_argument("--reset", action="store_true", help="重置数据库 (删除所有数据表)")
    parser.add_argument("--init", action="store_true", help="初始化数据库 (创建表和超级管理员)")

    args = parser.parse_args()

    if args.reset:
        asyncio.run(reset_db())

    if args.init:
        asyncio.run(init_db())

    if not args.reset and not args.init:
        # 默认行为（如果未提供参数，提示用法）
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
