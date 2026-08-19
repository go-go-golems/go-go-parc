---
title: "PROJECT REPORT - Triage of Uncommitted Files in the go-go-parc Vault - Deriving Ignore Policy from Commit History"
aliases:
  - go-go-parc uncommitted files triage
  - vault gitignore policy from commit history
  - transcript zip archive dedup triage
  - generated pdf docx deletion with md source
status: active
type: article
created: 2026-08-19
repo: /home/manuel/code/wesen/go-go-golems/go-go-parc
tags:
  - article
  - project-report
  - git
  - gitignore
  - obsidian
  - vault
  - transcripts
  - triage
---

# Triage of Uncommitted Files in the go-go-parc Vault

A repository with hundreds of untracked files presents a classification problem, not a storage problem. Each untracked file must be assigned to one of three outcomes: commit it to history, ignore it forever, or delete it from the working tree. The wrong assignment is costly in different directions. A file committed that should have been ignored enlarges history with data that no one can recover from a clone. A file ignored that should have been committed leaves a gap in the record that the next contributor will not notice until they need the file. A file deleted that should have been committed is gone. The decision for each file is independent, but the criteria are not: they are derived from what the repository already does, not from what an operator thinks it should do.

This report documents the triage of 783 untracked files in the `go-go-parc` Obsidian vault and the three-commit change that resolved them. The method is the contribution: the vault's existing commit history is treated as the specification, and the policy for new files is inferred by comparing what the repository already tracks against what it leaves untracked, grouped by file class. The work removed 122 generated documents from the working tree (103 MB), gitignored 165 packaging and build artifacts (228 MB), and committed 490 files (262 MB) that match the vault's established content pattern. The report states the classification rules, the evidence for each rule, and the validation that confirmed no rule leaked the wrong class of file into history.

> [!summary]
> - 783 untracked files were classified into three outcomes: 490 committed (config plus transcript output files), 165 gitignored (zip and tar.gz bundles, wheels, firmware blobs), and 122 deleted from disk (generated PDFs and docx that had a `.md` source sibling).
> - The ignore policy was derived from the repository's existing commit history: `git ls-tree -r --name-only HEAD` counts showed that 5 of 159 transcript zips were ever committed, and 0 tar.gz, wheel, ELF, or kernel Image files were ever committed. The established practice is the spec.
> - Generated documents with a markdown source were deleted rather than ignored, because ignoring leaves dead files on disk that a future archive run will re-import; deletion breaks the cycle.
> - 6 OOXML `.docx` files were misdetected as `application/octet-stream` by libmagic and would have been missed by a naive extension filter; MIME classification was backed by a content sniff (`file -b`) before deletion.
> - Git's content-addressed object store means the 169 byte-identical duplicate images among the staged files share one blob each, so the duplicates cost working-tree disk but add approximately zero bytes to repository history.
> - The change landed as three commits (`ee663ce`, `69b1349`, `ee73c3a`) and pushed to `origin/main`; no ignored directory, archive, or firmware blob entered any commit.

## 1. The classification problem

A vault is a git repository that holds an Obsidian knowledge base alongside its generated tooling. The `go-go-parc` vault has two kinds of content mixed in one tree: hand-authored notes (`Projects/`, `Research/`, `Logs/`, `Tickets/`, `ttmp/`) and imported ChatGPT transcripts (`Transcripts/`). The transcript import is automated by the `chatgpt-transcript-archiving` skill, which downloads a day's conversations and their code-interpreter output files with `surf-go`, writes them to `Transcripts/YYYY/MM/DD/`, and ends with `git add Transcripts/` followed by a commit. The import is unattended, so the boundary between what it should and should not commit is not enforced by the skill. It is enforced, when it is enforced at all, by a human triage after the fact.

The starting state was 783 untracked files plus one modified tracked file. The untracked files were not homogeneous. They fell into classes that require different outcomes:

