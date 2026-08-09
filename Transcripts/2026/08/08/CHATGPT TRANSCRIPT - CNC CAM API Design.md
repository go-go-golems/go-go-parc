# CNC CAM API Design

- URL: https://chatgpt.com/c/6a77105f-7298-83ea-8058-ea1c9f9fc732
- Created: 2026-08-08T11:17:53.180Z

---

> We want to create a JS API / intermediate representation for CNC CAM programs, that can be compiled / interpreted to create G-Code ultimately. It should allow geometry but also machine actions, and ultimately present a nice API to create milling geometry.
>
>
>
> Use mathematical concepts to design the API, think category theory, denotational semantics, operational semantics, so that we can design something composable and with guarantees.
>
>
>
> Here's a g-code cheatsheet and an example test CAM thing I did yesterday (not guaranteed to be correct).
>
>
>
> \---
>
>
>
> # G-code Cheatsheet
>
> Scoped to the codes in `MakeraBadge.nc` plus the probing example, with the common neighbours you'll hit next.
>
> ---
>
> ## Core concepts
>
> | Term Meaning    |                                                                                      |
> | --------------- | ------------------------------------------------------------------------------------ |
> | **Word**        | One letter + number, e.g. `X14.81`. The letter is the address, the number the value. |
> | **Block**       | One line. All words in a block are evaluated together, not sequentially.             |
> | **Modal**       | Stays active until replaced. `G90`, `G21`, `G1`, `F`, `S` are modal.                 |
> | **Non-modal**   | Fires once, then gone. `G4`, `G28`, `G53`, `G38.x`.                                  |
> | **Modal group** | Only one member active at a time. `G0`/`G1`/`G2`/`G3` are all group 1.               |
>
> **Rule of thumb:** if a move behaves strangely, check what modal state is actually active, not the line that moved. Stale `G91`, stale `G20`, and stale work offsets cause most surprises.
>
> ---
>
> ## Motion
>
> | Code Name Notes  |                |                                                                                                                                                                              |
> | ---------------- | -------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
> | `G0`             | Rapid traverse | Max machine speed. Ignores `F`. Classically axes may move at independent rates (dogleg path) — do not assume a straight line for clearance. Positioning only, never cutting. |
> | `G1`             | Linear feed    | Coordinated straight line at the active `F`. The workhorse.                                                                                                                  |
> | `G2`             | Arc CW         | Center form `G2 X.. Y.. I.. J..` (I/J = center offset *from start point*) or radius form `G2 X.. Y.. R..`.                                                                   |
> | `G3`             | Arc CCW        | Same syntax as `G2`.                                                                                                                                                         |
> | `G4`             | Dwell          | `G4 P1.5` — pause. Units of P vary by control (seconds vs ms).                                                                                                               |
>
> `I`/`J`/`K` are the arc center offsets for X/Y/Z respectively. Radius form is ambiguous for arcs near 180°; center form is safer for CAM output.
>
> **Multi-axis** **`G1`** **= a ramp.** `G1 X56.19 Y8.69 Z-1.5 F300` descends while moving in XY — that's how CAM enters material without plunging straight down.
>
> ---
>
> ## Coordinate & unit modes
>
> | Code Name Notes       |                     |                                                                                                               |
> | --------------------- | ------------------- | ------------------------------------------------------------------------------------------------------------- |
> | `G90`                 | Absolute            | Coordinates are positions.                                                                                    |
> | `G91`                 | Incremental         | Coordinates are distances from current position.                                                              |
> | `G20`                 | Inch                |                                                                                                               |
> | `G21`                 | Millimetre          |                                                                                                               |
> | `G17` / `G18` / `G19` | Plane select        | XY / XZ / YZ. Sets the arc plane and drill axis. `G17` is the default.                                        |
> | `G53`                 | Machine coordinates | **Non-modal, one-shot.** `G53 G0 Z-5` goes to machine Z−5 regardless of work offset. The safe way to retract. |
> | `G54`–`G59`           | Work offsets        | Where your part zero lives. Modal. Absent from the Makera file — it uses an implicit single offset.           |
>
> ---
>
> ## Feeds, speeds, tooling
>
> | Code Name Notes       |                                |                                                                                                                                         |
> | --------------------- | ------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------- |
> | `F`                   | Feedrate                       | mm/min under `G21 G94`. Modal — persists across blocks.                                                                                 |
> | `S`                   | Spindle speed                  | RPM. Modal. **Does not start the spindle.**                                                                                             |
> | `T`                   | Tool select                    | On machines with a carousel, `T` pre-stages and `M6` swaps. On simpler controls they're issued together.                                |
> | `G94`                 | Feed per minute                | Default on mills.                                                                                                                       |
> | `G95`                 | Feed per revolution            | Lathe convention.                                                                                                                       |
> | `G43` / `G49`         | Tool length offset on / off    | `G43 H1 Z..` applies the length in offset register H1. Absent from the Makera file — the Z1 handles TLO internally via its tool setter. |
> | `G41` / `G42` / `G40` | Cutter comp left / right / off | Control offsets the path by the tool radius. Most hobby CAM bakes compensation into the toolpath instead and never emits these.         |
>
> ---
>
> ## M-codes (machine functions)
>
> | Code Meaning  |                                                                      |
> | ------------- | -------------------------------------------------------------------- |
> | `M3`          | Spindle on, clockwise (at the active `S`)                            |
> | `M4`          | Spindle on, counter-clockwise                                        |
> | `M5`          | Spindle stop                                                         |
> | `M6`          | Tool change                                                          |
> | `M8` / `M9`   | Flood coolant on / off                                               |
> | `M0`          | Program pause, resume on operator input                              |
> | `M1`          | Optional stop (only if the panel switch is on)                       |
> | `M2`          | Program end                                                          |
> | `M30`         | Program end + rewind. Usually also resets modals — prefer over `M2`. |
>
> `M02` and `M2` are identical; leading zeros are cosmetic. Your file uses `M5` in one place and `M05` in another, which is harmless but reveals inconsistent post-processor templates.
>
> ---
>
> ## Homing
>
> | Code Behaviour  |                                                                                         |
> | --------------- | --------------------------------------------------------------------------------------- |
> | `G28`           | Return to reference (home) position.                                                    |
> | `G28 X0 Y0`     | Go to the **intermediate point** X0 Y0 in the *current* coordinate system, *then* home. |
> | `G30`           | Return to secondary reference point.                                                    |
>
> **Hazard:** the intermediate point is the classic `G28` crash. `G28 Z0` in a work offset where Z0 is the part top will drive the tool into the part on its way home. Retract with `G53 G0 Z…` first, or issue `G28` bare.
>
> ---
>
> ## Probing
>
> Two dialects for the same operation: move toward a target, abort the move the moment the probe input changes state, and latch where it happened.
>
> ### LinuxCNC / Mach / GRBL
>
> | Code Direction On no-contact  |                                   |                   |
> | ----------------------------- | --------------------------------- | ----------------- |
> | `G38.2`                       | Toward workpiece, stop on contact | **Error**         |
> | `G38.3`                       | Toward workpiece, stop on contact | Continue silently |
> | `G38.4`                       | Away, stop on loss of contact     | **Error**         |
> | `G38.5`                       | Away, stop on loss of contact     | Continue silently |
>
> Use `.2` unless you have a specific reason not to. A silent failure feeds a garbage coordinate into everything downstream.
>
> ### Fanuc / Haas
>
> `G31 Z-100 F200` — skip function. One form only, no error variant. Verify success yourself by checking the trip position against the commanded endpoint, or by reading the control's probe-status variable.
>
> ### Result variables
>
> | Variable Holds  |                               |
> | --------------- | ----------------------------- |
> | `#5061`         | X position at trip            |
> | `#5062`         | Y position at trip            |
> | `#5063`         | Z position at trip            |
> | `#5064`–`#5066` | A / B / C at trip             |
> | `#5070`         | Probe success flag (LinuxCNC) |
>
> Positions are reported in the **current coordinate system**, so a work offset change between probes invalidates the comparison.
>
> ### Probing rules that bite
>
> - **Two-pass always.** Fast approach to find the surface, retract, slow re-probe for the real number. Trip point shifts measurably with approach speed.
> - **Same tool offset for both hits**, or the subtraction is meaningless.
> - **Pretravel cancels** when subtracting two probes with the same stylus, so thickness measurement needs no compensation term. Absolute Z does.
> - Single-block the first run. Always.
>
> ---
>
> ## What `MakeraBadge.nc` actually uses
>
> ```
> G0 G1 G21 G28 G90    M02 M3 M5 M6    T1 T2    X Y Z F S
>
> ```
>
> That's the entire vocabulary. Twelve codes and eight addresses.
>
> Notable by absence: **no arcs** (every curve is polylined into short `G1` segments — hence 17,439 of them), no cutter comp, no work offset call, no tool length offset, no canned cycles, no macro variables, no coolant. Modal state is established once on line 17 and never revisited.
>
> This is characteristic of hobby-CAM output: maximally explicit, minimally clever, and portable to nearly any interpreter because it leans on almost no optional features.
>
> ---
>
> ## Minimal safe program skeleton
>
> ```
> G90 G21 G94 G17          ; absolute, mm, feed/min, XY plane
> G53 G0 Z-5               ; retract in machine coords — safe from any state
> T1 M6                    ; tool change
> G54                      ; work offset
> S10000 M3                ; spindle up to speed
> G0 X0 Y0                 ; position clear of the part
> G0 Z5                    ; approach height
> G1 Z-1 F300              ; plunge
> G1 X50 Y50 F1000         ; cut
> G0 Z5                    ; retract
> G53 G0 Z-5               ; safe Z before anything else moves
> M5                       ; spindle off
> G28                      ; home
> M30                      ; end and reset
>
> ```
>
> The two `G53 G0 Z-5` lines are the load-bearing ones. Retracting in machine coordinates is immune to whatever work offset or modal state is active.

I’ll treat the uploaded Dropcut prototype as the concrete reference implementation, then separate its geometry, planning, machine semantics, verification, and G-code concerns into a typed/composable IR. I’ll also distinguish what should be mathematically pure from what is controller/postprocessor-specific.

```json
{"system2_search_query":[{"q":"site:linuxcnc.org docs G-code overview RS274NGC modal groups LinuxCNC official"},{"q":"site:nist.gov RS274NGC interpreter PDF Kramer Proctor Messina"},{"q":"site:step-nc.org STEP-NC AP238 official overview CNC manufacturing"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Searched 5 websites**

</details>

```unknown
from pathlib import Path
p = Path("/mnt/data/dropcut-cam(1).jsx")
text = p.read_text()
len(text), text.count("\n"), text[:200]

