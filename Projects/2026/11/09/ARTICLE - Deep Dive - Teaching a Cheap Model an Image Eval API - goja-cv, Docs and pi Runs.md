---
title: "Deep Dive: Teaching a Cheap Model an Image Eval API — goja-cv, Docs and pi Runs"
aliases:
  - goja-cv agent iteration
  - goja-cv pi runs
  - Eval tool API iteration with pi and deepseek
tags:
  - article
  - deep-dive
  - agents
  - llm-tools
  - computer-vision
  - goja
  - go-go-goja
  - mcp
  - api-design
  - evaluation
status: active
type: article
created: 2026-11-09
repo: /Users/manuel/code/wesen/go-go-golems/goja-cv
---

# Deep Dive: Teaching a Cheap Model an Image Eval API — goja-cv, Docs and pi Runs

This note records how the agent-facing surface of `goja-cv` was shaped by watching a real, inexpensive model
use it. `goja-cv` is a Go image-analysis engine that an LLM agent drives through a single JavaScript `eval`
tool, served over MCP. Over one night we ran the `pi` coding agent with `lunaroute/deepseek-4.1-flash` against
it six times on an image with known ground truth, read every failed tool call, decided for each one whether
documentation or the API was at fault, fixed it, and ran again. The note explains the system first, then the
experiment, then each round, and ends with the rules that generalize to any "eval as a tool" API.

> [!summary]
> - The model answered all five questions correctly in every run; what changed was **how much it struggled**: tool calls fell from 30 to about 20 and errors from 6 to 2–5 — and by the last round every error was a structured message with a hint or a literal fix that the model followed on its next call.
> - **Documentation reachable through the tool** (`cv.docs.search/read`) removed the single largest error class. Docs only in a resource or a system prompt the model never sees would not have.
> - Most remaining errors were **API defects disguised as model mistakes**: a help function that throws, data that forgets where it came from, a missing "stats inside a box", option names that differ from the model's vocabulary.
> - Every error message should carry a **literal fix**. The model copies it.

## Why this note exists

When you give an agent a code-eval tool instead of a fixed set of functions, the API is the prompt. Every name,
every error message and every return shape is something the model reads and reacts to. That makes API quality
measurable in a way it usually is not: run the agent, count tool calls and errors at equal correctness, and
look at each failure. This note preserves the method, the concrete findings, and the design rules that came
out of it, because the same loop applies to any domain-specific eval API.

## The system in one page

An agent has one tool, `eval`. It sends the body of an async JavaScript function; the system runs it in a
persistent session and returns a YAML rendering of the returned value, any images the code returned, and a
short context block.

```
 pi (deepseek-4.1-flash)
   │  tool call: cv_eval { code }                       ┌───────────────────────────────────────────┐
   └──────────── pi-mcp-adapter (stdio) ───────────────▶│ goja-cv mcp                               │
                                                        │   replmcp (go-go-goja) ── replapi/session │
   ◀── text: YAML result + warnings + context ─────────│   goja VM: prelude.js → require("cv")     │
   ◀── image content: looks (JPEG/PNG)  ───────────────│   Go engine: graph, evaluator, kernels    │
                                                        └───────────────────────────────────────────┘
```

The language the agent writes is called `cv`. Its core idea is that calls build a graph rather than compute
pixels:

```js
const specks = img.detect.specks({ maxArea: 120 })        // a Regions node; nothing has run
const dust   = specks.where({ score: { gte: 0.5 } })      // another node
const healed = img.heal(dust, { radius: 3 })               // an Image node
return {
  count: await dust.count(),                                // evaluation happens here
  check: await healed.check.dust(),                         // and here
  view:  cv.compare([img, healed], { mode: "side" }).look("before / after"),  // an image result
}
```

Four properties matter for the rest of the note:

- **Nodes are lazy and typed.** `img.detect.specks()` returns a `Regions` node; `await` turns it into plain
  data (`{ count, items: [...] }`). Pixels never cross into JavaScript.
