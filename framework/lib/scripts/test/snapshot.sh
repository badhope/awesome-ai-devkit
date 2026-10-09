#!/usr/bin/env bash
# snapshot.sh — Snapshot testing helper (compare output to stored snapshot)
# Usage:
#   bash snapshot.sh record <name> '<command>'    — Record snapshot
#   bash snapshot.sh verify <name> '<command>'    — Compare command output to snapshot
#   bash snapshot.sh list                         — List all snapshots
#   bash snapshot.sh clean                        — Delete all snapshots
# Exit codes: 0=match 1=different 2=command failed
set -euo pipefail

SNAP_DIR=".snapshots"
mkdir -p "$SNAP_DIR"

cmd="${1:-help}"
shift || true

case "$cmd" in
    record)
        name="$1"
        shift
        cmd_str="$*"
        echo "Recording: $name"
        eval "$cmd_str" > "$SNAP_DIR/${name}.snap"
        echo "Saved to .snapshots/${name}.snap"
        ;;

    verify)
        name="$1"
        shift
        cmd_str="$*"
        snap="$SNAP_DIR/${name}.snap"

        if [[ ! -f "$snap" ]]; then
            echo "No snapshot: $name (run 'snapshot.sh record $name ...' first)"
            exit 1
        fi

        actual=$(eval "$cmd_str" 2>&1)
        expected=$(cat "$snap")

        if [[ "$actual" == "$expected" ]]; then
            echo "✓ $name: MATCH"
            exit 0
        else
            echo "✗ $name: DIFFER"
            diff <(echo "$expected") <(echo "$actual") || true
            exit 1
        fi
        ;;

    list)
        echo "Snapshots:"
        for f in "$SNAP_DIR"/*.snap 2>/dev/null; do
            name=$(basename "$f" .snap)
            size=$(wc -c < "$f" | tr -d ' ')
            echo "  $name (${size}B)"
        done
        ;;

    clean)
        count=$(ls "$SNAP_DIR"/*.snap 2>/dev/null | wc -l | tr -d ' ')
        rm -f "$SNAP_DIR"/*.snap
        echo "Removed $count snapshot(s)"
        ;;

    *)
        echo "Usage: snapshot.sh {record|verify|list|clean} [args]"
        exit 1
        ;;
esac
