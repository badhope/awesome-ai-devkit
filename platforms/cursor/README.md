# Cursor 接入方式

- **官方格式**：`.cursor/rules/*.mdc`（新版 Rules，frontmatter 含 `description`/`globs`/`alwaysApply`）；旧版 `.cursorrules`；两者兼容；根 `AGENTS.md` 亦被支持。
- **本仓库提供**：示例规则 `examples/awesome-devkit.mdc`（可复制到项目 `.cursor/rules/`）。

## 接入步骤

```bash
mkdir -p .cursor/rules
cp platforms/cursor/examples/awesome-devkit.mdc .cursor/rules/awesome-devkit.mdc
```

> 也可以用旧方式：把仓库根 `.cursorrules` 复制到项目根（Cursor 自动读取）。

## 说明

Cursor 的 `.mdc` 规则支持 glob 限定作用范围与 `alwaysApply`。把框架核心规则作为 `alwaysApply` 规则，场景规则按目录应用即可。

> AI生成
