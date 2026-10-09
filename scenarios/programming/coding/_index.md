---
name: coding
description: 通用多语言编程开发场景（自适应全能底座）。通过「auto-detect 识别 → team-composer 组队 → scaffold-generator 生成 → 执行」自动适配任意技术栈与项目类型（前端/后端/全栈/CLI/库/算法）。可直接用于独立编码任务，也可被 fullstack/mobile/ml-native 等子场景继承。
lifecycle_stage: active
target_users: [程序员, 技术负责人, 开源维护者]
scenarios: [programming/coding]
---

# 通用编程开发 — AI 编码场景

> **定位**：这是一个**跨语言、跨项目类型的自适应全能开发底座**。它不做前后端/移动/AI 等特定方向的硬编码编排（那些是 `fullstack`、`mobile`、`ml-native` 等子场景的具体化），而是让开发能力**自动适配**任何项目——不管你是写前端、后端、全栈、CLI、库还是算法，它都能自己判断该用什么角色、技能、脚手架。
>
> **核心机制**：`识别 → 组队 → 生成 → 执行` 自适应引擎。拿到任务先自动扫项目确定技术栈/类型，再自动组建合适团队并生成适配的脚手架，最后执行。

## 快速开始

**默认入口：自适应开发**（推荐——任何技术栈都能自动适配）

```bash
# 1. 把本场景复制到你的项目根
cp -r scenarios/programming/coding ./devkit-coding

# 2. 让 coding-agent 自适应执行（识别→组队→生成→执行）
python3 scenarios/programming/coding/lib/stack-detector.py --project . --json   # 先看识别结果
python3 scaffolds/scaffold-runner.py --root . --provider opencode               # 用默认自适应脚手架

# 3. 或显式指定技术栈（可选，让 scaffold-runner 的产物/门禁更精准）
python3 scaffolds/scaffold-runner.py --root . --provider opencode --stack react
```

**手动选用脚手架**（按需）：

```bash
cp devkit-coding/scaffolds/feature-development.yaml ./scaffold.yaml
bash hooks/scripts/pre-task.sh scaffold.yaml
# ... Agent 依序执行 ...
bash hooks/scripts/post-task.sh scaffold.yaml
```

> **默认自适应脚手架**：`scaffolds/adaptive-feature.yaml` 会根据识别到的技术栈，自动调整产物路径（`.tsx`/`.py`/`.go`）与质量门禁（vitest/pytest/go test/cargo test）。

## 场景结构

```
coding/
├── _index.md              # 本文件
├── agents/                # coding-agent（自动编排者）
├── skills/                # 3 个编排技能：auto-detect / team-composer / scaffold-generator
├── lib/                   # stack-detector.py（技术栈识别器，可执行）
├── scaffolds/             # 通用脚手架（功能开发/重构/故障响应）+ 静态模板
├── workflows/             # coding-lifecycle 工作流
├── mcp/                   # 通用编程 MCP 配置
├── context/               # 项目上下文模板
└── examples/              # 已完成项目案例
```

## 与框架层的关系（不重复造轮）

| 能力 | 来源 | 说明 |
|------|------|------|
| 技能 | `framework/skills/`（37 个） | 规划、重构、调试、审查、安全、Git、测试等全部通用技能 |
| 角色 | `framework/agents/`（11 个） | 架构师、后端、前端、QA、安全、DevOps 等开发团队角色 |
| 规则 | `rules/`（顶层权威） | 编码规范、安全检查、协作规范 |
| MCP | `framework/mcp/` | 通用 MCP 全集 |
| 机制 | `hooks/`（顶层） | enforce_active 门禁、生命周期钩子 |

本场景补充的是**自适应编排层**：auto-detect（识别）、team-composer（组队）、scaffold-generator（生成脚手架）、stack-detector（识别器）。

## 自适应编排主流程

> 任何编码任务，coding-agent 自动按此推进（详见 `workflows/coding-lifecycle.md`）：

```
① auto-detect 识别   → {{tech_stack}} / {{project_type}} / {{test_framework}} / {{role_set}}
② team-composer 组队 → 按类型自动选角色（复用 framework 11 角色）
③ scaffold-generator → 动态生成适配技术栈的 scaffold.yaml
④ 执行              → 需求→方案→编码→测试→审查→提交
```

### 项目类型 → 团队 → 门禁（自适应映射）

| 项目类型 | 自动组建团队 | 质量门禁 |
|---------|------------|---------|
| frontend | frontend + design-system + QA | `npm run build` 无错误 |
| backend | backend + database + QA + security | `pytest` / `go test` 全通过 |
| fullstack | architect + frontend + backend + QA + review + security | 前后端联调 + E2E |
| cli / library | backend + code-reviewer | 全量测试 + lint |

## 推荐角色组合

- **极简（1 人）**：`coding-agent`（自动编排，兼实现与审查）
- **标准（2-3 人）**：按 auto-detect 结果自动组团队
- **完整（3+ 人）**：上表 + `security-review-engineer` + `devops-deploy-engineer`

> 角色均来自框架层 `framework/agents/`，本场景不重复定义。`coding-agent` 负责自动编排。

## 场景脚手架

| 脚手架 | 适用场景 | 步骤数 |
|--------|---------|--------|
| `scaffolds/feature-development.yaml` | 通用功能开发（需求→提交） | 6 |
| `scaffolds/refactoring.yaml` | 通用代码重构 | 6 |
| `scaffolds/incident-response.yaml` | 通用故障响应 | 5 |
| `scaffold-generator` 动态生成 | 按技术栈量身定制（推荐） | 随项目 |

## 与其它子场景的关系

- **coding**（本场景）是自适应底座，`fullstack`/`mobile`/`ml-native`/`cli-tool`/`library` 都是它的**具体化**。
- 做特定类型项目时，可用对应子场景，也可直接用 coding 的自适应识别（会识别为对应类型并自动组队）。
- coding 的识别结果即 fullstack 等场景的"正确入口"判断依据。

## 维护策略

1. **新增通用技能** → 放 `framework/skills/`，本场景自动继承
2. **新增场景专属技能** → 放 `skills/<name>/SKILL.md`（frontmatter `name` == 目录名）
3. **新增识别规则** → 扩展 `lib/stack-detector.py`（新增指纹/类型判定）
4. **新增脚手架** → 在 `scaffolds/` 加 yaml 或用 scaffold-generator 动态生成
5. **角色裁剪建议** → 编辑 team-composer 的映射表

---

遵循 Awesome AI DevKit 框架分层架构，对标 2026.10 行业最佳实践（Codex / Claude Code / Qoder / opencode）。

> AI生成