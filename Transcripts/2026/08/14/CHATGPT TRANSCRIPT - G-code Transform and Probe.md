# G-code Transform and Probe

- URL: https://chatgpt.com/c/6a7c0df3-b04c-83ea-ac18-4b257d5bb475
- Created: 2026-08-12T06:08:53.600Z

---

> study how the transform works and how the gcode controls which machine type and how the probe contact stuff works. https://github.com/jackdoe/grbly-rs

<details><summary>💭 Thinking</summary>

**Investigating the repository**

I’m going to inspect the repository’s structure, documentation, transformation logic, machine definitions, G-code generation, and probing workflow. I’ll trace how contacts become coordinates and how those coordinates are transformed and emitted.

**Investigated the repository**

</details>

I’ll trace this from the code outward: coordinate transforms, the G-code parser/state that selects machine behavior, and the probe/contact path from input detection through motion termination and reported coordinates.

```python3
{"path":"/GitHub/link_694554034b848191ab0db5a14b130105/get_repo","args":{"repository_full_name":"jackdoe/grbly-rs"}}
```

<details><summary>💭 Thinking</summary>

**Inspected GrblY-RS transformation and probing code across repository sources**

</details>

The repository is small enough to trace end-to-end. The main split is `src/gcode` for parsing/state and `src/grbl` for controller/motion behavior, so I’m following the same datum through both layers rather than treating them separately.

```python3
{"path":"/GitHub/link_694554034b848191ab0db5a14b130105/fetch","args":{"url":"https://api.github.com/repos/jackdoe/grbly-rs/contents/src/gcode?ref=master"}}
```

<details><summary>💭 Thinking</summary>

**Inspected GRBL transformation, machine controls, and heightmap probe implementation**

</details>

One important detail is already clear: the “transform” is not a generic affine matrix. It normalizes modal G-code into absolute millimeter linear segments, applies an XY `Placement` (orientation first, then offsets), samples the heightmap in those transformed XY coordinates, and adds only the resulting `dz` to Z.

```python3
{"path":"/GitHub/link_694554034b848191ab0db5a14b130105/fetch","args":{"url":"https://api.github.com/repos/jackdoe/grbly-rs/contents/src/ui?ref=master"}}
```

<details><summary>💭 Thinking</summary>

**Inspected G-code semantics and machine status**

</details>

```unknown
git clone --depth 1 https://github.com/jackdoe/grbly-rs.git /tmp/grbly-rs
```

<details><summary>💭 Thinking</summary>

**Cloned repository for machine type search**

</details>

```python3
{"path":"/GitHub/link_694554034b848191ab0db5a14b130105/fetch_file","args":{"repository_full_name":"jackdoe/grbly-rs","path":"src/grbl/engine.rs","ref":"master","encoding":"utf-8"}}
```

```json
{"uri":"/response/turn15","query":"probe","start_line":1,"end_line":7}
```

```json
{"uri":"/response/turn15","query":"probe_result_tx"}
```

```json
{"uri":"/response/turn15","query":"ensure_transformed"}
```

```json
{"uri":"/response/turn15","query":"pub fn probe"}
```

```json
{"uri":"/response/turn15","query":"fn guarded_probe"}
```

```json
{"uri":"/response/turn15","query":"reply.ok"}
```

```json
{"uri":"/response/turn17","query":"fn start_grid"}
```

```json
{"uri":"/response/turn17","query":"run_auto"}
```

```json
{"uri":"/response/turn17","query":"engine.probe_at"}
```

```json
{"uri":"/response/turn17","query":"HeightMap::new"}
```

<details><summary>💭 Thinking</summary>

**Inspected GRBL probe code and UI handling for machine detection**

</details>

```python3
{"path":"/GitHub/link_694554034b848191ab0db5a14b130105/fetch","args":{"url":"https://api.github.com/repos/jackdoe/grbly-rs/git/trees/master?recursive=1"}}
```

```json
{"uri":"/response/turn25","query":"Orientation::ALL"}
```

```json
{"uri":"/response/turn26","query":"M4"}
```

```json
{"uri":"/response/turn26","query":"M3"}
```

<details><summary>💭 Thinking</summary>

