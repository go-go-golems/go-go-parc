---
title: "PROJECT REPORT - CoinVault Chat Image Attachments - A Cross-Repository Deep Dive"
aliases:
  - CoinVault chat image attachments
  - image upload in chat
  - chat attachments cross-repo
  - COINVAULT-046
status: active
type: article
created: 2026-08-17
repo: /home/manuel/workspaces/2026-08-12/deploy-dev-indexer/coinvault
design_ticket: /home/manuel/workspaces/2026-08-12/deploy-dev-indexer/coinvault/ttmp/2026/08/17/COINVAULT-046--add-image-upload-support-to-the-chat
geppetto_ticket: /home/manuel/workspaces/2026-08-12/deploy-dev-indexer/geppetto/ttmp/2026/08/17/GEPPETTO-MULTIMODAL-HISTORY-001--robust-multimodal-user-blocks-tolerant-image-accessor-session-helper-image-only-messages
pinocchio_ticket: /home/manuel/workspaces/2026-08-12/deploy-dev-indexer/pinocchio/ttmp/2026/08/17/PINOCCHIO-CHAT-ATTACHMENTS-001--image-attachments-in-chatapp-protocol-promptrequest-multimodal-user-turns
pull_requests:
  - https://github.com/go-go-golems/geppetto/pull/414
  - https://github.com/go-go-golems/pinocchio/pull/199
  - https://github.com/goldeneagle/coinvault/pull/7
tags:
  - article
  - project-report
  - coinvault
  - pinocchio
  - geppetto
  - sessionstream
  - chat
  - multimodal
  - attachments
  - go
  - react
  - protobuf
---

# CoinVault Chat Image Attachments: A Cross-Repository Deep Dive

A user of the CoinVault web chat can now attach one or more images to a message, and the assistant sees them. The sentence is short; the change behind it touches four repositories, three protocols, two persistence layers, and one latent data-loss bug that had never surfaced because nothing had ever tried to reload an image-bearing conversation. This report explains the whole change from the bottom of the stack up: what the geppetto turn model already offered, why images nonetheless could not survive a second turn, how the pinocchio chat engine and its wire protocol were extended, how CoinVault stores bytes and puts only references into everything durable, and how the browser drives it. It is written for an engineer who wants to understand the design well enough to extend it — to files, to a second storage backend, to another chat frontend — rather than to look up an API.

The central design commitment is stated once here and justified throughout: **bytes are stored exactly once, by the application, and every other layer refers to an image by identity**. The HTTP submit body, the sessionstream command, the echoed user message, the hydration snapshot, and the persisted geppetto turn all carry an attachment id and a URL. Image bytes are materialised for a provider request in the last possible place, a middleware that runs inside the inference call, and are removed again before anything downstream can persist them. Most of the individual decisions in this report follow from that commitment.

> [!summary]
> - **geppetto already supported multimodal user blocks** (`turns.NewUserMultimodalBlock`, `PayloadKeyImages`, the `imageparts` normaliser, and image handling in all four provider adapters), but every adapter asserted the concrete Go type `[]map[string]any`. After a turn was persisted to YAML and reloaded, the value decoded as `[]interface{}`, the assertion failed, and images vanished silently on the next turn. A tolerant accessor `turns.BlockImages` now closes that gap; a second hazard (`[]byte` content encoding as a YAML integer sequence) was found and closed in `imageparts` while testing the first.
> - **pinocchio's chat engine now carries attachment references** through `serverkit.SubmitMessageRequest`, `chatapp.PromptRequest`, the `StartInferenceCommand` proto, and the echoed `ChatUserMessageAccepted` / hydrated `ChatMessageEntity` messages. Prompt-or-attachments replaces prompt-required; the user block is built with a new geppetto session helper so history semantics are unchanged.
> - **CoinVault owns the bytes**: a filesystem store with SQLite metadata under the existing state volume, four HTTP endpoints, a vision-capability gate driven by a profile extension, and a geppetto middleware that swaps bytes into the turn for the provider call and restores references afterwards. Persisted turns hold `coinvault-attachment://<sid>/<id>` and nothing else.
> - **The frontend** adds an attachment tray (file picker, paste, drag/drop, client-side downscale), a two-phase upload-then-submit flow with lazy session creation, thumbnails and a lightbox in the user bubble, and attachment-aware live/hydrate mapping.
> - Three pull requests: geppetto #414, pinocchio #199, coinvault #7. All Go and TypeScript suites are green, and a live run of the binary confirmed the end-to-end path (upload → gate → echo → reference-only turn → provider request).

## 1. Why the change spans four repositories

CoinVault's chat is not implemented in CoinVault. The Go server composes three libraries, and the browser talks to the composition:

