---
title: "Fringe UI DSL Pattern Backend Frontend Walkthrough"
aliases:
  - Fringe UI DSL Pattern Report
  - HAIR 032 033 034 UI DSL Walkthrough
  - Fringe Backend Driven UI DSL Guide
  - Goja DSL Rendering Pattern
_tags_note: "Tags use Obsidian-compatible strings; keep project-report for PARC indexing."
tags:
  - project-report
  - article
  - frontend
  - backend
  - react
  - goja
  - dsl
  - server-driven-ui
  - protobuf
  - design-system
status: active
type: project-report
created: 2026-05-13
repo: /home/manuel/workspaces/2026-04-21/hair-v2/hair-booking
source_tickets:
  - HAIR-032
  - HAIR-033
  - HAIR-034
related_docs:
  - /home/manuel/workspaces/2026-04-21/hair-v2/hair-booking/ttmp/2026/05/13/HAIR-032--declarative-page-builder-dsl-for-fringe-intake-pages/design-doc/01-fringe-page-builder-dsl-analysis-design-and-implementation-guide.md
  - /home/manuel/workspaces/2026-04-21/hair-v2/hair-booking/ttmp/2026/05/13/HAIR-033--make-fringe-widgets-interactive-and-app-ready/design-doc/02-backend-driven-dsl-callback-architecture-guide.md
  - /home/manuel/workspaces/2026-04-21/hair-v2/hair-booking/ttmp/2026/05/13/HAIR-033--make-fringe-widgets-interactive-and-app-ready/design-doc/03-goja-sandbox-multi-step-intake-dsl-guide.md
  - /home/manuel/workspaces/2026-04-21/hair-v2/hair-booking/ttmp/2026/05/13/HAIR-033--make-fringe-widgets-interactive-and-app-ready/design-doc/05-routing-sessions-events-schema-and-rerendering-questions-for-goja-dsl.md
  - /home/manuel/workspaces/2026-04-21/hair-v2/hair-booking/ttmp/2026/05/13/HAIR-034--routing-and-protobuf-centered-dsl-transport-hard-cutover/design-doc/01-routing-sessions-and-protobuf-centered-dsl-transport-hard-cutover-guide.md
updated: 2026-05-14
---

# Fringe UI DSL Pattern Backend Frontend Walkthrough

This report explains the Fringe UI DSL pattern as an engineering system. The focus is not only what files exist, but how the pieces fit together: how a page is represented, how backend JavaScript builds it, how the Go runtime turns callbacks into opaque action ids, how protobuf JSON carries the page to the browser, how React chooses widgets from node kinds and props, and how page authors should write navigation, state, composition, and interaction logic.

The repository is:

```text
/home/manuel/workspaces/2026-04-21/hair-v2/hair-booking
```

The DSL work spans three implementation phases. HAIR-032 introduced a frontend JSON page DSL and React renderer. HAIR-033 moved interaction ownership to a Goja runtime on the backend. HAIR-034 made protobuf JSON the central transport contract for successful flow states, errors, and interaction events. Together, these phases form the current backend-driven UI architecture.

> [!summary]
> The Fringe UI DSL represents pages as JSON trees. Each page has a shell and a list of nodes. Each node has a `kind`, optional `props`, optional `children`, and optional `meta`.
>
> Backend JavaScript running in Goja writes pages with `require("fringe/dsl")`. During render, JavaScript registers callbacks with `ctx.action(...)`. The browser never receives callbacks; it receives opaque action references embedded in page JSON.
>
> The frontend renderer is an interpreter. It reads `node.kind`, extracts typed props from JSON, chooses the matching React atom, molecule, or organism, and wires events back to the backend dispatcher.
>
> Page authors should treat state as backend-owned flow state, navigation as a state transition followed by `render(ctx)`, and composition as stable JSON node trees with stable `meta.id` values.

## 1. The purpose of the DSL

The DSL exists because the Fringe intake UI has two competing requirements. The design system wants reusable React components with clear props and strong visual consistency. The application flow wants pages that can be generated, varied, transported, inspected, and driven by backend logic. Handwritten React is excellent for component implementation, but it is not a good transport format. JSON is a good transport format, but it cannot contain functions, JSX, or component instances.

The DSL resolves this by separating authoring from rendering. Authors use a fluent JavaScript API, but the API emits plain JSON. The backend can send that JSON to the browser. The browser can interpret it into React components. Interaction callbacks remain on the backend, where business logic, session state, and host services live.

The system is intentionally not a general React replacement. It is a constrained page language for Fringe intake and booking screens. It describes pages in terms of known layout primitives, display primitives, selection controls, input widgets, data-display widgets, and shells. When a page needs a new kind of UI, the right change is usually to add a new node kind and renderer mapping, not to smuggle arbitrary HTML through `props`.

## 2. The core model: page, shell, node, action, effect

The DSL has five central concepts.

A **page** is the full screen returned by the backend. It has an identity, title, shell, ordered node list, and optional metadata. The TypeScript contract lives in `web/src/page-dsl/schema.ts`; the Go runtime mirror lives in `pkg/dslgoja/schema.go`; the protobuf transport contract lives in `proto/fringe/dsl/v1/dsl.proto`.

