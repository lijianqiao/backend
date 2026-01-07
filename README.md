# FastAPI Admin RBAC Backend

基于 FastAPI + SQLAlchemy 2.0 (Async) + Pydantic v2 构建的高性能、现代化的通用后台管理系统后端。

严格遵循分层架构设计，集成了 RBAC 权限管理、全面的日志审计、事务管理以及类型安全的开发规范。

## ✨ 核心特性

### 架构
*   **分层清晰**: API -> Service -> CRUD -> Models/Schemas。
*   **异步链路**: 基于 FastAPI + SQLAlchemy 2.0 Async。
*   **事务管理**: `@transactional` 自动提交/回滚。
*   **类型标注**: 全面 Type Hinting，便于静态检查。

### 权限
*   **RBAC**: 用户 - 角色 - 菜单/权限。
*   **JWT 认证**: OAuth2 Password Bearer，支持刷新。
*   **软删除**: 常用业务实体支持软删除与回收站。

### 日志
*   **结构化日志**: `structlog` JSON 日志，带请求上下文。
*   **审计日志**: 自动记录写操作（POST/PUT/DELETE），包含操作人、IP、耗时、状态。

## 🛠️ 技术栈

*   **Python**: 3.13+
*   **Web Framework**: FastAPI
*   **Database**: PostgreSQL + SQLAlchemy (Async) + Alembic (Migrations)
*   **Schema**: Pydantic v2
*   **Logging**: Structlog
*   **Utils**: Phonenumbers (手机号验证), User-Agents (UA解析), Password generation (Argon2/Bcrypt via pwdlib)

## 🚀 快速开始

### 1. 环境准备
确保已安装 Python 3.12+ 和 PostgreSQL 数据库。

```bash
uv venv --python 3.13
```

### 2. 配置环境变量
复制 `.env.example` 为 `.env` 并修改配置：
```bash
cp .env.example .env
# 编辑 .env 设置 SQLALCHEMY_DATABASE_URI 等
```

### 3. 安装依赖
```bash
uv sync
```

### 4. 数据库初始化
```bash
# 生成并应用迁移
uv run alembic revision --autogenerate -m "init"
uv run alembic upgrade head

# 初始化基础数据 (创建超级管理员 admin/password)
uv run initial_data.py --init
```

### 5. 启动服务
```bash
uv run start.py
```
访问文档: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 6. 运行测试
```bash
## 安装测试依赖
uv sync --dev

## 运行测试
uv run pytest
```

## 📂 目录结构

```text
backend/
├── app/
│   ├── api/            # API 接口层 (Controller)
│   ├── core/           # 核心配置 (Config, Security, Logger, Middleware, Decorators)
│   ├── crud/           # 数据访问层 (Repository)
│   ├── models/         # SQLAlchemy 数据模型
│   ├── schemas/        # Pydantic 数据校验模型
│   ├── services/       # 业务逻辑层 (Service)
│   └── main.py         # 应用入口
├── alembic/            # 数据库迁移脚本
├── logs/               # 运行时日志 (自动生成)
├── initial_data.py     # 数据初始化脚本
├── start.py            # 启动脚本
└── .env                # 环境变量配置
```

## 📝 开发指南

### 新增功能流程
1.  **Model**: 在 `app/models` 定义数据库模型。
2.  **Schema**: 在 `app/schemas` 定义 Pydantic 模型 (Create/Update/Response)。
3.  **CRUD**: 在 `app/crud` 继承 `CRUDBase` 实现数据操作。
4.  **Service**: 在 `app/services` 编写业务逻辑，使用 `@transactional` 管理事务。
5.  **API**: 在 `app/api/v1/endpoints` 编写路由，注入 Service。

### 代码规范
*   遵循 PEP8。
*   所有业务异常抛出 `CustomException`。
*   所有数据库写操作必须经过 Audit Middleware (自动) 或 Service 层事务。