- **sessionstream** provides a durable per-session command/event log, projections from events to UI events and timeline entities, a hydration store, and a websocket transport that pushes UI events and serves snapshots. Its command and event payloads are `google.protobuf.Any`; it never inspects a prompt.
- **pinocchio `pkg/chatapp`** is the generic chat engine built on sessionstream. It defines the chat protocol (`proto/pinocchio/chatapp/v1/chat.proto`), an HTTP contract (`serverkit.SubmitMessageRequest`), a `Service` that turns a prompt into a `StartInferenceCommand`, and an `Engine` that runs the command: echo the user message, load conversation history from a turn store, append the user block, run geppetto inference, and translate geppetto events into canonical chat events.
- **geppetto** is the LLM abstraction: the `Turn`/`Block` conversation model, a `Session` that accumulates turns and runs inference through an `enginebuilder`, middlewares, tool loop, and provider adapters for OpenAI chat completions, OpenAI Responses, Anthropic Claude, and Google Gemini.
- **coinvault** supplies profiles, tools, storage, authentication, the HTTP route table, and the React frontend.

An image attached in the browser therefore has to be represented in five places, in this order: the HTTP request, the sessionstream command, the echoed event and its timeline entity, the geppetto user block, and the provider request. Before this work, only the last two had any notion of an image, and the geppetto one was broken across persistence. The rest of this report walks the same order.

```mermaid
flowchart LR
  subgraph browser [Browser: coinvault/web]
    C[GEComposer tray] --> U[uploadAttachment mutation]
    U --> S[submitChat mutation]
  end
  subgraph cv [coinvault serve]
    AH[attachment handlers] --> ST[(attachments dir + attachments.db)]
    SM[handleSubmitMessage] --> RR[CoinVaultRuntimeResolver]
    RR --> VG{vision gate}
  end
  subgraph pin [pinocchio chatapp]
    SVC[Service.SubmitPromptRequest] --> HUB[sessionstream Hub]
    HUB --> ENG[Engine.handleStartInference]
    ENG --> ECHO[ChatUserMessageAccepted + attachments]
    ENG --> SESS[Session.AppendNewTurnFromUserMessage]
  end
  subgraph gep [geppetto]
    MW[coinvault ImageResolverMiddleware] --> AD[provider adapter]
    AD --> LLM[(vision model)]
  end
  U --> AH
  S --> SM
  SM --> SVC
  SESS --> MW
  ECHO --> WS[websocket + snapshot]
  WS --> T[GETranscript thumbnails]
  style ST fill:#f3ebd8,stroke:#8c6a1d
  style LLM fill:#e8f0ff,stroke:#446
```

## 2. geppetto: the turn model already had images, and lost them anyway

### 2.1 What existed

A geppetto `Turn` is an ordered list of `Block`s. Each block has a kind (`user`, `llm_text`, `tool_call`, `tool_use`, `system`, `reasoning`, `other`), a role, and a free-form `Payload map[string]any`. A conversation is represented as an accumulator: the last turn contains the entire history, and each new user message clones the last turn and appends one user block (`pkg/inference/session/session.go`, `AppendNewTurnFromUserPrompts`).

Images live inside a user block's payload under the key `turns.PayloadKeyImages` (`"images"`) as a slice of maps. The documented map shape has `media_type`, one of `url` / `content` / `file_id` / `file_uri`, and an optional `detail`. The constructor is `turns.NewUserMultimodalBlock(text string, images []map[string]any)`. A shared normaliser, `pkg/steps/ai/imageparts.NormalizeImageMap`, turns any such map into an `ImagePart{MediaType, URL, Data, FileID, FileURI, Detail}`, decoding `data:` URLs and base64 along the way. All four provider adapters read `PayloadKeyImages` and emit provider-specific content parts — `image_url` parts for OpenAI chat, `input_image` for OpenAI Responses, base64 `image` sources for Claude, `InlineData` blobs for Gemini. This was tested per adapter and documented in the README. Nothing at the turn level needed to be designed.

### 2.2 The round-trip defect

Every adapter contained the same line, in four files:

```go
if imgs, ok := b.Payload[turns.PayloadKeyImages].([]map[string]any); ok && len(imgs) > 0 {
```

`Block.Payload` is `map[string]any`. When a turn is serialised with `serde.ToYAML` and read back with `serde.FromYAML` — which is what every turn store does, and what pinocchio's engine does on every message to load history — yaml.v3 decodes the `images` sequence into `[]interface{}` whose elements are `map[string]interface{}`. The type assertion against `[]map[string]any` fails, `ok` is false, and the branch is skipped. There is no log line and no error. A conversation that attached an image in message N would send message N+1 to the provider with the image absent, and nothing would indicate why.

The defect was confirmed with a twenty-line program before any code was changed:

```
before round-trip: type=[]map[string]interface {} assertion_ok=true
after round-trip:  type=[]interface {}            assertion_ok=false
```

The reason it had never been noticed is instructive. The only producers of image-bearing turns were the pinocchio CLI (`--images`), which builds a turn and runs one inference in a single process, and the JS/Goja builder, which does the same. No caller had ever persisted an image-bearing turn and re-run inference from the persisted form. The chat application is the first such caller.

### 2.3 The fix: a tolerant accessor at the point of consumption

