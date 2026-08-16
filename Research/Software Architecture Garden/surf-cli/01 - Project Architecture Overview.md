---
title: "Project Architecture Overview — surf-cli"
aliases:
  - surf fundamental architecture patterns
  - surf CLI host extension split
  - surf JavaScript facade
status: candidate
type: architecture-garden-design
created: 2026-08-14
analyzed: 2026-08-14
repository: /home/manuel/workspaces/2026-08-07/add-3d-model-verbs/surf-cli
repository_remote: git@github.com:wesen/surf-cli.git
repository_branch: task/add-3d-model-verbs
repository_commit: c029d4c65741e1a26d15af2974046244e02aebd5
go_module: github.com/nicobailon/surf-cli/gohost
tags:
  - architecture-garden
  - surf
  - browser-automation
  - native-messaging
  - cli
  - facade
  - ipc
  - go
related_files:
  - go/cmd/surf-go/main.go
  - go/cmd/surf-host-go/main.go
  - go/internal/cli/transport/client.go
  - go/internal/host/router/toolmap.go
  - go/internal/host/router/ingress.go
  - go/internal/host/pending/store.go
  - go/internal/host/pending/id_allocator.go
  - go/internal/host/socketbridge/session.go
  - go/internal/host/socketbridge/listener.go
  - go/internal/host/socketbridge/listener_unix.go
  - go/internal/host/nativeio/codec.go
  - go/internal/host/config/socket_path.go
  - go/internal/installer/native_host.go
  - go/internal/host/providers/chatgpt.go
  - go/internal/cli/commands/base.go
  - go/internal/cli/commands/format.go
  - go/internal/cli/commands/js.go
  - go/internal/cli/commands/tool_simple.go
  - go/internal/cli/commands/tab_ready.go
  - go/pkg/marketplacecapture/envelope.go
related_notes:
  - "[[Research/Software Architecture Garden/surf-cli/README|Architecture Garden — surf-cli]]"
  - "[[Research/Software Architecture Garden/README|Software Architecture Garden]]"
  - "[[Research/Software Architecture Garden/devctl/README|devctl architecture study]]"
  - "[[Research/Software Architecture Garden/rag-evaluation-system/README|rag-evaluation-system architecture study]]"
  - "[[Research/Software Architecture Garden/go-go-datadrop/README|go-go-datadrop architecture study]]"
  - "[[Research/Software Architecture Garden/go-go-goja/README|go-go-goja architecture study]]"
---

# Project Architecture Overview — surf-cli

## Why this note exists

`surf` lets you drive a live, logged-in browser from scripts and the command line. The interesting architecture is not in any one site extractor; it is in the *bridge* that makes a normal CLI able to script a browser it cannot touch directly — only a browser extension can. This entry records the five foundational patterns that define that bridge, so a future engineer can rebuild or safely modify surf's core shape, and so the shape can be compared with other "script the browser" tools.

It is deliberately a project-overview study. Finer-grained sub-patterns (ID-rewrite correlation, pure error classification at the effect boundary, owned-tab retry with an idempotency boundary, versioned capture envelopes, bulk-export manifests) exist in the code and are summarized in the [[Research/Software Architecture Garden/surf-cli/README|project README]], but the load-bearing decisions are the five fundamentals below.

## The system at a glance

```text
                                    (Chrome native messaging: stdio + 4-byte length frames)
   CLI client ──Unix socket──► host ─────────────────────────────────────────────────────► browser extension ──► Chrome
  (surf-go)      (NDJSON lines)  (surf-host-go)                                                (the only thing that can touch the page)
```

- **`surf-go`** (`go/cmd/surf-go`) — the user-facing CLI. Builds intent, renders output, never touches the browser.
- **`surf-host-go`** (`go/cmd/surf-host-go`) — a long-lived broker, launched *by the browser* as a native-messaging subprocess; exposes a local Unix socket so CLI clients can request work.
- **The browser extension** — the only component with page access. Installed via a native-messaging manifest (`go/internal/installer/native_host.go`, `HostName = "surf.browser.host"`).