A **shell** is the page-level frame. The same content nodes can be rendered inside a mobile intake shell, a bare shell, or a desktop shell. The shell is selected by `page.shell.kind` and configured by `page.shell.props`.

A **node** is one UI instruction. It says: render this kind of thing with these props, these children, and this metadata. The renderer interprets the node; the node does not contain React code.

An **action reference** is an opaque pointer to a backend callback. It has an `id` and an `event` name. Action refs usually live under `props.actions`, for example `props.actions.change` or `shell.props.actions.next`.

An **effect** is an allow-listed side effect returned next to a page, such as a toast. The page is still the main response; effects are secondary instructions.

The simplified shape is:

```ts
interface DslPage {
  schemaVersion: 1;
  id: string;
  title: string;
  shell: {
    kind: "intake" | "bare" | "desktop";
    props?: JsonObject;
  };
  nodes: DslNode[];
}

interface DslNode {
  kind: string;
  props?: JsonObject;
  children?: DslNode[];
  meta?: {
    id?: string;
    dataSection?: string;
    dataPart?: string;
    region?: "main" | "context";
  };
}

interface ActionRef {
  id: string;
  event: string;
}
```

The important rule is that `props` and `children` must be JSON-compatible. If a value cannot be represented in JSON, it does not belong in the page tree. A callback becomes an action reference. A date becomes a string. A custom object becomes a plain JSON object. A React element becomes a node.

## 3. The full request and render loop

The system has one primary loop. Everything else is detail around that loop.

```mermaid
flowchart TD
  BrowserRoute[Browser route /dsl-goja-demo]
  BackendPage[BackendDslPage]
  Start[POST /api/dsl/flows/fringe.intake.v1/start]
  Runtime[Go dslgoja.Runtime]
  VM[Goja VM with intake.flow.js]
  Render[render(ctx)]
  ActionRegistry[Page-version action registry]
  Proto[protobuf JSON FlowState]
  ReactRenderer[DslPageRenderer]
  Widget[React atoms/molecules/organisms]
  UserEvent[User interaction]
  EventPost[POST /api/dsl/flows/{sessionId}/events]
  Dispatch[FlowSession.Dispatch]
  Callback[Goja callback]
  NextRender[return render(ctx)]

  BrowserRoute --> BackendPage --> Start --> Runtime --> VM --> Render
  Render --> ActionRegistry
  Render --> Proto --> BackendPage --> ReactRenderer --> Widget --> UserEvent
  UserEvent --> EventPost --> Dispatch --> Callback --> NextRender --> Proto
```

The browser starts or resumes a flow. The backend creates or finds a `FlowSession`. The session owns one Goja VM, JavaScript state, the current page, the current action registry, retired actions, processed event ids, and host-module state. The JavaScript flow renders a page. The rendered page is converted to protobuf JSON and returned to the browser. React interprets the JSON into components. When the user interacts, the browser posts an event that names the session, page version, node, event, and opaque action id. The backend checks the event and calls the registered JavaScript callback. The callback mutates backend state and returns the next rendered page.

The frontend is not deciding which page comes next. It reports the interaction and renders the returned page.

## 4. Authoring layer: the fluent DSL builder

There are two builder implementations with the same pattern.

The frontend builder in `web/src/page-dsl/builder.ts` is used for examples, Storybook, and local fixtures. The backend builder source is embedded in `pkg/dslgoja/modules_dsl.go` and exposed to Goja as `require("fringe/dsl")`. Both builders have the same idea: build ordinary JavaScript objects with chainable helper methods, then call `toJSON()` to produce a plain JSON page.

A minimal frontend-authored page looks like this:

```ts
import { page, n } from "./builder";

const servicePage = page("intake-service", "Service")
  .intake({
    step: 1,
    total: 7,
    eyebrow: "Chapter I · The Ask",
    title: "What brings you in?",
  })
  .add(
    n.text("Pick one to start — you can add more later.", { variant: "editorial" }).id("service-intro"),
    n.selectableGroup(serviceOptions, "highlights", { mode: "single" }).id("service-options"),
  )
  .toJSON();
```

A backend-authored Goja page looks similar, but action callbacks are registered with `ctx.action(...)`:

```js
const { page, n } = require("fringe/dsl");

function serviceStep(ctx) {
  return page("intake-service", "Service")
    .intake(shell(ctx, {
      step: 1,
      eyebrow: "Chapter I · The Ask",
      title: "What brings you in?",
      next: "color",
      skip: "color",
    }))
    .add(
      n.text("Pick one to start — you can add more later.", {
        variant: "editorial",
        style: { marginBottom: 16 },
      }).id("service-intro"),
      n.segmented([
        { value: "cut", label: "Cut" },
        { value: "color", label: "Color" },
        { value: "extensions", label: "Extensions" },
      ], ctx.state.category, {
        actions: {
          change: ctx.action("setCategory", function (event) {
            ctx.state.category = event.value;
            return render(ctx);
          }, "change"),
        },
      }).id("category-tabs"),
    )
    .toJSON();
}
```

