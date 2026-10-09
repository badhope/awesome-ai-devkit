# Gemini CLI 接入方式

- **官方格式**：`GEMINI.md`（仓库根）、AGENTS.md（支持）、官方 MCP。
- **本仓库**：`GEMINI.md`（复制到项目根）。

## 接入步骤

```bash
cp platforms/gemini-cli/GEMINI.md /path/to/your/project/GEMINI.md
# MCP：
gemini config add mcp --name filesystem --cmd "npx -y @modelcontextprotocol/server-filesystem ."
```

## 说明

Gemini CLI 读取 `GEMINI.md` 作为项目指令，也支持 AGENTS.md。统一指令见根 `AGENTS.md`。

> AI生成
