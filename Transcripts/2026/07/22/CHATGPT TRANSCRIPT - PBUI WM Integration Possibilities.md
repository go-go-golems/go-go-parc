# PBUI WM Integration Possibilities

- URL: https://chatgpt.com/c/6a61020b-268c-83ea-87ba-cab6f7808a17
- Created: 2026-07-22T17:46:52.163Z

---

> Look at https://github.com/go-go-golems/go-go-wm and wailsv2 (go UI app toolkit) and potentially qtqml and how to integrate them into the PBUI concept of the WM, so that graphical apps can easily expose and react to the PBUI actions / expose menus / interface with the wm broker and all that. 
>
> Write a detailed report on the possibilities here, and what possibilities it opens (inspired by smalltalk / genera dynamic windows, PBUI thesis, CLIM common lisp / hypercard) as an interoperable semantically rich UI / WM system.

I’ll map the repository’s PBUI/broker architecture, evaluate Wails v2 and Qt/QML integration surfaces, then propose a concrete protocol, SDK, migration path, and staged implementation plan.

<details><summary>💭 Thinking</summary>

**Inspected GitHub repo and searched files for keywords**

</details>

```unknown
bash -lc rm -rf /tmp/go-go-wm && git clone --depth 1 https://github.com/go-go-golems/go-go-wm.git /tmp/go-go-wm && find /tmp/go-go-wm -maxdepth 2 -type f | sed 's#^/tmp/go-go-wm/##' | sort | head -200
```

<details><summary>💭 Thinking</summary>

**Cloned public repo using container**

</details>

