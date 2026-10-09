---
name: linter-formatter
description: Lint 和格式化集成。代码写入后自动触发 lint + format（通过 hooks），对齐 Claude Code 的自动化 hooks 模式。支持 ESLint/Prettier/Biome/Ruff/gofmt/clippy。2026 主流：Biome 取代部分 ESLint+Prettier 场景。
layer: quality
tags: [lint, format, hooks, automation, code-quality]
---

# Linter & Formatter — 自动化代码质量

## 触发条件

代码写入/修改后自动触发（通过 hooks 配置），或手动运行时。

## 核心模式

### 1. 技术栈 → 工具映射

| 技术栈 | Linter | Formatter | 配置文件 |
|--------|--------|-----------|---------|
| TypeScript/JS | ESLint / Biome | Prettier / Biome | .eslintrc.* / biome.json |
| Vue / Svelte | ESLint + vue plugin | Prettier | .eslintrc.vue.* |
| Python | Ruff / Flake8 | Ruff / Black / isort | pyproject.toml |
| Go | golangci-lint | gofmt | .golangci.yml |
| Rust | Clippy | rustfmt | rustfmt.toml |
| Java | Checkstyle | google-java-format | checkstyle.xml |
| CSS/SCSS | Stylelint | Prettier | .stylelintrc |
| SQL | SQLFluff | sql-formatter | .sqlfluff |
| Shell | ShellCheck | shfmt | .shellcheckrc |

### 2. Hooks 集成

代码写入后自动触发（与 Awesome AI DevKit hooks 系统配合）：

```yaml
# hooks/config.yaml
hooks:
  post_write:
    - script: "hooks/scripts/auto-lint.sh"
      description: "文件写入后自动 lint + format"
```

触发规则：
- `.ts/.tsx/.js/.jsx` → `npx eslint --fix` + `npx prettier --write`
- `.py` → `ruff check --fix` + `ruff format`
- `.go` → `gofmt -w` + `golangci-lint run`
- `.rs` → `cargo fmt -- --check` + `cargo clippy`
- `.sql` → `sqlfluff fix`

### 3. 安全规则（2026 Lint 增强）

强制规则：
- 禁止 console.log/error 在 production 代码（env check）
- 禁止使用 any / 类型断言（除非标注 @ts-ignore 理由）
- import 排序和去未使用变量
- 复杂度阈值：单个函数不超过 15 分支
- 文件长度警告：> 400 行给出拆分建议
- 模块循环依赖检测（2026 主流要求）
- 导出成员按字母序排列（可读性）

### 4. 与 scaffold.yaml 集成

```yaml
steps:
  - goal: "实现模块 X"
    outputs:
      - src/module/x.py
    quality_gate: "ruff check src/module/x.py 通过"

post_task:
  quality_gates:
    - "ESLint 0 errors（warnings 不阻塞）"
    - "Prettier formatted"
```

## Checklist

- [ ] 提交前 lint 0 errors
- [ ] 格式化规则与团队一致
- [ ] CI 中运行 lint（不只本地）
- [ ] IDE 配置文件共享（.settings/ 或 root）

## 推荐 SubAgent

- security-review-engineer（安全 lint 规则检查）
- devops-deploy-engineer（CI 集成）
