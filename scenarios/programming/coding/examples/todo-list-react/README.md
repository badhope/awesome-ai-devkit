# 案例：todo-list — React 前端（自适应开发）

> 用 coding 场景的**自适应编排**（识别→组队→生成→执行）完成的 React 前端待办清单应用，验证 coding 能自动适配前端技术栈。

## 背景

- 在已有的 React + TypeScript + Vite 项目中添加「待办清单」功能
- 用户只给一句描述，不感知技术栈——coding 自动完成识别与适配

## 使用的自适应流程

```
1. 识别 → stack-detector 识别 package.json
           结果：frontend + React + vitest
2. 组队 → team-composer → frontend-ui-developer + design-system-architect + test-qa-engineer
3. 生成 → scaffold-generator → adaptive-feature.yaml（产物后缀自动 .tsx、门禁 vitest）
4. 执行 → scaffold-runner + opencode 按 6 步跑通
```

## 自动产物结构

```
src/todo-list/
  types.ts              # 类型定义
  reducer.ts            # 状态 reducer
  TodoList.tsx          # React 组件
  index.ts              # 导出
src/App.tsx / main.tsx  # 应用入口
tests/
  todo-list.unit.test.tsx       # 单元测试
  todo-list.integration.test.tsx # 集成测试
  todo-list.e2e.test.tsx        # E2E 测试
docs/requirements/, docs/design/  # 需求与设计文档
dist/                              # vite build 产物
```

## 技术栈映射（自适应核心）

| 识别项 | 结果 |
|--------|------|
| tech_stack | React + TypeScript + Vite |
| project_type | frontend |
| test_framework | vitest |
| build_tool | vite |
| 产物后缀 | `.tsx` / `.ts`（由 --stack react 自动决定） |
| 质量门禁 | `vite build` + `vitest run` 通过 |

> 换成 Go 项目会自动映射为 `.go` + `go test`，Python 为 `.py` + `pytest`——同一套 scaffold 自动适配任意技术栈。

## 验证结果

- ✅ 识别正确：`project_type=frontend, test_framework=vitest`
- ✅ 真实端到端 6 步全部通过（含单元/集成/E2E 测试 + build）
- ✅ doctor 8/9、pytest 7 passed

## 复盘

- **自适应关键**：`scaffold-runner --stack` 让产物/门禁随技术栈自动变化
- **可复现**：见下方命令
- 产物在 `.temp/`（未入库），仅验证用

## 可复现命令

```bash
python3 scenarios/programming/coding/lib/stack-detector.py --project . --json
python3 scaffolds/scaffold-runner.py --root . --provider opencode
```

> AI生成
