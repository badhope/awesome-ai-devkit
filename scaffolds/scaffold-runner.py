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
) -> str:
    goal = step.get("goal", "")
    description = step.get("description", "")
    skills = step.get("skills", [])
    outputs = step.get("outputs", [])
    quality_gate = str(step.get("quality_gate", ""))

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

    # 格式化 outputs
    output_lines = []
    for out in outputs:
        if isinstance(out, dict):
            for path, criteria in out.items():
                must_contain = criteria.get("must_contain", []) if isinstance(criteria, dict) else []
                line = f"- `{path}`"
                if must_contain:
                    line += f" — must contain: {', '.join(must_contain)}"
                output_lines.append(line)
        elif isinstance(out, str):
            output_lines.append(f"- `{out}`")

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


def step_outputs_gate(outputs: list, project_root: Path) -> list[str]:
    """逐步强制：校验本步产出物文件存在 + contains 关键词。返回缺失/不满足清单。"""
    problems: list[str] = []
    for out in outputs:
        if isinstance(out, str):
            p = project_root / out
            if not p.exists():
                problems.append(f"missing: {out}")
        elif isinstance(out, dict):
            for path, criteria in out.items():
                p = project_root / path
                if not p.exists():
                    problems.append(f"missing: {path}")
                    continue
                if isinstance(criteria, dict):
                    contains = criteria.get("contains", [])
                    if contains:
                        try:
                            text = p.read_text(encoding="utf-8", errors="ignore")
                        except Exception:  # noqa: BLE001
                            text = ""
                        for kw in contains:
                            if kw not in text:
                                problems.append(f"{path} 缺含: {kw}")
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
                 auto_commit: bool, project_root: Path) -> int:

    scaffold_file = Path(scaffold_path)
    if not scaffold_file.exists():
        print(f"[ERROR] scaffold not found: {scaffold_path}")
        return 1

    data = yaml.safe_load(scaffold_file.read_text(encoding="utf-8"))
    version = data.get("version", "?")
    task = data.get("task", {})
    task_name = task.get("name", "unknown")
    raw_steps = data.get("steps", [])

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
                                           prev_errors="\n".join(errors_history[-2:]))
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
                                               prev_errors="\n".join(errors_history[-2:]))
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
                                               prev_errors="\n".join(errors_history[-2:]))
                    print(f"  Attempt {attempt}/3...")
                    ok, output, err = call_agent(prompt, provider, project_root)
                    result.agent_output = output
                    if ok:
                        # 逐步强制：校验本 step 的产出物（文件存在 + contains）
                        gate_errors = step_outputs_gate(step.get("outputs", []), project_root)
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

    args = parser.parse_args()
    sys.exit(run_scaffold(
        scaffold_path=args.scaffold,
        provider=args.provider,
        dry_run=args.dry_run,
        auto_commit=args.auto_commit,
        project_root=Path(args.root).resolve(),
    ))


if __name__ == "__main__":
    main()
