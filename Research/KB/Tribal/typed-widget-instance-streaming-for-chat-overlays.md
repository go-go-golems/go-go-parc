---
title: "Typed Widget Instance Streaming for Chat Overlays — How We Do It"
aliases:
  - typed widget streaming
  - chat overlay architecture
  - generative UI widgets
  - sessionstream widgets
  - frontend tool calling
  - chat overlay API
tags: [knowledge-base, tribal, chat, overlay, widgets, streaming, sessionstream, react, typescript]
status: active
type: knowledge-base
created: 2026-05-31
repos:
  - /home/manuel/code/wesen/go-go-golems/go-go-os-frontend
  - /home/manuel/code/wesen/go-go-golems/sessionstream
  - /home/manuel/code/wesen/go-go-golems/geppetto
---

# Typed Widget Instance Streaming for Chat Overlays — How We Do It

> [!summary]
> Generative UI in our chat overlays is expressed as durable typed widget instances, not model-generated JSX or ad-hoc JSON. The model selects widget types and fills parameters; the frontend renders from a typed registry. The architecture has three layers: a headless browser overlay runtime (React is optional), a sessionstream hub (source of truth for commands, events, projections, timeline, snapshots, reconnect), and a Geppetto/Pinocchio runtime (inference, tool loops, profile resolution). Frontend tool calling is a sessionstream-native round trip: backend publishes `ChatFrontendToolCallRequested`, frontend executes or renders, frontend submits `ChatFrontendToolResult`, backend resumes.

## The pattern

The architecture separates three ownership domains:

```
Browser Overlay (TypeScript)     → rendering, browser capabilities, user interaction
Sessionstream Hub (Go)           → source of truth: commands, events, projections, timeline, snapshots
Geppetto/Pinocchio Runtime (Go) → inference, tool loops, profile resolution
```

Each domain owns a narrow contract:

1. **Backend publishes** typed events and timeline entities through sessionstream
2. **Browser reduces** snapshots and UI events into local render state
3. **Host applications register** widgets and tools by stable names and schemas

### Generative UI is typed widget instances

The model does not emit JSX. It emits typed widget instances — durable entities that the browser validates against an allowlisted registry. Unknown widgets and invalid props are rejected or visibly degraded.

```typescript
// The model selects a widget type and fills parameters
{ type: "ProductCard", props: { name: "Boots", price: 89.99, inStock: true } }

// The frontend renders from a typed registry
registry.defineWidget("ProductCard", {
  schema: productCardSchema,
  render: ProductCardComponent,
  actions: { addToCart: { type: "tool", name: "cart.add" } }
})
```

This is the central design decision: **generative UI is a typed widget instance stream, not model-generated UI code.** The model selects types and fills parameters; the frontend renders from a registry. This prevents the model from injecting arbitrary markup, enforces visual consistency, and makes widget schemas versionable and auditable.

### Frontend tool calling: sessionstream-native round trip

Frontend tool calling is not a direct API call. It is a round trip through sessionstream:

```
1. Backend publishes ChatFrontendToolCallRequested (tool name, args, schema)
2. Frontend receives event, executes the tool or renders an approval UI
3. Frontend submits ChatFrontendToolResult (result or rejection)
4. Backend resumes the run with the result
```

Human-in-the-loop tools use the same protocol as automatic frontend tools. The only difference: the call stays pending until the user acts on a React-rendered approval UI.

```
"add boots to cart" → backend requests cart.add tool → page executes it → cart updates → backend resumes
"approve checkout"  → backend requests checkout.confirm tool → page renders approval card → user clicks APPROVE → backend resumes
```

### The browser package is headless-first, React-second

The browser overlay has a headless session runtime plus optional React components. React is one consumer of the runtime, not the owner of the architecture. The split:

| Layer | Responsibility | React-dependent? |
|---|---|---|
| Transport | WebSocket connection, snapshot-before-live reconnect, protobuf envelope | No |
| Redux store | Timeline state, overlay slices, widget instances | No |
| Tool registry | Schema validation, execution routing | No |
| Widget registry | Type schemas, render functions | No (render functions are) |
| React overlay | ChatPanel, ChatMessages, ChatComposer, WidgetOutlet | Yes |

This means the same runtime can power a terminal client, a non-React embed, or a React overlay without duplicating the transport and state layers.

### Sessionstream is the source of truth

Not the frontend. Not the backend. Sessionstream owns:

- **Commands** — client-initiated actions
- **Canonical backend events** — handler-published domain events
- **UI projections** — derived live client-facing events
- **Timeline projections** — derived durable state
- **Snapshots** — persisted state for reconnect
- **Reconnect behavior** — snapshot-before-live: subscribe → receive full timeline snapshot → receive future live UI events

The frontend reduces snapshots and live UI events into local render state. If the frontend disconnects and reconnects, sessionstream replays the snapshot, and the frontend rebuilds state from the timeline.

### Existing implementation: `@go-go-golems/os-chat`

The `os-chat` package already implements much of this architecture:

- Redux timeline and overlay slices
- Protobuf envelope handling over WebSocket
- Renderer registry with typed schemas
- Widget outlet for rendering registered widgets
- Tool registry with execution routing

The overlay package should build on this substrate, not replace it.

## Why we do it this way

**Typed widgets prevent model-generated UI code from becoming a security and consistency risk.** If the model emits raw JSX, it can inject arbitrary markup, break visual consistency, and create unversioned UI artifacts. Typed widget instances make the API surface auditable: every widget type has a schema, and the frontend validates props against that schema.