| Class | Example paths | Count | First instinct |
|---|---|---|---|
| Local agent shims | `.claude/skills`, `.codex/skills` | 2 | Ignore (symlinks) |
| Generated tooling | `.pi/npm/`, `.ruff_cache/` | 2 trees | Ignore |
| Obsidian trash | `.trash/` | 1 tree | Ignore |
| Project config | `.pi/settings.json`, `.ttmp.yaml` | 2 | Commit |
| Modified skill | `.pi/skills/concept-study-slips/SKILL.md` | 1 | Commit |
| Transcript output | `Transcripts/2026/07/…`, `Transcripts/2026/08/…` | 771 | Commit some, ignore some, delete some |

The first instinct is not a decision. A symlink that is local to one machine must not be committed, but a config file that documents the project must. A transcript zip bundle that duplicates files already committed uncompressed must not be committed, but a reference PDF that has no source must. The classification requires evidence per class, and the evidence is the repository itself.

## 2. Deriving policy from commit history

The repository's existing tracked content is the only authoritative statement of what belongs in the vault. A README can describe intent, but the commit history records what actually happened. The method is to compare the tracked set against the untracked set, grouped by file class, and to read the disparity as a policy.

The query that establishes the policy for a class is `git ls-tree -r --name-only HEAD` filtered by extension. For transcript archives, the result was decisive:

```text
$ git ls-tree -r --name-only HEAD -- Transcripts/ | grep -ciE '\.zip$'
5
$ git ls-files --others --exclude-standard Transcripts/ | grep -ciE '\.zip$'
159
```

Five zips committed against 159 untracked. The repository has had 159 opportunities to commit a transcript zip and took five of them. The rate is not a preference; it is a refusal. The same query for other archive and build classes returned a stronger result:

| Class | Tracked in HEAD | Untracked | Inferred policy |
|---|---|---|---|
| `*.zip` (transcript bundles) | 5 | 159 | Ignore |
| `*.tar.gz` | 0 | 2 | Ignore |
| `*.whl` (Python wheels) | 0 | 1 | Ignore |
| `*.elf` (firmware) | 0 | 1 | Ignore |
| `*.Image` (kernel boot) | 0 | 1 | Ignore |
| `*.png` (transcript images) | 114 | 144 | Commit |
| `*.md` (transcripts) | 356 | 2 | Commit |
| `*.pdf` (transcripts) | 10 | 124 | Commit selectively |

The archive classes have a tracked count of zero or near-zero. The content classes have a tracked count in the hundreds. The policy reads off the table: commit what the repository already commits in bulk, ignore what the repository already refuses in bulk. The selective case is the PDF, which the repository commits sometimes; that case requires a finer rule, developed in section 5.

This method has a property that a policy written from intent does not have: it is self-correcting. If the repository's practice changes, the query returns a different ratio and the inferred policy changes with it. A policy written in a README is a statement made once; a policy derived from `git ls-tree` is a statement re-derived every time the triage runs.

## 3. Local tooling and generated trees

Five untracked paths were not transcript content and not project config. They were artifacts of the tools that operate on the vault, created locally and regenerated on demand.

```text
.claude/skills   -> ../.pi/skills   (symlink, agent harness)
.codex/skills    -> ../.pi/skills   (symlink, agent harness)
.pi/npm/         (pi extension node_modules, .gitignore inside)
.ruff_cache/     (ruff linter cache, .gitignore inside)
.trash/          (Obsidian trash bin)
```

Two of these already contained a `.gitignore` that ignored their own contents, which is a signal from the tool that generated them. The signal is correct but insufficient: a directory that ignores its contents still appears as an untracked directory in `git status`, which is noise on every status check. Ignoring the directory at the repository root removes the noise. The rules added to `.gitignore`:

```gitignore
# Local agent-harness shims: auto-created symlinks (.claude/skills, .codex/skills)
# pointing at ../.pi/skills. Machine-local, not vault content.
.claude/
.codex/

# Generated pi extension/skill node_modules, managed by pi and regenerated locally.
.pi/npm/

# Obsidian trash bin.
.trash/

# ruff Python linter cache.
.ruff_cache/
```

A check confirmed that no file under any of these paths was tracked before the rule was added:

