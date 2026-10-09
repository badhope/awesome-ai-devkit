---
name: integration-patterns
description: 全栈集成模式。前后端协作、API 契约传递、错误处理统一规范。当需要协调前后端对接或处理跨层通信问题时触发。
layer: orchestration
tags: [fullstack, integration, api, error-handling]
---

# 全栈集成模式

## 触发条件

当需要定义前后端协作接口、统一错误处理、或处理跨层数据流转时触发。

## 核心模式

### 1. API 契约先行

```
流程:
────────────────────────────────────────────────
1. 后端先定义 OpenAPI / TypeScript interface
2. 前端基于契约生成 mock 或 api client
3. 联调时用真实后端替换 mock
4. 契约变更必须同步更新 docs/design

规则:
  - 后端不擅自改契约（先通知架构师）
  - 前端不 hardcode 响应结构（用类型生成）
  - 共享 interface 放在 packages/shared_types/ 或 types/ 目录
────────────────────────────────────────────────
```

### 2. 统一错误响应格式

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "字段 email 格式不正确",
    "details": [{"field": "email", "issue": "invalid_format"}],
    "trace_id": "abc-123-def"
  }
}
```

```typescript
// 前端统一错误处理
class ApiError extends Error {
  code: string;
  details: Array<{field: string; issue: string}>;
  traceId: string;
}

async function apiCall<T>(...): Promise<T> {
  const res = await fetch(url, opts);
  if (!res.ok) {
    const body = await res.json();
    throw new ApiError(body.error);
  }
  return res.json();
}
```

### 3. 并行开发模式

```
契约确认后:
──────────────────────────────────────────────────
后端 (SubAgent)                     前端 (SubAgent)
├── 领域模型/Schema 定义             ├── 基于契约生成 TypeScript types
├── API 路由 + 参数校验              ├── 页面/组件结构
├── 业务逻辑实现                     ├── 状态管理/数据访问层
├── 数据库迁移                       ├── 表单/交互
└── 单元测试                         └── Storybook/组件测试

合入条件:
  ✓ 后端契约测试通过
  ✓ 前端 build/typecheck 通过
  ✓ 集成测试覆盖核心流程
──────────────────────────────────────────────────
```

### 4. 数据流转规则

```
后端:
──────────────────────────────────────────────────
输入校验: 白名单 > 黑名单，zod/schema 校验
金额处理: 整数（分）存储和传输，前端展示时转换
时间: ISO 8601 + UTC，不传本地时间
空值: 用 null，不用 undefined 或空字符串

前端:
──────────────────────────────────────────────────
表单校验: 即时反馈，submit 前完整校验
金额展示: 分 → 元，千分位格式化
时间展示: 相对时间（刚刚/N分钟前）+ 绝对时间 tooltip
加载状态: skeleton/spinner，不白屏
```

## Checklist

- [ ] API 契约在 design 阶段确定，不用运行时猜测
- [ ] 错误码是有意义的字符串，不是数字
- [ ] 空值和边界值前后端一致处理
- [ ] 并行开发时契约文件独立版本管理
- [ ] 集成测试覆盖核心 Happy Path + 关键 Sad Path

## 推荐 SubAgent

- backend-api-developer（契约定义者）
- frontend-ui-developer（契约消费者）
- test-qa-engineer（集成验证者）
