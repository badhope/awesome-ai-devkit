---
name: test-strategy
description: 测试策略设计。基于测试金字塔规划单元/集成/E2E 测试，制定覆盖重点、mock 边界与 CI 集成，保证质量与可维护性。
layer: quality
tags: [testing, test-strategy, unit, integration, e2e, coverage]
---

# Test Strategy — 测试策略设计

## 触发条件
- 规划新功能测试、补测试覆盖、编写测试计划时使用。

## 测试金字塔（参考）
```
        ▲  E2E (少量)   — 关键用户流
       ▲  集成测试        — 模块间/DB/API 联调
      ▲     单元测试 (最多) — 核心业务逻辑
```

## 策略要点

### 1. 分层
- **单元测试**：单个函数/类，快、隔离（mock 外部）
- **集成测试**：组件协作、数据库、第三方 API（用真实或 test double）
- **E2E**：关键用户旅程（登录、下单等），少量但关键

### 2. 覆盖重点（风险驱动）
- 核心业务逻辑、金额/状态/权限相关，优先覆盖
- 边界、异常、并发分支不能漏
- 覆盖率 ≥80% 核心模块（工具/gate 可达）

### 3. Mock 边界
- mock 外部 I/O（网络、DB、第三方），不要 mock 被测内部
- 用清晰的 fixture/factory（见 devkit-utilities test/factory）

### 4. 验收标准（BDD 风格）
```
Given 前置条件
When  执行动作
Then  期望结果
```

## 输出
```
测试计划:
- 单元: <list>
- 集成: <list>
- E2E: <list>
- 覆盖目标: ...
- mock 边界: ...
```

## Checklist
- [ ] 三层覆盖（单元/集成/E2E）有侧重
- [ ] 核心业务路径全部覆盖
- [ ] 边界/异常分支已覆盖
- [ ] mock 只在边界