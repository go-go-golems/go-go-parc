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

## 4. Qt/QML integration

### 4.1 Integration choices

There are four plausible Qt paths:

1. **C++ Qt plugin/QML module speaking PBUI directly.** Most maintainable and most aligned with Qt's object and model systems.
2. **Go backend plus C++ QML shell.** Useful when core application logic is already Go but the presentation layer is native QML.
3. **MIQT all-Go application.** Viable for a focused experiment; introduces CGO, generated bindings, Qt deployment, licensing, and main-thread constraints.
4. **Qamel.** Its intentionally small binding surface and JSON-string workarounds for compound values make it unsuitable as the principal PBUI/QML bridge.

The recommended production path is option 1. PBUI remains language-neutral; the Qt adapter is a normal protocol client, not a Go-specific shim.

### 4.2 Native Qt module design

Create a module such as:

```text
integrations/qtqml/PbuiQt/
  CMakeLists.txt
  pbuisession.h/.cpp
  pbuiactionmodel.h/.cpp
  pbuimenumodel.h/.cpp
  pbuipresentationattached.h/.cpp
  plugin.cpp
  qml/
    Presentation.qml
    ContextMenu.qml
    AcceptBanner.qml
    qmldir
```

Use `QLocalSocket` for the local-domain connection and incremental NDJSON framing. The socket participates naturally in the Qt event loop. Parsing, schema validation, and routing should occur in the module; QML should receive normalized values and models rather than raw protocol frames.

### 4.3 QML-facing singleton

Expose a singleton `Pbui` derived from `QObject`:

```cpp
class PbuiSession : public QObject {
    Q_OBJECT
    QML_ELEMENT
    QML_SINGLETON

    Q_PROPERTY(bool connected READ connected NOTIFY connectedChanged)
    Q_PROPERTY(QVariantMap acceptSession READ acceptSession
               NOTIFY acceptSessionChanged)
    Q_PROPERTY(QObject* context READ contextObject CONSTANT)
    Q_PROPERTY(QObject* actions READ actions CONSTANT)

public:
    Q_INVOKABLE QString registerPresentation(const QVariantMap &descriptor);
    Q_INVOKABLE void unregisterPresentation(const QString &presentationId);
    Q_INVOKABLE void answer(const QString &sessionId,
                            const QVariantMap &object);
    Q_INVOKABLE QString invoke(const QVariantMap &request);
    Q_INVOKABLE void cancelInvocation(const QString &invocationId);
    Q_INVOKABLE void requestMenu(const QVariantMap &request);
    Q_INVOKABLE void setSelection(const QVariantList &objects);
    Q_INVOKABLE void hover(const QVariantMap &presentation,
                           const QString &doc);

signals:
    void connectedChanged();
    void acceptSessionChanged();
    void invocationProgress(const QString &id, const QVariantMap &progress);
    void invocationFinished(const QString &id, const QVariantMap &result);
    void actionRunRequested(const QVariantMap &invocation);
    void menuResolved(const QString &requestId, QObject *menuModel);
};
```

Qt already provides the relevant language bridge: QML can read QObject properties, call public slots or `Q_INVOKABLE` methods, and react to signals. This is a natural fit for a stateful PBUI session.

### 4.4 Action and menu models

Represent action collections with `QAbstractListModel`, not unstructured JavaScript arrays. Suggested roles:

```text
id
label
doc
enabled
visible
checked
checkable
group
order
shortcut
iconName
hasParameters
owner
```

A menu tree can be modeled either as nested models or as a flat model with parent IDs. Native QML `Menu` items may be created dynamically with `Instantiator`:

```qml
Menu {
    id: menu

    Instantiator {
        model: Pbui.actions.forSubject(root.object)

        delegate: MenuItem {
            text: model.label
            enabled: model.enabled
            visible: model.visible
            checkable: model.checkable
            checked: model.checked
            onTriggered: Pbui.invoke({
                action: model.id,
                subject: root.object
            })
        }

        onObjectAdded: (index, object) => menu.insertItem(index, object)
        onObjectRemoved: (index, object) => menu.removeItem(object)
    }
}
```

Qt can render menus as native platform menus, separate popup windows, or ordinary scene items. The adapter should expose the broker's requested policy but let the application choose the mode compatible with its platform and visual design.

### 4.5 Reusable QML presentation component

A reusable wrapper mirrors the Wails component:

```qml
import QtQuick
import QtQuick.Controls
import Org.GoGoGolems.Pbui

Item {
    id: root

    required property var object
    property string primaryAction: ""
    property string doc: ""
    property string presentationId: ""

    readonly property bool acceptCompatible:
        Pbui.typeMatches(Pbui.acceptSession.types || [], object.ptype)

    Component.onCompleted: {
        presentationId = Pbui.registerPresentation({
            object: object,
            surface: PbuiWindow.surfaceId,
            doc: doc
        })
    }

    Component.onDestruction:
        Pbui.unregisterPresentation(presentationId)

    HoverHandler {
        onHoveredChanged: Pbui.hover(
            { id: root.presentationId, object: root.object },
            hovered ? root.doc : ""
        )
    }

    TapHandler {
        acceptedButtons: Qt.LeftButton | Qt.RightButton
        onTapped: (eventPoint, button) => {
            if (button === Qt.RightButton) {
                Pbui.requestMenu({
                    subject: root.object,
                    presentation: root.presentationId
                })
            } else if (root.acceptCompatible) {
                Pbui.answer(Pbui.acceptSession.id, root.object)
            } else if (root.primaryAction !== "") {
                Pbui.invoke({action: root.primaryAction, subject: root.object})
            } else {
                Pbui.requestMenu({
                    subject: root.object,
                    presentation: root.presentationId
                })
            }
        }
    }
}
```

The visual child remains application-defined. `Presentation` adds semantics and interaction policy; it does not dictate a chip style.

### 4.6 Attached properties as an alternative

For existing QML applications, an attached property API may reduce wrapper nesting:

```qml
Text {
    text: commit.shortHash

    PbuiPresentation.object: ({
        ptype: "org.example.git.commit",
        id: commit.hash,
        label: commit.shortHash
    })
    PbuiPresentation.primaryAction: "org.example.git.open"
    PbuiPresentation.doc: commit.summary
}
```

The attached object can install hover/tap handlers or expose helper functions. It must avoid interfering with controls that already own gestures; explicit wrappers are safer for complex interactive components.

### 4.7 Qt threading model

All QObject and model mutations visible to QML must occur on the Qt object's owning thread, normally the GUI thread. `QLocalSocket` can live on that thread and use asynchronous signals. CPU-heavy decoding or schema work may be moved to a worker, but normalized updates must be queued back using signals or `QMetaObject::invokeMethod`.

