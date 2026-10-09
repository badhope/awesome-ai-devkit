---
name: loop-verification
description: 工程验证循环（Loop Engineering）。任务完成后自动执行质量门禁验证、收集失败项、自动修复、重新验证，循环直到全部通过。对齐 Claude Code/Codex 的核心 self-verify 模式。可配置 max_loops（默认 3）和 fail_threshold。与 scaffold post_task.quality_gates 和 devkit-doctor.py 深度集成。
layer: quality
tags: [verification, loop, auto-fix, quality-gates, self-heal, iterative]
---

# Loop Verification — 工程验证循环

## 触发条件

任务开发阶段完成后（post_task 阶段）自动触发，或手动调用以对项目执行全量质量门禁循环验证。

## 核心理念

```
验证 → 收集失败 → 自动修复 → 重新验证 → ... → 全部通过
```

对齐 Claude Code/Codex 的 self-heal 模式：任务完成后不假设一次成功，而是通过迭代循环持续验证和修复，直到所有质量门禁通过或达到最大循环次数。

## 配置参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `max_loops` | 3 | 最大验证循环次数 |
| `fail_threshold` | 0 | 允许通过的失败门禁数（0 = 全部必须通过） |
| `auto_fix` | true | 是否自动修复可修复的失败项 |
| `stop_on_unfixable` | false | 遇到不可修复项时是否立即停止 |

### 配置方式

在 scaffold.yaml 中配置：

```yaml
post_task:
  quality_gates:
    - "loop-verification: 自动循环验证所有质量门禁，最多 3 轮"
  loop_config:
    max_loops: 3
    fail_threshold: 0
    auto_fix: true
```

## 执行流程

### 阶段 1：收集门禁清单

从 scaffold post_task.quality_gates 读取所有质量门禁检查项，构建验证队列。

```
输入: scaffold.yaml → post_task.quality_gates[]
输出: gate_queue = [gate_1, gate_2, ..., gate_n]
```

### 阶段 2：执行验证（单轮）

对每个门禁执行检查，分类结果：

| 状态 | 含义 | 处理 |
|------|------|------|
| PASS | 当前轮通过 | 标记为 done |
| FAIL + auto_fixable | 可自动修复 | 进入修复队列 |
| FAIL + manual_required | 需人工介入 | 记录并报告 |
| WARN | 警告但不阻塞 | 记录，按 fail_threshold 判断 |

### 阶段 3：自动修复

对 `auto_fixable` 的失败项调用对应修复策略：

| 门禁类型 | 修复策略 |
|----------|---------|
| 测试失败 | 分析错误输出，定位根因，修改代码重跑 |
| Lint 错误 | 运行 linter --fix / formatter |
| 类型错误 | 根据 TS/mypy 输出修正类型 |
| 安全泄露 | 移除硬编码密钥，替换为环境变量引用 |
| 覆盖率不足 | 补充测试用例 |
| CHANGELOG 缺失 | 根据 git log 生成 changelog 条目 |

### 阶段 4：循环判断

```
if all_passed and fail_count <= fail_threshold:
    → 退出循环，报告成功
elif current_loop >= max_loops:
    → 退出循环，报告剩余失败项（含修复建议）
else:
    → current_loop++, 返回阶段 2
```

## 集成点

### 1. 与 scaffold post_task.quality_gates 集成

scaffold.yaml 中定义的每条 `quality_gates` 条目都会被 loop-verification 逐一验证：

```yaml
# feature-development.yaml 示例
post_task:
  quality_gates:
    - "全量测试通过: 运行项目测试命令，所有 pass"
    - "覆盖率 ≥ 60%（核心业务模块）"
    - "无安全硬编码泄露: grep 敏感词仅出现在 test/mock 中"
    - "CHANGELOG 已更新"
    - "memory-persistent 已更新（如有架构决策）"
    - "loop-verification: 自动循环验证所有质量门禁，最多 3 轮"
```

loop-verification 会解析每条门禁的描述文本，映射到对应的检查命令和修复策略。

### 2. 与 devkit-doctor.py 集成

loop-verification 复用 devkit-doctor 的检查器架构：

```python
# 调用 devkit-doctor 获取基础检查结果
python devkit-doctor.py --format json --root /path/to/project

# loop-verification 在此基础上叠加门禁级检查
# 并在循环中逐轮重跑 doctor 确认修复效果
```

