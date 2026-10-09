---
name: memory-management
description: Agent 长期记忆管理。任务完成后自动提取经验教训，下次开工前自动加载相关记忆。对齐 OpenClaw/Ruflo 的主动记忆模式。
layer: orchestration
tags: [memory, experience, learning, persistence, agent-state]
---

# Memory Management — Agent 经验沉淀与复用

## 触发条件

每个开发任务完成后（post-task hook）自动执行经验提取；每个任务开工前（pre-task hook）自动加载相关记忆。

## 核心模式

### 1. 记忆层级

```
会话级 (session)  →  logs/sessions/<id>/    自动管理，短期
项目级 (project)  →  context/memory/        跨会话持久
个人级 (personal) →  ~/.config/devkit/memory/ 跨项目持久（可选）
```

### 2. 记忆数据结构

```jsonl
// context/memory/entries/<topic>.jsonl
{"ts":"2026-10-06T10:00:00Z","type":"lesson","scope":"project","tags":["auth","jwt"],"summary":"JWT 秘钥必须 ≥ 32 字节且存环境变量","confidence":0.95}
{"ts":"2026-10-06T10:05:00Z","type":"decision","scope":"project","tags":["db","postgres"],"summary":"选型 Postgres 而非 MySQL: 项目需要 JSONB 全文搜索","confidence":0.9}
```

| type | 用途 | 触发时机 |
|------|------|---------|
| lesson | 踩坑教训 | 失败或发现问题后 |
| decision | 技术选型原因 | ADR 写入后 |
| pattern | 可复用做法 | 发现优雅解法时 |
| warning | 安全风险/注意事项 | 安全审查发现后 |

### 3. Post-task 记忆提取规则

任务完成 → agent 在 `context/memory/entries/` 写入本次发现（每条 1 行 JSONL）：

```
必须写入:
  - 踩过的坑 → type: lesson
  - 关键决策 → type: decision（引用 ADR 编号）

可选写入:
  - 好模式 → type: pattern
  - 安全警告 → type: warning
```

### 4. Pre-task 记忆加载

scaffold.yaml 的 `memory` 段扩展为支持标签过滤：

```yaml
memory:
  - context/project.yaml
  - context/architecture.md
  - memory_query:
      tags: [auth, security]    # 按标签匹配
      scope: project
      limit: 5                  # 最多加载 5 条
```

Agent 执行 `memory_query` 时，扫描 `context/memory/entries/*.jsonl`，按 tags 交集排序，返回最近 N 条。

### 5. 存储约束

| 规则 | 说明 |
|------|------|
| 单文件 < 100KB | 超过按月份轮转 |
| 敏感信息不入记忆 | API key/密码等不提取 |
| 过期机制 | 超过 6 个月标记 stale，仅匹配时降低权重 |
| 去重 | 同类 lesson 只保留最新一条（按 tags + summary hash） |

## Checklist

- [ ] 每次任务完成至少提取 1 条 lesson 或 decision
- [ ] 经验按标签组织，不含无用信息
- [ ] 加载时按 tag 相关性过滤
- [ ] 有时间戳和置信度
- [ ] 敏感数据不进记忆文件

## 推荐 SubAgent

- architect-system-designer（decision 提取）
- security-review-engineer（warning 提取）
- test-qa-engineer（lesson 提取）