This matters especially for MIQT. Any all-Go experiment must marshal Qt object access to the main thread and avoid calling QML-facing objects from arbitrary Go goroutines.

### 4.8 Go application logic with QML

When the application domain is Go but the UI is QML, use a clear process or language-boundary arrangement:

```text
Option A: one process
  Go domain library <-> C ABI or generated Qt binding <-> C++ QObject models
  C++ PBUI module <-> broker

Option B: two local processes
  Go service <-> application-private IPC <-> QML/C++ frontend
  QML/C++ frontend <-> PBUI broker

Option C: MIQT experiment
  Go domain + MIQT QObject/QML bindings + Go PBUI client
```

Option B adds process management but can isolate crashes and avoid exposing a large C ABI. The PBUI protocol does not need to know which arrangement is used.

### 4.9 Qt Remote Objects: inspiration, not transport replacement

Qt Remote Objects can replicate QObject APIs and properties into replicas, including dynamic replicas that learn their interface after initialization. That resembles part of the desired live-object experience. It is useful conceptual input for:

- revisions and initialization states;
- source/replica ownership;
- reconnect and reinitialization;
- property-change propagation.

It should not replace PBUI's protocol because:

- PBUI must include non-Qt clients;
- PBUI actions and presentation types are not identical to QObject methods and properties;
- broker-mediated permissions, menus, accept sessions, and WM context remain necessary;
- a Qt-native replication protocol would make the semantic plane toolkit-specific.

### 4.10 MIQT and Qamel assessment

#### MIQT

MIQT is the stronger all-Go option. It covers Qt 5.15 and Qt 6.4+, includes QML support, and is MIT licensed, but its own project description warns that it may be immature. It also inherits Qt's licensing and deployment obligations and requires careful adherence to Qt's main-thread model.

Recommended use:

- build one reference PBUI QML application;
- measure binary size, startup, deployment, callback ergonomics, model updates, and main-thread behavior;
- keep the wire protocol and QML-facing contract identical to the C++ plugin design;
- decide later whether MIQT is suitable for first-party applications.

Do not make the PBUI broker or type/action packages depend on MIQT.

#### Qamel

Qamel intentionally binds a limited set of QML classes, describes itself as work in progress, and uses JSON strings for many compound values. That is poorly matched to a system whose core includes nested schemas, menus, context snapshots, live models, and invocation progress. It may remain useful for a tiny Go-to-QML application but should not be the primary PBUI integration target.

---

## 5. Window-manager integration

### 5.1 The WM as context authority and action provider

The WM should remain a privileged PBUI client with two responsibilities:

1. publish authoritative desktop context: focused window, workspace, geometry, floating/fullscreen state, and window lifecycle;
2. register safe semantic actions over `window`, `tile`, `workspace`, and `application-instance` objects.

The current tile and workspace verbs are a good start. They should move into the general action schema and include state, permissions, and explicit results.

Example:

```json
{
  "id": "org.go-go-wm.window.move-to-workspace",
  "subject": {"types": ["org.go-go-wm.window"]},
  "parameters": [
    {
      "name": "workspace",
      "types": ["org.go-go-wm.workspace"],
      "acquisition": "accept"
    }
  ],
  "result": {"types": ["org.go-go-wm.window"]},
  "placements": ["context-menu", "command-palette"],
  "permissions": ["wm.window.move"]
}
```

### 5.2 Window attachment protocol

A client assertion such as `role: wm` or `name: app` is not sufficient for trusted attachment. Add a flow:

```text
1. app connects; broker obtains peer PID/UID from Unix socket credentials
2. app requests a one-use window attachment token
3. app publishes native window hints and token
4. WM observes the new native window and reports its native identity
5. broker correlates PID/hints/token and creates WindowRef
6. app, WM, and broker receive the attachment result
```

A `WindowRef` can contain:

```json
{
  "id": "window://x11/0x04600007",
  "app": "app://org.example.git/instance/7",
  "logical_id": "main",
  "native": {
    "backend": "x11",
    "xid": 7340039,
    "pid": 42173,
    "class": "org-example-git",
    "instance": "org-example-git"
  },
  "workspace": "workspace://3",
  "state": ["focused", "tiled"]
}
```

### 5.3 Safe PBUI actions versus raw control operations

The raw WM socket remains valuable for:

- trusted configuration scripts;
- test harnesses;
- administrative introspection;
- serialized batch layout operations;
- recovery and debugging.

PBUI actions should be narrower and policy-aware. For example:

- `window.focus` may be broadly allowed;
- `window.close` may require user gesture or owner permission;
- `workspace.delete` may require confirmation and reject the last workspace;
- arbitrary `wmcore.Op` batches should remain privileged;
- an application may move its own windows but not unrelated windows without a grant.

This avoids coupling every app to `wmcore.Op` and allows future Wayland or another WM backend to implement the same semantic actions differently.

### 5.4 Menu composition at the WM boundary

When the WM renders a menu for an object attached to a window, it can compose:

- actions registered for the object's type;
- application-local actions exposed through PBUI;
- view/presentation actions such as reveal, copy link, inspect;
- WM actions on the containing window/tile/workspace;
- desktop services such as share, open with, pin, or automate.

Composition should preserve group boundaries and ownership labels. It should not dump every applicable action into one unstructured list.

### 5.5 Mouse documentation and accept indication

The current WM mouse-documentation line and global accept banner are direct descendants of Dynamic Windows and should be retained. Toolkit adapters add local cues:

- compatible object highlight;
- cursor or focus-ring change;
- local prompt and Escape hint;
- accessibility announcement;
- optional dimming of incompatible semantic objects.

The WM remains the desktop-global indicator and cancellation authority for the active seat.

### 5.6 X11 and future Wayland

The current WM is an X11 reparenting manager. The semantic protocol should not encode X11 assumptions beyond the native attachment payload.

For Wayland, the same higher-level model can survive, but implementation changes are substantial:

- the compositor rather than an external client controls placement and focus;
- application identity uses Wayland application IDs and compositor policy;
- global pointer coordinates and arbitrary window control are more constrained;
- a PBUI-aware compositor or compositor plugin is the appropriate WM participant.

Design `WindowRef.native.backend` and action contracts now so that `x11`, `wayland`, and potentially remote/virtual windows can coexist later.

---

## 6. Protocol and broker evolution

### 6.1 Preserve the debuggable v1 transport

NDJSON over a Unix socket is a good development transport:

- inspectable with standard tools;
- easy to fuzz and record;
- language-neutral;
- sufficient for small control messages;
- already hidden behind a codec interface.

Keep it for v1 and likely for v2 initially. Add deterministic CBOR only when profiling demonstrates a need or binary payload pressure becomes material. Large images and documents should not be embedded in one JSON frame; use content-addressed blobs, file descriptors, local URLs, or provider streaming.

