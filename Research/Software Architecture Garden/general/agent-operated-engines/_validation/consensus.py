#!/usr/bin/env python3
"""Consensus defects: chapter sections flagged with high severity by two or more independent runs of one version.
Reviewers are asked for at least five notes and usually rate two or three as high, so a single high note is weak
evidence; agreement between runs is strong. usage: consensus.py NN TAG [MINRUNS]"""
import json, pathlib, re, sys, collections
HERE = pathlib.Path(__file__).resolve().parent
n, tag = sys.argv[1], sys.argv[2]; need = int(sys.argv[3]) if len(sys.argv) > 3 else 2

def keys(section):
    s = section.lower()
    out = set()
    for m in re.finditer(r"(?:implementation )?notes? (\d+)(?:\s*(?:and|,|&|–|-|vs\.?)\s*(\d+))?", s):
        out.update("note " + g for g in m.groups() if g)
    for word in ("sketch", "motivation", "solution", "structure", "collaboration", "applicability", "consequence",
                 "known use", "variation", "forces", "intent", "problem", "related"):
        if word in s:
            out.add(word)
    return out or {s[:30]}

flag = collections.defaultdict(lambda: collections.defaultdict(list))
runs = 0
for f in sorted(HERE.glob(f"answers/{n}-*-{tag}.json")):
    runs += 1; sc = f.name[len(n) + 1:-len(tag) - 6]
    for x in json.loads(f.read_text()).get("review_notes", []):
        if x.get("severity") == "high":
            for k in keys(x.get("section", "")):
                flag[k][sc].append(f"[{x.get('kind')}] {x.get('note', '')[:170]}")
print(f"== {n} {tag}: {runs} runs")
for k, by in sorted(flag.items(), key=lambda kv: -len(kv[1])):
    if len(by) >= need:
        print(f"  {k}: flagged high by {len(by)} runs ({', '.join(sorted(by))})")
        for sc, notes in sorted(by.items()):
            print(f"     {sc}: {notes[0]}")