```text
$ for d in .claude .codex .trash .pi/npm; do echo "$d: $(git ls-files "$d" | wc -l) tracked"; done
.claude: 0 tracked
.codex: 0 tracked
.trash: 0 tracked
.pi/npm: 0 tracked
```

Zero tracked files is the precondition for adding an ignore rule. Ignoring a path that already has tracked files does not remove them from history, but it makes their status confusing to reason about. The check is cheap and prevents that class of mistake.

## 4. Archive bundles and the duplication they encode

The 159 transcript zips are the largest ignored class by volume. The decision to ignore them rests on two facts. The first is the commit-history ratio from section 2. The second is what the zips contain, which determines why the ratio is what it is.

A transcript import writes the conversation's output files uncompressed into a per-conversation folder, then writes a zip bundle that packages the same files. The bundle is a convenience for download, not a source of truth. The evidence is the zip's contents read against its directory siblings:

```text
$ unzip -l "Transcripts/2026/08/08/JS API for CNC CAM/cnc-cam-ir-code.zip" | head -12
Archive:  Transcripts/.../cnc-cam-ir-code.zip
  Length      Date    Time    Name
---------  ---------- -----  ----
     3184  2026-08-08 07:40   artifacts/generated/badge.nc
     1742  2026-08-08 07:40   artifacts/generated/probing.ir.json
    21754  2026-08-08 07:40   artifacts/generated/badge.ir.json
      360  2026-08-08 07:40   artifacts/generated/probing.nc
      571  2026-08-08 07:40   artifacts/generated/badge-summary.json

$ ls "Transcripts/2026/08/08/JS API for CNC CAM/" | grep -vE '\.zip$'
badge.ir.json        badge.nc        probing.ir.json        probing.nc
```

The zip's `badge.nc` is the directory's `badge.nc`. Committing both stores the same bytes under two paths. The ignore rule covers the plain zip, the surf-go hash-suffixed dedup variant (`*.zip-<8hex>`), and the checksum sidecars that verify ignored zips:

```gitignore
Transcripts/**/*.zip
Transcripts/**/*.zip-*
Transcripts/**/*.zip.sha256
Transcripts/**/*.zip-*.sha256
```

The hash-suffixed variant requires its own rule because the suffix defeats a plain `*.zip` match. surf-go appends an 8-hex-character content hash to filenames when it deduplicates across import runs, producing names like `pbui.zip-788138fd` and `rag-ttc(2).zip-4b485865`. The pattern `*.zip-*` matches the suffix without matching real `.zip.sha256` sidecars, which the separate `*.zip.sha256` rule covers. Five `.zip.sha256` files were staged before the sidecar rule was added; each verified a now-ignored zip, so each was orphaned by the zip rule. The sidecar rule retired them.

Two other archive classes followed the same reasoning. The transcript history held zero `.tar.gz` files and zero `.whl` files:

```text
$ git ls-tree -r --name-only HEAD -- Transcripts/ | grep -ciE '\.tar\.gz$'
0
$ git ls-tree -r --name-only HEAD -- Transcripts/ | grep -ciE '\.whl$'
0
```

The two tarballs (`pbui-lean-mock.tar.gz`, `gojamacro.tar.gz`) and the wheel (`dag_agent_sync-0.1.0-py3-none-any.whl`) are build bundles. Their contents are not duplicated uncompressed alongside them, but they are packaging artifacts whose source lives in code repositories outside the vault. The vault's role is to record the conversation that produced them, not to mirror the build output. The rule:

```gitignore
Transcripts/**/*.tar.gz
Transcripts/**/*.whl
```

These three files total 90 KB. The volume is not the reason for the rule. The reason is consistency: the vault commits transcript output, not build packaging, and the commit history says so without exception.

## 5. Generated documents and the delete decision

Transcript imports produce rendered documents in two formats: a `.md` source and a rendered `.pdf` or `.docx`. The `.md` is the source the import writes; the rendered file is a convenience export. When both are present, the rendered file is regenerable from the source by a single command. Committing both stores the source and a derivative of the source under two paths. The vault's commit history shows that the repository commits rendered PDFs sometimes, which means the rule is not "ignore all PDFs." The rule is "delete the rendered file when its source is present, and commit the rendered file when its source is absent."

