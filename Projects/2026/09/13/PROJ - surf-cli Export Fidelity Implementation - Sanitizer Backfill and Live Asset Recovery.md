---
title: "surf-cli Export Fidelity Implementation: Sanitizer, Backfill, and Live Asset Recovery"
aliases:
    - surf-cli export fidelity implementation
    - chatgpt transcript export fixes implementation report
tags:
    - project
    - surf-cli
    - chatgpt
    - pandoc
    - latex
    - remarquee
    - transcripts
status: active
type: project
created: 2026-09-13
repo: /home/manuel/code/wesen/surf-cli
repo-secondary: /home/manuel/code/wesen/go-go-golems/remarquee
issue: https://github.com/wesen/surf-cli/issues/12
ticket: SURF-20260913-EXPORTFIX
---

# surf-cli Export Fidelity Implementation: Sanitizer, Backfill, and Live Asset Recovery

The companion report to this one — [PROJ - remarquee Sync Convert Failures - Transcript Math Delimiters and Export Fidelity](PROJ - remarquee Sync Convert Failures - Transcript Math Delimiters and Export Fidelity.md) — diagnosed why 149 markdown files failed PDF conversion during a `remarquee upload sync` and wrote the fix design into surf-cli ticket `SURF-20260913-EXPORTFIX`. This report covers what happened next: the design was implemented, and the implementation survived contact with the real corpus badly enough to teach two lessons that synthetic tests could not. By the end you should understand the pipeline as a system of pure string transforms, know why the prose/math classifier looks the way it does, and be able to reproduce the live end-to-end proof: a file that failed conversion in production was re-downloaded through the browser with its six missing figures and converted by remarquee without errors.

> [!summary]
> - All five design pieces (D1–D5) shipped in nine commits: a prose/math sanitizer, write-time normalization in the download path, reference rewriting, a one-shot backfill command, and second-wave asset discovery that fetches missing `/mnt/data` files through the live browser session.
> - Running the backfill over copies of the real broken files caught two sanitizer defects that all synthetic unit tests had passed: display math containing `\text{...}` phrases was escaped wholesale, and `\to` was corrupted to `\\to` by an escape rule without a word boundary.
> - The decisive test was idempotence on real content, not correctness on synthetic fixtures: the second backfill pass reported a file as changed again, which is how both defects surfaced.
> - Live validation closed the loop: the tiny-idp conversation — the only corpus file still failing after offline fixes — re-downloaded with all six never-fetched figures, and remarquee converted and uploaded it.

## The pipeline as a system

Every fix in this work is a pure function over a markdown string, composed by a single walker. That decision shaped everything downstream, so it is worth stating precisely before the pieces.

The walker is `transformProse(md, f)` in `go/internal/cli/commands/chatgpt_math.go`. It splits the document into lines, classifies each line as fenced code or prose (fenced blocks may be prefixed with blockquote markers, since every user line in an API transcript carries `> `), and applies `f` to each contiguous prose region. Two invariants protect the caller. First, `f` is responsible for skipping inline code spans, so backtick-delimited content survives every transform. Second, if a transform ever changes a region's line count, the walker discards the result and leaves the region untouched — a corruption circuit breaker in place of a full markdown parser.

On top of the walker sit four transforms, applied in a fixed order:

```go
// normalizeMarkdownDocument applies the full export-fidelity markdown
// normalization pipeline to a ChatGPT-derived markdown document.
func normalizeMarkdownDocument(md string) string {
	return sanitizeMathAdjacentProse(normalizeMathDelimiters(md))
}
```

`normalizeMathDelimiters` (which predates this work) rewrites ChatGPT's `\(...\)` and `\[...\]` math delimiters to `$...$` and `$$...$$`. `sanitizeMathAdjacentProse` (new) escapes prose that collides with math syntax. `rewriteSandboxReferences` rewrites sandbox asset references to local file names. The D5 backfill composes all of them; the download path applies the first at write time and the third after a conversation's files are all on disk.

Why pure functions rather than a markdown parser? The corpus is ChatGPT exports and scraped source dumps, not conforming CommonMark. A parser would have to be correct about every construct in those documents to be safe in one; a line-based walker with fence and code-span protection is wrong about some things (indented code blocks, list continuations) in ways that are *detectable and conservative* — it transforms too little in ambiguous places, never too much. The P5 validation demonstrated that this trade-off is the right one on this corpus: pandoc itself classifies the production `\r\n` line as prose while treating the adjacent lines as a verbatim block, so a walker that under-protects indented lines fixes exactly the lines that fail.

## The sanitizer and its classifier

`sanitizeMathAdjacentProse` handles the two production failure forms that math delimiter conversion cannot touch.

