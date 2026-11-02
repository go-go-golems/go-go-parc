---
title: "jigcad: An Agent API That Teaches Through Its Errors, a Sandbox, and a Rule for await"
aliases:
  - jigcad agent sandbox
  - jigcad guard proxies and help
  - jigcad await rule
  - JIG-012 and JIG-013 report
tags:
  - project
  - llm
  - agents
  - javascript
  - api-design
  - evaluation
status: complete
type: project
created: 2026-11-01
repo: /home/manuel/code/wesen/go-go-golems/jig
---

# jigcad: An Agent API That Teaches Through Its Errors, a Sandbox, and a Rule for await

jigcad's agent changes CAD scripts by writing JavaScript that runs against the workbench. Its quality depends less on the model than on the API the model writes against: what is in scope, what a wrong name does, what an error says, and which calls return a Promise. This report follows two tickets that changed that API. JIG-012 moved the agent's code into a sandboxed worker with its own copy of the geometry engine, made wrong names fail at the point of the mistake with the nearest right ones, generated the documentation and a `help()` function from one registry, and gave every compile result one shape. JIG-013 then removed the largest failure class that remained, the forgotten `await`, by making reads synchronous and the remaining asynchronous calls loud. Each change was measured with the evaluation harness described in [[PROJECT REPORT - jigcad - Measuring the Workbench Agent, an Evaluation Harness and a Promise Hint]]; the system as a whole is described in [[PROJECT REPORT - jigcad - Architecture of a Browser CAD Workbench, from Script to Agent]].

> [!summary]
> - Models learn an API from its error messages, not from its documentation. A wrong name now throws where it is read, with the nearest names, where else the name lives, and a `help('…')` pointer; common runtime errors get a note in the step's own terms. Over four measured batches, runs with a misuse error fell from 24 % to 15 % and failed steps from 18 % to 11 %.
> - The agent's code runs in a sandboxed iframe and worker with its own engine, so the language (`j`, `mm`, `deg`) is in scope and `check()` returns a live program. A mirror of the page state keeps synchronous calls synchronous; only effects and engine queries cross the port.
> - The forgotten `await` was the one class that did not shrink. Its cause was in the API: calls were asynchronous by accident of which thread held the program, and the documentation never said which. JIG-013 states one rule — reading is synchronous, compiling, drawing and changing the workbench is awaited — and makes it true: the sandbox answers reads from its own compiled copy of the page's program, and a Promise used as a value throws with the fix. In the next 140 runs, no step left a Promise unawaited (from 38 runs before), and failed steps fell to 11 %.
> - Reading the failing steps by hand found three defects that aggregate numbers hid: a classifier that counted unawaited promises as wrong names, a hint that suggested a quantity method for an array mistake, and a sandbox bug from the first phase that had stripped members off the language's functions.

## 1. The agent's interface and why it matters

### 1.1 One tool, one scope

The agent panel sends the person's request, a context block and a reference document to a language model. The model answers in text or calls one tool, `eval`, whose input is `{ code }`: the body of an async JavaScript function. The workbench runs the code with a fixed set of names in scope and sends back the returned value written as YAML, preceded by anything the code logged. A *turn* is everything between the request and the final answer; a *step* is one `eval` call.

The names in scope are the agent's whole interface to the workbench. They fall into groups:

| Group | Names | What they do |
|---|---|---|
| files | `files.list/read/grep/edit/write/rename/remove` | the preset's editable files |
| compile | `run()`, `check(variant?)` | compile the files on the page; compile a variant without touching it |
| the program | `program.summary/metrics/diagnostics/params/graph/ir/bodies/…` | read the last compile |
| queries | `why`, `faces`, `feature`, `sketch` | ask the engine about names, faces, features, sketches |
| measure | `measure.face/edge/distance/angle/bbox/area` | geometry in world coordinates |
| the bench | `select`, `view.set`, `look`, `params.set`, `presets.*`, `exportFile` | act on what the person sees |
| helpers | `lab.*`, `log`, `console`, (new) `help` | links, logging, documentation |

Everything the model knows about these names comes from three places: the reference appended to the system prompt, the results of its own steps, and nothing else. This report is about the second source.

### 1.2 What the transcripts showed

Ticket JIG-011 analysed one long transcript in which the agent built a "cat magnet pin" preset, and counted misuse over 517 recorded runs. Three findings set up the work that follows.

