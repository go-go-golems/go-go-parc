#!/usr/bin/env python3
"""Validate the wikilinks of an Obsidian index (or any vault note).

Checks every ``[[...]]`` link in a markdown file:
  * intra-file links  ``[[#Heading]]`` and ``[[#Heading|alias]]``
  * cross-file links  ``[[path]]``, ``[[path|alias]]``,
                      ``[[path#anchor]]``, ``[[path#anchor|alias]]``

Cross-file targets are resolved two ways, the way Obsidian resolves them:
  * vault-rooted   -- the path is taken from the vault root, and
  * folder-relative -- the path is taken from the directory of the linking file.
A target file is accepted with or without a ``.md`` extension.

An anchor is valid only if it matches a markdown heading in the target file
(strip leading ``#`` markers; trailing/leading whitespace ignored), exactly as
Obsidian links headings.

Usage:
    validate_index_links.py <index.md> [<other.md> ...]
    validate_index_links.py --self-test

Exit code is 0 when every link resolves, 1 otherwise.

This script is intentionally dependency-free (Python 3.8+) so it can be run from
any checkout without installing anything.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Iterable

# A wikilink is [[ target ]], optionally with a #anchor and/or a |alias.
# Targets/anchors/aliases stop at ] or |, so the regex never overruns a link.
WIKILINK_RE = re.compile(r"\[\[([^]\|#]+)(?:#([^]\|]+))?(?:\|[^]]*)?\]\]")
INTRA_RE = re.compile(r"\[\[#([^]\|]+)(?:\|[^]]*)?\]\]")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)
# A fenced code block starts with a line whose first non-space chars are ```
# (optionally followed by a language tag) and ends at the next such fence.
FENCE_RE = re.compile(r'^\s*```')
# An inline code span is a backtick, content with no backtick or newline, backtick.
# Obsidian renders wikilinks inside inline code as literal text too. To match
# Obsidian's anchor resolution we keep the inner text but strip ``[`` and ``]``
# so that example syntax like `` `[[#Entry]]` `` stops looking like a link,
# while a heading such as `` `require()` `` keeps its literal word in the anchor.
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")


def _strip_inline_code(text: str) -> str:
    """Replace inline code spans with their inner text, brackets removed."""
    return INLINE_CODE_RE.sub(
        lambda m: m.group(0)[1:-1].replace("[", "").replace("]", ""), text
    )


def strip_fenced_code(text: str) -> str:
    """Remove fenced code blocks so wikilinks shown as *examples* are not checked.

    Obsidian does not render ``[[...]]`` inside a fenced code block as a link --
    it is literal text -- so a validator that aims to match real link resolution
    must skip those spans.
    """
    out: list[str] = []
    in_fence = False
    for line in text.splitlines(keepends=True):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            out.append("")  # preserve line numbering / heading offsets
            continue
        out.append("" if in_fence else line)
    return "".join(out)


def headings_of(text: str) -> set[str]:
    """Return the set of heading texts (without the leading # marks).

    Inline code inside a heading is normalized the same way links are, so an
    anchor written with backticks (`` `require()` ``) matches the heading.
    """
    return {
        _strip_inline_code(h).strip()
        for _lvl, h in HEADING_RE.findall(text)
    }


def resolve(linking_file: Path, vault: Path, target: str) -> Path | None:
    """Resolve a wikilink target to an existing file, vault-rooted or relative."""
    candidates: list[Path] = []
    for base in (vault, linking_file.parent):
        candidates.append(base / target)
        if not target.endswith(".md"):
            candidates.append(base / f"{target}.md")
    for c in candidates:
        if c.exists():
            return c
    return None


def check_file(file: Path, vault: Path) -> list[str]:
    """Return a list of human-readable problem strings for one file."""
    problems: list[str] = []
    text = file.read_text(encoding="utf-8")
    file_headings = headings_of(text)
    # Only check links outside fenced code blocks and inline code spans, the way
    # Obsidian renders them. Inline code keeps its inner text (minus brackets)
    # so real headings containing inline code still match their anchors.
    prose = _strip_inline_code(strip_fenced_code(text))

    # intra-file anchors
    for anchor in sorted(set(INTRA_RE.findall(prose))):
        if anchor.strip() not in file_headings:
            problems.append(f"intra-file anchor not found: [[#{anchor}]]")

    # cross-file links
    for target, anchor in WIKILINK_RE.findall(prose):
        resolved = resolve(file, vault, target)
        if resolved is None:
            problems.append(f"missing file: [[{target}]]")
            continue
        if anchor:
            target_headings = headings_of(resolved.read_text(encoding="utf-8"))
            if anchor.strip() not in target_headings:
                problems.append(
                    f"anchor not found in {resolved.name}: [[{target}#{anchor}]]"
                )
    return problems


def find_vault(start: Path) -> Path:
    """Walk up to the first directory containing a .obsidian or .git marker.

    Falls back to the linking file's directory when no marker is found, so that
    out-of-vault files (e.g. a temp copy) still resolve folder-relative links."""
    start = start.resolve()
    for p in [start, *start.parents]:
        if (p / ".obsidian").is_dir() or (p / ".git").is_dir():
            return p
    return start.parent if start.is_file() else start


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="*", help="markdown files to validate")
    parser.add_argument(
        "--self-test", action="store_true", help="run a tiny built-in regression"
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.self_test:
        return _self_test()

    if not args.files:
        parser.error("at least one file is required (or use --self-test)")

    vault = find_vault(Path(args.files[0]).resolve())
    total = 0
    for f in args.files:
        path = Path(f)
        if not path.exists():
            print(f"missing file: {f}")
            total += 1
            continue
        problems = check_file(path, vault)
        if problems:
            total += len(problems)
            print(f"[{path.name}] {len(problems)} problem(s):")
            for p in problems:
                print(f"    {p}")
        else:
            print(f"[{path.name}] all links resolve")
    print(f"{'PASS' if total == 0 else f'{total} PROBLEM(S)'}")
    return 0 if total == 0 else 1


def _self_test() -> int:
    """A tiny in-memory regression so the script can be sanity-checked."""
    sample = (
        "# H1 Some Title\n"
        "## A Heading\n"
        "Text with [[#A Heading]] and [[#A Heading|alias]] and "
        "[[note#Other Heading]] and [[broken#Nope]].\n"
    )
    heads = headings_of(sample)
    assert "A Heading" in heads, heads
    assert "H1 Some Title" in heads, heads
    # the regex must not overrun a link boundary
    found = WIKILINK_RE.findall(sample)
    targets = {t for t, _ in found}
    assert "broken" in targets, found
    print("self-test passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
