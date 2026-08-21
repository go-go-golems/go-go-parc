# JS API for CNC CAM

- URL: https://chatgpt.com/c/6a77109e-24bc-83ea-8041-53e20fa77135
- Created: 2026-08-08T11:18:54.763Z

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
> Take screenshots as you work. Write up a whole report in markdown + pdf along with the code.
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

<details><summary>💭 Thinking</summary>

**Planning the architecture**

I’m designing a comprehensive implementation around the provided source, including parsing, typed representations, semantics, validation, code generation, interpretation, tests, and documentation. I’ll ground the design in compositional mathematical concepts and the existing code.

**Planned the architecture**

</details>

```unknown
bash -lc cat /home/oai/skills/pdfs/SKILL.md && printf '\n---FILES---\n' && ls -la /mnt/data | sed -n '1,120p'
```

I’ll extract the prototype’s implicit CAM model, formalize a typed compositional IR and semantics, then implement a TypeScript compiler/interpreter with tests, examples, screenshots, and Markdown/PDF documentation.

<details><summary>💭 Thinking</summary>

**Refining safety semantics**

I’m specifying modal safety, effect tracking, continuity, finite values, capability limits, conservative collision checks, and typed machine states. I’m also treating sequential composition categorically while accounting for stateful compilation.

**Refined safety semantics**

**Designing the prototype**

I’m planning a dependency-free TypeScript package with a canonical motion IR, geometry builders, Drop-cut compatibility, machining operations, G-code compilation, simulation, validation, examples, and tests covering the listed commands and safety conditions.

**Designed the prototype**

</details>

```unknown
bash -lc node --version && npm --version && (tsc --version || true) && (npx --yes tsx --version || true) && (which chromium || which chromium-browser || which google-chrome || true) && (python -V)
```

<details><summary>💭 Thinking</summary>

**Auditing the source**

I’m examining the existing prototype’s combined geometry, CAM, G-code, verification, and UI responsibilities. I’m identifying its current motion representation and gaps around machine safety, tooling, dialects, and capability profiles.

**Audited the source**

</details>

```unknown
bash -lc python - <<'PY'
import re, pathlib, json
p=pathlib.Path('/mnt/data/dropcut-cam(1)(1).jsx')
s=p.read_text()
funcs=[]
for m in re.finditer(r'^(?:async\s+)?function\s+([A-Za-z_$][\w$]*)\s*\(', s, re.M):
    funcs.append(m.group(1))
const_funcs=[]
for m in re.finditer(r'^const\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?\(', s, re.M):
    const_funcs.append(m.group(1))
print('lines', len(s.splitlines()))
print('functions', len(funcs), funcs)
print('arrow const functions', len(const_funcs), const_funcs[:50])
for token in ['G0','G1','G2','G3','G17','G18','G19','G21','G90','G94','G53','G54','M6','M30','G38.2']:
    print(token, s.count(token))
print('moves push', s.count('moves.push'))
print('raw pts indexing', len(re.findall(r'pts\[', s)))
PY
```

The prototype’s `{kind, phase, pts, ops}` model provides reusable move intent, arc fitting, and dexel verification. I’ll decouple geometry, planning, safety, simulation, modal compilation, and dialect output.

<details><summary>💭 Thinking</summary>

**Designed CNC CAM JavaScript IR API and inspected compiler architecture**

</details>

