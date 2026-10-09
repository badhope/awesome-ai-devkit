# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] — 2026-10-09

### Added
- devkit-doctor.py — CLI health check tool covering skills/scaffolds/mcp/hooks/env
- tests/test_devkit_doctor.py — self-contained integration tests
- scaffolds/scaffold-runner.py — flat-scaffold execution engine
- scaffolds/scaffold-protocol.md — Scaffold Protocol v2.0
- scenarios/programming/fullstack/{bootstrap.sh,bootstrap.ps1}
- context/architecture.md (ADR-001)
- docs/requirements/devkit-doctor.md + docs/design/devkit-doctor.md
- AGENTS.md — 跨平台统一指令（官方 AGENTS.md 标准，含平台自省声明）
- platforms/ — 平台能力矩阵 + 自省机制（复用平台原生能力，不重复造轮子）
- framework/ — 通用能力层（skills 通用技能库 33+ / agents 多角色 / mcp 全集）
- framework/skills 新增 10 个通用技能：code-review、debugging、test-strategy、api-design、secret-scanner、performance-optimization、documentation-writing、architecture-design、requirements-analysis、commit-conventions

### Changed
- scaffold-runner：修复 opencode Windows shim 调用（.cmd/.ps1 经 cmd /c + stdin 传参），并完成真实端到端验证（scaffold-runner→opencode→读 AGENTS.md+skill→产物门禁→完工强制）
- scaffold-runner：新增 opencode provider、每步强制产物校验（outputs gate）、完工强制门禁（enforce_active）、skills 路径指向 framework 通用层
- .gitignore 忽略 logs/sessions/（session 产物不入库）
- 新增 hooks/scripts/enforce_active.py 强制门禁（机制层，跨平台）：上下文/doctor/测试/密钥/CHANGELOG 校验
- hooks/config.yaml 挂载开工（--pre）与完工强制门禁
- AGENTS.md / platforms/README 增加「提示层 vs 机制层」分层说明与按平台强制接入
- devkit-doctor 支持带参数的脚本引用（如 script.py --pre）
- 版本统一为 2.0.0（README/plugin/expert/docs/CHANGELOG 一致）
- devkit-doctor 技能检查增强：扫描所有场景 skills 并集 + 校验「技能名 == 目录名」
- AGENTS.md 增加「强制主动使用能力」机制（Skills/Agents/MCP 必须主动调用，禁止闲置）
- 通用技能从 scenarios/programming/fullstack/skills 提升至 framework/skills（去重、解耦场景）
- fullstack/lib 提升为 framework/lib（通用脚本库）
- devkit-doctor.py 支持检查 framework/skills 通用技能层
- bootstrap 检查 framework/skills
- scaffold.yaml split sequential/parallel (YAML dup-key bug) → flat v2.0
- platforms/ 重构：删除 17 个重复平台 README，改为单一平台能力矩阵 + 自省声明（复用平台原生能力）
- AGENTS.md 增加平台自省机制（识别平台 → 用平台原生能力 → 只补缺失）
- fullstack/scaffolds/*.yaml rewritten in v2.0
- hooks/scripts/{error-alert.sh,pre-task.sh} bash JSON parsing → Python inline
- mcp/config/awesome-servers.json 28 servers → 12 (removed duplicate-key hack)
- .env.example 140+ vars → 8 core vars
- README.md repositioning

### Removed
- fullstack/tools/ (26 Python utilities)
- fullstack/validation/ (5 scripts)
- hooks/scripts/middleware/ (6 orphaned middleware files)
- tools/README.md
- docs/PLATFORMS.md（内容并入 platforms/README.md）
- platforms/ 下 17 个冗余平台 README（保留官方必需入口）

### Fixed
- YAML duplicate key silently dropping steps
- pre-task.sh nested $() syntax error
- error-alert.sh JSON parsing failure in Git Bash
- Cross-platform bootstrap path + Python invocation

> AI生成