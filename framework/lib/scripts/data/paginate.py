#!/usr/bin/env python3
"""paginate.py — Offset/cursor pagination helper
Usage:
    python3 paginate.py offset --page 3 --per-page 20
    python3 paginate.py cursor --after "eyJpZCI6MjB9" --per-page 20
    python3 paginate.py meta --total 500 --page 3 --per-page 20
Exit codes: 0=ok
"""
import json, sys, base64

def offset_paginate(page, per_page):
    page = max(1, page)
    per_page = max(1, min(100, per_page))
    offset = (page - 1) * per_page
    return {"offset": offset, "limit": per_page, "page": page, "per_page": per_page}

def encode_cursor(data):
    return base64.b64encode(json.dumps(data).encode()).decode()

def decode_cursor(cursor_str):
    try:
        return json.loads(base64.b64decode(cursor_str.encode()).decode())
    except Exception:
        return None

def cursor_paginate(after, per_page, sort_field="id"):
    per_page = max(1, min(100, per_page))
    params = {"limit": per_page, "per_page": per_page}
    if after:
        cursor = decode_cursor(after)
        if cursor:
            params[f"{sort_field}_gt"] = cursor.get(sort_field)
            params["after"] = after
    return params

def page_meta(total, page, per_page):
    per_page = max(1, per_page)
    total_pages = (total + per_page - 1) // per_page
    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
        "next_page": page + 1 if page < total_pages else None,
        "prev_page": page - 1 if page > 1 else None,
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cmd = sys.argv[1]
    args = sys.argv[2:]
    def get(flag, default=None):
        try: return args[args.index(flag) + 1]
        except (ValueError, IndexError): return default

    if cmd == "offset":
        r = offset_paginate(int(get("--page", 1)), int(get("--per-page", 20)))
        print(json.dumps(r, indent=2))
    elif cmd == "cursor":
        r = cursor_paginate(get("--after"), int(get("--per-page", 20)), get("--sort", "id"))
        print(json.dumps(r, indent=2))
    elif cmd == "meta":
        r = page_meta(int(get("--total", 0)), int(get("--page", 1)), int(get("--per-page", 20)))
        print(json.dumps(r, indent=2))
    else:
        print(f"Unknown: {cmd}")
        sys.exit(1)