**Sessionstream as source of truth enables correct reconnect behavior.** If the frontend owned the conversation state, a page refresh would lose state. Sessionstream's snapshot-before-live contract means the frontend can rebuild from durable timeline entities after a disconnect.

**Headless-first architecture enables non-React consumers.** A terminal client, a script-tag embed, or a native app can all consume the same sessionstream transport and Redux store without depending on React.

**Frontend tool calling through sessionstream keeps the backend in control.** If tool handlers called backend APIs directly, the backend would lose visibility into what tools were called and what results were returned. The sessionstream round trip makes every tool invocation a durable event.

Alternatives considered and rejected:
- **Model-generated JSX.** Security risk, consistency risk, no schema validation, no version control.
- **Product-specific package (`@golems/commerce-assistant`)**. The real abstraction is a generic chat overlay with typed widgets. Ecommerce widgets are a preset layer, not the package identity.
- **Frontend as source of truth.** A page refresh loses state. Reconnect becomes a frontend-local problem instead of a durable backend contract.

## Evidence

| Report | Date | Contribution |
|---|---|---|
| [[ARTICLE - Chatbot Overlay Framework - TypeScript and Frontend Tool Calling Deep Dive]] | 2026-05-29 | Implementation: TypeScript transport, Redux timeline, widget registry, tool registry, frontend tool calling round trip, human-in-the-loop tools |
| [[ARTICLE - Chat Overlay API - Sessionstream Widget Runtime Deep Dive]] | 2026-05-29 | Architecture: headless-first browser package, sessionstream as source of truth, widget instances as durable entities, ordinals as strings |
| [[ARTICLE - Chat Overlay API - Two Proposals for a Typed Widget Streaming Architecture]] | 2026-05-29 | Two proposals comparison, existing os-chat substrate, ecommerce-specific vs generic package tension |

## Working rules

1. **Generative UI is typed widget instances, not model-generated JSX.** The model selects widget types and fills parameters; the frontend renders from a registry. Validate all widget props against schemas. Reject or visibly degrade unknown types.

2. **Frontend tool calling is a round trip through sessionstream.** Never call backend APIs directly from a tool handler. The round trip makes every invocation a durable event.

3. **Human-in-the-loop tools use the same protocol as automatic frontend tools.** The only difference is the call stays pending until the user acts. No special API surface for approval flows.

4. **Sessionstream is the source of truth.** Not the frontend, not the backend. Sessionstream owns commands, events, projections, timeline, snapshots, and reconnect behavior.

5. **The browser package is headless-first, React-second.** React is one consumer of the runtime, not the owner of the architecture. Transport, state, and registries must work without React.

6. **Keep ordinals as strings in JavaScript state and public JSON.** Avoid numeric ordinals that require careful comparison. String ordinals sort lexicographically and serialize without precision issues.

7. **Keep Geppetto free of overlay-specific concepts.** Geppetto runs inference and tool loops. It should not know about widget types, browser capabilities, or React rendering.

8. **Widget schemas are versioned and auditable.** Every widget type has a schema. The frontend validates props against that schema. Schema changes are breaking changes and must be versioned.

9. **Reconnect uses snapshot-before-live.** On reconnect, receive the full timeline snapshot first, then subscribe to live UI events. This is a sessionstream contract, not a frontend implementation detail.

10. **Reject or visibly degrade unknown widgets and invalid props.** Never silently ignore a widget type the frontend doesn't recognize. Either reject it (error boundary) or render a degraded placeholder that makes the unknown type visible.

## Gotchas

1. **Unresolved tension: ecommerce-specific vs generic package.** The package could be `@golems/commerce-assistant` or `@go-go-golems/chat-overlay`. This decision affects every downstream consumer. The current implementation chose the generic direction, but the tension is not fully resolved — ecommerce widgets may drift back into the core package.

2. **Model-generated UI code is a security and consistency risk.** Typed widgets prevent the model from injecting arbitrary markup, but the temptation to let the model emit JSX directly will recur. Every time someone proposes "just let the model generate the UI," point them to this rule.

3. **Reconnect behavior must be defined by sessionstream, not the frontend.** If the frontend implements its own reconnect logic (e.g., re-sending commands), it will diverge from the sessionstream contract and produce duplicate events. Always use snapshot-before-live.

4. **Protobuf envelope handling is not trivial.** The `ServerFrame` oneof has multiple frame types. A consumer that only handles `UiEventFrame` will miss `SnapshotFrame`, `SubscribedFrame`, and `ErrorFrame`. Handle all frame types or document which ones you intentionally skip.

5. **Widget registry schemas must not drift from backend types.** If the backend emits a `ProductCard` with fields the frontend schema doesn't expect, the frontend will either reject or degrade. Keep schemas in sync between Go backend types and TypeScript frontend schemas. Consider generating TypeScript types from Go or protobuf definitions.

6. **Tool handler errors must be submitted as `ChatFrontendToolResult`, not thrown.** If a tool handler throws an exception, the backend never receives a result and the run hangs. Always catch errors and submit them as tool results with error information.

## Related KB entries

- [[Tribal/bubbletea-streaming-llm-uis]] — Terminal streaming LLM UIs with sessionstream. This entry covers web streaming UIs with the same sessionstream substrate.
- [[Tribal/pi-extension-event-seams]] — Similar event-driven architecture in Pi extensions: observe state, transform at mutable hooks, display through surfaces.
- [[Tribal/goja-runtime-ownership-and-context-propagation]] — The goja runtime owner pattern is used in Geppetto for JavaScript tool execution within the chat overlay backend.
