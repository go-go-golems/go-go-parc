---
title: "StackChan Pet: The Pet VM — A Synchronous Dataflow Interpreter for Emotional Pets — A Technical Deep Dive"
aliases:
  - StackChan pet VM
  - Pet VM deep dive
  - ESP-63 VM report
  - Pet dataflow interpreter
tags: [project-report, virtual-machine, dataflow, interpreter, javascript, quickjs, esp32-s3, tamagotchi, embedded]
status: active
type: project-report
created: 2026-09-26
repo: /home/manuel/code/wesen/go-go-golems/esp32-s3-m5
branch: esp-63-stackchan-pet
source_ticket: ESP-63-STACKCHAN-TAMAGOTCHI
code_paths:
  - 0120-m5stackchan-pet/js/lib/vm.js
  - 0120-m5stackchan-pet/js/lib/ops.js
  - 0120-m5stackchan-pet/js/lib/graph.js
  - 0120-m5stackchan-pet/js/lib/events.js
  - 0120-m5stackchan-pet/js/lib/device.js
related_vault_notes:
  - "[[PROJECT REPORT - StackChan Pet - An Emotional Tamagotchi DSL Compiled to a Dataflow IR - A Technical Deep Dive]]"
  - "[[PROJECT REPORT - StackChan Pet - Running the Pet on the Robot - Device Runtime, Screen UI and Real-Time Scheduling - A Technical Deep Dive]]"
---

# StackChan Pet: The Pet VM — A Synchronous Dataflow Interpreter for Emotional Pets

The pet VM is the part of the StackChan pet system that makes a compiled pet behave over time. It receives the compiler's output, a graph of about one hundred typed nodes, and advances it in fixed steps: needs drain, events arrive, the emotional state moves, a label is chosen, a behavior is selected, and an *intent* is published for the C++ executor that drives the robot's face, head and lights. The same 1,341-line JavaScript file, `0120-m5stackchan-pet/js/lib/vm.js`, runs in Node for tests, in the desktop simulator for multi-day fast-forwarding, and inside QuickJS on the robot.

This report explains how that VM works: what it receives, how it turns a graph into a sequence of evaluations, what each operation computes, how events are delivered, how user lambdas are called safely, how its output is formed, and how its state survives a power cut. The two earlier reports describe the system around it. [[PROJECT REPORT - StackChan Pet - An Emotional Tamagotchi DSL Compiled to a Dataflow IR - A Technical Deep Dive]] covers the pet language and the compiler. [[PROJECT REPORT - StackChan Pet - Running the Pet on the Robot - Device Runtime, Screen UI and Real-Time Scheduling - A Technical Deep Dive]] covers the firmware that hosts the VM on the robot. This report stays inside the VM.

> [!summary]
> - The VM interprets a synchronous dataflow graph. Each tick evaluates every node of one rate domain exactly once, in an order fixed by the compiler. It has no instruction stream and no program counter.
> - State nodes read inputs during the tick but publish their new value only after every node has run. That single rule makes evaluation order irrelevant for feedback, and makes cycles legal whenever they pass through a state node.
> - Events live in one append-only log read through per-domain cursors. Every event reaches every domain exactly once, and events emitted during a tick are seen on the next one, which rules out instantaneous event loops.
> - User lambdas run as hooks with a read-only context. The VM records every value a hook reads and re-runs the hook only when one of those values changes. It also enforces a rate limit and quarantines a hook after three failures.
> - The file header states its semantics as normative: a planned C++ VM must reproduce them, and the JavaScript VM stays the reference against which it will be tested.

## Why the pet is a graph, and why it needs an interpreter

A pet could have been a script with its own timer loop. The project chose a different form for three reasons, which the first report develops in full. The robot's frame-rate work must stay in native code. A pet must be testable over simulated days in seconds. And its structure should be inspectable: which need feeds which emotion, which condition ends which behavior.

A graph satisfies all three. The compiler turns a pet script into nodes and edges, checks types and cycles, and emits a JSON document. Something must then execute that document. The VM is that executor for the two slow domains of the pet: the *body*, which ticks once per second (needs, age, care quality), and the *mind*, which ticks ten times per second (emotion, labels, behavior choice). A third, fast domain, the *expression* at up to 50 Hz, lives in the C++ executor and is outside this report.

## Vocabulary

The terms below are defined in the order in which they build on each other.