### 6.2 Session handshake

Replace a single protocol integer with a negotiated range and feature set:

```json
{
  "t": "hello",
  "seq": 1,
  "client": {
    "app_id": "org.example.git",
    "instance_id": "01J3...",
    "sdk": "pbui-wails/0.1.0"
  },
  "protocol": {"min": 1, "max": 2},
  "features": [
    "action-results",
    "menu-tree",
    "object-ref",
    "window-attach"
  ],
  "requested_capabilities": ["events.publish", "actions.register"]
}
```

Broker response:

```json
{
  "t": "welcome",
  "seq": 1,
  "protocol": 2,
  "connection_id": "conn://broker/42",
  "features": ["action-results", "menu-tree", "object-ref"],
  "granted_capabilities": ["events.publish", "actions.register"],
  "limits": {
    "max_frame_bytes": 1048576,
    "max_actions": 1000,
    "max_pending_requests": 128
  }
}
```

### 6.3 Proposed v2 message families

```text
Session
  hello, welcome, heartbeat, goodbye, error

Manifest and capabilities
  manifest.publish, manifest.withdraw, capability.request, capability.changed

Types and objects
  type.register, type.withdraw
  object.resolve, object.result
  object.watch, object.changed, object.invalidated, object.release

Actions
  action.register, action.withdraw
  action.query, action.list, action.state
  action.invoke, action.accepted, action.progress
  action.output, action.result, action.error, action.cancel

Interaction context
  context.update, context.snapshot
  selection.update, clipboard.update, hover.update

Accept
  accept.start, accept.mode, accept.answer, accept.add
  accept.finish, accept.cancel, accept.clear

Menus
  menu.publish, menu.withdraw, menu.resolve, menu.result
  menu.show, menu.dismissed

Surfaces and windows
  surface.publish, surface.withdraw, surface.open, surface.patch
  surface.event, surface.snapshot
  window.attach.request, window.attach.offer, window.attached
  window.changed, window.detached

Events and state
  event.emit, event.subscribe, event
  state.subscribe, state.snapshot, state.patch, state.resync
```

This is a vocabulary, not a requirement to implement every family at once.

### 6.4 Backward mapping

An additive bridge can preserve current clients:

| v1 | v2 interpretation |
|---|---|
| `Object` | inline immutable object snapshot |
| `Verb` | action with implicit `subject` and no declared result |
| `Accepts` | one follow-up parameter acquired through `accept` |
| `register` | `action.register` batch |
| `verb.invoke` | `action.invoke` with fire-and-forget compatibility reply |
| `verb.run` | owner-side invocation request |
| `menu.request` | resolve actions and either return menu or send `menu.show` |
| `doc.hover` | `hover.update` with documentation only |
| `event` | best-effort event stream |

The broker can expose v2 internally while translating v1 frames at the edge.

### 6.5 Reliable state versus lossy events

The current broker intentionally drops events for slow clients. That is appropriate for telemetry, hover, trace, and repaint hints. It is not appropriate for authoritative state.

Separate two mechanisms:

- **Events:** best-effort, ordered when delivered, optional coalescing, no guarantee of replay.
- **State streams:** versioned snapshots and patches; clients detect revision gaps and request resynchronization.

Use state streams for:

- active accept session;
- action registry;
- type registry;
- window/workspace context;
- selection;
- surface catalog;
- live object revisions.

### 6.6 Reconnect and registration leases

Registrations should belong to a broker connection or explicit lease. On disconnect:

- transient actions and surfaces are withdrawn;
- live object providers are invalidated or marked offline;
- pending invocations receive an owner-disconnected error;
- accept sessions owned by the requester are cancelled;
- durable manifests may be restored only after the same authenticated application reconnects.

SDKs should replay their manifest after reconnect. The broker should assign ownership; client-supplied labels are metadata, not authority.

### 6.7 Security model

Before allowing remote transports, background automation, or sensitive applications, add:

1. **Peer identity:** Unix peer UID/PID and executable metadata where available.
2. **Broker-assigned connection and owner IDs:** do not route authority by a freely chosen client name.
3. **Capabilities:** action registration, event publishing, object resolution, WM operations, clipboard access, and automation should be independently grantable.
4. **User-consent policy:** sensitive operations can require an active gesture, confirmation, or durable grant.
5. **Capability-bearing object references:** providers can expose only operations allowed by the reference.
6. **Schema and size validation:** validate action arguments, object snapshots, menu depth, string lengths, and list counts.
7. **Rate and concurrency limits:** prevent one client from exhausting broker queues or flooding menus/events.
8. **Audit trace:** record caller, action, subject, result, permission decision, and correlation ID for privileged actions.
9. **Secret redaction:** object labels and snapshots may be displayed widely; sensitive fields should require explicit resolution.
10. **No raw browser access:** Wails web content communicates through its Go bridge, not directly with the desktop socket.

### 6.8 Broker decomposition over time

The initial broker can remain one process and one state loop. As features grow, divide internal responsibilities without prematurely creating network services:

```text
SessionManager
Registry       (types, actions, manifests, surfaces)
ContextManager (focus, selection, clipboard, hover)
AcceptManager
InvocationRouter
ObjectRouter
StateJournal
PolicyEngine
```

Each component can own state through the same posted-operation discipline used today. Persistence and journaling can remain optional.

---

## 7. Historical design lineage translated into PBUI

### 7.1 Ciccarelli's presentation-based user interfaces

The 1984 PBUI thesis distinguishes an application database from a presentation database. A presenter maintains the semantic relation between them; a recognizer interprets user operations on presentations as application commands. It argues that presentation and application domains can remain independent while links form a uniform network.

The modern mapping is direct:

| Thesis concept | Proposed system |
|---|---|
| application database | provider-owned domain objects |
| presentation database | registered presentations and surfaces |
| presenter | Wails/QML/terminal/SurfaceSpec renderer adapter |
| recognizer | common click contract, accept manager, action resolver |
| operation on presentation | action invocation with subject/context |
| links across databases | `ObjectRef`, `PresentationRef`, provider routing |

The major lesson is not “draw every UI centrally.” It is “retain the semantic link between the visible representation and the domain object, then make interaction operate through that link.”

### 7.2 Symbolics Genera Dynamic Windows

Dynamic Windows combined typed command input, menus, and mouse-sensitive text/graphics. `accept` could be satisfied by typing or by selecting an appropriately typed presented object. Mouse documentation explained operations available at the pointer. Presentation types participated in a subtype relation, and translators connected one type or input context to another.

PBUI already reproduces several of these ideas:

- global typed accept;
- presentations that can appear in text or graphics;
- type-directed menus;
- a mouse-documentation line;
- actions that themselves request another typed object.

The next steps that most closely recover the Genera model are:

- real type hierarchy and translators;
- command parameters with typed acquisition;
- simultaneous keyboard, menu, and direct-manipulation entry paths;
- richer mouse documentation and action-state feedback;
- nested or scoped input contexts;
- command tables as composable action/menu catalogs.

### 7.3 CLIM

CLIM formalizes presentation types, input contexts, commands with typed arguments, command tables, translators, gestures, and incremental redisplay. A displayed object is recognized when its presentation type is compatible with the current input context; the user may type a command or click a presentation to supply an argument.

The strongest lessons for PBUI are:

- **Commands should have typed arguments**, not merely an object subject plus callback.
- **Type applicability and current enabled state are different.** Translators and testers make this explicit.
- **Command tables are contextual composition units.** They can feed menus, keyboard commands, and palettes.
- **Presentation translators should be named and inspectable.** Silent arbitrary coercion is dangerous.
- **Incremental redisplay is semantic.** A portable surface protocol should patch identified nodes or rows, not continuously ship full pixel buffers.

PBUI should adopt these concepts in protocol-neutral form rather than clone CLIM's Lisp API.

### 7.4 Smalltalk

Smalltalk's relevant contribution is the live object world:

- object identity persists while inspectors and views change;
- tools are ordinary objects in the running system;
- messages are a uniform operation mechanism;
- browsers and inspectors permit immediate traversal and modification;
- the environment can be extended while it is running.

For PBUI, this implies:

- `ObjectRef` must be resolvable and inspectable, not only a copied JSON value;
- inspectors and alternate views should be discoverable by type;
- actions can be registered and withdrawn live;
- desktop state and user tools can be introspected through the same semantic APIs;
- application and development tooling need not be categorically separate.

The system should not expose unrestricted object mutation merely because an inspector exists. Capabilities and provider policy are the modern boundary that a single-user image historically did not need.

### 7.5 HyperCard

HyperCard combined user-authored cards, object-attached scripts, navigation, and message propagation through button/field/card/background/stack layers. Its significance here is not visual nostalgia; it is that end users could assemble persistent interactive surfaces whose behavior participated in a comprehensible message system.

A PBUI analogue would provide:

- user-authored portable surfaces made from typed fields, objects, buttons, tables, and views;
- action references rather than arbitrary shell snippets by default;
- message/action fallback from control to surface to application to desktop services;
- inspectable scripts or workflows attached to surface objects;
- persistent stacks/decks/workspaces restored with semantic object references;
- the ability to turn an ad hoc inspector or REPL result into a durable tool.

The message path should be explicit and debuggable. Unbounded implicit bubbling across the desktop would make action resolution unpredictable.

### 7.6 What not to copy

- Do not require one language runtime or one in-process object memory.
- Do not centralize all rendering in the WM.
- Do not make unrestricted live mutation the default.
- Do not depend on pointer identity across processes.
- Do not permit translator chains to execute invisibly without policy.
- Do not couple semantic type names to toolkit class names.
- Do not turn every UI event into a globally broadcast message.

The objective is the composability of those systems with modern process isolation, multiple toolkits, explicit security, and inspectable protocols.

---

## 8. What this architecture makes possible

### 8.1 Object-aware applications without bilateral integrations

In conventional desktop integration, application A must know how to call application B, or both must agree on a file format and launch convention. PBUI changes the unit of integration:

- applications expose typed objects;
- providers expose actions over types;
- the broker resolves applicable actions;
- the user supplies context and parameters through presentations.

A new diff tool can register an action over two `git-commit` objects and immediately become available in every existing commit presentation. No terminal plugin, Git browser plugin, or WM patch is required.

### 8.2 A universal command palette that is actually contextual

A desktop command palette can combine:

- application commands from the active Wails or QML application;
- actions on the selected semantic object;
- actions on the active window, tile, and workspace;
- open-with/view providers;
- recently used workflows;
- user-authored commands;
- commands whose next argument can be acquired by `accept`.

Unlike a launcher that only starts executables, this palette operates on the current semantic world. Search results can explain why an action is enabled, what subject it will use, and which argument it will request next.

### 8.3 Cross-application typed picking

Typed accept becomes a general desktop interaction primitive:

- “attach a file” can be satisfied by a file row, terminal hyperlink, notebook result, or recent-files surface;
- “choose a color” can be satisfied by a palette, CSS inspector, screenshot sampler, or document swatch;
- “send to workspace” can be satisfied by clicking a workspace chip;
- “compare with” can select a compatible object in any process;
- a command can request multiple objects and show a collection tray before completion.

This is more composable than clipboard-only interaction because the requester declares the type it needs and the system can expose compatible objects and translators.

### 8.4 Semantic clipboard and drag/drop

The ordinary clipboard can carry text and URI fallbacks while PBUI carries identity and type. Copying a database row can preserve:

- human-readable text;
- a stable application URI;
- an object reference with a bounded snapshot;
- allowed actions or resolution capabilities;
- provenance and revision.

A paste target can then offer context-specific actions rather than merely parse text. Semantic drag/drop follows the same model.

### 8.5 Live inspectors and alternate views

View providers can register against types:

```text
org.example.git.commit
  compact chip
  summary row
  detail inspector
  graph node
  raw JSON view
  blame/context view
```

The user can invoke “Inspect” on any object, and the broker can choose or ask among providers. A Smalltalk-like inspector can display live properties through `object.resolve` and `object.watch`. The same object may remain open in multiple views and update by revision.

### 8.6 Dynamic windows and tool surfaces

An action result need not be a scalar. It can publish or open a surface:

- a transient parameter form;
- a comparison view next to its source window;
- a notebook cell inspector;
- a task monitor for a long-running invocation;
- a persistent dashboard composed from object queries;
- a HyperCard-like user tool;
- a floating lens that follows selection;
- a workspace-specific command panel.

The WM can place the surface semantically—adjacent to the source, transient for a window, tiled into the current workspace, or restored to a previous slot—without knowing its internal toolkit.

### 8.7 Desktop-level workflows

Because actions declare types and results, a workflow engine can compose them:

```text
selected file
  -> parse log
  -> extract incident IDs
  -> select one incident
  -> open incident inspector
  -> create investigation workspace
```

A workflow can pause for typed `accept`, stream progress, surface intermediate objects, and remain inspectable. This is significantly safer and more robust than replaying mouse coordinates.

### 8.8 Semantic automation and agents

Automation can target:

- stable action IDs;
- object IDs and revisions;
- declared parameter schemas;
- window/workspace references;
- result objects and invocation status.

This enables:

- deterministic macros;
- integration tests that assert semantic state;
- shell and Go scripting;
- constrained agent operation;
- recording and replay with explicit permission boundaries;
- introspection of available commands before execution.

The current serialized WM operations and event trace are already strong test ingredients. PBUI action and object IDs extend that determinism to graphical applications.

