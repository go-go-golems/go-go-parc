---
title: "Chat Overlay API: Two Proposals for a Typed Widget Streaming Architecture"
aliases:
  - Chat Overlay API
  - Chat Overlay Deep Dive
  - Chatbot React API
  - chat-overlay
  - commerce-assistant
tags:
  - article
  - sessionstream
  - geppetto
  - pinocchio
  - react
  - chat-overlay
  - widgets
  - protobuf
  - ecommerce
status: active
type: article
created: 2026-05-29
repo: /home/manuel/workspaces/2026-05-29/chatbot-react
---

# Chat Overlay API: Two Proposals for a Typed Widget Streaming Architecture

This article examines two independent proposals for building a browser-side chat overlay that renders typed widget instances streamed from a sessionstream backend, powered by Geppetto inference and Pinocchio configuration. Both proposals share the same foundational architecture—sessionstream as the substrate, Geppetto as the LLM runtime, Pinocchio as the configuration layer—but differ in API surface design, naming conventions, target audience framing, and the granularity of their widget lifecycle models.

The purpose of this article is not to declare a winner. It is to trace the architectural decisions in both proposals, connect them to the real packages that exist in the workspace today, identify where they agree and diverge, and surface the design tensions that must be resolved before implementation begins.

> [!summary]
> - Both proposals converge on a three-layer architecture: browser overlay + sessionstream hub + Geppetto/Pinocchio runtime.
> - The central design decision is that generative UI is a typed widget instance stream, not model-generated UI code.
> - The existing `@go-go-golems/os-chat` package already implements much of Proposal B's architecture with Redux, protobuf envelope handling, and a renderer registry.
> - The main unresolved tension is whether the package is an ecommerce-specific product (`@golems/commerce-assistant`) or a generic headless chat overlay (`@go-go-golems/chat-overlay`).

## Why this note exists

Two separate design documents were written for the same system. They overlap in intent but differ in specificity. Before writing any code, the engineering team benefits from understanding what each proposal prioritizes, what the existing codebase already provides, and where the two proposals make incompatible assumptions. This article provides that analysis by walking through each proposal's architecture, comparing their API surfaces, grounding them in the real source packages, and identifying the design decisions that remain open.

## The existing substrate

Both proposals build on three packages that already exist in the workspace. Understanding their current state is necessary before evaluating what the proposals add.

### sessionstream

`sessionstream` is a Go framework for session-scoped, event-driven applications. Its core model is:

1. A client sends a command for a session.
2. A handler publishes canonical backend events.
3. UI projections derive live client-facing events.
4. Timeline projections derive durable state.
5. Hydration stores persist snapshots for reconnect.

The transport contract is defined in `proto/sessionstream/v1/transport.proto`. The wire format is protobuf JSON over WebSocket. The reconnect contract is snapshot-before-live: a subscribing client first receives the full timeline snapshot, then receives future live UI events.

```protobuf
message ServerFrame {
  oneof frame {
    HelloFrame hello = 1;
    SnapshotFrame snapshot = 2;
    SubscribedFrame subscribed = 3;
    UiEventFrame ui_event = 5;
    ErrorFrame error = 6;
    PingFrame ping = 7;
    PongFrame pong = 8;
  }
}
```

The `SnapshotFrame` carries `repeated SnapshotEntity` values, each with a `kind`, `id`, ordinal metadata, and a `google.protobuf.Any` payload. The `UiEventFrame` carries a named event with an ordinal and an `Any` payload. Browser clients must treat `uint64` ordinals as protobuf JSON strings, not JavaScript numbers, because JavaScript `number` cannot represent all `uint64` values without precision loss.

The schema contract requires concrete protobuf messages at the top level of every command, event, UI event, and timeline entity. Top-level `google.protobuf.Struct` payloads are rejected by the schema-vet analyzer. Open-ended data may appear inside a concrete message at a deliberate boundary, but the envelope itself must be named and typed.

### Geppetto

Geppetto is the Go runtime core for LLM applications. It provides provider-agnostic inference engines, first-class tool calling, middleware composition, typed turn/block data, session lifecycle, and JavaScript bindings through Goja (`require("geppetto")`).

The Geppetto runtime model is registry-first and profile-first. Runtime configuration is resolved from profile registries using stackable sources (YAML files, SQLite databases, DSN strings). Applications own the final `StepSettings` and pass explicit engine configuration. Geppetto does not provide overlay abstractions in its runtime composition.

