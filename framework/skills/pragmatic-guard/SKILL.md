---
name: pragmatic-guard
description: 防「AI 坏毛病」强制守门：重复造轮 / 冗余文件 / 虚假实现 / 过度设计 / 业务不合现实。在编码实现与提交前，强制用 pragmatic-guard.py 扫描并整改，避免产出"好看但无用/假装完成/过度抽象/不合业务逻辑"的代码。当 AI 写代码时自动触发，作为完工门禁之一。
layer: quality
tags: [pragmatic, anti-bullshit, quality-gate, guard, minimal]
---

# Pragmatic Guard — 防 AI 坏毛病守门

## 触发条件

**每次编码任务**在"实现完成、提交/完工前"自动执行。防止 AI 写出重复造轮、冗余、虚假、过度设计、不合业务的代码。

## 核心能力

### 自动运行门禁

```bash
# 扫描项目，检测 5 类问题
python3 framework/lib/scripts/quality/pragmatic-guard.py --project . --json

# 仅检测某类
python3 framework/lib/scripts/quality/pragmatic-guard.py --project . --check fake --check redundancy
```

**退出码**：`0` = 通过，`1` = 发现问题（**必须整改后才能提交/完工**）。

### 5 类坏毛病 → 检测 → 整改

| 坏毛病 | 检测信号 | 整改要求 |
|--------|---------|---------|
| **重复造轮子** | 已有库/框架可完成却手写；全仓库相似实现 | 实现前先查 `package.json`/`go.mod`/`requirements` 是否已有依赖；复用现有工具，不手写 |
| **冗余文件** | 空文件、无意义命名（util/dummy/stub）、未被引用文件 | 删除无用文件；新增文件必须被 import/require 引用 |
| **虚假实现** | `pass`/`TODO`/`NotImplementedError`/空函数体/`return None #TODO` | 不写占位符；未实现的功能要么真做，要么不做并说明 |
| **过度设计** | 过度工厂/无用配置类/冗余命名/永假分支 | YAGNI + KISS：不加用不到的抽象、泛化、参数、死分支 |
| **业务不合现实** | 魔法数字（>4 位无命名）、演示字符串（hello/world）、try 无 catch | 数字命名常量；真实业务命名；异常必须处理 |

## 执行流程

```
1. 编码实现完成 → 运行 pragmatic-guard.py --project . --json
2. 若 FAIL → 逐条整改（删冗余/补实现/去过度设计/命名常量/加异常处理）
3. 重跑直到 PASS
4. 再进入测试 / 提交阶段
```

## 原则

- **机制强制**：不只靠提示，用可执行脚本 + 退出码阻断不合格产物
- **真实优先**：宁可不做，不可"假装完成"（pass/TODO 冒充）
- **最小可用**：够用就好，拒绝无意义的抽象和冗余
- **符合现实**：业务逻辑、命名、取值必须贴近真实使用场景

## Checklist
- [ ] 实现前已查复用（库/框架/现有代码）
- [ ] 无空文件、无未引用文件、无占位命名
- [ ] 无 pass/TODO/NotImplemented/空函数体
- [ ] 无过度设计信号（过度工厂/死分支/名词堆叠）
- [ ] 魔法数字已命名常量、无演示字符串、异常已处理
- [ ] `pragmatic-guard.py --project .` 返回 exit 0

## 推荐 SubAgent
- code-review（实现后交叉审查）
- linter-formatter（格式与静态检查）