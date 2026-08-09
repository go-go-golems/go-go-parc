# CNC GCODE Previewer Features

- URL: https://chatgpt.com/c/6a7714df-59a8-83ea-b74c-02fc3c14bad7
- Created: 2026-08-08T11:37:34.459Z

---

> features of a CNC GCODE previewer, in 3 examples of a GCODE previewer, from simple to complex. I want to preview my CNC Jobs before running them on my makera Z1

I’ll frame this as three escalating previewer designs—basic path inspection, stock-removal simulation, then machine-aware verification—and tie each level to what matters before running a job on a Makera Z1.

```json
{"system2_search_query":[{"q":"Makera Z1 G-code supported commands controller software Z1 CNC official"},{"q":"site:makera.com Z1 CNC gcode software controller"},{"q":"NC Viewer online G-code features official"},{"q":"CAMotics features G-code simulation official"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Designing previewer examples**

I’m organizing three concepts from basic visualization to machine-aware verification: a simple path viewer, a stock-removal simulator, and an advanced Z1-specific checker with envelopes, collisions, tooling, and controller compatibility.

**Designed previewer examples**

</details>

```json
{"image_query":[{"q":"NCViewer G-code viewer screenshot toolpath"},{"q":"CAMotics CNC simulator screenshot stock removal"}],"response_length":"short"}
```

<details><summary>💭 Thinking</summary>

**Refining machine safety**

I’m separating work envelope from actual safe motion. The strongest Z1 previewer combines final-code parsing, stock removal, tool and holder models, fixture collisions, rapid-motion warnings, controller compatibility, and machine-specific limits.

**Refined machine safety**

**Searched 16 websites**

</details>

iturn744681image1turn744681image0turn744681image3turn744681image4

For a **Makera Z1**, I would think of a G-code previewer as three increasingly capable systems. The key distinction is that a pretty 3D toolpath is not necessarily a safety simulator.

The Z1's nominal 3-axis working area is **200 × 200 × 100 mm**, its spindle runs up to **13,000 RPM**, and Makera publishes its own supported-code list. The optional rotary setup has an Ø80 × 150 mm working area. Those are useful parameters for a Z1-specific verifier. citeturn365491view0turn136811search19

## 1. Simple: G-code backplotter

Think **NC Viewer**.

You load:

```text
part.nc
```

and immediately get something like:

```text
             Z
             ↑
             │      ───── rapid
             │     /
             │    /
             │   ●──────── cutting path
             │  / ╲
             │ /   ╲_____
             └──────────────→ X
            /
           Y
```

Its main purpose is answering:

> **"Does this G-code roughly go where I think it goes?"**

A good simple viewer should have:

- 3D orbit/pan/zoom
- top/front/right/isometric views
- coordinate axes and origin
- `G0` rapid moves visually distinct from `G1/G2/G3` cutting moves
- arc rendering rather than turning everything into ugly line segments
- current X/Y/Z coordinates
- line-by-line G-code highlighting
- click a toolpath segment → jump to its G-code line
- click a G-code line → highlight its path
- playback/scrubbing
- hide/show rapids
- toolpath bounding box:
  - min X
  - max X
  - min Y
  - max Y
  - min Z
  - max Z
- units indicator
- feed and spindle display
- estimated runtime
- tool-change markers

NC Viewer is essentially in this category: it provides a 3D backplot, DRO, configurable views, rapid-motion display, path points and line/path inspection. citeturn365491view4

### Z1-specific additions

This simple viewer becomes substantially more useful if you give it a **Makera Z1 profile**.

For example:

```text
Makera Z1
────────────────────────────
Work area     200 × 200 × 100 mm
Spindle max   13,000 RPM

PROGRAM
X range       12.0 → 186.4 mm   ✓
Y range        8.0 → 197.8 mm   ✓
Z range      -14.2 →   8.0 mm   ✓

Max RPM       16,000             ✕
Rapid below stock               ✕
Unknown G-code: G68             ⚠

3 errors
2 warnings
```

I'd include checks for:

- path outside configured Z1 work envelope
- spindle command above 13,000 RPM
- unsupported G/M codes
- suspicious unit changes `G20 ↔ G21`
- `G90/G91` mode changes
- suspiciously enormous movements
- negative Z excursions beyond your stock/spoilboard
- `G0` moves below a configurable safe height
- zero/negative feed
- spindle-off cutting moves
- unexpected tool changes

This is **very easy to implement compared with a true simulator**, and already catches a surprising class of CAM/postprocessor mistakes.

---

# 2. Medium: stock-removal simulator

Think **CAMotics**.

Now the application understands not just a line traced by the cutter center, but:

> **"What material will this cutter actually remove?"**

You tell it:

```text
Stock:
100 × 80 × 12 mm aluminum