Key Geppetto packages:

- `pkg/turns`: canonical conversation model with `Turn` and `Block` types
- `pkg/inference/engine`: provider engine interfaces
- `pkg/inference/toolloop`: orchestration loop for tool calls, results, and retries
- `pkg/inference/middleware`: inference middleware pipeline
- `pkg/profiles`: profile registries with stack resolution and provenance

The JavaScript API exposes `gp.turns`, `gp.engines`, `gp.profiles`, `gp.schemas`, `gp.middlewares`, `gp.events`, and `gp.tools`.

### Pinocchio

Pinocchio is the interactive CLI and webchat layer that consumes Geppetto as infrastructure. It owns:

- Layered unified config documents (global, project, override)
- Engine-profile registry discovery and resolution
- Prompt repositories mapped to command hierarchies
- Webchat runtime with WebSocket transport
- Turn and timeline persistence

Pinocchio resolves profiles from a registry source stack with deterministic precedence. The `pinocchio js` command bootstraps a Goja runtime with both `require("geppetto")` and `require("pinocchio")`, allowing scripts to resolve engine profiles and build inference engines from the same configuration path the CLI uses.

## The existing frontend: `@go-go-golems/os-chat`

Before the proposals were written, a substantial React chat package already existed in the monorepo. The `@go-go-golems/os-chat` package at `/home/manuel/workspaces/2026-05-29/chatbot-react/go-go-os-frontend/packages/os-chat/` provides:

**WebSocket manager (`wsManager.ts`)** — A full `WsManager` class that manages connection lifecycle, connection nonce tracking (to handle concurrent connect/disconnect races), hydration via HTTP timeline snapshots, frame buffering during hydration, and post-hydration replay with sequence-based deduplication. The manager emits lifecycle events for each phase (connect.begin, ws.open, hydrate.start, hydrate.snapshot.applied, replay.complete, hydrate.complete) and tracks connection status through Redux actions.

**Semantic event registry (`semRegistry.ts`)** — A handler registry that maps semantic event types to typed handlers. Events arrive as `{ sem: true, event: { type, id, data, metadata, seq } }` envelopes. The registry decodes protobuf payloads using `@bufbuild/protobuf` `fromJson`, extracts usage metadata, manages stream tracking (multiple concurrent LLM streams per conversation), and dispatches timeline upserts. Default handlers cover `timeline.upsert`, `llm.start`, `llm.delta`, `llm.final`, `llm.thinking.*`, `log`, `agent.mode`, and `debugger.pause`.

**Timeline slice (`timelineSlice.ts`)** — A Redux Toolkit slice that manages per-conversation timeline state as an ordered entity list. It supports `upsertEntity` with version-based conflict resolution, `addEntity` for append-only entries, `mergeSnapshot` for hydration, `applySnapshot` for full replacement, and specialized actions for suggestions with consumption tracking.

**Renderer registry (`rendererRegistry.ts`)** — A registration system for timeline renderers keyed by entity kind. Built-in renderers cover `message`, `tool_call`, `tool_result`, `status`, and `log`. Extension renderers can be registered at runtime via `registerTimelineRenderer(kind, renderer)`. The registry notifies subscribers when its contents change, enabling React components to re-render when new renderers are added.

**Profile and conversation management** — Hooks for profile selection, conversation creation, and profile switching. HTTP transport for chat commands. Profile API integration.

This package is not a proposal. It is working code. Any new chat overlay package must either extend `os-chat` or explicitly replace parts of it, and the burden of justification falls on the replacement path.

## Proposal A: `@golems/commerce-assistant`

Proposal A frames the package as an ecommerce-specific product called `@golems/commerce-assistant`. The central API is `createCommerceAssistant()`, which bundles session management, sessionstream transport, overlay configuration, ecommerce context (page, product, cart, locale, currency), typed widgets, and frontend actions into a single factory call.

### Architecture layers

```text
Browser
  └─ createCommerceAssistant()
       ├─ overlay UI
       ├─ message state
       ├─ widget registry
       ├─ ecommerce context
       └─ sessionstream transport

Backend
  └─ sessionstream hub
       ├─ commands
       ├─ backend events
       ├─ UI projections
       ├─ timeline entities
       └─ hydration

LLM/runtime
  └─ Pinocchio + Geppetto
       ├─ profile/config resolution
       ├─ model engine
       ├─ tools
       └─ widget-producing tool calls
```