```unknown
bash -lc set -euo pipefail
ROOT=/mnt/data/cnc-cam-ir
rm -rf "$ROOT"
mkdir -p "$ROOT"/{src,examples,test,type-tests,schema,artifacts/screenshots,artifacts/gcode,docs}
cat > "$ROOT/package.json" <<'EOF'
{
  "name": "@prototype/cnc-cam-ir",
  "version": "0.1.0",
  "private": true,
  "description": "A compositional, validated CNC CAM intermediate representation and G-code compiler prototype.",
  "type": "module",
  "main": "dist/src/index.js",
  "types": "dist/src/index.d.ts",
  "exports": {
    ".": {
      "types": "./dist/src/index.d.ts",
      "import": "./dist/src/index.js"
    }
  },
  "scripts": {
    "clean": "rm -rf dist",
    "build": "tsc -p tsconfig.json",
    "test": "npm run build && node --test test/*.test.mjs",
    "example": "npm run build && node dist/examples/badge.js"
  },
  "engines": {
    "node": ">=20"
  },
  "license": "UNLICENSED"
}
EOF
cat > "$ROOT/tsconfig.json" <<'EOF'
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noImplicitOverride": true,
    "useUnknownInCatchVariables": true,
    "declaration": true,
    "sourceMap": true,
    "rootDir": ".",
    "outDir": "dist",
    "skipLibCheck": true
  },
  "include": ["src/**/*.ts", "examples/**/*.ts", "type-tests/**/*.ts"]
}
EOF
cat > "$ROOT/src/units.ts" <<'EOF'
/** Canonical units used by the machine-independent IR. */

declare const quantityBrand: unique symbol;

export type Quantity<Unit extends string> = number & {
  readonly [quantityBrand]: Unit;
};

export type Millimeters = Quantity<"mm">;
export type MillimetersPerMinute = Quantity<"mm/min">;
export type RevolutionsPerMinute = Quantity<"rpm">;
export type Seconds = Quantity<"s">;
export type Degrees = Quantity<"deg">;

function finite(value: number, label: string): number {
  if (!Number.isFinite(value)) {
    throw new RangeError(`${label} must be finite; received ${String(value)}`);
  }
  return value;
}

function nonNegative(value: number, label: string): number {
  finite(value, label);
  if (value < 0) throw new RangeError(`${label} must be >= 0; received ${value}`);
  return value;
}

function positive(value: number, label: string): number {
  finite(value, label);
  if (value <= 0) throw new RangeError(`${label} must be > 0; received ${value}`);
  return value;
}

/** A signed coordinate or distance in millimetres. */
export const mm = (value: number): Millimeters => finite(value, "millimetres") as Millimeters;

/** Convert inches to canonical millimetres. */
export const inch = (value: number): Millimeters => mm(finite(value, "inches") * 25.4);

export const mmPerMin = (value: number): MillimetersPerMinute =>
  positive(value, "feed rate") as MillimetersPerMinute;

export const rpm = (value: number): RevolutionsPerMinute =>
  nonNegative(value, "spindle speed") as RevolutionsPerMinute;

export const seconds = (value: number): Seconds =>
  nonNegative(value, "seconds") as Seconds;

export const degrees = (value: number): Degrees =>
  finite(value, "degrees") as Degrees;

/** Runtime erasure is intentional: quantities serialize as JSON numbers. */
export const scalar = <U extends string>(value: Quantity<U>): number => value as number;
EOF
cat > "$ROOT/src/math.ts" <<'EOF'
import { mm, type Millimeters } from "./units.js";

export type FrameId = "machine" | `G${54 | 55 | 56 | 57 | 58 | 59}` | (string & {});

export interface Point2<F extends FrameId = FrameId> {
  readonly frame: F;
  readonly x: Millimeters;
  readonly y: Millimeters;
}

export interface Point3<F extends FrameId = FrameId> extends Point2<F> {
  readonly z: Millimeters;
}

export interface Vector2 {
  readonly x: Millimeters;
  readonly y: Millimeters;
}

export interface Vector3 extends Vector2 {
  readonly z: Millimeters;
}

export interface AxisTarget {
  readonly x?: Millimeters;
  readonly y?: Millimeters;
  readonly z?: Millimeters;
}

export interface Box2<F extends FrameId = FrameId> {
  readonly frame: F;
  readonly min: Point2<F>;
  readonly max: Point2<F>;
}

export interface Box3<F extends FrameId = FrameId> {
  readonly frame: F;
  readonly min: Point3<F>;
  readonly max: Point3<F>;
}

export const point2 = <F extends FrameId>(frame: F, x: number, y: number): Point2<F> => ({
  frame,
  x: mm(x),
  y: mm(y),
});

export const point3 = <F extends FrameId>(frame: F, x: number, y: number, z: number): Point3<F> => ({
  frame,
  x: mm(x),
  y: mm(y),
  z: mm(z),
});

export const target = (coordinates: { x?: number; y?: number; z?: number }): AxisTarget => {
  const result: { x?: Millimeters; y?: Millimeters; z?: Millimeters } = {};
  if (coordinates.x !== undefined) result.x = mm(coordinates.x);
  if (coordinates.y !== undefined) result.y = mm(coordinates.y);
  if (coordinates.z !== undefined) result.z = mm(coordinates.z);
  return result;
};

export const box2 = <F extends FrameId>(
  frame: F,
  minX: number,
  minY: number,
  maxX: number,
  maxY: number,
): Box2<F> => {
  if (!(minX <= maxX && minY <= maxY)) throw new RangeError("Invalid Box2 bounds");
  return { frame, min: point2(frame, minX, minY), max: point2(frame, maxX, maxY) };
};

export const box3 = <F extends FrameId>(
  frame: F,
  minX: number,
  minY: number,
  minZ: number,
  maxX: number,
  maxY: number,
  maxZ: number,
): Box3<F> => {
  if (!(minX <= maxX && minY <= maxY && minZ <= maxZ)) throw new RangeError("Invalid Box3 bounds");
  return { frame, min: point3(frame, minX, minY, minZ), max: point3(frame, maxX, maxY, maxZ) };
};

export const distance2 = <F extends FrameId>(a: Point2<F>, b: Point2<F>): number =>
  Math.hypot((b.x as number) - (a.x as number), (b.y as number) - (a.y as number));

export const distance3 = <F extends FrameId>(a: Point3<F>, b: Point3<F>): number =>
  Math.hypot(
    (b.x as number) - (a.x as number),
    (b.y as number) - (a.y as number),
    (b.z as number) - (a.z as number),
  );

export interface Transform2<From extends FrameId, To extends FrameId> {
  readonly from: From;
  readonly to: To;
  /** Row-major affine matrix [a c tx; b d ty; 0 0 1]. */
  readonly matrix: readonly [number, number, number, number, number, number];
}

export const transform2 = <From extends FrameId, To extends FrameId>(
  from: From,
  to: To,
  matrix: readonly [number, number, number, number, number, number],
): Transform2<From, To> => {
  if (!matrix.every(Number.isFinite)) throw new RangeError("Transform contains a non-finite value");
  return { from, to, matrix };
};

export const identityTransform2 = <F extends FrameId>(frame: F): Transform2<F, F> =>
  transform2(frame, frame, [1, 0, 0, 1, 0, 0]);

export const translation2 = <From extends FrameId, To extends FrameId>(
  from: From,
  to: To,
  dx: number,
  dy: number,
): Transform2<From, To> => transform2(from, to, [1, 0, 0, 1, dx, dy]);

export const rotation2 = <From extends FrameId, To extends FrameId>(
  from: From,
  to: To,
  radians: number,
): Transform2<From, To> => {
  const c = Math.cos(radians);
  const s = Math.sin(radians);
  return transform2(from, to, [c, s, -s, c, 0, 0]);
};

export const composeTransform2 = <A extends FrameId, B extends FrameId, C extends FrameId>(
  first: Transform2<A, B>,
  second: Transform2<B, C>,
): Transform2<A, C> => {
  const [a1, b1, c1, d1, tx1, ty1] = first.matrix;
  const [a2, b2, c2, d2, tx2, ty2] = second.matrix;
  return transform2(first.from, second.to, [
    a2 * a1 + c2 * b1,
    b2 * a1 + d2 * b1,
    a2 * c1 + c2 * d1,
    b2 * c1 + d2 * d1,
    a2 * tx1 + c2 * ty1 + tx2,
    b2 * tx1 + d2 * ty1 + ty2,
  ]);
};

export const applyTransform2 = <A extends FrameId, B extends FrameId>(
  transform: Transform2<A, B>,
  point: Point2<A>,
): Point2<B> => {
  const [a, b, c, d, tx, ty] = transform.matrix;
  const x = point.x as number;
  const y = point.y as number;
  return point2(transform.to, a * x + c * y + tx, b * x + d * y + ty);
};

export const samePoint2 = <F extends FrameId>(a: Point2<F>, b: Point2<F>, tolerance = 1e-9): boolean =>
  distance2(a, b) <= tolerance;
EOF
cat > "$ROOT/src/geometry.ts" <<'EOF'
import {
  applyTransform2,
  distance2,
  point2,
  samePoint2,
  type FrameId,
  type Point2,
  type Transform2,
} from "./math.js";

export type ArcDirection = "cw" | "ccw";

export interface LineSegment2<F extends FrameId = FrameId> {
  readonly kind: "line";
  readonly from: Point2<F>;
  readonly to: Point2<F>;
}

export interface ArcSegment2<F extends FrameId = FrameId> {
  readonly kind: "arc";
  readonly from: Point2<F>;
  readonly to: Point2<F>;
  readonly center: Point2<F>;
  readonly direction: ArcDirection;
}

export type Segment2<F extends FrameId = FrameId> = LineSegment2<F> | ArcSegment2<F>;

export interface Path2<F extends FrameId = FrameId> {
  readonly frame: F;
  readonly start: Point2<F>;
  readonly segments: readonly Segment2<F>[];
  readonly closed: boolean;
}

export interface Region2<F extends FrameId = FrameId> {
  readonly frame: F;
  readonly outer: Path2<F>;
  readonly holes: readonly Path2<F>[];
}

function checkedArc<F extends FrameId>(arc: ArcSegment2<F>, tolerance = 1e-6): ArcSegment2<F> {
  const r0 = distance2(arc.from, arc.center);
  const r1 = distance2(arc.to, arc.center);
  if (r0 <= tolerance) throw new RangeError("Arc radius must be positive");
  if (Math.abs(r0 - r1) > tolerance) {
    throw new RangeError(`Arc endpoints are not equidistant from center (${r0} vs ${r1})`);
  }
  if (samePoint2(arc.from, arc.to, tolerance)) {
    throw new RangeError("A full circle must be represented by at least two arcs");
  }
  return arc;
}

export class Path2Builder<F extends FrameId> {
  readonly #frame: F;
  readonly #start: Point2<F>;
  #cursor: Point2<F>;
  readonly #segments: Segment2<F>[] = [];
  #closed = false;

  constructor(frame: F, x: number, y: number) {
    this.#frame = frame;
    this.#start = point2(frame, x, y);
    this.#cursor = this.#start;
  }

  lineTo(x: number, y: number): this {
    this.#assertOpen();
    const to = point2(this.#frame, x, y);
    if (!samePoint2(this.#cursor, to)) {
      this.#segments.push({ kind: "line", from: this.#cursor, to });
      this.#cursor = to;
    }
    return this;
  }

  arcTo(options: {
    readonly x: number;
    readonly y: number;
    readonly centerX: number;
    readonly centerY: number;
    readonly direction: ArcDirection;
  }): this {
    this.#assertOpen();
    const to = point2(this.#frame, options.x, options.y);
    const center = point2(this.#frame, options.centerX, options.centerY);
    const arc = checkedArc({
      kind: "arc",
      from: this.#cursor,
      to,
      center,
      direction: options.direction,
    });
    this.#segments.push(arc);
    this.#cursor = to;
    return this;
  }

  close(): this {
    this.#assertOpen();
    if (!samePoint2(this.#cursor, this.#start)) {
      this.#segments.push({ kind: "line", from: this.#cursor, to: this.#start });
      this.#cursor = this.#start;
    }
    this.#closed = true;
    return this;
  }

  build(): Path2<F> {
    if (this.#segments.length === 0) throw new RangeError("A path must contain at least one segment");
    return Object.freeze({
      frame: this.#frame,
      start: this.#start,
      segments: Object.freeze([...this.#segments]),
      closed: this.#closed,
    });
  }

  #assertOpen(): void {
    if (this.#closed) throw new Error("Cannot append to a closed path");
  }
}

export const path2 = <F extends FrameId>(frame: F, x: number, y: number): Path2Builder<F> =>
  new Path2Builder(frame, x, y);

export const polyline = <F extends FrameId>(
  frame: F,
  points: readonly (readonly [number, number])[],
  closed = false,
): Path2<F> => {
  if (points.length < 2) throw new RangeError("Polyline needs at least two points");
  const first = points[0];
  if (!first) throw new RangeError("Polyline is empty");
  const builder = path2(frame, first[0], first[1]);
  for (const p of points.slice(1)) builder.lineTo(p[0], p[1]);
  if (closed) builder.close();
  return builder.build();
};

export const rectangle = <F extends FrameId>(
  frame: F,
  options: { readonly centerX: number; readonly centerY: number; readonly width: number; readonly height: number },
): Path2<F> => {
  if (!(options.width > 0 && options.height > 0)) throw new RangeError("Rectangle dimensions must be positive");
  const x0 = options.centerX - options.width / 2;
  const x1 = options.centerX + options.width / 2;
  const y0 = options.centerY - options.height / 2;
  const y1 = options.centerY + options.height / 2;
  return path2(frame, x0, y0).lineTo(x1, y0).lineTo(x1, y1).lineTo(x0, y1).close().build();
};

export const roundedRectangle = <F extends FrameId>(
  frame: F,
  options: {
    readonly centerX: number;
    readonly centerY: number;
    readonly width: number;
    readonly height: number;
    readonly radius: number;
  },
): Path2<F> => {
  const { centerX: cx, centerY: cy, width: w, height: h, radius: r } = options;
  if (!(w > 0 && h > 0 && r > 0 && 2 * r <= Math.min(w, h))) {
    throw new RangeError("Invalid rounded rectangle dimensions");
  }
  const x0 = cx - w / 2;
  const x1 = cx + w / 2;
  const y0 = cy - h / 2;
  const y1 = cy + h / 2;
  return path2(frame, x0 + r, y0)
    .lineTo(x1 - r, y0)
    .arcTo({ x: x1, y: y0 + r, centerX: x1 - r, centerY: y0 + r, direction: "ccw" })
    .lineTo(x1, y1 - r)
    .arcTo({ x: x1 - r, y: y1, centerX: x1 - r, centerY: y1 - r, direction: "ccw" })
    .lineTo(x0 + r, y1)
    .arcTo({ x: x0, y: y1 - r, centerX: x0 + r, centerY: y1 - r, direction: "ccw" })
    .lineTo(x0, y0 + r)
    .arcTo({ x: x0 + r, y: y0, centerX: x0 + r, centerY: y0 + r, direction: "ccw" })
    .close()
    .build();
};

export const circle = <F extends FrameId>(
  frame: F,
  options: { readonly centerX: number; readonly centerY: number; readonly radius: number },
): Path2<F> => {
  const { centerX: cx, centerY: cy, radius: r } = options;
  if (!(r > 0)) throw new RangeError("Circle radius must be positive");
  return path2(frame, cx + r, cy)
    .arcTo({ x: cx, y: cy + r, centerX: cx, centerY: cy, direction: "ccw" })
    .arcTo({ x: cx - r, y: cy, centerX: cx, centerY: cy, direction: "ccw" })
    .arcTo({ x: cx, y: cy - r, centerX: cx, centerY: cy, direction: "ccw" })
    .arcTo({ x: cx + r, y: cy, centerX: cx, centerY: cy, direction: "ccw" })
    .close()
    .build();
};

export const region = <F extends FrameId>(outer: Path2<F>, holes: readonly Path2<F>[] = []): Region2<F> => {
  if (!outer.closed) throw new RangeError("Region outer path must be closed");
  for (const hole of holes) {
    if (hole.frame !== outer.frame || !hole.closed) throw new RangeError("Region holes must be closed and share the frame");
  }
  return { frame: outer.frame, outer, holes: Object.freeze([...holes]) };
};

export const transformPath2 = <A extends FrameId, B extends FrameId>(
  path: Path2<A>,
  transform: Transform2<A, B>,
): Path2<B> => ({
  frame: transform.to,
  start: applyTransform2(transform, path.start),
  closed: path.closed,
  segments: path.segments.map((segment): Segment2<B> => {
    if (segment.kind === "line") {
      return {
        kind: "line",
        from: applyTransform2(transform, segment.from),
        to: applyTransform2(transform, segment.to),
      };
    }
    return checkedArc({
      kind: "arc",
      from: applyTransform2(transform, segment.from),
      to: applyTransform2(transform, segment.to),
      center: applyTransform2(transform, segment.center),
      direction: segment.direction,
    }, 1e-5);
  }),
});

export const pathLength = <F extends FrameId>(path: Path2<F>): number =>
  path.segments.reduce((sum, segment) => {
    if (segment.kind === "line") return sum + distance2(segment.from, segment.to);
    const r = distance2(segment.from, segment.center);
    const a0 = Math.atan2((segment.from.y as number) - (segment.center.y as number), (segment.from.x as number) - (segment.center.x as number));
    const a1 = Math.atan2((segment.to.y as number) - (segment.center.y as number), (segment.to.x as number) - (segment.center.x as number));
    let sweep = a1 - a0;
    if (segment.direction === "ccw") {
      while (sweep <= 0) sweep += Math.PI * 2;
    } else {
      while (sweep >= 0) sweep -= Math.PI * 2;
    }
    return sum + Math.abs(sweep) * r;
  }, 0);
EOF
cat > "$ROOT/src/ir.ts" <<'EOF'
import type { ArcDirection } from "./geometry.js";
import type { AxisTarget, FrameId, Point3 } from "./math.js";
import type {
  Millimeters,
  MillimetersPerMinute,
  RevolutionsPerMinute,
  Seconds,
} from "./units.js";

export type Plane = "XY" | "XZ" | "YZ";
export type Engagement = "air" | "cut" | "probe";
export type SpindleMode = "cw" | "ccw" | "off";
export type CoolantMode = "flood" | "mist" | "off";

export interface ToolDefinition<Id extends number = number> {
  readonly id: Id;
  readonly kind: "flat-end" | "ball-nose" | "drill" | "v-bit" | "custom";
  readonly diameter: Millimeters;
  readonly fluteLength?: Millimeters;
  readonly description?: string;
}

export interface InstructionMeta {
  readonly operationId?: string;
  readonly operationLabel?: string;
  readonly source?: string;
  readonly notes?: readonly string[];
}

interface BaseInstruction {
  readonly meta?: InstructionMeta;
}

export interface SetModesInstruction extends BaseInstruction {
  readonly kind: "set-modes";
  readonly units: "mm";
  readonly distance: "absolute";
  readonly feedMode: "per-minute";
  readonly plane: Plane;
}

export interface SelectWorkOffsetInstruction extends BaseInstruction {
  readonly kind: "select-work-offset";
  readonly index: 1 | 2 | 3 | 4 | 5 | 6;
}

export interface CommentInstruction extends BaseInstruction {
  readonly kind: "comment";
  readonly text: string;
}

export interface ToolChangeInstruction extends BaseInstruction {
  readonly kind: "tool-change";
  readonly tool: ToolDefinition;
}

export interface SpindleInstruction extends BaseInstruction {
  readonly kind: "spindle";
  readonly mode: SpindleMode;
  readonly speed?: RevolutionsPerMinute;
}

export interface CoolantInstruction extends BaseInstruction {
  readonly kind: "coolant";
  readonly mode: CoolantMode;
}

export interface RapidInstruction extends BaseInstruction {
  readonly kind: "rapid";
  readonly frame: "machine" | "work";
  readonly target: AxisTarget;
}

export interface LinearInstruction extends BaseInstruction {
  readonly kind: "linear";
  readonly frame: "work";
  readonly target: AxisTarget;
  readonly feed: MillimetersPerMinute;
  readonly engagement: Engagement;
}

export interface ArcInstruction extends BaseInstruction {
  readonly kind: "arc";
  readonly frame: "work";
  readonly plane: Plane;
  readonly target: AxisTarget;
  /** Center offset from the arc start, expressed in canonical XYZ axes. */
  readonly centerOffset: AxisTarget;
  readonly direction: ArcDirection;
  readonly feed: MillimetersPerMinute;
  readonly engagement: Engagement;
}

export interface DwellInstruction extends BaseInstruction {
  readonly kind: "dwell";
  readonly duration: Seconds;
}

export interface ProbeInstruction extends BaseInstruction {
  readonly kind: "probe";
  readonly frame: "work";
  readonly target: AxisTarget;
  readonly feed: MillimetersPerMinute;
  readonly errorOnMiss: boolean;
  readonly sense: "contact" | "loss";
}

export interface PauseInstruction extends BaseInstruction {
  readonly kind: "pause";
  readonly optional: boolean;
  readonly message?: string;
}

export interface HomeInstruction extends BaseInstruction {
  readonly kind: "home";
  readonly axes?: readonly ("X" | "Y" | "Z")[];
}

export interface EndInstruction extends BaseInstruction {
  readonly kind: "end";
  readonly rewind: boolean;
}

export type Instruction =
  | SetModesInstruction
  | SelectWorkOffsetInstruction
  | CommentInstruction
  | ToolChangeInstruction
  | SpindleInstruction
  | CoolantInstruction
  | RapidInstruction
  | LinearInstruction
  | ArcInstruction
  | DwellInstruction
  | ProbeInstruction
  | PauseInstruction
  | HomeInstruction
  | EndInstruction;

export interface CanonicalProgram {
  readonly version: "cnc-ir/0.1";
  readonly name: string;
  readonly instructions: readonly Instruction[];
}

export interface AxisState {
  readonly x?: Millimeters;
  readonly y?: Millimeters;
  readonly z?: Millimeters;
}

export interface MachineState {
  readonly units: "mm";
  readonly distance: "absolute";
  readonly feedMode: "per-minute";
  readonly plane: Plane;
  readonly workOffset?: 1 | 2 | 3 | 4 | 5 | 6;
  readonly tool?: ToolDefinition;
  readonly spindle: { readonly mode: SpindleMode; readonly speed?: RevolutionsPerMinute };
  readonly coolant: CoolantMode;
  readonly workPosition: AxisState;
  readonly machinePosition: AxisState;
  readonly ended: boolean;
}

export interface LineTrajectory {
  readonly kind: "line";
  readonly frame: "work" | "machine";
  readonly start: AxisState;
  readonly end: AxisState;
  readonly feed?: MillimetersPerMinute;
  readonly rapid: boolean;
}

export interface ArcTrajectory {
  readonly kind: "arc";
  readonly frame: "work";
  readonly plane: Plane;
  readonly start: Point3<FrameId>;
  readonly end: Point3<FrameId>;
  readonly center: Point3<FrameId>;
  readonly direction: ArcDirection;
  readonly feed: MillimetersPerMinute;
}

export type Trajectory = LineTrajectory | ArcTrajectory;
EOF
cat > "$ROOT/src/program.ts" <<'EOF'
import type { Instruction, ToolDefinition } from "./ir.js";
import { mm, rpm, type RevolutionsPerMinute } from "./units.js";
import { target } from "./math.js";

const stateBrand: unique symbol = Symbol("stateBrand");

export interface Cold {
  readonly [stateBrand]: { readonly lifecycle: "cold" };
}

export interface Ended {
  readonly [stateBrand]: { readonly lifecycle: "ended" };
}

export interface NoTool {
  readonly kind: "none";
}

export interface Loaded<Id extends number> {
  readonly kind: "loaded";
  readonly id: Id;
}

export type ToolSlot = NoTool | Loaded<number>;
export type SpindleState = "off" | "on";

export interface Ready<Tool extends ToolSlot, Spindle extends SpindleState> {
  readonly [stateBrand]: {
    readonly lifecycle: "ready";
    readonly tool: Tool;
    readonly spindle: Spindle;
  };
}

export type Effect =
  | "setup"
  | "tool-change"
  | "spindle"
  | "coolant"
  | "motion"
  | "probe"
  | "operator"
  | "end"
  | "unsafe";

/**
 * An indexed program. Objects are typestates and arrows are programs.
 * `then` is categorical composition; `identity` is the identity arrow.
 */
export class Program<Input, Output, Effects extends Effect = never> {
  declare private readonly _inputInvariant: (value: Input) => Input;
  declare private readonly _outputInvariant: (value: Output) => Output;
  declare private readonly _effect: Effects;

  readonly name: string;
  readonly instructions: readonly Instruction[];

  /** @internal Use exported combinators or unsafeProgram. */
  constructor(name: string, instructions: readonly Instruction[]) {
    this.name = name;
    this.instructions = Object.freeze([...instructions]);
  }

  then<Next, MoreEffects extends Effect>(
    next: Program<Output, Next, MoreEffects>,
  ): Program<Input, Next, Effects | MoreEffects> {
    const name = this.name !== "fragment" ? this.name : next.name;
    return new Program(name, [...this.instructions, ...next.instructions]);
  }

  named(name: string): Program<Input, Output, Effects> {
    return new Program(name, this.instructions);
  }
}

/** @internal */
export const primitive = <Input, Output, Effects extends Effect>(
  instructions: readonly Instruction[],
): Program<Input, Output, Effects> => new Program("fragment", instructions);

export const identity = <State>(): Program<State, State, never> => primitive([]);

export interface BootstrapOptions {
  readonly name: string;
  readonly workOffset?: 1 | 2 | 3 | 4 | 5 | 6;
  readonly safeMachineZ: number;
  readonly comment?: string;
}

export const bootstrap = (
  options: BootstrapOptions,
): Program<Cold, Ready<NoTool, "off">, "setup" | "motion"> => {
  const workOffset = options.workOffset ?? 1;
  const instructions: Instruction[] = [
    { kind: "comment", text: options.comment ?? options.name },
    { kind: "set-modes", units: "mm", distance: "absolute", feedMode: "per-minute", plane: "XY" },
    { kind: "select-work-offset", index: workOffset },
    { kind: "rapid", frame: "machine", target: target({ z: options.safeMachineZ }) },
  ];
  return new Program(options.name, instructions);
};

export const defineTool = <const Id extends number>(
  id: Id,
  definition: Omit<ToolDefinition<Id>, "id" | "diameter"> & { readonly diameter: number },
): ToolDefinition<Id> => ({ ...definition, id, diameter: mm(definition.diameter) });

export const changeTool = <const Id extends number>(
  tool: ToolDefinition<Id>,
): Program<Ready<any, "off">, Ready<Loaded<Id>, "off">, "tool-change"> =>
  primitive([{ kind: "tool-change", tool }]);

export const spindleOn = <const Id extends number>(
  tool: ToolDefinition<Id>,
  speed: number | RevolutionsPerMinute,
  mode: "cw" | "ccw" = "cw",
): Program<Ready<Loaded<Id>, "off">, Ready<Loaded<Id>, "on">, "spindle"> => {
  const spindleSpeed = typeof speed === "number" ? rpm(speed) : speed;
  return primitive([{ kind: "spindle", mode, speed: spindleSpeed, meta: { notes: [`tool T${tool.id}`] } }]);
};

export const spindleOff = <const Id extends number>(
  tool: ToolDefinition<Id>,
): Program<Ready<Loaded<Id>, "on">, Ready<Loaded<Id>, "off">, "spindle"> =>
  primitive([{ kind: "spindle", mode: "off", meta: { notes: [`tool T${tool.id}`] } }]);

export const coolantOn = <const Id extends number, S extends SpindleState>(
  tool: ToolDefinition<Id>,
  spindle: S,
  mode: "flood" | "mist" = "flood",
): Program<Ready<Loaded<Id>, S>, Ready<Loaded<Id>, S>, "coolant"> =>
  primitive([{ kind: "coolant", mode, meta: { notes: [`tool T${tool.id}`] } }]);

export const coolantOff = <const Id extends number, S extends SpindleState>(
  tool: ToolDefinition<Id>,
  spindle: S,
): Program<Ready<Loaded<Id>, S>, Ready<Loaded<Id>, S>, "coolant"> =>
  primitive([{ kind: "coolant", mode: "off", meta: { notes: [`tool T${tool.id}`] } }]);

export const operatorPause = <T extends ToolSlot, S extends SpindleState>(
  optional: boolean,
  message?: string,
): Program<Ready<T, S>, Ready<T, S>, "operator"> => {
  const instruction: Instruction = message === undefined
    ? { kind: "pause", optional }
    : { kind: "pause", optional, message };
  return primitive([instruction]);
};

export interface FinishOptions {
  readonly safeMachineZ: number;
  readonly home?: boolean;
  readonly rewind?: boolean;
}

export const finish = (
  options: FinishOptions,
): Program<Ready<any, "off">, Ended, "motion" | "end"> => {
  const instructions: Instruction[] = [
    { kind: "rapid", frame: "machine", target: target({ z: options.safeMachineZ }) },
  ];
  if (options.home) instructions.push({ kind: "home" });
  instructions.push({ kind: "end", rewind: options.rewind ?? true });
  return primitive(instructions);
};

export const unsafeProgram = (
  name: string,
  instructions: readonly Instruction[],
): Program<unknown, unknown, "unsafe"> => new Program(name, instructions);
EOF
cat > "$ROOT/src/milling.ts" <<'EOF'
import type { Path2, Segment2 } from "./geometry.js";
import { point2, target, type Box2, type FrameId } from "./math.js";
import type { Instruction, ToolDefinition } from "./ir.js";
import { primitive, type Loaded, type Program, type Ready } from "./program.js";
import { mmPerMin, seconds, type MillimetersPerMinute } from "./units.js";

export interface CuttingParameters {
  readonly topZ: number;
  readonly bottomZ: number;
  readonly stepDown: number;
  readonly safeZ: number;
  readonly feed: number | MillimetersPerMinute;
  readonly plungeFeed: number | MillimetersPerMinute;
}

export interface OperationOptions {
  readonly id?: string;
  readonly label?: string;
}

let operationCounter = 0;

function operationMeta(options: OperationOptions | undefined, fallback: string) {
  const id = options?.id ?? `op-${++operationCounter}`;
  return { operationId: id, operationLabel: options?.label ?? fallback } as const;
}

function feed(value: number | MillimetersPerMinute): MillimetersPerMinute {
  return typeof value === "number" ? mmPerMin(value) : value;
}

function depthLevels(topZ: number, bottomZ: number, stepDown: number): number[] {
  if (!(stepDown > 0)) throw new RangeError("stepDown must be positive");
  if (!(bottomZ < topZ)) throw new RangeError("bottomZ must be below topZ");
  const levels: number[] = [];
  for (let z = topZ - stepDown; z > bottomZ + 1e-9; z -= stepDown) levels.push(z);
  levels.push(bottomZ);
  return levels;
}

function movementForSegment<F extends FrameId>(
  segment: Segment2<F>,
  z: number,
  cuttingFeed: MillimetersPerMinute,
  meta: ReturnType<typeof operationMeta>,
): Instruction {
  if (segment.kind === "line") {
    return {
      kind: "linear",
      frame: "work",
      target: target({ x: segment.to.x as number, y: segment.to.y as number, z }),
      feed: cuttingFeed,
      engagement: "cut",
      meta,
    };
  }
  return {
    kind: "arc",
    frame: "work",
    plane: "XY",
    target: target({ x: segment.to.x as number, y: segment.to.y as number, z }),
    centerOffset: target({
      x: (segment.center.x as number) - (segment.from.x as number),
      y: (segment.center.y as number) - (segment.from.y as number),
    }),
    direction: segment.direction,
    feed: cuttingFeed,
    engagement: "cut",
    meta,
  };
}

function startAtPath<F extends FrameId>(
  path: Path2<F>,
  z: number,
  safeZ: number,
  plungeFeed: MillimetersPerMinute,
  meta: ReturnType<typeof operationMeta>,
): Instruction[] {
  return [
    { kind: "rapid", frame: "work", target: target({ z: safeZ }), meta },
    {
      kind: "rapid",
      frame: "work",
      target: target({ x: path.start.x as number, y: path.start.y as number }),
      meta,
    },
    {
      kind: "linear",
      frame: "work",
      target: target({ x: path.start.x as number, y: path.start.y as number, z }),
      feed: plungeFeed,
      engagement: "cut",
      meta,
    },
  ];
}

export const contour = <const Id extends number, F extends FrameId>(
  tool: ToolDefinition<Id>,
  toolCenterPath: Path2<F>,
  params: CuttingParameters & OperationOptions,
): Program<Ready<Loaded<Id>, "on">, Ready<Loaded<Id>, "on">, "motion"> => {
  const meta = operationMeta(params, params.label ?? "contour");
  const cuttingFeed = feed(params.feed);
  const plunge = feed(params.plungeFeed);
  const instructions: Instruction[] = [
    { kind: "comment", text: `BEGIN ${meta.operationLabel} (${meta.operationId})`, meta },
  ];
  for (const z of depthLevels(params.topZ, params.bottomZ, params.stepDown)) {
    instructions.push(...startAtPath(toolCenterPath, z, params.safeZ, plunge, meta));
    for (const segment of toolCenterPath.segments) {
      instructions.push(movementForSegment(segment, z, cuttingFeed, meta));
    }
    instructions.push({ kind: "rapid", frame: "work", target: target({ z: params.safeZ }), meta });
  }
  instructions.push({ kind: "comment", text: `END ${meta.operationLabel}`, meta });
  return primitive(instructions.map((instruction) => ({
    ...instruction,
    meta: { ...instruction.meta, notes: [...(instruction.meta?.notes ?? []), `tool T${tool.id}`] },
  })));
};

export const engrave = <const Id extends number, F extends FrameId>(
  tool: ToolDefinition<Id>,
  path: Path2<F>,
  params: Omit<CuttingParameters, "stepDown" | "topZ"> & { readonly depth: number } & OperationOptions,
): Program<Ready<Loaded<Id>, "on">, Ready<Loaded<Id>, "on">, "motion"> =>
  contour(tool, path, {
    topZ: 0,
    bottomZ: params.depth,
    stepDown: Math.abs(params.depth) + 1,
    safeZ: params.safeZ,
    feed: params.feed,
    plungeFeed: params.plungeFeed,
    ...(params.id === undefined ? {} : { id: params.id }),
    ...(params.label === undefined ? {} : { label: params.label }),
  });

export interface RasterPocketParameters extends CuttingParameters, OperationOptions {
  readonly stepover: number;
}

function rasterRows<F extends FrameId>(bounds: Box2<F>, toolRadius: number, stepover: number) {
  if (!(stepover > 0)) throw new RangeError("stepover must be positive");
  const x0 = (bounds.min.x as number) + toolRadius;
  const x1 = (bounds.max.x as number) - toolRadius;
  const y0 = (bounds.min.y as number) + toolRadius;
  const y1 = (bounds.max.y as number) - toolRadius;
  if (!(x0 < x1 && y0 <= y1)) throw new RangeError("Tool does not fit inside the rectangular region");
  const count = Math.max(1, Math.ceil((y1 - y0) / stepover));
  const actual = count === 0 ? 0 : (y1 - y0) / count;
  return { x0, x1, y0, y1, count, actual };
}

export const pocketRectangle = <const Id extends number, F extends FrameId>(
  tool: ToolDefinition<Id>,
  bounds: Box2<F>,
  params: RasterPocketParameters,
): Program<Ready<Loaded<Id>, "on">, Ready<Loaded<Id>, "on">, "motion"> => {
  const meta = operationMeta(params, params.label ?? "rectangular pocket");
  const cuttingFeed = feed(params.feed);
  const plunge = feed(params.plungeFeed);
  const radius = (tool.diameter as number) / 2;
  const rows = rasterRows(bounds, radius, params.stepover);
  const instructions: Instruction[] = [
    { kind: "comment", text: `BEGIN ${meta.operationLabel} (${meta.operationId})`, meta },
  ];

  for (const z of depthLevels(params.topZ, params.bottomZ, params.stepDown)) {
    const start = point2(bounds.frame, rows.x0, rows.y0);
    instructions.push(
      { kind: "rapid", frame: "work", target: target({ z: params.safeZ }), meta },
      { kind: "rapid", frame: "work", target: target({ x: start.x as number, y: start.y as number }), meta },
      {
        kind: "linear",
        frame: "work",
        target: target({ x: start.x as number, y: start.y as number, z }),
        feed: plunge,
        engagement: "cut",
        meta,
      },
    );
    for (let row = 0; row <= rows.count; row++) {
      const y = row === rows.count ? rows.y1 : rows.y0 + row * rows.actual;
      const xEnd = row % 2 === 0 ? rows.x1 : rows.x0;
      instructions.push({
        kind: "linear",
        frame: "work",
        target: target({ x: xEnd, y, z }),
        feed: cuttingFeed,
        engagement: "cut",
        meta,
      });
      if (row < rows.count) {
        const nextY = row + 1 === rows.count ? rows.y1 : rows.y0 + (row + 1) * rows.actual;
        instructions.push({
          kind: "linear",
          frame: "work",
          target: target({ x: xEnd, y: nextY, z }),
          feed: cuttingFeed,
          engagement: "cut",
          meta,
        });
      }
    }
    instructions.push({ kind: "rapid", frame: "work", target: target({ z: params.safeZ }), meta });
  }
  instructions.push({ kind: "comment", text: `END ${meta.operationLabel}`, meta });
  return primitive(instructions.map((instruction) => ({
    ...instruction,
    meta: { ...instruction.meta, notes: [...(instruction.meta?.notes ?? []), `tool T${tool.id}`] },
  })));
};

/** Facing is the same raster algebra with a shallow target depth. */
export const faceRectangle = pocketRectangle;

export interface CircularPocketParameters extends CuttingParameters, OperationOptions {
  readonly centerX: number;
  readonly centerY: number;
  readonly radius: number;
  readonly stepover: number;
}

export const pocketCircle = <const Id extends number>(
  tool: ToolDefinition<Id>,
  params: CircularPocketParameters,
): Program<Ready<Loaded<Id>, "on">, Ready<Loaded<Id>, "on">, "motion"> => {
  const meta = operationMeta(params, params.label ?? "circular pocket");
  const cuttingFeed = feed(params.feed);
  const plunge = feed(params.plungeFeed);
  const maxCenterRadius = params.radius - (tool.diameter as number) / 2;
  if (!(maxCenterRadius >= 0)) throw new RangeError("Tool does not fit inside circular pocket");
  if (!(params.stepover > 0)) throw new RangeError("stepover must be positive");
  const rings = Math.max(1, Math.ceil(maxCenterRadius / params.stepover));
  const radialStep = maxCenterRadius / rings;
  const instructions: Instruction[] = [
    { kind: "comment", text: `BEGIN ${meta.operationLabel} (${meta.operationId})`, meta },
  ];

  for (const z of depthLevels(params.topZ, params.bottomZ, params.stepDown)) {
    instructions.push(
      { kind: "rapid", frame: "work", target: target({ z: params.safeZ }), meta },
      { kind: "rapid", frame: "work", target: target({ x: params.centerX, y: params.centerY }), meta },
      {
        kind: "linear",
        frame: "work",
        target: target({ x: params.centerX, y: params.centerY, z }),
        feed: plunge,
        engagement: "cut",
        meta,
      },
    );
    for (let ring = 1; ring <= rings; ring++) {
      const r = ring * radialStep;
      instructions.push({
        kind: "linear",
        frame: "work",
        target: target({ x: params.centerX + r, y: params.centerY, z }),
        feed: cuttingFeed,
        engagement: "cut",
        meta,
      });
      instructions.push({
        kind: "arc",
        frame: "work",
        plane: "XY",
        target: target({ x: params.centerX - r, y: params.centerY, z }),
        centerOffset: target({ x: -r, y: 0 }),
        direction: "ccw",
        feed: cuttingFeed,
        engagement: "cut",
        meta,
      });
      instructions.push({
        kind: "arc",
        frame: "work",
        plane: "XY",
        target: target({ x: params.centerX + r, y: params.centerY, z }),
        centerOffset: target({ x: r, y: 0 }),
        direction: "ccw",
        feed: cuttingFeed,
        engagement: "cut",
        meta,
      });
    }
    instructions.push({ kind: "rapid", frame: "work", target: target({ z: params.safeZ }), meta });
  }
  instructions.push({ kind: "comment", text: `END ${meta.operationLabel}`, meta });
  return primitive(instructions.map((instruction) => ({
    ...instruction,
    meta: { ...instruction.meta, notes: [...(instruction.meta?.notes ?? []), `tool T${tool.id}`] },
  })));
};

export interface DrillParameters extends OperationOptions {
  readonly points: readonly { readonly x: number; readonly y: number }[];
  readonly topZ: number;
  readonly bottomZ: number;
  readonly safeZ: number;
  readonly feed: number | MillimetersPerMinute;
  readonly dwellSeconds?: number;
  readonly peck?: number;
}

export const drill = <const Id extends number>(
  tool: ToolDefinition<Id>,
  params: DrillParameters,
): Program<Ready<Loaded<Id>, "on">, Ready<Loaded<Id>, "on">, "motion"> => {
  if (!(params.bottomZ < params.topZ)) throw new RangeError("Drill bottomZ must be below topZ");
  const meta = operationMeta(params, params.label ?? "drill");
  const plunge = feed(params.feed);
  const instructions: Instruction[] = [
    { kind: "comment", text: `BEGIN ${meta.operationLabel} (${meta.operationId})`, meta },
  ];
  for (const p of params.points) {
    instructions.push(
      { kind: "rapid", frame: "work", target: target({ z: params.safeZ }), meta },
      { kind: "rapid", frame: "work", target: target({ x: p.x, y: p.y }), meta },
    );
    if (params.peck && params.peck > 0) {
      for (let z = params.topZ - params.peck; z > params.bottomZ + 1e-9; z -= params.peck) {
        instructions.push(
          { kind: "linear", frame: "work", target: target({ x: p.x, y: p.y, z }), feed: plunge, engagement: "cut", meta },
          { kind: "rapid", frame: "work", target: target({ z: params.topZ + 0.5 }), meta },
        );
      }
    }
    instructions.push({
      kind: "linear",
      frame: "work",
      target: target({ x: p.x, y: p.y, z: params.bottomZ }),
      feed: plunge,
      engagement: "cut",
      meta,
    });
    if (params.dwellSeconds && params.dwellSeconds > 0) {
      instructions.push({ kind: "dwell", duration: seconds(params.dwellSeconds), meta });
    }
    instructions.push({ kind: "rapid", frame: "work", target: target({ z: params.safeZ }), meta });
  }
  instructions.push({ kind: "comment", text: `END ${meta.operationLabel}`, meta });
  return primitive(instructions.map((instruction) => ({
    ...instruction,
    meta: { ...instruction.meta, notes: [...(instruction.meta?.notes ?? []), `tool T${tool.id}`] },
  })));
};
EOF
cat > "$ROOT/src/profile.ts" <<'EOF'
import type { Box3 } from "./math.js";
import type { Plane } from "./ir.js";
import type { Millimeters, MillimetersPerMinute, RevolutionsPerMinute } from "./units.js";

export interface MachineCapabilities {
  readonly arcs: readonly Plane[];
  readonly probing: boolean;
  readonly coolant: readonly ("flood" | "mist")[];
  readonly toolChange: boolean;
  readonly home: boolean;
}

export interface MachineProfile {
  readonly name: string;
  readonly workEnvelope: Box3;
  readonly machineEnvelope: Box3<"machine">;
  readonly clearanceZ: Millimeters;
  readonly safeMachineZ: Millimeters;
  readonly maxFeed: MillimetersPerMinute;
  readonly maxRapid: MillimetersPerMinute;
  readonly maxSpindle: RevolutionsPerMinute;
  readonly rapidKinematics: "coordinated" | "dogleg-or-unknown";
  readonly capabilities: MachineCapabilities;
  readonly arcTolerance: Millimeters;
}
EOF
cat > "$ROOT/src/semantics.ts" <<'EOF'
import { point3, type AxisTarget, type FrameId, type Point3 } from "./math.js";
import type {
  ArcInstruction,
  AxisState,
  CanonicalProgram,
  Instruction,
  MachineState,
  Trajectory,
} from "./ir.js";
import type { MachineProfile } from "./profile.js";
import { mm, type Millimeters } from "./units.js";

export interface RuntimeDiagnostic {
  readonly severity: "error" | "warning";
  readonly code: string;
  readonly message: string;
  readonly instructionIndex: number;
}

export interface TraceStep {
  readonly instructionIndex: number;
  readonly instruction: Instruction;
  readonly before: MachineState;
  readonly after: MachineState;
  readonly trajectory?: Trajectory;
}

export interface ExecutionTrace {
  readonly initial: MachineState;
  readonly final: MachineState;
  readonly steps: readonly TraceStep[];
  readonly diagnostics: readonly RuntimeDiagnostic[];
  readonly estimatedSeconds: number;
  readonly pathLengthMm: number;
}

export const initialMachineState = (): MachineState => ({
  units: "mm",
  distance: "absolute",
  feedMode: "per-minute",
  plane: "XY",
  spindle: { mode: "off" },
  coolant: "off",
  workPosition: {},
  machinePosition: {},
  ended: false,
});

function mergeAxis(state: AxisState, target: AxisTarget): AxisState {
  return {
    ...(state.x === undefined ? {} : { x: state.x }),
    ...(state.y === undefined ? {} : { y: state.y }),
    ...(state.z === undefined ? {} : { z: state.z }),
    ...(target.x === undefined ? {} : { x: target.x }),
    ...(target.y === undefined ? {} : { y: target.y }),
    ...(target.z === undefined ? {} : { z: target.z }),
  };
}

function axisDistance(a: AxisState, b: AxisState): number | undefined {
  if (a.x === undefined || a.y === undefined || a.z === undefined || b.x === undefined || b.y === undefined || b.z === undefined) {
    return undefined;
  }
  return Math.hypot(
    (b.x as number) - (a.x as number),
    (b.y as number) - (a.y as number),
    (b.z as number) - (a.z as number),
  );
}

function fullPoint(frame: FrameId, axis: AxisState): Point3<FrameId> | undefined {
  if (axis.x === undefined || axis.y === undefined || axis.z === undefined) return undefined;
  return point3(frame, axis.x as number, axis.y as number, axis.z as number);
}

function arcCenter(start: Point3<FrameId>, arc: ArcInstruction): Point3<FrameId> {
  return point3(
    start.frame,
    (start.x as number) + ((arc.centerOffset.x ?? mm(0)) as number),
    (start.y as number) + ((arc.centerOffset.y ?? mm(0)) as number),
    (start.z as number) + ((arc.centerOffset.z ?? mm(0)) as number),
  );
}

function arcLength(start: Point3<FrameId>, end: Point3<FrameId>, center: Point3<FrameId>, arc: ArcInstruction): number {
  const uv = (p: Point3<FrameId>): readonly [number, number] => {
    if (arc.plane === "XY") return [(p.x as number), (p.y as number)];
    if (arc.plane === "XZ") return [(p.x as number), (p.z as number)];
    return [(p.y as number), (p.z as number)];
  };
  const [su, sv] = uv(start);
  const [eu, ev] = uv(end);
  const [cu, cv] = uv(center);
  const radius = Math.hypot(su - cu, sv - cv);
  let sweep = Math.atan2(ev - cv, eu - cu) - Math.atan2(sv - cv, su - cu);
  if (arc.direction === "ccw") while (sweep <= 0) sweep += Math.PI * 2;
  else while (sweep >= 0) sweep -= Math.PI * 2;
  const helicalAxis = arc.plane === "XY" ? "z" : arc.plane === "XZ" ? "y" : "x";
  const deltaHelix = ((end[helicalAxis] as number) - (start[helicalAxis] as number));
  return Math.hypot(Math.abs(sweep) * radius, deltaHelix);
}

function copyState(state: MachineState, patch: Partial<MachineState>): MachineState {
  return { ...state, ...patch };
}

/** One operational small-step transition. */
export function stepInstruction(
  state: MachineState,
  instruction: Instruction,
  profile: MachineProfile,
): { readonly state: MachineState; readonly trajectory?: Trajectory; readonly seconds: number; readonly length: number } {
  switch (instruction.kind) {
    case "set-modes":
      return { state: copyState(state, { plane: instruction.plane }), seconds: 0, length: 0 };
    case "select-work-offset":
      return { state: copyState(state, { workOffset: instruction.index }), seconds: 0, length: 0 };
    case "comment":
    case "pause":
    case "home":
      return { state, seconds: 0, length: 0 };
    case "tool-change":
      return { state: copyState(state, { tool: instruction.tool }), seconds: 0, length: 0 };
    case "spindle":
      return {
        state: copyState(state, {
          spindle: instruction.mode === "off"
            ? { mode: "off" }
            : { mode: instruction.mode, ...(instruction.speed === undefined ? {} : { speed: instruction.speed }) },
        }),
        seconds: 0,
        length: 0,
      };
    case "coolant":
      return { state: copyState(state, { coolant: instruction.mode }), seconds: 0, length: 0 };
    case "dwell":
      return { state, seconds: instruction.duration as number, length: 0 };
    case "rapid": {
      const before = instruction.frame === "work" ? state.workPosition : state.machinePosition;
      const after = mergeAxis(before, instruction.target);
      const d = axisDistance(before, after) ?? 0;
      const trajectory: Trajectory = {
        kind: "line",
        frame: instruction.frame,
        start: before,
        end: after,
        rapid: true,
      };
      const next = instruction.frame === "work"
        ? copyState(state, { workPosition: after })
        : copyState(state, { machinePosition: after });
      return { state: next, trajectory, seconds: d / ((profile.maxRapid as number) / 60), length: d };
    }
    case "linear":
    case "probe": {
      const before = state.workPosition;
      const after = mergeAxis(before, instruction.target);
      const d = axisDistance(before, after) ?? 0;
      const trajectory: Trajectory = {
        kind: "line",
        frame: "work",
        start: before,
        end: after,
        feed: instruction.feed,
        rapid: false,
      };
      return {
        state: copyState(state, { workPosition: after }),
        trajectory,
        seconds: d / ((instruction.feed as number) / 60),
        length: d,
      };
    }
    case "arc": {
      const start = fullPoint(`G${53 + (state.workOffset ?? 1)}` as FrameId, state.workPosition);
      const merged = mergeAxis(state.workPosition, instruction.target);
      const end = fullPoint(start?.frame ?? "G54", merged);
      if (!start || !end) {
        return { state: copyState(state, { workPosition: merged }), seconds: 0, length: 0 };
      }
      const center = arcCenter(start, instruction);
      const d = arcLength(start, end, center, instruction);
      return {
        state: copyState(state, { workPosition: merged, plane: instruction.plane }),
        trajectory: {
          kind: "arc",
          frame: "work",
          plane: instruction.plane,
          start,
          end,
          center,
          direction: instruction.direction,
          feed: instruction.feed,
        },
        seconds: d / ((instruction.feed as number) / 60),
        length: d,
      };
    }
    case "end":
      return { state: copyState(state, { ended: true }), seconds: 0, length: 0 };
  }
}

/**
 * Denotation into partial state transformers with an execution trace.
 * The validator supplies the error relation; this interpreter remains deterministic.
 */
export function interpretProgram(
  program: CanonicalProgram,
  profile: MachineProfile,
  initial: MachineState = initialMachineState(),
): ExecutionTrace {
  let state = initial;
  let elapsed = 0;
  let pathLength = 0;
  const steps: TraceStep[] = [];
  const diagnostics: RuntimeDiagnostic[] = [];
  program.instructions.forEach((instruction, instructionIndex) => {
    const before = state;
    const result = stepInstruction(state, instruction, profile);
    state = result.state;
    elapsed += result.seconds;
    pathLength += result.length;
    steps.push({
      instructionIndex,
      instruction,
      before,
      after: state,
      ...(result.trajectory === undefined ? {} : { trajectory: result.trajectory }),
    });
  });
  return {
    initial,
    final: state,
    steps,
    diagnostics,
    estimatedSeconds: elapsed,
    pathLengthMm: pathLength,
  };
}
EOF

```