The authoring style should make page logic legible. A page function should read as a sequence of visible UI decisions: choose the shell, add explanatory text, add controls, attach actions, and assign stable ids.

## 5. The JSON contract

The JSON page is the only thing the renderer needs. A rendered service step contains data like this:

```json
{
  "schemaVersion": 1,
  "id": "intake-service",
  "title": "Service",
  "shell": {
    "kind": "intake",
    "props": {
      "step": 1,
      "total": 7,
      "eyebrow": "Chapter I · The Ask",
      "title": "What brings you in?",
      "actions": {
        "next": { "id": "act_...", "event": "next" },
        "skip": { "id": "act_...", "event": "skip" }
      }
    }
  },
  "nodes": [
    {
      "kind": "text",
      "props": { "text": "Pick one to start — you can add more later.", "variant": "editorial" },
      "meta": { "id": "service-intro" }
    },
    {
      "kind": "segmented",
      "props": {
        "options": [
          { "value": "cut", "label": "Cut" },
          { "value": "color", "label": "Color" }
        ],
        "value": "color",
        "actions": {
          "change": { "id": "act_...", "event": "change" }
        }
      },
      "meta": { "id": "category-tabs" }
    }
  ]
}
```

This page is inspectable, serializable, and stable enough for Storybook, tests, debug panels, and protobuf transport. It also has a strict boundary: the browser can see that an action exists, but cannot see the callback implementation.

## 6. Backend runtime: one flow session, one Goja VM

The runtime lives in `pkg/dslgoja/runtime.go`. The central object is `FlowSession`:

```go
type FlowSession struct {
    ID      string
    FlowID  string
    Version int64

    VM          *goja.Runtime
    flow        *goja.Object
    state       goja.Value
    CurrentPage Page

    CurrentActions  map[string]ActionRegistration
    RetiredActions  map[string]RetiredActionInfo
    ProcessedEvents map[string]InteractionResult

    mu sync.Mutex
    rt *Runtime
}
```

A flow session is a running instance of a flow definition. `flowId` identifies the script, such as `fringe.intake.v1`. `sessionId` identifies one user’s active instance of that script. Two browser tabs should normally get two different sessions unless the app deliberately resumes the same session.

The runtime startup path is:

```text
StartFlow(ctx, flowID, source)
  create goja.Runtime
  create FlowSession with empty action maps
  install modules into the VM
  run intake.flow.js through wrapFlowSource
  call initialState() if present
  store state on session
  call session.Render(ctx)
  return session and first InteractionResult
```

The Go implementation follows that sequence directly in `Runtime.StartFlow`. The script source is wrapped so the VM returns an object with two known exports:

```go
func wrapFlowSource(source string) string {
    return "(function(){\n" + source + "\n; return { initialState: (typeof initialState === 'function' ? initialState : undefined), render: render };\n})()"
}
```

The flow script therefore has a small required interface:

```js
function initialState() {
  return { step: "service" };
}

function render(ctx) {
  return serviceStep(ctx);
}
```

`initialState()` is optional. `render(ctx)` is required.

## 7. The render transaction and callback registry

The runtime does not allow callbacks to be registered at arbitrary times. It registers them during a render transaction. This rule keeps action ids aligned with a specific page version.

During render, `FlowSession.renderLocked` creates a transaction:

```go
tx := &renderTransaction{NextActions: map[string]ActionRegistration{}}
s.activeTx = tx
ctxObj := s.newContextObject()
value, err := s.rt.callWithTimeout(ctx, s, render, goja.Undefined(), ctxObj)
page, err := exportPageValue(s.VM, value)
return s.commitRenderTransaction(tx, page, nil), nil
```

`newContextObject()` exposes `ctx.action` to JavaScript:

```go
_ = obj.Set("action", func(call goja.FunctionCall) goja.Value {
    name := call.Argument(0).String()
    callback, ok := goja.AssertFunction(call.Argument(1))
    event := name
    if len(call.Arguments) >= 3 {
        event = call.Argument(2).String()
    }
    id := "act_" + uuid.NewString()
    s.activeTx.NextActions[id] = ActionRegistration{
        ID: id,
        Name: name,
        Event: event,
        Version: s.Version + 1,
        Callback: callback,
    }
    ref := s.VM.NewObject()
    ref.Set("id", id)
    ref.Set("event", event)
    return ref
})
```

The important properties are:

- Every action id is opaque and newly generated.
- The action id maps to a Goja callback held in `NextActions`.
- The returned value is a JSON-safe object with `id` and `event`.
- `ctx.action` panics if it is called outside a render transaction.

After the page exports successfully, `commitRenderTransaction` retires the previous action map and installs the new one:

```go
func (s *FlowSession) commitRenderTransaction(tx *renderTransaction, page Page, effects []Effect) *InteractionResult {
    for id, action := range s.CurrentActions {
        s.RetiredActions[id] = RetiredActionInfo{...}
    }
    s.Version++
    s.CurrentPage = page
    s.CurrentActions = tx.NextActions
    return &InteractionResult{SessionID: s.ID, PageVersion: s.Version, Page: page, Effects: effects}
}
```

This is one of the most important design decisions in the system. The new action registry is committed only after the page is successfully exported. A callback cannot leave the session halfway updated with a new action registry and a failed page.

## 8. Dispatch: how a browser event becomes a backend callback

When the user interacts with a rendered widget, the frontend posts an `InteractionEvent` to the backend. The backend handler in `pkg/server/handlers_dsl.go` decodes protobuf JSON, converts it to `dslgoja.InteractionEvent`, and calls `session.Dispatch`.

The dispatch algorithm is:

```text
Dispatch(event):
    lock session

    if eventId was already processed:
        return cached result

    if event.pageVersion != session.Version:
        return current page with stale-page effect

    action = CurrentActions[event.actionId]
    if action does not exist:
        if action id is retired:
            return current page with stale-action effect
        else:
            return error

    if event.nodeId conflicts with registered node id:
        return error

    create new render transaction
    convert event into JS object
    call action.Callback(event)
    export returned page
    commit render transaction
    cache result under eventId
    return result
```

The page-version check is an optimistic concurrency check. It prevents a stale browser view from mutating current backend state. If two tabs share one session and tab A advances the flow, tab B’s old action ids no longer mutate the flow. Tab B receives the current page with an informational effect.

The event id is an idempotency key. If the browser retries the same event, the backend can return the cached result instead of invoking the callback twice.

## 9. HTTP API and protobuf transport

The DSL API is mounted with standard-library `http.ServeMux` routes:

```text
POST /api/dsl/flows/{flowId}/start
GET  /api/dsl/flows/{sessionId}
POST /api/dsl/flows/{sessionId}/events
```

The handlers are in `pkg/server/handlers_dsl.go`.

The success envelope is `FlowState` from `proto/fringe/dsl/v1/dsl.proto`:

```protobuf
message FlowState {
  string session_id = 1;
  uint32 page_version = 2;
  Page page = 3;
  repeated Effect effects = 4;
}
```

The page and node messages preserve dynamic widget props through protobuf `Struct`:

```protobuf
message Page {
  uint32 schema_version = 1;
  string id = 2;
  string title = 3;
  string description = 4;
  Shell shell = 5;
  repeated Node nodes = 6;
  google.protobuf.Struct meta = 7;
}

message Node {
  string kind = 1;
  google.protobuf.Struct props = 2;
  repeated Node children = 3;
  NodeMeta meta = 4;
}
```

This is a deliberate compromise. The transport envelope is strongly defined, but widget props remain dynamic enough for the design system to evolve without regenerating protobuf messages for every prop. If a widget becomes central and stable, it can later receive a typed protobuf prop message.

The Go conversion boundary is `pkg/dslgoja/proto_convert.go`. It converts runtime structs into generated protobuf messages and converts incoming protobuf events back into runtime event structs. The frontend boundary is `web/src/page-dsl/backendClient.ts`, which uses generated TypeScript schemas with `fromJson` and `toJson` from `@bufbuild/protobuf`.

A successful browser event post follows this path:

```ts
const protoEvent = fromJson(InteractionEventSchema, interactionEventJson(sessionId, event));
const response = await fetch(`/api/dsl/flows/${sessionId}/events`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(toJson(InteractionEventSchema, protoEvent)),
});
const state = fromJson(FlowStateSchema, await response.json());
```

One detail matters: optional protobuf `Value` fields must be omitted when undefined. The client builds event JSON by adding `value` and `meta` only when they are defined. Sending `value: undefined` is not valid protobuf JSON.

## 10. Frontend bridge: start, recover, dispatch, rerender

The React component that owns the live backend bridge is `web/src/page-dsl/BackendDslPage.tsx`. It is intentionally thin. It does not know flow business logic. It knows how to start or resume a flow, hold the returned `FlowState`, render the page, and send interaction events back.

On mount, it does this:

```text
BackendDslPage load:
    if sessionId prop exists:
        GET /api/dsl/flows/{sessionId}
    else:
        POST /api/dsl/flows/{flowId}/start

    if GET returns dsl_session_not_found:
        clear/recover and start a new flow

    set React state to FlowState
    call onStateChange
```

For interactions, it creates a render context:

```ts
const context = {
  backendDispatch: async (event: DslBackendEvent) => {
    const interactionEvent = {
      ...event,
      eventId: crypto.randomUUID(),
      pageVersion: state.pageVersion,
    };
    const nextState = await client.postDslEvent(state.sessionId, interactionEvent);
    setState(nextState);
    onStateChange?.(nextState);
  },
};
```

Then it renders:

```tsx
<DslPageRenderer page={state.page} context={context} forceDesktop={forceDesktop} />
```

That is the frontend contract. The renderer receives a page and a dispatch function. It does not know how to calculate the next page.

## 11. Route and session behavior

