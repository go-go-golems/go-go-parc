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

## Step 7 — replicates, chapters 07–13, more builds, diaries, playbooks

- **Replicates** (`a2`, `b2` = the same scenarios with fresh agents; `multi.sh` pools runs across chapters). Across 22
  replicate runs of chapters 01–06, every fit verdict was right and one quiz answer was scored wrong — by the key, not
  the agent (chapter 04 a2: "margin positions lie outside the window" is correct; key widened). Ratings of the same
  version differ by about one point between replicates: judge by medians of four or more runs.
- **Extractor repairs**: two answers had a `]` closing an object and unescaped quotes inside strings; `extract.py` now
  reads only the final message and repairs both (rebalancing closers, escaping inner quotes); both runs recovered.
- **Chapters 07–10 v2** from notes: 07 (ids checked on return; sheets vs overviews clarified; the 14/13 of 53 figure
  defined, and the annotator sessions where both versions found 9 of 13); 08 (shadowing by save, identity after rename,
  TOCTOU claim softened, parents created inside the root); 09 (extract from the final message only, atomic answers with
  status, run timeouts, a canary test of the seal, reproducible → reconstructible); 10 (headline comparison flagged as
  tuned on its own tiles, multi-class thresholds, review capacity).
- **Chapters 11–13 v1** written and validated (stage A with replicates).
- **Stage B builds**: tasks, hidden tests and references for 03 (`gridflow`, 17 tests), 04 (`stencilpipe`, 9 tests:
  exactness and economy by counted cells), 06 (`shopcli`, 16), 08 (`jailfs`, 18: symlinks, dangling links, identity,
  shadowing), 11 (`labelbook`, 9); every reference passes its tests. Three builders per chapter; builders now keep
  `DIARY.md` in the diary skill's format (`build/DIARY-FORMAT.md`), copied to `builds/` after each stage.
- **Load**: with ~25 concurrent pi processes, lunaroute queues requests; some builders sat on their first request for
  minutes. Not a failure; keep concurrent builders to about a dozen.
- **Playbooks** in `Research/playbooks/`: `validating-design-patterns-with-model-engineering.md` (this method) and
  `extracting-pattern-languages-from-codebases.md` (the pattern-extraction skill adapted to the vault, with this
  validation built into Part 2).

## Step 8 — builds scored, controls, a design review in the spirit of Alexander, Gabriel and Fowler

