# JS DSL for Manufacturing

- URL: https://chatgpt.com/c/6a736684-c764-83ea-ac19-0a15e19586cc
- Created: 2026-08-05T16:36:34.763Z

---

> sketch out a DSL for describing manufacturing lines, concise, examples from simple to complex, as JS API

<details><summary>💭 Thinking</summary>

**Sketching DSL examples**

I’m shaping a compact, composable JavaScript API: primitives create nodes, chaining connects them, and options express timing, capacity, resources, batching, branching, and rework. Examples will progress from a straight line to richer workflows.

**Sketched DSL examples**

</details>

## Proposed JS DSL

Graph-first, declarative, and simulation-friendly:

```js
import { line, dist } from "@factory/line";

const factory = line("line-name", {
  timeUnit: "second",
  quantityUnit: "part",
});
```

Every node is addressable. Calling `.to()` creates material flow.

```js
source.to(station).to(buffer).to(sink);
```

## 1. Simple serial line

```js
const L = line("Bracket line");

const raw = L.source("raw-brackets", {
  arrival: { every: "15s" },
});

const drill = L.station("drill", {
  cycle: "10s",
});

const deburr = L.station("deburr", {
  cycle: "8s",
});

const finished = L.sink("finished");

raw.to(drill).to(deburr).to(finished);

L.validate();
```

## 2. Buffers, failures, and constrained resources

```js
const L = line("Machining cell");

L.resource("operator", {
  count: 2,
});

L.resource("mill", {
  count: 1,
  reliability: {
    mtbf: "40h",
    mttr: "20m",
  },
});

const raw = L.source("raw", {
  arrival: { every: "30s" },
});

const queue = L.buffer("mill-queue", {
  capacity: 12,
  discipline: "fifo",
});

const milling = L.station("milling", {
  cycle: dist.triangular("20s", "25s", "40s"),
  requires: {
    mill: 1,
    operator: 1,
  },
});

const finished = L.sink("finished");

raw.to(queue).to(milling).to(finished);
```

## 3. Inspection and rework loop

```js
const L = line("Valve assembly");

const parts = L.source("parts", {
  arrival: { every: "20s" },
});

const assembly = L.station("assembly", {
  cycle: "16s",
});

const inspection = L.inspect("leak-test", {
  cycle: "5s",
  outcomes: {
    pass: 0.96,
    rework: 0.03,
    scrap: 0.01,
  },
});

const rework = L.station("rework", {
  cycle: "45s",
});

const finished = L.sink("finished");
const scrap = L.sink("scrap");

parts.to(assembly).to(inspection);

inspection.out("pass").to(finished);
inspection.out("scrap").to(scrap);

inspection
  .out("rework")
  .to(rework)
  .to(inspection, {
    maxVisits: 2,
    overflow: scrap,
  });
```

## 4. Parallel machines and batch processing

```js
const L = line("Heat-treatment line");

const raw = L.source("raw", {
  arrival: { every: "12s" },
});

const machining = L.station("machining", {
  units: 3,
  dispatch: "shortest-queue",
  cycle: dist.normal("28s", "4s"),
});

const ovenQueue = L.buffer("oven-queue", {
  capacity: 100,
});

const oven = L.batch("heat-treatment", {
  batchSize: 20,
  maxWait: "15m",
  cycle: "50m",
  units: 2,
});

const cooling = L.delay("cooling", {
  duration: "30m",
  capacity: 60,
});

const finished = L.sink("finished");

raw
  .to(machining)
  .to(ovenQueue)
  .to(oven)
  .to(cooling)
  .to(finished);
```

## 5. Mixed products, shifts, and shared resources