- **The language was out of reach.** The agent's code ran on the page, while the engine and its language `j` ran in a Web Worker. `j`, `mm` and `deg` were not defined in eval code. In the history, `j is not defined` and `mm is not defined` appear in 72 and 39 steps. To try one call of the language, the agent pasted a whole part into a string and compiled it with `check()`, and it encoded answers in a bounding box width because `check()` could not return a value computed inside the script.
- **A wrong name surfaced late.** `program.metric(…)` is `undefined`, and the mistake shows up as `program.metric is not a function`. Worse, `r.summary.name` after a failed compile reads `undefined.name`, two calls away from the cause.
- **Shapes disagreed.** `program.bodies()` returned `faces: 11` (a count named like a list), `program.metrics()` returned `{ value, unit, fidelity }` objects that code read both with and without `.value`, and `check().summary` and `program.summary()` had different fields.

### 1.3 What two earlier projects measured

Two earlier projects by the same author had solved parts of this problem, and one of them had measured it.

**factory-videos** recorded 230 agent evals with error handling built for them. The agent read the documentation 4 times and followed 1 of 8 error messages that named a documentation topic, yet it fixed nearly every failed eval on the next step from the message alone. The project drew four rules from that: put fixes into messages and into functions that cannot be misread, and documentation last; make silent failures loud first; guard namespaces with a `Proxy` whose `get` trap throws for an unknown key, but not values, because `x.maybe?.()` reads the property before the optional call and would throw through a proxy; and test every message with a lint that calls each function with the junk models send, with no model involved. It also tried type-checking eval code with `tsc` and dropped it: 141 flagged evals had worked, against 42 that failed.

**Kiln** ran its agent's code in a fresh `<iframe sandbox="allow-scripts">` built from `srcdoc`, whose Content-Security-Policy refused every connection. Its one script started a Web Worker from a `blob:` URL and handed it a `MessagePort`; the worker held its own copy of the language, and every call into the workbench was a message the page checked against an allowlist.

jigcad's evaluator was older than both in some respects (promise tracking from JIG-004, images, `look()`, warnings as text, approval of each step in Ask mode). What it lacked was the language in the agent's hands, and any feedback for a wrong name.

## 2. Measuring misuse

Before changing the API, JIG-012 built the tools to measure it. Both are model-free.

### 2.1 The failure report

`tools/agent-eval/failures.mjs` reads any number of `results.jsonl` files written by the harness and classifies every step's result:

```js
export function classify(step) {
  const head = String(step?.result ?? '').replace(/^logs:[\s\S]*?\n---\n/, '');   // the logs come first
  if (/never awaited/.test(head) && /* the error is the promise's */ …) return 'promise not awaited';
  let m;
  if ((m = /^ReferenceError: ([\w$]+) is not defined/.exec(head))) return `not defined: ${m[1]}`;
  if ((m = /^TypeError: Cannot read properties of (?:undefined|null) \(reading '([^']+)'\)/.exec(head))) return `read of undefined: .${m[1]}`;
  if ((m = /^TypeError: (.+?) is not a function/.exec(head))) return `not a function: …`;
  if ((m = /^TypeError: ([\w$.()]+) does not exist/.exec(head))) return `guarded name: ${m[1]}`;
  …
}
export const MISUSE = c => /^(not defined|read of undefined|not a function|guarded name|NaN in an error)/.test(c);
```

For each class it reports steps and runs, and for the whole batch: the share of runs with at least one misuse error, steps to recover after a failed step, stuck loops (three or more failures in a row), and coverage (which scope names the code called). Over the 517 historical runs: 2,697 steps, 16 % failed, 26 % of runs with a misuse error, 15 stuck loops.

### 2.2 The message lint

`test/agent/lint.test.mjs` calls every function of the scope with nine argument lists that models send by mistake — none, `undefined`, `null`, `''`, `42`, `{}`, `[]`, an unknown id, too many arguments — and reads the messages. A message fails when it does not name the call, or when it is the implementation talking: `NaN`, `Cannot read properties`, `is not a function`, `[object Object]`. When it was written it found 11 offenders. `faces({})` answered `faces: cannot read the query [object Object]`; `view.set(null)` answered `Cannot destructure property 'name' of '(intermediate value)…' as it is null`. The test keeps a list of known offenders that may only shrink; JIG-012 emptied it by adding argument checks such as:

```js
export function textArg(verb, v, what, example) {
  if (typeof v === 'string' && v) return v;
  throw new TypeError(`${verb}: give ${what} as text, such as ${example} (got ${kindOf(v)})`);
}
// faces({}) → TypeError: faces: give a selector as text, such as '%plane' or '>Z' (got an object)
```

## 3. The sandbox

### 3.1 Where the code runs

The agent's code now runs in a worker inside a sandboxed iframe, with its own copy of the engine.

```text
 page (Host)                                         sandboxed iframe (opaque origin, CSP refuses connections)
 ┌──────────────────────────────────────┐            ┌───────────────────────────────────────────────────┐
 │ files, overrides, program, lastGood   │            │  blob: worker  (dist/agent-worker.js)              │
 │ engine worker: the page's Program     │  ctx  ──►  │   mirror host over ctx                             │
 │ labScope(host): checks every call,    │            │   labScope(mirror): files, program, queries, …     │
 │   enforces Ask / Read-only            │  ◄── call  │   stubs for effects: run, look, params.set, …      │
 │                                       │  ret  ──►  │   own engine: j, units, data, check()              │
 └──────────────────────────────────────┘            └───────────────────────────────────────────────────┘
```

The iframe is built from `srcdoc` with `sandbox="allow-scripts"`, so it has an opaque origin: no cookies, no storage, no access to the page. Its Content-Security-Policy is `default-src 'none'; script-src 'unsafe-inline' 'unsafe-eval'; worker-src blob:`. Its one script waits for a message from the parent carrying the worker's source text and a `MessagePort`, starts a worker from a `blob:` URL of that text, and hands it the port. The worker cannot fetch, so the page fetches the OpenCascade and Rust WebAssembly bytes and sends copies in the `init` message.

A check in a separate headless Chrome confirmed the isolation from inside a step: `fetch` fails, a `WebSocket` is refused by `connect-src`, `importScripts` raises `NetworkError`, `localStorage` and `document` are undefined, `indexedDB.open` raises `SecurityError`, and `self.origin` is `null`. A loop that never yields ends the worker when the step's time runs out; the next step starts a new one, which takes about 0.3 s including the engine.

In Node, where the harness runs, the same runner runs in a `worker_threads` worker.

### 3.2 The protocol

Each step gets its own `MessageChannel`. The page sends `{ t: 'eval', port }` on the worker's control port, then `{ t: 'start', code, api, ctx, readOnly }` on the step's port. The sandbox answers effect calls with `{ t: 'call', id, path, args }`, the page replies `{ t: 'ret', id, ok, value | error, ctx? }`, and the step ends with `{ t: 'done', ok, text }`.

`ctx` is the page state the step needs: the files and which are edited, the override values, the last program and the last good program, the selection, the view, the presets. It is built by `ctxOf(host)` in `src/agent/sandbox/serve.js`. A program record reaches 6.3 MB for the largest preset (bodies carry typed arrays); structured cloning it once per step was cheap enough that no cache was added.

### 3.3 Why a mirror, not a remote API

The obvious design sends every scope call across the port. That makes every call asynchronous, and it breaks code the model writes thousands of times: `files.read('script.js').split('\n')` appears in 992 historical steps, `program.metrics().volume` in 355. Instead, the sandbox runs the *same* scope code as the page (`labScope`) over a mirror host built from `ctx`. Reads of files and program records are local and synchronous. Effects are stubs that send a message and wait. File edits are applied to the mirror at once, so the next line sees them, and queued to the page in order; a refusal from the page becomes a note in the result.

```js
// runner.js: file changes apply locally (sync, as on the page), the page follows in order
scope.files[fn] = (...args) => {
  const v = local(...args);
  queue = queue.then(() => call(`files.${fn}`, args)).then(r => {
    refresh(r.ctx);
    if (!r.ok) notes.push(`note: the workbench refused files.${fn}(…): ${r.error?.message}`);
  });
  return v;
};
```

The page executes every effect through its own `labScope`, which is where Read-only mode is enforced, so code in the sandbox cannot get around it.

### 3.4 The language in scope

