---
name: web-browser-vision
description: Web 访问与视觉能力。浏览器自动化（Playwright）、截图分析、OCR、Web 搜索与内容抓取。对齐 OpenClaw 内置 web_search/screenshot 和 Claude Code WebFetch。
layer: capabilities
tags: [web, browser, screenshot, vision, ocr, fetch]
---

# Web, Browser & Vision — 网络访问与图像视觉

## 触发条件

需要查询外部信息、访问网页、分析截图、处理图像内容时。

## 1. 工具清单

| 工具 | 方式 | 用途 |
|------|------|------|
| web_search | CatPaw 内置 | 实时搜索 |
| web_fetch | CatPaw 内置 | URL 内容提取 |
| screenshot | Playwright MCP | 页面截图 |
| image_read | Vision API | 图像理解 |
| OCR | Tesseract / API | 图片文字提取 |
| browser | Playwright MCP | 自动化操作 |

## 2. 集成方式

```yaml
# mcp-config.yaml 启用
playwright:
  enabled: true   # 浏览器自动化 + 截图
```

## 3. 典型用法

```
agent -> web_search: "React 19 new features 2026"
agent -> web_fetch: "https://docs.example.com/api"
agent -> screenshot: "http://localhost:3000"
agent -> image_read: "screenshots/error.png"
```

## 推荐 SubAgent

- frontend-ui-developer（截图视觉回归分析）
- design-system-architect（设计稿对比）
- security-review-engineer（安全页面审计）
