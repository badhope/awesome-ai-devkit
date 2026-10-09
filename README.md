# Awesome AI DevKit

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.0.0-green.svg)](https://github.com/x33834/awesome-ai-devkit/releases/tag/v2.0.0)
[![Scenarios](https://img.shields.io/badge/scenarios-1-blue.svg)](scenarios/)
[![Source](https://img.shields.io/badge/source%20platforms-4-lightgrey.svg)](#source-code--4-platforms)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/x33834/awesome-ai-devkit/pulls)
[![Website](https://img.shields.io/badge/website-live-success.svg)](https://x33834.github.io/awesome-ai-devkit/)

**AI Coding Configuration Ecosystem** — modular scenarios that turn AI coding tools into full development teams. Runs on any platform that supports the Expert plugin standard.

[🇨🇳 中文](README_zh.md) | [🌐 English](README.md)

---

## What is this?

Awesome AI DevKit is a cross-platform **scenario-based** AI coding configuration repository. Each scenario provides a tailored team of AI roles, skills, workflows, and best practices for a specific domain.

> This is a **standard and configuration** repository — scenarios, roles, skills, and workflows are modular, mix-and-match.

Works on **any tool that supports the Expert plugin standard**.

### Key Capabilities

- **Instruction Grooming** — auto-polish vague user instructions into structured prompts, with intelligent defaults and project-aware inference
- **AI Agent Security** — prompt injection defense, sub-agent depth control, skill integrity verification, resource limits
- **Quality Assurance** — automated testing workflows, code quality analysis, release governance, semantic versioning
- **Context Optimization** — intelligent context compression and memory management across long sessions
- **Multi-Role Teams** — each scenario provides a domain-specific team of product, engineering, QA, and operations roles
- **Scaffold Workflows** — YAML-defined multi-step development protocols with built-in quality gates

---

## Included Scenarios

### Fullstack Dev Team *(included)*

A complete product-to-operations pipeline: 11 universal roles (PM, Architect, Backend, Frontend, Design System, QA, Code Review, Security, DevOps, SRE, Database Engineer) and 37 reusable skills (code quality, security, context, automation, review, debugging, test strategy, planning, and more) in the `framework/` layer.

| What | Path |
|------|------|
| Roles & Skills | `scenarios/programming/fullstack/` |
| Quick start (included) | See below |

### Universal Coding Scene *(included)*

A cross-language, stack-agnostic coding foundation: covers the full "plan → code → test → refactor → commit" flow, reusing the 37 universal skills and 11 roles in `framework/`. Ideal for scripts, CLIs, libraries, algorithms, and any non-stack-specific task; can be inherited by fullstack, mobile, ml-native and other sub-scenes.

| What | Path |
|------|------|
| Scene definition & scaffolds | `scenarios/programming/coding/` |
| Coding lifecycle workflow | `scenarios/programming/coding/workflows/` |

More scenarios (business-ops, data-engineering, ml-native, mobile, etc.) can be added — see [`scenarios/`](scenarios/) for the full list and contribution guide.

---

## Quick Start

### 1. Clone

```bash
git clone https://gitcode.com/badhope/awesome-ai-devkit.git
cd awesome-ai-devkit
```

### 2. Bootstrap the Fullstack scenario

```bash
# Linux / macOS / WSL
bash scenarios/programming/fullstack/bootstrap.sh

# Windows PowerShell
powershell -File scenarios/programming/fullstack/bootstrap.ps1
```

This verifies prerequisites (git, node, python) and creates `context/project.yaml` from template.

### 3. Configure

Edit `scenarios/programming/fullstack/context/project.yaml` and fill in:

- Project name
- Tech stack (frontend, backend, database)
- Any project-specific conventions

### 4. Start Using

Open your AI coding tool in the project directory. Load the Fullstack scenario, then:

> "Use the fullstack dev team to implement [your feature]"

Available workflows inside the Fullstack scenario:

- `scaffolds/feature-development.yaml` — new feature implementation
- `scaffolds/refactoring.yaml` — code refactoring
- `scaffolds/incident-response.yaml` — production incident handling

---

## Install as Expert Plugin

Follow your AI coding tool's plugin installation guide. Generally:

```bash
cd /path/to/awesome-ai-devkit
# Refer to your tool's documentation for Expert plugin installation
```

Registers the Fullstack scenario and other included content as an Expert in your workspace.

---

## Project Structure

```
awesome-ai-devkit/
├── framework/                   # Universal capability layer (cross-platform)
│   ├── skills/                  # 37+ universal skill library (agentskills.io)
│   ├── agents/                  # Universal dev-team roles (11)
│   ├── mcp/                     # Universal MCP collection
│   ├── lib/                     # Universal scripts
│   └── rules/                   # Universal rules
├── scenarios/
│   ├── programming/fullstack/   # Fullstack Dev Team scenario (reuses framework)
│   │   ├── scaffolds/           # Workflow templates
│   │   ├── workflows/           # Step-by-step playbooks
│   │   ├── hooks/               # Lifecycle hooks
│   │   └── context/             # Project config templates
│   └── ...                      # More scenarios (business-ops, mobile, etc.)
├── mcp/config/                  # Platform-specific MCP settings
├── roles/expanded/              # Extended role definitions
├── docs/                        # Design docs
└── experts/                     # Expert plugin manifests (platform-agnostic)
```

---

## Source Code

| Platform | URL | Purpose |
|----------|-----|---------|
| GitCode | https://gitcode.com/badhope/awesome-ai-devkit | **Primary repo** |
| Gitee | https://gitee.com/badhope/awesome-ai-devkit | China mirror |
| GitHub | https://github.com/X33834/awesome-ai-devkit | **Website + Release** |
| GitHub | https://github.com/Morningstar202604/awesome-ai-devkit | Backup mirror |

## Links

- Website: https://x33834.github.io/awesome-ai-devkit/
- Releases: https://github.com/X33834/awesome-ai-devkit/releases
- Report issues: https://github.com/X33834/awesome-ai-devkit/issues

---

## License

MIT © [badhope](https://gitcode.com/badhope)

> AI生成