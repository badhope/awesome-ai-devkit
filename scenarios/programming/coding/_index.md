---
name: coding
description: 通用多语言编程开发场景。作为编程子场景的通用底座，覆盖「规划→编码→测试→重构→提交」全流程，跨语言、跨项目类型复用。可直接用于独立编码任务，也可被 fullstack/mobile/ml-native 等子场景继承。
lifecycle_stage: active
target_users: [程序员, 技术负责人, 开源维护者]
scenarios: [programming/coding]
---

# 通用编程开发 — AI 编码场景

> **定位**：这是一个**跨语言、跨项目类型**的通用编程开发底座。它不做前后端/移动/AI 等特定方向的深度编排（那些交给 `fullstack`、`mobile`、`ml-native` 等子场景），而是把「把一件事写对、测对、交付对」的最小可靠路径固化下来。
>
> **适用场景**：脚本、CLI 工具、库、算法实现、单机服务、任何"不是特定技术栈的编码任务"。也可以作为其他编程子场景继承的地基。

## 快速开始

```bash
# 1. 把本场景复制到你的项目根
cp -r scenarios/programming/coding ./devkit-coding

# 2. 选一个脚手架，作为本次开发任务的执行蓝图
cp devkit-coding/scaffolds/task-development.yaml ./scaffold.yaml

# 3. 开工 → 按 steps 执行 → 完工验收
bash hooks/scripts/pre-task.sh scaffold.yaml      # 场景/仓库根下运行
# ... Agent 按 steps[] 逐步执行 ...
bash hooks/scripts/post-task.sh scaffold.yaml
```

> 若你的项目已有 `scaffold-workflow` 脚手架运行时，可直接用 `scaffold-runner.py`：
> ```bash
> python3 scaffolds/scaffold-runner.py --scaffold scaffold.yaml --provider opencode
> ```

## 场景结构

```
coding/
├── _index.md              # 本文件
├── agents/                # 通用编程专属角色（如 tech-lead 简化版、编码执行者）
├── skills/                # 通用编程专属技能（如规范、入门引导）
├── scaffolds/             # 通用开发脚手架（功能开发、故障响应、重构）
├── workflows/             # 端到端工作流（编码 → 测试 → 提交）
├── mcp/                   # 通用编程 MCP 配置
├── context/               # 项目上下文模板
└── examples/              # 已完成项目案例
```

## 与框架层的关系（不重复造轮）

本场景是**通用底座**，绝大多数能力直接复用框架层，不重复造：

| 能力 | 来源 | 说明 |
|------|------|------|
| 技能 | `framework/skills/`（37 个） | 规划、重构、调试、代码审查、安全、Git、测试等全部通用技能 |
| 角色 | `framework/agents/`（11 个） | 架构师、后端、前端、QA、安全、DevOps 等开发团队角色 |
| 规则 | `rules/`（顶层权威） | 编码规范、安全检查、协作规范 |
| MCP | `framework/mcp/` | 通用 MCP 全集 |
| 机制 | `hooks/`（顶层） | enforce_active 门禁、生命周期钩子 |

本场景只补充**通用编程**特有的少量编排与引导内容。

## 编码开发主流程

> 任何编程任务，按此 6 步推进（详见 `workflows/coding-lifecycle.md`）：

```
1. 需求澄清   → instruction-grooming + task-tracker   → 可执行验收标准
2. 方案设计   → architecture-design + project-health  → 简短技术方案 + ADR
3. 编码实现   → 复用框架 agent（backend/frontend 等） → 代码 + 单元测试
4. 测试验证   → test-strategy + loop-verification     → 全量测试通过
5. 格式化审查 → linter-formatter + code-review + security → 无 lint/高危
6. 提交交付   → git-workflow + commit-conventions + memory-persistent → 干净提交
```

## 推荐角色组合

- **极简（1 人）**：`senior-developer`（兼架构）+ `code-reviewer`
- **标准（2-3 人）**：`architect-system-designer` + `backend-api-developer` / `frontend-ui-developer` + `test-qa-engineer`
- **完整（3+ 人）**：上表 + `security-review-engineer` + `devops-deploy-engineer`

> 角色均来自框架层 `framework/agents/`，无需在本场景重复定义。本场景仅提供裁剪与编排建议。

## 场景脚手架

| 脚手架 | 适用场景 | 步骤数 |
|--------|---------|--------|
| `scaffolds/feature-development.yaml` | 通用功能开发（需求→提交） | 6 |
| `scaffolds/refactoring.yaml` | 通用代码重构 | 6 |
| `scaffolds/incident-response.yaml` | 通用故障响应 | 5 |

## 与其它子场景的关系

- **coding**（本场景）是通用底座，`fullstack`/`mobile`/`ml-native`/`cli-tool`/`library` 都是它的**具体化**。
- 做特定类型项目时，优先选对应子场景；做通用/快速编码任务，直接用本场景。
- 更深的实现参考 `fullstack`（11 层能力全链路示例）。

## 维护策略

1. **新增通用技能** → 放 `framework/skills/`，本场景自动继承
2. **新增场景专属技能** → 放 `skills/<name>/SKILL.md`（frontmatter `name` 需等于目录名）
3. **新增脚手架** → 在 `scaffolds/` 加 yaml，遵循 Scaffold Protocol v2.0
4. **角色裁剪建议** → 编辑本文件"推荐角色组合"表

---

遵循 Awesome AI DevKit 框架分层架构，对标 2026.10 行业最佳实践（Codex / Claude Code / Qoder / opencode）。

> AI生成
