# ──────────────────────────────────────────────────────────────────────
# Awesome AI DevKit — Scaffold Runner v2.0
#
# 读取 scaffold.yaml，逐步调用 AI agent CLI 执行开发任务。
#
# 设计理念:
#   - 最薄的 glue 层
#   - 不重复造 LLM orchestration，复用成熟 CLI agent
#   - 每步 prompt 包含 goal + referenced skill 内容 + quality gate
#   - 失败时把报错上下文重新塞给 agent，让它自己修
#   - 支持 auto-commit 和 dry-run
#
# 用法:
#   python3 scaffolds/scaffold-runner.py                          # 默认 scaffold.yaml
#   python3 scaffolds/scaffold-runner.py my-feature.yaml          # 指定 scaffold
#   python3 scaffolds/scaffold-runner.py --dry-run                # 只生成 prompt 不执行
#   python3 scaffolds/scaffold-runner.py --provider claude        # Claude Code (默认)
#   python3 scaffolds/scaffold-runner.py --provider cursor-agent  # Cursor
#   python3 scaffolds/scaffold-runner.py --provider "custom-cmd"  # 自定义命令
# ──────────────────────────────────────────────────────────────────────

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

try:
    import yaml
except ImportError:
    sys.exit("[ERROR] 需要 PyYAML:  pip install pyyaml")


DEFAULT_SCAFFOLD = "scaffold.yaml"
DEFAULT_PROVIDER = "claude"
SESSION_BASE = "logs/sessions"


# ── 数据结构 ─────────────────────────────────────────────────────────

class StepResult:
    def __init__(self, step_id: str, goal: str):
        self.step_id = step_id
        self.goal = goal
        self.success = False
        self.attempts = 0
        self.error_output = ""
        self.agent_output = ""

    def to_dict(self) -> dict:
        return {
            "step_id": self.step_id,
            "goal": self.goal,
            "success": self.success,
            "attempts": self.attempts,
            "error_output": self.error_output[:500] if self.error_output else "",
        }


class Session:
    def __init__(self, scaffold_path: str, project_root: Path):
        self.scaffold_path = scaffold_path
        self.project_root = project_root
        self.session_id = f"run-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
        self.session_dir = project_root / SESSION_BASE / self.session_id
        self.steps: list[StepResult] = []
        self.success = False

    def ensure_dirs(self):
        self.session_dir.mkdir(parents=True, exist_ok=True)

    def save_meta(self, task_name: str, provider: str):
        meta = {
            "session_id": self.session_id,
            "task": task_name,
            "scaffold": self.scaffold_path,
            "provider": provider,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "steps_total": 0,
            "steps_completed": 0,
        }
        (self.session_dir / "meta.json").write_text(
            json.dumps(meta, indent=2, ensure_ascii=False)
        )

    def save_report(self, step_results: list[StepResult]):
        report = {
            "session_id": self.session_id,
            "success": self.success,
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "steps_total": len(step_results),
            "steps_completed": sum(1 for s in step_results if s.success),
            "steps": [s.to_dict() for s in step_results],
        }
        (self.session_dir / "report.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False)
        )


# ── Prompt 构建 ──────────────────────────────────────────────────────

