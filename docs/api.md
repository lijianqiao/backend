# Admin RBAC Backend

Version: 0.1.0

## 基础路由：`http://localhost:8000`

[TOC]

## Auth

### 用户登录

**URL**: `/api/v1/auth/login`

**Method**: `POST`

**Description**:

OAuth2 兼容的 Token 登录接口。

验证用户名和密码，返回短期有效的 Access Token 和长期有效的 Refresh Token。
每个 IP 每分钟最多允许 5 次请求。

Args:
request (Request): 请求对象，用于获取 IP 地址。
background_tasks (BackgroundTasks): 后台任务，用于异步记录登录日志。
form_data (OAuth2PasswordRequestForm): 表单数据，包含 username 和 password。
auth_service (AuthService): 认证服务依赖。

Returns:
Token: 包含 Access Token 和 Refresh Token 的响应对象。

Raises:
CustomException: 当用户名或密码错误时抛出 400 错误。

#### Request Body (application/x-www-form-urlencoded)

| 参数名          | 类型     | 必填 | 描述          |
| :-------------- | :------- | :--- | :------------ |
| `grant_type`    | `string` | 否   | Grant Type    |
| `username`      | `string` | 是   | Username      |
| `password`      | `string` | 是   | Password      |
| `scope`         | `string` | 否   | Scope         |
| `client_id`     | `string` | 否   | Client Id     |
| `client_secret` | `string` | 否   | Client Secret |

#### Responses

**Status Code**: `200` - Successful Response

Format: `application/json`

| 参数名          | 类型     | 必填 | 描述          |
| :-------------- | :------- | :--- | :------------ |
| `access_token`  | `string` | 是   | Access Token  |
| `refresh_token` | `string` | 是   | Refresh Token |
| `token_type`    | `string` | 是   | Token Type    |

**Status Code**: `422` - Validation Error

Format: `application/json`

| 参数名   | 类型                     | 必填 | 描述   |
| :------- | :----------------------- | :--- | :----- |
| `detail` | `Array[ValidationError]` | 否   | Detail |

---

### 刷新令牌

**URL**: `/api/v1/auth/refresh`

**Method**: `POST`

**Description**:

使用 Refresh Token 换取新的 Access Token。

当 Access Token 过期时，可以使用此接口获取新的 Access Token，而无需重新登录。

Args:
token_in (TokenRefresh): 包含 refresh_token 的请求体。
auth_service (AuthService): 认证服务依赖。

Returns:
Token: 包含新的 Access Token 和 (可选) 新的 Refresh Token。

Raises:
UnauthorizedException: 当 Refresh Token 无效或过期时抛出 401 错误。

#### Request Body (application/json)

| 参数名          | 类型     | 必填 | 描述          |
| :-------------- | :------- | :--- | :------------ |
| `refresh_token` | `string` | 是   | Refresh Token |

#### Responses

**Status Code**: `200` - Successful Response

Format: `application/json`

| 参数名          | 类型     | 必填 | 描述          |
| :-------------- | :------- | :--- | :------------ |
| `access_token`  | `string` | 是   | Access Token  |
| `refresh_token` | `string` | 是   | Refresh Token |
| `token_type`    | `string` | 是   | Token Type    |

**Status Code**: `422` - Validation Error

Format: `application/json`

| 参数名   | 类型                     | 必填 | 描述   |
| :------- | :----------------------- | :--- | :----- |
| `detail` | `Array[ValidationError]` | 否   | Detail |

---

### 测试令牌有效性

**URL**: `/api/v1/auth/test-token`

**Method**: `POST`

**Description**:

测试 Access Token 是否有效。

仅用于验证当前请求携带的 Token 是否合法，并返回当前用户信息。

Args:
current_user (User): 当前登录用户 (由依赖自动注入)。

Returns:
ResponseBase[UserResponse]: 包含当前用户信息的统一响应结构。

#### Responses

**Status Code**: `200` - Successful Response

Format: `application/json`

| 参数名    | 类型           | 必填 | 描述    |
| :-------- | :------------- | :--- | :------ |
| `code`    | `integer`      | 否   | Code    |
| `message` | `string`       | 否   | Message |
| `data`    | `UserResponse` | 否   |         |

---

## Dashboard

### 获取仪表盘统计

**URL**: `/api/v1/dashboard/summary`

**Method**: `GET`

**Description**:

获取仪表盘统计数据。

聚合查询用户、角色、菜单的总量，以及今日登录/操作次数、近七日登录趋势和最新登录记录。
数据用于前端仪表盘首页展示。

Args:
current_user (User): 当前登录用户。
service (DashboardService): 仪表盘服务依赖。

Returns:
ResponseBase[DashboardStats]: 包含各项统计指标的响应对象。

#### Responses

**Status Code**: `200` - Successful Response

Format: `application/json`

| 参数名    | 类型             | 必填 | 描述    |
| :-------- | :--------------- | :--- | :------ |
| `code`    | `integer`        | 否   | Code    |
| `message` | `string`         | 否   | Message |
| `data`    | `DashboardStats` | 否   |         |

---

## Logs

### 获取登录日志

**URL**: `/api/v1/logs/login`

**Method**: `GET`

**Description**:

获取登录日志 (分页)。

查询系统登录日志记录，支持分页。按创建时间倒序排列。

Args:
current_user (User): 当前登录用户。
log_service (LogService): 日志服务依赖。
page (int, optional): 页码. Defaults to 1.
page_size (int, optional): 每页数量. Defaults to 20.

