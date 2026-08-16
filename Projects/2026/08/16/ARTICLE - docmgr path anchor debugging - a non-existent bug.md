---
title: "ARTICLE: Debugging docmgr Path Anchors — A Controlled Reproduction of a Non-Existent Bug"
aliases:
  - docmgr path anchor debugging
  - docmgr abs repo anchor ordeal
tags:
  - article
  - debugging
  - docmgr
  - go
  - epistemology
  - path-resolution
  - frontmatter
status: active
type: article
created: 2026-08-16
repo: /home/manuel/code/wesen/go-go-golems/docmgr
---

# ARTICLE: Debugging docmgr Path Anchors — A Controlled Reproduction of a Non-Existent Bug

This article records a debugging investigation into `docmgr`'s path-anchoring system and the failure of an investigation methodology. The triggering incident was a `docmgr doctor` report that flagged freshly related source files as `missing_related_file`, while the same files provably existed on disk. The investigation produced a confident hypothesis — that `doc relate` and `docmgr doctor` were inconsistent in how they resolved absolute paths — and then produced a clean reproduction that disproved the hypothesis entirely. The bug did not exist. The warnings were stale state produced by the investigator's own failed `--remove-files` calls.

The article exists because the failure mode is general. An investigator who forms a hypothesis from contaminated state, and who does not perform a clean reproduction before concluding, will report non-existent bugs and waste maintainers' time. The docmgr source paths cited here are verifiable against `internal/paths/anchored.go`, `internal/paths/resolver.go`, and `pkg/commands/doctor.go` in the docmgr repository.

> [!summary]
> - docmgr anchors related-file paths with explicit schemes: `repo://`, `ws://`, `docs://`, `doc://`, and `abs://`. The write side (`relate`) chooses the tightest containing anchor; the read side (`doctor`) resolves each scheme to an absolute path and calls `os.Stat`.
> - The `abs://` scheme is not a broken fallback. Doctor resolves `abs://` directly against the filesystem and finds files outside the repository root. An in-repo `abs://` entry and an out-of-repo `abs://` entry both pass `doctor` when the file exists.
> - The reported "bug" was stale duplicate frontmatter. The investigator's `--remove-files` calls silently no-op'd because the target strings did not match the stored form, leaving duplicate entries that were never cleaned up.
> - The actionable output of this report is the **improvement spec**: a gap-to-fix mapping and proposed replacement text for the docmgr skill, `--remove-files` output, the `doctor` message, and a new `--replace-files` command, so the next investigator does not fall into the same hole.

## Why this note exists

This note preserves a reusable debugging lesson, not a project changelog. The triggering project was a scroll-restoration architecture review (`PV-SCROLL-REVIEW-025`) that related external source files to a design document. When `docmgr doctor` reported those files missing, the investigation expanded into docmgr's path-resolution internals. The lesson generalizes: it applies to any investigation of a system whose state is mutated by the investigator's own commands.

## The docmgr path-anchor system

docmgr stores related files in YAML frontmatter under a `RelatedFiles` key. Each entry has a `Path` and a `Note`. The `Path` is an anchored string that makes the path's base directory explicit, rather than leaving a reader to guess whether a bare string is repository-relative, document-relative, or absolute.

The schemes, defined in `internal/paths/anchored.go`:

| Scheme | Meaning | Base |
|---|---|---|
| `repo://pkg/foo.go` | Relative to the repository root | `r.repoRoot` |
| `ws://glazed/pkg/fields.go` | Relative to a `go.work` workspace member | `r.wsRoot` + member |
| `docs://2026/07/05/T/design/01.md` | Relative to the docs root (`ttmp`) | `r.docsRoot` |
| `doc://../reference/01-diary.md` | Relative to the referencing doc's directory | `r.docDir` |
| `abs:///home/user/x.go` | Absolute path, the escape hatch | the path itself |

