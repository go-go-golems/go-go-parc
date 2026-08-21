# CNC API Design

- URL: https://chatgpt.com/c/6a771aa3-181c-83ea-bb1f-fc7f54988b38
- Created: 2026-08-08T12:01:41.655Z

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
> | Code Name Notes |                |                                                                                                                                                                              |
> | --------------- | -------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
> | `G0`            | Rapid traverse | Max machine speed. Ignores `F`. Classically axes may move at independent rates (dogleg path) — do not assume a straight line for clearance. Positioning only, never cutting. |
> | `G1`            | Linear feed    | Coordinated straight line at the active `F`. The workhorse.                                                                                                                  |
> | `G2`            | Arc CW         | Center form `G2 X.. Y.. I.. J..` (I/J = center offset *from start point*) or radius form `G2 X.. Y.. R..`.                                                                   |
> | `G3`            | Arc CCW        | Same syntax as `G2`.                                                                                                                                                         |
> | `G4`            | Dwell          | `G4 P1.5` — pause. Units of P vary by control (seconds vs ms).                                                                                                               |
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
> | Code Meaning |                                                                      |
> | ------------ | -------------------------------------------------------------------- |
> | `M3`         | Spindle on, clockwise (at the active `S`)                            |
> | `M4`         | Spindle on, counter-clockwise                                        |
> | `M5`         | Spindle stop                                                         |
> | `M6`         | Tool change                                                          |
> | `M8` / `M9`  | Flood coolant on / off                                               |
> | `M0`         | Program pause, resume on operator input                              |
> | `M1`         | Optional stop (only if the panel switch is on)                       |
> | `M2`         | Program end                                                          |
> | `M30`        | Program end + rewind. Usually also resets modals — prefer over `M2`. |
>
> `M02` and `M2` are identical; leading zeros are cosmetic. Your file uses `M5` in one place and `M05` in another, which is harmless but reveals inconsistent post-processor templates.
>
> ---
>
> ## Homing
>
> | Code Behaviour |                                                                                         |
> | -------------- | --------------------------------------------------------------------------------------- |
> | `G28`          | Return to reference (home) position.                                                    |
> | `G28 X0 Y0`    | Go to the **intermediate point** X0 Y0 in the *current* coordinate system, *then* home. |
> | `G30`          | Return to secondary reference point.                                                    |
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
> | Code Direction On no-contact |                                   |                   |
> | ---------------------------- | --------------------------------- | ----------------- |
> | `G38.2`                      | Toward workpiece, stop on contact | **Error**         |
> | `G38.3`                      | Toward workpiece, stop on contact | Continue silently |
> | `G38.4`                      | Away, stop on loss of contact     | **Error**         |
> | `G38.5`                      | Away, stop on loss of contact     | Continue silently |
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

I’ll treat the uploaded CAM as a concrete prototype, then separate its concerns into a typed semantic IR, a compositional geometry layer, and machine-specific lowering. I’ll also state the laws/invariants each layer should preserve.

<details><summary>💭 Thinking</summary>

**Modeling the compiler**

I’m designing a layered system: typed geometry and units first, immutable paths next, then motion IR carrying feeds, probing, and intent. I’m treating programs as composable state transitions that can eventually interpret into machine instructions.

**Modeled the compiler**

**Refining semantics**

I’m separating pure geometry from machine effects and controller-specific modal encoding. Programs compose as state transitions, while backends preserve observable behavior through validated lowering, optimization, and explicit handling of frames, tools, probing, and errors.

**Refined semantics**

</details>

The uploaded prototype already has the seed of the right split: it builds semantic-ish moves (`rapid`, `plunge`, `ramp`, `cut`) and only later emits G-code.  The main redesign is to make that middle layer mathematically precise and keep G-code notions out of it.

I would make the core abstraction **neither G-code nor “a list of moves.”** It should be a small semantic language whose values denote geometry, tool motion, and machine-state transitions. G-code is then one interpretation of that language.