Returns:
ResponseBase[PaginatedResponse[LoginLogResponse]]: 分页后的登录日志列表。

#### Requests Parameters (Query/Path)

| 参数名      | 位置    | 类型      | 必填 | 描述      | Default |
| :---------- | :------ | :-------- | :--- | :-------- | :------ |
| `page`      | `query` | `integer` | 否   | Page      | 1       |
| `page_size` | `query` | `integer` | 否   | Page Size | 20      |

#### Responses

**Status Code**: `200` - Successful Response

Format: `application/json`

| 参数名    | 类型                                  | 必填 | 描述    |
| :-------- | :------------------------------------ | :--- | :------ |
| `code`    | `integer`                             | 否   | Code    |
| `message` | `string`                              | 否   | Message |
| `data`    | `PaginatedResponse_LoginLogResponse_` | 否   |         |

**Status Code**: `422` - Validation Error

Format: `application/json`

| 参数名   | 类型                     | 必填 | 描述   |
| :------- | :----------------------- | :--- | :----- |
| `detail` | `Array[ValidationError]` | 否   | Detail |

---

### 获取操作日志

**URL**: `/api/v1/logs/operation`

**Method**: `GET`

**Description**:

获取操作日志 (分页)。

查询系统操作日志（API 调用记录），支持分页。按创建时间倒序排列。

Args:
current_user (User): 当前登录用户。
log_service (LogService): 日志服务依赖。
page (int, optional): 页码. Defaults to 1.
page_size (int, optional): 每页数量. Defaults to 20.

Returns:
ResponseBase[PaginatedResponse[OperationLogResponse]]: 分页后的操作日志列表。

#### Requests Parameters (Query/Path)

| 参数名      | 位置    | 类型      | 必填 | 描述      | Default |
| :---------- | :------ | :-------- | :--- | :-------- | :------ |
| `page`      | `query` | `integer` | 否   | Page      | 1       |
| `page_size` | `query` | `integer` | 否   | Page Size | 20      |

#### Responses

**Status Code**: `200` - Successful Response

Format: `application/json`

| 参数名    | 类型                                      | 必填 | 描述    |
| :-------- | :---------------------------------------- | :--- | :------ |
| `code`    | `integer`                                 | 否   | Code    |
| `message` | `string`                                  | 否   | Message |
| `data`    | `PaginatedResponse_OperationLogResponse_` | 否   |         |

**Status Code**: `422` - Validation Error

Format: `application/json`

| 参数名   | 类型                     | 必填 | 描述   |
| :------- | :----------------------- | :--- | :----- |
| `detail` | `Array[ValidationError]` | 否   | Detail |

---

## Menus

### 获取菜单列表

**URL**: `/api/v1/menus/`

**Method**: `GET`

**Description**:

获取菜单列表 (分页)。

查询系统菜单记录，支持分页。按排序字段排序。

Args:
current_user (User): 当前登录用户。
menu_service (MenuService): 菜单服务依赖。
page (int, optional): 页码. Defaults to 1.
page_size (int, optional): 每页数量. Defaults to 20.

Returns:
ResponseBase[PaginatedResponse[MenuResponse]]: 分页后的菜单列表。

#### Requests Parameters (Query/Path)

| 参数名      | 位置    | 类型      | 必填 | 描述      | Default |
| :---------- | :------ | :-------- | :--- | :-------- | :------ |
| `page`      | `query` | `integer` | 否   | Page      | 1       |
| `page_size` | `query` | `integer` | 否   | Page Size | 20      |

#### Responses

**Status Code**: `200` - Successful Response

Format: `application/json`

| 参数名    | 类型                              | 必填 | 描述    |
| :-------- | :-------------------------------- | :--- | :------ |
| `code`    | `integer`                         | 否   | Code    |
| `message` | `string`                          | 否   | Message |
| `data`    | `PaginatedResponse_MenuResponse_` | 否   |         |

**Status Code**: `422` - Validation Error

Format: `application/json`

| 参数名   | 类型                     | 必填 | 描述   |
| :------- | :----------------------- | :--- | :----- |
| `detail` | `Array[ValidationError]` | 否   | Detail |

---

### 创建菜单

**URL**: `/api/v1/menus/`

**Method**: `POST`

**Description**:

创建新菜单。

创建新的系统菜单或权限节点。

Args:
menu_in (MenuCreate): 菜单创建数据 (标题, 路径, 类型等)。
current_user (User): 当前登录用户。
menu_service (MenuService): 菜单服务依赖。

Returns:
ResponseBase[MenuResponse]: 创建成功的菜单对象。

#### Request Body (application/json)

| 参数名       | 类型      | 必填 | 描述     |
| :----------- | :-------- | :--- | :------- |
| `parent_id`  | `string`  | 否   | 父菜单ID |
| `path`       | `string`  | 否   | 路由路径 |
| `component`  | `string`  | 否   | 组件路径 |
| `icon`       | `string`  | 否   | 图标     |
| `sort`       | `integer` | 否   | 排序     |
| `is_hidden`  | `boolean` | 否   | 是否隐藏 |
| `permission` | `string`  | 否   | 权限标识 |
| `title`      | `string`  | 是   | 菜单标题 |
| `name`       | `string`  | 是   | 组件名称 |

#### Responses

**Status Code**: `200` - Successful Response

