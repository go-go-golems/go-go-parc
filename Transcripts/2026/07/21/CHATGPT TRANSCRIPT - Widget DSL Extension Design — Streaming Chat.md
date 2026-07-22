# Widget DSL Extension Design

- URL: https://chatgpt.com/c/6a5e891a-5b18-83ea-b26b-8259c18fb307
- Created: 2026-07-20T20:46:18.942Z

## Turn 0 - user

- Message ID: `0fb24674-81fb-45e1-91cc-cace6779c391`

look at github.com/go-go-golems/rag-evaluation-system's widget DSL, and https://parc.yolo.scapegoat.dev/note/research/kb/projects/widget-dsl (and its links to project reports) and then also https://parc.yolo.scapegoat.dev/note/research/kb/projects/go-go-goja and github.com/go-go-golems/go-go-goja (its event emitter, http framework, for example), and https://parc.yolo.scapegoat.dev/note/research/kb/projects/geppetto and https://parc.yolo.scapegoat.dev/note/research/kb/projects/sessionstream (and their github repos).

And github.com/go-go-golems/react-chat/

What I want to do is extend widget.dsl to be able to have streaming SSE/websocket chat bot widgets with embeddable widgets too, integrated into the current widget.dsl / IR renderer approach. 

Analyze, brainstorm, design, make a full report that explains everything to a new developer to the team and what different things are we could do and how they all work and such.

## Turn 1 - assistant

- Message ID: `580765e5-db07-42c7-b1c6-a6a498cb7dc2`
- Model: `gpt-5-6-pro`

I’ll trace the Widget DSL/IR pipeline and related transport/session projects, then compare streaming-chat integration architectures and deliver a developer-facing design report with an implementation roadmap.

## Turn 2 - assistant

- Message ID: `f208265e-5681-4e63-b49a-ccfd82cd4a7a`
- Model: `gpt-5-6-pro`



## Turn 3 - assistant

- Message ID: `46176ec9-09e5-4952-ab61-f6f46b181c78`
- Model: `gpt-5-6-pro`



## Turn 4 - assistant

- Message ID: `834921cc-839e-4237-8873-a1c0b1a5c7aa`
- Model: `gpt-5-6-pro`



## Turn 5 - assistant

- Message ID: `56e006d5-664f-481e-b6b2-3c8d1418fd1d`
- Model: `gpt-5-6-pro`

Goja’s runtime ownership, event-loop scheduling, scoped async callbacks, and EventEmitter appear promising for streaming state; meanwhile, I’m reconstructing inaccessible PARC material from repository documentation.

## Turn 6 - assistant

- Message ID: `93289556-7a49-490e-984a-6e3df5a7f8f9`
- Model: `gpt-5-6-pro`



## Turn 7 - assistant

- Message ID: `d8b30c6a-f4b3-49b6-88ce-d170b81aa1fc`
- Model: `gpt-5-6-pro`



## Turn 8 - assistant

- Message ID: `cef37523-cf57-4606-abc3-047f9386bd1b`
- Model: `gpt-5-6-pro`



## Turn 9 - assistant

- Message ID: `963431d4-a110-45c7-b3e4-9f473b1915b3`
- Model: `gpt-5-6-pro`

The likely design is a generic live-resource adapter: Widget DSL declares typed chat intent, React handles browser state, and SessionStream provides snapshot-first durable events. Schema/version/action validation remains the key gap.

## Turn 10 - assistant

- Message ID: `95c7d5a7-82e5-43a8-b36c-a0514a562fab`
- Model: `gpt-5-6-pro`



## Turn 11 - assistant

- Message ID: `a4d6db2e-4fac-437b-8b79-092a3db5f09f`
- Model: `gpt-5-6-pro`



## Turn 12 - assistant

- Message ID: `c8841e45-83d6-43e5-ada8-9ffb524ca3ac`
- Model: `gpt-5-6-pro`



## Turn 13 - assistant

- Message ID: `bdb71a15-b028-4c33-be57-a7f80c98e94a`
- Model: `gpt-5-6-pro`



## Turn 14 - assistant

- Message ID: `c24778da-8e75-45f2-860f-5049c5706abb`
- Model: `gpt-5-6-pro`



## Turn 15 - assistant

- Message ID: `2e5084e4-cd3d-4f7c-94ab-69b3a9ecf298`
- Model: `gpt-5-6-pro`