Your current prototype is already pointing in this direction: job generation produces semantic-ish move classes before `toGcode` exists. fileciteturn0file0L478-L488 But the representation currently collapses those moves into point arrays, then later tries to recover higher-order structure such as arcs. fileciteturn0file0L952-L967 I would formalize that middle layer rather than extending the G-code layer upward.

## 1. Three languages, not one

I would explicitly have three IR levels:

```text
Declarative CAM
    ↓ planning
Geometric / Machine Semantic IR
    ↓ machine lowering
Controller IR
    ↓ postprocessor
G-code text
```

The **Declarative CAM API** is what humans want to use:

```js
pocket(region, {...})
profile(curve, {...})
surface(model, {...})
drill(points, {...})
```

The **Semantic IR** contains exact tool trajectories and machine actions:

```js
feedAlong(curve, ...)
rapidTo(pose)
toolChange(tool)
spindle(...)
probeAlong(...)
dwell(...)
```

The **Controller IR** knows about things like modal groups, available planes, work-offset registers, macro variables, and whether arcs are supported.

Only the final postprocessor knows that those concepts happen to be spelled `G1`, `G17`, `G54`, `M3`, and so forth.

This separation is particularly useful because your current `compressCut()` embeds `G17/G18/G19` into the arc representation itself. fileciteturn0file0L1009-L1040 That information belongs one layer lower. An arc is geometrically an arc; whether a controller can encode it with `G18` is a property of the target machine.

---

# 2. Give geometry an actual denotation

The most important rule I would adopt is:

> **Geometry denotes mathematical objects. Discretization is an implementation detail.**

For example, don't make a path fundamentally be:

```js
[x0, y0, z0, x1, y1, z1, ...]
```

Instead:

```ts
type Curve3<F> =
  | Line3<F>
  | CircularArc3<F>
  | Bezier3<F>
  | CompositeCurve3<F>;
```

where conceptually a curve is

$$
\gamma : [0,1] \to \mathbb{R}^3
$$

or, more generally for future 5-axis work,

$$
\gamma : [0,1] \to SE(3)
$$

because the tool has both a position and orientation.

A circular arc should therefore look something like:

```ts
interface CircularArc3<F> {
  readonly kind: "arc";
  readonly start: Pose<F>;
  readonly end: Pose<F>;
  readonly center: Point3<F>;
  readonly normal: Vector3<F>;
  readonly sweep: Angle;
}
```

No `G17`.

No `I`, `J`, or `K`.

No CW/CCW from the perspective of a controller plane.

Those are properties produced when lowering this geometric object to a particular controller.

That immediately removes a substantial amount of accidental complexity from your arc fitting code.

---

# 3. Paths form a category

There is a particularly natural categorical structure here.

Take points/poses as objects and continuous paths between them as morphisms:

$$
p \xrightarrow{\gamma} q
$$

Two paths compose exactly when the endpoint of one equals the start point of the next:

$$
\gamma_1 : p \to q
\qquad
\gamma_2 : q \to r
$$

giving

$$
\gamma_2 \circ \gamma_1 : p \to r.
$$

The identity morphism is the zero-length path.

So your fundamental path API can literally obey the category laws:

$$
(f \circ g) \circ h
=
f \circ (g \circ h)
$$

and

$$
id \circ f = f = f \circ id.
$$

In TypeScript-ish form:

```ts
interface Path<F> {
  readonly start: Pose<F>;
  readonly end: Pose<F>;
  readonly segments: readonly Curve3<F>[];
}

function concat<F>(a: Path<F>, b: Path<F>): Path<F> {
  assertPoseEqual(a.end, b.start);
  return path([...a.segments, ...b.segments]);
}
```

This is much more than mathematical decoration. It means discontinuous paths become structurally invalid rather than something discovered when the machine suddenly jumps.

Transforms then act functorially:

$$
T(id_p)=id_{T(p)}
$$

and

$$
T(g\circ f)=T(g)\circ T(f).
$$

These become excellent property tests.

---

# 4. Geometry itself should be algebraic

For ordinary 2.5D CAM, I would treat planar machining geometry primarily as **regular closed subsets of** $\mathbb R^2$, rather than as arbitrary polygon lists.

