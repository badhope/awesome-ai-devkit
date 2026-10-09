#!/usr/bin/env python3
# ──────────────────────────────────────────────────────────────────────
# Awesome AI DevKit — devkit-doctor v2.0
#
# 安装健康检查工具。扫描当前项目并报告 skill/scaffold/mcp/hooks/env 状态。
#
# usage:
#   python3 devkit-doctor.py                           # 运行全部检查
#   python3 devkit-doctor.py --format json             # JSON 输出
#   python3 devkit-doctor.py --check skills            # 只检查 skills
#   python3 devkit-doctor.py --root /path/to/project   # 指定项目根
#   python3 devkit-doctor.py --fix                       # 尝试自动修复
#   python3 devkit-doctor.py --verbose / -v              # 显示详细信息
#   python3 devkit-doctor.py --version                   # 显示版本号
# ──────────────────────────────────────────────────────────────────────

import argparse
import json
import os
import re
import stat
import subprocess
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional

try:
    import yaml
except ImportError:
    sys.exit("[ERROR] 需要 PyYAML:  pip install pyyaml")


# ── 版本信息 ─────────────────────────────────────────────────────────

__version__ = "2.0.0"


# ── ANSI 色彩系统（无第三方依赖） ─────────────────────────────────────

class Color:
    """ANSI 转义码色彩系统 — 纯原生，无需 colorama"""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"

    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"

    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"

    @staticmethod
    def supports_color() -> bool:
        """检测当前终端是否支持 ANSI 色彩"""
        if os.environ.get("NO_COLOR"):
            return False
        if os.environ.get("FORCE_COLOR"):
            return True
        if os.name == "nt":
            # Windows 10+ 启用 ANSI 支持
            try:
                kernel32 = __import__("ctypes").windll.kernel32
                # ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
                return True
            except Exception:
                return "ANSICON" in os.environ or "WT_SESSION" in os.environ
        return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

    @staticmethod
    def strip(text: str) -> str:
        """移除所有 ANSI 转义码（用于纯文本输出模式）"""
        return re.sub(r"\033\[[0-9;]*m", "", text)


USE_COLOR = Color.supports_color()


def c(text: str, *codes: str) -> str:
    """给文本上色。如果不支持色彩则返回原文"""
    if not USE_COLOR:
        return text
    return "".join(codes) + text + Color.RESET


def cb(text: str, color_code: str) -> str:
    """快捷：单色文本"""
    return c(text, color_code)


def cbold(text: str, color_code: str = "") -> str:
    """快捷：加粗着色"""
    if color_code:
        return c(text, Color.BOLD, color_code)
    return c(text, Color.BOLD)


# ── ASCII Banner ─────────────────────────────────────────────────────

BANNER = r"""
 █████╗ ██╗    ██████╗ ███████╗██╗   ██╗██╗  ██╗██╗████████╗
██╔══██╗██║    ██╔══██╗██╔════╝██║   ██║██║ ██╔╝██║╚══██╔══╝
███████║██║    ██║  ██║█████╗  ██║   ██║█████╔╝ ██║   ██║
██╔══██║██║    ██║  ██║██╔══╝  ╚██╗ ██╔╝██╔═██╗ ██║   ██║
██║  ██║██║    ██████╔╝███████╗ ╚████╔╝ ██║  ██╗██║   ██║
╚═╝  ╚═╝╚═╝    ╚═════╝ ╚══════╝  ╚═╝   ╚═╝  ╚═╝╚═╝   ╚═╝
"""