### Widget definition

The widget API uses `defineWidget()` with a namespaced string name (`commerce.product-carousel`), a version field, a Zod schema for props validation, a React component reference, and per-widget action definitions. Actions can either run locally (with a `run` function) or delegate to the backend (with a `command` string).

```ts
const productCarouselWidget = defineWidget({
  name: "commerce.product-carousel",
  version: "1",
  schema: z.object({
    title: z.string().optional(),
    products: z.array(z.object({
      id: z.string(),
      handle: z.string(),
      title: z.string(),
      imageUrl: z.string().url().optional(),
      price: z.object({ amount: z.number(), currency: z.string() }),
      badges: z.array(z.string()).default([]),
    })),
    reason: z.string().optional(),
  }),
  component: ProductCarousel,
  actions: {
    addToCart: {
      input: z.object({
        productId: z.string(),
        variantId: z.string(),
        quantity: z.number().default(1),
      }),
      command: "CommerceWidgetAction",
    },
  },
});
```

The widget registry is allowlisted: the backend can only request widgets that the frontend has registered. A backend request for an unregistered widget produces no render output.

### Widget lifecycle

Proposal A describes a widget instance stream using three backend events:

- `CommerceWidgetUpserted` — creates or replaces a widget instance with initial props
- `CommerceWidgetPatched` — applies a partial update to existing props
- `CommerceWidgetCompleted` — marks the widget as ready
- `CommerceWidgetRemoved` — removes the widget from the UI

Widget instances are also durable timeline entities. On reconnect, the snapshot includes committed widget entities.

### Protobuf schema approach

Proposal A is explicit about protobuf schema design. Widget event payloads use concrete top-level messages with `google.protobuf.Any` for the widget-specific props:

```protobuf
message WidgetInstanceUpsertedEvent {
  string instance_id = 1;
  string widget_name = 2;
  string widget_version = 3;
  string parent_message_id = 4;
  WidgetStatus status = 5;
  google.protobuf.Any props = 6;
}
```

Each widget type gets its own concrete props message:

```protobuf
message ProductCarouselProps {
  string title = 1;
  repeated ProductCardProps products = 2;
  string reason = 3;
}
```

This approach satisfies sessionstream's schema-vet policy because the top-level message is concrete, and the open-ended data is inside a deliberate boundary (`Any` wrapping a concrete widget message).

### Widget/tool bridge

Proposal A introduces a build-time code generation concept: a widget definition produces four outputs simultaneously:

1. A frontend component definition (React)
2. An LLM-callable tool schema (for Geppetto tool calling)
3. A protobuf payload schema (for sessionstream transport)
4. A timeline entity payload (for hydration)

The generation step would be:

```ts
widgets.generate({
  out: {
    proto: "proto/commerce/widgets/v1/widgets.proto",
    ts: "src/generated/widgets.ts",
    manifest: "public/widgets.manifest.json",
    tools: "agent/generated/widget-tools.js",
  },
});
```

The generated tool would allow the agent to call:

```js
await tools.showProductCarousel({
  title: "Best matches",
  products,
  reason: "These match the size, budget, and color constraints.",
});
```

Which publishes `CommerceWidgetUpserted` through the sessionstream pipeline, gets projected into a UI event, and renders in the browser.

### Geppetto/Pinocchio integration

Proposal A describes a Pinocchio JS agent factory:

```js
const gp = require("geppetto");
const commerce = require("commerce-assistant");

const resolved = gp.profiles.resolve({ profileSlug: "shop-assistant" });
const engine = gp.engines.fromResolvedProfile(resolved);

module.exports = commerce.createAgent({
  engine,
  runtime: gp.runner.resolveRuntime({
    systemPrompt: commerce.prompts.ecommerceConcierge(),
    toolNames: ["catalog.search", "catalog.compare", "cart.propose", "widget.render"],
  }),
  tools: {
    searchProducts: commerce.tools.searchProducts(catalog),
    renderWidget: commerce.tools.renderWidget(),
  },
});
```

The agent publishes canonical backend events into sessionstream. It does not return UI directly.

### Starter widget set

Proposal A names these first-priority widgets:

| Widget | Purpose |
|--------|---------|
| `commerce.product-card` | Single product display |
| `commerce.product-carousel` | Horizontal product recommendations |
| `commerce.variant-picker` | Product variant selection |
| `commerce.compare-table` | Side-by-side product comparison |
| `commerce.cart-preview` | Current cart contents |
| `commerce.cart-diff` | Proposed cart changes |
| `commerce.coupon-card` | Discount or bundle offer |
| `commerce.order-status` | Order tracking display |
| `commerce.review-summary` | Product review aggregation |
| `commerce.size-fit-guide` | Size/fit recommendation |
| `commerce.policy-card` | Policy information display |
| `commerce.checkout-handoff` | Checkout redirect action |

The four highest-priority widgets cover the purchase funnel stages: discovery (`product-carousel`), decision (`compare-table`), configuration (`variant-picker`), and conversion (`cart-preview`).

## Proposal B: `@go-go-golems/chat-overlay`

Proposal B frames the package as a generic headless chat overlay called `@go-go-golems/chat-overlay`. The central API is `createChatOverlay()`, which is domain-agnostic by default and adds ecommerce as an optional preset.

### Architecture layers

The layer structure is identical to Proposal A, but the ownership framing is different. The frontend package is not ecommerce-specific. Ecommerce semantics live in an optional preset:

```ts
import { ecommercePreset } from "@go-go-golems/chat-overlay/ecommerce";

createChatOverlay({
  ...ecommercePreset(),
  transport,
});
```

### Widget definition

Proposal B's `defineWidget()` takes a dot-separated name (`product.carousel`), a description, a schema (Zod or JSON Schema), and a render function that receives a context object with `props`, `instance`, `overlay`, and `status`:

```ts
const ProductCarouselWidget = defineWidget("product.carousel", {
  description: "Display a list of recommended products.",
  schema: z.object({
    title: z.string().optional(),
    products: z.array(z.object({
      id: z.string(),
      title: z.string(),
      imageUrl: z.string().optional(),
      price: z.string().optional(),
    })),
  }),
  render: ({ props, instance, overlay }) => (
    <ProductCarousel
      {...props}
      onProductClick={(product) => {
        overlay.command("product.clicked", {
          widgetId: instance.id,
          productId: product.id,
        });
      }}
    />
  ),
});
```

Notable differences from Proposal A:

- No `version` field on widgets
- No `component` property; uses a `render` function instead
- No per-widget action definitions; actions go through `overlay.command()`
- Widget names use dot notation without a namespace prefix
- Schema can be Zod or plain JSON Schema (important for non-React environments)

### Widget lifecycle

Proposal B describes a three-phase widget instance stream:

1. `WidgetInstanceStarted` — initial props, status `"draft"` or `"streaming"`
2. `WidgetInstanceDelta` — partial props patch (JSON merge patch semantics)
3. `WidgetInstanceCompleted` — status `"ready"`

This is a subset of Proposal A's lifecycle (Proposal A adds `WidgetPatched` and `WidgetRemoved`). Both proposals agree that widget instances are durable timeline entities that survive reconnects through snapshot hydration.

### Frontend event model

Proposal B normalizes all sessionstream UI events into a compact client-side event model:

```ts
type OverlayEvent =
  | MessageEvent
  | MessageDeltaEvent
  | WidgetEvent
  | SuggestionEvent
  | StatusEvent
  | ErrorEvent;
```

With an explicit event name mapping:

```ts
const eventMap = {
  UserMessageAccepted: "message",
  AssistantMessageStarted: "message",
  AssistantMessageDelta: "message.delta",
  AssistantMessageCompleted: "message",
  WidgetInstanceStarted: "widget",
  WidgetInstanceDelta: "widget",
  WidgetInstanceCompleted: "widget",
  SuggestionsUpdated: "suggestions",
  RunStatusChanged: "status",
};
```

This normalization layer is absent from Proposal A, which expects the frontend to consume sessionstream event names directly.

### Backend command model

Proposal B defines four core commands:

| Command | Purpose |
|---------|---------|
| `chat.submit` | Send a user message with optional context |
| `widget.action` | Dispatch a widget action |
| `context.patch` | Update session context |
| `handoff.request` | Request human handoff |

Ecommerce-specific commands (`cart.add`, `coupon.apply`, `checkout.start`) are layered on top via `overlay.command()`. This produces a clean separation between the generic overlay protocol and domain-specific extensions.

Proposal A uses domain-prefixed command names (`CommerceSendMessage`, `CommerceStopRun`, `CommercePatchContext`, `CommerceWidgetAction`) that embed the ecommerce domain directly in the protocol.

### Transport interface

Proposal B defines a transport interface:

