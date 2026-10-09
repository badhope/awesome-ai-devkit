# 通用编程场景 — Skills 说明

> 本场景是**自适应编排底座**。编码相关能力绝大多数复用框架层 `framework/skills/` 的 **38 个通用技能**；同时提供 **3 个场景专属「编排」技能** + 1 个识别脚本，让开发能力自动适配任意技术栈。

## 场景专属编排技能（本目录）

| 技能 | 作用 |
|------|------|
| `auto-detect` | 自动识别技术栈/项目类型/测试框架/工具链（扫描项目配置文件） |
| `team-composer` | 按项目类型自动组建团队（复用 framework 11 角色） |
| `scaffold-generator` | 动态生成适配技术栈的 scaffold.yaml |

配套脚本：`../lib/stack-detector.py` — 可执行识别器，输出 `{tech_stack, project_type, test_framework, build_tool, role_set}` JSON。

## 自适应流程

```
任务 → auto-detect(识别) → team-composer(组队) → scaffold-generator(生成) → coding-agent(执行)
```

## 复用的框架技能（核心子集）

| 技能 | 用途 |
|------|------|
| `planning` | 任务拆解与执行计划 |
| `refactoring` | 安全重构（守护测试下） |
| `debugging` | 问题定位与修复 |
| `code-review` | 代码自审 |
| `security-governance` | 安全基线 |
| `test-strategy` | 测试策略与覆盖 |
| `linter-formatter` | lint + 格式化 |
| `git-workflow` + `commit-conventions` | 规范提交 |
| `loop-verification` | 循环验证质量门禁 |
| `memory-persistent` | 决策持久化 |

> 完整列表见 `framework/skills/`。

## 约定

- 新技能若可跨场景复用 → 放 `framework/skills/`
- 仅本场景独有且与"自适应编排"相关 → 放本目录（如 auto-detect 等）

> AI生成
