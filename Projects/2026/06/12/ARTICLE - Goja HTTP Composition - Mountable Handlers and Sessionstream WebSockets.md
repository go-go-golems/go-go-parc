---
title: "Goja HTTP Composition: Mountable Handlers and Sessionstream WebSockets"
aliases:
  - Goja HTTP Composition
  - Mountable Goja HTTP Handlers
  - Express Mountable Handlers
  - Sessionstream Goja WebSocket Mounting
tags:
  - article
  - go
  - goja
  - xgoja
  - http
  - websocket
  - sessionstream
  - architecture
  - protobuf
status: active
type: article
created: 2026-06-12
repo: /home/manuel/workspaces/2026-06-12/goja-sessionstream
---

# Goja HTTP Composition: Mountable Handlers and Sessionstream WebSockets

This report explains the current state and design direction of the Goja HTTP composition work across `go-go-goja` and `sessionstream`. The immediate implementation delivered two connected capabilities. First, `sessionstream` now has phase-1 Goja bindings that let JavaScript construct typed protobuf commands, register schemas, create hubs, handle commands, publish events, define projections, and observe fanout. Second, `go-go-goja` now has a shared mountable `http.Handler` ABI so JavaScript Express applications can mount Go-backed HTTP handlers exposed by other native modules.

The key design point is precise: JavaScript is the composition language, but Go remains the owner of HTTP server machinery, WebSocket upgrade handling, protobuf message identity, and sessionstream execution semantics. JavaScript connects Go-backed pieces together. It does not have to reimplement the parts that are already correct in Go.

> [!summary]
> - `sessionstream` now exposes a phase-1 `require("sessionstream")` module with schema registration, Hub wrappers, JavaScript command handlers, projections, EventEmitter fanout, and WebSocket server objects.
> - `go-go-goja` now exposes a shared `gojahttp.AttachHTTPHandler` / `HTTPHandlerFromValue` ABI and `express.app().mount(...)`, allowing JavaScript to mount Go `http.Handler` values.
> - Existing Goja HTTP route patterns already support `:param` captures and segment-level `*` wildcards; mounted handlers use prefix matching instead of route-pattern matching.
> - The next integration step is to make `ss.webSocket.server(hub)` attach the new `gojahttp` handler ref, then add a runnable smoke app that calls `app.mount("/ws", ss.webSocket.server(hub))`.

## Why this work exists

The original problem came from `sessionstream`. The framework is protobuf-first. Commands, backend events, UI events, and timeline entities are concrete Go protobuf messages. A JavaScript integration cannot treat these as arbitrary maps without weakening the framework's type boundary. If a command enters the Hub as a map, the Hub has to recover type information after the fact. If the command enters as a concrete `proto.Message`, the JavaScript binding preserves the same contract that Go callers use.

The first part of the solution was the `go-go-goja` protobuf builder generator. It lets JavaScript construct real Go protobuf messages through fluent builders:

```javascript
const pb = require("sessionstream.examples.chatdemo.v1")

const command = pb.StartInferenceCommand.builder()
  .prompt("Explain ordinals")
  .build()
```

The returned value is a JavaScript object with a hidden Go protobuf reference. Go code can recover the concrete message:

```go
msg, ok := protogoja.MessageFromValue(value)
cmd := msg.(*chatdemov1.StartInferenceCommand)
```

That solved typed payload construction. It did not solve HTTP composition. The sessionstream WebSocket transport is a Go `http.Handler`; it performs WebSocket upgrades and manages subscription/hydration behavior. The Goja Express module owns the HTTP host. Before the mountable handler work, JavaScript could register JavaScript routes, but it could not take a Go-backed WebSocket server object from one module and mount it into the Express host owned by another module.

The new shared handler ABI solves that composition problem.

## The two repositories and the relevant commits

The work spans two sibling repositories in the workspace:

```text
/home/manuel/workspaces/2026-06-12/goja-sessionstream/go-go-goja
/home/manuel/workspaces/2026-06-12/goja-sessionstream/sessionstream
```

The main `sessionstream` implementation commit is:

```text
14ca1f54b1edb88819bd085cd597351aa0da1e7a
Add Goja bindings for sessionstream
```