The first form is the paired dollar sign. MQTT documentation contains `A subscription to "$SYS/#" will receive messages published to topics beginning with "$SYS/"`. Two literal dollars in one paragraph close a `tex_math_dollars` math region between them; the region contains `#`, which LaTeX rejects in math mode. The sanitizer scans each prose segment left to right. At each `$` it looks for a closing `$` (skipping already-escaped ones), classifies the span content, and either copies the span verbatim (math) or escapes both dollars as `\$` (prose). The scan must be a stateful single pass: after escaping an opening dollar, the scanner jumps past the closing dollar, because leaving it in place would let it pair with the *next* dollar and corrupt the following text.

The second form is the literal escape sequence. Scraped C source contains `const char* message = "HTTP/1.1 422 Unprocessable Entity\r\n\r\n";` on a line that pandoc classifies as prose (verified by rendering the file: the `\r\n` lands in text mode while the very next line opens a `\begin{verbatim}`). Pandoc's `raw_tex` handling passes `\r` to LaTeX as a control sequence, and compilation dies with `Undefined control sequence`. The sanitizer doubles the backslash of every `\r`, `\n`, `\t` run in prose, so the sequences render as text in both pandoc and Obsidian.

Idempotence is a property of the scanner, not an afterthought. Three rules produce it: an escaped dollar `\$` is consumed as a two-character verbatim unit; an escaped backslash `\\` likewise; and a literal escape is only recognized when the preceding character is not itself a backslash. A second pass over already-sanitized text therefore finds nothing to change. Without these rules, a re-run would corrupt `\\r` into `\\\r`, and the backfill command — whose whole purpose is to be runnable repeatedly over a vault — would be unsafe.

The interesting part is `looksLikeMath`, the span classifier, because its current shape is a record of two failures.

## Two defects the fixtures did not catch

The unit tests for the sanitizer passed on the first run. The implementation was still wrong. What exposed it was not more unit testing but a property check over real content: the D5 backfill was run twice over a 41-file copy of the production corpus, and the second pass reported `tiny-idp-interpreter-theory-companion.md` as changed again. An idempotent pipeline had produced a different file, which means the first pass had misclassified something — and the before/after diff named it.

**Defect one: display math escaped wholesale.** The word-run heuristic classified a span as prose when its content contained three or more consecutive words. A display block in the tiny-idp companion contains `\text{after a positive safety result},` — legitimate math with an English phrase inside. The heuristic matched, the whole `$$...$$` block was escaped to `\$\$`, and a page of mathematics became literal text. The lesson generalizes: ChatGPT-authored display blocks are always intended math, whatever their content looks like, so the `$$` branch of the scanner now copies display spans verbatim without ever consulting the classifier.

**Defect two: the escape rule without a boundary.** Once defect one had escaped the display block, its interior was ordinary prose to the second pass, and the literal-escape rule went to work on it. The regex matched `\t` inside `\to` — backslash, `t`, then `o` — and doubled it, turning `\mathsf{Idle}\to\mathsf{Leased}` into `\mathsf{Idle}\\to\mathsf{Leased}`. The production case was `\r\n`, where the letter is the last character of the token; `\to`, `\text`, `\right`, and `\newline` are TeX commands whose first letter collides with an escape name. The fix is a word boundary: a literal escape is recognized only when the letter is followed by a non-letter. RE2 has no lookahead, so the regex run was replaced by a manual scan in `isLiteralEscape` and `writeDoubledEscapeRun`.

The two defects interacted, which is why the diff alone was misleading: defect one created the conditions for defect two, and the visible corruption (`\\to`) sat far from its cause (`\text{after a positive safety result}`). Inspecting the pass-1 output separately from the pass-2 diff was what separated the two.

The classifier itself came out of this with a sharper rule. Real prose pairs — `$SYS/#`, `Entity\r\n`, a run of English words — have a property that `\text{...}` math lacks: they contain no backslash commands. The final `looksLikeMath` therefore reads:

- content with `#` or quote characters is prose (those characters are fatal or alien in math mode);
- content containing any TeX command is math, regardless of word runs;
- otherwise, a run of three or more words containing a common English stopword (`the`, `of`, `is`, ...) is prose; everything else is math.

Each clause is a decision that a production failure forced. The stopword requirement inside the last clause is what keeps `$n \text{ is the count}$` on the math side of the line while still catching prose like `$five six seven eight dollars for it and ...$`.

The general lesson is worth stating as a rule: **synthetic fixtures verify the cases their author imagined; idempotence over the real corpus verifies the cases the corpus contains.** The unit suite covered every production failure form and still passed while the sanitizer corrupted real documents. The cheap corpus-level gate — run the transform twice, require byte-equality — is what caught both defects, and it now exists as a test over the full pipeline composition.

## Write-time normalization and reference rewriting

