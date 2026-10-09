#!/usr/bin/env bash
# dependency-audit.sh — 多语言依赖审计统一入口
# 退出码：0=无问题 1=中低风险 2=高风险/阻断
set -euo pipefail

FORMAT="human"; SEVERITY="low"; AUTO_FIX=false; GENERATE_SBOM=false; SCAN_PATH="."

while [[ $# -gt 0 ]]; do
    case "$1" in
        --format) FORMAT="${2:-human}"; shift 2 ;;
        --severity) SEVERITY="${2:-low}"; shift 2 ;;
        --fix) AUTO_FIX=true; shift ;;
        --sbom) GENERATE_SBOM=true; shift ;;
        --path) SCAN_PATH="${2:-.}"; shift 2 ;;
        -h|--help) head -n 12 "$0" | grep "^#" | sed 's/^#\s\?//'; exit 0 ;;
        *) shift ;;
    esac
done

PROJECT_ROOT="$(git -C "${SCAN_PATH}" rev-parse --show-toplevel 2>/dev/null || echo "${SCAN_PATH}")"
TIMESTAMP="$(date -u +%Y%m%d_%H%M%S)"
REPORT_DIR="${PROJECT_ROOT}/reports"
mkdir -p "${REPORT_DIR}"
REPORT_FILE="${REPORT_DIR}/dependency-audit-${TIMESTAMP}.json"
MAX_SEVERITY=0; TOTAL_CRITICAL=0; TOTAL_HIGH=0; TOTAL_MEDIUM=0; TOTAL_LOW=0; TOTAL_FIXED=0

log_info() { echo "[INFO]  $*" >&2; }
log_error(){ echo "[ERROR] $*" >&2; }
check_tool() { command -v "$1" &>/dev/null; }

record() {
    local sev_rank=0
    case "${2,,}" in
        critical) sev_rank=4; TOTAL_CRITICAL=$((TOTAL_CRITICAL+1)) ;;
        high) sev_rank=3; TOTAL_HIGH=$((TOTAL_HIGH+1)) ;;
        medium) sev_rank=2; TOTAL_MEDIUM=$((TOTAL_MEDIUM+1)) ;;
        low) sev_rank=1; TOTAL_LOW=$((TOTAL_LOW+1)) ;;
    esac
    [[ ${sev_rank} -gt ${MAX_SEVERITY} ]] && MAX_SEVERITY=${sev_rank}
    [[ "${FORMAT}" == "human" ]] && echo "  [${2^^}] $1" >&2
}

audit_nodejs() {
    check_tool npm || { log_error "npm 未安装"; return; }
    log_info "Node.js 审计"
    local aj; aj=$(cd "${SCAN_PATH}" && npm audit --json 2>/dev/null || echo '{"error":"fail"}')
    echo "${aj}" | python3 -c "
import sys,json
d=json.load(sys.stdin)
if 'error' in d: sys.exit(0)
for n,v in d.get('vulnerabilities',{}).items():
    print(f'{n}|{v.get(\"severity\",\"low\").lower()}|')
" 2>/dev/null | while IFS='|' read -r p s _; do [[ -n "${p}" ]] && record "${p}" "${s}"; done
    [[ "${AUTO_FIX}" == true ]] && (cd "${SCAN_PATH}" && npm audit fix --only=prod 2>/dev/null || true)
}

audit_python() {
    check_tool pip-audit || { log_error "pip-audit 未安装"; return; }
    log_info "Python 审计"
    pip-audit --strict --desc --format json 2>/dev/null | python3 -c "
import sys,json
for i in json.load(sys.stdin):
    for v in i.get('ulns',[]):
        s='medium'; x=(v.get('description','') or '').lower()
        if 'rce' in x: s='critical'
        elif 'sql' in x or 'xss' in x: s='high'
        print(f\"{i.get('name','?')}|{s}|{v.get('id','')}\")
" 2>/dev/null | while IFS='|' read -r p s _; do [[ -n "${p}" ]] && record "${p}" "${s}"; done
    [[ "${AUTO_FIX}" == true ]] && pip-audit --fix 2>/dev/null || true
}

audit_go() {
    check_tool govulncheck || { log_error "govulncheck 未安装"; return; }
    log_info "Go 审计"
    (cd "${SCAN_PATH}" && govulncheck -json ./... 2>/dev/null) | python3 -c "
import sys,json
for l in sys.stdin:
    d=json.loads(l.strip())
    if d.get('type')!='vulnerability': continue
    o=d.get('osv',{}); s='medium'; x=(o.get('details','') or '').lower()
    if 'rce' in x or 'code' in x: s='critical'
    elif 'panic' in x: s='high'
    print(f\"{o.get('id','?')}|{s}|\")
" 2>/dev/null | while IFS='|' read -r p s _; do [[ -n "${p}" ]] && record "${p}" "${s}"; done
}

audit_rust() {
    check_tool cargo-audit || { log_error "cargo-audit 未安装"; return; }
    log_info "Rust 审计"
    (cd "${SCAN_PATH}" && cargo audit --json 2>/dev/null) | python3 -c "
import sys,json
d=json.loads(sys.stdin.read())
for v in d.get('vulnerabilities',{}).get('list',[]):
    n=v.get('package',{}).get('name','?'); s='medium'
    if 'Critical' in str(v): s='critical'
    elif 'High' in str(v): s='high'
    print(f'{n}|{s}|')
" 2>/dev/null | while IFS='|' read -r p s _; do [[ -n "${p}" ]] && record "${p}" "${s}"; done
}

main() {
    log_info "路径: ${SCAN_PATH} | 级别: ${SEVERITY} | 修复: ${AUTO_FIX}"
    local types=""
    [[ -f "${SCAN_PATH}/package.json" || -f "${SCAN_PATH}/package-lock.json" ]] && types+=" nodejs"
    [[ -f "${SCAN_PATH}/requirements.txt" || -f "${SCAN_PATH}/pyproject.toml" ]] && types+=" python"
    [[ -f "${SCAN_PATH}/go.mod" ]] && types+=" go"
    [[ -f "${SCAN_PATH}/Cargo.toml" ]] && types+=" rust"
    [[ -z "${types}" ]] && { log_warn "未检测到项目类型"; echo '{"summary":{"total":0,"exit_code":0}}' > "${REPORT_FILE}"; exit 0; }
    log_info "类型:${types}"
    for t in ${types}; do case "${t}" in nodejs) audit_nodejs;; python) audit_python;; go) audit_go;; rust) audit_rust;; esac; done
    local total=$((TOTAL_CRITICAL+TOTAL_HIGH+TOTAL_MEDIUM+TOTAL_LOW))
    local ec=0; [[ ${MAX_SEVERITY} -ge 3 ]] && ec=2; [[ ${MAX_SEVERITY} -ge 1 && ${ec} -eq 0 ]] && ec=1
    echo "{\"project\":\"$(basename "${PROJECT_ROOT}")\",\"summary\":{\"critical\":${TOTAL_CRITICAL},\"high\":${TOTAL_HIGH},\"medium\":${TOTAL_MEDIUM},\"low\":${TOTAL_LOW},\"total\":${total},\"exit_code\":${ec}},\"vulnerabilities\":[]}" > "${REPORT_FILE}"
    echo ""; echo "=== Dependency Audit ==="
    echo "CRITICAL: ${TOTAL_CRITICAL} | HIGH: ${TOTAL_HIGH} | MEDIUM: ${TOTAL_MEDIUM} | LOW: ${TOTAL_LOW}"
    echo "Exit: ${ec} | Report: ${REPORT_FILE}"
    exit ${ec}
}
main
