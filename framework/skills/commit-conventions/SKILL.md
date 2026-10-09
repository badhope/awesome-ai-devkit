---
name: commit-conventions
description: Conventional Commits 提交规范。统一的提交信息格式，配合自动 changelog 与语义化版本，保证提交历史清晰、可追溯。
layer: engineering
tags: [git, commit, conventional-commits, changelog, semantic-version]
---

# 提交规范（Conventional Commits）

## 触发条件
- 每次提交代码时遵循本规范，保持提交历史可读、可自动发布。

## 提交格式
```
<type>(<scope>): <description>
```
- `type` 必填，`scope` 可选（模块/场景）
- `description` 用祈使句、简洁、≤72 字符

## Type 类型
| type | 用途 |
|------|------|
| `feat` | 新功能 |
| `fix` | 修复 bug |
| `docs` | 仅文档 |
| `refactor` | 重构（不改功能） |
| `test` | 加/改测试 |
| `chore` | 杂务/构建/依赖 |
| `ci` | CI/CD |
| `perf` | 性能优化 |
| `style` | 格式/风格（无逻辑） |
| `revert` | 回滚 |

## 破坏性变更
```
feat(api)!: 重命名 users 端点
```
加 `!`，并在 body 注明 `BREAKING CHANGE:`。

## 示例
- `feat(auth): 增加刷新令牌接口`
- `fix(bootstrap): 用 python 而非 python3 修复 Windows`
- `docs(readme): 补充平台支持说明`

## 提交颗粒
- **一个提交一件事**（focused、single-purpose）
- 不混搭 修复+重构+文档 于一个提交

## 与工具联动
- `git-workflow` / `semantic-release` 依此自动生成 changelog 与版本号
- 提交前先 `git add` 相关文件，避免无关变更入库

## Checklist
- [ ] 格式 `<type>(<scope>): 描述`
- [ ] 一句话、≤72 字符
- [ ] 单一职责
- [ ] 破坏性变更已标注 `!` / `BREAKING CHANGE`