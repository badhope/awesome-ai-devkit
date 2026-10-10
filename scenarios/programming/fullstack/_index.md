---
name: Web 全栈开发
description: Awesome AI DevKit 全栈开发场景。包含 11 层能力体系，覆盖产品/架构/开发/质量/运维/辅助全链路。
lifecycle_stage: active
scenarios: [programming/fullstack]
---

# 全栈开发 — AI 编程场景

> **直接使用**：复制此场景到你的项目，即可获得完整的 AI 全栈开发能力。
>
> **核心理念**：角色/技能/工具数量为推荐值，按需增减。大项目全覆盖，小项目只选核心。

## 快速开始

1. 复制 `context/project.template.yaml` 为 `context/project.yaml`，填入你的项目信息
2. 选择适合你的角色组合（推荐全部 11 个 agent 角色）
3. 启动开发流水线（见 [workflows/sdlc/feature-development.md](workflows/sdlc/feature-development.md)）
4. 运行健康检查 `python3 ../../devkit-doctor.py`（或项目自带校验命令）

## 场景结构

```
fullstack/
├── _index.md              # 本文件
├── agents/                # 11 个 AI 角色（系统架构师、后端、前端、QA、DevOps 等）
├── skills/                # 19 个可复用技能模块
├── mcp/                   # MCP 服务器配置（8 个核心服务已启用）
├── scaffolds/             # 3 个脚手架模板（功能开发、故障响应、重构）
├── workflows/             # 6 个端到端工作流 + README
├── hooks/                 # 生命周期钩子 + 中间件 + 脚本
├── context/               # 项目上下文模板
└── lib/                   # 共享工具脚本（API、数据库、基础设施、测试）
```

## 外部依赖

`rules/` 和 `experts/` 目录位于仓库顶层（不在 `fullstack/` 内）：

```
awesome-ai-devkit/
├── rules/                  # Layer 1 — 编码规范 / 安全检查 / 协作规范
│   ├── coding-standards.md
│   ├── collaboration-rules.md
│   └── security-checklist.md
├── experts/                # Expert 插件定义（跨层打包）
│   ├── fullstack-expert.md
│   └── fullstack-expert.plugin.json
└── scenarios/programming/fullstack/   # 当前场景
```

使用时注意：

- 复制 `fullstack/` 用于项目时，需**同时复制**顶层 `rules/` 和 `experts/` 目录
- 或在 fullstack 内部通过相对路径引用：`../../rules/` 和 `../../experts/`

## 11 层能力映射

| 层 | 全栈场景实现 |
|----|------------|
| Layer 1 Rules | 引用自框架顶层 `rules/`（编码规范 / 安全检查 / 协作规范） |
| Layer 2 Prompts | 11 个 Agent 角色自带 system prompt（见 `agents/`） |
| Layer 3 Tools | Agent 内置工具集（`read_file`, `write`, `bash`, `web_search` 等） |
| Layer 4 MCP | MCP 服务器配置（[mcp/mcp-config.yaml](mcp/mcp-config.yaml)，8 个核心服务已启用） |
| Layer 5 Skills | 19 个可复用技能模块（见 `skills/`） |
| Layer 6 Agents | 11 个 Agent 角色（见 `agents/`） |
| Layer 7 Expert | [experts/fullstack-expert.md](../../experts/fullstack-expert.md) 统一编排 |
| Layer 8 Workflow | 6 个工作流（见 `workflows/`，含 SDLC/故障/入职） |
| Layer 9 Hooks | 生命周期钩子 + 中间件链（见 `hooks/`） |
| Layer 10 Context | 项目上下文 + 会话状态 + ADR（见 `context/`） |
| Layer 11 Validation | Schema 校验 + 自动化检查（[devkit-doctor.py](../../devkit-doctor.py)） |

## Scaffold 协议集成

本场景接入 Scaffold Protocol v2.0。Agent 接到开发任务时，按以下流程执行：

```bash
# 1. 复制场景特定的脚手架模板
cp scaffolds/<template>.yaml ./scaffold.yaml

# 2. 编辑步骤 + 角色 + 技能引用
vim scaffold.yaml

# 3. 开工校验 → Agent 按 steps[] 执行 → 完工验收
bash hooks/scripts/pre-task.sh scaffold.yaml
# ... Agent 按步骤执行 ...
bash hooks/scripts/post-task.sh scaffold.yaml
```

### 场景特定脚手架

| 脚手架 | 适用场景 | 步骤数 | 引用 Skills |
|--------|---------|--------|------------|
| `scaffolds/feature-development.yaml` | 端到端功能开发 | 6 | 12 |
| `scaffolds/incident-response.yaml` | 故障响应 | 5 | 10 |
| `scaffolds/refactoring.yaml` | 代码重构 | 6 | 10 |

> 场景脚手架中的 skill 引用复用通用层 `framework/skills/` 中的 38 个通用技能。

---

场景文件虽多，但启动时**并非全量加载**。按团队规模选择：

| 规模 | 推荐组合 |
|------|---------|
| 小团队（1-3 人） | `agents/` 核心角色 + `skills/` 基础技能 + `workflows/sdlc/feature-development.md` |
| 中型（4-8 人） | 上述 + `hooks/` + 全部 `skills/` + `context/` |
| 大型（9-15 人） | 上述 + 全部 `mcp/` 服务 + `workflows/` 全套 |
| 企业级（16+ 人） | 全部目录 + `scaffolds/` 全套 + 自定义扩展 |

## 关键约定

| 约定 | 位置 |
|------|------|
| 工具调用通过 Middleware 链鉴权/限流/缓存 | [hooks/config.yaml](hooks/config.yaml) |
| Agent 权限通过 `allowed_scopes` 控制 | [context/project.template.yaml](context/project.template.yaml) |
| 会话可续传 — 通过 `logs/sessions/*.jsonl` | [context/README.md](context/README.md) |
| 架构决策以 ADR 形式持久化 | [context/architecture.md](context/architecture.md) |
| Git 提交前执行自动检查 | [hooks/config.yaml](hooks.config.yaml) `agent_lifecycle` |

## 维护策略

1. **新增 Skill** → 在 `skills/<name>/SKILL.md` 写 YAML frontmatter + 正文
2. **新增 MCP 服务** → 在 `mcp/mcp-config.yaml` 添加 server 条目
3. **调整 Hooks** → 修改 [hooks/config.yaml](hooks/config.yaml)，无需改代码
4. **升级 ADR** → 在 [context/architecture.md](context/architecture.md) 追加段落，标记 `proposed → accepted`
5. **变更角色** → 编辑 `agents/` 目录中对应角色的 .md 文件

## 致谢

遵循 Awesome AI DevKit 框架 11 层架构，对标 2026.10 行业最佳实践（Codex / Claude Code / Qoder）。