```js
const L = line("Mixed-model motor line");

const twoShift = L.calendar("two-shift", {
  monday:    [["06:00", "14:00"], ["14:00", "22:00"]],
  tuesday:   [["06:00", "14:00"], ["14:00", "22:00"]],
  wednesday: [["06:00", "14:00"], ["14:00", "22:00"]],
  thursday:  [["06:00", "14:00"], ["14:00", "22:00"]],
  friday:    [["06:00", "14:00"], ["14:00", "22:00"]],
});

L.resource("assembler", {
  count: 6,
  calendar: twoShift,
});

L.resource("test-rig", {
  count: 2,
  calendar: twoShift,
});

const standard = L.product("standard-motor");
const premium = L.product("premium-motor");

const orders = L.source("orders", {
  mix: {
    [standard]: 0.75,
    [premium]: 0.25,
  },
  arrival: { every: "40s" },
});

const kitting = L.station("kitting", {
  cycle: "25s",
  requires: { assembler: 1 },
});

const assembly = L.station("assembly", {
  units: 4,
  requires: { assembler: 1 },
});

assembly.for(standard, {
  cycle: "90s",
});

assembly.for(premium, {
  cycle: "140s",
});

const test = L.inspect("functional-test", {
  requires: { "test-rig": 1 },
  outcomes: {
    pass: 0.98,
    rework: 0.02,
  },
});

test.for(standard, { cycle: "45s" });
test.for(premium, { cycle: "75s" });

const rework = L.station("rework", {
  cycle: "8m",
  requires: { assembler: 1 },
});

const shipping = L.sink("shipping");
const manualReview = L.sink("manual-review");

orders.to(kitting).to(assembly).to(test);

test.out("pass").to(shipping);

test
  .out("rework")
  .to(rework)
  .to(test, {
    maxVisits: 1,
    overflow: manualReview,
  });
```

## Execution API

```js
const report = await L.simulate({
  duration: "30d",
  warmup: "2d",
  replications: 100,
  seed: 42,
});

console.log(report.throughput);
console.log(report.leadTime.p95);
console.log(report.utilization("assembly"));
console.log(report.wip("oven-queue"));
console.log(report.bottlenecks());
```

Optional outputs:

```js
await L.render({
  format: "svg",
  file: "motor-line.svg",
});

await L.export({
  format: "json",
  file: "motor-line.json",
});
```

## Minimal conceptual model

```js
line
  ├─ product
  ├─ calendar
  ├─ resource
  ├─ source
  ├─ station
  ├─ inspect
  ├─ batch
  ├─ buffer
  ├─ delay
  └─ sink
```

The key design choice is to keep **topology** in `.to()` calls and **behavior** inside node declarations. This makes the same definition usable for validation, visualization, simulation, and eventually execution-system configuration.


---

> what are provable properties

For this DSL, “provable” should mean **true for every possible execution**, not merely observed in simulation.

## Useful properties

### 1. Structural validity

Decidable from the graph alone:

```js
L.prove({
  everySourceReaches: "sink",
  noUnconnectedNodes: true,
  boundedReworkLoops: true,
});
```

Examples:

- Every source has a path to a sink.
- Every outcome is connected.
- No node is unreachable.
- Cycles have explicit visit limits.
- Product routes are complete.

### 2. Type and routing safety

```js
L.prove({
  productsAcceptedByEveryStation: true,
  outcomesExhaustive: true,
  noProductReaches: ["wrong-packaging"],
});
```

Possible guarantees:

- A station never receives an unsupported product.
- Inspection probabilities sum to 1.
- Every possible inspection outcome has a route.
- Premium products cannot enter the standard-only branch.
- Scrap can never reach shipping.

Example invariant:

```js
L.assert(
  never(
    item => item.product === premium &&
            item.location === standardPackaging
  )
);
```

### 3. Resource safety

```js
L.prove({
  resourceUsageWithinCapacity: true,
  resourcesAlwaysReleased: true,
  acquisitionOrderIsAcyclic: true,
});
```

This can establish:

- No station acquires more resources than exist.
- Resources cannot be leaked.
- A shared machine cannot process two jobs simultaneously.
- Deadlock cannot arise from circular resource acquisition.

```js
L.resourceOrder([
  "operator",
  "fixture",
  "test-rig",
]);
```

A global acquisition order makes circular wait impossible.

### 4. Capacity and WIP bounds

For finite buffers and bounded rework:

```js
L.prove({
  maxWip: "<= 148",
  maxAt: {
    "oven-queue": 100,
    cooling: 60,
  },
});
```

A simple upper bound is often:

```text
buffer capacities
+ station capacities
+ batch capacities
+ maximum in-flight items
```

You can also prove conservation:

```js
L.prove({
  conservation:
    "entered = finished + scrapped + active",
});
```

This detects duplicated or lost parts.

### 5. Termination

```js
L.prove({
  everyItemEventuallyTerminates: true,
});
```

This requires assumptions such as:

- Every cycle has a bounded duration.
- Resources eventually become available.
- Rework visits are bounded.
- No route contains an unrestricted cycle.
- Stations do not fail permanently.

For the earlier rework example:

```js
inspection
  .out("rework")
  .to(rework)
  .to(inspection, {
    maxVisits: 2,
    overflow: scrap,
  });
```

