#!/usr/bin/env python3
"""
Awesome AI DevKit — Stack Detector v1.0
技术栈 / 项目类型 / 测试框架 / 构建工具 自动识别器。

用法:
  python3 stack-detector.py                    # 扫描当前目录
  python3 stack-detector.py --project <dir>    # 扫描指定目录
  python3 stack-detector.py --json             # JSON 输出（供 scaffold-runner 消费）

输出变量（供 {{变量}} 注入 / scaffold 生成）:
  - tech_stack    : 人类可读技术栈概述，如 "React + TypeScript + Vite"
  - languages      : 检测到的主语言列表
  - project_type   : frontend | backend | fullstack | cli | library | mobile | ml | unknown
  - test_framework : pytest | jest | vitest | go test | cargo test | ...
  - build_tool     : vite | webpack | cargo | go build | maven | gradle | pip ...
  - package_mgr    : npm | pnpm | yarn | pip | poetry | cargo | go mod | ...
  - role_set       : 推荐团队角色组合（供 team-composer 使用）
"""

import argparse
import json
import os
import sys
from pathlib import Path


LANGUAGE_HINTS = {
    "package.json": "JavaScript",
    "tsconfig.json": "TypeScript",
    "pyproject.toml": "Python",
    "requirements.txt": "Python",
    "setup.py": "Python",
    "go.mod": "Go",
    "Cargo.toml": "Rust",
    "pom.xml": "Java",
    "build.gradle": "Java",
    "build.gradle.kts": "Kotlin",
    "composer.json": "PHP",
    "Gemfile": "Ruby",
}

# 主语言优先级（多个命中时取第一个为主语言）
LANGUAGE_PRIORITY = [
    "Python", "TypeScript", "JavaScript", "Go", "Rust",
    "Java", "Kotlin", "Swift", "C#", "C++", "C", "PHP", "Ruby",
]

FRONTEND_MARKERS = [
    "next.config.js", "next.config.ts", "vite.config.js", "vite.config.ts",
    "vite.config.mjs", "vue.config.js", "angular.json", "svelte.config.js",
    "nuxt.config.js", "nuxt.config.ts", "astro.config.mjs", "tailwind.config.js",
    "src/main.tsx", "src/App.tsx", "src/main.jsx", "pages/index.tsx",
]

BACKEND_MARKERS = [
    "app.py", "main.py", "manage.py", "server.py",
    "cmd/main.go", "main.go", "src/main.rs", "src/main.kt",
    "app/main.py", "application.py", "server.js", "app.js", "index.js",
]

MOBILE_MARKERS = [
    "app.json", "app.config.js", "app.config.ts",   # Expo / React Native
    "pubspec.yaml",                                   # Flutter
    "build.gradle", "build.gradle.kts", "settings.gradle",  # Android
    "Podfile",                                        # iOS CocoaPods
    "android/app/src/main/AndroidManifest.xml",
    "ios/Podfile",
    "lib/main.dart",                                  # Flutter 入口
]

ML_MARKERS = [
    "requirements-ai.txt", "ml_requirements.txt", "requirements-ml.txt",
    "pytorch", "tensorflow", "transformers", "diffusers", "keras",
    "llm", "rag", "copilot", "fine_tune", "training.py", "train.py",
    "ml/", "models/", "training/",
]
ML_DEPENDENCY_KEYWORDS = [
    "langchain", "langgraph", "openai", "pytorch", "torch", "tensorflow",
    "transformers", "diffusers", "scikit-learn", "sklearn", "llama-index",
    "anthropic", "pydantic-ai", "dspy", "mlx",
]

DATABASE_MARKERS = [
    "alembic.ini", "prisma/schema.prisma", "schema.sql",
    "docker-compose.yml", "docker-compose.yaml",
]

TEST_FRAMEWORKS = {
    "pytest": {"files": ["pytest.ini", "pyproject.toml"], "lang": "Python"},
    "unittest": {"files": ["requirements.txt"], "lang": "Python"},
    "jest": {"files": ["jest.config.js", "jest.config.ts"], "lang": "JavaScript"},
    "vitest": {"files": ["vitest.config.js", "vitest.config.ts", "vite.config.ts"], "lang": "JavaScript"},
    "go test": {"files": ["go.mod"], "lang": "Go"},
    "cargo test": {"files": ["Cargo.toml"], "lang": "Rust"},
    "junit": {"files": ["pom.xml", "build.gradle"], "lang": "Java"},
}

