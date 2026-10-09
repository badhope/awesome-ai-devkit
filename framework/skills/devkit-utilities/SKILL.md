---
name: devkit-utilities
description: Awesome AI DevKit 内置工具集。提供环境检查、数据库迁移、Token 用量追踪、分页、测试工厂、快照测试等跨项目通用能力。所有脚本自包含，agent 可直接调用无需安装。
layer: utilities
tags: [utilities, scripts, database, testing, monitoring]
---

# DevKit Utilities — 内置高频通用工具

## 触发条件

当项目需要以下能力时，agent 直接调用对应脚本（无需安装）：

| 能力 | 脚本 | 典型用法 |
|------|------|---------|
| 环境检查 | `framework/lib/scripts/core/env-check.sh` | 开工前验证 .env 完整性 |
| Token 追踪 | `framework/lib/scripts/core/token-tracker.py` | 记录 LLM 用量、计算成本 |
| 错误码查询 | `framework/lib/scripts/core/error-code.sh` | 统一 API 错误码 |
| 数据库迁移 | `framework/lib/scripts/data/migrate.sh` | 运行/回滚/创建迁移 |
| 分页参数 | `framework/lib/scripts/data/paginate.py` | Offset/Cursor 分页计算 |
| 测试数据生成 | `framework/lib/scripts/data/seed.py` | 生成假数据 SQL/JSON/CSV |
| 错误响应格式 | `framework/lib/scripts/api/error-format.py` | 标准化 API 错误响应 |
| 速率限制 | `framework/lib/scripts/api/rate-limit.sh` | Redis 限流检查 |
| 测试对象工厂 | `framework/lib/scripts/test/factory.py` | 快速构造测试对象 |
| 快照测试 | `framework/lib/scripts/test/snapshot.sh` | 输出快照对比 |

## 使用规则

```bash
# Core
bash framework/lib/scripts/core/env-check.sh --required DATABASE_URL,API_KEY
python3 framework/lib/scripts/core/token-tracker.py log --provider anthropic --model claude-sonnet-4-20250514 --input 1500 --output 800
python3 framework/lib/scripts/core/token-tracker.py report
python3 framework/lib/scripts/core/token-tracker.py budget --max 5.00
bash framework/lib/scripts/core/error-code.sh E1001

# Data
bash framework/lib/scripts/data/migrate.sh create add_users_table
bash framework/lib/scripts/data/migrate.sh up
bash framework/lib/scripts/data/migrate.sh status
python3 framework/lib/scripts/data/paginate.py offset --page 3 --per-page 20
python3 framework/lib/scripts/data/paginate.py meta --total 500 --page 3 --per-page 20
python3 framework/lib/scripts/data/seed.py users 100
python3 framework/lib/scripts/data/seed.py products 50 --csv

# API
python3 framework/lib/scripts/api/error-format.py --code E1002 --detail "User not found"
python3 framework/lib/scripts/api/error-format.py --list
bash framework/lib/scripts/api/rate-limit.sh "user:123" --window 60 --max 100

# Test
python3 framework/lib/scripts/test/factory.py user
python3 framework/lib/scripts/test/factory.py product --count 5
python3 framework/lib/scripts/test/factory.py order --fk user_id=5
bash framework/lib/scripts/test/snapshot.sh list
```

## 脚本依赖

| 依赖 | 用途 | 必需 |
|------|------|------|
| python3 ≥ 3.10 | 运行 Python 脚本 | ✅ |
| bash (Git Bash on Win) | 运行 Shell 脚本 | ✅ |
| psql | 数据库迁移（可选） | ❌ |
| redis-cli | 速率限制（可选） | ❌ |

## Checklist

- [ ] 开工前 `env-check.sh` 通过
- [ ] 迁移文件按时间戳命名（YYYYMMDDHHMMSS_name.sql）
- [ ] Token 用量日志写入 `logs/token-usage/`
- [ ] API 错误响应使用标准错误码 (E1xxx-E4xxx)
- [ ] 测试数据包含 id、created_at 等审计字段
