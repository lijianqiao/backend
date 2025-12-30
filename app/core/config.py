"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: config.py
@DateTime: 2025-12-30 11:30:00
@Docs: 系统配置管理 (System Configuration).
"""

from typing import Literal

from pydantic import PostgresDsn, RedisDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    系统配置类，基于 Pydantic Settings 管理环境变量。
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    # 项目信息
    PROJECT_NAME: str = "Admin RBAC Backend"
    API_V1_STR: str = "/api/v1"

    # 环境
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    # 安全
    SECRET_KEY: str = "changethis"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 天
    PASSWORD_COMPLEXITY_ENABLED: bool = True  # 开启后需要大小写+数字+特殊字符且>=8位

    # CORS (跨域资源共享)
    BACKEND_CORS_ORIGINS: list[str] = ["*"]

    # 数据库
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "admin_rbac"
    DB_POOL_SIZE: int = 5  # 连接池大小
    DB_MAX_OVERFLOW: int = 10  # 最大溢出连接数

    # 初始化超级管理员 (Initial Superuser)
    FIRST_SUPERUSER: str = "admin"
    FIRST_SUPERUSER_PASSWORD: str = "password"
    FIRST_SUPERUSER_EMAIL: str = "admin@example.com"
    FIRST_SUPERUSER_PHONE: str = "13800138000"

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""

    @computed_field
    @property
    def REDIS_URL(self) -> RedisDsn:
        """
        根据配置生成 Redis 连接 URI.
        """
        password_part = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return RedisDsn(f"redis://{password_part}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}")

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        """
        根据配置生成 SQLAlchemy 数据库连接 URI。
        """
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )


settings = Settings()
