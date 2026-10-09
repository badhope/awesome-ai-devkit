# 通用编程场景 — Skills 说明

> 本场景是**通用底座**，编码相关能力绝大多数直接复用框架层 `framework/skills/` 的 **37 个通用技能**，不重复造轮。

## 复用的框架技能（核心子集）

| 技能 | 用途 |
|------|------|
| `planning` | 任务拆解与执行计划 |
| `refactoring` | 安全重构（守护测试下） |
| `debugging` | 问题定位与修复 |
| `code-review` | 代码自审 |
| `security-governance` | 安全基线（密钥/注入/越权） |
| `test-strategy` | 测试策略与覆盖 |
| `linter-formatter` | lint + 格式化 |
| `git-workflow` + `commit-conventions` | 规范提交 |
| `loop-verification` | 循环验证质量门禁 |
| `memory-persistent` | 决策持久化 |

> 完整列表见 `framework/skills/`。按任务在 scaffold 的 `skills:` 字段引用即可。

## 场景专属技能

本场景当前**不需要**额外技能——所有通用编程能力已在框架层覆盖。若未来需要补充"通用编程专属"能力（如语言无关的入门引导、脚手架编写规范），在此目录按 `SKILL.md`（frontmatter `name` == 目录名）添加。

## 约定

- 新技能若可跨场景复用 → 放 `framework/skills/`
- 仅本场景独有且通用编程特有 → 放本目录

> AI生成