The live demo app is `web/src/LiveDslDemoApp.tsx`. It adds product-shell behavior around `BackendDslPage`:

- It stores the `sessionId` in tab-scoped `sessionStorage`.
- It projects backend page ids into URLs such as `/dsl-goja-demo/service` and `/dsl-goja-demo/photos`.
- It uses `replaceState` for the first page or same-page correction.
- It uses `pushState` when the backend transitions to a new page id.
- It shows a debug panel with route, shell, session, page version, page id, and current page JSON.
- It forces the desktop shell on wide viewports while using the same backend JSON.

The important distinction is that URLs are a projection of backend state, not the owner of backend state. The backend page id determines the route after the backend response succeeds. If the user clicks next, the browser does not optimistically navigate to `/color`; it posts the event, receives `page.id = "intake-color"`, and then updates the URL.

This rule avoids split-brain navigation. The URL follows the flow; it does not lead the flow.

## 12. Frontend renderer: JSON interpreter to React widgets

The renderer lives in `web/src/page-dsl/render.tsx`. Its main function is `renderNode(node, ctx, key)`. It reads `node.kind`, extracts values from `node.props`, and returns a React element.

The renderer is an interpreter with a switch statement:

```tsx
export function renderNode(node: DslNode, ctx?: DslRenderContext, key?: Key): ReactNode {
  const props = node.props || {};
  const common = dataAttrs(node);

  switch (node.kind) {
    case "text":
      return <div key={key} {...common}>{str(props, "text")}</div>;

    case "button":
      return <Button key={key} onClick={() => dispatchAction(ctx, node, props, "click", "action")}>
        {str(props, "children")}
      </Button>;

    case "chipGroup":
      return <ChipGroup
        key={key}
        options={jsonArray(props, "options") as any}
        value={jsonArray(props, "value") as string[]}
        onChange={(value, meta) => dispatchAction(ctx, node, props, "change", "action", value, meta)}
      />;
  }
}
```

The helper functions at the top of the file are part of the contract. `str`, `num`, `bool`, `jsonArray`, and `nullableStr` make dynamic JSON props safe enough to consume. They avoid passing arbitrary `unknown` values straight into React components.

The renderer also attaches data attributes from node metadata:

```ts
function dataAttrs(node: DslNode) {
  return {
    "data-dsl-kind": node.kind,
    "data-dsl-id": node.meta?.id,
    "data-component": node.meta?.dataComponent,
    "data-section": node.meta?.dataSection,
    "data-part": node.meta?.dataPart,
  };
}
```

Those attributes are useful for debugging, screenshots, visual diffing, and targeted tests. A page author should give meaningful `meta.id` values to every important node.

## 13. How widgets are chosen

Widget selection happens in two layers.

The first layer is direct mapping from `node.kind` to a React component. Examples:

| DSL node kind | Rendered component | File family |
| --- | --- | --- |
| `eyebrow` | `Eyebrow` | `web/src/atoms/Eyebrow` |
| `button` | `Button` | `web/src/atoms/Button` |
| `chipGroup` | `ChipGroup` | `web/src/atoms/Chip` |
| `segmented` | `Segmented` | `web/src/atoms/Segmented` |
| `card` | `Card` | `web/src/atoms/Card` |
| `progress` | `Progress` | `web/src/atoms/Progress` |
| `masthead` | `Masthead` | `web/src/molecules/Masthead` |
| `uploadTile` | `PhotoTile` | `web/src/molecules/PhotoTile` |
| `kvRow` | `SummaryRow` | `web/src/molecules/SummaryRow` |
| `personCard` | `StylistCard` | `web/src/molecules/StylistCard` |
| `dayCell` | `DayCell` | `web/src/molecules/DayCell` |
| `calendarGrid` | `DayPickerGrid` | `web/src/molecules/DayCell` |

The second layer is heuristic mapping inside generic node kinds. The most important example is `selectableGroup`. It chooses different molecules based on option shape and layout props:

```text
selectableGroup(options, value, props):
    hasBadges = any option has badge
    hasSubtitles = any option has subtitle
    columns = props.columns or 1

    if hasBadges:
        render ServiceOption rows
    else if hasSubtitles and columns <= 1:
        render BudgetOption rows
    else if columns > 1 and hasSubtitles:
        render BudgetOption grid
    else if columns > 1:
        render TimeSlot grid
    else:
        render ServiceOption fallback rows
```

This heuristic makes the DSL compact. A page author can use `n.selectableGroup(...)` for service selection, budget selection, and time-slot selection, and the renderer chooses the most appropriate existing widget.

The tradeoff is that option shape becomes part of the contract. If an option includes `badge`, it becomes a service-style row. If it includes `subtitle`, it tends toward budget-style presentation. If it has only title/value and columns greater than one, it becomes compact time slots. Page authors should use this deliberately and not accidentally add fields that change the renderer’s choice.

## 14. Composition patterns

A DSL page composes UI in a tree. The top-level page has `nodes`. Some nodes, such as `card`, `stack`, and `grid`, have `children`. The renderer recursively calls `renderNode` for children.

