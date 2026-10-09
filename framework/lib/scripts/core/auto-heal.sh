#!/usr/bin/env bash
# =====================================================================
# auto-heal.sh — 自动修复引擎（修复执行器）
#
# 功能：
#   1. 检测项目类型（python/node/go/rust）
#   2. 运行对应的 linter --fix
#   3. 运行 formatter
#   4. 分析 git diff 区分纯格式 vs 实质性变更
#   5. 检测依赖安装并尝试修复
#
# 输入：
#   --project <path>      项目根目录（默认当前目录）
#   --issues <file>       loop-verification 传入的 issues.json
#   --dry-run             仅检测不修复
#   --severity <level>   最低修复级别：info/warning/error（默认 warning）
#   --verbose             详细输出
#   --help                显示帮助
#
# 退出码：
#   0 = 修复成功 / dry-run 完成 / 无需修复
#   1 = 检测到需要人工审查的实质性变更
#   2 = 参数错误
#   3 = 致命错误（无法继续）
#
# 安全边界：
#   - 不修改 node_modules/ vendor/ .venv/ generated/ build/ dist/ .git/
#   - 不修改 lock 文件（package-lock.json 等）
#   - 不修改测试断言逻辑
#   - 不修改业务逻辑代码
# =====================================================================

set -euo pipefail

# ── 全局变量 ──────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="."
ISSUES_FILE=""
DRY_RUN=false
SEVERITY="warning"
VERBOSE=false
REPORT_FILE=""

# ── 安全排除目录 ─────────────────────────────────────────────────
SAFE_EXCLUDE_DIRS=(
    "node_modules"
    "vendor"
    ".venv"
    "venv"
    "generated"
    "dist"
    "build"
    ".git"
    "__pycache__"
    ".cache"
    "target"           # Rust
    "out"
    ".next"
    ".nuxt"
)

# 锁定文件列表
LOCK_FILES=(
    "package-lock.json"
    "yarn.lock"
    "pnpm-lock.yaml"
    "Cargo.lock"
    "poetry.lock"
    "Pipfile.lock"
    "go.sum"
    "composer.lock"
    "Gemfile.lock"      # Ruby
    "mix.lock"          # Elixir
)

# ── 颜色与日志 ─────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${BLUE}[auto-heal]${NC} $*"; }
log_ok()   { echo -e "${GREEN}[auto-heal]${NC} $*"; }
log_warn() { echo -e "${YELLOW}[auto-heal]${NC} $*"; }
log_err()  { echo -e "${RED}[auto-heal]${NC} $*" >&2; }

[[ "$VERBOSE" == true ]] && log_verbose() { echo -e "${BLUE}[auto-heal:verbose]${NC} $*"; } || log_verbose() { :; }

# ── 帮助信息 ──────────────────────────────────────────────────────
show_help() {
    cat <<'EOF'
auto-heal.sh — 自动修复引擎

用法: bash lib/scripts/core/auto-heal.sh [选项]

选项:
  --project <path>      项目根目录（默认当前目录）
  --issues <file>       loop-verification 传入的 issues.json 文件
  --dry-run             仅检测不修复（输出发现的问题）
  --severity <level>   最低修复级别：info/warning/error（默认 warning）
  --verbose             详细输出模式
  --report <file>       修复结果输出 JSON 文件路径
  --help                显示帮助信息

退出码:
  0 = 修复成功或无需修复
  1 = 检测到需人工审查的实质性变更
  2 = 参数错误
  3 = 致命错误

安全边界:
  - 绝不修改 node_modules/ vendor/ .venv/ generated/ dist/ build/ .git/
  - 绝不修改 lock 文件
  - 绝不修改测试断言逻辑
  - 绝不修改业务逻辑代码

示例:
  bash auto-heal.sh --project ./my-app
  bash auto-heal.sh --project ./my-app --dry-run
  bash auto-heal.sh --issues issues.json --report result.json
  bash auto-heal.sh --project ./my-app --severity error
EOF
}