Then:

```js
union(a, b)
intersect(a, b)
difference(a, b)
offset(a, radius)
boundary(a)
transform(T, a)
```

have clear mathematical meanings.

For example, cutter compensation and tool-accessible regions are naturally related to Minkowski operations:

$$
A \oplus B
=
\{a+b\mid a\in A,b\in B\}.
$$

A tool-center exclusion region is essentially an obstacle dilated by the reflected cutter.

Your drop-cutter algorithm is already working with this sort of geometry implicitly: it constructs a cutter-location surface from the model and cutter geometry. The current code's evaluator computes exactly this collision-envelope concept for ball and flat tools. fileciteturn0file0L203-L307

Making that concept explicit gives you a common mathematical foundation for pocketing, offsets, drop-cutting, collision detection, verification, and eventually 5-axis configuration-space reasoning.

---

# 5. Separate “motion” from “intent”

One thing I would definitely change from the prototype is this:

```js
rapid
plunge
ramp
cut
```

Those aren't all the same kind of classification.

In your existing implementation, `plunge` and `ramp` simply select different feedrates, and both ultimately lower to `G1`. fileciteturn0file0L483-L486 fileciteturn0file0L1143-L1148

So a better semantic decomposition is:

```ts
type Motion<F> =
  | RapidTo<F>
  | FeedAlong<F>
  | ProbeAlong<F>;
```

and then feed moves carry **intent**:

```ts
interface FeedAlong<F> {
  readonly kind: "feed";
  readonly path: Path<F>;
  readonly feed: FeedRate;

  readonly intent:
    | "entry"
    | "rough"
    | "finish"
    | "link"
    | "air";

  readonly contact:
    | { kind: "removeMaterial"; tool: ToolRef }
    | { kind: "forbidMaterialContact" };
}
```

A helix is therefore not a special machine operation.

It is just:

```text
FeedAlong(
    Helix(...),
    intent = entry
)
```

A plunge is:

```text
FeedAlong(
    Line(...vertical...),
    intent = entry
)
```

This cleans up both the semantics and the downstream simulator.

---

# 6. Rapid is semantically special

Your cheat sheet contains an important detail that should influence the IR design:

**G0 does not necessarily denote a straight line.**

Therefore this is actually misleading:

```ts
RapidAlong(Line3)
```

because it claims a geometric path that the controller may not execute.

I would make rapid fundamentally endpoint-based:

```ts
interface RapidTo<F> {
  readonly kind: "rapid";
  readonly target: Pose<F>;
}
```

Its denotation is machine-dependent:

$$
Rapid_M(p,q)
\subseteq Paths(p,q).
$$

For a machine with independent-axis rapid motion, the actual trajectory is determined by the machine/controller kinematics.

Consequently a safety proof for a rapid is:

$$
\forall \gamma \in Rapid_M(p,q),
\quad
Sweep(tool,\gamma)\cap Obstacles=\emptyset.
$$

If you specifically require a geometrically straight non-cutting move, that's a coordinated feed move, not a rapid:

```js
feedAlong(line(a, b), {
  feed: machine.highTraverseFeed,
  intent: "air"
});
```

That distinction eliminates an entire category of bad assumptions.

---

# 7. Machine programs are state transformations

Now introduce a semantic machine state:

```ts
interface MachineState {
  pose: Pose<MachineFrame>;
  tool: ToolRef | null;

  spindle:
    | { mode: "off" }
    | { mode: "cw" | "ccw"; rpm: AngularSpeed };

  coolant: "off" | "flood" | "mist";

  frames: FrameBindings;
}
```

Then a program denotes a partial state transformation:

$$
\llbracket P\rrbracket :
(MachineState,World)
\to
Result<(MachineState,World),Fault>.
$$

Categorically, these are arrows in the Kleisli category of a state/error computation.

Composition is just sequential program composition.

This gives `seq()` an exact denotation:

```js
seq(a, b, c)
```

means

$$
\llbracket c\rrbracket
\circ
\llbracket b\rrbracket
\circ
\llbracket a\rrbracket.
$$

