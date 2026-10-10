# AGENTS.md

> **跨平台统一指令（AGENTS.md）** — 本文件是 Awesome AI DevKit 仓库面向**所有 AI 编码 Agent** 的权威说明书。
> `AGENTS.md` 是被 Cursor、Claude Code、OpenAI Codex、Gemini CLI、GitHub Copilot、Cline 等主流工具**官方支持**的跨平台指令标准（Anthropic 与 OpenAI 均已采用），用于替代各平台各自维护的 `.cursorrules` / `CLAUDE.md` / `AGENT.md` 碎片化配置。
>
> 放到本仓库根目录，任何支持 AGENTS.md 的工具打开本目录都会自动读取并生效。

---

## 1. 本仓库是什么

Awesome AI DevKit 是一个**跨平台的场景化 AI 编程配置生态**。它分为两层：

- **通用框架层（Framework）**：11 层通用能力，跨领域复用，与具体业务无关。
  `Rules` · `Roles` · `Skills` · `Tools` · `MCP` · `Agents` · `Expert` · `Workflows` · `Hooks` · `Context` · `Validation`
- **专用场景层（Scenarios）**：基于框架的二次开发，把某个领域（如全栈、论文、金融）专用的角色、技能、团队配置进去。每个场景独立可组合。

通用能力的实体存放在 **`framework/`** 目录：

- `framework/skills/` — 通用技能库（`agentskills.io` 标准 `SKILL.md`，38+ 个）
- `framework/agents/` — 通用多角色团队（跨场景复用）
- `framework/mcp/` — 通用 MCP 全集
- `framework/rules/` — 通用规则（权威在根 `rules/`）

`framework/` 是"从空白把能力拉满"的核心；`scenarios/` 只在上面补充领域专属。详见 [`framework/README.md`](framework/README.md)。

当前内置一个完整示例场景：`scenarios/programming/fullstack/`（全栈开发团队，复用框架通用层）。更多场景按需添加。

---

## 2. 关键原则（适用于所有助手）

1. **先读后写**：修改任何文件前先读取现有内容与结构，不做无关改动。
2. **区分框架与场景**：通用能力放框架层，领域专用内容放对应场景目录，不要混放。
3. **质量门禁**：提交前通过 `python devkit-doctor.py` 与 `python -m pytest -q`。
4. **配置即代码**：角色、技能、工作流、钩子、MCP 都是 YAML/Markdown 配置，遵循 schema 与既有范例。
5. **安全底线**：禁止硬编码密钥；使用 `${VAR}` 占位；禁止提交个人绝对路径（`/Users/...`、`C:\Users\...`、`/mnt/...`）。
6. **主动使用能力（强制）**：本框架已用开放标准提供了 Skills / Agents / Subagents / MCP / Hooks 等能力，**必须主动加载与调用，禁止因"用户没点名"而闲置**。每次任务启动先调用 `instruction-grooming`；凡适用场景/技能/工具的，一律调用；完工按 `quality_gate` 校验（详见 §4）。

---

## 3. 编码规范

详细的按语言规范见 `rules/coding-standards.md`，核心约定：

| 维度 | 约定 |
|------|------|
| 命名 | 变量/函数 `camelCase`（TS）/`snake_case`（Py）；类 `PascalCase`；常量 `UPPER_SNAKE` |
| 类型 | TS 禁止 `any`；Python 公共函数必须有类型注解（3.10+ 用 `X \| None`） |
| 函数 | ≤50 行；≤3 参数（多则用 options 对象）；单一职责、纯函数优先 |
| 错误 | 不吞异常；结构化错误 + `request_id`；边界处校验输入 |
| 日志 | JSON 格式；禁止生产环境 `console.log` / `print` |
| 数据库 | 参数化查询（禁拼接 SQL）；变更走 migration；软删除 `deleted_at` |
| API | RESTful；资源复数；正确状态码；OpenAPI 文档；版本化 |
| 测试 | 业务逻辑全覆盖；AAA 模式；mock 外部依赖；覆盖率 ≥80% |

---

## 4. 工作方式（框架能力）

> **强制主动使用流程**（凡任务必执行，不得跳过，见原则 6）：
> 1. **启动** → 调用 `instruction-grooming` 明确意图；
> 2. **匹配技能** → 加载并调用对应 `framework/skills` 或场景技能的 `SKILL.md`；
> 3. **协作** → 需要分工时调度对应角色/Subagent（`framework/agents`）；
> 4. **工具** → 需要外部能力时启用对应 MCP server；
> 5. **多步任务** → 按 scaffold 工作流执行，逐步满足 `quality_gate`。
> 铁律：**凡是能用上的能力，就用；不能闲置。** 若"有 skill/agent 但没用"，视为执行缺陷。

