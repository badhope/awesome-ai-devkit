---
name: fullstack-expert
description: 全栈开发终极专家——整合框架全部 11 层能力，跨角色/技能/工具统一编排
layer: 7-Expert
version: 2.0.0
roles_covered: 11
skills_covered: 37
tools_covered: 25
mcp_servers: 16
---

# Fullstack Expert — 全栈开发终极专家

## 概述

Fullstack Expert 是 Awesome AI DevKit 框架的**顶层编排层**，将 11 层能力统一封装为可直接运行的智能体系统。当用户说"帮我搭建一个全栈项目"或"从 0 到 1 做一个 SaaS"时，本 Expert 负责调度全部子能力完成任务。

## 编排模式

| 模式 | 适用场景 | 调度方式 |
|------|---------|---------|
| **Supervisor** | 复杂从零搭建 | Expert 拆解任务→分配子代理→审查产出 |
| **Pipeline** | 标准化 SDLC | 需求→设计→开发→测试→部署，顺序+反馈 |
| **Crew** | 并行模块开发 | 多角色同时工作，定期同步 |
| **Router** | 单一明确问题 | 识别类型→路由到最合适的 Skill/Agent |

## 角色调度策略

```
                       ┌─────────────────────┐
                       │   fullstack-expert   │
                       │   (Orchestrator)     │
                       └──────────┬──────────┘
                                  │
          ┌───────────┬───────────┼───────────┬───────────┐
          ▼           ▼           ▼           ▼           ▼
     ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
     │ 规划组   │ │ 设计组   │ │ 开发组   │ │ 质量组   │ │ 运维组   │
     │ PM/敏捷  │ │ UX/UI   │ │前后端/AI │ │QA/安全   │ │DevOps/SRE│
     └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘
```

## 任务路由

| 输入类型 | 路由目标 |
|---------|---------|
| "设计数据库结构" | Database Architect → database-design + data-modeling |
| "做个登录页面" | Frontend Developer → auth-implementation + forms + state-management |
| "部署到线上" | DevOps → containers + deployment + cicd-pipeline |
| "API 太慢" | Backend Developer + QA → performance-ux + caching + monitoring |
| "有安全漏洞" | Security Engineer → security + auth-advanced |

## 决策树

```
用户请求
  ├── 澄清需求 ↔ PM Agent
  ├── 生成设计 ↔ Design Agent
  ├── 编写代码 ↔ Full-Stack Dev Agent
  ├── 修复问题 ↔ QA + Dev Agent
  └── 发布上线 ↔ DevOps Agent
        └── 回滚? ↔ SRE Agent
```

## 跨层联动示例

**场景：从需求到上线**

```
Layer 1 Rules   → 加载 coding-standards + security-checklist
Layer 2 Prompts → 激活 Tech Lead + Frontend + Backend + QA 角色
Layer 3 Tools   → scaffold + db-client + http-client + linter
Layer 4 MCP     → 启用 filesystem + git + postgres + browser MCP
Layer 5 Skills  → api-design → auth-implementation → test-strategy
Layer 6 Agents  → PM → Architect → Dev → QA → DevOps 流水线
Layer 7 Expert  → 编排 + 质量门禁 + 异常回退
Layer 8 Workflow→ feature-development.md 流程
Layer 9 Hooks   → rate_limiter + auth_check + sql_guard 中间件
Layer 10 Context→ project.yaml 持久化 + session 续传
Layer 11 Validation→ checks.py 全量校验
```

## 输出物

- 完整的可运行代码仓库
- 数据库 migration 文件
- API 文档（OpenAPI / Swagger）
- 测试报告（覆盖率 + E2E）
- 部署配置（docker-compose / CI pipeline）
- ADR 文档（架构决策记录）
- CHANGELOG + Release Notes
