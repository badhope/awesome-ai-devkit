#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────
# hooks/scripts/bootstrap-templates.sh
#
# First-step installer — registers template environment variables
# and ensures prompt template infrastructure is ready.
#
# Called by: hooks/agent-lifecycle/on_agent_start.sh (or equivalent)
# Timeout budget: 10 seconds. Non-fatal.
# ──────────────────────────────────────────────────────────────────────
set -euo pipefail

PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "${PROJECT_ROOT}"

TEMPLATE_CONTEXT="scenarios/programming/fullstack/context/project.yaml"
TEMPLATE_SOURCE="scenarios/programming/fullstack/context/project.template.yaml"

# ── Ensure context/project.yaml exists ──────────────────────────────
if [[ ! -f "${TEMPLATE_CONTEXT}" ]]; then
    if [[ -f "${TEMPLATE_SOURCE}" ]]; then
        echo "[INFO] 创建 context/project.yaml 模板"
        cp "${TEMPLATE_SOURCE}" "${TEMPLATE_CONTEXT}"
    else
        echo "[WARN] project.template.yaml 不存在 — 跳过创建 project.yaml" >&2
    fi
fi

# ── Extract project metadata (best-effort, no yq dependency) ────────
PROJECT_NAME=""
TECH_STACK=""

if [[ -f "${TEMPLATE_CONTEXT}" ]]; then
    PROJECT_NAME="$(grep '^name' "${TEMPLATE_CONTEXT}" 2>/dev/null | head -1 | sed 's/name:\s*//' | tr -d '"' | tr -d "'" || echo '')"
    # Build tech_stack string from stack section
    STACK_FRONTEND="$(awk '/^\s\sfrontend:/{sub(/.*frontend: */,""); print; exit}' "${TEMPLATE_CONTEXT}" 2>/dev/null || echo '')"
    STACK_BACKEND="$(awk '/^\s\sbackend:/{sub(/.*backend: */,""); print; exit}' "${TEMPLATE_CONTEXT}" 2>/dev/null || echo '')"
    STACK_DATABASE="$(awk '/^\s\sdatabase:/{sub(/.*database: */,""); print; exit}' "${TEMPLATE_CONTEXT}" 2>/dev/null || echo '')"

    # Compose tech_stack
    TECH_STACK_PARTS=()
    [[ -n "${STACK_FRONTEND}" && "${STACK_FRONTEND}" != "(not set)" ]] && TECH_STACK_PARTS+=("${STACK_FRONTEND}")
    [[ -n "${STACK_BACKEND}" && "${STACK_BACKEND}" != "(not set)" ]] && TECH_STACK_PARTS+=("${STACK_BACKEND}")
    [[ -n "${STACK_DATABASE}" && "${STACK_DATABASE}" != "(not set)" ]] && TECH_STACK_PARTS+=("${STACK_DATABASE}")

    if [[ ${#TECH_STACK_PARTS[@]} -gt 0 ]]; then
        TECH_STACK="$(IFS=' + '; echo "${TECH_STACK_PARTS[*]}")"
    fi
fi

PROJECT_NAME="${PROJECT_NAME:-my-project}"
TECH_STACK="${TECH_STACK:-unknown}"

# ── Collect runtime variables ───────────────────────────────────────
CURRENT_DATE="$(date +%Y-%m-%d)"
CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'unknown')"
CURRENT_LOCALE="${LANG:-unknown}"
CURRENT_OS="$(uname -s 2>/dev/null || echo 'Unknown')"

# Count available skills
SKILLS_DIR="framework/skills"
SKILL_COUNT=0
if [[ -d "${SKILLS_DIR}" ]]; then
    SKILL_COUNT="$(find "${SKILLS_DIR}" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')"
fi

# ── Export template variables as environment ────────────────────────
export PROJECT_NAME
export TECH_STACK
export PROJECT_ROOT
export CURRENT_DATE
export CURRENT_BRANCH
export CURRENT_LOCALE
export CURRENT_OS
export SKILL_COUNT

# ── Output summary JSON ─────────────────────────────────────────────
cat <<EOF
{
  "bootstrap": "prompt-templates",
  "status": "ready",
  "project_name": "${PROJECT_NAME}",
  "tech_stack": "${TECH_STACK}",
  "project_root": "${PROJECT_ROOT}",
  "variables": {
    "project_name": "${PROJECT_NAME}",
    "tech_stack": "${TECH_STACK}",
    "project_root": "${PROJECT_ROOT}",
    "date": "${CURRENT_DATE}",
    "branch": "${CURRENT_BRANCH}",
    "locale": "${CURRENT_LOCALE}",
    "os": "${CURRENT_OS}",
    "skill_count": ${SKILL_COUNT}
  },
  "available_placeholders": [
    "{{project_name}}",
    "{{tech_stack}}",
    "{{project_root}}",
    "{{date}}",
    "{{branch}}",
    "{{locale}}",
    "{{os}}",
    "{{scaffold_type}}",
    "{{skill_count}}",
    "{{role}}"
  ],
  "bootstrapped_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

echo "[BOOTSTRAP] project=${PROJECT_NAME} stack=${TECH_STACK}" >&2
echo "[BOOTSTRAP] 提示词模板系统就绪 — 变量可在 agent frontmatter 和提示词中使用" >&2
echo "[BOOTSTRAP] 可用变量: {{project_name}} {{tech_stack}} {{date}} {{branch}} {{os}} {{locale}}" >&2

exit 0
