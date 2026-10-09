---
name: mutation-testing
description: 变异测试（Mutation Testing）。通过向代码注入变异体（mutation）来评估测试集的检测能力，输出变异分数（Mutation Score），揭示"高覆盖率但低效力"的测试盲区。对齐 Stryker、Mutmut、cargo-mutants 等主流框架。
layer: quality
tags: [mutation, test-quality, fault-injection, coverage]
---

# Mutation Testing — 变异测试

## 触发条件

验证测试质量时使用，覆盖率看似较高但担心测试遗漏场景时，或 CI 中作为质量门禁的进阶指标。

## 核心概念

变异测试是"测试的测试"：

```
原始代码:  if (a > b) { return a }
变异体 1:  if (a >= b) { return a }   ← 边界变异
变异体 2:  if (a < b)  { return a }   ← 条件取反
变异体 3:  if (a > b)  { return b }   ← 返回值变异

测试集若无法检测任何变异体 → 变异存活（Survived） → 测试存在盲区
```

### 变异分数

```
Mutation Score = (Killed Mutants / Total Mutants) * 100%

≥ 90%: 优秀 — 测试做到了细粒度断言
≥ 80%: 良好 — 核心逻辑被充分测试
60-79%: 一般 — 存在明显盲区，需补测试
< 60%:  较差 — 测试形同虚设
```

## 支持框架

| 语言/栈 | 框架 | 安装命令 |
|---------|------|----------|
| JavaScript/TypeScript | Stryker Mutator | `npm install --save-dev @stryker-mutator/core` |
| Python | Mutmut | `pip install mutmut` |
| Go | go-mutesting | `go install github.com/devdot/go-mutesting@latest` |
| Rust | cargo-mutants | `cargo install cargo-mutants` |

## 配置示例

### Stryker (JS/TS)

```json
// stryker.conf.json
{
  "$schema": "./node_modules/@stryker-mutator/core/schema/stryker-schema.json",
  "packageManager": "npm",
  "reporters": ["html", "clear-text", "progress"],
  "mutate": ["src/**/*.ts", "!src/**/*.spec.ts", "!src/**/__tests__/**"],
  "testRunner": "jest",
  "coverageAnalysis": "perTest",
  "thresholds": {
    "high": 85,
    "low": 70,
    "break": 60
  }
}
```

```bash
# 运行
npx stryker run

# 输出示例
# [2026-01-15 10:30:45] Mutation score: 87.3% (131/150)
#   ✓ Killed:     114
#   ✗ Survived:    19
#   ⏱ Timeout:     12
#   ⊘ Compile Error: 5
```

### Mutmut (Python)

```toml
# pyproject.toml
[tool.mutmut]
paths_to_mutate = "src/"
runner = "python -m pytest tests/ -x -q"
tests_dir = "tests/"
```

```bash
# 运行
mutmut run

# 查看结果
mutmut results

# 输出示例
# mutant                         | status
# ----                           | ------
# src/calc.py line 12: > → >=    | survived
# src/calc.py line 18: + → -     | killed
# src/calc.py line 24: return → None | killed
# ...
# Mutation score: 82.5% (66/80)
```

### go-mutesting (Go)

```bash
# 运行（无需配置文件）
go-mutesting ./...

# 输出示例
# /src/calc/max.go:12:13: ... mutated by > → >=
# /src/calc/max.go:12:13: ... killed
# /src/calc/max.go:18:8:  ... mutated by a → a+1
# /src/calc/max.go:18:8:  ... survived
#
# Mutation score: 78.9% (15/19)
```

### cargo-mutants (Rust)

```bash
# 运行
cargo mutants

# 输出示例
#   src/lib.rs:12: mutated `>` to `>=` ... CAUGHT
#   src/lib.rs:18: mutated `+` to `-` ... CAUGHT
#   src/lib.rs:24: removed early escape ... MISSED
#
# Mutation score: 91.2% (31/34)
#   Caught:  31
#   Missed:  3
#   Timeout: 0
```

## 输出解读

```
┌─────────────────────────────────────────────────────────┐
│ Mutation Test Report                                    │
├─────────────────────────────────────────────────────────┤
│ Score: 87.3% (Good)                                     │
│                                                         │
│ Killed (已杀):      114  ✓ 测试成功捕捉变异            │
│ Survived (存活):    19   ✗ 测试未察觉变异 ← 需补测试   │
│ Timeout (超时):     12   ⏱ 变异导致无限循环           │
│ Compile Error (编译): 5   ⊘ 变异体不合法（不计入）     │
│                                                         │
│ Survived 详情:                                          │
│   src/auth/jwt.ts:45  → 替换 expired 检查              │
│     → 建议: 添加过期断言 expect(token).toBeExpired()    │
│   src/api/ratelimit.ts:88 → 移除限流计数               │
│     → 建议: 验证计数是否实际递增                        │
└─────────────────────────────────────────────────────────┘
```

## 变异类型速查

| 类型 | 示例 | 检测重点 |
|------|------|---------|
| 边界变异 | `>` → `>=`, `<` → `<=` | 边界条件断言 |
| 算术变异 | `+` → `-`, `*` → `/` | 计算结果断言 |
| 条件取反 | `if (a)` → `if (!a)` | 分支覆盖完整性 |
| 返回值变异 | `return x` → `return null` | 返回值非空断言 |
| 常量替换 | `0` → `1`, `""` → `"x"` | 默认值处理 |
| 语句删除 | 移除函数体 | 副作用断言 |

## 与 Scaffold 集成

### 作为 Quality Gate

```yaml
steps:
  - goal: "集成测试"
    description: "变异测试验证测试质量，分数 ≥ 80 作为门禁"
    skills: [mutation-testing]
    outputs:
      - reports/mutation/<scope>.html
    quality_gate: "变异分数 ≥ 80%（Killed / (Total - Ignored)）"
```

### 最低配置（嵌入 scaffold 步骤）

```yaml
  - goal: "集成测试 + QA 验收"
    skills: [mutation-testing, project-health]
    quality_gate: |
      - 所有测试通过
      - 代码覆盖率 ≥ 60%
      - 变异分数 ≥ 80%（核心业务模块）
```

### 分数目标建议

```yaml
post_task:
  quality_gates:
    - "全量测试通过: 所有 pass"
    - "覆盖率 ≥ 60%（核心业务模块）"
    - "变异分数 ≥ 80%（src/core/ 模块; Stryker/Mutmut 输出 break 阈值 70）"
```

## 最佳实践

1. 先跑基础覆盖率：确保行覆盖率 ≥ 60% 再做变异测试（避免大量"未覆盖"变异体干扰结果）
2. 聚焦核心模块：`src/core/`、`src/auth/`、`src/payment/` 是高价值目标
3. 渐进式提升：先设 break 阈值 60，稳定后提升至 80
4. 排除非核心变异：配置文件、日志函数、纯 getter/setter 可标记为 `ignored`
5. CI 中增量运行：仅对 diff 文件做变异测试，节省时间

## Checklist

- [ ] 项目已有基础测试（覆盖率 ≥ 60%）
- [ ] 已选框架并安装对应工具
- [ ] 配置 `mutate` 路径排除测试文件和生成产物
- [ ] 设置 `break` 阈值（CI 失败下限）
- [ ] 核心模块变异分数 ≥ 80%
- [ ] Survived 变异体已逐个审查（非全部忽略）

## 推荐 SubAgent

- test-qa-engineer（补充 Survived 变异体对应的测试）
- backend-api-developer（修复测试无法捕获的变异）
- frontend-ui-frontend（组件变异测试集成）
