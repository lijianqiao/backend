# 部门管理测试文档

本文档用于补全部门管理（Department/Dept）的测试用例清单与编写指引，覆盖 CRUD、Schemas、Services、API 四层。

## 1. 测试目标

- 覆盖部门树与分页查询的核心逻辑：过滤、搜索、排序、层级构建。
- 覆盖新增的 `keyword` 搜索能力：部门名称/部门编码/负责人（leader）三字段。
- 覆盖软删除/回收站/恢复/批量操作的正确性。
- 避免异步 SQLAlchemy 下触发 relationship 懒加载（`MissingGreenlet`）的回归。

## 2. 建议的测试文件结构

- CRUD：`tests/test_crud/test_crud_dept.py`
- Schemas：`tests/test_schemas/test_dept.py`
- Services：`tests/test_services/test_dept_service.py`
- API：`tests/test_api/test_depts.py`

> 说明：当前项目按模块拆分测试（`tests/test_api/*`, `tests/test_crud/*`, `tests/test_services/*`, `tests/test_schemas/*`），部门管理建议沿用同样结构。

## 3. 公共准备（建议复用 fixtures）

### 3.1 数据准备建议

最小可复用数据集（建议每个测试用例按需创建，避免用全局固定数据导致耦合）：

- 根部门 A：`name="总部" code="HQ" leader="张三" sort=1`
- 子部门 A1：`name="研发" code="RD" leader="李四" parent_id=A.id sort=1`
- 子部门 A2：`name="测试" code="QA" leader="王五" parent_id=A.id sort=2`
- 根部门 B：`name="分部" code="BR" leader="赵六" sort=2`

### 3.2 账号与权限

API 层测试建议复用现有登录/鉴权相关 fixture：
- 使用管理员/超级管理员 token
- 或直接复用项目里已有的 `client` / `authorized_client`（以 `tests/conftest.py` 为准）

## 4. CRUD 层测试（CRUDDept）

目标对象：`app/crud/crud_dept.py` 的 `CRUDDept`

### 4.1 get_multi_paginated()

必测点：
- 基础分页：
  - page=1/page_size=20 返回数量正确
  - total 统计正确
- 软删除过滤：
  - `include_deleted=False` 时不返回 `is_deleted=True`
  - `include_deleted=True` 时包含已删除记录
- `is_active` 过滤：
  - `is_active=True/False` 时只返回对应状态
- `keyword` 搜索（三字段）：
  - keyword 命中 `Department.name`
  - keyword 命中 `Department.code`
  - keyword 命中 `Department.leader`
  - keyword 不命中返回空
- 排序：
  - 按 `sort asc, created_at desc` 的整体顺序稳定

### 4.2 get_tree()

必测点：
- 基础：返回的是“用于构建树的部门列表”（非仅顶层）
- 软删除过滤：
  - `include_deleted=False` 时不包含已删除
- `is_active` 过滤：
  - `is_active` 参数生效
- `keyword` 搜索（三字段）：
  - 命中 name/code/leader 的记录会被返回
  - 不命中返回空列表

> 注意：树构建在 Service 层完成，CRUD 层只需验证“过滤+搜索+排序”的正确性。

### 4.3 其他基础方法

按需补充（建议覆盖）：
- `exists_code()`：已存在/不存在、排除自身 `exclude_id` 场景
- `has_children()`：有子部门/无子部门
- `has_users()`：部门下有关联用户/无用户
- `get_children_ids()`：递归获取多层子部门 ID 的完整性

## 5. Schemas 层测试（DeptCreate/DeptUpdate/DeptResponse）

目标对象：`app/schemas/dept.py`

必测点：
- `DeptCreate`：
  - `name/code` 非空、长度限制
  - `sort` 非负
  - `email` 格式校验（可选）
- `DeptUpdate`：
  - 可选字段为 None 时可通过校验
  - `sort` 非负
- `DeptResponse`：
  - `children` 默认应为空列表且互不共享（`default_factory=list`）

## 6. Service 层测试（DeptService）

目标对象：`app/services/dept_service.py`

### 6.1 get_dept_tree()

必测点：
- 能构建多级树结构：
  - roots 数量正确
  - children 挂载正确
  - children 按 `sort` 排序
- 过滤：
  - `is_active` 过滤生效
  - 软删除子节点不出现在树中（`is_deleted=True` 的节点不应出现在 children）
- 搜索：
  - `keyword` 会传递到 CRUD 层并生效（name/code/leader）
- 防循环：
  - 若出现异常数据（循环引用），`visited` 能避免无限递归（至少保证函数返回且不抛递归错误）

### 6.2 create/update/delete/restore

必测点（建议按最小闭环覆盖）：
- create：code 重复报错；parent 不存在报错
- update：
  - code 重复（排除自身）
  - parent 不能是自身
  - parent 不能设置为自己的子部门（形成循环）
- delete：
  - 有子部门不可删
  - 有用户不可删
- restore：不存在或未删除时报错

## 7. API 层测试（/api/v1/depts）

目标对象：`app/api/v1/endpoints/depts.py`

### 7.1 GET /tree

必测点：
- 正常返回 `ResponseBase[list[DeptResponse]]`
- 支持 `keyword`：name/code/leader 搜索
- 支持 `is_active` 过滤

> 说明：当前实现是“先在 SQL 层过滤，再构建树”。如果你期望“命中子节点时自动补齐祖先路径”，需要单独定义行为并为其加测试。

### 7.2 GET /

必测点：
- 分页字段 `page/page_size/total/items` 正确
- 支持 `keyword`：name/code/leader 搜索
- 支持 `is_active` 过滤

### 7.3 POST /、PUT /{id}、DELETE /{id}

必测点：
- 创建成功返回字段完整
- 更新成功 message 正确
- 删除成功（软删除）
- 异常场景：不存在/权限不足/参数校验失败

### 7.4 回收站与批量操作

按需覆盖：
- GET /recycle-bin（需超级管理员）
- POST /{id}/restore（需超级管理员）
- DELETE /batch
- POST /batch/restore

## 8. 运行方式

项目推荐（使用 uv）：

```bash
uv run pytest
```

或使用虚拟环境 Python：

```bash
D:/project/admin-rbac/backend/.venv/Scripts/python.exe -m pytest -q
```

## 9. 验收标准（建议）

- CRUD/Service/API/Schemas 至少各有 1 个基础用例覆盖主链路。
- `keyword` 搜索：name/code/leader 三字段各至少 1 个用例。
- 部门树：至少覆盖 2 层结构构建与排序。
- 不出现 `MissingGreenlet` 相关 500 回归。
