---
title: "Gnosis Compiler: Python Rebuild and Web Experimentation Tool"
aliases:
  - Gnosis Compiler
  - Gnosis Python Compiler
  - Gnosis Bytecode Compiler
  - GNBC Compiler
tags:
  - project
  - compiler
  - python
  - bytecode
  - e-ink
  - layout
  - partial-evaluation
  - web-ui
status: active
type: project
created: 2026-03-22
repo: /home/manuel/code/wesen/2026-03-22--gnosis-compiler
related: "[[PROJ - Gnosis Layout Engine - PaperS3 UI Operating System]]"
---

# Gnosis Compiler: Python Rebuild and Web Experimentation Tool

The previous Gnosis project ([[PROJ - Gnosis Layout Engine - PaperS3 UI Operating System]]) implemented a layout engine directly in C++ on the ESP32-S3. Screen descriptions were written as C++ struct initializer trees — fast to execute, but impossible to iterate on without reflashing the MCU. Two earlier React/JSX prototypes (`gnosis-compiler.jsx` and `gnosis-engine.jsx`) explored the idea of compiling a JSON DSL into bytecode in the browser, but they bundled five concerns into single files: authoring format, layout algorithm, optimization logic, bytecode emission, and visualization UI.

This project is a clean restart: a proper **compiler** written in Python (~900 lines) that follows the front-end / middle-end / back-end architecture of a real compiler. It takes a YAML screen description plus compile-time props, runs it through parsing, normalization, optimization passes, layout, bytecode lowering, and binary serialization, and produces a compact GNBC (GNOSIS Bytecode) file that a microcontroller can interpret directly.

On top of the compiler, we built a browser-based **web experimentation tool** — a Flask server serving a single-page frontend that lets you edit YAML, see the compiled screen rendered on an HTML5 canvas in real time, and inspect every intermediate artifact: the AST at each pipeline stage, the disassembly listing, the hex dump, compilation statistics, refresh regions, and bind values.

> [!summary]
> **The compiler** has six stages:
> 1. **Front-end**: parse YAML/JSON, substitute compile-time props, normalize aliases
> 2. **Dead elimination**: remove `visible: false` and `cond when: false` nodes
> 3. **Box flattening**: merge nested same-axis containers (two fixed-point passes)
> 4. **Classification**: assign IDs, mark subtrees as static or dynamic
> 5. **Layout**: compute pixel Rect(x,y,w,h) for every node via two-pass flex algorithm
> 6. **Lowering + serialization**: emit bytecode, intern strings, record bind sites, merge refresh regions, pack into GNBC binary
>
> **The web tool** has: YAML editor with auto-compile, canvas bytecode interpreter rendering all 12 opcodes, 7 inspector panels, 3 debug overlays, 6 preset screens, and a bind value simulator.

## Why rebuild the compiler from scratch

The old React prototypes (`source/gnosis-compiler.jsx`, `source/gnosis-engine.jsx`) worked as demos but were architecturally unsound as compilers. They mixed layout computation with rendering, used a different opcode set than what the MCU needs, embedded font data and UI chrome in the same file as the compilation logic, and had no concept of intermediate representations. You could not add an optimization pass without touching the rendering code. You could not change the binary format without rewriting the UI.

The rebuild separates the compiler into isolated stages, each in its own file, each operating on a well-defined representation. The authored DSL goes in, a canonical AST comes out. The AST goes through optimization passes. The optimized AST gets laid out. The laid-out AST gets lowered to bytecode. The bytecode gets serialized. At no point does a later stage reach backward. This is the same pipeline structure used in GCC, LLVM, and every other real compiler — scaled down to a much simpler problem domain.

The practical benefit is that you can now add a new optimization pass by writing a single pure function, debug a stage in isolation by printing the intermediate AST, and change the binary format without touching the layout engine.

## The core insight: partial evaluation

The compiler's power comes from a single idea borrowed from programming language theory: **partial evaluation**. Anything that can be computed before the program reaches the MCU is computed at compile time.

This means:

- **Static text** is interned into a string pool. The MCU stores each string once and references it by a 16-bit ID. The compiler deduplicates identical strings automatically.
- **Layout rectangles** are fully precomputed. The MCU never runs a layout algorithm. Every widget has a fixed pixel position and size baked into the bytecode.
- **Lists and grids** with static data are lowered into individual TEXT instructions. A 6-item task list produces 6 TEXT instructions, not a "list" widget. The MCU has no concept of "list" — it just draws text at pre-computed positions.
- **Dead nodes** (invisible, conditional-false) are removed entirely. They do not consume bytecode space, string pool entries, or MCU memory.
- **Nested containers** are flattened when safe, reducing tree depth and simplifying the instruction stream.

The only things that remain for runtime are **bind values** — sensor readings, clocks, battery levels — which genuinely change on the device. For these, the compiler precomputes exactly which rectangles on screen need refreshing, which waveform to use, and which bytecode offset to patch.

## The DSL: what you author

The input is a YAML file describing a screen. A screen has three vertical bands — bar (top), body (main), nav (bottom) — with the body getting whatever height remains after the fixed-height bar and nav.

```yaml
type: screen
width: 400
height: 280
bar:
  type: hbox
  h: 16
  border_b: true
  children:
    - type: label
      text: "{{title}}"
    - type: spacer
    - type: label
      text: "{{status}}"
      color: ghost
body:
  type: hbox
  split: 188
  children:
    - type: fixed
      children:
        - type: label
          x: 8
          y: 8
          text: ROLL
          color: ghost
        - type: label
          x: 8
          y: 24
          bind: sensor.roll
          field_w: 3
          size: 2
          waveform: part
    - type: vbox
      children:
        - type: label
          h: 16
          text: TASKS
          color: ghost
        - type: list
          data: { $prop: tasks }
          row_h: 16
          max_items: 6
nav:
  type: hbox
  h: 16
  border_t: true
  children:
    - type: label
      text: A:OK
      color: mid
    - type: spacer
    - type: label
      text: "{{footer}}"
      color: mid
```

There are 15 node types. Container types (`screen`, `vbox`, `hbox`, `fixed`, `btn`, `cond`, `spacer`) define structure. Leaf types (`label`, `bar`, `list`, `grid`, `sep`, `fill`, `circle`, `cross`) produce draw instructions. The DSL supports the same widget vocabulary as the C++ firmware — labels with size multipliers, progress bars, grid calendars, list views — but describes them declaratively instead of as C++ struct initializations.

### Props vs binds

The most important distinction in the DSL is between **props** (compile-time) and **binds** (runtime).

**Props** use `{{mustache}}` syntax for strings and `{$prop: key}` for complex values. They are resolved before layout, so the compiler knows the exact text content and can compute string widths, intern text, and lower lists into flat draw instructions. Different props produce different binaries — this is like instantiating a React component with different props.

**Binds** use the `bind:` property. The compiler does not know the runtime value, so it reserves a rectangle based on `field_w` (worst-case character count) and emits a `BIND_TEXT` or `BIND_BAR` instruction that the MCU fills in at runtime. It also records the rectangle in a refresh region so the MCU knows exactly which screen area to redraw when the value changes.

This split is the mechanism by which partial evaluation works: props are the "known" inputs, binds are the "unknown" inputs. The compiler fully evaluates everything that depends only on known inputs.

## The compilation pipeline in detail

### Front-end (`dsl.py`, 215 lines)

The front-end is three functions chained together:

1. **`load_source()`** parses YAML or JSON. It auto-detects the format by file extension or by inspecting the first character. File paths, raw strings, and already-parsed dicts are all accepted.

2. **`resolve_props()`** recursively walks the tree and replaces `{{key}}` with the prop value and `{$prop: key}` with the entire subtree. Nested dot-path lookups work: `{{settings.display.brightness}}`. When a `$prop` resolves to a list inside a list context, the list is spliced in (flattened one level).

3. **`normalize_screen()`** canonicalizes aliases (`items` -> `children`, `label` -> `text`, `layout` -> `type`), validates that all node types are recognized, lowercases color and waveform strings, and wraps non-screen roots in a synthetic screen with empty bar and nav.

