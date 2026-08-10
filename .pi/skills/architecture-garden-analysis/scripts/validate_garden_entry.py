#!/usr/bin/env python3
"""Validate a Software Architecture Garden project entry.

Checks frontmatter, source snapshot metadata, required analytical sections,
Markdown fences, Obsidian wikilinks/headings, portable math, unresolved template
placeholders, and the Garden root backlink.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
REMOTE_RE = re.compile(r"^(?:git@|ssh://|https?://|file://|/).+")
ANGLE_RE = re.compile(r"<([^>\n]{1,160})>")
ALLOWED_ANGLE_RE = re.compile(
    r"(?:!--.*--|/?(?:br|sub|sup|code|kbd|details|summary|span|div|table|thead|tbody|tr|td|th)(?:\s[^>]*)?/?)$",
    re.I,
)
GENERIC_TYPE_RE = re.compile(r"[A-Z][A-Za-z0-9]*(?:\s*,\s*[A-Z][A-Za-z0-9]*)*")
PORTABILITY_CHECKS = (
    (re.compile(r"\\xRightarrow\b"), r"Use a portable alternative to \\xRightarrow."),
    (re.compile(r"\\llbracket\b"), r"Avoid \\llbracket unless the PDF toolchain supplies it."),
    (re.compile(r"\\mathbin\s*\{?\\bind\b"), r"Use \\operatorname{bind} instead of custom \\bind."),
)

REQUIRED_SECTIONS: tuple[tuple[str, tuple[re.Pattern[str], ...]], ...] = (
    ("snapshot identity and evidence", (re.compile(r"^Snapshot identity and evidence$", re.I),)),
    ("architecture/runtime path", (re.compile(r"^Architecture(?: and runtime path| in one diagram)?$", re.I), re.compile(r"^The architecture in one diagram$", re.I))),
    ("maturity assessment", (re.compile(r"^(?:Pattern )?Maturity assessment$", re.I),)),
    ("architecture debt/open laws", (re.compile(r"^Architecture debt and open laws$", re.I), re.compile(r"^Laws that should guide hardening$", re.I))),
    ("related studies", (re.compile(r"^Related studies$", re.I),)),
)

RECOMMENDED_SECTIONS: tuple[tuple[str, tuple[re.Pattern[str], ...]], ...] = (
    ("candidate common vocabulary", (re.compile(r"^Candidate common vocabulary$", re.I),)),
    ("mathematical and computer-science foundations", (re.compile(r"^Mathematical and computer-science foundations$", re.I),)),
    ("Pattern Zoo correlation", (re.compile(r"^Correlation with the Pattern Zoos$", re.I), re.compile(r"^Cross-correlation with the Pattern Zoos$", re.I))),
    ("cross-project comparison", (re.compile(r"^Cross-project comparison$", re.I),)),
    ("implications for composable APIs", (re.compile(r"^Implications for composable APIs$", re.I), re.compile(r"^Implications for elegant JavaScript APIs$", re.I))),
    ("candidate ecosystem patterns", (re.compile(r"^Candidate ecosystem patterns$", re.I),)),
)


@dataclass(frozen=True)
class Finding:
    level: str
    message: str


def repository_root(start: Path) -> Path:
    result = subprocess.run(
        ["git", "-C", str(start), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        return Path(result.stdout.strip()).resolve()
    return start.resolve()


def parse_frontmatter(text: str) -> tuple[dict[str, str], int, list[Finding]]:
    findings: list[Finding] = []
    if not text.startswith("---\n"):
        return {}, 0, [Finding("ERROR", "Entry does not start with YAML frontmatter.")]
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}, 0, [Finding("ERROR", "YAML frontmatter is not closed.")]
    raw = text[4:end]
    values: dict[str, str] = {}
    for line in raw.splitlines():
        match = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*?)\s*$", line)
        if match:
            values[match.group(1)] = match.group(2).strip('"\'')
    for key in (
        "title",
        "status",
        "type",
        "created",
        "analyzed",
        "repository",
        "repository_remote",
        "repository_commit",
        "repository_branch",
        "repository_commit_date",
        "repository_worktree",
    ):
        if not values.get(key):
            findings.append(Finding("ERROR", f"Frontmatter is missing required property {key}."))
    if values.get("type") and values["type"] != "architecture-garden-project":
        findings.append(Finding("ERROR", "Frontmatter type must be architecture-garden-project."))
    commit = values.get("repository_commit", "")
    if commit and not COMMIT_RE.fullmatch(commit):
        findings.append(Finding("ERROR", "repository_commit must be a full 40-character lowercase hex hash."))
    remote = values.get("repository_remote", "")
    if remote and not REMOTE_RE.fullmatch(remote):
        findings.append(Finding("ERROR", "repository_remote must be an SSH, HTTP(S), file, or absolute-path URL."))
    branch = values.get("repository_branch", "")
    if branch and (branch.strip() != branch or re.search(r"\s", branch)):
        findings.append(Finding("ERROR", "repository_branch must be a non-whitespace Git branch name."))
    commit_date = values.get("repository_commit_date", "")
    if commit_date:
        try:
            datetime.fromisoformat(commit_date.replace("Z", "+00:00"))
        except ValueError:
            findings.append(Finding("ERROR", "repository_commit_date must be an ISO-8601 timestamp."))
    worktree = values.get("repository_worktree", "")
    if worktree and worktree not in {"clean", "dirty"}:
        findings.append(Finding("ERROR", "repository_worktree must be exactly clean or dirty."))
    if not re.search(r"(?m)^tags:\s*$", raw):
        findings.append(Finding("ERROR", "Frontmatter must contain a tags list."))
    if not re.search(r"(?m)^related_files:\s*$", raw):
        findings.append(Finding("WARN", "Frontmatter has no related_files list."))
    if not re.search(r"(?m)^related_notes:\s*$", raw):
        findings.append(Finding("WARN", "Frontmatter has no related_notes list."))
    return values, end + len("\n---\n"), findings


def markdown_headings(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    return {match.group(2).strip() for match in HEADING_RE.finditer(text)}


def resolve_wikilink(entry: Path, root: Path, raw: str) -> tuple[Path, str]:
    target = raw.split("|", 1)[0]
    target = target.split("^", 1)[0]
    if target.startswith("#"):
        return entry, target[1:]
    path_text, separator, heading = target.partition("#")
    candidate = Path(path_text)
    if not candidate.is_absolute():
        candidate = root / candidate
    if not candidate.suffix:
        candidate = candidate.with_suffix(".md")
    return candidate.resolve(), heading if separator else ""


def validate_fences(text: str) -> list[Finding]:
    findings: list[Finding] = []
    active: tuple[str, int] | None = None
    for line in text.splitlines():
        match = re.match(r"^\s*(`{3,}|~{3,})(.*)$", line)
        if not match:
            continue
        marker = match.group(1)
        if active is None:
            active = (marker[0], len(marker))
        elif marker[0] == active[0] and len(marker) >= active[1]:
            active = None
    if active is not None:
        findings.append(Finding("ERROR", f"Unclosed {active[0] * active[1]} code fence."))
    return findings


def validate_sections(text: str) -> list[Finding]:
    findings: list[Finding] = []
    h2 = [match.group(2).strip() for match in HEADING_RE.finditer(text) if len(match.group(1)) == 2]
    positions: list[tuple[str, int]] = []
    for label, patterns in REQUIRED_SECTIONS:
        matches = [i for i, heading in enumerate(h2) if any(pattern.fullmatch(heading) for pattern in patterns)]
        if not matches:
            findings.append(Finding("ERROR", f"Missing required section: {label}."))
        else:
            positions.append((label, matches[0]))
    if len(positions) == len(REQUIRED_SECTIONS):
        observed = [position for _, position in positions]
        if observed != sorted(observed):
            order = [label for label, _ in sorted(positions, key=lambda item: item[1])]
            findings.append(Finding("ERROR", f"Required sections are out of order: {order}"))
    for label, patterns in RECOMMENDED_SECTIONS:
        if not any(any(pattern.fullmatch(heading) for pattern in patterns) for heading in h2):
            findings.append(
                Finding(
                    "WARN",
                    f"Missing conditional section: {label}; add it when evidence supports a claim, or state why it is not applicable.",
                )
            )
    return findings


def run_git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def validate_source_snapshot(values: dict[str, str]) -> list[Finding]:
    findings: list[Finding] = []
    repo_text = values.get("repository", "")
    if not repo_text:
        return findings
    repo = Path(repo_text).expanduser()
    if not repo.exists():
        findings.append(Finding("WARN", f"Analyzed repository path does not exist on this machine: {repo}"))
        return findings
    if run_git(repo, "rev-parse", "--git-dir").returncode != 0:
        findings.append(Finding("WARN", f"Analyzed repository path is not a Git checkout: {repo}"))
        return findings

    recorded = values.get("repository_commit", "")
    if recorded and run_git(repo, "cat-file", "-e", f"{recorded}^{{commit}}").returncode != 0:
        findings.append(Finding("ERROR", f"Recorded repository_commit does not identify a commit in the checkout: {recorded}"))
        return findings

    recorded_date = values.get("repository_commit_date", "")
    if recorded and recorded_date:
        actual_date_result = run_git(repo, "show", "-s", "--format=%cI", recorded)
        if actual_date_result.returncode == 0:
            try:
                expected_dt = datetime.fromisoformat(recorded_date.replace("Z", "+00:00"))
                actual_dt = datetime.fromisoformat(actual_date_result.stdout.strip().replace("Z", "+00:00"))
                if expected_dt != actual_dt:
                    findings.append(
                        Finding(
                            "ERROR",
                            f"repository_commit_date {recorded_date} does not match commit date {actual_date_result.stdout.strip()}.",
                        )
                    )
            except ValueError:
                pass  # Syntax is reported by parse_frontmatter.

    head_result = run_git(repo, "rev-parse", "HEAD")
    head = head_result.stdout.strip() if head_result.returncode == 0 else ""
    if head and recorded and head != recorded:
        findings.append(Finding("WARN", f"Target checkout HEAD {head} differs from recorded snapshot {recorded}."))

    current_remote_result = run_git(repo, "remote", "get-url", "origin")
    current_remote = current_remote_result.stdout.strip() if current_remote_result.returncode == 0 else ""
    recorded_remote = values.get("repository_remote", "")
    if current_remote and recorded_remote and current_remote != recorded_remote:
        findings.append(
            Finding("WARN", f"Current origin {current_remote} differs from recorded repository_remote {recorded_remote}.")
        )

    current_branch_result = run_git(repo, "branch", "--show-current")
    current_branch = current_branch_result.stdout.strip() if current_branch_result.returncode == 0 else ""
    recorded_branch = values.get("repository_branch", "")
    if head == recorded and current_branch and recorded_branch and current_branch != recorded_branch:
        findings.append(
            Finding("WARN", f"Current branch {current_branch} differs from recorded repository_branch {recorded_branch}.")
        )

    status_result = run_git(repo, "status", "--porcelain")
    if status_result.returncode == 0:
        current_worktree = "dirty" if status_result.stdout.strip() else "clean"
        recorded_worktree = values.get("repository_worktree", "")
        if head == recorded and recorded_worktree and current_worktree != recorded_worktree:
            findings.append(
                Finding(
                    "WARN",
                    f"Current worktree is {current_worktree}, but repository_worktree records {recorded_worktree}.",
                )
            )
    return findings


def unresolved_placeholders(text: str) -> list[str]:
    placeholders: list[str] = []
    for match in ANGLE_RE.finditer(text):
        value = match.group(1).strip()
        if ALLOWED_ANGLE_RE.fullmatch(value) or GENERIC_TYPE_RE.fullmatch(value):
            continue
        # Comparison operators normally contain surrounding whitespace and no
        # closing angle pair; angle-delimited lowercase prose is a template marker.
        if re.search(r"[a-z]", value) or " " in value:
            placeholders.append(match.group(0))
    return placeholders


def validate_root_backlink(entry: Path, root: Path, garden_root: Path) -> list[Finding]:
    if not garden_root.exists():
        return [Finding("WARN", f"Garden root README not found: {garden_root}")]
    try:
        relative = entry.relative_to(root).with_suffix("")
    except ValueError:
        return [Finding("WARN", "Entry is outside the repository; Garden root backlink was not checked.")]
    text = garden_root.read_text(encoding="utf-8", errors="replace")
    expected = f"[[{relative.as_posix()}"
    if expected not in text:
        return [Finding("ERROR", f"Garden root does not link to this entry; expected target prefix {expected}.")]
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("entry", type=Path)
    parser.add_argument("--root", type=Path, help="Vault/repository root; defaults to Git root or cwd.")
    parser.add_argument(
        "--garden-root",
        type=Path,
        help="Garden README; defaults to Research/Software Architecture Garden/README.md under root.",
    )
    args = parser.parse_args()

    root = args.root.resolve() if args.root else repository_root(Path.cwd())
    entry = args.entry.resolve()
    garden_root = (
        args.garden_root.resolve()
        if args.garden_root
        else root / "Research/Software Architecture Garden/README.md"
    )
    if not entry.exists():
        print(f"ERROR: entry does not exist: {entry}", file=sys.stderr)
        return 2

    text = entry.read_text(encoding="utf-8", errors="replace")
    values, _, findings = parse_frontmatter(text)
    findings.extend(validate_sections(text))
    findings.extend(validate_fences(text))
    findings.extend(validate_source_snapshot(values))
    findings.extend(validate_root_backlink(entry, root, garden_root))

    if "> [!summary]" not in text:
        findings.append(Finding("ERROR", "Entry has no [!summary] callout."))
    if "```mermaid" not in text:
        findings.append(Finding("WARN", "Entry has no Mermaid architecture diagram."))
    placeholders = unresolved_placeholders(text)
    if placeholders:
        sample = ", ".join(sorted(set(placeholders))[:5])
        findings.append(Finding("ERROR", f"Entry still contains project-template placeholders: {sample}"))

    for expression, message in PORTABILITY_CHECKS:
        count = len(expression.findall(text))
        if count:
            findings.append(Finding("ERROR", f"{message} Found {count} occurrence(s)."))

    heading_cache: dict[Path, set[str]] = {}
    links = list(WIKILINK_RE.finditer(text))
    for match in links:
        raw = match.group(1)
        target, heading = resolve_wikilink(entry, root, raw)
        if not target.exists():
            findings.append(Finding("ERROR", f"Broken wikilink target: [[{raw}]] -> {target}"))
            continue
        if heading and target.suffix.lower() == ".md":
            headings = heading_cache.setdefault(target, markdown_headings(target))
            if heading not in headings:
                findings.append(Finding("ERROR", f"Broken heading anchor: [[{raw}]]"))

    errors = [finding for finding in findings if finding.level == "ERROR"]
    warnings = [finding for finding in findings if finding.level == "WARN"]
    for finding in findings:
        print(f"{finding.level}: {finding.message}")
    print(
        f"Checked {entry}: {len(links)} wikilinks, "
        f"{len(errors)} errors, {len(warnings)} warnings."
    )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
