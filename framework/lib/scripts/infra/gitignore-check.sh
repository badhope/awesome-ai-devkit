#!/usr/bin/env bash
# gitignore-check.sh — Verify critical files are gitignored
# Usage: bash lib/scripts/infra/gitignore-check.sh
set -euo pipefail

if [[ ! -f .gitignore ]]; then
    echo "ERROR: No .gitignore found!"
    echo "  Add one with: curl -sL https://gitignore.io/api/node,python,docker > .gitignore"
    exit 2
fi

IGNORE_CONTENT=$(cat .gitignore)
MISSING=""

check_ignore() {
    local pattern="$1"
    local name="$2"
    if echo "$IGNORE_CONTENT" | grep -qE "$pattern"; then
        echo "  ✓ $name"
    else
        echo "  ✗ $name"
        MISSING="$MISSING\n    - $name"
    fi
}

echo "Gitignore Check"
echo "============================================"

check_ignore "\.env" ".env files"
check_ignore "node_modules" "node_modules/"
check_ignore "__pycache__|\.pyc" "Python cache"
check_ignore "dist|build" "Build output"
check_ignore "\.log$" "Log files"
check_ignore "\.DS_Store" "macOS files"
check_ignore "\.vscode|\.idea" "IDE configs (optional but recommended)"
check_ignore "coverage" "Coverage reports"

echo ""
if [[ -n "$MISSING" ]]; then
    echo "Missing patterns:$MISSING"
    echo "STATUS: INCOMPLETE"
    exit 1
fi

echo "STATUS: COMPLETE — All critical patterns present"
exit 0