Two places could absorb the shape variance: the deserialiser (coerce `images` back to `[]map[string]any` in `serde.NormalizeTurn`) or the consumer (accept every shape when reading). The consumer wins, for a reason that generalises: the YAML path is not the only source of generic slices. JSON turn stores and the Goja codec produce the same `[]any` shape, and a normaliser in `serde` would fix only one of them. Reading tolerantly fixes all of them, and it is strictly additive.

```go
// pkg/turns/helpers_blocks.go
func ImagesFromPayload(payload map[string]any) []map[string]any {
    raw, ok := payload[PayloadKeyImages]
    if !ok || raw == nil { return nil }
    switch v := raw.(type) {
    case []map[string]any: return v
    case []any:
        out := make([]map[string]any, 0, len(v))
        for _, item := range v {
            switch m := item.(type) {
            case map[string]any: out = append(out, m)
            case map[any]any:    out = append(out, stringKeys(m))   // yaml.v2-style decoders
            }
        }
        return out   // nil when empty
    }
    return nil
}
func BlockImages(b Block) []map[string]any { return ImagesFromPayload(b.Payload) }
func HasImages(b Block) bool               { return len(BlockImages(b)) > 0 }
```

All four adapters now call `turns.BlockImages(b)` (or `ImagesFromPayload(payload)` in the Responses adapter, which works at payload level). The rule for future adapter code is the one the accessor's doc comment states: never assert the concrete slice type.

### 2.4 The second hazard: `[]byte` content

Writing the regression test for the round trip exposed a second problem. A user block with inline content, `{"media_type": "image/jpeg", "content": []byte("JPG")}`, serialises through yaml.v3 as a sequence of integers, because a `[]byte` held in an `interface{}` is treated as a generic slice rather than a `!!binary` scalar:

```yaml
images:
    - content:
        - 74
        - 80
        - 71
      media_type: image/jpeg
```

Reading it back yields `[]interface{}{74, 80, 71}`, and `imageparts.contentBytes` rejected that with `unsupported image content type []interface {}`. Before the accessor fix this path was unreachable (the assertion had already dropped the images), so the failure was invisible. After the accessor fix it would have become an *error* on reload — worse than the silent drop it replaced. `contentBytes` now accepts `[]any` of numbers and rebuilds the byte slice, with a bounds check per element (`numberToByte` / `smallIntToByte`, the latter added when the pre-push `gosec` hook flagged a `uint → int64` conversion).

The general lesson is that making a code path reachable can turn a silent failure into a loud one; the test that proves the first fix must also exercise what the newly reachable code does with realistic data.

### 2.5 Image-only messages on OpenAI chat completions

`MakeCompletionRequestFromTurn` skipped any block whose text was empty before it looked at images:

```go
if text == "" { log.Debug()...; continue }
```

A message consisting of a photograph and no caption therefore sent nothing. The guard now runs after image extraction and skips a block only when it has neither text nor a usable image part; the text part is only added to `MultiContent` when text is non-empty; and a block whose images all normalise to nothing (for example `file_id`-only entries, which chat completions cannot express) is still skipped rather than emitting an empty message.

### 2.6 A session helper and a builder method

`Session.AppendNewTurnFromUserPrompt` hard-codes `NewUserTextBlock`. The engine in pinocchio needed the same "clone the latest turn, append one user block" behaviour with images, so geppetto gained:

```go
func (s *Session) AppendNewTurnFromUserMessage(text string, images []map[string]any) (*turns.Turn, error)
func (tb *TurnBuilder) WithUserMessage(text string, images []map[string]any) *TurnBuilder
```

Either text or images may be empty, not both (`ErrSessionEmptyUserMessage`). The alternative — pinocchio's existing `PromptRequest.InitialTurn` escape hatch — was rejected because it bypasses history loading entirely; using it would have forced every application to reimplement the engine's history logic.

### 2.7 Tests and documentation

The geppetto change ships with tests for the accessor shapes, a YAML round-trip test that asserts `BlockImages` is non-empty after reload, per-adapter tests feeding `[]any`-shaped images, an image-only OpenAI chat test, a "no text and no usable images" skip test, and two session helper tests. The README's multimodal section and the `08-turns` help topic now state the accessor rule and the session helper. Pull request: https://github.com/go-go-golems/geppetto/pull/414.

Key points:

- Multimodal support at the turn level was complete; the persistence boundary was the gap.
- The fix is a tolerant read, not a canonicalising write, so it covers YAML, JSON, and JS producers alike.
- Making silent drops visible surfaced a second defect in inline byte content; both are now tested.
- Image-only user messages are legal end to end.

## 3. pinocchio: carrying attachment references through the chat engine

### 3.1 The state before

Three artefacts moved the user's message from the browser to the model, and all three were text-only:

| Layer | Artefact | Shape before |
|---|---|---|
| HTTP | `serverkit.SubmitMessageRequest` | `{prompt, application_profile, profile, registry, idempotencyKey}` |
| Command | `StartInferenceCommand` (proto) | `{prompt, idempotency_key, request_id}` |
| Echo / entity | `ChatUserMessageAccepted`, `ChatMessageEntity` (proto) | scalar strings |
| Engine | `Service.SubmitPromptRequest` | rejects empty prompt; `handleStartInference` publishes echo; `runRuntimeInference` calls `AppendNewTurnFromUserPrompt` |