- **Node.** One operation in the graph, identified by a semantic string such as `need.hunger` or `beh`. A node has an *op* (its operation type), *params* (constants), *input ports* and *output ports*.
- **Op.** The operation type, for example `state.meter` or `fn.cmp`. The 37 ops are declared in `ops.js` with their port names, port types and default domain. That table is the contract between the compiler and every VM implementation.
- **Port and reference.** An output port is named `node.port`, for example `need.hunger.out`. An input port holds a list of references, each either a port name or a literal `{lit: value}`.
- **Combine rule.** How an input with several references merges them: `single`, `sum`, `product`, `and`, `or` or `list`.
- **Slot.** The VM's storage for one output port: an entry in a dense array, `vm.S`, addressed by integer index.
- **Domain.** The rate group a node belongs to: `body` (1000 ms), `mind` (100 ms), or `any` (sources evaluated at the start of every domain tick). The compiler assigns `auto` nodes to a concrete domain.
- **Tick.** One evaluation of one domain. A call to `advanceTo(t)` runs every tick that falls due up to time `t`.
- **Pure node and state node.** A pure node computes its outputs from its inputs and writes them immediately. A state node keeps private state between ticks, updates it during a tick, and *publishes* it to its output slots only at the end of the tick.
- **Event.** A named, timestamped record with an optional payload, such as `head.swipe {dir: "forward"}`. Events come from the hardware (`inject`) or from nodes (`emit`).
- **Cursor.** For each domain, the sequence number of the last event that domain has consumed.
- **Hook.** A user lambda the compiler could not turn into nodes, stored in a *hook table* beside the IR and called by the VM with a context object `ctx`.
- **Act.** An animation timeline (face, head, voice and light steps). The VM starts and stops acts; the C++ executor plays them.
- **Intent.** The VM's output after each mind tick: label, intensity, valence and arousal, behavior, flags, and the act start/stop requests of that tick.

## What the VM receives

The compiler emits a JSON IR. The VM reads these fields:

| Field | Contents |
|---|---|
| `nodes` | Every node: `{id, op, domain, params, in, persist}` |
| `order` | For each domain, the node ids in evaluation order |
| `exposes` | Names under which values appear in `ctx`, e.g. `need.hunger` → `need.hunger.out` |
| `timelines` | Named act timelines, already flattened to timed steps |
| `hooks` | Metadata for each hook: site, kind, return type, budget, default |
| `persist` | Which nodes to snapshot, save period, offline policy and cap |
| `items`, `seed` | NFC item table; the seed for the pet's random numbers |

The hook table itself is not in the JSON. It holds real JavaScript functions and is passed to the VM's constructor beside the IR.

A real node from the default pet `mochi` shows the shape. This is the hunger meter:

```json
{"id":"need.hunger","op":"state.meter","domain":"body",
 "params":{"name":"hunger","init":0.8,"drainPerSec":0.0000347,"fillPerSec":0,"sleepDrain":0.5,
   "refills":[{"pattern":"care.feed","amount":0.35,"where":{"item":null}},
              {"pattern":"pet.refill","fromPayload":"hunger"}]},
 "in":{"drainScale":["life.needsScale"],"filling":["beh.asleep"]},
 "persist":true}
```

The drain rate is `1 / 28,800 s`, so a full meter empties in eight hours. The `drainScale` input connects the meter to the life stage, since a baby's needs drain faster. The `filling` input connects it to the behavior selector: while the pet is asleep, hunger drains at half rate. And the refill table says which events top the meter up and by how much. `mochi` compiles to 100 nodes: 18 in the `any` domain, 7 in `body` and 75 in `mind`.

## Construction: turning names into indices

The IR names everything with strings. Evaluating by string would mean building a key such as `need.hunger.out` and looking it up in a map for every input of every node on every tick. The first version of the VM did exactly that, and a ten-hour simulation took 12.4 seconds. A CPU profile attributed most of the time to string construction, object allocation per node per tick, and a regular expression compiled on every event-pattern match.

The constructor now does all name resolution once, in `compileSlots()`:

```js
compileSlots() {
  const index = new Map()
  const slotOf = (key) => { if (!index.has(key)) index.set(key, index.size); return index.get(key) }
  this.rt = new Map()
  for (const n of this.ir.nodes) {
    const sig = OPS[n.op]
    const r = { id: n.id, op: n.op, p: n.params, out: {}, in: {}, sig: sig.inputs,
                eval: EVAL[n.op] || null, step: STEP[n.op] || null, publish: PUBLISH[n.op] || null, st: null }
    for (const port of Object.keys(sig.outputs)) r.out[port] = slotOf(`${n.id}.${port}`)
    this.rt.set(n.id, r)
  }
  for (const n of this.ir.nodes) {
    const r = this.rt.get(n.id)
    for (const [port, refs] of Object.entries(n.in)) r.in[port] = refs.map((ref) => (typeof ref === 'string' ? slotOf(ref) : ref))
  }
  this.S = new Array(index.size).fill(undefined)
  this.orderRt = {}
  for (const d of ['any', 'body', 'mind']) this.orderRt[d] = this.ir.order[d].map((id) => this.rt.get(id))
}
```

