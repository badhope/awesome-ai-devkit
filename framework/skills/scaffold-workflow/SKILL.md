---
name: scaffold-workflow
description: 全栈开发工作流编排。当 Agent 需要按 scaffold 步骤推进开发任务时触发，遵循 Awesome AI DevKit 的 Scaffold Protocol v2.1。
layer: orchestration
tags: [scaffold, workflow, fullstack, orchestration]
---

# Scaffold Workflow Orchestration

## 触发条件

当需要规划多步骤全栈开发任务、协调多个 SubAgent 并行/串行工作时触发。

## 核心模式

### 1. Scaffold v2.1 协议

```
步骤类型:
────────────────────────────────────────────────
serial     — 前一步完成才能开始下一步
parallel   — 多个步骤可同时执行（dispatch 给不同 SubAgent）
quality_gate — 步骤间的验证点，agent 自定验证方式

执行规则:
  - 按顺序遍历 steps 列表
  - parallel: true 的步骤可 dispatch 给多个 SubAgent 同时执行
  - quality_gate 描述文本由 agent 自定验证方式（不执行 shell）
  - 上一步的输出成为下一步的上下文
────────────────────────────────────────────────
```

### 2. 标准全栈工作流（11 个专业角色）

```
Phase 1  需求分析 → @product-manager + @architect-system-designer
          PM: docs/requirements/<feature>.md + 用户故事 + 验收标准
          架构师: 可行性初评 + 技术约束识别

Phase 2  技术设计 → @architect-system-designer + @database-engineer
          架构师: API 契约 + ADR + 系统架构图
          DBA: Schema 设计 + 索引策略 + 迁移方案

Phase 3  实现（parallel）:
          ├→ @backend-api-developer  (API + 业务逻辑)
          ├→ @frontend-ui-developer  (UI + 交互)
          └→ @design-system-architect (组件规范 + Token + 无障碍)

Phase 4  质量门禁（parallel）:
          ├→ @test-qa-engineer        (测试 + 覆盖率 + 变异测试)
          └→ @code-reviewer           (独立代码审查)

Phase 5  安全审查 → @security-review-engineer (只读)
          质量门禁: 无 CRITICAL/HIGH 漏洞

Phase 6  部署上线:
          ├→ @devops-deploy-engineer  (CI/CD + 构建 + 部署)
          └→ @site-reliability-engineer (监控 + SLO + 告警)
```

### 3. SubAgent 矩阵

```
                        读代码  写代码  写测试  只读审查  读/写配置
──────────────────────────────────────────────────────────────────
product-manager          ✓       ✓
architect-system-designer ✓       ✓
database-engineer        ✓       ✓                       ✓
backend-api-developer    ✓       ✓               ✓       ✓
frontend-ui-developer    ✓       ✓               ✓       ✓
design-system-architect  ✓       ✓               ✓       ✓
test-qa-engineer         ✓       ✓       ✓               ✓
code-reviewer            ✓                       ✓
security-review-engineer ✓                       ✓
devops-deploy-engineer   ✓                       ✓       ✓
site-reliability-engineer ✓                       ✓       ✓
```

### 4. 协作链路

```
product-manager ─────────┐
                         ▼
architect-system-designer ──→ database-engineer
        │                         │
        ├─────────────────────────┤
        ▼                         ▼
backend-api-developer ◄──── design-system-architect
        │                         ▲
        └────→ frontend-ui-developer
                    │
                    ▼
            test-qa-engineer ────→ code-reviewer
                    │                    │
                    ▼                    ▼
            security-review-engineer      │
                    │                    │
                    ▼                    ▼
            devops-deploy-engineer ←─────┘
                    │
                    ▼
            site-reliability-engineer
```

### 5. SubAgent 调度规则

```
创建 SubAgent 判断:
────────────────────────────────────────────────
✓ 多个独立实现任务（后端 + 前端 + token） → 并行 dispatch
✓ 实现与测试 → 串行（实现完再测）
✓ 大规模代码修改 → 独立 SubAgent 隔离开销
✓ 质量关卡（review/security） → 独立 SubAgent 角色保证客观
✗ 简单查询/小改动 → Agent 自己做，不开 SubAgent
✗ 强依赖连续上下文的任务 → 串行执行
```

### 6. 质量门禁

| Gate | 负责角色 | 验证方式 |
|------|---------|---------|
| 验收标准通过 | product-manager | Gherkin 全部 PASS |
| 技术方案审核 | architect-system-designer | ADR 完整 |
| 测试通过 | test-qa-engineer | 覆盖率 ≥ 80%，变异分数 ≥ 70% |
| 代码审查通过 | code-reviewer | REQUEST_CHANGES → 修复重审 |
| 安全审查通过 | security-review-engineer | 无 CRITICAL/HIGH |
| 构建成功 | devops-deploy-engineer | image 可运行 |
| 监控就绪 | site-reliability-engineer | 告警 + SLO 已配置 |

## Checklist

- [ ] Scaffold 文件遵循 v2.1 flat 格式
- [ ] 并行步骤 dispatch 给独立 SubAgent
- [ ] 每个 quality_gate 有明确验证逻辑
- [ ] SubAgent 上下文传递依赖文件和 git
- [ ] 失败步骤有 retry 机制（最多 2 次）
- [ ] 11 个角色各司其职，不越权

## 推荐 SubAgent（按出现顺序）

- instruction-grooming（用户指令清洗与补全 — 入口角色）
- product-manager（需求 + PRD + 验收标准）
- architect-system-designer（架构 + API 契约 + ADR）
- database-engineer（Schema + 迁移 + 索引）
- backend-api-developer（API + 业务逻辑 + 迁移执行）
- frontend-ui-developer（UI + 交互 + 状态管理）
- design-system-architect（Token + 组件 + 无障碍）
- test-qa-engineer（测试 + 覆盖率 + 变异测试 + 回归）
- code-reviewer（独立代码审查 + 跨文件影响分析）
- security-review-engineer（安全审计 + AI Prompt 注入防护）
- devops-deploy-engineer（部署 + CI/CD + SBOM）
- site-reliability-engineer（监控 + SLO + 混沌工程 + 告警）
