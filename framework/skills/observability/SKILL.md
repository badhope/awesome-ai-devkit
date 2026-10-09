---
name: observability
description: 可观测性实践。为应用接入日志、指标、链路追踪，定义健康检查与监控，便于定位问题、评估性能、支持 SLO/SLI。
layer: infra
tags: [observability, logging, metrics, tracing, monitoring, slo]
---

# Observability — 可观测性

## 触发条件
- 新增/改造服务、排查线上问题、定义监控时使用。

## 三大支柱
1. **Logs（日志）**：结构化（JSON）、有 `request_id`/时间/级别/服务
2. **Metrics（指标）**：RED/USE 方法论
   - RED：Rate（请求率）、Errors（错误率）、Duration（延迟）
   - USE：Utilization、Saturation、Errors
3. **Traces（追踪）**：跨服务请求链路，定位慢路径

## 关键实践
- **结构化日志**：禁止散乱 print；统一格式 `{ts, level, service, request_id, msg, ...}`
- **健康检查**：`/health`（存活）+ `/ready`（就绪），用于探活/滚动发布
- **SLO/SLI**：定义服务可用性目标（如 99.9%），用 SLI 度量
- **告警**：围绕 SLO 设告警，避免噪声（不监控一切）
- **观测配置**：日志/指标归集到统一平台（若接入 MCP 见 `mcp-config`）

## 输出
```
观测方案:
- 日志规范（字段/级别/归集）
- 关键指标（RED 三件套 + 业务指标）
- 健康检查端点
- SLO/SLI 定义
- 告警规则
```

## Checklist
- [ ] 结构化日志、含 request_id
- [ ] 有健康检查端点
- [ ] 定义 SLO/SLI
- [ ] 关键路径有指标/追踪