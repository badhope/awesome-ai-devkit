---
name: task-tracker
description: 任务追踪与进度管理。在 agent 长任务执行中维护 status/progress，对齐 Claude Code 的 TodoWrite 工具模式。防止复杂多步骤任务丢失进度。
layer: orchestration
tags: [task, tracking, todo, progress, agent-state]
---

# Task Tracker -- Agent 任务进度追踪

## 触发条件

执行涉及 3 个以上步骤的复杂任务时，agent 创建并维护任务清单。

## 核心模式

### 1. 任务生命周期

```
pending     待执行
in_progress 正在执行（当前步骤）
completed   完成
blocked     阻塞（外部依赖 / 等待人类）
skipped     跳过（经评估后不需要）
```

### 2. 任务文件格式

```json
// logs/sessions/<session-id>/tasks.json
{
  "session_id": "task-20261006-100000",
  "tasks": [
    {
      "id": "t1",
      "title": "定义数据模型",
      "status": "completed",
      "output": "models/user.py",
      "duration_ms": 12000
    },
    {
      "id": "t2",
      "title": "实现 API 端点",
      "status": "in_progress",
      "depends_on": ["t1"]
    },
    {
      "id": "t3",
      "title": "编写集成测试",
      "status": "pending",
      "depends_on": ["t2"]
    }
  ],
  "updated_at": "2026-10-06T10:00:00Z"
}
```

### 3. 任务拆分原则

```
粒度参考:
  任务 title ≈ "实现 X 功能" 或 "修复 Y 问题"
  输出 ≈ 一个文件或一个测试通过
  耗时 ≈ 30s - 5min

✗ 不拆太小（"创建目录"不值得一个任务）
✗ 不拆太大（"实现整个认证系统"太粗，需拆分）
```

### 4. 可视化输出

```
═══════════════════════════════════════════
 Task Progress [task-20261006-100000]
═══════════════════════════════════════════
 ✓ t1 定义数据模型        (12s)
 ✓ t2 实现 API 端点       (28s)
 ► t3 编写集成测试        (in progress...)
 ⏳ t4 运行全量测试        (pending)

 Progress: 2/4 | Elapsed: 40s | ETA: ~2min
═══════════════════════════════════════════
```

### 5. 与 Scaffold 集成

scaffold.yaml 输出自动成为任务追踪源，步骤完成即更新 task status。

## Checklist

- [ ] 长任务（>3步）自动创建 task list
- [ ] 每个任务有明确完成标准（文件路径或测试通过）
- [ ] 阻塞时立即报告，不静默跳过
- [ ] 完成后更新 task status（不遗留 in_progress）

## 推荐 SubAgent

- architect-system-designer（任务拆分）
- test-qa-engineer（验证完成标准）
