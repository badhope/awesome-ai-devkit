---
name: memory-persistent
description: 持久化跨会话记忆。基于文件系统的长期经验存储，对齐 OpenClaw 2.0 的 Memory 持久记忆组和 OpenCode 的 SQLite 持久化会话存储。
layer: orchestration
tags: [memory, persistence, cross-session, learning]
---

# Persistent Memory -- 跨会话持久化记忆

## 触发条件

每个开发会话结束时自动保存关键信息，下次开工前自动查询相关历史。

## 核心模式

### 1. 存储架构（三层）

```
会话层: logs/sessions/<id>/memory.json    <- 当前会话临时
项目层: context/memory/entries/*.jsonl    <- 跨会话持久（推荐主用）
个人层: ~/.config/devkit/memory/entries/*.jsonl  <- 跨项目持久（可选）
```

### 2. 记忆条目格式

```jsonl
// context/memory/entries/<topic>.jsonl
{"ts":"2026-10-06T10:00:00Z","type":"lesson","scope":"project","tags":["auth"],"summary":"...","confidence":0.95}
{"ts":"2026-10-06T11:00:00Z","type":"decision","scope":"project","tags":["db","postgres"],"summary":"...","confidence":0.9}
{"ts":"2026-10-06T12:00:00Z","type":"warning","scope":"project","tags":["security","sqli"],"summary":"...","confidence":1.0}
```

### 3. 检索与注入

```
新任务开工:
  1. 从 scaffold.yaml memory_query.tags 获取搜索标签
  2. 扫描 context/memory/entries/*.jsonl
  3. 按 tag 交集 + 时间戳排序
  4. 返回最近 N 条高置信度记忆
  5. 注入 agent context

相关性算法:
  score = tag_overlap * 0.5 + confidence * 0.3 + recency * 0.2
  recency = 1.0 / (1 + days_since)
  返回 score > 0.5 的 top-N
```

### 4. 维护规则

| 规则 | 说明 |
|------|------|
| 单文件 < 100KB | 超过按月份轮转 |
| 敏感数据不入记忆 | API key/密码不提取 |
| 过期机制 | > 6 个月降低权重 |
| 去重 | 同类 lesson 只保留最新 |

## 推荐 SubAgent

- architect-system-designer（decision 提取）
- security-review-engineer（warning 提取）
