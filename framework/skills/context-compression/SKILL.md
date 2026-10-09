---
name: context-compression
description: 上下文压缩实战指南。当对话过长或上下文接近上限时，按 5 级策略渐进式压缩历史消息，保留关键决策与待办。与 devkit-doctor、hooks 深度集成，可自动检测会话长度并触发压缩。
layer: orchestration
tags: [context, compression, summarization, token-management, session-management]
---

# Context Compression — 上下文压缩实战指南

## 触发条件

满足以下任一条件时自动或手动触发压缩：

| 指标 | 阈值 | 说明 |
|------|------|------|
| 对话轮次 | > 50 轮 | 用户 + agent 消息累计超过 50 条 |
| 上下文占用 | > 60% | 当前 token 占用超过模型上下文窗口 60% |
| Agent 响应 | 明显变慢 | 同等任务响应时间相比正常状态增加 50%+ |
| 手动指令 | 用户触发 | 用户输入 `/compress` 或 "压缩上下文" |

## 五级压缩策略

根据上下文占用程度和影响范围，采用渐进式压缩策略：

---

### Level 1: 轻度压缩

**触发条件**：上下文占用 60-70%，对话轮次 50-80 轮

**策略**：
- 移除代码块中的注释和空行
- 删除重复的确认性对话（"好的"、"明白了"）
- 精简 agent 的冗余解释文字

**保留**：
- 完整代码实现（仅去除注释）
- 所有决策和讨论结论
- 待办任务清单

**影响**：token 减少 10-15%，信息损失几乎为零

---

### Level 2: 中度压缩

**触发条件**：上下文占用 70-80%，对话轮次 80-150 轮

**策略**：
- 摘要较长代码块，只保留函数/类签名 + 关键逻辑说明
- 将多轮讨论压缩为结论 + 决策理由
- 移除中间调试过程的日志输出

**保留**：
- API 签名和接口契约
- 架构决策（含 ADR 编号）
- 错误修复的根因和方案
- 最终配置（不含试错过程）
- 当前任务目标与待办

**影响**：token 减少 25-35%，保留核心语义

---

### Level 3: 重度压缩

**触发条件**：上下文占用 80-90%，对话轮次 150-250 轮

**策略**：
- 保留最近 3 条消息（完整保留，确保当前任务连贯）
- 从历史消息中提取最相关的 2 条（含关键决策或架构上下文）
- 其余全部压缩为结构化摘要

**保留**：
```json
{
  "goal": "当前任务目标（一句话）",
  "decisions": ["关键决策列表"],
  "pending": ["待完成子任务"],
  "constraints": ["不可违反的约束"],
  "learnings": ["本次会话重要发现"],
  "recent_3": ["最近 3 条完整消息"],
  "relevant_2": ["最相关的 2 条历史消息（按任务相关度排序）"]
}
```

**影响**：token 减少 50-60%，可能丢失部分细节但对当前任务影响可控

---

### Level 4: 激进压缩

**触发条件**：上下文占用 90-95%，对话轮次 > 250 轮 或 接近硬上限

**策略**：
- 完全压缩所有历史讨论为当前任务的要点列表
- 丢弃所有中间代码、调试日志、讨论过程
- 仅保留"是什么"和"要做什么"，丢弃"为什么这样做"的详细论证

**保留**：
```
## 当前任务
- [任务描述]

## 已完成
- [已完成子任务列表]

## 下一步
- [下一步动作]

## 关键约束
- [不可违反的条件]
```

**影响**：token 减少 70-80%，丢失大量推理过程但保留可执行的任务上下文

---

### Level 5: 重启（清空上下文）

**触发条件**：上下文占用 > 95% 或 无法继续生成有效响应

**策略**：
- 将当前任务状态写入任务文件（参考 task-tracker 格式）
- 清空完整对话上下文
- 恢复完整 system prompt + 当前任务文件 + 最少必要上下文