```ts
type ChatTransport = {
  connect(input: {
    sessionId: string;
    onSnapshot: (snapshot: SessionSnapshot) => void;
    onEvent: (event: UIEventFrame) => void;
    onError: (error: Error) => void;
  }): Promise<ChatConnection>;
  send(command: ChatCommand): Promise<void>;
};
```

This interface is pluggable. The `sessionstreamTransport()` factory is one implementation; others could use HTTP polling, SSE, or different WebSocket protocols. The transport receives typed frames with string ordinals.

### React integration

Both proposals provide React bindings. Proposal B is more explicit about the component hierarchy:

```tsx
<ChatOverlayProvider config={overlayConfig}>
  <Storefront />
  <ChatBubble />
  <ChatPanel>
    <WidgetOutlet />
  </ChatPanel>
</ChatOverlayProvider>
```

With hooks:

```ts
const chat = useChatOverlay();
chat.open();
chat.send("Which lens works with this camera?");
chat.command("cart.add", { productId: "sku_123" });
```

And widget registration via `useOverlayWidget()`:

```tsx
function EcommerceWidgets() {
  useOverlayWidget(productCarousel);
  useOverlayWidget(cartReview);
  return null;
}
```

### Non-React integration

Proposal B explicitly addresses non-React environments with two mechanisms:

1. **Web components** — a `<shop-chat>` custom element for HTML integration
2. **Plain JS widget registration** — a `ShopChat.defineWidget()` API with DOM-based rendering

```js
ShopChat.defineWidget("coupon.offer", {
  schema: { type: "object", required: ["code", "label"], properties: { ... } },
  render(el, { props, overlay }) {
    el.innerHTML = `<div class="coupon">...</div>`;
    el.querySelector("button").onclick = () => {
      overlay.command("coupon.apply", { code: props.code });
    };
  }
});
```

This is important for the stated target environments: Shopify theme scripts, WooCommerce stores, and custom storefronts that may not use React.

## Where the proposals agree

Both proposals converge on these architectural decisions:

**Sessionstream is the source of truth.** Neither proposal puts authoritative state in the browser. Commands go to sessionstream. Events come from sessionstream. Projections derive UI state from canonical backend events. Hydration restores state from timeline entities after reconnect.

**Generative UI is typed widget instances, not model-generated code.** The LLM never emits JSX or HTML. It emits a typed widget request with validated props. The frontend instantiates a registered renderer. This is the fundamental design principle that distinguishes these proposals from approaches like raw markdown rendering or code-generation-based dynamic UI.

**Widget instances are durable.** Widgets are timeline entities. They survive page reloads, reconnects, and server restarts because they are projected into the hydration store alongside messages and other conversation state.

**The React layer is thin.** The runtime must work from plain JavaScript. React is an optional rendering layer, not a requirement. Both proposals expose imperative APIs (`assistant.send()`, `overlay.command()`) that work without React.

**Ordinals are strings in JavaScript.** Both proposals acknowledge the sessionstream requirement that `uint64` ordinals must not be coerced through JavaScript `number`.

**Geppetto publishes events, not UI.** The LLM runtime calls tools, tools produce work, and work publishes canonical backend events. UI state is always a projection of those events, never a direct output of the inference pipeline.

## Where the proposals diverge

### Package identity: ecommerce-specific vs. generic

Proposal A names the package `@golems/commerce-assistant` and embeds ecommerce semantics (cart, products, variants, coupons) in the core API. The `createCommerceAssistant()` factory takes ecommerce-specific configuration like `visitorId`, `cartId`, `storefront.page()`, and `storefront.currentProduct()`.

Proposal B names the package `@go-go-golems/chat-overlay` and treats ecommerce as an optional preset. The core API is domain-agnostic. The `createChatOverlay()` factory takes generic session, transport, theme, and context configuration. Ecommerce widgets are added through the preset or manual registration.

This is the most consequential design tension. An ecommerce-specific package has a clearer value proposition for shop integrators (one import, one factory call, done) but limits reuse. A generic package can serve any chat overlay use case (support desks, operator dashboards, internal tools) but requires more configuration for the ecommerce case.

The existing `os-chat` package is already generic. It renders timeline entities of any kind through a pluggable renderer registry. Making the new package ecommerce-specific would create a parallel implementation of concepts `os-chat` already provides.

### Widget lifecycle granularity