- **角色（Agents）**：`framework/agents/*.md` 定义通用开发团队角色（frontmatter：`name`/`description`/`tools`）。任务匹配时主动调度对应角色/Subagent。
- **技能（Skills）**：`framework/skills/<name>/SKILL.md` 定义可复用技能（frontmatter 含 `name`/`description`）。任务匹配时主动加载并调用；亦通过 `skills:` 在 scaffold 中引用。
- **工作流（Scaffolds）**：`scaffolds/*.yaml` 定义多步骤开发协议（`version: "2.0"`），含 `steps`、`parallel`、`outputs`、`quality_gate`。复制一个既有 scaffold 改造成新流程。
- **钩子（Hooks）**：`hooks/config.yaml` 绑定生命周期脚本（`pre-task` / `post-task` / `middleware`）。
- **上下文（Context）**：`context/project.yaml` 记录项目元数据；`context/architecture.md` 记录 ADR。
- **MCP**：`mcp/mcp-config.yaml` 声明 MCP server；启用 `enabled: true` 的服务。连接统一走官方 **MCP**（Model Context Protocol，Linux Foundation 托管开放标准）。

---

## 5. 质量与安全门禁

**分层强制（不只靠提示，靠机制）**：提示词只约束"自觉"，以下机制把关键动作变成"**不通过就失败**"，平台无关：

- **L1 机制层**：`hooks/scripts/enforce_active.py`（跨平台门禁：项目上下文 / doctor / 测试 / 密钥 / CHANGELOG / **pragmatic-guard**）。完工与开工均挂载在 `hooks/config.yaml`。
- **L2 平台原生钩子**：有 hooks 的平台（Claude Code / Cursor 等）把 `enforce_active.py` 挂到原生事件，见 `platforms/README.md`。
- **L3 结果门禁**：`quality_gate` / CI / `devkit-doctor` —— 不满足即判定失败。
- **防「AI 坏毛病」门禁（pragmatic-guard）**：`framework/lib/scripts/quality/pragmatic-guard.py`（已并入 enforce_active 完工链）。产出代码必须通过它，否则**拒绝提交/完工**。它拦截 5 类 AI 坏毛病：
  1. **重复造轮子** — 已有库/框架可完成却手写；实现前先查依赖与现有代码
  2. **冗余文件** — 空文件、无用命名（placeholder/dummy/stub）、未被引用文件
  3. **虚假实现** — `pass`/`TODO`/`FIXME`/`NotImplementedError`/空函数体/占位 `return None`
  4. **过度设计** — 过度工厂/无用配置类/命名堆叠/永假分支（YAGNI + KISS）
  5. **业务不合现实** — 魔法数字（>4 位）、演示字符串（hello/world）、try 无 except（异常被吞）
  ```
  python3 framework/lib/scripts/quality/pragmatic-guard.py --project .   # 0=通过，1=整改后重跑
  ```

在任务中执行：

- 提交前运行 `python devkit-doctor.py`（检查 skills/scaffolds/mcp/hooks/agents/json/docs/git/env）。
- 完工运行 `python hooks/scripts/enforce_active.py`（强制门禁）。
- 运行 `python -m pytest -q` 保证测试通过。
- 变更遵循 Conventional Commits：`feat:` `fix:` `docs:` `chore:` `ci:`。
- CHANGELOG 遵循 Keep a Changelog；版本遵循 Semantic Versioning。
- 不得提交 `.env`、密钥、`node_modules/`、`__pycache__/` 等（见 `.gitignore`）。

---

## 6. 平台适配（不重复造轮子）

面向所有主流 AI 编码平台。核心原则：

- **复用平台原生能力**：Skill 加载、Subagents/多 Agent 协作、Rules、Hooks、MCP 客户端、命令/插件——平台已内置，**绝不重复造**。
- **只补平台缺失的**：领域场景、专家团队提示词、私有规则等平台没有的，才由仓库提供。
- **统一开放载体**：通用能力只用一个载体维护 —— 本 `AGENTS.md` + `agentskills.io` 的 `SKILL.md` + `MCP`。
- **平台自省（Agent 读取时判定用什么）**：
  1. 识别平台：读取根 `AGENTS.md` 或平台入口文件（`CLAUDE.md` / `GEMINI.md` / `copilot-instructions.md` / `.cursorrules`）
  2. 平台已内置的 → 用平台原生的（多 Agent、Skill 加载、MCP、Hook），不重复
  3. 平台缺失的 → 才加载 `scenarios/` / `platforms/` 内容
  4. 全程遵循本 `AGENTS.md`，不自造协议、不与平台冲突

各平台能力矩阵与自省机制见 [`platforms/README.md`](platforms/README.md)。

---

## 7. 快速上手（维护者用）

```bash
# 健康检查
python devkit-doctor.py

# 测试
python -m pytest -q

# 初始化一个场景
bash   scenarios/programming/fullstack/bootstrap.sh   # macOS/Linux
powershell -File scenarios/programming/fullstack/bootstrap.ps1   # Windows
```
