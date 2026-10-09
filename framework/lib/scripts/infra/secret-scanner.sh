#!/usr/bin/env bash
# secret-scanner.sh — Scan code for hardcoded secrets
# Usage: bash lib/scripts/infra/secret-scanner.sh [--path .] [--severity HIGH|MEDIUM|LOW]
# Exit codes: 0=clean, 1=found secrets
set -euo pipefail

SCAN_PATH="${1:-.}"
SEVERITY="${2:-HIGH}"

# Patterns that indicate hardcoded secrets
PATTERNS=(
    # API Keys
    'AIza[0-9A-Za-z_-]{35}'                           # Google API Key
    'sk-[0-9a-zA-Z]{48}'                              # OpenAI API Key
    'ghp_[0-9a-zA-Z]{36}'                             # GitHub Personal Token
    'gho_[0-9a-zA-Z]{36}'                             # GitHub OAuth Token
    'xoxb-[0-9]{11}-[0-9]{11}-[0-9a-zA-Z]{24}'       # Slack Bot Token
    'xoxp-[0-9]{11}-[0-9]{11}-[0-9a-zA-Z]{24}'       # Slack User Token
    'SK[0-9a-zA-Z]{32}'                               # Stripe Secret Key
    'rk_[0-9a-zA-Z]{32}'                              # Stripe Restricted Key

    # Private Keys
    '-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY'

    # Passwords in code
    'password\s*[:=]\s*['"'"'"][^'"'"'"]{8,}'"'"'"']
    'passwd\s*[:=]\s*['"'"'"][^'"'"'"]{8,}'"'"'"']
    'secret\s*[:=]\s*['"'"'"][^'"'"'"]{8,}'"'"'"']

    # Connection strings with credentials
    'mysql://[^:]+:[^@]+@'
    'postgres://[^:]+:[^@]+@'
    'mongodb(\+srv)?://[^:]+:[^@]+@'

    # AWS Keys
    'AKIA[0-9A-Z]{16}'                                # AWS Access Key
    '[0-9a-zA-Z/+]{40}'                               # AWS Secret Key (heuristic)
)

# Files to ignore
IGNORE_DIRS="(\.git|node_modules|dist|build|__pycache__|\.venv|vendor)"
IGNORE_FILES="(\.lock|\.min\.|\.map)"

FOUND=0
SCANED=0

while IFS= read -r -d '' file; do
    SCANED=$((SCANED + 1))
    # Skip ignored directories and files
    if [[ "$file" =~ $IGNORE_DIRS ]] || [[ "$file" =~ $IGNORE_FILES ]]; then
        continue
    fi

    for pattern in "${PATTERNS[@]}"; do
        matches=$(grep -nE "$pattern" "$file" 2>/dev/null || true)
        if [[ -n "$matches" ]]; then
            FOUND=$((FOUND + 1))
            echo ""
            echo "FILE: $file"
            echo "$matches" | while IFS= read -r line; do
                # Redact actual value for safety
                redacted=$(echo "$line" | sed 's/[:=].*/: [REDACTED]/')
                echo "  $redacted"
            done
        fi
    done
done < <(find "$SCAN_PATH" -type f -print0 2>/dev/null)

echo ""
echo "============================================"
echo "Secret Scan Result"
echo "  Files scanned: $SCANED"
echo "  Issues found:  $FOUND"
echo "============================================"

if [[ $FOUND -gt 0 ]]; then
    echo "STATUS: FAIL — Remove hardcoded secrets!"
    echo "  Tips:"
    echo "    - Move to .env and getenv()"
    echo "    - Use secret manager (AWS SM, Vault)"
    echo "    - Revoke compromised keys immediately"
    exit 1
fi

echo "STATUS: CLEAN — No hardcoded secrets found"
exit 0