<details><summary>💭 Thinking</summary>

**Built and validated CNC CAM IR prototype project files**

</details>

```unknown
bash -lc set -euo pipefail
ROOT=/mnt/data/cnc-cam-ir
cat > "$ROOT/examples/badge-program.ts" <<'EOF'
import {
  assertValid,
  bootstrap,
  box2,
  box3,
  changeTool,
  compileGCode,
  coolantOff,
  coolantOn,
  defineTool,
  finish,
  interpretProgram,
  mm,
  mmPerMin,
  rpm,
  roundedRectangle,
  spindleOff,
  spindleOn,
  type MachineProfile,
} from "../src/index.js";
import { faceRectangle, pocketCircle, contour } from "../src/milling.js";

export const profile: MachineProfile = {
  name: "Reference 3-axis mill",
  workEnvelope: box3("G54", -150, -100, -25, 150, 100, 60),
  machineEnvelope: box3("machine", -10, -10, -120, 320, 220, 0),
  clearanceZ: mm(3),
  safeMachineZ: mm(-5),
  maxFeed: mmPerMin(3000),
  maxRapid: mmPerMin(5000),
  maxSpindle: rpm(24000),
  rapidKinematics: "dogleg-or-unknown",
  capabilities: {
    arcs: ["XY", "XZ", "YZ"],
    probing: true,
    coolant: ["flood"],
    toolChange: true,
    home: true,
  },
  arcTolerance: mm(0.01),
};

export const tool1 = defineTool(1, {
  kind: "flat-end",
  diameter: 3,
  fluteLength: mm(12),
  description: "3 mm carbide flat end mill",
});

// The nominal badge is 40 x 30 mm with R3 corners. This is the outside
// tool-center path, offset by the 1.5 mm tool radius.
export const outsideToolCenter = roundedRectangle("G54", {
  centerX: 0,
  centerY: 0,
  width: 43,
  height: 33,
  radius: 4.5,
});

export const badgeProgram = bootstrap({
  name: "Compositional badge example",
  workOffset: 1,
  safeMachineZ: -5,
  comment: "Typed CAM IR example: face, circular pocket, outside contour",
})
  .then(changeTool(tool1))
  .then(spindleOn(tool1, 12_000))
  .then(coolantOn(tool1, "on", "flood"))
  .then(faceRectangle(tool1, box2("G54", -24, -19, 24, 19), {
    id: "face-top",
    label: "face stock top",
    topZ: 0.2,
    bottomZ: -0.2,
    stepDown: 0.4,
    safeZ: 5,
    stepover: 1.8,
    feed: 900,
    plungeFeed: 250,
  }))
  .then(pocketCircle(tool1, {
    id: "center-pocket",
    label: "center circular pocket",
    centerX: 0,
    centerY: 0,
    radius: 5,
    topZ: -0.2,
    bottomZ: -1.5,
    stepDown: 0.65,
    safeZ: 5,
    stepover: 1.2,
    feed: 650,
    plungeFeed: 180,
  }))
  .then(contour(tool1, outsideToolCenter, {
    id: "outside-profile",
    label: "outside profile",
    topZ: -0.2,
    bottomZ: -2,
    stepDown: 0.9,
    safeZ: 5,
    feed: 700,
    plungeFeed: 180,
  }))
  .then(coolantOff(tool1, "on"))
  .then(spindleOff(tool1))
  .then(finish({ safeMachineZ: -5, home: true, rewind: true }));

export const validatedBadge = assertValid(badgeProgram, profile);
export const badgeGCode = compileGCode(validatedBadge);
export const badgeTrace = interpretProgram(validatedBadge, profile);
EOF
cat > "$ROOT/examples/badge.ts" <<'EOF'
import { badgeGCode, badgeTrace, validatedBadge } from "./badge-program.js";

console.log(`Program: ${validatedBadge.name}`);
console.log(`IR instructions: ${validatedBadge.instructions.length}`);
console.log(`Path length: ${badgeTrace.pathLengthMm.toFixed(1)} mm`);
console.log(`Idealized time: ${(badgeTrace.estimatedSeconds / 60).toFixed(2)} min`);
console.log(`G-code lines: ${badgeGCode.lines.length}`);
console.log("--- G-CODE ---");
console.log(badgeGCode.text);
EOF
cat > "$ROOT/type-tests/typestate.ts" <<'EOF'
import {
  bootstrap,
  box3,
  changeTool,
  compileGCode,
  defineTool,
  finish,
  mm,
  mmPerMin,
  rpm,
  roundedRectangle,
  spindleOff,
  spindleOn,
  type MachineProfile,
} from "../src/index.js";
import { contour } from "../src/milling.js";

const profile: MachineProfile = {
  name: "type-test",
  workEnvelope: box3("G54", -50, -50, -20, 50, 50, 20),
  machineEnvelope: box3("machine", 0, 0, -100, 100, 100, 0),
  clearanceZ: mm(3),
  safeMachineZ: mm(-5),
  maxFeed: mmPerMin(2000),
  maxRapid: mmPerMin(5000),
  maxSpindle: rpm(24000),
  rapidKinematics: "dogleg-or-unknown",
  capabilities: { arcs: ["XY"], probing: false, coolant: [], toolChange: true, home: true },
  arcTolerance: mm(0.01),
};
void profile;

const t1 = defineTool(1, { kind: "flat-end", diameter: 3 });
const t2 = defineTool(2, { kind: "ball-nose", diameter: 3 });
const path = roundedRectangle("G54", { centerX: 0, centerY: 0, width: 10, height: 8, radius: 1 });
const cut1 = contour(t1, path, { topZ: 0, bottomZ: -1, stepDown: 1, safeZ: 5, feed: 500, plungeFeed: 100 });
const cut2 = contour(t2, path, { topZ: 0, bottomZ: -1, stepDown: 1, safeZ: 5, feed: 500, plungeFeed: 100 });

const loadedButStopped = bootstrap({ name: "bad", safeMachineZ: -5 }).then(changeTool(t1));
// @ts-expect-error Cutting cannot compose while the spindle typestate is off.
loadedButStopped.then(cut1);

const spinningT1 = loadedButStopped.then(spindleOn(t1, 10_000));
// @ts-expect-error A T2 operation cannot compose with the T1-loaded typestate.
spinningT1.then(cut2);

const complete = spinningT1
  .then(cut1)
  .then(spindleOff(t1))
  .then(finish({ safeMachineZ: -5 }));
// @ts-expect-error The G-code compiler accepts only a runtime-validated witness.
compileGCode(complete);
EOF
cat > "$ROOT/test/ir.test.mjs" <<'EOF'
import test from "node:test";
import assert from "node:assert/strict";

import {
  assertValid,
  canonicalize,
  compileGCode,
  compileInstructions,
  initialMachineState,
  interpretProgram,
  mm,
  mmPerMin,
  rpm,
  target,
  unsafeProgram,
  validateProgram,
  box3,
} from "../dist/src/index.js";
import { badgeGCode, badgeProgram, badgeTrace, profile, validatedBadge } from "../dist/examples/badge-program.js";

function minimalProfile(overrides = {}) {
  return {
    name: "test mill",
    workEnvelope: box3("G54", -100, -100, -20, 100, 100, 50),
    machineEnvelope: box3("machine", -10, -10, -100, 200, 200, 0),
    clearanceZ: mm(3),
    safeMachineZ: mm(-5),
    maxFeed: mmPerMin(2000),
    maxRapid: mmPerMin(5000),
    maxSpindle: rpm(24000),
    rapidKinematics: "dogleg-or-unknown",
    capabilities: { arcs: ["XY", "XZ", "YZ"], probing: true, coolant: ["flood"], toolChange: true, home: true },
    arcTolerance: mm(0.01),
    ...overrides,
  };
}

test("badge example validates and compiles to a conservative skeleton", () => {
  assert.equal(validatedBadge.version, "cnc-ir/0.1");
  assert.ok(badgeTrace.pathLengthMm > 1000);
  assert.match(badgeGCode.text, /G21 G90 G94 G17/);
  assert.match(badgeGCode.text, /G53 G0 Z-5\.000/);
  assert.match(badgeGCode.text, /T1 M6/);
  assert.match(badgeGCode.text, /S12000 M3/);
  assert.match(badgeGCode.text, /G3 /);
  assert.match(badgeGCode.text, /M5/);
  assert.match(badgeGCode.text, /G28/);
  assert.match(badgeGCode.text, /M30/);
});

test("runtime validator rejects cutting without tool and spindle", () => {
  const program = unsafeProgram("unsafe cut", [
    { kind: "set-modes", units: "mm", distance: "absolute", feedMode: "per-minute", plane: "XY" },
    { kind: "select-work-offset", index: 1 },
    { kind: "rapid", frame: "machine", target: target({ z: -5 }) },
    { kind: "rapid", frame: "work", target: target({ z: 5 }) },
    { kind: "rapid", frame: "work", target: target({ x: 0, y: 0 }) },
    { kind: "linear", frame: "work", target: target({ z: -1 }), feed: mmPerMin(100), engagement: "cut" },
    { kind: "rapid", frame: "machine", target: target({ z: -5 }) },
    { kind: "end", rewind: true },
  ]);
  const result = validateProgram(program, minimalProfile());
  assert.equal(result.ok, false);
  const codes = new Set(result.diagnostics.map((d) => d.code));
  assert.ok(codes.has("E_CUT_NO_TOOL"));
  assert.ok(codes.has("E_CUT_SPINDLE_OFF"));
});

test("runtime validator rejects a combined dogleg rapid below clearance", () => {
  const program = unsafeProgram("dogleg", [
    { kind: "set-modes", units: "mm", distance: "absolute", feedMode: "per-minute", plane: "XY" },
    { kind: "select-work-offset", index: 1 },
    { kind: "rapid", frame: "machine", target: target({ z: -5 }) },
    { kind: "rapid", frame: "work", target: target({ z: 5 }) },
    { kind: "rapid", frame: "work", target: target({ x: 0, y: 0 }) },
    { kind: "linear", frame: "work", target: target({ z: -1 }), feed: mmPerMin(100), engagement: "air" },
    { kind: "rapid", frame: "work", target: target({ x: 20, z: 5 }) },
    { kind: "rapid", frame: "machine", target: target({ z: -5 }) },
    { kind: "end", rewind: true },
  ]);
  const result = validateProgram(program, minimalProfile());
  const codes = new Set(result.diagnostics.map((d) => d.code));
  assert.ok(codes.has("E_RAPID_LATERAL_CLEARANCE"));
  assert.ok(codes.has("E_DOGLEG_RAPID"));
});

test("runtime validator rejects inconsistent center-form arcs", () => {
  const program = unsafeProgram("bad arc", [
    { kind: "set-modes", units: "mm", distance: "absolute", feedMode: "per-minute", plane: "XY" },
    { kind: "select-work-offset", index: 1 },
    { kind: "rapid", frame: "machine", target: target({ z: -5 }) },
    { kind: "tool-change", tool: { id: 1, kind: "flat-end", diameter: mm(3) } },
    { kind: "spindle", mode: "cw", speed: rpm(10000) },
    { kind: "rapid", frame: "work", target: target({ z: 5 }) },
    { kind: "rapid", frame: "work", target: target({ x: 0, y: 0 }) },
    { kind: "linear", frame: "work", target: target({ z: 0 }), feed: mmPerMin(100), engagement: "cut" },
    { kind: "arc", frame: "work", plane: "XY", target: target({ x: 10, y: 0, z: 0 }), centerOffset: target({ x: 1, y: 0 }), direction: "ccw", feed: mmPerMin(500), engagement: "cut" },
    { kind: "rapid", frame: "work", target: target({ z: 5 }) },
    { kind: "spindle", mode: "off" },
    { kind: "rapid", frame: "machine", target: target({ z: -5 }) },
    { kind: "end", rewind: true },
  ]);
  const result = validateProgram(program, minimalProfile());
  assert.ok(result.diagnostics.some((d) => d.code === "E_ARC_RADIUS_MISMATCH"));
});

test("denotation preserves sequential composition", () => {
  const canonical = canonicalize(badgeProgram);
  const split = Math.floor(canonical.instructions.length / 2);
  const first = { ...canonical, name: "first", instructions: canonical.instructions.slice(0, split) };
  const second = { ...canonical, name: "second", instructions: canonical.instructions.slice(split) };
  const whole = interpretProgram(canonical, profile, initialMachineState());
  const left = interpretProgram(first, profile, initialMachineState());
  const right = interpretProgram(second, profile, left.final);
  assert.deepEqual(right.final, whole.final);
  assert.ok(Math.abs(left.pathLengthMm + right.pathLengthMm - whole.pathLengthMm) < 1e-9);
  assert.ok(Math.abs(left.estimatedSeconds + right.estimatedSeconds - whole.estimatedSeconds) < 1e-9);
});

test("state-threaded postprocessor preserves composition", () => {
  const instructions = validatedBadge.instructions;
  const split = Math.floor(instructions.length / 2);
  const whole = compileInstructions(instructions);
  const first = compileInstructions(instructions.slice(0, split));
  const second = compileInstructions(instructions.slice(split), undefined, first.state);
  assert.deepEqual([...first.lines, ...second.lines], whole.lines);
  assert.deepEqual(second.state, whole.state);
});

test("compiler requires a validation witness at runtime API boundary", () => {
  assert.throws(() => assertValid(unsafeProgram("empty", []), minimalProfile()), /validation failed/i);
  assert.equal(compileGCode(validatedBadge).text, badgeGCode.text);
});
EOF
cd "$ROOT"
npm run build
npm test

```

