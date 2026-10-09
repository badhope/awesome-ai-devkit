#!/usr/bin/env python3
"""error-format.py — Standard API error response formatter
Usage:
    python3 error-format.py --code E1002 --detail "User 123 not found"
    python3 error-format.py --code E3001 --request-id abc-123
    python3 error-format.py --list   # Show all error codes
"""
import json, sys

ERRORS = {
    "E1000": ("Unknown error", 500),
    "E1001": ("Request validation failed", 400),
    "E1002": ("Resource not found", 404),
    "E1003": ("Missing or invalid credentials", 401),
    "E1004": ("Permission denied", 403),
    "E1005": ("Resource already exists", 409),
    "E1006": ("Too many requests", 429),
    "E1007": ("External service error", 502),
    "E1008": ("Operation timed out", 504),
    "E2000": ("Database operation failed", 500),
    "E2001": ("Migration failed", 500),
    "E2002": ("Cannot connect to database", 503),
    "E3000": ("Authentication error", 401),
    "E3001": ("Token has expired", 401),
    "E3002": ("Token is malformed", 401),
    "E4000": ("Business rule violation", 422),
    "E4001": ("Insufficient balance", 422),
    "E4002": ("Usage quota exceeded", 429),
}

def format_error(code, detail=None, request_id=None, **extra):
    if code not in ERRORS:
        code = "E1000"
    msg, status = ERRORS[code]
    resp = {
        "error": {
            "code": code,
            "message": msg,
        }
    }
    if detail:
        resp["error"]["detail"] = detail
    if request_id:
        resp["error"]["request_id"] = request_id
    for k, v in extra.items():
        resp["error"][k] = v
    return resp, status

if __name__ == "__main__":
    args = sys.argv[1:]
    if "--list" in args:
        for code, (msg, status) in sorted(ERRORS.items()):
            print(f"  {code} [{status}] {msg}")
        sys.exit(0)
    def get(flag, default=None):
        try: return args[args.index(flag) + 1]
        except (ValueError, IndexError): return default
    code = get("--code", "E1000")
    resp, status = format_error(code, get("--detail"), get("--request-id"))
    print(json.dumps(resp, indent=2, ensure_ascii=False))
    sys.exit(1 if status >= 500 else 0)