That becomes your fundamental program combinator.

---

# 8. Material removal has an unusually clean semantics

This is where the mathematical model gets especially useful.

Let the stock be a solid

$$
S\subseteq\mathbb R^3
$$

and the cutter geometry be

$$
K\subseteq\mathbb R^3.
$$

For a tool trajectory

$$
\gamma:[0,1]\to SE(3)
$$

define its swept volume:

$$
Sweep(K,\gamma)
=
\bigcup_{t\in[0,1]}
\gamma(t)K.
$$

Then a cutting motion has the simple denotation:

$$
S'
=
S\setminus Sweep(K,\gamma).
$$

This should be the reference semantics of your simulator.

Your current dexel verification already approximates precisely this idea: it sweeps the cutter footprint along every non-rapid segment and updates a stock height field. fileciteturn0file0L1247-L1267

So dexel simulation isn't a separate conceptual feature. It's one numerical interpreter for the semantic definition above.

Later you can add other interpreters:

```text
Semantic removal
      ↓
Dexel interpreter
Voxel interpreter
Exact B-rep interpreter
GPU heightfield interpreter
Collision-only interpreter
```

All are approximations/interpretations of the same operation.

---

# 9. Coordinate systems should be frames, not G90/G54/G53

Make coordinate frames part of the type system:

```ts
type Machine = Frame<"machine">;
type Part = Frame<"part">;
type Fixture = Frame<"fixture">;

Point3<Part>
Point3<Machine>
```

and define transformations:

```ts
Transform<Part, Machine>
```

Conceptually these are elements of $SE(3)$ for rigid coordinate systems.

Then:

```js
transform(partToMachine, p)
```

is well-defined, while accidentally adding a machine-coordinate point to a work-coordinate vector can be rejected.

This also gives a much cleaner meaning to G-code coordinate features.

`G90/G91` disappear from Semantic IR entirely. They are encoding strategies.

`G20/G21` disappear too; quantities have actual dimensions.

`G17/G18/G19` disappear.

`G53` means the backend is encoding a motion whose target is expressed in the machine frame.

`G54` means the backend chose to realize some `Part → Machine` frame binding using controller work-offset register 1.

That's a huge improvement in reasoning ability.

---

# 10. Units should be values, not conventions

Even if the runtime representation is just numbers, the API should expose dimensional values:

```ts
const d = mm(3);
const feed = mmPerMin(600);
const speed = rpm(10_000);
const delay = seconds(1.5);
```

Internally everything can normalize to SI or mm-based canonical units.

At minimum TypeScript branding can prevent:

```ts
rpm(10000) + mm(3)
```

or accidentally supplying a feed rate where a length was expected.

This is a very cheap guarantee.

---

# 11. A good minimal Semantic IR

I would start approximately here:

```ts
type Primitive<F> =
  | {
      tag: "rapidTo";
      target: Pose<F>;
    }

  | {
      tag: "feedAlong";
      path: Path<F>;
      feed: FeedRate;
      intent: "entry" | "rough" | "finish" | "link" | "air";
      contact:
        | { kind: "cut"; tool: ToolRef }
        | { kind: "none" };
    }

  | {
      tag: "toolChange";
      tool: ToolRef;
    }

  | {
      tag: "spindle";
      mode: "off" | "cw" | "ccw";
      rpm?: AngularSpeed;
    }

  | {
      tag: "coolant";
      mode: "off" | "flood" | "mist";
    }

  | {
      tag: "dwell";
      duration: Duration;
    }

  | {
      tag: "pause";
      optional: boolean;
    }

  | {
      tag: "home";
      axes?: readonly Axis[];
    }

  | {
      tag: "end";
    };
```

Then:

```ts
type Program<F> =
  | { tag: "empty" }
  | { tag: "primitive"; value: Primitive<F> }
  | { tag: "seq"; children: readonly Program<F>[] };
```

This AST is essentially the **free category/free monoid generated by your machine primitives**.

An interpreter is just a fold over it.

That makes G-code generation, simulation, visualization, time estimation, machine-state validation, and pretty-printing all independent interpretations of one structure.

