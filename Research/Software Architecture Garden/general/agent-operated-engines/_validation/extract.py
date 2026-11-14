#!/usr/bin/env python3
"""Extract the JSON answer from the FINAL assistant message of a pi events.jsonl, defensively (pi subagents
handbook). Repairs, tried in order: raw newlines in strings (strict=False); unescaped double quotes inside strings;
mismatched closing brackets. usage: extract.py EVENTS OUT"""
import json, re, sys


def final_text(path):
    texts = []
    for line in open(path):
        try:
            e = json.loads(line)
        except Exception:
            continue
        m = e.get("message") if isinstance(e, dict) else None
        if e.get("type") == "message_end" and isinstance(m, dict) and m.get("role") == "assistant":
            t = "".join(c.get("text", "") for c in m.get("content") or [] if c.get("type") == "text")
            if t.strip():
                texts.append(t)
    return texts[-1] if texts else ""


def escape_inner_quotes(s):
    """Inside a string, a quote not followed (after spaces) by , : } ] or end is escaped."""
    out, i, in_str = [], 0, False
    while i < len(s):
        c = s[i]
        if in_str:
            if c == "\\":
                out.append(s[i:i + 2]); i += 2; continue
            if c == '"':
                j = i + 1
                while j < len(s) and s[j] in " \t\r\n":
                    j += 1
                if j >= len(s) or s[j] in ",:}]":
                    in_str = False; out.append(c)
                else:
                    out.append('\\"')
                i += 1; continue
            out.append(c); i += 1; continue
        if c == '"':
            in_str = True
        out.append(c); i += 1
    return "".join(out)


def balance_closers(s):
    """Replace a closing bracket that does not match the innermost open one."""
    out, stack, in_str, i = [], [], False, 0
    pair = {"{": "}", "[": "]"}
    while i < len(s):
        c = s[i]
        if in_str:
            out.append(c)
            if c == "\\":
                out.append(s[i + 1:i + 2]); i += 2; continue
            if c == '"':
                in_str = False
            i += 1; continue
        if c == '"':
            in_str = True
        elif c in "{[":
            stack.append(c)
        elif c in "}]":
            if stack:
                c = pair[stack.pop()]
        out.append(c); i += 1
    return "".join(out)


def parse(txt):
    attempts = [lambda t: json.loads(t), lambda t: json.loads(t, strict=False),
                lambda t: json.loads(escape_inner_quotes(t), strict=False),
                lambda t: json.loads(balance_closers(t), strict=False),
                lambda t: json.loads(balance_closers(escape_inner_quotes(t)), strict=False)]
    last = None
    for f in attempts:
        try:
            return f(txt)
        except json.JSONDecodeError as e:
            last = e
    raise last


text = final_text(sys.argv[1])
blocks = re.findall(r"```json\s*(\{.*\})\s*```", text, re.S)
if not blocks:
    print("no fenced json block in the final message", file=sys.stderr); sys.exit(1)
try:
    obj = parse(blocks[-1])
except json.JSONDecodeError as err:
    print(f"no valid JSON after repairs: {err}", file=sys.stderr); sys.exit(1)
json.dump(obj, open(sys.argv[2], "w"), indent=2, ensure_ascii=False)
print(f"wrote {sys.argv[2]}")
