# Window Manager Performance Optimization

- URL: https://chatgpt.com/c/6a601566-80fc-83ea-8501-7e7c4ce1c068
- Created: 2026-07-22T00:57:14.993Z

---

> I am working on a window manager :https://github.com/go-go-golems/go-go-wm
>
> It is quite slow, inspired by i3. I don't know much about window managers.
>
> It is a special window manager that uses the presentation based UI pattern from the 80ies (genera dynamic windows, common lisp CLIM) and is fully sriptable by my github.com/go-go-golems/go-go-goja scripting environment, with a lot of DSL research https://parc.yolo.scapegoat.dev/note/research/kb/projects/widget-dsl and https://parc.yolo.scapegoat.dev/note/research/kb/projects/go-go-goja
>
> Read up on all the go-go-wm entries of the last 3 days : https://parc.yolo.scapegoat.dev/note/projects/2026/07/18/proj-go-go-wm-building-a-presentation-based-window-manager-in-go
>
> Read the code carefully.
>
> ---
>
> Research using the code of i3 and other window managers if you want:
>
> - systematically approach building a window manager
> - review the existing implement
> - what I need to do to improve the performance (especially window resizing for example is very slow)
> - how to design / architect a full UI scriptability, where I want to basically allow custom "widgets" to be created from JS with full PBUI so that I can create custom menu bar ,right click menu widgets, modals, taskbars etc... 
>
> Create a detailed document that is very educational as well in purpose, it goes really deep but explains all the necessary concepts for a new developer / intern. I'm attaching some writing guidelines whch can help. We are creating something quite novel here, using UX patterns that have also been forgotten over time (inspired by smalltalk and genera and hypercard and all the cool stuff from the 70 80ies).
>
> I'm attaching my oriignal self contained sketch of what became go-go-wm, and also a textbook writing skill. The basketball one has really interesting widgets and stuff that can be quite useful for a developer wm like the one we are building.
>
>
> Focus on the performance / best practices when writing a x11 window manager.

I’ll audit the recent notes and source, trace X11 hot paths, compare mature window managers, and produce a cited handbook with prioritized performance and scriptable PBUI recommendations.

<details><summary>💭 Thinking</summary>

**Listed files and read attachments from conversation**

</details>

```unknown
bash -lc cat /home/oai/skills/docx/SKILL.md
```

<details><summary>💭 Thinking</summary>

**Read docx skill documentation**

**Searched library for attachments and inspected code files**

**Inspected GitHub repo and fetched code attachments**

</details>

```unknown
bash -lc git ls-remote https://github.com/go-go-golems/go-go-wm.git HEAD
```

<details><summary>💭 Thinking</summary>

**Inspected remote repository reference**

**Retrieved GitHub repository metadata and searched for package occurrences**

</details>

