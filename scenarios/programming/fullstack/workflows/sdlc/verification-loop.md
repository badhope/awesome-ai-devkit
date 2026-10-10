---
name: verification-loop
description: 工程验证循环（Loop Engineering）工作流。任务完成后自动执行质量门禁验证、收集失败项、自动修复、重新验证，循环直到全部通过。Claude Code/Codex 核心 self-heal 模式的标准化实现。
version: "1.0"
agents_involved:
  - code-reviewer
  - test-qa-engineer
  - security-review-engineer
  - backend-api-developer
  - frontend-ui-developer
  - devops-deploy-engineer
estimated_duration: 1-10 分钟（取决于门禁数量和修复复杂度）
---

# 验证循环工作流

> 任务完成后不假设一次成功。通过迭代循环持续验证和修复，直到所有质量门禁通过或耗尽最大循环次数。

---

## 流程总览

```
                ┌─────────────────────┐
                │  收集质量门禁清单     │
                └──────────┬──────────┘
                           │
                ┌──────────▼──────────┐
                │  Round N: 执行验证   │◄──────────┐
                └──────────┬──────────┘           │
                           │                       │
                ┌──────────▼──────────┐           │
                │  分类门禁结果        │           │
                │  PASS / FAIL / WARN  │           │
                └──────────┬──────────┘           │
                           │                       │
              ┌────────────┼────────────┐         │
              │            │            │         │
    ┌─────────▼──┐  ┌─────▼─────┐  ┌──▼────────┐│
    │ 全部通过    │  │ 可自动修复  │  │ 需人工介入 ││
    │ → 成功退出  │  │ → 修复代码  │  │ → 记录报告 ││
    └────────────┘  └─────┬──────┘  └───────────┘│
                          │                       │
                ┌─────────▼──────────┐           │
                │  重跑验证            ├───────────┘
                └─────────────────────┘
                          │
                ┌─────────▼──────────┐
                │  达到 max_loops?    │──是──→ 报告剩余失败
                └─────────────────────┘
```

---

## Stage 1: 收集门禁清单

**触发**: post_task 阶段启动时

**输入**:
- scaffold.yaml 中 `post_task.quality_gates` 定义的门禁列表
- loop_config 配置参数（max_loops, fail_threshold, auto_fix）
- devkit-doctor 基线报告

**产出**:
- 结构化的门禁队列（gate_queue）
- 每条门禁对应的检查命令和修复策略映射

**执行逻辑**:

```
1. 读取 scaffold.yaml → post_task.quality_gates[]
2. 解析每条门禁描述 → 映射到 GateChecker
3. 运行 devkit-doctor --format json 获取基线健康状态
4. 合并生成完整验证计划
```

**验收条件**:
- [ ] 所有门禁条目已解析并映射到检查器
- [ ] devkit-doctor 基线报告可用
- [ ] loop_config 参数已加载

---

## Stage 2: 执行验证（单轮）

**触发**: 每轮循环开始

**输入**: gate_queue（待验证门禁列表）

**门禁检查项**:
- 测试通过率：运行测试命令，确认全部 pass
- 覆盖率达标：检查覆盖率是否 ≥ 阈值（默认 60%）
- 安全硬编码：grep 敏感词仅出现在 test/mock
- Lint 零错误：确认无 error 级别 lint 问题
- 类型检查：TypeScript/mypy 零错误
- CHANGELOG：文档已更新且包含当前变更
- 架构决策：如有 ADR，memory/persistent 已更新

**验收条件**:
- [ ] 每个门禁有明确的 PASS / FAIL / WARN 状态
- [ ] FAIL 门禁已标记是否 auto_fixable
- [ ] 有错误输出的门禁已捕获完整 stderr

---

## Stage 3: 自动修复

**触发**: 存在 auto_fixable 的 FAIL 项

**修复策略映射**:

| 门禁类型 | 修复动作 | 负责 SubAgent |
|---------|---------|--------------|
| 测试失败 | 分析错误堆栈 → 定位根因 → 修改源码 → 重跑 | backend-api-developer / frontend-ui-developer |
| 覆盖率低 | 分析未覆盖分支 → 补充测试用例 | test-qa-engineer |
| Lint 错误 | 运行 linter --fix / formatter | code-reviewer |
| 类型错误 | 根据 TS/mypy 输出修正类型标注 | backend-api-developer / frontend-ui-developer |
| 安全泄露 | 移除硬编码密钥 → 替换为 env var 引用 | security-review-engineer |
| CHANGELOG | 基于 git log 生成 changelog 条目 | code-reviewer |

**不可自动修复项**:
- ADR 更新（需人工撰写架构决策）
- 文档完整度（需人工撰写文档）
- 业务逻辑正确性（需人工验收）

**验收条件**:
- [ ] 所有 auto_fixable FAIL 项已执行修复
- [ ] 修复内容有完整 diff 记录
- [ ] 不可修复项已明确标记并给出人工指引

---

## Stage 4: 循环判断

**决策逻辑**:

```
IF all_gates_passed AND fail_count <= fail_threshold:
    STATUS = SUCCESS
    退出循环，输出成功报告

ELIF current_loop >= max_loops:
    STATUS = EXHAUSTED
    退出循环，输出剩余失败报告（含修复建议）

ELSE:
    STATUS = CONTINUE
    current_loop += 1
    返回 Stage 2（执行验证）
```