The step's scope adds the engine's own `j`, the unit functions (`mm`, `cm`, `deg`, `lw`, `layer`, …) and `data`, so `return j.fit.hole(mm(6), 'press')` answers `j.fit.hole(6 mm, press)`. `check(variant?)` compiles in the sandbox's engine and returns a live `program` whose queries work until the next `check()`. A script can call `log(…)`, and its lines come back as `logs` in `run()` and `check()`, so a script can report a value it computed. Globals a step adds are deleted afterwards: nothing carries over between steps, and the reference says so.

## 4. Errors that teach

### 4.1 Guarded namespaces

A guarded namespace throws at the read of a name it does not have:

```text
TypeError: j.fit.hol does not exist. Did you mean j.fit.hole? (j.fit has: calibrate, classes, coupon, gap,
hole, pin, profile, profileRegister) help('j.fit') says what each does. (line 1)
```

`src/engine/guard.js` builds the proxy. Three details matter.

- **The target is a shadow.** The namespaces of `j` are frozen, and a proxy may not return a different value for a frozen property of its own target (a proxy invariant). The guard's target is an empty object or function, and every trap forwards to the real namespace.
- **Probes pass.** `await j.fit` reads `then`; serializers read `toJSON`; test tools read `asymmetricMatch` and `$$typeof`; Node's inspector reads a symbol. These must stay `undefined`, so they and every symbol pass through.
- **The message says where else.** An index of the whole tree answers "faces is j.sel.faces"; in the agent's scope, a name that is a function on its own is named as such: `program.facez does not exist. In scope on its own: faces(…)`. A unit under `j` gets its own hint: `j.mm` → "mm is not under j: units and unit functions are in scope on their own".

Nearest names come from an edit distance with transpositions in which a difference of case costs half, and prefixes or containments ("faceCount" for "faces") count as closer than their raw distance. The guard applies to `j` in `makeJ()`, so scripts get it too, and to the agent's namespaces (`files`, `program`, `params`, `measure`, `view`, `presets`, `lab`, `check().program`). `data` is left unguarded so that `data.x ?? fallback` keeps working.

### 4.2 Hints

A proxy cannot catch everything: the value a builder returns is not guarded, and `undefined.name` is not a namespace read. `src/agent/hints.js` appends notes for what is left, as a pure function of the error, the code and the names in scope:

```text
ReferenceError: box is not defined (line 1)
note: box is j.box.

TypeError: j.part(...).faces is not a function (line 1)
note: j.part(...) has no .faces(). .faces() is a method of a selector; j.part(...) is something else.

TypeError: Cannot read properties of undefined (reading 'name') (line 1)
note: r.summary is undefined. check() and run() give summary, metrics and program only when the script compiles
(ok: true); when it fails they give errors. Test r.ok first, or return r.errors.

ReferenceError: myPart is not defined (line 1)
note: myPart is not in this step's scope. Steps do not share variables: a const, let or globalThis value from an
earlier step is gone. Define it again here, or keep it in a file and read it.
```

Method suggestions come from sample values of the language (a part, a quantity, a sketch, a region, a selector, an assembly, a print job, a design) whose prototypes are read once per worker.

### 4.3 Values that describe themselves

The result of `return j.fit.hole(mm(6), 'press')` used to be the raw fields of a Quantity object (`v: 0, d: [...], u: mm, sym, fn, text`). The YAML writer now prints any non-plain value with its own `toString` as that one line, and Part, Assembly, PrintJob and Design gained one: `part box: add1 (add) · fillet1 (fillet)`.

### 4.4 One documentation registry and help()

`src/agent/docs.js` holds one record per row of the reference's scope table:

```js
{ group: 'compile', names: ['check'], awaited: ['check'], sig: '`await check(variant?, options?)`',
  text: 'compiles in the sandbox, without touching the editor or the view: … `program` is live …' }
```

The table in `reference.md` is the marker `<!-- agent-scope -->`, rendered from the records. A test fails when a scope name has no record or a record names nothing. `help(x)` answers from the same records for the scope, and for the language from the language reference itself, which is regular enough to parse: every bullet has the form ``- `sig` ✓: what it does. Example: `code`.``, and the section a method bullet is in says whose method it is. That gives 198 `j` paths, 25 units, and methods by kind (part 37, quantity 32, sketch 29, …). `help(j.fit)` lists a namespace with one line per member; `help(somePart)` lists a value's methods; `help('chek')` answers "Nearest: check". The guard messages end with the `help` call that answers.