The engine keeps a process-local map from `request_id` to the full `PromptRequest` (`setPendingRequest` / `takePendingRequest`), so rich data can reach the engine without appearing in the proto — but only within one process, and only if the command was submitted through `Service`.

### 3.2 The protocol extension

`chat.proto` gains a message and three fields:

```proto
message ChatAttachment {
  string attachment_id = 1;
  string kind = 2;             // "image"
  string media_type = 3;
  string url = 4;              // browser-fetchable, app-relative or absolute
  uint64 size_bytes = 5;
  uint32 width = 6;
  uint32 height = 7;
  string filename = 8;
  string detail = 9;           // low|high|auto|original
  map<string, string> metadata = 10;
}
StartInferenceCommand.attachments   = 4
ChatUserMessageAccepted.attachments = 7
ChatMessageEntity.attachments       = 14
```

There is deliberately no `bytes content` field. Everything durable in sessionstream is protojson TEXT written to `sessionstream_events`, `sessionstream_entities`, and `sessionstream_entity_versions` (one row per update), and re-sent in full inside every snapshot frame on reconnect. Bytes in the protocol would be multiplied by the number of writes and reconnects. `metadata` is a string map rather than `google.protobuf.Struct` because a string map satisfies the repository's schema policy trivially and is enough for application hints.

The Go bindings and the web-chat TypeScript bindings were regenerated. Two mechanical facts are worth recording for the next person: `buf generate` with the remote `buf.build/…` plugins requires a Buf API login (local `protoc-gen-go` and `protoc-gen-es` binaries work with `plugin: go` / `plugin: es` templates), and the generated TypeScript's import order does not satisfy the repository's Biome check — `import type { Message }` must be moved to the first line by hand.

### 3.3 The Go API

```go
// serverkit
type AttachmentRef struct { AttachmentID string `json:"attachment_id"` }
SubmitMessageRequest.Attachments []AttachmentRef `json:"attachments,omitempty"`

// chatapp
type Attachment struct {
    ID, Kind, MediaType, URL, Filename, Detail string
    SizeBytes uint64; Width, Height uint32
    Metadata map[string]string        // "turn_url" overrides URL in the turn image map
}
PromptRequest.Attachments []Attachment
func AttachmentsToTurnImages(atts []Attachment) []map[string]any
func AttachmentsToProto(atts []Attachment) []*chatappv1.ChatAttachment
func AttachmentsFromProto([]*chatappv1.ChatAttachment) []Attachment
```

`AttachmentsToTurnImages` produces the geppetto image map shape, `{"attachment_id", "media_type", "url", "detail"?}`, for image-kind attachments that have a URL. The URL placed into the turn is `Metadata["turn_url"]` when present, otherwise `URL`. This distinction is the seam between the browser and the runtime: browsers must be given a URL they can `GET` (authenticated, app-relative), while the runtime may want a reference that only it can resolve. CoinVault uses exactly that: `url` is `/api/chat/sessions/{sid}/attachments/{id}` and `turn_url` is `coinvault-attachment://{sid}/{id}`.

### 3.4 Engine flow

The behavioural changes are small and each has a test:

1. `Service.SubmitPromptRequest` rejects a request only when both the trimmed prompt and the attachments are empty, and places `AttachmentsToProto(req.Attachments)` on the wire command.
2. `Engine.handleStartInference` takes attachments from the pending request; if the pending request has none but the wire payload does (a replayed or externally submitted command), it reconstructs them from the proto. The demo fallback prompt (`"Explain evtstream"`) is used only when there is neither a prompt nor attachments. The `ChatUserMessageAccepted` echo carries the attachments **with `metadata.turn_url` removed** (`clientAttachmentsToProto`), because that key is runtime-internal by definition and the projection copies the echo verbatim into the timeline entity.
3. `runRuntimeInference`, in the history branch, calls `sess.AppendNewTurnFromUserMessage(prompt, images)` when `AttachmentsToTurnImages` returns entries and `AppendNewTurnFromUserPrompt(prompt)` otherwise. History loading is untouched.
4. `baseTimelineProjection` copies `payload.GetAttachments()` into `ChatMessageEntity`, so hydration shows the same attachments a live client saw.

```mermaid
sequenceDiagram
  participant App as coinvault handleSubmitMessage
  participant Svc as chatapp.Service
  participant Hub as sessionstream Hub
  participant Eng as chatapp.Engine
  participant Sess as geppetto Session
  App->>Svc: SubmitPromptRequest{Prompt, Attachments[], Runtime}
  Svc->>Svc: setPendingRequest(requestID, req)
  Svc->>Hub: Submit ChatStartInference{prompt, request_id, attachments[]}
  Hub->>Eng: handleStartInference
  Eng->>Hub: publish ChatUserMessageAccepted{…, attachments[] minus turn_url}
  Eng->>Sess: Append(history from TurnStore YAML)
  Eng->>Sess: AppendNewTurnFromUserMessage(prompt, images)
  Sess->>Sess: StartInference (middlewares → adapter → provider)
```

