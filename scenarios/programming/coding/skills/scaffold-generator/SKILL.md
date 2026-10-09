---
name: scaffold-generator
description: 根据 auto-detect 识别出的技术栈/项目类型与 team-composer 组建的团队，动态生成适配的 scaffold.yaml（步骤、技术栈、质量门禁随项目类型变化）。当需要一个"量身定制"的开发脚手架，而非使用静态模板时调用。
layer: orchestration
tags: [scaffold, generate, adaptive, yaml, workflow]
---

# Scaffold Generator — 动态生成开发脚手架

## 触发条件

在 `auto-detect`（识别）+ `team-composer`（组团队）之后，生成一个**适配当前项目技术栈**的 scaffold.yaml，作为本次任务的执行蓝图。

## 核心能力

### 按项目类型生成步骤骨架

| 项目类型 | 核心步骤骨架 |
|---------|------------|
| **frontend** | 需求 → UI/组件设计 → 前端实现 → 交互+响应式 → 测试 → 审查 |
| **backend** | 需求 → API/数据模型设计 → 后端实现 → 测试 → 安全审查 → 提交 |
| **fullstack** | 需求 → 架构+API+Schema → 后端实现(并行) + 前端实现(并行) → 集成测试 → 审查 → 发布 |
| **cli** | 需求 → CLI 接口设计 → 实现 → 测试 → 文档 → 打包 |
| **library** | 需求 → API 设计 → 实现 → 单测覆盖 → 文档 → 发布 |
| **ml** | 需求 → 数据/模型方案 → 实现 → 评估 → 测试 → 安全审查 |

### 随技术栈变化的产出与门禁

| 技术栈 | 示例产出路径 | 质量门禁 |
|--------|------------|---------|
| TypeScript/JS | `src/components/*.tsx` | `npm run build` 无 error |
| Python | `src/<module>/*.py` | `pytest` 全通过 |
| Go | `cmd/` + `internal/*.go` | `go test ./...` 全通过 |
| Rust | `src/lib.rs` / `src/main.rs` | `cargo test` 全通过 |

## 使用方式

生成 scaffold 时，用 `<变量>` 占位符标记会变化的路径（scaffold-runner 会自动替换）：

```yaml
version: "2.0"
task:
  name: "feature-development"
  feature: "your-feature"      # 会被 runner 替换 <feature>
steps:
  - goal: "编码实现 + 单元测试"
    skills: [debugging, linter-formatter]
    outputs:
      - src/<module>/<feature>.<ext>:     # <module>/<ext> 自动替换
          contains: [def, class]
    quality_gate: "单元测试全部通过"
```

### 变量注入

- `{{tech_stack}}`、`{{project_type}}`、`{{test_framework}}`、`{{build_tool}}` 由 auto-detect 填充
- 这些变量随 prompt 注入 agent，确保它按正确技术栈实现

## 生成的脚手架结构

每个生成结果包含：

```
1. task 元数据（name/description/type/feature）
2. memory 引用（context/project.yaml、architecture.md、CHANGELOG.md）
3. steps 列表（阶段、技能、产出物、质量门禁）
4. post_task quality_gates + loop_config（最多 3 轮自动修复）
```

## 与静态模板的关系

- 静态模板（`scaffolds/*.yaml`）作为**起点/参考**
- 本技能在静态基础上，按识别的技术栈**覆盖/定制**产出路径与门禁
- 既保持速度（复用模板骨架）又保证适配（技术栈特化）

## 原则

- **量身定制**：不硬编码步骤，随项目类型与语言变化
- **门禁可执行**：质量门禁必须是该技术栈可实际运行的命令（test/build）
- **占位符化**：路径用 `<var>` 占位，交给 runner 替换
- **轻量**：产物/门禁按需定制，不过度设计

## Checklist
- [ ] 已确定项目类型与技术栈（auto-detect）
- [ ] 已确定团队组合（team-composer）
- [ ] 已生成适配技术栈的步骤/产出/门禁
- [ ] 产出路径已用占位符化
- [ ] 门禁是技术栈可执行的命令

## 推荐 SubAgent
- coding-agent（据生成的 scaffold 执行任务）