The distinction matters because a rendered file without a source is a primary document. A textbook PDF uploaded as a reference (`Polygon Mesh Processing (Botsch et al.).pdf-066d8286`, 23 MB) has no `.md` source in the vault; it is the only form of that content the vault holds. A type specimen PDF (`DATALAB-Type-Specimen-Clean-v2.pdf`) is a designed artifact with no text source. These are committed. A thesis PDF that sits next to `The_Semantics_and_Dynamics_of_RAG.md` (316 KB) is a render of that markdown; it is deleted.

The test that assigns each rendered file to an outcome is the presence of a `.md` sibling with the same basename:

```text
PDF: theory_of_erp_system_ontologies.pdf  (480218 bytes)
 MD: theory_of_erp_system_ontologies.md  (266429 bytes, 6903 lines)
 -> DELETE the PDF; the .md is the source.
```

A file with a sibling smaller than 200 bytes would fail the test, on the assumption that an empty or stub `.md` is not a real source. No file failed the test. The deletion was performed with `git rm -f` after staging, which removes the file from both the index and the working tree:

```text
deleted: 100  (PDFs with .md sibling, 78.9 MB)
deleted:  18  (docx with .md sibling, 24.1 MB)
kept:     24  (PDFs with no .md sibling, 38.8 MB)
kept:      1  (docx with no .md sibling, 1.6 MB)
```

Deletion is the correct outcome, not ignoring, for a reason that follows from the import loop. The import skill re-downloads a day's conversations when invoked. An ignored rendered file remains on disk; the next import run sees the file already present and skips it, but the file stays in the working tree as dead weight that `git status` will never report because it is ignored. Ignoring a generated file hides it; deleting it removes it. For a file that a future import will regenerate, the correct outcome is to delete it so that the next import either re-creates it (and the triage deletes it again) or does not (and the file is gone). The cycle is stable only if the file is deleted, not if it is ignored.

## 6. The MIME detection pitfall

The docx count in section 5 is 18 deleted plus 1 kept. The count almost became 12 deleted, because six `.docx` files were misclassified by their MIME type. The classification pipeline used `file -b --mime-type` to separate text from binary before checking for `.md` siblings. The OOXML docx format is a zip container, and libmagic reports it by content sniff. Six of the docx files in this batch were reported as `application/octet-stream` rather than `application/vnd.openxmlformats-officedocument.wordprocessingml.document`:

```text
$ file -b --mime-type "Transcripts/2026/08/09/Designing RAG Abstractions/The_Semantics_and_Dynamics_of_RAG.docx"
application/octet-stream

$ file -b "Transcripts/2026/08/09/Designing RAG Abstractions/The_Semantics_and_Dynamics_of_RAG.docx"
Microsoft OOXML
```

The `--mime-type` output is `application/octet-stream`; the plain `file -b` output is `Microsoft OOXML`. A classifier that trusted the MIME type alone would see `octet-stream` and treat the file as an unknown binary, not a docx, and would not check for a `.md` sibling. The six files would have been committed as 6.8 MB of generated content that duplicates a markdown source already in the same folder.

The fix is to back the MIME classification with a content sniff. A file is a docx when its MIME type is the OOXML type, or when its MIME type is `octet-stream` and its `file -b` description contains `Microsoft OOXML`. The same `.md`-sibling test then applies, and the six files were deleted with the rest. The general lesson is that MIME type alone is not a reliable classifier for container formats; the content description is the ground truth, and the MIME type is a hint that can be wrong in either direction.

## 7. Firmware blobs and the build-bundle folder

The `Raw metal firmware Rabbit R1/` folder held six files: two built firmware blobs, one zip, and three text sidecars. The blobs are the build output of a bare-metal bring-up for the Rabbit r1:

