#!/usr/bin/env python3
"""Count commits per day per repo using HEAD only (no --all), matching skill methodology."""
import json, os, subprocess

INVEST_DIR = os.path.dirname(os.path.abspath(__file__))
days = ["2026-07-21","2026-07-22","2026-07-23","2026-07-24","2026-07-25","2026-07-26","2026-07-27"]

roots = [
    "/home/manuel/code/wesen",
    "/home/manuel/workspaces",
    "/home/manuel/code/others/llms/pi/nicobailon/surf-cli",
]

repos = []
for root in roots:
    if not os.path.exists(root):
        continue
    for dirpath, dirnames, _ in os.walk(root):
        if '.git' in dirnames:
            repos.append(dirpath)
            dirnames[:] = []
        rel = os.path.relpath(dirpath, root)
        if rel.count(os.sep) >= 4:
            dirnames[:] = []
repos = sorted(set(repos))
print(f"Found {len(repos)} git repos")

results = {}
for repo in repos:
    counts = {}
    for d in days:
        try:
            out = subprocess.run(
                ['git','-C',repo,'log',
                 f'--since={d} 00:00:00',f'--until={d} 23:59:59',
                 '--date=short','--pretty=%H'],
                capture_output=True, text=True, timeout=30)
            lines = [l for l in out.stdout.strip().split('\n') if l.strip()]
            counts[d] = len(lines)
        except Exception as e:
            counts[d] = -1
    total = sum(v for v in counts.values() if v > 0)
    if total > 0:
        results[repo] = counts

with open(os.path.join(INVEST_DIR,'results','git-commits-per-day.json'),'w') as fh:
    json.dump(results, fh, indent=2)

# Print per-day totals
print("\n=== Per-day commit totals (HEAD only) ===")
for d in days:
    day_total = sum(r.get(d,0) for r in results.values() if r.get(d,0)>0)
    repos_active = [r for r,v in results.items() if v.get(d,0)>0]
    print(f"{d}: {day_total} commits across {len(repos_active)} repos")
print(f"\nSaved {len(results)} repos with commits")