### 8.9 Accessibility and alternative interaction

Semantic descriptors provide information otherwise lost in custom rendering:

- object type and label;
- action names and documentation;
- enabled state;
- typed parameter prompts;
- selection and focus context;
- progress and result descriptions.

Toolkit adapters must still implement platform accessibility APIs, but PBUI can generate a consistent semantic command inventory for screen readers, voice control, switch access, and keyboard-only operation. An accept session can expose a searchable list of eligible objects in addition to pointer highlighting.

### 8.10 Session persistence and world snapshots

A desktop snapshot can record:

- workspaces and window placement;
- application instance manifests;
- surface restoration keys;
- selected object references;
- open inspectors and their view modes;
- user-authored panels;
- workflow state where resumable.

Restoration is semantic rather than pixel-based. Providers resolve still-valid objects, report missing revisions, or offer migration. This approaches the continuity of Smalltalk images and Genera worlds while retaining process isolation.

### 8.11 Collaboration and remote views

A later version could route selected PBUI capabilities across a secure transport:

- share a read-only live object inspector;
- publish a presentation surface to another session;
- request a typed object from a collaborator;
- invoke a narrowly granted action;
- mirror an invocation's progress.

This should be a later layer, not a reason to weaken local security or complicate the first Wails adapter. Object snapshots, capabilities, and explicit provider boundaries are prerequisites.

---

## 9. Worked scenarios

### 9.1 Wails Git browser and QML diff viewer

1. A Wails Git browser presents each commit row as `org.example.git.commit` with a stable hash and repository reference.
2. A QML diff viewer registers `org.example.diff.compare-commits`, whose subject and `other` parameter both accept commit objects.
3. The user right-clicks a commit in the Wails browser. The local or WM menu includes “Compare with…”.
4. Invocation begins. The diff viewer requests acquisition of the `other` parameter.
5. Every Wails, QML, terminal, and WM-native commit presentation highlights locally.
6. The user clicks a commit hash printed in a terminal.
7. The terminal adapter answers with an object reference reconstructed from its `pbui://` hyperlink or provider metadata.
8. The diff viewer reports progress while loading repositories, then publishes a `git-diff` object and a native QML surface.
9. The WM places the diff surface adjacent to the source Wails window because the invocation context includes its `WindowRef`.
10. The resulting diff object gains actions from other providers: save patch, email, inspect changed files, or attach to an issue.

No pairwise Wails-to-QML integration exists. Both integrate once with PBUI.

### 9.2 Color mixing across a notebook and design tool

1. A notebook cell displays a live `color` object.
2. A Wails design tool registers `color.apply-to-selection` and `color.mix`.
3. “Mix with…” starts an accept session for another color.
4. A QML palette highlights compatible swatches; a terminal CSS value is also eligible.
5. The result is another color object, not only a string. It can be presented in the notebook, applied to the Wails selection, copied as CSS, or inspected in a color-space view.

This demonstrates why semantic values should survive through results and not collapse into text.

### 9.3 A universal inspector from a terminal

1. A terminal displays a `pbui://org.example.service/…` hyperlink generated by a CLI.
2. Secondary click asks the broker for actions.
3. `any.inspect` resolves available view providers for the service object.
4. A portable summary surface opens immediately in a WM tile.
5. The user switches that surface to a richer QML topology view.
6. Both views subscribe to the same live object revision stream.
7. A “Restart” action is visible only to a connection holding the required operational capability and asks for confirmation.

### 9.4 Window actions composed with object actions

1. A document object is presented inside a Wails editor window.
2. Its context menu contains document actions: save, export, inspect metadata.
3. The WM contributes containing-window actions: split right, move to workspace, float, fullscreen.
4. A user-installed workflow contributes “Open review workspace”, which creates a workspace, moves the window, opens an issue surface, and starts an accept for a reviewer.
5. Grouping and ownership labels keep these action classes understandable.

### 9.5 HyperCard-like user panel

1. A user creates a portable surface with text, fields, typed object slots, buttons, and tables.
2. Buttons reference registered action IDs or a constrained workflow; they do not embed unrestricted shell code by default.
3. An object slot declares it accepts `org.example.project` and can be filled by clicking any project presentation.
4. The surface persists its object references and layout in a deck-like document.
5. A message fallback allows a button action to be handled by the control, surface script, application, or desktop service in an explicit ordered chain.
6. The panel can be shared or installed as a launcher command after permission review.

This recovers HyperCard's end-user construction model while preserving typed interoperation and process boundaries.

---

## 10. Recommended implementation sequence

### Phase 0 — protocol and trust foundation

**Goal:** make the current broker safe and stable enough for toolkit SDKs.

Implement:

- ADR defining semantic, presentation, and WM planes;
- protocol range and feature negotiation while retaining v1;
- broker-assigned connection/owner IDs;
- Unix peer credential capture;
- client manifest with app and instance identity;
- registration ownership by connection;
- reconnecting Go session wrapper with manifest replay;
- authoritative snapshot endpoint for accept/action registry;
- bounded queues and documented event-loss behavior;
- stable error codes and request deadlines;
- conformance trace fixtures.

Acceptance criteria:

- a client can disconnect/reconnect without duplicate verbs;
- stale owners cannot receive invocations;
- a client cannot claim the privileged WM role without policy;
- a sequence gap can be repaired by snapshot;
- v1 CLI and existing demo applications continue to work.

### Phase 1 — Wails v2 MVP

**Goal:** one polished graphical app participates fully in existing PBUI v1 semantics.

Implement:

- `pbuiwails.Bridge` using the reconnecting session;
- Wails lifecycle hooks;
- generated frontend models;
- React provider and `<Presentation>` component;
- accept state and highlighting;
- invoke/register current verbs;
- local and WM menu modes;
- hover/mouse documentation;
- selection publication;
- X11 window attachment proof of concept;
- reference application, preferably a Git/object browser;
- integration tests against a broker simulator and an Xvfb/Xephyr WM session.

Acceptance criteria:

- a Wails object can answer accept started by another process;
- a terminal object can answer accept started by the Wails app;
- a daemon-provided verb appears in the Wails local menu and runs;
- a Wails-provided verb appears in a WM menu on an object displayed elsewhere;
- reconnect restores registrations and accept state;
- the app remains locally usable with no broker.

### Phase 2 — action, menu, and context model

**Goal:** move from flat verbs to a coherent desktop command system.

Implement:

- v2 action descriptor and v1 mapping;
- invocation IDs, result, error, cancellation, and progress;
- menu tree and dynamic state queries;
- active-window, workspace, pointer, and selection context;
- universal command palette surface;
- safe WM actions over window/tile/workspace objects;
- application menu projection for Wails;
- action grouping, ordering, documentation, and shortcut hints.

