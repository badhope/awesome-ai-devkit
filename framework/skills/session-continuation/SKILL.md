---
name: session-continuation
description: 跨会话续传。把一次会话的关键上下文（目标、决策、进度、技术栈、约定）沉淀为可复用的摘要/状态，让新会话无需重复交代即可续接任务。
layer: context
tags: [session, continuation, context, handoff, memory]
---

# Session Continuation — 会话续传

## 触发条件
- 任务跨多个会话、需要换新会话/新 agent 继续、或要交接进度时。

## 目标
- 新会话能**快速进入状态**：知道在做什么、做到哪、下一步是什么、有哪些约束，不需要重新读全部内容。

## 沉淀内容（写一个 handoff 文件）
```
# Session Handoff — <task>
## 目标
<当前 goal>
## 进度
<已完成 / 进行中>
## 关键决策
<ADR / 技术选型 / 约定>
## 技术栈与环境
<框架/依赖/命令>
## 下一步
<明确的 TODO>
## 风险 / 阻塞
<待决事项>
```

## 位置约定
- 写到一个固定文件（如 `docs/handoff.md` 或 `context/session.md`），新会话读取即可续接
- 与 `memory-persistent`、`context-compression` 配合：长记忆存持久层，短期状态存 handoff

## 原则
- **简洁可执行**：下一步要明确，不模糊
- **即时更新**：任务节点更新 handoff，而非任务结束才写
- **不重复**：技术栈等已在 context 的不重复，只写增量

## Checklist
- [ ] 有明确的 handoff 文件
- [ ] 含目标/进度/决策/下一步
- [ ] 新会话读它能直接续接
- [ ] 与记忆/上下文配合