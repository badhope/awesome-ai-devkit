# Platform × Protocol 支持文档

> Awesome AI DevKit 的跨平台接入规范。原则：**统一 AGENTS.md + 官方 MCP + 各平台官方配置格式**，不自造协议。

## 一、统一协议（官方标准）

### 1. AGENTS.md — 跨工具统一指令
`AGENTS.md` 已被主流 AI 编码工具**官方采用**作为项目级指令标准：

- **Claude Code**：2.1.277+ 支持根 `AGENTS.md`
- **OpenAI Codex**：官方采用 `AGENTS.md`
- **Cursor**：支持 `AGENTS.md`（同时兼容 `.cursor/rules` 与 `.cursorrules`）
- **Gemini CLI**：支持 `AGENTS.md`（另有 `GEMINI.md`）
- **GitHub Copilot**：支持 `AGENTS.md`（另有 `.github/copilot-instructions.md`）
- **Cline / Windsurf / Continue 等**：兼容 AGENTS.md

> 意义：一套指令，多处生效，终结 `.cursorrules` / `CLAUDE.md` / `AGENT.md` 各自为政的碎片化。

### 2. MCP — 工具连接开放标准
- **Model Context Protocol**（Anthropic 发起，已捐赠 Linux Foundation / Agentic AI Foundation 托管）。
- 让工具以统一方式连接文件系统、Git、数据库、浏览器、第三方 API。
- 主流 AI 编码工具均支持 MCP。

### 3. 各平台官方配置格式（矩阵）

| 平台 | 官方入口 | AGENTS.md | MCP | 补充 |
|------|------|:---:|:---:|------|
| Claude Code | `CLAUDE.md` | ✅ | ✅ | `~/.claude/plugins`、`.claude/skills` |
| Cursor | `.cursor/rules/*.mdc` | ✅ | ✅ | 兼容 `.cursorrules` |
| OpenAI Codex | `AGENTS.md` | ✅ | ✅ | `~/.codex/config.toml` |
| Gemini CLI | `GEMINI.md` | ✅ | ✅ | `gemini config add mcp` |
| GitHub Copilot | `.github/copilot-instructions.md` | ✅ | ✅ | 新版支持 AGENTS.md |
| Cline | `CLAUDE.md` / `.clinerules` | ✅ | ✅ | 兼容 AGENTS.md |
| Windsurf | `.windsurf/rules/*.md` | ✅ | ✅ | 兼容 AGENTS.md |
| 通义灵码 | 官方 MCP / 技能 | ✅ | ✅ | 以官方文档为准 |
| 豆包 MarsCode | 官方 MCP / 技能 | ✅ | ✅ | 以官方文档为准 |
| Kimi for Coding | `AGENTS.md` / MCP | ✅ | ✅ | 以官方文档为准 |
| Trae | MCP + 规则 | ✅ | ✅ | 以官方文档为准 |
| 百度 Comate | MCP + 指令 | ✅ | ✅ | 以官方文档为准 |
| 智谱 CodeGeeX | `CLAUDE.md` 兼容 + MCP | ✅ | ✅ | 以官方文档为准 |
| Zed | `.rules/` / MCP | ✅ | ✅ | `.zed/mcp.json` |
| Continue | `config.json` + MCP | ✅ | ✅ | `~/.continue/` |
| Aider | `CONVENTIONS.md` + MCP | ✅ | ✅ | `aider --mcp` |
| JetBrains AI | 官方 MCP + 指令 | ✅ | ✅ | 项目级 MCP |

## 二、目录结构

```
AGENTS.md                 # 跨平台统一指令（权威）
platforms/<平台>/          # 各平台官方格式适配 + 接入说明
mcp/config/               # 各平台 MCP 配置（JSON）
scenarios/<场景>/mcp/     # 场景级 MCP 配置（yaml）
```

## 三、接入一个平台（通用步骤）

1. **统一指令**：仓库根 `AGENTS.md`（多数平台原生支持）。
2. **官方文件**：按上表把对应官方配置文件复制到项目（如 `CLAUDE.md` / `copilot-instructions.md` / `GEMINI.md`）。
3. **MCP**：按平台官方方式启用 `mcp/config/` 中需要的 server。
4. **场景**：加载 `scenarios/<场景>` 的角色/技能/工作流。

## 四、新增平台模板

新平台 = 在 `platforms/<name>/` 建 `README.md`，说明：官方格式、接入命令、MCP 方式、AGENTS.md 支持情况。参考现有范例。

## 五、注意

- 国内平台（通义/豆包/Kimi/Trae/Comate/CodeGeeX）的接入以**各厂商官方最新文档**为准，本仓库提供统一指令与 MCP 兜底。
- 协议能力以官方为准，不自行发明；如官方新增格式，按需更新本表。

> AI生成
