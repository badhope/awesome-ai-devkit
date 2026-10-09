#!/usr/bin/env bash
# rate-limit.sh — Check rate limit status (Redis-backed)
# Usage: bash rate-limit.sh <identifier> [--window 60] [--max 100]
# Example: bash rate-limit.sh "user:123" --window 60 --max 100
# Exit codes: 0=allowed 1=limited
set -euo pipefail

REDIS_URL="${REDIS_URL:-redis://localhost:6379}"
ID="${1:-}"
WINDOW="${3:-60}"
MAX="${5:-100}"

if [[ -z "$ID" ]]; then
    echo "Usage: rate-limit.sh <identifier> [--window 60] [--max 100]"
    exit 1
fi

# Use Redis INCR + EXPIE for sliding window counting
KEY="ratelimit:${ID}"
NOW=$(date +%s)

COUNT=$(redis-cli -u "$REDIS_URL" INCR "$KEY" 2>/dev/null || echo "0")
if [[ "$COUNT" -eq 1 ]]; then
    redis-cli -u "$REDIS_URL" EXPIRE "$KEY" "$WINDOW" &>/dev/null
fi

REMAINING=$((MAX - COUNT))
if [[ $REMAINING -lt 0 ]]; then
    REMAINING=0
fi

echo "limit: $MAX"
echo "window: ${WINDOW}s"
echo "current: $COUNT"
echo "remaining: $REMAINING"

if [[ $COUNT -gt $MAX ]]; then
    TTL=$(redis-cli -u "$REDIS_URL" TTL "$KEY" 2>/dev/null || echo "$WINDOW")
    echo "retry_after: ${TTL}s"
    echo "STATUS: LIMITED"
    exit 1
fi

echo "STATUS: ALLOWED"
exit 0
