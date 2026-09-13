---
title: "remarquee Sync Convert Failures: Transcript Math Delimiters and Export Fidelity"
aliases:
    - remarquee convert failures root cause
    - chatgpt transcript export fidelity
tags:
    - project
    - remarquee
    - surf-cli
    - pandoc
    - latex
    - transcripts
status: active
type: project
created: 2026-09-13
repo: /home/manuel/code/wesen/surf-cli
repo-secondary: /home/manuel/code/wesen/go-go-golems/remarquee
---

# remarquee Sync Convert Failures: Transcript Math Delimiters and Export Fidelity

On 2026-09-13, a `remarquee upload sync` of this vault planned 303 uploads and failed to convert 149 of them to PDF. The run took 26 minutes and ended with `Error: 149 file(s) failed during sync (convert=149, upload=0, delete=0)`. This report is the root-cause analysis of those failures. By the end of it you should understand the conversion pipeline well enough to predict, from a markdown file's content alone, whether it will convert; you should know which of the four failure classes a given file belongs to; and you should be able to evaluate the fix design that now lives in surf-cli ticket `SURF-20260913-EXPORTFIX` and GitHub issue [wesen/surf-cli#12](https://github.com/wesen/surf-cli/issues/12).

> [!summary]
> - The 149 failures reduce to four classes: math delimiter breakage (~100 files), never-downloaded sandbox assets, downloaded-but-unlinked asset references, and prose characters that collide with math syntax.
> - The transcript markdown in the vault is faithful to what ChatGPT produced. The corruption happens downstream, in the pandoc reader configuration and in two specific gaps of surf-cli's export pipelines.
> - The `chatgpt transcript` path already normalizes math delimiters (`--math-dollars`, default on since 2026-08-10). The `chatgpt download` path never does, and most failing files are downloaded sandbox artifacts, not transcript renders.
> - The fix design (D1–D5) is written and ticketed in surf-cli; no implementation has happened yet.

## The failing sync, as observed

The sync run printed a plan summary first, then executed it. Two numbers in that output look contradictory until you know the execution model, and both matter for reading the log:

```text
SYNC: remote-dir=/PARC
SUMMARY: upload=303 skip=2002 stale=0 orphan=0 error=0
...
ERRORS: convert-failed=149 upload-failed=0 delete-failed=0
Error: 149 file(s) failed during sync (convert=149, upload=0, delete=0)
```

The `SUMMARY` line reports the *plan*: 303 local markdown files had no remote counterpart, 2002 already existed remotely. Its `error=0` is a statement about the plan phase, not about the run. The `ERRORS` line reports the *execution*: of the 303 planned conversions, 149 produced no PDF. Nothing failed during upload or deletion; every failure happened between reading a markdown file and producing a PDF.

The failure population is not uniform. Sorting the 149 failures by their pandoc output yields four classes, and the class a file belongs to is decided entirely by patterns in the markdown source.

| Class | Signature in pandoc output | Approximate count | Example file |
|---|---|---|---|
| Math delimiter breakage | `! Missing $ inserted`, `Command \mathcal allowed only in math mode`, `\symcalallowed` | ~100 | `Transcripts/2026/08/20/Design Optimization Framework/optkit-design-and-migration-guide.md` |
| Missing asset, absolute path | `pandoc: /mnt/data/...: withBinaryFile: does not exist` | 3 | `Transcripts/2026/07/21/.../tiny-idp-interpreter-theory-companion.md` |
| Missing asset, relative path | `[WARNING] Could not fetch resource figures/...: replacing image with description` (non-fatal alone) | dozens | `Transcripts/2026/08/06/.../SENTINEL-KERNEL-THESIS.md` |
| Prose/math collision | `You can't use 'macro parameter character #' in math mode`, `Undefined control sequence` | ~6 | `Research/2026/08/03/busybar-communication-sources/external-mqtt-oasis.md` |

The fourth class needs a note: the image warnings in class 3 are non-fatal by themselves — pandoc replaces the image with its alt text and continues. Those files fail because their prose *also* contains class-1 or class-4 breakage. The classes are orthogonal: a file can carry several at once, and the fix for one does not fix another.

## How a transcript becomes a PDF

