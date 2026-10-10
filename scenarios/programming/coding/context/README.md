# 通用编程场景 — 项目上下文共享层

> Awesome AI DevKit Layer 10 (Context) 在通用编程场景的实现。

## 文件清单

| 文件 | 作用 | 何时读写 |
|------|------|---------|
| `project.yaml` | 项目级元数据（语言、技术栈、授权 Agent、路径约束） | Agent 启动加载，运行中只读 |
| `architecture.md` | 所有 ADR（架构决策记录） | Agent 按 topic 检索 |
| `logs/sessions/*.jsonl` | 会话运行日志 | Agent 结束时写入 |

## 使用方式

```bash
# 初始化项目上下文
cp context/project.template.yaml context/project.yaml
# 编辑 project.yaml，填写语言、测试框架、编码约定、Agent 列表
```

- **Start**: 自动注入 `project.yaml` 摘要
- **During**: Agent 检查 `stack` / `allowed_paths`
- **End**: 写入会话日志；发现新决策以 ADR 追加到 `architecture.md`

## 安全约束

| 类别 | 规则 |
|------|------|
| 写入 | 仅通过 git 提交写入；运行时只读 |
| 密钥 | 绝不放 context/；用环境变量或 vault |
| 日志 | sessions/*.jsonl 保留 50 个，自动轮转 |
| 范围 | denied_paths 列出的目录 Agent 拒绝操作 |