Use `card` when child rows belong to one visual surface:

```js
n.card({ accent: "#6b3a4a", style: { marginBottom: 14 } },
  n.kvRow("Service", selectedServiceName(ctx), editAction(ctx, "editEstimateService", "service")).id("estimate-service"),
  n.kvRow("Tone", ctx.state.tones.join(", "), editAction(ctx, "editEstimateColor", "color")).id("estimate-tones"),
  n.kvRow("Budget", ctx.state.budget, editAction(ctx, "editEstimateBudget", "budget")).id("estimate-budget"),
).id("estimate-card")
```

Use `grid` when the page needs a structural layout primitive independent of the specific child widget:

```js
n.grid(3, { gap: 10 },
  tile("front", "Front"),
  tile("side", "Side"),
  tile("back", "Back"),
).id("photo-grid")
```

Use `stack` when vertical grouping is needed without a card surface:

```js
n.stack({ gap: 12 },
  n.text("Choose a tone family", { variant: "h3" }).id("tone-heading"),
  n.chipGroup(toneOptions, ctx.state.tones, { actions: {...} }).id("tone-chips"),
).id("tone-section")
```

Composition should keep behavior at the interactive node. A `card` should usually not own the edit action for a specific `kvRow`; the row should own it. A `grid` should not own the upload action for a photo tile; the tile should own it. Containers arrange; leaves interact.

## 15. Shells: mobile, bare, and desktop

The renderer chooses a shell in `DslPageRenderer`:

```tsx
const effectiveKind = forceDesktop && page.shell.kind === "intake" ? "desktop" : page.shell.kind;

if (effectiveKind === "intake") {
  return <IntakeShell ...>{content}</IntakeShell>;
}

if (effectiveKind === "desktop") {
  return <DesktopShell ...>{desktopContent}</DesktopShell>;
}

return <div data-component="DslBarePage">{content}</div>;
```

The mobile `intake` shell maps `shell.props` to `IntakeShell` props:

```tsx
<IntakeShell
  step={num(props, "step", 1)}
  total={num(props, "total", 9)}
  eyebrow={str(props, "eyebrow")}
  title={str(props, "title", page.title)}
  nextLabel={str(props, "nextLabel", "Keep going →")}
  onNext={() => dispatchShellAction(context, props, "next", "onNext")}
  onBack={() => dispatchShellAction(context, props, "back", "onBack")}
  onSkip={() => dispatchShellAction(context, props, "skip", "onSkip")}
>
  {content}
</IntakeShell>
```

The desktop shell uses the same page JSON but projects it into a wider layout. It partitions top-level nodes into main content and context-panel content. A node with `meta.region = "context"` always goes to the right-side accent panel. `stat` and `personCard` also go to context automatically. Everything else stays in main content.

This is a useful design pattern: shell choice should be mostly orthogonal to page content. The page author writes semantic nodes. The shell decides density, navigation placement, and contextual layout.

## 16. Navigation patterns for page authors

Navigation is backend state mutation followed by rerender. The flow script in `pkg/dslgoja/flows/intake.flow.js` uses one field, `ctx.state.step`, as the router state:

```js
function goto(ctx, step) {
  ctx.state.step = step;
  return render(ctx);
}

function render(ctx) {
  switch (ctx.state.step) {
    case "color":    return colorStep(ctx);
    case "photos":   return photosStep(ctx);
    case "budget":   return budgetStep(ctx);
    case "estimate": return estimateStep(ctx);
    case "booking":  return bookingStep(ctx);
    case "confirm":  return confirmStep(ctx);
    case "service":
    default:          return serviceStep(ctx);
  }
}
```

The shell helper wires navigation actions into the page shell:

```js
function shell(ctx, config) {
  const actions = {};
  if (config.back) actions.back = ctx.action("back", function () { return goto(ctx, config.back); }, "back");
  if (config.next) actions.next = ctx.action("next", function () { return goto(ctx, config.next); }, "next");
  if (config.skip) actions.skip = ctx.action("skip", function () { return goto(ctx, config.skip); }, "skip");
  return {
    step: config.step,
    total: 7,
    eyebrow: config.eyebrow,
    title: config.title,
    nextLabel: config.nextLabel || "Keep going →",
    actions,
  };
}
```

This pattern is easy to review because all navigation is visible in each step’s shell declaration:

```js
.intake(shell(ctx, {
  step: 3,
  eyebrow: "Chapter III · References",
  title: "Add a few photos",
  back: "color",
  next: "budget",
  skip: "budget",
}))
```

A page author should prefer named steps and a small router over scattered boolean flags. The flow can later grow from `ctx.state.step` into a richer route object, but the principle stays the same: the backend owns the current step, and navigation changes that state.

## 17. State patterns for page authors

`ctx.state` is the flow’s mutable JavaScript state. The flow initializes it in `initialState()`:

```js
function initialState() {
  return {
    step: "service",
    category: "color",
    service: "highlights",
    tones: ["dimensional"],
    damage: 2,
    photos: { front: false, side: false, back: false },
    budget: "flexible",
    day: "2026-06-19",
    time: "12:00",
  };
}
```