---

# 12. Probing is where you eventually need a monad

Ordinary static CAM has no returned values, so `seq()` is enough.

Probing changes that:

```text
probe Z
     ↓
returns hit position
     ↓
use hit position to establish work frame
```

That's an effect producing a runtime result.

This is where a free-monad/algebraic-effects formulation becomes genuinely useful rather than decorative.

Conceptually:

```ts
Probe : Program<ProbeResult>
```

and

```ts
flatMap :
  Program<A> ->
  (A -> Program<B>) ->
  Program<B>
```

But there is an important staging issue.

This must **not** happen:

```js
const hit = probe(...);
if (hit.z > 5) { ... }
```

because `hit.z` doesn't exist while your JS CAM program is being constructed.

Instead the value should be symbolic:

```ts
Expr<Length>
```

So something like:

```js
program(function* ($) {
  const hit = yield* $(probe.towardZ(...));

  yield* $(
    frames.setOriginZ(
      partFrame,
      sub(hit.position.z, probeTipOffset)
    )
  );
});
```

A LinuxCNC-style post could lower that symbolic value to `#5063`.

A controller without macro/runtime-expression capabilities rejects it.

A live machine interpreter could actually execute the probe and resume the JS computation.

Same semantic program; different interpreters.

---

# 13. Controller capabilities are part of compilation

The target should have a declarative capability description:

```ts
interface MachineProfile {
  axes: Axes;
  limits: Limits;

  rapidModel: RapidModel;

  capabilities: {
    arcsXY: boolean;
    arcsXZ: boolean;
    arcsYZ: boolean;

    probe: boolean;
    runtimeVariables: boolean;

    toolChange: boolean;
    coolant: boolean;
    workOffsets: number;
  };

  tolerances: {
    path: Length;
  };
}
```

Then lowering is:

```ts
lower(
  semanticProgram,
  machineProfile
): Result<ControllerProgram, Diagnostic[]>
```

If an exact circular arc is unsupported, flatten it within tolerance.

If only XY arcs are supported, flatten non-XY arcs.

If no automatic tool changer exists, a policy might lower `toolChange(T2)` to a safe retract + `M0`.

Or it can reject it.

This is vastly better than having CAM algorithms know controller restrictions.

---

# 14. Treat compilation as a semantics-preserving functor

There is a useful north-star property for every compiler pass.

Given:

$$
C : SemanticProgram \to ControllerProgram
$$

we want

$$
C(g\circ f)
\equiv
C(g)\circ C(f)
$$

up to the permitted observational equivalence.

For exact lowering, that means identical machine effects.

For approximation passes, define an explicit tolerance:

$$
d_H(
Trace(P),
Trace(C(P))
)
\le \epsilon
$$

where $d_H$ is, for example, Hausdorff distance between tool-center trajectories.

Arc compression then becomes a well-specified optimization:

```text
polycurve
   ↓ approximate ε
line/arc curve
```

rather than "find some G2/G3s".

Your current code performs this optimization after finishing paths have already been turned into sampled points. fileciteturn0file0L952-L967 I would invert that worldview: lines and arcs should remain first-class as long as possible, and tessellation should happen only when a target can't express them.

---

# 15. The high-level API can then be very pleasant

For example:

```js
const outline =
  region.roundRect({
    width: mm(50),
    height: mm(30),
    radius: mm(4),
  });

const holes = union(
  circle(pt(-15, 0), mm(2)),
  circle(pt( 15, 0), mm(2)),
);

const part = difference(outline, holes);

const t1 = tools.flatEndMill({
  id: 1,
  diameter: mm(3),
});

const job = seq(
  machine.toolChange(t1),

  machine.spindle.cw(rpm(10_000)),

  cam.pocket(part, {
    tool: t1,
    top: mm(0),
    bottom: mm(-3),
    stepDown: mm(1),
    stepOver: ratio(0.45),
    feed: mmPerMin(600),

    entry: cam.entry.auto({
      maxRampAngle: deg(3),
    }),
  }),

  cam.profile(outline.boundary(), {
    tool: t1,
    depth: mm(-3),
    feed: mmPerMin(500),
  }),

  machine.spindle.stop(),

  machine.end()
);
```