Two operations matter for this investigation. The **write side** is `doc relate`, which takes a path (absolute or otherwise) and stamps the tightest containing anchor onto it before persisting it to frontmatter. The **read side** is `docmgr doctor`, which resolves each stored `Path` back to an absolute path and checks `os.Stat` to confirm the file exists.

### The write side: `AnchoredFor`

`doc relate` calls `anchoredForWrite` in `pkg/commands/relate.go`, which resolves the input to an absolute path and then calls `Resolver.AnchoredFor`. `AnchoredFor` chooses the anchor by containment, in precedence order, defined at `internal/paths/anchored.go:131`:

```go
func (r *Resolver) AnchoredFor(absPath string) AnchoredPath {
    absPath = filepath.Clean(strings.TrimSpace(absPath))
    if absPath == "" || !filepath.IsAbs(absPath) {
        return AnchoredPath{Scheme: SchemeLegacy, Rel: filepath.ToSlash(absPath)}
    }
    if rel := relativeWithin(absPath, r.repoRoot); rel != "" && rel != "." {
        return AnchoredPath{Scheme: SchemeRepo, Rel: rel}
    }
    if r.wsRoot != "" {
        if rel := relativeWithin(absPath, r.wsRoot); rel != "" && rel != "." {
            // ... ws://
        }
    }
    if rel := relativeWithin(absPath, r.docsRoot); rel != "" && rel != "." {
        return AnchoredPath{Scheme: SchemeDocs, Rel: rel}
    }
    return AnchoredPath{Scheme: SchemeAbs, Rel: filepath.ToSlash(absPath)}
}
```

`relativeWithin(target, base)` returns the target path relative to `base` if the target is inside `base`, and the empty string otherwise (it returns empty when `filepath.Rel` errors or when the result begins with `..`). The precedence is strict: a file inside the repository root becomes `repo://`, a file inside the docs root (but not the repo root) becomes `docs://`, and only a file outside all known roots becomes `abs://`.

### The read side: `doctor`

`docmgr doctor` iterates each document's `RelatedFiles` and, for each entry, calls `resolver.Resolve(rf.Path)` and checks the `Exists` field. The relevant code is at `pkg/commands/doctor.go:808`:

```go
for _, rf := range doc.RelatedFiles {
    if strings.TrimSpace(rf.Path) == "" {
        continue
    }
    // ...
    n := resolver.Resolve(rf.Path)
    if !n.Exists {
        if err := emit("missing_related_file", "warning",
            fmt.Sprintf("related file not found: %s", rf.Path), h.Path); err != nil {
            return err
        }
    }
}
```

`Resolve` dispatches to `resolveAnchored` for anchored strings. The anchor's base is resolved in `anchoredTarget` at `internal/paths/resolver.go:138`. The `abs://` branch is direct:

```go
case SchemeAbs:
    anchor = AnchorAbs
    absPath = filepath.Clean(filepath.FromSlash(a.Rel))
```

For `abs://`, `absPath` is taken directly from the payload, with no base joining. The result is then passed to `buildResult`, which calls `os.Stat(absPath)` to set `Exists`. There is no resolution relative to the document's directory. An `abs://` path is the absolute path itself.

## The symptom

During the scroll-restoration review, six external source files were saved into a ticket's `sources/` directory and related to a design document with `docmgr doc relate`. The files were passed as absolute paths, per the docmgr skill's guidance to prefer absolute paths in `--file-note`. The first `relate` calls produced frontmatter entries prefixed `abs://`:

```yaml
RelatedFiles:
    - Path: abs:///home/manuel/workspaces/.../sources/00-sources-index.md
      Note: Curated index mapping external patterns to review recommendations
```

`docmgr doctor` then reported:

```text
1) [warning] Missing related file entry
Doc: .../design-doc/01-scroll-restoration-architecture-and-pr-21-code-review.md
Related file: abs:///home/manuel/workspaces/.../sources/00-sources-index.md
Status: missing on disk
```

The file provably existed at that exact absolute path:

```text
$ ls -la /home/manuel/workspaces/.../sources/00-sources-index.md
-rw-rw-r-- 1 manuel manuel 9909 Aug 16 18:51 .../sources/00-sources-index.md
```

