#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
强制主动使用门禁（Enforce Active）— 跨平台、平台无关。

把"AI 是否真正使用了框架能力 / 是否产出合格"从"靠提示词自觉"下沉为"程序强制校验"。
任何平台（Cursor / Claude Code / Codex / Gemini / Cline / 国产工具…）都可运行：
  - 作为完工门禁：python hooks/scripts/enforce_active.py
  - 作为开工自检：python hooks/scripts/enforce_active.py --pre
  - 由平台原生 hook 挂载：见 platforms/README.md

不通过（FAIL）则 exit 1，流程被阻断 —— 这就是"最底层"的强制，不依赖模型服从。
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


def find_root(start: Path) -> Path:
    """向上查找仓库根（含 AGENTS.md 或 framework/ 的目录）"""
    cur = start.resolve()
    for _ in range(6):
        if (cur / "AGENTS.md").exists() and (cur / "framework").exists():
            return cur
        parent = cur.parent
        if parent == cur:
            break
        cur = parent
    return start.resolve()


def run(cmd, cwd, timeout=60):
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout
    except Exception as e:  # noqa: BLE001
        return -1, str(e)


def main():
    ap = argparse.ArgumentParser(description="强制主动使用门禁")
    ap.add_argument("--pre", action="store_true", help="开工自检模式（较轻）")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    args = ap.parse_args()

    root = find_root(Path.cwd())
    fails: list[str] = []
    warns: list[str] = []

    # ── 1. 项目上下文已加载 ─────────────────────────────────────
    ctx = root / "context" / "project.yaml"
    if not ctx.exists():
        fails.append("context/project.yaml 缺失（未加载项目上下文）")

    # ── 2. 通用能力层存在 ──────────────────────────────────────
    fw_skills = root / "framework" / "skills"
    if not fw_skills.exists():
        fails.append("framework/skills 缺失（通用技能库）")
    else:
        n_skill = sum(1 for d in fw_skills.iterdir() if d.is_dir())
        if n_skill == 0:
            fails.append("framework/skills 为空")

    # ── pre 模式到此为止（开工自查） ───────────────────────────
    if not args.pre:
        # ── 3. doctor 门禁（仓库健康） ───────────────────────────
        rc, out = run_cmd([sys.executable, "devkit-doctor.py", "--format", "json"], root)
        d = None
        if out.strip():
            try:
                d = json.loads(out)
            except json.JSONDecodeError:
                d = None
        if d:
            bad = [c for c in d.get("checks", []) if c.get("result") == "fail"]
            if bad:
                fails.append("devkit-doctor FAIL: " + ", ".join(c["name"] for c in bad))
        else:
            warns.append(f"devkit-doctor 未能运行 (rc={rc})")

        # ── 4. 测试覆盖（核心业务有测试） ─────────────────────────
        tests = root / "tests"
        if not (tests.exists() and list(tests.rglob("test_*.py"))):
            warns.append("未发现测试文件（tests/test_*.py）")

        # ── 5. 密钥泄露扫描 ──────────────────────────────────────
        secret_pat = re.compile(
            r"(sk-[A-Za-z0-9]{10,}|ghp_[A-Za-z0-9]{20,}|"
            r"AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----)",
            re.IGNORECASE,
        )
        leaks = []
        for p in root.rglob("*"):
            if (
                p.is_file()
                and ".git" not in p.parts
                and p.suffix in (".py", ".ts", ".js", ".tsx", ".jsx", ".go", ".sh", ".yaml", ".yml", ".json")
            ):
                try:
                    txt = p.read_text(encoding="utf-8", errors="ignore")
                except Exception:  # noqa: BLE001
                    continue
                if secret_pat.search(txt):
                    leaks.append(str(p.relative_to(root)))
        if leaks:
            fails.append("疑似密钥泄露: " + ", ".join(leaks[:5]))

        # ── 6. CHANGELOG / 文档更新 ──────────────────────────────
        if root.joinpath("CHANGELOG.md").exists():
            changelog = root.joinpath("CHANGELOG.md").read_text(encoding="utf-8")
            if "Unreleased" not in changelog and not re.search(r"## \[\d+\.\d+\.\d+\]", changelog):
                warns.append("CHANGELOG.md 未更新（无版本段落）")
        else:
            warns.append("CHANGELOG.md 缺失")

    # ── 输出 ─────────────────────────────────────────────────────
    if args.json:
        print(json.dumps({"root": str(root), "pass": not fails, "fails": fails, "warns": warns},
                         ensure_ascii=False, indent=2))
    else:
        print(f"[EnforceActive] 仓库根: {root}")
        for w in warns:
            print(f"  [WARN] {w}")
        for f in fails:
            print(f"  [FAIL] {f}")
        if not fails:
            print("  [PASS] 强制门禁通过")
        print(f"  fail={len(fails)} warn={len(warns)}")

    sys.exit(1 if fails else 0)


def run_cmd(cmd, cwd):
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=60)
        return r.returncode, r.stdout
    except Exception as e:  # noqa: BLE001
        return -1, str(e)


if __name__ == "__main__":
    main()