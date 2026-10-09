---
name: documentation-writing
description: 技术文档写作。编写清晰的 README、架构文档、ADR、API 文档与关键注释，面向读者可理解，结构一致、维护友好。
layer: docs
tags: [documentation, docs, writing, readme, adr]
---

# 技术文档写作

## 触发条件
- 写 README、架构决策（ADR）、API 文档、变更说明、复杂逻辑注释时。

## 原则
- **面向读者**：先回答"这是什么/怎么用"，再深入
- **结构一致**：标题层级、代码块、表格统一
- **精简**：一句话能说清的不写一段；不堆砌空话

## 文档类型

### README
```
# 项目名
简介（一句话） · 徽章 · 截图
## 快速开始（clone→install→run→demo）
## 用法示例
## 配置
## 贡献 / 许可证
```
> 同步维护中英文：README.md 与 README_zh.md。

### ADR（架构决策记录）
```
# ADR-<编号>: <标题>
状态: [accepted|proposed|deprecated]
背景：为什么需要决策
决策：选择什么
权衡：备选方案对比
影响：对系统的影响
```

### API 文档
- 端点表（method/path/req/res/错误码）+ OpenAPI

### 代码注释
- 只注释"为什么"（业务原因、约束），不注释"是什么"
- 公共 API 加 docstring/JSDoc

## Checklist
- [ ] 标题/结构一致
- [ ] 快速开始可直接运行
- [ ] 有示例代码
- [ ] 中英文同步（如适用）
- [ ] 无过时/重复信息