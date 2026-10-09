---
name: auto-heal
description: 自动修复引擎。作为 loop-verification 的修复 executor，检测代码质量问题并自动修复：格式问题、缺失依赖、简单测试失败、安全漏洞模式、文档缺失。严格安全边界，不修改业务逻辑和架构决策。
layer: infrastructure
tags: [auto-heal, auto-fix, repair, code-quality, security, self-healing]
---

# Auto Heal — 自动修复引擎

## 触发条件

| 触发源 | 场景 | 条件 |
|--------|------|------|
| loop-verification | 质量门禁检查失败 | 门禁状态为 FAIL + auto_fixable |
| hooks | 文件写入后检测 | post_write 触发 lint/安全扫描 |
| 手动调用 | 用户指令 | `/auto-heal` 或 "自动修复" |
| devkit-doctor | 健康检查发现可修复问题 | doctor 输出 fixable_issues > 0 |

## 修复能力矩阵

### 1. 格式问题 → 自动 Lint/Format

**检测**：linter 报告 style/import-order/trailing-space 等非逻辑错误

**修复动作**：
```bash
# Node.js
npx eslint --fix <files>
npx prettier --write <files>

# Python
ruff check --fix <files>
ruff format <files>

# Go
gofmt -w <files>
goimports -w <files>

# Rust
cargo fmt
```

**安全限制**：
- 仅修改空白、导入排序、分号等无关代码逻辑的部分
- 不修改变量命名（即使 linter 建议更名的情况需人工确认）
- 修复后 git diff 不包含非空白字符变更时视为纯格式修复

---

### 2. 缺失依赖 → 自动安装

**检测**：import 语句引用未安装的模块 / ModuleNotFoundError / resolving dependency failed

**修复动作**：
```bash
# Node.js - 检测 package.json 安装状态
npm install <package>        # runtime dep
npm install -D <package>    # dev dep

# Python - 检测虚拟环境安装状态
pip install <package>

# Go
go get <package>
```

**安全限制**：
- 不自动升级到主版本（可能有破坏性变更）
- 锁定版本号写入依赖文件
- 不安装未经验证的第三方包（检查下载量/星标/更新频率）
- 安装后运行 `npm audit` / `pip audit` 确认无已知漏洞

---

### 3. 测试失败 → 分析并尝试修复

**检测**：测试运行输出包含 FAIL/FAILED/assertion_error

**修复流程**：
```
1. 解析测试输出，定位失败文件和行号
2. 区分失败类型：
   a. 测试代码过时（被测代码已修改但测试未更新）
   b. 被测代码有 bug（实现不符合预期）
   c. 环境问题（端口占用、数据库连接、未 mock）
3. 仅修复类型 (a)——测试代码与实现不匹配
4. 类型 (b)(c) 不上报，标记为需人工介入
```

**安全限制**：
- 不修改断言逻辑（降低测试标准不算修复）
- 不跳过或删除失败的测试
- 修复后必须运行完整测试套件确认不引入新失败

---

### 4. 安全漏洞 → 替换不安全代码模式

**检测**：静态分析发现以下内容

| 漏洞类型 | 不安全模式 | 安全替换 |
|---------|-----------|---------|
| SQL 注入 | 字符串拼接 SQL | 参数化查询 / ORM |
| XSS | innerHTML / v-html | textContent / 自动转义模板 |
| 硬编码密钥 | password = "xxx" | getenv("SECRET") |
| 弱加密 | MD5/SHA1 用于密码 | bcrypt / argon2 |
| 路径拼接 | open(user_input) | 路径验证 + 白名单 |
| eval 执行 | eval(user_input) | JSON.parse / 类型化解析 |

**修复动作**：
```python
# 修复前（不安全）
query = f"SELECT * FROM users WHERE id = {user_id}"

# 修复后（安全）
query = "SELECT * FROM users WHERE id = ?"
cursor.execute(query, (user_id,))
```

**安全限制**：
- 不做语义级别的修复（如重写认证流程）
- 仅执行一对一的模式替换
- 修复后标记 code review 待审

---

### 5. 文档缺失 → 扫描并生成文档

**检测**：公开 API / 函数缺少 docstrings 或 README 未覆盖新功能

**修复动作**：
```
1. 扫描项目公开接口（无前导下划线的函数/类）
2. 检测缺少的 docstring/google-style/pep257 格式的文档注释
3. 基于函数签名、类型注解、调用模式生成模板文档
4. 检查 README.md 是否需要更新（新功能入口）
```

