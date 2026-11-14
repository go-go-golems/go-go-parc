# Validation log — Agent-Operated Engines

Diary of how each chapter was checked with isolated pi agents (DeepSeek 4.1 Flash via lunaroute, thinking high),
following `Research/playbooks/pi-coding-subagents-handbook.md`. Newest step last.

## Method

Two stages per chapter.

**Stage A — read, answer, transfer, review** (`validate.sh`, `batch.sh`, `score.py`, `show.py`). One isolated run
per scenario: no tools, no files; the prompt holds the chapter version (frozen as `versions/NN-TAG.md`), the
overview's notation, the tasks (`scenarios/NN-X.md`) and a JSON output contract. Each scenario has four quiz
questions with a hidden key (`keys/NN.json`), one transfer task where the pattern fits, and one control where it
should not be used. Scored automatically: quiz (keyword groups), fit verdicts. Read by hand: transfer mappings,
sketches and chosen notes, and the review notes, which drive the next version. Same scenarios rerun on every version.

**Stage B — build real software** (`build/build.sh`, `after.sh`, `coach.sh`, `analyze.sh`). A pi agent with read,
write, edit and bash, in its own directory holding only `CHAPTER.md` and `TASK.md`, builds a small stdlib-only Python
project that needs the pattern, writes and runs its own tests, and reports in JSON. Afterwards: hidden acceptance
tests (`build/hidden/NN/`, checked first against a reference implementation), the agent's own tests, a transcript
export and a go-minitrace conversion; `analyze.sh` queries what the agent did (tool calls, test runs, files, when it
read the chapter). `coach.sh` resumes the session with a hint, to measure what extra information fixes.

## Step 1 — chapter 01, stage A (v1 → v3)

| Version | Quiz a / b | Fits a / b | Clarity | Reusability | Would apply |
| --- | --- | --- | --- | --- | --- |
| v1 | 4/4, 4/4 | 2/2, 2/2 | 3, 3 | 3, 3 | 4, 3 |
| v2 | 4/4, 4/4 | 2/2, 2/2 | 4, 4 | 4, 3 | 4, 4 |
| v3 | 4/4, 4/4 | 2/2, 2/2 | 4, 3 | 4, 3 | 4, 4 |

v1 → v2: the walker sketch only checked a subset of result keys; limits' units were ambiguous because the sketch
converted before checking; warnings had no channel back; `flags` undefined; no rule for one name on several kinds; no
cross-argument hook; "no consumer keeps a list" contradicted by the chapter's own exceptions. All fixed.
v2 → v3: defined "expansion"; positional/named matching and duplicates; method-level redirects in the record; samples
in the record; record evolution (defaults are part of identity); stopping rule for applicability; trimmed.

Transfer quality (graded by hand, v3): home automation — all eight participants mapped, one bind path for voice and
app, plug-in records validated at start-up, the host-owned `confirm` flag (added in v2) used correctly. SQL UDFs —
found the crux (overload sets need a candidate lookup) from note 7 and the variations, read implicit casts as the
silent-default bug, used v3's "defaults are identity" note for plan invalidation; one gap (ambiguous matches).
Controls (protobuf already generates the records; one consumer only) rejected with the right reasons and alternatives.

## Step 2 — chapter 02, stage A (v1 → v2, v3 written)

| Version | Quiz a / b | Fits a / b | Clarity | Reusability | Would apply |
| --- | --- | --- | --- | --- | --- |
| v1 | 4/4, 4/4 | 2/2, 2/2 | 3, 3 | 3, 4 | 4, 4 |
| v2 | 4/4, 4/4 | 2/2, 2/2 | 3, 4 | 4, 3 | 4, 4 |

v1 found pseudocode that dropped refusals, frames compared but never converted, a `resultSpace` contradiction,
undefined `level` and bare numbers, no owner for conversions. v2 added the conversion catalogue, three separate axes,
value-dependent conversion parameters (the FX transfer found this gap on its own). v2's reviewers then found a dead
`ENCODING` check, a missing explicit-loss path, three different frame predicates, losslessness that depends on
precision, and masks without a space (goja-cv reads masks as stored). Fixed in v3, not yet rerun.

