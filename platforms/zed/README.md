# Zed 接入方式

- **官方格式**：`.rules/`（项目规则目录）、`AGENTS.md`；支持 MCP（`.zed/mcp.json` 或 settings）。
- **本仓库**：根 `AGENTS.md` 统一指令。

## 接入步骤

```bash
mkdir -p .zed
# 在 .zed/settings.json 或 .zed/mcp.json 配置 MCP
# 规则放 .rules/ 或根 AGENTS.md
```

## 说明
Zed 支持 AGENTS.md 与 `.rules/`。用根 `AGENTS.md` 作为统一指令，MCP 在 `.zed/` 配置。

> AI生成
