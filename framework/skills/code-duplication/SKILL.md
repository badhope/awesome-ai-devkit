---
name: code-duplication
description: 代码重复检测。发现 copy-paste 代码，推动抽象为复用函数。补齐 agent 平台缺乏的结构化代码质量分析能力。
layer: quality
tags: [code-quality, duplication, refactoring, similarity]
---

# Code Duplication — 代码重复检测

## 触发条件

代码重构前扫描，或 CI 中定期运行。

## 核心模式

### 1. 检测维度

```
结构重复: 相同逻辑不同变量名
语法重复: > 5 行几乎一致的代码块
模式重复: 同一 try-catch 模式出现在 3+ 处
配置重复: 相同硬编码值（magic number/string）
```

### 2. 检测规则

```python
# 检测阈值
MIN_BLOCK_SIZE = 5       # 至少 5 行才算重复
SIMILARITY_THRESHOLD = 0.85  # 85% 相似才算重复
MIN_OCCURRENCES = 2      # 至少出现 2 次
```

### 3. 输出格式

```
Duplication Report:
==================

[CRITICAL] 12 lines duplicated across 3 files
  src/api/users.py:45-56
  src/api/orders.py:78-89
  src/api/products.py:112-123
  → 建议: 提取为 paginate_query() 工具函数

[HIGH] Magic number "86400" found 5 times
  src/middleware/cache.py:12
  src/middleware/rate_limit.py:34
  src/auth/jwt.py:67
  src/sessions/manager.py:23
  src/api/health.py:8
  → 建议: 定义为常量 SECONDS_PER_DAY

[MEDIUM] try-catch-log pattern repeated 4 times
  src/services/*.py (files: 4)
  → 建议: 提取为 @handle_errors decorator

Score: 74/100
  Duplicated lines: 89 / 3,200 total (2.8%)
  Target: < 2%
```

### 4. 与 Scaffold 集成

```yaml
steps:
  - goal: "重构认证模块"
    pre_check:
      - duplication_scan:
          threshold: 0.85
          fail_if_score_below: 70
    quality_gate: "代码重复率 < 2%"
```

## 推荐 SubAgent

- architect-system-designer（设计抽象方案）
- backend-api-developer（执行提取重构）