Each callback should do three things:

1. Read the event value.
2. Mutate a small part of `ctx.state`.
3. Return `render(ctx)`.

Examples:

```js
actions: {
  change: ctx.action("setService", function (event) {
    ctx.state.service = event.value;
    return render(ctx);
  }, "change"),
}
```

```js
actions: {
  change: ctx.action("setDamage", function (event) {
    ctx.state.damage = Number(event.value);
    return render(ctx);
  }, "change"),
}
```

This keeps callbacks small. The render function remains the only place that chooses the page. A callback that tries to construct a partial UI response directly becomes harder to reason about because it bypasses the step router.

Derived values should be helper functions, not duplicated state. The flow uses helpers such as `selectedServiceName(ctx)`, `estimateRange(ctx)`, and `photoCount(ctx)`. That keeps state minimal and makes rerendering deterministic.

```js
function photoCount(ctx) {
  return Object.keys(ctx.state.photos).filter(function (k) {
    return ctx.state.photos[k];
  }).length;
}
```

## 18. Editing and non-linear navigation

Summary pages use edit actions to jump back to earlier steps. The pattern is:

```js
function editAction(ctx, name, step) {
  return {
    actions: {
      edit: ctx.action(name, function () {
        return goto(ctx, step);
      }, "edit"),
    },
  };
}
```

Then the page attaches edit actions to `kvRow` nodes:

```js
n.kvRow("Service", selectedServiceName(ctx), editAction(ctx, "editEstimateService", "service")).id("estimate-service")
n.kvRow("Tone", ctx.state.tones.join(", "), editAction(ctx, "editEstimateColor", "color")).id("estimate-tones")
n.kvRow("Budget", ctx.state.budget, editAction(ctx, "editEstimateBudget", "budget")).id("estimate-budget")
```

The frontend renderer treats a `kvRow` as editable when either `props.editable` is true or an `edit` action exists:

```tsx
const editable = bool(props, "editable") || !!actionRef(props, "edit");
return <SummaryRow onEdit={editable ? () => dispatchAction(ctx, node, props, "edit", "onEdit") : undefined} />;
```

This is an important pattern. The backend does not tell the frontend to show a specific callback function. It tells the frontend that this row has an `edit` action reference. The renderer knows that an editable summary row should display edit affordance and dispatch the `edit` event when clicked.

## 19. Interaction wiring in the renderer

The renderer has two dispatch modes: backend action refs and local Storybook actions.

The key helper is `dispatchAction`:

```ts
function dispatchAction(ctx, node, props, eventName, localKey, value, meta) {
  const ref = actionRef(props, eventName);
  if (ref && ctx?.backendDispatch) {
    void ctx.backendDispatch({
      nodeId: node.meta?.id || "",
      nodeKind: node.kind,
      actionId: ref.id,
      event: ref.event,
      value,
      meta,
    });
    return;
  }

  if (ref && !ctx?.backendDispatch) {
    console.log(`DSL backend action: ${ref.id}`, { node, eventName, value, meta });
    return;
  }

  action(ctx, props, localKey, node)?.(value, meta);
}
```

This enables the same renderer to work in two environments:

- In the live app, `ctx.backendDispatch` is present, so action refs post to the backend.
- In Storybook/local examples, `ctx.actions` can provide local callbacks for interactive demos.

Shell actions use the same pattern through `dispatchShellAction`, except the node id is synthetic, such as `shell.next`, and the node kind is `intakeShell`.

## 20. Stable ids, React keys, and DOM stability

The renderer uses `node.meta.id` as the React key when present:

```ts
function nodeKey(node: DslNode, index: number): Key {
  return node.meta?.id || `${node.kind}:${index}`;
}
```

Stable ids are not optional for real flows. They are the connection point for three concerns:

- React reconciliation uses them to preserve DOM identity across rerenders.
- Browser events include them as `nodeId`.
- Debugging and visual-diff tooling use them as selectors.

A page author should give stable ids to all meaningful nodes:

```js
n.segmented(...).id("category-tabs")
n.selectableGroup(...).id("service-options")
n.grid(...).id("photo-grid")
n.kvRow(...).id("estimate-service")
```

Do not include action ids in React keys. Action ids intentionally change when a page version changes. If keys include action ids, every render becomes a remount. Use semantic node ids instead.

## 21. Choosing new widgets and extending the DSL

Adding a new widget requires changes at the contract boundary and renderer boundary. The recommended sequence is:

1. Implement or identify the React component in `atoms`, `molecules`, or `organisms`.
2. Add a new node kind to `web/src/page-dsl/schema.ts` if it should be first-class.
3. Add a builder helper to `web/src/page-dsl/builder.ts` for frontend examples.
4. Add the same helper to the backend `dslModuleSource` in `pkg/dslgoja/modules_dsl.go`.
5. Add a renderer case in `web/src/page-dsl/render.tsx`.
6. Add a Storybook page or fixture that exercises the new node.
7. Add backend flow coverage if the real Goja flow uses it.

