#!/usr/bin/env python3
"""token-tracker.py — Track LLM token usage and calculate cost
Usage:
    python3 token-tracker.py log --provider anthropic --model claude-sonnet-4-20250514 --input 1500 --output 800
    python3 token-tracker.py report  # Show session cost summary
    python3 token-tracker.py budget --max 5.00  # Warn if exceeds $5
Exit codes: 0=ok 1=budget exceeded
"""
import json, sys, os
from datetime import datetime, timezone
from pathlib import Path

# USD per 1M tokens (2026 pricing)
PRICING = {
    "claude-sonnet-4-20250514":    {"input": 3.00, "output": 15.00},
    "claude-opus-4-20250514":      {"input": 15.00, "output": 75.00},
    "claude-haiku-4-20250514":     {"input": 0.25, "output": 1.25},
    "gpt-5.2":                     {"input": 2.50, "output": 10.00},
    "gpt-4o":                      {"input": 2.50, "output": 10.00},
    "gpt-4o-mini":                 {"input": 0.15, "output": 0.60},
    "gemini-2.5-pro":              {"input": 1.25, "output": 5.00},
    "deepseek-v3":                 {"input": 0.27, "output": 1.10},
    "_default":                    {"input": 3.00, "output": 15.00},
}

LOG_DIR = Path("./logs/token-usage")

def get_price(model):
    return PRICING.get(model, PRICING["_default"])

def log_usage(provider, model, input_t, output_t):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    price = get_price(model)
    cost_in  = (input_t / 1_000_000) * price["input"]
    cost_out = (output_t / 1_000_000) * price["output"]
    cost = cost_in + cost_out
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "provider": provider,
        "model": model,
        "tokens_in": input_t,
        "tokens_out": output_t,
        "cost_usd": round(cost, 6),
    }
    logfile = LOG_DIR / f"{datetime.now():%Y-%m}.jsonl"
    with open(logfile, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"Logged: {input_t}+{output_t} tokens, ${cost:.6f} ({provider}/{model})")
    return cost

def show_report():
    total_cost = 0
    total_in = 0
    total_out = 0
    by_model = {}
    for logfile in sorted(LOG_DIR.glob("*.jsonl")):
        for line in open(logfile):
            e = json.loads(line)
            total_cost += e["cost_usd"]
            total_in += e["tokens_in"]
            total_out += e["tokens_out"]
            m = e["model"]
            if m not in by_model:
                by_model[m] = {"cost": 0, "in": 0, "out": 0}
            by_model[m]["cost"] += e["cost_usd"]
            by_model[m]["in"] += e["tokens_in"]
            by_model[m]["out"] += e["tokens_out"]
    print(f"\nToken Usage Report")
    print(f"  Total: {total_in:,} in + {total_out:,} out = ${total_cost:.4f}")
    for m, v in sorted(by_model.items(), key=lambda x: -x[1]["cost"]):
        print(f"  {m}: {v['in']:,}+{v['out']:,} = ${v['cost']:.4f}")

def check_budget(max_cost):
    total = 0
    for logfile in LOG_DIR.glob("*.jsonl"):
        for line in open(logfile):
            total += json.loads(line)["cost_usd"]
    print(f"Budget: ${total:.4f} / ${max_cost:.2f} ({total/max_cost*100:.1f}%)")
    if total > max_cost:
        print("EXCEEDED")
        sys.exit(1)
    print("OK")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cmd = sys.argv[1]
    args = sys.argv[2:]
    if cmd == "log":
        provider = args[args.index("--provider") + 1]
        model = args[args.index("--model") + 1]
        tin = int(args[args.index("--input") + 1])
        tout = int(args[args.index("--output") + 1])
        log_usage(provider, model, tin, tout)
    elif cmd == "report":
        show_report()
    elif cmd == "budget":
        mx = float(args[args.index("--max") + 1])
        check_budget(mx)
    else:
        print(f"Unknown: {cmd}")
        sys.exit(1)