Everything below is a consequence of three foundational decisions: separate the CLI from the host; let the host + extension own the browser; run JavaScript behind a tooling facade.

> [!summary]
> - **A.** The CLI never holds browser authority; it talks JSON over a local socket to a host that does.
> - **B.** The host is a *browser-launched* native-messaging subprocess that *also* serves a socket — authority comes from being launched by the browser, CLI access is a layered second channel.
> - **C.** Page interaction is named, versioned tools + per-site embedded scripts, with raw `js` kept as an intentional escape hatch.
> - **D.** Auth is not surf's job; the signed-in live browser session *is* the authority.
> - **E.** All browser work is declarative JSON intent over one serialized effect channel, which is what lets concurrent CLI clients share one browser safely.

## Pattern A — CLI client / host broker split

### Pattern statement

The process that presents a user interface (parses flags, formats output, owns a process lifetime) is never the process that holds browser authority. They communicate only over a local socket with a JSON line protocol. The CLI is disposable and stateless; the host is persistent and authoritative.

### Concrete architecture

- Two separate binaries: `go/cmd/surf-go` (client) and `go/cmd/surf-host-go` (host). The client imports only `go/internal/cli/transport` + `go/internal/cli/commands`; the host imports only `go/internal/host/*`. There is no shared runtime state and no in-process call across the boundary.
- The wire protocol is NDJSON lines over a Unix socket. `transport/client.go` `Send` writes one `{"type":"tool_request",...}\n` and reads one reply line; `Stream` reads a line loop for streaming tools. Requests are fully self-describing.
- The CLI's job ends at building a request (`base.go:BuildToolRequest`) and rendering a response (`format.go:ToolResponseToRows`, plus the dual-mode Markdown/rows rendering described under Pattern C). The host's job is to interpret the request and broker it to the browser.

### Behavioral contract

- The CLI may be invoked many times, concurrently, by scripts; each invocation opens its own socket connection and is independent.
- A CLI crash is harmless to the browser session and to the host.
- The host may be rebuilt or replaced without restarting the browser, as long as the socket and protocol are preserved.

### Why alternatives are wrong

A single-process CLI that talks native messaging directly would force every CLI invocation to either re-launch the browser connection or hold it open — coupling CLI lifetime to browser lifetime and making a CLI crash tear down the signed-in session. A shared library would reintroduce in-process coupling and process-lifetime entanglement. The split keeps the two concerns on opposite sides of a socket on purpose.

### Negative space

- The socket (`/tmp/surf.sock` by default, `go/internal/host/config/socket_path.go`) is a **trust boundary only by convention** — any local process can connect and request any tool. This split is a *structuring* boundary, not a security one. (See Pattern D and the open question on the trust model.)
- The tool protocol is synchronous one-request/one-reply for tools. Streaming tools use a separate line-loop connection; there is no multiplexing of multiple in-flight tool replies on a single CLI connection beyond that.

### Failure modes

- If the host is not running (browser not open, extension not installed), the CLI's socket dial fails fast with a clear error — surf does not silently start the host (it cannot; only the browser can).
- Windows uses a named pipe (`//./pipe/surf`) as the socket equivalent; the named-pipe transport on the *client* side is explicitly not yet implemented (`transport/client.go` returns an error on windows).

### Testing and verification

`go/internal/cli/transport/client_test.go` exercises the client; `go/cmd/surf-go/integration_test.go` builds the full root and drives commands against a mock host, asserting the socket round-trip end to end.

### Maturity

**Established.** It is the defining decision of the project; both binaries exist, are tested, and the import separation is clean.

## Pattern B — Host as native-messaging subprocess, not a server you start

### Pattern statement

The host is not a daemon the user starts; the browser starts it as a native-messaging child process. The host's stdin/stdout are owned by the browser's native-messaging framing; the host's socket is the surface it *adds* for CLI clients. Browser authority flows from being launched by the browser; CLI access is a second channel the host layers on top.

