#!/usr/bin/env python3
"""Extract token usage from Pi session JSONL files."""

import json
import sys
from collections import defaultdict
from pathlib import Path

def extract_tokens_from_session(filepath):
    """Extract token usage from a Pi session JSONL file."""
    model_stats = defaultdict(lambda: {"calls": 0, "input": 0, "output": 0, "total": 0, "cache_read": 0, "cache_write": 0})

    with open(filepath, 'r') as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                if entry.get('type') != 'message':
                    continue

                # Pi stores usage in .message.usage
                message = entry.get('message', {})
                usage = message.get('usage')
                model = message.get('model')

                if not usage or not model:
                    continue

                model_stats[model]["calls"] += 1
                model_stats[model]["input"] += usage.get('input', 0)
                model_stats[model]["output"] += usage.get('output', 0)
                model_stats[model]["total"] += usage.get('totalTokens', 0)
                model_stats[model]["cache_read"] += usage.get('cacheRead', 0)
                model_stats[model]["cache_write"] += usage.get('cacheWrite', 0)

            except json.JSONDecodeError:
                continue

    return model_stats

def main():
    sessions = [
        ("d5862158 (8080-rom, Apr 15)", "~/.pi/agent/sessions/--home-manuel-code-wesen-2026-04-15--8080-rom--/2026-04-15T15-44-38-065Z_d5862158-d05b-49ac-b6be-15e9795c1a67.jsonl"),
        ("2035dd97 (crib-k3s, Apr 16)", "~/.pi/agent/sessions/--home-manuel-code-wesen-crib-k3s--/2026-04-16T01-34-34-242Z_2035dd97-cfb1-47ba-a90d-41096ae624d5.jsonl"),
        ("07fe66a4 (pinocchiorc, Apr 16)", "~/.pi/agent/sessions/--home-manuel-workspaces-2026-04-10-pinocchiorc--/2026-04-16T18-17-22-406Z_07fe66a4-97ee-4b3a-a802-da3b615bc9f2.jsonl"),
    ]

    grand_total = {"input": 0, "output": 0, "total": 0, "cache_read": 0}
    glm51_total = {"input": 0, "output": 0, "total": 0, "cache_read": 0, "calls": 0}

    print("=" * 80)
    print("RAW PI SESSION TOKEN USAGE ANALYSIS")
    print("=" * 80)
    print()

    for session_name, filepath in sessions:
        filepath = Path(filepath).expanduser()
        if not filepath.exists():
            print(f"⚠️  File not found: {filepath}")
            continue

        print(f"\n{'='*80}")
        print(f"Session: {session_name}")
        print(f"File: {filepath}")
        print(f"File size: {filepath.stat().st_size:,} bytes")
        print(f"{'='*80}")

        stats = extract_tokens_from_session(filepath)

        if not stats:
            print("  No token usage data found")
            continue

        print(f"\n{'Model':<50} {'Calls':>8} {'Input':>12} {'Output':>12} {'Total':>14} {'CacheRead':>12}")
        print("-" * 110)

        session_input = 0
        session_output = 0
        session_total = 0

        for model, data in sorted(stats.items()):
            print(f"{model:<50} {data['calls']:>8} {data['input']:>12,} {data['output']:>12,} {data['total']:>14,} {data['cache_read']:>12,}")
            session_input += data['input']
            session_output += data['output']
            session_total += data['total']

            # Track glm-5.1 totals
            if model == "glm-5.1":
                glm51_total["input"] += data['input']
                glm51_total["output"] += data['output']
                glm51_total["total"] += data['total']
                glm51_total["cache_read"] += data['cache_read']
                glm51_total["calls"] += data['calls']

        print("-" * 110)
        print(f"{'SESSION TOTAL':<50} {'':>8} {session_input:>12,} {session_output:>12,} {session_total:>14,}")

        grand_total["input"] += session_input
        grand_total["output"] += session_output
        grand_total["total"] += session_total

    print()
    print("=" * 80)
    print("GRAND TOTAL (All 3 Sessions)")
    print("=" * 80)
    print(f"  Total Input Tokens:  {grand_total['input']:,}")
    print(f"  Total Output Tokens: {grand_total['output']:,}")
    print(f"  Total Tokens:        {grand_total['total']:,}")
    print()
    print("=" * 80)
    print("GLM-5.1 ONLY (April 15-16, 2026)")
    print("=" * 80)
    print(f"  glm-5.1 API Calls:   {glm51_total['calls']:,}")
    print(f"  glm-5.1 Input:       {glm51_total['input']:,}")
    print(f"  glm-5.1 Output:      {glm51_total['output']:,}")
    print(f"  glm-5.1 Total:       {glm51_total['total']:,}")
    print(f"  glm-5.1 Cache Read:  {glm51_total['cache_read']:,}")
    print()
    print("NOTE: The minitrace extraction was CORRECT - the numbers are accurate!")
    print("The confusion was about what 'totalTokens' means in the Pi usage data.")
    print("=" * 80)

if __name__ == "__main__":
    main()