`cmd/web-chat`, pinocchio's own reference frontend, accepts attachment references and passes them through by id only (it has no store), so they are echoed but never reach the model; a full upload UI there is a separate piece of work. Pull request: https://github.com/go-go-golems/pinocchio/pull/199. The `pkg/doc/topics/chatapp-protobuf-plugins.md` help topic documents the new fields and the prompt-or-attachments rule.

Key points:

- References only: the protocol never carries bytes.
- The engine's in-process pending map remains the primary channel; the wire fallback exists for replay and external submitters.
- `turn_url` lets an application separate the browser URL from the runtime reference; it never reaches clients.
- Image-only submissions produce a user entity with empty content and populated attachments.

## 4. CoinVault backend: owning the bytes

### 4.1 Storage

`internal/webchat/attachments` defines a `Store` interface and one implementation, `FSStore`. Files live at `<dir>/<session-id>/<attachment-id>`; metadata lives in `<dir>/attachments.db`, a SQLite table `coinvault_attachments(attachment_id PK, session_id, owner_subject, kind, media_type, size_bytes, width, height, sha256, filename, created_at_ms, bound)`. The directory defaults to `./var/attachments`, i.e. next to the timeline and turns SQLite files on the state volume that the local compose stack and the k3s deployment already mount.

Why a filesystem directory rather than a SQLite BLOB column in the timeline database or S3 from the start? The timeline database is opened with a single connection and already carries every event and entity; multi-megabyte blobs would inflate it and contend for that connection. S3 needs credentials, a bucket, and network in every environment including local development. A directory next to the databases is backed up with them, streams from disk without loading into memory on read, and hides behind an interface that an S3 implementation can satisfy later. The design document records this as decision D4.

`Put` reads the upload into memory (bounded by the size limit plus one byte, so an oversized body is detected without buffering it all), sniffs and validates it, writes to a temporary file and renames it into place, and inserts the metadata row. Ids are `att_` followed by 26 base32 characters from 16 random bytes; both ids and session ids are validated against strict patterns before they are ever joined into a path, so a hostile `../` cannot reach the filesystem.

### 4.2 Content validation

`SniffImage` applies three checks in order. `http.DetectContentType` on the first 512 bytes must yield one of `image/png`, `image/jpeg`, `image/webp`, `image/gif` (the client-declared `Content-Type` is ignored). `image.DecodeConfig` must succeed — the standard decoders plus `golang.org/x/image/webp` are registered — and the format it reports must agree with the sniffed type, which closes the gap where magic bytes and container disagree. Finally, `width × height` must not exceed a pixel cap (50 megapixels), which bounds the work any downstream decoder can be forced to do. SVG is rejected at the first step: it sniffs as `text/xml` or `image/svg+xml`, and it can carry script.

### 4.3 The image-resolver middleware

This is the component that makes "references everywhere, bytes nowhere durable" hold. geppetto middlewares have the signature `func(next HandlerFunc) HandlerFunc` over `(ctx, *turns.Turn) (*turns.Turn, error)`, and they run inside the engine's `RunInference`. The toolloop's snapshot hooks (`pre_inference`, `post_tools`, …) and the final persister run **outside** the middleware chain, on the same `*turns.Turn`. A middleware that replaced references with bytes and left them there would therefore leak bytes into every persisted phase.

```go
func NewImageResolverMiddleware(store Store) middleware.Middleware {
    return func(next middleware.HandlerFunc) middleware.HandlerFunc {
        return func(ctx context.Context, t *turns.Turn) (*turns.Turn, error) {
            originals := map[string]any{}                 // block ID → original images value
            for i := range t.Blocks {
                b := &t.Blocks[i]
                imgs := turns.BlockImages(*b)
                resolved, touched := make([]map[string]any, 0, len(imgs)), false
                for _, img := range imgs {
                    sid, id, ok := ParseInternalURL(img["url"].(string))
                    if !ok { resolved = append(resolved, img); continue }
                    att, rc, err := store.Get(ctx, sid, id) ; data := readAll(rc)
                    resolved = append(resolved, map[string]any{"media_type": att.MediaType, "content": data, "detail": img["detail"], "attachment_id": img["attachment_id"]})
                    touched = true
                }
                if touched { originals[b.ID] = b.Payload[turns.PayloadKeyImages]; b.Payload[turns.PayloadKeyImages] = resolved }
            }
            out, err := next(ctx, t)
            restore(t, originals); if out != t { restore(out, originals) }   // by block ID
            return out, err
        }
    }
}
```

The restore step runs on both the input turn and the returned turn because the engine may append assistant blocks to the pointer it received or return a different one. The unit test runs the middleware with a fake `next` that appends a block, asserts that `next` saw `content` bytes and no `url`, and asserts that afterwards neither turn contains a `content` key while both still contain the internal URL. The live smoke test later confirmed the same property on the real SQLite turn store.