Every failure in this report happened inside one pipeline, so the pipeline is where the analysis has to start. remarquee converts markdown to PDF through three stages, each with its own parser:

```mermaid
flowchart LR
    A[markdown source<br/>vault .md file] -->|remarquee mdpdf<br/>preprocess| B[pandoc<br/>markdown reader]
    B -->|pandoc AST| C[pandoc LaTeX writer]
    C -->|LaTeX document| D[xelatex]
    D -->|PDF| E[reMarkable upload]
    style A fill:#e8f0e8
    style D fill:#f0e0e0
```

The first stage is remarquee's own preprocessing (`pkg/mdpdf/preprocess.go`): it strips YAML frontmatter, resolves local image paths, renders Mermaid blocks, and normalizes list spacing. The second stage is pandoc's *markdown reader*, which parses the markdown into an abstract syntax tree. The third is pandoc's *LaTeX writer* plus xelatex. The critical property of this chain is that each stage has its own notion of what math is, and the stages do not negotiate. What the markdown reader decides is math, the LaTeX writer emits inside math mode. What the reader decides is *not* math, the writer emits as ordinary text — and if that text happens to contain TeX commands, xelatex receives them in text mode and fails.

That property is the entire root cause of class 1, and it is worth seeing precisely before moving on to where the offending content comes from.

## Root cause one: math delimiters and the pandoc reader

remarquee invokes pandoc with remarquee's own reader configuration:

```go
// pkg/mdpdf/pandoc.go (remarquee)
const DefaultFromFormat = "markdown-yaml_metadata_block"
```

Pandoc's `markdown` format enables the `tex_math_dollars` extension — `$...$` and `$$...$$` are math — but does **not** enable `tex_math_single_backslash`, which is the extension that recognizes `\(...\)` and `\[...\]` as math delimiters. ChatGPT renders its math with exactly those backslash delimiters, so every math-bearing ChatGPT export parses under a reader that does not know its math syntax.

What happens to `\(\Theta\)` under that reader is not a graceful fallback. This is a real reproduction, run against pandoc with remarquee's exact reader configuration:

```console
$ cat repro.md
Let \(\Theta\) be a **search space**. Let \(X\) be the space of cases or
inputs and \(\mathcal T\) the space of possible trajectories.

\[
K : \Theta \times X \rightsquigarrow \mathcal T.
\]

$ pandoc --from=markdown-yaml_metadata_block -t latex repro.md
Let (\Theta) be a \textbf{search space}. Let (X) be the space of cases
or inputs and (\mathcal T) the space of possible trajectories.

{[} K : \Theta \times X \rightsquigarrow \mathcal T. {]}
```

The reader consumes the `\(` and `\)` tokens and treats their *contents* as prose. The LaTeX writer then emits that prose into the document body. The compiled result places `\mathcal`, `\Theta`, and `\rightsquigarrow` in text mode, where they are illegal. Pushing the same input through to PDF reproduces the production error exactly:

```text
$ pandoc --from=markdown-yaml_metadata_block repro.md -o repro.pdf --pdf-engine=xelatex
Error producing PDF.
! LaTeX Error: \symcalallowed only in math mode.
l.61 or inputs and (\mathcal
```

That error message deserves a moment, because its mangled form sent the investigation down a false path initially. LaTeX's actual message is `Command \mathcal allowed only in math mode`. The terminal wrapped the line after `\symcal`, so the log showed the two character sequences `\symcal` and `allowed only in math mode` on adjacent lines, reading as a single nonexistent command `\symcalallowed`. No such command exists anywhere. When an error message names a command that does not exist, suspect line wrapping in the captured log before suspecting the tool.

Two conclusions follow from this reproduction, and both shape the fix.

First, **the vault's transcript markdown is faithful**. `optkit-design-and-migration-guide.md` contains 46 well-formed `\(...\)` inline spans and `\[...\]` display blocks. ChatGPT wrote them; surf-cli exported them verbatim; the corruption happens in the reader, at conversion time. Any fix that "repairs" the vault files would be destroying correct source data to accommodate a reader configuration — although, as the next section shows, there is a legitimate normalization that Obsidian also benefits from.

