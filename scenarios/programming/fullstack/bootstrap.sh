#!/usr/bin/env bash
# =============================================================================
# Awesome AI DevKit — 全栈场景 Bootstrap 脚本 (macOS / Linux / WSL)
# -----------------------------------------------------------------------------
# 做什么：
#   1. 检查前置工具 (git, node, python3)
#   2. 初始化 context/project.yaml
#   3. 安装 mcp-config.yaml 中启用的 MCP server
#   4. 提示下一步
# =============================================================================

set -uo pipefail

# ── 颜色 ──────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BOLD='\033[1m'
NC='\033[0m'

log_ok()   { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_err()  { echo -e "${RED}[ERR]${NC} $1"; }
log_info() { echo -e "$1"; }

# ── 路径 ───────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
MCP_CONFIG="$SCRIPT_DIR/mcp/mcp-config.yaml"
CONTEXT_DIR="$SCRIPT_DIR/context"

echo ""
echo -e "${BOLD}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║  Awesome AI DevKit — 全栈场景初始化             ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════════════════╝${NC}"
echo ""

# ── Step 1: 前置工具检查 ─────────────────────────────────────────────
echo -e "${BOLD}[1/4] 检查前置工具...${NC}"

check_tool() {
    if command -v "$1" &>/dev/null; then
        local ver
        ver=$("$1" --version 2>&1 | head -1)
        log_ok "$1: $ver"
        return 0
    else
        log_err "$1 未安装"
        return 1
    fi
}

MISSING=0
check_tool git    || { MISSING=$((MISSING+1)); echo "    → 安装: https://git-scm.com/downloads"; }
check_tool node   || { MISSING=$((MISSING+1)); echo "    → 安装: https://nodejs.org 或使用 nvm"; }
check_tool python3 || { MISSING=$((MISSING+1)); echo "    → 安装: https://python.org 或使用 pyenv"; }
check_tool npx    || log_warn "npx 缺失 (通常随 node 安装，请检查 node 版本)"

# Docker 可选
if command -v docker &>/dev/null; then
    log_ok "docker: $(docker --version 2>&1)"
else
    log_warn "docker 未安装 (可选，若需要请安装 Docker Desktop)"
fi

echo ""

if [[ $MISSING -gt 0 ]]; then
    echo -e "${YELLOW}以上为缺失的必需工具。请先安装再继续。${NC}"
    echo ""
fi

# ── Step 2: 初始化项目上下文 ────────────────────────────────────────
echo -e "${BOLD}[2/4] 初始化项目上下文...${NC}"

if [[ ! -f "$CONTEXT_DIR/project.yaml" ]]; then
    if [[ -f "$CONTEXT_DIR/project.template.yaml" ]]; then
        cp "$CONTEXT_DIR/project.template.yaml" "$CONTEXT_DIR/project.yaml"
        log_ok "已创建 context/project.yaml (从模板复制)"
        echo ""
        echo -e "  ${YELLOW}>>> 请编辑 context/project.yaml，填写：${NC}"
        echo -e "  ${YELLOW}   - name: 你的项目名${NC}"
        echo -e "  ${YELLOW}   - stack.frontend / backend / database${NC}"
        echo ""
    else
        log_warn "模板缺失: $CONTEXT_DIR/project.template.yaml"
    fi
else
    log_ok "context/project.yaml 已存在，跳过"
fi

echo ""

# ── Step 3: 安装 MCP server ──────────────────────────────────────────
echo -e "${BOLD}[3/4] 安装 MCP servers...${NC}"

if [[ ! -f "$MCP_CONFIG" ]]; then
    log_warn "MCP 配置不存在: $MCP_CONFIG，跳过安装"
else
    # 用 Python 解析 MCP 配置（跨平台可靠）
    read -r -a SERVERS_TO_INSTALL <<< "$(cd "$SCRIPT_DIR" && python3 -c "
import yaml, sys
with open(sys.argv[1]) as f:
    data = yaml.safe_load(f)
servers = data.get('servers', {})
enabled = [name for name, cfg in servers.items() if cfg.get('enabled')]
print(' '.join(enabled))
" mcp/mcp-config.yaml)"

    if [[ ${#SERVERS_TO_INSTALL[@]} -eq 0 ]]; then
        log_info "没有标记 enabled: true 的 MCP server"
    else
        log_info "将安装 ${#SERVERS_TO_INSTALL[@]} 个 MCP server..."
        for server in "${SERVERS_TO_INSTALL[@]}"; do
            log_info "  → $server (需要手动配置到 AI 工具中)"
        done
        echo ""
        echo -e "  ${YELLOW}重要：MCP server 需要在你使用的 AI 编码工具中配置：${NC}"
        echo -e "  ${YELLOW}  - Cursor: Settings → MCP → 添加 server${NC}"
        echo -e "  ${YELLOW}  - Claude Code: claude mcp add ...${NC}"
        echo -e "  ${YELLOW}  - 更多配置参考: mcp/config/awesome-servers.json${NC}"
    fi
fi

echo ""

# ── Step 4: 验证 ───────────────────────────────────────────────────────
echo -e "${BOLD}[4/4] 环境就绪检查...${NC}"

FINAL_OK=true

[[ -f "$CONTEXT_DIR/project.yaml" ]] && log_ok "project.yaml" || { log_err "project.yaml 不存在"; FINAL_OK=false; }
SKILL_COUNT=$(find "$PROJECT_ROOT/framework/skills" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')
[[ -d "$PROJECT_ROOT/framework/skills" ]] && log_ok "framework/skills ($SKILL_COUNT 个通用技能)" || { log_err "framework/skills 缺失"; FINAL_OK=false; }
[[ -d "$SCRIPT_DIR/scaffolds" ]] && log_ok "scaffolds/ (3 个工作流)" || log_warn "scaffolds/ 缺失"

echo ""

# ── 下一步 ─────────────────────────────────────────────────────────────
if $FINAL_OK; then
    echo -e "${BOLD}${GREEN}✓ 初始化完成！${NC}"
    echo ""
    echo -e "${BOLD}下一步：${NC}"
    echo -e "  1. 编辑 ${YELLOW}context/project.yaml${NC} 填写项目信息"
    echo -e "  2. 用你的 AI 编码工具(Cursor / Claude Code)打开项目目录"
    echo -e "  3. 告诉 agent: ${YELLOW}\"按 feature-development scaffold 实现 XXX 功能\"${NC}"
    echo ""
else
    echo -e "${BOLD}${RED}✗ 初始化未完全成功，请解决上述问题后重试。${NC}"
    echo ""
fi