factory-videos' evidence predicts that models rarely call help, and the registry is worth having anyway because it keeps the reference correct. In the batch after this phase the model called `help` 10 times in 70 runs, among them `help(j.lib.magnet)` and `help('part.add')`.

### 4.5 One result shape

`run().summary`, `check().summary` and `program.summary()` are now the same object. `program.metrics()` returns plain numbers in their units, and `program.metrics({ detail: true })` returns `{ value, unit, fidelity }`. `program.bodies()` names its counts `faceCount` and `edgeCount`. No backward compatibility was kept; the reference, prompt and cases changed with the code, and a hint catches the old `.value` habit.

## 5. Three defects found by reading steps

The aggregate numbers after the first measured phase looked good. Reading every failed step of the batch showed three defects that the numbers had hidden.

**The classifier counted promises as wrong names.** Ten steps were classified `not a function: .map`. Read one by one, almost all were the same mistake: `const holes = faces('…'); holes.map(…)`, an unawaited Promise kept in a variable. The classifier only recognised `faces(...).map`. With the rule corrected (and a guard against the opposite mistake, an unrelated `program.metric` error next to a promise note), the baseline's misuse share moved from 27 % to 24 % and phase 2's from 23 % to 18 %. Every report was recomputed with the corrected classifier.

**A hint made the mistake worse.** For `holes.map is not a function` the hint suggested "Nearest methods: .max() (quantity)", because it searched the language's methods for anything close to `map`. Array, string and promise methods now get their own notes ("is not an array; return holes to see what it is"), a call known to answer later gets "returns a Promise: write (await …).map(…)", and no note repeats what the promise note already says.

**The sandbox stripped the language.** One step failed with `j.frame.on is not a function`. `j.frame.on` exists. In the sandbox, `j` had been added to the scope before `trackScope`, which wraps every function and copies every plain object one level deep so it can track the Promises they return. `j` is a plain object; its functions became wrappers without their own members (`j.frame.on`, `j.q.sin`), and the copy lost the top-level guard. The defect had been present since the sandbox was built; its tests checked `j.fit.hole`, a member of a plain sub-object, which survived the copy. The language now goes into the scope after tracking.

## 6. The forgotten await

### 6.1 The class that did not shrink

| | baseline | after errors | after docs and shapes |
|---|---:|---:|---:|
| runs with a misuse error | 24 % | 18 % | 16 % |
| failed steps | 18 % | 16 % | 15 % |
| never recovered | 5 | 1 | 0 |
| runs with an unawaited promise | 28 | 29 | 38 |
| — steps that failed | 15 | 15 | 24 |
| — steps that returned a wrong value | 16 | 16 | 25 |

