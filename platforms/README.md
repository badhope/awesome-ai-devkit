# Platforms — 平台自省与能力矩阵

> **根本原则：不重复造轮子。**
> 我们的目标是：**无论从哪个平台、哪个空白项目开始，把该平台的 Agent 能力从空白自动拉到最大。**
> 为此，**平台已内置的能力直接复用，绝不重复造；只有在"平台本身没有"时才由我们补充。** 避免重复、避免冲突。

## 通用能力只用一个开放载体

通用能力层用**开放标准**承载，维护一份、处处生效（不因平台而各写各的）：

| 能力 | 开放载体 | 说明 |
|------|------|------|
| 统一指令/规则 | **`AGENTS.md`**（仓库根） | 跨工具标准，主流平台原生读取 |
| 技能 Skills | **`SKILL.md`**（`agentskills.io` 开放格式） | 按需加载的专业能力包 |
| 工具连接 | **`MCP`**（Model Context Protocol） | 开放标准，主流平台全支持 |

平台已内置的机制（Skill 加载、Subagents/多 Agent 协作、Rules、Hooks、MCP 客户端、命令/插件）——**全部复用平台原生能力**，我们不重复实现。

## 平台能力矩阵（内置→复用；缺→我们补）

| 平台 | 平台原生内置（我们复用） | 我们需补 | 官方入口 |
|------|------|:---:|------|
| Claude Code | CLAUDE.md / Skills / Subagents / Agent Teams / MCP / Hooks / Plugins | 仅组织场景内容 | `claude-code/CLAUDE.md` |
| Cursor | Rules / Skills / MCP / Agent / CLI / hooks | 仅组织场景内容 | `cursor/examples/*.mdc` |
| OpenAI Codex | AGENTS.md / MCP / Skills | 复用根 AGENTS.md | （根 AGENTS.md） |
| Gemini CLI | GEMINI.md / AGENTS.md / MCP | 仅入口 | `gemini-cli/GEMINI.md` |
| GitHub Copilot | copilot-instructions / AGENTS.md / MCP / Skills | 仅入口 | `github-copilot/copilot-instructions.md` |
| Cline | CLAUDE.md 兼容 / MCP | 复用 | — |
| Windsurf | `.windsurf/rules` / AGENTS.md | 复用 | — |
| 通义灵码 | MCP / 指令 / 技能 | 复用 | — |
| 豆包 MarsCode | MCP / 技能 | 复用 | — |
| Kimi for Coding | AGENTS.md / MCP | 复用 | — |
| Trae | MCP / 规则 | 复用 | — |
| 百度 Comate | MCP / 指令 | 复用 | — |
| 智谱 CodeGeeX | AGENTS 兼容 / MCP | 复用 | — |
| Zed / Continue / Aider / JetBrains | 各自官方支持 AGENTS.md + MCP | 复用 | — |

> 结论：主流平台**都已内置** AGENTS.md + Skills + MCP 三件套。绝大多数情况下我们**只需**让平台读取根 `AGENTS.md` 与 `SKILL.md` 即可，**无需为平台专门造配置**。个别平台因官方入口文件不同（CLAUDE.md / GEMINI.md / copilot-instructions.md）才保留对应入口文件。

## 自省机制（让 Agent 知道自己该用什么）

`AGENTS.md` 内置**平台自省声明**，Agent 读取时按以下逻辑工作：

```
1. 识别当前平台（读取本仓库 AGENTS.md / 平台入口文件）
2. 用平台原生机制加载：Rules / Skills(SKILL.md) / MCP
3. 平台已有的（多 Agent、Subagents、Hook、命令）→ 用平台原生的，不重复
4. 平台没有的（某个领域场景、专家团队提示词）→ 才加载 platforms/scenarios 内容
5. 全程遵循根 AGENTS.md 的规则，不自造协议、不与平台冲突
```

## 目录约定（只保留"官方必需"入口文件）

```
platforms/
├── README.md                       # 本文件：平台能力矩阵 + 自省机制
├── claude-code/CLAUDE.md           # Claude Code 官方入口（内容指向根 AGENTS.md）
├── gemini-cli/GEMINI.md            # Gemini CLI 官方入口
├── github-copilot/copilot-instructions.md  # Copilot 官方入口
└── cursor/examples/*.mdc           # Cursor Rules 官方格式示例
```

## 强制机制（按平台接入）

**核心问题**：提示词只靠模型"自觉"，会不主动/不听话。因此把关键动作下沉为**机器可校验的门禁**（`hooks/scripts/enforce_active.py`，跨平台，不依赖任何特定工具）：

```
分层控制（低→高）：
L0 提示层   AGENTS.md + platform 入口        → 所有平台（兜底）
L1 机制层   hooks/scripts/enforce_active.py  → 跨平台，任何地方可跑
L2 原生钩子 各平台官方 hooks 挂载 enforce    → 能力平台（推荐）
L3 门禁     CI / quality_gate / doctor       → 最终校验，不通过即失败
```

按平台接入差异：

| 平台 | 原生 hook 能力 | 强制接入方式 |
|------|------|------|
| **Claude Code** | ✅ 原生 hooks（Stop/PreToolUse/SubagentStop 等） | 把 `enforce_active.py` 挂到 `Stop`/`PostToolUse` hook |
| **Cursor** | ✅ 支持 hooks / rules | rules 强制调用；或挂到 hooks |
| **OpenAI Codex** | ⚠️ 有限 | AGENTS.md 强制 + 手动/脚本调用 |
| **Gemini CLI** | ⚠️ 有限 | AGENTS.md 强制 + 手动 |
| **Copilot / Cline / 国产工具** | ⚠️ 差异较大 | AGENTS.md 强制 + 脚本/CI |
| **CI（GitHub Actions）** | ✅ 通用 | 把 `enforce_active.py` 作为 job 步骤（平台无关最强门禁） |

> 结论：**`enforce_active.py` 是平台无关的"最底层强制"**；平台若有原生 hooks，就把它挂上去增强；没有，就靠 AGENTS.md 强制调用 + CI 兜底。**尽量用，不强求**。

## 参考
- `AGENTS.md`（根）— 统一指令权威（含平台自省声明 + 强制主动使用机制）
- `mcp/config/` — 各平台 MCP 配置（官方格式）
- `scenarios/<场景>/` — 领域专用内容（按需加载）

> AI生成