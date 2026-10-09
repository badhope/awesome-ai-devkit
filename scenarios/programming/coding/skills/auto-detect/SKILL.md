---
name: auto-detect
description: 自动识别项目技术栈、项目类型、测试框架、构建工具与推荐团队角色。通过扫描项目配置文件（package.json/pyproject.toml/go.mod/Cargo.toml 等）自动推断，输出供后续编排的变量。当收到任何开发任务且不清楚项目用什么技术栈、属于什么类型、该用哪些角色时，必须先执行本技能。
layer: orchestration
tags: [detect, tech-stack, project-type, auto, adaptive, scanner]
---

# Auto-Detect — 技术栈与项目类型自动识别

## 触发条件

任何开发任务的**第一步**：先识别项目再决定怎么做。不需要用户告知技术栈——本技能自动从项目文件推断。

## 核心能力

### 1. 识别范围

| 识别项 | 说明 | 示例 |
|--------|------|------|
| `tech_stack` | 技术栈概述 | "React + TypeScript + Vite" |
| `project_type` | 项目类型 | frontend / backend / fullstack / cli / library / mobile / ml |
| `primary_language` | 主语言 | Python / TypeScript / Go / Rust ... |
| `test_framework` | 测试框架 | pytest / jest / vitest / go test / cargo test |
| `build_tool` | 构建工具 | vite / webpack / cargo / go build / maven |
| `package_manager` | 包管理器 | pnpm / npm / pip / cargo / go mod |
| `role_set` | 推荐团队角色 | 来自 framework/agents 的组合 |
| `has_database` | 是否用数据库 | true/false |

### 2. 自动检测来源

按以下顺序读取项目特征：

1. **清单文件**：`package.json`（读 dependencies 定框架）、`pyproject.toml`、`go.mod`、`Cargo.toml`、`pom.xml`
2. **框架指纹**：`vite.config` → 前端，`next.config` → Next，`main.go`/`app.py` → 后端
3. **目录结构**：`cmd/`、`src/`、`migrations/`、`frontend/`+`backend/`（→ 全栈）
4. **测试配置**：`pytest.ini`、`jest.config`、`vitest.config`、`go.mod`+`*_test.go`

## 使用方式

### 方式 A：运行识别器（推荐）

```bash
python3 scenarios/programming/coding/lib/stack-detector.py --project . --json
```

输出 JSON 直接给出全部识别结果，供 `team-composer` 与 `scaffold-generator` 消费。

### 方式 B：Agent 手动判断

当脚本不可用时，Agent 按下表规则人工判断：

| 观察到 | 判定 |
|--------|------|
| `package.json` 含 react/vue + `vite.config` | frontend，vitest |
| `package.json` 含 express + `server.js` | backend，jest |
| 同时有 `frontend/` + `backend/` | fullstack |
| `go.mod` + `cmd/` | backend / cli，go test |
| `pyproject.toml` + `app.py` | backend，pytest |
| `Cargo.toml` + `src/main.rs` | cli，cargo test |
| 只有 `lib/`/`src/` 无入口 | library |
| 出现 `ml/`、`langchain`、`pytorch` | ml |

## 执行流程

```
1. 扫描项目根：读清单文件、框架指纹、目录结构
2. 运行 stack-detector.py --json（若可用）
3. 汇总识别结果 → 填入 {{tech_stack}} / {{project_type}} / {{test_framework}} / {{build_tool}}
4. 交给 team-composer 组团队、scaffold-generator 生成脚手架
5. 输出识别摘要（说明判断依据）
```

## 输出格式

```
📡 项目识别:
- 技术栈: React + TypeScript + Vite
- 类型: frontend
- 测试: vitest
- 构建: vite
- 包管理: pnpm
- 团队建议: frontend-ui-developer, design-system-architect, test-qa-engineer
```

## 原则

- **自动优先**：能读项目文件判断的，绝不问用户
- **不确定时**：技术栈/测试框架二选一有明显优劣时才询问；否则采用识别结果默认值
- **全栈包含**：`frontend/`+`backend/` 并存时判定 fullstack，自动组前后端+架构+DevOps 团队
- **轻量**：识别过程不新建文件，只读

## Checklist

- [ ] 已扫描项目清单文件与目录结构
- [ ] 已运行 stack-detector（如可用）
- [ ] 已输出 {tech_stack, project_type, test_framework, build_tool, package_manager}
- [ ] 已传递给 team-composer / scaffold-generator

## 推荐 SubAgent

- team-composer（据识别结果组团队）
- scaffold-generator（据识别结果生成脚手架）