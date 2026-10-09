#!/usr/bin/env bash
# error-code.sh — Standardized error code lookup
# Usage: bash lib/scripts/core/error-code.sh E2001
# Exit codes: 0=found, 1=not found

declare -A ERROR_CODES=(
    [E1000]="UNKNOWN | Unknown error | 500"
    [E1001]="VALIDATION | Request validation failed | 400"
    [E1002]="NOT_FOUND | Resource not found | 404"
    [E1003]="UNAUTHENTICATED | Missing or invalid credentials | 401"
    [E1004]="FORBIDDEN | Permission denied | 403"
    [E1005]="CONFLICT | Resource already exists | 409"
    [E1006]="RATE_LIMITED | Too many requests | 429"
    [E1007]="DEPENDENCY_FAILED | External service error | 502"
    [E1008]="TIMEOUT | Operation timed out | 504"
    [E2000]="DB_ERROR | Database operation failed | 500"
    [E2001]="DB_MIGRATION | Migration failed | 500"
    [E2002]="DB_CONNECTION | Cannot connect to database | 503"
    [E3000]="AUTH_ERROR | Authentication error | 401"
    [E3001]="TOKEN_EXPIRED | Token has expired | 401"
    [E3002]="TOKEN_INVALID | Token is malformed | 401"
    [E4000]="BUSINESS_RULE | Business rule violation | 422"
    [E4001]="INSUFFICIENT_BALANCE | Not enough balance | 422"
    [E4002]="QUOTA_EXCEEDED | Usage quota exceeded | 429"
)

CODE="${1^^}"
if [[ -z "${ERROR_CODES[$CODE]+x}" ]]; then
    echo "Unknown code: $CODE"
    echo "Available:" $(echo "${!ERROR_CODES[@]}" | tr ' ' '\n' | sort | tr '\n' ' ')
    exit 1
fi

IFS='|' read -r name msg status <<< "${ERROR_CODES[$CODE]}"
name=$(echo "$name" | xargs)
msg=$(echo "$msg" | xargs)
echo "Code:    $CODE"
echo "Name:    $name"
echo "Message: $msg"
echo "HTTP:    $status"
exit 0
