#!/usr/bin/env python3
"""Collect the high-severity review notes of one chapter version across all runs, grouped by kind.
usage: highnotes.py NN TAG [MAXCHARS]"""
import json, pathlib, sys
HERE = pathlib.Path(__file__).resolve().parent
n, tag = sys.argv[1], sys.argv[2]; mx = int(sys.argv[3]) if len(sys.argv) > 3 else 260
rows = []
for f in sorted(HERE.glob(f"answers/{n}-*-{tag}.json")):
    sc = f.name[len(n) + 1:-len(tag) - 6]
    for x in json.loads(f.read_text()).get("review_notes", []):
        if x.get("severity") == "high":
            rows.append((x.get("kind", ""), sc, x.get("section", ""), x.get("note", ""), x.get("suggestion", "")))
for kind in ("wrong", "missing", "unclear", "too-specific", "too-long", "other"):
    for k, sc, sec, note, sug in rows:
        if k == kind:
            print(f"[{k}|{sc}] {sec[:60]} :: {note[:mx]}  => {sug[:mx//2]}")