**生成模板**（Python 示例）：
```python
def authenticate_user(username: str, secret: str) -> AuthResult:
    """
    认证用户凭据并返回认证结果。

    Args:
        username: 用户唯一标识符。
        secret: 用户提供的密钥/密码。

    Returns:
        AuthResult: 包含认证状态和令牌的结果对象。

    Raises:
        AuthError: 当凭据无效或账户被锁定时抛出。
    """
```

**安全限制**：
- 生成文档标记为 `[AUTO_GENERATED]`，提示人工审阅
- 不覆盖已有文档（仅补充缺失部分）
- 不对内部实现细节生成文档

---

## 修复优先级

```
┌─────────────────────────────────────────────┐
│  Priority 1: 安全漏洞（即时修复）              │
│  → 硬编码密钥、注入漏洞、弱加密                │
│  → 不等待用户确认，修复后报警                  │
├─────────────────────────────────────────────┤
│  Priority 2: 功能正确性（尽快修复）             │
│  → 编译错误、导入失败、类型错误                │
│  → 修复失败上报 loop-verification              │
├─────────────────────────────────────────────┤
│  Priority 3: 代码质量（批次修复）               │
│  → Lint 警告、格式问题、复杂度阈值             │
│  → 合并同类修复，减少交互次数                  │
├─────────────────────────────────────────────┤
│  Priority 4: 文档（顺带修复）                   │
│  → 缺失 docstring、README 过期                │
│  → 作为其他修复的附带产出                      │
└─────────────────────────────────────────────┘
```

---

## 修复范围限制（绝对红线）

auto-heal **严禁修改**以下任何内容：

| 禁止修改项 | 原因 | 处理方式 |
|-----------|------|---------|
| 业务逻辑 | 自动修复可能引入语义错误，改变程序行为 | 上报 loop-verification 需人工修复 |
| 架构决策 | 涉及系统级设计考量，不能自动决策 | 记录建议但不修改 |
| 数据库 Schema | 迁移需要严格版本控制和 review | 生成迁移建议文件，不执行 |
| 测试断言逻辑 | 修改断言等于降低测试标准 | 标记为需人工 review |
| 配置文件（业务相关） | API 地址、功能开关等影响运行时行为 | 仅修复格式，不改值 |
| algorithm 选择 | 涉及性能和正确性权衡 | 不替换算法 |

**安全边界——绝不触碰**：
- `node_modules/` 目录
- `vendor/` 目录
- `.venv/` / `venv/` 虚拟环境
- `generated/` / `dist/` / `build/` 输出目录
- `.git/` 内部目录
- 任何 lock 文件（package-lock.json, Cargo.lock 等）
- 三方可执行二进制文件

---

## 与 loop-verification 集成

### 角色定位

auto-heal 是 loop-verification 循环中的**修复 executor**：

```
loop-verification 循环:
  ┌──────────────────────────────────────────────┐
  │ 1. 执行质量门禁检查（doctor + gates）          │
  │ 2. 收集失败项 → 分类 auto_fixable / manual    │
  │ 3. 调用 auto-heal 修复 auto_fixable 项        │  ← 本次执行
  │ 4. 验证修复效果（重跑对应检查）                 │
  │ 5. 循环直到全部通过或达到 max_loops            │
  └──────────────────────────────────────────────┘
```

### 调用约定

loop-verification 通过以下接口调用 auto-heal：

```bash
# 自动修复传入的失败列表
bash framework/lib/scripts/core/auto-heal.sh --issues <issues.json>

# issues.json 格式
{
  "round": 1,
  "issues": [
    {
      "type": "lint",
      "severity": "warning",
      "file": "src/auth/handler.ts",
      "description": "Missing semicolon",
      "auto_fixable": true,
      "fix_command": "npx eslint --fix src/auth/handler.ts"
    },
    {
      "type": "missing_dependency",
      "severity": "error",
      "package": "jsonwebtoken",
      "auto_fixable": true
    }
  ]
}
```

### 修复结果回传

auto-heal 完成后输出修复报告：

