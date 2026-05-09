#!/usr/bin/env python3
"""Extract token usage from Pi session JSONL files - with proper token accounting."""

import json
from collections import defaultdict
from pathlib import Path

def extract_tokens_from_session(filepath):
    """Extract token usage from a Pi session JSONL file."""
    model_stats = defaultdict(lambda: {
        "calls": 0, 
        "input": 0, 
        "output": 0, 
        "cache_read": 0,
        "cache_write": 0,
        "total_tokens": 0,  # input + output + cacheRead + cacheWrite
        "billing_tokens": 0  # input + output (what you pay for)
    })

    with open(filepath, 'r') as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                if entry.get('type') != 'message':
                    continue

                message = entry.get('message', {})
                usage = message.get('usage')
                model = message.get('model')

                if not usage or not model:
                    continue

                model_stats[model]["calls"] += 1
                model_stats[model]["input"] += usage.get('input', 0)
                model_stats[model]["output"] += usage.get('output', 0)
                model_stats[model]["cache_read"] += usage.get('cacheRead', 0)
                model_stats[model]["cache_write"] += usage.get('cacheWrite', 0)
                model_stats[model]["total_tokens"] += usage.get('totalTokens', 0)
                model_stats[model]["billing_tokens"] += usage.get('input', 0) + usage.get('output', 0)

            except json.JSONDecodeError:
                continue

    return model_stats

def main():
    sessions = [
        ("d5862158 (8080-rom, Apr 15)", "~/.pi/agent/sessions/--home-manuel-code-wesen-2026-04-15--8080-rom--/2026-04-15T15-44-38-065Z_d5862158-d05b-49ac-b6be-15e9795c1a67.jsonl"),
        ("2035dd97 (crib-k3s, Apr 16)", "~/.pi/agent/sessions/--home-manuel-code-wesen-crib-k3s--/2026-04-16T01-34-34-242Z_2035dd97-cfb1-47ba-a90d-41096ae624d5.jsonl"),
        ("07fe66a4 (pinocchiorc, Apr 16)", "~/.pi/agent/sessions/--home-manuel-workspaces-2026-04-10-pinocchiorc--/2026-04-16T18-17-22-406Z_07fe66a4-97ee-4b3a-a802-da3b615bc9f2.jsonl"),
    ]

    glm51_total = {
        "calls": 0, "input": 0, "output": 0, 
        "cache_read": 0, "cache_write": 0,
        "billing_tokens": 0, "total_tokens": 0
    }

    print("=" * 100)
    print("GLM-5.1 TOKEN USAGE - APRIL 15-16, 2026")
    print("=" * 100)
    print()
    print("Token Accounting:")
    print("  - input: New tokens sent to API (billed)")
    print("  - output: Generated tokens from API (billed)")  
    print("  - cacheRead: Tokens read from cache (may be discounted)")
    print("  - cacheWrite: Tokens written to cache (may be discounted)")
    print("  - billing_tokens = input + output (what you typically pay for)")
    print("  - total_tokens = input + output + cacheRead + cacheWrite (all tokens processed)")
    print()

    for session_name, filepath in sessions:
        filepath = Path(filepath).expanduser()
        if not filepath.exists():
            continue

        print(f"\n{'='*100}")
        print(f"Session: {session_name}")
        print(f"{'='*100}")

        stats = extract_tokens_from_session(filepath)

        print(f"\n{'Model':<50} {'Calls':>8} {'Input':>12} {'Output':>12} {'Billing':>14} {'CacheRead':>12} {'Total':>14}")
        print("-" * 100)

        for model, data in sorted(stats.items()):
            print(f"{model:<50} {data['calls']:>8} {data['input']:>12,} {data['output']:>12,} {data['billing_tokens']:>14,} {data['cache_read']:>12,} {data['total_tokens']:>14,}")

            if model == "glm-5.1":
                glm51_total["calls"] += data['calls']
                glm51_total["input"] += data['input']
                glm51_total["output"] += data['output']
                glm51_total["cache_read"] += data['cache_read']
                glm51_total["cache_write"] += data['cache_write']
                glm51_total["billing_tokens"] += data['billing_tokens']
                glm51_total["total_tokens"] += data['total_tokens']

    print()
    print("=" * 100)
    print("GLM-5.1 TOTALS (April 15-16, 2026)")
    print("=" * 100)
    print(f"  API Calls:       {glm51_total['calls']:,}")
    print(f"  Input Tokens:    {glm51_total['input']:,}")
    print(f"  Output Tokens:   {glm51_total['output']:,}")
    print(f"  → BILLING TOTAL: {glm51_total['billing_tokens']:,} tokens (input + output)")
    print()
    print(f"  Cache Read:      {glm51_total['cache_read']:,} tokens")
    print(f"  Cache Write:     {glm51_total['cache_write']:,} tokens")
    print(f"  → TOTAL PROCESS: {glm51_total['total_tokens']:,} tokens (input + output + cache)")
    print()
    print("NOTE: For most providers, 'billing_tokens' (input + output) is what you're charged for.")
    print("      Cache tokens are often billed at a different rate or free.")
    print("=" * 100)

if __name__ == "__main__":
    main()
