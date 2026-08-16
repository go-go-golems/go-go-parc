---
title: surf-cli — Index of Design Patterns
aliases:
  - surf design pattern index
  - surf-cli pattern index
  - surf glossary
status: active
type: architecture-garden-index
created: 2026-08-16
analyzed: 2026-08-16
analysis_schema: architecture-garden-v1
repository: /home/manuel/workspaces/2026-08-07/add-3d-model-verbs/surf-cli
repository_commit: 89aadf5
derived_from: Research/Software Architecture Garden/surf-cli/README.md
tags:
  - architecture-garden
  - surf
  - design-pattern-index
  - browser-automation
  - native-messaging
  - ipc
  - go
related_notes:
  - "[[Research/Software Architecture Garden/surf-cli/README]]"
  - "[[Research/Software Architecture Garden/surf-cli/01 - Project Architecture Overview]]"
  - "[[Research/Software Architecture Garden/surf-cli/02 - Browser-Launched Host Broker]]"
  - "[[Research/Software Architecture Garden/surf-cli/Index of Design Patterns - Rationale]]"
  - "[[Research/Software Architecture Garden/README]]"
---

# surf-cli — Index of Design Patterns

This is the back-of-the-book index for the [[Research/Software Architecture Garden/surf-cli/README|surf-cli architecture study]]. It catalogues the design patterns and vocabulary of surf's browser-scripting broker — the CLI/host split, the browser-launched native-messaging host, the JavaScript facade, the live session as authority, and the serialized effect channel — so a reader can find a concept by name, recall it in one sentence, and jump to the exact place it is established, applied, compared, or owed.

This is a **hybrid index-plus-glossary**: each entry carries a one-sentence definition (the glossary job — *what does this mean?*) and a set of locators (the index job — *where can I read about this?*). It is filed by how a reader is likely to remember a concept, not by how the study happened to phrase it, so it carries many `See` redirects from alternate phrasings to the canonical entry.

## How to read this index

