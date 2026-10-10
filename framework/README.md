# Framework — 通用能力层

> **本仓库的根本**：跨平台、从空白起步，把 Agent 能力拉到最大。
> `framework/` 承载**平台无关、跨场景复用**的通用能力；`scenarios/` 只放各领域专属内容。

## 设计原则

1. **复用平台原生能力**：Skill 加载、多 Agent、MCP、Hooks——平台已内置，我们用开放标准承载，**不重复造轮子**。
2. **通用先行、专属后补**：先在通用层把能力拉满，再按场景/平台差异做适配。
3. **开放标准**：技能用 `agentskills.io` 的 `SKILL.md`；工具连接用 `MCP`；统一指令用 `AGENTS.md`。
4. **不与平台冲突**：只补平台没有的，不自造协议。

## 目录结构

```
framework/
├── skills/      # 通用技能库（agentskills.io 标准 SKILL.md）
├── agents/      # 通用多角色团队（跨场景可复用）
├── mcp/         # 通用 MCP 配置与说明
└── rules/       # 通用规则（根 rules/ 为权威，此处说明）
```

## 通用技能库（framework/skills/，38+ 个）

| 类别 | 技能 |
|------|------|
| 编排 | instruction-grooming、scaffold-workflow、task-tracker、loop-verification、sub-agent-guard、planning |
| 上下文/记忆 | memory-management、memory-persistent、context-compression、model-routing、session-continuation |
| 质量 | code-review、debugging、test-strategy、mutation-testing、linter-formatter、project-health、refactoring |
| 安全 | security-governance、secret-scanner、dependency-audit、sub-agent-guard |
| 工程 | git-workflow、commit-conventions、semantic-release、api-design、integration-patterns |
| 文档 | documentation-writing、requirements-analysis、architecture-design |
| 基础设施 | devkit-infra、devkit-utilities、auto-heal、code-duplication、calculator-math、web-browser-vision、observability |

> 技能格式：`framework/skills/<name>/SKILL.md`（frontmatter: `name`/`description`/`layer`/`tags` + 正文）。

## 通用多角色团队（framework/agents/）

为跨场景提供标准开发团队角色（产品/架构/前端/后端/QA/安全/DevOps/SRE/DB），详见 `framework/agents/README.md`。

## 通用 MCP（framework/mcp/）

通用 MCP 全集（filesystem/git/github/postgres/redis/playwright 等）见 `framework/mcp/README.md` 与 `mcp/config/awesome-servers.json`。

## 场景如何复用通用层

任意场景只需：
1. 在 scaffold 中引用通用技能名（如 `skills: [instruction-grooming, security-governance]`）
2. 复用通用角色与 MCP
3. 只补充领域专属的 skill/agent/workflow

> `devkit-doctor.py` 会同时检查 `framework/skills`（通用）+ `scenarios/*/skills`（场景）。

## 参考
- 统一指令：根 `AGENTS.md`
- 平台适配：`platforms/`
- 场景扩展：`scenarios/README.md`