Transfer quality (v1): drone survey — good mapping and a domain insight (areas in degrees are off by cos latitude),
frame logic muddled by v1's own sketch. Currency — strong: the date became part of the tag, rates recorded as
conversions, sum-then-convert vs convert-then-sum flagged. Controls (web-form profiles; per-sample tags in an audio
loop) rejected correctly, with container-level tagging proposed for audio.

## Step 3 — stage B pilot, chapter 01 (running)

Task `build/tasks/01-TASK.md`: `hubreg`, a home-automation hub's action registry and CLI, three consumers (assistant
tool schemas, app controls, hub validation), demo plug-ins. Hidden tests (25) target what only the chapter teaches:
consistency checks at registration, usual-range warnings, no silent coercion, redirects with fixes, nearest names,
one record per kind and name, host-owned confirmation, a walker that checks result fields both ways. The reference
implementation passes 25/25. Two agents (`a1`, `a2`) build from the v3 chapter.

## Step 4 — stage B pilot result (chapter 01, v3 chapter)

| Agent | Hidden tests | Own tests | Modules | Time / tool calls |
| --- | --- | --- | --- | --- |
| a1 | 25/25 | 159 passing | spec, argtypes, diagnose, render, registry, walker, demo, cli | 7 min / 48 |
| a2 | 24/25 → 25/25 | 155 passing | records, argtypes, binder, describe, diagnose, registry, walker, demo | — |

a2's failure was a gap in the task, not the chapter: it named the warning `W_RANGE`, and the task never fixed the code.
The hidden test now accepts any code containing `RANGE`, and the task states it. go-minitrace (a1): read TASK.md and
CHAPTER.md once at turn 1, never re-read the chapter; built modules in the order of the chapter's participants; wrote
`test_surface.py` ("everything reachable is a record", note 9) and `test_types.py` (pluggable types, note 6).
Both builders independently fixed the same sketch bug: unknown keys must be checked before missing arguments.

## Step 5 — coaching (resume with a change request)

`build/tasks/01-COACH-extend.md`: a new `rgb` argument type and a plug-in using it without touching the core, a fifth
consumer (`voice_phrases`), and a renamed argument with a repair. Hidden extension tests (7) verified first against an
extended reference. Both agents: 25/25 original, 7/7 extension; own tests 186 and 192. Type and plug-in were new files
only (both credit note 6); the consumer needed a 2–3 line delegate on the registry because the API named the method;
the rename was a data edit plus a redirect (notes 4 and 8). a2 added a test proving the core files never mention the
new type. Gaps they reported (folded into chapter 01 v5): rendering domain types in tool schemas; alias versus refusal
for renames; consumers as modules outside the core. Caveat: go-minitrace records edits made through bash heredocs as
executions without a file path; `after.sh` now snapshots the work directory per stage and diffs the snapshots.

## Step 6 — chapters 03–06, stage A

| Chapter | Version | Quiz a / b | Fits | Clarity | Reusability | Main findings |
| --- | --- | --- | --- | --- | --- | --- |
| 03 | v1 | 4/4, 4/4 | 2/2, 2/2 | 3, 3 | 4, 4 | operation version missing from the key; build-time functions must be data-independent; undefined run memo; sketch contradicted note 7 |
| 03 | v2 | 4/4, 4/4 | 2/2, 2/2 | 4, 4 | 4, 3 | (one run first returned a truncated answer and was retried) |
| 04 | v1 | 4/4, 4/4 | 2/2, 2/2 | 4, 4 | 3, 3 | reach cannot express resampling, multi-input extents, directional reach, scattered windows → footprints |
| 04 | v2 | 4/4, 4/4 | 2/2, 2/2 | 4, 4 | 3, 4 | |
| 05 | v1 | 4/4, 4/4 | 2/2, 2/2 | 4, 4 | 4, 3 | (key fixed: "None … ever called" is correct) timeout, contract specimen, prelude failure, helpers vs state |
| 05 | v2 | 4/4, 4/4 | 2/2, 2/2 | 3, 4 | 2, 3 | regression: pictures as a first-class participant, pasted tool description → v3 generalises |
| 06 | v1 | 4/4, 4/4 | 2/2, 2/2 | 3, 3 | 3, 3 | suggestion order stated three ways; a false example (crop/drop); open host codes; undefined sketch helpers |