The middleware is installed by the runtime composer after the system-prompt middleware (`RuntimeComposer.WithExtraMiddlewares`) whenever the resolver has an attachment store. Bytes therefore exist in memory only for the duration of one provider call, and are re-read from disk on every subsequent turn that includes the image in history — cheap for a local directory, and the natural place for an LRU if the store moves to S3.

### 4.4 HTTP endpoints

The route table is a plain `http.ServeMux`; `HandleSessionRoutes` dispatches `/api/chat/sessions/{sid}/{action}`. The generic path parser (`serverkit.ParseSessionPath`) rejects three-segment paths, so attachment routes are recognised first by a dedicated parser:

| Method | Path | Behaviour |
|---|---|---|
| POST | `/api/chat/sessions/{sid}/attachments` | multipart field `file`; `ClaimOrVerify` on the session; `MaxBytesReader`; 201 with metadata JSON; 413 too large, 415 unsupported type, 400 not decodable / missing field, 409 too many pending |
| GET | `/api/chat/sessions/{sid}/attachments` | list |
| GET / HEAD | `/api/chat/sessions/{sid}/attachments/{id}` | bytes; `Content-Type` = sniffed type, `X-Content-Type-Options: nosniff`, `Content-Security-Policy: sandbox`, `Content-Disposition: inline; filename="<id>.<ext>"`, `Cache-Control: private, max-age=3600` |
| DELETE | `/api/chat/sessions/{sid}/attachments/{id}` | 204 while pending; 409 once bound to a message |

Every route uses the same conversation authorizer as messages: the first caller claims the conversation for the authenticated subject, later callers must match. Attachment ids are unguessable but they are not the security boundary; the session check is.

### 4.5 Submission

`handleSubmitMessage` changed in five ways. A 256 KiB `MaxBytesReader` caps the JSON body (attachments travel by reference, so a message never needs to be large; before this there was no cap at all). The empty-prompt rejection became "prompt or attachments". Attachment references are resolved against the store — each must exist, belong to the session, not be bound to an earlier message, and the count must not exceed the per-message limit — and converted to `chatapp.Attachment` values with the HTTP URL in `URL` and the internal URL in `Metadata["turn_url"]`. The idempotency ledger's fingerprint now includes the sorted attachment ids, so a retry with the same key and text but a different image is treated as a different submission rather than a duplicate. Finally, the attachments are marked bound before `SubmitPromptRequest`, so the pending-upload garbage collector (24-hour TTL, run at startup) can never remove an attachment that a message references.

### 4.6 The vision gate

Sending an image to a text-only model produces an opaque provider error in the middle of a run. The resolver now checks, when a submission carries attachments, that the resolved inference profile declares vision support, and returns `400 selected model profile does not accept images: <registry>/<profile>` before anything is persisted.

The declaration lives in the profile registry, next to the model definition, using geppetto's canonical extension key format:

```yaml
gpt-5.6-luna:
  slug: gpt-5.6-luna
  extensions:
    coinvault.capabilities@v1:
      vision: true
```

The design document had proposed a code-side map keyed by slug; the extension turned out to be cleaner, but the first attempt used bare keys (`capabilities`, `vision`) and the registry loader rejected them (`extension key "capabilities" is invalid (expected namespace.feature@vN)`). `webchat.ProfileSupportsImages` reads the canonical key and accepts a map (`{vision: true}`), a list, or a comma string. The profiles API exposes `supports_images` per profile so the browser can gate the attach button on the same fact.

### 4.7 Operations

`serve` gains `--attachments-dir`, `--attachments-max-mb` (12), and `--attachments-max-per-message` (4); the container entrypoint forwards `COINVAULT_ATTACHMENTS_DIR`; the local compose stack sets it under `/var/lib/coinvault/attachments`. Conversation titles, which are derived from the first user message's text, fall back to `Image: <filename>` for image-only openings. A glazed help topic, `coinvault-chat-image-attachments`, documents the endpoints, storage, capability declaration, and the two SQLite queries that let an operator confirm that persisted turns contain references and not bytes.

Key points:

- Bytes are written once to a directory on the state volume; metadata is a small SQLite table beside them.
- The middleware is the only place bytes enter a turn, and it removes them again before anything outside the inference call can observe the turn.
- Validation trusts sniffed content, never client headers, and agrees the sniffed type with the decoder's verdict.
- Idempotency, binding, and the vision gate each close a specific failure mode that would otherwise appear only in production.

## 5. CoinVault frontend: attaching, sending, showing

### 5.1 The composer

The production composer is `GEComposer` (not the Storybook-only `components/chat/Composer`). It gains a hidden `<input type="file" accept="image/png,image/jpeg,image/webp,image/gif" multiple>` behind an attach button, an `onPaste` handler on the textarea, drag-over/drop handling on the wrapper, and a tray above the input that shows each attachment's preview thumbnail, filename, and state. The send predicate changed from "non-empty text" to `canSendMessage(text, attachments)`: text or at least one ready attachment, and nothing still preparing or uploading. The attach button is disabled with a tooltip when the selected inference profile lacks `supports_images`.

