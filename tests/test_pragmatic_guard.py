#!/usr/bin/env python3
"""pragmatic-guard 单测 — 防 AI 坏毛病门禁（虚假实现/冗余/过度设计/业务不合现实）。"""

import importlib.util
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GUARD = PROJECT_ROOT / "framework" / "lib" / "scripts" / "quality" / "pragmatic-guard.py"

spec = importlib.util.spec_from_file_location("pragmatic_guard", GUARD)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
scan = mod.scan


def _write(root: Path, path: str, content: str):
    p = root / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


def test_clean_project_passes():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root, "src/calc.py",
               "RATE = 0.1\ndef calc(amount):\n"
               "    if amount < 0:\n        raise ValueError('neg')\n"
               "    return amount * RATE\n")
        _write(root, "src/main.py", "from src.calc import calc\nprint(calc(1))\n")
        r = scan(root, ["all"])
        assert r["pass"], f"干净项目应通过: {r['issues']}"


def test_fake_placeholder_detected():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root, "src/api.py",
               "def do_thing():\n    pass\n\ndef todo_api():\n    return None\n")
        r = scan(root, ["fake"])
        assert not r["pass"]
        assert any("pass" in i for i in r["issues"]) or any("占位" in i for i in r["issues"])


def test_redundant_empty_file_detected():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root, "src/real.py", "def f(): return 1\n")
        _write(root, "src/empty.py", "")
        r = scan(root, ["redundancy"])
        assert not r["pass"]
        assert any("空文件" in i for i in r["issues"])


def test_magic_number_detected():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root, "src/a.py", "def f():\n    x = 123456789\n    return x\n")
        r = scan(root, ["business"])
        assert not r["pass"]
        assert any("魔法数字" in i for i in r["issues"])


def test_overengineering_detected():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root, "src/f.py",
               "class BaseFactory:\n    pass\n\ndef use():\n    return BaseFactory()\n")
        r = scan(root, ["overengineering"])
        assert not r["pass"]
        assert any("过度设计" in i for i in r["issues"])


def test_unreferenced_file_detected():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root, "src/main.py", "print('ok')\n")
        _write(root, "src/orphan.py", "def helper(): return 1\n")
        r = scan(root, ["redundancy"])
        assert not r["pass"]
        assert any("未被引用" in i for i in r["issues"])