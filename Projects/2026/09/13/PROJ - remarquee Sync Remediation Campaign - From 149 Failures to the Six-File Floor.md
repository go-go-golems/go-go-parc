---
title: "remarquee Sync Remediation Campaign: From 149 Failures to the Six-File Floor"
aliases:
    - remarquee sync remediation campaign
    - export fidelity campaign closing report
tags:
    - project
    - remarquee
    - surf-cli
    - chatgpt
    - pandoc
    - latex
    - transcripts
    - subagents
status: complete
type: project
created: 2026-09-13
repo: /home/manuel/code/wesen/surf-cli
repo-secondary: /home/manuel/code/wesen/go-go-golems/remarquee
issue: https://github.com/wesen/surf-cli/issues/12
ticket: SURF-20260913-EXPORTFIX
---

# remarquee Sync Remediation Campaign: From 149 Failures to the Six-File Floor

Two earlier reports in this series diagnosed and then implemented the fixes for a `remarquee upload sync` that failed to convert 149 markdown files to PDF. This report closes the series: it covers the remediation campaign that ran those fixes over the real corpus and pushed the failure count from 149 down to 6, and it examines what the campaign taught that the code alone could not. By the end you should be able to read a bulk-conversion failure report as an operational instrument — knowing which classes yield to pipelines, which to engine configuration, which to re-acquisition from the source, and which to a verification-gated manual loop — and you should know the specific failure modes this corpus exhibited at each boundary, because several of them were not in anyone's model of the system when the first sync failed.

> [!summary]
> - The campaign ran four rounds — vault-wide backfill, remarquee engine hardening, live asset re-acquisition, and a parallel manual-fix campaign over 50 files — reducing convert failures 149 → 80 → 62 → 12 → 6.
> - The floor is real, not aspirational: every remaining failure is image-binary corruption or format refusal in the scraped-source ingestion pipeline, a different system from the ChatGPT export pipeline the campaign repaired.
> - Two failure classes were discovered only by running the work: ChatGPT's sandbox has a retention window that expires old assets server-side (`no download_url`), and two "broken" files were in fact zero-byte exports — empty from birth, not corrupted.
> - The manual round was tractable because each fix was gated on compilation: edit, compile, read the error, edit again. That loop is safe to parallelize across disjoint files and is the correct shape for content problems that no string transform can classify.
> - The workers repeatedly found better root causes than the orchestrator's prompts: "JSON in prose" was usually a broken outer code fence; a mangled `\right` was a literal carriage-return byte; control-character corruption was C-escape decoding, not random bit rot.

## The shape of the campaign

A remediation campaign over a failing corpus is a sequence of rounds, each removing one failure class, each measured by the same instrument: `remarquee upload sync --remote-dir /PARC`, its `convert-failed` counter, and its per-file error blocks. The counter is what makes the campaign legible. Every round ended with a full sync rerun, and every rerun produced an auditable delta.

| Round | Intervention | Convert failures |
|---|---|---|
| 0 — baseline | none (the original 2026-09-13 morning sync) | 149 |
| 1 | vault-wide export-fidelity backfill (189 files rewritten) | 80 |
| 2 | remarquee engine hardening (reader format + LaTeX preamble) | 62 |
| 3 | live sandbox re-downloads, asset merge, empty-file handling | 12 |
| 4 | manual LaTeX-content fixes (50 files, parallel workers) | **6** |

The instrumentation mattered twice beyond the headline number. First, the second rerun revealed 10 uploads failing on `401 Unauthorized` — the reMarkable cloud token had expired mid-run — which is a transient class the count would otherwise have hidden as content failure. Second, reruns with output redirected to a file recovered something the original terminal capture had lost: the original scroll buffer was missing 52 outcome lines, and the redirected logs never were. When a run takes twenty-five minutes and prints thousands of lines, the log is the experiment; capture it to a file.

## Round 1: the backfill at vault scale

`surf chatgpt normalize-export` walked all 2312 vault markdown files and rewrote 189 of them: math delimiters converted, prose-paired dollars escaped, literal escape sequences doubled, and two sandbox references linked to sibling downloads. Two properties made running it over the whole vault safe rather than merely tempting.

