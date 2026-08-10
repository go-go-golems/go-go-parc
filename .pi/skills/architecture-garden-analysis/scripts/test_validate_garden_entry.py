#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("validate_garden_entry.py").resolve()


class GardenEntryValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "vault"
        self.target = Path(self.temp.name) / "target"
        self.entry = self.root / "Research/Software Architecture Garden/demo/README.md"
        self.garden = self.root / "Research/Software Architecture Garden/README.md"
        self.target.mkdir(parents=True)
        self.root.mkdir(parents=True)

        self.git("init", "-b", "main")
        self.git("config", "user.name", "Validator Test")
        self.git("config", "user.email", "validator@example.com")
        self.git("remote", "add", "origin", "ssh://git@example.com/org/demo.git")
        (self.target / "README.md").write_text("# Demo\n")
        self.git("add", "README.md")
        self.git("commit", "-m", "Initial demo")
        self.commit = self.git("rev-parse", "HEAD").stdout.strip()
        self.commit_date = self.git("show", "-s", "--format=%cI", self.commit).stdout.strip()

        self.entry.parent.mkdir(parents=True)
        self.garden.parent.mkdir(parents=True, exist_ok=True)
        self.garden.write_text(
            "# Garden\n\n[[Research/Software Architecture Garden/demo/README|demo]]\n"
        )
        (self.root / "Evidence.md").write_text("# Evidence\n")
        self.entry.write_text(self.valid_entry())

    def tearDown(self) -> None:
        self.temp.cleanup()

    def git(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", "-C", str(self.target), *args],
            capture_output=True,
            text=True,
            check=True,
        )

    def valid_entry(self) -> str:
        return f"""---
title: Architecture Garden — demo
status: active
type: architecture-garden-project
created: 2026-08-10
analyzed: 2026-08-10
repository: {self.target}
repository_remote: ssh://git@example.com/org/demo.git
repository_commit: {self.commit}
repository_branch: main
repository_commit_date: {self.commit_date}
repository_worktree: clean
tags:
  - architecture-garden
related_files:
  - README.md
related_notes:
  - \"[[Research/Software Architecture Garden/README]]\"
---

# Architecture Garden — demo

> [!summary]
> Minimal valid fixture with `List<T>` and portable math.

![[Evidence]]

## Snapshot identity and evidence

Pinned source.

## Architecture and runtime path

```mermaid
flowchart LR
    A[Input<br/>typed] --> B[Output]
```

$$
\\mathsf X
$$

## Pattern maturity assessment

No cross-project relation is claimed.

## Architecture debt and open laws

No open law was found in this fixture.

## Related studies

- [[Evidence]]
"""

    def validate(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(self.entry),
                "--root",
                str(self.root),
                "--garden-root",
                str(self.garden),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

    def replace(self, old: str, new: str) -> None:
        self.entry.write_text(self.entry.read_text().replace(old, new, 1))

    def test_minimal_entry_and_mathsf_are_valid(self) -> None:
        result = self.validate()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("0 errors", result.stdout)
        self.assertIn("Missing conditional section", result.stdout)

    def test_broken_embedded_wikilink_is_rejected(self) -> None:
        self.replace("![[Evidence]]", "![[Missing Embedded Note]]")
        result = self.validate()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("Broken wikilink target", result.stdout)

    def test_unresolved_lowercase_placeholder_is_rejected(self) -> None:
        self.replace("Pinned source.", "Pinned source for <term>.")
        result = self.validate()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("project-template placeholders", result.stdout)

    def test_invalid_snapshot_metadata_is_rejected(self) -> None:
        cases = {
            "repository_remote: ssh://git@example.com/org/demo.git": "repository_remote: not-a-remote",
            "repository_branch: main": "repository_branch: bad branch",
            f"repository_commit_date: {self.commit_date}": "repository_commit_date: yesterday",
            "repository_worktree: clean": "repository_worktree: maybe",
        }
        for old, new in cases.items():
            with self.subTest(new=new):
                self.entry.write_text(self.valid_entry().replace(old, new, 1))
                result = self.validate()
                self.assertNotEqual(0, result.returncode, result.stdout)

    def test_commit_date_must_match_recorded_commit(self) -> None:
        self.replace(
            f"repository_commit_date: {self.commit_date}",
            "repository_commit_date: 2000-01-01T00:00:00+00:00",
        )
        result = self.validate()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("does not match commit date", result.stdout)


if __name__ == "__main__":
    unittest.main()