## The hypothesis (and why it was wrong)

The hypothesis was that `relate` and `doctor` were inconsistent for untracked files. The reasoning, in order:

1. `relate` had stored `abs://` for a file that was inside the repository root. By the `AnchoredFor` precedence, an in-repo file should have produced `repo://`.
2. The file was not git-tracked (`git ls-files --error-unmatch` failed). The hypothesis concluded that `relate` keyed "repo membership" off git tracking, fell back to `abs://` for untracked files, and that `doctor` could not resolve `abs://` against the filesystem root.
3. Therefore, relating any untracked file — including all freshly-created ticket documents — would always produce a doctor warning.

The reasoning was internally coherent and matched the observed symptom. It was also wrong, because the first premise was false. The file *was* inside the repository root, and `AnchoredFor` *did* check containment by path, not by git tracking. The `abs://` entries were not produced by `relate` at all in the state that was being inspected.

## The controlled reproduction

The decisive test was to wipe the frontmatter clean and run a single `relate` from a known state. The test was run from the repository root, so `os.Getwd()` returned the repository root and `FindRepositoryRoot` resolved to it.

```text
$ # wipe all source-related entries from frontmatter
$ # (python edit removing any RelatedFiles entry whose Path contains "sources/")

$ docmgr doc relate --doc "$DESIGN" \
    --file-note "/home/manuel/.../sources/tanstack-router-scroll-restoration.md:Confirms per-entry key pattern"
related 1 file(s) to ... (added 1, updated 0, removed 0)

$ grep 'sources/tanstack' "$DESIGN"
    - Path: repo://ttmp/2026/08/16/PV-SCROLL-REVIEW-025--.../sources/tanstack-router-scroll-restoration.md
```

The same absolute path that had previously produced `abs://` now produced `repo://`. `AnchoredFor` worked correctly: the file was inside the repository root, so it received the `repo://` anchor. The earlier `abs://` entries were stale.

The second test confirmed that `doctor` resolves genuine `abs://` paths correctly. A file was created outside the repository root, at `/tmp/pv-outside-test-file.md`, and related:

```text
$ docmgr doc relate --doc "$DESIGN" --file-note "/tmp/pv-outside-test-file.md:outside-repo test"
related 1 file(s) to ... (added 1, updated 0, removed 0)

$ grep 'outside-test' "$DESIGN"
    - Path: abs:///tmp/pv-outside-test-file.md

$ docmgr doctor --ticket PV-SCROLL-REVIEW-025 --stale-after 30
## Doctor Report (1 findings)
### PV-SCROLL-REVIEW-025
- ✅ All checks passed
```

A genuine `abs:///tmp/...` entry, for a file outside the repository, passed `doctor`. The `os.Stat` call in `buildResult` found the file. This refutes the hypothesis that `doctor` cannot resolve `abs://` paths.

After removing the outside-repo test entry and re-relating the remaining two source files with absolute paths, all entries became `repo://` and `doctor` passed cleanly:

```text
$ docmgr doctor --ticket PV-SCROLL-REVIEW-025 --stale-after 30
## Doctor Report (1 findings)
### PV-SCROLL-REVIEW-025
- ✅ All checks passed
```

The bug did not exist. The warnings were stale frontmatter.

## How the stale state was produced

The stale `abs://` entries were produced by the investigator's own `--remove-files` calls. During the attempt to fix the warnings, several `docmgr doc relate --remove-files <path>` commands were run with target strings that did not exactly match the stored form. The command reported success:

```text
$ docmgr doc relate --doc "$DESIGN" --remove-files "abs:///nonexistent/never/stored/this.md"
no related file changes for ... (remove targets were not present)
```

The message `no related file changes ... (remove targets were not present)` states that nothing was removed. The investigator treated this message as confirmation that the removal had succeeded, and concluded that the stale entries were a docmgr defect rather than the expected consequence of a no-op removal. The duplicate `abs://` entries persisted alongside newer `repo://` entries, and `doctor` continued to flag the duplicates as missing.