def build_step_prompt(
    step: dict,
    task: dict,
    project_root: str,
    skills_dir: Path,
    prev_errors: str = "",
    vars: Optional[dict] = None,
) -> str:
    goal = step.get("goal", "")
    description = step.get("description", "")
    skills = step.get("skills", [])
    outputs = step.get("outputs", [])
    quality_gate = str(step.get("quality_gate", ""))
    vars = vars or {}

    # 读取引用的 skill 全文
    skill_sections = []
    for skill_id in skills[:3]:  # 最多 3 个核心 skill
        skill_path = skills_dir / skill_id / "SKILL.md"
        if skill_path.exists():
            content = skill_path.read_text(encoding="utf-8")
            # 仅截取前 3000 字符防止 context 爆炸
            if len(content) > 3000:
                content = content[:3000] + "\n... (truncated)"
            skill_sections.append(f"## Skill: {skill_id}\n\n{content}")

    # 格式化 outputs（替换 <var> 占位符）
    output_lines = []
    for out in outputs:
        if isinstance(out, dict):
            for path, criteria in out.items():
                resolved = path
                for k, v in vars.items():
                    resolved = resolved.replace(f"<{k}>", v)
                must_contain = criteria.get("contains", []) if isinstance(criteria, dict) else []
                line = f"- `{resolved}`"
                if must_contain:
                    line += f" — must contain: {', '.join(must_contain)}"
                output_lines.append(line)
        elif isinstance(out, str):
            resolved = out
            for k, v in vars.items():
                resolved = resolved.replace(f"<{k}>", v)
            output_lines.append(f"- `{resolved}`")

    parts = [
        f"# Step: {goal}",
        "",
        f"**Description**: {description}" if description else "",
        "",
        "## Context",
        f"- Task: {task.get('name', 'unknown')}",
        f"- Working directory: {project_root}",
        "",
        "## Required Outputs",
        *(output_lines if output_lines else ["(no specific outputs)"]),
        "",
    ]

    if quality_gate:
        parts += ["## Quality Gate", f"After completing this step, verify: **{quality_gate}**", ""]

    if skill_sections:
        parts += ["## Reference Skills", *skill_sections, ""]

    if prev_errors:
        parts += [
            "## Previous Errors",
            "The following errors occurred in prior attempts. Fix them:",
            "```",
            prev_errors[-2000:],  # 截断防止超长
            "```",
            "",
        ]

    parts += [
        "## Instructions",
        "1. Read all reference skill(s) carefully",
        "2. Produce all required output files",
        "3. Self-verify against quality gate",
        "4. If quality gate fails, fix and re-verify until passing",
        "5. When done, reply with 'DONE' and a one-line summary",
        "",
        "Begin.",
    ]

    return "\n".join(p for p in parts if p)


# ── Agent 调用 ───────────────────────────────────────────────────────

def call_agent(prompt: str, provider: str, project_root: Path) -> tuple[bool, str, str]:
    """调用 AI agent CLI"""

    if provider == "claude":
        return _call_claude(prompt, project_root)
    elif provider == "cursor-agent":
        return _call_cursor(prompt, project_root)
    elif provider == "opencode":
        return _call_opencode(prompt, project_root)
    else:
        return _call_custom(prompt, provider, project_root)


def _call_claude(prompt: str, project_root: Path) -> tuple[bool, str, str]:
    try:
        result = subprocess.run(
            ["claude", "--print", "--dangerously-skip-permissions", prompt],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=600,
        )
        output = result.stdout + result.stderr
        if result.returncode == 0 or "DONE" in output:
            return True, output, ""
        return False, output, f"Exit code {result.returncode}"
    except FileNotFoundError:
        return False, "", "claude CLI not found. Install: npm i -g @anthropic-ai/claude-code"
    except subprocess.TimeoutExpired:
        return False, "", "Timeout (600s)"


def _call_cursor(prompt: str, project_root: Path) -> tuple[bool, str, str]:
    try:
        result = subprocess.run(
            ["cursor-agent", "chat", "--print", prompt],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=600,
        )
        if result.returncode == 0:
            return True, result.stdout + result.stderr, ""
        return False, result.stdout + result.stderr, f"Exit code {result.returncode}"
    except FileNotFoundError:
        return False, "", "cursor-agent CLI not found"
    except subprocess.TimeoutExpired:
        return False, "", "Timeout (600s)"


def _call_custom(prompt: str, cmd: str, project_root: Path) -> tuple[bool, str, str]:
    try:
        result = subprocess.run(
            cmd.split(),
            input=prompt,
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=600,
        )
        if result.returncode == 0:
            return True, result.stdout + result.stderr, ""
        return False, result.stdout + result.stderr, f"Exit code {result.returncode}"
    except FileNotFoundError:
        return False, "", f"Command not found: {cmd}"
    except subprocess.TimeoutExpired:
        return False, "", "Timeout (600s)"


