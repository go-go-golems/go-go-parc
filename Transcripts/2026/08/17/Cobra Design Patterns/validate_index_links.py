#!/usr/bin/env python3
"""Validate local links and index invariants in the Cobra Architecture Garden.

The bundle uses vault-rooted Obsidian links such as
``Research/Software Architecture Garden/cobra/designs/...``. This validator
maps that prefix back to the bundle root, checks files and headings, checks
ordinary Markdown links, detects duplicate index entries, and verifies that
redirects terminate at canonical entries.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote

VAULT_PREFIX = "Research/Software Architecture Garden/cobra"
INDEX_NAME = "Index of Design Patterns.md"

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)
WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]\n]*\]\(([^)\n]+)\)")
FENCED_BLOCK_RE = re.compile(r"```.*?```|~~~.*?~~~", re.DOTALL)
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
REDIRECT_RE = re.compile(r"^\*See\*\s+\[\[#([^\]]+)\]\]\.\s*$", re.MULTILINE)
EXTERNAL_SCHEMES = ("http://", "https://", "mailto:", "tel:", "data:")


@dataclass(frozen=True)
class Problem:
    file: Path
    line: int
    message: str

    def render(self, root: Path) -> str:
        try:
            name = self.file.relative_to(root)
        except ValueError:
            name = self.file
        return f"{name}:{self.line}: {self.message}"


def strip_nonprose(text: str) -> str:
    """Remove fenced code and comments while preserving line numbers."""

    def blank(match: re.Match[str]) -> str:
        return "\n" * match.group(0).count("\n")

    text = FENCED_BLOCK_RE.sub(blank, text)
    return HTML_COMMENT_RE.sub(blank, text)


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def clean_heading(raw: str) -> str:
    # Remove optional ATX closing hashes and normalize whitespace.
    raw = re.sub(r"\s+#+\s*$", "", raw.strip())
    return re.sub(r"\s+", " ", raw)


def headings_for(text: str) -> dict[str, list[int]]:
    result: dict[str, list[int]] = {}
    for match in HEADING_RE.finditer(strip_nonprose(text)):
        heading = clean_heading(match.group(2))
        result.setdefault(heading, []).append(line_number(text, match.start()))
    return result


def split_target(raw: str, *, wiki: bool) -> tuple[str, str | None]:
    target = raw.strip()
    if wiki:
        target = target.split("|", 1)[0].strip()
    else:
        # Optional Markdown title: path "title". Titles are not used by this bundle.
        target = re.sub(r"\s+[\"'].*[\"']\s*$", "", target).strip()
        if target.startswith("<") and target.endswith(">"):
            target = target[1:-1]
    target = unquote(target)
    if "#" in target:
        path_part, fragment = target.split("#", 1)
        return path_part, fragment or None
    return target, None


def is_external(path_part: str) -> bool:
    lowered = path_part.lower()
    return lowered.startswith(EXTERNAL_SCHEMES) or lowered.startswith("//")


def resolve_target(
    root: Path,
    source: Path,
    path_part: str,
    *,
    wiki: bool,
) -> Path | None:
    if not path_part:
        return source
    if is_external(path_part):
        return None

    normalized = path_part.replace("\\", "/").strip()
    prefix_with_slash = VAULT_PREFIX + "/"
    if normalized == VAULT_PREFIX:
        normalized = "README"
    elif normalized.startswith(prefix_with_slash):
        normalized = normalized[len(prefix_with_slash) :]

    candidate = Path(normalized)
    if wiki:
        if candidate.suffix == "":
            candidate = candidate.with_suffix(".md")
        if candidate.is_absolute():
            resolved = candidate
        elif "/" in normalized:
            resolved = root / candidate
        else:
            # Obsidian permits basename lookup. Prefer the source directory, then
            # require a unique match across the bundle.
            local = source.parent / candidate
            if local.exists():
                return local.resolve()
            matches = [p for p in root.rglob(candidate.name) if p.is_file()]
            if len(matches) == 1:
                return matches[0].resolve()
            return (root / candidate).resolve()
        return resolved.resolve()

    # Ordinary Markdown links are relative to the source document unless they
    # were written with the explicit vault prefix above.
    if path_part.replace("\\", "/").startswith(prefix_with_slash):
        return (root / candidate).resolve()
    return (source.parent / candidate).resolve()


def heading_matches(fragment: str, headings: dict[str, list[int]]) -> bool:
    fragment = clean_heading(unquote(fragment))
    if fragment in headings:
        return True

    # Markdown fragments normally use a GitHub-style slug. This fallback is
    # intentionally narrow; Obsidian heading links should match exactly.
    def slug(value: str) -> str:
        value = value.casefold().strip()
        value = re.sub(r"[^\w\s-]", "", value, flags=re.UNICODE)
        value = re.sub(r"[\s_]+", "-", value)
        return re.sub(r"-+", "-", value).strip("-")

    wanted = fragment.casefold()
    return any(slug(h) == wanted for h in headings)


def validate_links(root: Path) -> list[Problem]:
    problems: list[Problem] = []
    files = sorted(root.rglob("*.md"))
    cache: dict[Path, tuple[str, dict[str, list[int]]]] = {}

    for path in files:
        text = path.read_text(encoding="utf-8")
        cache[path.resolve()] = (text, headings_for(text))

    for source in files:
        original = source.read_text(encoding="utf-8")
        prose = strip_nonprose(original)
        matches: list[tuple[int, str, bool]] = []
        matches.extend((m.start(), m.group(1), True) for m in WIKILINK_RE.finditer(prose))
        matches.extend((m.start(), m.group(1), False) for m in MARKDOWN_LINK_RE.finditer(prose))

        for offset, raw, wiki in sorted(matches):
            path_part, fragment = split_target(raw, wiki=wiki)
            target = resolve_target(root, source, path_part, wiki=wiki)
            if target is None:
                continue

            line = line_number(prose, offset)
            if not target.exists():
                problems.append(Problem(source, line, f"missing target: {raw!r} -> {target}"))
                continue
            if target.is_dir():
                continue
            if fragment is None:
                continue
            if target.suffix.lower() != ".md":
                problems.append(Problem(source, line, f"fragment on non-Markdown target: {raw!r}"))
                continue

            target_key = target.resolve()
            if target_key not in cache:
                target_text = target.read_text(encoding="utf-8")
                cache[target_key] = (target_text, headings_for(target_text))
            target_headings = cache[target_key][1]
            if not heading_matches(fragment, target_headings):
                problems.append(
                    Problem(
                        source,
                        line,
                        f"missing heading {fragment!r} in {target.relative_to(root) if target.is_relative_to(root) else target}",
                    )
                )

    return problems


def validate_index(root: Path) -> list[Problem]:
    problems: list[Problem] = []
    index_path = root / INDEX_NAME
    if not index_path.exists():
        return [Problem(index_path, 1, "index file is missing")]

    text = index_path.read_text(encoding="utf-8")
    h3 = [
        (clean_heading(m.group(2)), line_number(text, m.start()))
        for m in HEADING_RE.finditer(strip_nonprose(text))
        if len(m.group(1)) == 3
    ]
    counts = Counter(name for name, _ in h3)
    for name, count in sorted(counts.items()):
        if count > 1:
            first_line = next(line for heading, line in h3 if heading == name)
            problems.append(Problem(index_path, first_line, f"duplicate level-3 index heading {name!r} ({count} occurrences)"))

    headings = {name for name, _ in h3}
    redirects: dict[str, str] = {}
    current_h3: str | None = None
    for line_no, line in enumerate(text.splitlines(), 1):
        match = re.match(r"^###\s+(.+?)\s*$", line)
        if match:
            current_h3 = clean_heading(match.group(1))
            continue
        if current_h3:
            redirect = REDIRECT_RE.match(line)
            if redirect:
                redirects[current_h3] = clean_heading(redirect.group(1))

    for alias, target in sorted(redirects.items()):
        line = next(line for heading, line in h3 if heading == alias)
        if target not in headings:
            problems.append(Problem(index_path, line, f"redirect {alias!r} points to missing heading {target!r}"))
        elif target in redirects:
            problems.append(Problem(index_path, line, f"redirect chain is not allowed: {alias!r} -> {target!r}"))
        elif target == alias:
            problems.append(Problem(index_path, line, f"self-redirect is not allowed: {alias!r}"))

    return problems


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "root",
        nargs="?",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Garden bundle root (defaults to the parent of scripts/)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    if not root.is_dir():
        print(f"error: not a directory: {root}", file=sys.stderr)
        return 2

    problems = validate_index(root) + validate_links(root)
    if problems:
        for problem in sorted(problems, key=lambda p: (str(p.file), p.line, p.message)):
            print(problem.render(root), file=sys.stderr)
        print(f"FAILED: {len(problems)} validation problem(s)", file=sys.stderr)
        return 1

    markdown_count = sum(1 for _ in root.rglob("*.md"))
    print(f"PASS: {markdown_count} Markdown files; index headings, redirects, files, and heading links resolve")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