- **Builds scored** (hidden tests; own tests all green): 03 gridflow b1–b3 17/17 each (after the test fix below);
  04 stencilpipe c1 8/9 (scattered windows cost their bounding box: 40,000 cells for two 8×8 windows); 08 jailfs f1
  18/18, f2 17/18 (a symlinked directory inside the root gave `E_NOT_FOUND`, not `E_ACCESS`), f3 18/18; 11 labelbook
  (chapter v1) e1 8/9, e2 9/9, e3 8/9 (the export sidecar records the export's own inputs, not the makers of the
  exported labels: the chapter's note 8 says "provenance travels in a sidecar" without saying whose).
- **An unfair test.** All three chapter 3 builders failed `test_budget_evicts_and_stays_correct` with zero evictions.
  Each had decided, separately, that an entry larger than the whole budget is not stored (the chapter's note 8 says a
  value too large to cache reports its warnings at once). The test's budget, 200 bytes, was smaller than one 20×20
  grid. Fixed to 20 kB and twelve grids (fits one grid under any size estimate, not thirteen); reference and all three
  builds pass. Agreement among builders is evidence about the yardstick.
- **A script edited mid-batch** (`build.sh`, adding the diary) killed four finished builders before scoring; `after.sh`
  run by hand. New behaviour now goes in new scripts (`control.sh`, `review/review.sh`).
- **Builder feedback folded in** (consensus, two or more of three): chapter 3 — the placeholder must hash to a constant
  and be bound per evaluation, or be substituted at build time (3/3 tripped on the sketch); bounded pools deadlock in
  synchronous hosts (2/3); a cached parent carries the warnings of its whole subgraph (2/3, one shipped the bug
  first). Chapter 8 — containment without `os.Root`/`openat2` by a component walk with `dir_fd` and `O_NOFOLLOW` (3/3);
  links that stay inside the root: decide, refusing all is simpler (3/3 refused all); a fixed order when several
  refusals apply (2/3). Chapter 11 — the fold sketch's undo (3/3) had already been fixed in v2 from stage A notes.
- **Size.** References are 89–159 lines; builds are 566–1,592 lines of source plus as much test code. Whether the
  chapters cause this (participants copied from the Structure table: several builders say it "mapped one-to-one onto
  files") or the model does, the controls will show.
- **New stage** (the user: judge like Richard Gabriel and Christopher Alexander, possibly Martin Fowler; rubric from
  `Research/playbooks/pattern-extraction-with-agent-validation.md` §6): `build/control.sh NN AGENT` runs the task
  without the chapter (two per task, tag `ctl`); `build/review/review.sh NN REV` gives one read-only reviewer the
  chapter, the task, `RUBRIC.md`, a fixed next change (`NEXT-NN.md`) and all builds of the task shuffled into
  `impl-A…` (code and tests only; diaries and notes removed; the key kept outside the reviewer's directory);
  `review/unblind.py NN` joins scores with arms. Chapter 1 gets three fresh builds on v5 (`a3`–`a5`), since the v3
  builds' work directories now hold the extension.
- **Two more unfair tests, found the same way.** Chapter 4: `test_many_windows_equal_cuts` built its comparison node
  on one engine and evaluated it on another; c3 rightly refused a foreign node. Chapter 6:
  `test_host_failure_has_closed_code_and_host_name` demanded `E_HOST` for a margin on a zero price; all three builders
  anticipated the division and refused it as a repairable `E_ARG_RANGE`, which is what the chapter teaches. Both tests
  fixed (the second accepts either a closed host error or an anticipated refusal with a fix); references pass.
- **Scores after the fixes:** 04 c1 8/9 (scattered windows cost their bounding box), c2 8/9 (a cached whole result does
  not serve windows), c3 9/9; 06 d1 15/16 (namespace member not suggested first), d2 16/16, d3 16/16. Four of the
  first six test failures that every builder shared were the yardstick's fault.
- **Reviews by Opus subagents** (the user's choice) instead of pi: `review/prepare.sh NN REV` builds the blind
  directory and keeps the key in `reviews/NN-REV-key.json`; the subagent writes `REVIEW.json`.

## Step 9 — controls and the blind design review (Opus reviewers, Alexander / Gabriel / Fowler)

Six tasks, three builds with the chapter and two controls without it per task; one blind Opus reviewer per task
(`build/review/`, `reviews/NN-o1.json` and keys). Chapter 1 builds are the fresh v5 ones (a3–a5, all 25/25).

**Hidden tests.** Chapter arm 276/282 (98 %), control arm 165/188 (88 %); the chapter arm passes more on every task.
The tests the controls fail are the chapter-only properties: provenance in the export sidecar (11, both controls),
quantised scale and single-flight (03), redirect fixes that run and the namespace-first order (06), cached whole
results serving windows (04), redirect fixes (01). Contested: 08 `test_session_may_replace_its_own_file` contradicts
the task's literal rule ("refuse replacing a file this session read"); both controls followed the task.

**Review scores (means, chapter vs control; rank 1 = best of 5).**

| Task | forces | adapted | wholeness | habitability | growth | smells | tests | rank |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 01 hubreg | 4.0 / 2.5 | 3.7 / 3.5 | 3.0 / 3.5 | 4.0 / 2.5 | 4.7 / 2.0 | 3.0 / 2.0 | 3.7 / 2.0 | 2.0 / 4.5 |
| 03 gridflow | 4.0 / 2.0 | 3.7 / 3.5 | 3.0 / 3.5 | 3.3 / 3.5 | 4.0 / 3.0 | 2.7 / 2.5 | 4.3 / 3.0 | 2.0 / 4.5 |
| 04 stencilpipe | 3.3 / 3.5 | 3.3 / 4.5 | 2.7 / 4.0 | 3.0 / 4.0 | 3.7 / 5.0 | 2.7 / 4.0 | 4.0 / 4.0 | 3.7 / 2.0 |
| 06 shopcli | 3.3 / 3.5 | 2.7 / 4.0 | 2.7 / 4.0 | 3.3 / 2.5 | 3.7 / 3.5 | 2.3 / 2.5 | 3.3 / 4.5 | 3.7 / 2.0 |
| 08 jailfs | 3.7 / 3.0 | 3.0 / 3.5 | 3.0 / 3.0 | 3.0 / 3.5 | 3.0 / 2.5 | 2.7 / 2.5 | 3.3 / 3.5 | 3.3 / 2.5 |
| 11 labelbook | 3.7 / 2.5 | 3.0 / 4.5 | 3.0 / 4.0 | 3.3 / 4.0 | 2.7 / 3.0 | 2.3 / 3.5 | 3.3 / 4.0 | 3.3 / 2.5 |

**Reading.** The chapters transfer forces and tests (forces higher in 4 of 6, hidden tests higher in 6 of 6) and,
for the registry and the lazy graph, better structure (growth 4.7 vs 2.0 and 4.0 vs 3.0; best-ranked builds are all
chapter builds). But in four tasks (04, 06, 08, 11) the controls are judged better adapted and more whole and rank
higher: chapter builds transcribe the Structure table into one module per participant and copy known-use details
from the sketches (`require()` and `E_ARG` into jailfs, receiver lookup and a site tracker into shopcli, the
sketch's 0.6 cost constant and scale conversion into stencilpipe, "decoded sources outside the cap" and key salting
into gridflow, unenforced maker kinds into labelbook). Five of six "worse is better" picks are controls. Chapter
builds are about 24 % larger than controls (mean 1,344 vs 1,087 source lines); both arms are 5–15× the references.
This is Alexander's warning: a pattern read as a template yields structure not adapted to its place.

**Defects shown by probes** (reviewers ran the code on copies): 08 — following note 7, three builds `realpath` the
agent's absolute path (a save writes through an in-root link) and three let writes land in a read root mounted inside
the workspace; 01 — host-decided confirmation does not reach the describers (the assistant is told a guarded action
needs none); 03 — mutable cached values handed to callers, callables keyed by identity serve stale values (the
chapter's own Motivation); 04 — an origin-dependent prefix-sum box makes windows differ from whole results while
tolerance tests pass, and the bounding-box shortcut computes the whole grid for two probes; 06 — fixes that pass
"must bind" by inventing values, and four of five drop the `repeat N:` prefix; 11 — multi-round semantics undefined
(four of five revert to the proposed label when an accept follows a correction), the fold must own the status
vocabulary, and unlocked sequential ids lose a third of the labels under four writers.

**Caveats.** One reviewer per task; three against two builds; one builder model; ordinal scores; blindness partial
(chapter vocabulary remains, deliberately). Next: revise the chapters (responsibilities not modules, optional parts
marked, known-use details out of the sketches, a smallest form, the probe defects), then rerun the same builds,
controls and reviews on the new versions.

## Step 10 — revised chapters (r1): rebuilds and a second blind review

The chapters revised after step 9 (roles, not modules; a Needed column; smallest form first; project specifics out of
the sketches; the probe-confirmed fixes) were frozen as `r1` and rebuilt, three builders per task; the controls are
the same as in step 9. One blind Opus reviewer per task again (`reviews/NN-o2.json`, keys beside them).

**Hidden tests.** r1 chapter builds 275/282 (v-round 276/282; controls 165/188). Two regressions shared by all
three builders, both caused by the revision's conditional wording: chapter 3 dropped single-flight ("only when there
are concurrent callers"; the task never says so), chapter 4 dropped the cut-from-whole path ("only when whole values
are cached"). Chapters 6, 8 and 11 went to 48/48, 54/54 and 27/27. Builds shrank for 03 (1,245 → 963 lines), 04
(923 → 744) and 08 (1,195 → 888); grew for 11 (784 → 1,237) and 01 (2,137 → 2,300).

**Design review, chapter arm (mean rank among five, 1 best), round 1 → round 2:** 01 2.0 → 2.0; 03 2.0 → 2.7;
04 3.7 → 3.3; 06 3.7 → 2.0; 08 3.3 → 2.0; 11 3.3 → 2.0. The top-ranked build is a chapter build in five of six tasks
(was two); chapter builds take the top three in 01, 06, 08 and 11. Adapted and wholeness narrowed but chapter builds
still trail controls on "adapted" in four tasks; the chapter 11 reviewer saw near-identical docstrings across the
chapter builds ("transcribed rather than generated"). Chapter 8: all three chapter builds now avoid both security
holes; the only build with both is a control.

**Caveat.** The controls are the same code in both rounds, yet their scores moved (06 control mean rank 2.0 → 4.5):
reviewers rank within the set, so a better set pushes the same control down. Read round-to-round changes as about one
point of noise; the convergent findings (which builds have which bugs) are firmer than the scores.

**Text fixes after round 2 (no rerun):** chapter 4 makes the cut-from-whole step unconditional; chapter 3 asks
"can two requests for one value overlap?" instead of "concurrent callers", and keys on an operation's registration,
not only its declared version (a reviewer reproduced stale values after re-registration with the same version);
chapter 1's walker runs against a test host, never a live one (all five hub self-tests actuated every action).
Patterns are done for now unless something egregious turns up.