A small follow-up in `sessionstream` updated the shared docmgr vocabulary:

```text
382ca49ad1a32e9cb28e3f113480b1a0d42d7a47
Update docmgr vocabulary for HTTP mount ticket
```

The `go-go-goja` HTTP composition commits are:

```text
f7965d47206728bac5a2d6fd639a005c15e11fb6
Add mountable HTTP handlers to Express

a0c82e2af4e948f6e644b15e0b083036ec2e5e8d
Diary: validate mountable HTTP handlers
```

The `go-go-goja` branch was also merged with current `origin/main`, which brought in xgoja v2 source graph and TypeScript changes:

```text
3f1b66a Merge remote-tracking branch 'origin/main' into task/goja-sessionstream
```

## The architecture in one view

The final intended application shape is this:

```javascript
const express = require("express")
const ss = require("sessionstream")
const pb = require("sessionstream.examples.chatdemo.v1")

const app = express.app()

const schemas = ss.schemas()
  .registerCommand("ChatStartInference", pb.StartInferenceCommand)
  .registerEvent("ChatUserMessageAccepted", pb.UserMessageAcceptedEvent)
  .registerUIEvent("ChatMessageAccepted", pb.ChatMessageUpdate)
  .registerTimelineEntity("ChatMessage", pb.ChatMessageEntity)

const hub = ss.hub({ schemas })

hub.command("ChatStartInference", (cmd, session, pub) => {
  pub.publish("ChatUserMessageAccepted",
    pb.UserMessageAcceptedEvent.builder()
      .messageId("m1-user")
      .role("user")
      .content(cmd.payload.prompt)
      .build())
})

app.get("/", (_req, res) => res.send("sessionstream goja smoke"))
app.mount("/ws", ss.webSocket.server(hub))
```

The corresponding implementation graph is:

```mermaid
flowchart TD
  JS[JavaScript app]
  Express[require("express")]
  SS[require("sessionstream")]
  PB[Generated protobuf builder module]
  Host[gojahttp.Host]
  Hub[sessionstream.Hub]
  WSServer[sessionstream transport/ws.Server]
  HandlerRef[gojahttp hidden http.Handler ref]
  Browser[Browser WebSocket client]

  JS --> Express
  JS --> SS
  JS --> PB
  PB -->|hidden ProtoMessage refs| SS
  SS --> Hub
  SS --> WSServer
  WSServer --> HandlerRef
  Express --> Host
  JS -->|app.mount("/ws", ws)| Express
  Express -->|unwrap handler ref| HandlerRef
  HandlerRef -->|register handler| Host
  Browser -->|GET /ws upgrade| Host
  Host --> WSServer
```

The important boundary is the hidden reference. JavaScript sees an ordinary object with methods such as `connections()`. Go code sees an object carrying a hidden `http.Handler`. Express does not need to import sessionstream. Sessionstream does not need to import Express. Both modules agree on a small ABI in `pkg/gojahttp`.

## Sessionstream Goja bindings

The new sessionstream module lives at:

```text
sessionstream/pkg/js/modules/sessionstream
```

It exposes `require("sessionstream")` with these phase-1 exports:

```javascript
ss.version
ss.schemas(input?)
ss.hub(options?)
ss.eventEmitterFanout(emitter)
ss.fanout.eventEmitter(emitter)
ss.webSocket.server(hub)
```

The Hub wrapper exposes:

```javascript
hub.submit(sessionId, commandName, payload)
hub.snapshot(sessionId)
hub.command(name, handler)
hub.uiProjection(handler)
hub.timelineProjection(handler)
hub.run()
hub.shutdown()
```

This is not a JavaScript reimplementation of sessionstream. It is a wrapper over the Go framework. The Go `Hub` still validates payload types, assigns ordinals, invokes command handlers, applies projections, updates hydration state, and fans out UI events.

### Schema registration from generated prototype tokens

The schema wrapper accepts generated message namespace objects:

```javascript
const schemas = ss.schemas()
  .registerCommand("ChatStartInference", pb.StartInferenceCommand)
  .registerEvent("ChatUserMessageAccepted", pb.UserMessageAcceptedEvent)
  .registerUIEvent("ChatMessageAccepted", pb.ChatMessageUpdate)
  .registerTimelineEntity("ChatMessage", pb.ChatMessageEntity)
```