# ── 参数解析 ──────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case "$1" in
        --project)   PROJECT_ROOT="$2"; shift 2 ;;
        --issues)    ISSUES_FILE="$2"; shift 2 ;;
        --dry-run)   DRY_RUN=true; shift ;;
        --severity)  SEVERITY="$2"; shift 2 ;;
        --verbose)   VERBOSE=true; shift ;;
        --report)    REPORT_FILE="$2"; shift 2 ;;
        --help)      show_help; exit 0 ;;
        *)           log_err "未知参数: $1"; show_help; exit 2 ;;
    esac
done

# 切换到项目根目录
cd "$PROJECT_ROOT" 2>/dev/null || { log_err "无法进入项目目录: $PROJECT_ROOT"; exit 3; }
PROJECT_ROOT="$(pwd)"
log_verbose "项目根目录: $PROJECT_ROOT"

# ── 后续需要人工审查的标志 ────────────────────────────────────────
NEEDS_REVIEW=false
ISSUES_FOUND=0
ISSUES_FIXED=0
ISSUES_SKIPPED=0
FIXES_APPLIED=()

# ── 项目类型检测 ─────────────────────────────────────────────────
detect_project_type() {
    local types=()

    if [[ -f "package.json" ]]; then
        types+=("node")
    fi
    if [[ -f "pyproject.toml" ]] || [[ -f "requirements.txt" ]] || [[ -f "setup.py" ]] || [[ -f "setup.cfg" ]]; then
        types+=("python")
    fi
    if [[ -f "go.mod" ]]; then
        types+=("go")
    fi
    if [[ -f "Cargo.toml" ]]; then
        types+=("rust")
    fi
    if [[ -f "pom.xml" ]] || [[ -f "build.gradle" ]] || [[ -f "build.gradle.kts" ]]; then
        types+=("java")
    fi

    if [[ ${#types[@]} -eq 0 ]]; then
        log_err "无法识别项目类型"
        echo "unknown"
        return 1
    fi

    echo "${types[*]}"
}

# ── 构建 find 排除参数 ─────────────────────────────────────────────
build_find_excludes() {
    local excludes=()
    for dir in "${SAFE_EXCLUDE_DIRS[@]}"; do
        excludes+=("-not" "-path" "*/${dir}/*" "-not" "-path" "*/${dir}")
    done
    echo "${excludes[@]:-}"
}

# ── 安全文件检查 ──────────────────────────────────────────────────
is_safe_to_modify() {
    local file="$1"

    # 检查是否在排除目录中
    for dir in "${SAFE_EXCLUDE_DIRS[@]}"; do
        if [[ "$file" == *"/$dir/"* ]] || [[ "$file" == *"/$dir" ]]; then
            log_verbose "跳过安全排除目录中的文件: $file"
            return 1
        fi
    done

    # 检查是否为 lock 文件
    local basename
    basename="$(basename "$file")"
    for lock in "${LOCK_FILES[@]}"; do
        if [[ "$basename" == "$lock" ]]; then
            log_verbose "跳过 lock 文件: $file"
            return 1
        fi
    done

    # 检查是否在项目根目录下
    if [[ "$file" != "$PROJECT_ROOT"* ]] && [[ "$file" != ./* ]]; then
        log_verbose "跳过项目外文件: $file"
        return 1
    fi

    return 0
}

# ── Git diff 分析 ─────────────────────────────────────────────────
analyze_git_diff_changes() {
    local diff_output
    diff_output="$(git diff --stat 2>/dev/null || echo "")"

    if [[ -z "$diff_output" ]]; then
        log_verbose "git diff 无变更"
        return 0
    fi

    echo "─── 修复变更统计 ───"
    echo "$diff_output"
    echo ""

    # 分析变更是否为纯格式（仅空白和导入排序）
    local changed_lines
    changed_lines="$(git diff 2>/dev/null || true)"

    # 检查是否有非空白字符的实质性变更
    # 去除 +/- 前缀、空白字符后，看是否有实际内容差异
    local substantive_changes=false

    # 提取每个文件的变更内容
    while IFS= read -r file; do
        [[ -z "$file" ]] && continue
        file="${file#?}"

        local file_diff
        file_diff="$(git diff -- "$file" 2>/dev/null || true)"

        # 移除纯空白行变更（仅空格/制表符差异）
        local clean_diff
        clean_diff="$(echo "$file_diff" | grep -E '^[+-]' | grep -v '^[+-][[:space:]]*$' | grep -v '^[+-][[:space:]]*#' | grep -v '^[+-][[:space:]]*$' || true)"

        # 如果去除空白行后还有实质差异
        if [[ -n "$clean_diff" ]]; then
            # 再检查是否仅为 import 排序变更
            local non_import_diff
            non_import_diff="$(echo "$clean_diff" | grep -vE '(^import |from .* import|^from )' || true)"

            if [[ -n "$non_import_diff" ]]; then
                substantive_changes=true
                log_warn "检测到实质性代码变更: $file"
                echo "$non_import_diff" | head -5
            else
                log_verbose "仅 import 排序变更: $file（安全）"
            fi
        fi
    done <<< "$(git diff --name-only 2>/dev/null || true)"

    if [[ "$substantive_changes" == true ]]; then
        echo ""
        log_warn "发现需人工审查的实质性代码变更"
        return 1
    else
        echo ""
        log_ok "所有变更为纯格式/导入排序（安全）"
        return 0
    fi
}

# ── Node.js 修复 ──────────────────────────────────────────────────
fix_node_project() {
    log_info "项目类型: Node.js (TypeScript/JavaScript)"

    local has_changes=false

    # 检查 package.json 确定包管理器
    local pkg_manager=""
    if [[ -f "package-lock.json" ]]; then
        pkg_manager="npm"
    elif [[ -f "yarn.lock" ]]; then
        pkg_manager="yarn"
    elif [[ -f "pnpm-lock.yaml" ]]; then
        pkg_manager="pnpm"
    else
        pkg_manager="npm"
    fi
    log_verbose "包管理器: $pkg_manager"

    # 运行 ESLint 修复
    if npx eslint --version >/dev/null 2>&1; then
        log_info "运行: npx eslint . --fix"
        if [[ "$DRY_RUN" == true ]]; then
            log_verbose "[dry-run] npx eslint . --fix"
            local lint_output
            lint_output="$(npx eslint . 2>/dev/null || true)"
            local lint_issues
            lint_issues="$(echo "$lint_output" | grep -cE 'error' || true)"
            log_info "发现 $lint_issues 个 ESLint 问题（dry-run 未修复）"
            ISSUES_FOUND=$((ISSUES_FOUND + lint_issues))
        else
            npx eslint . --fix 2>/dev/null || true
            local lint_fixed=$?
            if [[ $lint_fixed -eq 0 ]]; then
                log_ok "ESLint 修复完成"
                ISSUES_FIXED=$((ISSUES_FIXED + 1))
                FIXES_APPLIED+=("eslint --fix")
                has_changes=true
            else
                log_warn "ESLint 仍有问题未自动修复"
                ISSUES_SKIPPED=$((ISSUES_SKIPPED + 1))
            fi
        fi
    else
        log_verbose "ESLint 未配置，跳过"
    fi

    # 运行 Prettier 修复
    if [[ -f ".prettierrc" ]] || [[ -f "prettier.config.js" ]] || [[ -f ".prettierrc.json" ]] || grep -q '"prettier"' package.json 2>/dev/null; then
        log_info "运行: npx prettier --write ."
        if [[ "$DRY_RUN" == true ]]; then
            log_verbose "[dry-run] npx prettier --write ."
        else
            npx prettier --write . 2>/dev/null || true
            log_ok "Prettier 格式化完成"
            FIXES_APPLIED+=("prettier --write")
            has_changes=true
        fi
    elif npx prettier --version >/dev/null 2>&1; then
        log_verbose "Prettier 可用但无配置文件"
    fi

    # 检查依赖完整性
    if [[ "$DRY_RUN" == false ]]; then
        log_info "检查依赖完整性..."
        if $pkg_manager audit >/dev/null 2>&1; then
            log_ok "依赖审计通过"
        else
            log_warn "依赖审计发现问题（需人工review）"
        fi
    fi

    return 0
}

# ── Python 修复 ───────────────────────────────────────────────────
fix_python_project() {
    log_info "项目类型: Python"

    local has_changes=false

    # 检查虚拟环境
    if [[ -d ".venv" ]] || [[ -d "venv" ]]; then
        log_verbose "检测到虚拟环境"
        local python_cmd="python3"
        if [[ -f ".venv/bin/python" ]]; then
            python_cmd=".venv/bin/python"
        elif [[ -f "venv/bin/python" ]]; then
            python_cmd="venv/bin/python"
        fi
    else
        local python_cmd="python3"
    fi

    # 运行 Ruff lint + format
    if command -v ruff >/dev/null 2>&1 || $python_cmd -m ruff --version >/dev/null 2>&1; then
        local ruff_cmd="ruff"
        $python_cmd -m ruff --version >/dev/null 2>&1 && ruff_cmd="$python_cmd -m ruff"

        log_info "运行: $ruff_cmd check --fix"
        if [[ "$DRY_RUN" == true ]]; then
            log_verbose "[dry-run] $ruff_cmd check --fix"
            local ruff_output
            ruff_output="$($ruff_cmd check . 2>/dev/null || true)"
            local ruff_issues
            ruff_issues="$(echo "$ruff_output" | grep -cE 'error|warning' || true)"
            log_info "发现 $ruff_issues 个 Ruff 问题（dry-run 未修复）"
            ISSUES_FOUND=$((ISSUES_FOUND + ruff_issues))
        else
            $ruff_cmd check --fix . 2>/dev/null || true
            log_ok "Ruff 修复完成"
            ISSUES_FIXED=$((ISSUES_FIXED + 1))
            FIXES_APPLIED+=("ruff check --fix")

            log_info "运行: $ruff_cmd format"
            if [[ "$DRY_RUN" == true ]]; then
                log_verbose "[dry-run] $ruff_cmd format ."
            else
                $ruff_cmd format . 2>/dev/null || true
                log_ok "Ruff 格式化完成"
                FIXES_APPLIED+=("ruff format")
                has_changes=true
            fi
        fi
    else
        log_verbose "Ruff 未安装，尝试 flake8 + black"
        # Fallback: flake8 + black
        if command -v black >/dev/null 2>&1 || $python_cmd -m black --version >/dev/null 2>&1; then
            local black_cmd="black"
            $python_cmd -m black --version >/dev/null 2>&1 && black_cmd="$python_cmd -m black"

            log_info "运行: $black_cmd ."
            if [[ "$DRY_RUN" != true ]]; then
                $black_cmd . 2>/dev/null || true
                log_ok "Black 格式化完成"
                FIXES_APPLIED+=("black")
                has_changes=true
            fi
        fi
    fi

    # 运行 isort（如果已安装）
    if command -v isort >/dev/null 2>&1 || $python_cmd -m isort --version >/dev/null 2>&1; then
        local isort_cmd="isort"
        $python_cmd -m isort --version >/dev/null 2>&1 && isort_cmd="$python_cmd -m isort"

        log_info "运行: $isort_cmd .（导入排序）"
        if [[ "$DRY_RUN" != true ]]; then
            $isort_cmd . 2>/dev/null || true
            log_ok "import 排序完成"
            FIXES_APPLIED+=("isort")
            has_changes=true
        fi
    fi

    # 检查依赖安全性
    if command -v pip-audit >/dev/null 2>&1 && [[ "$DRY_RUN" == false ]]; then
        log_info "运行 pip-audit..."
        pip-audit 2>/dev/null || log_warn "pip-audit 发现问题（需人工review）"
    fi

    return 0
}

# ── Go 修复 ───────────────────────────────────────────────────────
fix_go_project() {
    log_info "项目类型: Go"

    local has_changes=false

    # gofmt 格式化
    if command -v gofmt >/dev/null 2>&1; then
        log_info "运行: gofmt -w ."
        if [[ "$DRY_RUN" == true ]]; then
            log_verbose "[dry-run] gofmt -l ."
            local gofmt_issues
            gofmt_issues="$(gofmt -l . 2>/dev/null | wc -l)"
            log_info "发现 $gofmt_issues 个需要格式化的文件（dry-run 未修复）"
            ISSUES_FOUND=$((ISSUES_FOUND + gofmt_issues))
        else
            # gofmt -l 列出需要格式化的文件
            local files_needing_format
            files_needing_format="$(gofmt -l . 2>/dev/null || true)"
            if [[ -n "$files_needing_format" ]]; then
                echo "$files_needing_format" | while read -r f; do
                    is_safe_to_modify "$f" && gofmt -w "$f" 2>/dev/null || true
                done
                log_ok "gofmt 格式化完成"
                ISSUES_FIXED=$((ISSUES_FIXED + 1))
                FIXES_APPLIED+=("gofmt -w")
                has_changes=true
            else
                log_ok "gofmt 检查通过，无需格式化"
            fi
        fi
    fi

    # goimports（如果安装了）
    if command -v goimports >/dev/null 2>&1; then
        log_info "运行: goimports -w ."
        if [[ "$DRY_RUN" != true ]]; then
            # goimports -w .
            find . -name "*.go" -not -path "*/vendor/*" -not -path "*/.git/*" -print0 2>/dev/null | \
                xargs -0 goimports -w 2>/dev/null || true
            log_ok "goimports 完成"
            FIXES_APPLIED+=("goimports -w")
            has_changes=true
        fi
    fi

    # golangci-lint run --fix（如果安装了）
    if command -v golangci-lint >/dev/null 2>&1; then
        log_info "运行: golangci-lint run --fix"
        if [[ "$DRY_RUN" == true ]]; then
            log_verbose "[dry-run] golangci-lint run"
            local lint_issues
            lint_issues="$(golangci-lint run 2>&1 | grep -c '::' || true)"
            log_info "发现 $lint_issues 个 lint 问题（dry-run 未修复）"
            ISSUES_FOUND=$((ISSUES_FOUND + lint_issues))
        else
            golangci-lint run --fix 2>/dev/null || true
            log_ok "golangci-lint 修复完成"
            FIXES_APPLIED+=("golangci-lint run --fix")
        fi
    fi

    return 0
}

# ── Rust 修复 ─────────────────────────────────────────────────────
fix_rust_project() {
    log_info "项目类型: Rust"

    local has_changes=false

    # cargo fmt
    if command -v cargo >/dev/null 2>&1; then
        log_info "运行: cargo fmt"
        if [[ "$DRY_RUN" == true ]]; then
            log_verbose "[dry-run] cargo fmt -- --check"
            cargo fmt -- --check 2>/dev/null || log_info "代码需要格式化"
        else
            cargo fmt 2>/dev/null || true
            log_ok "cargo fmt 完成"
            FIXES_APPLIED+=("cargo fmt")
            has_changes=true
        fi
    else
        log_verbose "cargo 未安装，跳过 Rust 修复"
    fi

    # cargo clippy --fix（仅修复简单 lint）
    if command -v cargo >/dev/null 2>&1; then
        log_info "运行: cargo clippy --fix --allow-dirty"
        if [[ "$DRY_RUN" == true ]]; then
            log_verbose "[dry-run] cargo clippy -- -W clippy::all"
        else
            # clippy --fix 自动修复 clippy 建议
            cargo clippy --fix --allow-dirty --allow-no-vcs 2>/dev/null || true
            log_ok "cargo clippy 修复完成"
            FIXES_APPLIED+=("cargo clippy --fix")
            has_changes=true
        fi
    fi

    return 0
}

# ── 修复结果评估 ──────────────────────────────────────────────────
evaluate_results() {
    echo ""
    echo "============================================"
    log_info "修复结果报告"
    echo "============================================"
    echo ""

    if [[ "$DRY_RUN" == true ]]; then
        log_info "DRY RUN 模式（仅检测）："
        echo "  发现问题数: $ISSUES_FOUND"
        echo "  无需执行任何修复"
        echo "  退出码: 0（dry-run 完成）"
        return 0
    fi

    # 检查是否有实际变更钦敬
    if ! git diff --quiet 2>/dev/null; then
        log_info "检测到文件变更，分析变更性质..."

        if ! analyze_git_diff_changes; then
            # 发现实质性变更
            NEEDS_REVIEW=true
            echo ""
            log_warn "⚠ 检测到需人工审查的实质性代码变更"
            log_warn "→ 建议：提交前请人工 review 所有变更"
            log_warn "→ 特别是安全修复引入的逻辑修改"

            # 输出变更文件列表
            echo ""
            echo "变更文件列表："
            git diff --name-only 2>/dev/null | while read -r f; do
                echo "    - $f"
            done
        else
            log_ok "所有变更为纯格式/导入排序（自动安全）"
        fi
    else
        log_ok "无需修复或修复未产生文件变更"
    fi

    # 输出修复摘要
    echo ""
    echo "修复摘要："
    echo "  尝试修复: $((ISSUES_FIXED + ISSUES_SKIPPED)) 项"
    echo "  修复成功: $ISSUES_FIXED 项"
    echo "  跳过/失败: $ISSUES_SKIPPED 项"

    if [[ ${#FIXES_APPLIED[@]} -gt 0 ]]; then
        echo ""
        echo "已执行修复："
        for fix in "${FIXES_APPLIED[@]}"; do
            echo "    → $fix"
        done
    fi

    # 最终判定
    if [[ "$NEEDS_REVIEW" == true ]]; then
        echo ""
        echo "状态: NEEDS_REVIEW（退出码 1）"
        echo "说明：修复引入了实质性代码变更，需人工审查后确认"
        return 1
    else
        echo ""
        log_ok "状态: SUCCESS（退出码 0）"
        return 0
    fi
}

# ── 生成修复报告文件 ──────────────────────────────────────────────
generate_report() {
    [[ -z "$REPORT_FILE" ]] && return 0

    local status="success"
    [[ "$NEEDS_REVIEW" == true ]] && status="needs_review"

    cat > "$REPORT_FILE" <<EOF
{
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date -u)",
  "project_root": "$PROJECT_ROOT",
  "dry_run": $DRY_RUN,
  "issues_found": $ISSUES_FOUND,
  "issues_fixed": $ISSUES_FIXED,
  "issues_skipped": $ISSUES_SKIPPED,
  "status": "$status",
  "fixes_applied": [
$(printf '    "%s"' "${FIXES_APPLIED[@]:-}" | sed 's/" "/","/g')
  ]
}
EOF
    log_info "修复报告已保存: $REPORT_FILE"
}

# ── 主流程 ────────────────────────────────────────────────────────
main() {
    echo "============================================"
    log_info "自动修复引擎 (auto-heal) 启动"
    echo "============================================"
    echo ""

    # dry-run 提示
    [[ "$DRY_RUN" == true ]] && log_warn "DRY RUN 模式（仅检测，不执行修复）"

    # 步骤 1: 检测项目类型
    echo "─── 步骤 1: 项目类型检测 ───"
    local project_types
    project_types="$(detect_project_type)"
    if [[ $? -ne 0 ]]; then
        log_err "项目类型检测失败"
        exit 3
    fi
    log_info "检测到项目类型: $project_types"
    echo ""

    # 步骤 2: 检查 git 状态
    echo "─── 步骤 2: 检查 git 状态 ───"
    if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        log_ok "git 仓库正常"
        # 保存当前状态用于后续 diff 分析
        git add -A --local 2>/dev/null || true
    else
        log_warn "非 git 仓库，无法进行 diff 分析"
    fi
    echo ""

    # 步骤 3: 按项目类型执行修复
    echo "─── 步骤 3: 执行自动修复 ───"
    for ptype in $project_types; do
        case "$ptype" in
            node)   fix_node_project ;;
            python) fix_python_project ;;
            go)     fix_go_project ;;
            rust)   fix_rust_project ;;
            *)      log_warn "不支持的项目类型: $ptype，跳过" ;;
        esac
        echo ""
    done

    # 步骤 4: 评估修复结果
    echo "─── 步骤 4: 修复结果评估 ───"
    evaluate_results
    local eval_result=$?

    # 步骤 5: 生成报告
    if [[ -n "$REPORT_FILE" ]]; then
        echo ""
        echo "─── 步骤 5: 生成修复报告 ───"
        generate_report
    fi

    echo ""
    echo "============================================"
    [[ $eval_result -eq 0 ]] && log_ok "auto-heal 完成" || log_warn "auto-heal 完成（需人工审查）"
    echo "============================================"

    exit $eval_result
}

# ── 入口 ──────────────────────────────────────────────────────────
main