With the transforms correct, wiring them into the download path is a small amount of structural work with one architectural decision each.

`chatgpt download` writes files at four completion points: input and output downloads, each with a direct write and a chunked fallback for files that exceed the native messaging output cap. The chunked path streams to `dest + ".part"` and renames on completion, so it never holds the full byte slice in Go. The normalization hook therefore runs *post-write* — read the file, transform, write back if changed — which covers all four points uniformly. The hook is best-effort by design: the raw artifact is already safely on disk when normalization runs, and a normalization failure must never mark a successful download as failed. Provenance beats normalization.

Reference rewriting has one correctness constraint that is invisible until it bites: the needle ordering. A sandbox path appears in two forms, `sandbox:/mnt/data/<path>` and `/mnt/data/<path>`, and the first contains the second as a suffix. Replacing the bare form first produces `sandbox:<localName>` — a corrupted reference. `rewriteSandboxReferences` sorts needles longest-first, so the prefixed form always wins. The mapping it uses is not new data: the download result already carries each file's sandbox path and its collision-safe local name (`<name>-<hash8>`), so the rewrite is a pure function over information the flow already possessed.

Two policy decisions in the rewrite are deliberate. Skipped downloads (files already on disk from an earlier run, with `--skip-existing`) contribute to the mapping, because a skipped file still proves where its asset lives — this is what lets re-runs link references to assets fetched long ago. And unmapped references are left verbatim. A reference to a never-downloaded file is provenance information about the sandbox origin; deleting it would make the export self-consistent and historically false.

## The backfill command

`surf chatgpt normalize-export` turns the pipeline into a maintenance verb over the existing vault. It walks a directory tree for `.md` files, applies `normalizeMarkdownDocument` to each, and — with `--rewrite-references` — rebuilds the sandbox mapping by matching each `/mnt/data/...` reference's basename against sibling files, accepting either an exact name or the `<basename>-<hash>` download naming. Dry-run is the default; `--write` applies. The report row per file carries `status`, `math_changed`, `refs_rewritten`, and `refs_unresolved`, so a dry run over the vault states exactly what a write would do.

The sibling-matching mode exists because most of the affected vault directories were exported before any of this code existed and have no manifests. The downloaded assets sit next to the markdown with recognizable names, which is enough to reconstruct the mapping without the browser.

## Second-wave asset discovery

The first download wave discovers assets by scanning assistant message text for `sandbox:/mnt/data/...` links. Artifacts authored inside the sandbox reference their own figures by bare relative path — `![...](figures/01-triage-overview.png)` — and message text never contains those strings, so the figures were never fetched. The D2 second wave scans the artifacts themselves.

`resolveSandboxAssetRefs(md, baseSandboxDir)` returns every sandbox path a document references: absolute forms anywhere in the text, plus relative image-syntax targets (an image is always an asset) and link targets with asset or markdown extensions, resolved against the referencing artifact's own sandbox directory and clamped so `..` cannot escape `/mnt/data/`. The base directory comes from the download result — each artifact's sandbox path is known, so its directory is known, so its relative references resolve to full sandbox paths.

