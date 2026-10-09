#!/usr/bin/env bash
# migrate.sh — Database migration runner (Postgres)
# Usage:
#   bash migrate.sh up [N]          — Run N pending migrations (default: all)
#   bash migrate.sh down [N]        — Rollback N migrations
#   bash migrate.sh create <name>   — Create new migration file
#   bash migrate.sh status          — Show applied vs pending
#   bash migrate.sh verify          — Check connection + schema state
# Dependencies: psql (Postgres CLI)
set -euo pipefail

MIGRATION_DIR="./migrations"
DB_URL="${DATABASE_URL:-}"

if [[ -z "$DB_URL" ]]; then
    echo "ERROR: DATABASE_URL not set"
    exit 1
fi

mkdir -p "$MIGRATION_DIR"

ensure_tracking_table() {
    psql "$DB_URL" -q -c "
        CREATE TABLE IF NOT EXISTS _migrations (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL UNIQUE,
            applied_at TIMESTAMPTZ DEFAULT now(),
            checksum VARCHAR(64)
        );" 2>/dev/null || { echo "ERROR: Cannot connect to database"; exit 1; }
}

get_applied() {
    psql "$DB_URL" -t -A -c "SELECT name FROM _migrations ORDER BY id;" 2>/dev/null | grep -v '^$' | sort
}

cmd="${1:-help}"
shift || true

case "$cmd" in
    create)
        name="${1:-migration}"
        name="${name// /_}"
        ts=$(date +%Y%m%d%H%M%S)
        file="$MIGRATION_DIR/${ts}_${name}.sql"
        cat > "$file" << MIG_EOF
-- Migration: ${name}
-- Created: $(date -u +%Y-%m-%dT%H:%M:%SZ)

BEGIN;

-- ↑ UP: Apply changes here


-- ↓ DOWN: Rollback (reverse the above)
-- Keep this section as comments for safety.

COMMIT;
MIG_EOF
        echo "Created: $file"
        ;;

    up)
        ensure_tracking_table
        N="${1:-999999}"
        applied=$(get_applied)
        count=0
        for f in $(ls "$MIGRATION_DIR"/*.sql 2>/dev/null | sort); do
            [[ $count -ge $N ]] && break
            fname=$(basename "$f")
            if echo "$applied" | grep -qx "$fname"; then
                continue
            fi
            checksum=$(sha256sum "$f" | cut -d' ' -f1)
            echo "Applying: $fname"
            # Run only the UP section (before -- ↓ DOWN comment)
            sql=$(sed -n '/--.*DOWN/,$!p' "$f" | sed '/^--.*$/d')
            if [[ -n "$sql" ]]; then
                echo "$sql" | psql "$DB_URL" -q
            fi
            psql "$DB_URL" -q -c "INSERT INTO _migrations (name, checksum) VALUES ('$fname', '$checksum');"
            count=$((count + 1))
        done
        echo "Applied $count migration(s)"
        ;;

    down)
        ensure_tracking_table
        N="${1:-1}"
        for i in $(seq 1 "$N"); do
            last=$(psql "$DB_URL" -t -A -c "SELECT name FROM _migrations ORDER BY id DESC LIMIT 1;" 2>/dev/null)
            [[ -z "$last" ]] && { echo "No more migrations to rollback"; break; }
            echo "Rolling back: $last"
            # Run DOWN section only
            f="$MIGRATION_DIR/$last"
            if [[ -f "$f" ]]; then
                sql=$(sed -n '/--.*DOWN/,$p' "$f" | grep -v '^\s*--.*DOWN' | sed '/^\s*--/d')
                [[ -n "$sql" ]] && echo "$sql" | psql "$DB_URL" -q
            fi
            psql "$DB_URL" -c "DELETE FROM _migrations WHERE name='$last';" -q
        done
        ;;

    status)
        ensure_tracking_table
        applied=$(get_applied | wc -l | tr -d ' ')
        pending=$(ls "$MIGRATION_DIR"/*.sql 2>/dev/null | wc -l | tr -d ' ')
        echo "Applied: $applied | Pending files: $pending"
        echo ""
        echo "Applied:"
        get_applied | sed 's/^/  ✓ /'
        for f in $(ls "$MIGRATION_DIR"/*.sql 2>/dev/null | sort); do
            fname=$(basename "$f")
            if ! get_applied | grep -qx "$fname"; then
                echo "  ⏳ $fname"
            fi
        done
        ;;

    verify)
        if psql "$DB_URL" -c "SELECT 1;" &>/dev/null; then
            echo "Database connection: OK"
        else
            echo "ERROR: Cannot connect"
            exit 1
        fi
        ensure_tracking_table
        count=$(psql "$DB_URL" -t -A -c "SELECT COUNT(*) FROM _migrations;" 2>/dev/null | tr -d ' ')
        echo "Migrations tracked: $count"
        ;;

    *)
        echo "Usage: migrate.sh {up|down|create|status|verify} [args]"
        exit 1
        ;;
esac
