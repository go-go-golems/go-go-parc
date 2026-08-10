#!/usr/bin/env python3
"""Validate Pattern Zoo structure, Obsidian links, fences, and portable math.

Run from a repository or vault root:

    python3 .pi/skills/pattern-zoo-authoring/scripts/validate_pattern_zoo.py \
        "Transcripts/Research/09 - RAG-MATHS Pattern Zoo.md" \
        --expected-patterns 12
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


PATTERN_RE = re.compile(r"^# Pattern\s+(\d+)(?:\s*[—:.-]\s*|\s+)(.+?)\s*$", re.MULTILINE)
WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
HEADING_RE = re.compile(r"^#{1,6}\s+(.*?)(?:\s+#+)?\s*$")

REQUIRED_SECTIONS = {
    "first-day": {"The first-day version"},
    "problem": {"The problem it solves", "Problem"},
    "math": {"The mathematical model", "Mathematical model"},
    "advanced": {"Advanced reader: category theory and abstract mathematics"},
    "example": {
        "Worked RAG example and pseudocode",
        "Worked RAG example/pseudocode",
        "Worked example and pseudocode",
    },
    "failures": {"Failure modes"},
    "sightings": {"Names and sightings"},
    "key-points": {"Key points"},
}

PORTABILITY_CHECKS = [
    (re.compile(r"\\\(|\\\)"), r"Use $...$ instead of \\(...\\) for Pandoc portability."),
    (re.compile(r"^\\\[$|^\\\]$", re.MULTILINE), r"Use $$ fences instead of \\[...\\] for Pandoc portability."),
    (re.compile(r"\\llbracket|\\rrbracket"), r"\\llbracket/\\rrbracket may require an unavailable package; use portable notation such as \\mathcal I."),
    (re.compile(r"\\xRightarrow"), r"\\xRightarrow may require mathtools; use \\xrightarrow when possible."),
    (re.compile(r"\\bind\b"), r"Custom \\bind is not portable; use \\operatorname{bind}."),
]


@dataclass
class Finding:
    level: str
    message: str


def repository_root(start: Path) -> Path:
    try:
        result = subprocess.run(
            ["git", "-C", str(start), "rev-parse", "--show-toplevel"],
            check=True,
            capture_output=True,
            text=True,
        )
        return Path(result.stdout.strip()).resolve()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return start.resolve()


def markdown_headings(path: Path) -> set[str]:
    headings: set[str] = set()
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = HEADING_RE.match(line)
        if match:
            headings.add(match.group(1).strip())
    return headings


def validate_fences(text: str) -> list[Finding]:
    findings: list[Finding] = []
    active: tuple[str, int] | None = None
    for number, line in enumerate(text.splitlines(), 1):
        match = re.match(r"^\s*(`{3,}|~{3,})(.*)$", line)
        if not match:
            continue
        marker = match.group(1)
        char = marker[0]
        if active is None:
            active = (char, len(marker))
        elif char == active[0] and len(marker) >= active[1]:
            active = None
    if active is not None:
        findings.append(Finding("ERROR", f"Unclosed {active[0] * active[1]} code fence."))
    return findings


def resolve_wikilink(book: Path, root: Path, raw: str) -> tuple[Path, str]:
    target = raw.split("|", 1)[0]
    target = target.split("^", 1)[0]  # block IDs are not heading-validated here
    if target.startswith("#"):
        return book, target[1:]

    path_text, separator, heading = target.partition("#")
    candidate = Path(path_text)
    if not candidate.is_absolute():
        candidate = root / candidate
    if not candidate.suffix:
        candidate = candidate.with_suffix(".md")
    return candidate.resolve(), heading if separator else ""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("book", type=Path)
    parser.add_argument("--expected-patterns", type=int)
    parser.add_argument("--root", type=Path, help="Vault/repository root; defaults to Git root or cwd.")
    parser.add_argument(
        "--allow-pandoc-hostile-math",
        action="store_true",
        help="Downgrade known PDF-hostile TeX constructs from errors to warnings.",
    )
    args = parser.parse_args()

    book = args.book.resolve()
    if not book.exists():
        print(f"ERROR: file does not exist: {book}", file=sys.stderr)
        return 2

    root = (args.root.resolve() if args.root else repository_root(Path.cwd()))
    text = book.read_text(encoding="utf-8", errors="replace")
    findings: list[Finding] = []

    if not text.startswith("---\n"):
        findings.append(Finding("ERROR", "Book does not start with YAML frontmatter."))
    else:
        end = text.find("\n---\n", 4)
        if end < 0:
            findings.append(Finding("ERROR", "YAML frontmatter is not closed."))
        else:
            frontmatter = text[4:end]
            for key in ("title:", "tags:"):
                if not re.search(rf"(?m)^{re.escape(key)}", frontmatter):
                    findings.append(Finding("WARN", f"Frontmatter has no {key[:-1]} property."))

    matches = list(PATTERN_RE.finditer(text))
    numbers = [int(match.group(1)) for match in matches]
    if args.expected_patterns is not None and len(matches) != args.expected_patterns:
        findings.append(
            Finding("ERROR", f"Expected {args.expected_patterns} patterns, found {len(matches)}.")
        )
    if numbers and numbers != list(range(1, len(numbers) + 1)):
        findings.append(Finding("ERROR", f"Pattern numbering is not contiguous from 1: {numbers}"))
    if not matches:
        findings.append(Finding("ERROR", "No '# Pattern N — Name' headings found."))

    for index, match in enumerate(matches):
        number = int(match.group(1))
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        section = text[match.start():end]
        headings = [
            heading.group(1).strip()
            for line in section.splitlines()
            if (heading := HEADING_RE.match(line)) and line.startswith("## ")
        ]
        positions: list[tuple[str, int]] = []
        for label, accepted in REQUIRED_SECTIONS.items():
            matching_positions = [
                position for position, heading in enumerate(headings) if heading in accepted
            ]
            if not matching_positions:
                findings.append(
                    Finding(
                        "ERROR",
                        f"Pattern {number} is missing {label} section; expected one of {sorted(accepted)}.",
                    )
                )
            else:
                positions.append((label, matching_positions[0]))
        observed_positions = [position for _, position in positions]
        if len(positions) == len(REQUIRED_SECTIONS) and observed_positions != sorted(observed_positions):
            observed_order = [label for label, _ in sorted(positions, key=lambda item: item[1])]
            expected_order = list(REQUIRED_SECTIONS)
            findings.append(
                Finding(
                    "ERROR",
                    f"Pattern {number} sections are out of order: observed {observed_order}; "
                    f"expected {expected_order}.",
                )
            )

    findings.extend(validate_fences(text))

    for expression, message in PORTABILITY_CHECKS:
        count = len(expression.findall(text))
        if count:
            level = "WARN" if args.allow_pandoc_hostile_math else "ERROR"
            findings.append(Finding(level, f"{message} Found {count} occurrence(s)."))

    heading_cache: dict[Path, set[str]] = {}
    link_count = 0
    for match in WIKILINK_RE.finditer(text):
        raw = match.group(1)
        target, heading = resolve_wikilink(book, root, raw)
        link_count += 1
        if not target.exists():
            findings.append(Finding("ERROR", f"Broken wikilink target: [[{raw}]] -> {target}"))
            continue
        if heading and target.suffix.lower() == ".md":
            headings = heading_cache.setdefault(target, markdown_headings(target))
            if heading not in headings:
                findings.append(
                    Finding("ERROR", f"Broken heading anchor: [[{raw}]] (heading not in {target})")
                )

    errors = [finding for finding in findings if finding.level == "ERROR"]
    warnings = [finding for finding in findings if finding.level == "WARN"]

    for finding in findings:
        print(f"{finding.level}: {finding.message}")

    print(
        f"Checked {book}: {len(matches)} patterns, "
        f"{text.count('## Advanced reader: category theory and abstract mathematics')} advanced sections, "
        f"{link_count} wikilinks, {len(errors)} errors, {len(warnings)} warnings."
    )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
