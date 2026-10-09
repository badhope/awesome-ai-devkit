#!/usr/bin/env python3
"""
Awesome AI DevKit — Pragmatic Guard v1.1
防「AI 坏毛病」强制门禁脚本：重复造轮 / 冗余文件 / 虚假实现 / 过度设计 / 业务不合现实。

用法:
  python3 pragmatic-guard.py --project <dir>            # 扫描项目（默认当前目录）
  python3 pragmatic-guard.py --project <dir> --check fake --check redundancy
  python3 pragmatic-guard.py --json                  # JSON 输出（供 CI/门禁消费）

退出码:
  0 = 全部通过
  1 = 发现问题（阻断提交/完工）
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


# 排除目录：依赖/构建/版本控制/框架层自身/测试/文档
SKIP_DIRS = {
    "node_modules", ".git", ".venv", "venv", "__pycache__", "dist", "build",
    ".next", "target", ".temp", ".pytest_cache", ".ruff_cache", "logs",
    "framework",           # 框架层自身（能力仓库，非项目业务代码）
    "docs",                # 文档
    "tests",               # 测试（故意构造的边界用例不算坏毛病）
    "examples",            # 示例
    "scripts", "hooks", "platforms", "scaffolds", "rules", "experts",
}
TEST_FILE_PATTERNS = (
    re.compile(r"^test_"), re.compile(r"_test\.py$"), re.compile(r"\.test\.(ts|tsx|js|jsx)$"),
    re.compile(r"(spec|test)\.(ts|tsx|js|jsx|go|rs)$"), re.compile(r"_test\.go$"),
)

# ── 1. 虚假实现 ──────────────────────────────────────────
# 空函数体：def/function/func/fn X(...): 后紧跟 pass 或 ...
FAKE_EMPTY_FN = re.compile(
    r"\b(def|function|func|fn)\s+(\w+)\s*\([^)]*\)\s*:\s*\n\s*(pass|\.\.\.)\s*(\n|$)",
    re.MULTILINE,
)
# 单行占位标记
FAKE_MARKERS = [
    re.compile(r"\braise\s+NotImplementedError\b"),
    re.compile(r"\bTODO\b"), re.compile(r"\bFIXME\b"), re.compile(r"\bXXX\b"),
    re.compile(r"return\s+None\s*#\s*(TODO|stub|未实现|not.?implemented|占位)", re.IGNORECASE),
]

# ── 2. 冗余文件 ──────────────────────────────────────────────
EMPTY_FILE_EXTS = {".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs",
                   ".java", ".kt", ".swift", ".rb", ".cpp", ".c"}
USELESS_NAME_PARTS = ["placeholder", "dummy", "stub", "fake_", "temp_", "tmp_", "useless", "delete_me"]

# ── 3. 过度设计信号 ──────────────────────────────────────────
OVERENGINEER_PATTERNS = [
    re.compile(r"AbstractFactory|BaseFactory|FactoryFactory"),
    re.compile(r"class\s+\w+(Manager|Registry|Service)Manager\b", re.IGNORECASE),
    re.compile(r"\b\w+_\w+_(util|helper)\b", re.IGNORECASE),
    re.compile(r"if\s+False\s*:"),
]

# ── 4. 业务不合现实 ──────────────────────────────────────────
MAGIC_NUMBER = re.compile(r"(?<![\w.])\d{5,}(?![\w.])")
TOY_STRINGS = ["hello", "world", "foobar", "test123", "asdf", "lorem", "dummy_data"]
STRING_RE = re.compile(r"['\"][^'\"]*['\"]")


def _is_test_file(path: Path) -> bool:
    name = path.name
    stem = path.stem
    return any(p.search(name) or p.search(stem) for p in TEST_FILE_PATTERNS)


def _should_scan(root: Path, p: Path) -> bool:
    """是否扫描该文件：非跳过目录、非测试文件、后缀在源码列表。"""
    rel = p.relative_to(root)
    if any(part in SKIP_DIRS for part in rel.parts):
        return False
    if p.suffix.lower() not in EMPTY_FILE_EXTS:
        return False
    if _is_test_file(p):
        return False
    return True


def _source_files(root: Path) -> list:
    return [p for p in root.rglob("*") if p.is_file() and _should_scan(root, p)]


def _strip_comments(line: str) -> str:
    """去除行内注释（# 和 //）。"""
    if "#" in line:
        line = line.split("#", 1)[0]
    elif "//" in line and not line.strip().startswith(("http", "://")):
        line = line.split("//", 1)[0]
    return line


def _in_string(text: str, pos: int) -> bool:
    """判断文本某位置是否在字符串字面量内。"""
    # 简易：扫描到 pos 的引号配对数
    before = text[:pos]
    return before.count('"') % 2 == 1 or before.count("'") % 2 == 1


