# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- scenarios/programming/coding — 通用编程底座场景（跨语言/技术栈）：_index、coding-agent、3 个通用脚手架（feature-development/refactoring/incident-response）、coding-lifecycle 工作流、project 上下文、mcp 配置
- framework/skills 新增 4 个通用技能：planning、refactoring、observability、session-continuation（通用技能库达 37，后增至 38）
- 同步 README/README_zh/docs/experts 技能计数至 37，并将 coding 场景登记进场景索引

### Added — 自适应编排层（coding 场景升级为"全能自适应底座"）
- skills/auto-detect — 自动识别技术栈/项目类型/测试框架/工具链（扫描项目配置）
- skills/team-composer — 按项目类型自动组建团队（复用 framework 11 角色）
- skills/scaffold-generator — 动态生成适配技术栈的 scaffold
- lib/stack-detector.py — 可执行识别器（输出 tech_stack/project_type/test_framework/role_set）
- scaffolds/adaptive-feature.yaml — 自适应功能开发脚手架
- coding-agent 增强为自动编排者：识别 → 组队 → 生成 → 执行
- scaffold-runner：新增 --stack 技术栈驱动变量映射（ext/module/test_framework 随栈自适应），并支持自动推断技术栈

### Added — 自适应引擎深化
- stack-detector 扩展技术栈指纹：移动端（React Native/Flutter/Android/iOS）、AI/ML（LangChain/PyTorch/TensorFlow）、及更多语言
- coding 默认入口改为自适应（adaptive-feature）；_index/coding-agent 快速开始更新
- examples/todo-list-react — 第一个完整案例（React 前端自适应开发，含复盘）
- tests/test_stack_detector.py — 6 项自适应识别单测（React/Go/Python-ML/Flutter/Rust-CLI/library）
- 真实多技术栈端到端实测全部通过：React 前端、Go 后端、Rust CLI、Python 后端（各 6/6 steps）

### Fixed
- stack-detector：修复普通 React 前端被 App.tsx 误判为 mobile（改为依赖含 react-native/expo 才判 mobile）
- scaffold-runner：修复 scaffold 模板路径占位符（`<feature>`/`<module>`/`<ext>`）未替换导致的产物门禁误判缺失（影响 coding/fullstack 场景）；支持 `--feature` 覆盖与 glob 模糊匹配，并新增回归测试

### Added — 防「AI 坏毛病」强制门禁（pragmatic-guard）
- framework/lib/scripts/quality/pragmatic-guard.py — 可执行校验脚本，检测 5 类问题：重复造轮/冗余文件/虚假实现（pass/TODO/空函数体）/过度设计/业务不合现实（魔法数字/演示字符串/异常被吞）；退出码 0=通过、1=阻断
- framework/skills/pragmatic-guard — 通用技能（5 类规则清单 + 门禁用法），所有编程场景继承
- 挂进 coding adaptive-feature.yaml 的「代码审查」步骤与 post_task 门禁；coding-agent 审查阶段强制运行
- framework 技能库 37→38；tests/test_pragmatic_guard.py 6 项单测（干净项目通过 / 各类坏毛病检出）

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