<details><summary>💭 Thinking</summary>

**Created CNC CAM examples, tests, G-code artifacts, and tooling**

</details>

```unknown
bash -lc set -euo pipefail
ROOT=/mnt/data/cnc-cam-ir
cat > "$ROOT/examples/probe-program.ts" <<'EOF'
import {
  assertValid,
  bootstrap,
  box3,
  changeTool,
  compileGCode,
  defineTool,
  finish,
  mm,
  mmPerMin,
  probe,
  rapid,
  rpm,
  type MachineProfile,
} from "../src/index.js";

export const probingProfile: MachineProfile = {
  name: "Reference probe-capable mill",
  workEnvelope: box3("G54", -100, -100, -30, 100, 100, 50),
  machineEnvelope: box3("machine", -10, -10, -100, 250, 180, 0),
  clearanceZ: mm(3),
  safeMachineZ: mm(-5),
  maxFeed: mmPerMin(2000),
  maxRapid: mmPerMin(5000),
  maxSpindle: rpm(24000),
  rapidKinematics: "dogleg-or-unknown",
  capabilities: {
    arcs: ["XY"],
    probing: true,
    coolant: [],
    toolChange: true,
    home: true,
  },
  arcTolerance: mm(0.01),
};

export const probeTool = defineTool(99, {
  kind: "custom",
  diameter: 4,
  description: "Touch probe stylus",
});

export const probeProgram = bootstrap({
  name: "Two-pass Z probing skeleton",
  safeMachineZ: -5,
  workOffset: 1,
})
  .then(changeTool(probeTool))
  .then(rapid(probeTool, "off", "work", { z: 8 }))
  .then(rapid(probeTool, "off", "work", { x: 0, y: 0 }))
  .then(probe(probeTool, { target: { z: -10 }, feed: 200, errorOnMiss: true, label: "fast contact" }))
  .then(rapid(probeTool, "off", "work", { z: 3 }))
  .then(probe(probeTool, { target: { z: -2 }, feed: 40, errorOnMiss: true, label: "slow contact" }))
  .then(finish({ safeMachineZ: -5, home: false }));

export const validatedProbeProgram = assertValid(probeProgram, probingProfile);
export const probeGCode = compileGCode(validatedProbeProgram);
EOF
cat > "$ROOT/examples/probe.ts" <<'EOF'
import { probeGCode } from "./probe-program.js";
console.log(probeGCode.text);
EOF
cat >> "$ROOT/test/ir.test.mjs" <<'EOF'

test("probing action lowers to fail-on-miss G38.2", async () => {
  const { probeGCode } = await import("../dist/examples/probe-program.js");
  const matches = probeGCode.text.match(/G38\.2/g) ?? [];
  assert.equal(matches.length, 2);
  assert.doesNotMatch(probeGCode.text, /G38\.3/);
});
EOF
cat > "$ROOT/README.md" <<'EOF'
# Compositional CNC CAM IR prototype

This package is a dependency-free TypeScript/JavaScript prototype for describing milling geometry, manufacturing intent, explicit machine motion, and controller output without making G-code the source language.

The safety boundary is deliberate:

1. Geometry is represented as exact line/center-form arc paths in named frames.
2. Manufacturing intent (`contour`, rectangular/circular pockets, facing, drilling) lowers to a canonical, non-modal motion IR.
3. Programs are indexed by typestate: tool identity and spindle state must match before fragments compose.
4. A machine-profile validator checks dynamic invariants and returns a `ValidatedProgram` witness.
5. Only a validated witness is accepted by the normal G-code compiler.
6. The same IR is interpreted for traces, time/path estimates, testing, serialization, and migration from the uploaded drop-cutter job format.

## Run

```bash
npm run build
npm test
npm run example
```

No npm dependencies are required; TypeScript 5.8+ and Node 20+ are sufficient.

## API sketch

```ts
const tool1 = defineTool(1, { kind: "flat-end", diameter: 3 });
const boundary = roundedRectangle("G54", {
  centerX: 0, centerY: 0, width: 43, height: 33, radius: 4.5,
});

