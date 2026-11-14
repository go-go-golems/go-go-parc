---
title: One Eval Tool over a Scripted Session
aliases:
  - Code as the agent's action
  - Eval tool with a session
  - Scripted session with layered libraries
status: established
type: architecture-garden-pattern
created: 2026-11-14
tags:
  - architecture-garden
  - patterns
  - agents
  - mcp
  - goja
related_notes:
  - "[[00-overview|Agent-Operated Engines - A Pattern Language]]"
---

# Chapter 5 · One Eval Tool over a Scripted Session

*The agent sends small programs to a persistent session through one tool, and reads back capped text, a context
block and pictures; task libraries load into the session in layers.*

Rating: ★ (a good form among several; the variations name the others; see the overview).

## Intent

Give an agent one tool that runs a short program against the engine's API in a session that persists between calls,
and return what the program produced in a form the agent can read: text with a size limit, tables for lists of
records, a block that reminds the agent what the session holds, and the pictures the program made. Let task-specific
helper libraries load into the session in layers, instead of being pasted into programs.

## Also known as

Code as action (CodeAct), eval tool, REPL tool, notebook kernel for agents.

## Motivation

An agent inspecting a scan needs dozens of operations, combined freely: open, convert, filter, crop, measure, sort
the results, draw the best twelve. Offering each operation as a separate tool fails in three ways. The agent must
make one round trip per step; it cannot loop over a list of candidates or filter results without another round trip;
and the tool list grows with the catalogue until it crowds the context. goja-cv and the Editor lab both chose one
tool, `eval`, that runs a JavaScript function body with the engine's API in scope and returns the value as YAML. In
one eval an agent can find candidates, keep the twelve strongest and return a contact sheet of them.

One tool raises its own problems, and the originating projects met each of them:

- **State vanished between calls.** In goja-cv, top-level `const` and `let` declarations do not survive into the next
  eval; code later in a session could not see constants declared earlier. State has to live on an explicit object
  (`mem`).
- **Libraries were pasted.** Thirty-nine annotator agents each pasted a 3.2 KB helper file into their first eval,
  because the session had no way to load it; ten trimmed it, and code later in the session could not see its
  top-level constants. Of 374 evals, 39 were pastes.
- **Output was lost or overwhelming.** goja-cv v1 dropped pictures created by a bare `x.look()` statement, and a
  result that returned a whole array of regions could exceed what the agent could read.
- **Documentation went unread.** The same 39 agents never called `cv.docs` or `cv.help`; they learned from the
  helpers and from results.

The shape recurs wherever a model drives a system with many operations:

- A **data-analysis assistant** runs Python against loaded tables in a sandboxed kernel.
- A **database agent** sends SQL and reads result sets, with session variables and temporary tables.
- An **infrastructure agent** runs commands in a shell session with credentials and a working directory.

## Problem

**An agent that drives a large engine through one tool call per operation cannot combine, loop or filter without
round trips, and an agent that sends programs instead loses state, floods its context or misses what its programs
made unless the session and its results are designed for it.**

## Forces

- **Expressiveness against safety.** A general program can do anything the API allows, including mistakes that a
  narrow tool would prevent.
- **Persistence against reproducibility.** State that survives between calls saves work, and makes a call's result
  depend on everything before it.
- **Completeness against the context budget.** The agent needs to see results, but every character and every picture
  displaces something else in its context.
- **Generic session against domain needs.** A REPL session is generic; images, warnings and domain-specific context
  are not.
- **Loading against inlining.** Libraries loaded by the session are invisible in the transcript unless the session
  says what it loaded; pasted code is visible and wasteful.

## Solution

**Therefore: give the agent one tool that runs a program in a persistent session with the engine's API in scope, and
make state explicit: one named object holds whatever must survive between calls. Build the session from two parts: a
generic runtime that executes, times out and persists, and a domain result processor that turns what a program
returned and created into the reply. The reply holds text capped at a fixed size with a note saying how to get the
rest, lists of flat records rendered as tables, the warnings raised with their line numbers, a context block rebuilt
on every call (what the session holds, which helpers exist and what changed since the last call), and every picture
the program created, within a budget, with a placeholder naming any that were left out. Load task libraries into the
session as preludes or by name, in layers; let each helper describe itself from its own source.**

