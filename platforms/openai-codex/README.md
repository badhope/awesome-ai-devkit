# OpenAI Codex 接入方式

- **官方格式**：`AGENTS.md`（Codex CLI 官方采用）；MCP（`~/.codex/config.toml`）。
- **本仓库**：根 `AGENTS.md` 已就绪，Codex 直接使用，无需额外文件。

## 接入步骤

```bash
# Codex 默认读取仓库根 AGENTS.md（已内置）
# MCP 配置（官方）：
codex mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem .
```

## 说明

Codex 官方已将 `AGENTS.md` 作为项目指令入口。把本仓库根 `AGENTS.md` 保留即可，Codex 打开目录自动生效。

> AI生成
