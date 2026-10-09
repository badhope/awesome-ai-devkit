# Awesome AI DevKit

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.0.0-green.svg)](https://github.com/x33834/awesome-ai-devkit/releases/tag/v2.0.0)
[![场景](https://img.shields.io/badge/场景-1-blue.svg)](scenarios/)
[![源码平台](https://img.shields.io/badge/源码平台-4-lightgrey.svg)](#源码--4-个平台)
[![欢迎 PR](https://img.shields.io/badge/PR-欢迎-brightgreen.svg)](https://github.com/x33834/awesome-ai-devkit/pulls)
[![官网](https://img.shields.io/badge/官网-在线-success.svg)](https://x33834.github.io/awesome-ai-devkit/)

**AI 编程配置生态** — 模块化场景，将 AI 编码工具变成完整的开发团队。基于任何支持专家插件标准的平台运行。

[🇨🇳 中文](README_zh.md) | [🌐 English](README.md)

---

## 这是什么？

Awesome AI DevKit 是一个跨平台的**场景化** AI 编程配置仓库。每个场景提供一套针对特定领域的 AI 角色、技能、工作流和最佳实践。

> 本项目是一个**标准与配置**仓库 — 场景、角色、技能、工作流均为模块化，按需组合。

运行在**任何支持 Expert 插件标准的工具上**。

### 核心能力

- **指令润色** — 自动将口语化/模糊的用户指令转化为结构化提示词，智能推断默认值、结合项目上下文
- **AI Agent 安全** — Prompt 注入防御、子代理深度管控、Skill 完整性校验、资源限制
- **质量保障** — 自动化测试工作流、代码质量分析、发布治理、语义化版本
- **上下文优化** — 智能上下文压缩、跨长会话记忆管理
- **多角色团队** — 每个场景提供产品、工程、QA、运维等特定领域的角色配置
- **脚手架工作流** — YAML 定义的多步骤开发协议，内建质量门禁

---

## 内置场景

### 全栈开发团队 *(内置)*

覆盖产品到运维的完整流水线：11 个通用角色（产品经理、架构师、后端、前端、设计系统、QA、代码审查、安全审查、DevOps、SRE、数据库工程师）和 37 个通用技能（代码质量、安全、上下文、自动化、审查、调试、测试策略、规划等），位于 `framework/` 通用层。

| 内容 | 路径 |
|------|------|
| 角色与技能 | `scenarios/programming/fullstack/` |
| 快速开始（内置） | 见下方 |

更多场景（业务运营、数据工程、ML、移动端等）可按需添加 — 参见 [`scenarios/`](scenarios/) 了解完整列表和贡献指南。

---

## 快速开始

### 1. 克隆

```bash
git clone https://gitcode.com/badhope/awesome-ai-devkit.git
cd awesome-ai-devkit
```

### 2. 初始化全栈场景

```bash
# Linux / macOS / WSL
bash scenarios/programming/fullstack/bootstrap.sh

# Windows PowerShell
powershell -File scenarios/programming/fullstack/bootstrap.ps1
```

脚本会自动检查前置工具（git、node、python）并创建 `context/project.yaml` 模板。

### 3. 配置

编辑 `scenarios/programming/fullstack/context/project.yaml`，填写：

- 项目名称
- 技术栈（前端、后端、数据库）
- 项目特定的约定规范

### 4. 开始使用

在 AI 编码工具中打开项目目录，加载全栈场景，然后输入：

> "使用全栈开发团队来实现 [你的功能]"

全栈场景内置工作流：

- `scaffolds/feature-development.yaml` — 新功能实现
- `scaffolds/refactoring.yaml` — 代码重构
- `scaffolds/incident-response.yaml` — 线上故障响应

---

## 安装为 Expert 插件

参考你所使用的 AI 编码工具的官方插件安装指南。一般步骤：

```bash
cd /path/to/awesome-ai-devkit
# 参考所用工具的文档安装 Expert 插件
```

将全栈场景及内置内容注册为 Expert，所有角色和技能即可使用。

---

## 项目结构

```
awesome-ai-devkit/
├── framework/                   # 通用能力层（跨平台复用）
│   ├── skills/              # 37+ 通用技能库（agentskills.io 标准）
│   ├── agents/              # 通用开发团队角色（11 个）
│   ├── mcp/                 # 通用 MCP 全集
│   ├── lib/                 # 通用脚本库
│   └── rules/               # 通用规则
├── scenarios/
│   ├── programming/fullstack/   # 全栈开发团队场景（复用 framework）
│   │   ├── scaffolds/           # 工作流模板
│   │   ├── workflows/           # 分步操作手册
│   │   ├── hooks/               # 生命周期钩子
│   │   └── context/             # 项目配置模板
│   └── ...                      # 更多场景（业务运营、移动端等）
├── mcp/config/                  # 各平台 MCP 设置
├── roles/expanded/              # 扩展角色定义
├── docs/                        # 设计文档
└── experts/                     # Expert 插件清单（平台无关）
```

---

## 源码

| 平台 | 地址 | 用途 |
|------|------|------|
| GitCode | https://gitcode.com/badhope/awesome-ai-devkit | **主仓库** |
| Gitee | https://gitee.com/badhope/awesome-ai-devkit | 国内镜像 |
| GitHub | https://github.com/X33834/awesome-ai-devkit | **官网 + Release** |
| GitHub | https://github.com/Morningstar202604/awesome-ai-devkit | 备用镜像 |

## 相关链接

- 官网: https://x33834.github.io/awesome-ai-devkit/
- 发布页: https://github.com/X33834/awesome-ai-devkit/releases
- 问题反馈: https://github.com/X33834/awesome-ai-devkit/issues

---

## 许可证

MIT © [badhope](https://gitcode.com/badhope)

> AI生成