## Applicability

Use it when:

- the agent needs many operations of one engine and combines them in data-dependent ways (loops, filters, sorts);
- results are large or structured and must be summarised before the agent reads them;
- the engine has state worth keeping between calls (opened inputs, cached values, loaded helpers).

Do not use it when:

- the agent needs a handful of independent actions with side effects that must each be confirmed; separate, narrow
  tools make each one visible and reviewable;
- there is no sandbox that can contain programs; then do not run model-written code at all, and offer narrow
  structured tools instead (the reply format of this pattern still applies);
- every call must be reproducible on its own (an audit-grade API); a stateless call with explicit inputs fits better.

## Structure

| Participant | Responsibility |
| --- | --- |
| **Eval tool** | The one tool: takes a program, returns the reply. Its description states the contract in a few clauses: the language and what a program is (a function body, async or not); how to get a value back (`return`); the cap on replies; how attachments are made; where state must live; how to load libraries and find help. |
| **Session** | A persistent runtime: executes programs one at a time (a second call waits), enforces the deadline, owns the state object and the loaded libraries, applies policies (read-only, persistence). |
| **State object** | The named object (`mem`) that survives between calls; anything else is local to one program. It holds data and the helper functions libraries install; the context block lists the two separately. The agent removes what it no longer needs (`delete mem.x`). |
| **Result processor** | Domain plug-in to the session: before each call it resets per-call state; after it, it renders the value, warnings, context block and attachments; on failure, it renders the error with the line and whatever was created before it. It remembers which helper sources it has already shown. |
| **Context block** | Rebuilt on every call, within its own small budget: named inputs, the state object's data keys with their kinds, helper functions with signatures, libraries available to load, and full doc lines only for helpers that are new or whose source changed (by hash) since the last successful call. |
| **Attachment queue** | What the program made for the agent to see: pictures, charts, rendered tables. Delivered in order within a count and byte budget, each once, whether or not the program also returned it. Files it saved stay in the workspace and are named in the reply. An engine without pictures has an empty queue, not a different pattern. |
| **Library loader** | Loads helper libraries at session start (preludes, in order) or on demand by name; libraries install helpers on the state object. Preludes produce no output. A prelude that fails stops the session from starting, and the tool's start-up error names the file, the line and the message. |

## Collaborations

1. The session starts and runs the preludes in order, a general library then a task library built on it.
2. For each call, the processor resets its per-call state; the session runs the program under its deadline.
3. Operations raise warnings with their call sites; attachments the program makes join the queue.
4. The processor renders the reply: the value, capped, with tables; warnings folded by line; the context block;
   attachments within the budget, naming any left out. On failure, the same reply with a structured error in place of
   the value (see [Chapter 6](06-repairable-errors.md)).

```mermaid
sequenceDiagram
  participant A as Agent
  participant T as eval tool
  participant S as Session (generic)
  participant P as Result processor (domain)
  A->>T: program
  T->>S: run with timeout
  S->>P: before-hook (reset per-call state)
  S->>S: execute; warnings and pictures recorded
  S->>P: process(value) or processFailure(error)
  P-->>T: capped text + tables + warnings + context + pictures
  T-->>A: reply
```

## Sketch