def _call_opencode(prompt: str, project_root: Path) -> tuple[bool, str, str]:
    """调用 opencode CLI（跨平台）—— prompt 经 stdin 传入，避免 Windows cmd 引号问题"""
    import shutil
    found = shutil.which("opencode")
    if not found:
        return False, "", "opencode CLI not found. Install: npm i -g opencode-ai"
    # Windows 上 opencode 常为 .cmd/.ps1 shim，经 cmd /c 执行；prompt 走 stdin
    if os.name == "nt" and not found.lower().endswith(".exe"):
        argv = ["cmd", "/c", "opencode", "run", "--auto"]
    else:
        argv = [found, "run", "--auto"]
    try:
        result = subprocess.run(argv, input=prompt, cwd=str(project_root),
                                capture_output=True, text=True, timeout=600)
        output = result.stdout + result.stderr
        if result.returncode == 0 or "DONE" in output:
            return True, output, ""
        return False, output, f"Exit code {result.returncode}"
    except FileNotFoundError:
        return False, "", "opencode CLI not found. Install: npm i -g opencode-ai"
    except subprocess.TimeoutExpired:
        return False, "", "Timeout (600s)"


# ── Git ──────────────────────────────────────────────────────────────

def git_commit_step(project_root: Path, msg: str) -> bool:
    try:
        subprocess.run(["git", "add", "-A"], cwd=str(project_root),
                       check=True, capture_output=True)
        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=str(project_root), capture_output=True,
        )
        if result.returncode == 0:
            return True  # nothing to commit
        subprocess.run(
            ["git", "commit", "-m", msg[:72]],
            cwd=str(project_root), check=True, capture_output=True,
        )
        return True
    except Exception:
        return False


def step_outputs_gate(outputs: list, project_root: Path, vars: Optional[dict] = None) -> list[str]:
    """逐步强制：校验本步产出文件存在 + contains 关键词。返回缺失/不满足清单。

    路径中的 <占位符> 会先按 vars 替换；仍未替换的占位符（如 <module>、<ext>）
    视为 glob 通配符做模糊匹配，避免因模板占位符未穷举而误判产物缺失。
    """
    import glob as _glob

    vars = vars or {}
    problems: list[str] = []

    def _resolve(path: str) -> list:
        """返回：完全匹配则 [path]，存在未替换占位符则 glob 匹配列表，否则空列表。"""
        resolved = path
        for k, v in vars.items():
            resolved = resolved.replace(f"<{k}>", v)
        if "<" in resolved and ">" in resolved:
            # 仍有未替换占位符 → 转 glob 模式（<name> → *）
            pattern = ""
            i = 0
            while i < len(resolved):
                if resolved[i] == "<":
                    j = resolved.find(">", i)
                    if j == -1:
                        pattern += resolved[i:]
                        break
                    pattern += "*"
                    i = j + 1
                else:
                    pattern += resolved[i]
                    i += 1
            return [p for p in _glob.glob(str(project_root / pattern), recursive=True)
                    if (project_root / p).is_file()]
        return [resolved] if (project_root / resolved).exists() else []

    for out in outputs:
        if isinstance(out, str):
            matches = _resolve(out)
            if not matches:
                problems.append(f"missing: {out}")
        elif isinstance(out, dict):
            for path, criteria in out.items():
                matches = _resolve(path)
                if not matches:
                    problems.append(f"missing: {path}")
                    continue
                if isinstance(criteria, dict):
                    contains = criteria.get("contains", [])
                    if contains:
                        checked_any = False
                        for m in matches:
                            try:
                                text = (project_root / m).read_text(encoding="utf-8", errors="ignore")
                            except Exception:  # noqa: BLE001
                                text = ""
                            checked_any = True
                            if all(kw in text for kw in contains):
                                break
                        else:
                            problems.append(f"{path} 缺含: {', '.join(contains)}")
    return problems