def print_banner():
    """打印顶部 ASCII Banner + 版本信息"""
    lines = BANNER.rstrip().split("\n")
    for line in lines:
        print(cbold(line, Color.CYAN))
    version_str = f"devkit-doctor v{__version__} — Installation Health Check"
    padding = max(0, (56 - len(Color.strip(version_str))) // 2)
    print(" " * padding + cbold(version_str, Color.DIM))
    print(" " * 12 + c("─" * 44, Color.DIM))
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(" " * 12 + c(f"Scanned at {timestamp}", Color.DIM))
    print()


# ── 数据模型 ─────────────────────────────────────────────────────────


class CheckResult(Enum):
    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"
    INFO = "info"


@dataclass
class Finding:
    result: CheckResult
    message: str
    fix_hint: str = ""
    detail: str = ""  # verbose-only extra info


@dataclass
class CheckReport:
    name: str
    description: str = ""
    findings: list[Finding] = field(default_factory=list)
    fixed: list[str] = field(default_factory=list)  # 自动修复记录

    @property
    def result(self) -> CheckResult:
        if any(f.result == CheckResult.FAIL for f in self.findings):
            return CheckResult.FAIL
        if any(f.result == CheckResult.WARN for f in self.findings):
            return CheckResult.WARN
        return CheckResult.PASS

    @property
    def pass_count(self) -> int:
        return sum(1 for f in self.findings if f.result == CheckResult.PASS)

    @property
    def fail_count(self) -> int:
        return sum(1 for f in self.findings if f.result == CheckResult.FAIL)

    @property
    def warn_count(self) -> int:
        return sum(1 for f in self.findings if f.result == CheckResult.WARN)


# ── 抽象检查器 ───────────────────────────────────────────────────────


class BaseCheck(ABC):
    name: str = "base"
    description: str = ""

    def __init__(self, root: Path, verbose: bool = False, auto_fix: bool = False):
        self.root = root
        self.verbose = verbose
        self.auto_fix = auto_fix

    @abstractmethod
    def run(self) -> CheckReport:
        ...


# ── 检查器实现 ───────────────────────────────────────────────────────

# 合法工具名集合（CatPaw / Cursor / 通用 AI coding agent 工具）
KNOWN_TOOLS = {
    "read_file", "glob_file_search", "grep", "bash", "write",
    "codebase_search", "project_layout", "web_search", "web_fetch",
    "read_lints", "list_dir", "read_file_for_edit",
    # common aliases
    "file_read", "file_write", "shell", "terminal",
    "search_files", "search_code",
}

# 已知废弃/不存在的工具名
DEPRECATED_TOOLS = {
    "python", "create_fixchain_trace", "feature_map",
    "read_multiple_files", "create_plan",
    "enable_in_context_learning",
    "edit_file",  # deprecated, replaced by string_replace / multi_edit
    "string_replace",   # internal tool name, check context
    "multi_edit",       # internal tool name, check context
}


class SkillIntegrityCheck(BaseCheck):
    """检查所有 SKILL.md 是否存在且 frontmatter 合法"""

    name = "skills"
    description = "检查 skills/ 数量和 frontmatter 格式"

    def run(self) -> CheckReport:
        report = CheckReport(self.name, self.description)
        # 通用技能优先：框架层 framework/skills，其次场景 skills，再根 skills
        skills_dir = self.root / "framework" / "skills"
        if not skills_dir.exists():
            skills_dir = self.root / "scenarios" / "programming" / "fullstack" / "skills"
        if not skills_dir.exists():
            skills_dir = self.root / "skills"
        if not skills_dir.exists():
            report.findings.append(Finding(CheckResult.FAIL, "skills/ 目录不存在",
                                           "请确认项目根目录正确或创建 framework/skills"))
            return report

        skill_dirs = sorted([d for d in skills_dir.iterdir() if d.is_dir()])
        missing = []
        bad_frontmatter = []
        no_description = []
        frontmatter_issues = []
        for d in skill_dirs:
            skill_md = d / "SKILL.md"
            if not skill_md.exists():
                missing.append(d.name)
                continue
            content = skill_md.read_text(encoding="utf-8")
            if not content.strip().startswith("---"):
                bad_frontmatter.append(d.name)
                continue
            # parse frontmatter for name and description
            fm_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
            if fm_match:
                try:
                    fm = yaml.safe_load(fm_match.group(1))
                    if isinstance(fm, dict):
                        if not fm.get("name"):
                            frontmatter_issues.append((d.name, "缺少 name 字段"))
                        if not fm.get("description"):
                            no_description.append(d.name)
                            frontmatter_issues.append((d.name, "缺少 description 字段"))
                except yaml.YAMLError:
                    frontmatter_issues.append((d.name, "YAML frontmatter 解析失败"))
            else:
                bad_frontmatter.append(d.name)

        total = len(skill_dirs)
        if missing:
            report.findings.append(Finding(
                CheckResult.FAIL,
                f"缺失 SKILL.md: {', '.join(missing)}",
                f"在 {skills_dir}/<name>/ 下创建 SKILL.md"))
        if bad_frontmatter:
            report.findings.append(Finding(
                CheckResult.WARN,
                f"SKILL.md 无/YAML frontmatter: {', '.join(bad_frontmatter)}",
                "请在 SKILL.md 开头添加 YAML frontmatter (---)"))
        for fname, issue in frontmatter_issues:
            if "缺少 description" not in issue:  # description is warning, reported separately
                report.findings.append(Finding(
                    CheckResult.WARN,
                    f"{fname}: {issue}",
                    "frontmatter 应含 name/description/layer/tags"))

        if no_description:
            report.findings.append(Finding(
                CheckResult.WARN,
                f"缺少 description 字段: {', '.join(n_description[:5])}" if (
                    n_description := no_description) else "",
                "添加 description: 字段提高 skill 可发现性"))

        if not missing and not bad_frontmatter and not frontmatter_issues:
            report.findings.append(Finding(
                CheckResult.PASS, f"{total}/{total} SKILL.md 存在且结构正常"))

        if self.verbose and skill_dirs:
            report.findings.append(Finding(
                CheckResult.INFO,
                f"Skills 列表: {', '.join(d.name for d in skill_dirs)}"))

        return report


class ScaffoldValidityCheck(BaseCheck):
    """检查 scaffold yaml 格式和 skill ID 引用"""

    name = "scaffolds"
    description = "检查 scaffolds/ 的 skill ID 引用是否都存在"

    def run(self) -> CheckReport:
        report = CheckReport(self.name, self.description)
        scaffold_dir = self.root / "scenarios" / "programming" / "fullstack" / "scaffolds"
        if scaffold_dir.exists():
            scaffold_files = list(scaffold_dir.glob("*.yaml")) + list(scaffold_dir.glob("*.yml"))
        elif (self.root / "scaffolds").exists():
            scaffold_files = list((self.root / "scaffolds").glob("*.yaml"))
            scaffold_files += list((self.root / "scaffolds").glob("*.yml"))
        else:
            scaffold_files = list(self.root.glob("scaffold*.yaml"))
        if not scaffold_files:
            report.findings.append(Finding(CheckResult.WARN, "未找到 scaffold yaml 文件"))
            return report

        skills_dir = self.root / "framework" / "skills"
        if not skills_dir.exists():
            skills_dir = self.root / "scenarios" / "programming" / "fullstack" / "skills"
        valid_skills = {d.name for d in skills_dir.iterdir() if d.is_dir()} if skills_dir.exists() else set()

        errors = []
        total_steps = 0
        total_skills_used = set()
        for sf in scaffold_files:
            try:
                data = yaml.safe_load(sf.read_text(encoding="utf-8"))
                if not data or not isinstance(data, dict):
                    errors.append(f"{sf.name}: 格式错误或为空")
                    continue
                steps = data.get("steps", [])
                for step in steps:
                    if isinstance(step, dict):
                        total_steps += 1
                        for skill in step.get("skills", []):
                            total_skills_used.add(skill)
                            if valid_skills and skill not in valid_skills:
                                errors.append(f"{sf.name}: 引用了不存在的 skill '{skill}'")
            except yaml.YAMLError as e:
                errors.append(f"{sf.name}: YAML 解析错误 - {e}")

        if errors:
            for e in errors[:10]:
                report.findings.append(Finding(CheckResult.FAIL, e, "修正 scaffold yaml"))
            if len(errors) > 10:
                report.findings.append(Finding(
                    CheckResult.INFO, f"... 还有 {len(errors) - 10} 个问题"))
        else:
            report.findings.append(Finding(
                CheckResult.PASS,
                f"{len(scaffold_files)} 个 scaffold 有效, {total_steps} 个步骤"))

        if self.verbose:
            report.findings.append(Finding(
                CheckResult.INFO,
                f"共使用 {len(total_skills_used)} 个 skill: {', '.join(sorted(total_skills_used))}"))

        return report


class MCPConfigCheck(BaseCheck):
    """检查 mcp-config.yaml 格式和引用"""

    name = "mcp"
    description = "检查 mcp-config.yaml 格式和引用"

    def run(self) -> CheckReport:
        report = CheckReport(self.name, self.description)
        mcp_configs = list(self.root.rglob("mcp-config.yaml"))
        if not mcp_configs:
            # also check .json configs
            mcp_configs = list(self.root.rglob("*-mcp*.json"))
        if not mcp_configs:
            report.findings.append(Finding(CheckResult.WARN, "未找到 mcp-config.yaml"))
            return report

        for cfg in mcp_configs:
            if cfg.suffix == ".json":
                self._check_json_config(cfg, report)
            else:
                self._check_yaml_config(cfg, report)

        return report

    def _check_yaml_config(self, cfg: Path, report: CheckReport):
        try:
            data = yaml.safe_load(cfg.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                report.findings.append(Finding(CheckResult.FAIL, f"{cfg.name}: 根结构不是 map"))
                return
            servers = data.get("servers", {})
            if not isinstance(servers, dict):
                report.findings.append(Finding(CheckResult.FAIL, f"{cfg.name}: servers 格式错误"))
                return
            enabled = [n for n, c in servers.items() if isinstance(c, dict) and c.get("enabled")]
            disabled = [n for n, c in servers.items() if isinstance(c, dict) and not c.get("enabled")]
            report.findings.append(Finding(
                CheckResult.PASS,
                f"{cfg.relative_to(self.root)}: {len(enabled)}/{len(servers)} servers enabled"))
            # check settings
            settings = data.get("settings", {})
            if settings:
                if settings.get("auto_restart"):
                    report.findings.append(Finding(
                        CheckResult.INFO,
                        f"auto_restart 已启用 (max_attempts={settings.get('restart_max_attempts', '?')})"))
            # check missing command in enabled servers
            for name, conf in servers.items():
                if isinstance(conf, dict) and conf.get("enabled") and not conf.get("command"):
                    report.findings.append(Finding(
                        CheckResult.WARN,
                        f"Server '{name}' enabled 但未配置 command",
                        f"添加 command 字段给 {name}"))
            if self.verbose:
                report.findings.append(Finding(
                    CheckResult.INFO,
                    f"Enabled: {', '.join(enabled)}"))
                report.findings.append(Finding(
                    CheckResult.INFO,
                    f"Disabled: {', '.join(disabled)}"))
        except Exception as e:
            report.findings.append(Finding(CheckResult.FAIL, f"{cfg.name}: {e}"))

    def _check_json_config(self, cfg: Path, report: CheckReport):
        try:
            data = json.loads(cfg.read_text(encoding="utf-8"))
            if "mcpServers" in data:
                servers = data["mcpServers"]
                report.findings.append(Finding(
                    CheckResult.PASS,
                    f"{cfg.relative_to(self.root)}: {len(servers)} 个 MCP servers"))
            elif "servers" in data:
                servers = data["servers"]
                report.findings.append(Finding(
                    CheckResult.PASS,
                    f"{cfg.relative_to(self.root)}: {len(servers)} 个 MCP servers"))
            else:
                report.findings.append(Finding(
                    CheckResult.WARN, f"{cfg.name}: 未识别的结构"))
        except json.JSONDecodeError as e:
            report.findings.append(Finding(CheckResult.FAIL, f"{cfg.name}: JSON 错误 - {e}"))


class HooksCheck(BaseCheck):
    """检查 hooks/scripts/ 所有脚本是否存在且可执行"""

    name = "hooks"
    description = "检查 hooks/scripts/ 脚本存在性和可执行性"

    def run(self) -> CheckReport:
        report = CheckReport(self.name, self.description)
        hooks_dir = self.root / "hooks" / "scripts"
        if not hooks_dir.exists():
            report.findings.append(Finding(CheckResult.FAIL, "hooks/scripts/ 不存在",
                                           "创建 hooks/scripts/ 目录"))
            if self.auto_fix:
                try:
                    hooks_dir.mkdir(parents=True, exist_ok=True)
                    report.fixed.append("创建 hooks/scripts/ 目录")
                except OSError as e:
                    report.findings.append(Finding(CheckResult.FAIL, f"自动修复失败: {e}"))
            return report

        scripts = list(hooks_dir.glob("*.sh")) + list(hooks_dir.glob("*.py"))
        if not scripts:
            report.findings.append(Finding(CheckResult.WARN, "hooks/scripts/ 下无脚本"))
            self._check_fullstack_hooks(report)
            return report

        # check executability (Unix only)
        non_exec = []
        broken_shebang = []
        for s in scripts:
            if os.name != "nt":
                if not os.access(s, os.X_OK):
                    non_exec.append(s.name)
                    if self.auto_fix:
                        try:
                            s.chmod(s.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
                            report.fixed.append(f"chmod +x {s.name}")
                        except OSError as e:
                            report.findings.append(Finding(
                                CheckResult.WARN, f"chmod 失败 {s.name}: {e}"))
            # check shebang
            if s.suffix == ".sh":
                first_line = s.read_text(encoding="utf-8").split("\n")[0] if s.exists() else ""
                if not first_line.startswith("#!"):
                    broken_shebang.append(s.name)

        if non_exec and not self.auto_fix:
            report.findings.append(Finding(
                CheckResult.WARN,
                f"脚本不可执行: {', '.join(non_exec)}",
                f"chmod +x {' '.join(non_exec)}"))
        if broken_shebang:
            report.findings.append(Finding(
                CheckResult.WARN,
                f".sh 缺少 shebang: {', '.join(broken_shebang)}",
                "添加 #!/usr/bin/env bash 或 #!/bin/bash"))

        # count ok scripts
        ok_count = len(scripts) - len(non_exec)
        report.findings.append(Finding(
            CheckResult.PASS,
            f"{ok_count}/{len(scripts)} hooks 脚本就绪"))

        # check config.yaml references
        self._check_fullstack_hooks(report)

        if self.verbose:
            report.findings.append(Finding(
                CheckResult.INFO,
                f"脚本列表: {', '.join(s.name for s in scripts)}"))

        return report

    def _check_fullstack_hooks(self, report: CheckReport):
        """检查 fullstack 场景的 hooks config.yaml"""
        fullstack_hooks = self.root / "scenarios" / "programming" / "fullstack" / "hooks" / "config.yaml"
        if fullstack_hooks.exists():
            try:
                cfg = yaml.safe_load(fullstack_hooks.read_text(encoding="utf-8"))
                refs = []
                for section in cfg.get("hooks", {}).values():
                    if isinstance(section, dict):
                        for hook_list in section.values():
                            if isinstance(hook_list, list):
                                for h in hook_list:
                                    if isinstance(h, dict):
                                        script_path = h.get("script") or h.get("path")
                                        if script_path:
                                            refs.append(script_path)
                # 路径解析：fullstack hooks config.yaml 位于 fullstack/hooks/，
                # 其内部引用的路径如 "hooks/scripts/foo.sh" 对应的是
                # fullstack/hooks/scripts/foo.sh，即相对于 config 文件的两级父目录
                missing_refs = []
                config_dir = fullstack_hooks.parent  # fullstack/hooks/
                config_grandparent = config_dir.parent  # fullstack/
                for r in refs:
                    resolved = config_dir / r  # fullstack/hooks/ + hooks/scripts/...
                    if not resolved.exists():
                        resolved = config_grandparent / r  # fullstack/ + hooks/scripts/...
                    if not resolved.exists():
                        resolved = self.root / r  # project root + hooks/scripts/...
                    if not resolved.exists():
                        missing_refs.append(r)
                if missing_refs:
                    report.findings.append(Finding(
                        CheckResult.FAIL,
                        f"config.yaml 引用了不存在的脚本: {', '.join(missing_refs)}"))
                elif refs:
                    report.findings.append(Finding(
                        CheckResult.PASS, f"{len(refs)} 个引用脚本全部存在"))
            except Exception as e:
                report.findings.append(Finding(
                    CheckResult.FAIL, f"fullstack hooks/config.yaml 解析错误: {e}"))

        # root hooks config
        root_config = self.root / "hooks" / "config.yaml"
        if root_config.exists():
            try:
                cfg = yaml.safe_load(root_config.read_text(encoding="utf-8"))
                refs = set()
                for section in cfg.get("hooks", {}).values():
                    if isinstance(section, dict):
                        for hook_list in section.values():
                            if isinstance(hook_list, list):
                                for h in hook_list:
                                    if isinstance(h, dict) and "script" in h:
                                        refs.add(h["script"])
                missing_refs = [r for r in refs if not (self.root / r).exists()]
                if missing_refs:
                    report.findings.append(Finding(
                        CheckResult.FAIL,
                        f"root config.yaml 引用不存在的脚本: {', '.join(missing_refs)}"))
            except Exception:
                pass


class AgentToolsCheck(BaseCheck):
    """检查 agents/ 的 tools 列表是否合理"""

    name = "agents"
    description = "检查 agents/ 的 tools 列表是否合理（不含已废弃工具名）"

    DEPRECATED_TOOLS_LOCAL = {
        "python", "create_fixchain_trace", "feature_map",
    }

    def run(self) -> CheckReport:
        report = CheckReport(self.name, self.description)
        agents_dir = self.root / "framework" / "agents"
        if not agents_dir.exists():
            agents_dir = self.root / "scenarios" / "programming" / "fullstack" / "agents"
        if not agents_dir.exists():
            agents_dir = self.root / "agents"
        if not agents_dir.exists():
            report.findings.append(Finding(CheckResult.WARN, "agents/ 目录不存在"))
            return report

        agent_files = list(agents_dir.glob("*.md"))
        if not agent_files:
            report.findings.append(Finding(CheckResult.WARN, "agents/ 下无 .md 文件"))
            return report

        total_agents = 0
        deprecated_found = []
        unknown_tools = []
        tools_missing = []

        for af in agent_files:
            content = af.read_text(encoding="utf-8")
            # extract frontmatter
            fm_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
            if not fm_match:
                continue
            total_agents += 1
            try:
                fm = yaml.safe_load(fm_match.group(1))
            except yaml.YAMLError:
                continue
            tools_str = fm.get("tools", "")
            if not tools_str:
                tools_missing.append(af.stem)
                continue
            # parse tools list (comma-separated in frontmatter)
            tools = [t.strip() for t in re.split(r"[,，\s]+", str(tools_str)) if t.strip()]
            for tool in tools:
                if tool.lower() in self.DEPRECATED_TOOLS_LOCAL:
                    deprecated_found.append((af.stem, tool))
                elif tool.lower() not in KNOWN_TOOLS and tool not in {
                    "string_replace", "multi_edit"
                }:
                    # Not necessarily an error, just informational
                    pass

        if deprecated_found:
            for agent, tool in deprecated_found:
                report.findings.append(Finding(
                    CheckResult.FAIL,
                    f"{agent}: 使用了废弃工具 '{tool}'",
                    f"从 frontmatter tools 中移除 '{tool}'"))
        if tools_missing:
            report.findings.append(Finding(
                CheckResult.WARN,
                f"未声明 tools 的 agent: {', '.join(tools_missing[:10])}",
                "在 frontmatter 中添加 tools: 字段"))

        if not deprecated_found:
            report.findings.append(Finding(
                CheckResult.PASS,
                f"{total_agents} 个 agent 的 tools 声明均有效"))

        if self.verbose and agent_files:
            report.findings.append(Finding(
                CheckResult.INFO,
                f"Agents: {', '.join(af.stem for af in agent_files)}"))

        return report


class JSONFormatCheck(BaseCheck):
    """检查 JSON 文件格式（plugin.json、*.json）"""

    name = "json"
    description = "检查 JSON 文件格式正确性"

    def run(self) -> CheckReport:
        report = CheckReport(self.name, self.description)
        # find important JSON files
        json_files = []
        # root-level JSON
        for pattern in ["*.json", "experts/*.json"]:
            json_files.extend(self.root.glob(pattern))
        # mcp config JSON
        json_files.extend((self.root / "mcp" / "config").glob("*.json"))
        # .catpaw-plugin
        json_files.extend(self.root.rglob(".catpaw-plugin/*.json"))

        # de-duplicate
        seen = set()
        unique_files = []
        for f in json_files:
            if f not in seen:
                seen.add(f)
                unique_files.append(f)
        json_files = sorted(unique_files)

        if not json_files:
            report.findings.append(Finding(CheckResult.WARN, "未找到 JSON 文件"))
            return report

        invalid = []
        valid_count = 0
        for jf in json_files:
            try:
                json.loads(jf.read_text(encoding="utf-8"))
                valid_count += 1
            except json.JSONDecodeError as e:
                invalid.append((jf.relative_to(self.root), str(e)))

        if invalid:
            for path, err in invalid[:5]:
                report.findings.append(Finding(
                    CheckResult.FAIL, f"{path}: {err}", "修正 JSON 语法错误"))
        else:
            report.findings.append(Finding(
                CheckResult.PASS, f"{valid_count}/{len(json_files)} JSON 文件有效"))

        if self.verbose:
            report.findings.append(Finding(
                CheckResult.INFO,
                f"JSON 文件: {', '.join(str(f.relative_to(self.root)) for f in json_files)}"))

        return report


class DocLinksCheck(BaseCheck):
    """检查文档链接有效性（README.md 中的本地链接）"""

    name = "docs"
    description = "检查文档链接有效性（README.md 中的本地链接）"

    def run(self) -> CheckReport:
        report = CheckReport(self.name, self.description)
        readme = self.root / "README.md"
        if not readme.exists():
            report.findings.append(Finding(CheckResult.WARN, "README.md 不存在"))
            return report

        content = readme.read_text(encoding="utf-8")
        # find local relative links: [text](path/to/file)
        local_links = re.findall(r"\]\((?!http|https|mailto|#)([^)]+)\)", content)
        # exclude anchor-only and absolute URLs
        local_links = [l for l in local_links if not l.startswith("#") and "/" in l or "." in l.split("#")[0]]

        broken = []
        checked = 0
        for link in local_links:
            anchor = ""
            if "#" in link:
                link, anchor = link.split("#", 1)
            if not link:
                continue
            target = self.root / link
            checked += 1
            if not target.exists():
                broken.append(link)

        if broken:
            for b in broken[:10]:
                report.findings.append(Finding(
                    CheckResult.WARN,
                    f"README.md 中链接失效: {b}",
                    f"创建文件 {b} 或更新链接"))
        elif checked > 0:
            report.findings.append(Finding(
                CheckResult.PASS, f"README.md 中 {checked} 个本地链接全部有效"))
        else:
            report.findings.append(Finding(
                CheckResult.INFO, "README.md 中无本地文件链接"))

        # check README_zh.md too
        readme_zh = self.root / "README_zh.md"
        if readme_zh.exists():
            zh_content = readme_zh.read_text(encoding="utf-8")
            zh_links = re.findall(r"\]\((?!http|https|mailto|#)([^)]+)\)", zh_content)
            zh_broken = []
            for link in zh_links:
                if "#" in link:
                    link = link.split("#", 0)[0]
                if not link:
                    continue
                if not (self.root / link).exists():
                    zh_broken.append(link)
            if zh_broken:
                report.findings.append(Finding(
                    CheckResult.WARN,
                    f"README_zh.md 中 {len(zh_broken)} 个链接失效",
                    "同步更新中英文 README"))

        return report


class GitStatusCheck(BaseCheck):
    """检查 Git 仓库状态"""

    name = "git"
    description = "检查 Git 仓库状态（远程配置、未提交修改）"

    def run(self) -> CheckReport:
        report = CheckReport(self.name, self.description)
        git_dir = self.root / ".git"
        if not git_dir.exists():
            report.findings.append(Finding(
                CheckResult.WARN, "非 Git 仓库", "运行 git init"))
            return report

        # check remote
        try:
            result = subprocess.run(
                ["git", "remote", "-v"], capture_output=True, text=True,
                timeout=10, cwd=str(self.root))
            remotes = result.stdout.strip()
            if remotes:
                remotes_list = [line.split("\t")[0] for line in remotes.split("\n") if "\t" in line]
                unique_remotes = list(dict.fromkeys(remotes_list))
                report.findings.append(Finding(
                    CheckResult.PASS,
                    f"Remote 配置: {', '.join(unique_remotes)}"))
            else:
                report.findings.append(Finding(
                    CheckResult.WARN, "未配置 remote 仓库",
                    "git remote add origin <url>"))
        except Exception as e:
            report.findings.append(Finding(CheckResult.WARN, f"检查 remote 失败: {e}"))

        # check uncommitted changes
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"], capture_output=True, text=True,
                timeout=10, cwd=str(self.root))
            changes = [line for line in result.stdout.strip().split("\n") if line.strip()]
            if changes:
                report.findings.append(Finding(
                    CheckResult.WARN,
                    f"有 {len(changes)} 个未提交修改",
                    "git add . && git commit -m '...'"))
                if self.verbose:
                    for ch in changes[:20]:
                        report.findings.append(Finding(
                            CheckResult.INFO, f"  {ch}"))
            else:
                report.findings.append(Finding(
                    CheckResult.PASS, "工作区干净，无未提交修改"))
        except Exception as e:
            report.findings.append(Finding(CheckResult.WARN, f"检查 status 失败: {e}"))

        # check current branch
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"], capture_output=True, text=True,
                timeout=10, cwd=str(self.root))
            branch = result.stdout.strip()
            if branch:
                report.findings.append(Finding(
                    CheckResult.INFO, f"当前分支: {branch}"))
        except Exception:
            pass

        return report


class EnvDependencyCheck(BaseCheck):
    """检查环境依赖版本"""

    name = "env"
    description = "检查环境依赖版本"

    MIN_VERSIONS = {"git": (2, 0), "node": (18, 0), "python": (3, 10)}

    def _get_version(self, cmd: str) -> Optional[tuple]:
        try:
            result = subprocess.run(
                [cmd, "--version"], capture_output=True, text=True, timeout=10)
            output = result.stdout + result.stderr
            match = re.search(r"(\d+)\.(\d+)(?:\.\d+)?", output)
            if match:
                return int(match.group(1)), int(match.group(2))
        except Exception:
            pass
        return None

    def run(self) -> CheckReport:
        report = CheckReport(self.name, self.description)
        for tool, (major, minor) in self.MIN_VERSIONS.items():
            ver = self._get_version(tool)
            if ver is None:
                report.findings.append(Finding(
                    CheckResult.FAIL,
                    f"{tool} 未安装",
                    f"请安装 {tool} >={major}.{minor}"))
            elif ver < (major, minor):
                report.findings.append(Finding(
                    CheckResult.WARN,
                    f"{tool} v{ver[0]}.{ver[1]} < 最低要求 v{major}.{minor}"))
            else:
                report.findings.append(Finding(
                    CheckResult.PASS,
                    f"{tool} v{ver[0]}.{ver[1]}"))
        # additional tools (non-blocking)
        extra_tools = ["docker", "npm"]
        for tool in extra_tools:
            ver = self._get_version(tool)
            if ver:
                report.findings.append(Finding(
                    CheckResult.INFO, f"{tool} v{ver[0]}.{ver[1]} (可选)"))
        return report


# ── 检查器注册表 ─────────────────────────────────────────────────────

ALL_CHECKS = [
    SkillIntegrityCheck,
    ScaffoldValidityCheck,
    MCPConfigCheck,
    HooksCheck,
    AgentToolsCheck,
    JSONFormatCheck,
    DocLinksCheck,
    GitStatusCheck,
    EnvDependencyCheck,
]


# ── 输出格式化 ───────────────────────────────────────────────────────

RESULT_ICONS = {
    CheckResult.PASS: ("✓", Color.GREEN),
    CheckResult.FAIL: ("✗", Color.RED),
    CheckResult.WARN: ("⚠", Color.YELLOW),
    CheckResult.INFO: ("●", Color.BLUE),
}

RESULT_LABELS = {
    CheckResult.PASS: "PASS",
    CheckResult.FAIL: "FAIL",
    CheckResult.WARN: "WARN",
    CheckResult.INFO: "INFO",
}


def _human_list(items: list[str], max_show: int = 5) -> str:
    """将列表格式化为可读字符串，超过 max_show 则折叠"""
    if len(items) <= max_show:
        return ", ".join(items)
    shown = ", ".join(items[:max_show])
    return f"{shown} ... +{len(items) - max_show} more"


def format_text(reports: list[CheckReport], verbose: bool = False) -> str:
    """彩色文本格式输出"""
    print_banner()

    lines = []
    total_pass = 0
    total_fail = 0
    total_warn = 0
    total_checks = len(reports)

    for r in reports:
        # section header with colored result badge
        icon, color = RESULT_ICONS[r.result]
        label = RESULT_LABELS[r.result]

        # Choose badge style: background-colored label with white text
        bg_colors = {
            CheckResult.PASS: Color.BG_GREEN,
            CheckResult.FAIL: Color.BG_RED,
            CheckResult.WARN: Color.BG_YELLOW,
        }
        bg = bg_colors.get(r.result, Color.BG_BLUE)
        if USE_COLOR:
            badge = f"\033[1m{bg}\033[97m {icon} [{label}] \033[0m"
        else:
            badge = f" {icon} [{label}] "

        section_title = cbold(f"  {r.name.upper()}", color)
        if r.description:
            section_title += c(f"  —  {r.description}", Color.DIM)
        lines.append(section_title)
        lines.append(badge)

        for f in r.findings:
            if f.result == CheckResult.INFO and not verbose:
                continue
            fin_icon, fin_color = RESULT_ICONS[f.result]
            indent = "    "
            lines.append(f"{indent}{c(fin_icon, fin_color)} {f.message}")
            if f.fix_hint:
                lines.append(f"{indent}  {c('→', Color.CYAN)} {c(f.fix_hint, Color.DIM)}")
            if f.detail and verbose:
                lines.append(f"{indent}  {c(f.detail, Color.DIM)}")

        # show auto-fix results
        if r.fixed:
            fix_msg = c(f"    已自动修复: {_human_list(r.fixed)}", Color.GREEN)
            lines.append(fix_msg)

        lines.append("")

        # count
        if r.result == CheckResult.PASS:
            total_pass += 1
        elif r.result == CheckResult.FAIL:
            total_fail += 1
        elif r.result == CheckResult.WARN:
            total_warn += 1

    # ── Summary ─────────────────────────────────────────────────────
    lines.append(c("─" * 56, Color.DIM))
    lines.append("")
    if total_fail == 0 and total_warn == 0:
        summary = cbold(f"  {total_pass}/{total_checks} 检查全部通过", Color.GREEN)
    elif total_fail > 0:
        summary = cbold(
            f"  {total_pass}/{total_checks} 通过 · {total_fail} 失败 · {total_warn} 警告",
            Color.RED)
    else:
        summary = cbold(
            f"  {total_pass}/{total_checks} 通过 · {total_warn} 警告",
            Color.YELLOW)
    lines.append(summary)

    # fix suggestions summary
    all_fixable = []
    for r in reports:
        for f in r.findings:
            if f.fix_hint and f.result in (CheckResult.FAIL, CheckResult.WARN):
                all_fixable.append((r.name, f.fix_hint))
    if all_fixable:
        lines.append("")
        lines.append(cbold("  修复建议:", Color.CYAN))
        for check_name, hint in all_fixable[:15]:
            lines.append(f"    {c('→', Color.YELLOW)} [{check_name}] {c(hint, Color.DIM)}")
        if len(all_fixable) > 15:
            lines.append(f"    {c(f'... 还有 {len(all_fixable) - 15} 条', Color.DIM)}")

    lines.append("")
    lines.append(c("─" * 56, Color.DIM))
    lines.append("")
    return "\n".join(lines)


def format_json(reports: list[CheckReport]) -> str:
    result = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "generator": f"devkit-doctor v{__version__}",
        "checks": [
            {
                "name": r.name,
                "description": r.description,
                "result": r.result.value,
                "fixed": r.fixed,
                "findings": [
                    {
                        "result": f.result.value,
                        "message": f.message,
                        "fix_hint": f.fix_hint,
                        "detail": f.detail,
                    }
                    for f in r.findings
                ],
            }
            for r in reports
        ],
        "summary": {
            "pass": sum(1 for r in reports if r.result == CheckResult.PASS),
            "fail": sum(1 for r in reports if r.result == CheckResult.FAIL),
            "warn": sum(1 for r in reports if r.result == CheckResult.WARN),
            "total": len(reports),
        },
    }
    fail = result["summary"]["fail"]
    result["exit_code"] = 1 if fail > 0 else 0
    return json.dumps(result, indent=2, ensure_ascii=False)


