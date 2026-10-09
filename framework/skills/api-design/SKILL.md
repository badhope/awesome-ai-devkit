---
name: api-design
description: API 设计。RESTful / OpenAPI 规范的接口设计，涵盖资源建模、状态码、错误格式、分页、版本化与文档，保证一致与可演进。
layer: architecture
tags: [api, rest, graphql, openapi, design, contract]
---

# API Design — 接口设计

## 触发条件
- 新增/修改接口时使用，保证一致性与可维护性。

## RESTful 约定

### 资源与路由
- 资源用复数名词：`GET /api/v1/users`、`POST /api/v1/orders`
- 子资源：`GET /api/v1/users/{id}/orders`
- 动作走 POST（RPC 用 `/actions` 或 POST 端点），避免动词路由

### 状态码
- 200/201/204：成功
- 400：参数错误 / 422：语义校验失败
- 401/403：未认证/无权限
- 404：不存在 / 409：冲突
- 429：限流 / 5xx：服务端

### 错误格式（统一）
```
{ "error": { "code": "E4001", "message": "..." , "details": {...}} }
```
> 复用 `framework/lib/scripts/api/error-format.py`。

### 分页
- Offset 分页（管理后台）：`?page=1&per_page=20`
- Cursor 分页（无限滚动）：`?cursor=...&limit=20`

### 版本化
- URL 前缀 `v1`，或 Header；变更不破坏旧版

### 文档
- 提供 OpenAPI/Swagger 描述全部端点（方法、参数、响应、错误码）

## 一致性清单
- [ ] 资源复数 + 正确状态码
- [ ] 统一错误格式
- [ ] 输入在边界校验
- [ ] 分页 + 版本化
- [ ] OpenAPI 文档同步

## 输出
接口设计 = 端点表（method, path, req, res, err）+ OpenAPI 片段