Format: `application/json`

| 参数名    | 类型           | 必填 | 描述    |
| :-------- | :------------- | :--- | :------ |
| `code`    | `integer`      | 否   | Code    |
| `message` | `string`       | 否   | Message |
| `data`    | `MenuResponse` | 否   |         |

**Status Code**: `422` - Validation Error

Format: `application/json`

| 参数名   | 类型                     | 必填 | 描述   |
| :------- | :----------------------- | :--- | :----- |
| `detail` | `Array[ValidationError]` | 否   | Detail |

---

### 批量删除菜单

**URL**: `/api/v1/menus/batch`

**Method**: `DELETE`

**Description**:

批量删除菜单。

支持软删除和硬删除。如果存在子菜单，将级联删除或校验（取决于具体实现策略）。

Args:
request (BatchDeleteRequest): 批量删除请求体 (包含 ID 列表和硬删除标志)。
current_user (User): 当前登录用户。
menu_service (MenuService): 菜单服务依赖。

Returns:
ResponseBase[BatchOperationResult]: 批量操作结果（成功数量等）。

#### Request Body (application/json)

| 参数名        | 类型            | 必填 | 描述                    |
| :------------ | :-------------- | :--- | :---------------------- |
| `ids`         | `Array[string]` | 是   | 要删除的 ID 列表        |
| `hard_delete` | `boolean`       | 否   | 是否硬删除 (默认软删除) |

#### Responses

**Status Code**: `200` - Successful Response

Format: `application/json`

| 参数名    | 类型                   | 必填 | 描述    |
| :-------- | :--------------------- | :--- | :------ |
| `code`    | `integer`              | 否   | Code    |
| `message` | `string`               | 否   | Message |
| `data`    | `BatchOperationResult` | 否   |         |

**Status Code**: `422` - Validation Error

Format: `application/json`

| 参数名   | 类型                     | 必填 | 描述   |
| :------- | :----------------------- | :--- | :----- |
| `detail` | `Array[ValidationError]` | 否   | Detail |

---

### 更新菜单

**URL**: `/api/v1/menus/{id}`

**Method**: `PUT`

**Description**:

更新菜单。

更新指定 ID 的菜单信息。

Args:
id (UUID): 菜单 ID。
menu_in (MenuUpdate): 菜单更新数据。
current_user (User): 当前登录用户。
menu_service (MenuService): 菜单服务依赖。

Returns:
ResponseBase[MenuResponse]: 更新后的菜单对象。

#### Requests Parameters (Query/Path)

| 参数名 | 位置   | 类型     | 必填 | 描述 | Default |
| :----- | :----- | :------- | :--- | :--- | :------ |
| `id`   | `path` | `string` | 是   | Id   |         |

#### Request Body (application/json)

| 参数名       | 类型      | 必填 | 描述       |
| :----------- | :-------- | :--- | :--------- |
| `title`      | `string`  | 否   | Title      |
| `name`       | `string`  | 否   | Name       |
| `parent_id`  | `string`  | 否   | Parent Id  |
| `path`       | `string`  | 否   | Path       |
| `component`  | `string`  | 否   | Component  |
| `icon`       | `string`  | 否   | Icon       |
| `sort`       | `integer` | 否   | Sort       |
| `is_hidden`  | `boolean` | 否   | Is Hidden  |
| `permission` | `string`  | 否   | Permission |

#### Responses

**Status Code**: `200` - Successful Response

Format: `application/json`

| 参数名    | 类型           | 必填 | 描述    |
| :-------- | :------------- | :--- | :------ |
| `code`    | `integer`      | 否   | Code    |
| `message` | `string`       | 否   | Message |
| `data`    | `MenuResponse` | 否   |         |

**Status Code**: `422` - Validation Error

Format: `application/json`

| 参数名   | 类型                     | 必填 | 描述   |
| :------- | :----------------------- | :--- | :----- |
| `detail` | `Array[ValidationError]` | 否   | Detail |

---

### 删除菜单

**URL**: `/api/v1/menus/{id}`

**Method**: `DELETE`

**Description**:

删除菜单。

删除指定 ID 的菜单。

Args:
id (UUID): 菜单 ID。
current_user (User): 当前登录用户。
menu_service (MenuService): 菜单服务依赖。

Returns:
ResponseBase[MenuResponse]: 已删除的菜单对象信息。

#### Requests Parameters (Query/Path)

| 参数名 | 位置   | 类型     | 必填 | 描述 | Default |
| :----- | :----- | :------- | :--- | :--- | :------ |
| `id`   | `path` | `string` | 是   | Id   |         |

#### Responses

**Status Code**: `200` - Successful Response

Format: `application/json`

| 参数名    | 类型           | 必填 | 描述    |
| :-------- | :------------- | :--- | :------ |
| `code`    | `integer`      | 否   | Code    |
| `message` | `string`       | 否   | Message |
| `data`    | `MenuResponse` | 否   |         |

**Status Code**: `422` - Validation Error

Format: `application/json`

| 参数名   | 类型                     | 必填 | 描述   |
| :------- | :----------------------- | :--- | :----- |
| `detail` | `Array[ValidationError]` | 否   | Detail |

---

### 恢复已删除菜单

**URL**: `/api/v1/menus/{id}/restore`

**Method**: `POST`

**Description**:

恢复已删除菜单。

从回收站中恢复指定菜单。
需要超级管理员权限。

