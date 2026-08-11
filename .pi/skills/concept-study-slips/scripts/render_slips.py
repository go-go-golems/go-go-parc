#!/usr/bin/env python3
"""Render concept YAML files as brutalist almanach slips for the thermal printer.

Two forms, both generated from one concept file so they cannot drift:

  card      title -> SYMBOLS table -> law banner -> DISCIPLINE (is/is not)
            -> vocabulary -> SIGHTED IN specimen -> OBSERVED -> limit   (~15cm)
  briefing  a labelled section stack for someone new to the code        (~45cm)

See ../references/CONCEPT-TEMPLATE.yaml for the input schema and
../references/PLAYBOOK.md for how to gather the content.

Usage:
  render_slips.py --concepts DIR                    # write layouts for all
  render_slips.py --concepts DIR 03 05              # only those ids
  render_slips.py --concepts DIR --preview 03       # render a PNG and look at it
  render_slips.py --concepts DIR --print 03         # print via the crib service
  render_slips.py --concepts DIR --form briefing --print 03

Requires pyyaml and almanach-render-service on PATH (see the almanach-printing
skill for printer setup).
"""

import argparse
import pathlib
import subprocess
import sys

import yaml

WEB_DIR = pathlib.Path.home() / "code/wesen/go-go-golems/almanach/web/dist"

# Code and math must escape the brutalist theme's uppercasing, and Archivo has
# no set-theory glyphs — hence the explicit font stacks.
MONO = {"font": "'DejaVu Sans Mono', monospace", "textCase": "none", "weight": 700, "size": 10}
MATH = {"font": "'DejaVu Sans', sans-serif", "textCase": "none"}

PAGE = {"almanach_studio_version": 1, "theme": "brutalist", "paperWidth": 384,
        "bodyScale": 1, "feedLines": 8}


def page(blocks: list[dict]) -> dict:
    return {**PAGE, "blocks": blocks}


def card_for(c: dict) -> dict:
    """The study slip: one law at a glance, for a chalkboard."""
    p = c["slug"]
    blocks: list[dict] = [
        {"id": f"{p}-title", "type": "title",
         "data": {"text": c["title"], "subtitle": c["subtitle"]}},
        {"id": f"{p}-sym-label", "type": "text", "data": {"text": "SYMBOLS", "preset": "micro"}},
        {"id": f"{p}-sym", "type": "table",
         "data": {"cols": [{"label": "SYM", "w": 78}, {"label": "MEANING", "w": "1fr"}],
                  "rows": [list(r) for r in c["symbols"]]}},
        {"id": f"{p}-law", "type": "banner", "data": {"text": c["law"], "pad": "m"},
         "style": dict(MATH)},
    ]
    if c.get("law_extra"):
        blocks.append({"id": f"{p}-law2", "type": "text",
                       "data": {"text": c["law_extra"], "preset": "body", "align": "center"},
                       "style": dict(MATH)})
    disc = c["discipline"]
    blocks += [
        {"id": f"{p}-disc-label", "type": "text", "data": {"text": "DISCIPLINE", "preset": "micro"}},
        {"id": f"{p}-disc", "type": "table",
         "data": {"cols": [{"label": "IT IS", "w": "1fr"}, {"label": "IT IS NOT", "w": "1fr"}],
                  "rows": [[a, b] for a, b in zip(disc["is"], disc["is_not"])]}},
        {"id": f"{p}-vocab", "type": "kv",
         "data": {"items": [["LOCAL", c["vocabulary"]["local"]],
                            ["AS A PATTERN", c["vocabulary"]["proposed"]],
                            ["ELSEWHERE", c["vocabulary"]["elsewhere"]]]}},
        {"id": f"{p}-rule1", "type": "rule", "data": {"weight": "thick"}},
        {"id": f"{p}-sight", "type": "text",
         "data": {"text": f"SIGHTED IN  {c['sighted_in']['symbol']}", "preset": "micro"}},
        {"id": f"{p}-file", "type": "text",
         "data": {"text": c["sighted_in"]["file"], "preset": "small"}, "style": dict(MONO)},
    ]
    # One block per code line: "\n" does not break a line inside a text block.
    for i, line in enumerate(c["sighted_in"]["code"]):
        blocks.append({"id": f"{p}-code-{i}", "type": "text",
                       "data": {"text": line, "preset": "small"}, "style": dict(MONO)})
    blocks += [
        {"id": f"{p}-obs-label", "type": "text", "data": {"text": "OBSERVED", "preset": "micro"}},
        {"id": f"{p}-obs", "type": "text",
         "data": {"text": c["observed"].strip(), "preset": "body"}},
        {"id": f"{p}-rule2", "type": "rule", "data": {"weight": "heavy"}},
        {"id": f"{p}-note", "type": "text", "data": {"text": c["note"].strip(), "preset": "body"},
         "style": dict(MATH)},
    ]
    return page(blocks)