After the front-end, every node has a `type`, a `children` list, and canonical property names. No later stage needs to handle source-level aliases.

### Middle-end (`passes.py`, 115 lines)

Four pure-function tree transforms:

1. **Dead node elimination**: removes nodes with `visible: false`. Removes `cond` nodes with `when: false`. Unwraps `cond` nodes with `when: true` (promotes their children). This is classic dead code elimination on a tree IR.

2. **Box flattening** (run twice for fixed-point): merges a vbox-inside-vbox into a single vbox when the inner one has no explicit height and no borders. Same for hbox-inside-hbox (additionally requiring no split and no explicit width). This is algebraic simplification — reducing tree depth without changing semantics.

3. **ID assignment**: gives each node a sequential ID (`n1`, `n2`, ...) for debug tracing and bind site identification.

4. **Static/dynamic classification**: bottom-up walk that marks a subtree as `_static: true` if it contains no `bind` properties. This is binding-time analysis — the compiler uses it to determine which nodes need refresh metadata.

### Layout (`layout.py`, 235 lines)

The layout engine computes a `Rect(x, y, w, h)` for every node. The algorithm is a direct implementation of the formal specification in `source/gnosis-layout-algorithm.md`.

The screen is divided into three bands: bar gets its declared height, nav gets its declared height, body gets the remainder. Each band is laid out recursively.

**VBOX** uses a two-pass algorithm: pass 1 sums fixed-height children and counts flex children, pass 2 distributes remaining space equally among flex children and assigns y-positions. This is the same algorithm as CSS flexbox in its simplest form.

**HBOX** mirrors VBOX on the x-axis, with two additions: a special `split` mode for two-pane layouts (fixed left width, 1px divider, flex right), and intrinsic width measurement for labels and buttons (text width = character count x glyph width x size multiplier).

**FIXED** positions children at explicit `(x, y)` offsets relative to the parent origin. Leaf widgets without explicit dimensions get intrinsic sizes — labels get text-width x line-height, separators get parent-width x 1px, buttons get widest-child-label + 8px.

**Leaf measurement** precomputes content metrics: `max_visible_chars` for labels (how many characters fit in the allocated width), `visible_rows` for lists, `cell_w` and `visible_rows` for grids. These values are used during lowering to determine how much content to emit.

### Lowering (`lower.py`, 419 lines)

The lowerer walks the laid-out AST and emits a flat bytecode instruction stream. This is the largest stage because each of the 15 node types has its own emission logic.

Two interning tables are built during the walk:

- **StringPool**: maps static text to dense IDs (0, 1, 2, ...). Deduplicates identical strings.
- **BindTable**: maps bind names to dense IDs. The MCU uses these IDs to look up current runtime values.

For each node, the lowerer emits the appropriate instructions. Static labels produce `TEXT` (referencing the string pool). Bound labels produce `BIND_TEXT` (referencing the bind table). Bars, circles, crosses, separators, and rectangles each have their own opcodes. Borders produce `HLINE`. Split-pane dividers produce `VLINE`.

Lists and grids are lowered at compile time: each row/cell becomes individual `TEXT` and `FILL_RECT` instructions. A 6-item list becomes ~12 instructions. The MCU has no list widget — just pre-positioned text draws.

For every bound widget, the lowerer records a `BindSite` — the bind ID, the screen rectangle, the waveform, the node ID, and the byte offset in the code section. After all nodes are lowered, nearby bind sites are greedily merged into `RefreshRegion`s: if the union area waste of two sites is below a threshold (512 px^2), they merge into one region with the worst-case waveform.

### Serialization (`serialize.py`, 85 lines)

The final step packs everything into a GNBC (GNOSIS Bytecode) binary:

```
Header (26 bytes):
  "GNBC" magic, version, flags, width, height,
  section offsets and counts for strings/binds/regions/code

String section:
  For each string: length(u16 LE) + UTF-8 bytes

Bind section:
  For each bind name: length(u16 LE) + UTF-8 bytes

Region section:
  For each region: rect(4xu16) + waveform(u8) + bind_count(u8) + bind_ids

Code section:
  Raw bytecode ending with HALT (0xFF)
```