Each generated message namespace carries a hidden prototype token attached by the protobuf builder generator. Sessionstream reads that token and registers the corresponding Go protobuf prototype in `SchemaRegistry`.

This design removes a source of duplication. The same generated module provides:

- a JavaScript builder API;
- a TypeScript declaration surface;
- a hidden protobuf prototype token for host modules;
- built message values carrying hidden concrete `proto.Message` refs.

### Payload conversion rule

When a JavaScript value is used as a command, event, UI event, or timeline entity payload, the binding follows this order:

```text
1. Try protogoja.MessageFromValue(value).
2. If successful, validate the protobuf descriptor against the registered schema.
3. Clone the message and pass it into sessionstream.
4. Otherwise, encode the JS value as JSON and decode it with protojson using the registered schema.
```

In pseudocode:

```go
func jsValueToProto(registry, kind, name, value) (proto.Message, error) {
    if msg, ok := protogoja.MessageFromValue(value); ok {
        validateDescriptor(registry, kind, name, msg)
        return proto.Clone(msg), nil
    }

    prototype := lookupPrototype(registry, kind, name)
    bytes := json.Marshal(value.Export())
    msg := prototype.ProtoReflect().New().Interface()
    protojson.UnmarshalOptions{DiscardUnknown: false}.Unmarshal(bytes, msg)
    return msg, nil
}
```

The first path is the primary typed path. The second path is a compatibility path for simple scripts and tests. The fallback is strict: unknown fields fail rather than being silently discarded.

### Command handlers and publishers

A JavaScript command handler receives three values:

```javascript
hub.command("ChatStartInference", (cmd, session, pub) => {
  pub.publish("ChatUserMessageAccepted", eventPayload)
})
```

The incoming `cmd.payload` is JSON-shaped for reading. The outgoing `eventPayload` can be a generated protobuf builder value, which preserves type identity. This is a deliberate asymmetric shape: input is convenient to inspect; output can be type-preserving.

The publisher adapter is the important part:

```go
pub.Publish(ctx, sessionstream.Event{
    Name:      name,
    SessionId: sid,
    Payload:   msg,
})
```

The JavaScript handler does not mutate Hub state directly. It publishes backend events, and the Hub applies the ordinary sessionstream pipeline.

### Projections and timeline view

The module supports both projection types:

```javascript
hub.uiProjection((event, session, view) => [
  { name: "ChatMessageAccepted", payload: uiPayload }
])

hub.timelineProjection((event, session, view) => [
  { kind: "ChatMessage", id: "m1", payload: entityPayload }
])
```

The `TimelineView` wrapper is read-only:

```javascript
view.ordinal()
view.get(kind, id)
view.list(kind)
```

This is the right restriction. A projection should derive outputs from the current view. It should not mutate the store directly. The Hub remains responsible for applying timeline entity changes.

### EventEmitter fanout

The binding exposes EventEmitter-backed fanout:

```javascript
const EventEmitter = require("events")
const ee = new EventEmitter()

const hub = ss.hub({
  schemas,
  fanout: ss.eventEmitterFanout(ee),
})

ee.on("ui", batch => {
  // batch.sessionId, batch.ordinal, batch.events
})
```

The implementation uses `jsevents.Manager` and `EmitterRef`, which are designed for safe Go-to-JavaScript emission. The first attempt used synchronous emission. That deadlocked when a JavaScript-originated `hub.submit` synchronously reached fanout and attempted to call back into the same Goja owner thread. The final implementation schedules emission asynchronously with `EmitterRef.EmitWithBuilder`.

The rule is general: if Go code can be reached from JavaScript and then needs to emit back into JavaScript, avoid a synchronous owner-thread round trip unless the owner layer explicitly handles reentrancy.

## The compiled chatdemo proof

The sessionstream repository now contains a compiled proof package:

```text
sessionstream/examples/goja-chatdemo
```

It is not a runnable application yet. It is a test-backed smoke example.

Important files:

```text
examples/goja-chatdemo/scripts/start-inference.js
examples/goja-chatdemo/goja_chatdemo_test.go
examples/goja-chatdemo/provider/provider.go
examples/goja-chatdemo/provider/provider_test.go
examples/goja-chatdemo/xgoja.yaml
```

The JavaScript fixture is intentionally small:

```javascript
const pb = require("sessionstream.examples.chatdemo.v1")

exports.command = pb.StartInferenceCommand.builder()
  .prompt("Explain ordinals")
  .build()
```

The test registers the generated protobuf builder module, executes that script, extracts the concrete Go protobuf command, submits it into the existing chatdemo Hub, waits for the engine to become idle, and checks snapshot entities plus UI fanout batches.

The test matters because it crosses the full boundary:

```text
JavaScript builder
  -> hidden ProtoMessage ref
  -> concrete Go protobuf command
  -> sessionstream Hub.Submit
  -> chatdemo command handler
  -> backend events
  -> UI/timeline projections
  -> snapshot/fanout assertions
```

## The mountable HTTP handler ABI

The new `go-go-goja` ABI lives at:

```text
go-go-goja/pkg/gojahttp/mountable.go
```

It introduces:

```go
type HandlerRef struct {
    Handler http.Handler
}

func AttachHTTPHandler(vm *goja.Runtime, obj *goja.Object, handler http.Handler) error
func HTTPHandlerFromValue(value goja.Value) (http.Handler, bool)
```

The implementation uses a hidden property:

```go
const hiddenHTTPHandlerKey = "__go_go_goja_http_handler"
```

The property is attached as non-writable, non-enumerable, and non-configurable. This mirrors the protobuf hidden-reference pattern. JavaScript cannot discover the handler with `Object.keys`, and it does not need direct access to the Go pointer. A Go-backed HTTP module can extract it when necessary.

The ABI is deliberately small. It does not define routing, middleware, response helpers, or WebSocket behavior. It only says: this JavaScript value carries a Go `http.Handler`.

## Host mount semantics

`gojahttp.Host` now has generic handler mounting APIs:

```go
type MountOptions struct {
    StripPrefix     bool
    ExcludePrefixes []string
}

func (h *Host) RegisterHandler(prefix string, handler http.Handler)
func (h *Host) RegisterHandlerWithOptions(prefix string, handler http.Handler, opts MountOptions)
```

The existing static handler API remains:

```go
func (h *Host) RegisterStaticHandler(prefix string, handler http.Handler)
func (h *Host) RegisterStaticHandlerWithOptions(prefix string, handler http.Handler, excludePrefixes []string)
```

The behavior difference is important:

| API | Default path behavior | Intended use |
|---|---|---|
| `RegisterHandler` | Preserve original path | WebSockets, APIs, Go-backed transports |
| `RegisterHandlerWithOptions(... StripPrefix:true)` | Strip mount prefix | Handlers that expect relative paths |
| `RegisterStaticHandler` | Strip mount prefix | File servers and static assets |

For a WebSocket server mounted at `/ws`, preserving the original path is the safer default. The handler sees `/ws` or `/ws/...`, which is useful for logging, upgrade checks, subprotocol choices, and future multiplexing.

## Express `app.mount`

The Express module now exposes:

```javascript
app.mount(prefix, mountableHandler, options?)
app.mountHandler(prefix, mountableHandler, options?)
```

The two names call the same implementation. `mount` is short and idiomatic for application code; `mountHandler` is explicit and useful in documentation where the distinction from JavaScript route handlers matters.

Mount options are:

```typescript
type MountOptions = {
  stripPrefix?: boolean
  excludePrefixes?: string[]
}
```

A Go-backed module can expose a mountable object:

```go
obj := vm.NewObject()
err := gojahttp.AttachHTTPHandler(vm, obj, handler)
```

JavaScript can mount it:

```javascript
app.mount("/ws", wsServer)
app.mountHandler("/api", apiHandler, { stripPrefix: true })
```

The Express app unwraps the hidden handler ref and registers it on the host. If the value is a plain object, the API returns an error:

```text
app.mount("/bad") requires a Go http.Handler-backed object
```

## Route patterns and mounted handlers

The Goja HTTP stack now has two different matching concepts. They should not be collapsed.

JavaScript routes use route patterns:

```javascript
app.get("/users/:id", (req, res) => {
  res.json({ id: req.params.id })
})

app.get("/assets/*", (req, res) => {
  res.send("matched")
})
```

The current pattern rules are:

- `:name` captures one path segment into `req.params.name`.
- `*` matches the remainder of the path when it appears as a complete segment.
- `*` does not currently expose a captured splat value.
- Wildcards inside a segment, such as `*.js`, are not wildcard patterns.

Mounted handlers use prefix matching:

```javascript
app.mount("/ws", wsServer)
```

This matches:

```text
/ws
/ws/anything
```

It does not extract route parameters. The mounted Go handler receives the request and can inspect the path itself. This is the correct first behavior for WebSocket and transport handlers. They need ownership of the HTTP request, not a JavaScript route parameter object.

## xgoja `serve` integration

xgoja v2 already supports provider command sets. The HTTP provider contributes the `serve` command set:

```yaml
providers:
  - id: http
    import: github.com/go-go-golems/go-go-goja/pkg/xgoja/providers/http

runtime:
  modules:
    - provider: http
      name: express
      as: express

commands:
  - id: serve
    type: provider.command-set
    provider: http
    name: serve
    mount: serve
    sources: [sites]
```

The `serve` command runs JavaScript verbs that register Express routes and keeps the runtime alive. Because `app.mount` registers onto the same `gojahttp.Host`, mounted Go handlers should work under the same `serve` flow once the producing module exposes mountable handler objects.

The HTTP provider also has a hot-reload path that uses an external `gojahttp.Host` service. The mountable handler design fits that path because the ABI terminates at `gojahttp.Host`, not at a specific Express implementation detail.

## What still needs to be done in sessionstream

The sessionstream WebSocket wrapper currently returns an object with connection introspection. It should now also attach the mountable handler ref:

```go
func (m *moduleRuntime) webSocketServerBuilder(call goja.FunctionCall) goja.Value {
    hub, ok := m.hubRef(call.Argument(0))
    if !ok {
        panic(m.vm.NewTypeError("webSocket.server expects a sessionstream Hub"))
    }

    server, err := ws.NewServer(hub.hub)
    if err != nil {
        panic(m.vm.NewGoError(err))
    }

    obj := m.vm.NewObject()
    m.attachRef(obj, &websocketRef{server: server})

    if err := gojahttp.AttachHTTPHandler(m.vm, obj, server); err != nil {
        panic(m.vm.NewGoError(err))
    }

    m.mustSet(obj, "connections", func() any {
        return server.Connections()
    })

    return obj
}
```

After that change, a real smoke app can be added:

```text
sessionstream/examples/goja-chatdemo/cmd/smoke/main.go
```

The smoke app should:

1. create a `gojahttp.Host`;
2. create a Goja runtime with `express`, `sessionstream`, and the chatdemo protobuf builder module;
3. run JavaScript that creates schemas, a Hub, command/projection handlers, and a WebSocket server;
4. call `app.mount("/ws", ss.webSocket.server(hub))`;
5. start an HTTP server or use `httptest` for a non-interactive smoke;
6. submit a command and verify snapshot/fanout behavior;
7. optionally perform a WebSocket subscribe roundtrip.

## Validation evidence

The `go-go-goja` mountable handler work passed:

```bash
go test ./pkg/gojahttp ./modules/express ./pkg/xgoja/providers/http -count=1
go test ./pkg/xgoja/... ./modules/express ./pkg/gojahttp -count=1
go test ./... -count=1
```

The implementation commit also passed the repository pre-commit hook, which ran:

```text
go generate ./...
go test ./...
golangci-lint run -v
GOWORK=off go vet -vettool=/tmp/glazed-lint ...
```

The sessionstream binding work previously passed:

```bash
cd /home/manuel/workspaces/2026-06-12/goja-sessionstream/sessionstream

go test ./pkg/js/modules/sessionstream/... -count=1
go test ./examples/chatdemo ./examples/goja-chatdemo/... ./pkg/js/modules/sessionstream/... -count=1
make schema-vet
go test ./... -count=1
```

The go-go-goja compatibility tests after merging `origin/main` also passed:

