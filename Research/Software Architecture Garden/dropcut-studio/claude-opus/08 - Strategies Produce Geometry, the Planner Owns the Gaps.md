---
title: Strategies Produce Geometry, the Planner Owns the Gaps
aliases:
  - Separate path generation from linking
  - Entry degradation ladder with diagnostics
  - Conservative link floors and proof-carrying links
status: established
maturity_caveat: the separation is sound; the ToolpathSet contract is too thin to carry clearance evidence (CAM-002)
type: architecture-garden-design
created: 2026-10-25
analyzed: 2026-10-25
analysis_author: claude-opus-5-5
repository: /home/manuel/code/wesen/dropcut-studio
repository_remote: git@github.com:wesen/dropcut-studio.git
repository_commit: f3ebac2d5291b4a371bde25ae3a44d6f752cff41
tags:
  - architecture-garden
  - dropcut-studio
  - planning
  - cam
  - safety
  - plugins
related_files:
  - packages/planner/src/types.ts
  - packages/planner/src/run.ts
  - packages/planner/src/linker.ts
  - packages/planner/src/entry.ts
  - packages/planner/src/refine.ts
  - packages/strategies/src/registry.ts
  - packages/strategies/src/zlevel-rough.ts
  - packages/strategies/src/constant-scallop.ts
  - ttmp/2026/08/11/CAM-002--stock-aware-pocket-linking-and-consistent-cam-planning-architecture/design-doc/01-stock-aware-pocket-linking-architecture-and-implementation-guide.md
related_notes:
  - "[[Research/Software Architecture Garden/dropcut-studio/claude-opus/05 - Graded Evidence Certificates - Say What Was Verified and to What Resolution]]"
  - "[[Research/Software Architecture Garden/dropcut-studio/claude-opus/06 - Branch-and-Bound Spatial Queries - Tight Bounds Beat Fast Code]]"
---

# Strategies Produce Geometry, the Planner Owns the Gaps

A machining operation produces a set of cutting paths. Between any two of them the tool must get from one end to the next start, and how it does that — stay down and cut across, or lift, rapid over and descend again — decides both cycle time and whether the tool survives. In the prototype, path generation and linking were interleaved in one 460-line `generateJob` function. DROPCUT Studio splits them: strategies return geometry, and the planner alone decides every transition. This chapter explains that split, the entry ladder and conservative floors the planner applies, a bug the split let the simulator find, and the limit the split has reached.

> [!summary]
> - A strategy implements `plan(ctx, params) → ToolpathSet`: independent paths, their purpose, a stepover, optional diagnostics. It never emits traverses, entries or spindle commands.
> - `runPlan` owns tool changes, spindle scoping, path ordering, linking, entry and final retract, and memoises expensive geometry per operation.
> - Entry follows a **degradation ladder** — helix, ramp, plunge — and every degradation emits an `entry.degraded` diagnostic.
> - Retracts are floored at the **stock top**. That floor exists because the simulator caught rapids ploughing through 12.9 mm of uncut stock.
> - The limit: `ToolpathSet` carries geometry but no clearance evidence, so the planner must infer semantics from endpoints. Distance is used where proof is needed. CAM-002 designs the fix.

## 1. Two kinds of decision

A **strategy** decides *where material is removed*: the shape of each pass for a given tool and part. Raster finishing, constant-scallop finishing, Z-level roughing and pocketing are strategies. A **link** decides *how the tool moves between passes*. An **entry** decides *how the tool descends into material* at the start of a pass.

These are different kinds of decision with different inputs. A strategy needs the CL surface and the operation's parameters. A link needs the current material state between two points. An entry needs the local free space and the tool's cutting geometry. Putting them in one function means every strategy reimplements linking, and a linking fix must be applied in every strategy.

## 2. The strategy contract

`packages/planner/src/types.ts` defines the boundary:

```ts
export interface ToolpathSet {
  readonly paths: readonly Path<"work">[];
  readonly purpose: CuttingPurpose;       // "rough" | "finish" | ...
  readonly description: string;           // "constant scallop: 47 contours"
  readonly stepover: Mm;                  // for the error budget, UI and link thresholds
  readonly diagnostics?: readonly Diagnostic[];
}

export interface ToolpathStrategy<P = unknown> {
  readonly name: string;
  plan(ctx: PlanningContext, params: P): ToolpathSet;
}
```

The comment on `ToolpathSet` names the decision explicitly: *linking between them is the planner's job, not the strategy's — that separation is what the prototype's `generateJob` collapsed.*

Strategies receive a `PlanningContext` that gives them geometry services and nothing else: the mesh, the tool, the setup, padded bounds, a cancellation signal, a progress callback, a memoised CL evaluator `evaluate(inflate)` and a memoised CL field `cutterLocationField(spacing, inflate)`. They cannot emit commands because the context offers no way to.

### 2.1 Dependency direction

`@cam/planner` does not import `@cam/strategies`. The dispatch function lives in `packages/strategies/src/registry.ts` and is injected into the runner:

```ts
const run = runPlan(script.plan, { mesh, strategies: dispatchStrategy });
```

The registry's comment states the consequence: strategies know about the planner's context type; the planner does not know which strategies exist. Adding a strategy edits the registry and nothing else.

### 2.2 Two strategy-side ideas worth naming

**Surface inflation for stock-to-leave.** Z-level roughing must leave an allowance on the part for the finishing pass. Instead of offsetting paths afterwards, `planZLevelRough` evaluates the CL surface for a tool grown by the allowance — `ctx.evaluate(allowance)`. The drop-cutter adds `inflate` to the tool radius and then to the tip height, so the resulting surface is offset outwards by exactly the allowance. One parameter, no special cases, and it composes with every downstream consumer of the surface.

**The field decides where, the evaluator decides how deep.** Constant-scallop finishing solves an Eikonal equation $|\nabla T| = \sqrt{1 + |\nabla f|^2}/s_0$ on a sampled CL field and takes integer level sets of $T$ as passes, so passes are a constant distance apart *on the surface* rather than in XY. The contours come from the interpolated field, but each contour is lifted onto the **exact** CL evaluator with adaptive chord refinement (`liftPolyline` in `refine.ts`), which subdivides any span whose midpoint deviates from the surface by more than the chord tolerance. Bilinear interpolation never decides cutting depth. That is what makes the `chord-refinement` entry in the error budget a guarantee rather than an estimate.

## 3. What the planner owns

`runPlan` in `packages/planner/src/run.ts` turns a plan into canonical commands. For each operation:

```text
if tool differs:   spindle off (if running) → tool change
if spindle off:    spindle on at the operation's speed
comment            "<op id> (<op kind>)"
set   = strategy(ctx, op)
paths = orderPaths(set.paths, cursor)          // greedy nearest-neighbour, may reverse open paths
for each path p:
    first path:    traverse at clearance → entry → cut
    later paths:   link = planLink(cursor, p.start)
                   if link.kind == "retract": entry from link.leavesAtZ
                   cut
traverse to clearance                          // end of operation
```

At the end of the plan it appends a spindle-off if the spindle is still running. Every command carries provenance — operation id, strategy description, path index — so a later diagnostic can say *finishSurface #2, path 41* instead of *line 9,214*.

## 4. The link decision

`planLink(from, to, opts)` returns one of two decisions.

**Stay down** requires *both* a short XY gap — at most `max(3 × stepover, 1.5 mm)` — *and* a straight-line clearance test: the surface is sampled along the link at intervals of about half a tool radius and must never rise above the linearly interpolated tool height. The link is emitted as a cut at feed with purpose `lead-in`.

**Retract** otherwise. The retract height is

