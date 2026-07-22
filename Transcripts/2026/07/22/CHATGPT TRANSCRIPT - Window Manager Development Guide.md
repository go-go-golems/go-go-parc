# Window Manager Development Guide

- URL: https://chatgpt.com/c/6a602667-4ac0-83ea-af48-ac5d8135a6e8
- Created: 2026-07-22T02:09:44.180Z

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
> ---
>
> focus also heavily on the custom REPL / JS scriptability as building bloks for the OS
>
> Create a markdown document for the output, no docx/pdf .

I’ll synthesize recent project notes, repository hot paths, comparative window-manager designs, and attached materials into a self-contained Markdown chapter with prioritized performance and JS/PBUI architecture plans.

<details><summary>💭 Thinking</summary>

**Listed conversation and recently uploaded files for analysis**

</details>

```unknown
bash -lc rm -rf /mnt/data/go-go-wm && git clone --depth 1 https://github.com/go-go-golems/go-go-wm.git /mnt/data/go-go-wm
```

<details><summary>💭 Thinking</summary>

**Cloned GitHub repository into container**

**Fetched repository metadata and searched recent commits**

</details>

```json
{"open":[{"ref_id":"https://parc.yolo.scapegoat.dev/note/projects/2026/07/18/proj-go-go-wm-building-a-presentation-based-window-manager-in-go"},{"ref_id":"https://parc.yolo.scapegoat.dev/note/research/kb/projects/widget-dsl"},{"ref_id":"https://parc.yolo.scapegoat.dev/note/research/kb/projects/go-go-goja"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searching for cached pages on specific projects**

</details>

```unknown
bash -lc python - <<'PY'
import urllib.request
u='https://parc.yolo.scapegoat.dev/note/projects/2026/07/18/proj-go-go-wm-building-a-presentation-based-window-manager-in-go'
try:
    data=urllib.request.urlopen(u, timeout=30).read()
    print(len(data), data[:100])
    open('/mnt/data/parc.html','wb').write(data)
except Exception as e:
    print(repr(e))
