---
name: team-composer
description: 根据 auto-detect 识别出的技术栈与项目类型，自动挑选并编排合适的开发团队角色组合（复用 framework/agents 11 个通用角色）。当确定了项目类型但不确定该用哪些角色、或需要按项目规模裁剪团队时使用。
layer: orchestration
tags: [team, compose, role, adaptive, orchestration]
---

# Team Composer — 自动组建开发团队

## 触发条件

在 `auto-detect` 之后执行。拿到项目类型与技术栈后，自动选出合适的角色组合，不手动指定。

## 核心能力

### 按项目类型推荐角色

| 项目类型 | 推荐角色组合 | 说明 |
|---------|------------|------|
| **fullstack** | architect-system-designer + frontend-ui-developer + backend-api-developer + test-qa-engineer + code-reviewer + security-review-engineer | 全栈：架构定调 + 前后端 + QA + 审查 + 安全 |
| **frontend** | frontend-ui-developer + design-system-architect + test-qa-engineer | 前端专注 |
| **backend** | backend-api-developer + database-engineer + test-qa-engineer + security-review-engineer | 后端 + 数据 + 安全 |
| **cli** | backend-api-developer + code-reviewer | 轻量：实现 + 审查 |
| **library** | backend-api-developer + code-reviewer | 库开发 |
| **mobile** | frontend-ui-developer + test-qa-engineer | 移动端 |
| **ml** | backend-api-developer + test-qa-engineer + security-review-engineer | AI 应用 |

### 按规模裁剪

| 规模 | 处理 |
|------|------|
| 单点小改（<3 文件） | 只保留 1 个实现者 + 1 个审查者 |
| 标准功能 | 上表默认组合 |
| 大型/全新项目 | 上表 + devops-deploy-engineer + site-reliability-engineer |

### 角色来源

所有角色均来自 **`framework/agents/`** 通用层，本场景**不重复定义**，只做编排。

## 使用方式

```bash
# 1. 先识别（或用 stack-detector 输出）
python3 scenarios/programming/coding/lib/stack-detector.py --project . --json
# → 得到 role_set 字段

# 2. 按 role_set 引用角色
# 每个角色的定义在 framework/agents/<name>.md
```

## 团队协作链

组建团队后，定义角色间输入/输出依赖（参照 framework agent 的"上游/下游"约定）：

- 架构师产出方案 → 后端/前端实现 → QA 测试 → reviewer 审查 → 安全复核
- 并行步骤可用 scaffold 的 `parallel: true` 标记（后端与前端同时开工）
- 用 `context/architecture.md` 共享 ADR 决策，`context/project.yaml` 共享技术栈

## 输出格式

```
👥 组建团队 (frontend):
- frontend-ui-developer   — UI 实现
- design-system-architect — 设计系统与组件
- test-qa-engineer        — 测试覆盖
协作链: design → UI → test
```

## 原则

- **复用 framework 角色**，不新造
- **按需裁剪**：小任务用最少角色，大任务加角色
- **全栈自动**：fullstack 类型自动拉起前后端+架构+DevOps 完整协作链

## Checklist
- [ ] 已确定项目类型（来自 auto-detect）
- [ ] 已选择合适角色组合
- [ ] 已定义角色间输入/输出协作链
- [ ] 已按任务规模裁剪

## 推荐 SubAgent
- scaffold-generator（据团队与类型生成脚手架）