This is the most novel and most transferable of the five fundamentals. The non-obvious idea is that *authority comes from being browser-launched*, while *CLI access is a deliberately separate, layered channel* — the host is a bridge between two worlds, owned by the browser on one side and serving CLIs on the other.

### Concrete architecture

- `go/internal/installer/native_host.go` writes a per-browser native-messaging manifest (Chrome, Chromium, Brave, Edge) pointing at the `surf-host-go` binary under the stable host name `surf.browser.host`. The browser discovers and launches the host by this name.
- `surf-host-go` speaks Chrome native messaging on its stdin/stdout: `go/internal/host/nativeio/codec.go` reads and writes **4-byte little-endian length-prefixed frames**, capped at 16 MiB (`DefaultMaxFrameSize = 16 * 1024 * 1024`). `ReadFrame` reads the 4-byte header then exactly `n` bytes; `WriteFrame` prepends the header.
- On startup the host sends `HOST_READY` with its socket endpoint to the extension, then begins accepting CLI sessions on the socket (`socketbridge/listener.go`, with a platform split `listener_unix.go` / `listener_windows.go`).
- The host runs two loops concurrently: an accept loop for CLI sessions (`acceptLoop` → `handleSession`) and a native read loop for extension replies (`readNativeLoop`). Both feed one native writer guarded by a mutex (Pattern E).

### Behavioral contract

- The browser owns the host's process lifetime: it launches the host, owns its stdin/stdout, and detects disconnection.
- When the extension reloads or the browser closes the native channel, the host's stdin hits EOF (`errNativeDisconnected`); the host then notifies all CLI clients ("Surf extension was reloaded. Restart your command.") and exits. It does not attempt to outlive the browser.
- The host is the single owner of the native write path; no other component writes to the extension.

### Why alternatives are wrong

- A user-started daemon would have to discover/re-establish the browser connection itself, which it cannot do (only the browser can open the native-messaging channel to a host it launched).
- Letting the CLI speak native messaging directly would push Chrome's framing protocol and process model into every caller and couple CLI lifetime to browser lifetime — exactly what Pattern A avoids.
- A single combined "host = the extension" design would remove the local socket and make scripting from external processes impossible.

### Negative space

- The host is tied to the browser's process model: when the extension reloads, the host dies, and in-flight CLI requests fail. This is by design (the host is the browser's child), but it means surf is unavailable across extension reloads.
- There is exactly one native stream, so one serialized write path (Pattern E). The host cannot parallelize effects onto the extension.
- The browser-extension side of this contract is a separate TypeScript codebase; this study treats it as the counterparty of the framing and message contract, not as audited implementation.

### Failure modes

- **Extension reload kills all CLI work in flight.** `readNativeLoop` returns `errNativeDisconnected` on stdin EOF; `run` then calls `sessions.NotifyExtensionDisconnected`, which writes an `extension_disconnected` message to every session and closes them. This is graceful but terminal for in-flight requests.
- **Malformed native frames are discarded, not fatal.** `ErrInvalidJSON` and `ErrFrameTooLarge` are logged and the read loop continues (`readNativeLoop`), so one bad frame does not tear down the host.
- **Oversized payloads are rejected at the frame boundary** (`DefaultMaxFrameSize`), bounding untrusted input before JSON parsing.

### Testing and verification

`go/internal/host/nativeio/codec_test.go` exercises framing, `ErrFrameTooLarge`, and `ErrInvalidJSON`. `go/cmd/surf-host-go/main_test.go` exercises session handling, the chatgpt provider dispatch, and disconnect semantics.

### Applicability and non-applicability

- **Apply** when scripting a browser that exposes a native-messaging host API from ephemeral external processes.
- **Do not apply** when the browser connection can be held by a long-lived single owner that is also the UI (then a host broker is unnecessary indirection), or when there is no extension/native-messaging channel at all.

### Maturity

**Established**, and the strongest candidate for cross-project ecosystem guidance ("Browser-launched host broker").

## Pattern C — JavaScript behind a tooling facade

### Pattern statement

