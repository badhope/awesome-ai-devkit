#!/usr/bin/env bash
# readme-check.sh — Check README.md completeness
# Usage: bash lib/scripts/infra/readme-check.sh [--file README.md]
# Exit codes: 0=complete, 1=missing sections
set -euo pipefail

README="${1:-README.md}"

if [[ ! -f "$README" ]]; then
    echo "ERROR: $README not found"
    exit 1
fi

CONTENT=$(cat "$README" 2>/dev/null)
MISSING=""
FOUND=0
TOTAL=0

check_section() {
    local pattern="$1"
    local name="$2"
    TOTAL=$((TOTAL + 1))
    if echo "$CONTENT" | grep -qiE "$pattern"; then
        echo "  ✓ $name"
        FOUND=$((FOUND + 1))
    else
        echo "  ✗ $name"
        MISSING="$MISSING\n    - $name"
    fi
}

echo "README Check: $README"
echo "============================================"

check_section "^# .+" "Title"
check_section "## (Overview|Introduction|About)" "Overview"
check_section "## (Getting Started|Quick Start|Installation)" "Getting Started"
check_section "## (Usage|API|Examples)" "Usage/Examples"
check_section "## (Contributing|Contribution)" "Contributing"
check_section "## License" "License"
check_section "\`\`\`" "Code examples"
check_section "(!\[.*?\]\(.*?\)|<img )" "Screenshots/Diagrams (optional)"
check_section "## (Changelog|Releases|Versioning)|CHANGELOG" "Changelog link"

echo ""
echo "============================================"
echo "Score: $FOUND/$TRUE sections present"

if [[ -n "$MISSING" ]]; then
    echo ""
    echo "Missing sections:$MISSING"
    echo ""
    echo "STATUS: INCOMPLETE"
    exit 1
fi

echo "STATUS: COMPLETE"
exit 0