#### Requests Parameters (Query/Path)

| 参数名 | 位置   | 类型     | 必填 | 描述 | Default |
| :----- | :----- | :------- | :--- | :--- | :------ |
| `id`   | `path` | `string` | 是   | Id   |         |

#### Responses

**Status Code**: `200` - Successful Response

Format: `application/json`

| 参数名    | 类型           | 必填 | 描述    |
| :-------- | :------------- | :--- | :------ |
| `code`    | `integer`      | 否   | Code    |
| `message` | `string`       | 否   | Message |
| `data`    | `MenuResponse` | 否   |         |

**Status Code**: `422` - Validation Error

Format: `application/json`

| 参数名   | 类型                     | 必填 | 描述   |
| :------- | :----------------------- | :--- | :----- |
| `detail` | `Array[ValidationError]` | 否   | Detail |

---

### 获取菜单回收站列表

**URL**: `/api/v1/menus/recycle-bin`

**Method**: `GET`

**Description**:

获取已删除的菜单列表 (回收站)。
仅限超级管理员。

#### Requests Parameters (Query/Path)

| 参数名      | 位置    | 类型      | 必填 | 描述      | Default |
| :---------- | :------ | :-------- | :--- | :-------- | :------ |
| `page`      | `query` | `integer` | 否   | Page      | 1       |
| `page_size` | `query` | `integer` | 否   | Page Size | 20      |

#### Responses

**Status Code**: `200` - Successful Response

Format: `application/json`

| 参数名    | 类型                              | 必填 | 描述    |
| :-------- | :-------------------------------- | :--- | :------ |
| `code`    | `integer`                         | 否   | Code    |
| `message` | `string`                          | 否   | Message |
| `data`    | `PaginatedResponse_MenuResponse_` | 否   |         |

**Status Code**: `422` - Validation Error

Format: `application/json`

| 参数名   | 类型                     | 必填 | 描述   |
| :------- | :----------------------- | :--- | :----- |
| `detail` | `Array[ValidationError]` | 否   | Detail |

---

## Roles

### 获取角色列表

**URL**: `/api/v1/roles/`

**Method**: `GET`

**Description**:

获取角色列表 (分页)。

查询系统角色记录，支持分页。

Args:
role_service (RoleService): 角色服务依赖。
current_user (User): 当前登录用户。
page (int, optional): 页码. Defaults to 1.
page_size (int, optional): 每页数量. Defaults to 20.

Returns:
ResponseBase[PaginatedResponse[RoleResponse]]: 分页后的角色列表。

#### Requests Parameters (Query/Path)

| 参数名      | 位置    | 类型      | 必填 | 描述      | Default |
| :---------- | :------ | :-------- | :--- | :-------- | :------ |
| `page`      | `query` | `integer` | 否   | Page      | 1       |
| `page_size` | `query` | `integer` | 否   | Page Size | 20      |

#### Responses

**Status Code**: `200` - Successful Response

Format: `application/json`

| 参数名    | 类型                              | 必填 | 描述    |
| :-------- | :-------------------------------- | :--- | :------ |
| `code`    | `integer`                         | 否   | Code    |
| `message` | `string`                          | 否   | Message |
| `data`    | `PaginatedResponse_RoleResponse_` | 否   |         |

**Status Code**: `422` - Validation Error

Format: `application/json`

| 参数名   | 类型                     | 必填 | 描述   |
| :------- | :----------------------- | :--- | :----- |
| `detail` | `Array[ValidationError]` | 否   | Detail |

---

### 创建角色

**URL**: `/api/v1/roles/`

**Method**: `POST`

**Description**:

创建新角色。

创建新的系统角色。

Args:
role_in (RoleCreate): 角色创建数据 (名称, 标识, 描述等)。
current_user (User): 当前登录用户。
role_service (RoleService): 角色服务依赖。

Returns:
ResponseBase[RoleResponse]: 创建成功的角色对象。

#### Request Body (application/json)

| 参数名        | 类型      | 必填 | 描述           |
| :------------ | :-------- | :--- | :------------- |
| `description` | `string`  | 否   | 描述           |
| `sort`        | `integer` | 否   | 排序           |
| `name`        | `string`  | 是   | 角色名称       |
| `code`        | `string`  | 是   | 角色编码       |
| `menu_ids`    | `array`   | 否   | 关联菜单ID列表 |

#### Responses

**Status Code**: `200` - Successful Response

Format: `application/json`

| 参数名    | 类型           | 必填 | 描述    |
| :-------- | :------------- | :--- | :------ |
| `code`    | `integer`      | 否   | Code    |
| `message` | `string`       | 否   | Message |
| `data`    | `RoleResponse` | 否   |         |

**Status Code**: `422` - Validation Error

Format: `application/json`

| 参数名   | 类型                     | 必填 | 描述   |
| :------- | :----------------------- | :--- | :----- |
| `detail` | `Array[ValidationError]` | 否   | Detail |

---

### 批量删除角色

**URL**: `/api/v1/roles/batch`

**Method**: `DELETE`

**Description**:

批量删除角色。

支持软删除和硬删除。

Args:
request (BatchDeleteRequest): 批量删除请求体 (包含 ID 列表和硬删除标志)。
current_user (User): 当前登录用户。
role_service (RoleService): 角色服务依赖。

Returns:
ResponseBase[BatchOperationResult]: 批量操作结果（成功数量等）。

