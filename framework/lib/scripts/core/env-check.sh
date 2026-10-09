#!/usr/bin/env bash
# =====================================================================
# env-check.sh — 运行时环境检测，返回 JSON 格式数据供其他脚本消费
#
# 功能：
#   1. 检测当前 OS（Windows/macOS/Linux）和版本
#   2. 检测 git/node/python 版本
#   3. 检测已安装的 linter/formatter（ruff, eslint, prettier, gofmt, cargo fmt）
#   4. 检测已安装的审计工具（pip-audit, npm audit, govulncheck, cargo audit）
#   5. 输出 JSON 格式：{"os": {...}, "tools": {...}, "auditors": {...}, "status": "ok|partial|missing"}
#   6. 关键工具缺失时给出安装命令建议
#
# 用法：
#   bash env-check.sh              # 输出 JSON 到 stdout
#   bash env-check.sh --pretty     # 格式化 JSON 输出
#   bash env-check.sh --summary    # 人类可读摘要 + JSON
#   bash env-check.sh --quiet      # 仅输出状态码，不输出 JSON
#
# 退出码：
#   0 = 所有关键工具就绪（status: ok）
#   1 = 部分工具缺失（status: partial）
#   2 = 关键工具缺失（status: missing）
# =====================================================================

set -euo pipefail

# ── 参数解析 ──────────────────────────────────────────────────────
MODE="json"
case "${1:-}" in
    --pretty)  MODE="pretty" ;;
    --summary) MODE="summary" ;;
    --quiet)   MODE="quiet" ;;
    ""|--)    MODE="json" ;;
    *)
        echo "用法: bash env-check.sh [--pretty|--summary|--quiet]" >&2
        exit 1
        ;;
esac

# ── 辅助函数 ──────────────────────────────────────────────────────

# 获取命令版本（通用）
get_version() {
    local cmd="$1"
    local version_flag="${2:---version}"
    local version=""

    if command -v "$cmd" >/dev/null 2>&1; then
        version="$($cmd $version_flag 2>/dev/null | head -1 | tr -d '\r')"
        # 清理常见格式
        version="$(echo "$version" | sed -E 's/.*v([0-9]+\.[0-9]+\.[0-9]+).*/\1/' )"
        # 如果清理失败，保留原始输出尾部
        [[ -z "$version" ]] && version="$($cmd $version_flag 2>/dev/null | head -1 | tr -d '\r')"
        echo "$version"
    else
        echo ""
    fi
}

# 检测 shell-safe 字符串（避免 JSON 注入）
json_escape() {
    local s="${1:-}"
    s="${s//\\/\\\\}"
    s="${s//\"/\\\"}"
    s="${s//$'\n'/\\n}"
    s="${s//$'\r'/}"
    s="${s//$'\t'/\\t}"
    printf '%s' "$s"
}

# ── OS 检测 ─────────────────────────────────────────────────────
detect_os() {
    local os_name="" os_version="" os_arch="" os_family=""

    case "$(uname -s)" in
        Linux*)
            os_name="Linux"
            os_family="linux"
            if [[ -f /etc/os-release ]]; then
                # shellcheck source=/dev/null
                source /etc/os-release
                os_version="${PRETTY_NAME:-${VERSION_ID:-}}"
            else
                os_version="$(uname -r)"
            fi
            ;;
        Darwin*)
            os_name="macOS"
            os_family="macos"
            os_version="$(sw_vers -productVersion 2>/dev/null || echo "")"
            ;;
        CYGWIN*|MINGW*|MSYS*|Windows_NT)
            os_name="Windows"
            os_family="windows"
            if command -v powershell >/dev/null 2>&1; then
                os_version="$(powershell -Command "[System.Environment]::OSVersion.Version.ToString()" 2>/dev/null | tr -d '\r')"
            fi
            [[ -z "$os_version" ]] && os_version="$(cmd //c ver 2>/dev/null | tr -d '\r')"
            ;;
        MINGW*|MSYS*)
            os_name="Windows (Git Bash)"
            os_family="windows"
            os_version="$(uname -r)"
            ;;
        FreeBSD*)
            os_name="FreeBSD"
            os_family="freebsd"
            os_version="$(uname -r)"
            ;;
        *)
            os_name="$(uname -s)"
            os_family="unknown"
            os_version="$(uname -r)"
            ;;
    esac

    os_arch="$(uname -m)"

    printf '{"name":"%s","version":"%s","arch":"%s","family":"%s"}' \
        "$(json_escape "$os_name")" \
        "$(json_escape "$os_version")" \
        "$(json_escape "$os_arch")" \
        "$(json_escape "$os_family")"
}

