# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] — 2026-10-06

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