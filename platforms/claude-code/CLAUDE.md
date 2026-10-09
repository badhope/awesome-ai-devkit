# Awesome AI DevKit — Claude Code

> 这是 **Claude Code 官方识别的项目说明文件**（`CLAUDE.md`）。
> 权威统一指令见仓库根 [../AGENTS.md](../AGENTS.md)；本文件是 Claude Code 的特化入口。

## 这是什么

Awesome AI DevKit 是一个跨平台场景化 AI 编程配置生态：通用框架层 + 专用场景层。
Claude Code 打开本仓库后自动读取本文件与根 `AGENTS.md`。

## 对 Claude Code 的约定

1. **先读后写**：修改前先读取目标文件与项目结构。
2. **加载场景**：按需激活 `scenarios/` 下对应场景的角色与技能（如 `scenarios/programming/fullstack/`）。
3. **健康检查**：改动后运行 `python devkit-doctor.py` 与 `python -m pytest -q`。
4. **MCP**：本仓库的 MCP 配置见 `mcp/config/claude-desktop.json`；按需启用 `enabled: true` 的 server。
5. **提交规范**：遵循 Conventional Commits；不提交密钥/个人路径。

## 场景示例

用户说「用全栈团队实现某功能」时：
- 读取 `context/project.yaml` 与 `context/architecture.md`
- 按 `scenarios/programming/fullstack/scaffolds/feature-development.yaml` 的步骤执行
- 每阶段输出物满足 `outputs.contains` 与 `quality_gate`

## 更多

- 规则与规范：`rules/`
- 角色：`scenarios/<场景>/agents/`
- 技能：`scenarios/<场景>/skills/`
- 工作流：`scenarios/<场景>/scaffolds/`

> AI生成