```text
r1bm-0.1.0.Image    9171 B    ARM64 kernel boot image
r1bm-0.1.0.elf      78480 B   ELF 64-bit LSB executable, ARM aarch64
rabbit-r1-baremetal-0.1.0.zip  48200 B   build bundle
r1bm-0.1.0.map      10684 B   linker map (text)
r1bm-0.1.0-build-report.txt   2161 B   build report (text)
rabbit-r1-baremetal-0.1.0-SHA256SUMS  485 B   checksums (text)
```

The commit history held zero `.elf` and zero `.Image` files. The blobs are built artifacts; the source that produced them is a code repository outside the vault. The first decision was to unstage the two blobs and ignore them by extension, matching the archive rule. The text sidecars were initially kept on the grounds that they are build metadata, not blobs.

The second decision reconsidered the sidecars. The SHA256SUMS file references only the now-ignored artifacts:

```text
$ cat rabbit-r1-baremetal-0.1.0-SHA256SUMS
4e6427...  /mnt/data/rabbit-r1-baremetal-0.1.0.zip
fc694d...  /mnt/data/r1bm-0.1.0.Image
08f6f8...  /mnt/data/r1bm-0.1.0.elf
7a167a...  /mnt/data/r1bm-0.1.0.map
93cd76...  /mnt/data/r1bm-0.1.0-build-report.txt
```

The checksums verify files that the vault no longer versions. The build report and the map describe a build whose output the vault does not hold. A folder in which every file is a sidecar for an ignored artifact has no vault content. The third decision ignored the folder as a whole rather than enumerating its files:

```gitignore
Transcripts/**/*.elf
Transcripts/**/*.Image
Transcripts/**/Raw metal firmware Rabbit R1/
```

The folder-level rule is preferred over the file-level enumeration for a reason of maintenance. The next build bundle dropped into that folder will hold a different version (`r1bm-0.2.0.elf`, a different map, a different report). A rule that enumerated the current filenames would miss the next version. A rule that names the folder ignores every file the folder will ever hold. The extension rules for `.elf` and `.Image` remain because a future build bundle may land in a differently named folder, and the extension is the invariant across folder names.

## 8. Duplicate content and the object store

Among the 490 files staged for commit, 169 were byte-identical copies of other staged files, across 103 content groups. The largest single group was four copies of one 1.33 MB image, wasted 3.99 MB of working-tree space. The total wasted working-tree space from duplicates was 98.7 MB. The total repository-history cost of those duplicates was approximately zero.

Git stores file content as blobs keyed by the SHA-1 hash of the content. Two files with identical content produce the same blob. The commit records a tree that maps both paths to the same blob hash. The blob is written to the object store once. The 169 redundant copies add 169 tree entries that reference already-stored blobs; they add no blob data. The 98.7 MB of "wasted" space is working-tree disk, which was already spent when the import wrote the files. The push transfers each unique blob once.

This property is the reason the duplicate images were committed rather than deduplicated. A deduplication pass that deleted redundant copies from the working tree would reduce working-tree disk by 98.7 MB but would change which path holds each image. The transcripts reference images by their original filenames; the surf-go hash suffix in each filename is the deduplication key the import tool already uses. Removing one copy of two identical files breaks the reference in the transcript that points at the removed copy. The cost of keeping both copies is one tree entry per duplicate, which is negligible. The cost of removing one is a broken reference, which is not. The correct outcome is to commit the duplicates and let the object store deduplicate at the blob layer, which is the layer where deduplication is free.

The check that confirmed the storage cost is a content hash of every staged file:

```text
staged paths:        490
unique-content groups: 321
groups with duplicates: 103
redundant copies:    169
WASTED from duplicates (working tree): 98.7 MB
=> duplicates add ~0 to repo history; only the 321 unique blobs get stored
```

The 490 files commit as 321 unique blobs. The 169 duplicates are 169 tree entries pointing at blobs already in the set.

## 9. The commit structure

The triage landed as three commits, ordered so that the ignore rule precedes the content it governs. If the content commit were first, the ignored files would be untracked for one commit and the ignore commit would not prevent them from being added by a careless `git add Transcripts/` in between. The ignore commit first makes the rule active before any content is staged.

