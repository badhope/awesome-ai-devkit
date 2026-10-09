#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────
# hooks/scripts/pre-task.sh
#
# 任务开工前脚手架前置钩子。
# 读取 scaffold.yaml，执行前置检查，创建 session 日志目录。
#
# 协议: scaffolds/scaffold-protocol.md (v2.0)
# 兼容: v1.0 (读取 identification.name) 和 v2.0 (读取 task.name)
#
# 调用方式:
#   hooks/scripts/pre-task.sh                    # 使用默认 scaffold.yaml
#   hooks/scripts/pre-task.sh my-feature.yaml    # 指定 scaffold 文件
#
# 退出码:
#   0 — 开工就绪
#   1 — 阻断性检查失败
# ──────────────────────────────────────────────────────────────────────

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
SCAFFOLD_FILE="${1:-scaffold.yaml}"
SESSION_ID=""
SESSION_DIR=""

cecho() { echo -e "\033[1;36m[pre-task]\033[0m $*"; }
warn()  { echo -e "\033[1;33m[pre-task ⚠]\033[0m $*"; }
err()   { echo -e "\033[1;31m[pre-task ✗]\033[0m $*"; }
ok()    { echo -e "\033[1;32m[pre-task ✓]\033[0m $*"; }

cleanup() {
    if [[ -n "${SESSION_DIR}" && -d "${SESSION_DIR}" ]]; then
        echo '{"status": "aborted", "session": "${SESSION_ID}"}' > "${SESSION_DIR}/ABORTED" 2>/dev/null || true
    fi
}
trap cleanup EXIT

cecho "Scaffold Protocol v2.0 — Pre-flight Check"

# ── Step 1: 定位 scaffold.yaml ──────────────────────────────────────
if [[ ! -f "${SCAFFOLD_FILE}" ]]; then
    err "未找到 scaffold.yaml: ${SCAFFOLD_FILE}"
    echo ""
    echo "Agent 必须创建一份 scaffold.yaml 才能开工。"
    echo "请使用模板: cp templates/project-scaffold/scaffold.yaml.template ./scaffold.yaml"
    exit 1
fi
ok "找到 scaffold: ${SCAFFOLD_FILE}"

# ── Step 2: YAML 格式校验 ───────────────────────────────────────────
if ! python3 -c "import yaml; yaml.safe_load(open('${SCAFFOLD_FILE}'))" 2>/dev/null; then
    err "scaffold.yaml 格式不合法，请检查 YAML 语法"
    exit 1
fi
ok "YAML 格式合法"

# ── Step 3: 协议版本校验 ────────────────────────────────────────────
PROTOCOL_VERSION="$(python3 -c "
import yaml
data = yaml.safe_load(open('${SCAFFOLD_FILE}'))
print(data.get('version', ''))
" 2>/dev/null || echo "")"

if [[ "${PROTOCOL_VERSION}" == "2.0" ]]; then
    ok "协议版本: v2.0"
elif [[ "${PROTOCOL_VERSION}" == "1.0" ]]; then
    warn "协议版本: v1.0（仍兼容，建议升级到 v2.0）"
else
    warn "协议版本: ${PROTOCOL_VERSION:-unknown}（期望 2.0）"
fi

# ── Step 4: 任务名已填（兼容 v1.0 + v2.0） ────────────────────────
TASK_NAME="$(python3 -c "
import yaml
data = yaml.safe_load(open('${SCAFFOLD_FILE}'))
# v2.0: task.name  |  v1.0: identification.name
name = data.get('task', {}).get('name', '') or data.get('identification', {}).get('name', '')
print(name)
" 2>/dev/null || echo "")"

if [[ -z "${TASK_NAME}" || "${TASK_NAME}" == *"<"* ]]; then
    err "task.name（或 identification.name）未填写或包含 <占位符>"
    exit 1
fi
ok "任务: ${TASK_NAME}"

# ── Step 5: project.yaml 存在检查 ──────────────────────────────────
cd "${REPO_ROOT}"
if [[ -f "context/project.yaml" ]]; then
    ok "project.yaml 已存在"
elif [[ -f "scenarios/programming/fullstack/context/project.yaml" ]]; then
    ok "project.yaml 已存在（fullstack 场景内）"
else
    warn "未找到 context/project.yaml，请先运行 bootstrap.sh / bootstrap.ps1"
fi

# ── Step 6: skills 引用检查（兼容 v1.0 + v2.0 格式） ──────────────
MISSING_SKILLS=0
SKILLS_DIR="framework/skills"

while IFS= read -r skill_id; do
    skill_id="$(echo "${skill_id}" | xargs)"
    [[ -z "${skill_id}" ]] && continue
    if [[ ! -d "${SKILLS_DIR}/${skill_id}" ]]; then
        err "引用的 skill '${skill_id}' 不在 ${SKILLS_DIR}/ 中"
        MISSING_SKILLS=$((MISSING_SKILLS + 1))
    fi
done < <(python3 -c '
import yaml, sys
data = yaml.safe_load(open(sys.argv[1]))
skills = set()
for section in ["parallel", "sequential"]:
    for step in data.get("steps", {}).get(section, []):
        for s in step.get("skills", []):
            skills.add(s)
for step in data.get("steps", []):
    if isinstance(step, dict):
        for s in step.get("skills", []):
            skills.add(s)
for s in skills:
    print(s)
' "${SCAFFOLD_FILE}" 2>/dev/null | sort -u || true)

if [[ "${MISSING_SKILLS}" != "0" && "${MISSING_SKILLS}" != "" ]]; then
    err "${MISSING_SKILLS} 个引用的 skill 不存在 — 请修正 scaffold.yaml"
    exit 1
fi
ok "所有引用的 skills 都存在"

# ── Step 7: 初始化 session ─────────────────────────────────────────
SESSION_ID="task-$(echo "${TASK_NAME}" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')-$(date +%s)"
SESSION_DIR="logs/sessions/${SESSION_ID}"
mkdir -p "${SESSION_DIR}"

cat > "${SESSION_DIR}/meta.json" << META_EOF
{
  "task": "${TASK_NAME}",
  "scaffold": "${SCAFFOLD_FILE}",
  "session_id": "${SESSION_ID}",
  "started_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "protocol_version": "${PROTOCOL_VERSION}",
  "started_by": "${USER:-unknown}",
  "git_branch": "$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'no-git')"
}
META_EOF

ok "Session 创建: ${SESSION_DIR}"

# ── Step 8: 输出环境变量 ───────────────────────────────────────────
export DEVKIT_SESSION_ID="${SESSION_ID}"
export DEVKIT_SESSION_DIR="${REPO_ROOT}/${SESSION_DIR}"
export DEVKIT_SCAFFOLD="${REPO_ROOT}/${SCAFFOLD_FILE}"

echo ""
cecho "══════════════════════════════════════════════════"
cecho "✅ 脚手架就绪 — Agent 可以开工"
cecho "   任务: ${TASK_NAME}"
cecho "   Session: ${SESSION_ID}"
cecho "   Outputs → ${SESSION_DIR}/"
cecho "══════════════════════════════════════════════════"
echo ""
echo "# Agent 请在以下环境变量下执行:"
echo "export DEVKIT_SESSION_ID=\"${SESSION_ID}\""
echo "export DEVKIT_SESSION_DIR=\"${REPO_ROOT}/${SESSION_DIR}\""
echo "export DEVKIT_SCAFFOLD=\"${REPO_ROOT}/${SCAFFOLD_FILE}\""

exit 0