```json
{
  "round": 1,
  "attempted": 5,
  "succeeded": 4,
  "failed": 1,
  "details": [
    {
      "issue_id": "lint-001",
      "status": "fixed",
      "method": "eslint --fix",
      "file_changed": "src/auth/handler.ts"
    },
    {
      "issue_id": "dep-001",
      "status": "fixed",
      "method": "npm install jsonwebtoken",
      "package": "jsonwebtoken@9.0.0"
    },
    {
      "issue_id": "test-002",
      "status": "skipped",
      "reason": "断言逻辑修改超出安全范围，需人工介入"
    }
  ]
}
```

---

## 使用示例

### 示例 1：自动修复 Lint 错误

```bash
# 检测到 ESLint 错误
$ bash framework/lib/scripts/core/auto-heal.sh --project ./my-app

[auto-heal] 项目类型: Node.js (TypeScript)
[auto-heal] 运行: npx eslint . --fix
[auto-heal] 修复完成：
  - 12 个文件已修复（导入排序 + 尾随空格）
  - git diff 确认：仅空白和 import 顺序变更
[auto-heal] 状态: SUCCESS (exit 0)
```

### 示例 2：检测需人工审查的变更

```bash
# 检测到安全修复需要语义变更
$ bash framework/lib/scripts/core/auto-heal.sh --project ./my-app --issues issues.json

[auto-heal] 项目类型: Python
[auto-heal] 修复安全漏洞: SQL 注入 - 替换为参数化查询
[auto-heal] git diff 检测到实质性代码变更:
  - src/db/query.py: 4 行逻辑变更（非纯格式）
[auto-heal] 状态: NEEDS_REVIEW (exit 1)
[auto-heal] 说明：安全修复涉及代码逻辑修改，已标记 code review
```

### 示例 3：Dry Run 模式

```bash
# 只检测不修复
$ bash framework/lib/scripts/core/auto-heal.sh --project ./my-app --dry-run

[auto-heal] DRY RUN 模式（仅检测）
[auto-heal] 项目类型: Go
[auto-heal] 发现 3 个可修复问题：
  - 5 个文件未通过 gofmt（可通过 `gofmt -w` 修复）
  - 2 个未使用导入（可通过 `goimports -w` 修复）
[auto-heal] 状态: DRY_RUN_COMPLETE (exit 0)
```

### 示例 4：在 loop-verification 中的调用

```bash
# Round 1: 门禁检查发现 2 项可自动修复
$ python devkit-doctor.py --format json --root ./project > round1_result.json

$ bash framework/lib/scripts/core/auto-heal.sh --issues round1_result.json
[auto-heal] Round 1: 尝试修复 2 项
  → Lint (src/api.ts): eslint --fix → 已修复
  → Missing dep (zod): npm install zod → 已安装
[auto-heal] 修复完成。重跑门禁验证...

# Round 2: 重跑 doctor 确认修复
$ python devkit-doctor.py --format json --root ./project
→ 所有门禁通过，退出循环
```

---

## Checklist

- [ ] 修复前确认问题类型在修复能力范围内
- [ ] 安全修复优先执行（不等待确认）
- [ ] 修复后运行相关测试确认不引入回归
- [ ] 纯格式/导入排序修复：自动提交或通过
- [ ] 实质性代码变更修复：输出警告，需人工标记 review
- [ ] 严格遵守修复范围限制（不碰业务逻辑、架构决策、数据库 Schema）
- [ ] 安全边界：不修改 node_modules、vendor、generated、lock 文件
- [ ] loop-verification 集成正确（修复后重跑对应检查确认效果）
- [ ] 修复结果格式符合 loop-verification 报告要求（attempted/succeeded/failed）
- [ ] git diff 分析正确区分纯格式变更和逻辑变更
- [ ] dry-run 模式只输出检测信息不执行任何修复操作

## 推荐 SubAgent

- test-qa-engineer（测试失败诊断与回归验证）
- security-review-engineer（安全漏洞修复的 review 与确认）
- code-reviewer（逻辑变更的人工 review 判定）
- devops-deploy-engineer（依赖变更的 CI 集成验证）

## 与 Other Skills 的关系

| Skill | 关系 |
|-------|------|
| loop-verification | auto-heal 是其修复 executor 组件 |
| linter-formatter | auto-heal 复用 lint/format 工具 |
| security-governance | 安全规则复用 security skill 的定义 |
| devkit-doctor | 依赖 doctor 的检查结果作为修复输入 |
| context-compression | 修复过程中上下文增长，可能需要联动压缩 |