集成方式：
- loop-verification 启动时先执行一次 `devkit-doctor` 获取基线
- 每轮修复后重跑 `devkit-doctor` 验证改善情况
- 最终报告合并 doctor 检查和门禁检查结果

### 3. 与 hooks 集成

在 `hooks/config.yaml` 中注册 loop-verification 为 on_agent_end 钩子：

```yaml
hooks:
  agent_lifecycle:
    on_agent_end:
      - script: "skills/loop-verification/run-loop.sh"
        timeout: 120
        description: "循环验证质量门禁直到全部通过"
```

## 门禁检查映射表

| 门禁关键词 | 检查命令 | 自动修复 |
|-----------|---------|---------|
| 测试通过 | `pytest` / `npm test` / `go test ./...` | 是（根据错误定位修复） |
| 覆盖率 | `pytest --cov` / `npm test -- --cov` | 是（补充测试用例） |
| 安全硬编码 | `grep -r "password\|secret\|token" src/` | 是（替换为 env var） |
| Lint | `eslint` / `ruff check` / `golangci-lint run` | 是（linter --fix） |
| 类型检查 | `tsc --noEmit` / `mypy` | 部分（简单类型可自动修补） |
| CHANGELOG | `test -f CHANGELOG.md && git diff` | 是（根据 commits 生成） |
| 内存持久化 | `test -f context/memory/` | 否（需 Agent 判断） |
| ADR 更新 | `grep -l "ADR" context/architecture.md` | 否（需人工撰写） |
| 文档完整 | `ls docs/` 检查 | 否（需人工撰写） |

## 输出格式

### 单轮报告

```
=== Loop Verification — Round 1/3 ===

 Quality Gates Status:
 ✓ 全量测试通过 (12/12 pass)
 ✗ 覆盖率 ≥ 60% (当前 45%)          → auto-fixable
 ✓ 无安全硬编码泄露
 ✗ CHANGELOG 已更新 (未发现变更)     → auto_fixable
 ✓ memory-persistent 已更新

 Auto-fixing 2 failures...
   → 补充 auth 模块测试用例 (+12% 覆盖率)
   → 基于 5 commits 生成 CHANGELOG 条目

=== Loop Verification — Round 2/3 ===

 Quality Gates Status:
 ✓ 全量测试通过 (14/14 pass)
 ✓ 覆盖率 ≥ 60% (当前 62%)
 ✓ 无安全硬编码泄露
 ✓ CHANGELOG 已更新
 ✓ memory-persistent 已更新

 ALL GATES PASSED (2 rounds)
```

### 最终报告（max_loops 耗尽）

```
=== Loop Verification — COMPLETED (3/3 rounds exhausted) ===

 Remaining Failures (1):
 ✗ ADR 已更新 — 架构决策文档缺少本次变更记录
   → Manual fix required: 在 context/architecture.md 追加 ADR 条目

 Summary:
 - Passed: 4/5 gates
 - Auto-fixed: 3 failures across 2 rounds
 - Manual attention needed: 1 gate
 - Doctor baseline: PASS (all checks green)
```

## 推荐 SubAgent

- test-qa-engineer（测试失败分析与补充用例编写）
- security-review-engineer（安全门禁检查与修复）
- code-reviewer（lint/类型门禁的修复验证）
- devops-deploy-engineer（CI 集成确保循环在流水线中执行）

## 与 Other Skills 的关系

| Skill | 关系 |
|-------|------|
| linter-formatter | loop-verification 调用 lint 结果作为门禁 |
| project-health | loop-verification 复用健康检查维度和评分 |
| security-governance | 安全门禁复用 security skill 的检查项 |
| code-duplication | 代码重复率可作为额外门禁加入循环 |
| memory-persistent | 架构决策持久化门禁 |

## Checklist

- [ ] scaffold post_task 已注册 loop-verification 门禁
- [ ] max_loops 根据项目规模合理设置（简单项目 2，复杂项目 5）
- [ ] fail_threshold 与团队质量红线对齐
- [ ] 自动修复策略覆盖了可修复门禁类型
- [ ] devkit-doctor 的 CheckResult 格式与 loop-verification 报告兼容
- [ ] 手动门禁（ADR、文档）有明确的人工介入指引