All values are little-endian. The MCU reads the header, walks to each section by offset, and interprets the code section sequentially. No parsing, no allocation, no searching.

## The bytecode instruction set

The ISA has 12 opcodes. Each starts with a 1-byte opcode followed by fixed-format operands:

| Op | Hex | Bytes | Description |
|---|---|---|---|
| NOP | 0x00 | 1 | No operation |
| HLINE | 0x01 | 8 | Horizontal line: x, y, w, color |
| VLINE | 0x02 | 8 | Vertical line: x, y, h, color |
| FILL_RECT | 0x03 | 10 | Filled rectangle: x, y, w, h, color |
| STROKE_RECT | 0x04 | 10 | Stroked rectangle: x, y, w, h, color |
| TEXT | 0x10 | 10 | Static text: x, y, size, color, max_chars, string_id |
| BIND_TEXT | 0x11 | 9 | Dynamic text: x, y, size, color, max_chars, bind_id |
| BAR | 0x12 | 15 | Static bar: x, y, w, h, value, max, track_color, fill_color |
| BIND_BAR | 0x13 | 14 | Dynamic bar: x, y, w, h, bind_id, max, track_color, fill_color |
| CIRCLE | 0x14 | 8 | Circle: cx, cy, r, color |
| CROSS | 0x15 | 8 | Cross: cx, cy, len, color |
| HALT | 0xFF | 1 | End of program |