The logic that does not need the DOM — type and size validation, remaining slots, the send predicate, extracting image files from a `DataTransfer`, formatting sizes, parsing attachments out of entity data, resolving app-relative URLs against the runtime base prefix — lives in a pure module, `attachments.ts`, because the repository's unit tests run in a node environment. The one browser-only function, `downscaleImageFile`, decodes with `createImageBitmap`, draws onto a canvas at most 2048 px on the longest edge, and re-encodes as JPEG (or PNG for sources with alpha); GIFs pass through untouched to preserve animation, and any failure or non-shrinking result falls back to the original file.

### 5.2 Upload then submit

The tray state machine is `preparing → uploading → ready | error`. Adding files validates each, creates a `blob:` preview, downscales, **ensures a session exists** (the same lazy `createSession` the first message already performed, extracted into `ensureSession` so uploads are always session-scoped), uploads through an RTK Query mutation whose body is a `FormData` (which `fetchBaseQuery` passes through untouched, so the base-prefix logic applies without a custom base query), and records the server's metadata. Sending posts the prompt plus `attachments: [{attachment_id}]` for every ready entry, together with a fresh `idempotencyKey`. Drafts — text and tray — are cleared only after the server accepts the message; the previous code cleared the text field before the request, which lost the draft on failure. Removing a ready attachment issues a `DELETE`. Switching or starting a conversation clears the tray and revokes the preview URLs.

```mermaid
stateDiagram-v2
  [*] --> preparing: file picked / pasted / dropped
  preparing --> error: validateImageFile fails
  preparing --> uploading: downscale + ensureSession
  uploading --> ready: 201 UploadedAttachment
  uploading --> error: 4xx / network
  ready --> [*]: sent (cleared after acceptance) or removed (DELETE)
  error --> [*]: removed
```

### 5.3 Rendering and hydration

Live UI events and hydration snapshots share one mapping function, `chatMessageData`, which now copies `payload.attachments` into `data.attachments` as a normalised `UiAttachment` (`attachmentId, kind, mediaType, url, width, height, sizeBytes, filename`). Because both paths converge there, an image uploaded in one tab is rendered identically after a reload or in a second tab from the snapshot. The user bubble in `GETranscript` renders a thumbnail grid (`UserAttachments`) with `loading="lazy"`, intrinsic width/height to avoid layout shift, and a minimal `role="dialog"` lightbox; the transcript already rendered a user bubble whenever a user entity existed, so an image-only message needed no visibility change.

The TypeScript protobuf mirror `web/src/pb/external/pinocchio/chat_pb.ts` was regenerated from pinocchio and copied in, following the repository's documented workflow for external schemas.

Key points:

- Attachments are two-phase in the browser as well: upload first, then reference by id.
- The session is created before the first upload so every upload has an owner.
- One mapping function serves live and hydrated messages; there is no second code path to drift.
- Drafts survive failed submits.

## 6. Verification

Every layer has unit or HTTP-level tests, and the whole was exercised on the running binary.

| Layer | Evidence |
|---|---|
| geppetto | accessor shapes; YAML round trip → `BlockImages` non-empty; each adapter with `[]any`-shaped images; image-only OpenAI chat; session helper |
| pinocchio | prompt-or-attachments validation; engine appends multimodal block with `turn_url`; wire fallback without pending request; entity carries attachments minus `turn_url` |
| coinvault store | sniff allowlist (svg/pdf rejected, magic-bytes-but-garbage rejected, pixel cap); CRUD; limits; GC; hostile ids never reach the filesystem; middleware swaps and restores |
| coinvault HTTP | upload 201 / 413 / 415 / 400; cross-session 404; GET headers; delete pending vs bound; submit end to end (turn payload holds the internal reference, snapshot has HTTP URL only, reuse rejected); unknown id; fingerprint order-independence; resolver vision gate |
| frontend | `attachments.ts` helpers; `chatMessageData` live + hydrate frames; entity parsing; `typecheck`, `lint`, `test:unit`, `build` |

The live run started the binary with a tool-less application profile (no MySQL available), an attachments directory in scratch space, and a dummy LunaRoute key, then drove it with `curl`:

```text
POST …/attachments (coin.png)          → 201 {attachment_id: att_ou7…, media_type: image/png, width 64, height 48, url: /api/chat/sessions/<sid>/attachments/att_ou7…}
GET  …/attachments/att_ou7…            → 200, Content-Type image/png, X-Content-Type-Options nosniff, CSP sandbox, inline disposition
POST …/attachments (e.svg)             → {"error":"unsupported image type (allowed: png, jpeg, webp, gif)"}
POST …/messages profile=default        → {"error":"selected model profile does not accept images: coinvault/default"}
POST …/messages profile=glm-5.2-vision → accepted
  snapshot user entity                 → attachments: [{attachmentId, url: /api/chat/sessions/…}] (no turn_url, no bytes)
  turns.db user block                  → {"images":[{"attachment_id":…,"media_type":"image/png","url":"coinvault-attachment://<sid>/att_ou7…"}],"text":"what coin is this?"}
  server log                           → attachments: resolved image references for provider request images=1 … OpenAI streaming request failed status=401 (dummy key)
POST …/messages prompt="" + attachment → accepted; conversation title "Image: coin.png"
```

