# Contributing to Awesome AI DevKit

Thanks for your interest in contributing! Awesome AI DevKit is a scenario-based AI coding configuration ecosystem. Your contributions help turn AI coding tools into complete, production-ready development teams.

## Ways to contribute

- **Report issues** — bugs, broken references, or missing files in the repo
- **Add / improve a scenario** — e.g. business-ops, data-engineering, ml-native, mobile
- **Add / improve skills** — reusable `SKILL.md` modules under `scenarios/<scenario>/skills/`
- **Improve tools & workflows** — `devkit-doctor.py`, scaffolds, hooks, MCP configs
- **Improve docs** — README (en/zh), design docs, contribution guides

## Getting started

1. Fork the repository on your platform (GitCode / GitHub).
2. Clone your fork locally.
3. Create a branch: `git checkout -b feat/my-change`.

## Development workflow

We follow a simple, transparent workflow. Keep the repo healthy:

- **Config integrity**: every `SKILL.md`, scaffold, agent, hook, and MCP config must have valid references. Run the health check before submitting:

  ```bash
  python devkit-doctor.py
  ```

- **Tests**: if you touch Python tooling, add/adjust tests and run:

  ```bash
  python -m pytest -q
  ```

- **Scaffold protocol**: when you add a workflow, keep it aligned with `scaffolds/scaffold-protocol.md` (v2.0).

## Commit conventions

We use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` new scenarios, skills, workflows, or features
- `fix:` bug fixes, broken references, path issues
- `docs:` documentation-only changes
- `chore:` maintenance, formatting, config
- `ci:` CI/CD pipeline changes

Examples:

- `feat(scenarios): add data-engineering scenario`
- `fix(bootstrap): use python instead of python3 on Windows`
- `docs(readme): clarify scenario extension`

## Pull request checklist

- [ ] `python devkit-doctor.py` passes (no FAIL)
- [ ] `python -m pytest -q` passes
- [ ] Both `README.md` and `README_zh.md` updated if behavior changes
- [ ] `CHANGELOG.md` updated under `[Unreleased]`
- [ ] No hardcoded secrets / absolute personal paths committed

## Reporting issues

Use the issue tracker. Include:

- The exact command or action that failed
- Expected vs. actual behavior
- Platform / tool version (OS, git, node, python, AI coding tool)
- Any error output from `devkit-doctor.py`

Thanks for making AI coding configuration better for everyone.
