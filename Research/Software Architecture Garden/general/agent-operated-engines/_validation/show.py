#!/usr/bin/env python3
"""Print the answers of one chapter version for reading: quiz, transfer verdicts, review notes, ratings.
usage: show.py NN TAG [--notes-only]"""
import json, pathlib, sys
HERE = pathlib.Path(__file__).resolve().parent
n, tag = sys.argv[1], sys.argv[2]
only = "--notes-only" in sys.argv
for f in sorted(HERE.glob(f"answers/{n}-*-{tag}.json")):
    a = json.loads(f.read_text()); print("=====", f.name)
    if not only:
        for q in a.get("quiz", []): print(" ", q["id"], "|", q.get("answer"))
        for t in a.get("transfer", []):
            print(" ", t["id"], "fits", t.get("fits"), "|", t.get("why"))
            print("     risk:", t.get("risk"))
    for x in a.get("review_notes", []):
        print("  NOTE", x.get("severity"), x.get("kind"), "|", x.get("section"), "|", x.get("note"), "=>", x.get("suggestion"))
    print("  RATINGS", a.get("ratings"))
