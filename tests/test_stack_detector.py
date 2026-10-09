#!/usr/bin/env python3
"""stack-detector 自适应识别测试 — 验证技术栈/项目类型/工具链识别的正确性。"""

import importlib.util
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DETECTOR = PROJECT_ROOT / "scenarios" / "programming" / "coding" / "lib" / "stack-detector.py"

spec = importlib.util.spec_from_file_location("stack_detector", DETECTOR)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
detect = mod.detect


def _write(root: Path, path: str, content: str = ""):
    p = root / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


def test_detect_react_frontend():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root, "package.json",
               '{"dependencies":{"react":"^18","typescript":"^5"},"devDependencies":{"vite":"^5"}}')
        _write(root, "vite.config.ts", "export default {}")
        _write(root, "src/App.tsx", "export const App=()=><div/>")
        r = detect(root)
        assert r["project_type"] == "frontend"
        assert "react" in r["tech_stack"].lower() or "React" in r["tech_stack"]


def test_detect_go_backend():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root, "go.mod", "module demo\n\ngo 1.22")
        _write(root, "cmd/server/main.go", "package main\nfunc main(){}")
        r = detect(root)
        assert r["project_type"] == "backend"
        assert r["primary_language"] == "Go"
        assert r["test_framework"] == "go test"


def test_detect_python_ml():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root, "requirements.txt", "langchain==0.2\nopenai==1.0\nfastapi")
        _write(root, "app.py", "from fastapi import FastAPI\napp=FastAPI()")
        r = detect(root)
        assert r["project_type"] == "ml"
        assert "langchain" in r["tech_stack"].lower()


def test_detect_flutter_mobile():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root, "pubspec.yaml", "name: flutter_app")
        _write(root, "lib/main.dart", "void main(){}")
        r = detect(root)
        assert r["project_type"] == "mobile"
        assert r["test_framework"] == "flutter test"


def test_detect_rust_cli():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root, "Cargo.toml", "[package]\nname='rcli'")
        _write(root, "src/main.rs", "fn main(){}")
        r = detect(root)
        assert r["project_type"] == "cli"
        assert r["primary_language"] == "Rust"


def test_detect_unknown_library():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root, "lib/helper.py", "def helper(): pass")
        r = detect(root)
        assert r["project_type"] == "library"