# ── 工具检测 ─────────────────────────────────────────────────────
detect_tools() {
    local tools_json="{"
    local first=true

    # ── Git ──
    local git_ver=""
    if command -v git >/dev/null 2>&1; then
        git_ver="$(git --version 2>/dev/null | awk '{print $3}')"
    fi
    first=true

    # ── Node.js ──
    local node_ver="" npm_ver=""
    if command -v node >/dev/null 2>&1; then
        node_ver="$(node --version 2>/dev/null | tr -d 'v\r')"
    fi
    if command -v npm >/dev/null 2>&1; then
        npm_ver="$(npm --version 2>/dev/null | tr -d '\r')"
    fi

    # ── Python ──
    local python_ver="" python3_ver="" pip_ver=""
    if command -v python3 >/dev/null 2>&1; then
        python3_ver="$(python3 --version 2>/dev/null | awk '{print $2}')"
    fi
    if command -v python >/dev/null 2>&1; then
        python_ver="$(python --version 2>/dev/null | awk '{print $2}')"
    fi
    if command -v pip3 >/dev/null 2>&1; then
        pip_ver="$(pip3 --version 2>/dev/null | awk '{print $2}')"
    elif command -v pip >/dev/null 2>&1; then
        pip_ver="$(pip --version 2>/dev/null | awk '{print $2}')"
    fi

    # ── Go ──
    local go_ver=""
    if command -v go >/dev/null 2>&1; then
        go_ver="$(go version 2>/dev/null | awk '{print $3}' | tr -d 'go\r')"
    fi

    # ── Rust ──
    local rust_ver="" cargo_ver=""
    if command -v rustc >/dev/null 2>&1; then
        rust_ver="$(rustc --version 2>/dev/null | awk '{print $2}')"
    fi
    if command -v cargo >/dev/null 2>&1; then
        cargo_ver="$(cargo --version 2>/dev/null | awk '{print $2}')"
    fi

    # ── Java ──
    local java_ver=""
    if command -v java >/dev/null 2>&1; then
        java_ver="$(java -version 2>&1 | head -1 | sed -E 's/.*"(.*)".*/\1/')"
    fi

    # ── Linter/Formatter ──
    # Ruff (Python)
    local ruff_ver=""
    if command -v ruff >/dev/null 2>&1; then
        ruff_ver="$(ruff --version 2>/dev/null | awk '{print $2}')"
    fi

    # ESLint (Node)
    local eslint_ver=""
    if command -v eslint >/dev/null 2>&1; then
        eslint_ver="$(eslint --version 2>/dev/null | tr -d 'v\r')"
    elif command -v npx >/dev/null 2>&1 && npx eslint --version >/dev/null 2>&1; then
        eslint_ver="$(npx eslint --version 2>/dev/null | tr -d 'v\r')"
        eslint_ver="(npx) ${eslint_ver}"
    fi

    # Prettier
    local prettier_ver=""
    if command -v prettier >/dev/null 2>&1; then
        prettier_ver="$(prettier --version 2>/dev/null | tr -d 'v\r')"
    fi

    # Go fmt
    local gofmt_ver=""
    if command -v gofmt >/dev/null 2>&1; then
        gofmt_ver="$(gofmt --help 2>&1 | head -1 || echo 'installed')"
    fi

    # Cargo fmt
    local cargo_fmt_ver=""
    if command -v cargo-fmt >/dev/null 2>&1; then
        cargo_fmt_ver="$(cargo fmt -- --version 2>/dev/null | tr -d '\r')"
    elif command -v cargo >/dev/null 2>&1; then
        cargo_fmt_ver="via cargo"
    fi

    # Black (Python)
    local black_ver=""
    if command -v black >/dev/null 2>&1; then
        black_ver="$(black --version 2>/dev/null | awk '{print $3}')"
    fi

    # isort (Python)
    local isort_ver=""
    if command -v isort >/dev/null 2>&1; then
        isort_ver="$(isort --version 2>/dev/null | head -1 | awk '{print $NF}')"
    fi

    # golangci-lint
    local golangci_ver=""
    if command -v golangci-lint >/dev/null 2>&1; then
        golangci_ver="$(golangci-lint --version 2>/dev/null | awk '{print $4}' | tr -d 'v\r')"
    fi

    # ── 构建 tools JSON ──
    TAGS='git node npm python3 pip go rustc cargo java ruff eslint prettier gofmt cargo_fmt black isort golangci-lint'

    build_tool_entry() {
        local name="$1" ver="$2" installed="false"
        [[ -n "$ver" ]] && installed="true"
        if [[ "$first" == true ]]; then
            first=false
        else
            tools_json+=","
        fi
        tools_json+="\"$(json_escape "$name")\":{\"installed\":$installed,\"version\":\"$(json_escape "$ver")\"}"
    }

    build_tool_entry "git" "$git_ver"
    build_tool_entry "node" "$node_ver"
    build_tool_entry "npm" "$npm_ver"
    build_tool_entry "python3" "$python3_ver"
    build_tool_entry "pip" "$pip_ver"
    build_tool_entry "go" "$go_ver"
    build_tool_entry "rustc" "$rust_ver"
    build_tool_entry "cargo" "$cargo_ver"
    build_tool_entry "java" "$java_ver"
    build_tool_entry "ruff" "$ruff_ver"
    build_tool_entry "eslint" "$eslint_ver"
    build_tool_entry "prettier" "$prettier_ver"
    build_tool_entry "gofmt" "$gofmt_ver"
    build_tool_entry "cargo_fmt" "$cargo_fmt_ver"
    build_tool_entry "black" "$black_ver"
    build_tool_entry "isort" "$isort_ver"
    build_tool_entry "golangci-lint" "$golangci_ver"

    tools_json+="}"
    echo "$tools_json"
}