Acceptance criteria:

- one action appears consistently in native app menu, context menu, WM menu, and palette where declared;
- dynamic enabled/checked state updates without republishing the action;
- a long invocation reports progress and can be cancelled;
- WM actions enforce ownership/capability policy.

### Phase 3 — live objects, type registry, and generalized accept

**Goal:** support identity, inspectors, translators, and multi-step typed workflows.

Implement:

- namespaced type definitions and subtype matching;
- `ObjectRef` plus inline-object compatibility;
- resolver/watch/invalidation routing;
- provider leases and revisions;
- presentation occurrence registry;
- scoped accept sessions and cardinality;
- named translators with explicit policy;
- semantic clipboard and drag/drop payload;
- generic inspector and view-provider registry.

Acceptance criteria:

- two views of one live object update from the same revision stream;
- an invalid or offline object degrades to its snapshot and reports status;
- an action with two typed parameters can acquire them from different applications;
- translator application is visible and auditable;
- a semantic clipboard object retains a normal text/URI fallback.

### Phase 4 — Qt/QML SDK

**Goal:** a native QML application has parity with the Wails adapter.

Implement:

- C++ `PbuiQt` QML module;
- asynchronous `QLocalSocket` session;
- QObject singleton and action/menu/context models;
- `Presentation.qml` and attached-property option;
- native/local/WM menu modes;
- accept highlighting and accessibility notifications;
- window attachment;
- QML reference application;
- MIQT compatibility spike using the same public semantics.

Acceptance criteria:

- Wails and QML applications exchange typed accepts and actions;
- action models update on the QML thread without races;
- QML menu rendering supports nested and dynamic items;
- reconnect and offline behavior match Wails semantics.

### Phase 5 — portable surfaces and persistent semantic desktop

**Goal:** enable dynamic windows, user-authored tools, and world restoration.

Implement:

- `SurfaceSpec` v2 derived from `uispec`;
- keyed nodes and incremental patches;
- forms, typed slots, list/tree/table views, plots, and inspector panes;
- surface lifecycle and placement hints;
- user-authored deck/panel format;
- restoration keys and desktop snapshots;
- workflow engine over typed actions;
- permission UI and audit inspector.

Acceptance criteria:

- one portable surface renders in the WM and a standalone host;
- a surface survives process restart through snapshot/restoration;
- a user can construct a panel that acquires typed objects and invokes actions;
- patches update identified surface regions without full rerender protocol traffic.

---

## 11. Concrete repository organization

A possible layout inside `go-go-wm` or a companion workspace:

```text
pkg/pbui/
  object.go                  v1 inline object
  wire.go                    v1 codec
  protocolv2/
    envelope.go
    handshake.go
    manifest.go
    types.go
    objects.go
    actions.go
    context.go
    menus.go
    surfaces.go
  schema/
    validate.go
    registry.go
    match.go
  session/
    client.go
    reconnect.go
    replay.go
    snapshot.go
  broker/
    broker.go
    sessions.go
    registry.go
    invocations.go
    context.go
    policy.go

pkg/pbuiwm/
  actions.go
  attachment.go
  context.go

integrations/
  wailsv2/
    pbuiwails/
    frontend/
    examples/
  qtqml/
    PbuiQt/
    examples/

pkg/surfacespec/
  model.go
  normalize.go
  patch.go
  host.go

cmd/
  pbui-inspect
  pbui-actions
  pbui-trace
  pbui-conformance
```

Keep the protocol model packages free of Wails, Qt, X11, Goja, and rendering dependencies.

---

## 12. Design decisions and trade-offs

### 12.1 Toolkit adapter comparison

| Option | Integration effort | Native UX | Go reuse | Long-term risk | Recommendation |
|---|---:|---:|---:|---:|---|
| Wails v2 Go bridge + TS components | Low | Good, webview-based | Excellent | WebKit deployment and DOM/native coordinate seams | **First implementation** |
| C++ Qt/QML plugin | Medium | Excellent | Protocol reuse, not Go client reuse | C++/Qt packaging and licensing obligations | **Second, durable native SDK** |
| MIQT all-Go QML | Medium to high | Excellent if mature enough | High | CGO, generated binding maturity, main-thread complexity | Experimental/reference path |
| Qamel | Low for tiny apps | Limited by binding surface | High | Compound-value and API limitations | Not the primary SDK |
| WM-rendered `SurfaceSpec` | Medium | Consistent PBUI-native style | Excellent | Limited compared with full toolkit; central host complexity | Complementary for dynamic tools |
| Direct toolkit-specific WM APIs | Initially low | Toolkit-specific | Variable | Tight coupling, no interoperability | Reject |

### 12.2 Central versus local menus

| Central WM menu | Local toolkit menu |
|---|---|
| Uniform across terminals and weak clients | Better native placement and accessibility |
| Can compose object and WM actions | Can include rich application-specific controls |
| Desktop-global accept/context visibility | No global coordinate ambiguity |
| One renderer to test | Native platform conventions |
| Risks looking foreign inside polished apps | Requires each adapter to implement rendering |

Use both. The broker resolves semantics; rendering policy is negotiated.

### 12.3 Portable surfaces versus native applications

Portable surfaces maximize inspectability, persistence, and dynamic construction. Native applications maximize rendering capability, complex text input, GPU use, accessibility integration, and established toolkit ecosystems.

The system is strongest when portable surfaces are a **common semantic document format for tools**, not a mandatory universal widget set.

### 12.4 Open type namespace versus central ontology

An open namespace permits experimentation. A completely ungoverned namespace produces collisions and near-duplicate types.

Use:

- reverse-domain or URI-like names for public types;
- a small reserved `pbui.*` and `org.go-go-wm.*` core;
- aliases only through explicit registry entries;
- schema versioning;
- discovery tools that show providers and type relationships;
- community conventions rather than a mandatory central server.

### 12.5 Dynamic live system versus reproducibility

Live action registration and mutable surfaces create power but can make behavior difficult to reproduce. Counter this with:

- manifests and versions;
- broker trace and registry snapshots;
- action-owner provenance in menus;
- deterministic surface specs;
- explicit reload boundaries;
- replayable invocation records;
- tooling that answers “why is this action here?” and “who owns it?”.

---

## 13. Risks and mitigations

### 13.1 Action and type explosion

**Risk:** menus become crowded and semantically duplicate types proliferate.

**Mitigation:** namespaces, groups, ranking, favorites, recency, command-table scopes, provider attribution, type discovery, aliases, and linting tools.

### 13.2 Unpredictable action composition

**Risk:** users cannot understand why an action appears or which process will execute it.

**Mitigation:** display owner/provider, applicability explanation, permission badge, result type, and parameter requirements; provide an action inspector.

### 13.3 Stale live references

**Risk:** objects disappear, revisions change, or providers disconnect.