The five-color palette (BG, FG, MID, LIGHT, GHOST) maps to e-ink dithering patterns on the real hardware and to hex values (#d8d4cc, #2a2a28, #9e9a92, #c4c0b8, #b8b4ac) in the web tool.

## Compilation statistics for the dashboard example

The dashboard screen — split pane with sensor readouts on the left, task list on the right, status bar and nav — compiles to:

- **19 AST nodes** (14 static, 5 dynamic)
- **205 bytes** of bytecode (22 instructions + HALT)
- **13 interned strings** ("GNOSIS//NAV", "LINK", "ROLL", "TEMP", "TASKS", 6 task items, "A:OK", "READY")
- **2 binds** (sensor.roll, sensor.temp)
- **3 refresh regions** (roll text, roll bar, temp text)
- **371 bytes** total GNBC binary

Those 371 bytes contain everything the MCU needs: the draw program, the string table, the bind mapping, and the refresh region metadata. The MCU runtime just needs a bytecode interpreter (~200 lines of C), a bind value provider, and an EPD partial refresh driver.

## The web experimentation tool

On top of the compiler, we built a browser-based workbench for interactive experimentation. The architecture is straightforward: a Flask server calls the compiler's `compile_with_stages()` method and returns all intermediate artifacts as JSON; a single-file HTML frontend renders them.

### What you see

The UI has three main areas:

- **Left column**: YAML source editor and props editor (tabbed), with auto-compile on keystroke (400ms debounce)
- **Right top**: HTML5 canvas rendering the compiled screen, with debug overlay toggles (bounds, depth heatmap, dirty regions)
- **Bottom panel** (drag-resizable): seven inspector tabs — Disassembly, AST viewer (switchable between 7 pipeline stages), Hex dump, Statistics, Manifest JSON, Refresh Regions, Bind Simulator

The canvas rendering is done by a JavaScript bytecode interpreter that decodes all 12 opcodes with little-endian u16 encoding, draws with a 5x7 bitmap font extracted from the original JSX prototypes, and applies the e-ink palette with optional grain texture. Bound values show either the field name or a user-provided simulation value from the Bind Simulator panel.

### Six preset screens

The tool ships with six presets that exercise different compiler features:

| Preset | Nodes | Code | Binds | Key feature |
|---|---|---|---|---|
| dashboard | 19 | 205B | 2 | Split pane, sensors, task list |
| boot | ~12 | 132B | 0 | Concentric circles, cross, progress bar |
| calendar | ~40 | 583B | 0 | Grid with 31 days, agenda, upcoming |
| sensors | ~25 | 257B | 6 | Six runtime binds with progress bars |
| widgets | ~30 | 367B | 2 | Gallery: text sizes, bars, shapes, lists, inverted |
| minimal | ~6 | 57B | 0 | Simplest possible screen |

### How to run it

```bash
cd /home/manuel/code/wesen/2026-03-22--gnosis-compiler
pip install flask pyyaml
python web_server.py --debug
# Open http://127.0.0.1:8080
```

## Project file structure

```
gnosis_compiler/           # The compiler (Python package)
  compiler.py              # Orchestrator: compile() and compile_with_stages()
  dsl.py                   # Front-end: parsing, props, normalization
  passes.py                # Middle-end: 4 optimization passes
  layout.py                # Layout engine: recursive two-pass flex
  lower.py                 # Bytecode emission + region analysis
  serialize.py             # GNBC binary serialization
  constants.py             # Opcodes, colors, waveforms, node types
  model.py                 # Program, BindSite, RefreshRegion, CompileOptions
  bytecode.py              # ByteWriter, StringPool, BindTable
  disasm.py                # Disassembler: bytecode -> text
  util.py                  # Rect, deep_clone, interpolation
  cli.py                   # Command-line interface

web_server.py              # Flask server wrapping the compiler
web/index.html             # Single-file frontend (canvas + 7 panels)

examples/                  # 6 preset screen definitions
  dashboard.yaml + .props.yaml
  boot.yaml
  calendar.yaml + .props.yaml
  sensors.yaml + .props.yaml
  widgets.yaml
  minimal.yaml

source/                    # Original JSX prototypes (reference)
  gnosis-compiler.jsx      # React bytecode compiler + executor
  gnosis-engine.jsx        # React layout engine visualization
  gnosis-layout-algorithm.md  # Formal algorithm spec (pseudocode)

docs/architecture-guide.md # 1300-line textbook for new engineers
tests/test_compiler.py     # Smoke tests
```

## Relationship to the C++ firmware

The Python compiler and the C++ firmware ([[PROJ - Gnosis Layout Engine - PaperS3 UI Operating System]]) implement the same layout algorithm (two-pass flex, split-pane hbox, fixed positioning) and the same dirty region tracking (collect + greedy merge). The difference is where the computation happens:

| Aspect | C++ Firmware | Python Compiler |
|---|---|---|
| Layout | At runtime on MCU | At compile time on laptop |
| Screen definition | C++ struct initializers | YAML/JSON files |
| String storage | Inline in code | Interned string pool |
| Widget rendering | Direct M5GFX calls | Bytecode instructions |
| Dirty tracking | Runtime tree walk | Precomputed regions |
| Data binding | Manual `MarkDirty()` | Bind table + BIND_TEXT/BAR opcodes |
| Iteration speed | Reflash MCU | Edit YAML, auto-compile |

The Python compiler is the "do everything possible off-device" evolution of the C++ engine. The goal is that the MCU runtime shrinks from a ~2000-line layout engine to a ~200-line bytecode interpreter — smaller, simpler, and with all the intelligence in the compiler where it's easy to iterate on.

## What I learned

The most important lesson is that **the compiler pipeline structure matters more than any individual optimization**. Once parsing, normalization, passes, layout, lowering, and serialization are cleanly separated, adding new capabilities is mechanical: write a new pass function, slot it into the pipeline, done. In the old single-file prototypes, every change required understanding the entire system.

The props-vs-binds distinction proved to be exactly the right abstraction boundary. It maps cleanly to partial evaluation theory (known inputs vs unknown inputs) and gives the compiler maximum freedom to optimize. A value that could be a bind but is actually a prop is free: the compiler folds it away completely. This is why the 6-item task list compiles to 12 flat draw instructions instead of a runtime list widget.

The web experimentation tool turned out to be more valuable than expected. Being able to edit YAML and instantly see the compiled bytecode, the laid-out rectangles, and the per-pass AST diffs makes the compiler's behavior tangible in a way that reading code or test output never achieves. The AST stage switcher, in particular, makes dead node elimination and box flattening visible — you can watch nodes disappear.
