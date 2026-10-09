# Awesome AI DevKit — Gemini CLI

> Gemini CLI 官方项目指令文件（`GEMINI.md`）。
> 权威统一说明见仓库根 `AGENTS.md`。

## 项目性质
- 跨平台场景化 AI 编程配置生态：通用框架层 + 领域场景层。
- 内置示例：`scenarios/programming/fullstack/` 全栈开发团队。

## 对 Gemini CLI 的约定
- 先读后写；改动前运行 `python devkit-doctor.py` 与 `python -m pytest -q`。
- 遵循 `rules/coding-standards.md`（命名、类型、测试、安全、错误处理）。
- 提交遵循 Conventional Commits；不提交密钥/个人绝对路径。
- 场景任务：读取 `context/project.yaml`，按 `scaffolds/*.yaml` 执行多步骤协议。

## MCP
- 启用本仓库场景的 MCP server（`mcp/mcp-config.yaml` 中 `enabled: true`）。

> AI生成