| Commit | Subject | Files | Insertions |
|---|---|---|---|
| `ee663ce` | `chore: ignore local agent/tooling artifacts, transcript zip/tar.gz/whl bundles and firmware build blobs` | 1 | +41 |
| `69b1349` | `chore: track pi + docmgr project config; quote concept-study-slips frontmatter` | 3 | +12 −1 |
| `ee73c3a` | `docs: archive ChatGPT transcripts and output files (2026-07/08 batches)` | 486 | +120187 |

The first commit is the `.gitignore` alone. The 41 added lines are the five ignore rules with their justifying comments. Committing the ignore rule by itself makes the policy auditable in one diff: a reviewer reads one file and sees every class of file the vault refuses, with the reason inline.

The second commit is the project config: `.pi/settings.json` (the pi package list, pairing with the already-tracked `.pi/pinned-skills.json`), `.ttmp.yaml` (the docmgr root config pointing at the tracked `ttmp/` workspace), and the one-line frontmatter fix to `concept-study-slips/SKILL.md` that quotes the YAML `description` value because it contains an em-dash. Config is separated from content because a future bisect that looks for a content change should not land on a config commit, and a future reader who wants the vault's tooling configuration should find it in one commit, not spread across a content commit.

The third commit is the 486 transcript files. The commit message states what is included and, by reference to the first commit, what is excluded. The 120187 insertions are the transcript markdown and output files; the binaries are stored as blobs and do not contribute line insertions to the diffstat.

## 10. Validation

Each ignore rule was checked after it was added, before any content was staged against it. The check is `git check-ignore <path>`, which reports whether a path matches an ignore rule and which rule matched:

```text
$ git check-ignore .claude/skills && echo IGNORED
IGNORED
$ git check-ignore "Transcripts/.../cnc-cam-ir-code.zip" && echo IGNORED
IGNORED
$ git check-ignore "Transcripts/.../r1bm-0.1.0.elf" && echo IGNORED
IGNORED
```

After staging, a negative check confirmed that no ignored class leaked into the commit. The check is a `grep` of the staged file list for each ignored pattern, expecting no matches:

```text
local tooling dirs staged: none (good)
archives (zip/tar.gz/whl) staged: none (good)
firmware blobs staged: none (good)
firmware folder staged: none (good)
```

A final check confirmed the working tree had no untracked-and-unignored files remaining:

```text
$ git status --porcelain | grep -c '^??'
0
```

A count of zero means every file in the working tree is either tracked, staged, or ignored. There is no fourth state. A zero result is the only state in which the triage is complete; a non-zero result is a file the classification missed.

The deletions were verified by a separate check. A `git rm -f` removes a file from the index and the working tree. The verification is a stat of each deleted path, expecting absence:

```text
confirmed gone from disk: 100 / 100   (PDFs)
confirmed gone from disk: 18 / 18     (docx)
```

A deletion that left the file on disk would mean `git rm` failed silently, which it does not, but the check is cheap and the cost of a wrong deletion is high.

## 11. Decisions, constraints, and remaining work

| Decision | Result | Rationale |
|---|---|---|
| Derive ignore policy from `git ls-tree HEAD` counts | Applied | The commit history is the only authoritative record of what the vault commits. Intent in a README can drift; counts cannot. |
| Delete generated docs with a `.md` sibling | Applied | Ignoring leaves dead files on disk that re-import keeps; deletion breaks the cycle. The `.md` is the source. |
| Keep generated docs with no `.md` sibling | Applied | A rendered file with no source is a primary document. Deleting it loses content the vault holds in no other form. |
| Ignore zip, tar.gz, whl, elf, Image by extension | Applied | Commit history holds zero or near-zero of each. The extension is the invariant across folder names. |
| Ignore the `Raw metal firmware Rabbit R1/` folder | Applied | Every file in it is a sidecar for an ignored artifact. Folder-level rules survive version changes that file-level rules miss. |
| Commit duplicate images without deduplication | Applied | The object store deduplicates at the blob layer. Working-tree deduplication breaks transcript references for no storage gain. |
| Commit the ignore rule before the content | Applied | The rule is active before any content is staged, preventing a careless `git add` from adding the wrong class. |
| Back MIME classification with a content sniff | Applied | libmagic reports 6 OOXML docx as `octet-stream`. The `file -b` description is ground truth; the MIME type is a hint. |
| Add a pre-commit guard for generated docs | Not implemented | The delete rule is applied at triage time, not enforced at commit time. A future import can re-add a generated PDF that the triage must then delete again. |

