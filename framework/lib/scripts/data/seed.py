#!/usr/bin/env python3
"""seed.py — Generate realistic test data for database seeding
Usage:
    python3 seed.py users 100          — Generate 100 fake users as SQL
    python3 seed.py orders 50 --fk     — Generate 50 orders with FK references
    python3 seed.py json users 10      — Output as JSON array
    python3 seed.py csv products 100   — Output as CSV
Exit codes: 0=ok
"""
import json, sys, random, uuid, csv, io
from datetime import datetime, timedelta, timezone

DOMAINS = ["example.com", "test.org", "demo.io", "sample.net", "mail.com"]
FIRST = ["James","Mary","John","Patricia","Robert","Jennifer","Michael","Linda","William","Elizabeth","David","Barbara","Richard","Susan"]
LAST = ["Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis","Rodriguez","Martinez","Hernandez","Lopez","Gonzalez","Wilson"]
PROD_NAMES = ["Widget","Gadget","Doohickey","Thingamajig","Gizmo","Contraption","Apparatus","Device"]
PROD_SUFFIX = ["Pro","Plus","Max","Lite","Ultra","Mini","Air","One"]
STATUSES = ["draft", "pending", "active", "completed", "cancelled"]

def gen_name():
    return f"{random.choice(FIRST)} {random.choice(LAST)}"

def gen_email(name):
    slug = name.lower().replace(" ", ".")
    return f"{slug}@{random.choice(DOMAINS)}"

def gen_ts(days_back=365):
    dt = datetime.now(timezone.utc) - timedelta(days=random.randint(0, days_back))
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

def gen_users(n, keys=False):
    users = []
    for _ in range(n):
        name = gen_name()
        u = {
            "id": str(uuid.uuid4()) if not keys else None,
            "name": name,
            "email": gen_email(name),
            "created_at": gen_ts(),
            "is_active": random.random() > 0.1,
        }
        if keys: u["id"] = str(uuid.uuid4())
        users.append(u)
    return users

def gen_products(n):
    prods = []
    seen = set()
    for _ in range(n):
        while True:
            name = f"{random.choice(PROD_NAMES)} {random.choice(PROD_SUFFIX)} {random.randint(0, 99)}"
            if name not in seen:
                seen.add(name)
                break
        prods.append({
            "name": name,
            "price_cents": random.randint(99, 99999),
            "stock": random.randint(0, 500),
            "status": random.choice(["active", "draft", "discontinued"]),
        })
    return prods

def gen_orders(n, max_user_id=100):
    orders = []
    for _ in range(n):
        orders.append({
            "user_id": random.randint(1, max_user_id),
            "total_cents": random.randint(499, 499999),
            "status": random.choice(STATUSES),
            "created_at": gen_ts(30),
        })
    return orders

def to_sql(table, rows):
    if not rows: return "-- No data"
    cols = list(rows[0].keys())
    lines = [f"INSERT INTO {table} ({', '.join(cols)}) VALUES"]
    vals = []
    for r in rows:
        parts = []
        for c in cols:
            v = r[c]
            if v is None: parts.append("NULL")
            elif isinstance(v, bool): parts.append("TRUE" if v else "FALSE")
            elif isinstance(v, (int, float)): parts.append(str(v))
            else: parts.append(f"'{str(v).replace(chr(39), chr(39)+chr(39))}'")
        vals.append(f"  ({', '.join(parts)})")
    return ",\n".join(vals) + ";"

def to_json(rows):
    return json.dumps(rows, indent=2, ensure_ascii=False)

def to_csv(rows):
    if not rows: return ""
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=rows[0].keys())
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    entity, n = sys.argv[1], int(sys.argv[2])
    flags = sys.argv[3:]
    fmt = "sql" if "--csv" not in flags and "--json" not in flags else ("csv" if "--csv" in flags else "json")
    table = entity if "--table" not in flags else flags[flags.index("--table") + 1]

    if entity == "users": rows = gen_users(n)
    elif entity == "products": rows = gen_products(n)
    elif entity == "orders": rows = gen_orders(n)
    else: print(f"Unknown: {entity}"); sys.exit(1)

    if fmt == "sql": print(to_sql(table, rows))
    elif fmt == "json": print(to_json(rows))
    elif fmt == "csv": print(to_csv(rows), end="")