BUILD_TOOLS = {
    "vite": ["vite.config.js", "vite.config.ts", "vite.config.mjs"],
    "webpack": ["webpack.config.js", "webpack.config.ts"],
    "next": ["next.config.js", "next.config.ts"],
    "cargo": ["Cargo.toml"],
    "go build": ["go.mod"],
    "maven": ["pom.xml"],
    "gradle": ["build.gradle", "build.gradle.kts"],
    "pip": ["requirements.txt", "setup.py", "pyproject.toml"],
    "flutter": ["pubspec.yaml"],
    "expo": ["app.json", "app.config.js", "app.config.ts"],
}

PACKAGE_MANAGERS = {
    "pnpm": ["pnpm-lock.yaml", "package.json"],
    "yarn": ["yarn.lock", "package.json"],
    "npm": ["package-lock.json", "package.json"],
    "bun": ["bun.lockb", "bun.lock", "package.json"],
    "pip": ["requirements.txt", "pyproject.toml", "setup.py"],
    "poetry": ["poetry.lock"],
    "cargo": ["Cargo.toml", "Cargo.lock"],
    "go mod": ["go.mod"],
    "maven": ["pom.xml"],
    "gradle": ["build.gradle", "build.gradle.kts"],
    "flutter": ["pubspec.yaml", "pubspec.lock"],
}


def find_project_files(root: Path, depth: int = 3) -> set:
    """浅层扫描项目根（跳过依赖/构建/版本控制目录），收集存在的文件路径。"""
    found = set()
    skip_dirs = {"node_modules", ".git", ".venv", "venv", "__pycache__", "dist", "build", ".next", "target", ".temp"}
    for p in root.rglob("*"):
        rel = p.relative_to(root)
        if any(x in rel.parts for x in skip_dirs):
            continue
        parts = list(rel.parts)
        if len(parts) > depth:
            continue
        found.add(str(rel).replace(os.sep, "/"))
    return found


