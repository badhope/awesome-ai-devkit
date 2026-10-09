# Claude Code 接入

- **官方格式**：`CLAUDE.md`（仓库根）、`~/.claude/plugins/`（插件）、`.claude/skills/`（技能）、MCP（`.mcp.json` 或 `claude mcp add`）。
- **本仓库提供**：`CLAUDE.md`（复制到项目根即可生效）。
- **AGENTS.md**：Claude Code 2.1.277+ 原生支持根 `AGENTS.md`，本仓库已内置。

## 接入步骤

```bash
# 方式 A：把本仓库的 CLAUDE.md 复制到你的项目根
cp platforms/claude-code/CLAUDE.md /path/to/your/project/CLAUDE.md

# 方式 B：启用 MCP（官方）
claude mcp add filesystem npx -y @modelcontextprotocol/server-filesystem /path/to/project
claude mcp add git npx -y @modelcontextprotocol/server-git --repo /path/to/project
```

## 技能（Skills）接入

Claude Code 官方支持 Agent Skills。将 `scenarios/<场景>/skills/<name>/SKILL.md` 放入 `.claude/skills/<name>/SKILL.md` 即可注册为一个技能。

## MCP 参考配置

见 `mcp/config/claude-desktop.json`。

> AI生成