After construction, each node is a small runtime record. It holds integer indices for its outputs, integer indices (or literals) for its inputs, and direct references to up to four functions from the op tables:

| Table | Called | Purpose |
|---|---|---|
| `INIT[op]` | once, at construction | Create the node's private state |
| `EVAL[op]` | every tick, pure nodes | Compute outputs and write them to `vm.S` immediately |
| `STEP[op]` | every tick, state nodes | Update private state from inputs, events and `dt` |
| `PUBLISH[op]` | end of tick, state nodes | Copy private state to the output slots |

The per-domain evaluation order also becomes an array of runtime records, so the hot loop iterates plain arrays. After this change and a compiled-pattern cache for event matching, the same ten-hour simulation took 2.1 seconds, and its printed output was byte-identical, which showed the refactor preserved the semantics. A `Proxy` named `vm.slots` still offers access by name for tools and tests. It is never used on the evaluation path.

## Time and the tick loop

### Advancing time

The VM's clock, `vm.t`, is in pet time: milliseconds since the Unix epoch. Each domain has a period (1000 ms for body, 100 ms for mind), a `nextDue` time and a `lastTick` time. `advanceTo(target)` runs every due tick in time order:

```js
advanceTo(target) {
  while (true) {
    const next = this.nextDue.body < this.nextDue.mind ? this.nextDue.body : this.nextDue.mind
    if (next > target) break
    this.t = next
    if (this.nextDue.body <= next) this.tick('body')
    if (this.nextDue.mind <= next) this.tick('mind')
  }
  if (target > this.t) this.t = target
}
```

When both domains are due at the same instant, body runs first. Every tenth mind tick therefore sees needs that were updated in the same instant. The loop makes the VM independent of how often it is called. The robot calls it every 100 ms; the simulator may call it once for five simulated days. For spans longer than 15 minutes the simulator lengthens the mind period to 1000 ms, which trades exact event timing for speed. Tests that assert exact event times advance in steps of 15 minutes or less.

### One tick

A tick of domain `D` has four phases:

```js
tick(domain) {
  const dt = this.t - this.lastTick[domain]
  this.lastTick[domain] = this.t
  this.nextDue[domain] = this.t + this.periods[domain]
  const events = this.eventsFor(domain)          // events since this domain's cursor
  this.cursor[domain] = this.seq                 // taken at tick start
  const committed = []
  for (const r of this.orderRt.any) r.eval(this, r, dt, events)     // 1. sources
  if (domain === 'mind') this.pumpActs()                            //    timeline emits
  for (const r of this.orderRt[domain]) {                           // 2. the domain's nodes
    if (r.step) { r.step(this, r, r.st, dt, events); committed.push(r) }
    else if (r.eval) r.eval(this, r, dt, events)
  }
  for (const f of this.listeners.evaluated) f(domain)               //    test hook
  for (const r of committed) r.publish(this, r, r.st)               // 3. commit state
  if (domain === 'mind') this.publishIntent()                       // 4. output
  this.trimLog()
}
```

1. **Sources.** The 18 source nodes of `mochi` (clock, traits, event counters, time-since-event values) are evaluated first, so every node in the tick sees the same view of the outside world.
2. **Domain nodes.** Every node of the domain runs once, in the compiler's order. A pure node's `EVAL` writes its outputs immediately; a state node's `STEP` updates private state and joins the commit list.
3. **Commit.** Every state node publishes its new state to its output slots.
4. **Output.** After a mind tick, the intent is assembled and published to listeners.

`dt` is the actual elapsed time since the domain last ran, not a constant. After a long gap, one body tick drains needs by the whole gap. The `evaluated` listener exists for one test: it compares a lowered lambda's node output with the original lambda's output at the exact point in the tick where both see the same inputs.

## Ordering, domains and the cycle rule

### Why state nodes publish late

The central semantic rule of the VM is that a state node's outputs, during a tick, always hold its value from the previous tick. Consider the hunger meter and the node that detects low hunger:

```text
need.hunger       (state.meter, body)   →  need.hunger.out
need.hunger.low   (state.hysteresis, mind) reads need.hunger.out
```

Because the meter publishes at the end of its tick, any node that reads `need.hunger.out` during a tick reads a value that is stable for the whole tick, whatever order the nodes run in. This is the unit-delay rule of synchronous dataflow languages such as Lustre and Esterel. It has two consequences:

- **Feedback through state is legal.** The emotion core reads the reactions node, which reads events, and behaviors read the emotion core's output. The behavior selector's `asleep` output also feeds back into the need meters' `filling` input. Each of these loops passes through a state node, so each is well defined: the loop's value is always last tick's.
- **Feedback without state is an error.** A loop of pure nodes has no defined value, because each node would need the others' outputs from the same tick. The compiler rejects it.