A new node kind should be added when the widget has distinct semantics. For example, `calendarGrid` is a distinct node kind because it carries date-selection semantics and maps naturally to `DayPickerGrid`. A new prop on an existing node kind is enough when the widget remains the same semantic control with a small visual variant.

The implementation decision can be expressed as:

```text
If the renderer would switch to a different component family, add a node kind.
If the renderer would keep the same component and only change presentation, add a prop.
If the behavior requires backend state, add an action ref under props.actions.
If the behavior requires privileged host work, expose a host module and return JSON props.
```

## 22. Writing a good DSL page

A good page function has a stable shape:

```js
function someStep(ctx) {
  return page("intake-some-step", "Some Step")
    .intake(shell(ctx, {
      step: 4,
      eyebrow: "Chapter IV · Something",
      title: "Make a decision",
      back: "previous",
      next: "next",
    }))
    .add(
      n.text("Explain what the user should do.", { variant: "editorial" }).id("some-intro"),
      n.selectableGroup(options, ctx.state.someValue, {
        mode: "single",
        actions: {
          change: ctx.action("setSomeValue", function (event) {
            ctx.state.someValue = event.value;
            return render(ctx);
          }, "change"),
        },
      }).id("some-options"),
    )
    .toJSON();
}
```

The page function should satisfy these rules:

- The page id should identify the screen, not the current data value.
- The shell should declare navigation in one place.
- The main content should be ordered as it appears on the screen.
- Each important node should have a stable `meta.id`.
- Each callback should mutate backend state and return `render(ctx)`.
- Derived labels should come from helper functions.
- Widget props should be JSON-safe.
- Styling should use design-system defaults first and inline style only for page-specific spacing or rare accents.

## 23. Anti-patterns

Avoid browser-owned navigation for backend DSL pages. A click handler should not decide the next route locally. It should dispatch the backend action and let the returned page update the route.

Avoid serializing function names as trusted commands. The browser should not send `handler: "deleteAppointment"`. It should send an opaque action id that the current page registered.

Avoid unstable node ids. An id such as `option-${Math.random()}` or `photo-${actionId}` defeats React reconciliation and makes event traces difficult to read.

Avoid duplicating derived state. If the estimate range can be computed from service and budget, compute it in a helper. Do not store `estimateRange` separately unless a business event freezes it.

Avoid making containers own leaf behavior. A grid should not decide which photo tile was uploaded. The tile action should carry the tile’s value or node id.

Avoid sending `undefined` through protobuf JSON. Omit optional fields instead.

Avoid putting arbitrary HTML or JSX-like data into props. If a page needs rich structured content, create nodes for that structure.

## 24. Testing and debugging patterns

The DSL has several useful inspection points.

The live route `/dsl-goja-demo` shows the current page JSON in the debug panel. This is the fastest way to verify that the backend returned the page shape you expect.

The backend endpoints can be tested with curl:

```bash
curl -sS -X POST http://127.0.0.1:19080/api/dsl/flows/fringe.intake.v1/start | jq .
```

The returned JSON should include `sessionId`, `pageVersion`, and `page`.

A widget action can be inspected by finding `props.actions`:

```bash
jq '.page.nodes[] | select(.meta.id == "category-tabs") | .props.actions' state.json
```

The frontend renderer can be tested through Storybook examples and React tests. The transport contract is tested on both sides: Go tests validate proto JSON conversion; TypeScript tests validate generated protobuf schemas and frontend parsing.

For rerendering issues, inspect these values first:

- Does the node have a stable `meta.id`?
- Did the backend return a new `pageVersion`?
- Did the action id belong to the current page version?
- Did the browser omit undefined optional values?
- Is the renderer using `node.meta.id` rather than an index key?
- Is an overlay or status message visually covering the target area?

## 25. The pattern in one page-author checklist

When writing a new backend-driven DSL page, use this checklist:

1. Add or reuse a named step in `ctx.state.step`.
2. Add a step function that returns `page(...).intake(...).add(...).toJSON()`.
3. Add the step to `render(ctx)`.
4. Give every important node a stable `.id(...)`.
5. Put navigation actions in `shell(ctx, ...)`.
6. Put widget actions under `props.actions` using `ctx.action(...)`.
7. In each callback, mutate `ctx.state` and return `render(ctx)`.
8. Use existing semantic node kinds before adding new ones.
9. If a new visual component is needed, add a renderer mapping and builder helper.
10. Verify the live JSON in the debug panel or via curl before debugging React.

## 26. The working rule

The DSL is a backend-authored page language with a React interpreter. The backend owns flow state, callbacks, navigation decisions, and privileged operations. The frontend owns rendering, component selection, responsive shell projection, and event transport. Page authors should write JSON-safe page trees with stable ids and small callbacks. Renderer authors should map node semantics to design-system components without leaking business logic into React.

That boundary is what makes the pattern useful. It allows the product flow to evolve in backend JavaScript while keeping the browser as a consistent, inspectable, design-system renderer.