# ── Step 分组: 扁平列表 → 串行/并行分组 ──────────────────────────────

def group_steps(steps: list[dict]) -> list[tuple[str, list[int]]]:
    """
    将扁平 step 列表分组为 (mode, indices) 列表。
    连续的 parallel: true 步骤合并为一个并行组。
    """
    groups: list[tuple[str, list[int]]] = []
    i = 0
    while i < len(steps):
        if steps[i].get("parallel"):
            parallel_indices = []
            while i < len(steps) and steps[i].get("parallel"):
                parallel_indices.append(i)
                i += 1
            groups.append(("parallel", parallel_indices))
        else:
            groups.append(("serial", [i]))
            i += 1
    return groups


# ── 主流程 ───────────────────────────────────────────────────────────

def run_scaffold(scaffold_path: str, provider: str, dry_run: bool,
                 auto_commit: bool, project_root: Path, feature: str = "",
                 stack: str = "") -> int:

    scaffold_file = Path(scaffold_path)
    if not scaffold_file.exists():
        print(f"[ERROR] scaffold not found: {scaffold_path}")
        return 1

    data = yaml.safe_load(scaffold_file.read_text(encoding="utf-8"))
    version = data.get("version", "?")
    task = data.get("task", {})
    task_name = task.get("name", "unknown")
    raw_steps = data.get("steps", [])

    # 占位符变量：<feature> 等模板路径替换为真实值（取自 task 或 CLI）
    vars: dict = {"feature": feature, "module": feature, "ext": "py"}
    # 技术栈 → 占位符默认值映射（让 <ext>/<module>/<test_framework> 随技术栈自适应）
    _stack_vars = {
        "react":   {"ext": "tsx", "module": "components", "test_framework": "vitest"},
        "vue":     {"ext": "vue", "module": "components", "test_framework": "vitest"},
        "svelte":  {"ext": "svelte", "module": "components", "test_framework": "vitest"},
        "next":    {"ext": "tsx", "module": "components", "test_framework": "jest"},
        "angular": {"ext": "ts", "module": "app", "test_framework": "jest"},
        "express": {"ext": "js", "module": "routes", "test_framework": "jest"},
        "fastify": {"ext": "ts", "module": "routes", "test_framework": "vitest"},
        "python":  {"ext": "py", "module": "services", "test_framework": "pytest"},
        "django":  {"ext": "py", "module": "apps", "test_framework": "pytest"},
        "fastapi": {"ext": "py", "module": "routers", "test_framework": "pytest"},
        "flask":   {"ext": "py", "module": "routes", "test_framework": "pytest"},
        "go":      {"ext": "go", "module": "internal", "test_framework": "go test"},
        "rust":    {"ext": "rs", "module": "src", "test_framework": "cargo test"},
        "java":    {"ext": "java", "module": "src", "test_framework": "junit"},
    }
    if stack and stack.lower() in _stack_vars:
        vars.update(_stack_vars[stack.lower()])
    vars.setdefault("test_framework", "pytest")

    if not raw_steps:
        print("[ERROR] no steps defined in scaffold")
        return 1

    # Session
    session = Session(scaffold_path, project_root)
    session.ensure_dirs()
    session.save_meta(task_name, provider)

    print(f"\n{'='*60}")
    print(f"  Awesome AI DevKit Scaffold Runner v2.0")
    print(f"  Task: {task_name}")
    print(f"  Steps: {len(raw_steps)}")
    print(f"  Provider: {provider}")
    print(f"  Session: {session.session_dir}")
    print(f"{'='*60}\n")

    # Memory files
    for mf in data.get("memory", []):
        if mf.startswith("git "):
            continue
        p = project_root / mf
        icon = "✓" if p.exists() else "⚠"
        print(f"  {icon} Memory: {mf}")

    # Skills dir（通用层优先）
    skills_dir = project_root / "framework" / "skills"
    if not skills_dir.exists():
        skills_dir = project_root / "scenarios" / "programming" / "fullstack" / "skills"
    if not skills_dir.exists():
        skills_dir = project_root / "skills"

    # 分组
    groups = group_steps(raw_steps)
    print(f"\n  Execution groups: {len(groups)}")
    print()

    # 执行
    all_results: list[StepResult] = []
    step_counter = 0
    errors_history: list[str] = []

    for mode, indices in groups:
        if mode == "parallel" and len(indices) > 1:
            print(f"── Parallel Block ({len(indices)} steps) ──\n")
            # 并行模式: 依次提示 agent 做所有并行任务 (实际需 agent 支持并行)
            for idx in indices:
                step_counter += 1
                step = raw_steps[idx]
                result = StepResult(f"step-{step_counter:02d}", step.get("goal", ""))
                prompt = build_step_prompt(step, task, str(project_root), skills_dir,
                                           prev_errors="\n".join(errors_history[-2:]), vars=vars)
                print(f"  [{step_counter}/{len(raw_steps)}] (parallel) {step.get('goal', '')}")
                if dry_run:
                    prompt_path = session.session_dir / f"step-{step_counter:02d}-prompt.md"
                    prompt_path.write_text(prompt, encoding="utf-8")
                    print(f"    (dry-run) prompt saved → {prompt_path.relative_to(project_root)}")
                else:
                    print(f"    Prompt length: {len(prompt)} chars")
                result.success = True  # dry-run always succeeds
                all_results.append(result)
        else:
            print(f"── Serial Block ──\n")
            for idx in indices:
                step_counter += 1
                step = raw_steps[idx]
                goal = step.get("goal", f"Step {step_counter}")
                result = StepResult(f"step-{step_counter:02d}", goal)

                print(f"[{step_counter}/{len(raw_steps)}] {goal}")

                if dry_run:
                    prompt = build_step_prompt(step, task, str(project_root), skills_dir,
                                               prev_errors="\n".join(errors_history[-2:]), vars=vars)
                    prompt_path = session.session_dir / f"step-{step_counter:02d}-prompt.md"
                    prompt_path.write_text(prompt, encoding="utf-8")
                    print(f"  (dry-run) prompt → {prompt_path.relative_to(project_root)}")
                    result.success = True
                    all_results.append(result)
                    continue

                # 真实执行（含逐步强制产物门禁）
                for attempt in range(1, 4):
                    result.attempts = attempt
                    prompt = build_step_prompt(step, task, str(project_root), skills_dir,
                                               prev_errors="\n".join(errors_history[-2:]), vars=vars)
                    print(f"  Attempt {attempt}/3...")
                    ok, output, err = call_agent(prompt, provider, project_root)
                    result.agent_output = output
                    if ok:
                        # 逐步强制：校验本 step 的产出物（文件存在 + contains）
                        gate_errors = step_outputs_gate(step.get("outputs", []), project_root, vars)
                        if gate_errors:
                            result.error_output = "\n".join(gate_errors)
                            errors_history.append(f"[{goal}] outputs 未满足: {'; '.join(gate_errors[:3])}")
                            print(f"  ✗ outputs 未满足: {'; '.join(gate_errors[:3])}")
                        else:
                            result.success = True
                            errors_history.clear()
                            print(f"  ✓ Done (outputs 已校验)")
                            if auto_commit and git_commit_step(project_root, goal):
                                print(f"  ✓ Committed")
                            break
                    else:
                        result.error_output = err + output
                        errors_history.append(f"[{goal}] {err}")
                        print(f"  ✗ {err[:80]}")

                all_results.append(result)
                if not result.success:
                    print(f"\n[ABORT] Step {step_counter} failed after 3 attempts.")
                    session.save_report(all_results)
                    return 1

    # Post-task
    post_gates = data.get("post_task", {}).get("quality_gates", [])
    if post_gates:
        print(f"\n── Post-task Gates ──")
        for g in post_gates:
            print(f"  □ {g}")
        print()

    # 强制完工门禁（机制层，跨平台）—— 不通过即失败，不依赖 AI 自觉
    enforce_script = project_root / "hooks" / "scripts" / "enforce_active.py"
    if enforce_script.exists():
        print(f"\n── 强制完工门禁 (enforce_active) ──")
        rc = subprocess.run([sys.executable, str(enforce_script)],
                            cwd=str(project_root)).returncode
        if rc != 0:
            print(f"[ABORT] 强制完工门禁未通过（enforce_active 退出码 {rc}）")
            session.success = False
            session.save_report(all_results)
            return 1
        print(f"  ✓ 强制完工门禁通过")

    session.success = True
    session.save_report(all_results)
    print(f"{'='*60}")
    print(f"  ✅ Complete — {sum(1 for r in all_results if r.success)}/{len(all_results)} steps")
    print(f"  Report: {session.session_dir / 'report.json'}")
    print(f"{'='*60}")
    return 0