Page interaction is expressed as JavaScript that runs in the page, but callers almost never write that JavaScript directly. The host exposes a closed set of named, versioned tools; site-extraction commands embed their own page scripts behind typed options. Raw `js`/`eval` is an explicit escape hatch, not the primary surface.

### Concrete architecture

The facade has two layers.

**Layer 1 — generic tool facade (host router).** `go/internal/host/router/toolmap.go` `MapToolToMessage` is a ~103-arm switch translating a tool name + args into a canonical extension message (`EXECUTE_NAVIGATE`, `READ_PAGE`, `EXECUTE_JAVASCRIPT`, `CLICK_REF`, `EXECUTE_SCREENSHOT`…). It normalizes aliases (`"js"`/`"javascript_tool"`, `"page.read"`/`"page.text"`/`"get_page_text"`) and injects `tabId` when present. The extension sees only canonical messages; the CLI sees friendly tool names. The host can also *deny* before any effect: `providerPrefixes` (`ai`, `chatgpt`, `gemini`, …) and `deferredTools` return `UnsupportedToolError`.

**Layer 2 — per-site extraction facade (CLI commands).** ~63 embedded JS scripts (`//go:embed scripts/*.js`) each implement a site's extraction. Each command injects typed options as a `const SURF_OPTIONS = {...};` prelude and concatenates the embedded script:

```go
return fmt.Sprintf("const SURF_OPTIONS = %s;\n%s", opts, script), nil
```

then sends it through the `js` tool. The script returns a plain JS object; the host's `format.go:parseResult` extracts the `text` content block and `parseStructuredText` decodes it as JSON. Decoding uses `json.Decoder.UseNumber()` + `normalizeJSONNumbers` (int64 when integral) to preserve integer precision — a real bug fix (issue #5: a tab id `441403900` came back as `"4.414039e+08"`, which `--tab-id` rejected and which was consistent with 10 different integers).

**The escape hatch.** `go/internal/cli/commands/js.go` and `tool_raw.go` expose a raw `js` command that runs arbitrary code in the page. It is deliberately present for power users and ad-hoc work, but the productive surface is the named tools and embedded scripts, not free JS.

### Behavioral contract

- The tool set is closed and versioned: adding a tool requires a router change, but callers get a stable verb.
- Per-site scripts are self-contained: they read `SURF_OPTIONS`, do the work, and return a JSON-serializable object.
- The escape hatch is always available; it is not hidden, gated, or deprecated.

### Why alternatives are wrong

- Exposing raw `js` as the *only* surface would push fragile, site-specific DOM knowledge into every caller and give no stable contract across page/site churn.
- A fully closed surface with no escape hatch would make surf unusable for anything the facade does not yet name.
- Letting the host run the JS itself (e.g. in a VM) would lose the live, signed-in, real-browser session — the whole point of surf.

### Negative space

- The facade is a *translation*, not a *type system*: args are `map[string]any`, validated loosely (`stringOr`, `boolOr`, `intOr`). The router does not statically check that a tool's args match its documented shape.
- Embedded scripts are the real per-site logic and can drift from the host's expectations. There is no surf-level contract test binding the Go options to the JS scripts.
- The facade does not sandbox: the raw `js` escape hatch runs arbitrary code in the page with the user's session.
- Number precision across the JSON boundary is a recurring hazard; the `UseNumber` fix is evidence that it bit once.

### Failure modes

- A page redesign can break an embedded script; the facade tool name stays stable, but the script behind it must be updated.
- A tool with a wrong arg type passes the loose validators and may fail deep in the extension with a less helpful error.

### Testing and verification

`go/internal/host/router/toolmap_test.go` and `toolmap_contract_test.go` pin the tool→message mapping. Per-command tests (e.g. `kagi_search_test.go`, `chatgpt_transcript_test.go`) assert the `SURF_OPTIONS` prelude shape and the generated code. `format_test.go` covers `parseResult`/`parseStructuredText` including number normalization.

### Maturity

**Established** for both facade layers (the tool router and the embedded-script-with-options pattern repeat across ~60 commands); the escape hatch is an intentional, documented part of the design, not debt.