**Clarifying machine behavior**

I’m distinguishing machine selection from motion selection: this code handles G0–G3 motion and passes M/S commands through, but it doesn’t choose router versus laser. That behavior comes from controller configuration and firmware semantics.

**Clarified machine behavior**

**Inspected G-code processing, machine modes, placement controls, and engine logic**

</details>

```python3
{"path":"/GitHub/link_694554034b848191ab0db5a14b130105/fetch_file","args":{"repository_full_name":"jackdoe/grbly-rs","path":"src/gcode/words.rs","ref":"master","encoding":"utf-8"}}
```

```json
{"uri":"/response/turn25","query":"fn draw_placement"}
```

```json
{"uri":"/response/turn25","query":"offset_x"}
```

<details><summary>💭 Thinking</summary>

**Inspected G-code parsing, editor placement, and machine-type detection**

</details>

I studied the current `master` implementation. The architecture is fairly clean, but there are several important edge cases.

### Transform model

The streaming transform lives in `src/gcode/transform.rs`. It only activates when either a heightmap is attached or the job has a non-identity placement. With neither, the original G-code is returned byte-for-byte as lines, which is significant because unsupported G-code remains untouched in that case. fileciteturn7file0L2-L2

When active, it maintains a small modal state: current XYZ, G90/G91, G20/G21, current motion G0–G3, and feed. It resolves everything to **absolute millimeters**, then emits new `G90 G21 G0/G1` moves. G2/G3 arcs are tessellated into linear segments. With a heightmap, XY motion is further chopped into roughly 1 mm pieces. fileciteturn7file0L2-L2 fileciteturn8file0L2-L2

Placement is:

`original XY → orientation → XY offset`

The eight orientations are R0/R90/R180/R270, transpose/anti-transpose, and X/Y mirrors. Z is not changed by placement. fileciteturn10file0L2-L2

Then for every generated point it does conceptually:

`machine-stream X,Y = placement(original X,Y)`

`machine-stream Z = original/interpolated Z + heightmap.dz(transformed X,Y)`

So the heightmap is deliberately queried **after** rotation/mirroring/offset. `HeightMap::dz()` is bilinear interpolation, and coordinates outside its bbox are clamped to the nearest map edge. fileciteturn13file0L2-L2

Both `start_job()` and `step_line()` use exactly this transform through `ensure_transformed()`. The result is cached against the G-code `Arc`, heightmap `Arc`, and placement. The `src` array maps every generated 1-mm/tessellated line back to its original source G-code line for progress and soft-limit reporting. fileciteturn23file0L2-L2

### What G-code determines

There is **no physical “machine type” selection** in this codebase. `MachineState` doesn't contain a router/laser/mill/etc. type, and connection just opens a GRBL serial port and requests `$$`. The settings parser only consumes `$20` and `$130/$131/$132` for soft limits/travel; it doesn't, for example, inspect GRBL `$32` to classify laser mode. fileciteturn10file0L2-L2 fileciteturn24file0L2-L2

What G-code *does* select is the **motion type**. `G0`, `G1`, `G2`, and `G3` set a modal `motion` variable corresponding to rapid, linear, clockwise arc, and counterclockwise arc. A later line containing only `X/Y/Z` inherits that last motion. G90/G91 determine coordinate mode and G20/G21 units. fileciteturn22file0L2-L2

Things such as `M3 S10000` aren't interpreted as a machine type. They ultimately pass through to GRBL. So whether `M3 S...` means a router spindle, laser power, or something else is fundamentally a property of the attached GRBL machine/firmware configuration, not `grbly-rs`.

### Probe/contact path

There are actually **two separate probe signals**.

The live **electrical contact indicator** comes from the normal GRBL status polling. The engine sends realtime `?` every 200 ms. The response parser reads the `Pn:` field, and `MachineState.probe_active` becomes true when that field contains `P`. That's what drives `PROBE PIN: CONNECTED` versus `OPEN`. fileciteturn16file0L2-L2 fileciteturn24file0L2-L2

An actual probing operation uses `G38.3`. For a grid point, the engine sends safe Z, rapids to XY, then:

`G38.3 Z-max_depth Ffeed`