### How the compiler orders nodes

The order the VM follows is computed by `graph.js`. Only *ordering edges* constrain it: edges between two nodes of the same domain, excluding edges out of state nodes (their outputs are last tick's) and edges out of `any`-domain sources (evaluated before everything). A Tarjan strongly-connected-components pass over the ordering edges reports every remaining cycle as `cycle-without-state`, naming the path. Kahn's algorithm then produces a topological order per domain, breaking ties by node id, so the same graph always yields the same order.

### How nodes get a domain

Most pure nodes are declared `auto`. The compiler places an `auto` node in the domain of its fastest consumer: if any consumer is in `mind` (or in `any`), the node goes to `mind`; if all are in `body`, it goes to `body`; a node exposed to hooks goes to `mind`. A value that crosses from body to mind is read as last committed: a sample-and-hold, with no interpolation. This is why `mochi`'s body domain has only seven nodes (four need meters, mood, life stage, care quality), while its 75 mind nodes include the need thresholds, the emotion core, the labeler, the behavior selector and all their arithmetic.

### Combining inputs

An input port with several references merges them according to its combine rule. `vm.in(r, port)` implements the rules on the integer slot indices:

| Rule | Result | Default with no references |
|---|---|---|
| `single` | The first reference; the port default if it is `undefined` | Port default |
| `sum` | Sum of numeric values, non-numbers as 0 | 0 |
| `product` | Product, skipping `null` and `undefined` | 1 |
| `and` / `or` | Logical conjunction / disjunction | `true` / `false` |
| `list` | Array of all values | `[]` |

These rules let components connect independently. The emotion core's `baseV` input is a `sum`, so need pressure and mood both lower or raise the valence baseline without knowing about each other. A meter's `drainScale` is a `product`, so life stage, personality and user graphs can each scale drain.

## Events

### One log, one cursor per domain

Every event is appended to `vm.log` with a sequence number and the current pet time:

```js
logEvent(name, payload, t) {
  const e = { seq: ++this.seq, name, t, payload }
  this.log.push(e)
  // per-name statistics: last time, last payload, the last 64 times
}
```

At the start of a tick, `eventsFor(domain)` returns the log entries with sequence numbers above that domain's cursor, and the cursor is then set to the current sequence number. This design gives three properties that simpler schemes lack:

- **Exactly-once delivery to every domain.** A head swipe injected between ticks is seen by the next mind tick and, independently, by the next body tick, which may be up to a second later. A scheme in which an event is "present" for one tick would let the 1 Hz body domain miss most events.
- **Next-tick delivery of emitted events.** A node that emits during a tick appends to the log after the tick's cursor was taken. The event is delivered on the next tick. An event can therefore never trigger itself within one tick, and chains of emitted events advance one tick per link.
- **Bounded memory.** `trimLog()` drops entries that both domains have consumed, once more than 256 have accumulated.

### Queries over history

Many nodes need history, not just this tick's events: "how long since the head was touched", "how many shakes in the last two minutes". The VM keeps per-name statistics beside the log: the last time, the last payload and the last 64 times. Patterns such as `head.*` or `care.feed|care.play` are matched against the known event names once and cached. The cache is invalidated only when a new event name first appears. `sinceMs(pattern)` and `countIn(pattern, window)` answer from these statistics without scanning the log.

### Hardware events with meaning

`inject()` is the entry point for events from the hardware. It does one piece of interpretation. An `nfc.tag` event's card id is matched against the pet's declared items, and a matching card produces a second event, `care.<verb>` with the item's name and taste, so the rest of the graph cannot tell a food card from a menu button. An unknown card produces `nfc.unknown`.

## What each operation computes

### Sources and pure functions

Sources read the world. `src.clock` computes the local minute of the day from `vm.t` and the time-zone offset, and whether it is night (outside the dawn–dusk window). `src.since` returns milliseconds since a pattern last fired, or infinity. `src.count` returns occurrences within a window. `src.events` returns this tick's matching events. `src.signal` reads a hardware signal such as battery level, and `src.trait` reads a personality trait.

The pure functions are conventional: arithmetic, `fn.clamp`, the affine `fn.map` (`a·x + b`), the piecewise-linear `fn.curve`, comparison, logic, `fn.select` (if-then-else), `fn.cosine` (a daily wave with a configurable peak time) and `fn.window` (a time-of-day window that may wrap midnight). Two need explanation:

- **`fn.div` returns 0 on division by zero.** The VM never produces `Infinity` or `NaN` from arithmetic, because such values would propagate into state and into the executor.
- **`fn.expr` evaluates an expression tree** produced by the compiler from a user lambda (see "Hooks" below).

### State operations

| Op | State | Step |
|---|---|---|
| `state.meter` | `x ∈ [0,1]` | Drain by `drainPerSec · drainScale · dt` (times `sleepDrain` while `filling`), or fill at `fillPerSec` while `filling`; add refills matched from this tick's events; clamp; emit `need.<n>.relief` when refilled |
| `state.hysteresis` | `on` | Turn on when `x` crosses `on`, off when it crosses `off` (either direction, per `below`) |
| `state.edge` | previous boolean | Emit a named event on a rising or falling edge |
| `state.integrator` | `x` | Integrate a rate, add event deltas, optionally decay toward a value with a half-life |
| `state.ema` | `y` | Exponential average with a half-life (the pet's mood uses 6 h) |
| `state.gap` | previous time | Time between consecutive matching events (used to greet the player after an absence) |
| `state.affect` | `v, a`, extra dimensions | The emotion core; see below |
| `state.labeler` | current label, pending label | Chooses the emotion label; see below |
| `state.lifecycle` | stage, age, form | Egg, then stages by duration; calls the `evolve` hook to choose an adult form |
| `state.careQuality` | mistakes, good deeds, discipline | Counts needs left critical too long and ignored calls; quality = `(good + 2) / (good + mistakes + 2)` |

The meter's relief event deserves a closer look, because it came from observing the pet rather than from the design. When a need is refilled, the meter emits `need.<n>.relief` with `relief = min(1, gained · (0.5 + 1.5 · (1 − before)))`. A starving pet that is fed produces a large relief and a strong positive impulse; a full pet that is fed produces almost none. Without this, reversing neglect registered only as needs slowly ceasing to hurt, and a simulator test of a neglected pet being fed failed because the pet never looked happy.

### The emotion core: `state.affect`

The pet's instantaneous emotion is a point: valence `v ∈ [−1, 1]` and arousal `a ∈ [0, 1]`. Each mind tick:

```js
const bv = clamp(p.baseline.v + vm.in(r, 'baseV'), -1, 1)   // baseline + need pressure + mood + …
const ba = clamp(p.baseline.a + vm.in(r, 'baseA'), 0, 1)    // baseline + circadian + energy + …
const k = Math.exp((-dt * LN2) / p.halfLifeMs)              // 90 s half-life by default
st.v = bv + (st.v - bv) * k                                  // relax toward the baseline
st.a = ba + (st.a - ba) * k
// then each impulse from reactions, games and relief:
//   a labelled impulse pulls toward that label's point:  v += s · gain · (point.v − v)
//   a raw impulse adds:                                   v += Δv · gain
```

The point relaxes exponentially toward a baseline that other nodes set (need pressure lowers valence, low energy lowers arousal, the circadian wave raises arousal by day), and impulses move it. A labelled impulse such as `love` with strength 0.5 moves the point halfway toward `love`'s canonical point `(0.8, 0.45)`, so repeated impulses converge rather than overshoot. The node also remembers the last negative label it was pulled toward, which lets the labeler distinguish `angry` from `scared` in the same region of the plane.

### Choosing a label: `state.labeler`

The labeler turns the point into one of the style names the executor understands:

1. **Raised labels first.** Labels raised by conditions such as low hunger (`hungry`, `lonely`, `bored`, `sleepy` for `mochi`) win in priority order, but only while valence is below `raisedMaxV` (0.35). A delighted pet therefore looks delighted even when slightly hungry. This limit also came from a failing simulator test.
2. **Otherwise regions.** An ordered list of boxes in the `(v, a)` plane, each optionally requiring a recent event (`love` requires a head touch within 20 s) or a particular last negative label.
3. **Dwell.** A new candidate must persist for `minDwellMs` (1.5 s) before it replaces the current label, which prevents flicker when the point sits near a boundary.
4. **Intensity.** The distance of the point from neutral, divided by 0.8 and clamped to 1.

### Choosing a behavior: `mind.utility`

The behavior selector is the most intricate node. Each mind tick it runs three steps:

```text
1. If a behavior is running, is it finished?
     its `until` condition holds and it has run for minDuration, or its random duration elapsed,
     or its game reported done, or its one-shot timeline ended, or the life stage no longer allows it.
2. Score every available behavior:
     skip if the stage forbids it, it is cooling down, its `when` is false,
     or it is triggered by an event that is not fresh (or was already handled);
     u = classWeight(class) · clamp(score, 0, 1),   plus hysteresis (0.1) for the running one.
3. Switch if a different behavior won and either nothing is running,
     or the winner's class outranks the current one's,
     or the current one has run for its minimum duration and the winner scores higher.
```

Class weights are `reflex 1.0 > care 0.9 > drive 0.7 > idle 0.3`, so a care behavior the player asked for (eating, playing, waking up) beats a drive such as sleep. Starting a behavior records its start time, draws a random duration if it has a range, builds its act (from a timeline, from a hook, or by the taste of the food that triggered it), requests the act on the behavior layer, and emits `behavior.<name>.start`. Finishing applies its cooldown and, when it finished normally, emits `done` and plays its exit flourish.

A trigger behavior shows why the details matter. `eat` is triggered by `care.feed` within a 2-second window. Without the check `lastStart[b] >= t − since`, the same feed event would restart `eat` every tick of its window. Without keeping a triggered behavior a candidate after its window has passed, `idle` would pre-empt a minigame as soon as the game's minimum duration elapsed. Both conditions exist because early versions failed exactly that way.

### Games: `mind.game`

A minigame is a small state machine owned by a behavior. When its behavior becomes current, the node starts round 1: it calls the `start` and `secret` hooks and opens an input overlay (for example a split screen). It then waits for a `screen.tap`, mapping the tap's x coordinate to one of the options, or for a timeout. On input it calls `reveal` and `score`, and plays the reveal act. After the last round it calls `finish` and applies the result: a refill, an emotion impulse, an act, a score banner. It then emits `game.<name>.done`, which ends the behavior.

## Hooks: calling user code safely

### The context object

A hook receives `ctx`, a read-only view of the pet. It is built once per VM from the IR's `exposes` table. Each exposed name becomes a getter on a frozen object tree: `ctx.need.hunger`, `ctx.feel.valence`, `ctx.behavior.current`, `ctx.life.stage`. The tree also has methods: `ctx.since(pattern)`, `ctx.count(pattern, window)`, `ctx.is(label)`, `ctx.rand()` and `ctx.mem.get(key)`. Writes throw in strict mode, so a hook cannot change state. Effects are expressed only through return values: a number, a boolean, an impulse or an act.

The design document had specified a `Proxy` for this view. The implementation uses getters defined once, plus a swappable recorder. That is cheaper than a proxy per call, and it behaves identically in QuickJS.

### Dependency tracking

Every getter records the key it read and the value it returned into `vm.reads` when a recorder is active:

```js
const record = (key, v) => { if (vm.reads) vm.reads.set(key, v); return v }
const getter = (obj, name, key, read) => Object.defineProperty(obj, name, { get: () => record(key, read()), enumerable: true })
```

A *signal hook*, such as a behavior score, is therefore re-run only when needed:

```js
'js.hook': (vm, r) => {
  const minGap = meta.budget.maxHz ? 1000 / meta.budget.maxHz : 0
  if (prev !== undefined && (vm.t - hs.lastCall < minGap || !vm.hookDirty(p.hook))) return
  const res = vm.callHook(p.hook, [vm.ctx])
  vm.S[oi] = res.ok && res.value != null ? res.value : p.default
}
```

`hookDirty` re-reads every key from the hook's last read set and compares it with the recorded value. Numbers within 1/256 count as equal, objects are compared by JSON, and everything else strictly. Because the read set is rebuilt on every call, a hook whose branches read different values is tracked correctly: `ctx.need.fun < 0.4 ? ctx.since('play') : 0` depends on `since('play')` only while fun is low. A hook that calls `ctx.rand()` records a value that never compares equal, so it always re-runs at its rate limit. The default rate limit for signal hooks is 4 Hz.

### Validation and quarantine

`callHook` measures the call, validates the return value against the site's declared type, and handles failure:

| Declared return | Accepted | Rejected |
|---|---|---|
| `num` | a finite number, or `null` (use the default) | anything else, including `NaN` |
| `bool` | anything (coerced) | — |
| `impulse` | a label string, an impulse object, or `null` | other types |
| `act` | an Act value, or `null` | other values |

A hook that throws or returns an invalid value counts a failure, and its output falls back to the component default. Three consecutive failures quarantine the hook for 60 seconds, and a diagnostic is emitted. A failed call clears the hook's read set. That detail was found by a test: a hook that threw before reading anything had an empty read set, never looked dirty again, was never retried, and so could never reach three failures.

### Lambdas that become nodes

Most hooks never run as JavaScript. The compiler parses a lambda's source text, which it obtains with `Function.prototype.toString`, and when the lambda is a pure expression over `ctx` it replaces the hook with an `fn.expr` node. The lambda from the example pet `tofu`

```js
score: ctx => (1 - ctx.need.affection) * (ctx.since('head.press') > 30 * 60e3 ? 1 : 0.3)
```

becomes this node:

```json
{"id":"hook.0","op":"fn.expr","domain":"mind",
 "params":{"expr":{"k":"bin","op":"*",
   "a":{"k":"bin","op":"-","a":{"k":"num","v":1},"b":{"k":"var","i":0}},
   "b":{"k":"cond","c":{"k":"bin","op":">","a":{"k":"var","i":1},"b":{"k":"num","v":1800000}},
        "a":{"k":"num","v":1},"b":{"k":"num","v":0.3}}},
   "returns":"num","default":0},
 "in":{"vars":["need.affection.out","_since50.out"]}}
```

Each `ctx` read became an input reference: `ctx.need.affection` became the meter's output, and `ctx.since('head.press')` became a new `src.since` source node. The constant `30 * 60e3` was folded to `1800000`. The VM's `evalExpr` walks the tree. It applies the same contract as the hook it replaced, so a non-finite numeric result falls back to the default. In the twelve example pets, 10 of 35 lambdas lower this way. The rest return acts, call evolve or game callbacks, or use local variables.

## Acts and the intent

### Starting and stopping animations

The VM does not play animations; it requests them. `startAct(layer, timeline)` records a running act and appends a request to the current tick's list:

```js
this.requests.push({ op: 'start', layer, id: act.id, t: this.t, hold: act.hold, owner: act.owner, timeline: flat })
```

There is at most one act on the behavior layer. Starting a new one first requests a stop of the previous one. Any number of reaction acts can overlap, and they expire when their timeline and hold time have both elapsed. The executor receives the flattened timeline in the request, so it needs no copy of the IR's timeline table.

One animation feature needs the VM's cooperation: an `emit` step inside a timeline, which raises an event at a precise time during the animation (Example 5's peekaboo counts rounds this way). Timelines may loop, and the mind ticks only every 100 ms, so `pumpActs()` computes, for each emit step, every occurrence `t0 + k·duration + step.t` that falls in the interval since the previous pump. It logs each occurrence at its exact time, not at the tick time. Each occurrence owned by a behavior also emits `behavior.<name>.round`, which drives per-round refills.

### The published intent

After every mind tick, `publishIntent()` reads the inputs of the single `sink.intent` node and publishes:

```json
{"t":1767254475395,"label":"love","intensity":0.46,"v":0.46,"a":0.35,"behavior":"idle",
 "pose":null,"lightsLevel":null,"quiet":false,"asleep":false,"stage":"baby","form":null,
 "overlay":null,"requests":[]}
```

The requests list is then cleared, so each act request appears in exactly one intent. On the robot, the device layer merges the intents of a 100 ms interval into one: the latest state plus every request in order. It forwards that to the C++ executor.

## Determinism

The simulator's value depends on determinism: the same pet, seed and event script must produce the same trace every time. The VM has three sources of variation, and each is controlled:

- **Randomness** comes only from two `mulberry32` generators seeded from the IR's seed, one for behavior durations and one for `ctx.rand()`. JavaScript's `Math.random` is never used.
- **Time** comes only from `vm.t`. The host clock, `hostNow`, is used only to measure how long hooks take. It never influences a value.
- **Order** is fixed by the compiler: domains in time order, body before mind at equal times, nodes in the stored topological order, events in sequence order.

The evidence is the performance refactor described earlier: the ten-hour run printed byte-identical output before and after the VM's internals were rewritten. Hooks are the one open question. On the robot they run synchronously inside the tick, so determinism holds. The planned C++ VM will run them asynchronously in QuickJS with one tick of latency, and the design specifies that the simulator will then record and replay the hook latency schedule.

## Persistence and offline time

### Snapshot and restore

A snapshot contains the private state of every node the compiler marked persistent. For `mochi` those are the four need meters, the mood average, the emotion core, the lifecycle and care quality. The snapshot also carries traits, the pet's memory, and `savedAt`:

```js
snapshot() {
  const state = {}
  for (const id of this.ir.persist.nodes || []) { const st = this.st.get(id); if (st) state[id] = JSON.parse(JSON.stringify(st)) }
  return { ir: this.ir.ir, pet: this.ir.pet, irHash: this.ir.hash, savedAt: this.t, state, traits: { ...this.traits }, mem: { ...this.mem } }
}
```

Restoring matches entries by node id: each restored state is copied into the node and published. An entry whose node no longer exists is counted as dropped. Because ids are semantic (`need.hunger`), a pet script can be edited and reloaded without losing its state: renaming a need resets it, while keeping the name keeps its value. On the robot a snapshot is 520–590 bytes of JSON.

### Catching up

`catchUp(elapsedMs)` simulates time the robot was off, under the pet's offline policy (default `asleep`, capped at 12 hours). Gaps below 60 seconds are ignored. Otherwise it steps only the body domain, in 60-second steps, running only the ops whose meaning survives without a mind: meters, lifecycle, integrators and averages. Under the `asleep` policy it forces the behavior selector's `asleep` output to true, so energy refills and other needs drain at sleep rate. Afterwards the emotion core is reset to its baseline, because feelings do not persist across a night.

A defect in how the device layer used catch-up illustrates why this function advances the clock. The device created the VM at the current time and then caught up by the gap since the save, which moved the clock forward a second time. The VM then sat ahead of real time and ignored every tick until real time caught up. The fix creates the VM at `savedAt` and lets catch-up bring it to the present. The second report tells that story in detail.

## Performance

| Environment | Default pet, one mind tick | Notes |
|---|---|---|
| Node 24 (desktop) | about 5.8 µs (first version: about 34 µs) | After dense slots and the pattern cache |
| QuickJS (desktop) | about 75 µs | Same engine as the robot |
| QuickJS on the ESP32-S3 | about 17.9 ms | Measured with an on-device microbenchmark |

The device figure is about 220 times the desktop QuickJS figure. A CPU-bound `fib(20)` benchmark shows a ratio of about 88 between the same two environments, and the VM's ratio is roughly 2.5 times worse. The VM performs mostly property reads and writes on objects: runtime records, slot arrays, private state and event statistics. On the robot those live in PSRAM, which is slower than the internal RAM the interpreter's hot data would prefer. A full tick on the robot, including intent serialization and the UI model, costs 20–30 ms, about 20–30% of one core. The JavaScript heap for a running pet is about 1.1 MB, stable over time. Garbage collection is performed explicitly outside ticks, because a full collection takes 0.16–0.56 s on the device.

## How the VM is tested

| Test | What it establishes |
|---|---|
| `tests/vm.test.js` (13) | Tick order, state commit timing, exactly-once delivery, next-tick emits, hooks, quarantine, snapshot round trips |
| `tests/behaviors.test.js` (9) | Utility selection, triggers, cooldowns, minimum durations, games, the wake/sleep interaction |
| `tests/lower-lambda.test.js` | Lowered `fn.expr` nodes produce exactly the hook's values over real trajectories, compared in the `evaluated` phase |
| `tests/examples.test.js`, `tests/hoshi.test.js` | All twelve example pets run; a five-day simulation evolves `hoshi` into its `star` form |
| Full suite under QuickJS | The same tests on the robot's engine (found an argument-count limit on `Math.max(...array)` that Node does not have) |

The C++ executor was verified against the JavaScript executor model by replaying about 1.7 million recorded intents and comparing every channel output. The C++ VM, when written, will be verified the same way: both VMs replay recorded event logs, and their intent streams must match exactly. The normative comment at the top of `vm.js` is the specification for that work.

## Limitations

- **Hooks are synchronous.** On the robot a slow hook delays the tick. The quarantine and rate limit bound the damage, but a hook that loops forever is stopped only by the device's 1-second job deadline, and the VM has no rollback for a tick interrupted halfway.
- **Coercions are permissive.** Booleans and numbers convert freely (`true` is 1; non-zero is true). This keeps the JavaScript VM simple, and the C++ VM must replicate it exactly.
- **Coarse fidelity in long simulations.** The simulator's 1-second mind period for spans over 15 minutes changes event timing inside those spans.
- **Pet modules stay loaded.** Each pet load on the device leaves its module record in the QuickJS runtime, about 48 KB, until reboot.
- **Gestures are not the VM's concern, and are unfinished.** The VM requests acts correctly, but the C++ executor does not yet turn head gestures such as `nod` into motion.

## Key points

- The pet VM is a synchronous dataflow interpreter. It evaluates each domain's nodes once per tick in a compiler-fixed topological order, and has no instruction stream.
- State nodes publish at the end of the tick, so every reader sees last tick's value. This makes feedback through state well defined and lets the compiler reject only feedback without state.
- Events are delivered through one append-only log and a cursor per domain. Every event reaches every domain exactly once, and emitted events arrive on the next tick.
- Hooks see a frozen, getter-based `ctx`. The VM records their reads, re-runs them only when a read value changes (at most 4 Hz by default), validates their results, and quarantines them after three failures.
- Most simple lambdas never run as JavaScript: the compiler parses them into `fn.expr` nodes whose inputs are the values the lambda read.
- Name resolution happens once at construction. Dense integer slots made the VM about six times faster with byte-identical output, which also demonstrated that its semantics are deterministic.
- Snapshots are keyed by semantic node ids, and catch-up simulates only the body domain, so a pet survives both power cuts and script edits.

## Related notes

- [[PROJECT REPORT - StackChan Pet - An Emotional Tamagotchi DSL Compiled to a Dataflow IR - A Technical Deep Dive]]: the pet language, compiler and executor.
- [[PROJECT REPORT - StackChan Pet - Running the Pet on the Robot - Device Runtime, Screen UI and Real-Time Scheduling - A Technical Deep Dive]]: how the VM is hosted on the robot.
- Source: `0120-m5stackchan-pet/js/lib/vm.js` (the VM), `ops.js` (op signatures), `graph.js` (linking, domains, cycles, order), `events.js` (pattern matching), `device.js` (the device-facing API).
