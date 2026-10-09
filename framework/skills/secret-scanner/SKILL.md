---
name: secret-scanner
description: 密钥与敏感信息扫描。扫描代码、配置、日志中的硬编码密钥、API Token、连接串、私钥等，识别并消除敏感泄露风险。
layer: security
tags: [secret, scanner, security, credential, leak]
---

# Secret Scanner — 密钥扫描

## 触发条件
- 提交前、审查时、怀疑有密钥泄露时使用。

## 扫描目标（模式）
- API 密钥：`sk-*`、`ak-*`、`ghp_*`、`AIza*`、`AKIA*`
- Token / Bearer：`Bearer <token>`、JWT
- 连接串：`postgres://user:pass@host`、`mysql://`、`redis://`
- 私钥：`-----BEGIN RSA/EC/OPENSSH PRIVATE KEY-----`
- 通用：`<secret>`、`<password>` 被赋值非占位

## 检查点
- 源码 `.py/.ts/.js/.java` 等
- 配置文件 `.env` / `.env.*`、`config.*`、`docker-compose`
- 日志、测试 fixture、示例代码（示例可豁免但要标注）
- git 历史中是否曾提交过（如已提交需轮换密钥）

## 处理规则
- 已泄露 → 立即提示**轮换密钥**并清除历史
- 必须用密钥 → 用环境变量 `${VAR}` 或 `.env`（gitignore）
- 示例/测试允许 mock 密钥，但需注释说明

## 使用
```bash
bash framework/lib/scripts/infra/secret-scanner.sh
```

## Checklist
- [ ] 无硬编码密钥/Token/连接串
- [ ] 密钥走环境变量，.env 已 gitignore
- [ ] 私钥无提交
- [ ] 日志无敏感字段