The following work remains if the triage policy is to be enforced rather than re-applied.

1. **Enforce the generated-doc rule at import time.** The `chatgpt-transcript-archiving` skill ends with `git add Transcripts/`. A pre-commit hook or a skill step that deletes any `.pdf` or `.docx` with a `.md` sibling before the `git add` would make the triage automatic. The rule is currently applied by a human after the import.
2. **Add a pre-commit check for ignored extensions.** A hook that rejects any staged `.zip`, `.tar.gz`, `.whl`, `.elf`, or `.Image` under `Transcripts/` would prevent a future careless `git add` from committing a build artifact. The ignore rules prevent untracked files from appearing in `git status`; a pre-commit check would prevent a staged file from entering a commit.
3. **Record the policy in the vault.** The `.gitignore` comments state the rules and their reasons. A short note in the vault's project documentation that points at the `.gitignore` as the policy source would make the policy discoverable by a contributor who does not read gitignore files by habit.

## Key points to retain

- A repository's commit history is the specification of what belongs in it. The policy for a new file is inferred by comparing the tracked set against the untracked set grouped by class, not by reasoning from intent.
- The ignore decision and the delete decision apply to different classes. Packaging and build artifacts are ignored because they are regenerated by tools; generated documents with a source are deleted because ignoring leaves dead files that the next import cycle preserves.
- A rendered document is committed when it has no source sibling and deleted when it does. The presence of a `.md` with the same basename is the test. A rendered file with no source is a primary document.
- libmagic misclassifies container formats. A MIME type of `application/octet-stream` does not exclude a file from being an OOXML docx. The content description from `file -b` is the ground truth.
- Git's object store deduplicates by content hash. Byte-identical files share a blob. Working-tree duplicates cost disk, not history. Deduplicating at the working tree breaks references for no storage gain.
- An ignore rule is committed before the content it governs so that the rule is active before any content is staged. The order prevents a careless `git add` from adding the class the rule is meant to exclude.
- The triage is complete when `git status --porcelain | grep -c '^??'` returns zero. Every file is tracked, staged, or ignored. A non-zero result is a missed classification, not a tolerated state.

## Evidence and implementation references

- Repository: `/home/manuel/code/wesen/go-go-golems/go-go-parc` (Obsidian vault, `origin/main` at `github.com/go-go-golems/go-go-parc`)
- Triage commits: `ee663ce` (ignore rules), `69b1349` (config), `ee73c3a` (transcript content, 486 files)
- Policy source: `.gitignore` at the repository root (51 lines after the change)
- Commit-history queries: `git ls-tree -r --name-only HEAD -- Transcripts/` filtered by extension
- Deletion tool: `git rm -f <path>` after staging, removing from index and working tree
- MIME classification: `file -b --mime-type <path>` backed by `file -b <path>` for container formats
- Import skill: `chatgpt-transcript-archiving` (`/home/manuel/.pi/agent/skills/chatgpt-transcript-archiving/SKILL.md`), which ends with `git add Transcripts/` and a commit
- Surf-go dedup: 8-hex-character content-hash suffix appended to filenames (`*.zip-<hash>`, `*.png-<hash>`, `*.pdf-<hash>`)
- Precedent report: `Projects/2026/08/16/PROJECT REPORT - Laptop Media Backup and Retention Isolation - Freeing 42G With a Tag-Scoped Restic Snapshot.md`

## Related notes

- [[PROJECT REPORT - Laptop Media Backup and Retention Isolation - Freeing 42G With a Tag-Scoped Restic Snapshot]] — the format and style precedent for this report, a triage of restic snapshots that applies the same method of deriving policy from the existing state of the system.