- **Images are returned as values.** `node.look()` returns a Go object implementing
  `resultcontent.Provider` (a go-go-goja interface added for this project); the MCP layer sends it as image
  content, numbered and captioned with its scale (`look 1: specks (256×192, 1 image px = 1.0 doc px)`).
- **Errors are structured**: `code`, `message`, `where` (the agent's line), `path` (the graph path), `hint`,
  `fix`.
- **The session persists**: `mem` holds values between evals.

The design came from comparing nine independent prototypes of the same prompt (ticket CVJS-001 in the
dust-scanning repo); this note picks up after the first working build of `goja-cv mcp`.

## The experiment

### Ground truth first

The test image is a synthetic 256×192 16-bit "film scan" generated by goja-cv's own test code. It has a
smooth gradient, sensor-like noise, 40 hard-edged dust specks at known positions (30 dark, 10 bright, some
elongated), and one soft round bright "star" that is not dust. Because the image is generated, every question
has an exact answer:

| question | ground truth |
|---|---|
| size, bit depth, exposure | 256×192, 16-bit; low clipping |
| how many specks, how many dark/bright | 40; 30 dark, 10 bright |
| a bright feature that is not dust | the star at (200.5, 46.5), σ 2.2 |
| the largest speck | bright, elongated, centred near (155, 135) — detector id 31, box [147,133,15,5] |
| heal the dust, keep the star | `check.dust()` clean; star unchanged |

The questions were given verbatim in every run, with one instruction: measure with cv, do not guess from the
picture.

### The harness

`scripts/06-pi-cv-agent/run.sh` (in the CVJS-001 ticket) builds goja-cv, generates the image, writes a
project `.mcp.json`, and runs pi headless:

```json
{ "mcpServers": { "cv": {
    "command": "<out>/goja-cv",
    "args": ["mcp", "--image", "<out>/img/planted-256x192-16bit.tif", "--root", "<out>/img"],
    "lifecycle": "keep-alive",
    "directTools": ["eval"] } } }
```

```bash
pi -p --mode json -a --mcp-project-servers allow \
   --no-builtin-tools --no-context-files --no-skills --no-prompt-templates \
   --session-dir "$OUT/session" --model lunaroute/deepseek-4.1-flash \
   --append-system-prompt "You have a cv image-analysis MCP server. Use its eval tool for every measurement and edit." \
   "$(cat questions.md)" < /dev/null > "$OUT/events.jsonl"
```

Three settings carry the experiment's validity. `--no-builtin-tools` removes pi's file and shell tools, so
every answer must come through cv. `directTools: ["eval"]` exposes the server's tool as a first-class pi tool
(`cv_eval`) instead of behind the adapter's search proxy. `lifecycle: keep-alive` keeps one server process,
so `mem` survives between calls.

Each run was graded against the table above and then dissected: a small script prints every call's code and
result from the event log, and `go-minitrace convert pi` turns the session into a queryable archive
(`tool_calls` with position, success, duration).

### The harness bugs, because they will recur

Four failures happened before the first valid run, and each is a general trap for headless agent runs:

- **pi waited on stdin.** In print mode with an inherited open stdin it sat idle at 0% CPU. Fix: `< /dev/null`.
- **An empty prompt.** `HERE=$(cd "$(dirname "$0")" && pwd)` captured two lines because `cd` on a relative
  path echoes the directory when `CDPATH` is set; `cat $HERE/questions.md` failed and pi got an empty
  message. Fix: `unset CDPATH` and `CDPATH= cd -- …`.
- **A wait loop that exited at once.** `while pgrep -f "pi-run-03/session"` never matched because pi renames
  its process title to `pi`. Fix: wait on the run's own PID.
- **The image generator does not create its output directory.** Fix: `mkdir -p` first.

## Run 1: no documentation

Build: goja-cv before `cv.docs`. The agent had the MCP server instructions, `cv.help()` (op reference
generated from the registry) and nothing else.

Result: **all five answers correct, 30 calls, 6 errors.** The answers were good — it found the star, explained
why it is not dust (score 0.00, sharpness 0.30 against a dust mean of 0.67, aspect 1.01, a smooth radial
profile), named speck 31 as the largest dust speck, healed, and verified the star was bit-identical. The
path there was the interesting part.

**Eleven of thirty calls were API discovery**: `cv.help("stats")`, `cv.help("detect.specks")`,
`Object.keys(cv)`, `Object.getOwnPropertyNames(Object.getPrototypeOf(r))`. With no searchable documentation,
the model reverse-engineered the API.

**Four of six errors were one misunderstanding.** The model awaited a node and then kept using the result as
a node:

```js
const r = await img.detect.specks({ polarity: 'both' });
const dust = r.where({ score: { gte: 0.5 } });     // TypeError: Object has no member 'where'
```

`await` had turned the node into plain data, which has no `where`. The same shape appeared with `r.filter`,
`r.explain()` and `img.overlay(r)` (`E_WRONG_KIND: overlay needs a Regions|Mask node as argument 1, got an
object`). The goja error said nothing useful.

**Two errors came from `cv.help` throwing.** The model batched lookups —
`return [cv.help("open"), cv.help("explain"), cv.help("Image")]` — and the one name that was not an op
(`"Image"`, later `"mask.stats"`) threw and discarded the whole batch.

**Two workarounds revealed missing API.** To measure the brightness profile of the star the model wrote

```js
const kept = img.within(m.not(), i => i.exposure(-10)).stats()   // darken everything outside the box
```

because there was no way to compute statistics inside a box. And to answer "bit depth" it measured histogram
quantization to prove the data was more than 8 bits, because nothing reported the file's bit depth.

## Run 2: documentation as part of the tool

Between runs, goja-cv gained `cv.docs`: nine short Markdown topics embedded in the binary (getting started,
units and scales, nodes and evaluation, lambdas, masks and regions, looks, params, errors, recipes), reachable
from inside eval:

```js
cv.docs.list()                              // [{ id, title, summary }]
cv.docs.search("heal dust", { limit: 3 })   // [{ id, title, section, snippet, score }]
cv.docs.read("recipes", { section: "Remove dust" })
```

The MCP server instructions were cut to a compact reference (about 2,500 characters) that ends with "use
`cv.docs.search` / `cv.docs.read` for more". Every JavaScript block in the topics is executed by a test, so
the docs cannot describe an API that does not exist.

The design choice — docs as functions of the eval scope rather than only an MCP resource or a long system
prompt — came from an agent design system that exposes `book.search(text)` and `doc(id)` inside its eval
scope. The reasoning: a client may not show resources to the model at all, and the eval tool is the one
channel guaranteed to reach it.

Result: **all correct, 30 calls, 5 errors.** The call count did not move, but the composition did:

- The model read five topics early (`getting-started`, `list`, `recipes`, `masks-and-regions`,
  `units-and-scales`).
- **The await misunderstanding disappeared** (4 → 0). It kept nodes and awaited only to read data, as the
  getting-started topic shows.
- It wrote idiomatic chains: `dust.sortBy("area").top(3)`, `check.dust().maxArea`,
  `blend(img, healed, { mode: "difference" })`.

New and remaining problems:

- **`cv.help` still threw** on names the model found natural: `"evaluate"` (a cv function, not an op),
  `"Mask.coverage"`, `"Regions.filter"`, `"Regions.explain"` — the `Kind.method` form. Three errors.
- **The model invented a session id.** The eval tool's schema had an optional `sessionId`; on its second call
  the model passed `"sessionId": "probe"` and got the raw internal error
  `evaluate in session probe: replsession: session not found`.
- **Both workarounds persisted** (stats in a box, bit depth), now via a different hack: luminance masks
  intersected with box masks and their coverage.

## Error classification

After two runs, every error belonged to one of three classes, and each class has a different fix:

| class | example | right fix |
|---|---|---|
| **concept the model lacks** | using awaited data as a node | documentation the model can find — and then make the API forgive it |
| **API that punishes reasonable use** | `cv.help("Image")` throwing; an optional `sessionId` with no explanation | change the API |
| **capability that is missing** | stats inside a box; bit depth | add the capability |

The first class is the only one documentation can fix, and even there the API can do better. The other two
look like model mistakes in a transcript but are design defects: the model did something sensible and the API
refused it.

## API round 1

Fixes made in goja-cv (and one in go-go-goja's `replmcp`), each with a test that replays the failing call
verbatim:

1. **`cv.help` never throws.** It accepts op names, kind names (`"Mask"` lists its methods), `Kind.method`,
   cv functions and globals, with or without a `cv.` prefix. An unknown name returns
   `{ found: false, didYouMean, hint }`, and `"mask.stats"` points to the new stats-with-mask call.
2. **Awaited data keeps a link to its node.** The awaited object carries a hidden symbol and the node's
   methods as non-enumerable properties, but only where the data has no field of that name. So
   `r.where(…)`, `r.filter(…)`, `r.explain()`, `img.overlay(r)` and `img.heal(r)` work on awaited data, while
   `Object.keys`, JSON and the YAML result are unchanged. The alternative, a structured error with a fix, was
   rejected because "await, then reuse" is natural JavaScript and the model kept doing it.
3. **`img.stats({ mask })` and `img.stats({ box: [x, y, w, h] })`**, weighted by the mask, with the same
   output shape plus `area` and `coverage`, and a "measure inside a box or region" recipe.
4. **Image metadata.** `await img` reports `file`, `format`, `bitDepth`, `fileChannels`, `colorSpace`; the
   context block shows `img = planted-256x192-16bit.tif (256×192, 16-bit TIFF)`.
5. **Unknown session ids** produce a tool error that lists the existing sessions and says to omit
   `sessionId`; the schema now says "Optional; omit it to use the default session … only pass ids returned by
   create_session or list_sessions."
6. **A concurrency bug.** Run 1 had one error whose `where:` line quoted text that was not in that eval. pi
   sends tool calls in parallel; two evals' sources could be swapped before the session ran them. Evals are now
   serialized per session; a 12-way concurrent test failed before and passes after.

The sixth fix is worth dwelling on. The bug existed from the first build, every unit test passed, and only a
real client with real parallel tool calls exposed it. Agent runs are integration tests that humans do not
write.

## Runs 3 and 4

Two runs on the same build, in parallel, to see variance.

Result: **all correct in both; 23 and 20 calls; 4 and 3 errors.** About a third fewer calls than runs 1–2. The
model used `img.stats({ box })` for the star profile, read `await img` for the bit depth, and its help lookups
stopped failing.

The remaining seven errors were small and, again, recurring:

- **A collision created by fix 2.** `const n = await specks.count()` after `specks` had been awaited:
  `r.count` is the data field (a number, 41), which shadows the node method `count()`. goja reported
  `TypeError: Value is not an object: 41`. Forgiveness in one place had created a new sharp edge.
- **Awaited `top(n)` used as an array**: `rows.slice(0, 3)` on `{ count, items }`.
- **Option vocabulary**: `img.mask.luminance({ min: 0.99 })` in both runs. The error already listed the valid
  options (`above, below, softness`); the model wanted the word it used.
- **Unknown names on `cv` itself**: `await cv.info()` produced a raw TypeError, because the `cv` object had no
  did-you-mean.
- **`color: "lime"`**, which is a CSS colour.

## API round 2

1. **Raw TypeErrors on cv data become structured errors.** When awaited data has a field that shadows a node
   method, the eval records it; on the TypeError the processor finds `<receiver>.count(` on the failing line
   and adds: *"After await, specks is data: specks.count is a number (41), not a method. Read it, or call
   count() on the Regions node before awaiting it."* with `fix: specks.count`. Awaited Regions get hidden
   array methods (`slice`, `map`, `forEach`, …) that throw `E_NOT_ARRAY` with `fix: rows.items.slice(…)`.
2. **Semantic option synonyms**, checked before edit distance: `min` → `above`, `max` → `below`,
   `threshold` → `above`, `radius`/`sigma` → `r`, `opacity` ↔ `alpha`, `rect`/`roi` → `box`. The fix keeps the
   agent's value: `mask.luminance({ above: 0.99 })`.
3. **`cv` and `P` give structured unknown-name errors** with did-you-mean: `cv.info` → `await img   // or
   cv.describe(img)`; `cv.stats` → "`stats` is an Image method", fix `img.stats(…)`.
4. **CSS colour names and `#rgb`/`#rrggbb`** in every colour argument.

## Runs 5 and 6

Two more runs, in parallel, on the round-2 build.

Result: **all correct in both; 40 and 19 calls; 5 and 2 errors.** Run 5 is the outlier in effort: it re-verified
everything, ran a second "loose" detection to look for faint specks it might have missed, and profiled the
star three different ways. Its answers were the most thoroughly justified of all six runs. Run 6 was the
leanest run so far.

What changed is the *character* of the errors. Every one was a structured cv error, and in every case the
next call fixed it:

| run | call | what the model wrote | what it got back |
|---|---|---|---|
| 5 | 2 | `await cv.eval ? null : null` | `E_UNKNOWN_METHOD: cv has no "eval"` (feature-detection on `cv` now throws, by design) |
| 5 | 9 | `const n = await s.count()` on awaited data | `TypeError … 41` with `fix: s.count` |
| 5 | 14 | `img.mask.luminance({ min: 0.95 })` | `E_UNKNOWN_OPTION` with `fix: mask.luminance({ above: 0.95 })` |
| 5 | 19 | `img.overlay([{ box: [...], label: "…" }])` | `E_WRONG_KIND: overlay needs a Regions\|Mask node as argument 1, got a list` |
| 5 | 25 | `healed.detect.specks(…)` in a later eval | `ReferenceError` with hint *"Top-level const/let do not survive between evals; keep values in mem"* |
| 6 | 5 | `await img.exposure()` | `E_ARG_TYPE: exposure is missing its ev argument` |
| 6 | 17 | `img.within(healed)` | `E_WRONG_KIND: within needs a Mask as argument 1, got an Image` |

Three of these are the model probing or slipping (`exposure()` without an argument, `within` with an image). Two
are the old patterns, now caught with a fix (`count()` on data, `min`). Two point at new, small API questions:
whether `overlay` should accept a plain list of boxes for ad-hoc annotation, and whether `cv` should
tolerate `cv.x ? … : …` feature checks instead of throwing.

The spread between run 5 (40 calls) and run 6 (19) on the same build is the clearest evidence in this note
that single runs are noisy. Calls per run measure friction only roughly; errors per call and whether each
error is recovered in one step are steadier signals.

## Results

| run | build | calls | errors | correct | what changed before the run |
|---|---|---|---|---|---|
| 1 | first MCP build | 30 | 6 | 5/5 | — |
| 2 | + `cv.docs`, compact instructions | 30 | 5 | 5/5 | docs reachable from eval |
| 3 | + API round 1 | 23 | 4 | 5/5 | help never throws, awaited data keeps node, stats in box, metadata, session errors, per-session lock |
| 4 | same as 3 | 20 | 3 | 5/5 | |
| 5 | + API round 2 | 40 | 5 | 5/5 | TypeError translation, option synonyms, did-you-mean on `cv`/`P`, CSS colours |
| 6 | same as 5 | 19 | 2 | 5/5 | |

Two caveats keep these numbers honest. Each configuration has one or two runs, and the model's path varies
between runs on the same build (runs 5 and 6 differ by 21 calls). And correctness never varied — the
questions were answerable on the first build. The measurement is effort and friction, not capability.

## Rules that generalize

These held across every round and apply to any eval-style tool API.

**Put documentation inside the tool.** A model reads what it can query through the channel it is using. In
run 1 it spent a third of its calls on discovery; in run 2 it read five topics and stopped making the
dominant mistake. Searchable topics with runnable examples beat a long system prompt that the client may
truncate and a resource the client may not show.

**Never throw from a discovery function.** Models batch lookups. A help function that throws on an unknown
name discards every other answer in the batch. Return `{ found: false, didYouMean }` instead.

**Every error carries a literal fix.** The most effective errors in these runs were the ones with a `fix:`
line the model could copy: `fix: mask.luminance({ above: 0.99 })`, `fix: rows.items.slice(…)`. A list of valid
options is good; the exact corrected call is better.

**Translate the runtime's errors into the API's language.** `TypeError: Value is not an object: 41` is a
correct statement about JavaScript and a useless one about the API. Where the failing expression involves the
API's own objects, rewrite the error in the API's terms.

**Accept the model's vocabulary.** `min`, `max`, `threshold`, `lime`, `Kind.method` and `cv.info` are not
errors of reasoning; they are reasonable words. Synonyms that map to the canonical name, and did-you-mean on
every object the agent can touch, are cheap.

**Watch the workarounds, not only the errors.** The two biggest capability gaps (stats in a region, file
metadata) never produced an error. They showed up as strange code — darkening the whole image by ten stops
to isolate a box — which only reading the transcript reveals.

**Every forgiveness creates an edge.** Making awaited data carry node methods removed four errors and created
a name collision that produced two new ones. Keep replaying old failures as tests after each change.

**Optional parameters invite invention.** An optional `sessionId` with no explanation was filled with
`"probe"`. Describe optional parameters in the schema, say when to omit them, and make the error for a bad
value explain the recovery.

**Real clients find real bugs.** Parallel tool calls exposed a source-swapping race that no unit test had
covered. Run the agent early.

## Where things are

- Engine and MCP server: `/Users/manuel/code/wesen/go-go-golems/goja-cv` (`pkg/cvsession`, `pkg/cv/docs/topics`,
  `pkg/gojamod/cv/prelude.js`, `cmd/goja-cv`); remote `go-go-golems/goja-cv`.
- Result content, `replmcp`, `goja-repl mcp`, xgoja `mcp` command set: go-go-goja PR #108
  (branch `task/cvjs-001-resultcontent-replmcp`).
- Ticket with design docs, the intern guide, diaries for every agent, the harness and all runs:
  `/Users/manuel/code/wesen/2026-11-07--dust-scanning/ttmp/2026/11/08/CVJS-001--js-eval-cv-api-for-agents-compare-9-implementations/`
  - harness: `scripts/06-pi-cv-agent/run.sh`, `questions.md`, `planted-truth.json`
  - summaries: `scripts/07-pi-events-summary.py`
  - runs: `various/pi-runs/` (session JSONL, HTML transcript, per-call summary per run; `README.md` table)

To reproduce a run:

```bash
T=ttmp/2026/11/08/CVJS-001--js-eval-cv-api-for-agents-compare-9-implementations
$T/scripts/06-pi-cv-agent/run.sh ~/code/wesen/go-go-golems/goja-cv /tmp/pi-run-N
python3 -I $T/scripts/07-pi-events-summary.py /tmp/pi-run-N/events.jsonl --errors-only
go-minitrace convert pi --source-session /tmp/pi-run-N/session/*.jsonl --output-dir /tmp/mt
```

## Open questions

- The test image is easy (SNR ≥ 17). A real film-scan crop from the DUST-001 dataset, with ground truth from
  Lightroom heals, is the next test.
- One model, one thinking level (pi's default `xhigh`). A smaller or faster model, or lower thinking, would show
  which fixes matter most when the model is weaker.
- The hand-written parts of the agent surface (the "most used calls" in the instructions, the synonym table,
  the help redirects) can drift from the registry; only phrase tests guard them.