## Turn 16 - assistant

- Message ID: `84b56535-2ec3-43f1-b8c2-c84e813a9896`
- Model: `gpt-5-6-pro`



## Turn 17 - assistant

- Message ID: `25d3abba-2f0e-4ad1-80d5-734304b77419`
- Model: `gpt-5-6-pro`



## Turn 18 - assistant

- Message ID: `a9693c1b-0de8-4389-b778-d954e4d1cd3e`
- Model: `gpt-5-6-pro`

# Report complete

[Read or download the full architecture report](sandbox:/mnt/data/widget-dsl-streaming-chat-architecture-report.md)

The report is approximately 9,500 words and includes the current-system walkthrough, alternative architectures, proposed IR and DSL contracts, transport design, embedded-widget protocol, security model, testing strategy, package boundaries, file-level changes, and phased implementation plan.

## Central recommendation

Add a first-class:

```javascript
widget.chat.assistant(...)
```

that lowers to an ordinary:

```json
{
  "kind": "component",
  "type": "ChatSession",
  "props": {}
}
```

The `ChatSession` registry adapter mounts a stateful `react-chat` runtime. **Do not turn the page-level Widget IR into the streaming state store.** This follows the existing architecture: Goja emits serializable UI data, while the React registry owns rendering, behavior, and callback translation. fileciteturn88file0L23-L30 fileciteturn88file0L40-L69

The recommended stack is:

```text
widget.chat.assistant
  -> ChatSession Widget IR node
  -> React ChatSession adapter
  -> react-chat state/runtime
  -> sessionstream snapshot + live events
  -> Geppetto-backed inference
```

For embedded generative UI:

```text
typed, versioned widget instance
  -> allowlisted catalog recipe
  -> WidgetNode
  -> existing WidgetRenderer
```

A complete `WidgetIRDocument` remains available as a restricted escape hatch for trusted server-authored compositions. Arbitrary JSX, HTML, scripts, or model-produced React code should not enter the protocol.

## Transport decision

Use **sessionstream WebSocket plus HTTP commands first**. The existing transport already provides subscription, snapshot, and live UI frames; command ingress is explicitly outside the WebSocket adapter, and production callers are expected to wrap it with authentication, authorization, origin controls, and rate limiting. fileciteturn117file0L11-L30 fileciteturn118file0L58-L73

The current sessionstream Goja wrapper already creates the native WebSocket server, assigns it as UI fanout, attaches the hidden Go `http.Handler`, and exposes it for `app.mount(...)`. fileciteturn112file0L11-L29

Add SSE as a second implementation of the same browser event-transport interface:

```text
ChatEventTransport
  ├── SessionstreamWebSocketTransport
  └── SessionstreamSSETransport
```

SSE should also be a native Go handler, mounted from JavaScript, and should implement the same snapshot-before-live sequence. Supporting WebSocket and SSE simultaneously requires a fanout multiplexer because `Hub.SetUIFanout` currently replaces the previous fanout rather than adding another one. fileciteturn123file0L22-L39

## `react-chat` integration

Much of the required runtime already exists: timeline adapters handle streamed widget lifecycle events and snapshot hydration, including start, patch, completion, removal, and durable `ChatWidgetInstance` entities. fileciteturn109file0L13-L74

The main hardening work is:

- split event transport from HTTP command transport;
- add reconnect, disposal, and component-specific session persistence;
- retain ordinals as decimal strings rather than JavaScript numbers;
- make widget updates idempotent;
- add schema and version metadata to the widget registry.

The current registry contains only a widget name and React component, with no version or prop validation. fileciteturn116file0L12-L22

## Widget DSL changes

The report proposes:

- `widget.chat` and `widget.chat.intent` namespaces;
- `ChatAssistantBuilder`;
- a host-owned connection registry so credentials never enter IR;
- a new serializable `command` action for chat-session commands;
- descriptor, declaration, documentation, schema, golden, Storybook, preview, and browser-test updates.

That matches the v3 project’s existing rule that runtime exports, descriptors, declarations, documentation, examples, and tests are one product surface rather than independent lists. fileciteturn106file0L75-L100

The direct PARC host was unavailable in the browsing environment, so the analysis used the corresponding source notes and linked project reports from `go-go-golems/go-go-parc`.

