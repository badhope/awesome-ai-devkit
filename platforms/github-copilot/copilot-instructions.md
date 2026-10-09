# Awesome AI DevKit — GitHub Copilot 项目指令

> 官方 Copilot 项目级指令文件（`copilot-instructions.md`）。
> 权威统一说明见仓库根 `AGENTS.md`。本文件为 Copilot 提供仓库级上下文。

## 项目性质
- 跨平台场景化 AI 编程配置生态：通用框架层 + 各领域场景层。
- 当前内置示例场景：`scenarios/programming/fullstack/`（全栈开发团队）。

## 对 Copilot 的约定
- 修改文件前先读取结构与现有内容。
- 遵循 `rules/coding-standards.md`（TS/Python 命名、类型、测试、安全）。
- 提交遵循 Conventional Commits；不提交密钥、`.env`、个人绝对路径。
- 改动前运行 `python devkit-doctor.py` 与 `python -m pytest -q`。
- 场景相关：加载 `context/project.yaml`、按 `scaffolds/*.yaml` 执行。

## 技术栈默认（全栈场景）
- 前端：Next.js / React + TS；后端：FastAPI + Pydantic；DB：PostgreSQL + Redis + Qdrant。

> AI生成