- Each entry is a **heading**, so every `See` and `see also` is a clickable link that lands on that entry.
- A trailing locator links into the surf-cli study. The five fundamentals live in [[Research/Software Architecture Garden/surf-cli/01 - Project Architecture Overview|the Project Architecture Overview]] (linked as "Pattern A"…"Pattern E"); the flagship goes deeper in [[Research/Software Architecture Garden/surf-cli/02 - Browser-Launched Host Broker|the Browser-Launched Host Broker entry]] (linked by its section); cross-cutting maturity and guidance live in the [[Research/Software Architecture Garden/surf-cli/README|project README]]. A locator points at the section that *substantively* treats the concept — a passing mention is not indexed (the disappointed-reader test).
- A leading **↳** marks a cross-reference into the wider Garden or a Pattern Zoo, so the reader can tell at a glance whether a pattern is local or travels.
- A trailing bracket, e.g. `[Established]`, `[Candidate ecosystem pattern]`, `[Open correctness obligation]`, is the Garden's [[Research/Software Architecture Garden/README#Pattern maturity vocabulary|maturity label]] for that pattern, taken from [[Research/Software Architecture Garden/surf-cli/README#Maturity assessment|the study's maturity table]].
- **`See`** redirects to the canonical entry when the entry itself has no locators (alternate phrasing, synonym, reader-memory handle). **`see also`** links to a *related but distinct* concept the reader should not collapse into one.
- For native-messaging handles, socket paths, frame budgets, and closed vocabularies, see the [[#Identity strings, schemas, and budgets|notation table]] near the end.

The reasoning behind every entry — what kind of evidence grounds it, and what a reader loses if it is omitted — is in [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns - Rationale|the companion rationale]].

---

## A

### Authority flows from being browser-launched

The governing law of the host broker: the browser *spawns* the host as a native-messaging child, so browser authority comes from the spawn, not from any "connect to the browser" operation the host performs. [Established] [[Research/Software Architecture Garden/surf-cli/02 - Browser-Launched Host Broker#2. Pattern statement|law (§2)]], [[Research/Software Architecture Garden/surf-cli/02 - Browser-Launched Host Broker#6. Mathematical and computer-science foundations|§6]]. *The non-obvious half of the broker pattern; the thing a user-started daemon cannot replicate.* *see also* [[#Browser-Launched Host Broker]], [[#The host cannot start itself]].

### Auth is not surf's job

*See* [[#Implicit authority]]. (The recorded design decision that credentials are out of scope: surf drives the human's signed-in session, it does not acquire one.)

## B

### Browser-Launched Host Broker

The flagship pattern: a native-messaging subprocess the browser owns, which *adds* a local socket for ephemeral CLI clients, so authority flows from being browser-launched while client access is a deliberately separate, layered channel. [Established] [[Research/Software Architecture Garden/surf-cli/01 - Project Architecture Overview#Pattern B — Host as native-messaging subprocess, not a server you start|Pattern B]], [[Research/Software Architecture Garden/surf-cli/02 - Browser-Launched Host Broker|deep entry]], [[Research/Software Architecture Garden/surf-cli/README#Candidate ecosystem patterns|README §Candidate]]. ↳ [[Research/Software Architecture Garden/devctl/README|devctl]] host-owned intent/effect; [[Transcripts/Research/10 - PBUI-MATHS Pattern Zoo Handbook|PBUI Pattern 5]] (command as data). *The strongest candidate for cross-project ecosystem guidance.* *see also* [[#Authority flows from being browser-launched]], [[#Effect channel]], [[#Native-messaging host]], [[#The host cannot start itself]].

### Browser owns the host

*See* [[#Browser-Launched Host Broker]]. (Reader-memory phrasing for the direction-of-authority law.)

## C

### Cascade disconnect

A single extension disconnect (stdin EOF) transitively invalidates every live CLI session and every pending request, because no reply can ever come back; the host implements it as `notify(all sessions) ∘ close(all sessions)` with per-session pending/stream reclamation. [Established] [[Research/Software Architecture Garden/surf-cli/02 - Browser-Launched Host Broker#5. Behavioral contract|§5]], [[Research/Software Architecture Garden/surf-cli/02 - Browser-Launched Host Broker#6. Mathematical and computer-science foundations|§6.4]]. *A safety (never-block-forever) property, and the reason an extension reload is surfaced, not hidden.* *see also* [[#Extension reload kills in-flight work]], [[#Disconnect is a graceful cascade, not a silent failure]].

### CLI client / host broker split

Pattern A: the process that presents a UI never holds browser authority; a disposable, stateless CLI talks JSON over a local socket to a persistent host that does. [Established] [[Research/Software Architecture Garden/surf-cli/01 - Project Architecture Overview#Pattern A — CLI client / host broker split|Pattern A]]. *see also* [[#Browser-Launched Host Broker]], [[#Declarative intent over a serialized effect channel]].

## D

### Declarative intent over a serialized effect channel

Pattern E: everything the browser must do is self-describing JSON intent, and one mutex-guarded native write linearizes all browser effects, which is what lets concurrent CLI clients share one browser safely. [Established] [[Research/Software Architecture Garden/surf-cli/01 - Project Architecture Overview#Pattern E — Declarative intent over a single serialized effect channel|Pattern E]], [[Research/Software Architecture Garden/surf-cli/02 - Browser-Launched Host Broker#6. Mathematical and computer-science foundations|§6.2]]. *The glue that makes the CLI/host split and the facade composable across process boundaries.* *see also* [[#Effect channel]], [[#Identity rewrite at the boundary]], [[#One writer is one linearization point]].

### Disconnect is a graceful cascade, not a silent failure

The candidate ecosystem rule that an extension reload — the one signal a CLI most needs — should propagate as an explicit, actionable message rather than hide behind a generic timeout. [Candidate ecosystem pattern] [[Research/Software Architecture Garden/surf-cli/02 - Browser-Launched Host Broker#12. Candidate ecosystem guidance|§12]]. *see also* [[#Cascade disconnect]], [[#Extension reload kills in-flight work]].

### Dual-mode commands (Markdown / rows toggle)

One extraction function feeds two renderers — a human Markdown report by default and structured rows behind `--with-glaze-output` — so the same command serves a terminal human and a piping script with no duplicated work. [Established] [[Research/Software Architecture Garden/surf-cli/01 - Project Architecture Overview#Pattern C — JavaScript behind a tooling facade|Pattern C]]. *see also* [[#Tool facade]].

## E

### Effect channel

The single serialized native write path (`writeNative` + `nativeWriteMu`); the one linearization point for all browser effects, which makes concurrent CLI clients safe by construction. [Established] [[Research/Software Architecture Garden/surf-cli/02 - Browser-Launched Host Broker#4. Implementation details|§4.3]], [[Research/Software Architecture Garden/surf-cli/02 - Browser-Launched Host Broker#7. Design-pattern vocabulary|§7]]. *see also* [[#Declarative intent over a serialized effect channel]], [[#One writer is one linearization point]].

### Escape hatch

An intentionally-present raw surface (`surf js` / `eval`) that runs caller code in the page with the user's session; documented and named, not hidden or deprecated, because a fully closed facade would make surf unusable for anything it does not yet name. [Established] [[Research/Software Architecture Garden/surf-cli/01 - Project Architecture Overview#Pattern C — JavaScript behind a tooling facade|Pattern C]]. *see also* [[#Tool facade]], [[#Escape hatch is not a sandbox]].

### Escape hatch is not a sandbox

*See* [[#Escape hatch]]. (The discipline that the raw `js` surface is a power tool, not a safe one — it runs caller code in the page with the user's session, so the boundary is JSON, not "data vs code" and not "trusted vs untrusted".)

### Extension-internal bookkeeping keys

`_resolvedTabId` and `_hint` are fields the extension's `initNativeMessaging` wrapper appends to every response; they are not tool output and are stripped from both error classification and user-facing content so they never leak. [Established] [[Research/Software Architecture Garden/surf-cli/02 - Browser-Launched Host Broker#14. Evidence and references|§14]]. *see also* [[#Pure error classification at the effect boundary]].

### Extension reload kills in-flight work

The most operationally surprising failure: when the extension reloads, stdin EOFs, the host tells every CLI client to restart its command, and exits — so a long bulk export can be interrupted by a developer reload. [Failure mode] [[Research/Software Architecture Garden/surf-cli/02 - Browser-Launched Host Broker#9. Failure modes and tricky details|§9.1]]. *Correct (the host is the browser's child and the channel just closed) but operationally surprising; the explicit message is the mitigation, not silence.* *see also* [[#Cascade disconnect]].

## H

### The host cannot start itself

A direct corollary of the authority law: `surf <command>` does not launch the host; if the browser/extension is not running, the CLI's socket dial fails fast with a clear error, because only the browser can open a native-messaging channel to a host it launched. [Established] [[Research/Software Architecture Garden/surf-cli/02 - Browser-Launched Host Broker#9. Failure modes and tricky details|§9.6]]. *see also* [[#Authority flows from being browser-launched]], [[#Browser-Launched Host Broker]].

## I

### Identity rewrite at the boundary

The host mints a fresh host id per outbound native message and restores the client's original id on reply, so N concurrent CLI sessions share one extension stream without leaking client identity into the extension. [Established] [[Research/Software Architecture Garden/surf-cli/02 - Browser-Launched Host Broker#4. Implementation details|§4.4]], [[Research/Software Architecture Garden/surf-cli/02 - Browser-Launched Host Broker#6. Mathematical and computer-science foundations|§6.3]]. *see also* [[#Declarative intent over a serialized effect channel]].

### Implicit authority

Pattern D: authentication is not surf's job — the live, signed-in browser session *is* the authority, and surf drives it rather than acquiring it, which is what sidesteps 2FA/CAPTCHA/session-storage and is arguably the reason surf exists. [Established] [[Research/Software Architecture Garden/surf-cli/01 - Project Architecture Overview#Pattern D — Live browser session as the implicit authority|Pattern D]]. *see also* [[#Browser-Launched Host Broker]].

## J

### JavaScript behind a tooling facade

*See* [[#Tool facade]]. (The study's Pattern C, filed under the verb a reader remembers.)

### JSON number precision loss

A real, documented bug (issue #5): decoding JSON numbers as `float64` turned an integer tab id `441403900` into `"4.414039e+08"`, which `--tab-id` rejected and which was consistent with ten different integers; the fix uses `json.Decoder.UseNumber()` + integer normalization. [Failure mode] [[Research/Software Architecture Garden/surf-cli/01 - Project Architecture Overview#Pattern E — Declarative intent over a single serialized effect channel|Pattern E]], [[Research/Software Architecture Garden/surf-cli/02 - Browser-Launched Host Broker#14. Evidence and references|§14]]. *The canonical "a number that crosses a JSON boundary is not the same number" failure; any new code crossing the boundary must respect it.*

## N

### Native framing

The byte contract the host and extension share: each message is a 4-byte little-endian length prefix followed by exactly that many bytes, capped at 16 MiB, which bounds untrusted input before JSON parsing. [Established] [[Research/Software Architecture Garden/surf-cli/02 - Browser-Launched Host Broker#4. Implementation details|§4.1]]. *see also* [[#Native-messaging host]].

### Native-messaging host

The browser-defined role: a process the browser launches by stable name (`surf.browser.host`), communicating over length-prefixed stdin/stdout frames; surf's instance is the host the browser spawns, which then *adds* a socket to become the broker. [Established] [[Research/Software Architecture Garden/surf-cli/02 - Browser-Launched Host Broker#3. Concrete architecture|§3]]. *see also* [[#Browser-Launched Host Broker]], [[#Native framing]].

### Numbers are not safe across JSON

*See* [[#JSON number precision loss]]. (Reader-memory phrasing for the precision-loss failure mode.)

## O

### One writer is one linearization point

The math behind the effect channel: because exactly one goroutine at a time holds the native write mutex, the observed native stream is a total order consistent with the mutex acquisitions, giving a single equivalent serial execution as seen by the extension. [Established] [[Research/Software Architecture Garden/surf-cli/02 - Browser-Launched Host Broker#6. Mathematical and computer-science foundations|§6.2]]. *Linearizes dispatch, not browser execution.* *see also* [[#Effect channel]], [[#Declarative intent over a serialized effect channel]].

### Owned-tab retry with an idempotency boundary

A retry helper that always opens a fresh tab (never reuses a target whose execution context navigation may have invalidated) and is documented as safe only for read-only operations, because replaying a mutation is not idempotent. [Candidate ecosystem pattern] [[Research/Software Architecture Garden/surf-cli/01 - Project Architecture Overview#Open questions|overview §Open questions]]. *The transferable idea is the documented idempotency boundary on a retry helper — naming when retry is safe, not just how to retry.*

## P

### Pure error classification at the effect boundary

A native response is an error iff an `error` field is present *and* every other key (except `type`, `error`, and extension-internal bookkeeping keys) is nil; a non-empty payload that also carries `error` is a result, not an error. [Established] [[Research/Software Architecture Garden/surf-cli/02 - Browser-Launched Host Broker#14. Evidence and references|§14]]. *see also* [[#Extension-internal bookkeeping keys]].

## R

### Readiness fence (stable-for window)

A readiness probe that waits until the real page (a stable href, not `about:blank`, `readyState` complete/interactive) is unchanged for a declared window, rather than treating one snapshot of `readyState` as "loaded". [Emergent] [[Research/Software Architecture Garden/surf-cli/01 - Project Architecture Overview#Open questions|overview §Open questions]]. *A stability property over time, not a single check.*

## S

### Serialized effect channel

*See* [[#Effect channel]]. (Alternate phrasing of the single-write-path concept.)

### Socket is not a trust boundary

The Unix socket is a *structuring* boundary, not a *security* one: any local process can connect and request any tool, so the broker is meaningful on a single-user workstation and wrong on a shared host. [Open correctness obligation] [[Research/Software Architecture Garden/surf-cli/02 - Browser-Launched Host Broker#9. Failure modes and tricky details|§9.2]], [[Research/Software Architecture Garden/surf-cli/02 - Browser-Launched Host Broker#13. Open questions|§13]]. *A deliberate scope an adopter must state explicitly, not a bug in the broker.*

### Surf is not a daemon

*See* [[#The host cannot start itself]]. (The reader-memory phrasing that most directly refutes the tempting "start a server" alternative.)

## T

### Tab targeting (preferred-order, absence-as-sentinel)

Tab scope is resolved once, in a declared preference order (`msg.tabId` → `params.tabId` → `args.tabId`), with `-1` meaning "no override" because `0` is a valid tab id and cannot serve as the absent value. [Emergent] [[Research/Software Architecture Garden/surf-cli/01 - Project Architecture Overview#Pattern E — Declarative intent over a single serialized effect channel|Pattern E]]. *An emergent contract; the sentinel is a convention, not a type.*

### Tool facade

Pattern C: page interaction is a closed set of named, versioned tools (~103-arm switch) plus ~60 per-site embedded scripts behind typed `SURF_OPTIONS`, with raw `js` kept as an explicit escape hatch rather than the primary surface. [Established] [[Research/Software Architecture Garden/surf-cli/01 - Project Architecture Overview#Pattern C — JavaScript behind a tooling facade|Pattern C]]. *see also* [[#Dual-mode commands (Markdown / rows toggle)]], [[#Escape hatch]].

### The facade is not a type system

*See* [[#Tool facade]]. (The discipline that the facade translates and normalizes but does not statically check — args are `map[string]any` validated loosely — so it is not a substitute for typed args.)

## V

### Versioned capture envelope

A capture is a versioned, self-validating evidence unit (`marketplace-capture/v1`) whose validity is a precondition for a sha256 fingerprint, and for which an empty result is a distinct valid state rather than a failure. [Candidate ecosystem pattern] [[Research/Software Architecture Garden/surf-cli/01 - Project Architecture Overview#Open questions|overview §Open questions]]. ↳ [[Research/Software Architecture Garden/upwork-tracker/README|Upwork Tracker]] immutable capture boundary. *Shared lineage with the Upwork Tracker envelope.*

## W

### Windows named-pipe transport (not implemented)

The client-side Windows transport over `//./pipe/surf` is explicitly not yet implemented and returns a clear error rather than silently failing; the host listener has a Windows stub. [Open correctness obligation] [[Research/Software Architecture Garden/surf-cli/02 - Browser-Launched Host Broker#4. Implementation details|§4.5]]. *An acknowledged gap, not a hidden one.*

---

## Identity strings, schemas, and budgets

This is the index's notation table. surf speaks in a small set of versioned handles, fixed paths, frame budgets, and closed vocabularies; a reader will frequently think "what did `surf.browser.host` mean again?" Look it up here, then follow the locator.

| Handle / value | Kind | Meaning | Where |
|---|---|---|---|
| `surf.browser.host` | native-messaging name | The stable host name the browser launches `surf-host-go` by; written into per-browser native-messaging manifests. | [[Research/Software Architecture Garden/surf-cli/02 - Browser-Launched Host Broker#3. Concrete architecture|§3]], [[#Native-messaging host]] |
| `/tmp/surf.sock` | socket endpoint | Default Unix-domain socket the host listens on for CLI clients. | [[Research/Software Architecture Garden/surf-cli/02 - Browser-Launched Host Broker#3. Concrete architecture|§3]], [[#CLI client / host broker split]] |
| `//./pipe/surf` | socket endpoint (Windows) | Windows named-pipe equivalent of the socket; client transport not yet implemented. | [[Research/Software Architecture Garden/surf-cli/02 - Browser-Launched Host Broker#4. Implementation details|§4.5]], [[#Windows named-pipe transport (not implemented)]] |
| `SURF_SOCKET_PATH` | env override | Overrides the socket endpoint at runtime; the host communicates the resolved endpoint to the extension in `HOST_READY`. | [[Research/Software Architecture Garden/surf-cli/02 - Browser-Launched Host Broker#4. Implementation details|§4.2]] |
| 4-byte LE length prefix | frame contract | Each native message is a little-endian `uint32` length followed by exactly that many bytes. | [[Research/Software Architecture Garden/surf-cli/02 - Browser-Launched Host Broker#4. Implementation details|§4.1]], [[#Native framing]] |
| `DefaultMaxFrameSize = 16 * 1024 * 1024` | frame budget | 16 MiB cap on a single native frame; bounds untrusted input before JSON parsing. | [[Research/Software Architecture Garden/surf-cli/02 - Browser-Launched Host Broker#4. Implementation details|§4.1]], [[#Native framing]] |
| `HOST_READY` | startup frame | The host's first outbound native message, carrying the resolved socket endpoint, sent before accepting CLI sessions. | [[Research/Software Architecture Garden/surf-cli/02 - Browser-Launched Host Broker#4. Implementation details|§4.2]] |
| `extension_disconnected` | disconnect frame | Sent to every CLI session when stdin EOFs (extension reloaded); carries a "restart your command" message. | [[Research/Software Architecture Garden/surf-cli/02 - Browser-Launched Host Broker#5. Behavioral contract|§5]], [[#Cascade disconnect]] |
| `tool_request` / `execute_tool` | intent envelope | The JSON shape a CLI sends: `{type, method, params:{tool,args}, id, tabId, windowId}`. | [[Research/Software Architecture Garden/surf-cli/01 - Project Architecture Overview#Pattern E — Declarative intent over a single serialized effect channel|Pattern E]], [[#Declarative intent over a serialized effect channel]] |
| `providerPrefixes` | closed vocabulary | Tool-name prefixes the host denies before any effect: `ai`, `chatgpt`, `gemini`, `perplexity`, `grok`, `aistudio`, `aistudio.build`. | [[Research/Software Architecture Garden/surf-cli/01 - Project Architecture Overview#Pattern C — JavaScript behind a tooling facade|Pattern C]], [[#Tool facade]] |
| `deferredTools` | closed vocabulary | Tool names the host defers/rejects in the go-core profile (`smoke`, `batch`, `health`, `perf.*`, `bookmark.*`, `history.*`). | [[Research/Software Architecture Garden/surf-cli/01 - Project Architecture Overview#Pattern C — JavaScript behind a tooling facade|Pattern C]], [[#Tool facade]] |
| `marketplace-capture/v1` | capture schema | Versioned, self-validating capture envelope; validity precedes a sha256 fingerprint; empty records are a distinct valid state. | [[Research/Software Architecture Garden/surf-cli/01 - Project Architecture Overview#Open questions|overview §Open questions]], [[#Versioned capture envelope]] |
| Extension-internal keys | closed vocabulary | `_resolvedTabId`, `_hint` — bookkeeping the extension appends to every response; stripped from classification and user-facing output. | [[Research/Software Architecture Garden/surf-cli/02 - Browser-Launched Host Broker#14. Evidence and references|§14]], [[#Extension-internal bookkeeping keys]] |

---

## Cross-reference summary

The concepts above connect to the wider Garden through a small number of load-bearing correspondences. Each is a *correspondence, not an equivalence*: the Garden's discipline is that a registry is not authority, a socket is not a trust boundary, and a tool name is not the page effect it maps to.

- **Serializable intent crosses boundaries while trusted hosts own effects** — [[#Declarative intent over a serialized effect channel]], [[#Browser-Launched Host Broker]], [[#Tool facade]]. ↳ [[Transcripts/Research/10 - PBUI-MATHS Pattern Zoo Handbook#Pattern 5 — Command as Data|PBUI Pattern 5]]; [[Research/Software Architecture Garden/devctl/README|devctl]] host-owned intent/effect; [[Research/Software Architecture Garden/rag-evaluation-system/README|rag-evaluation-system]].
- **A versioned, self-validating capture envelope with a content-addressed fingerprint** — [[#Versioned capture envelope]]. ↳ [[Research/Software Architecture Garden/upwork-tracker/README|Upwork Tracker]] immutable capture boundary (shared lineage).
- **An intentional escape hatch alongside a closed facade** — [[#Escape hatch]], [[#Tool facade]]. ↳ [[Research/Software Architecture Garden/go-go-goja/README|go-go-goja]] (whose bypasses are documented *debt*; contrast: surf's `js` is an intentional, non-debt escape hatch).

Patterns marked *Candidate ecosystem pattern* ([[#Browser-Launched Host Broker]], [[#Disconnect is a graceful cascade, not a silent failure]], [[#Owned-tab retry with an idempotency boundary]], [[#Versioned capture envelope]]) have at most shared-lineage or adjacent-domain evidence as a second occurrence, and so remain candidates until an independent "script the browser" implementation confirms the same law.

## Related documents

- [[Research/Software Architecture Garden/surf-cli/README|surf-cli study]] — the evidence-pinned source this index catalogues.
- [[Research/Software Architecture Garden/surf-cli/01 - Project Architecture Overview|Project Architecture Overview]] — the five fundamentals in full.
- [[Research/Software Architecture Garden/surf-cli/02 - Browser-Launched Host Broker|Browser-Launched Host Broker]] — the deep treatment of the flagship pattern.
- [[Research/Software Architecture Garden/surf-cli/Index of Design Patterns - Rationale|Rationale]] — why each term was chosen and why it belongs.
- [[Research/Software Architecture Garden/README|Software Architecture Garden]] — the Garden root and its maturity vocabulary.