## Pattern D — Live browser session as the implicit authority

### Pattern statement

Authentication is not done by surf. Surf operates against a browser that is already signed in by the human. The "credentials" are the live cookies and session in the active browser; surf's job is to drive that session, not to acquire it.

### Concrete architecture

- Commands that need auth don't take tokens — they open/navigate a tab in the signed-in browser and read/work the page. The `chatgpt` provider checks for a session cookie *via the extension* (`GET_CHATGPT_COOKIES` in `go/internal/host/providers/chatgpt.go`) and fails with `"ChatGPT login required"` rather than logging in.
- Readiness probes (`go/internal/cli/commands/tab_ready.go`) wait for the *real* page — `readyState` complete/interactive, a stable href, not `about:blank` — rather than assuming a URL means a loaded, logged-in page.

### Behavioral contract

- Surf never prompts for, stores, or transmits credentials. It inherits the human's session.
- A login wall or expired session surfaces as an ordinary error ("login required", readiness timeout) for the human to resolve.

### Why alternatives are wrong

Acquiring credentials would force surf to manage 2FA, CAPTCHA, session storage, refresh, and revocation — re-implementing the browser's hardest problems. Reusing the live session sidesteps all of it and is what makes "drive my logged-in browser from a script" viable at all.

### Negative space

- The browser session is the authority, so surf inherits its fragility: a reloaded extension, an expired session, a login wall, or a page redesign all break commands.
- There is no surf-level retry that can fix a *missing login* — it surfaces as an error by design. Retries that *do* exist (owned-tab retry) are explicitly limited to read-only operations, because replaying a mutation is not idempotent.
- Commands that own a tab must clean it up; readiness failure closes the owned tab to avoid leaks (`tab_ready.go:openOwnedTab`).

### Failure modes

- A logged-out session makes every authed command fail; surf cannot self-heal it.
- A page that loads but is a login redirect can pass a naive "page loaded" check; the readiness fence (stable href, `about:blank` rejection) reduces but does not eliminate this.

### Maturity

**Established** — a deliberate, load-bearing design choice (and arguably the *reason surf exists*). Worth stating explicitly because it is usually left implicit.

## Pattern E — Declarative intent over a single serialized effect channel

### Pattern statement

Everything the browser must do is expressed as self-describing JSON intent; the host rewrites it onto one serialized native channel. There is no shared memory, no callbacks, no in-process coupling across the CLI/host/extension boundary — only messages. This is the binding glue of Patterns A–C, stated as its own law because it is what makes the split work.

### Concrete architecture

- Intent is plain JSON: `base.go:BuildToolRequest` produces `{"type":"tool_request","method":"execute_tool","params":{tool,args},"id",...}`. No code crosses the wire, only data — modulo the deliberate `js` escape hatch (Pattern C), which sends *code as data*, so the boundary is JSON, not "data vs code."
- The host is the **sole** writer to the native channel: `hostRuntime.writeNative` holds `nativeWriteMu`; nothing else writes `os.Stdout`. One serialized stream = one linearization point for all browser effects.
- The host rewrites identity at the boundary so many clients can share one stream: `pending.IDAllocator` assigns a fresh `hostID` per outbound native message; `pending.Store` maps `hostID → {Session, Kind, OriginalID}`; on reply, `handleNativeMessage` does `pending.Pop(id)`, restores the original client id, and routes to the owning session.

### Behavioral contract

- Concurrent CLI clients never interleave bytes on the native stream; the host sequences their effects even if the browser itself could not.
- Declarative intent lets the host validate or deny before any effect (`UnsupportedToolError`, `providerPrefixes`, `LOCAL_WAIT` handled without touching the extension).
- A reply is matched to a request by the host's id, never by the client's id crossing to the extension.

### Why alternatives are wrong

- Shared memory or callbacks across the process boundary would reintroduce process-lifetime coupling and destroy the disposability of the CLI (Pattern A).
- Letting clients write directly to the native channel would race and corrupt the single browser stream.
- Carrying the client's id onto the wire would leak client identity into the extension and make multiplexing ambiguous.