Proposal A defines four widget events: `Upserted`, `Patched`, `Completed`, `Removed`. This gives fine-grained control over widget state transitions and supports explicit removal.

Proposal B defines three: `Started`, `Delta`, `Completed`. There is no explicit removal event. Widgets accumulate in the timeline until the session ends.

The difference matters for long-lived sessions where widgets become stale. An inventory comparison widget from ten minutes ago may no longer be relevant. Proposal A can explicitly remove it; Proposal B would either leave it in the timeline or require a separate removal mechanism.

### Event name scoping

Proposal A uses domain-prefixed names: `CommerceSendMessage`, `CommerceWidgetUpserted`, `CommerceCartProposalCreated`. This makes event names self-documenting but creates a naming obligation for every domain that builds on sessionstream.

Proposal B uses generic names: `chat.submit`, `widget.action`, `context.patch`. The event mapping layer normalizes backend-specific names into a stable client-side vocabulary.

The sessionstream framework itself uses unscoped names in its chat demo (`ChatStartInference`, `ChatUserMessageAccepted`, `ChatTokensDelta`). The `os-chat` frontend uses type strings like `timeline.upsert`, `llm.start`, `llm.delta`, `llm.final` in its semantic event registry. Neither of these uses domain prefixes.

### Schema approach: Zod-only vs. Zod + JSON Schema

Proposal A uses Zod schemas exclusively for widget validation. This requires the widget definition to run in a JavaScript/TypeScript environment that supports Zod.

Proposal B supports both Zod schemas and plain JSON Schema objects. This is necessary for the non-React integration path, where widget definitions may come from plain JavaScript or even from server-delivered configuration.

### Widget versioning

Proposal A includes a `version` field on every widget definition. The backend specifies which version it is requesting, and the frontend can maintain backward-compatible renderers for older versions.

Proposal B has no versioning mechanism. Widget schemas are implicitly versioned by the package version.

Versioning matters for long-lived deployments where the frontend and backend may update independently. An ecommerce site that customizes widget renderers needs to know whether a widget's props shape has changed.

### Build-time code generation

Proposal A introduces a `createWidgetCatalog()` + `widgets.generate()` pipeline that produces protobuf schemas, TypeScript types, widget manifests, and LLM tool definitions from a single widget definition source. This is a build-time concern that Proposal B does not address.

Code generation solves a real problem: keeping four representations of the same widget (React component, protobuf schema, LLM tool, timeline entity) in sync is error-prone when done manually. But it also introduces build complexity and a code generation pipeline that must be maintained.

## What the existing code already provides

The `@go-go-golems/os-chat` package already implements much of what both proposals describe. The mapping between proposal concepts and existing code is direct:

| Proposal concept | Existing `os-chat` implementation |
|------------------|----------------------------------|
| Widget registry | `rendererRegistry.ts` — `registerTimelineRenderer(kind, renderer)` |
| Widget instance storage | `timelineSlice.ts` — `TimelineEntity` with kind-based upsert |
| Sessionstream transport | `wsManager.ts` — WebSocket with hydration, buffering, replay |
| Event normalization | `semRegistry.ts` — typed handlers for `timeline.upsert`, `llm.*` |
| Protobuf decoding | `semRegistry.ts` — `fromJson()` with `@bufbuild/protobuf` schemas |
| Ordinal handling | `wsManager.ts` — sequence-based deduplication during replay |
| React component rendering | `ChatConversationWindow.tsx` — renders timeline entities via registered renderers |
| Profile selection | `useCurrentProfile.ts`, `profileSlice.ts` |
| Connection lifecycle | `chatSessionSlice.ts` — connection status, streaming state, error tracking |

The gap between `os-chat` and the proposals is primarily in three areas:

1. **Widget action dispatching.** `os-chat` renders entities but has no mechanism for widgets to send actions back to the backend. The proposals add `overlay.command()` and per-widget action definitions.

2. **Widget-specific props validation.** `os-chat` renders any entity kind with a registered renderer, but the renderer receives `Record<string, unknown>` props. The proposals add Zod schema validation per widget.

3. **Ecommerce context injection.** `os-chat` has no concept of storefront context (page, cart, product, locale). The proposals add context providers that feed into commands.

These gaps are incremental extensions, not architectural rewrites. The question is whether to extend `os-chat` in-place or create a new package that imports and extends it.

## Implementation sequence

Both proposals suggest similar implementation sequences. Proposal B is more explicit about the ordering:

1. **Core event store** — a reducer that consumes snapshots and live UI events into `{ messages, widgets, suggestions, status }`. The existing `timelineSlice` and `chatSessionSlice` already provide most of this.

2. **Sessionstream transport** — WebSocket subscribe, snapshot-before-live hydration, command POST, reconnect, ordinal-safe string ordering. The existing `WsManager` already provides this.

3. **Widget registry** — `defineWidget`, validation, lazy loading, fallback renderer. The existing `rendererRegistry` provides the registration and resolution mechanism but lacks per-widget schema validation.

4. **Overlay shell** — floating launcher, panel, composer, message list, widget outlet. This is the primary new UI work.

5. **Domain preset** — product carousel, cart review, coupon, checkout nudge. These are new React components that render validated widget props.

6. **Backend command bridge** — mapping frontend commands to typed sessionstream commands with protobuf payloads.

7. **LLM tool bridge** — tool calls that emit canonical backend events producing widget instances.

## Open design decisions

### Package scope

Should the new package be `@golems/commerce-assistant` (ecommerce-specific) or `@go-go-golems/chat-overlay` (generic with ecommerce preset)? The existing `os-chat` package is already generic. Creating a second generic package would duplicate effort. Creating an ecommerce-specific package that imports `os-chat` as a dependency would extend rather than replace.

### Relationship to `os-chat`

Should the new code extend `os-chat` directly, or should it be a separate package that consumes `os-chat` as a dependency? The `os-chat` package already provides the transport, state management, and renderer infrastructure. Duplicating that infrastructure in a new package would create maintenance burden and version drift.

### Widget lifecycle events

Should the widget lifecycle use four events (Started, Patched, Completed, Removed) or three (Started, Delta, Completed)? The removal event is useful for long-lived sessions but adds protocol complexity. A middle ground would be to support removal through timeline entity tombstones, which sessionstream already models via the `tombstone` field on `SnapshotEntity`.

### Code generation

Should the build pipeline include code generation from widget definitions? Proposal A's `createWidgetCatalog().generate()` pattern is elegant but introduces build tooling. An alternative is to define protobuf schemas manually and generate only TypeScript types, which is the current approach in `os-chat`.

### Script-tag delivery

Should the package support non-React, script-tag installation? Proposal B explicitly supports this with web components and plain JS widget registration. This is necessary for Shopify/WooCommerce integration but adds build complexity (a separate UMD bundle).

## Recommended resolution

The most productive path forward is to:

1. **Extend `os-chat` rather than replace it.** The package already provides the transport, state, and renderer infrastructure. Widget action dispatching and context injection can be added as new modules.

2. **Use the generic naming from Proposal B.** `chat-overlay` as a concept layer on top of `os-chat` avoids duplicating infrastructure while keeping the package reusable for non-ecommerce applications.

3. **Adopt Proposal A's widget versioning and protobuf patterns.** The `version` field and concrete protobuf messages per widget type are correct design decisions that cost little to implement and provide forward compatibility.

4. **Adopt Proposal B's event normalization and transport interface.** The `eventMap` pattern and pluggable `ChatTransport` interface decouple the frontend from sessionstream-specific event names.

5. **Defer code generation.** Start with hand-written protobuf schemas and generated TypeScript types (the current pattern in `os-chat`). Add `createWidgetCatalog().generate()` when the widget set stabilizes.

6. **Support both React and plain JS widget rendering.** This is necessary for the target deployment environments and aligns with the existing `rendererRegistry` pattern (renderers are just React components that receive an entity; a DOM-based alternative is straightforward).

## Related notes

- [[PROJ - CoinVault - RAG Web Chat for Gold Coin Inventory]] — the first production application using sessionstream + Pinocchio + Geppetto for a web chat interface
- The sessionstream repository at `/home/manuel/workspaces/2026-05-29/chatbot-react/sessionstream/` contains the framework, transport proto, and chat demo
- The Geppetto repository at `/home/manuel/workspaces/2026-05-29/chatbot-react/geppetto/` contains the LLM runtime, profile registries, and JavaScript bindings
- The Pinocchio repository at `/home/manuel/workspaces/2026-05-29/chatbot-react/pinocchio/` contains the webchat runtime, configuration layer, and prompt repositories
- The `os-chat` package at `/home/manuel/workspaces/2026-05-29/chatbot-react/go-go-os-frontend/packages/os-chat/` contains the existing React chat UI and state management
