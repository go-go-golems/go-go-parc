#!/usr/bin/env python3
"""Score the answers of one chapter version against its key (keys/NN.json, never shown to the agents).
usage: score.py NN TAG [TAG2]   (with TAG2: the same scenarios compared across two versions)

keys/NN.json: {"quiz": {"a": {"Q1": [["word", "synonym"], ["other"]], ...}, ...},
               "fits": {"a": {"T1": true, "T2": false}, ...}}
A quiz answer passes when, for every group, at least one of its words appears (case-insensitive).
Prints per run: quiz passed, fit verdicts right, review-note counts by severity, ratings, answer size, and the
behaviour seen in events.jsonl (thinking characters, turns)."""
import json, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
RUNS = pathlib.Path.home() / "pattern-validation" / "agent-operated-engines"


def behaviour(n, tag, sc):
    ev = RUNS / n / tag / sc / "events.jsonl"
    think = text = turns = 0
    if not ev.exists():
        return {}
    for line in ev.open():
        try:
            e = json.loads(line)
        except Exception:
            continue
        m = e.get("message") if isinstance(e, dict) else None
        if e.get("type") == "message_end" and isinstance(m, dict) and m.get("role") == "assistant":
            turns += 1
            for c in m.get("content") or []:
                if c.get("type") == "thinking":
                    think += len(c.get("thinking") or "")
                elif c.get("type") == "text":
                    text += len(c.get("text") or "")
    return {"turns": turns, "thinking_chars": think, "text_chars": text}


def score(n, tag):
    key = json.loads((HERE / "keys" / f"{n}.json").read_text())
    rows = []
    for f in sorted(HERE.glob(f"answers/{n}-*-{tag}.json")):
        sc = f.name[len(n) + 1:-len(tag) - 6]
        a = json.loads(f.read_text())
        qk, fk = key["quiz"].get(sc, {}), key["fits"].get(sc, {})
        quiz = {q["id"]: q.get("answer", "") for q in a.get("quiz", [])}
        qpass = [qid for qid, groups in qk.items()
                 if all(any(w.lower() in str(quiz.get(qid, "")).lower() for w in g) for g in groups)]
        fits = {t["id"]: t.get("fits") for t in a.get("transfer", [])}
        fright = [tid for tid, want in fk.items() if fits.get(tid) is want]
        notes = a.get("review_notes", [])
        sev = {s: sum(1 for x in notes if x.get("severity") == s) for s in ("high", "medium", "low")}
        r = a.get("ratings", {})
        rows.append((sc, f"quiz {len(qpass)}/{len(qk)}", f"fits {len(fright)}/{len(fk)}",
                     f"notes h{sev['high']} m{sev['medium']} l{sev['low']}",
                     f"clarity {r.get('clarity')} reuse {r.get('reusability')} apply {r.get('would_apply_it')}",
                     behaviour(n, tag, sc),
                     [q for q in qk if q not in qpass], [t for t in fk if t not in fright]))
    return rows


for tag in sys.argv[2:]:
    print(f"== chapter {sys.argv[1]} version {tag}")
    for sc, q, ft, nt, rt, b, qmiss, fmiss in score(sys.argv[1], tag):
        print(f"  {sc}: {q}, {ft}, {nt}, {rt}, {b}" + (f"  missed quiz {qmiss}" if qmiss else "") +
              (f"  wrong fits {fmiss}" if fmiss else ""))