# ── 审计工具检测 ──────────────────────────────────────────────────
detect_auditors() {
    local auditors_json="{"
    local first=true

    build_auditor_entry() {
        local name="$1" ver="$2" installed="false" cmd_suggest="${3:-}"
        [[ -n "$ver" ]] && installed="true"
        if [[ "$first" == true ]]; then
            first=false
        else
            auditors_json+=","
        fi
        auditors_json+="\"$(json_escape "$name")\":{\"installed\":$installed,\"version\":\"$(json_escape "$ver")\",\"install_cmd\":\"$(json_escape "$cmd_suggest")\"}"
    }

    # pip-audit
    local pip_audit_ver=""
    if command -v pip-audit >/dev/null 2>&1; then
        pip_audit_ver="$(pip-audit --version 2>/dev/null | awk '{print $3}')"
    fi
    build_auditor_entry "pip-audit" "$pip_audit_ver" "pip install pip-audit"

    # npm audit (built-in with npm)
    local npm_audit_ver=""
    if command -v npm >/dev/null 2>&1; then
        npm_audit_ver="$(npm --version 2>/dev/null | tr -d '\r')"
        npm_audit_ver="via npm@${npm_audit_ver}"
    fi
    build_auditor_entry "npm-audit" "$npm_audit_ver" "built-in with npm"

    # yarn audit
    local yarn_ver=""
    if command -v yarn >/dev/null 2>&1; then
        yarn_ver="$(yarn --version 2>/dev/null | tr -d '\r')"
        yarn_ver="via yarn@${yarn_ver}"
    fi
    build_auditor_entry "yarn-audit" "$yarn_ver" "npm install -g yarn"

    # govulncheck
    local govulncheck_ver=""
    if command -v govulncheck >/dev/null 2>&1; then
        govulncheck_ver="$(govulncheck -version 2>/dev/null || echo 'installed')"
    fi
    build_auditor_entry "govulncheck" "$govulncheck_ver" "go install golang.org/x/vuln/cmd/govulncheck@latest"

    # cargo audit
    local cargo_audit_ver=""
    if command -v cargo-audit >/dev/null 2>&1; then
        cargo_audit_ver="$(cargo audit --version 2>/dev/null | awk '{print $2}')"
    fi
    build_auditor_entry "cargo-audit" "$cargo_audit_ver" "cargo install cargo-audit"

    # OS-level: snyk
    local snyk_ver=""
    if command -v snyk >/dev/null 2>&1; then
        snyk_ver="$(snyk --version 2>/dev/null | tr -d '\r')"
    fi
    build_auditor_entry "snyk" "$snyk_ver" "npm install -g snyk"

    # OS-level: trivy (container scanner)
    local trivy_ver=""
    if command -v trivy >/dev/null 2>&1; then
        trivy_ver="$(trivy --version 2>/dev/null | awk '{print $2}')"
    fi
    build_auditor_entry "trivy" "$trivy_ver" "aquasecurity.github.io/trivy"

    auditors_json+="}"
    echo "$auditors_json"
}

