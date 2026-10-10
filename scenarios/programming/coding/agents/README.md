# 通用编程场景 — Agents

> 本场景是**通用底座**，编码角色**复用框架层 `framework/agents/` 的 11 个通用 agent**，不重复定义完整角色。

## 复用框架角色（核心子集）

| 角色 | 用途 |
|------|------|
| `architect-system-designer` | 方案设计、ADR、接口契约 |
| `backend-api-developer` | 后端/服务实现 |
| `frontend-ui-developer` | 前端/界面实现 |
| `test-qa-engineer` | 测试策略与执行 |
| `code-reviewer` | 独立代码审查 |
| `security-review-engineer` | 安全基线审查 |
| `devops-deploy-engineer` | 构建/CI/CD |

> 完整列表见 `framework/agents/`。

## 场景专属角色

`coding-agent`（见本目录）— 通用编码执行者：在「通用编程开发场景」下按 Scaffold 协议端到端推进任务（需求→方案→编码→测试→审查→提交），并负责复用/编排框架层角色。

## 约定

- 新角色若跨场景通用 → 放 `framework/agents/`
- 仅本场景独有且通用编程特有 → 放本目录
