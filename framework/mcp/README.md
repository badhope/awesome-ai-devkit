# Framework / MCP — 通用 MCP 全集

> 工具连接统一走 **MCP**（Model Context Protocol，开放标准）。这里给出**跨场景通用**的 MCP 推荐全集；各场景可在此基础上按需启用。

## 通用 MCP 全集（按需启用）

| 类别 | server | 说明 | 默认 |
|------|------|------|:---:|
| 文件系统 | `filesystem` | 本地文件读写 | ✅ |
| 版本控制 | `git` | diff / log / blame / 分支 | ✅ |
| 代码托管 | `github` | Issues / PR / CI | ✅ |
| 数据库 | `postgres` | 查询 / schema | ✅ |
| 缓存 | `redis` | KV / 队列 / 订阅 | ⏸ |
| 浏览器 | `playwright` | E2E / 截图 / 爬取 | ✅ |
| 容器 | `docker` | 容器 / 镜像 | ⏸ |
| 搜索 | `brave-search` | 网页搜索 | ✅ |
| 支付 | `stripe` | 支付 / 订阅 / 发票 | ⏸ |
| 邮件 | `resend` | 邮件发送 | ⏸ |
| 向量库 | `qdrant` | 向量检索 | ⏸ |
| 知识库 | `notion` | 读写 | ⏸ |
| 消息 | `slack` | 消息 / 频道 | ⏸ |
| 项目 | `linear` | Issue / Sprint | ⏸ |
| 部署 | `vercel` | 环境变量 / 部署 | ⏸ |
| 监控 | `sentry` | 错误追踪 | ⏸ |
| BaaS | `supabase` | Auth / DB / Storage | ⏸ |

> ✅=默认启用；⏸=按需启用（需对应 env/key）。完整 server 定义见 `mcp/config/awesome-servers.json` 与 `scenarios/programming/fullstack/mcp/mcp-config.yaml`。

## 使用

- 场景级：`scenarios/<场景>/mcp/mcp-config.yaml` 中设 `enabled: true/false`。
- 平台级：`mcp/config/*.json`（对应各工具官方 MCP 配置格式）。
- 安全：`filesystem_block` 保护 `.env`、`.git/`、`*.key`、`secrets/`。

## 原则

- **用官方 MCP**，不自造工具协议。
- **默认启用**必要的（filesystem/git/github/postgres/playwright），其余按场景按需，避免资源浪费与密钥暴露。
