#Requires -Version 5.1
<#
.SYNOPSIS
    Awesome AI DevKit — Fullstack Scenario Bootstrap (Windows PowerShell)

.DESCRIPTION
    1. Check prerequisites (git, node, python3)
    2. Initialize context/project.yaml
    3. Guide for MCP server setup
    4. Verify environment

.EXAMPLE
    powershell -File scenarios/programming/fullstack/bootstrap.ps1
#>

# ── Paths ─────────────────────────────────────────────────────────
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot  = Split-Path (Split-Path (Split-Path $ScriptDir -Parent) -Parent) -Parent
$MCPConfig = Join-Path $ScriptDir "mcp\mcp-config.yaml"
$ContextDir = Join-Path $ScriptDir "context"

# ── Colors ───────────────────────────────────────────────────────
function Write-Ok   { param($msg) Write-Host "[OK]   $msg" -ForegroundColor Green }
function Write-Warn { param($msg) Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-Err  { param($msg) Write-Host "[ERR]  $msg" -ForegroundColor Red }
function Write-Info { param($msg) Write-Host "       $msg" }

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════╗" -ForegroundColor White
Write-Host "║  Awesome AI DevKit — 全栈场景初始化 (Windows)   ║" -ForegroundColor White
Write-Host "╚══════════════════════════════════════════════════╝" -ForegroundColor White
Write-Host ""

# ── Step 1: Prerequisites ──────────────────────────────────────
Write-Host "[1/4] 检查前置工具..." -ForegroundColor White

function Test-Tool {
    param([string]$Name)
    try {
        $cmd = Get-Command $Name -ErrorAction Stop
        $ver = & $Name --version 2>&1 | Select-Object -First 1
        Write-Ok "$Name : $ver"
        return $true
    } catch {
        Write-Err "$Name 未安装"
        return $false
    }
}

$Missing = 0
if (-not (Test-Tool "git"))    { $Missing++; Write-Info "安装: https://git-scm.com/downloads" }
if (-not (Test-Tool "node"))   { $Missing++; Write-Info "安装: https://nodejs.org" }
if (-not (Test-Tool "python")) { $Missing++; Write-Info "安装: https://python.org" }
if (-not (Test-Tool "npx"))    { $Missing++; Write-Info "随 Node.js 安装" }

if (Get-Command "docker" -ErrorAction SilentlyContinue) {
    Write-Ok "docker : $((docker --version 2>&1))"
} else {
    Write-Warn "docker 未安装 (可选)"
}

Write-Host ""

if ($Missing -gt 0) {
    Write-Host "以上为缺失的工具。请先安装再继续。" -ForegroundColor Yellow
    Write-Host ""
}

# ── Step 2: Initialize context ─────────────────────────────────
Write-Host "[2/4] 初始化项目上下文..." -ForegroundColor White

$ProjectYaml   = Join-Path $ContextDir "project.yaml"
$TemplateYaml  = Join-Path $ContextDir "project.template.yaml"

if (-not (Test-Path $ProjectYaml)) {
    if (Test-Path $TemplateYaml) {
        Copy-Item $TemplateYaml $ProjectYaml
        Write-Ok "已创建 context/project.yaml (从模板)"
        Write-Host ""
        Write-Host "  >>> 请编辑 context/project.yaml，填写：" -ForegroundColor Yellow
        Write-Host "  - name: 你的项目名" -ForegroundColor Yellow
        Write-Host "  - stack.frontend / backend / database" -ForegroundColor Yellow
        Write-Host ""
    } else {
        Write-Warn "模板缺失: $TemplateYaml"
    }
} else {
    Write-Ok "context/project.yaml 已存在，跳过"
}

Write-Host ""

# ── Step 3: MCP servers ────────────────────────────────────────
Write-Host "[3/4] MCP servers 配置..." -ForegroundColor White

if (Test-Path $MCPConfig) {
    # 用 Python 解析启用的 servers
    $ServersRaw = python -c @"
import yaml, sys, json
with open('$($MCPConfig -replace '\\','\\')') as f:
    data = yaml.safe_load(f)
servers = data.get('servers', {})
enabled = [name for name, cfg in servers.items() if cfg.get('enabled')]
print(' '.join(enabled))
"@ 2>$null
    
    if ($ServersRaw) {
        $Servers = $ServersRaw -split ' '
        Write-Host "  将配置 $($Servers.Count) 个 MCP server：" -ForegroundColor White
        foreach ($s in $Servers) { Write-Host "  → $s" }
        Write-Host ""
        Write-Host "  重要：需要在 AI 编码工具中配置" -ForegroundColor Yellow
    } else {
        Write-Host "  没有标记 enabled: true 的 MCP server" -ForegroundColor White
    }
} else {
    Write-Warn "MCP 配置不存在: $MCPConfig"
}

Write-Host ""

# ── Step 4: Verify ─────────────────────────────────────────────
Write-Host "[4/4] 环境就绪检查..." -ForegroundColor White

$FinalOK = $true
$SkillCount = @(Get-ChildItem (Join-Path $RepoRoot "framework\skills") -Directory -ErrorAction SilentlyContinue).Count

if (Test-Path $ProjectYaml) { Write-Ok "project.yaml" } else { Write-Err "project.yaml 不存在"; $FinalOK = $false }
if (Test-Path (Join-Path $RepoRoot "framework\skills")) { Write-Ok "skills/ ($SkillCount 个技能)" } else { Write-Err "framework/skills 缺失"; $FinalOK = $false }
if (Test-Path (Join-Path $ScriptDir "scaffolds")) { Write-Ok "scaffolds/ (3 个工作流)" } else { Write-Warn "scaffolds/ 缺失" }

Write-Host ""

# ── Done ──────────────────────────────────────────────────────
if ($FinalOK) {
    Write-Host "初始化完成！" -ForegroundColor Green
    Write-Host ""
    Write-Host "下一步：" -ForegroundColor White
    Write-Host "  1. 编辑 context/project.yaml 填写项目信息" -ForegroundColor Yellow
    Write-Host "  2. 用 Cursor / Claude Code 打开项目目录" -ForegroundColor Yellow
    Write-Host "  3. 告诉 agent: '按 feature-development scaffold 实现 XXX 功能'" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host "初始化未完全成功，请解决上述问题后重试。" -ForegroundColor Red
    Write-Host ""
}