**重启文件模板**（写入 `context/session-resume.json`）：
```json
{
  "resumed_at": "2026-10-08T14:30:00Z",
  "original_session_id": "session_xxx",
  "original_turn_count": 340,
  "current_task": {
    "description": "实现用户认证模块",
    "progress_pct": 65,
    "completed_steps": ["数据库设计", "API 定义", "前端表单"],
    "remaining_steps": ["后端实现", "集成测试", "部署验证"]
  },
  "key_decisions": [
    "ADR-003: 使用 JWT + Refresh Token 双令牌方案",
    "使用 bcrypt 而非 argon2（兼容性考量）"
  ],
  "latest_artifacts": [
    "src/routes/auth.ts",
    "src/models/user.ts"
  ]
}
```

**影响**：token 释放 90%+，丢失所有历史但可基于文件恢复工作状态

---

## 保留清单：什么时候不能压缩

以下场景执行压缩会导致严重信息丢失或操作失败：

| 场景 | 原因 | 替代方案 |
|------|------|---------|
| 正在写长文件 | 压缩后可能丢失文件已写部分的结构记忆 | 完成写入后再压缩 |
| 正在调试复杂问题 | 错误信息和调试线索是关键上下文 | 保留最近 20 轮 + 所有错误相关消息 |
| 正在做架构决策 | 决策论证过程对后续实现至关重要 | 仅用 Level 1 压缩 |
| 多模块并行开发 | 压缩后容易混淆不同模块的上下文 | 按模块分别压缩 |
| Git 操作进行中 | 操作上下文对完成提交/PR 必须 | 完成操作后压缩 |
| 子 Agent 刚返回结果 | 结果可能是后续任务的关键输入 | 消费完结果后再压缩 |

**规则**：当不确定是否应压缩时，选择比当前级别更保守的策略（低一级）。

---

## Prompt 模板

### 通用压缩指令

先复制以下模板到对话中触发压缩：

```
【压缩指令 - Level {N}】

请对当前对话上下文执行 Level {N} 压缩：

1. 提取以下结构化信息：
   - 当前任务目标
   - 已完成的子任务
   - 待完成的子任务
   - 关键架构/技术决策
   - 不可违反的约束条件

2. 按 Level {N} 策略执行压缩：
   - Level 1: 仅去除代码注释/空行/冗余对话
   - Level 2: 代码摘要化，保留签名+关键逻辑
   - Level 3: 保留最近3+最相关2，其余压缩
   - Level 4: 压缩为任务要点列表
   - Level 5: 写入 session-resume.json 后重置

3. 压缩完成后输出：
   - 原始 token 估算 vs 压缩后 token 估算
   - 压缩摘要（可直接作为新 context 开头）
   - 如有无法压缩的关键信息，标注警告
```

### Level 5 重启专用指令

```
【上下文重启指令】

当前上下文已接近上限，执行安全重启：

1. 将当前任务状态写入 context/session-resume.json
2. 列出所有未完成的文件路径和最后编辑位置
3. 确认重启后可基于 resume 文件恢复工作
4. 清空上下文，以 system prompt + session-resume.json 开始

注意：如果有未保存的代码修改，请先确保已写入磁盘。
```

### 与 devkit-doctor 集成检查指令

```
请检查当前会话上下文使用率：
1. 调用 devkit-doctor 检查 session 状态
2. 如果上下文占用 > 60%，建议压缩级别：
   - 60-70% → Level 1（轻度）
   - 70-80% → Level 2（中度）
   - 80-90% → Level 3（重度）
   - 90-95% → Level 4（激进）
   - > 95%    → Level 5（重启）
3. 输出压缩建议，等待用户确认后执行
```

---

## 与现有组件集成

### 1. 与 devkit-doctor 集成

devkit-doctor 可检查当前会话长度并在状态报告中添加压缩建议：

```yaml
# devkit-doctor 扩展检查项
checks:
  session_health:
    - metric: context_utilization
      warning_threshold: 0.60
      critical_threshold: 0.85
      action: recommend_compression

    - metric: turn_count
      warning_threshold: 50
      critical_threshold: 150
      action: recommend_compression
```