PY
```

<details><summary>💭 Thinking</summary>

**Downloaded HTML using urllib in Python**

</details>

```json
{"open":[{"ref_id":"https://r.jina.ai/http://parc.yolo.scapegoat.dev/note/projects/2026/07/18/proj-go-go-wm-building-a-presentation-based-window-manager-in-go"},{"ref_id":"https://r.jina.ai/http://parc.yolo.scapegoat.dev/note/research/kb/projects/widget-dsl"},{"ref_id":"https://r.jina.ai/http://parc.yolo.scapegoat.dev/note/research/kb/projects/go-go-goja"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 9 websites**

</details>

```json
{"search_query":[{"q":"\"parc.yolo.scapegoat.dev/note/projects/2026/07/18/proj-go-go-wm-building-a-presentation-based-window-manager-in-go\"","domains":["r.jina.ai"]},{"q":"\"parc.yolo.scapegoat.dev/note/research/kb/projects/widget-dsl\"","domains":["r.jina.ai"]},{"q":"\"parc.yolo.scapegoat.dev/note/research/kb/projects/go-go-goja\"","domains":["r.jina.ai"]}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Searching for exact URLs via web queries**

</details>

```json
{"open":[{"ref_id":"https://r.jina.ai/https://parc.yolo.scapegoat.dev/note/projects/2026/07/18/proj-go-go-wm-building-a-presentation-based-window-manager-in-go"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searching the web**

**Searched GitHub for exact slug and repository keywords**

</details>

```json
{"open":[{"ref_id":"https://github.com/go-go-golems/go-go-wm"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

The code’s state-machine refactoring is promising, but resize latency now appears architectural: synchronous rendering and X round-trips remain on the event-loop critical path despite existing optimizations.

<details><summary>💭 Thinking</summary>

**Searched and fetched files from GitHub repository for analysis**

</details>

```json
{"search_query":[{"q":"site:github.com/go-go-golems/go-go-wm/blob/main/pkg/wmcore"},{"q":"site:github.com/go-go-golems/go-go-wm/blob/main/pkg/wmx11"},{"q":"site:github.com/go-go-golems/go-go-wm/blob/main/pkg/pbui"},{"q":"site:github.com/go-go-golems/go-go-wm/blob/main/examples/scripts"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 20 websites**

</details>

```json
{"open":[{"ref_id":"https://github.com/go-go-golems/go-go-wm/tree/main/ttmp?plain=1"},{"ref_id":"https://github.com/go-go-golems/go-go-wm/tree/main/pkg/wmcore?plain=1"},{"ref_id":"https://github.com/go-go-golems/go-go-wm/tree/main/pkg/wmx11?plain=1"},{"ref_id":"https://github.com/go-go-golems/go-go-wm/tree/main/pkg/pbui?plain=1"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searching the web**

</details>

```unknown
bash -lc ls -l /mnt/data/go-go-wm-inputs && wc -l /mnt/data/go-go-wm-inputs/* | sort -n
```

<details><summary>💭 Thinking</summary>

**Listed and counted files in data directory**

**Searched and compared GitHub commits and analyzed changes**

</details>

```unknown
bash -lc printf '%s
' '--- shell headings/components ---'; rg -n "^(export |const |function |class |//|/\*|#)|PBUI|present|accept|menu|modal|taskbar|status|widget|REPL|listener|inspector|command" '/mnt/data/go-go-wm-inputs/pbui-shell(3).jsx' | head -n 240; printf '%s
' '--- basketball headings/components ---'; rg -n "^(export |const |function |class |//|/\*|#)|PBUI|present|accept|menu|modal|taskbar|status|widget|command|timeline|chart|court|play|lineup|inspector" '/mnt/data/go-go-wm-inputs/pbui-basketball.jsx' | head -n 320; printf '%s
' '--- writing skill ---'; sed -n '1,320p' '/mnt/data/go-go-wm-inputs/SKILL(6).md'
```

<details><summary>💭 Thinking</summary>

**Inspected local files, components, and basketball code**

</details>

```json
{"open":[{"ref_id":"https://codeload.github.com/go-go-golems/go-go-wm/zip/refs/heads/main"}],"response_length":"short"}
```

<details><summary>💭 Thinking</summary>

**Searched 8 websites**

</details>

```unknown
bash -lc rm -rf /mnt/data/go-go-wm-main && git clone --depth=1 https://github.com/go-go-golems/go-go-wm.git /mnt/data/go-go-wm-main
```

<details><summary>💭 Thinking</summary>

**Cloned GitHub repository in container**

**Fetched and inspected files and architecture from GitHub repositories**

</details>

```json
{"open":[{"ref_id":"https://raw.githubusercontent.com/go-go-golems/go-go-wm/main/pkg/wmcore/layout.go"}],"response_length":"short"}
```

<details><summary>💭 Thinking</summary>

**Searching the web**

**Organizing code review**

I’m thinking of how to approach reviewing code. I’ll focus on major systems and use GitHub to get key documents, inspecting specific modules, and saving relevant sections for analysis.

**Organized a code review**

</details>

```unknown
bash -lc python - <<'PY'
for w,h in [(1920,1080),(2560,1440),(3840,2160)]:
    b=w*h*4
    print(f'{w}x{h}: {b/1024/1024:.2f} MiB/pass; at 60Hz {b*60/1e9:.2f} GB/s; 3 passes {b*60*3/1e9:.2f} GB/s')
PY
```

<details><summary>💭 Thinking</summary>

**Calculated display bandwidth and memory usage**

</details>

Direct inspection adds two concrete defects: stale MotionNotify events accumulate, and tiled ConfigureRequest triggers full relayout. For scriptability, I’m converging on keyed, retained snapshots with Go-owned validation and resources.

<details><summary>💭 Thinking</summary>

**Fetched file and changelog content for analysis and updates**

**Inspected i3 WM and related module architectures and code**

**Focusing on project analysis**

I’m approaching this by analyzing the last three days of project notes, comparing window manager designs, and reviewing architecture and key features. I will deliver a detailed, educational Markdown document following the user’s specifications.

**Summarizing project notes**

I’m reviewing Go-Go-WM’s repo, focusing on system design, key modules, and recent versions. I’ll describe the architecture, performance fixes, and features like the PBUI Unix-socket broker and JS REPL.

**Focused on project analysis**

**Fetched and inspected source code in repositories**

**Materialized files for programmatic use and storage**

</details>

```unknown
bash -lc wc -l /mnt/data/go-go-wm-inputs/pbui-widget-dsl-intern-guide.md && sed -n '1,220p' /mnt/data/go-go-wm-inputs/pbui-widget-dsl-intern-guide.md
```

<details><summary>💭 Thinking</summary>

**Inspected local guide content and grepped headings for components**

**Researched X Protocol, event queues, and coalescing techniques**

</details>

```json
{"search_query":[{"q":"site:awesomewm.org/doc/api declarative widget system signals awful.widget official"},{"q":"site:docs.qtile.org latest widgets bar command graph official"},{"q":"site:wlroots.pages.freedesktop.org scene graph damage tracking official documentation"},{"q":"site:x.org releases current doc xorg-docs ICCCM ConfigureRequest synthetic ConfigureNotify official"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 29 websites**

**Retrieved GitHub repository and fetched relevant file content**

</details>

```json
{"search_query":[{"q":"Common Lisp Interface Manager II Specification presentations presentation types commands accept official"},{"q":"site:mcclim.common-lisp.dev presentation types command tables accept documentation"},{"q":"Genera Dynamic Windows presentation system command tables documentation"},{"q":"HyperCard scripting model cards buttons fields messages official manual PDF"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 41 websites**

</details>

```unknown
bash -lc ls -l /mnt/data/go-go-wm-inputs && sed -n '1,180p' /mnt/data/go-go-wm-inputs/SKILL\(6\).md
```

<details><summary>💭 Thinking</summary>

**Inspected repository files and executed commands to check status**

**Fetched files and assessed contents from GitHub repository**

</details>

```json
{"open":[{"ref_id":"https://codeload.github.com/go-go-golems/go-go-wm/tar.gz/refs/heads/main"}],"response_length":"short"}
```

<details><summary>💭 Thinking</summary>

**Searched 13 websites**

</details>

```json
{"open":[{"ref_id":"https://github.com/go-go-golems/go-go-wm/archive/refs/heads/main.tar.gz"}],"response_length":"short"}
```

<details><summary>💭 Thinking</summary>

**Searching the web**

</details>

```unknown
bash -lc rm -rf /mnt/data/go-go-wm-src && git clone --depth=1 https://github.com/go-go-golems/go-go-wm.git /mnt/data/go-go-wm-src
```

<details><summary>💭 Thinking</summary>

**Cloned GitHub repository with depth 1**

</details>

```json
{"search_query":[{"q":"site:specifications.freedesktop.org/wm-spec/latest _NET_WM_SYNC_REQUEST resize official"},{"q":"site:specifications.freedesktop.org/wm-spec/latest _NET_WM_STATE_FULLSCREEN _NET_ACTIVE_WINDOW official"},{"q":"site:x.org XSync extension alarm counter official specification resize synchronization"},{"q":"site:tronche.com/gui/x/xlib/events/processing-overview MotionNotify compression XCheckTypedEvent"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 21 websites**

**Inspected Goja repo architecture and searched for runtimeowner package**

</details>

```json
{"search_query":[{"q":"site:parc.yolo.scapegoat.dev/note/projects/2026/07 go-go-wm"},{"q":"site:parc.yolo.scapegoat.dev/note/research/kb/projects/widget-dsl widget dsl"},{"q":"site:parc.yolo.scapegoat.dev/note/research/kb/projects/go-go-goja goja"},{"q":"site:parc.yolo.scapegoat.dev \"GGWM-011\""}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searching specific PARC site pages and project slugs**

**Fetched file content for analysis and inspection**

**Organizing project analysis**

I’m focusing on creating a detailed Markdown document for the user’s project. I’ll compile and analyze the last three days of notes, architecture, and performance metrics, then compare it with other window managers.

**Organized project analysis**

</details>

```json
{"search_query":[{"q":"site:github.com/go-go-golems/go-go-wm \"handleConfigureRequest\""},{"q":"site:github.com/go-go-golems/go-go-wm \"func (w *WM) emitEvent\""},{"q":"site:github.com/go-go-golems/go-go-wm \"func (w *WM) Run\""}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 6 websites**

**Searched GitHub repository for file references**

</details>

```unknown
bash -lc git ls-remote https://github.com/go-go-golems/go-go-wm.git HEAD
```

<details><summary>💭 Thinking</summary>

**Tested git remote connection**

**Fetched and inspected code from GitHub repository for review**

</details>

```unknown
bash -lc sed -n '1,360p' '/mnt/data/go-go-wm-inputs/SKILL(6).md'
```

<details><summary>💭 Thinking</summary>

**Read writing guidelines and inspected methods in PBUI shell files**

**Generated document with citations, evaluated layout, and fetched content**

</details>

```unknown
bash -lc cat > /mnt/data/go-go-wm-engineering-guide.md <<'EOF'
---
title: "Engineering go-go-wm"
subtitle: "A presentation-based window manager, scriptable desktop kernel, and developer workbench"
author: "Architecture and implementation review"
date: 2026-07-21
reviewed_repository: "go-go-golems/go-go-wm"
reviewed_commit: "5b73c9f37c97538f6767ecdc3ece4fb599932377"
project_log_window: "2026-07-18 through 2026-07-20"
---

# Engineering go-go-wm

## A presentation-based window manager, scriptable desktop kernel, and developer workbench

This document explains how to turn `go-go-wm` from a compelling prototype into a responsive, systematically engineered window manager whose user interface can be extended from JavaScript without surrendering correctness, latency, or host control. It is both an implementation review and a design textbook. A new developer should be able to read it from the beginning, understand the responsibilities of an X11 window manager, trace the current resize path, and then follow the proposed architecture into the PBUI widget runtime and REPL.

The central conclusion is direct:

> `go-go-wm` should not become “i3 with scriptable decorations.” It should become a small desktop kernel in which windows, workspaces, commands, results, traces, and widgets are all addressable through typed presentations, while the Go host retains authority over geometry, effects, resources, and scheduling.

That product direction is technically compatible with the strongest parts of the current code. The pure `wmcore` model, operations-as-data, single-owner WM loop, Goja runtime ownership, declarative `uispec`, PBUI broker, and rich-value REPL are the correct foundations. The current performance problem comes from crossing those layers at the wrong granularity during interactive work: one pointer sample can trigger layout, X geometry, full-frame rasterization, buffer replacement, pixel conversion, and client repainting on the same goroutine.

The solution is not another isolated pixel-loop optimization. The solution is to introduce explicit clocks, transactions, retained identity, and load shedding.

---

# 1. Scope, evidence, and reading strategy

## 1.1 What was reviewed

The review was performed against `go-golems/go-go-wm` commit [`5b73c9f`](https://github.com/go-go-golems/go-go-wm/tree/5b73c9f37c97538f6767ecdc3ece4fb599932377), with detailed attention to these areas:

| Area | Principal paths reviewed | Why it matters |
|---|---|---|
| WM ownership and reconciliation | `pkg/wmx11/wm.go`, `manage.go`, `input.go`, `events.go`, `divider.go`, `float.go`, `focus_state.go`, `scripting.go` | Event latency, geometry, focus invariants, X requests, drag behavior, script attachment |
| Pure desktop model | `pkg/wmcore` | Deterministic layout, operations, ratios, tree mutation, serialization |
| Pixel and upload path | `pkg/draw`, `pkg/xshm` | Full-frame work, allocation, conversion, shared pixmaps, cache lifetime |
| PBUI semantics and transport | `pkg/pbui`, `pkg/pbui/broker` | Typed objects, verbs, accept sessions, event routing, process boundaries |
| JavaScript modules | `pkg/jsmod`, `wmmod`, `uimod`, `pbuimod`, `pkg/xgojaprovider` | Goja ownership, snapshots, queues, DSL normalization, host effects |
| Script-defined UI | `pkg/apps/uispec`, `pkg/jsmod/uimod` | Current UI IR, rendering contract, interaction regions, full rerender behavior |
| Rich REPL | `pkg/repl`, `pkg/cmds/replui.go` | Values as presentations, alternate views, evaluation capture, OS-level scripting potential |

The project diary was read for July 18, 19, and 20, 2026 through the repository’s `ttmp/2026/07/.../GGWM-*` ticket corpus. The public PARC page itself was not reliably retrievable from this execution environment, so repository ticket entries, changelogs, and design documents are the source of record used here. Those entries cover GGWM-001 through GGWM-011: the initial PBUI/X11 implementation, Goja DSL, UI module, themes, performance work, MIT-SHM, floating windows, launcher, rich REPL, review fixes, and focus/fullscreen state consolidation.

The attached materials were also treated as design inputs:

- The original PBUI shell sketch establishes the presentation contract, cross-workspace `accept`, type-directed object menus, live collected objects, shell objects as presentations, listener, inspector, trace, and mouse documentation.
- The basketball workbench demonstrates coordinated views, shared selection, comparison through typed input, watchlists, plots, tables, inspectors, and trace surfaces.
- The attached textbook guidance determines the structure of this document: foundational explanation first, concrete code and traces, direct language, and no substitute analogies.

## 1.2 What this document does not claim

This is not a formal proof that every X11 protocol edge case is implemented or missing. The repository is young and changing quickly. Statements about current behavior are tied to the reviewed commit and cited code paths. For protocol features outside those paths, the document uses “not observed in the reviewed implementation” rather than treating absence from one file as proof of absence from the whole repository.

Performance numbers from GGWM-005 and GGWM-006 are historical measurements recorded by the project. The memory-bandwidth calculations later in this document are illustrative lower bounds, not new benchmarks. The first task in the proposed roadmap is therefore measurement, not acceptance of an unverified performance theory.

## 1.3 How to read the document

A developer new to window managers should read Chapters 2 through 7 in order. They build the X11 and ownership model required to understand the review. A developer already comfortable with X11 can start at Chapter 5, which maps the current repository, then continue to the resize analysis in Chapters 7 through 10.

The scripting and PBUI design begins in Chapter 12. The REPL architecture in Chapter 18 depends on the retained widget identity, typed command, capability, and effect concepts developed before it.

---

# 2. The product thesis

## 2.1 Presentation-based UI is a semantic contract

A conventional GUI toolkit starts from controls: buttons, labels, menus, fields, lists. A presentation-based interface starts from an object and a type. The visible face is one rendering of that typed object in a particular context. The same object can be rendered as a compact chip, a table row, an inspector page, a plot point, a menu subject, or a REPL result while retaining the same semantic identity.

The original sketch’s `P` component captures the essential rule:

```jsx
function P({ ptype, value, doc, children, onActivate }) {
  const acceptable = ui.accepting && typeMatches(ui.accepting.ptype, ptype)

  return (
    <span
      className={acceptable ? "pres acceptable" : "pres"}
      onClick={(event) => {
        if (acceptable) {
          ui.accepting.resolve({ ptype, value })
          ui.setAccepting(null)
          return
        }
        if (onActivate) onActivate()
        else ui.openObjectMenu({ ptype, value }, event)
      }}
      onContextMenu={(event) => ui.openObjectMenu({ ptype, value }, event)}
      onMouseEnter={() => ui.setMouseDoc(doc)}
    >
      {children}
    </span>
  )
}
```

The important part is not the React syntax. It is the ordering of semantic decisions:

1. A pending typed input operation gets first refusal.
2. Otherwise the presentation may have a primary activation.
3. Otherwise the object’s applicable commands are available.
4. Hover documentation derives from the same semantic object.
5. Re-presenting the object elsewhere does not remove these behaviors.

That contract should survive the move from the sketch to native X11 surfaces and JavaScript-defined widgets. It should become more explicit, versioned, and secure, but it should not be reduced to hand-wired click callbacks.

## 2.2 The shell itself is part of the object system

The sketch treats tiles and workspaces as presentations. That is more consequential than it first appears. It means shell operations can use the same command acquisition mechanism as application operations:

```text
command: tile.swap
subject: <tile leaf-17>
missing input: <tile>

ACCEPTING <tile> — choose the destination tile
```

The user can satisfy the command by clicking any tile presentation, including one in a different workspace if the interaction policy permits it. No tile picker widget is required. The visible desktop is already an input space.

The same principle extends naturally:

- A managed X client is a `<window>` presentation.
- A process is a `<process>` presentation.
- A workspace is a `<workspace>` presentation.
- A split is a `<split>` presentation.
- A command invocation is a `<command-run>` presentation.
- A profiler sample is a `<frame-sample>` presentation.
- A REPL result is a presentation whose type comes from the result, not from the REPL.

This is why PBUI belongs near the desktop kernel rather than inside one widget toolkit. It defines how semantic objects participate in the desktop.

## 2.3 Coordinated views are a system pattern, not an application trick

The basketball workbench demonstrates a second principle. Clicking a player in a leaderboard changes the shot chart and trend view because those surfaces are projections of shared semantic state. A watchlist re-presents players, teams, and games without turning them into dead text. A radar command can request another `<player>` from any surface. Plot points remain inspectable objects.

The developer desktop should apply the same pattern to its own operation:

```text
selected <window>
    ├── tree view highlights its leaf
    ├── X property inspector shows its ICCCM/EWMH state
    ├── event trace filters to its client and frame windows
    ├── resize profiler shows its most recent geometry transaction
    ├── process view selects its owning PID when known
    └── REPL binds $_selection to a stable reference
```

None of those views should call each other. They subscribe to a shared selection or query model and render the same typed object according to context.

## 2.4 The REPL is a first-class desktop surface

The current rich REPL already points beyond a configuration console. It captures raw JavaScript values, derives presentation types, gives results alternate views, supports `Out(n)` and `$_`, and exposes PBUI verbs. This is the beginning of an interactive desktop kernel interface.

The target is not merely “run JavaScript that calls the WM API.” The target is:

- Queries return stable typed objects, tables, streams, and views.
- Effectful operations produce plans, receipts, traces, and undo information.
- Results can be selected, pinned, compared, dragged, accepted, and re-presented.
- New commands and widgets can be defined live and installed with explicit capabilities.
- Every action is attributable to a runtime, cell, command, revision, and user gesture.

The REPL then becomes the place where the operating environment can be inspected and extended while it is running.

---

# 3. Window-manager fundamentals for a new developer

## 3.1 The X server owns windows; the WM owns policy

In X11, applications and the window manager are clients of the X server. An application creates a top-level window and asks the server to map or configure it. The WM receives selected requests because it has claimed `SubstructureRedirect` on the root window. The WM decides whether, where, and how that top-level window appears.

`go-go-wm` performs the ownership handshake in `pkg/wmx11/wm.go`:

```go
err := root.Listen(
    xproto.EventMaskSubstructureRedirect,
    xproto.EventMaskSubstructureNotify,
    xproto.EventMaskButtonPress,
    xproto.EventMaskFocusChange,
)
```

Only one client can hold the redirect selection for a root window. Failure normally means another WM is active. This is not a lock implemented by the application; it is enforced by the X server.

A basic lifecycle looks like this:

```text
application                     X server                       WM
    |                               |                           |
    | CreateWindow                  |                           |
    |------------------------------>|                           |
    | MapWindow                     |                           |
    |------------------------------>|                           |
    |                               | MapRequest                |
    |                               |-------------------------->|
    |                               |                           | inspect properties
    |                               |                           | create frame
    |                               |                           | save-set + reparent
    |                               |                           | configure client
    |                               |                           | map frame + client
    |                               |<--------------------------|
    |                               |                           |
```

The exact ordering matters. Reparenting, save-set membership, event selection, mapping, focus, and teardown determine whether applications survive WM restart, whether zombie frames remain, and whether events are delivered to the correct callback.

## 3.2 Reparenting separates client content from shell decoration

A reparenting WM creates a frame window and moves the client window underneath it in the X hierarchy. The frame can provide a title strip, border, drag target, buttons, and stacking unit. The client remains responsible for drawing its own content.

The current tiled path creates a frame, reparents the client at the title offset, and removes the client border:

```go
xproto.ChangeSaveSet(conn, xproto.SetModeInsert, clientWin)
xproto.ConfigureWindow(conn, clientWin,
    xproto.ConfigWindowBorderWidth, []uint32{0})
xproto.ReparentWindow(conn, clientWin, frameWin, 0, draw.TitleH)
```

The conceptual geometry is:

```text
frame window
┌──────────────────────────────────────┐
│ title strip / controls               │  TitleH
├──────────────────────────────────────┤
│                                      │
│ client window                        │
│ application draws this area          │
│                                      │
└──────────────────────────────────────┘
```

A crucial performance implication follows: the WM does not need a full-frame pixel buffer for an external client. It only needs to draw the decoration not covered by the child window. The reviewed implementation currently uses a full-frame RGBA image and background pixmap for the frame, even though most pixels are hidden by the client. Chapter 8 explains why this becomes expensive during resize and how to split the surfaces.

## 3.3 Requests are not commands

An application can issue `ConfigureWindow`, but for a managed top-level window the request is a proposal. The WM may honor it, transform it, or reject it. For a tiled window, the tree normally owns geometry. For a floating window, requested geometry may be accepted subject to work-area and size constraints.

When the WM denies a tiled client’s requested geometry, it should report the actual unchanged geometry with a synthetic `ConfigureNotify`. This is part of the ICCCM contract. Re-running a complete layout and repaint merely to reassert the same geometry is unnecessary and can create request/repaint feedback.

The decision should be explicit:

```go
func handleConfigureRequest(ev ConfigureRequest) {
    f := byClient[ev.Window]
    switch {
    case f == nil:
        // Unmanaged or override-redirect: pass through the requested mask.
        configureUnmanaged(ev)

    case f.floating && !fullscreen.Owns(f):
        // The floating layer owns policy but may honor requested fields.
        applyFloatingRequest(f, ev)
        sendSyntheticConfigureNotify(f)

    default:
        // The tree or fullscreen state owns geometry.
        sendSyntheticConfigureNotify(f)
    }
}
```

This is both a correctness rule and a performance rule. Protocol correctness often removes workarounds that would otherwise become hot paths.

## 3.4 Focus is state, protocol, and visual feedback

Keyboard focus has at least three coupled effects:

1. The X server’s input focus changes.
2. `_NET_ACTIVE_WINDOW` and related interoperability state may change.
3. The shell’s visual focus decoration changes.

Floating windows and fullscreen windows make focus more difficult because “focused tiled leaf” is no longer enough to represent the active target. The recent `focusState` work is therefore a strong architectural correction. It represents exactly one focus kind and preserves the tiled leaf to restore after a float or fullscreen surface closes.

A useful invariant is:

```text
At every stable WM-loop boundary:

exactly one of
    no focus,
    tiled leaf focus,
    floating client focus,
    fullscreen focus
is active,

and any restoration target is explicit state rather than an accidental
leftover in another field.
```

The same method should be applied to interaction modes, overlays, keyboard grabs, and accept sessions: encode state machines as types with one owner instead of distributing boolean conventions across event handlers.

## 3.5 Passive grabs and replay preserve application input

A click inside an application window normally goes directly to the application. A click-to-focus WM needs to observe the first click without consuming it. The current code installs a synchronous passive button grab, focuses the frame, and calls `AllowEvents(..., ReplayPointer, ...)` so the original click is replayed to the client.

This pattern illustrates an important WM rule: input policy must preserve application protocol behavior. A WM that focuses correctly but swallows the user’s click is still incorrect from the user’s perspective.

## 3.6 Stacking and transients form another state machine

Tiled frames, floating frames, bars, menus, drag previews, launchers, notifications, and fullscreen windows occupy different stacking bands. A transient dialog should stay associated with its leader. A menu must not disappear under a dialog. A fullscreen client normally owns the output geometry but shell-level emergency or command surfaces may still need a defined policy.

A robust design names these layers:

```text
highest
    emergency / lock / secure prompt
    modal shell overlays
    context menus and tooltips
    fullscreen surface policy layer
    notifications
    floating/transient frames
    tiled frames and internal tiles
    desktop background
lowest
```

Do not rely on the last sequence of `Stack(Above)` calls as the model. Keep a stacking model and reconcile it. This becomes essential once JavaScript can create overlays.

## 3.7 ICCCM and EWMH are compatibility contracts

ICCCM covers core client/WM conventions such as size hints, protocols, focus models, and synthetic configure notifications. EWMH adds desktop, active-window, window-type, state, work-area, fullscreen, close, ping, and synchronization conventions commonly used by modern toolkits.

The current `setupEWMH` advertises a deliberate subset: supporting-WM check, WM name, client list, active window, desktop count/current/names, and per-window desktop. That is enough for early integration but not a complete compatibility target.

A systematic implementation should maintain a table rather than adding atoms reactively:

| Tier | Protocol surface | Reason |
|---|---|---|
| 0: lifecycle | `WM_PROTOCOLS`, `WM_DELETE_WINDOW`, normal hints, synthetic `ConfigureNotify`, save-set, focus | Basic correctness and application survival |
| 1: common desktop tools | client-list stacking, window type, window state, fullscreen, active-window requests, close-window, frame extents, allowed actions, work area | Pagers, panels, dialogs, common GUI toolkits |
| 2: responsiveness | `_NET_WM_PING`, `_NET_WM_SYNC_REQUEST`, demands-attention, user-time | Hung-client detection and paced live resize |
| 3: outputs | RandR changes, per-output work areas, struts, fullscreen monitor selection | Multi-monitor operation |

Each row needs a test client and an expected event/property trace. “Supported” should mean behavior is implemented, not merely that an atom appears in `_NET_SUPPORTED`.

## 3.8 A window manager is not necessarily a compositor

An X11 WM decides placement, focus, stacking, and policy. A compositor redirects window drawing and combines surfaces into output frames, enabling effects, transparency, animation, and damage-driven composition. `go-go-wm` currently draws its own frame and internal-app pixels but is not a general compositor.

This distinction matters for the proposed retained scene graph. The scene graph initially manages only WM-owned surfaces and semantics. It does not require turning `go-go-wm` into a compositor. External client content remains an X child window. A future Wayland port or compositor can reuse the retained scene and PBUI layers while replacing the X11 shell.

---

# 4. A systematic way to build a window manager

A window manager becomes maintainable when each stage has explicit invariants, protocol traces, and failure tests. The following sequence is suitable both for implementation planning and intern education.

## 4.1 Stage 0: define the authoritative model

Before handling X events, define the model that answers:

- Which outputs and work areas exist?
- Which workspaces exist and which output shows each one?
- Which managed clients exist?
- Which clients are tiled, floating, transient, or fullscreen?
- What is focused?
- What is the stacking order?
- What interaction mode is active?

`wmcore.Desktop`, its split tree, and operations are a good start. The next step is to broaden the authoritative model so floating, fullscreen, overlays, outputs, and focus are not side tables with implicit coupling.

The model should be serializable and independently testable. X window IDs can appear as opaque handles at the shell boundary, but the layout and state-transition logic should not require a live display.

## 4.2 Stage 1: claim the root and prove exclusive ownership

Tests:

- Starting with no WM succeeds.
- Starting a second instance fails predictably.
- Shutdown releases ownership.
- A failed startup does not leave sockets or partial state behind.
- `--replace` behavior, if added, has an explicit handshake rather than relying on timing.

A root-ownership failure should be reported before starting brokers, REPLs, or script runtimes that assume a live WM.

## 4.3 Stage 2: implement lifecycle before layout features

Lifecycle operations include map, reparent, unmap, destroy, withdrawal, save-set behavior, and restart adoption. The invariant is:

```text
Every managed client has exactly one live shell record and exactly one frame.
Every frame record points to live X resources or is in a teardown transition.
A client teardown removes callbacks, maps, buffers, focus references, and model membership once.
```

The project has already fixed an important class of bugs here by attaching lifecycle callbacks to client windows and calling `xevent.Detach` during teardown. Continue this discipline with explicit states such as `managing`, `managed`, `withdrawing`, and `destroyed` if asynchronous protocol work grows.

## 4.4 Stage 3: make geometry a transaction

Layout computation should produce an immutable snapshot. Reconciliation should diff the previous and next snapshots, generate X requests, and commit bookkeeping once.

```go
type LayoutSnapshot struct {
    Revision uint64
    Frames   map[FrameID]FrameGeometry
    Dividers map[SplitID]DividerGeometry
    Damage   Region
}

type GeometryDelta struct {
    MoveResizeFrames []FrameChange
    ResizeClients    []ClientChange
    Map              []XWindow
    Unmap            []XWindow
    Restack          []StackChange
}
```

This design prevents unrelated concerns from deciding independently to map, paint, resize, or restack the same window. It also creates a unit-testable representation of what one operation should do to X.

## 4.5 Stage 4: make focus and grabs explicit

Tests should cover:

- Focus tile, float, transient, and fullscreen.
- Close the focused target and restore correctly.
- Switch workspace while a float or fullscreen window is focused.
- Click-to-focus replays the application click.
- A modal shell overlay scopes keyboard and pointer input.
- An aborted drag releases pointer and keyboard grabs.
- Script errors cannot leave a grab active.

The existing `focusState` is the right pattern. Add comparable `interactionState` and `overlayState` owners.

## 4.6 Stage 5: add workspaces and interoperability

Workspace switching is more than changing `Desktop.Current`. It changes mapping, focus, EWMH properties, fullscreen ownership, floating visibility, bar state, and possibly output assignment.

Treat it as one transaction with a trace such as:

```text
workspace.switch revision=184 from=dev to=web
  fullscreen.exit        client=0x3a00007 reason=workspace-switch
  unmap.frame            frame=leaf-17
  unmap.float            client=0x4c00011
  map.frame              frame=leaf-22
  focus.tile             leaf=leaf-22
  ewmh.current-desktop   index=2
  paint.damage           top-bar=[0,0 1920x28]
commit revision=185
```

A trace like this is executable documentation. It also exposes duplicate work immediately.

## 4.7 Stage 6: add floating, transient, and fullscreen policy

Detection must be separate from placement. The current `floatDecision` already follows a useful precedence order: script rule, transient leader, EWMH window type, fixed size. Preserve that separation and add tests for every precedence combination.

Fullscreen should own both geometry and focus through explicit state. The recent `fullscreenState` and `focusState` work demonstrates how to turn review-discovered conventions into testable invariants.

## 4.8 Stage 7: add outputs and dynamic topology

Do not bolt multi-monitor support onto `screen` and `area` scalar fields. Introduce outputs as first-class objects:

```go
type Output struct {
    ID        OutputID
    Name      string
    Geometry  Rect
    WorkArea  Rect
    Scale     Rational
    Transform Transform
    ActiveWS  WorkspaceID
}
```

Then define where workspaces live, how focus crosses outputs, how fullscreen is scoped, and what happens when an output disappears. Output change is a model transaction followed by geometry reconciliation, not a special repaint path.

## 4.9 Stage 8: add an interactive frame scheduler

Pointer motion, animations, client repaint synchronization, and script UI updates require a scheduler. Event handlers should record intent; scheduled commits should perform bounded work. Chapter 9 specifies this in detail.

## 4.10 Stage 9: expose one command graph

Keybindings, launcher entries, context menus, REPL calls, IPC, scripts, and typed PBUI verbs should resolve to the same command definitions. The caller changes; the command’s validation, capability requirements, argument acquisition, effect plan, transaction, and trace do not.

This is where `go-go-wm` can surpass the usual split between configuration API, IPC API, widget API, and internal function calls.

## 4.11 Stage 10: make the shell scriptable through validated descriptions

JavaScript should describe widgets, commands, subscriptions, and effects. The Go host should validate them, assign identities, schedule them, and commit effects. This preserves the interactive power of a live system without executing arbitrary JavaScript on the X event loop.

---
EOF
```

<details><summary>💭 Thinking</summary>

**Created markdown guide and wrote engineering chapters 8-11**

</details>

```unknown
bash -lc cat >> /mnt/data/go-go-wm-engineering-guide.md <<'EOF'
# 13. Target architecture: a small desktop kernel

## 13.1 The kernel is the authority, not the renderer

The target architecture separates authoritative state from its presentations:

```text
                                   ┌───────────────────────────────┐
                                   │      command definitions      │
                                   │ typed inputs · auth · preview │
                                   └──────────────┬────────────────┘
                                                  │ command run
┌──────────────┐  X events  ┌────────────────────▼────────────────────┐
│ X11 backend  │───────────▶│              desktop kernel             │
│ windows/atoms│◀───────────│ model revisions · focus · stack · ops   │
└──────────────┘  X effects │ journal · object registry · selections │
                            └──────────┬───────────────┬───────────────┘
                                       │ snapshots      │ semantic events
                              ┌────────▼─────────┐ ┌────▼─────────────────┐
                              │ scene/render host│ │ PBUI broker/router   │
                              │ widget reconcile │ │ refs · verbs · accept│
                              │ layout · damage  │ │ subscriptions        │
                              └────────┬─────────┘ └────┬─────────────────┘
                                       │ Widget IR       │
                                 ┌─────▼─────────────────▼─────┐
                                 │       runtime manager        │
                                 │ Goja owners · apps · REPL    │
                                 │ capabilities · budgets       │
                                 └──────────────────────────────┘
```

The kernel can operate with a minimal renderer, no JavaScript, and no broker. The renderer can be tested from snapshots. A runtime can crash without invalidating X resources. A broker participant can disappear without corrupting the model.

## 13.2 Proposed package responsibilities

Package names are illustrative; the important part is ownership.

```text
pkg/kernel
    authoritative desktop state
    revisions, command transactions, journal
    focus/stack/interaction/selection state machines
    object registry and snapshot queries

pkg/platform/x11
    root ownership, atoms, client lifecycle, X requests/events
    ICCCM/EWMH, RandR, sync protocol
    no application command policy

pkg/geometry
    layout snapshots, diffs, commit plans, resize sessions

pkg/scene
    retained scene graph, hit testing, layers, damage

pkg/widgets
    Widget IR schema, normalization, reconciliation, layout
    native widget implementations and state store

pkg/pbui
    presentation types, object refs, renderers, typed commands
    accept sessions, semantic router, wire protocol

pkg/runtime
    Goja RuntimeManager, runtime profiles, generations
    capabilities, budgets, event/effect bridge, hot reload

pkg/repl
    kernel protocol, cells, provenance, rich values, streams

pkg/diagnostics
    traces, counters, protocol inspector, performance sessions
```

Do not perform a directory reorganization before the behavioral seams exist. Extract concrete managers one invariant at a time, with tests, then move files when the dependency direction is clear.

## 13.3 The universal path is snapshot → intent → command → transaction

A user action should have one conceptual path regardless of whether it starts in a keybinding, menu, script, bar, REPL, or IPC client:

```text
1. Caller reads an immutable snapshot at revision R.
2. Caller expresses an intent or command with typed object references.
3. Host resolves references and validates capabilities.
4. Missing typed arguments are acquired through accept sessions.
5. Command builds or validates an effect plan.
6. Kernel commits against revision R or applies conflict policy.
7. Kernel emits revision R+1, receipt, semantic events, and damage impact.
8. Views update from the new snapshot.
```

This replaces multiple special paths such as “keybinding calls internal function,” “menu sends verb over broker,” “REPL calls synchronous module method,” and “widget callback mutates closure state then redraws.” Those entry points remain ergonomic, but they lower to one command system.

## 13.4 Revisions make asynchronous scripting tractable

A script may render from revision 120, wait for a user to choose a workspace, and submit an operation after the model reaches revision 128. The host needs an explicit conflict policy:

```go
type CommitRequest struct {
    CommandRun    CommandRunID
    BaseRevision  uint64
    Preconditions []Precondition
    Effects       []Effect
    IdempotencyKey string
}

type ConflictPolicy string

const (
    RejectOnConflict ConflictPolicy = "reject"
    RebaseReferences ConflictPolicy = "rebase-refs"
    LastWriterWins   ConflictPolicy = "last-writer-wins" // restricted uses
)
```

For layout mutations, reject or validate preconditions. For setting a theme, last-writer-wins may be acceptable. For closing a window, resolving a stable reference and checking that it is still live may be sufficient.

A rejected command returns a presentation-rich conflict:

```text
<command-conflict>
  requested at revision 120
  current revision 128
  precondition failed: split-19 no longer contains window-7
  actions: Recompute plan · Inspect changes · Abort
```

## 13.5 Semantic state and visual state are related but distinct

A `<window>` object remains the same semantic object when its title, focus, geometry, or workspace changes. Its visual faces can update independently. Conversely, two visual nodes may present the same object at once.

The architecture therefore keeps:

```text
semantic registry
  ObjectRef → current snapshot, type, provenance, capabilities

presentation instances
  PresentationID → ObjectRef + renderer + context + visual node

widget instances
  WidgetID → component/type/key/local state/resources
```

Do not collapse these IDs. They answer different questions.

---

# 14. Widget IR and custom JavaScript components

## 14.1 The IR must be hierarchical, serializable, and versioned

The current rows and segments can express compact forms but not a complete desktop UI. Widget IR v2 should use a versioned page envelope:

```json
{
  "version": 2,
  "app": "dev-workbench",
  "generation": 14,
  "root": {
    "type": "column",
    "key": "root",
    "props": { "gap": 6, "padding": 8 },
    "children": []
  }
}
```

Every node is plain data:

```go
type WidgetNode struct {
    Type     string          `json:"type"`
    Key      string          `json:"key,omitempty"`
    Props    json.RawMessage `json:"props,omitempty"`
    Children []WidgetNode    `json:"children,omitempty"`
}
```

Normalization converts the wire shape into typed host nodes, validates constraints, assigns IDs, and records source paths for errors.

No JavaScript closure crosses this boundary. Event handlers are referenced by IDs registered with the runtime owner.

## 14.2 Stable keys create retained identity

A component instance ID derives from:

```text
runtime ID
app ID
runtime generation
parent component instance ID
component type
explicit key
```

For a list of windows:

```js
ui.list({
  key: "windows",
  items: windows,
  itemKey: (window) => window.ref.id,
  renderItem: (window) => WindowRow({ key: window.ref.id, window })
})
```

The author must provide keys for reorderable collections. Index keys are acceptable only for fixed, non-stateful sequences. The normalizer should warn when a dynamic collection lacks stable keys.

Identity enables:

- local component state;
- retained text and layout caches;
- focus preservation after rerender;
- incremental updates;
- animation and transition state if later desired;
- exact teardown of subscriptions and resources;
- hot-reload reconciliation.

## 14.3 Components lower to host primitives

A custom JS component is an authoring abstraction, not a new renderer implementation:

```js
const WindowBadge = ui.component("WindowBadge", (props, ctx) => {
  const w = props.window
  const focused = ctx.useSelector(
    wm.selection("focusedWindow"),
    (ref) => ref && ref.id === w.ref.id
  )

  return ui.presentation({
    key: props.key,
    object: w.ref,
    context: "window-badge",
    child: ui.row({
      gap: 4,
      children: [
        ui.icon({ name: w.floating ? "float" : "tile" }),
        ui.text({ text: w.title, weight: focused ? 700 : 400 }),
        ui.text({ text: w.workspace, tone: "muted" })
      ]
    })
  })
})
```

The component function runs on the JS owner and returns Widget IR. The host supports only registered primitive types. This lets scripts compose arbitrarily rich widgets while the host controls layout, paint, input, and cost.

## 14.4 Minimal native primitive inventory

A practical first set is:

| Category | Primitives |
|---|---|
| Layout | `row`, `column`, `stack`, `grid`, `spacer`, `separator`, `scroll`, `clip` |
| Content | `text`, `icon`, `image`, `rect`, `path`, `sparkline` |
| Input | `button`, `field`, `editor`, `toggle`, `select`, `slider` |
| Collections | `list`, `virtualList`, `table`, `tree` |
| Semantics | `presentation`, `commandButton`, `dropTarget`, `mouseDoc` |
| Structure | `componentHost`, `portal`, `focusScope`, `errorBoundary` |
| Feedback | `progress`, `badge`, `tooltipAnchor`, `emptyState` |

Charts should initially be compositions of paths, text, and presentation marks. Specialized high-volume plots can be added when profiles show the generic path is insufficient.

## 14.5 Layout contract

Every node participates in two phases:

```text
measure(constraints) → size requirements
arrange(rect)         → child rectangles and clipping
```

Constraints are explicit:

```go
type Constraints struct {
    MinW, MaxW int
    MinH, MaxH int
    Scale      Rational
}

type MeasureResult struct {
    Min       Size
    Preferred Size
    Max       Size
    Baseline  int
}
```

Do not infer “fill” from magic negative dimensions. Use typed properties:

```js
ui.row({
  width: ui.fill,
  children: [
    ui.text({ text: title, flex: 1 }),
    ui.button({ label: "close", width: ui.content })
  ]
})
```

The first implementation can support row, column, stack, fixed/content/fill sizing, min/max, flex weight, gap, padding, and scrolling. Grid and advanced text flow can follow.

## 14.6 Local state is stored by the host runtime manager

A hooks-like API is feasible if ownership is precise:

```js
const [query, setQuery] = ctx.useState("")
const windows = ctx.useSelector(
  wm.windows(),
  (all) => filterWindows(all, query)
)
ctx.useEffect(() => wm.subscribe("window.*", ctx.invalidate), [])
```

The host stores hook slots under the component instance. JavaScript values in those slots still belong to the runtime and are accessed only on its owner. The render host receives only normalized data.

Rules should be strict:

- Hook order is stable within a component type.
- Effects return disposers.
- Unmount invokes disposers on the runtime owner.
- Async effects receive cancellation tied to component generation.
- State updates after unmount are ignored and traced.
- A component render has an execution budget.

A simpler signal API may be easier initially:

```js
const query = ui.signal("")
query.set("firefox")
query.get()
```

The architecture requirement is retained identity, not a particular React-compatible syntax.

## 14.7 Event references and generations

Normalized nodes refer to handlers like this:

```json
{
  "type": "button",
  "key": "close",
  "props": {
    "label": "close",
    "onAction": {
      "runtime": "desktop-app:taskbar",
      "generation": 14,
      "handler": 87
    }
  }
}
```

When an event arrives:

1. The host checks that the runtime and generation are live.
2. The host creates an immutable event payload with stable object refs.
3. The host posts the handler invocation to the runtime owner.
4. The handler returns or emits declarative effects.
5. Stale generation events are discarded with a diagnostic counter.

This prevents a click queued before hot reload from invoking a callback in the new runtime with incompatible state.

## 14.8 Event routing

Widget events need a precise route. Use capture, target, and bubble phases where hierarchical interception is useful:

```text
surface root capture
  → focus scope capture
    → scroll/list capture
      → presentation target
    ← bubble through ancestors
```

Event payload:

```go
type UIEvent struct {
    ID             EventID
    Type           UIEventType
    Phase          EventPhase
    Surface        SurfaceID
    Target         WidgetID
    Presentation   *PresentationID
    Object         *ObjectRef
    Position       Point
    LocalPosition  Point
    Button         int
    Modifiers      Modifiers
    Key            string
    Text           string
    Timestamp      time.Time
    LayoutRevision uint64
}
```

Default behaviors—focus, scrolling, button press visuals, presentation menus, accept acquisition—belong to host widget semantics. A script may prevent or augment them only where the widget contract allows it.

## 14.9 Hit testing comes from arranged nodes

The renderer and input router must use the same geometry. Do not have each widget separately emit ad hoc `Region` rectangles after rasterization.

Each arranged node contributes:

```go
type HitNode struct {
    WidgetID       WidgetID
    Rect           Rect
    Clip           Region
    Z              int
    PointerEvents  PointerPolicy
    Presentation   *PresentationID
    Cursor         CursorKind
    MouseDoc       PresentationSpec
}
```

The index returns the topmost eligible node. Presentation semantics are attached to that node and survive changes in visual face.

## 14.10 Virtualization is mandatory for developer tools

Window lists may be small, but event traces, REPL notebooks, process tables, logs, protocol traces, and datasets can be large. `virtualList` and `table` should be early primitives, not later optimizations.

The host owns:

- visible range calculation;
- overscan;
- row height estimates and corrections;
- stable selection and focus for off-screen items;
- lazy presentation registration;
- recycling or retaining item instances according to key policy.

A script supplies data references and row components. It should not create ten thousand widget nodes when twenty are visible.

## 14.11 Error boundaries produce presentations

A component error should replace the failed subtree with an `<ui-error>` presentation containing:

- runtime/app/component identity;
- source file and stack where available;
- last event or state update;
- generation and render revision;
- actions: retry, reload app, open in REPL, inspect trace, disable app.

The rest of the desktop remains usable. An error surface should be host-rendered so it does not depend on the failing runtime.

## 14.12 Compatibility with `uispec`

A v1 adapter can map:

```text
row          → row
text/hint    → text with tone
button       → button action reference
object       → presentation
field        → field
image        → image
simple table → table
```

Existing rich REPL views can migrate incrementally. New components use v2 directly.

---

# 15. PBUI as the semantic layer

## 15.1 Presentation types need a registry

A presentation type should define more than a string name:

```go
type PresentationType struct {
    Name       string
    Version    uint32
    Parents    []TypeRef
    Schema     JSONSchema
    Summary    RendererRef
    Describe   RendererRef
    Faces      map[PresentationContext]RendererRef
    Canonicalize CanonicalizerRef
}
```

The registry answers:

- Is a value valid for this type?
- Does type A satisfy a request for type B?
- How is it summarized or described?
- Which face is used in a title, menu, table, REPL, or inspector?
- Which commands accept it?
- How is an inline value canonicalized for equality or references?

Registration may come from Go, a trusted script, or a remote provider. Namespaces and versions prevent accidental collisions.

## 15.2 Type matching should support a controlled lattice

Current exact matching plus `any` proves the idea. Add declared parent relationships:

```text
window
  ├── tiled-window
  ├── floating-window
  └── transient-window

shell-object
  ├── workspace
  ├── split
  ├── tile
  └── output

numeric
  ├── integer
  ├── duration
  ├── ratio
  └── byte-size
```

A request for `<window>` accepts any declared subtype. A request for `<numeric>` does not automatically accept arbitrary JavaScript numbers unless they are presented under a compatible type.

Avoid arbitrary script predicates in the broker’s hot matching path. If refinement predicates are needed, normalize them into bounded host-evaluable constraints:

```json
{
  "type": "window",
  "where": { "floating": false, "workspace": "dev" }
}
```

## 15.3 Presentation methods are context-sensitive

The same object needs different faces:

```text
compact-chip      “Firefox · web”
table-cell        “Firefox”
window-title      icon + title + modified/urgent state
menu-subject      title, class, workspace, thumbnail
inspector         all known fields and protocol properties
repl-result       summary plus selectable alternate views
mouse-doc         “<window> Firefox — L: focus · R: commands”
```

A face is a renderer selected by `(ptype, context, theme, capabilities)`. It returns Widget IR, not pixels or a JavaScript callback to run during paint.

## 15.4 Object references preserve identity and provenance

A reference should include enough information to resolve safely:

```json
{
  "namespace": "wm/session-2026-07-21T14:03:11Z",
  "type": "window",
  "id": "client:0x04c00011",
  "version": 38,
  "generation": 1
}
```

A resolved snapshot might be:

```json
{
  "ref": { "...": "..." },
  "title": "go-go-wm — trace",
  "class": "kitty",
  "workspace": "dev",
  "leaf": "leaf-17",
  "geometry": { "x": 18, "y": 42, "w": 942, "h": 1010 },
  "focused": true,
  "floating": false,
  "revision": 184
}
```

Provenance identifies producer, command run or REPL cell, source revision, and capability context. This becomes important when an object is collected into notes or a watchlist and used later.

## 15.5 Commands are typed objects with acquisition plans

A command definition should be data:

```go
type Command struct {
    ID            CommandID
    Label         string
    Documentation PresentationSpec
    Subject       TypeConstraint
    Inputs        []CommandInput
    Availability  PredicatePlan
    Preview       PreviewHandlerRef
    Execute       ExecuteHandlerRef
    Capabilities  CapabilitySet
    UndoPolicy    UndoPolicy
}

type CommandInput struct {
    Name         string
    Accepts      TypeConstraint
    Prompt       PresentationSpec
    Optional     bool
    Default      DefaultPlan
    Multiple     bool
}
```

Example JavaScript registration:

```js
pbui.command({
  id: "window.move-to-workspace",
  label: "Move to workspace…",
  subject: "window",
  inputs: [
    {
      name: "workspace",
      accepts: "workspace",
      prompt: ({ subject }) =>
        ui.text(`Move ${subject.label} to which workspace?`)
    }
  ],
  capabilities: ["wm.mutate"],
  run({ subject, workspace, snapshot }) {
    return wm.effects([
      wm.effect.moveWindow({
        window: subject.ref,
        workspace: workspace.ref,
        baseRevision: snapshot.revision
      })
    ])
  }
})
```

The command can be invoked from a window menu, REPL, launcher, keyboard binding, taskbar, or script. Missing inputs enter typed acquisition.

## 15.6 Accept is continuation state

`accept(type, prompt)` is ergonomic, but the underlying model is a paused command run with a missing argument. Store that continuation in the host:

```text
command run 91
  subject = <window client:0x4c00011>
  workspace = missing; accepts <workspace>
  state = acquiring(workspace)
```

When the user clicks a compatible presentation, the host validates the reference, fills the argument, and resumes the command handler on its runtime owner. If the runtime was reloaded or closed, the session ends with a stale-continuation result rather than invoking an invalid closure.

This model also supports:

- multiple arguments acquired in sequence;
- optional defaults;
- collection of several objects;
- nested commands;
- alternate acquisition surfaces such as searchable pickers;
- cancellation and timeout;
- command previews before commit.

## 15.7 Object menus are command queries

An object menu should not be assembled by a switch statement such as `actionsFor(ptype, value)`. It is the result of querying the command registry:

```text
query:
  subject = <window>
  context = object-menu
  runtime capabilities = {...}
  model revision = 184

result:
  Focus
  Move to workspace…
  Toggle floating
  Fullscreen
  Inspect
  Watch
  Close
```

Availability can depend on current state. The query returns disabled commands with reasons where useful:

```text
Tile split…   disabled: window is floating
```

Menus remain useful even though commands can also be invoked through accept or REPL. The menu provides discovery; typed acquisition provides composition.

## 15.8 Semantic selection is global but scoped

The developer workbench needs shared selection. Define named selection channels:

```text
focus.window        singleton, follows keyboard focus
inspect.primary     singleton, user-controlled
compare.windows     ordered set, max N
watch.objects       persistent set
trace.filter        query expression
```

A view may publish to or subscribe from a channel. Cross-view coordination occurs through typed selection state, not direct calls.

Selections should contain `ObjectRef`s. When a reference becomes stale, the selection retains a tombstone presentation until the user removes it or a policy expires it.

## 15.9 The protocol must remain bounded

PBUI v2 envelopes should retain strict limits:

- maximum frame bytes;
- maximum nesting depth;
- maximum object inline payload;
- maximum command inputs and menu results;
- maximum Widget IR nodes per update;
- bounded strings and documentation;
- explicit binary/resource transfer rather than base64 blobs in normal messages;
- per-client send queue and rate budgets;
- schema version and feature negotiation.

Large data stays behind stable references or resource handles. A presentation is not a license to serialize the whole world into every event.

## 15.10 Semantic accessibility follows naturally

Because a presentation already has type, object, label, documentation, commands, focusability, and state, it can provide an accessibility tree more reliably than pixel-only custom widgets.

A future accessibility adapter can expose:

```text
role: window item
name: “Firefox”
description: “workspace web, tiled, focused”
actions: focus, move, close, inspect
selected: true
```

This should influence the IR now: labels, roles, focus order, state, and action names must be first-class data, not inferred from pixels.

---

# 16. Bars, menus, modals, taskbars, and overlay surfaces

## 16.1 These are scene roots with shell policies

A top bar, context menu, modal, taskbar, tooltip, notification, and launcher can all render Widget IR, but they differ in placement, stacking, focus, input grabs, lifetime, and security. Model those policies separately from their widget content.

```go
type SurfaceSpec struct {
    Kind          SurfaceKind
    Layer         Layer
    Anchor        AnchorSpec
    Size          SizePolicy
    FocusPolicy   FocusPolicy
    PointerPolicy PointerPolicy
    KeyboardGrab  GrabPolicy
    Dismiss       DismissPolicy
    Scope         ScopeID
    Owner         OwnerRef
    Root          WidgetNode
}
```

The script describes `Root` and requests a permitted surface policy. The host creates X windows, enforces work area and stacking, routes input, and cleans up resources.

## 16.2 Top bars and taskbars reserve geometry explicitly

A bar should register a strut/work-area claim in the kernel rather than relying on hard-coded `BarH` arithmetic:

```go
type EdgeReservation struct {
    Surface SurfaceID
    Output  OutputID
    Edge    Edge
    Size    int
    Priority int
}
```

The output work area derives from active reservations. This prepares EWMH `_NET_WORKAREA` and `_NET_WM_STRUT_PARTIAL` interoperability and allows script-defined bars without corrupting tiled geometry.

Example JavaScript:

```js
ui.surface({
  id: "developer-topbar",
  kind: "bar",
  layer: "shell",
  anchor: { output: "focused", edge: "top" },
  reserve: 30,
  capabilities: ["ui.bar"],
  content: TopBar()
})
```

A taskbar item should be a `<window>` presentation. A workspace chip should be a `<workspace>` presentation. The bar does not implement separate menu logic; it queries commands for those objects.

## 16.3 Context menus use portals and focus scopes

A presentation requests a menu at a root coordinate. The host:

1. Queries applicable commands.
2. Builds a host or script-rendered menu surface.
3. Places it within output bounds.
4. Creates a focus scope.
5. Installs pointer/keyboard grab policy.
6. Routes arrow keys, type-ahead, Enter, and Escape through native menu semantics.
7. Invokes the selected command.
8. Dismisses and releases grabs through one cleanup path.

JavaScript may customize item faces or contribute commands. It should not manually grab the pointer or create override-redirect windows.

Submenus are child overlay scopes with explicit parent relationships. Avoid asynchronous menu population that reorders the item under the pointer without policy; use placeholders or stable sections.

## 16.4 Modals are command continuations with a surface

A modal often gathers structured input that is not efficiently acquired by clicking existing presentations. It still belongs to a command run:

```text
command run: workspace.create
missing inputs:
  name <string>
  output <output> optional
  template <workspace-template> optional

acquisition surface: modal form
```

The modal’s submit action returns typed values to the continuation. Cancellation aborts the command run. Authorization is evaluated when the final plan commits, not merely when the modal opens.

Modal focus must be scoped. Global WM emergency keys and secure actions remain host-controlled. A script modal cannot intercept a configured escape hatch unless explicitly trusted.

## 16.5 Tooltips and mouse documentation are different

Mouse documentation is a persistent shell line explaining the object and available interaction. A tooltip is a transient overlay near the pointer. Both can derive from the same presentation metadata, but they have different timing and placement.

Preserve the Genera/CLIM-inspired mouse-documentation line because it exposes semantic state without requiring hover delay. It is especially valuable during accept mode:

```text
ACCEPTING <workspace> — L: choose “web” · R: workspace commands · Esc: abort
```

## 16.6 Notifications are typed objects, not only strings

A notification can carry a subject, command actions, urgency, lifetime, and provenance:

```js
ui.notify({
  subject: buildRun.ref,
  summary: "Build failed",
  body: "pkg/wmx11: TestResizeCoalescing",
  urgency: "high",
  actions: ["build.open-log", "build.rerun"]
})
```

The notification itself becomes a `<notification>` presentation and can be collected into a trace or history surface.

## 16.7 A worked taskbar design

```js
const Taskbar = ui.component("Taskbar", (_, ctx) => {
  const windows = ctx.useSelector(
    wm.windows({ workspace: wm.currentWorkspace() }),
    (snapshot) => snapshot.windows
  )

  return ui.row({
    key: "taskbar",
    gap: 2,
    children: windows.map((w) =>
      ui.presentation({
        key: w.ref.id,
        object: w.ref,
        context: "taskbar-item",
        onActivate: ctx.handler(() =>
          wm.command("window.focus", { subject: w.ref })
        ),
        child: ui.buttonFace({
          label: w.title,
          icon: w.icon,
          state: {
            focused: w.focused,
            urgent: w.urgent,
            floating: w.floating
          }
        })
      })
    )
  })
})
```

The script decides composition. The host provides the window snapshot, presentation semantics, command execution, button behavior, title rendering, focus state, and resource limits.

---

# 17. Effects, capabilities, budgets, and hot reload

## 17.1 Handlers return effects, not host pointers

A handler should return or emit declarative effects:

```js
return effects.batch([
  effects.wm.command("window.move-to-workspace", {
    subject: windowRef,
    workspace: workspaceRef,
    baseRevision: event.modelRevision
  }),
  effects.selection.set("inspect.primary", windowRef),
  effects.ui.closeSurface(menuSurfaceRef)
])
```

The host validates and executes the batch. Effects have IDs and receipts:

```go
type EffectReceipt struct {
    EffectID       EffectID
    CommandRun     CommandRunID
    Status         EffectStatus
    Started        time.Time
    Completed      time.Time
    BaseRevision   uint64
    CommitRevision uint64
    Result         []Object
    Error          *PresentedError
    Undo           *UndoToken
}
```

Receipts are presentations and appear in the REPL, trace, or inspector.

## 17.2 Use asynchronous calls for interactive work

Synchronous `wm.tree()` and `wm.apply()` are convenient in a startup script and REPL. Widget handlers should prefer promises backed by asynchronous command requests. The runtime remains free to process cancellation, UI state, and other events while the WM commits.

```js
const receipt = await wm.execute({
  command: "window.toggle-floating",
  subject: windowRef,
  baseRevision: event.modelRevision
})
```

The native module starts work outside the Goja owner as required, then posts promise resolution back through `RuntimeServices`. No promise resolver is called from an arbitrary goroutine.

## 17.3 Capability sets are granular and contextual

Example capabilities:

```text
wm.read.windows
wm.read.tree
wm.read.protocol-properties
wm.mutate.layout
wm.mutate.focus
wm.mutate.close
wm.register.keys.global
wm.register.commands
process.spawn
process.inspect
ui.surface.tile
ui.surface.bar
ui.surface.overlay
ui.surface.modal
pbui.register.type
pbui.register.command
pbui.resolve.foreign
fs.read.scoped
fs.write.scoped
network.connect
clipboard.read
clipboard.write
notifications.post
```

Capabilities can include constraints:

```json
{
  "capability": "process.spawn",
  "allow": ["kitty", "firefox", "/usr/bin/make"],
  "maxConcurrent": 4
}
```

The desktop configuration can be fully trusted. Installable widgets should request a manifest and receive user or administrator approval. A REPL session can escalate through an explicit prompt whose decision is itself traced.

## 17.4 Budgets are separate from permissions

A runtime may have permission to render a table and still exceed resource limits. Define budgets:

```go
type RuntimeBudget struct {
    MaxOwnerTask        time.Duration
    MaxRenderTask       time.Duration
    MaxIRNodes          int
    MaxIRDepth          int
    MaxStringBytes      int
    MaxInlineImageBytes int
    MaxQueuedEvents     int
    MaxEffectsPerSecond int
    MaxRendersPerSecond int
    MaxTimers           int
    MaxSubscriptions    int
    MaxSurfacePixels    int64
    MaxCachedBytes      int64
}
```

Enforcement behavior should be explicit:

- Reject an oversized update and preserve the last valid UI.
- Replace the failed subtree with an error presentation.
- Coalesce excessive invalidations.
- Interrupt an overlong JS task where the Goja/runtime facilities permit it.
- Disable a repeatedly failing runtime after a policy threshold.
- Never freeze the WM loop while deciding how to handle a script budget violation.

## 17.5 Subscription APIs should be declarative and coalesced

Avoid generic event listeners that receive the entire event stream and call `wm.tree()` after each event. Provide selectors:

```js
const sub = wm.subscribe({
  select: wm.windows({ workspace: "current" }),
  fields: ["ref", "title", "focused", "urgent", "workspace"],
  delivery: "latest",
  maxRateHz: 30,
  onChange: ctx.handler((snapshot) => windowsSignal.set(snapshot))
})
```

The host can use impact metadata to update only subscribers affected by a command. A subscription receives a new revision even if its selected value is unchanged only when requested for audit purposes.

## 17.6 Hot reload is a generation transition

Reload sequence:

```text
1. Parse/build a new runtime or app generation in isolation.
2. Run initializers and normalize command/type/widget registrations.
3. Render and validate initial surfaces within budgets.
4. Atomically switch active generation.
5. Reconcile compatible component keys and migrate declared state.
6. Reject queued events referencing the old generation.
7. Dispose old subscriptions, timers, surfaces, handlers, and resources.
8. Close the old runtime after outstanding cancellable work ends or times out.
```

Do not mutate a live runtime in place and hope all callbacks now point to the new definitions. Generation boundaries make stale work detectable.

State migration should be opt-in:

```js
ui.app({
  id: "taskbar",
  stateVersion: 3,
  migrate(oldState, oldVersion) { ... }
})
```

Host-owned semantic selections and object references survive reload independently of component-local state.

## 17.7 Trusted and untrusted code should not share one VM

A failure, infinite loop, prototype mutation, or leaked global in one app should not corrupt all script UI. Use one runtime per installed app or trust domain, with the trusted desktop configuration in its own runtime. Shared libraries are loaded separately or through immutable module factories.

Runtime isolation has a cost. Bars composed from many tiny widgets can either:

- host each third-party widget in its own runtime and combine their Widget IR under a host bar;
- group widgets from one trusted package in one runtime;
- use subprocess runtimes for stronger isolation when needed later.

The semantic and Widget IR protocols make these choices possible because rendering does not depend on shared JavaScript objects.

## 17.8 Secure prompts are host-owned

Capability escalation, lock screens, credential prompts, and confirmation for destructive commands must use host-owned surfaces and input policies. A script may request them and provide explanatory content, but it cannot render a visually indistinguishable authorization surface with the same trust mark.

Reserve a secure layer and visual identity. This is a future-facing requirement that is cheap to encode in the surface policy now and difficult to retrofit after scripts can create arbitrary topmost modals.

---
EOF
```

The finalized handbook adds synthetic ConfigureNotify handling, shared scheduling for WM and xapp surfaces, and a supervised REPL-as-shell model with transactions, hot reload, capabilities, and diagnostics.

<details><summary>💭 Thinking</summary>

**Wrote widget architecture chapters and checked document word count**

</details>

```json
{"search_query":[{"q":"site:x.org/releases/current/doc/xorg-docs/icccm ICCCM ConfigureNotify ConfigureRequest"},{"q":"site:specifications.freedesktop.org/wm-spec latest _NET_WM_SYNC_REQUEST"},{"q":"site:awesomewm.org apidoc widget::layout_changed widget::redraw_needed"},{"q":"site:docs.qtile.org latest command graph widgets bars"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 36 websites**

</details>

```unknown
bash -lc cat >> /mnt/data/go-go-wm-engineering-guide.md <<'EOF'
# 21. Prioritized roadmap

## 21.1 The first twelve changes

The order below maximizes responsiveness and architectural leverage while limiting rewrite risk.

| Priority | Change | Why now | Completion evidence |
|---:|---|---|---|
| 1 | Add resize-session metrics and event-age tracing | The next changes need measured baselines and regression evidence | A `<resize-session>` record reports received/applied samples, stage timings, X request counts, pixels, and surface churn |
| 2 | Add outline resize as the default mode | It immediately removes client and raster cost from the drag loop | Divider tracks current pointer; only one final client geometry commit occurs |
| 3 | Replace timestamp gating with latest-sample scheduling | It removes stale-pointer lag in both outline and live modes | Applied sample age stays within one scheduler interval under event bursts |
| 4 | Replace tiled ConfigureRequest relayout with synthetic notification | It removes unnecessary full reconciliation and fixes protocol behavior | Protocol test observes one synthetic `ConfigureNotify` and no layout/paint |
| 5 | Split layout computation from geometry, visibility, and paint reconciliation | It gives all subsequent work a precise transaction boundary | Ratio drag issues only geometry effects declared by a layout diff |
| 6 | Make frame/divider synchronization idempotent | It removes repeated map/paint requests and creates testable managers | Repeating the same snapshot records zero X effects |
| 7 | Move external-client decoration into a title child plus solid frame border | It removes full-pane WM pixel work from the common path | External frame has no full-content RGBA/SHM buffer |
| 8 | Replace goroutine-per-event emission with a sequenced outbox | It bounds event work and preserves source order | Burst test shows stable sequence and explicit drop/backpressure behavior |
| 9 | Introduce hierarchical Widget IR v2 with a v1 adapter | It enables custom bars, menus, modals, and retained identity without breaking current scripts | Existing `uispec` apps render through the adapter; v2 keyed component survives reorder |
| 10 | Add stable PBUI object references and typed command definitions | It fixes REPL identity and unifies menus, launcher, keys, scripts, and accept | One command can be invoked through menu, REPL, keybinding, and IPC with the same receipt |
| 11 | Add RuntimeManager profiles, generations, capabilities, and budgets | It makes third-party or live-defined widgets supportable | Reload rejects stale events; app failure does not affect trusted config or WM |
| 12 | Upgrade the REPL to stable cells, effect plans, streams, and mounted components | It turns the existing rich REPL into the desktop’s development/control surface | A cell defines a widget, mounts it, inspects its surface, commits a WM plan, and receives a traceable receipt |

## 21.2 Phase 0: baseline and safety rails

Deliverables:

- A benchmark manifest with deterministic layouts, clients, resolutions, and pointer traces.
- Structured WM-loop task timing.
- Resize session counters and sample-age measurement.
- Recording X effect backend.
- Protocol tests for ConfigureRequest behavior.
- Architecture tests that Goja is never entered on the WM owner.
- A protocol capability matrix generated from code/test registrations.

Exit criteria:

- Current behavior can be reproduced and compared automatically.
- Every resize commit can be attributed to an input sample and epoch.
- The test suite detects duplicate geometry/map/divider effects.

## 21.3 Phase 1: responsive resize

Deliverables:

- Explicit `interactionState` for divider resize.
- Latest-wins motion samples and scheduler ticks.
- Outline helper/preview surface.
- Final exact commit on release.
- Config and JS command to choose outline/live/adaptive mode.
- Geometry-only live mode behind an experimental flag.
- Synthetic ConfigureNotify for denied tiled requests.

Exit criteria:

- Outline mode remains responsive with an intentionally slow client.
- Release, Escape, client destruction, and workspace switch release all grabs and previews.
- Live mode never commits more than once per frame tick.
- The final ratio matches the release coordinates and snap policy.

## 21.4 Phase 2: geometry transactions and decoration separation

Deliverables:

- `LayoutSnapshot` and `GeometryDelta`.
- Idempotent geometry/visibility/stack reconcilers.
- Title child window and frame-background border for external clients.
- Distinct internal content host.
- Dirty EWMH and bar state.
- Incremental divider manager.
- Adaptive live resize and optional XSync pacing.

Exit criteria:

- No external-client frame owns a pane-sized WM bitmap.
- A ratio tick emits only changed frame/client/divider requests.
- Unchanged visible frames are not remapped.
- Surface churn metrics remain zero for external content during resize.

## 21.5 Phase 3: retained scene and Widget IR v2

Deliverables:

- Scene nodes, layers, per-surface damage, and hit-test index.
- Layout versus paint invalidation.
- Widget IR v2 normalizer and schema.
- Stable keys/component instances.
- Core layout/content/input primitives.
- `uispec` v1 adapter.
- Virtual list/table.
- Portal, focus scope, and error boundary.
- Latest-wins render jobs with stale-result rejection.

Exit criteria:

- Hover repaints only affected bounds and performs no layout.
- Reordering keyed rows preserves local state and focus.
- A 100,000-row data source creates only the visible widget instances.
- A failing component is replaced by a host-rendered error presentation.

## 21.6 Phase 4: PBUI v2 and one command graph

Deliverables:

- Namespaced, versioned presentation type registry.
- Stable `ObjectRef` with resolver and tombstone behavior.
- Context-specific presentation faces.
- Typed command definitions, availability, preview, effect plan, and receipt.
- Scoped accept sessions and command continuations.
- Object-menu command queries.
- Selection channels and watchlists.
- Protocol negotiation and v1 compatibility bridge.

Exit criteria:

- The same `<window>` ref is presented in a taskbar, table, inspector, trace, and REPL.
- Selecting it in one view updates all subscribed coordinated views.
- A command with two missing typed inputs can be completed across surfaces and workspaces.
- Disconnecting the object provider yields an explicit stale presentation.

## 21.7 Phase 5: scriptable shell surfaces

Deliverables:

- Surface policy API for bars, taskbars, menus, modals, tooltips, notifications, and overlays.
- Layer/stack reconciler.
- Edge reservations and output work areas.
- Host-owned menu keyboard/pointer behavior.
- Modal command forms.
- Secure surface layer and capability prompts.

Exit criteria:

- A JavaScript taskbar and menu bar can replace built-in versions without direct X access.
- Context menus never leak grabs and cannot appear outside output bounds.
- A script modal cannot intercept the host emergency key.
- Bar reservations update layout and EWMH work area consistently.

## 21.8 Phase 6: runtime isolation and live development

Deliverables:

- Runtime profiles and per-app owner instances.
- Capability manifests and constrained grants.
- Execution/IR/event/effect/surface budgets.
- Generation-based hot reload.
- Disposer tracking.
- Declarative selectors and coalesced subscriptions.
- Package export/import path.

Exit criteria:

- Reload is atomic and stale callbacks are discarded.
- A runaway app can be interrupted or disabled without freezing the WM.
- Closing a runtime removes every owned command, surface, timer, subscription, and handler.
- Third-party app capabilities are visible as an inspectable object.

## 21.9 Phase 7: REPL kernel and developer workbench

Deliverables:

- Stable cell/output IDs and cell-scoped console.
- Multiline editor, completion, cancellation, and runtime restart.
- Snapshot versus live outputs.
- Async progress and stream cells.
- Effect plans, conflict presentations, receipts, and undo tokens.
- Live component definition/mounting.
- Coordinated window/tree/trace/profiler/inspector workbench.
- Experiment-to-package export.

Exit criteria:

- Equal values from different cells remain distinguishable.
- A long history renders only visible cells.
- A command plan can be inspected and committed against a revision.
- A mounted component can be traced to its source cell and exported.

## 21.10 Protocol and platform work that should proceed in parallel

Maintain a separate compatibility track:

- ICCCM focus models, `WM_TAKE_FOCUS`, normal hints, withdrawal, manager selection.
- EWMH state and client messages, stacking list, work area, frame extents, ping, sync request.
- RandR output topology and dynamic change.
- System tray protocol only if it remains relevant to the product; do not let it distort the PBUI surface model.
- Clipboard and selections as typed services where useful.
- Session/restart recovery and model journal persistence.

The X11 backend should mature without becoming the permanent definition of the kernel. Platform-independent object, command, widget, and runtime protocols are the long-term asset.

---

# 22. Changes to avoid

## 22.1 Do not run JavaScript on the X event loop

It would make input latency depend on arbitrary script code and would violate Goja ownership. Preserve posted semantic events and immutable render snapshots.

## 22.2 Do not expose a raw drawing context as the primary widget API

It prevents validation, diffing, semantic hit testing, remote execution, damage calculation, and reliable budgets. Use serializable primitives and add specialized native nodes when needed.

## 22.3 Do not optimize `wmcore.Layout` before measuring the reduced pipeline

The tree traversal and map allocation are visible inefficiencies, including the duplicate pass during current resize. Remove duplicate passes and add snapshots. Do not replace a clear pure algorithm with a complex incremental tree before pane-sized raster and client repaint work are eliminated.

## 22.4 Do not treat MIT-SHM as the final performance architecture

Shared pixmaps improve transfer. They do not remove raster area, conversion, resize allocation, or client redraw. Use SHM for appropriate stable surfaces after reducing work.

## 22.5 Do not rewrite all existing UI into Widget IR v2 at once

Keep a v1 adapter. Migrate surfaces when they need retained identity or richer layout. The REPL’s existing views should remain functional throughout.

## 22.6 Do not make every script equally trusted

A desktop configuration, a downloaded clock widget, a REPL cell, and a remote broker process have different authority and failure expectations. Encode profiles and capabilities before the ecosystem grows.

## 22.7 Do not implement menus, modals, and bars as ordinary tiled clients

They require shell-level placement, stacking, focus, and grabs. Let them share Widget IR while using distinct surface policies.

## 22.8 Do not duplicate the command API for each surface

A context menu, launcher, keybinding, REPL, and taskbar should not each call separate internal functions. Build one typed command graph and adapt entry points to it.

## 22.9 Do not make “live output” mean silently mutable history

REPL snapshots and live subscriptions serve different needs. Label and implement them separately.

## 22.10 Do not add concurrency where ownership is sufficient

The single WM owner is valuable. Move expensive pure work off the loop; do not make focus, X resources, or model mutation concurrently writable. Concurrency is a scheduling tool, not a replacement for state ownership.

---

# 23. Intern and new-developer learning path

## 23.1 Reading order through the code

Read in this order:

1. `pkg/wmcore` types, operations, and layout. Write down every invariant you infer.
2. `pkg/wmx11/wm.go` from `New` through `Run`, `Apply`, `ApplyBatch`, and `afterOp`.
3. `manage.go` from `MapRequest` through reparenting, teardown, relayout, and `paintFrame`.
4. `input.go` and `divider.go`, tracing one drag from button press to release.
5. `events.go`, `float.go`, and `focus_state.go` for lifecycle, stacking, and focus.
6. `xshm` and `draw` for the current pixel pipeline.
7. `pbui/object.go`, wire protocol, and broker loop.
8. `jsmod/bridge.go`, queue/event fan, `wmmod`, and `wmx11/scripting.go` for ownership.
9. `uispec` and `uimod` for snapshot UI.
10. `repl` values, derivation, session, and command UI.

For each path, answer:

- Who owns this state?
- On which goroutine may it change?
- Is this data a snapshot, reference, command, event, or resource?
- What is the failure and cancellation path?
- Is the function pure, or what effects does it issue?
- Can two callers cause the same effect redundantly?
- What bounds its work?

## 23.2 Exercise 1: trace one window lifecycle

Run under Xephyr and capture:

```text
CreateWindow
MapRequest
property reads
frame create
save-set insert
client border change
reparent
event selection
frame/client map
focus
client exit
DestroyNotify or UnmapNotify
callback detach
buffer drop
frame destroy
model leaf update
focus restore
```

Annotate each line with the responsible source function. The output should be a rendered trace and raw X trace.

Learning goal: understand that lifecycle correctness precedes layout features.

## 23.3 Exercise 2: prove divider sync idempotence

Refactor divider synchronization behind a recording backend. Add a test that a second identical desired snapshot produces no X requests and no paint. Then change one divider mode and prove only that divider repaints.

Learning goal: understand reconciliation as a diff rather than a redraw command.

## 23.4 Exercise 3: implement latest-wins sampling

Write a pure or isolated scheduler test:

```text
receive samples 1..100 while one tick is pending
commit tick
expected applied sample = 100
expected commits = 1
expected superseded = 99
```

Then test that release commits sample 101 immediately and no later scheduled tick re-applies sample 100.

Learning goal: distinguish throttling from coalescing.

## 23.5 Exercise 4: synthetic ConfigureNotify

Use a test client to request a new size while tiled. Assert:

- model revision unchanged;
- no `MoveResize` or paint effects;
- one synthetic `ConfigureNotify` with root-space actual geometry;
- client does not continue requesting based on missing notification.

Learning goal: protocol correctness can remove performance work.

## 23.6 Exercise 5: title-only decoration

Introduce a title child window for one experimental frame type. Compare raster pixels and surface allocations during resize against the old full-frame path. Preserve focus, buttons, exposure, theme change, and teardown.

Learning goal: choose a surface decomposition that matches ownership of pixels.

## 23.7 Exercise 6: keyed widget reconciliation

Given:

```text
old: [A(key=a, state=1), B(key=b, state=2)]
new: [B(key=b), A(key=a)]
```

Prove that instances and local state follow keys rather than positions. Add unkeyed behavior and a diagnostic warning.

Learning goal: retained identity is the foundation for scriptable custom widgets.

## 23.8 Exercise 7: define a presentation type and command

Register `<resize-session>`, provide compact and inspector faces, and define `Compare with…` accepting another `<resize-session>`. Invoke it from a plot point and from the REPL.

Learning goal: understand type-directed commands and cross-view input.

## 23.9 Exercise 8: break a script safely

Create a component that throws, schedules an async update after unmount, exceeds its node budget, and registers a timer. Confirm:

- only its subtree fails;
- the error presentation is usable;
- stale update is ignored;
- timer is disposed;
- WM input remains responsive;
- diagnostics identify runtime, generation, component, and event.

Learning goal: failure containment is part of the widget contract.

---

# 24. Proposed architecture decision records

## ADR-001: The desktop kernel has one mutation owner

**Status:** Preserve.

All authoritative desktop, focus, interaction, stacking, and X resource state changes on one owner loop. Other goroutines submit commands, notifications, or immutable work results.

**Consequence:** The owner must not execute unbounded raster, script, network, or client-wait work.

## ADR-002: JavaScript crosses host boundaries as data and references

**Status:** Preserve and extend.

JavaScript describes UI, commands, subscriptions, and effects as normalized data. Callbacks remain runtime-owned and are referenced by generation-aware IDs. Render code never calls JavaScript.

**Consequence:** Custom rendering must be expressed through registered primitives or bounded resources.

## ADR-003: One command graph serves every entry point

**Status:** Proposed.

Keys, menus, launcher, IPC, scripts, PBUI verbs, and REPL use one typed command definition and transaction path.

**Consequence:** Existing direct helper methods become adapters or internal command implementations.

## ADR-004: Outline is the guaranteed resize mode

**Status:** Proposed.

Outline resize is always available and is the default until live modes meet measured budgets. Live geometry and live content are adaptive capabilities, not correctness requirements.

**Consequence:** The product remains responsive with slow or unsynchronized clients.

## ADR-005: External client content is never rasterized by the WM

**Status:** Proposed.

The WM draws decoration surfaces only. External clients remain child windows. Internal PBUI content uses separate scene surfaces.

**Consequence:** Frame representation and rendering resources split by content kind.

## ADR-006: Widget UI is retained and keyed

**Status:** Proposed.

Widget IR v2 is hierarchical, serializable, versioned, and reconciled by stable keys. Layout, paint, hit-test, and semantic invalidation are distinct.

**Consequence:** `uispec` v1 remains through an adapter; full redraw is no longer the only update mode.

## ADR-007: PBUI objects have stable references

**Status:** Proposed.

Mutable, remote, or occurrence-specific objects use namespaced/versioned refs. Inline values remain supported for small immutable data.

**Consequence:** The broker needs resolver, stale, provenance, and capability semantics.

## ADR-008: Script runtimes are isolated by trust domain

**Status:** Proposed.

Trusted config, apps, automation, macros, and REPL use explicit runtime profiles. Installed apps normally receive independent runtimes, capabilities, budgets, generations, and disposers.

**Consequence:** Shared state crosses through snapshots, object refs, commands, and PBUI rather than JS object identity.

## ADR-009: Observability events are ordered facts

**Status:** Proposed.

The kernel writes ordered event envelopes through a bounded sequenced outbox or journal. High-frequency state uses coalescing streams with explicit policies.

**Consequence:** No goroutine-per-event emission; subscribers can recover by sequence or revision.

## ADR-010: REPL history is immutable; liveness is explicit

**Status:** Proposed.

Cell source, execution, snapshot results, receipts, and errors are immutable records. Live views are subscriptions attached to outputs and labeled as such.

**Consequence:** Debugging and replay remain meaningful while supporting live operational dashboards.

---

# 25. Review checklists

## 25.1 Resize-path review

- [ ] Motion callbacks perform no layout, raster, broker I/O, or JavaScript.
- [ ] Only the latest pointer sample is pending.
- [ ] Every interaction has an epoch and one finalizer.
- [ ] The final release position is queried or otherwise current.
- [ ] Layout is computed at most once per committed sample.
- [ ] Geometry is committed from a diff.
- [ ] Unchanged frames are not configured, mapped, or painted.
- [ ] External client decoration area, not pane area, determines WM raster work.
- [ ] Slow clients cause pacing or downgrade, not owner-loop blocking.
- [ ] ConfigureRequest denial sends the required synthetic event.
- [ ] Grabs and preview resources are released on all exit paths.
- [ ] Metrics report sample age, stage duration, X requests, raster pixels, and surface churn.

## 25.2 JavaScript widget review

- [ ] The widget tree is plain normalized data.
- [ ] Dynamic collections have stable keys.
- [ ] Handlers carry runtime and generation IDs.
- [ ] JavaScript runs only on its runtime owner.
- [ ] Effects are declarative and capability-checked.
- [ ] Subscriptions have delivery/coalescing policy and disposers.
- [ ] Node, depth, text, image, event, render-rate, and surface budgets are enforced.
- [ ] Host-owned hover, press, focus, accept, and drag feedback do not wait for JS.
- [ ] Error and teardown paths preserve the last valid desktop state.
- [ ] Portals and overlays declare layer, focus, grab, dismiss, and owner policy.
- [ ] Accessibility and presentation metadata are data, not inferred from pixels.

## 25.3 PBUI command review

- [ ] Subject and inputs use type constraints.
- [ ] Object identity is stable or explicitly inline immutable data.
- [ ] Availability is evaluated against a named revision.
- [ ] Missing inputs create scoped accept sessions.
- [ ] Continuations are invalidated on runtime generation change.
- [ ] Authorization is checked at commit.
- [ ] Effects have idempotency and conflict behavior.
- [ ] Results and errors are presentations.
- [ ] Object menus query the command registry rather than duplicate switch logic.
- [ ] The command can be invoked through multiple entry points without changing semantics.

## 25.4 REPL cell review

- [ ] Cell and output IDs are stable.
- [ ] Console output is scoped to the execution.
- [ ] Base and end model revisions are recorded.
- [ ] Snapshot and live views are distinguished.
- [ ] Async work is cancellable and progress-aware.
- [ ] Effect receipts show partial completion accurately.
- [ ] Large histories and outputs are virtualized/lazy.
- [ ] Equal result values remain distinct occurrences.
- [ ] Capabilities and budgets are visible.
- [ ] Runtime restart preserves prior immutable cells.

---
EOF
```

<details><summary>💭 Thinking</summary>

**Appended to engineering guide with appendix, glossary, and links**

**Summarizing project insights**

I’m pulling together key code findings from the recent go-go-wm commits and related materials, then I’ll compose those into a detailed Markdown document, explained with clarity.

**Summarized project insights**

</details>

```unknown
bash -lc set -euo pipefail
f=/mnt/data/go-go-wm-engineering-guide.md
stat -c 'path=%n\nsize=%s bytes\nmodified=%y' "$f"
wc -l -w -c "$f"
printf '\n--- HEAD ---\n'
head -n 40 "$f"
printf '\n--- TAIL ---\n'
tail -n 60 "$f"
printf '\n--- FENCE COUNT ---\n'
grep -c '^```' "$f" || true
printf '\n--- TODO/PLACEHOLDER CHECK ---\n'
grep -nE 'TODO|TBD|PLACEHOLDER|FIXME|XXX|lorem ipsum|\[insert|coming soon' "$f" | head -n 50 || true
printf '\n--- MERGE MARKERS ---\n'
grep -nE '^(<<<<<<<|=======|>>>>>>>)' "$f" || true

```

<details><summary>💭 Thinking</summary>

**Inspected and validated markdown file for accuracy and structure**

</details>

```unknown
bash -lc python - <<'PY'
from pathlib import Path
p = Path('/mnt/data/go-go-wm-engineering-guide.md')
text = p.read_text()
text = text.replace('against `go-golems/go-go-wm` commit', 'against `go-go-golems/go-go-wm` commit')
needle = '''The solution is not another isolated pixel-loop optimization. The solution is to introduce explicit clocks, transactions, retained identity, and load shedding.\n\n---\n\n# 1. Scope, evidence, and reading strategy\n'''
insert = '''The solution is not another isolated pixel-loop optimization. The solution is to introduce explicit clocks, transactions, retained identity, and load shedding.\n\n## Executive findings\n\n| Finding | Engineering consequence | First concrete move |\n|---|---|---|\n| Interactive resize performs input handling, layout mutation, X geometry, decoration rasterization, buffer replacement, pixel conversion, and client resize on one owner loop | A slow frame delays consumption of newer pointer samples and makes the desktop visibly trail the cursor | Add a latest-sample resize scheduler and make outline resize the guaranteed low-latency mode |\n| The WM paints a full-frame backing image even when an external child client covers nearly all of it | The pixel area processed is much larger than the visible shell decoration | Separate title, border, and internal-content surfaces; never rasterize external client content in the WM |\n| `relayout()` is both a safe recovery primitive and the default local update mechanism | Local interactions pay for visibility, divider, float, geometry, and repaint reconciliation together | Introduce geometry, visibility, stack, focus, and damage diffs with an explicit full-reconcile escape hatch |\n| The Goja owner and immutable-snapshot boundary are sound | Scriptability can grow without putting JavaScript on the X event path | Preserve the boundary and add a keyed, retained, versioned Widget IR rather than exposing raw drawing callbacks |\n| PBUI already unifies objects, typed input, verbs, menus, and cross-process participation | The same semantic layer can drive widgets, shell objects, menus, inspectors, and direct manipulation | Add stable object references, a presentation-type registry, typed commands, and scoped accept continuations |\n| The rich REPL already treats values as alternate presentations | It can become the interactive programming and observability interface of the desktop kernel | Give cells stable identity, model effects as plans and receipts, support streams, and make mounted components first-class objects |\n\n## Contents\n\n- [1. Scope, evidence, and reading strategy](#1-scope-evidence-and-reading-strategy)\n- [2. The product thesis](#2-the-product-thesis)\n- [3. Window-manager fundamentals for a new developer](#3-window-manager-fundamentals-for-a-new-developer)\n- [4. A systematic way to build a window manager](#4-a-systematic-way-to-build-a-window-manager)\n- [5. The current architecture](#5-the-current-architecture)\n- [6. Ownership, concurrency, and authority](#6-ownership-concurrency-and-authority)\n- [7. The current resize path, step by step](#7-the-current-resize-path-step-by-step)\n- [8. Measure the interaction, not only the CPU profile](#8-measure-the-interaction-not-only-the-cpu-profile)\n- [9. Redesign interactive resize](#9-redesign-interactive-resize)\n- [10. Decorations, surfaces, retained rendering, and damage](#10-decorations-surfaces-retained-rendering-and-damage)\n- [11. Detailed implementation review](#11-detailed-implementation-review)\n- [12. The present JavaScript architecture](#12-the-present-javascript-architecture)\n- [13. Target architecture: a small desktop kernel](#13-target-architecture-a-small-desktop-kernel)\n- [14. Widget IR and custom JavaScript components](#14-widget-ir-and-custom-javascript-components)\n- [15. PBUI as the semantic layer](#15-pbui-as-the-semantic-layer)\n- [16. Bars, menus, modals, taskbars, and overlay surfaces](#16-bars-menus-modals-taskbars-and-overlay-surfaces)\n- [17. Effects, capabilities, budgets, and hot reload](#17-effects-capabilities-budgets-and-hot-reload)\n- [18. The REPL as an operating-environment building block](#18-the-repl-as-an-operating-environment-building-block)\n- [19. Observability as a PBUI application](#19-observability-as-a-pbui-application)\n- [20. Testing strategy](#20-testing-strategy)\n- [21. Prioritized roadmap](#21-prioritized-roadmap)\n- [22. Changes to avoid](#22-changes-to-avoid)\n- [23. Intern and new-developer learning path](#23-intern-and-new-developer-learning-path)\n- [24. Proposed architecture decision records](#24-proposed-architecture-decision-records)\n- [25. Review checklists](#25-review-checklists)\n- [26. Final engineering position](#26-final-engineering-position)\n- [Appendix A. Source map](#appendix-a-source-map)\n- [Appendix B. Glossary](#appendix-b-glossary)\n- [Appendix C. Illustrative performance arithmetic](#appendix-c-illustrative-performance-arithmetic)\n\n---\n\n# 1. Scope, evidence, and reading strategy\n'''
if needle not in text:
    raise SystemExit('insertion needle not found')
text = text.replace(needle, insert, 1)
p.write_text(text)
print('updated', p)
PY
stat -c 'size=%s bytes' /mnt/data/go-go-wm-engineering-guide.md
wc -l -w -c /mnt/data/go-go-wm-engineering-guide.md
head -n 105 /mnt/data/go-go-wm-engineering-guide.md
```

<details><summary>💭 Thinking</summary>

**Inserted findings, cloned repository, and validated markdown parser**

</details>

```json
{"paths":["files"]}
```

```json
{"paths":["GitHub"],"query":"tree"}
```

```json
{"paths":["GitHub"],"query":"commit"}
```

```json
{"paths":["GitHub"],"query":"directory"}
```

```json
{"paths":["GitHub"],"query":"file"}
```

# Deliverable

[Download the completed Markdown handbook](sandbox:/mnt/data/go-go-wm-architecture-performance-scriptability-handbook.md)

The document is approximately **29,000 words** and includes:

- A foundational explanation of X11 window-manager mechanics for new developers.
- A package-by-package review of `go-go-wm` at commit `5b73c9f37c97538f6767ecdc3ece4fb599932377`.
- A synthesis of the July 18–20 GGWM project entries.
- A detailed trace of the current resize pipeline and its main performance problems:
  - stale pointer-event processing;
  - durable tree mutations during every preview update;
  - broad reconciliation;
  - full-frame decoration buffers;
  - resize-time MIT-SHM resource recreation;
  - redundant tiled `ConfigureRequest` relayouts;
  - the second full redraw/upload loop in `xapp`.
- An incremental resize plan covering latest-wins coalescing, preview-versus-commit state, outline/adaptive resize, client synchronization, thin frame decorations, retained buffers, X request diffs, and measurement.
- A proposed retained **Presentation Scene IR** with stable keys, hierarchical layout, damage tracking, semantic overlays, presentation wrappers, virtualized collections, and indexed hit testing.
- A unified surface architecture for bars, taskbars, menus, context menus, modals, popovers, tooltips, standalone windows, and embedded tiles.
- A concrete JavaScript API design with data-only scene snapshots and VM-free rendering.
- A supervised runtime model with per-service Goja owners, capabilities, resource leases, restart policy, generation-safe hot reload, event delivery classes, transactions, operation receipts, and recovery controls.
- A substantial treatment of the rich REPL as the desktop shell, including typed `Out[n]` values, object insertion, cancellable cells, transaction previews, provenance, inspectors, event cursors, and runtime debugging.
- A phased implementation roadmap, package-level change map, test strategy, intern curriculum, review checklists, and source bibliography.

The public PARC pages were not directly retrievable in the execution environment. The corresponding repository documents under `ttmp/2026/07/18`, `ttmp/2026/07/19`, and `ttmp/2026/07/20` were reviewed instead.