#### Request Body (application/json)

| 参数名        | 类型            | 必填 | 描述                    |
| :------------ | :-------------- | :--- | :---------------------- |
| `ids`         | `Array[string]` | 是   | 要删除的 ID 列表        |
| `hard_delete` | `boolean`       | 否   | 是否硬删除 (默认软删除) |

#### Responses

**Status Code**: `200` - Successful Response

Format: `application/json`

| 参数名    | 类型                   | 必填 | 描述    |
| :-------- | :--------------------- | :--- | :------ |
| `code`    | `integer`              | 否   | Code    |
| `message` | `string`               | 否   | Message |
| `data`    | `BatchOperationResult` | 否   |         |

**Status Code**: `422` - Validation Error

Format: `application/json`

| 参数名   | 类型                     | 必填 | 描述   |
| :------- | :----------------------- | :--- | :----- |
| `detail` | `Array[ValidationError]` | 否   | Detail |

---

### 更新角色

**URL**: `/api/v1/roles/{id}`

**Method**: `PUT`

**Description**:

更新角色。

更新指定 ID 的角色信息。

Args:
id (UUID): 角色 ID。
role_in (RoleUpdate): 角色更新数据。
current_user (User): 当前登录用户。
role_service (RoleService): 角色服务依赖。

Returns:
ResponseBase[RoleResponse]: 更新后的角色对象。

#### Requests Parameters (Query/Path)

| 参数名 | 位置   | 类型     | 必填 | 描述 | Default |
| :----- | :----- | :------- | :--- | :--- | :------ |
| `id`   | `path` | `string` | 是   | Id   |         |

#### Request Body (application/json)

| 参数名        | 类型      | 必填 | 描述           |
| :------------ | :-------- | :--- | :------------- |
| `name`        | `string`  | 否   | 角色名称       |
| `code`        | `string`  | 否   | 角色编码       |
| `description` | `string`  | 否   | 描述           |
| `sort`        | `integer` | 否   | 排序           |
| `menu_ids`    | `array`   | 否   | 关联菜单ID列表 |

#### Responses

**Status Code**: `200` - Successful Response

Format: `application/json`

| 参数名    | 类型           | 必填 | 描述    |
| :-------- | :------------- | :--- | :------ |
| `code`    | `integer`      | 否   | Code    |
| `message` | `string`       | 否   | Message |
| `data`    | `RoleResponse` | 否   |         |

**Status Code**: `422` - Validation Error

Format: `application/json`

| 参数名   | 类型                     | 必填 | 描述   |
| :------- | :----------------------- | :--- | :----- |
| `detail` | `Array[ValidationError]` | 否   | Detail |

---

### 删除角色

**URL**: `/api/v1/roles/{id}`

**Method**: `DELETE`

**Description**:

删除角色 (软删除)。

Args:
id (UUID): 角色 ID。
active_superuser (User): 当前登录超级用户。
role_service (RoleService): 角色服务依赖。

Returns:
ResponseBase[RoleResponse]: 删除后的角色对象。

#### Requests Parameters (Query/Path)

| 参数名 | 位置   | 类型     | 必填 | 描述 | Default |
| :----- | :----- | :------- | :--- | :--- | :------ |
| `id`   | `path` | `string` | 是   | Id   |         |

#### Responses

**Status Code**: `200` - Successful Response

Format: `application/json`

| 参数名    | 类型           | 必填 | 描述    |
| :-------- | :------------- | :--- | :------ |
| `code`    | `integer`      | 否   | Code    |
| `message` | `string`       | 否   | Message |
| `data`    | `RoleResponse` | 否   |         |

**Status Code**: `422` - Validation Error

Format: `application/json`

| 参数名   | 类型                     | 必填 | 描述   |
| :------- | :----------------------- | :--- | :----- |
| `detail` | `Array[ValidationError]` | 否   | Detail |

---

### 恢复已删除角色

**URL**: `/api/v1/roles/{id}/restore`

**Method**: `POST`

**Description**:

恢复已删除角色。

从回收站中恢复指定角色。
需要超级管理员权限。

#### Requests Parameters (Query/Path)

| 参数名 | 位置   | 类型     | 必填 | 描述 | Default |
| :----- | :----- | :------- | :--- | :--- | :------ |
| `id`   | `path` | `string` | 是   | Id   |         |

#### Responses

**Status Code**: `200` - Successful Response

Format: `application/json`

| 参数名    | 类型           | 必填 | 描述    |
| :-------- | :------------- | :--- | :------ |
| `code`    | `integer`      | 否   | Code    |
| `message` | `string`       | 否   | Message |
| `data`    | `RoleResponse` | 否   |         |

**Status Code**: `422` - Validation Error

Format: `application/json`

| 参数名   | 类型                     | 必填 | 描述   |
| :------- | :----------------------- | :--- | :----- |
| `detail` | `Array[ValidationError]` | 否   | Detail |

---

### 获取角色回收站列表

**URL**: `/api/v1/roles/recycle-bin`

**Method**: `GET`

**Description**:

获取已删除的角色列表 (回收站)。
仅限超级管理员。

#### Requests Parameters (Query/Path)

| 参数名      | 位置    | 类型      | 必填 | 描述      | Default |
| :---------- | :------ | :-------- | :--- | :-------- | :------ |
| `page`      | `query` | `integer` | 否   | Page      | 1       |
| `page_size` | `query` | `integer` | 否   | Page Size | 20      |

