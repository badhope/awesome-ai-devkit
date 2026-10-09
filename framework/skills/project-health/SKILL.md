---
name: project-health
description: 项目健康度综合检查。一键扫描依赖新鲜度、测试覆盖、文档完整度、安全漏洞、代码质量，输出可读的健康报告。对齐 Qoder、Aider 的 repo 健康评估。
layer: quality
tags: [health, audit, dependencies, coverage, security, quality]
---

# Project Health — 项目健康度综合检查

## 触发条件

开工前评估项目状态，或 CI 中定期运行。

## 核心模式

### 1. 检查维度

| 维度 | 工具 | 指标 |
|------|------|------|
| 依赖新鲜度 | npm/pip list outdated | 过期依赖数量 |
| 测试覆盖 | coverage report | 覆盖率 % |
| 安全漏洞 | npm audit / pip audit / OWASP check | HIGH/CRITICAL 数量 |
| 文档完整 | README + docs/ 检查 | 是否覆盖关键模块 |
| 代码质量 | ESLint/Ruff warning 数 | warning/error 数量 |
| Git 健康 | 分支状态、stale branches | 未合并分支数 |
| 技术债 | TODO/FIXME/HACK 注释 | 数量趋势 |
| CI 健康 | GitHub Actions / CI 状态 | 通过率 |

### 2. 输出格式

```
==========================================
 Project Health: <project-name>
 2026-10-06 10:00 UTC | Branch: main
==========================================

 Overall Score: 82/100  [B+]

 Dependencies    [A]  142/145 up to date (3 outdated)
 Test Coverage   [B+] 78% lines covered
 Security        [A-] 0 critical, 2 high
 Documentation   [B]  12/15 modules documented
 Code Quality    [B+] 5 warnings, 0 errors
 Git Health      [A]  2 branches, 0 stale
 Technical Debt  [C+] 47 TODO/FIXME found
 CI Status       [A]  100% pass (12/12)

 Top 3 Actions:
  1. Update lodash 4.17.20 → 4.17.21 (security)
  2. Add tests for auth module (coverage +12%)
  3. Refactor src/utils/parser.py (high complexity)

==========================================
```

### 3. Score 算法

```
Overall = (
  Dependency * 0.15 +
  Coverage * 0.20 +
  Security * 0.25 +
  Documentation * 0.10 +
  CodeQuality * 0.15 +
  Git * 0.05 +
  CI * 0.10
)

A: 90-100  B+: 80-89  B: 70-79  C+: 60-69  C: 50-59  D: <50
```

## 推荐 SubAgent

- devops-deploy-engineer（CI 状态检查）
- security-review-engineer（安全维度）
- test-qa-engineer（覆盖维度）