The first is idempotence. The sanitizer had been hardened against exactly this before release — display `$$` blocks containing `\text{...}` phrases, `\to` matched as `\t` — but the vault-wide run still surfaced a residue: two files changed on the second pass and only converged on the third. Idempotence on a corpus is a measurable property, and this one measured 99.96% on first application. The residue went into the ticket as a documented observation with a candidate cause, not as a blocker; the alternative — blocking a 189-file repair on two files' convergence behavior — would have cost more than it protected.

The second property is reviewability. The vault is a git repository, so the backfill was a diff before it was a fact: 17,439 line-pairs across 189 files, spot-checked before commit. The transformation's line-preserving design (no fix adds or removes a newline) is what made the diff reviewable at all — a rewriting tool that reflows content would have produced diffs too large to read and too noisy to trust.

## Round 2: the engine side of the boundary

The backfill fixed the files; remarquee's conversion configuration still had two independent defects, both fixed in one commit (`6e049ff`).

**The reader format.** Pandoc's default markdown reader does not enable `tex_math_single_backslash`, so `\(...\)` and `\[...\]` are not math delimiters to it — the reader consumes the delimiter tokens and hands the inner TeX commands to LaTeX in text mode, where they are fatal. surf-cli now normalizes delimiters at extraction time, but remarquee's default reader gained `+tex_math_single_backslash` anyway, because the converter is the last component that can save a legacy file that bypassed every upstream pipeline. Defense-in-depth here is cheap: one extension name.

**The preamble.** The failing corpus named a small set of commands that real LaTeX defines but the preamble never loaded: `\centernot` (negated arrows, package `centernot`), `\xRightarrow` (extensible arrows, package `mathtools`), and the `CD` commutative-diagram environment (package `amscd`). The most instructive case is `\require`. ChatGPT renders math with MathJax, and MathJax's dialect includes `\require{AMScd}` — a directive telling the browser renderer to lazy-load an extension before rendering what follows. ChatGPT emits it before commutative diagrams. xelatex has no `\require`; the math span dies with `Undefined control sequence`. This is a boundary divergence in the precise sense: two systems that both speak "LaTeX" do not speak the same language, and the export path crossed the boundary without translating. The fix in remarquee's preamble is one line — `\newcommand{\require}[1]{}` — a no-op that lets the surrounding math compile, plus `amscd` so the diagram the directive was loading actually renders. Three of the previously-failing transcripts convert because of those four preamble lines alone.

## Round 3: what the source still had

The remaining asset failures required going back to ChatGPT, and the campaign's third round is the one that rewrote the understanding of what "re-download the missing files" means.

**Retention is a window, not a guarantee.** The re-download of thirteen conversations discovered that ChatGPT's interpreter sandbox expires old files server-side. The download endpoint answers with a payload containing no download URL — the discovery pass sees the reference, requests the file, and the backend declines. Seven to forty-five such refusals per conversation, for conversations from July and August. The assets that predate the window are not "missing" in any recoverable sense; they are gone. What survived inside the window: six figures for the tiny-idp conversation, two user-uploaded images for the RAG handbook, five images for one more conversation. The window is the constraint that turns "re-download the missing files" from a batch operation into a triage.

**Two files were empty from birth.** The tiny-idp monograph and the Goja Cloud textbook both failed conversion with `Error producing PDF` and no visible LaTeX error — because the vault files were zero bytes. The pandoc behavior on empty input (a document with no pages) is its own confusing signature, and the diagnosis came from `ls`, not from the compiler. The live re-download had the real content both times (103KB and 113KB). An empty export is a failure of the original extraction run that no conversion-side fix can address; the campaign deleted one born-empty project report that had no git history and replaced the two recoverable ones.

**Fatal and non-fatal references are a taxonomy.** After the merge, the corpus's image references fall into three classes with different severities, and the campaign exploited the difference. An absolute `/mnt/data/...` image reference makes pandoc try to open a file that does not exist on this machine — fatal. A relative reference to a missing file, like `figures/rotated-out.png`, makes pandoc print `Could not fetch resource ... replacing image with description` — a warning; the document renders with the alt text where the image would have been. So the merge downgraded the three permanently-rotated handbook figures from absolute to bare relative basenames: the reference survives as provenance, the PDF gains an alt-text placeholder instead of failing, and the failure class moves from "blocks conversion" to "renders incompletely." That is the correct trade when the alternative is no PDF at all.

