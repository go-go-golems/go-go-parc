#!/usr/bin/env python3
"""Find git repos under candidate cwds and count commits per day for the week."""
import json, os, subprocess
from datetime import datetime

INVEST_DIR = os.path.dirname(os.path.abspath(__file__))
days = ["2026-07-21","2026-07-22","2026-07-23","2026-07-24","2026-07-25","2026-07-26","2026-07-27"]

# Candidate roots from cwds
roots = [
    "/home/manuel/code/wesen",
    "/home/manuel/workspaces",
    "/home/manuel/code/others/llms/pi/nicobailon/surf-cli",
]

# Find all .git dirs (repos) under roots, depth-limited
repos = []
for root in roots:
    if not os.path.exists(root):
        continue
    for dirpath, dirnames, _ in os.walk(root):
        # skip nested .git
        if '.git' in dirnames:
            repos.append(dirpath)
            # don't descend into this repo's tree
            dirnames[:] = []
        # limit depth a bit
        rel = os.path.relpath(dirpath, root)
        if rel.count(os.sep) >= 4:
            dirnames[:] = []

# dedupe
repos = sorted(set(repos))
print(f"Found {len(repos)} git repos")

# For each repo, count commits per day
results = {}
for repo in repos:
    counts = {}
    for d in days:
        try:
            out = subprocess.run(
                ['git','-C',repo,'log','--all',
                 f'--since={d} 00:00:00','--until={d} 23:59:59',
                 '--date=short','--pretty=%H'],
                capture_output=True, text=True, timeout=30)
            lines = [l for l in out.stdout.strip().split('\n') if l.strip()]
            counts[d] = len(lines)
        except Exception as e:
            counts[d] = -1
    total = sum(v for v in counts.values() if v > 0)
    if total > 0:
        results[repo] = counts
        print(f"{repo}: {counts} (total {total})")

with open(os.path.join(INVEST_DIR,'results','git-commits-per-day.json'),'w') as fh:
    json.dump(results, fh, indent=2)
print(f"\nSaved git-commits-per-day.json ({len(results)} repos with commits)")