const program = bootstrap({
  name: "badge",
  workOffset: 1,
  safeMachineZ: -5,
})
  .then(changeTool(tool1))
  .then(spindleOn(tool1, 12_000))
  .then(milling.contour(tool1, boundary, {
    topZ: 0,
    bottomZ: -2,
    stepDown: 1,
    safeZ: 5,
    feed: 700,
    plungeFeed: 180,
  }))
  .then(spindleOff(tool1))
  .then(finish({ safeMachineZ: -5, home: true }));

const checked = assertValid(program, machineProfile);
const gcode = compileGCode(checked);
```

## Package map

- `src/geometry.ts` - exact 2D lines/arcs, paths, regions, affine frame transforms.
- `src/intent.ts` - serializable manufacturing intent and its lowering interpreter.
- `src/program.ts` - indexed/free program category and machine-action combinators.
- `src/milling.ts` - reference 2.5D planners.
- `src/ir.ts` - canonical non-modal machine IR.
- `src/validate.ts` - machine-profile validation and proof witness.
- `src/semantics.ts` - operational small-step interpreter and trace denotation.
- `src/gcode.ts` - state-threaded modal postprocessor.
- `src/dropcut-adapter.ts` - migration adapter for `{kind, phase, pts, ops}` jobs.
- `schema/cnc-ir.schema.json` - JSON Schema for persisted canonical IR.
- `examples/` - badge and fail-on-miss probing programs.
- `type-tests/` - compile-time negative tests.
- `test/` - runtime, semantic-law, and compiler-law tests.

## Scope

The reference planners are intentionally small. Robust arbitrary offsets, booleans, rest machining, stock/fixture collision, cutter engagement, 5-axis kinematics, and controller-specific probing variables belong behind explicit geometry-kernel, stock-model, verifier, and postprocessor interfaces. The report in `docs/` specifies those extension points and the formal contracts they should satisfy.
EOF
python - <<'PY'
import json, pathlib
root=pathlib.Path('/mnt/data/cnc-cam-ir')
axis_target={
  "type":"object",
  "properties":{"x":{"type":"number"},"y":{"type":"number"},"z":{"type":"number"}},
  "minProperties":1,
  "additionalProperties":False,
}
meta={
  "type":"object",
  "properties":{
    "operationId":{"type":"string"},
    "operationLabel":{"type":"string"},
    "source":{"type":"string"},
    "notes":{"type":"array","items":{"type":"string"}},
  },
  "additionalProperties":False,
}
tool={
  "type":"object",
  "required":["id","kind","diameter"],
  "properties":{
    "id":{"type":"integer","minimum":0},
    "kind":{"enum":["flat-end","ball-nose","drill","v-bit","custom"]},
    "diameter":{"type":"number","exclusiveMinimum":0},
    "fluteLength":{"type":"number","exclusiveMinimum":0},
    "description":{"type":"string"},
  },
  "additionalProperties":False,
}
def inst(kind, required, props):
    return {
      "type":"object",
      "required":["kind",*required],
      "properties":{"kind":{"const":kind},"meta":{"$ref":"#/$defs/meta"},**props},
      "additionalProperties":False,
    }
plane={"enum":["XY","XZ","YZ"]}
feed={"type":"number","exclusiveMinimum":0}
instructions=[
 inst("set-modes",["units","distance","feedMode","plane"],{"units":{"const":"mm"},"distance":{"const":"absolute"},"feedMode":{"const":"per-minute"},"plane":plane}),
 inst("select-work-offset",["index"],{"index":{"type":"integer","minimum":1,"maximum":6}}),
 inst("comment",["text"],{"text":{"type":"string"}}),
 inst("tool-change",["tool"],{"tool":{"$ref":"#/$defs/tool"}}),
 inst("spindle",["mode"],{"mode":{"enum":["cw","ccw","off"]},"speed":{"type":"number","minimum":0}}),
 inst("coolant",["mode"],{"mode":{"enum":["flood","mist","off"]}}),
 inst("rapid",["frame","target"],{"frame":{"enum":["machine","work"]},"target":{"$ref":"#/$defs/axisTarget"}}),
 inst("linear",["frame","target","feed","engagement"],{"frame":{"const":"work"},"target":{"$ref":"#/$defs/axisTarget"},"feed":feed,"engagement":{"enum":["air","cut","probe"]}}),
 inst("arc",["frame","plane","target","centerOffset","direction","feed","engagement"],{"frame":{"const":"work"},"plane":plane,"target":{"$ref":"#/$defs/axisTarget"},"centerOffset":{"$ref":"#/$defs/axisTarget"},"direction":{"enum":["cw","ccw"]},"feed":feed,"engagement":{"enum":["air","cut","probe"]}}),
 inst("dwell",["duration"],{"duration":{"type":"number","minimum":0}}),
 inst("probe",["frame","target","feed","errorOnMiss","sense"],{"frame":{"const":"work"},"target":{"$ref":"#/$defs/axisTarget"},"feed":feed,"errorOnMiss":{"type":"boolean"},"sense":{"enum":["contact","loss"]}}),
 inst("pause",["optional"],{"optional":{"type":"boolean"},"message":{"type":"string"}}),
 inst("home",[],{"axes":{"type":"array","uniqueItems":True,"items":{"enum":["X","Y","Z"]}}}),
 inst("end",["rewind"],{"rewind":{"type":"boolean"}}),
]
schema={
 "$schema":"https://json-schema.org/draft/2020-12/schema",
 "$id":"https://example.invalid/cnc-ir/0.1/schema.json",
 "title":"Canonical CNC IR 0.1",
 "description":"Machine-independent, explicit, canonical mill program IR. Numeric motion values are mm, mm/min, rpm, and seconds.",
 "type":"object",
 "required":["version","name","instructions"],
 "properties":{
   "version":{"const":"cnc-ir/0.1"},
   "name":{"type":"string","minLength":1},
   "instructions":{"type":"array","items":{"$ref":"#/$defs/instruction"}},
 },
 "additionalProperties":False,
 "$defs":{
   "axisTarget":axis_target,
   "meta":meta,
   "tool":tool,
   "instruction":{"oneOf":instructions},
 },
}
(root/'schema/cnc-ir.schema.json').write_text(json.dumps(schema, indent=2)+"\n")
PY
cd "$ROOT"
npm test
node dist/examples/probe.js > artifacts/gcode/probe-example.nc
head -60 artifacts/gcode/probe-example.nc

```