## Round 4: manual fixing as an engineering shape

After rounds one through three, 58 failures remained, dominated by a class the implementation report had judged "not safely automatable": unwrapped math in prose, raw book-template TeX, invented macros, code fragments sitting in prose. The user called for manual fixing, and the campaign's answer to "manual" deserves precision, because it was not a person opening files one at a time.

**Why the class resists a pipeline.** The two dominant sub-classes want opposite treatments. Unwrapped math — `\mathrm` sitting in text mode because a scraped arXiv abstract lost its delimiters — wants wrapping in `$...$`. A literal TeX mention in pasted code — `/** \brief`, `f.write('\n'` — wants escaping or a code fence, because it is *not* math and must not be wrapped. Distinguishing them requires knowing what the author meant, which is exactly the information a string transform does not have. Any blind heuristic fixes one sub-class while corrupting the other.

**Why the class yields to a loop.** The reframing that made the round tractable: the unit of work is not "classify this file" but "make this file compile." A fix-compile-iterate loop — edit, run pandoc with the exact production flags, read the first error, edit again — converges because each compile is ground truth. The judgment shifts from classification (hard, unsafe) to localization (easy, verified). Fifty files at up to six iterations each is bounded work, and the work parallelizes perfectly: the files are disjoint, the verifier is a script, the loop needs no shared state.

**The orchestration.** The 44 math-class files were partitioned into six families by error signature — control-character corruption (4 files), raw `\frontmatter` book structure (12), invented math macros (8), unfenced code fragments (13), malformed math and JSON-in-prose (7) — and each family went to one parallel subagent (fresh context, `glm-5.3-flash`), with the file list, the evidence, family-specific fix guidance, and a hard contract: every file must reach `PASS` under the production-equivalent verifier, with up to six iterations, editing only its own files, committing nothing. The orchestrator then independently re-ran the full 44-file verification sweep before committing.

**The workers out-diagnosed the orchestrator.** This is the round's most valuable output. The prompts were written from the sync log's first-error lines, and the workers' compile loops found better root causes. Files prompted as "JSON in prose creating phantom math" were really broken outer code fences — heredoc scripts with embedded triple-backtick lines that closed their own container early, leaking script content into prose; the `$`-pairing diagnosis was a symptom, not the disease. A `Missing \right` error turned out to be a literal carriage-return byte that had replaced `\r` inside `\right`. The control-character corruption decoded as C-escape mangling: a decoder had turned `\tau` into TAB+`au` and `\frac` into form-feed+`rac`, which is why restoring `\tau` and `\frac` — not deleting the bytes — was the correct fix. Two "corrupt image" files were remote URLs serving AVIF (which xelatex cannot load) and a Wikimedia endpoint returning HTTP 403 to non-browser fetchers. In every case the loop's ground truth corrected the prompt's hypothesis. An orchestrator that insists its own diagnosis is the contract would have shipped worse fixes.

**Two process defects, both cheap lessons.** The shared verifier script wrote fixed paths under `/tmp`, and five concurrent workers overwrote each other's intermediate files, producing transient false PASS/FAIL flips; three workers independently built race-free private copies before trusting their results. The harness should have used per-invocation temporary files from the start. The second defect was the orchestrator's: partitioning files by the *first* error line of a multi-error block misclassified six files whose real fatals (undefined custom environments) sat behind an image warning. The cleanup round existed because of that. A file's category should come from its full error block, or the plan should expect a second sweep.

## The floor

Six failures remain, and the campaign's claim is that they are the floor for this ticket — not because fixing them is impossible, but because they are not this system's failures.

| File | Image problem |
|---|---|
| busybar `external-mongoose-mqtt` | dozens of "webp" files that are HTML error pages saved as images |
| busybar `external-busylib` | a `.vs` C source file referenced as an image |
| busybar `external-lvgl-github` | an unloadable gif |
| koffi `node-addon-api/README` | genuinely malformed SVG shipped inside the npm package |
| RES Anthropic 2024 | remote image served as AVIF, unloadable by xelatex |
| RES RAGAS (arXiv full) | unloadable remote image in scraped source |

