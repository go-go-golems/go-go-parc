#!/usr/bin/env python3
"""Unblind the design reviews of one task: scores per implementation with its arm (chapter or control), means per
arm and lens, ranking positions, and the chapter lessons.  usage: unblind.py NN"""
import json, pathlib, statistics, sys

HERE = pathlib.Path(__file__).resolve().parent
REVIEWS = HERE.parent.parent / "reviews"
LENSES = ["forces", "adapted", "wholeness", "habitability", "growth", "smells", "tests"]
n = sys.argv[1]
by_arm = {}
for f in sorted(REVIEWS.glob(f"{n}-*.json")):
    if f.name.endswith("-key.json"):
        continue
    rev = f.stem[len(n) + 1:]
    key = json.loads((REVIEWS / f"{n}-{rev}-key.json").read_text())
    a = json.loads(f.read_text())
    ranking = a.get("ranking", [])
    print(f"== {n} review {rev}")
    for letter, impl in sorted(a.get("implementations", {}).items()):
        k = key.get(letter, {})
        s = impl.get("scores", {})
        pos = ranking.index(letter) + 1 if letter in ranking else None
        print(f"  {letter} {k.get('arm', '?'):7} {k.get('tag', '?')}/{k.get('agent', '?'):3} "
              + " ".join(f"{l[:5]}={s.get(l)}" for l in LENSES) + f"  rank={pos}")
        for l in LENSES:
            if isinstance(s.get(l), (int, float)):
                by_arm.setdefault(k.get("arm"), {}).setdefault(l, []).append(s[l])
        by_arm.setdefault(k.get("arm"), {}).setdefault("rank", []).append(pos or 0)
    g = a.get("generativity", {})
    print("  groups:", g.get("groups"), "| shared seams:", [(x.get("seam"), x.get("in")) for x in g.get("shared_seams", [])][:6])
    print("  worse is better:", (a.get("worse_is_better") or "")[:300])
    for lesson in a.get("chapter_lessons", []):
        print("  lesson:", lesson[:300])
print("== means per arm")
for arm, d in sorted(by_arm.items(), key=lambda x: str(x[0])):
    print(f"  {arm:8} " + " ".join(f"{l[:5]}={statistics.mean(v):.1f}" for l, v in d.items() if v))
