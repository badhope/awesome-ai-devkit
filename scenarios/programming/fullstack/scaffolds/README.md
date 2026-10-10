# 全栈开发 — 场景脚手架库

> 本目录包含全栈开发场景的 **可直接使用的脚手架配置**。
> 所有脚手架中的 skill 引用均来自通用层 `framework/skills/` 目录（38 个通用技能）。

---

## 使用方式

```bash
# 1. 选择适合的脚手架
cp scenarios/programming/fullstack/scaffolds/<name>.yaml ./scaffold.yaml

# 2. 根据需要微调步骤
vim scaffold.yaml

# 3. 开工 → 执行 → 完工
bash hooks/scripts/pre-task.sh scaffold.yaml
# ... Agent 按 steps[] 逐步执行 ...
bash hooks/scripts/post-task.sh scaffold.yaml
```

---

## 脚手架清单

| 文件 | 适用场景 | 步骤数 | 参与角色 | 引用 Skills |
|------|---------|--------|---------|------------|
| `feature-development.yaml` | 端到端功能开发（需求→部署） | 6 | 6 | 12 |
| `incident-response.yaml` | 故障检测→止损→修复→复盘 | 5 | 4 | 10 |
| `refactoring.yaml` | 代码重构（含安全/性能优化） | 6 | 3 | 10 |

---

## 编写规范

每个脚手架必须遵循以下原则：

1. **Skill 复用通用层** — `framework/skills/` 中的 38 个通用技能
2. **Agent 来自本场景** — `../roles/` 表中定义的角色
3. **每步 outputs 必须有 `contains`** — 产出物的关键验证点（协议字段名）
4. **必须有 `post_task.quality_gates`** — 完工验收标准
5. **失败必须有回退** — `on_failure.retry` + `fallback_skill`

协议文档: [../../../../scaffolds/scaffold-protocol.md](../../../../scaffolds/scaffold-protocol.md)
