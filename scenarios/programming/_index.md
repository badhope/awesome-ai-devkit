---
name: 编程开发
description: Web 全栈、移动端、AI 原生、命令行工具、开源库等编程任务的通用框架
lifecycle_stage: active
target_users: [全栈工程师, 移动端工程师, 工具链开发者]
---

# 编程开发场景

> **灵活为本**：以下所有角色/技能/工具数量为**推荐值**，非硬性要求。实际项目按团队规模、复杂度、预算自由裁剪。

## 推荐角色组合

### 极简模式（1-2 人，推荐）
- `tech-lead`（兼架构）
- `senior-developer`（兼前后端）
- `qa-engineer`（兼安全）

### 标准模式（3-7 人）
- `product-manager`
- `tech-lead`
- `frontend-developer`
- `backend-developer`
- `qa-engineer`
- `devops-engineer`

### 完整模式（8+ 人）
参考 `roles/expanded/PROGRAMMING_ROLES.md` 全角色列表

## 子场景

| 子场景 | 说明 | 入口 |
|--------|------|------|
| coding | **通用编程底座**（跨语言/技术栈，规划→编码→测试→提交；可被其他子场景继承） | `scenarios/programming/coding/` |
| fullstack | Web 全栈应用（前后端 + 数据库 + 部署） | `scenarios/programming/fullstack/` |
| mobile | iOS / Android / 跨平台 | `scenarios/programming/mobile/` |
| ml-native | AI 原生应用（LLM Agent、RAG、Copilot） | `scenarios/programming/ml-native/` |
| cli-tool | 命令行工具 / DevTool | `scenarios/programming/cli-tool/` |
| library | 开源库 / SDK / 框架 | `scenarios/programming/library/` |

## 通用能力

所有编程子场景共享：
- `skills/` — API 设计、数据库建模、测试编写、代码审查、CI/CD 流水线
- `hooks/` — pre-commit lint、安全审计、依赖检查
- `workflows/` — 需求→设计→实现→测试→部署 全流程

## 推荐 Hooks

```
before_tool_call: [auth-check, rate-limit, cache-lookup]
after_tool_call:  [log-writer, cache-write, metrics-push]
on_agent_start:   [context-loader, env-check]
on_agent_error:  [alert-dispatcher]
```
