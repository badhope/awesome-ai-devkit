---
name: model-routing
description: 智能模型路由与动态提示词组装。根据任务复杂度、上下文长度、时效要求自动选择最优 LLM 模型；支持提示词变量注入（{{project_name}}、{{tech_stack}}、{{date}} 等）。
layer: core
tags: [model, routing, prompt, template, dynamic]
---

# Model Routing — 智能路由与动态提示词

## 核心能力

### 1. 变量注册表

以下变量在各 agent 的 system prompt 中可使用，运行时由框架自动解析：

| 变量 | 含义 | 示例值 | 来源 |
|------|------|--------|------|
| `{{project_name}}` | 项目名 | "MyApp" | context/project.yaml |
| `{{tech_stack}}` | 技术栈概述 | "Next.js + FastAPI + Postgres" | context/project.yaml |
| `{{project_root}}` | 项目根路径 | "/workspace/myapp" | 运行时检测 |
| `{{date}}` | 当前日期 | "2026-10-07" | 系统时钟 |
| `{{branch}}` | 当前 Git 分支 | "feature/auth" | git |
| `{{locale}}` | 语言区域 | "zh-CN" | 系统 locale |
| `{{os}}` | 操作系统 | "Windows" | 系统检测 |
| `{{scaffold_type}}` | 当前 scaffold 类型 | "feature" | scaffold.yaml |
| `{{skill_count}}` | 可用技能数 | 23 | skills/ 目录 |
| `{{role}}` | 当前 agent 角色名 | "backend-api-developer" | agent .md |

### 2. 模型路由规则

| 任务特征 | 推荐模型 | 理由 |
|---------|---------|------|
| 简单编辑（<10 行） | 最快模型（Haiku/Sonnet） | 延迟低、成本低 |
| 中等任务（文件内修改） | 平衡模型（Sonnet） | 质量/成本平衡 |
| 复杂推理（跨文件重构） | 最强模型（Opus） | 需要深度推理 |
| 安全审查 | 最强模型（Opus） | 需要全面分析 |
| Bug 修复（有 stack trace） | 平衡模型（Sonnet） | 不需要最强推理 |
| 文档编写 | 最快模型（Haiku/Sonnet） | 不需要代码能力 |

### 3. 使用方式

agent .md 中的 frontmatter 可声明 `model_override`：

```yaml
---
name: security-review-engineer
model_override:
  default: "sonnet"
  high_complexity: "opus"
  security_critical: "opus"
---
```

### 4. 变量注入机制

变量在 agent 启动时由框架解析并注入到 system prompt 中。解析顺序：

1. **静态变量** — 从 `context/project.yaml` 读取（`project_name`、`tech_stack`）
2. **运行时变量** — 由 bootstrap hook 生成（`date`、`branch`、`os`、`locale`）
3. **动态变量** — 由 scaffold runner 在任务执行前计算（`scaffold_type`、`skill_count`、`role`）

注入引擎伪代码：

```
for each variable in registered_variables:
    value = resolver.resolve(variable, context)
    system_prompt = system_prompt.replace("{{" + variable + "}}", value)
```

### 5. 配置示例

```yaml
# context/project.yaml 扩展
model_routing:
  primary:
    provider: anthropic
    model: claude-sonnet-4-20250514
  fallbacks:
    - provider: openai
      model: gpt-5.2
  variables:
    inject_at_start: true      # agent 启动时自动注入
    strict_mode: false         # true = 未解析变量则报错
```

### 6. 多 Provider 适配

```
Provider 统一调用接口:
────────────────────────────────────────────
Anthropic     → claude / claude --print
OpenAI        → codex / openai api call
OpenRouter    → 统一入口，按 model 字段路由
本地 (llama)  → ollama / llama.cpp / onnx

Scaffold Runner 扩展:
  DEVKIT_PROVIDER=openrouter
  DEVKIT_MODEL=claude-sonnet-4-20250514
    → python3 scaffolds/scaffold-runner.py --provider openrouter
```

## Checklist

- [ ] context/project.yaml 已填项目名和技术栈
- [ ] agent frontmatter 声明了 model_override
- [ ] 变量注入引擎（运行时）支持所有注册变量
- [ ] 模型路由表覆盖了 6 种任务特征
- [ ] bootstrap hook 注册了模板环境变量
- [ ] 变量注入顺序正确（静态 → 运行时 → 动态）

## 推荐 SubAgent

- architect-system-designer（架构设计用最强推理）
- security-review-engineer（安全审查用高推理模型）