#### Responses

**Status Code**: `200` - Successful Response

Format: `application/json`

| 参数名    | 类型                              | 必填 | 描述    |
| :-------- | :-------------------------------- | :--- | :------ |
| `code`    | `integer`                         | 否   | Code    |
| `message` | `string`                          | 否   | Message |
| `data`    | `PaginatedResponse_RoleResponse_` | 否   |         |

**Status Code**: `422` - Validation Error

Format: `application/json`

| 参数名   | 类型                     | 必填 | 描述   |
| :------- | :----------------------- | :--- | :----- |
| `detail` | `Array[ValidationError]` | 否   | Detail |

---

## Uncategorized

### Health Check

**URL**: `/api/v1/health`

**Method**: `GET`

**Description**:

健康检查接口 (Database & Cache Check).

#### Responses

**Status Code**: `200` - Successful Response

Format: `application/json`

No properties (Empty Object)

---

## Users

### 获取用户列表

**URL**: `/api/v1/users/`

**Method**: `GET`

**Description**:

查询用户列表 (分页)。

获取所有系统用户，支持分页。需要超级管理员权限。

Args:
user_service (UserService): 用户服务依赖。
current_user (User): 当前登录用户。
active_superuser (User): 超级管理员权限验证。
page (int, optional): 页码. Defaults to 1.
page_size (int, optional): 每页数量. Defaults to 20.

Returns:
ResponseBase[PaginatedResponse[UserResponse]]: 分页后的用户列表。

#### Requests Parameters (Query/Path)

| 参数名      | 位置    | 类型      | 必填 | 描述      | Default |
| :---------- | :------ | :-------- | :--- | :-------- | :------ |
| `page`      | `query` | `integer` | 否   | Page      | 1       |
| `page_size` | `query` | `integer` | 否   | Page Size | 20      |

#### Responses

**Status Code**: `200` - Successful Response

Format: `application/json`

| 参数名    | 类型                              | 必填 | 描述    |
| :-------- | :-------------------------------- | :--- | :------ |
| `code`    | `integer`                         | 否   | Code    |
| `message` | `string`                          | 否   | Message |
| `data`    | `PaginatedResponse_UserResponse_` | 否   |         |

**Status Code**: `422` - Validation Error

Format: `application/json`

| 参数名   | 类型                     | 必填 | 描述   |
| :------- | :----------------------- | :--- | :----- |
| `detail` | `Array[ValidationError]` | 否   | Detail |

---

### 创建用户

**URL**: `/api/v1/users/`

**Method**: `POST`

**Description**:

创建新用户。

注册新的系统用户。需要超级管理员权限。

Args:
user_in (UserCreate): 用户创建数据 (用户名, 密码, 邮箱等)。
current_user (User): 当前登录用户。
active_superuser (User): 超级管理员权限验证。
user_service (UserService): 用户服务依赖。

Returns:
ResponseBase[UserResponse]: 创建成功的用户对象。

#### Request Body (application/json)

| 参数名         | 类型      | 必填 | 描述             |
| :------------- | :-------- | :--- | :--------------- |
| `username`     | `string`  | 是   | 用户名           |
| `email`        | `string`  | 否   | 邮箱             |
| `phone`        | `string`  | 是   | 手机号           |
| `nickname`     | `string`  | 否   | 昵称             |
| `gender`       | `string`  | 否   | 性别             |
| `is_active`    | `boolean` | 否   | 是否激活         |
| `is_superuser` | `boolean` | 否   | 是否为超级管理员 |
| `password`     | `string`  | 是   | 密码             |

#### Responses

**Status Code**: `200` - Successful Response

Format: `application/json`

| 参数名    | 类型           | 必填 | 描述    |
| :-------- | :------------- | :--- | :------ |
| `code`    | `integer`      | 否   | Code    |
| `message` | `string`       | 否   | Message |
| `data`    | `UserResponse` | 否   |         |

**Status Code**: `422` - Validation Error

Format: `application/json`

| 参数名   | 类型                     | 必填 | 描述   |
| :------- | :----------------------- | :--- | :----- |
| `detail` | `Array[ValidationError]` | 否   | Detail |

---

### 批量删除用户

**URL**: `/api/v1/users/batch`

**Method**: `DELETE`

**Description**:

批量删除用户。

支持软删除和硬删除。需要超级管理员权限。

Args:
request (BatchDeleteRequest): 批量删除请求体 (包含 ID 列表和硬删除标志)。
current_user (User): 当前登录用户。
active_superuser (User): 超级管理员权限验证。
user_service (UserService): 用户服务依赖。

Returns:
ResponseBase[BatchOperationResult]: 批量操作结果（成功数量等）。

#### Request Body (application/json)

| 参数名        | 类型            | 必填 | 描述                    |
| :------------ | :-------------- | :--- | :---------------------- |
| `ids`         | `Array[string]` | 是   | 要删除的 ID 列表        |
| `hard_delete` | `boolean`       | 否   | 是否硬删除 (默认软删除) |

#### Responses

**Status Code**: `200` - Successful Response

Format: `application/json`

| 参数名    | 类型                   | 必填 | 描述    |
| :-------- | :--------------------- | :--- | :------ |
| `code`    | `integer`              | 否   | Code    |
| `message` | `string`               | 否   | Message |
| `data`    | `BatchOperationResult` | 否   |         |

**Status Code**: `422` - Validation Error

