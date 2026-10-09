# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] — 2026-10-06

### Added
- devkit-doctor.py — CLI health check tool covering skills/scaffolds/mcp/hooks/env
- tests/test_devkit_doctor.py — self-contained integration tests
- scaffolds/scaffold-runner.py — flat-scaffold execution engine
- scaffolds/scaffold-protocol.md — Scaffold Protocol v2.0
- scenarios/programming/fullstack/{bootstrap.sh,bootstrap.ps1}
- context/architecture.md (ADR-001)
- docs/requirements/devkit-doctor.md + docs/design/devkit-doctor.md

### Changed
- scaffold.yaml split sequential/parallel (YAML dup-key bug) → flat v2.0
- fullstack/scaffolds/*.yaml rewritten in v2.0
- hooks/scripts/{error-alert.sh,pre-task.sh} bash JSON parsing → Python inline
- mcp/config/awesome-servers.json 28 servers → 12 (removed duplicate-key hack)
- .env.example 140+ vars → 8 core vars
- README.md repositioning

### Removed
- fullstack/tools/ (26 Python utilities)
- fullstack/validation/ (5 scripts)
- hooks/scripts/middleware/ (6 orphaned middleware files)
- tools/README.md

### Fixed
- YAML duplicate key silently dropping steps
- pre-task.sh nested $() syntax error
- error-alert.sh JSON parsing failure in Git Bash
- Cross-platform bootstrap path + Python invocation

> AI生成