It installs a one-shot channel before sending the command and waits up to 60 seconds. GRBL's `[PRB:x,y,z:1]` message is separately parsed as a `ResponseType::Probe`; the final `1` means contact occurred. A `0` becomes `NoContact`. In either PRB-result case, the engine sends a retract before returning. fileciteturn23file0L2-L2 fileciteturn16file0L2-L2

The code treats the returned PRB position as machine coordinates and converts probe Z into work coordinates with:

`probe_work_z = PRB.z - WCO.z`

That resulting **work-Z value** is what gets stored in the heightmap. fileciteturn23file0L2-L2

That explains the zeroing workflow. The map does **not** internally subtract its first sample or fit a reference plane. If the board's nominal surface was zeroed beforehand, samples might be something like `0.000, +0.042, -0.018...`, and those values can directly be added to cutting Z. If the surface is sitting at work Z=5, the map would contain values around 5 and the streaming transform would literally add ~5 mm to every programmed Z. The UI therefore warns when WPos isn't approximately `(0,0,0)` before a grid probe. fileciteturn18file0L2-L2

The grid itself is the placed job bbox. Auto mode probes each non-skipped grid point. Manual mode simply records the current `mstate.wpos.z` when DONE is pressed. Skipped samples are filled afterward by inverse-distance weighting, then a `HeightMap` is created, cached, attached to `JobState`, and the transform cache is invalidated. fileciteturn18file0L2-L2 fileciteturn19file0L2-L2

### Important things I found

- **Loaded `G38.3` commands are unsafe when the transform is active.** The transform only recognizes G0–G3 as motion commands, while *any* X/Y/Z word is treated as motion. Thus something like `G38.3 Z-1 F50` can become a standalone `G38.3` followed by an inherited G0/G1 Z move. The same fundamental problem affects axis-bearing commands such as G10, G53, tool-offset commands, etc. With identity placement/no map they pass through safely because the transform fast-path does nothing. fileciteturn7file0L2-L2

- **Inch-mode feed appears to have a bug.** X/Y/Z/I/J/R are multiplied by 25.4 under G20, but `F` is stored without conversion. Generated motion is always `G21`, so an input `G20 ... F10` becomes a millimeter-mode move at `F10`, rather than approximately `F254`. The inch-mode tests cover coordinates but not feed conversion. fileciteturn7file0L2-L2 fileciteturn8file0L2-L2

- **`PROBE HERE` depends on whatever modal state GRBL currently has.** Grid probing first sends `G90 G21` rapids, so its G38.3 inherits absolute/mm mode. `probe_here()` has no preliminary rapid and sends only `G38.3 Z... F...`. If GRBL was left in G91 or G20, that single probe can behave differently than intended. fileciteturn23file0L2-L2

- **The live contact indicator doesn't gate the actual probe command.** `guarded_probe()` checks connected/busy, but doesn't reject an already-active probe pin. Also an `error:` response merely ACKs the send queue; it doesn't wake the probe result channel, so certain GRBL command errors can manifest as the full probe timeout rather than an immediate probe error. fileciteturn23file0L2-L2 fileciteturn24file0L2-L2

- **Heightmap-induced Z isn't part of the soft-limit preflight.** Soft limits inspect `JobState.segments`, which have placement applied but not the later `dz` correction. Also, a cached heightmap survives loading another G-code file, while `dz()` clamps outside the old bbox; placement changes explicitly clear the map, but ordinary file loading doesn't. Those are worth treating carefully. fileciteturn10file0L2-L2 fileciteturn13file0L2-L2 fileciteturn25file0L2-L2

So the mental model I have now is:

**G-code → minimal modal parser → absolute-mm geometry → placement XY → optional 1 mm subdivision → heightmap Z correction → GRBL serial**, while **probe contact → GRBL `Pn:P` for live state / `[PRB:...]` for a completed G38.3 → work-Z samples → bilinear heightmap → same streaming transform**.

The biggest architectural boundary is that the transform is reliable for the subset documented in the README—ordinary G0/G1/G2/G3 geometry—but it is not currently a general semantics-preserving G-code rewriter. fileciteturn9file0L2-L2

