# Framework / Agents — 通用多角色团队

> 框架提供**跨场景复用**的通用开发团队角色。任意领域场景可组合这些角色，覆盖从需求到上线的完整闭环。

## 通用角色清单（11 个）

| 角色 | 职责 |
|------|------|
| product-manager | 需求分析、验收标准、优先级 |
| architect-system-designer | 技术设计、ADR、API 契约 |
| database-engineer | Schema、迁移、索引策略 |
| backend-api-developer | API、业务逻辑、数据库逻辑 |
| frontend-ui-developer | UI 组件、状态管理、数据获取 |
| design-system-architect | 设计系统、组件 API、无障碍 |
| test-qa-engineer | 单元/集成/E2E、变异测试 |
| code-reviewer | 独立代码审查 |
| security-review-engineer | OWASP、AI 安全、注入防御 |
| devops-deploy-engineer | CI/CD、部署、SBOM |
| site-reliability-engineer | SLO/SLI、监控、混沌 |

## 使用方式

- 完整定义在 `framework/agents/*.md`（已提升为框架级通用角色）。
- 场景复用：scaffold 的 step 里用对应角色/技能名即可，无需在每个场景重复定义。
- 平台加载：按各平台官方机制（AGENTS.md / Skills / subagents）注册这些角色。

## 原则

- **复用**：通用角色提升为框架能力，场景按需选取，不重复造定义。
- **可组合**：小型任务只需 1-2 个角色，复杂任务用完整团队。

## 相关
- 通用技能：`framework/skills/`
- 统一指令：根 `AGENTS.md`
- 完整全栈团队示例：`scenarios/programming/fullstack/`