```bash
cd /home/manuel/workspaces/2026-06-12/goja-sessionstream/go-go-goja

go test ./pkg/xgoja/... ./pkg/protogoja ./pkg/jsevents/... ./cmd/protoc-gen-goja-builder ./examples/xgoja/15-protobuf-builder-provider/... -count=1
make -C examples/xgoja/15-protobuf-builder-provider smoke
go test ./... -count=1
```

## Failure modes and design constraints

### Hidden refs are lost by broad export

The sessionstream binding uncovered a repeatable rule: if a JavaScript value carries a hidden Go reference, avoid converting it through broad `ExportTo` into generic Go structs or maps when that hidden identity matters. The value should stay as `goja.Value` until the consuming code has tried the hidden-ref extraction path.

This affected projection result decoding. Exporting the whole projection result erased nested generated protobuf message refs. The fix was to inspect array/object properties manually and keep `payload` as a `goja.Value`.

The same rule applies to mountable handlers. `app.mount` receives a `goja.Value` and calls `gojahttp.HTTPHandlerFromValue` directly. It does not export the object to a Go map.

### Generic handler mounts should not default to stripping paths

Static file handlers usually expect paths relative to their filesystem root. Generic HTTP handlers often expect the original request path. The implementation therefore keeps static helper behavior unchanged while making generic mounts preserve paths by default.

This distinction is visible in tests:

```text
app.mount("/ws", handler)                         -> handler sees /ws/chat
app.mountHandler("/api", handler, {stripPrefix}) -> handler sees /ping for /api/ping
app.static("/static", dir)                       -> file server sees stripped path
```

### Mounted handlers currently precede JavaScript routes

`gojahttp.Host` checks mounted handlers before JavaScript route handlers. This preserves existing static mount precedence. It also makes sense for WebSockets: an upgrade request to `/ws` should reach the WebSocket handler before ordinary route dispatch.

A future router could interleave mounted handlers and JS routes by registration order. That would require a larger router representation and a migration decision. The current implementation keeps the change small.

### Wildcard route matching does not capture a splat

The current wildcard route pattern is useful for broad matching, but it does not produce a captured remainder. If scripts need the captured remainder later, the router can add a conventional field such as `req.params["*"]` or `req.params.splat`. That is independent of handler mounting.

## Recommended next implementation sequence

The next work should happen in `sessionstream`, now that `go-go-goja` exposes the ABI.

1. Import `github.com/go-go-golems/go-go-goja/pkg/gojahttp` in `pkg/js/modules/sessionstream`.
2. Attach the WebSocket `*ws.Server` to the JS wrapper object with `gojahttp.AttachHTTPHandler`.
3. Add an integration test that registers both `express` and `sessionstream`, runs JavaScript, and calls:

   ```javascript
   app.mount("/ws", ss.webSocket.server(hub))
   ```

4. Use `httptest` to verify that `/ws` reaches the sessionstream WebSocket handler. A full WebSocket subscribe roundtrip is better than only checking status codes.
5. Add a runnable smoke app under `examples/goja-chatdemo/cmd/smoke`.
6. Update `examples/goja-chatdemo/README.md` with both the test-backed smoke path and the runnable app path.

## Current status

The core design is now implemented in `go-go-goja`. Express can mount Go-backed handlers exposed through a shared hidden-ref ABI. The sessionstream Goja module already exposes a WebSocket server object, but it has not yet attached the new handler ref. The final composition step is therefore small and well-defined.

The important result is architectural: Goja modules can now compose at the HTTP handler boundary without compile-time coupling to each other. Express owns the host. Sessionstream owns the WebSocket handler. JavaScript decides where the handler is mounted.

## Key points

- `app.mount` is not JavaScript middleware. It mounts a Go `http.Handler` carried by a JavaScript-visible object.
- `gojahttp.AttachHTTPHandler` is the shared ABI. Producer modules attach; consumer modules extract.
- JavaScript route patterns support `:params` and segment-level `*`; mounted handlers use prefix matching.
- Generic mounted handlers preserve request paths by default; static file helpers still strip prefixes.
- The sessionstream WebSocket server should be the first downstream producer of a mountable handler object.
- A real smoke app should be added after sessionstream attaches the handler ref.
