#!/usr/bin/env python3
"""Extract the last fenced ```json block of the assistant's messages from a pi events.jsonl (defensive, as in the
pi subagents handbook). usage: extract.py EVENTS OUT"""
import json, re, sys

texts = []
for line in open(sys.argv[1]):
    try:
        e = json.loads(line)
    except Exception:
        continue
    def walk(o):
        if isinstance(o, dict):
            if o.get("role") == "assistant":
                for c in o.get("content") or []:
                    if isinstance(c, dict) and c.get("type") == "text":
                        texts.append(c["text"])
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(e)
for t in reversed(texts):
    m = re.findall(r"```json\s*(\{.*\})\s*```", t, re.S)
    if not m:
        continue
    txt = m[-1]
    try:
        obj = json.loads(txt)
    except json.JSONDecodeError:
        try:
            obj = json.loads(txt, strict=False)  # raw newlines inside strings
        except json.JSONDecodeError as err:
            print(f"no valid JSON: {err}", file=sys.stderr)
            continue
    json.dump(obj, open(sys.argv[2], "w"), indent=2, ensure_ascii=False)
    print(f"wrote {sys.argv[2]}")
    sys.exit(0)
print("no fenced json block found", file=sys.stderr)
sys.exit(1)
