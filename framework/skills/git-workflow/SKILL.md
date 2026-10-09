---
name: git-workflow
description: Git 智能工作流增强。智能 commit message 生成、分支命名规范、PR 描述自动编写、冲突解决策略。所有开发团队的通用需求。
layer: workflow
tags: [git, commit, branch, pull-request, workflow]
---

# Git Workflow — Git 工作流增强

## 触发条件

代码开发完成后准备提交时，或创建 PR 时。

## 核心模式

### 1. Commit Message 规范（Conventional Commits）

```
<type>(<scope>): <description>

[optional body]

[optional footer]

type:
  feat:     新功能
  fix:      修复 bug
  docs:     文档变更
  style:    格式修改（不影响代码运行）
  refactor: 重构
  perf:     性能优化
  test:     测试
  chore:    构建/工具变更
  ci:       CI 配置
  revert:   回滚
```

### 2. 智能生成规则

```
Agent 根据 diff 自动判断:
  +++ new feature file    → feat
  +++ test file           → test
  --- bug fix             → fix
  -M utils refactor only  → refactor
  +++ README              → docs
  .github/workflows/*.yml → ci

生成格式:
  feat(auth): add JWT refresh token implementation
  fix(cart): handle empty cart checkout edge case
  refactor(pagination): extract offset/cursor logic into shared util
```

### 3. 分支命名规范

```
feature/<ticket>-short-desc    → feat
bugfix/<ticket>-short-desc     → fix
hotfix/<ticket>-short-desc     → critical fix
chore/<desc>                   → maintenance
refactor/<desc>                → refactoring

例: feature/PROJ-123-user-auth
    fix/PROJ-456-cart-total-calculation
```

### 4. PR 模板

```markdown
## Summary
<!-- 1-3 sentences what changed -->

## Motivation
<!-- Why this change? -->

## Changes
- [ ] Breaking change
- [ ] New feature
- [ ] Bug fix
- [ ] Refactor
- [ ] Documentation

## Testing
<!-- How was this tested? -->

## Checklist
- [ ] Lint passes
- [ ] Tests added/updated
- [ ] Documentation updated
```

### 5. Commit 粒度

```
一个 commit = 一个逻辑变更
✗ 不要 "feat: add auth + fix cart bug + update docs" (3 commits)
✓ 拆分为 3 个独立 commit
✓ 每个 commit 可以独立 revert
✓ 历史干净 → git blame 好用
```

## Checklist

- [ ] commit message 遵循 Conventional Commits
- [ ] 分支命名含 ticket ID（如有）
- [ ] 一个 commit 一个逻辑变更
- [ ] 提交前运行 lint + test
- [ ] PR 描述完整

## 推荐 SubAgent

- backend-api-developer（feat/fix commits）
- devops-deploy-engineer（CI 相关 commits）
- architect-system-designer（refactor commits）
