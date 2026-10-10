# 通用编程场景 — Scaffold 脚手架库

> 跨语言、跨技术栈的**通用编程脚手架**。所有 skill 引用均来自通用层 `framework/skills/`（38 个通用技能）。

## 使用方式

```bash
# 1. 选择脚手架
cp scenarios/programming/coding/scaffolds/<name>.yaml ./scaffold.yaml

# 2. 按需微调步骤
vim scaffold.yaml

# 3. 开工 → 执行 → 完工
bash hooks/scripts/pre-task.sh scaffold.yaml
# ... Agent 按 steps[] 执行 ...
bash hooks/scripts/post-task.sh scaffold.yaml
```

## 脚手架清单

| 文件 | 适用场景 | 步骤数 | 引用 Skills |
|------|---------|--------|-----------|
| `feature-development.yaml` | 通用功能开发（需求→提交） | 6 | 通用层 |
| `refactoring.yaml` | 通用代码重构 | 6 | 通用层 |
| `incident-response.yaml` | 通用故障响应 | 5 | 通用层 |

## 与 fullstack 脚手架的关系

- **本场景**：通用底座，语言无关，适合脚本/CLI/库/算法等通用任务
- **fullstack**：全栈端到端（含部署/数据库/前端），适合特定 Web 技术栈项目
- 两者均复用 `framework/skills/` 38 个通用技能，不重复定义