(The third column also counts calls on `check()`'s live program, which were tracked from that batch on: 10 of its 49 unawaited steps.)

The JIG-004 note — `note: check() returned a Promise that this step never awaited. Write: const x = await check();` — helps the next step. It cannot prevent the first.

### 6.2 Why the model forgets

Two causes, both in the API rather than the model.

- **The documentation never said which calls return a Promise.** The reference said once that the code "can `await`". In the table only `look` was written as `await look(…)`. The prompt wrote "Then call run() and read the result: { ok, errors }" and "check(variant) compiles a variant".
- **The split followed plumbing.** About half of the scope was synchronous, and those were the calls used most. `faces()` reads like `program.bodies()`, yet it returned a Promise, and on `check()`'s live program even the reads were asynchronous. A reader cannot predict that split from the names, because it follows which thread holds the compiled program, not what a call does.

### 6.3 Is the asynchrony needed?

| Call | Why asynchronous | Inherent? |
|---|---|---|
| `run`, `params.set/clear`, `presets.load/create` | recompile the page's program | yes: they compile and change the workbench |
| `check` | compiles a script; scripts are async function bodies | yes |
| `look`, `exportFile` | the page draws or exports | yes |
| `select`, `view.set`, `presets.rename`, `lab.follow` | cross to the page, which owns that state | yes: they change the workbench |
| `faces`, `why`, `feature`, `sketch`, `measure.area`, `params.get`, `program.ir(…, { node })` | the question crosses a port to the thread that holds the Program | no: answering is a lookup on a compiled Program |

`Program.faces(sel)` in `src/engine/program.js` is synchronous. The only asynchronous step on the engine side was the evaluation of selector text that starts with `j.`, which ran as an async script body. Asynchrony also buys nothing for composition here: one engine answers every query in order, so `Promise.all` saves no time, and a runaway step is stopped by ending its worker. It costs the most common pattern in the data, chaining on a query result: `faces('%plane').filter(…).map(…)`.

### 6.4 The rule

> Reading (and editing files) is synchronous. Anything that compiles, draws, or changes the workbench — params, presets, selection, view, links, exports — returns a Promise: `await` it.

Two facts make it safe to follow. `await` on a value is harmless, so a model that awaits too much is never wrong. And a Promise used as a value now throws at the line where it is used (§6.6).

### 6.5 Synchronous reads from a shadow program

The sandbox has its own engine, so it can hold its own compiled copy of the page's program and answer reads from it. JIG-013 calls this copy the *shadow*.

```text
step starts ──► page's lastGood.hash == shadow's hash ? ──yes──► run the code
                         │ no
                         ▼
          compile goodInputs into the 'shadow' slot (async: the step has not started) ──► run the code

inside the code:  faces('%plane')   ──► Program.faces on the shadow ──► records, synchronously
                  await run()       ──► bridged to the page ──► ctx refreshed ──► shadow rebuilt ──► result
```

Four changes make it work.

- **The page records its inputs.** On every compile that succeeds, `Host.compile` stores `goodInputs = { files, override }` next to `lastGood`, and `ctxOf` sends it.
- **The engine keeps several programs.** The engine worker used to keep one current Program, and after each compile its garbage collector freed every kernel body that the feature cache and the live programs did not reference. It now keeps named slots; `releasePrograms(...keep)` takes all of them, so each slot's bodies survive the next compile. `callSync(slot, method, args)` answers on any slot without `await`, and selector text is evaluated as a plain function. The sandbox uses two slots, `shadow` and `check`.
- **The hashes must agree.** After compiling the shadow, the sandbox compares its program hash with the page's. The same inputs and the same engine bundle give the same hash; a test compiles a preset with overrides and a two-body preset into different slots and compares. A mismatch makes every read throw a message saying so, rather than answer about a different model.
- **One query path.** The scope's query functions use the synchronous path when their host has one and the asynchronous one otherwise:

```js
function ask(host, method, verb, args, shape = v => v) {
  if (typeof host.callSync === 'function') {
    let v;
    try { v = host.callSync(method, ...args); } catch (e) { throw prefixed(verb, e); }
    return shape(v);
  }
  return call(host, method, verb, ...args).then(shape);   // the page: its engine is in a worker
}
```

The sandbox's mirror host answers from the shadow, and `check()`'s live program from the `check` slot. Because the selector now runs in the same realm as the engine, a selector value works too: `faces(j.sel.faces('>Z').of('body'))`. `faces()` with no selector lists every face, which models had asked for with `faces('')` and `faces('*')`.

The cost is a second compile in the sandbox each time the page's good compile changes: tens of milliseconds for the shared 60 × 40 × 30 mm box, about a second for the largest presets.

### 6.6 Loud promises

The calls that stay asynchronous return a tracked thenable (JIG-004). It is now a `Proxy` that answers `then`, `catch`, `finally` and the usual probes, and throws on any other property:

```js
function loud(tp, t) {
  return new Proxy(tp, {
    get(target, k) {
      if (typeof k === 'symbol' || PASS.has(k)) return Reflect.get(target, k);   // then, catch, finally, toJSON, …
      t.consumed = true;                                                           // the error says it: no note
      throw new TypeError(`${t.label} returned a Promise: write (await ${t.label}).${String(k)}`);
    },
  });
}
```

`await`, `Promise.all` and `Promise.resolve` read only `then`, so they work. `const r = check(); return r.ok` used to return `undefined`; it now fails with `TypeError: check() returned a Promise: write (await check()).ok (line 1)`.

Two more cases no longer need the model's attention. A Promise inside the returned value (`return { r: check() }`) is awaited before the value is written. A call the step started and never awaited (`run(); return 1`) is allowed to finish within the step's time, so its failure is reported in the step.

### 6.7 The rule in the documentation

The registry marks the awaited names, so the table and `help()` write `await run()`, `await check(variant?, options?)`, `await params.set(name, value)`. The reference opens the scope section with the rule and the list; the prompt states it in one sentence and writes its own examples as `const r = await run()`. A test ties the documentation to the code: the awaited names must be exactly the calls the sandbox bridges to the page, minus file edits, plus `check`.

### 6.8 What it measured

The last batch ran every case twice on both models (140 runs) from a worktree frozen at the JIG-013 commit:

| | baseline | after errors (JIG-012 phase 2) | after docs and shapes (JIG-012 phases 3–5) | after the rule (JIG-013) |
|---|---:|---:|---:|---:|
| runs | 66 | 66 | 70 | 140 |
| passed | 64 | 63 (1 backend error) | 68 | 136 |
| failed steps | 18 % | 16 % | 15 % | 11 % |
| runs with a misuse error | 24 % | 18 % | 16 % | 15 % |
| runs with an unawaited promise | 28 | 29 | 38 | 0 |
| tool calls per run (default / complex) | | | 5.2 / 7.6 | 4.3 / 6.8 |

No step in 140 runs used a Promise as a value or left one unawaited. The loud-promise error never fired, which is the expected outcome: the reads it would have caught are values now, and the calls that stayed asynchronous were awaited. Fewer failed steps also meant fewer tool calls per run.

The four failures were engineering judgment rather than API misuse: holes placed slightly off the request, a fillet the engine refused, a wrong volume on a switch plate, and one exploration of ear fillets that used up its steps before creating the preset. Reading the failing steps again found two defects outside the targeted class. `look()` refused overlays written as `{ dims: true }`, the form `view.set` takes (5 steps); it now takes both forms. And the harness's renderer could not draw a preset the agent had just created, because it loaded presets by id in a separate browser page; it now draws from the files. Both were fixed after the batch.

## 7. What these tickets established

- **Fix the API before the model.** Every large improvement came from changing what the code does at the point of a mistake: a wrong name throws with the right one, a Promise used as a value throws with the fix, a read returns a value. Notes after the fact helped the next step; they did not prevent the first.
- **The documentation must describe the contract the model will hit.** For the `await` rule, the reference was silent and the prompt's examples taught the mistake. Generating the table from a registry, and testing the registry against the code, keeps them from drifting.
- **Read the failing steps.** A classifier rule, a misleading hint and a stripped `j` were each invisible in the batch totals and obvious in the first ten failing steps.
- **One repeat per case is noise for pass rates.** Pass rates moved by one or two cases between batches; misuse shares, recovery counts and the classes of failure moved consistently. The last batch ran two repeats per case.

## 8. Open questions

- An engine error, `add magnetPocket failed: Cannot read properties of undefined (reading 'type')`, appeared once after a sequence of edits and did not reproduce when the same edits were replayed. Feature failures that are JavaScript errors from inside the engine are now reported as `engine.bug` with their first engine frames, so the next occurrence can be diagnosed.
- On the page fallback, used only when the sandbox cannot start, reads remain asynchronous.
- The harness tests two models (one per tier). Whether the rule and the loud promises help a stronger model as much is not measured.

## 9. Important files

| File | Role |
|---|---|
| `import/jigcad/src/agent/sandbox/runner.js` | the sandbox's side: mirror host, stubs, the shadow, `check()`, `runStep` |
| `import/jigcad/src/agent/sandbox/{client,serve,frame,node}.js` | the page's side, the bridge and `ctxOf`, the iframe, the Node worker |
| `import/jigcad/src/engine/guard.js` | guarded namespaces, nearest names |
| `import/jigcad/src/agent/hints.js` | notes for errors a proxy cannot catch |
| `import/jigcad/src/agent/docs.js`, `help.js`, `langdocs.js` | the registry, `help()`, the language reference as records |
| `import/jigcad/src/agent/scope.js` | the scope; `ask()`, the one query path; argument checks |
| `import/jigcad/src/agent/evaltool.js` | tracking, loud promises, `settleValue`, `drain`, `guardScope` |
| `import/jigcad/src/engine/worker.js`, `program.js` | slots, `callSync`, `releasePrograms(...keep)` |
| `import/jigcad/tools/agent-eval/failures.mjs` | the failure report |
| `import/jigcad/test/agent/lint.test.mjs` | the message lint |
| `ttmp/2026/11/01/JIG-012-AGENT-SANDBOX--…/`, `ttmp/2026/11/01/JIG-013-AWAIT-RULE--…/` | guides, diaries, batches and reports |