Each part can visit inspection at most three times, so the rework cycle cannot continue forever.

### 6. Deadlock freedom

```js
L.prove({
  deadlockFree: true,
});
```

Typical proof strategies:

- The material-flow graph is acyclic.
- Buffers cannot form circular blocking dependencies.
- Resources are acquired in one global order.
- Stations release resources before blocking output.
- At least one location in every production cycle has spare capacity.

Finite buffers make this substantially harder than graph-cycle detection. A cyclic line can be live, and an acyclic line can still block permanently under some resource semantics.

### 7. Throughput bounds

Exact throughput is generally not statically provable for arbitrary stochastic models, but bounds are.

```js
L.prove({
  throughput: {
    upperBound: "120/hour",
  },
});
```

For serial stations:

```text
throughput ≤ minimum station capacity
```

For a station with `n` identical units and cycle time `t`:

```text
capacity = n / t
```

Example:

```js
const assembly = L.station("assembly", {
  units: 4,
  cycle: "90s",
});
```

Its maximum nominal capacity is:

```text
4 / 90 seconds = 160 parts/hour
```

The whole line cannot exceed that rate.

A lower bound requires stronger assumptions about arrivals, failures, blocking, schedules, and dispatch policies.

### 8. Timing guarantees

With bounded rather than arbitrary distributions:

```js
const drill = L.station("drill", {
  cycle: dist.bounded("8s", "12s"),
});
```

You can prove bounds such as:

```js
L.prove({
  leadTime: {
    max: "<= 4h",
  },
  response: {
    from: "inspection",
    to: "scrap",
    within: "10m",
  },
});
```

A hard lead-time maximum usually requires:

- Bounded processing times.
- Bounded queue sizes.
- Fair scheduling.
- Bounded downtime.
- No indefinite shift closure.
- Bounded route length.

A normal or exponential distribution has no finite maximum, so no finite worst-case completion time can be proved.

### 9. Quality bounds

```js
L.prove({
  shippedDefectRate: "<= 0.005",
});
```

This needs explicit semantics for:

- Incoming defect rates.
- Detection sensitivity.
- False-positive rates.
- Rework effectiveness.
- Independence or correlation assumptions.

For purely probabilistic inspection, this is usually a probabilistic proof rather than an absolute invariant:

```js
L.proveProbability(
  eventually(item => item.location === shipping),
  { atLeast: 0.97 }
);
```

### 10. Determinism and reproducibility

```js
L.prove({
  deterministicGivenSeed: true,
  dispatchPolicyTotal: true,
  noAmbiguousRoutes: true,
});
```

This guarantees that:

- Every routing decision has one defined result.
- Ties have an explicit resolution rule.
- The same model, seed, and inputs produce the same event trace.

## A possible assertion API

```js
import {
  always,
  eventually,
  never,
  implies,
  count,
  at,
} from "@factory/verify";

L.assert(
  always(
    count(at("test-rig")) <= 2
  )
);

L.assert(
  always(
    implies(
      item => item.location === shipping,
      item => item.inspections.includes("functional-test")
    )
  )
);

L.assert(
  never(
    item => item.status === "scrapped" &&
            item.location === shipping
  )
);

L.assert(
  always(
    implies(
      item => item.location === rework,
      item => item.reworkVisits <= 1
    )
  )
);
```

## Proof tiers

A practical implementation should distinguish these levels:

```js
const result = await L.verify({
  mode: "static",       // types, graph reachability, capacities
  // mode: "bounded",   // exhaustive exploration up to a limit
  // mode: "symbolic",  // SMT/model checking
  // mode: "stochastic" // probabilistic model checking
});
```

| Tier | Good for | Limitation |
|---|---|---|
| Static analysis | Routing, types, graph invariants | Cannot capture all runtime states |
| Bounded checking | Concrete counterexamples | Only proves up to a bound |
| Model checking | Safety, liveness, deadlock | State-space explosion |
| SMT solving | Numeric capacities and timing constraints | Requires restricted semantics |
| Probabilistic checking | Reliability and quality probabilities | Depends on distribution assumptions |
| Simulation | Performance estimates | Does not prove universal properties |

The strongest initial feature set would be: **route completeness, product safety, conservation, resource bounds, bounded-loop termination, and deadlock checks**. These are valuable and tractable without pretending that arbitrary throughput or lead-time guarantees are always decidable.

