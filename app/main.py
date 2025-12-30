"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: main.py
@DateTime: 2025-12-30 12:50:00
@Docs: 应用程序入口 (Main Application Entry).
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.api import api_router
from app.core.cache import close_redis, init_redis
from app.core.config import settings
from app.core.exceptions import CustomException
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

# 注册 API 路由
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.exception_handler(CustomException)
async def custom_exception_handler(request: Request, exc: CustomException):
    """
    自定义业务异常处理器。
    """
    return JSONResponse(
        status_code=exc.code,
        content={"error_code": exc.code, "message": exc.message, "details": exc.details},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    参数验证异常处理器 (覆盖 FastAPI 默认行为，返回 JSON)。
    """
    return JSONResponse(
        status_code=422,
        content={"error_code": 422, "message": "参数验证错误", "details": exc.errors()},
    )