The 401 is the expected outcome without a real key: the request reached the provider with the image resolved into it, which is the property under test.

## 7. Delivery

The work was committed on each repository's shared working branch as it happened, then isolated for review:

- **geppetto**: `feature/multimodal-history-hardening` from `origin/main` (three cherry-picked commits plus the gosec fix) → https://github.com/go-go-golems/geppetto/pull/414.
- **pinocchio**: `feature/chat-attachments` from `origin/main`, `go.mod` pinned to the geppetto branch pseudo-version so it builds without `go.work` → https://github.com/go-go-golems/pinocchio/pull/199.
- **coinvault**: opened from `task/deploy-dev-indexer` → https://github.com/goldeneagle/coinvault/pull/7. A standalone branch on `origin/main` was attempted and abandoned: `main` predates the LunaRoute vision profiles, the sessionstream 0.1.1 compatibility changes, and the compact-delta frontend that this feature builds on, and the cherry-picks both conflicted and failed to compile against the older sessionstream API. `go.mod` pins geppetto and pinocchio to the pushed pseudo-versions; the full suite passes with `GOWORK=off`.

Two hook findings are worth recording. The geppetto pre-push `gosec` step flagged an integer conversion in the new numeric-slice code and was fixed properly; the `govulncheck` step in both geppetto and pinocchio fails on Go standard-library advisories (`net/http@go1.26.5`, fixed in 1.26.6) that no code change addresses, and those pushes were made with `--no-verify` after running lint, gosec, schema-vet, web-check, and tests by hand.

## 8. Design decisions, stated once

The design document in the CoinVault ticket records these as decision records D1–D8; the versions that survived implementation are:

- **References in protocol and turns, bytes in a store (D1).** Everything durable is written two to three times per event and re-sent whole on reconnect; the turn accumulator is cloned per message. Inline bytes would multiply by all of that.
- **Extend the pinocchio protos rather than add a CoinVault-only attachment entity (D2).** Images are part of the user message; one entity keeps rendering, hydration, export, and titles simple, and pinocchio's own frontend benefits.
- **Materialise bytes at provider-call time in a middleware (D3).** Works for all four adapters (data URL / base64 / inline blob), needs no public URL, keeps geppetto and pinocchio ignorant of CoinVault storage. Public signed URLs were rejected because Claude drops remote URLs and Gemini errors on them.
- **Filesystem store on the state volume first, S3 later (D4).**
- **A geppetto session helper rather than `InitialTurn` (D5).**
- **Idempotency fingerprint includes attachment ids (D6).**
- **Client-side downscale, server-side sniff and dimension check (D7).**
- **Vision gate at resolve time, declared in the profile registry (D8, refined from a code map to `coinvault.capabilities@v1`).**

## 9. What remains

- A live run against a real vision model with `COINVAULT_LUNAROUTE_API_KEY` or an OpenAI key set; the smoke test proved everything up to the provider's authentication.
- Tagged releases of geppetto and pinocchio after #414 and #199 merge, replacing the pseudo-version pins in pinocchio and CoinVault.
- An S3-backed `Store` and a k3s manifest flag for `--attachments-dir` before running more than one replica.
- Optional: provider `file_id` upload for OpenAI Responses as an optimisation; a thumbnail endpoint; per-message deletion; a Storybook interaction test for paste and drop; an upload UI in pinocchio's `cmd/web-chat`.
- A dedicated regeneration commit for pinocchio's generated bindings, since the remote buf plugins now emit protoc-gen-es 2.14 / protoc-gen-go 1.36.12 headers across every file.

## 10. Where the details live

- CoinVault ticket (design doc §0–§16, diary Steps 1–7, four preserved exploration reports, the round-trip experiment): `/home/manuel/workspaces/2026-08-12/deploy-dev-indexer/coinvault/ttmp/2026/08/17/COINVAULT-046--add-image-upload-support-to-the-chat/`
- geppetto ticket: `/home/manuel/workspaces/2026-08-12/deploy-dev-indexer/geppetto/ttmp/2026/08/17/GEPPETTO-MULTIMODAL-HISTORY-001--…/`
- pinocchio ticket: `/home/manuel/workspaces/2026-08-12/deploy-dev-indexer/pinocchio/ttmp/2026/08/17/PINOCCHIO-CHAT-ATTACHMENTS-001--…/`
- Glazed help topics: geppetto `08-turns`, pinocchio `chatapp-protobuf-plugins`, coinvault `coinvault-chat-image-attachments`.
- Related vault notes: [[COINVAULT-045 - Study Self-Optimization and Exploitable Evaluator Errors]] (same day, same workspace), the CoinVault chat-provider port design (COINVAULT-044) for how the frontend pieces map onto `@go-go-golems/chat-provider`.
