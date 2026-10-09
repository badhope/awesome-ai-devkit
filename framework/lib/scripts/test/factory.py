#!/usr/bin/env python3
"""factory.py — Test data factory for unit/integration tests
Usage:
    python3 factory.py user           → Generate one user dict
    python3 factory.py user --count 5 → Generate list of 5 users
    python3 factory.py product        → Generate one product dict
    python3 factory.py order --fk user=5 → Generate order with FK
    python3 factory.py list           → List available models
    python3 factory.py schema user    → Show schema for model
"""
import json, sys, random, uuid
from datetime import datetime, timezone

MODELS = {
    "user": {
        "fields": {
            "id", "name", "email", "is_active", "created_at",
        },
        "defaults": {
            "is_active": True,
        },
        "generators": {
            "id": lambda: str(uuid.uuid4()),
            "name": lambda: f"Test User {random.randint(1000,9999)}",
            "email": lambda: f"test{uuid.uuid4().hex[:8]}@example.com",
            "created_at": lambda: datetime.now(timezone.utc).isoformat(),
        },
    },
    "product": {
        "fields": {
            "id", "name", "price_cents", "stock", "status",
        },
        "defaults": {
            "stock": 100,
            "status": "active",
        },
        "generators": {
            "id": lambda: str(uuid.uuid4()),
            "name": lambda: f"Product-{random.randint(1,999):03d}",
            "price_cents": lambda: random.randint(99, 99999),
        },
    },
    "order": {
        "fields": {
            "id", "user_id", "total_cents", "status", "created_at",
        },
        "defaults": {
            "status": "pending",
        },
        "generators": {
            "id": lambda: str(uuid.uuid4()),
            "total_cents": lambda: random.randint(499, 49999),
            "created_at": lambda: datetime.now(timezone.utc).isoformat(),
        },
    },
    "post": {
        "fields": {
            "id", "user_id", "title", "content", "published", "created_at",
        },
        "defaults": {
            "published": False,
        },
        "generators": {
            "id": lambda: str(uuid.uuid4()),
            "title": lambda: f"Test Post {random.randint(1,9999)}",
            "content": lambda: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 3,
            "created_at": lambda: datetime.now(timezone.utc).isoformat(),
        },
    },
}

def make_one(model_name, overrides=None):
    if model_name not in MODELS:
        return None
    spec = MODELS[model_name]
    result = {}
    for field in spec["fields"]:
        if overrides and field in overrides:
            result[field] = overrides[field]
        elif field in spec.get("defaults", {}):
            result[field] = spec["defaults"][field]
        elif field in spec.get("generators", {}):
            result[field] = spec["generators"][field]()
        else:
            result[field] = None
    return result

def make_many(model_name, count, overrides=None):
    return [make_one(model_name, overrides) for _ in range(count)]

if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] in ("list", "--list"):
        print("Available models:")
        for name, spec in sorted(MODELS.items()):
            print(f"  {name}: {', '.join(sorted(spec['fields']))}")
        sys.exit(0)
    if args[0] == "schema":
        name = args[1] if len(args) > 1 else ""
        if name not in MODELS:
            print(f"Unknown: {name}"); sys.exit(1)
        print(json.dumps(MODELS[name], indent=2, default=str))
        sys.exit(0)

    model_name = args[0]
    if model_name not in MODELS:
        print(f"Unknown model: {model_name}"); sys.exit(1)

    flags = args[1:]
    count = 1
    if "--count" in flags:
        count = int(flags[flags.index("--count") + 1])

    overrides = {}
    for f in flags:
        if f.startswith("--") and "=" in f and f not in ("--count",):
            key, val = f[2:].split("=", 1)
            overrides[key] = val

    if count == 1:
        print(json.dumps(make_one(model_name, overrides), indent=2, ensure_ascii=False))
    else:
        print(json.dumps(make_many(model_name, count, overrides), indent=2, ensure_ascii=False))