def check_fake(root: Path) -> list:
    issues = []
    for p in _source_files(root):
        rel = str(p.relative_to(root)).replace(os.sep, "/")
        text = p.read_text(encoding="utf-8", errors="ignore")
        # 空函数体（pass）
        for m in FAKE_EMPTY_FN.finditer(text):
            issues.append(f"[fake] {rel} 空函数体/仅占位: {m.group(0).strip()[:50]}")
        # 未实现标记（跳过字符串与注释）
        for i, line in enumerate(text.splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith(("#", "//", "/*", "*", "--")):
                continue
            for pat in FAKE_MARKERS:
                if pat.search(line):
                    issues.append(f"[fake] {rel}:{i} 占位/未实现: {stripped[:60]}")
                    break
    return issues


def check_redundancy(root: Path) -> list:
    issues = []
    texts = {}
    for p in _source_files(root):
        texts[p] = p.read_text(encoding="utf-8", errors="ignore")
    rels = {str(p.relative_to(root)).replace(os.sep, "/") for p in texts}
    all_text = "\n".join(texts.values())
    entry_stems = {"index", "app", "main", "__init__", "cli", "server", "manage"}
    for p, text in texts.items():
        rel = str(p.relative_to(root)).replace(os.sep, "/")
        if not text.strip():
            issues.append(f"[redundant] 空文件: {rel}")
            continue
        base = p.stem.lower()
        for part in USELESS_NAME_PARTS:
            if part in base:
                issues.append(f"[redundant] 疑似无用命名: {rel}")
                break
        # 未被引用（排除入口文件）
        if p.stem not in entry_stems:
            stem = p.stem
            if stem not in all_text and len(texts) > 1:
                issues.append(f"[redundant] 可能未被引用: {rel}")
    return issues


def check_overengineering(root: Path) -> list:
    issues = []
    for p in _source_files(root):
        rel = str(p.relative_to(root)).replace(os.sep, "/")
        for i, line in enumerate(p.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            if line.strip().startswith(("#", "//")):
                continue
            for pat in OVERENGINEER_PATTERNS:
                if pat.search(line):
                    issues.append(f"[overengine] {rel}:{i} 过度设计: {line.strip()[:60]}")
                    break
    return issues


def check_business(root: Path) -> list:
    issues = []
    for p in _source_files(root):
        rel = str(p.relative_to(root)).replace(os.sep, "/")
        text = p.read_text(encoding="utf-8", errors="ignore")
        for i, line in enumerate(text.splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith(("#", "//")):
                continue
            if not stripped:
                continue
            # 魔法数字（排除字符串/注释/日期/端口号）
            code_part = STRING_REMOVE.sub("", stripped)
            if MAGIC_NUMBER.search(code_part) and not re.search(r"\b(20\d\d|19\d\d|:?\d{5}\b|\d{1,5}\bport)", stripped):
                issues.append(f"[business] {rel}:{i} 魔法数字(>4位)需命名常量: {stripped[:60]}")
            # 玩具字符串（排除 URL/路径）
            for s in TOY_STRINGS:
                if re.search(rf"['\"]\b{s}\b['\"]", stripped, re.IGNORECASE) and not re.search(r"/|\.|\:", stripped):
                    issues.append(f"[business] {rel}:{i} 疑似演示字符串'{s}': {stripped[:60]}")
                    break
        # try 无 except/catch
        if re.search(r"\btry\s*:", text) and not re.search(r"\b(except|catch)\b", text):
            issues.append(f"[business] {rel} try 无 except/catch（异常可能被吞）")
    return issues


STRING_REMOVE = re.compile(r"['\"][^'\"]*['\"]")


def scan(root: Path, checks: list) -> dict:
    result = {"pass": True, "issues": []}
    if "fake" in checks or "all" in checks:
        result["issues"].extend(check_fake(root))
    if "redundancy" in checks or "all" in checks:
        result["issues"].extend(check_redundancy(root))
    if "overengineering" in checks or "all" in checks:
        result["issues"].extend(check_overengineering(root))
    if "business" in checks or "all" in checks:
        result["issues"].extend(check_business(root))
    seen, uniq = set(), []
    for i in result["issues"]:
        if i not in seen:
            seen.add(i)
            uniq.append(i)
    result["issues"] = uniq
    result["pass"] = not uniq
    return result


def main():
    parser = argparse.ArgumentParser(description="Pragmatic Guard — 防 AI 坏毛病门禁")
    parser.add_argument("--project", "-p", default=".", help="项目根目录")
    parser.add_argument("--check", action="append", default=["all"],
                        choices=["all", "fake", "redundancy", "overengineering", "business"],
                        help="检查类别（可多次）")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    args = parser.parse_args()

    root = Path(args.project).resolve()
    if not root.exists():
        sys.exit(f"[ERROR] project not found: {root}")

    result = scan(root, args.check)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Pragmatic Guard — {root}")
        print(f"  {'✅ PASS' if result['pass'] else '❌ FAIL'}: {len(result['issues'])} 个问题")
        for i in result["issues"]:
            print(f"  ✗ {i}")
    sys.exit(0 if result["pass"] else 1)


if __name__ == "__main__":
    main()