This is the actual chain:

1. First `relate` calls stored `abs://` entries (the reason for the original `abs://` form is not fully recoverable, but the entries were present in the inspected frontmatter).
2. Attempted `--remove-files` calls targeted strings that did not match the stored form and removed nothing.
3. Subsequent `relate` calls added `repo://` entries for the same files, without removing the `abs://` duplicates.
4. `doctor` flagged the `abs://` duplicates, which the investigator interpreted as a resolution defect.

## The genuine residual issue

One real, narrow issue remains. `doc relate --remove-files` returns success when no stored entry matches the target, with no warning. The output is `no related file changes for ... (remove targets were not present)`, which is accurate but easy to overlook when it appears among other successful operations. A user who runs a remove and does not read the parenthetical will believe the removal succeeded.

This is a UX papercut, not a correctness defect. The command does not corrupt state; it accurately reports that nothing changed. The fix would be to surface a warning or a non-zero exit when zero targets match, so that a no-op removal is not confusable with a successful removal. It does not warrant a bug report about path resolution.

## Working rules

The rules below are the reusable output of this investigation.

- **Reproduce from a clean state before concluding.** A hypothesis formed from state that the investigator's own commands mutated is not evidence. Wipe the state, run the operation once, and observe the result. The controlled reproduction in this case took two commands and disproved a hypothesis that had been argued for several turns.
- **Distinguish "the system produced this" from "the system has this."** The `abs://` entries were present in the frontmatter, but they were not produced by the `relate` call under inspection. Presence is not provenance. Before attributing a stored value to a command, confirm the command produced it by running it from a clean state.
- **Read the full output of a no-op command.** `no related file changes ... (remove targets were not present)` states that nothing was removed. A removal that reports "no changes" did not succeed; it did nothing. Treat the parenthetical as load-bearing.
- **The write side and the read side use the same resolver.** `relate` and `doctor` both construct their resolver from `ws.Context().RepoRoot`, `ws.Context().DocsRoot`, and the document path. A divergence between them is unlikely without a code path that constructs a resolver from different inputs. Verify the inputs before assuming a divergence.
- **`abs://` is not a broken fallback.** It is the documented escape hatch for files outside all known roots, and `doctor` resolves it directly with `os.Stat`. An `abs://` entry that points at an existing file passes `doctor`, whether the file is inside or outside the repository.
- **Containment is by path, not by git tracking.** `AnchoredFor` uses `relativeWithin`, which calls `filepath.Rel`. A file inside the repository root becomes `repo://` regardless of whether it is git-tracked. Git tracking is irrelevant to anchor selection.

## Pseudocode: the resolution chain

The full write-then-read chain for an absolute input path:

```text
# WRITE SIDE: doc relate --file-note "/abs/path:note"
absInput = "/abs/path"
normalized = resolver.Resolve(absInput)         # Normalize: abs input -> buildResult(absInput)
absPath = normalized.Abs                        # = absInput (cleaned)
anchor = resolver.AnchoredFor(absPath)          # containment check: repo -> ws -> docs -> abs
if relativeWithin(absPath, repoRoot) != "":
    stored = "repo://" + relativeWithin(absPath, repoRoot)
elif relativeWithin(absPath, docsRoot) != "":
    stored = "docs://" + relativeWithin(absPath, docsRoot)
else:
    stored = "abs://" + absPath
# persist {Path: stored, Note: note} into frontmatter

# READ SIDE: docmgr doctor
for each rf in doc.RelatedFiles:
    a = ParseAnchored(rf.Path)
    switch a.Scheme:
      case SchemeRepo: absPath = filepath.Join(repoRoot, a.Rel)
      case SchemeAbs:  absPath = a.Rel                       # direct, no base
      # ...
    exists = os.Stat(absPath) == nil
    if not exists:
        emit("missing_related_file", rf.Path)
```

