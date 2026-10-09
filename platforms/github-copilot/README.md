# GitHub Copilot 接入方式

- **官方格式**：`.github/copilot-instructions.md`（仓库级指令）；AGENTS.md（新版支持）；官方 MCP。
- **本仓库提供**：`copilot-instructions.md`（复制到项目 `.github/`）。

## 接入步骤

```bash
# 把官方指令文件放到项目 .github/ 下
cp platforms/github-copilot/copilot-instructions.md /path/to/your/project/.github/copilot-instructions.md

# Copilot 同时读取根 AGENTS.md（官方已支持）
# MCP：在 Copilot 中启用 MCP server（官方配置）
```

## 说明

Copilot 读取 `.github/copilot-instructions.md` 作为项目级指令，与 AGENTS.md 配合，为仓库内的 AI 助手提供统一上下文。

> AI生成