$$
z_{\text{safe}} = \max\Big(\min\big(z_{\text{clearance}},\; \max_{\text{along}} \text{surface} + 0.6\big),\; z_{\text{stockTop}},\; z_{\text{from}},\; z_{\text{to}}\Big)
$$

and the link is a traverse with `allowCoordinated: false` that ends *at the safe height above the target*, not at cutting depth. The entry planner then descends under feed control.

Both terms of that formula encode a defect the simulator found.

### 4.1 Two bugs the dexel simulator caught

The README records the first run of the material simulator over a real compile: *it reported a rapid ploughing through 12.9 mm of stock.* Retract heights were computed from the **part** surface. On a finishing-only job, the material above the part has not been removed, so a "local safe height" a little above the part lay deep inside solid stock. The fix is the $z_{\text{stockTop}}$ floor, with this comment in `LinkOptions`:

> Computing a "local safe height" from the part alone produced rapids that ploughed through 12.9 mm of untouched stock — caught by the dexel simulator, not by any amount of staring at the code.

The second defect had traverses *ending* at cutting depth, so the final descent of each link was a rapid into material. The fix is `LinkDecision.leavesAtZ`: a retract leaves the tool at the safe height, and descending is the entry planner's job.

Both bugs illustrate why the separation matters. Because linking was one function with one contract, both fixes were local. Because simulation ran on the *emitted* motion (chapter 05), it saw the real rapids rather than the planner's intentions.

## 5. The entry ladder

An end mill has zero surface speed at its centre, so plunging straight down rubs rather than cuts. `planEntry` in `packages/planner/src/entry.ts` tries entries in preference order and uses each only if it fits:

| Rung | Fits when | Shape |
|---|---|---|
| Helix | the first cut direction offers more than one orbit diameter, and 12 sample points of the orbit are clear at depth | orbit at radius $R/2$ descending at the ramp angle, one flat revolution at depth, return to the entry point |
| Ramp | at least 0.8 mm of run along the first cut direction | zig-zag along the cut direction, descending each way, ending at the entry point |
| Plunge | always | straight down at plunge feed |

Every rung below the requested one emits an info diagnostic:

```text
entry.degraded: no room to helix; using a ramp entry instead
entry.degraded: no room to helix or ramp; plunging straight down, which is hard on the tool
```

The comment explains why this matters: *the prototype degraded silently, which meant a user could get plunge entries throughout a job and never know why their tools were dying.* A fallback without a diagnostic converts a planning limitation into an unexplained hardware cost.

Only roughing and pocket operations go through the ladder. Every other operation — finishing, facing, drilling — gets a straight controlled descent from `entryCommands`. Finishing paths start on the CL surface, so a ramp would only waste time. The descent is emitted as a **cut at plunge feed, not a rapid**, because it may pass through material roughing did not remove.

## 6. The limit of the separation

The separation is right. The contract between the two sides is too thin. CAM-002 (`ttmp/2026/08/11/CAM-002--…`) documents the visible symptom: an 8 mm rectangular pocket with 2 mm stepdowns retracts and re-enters four times inside one pocket.

The cause is an information mismatch across the strategy boundary, summarised in CAM-002's own table:

| Layer | Knows | Does not know |
|---|---|---|
| Pocket strategy | ring geometry, level order, that the centre is already cleared | global machine state |
| `ToolpathSet` | independent paths and a stepover | dependencies, cleared regions, link permissions |
| Generic linker | endpoints, static part surface, stock top | evolving material state, operation topology |
| Dexel simulator | evolving stock after emission | any way to revise planner choices |

The strategy *knows* the link from the outer corner of level $i$ back to the centre is through cleared material. It has no field in which to say so. The linker therefore sees a 6.95 mm gap, compares it with a 3.81 mm stay-down threshold, and retracts. Each layer behaves correctly for what it knows.

Two observations from that analysis generalise beyond pockets.