Format: `application/json`

| 参数名   | 类型                     | 必填 | 描述   |
| :------- | :----------------------- | :--- | :----- |
| `detail` | `Array[ValidationError]` | 否   | Detail |

---

### 获取当前用户

**URL**: `/api/v1/users/me`

**Method**: `GET`

**Description**:

获取当前用户信息。

返回当前登录用户的详细信息。

Args:
current_user (User): 当前登录用户 (由依赖自动注入)。

Returns:
ResponseBase[UserResponse]: 当前用户的详细信息。

#### Responses

**Status Code**: `200` - Successful Response

Format: `application/json`

| 参数名    | 类型           | 必填 | 描述    |
| :-------- | :------------- | :--- | :------ |
| `code`    | `integer`      | 否   | Code    |
| `message` | `string`       | 否   | Message |
| `data`    | `UserResponse` | 否   |         |

---

### 更新当前用户

**URL**: `/api/v1/users/me`

**Method**: `PUT`

**Description**:

更新当前用户信息。

用户自行修改个人资料（如昵称、邮箱、手机号等）。

Args:
user_service (UserService): 用户服务依赖。
user_in (UserUpdate): 用户更新数据。
current_user (User): 当前登录用户。

Returns:
ResponseBase[UserResponse]: 更新后的用户信息。

#### Request Body (application/json)

| 参数名         | 类型      | 必填 | 描述         |
| :------------- | :-------- | :--- | :----------- |
| `username`     | `string`  | 否   | Username     |
| `email`        | `string`  | 否   | Email        |
| `phone`        | `string`  | 否   | Phone        |
| `nickname`     | `string`  | 否   | Nickname     |
| `gender`       | `string`  | 否   | Gender       |
| `is_active`    | `boolean` | 否   | Is Active    |
| `is_superuser` | `boolean` | 否   | Is Superuser |

#### Responses

**Status Code**: `200` - Successful Response

Format: `application/json`

| 参数名    | 类型           | 必填 | 描述    |
| :-------- | :------------- | :--- | :------ |
| `code`    | `integer`      | 否   | Code    |
| `message` | `string`       | 否   | Message |
| `data`    | `UserResponse` | 否   |         |

**Status Code**: `422` - Validation Error

Format: `application/json`

| 参数名   | 类型                     | 必填 | 描述   |
| :------- | :----------------------- | :--- | :----- |
| `detail` | `Array[ValidationError]` | 否   | Detail |

---

### 修改密码 (当前用户)

**URL**: `/api/v1/users/me/password`

**Method**: `PUT`

**Description**:

修改当前用户密码。

需要验证旧密码是否正确。

Args:
user_service (UserService): 用户服务依赖。
password_data (ChangePasswordRequest): 密码修改请求 (包含旧密码和新密码)。
current_user (User): 当前登录用户。

Returns:
ResponseBase[UserResponse]: 用户信息 (密码修改成功后)。

#### Request Body (application/json)

| 参数名         | 类型     | 必填 | 描述   |
| :------------- | :------- | :--- | :----- |
| `old_password` | `string` | 是   | 旧密码 |
| `new_password` | `string` | 是   | 新密码 |

#### Responses

**Status Code**: `200` - Successful Response

Format: `application/json`

| 参数名    | 类型           | 必填 | 描述    |
| :-------- | :------------- | :--- | :------ |
| `code`    | `integer`      | 否   | Code    |
| `message` | `string`       | 否   | Message |
| `data`    | `UserResponse` | 否   |         |

**Status Code**: `422` - Validation Error

Format: `application/json`

| 参数名   | 类型                     | 必填 | 描述   |
| :------- | :----------------------- | :--- | :----- |
| `detail` | `Array[ValidationError]` | 否   | Detail |

---

### 重置密码 (管理员)

**URL**: `/api/v1/users/{user_id}/password`

**Method**: `PUT`

**Description**:

管理员重置用户密码。

强制修改指定用户的密码，不需要知道旧密码。需要超级管理员权限。

Args:
user_id (UUID): 目标用户 ID。
password_data (ResetPasswordRequest): 密码重置请求 (包含新密码)。
current_user (User): 当前登录用户。
active_superuser (User): 超级管理员权限验证。
user_service (UserService): 用户服务依赖。

Returns:
ResponseBase[UserResponse]: 用户信息 (密码重置成功后)。

#### Requests Parameters (Query/Path)

| 参数名    | 位置   | 类型     | 必填 | 描述    | Default |
| :-------- | :----- | :------- | :--- | :------ | :------ |
| `user_id` | `path` | `string` | 是   | User Id |         |

#### Request Body (application/json)

| 参数名         | 类型     | 必填 | 描述   |
| :------------- | :------- | :--- | :----- |
| `new_password` | `string` | 是   | 新密码 |

#### Responses

**Status Code**: `200` - Successful Response

Format: `application/json`

| 参数名    | 类型           | 必填 | 描述    |
| :-------- | :------------- | :--- | :------ |
| `code`    | `integer`      | 否   | Code    |
| `message` | `string`       | 否   | Message |
| `data`    | `UserResponse` | 否   |         |

**Status Code**: `422` - Validation Error

Format: `application/json`

| 参数名   | 类型                     | 必填 | 描述   |
| :------- | :----------------------- | :--- | :----- |
| `detail` | `Array[ValidationError]` | 否   | Detail |

---

### 恢复已删除用户

