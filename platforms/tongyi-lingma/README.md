# 通义灵码（阿里）接入方式

- **官方格式**：阿里云官方支持 MCP；支持 AGENTS.md / CLAUDE.md 风格指令；企业版可用自定义技能与规则。
- **本仓库**：根 `AGENTS.md` 即可被识别，配合 MCP 使用。

## 接入步骤

```bash
# 在通义灵码中启用 MCP server（官方支持）
# 项目根保留 AGENTS.md（统一指令）
# 按需把场景技能导入 IDE 技能市场/自定义技能
```

## MCP
参考 `mcp/config/` 中平台无关的 server 定义（filesystem / git / github / postgres 等）。

## 说明
以通义灵码**官方文档**为准接入 MCP 与技能；AGENTS.md 作为统一指令来源。

> AI生成