The two sides are symmetric. The write side computes the anchor from the absolute path; the read side computes the absolute path from the anchor. A file inside the repository root round-trips: `absInput` → `repo://rel` → `filepath.Join(repoRoot, rel)` → the original absolute path. A file outside round-trips through `abs://`. The chain is correct.

## Anti-patterns

- **Concluding from contaminated state.** The investigator's own `--remove-files` no-ops had left duplicate entries in the frontmatter. Concluding that `doctor` was broken based on those duplicates is the central error. Clean the state, then observe.
- **Attributing stored values to the wrong command.** The `abs://` entries were present, but not produced by the `relate` call under inspection. Treating presence as provenance produced a false premise.
- **Confusing a no-op with a success.** The `--remove-files` output stated that nothing was removed. Reading only the leading `no related file changes` and ignoring the parenthetical `(remove targets were not present)` led to the belief that the removal had worked.
- **Reporting a bug without a clean reproduction.** The hypothesis was argued for multiple turns before a clean reproduction was attempted. The reproduction took two commands and disproved it. A reproduction is cheaper than a bug report and more authoritative than an argument.

## Documentation and skill improvement spec

The ordeal is evidence of gaps in three places: the docmgr command help and `doctor` output, the `docmgr` agent skill (`SKILL.md` and `references/docmgr.md`), and the diagnostic playbook. Each wrong turn in the investigation maps to one gap and one concrete fix. This section is the actionable output of the report; it is what should be edited into docmgr or its skills to prevent the next investigator from repeating the rabbit hole.

### Gap-to-fix mapping

| Wrong turn in the ordeal | Where the gap lives | Proposed fix |
|---|---|---|
| Concluded `abs://` was a bug without a clean reproduction | docmgr skill `doctor` section; no diagnostic playbook step | Add a "Diagnosing `missing_related_file`" checklist: (1) confirm the file exists at the stored path; (2) wipe the frontmatter entry and re-`relate` from clean state; (3) only then suspect a resolver defect. |
| Had no model of what `abs://` vs `repo://` means, so guessed "git tracking" | `docmgr` skill `SKILL.md:56` says "Prefer absolute paths" with no anchoring model | Add an "Anchoring model" subsection stating the precedence and the containment rule (see proposed text below). |
| Assumed repo membership is keyed off git tracking | nowhere stated | State in the anchoring model: containment is by filesystem path (`filepath.Rel`), not by git tracking; an untracked in-repo file still becomes `repo://`. |
| Misread `no related file changes ... (remove targets were not present)` as success | `doc relate --remove-files` command output | Surface a `WARNING: 0 of N targets matched` line and a non-zero exit when zero targets match, so a no-op is not confusable with a successful removal (see proposed output below). |
| Could not tell stale duplicate entry from resolver bug | `docmgr doctor` `missing_related_file` message | Include the resolved absolute path the checker `stat`'d: `related file not found: <stored> (resolved to <abs>, stat failed)` (see proposed message below). |
| Stale duplicate entries accumulated with no clean reset path | `doc relate` only removes by exact stored string | Add `doc relate --replace-files` (atomic replace of the listed notes) so users escape duplicates without hand-editing frontmatter. |
| Skill instruction "prefer absolute paths" given without the reason | `docmgr` skill `SKILL.md:56`, `references/docmgr.md:191,314` | Annotate the instruction with *why*: absolute paths let `AnchoredFor` pick the tightest anchor automatically; relative paths risk resolving against the wrong base. |

### Proposed skill text: the anchoring model

Add this to the `docmgr` skill (`SKILL.md`, near the `--file-note` conventions) so users can reason about stored paths instead of guessing:

```markdown
### How related-file paths are anchored

`doc relate` stores each related file with an explicit anchor that makes its
base directory unambiguous. The anchor is chosen by filesystem containment, in
this precedence order:

1. `repo://<rel>` — the file is inside the repository root
2. `ws://<member>/<rel>` — inside a `go.work` workspace member
3. `docs://<rel>` — inside the docs root (`ttmp`)
4. `abs://<abs>` — anywhere else (the escape hatch)

