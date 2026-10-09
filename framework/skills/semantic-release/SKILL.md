---
name: semantic-release
description: 语义化版本与发布自动化。自动 bump 版本号、生成 CHANGELOG、打 tag。对齐 npm semantic-release / release-please。
layer: workflow
tags: [release, versioning, changelog, semver, automation]
---

# Semantic Release — 语义化版本与发布自动化

## 触发条件

代码准备发布到生产环境时。

## 核心模式

### 1. SemVer 规则

```
MAJOR.MINOR.PATCH

MAJOR: 不兼容的 API 变更
MINOR: 向后兼容的功能新增
PATCH: 向后兼容的 bug 修复

BREAKING CHANGE footer → MAJOR bump
feat: commit              → MINOR bump
fix: commit               → PATCH bump
```

### 2. 自动化流程

```
1. 扫描最近的 commits（上次 tag 以来）
2. 按 Conventional Commits 判断变更级别
3. 确定新版本号 (1.2.3 → 1.3.0)
4. 生成 CHANGELOG
5. git tag v1.3.0
6. 推送 tag
```

### 3. CHANGELOG 格式

```markdown
## [1.3.0] - 2026-10-06

### Features
- feat(auth): add OAuth2 integration (#42)
- feat(api): cursor-based pagination for list endpoints (#38)

### Bug Fixes
- fix(cart): fix total calculation for negative discounts (#40)
- fix(auth): token refresh race condition (#39)

### Refactoring
- refactor(utils): extract date formatting helpers (#41)

### BREAKING CHANGES
- API `/v1/users` response structure changed (see migration guide)
```

### 4. 与 Scaffold 集成

```yaml
post_task:
  steps:
    - goal: "发布 v1.3.0"
      skills: [semantic-release]
      outputs:
        - CHANGELOG.md (updated)
        - version.txt (updated)
        - git tag v1.3.0
```

### 5. 版本文件

不同技术栈的版本文件:

| 技术栈 | 文件 |
|--------|------|
| Node.js | package.json |
| Python | pyproject.toml / __init__.py |
| Rust | Cargo.toml |
| Go | version.go |
| Java | pom.xml / build.gradle |
| Docker | docker-compose.yml 中的 image tag |

## Checklist

- [ ] 版本号遵循 semver
- [ ] CHANGELOG 完整
- [ ] 破坏性变更已标注 BREAKING CHANGE
- [ ] tag 已推送
- [ ] 发布说明包含升级指南（如需要）

## 推荐 SubAgent

- devops-deploy-engineer（版本 bump + tag）
- architect-system-designer（BREAKING CHANGE 判定）