The core is now a phase-indexed free-category Plan with canonical commands and operational semantics. Tests validate category laws, safety, arcs, probing dialects, and staged single-axis rapids.

<details><summary>💭 Thinking</summary>

**Created CNC/CAM documentation, screenshots, validation reports, and package inventory**

</details>

```unknown
bash -lc python - <<'PY'
p='/mnt/data/cnc-cam-ir/src/intent.ts'
s=open(p).read()
s=s.replace('  type RasterPocketParameters,\n', '  type RasterPocketParameters,\n  type OperationOptions,\n')
s=s.replace('readonly parameters: CuttingParameters;', 'readonly parameters: CuttingParameters & OperationOptions;')
s=s.replace('parameters: CuttingParameters,\n  ): ContourIntent', 'parameters: CuttingParameters & OperationOptions,\n  ): ContourIntent')
open(p,'w').write(s)
PY
cd /mnt/data/cnc-cam-ir && npm test >/tmp/cnc-tests.txt && tail -16 /tmp/cnc-tests.txt
```

<details><summary>💭 Thinking</summary>

**Updated intent types and wrote CNC CAM API design report**

</details>

```unknown
bash -lc set -euo pipefail
ROOT=/mnt/data/cnc-cam-ir
cat > "$ROOT/docs/report.css" <<'EOF'
@page {
  size: A4;
  margin: 18mm 17mm 19mm 17mm;
  @bottom-center {
    content: counter(page);
    font-family: "DejaVu Sans", sans-serif;
    font-size: 8.5pt;
    color: #667085;
  }
}

:root {
  --ink: #17212b;
  --muted: #52606d;
  --line: #d7dee5;
  --soft: #f5f7f9;
  --blue: #1663a5;
  --amber: #a85d00;
}

html { font-size: 10.2pt; }
body {
  margin: 0;
  color: var(--ink);
  font-family: "DejaVu Sans", Arial, sans-serif;
  line-height: 1.47;
  hyphens: auto;
}

header#title-block-header {
  min-height: 225mm;
  display: flex;
  flex-direction: column;
  justify-content: center;
  border-top: 7px solid var(--blue);
  border-bottom: 1px solid var(--line);
  padding: 0 7mm;
  break-after: page;
}
header#title-block-header .title {
  font-size: 29pt;
  line-height: 1.08;
  letter-spacing: -0.02em;
  color: #0f2538;
  margin: 0 0 10mm;
}
header#title-block-header .subtitle {
  font-size: 14pt;
  line-height: 1.35;
  color: var(--muted);
  max-width: 150mm;
  margin: 0 0 15mm;
}
header#title-block-header .author,
header#title-block-header .date {
  font-size: 10pt;
  color: #667085;
  margin: 1mm 0;
}

nav#TOC {
  break-after: page;
  border: 1px solid var(--line);
  background: var(--soft);
  border-radius: 4px;
  padding: 8mm 10mm;
}
nav#TOC > ul { columns: 2; column-gap: 12mm; }
nav#TOC ul { padding-left: 5mm; margin: 0; }
nav#TOC li { margin: 1.2mm 0; break-inside: avoid; }
nav#TOC a { color: var(--ink); text-decoration: none; }

h1, h2, h3, h4 {
  color: #102a43;
  line-height: 1.18;
  break-after: avoid;
}
h1 {
  font-size: 21pt;
  margin: 0 0 7mm;
  padding-top: 2mm;
  border-bottom: 2px solid #b8c8d8;
  padding-bottom: 2.5mm;
  break-before: page;
}
main > h1:first-child { break-before: auto; }
h2 { font-size: 15.5pt; margin: 8mm 0 3mm; }
h3 { font-size: 12.5pt; margin: 6mm 0 2.2mm; }
h4 { font-size: 10.7pt; margin: 5mm 0 2mm; }

p { margin: 0 0 3.2mm; orphans: 3; widows: 3; }
ul, ol { margin: 1.5mm 0 3.5mm; padding-left: 7mm; }
li { margin: 1mm 0; }

blockquote {
  margin: 5mm 0;
  padding: 4mm 5mm;
  border-left: 4px solid var(--amber);
  background: #fff8ed;
  color: #3d4752;
  break-inside: avoid;
}
blockquote p:last-child { margin-bottom: 0; }

code {
  font-family: "DejaVu Sans Mono", Consolas, monospace;
  font-size: 0.9em;
  background: #f1f4f6;
  padding: 0.08em 0.25em;
  border-radius: 2px;
}
pre {
  background: #101820;
  color: #e6edf3;
  border: 1px solid #263442;
  border-radius: 4px;
  padding: 4mm;
  font-family: "DejaVu Sans Mono", Consolas, monospace;
  font-size: 8.15pt;
  line-height: 1.36;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  break-inside: avoid;
  margin: 3.5mm 0 5mm;
}
pre code { background: transparent; padding: 0; color: inherit; }

img, svg {
  display: block;
  max-width: 100%;
  height: auto;
  margin: 4mm auto 6mm;
  break-inside: avoid;
}
figure { break-inside: avoid; margin: 5mm 0; }
figcaption { color: var(--muted); font-size: 8.8pt; text-align: center; }

/* Keep very tall worklog screenshots to a printable page. */
img[src*="screenshots"] { max-height: 238mm; object-fit: contain; }

 table {
  width: 100%;
  border-collapse: collapse;
  margin: 4mm 0 6mm;
  font-size: 8.7pt;
  break-inside: auto;
}
thead { display: table-header-group; }
tr { break-inside: avoid; }
th {
  background: #eaf0f5;
  color: #102a43;
  text-align: left;
  font-weight: 700;
}
th, td {
  border: 1px solid #cfd8e1;
  padding: 2.2mm 2.5mm;
  vertical-align: top;
}

math { font-size: 1.02em; }

hr { border: 0; border-top: 1px solid var(--line); margin: 8mm 0; }
a { color: var(--blue); }

.page-break { break-before: page; }

/* Pandoc syntax classes */
.sourceCode .kw { color: #ff7b72; }
.sourceCode .dt { color: #79c0ff; }
.sourceCode .st { color: #a5d6ff; }
.sourceCode .dv, .sourceCode .fl { color: #d2a8ff; }
.sourceCode .co { color: #8b949e; font-style: italic; }
.sourceCode .fu { color: #d2a8ff; }
.sourceCode .op { color: #c9d1d9; }

@media print {
  a { text-decoration: none; }
}
EOF
cd "$ROOT/docs"
pandoc CNC_CAM_IR_Report.md \
  --standalone \
  --toc --toc-depth=3 \
  --number-sections \
  --mathml \
  --highlight-style=pygments \
  --embed-resources \
  --resource-path="$ROOT/docs:$ROOT" \
  --css=report.css \
  -o CNC_CAM_IR_Report.html
python - <<'PY'
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path('/mnt/data/cnc-cam-ir/docs')
html=(root/'CNC_CAM_IR_Report.html').read_text()
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox','--disable-dev-shm-usage'])
    page=browser.new_page(viewport={'width':1240,'height':1754}, device_scale_factor=1)
    page.set_content(html, wait_until='load', timeout=60000)
    page.emulate_media(media='print')
    page.wait_for_function("Array.from(document.images).every(i => i.complete)", timeout=60000)
    page.pdf(
        path=str(root/'CNC_CAM_IR_Report.pdf'),
        format='A4',
        print_background=True,
        prefer_css_page_size=True,
        display_header_footer=False,
        margin={'top':'0','right':'0','bottom':'0','left':'0'},
    )
    browser.close()
print('pdf written')
PY
pdfinfo "$ROOT/docs/CNC_CAM_IR_Report.pdf" | sed -n '1,20p'
ls -lh "$ROOT/docs/CNC_CAM_IR_Report."{md,html,pdf}

```