# ── 缺失工具建议 ──────────────────────────────────────────────────
generate_suggestions() {
    local tools_json="$1"
    local suggestions="["

    # 关键工具缺失建议（使用精确 JSON key 模式避免跨条目误匹配）
    local missing_critical=()
    echo "$tools_json" | grep -q '"git":{"installed":false' 2>/dev/null && missing_critical+=("git: https://git-scm.com/downloads")
    echo "$tools_json" | grep -q '"node":{"installed":false' 2>/dev/null && missing_critical+=("node: https://nodejs.org/ 或 nvm install --lts")
    echo "$tools_json" | grep -q '"python3":{"installed":false' 2>/dev/null && missing_critical+=("python3: https://www.python.org/downloads/")

    if [[ ${#missing_critical[@]} -gt 0 ]]; then
        local first_s=true
        for s in "${missing_critical[@]}"; do
            if [[ "$first_s" == true ]]; then
                first_s=false
            else
                suggestions+=","
            fi
            suggestions+="\"$(json_escape "$s")\""
        done
    fi

    suggestions+="]"
    echo "$suggestions"
}

# ── 状态判定 ──────────────────────────────────────────────────────
determine_status() {
    local tools_json="$1"
    local auditors_json="$2"

    # 关键工具：git、至少一种编程语言运行时
    local has_git=false has_any_lang=false has_any_formatter=false has_any_auditor=false

    echo "$tools_json" | grep -q '"git":{.*"installed":true' 2>/dev/null && has_git=true
    echo "$tools_json" | grep -qE '"(node|python3|go|cargo|java)":\{.*"installed":true' 2>/dev/null && has_any_lang=true
    echo "$tools_json" | grep -qE '"(ruff|eslint|prettier|gofmt|golangci-lint)":\{.*"installed":true' 2>/dev/null && has_any_formatter=true
    echo "$auditors_json" | grep -q '"installed":true' 2>/dev/null && has_any_auditor=true

    if [[ "$has_git" == true ]] && [[ "$has_any_lang" == true ]] && [[ "$has_any_formatter" == true ]] && [[ "$has_any_auditor" == true ]]; then
        echo "ok"
    elif [[ "$has_git" == true ]] && [[ "$has_any_lang" == true ]]; then
        echo "partial"
    else
        echo "missing"
    fi
}

# ── 主流程 ────────────────────────────────────────────────────────
main() {
    # 收集数据
    local os_json tools_json auditors_json status suggestions

    os_json="$(detect_os)"
    tools_json="$(detect_tools)"
    auditors_json="$(detect_auditors)"
    status="$(determine_status "$tools_json" "$auditors_json")"
    suggestions="$(generate_suggestions "$tools_json")"

    # 构建完整 JSON 输出
    local timestamp
    timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date -u +"%Y-%m-%dT%H:%M:%SZ")"

    local output
    output=$(cat <<ENDJSON
{
  "timestamp": "$timestamp",
  "os": $os_json,
  "tools": $tools_json,
  "auditors": $auditors_json,
  "status": "$status",
  "suggestions": $suggestions
}
ENDJSON
)

    # 根据模式输出
    case "$MODE" in
        json)
            echo "$output"
            ;;
        pretty)
            if command -v python3 >/dev/null 2>&1; then
                echo "$output" | python3 -m.tool json.tool 2>/dev/null || echo "$output"
            elif command -v jq >/dev/null 2>&1; then
                echo "$output" | jq .
            else
                echo "$output"
            fi
            ;;
        summary)
            echo "$output"
            echo ""
            echo "─── Environment Summary ───"
            local os_name=$(echo "$os_json" | sed -n 's/.*"name":"\([^"]*\)".*/\1/p')
            local os_ver=$(echo "$os_json" | sed -n 's/.*"version":"\([^"]*\)".*/\1/p')
            echo "  OS: ${os_name:-unknown} ${os_ver:-}"
            echo "  Status: $status"
            echo ""
            echo "  Installed tools:"
            echo "$tools_json" | tr ',' '\n' | grep '"installed":true' | sed 's/^[[:space:]]*//' | sed 's/":{.*$//' | sed 's/"//' | sed 's/^/    - /'
            echo ""
            echo "  Installed auditors:"
            echo "$auditors_json" | tr ',' '\n' | grep '"installed":true' | sed 's/^[[:space:]]*//' | sed 's/":{.*$//' | sed 's/"//' | sed 's/^/    - /'
            echo "─── End Summary ───"
            ;;
        quiet)
            : # no output
            ;;
    esac

    # 退出码
    case "$status" in
        ok)       exit 0 ;;
        partial)  exit 1 ;;
        missing)  exit 2 ;;
    esac
}

main
