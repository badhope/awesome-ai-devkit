# 场景层（Scenarios）

> 框架按「场景」组织上层结构。每个场景是一类开发任务的集合，场景内部的组件（agent / skill / tool / hook）可独立使用也可组合。
>
> **场景数量不限**，随需求增长。初始先铺「编程开发」，其他场景按需添加。

## 场景地图

```
scenarios/
├── programming/          # 编程开发 ← 当前主战场
│   ├── coding/           # 通用编程底座（跨语言，可被其他子场景继承）
│   ├── fullstack/        # Web 全栈
│   ├── mobile/           # 移动 App
│   ├── ml-native/        # AI 原生应用
│   ├── cli-tool/         # 命令行工具
│   └── library/          # 开源库 / SDK
├── data-engineering/     # 数据工程 ⚠️ 原型阶段
├── creative-content/     # 创意内容（PPT、文档、视频）⚠️ 原型阶段
├── devops/               # DevOps、基础设施、SRE ⚠️ 原型阶段
├── research/             # 科研探索 ⚠️ 原型阶段
└── business-ops/         # 业务运营（CRM、ERP、电商）⚠️ 原型阶段
```

## 原型阶段场景

以下场景目前处于规划中原型（仅有 `_index.md`，尚未填充完整内容），**建议使用 `programming/fullstack` 作为基础参考**进行扩展：

- `creative-content/` — 创意内容
- `data-engineering/` — 数据工程
- `devops/` — DevOps / SRE
- `research/` — 科研探索
- `business-ops/` — 业务运营

## 场景内部结构

```
scenarios/<name>/
├── _index.md             # 场景定义：描述、角色组合、推荐技能
├── agents/               # 场景专属角色
├── skills/               # 场景专属技能
├── tools/                # 场景专属工具
├── workflows/            # 场景专属流水线
└── examples/             # 已完成的项目案例
```

## 优势

1. **灵活裁剪**：做移动项目时只看 `programming/mobile/`，不用理解全框架
2. **按需扩展**：新项目类型 → 新建场景目录，不影响其他
3. **差异化管理**：不同场景可使用不同的角色集合、不同的 hooks、不同的技能包
4. **知识沉淀**：每个场景的 `examples/` 积累已完成项目，未来复用

## 场景元数据格式

```yaml
# scenarios/programming/_index.md
name: 编程开发
description: 各类编程任务的通用框架
target_users: [全栈工程师, 移动端工程师, 工具链开发者]
lifecycle_stage: active  # active | incubating | archived

# 推荐角色组合
recommended_roles:
  minimal: [tech-lead, senior-developer, qa-engineer]
  full:    [product-manager, tech-lead, frontend-developer, backend-developer, qa, devops, code-reviewer]

# 推荐技能
recommended_skills:
  api-development: true
  database-design: true
  cicd-pipeline: true

# 该场景的默认 hooks
hooks:
  before_action:
    - auth-check
    - rate-limit
  after_action:
    - log-writer
```

## 场景间协作

不同场景可通过共享角色和技能协作。例如：

- 一个 AI 原生项目 → `programming/ml-native/` 
  - 复用 `programming/fullstack/` 中的前端/后端 agent
  - 额外引入 `programming/ml-native/` 的 ml-engineer
  - 可选引入 `data-engineering/` 的数据处理技能