doctor 输出示例：
```
Session Health Check:
  Context utilization: 78% (WARNING)
  Turn count: 92 (WARNING)
  Recommendation: Apply Level 2 compression before continuing
```

### 2. 与 Hooks 集成

在 `hooks/config.yaml` 中添加上下文长度监控钩子：

```yaml
hooks:
  agent_lifecycle:
    on_agent_start:
      - script: "hooks/scripts/load-project-context.sh"
        timeout: 5
        description: "加载项目上下文"
      - script: "hooks/scripts/context-check.sh"
        timeout: 10
        description: "检查上次会话长度，判断是否需要压缩恢复"
```

新增 `hooks/scripts/context-check.sh` 脚本逻辑：

```bash
#!/usr/bin/env bash
# 检查上次会话长度，在 agent 启动时给出压缩恢复建议

SESSION_LOG="logs/session-length.log"
if [[ -f "$SESSION_LOG" ]]; then
    LAST_LENGTH=$(tail -1 "$SESSION_LOG" | jq -r '.turn_count // 0')
    if [[ "$LAST_LENGTH" -gt 50 ]]; then
        echo "WARNING: 上次会话 $LAST_LENGTH 轮，建议："
        if [[ "$LAST_LENGTH" -gt 250 ]]; then
            echo "  → 建议使用 Level 5 重启恢复（检查 context/session-resume.json）"
        elif [[ "$LAST_LENGTH" -gt 150 ]]; then
            echo "  → 建议使用 Level 3 压缩恢复"
        else
            echo "  → 建议使用 Level 2 压缩"
        fi
    fi
fi
```

### 3. 与 scaffold 集成

在 scaffold 步骤边界自动压缩：

```yaml
steps:
  - goal: "实现模块 A"
    outputs:
      - src/module/a.ts
    on_complete:
      compress:
        level: 1  # 每完成一步轻度压缩

post_task:
  compress:
    level: 2  # 任务完成后中度压缩，准备交付
```

### 4. 与 memory-persistent 集成

关键决策在压缩前写入持久化内存，确保压缩后仍可追溯：

```yaml
before_compress:
  - persist: decisions  # 将决策写入 memory/
  - persist: learnings  # 将经验写入 memory/
```

---

## 压缩策略决策树

```
当前上下文使用率？
├── < 60% → 不压缩，继续正常工作
├── 60-70% → Level 1（轻度）：去注释/空行/冗余
│   └── 正在写文件？→ 推迟到写入完成
├── 70-80% → Level 2（中度）：代码摘要化
│   └── 正在调试？→ 保留最近 20 轮 + 错误信息
├── 80-90% → Level 3（重度）：保留最近 3 + 最相关 2
│   └── 正在做架构决策？→ 降级到 Level 1
├── 90-95% → Level 4（激进）：压缩为要点列表
│   └── 有未写入磁盘的修改？→ 先写入文件再压缩
└── > 95% → Level 5（重启）：写 resume 文件 + 清空上下文
    └── 必须先确保所有修改已写入磁盘
```

---

## Checklist

- [ ] 触发条件监控：对话轮次 > 50 或上下文 > 60% 时自动提醒
- [ ] 渐进式策略：从 Level 1 到 Level 5 逐级升级，不跳级
- [ ] 保留清单遵守：写长文件/调试/架构决策时不压缩或降级
- [ ] 决策持久化：关键决策在压缩前写入 memory-persistent
- [ ] 可逆性保障：Level 5 重启必须有 session-resume.json
- [ ] devkit-doctor 集成：session health check 包含上下文使用率指标
- [ ] hooks 集成：on_agent_start 检查上次会话长度并给出恢复建议
- [ ] 信息损失确认：压缩后输出 token 减少量和丢失内容摘要
- [ ] 追溯能力：保留完整会话日志（logs/），可回溯原始讨论

## 推荐 SubAgent

- architect-system-designer（决策摘要提取与 ADR 关联）
- task-tracker（任务状态持久化与恢复点创建）