# ── CLI ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="scaffold-runner",
        description="Awesome AI DevKit Scaffold Runner v2.0 — drives AI agents step-by-step.",
    )
    parser.add_argument("scaffold", nargs="?", default=DEFAULT_SCAFFOLD)
    parser.add_argument("--provider", "-p",
                        default=os.environ.get("DEVKIT_PROVIDER", DEFAULT_PROVIDER))
    parser.add_argument("--dry-run", "-n", action="store_true")
    parser.add_argument("--auto-commit", action="store_true",
                        help="Auto git commit after each successful step")
    parser.add_argument("--root", default=".", help="Project root directory")
    parser.add_argument("--feature", default="",
                        help="Feature/module name used to substitute <feature> in scaffold outputs")
    parser.add_argument("--stack", default="",
                        help="Tech stack used to auto-set <ext>/<module>/<test_framework> "
                             "(e.g. react, go, python, rust). Auto-detected if omitted.")

    args = parser.parse_args()

    # feature 推断顺序：--feature > task.feature > scaffold 文件名（去掉扩展名与前置目录）
    scaffold_path = args.scaffold
    data = None
    if Path(scaffold_path).exists():
        try:
            data = yaml.safe_load(Path(scaffold_path).read_text(encoding="utf-8"))
        except Exception:
            data = None
    feature = args.feature
    if not feature and data:
        feature = str(data.get("task", {}).get("feature", "") or "")
    if not feature:
        feature = Path(scaffold_path).stem

    # 技术栈推断：--stack 优先；否则扫描项目根常见清单文件自动判断
    stack = args.stack
    if not stack:
        import re as _re
        root_p = Path(args.root).resolve()
        try:
            pkg = root_p / "package.json"
            if pkg.exists():
                pj = json.loads(pkg.read_text(encoding="utf-8"))
                deps = {**pj.get("dependencies", {}), **pj.get("devDependencies", {})}
                for name in ("react", "next", "vue", "svelte", "angular", "express", "fastify"):
                    if name in deps:
                        stack = name
                        break
                if not stack:
                    stack = "typescript" if ("typescript" in deps or (root_p / "tsconfig.json").exists()) else "javascript"
            elif (root_p / "go.mod").exists():
                stack = "go"
            elif (root_p / "Cargo.toml").exists():
                stack = "rust"
            elif (root_p / "pyproject.toml").exists() or (root_p / "requirements.txt").exists():
                stack = "python"
        except Exception:
            stack = ""

    sys.exit(run_scaffold(
        scaffold_path=scaffold_path,
        provider=args.provider,
        dry_run=args.dry_run,
        auto_commit=args.auto_commit,
        project_root=Path(args.root).resolve(),
        feature=feature,
        stack=stack,
    ))


if __name__ == "__main__":
    main()