**URL**: `/api/v1/users/{user_id}/restore`

**Method**: `POST`

**Description**:

恢复已删除用户。

从回收站中恢复指定用户。
需要超级管理员权限。

#### Requests Parameters (Query/Path)

| 参数名    | 位置   | 类型     | 必填 | 描述    | Default |
| :-------- | :----- | :------- | :--- | :------ | :------ |
| `user_id` | `path` | `string` | 是   | User Id |         |

#### Responses

**Status Code**: `200` - Successful Response

Format: `application/json`

| 参数名    | 类型           | 必填 | 描述    |
| :-------- | :------------- | :--- | :------ |
| `code`    | `integer`      | 否   | Code    |
| `message` | `string`       | 否   | Message |
| `data`    | `UserResponse` | 否   |         |

**Status Code**: `422` - Validation Error

Format: `application/json`

| 参数名   | 类型                     | 必填 | 描述   |
| :------- | :----------------------- | :--- | :----- |
| `detail` | `Array[ValidationError]` | 否   | Detail |

---

### 获取用户回收站列表

**URL**: `/api/v1/users/recycle-bin`

**Method**: `GET`

**Description**:

获取已删除的用户列表 (回收站)。
仅限超级管理员。

#### Requests Parameters (Query/Path)

| 参数名      | 位置    | 类型      | 必填 | 描述      | Default |
| :---------- | :------ | :-------- | :--- | :-------- | :------ |
| `page`      | `query` | `integer` | 否   | Page      | 1       |
| `page_size` | `query` | `integer` | 否   | Page Size | 20      |

#### Responses

**Status Code**: `200` - Successful Response

Format: `application/json`

| 参数名    | 类型                              | 必填 | 描述    |
| :-------- | :-------------------------------- | :--- | :------ |
| `code`    | `integer`                         | 否   | Code    |
| `message` | `string`                          | 否   | Message |
| `data`    | `PaginatedResponse_UserResponse_` | 否   |         |

**Status Code**: `422` - Validation Error

Format: `application/json`

| 参数名   | 类型                     | 必填 | 描述   |
| :------- | :----------------------- | :--- | :----- |
| `detail` | `Array[ValidationError]` | 否   | Detail |

---

### 获取特定用户信息

**URL**: `/api/v1/users/{user_id}`

**Method**: `GET`

**Description**:

获取特定用户的详细信息 (管理员)。

Args:
user_id (UUID): 目标用户 ID。
active_superuser (User): 超级管理员权限验证。
user_service (UserService): 用户服务依赖。

Returns:
ResponseBase[UserResponse]: 用户详细信息。

#### Requests Parameters (Query/Path)

| 参数名    | 位置   | 类型     | 必填 | 描述    | Default |
| :-------- | :----- | :------- | :--- | :------ | :------ |
| `user_id` | `path` | `string` | 是   | User Id |         |

#### Responses

**Status Code**: `200` - Successful Response

Format: `application/json`

| 参数名    | 类型           | 必填 | 描述    |
| :-------- | :------------- | :--- | :------ |
| `code`    | `integer`      | 否   | Code    |
| `message` | `string`       | 否   | Message |
| `data`    | `UserResponse` | 否   |         |

**Status Code**: `422` - Validation Error

Format: `application/json`

| 参数名   | 类型                     | 必填 | 描述   |
| :------- | :----------------------- | :--- | :----- |
| `detail` | `Array[ValidationError]` | 否   | Detail |

---

### 更新用户信息 (管理员)

**URL**: `/api/v1/users/{user_id}`

**Method**: `PUT`

**Description**:

管理员更新用户信息。

允许超级管理员修改任意用户的资料 (昵称、手机号、邮箱、状态等)。
不包含密码修改 (请使用重置密码接口)。

Args:
user_id (UUID): 目标用户 ID。
user_in (UserUpdate): 更新的用户数据。
active_superuser (User): 超级管理员权限验证。
user_service (UserService): 用户服务依赖。

Returns:
ResponseBase[UserResponse]: 更新后的用户信息。

#### Requests Parameters (Query/Path)

| 参数名    | 位置   | 类型     | 必填 | 描述    | Default |
| :-------- | :----- | :------- | :--- | :------ | :------ |
| `user_id` | `path` | `string` | 是   | User Id |         |

#### Request Body (application/json)

| 参数名         | 类型      | 必填 | 描述         |
| :------------- | :-------- | :--- | :----------- |
| `username`     | `string`  | 否   | Username     |
| `email`        | `string`  | 否   | Email        |
| `phone`        | `string`  | 否   | Phone        |
| `nickname`     | `string`  | 否   | Nickname     |
| `gender`       | `string`  | 否   | Gender       |
| `is_active`    | `boolean` | 否   | Is Active    |
| `is_superuser` | `boolean` | 否   | Is Superuser |

#### Responses

**Status Code**: `200` - Successful Response

Format: `application/json`

| 参数名    | 类型           | 必填 | 描述    |
| :-------- | :------------- | :--- | :------ |
| `code`    | `integer`      | 否   | Code    |
| `message` | `string`       | 否   | Message |
| `data`    | `UserResponse` | 否   |         |

**Status Code**: `422` - Validation Error

Format: `application/json`

| 参数名   | 类型                     | 必填 | 描述   |
| :------- | :----------------------- | :--- | :----- |
| `detail` | `Array[ValidationError]` | 否   | Detail |

---