Containment is by filesystem path (`filepath.Rel`), **not** by git tracking. An
untracked file inside the repository root still becomes `repo://`. `abs://` is
not a broken fallback: `doctor` resolves it directly with `os.Stat`, so an
`abs://` entry pointing at an existing file passes `doctor`, inside or outside
the repo.

This is why the skill recommends absolute paths in `--file-note`: an absolute
path lets `AnchoredFor` pick the tightest anchor automatically. A relative
path risks being resolved against the wrong base.
```

### Proposed skill text: diagnosing `missing_related_file`

Add this to the skill's `doctor` / validation section so the default response to a `missing_related_file` warning is a clean reproduction, not a bug report:

```markdown
### Diagnosing `missing_related_file` before reporting a bug

A `missing_related_file` warning means `doctor` resolved a stored `Path` to an
absolute path and `os.Stat` failed. Before suspecting a resolver defect:

1. Confirm the file exists at the stored path. `ls -la` the path verbatim.
2. Check the stored anchor. If it is `abs://` and the file is inside the repo,
   the entry is likely stale — `relate` would normally produce `repo://` for an
   in-repo file.
3. Wipe the entry from frontmatter and re-`relate` from clean state. If the
   re-`relate` produces `repo://` and `doctor` passes, the warning was a stale
   entry, not a bug.
4. Only if a clean re-`relate` reproduces the warning should a resolver defect
   be suspected.
```

### Proposed command output: `doc relate --remove-files`

Current output when zero targets match:

```text
no related file changes for ... (remove targets were not present)
```

The parenthetical is load-bearing but easy to overlook. Proposed:

```text
WARNING: 0 of 1 remove target(s) matched stored entries; nothing removed.
        Stored forms may differ from the supplied strings. Use `doc list --ticket <id>`
        to inspect stored RelatedFiles paths before retrying.
exit code: 1
```

A non-zero exit makes the no-op visible to scripts and to an investigator scanning command output, without changing the success case.

### Proposed command output: `docmgr doctor` missing-related-file

Current message:

```text
related file not found: abs:///home/.../sources/00-sources-index.md
```

The message shows the stored path but not the absolute path the checker actually `stat`'d, so the reader cannot distinguish a stale entry from a resolution defect. Proposed:

```text
related file not found: abs:///home/.../sources/00-sources-index.md
        (resolved to /home/.../sources/00-sources-index.md, stat failed)
```

With the resolved path visible, a stale `abs://` entry pointing at an existing file is immediately suspicious — the reader sees `stat failed` next to a path they can `ls`, which points at stale-state rather than resolver logic.

### Proposed command: `doc relate --replace-files`

The investigation got trapped because `--remove-files` removed nothing and left duplicates. An atomic replace would avoid the trap entirely:

```text
docmgr doc relate --doc <doc> --replace-files \
  --file-note "path1:reason1" \
  --file-note "path2:reason2"
```

Semantics: the listed `--file-note` entries become the complete `RelatedFiles` set for the doc; any prior entries not in the list are removed. This gives users a single command to recover from duplicate or stale entries, instead of hand-editing frontmatter or relying on fragile exact-string removes.

### What this report does not propose

The report does not propose changing the anchoring algorithm, the resolver, or the precedence order. The write side and the read side are symmetric and correct. The fixes are all in the presentation layer: skill text that teaches the model, command output that distinguishes no-op from success, and a doctor message that exposes the resolved path. The rabbit hole was caused by missing models and misleading output, not by incorrect code.

## Related notes

- Source repository: `/home/manuel/code/wesen/go-go-golems/docmgr`
- Triggering ticket: `PV-SCROLL-REVIEW-025` in `/home/manuel/workspaces/2026-08-15/better-index-links/publish-vault/ttmp/2026/08/16/`
- docmgr source paths cited: `internal/paths/anchored.go:131`, `internal/paths/resolver.go:138`, `internal/paths/resolver.go:202`, `pkg/commands/doctor.go:808`, `pkg/commands/relate.go:699`
