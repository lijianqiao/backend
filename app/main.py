"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: main.py
@DateTime: 2025-12-30 12:50:00
@Docs: 应用程序入口 (Main Application Entry).
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.api import api_router
from app.core.cache import close_redis, init_redis
from app.core.config import settings
from app.core.exception_handlers import register_exception_handlers
from app.core.logger import logger, setup_logging
from app.core.middleware import RequestLogMiddleware
from app.subscribers.log_subscriber import register_log_subscribers


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI 生命周期管理: 启动与关闭事件。
    """
    setup_logging()
    logger.info("服务正在启动...")

    # 初始化 Redis
    await init_redis()

    # 注册事件订阅者
    register_log_subscribers()

    yield

    # 关闭 Redis
    await close_redis()
    logger.info("服务正在关闭...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
    default_response_class=JSONResponse,
)

# 配置 CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# 添加请求日志中间件
app.add_middleware(RequestLogMiddleware)

# 注册全局异常处理器
register_exception_handlers(app)

# 注册 API 路由
app.include_router(api_router, prefix=settings.API_V1_STR)