```

<details><summary>💭 Thinking</summary>

**Inspected JSX structure and extracted top-level functions**

</details>

```json
{"system1_search_query":[{"q":"STEP-NC AP238 official ISO CNC workingsteps toolpath canonical machining functions"},{"q":"site:iso.org ISO 14649 STEP-NC milling workingsteps"},{"q":"site:nist.gov STEP-NC AP238 machining workingsteps NIST"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Searched 10 websites**

</details>

The strongest precedent is NIST’s RS274/NGC architecture: its interpreter translates modal G-code into **canonical machining functions**. For this project, I would use essentially the opposite direction: a semantic/canonical machining IR first, with G-code as one backend encoding. 

That also aligns with STEP-NC’s distinction between feature/operation-level “working steps” and low-level controller motion.

```json
{"system1_search_query":[{"q":"site:nist.gov \"canonical machining functions\" STRAIGHT_FEED ARC_FEED SET_FEED_RATE"},{"q":"site:linuxcnc.org \"canonical machining functions\" CNC"}],"response_length":"short"}
```

<details><summary>💭 Thinking</summary>

**Designing the CAM architecture**

I’m shaping the API around a semantic intermediate representation rather than raw G-code: geometry and intent first, explicit machine-independent motion next, then capability-aware lowering, verification, and postprocessing.

**Designed the CAM architecture**

**Searched 5 websites**

</details>

The uploaded prototype already contains the right *algorithmic* pieces—drop-cutter evaluation, sampled cutter-location fields, raster/hybrid/constant-scallop strategies, entry generation, arc fitting, verification, and G-code output—but they are coupled inside `generateJob`, `toGcode`, and `verifyJob`. The redesign should preserve those algorithms while replacing the untyped `{ kind, phase, pts, ops }` representation with explicit semantic objects.

Yes. The key design decision is:

> **Do not make G-code the semantic model. Make machining the semantic model, and treat G-code as one serialization/backend.**

That is very close to the architecture behind NIST's RS274/NGC work: its interpreter converts modal G-code into canonical machining functions. We want the reverse direction—construct canonical machining semantics first, then compile them to LinuxCNC, GRBL, Fanuc, Makera, etc. citeturn120405search0turn120405search5

STEP-NC points in the same direction at a higher abstraction level: it separates manufacturing features, working steps, technology parameters, and machine functions rather than reducing the process immediately to axis commands. citeturn557866search1turn557866search4

Your current Dropcut implementation already has most of the interesting CAM algorithms, but `generateJob()` currently conflates strategy planning, path construction, linking, clearance, feeds, entry methods, and the final move representation. Arc fitting, G-code generation, and verification then operate on that ad-hoc `{kind, phase, pts, ops}` representation. fileciteturn0file0

I would replace that with the following architecture.

---

# 1. The semantic stack

Think of the system as five languages:

| Layer | Describes | Example |
|---|---|---|
| **Geometry** | What physical things exist | stock, target part, fixture, cutter |
| **Manufacturing intent** | What should be done | rough this region, finish this surface |
| **Canonical machining IR** | Machine-independent physical actions | traverse, cut along curve, change tool, probe |
| **Machine IR** | Actions after machine capability/kinematic resolution | coordinated X/Y/Z move, spindle, fixture selection |
| **G-code IR/text** | Controller encoding | `G1 X10 Y20 F600` |

So:

```text
Geometry
   ↓
Manufacturing Plan
   ↓ planning
Canonical Machining IR
   ↓ machine lowering + validation
Machine Program
   ↓ postprocessor
G-code blocks
   ↓ pretty-print/modal compression
.nc
```

And verification should work primarily on the **canonical machining IR**, not on G-code text.

This gives us a compiler rather than a string generator.

---

# 2. Three mathematical objects sit at the center

There are three particularly useful mathematical models here.

## Geometry is sets and transformations

A solid is conceptually a subset

\[
S \subseteq \mathbb R^3.
\]

A tool is another solid

\[
T \subseteq \mathbb R^3.
\]

A coordinate frame transformation is an element of the rigid-motion group

\[
SE(3).
\]

For a simple 3-axis mill, much of the time we only need translations plus a fixed orientation, but designing around `SE(3)` means 4/5-axis machining doesn't require replacing the entire abstraction later.

This immediately suggests a typed geometry API:

```ts
const stock = box({
  x: mm(60),
  y: mm(40),
  z: mm(12),
});

const part = mesh(stl);

const fixture = frame("G54", {
  origin: vec3(mm(0), mm(0), mm(0)),
});
```

Crucially, **points should belong to frames**.

```ts
Point3<"part">
Point3<"machine">
Point3<"fixture:G54">
```

Mixing a machine-coordinate point with a work-coordinate point should not silently work.

That eliminates an entire class of CNC failures.

---

# 3. Paths naturally form a category

This is one of the category-theory ideas that is genuinely useful rather than decorative.

A path has a start pose and an end pose:

\[
p : A \to B.
\]

Another path might be

\[
q : B \to C.
\]

Then composition is possible:

\[
q \circ p : A \to C.
\]

But this:

\[
A\to B
\qquad
D\to E
\]

cannot be composed unless \(B=D\).

That is exactly the invariant we want for toolpaths.

So instead of:

```ts
[
  0, 0, 5,
  10, 0, 5,
  10, 10, -2
]
```

we want:

```ts
const path =
  Path.at(p(0, 0, 5))
    .lineTo(p(10, 0, 5))
    .lineTo(p(10, 10, -2));
```

Internally:

```ts
interface Path<A extends Pose, B extends Pose> {
  readonly start: A;
  readonly end: B;
  readonly segments: readonly Segment[];
}
```

And:

```ts
concat(
  p1: Path<A, B>,
  p2: Path<B, C>
): Path<A, C>
```

Composition is associative:

\[
(r\circ q)\circ p
=
r\circ(q\circ p)
\]

and the zero-length stationary path serves as the identity.

That makes toolpath concatenation an actual algebra with laws that can be property-tested.

---

# 4. But a path is not yet a machining action

This distinction is important.

The same geometric curve could mean:

```text
rapid through free space
cut material
probe toward a surface
feed while not cutting
lead-in
retract
```

So separate:

```ts
Curve
```

from:

```ts
Motion
```

For example:

```ts
type Motion =
  | Traverse
  | CuttingMove
  | ProbeMove;
```

A cutting move might be:

```ts
interface CuttingMove {
  kind: "cut";
  path: ToolPath;
  feed: FeedRate;
  tool: ToolRef;
  intent:
    | "rough"
    | "finish"
    | "plunge"
    | "ramp"
    | "lead-in"
    | "lead-out";
}
```

A traverse is semantically different:

```ts
interface Traverse {
  kind: "traverse";
  path: ToolPath;
  clearance: ClearanceRequirement;
}
```

Notice that there is no `G0`.

That's deliberate.

A postprocessor might implement a traverse as:

```text
G0 Z...
G0 X... Y...
G0 Z...
```

instead of:

```text
G0 X... Y... Z...
```

if the controller's rapid motion is not guaranteed to follow a coordinated straight line.

The high-level program asked for **safe traversal**, not for the byte sequence `G0`.

---

# 5. Denotational semantics of cutting

This gives us an exceptionally clean definition of what machining means.

Let the cutter occupy solid \(T\).

Let its trajectory be

\[
\gamma : [0,1]\rightarrow SE(3).
\]

The swept cutter volume is:

\[
\operatorname{Sweep}(T,\gamma)
=
\bigcup_{t\in[0,1]}
\gamma(t)T.
\]

If the current stock is \(S\), executing a cutting motion gives:

\[
S'
=
S\setminus\operatorname{Sweep}(T,\gamma).
\]

That is the denotational meaning of a cutting operation.

A rapid move has:

\[
S'=S.
\]

A finish operation doesn't fundamentally mean "lots of G1 instructions."

It means:

\[
S
\longmapsto
S\setminus V
\]

for some generated swept volume \(V\).

This gives us a much stronger basis for verification.

### Gouging

Let \(P\) be material that must remain in the final part.

A no-gouge condition is essentially:

\[
\operatorname{Sweep}(T,\gamma)
\cap
P_{\mathrm{protected}}
=
\varnothing.
\]

With an allowance \(a\), the protected region changes accordingly.

Your drop-cutter evaluator can therefore be seen as a specialized solver for finding cutter poses whose swept cutter geometry remains outside the protected part.

Your current `makeEvaluator()` is already computationally approximating exactly this sort of geometric relationship. fileciteturn0file0

---

# 6. Programs need effects, not just path composition

Category theory gives us another useful construction here.

Machine actions affect state:

```ts
interface MachineState {
  pose: Pose;
  tool: ToolId | null;
  spindle: SpindleState;
  coolant: CoolantState;
  fixture: FixtureFrame;
}
```

Executing a command has semantics approximately:

\[
\llbracket c\rrbracket :
\Sigma
\rightarrow
\operatorname{Result}(\Sigma\times Trace,\ Error)
\]

where \(\Sigma\) is the complete machining state.

So:

```text
command
    MachineState
        ↓
 Result<MachineState + physical trace>
```

Sequential composition is then equivalent to composition in the Kleisli category of something like:

```text
State
+ Error
+ Trace
```

In programming terms, it's approximately the combination of a State, Result, and Writer effect.

This isn't terminology we need to expose in the API. But it gives us precise laws.

For:

```ts
seq(a, b, c)
```

the semantics are:

\[
\llbracket c\rrbracket
\mathbin{>=>}
\llbracket b\rrbracket
\mathbin{>=>}
\llbracket a\rrbracket.
\]

If `b` fails its precondition, `c` cannot execute.

---

# 7. Canonical IR

I would make the central IR roughly this:

```ts
type CanonicalCommand =
  | ToolChange
  | Spindle
  | Coolant
  | Traverse
  | Cut
  | Probe
  | Dwell
  | Pause;
```

For example:

```ts
interface ToolChange {
  kind: "tool-change";
  tool: ToolRef;
}

interface Spindle {
  kind: "spindle";
  state:
    | { mode: "off" }
    | {
        mode: "cw" | "ccw";
        speed: RPM;
      };
}

interface Traverse {
  kind: "traverse";
  path: Path;
}

interface Cut {
  kind: "cut";
  path: Path;
  feed: FeedRate;
  tolerance: Length;
  purpose: CuttingPurpose;
}

interface Probe {
  kind: "probe";
  path: Path;
  feed: FeedRate;
  failure: "abort" | "continue";
  result: ProbeVariable;
}
```

The IR is deliberately **non-modal**.

Every cutting motion knows its feed.

Every spindle operation knows its speed.

Every path knows its frame.

Every arc knows its plane geometrically, rather than depending on stale `G17/G18/G19`.

G-code's modal groups are a property of the target language; LinuxCNC itself treats motion, plane selection, units, distance mode, feed-rate mode, coordinate systems, etc. as separate modal groups. citeturn120405search5

We should not infect the source language with those semantics.

---

# 8. G-code modal state becomes a compiler optimization

Suppose our canonical IR contains:

```ts
cut(lineA, feed(600));
cut(lineB, feed(600));
cut(lineC, feed(600));
```

Semantically each operation says `600 mm/min`.

The G-code postprocessor can observe:

```text
previous feed = 600
required feed = 600
```

and omit the redundant `F600`.

Likewise:

```text
currentPlane = XY
requiredPlane = XY
```

means don't emit another `G17`.

So:

```ts
Canonical Program
       ↓
explicit GCodeBlocks
       ↓
modal-state compression
       ↓
text
```

The compiler—not the programmer—owns modal state.

This converts G-code's dangerous hidden state into a mundane backend compression problem.

---

# 9. High-level manufacturing IR

Canonical moves are still too low-level for the API you actually want users to write.

Above them should be a manufacturing-plan layer:

```ts
type MillingOperation =
  | Face
  | Pocket
  | Profile
  | SurfaceRough
  | SurfaceFinish
  | Drill
  | Chamfer
  | ProbeOperation;
```

For example:

```ts
mill.surfaceFinish({
  surface: part.exterior(),
  tool: ballNose({
    diameter: mm(3),
  }),

  strategy: constantScallop({
    scallop: mm(0.01),
  }),

  tolerance: mm(0.01),
});
```

Your current strategies map cleanly to this layer:

```ts
raster(...)
hybridWaterline(...)
constantScallop(...)
```

The Eikonal solver belongs inside `constantScallop`, not inside the program representation.

Likewise:

```ts
rough({
  stepdown: mm(1.5),
  stepover: percent(45),
  stockToLeave: mm(0.2),
  entry: autoEntry({
    maxRampAngle: deg(3)
  })
})
```

could encapsulate much of your present roughing code. fileciteturn0file0

---

# 10. Preserve manufacturing features

The geometry API should not only expose generic meshes.

These:

```ts
Solid
Surface
Curve
Region2
```

are useful.

But so are:

```ts
Pocket
Hole
Boss
PlanarFace
FreeformSurface
Profile
Slot
```

because machining meaning is attached to them.

Compare:

```ts
remove(solid)
```

with:

```ts
mill.pocket(pocket, {...})
```

The second tells the planner a huge amount.

This is one of the useful ideas behind STEP-NC: its process model retains geometric and technological/manufacturing information above the raw axis-motion layer. citeturn557866search1turn557866search4

You don't need to implement STEP-NC, but you should borrow this idea.

---

# 11. The user-facing API could look like this

For example:

```ts
import {
  cam,
  mm,
  rpm,
  mmPerMin,
  deg,
} from "@mill/core";

const T1 = cam.tools.ballEndMill({
  name: "3mm ball",
  diameter: mm(3),
  fluteLength: mm(12),
});

const stock = cam.geometry.box({
  x: mm(50),
  y: mm(50),
  z: mm(15),
});

const part = cam.geometry.mesh(stl);

const setup = cam.setup({
  stock,
  part,

  fixture: cam.frame.workpiece({
    id: "top",
    origin: [mm(0), mm(0), mm(0)],
  }),
});

const plan = cam.plan(setup)

  .roughSurface({
    target: part,

    tool: T1,

    stepdown: mm(1.5),
    stepover: 0.45,
    stockToLeave: mm(0.2),

    entry: cam.entry.auto({
      maxRampAngle: deg(3),
    }),
  })

  .finishSurface({
    target: part,

    tool: T1,

    strategy: cam.strategy.constantScallop({
      height: mm(0.01),
    }),

    chordTolerance: mm(0.01),
  });
```

Then:

```ts
const canonical =
  await cam.planToolpaths(plan);
```

This returns **no G-code**.

It returns semantic machining operations.

---

# 12. Compilation should be explicit

Then:

```ts
const machine = machineProfile({
  axes: "XYZ",

  travels: {
    x: range(mm(-5), mm(300)),
    y: range(mm(-5), mm(180)),
    z: range(mm(-80), mm(0)),
  },

  spindle: {
    min: rpm(3000),
    max: rpm(24000),
  },

  rapid: {
    semantics: "axis-independent",
  },

  arcs: {
    xy: true,
    xz: true,
    yz: true,
    helical: false,
  },

  probing: "g38",
});
```

Then:

```ts
const result =
  await cam.compile(canonical, machine);
```

Maybe:

```ts
result.program
result.diagnostics
result.analysis
```

and finally:

```ts
const nc =
  linuxCNC.emit(result.program);
```

or:

```ts
const nc =
  makera.emit(result.program);
```

---

# 13. The really useful type trick: certified stages

Don't let these all have the same TypeScript type.

For example:

```ts
type PlannedProgram = ...
type LoweredProgram = ...
type ValidatedProgram = ...
type PostprocessedProgram = ...
```

Then:

```ts
plan(): PlannedProgram

lower(
  PlannedProgram,
  MachineProfile
): LoweredProgram

validate(
  LoweredProgram,
  Scene
): Result<ValidatedProgram, ValidationError[]>

emit(
  ValidatedProgram,
  PostProcessor
): GCode
```

The postprocessor cannot accidentally accept an arbitrary half-generated program.

You can enforce it with an unexported brand:

```ts
declare const validated:
  unique symbol;

export interface ValidatedProgram
  extends LoweredProgram {
  readonly [validated]: true;
}
```

Only the verifier module can create that value.

This isn't a mathematical proof of machine safety—but it is a useful API proof that the requested validation pipeline ran.

---

# 14. Units should not be bare numbers

Currently:

```ts
diameter: 3
feed: 600
rpm: 10000
clearance: 5
```

all have the same JavaScript type.

That's unnecessary risk.

Use branded measures:

```ts
type Mm = number & Brand<"mm">;
type Inch = number & Brand<"inch">;

type RPM = number & Brand<"rpm">;
type MmPerMinute =
  number & Brand<"mm/min">;

type Degree =
  number & Brand<"degree">;
```

Then:

```ts
lineTo({
  x: rpm(10000)
});
```

is a compile error.

At API boundaries, runtime schemas must validate the brands because TypeScript is erased.

---

# 15. Frames deserve the same treatment

This is even more important than units.

Something like:

```ts
type Point3<F> = {
  x: Mm;
  y: Mm;
  z: Mm;

  frame: F;
};
```

Then:

```ts
const machineP:
  Point3<MachineFrame>;

const partP:
  Point3<PartFrame>;
```

cannot be subtracted without:

```ts
transform(partToMachine, partP)
```

Coordinate transformations are morphisms:

\[
T_{AB}:A\rightarrow B
\]

with composition:

\[
T_{BC}\circ T_{AB}
:
A\rightarrow C.
\]

Rigid frame transformations form a groupoid: every coordinate transformation has an inverse.

That is exactly the mathematical structure we need.

---

# 16. Toolpaths should be geometric objects, not arrays

An internal segment type could be:

```ts
type Segment =
  | Line
  | Arc
  | Helix
  | Bezier
  | BSpline;
```

An arc shouldn't contain G-code-ish `I/J/K`.

Use geometric data:

```ts
interface Arc<F> {
  kind: "arc";

  start: Point3<F>;
  end: Point3<F>;

  center: Point3<F>;
  axis: UnitVector3<F>;

  sweep: Radians;
}
```

Then LinuxCNC might lower it into:

```text
G17
G3 X... Y... I... J...
```

while another controller could choose radius notation, linearize it, or use some higher-order interpolation format.

---

# 17. Arc fitting becomes an optimization pass

Your current `compressCut()` / `fitArcsRun()` can survive nearly intact algorithmically. fileciteturn0file0

But its conceptual type should change from:

```text
Float32Array → G-code-ish ops
```

to:

```text
Polyline
    ↓ ArcFit(tolerance)
PiecewiseCurve
```

with a postcondition:

\[
d_H(P,C)\leq\epsilon
\]

where \(d_H\) is some chosen geometric deviation metric and \(\epsilon\) is the requested fitting tolerance.

Then:

```ts
arcFit({
  tolerance: mm(0.01)
})
```

is a semantics-preserving compiler optimization.

It knows nothing about `G17`.

Later:

```ts
lowerArcs(machine)
```

decides whether the controller can actually represent them.

---

# 18. Compiler correctness becomes a commuting diagram

The architectural invariant should be:

```text
Canonical program P
        │
        │ postprocessor
        ▼
      G-code
```

with:

\[
\operatorname{Semantics}_{machine}(P)
\approx_\epsilon
\operatorname{Semantics}_{controller}
(
\operatorname{post}(P)
).
\]

In other words, compiling shouldn't materially change what the tool does.

The \(\epsilon\) is important because linearization and arc fitting introduce finite geometric tolerances.

Every lowering pass could therefore carry a **certificate/budget**:

```ts
interface ErrorBudget {
  geometric: Mm;
  timing?: Seconds;
}
```

If:

```text
drop-cutter sampling     0.005 mm
arc fitting              0.010 mm
post linearization       0.002 mm
```

you don't pretend the output has 0.001 mm accuracy.

You propagate a conservative error budget.

This is an excellent place for formal semantics to directly improve practical CAM.

---

# 19. Safety as predicates on programs

We can write many CAM guarantees as predicates.

For a program \(P\):

\[
\operatorname{WithinTravel}(P)
\]

\[
\operatorname{NoFixtureCollision}(P)
\]

\[
\operatorname{NoGouge}(P)
\]

\[
\operatorname{ToolCompatible}(P)
\]

\[
\operatorname{FeedWithinLimits}(P)
\]

\[
\operatorname{SpindleWithinLimits}(P)
\]

\[
\operatorname{Continuous}(P)
\]

and:

\[
\operatorname{Safe}(P)
=
\bigwedge_i P_i.
\]

The validator then returns:

```ts
type Validation =
  | {
      ok: true;
      program: ValidatedProgram;
      certificate: SafetyCertificate;
    }
  | {
      ok: false;
      errors: Diagnostic[];
    };
```

A diagnostic should point back to the manufacturing operation that caused it:

```text
finishSurface #2
  → path 41
    → segment 307
      → exceeds machine X travel by 1.42 mm
```

So every lowering pass should retain source provenance.

---

# 20. Not all verification is equally strong

This matters with your current dexel simulator.

Your `verifyJob()` samples the machining result onto a heightfield/dexel representation and computes gouge/excess deviation. That's very useful, but it is a **numerical approximation**, not a mathematical proof that no collision occurs between samples. fileciteturn0file0

Therefore the API should distinguish:

```ts
analysis: "sampled"
```

from something like:

```ts
analysis: "conservative-bound"
```

or:

```ts
analysis: "exact"
```

if you someday have such a verifier.

For example:

```ts
certificate.gouge = {
  status: "verified-to-resolution",
  spatialResolution: mm(0.15),
  numericalTolerance: mm(0.01),
};
```

That's much better than:

```ts
safe: true
```

because it describes what has actually been established.

---

# 21. Operational semantics

For the core IR, I'd actually write down a small-step semantics in the design document.

Suppose:

\[
\sigma =
(p,t,s,c,w,S)
\]

contains pose, tool, spindle, coolant, work coordinate system, and stock.

A spindle transition could be:

\[
\frac
{r\in Machine.spindleRange}
{\langle SpindleCW(r),\sigma\rangle
\rightarrow
\sigma[s:=CW(r)]}
\]

A tool change might require:

\[
s=OFF.
\]

So:

\[
\frac
{\sigma.spindle=OFF}
{\langle ToolChange(T),\sigma\rangle
\rightarrow
\sigma[tool:=T]}
\]

A cutting operation might require:

\[
tool\neq\varnothing
\]

and:

\[
feed>0.
\]

Then:

\[
\langle Cut(\gamma),\sigma\rangle
\rightarrow
\sigma[
pose:=\gamma(1),
stock:=stock\setminus Sweep(tool,\gamma)
].
\]

This gives the IR an actual specification independent of any implementation.

That specification becomes the reference for tests and eventually formal verification.

---

# 22. Scope combinators can encode lifecycle guarantees

Instead of:

```ts
spindle.on();
...
...
...
spindle.off();
```

offer:

```ts
withSpindle(
  {
    speed: rpm(10_000),
    direction: "cw",
  },

  () => {
    // machining operations
  }
);
```

Its meaning is:

```text
SpindleOn
body
SpindleOff
```

Likewise:

```ts
withCoolant("flood", body)
withTool(T1, body)
```

This is essentially structured resource management.

It eliminates malformed sequences by construction.

A generated program can still flatten to:

```text
T1 M6
S10000 M3
...
M5
```

but the API never asks users to manually balance starts and stops.

---

# 23. Strategies should be plugins

Your Dropcut algorithms make a good test case for this abstraction:

```ts
interface ToolpathStrategy<
  Input,
  Params
> {
  plan(
    ctx: PlanningContext,
    input: Input,
    params: Params
  ): Promise<ToolpathSet>;
}
```

Then:

```ts
RasterFinish
HybridWaterlineFinish
ConstantScallopFinish
ZLevelRough
```

become independent strategy implementations.

For example:

```ts
const constantScallop =
  defineStrategy({
    name: "constant-scallop",

    async plan(ctx, surface, p) {
      const field =
        await ctx.cutterLocationField(...);

      const eikonal =
        solveEikonal(...);

      return contoursToToolpaths(...);
    },
  });
```

This makes experimentation with CAM mathematics substantially easier.

---

# 24. Geometry should also be kernel-independent

Avoid exposing Three.js geometry as the canonical geometry model.

Three.js should be a renderer.

Use interfaces such as:

```ts
interface Surface {
  bounds(): Box3;
  evaluate(u: number, v: number): Point3;
}

interface Mesh extends Solid {
  triangles(): Iterable<Triangle>;
}

interface Solid {
  bounds(): Box3;
}
```

A future implementation could then use:

```text
triangle meshes
OpenCascade
Manifold
CGAL/WASM
signed-distance fields
NURBS
```

without changing the CAM API.

Your current STL triangles become one implementation of `Mesh`.

---

# 25. A nice API for 2.5D milling

You can make simple milling extremely concise.

For example:

```ts
const plate =
  sketch()
    .rect(mm(80), mm(50))
    .extrude(mm(8));

const pocket =
  sketch()
    .roundedRect(
      mm(40),
      mm(20),
      mm(3)
    )
    .pocket({
      depth: mm(4),
    });

const holes =
  pattern.grid({
    rows: 2,
    columns: 4,
    spacingX: mm(15),
  }).holes({
    diameter: mm(4),
    depth: through(),
  });
```

Then:

```ts
job
  .millPocket(pocket, {
    tool: T1,
    strategy: "offset",
  })

  .drill(holes, {
    tool: drill4mm,
  });
```

That is far more useful to a JS programmer than constructing lines of G-code.

---

# 26. And still allow escape to exact machine motions

Some users need complete control.

So the DSL should have an escape layer:

```ts
job.canonical(({ move, spindle }) => {
  spindle.cw(rpm(12_000));

  move.traverseTo(
    p(mm(0), mm(0), mm(5))
  );

  move.feedTo(
    p(mm(0), mm(0), mm(-1)),
    mmPerMin(300)
  );
});
```

But even this is semantic—not raw G-code.

Raw G-code should be an explicitly unsafe backend-specific escape hatch:

```ts
linuxcnc.raw("M64 P0");
```

possibly tagged:

```ts
effects: ["digital-output"]
```

so the rest of the compiler knows that it cannot fully analyze it.

---

# 27. Machine capabilities should be algebraic data

Don't write:

```ts
if (machine === "Makera")
```

throughout the compiler.

Define capabilities.

For example:

```ts
interface MachineCapabilities {
  axes: AxisSet;

  interpolation: {
    linear: true;
    arcXY: boolean;
    arcXZ: boolean;
    arcYZ: boolean;
    helix: boolean;
  };

  spindle: {
    directions: readonly (
      "cw" | "ccw"
    )[];

    range: Range<RPM>;
  };

  probe:
    | { kind: "g38" }
    | { kind: "g31" }
    | null;

  rapid:
    | "coordinated"
    | "axis-independent";

  toolChange:
    | "manual"
    | "automatic";

  coordinateSystems:
    readonly FixtureId[];
}
```

Then lowering is capability-driven.

---

# 28. This handles G-code dialects cleanly

The canonical IR might say:

```ts
probe({
  direction: vec3(0, 0, -1),
  maxTravel: mm(30),
  feed: mmPerMin(100),
  failure: "abort",
});
```

LinuxCNC could emit:

```text
G38.2 Z-30 F100
```

A Fanuc-style backend might emit:

```text
G31 Z-30 F100
```

plus whatever result-validation sequence its dialect requires.

The semantics are identical.

The encoding differs.

---

# 29. The postprocessor itself should have two stages

I would not even have the postprocessor directly produce strings.

First:

```ts
CanonicalIR
    ↓
GCodeIR
```

where:

```ts
interface GCodeBlock {
  motion?: MotionWord;
  axes?: Partial<Axes>;
  feed?: FeedRate;
  spindle?: RPM;
  misc?: MCode[];
  comment?: string;
}
```

Then:

```ts
GCodeIR
   ↓ modal optimizer
OptimizedGCodeIR
   ↓ formatter
string
```

This means you can unit-test:

```text
machine semantics → block semantics
```

separately from formatting.

---

# 30. The compiler pipeline I would implement

A complete version could look like:

```text
ManufacturingPlan
      ↓
feature expansion
      ↓
strategy planning
      ↓
ToolpathProgram
      ↓
linking
      ↓
entry/exit generation
      ↓
clearance planning
      ↓
curve refinement
      ↓
arc/spline fitting
      ↓
CanonicalProgram
      ↓
machine capability lowering
      ↓
kinematic transformation
      ↓
static machine validation
      ↓
material/collision verification
      ↓
ValidatedProgram
      ↓
dialect lowering
      ↓
GCodeIR
      ↓
modal compression
      ↓
G-code
```

Your current `generateJob()` contains approximately the middle six stages simultaneously. fileciteturn0file0

Separating them is probably the single largest architectural improvement available.

---

# 31. This also makes optimization principled

Once toolpaths have semantics, we can define optimization as:

\[
\min_P
\quad
C(P)
\]

subject to:

\[
\llbracket P\rrbracket
\models
Specification
\]

and:

\[
Safe(P).
\]

The cost could be:

\[
C(P)
=
\alpha\,time(P)
+
\beta\,toolwear(P)
+
\gamma\,retracts(P)
+
\delta\,jerk(P).
\]

Then nearest-neighbor contour ordering, feed optimization, stay-down links, retract minimization, entry selection, etc. become genuine optimization passes under safety constraints.

That is a much more general interpretation of what your roughing code is already doing heuristically.

---

# 32. Where the current Dropcut code maps

I'd refactor it approximately like this:

| Existing code | New subsystem |
|---|---|
| `parseSTL` / `buildModel` | `geometry/mesh` |
| `buildGrid` | `geometry/spatial-index` |
| `makeEvaluator` | `cam/drop-cutter/kernel` |
| `buildCLField` | `cam/fields/cutter-location` |
| `marchSquares` | `geometry/contours` |
| `solveEikonal` | `cam/strategies/constant-scallop` |
| `emitEntry` | `cam/planning/entry` |
| roughing part of `generateJob` | `cam/strategies/rough-raster` |
| raster finish | `cam/strategies/raster` |
| hybrid finish | `cam/strategies/hybrid` |
| scallop finish | `cam/strategies/constant-scallop` |
| path linking logic | `cam/planning/linker` |
| `compressCut` | `compiler/arc-fit` |
| `verifyJob` | `analysis/dexel` |
| `toGcode` | `posts/rs274` |
| Three.js code | `viewer/three` |

The existing prototype is thus quite reusable; the problem is much more its **semantic boundaries** than the underlying algorithms. fileciteturn0file0

---

# 33. Package structure

I would probably start with:

```text
@cam/units
@cam/math
@cam/geometry
@cam/machine
@cam/ir
@cam/planner
@cam/strategies
@cam/analysis
@cam/compiler
@cam/post-rs274
@cam/post-linuxcnc
@cam/post-makera
@cam/viewer-three
```

The dependency direction matters:

```text
geometry ← planner ← strategies
    ↑         ↓
    └────── ir
             ↓
          analysis
             ↓
          compiler
             ↓
            post
```

The renderer should depend on the IR.

The IR should **never** depend on Three.js or the renderer.

---

# 34. The most important distinction

I would name three types very explicitly:

```ts
ManufacturingPlan
ToolpathProgram
MachineProgram
```

because they answer three different questions:

```text
ManufacturingPlan:
    What machining do I want?

ToolpathProgram:
    How should the tool move relative
    to the workpiece?

MachineProgram:
    How can this particular machine
    realize those motions?
```

And G-code answers a fourth:

```text
How do I encode that MachineProgram
in this controller's language?
```

That separation is the foundation.

---

# 35. Where category theory really pays off

There are four category-theoretic ideas I'd retain in the design:

| Mathematical structure | CNC meaning |
|---|---|
| **Category of paths** | composable trajectories with matching endpoints |
| **Groupoid of frames** | coordinate transformations and inverses |
| **Kleisli composition** | stateful/failing machine operations |
| **Semantics-preserving morphisms** | compiler transformations/lowerings |

I would resist making the rest of the API "categorical" merely for elegance.

For instance, there is little benefit in exposing users to:

```ts
Kleisli<MachineState, ...>
```

instead of:

```ts
program.cut(...)
```

Category theory should determine the laws of the implementation, not make the API harder to read.

---

# 36. A very desirable end state

Eventually this:

```ts
const job =
  cam(setup)

    .rough(part, {
      tool: T1,
      stock: mm(0.2),

      strategy:
        rasterRough({
          stepdown: mm(1.5),
          stepover: 0.45,
        }),
    })

    .finish(part, {
      tool: T1,

      strategy:
        constantScallop({
          scallop: mm(0.01),
        }),
    });

const compiled =
  await job.compile(machine);

const checked =
  await compiled.verify({
    fixtures,
    tolerance: mm(0.02),
  });

const nc =
  linuxcnc.emit(
    checked.requireSafe()
  );
```

could simultaneously produce:

```text
job.plan
job.geometry
job.toolpaths
job.materialRemoval
job.timeEstimate
job.machineTrace
job.safetyCertificate
job.gcode
```

because they're all different interpretations of the **same semantic program**.

That is the deeper payoff of the denotational approach.

You stop treating "the program" as G-code text.

The program becomes an abstract machining object, and G-code, simulation, visualization, time estimation, verification, documentation, and optimization are all **interpreters of that object**.

That is the architecture I would build the library around.


---

> explain kleisli category

A **Kleisli category** is what you get when ordinary function composition is no longer enough because computations have an *effect*—failure, state, nondeterminism, logging, async work, etc.

For the CAM system, it is useful because a machining command is not really:

\[
\text{MachineState} \to \text{MachineState}
\]

It can also fail, produce measurements, emit a trace, update stock, and so on.

## 1. Start with ordinary functions

Suppose we have:

\[
f:A\to B
\]

and

\[
g:B\to C.
\]

We compose them normally:

\[
g\circ f:A\to C.
\]

In JavaScript:

```js
const f = a => makeB(a);
const g = b => makeC(b);

const h = a => g(f(a));
```

The important thing is that the output type of `f` exactly matches the input type of `g`.

---

## 2. Effects break ordinary composition

Suppose `f` can fail.

Instead of:

\[
f:A\to B
\]

we now have:

\[
f:A\to Result<B>.
\]

For example:

```js
function selectTool(id) {
  if (!toolExists(id))
    return { ok: false, error: "unknown tool" };

  return {
    ok: true,
    value: getTool(id)
  };
}
```

And suppose:

```js
function checkRPM(tool) {
  return {
    ok: true,
    value: recommendedRPM(tool)
  };
}
```

has type roughly:

\[
Tool\to Result<RPM>.
\]

You can't just write mathematical composition:

\[
checkRPM\circ selectTool
\]

because `selectTool` produces:

\[
Result<Tool>
\]

while `checkRPM` expects:

\[
Tool.
\]

There is an extra wrapper.

---

# 3. Kleisli composition solves exactly this

A monad \(M\) gives us computations shaped like:

\[
A\to M(B).
\]

A **Kleisli arrow**

\[
A \rightsquigarrow B
\]

is simply an ordinary function:

\[
A\to M(B).
\]

The funny arrow is useful notation:

\[
A \rightsquigarrow B
\quad := \quad
A\to M(B).
\]

So for `Result`:

\[
ToolId\rightsquigarrow Tool
\]

actually means:

\[
ToolId\to Result<Tool>.
\]

And:

\[
Tool\rightsquigarrow RPM
\]

means:

\[
Tool\to Result<RPM>.
\]

The Kleisli category tells us how to compose these anyway.

---

# 4. `bind` is the crucial operation

Suppose:

\[
f:A\to M(B)
\]

and:

\[
g:B\to M(C).
\]

The monad supplies an operation usually called `bind`:

\[
M(B)\times(B\to M(C))
\to M(C).
\]

For `Result`, `bind` means approximately:

```js
function bind(result, next) {
  if (!result.ok)
    return result;

  return next(result.value);
}
```

So Kleisli composition is:

```js
const composeK = (f, g) =>
  a => bind(f(a), g);
```

Mathematically:

\[
g \star f
=
a\mapsto
f(a)\bind g.
\]

Now:

\[
A\rightsquigarrow B
\]

and:

\[
B\rightsquigarrow C
\]

compose into:

\[
A\rightsquigarrow C.
\]

That's the central idea.

---

# 5. Why call it a *category*?

Because these effectful computations still satisfy the category laws.

We have objects:

\[
A,B,C,\ldots
\]

and morphisms:

\[
A\to M(B).
\]

There is an identity Kleisli arrow:

\[
\eta_A:A\to M(A)
\]

where \(\eta\), often called `pure` or `return`, simply puts a value into the effect:

```js
const pure = x => ({
  ok: true,
  value: x
});
```

And composition is Kleisli composition.

The monad laws guarantee:

### Left identity

\[
f\star \eta=f
\]

### Right identity

\[
\eta\star f=f
\]

### Associativity

\[
h\star(g\star f)
=
(h\star g)\star f.
\]

So effectful programs can be composed with the same algebraic predictability as ordinary functions.

---

# 6. A CNC example: commands that can fail

Imagine:

```ts
type MachineState = {
  tool: Tool | null;
  spindle: "off" | "cw";
  rpm: number;
  position: Point3;
};
```

A command could have the type:

```ts
type Command<A> =
  (state: MachineState) =>
    Result<[A, MachineState]>;
```

For example:

```js
const startSpindle = rpm => state => {
  if (!state.tool) {
    return {
      ok: false,
      error: "Cannot start spindle without a tool"
    };
  }

  if (rpm > 24000) {
    return {
      ok: false,
      error: "RPM exceeds machine limit"
    };
  }

  return {
    ok: true,
    value: [
      undefined,
      {
        ...state,
        spindle: "cw",
        rpm
      }
    ]
  };
};
```

And:

```js
const cutTo = point => state => {
  if (state.spindle !== "cw") {
    return {
      ok: false,
      error: "Cannot cut with spindle stopped"
    };
  }

  return {
    ok: true,
    value: [
      undefined,
      {
        ...state,
        position: point
      }
    ]
  };
};
```

These aren't ordinary state-transforming functions.

They are:

\[
State
\to
Result(A\times State).
\]

This combines two effects:

1. **State**
2. **Failure**

---

# 7. Why Kleisli composition is convenient here

We want to write:

```js
toolChange(T1)
startSpindle(10000)
cutTo(p1)
cutTo(p2)
stopSpindle()
```

But each operation potentially changes state or fails.

Kleisli composition lets us define sequencing once:

```js
const seq = (a, b) => state => {
  const r1 = a(state);

  if (!r1.ok)
    return r1;

  const [, state2] = r1.value;

  return b(state2);
};
```

Then:

```js
const program =
  seq(
    toolChange(T1),
    seq(
      startSpindle(10000),
      seq(
        cutTo(p1),
        cutTo(p2)
      )
    )
  );
```

Conceptually:

\[
ToolChange
\star
StartSpindle
\star
CutTo(p_1)
\star
CutTo(p_2).
\]

You don't manually write:

```text
if toolChange succeeded...
    take its state...
    if startSpindle succeeded...
        take its state...
        if cut succeeded...
```

The composition operator handles that plumbing.

---

# 8. The State monad by itself

Ignore failure for a moment.

A stateful computation returning a value \(A\) has the shape:

\[
State\to(A\times State).
\]

Call that:

\[
StateM(A).
\]

So:

\[
StateM(A)
=
State\to(A\times State).
\]

Then a Kleisli arrow:

\[
X\rightsquigarrow Y
\]

is:

\[
X\to StateM(Y).
\]

Expanding it:

\[
X
\to
\big(
State\to(Y\times State)
\big).
\]

That's why monads can initially look unnecessarily abstract: the notation hides a fairly ugly function type.

---

# 9. `getPosition` shows why there is a return value

A machine operation doesn't always just return `void`.

For example:

```js
const getPosition = state => [
  state.position,
  state
];
```

Its semantic type is:

\[
State\to(Point\times State).
\]

A probe might be even more interesting:

```js
const probeZ = target => state => {
  // machine runs probe...

  return [
    measuredContactPosition,
    newState
  ];
};
```

Now the measured position can feed the next computation:

```js
probeZ(...)
  >>= measuredZ =>
setWorkOffset(measuredZ)
```

This is one place where Kleisli composition becomes much more than fancy sequencing.

**The output of one effectful operation determines the next effectful operation.**

---

# 10. This is what `flatMap` is

If you've used:

```js
Promise.then(...)
```

or:

```js
array.flatMap(...)
```

or Rust:

```rust
Result::and_then
```

or Haskell:

```haskell
>>=
```

you've encountered essentially this idea.

For a `Promise`:

```js
fetchModel()
  .then(parseModel)
  .then(generateToolpath)
  .then(verifyToolpath);
```

Each function may return another promise.

`then` knows how to avoid producing:

```text
Promise<
  Promise<
    Promise<...>
  >
>
```

That flatten-and-sequence operation is monadic bind.

Therefore:

```js
Promise<A>
```

also gives rise to a Kleisli category where arrows look like:

\[
A\to Promise<B>.
\]

---

# 11. Why a monad is needed

You might wonder:

> Why don't we just define some custom composition function?

You can.

A monad is basically the statement that this custom notion of sequencing has a sufficiently regular algebra.

At minimum, think of a monad as supplying:

```ts
pure:
  A -> M<A>

flatMap:
  M<A> ->
  (A -> M<B>) ->
  M<B>
```

From those, we derive Kleisli composition:

```ts
composeK:
  (A -> M<B>) ->
  (B -> M<C>) ->
  (A -> M<C>)
```

So:

```text
Monad
   ↓
defines legal sequencing
   ↓
Kleisli category
```

---

# 12. Another CNC effect: logging

Suppose every operation should produce a physical trace.

Instead of:

\[
State\to Result(A\times State)
\]

we might have:

\[
State
\to
Result(
A\times State\times Trace
).
\]

A move could produce:

```js
{
  state: newState,

  trace: [
    {
      kind: "tool-motion",
      from,
      to,
      mode: "cut"
    }
  ]
}
```

Sequential composition combines traces:

\[
Trace_1 \mathbin{+\!\!+} Trace_2.
\]

This is analogous to the **Writer monad**.

Now the interpreter can simultaneously compute:

```text
final machine state
+
failure/success
+
physical motion trace
```

without individual commands having to know how an entire program is assembled.

---

# 13. Stock removal fits naturally too

For CAM, our state can be richer:

\[
\Sigma =
(
pose,
tool,
spindle,
fixture,
stock
).
\]

Then a `cut` morphism changes:

\[
stock
\]

according to:

\[
S'
=
S\setminus Sweep(T,\gamma).
\]

So operationally:

```text
Cut(path)
```

acts like:

\[
\Sigma\to Result(\Sigma\times Trace).
\]

And semantically it might:

1. verify a tool exists;
2. verify spindle state;
3. verify feed;
4. verify axis limits;
5. calculate the tool sweep;
6. remove that sweep from stock;
7. update machine position;
8. emit a trace.

That whole operation can still be composed with another command using exactly the same Kleisli operator.

---

# 14. Compare ordinary versus Kleisli composition

Ordinary category:

```text
A --f--> B --g--> C
```

Functions:

\[
f:A\to B
\]

\[
g:B\to C
\]

Composition:

\[
A\xrightarrow{g\circ f}C.
\]

Kleisli category for \(M\):

```text
A --f--> M<B>
            |
            | bind g
            v
           M<C>
```

where:

\[
f:A\to M(B)
\]

\[
g:B\to M(C).
\]

But in the **Kleisli category**, we draw these simply as:

```text
A --f--> B --g--> C
```

because the \(M\) is understood.

That's the trick.

We invent a new category in which **effectful computations look like ordinary arrows again**.

---

# 15. Why this is relevant to our CAM API

This gives a precise mathematical meaning to code such as:

```js
program
  .toolChange(T1)
  .spindleCW(rpm(10000))
  .traverseTo(p0)
  .cut(path1)
  .cut(path2)
  .stopSpindle();
```

Surface syntax makes it look like method chaining.

But semantically it can mean composition of arrows:

\[
\Sigma
\rightsquigarrow
\Sigma
\rightsquigarrow
\Sigma
\rightsquigarrow
\cdots
\]

where the hidden effect contains:

```text
machine state
failure
trace
possibly warnings
possibly measurements
```

So the program gets a very useful law:

\[
(P;Q);R=P;(Q;R).
\]

That means we can safely regroup programs:

```js
const rough = seq(...roughingOps);
const finish = seq(...finishOps);

const job =
  seq(setup, rough, finish, shutdown);
```

without changing their semantics.

That associativity is what makes large programs hierarchically composable.

---

# 16. One subtle but important point

The **Kleisli category is not the monad**.

The monad \(M\) gives you machinery like:

\[
\eta
\]

and:

\[
\bind.
\]

From that monad, you construct a category:

\[
Kl(M)
\]

called its **Kleisli category**.

Its:

- objects are the same underlying types \(A,B,C,\ldots\);
- arrows \(A\to B\) are functions \(A\to M(B)\);
- identities use `pure`;
- composition uses `bind`.

So:

\[
Monad
\quad\Longrightarrow\quad
Kleisli\ Category.
\]

---

# 17. The shortest possible intuition

If ordinary function composition says:

> **Take the result of computation A and give it to B.**

Kleisli composition says:

> **Run computation A, correctly handle its computational context/effects, then give its successful value to B.**

For the CNC library, that's roughly:

> **Execute one semantic machine operation, propagate its machine state, measurements, trace and possible failure, then execute the next.**

That is why I brought up Kleisli composition in the CAM architecture: it gives us a mathematically clean model for sequencing **stateful, fallible, physically meaningful machine actions** while preserving ordinary-looking composition laws.


---

> explain the budget pattern which i've seen you use many times (for example for building a RAG pipeline). Where does it come from, what are the theoretical computer-science and mathematical underpinnings.

The “budget pattern” I keep using is not one named design pattern with a single inventor. It is a recurring abstraction that appears whenever a computation consumes, accumulates, or is allowed only a bounded amount of some quantity.

In its simplest form:

\[
\text{computation} : (x,B) \mapsto (y,B')
\]

with an invariant such as

\[
B' \le B
\]

for a remaining-resource budget, or equivalently

\[
\operatorname{cost}(P)\le B.
\]

That simple idea connects to several fairly deep areas of mathematics and theoretical computer science.

## 1. The elementary version: resource accounting

Suppose a RAG pipeline has:

\[
B_{\text{tokens}}=20\,000.
\]

Retrieval spends 8,000 tokens, reranking spends 2,000, and generation gets what remains:

\[
20\,000-8\,000-2\,000=10\,000.
\]

You can model a stage as:

\[
f:A\times B\to C\times B.
\]

For example:

\[
Retrieve :
Query\times TokenBudget
\to
Documents\times TokenBudget.
\]

Then:

\[
Rerank :
Documents\times TokenBudget
\to
Documents'\times TokenBudget.
\]

The important property is compositionality.

If

\[
cost(f)=a
\]

and

\[
cost(g)=b,
\]

then sequential execution has:

\[
cost(g\circ f)=a+b.
\]

That tiny equation is the seed from which much of the theory grows.

---

# 2. Why I like the abstraction

Without budgets, systems often encode requirements informally:

> Don't retrieve too much.  
> Don't make the prompt huge.  
> Don't accumulate too much approximation error.  
> Don't retry forever.  
> Keep latency reasonable.

A budget turns that into an algebraic object.

Instead of:

```js
retrieve(query)
```

you get conceptually:

```js
retrieve(query, {
  tokens: 8000,
  latency: ms(500),
  candidates: 100
})
```

And the result can say:

```js
{
  documents,
  spent: {
    tokens: 7312,
    latency: ms(183),
    candidates: 72
  }
}
```

Now allocation, composition and verification become possible.

---

# 3. There are really two dual forms

I often move between these two presentations.

### Remaining budget

Start with \(B\) and consume it:

\[
B' = B-c.
\]

Require:

\[
c\le B.
\]

### Accumulated cost

Start with zero and accumulate:

\[
C'=C+c.
\]

Require at the end:

\[
C\le B.
\]

They are dual views of the same thing.

For program composition, accumulated cost is often mathematically cleaner:

\[
cost(P;Q)
=
cost(P)+cost(Q).
\]

For an API, remaining resources can be more intuitive.

---

# 4. The algebra underneath: monoids

This is perhaps the most fundamental mathematical connection.

A **monoid** consists of:

- a set \(M\);
- an associative operation \(\otimes\);
- an identity element \(e\).

For ordinary additive budgets:

\[
M=\mathbb R_{\ge0},
\]

\[
a\otimes b=a+b,
\]

\[
e=0.
\]

So costs compose:

\[
cost(P;Q)
=
cost(P)\otimes cost(Q).
\]

Associativity:

\[
(a+b)+c
=
a+(b+c)
\]

means that regrouping a pipeline doesn't alter its total cost.

That is exactly the same associativity we just discussed for categories and Kleisli composition.

This becomes especially useful when the budget is multidimensional.

---

# 5. Product budgets

A realistic RAG budget isn't one number.

It might be:

\[
B=
(
tokens,
latency,
money,
retrievals
).
\]

For example:

\[
B=(20000,2s,\$0.05,5).
\]

Composition is componentwise:

\[
(a_1,a_2,a_3,a_4)
+
(b_1,b_2,b_3,b_4)
=
(a_1+b_1,\ldots,a_4+b_4).
\]

So the resource algebra is the product monoid:

\[
\mathbb R_{\ge0}^4.
\]

That sounds abstract, but it gives a very practical design rule:

> Make stages report their resource usage using a common compositional algebra.

Then the orchestrator doesn't need to understand each implementation internally.

---

# 6. Some budgets don't use addition

This is where the pattern gets more interesting.

Suppose each approximation pass has a worst-case geometric deviation.

Pass A guarantees:

\[
\epsilon_A=0.01\text{ mm}.
\]

Pass B guarantees:

\[
\epsilon_B=0.02\text{ mm}.
\]

A conservative bound may be:

\[
\epsilon_{\text{total}}
\le
\epsilon_A+\epsilon_B.
\]

So addition works.

But other quantities compose differently.

For example, if we're tracking maximum memory usage for sequential phases, we might use:

\[
M(P;Q)
=
\max(M(P),M(Q))
\]

rather than addition.

Now our monoid is:

\[
(\mathbb R_{\ge0},\max,0).
\]

For probabilities, independent success probabilities might multiply:

\[
p_{\text{combined}}
=
p_1p_2.
\]

For reliability risks, we may use other operations again.

So the general pattern is not really “subtract numbers from a budget.”

It's:

> Attach a quantity from some algebra to computations and define how those quantities compose.

---

# 7. This connects directly to cost semantics

Programming-language theory has a long tradition of giving programs semantics beyond simply:

\[
\llbracket P\rrbracket = \text{value}.
\]

We can instead define:

\[
\llbracket P\rrbracket
=
(value,cost).
\]

A simple operational semantics might have transitions:

\[
\langle e,\sigma\rangle
\xrightarrow{c}
\langle e',\sigma'\rangle.
\]

The label \(c\) records resource use.

For example:

\[
\langle Retrieve(q),\sigma\rangle
\xrightarrow{3721\ tokens}
\langle docs,\sigma'\rangle.
\]

Along a trace,

\[
e_0
\xrightarrow{c_1}
e_1
\xrightarrow{c_2}
\cdots
\xrightarrow{c_n}
e_n,
\]

the total cost is:

\[
C
=
c_1\otimes c_2\otimes\cdots\otimes c_n.
\]

This is commonly called some variety of **cost semantics**, **resource semantics**, or **instrumented semantics**.

---

# 8. Complexity theory is one ancestor

Classical complexity theory is essentially a particular use of resource accounting.

We ask:

\[
T(n)
\]

for time and

\[
S(n)
\]

for space.

A program is acceptable if:

\[
T(n)\in O(n\log n)
\]

or:

\[
S(n)\le B.
\]

The budget pattern differs mostly in scale and purpose.

Complexity theory says:

> How does required resource grow asymptotically?

A runtime budget says:

> For this particular invocation, you may spend at most this much.

But conceptually they are close relatives.

---

# 9. Amortized analysis is an especially close relative

This is one of the deepest connections.

Suppose an individual operation sometimes costs a lot, but across many operations the average is bounded.

For dynamic arrays, most appends cost \(O(1)\), occasionally an append causes resizing and costs \(O(n)\).

Amortized analysis assigns **credits** or **potential** so that cheap operations save enough budget to pay for expensive future operations.

The potential method defines:

\[
\hat c_i
=
c_i
+
\Phi(D_i)
-
\Phi(D_{i-1}).
\]

Where:

- \(c_i\) is actual cost;
- \(\Phi\) is stored potential;
- \(\hat c_i\) is amortized cost.

Then:

\[
\sum_i c_i
\le
\sum_i \hat c_i
+
\Phi(D_0).
\]

This is extremely close to a computational budget.

You can think of potential as **stored future budget**.

That idea is useful in agentic/RAG systems too.

For example, you might allocate:

```text
cheap retrieval first
reserve expensive reranking
reserve fallback web search
reserve final generation context
```

Rather than spending the whole budget greedily at the beginning.

---

# 10. Linear logic gives a more structural interpretation

Ordinary classical logic permits assumptions to be reused freely:

\[
A\vdash A\land A
\]

in effect allowing duplication.

Linear logic, introduced by Jean-Yves Girard, treats assumptions as resources.

Having:

\[
A
\]

means you possess one instance of \(A\), and using it consumes it unless duplication is explicitly allowed.

The slogan is:

> propositions as resources.

That maps very naturally onto budgets.

If you have:

\[
10\,000\ Tokens
\]

you cannot implicitly duplicate that assumption into:

\[
10\,000\ Tokens
\otimes
10\,000\ Tokens.
\]

You must split it:

\[
10\,000
=
6\,000+4\,000.
\]

This is the conceptual basis for many resource-aware type systems.

---

# 11. Linear types and affine types

Linear type systems take the resource interpretation into programming languages.

A linear value must be used exactly once.

An affine value may be used at most once.

For example, conceptually:

```ts
Budget<10000>
```

could be consumed by an operation and replaced with:

```ts
Budget<6200>
```

You should not have both values alive simultaneously:

```text
Budget<10000>
Budget<6200>
```

because that would amount to creating budget from nowhere.

Rust's ownership discipline has some family resemblance to this, although Rust is not simply “a linear logic language.”

---

# 12. Quantitative type theory pushes this further

Instead of merely recording:

> this value may be used once,

quantitative type systems can annotate **how many times** something may be used.

Conceptually:

\[
x :_{3} A
\]

might mean:

> `x` may be consumed three times.

Or a typing judgment may carry resource information:

\[
\Gamma
\vdash^{r}
e:A
\]

meaning:

> expression \(e\) has type \(A\) and requires resource \(r\).

Then application might combine costs:

\[
\frac
{\Gamma\vdash^{r}f:A\to B
\qquad
\Delta\vdash^{s}x:A}
{\Gamma+\Delta
\vdash^{r+s}
f(x):B}.
\]

That is basically a static budget system.

---

# 13. Dependent types let the budget appear in types

With dependent types you can go even further:

\[
Program(B)
\]

could mean:

> a program statically known to require at most budget \(B\).

Then a combinator could have a type like:

\[
compose:
Program(a)
\to
Program(b)
\to
Program(a+b).
\]

Or, for CAM:

\[
ArcFit(\epsilon_1)
\to
Linearize(\epsilon_2)
\to
Program(\epsilon_1+\epsilon_2).
\]

This is what I was implicitly gesturing toward when I suggested an error budget for the CAM compiler.

A sufficiently expressive type system could make the accumulated tolerance part of the type itself.

---

# 14. Graded monads are almost exactly “monads with budgets”

This connects directly to the Kleisli discussion.

An ordinary monad says:

\[
M(A)
\]

meaning:

> a computation producing \(A\) with some effect.

A **graded monad** refines this to:

\[
M_r(A)
\]

where \(r\) describes the effect.

For example:

\[
M_{1000}(Document[])
\]

might mean:

> a computation producing documents and consuming at most 1000 tokens of budget.

Composition follows the grade algebra:

\[
M_r(A)
\quad\text{and}\quad
A\to M_s(B)
\]

produce:

\[
M_{r\otimes s}(B).
\]

With additive resource use:

\[
M_r(A)
\bind
(A\to M_s(B))
:
M_{r+s}(B).
\]

That is precisely a mathematical version of budget propagation through a pipeline.

So a RAG pipeline could conceptually have:

\[
Retrieve:
Query\to M_{5000}(Docs)
\]

\[
Rerank:
Docs\to M_{2000}(Docs)
\]

\[
Generate:
Docs\to M_{8000}(Answer).
\]

Therefore:

\[
Generate
\star
Rerank
\star
Retrieve
:
Query
\to
M_{15000}(Answer).
\]

That is a very clean formalization.

---

# 15. Indexed monads and effect systems are nearby ideas

There are several related constructions:

- graded monads;
- indexed monads;
- parameterized monads;
- effect systems;
- effect quantales;
- coeffects.

They differ in exactly what information the index records.

For instance, an indexed state computation might track:

\[
M_{S_0,S_1}(A)
\]

meaning:

> a computation starting in state type \(S_0\), ending in state type \(S_1\), and returning \(A\).

That could express CNC facts such as:

```text
before: spindle off
after:  spindle on
```

in the type.

A graded effect might separately record:

```text
travel distance ≤ 200 mm
error ≤ 0.02 mm
runtime ≤ 5 min
```

So typestate and resource budgets can coexist.

---

# 16. Ordered structures matter because a budget is a bound

A budget isn't only an algebra. It usually comes with an ordering:

\[
a\le b.
\]

For example:

\[
7312\le 8000.
\]

So a useful budget structure is often an **ordered monoid**:

\[
(M,\otimes,e,\le).
\]

We want composition to respect ordering:

\[
a\le b
\implies
a\otimes c
\le
b\otimes c.
\]

Then we can reason:

\[
cost(P)\le B_P,
\]

\[
cost(Q)\le B_Q
\]

implies:

\[
cost(P;Q)
\le
B_P\otimes B_Q.
\]

This monotonicity is one reason the abstraction composes so well.

---

# 17. Semirings appear when there is branching

Suppose:

```js
if (condition) {
  A();
} else {
  B();
}
```

Sequential composition normally adds costs:

\[
cost(A;B)=cost(A)+cost(B).
\]

But branching is different.

For a worst-case analysis:

\[
cost(A\text{ or }B)
=
\max(cost(A),cost(B)).
\]

Now we have two operations:

\[
\otimes = +
\]

for sequence, and:

\[
\oplus = \max
\]

for alternatives.

This forms a structure closely related to the **tropical semiring**:

\[
(\mathbb R_{\ge0}\cup\{-\infty\},
\max,+).
\]

This is not merely mathematical decoration.

It tells us how to calculate static worst-case costs of structured programs.

For example:

```text
retrieve
then
    either cheap reranking
    or expensive reranking
then
generate
```

has cost:

\[
R
+
\max(Cheap,Expensive)
+
G.
\]

---

# 18. Shortest paths and dynamic programming use the same algebra

The tropical/min-plus semiring is fundamental to shortest-path algorithms.

For path lengths:

- sequencing edges adds costs;
- choosing among paths takes the minimum.

So:

\[
\otimes=+
\]

and:

\[
\oplus=\min.
\]

This is exactly a budget problem:

> Find a composition of operations whose accumulated cost is minimal.

Many compiler optimizations, routing problems, query planners and RAG retrieval strategies can therefore be viewed as constrained path problems.

A RAG planner might search through actions such as:

```text
vector search
keyword search
rerank
query expansion
web search
summarize
```

with costs attached to each edge.

Then find:

\[
\arg\max_P Utility(P)
\]

subject to:

\[
Cost(P)\le B.
\]

---

# 19. This connects to constrained optimization

This is perhaps the broadest mathematical interpretation.

We frequently want:

\[
\max_x U(x)
\]

subject to:

\[
C(x)\le B.
\]

For RAG:

\[
\max
\quad
AnswerQuality
\]

subject to:

\[
Tokens\le 20000,
\]

\[
Latency\le 2s,
\]

\[
Cost\le \$0.05.
\]

This is classic constrained optimization.

We can introduce Lagrange multipliers:

\[
\mathcal L(x,\lambda)
=
U(x)
-
\lambda(C(x)-B).
\]

Now instead of a rigid constraint, we attach a shadow price to resource usage.

This interpretation is useful when deciding whether another retrieval step is worthwhile:

\[
\frac{\Delta Quality}
{\Delta Tokens}
\]

or:

\[
\frac{\Delta Quality}
{\Delta Latency}.
\]

Stop when marginal benefit no longer justifies marginal cost.

---

# 20. Knapsack is the discrete version

Suppose retrieved chunks have:

\[
(value_i,cost_i).
\]

You want the subset:

\[
S
\]

maximizing:

\[
\sum_{i\in S} value_i
\]

subject to:

\[
\sum_{i\in S} tokens_i
\le B.
\]

That is essentially the **knapsack problem**.

This is one reason “context budgeting” is such a natural framing for RAG.

Selecting prompt context isn't merely ranking.

It's frequently:

> ranking subject to a finite packing constraint.

A high-scoring 5,000-token passage might be worse than five 800-token passages that collectively cover the answer more completely.

---

# 21. Information theory also appears

A token budget makes context a limited-capacity communication channel.

Suppose retrieved evidence \(D\) contains information about answer \(Y\).

Ideally, we want to maximize something related to:

\[
I(D;Y),
\]

mutual information, while respecting:

\[
length(D)\le B.
\]

This leads to interpretations resembling the **information bottleneck**:

\[
\max I(Z;Y)
-
\beta I(Z;X).
\]

Very loosely:

> Compress the available information \(X\) into a limited representation \(Z\), preserving what matters for \(Y\).

That is exactly what good RAG context construction tries to do.

It's why I often talk about an **evidence budget**, not merely a token budget.

You don't want maximal text.

You want maximal decision-relevant evidence per unit of context.

---

# 22. Error budgets come from numerical analysis too

The CAM example is another branch of the same family.

Suppose an answer involves approximations:

\[
x
\xrightarrow{f}
\tilde y
\xrightarrow{g}
\tilde z.
\]

If:

\[
\|f(x)-\tilde f(x)\|
\le\epsilon_f
\]

and:

\[
\|g(y)-\tilde g(y)\|
\le\epsilon_g,
\]

we want a bound on final error.

If \(g\) is Lipschitz with constant \(L_g\):

\[
\|g(a)-g(b)\|
\le
L_g\|a-b\|,
\]

then:

\[
\epsilon_{total}
\le
L_g\epsilon_f+\epsilon_g.
\]

This is an **error budget**.

So error doesn't always simply add.

A later computation can amplify previous error.

That leads directly to condition numbers and numerical stability.

---

# 23. Condition numbers are budget amplification factors

Suppose:

\[
y=f(x).
\]

A perturbation:

\[
x+\delta x
\]

may cause:

\[
f(x+\delta x)-f(x).
\]

The condition number measures how strongly errors get amplified.

So in a CAM compiler:

```text
sampling error
→ curve fitting
→ coordinate transform
→ controller quantization
```

the proper error budget might be:

\[
\epsilon_{out}
\le
L_4(
 L_3(
  L_2\epsilon_1+\epsilon_2
 )+\epsilon_3
)+\epsilon_4.
\]

The simple sum I gave earlier is a conservative special case.

This is standard numerical-analysis reasoning applied as an API architecture.

---

# 24. Formal verification uses similar ideas

In program verification, we often reason with invariants:

\[
ResourceUsed\le B.
\]

Hoare logic could express:

\[
\{budget=b\}
\ P\
\{budget\ge b-c\}.
\]

For example:

\[
\{tokens=10000\}
Retrieve
\{tokens\ge5000\}.
\]

Then sequential composition uses the Hoare sequencing rule:

\[
\frac
{\{P\}C_1\{Q\}
\qquad
\{Q\}C_2\{R\}}
{\{P\}C_1;C_2\{R\}}.
\]

This gives a formal basis for budget-preserving pipelines.

There are entire families of **resource-aware logics** extending this idea.

---

# 25. Separation logic has a relevant analogy

Separation logic is usually associated with memory:

\[
P*Q
\]

means roughly that \(P\) and \(Q\) hold over disjoint pieces of state.

The resource interpretation is more general.

You can think of:

\[
Budget(6000)
*
Budget(4000)
\]

as decomposing:

\[
Budget(10000).
\]

Then one subsystem owns one portion and another subsystem owns the other.

This matters architecturally.

Instead of every RAG component sharing one mutable integer:

```js
budget.remaining
```

you can **allocate sub-budgets**:

```text
retrieval      6000
reranking      2000
answer          9000
reserve         3000
```

Each subsystem is responsible for its own slice.

That reduces coordination and makes invariants local.

---

# 26. Distributed systems made “budget” language especially common

Several practical engineering traditions independently converged on this vocabulary.

For example:

### Timeouts/deadlines

Instead of giving every RPC a 5-second timeout, propagate a remaining deadline:

```text
request budget: 2000 ms

service A uses 300 ms
↓
1700 ms remains

service B uses 700 ms
↓
1000 ms remains
```

Otherwise nested services can accidentally multiply latency.

### Retry budgets

Do not let every layer retry independently without bounds.

Use:

\[
retryCount\le B.
\]

### Error budgets

Site reliability engineering uses an availability objective such as:

\[
99.9\%.
\]

That means permitted unavailability is:

\[
0.1\%.
\]

The permitted failure amount is literally called an **error budget**.

The organization may spend that budget on risky deployments and changes.

The engineering usage and the mathematical resource interpretation reinforce each other.

---

# 27. Control theory has another version

Control systems work repeatedly under constraints:

\[
x_{t+1}
=
f(x_t,u_t)
\]

with:

\[
u_t\in U
\]

and perhaps:

\[
x_t\in X.
\]

Model predictive control solves:

\[
\min_{u_0,\ldots,u_n}
\sum_t cost(x_t,u_t)
\]

subject to resource and state constraints.

A budget-driven agent resembles this:

```text
current state
available actions
remaining budget
expected future utility
```

Choose the action that gives good expected utility while leaving enough resources for later.

This is more sophisticated than greedily spending whatever remains.

---

# 28. Probability gives us “risk budgets”

Suppose several independent operations can fail with probabilities:

\[
p_1,p_2,\ldots.
\]

You might require:

\[
P(failure)\le\epsilon.
\]

Then \(\epsilon\) is a **risk budget**.

For small independent probabilities, the union bound gives:

\[
P\left(\bigcup_i Failure_i\right)
\le
\sum_i p_i.
\]

Therefore you can allocate:

\[
\epsilon
=
\epsilon_1+\epsilon_2+\cdots+\epsilon_n.
\]

Again:

> split a global guarantee into local budgets that compose into the global one.

This same pattern appears extensively in differential privacy.

---

# 29. Differential privacy is a particularly beautiful example

A mechanism can be:

\[
(\epsilon,\delta)\text{-differentially private}.
\]

Running multiple mechanisms consumes privacy budget.

A basic composition theorem gives roughly:

\[
\epsilon_{total}
=
\sum_i\epsilon_i
\]

and:

\[
\delta_{total}
=
\sum_i\delta_i.
\]

So you literally have a mathematical **privacy budget** that computations consume.

More sophisticated composition theorems give tighter bounds.

This is perhaps one of the cleanest examples of the general budget pattern becoming a serious formal guarantee.

---

# 30. Why I use it often for RAG

RAG has an unusually large number of scarce resources:

\[
B=
(
context,
latency,
money,
retrievals,
attention,
evidence,
uncertainty
).
\]

If you don't make these explicit, each component optimizes itself locally:

```text
retriever:
    return more documents!

reranker:
    use more candidates!

summarizer:
    preserve everything!

generator:
    give me more context!
```

The result is globally poor.

Budgeting turns the design problem into:

\[
\max Quality(P)
\]

subject to:

\[
Cost(P)\preceq Budget.
\]

That gives the whole pipeline a shared notion of scarcity.

---

# 31. Evidence budget is slightly different

This is one of the subtler uses.

I sometimes propose something like:

```text
context budget
    16k tokens

evidence slots
    12 claims

source diversity budget
    ≤4 chunks/source

quote budget
    500 tokens

retrieval round budget
    3
```

Not everything here is literally fungible.

The point is to impose explicit constraints that prevent one stage or source from monopolizing the final representation.

Mathematically, this may be a product of heterogeneous ordered structures rather than one scalar.

---

# 32. Budget versus fuel

Programming-language theory sometimes calls the simplest version **fuel**.

An evaluator can be defined:

```ts
evaluate(expr, fuel)
```

Each reduction step consumes one unit:

\[
fuel' = fuel-1.
\]

At zero:

```text
OutOfFuel
```

This is useful for making potentially nonterminating computations total.

For example:

\[
eval:
Expr\times\mathbb N
\to
Result<Value,OutOfFuel>.
\]

Proof assistants often use related techniques when unrestricted recursion would otherwise cause termination problems.

A budget generalizes fuel from:

```text
number of steps
```

to arbitrary resources.

---

# 33. Budget versus quota versus bound

I find it useful to distinguish these.

A **bound** is mathematical:

\[
cost(P)\le B.
\]

A **quota** is a policy:

> this user gets 10,000 requests/day.

A **budget** often combines both:

> allocate a finite resource and make the system decide how to spend it.

The interesting architectural pattern isn't merely imposing a ceiling.

It's making resource allocation explicit and compositional.

---

# 34. Static versus dynamic budgets

There are two distinct approaches.

### Static

Prove before execution:

\[
cost(P)\le B.
\]

For example:

```ts
Program<Tokens<5000>>
```

This connects to types, complexity analysis and verification.

### Dynamic

Track during execution:

```js
if (budget.tokens < required) {
  return OutOfBudget;
}
```

This connects to runtime accounting and scheduling.

Good systems often use both:

```text
static conservative upper bound
+
dynamic actual consumption
```

---

# 35. Hard versus soft budgets

A **hard budget** is an invariant:

\[
C\le B.
\]

Violation means stop.

Examples:

```text
maximum travel
maximum context length
memory limit
safety tolerance
```

A **soft budget** is an optimization target:

\[
C\approx B.
\]

You may exceed it if utility warrants it.

Examples:

```text
preferred latency
preferred token count
preferred monetary cost
```

These lead to different algorithms.

Hard constraints naturally yield:

\[
\max U(x)
\quad
\text{s.t. }C(x)\le B.
\]

Soft ones often become penalty terms:

\[
\max
\left[
U(x)-\lambda C(x)
\right].
\]

---

# 36. Budgets lead naturally to hierarchical composition

Suppose:

\[
B_{job}=100.
\]

We split:

\[
B_{job}
=
B_{rough}
+
B_{finish}
+
B_{verify}.
\]

Then:

\[
B_{finish}
=
B_{sampling}
+
B_{pathgen}
+
B_{arcfit}.
\]

This forms a resource tree:

```text
100
├─ rough         40
├─ finish        40
│  ├─ sampling   15
│  ├─ planning   20
│  └─ fitting     5
└─ verify        20
```

This mirrors program decomposition.

That's important:

> The budget decomposition can have the same structure as the program decomposition.

That makes local reasoning possible.

---

# 37. Category-theoretic formulation

Since we've been talking category theory, here is the compact formulation.

Suppose programs form a category \(\mathcal C\).

Let resource costs live in a monoidal category \((R,\otimes,I)\).

A compositional cost semantics behaves like a monoidal mapping:

\[
Cost(P;Q)
=
Cost(P)\otimes Cost(Q).
\]

So there is a structure-preserving map from program composition to resource composition:

\[
\mathcal C
\longrightarrow
R.
\]

For simple scalar costs:

\[
R=(\mathbb R_{\ge0},+,0).
\]

Conceptually:

```text
program world             resource world

P ; Q        --------->   cost(P) + cost(Q)

identity     --------->   0
```

This is why the pattern feels so universally reusable.

It follows the composition structure of programs themselves.

---

# 38. And the graded-Kleisli formulation

Combine this with our previous conversation.

Instead of:

\[
A\rightsquigarrow B
\]

represent a computation as:

\[
A\rightsquigarrow_r B.
\]

The \(r\) says what resource/effect it consumes.

Then:

\[
A
\rightsquigarrow_r
B
\]

and:

\[
B
\rightsquigarrow_s
C
\]

compose as:

\[
A
\rightsquigarrow_{r\otimes s}
C.
\]

For additive budgets:

\[
A
\rightsquigarrow_r
B
\rightsquigarrow_s
C
\]

becomes:

\[
A
\rightsquigarrow_{r+s}
C.
\]

That's the categorical core of the pattern.

---

# 39. Back to our CAM compiler

Now the suggestion I made earlier should look less arbitrary.

Suppose we have:

```text
cutter-location discretization
     ε₁ = 0.004 mm

polyline approximation
     ε₂ = 0.006 mm

arc fitting
     ε₃ = 0.010 mm

controller quantization
     ε₄ = 0.001 mm
```

A conservative compiler certificate could carry:

\[
\epsilon
\le
\epsilon_1+
\epsilon_2+
\epsilon_3+
\epsilon_4.
\]

Thus:

\[
\epsilon\le0.021\text{ mm}.
\]

Each compiler pass has something like:

```ts
Pass<A, B> = {
  run(a: A): B;

  errorBound:
    ErrorBudget;
}
```

Composition produces:

```ts
compose(a, b).errorBound =
  combine(
    a.errorBound,
    b.errorBound
  );
```

The important word is **combine** rather than `+`.

Different resources need different algebras.

---

# 40. A general abstraction

If I were writing the reusable TypeScript abstraction, I might conceptualize it as:

```ts
interface ResourceAlgebra<R> {
  empty: R;

  combine(
    a: R,
    b: R
  ): R;

  within(
    used: R,
    limit: R
  ): boolean;
}
```

For tokens:

```ts
{
  empty: 0,
  combine: (a, b) => a + b,
  within: (x, max) => x <= max
}
```

For peak memory:

```ts
{
  empty: 0,
  combine: Math.max,
  within: (x, max) => x <= max
}
```

For several resources:

```ts
type Resources = {
  tokens: number;
  dollars: number;
  latency: number;
  retrievals: number;
};
```

with a product algebra.

That's the engineering manifestation of the mathematical idea.

---

# 41. Where it “comes from”

So if you ask for one historical source, there isn't one.

The same pattern has emerged repeatedly:

- **algorithm analysis:** time and space complexity;
- **amortized analysis:** credits and potential;
- **operations research:** constrained resource allocation;
- **linear programming:** finite resource constraints;
- **linear logic:** assumptions as consumable resources;
- **type theory:** linear, affine and quantitative types;
- **program semantics:** cost/resource semantics;
- **formal methods:** resource invariants and Hoare logics;
- **numerical analysis:** error propagation and tolerance allocation;
- **probability:** risk allocation and union bounds;
- **differential privacy:** formal privacy budgets;
- **distributed systems:** deadlines, retry budgets and quotas;
- **SRE:** error budgets;
- **control theory:** finite-horizon constrained optimization;
- **category theory:** graded effects and monoidal resource composition.

They are all manifestations of roughly the same abstraction:

\[
\boxed{
\text{Make scarce quantities explicit,
give them a composition law,
and require global bounds.}
}
\]

The especially important theoretical step is realizing that the “budget” doesn't have to be a number. It can be **any ordered algebra of resources whose composition mirrors the composition of computations**.

Once you see that, token budgets in RAG, tolerance budgets in CAM, privacy budgets, latency deadlines, proof step fuel, retry limits, memory bounds, and risk bounds stop looking like unrelated engineering tricks. They are instances of the same resource-sensitive semantics.