`discoverConversationAssets` runs a bounded breadth-first search over the conversation directory: scan every markdown file whose sandbox origin is known, fetch each newly discovered path through the same page-context interpreter download endpoint (with the referencing artifact's message id, which is the correct message context for its sibling assets), then scan any fetched markdown in turn, for at most three rounds. Fetched assets join the reference-rewrite mapping, which runs after the wave — so a figure that the second wave fetches is also a figure the rewriter links.

The one deliberate asymmetry: relative references in files with an *unknown* sandbox origin are skipped rather than guessed. The command would rather leave a reference dangling than fetch a path it inferred.

## The live proof

Offline validation left exactly one corpus file failing: the tiny-idp companion, whose `/mnt/data/tiny-idp-theory-assets/*.png` figures were never downloaded and whose references pandoc treats as hard errors. Closing that gap required the live browser path, which the session had available.

Three findings mattered during the live run, none of them about the new code.

First, the socket path. Snap Chromium confines the native host, so the surf socket lives at `/home/manuel/snap/chromium/common/surf-cli/surf.sock` — set by the host wrapper via `SURF_SOCKET_PATH` — not at the default `/tmp/surf.sock`. A CLI client that does not honor the environment variable cannot see the running host.

Second, a socket can exist as a process but not as a file. The running host held a valid listener, but its socket file was gone: an earlier manual `surf-host-go --version` invocation had bound the same path, and removed the socket file on exit, unlinking the live host's endpoint. The recovery is clean because the browser extension's service worker retries `connectNative` on a five-second timer — kill the stale host, wait seconds, and the browser respawns it with a fresh socket. The operational rule that falls out of this: never run the host binary manually beside a live host; kill-and-respawn is the safe recovery.

Third, the client/server split of the fix itself. The native host only relays page-context JavaScript; all of the new logic — discovery, normalization, rewriting — executes in the CLI client. A newly built `surf-go` binary runs against the months-old installed host without touching it, which meant the live validation needed no redeployment of the browser-side infrastructure.

The run itself, against conversation `6a5e08c8-8040-83ea-9d7b-750535bf03ff`:

```text
[output] tiny-idp-interpreter-theory-companion.md — downloaded (134672 bytes)
[output] tiny-idp-interpreter-theory.bib — downloaded (18811 bytes)
[output] pipeline.png — downloaded (107917 bytes)   ← second wave
[output] defun.png — downloaded (78235 bytes)       ← second wave
[output] capability.png — downloaded (64517 bytes)  ← second wave
[output] worker.png — downloaded (107739 bytes)     ← second wave
[output] generation.png — downloaded (95694 bytes)  ← second wave
[output] languages.png — downloaded (82964 bytes)    ← second wave
```

The written companion markdown verified at three properties: zero raw `\(` delimiters (math normalized), zero `/mnt/data` references (all six rewritten to the downloaded local names), and every `![Figure N ...]` pointing at a file on disk. The final command was the one whose production failure started the entire investigation:

```text
$ remarquee upload md tiny-idp-interpreter-theory-companion.md --remote-dir /D2-TEST
OK: uploaded tiny-idp-interpreter-theory-companion.pdf -> /D2-TEST
```

The file that died on `pandoc: /mnt/data/tiny-idp-theory-assets/pipeline.png: withBinaryFile: does not exist` now converts and uploads.

## What the validation covered, and what it did not

Precision about scope matters more here than enthusiasm. The offline validation converted four of five production failure files under remarquee's exact pandoc flags: optkit (463KB PDF, was `Command \mathcal allowed only in math mode`), SENTINEL (237KB, math fixed, missing figures remain non-fatal warnings until their conversation is re-downloaded), mqtt-oasis (451KB, was `macro parameter character # in math mode`), and mqtt_http_proxy (62KB, was `Undefined control sequence`). The live run closed the fifth. The backfill is idempotent over the whole 41-file corpus — second pass, 41/41 unchanged.

Not covered: the remaining affected corpus has not been re-downloaded or backfilled in place; the classifier is a heuristic and content that violates its assumptions (a prose pair containing a backslash command) would still slip through; and the scraped-source ingestion pipeline that produced the busybar webp corruption is a separate system with the same class of problem. The remarquee-side reader hardening (`+tex_math_single_backslash` in its default `--from`) remains open as defense-in-depth for files that predate any normalization.

## Key points

- Every fix is a pure string transform over markdown, composed by one line-based walker with fence and inline-code protection and a line-count circuit breaker; correctness does not depend on a markdown parser being right about a nonconforming corpus.
- Idempotence is the property that made the pipeline safe to run repeatedly over a vault, and idempotence testing on real corpus content — not synthetic fixtures — is what caught both implementation defects.
- Display `$$` spans are always intended math and never consult the prose classifier; `\text{...}` phrases inside math are the case that forced this rule.
- Escape-sequence recognition requires a word boundary: `\r\n` is a literal escape, `\to` and `\text` are TeX commands, and the difference is what follows the letter.
- A span containing any TeX command is math; real prose pairs never contain backslash commands.
- Needle length ordering prevents `sandbox:`-prefixed references from being corrupted by bare-path replacement.
- Unmapped references stay verbatim — exports must remain historically true about what the sandbox contained, even when a target is missing.
- The native host only relays JavaScript; all new logic runs in the CLI client, so new code ran against a months-old installed host without redeployment.
- Never run the host binary manually beside a live host: the second listener removes the socket file on exit and orphans the first. Kill the host and let the extension's five-second retry respawn it.

## Related documents

- [PROJ - remarquee Sync Convert Failures - Transcript Math Delimiters and Export Fidelity](PROJ - remarquee Sync Convert Failures - Transcript Math Delimiters and Export Fidelity.md) — the root-cause analysis that motivated this implementation
- surf-cli ticket `SURF-20260913-EXPORTFIX` — design doc, tasks, and implementation diary (steps 1–8): `ttmp/2026/09/13/SURF-20260913-EXPORTFIX--transcript-export-fidelity-math-normalization-sandbox-asset-downloads-and-reference-rewriting/`
- GitHub issue [wesen/surf-cli#12](https://github.com/wesen/surf-cli/issues/12) — tracking issue with implementation and live-validation status
- `VAULT MAINTENANCE - Transcript filename case collisions` (Logs/2026/09/06) — the branch/case-duplicate hygiene problem that multiplies conversion failures