**Mitigation:** snapshots, revision checks, leases, invalidation events, reconnection state, and explicit stale/offline faces.

### 13.4 UI-thread blocking

**Risk:** broker calls freeze Wails or QML.

**Mitigation:** asynchronous bridge APIs, bounded deadlines, queued callbacks, snapshot caching, and never performing socket I/O on the frontend/GUI thread.

### 13.5 Duplicate semantic and native behavior

**Risk:** a native widget's default click, selection, or context menu conflicts with PBUI.

**Mitigation:** adapter components must be opt-in and compositional; preserve native primary behavior, use the shared priority contract, and let applications choose local versus central menu policy.

### 13.6 Security and confused deputy behavior

**Risk:** an untrusted app registers misleading actions, claims another identity, or persuades a privileged provider to operate on a sensitive object.

**Mitigation:** authenticated ownership, capabilities, explicit caller identity, provider-side authorization, user gesture/confirmation policy, argument schemas, and audit records.

### 13.7 Sensitive data leakage

**Risk:** object snapshots, hover docs, event traces, or universal inspectors expose secrets.

**Mitigation:** minimal public snapshots, field-level resolution permissions, redaction, private types, non-persistent references, and per-subscriber event policies.

### 13.8 Broker as a single point of failure

**Risk:** semantic integration disappears when the broker exits.

**Mitigation:** applications remain locally functional; supervisor restart; reconnect/replay; optional registry journal; no broker ownership of application source data.

### 13.9 WM backend coupling

**Risk:** X11 window IDs leak into general APIs and block Wayland evolution.

**Mitigation:** opaque `WindowRef`, backend-specific native payload, semantic WM actions, and compositor-side implementations for future backends.

### 13.10 Portable surface overreach

**Risk:** `SurfaceSpec` grows into a weak reimplementation of Qt, HTML, or CLIM.

**Mitigation:** focus on inspectable tools, forms, lists, tables, plots, and typed presentations; allow native view providers for complex interactions; keep extension points declarative and versioned.

---

## 14. Testing and conformance

### 14.1 Protocol fixtures

Maintain canonical trace files for:

- handshake and feature negotiation;
- action registration/query/invocation/result;
- accept start/answer/cancel/supersede;
- reconnect and manifest replay;
- owner disconnect during invocation;
- state sequence gap and resync;
- malformed frames and schema limits;
- permission denial;
- object revision conflict;
- menu composition.

Every SDK should run the same traces.

### 14.2 Broker simulator

Provide an in-process or standalone simulator capable of:

- announcing accept mode;
- returning controlled action catalogs;
- injecting disconnects and delayed responses;
- generating sequence gaps;
- recording application messages;
- verifying deadlines and cancellation;
- asserting no GUI-thread blocking.

This permits Wails and QML UI tests without running the real WM.

### 14.3 Toolkit conformance application

Each adapter should implement the same small application:

- presents color, number, file, and custom objects;
- shows primary and secondary actions;
- starts and answers accept;
- displays local and central menus;
- publishes selection and hover docs;
- runs a cancellable action with progress;
- attaches a window;
- demonstrates offline and reconnect state.

Screenshots can differ. Semantic trace output must match.

### 14.4 Property and fuzz testing

Continue the repository's existing strengths:

- fuzz frame and schema decoding;
- property-test type matching and translator search;
- model action-registry invariants;
- race-test disconnect and accept matrices;
- test invocation cancellation and late-result rejection;
- limit menu recursion and object graph cycles;
- golden-test portable surface rendering where applicable.

### 14.5 End-to-end assertions

A full integration test should be able to say:

```text
Given a Wails commit presentation and a QML comparison action,
when the action starts accept and a terminal commit is selected,
then the QML owner receives both typed objects,
reports progress, publishes a diff surface,
and the WM attaches that surface adjacent to the Wails window.
```

The assertion should use protocol traces and WM tree/window snapshots, not image recognition.

---

## 15. Immediate implementation proposal

The smallest useful first change is not protocol v2. It is a Wails adapter that validates the current architecture and exposes exactly where v2 is needed.

### Initial pull-request set

#### PR A — reconnecting PBUI session

- add `pkg/pbui/session` around the current client;
- broker-assigned internal connection ID;
- manifest/verb replay;
- snapshot of active accept and registered verbs;
- connection-state events;
- tests for restart and duplicate prevention.

#### PR B — Wails Go bridge

- `integrations/wailsv2/pbuiwails`;
- lifecycle hooks;
- current v1 object, verb, accept, menu, hover, and event methods;
- namespaced Wails event envelope;
- frontend snapshot endpoint.

#### PR C — React semantic components

- provider, presentation wrapper, accept hook, action query hook;
- local context menu rendering;
- semantic selection publication;
- accessible keyboard/context-menu handling.

#### PR D — reference Wails application

- Git browser or object laboratory;
- provides and consumes verbs;
- proves cross-process accept with existing terminal/CLI tools;
- supports no-broker mode;
- integration test script under Xephyr/Xvfb.

#### PR E — window attachment prototype

- stable Wails class/program hints;
- app manifest plus PID/window correlation;
- PBUI `window`/`tile` object attached to the Wails window;
- menu composition with safe WM actions.

Only after these are used in practice should the full action/result and live-object schema be frozen.

### Suggested first public API

Go:

```go
bridge := pbuiwails.New(pbuiwails.Options{
    AppID:      "org.example.objectlab",
    InstanceID: uuid.NewString(),
    Socket:     os.Getenv("PBUI_SOCKET"),
})

err := wails.Run(&options.App{
    Title:     "Object Lab",
    OnStartup: bridge.Startup,
    OnDomReady: bridge.DomReady,
    OnShutdown: bridge.Shutdown,
    Bind: []interface{}{bridge, app},
})
```

React:

```tsx
function ColorSwatch({ value }: { value: string }) {
  return (
    <Presentation
      object={{ ptype: "color", value, label: value }}
      doc={`Color ${value}`}
      primaryAction="color.use"
    >
      <button className="swatch" style={{ background: value }}>
        {value}
      </button>
    </Presentation>
  );
}
```

The adapter should support the repository's current `Object` form first, then add `ObjectRef` as a compatible union.

---

## 16. Final assessment

The repository has already crossed the conceptual threshold that usually prevents this class of system from existing. Typed presentations, distributed verbs, cross-process accept, a separate broker, WM-rendered menus, semantic regions, a declarative surface IR, and serializable WM operations are present and working together.

Wails v2 does not require a redesign. It requires a disciplined adapter:

- Go PBUI session in the backend;
- generated calls for requests;
- Wails events plus snapshots for unsolicited state;
- semantic React/DOM components;
- local/native and WM menu projection;
- authenticated window attachment.