Every one is an image-acquisition defect in the scraped-source ingestion pipeline: the scraper saved whatever bytes came back without validating that they decode as the claimed format. The remediation is format validation (and re-encoding to PNG) at scrape time — a different ticket, in a different codebase, with the same verification shape this campaign used.

## What the campaign teaches

- **Boundaries are where dialects diverge.** MathJax's `\require` is not LaTeX's; a C-escape decoder's `\t` is not TeX's `\to`; an engine's retention window is not a filesystem. Three of the campaign's failure classes existed only because data crossed a boundary between systems that share a syntax but not a semantics. When a pipeline hands content between systems, inventory the dialect differences at each boundary before debugging the content.
- **Retention windows turn re-acquisition into triage.** "The source still has it" is a time-bounded property. The re-download round's real work was deciding what was inside the window, and the honest output of the pass was a permanent-loss list, not just recovered bytes.
- **Severity classes in image references are exploitable.** Absolute-path missing images are fatal; relative missing images are warnings. Downgrading an unrecoverable absolute reference to a relative one converts a conversion failure into a rendering placeholder — the right trade when the target is gone and the text should still read.
- **The fix-compile loop is the tractable middle.** "Not safely automatable" applies to blind transforms, not to verified iteration. Classification is unsafe; localization with compilation as ground truth is safe, parallelizable, and self-correcting — and it upgrades the fixer's diagnosis faster than the planner's, because the compiler is a better teacher than the prompt.
- **Shared scratch state breaks under fan-out.** Fixed `/tmp` paths in a verification harness are a concurrency bug that manifests as flaky test results, which is the worst way to discover a race. Unique temporary paths per invocation are the fix, and it should be built in the first version.
- **Partition by the full error block.** A multi-error file's first line is an introduction, not a summary. The campaign needed a cleanup round because six files were shelved under their opening symptom.

## Key points

- The campaign reduced convert failures from 149 to 6 in four measured rounds: backfill (189 files), engine hardening (reader extension + four preamble lines), live re-acquisition (bounded by sandbox retention, two empty exports replaced), and a parallel manual round (50 files, six families, per-file compile verification).
- Every fix was gated on evidence: unit tests for transforms, idempotence on the real corpus, full-file verification sweeps before commits, and a complete sync rerun per round.
- The remaining 6 are image-acquisition defects in the scraped-source pipeline — a different system, recommended for a separate ticket.
- The manual round's value exceeded its fixes: its compile loops corrected the orchestrator's diagnoses for at least four failure causes, including the fence-leak pattern that recurred across multiple families.
- Empty exports are a failure class with a confusing compiler signature; `ls` diagnoses what pandoc cannot.
- The full artifacts live in surf-cli ticket `SURF-20260913-EXPORTFIX` (closed complete, diary steps 1–11), remarquee commit `6e049ff`, and the vault commits `2f6ffe9`, `9e445b8`, `a8e8f9e`, `f6310c2`, `95eba2f`.

## Related documents

- [PROJ - remarquee Sync Convert Failures - Transcript Math Delimiters and Export Fidelity](PROJ - remarquee Sync Convert Failures - Transcript Math Delimiters and Export Fidelity.md) — the root-cause analysis that started the series
- [PROJ - surf-cli Export Fidelity Implementation - Sanitizer Backfill and Live Asset Recovery](PROJ - surf-cli Export Fidelity Implementation - Sanitizer Backfill and Live Asset Recovery.md) — the implementation report for the D1–D5 pipeline
- surf-cli ticket `SURF-20260913-EXPORTFIX` — full diary and changelog: `ttmp/2026/09/13/SURF-20260913-EXPORTFIX--transcript-export-fidelity-math-normalization-sandbox-asset-downloads-and-reference-rewriting/`
- GitHub issue [wesen/surf-cli#12](https://github.com/wesen/surf-cli/issues/12) — the complete round-by-round accounting
