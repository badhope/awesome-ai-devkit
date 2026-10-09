# Platforms — 跨平台接入层

> Awesome AI DevKit 支持**所有主流 AI 编码平台**。统一接入方式为：
> **1 个 AGENTS.md 权威指令 + MCP 官方工具连接 + 各平台官方配置格式**。

## 接入原则（坚持官方协议，不自造）

1. **统一指令**：根 `AGENTS.md` 是跨平台权威说明书（Cursor / Claude Code / Codex / Gemini / Copilot / Cline 官方支持）。各平台配置都指向它，避免多份重复维护。
2. **工具连接**：一律用 **MCP**（Model Context Protocol，Linux Foundation 托管的开放标准）。
3. **平台适配**：每个平台提供其**官方格式**的配置；官方不指定时用 AGENTS.md + MCP 兜底。
4. **可扩展**：新增平台 = 在 `platforms/<name>/` 加一份官方配置，参考既有范例。

## 平台矩阵

| 平台 | 官方接入格式 | AGENTS.md | MCP | 状态 |
|------|------|:---:|:---:|:---:|
| **海外主流** | | | | |
| Claude Code | `CLAUDE.md` / `~/.claude/plugins` / Skills | ✅ | ✅ | ready |
| Cursor | `.cursor/rules/*.mdc`（兼容 `.cursorrules`） | ✅ | ✅ | ready |
| OpenAI Codex | `AGENTS.md`（CLI 官方） | ✅ | ✅ | ready |
| Gemini CLI | `GEMINI.md` / `AGENTS.md` | ✅ | ✅ | ready |
| GitHub Copilot | `.github/copilot-instructions.md` | ✅ | ✅ | ready |
| Cline | `CLAUDE.md`（兼容）/ `.clinerules` | ✅ | ✅ | ready |
| Windsurf | `.windsurf/rules/*.md` | ✅ | ✅ | ready |
| **国产主流** | | | | |
| 通义灵码（阿里） | 官方规则/技能 + MCP | ✅ | ✅ | ready |
| 豆包 MarsCode（字节） | 官方 MCP / 技能 | ✅ | ✅ | ready |
| Kimi for Coding | `AGENTS.md` / MCP | ✅ | ✅ | ready |
| Trae（腾讯） | MCP + 规则 | ✅ | ✅ | ready |
| 百度 Comate | MCP + 指令 | ✅ | ✅ | ready |
| 智谱 CodeGeeX | `CLAUDE.md` / AGENTS 兼容 + MCP | ✅ | ✅ | ready |
| **长尾工具** | | | | |
| Zed | `.rules/` / AGENTS.md | ✅ | ✅ | ready |
| Continue | `config.json` + MCP | ✅ | ✅ | ready |
| Aider | `CONVENTIONS.md` | ✅ | ✅ | ready |
| JetBrains AI Assistant | 项目级 MCP + 指令 | ✅ | ✅ | ready |

> `ready` = 已提供官方格式适配；标注以该平台官方最新文档为准。

## 目录约定

```
platforms/
├── README.md                    # 本文件（总览 + 矩阵）
├── <平台>/README.md             # 该平台接入说明 + 官方配置
│   └── <官方格式文件>           # 可复制到项目根 / 平台目录
```

## 通用接入步骤（对任意平台）

```bash
# 1. 克隆框架
git clone https://gitcode.com/badhope/awesome-ai-devkit.git
cd awesome-ai-devkit

# 2. 健康检查
python devkit-doctor.py

# 3. 选一个场景，在目标平台加载（见 platforms/<平台>/）
```

## 参考

- `AGENTS.md`（仓库根）— 统一指令权威
- `mcp/config/` — 各平台 MCP 配置
- `docs/PLATFORMS.md` — 详细平台×协议支持文档

> AI生成