```json
{"open":[{"ref_id":"https://github.com/go-go-golems/go-go-wm"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

**Discovered GitHub repository file paths via API**

</details>

```json
{"open":[{"ref_id":"https://api.github.com/repos/go-go-golems/go-go-wm/git/trees/main?recursive=1"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searching for GitHub API tree data**

**Fetched and inspected AGENT file content via GitHub API**

</details>

```json
{"open":[{"ref_id":"https://github.com/go-go-golems/go-go-wm/tree/main/pkg"},{"ref_id":"https://github.com/go-go-golems/go-go-wm/tree/main/cmd/go-go-wm"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Searching the web**

**Searched recent commits, fetched pull request changes, and analyzed files**

**Searched and fetched files for analysis in go-go-wm repository**

**Investigating repo structure**

I’m diving deeper into repo details to understand file changes, especially around the UI broker and terminal integration. I’ll check the docs and fetch files to see what I can uncover.

**Investigated repo structure**

**Interacted with GitHub**

**Fetched PBUI documentation, design files, and commit details**

</details>

```json
{"search_query":[{"q":"site:wails.io/docs v2 bindings events menu context menu runtime Wails"},{"q":"site:wails.io/docs/reference/runtime/events Wails v2 events"},{"q":"site:wails.io/docs/reference/menus Wails v2 menus"},{"q":"site:wails.io/docs/howdoesitwork Wails v2 architecture webview Go JavaScript"}],"response_length":"long"}
```

PBUI already provides typed objects, distributed verbs, accept interactions, brokered menus, scriptable apps, and serializable WM commands, making toolkit integration primarily an adapter/protocol design problem.

<details><summary>💭 Thinking</summary>

**Searched 1 website**

**Inspected Wails repo, analyzed sources, and researched documentation**

</details>

```json
{"search_query":[{"q":"site:wails.io/docs/v2.13.0 how does Wails work binding Go frontend generated bindings"},{"q":"site:wails.io/docs/v2.13.0 reference runtime events menu application menu Wails v2"},{"q":"site:wails.io/docs/v2.13.0 reference options bind lifecycle OnStartup OnDomReady"},{"q":"site:wails.io/docs/v2.13.0 gettingstarted installation Linux WebKitGTK"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 2 websites**

</details>

```unknown
bash -lc python - <<'PY'
import requests
u='https://www.bitsavers.org/pdf/mit/ai/aim/AITR-794.pdf'
r=requests.get(u,timeout=30)
print(r.status_code,len(r.content),r.headers.get('content-type'))
open('/tmp/AITR-794.pdf','wb').write(r.content)
PY
```

<details><summary>💭 Thinking</summary>

**Downloaded file via curl in container**

</details>

```json
{"screenshot":[{"ref_id":"turn422251view0","pageno":1},{"ref_id":"turn422251view0","pageno":2},{"ref_id":"turn422251view0","pageno":3},{"ref_id":"turn422251view0","pageno":4},{"ref_id":"turn422251view0","pageno":5},{"ref_id":"turn422251view0","pageno":6},{"ref_id":"turn422251view0","pageno":7}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searching github.com**

**Fetched repository README, searched package path, and inspected broker security**

</details>

```json
{"search_query":[{"q":"site:wails.io/docs/reference/options/linux Wails Linux options Window class Webview GTK"},{"q":"site:wails.io/docs/reference/options Wails App options Linux ProgramName Window title"},{"q":"site:wails.io/docs/reference/runtime/window Wails window position screen coordinates"}],"response_length":"long"}
```

The durable boundary keeps rendering local while PBUI standardizes semantic interaction; Wails fits Go/DOM bindings, Qt/QML maps Actions via a singleton, with capability-gated WM control.

<details><summary>💭 Thinking</summary>

**Searched 2 websites**

**Planning detailed report**

I’m working on analyzing how to integrate Wails v2, Qt/QML, and WM into PBUI, focusing on a rich, interoperable UI system. I’ll build a protocol design and include concrete steps.

**Examining system architecture**

I’m reviewing the repository’s structure for PBUI integration, focusing on key components like the object model, broker, and client communication. I’ll map the WM integration and app frameworks.

**Planned a detailed report**

**Planning report structure**

I’m organizing the report into clear sections: scope, current systems, design, integration options for Wails and Qt, and WM integration. I’ll structure everything to explain the system’s architecture, design choices, and recommendations.

**Planned report structure**

</details>

```json
{"search_query":[{"q":"site:doc.qt.io/qt-6 qlocalsocket QLocalSocket local socket documentation"},{"q":"site:wails.io/docs/reference/runtime/events Wails v2 EventsEmit EventsOn"},{"q":"site:wails.io/docs/reference/menus Wails v2 application menu context menu"},{"q":"site:doc.qt.io/qt-6 qml register singleton QObject QML_ELEMENT QML_SINGLETON"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 2 websites**

</details>

```unknown
bash -lc cat > /mnt/data/pbui_wails_qml_integration_report.md <<'EOF'
# PBUI as a Semantic Desktop Protocol
## Integrating Wails v2 and Qt/QML with `go-go-wm`

**Date:** 22 July 2026  
**Status:** Architecture report and implementation proposal  
**Scope:** `go-go-golems/go-go-wm`, Wails v2, Qt 6/QML, and the design lineage of presentation-based interfaces, Symbolics Genera Dynamic Windows, CLIM, Smalltalk, and HyperCard.

---

## Executive recommendation

`go-go-wm` already contains the kernel of a semantic desktop system, not merely a tiling window manager. Its PBUI layer has four unusually important properties:

1. visible values carry an open semantic type (`ptype`) and JSON value;
2. applications contribute type-directed actions independently of the application that displays the value;
3. an `accept` session lets a command request an object of a given type and lets the user satisfy that request by clicking a compatible presentation anywhere on the desktop; and
4. the broker, applications, and window manager are separate processes joined by a deliberately simple protocol.

That foundation should be preserved. Wails and Qt/QML should not be integrated by teaching the window manager about React components, DOM nodes, QObjects, or QML items. They should be integrated by building **toolkit adapters around a toolkit-neutral PBUI semantic plane**.

The recommended direction is:

- **Implement Wails v2 first.** A Wails application's backend is already Go, so it can link the existing PBUI client directly. The frontend receives PBUI state through generated Go bindings and Wails events. This provides the shortest route to a polished graphical PBUI application without adding a C ABI, a second runtime, or a new transport.
- **Implement Qt/QML second as a native Qt module.** The durable route is a small C++ `QObject`/QML plugin using `QLocalSocket`, with actions and menus represented by `QAbstractListModel`. An all-Go MIQT experiment is useful, but it should not become a dependency of PBUI itself.
- **Keep two integration modes.** Ordinary applications remain native toolkit windows and annotate selected controls with PBUI semantics. Portable or dynamically generated tools may instead publish a declarative PBUI surface. The repository's existing `uispec` is a strong seed for that second mode.
- **Evolve “verbs” into a richer action model without breaking v1.** Add parameter/result schemas, dynamic enabled state, menu placement, cancellation, progress, permissions, and invocation results. A v1 verb then maps to a v2 action with one implicit subject argument.
- **Separate object identity from inline values.** Retain the current small `Object` for immutable values, but add live `ObjectRef` values with stable identity, revision, provider, resolver, subscriptions, and provenance.
- **Add a desktop context model.** Focused window, active application, workspace, pointer object, primary selection, multi-selection, and clipboard should be first-class inputs to action resolution. This is the missing step between a type-directed popup menu and a coherent semantic command environment.
- **Keep trusted WM control separate.** The existing WM control socket is a privileged mechanism for layout mutations. PBUI should expose a safe, typed subset as actions on `window`, `tile`, and `workspace` objects rather than make every graphical app a raw WM controller.
- **Harden identity and capability checks before network or multi-user use.** The current protocol is appropriate for a single-user local prototype. Production use needs peer credentials, broker-assigned identities, capability grants, request limits, and auditable invocation records.

The central design rule is:

> **PBUI owns semantic identity, action composition, selection, and inter-application coordination. The application toolkit owns pixels, layout, text input, accessibility implementation, and its native interaction conventions. The WM owns placement, focus, workspace policy, and trusted window operations.**

This division permits a Wails application, a QML application, a terminal, a REPL cell, and an embedded WM surface to participate in the same object-and-command environment without forcing them into one renderer.

---

## 1. What exists in `go-go-wm`

### 1.1 Typed presentations

The current `pkg/pbui.Object` is the smallest useful form of a presentation object:

```go
type Object struct {
    Ptype string          `json:"ptype"`
    Value json.RawMessage `json:"value"`
    Label string          `json:"label,omitempty"`
    Doc   string          `json:"doc,omitempty"`
}
```

`Ptype` is an open slug namespace rather than a closed enum. This matters: a Git client can introduce `git-commit`, a mail client can introduce `mail-message`, and the WM can introduce `tile` without a central release of the broker. `Label` and `Doc` provide a fallback face and mouse-documentation text. The `pbui://` URI form lets such objects survive transport through terminals and hyperlink-capable applications.

This is already close to the original presentation-based UI idea: the displayed thing is not merely a string; it is a visible occurrence associated with an application-level value and type.

### 1.2 Distributed verbs

A verb is data:

```go
type Verb struct {
    ID      string
    Label   string
    Ptypes  []string
    Accepts []string
    Owner   string
}
```

The owner need not be the application currently displaying the object. A daemon can register a new `git-commit` action and thereby extend commit presentations in terminals, Wails windows, QML views, and WM-native surfaces. This decoupling is the most important architectural property in the repository.

The current matching relation is deliberately minimal: exact type membership or `any`. That is sufficient for a prototype, but a larger system will need namespacing, inheritance, unions, parameter schemas, and explicit conversion rules.

### 1.3 Cross-application `accept`

The broker owns a global accept state machine. An application requests one object of one or more types and supplies a prompt. All connected presentation surfaces are notified. Compatible visible objects can be highlighted. Clicking one answers the request, even when the presentation belongs to another process.

This enables interactions that ordinary GUI toolkits make awkward:

- “Compare this commit with another commit” followed by a click in any Git-aware view.
- “Swap this tile with another tile” followed by a click on another window title.
- “Open this file in a viewer” where the file is selected from a terminal, notebook, or graphical file browser.
- “Apply this color to the current selection” where the color originates in another application.

The current implementation allows one global session, with a new request superseding the old one. That is coherent for a first prototype and matches the visible modal interaction, but it will need scoping and concurrency rules later.

### 1.4 Broker-owned composition

The broker owns:

- connected clients and roles;
- the verb registry;
- accept state;
- a best-effort event bus;
- routing of `verb.invoke` to the registering owner;
- routing of `menu.request` to a client with the `wm` role; and
- routing of mouse-documentation text to the WM.

The broker deliberately does not link X11. The WM is a privileged participant, not the semantic protocol server itself. This separation is exactly what makes Wails, QML, terminal, remote-test, and future compositor integrations possible.

### 1.5 A uniform click contract

The shared `apps.Region` model gives every rendered region either:

- a PBUI object;
- a local action identifier;
- documentation text; or
- a combination of object and local action.

The resolver establishes a consistent priority:

1. a matching pending accept wins on primary click;
2. otherwise a local primary action runs;
3. otherwise the object menu opens;
4. secondary click requests the object menu directly.

This policy is independent of the renderer. The X11 demo shell, embedded WM surfaces, Wails components, and QML components can all implement the same contract.

### 1.6 Declarative surfaces already exist

`pkg/apps/uispec` is a pure, validated intermediate representation with rows of text, objects, buttons, hints, tables, fields, and Go-rendered images. Rendering emits both pixels and semantic regions. The Goja UI module uses a snapshot handoff so the WM render loop never executes user JavaScript.

This is a valuable precedent. It demonstrates that semantic UI descriptions can be normalized once, rendered safely later, and remain compatible with accept highlighting and object menus. It should become the seed of an optional portable `SurfaceSpec`, not the mandatory representation of every graphical application.

### 1.7 The WM control plane is separate

`pkg/wmx11/ipc.go` implements a separate NDJSON socket for trusted layout queries and operations: tree snapshots, window snapshots, serialized layout operations, focus, move, float, fullscreen, themes, launchers, and command registration. Requests are posted back to the WM loop.

That separation should remain explicit:

- **PBUI plane:** semantic objects, actions, menus, selection, context, surfaces, events.
- **WM control plane:** trusted mutations of compositor/window-manager state.

The WM can bridge selected operations into PBUI actions, but arbitrary PBUI applications should not automatically gain raw control-socket authority.

### 1.8 Current strengths and constraints

| Area | Existing strength | Constraint to address |
|---|---|---|
| Object model | Open typed JSON values; labels, docs, URI encoding | No stable live identity, revision, resolver, provenance, or schema registry |
| Actions | Distributed registration and owner-routed invocation | No parameters, results, progress, cancellation, state, permissions, ordering, or duplicate-ID namespace rules |
| Accept | Cross-process typed picking already works | One global session; no cardinality, scope, nesting, translator path, or explicit cancellation token |
| Menus | WM-centralized object menu and CLI fallback | Flat verb list; no submenu tree, app menu, dynamic state, local/native rendering policy, or command palette model |
| Events | Simple global trace and application notifications | Best-effort drops, no replay/snapshot/resync distinction, one broad subscription mode |
| Rendering | Pure regions, X shell, declarative `uispec` | No toolkit SDKs; no portable surface lifecycle or patch protocol |
| WM integration | Privileged WM client plus separate control socket | No authenticated window-to-app attachment or semantic context service |
| Security | Local Unix socket and bounded frames | Client-supplied names/roles, no peer credential policy, capabilities, audit, or rate limiting |

---

## 2. The proposed system model

### 2.1 Three planes, five layers

The complete system should be understood as three cooperating planes:

```text
+---------------------------------------------------------------+
| Presentation plane                                            |
| Wails DOM/React | Qt/QML | terminal | WM-native SurfaceSpec    |
+------------------------------+--------------------------------+
                               | semantic annotations/events
+------------------------------v--------------------------------+
| PBUI semantic plane                                            |
| objects | types | actions | context | selection | menus        |
| accept sessions | surface catalog | invocation lifecycle       |
+------------------------------+--------------------------------+
                               | safe WM actions / attachment
+------------------------------v--------------------------------+
| Window-management plane                                       |
| windows | focus | workspaces | placement | trusted layout ops  |
+---------------------------------------------------------------+
```

Inside the semantic plane, use five layers:

1. **Transport/session:** framing, handshake, reconnect, feature negotiation, request correlation, backpressure.
2. **Semantic model:** type definitions, inline values, live object references, action descriptors.
3. **Interaction context:** focused application, windows, pointer object, selection, clipboard, accept sessions.
4. **Composition:** menus, command palette, translators, view providers, surface descriptors.
5. **Adapters:** Go, Wails, Qt/QML, terminal, scripting, WM, and test harnesses.

This keeps toolkit concerns at the edge. It also prevents the PBUI broker from becoming an all-purpose GUI server or compositor.

### 2.2 Presentations are occurrences, not widgets

A presentation is a semantic occurrence of an object in a view. One object may have many simultaneous presentations:

- a commit hash in a terminal;
- a row in a Wails history view;
- a graph node in QML;
- a chip in a REPL result;
- an inspector entry in a WM-native surface.

The presentation occurrence needs a short-lived identity so the system can represent hover, selection, bounds, and view-local actions, while the underlying object may have a longer-lived identity.

A useful split is:

```text
ObjectRef       stable semantic entity or immutable value
PresentationRef visible occurrence of that object in a specific surface
SurfaceRef      the containing view/window/panel
WindowRef       the native top-level window managed by the WM
```

Do not expose raw DOM nodes, pointers, or QObject addresses across the broker. Presentation references must be opaque IDs owned by the application adapter.

### 2.3 Inline values and live object references

Retain the current inline object for small immutable values. Add a second form for live identity:

```json
{
  "ptype": "org.example.git.commit",
  "id": "sha256:8b1f...",
  "rev": "repository-generation:4831",
  "provider": "app://org.example.git/instance/7",
  "label": "8b1f9c2 Fix broker reconnect",
  "doc": "Commit by A. Developer on 2026-07-21",
  "uri": "pbui://org.example.git.commit/sha256%3A8b1f...",
  "snapshot": {
    "hash": "8b1f9c2...",
    "repository": "file:///home/user/src/project"
  },
  "capability": "opaque-broker-issued-token"
}
```

Suggested semantics:

- `ptype`: namespaced semantic type.
- `id`: stable within the provider's declared scope.
- `rev`: optional optimistic-concurrency revision.
- `provider`: broker-assigned provider identity, not client-chosen owner text.
- `snapshot`: bounded summary sufficient for menus and disconnected display.
- `uri`: stable link form when appropriate.
- `capability`: optional unforgeable grant for resolution or mutation.

Add broker operations:

```text
object.resolve    fetch a requested face or property subset
object.watch      subscribe to changes or invalidation
object.changed    publish revision/snapshot updates
object.release    release lease/subscription
object.open       ask a provider for a canonical surface
```

The broker should not become a universal object database. Providers remain authoritative. The broker indexes descriptors and routes resolution.

### 2.4 Type definitions and subtyping

A type registry should remain open and distributed, but it needs enough metadata for interoperability:

```json
{
  "id": "org.example.git.commit",
  "version": 1,
  "extends": ["pbui.resource", "pbui.temporal-entity"],
  "schema": {
    "type": "object",
    "required": ["hash", "repository"],
    "properties": {
      "hash": {"type": "string"},
      "repository": {"type": "string", "format": "uri"}
    }
  },
  "faces": ["compact", "summary", "detail"],
  "canonical_uri": true
}
```

The matching relation should support:

- exact type;
- subtype;
- union;
- `any`;
- optional structural constraints;
- explicitly registered translators or coercions.

Avoid a general-purpose expression language in the first version. Use declarative type references and ask providers for dynamic applicability where necessary. A complex embedded predicate language would create security, compatibility, and tooling problems too early.

### 2.5 Actions rather than only flat verbs

Keep “verb” as familiar UI language and a v1 protocol alias, but model the v2 entity as an action or command descriptor:

```json
{
  "id": "org.example.git.compare",
  "version": 1,
  "label": "Compare with…",
  "doc": "Compare the subject commit with another commit",
  "subject": {"types": ["org.example.git.commit"]},
  "parameters": [
    {
      "name": "other",
      "label": "Other commit",
      "types": ["org.example.git.commit"],
      "acquisition": "accept"
    }
  ],
  "result": {"types": ["org.example.git.diff"]},
  "placements": ["context-menu", "command-palette"],
  "group": "compare",
  "order": 200,
  "state_provider": true,
  "execution": {
    "cancellable": true,
    "reports_progress": true,
    "idempotent": true
  },
  "permissions": ["object.read"]
}
```

Action resolution should answer two distinct questions:

1. **Could this action conceptually apply?** Based on subject type, parameter types, and context.
2. **Is it currently enabled, visible, checked, or selected?** Based on provider state, permissions, object revision, and application conditions.

A state query response can be compact and cacheable:

```json
{
  "action": "org.example.git.compare",
  "enabled": true,
  "visible": true,
  "checked": false,
  "label_override": "Compare 8b1f9c2 with…",
  "reason": ""
}
```

### 2.6 Invocation lifecycle

Invocation needs to become a first-class conversation rather than a fire-and-forget route:

```text
action.invoke
  -> action.accepted
  -> action.progress* / action.output*
  -> action.result | action.error | action.cancelled
```

Every invocation should carry:

- globally unique invocation ID;
- caller identity;
- action ID and version;
- subject object reference;
- parameter objects or literals;
- relevant context snapshot;
- deadline/cancellation token;
- expected revision where mutation is involved;
- optional idempotency key;
- optional parent invocation for workflows;
- trace/audit correlation ID.

This enables progress UIs, cancellation, undo records, automation replay, and deterministic integration tests.

### 2.7 Desktop context and selection

Actions should not be resolved only from the object under a right click. Introduce a context service with fields such as:

```json
{
  "seat": "default",
  "workspace": "workspace://3",
  "active_window": "window://0x04600007",
  "active_app": "app://org.example.editor/instance/2",
  "focused_surface": "surface://editor/main",
  "pointer_presentation": "presentation://editor/row/91",
  "selection": [
    {"ptype": "org.example.file", "id": "file:///tmp/a.txt"}
  ],
  "clipboard": {
    "text": "/tmp/a.txt",
    "objects": [{"ptype": "org.example.file", "id": "file:///tmp/a.txt"}]
  }
}
```

The context graph should distinguish:

- application-local selection;
- desktop primary selection;
- clipboard semantic payload;
- pointer/hover object;
- focused control and surface;
- active window and workspace;
- accept target and prompt.

Applications publish context changes; the WM publishes focus/window/workspace changes. The broker computes a coherent snapshot and emits coalesced updates.

### 2.8 Accept sessions as typed acquisition

Generalize `accept` into typed parameter acquisition:

```json
{
  "session": "accept://broker/991",
  "requester": "invocation://42",
  "types": ["org.example.git.commit"],
  "cardinality": {"min": 1, "max": 1},
  "scope": {
    "seat": "default",
    "workspace": "current",
    "exclude_surface": "surface://caller/dialog"
  },
  "prompt": "COMPARE — select another commit",
  "allow_translators": true,
  "deadline": "2026-07-22T19:00:00Z"
}
```

Recommended evolution:

- allow multiple sessions when they are on different seats or explicitly nested;
- choose one active session per seat by priority and focus;
- support one, optional, and multiple cardinality;
- retain Escape cancellation;
- allow keyboard search, paste, drag/drop, or explicit object entry in addition to clicking;
- expose compatible translators, such as `file-path -> file` or `commit-hash -> git-commit`, without silently applying unsafe conversions;
- highlight locally in each toolkit, not by screenshot analysis or WM overlays.

### 2.9 Menus, palettes, and command tables as one model

A PBUI menu should be a composable tree of action references, separators, groups, and dynamic providers:

```json
{
  "id": "menu://org.example.editor/document",
  "nodes": [
    {"action": "org.example.document.save"},
    {"action": "org.example.document.save-as"},
    {"separator": true},
    {
      "submenu": "Open With",
      "provider": "org.pbui.open-with-provider"
    },
    {"include": {"actions_for": "$subject", "group": "inspect"}}
  ]
}
```

The same action catalog can feed:

- native application menu bars;
- in-window context menus;
- WM-centralized object menus;
- a universal command palette;
- keyboard help overlays;
- voice or accessibility command enumeration;
- automation and agent APIs.

Rendering policy should be explicit:

- `render: local` for native toolkit placement and accessibility;
- `render: wm` for desktop-consistent cross-application object menus;
- `render: either` with broker policy and capability negotiation.

### 2.10 Surfaces and dynamic windows

A surface is a logical view that may or may not already have a top-level native window:

```json
{
  "id": "surface://org.example.git/commit-inspector/8b1f9c2",
  "kind": "inspector",
  "title": "Commit 8b1f9c2",
  "subject": {"ptype": "org.example.git.commit", "id": "sha256:8b1f..."},
  "view": {
    "provider": "org.example.git",
    "name": "commit-detail",
    "mode": "native"
  },
  "placement": {
    "preferred": "adjacent",
    "min_size": [420, 260],
    "transient_for": "window://0x04600007"
  },
  "state": {
    "serializable": true,
    "restoration_key": "git:repo:commit:8b1f9c2"
  }
}
```

Two surface modes are essential:

1. **Native surface:** Wails or QML owns rendering and exposes semantic presentations.
2. **Portable surface:** provider publishes a normalized `SurfaceSpec`; the WM or another host renders it.

Portable surfaces are appropriate for inspectors, launchers, notebooks, dashboards, prompts, and user-authored tools. They are not a replacement for full native applications.

---

## 3. Wails v2 integration

### 3.1 Why Wails is the first target

Wails has the most direct fit with the existing codebase:

- the backend is a normal Go program and can import `pkg/pbui/client`;
- bound Go methods are generated as Promise-returning JavaScript/TypeScript functions;
- Wails provides a bidirectional application-local event system between Go and the frontend;
- the existing Go structs can generate frontend models;
- application menus can be built and dynamically updated from Go;
- Linux windows expose class/program configuration useful for WM attachment;
- no new language boundary is required in the PBUI client itself.

The Wails event bus is not the PBUI bus. It is the internal bridge between one application's Go backend and its web frontend. The Go backend remains the only component connected to the broker.

### 3.2 Package structure

A practical split is:

```text
integrations/wailsv2/
  pbuiwails/                 Go bridge package
    bridge.go
    lifecycle.go
    actions.go
    menus.go
    window.go
  frontend/                  TypeScript package
    src/provider.tsx
    src/presentation.tsx
    src/hooks.ts
    src/menu.tsx
    src/types.ts
  example-react/
  example-vanilla/
```

The Go package should depend on PBUI but not on a particular frontend framework. The TypeScript package may provide a small framework-neutral core plus React bindings.

### 3.3 Go bridge responsibilities

`pbuiwails.Bridge` should own:

- broker connection and reconnect/backoff;
- handshake and feature negotiation;
- application manifest registration;
- action handler registry;
- pending requests and invocation lifecycle;
- conversion between Go PBUI messages and generated frontend models;
- Wails event emission for unsolicited state;
- application menu projection;
- window attachment metadata;
- a snapshot method used when the frontend first mounts or recovers from dropped local events.

Illustrative API:

```go
type Bridge struct {
    // internal connection, handlers, snapshots, Wails context
}

type Options struct {
    Socket      string
    AppID       string
    InstanceID  string
    Roles       []string
    Manifest    Manifest
    Reconnect   ReconnectPolicy
}

func New(opts Options) *Bridge
func (b *Bridge) Startup(ctx context.Context)
func (b *Bridge) DomReady(ctx context.Context)
func (b *Bridge) Shutdown(ctx context.Context)

// Methods bound into Wails-generated frontend bindings.
func (b *Bridge) Snapshot() FrontendSnapshot
func (b *Bridge) RegisterPresentations([]PresentationDescriptor) error
func (b *Bridge) Answer(session string, object ObjectRef) error
func (b *Bridge) CancelAccept(session string) error
func (b *Bridge) QueryActions(subject ObjectRef, context ContextHint) ([]ActionState, error)
func (b *Bridge) Invoke(req InvokeRequest) (InvocationReceipt, error)
func (b *Bridge) RequestMenu(req MenuRequest) (MenuResolution, error)
func (b *Bridge) SetSelection(SelectionUpdate) error
func (b *Bridge) Hover(HoverUpdate) error
func (b *Bridge) AttachWindow(WindowAttachment) error
```

Wails lifecycle usage:

- store the Wails application context in `OnStartup`;
- connect the PBUI session asynchronously and maintain backend state there;
- do not assume the frontend/window is ready during `OnStartup`;
- emit the initial frontend snapshot during or after `OnDomReady`;
- expose an explicit `Snapshot()` call so a frontend can always resynchronize;
- close the broker connection and withdraw transient registrations on shutdown.

### 3.4 Frontend API

A React-facing API can be small:

```tsx
<PbuiProvider bridge={Bridge}>
  <Presentation
    object={{
      ptype: "org.example.git.commit",
      id: commit.hash,
      label: commit.shortHash
    }}
    primaryAction="org.example.git.open"
    doc={`Commit ${commit.hash}`}
  >
    <CommitRow commit={commit} />
  </Presentation>
</PbuiProvider>
```

Hooks:

```ts
const accept = useAcceptMode();
const actions = usePbuiActions(subject);
const selection = usePbuiSelection();
const invoke = usePbuiInvoke();
```

The `<Presentation>` component should:

- associate the DOM element with a PBUI object and a generated presentation ID;
- add semantic data attributes useful for inspection and debugging;
- apply an accept-compatible state class;
- handle primary click according to the common click contract;
- handle `contextmenu` and request a PBUI menu;
- publish hover/documentation changes with throttling;
- participate in application selection and semantic drag/drop;
- apply correct ARIA role, accessible name, and keyboard affordances supplied by the host application.

Avoid serializing full object snapshots into HTML attributes. Keep the authoritative descriptor in a `WeakMap` or provider registry keyed by a short presentation ID. Data attributes should carry only non-sensitive debugging identifiers.

### 3.5 Frontend event bridge

Use generated Go bindings for request/response operations and Wails events for unsolicited state:

```text
PBUI broker
    -> Go bridge callback
    -> runtime.EventsEmit(ctx, "pbui:message", envelope)
    -> frontend provider reducer

Frontend gesture
    -> generated Bridge.Answer / Invoke / RequestMenu call
    -> Go bridge
    -> PBUI broker
```

A single versioned event envelope is preferable to dozens of unstable event names:

```json
{
  "version": 1,
  "kind": "accept.changed",
  "seq": 348,
  "data": {
    "session": "accept://broker/991",
    "types": ["org.example.git.commit"],
    "prompt": "COMPARE — select another commit"
  }
}
```

The provider should detect a sequence gap and call `Snapshot()` rather than assume all local events were received. This mirrors the recommended distinction between event hints and authoritative state.

### 3.6 Wails menus

There are three useful menu modes.

#### A. Native application menu

PBUI menu definitions can be projected into Wails `menu.Menu` and `menu.MenuItem` values. Dynamic updates use the Wails runtime menu-update function. This is suitable for File/Edit/View-style menus and context-dependent commands tied to the active document or selection.

Mapping:

| PBUI | Wails |
|---|---|
| action label | `MenuItem.Label` |
| accelerator | `MenuItem.Accelerator` |
| enabled | inverse of `Disabled` |
| visible | inverse of `Hidden` |
| checked | `Checked` |
| submenu | `SubMenu` |
| invoke | `Click` callback routing to PBUI |

The bridge should preserve platform-standard roles on macOS instead of replacing them with generic PBUI items.

#### B. Local web context menu

A React/HTML context menu renders the broker-resolved action tree inside the application. Advantages:

- precise placement relative to the DOM element;
- consistent behavior under HiDPI scaling and webview decorations;
- richer previews and parameter controls;
- direct accessibility integration with the application's DOM;
- no dependency on WM-specific popup placement.

This should be the default for ordinary in-application context menus.

#### C. WM-centralized semantic menu

The current PBUI behavior sends a menu request with screen coordinates and lets the WM render the popup. This remains valuable when:

- the object originated in a terminal or renderer without menus;
- a consistent cross-application desktop menu is desired;
- the menu contains WM actions and object actions composed together;
- accept mode and mouse documentation are visibly desktop-global.

The Wails adapter should support all three via a manifest policy. It should not force every Wails context menu through the WM.

### 3.7 Window attachment

A Wails process should attach each top-level window to its semantic application identity:

```json
{
  "app_id": "org.example.git",
  "instance_id": "01J3...",
  "window_id": "main",
  "pid": 42173,
  "title": "Repository — project",
  "class_hint": "org-example-git",
  "program_hint": "org.example.git",
  "token": "broker-issued-window-attachment-token"
}
```

On X11, the WM can correlate PID, class, instance, title, and native client ID. Wails' Linux class/program options make this correlation less heuristic. The token should bind the application connection to the window registration so another local process cannot claim an unrelated window merely by guessing its PID or title.

Once attached, PBUI can safely expose:

- `window.focus`;
- `window.move-to-workspace`;
- `window.float`;
- `window.fullscreen`;
- `window.split-with`;
- `window.close`;
- `window.inspect`;
- application-defined window actions.

The WM remains the owner of these operations and evaluates policy.

### 3.8 Selection and semantic drag/drop

The Wails adapter should integrate with normal browser selection and drag/drop rather than replace them.

Recommended payloads:

- ordinary MIME formats for compatibility: `text/plain`, `text/uri-list`;
- a PBUI JSON descriptor in an application-local custom MIME type;
- a `pbui://` URI when an object has a safe canonical link;
- broker-issued capabilities rather than raw private object data.

On drop, the application can query actions or translators from the dragged object type to the drop target type. A file dropped on a Git repository might offer “stage”, “copy into repository”, or “open”, while remaining a normal OS file drag for non-PBUI applications.

### 3.9 Failure and offline behavior

A graphical application must remain usable when the broker is absent.

The Wails adapter should provide:

- a connection-state observable;
- local primary actions that do not require PBUI;
- cached action/menu state with visible stale status where appropriate;
- bounded reconnect with jitter;
- re-registration after reconnect;
- snapshot resynchronization;
- deterministic withdrawal of old instance registrations;
- no blocking of the Wails UI thread on broker I/O.

The current Go client is concurrent-safe, but a production adapter needs a session layer above it for reconnect and manifest replay.

### 3.10 Wails-specific constraints

- Linux deployment includes GTK/WebKit dependencies and distribution-specific WebKit compatibility considerations.
- DOM screen coordinates and native window coordinates can differ under scaling and decorations; local menus avoid most of this problem.
- Wails' generated bindings and event system should be preferred over injecting arbitrary JavaScript through a window-execution API.
- Web frontend code must never receive unrestricted access to the broker socket or capabilities not required by the UI.
- The semantic adapter must not equate a React component instance with a stable object identity.

---
EOF
```

<details><summary>💭 Thinking</summary>

**Created PBUI Wails integration report and checked Markdown structure**

</details>

```json
{"paths":["GitHub"],"query":"tree"}
```

```json
{"paths":["GitHub"],"query":"contents"}
```

```json
{"paths":["GitHub"],"query":"search"}
```

```json
{"paths":["GitHub"],"query":"list repository"}
```

```json
{"paths":["GitHub"],"query":"fetch_file"}
```

# PBUI as a Semantic Desktop Protocol

[Download the detailed 12,400-word architecture report](sandbox:/mnt/data/pbui_wails_qml_integration_report.md)

## Main conclusion

`go-go-wm` already contains the core of a semantic desktop system rather than merely a tiling WM. Its PBUI layer defines typed presentation values, an open `ptype` namespace, distributed verbs, labels and documentation, and portable `pbui://` references. fileciteturn6file0L16-L24 fileciteturn6file0L79-L108

The broker is correctly separated from X11 and owns the verb registry, global accept state, and event routing. A menu request either answers a compatible pending accept or is sent to the WM for presentation, while invocation is routed back to whichever client registered the verb. fileciteturn7file0L3-L7 fileciteturn7file0L255-L315 fileciteturn8file0L12-L46

The application framework is also already renderer-neutral at the important boundary: rendering produces semantic regions, and the shared click contract prioritizes a compatible accept, then a local primary action, then the object menu. The declarative `uispec` layer turns normalized rows and segments into both pixels and semantic regions. fileciteturn14file0L3-L11 fileciteturn14file0L40-L71 fileciteturn15file0L3-L10 fileciteturn15file0L255-L313

The resulting architectural recommendation is:

> **Keep PBUI toolkit-neutral. Wails, Qt/QML, terminals, and WM-native surfaces should be adapters to a shared semantic plane. They should not be special cases implemented inside the window manager.**

PBUI should own semantic identity, action composition, typed acquisition, selection, menus, and cross-application coordination. Toolkits should own layout, rendering, text input, accessibility implementation, and native interaction conventions. The WM should own placement, focus, workspaces, and trusted window operations.

## Wails v2

Wails is the correct first graphical integration target.

A Wails application already has a normal Go backend, so it can reuse `pkg/pbui/client` directly. Wails generates Promise-returning JavaScript or TypeScript bindings for bound Go methods and provides a bidirectional event mechanism between Go and the frontend. It also supports application menus that can be updated dynamically. citeturn249055search12turn249055search9turn665910search0turn665910search5

The proposed Wails integration consists of:

1. A Go `pbuiwails.Bridge` that owns broker connection, reconnection, manifest replay, action handlers, menu projection, and window attachment.
2. A small TypeScript package with `PbuiProvider`, `useAcceptMode`, `usePbuiActions`, and a `<Presentation>` component.
3. Generated Go bindings for request/response operations such as answer, invoke, query actions, publish selection, and request a menu.
4. Wails events for unsolicited broker state, backed by an explicit snapshot method for resynchronization.
5. Three menu policies:
   - native Wails application menus;
   - local HTML/React context menus;
   - the existing WM-centralized PBUI menu.
6. Window attachment using application identity, PID, broker-issued token, and stable Linux class/program hints rather than title matching alone.

The frontend should not connect directly to the Unix socket. The Go backend should retain all broker credentials and capabilities.

## Qt/QML

The durable Qt path is a small native C++ QML module, not a Qt-specific PBUI protocol.

The module can use `QLocalSocket`, which maps to a local-domain socket on Unix, and expose a `Pbui` singleton as a `QObject`. QML can consume QObject properties, invokable methods, and signals; action and menu collections naturally map to `QAbstractListModel`. QML menus can generate their items dynamically from such models. citeturn665910search6turn750576search0turn750576search13turn750576search14turn750576search2turn665910search8

The report proposes:

- a `PbuiSession` singleton;
- `PbuiActionModel` and `PbuiMenuModel`;
- a reusable `Presentation.qml`;
- an optional attached-property API for existing controls;
- asynchronous socket handling on the Qt event loop;
- strict marshalling of all QML-visible model changes onto the Qt GUI thread;
- local, native, and WM-rendered menu modes;
- the same window-attachment and reconnection semantics as Wails.

MIQT is worth a compatibility spike for all-Go Qt applications, but it should remain optional. Qamel is too narrow for the principal bridge because a semantically rich PBUI client needs nested values, live models, menus, state updates, and invocation lifecycle support.

## Protocol evolution

The existing v1 NDJSON protocol should remain operational and debuggable. Its codec interface already leaves room for another encoding later, while the current framing is simple enough to inspect and fuzz. fileciteturn9file0L12-L20 fileciteturn9file0L63-L105

The report proposes an additive v2 model:

- **`ObjectRef`** for stable live identity, revisions, provider ownership, resolution, subscriptions, provenance, and bounded snapshots.
- **Actions** as an enriched form of verbs, with typed parameters, result types, dynamic enabled/checked state, menu placement, progress, cancellation, permissions, and invocation IDs.
- **Desktop context** covering active application, window, workspace, pointer presentation, semantic selection, and clipboard.
- **Scoped accept sessions** with cardinality, deadlines, nesting, seat/workspace scope, and explicit translators.
- **Menu trees** shared by native menus, context menus, WM menus, command palettes, accessibility, and automation.
- **Surface descriptors** for both native toolkit views and portable PBUI-rendered tools.
- **Reliable state streams** distinct from lossy telemetry events.
- **Authenticated ownership and capabilities**, using Unix peer credentials and broker-assigned connection identities.

The current raw WM control socket should remain separate. It exposes serialized layout and window-management operations and runs them on the WM loop. fileciteturn18file0L16-L38 fileciteturn18file0L105-L140 PBUI should project only a safe, policy-aware subset as actions on `window`, `tile`, and `workspace` objects.

## What this opens

The design recovers several historically powerful UI properties in an interoperable, multi-process form:

- Ciccarelli’s PBUI model linked application objects to visible presentations through presenters and recognizers. The modern equivalent is an application-owned object, a toolkit-owned presentation, and broker-mediated semantic action resolution. citeturn168092view2
- Genera Dynamic Windows allowed typed input to be supplied either textually or by clicking a compatible presentation, with mouse documentation and context-sensitive actions. citeturn804471view1turn804471view2turn804471view3
- CLIM adds the missing formal concepts: typed command arguments, presentation translators, input contexts, and composable command tables. citeturn430966search2
- Smalltalk supplies the live-object and inspector model.
- HyperCard supplies persistent user-authored surfaces and understandable message dispatch. Its message path proceeds through UI object and card/stack contexts rather than requiring every object to know every other object directly. citeturn457401search1turn457401search2

In practical terms, this enables:

- actions contributed by one application to appear on compatible objects in every other application;
- cross-application typed picking instead of clipboard-only workflows;
- a genuinely contextual universal command palette;
- semantic clipboard and drag/drop;
- live inspectors and interchangeable views selected by type;
- dynamic tool windows and HyperCard-like user panels;
- workflows composed from typed actions and intermediate objects;
- deterministic automation based on object and action IDs rather than screen coordinates;
- semantic desktop snapshots and restoration;
- richer keyboard, voice, and accessibility interfaces.

## Recommended first implementation

The first implementation should not attempt the entire v2 protocol.

Start with:

1. `pkg/pbui/session`: reconnection, broker-assigned ownership, manifest replay, and snapshots.
2. `integrations/wailsv2/pbuiwails`: Go lifecycle bridge and current-v1 functionality.
3. A React `<Presentation>` component with accept highlighting, menus, hover docs, and selection.
4. A reference Wails object browser that exchanges accepts and verbs with terminals and existing PBUI applications.
5. An authenticated X11 window-attachment proof of concept.
6. Only then formalize action results, live object references, context, and menu trees based on observed integration pressure.

The report includes protocol records, Wails and QML API sketches, menu and window-attachment designs, security boundaries, worked scenarios, repository layout, conformance tests, and a five-phase implementation plan.