`cam.pocket()` does **not** output G-code.

Its type is essentially:

```ts
Region2 × PocketParameters
    → Result<Program, PlanningError>
```

That's the separation I would build the whole library around.

---

# 16. Guarantees worth making first-class

I would design the validator/compiler around a relatively small set of explicit guarantees:

- **Dimensional correctness:** lengths, rates, angles, and time cannot be accidentally interchanged.
- **Frame correctness:** every geometric quantity belongs to a coordinate frame, and cross-frame operations require an explicit transform.
- **Path continuity:** concatenated geometric paths must share endpoints.
- **State correctness:** cutting can require the expected tool, spindle state, and other preconditions.
- **Capability correctness:** compilation succeeds only when every semantic operation can be faithfully implemented or approximated within declared tolerance.
- **Safety obligations:** rapids, air moves, limits, fixtures, stock contact, and retracts can each be `checked`, `assumed`, or `unknown`; production emission can require a configured assurance level.
- **Approximation bounds:** tessellation and arc fitting must report and respect geometric error tolerances.
- **Material monotonicity:** a cutting interpreter may only produce $S'\subseteq S$; it never creates stock.
- **Compiler equivalence:** modal compression must not change the interpreted tool trace or machine actions.

That last one is especially useful for G-code.

You can generate a maximally explicit controller program, interpret it, run modal compression, interpret the compressed version, and property-test that the traces are equivalent.

---

# 17. I would split your existing `toGcode` in two

Right now `toGcode()` is simultaneously choosing feeds, maintaining modal plane state, choosing G2/G3 orientation, formatting coordinates, and emitting text. fileciteturn0file0L1115-L1185

I would turn it into:

```text
Semantic IR
     │
     ▼
lowerForMachine()
     │
     ▼
Controller IR
     │
     ▼
modalize()
     │
     ▼
GCode Blocks
     │
     ▼
printGCode()
```

`modalize()` is where state such as the currently selected plane and current feed lives.

And a block itself should initially be structured data:

```ts
interface GBlock {
  motion?: MotionCode;
  coordinates?: AxisWords;
  arcCenter?: AxisWords;

  feed?: number;
  spindleSpeed?: number;

  modal?: readonly ModalChange[];
  machine?: readonly MAction[];
}
```

The text printer then does almost nothing.

This also reflects your cheat sheet's point that a G-code block is semantically a block of simultaneously interpreted words, not a little imperative sequence of tokens.

---

# 18. The most important refactor of Dropcut

I would make the first refactor surprisingly small.

Today you have:

```js
moves.push({
  kind,
  phase,
  pts
});
```

in the job generator. fileciteturn0file0L546-L560

Replace that conceptual type with something like:

```ts
Motion =
  | RapidTo
  | FeedAlong<Path>
```

and make `Path` contain actual:

```text
Line
Arc
Helix
Polyline
CompositePath
```

Then make `plunge`, `ramp`, `rough`, and `finish` annotations on `FeedAlong`, rather than motion types.

After that, rewrite your verifier to interpret `FeedAlong` and `RapidTo` rather than numeric `kinds`.

Then rewrite the G-code exporter as another interpreter.

At that point the architecture exists.

Everything else—pocketing, drilling, contouring, probing, canned cycles, 5-axis, machine simulation—can grow without turning the IR into a G-code-shaped object.

The concise mathematical description of the architecture would be:

$$
\boxed{
\text{CAM}
\;\xrightarrow{\text{planning}}\;
\text{Free category of typed machine effects over geometric paths}
\;\xrightarrow{\text{semantics-preserving lowering}}\;
\text{Controller program}
}
$$

with geometry living in spaces like $\mathbb R^2,\mathbb R^3,SE(3)$, cutting denoted by swept-volume subtraction, machine actions denoted by partial state transformations, and backends implemented as interpreters/folds of the same semantic program.

That is a foundation strong enough to make the JS surface API simple without making the implementation simplistic.