Qt/QML also fits cleanly when treated as a native protocol client:

- `QObject` singleton;
- `QAbstractListModel` action/menu models;
- reusable presentation components or attached properties;
- asynchronous local socket;
- strict GUI-thread marshalling.

The larger opportunity is to make PBUI the semantic coordination layer of the desktop. The resulting system can combine:

- the PBUI thesis's relation between application objects and visible presentations;
- Genera's typed input contexts, mouse documentation, and simultaneous command styles;
- CLIM's presentation types, translators, typed command arguments, and command tables;
- Smalltalk's live object identity, inspectors, and runtime extensibility;
- HyperCard's end-user construction and persistent scripted surfaces;
- modern toolkit rendering, process isolation, capability security, and testable wire protocols.

The appropriate end state is not “a window manager with more menus.” It is an **interoperable semantic UI fabric** in which windows, objects, commands, selections, and dynamically created views remain connected across applications and toolkits. The WM provides spatial organization and trusted desktop context; PBUI provides semantic organization; Wails, QML, terminals, and portable surfaces provide complementary presentation environments.

---

## Appendix A — proposed core records

### A.1 Application manifest

```json
{
  "app_id": "org.example.git",
  "version": "2.4.0",
  "instance_id": "01J3R6N0E4H5W7QMM54ZCR12M8",
  "display_name": "Git Browser",
  "sdk": "pbui-wails/0.1.0",
  "types": ["org.example.git.commit", "org.example.git.repository"],
  "actions": ["org.example.git.open", "org.example.git.compare"],
  "menus": ["menu://org.example.git/application"],
  "surfaces": ["git-history", "commit-detail"],
  "requested_capabilities": [
    "actions.register",
    "objects.provide",
    "context.selection.publish",
    "window.attach"
  ]
}
```

### A.2 Presentation descriptor

```json
{
  "id": "presentation://org.example.git/main/commit-row/91",
  "surface": "surface://org.example.git/main",
  "object": {
    "ptype": "org.example.git.commit",
    "id": "sha256:8b1f9c2...",
    "label": "8b1f9c2",
    "snapshot": {"summary": "Fix reconnect"}
  },
  "primary_action": "org.example.git.open",
  "doc": "Open commit 8b1f9c2",
  "state": ["visible", "selectable"]
}
```

### A.3 Invocation request

```json
{
  "t": "action.invoke",
  "seq": 47,
  "invocation": "invocation://caller/937",
  "action": "org.example.git.compare",
  "subject": {
    "ptype": "org.example.git.commit",
    "id": "sha256:8b1f9c2..."
  },
  "arguments": {},
  "context_revision": 1882,
  "origin": {
    "surface": "surface://org.example.git/main",
    "presentation": "presentation://org.example.git/main/commit-row/91",
    "window": "window://x11/0x04600007",
    "gesture": "context-menu"
  },
  "deadline_ms": 30000
}
```

### A.4 Progress and result

```json
{
  "t": "action.progress",
  "invocation": "invocation://caller/937",
  "fraction": 0.65,
  "message": "Computing rename detection",
  "details": {"files_processed": 130, "files_total": 200}
}
```

```json
{
  "t": "action.result",
  "invocation": "invocation://caller/937",
  "result": {
    "ptype": "org.example.git.diff",
    "id": "diff://repo/8b1f9c2..9a72e01",
    "label": "8b1f9c2..9a72e01"
  },
  "surfaces": ["surface://org.example.diff/view/8472"]
}
```

---

## Appendix B — SDK conformance checklist

An SDK is conformant when it:

- negotiates protocol/features and exposes connection state;
- uses broker-assigned owner identity;
- replays its manifest after reconnect without duplication;
- provides snapshot resynchronization;
- never blocks the toolkit UI thread on PBUI I/O;
- applies the common primary/secondary click contract;
- highlights compatible presentations during active accept;
- supports keyboard access to presentation menus and accept answers;
- publishes hover documentation with throttling;
- registers and withdraws actions with lifecycle ownership;
- routes incoming invocation requests to the correct toolkit thread;
- validates arguments and returns structured errors;
- supports cancellation and late-result rejection where negotiated;
- exposes local, native-application, and WM menu policies as applicable;
- publishes semantic selection without replacing native selection;
- keeps sensitive object details out of public snapshots;
- degrades safely when the broker is unavailable;
- provides trace logging suitable for integration tests.

---

## Appendix C — source map

### `go-go-wm` source files inspected

- `pkg/pbui/object.go` — typed values, verbs, and `pbui://` URIs.
- `pkg/pbui/wire.go` — protocol v1 messages, NDJSON codec, framing limits.
- `pkg/pbui/broker/broker.go` — connection roles, verb registry, accept state, menus, event bus.
- `pkg/pbui/client/client.go` — concurrent Go client and callback/request API.
- `pkg/pbui/broker/broker_test.go` — accept, cancellation, type mismatch, supersession, disconnect, and verb tests.
- `pkg/apps/apps.go` — semantic regions and common click resolution.
- `pkg/apps/uispec/uispec.go` — declarative surface IR and region generation.
- `pkg/apps/xapp/xapp.go` — standalone X11 PBUI application shell.
- `pkg/wmx11/pbui.go` — privileged WM PBUI client, menus, mouse docs, tile/workspace verbs.
- `pkg/wmx11/ipc.go` — separate trusted WM query/control plane.
- `pkg/wmx11/scripttiles.go` — snapshot-based script surfaces without VM execution in the render loop.
- `pkg/jsmod/*` and repository change history — Goja PBUI/WM/UI modules, event fan, rich REPL, launcher, and dynamic script commands.

### Wails primary documentation consulted

- Wails v2 application structure and Go method binding.
- Generated JavaScript/TypeScript bindings.
- Bidirectional Wails runtime events.
- Application menus and dynamic menu updates.
- Runtime lifecycle and window operations.
- Linux options and WebKit/GTK build requirements.

### Qt primary documentation consulted

- Qt 6 QObject properties, invokable methods, signals, and QML exposure.
- QML singleton registration.
- `QAbstractItemModel`, `QAbstractListModel`, and `QAbstractTableModel` use from QML.
- QML `Menu`, dynamic menu items, and popup modes.
- `QLocalSocket` local-domain socket behavior.
- Qt Remote Objects source/replica and dynamic-replica concepts.

### Historical primary material consulted

- Eugene Charles Ciccarelli IV, *Presentation Based User Interfaces*, MIT Artificial Intelligence Laboratory, 1984.
- Symbolics, *Programming the User Interface* / Dynamic Windows documentation.
- McCLIM manual sections on presentation types, input contexts, commands, translators, and command tables.
- Apple HyperTalk reference material on messages, object scripts, and navigation.
- Squeak/Smalltalk materials on inspectors, browsers, and live object interaction.

