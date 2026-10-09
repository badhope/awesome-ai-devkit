# Security Policy

Awesome AI DevKit is a **configuration** repository: it contains roles, skills, scaffolds, hooks, and MCP server settings that configure AI coding tools. It does **not** ship runtime services or secrets, but the configs may reference environment variables, API keys, and external services.

## Supported versions

Security fixes are applied to the default `main` branch and released on the next tag.

## Reporting a vulnerability

Please **do not** open a public issue for security problems. Instead, report privately to the maintainers.

- Email / channel: report via the issue tracker **only for non-sensitive issues**. For anything involving credentials, paths, or secrets, open a **private** vulnerability report or contact the maintainers directly.
- Include: repository, scenario, affected file, the risk, and a minimal reproduction (no real keys).

We will acknowledge within 3 business days and respond with next steps.

## What we treat as a vulnerability

- Leaked or hard-coded credentials, API keys, or personal machine paths in committed files
- Prompt-injection vectors introduced by a skill, role, or scaffold that would exfiltrate user data
- Scripts that execute unsafe commands with insufficient validation
- Misconfigured MCP settings that expose local filesystem/sensitive paths

## Security best practices for contributors

- Never commit real keys. Use `${VAR}` placeholders and provide them in `.env.example` only.
- Do not commit absolute personal paths (e.g. `/Users/xxx`, `C:\Users\xxx`, `/mnt/...`). Use `${PROJECT_ROOT}` or `${workspaceFolder}`.
- Use `filesystem_block` in MCP configs to protect `.env`, `.git/`, keys, and secrets.
- Run `python devkit-doctor.py` and the bundled secret scanner before submitting.

> AI生成