def briefing_for(c: dict) -> dict:
    """The long form: why it exists, how it works, who calls it, what bites."""
    b = c["briefing"]
    p = c["slug"]
    blocks: list[dict] = [
        {"id": f"{p}-b-band", "type": "banner", "data": {"text": b["label"], "pad": "m"}},
        {"id": f"{p}-b-title", "type": "title",
         "data": {"text": b["headline"], "subtitle": b["file"]}},
    ]
    for n, section in enumerate(b["sections"]):
        blocks += [
            {"id": f"{p}-b{n}-rule", "type": "rule", "data": {"weight": "thick"}},
            {"id": f"{p}-b{n}-label", "type": "text",
             "data": {"text": section["label"], "preset": "micro"}},
        ]
        for i, line in enumerate(section.get("code", [])):
            blocks.append({"id": f"{p}-b{n}-code-{i}", "type": "text",
                           "data": {"text": line, "preset": "small"}, "style": dict(MONO)})
        if section.get("kv"):
            blocks.append({"id": f"{p}-b{n}-kv", "type": "kv",
                           "data": {"items": [list(r) for r in section["kv"]]}})
        if section.get("checks"):
            # columns: 1 — the default two-up grid breaks items across the gutter.
            blocks.append({"id": f"{p}-b{n}-checks", "type": "checks",
                           "data": {"items": section["checks"], "columns": 1}})
        if section.get("text"):
            # Labels stay brutalist; paragraphs drop to mixed case, because a
            # screen of all-caps prose is slower to read, not louder.
            blocks.append({"id": f"{p}-b{n}-text", "type": "text",
                           "data": {"text": section["text"].strip(), "preset": "body"},
                           "style": {"textCase": "none"}})
    return page(blocks)


PAPER_HINT = ("a print that hangs or times out almost always means the printer is OUT OF PAPER "
              "or off the network — check the paper, then https://almanach.crib.scapegoat.dev/health. "
              "Do NOT blind-retry: queued jobs land later, so each retry is another physical copy.")


def do_print(target: pathlib.Path) -> bool:
    """Print one layout once. Never retries — see PAPER_HINT."""
    try:
        done = subprocess.run(
            ["almanach-render-service", "print-remote", "--layout", str(target), "--output", "yaml"],
            capture_output=True, text=True, timeout=240)
    except subprocess.TimeoutExpired:
        print(f"  PRINT TIMED OUT: {target.name}\n  {PAPER_HINT}", file=sys.stderr)
        return False
    status = next((l.strip() for l in done.stdout.splitlines() if "status_code" in l), None)
    if done.returncode != 0:
        detail = (done.stderr or done.stdout).strip().splitlines()
        print(f"  PRINT FAILED: {target.name}", file=sys.stderr)
        for line in detail[-3:]:
            print(f"    {line}", file=sys.stderr)
        print(f"  {PAPER_HINT}", file=sys.stderr)
        return False
    print(f"  printed {target.name} ({status or 'no status reported'})")
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="*", help="concept ids, e.g. 03 05 (default: all)")
    ap.add_argument("--concepts", type=pathlib.Path, default=pathlib.Path.cwd(),
                    help="directory of concept YAML files (default: cwd)")
    ap.add_argument("--form", choices=["both", "card", "briefing"], default="both",
                    help="which forms to produce (default: both)")
    ap.add_argument("--print", dest="do_print", action="store_true",
                    help="print through the remote almanach service, once, with no retry")
    ap.add_argument("--preview", action="store_true",
                    help="render a local PNG — always look at it before printing")
    args = ap.parse_args()

    source = args.concepts.resolve()
    out = source / "layouts"
    out.mkdir(parents=True, exist_ok=True)
    forms = ["briefing", "card"] if args.form == "both" else [args.form]

    rendered = failed = 0
    for path in sorted(source.glob("*.yaml")):
        concept = yaml.safe_load(path.read_text())
        if not isinstance(concept, dict) or "slug" not in concept:
            continue
        if args.ids and concept["id"] not in args.ids:
            continue

        for form in forms:
            if form == "briefing" and "briefing" not in concept:
                # The briefing is required: say so loudly rather than skipping.
                print(f"ERROR {path.name}: no briefing: section — the briefing is the primary "
                      f"form. Add it (see CONCEPT-TEMPLATE.yaml) and re-run.", file=sys.stderr)
                failed += 1
                continue
            suffix = "" if form == "card" else "-briefing"
            target = out / f"{concept['id']}-{concept['slug']}{suffix}.yaml"
            render = card_for if form == "card" else briefing_for
            yaml.safe_dump(render(concept), target.open("w"),
                           allow_unicode=True, sort_keys=False, width=10000)
            print(f"wrote {target.relative_to(source)}")
            rendered += 1

            if args.preview:
                subprocess.run(["almanach-render-service", "render", "--layout", str(target),
                                "--out", str(target.with_suffix(".png")), "--web-dir", str(WEB_DIR),
                                "--output", "yaml"], check=True, stdout=subprocess.DEVNULL)
                print(f"  preview {target.with_suffix('.png').relative_to(source)}")
            if args.do_print and not do_print(target):
                failed += 1

    if rendered == 0:
        print(f"no concept files matched in {source}", file=sys.stderr)
        return 1
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
