---
name: dependency-audit
description: 依赖审计与供应链安全。多语言依赖漏洞自动扫描（pip-audit/npm audit/govulncheck/cargo audit/OWASP）、CVSS 评级解读、自动修复策略、SBOM 生成、与 quality_gate 和 CI 集成。
layer: security
tags: [dependency, audit, supply-chain, security, sbom, cve, vulnerability]
---

# Dependency Audit — 依赖审计与供应链安全

## 触发条件

- 安全审查阶段（security-review-engineer 要求时）
- 切换分支后（hooks on_branch_change 自动触发）
- 每周定期审计（CI schedule 或 cron）
- Agent 退出前（on_agent_end 快速检查）
- 新依赖安装后

## 多语言依赖审计工具链

| 技术栈 | 审计工具 | 安装方式 | 一行命令 |
|--------|---------|---------|---------|
| Python | pip-audit | `pip install pip-audit` | `pip-audit --strict --desc` |
| Python | safety | `pip install safety` | `safety check` |
| Node.js | npm audit | 内置 | `npm audit --omit=dev` |
| Go | govulncheck | `go install golang.org/x/vuln/cmd/govulncheck@latest` | `govulncheck ./...` |
| Rust | cargo audit | `cargo install cargo-audit` | `cargo audit` |
| Java | OWASP | Docker | `docker run ... owasp/dependency-check` |

## CVSS 评级与处理策略

| 等级 | CVSS | 修复时限 | 阻断合并 |
|------|------|---------|---------|
| CRITICAL | 9.0–10.0 | 立即 | ✓ |
| HIGH | 7.0–8.9 | 24h | ✓ |
| MEDIUM | 4.0–6.9 | 1 周 | ✗ |
| LOW | 0.1–3.9 | 1 月 | ✗ |

## 自动修复策略

低风险：自动 `npm update` / `pip install --upgrade` / `cargo update`
中风险：通知 + 建议创建修复 PR
高风险/阻断：阻止合并 + 要求立即修复

## 与 quality_gate 集成

```yaml
post_task:
  quality_gates:
    - "依赖审计通过: 0 CRITICAL, 0 HIGH"
    - "SBOM 已生成"
    - "自动修复 commit 已提交（低风险项）"
```

## Checklist

- [ ] 工具链已安装（pip-audit / npm audit / govulncheck）
- [ ] lockfile 已生成
- [ ] 审计脚本可执行
- [ ] CI security job 已配置
- [ ] CRITICAL/HIGH 阻断 PR 合并
- [ ] 自动修复仅限 LOW 风险
