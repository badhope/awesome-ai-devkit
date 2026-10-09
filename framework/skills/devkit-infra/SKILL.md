---
name: devkit-infra
description: 项目基础设施检查工具集。密钥扫描、README 完整性、gitignore 检查、统一测试运行器。适用于所有项目的通用守护。
layer: infrastructure
tags: [infrastructure, security, readme, gitignore, test-runner]
---

# DevKit Infra — 项目基础设施守护

## 工具清单

| 工具 | 用法 | 说明 |
|------|------|------|
| `secret-scanner.sh` | `bash framework/lib/scripts/infra/secret-scanner.sh` | 扫描硬编码密钥 |
| `readme-check.sh` | `bash framework/lib/scripts/infra/readme-check.sh` | 检查 README 完整性 |
| `gitignore-check.sh` | `bash framework/lib/scripts/infra/gitignore-check.sh` | 验证 .gitignore 覆盖 |
| `test-runner.py` | `python3 framework/lib/scripts/test/test-runner.py` | 统一测试入口 |

## 使用场景

```bash
# 开工前检查
bash framework/lib/scripts/infra/secret-scanner.sh     # 无密钥泄露
bash framework/lib/scripts/infra/readme-check.sh      # README 完整
bash framework/lib/scripts/infra/gitignore-check.sh   # .gitignore 覆盖

# 测试
python3 framework/lib/scripts/test/test-runner.py       # 自动检测框架
python3 framework/lib/scripts/test/test-runner.py path  # 指定路径
python3 framework/lib/scripts/test/test-runner.py --watch  # 监视模式
```

## 集成到 scaffold

```yaml
post_task:
  infra_checks:
    - secret-scanner - 无硬编码密钥
    - readme-check - 文档完整
    - gitignore-check - .gitignore 覆盖
```
