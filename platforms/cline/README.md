# Cline 接入方式

- **官方格式**：`CLAUDE.md`（兼容）、`.clinerules`、根 `AGENTS.md`、官方 MCP。
- **本仓库**：复用 `claude-code/CLAUDE.md` 或根 `AGENTS.md`。

## 接入步骤

```bash
# 复用 Claude Code 的 CLAUDE.md，或直接依赖根 AGENTS.md
cp platforms/claude-code/CLAUDE.md /path/to/your/project/CLAUDE.md

# 可选 .clinerules（Cline 专有，追加到项目根）
echo "优先遵循仓库根 AGENTS.md 与 rules/ 规范" > .clinerules
```

## MCP
在 Cline 中启用 `mcp/config/cline-settings.json` 中的 server。

## 说明
Cline 兼容 Claude Code 的 `CLAUDE.md`，同时支持 AGENTS.md，可无缝使用本框架统一指令。

> AI生成
