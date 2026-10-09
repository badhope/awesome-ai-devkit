#!/usr/bin/env python3
"""
Awesome AI DevKit — Pragmatic Guard v1.0
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


# ── 1. 虚假实现：占位符 / 空壳 / 未完成标记 ──────────────────────────
FAKE_PLACEHOLDER_PATTERNS = [
    r"^\s*pass\s*(#.*)?$",                      # 空函数体（Python）
    r"NotImplementedError",
    r"^\s*(\.\.\.)\s*(#.*)?$",                  # 省略号占位
    r"\bTODO\b", r"\bFIXME\b", r"\bXXX\b",
]
FAKE_EMPTY_FN = re.compile(
    r"\b(def|function|func|fn)\s+(\w+)\s*\([^)]*\)\s*[:{]\s*"
    r"(\n\s*(pass|\.\.\.)\s*\n?)+"
)

# ── 2. 冗余文件 / 空文件 / 无用命名 ─────────────────────
EMPTY_FILE_EXTS = {".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs",
                   ".java", ".kt", ".swift", ".rb", ".cpp", ".c"}
USELESS_NAME_PARTS = ["util", "placeholder", "dummy", "stub", "fake_",
                      "temp_", "tmp_", "example_stub"]

# ── 3. 过度设计信号 ─────────────────────────────────────
OVERENGINEER_PATTERNS = [
    re.compile(r"AbstractFactory|BaseFactory|FactoryFactory"),
    re.compile(r"class\s+\w+(Config|Options|Context)\w*", re.IGNORECASE),
    re.compile(r"util_util|helper_helper|manager_manager|service_service", re.IGNORECASE),
    re.compile(r"if\s+False\s*:|@\s*\w*(deprecated|unused)\b", re.IGNORECASE),
]

# ── 4. 业务不合现实 / 魔法值 ────────────────────────────
MAGIC_NUMBER = re.compile(r"(?<![\w.])\d{5,}(?![\w.])")
# 常见玩具/演示字符串（不符合真实业务）
TOY_STRINGS = ["hello", "world", "foobar", "test123", "asdf", "lorem", "dummy_data"]


def _source_files(root: Path) -> list:
    skip = {"node_modules", ".git", ".venv", "venv", "__pycache__", "dist",
            "build", ".next", "target", ".temp", ".pytest_cache", ".ruff_cache", "logs"}
    files = []
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(root)
        if any(x in rel.parts for x in skip):
            continue
        if p.suffix.lower() in EMPTY_FILE_EXTS:
            files.append(p)
    return files


def _load_text(root: Path) -> dict:
    return {p: p.read_text(encoding="utf-8", errors="ignore")
            for p in _source_files(root)}


def check_fake(root: Path) -> list:
    issues = []
    for p, text in _load_text(root).items():
        rel = str(p.relative_to(root)).replace(os.sep, "/")
        lines = text.splitlines()
        for i, line in enumerate(lines, 1):
            if line.lstrip().startswith(("#", "//", "/*", "*", "--")):
                continue
            for pat in FAKE_PLACEHOLDER_PATTERNS:
                if re.search(pat, line):
                    issues.append(f"[fake] {rel}:{i} 占位/未实现: {line.strip()[:60]}")
                    break
        for m in FAKE_EMPTY_FN.finditer(text):
            issues.append(f"[fake] {rel} 空函数体: {m.group(2)}()")
    return issues


def check_redundancy(root: Path) -> list:
    issues = []
    texts = _load_text(root)
    all_rel = {str(p.relative_to(root)).replace(os.sep, "/") for p in texts}
    all_text = "\n".join(texts.values())
    entry_names = {"index", "app", "main", "__init__", "cli", "server"}
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
        # 未被引用检查（入口文件除外）
        if p.stem not in entry_names:
            stem = p.stem
            referenced = False
            for other_rel, other_text in texts.items():
                if other_rel == rel:
                    continue
                if re.search(rf"\b{re.escape(stem)}\b", other_text):
                    referenced = True
                    break
            if not referenced and len(texts) > 1:
                issues.append(f"[redundant] 可能未被引用: {rel}")
    return issues


def check_overengineering(root: Path) -> list:
    issues = []
    for p, text in _load_text(root).items():
        rel = str(p.relative_to(root)).replace(os.sep, "/")
        for i, line in enumerate(text.splitlines(), 1):
            for pat in OVERENGINEER_PATTERNS:
                if pat.search(line):
                    issues.append(f"[overengine] {rel}:{i} 过度设计: {line.strip()[:60]}")
                    break
    return issues


def check_business(root: Path) -> list:
    issues = []
    for p, text in _load_text(root).items():
        rel = str(p.relative_to(root)).replace(os.sep, "/")
        for i, line in enumerate(text.splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith(("#", "//")):
                continue
            if MAGIC_NUMBER.search(stripped) and not re.search(r"\b(20\d\d|19\d\d)\b", stripped):
                issues.append(f"[business] {rel}:{i} 魔法数字(>4位)需命名常量: {stripped[:60]}")
            for t in TOY_STRINGS:
                if re.search(rf"['\"]\b{t}\b['\"]", stripped, re.IGNORECASE):
                    issues.append(f"[business] {rel}:{i} 疑似演示字符串'{t}': {stripped[:60]}")
                    break
        if "try" in text and "except" not in text and "catch" not in text:
            issues.append(f"[business] {rel} try 无 except/catch（异常可能被吞）")
    return issues


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