### Negative space

- One serialized stream is the throughput ceiling; surf cannot parallelize effects onto the extension.
- Serialization is for *dispatch*; once dispatched, the browser's own execution ordering is outside surf's control.
- The pending store has no TTL: a native reply that never arrives leaves a slot until the owning session disconnects (`pending.DeleteForSession`). A reply with an unknown id is silently dropped.

### Failure modes

- **JSON number precision loss (real bug, issue #5).** Decoding numbers as `float64` turned an integer tab id into scientific notation that `--tab-id` rejected and that was consistent with 10 different integers. The fix (`UseNumber` + `normalizeJSONNumbers`) is the canonical "a number that crosses a JSON boundary is not the same number" failure, and evidence that this boundary is where precision bugs live.
- **Silent drop of unknown ids** is a debugging blind spot (logged nowhere).

### Testing and verification

`go/internal/host/pending/store_test.go` covers the correlation store; `go/internal/cli/commands/chatgpt_bulk_socket_test.go` exercises concurrent socket use; `format_test.go` covers number normalization; `go/cmd/surf-host-go/main_test.go` covers the dispatch and reply-restoration path including the pure-error-classification contract.

### Maturity

**Established.**

## Why alternatives are wrong, in the large

The five patterns resist several tempting simplifications:

- **"Just one process."** Collapsing CLI and host couples UI lifetime to browser authority (breaks A, E).
- **"Just start the host yourself."** Removes the browser's ownership of the host and the authority that comes from it (breaks B).
- **"Just expose raw JS."** Gives no stable contract and pushes site fragility to every caller (breaks C).
- **"Let surf log in."** Re-implements the browser's hardest problems and adds a credential store to attack (breaks D).
- **"Let clients share the native stream directly."** Races and corrupts the single browser effect channel (breaks E).

## Failure modes and tricky details (cross-cutting)

- **Extension reload = host death = all in-flight CLI work fails, gracefully.** This is the most operationally surprising behavior and follows directly from B (the host is the browser's child).
- **Numbers are not safe across JSON boundaries by default.** The `UseNumber` fix is a project-wide hazard any new code crossing the JSON boundary must respect.
- **The socket is not a security boundary.** Any local process can drive the browser. This is acceptable on a single-user workstation and wrong on a shared host.
- **Escape hatch is not sandboxed.** Raw `js` runs caller code in the page with the user's session; it is a power tool, not a safe surface.

## Applicability and non-applicability

- **Apply the overall shape** when scripting a browser that exposes a native-messaging host from ephemeral external processes, especially when the browser session is the human's live, signed-in session.
- **Do not apply** when there is no native-messaging/extension channel (B has no foothold), when a single long-lived owner is also the UI (A is unnecessary indirection), or when credential acquisition is actually the requirement (D would fight you).

## Candidate ecosystem guidance

1. **Browser-launched host broker.** A native-messaging subprocess the browser owns, which *adds* a local socket for ephemeral clients. Authority comes from being browser-launched; CLI access is a deliberately separate, layered channel. (Strongest candidate; transferable to any "script my browser from a CLI" tool.)
2. **Tool facade over a raw escape hatch.** A closed, versioned, alias-normalizing verb set in front of a page, with raw execution kept as a documented, intentional escape hatch rather than the primary surface.
3. **Implicit authority by reuse.** Do not acquire credentials; drive the human's existing signed-in session. State explicitly that auth is out of scope by design.

These remain candidates until compared with at least one other "script the browser" project.

## Open questions

1. **Security boundary of the socket.** Document the single-user-workstation trust model explicitly, or add a local-credential/peer-cred gate.
2. **Extension-side contract.** Map the extension's message handling and `initNativeMessaging` bookkeeping (`_resolvedTabId`, `_hint`) as a counterparty study.
3. **Effect ordering in the browser.** Characterize ordering guarantees for tools that assume sequence, given the host only serializes dispatch.
4. **Facade vs drift.** Whether a contract-test layer should bind the Go options to the embedded JS scripts.
5. **Reuse of the browser-launched-host-broker shape** in another project, to move candidate 1 toward validated ecosystem guidance.

## Evidence and references

### Source paths (all under the repository root)

- `go/cmd/surf-go/main.go` — CLI root, command wiring, dual-mode vs glazed command builders.
- `go/cmd/surf-host-go/main.go` — host runtime: accept loop, native read loop, single native writer, dispatch, reply restoration, disconnect cascade.
- `go/internal/cli/transport/client.go` — Unix socket client; `Send` (one request/one reply) and `Stream` (line loop).
- `go/internal/host/router/toolmap.go` — 103-arm tool→message facade; alias normalization; rejection.
- `go/internal/host/router/ingress.go` — request parsing; tab-id preferred-order resolution (sub-pattern).
- `go/internal/host/pending/store.go`, `id_allocator.go` — id-rewrite correlation.
- `go/internal/host/socketbridge/session.go`, `listener.go`, `listener_unix.go` — sessions and platform listeners.
- `go/internal/host/nativeio/codec.go` — 4-byte LE length framing, 16 MiB cap.
- `go/internal/host/config/socket_path.go` — socket path resolution (single owner convention).
- `go/internal/installer/native_host.go` — per-browser native-messaging manifest; `HostName = "surf.browser.host"`.
- `go/internal/host/providers/chatgpt.go` — `NativeCaller` interface; `GET_CHATGPT_COOKIES` → "login required".
- `go/internal/cli/commands/base.go` — `BuildToolRequest` (declarative intent).
- `go/internal/cli/commands/format.go` — `parseResult`, `parseStructuredText` (`UseNumber`), `extractErrorText`.
- `go/internal/cli/commands/js.go`, `tool_simple.go`, `tab_ready.go` — escape hatch, simple-tool wrapper, readiness fence.
- `go/pkg/marketplacecapture/envelope.go` — versioned, self-validating capture envelope (sub-pattern, shared lineage with Upwork Tracker).

### Tests asserting behavior

- `go/internal/host/nativeio/codec_test.go` — framing, `ErrFrameTooLarge`, `ErrInvalidJSON`.
- `go/internal/host/pending/store_test.go` — correlation store.
- `go/internal/host/router/toolmap_test.go`, `toolmap_contract_test.go` — tool→message contract.
- `go/cmd/surf-host-go/main_test.go` — dispatch, chatgpt provider, disconnect, pure-error classification (`_resolvedTabId`/`_hint` stripping).
- `go/cmd/surf-go/integration_test.go` — full root build and socket round-trip against a mock host.
- `go/internal/cli/commands/chatgpt_bulk_socket_test.go` — concurrent socket use.
- `go/internal/cli/commands/format_test.go` — number normalization.

### Documented bugs and issues

- JSON number precision loss: `go/internal/cli/commands/format.go` `parseStructuredText` comment + `https://github.com/wesen/surf-cli/issues/5`.
- Pure-error classification before internal-key stripping: `go/cmd/surf-host-go/main_test.go` (comment records the bug that motivated the fix).

### Related Garden notes

- [[Research/Software Architecture Garden/surf-cli/README|Architecture Garden — surf-cli]] — project study index.
- [[Research/Software Architecture Garden/README|Software Architecture Garden]] — maturity vocabulary and evidence hierarchy.
- [[Research/Software Architecture Garden/devctl/README|devctl]] — host-owned intent/effect; durable evidence and reconciliation.
- [[Research/Software Architecture Garden/rag-evaluation-system/README|rag-evaluation-system]] — typed values across Go/JS/browser; host-owned effects.
- [[Research/Software Architecture Garden/go-go-datadrop/README|go-go-datadrop]] — serializable verbs at one trusted effect seam.
- [[Research/Software Architecture Garden/go-go-goja/README|go-go-goja]] — catalog→registration; escape hatches as documented debt (contrast: surf's escape hatch is intentional).
- [[Research/Software Architecture Garden/upwork-tracker/README|Upwork Tracker]] — shared lineage of the marketplace-capture envelope.