Origin:
X = stock center
Y = stock center
Z = stock top

Tool 1:
6 mm flat end mill

Tool 2:
3 mm ball end mill
```

The preview starts with:

```text
┌──────────────────────┐
│                      │
│      solid stock     │
│                      │
└──────────────────────┘
```

and gradually turns it into the machined workpiece.

CAMotics does this sort of 3-axis cut-stock simulation and supports several tool shapes including cylindrical, conical and ballnose tools. It also has tool tables, playback, position/feed/spindle displays and adjustable simulation resolution. citeturn365491view2turn365491view3

### Features I'd add

#### Stock definition

Support:

- rectangular stock
- cylindrical stock
- STL/mesh stock eventually

For your Z1 jobs:

```text
Width:   80 mm
Depth:   65 mm
Height:  20 mm
```

with a translucent stock preview before simulation.

---

### Real cutter geometry

Instead of simulating the cutter as a point:

```text
Flat endmill

 │     │
 │     │
 │     │
 └─────┘
   6mm
```

or:

```text
Ball endmill

 │     │
 │     │
 ╰─────╯
   3mm
```

Then sweep that solid along the path.

Mathematically, this is approximately computing

\[
S_{\text{final}}
=
S_{\text{initial}}
\setminus
\bigcup_{t} T(t)
\]

where \(S\) is the stock and \(T(t)\) is the cutter volume transformed to its position at time \(t\).

That one equation is basically the heart of a milling simulator.

---

### Material-removal playback

The timeline should let you scrub through:

```text
0% ━━━━━━━━━●━━━━━━━━━━━━━━━━━━ 100%
             ↑
          line 18,421

Tool:     T2  3 mm ball
Position: X=43.21 Y=18.29 Z=-6.42
Feed:     600 mm/min
Spindle:  12,000 RPM
```

I'd allow playback at:

```text
0.1×  0.5×  1×  5×  20×  100×
```

The user should also be able to jump by:

- G-code line
- operation
- tool change
- warning
- Z level

---

### Really useful warnings

Once you have stock geometry, you can detect things a backplotter cannot.

For example:

**Rapid through material**

```text
WARNING — line 18741

G0 X32.18 Y54.22 Z-3.0

Rapid move intersects stock.

Entry point:
X 31.44
Y 52.91
Z -0.02
```

Or:

**Cut through bottom of stock**

```text
Stock bottom     Z = -12.00 mm
Lowest cutter    Z = -12.75 mm

⚠ Tool penetrates 0.75 mm below stock.
```

That would be particularly useful when you're using a sacrificial spoilboard.

CAMotics itself has an important limitation here: its documentation explicitly notes that it does **not currently detect all cases such as fixture/tool-shaft collisions or rapid moves through material**. citeturn744681image0

So those are exactly the areas where I'd improve upon it.

---

# 3. Complex: complete virtual Makera Z1

This is the industrial approach used by systems such as **NCSIMUL/VERICUT**.

The question changes from:

> "Does the cutter make the right shape?"

to:

> **"What will the actual CNC machine do when it executes this exact NC program?"**

Hexagon's NCSIMUL, for example, interprets the NC program and simulates material removal together with the machine's digital twin, including collision detection between machine components, tooling and fixtures. citeturn417251search0turn417251search1

For a hobby machine, you don't need the entire industrial feature set. But a **Z1 digital twin** would be extremely useful.

Imagine displaying:

```text
       MAKERA Z1 DIGITAL TWIN

       ┌──────── spindle ────────┐
       │             │           │
       │          holder         │
       │             │           │
       │           tool          │
       │             ▼           │
       │      ┌────────────┐     │
       │ vise │    PART    │     │
       │ ┌────┴────────────┴───┐ │
       │ │       table         │ │
       │ └─────────────────────┘ │
       └─────────────────────────┘
```

Now you model:

- spindle
- spindle nose
- collet
- tool holder
- cutter
- table
- spoilboard
- vise
- clamps
- stock
- probing hardware
- optional rotary axis

---

## Collision checking

This unlocks the most useful CNC safety feature.

### Cutter vs clamp

```text
COLLISION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Line 24,818
Time 00:17:42

Tool T3
6 mm ball end mill

Tool ↔ clamp #2

Clearance:
-1.84 mm

Stop simulation
```

### Holder vs stock

This is more subtle.

The cutter itself might be fine:

```text
      │ holder │
      │        │
      └────────┘   ← collision
       │      │
       │ tool │
       │      │
───────┼──────┼──── stock
       │      │
```

Your CAM toolpath can therefore be **geometrically correct yet physically impossible** because the holder hits the workpiece.

Industrial simulators explicitly check this sort of whole-machine interaction. NCSIMUL also detects conditions such as rapid motion through material, cutting with the spindle stopped and cutting beyond usable flute length. citeturn417251search2

---

# An especially valuable feature: fixture editor

For a hobby CNC, I would spend considerable effort here.

Let the user create clamps quickly:

```text
+ Add Fixture