Second, the failure is configuration-decidable. The same input with `+tex_math_single_backslash` added to the reader format parses every span as math and compiles. This gives remarquee a one-line defense (`DefaultFromFormat = "markdown-yaml_metadata_block+tex_math_single_backslash"`), and it gives a rule for reading any future failure of this class: the delimiter style in the source and the reader's extension set fully determine the outcome.

## Why the normalizer missed these files

surf-cli already contains the correct normalization. Commit `f0dcd64` (2026-08-10) added `normalizeMathDelimiters` to `go/internal/cli/commands/chatgpt_math.go`: it rewrites `\(...\)` → `$...$` and `\[...\]` → `$$...$$`, protects fenced code blocks (including inside blockquotes, fixed in `7b1f6d5`), protects inline code spans, and preserves the document's line count as an invariant. The `chatgpt transcript` command applies it to every markdown path it writes, gated by `--math-dollars`, which defaults to true:

```go
// go/internal/cli/commands/chatgpt_transcript.go (surf-cli)
md := renderChatGPTTranscriptMarkdown(data.Raw)
if s.MathDollars {
    md = normalizeMathDelimiters(md)
}
_, err = io.WriteString(w, md)
```

Dollar math is the right target format, not just a pandoc accommodation: Obsidian renders `$...$` natively and does not render `\(...\)` at all, so normalization improves the vault in Obsidian regardless of PDF conversion.

Given that, why did a file extracted on 2026-08-20 — ten days after the normalizer shipped, with the flag defaulting to on — still contain 46 raw `\(` spans? Because it never went through that code. The file is not a transcript render. It is a *downloaded sandbox artifact*: a markdown document ChatGPT authored inside its code-interpreter sandbox, saved to `/mnt/data/`, and downloaded by a different command, `surf chatgpt download`. Its output directory gives the provenance away — it sits alongside `optkit-design-and-migration-guide-9f242a2d.md` (a second, hash-suffixed copy of the same artifact), `rag-self-improvement.zip-4886de4e`, and a set of downloaded user images with hash-suffixed names. `chatgpt_download.go` has no call to `normalizeMathDelimiters`. Every markdown artifact it writes carries raw ChatGPT math delimiters, independent of when it was extracted.

So the failure population has a clean genealogy. Files that fail through class 1 are, with few exceptions:

- downloaded sandbox artifacts (never normalized, any date), or
- transcript renders extracted before 2026-08-10 (normalizer did not exist yet).

Transcript renders extracted after 2026-08-10 do not fail through class 1. The investigation confirmed this partition by checking the failing files' `\(` counts against their extraction dates and directory shapes.

## Root cause two: sandbox assets, two distinct gaps

The downloader's asset handling is where the remaining classes live, and it is more capable than the failures suggest. `chatgpt download` discovers and fetches two kinds of files: user-uploaded attachments (from message metadata) and code-interpreter outputs referenced in assistant message text as `sandbox:/mnt/data/...` links. The page-context JavaScript runs authenticated on chatgpt.com and downloads in chunks. The optkit directory proves it works: it contains ten `user-..._mnt_data__ren.jpg-<hash>` files that were fetched from the sandbox and written under collision-safe local names.

The failures come from what happens after the fetch — and from what the discovery scan never sees.

**Gap one: references are never rewritten.** The tiny-idp companion markdown references its figures by sandbox-absolute path:

```markdown
![Figure 1. The system is a staged family of interpreters, ...](/mnt/data/tiny-idp-theory-assets/pipeline.png){width=96%}
```

The downloader fetched binary files from that conversation and saved them under hash-suffixed names. But the mapping from sandbox path to local filename is used only for placement. No code writes that mapping back into the markdown, so the reference still points at a path that existed only inside ChatGPT's sandbox. pandoc reads the markdown from a temp directory, resolves the image path against that directory, and fails hard: `pandoc: /mnt/data/tiny-idp-theory-assets/pipeline.png: withBinaryFile: does not exist (No such file or directory)`. Unlike the missing-figure warning, this is a fatal error; the asset was in hand, and the document still lost it.

**Gap two: some assets are never discovered.** The discovery scan matches one pattern in one place: `sandbox:/mnt/data/...` strings inside assistant message text:

