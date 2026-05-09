#!/usr/bin/env python3
"""Analyze glm-5.1 token usage by hour of day."""

import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

def extract_tokens_by_hour(filepath, session_name):
    """Extract glm-5.1 token usage by hour from a minitrace file."""
    hourly_stats = defaultdict(lambda: {"calls": 0, "input": 0, "output": 0, "cache_read": 0})

    with open(filepath, 'r') as f:
        data = json.load(f)

    for turn in data.get('turns', []):
        # Only count glm-5.1 turns with usage
        if turn.get('model') != 'glm-5.1':
            continue

        usage = turn.get('usage')
        if not usage:
            continue

        # Parse timestamp
        timestamp = turn.get('timestamp')
        if not timestamp:
            continue

        try:
            # Parse ISO timestamp
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            hour = dt.hour
            date = dt.strftime('%Y-%m-%d')
            date_hour = f"{date} {hour:02d}:00"

            hourly_stats[date_hour]["calls"] += 1
            hourly_stats[date_hour]["input"] += usage.get('input_tokens', 0) or 0
            hourly_stats[date_hour]["output"] += usage.get('output_tokens', 0) or 0
            hourly_stats[date_hour]["cache_read"] += usage.get('cache_read_tokens', 0) or 0

        except (ValueError, AttributeError):
            continue

    return hourly_stats

def main():
    sessions = [
        ("d5862158 (8080-rom, Apr 15)", "/tmp/minitrace-analysis/pi-sessions/active/2026-04/d5862158-d05b-49ac-b6be-15e9795c1a67.minitrace.json"),
        ("2035dd97 (crib-k3s, Apr 16)", "/tmp/minitrace-analysis/pi-sessions/active/2026-04/2035dd97-cfb1-47ba-a90d-41096ae624d5.minitrace.json"),
        ("07fe66a4 (pinocchiorc, Apr 16)", "/tmp/minitrace-analysis/pi-sessions/active/2026-04/07fe66a4-97ee-4b3a-a802-da3b615bc9f2.minitrace.json"),
    ]

    all_hours = defaultdict(lambda: {"calls": 0, "input": 0, "output": 0, "cache_read": 0, "sessions": set()})

    print("=" * 100)
    print("GLM-5.1 TOKEN USAGE BY HOUR (April 15-16, 2026)")
    print("=" * 100)
    print()

    for session_name, filepath in sessions:
        if not Path(filepath).exists():
            continue

        hourly = extract_tokens_by_hour(filepath, session_name)

        print(f"\n{session_name}")
        print("-" * 100)
        print(f"{'Date/Hour':<20} {'Calls':>8} {'Input':>12} {'Output':>12} {'Billing':>14} {'Cache Read':>14}")
        print("-" * 100)

        for date_hour in sorted(hourly.keys()):
            stats = hourly[date_hour]
            billing = stats['input'] + stats['output']
            print(f"{date_hour:<20} {stats['calls']:>8} {stats['input']:>12,} {stats['output']:>12,} {billing:>14,} {stats['cache_read']:>14,}")

            # Aggregate for all sessions
            all_hours[date_hour]["calls"] += stats['calls']
            all_hours[date_hour]["input"] += stats['input']
            all_hours[date_hour]["output"] += stats['output']
            all_hours[date_hour]["cache_read"] += stats['cache_read']
            all_hours[date_hour]["sessions"].add(session_name)

    # Summary by hour across all sessions
    print()
    print("=" * 100)
    print("COMBINED GLM-5.1 USAGE BY HOUR (All Sessions)")
    print("=" * 100)
    print(f"{'Date/Hour':<20} {'Calls':>8} {'Input':>12} {'Output':>12} {'Billing':>14} {'Cache Read':>14}")
    print("-" * 100)

    total_calls = 0
    total_input = 0
    total_output = 0
    total_cache = 0

    for date_hour in sorted(all_hours.keys()):
        stats = all_hours[date_hour]
        billing = stats['input'] + stats['output']
        total_calls += stats['calls']
        total_input += stats['input']
        total_output += stats['output']
        total_cache += stats['cache_read']
        print(f"{date_hour:<20} {stats['calls']:>8} {stats['input']:>12,} {stats['output']:>12,} {billing:>14,} {stats['cache_read']:>14,}")

    print("-" * 100)
    print(f"{'TOTAL':<20} {total_calls:>8} {total_input:>12,} {total_output:>12,} {total_input + total_output:>14,} {total_cache:>14,}")
    print()

    # Summary by day
    print()
    print("=" * 100)
    print("DAILY SUMMARY")
    print("=" * 100)

    daily = defaultdict(lambda: {"calls": 0, "input": 0, "output": 0, "cache_read": 0})
    for date_hour, stats in all_hours.items():
        day = date_hour.split()[0]
        daily[day]["calls"] += stats['calls']
        daily[day]["input"] += stats['input']
        daily[day]["output"] += stats['output']
        daily[day]["cache_read"] += stats['cache_read']

    print(f"{'Date':<15} {'Calls':>10} {'Input':>14} {'Output':>14} {'Billing':>16} {'Cache Read':>16}")
    print("-" * 90)
    for day in sorted(daily.keys()):
        stats = daily[day]
        billing = stats['input'] + stats['output']
        print(f"{day:<15} {stats['calls']:>10,} {stats['input']:>14,} {stats['output']:>14,} {billing:>16,} {stats['cache_read']:>16,}")

    print()

if __name__ == "__main__":
    main()