<details><summary>💭 Thinking</summary>

**Finalizing deliverables**

I’m updating the test screenshot, rebuilding the report and PDF, checking the rendered pages, and packaging the source, compiled output, examples, schema, artifacts, and documentation into one verified bundle.

</details>

```unknown
bash -lc set -e
ROOT=/mnt/data/cnc-cam-ir
printf 'Root exists: '; test -d "$ROOT" && echo yes
printf 'Tests summary:\n'; tail -n 20 "$ROOT/artifacts/test-results.txt" || true
printf '\nScreenshot files:\n'; ls -lh "$ROOT/artifacts/screenshots" || true
printf '\nReport files:\n'; ls -lh "$ROOT/docs/CNC_CAM_IR_Report."{md,pdf,html} 2>/dev/null || true
printf '\nPackage tree top:\n'; find "$ROOT" -maxdepth 2 -type f | sort | sed -n '1,120p'

```

<details><summary>💭 Thinking</summary>

**Created and validated the complete CNC-CAM prototype report package**

</details>

## Deliverables

- [Full project bundle](sandbox:/mnt/data/cnc-cam-ir-full-bundle.zip) — source, compiled JavaScript, TypeScript declarations, tests, schema, examples, screenshots, generated IR/G-code, Markdown report, and PDF.
- [Code package](sandbox:/mnt/data/cnc-cam-ir-code.zip) — implementation and runnable examples without the main report files.
- [Design report — Markdown](sandbox:/mnt/data/CNC_CAM_IR_Design_Report.md)
- [Design report — PDF](sandbox:/mnt/data/CNC_CAM_IR_Design_Report.pdf) — 32 pages, rendered and visually inspected.
- [Work screenshots](sandbox:/mnt/data/cnc-cam-ir-screenshots.zip)
- [SHA-256 checksums](sandbox:/mnt/data/cnc-cam-ir-checksums.txt)

