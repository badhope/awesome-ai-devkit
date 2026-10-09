# Aider 接入方式

- **官方格式**：`CONVENTIONS.md`（仓库根约定文件，Aider 读取）；支持 MCP（`aider --mcp`）。
- **本仓库**：可用 `CONVENTIONS.md` 承接 AGENTS.md 的约定内容。

## 接入步骤

```bash
# 创建仓库约定文件（Aider 官方识别 CONVENTIONS.md）
echo "见仓库根 AGENTS.md 的编码/工程约定" > CONVENTIONS.md

# 启用 MCP（官方）
aider --mcp <server>
```

## 说明
Aider 读取 `CONVENTIONS.md` 作为约定。可将 `AGENTS.md` 的规范要点写入。

> AI生成
