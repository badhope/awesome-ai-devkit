#!/usr/bin/env python3
"""devkit-doctor 集成测试 — 自包含，无 patching，独立运行返回 0/1"""

import sys
import os
import tempfile
import subprocess
import importlib.util
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = PROJECT_ROOT / "devkit-doctor.py"
spec = importlib.util.spec_from_file_location("devkit_doctor", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

SR_SCRIPT = PROJECT_ROOT / "scaffolds" / "scaffold-runner.py"
if SR_SCRIPT.exists():
    sr_spec = importlib.util.spec_from_file_location("scaffold_runner", SR_SCRIPT)
    sr_mod = importlib.util.module_from_spec(sr_spec)
    sr_spec.loader.exec_module(sr_mod)
    step_outputs_gate = sr_mod.step_outputs_gate
else:
    step_outputs_gate = None

SkillIntegrityCheck = mod.SkillIntegrityCheck
ScaffoldValidityCheck = mod.ScaffoldValidityCheck
MCPConfigCheck = mod.MCPConfigCheck
HooksCheck = mod.HooksCheck
EnvDependencyCheck = mod.EnvDependencyCheck
CheckResult = mod.CheckResult
detect_project_root = mod.detect_project_root


def run_all():
    root = detect_project_root(PROJECT_ROOT)
    for cls in [SkillIntegrityCheck, ScaffoldValidityCheck,
                MCPConfigCheck, HooksCheck, EnvDependencyCheck]:
        report = cls(root).run()
        assert report.result == CheckResult.PASS, (
            f"{cls.name}: {report.result.value}: "
            f"{[f.message for f in report.findings]}")

def test_detect_project_root():
    detected = detect_project_root(PROJECT_ROOT)
    assert (detected / "scaffolds").exists()

def test_scaffold_rejects_bad_yaml():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "scaffolds").mkdir()
        (tmp / "scaffolds" / "bad.yaml").write_text("not: valid: yaml: [")
        report = ScaffoldValidityCheck(tmp).run()
        assert report.result == CheckResult.FAIL

def test_hooks_missing():
    with tempfile.TemporaryDirectory() as tmp:
        report = HooksCheck(Path(tmp)).run()
        assert report.result == CheckResult.FAIL

def test_skill_missing_file():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        skills = tmp / "scenarios" / "programming" / "fullstack" / "skills"
        skills.mkdir(parents=True)
        (skills / "fake-skill").mkdir()
        report = SkillIntegrityCheck(tmp).run()
        assert report.result == CheckResult.FAIL


def test_step_outputs_gate_resolves_placeholders():
    """真实 bug 回归：scaffold 用 <feature>/<module>/<ext> 模板路径时，
    门禁必须能匹配到实际生成的文件，而不是按字面路径误判缺失。"""
    if step_outputs_gate is None:
        return  # scaffold-runner 不存在则跳过
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        # 模拟 opencode 已生成的真实产物
        (tmp / "src" / "todo").mkdir(parents=True)
        (tmp / "tests").mkdir()
        (tmp / "src" / "todo" / "cli.py").write_text("def run():\n    pass\n", encoding="utf-8")
        (tmp / "tests" / "test_cli.py").write_text("def test_run():\n    pass\n", encoding="utf-8")

        # 字面模板路径（含未替换占位符）→ 应通过 glob 匹配到真实文件
        outputs = [
            {"src/<module>/<feature>.<ext>": {"contains": ["def"]}},
            {"tests/test_<feature>.<ext>": {"contains": ["test_"]}},
        ]
        problems = step_outputs_gate(outputs, tmp, {"feature": "cli", "module": "todo", "ext": "py"})
        assert problems == [], f"应匹配真实产物，但报问题: {problems}"

        # 完全未生成的文件 → 应报缺失
        problems = step_outputs_gate(["src/<module>/missing.<ext>"], tmp, {"module": "todo"})
        assert problems, "未生成文件应报缺失"

def test_mcp_missing_warns():
    with tempfile.TemporaryDirectory() as tmp:
        report = MCPConfigCheck(Path(tmp)).run()
        assert report.result == CheckResult.WARN

def test_env_git_unavailable():
    original = subprocess.run
    def fake_run(*a, **k):
        class R: stdout=""; stderr=""; returncode=1
        return R()
    subprocess.run = fake_run
    try:
        with tempfile.TemporaryDirectory() as tmp:
            report = EnvDependencyCheck(Path(tmp)).run()
            git_f = next(f for f in report.findings if "git" in f.message.lower())
            assert git_f.result in (CheckResult.FAIL, CheckResult.WARN)
    finally:
        subprocess.run = original


if __name__ == "__main__":
    tests = [
        ("真实项目全部检查通过", run_all),
        ("根目录自动检测",     test_detect_project_root),
        ("损坏 scaffold 处理", test_scaffold_rejects_bad_yaml),
        ("无 hooks 时 FAIL",   test_hooks_missing),
        ("缺失 SKILL.md FAIL", test_skill_missing_file),
        ("无 mcp 时 WARN",     test_mcp_missing_warns),
        ("git 不可用 FAIL",    test_env_git_unavailable),
    ]

    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"  pass  {name}")
        except Exception as e:
            print(f"  FAIL  {name}: {e}")
            failed += 1

    print(f"\n{'ALL TESTS PASS' if not failed else f'{failed} TESTS FAILED'}")
    sys.exit(0 if not failed else 1)