○ Rectangular clamp
○ Vise
○ Toe clamp
○ Bolt
○ Custom STL
```

For a rectangular clamp:

```text
Position:
X  17 mm
Y  32 mm
Z   8 mm

Size:
X  15 mm
Y  40 mm
Z  10 mm
```

and drag it directly in the viewport.

Then:

```text
CLEARANCE MAP

Tool → clamp 1     8.4 mm   ✓
Tool → clamp 2     3.1 mm   ✓
Holder → clamp 1   1.2 mm   ⚠
Spindle → stock   18.2 mm   ✓
```

For the kinds of flip-and-remount CNC operations you were asking about earlier, this becomes particularly valuable because you could retain the fixture definition between setups.

---

# The feature progression

| | Simple | Medium | Complex |
|---|---|---|---|
| Parse G-code | ✓ | ✓ | ✓ |
| 3D toolpath | ✓ | ✓ | ✓ |
| Line highlighting | ✓ | ✓ | ✓ |
| Feed/RPM | ✓ | ✓ | ✓ |
| Bounding box | ✓ | ✓ | ✓ |
| Z1 envelope check | ✓ | ✓ | ✓ |
| Actual cutter shape | — | ✓ | ✓ |
| Stock removal | — | ✓ | ✓ |
| Final cut geometry | — | ✓ | ✓ |
| Rapid-through-stock warning | optional | ✓ | ✓ |
| Clamp geometry | — | optional | ✓ |
| Tool holder | — | optional | ✓ |
| Full Z1 geometry | — | — | ✓ |
| Fixture collision | — | optional | ✓ |
| Spindle/head collision | — | — | ✓ |
| 4th-axis kinematics | — | — | ✓ |
| Controller-specific behavior | basic | partial | ✓ |

---

# What I would build/use for your Z1

I think the sweet spot is actually **Level 2½** rather than a full industrial digital twin:

```text
              Z1 G-CODE CHECKER

 ┌─────────────────────────────┐
 │                             │
 │       3D cut preview        │
 │                             │
 │ stock + tool + clamps       │
 │                             │
 └─────────────────────────────┘

 ┌──────────────┬──────────────┐
 │ G-CODE       │ CHECKS       │
 │              │              │
 │ G21          │ ✓ Units      │
 │ G90          │ ✓ Envelope   │
 │ G0 Z5        │ ✓ RPM        │
 │ G0 X...      │ ⚠ Clearance  │
 │ G1 Z...  ←───┼─● warning    │
 │              │              │
 └──────────────┴──────────────┘

     ▶  ━━━━━━━●━━━━━━━━━━

       SAFE TO RUN?
           ⚠ 2 warnings
```

Specifically, I'd implement these first:

1. **Makera-compatible G-code interpreter**
2. **3D backplotter**
3. **machine/work coordinate display**
4. **200 × 200 × 100 mm Z1 workspace overlay**
5. **stock definition**
6. **flat/ball/V-bit tool geometry**
7. **stock-removal simulation**
8. **rapid-through-stock detection**
9. **spoilboard penetration detection**
10. **13,000 RPM limit check**
11. **tool + holder definition**
12. **simple clamp/fixture solids**
13. **tool/holder/fixture collisions**
14. **click warning ↔ G-code line**
15. **playback/scrubber**
16. **final-stock STL export**
17. **optional comparison against the intended STL**
18. **eventually, the Z1 rotary-axis model**

The last item in #17 is particularly powerful. Given your original design \(M\) and simulated result \(S\), you can compute approximately

\[
E_{\mathrm{gouge}} = S^c \cap M
\]

for material removed that **should have remained**, and

\[
E_{\mathrm{rest}} = S \setminus M
\]

for material that **should have been removed but wasn't**.

Then render something conceptually like:

```text
GRAY   = correct part
RED    = gouged too deeply
BLUE   = uncut/rest material
```

At that point the application stops being merely a G-code *viewer* and starts becoming a genuine **G-code verifier**.

For your Z1 in particular, that is the direction I'd take: **inspect the final post-processed G-code that will actually be sent to the machine, rather than relying only on your CAM system's pre-post simulation.** Makera supports external CAD/CAM workflows in addition to Makera Studio, so independently checking the final NC output makes sense. citeturn365491view0turn136811search2

If we're building this as part of the CNC project, **Level 1 is a fairly contained graphics/parser project; Level 2 gets into computational geometry; and Level 3 leads directly into collision detection, swept volumes, spatial acceleration structures, and rigid-body kinematics**—which dovetails very closely with the CAM algorithms we've been discussing. memcite