```javascript
// go/internal/cli/commands/scripts/chatgpt_download.js (surf-cli)
const matches = p.match(/sandbox:\/mnt\/data\/[^)\]\s"'`]+/g) || [];
```

Sandbox-authored markdown artifacts do not reference their own figures that way. `SENTINEL-KERNEL-THESIS.md` references its figures with bare relative paths:

```markdown
![The rebuilt triage workspace at initial state.](figures/01-triage-overview.png){#fig:triage-overview width=100%}
```

Those eight figures were never downloaded because nothing ever asked for them. They are the reason the conversion attempt prints `Could not fetch resource figures/01-triage-overview.png` — and because the file also carries class-1 math breakage, the figures issue and the math issue present together in one failure.

The two gaps have different severities but the same shape: the download pipeline treats fetched files and markdown references as unrelated data. The fix design makes them one concern — the download result already contains the sandbox-path-to-local-name mapping that a rewrite step needs.

## Root cause three: prose that collides with math syntax

The remaining failures come from ordinary prose characters that the math conventions claim. Two concrete forms appeared in this run.

The MQTT source file `external-mqtt-oasis.md` documents broker wildcards: `A subscription to "$SYS/#" will receive messages published to topics beginning with "$SYS/"`. Two literal dollar signs sit in one paragraph. The `tex_math_dollars` convention pairs them: everything between the first `$` and the second becomes a math span — prose including the `#` character. LaTeX rejects `#` inside math mode (`macro parameter character # in math mode`), and the paragraph kills the document. Note that disabling dollar math is not a general fix here: dollar math is what normalized transcripts use. The document-level question is which `$` pairs are *meant* as math, and that is a content question the extractor is positioned to answer but the converter is not.

The API-scrape file `local-applications-services-web_server-openapi-assets-yaml.md` quotes an HTTP error body containing the literal two-character sequences `\r` and `\n`: `Unprocessable Entity\r\n`. Pandoc's markdown reader treats `\r` as a raw TeX control sequence and passes it through; xelatex fails with `Undefined control sequence`. The characters were prose all along — a quoted escape sequence, not an escape — and no reader configuration can know that without looking at the surrounding words.

Both forms also degrade rendering in Obsidian, which applies the same dollar-pairing convention. This is the argument for fixing them at extraction time in surf-cli rather than at conversion time in remarquee: the vault source should stand on its own in every consumer, not only in the one that reported the failures first.

## Secondary findings from the sync log

Three observations from the log matter for the fix work but are not root causes.

**52 planned uploads left no recorded outcome.** The plan listed 303 uploads; the log records 145 conversion failures and 106 successful uploads, leaving 52 files — a contiguous block of `Projects/2026/08/25` through `2026/09/05`, plus `busybar-firmware-sources` and one RES file — with neither an `OK:` nor an `ERROR-CONVERT:` line. The final counters (`convert-failed=149`, `303−149=154` implied successes) do not match the printed lines (145 + 106). Either remarquee's outcome reporting dropped a batch or the terminal scrollback did. Both raw (`/tmp/scrollbuf.txt`) and trimmed captures lack the lines, so the scrollback is consistent with itself; distinguishing tool bug from capture loss needs a re-run with output redirected to a file. The 52 files' actual sync state is unknown until then.

**Vault duplication multiplies every failure.** The ChatGPT branch flow produced near-identical trees (`Branch X`, `Branch Branch X`, `Branch Branch Branch X`, hash-suffixed and case-collision variants), and several documents exist under multiple dates (the Rabbit R1 guides on 08/07 and 08/11; CNC API Design on 08/08 and 08/11). Nearly every variant fails identically, so each unique defect is counted many times in the 149. Deduplication is vault hygiene, tracked separately in the vault's own maintenance notes — but any verification of a fix has to deduplicate the failure list first or it will overcount its progress.

**The rmapi warnings are noise with a real source.** Nineteen `WARNING: remote tree has changed, refresh the file tree` lines (from `apictx.go:259`) appear across the run. The sync's own uploads invalidate rmapi's cached remote tree, and the cache refreshes. No file is problematic here; the warning is a property of syncing through a mutating remote.

## The fix design

The design is written up in full in surf-cli ticket `SURF-20260913-EXPORTFIX` and tracked as [wesen/surf-cli#12](https://github.com/wesen/surf-cli/issues/12). It has five parts; the ordering reflects leverage and risk, and the first two are small because they reuse a proven pure function.

- **D1 — normalize math in the download path.** `chatgpt download` runs every downloaded markdown artifact through the existing `normalizeMathDelimiters` before writing it. The function is idempotent and fence- and code-span-safe, so re-downloads cannot double-apply.
- **D2 — recursive asset resolution.** After the first download wave, scan fetched text/markdown artifacts for references in three forms (`sandbox:/mnt/data/...`, `/mnt/data/...`, bare relative paths resolved against the sandbox root and the artifact's own sandbox directory) and fetch the discovered paths with the existing page-context chunked downloader. References that do not resolve inside the sandbox are reported in the manifest as `unresolved` rather than dropped silently.
- **D3 — rewrite references on write.** The download result already maps every fetched file's sandbox path to its local hash-suffixed name. After D2, rewrite all three reference forms in every written markdown file to those local names, relative, so each vault directory stays self-contained.
- **D4 — prose sanitizer.** A new pure function alongside `normalizeMathDelimiters`: escape mis-paired `$` in prose spans that fail a math-likeness test (conservative direction — an escaped dollar in prose always renders correctly), and wrap literal `\r`, `\n`, `\t` sequences in inline code outside code spans. Shares the fence/code-span walker with the existing normalizer.
- **D5 — one-shot backfill.** A `surf chatgpt normalize-export` maintenance subcommand applying D1 and D4 in place over a directory tree (dry-run by default), plus `--rewrite-references` using D3's matching against the hash-suffixed files that already sit in sibling directories. Conversations whose sandboxes have been rotated out stay partially unresolved, and the manifest says so.

remarquee independently gets the one-line reader change (`+tex_math_single_backslash` in `DefaultFromFormat`) as defense-in-depth, so legacy files convert even before the backfill runs. That change is in the remarquee repo and is deliberately not a substitute for the surf-cli fixes: the vault files must render correctly in Obsidian on their own, not only through the converter that happened to catch the problem.

The scraped-source files (the busybar webp corruption, a `.vs` file referenced as an image) come from a different ingestion pipeline and are out of scope for this design.

## Key points

- The 149 convert failures reduce to four content classes; the class is decided by patterns in the markdown source, not by chance: backslash math delimiters, absolute `/mnt/data` references, relative references to never-fetched sandbox figures, and prose `$`/`\r\n` collisions with math syntax.
- The pandoc reader, not the transcript content, corrupts backslash math: `markdown` without `tex_math_single_backslash` strips `\(`/`\)` and hands TeX commands to LaTeX in text mode. One reader-extension line makes the same file compile.
- `chatgpt transcript` has normalized math since 2026-08-10 (`--math-dollars`, default on). The failing files are mostly `chatgpt download` artifacts, which bypass that normalizer entirely — a path coverage gap, not a missing feature.
- The downloader fetches sandbox binaries correctly but never rewrites markdown references, and its discovery scan only sees `sandbox:/mnt/data/` links in message text, missing every reference an artifact makes to its own figures.
- Prose/math collisions are content defects worth fixing at extraction time, because Obsidian misrenders them the same way pandoc does.
- 52 files from the sync have no recorded outcome in either scrollback capture; their actual state needs a redirected-output re-run to determine.

## Related documents

- surf-cli ticket `SURF-20260913-EXPORTFIX` — full design doc, task breakdown, and testing plan: `ttmp/2026/09/13/SURF-20260913-EXPORTFIX--transcript-export-fidelity-math-normalization-sandbox-asset-downloads-and-reference-rewriting/`
- GitHub issue [wesen/surf-cli#12](https://github.com/wesen/surf-cli/issues/12) — tracking issue mirroring the ticket
- `PROJ - reMarkable Cleanup 2 - Batch Reorg, Rate Limit Backoff, and Glob Recovery` — same-day note on the remote-tree side of this sync
- `VAULT MAINTENANCE - Transcript filename case collisions` (Logs/2026/09/06) — the branch/case-duplicate hygiene problem that multiplies these failures
