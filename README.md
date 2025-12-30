# FastAPI Admin RBAC Backend

基于 FastAPI + SQLAlchemy 2.0 (Async) + Pydantic v2 构建的高性能、现代化的通用后台管理系统后端。

严格遵循分层架构设计，集成了 RBAC 权限管理、全面的日志审计、事务管理以及类型安全的开发规范。

## ✨ 核心特性

### 🏗️ 架构与规范
*   **严格分层架构**: API (Controller) -> Service (Business Logic) -> CRUD (Data Access) -> Models/Schemas。
*   **异步高性能**: 全链路异步 (`async/await`)，基于 `asyncpg` 和 `uvicorn`。
*   **SQLAlchemy 2.0**: 采用最新的 SQLAlchemy 2.0 语法，支持异步 Session。
*   **深度依赖注入 (DI)**: 
    *   Service 层通过构造函数注入 CRUD 依赖，彻底解耦。
    *   API 层通过 FastAPI `Depends` 自动装配 Service 和 Repository。
*   **事务管理**: 使用 `@transactional` 装饰器自动管理事务提交与回滚，业务代码零污染。
*   **类型安全**: 全面的 Type Hinting，通过 MyPy/Pyright 严格模式检查。

### 🛡️ 安全与权限 (RBAC)
*   **RBAC 模型**: 用户 (User) - 角色 (Role) - 菜单/权限 (Menu/Permission)。
*   **JWT 认证**: 基于 OAuth2 Password Bearer 流程，支持 Token 自动刷新。
*   **数据隔离**: (TODO) 支持部门级/个人级数据权限。
*   **软删除**: 全局支持软删除 (`SoftDeleteMixin`)，查询自动过滤，删除自动标记。
*   **乐观锁**: 核心业务数据通过 `version_id` 防止并发修改冲突。

### 📊 日志与审计
*   **结构化日志**: 使用 `structlog` 输出 JSON 格式日志，支持上下文绑定 (Trace ID)。
*   **高级文件日志**:
    *   `logs/api_traffic.log`: 纯净的 API 访问流量日志。
    *   `logs/info.log`: 应用运行日志 (按天轮转 + Gzip 压缩)。
    *   `logs/error.log`: 异常堆栈日志。
*   **全局审计 (Audit Log)**:
    *   **登录日志**: 记录登录成功/失败、User Agent 解析 (设备/OS/浏览器)。
    *   **操作日志**: Middleware 自动捕获所有**写操作** (POST/PUT/DELETE) 并异步写入数据库，记录操作人、IP、耗时及状态。

## 🛠️ 技术栈

*   **Python**: 3.10+
*   **Web Framework**: FastAPI
*   **Database**: PostgreSQL + SQLAlchemy (Async) + Alembic (Migrations)
*   **Schema**: Pydantic v2
*   **Logging**: Structlog
*   **Utils**: Phonenumbers (手机号验证), User-Agents (UA解析), Password generation (Argon2/Bcrypt via pwdlib)

## 🚀 快速开始

### 1. 环境准备
确保已安装 Python 3.10+ 和 PostgreSQL 数据库。

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