# ── 根目录检测 ───────────────────────────────────────────────────────


def detect_project_root(path: Path) -> Path:
    """向上查找包含 scaffolds/ 或 .cursorrules 的目录"""
    current = path.resolve()
    for _ in range(6):
        if (current / "scaffolds").exists() or (current / ".cursorrules").exists():
            return current
        if current.parent == current:
            break
        current = current.parent
    return path.resolve()


# ── CLI ──────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        prog="devkit-doctor",
        description="Awesome AI DevKit — 安装健康检查工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
examples:
  python3 devkit-doctor.py                           # 运行全部检查
  python3 devkit-doctor.py --format json             # JSON 输出
  python3 devkit-doctor.py --check skills            # 只检查 skills
  python3 devkit-doctor.py --fix                     # 自动修复问题
  python3 devkit-doctor.py --verbose                 # 显示详细信息
""",
    )
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="输出格式 (默认 text)")
    parser.add_argument("--check", default="all",
                        help="只运行指定检查 (skills|scaffolds|mcp|hooks|agents|json|docs|git|env|all)")
    parser.add_argument("--root", default=".", help="项目根目录 (默认自动检测)")
    parser.add_argument("--fix", action="store_true", default=False,
                        help="尝试自动修复可修复的问题（如 chmod +x、创建目录）")
    parser.add_argument("--verbose", "-v", action="store_true", default=False,
                        help="显示详细信息（包含 INFO 级别的检查项）")
    parser.add_argument("--version", action="version",
                        version=f"devkit-doctor {__version__}")
    parser.add_argument("--no-color", action="store_true", default=False,
                        help="禁用彩色输出")
    args = parser.parse_args()

    # 处理 --no-color
    global USE_COLOR
    if args.no_color:
        USE_COLOR = False

    root = detect_project_root(Path(args.root))
    os.chdir(root)

    # Select checks
    if args.check == "all":
        checks = ALL_CHECKS
    else:
        checks = [c for c in ALL_CHECKS if c.name == args.check]
        if not checks:
            sys.exit(f"[ERROR] 未知检查: {args.check}. 可用: {', '.join(c.name for c in ALL_CHECKS)}")

    # Run
    reports = []
    for check_cls in checks:
        try:
            reports.append(check_cls(root, verbose=args.verbose, auto_fix=args.fix).run())
        except Exception as e:
            r = CheckReport(check_cls.name, check_cls.description)
            r.findings.append(Finding(CheckResult.FAIL, f"检查器异常: {e}"))
            reports.append(r)

    # Output
    if args.format == "json":
        print(format_json(reports))
    else:
        print(format_text(reports, verbose=args.verbose))

    # Exit code
    if any(r.result == CheckResult.FAIL for r in reports):
        sys.exit(1)
    if any(r.result == CheckResult.WARN for r in reports):
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