```json
{"search_query":[{"q":"site:github.com/go-go-golems/go-go-wm go-go-wm GitHub"},{"q":"site:parc.yolo.scapegoat.dev/note/projects/2026/07/18 go-go-wm"},{"q":"site:parc.yolo.scapegoat.dev/note/projects/2026/07/19 go-go-wm"},{"q":"site:parc.yolo.scapegoat.dev/note/projects/2026/07/20 OR site:parc.yolo.scapegoat.dev/note/projects/2026/07/21 go-go-wm"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 12 websites**

**Tested GitHub fetch_file for directory listing**

</details>

The prototype confirms typed presentations, cross-pane accept, and type-directed verbs as the semantic core. Resize slowness now points to synchronous event-loop rendering, full invalidation, and costly pane redraws.

Resize stalls chiefly come from full-frame decoration buffers, per-size SHM recreation, and ineffective motion coalescing. Script tiles additionally incur two full-area writes plus conversion each repaint.

The 17,000-word draft now includes retained shell/runtime architecture, adaptive resize strategies, protocol tests, implementation phases, benchmarks, intern exercises, and source mapping. I’m completing DOCX layout verification.

```json
{"open":[{"ref_id":"https://github.com/go-go-golems/go-go-wm/archive/refs/heads/main.zip"},{"ref_id":"https://github.com/go-go-golems/go-go-wm"}],"response_length":"short"}
```

<details><summary>💭 Thinking</summary>

**Searching the web**

</details>

```json
{"open":[{"ref_id":"https://codeload.github.com/go-go-golems/go-go-wm/zip/refs/heads/main"}],"response_length":"short"}
```

<details><summary>💭 Thinking</summary>

**Searched 12 websites**

**Fetched GitHub archive, commits, and changes**

</details>

```unknown
bash -lc find /mnt/data/go-go-wm-research -maxdepth 3 -type f -printf '%p %s bytes\n' | sort
```

<details><summary>💭 Thinking</summary>

**Listed files and their sizes**

**Fetched and processed files from GitHub for PR #1**

</details>

```json
{"open":[{"ref_id":"https://raw.githubusercontent.com/go-go-golems/go-go-wm/main/go.mod"}],"response_length":"short"}
```

<details><summary>💭 Thinking</summary>

**Searching the web**

</details>

```json
{"search_query":[{"q":"\"Building a Presentation-Based Window Manager in Go\""},{"q":"site:parc.yolo.scapegoat.dev \"go-go-wm\""},{"q":"site:parc.yolo.scapegoat.dev/note/projects/2026/07/20 \"GGWM\""},{"q":"site:parc.yolo.scapegoat.dev/note/projects/2026/07/21 \"go-go-wm\""}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 6 websites**

</details>

```json
{"open":[{"ref_id":"https://codeload.github.com/go-go-golems/go-go-wm/zip/refs/heads/main"}],"response_length":"short"}
```

<details><summary>💭 Thinking</summary>

**Searching the web**

**Fetched raw files from GitHub**

</details>

```json
{"search_query":[{"q":"raw.githubusercontent.com/go-go-golems/go-go-wm/main/pkg/wmx11/divider.go"}],"response_length":"short"}
```

<details><summary>💭 Thinking</summary>

**Searched 10 websites**

</details>

```unknown
bash -lc set -euo pipefail
cd /mnt/data/go-go-wm-research/sources
printf 'PBUI shell functions:\n'
grep -nE '^(export default )?function |^class |^const [A-Z][A-Z0-9_]+ = ' 'pbui-shell(3).jsx' | head -120
printf '\nBasketball components:\n'
grep -nE '^(export default )?function |^class |^const [A-Z][A-Z0-9_]+ = ' pbui-basketball.jsx | head -220
```

<details><summary>💭 Thinking</summary>

**Inspected local prototype code and basketball widget performance**

**Fetched code files and inspected motion handling optimizations**

**Optimized frame rendering, inspected files, and fetched content**

**Searched and analyzed GGWM-001 GitHub commits and repository files**

**Researched i3 window manager performance and fetched source code**

</details>

```json
{"search_query":[{"q":"site:git.suckless.org/dwm/file/dwm.c.html resizemouse 1000 / 60"},{"q":"site:bspwm.org bspwm architecture XCB window manager"},{"q":"site:awesomewm.org doc lua widget declarative hierarchy"},{"q":"site:herbstluftwm.org architecture window manager frames"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 11 websites**

**Planning document creation**

I’m focusing on creating a detailed document with DOC X and Markdown. I'll carefully confirm what’s been read and include accurate citations. Planning includes possibly analyzing resources and building tests.

**Planned document creation**

</details>

```unknown
bash -lc cat /home/oai/skills/docx/SKILL.md && printf '\n---ATTACHED SKILL HEAD---\n' && sed -n '1,260p' /mnt/data/go-go-wm-research/sources/SKILL\(6\).md
```

<details><summary>💭 Thinking</summary>

**Read skill documents and cloned repository for updates**

</details>

```json
{"search_query":[{"q":"site:parc.yolo.scapegoat.dev/note/projects/2026/07/18 \"go-go-wm\""},{"q":"site:parc.yolo.scapegoat.dev/note/research/kb/projects/widget-dsl widget DSL"},{"q":"site:parc.yolo.scapegoat.dev/note/research/kb/projects/go-go-goja go-go-goja"},{"q":"X.Org ICCCM ConfigureRequest synthetic ConfigureNotify window manager specification"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 5 websites**

**Researching primary sources**

I’m diving into technical topics like X11 clients, window management, and design comparisons. I'll gather relevant resources including project diaries, specs, and documentation to ensure full coverage of the project’s requirements.

**Researched primary sources**

**Fetched project diaries, technical documents, and file content from line 246**

</details>

```json
{"search_query":[{"q":"github go-go-golems go-go-wm GGWM-007"},{"q":"github go-go-golems go-go-wm GGWM-008 launcher"},{"q":"github go-go-golems go-go-wm GGWM-009 REPL"},{"q":"github go-go-golems go-go-wm GGWM-011 focus fullscreen"}],"response_length":"short"}
```

<details><summary>💭 Thinking</summary>

**Searched 8 websites**

**Fetched GitHub file content and document sections for review**

</details>

```json
{"search_query":[{"q":"site:specifications.freedesktop.org/wm-spec latest _NET_WM_SYNC_REQUEST _NET_WM_STRUT_PARTIAL"},{"q":"site:x.org/releases/current/doc xcb tutorial request reply checked unchecked round trip"},{"q":"site:x.org/releases/current/doc/xextproto sync extension XSync official specification"},{"q":"site:x.org/releases/current/doc/xextproto damage extension specification official"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 68 websites**

**Comparing window managers**

I’m evaluating different window managers like i3, Awesome, bspwm, and dwm, focusing on their architecture, performance, and scriptability. I’ll review relevant source code for layout algorithms and event handling.

**Compared window managers**

**Fetched code, handled requests, and inspected files for events and focus state**

**Preparing technical document**

I’m creating a detailed document addressing go-go-wm performance, scriptability, and PBUI architecture. I’ll focus on Resize optimization, X11 best practices, and documentation quality for developers.

**Performance analysis and diagnosis**

I’m focusing on key performance issues like event path measurement, coalescing, and geometry handling. I'll use stage counters, traces, and optimizations to reduce X11 and WM-related latency.

**Optimizing resize and rendering**

I’m improving resize handling by separating client decorations from full frames. Using smaller surfaces and caching, I aim to reduce resource destruction and optimize the update process for PBUI layouts.

**Prepared technical document, analyzed performance, and optimized rendering**

</details>

```unknown
bash -lc sed -n '1,260p' '/mnt/data/go-go-wm-research/sources/SKILL(6).md' && printf '\n---JSX PROTOTYPE HEADINGS---\n' && grep -nE '^function |^const [A-Z][A-Za-z0-9_]* ?=|^export default|className=' '/mnt/data/go-go-wm-research/sources/pbui-shell(3).jsx' | head -160 && printf '\n---BASKETBALL COMPONENTS---\n' && grep -nE '^function |^const [A-Z][A-Za-z0-9_]* ?=|^export default' '/mnt/data/go-go-wm-research/sources/pbui-basketball.jsx' | head -220
```

<details><summary>💭 Thinking</summary>

**Read skill components for documentation creation**

</details>

```json
{"search_query":[{"q":"CLIM II specification presentations presentation types accept official PDF"},{"q":"Common Lisp Interface Manager specification presentation types accept official"},{"q":"Genera Dynamic Windows presentation types accept documentation"},{"q":"HyperCard scriptable UI HyperTalk official manual PDF"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 23 websites**

</details>

```unknown
bash -lc cat /home/oai/skills/docx/SKILL.md
```

<details><summary>💭 Thinking</summary>

**Read docx skill documentation**

**Extracted code snippets and fetched top commits for repository**

</details>

```unknown
bash -lc which pandoc || true; python - <<'PY'
import docx, sys
print('python-docx', docx.__version__)
PY
fc-list | head -20
```

<details><summary>💭 Thinking</summary>

**Checked Pandoc, Python-docx, and conversion-related packages**

</details>

```unknown
bash -lc mkdir -p /mnt/data/go-go-wm-research/{figures,docx_qa,build} && cat > /mnt/data/go-go-wm-research/figures/current-resize.dot <<'DOT'
digraph G {
  graph [rankdir=LR, bgcolor="white", fontname="Inter", fontsize=10, pad=0.2, nodesep=0.3, ranksep=0.5];
  node [shape=box, style="rounded,filled", fillcolor="#f4f4f4", color="#333333", fontname="Inter", fontsize=9, margin="0.10,0.07"];
  edge [color="#444444", fontname="Inter", fontsize=8, arrowsize=0.7];

  motion [label="X MotionNotify\n(many events)"];
  gate [label="16 ms wall-clock gate\ninput.go"];
  op [label="Apply OpSetRatio\nallocates durable tree update\nemits op/event"];
  layout [label="Full wmcore.Layout\nmap allocation + full traversal"];
  divs [label="syncDividers\nmove/map/paint all divider windows"];
  geom [label="MoveResize changed frames\nConfigure child clients"];
  frame [label="paintFrame for resized frames\nfull W x H RGBA fill + title/border"];
  shm [label="Size changed\nDestroy + recreate MIT-SHM surface\nfull RGBA to BGRA write"];
  client [label="Client receives ConfigureNotify"];
  xapp [label="PBUI xapp redraw\nfull app.Render + new X image\nupload + destroy"];
  release [label="ButtonRelease\nforce final motion"];

  motion -> gate -> op -> layout -> divs -> geom -> frame -> shm -> client -> xapp;
  release -> op [style=dashed, label="final position"];

  subgraph cluster_wm {
    label="Window-manager work";
    color="#999999";
    style="rounded,dashed";
    gate; op; layout; divs; geom; frame; shm;
  }
  subgraph cluster_client {
    label="Managed PBUI client work";
    color="#999999";
    style="rounded,dashed";
    client; xapp;
  }
}
DOT
cat > /mnt/data/go-go-wm-research/figures/target-resize.dot <<'DOT'
digraph G {
  graph [rankdir=LR, bgcolor="white", fontname="Inter", fontsize=10, pad=0.2, nodesep=0.28, ranksep=0.55];
  node [shape=box, style="rounded,filled", fillcolor="#f4f4f4", color="#333333", fontname="Inter", fontsize=9, margin="0.10,0.07"];
  edge [color="#444444", fontname="Inter", fontsize=8, arrowsize=0.7];

  motion [label="MotionNotify burst"];
  mailbox [label="Latest-pointer mailbox\nreplace stale coordinates"];
  sched [label="Resize scheduler\nat most one update in flight\nframe budget + queue-lag check"];
  preview [label="Transient preview ratio\nno durable op/event per frame"];
  subtree [label="Recompute affected split subtree\ndiff old/new geometry"];
  choose [shape=diamond, label="Mode and budget"];
  outline [label="Outline path\nmove one helper/divider window"];
  live [label="Live path\nbatch only changed X geometry\npaint thin decoration layers"];
  sync [label="Client synchronization\n_NET_WM_SYNC_REQUEST when supported\ntimeout and fallback"];
  release [label="ButtonRelease"];
  commit [label="Commit final ratio once\none OpSetRatio + event\nfull-quality reconciliation"];

  motion -> mailbox -> sched -> preview -> subtree -> choose;
  choose -> outline [label="outline / over budget"];
  choose -> live [label="live / budget available"];
  live -> sync;
  outline -> mailbox [style=dashed, label="next latest"];
  sync -> mailbox [style=dashed, label="next latest"];
  release -> mailbox [label="store final"];
  mailbox -> commit [label="release drains final", constraint=false];
}
DOT
cat > /mnt/data/go-go-wm-research/figures/pbui-scene.dot <<'DOT'
digraph G {
  graph [rankdir=LR, bgcolor="white", fontname="Inter", fontsize=10, pad=0.25, nodesep=0.35, ranksep=0.6];
  node [shape=box, style="rounded,filled", fillcolor="#f4f4f4", color="#333333", fontname="Inter", fontsize=9, margin="0.11,0.08"];
  edge [color="#444444", fontname="Inter", fontsize=8, arrowsize=0.7];

  js [label="JavaScript owner loop\nstate + handlers + composition"];
  snap [label="Immutable keyed SceneSpec\ndata only; generation stamped"];
  norm [label="Normalize + schema + capability validation\nreject unknown fields early"];
  diff [label="Keyed diff and invalidation\nlayout-dirty / paint-dirty / semantic-dirty"];
  layout [label="Measure and layout\nGo-owned widget protocols"];
  display [label="Retained display list and layers\ntext, geometry, images, hit regions"];
  damage [label="Damage accumulation\ncoalesce dirty rectangles"];
  surf [label="Surface manager\ntile, window, bar, menu, modal, popup"];
  x11 [label="X11 commit\nbatched requests, cached resources"];

  input [label="X input and PBUI broker events"];
  hit [label="Hit test + focus/input scope\nserialized EventEnvelope"];
  types [label="Presentation type registry\nrenderers, subtyping, coercions, verbs"];

  js -> snap -> norm -> diff -> layout -> display -> damage -> surf -> x11;
  input -> hit -> js;
  display -> hit [dir=both, label="regions / focus graph"];
  types -> norm [label="object validation"];
  types -> display [label="faces / accept styling"];
  types -> hit [label="accept and menu semantics"];

  subgraph cluster_vm {
    label="VM-owned";
    color="#999999";
    style="rounded,dashed";
    js;
  }
  subgraph cluster_host {
    label="Host-owned, VM-free hot path";
    color="#999999";
    style="rounded,dashed";
    snap; norm; diff; layout; display; damage; surf; x11; hit; types;
  }
}
DOT
cat > /mnt/data/go-go-wm-research/figures/surface-stack.dot <<'DOT'
digraph G {
  graph [rankdir=TB, bgcolor="white", fontname="Inter", fontsize=10, pad=0.2, nodesep=0.18, ranksep=0.28];
  node [shape=box, style="rounded,filled", fillcolor="#f4f4f4", color="#333333", fontname="Inter", fontsize=9, width=4.8, margin="0.12,0.08"];
  edge [color="#444444", fontname="Inter", fontsize=8, arrowsize=0.7];

  chrome [label="Global chrome band\nmenu bars, taskbars, launchers, notifications\nmay reserve work area with EWMH struts"];
  modal [label="Modal/input-scope band\nexplicit owner, focus restore, cancellation policy"];
  popup [label="Popover/menu/tooltip band\nanchored placement, outside-click dismissal"];
  floats [label="Floating application band\ndialogs, utilities, transient windows"];
  tiles [label="Tiled application and PBUI surface band\nwmcore geometry owns placement"];
  root [label="Root background"];

  chrome -> modal -> popup -> floats -> tiles -> root [label="stacked above"];
}
DOT
for f in /mnt/data/go-go-wm-research/figures/*.dot; do dot -Tpng -Gdpi=180 "$f" -o "${f%.dot}.png"; done
ls -lh /mnt/data/go-go-wm-research/figures/*.png
```

<details><summary>💭 Thinking</summary>

**Created Graphviz diagrams, analyzed images, and wrote handbook sections**

</details>

```unknown
bash -lc cat >> /mnt/data/go-go-wm-research/go-go-wm-handbook.md <<'EOF'

---

# Part IV. A fully scriptable presentation-based UI

## 24. Define the semantic target before defining widgets

A widget API can easily become a list of drawing calls and callbacks. That would miss the system's distinguishing idea. The target is not “React in Goja” and not “let scripts draw into X windows.” The target is a desktop where visible objects preserve identity, type, actions, documentation, and acceptance semantics across every surface.

A complete PBUI node can answer these questions:

- What object does this output represent?
- What presentation type is it using in this view?
- Which other types can accept it through subtyping or coercion?
- Which verbs are applicable, and which process owns each verb?
- What visual face should be used in this context?
- What region is pointer-sensitive?
- How does keyboard focus reach it?
- What documentation should appear on hover?
- How is it serialized when crossing a process boundary?
- Which state updates when it is activated?

CLIM's presentation types combine display, input acceptance, and type relationships. HyperCard made visible objects scriptable and routed messages through an object hierarchy. Smalltalk environments made inspection and modification part of ordinary development. The go-go-wm contribution is to combine those properties with process isolation, X11 window management, typed broker objects, and a modern embedded JavaScript runtime.

### 24.1 Five non-negotiable semantics

**First, presentations are not limited to controls.** A visual node, text span, plot point, row, image region, or composite group can carry a presentation.

**Second, `accept` is a desktop input mode, not a modal dialog owned by the requesting app.** Compatible presentations across processes become candidate input. The requestor receives a typed object, not coordinates or widget identity.

**Third, verbs are open and type-directed.** A process can attach a verb to a type it did not define. Menus are assembled from the registry at use time.

**Fourth, views are distinct from values.** A `player` can appear as a compact chip, a table row, a radar summary, an inspector card, or a shot-chart selection. The object identity and type remain stable.

**Fifth, scripting cannot compromise the host loop.** JavaScript may describe state, trees, handlers, and effects, but Go owns normalization, layout, hit testing, drawing, X resources, focus, grabs, and final commit.

### 24.2 The basketball prototype as a requirements test

A generic widget proposal is incomplete unless it can express the basketball prototype naturally:

- The leaders table has sortable columns, selectable player rows, numeric alignment, and presentation-sensitive names.
- The shot chart has court geometry plus hundreds of typed shot markers and shared player selection.
- The radar chart has axes, labels, polygons, comparison colors, and typed player series.
- Trends have plots with hover/click targets.
- Standings contain team presentations nested in rows.
- The watchlist stores object references and re-presents them in another view.
- Inspector and Trace surfaces react to desktop-wide interactions.

If the API requires each application to flatten all of those into ad hoc rectangular buttons, it is not a PBUI widget system. It is the current region list with more syntax.

## 25. Review of the current `ui` module

The current `require("ui")` API has the correct safety boundary:

- JavaScript builders produce plain data.
- `app({render, actions, verbs, onKey})` owns JS callables on the runtime loop.
- Render output is normalized into a Go `uispec.Spec`.
- The last normalized snapshot is protected by a mutex.
- WM tile and standalone host renderers read the snapshot without entering the VM.
- Actions post to the JS loop, execute handlers, rerender, install the new snapshot, and request a host redraw.

This design should be generalized, not replaced.

### 25.1 Limitations of the current row/segment IR

The current IR can represent text, hints, object chips, buttons, tables, images, and fields. It cannot yet express:

- Nested row/column/stack composition with stable identity.
- Constraints, alignment, wrapping, min/max sizes, or intrinsic measurement protocols.
- Clipping, scrolling, virtualization, transforms, or z-order inside a surface.
- A presentation wrapper around arbitrary visual children.
- Reusable style classes and state-dependent styles.
- Focus traversal and text-editing ownership.
- Menus, popovers, modals, tooltips, and surfaces as first-class objects.
- Fine invalidation or retained layers.
- Asynchronous data/resource states.
- Component-local state that survives keyed tree updates.

The direct solution is a hierarchical scene description with a small host-owned widget protocol.

## 26. The Presentation Scene IR

Call the normalized form `SceneSpec` and its installed, host-owned form `CompiledScene`.

### 26.1 Scene node shape

A practical normalized node:

```go
type SceneNode struct {
    Key       string
    Kind      NodeKind
    Children  []SceneNode

    Layout    LayoutProps
    Style     StyleRef
    Visual    VisualProps

    Present   *PresentationSpec
    Input     InputProps
    Handlers  HandlerRefs
    Semantics SemanticProps

    Resource  *ResourceRef
}
```

Every node has a stable key within its parent. `Kind` selects a Go-owned protocol implementation. Properties are normalized structs rather than untyped maps in the compiled form.

### 26.2 Core node kinds

Keep the initial vocabulary compact but composable.

| Category | Node kinds | Purpose |
|---|---|---|
| Layout | `row`, `column`, `stack`, `grid`, `padding`, `align`, `spacer`, `scroll`, `virtual-list`, `split` | Compute child constraints and placement. |
| Visual | `text`, `rect`, `border`, `line`, `path`, `image`, `icon`, `canvas`, `clip` | Produce draw operations. |
| Data display | `table`, `tree`, `sparkline`, `bar-chart`, `plot`, `markdown` | Host-owned composite renderers with data contracts. |
| Controls | `button`, `field`, `checkbox`, `radio`, `slider`, `select`, `tabs`, `menu-item` | Standard interaction and focus semantics. |
| PBUI | `present`, `object-face`, `accept-overlay`, `doc-region` | Associate typed objects and semantic interaction with any subtree. |
| Surface anchors | `menu-anchor`, `popover-anchor`, `tooltip-anchor`, `drag-region` | Connect scene geometry to surface manager behavior. |

`canvas` should not be an unrestricted imperative drawing callback. It should contain a data-only list of primitives or reference an immutable host resource. This keeps rendering deterministic and VM-free.

### 26.3 Presentation wrapper

A presentation node can wrap any child:

```js
ui.present(
  { ptype: "player", value: player.id, label: player.name,
    doc: `${player.team} · ${player.pts} PPG` },
  ui.group({
    key: `shot-${shot.id}`,
    children: [
      ui.circle({ cx: shot.x, cy: shot.y, r: 4,
                  class: shot.made ? "shot-made" : "shot-miss" }),
      shot.selected && ui.ring({ cx: shot.x, cy: shot.y, r: 7 })
    ]
  })
)
```

The compiler records the union of visible child bounds after transforms and clipping. The presentation supplies object, documentation, accept compatibility, menu target, and default activation policy. The child supplies its face.

For non-rectangular marks, hit policy can be:

```js
ui.present(obj, mark, { hit: "painted" })
ui.present(obj, mark, { hit: { shape: "circle", cx, cy, r: 8 } })
ui.present(obj, mark, { hit: { path } })
ui.present(obj, mark, { hit: "bounds" })
```

The host compiles these into a spatial hit index.

### 26.4 Immutable snapshots and stable keys

JavaScript renders an immutable tree. A new tree replaces the prior desired tree. Stable keys let the host match nodes across snapshots and retain:

- Measured text and intrinsic size.
- Scroll position.
- Field selection/cursor state when host-owned.
- Layer caches.
- Resource handles.
- Animation state, if later supported.
- Accessibility/focus identity.

A key must be semantically stable, not an array index when rows can reorder. Development mode should warn on duplicate or unstable keys.

### 26.5 Normalization

Normalization occurs on the JS loop immediately after `render()` returns. It should:

- Convert builder objects and plain objects into one schema.
- Validate required fields and ranges.
- Validate ptypes and JSON-serializable values.
- Resolve style class names and resource handles to stable IDs.
- Replace handler functions with runtime-owned handler IDs.
- Stamp the runtime/surface generation.
- Enforce node and depth limits.
- Produce source-coordinate paths for errors, such as `root.children[3].rows[41].cells[2]`.

The normalized snapshot contains no `goja.Value`, function, channel, file descriptor, XID, or Go pointer to script-owned mutable state.

### 26.6 Compilation

Compilation is host-side and may occur on a worker for expensive pure work, provided installation and X resources remain loop-owned. It produces:

```go
type CompiledScene struct {
    Generation uint64
    Root       *CompiledNode
    KeyIndex   map[NodeKey]*CompiledNode
    FocusGraph *FocusGraph
    HitIndex   *HitIndex
    Layers     *LayerTree
    Resources  []ResourceLease
    Size       Size
}
```

A failed compile leaves the previous valid scene installed and emits a script diagnostic. This is essential for live editing: one malformed frame should not blank a bar or modal that the user needs to recover.

## 27. Diffing and invalidation

A retained scene engine is valuable only if it can decide what did not change.

### 27.1 Invalidation classes

Each property belongs to one or more classes:

| Class | Examples | Required work |
|---|---|---|
| Structure | node kind, child list, key | Recompile affected subtree; layout and paint. |
| Layout | text/font metrics, padding, constraints, visibility, table columns | Measure/layout affected ancestors and descendants; paint changed bounds. |
| Paint | color, border, selected state, glyph content at same metrics | Repaint affected layer; no layout if bounds stable. |
| Semantic | ptype/value/doc/verb target, accept compatibility | Rebuild semantic index/overlay; often no base repaint. |
| Input | handler ID, focusable, cursor, drag policy | Rebuild hit/focus metadata; no paint unless state face changes. |
| Resource | image handle generation, font asset | Re-resolve resource; paint and perhaps layout if intrinsic size changed. |

The node implementation declares which fields have which effect. Scripts do not decide invalidation manually.

### 27.2 Layout propagation

If a text label changes width inside a horizontal row, the text node and ancestors up to the nearest constraint boundary become layout-dirty. Siblings may move. A background color change remains paint-dirty at that node. A selected row can repaint its row layer without recomputing column widths.

The compiler should track dependency edges:

```text
child intrinsic size -> parent layout -> sibling positions -> parent bounds
resource intrinsic size -> image measure -> ancestor layout
accept generation -> semantic overlay only
```

### 27.3 Damage accumulation

Paint produces damage rectangles in surface coordinates. Merge rectangles when the additional overdraw is below a threshold; otherwise preserve separate regions. A simple algorithm is sufficient initially:

```text
for each new rect:
    merge with an existing rect if union_area <= 1.4 * sum_area
cap region count at 32; above cap, use bounding box
```

Damage is clipped by scroll and clip nodes. Each retained raster layer receives local damage; clean layers are composited without rerendering.

### 27.4 Semantic overlays

Accept-mode highlighting should not ask every script to rerender and should not repaint full content. The compiled scene already knows presentation regions and ptypes. When broker accept state changes:

1. Increment `AcceptGeneration`.
2. Query presentation regions compatible with accepted types.
3. Damage only the overlay bounds.
4. Paint a host-defined highlight, cursor, or badge layer.

A script may supply style tokens such as `acceptable`, `accept-hover`, and `accept-selected`, but the host applies them. This preserves desktop-wide consistency and turns the current `repaintAllFrames` into small overlay damage.

### 27.5 Text and glyph caches

Text is common in bars, menus, tables, and REPL output. Cache shaping/measurement by `(font, size, text, options)` and raster glyphs or complete short labels as appropriate. Theme color changes should not invalidate geometry. If the renderer stores alpha masks for glyph runs, recoloring can avoid reshaping.

## 28. Presentation types, views, and translators

The current `pbui.Object` contains `Ptype`, JSON value, label, and documentation. This is an effective wire object. A full PBUI system needs a registry around it.

### 28.1 Type descriptor

```go
type PresentationType struct {
    Name        string
    Parents     []string
    Validate    JSONSchemaRef
    DefaultView string
    Views       map[string]ViewDescriptor
    Coercions   []CoercionDescriptor
    URI         URIDescriptor
}
```

Registration can be process-owned and broker-mediated, with a core set supplied by the WM. Type names remain stable slugs. Values remain JSON for wire safety.

### 28.2 Subtyping

Accept compatibility should support more than exact string equality. Examples:

```text
player        <: person
team          <: organization
file-path     <: pathname
git-commit    <: git-object
wm.tile       <: desktop-object
command       <: executable-object
```

A request for `person` should make `player` presentations acceptable. Multiple inheritance should be used cautiously but is valuable for domain types, as CLIM demonstrated. The broker can compute a type lattice from registered descriptors and reject cycles.

Compatibility:

```go
func Accepts(requested []TypeSpec, offered TypeSpec) Compatibility
```

The result can contain exact/subtype/coercion rank. Menus and highlights may show when a coercion will occur.

### 28.3 Coercions and translators

CLIM presentation translators convert an input presentation into another type in context. A process-safe PBUI equivalent is a registered translator:

```go
type Translator struct {
    ID       string
    From     []string
    To       string
    Label    string
    Owner    string
    Priority int
}
```

Examples:

- `player -> team` by selecting the player's team.
- `file-path -> directory` by taking the parent directory.
- `git-commit -> git-ref` by resolving a suitable ref, if available.
- `window -> workspace` by reading its current workspace.

A translator may be pure and broker-executable when expressed as a safe data transform, or owner-executed like a verb. `accept("team")` could allow clicking a player and offer or automatically apply the unambiguous translator, depending on policy.

Do not introduce implicit conversion everywhere initially. Start with subtyping and explicit translator menus, then add opt-in automatic coercion where the user can predict it.

### 28.4 Views

A type can expose named views:

```js
pbui.type({
  name: "player",
  parents: ["person"],
  views: {
    chip: player => ui.playerChip(player),
    row: player => ui.playerRow(player),
    card: player => ui.playerCard(player),
    compact: player => ui.text(player.name)
  }
});
```

The functions execute on the registering runtime to produce normalized scene data, not during host paint. View results can be cached by `(type, value hash, view, theme generation, view options)` if they are declared pure. A surface can request `ui.object(obj, {view: "chip"})`; if no view is registered or the owner is unavailable, the host uses `Label` or a standard JSON face.

For cross-process robustness, consider two view classes:

- **Portable view descriptors:** data templates or host-known view kinds stored by the broker.
- **Owner-rendered views:** asynchronous snapshots produced by a process. They require lifecycle and timeout handling.

Start with core host views and in-process JS views. Add remote owner-rendered views only when a concrete use case justifies the complexity.

### 28.5 Verbs

The existing verb registry already has the right open-world ownership model. Extend descriptors with:

```go
type Verb struct {
    ID          string
    Label       string
    Ptypes      []string
    Accepts     []string
    Owner       string
    Group       string
    Order       int
    EnabledWhen PredicateRef
    Result      *TypeSpec
    Effects     EffectClass
    Shortcut    string
}
```

`EnabledWhen` should remain data/predicate-based or be evaluated asynchronously on the owner loop with caching. Menus must remain responsive if an owner is slow; show disabled/loading state rather than blocking X input.

### 28.6 Object identity and values

JSON values are sufficient for immutable value objects. Some desktop objects represent live entities: a window, surface, REPL cell, or process. Use stable opaque IDs in the JSON value and resolve them through a host/service registry. Never serialize raw pointers or XIDs as authority. An XID may appear as diagnostic data, but operations should address a generation-stamped logical ID such as `window:42@7` so stale references fail safely.
EOF
```

<details><summary>💭 Thinking</summary>

**Wrote detailed sections for UI architecture and document, analyzed images**

</details>

```unknown
bash -lc ls -R /mnt/data/go-go-wm-research | sed -n '1,240p' && echo '--- build excerpt ---' && sed -n '1,280p' /mnt/data/go-go-wm-research/build/build_docx.py
```

<details><summary>💭 Thinking</summary>

**Listed files, inspected functions, analyzed images, and implemented adjustments**

</details>

```unknown
bash -lc set -euo pipefail
python /home/oai/skills/docx/scripts/a11y_audit.py /mnt/data/go-go-wm-research/go-go-wm-handbook.docx --out_json /mnt/data/go-go-wm-research/docx_qa_final/a11y_report.json || true
python /home/oai/skills/docx/scripts/heading_audit.py /mnt/data/go-go-wm-research/go-go-wm-handbook.docx > /mnt/data/go-go-wm-research/docx_qa_final/heading_audit.txt || true
python /home/oai/skills/docx/scripts/images_audit.py /mnt/data/go-go-wm-research/go-go-wm-handbook.docx > /mnt/data/go-go-wm-research/docx_qa_final/images_audit.txt || true
python /home/oai/skills/docx/scripts/style_lint.py /mnt/data/go-go-wm-research/go-go-wm-handbook.docx > /mnt/data/go-go-wm-research/docx_qa_final/style_lint.txt || true
printf '%s\n' '--- a11y ---'
cat /mnt/data/go-go-wm-research/docx_qa_final/a11y_report.json
printf '%s\n' '--- heading audit ---'
cat /mnt/data/go-go-wm-research/docx_qa_final/heading_audit.txt
printf '%s\n' '--- images audit ---'
cat /mnt/data/go-go-wm-research/docx_qa_final/images_audit.txt
printf '%s\n' '--- style lint ---'
cat /mnt/data/go-go-wm-research/docx_qa_final/style_lint.txt
printf '%s\n' '--- integrity ---'
unzip -t /mnt/data/go-go-wm-research/go-go-wm-handbook.docx | tail -n 3
file /mnt/data/go-go-wm-research/go-go-wm-handbook.docx /mnt/data/go-go-wm-research/go-go-wm-handbook.md
sha256sum /mnt/data/go-go-wm-research/go-go-wm-handbook.docx /mnt/data/go-go-wm-research/go-go-wm-handbook.md
stat -c '%n %s bytes' /mnt/data/go-go-wm-research/go-go-wm-handbook.docx /mnt/data/go-go-wm-research/go-go-wm-handbook.md
```

<details><summary>💭 Thinking</summary>

**Ran audits, edited, rebuilt, and analyzed DOCX with image comparison**

</details>


---

> Can I just get a markdown or the docx or something

```unknown
bash -lc cat /home/oai/skills/docx/SKILL.md && printf '\n---FILES---\n' && find /mnt/data/user-x1f8hHS2BvgaqSo6OU6QLJ5x/d6e960e260844774baf8b443bd1d7732/mnt/data/go-go-wm-research -maxdepth 3 -type f | sed 's#^#/##' | head -200
```

<details><summary>💭 Thinking</summary>

**Read and found top-level docx/md files in /mnt/data**

</details>

Here are both formats:

- [Download the Markdown document](sandbox:/mnt/data/go-go-wm-research/go-go-wm-handbook.md)
- [Download the formatted DOCX handbook](sandbox:/mnt/data/go-go-wm-research/go-go-wm-handbook.docx)

```json
{"paths":["files"]}
```

```json
{"paths":["GitHub"],"query":"content"}
```

```json
{"paths":["GitHub"],"query":"tree"}
```

```json
{"paths":["GitHub"],"query":"list"}
```

```json
{"paths":["GitHub"],"query":"search_code"}
```

```json
{"paths":["GitHub"],"query":"directory"}
```

```json
{"paths":["GitHub"],"query":"archive"}
```

```json
{"uri":"/response/turn7","query":"pkg/wmx11","start_line":1,"end_line":19828}
```

```json
{"uri":"/response/turn7","start_line":1,"num_lines":100}
```

```json
{"uri":"/response/turn37","query":"GGWM-001-PBUI-WM","start_line":1,"end_line":12173}
```

```json
{"paths":["GitHub"],"query":"download"}
```

```json
{"uri":"/response/turn7","query":"GGWM-007","start_line":1,"end_line":19828}
```

```json
{"paths":["GitHub"],"query":"branch"}
```

```json
{"paths":["GitHub"],"query":"commits"}
```

# go-go-wm technical handbook

- [Download the handbook — DOCX](sandbox:/mnt/data/go-go-wm-research/go-go-wm-handbook.docx)
- [Download the editable source — Markdown](sandbox:/mnt/data/go-go-wm-research/go-go-wm-handbook.md)

The 74-page document covers:

- X11 window-manager fundamentals: ownership, reparenting, requests versus events, `ConfigureRequest`, synthetic `ConfigureNotify`, ICCCM, EWMH, focus, stacking, and resource lifetimes.
- A code-level review of `go-go-wm`, including the current layout, frame, divider, rendering, MIT-SHM, PBUI client, `uispec`, Goja, focus, and fullscreen paths.
- A step-by-step diagnosis of interactive resize latency. The main problems identified are stale motion processing, durable operations during previews, broad reconciliation, full-window decoration buffers, resize-time SHM churn, and a second full redraw loop in `pkg/apps/xapp`.
- A prioritized implementation plan: latest-wins scheduling, transient resize state, outline/live/adaptive policies, ICCCM-correct configure handling, thin frame chrome, stable buffer capacity, diff-based reconciliation, and affected-subtree layout.
- A retained Presentation Scene IR for JavaScript-defined widgets, with stable keys, invalidation classes, damage tracking, spatial hit testing, presentation wrappers, type-directed verbs, views, translators, input scopes, surface kinds, capabilities, backpressure, resource handles, and transactional hot reload.
- Worked API designs for custom bars, menus, modals, typed tables, basketball shot-chart marks, taskbars, popovers, and PBUI-aware developer tools.
- A repository change map, test strategy, metrics schema, review checklists, and ten staged intern exercises.

The review used the current repository, its mirrored GGWM-001 through GGWM-011 design diaries for 18–20 July, the supplied PBUI prototypes and writing guidance, X11 protocol specifications, and reference implementation patterns from i3, AwesomeWM, and dwm. The public PARC pages were not retrievable in this environment, so their corresponding repository copies were used. Performance conclusions are based on static code-path analysis and the project’s existing profiles; no new live profile was captured on the target machine.