```text
-- the generic session and its plug-in seam
interface ResultProcessor:
  beforeEval(runtime)                          -- reset per-call state (attachments, warnings)
  process(runtime, value)  → Reply
  processFailure(runtime, error) → Reply

session = Session(runtime, processor, policy: {timeout: 30s, readOnly: false},
                  preludes: ["helpers.js", "judge-helpers.js"])      -- layered; output discarded

evalTool(program) → Reply                                         -- calls are serialised: one program at a time
  processor.beforeEval(runtime)
  try:   v = runtime.run(asyncBody(program), deadline: now() + policy.timeout)   -- the session owns the deadline
         return processor.process(runtime, v)
  catch e: return processor.processFailure(runtime, e)

-- the domain processor
process(runtime, v) → Reply
  text = yaml(v, tables: arrays of ≥ 2 flat records, tableBudget: ⅔ × CAP)
  if v is undefined: text = "nothing returned: end the code with `return …` to see a value"
  text = cap(text, CAP, note: "cut at N of M chars; return fewer fields or rows")   -- CAP bounds the value
  text = text ++ foldByLine(warnings()) ++ contextBlock(runtime)   -- short by construction: folded, deltas
  atts, left = budget(unique(queue()), maxCount: 4, maxBytes: 8 MiB)   -- each attachment once
  for a in left: text = text ++ warning(LOOKS, "not delivered: " ++ a.line)
  return Reply(text, atts)

contextBlock(runtime) → text                                       -- its own budget, a few hundred characters
  inputs  = named and unnamed opened inputs, one line each
  state   = [key ++ ": " ++ kindOf(mem[key]) for key in mem if not isFunction(mem[key])]   -- never call getters
  helpers = [signature(f) for f in functions(mem)]                  -- helpers installed by libraries or the agent
  docs    = [docLine(f) for f in functions(mem) if seen[f.name] ≠ hash(source(f))]
  for f in functions(mem): seen[f.name] = hash(source(f))           -- updated after successful calls only
  return fit(inputs ++ state ++ helpers ++ docs ++ ["libraries: " ++ join(loadable())], CONTEXT_BUDGET)

-- in use (one call)
mem.cands = (await img.as("linear").peaks({ snr: 1 })).filter(p => !p.edge).slice(0, 12)
return cv.sheet(mem.cands).look("top 12")
```

## Implementation notes