def detect(root: Path) -> dict:
    files = find_project_files(root)
    names = {Path(f).name for f in files}
    dirs = {f.split("/")[0] for f in files if "/" in f}

    # ── 语言 ────────────────────────────────────────────────
    languages = set()
    for name in names:
        if name in LANGUAGE_HINTS:
            languages.add(LANGUAGE_HINTS[name])
    if not languages:
        suffix_map = {".go": "Go", ".rs": "Rust", ".ts": "TypeScript", ".tsx": "TypeScript",
                      ".js": "JavaScript", ".jsx": "JavaScript", ".py": "Python",
                      ".java": "Java", ".kt": "Kotlin", ".swift": "Swift", ".c": "C",
                      ".cpp": "C++", ".rb": "Ruby", ".php": "PHP"}
        for f in files:
            lang = suffix_map.get(Path(f).suffix)
            if lang:
                languages.add(lang)
    primary = next((l for l in LANGUAGE_PRIORITY if l in languages), None)

    # ── 技术栈（读 package.json）───────────────────────────
    tech_stack = primary or "unknown"
    package_json = root / "package.json"
    if package_json.exists():
        try:
            data = json.loads(package_json.read_text(encoding="utf-8"))
            deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
            fw = []
            for name in ("react", "vue", "svelte", "next", "nuxt", "angular", "express", "fastify", "tailwindcss"):
                if name in deps:
                    fw.append(name)
            if "typescript" in deps or "tsconfig.json" in names:
                fw.append("typescript")
            if fw:
                tech_stack = " + ".join(dict.fromkeys(n.capitalize() for n in fw))
        except Exception:
            pass

    # ── 项目类型 ────────────────────────────────────────────
    has_frontend = any(m in names for m in FRONTEND_MARKERS)
    has_backend = any(m in names for m in BACKEND_MARKERS)
    has_mobile = any(m in names for m in MOBILE_MARKERS)
    # React Native 项目：有 App.tsx/App.jsx 且依赖含 react-native / expo 才算 mobile
    if not has_mobile and ("App.tsx" in names or "App.jsx" in names):
        try:
            if package_json.exists():
                _pj = json.loads(package_json.read_text(encoding="utf-8"))
                _deps = {**_pj.get("dependencies", {}), **_pj.get("devDependencies", {})}
                if "react-native" in _deps or "expo" in _deps:
                    has_mobile = True
        except Exception:
            has_mobile = False
    has_ml = any(m in names for m in ML_MARKERS) or any(
        d in dirs for d in ("ml", "models", "training"))
    # 依赖内容命中 AI 关键词（langchain/openai/pytorch 等）
    if not has_ml:
        try:
            dep_text = ""
            for f in ("requirements.txt", "requirements-ai.txt", "pyproject.toml", "package.json"):
                p = root / f
                if p.exists():
                    dep_text += p.read_text(encoding="utf-8", errors="ignore").lower()
            has_ml = any(k in dep_text for k in ML_DEPENDENCY_KEYWORDS)
        except Exception:
            has_ml = False
    has_db = any(m in names for m in DATABASE_MARKERS) or any(
        d in dirs for d in ("migrations", "alembic"))

    if has_mobile:
        ptype = "mobile"
    elif has_ml:
        ptype = "ml"
    elif has_frontend and has_backend:
        ptype = "fullstack"
    elif has_frontend:
        ptype = "frontend"
    elif has_backend:
        ptype = "backend"
    elif "Cargo.toml" in names or "cmd" in dirs or "bin" in dirs:
        ptype = "cli"
    elif has_db:
        ptype = "backend"
    elif "main.go" in names or "main.py" in names or "src/main.rs" in files:
        ptype = "cli"
    else:
        ptype = "library"

    # ── 移动端 / AI 技术栈细化（package.json 或 pubspec）─────
    if ptype in ("mobile", "ml"):
        try:
            if (root / "pubspec.yaml").exists():
                tech_stack = "Flutter (Dart)"
            elif package_json.exists():
                data = json.loads(package_json.read_text(encoding="utf-8"))
                deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                if "react-native" in deps or "expo" in deps:
                    tech_stack = "React Native" + (" + TypeScript" if "typescript" in deps else "")
                if ptype == "ml" and any(k in deps for k in ("langchain", "openai")):
                    tech_stack = "AI Agent (LangChain/OpenAI)"
        except Exception:
            pass
    if ptype == "ml" and tech_stack == primary:
        # 由 requirements/pyproject 推断 AI 栈
        try:
            req = ""
            for f in ("requirements.txt", "pyproject.toml"):
                p = root / f
                if p.exists():
                    req += p.read_text(encoding="utf-8", errors="ignore").lower()
            if "langchain" in req:
                tech_stack = "AI Agent (LangChain)"
            elif "pytorch" in req or "torch" in req:
                tech_stack = "ML (PyTorch)"
            elif "tensorflow" in req:
                tech_stack = "ML (TensorFlow)"
        except Exception:
            pass

    # ── 测试框架 ────────────────────────────────────────────
    test_fw = None
    for fw, spec in TEST_FRAMEWORKS.items():
        if spec["lang"] == (primary or "") and any(m in names for m in spec["files"]):
            test_fw = fw
            break
    if test_fw is None and primary:
        test_fw = {"Python": "pytest", "JavaScript": "jest", "TypeScript": "jest",
                   "Go": "go test", "Rust": "cargo test"}.get(primary, "unknown")
    if ptype == "mobile" and (root / "pubspec.yaml").exists():
        test_fw = "flutter test"

    # ── 构建 / 包管理 ──────────────────────────────────────
    build_tool = next((t for t, ms in BUILD_TOOLS.items() if any(m in names for m in ms)), None)
    pkg_mgr = next((m for m, ms in PACKAGE_MANAGERS.items() if any(x in names for x in ms)), None)

    return {
        "tech_stack": tech_stack,
        "languages": sorted(languages),
        "primary_language": primary,
        "project_type": ptype,
        "test_framework": test_fw,
        "build_tool": build_tool,
        "package_manager": pkg_mgr,
        "has_database": has_db,
        "role_set": team_for(ptype),
        "detected_files": sorted(files)[:40],
    }


def team_for(ptype: str) -> list[str]:
    """按项目类型返回推荐角色组合（来自 framework/agents 11 个通用角色）。"""
    if ptype == "fullstack":
        return ["architect-system-designer", "frontend-ui-developer", "backend-api-developer",
                "test-qa-engineer", "code-reviewer", "security-review-engineer"]
    if ptype == "frontend":
        return ["frontend-ui-developer", "design-system-architect", "test-qa-engineer"]
    if ptype == "backend":
        return ["backend-api-developer", "database-engineer", "test-qa-engineer",
                "security-review-engineer"]
    if ptype == "cli":
        return ["backend-api-developer", "code-reviewer"]
    if ptype == "mobile":
        return ["frontend-ui-developer", "test-qa-engineer"]
    if ptype == "ml":
        return ["backend-api-developer", "test-qa-engineer", "security-review-engineer"]
    return ["backend-api-developer", "code-reviewer"]


def main():
    parser = argparse.ArgumentParser(description="Stack Detector — 识别项目技术栈/类型/工具链")
    parser.add_argument("--project", "-p", default=".", help="项目根目录")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    args = parser.parse_args()

    root = Path(args.project).resolve()
    if not root.exists():
        sys.exit(f"[ERROR] project not found: {root}")
    result = detect(root)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for k, v in result.items():
            print(f"{k}: {v}")


if __name__ == "__main__":
    main()