**成功标准**:
- 所有门禁状态为 PASS
- 或剩余 FAIL 数 ≤ fail_threshold 且均为 manual_required

**失败标准**:
- 达到 max_loops 后仍有 auto_fixable FAIL 项（修复策略不足）
- 存在 stop_on_unfixable=true 的不可修复项

---

## Stage 5: 输出报告

**成功报告格式**:

```
╔══════════════════════════════════════════════╗
║  Loop Verification — PASSED                  ║
║  Completed in 2 rounds                       ║
╠══════════════════════════════════════════════╣
║  ✓ 全量测试通过 (14/14 pass)                  ║
║  ✓ 覆盖率 ≥ 60% (当前 62%)                    ║
║  ✓ 无安全硬编码泄露                            ║
║  ✓ CHANGELOG 已更新                           ║
║  ✓ memory-persistent 已更新                   ║
╠══════════════════════════════════════════════╣
║  Doctor baseline: PASS (5/5 checks green)     ║
║  Total fixes applied: 3                       ║
╚══════════════════════════════════════════════╝
```

**失败报告格式**:

```
╔══════════════════════════════════════════════╗
║  Loop Verification — EXHAUSTED               ║
║  3/3 rounds completed                        ║
╠══════════════════════════════════════════════╣
║  ✓ 全量测试通过                               ║
║  ✓ 覆盖率达标                                 ║
║  ✓ 安全门禁通过                               ║
║  ✗ ADR 已更新                                 ║
║  ✗ 文档完整度                                 ║
╠══════════════════════════════════════════════╣
║  Manual Actions Required:                     ║
║  1. 在 context/architecture.md 追加 ADR 条目  ║
║  2. 补充 deployment.md 中的回滚步骤说明       ║
╠══════════════════════════════════════════════╣
║  Doctor baseline: WARN (1 warning)            ║
║  Auto-fixable failures remaining: 0           ║
║  Manual attention needed: 2                   ║
╚══════════════════════════════════════════════╝
```

---

## 使用示例

### 示例 1: Feature Development Scaffold

```yaml
# feature-development.yaml
post_task:
  quality_gates:
    - "全量测试通过: 运行项目测试命令，所有 pass"
    - "覆盖率 ≥ 60%（核心业务模块）"
    - "无安全硬编码泄露: grep 敏感词仅出现在 test/mock 中"
    - "CHANGELOG 已更新"
    - "memory-persistent 已更新（如有架构决策）"
  loop_config:
    max_loops: 3
    fail_threshold: 0
```

执行输出:
```
Round 1: 3 PASS, 2 FAIL (覆盖率不足, CHANGELOG缺失) → auto-fix →
Round 2: 5 PASS → SUCCESS
```

### 示例 2: Incident Response Scaffold

```yaml
# incident-response.yaml
post_task:
  quality_gates:
    - "回归测试全部通过"
    - "监控仪表盘无异常告警"
    - "复盘报告有时间线和改进项"
  loop_config:
    max_loops: 2
    fail_threshold: 0
```

### 示例 3: Refactoring Scaffold

```yaml
# refactoring.yaml
post_task:
  quality_gates:
    - "所有测试通过（含回归守护测试）"
    - "性能无 regression"
    - "无新增安全漏洞"
    - "ADR 已更新"
  loop_config:
    max_loops: 3
    fail_threshold: 0
```

---

## 与 devkit-doctor.py 协同

```
┌─────────────────────────────────────────────────────────┐
│                   Loop Verification                      │
│                                                          │
│  Round 1                                                 │
│  ├─ devkit-doctor --format json  → 基线报告             │
│  ├─ 门禁检查                        → 5 项待验证        │
│  ├─ 2 FAIL (auto-fixable)           → 修复队列          │
│  └─ 执行修复                                             │
│                                                          │
│  Round 2                                                 │
│  ├─ devkit-doctor --format json  → 修复后验证           │
│  ├─ 门禁检查                        → 5 项待验证        │
│  └─ 5 PASS                          → SUCCESS           │
│                                                          │
│  Report: 合并 doctor 5/5 pass + gates 5/5 pass          │
└─────────────────────────────────────────────────────────┘
```

---

## 异常流程

| 异常场景 | 处理方式 |
|---------|---------|
| 修复后引入新失败 | 回滚本轮修复，标记该门禁为 manual_required |
| 连续 2 轮无改善 | 提前退出循环，报告需要架构级修改 |
| devkit-doctor 检查异常 | 记录异常但继续门禁检查 |
| 循环超时（>10min） | 强制退出，报告已完成轮次的结果 |
| auto_fix 产生语法错误 | 回滚该文件修复，标记为 manual_required |

---

## Hooks 集成建议

```yaml
# hooks/config.yaml
hooks:
  agent_lifecycle:
    on_agent_end:
      - script: "framework/skills/loop-verification/run-loop.sh"
        timeout: 120
        description: "循环验证质量门禁直到全部通过"
        config:
          max_loops: 3
          fail_threshold: 0
          auto_fix: true
```

---

## 版本演进

| 版本 | 变更 |
|------|------|
| v1.0 | 初始版本：基础循环验证 + scaffold 集成 + devkit-doctor 协同 |
| v1.1 (计划) | 并行门禁检查、增量验证（只检查变更相关门禁） |
| v1.2 (计划) | 门禁结果缓存、跨循环学习修复策略 |