Generated examples:

- [Badge canonical IR](sandbox:/mnt/data/cnc-cam-ir/artifacts/generated/badge.ir.json)
- [Badge G-code](sandbox:/mnt/data/cnc-cam-ir/artifacts/generated/badge.nc)
- [Two-pass probing IR](sandbox:/mnt/data/cnc-cam-ir/artifacts/generated/probing.ir.json)
- [Two-pass probing G-code](sandbox:/mnt/data/cnc-cam-ir/artifacts/generated/probing.nc)

## Implemented architecture

The implementation separates five semantic layers:

1. **Geometry** — immutable lines, center-form arcs, contours, frames, and similarity transforms.
2. **Process operations** — facing, contouring, explicit drilling, and an extension point for Dropcut strategies.
3. **Canonical machine IR** — spindle, tooling, coolant, work offsets, probing, pauses, homing, cutting motion, and explicitly staged rapid motion.
4. **Analysis and operational interpretation** — preflight diagnostics, traces, observations, bounds, distance, and time estimation.
5. **G-code refinement** — modal compilation, plane handling, `I/J/K` centers, one-shot `G53`, and dialect capability checking.

The categorical core is a phase-indexed `Plan<A,B>`:

- objects are coarse machine phases;
- primitive instructions are generators;
- identity is an empty plan;
- composition is command concatenation;
- identity and associativity are tested directly.

The executable denotation is a partial state-and-trace transformer, equivalent in shape to a combined `State + Either<Diagnostic> + Writer<Trace>` computation.

The design is grounded in the prototype’s existing rapid/plunge/ramp/cut move taxonomy and its nascent `{kind, phase, pts, ops}` representation. fileciteturn0file0L478-L560 The direct modal G-code emitter was then isolated behind a checked backend rather than remaining coupled to planning and UI state. fileciteturn0file0L1115-L1185

## Principal guarantees

The strongest rapid-motion invariant is structural: there is no generic `rapidTo(x,y,z)` canonical command. The IR has separate `rapid-z` and `rapid-xy` constructors, so a conforming backend cannot emit a combined `G0 X... Y... Z...` dogleg block.

Other checks include:

- tool and spindle prerequisites for cutting;
- safe retract before XY rapids, tool changes, homing, and program end;
- explicit machine-versus-work coordinate space;
- feed and spindle limits supplied by a machine profile;
- arc radius and planarity validation;
- supported G17/G18/G19 capability checks;
- explicit probe signal and failure policy;
- rejection of G38.2-style automatic failure semantics on a plain Fanuc `G31` profile;
- JSON Schema validation and command-to-G-code source maps.

## Validation

The final build passed all eight tests. Both generated IR documents validate against the included draft 2020-12 JSON Schema. The PDF is openable, unencrypted, text-based, and passed preflight.

The generated `.nc` files use an illustrative generic profile. They are not certified for a real machine and require machine-specific profile review, collision verification, simulation, and single-block or dry-run proving before execution.