1. **Make state explicit.** Whatever survives between calls should live in one documented object, listed in every
   context block. In runtimes that evaluate each program as a function body (goja-cv's JavaScript), top-level
   declarations vanish after the call; goja-cv agents who pasted helpers found the helpers' constants gone in the
   next eval. Runtimes that keep a namespace (a Python kernel) do not lose them, but a named state object still makes
   what persists visible.
2. **State the contract in the tool description.** goja-cv's reads: "Run JavaScript against the cv image API in a
   persistent session. The code is the body of an async function: use await, and return what you want to see
   (rendered as YAML, max 9000 chars). node.look("label") attaches an image (every look of an eval is delivered).
   Top-level const/let do not survive between calls; store values on mem. Task libraries: await cv.load(path, args);
   cv.scripts() lists them." Each sentence answers one of the contract's clauses; the names are goja-cv's own.
3. **Separate the generic session from the domain processor.** go-go-goja's `replsession` runs programs, enforces
   timeouts and persists sessions, and accepts a result processor with a before-hook and a failure hook; goja-cv's
   `cvsession` is such a processor, plugged in without changing the session. Keep anything domain-specific (looks,
   frames) out of the generic part, so the next engine can plug in the same way.
4. **Cap the text and say how to get the rest.** Both goja-cv and the Editor lab cap the rendered value at 9,000
   characters, a default chosen for current models' context windows, not a measured optimum. The lab appends "Return
   less: pick fields, slice arrays"; goja-cv cuts at a line boundary and gives tables two thirds of the budget, each
   with a note on which rows are shown. Warnings and the context block come after the cap and stay short because they
   are folded and incremental.
5. **Render lists of records as tables.** Agents filter and sort results in plain code; a list of flat records shown
   as a header line and one line per record is far more compact than nested YAML and easier to scan.
6. **Rebuild the context block on every call, and show deltas.** goja-cv lists inputs, state keys and helper
   signatures each time, but prints a helper's doc line only when the helper is new or its source changed. The
   block costs a few lines per call and keeps the agent from guessing what exists.
7. **Deliver every picture the program created.** goja-cv v1 delivered only returned pictures, and silently dropped
   `x.look()` used as a statement. v2 delivers everything created, returned ones first, and names by line any that
   exceed the per-call budget (four pictures, 8 MiB).
8. **Load, don't paste.** goja-cv added `--prelude` files and `cv.load(name)`, and lists loadable scripts with
   `cv.scripts()`. Libraries stack: the dust pipeline's judge runs load the general dust helpers first, then judge
   helpers that build on them. Prelude output is discarded, because no one reads it.
   Helpers describe themselves: a helper's parameter list and the first comment of its body, read from its
   source, become its line in the context block; the helper's author documents it once, where it is written.
9. **Failures, timeouts and empty results are replies too.** Render the structured error with the line in the
   agent's program, and still deliver the pictures and warnings produced before the failure. A timeout is a failure
   (`E_TIMEOUT`); state assigned before it persists. If the interrupt left the runtime unusable (goja cannot run
   promise jobs after an interrupt inside a resumed async function), goja-cv detects it and says to start a new
   session. A program that returns nothing gets a one-line reminder to `return` a value.
10. **Put the next step in the reply, not in documentation.** Agents did not read goja-cv's documentation; they read
    results. Hints, fixes and warnings in the reply (see [Chapter 6](06-repairable-errors.md)) reach them; a manual
    does not.
11. **Lints must be precise or absent.** goja-cv's `UNUSED_NODE` lint fired 19 times in the annotator study, 18 of them
    on correct code, and was deleted. A warning that is usually wrong teaches agents to ignore warnings.

## Variations

- **Many narrow tools** (one per operation, structured arguments). Each call is visible and validated by its schema;
  no loops or filtering without round trips. Suits few operations with side effects.
- **Structured call tool** (`call(path, args)`), which the Editor lab offers where the host forbids running code from
  strings: one tool, one API function per call, JSON arguments, the same reply format.
- **Stateless eval** with explicit inputs and outputs per call: reproducible and auditable, at the cost of re-sending
  state.
- **Notebook kernel** with cells kept as a document: the session's history becomes an artefact a person can rerun.

## Consequences

- \+ One tool covers the whole catalogue; agents combine, loop and filter in one call.
- \+ The domain processor turns raw values into replies sized for a context window.
- \+ Libraries and state make long sessions efficient, and the context block keeps them legible.
- \+ The generic session is reusable across engines.
- − Programs can do anything the API allows; safety rests on the API and the sandbox, not on the tool.
- − A call's result depends on the session's history, which makes single calls hard to reproduce.
- − Caps and budgets hide information; the notes that say what was cut must be good.
- − Agents still need to be told the contract (await, return, state object), and some will get it wrong at first.

## Known uses

- **CodeAct** (Wang et al., ICML 2024) showed that agents acting through executable code outperform agents choosing
  among JSON tool calls on many tasks.
- **ChatGPT's data analysis** runs model-written Python in a sandboxed kernel that keeps files and variables across
  calls.
- **Jupyter kernels** separate a generic execution protocol from language-specific kernels; IPython runs startup files
  from a profile before the first cell, a form of layered preludes.
- **SWE-agent** (Yang et al., 2024) designed its agent-computer interface around capped, summarised command output and
  feedback in each reply.

## Related chapters

- [Chapter 1 · Self-Describing Operation Registry](01-self-describing-operation-registry.md): the API in scope and its
  generated reference.
- [Chapter 3 · Content-Keyed Lazy Graph](03-content-keyed-lazy-graph.md): why `await` is the evaluation point.
- [Chapter 6 · Repairable Errors](06-repairable-errors.md): failure replies and warnings.
- [Chapter 7 · Numbered, Budgeted Evidence](07-numbered-budgeted-evidence.md): the pictures in the reply.
- [Chapter 8 · Contained Workspace](08-contained-workspace.md): where the session may read and write.
- [Chapter 9 · Sealed Agent Run](09-sealed-agent-run.md): sessions inside isolated, repeatable runs.
- Classic patterns: **Interpreter** (the eval tool), **Template Method** (the session calls the processor's hooks),
  **Facade** (the API in scope).