- **Distance is a cost heuristic, not a collision predicate.** A short link can cross an uncut island; a long link can be safe through a cleared cavity. Raising `stayDownDistance` would make the pocket look better by authorising links on proximity instead of proof.
- **Path reversal and reordering are semantic decisions.** `orderPaths` treats open paths as reversible: *a path is just as machinable backwards.* Geometrically that is true; mechanically, reversing a pass swaps climb and conventional milling, and reordering can move a deeper level before a shallower one. `ToolpathSet` cannot express "reversible but not reorderable across levels".

CAM-002 proposes three phases: a continuous pocket path whose level transitions return through the cleared centre (a local fix whose safety rests on a stated invariant); typed machining spans and links that preserve topology; and a conservative removal-state query, analytic for 2.5D regions first, sampled later, that link planning can consult. The direction is the right one: links should carry **clearance proof** produced by whoever has the knowledge, and the generic linker should stay conservative when no proof is supplied.

> [!note]
> CAM-002 §4.7 states that pockets are passed to the entry planner in plunge mode. At `f3ebac2`, `entryCommands` passes `"auto"` for every non-roughing operation that reaches the ladder, including pockets, with a 3° ramp angle. The repeated vertical columns CAM-002 describes are therefore entries that degrade to plunges because the next ring offers too little run, not plunges requested by mode.

## 7. Why tempting alternatives are wrong

**Let each strategy link its own paths.** It moves the safety-relevant decision into every strategy. The stock-top floor fix would have had to be applied six times.

**Expose `keepToolDown: true`.** A user switch cannot mean "emit direct motion regardless of material". At most it is a preference the planner honours when it can prove the link clear.

**Use the post-emission simulator as the planner's oracle.** It is a verifier at a sampling resolution. Planning against it would make the verifier's approximations into planning decisions and destroy its independence as evidence.

## 8. Applicability

The pattern — producers emit content, a coordinator owns every transition between content items — appears wherever transitions carry their own risk or cost: print and plotter drivers (pen-up moves), robot motion planning (approach and retreat), animation systems (transitions between clips), deployment orchestrators (draining between versions), and build systems (handoff between steps). The common lesson from CAM-002 is that the coordinator can only be as good as the evidence producers can hand it; a thin content-only contract forces conservative or heuristic transitions.

## 9. Candidate ecosystem guidance

1. Keep content generation and transition planning in separate components with a typed boundary.
2. Inject the plugin dispatch into the coordinator so the coordinator never imports its plugins.
3. Make fallbacks a ladder, and emit a diagnostic at every rung below the requested one.
4. Floor safety-relevant heights or limits at the most conservative state the coordinator can know (stock top, not part surface), and lower them only with evidence.
5. End a link in a safe state and hand descent to the component that controls it.
6. When a producer knows a transition is safe, give the contract a way to say so — clearance proof, not a distance threshold.
7. Treat ordering and reversal as semantic, and let producers constrain them.

## 10. Evidence and references

- `packages/planner/src/types.ts` — `ToolpathSet`, `ToolpathStrategy`, `PlanningContext`.
- `packages/planner/src/run.ts:55` (`runPlan`), `:237` (`entryCommands`), `:331` (`makeContext` memoisation).
- `packages/planner/src/linker.ts:72` (`planLink`), `:125` (`isStraightLinkClear`), `:175` (`orderPaths`, reversal).
- `packages/planner/src/entry.ts:50` (`planEntry`), `:94` (`tryHelix`), `:148` (`tryRamp`).
- `packages/planner/src/refine.ts` — `refineSpan`, `liftPolyline`.
- `packages/strategies/src/registry.ts` — `dispatchStrategy`.
- `packages/strategies/src/zlevel-rough.ts`, `constant-scallop.ts` — surface inflation; Eikonal level sets lifted onto the exact evaluator.
- README, "The simulator found bugs review did not."
- CAM-002 design doc §1, §4.5–4.8, §5.
