---
title: "slop Models in Go: Pi's Agent Directory on Geppetto Engines"
aliases:
  - slop Models in Go
  - SLOP-010 Deep Dive
  - geppetto providers/pi
  - slop sample on geppetto
tags:
  - project
  - slop
  - geppetto
  - llm
  - go
  - credentials
status: active
type: project
created: 2026-10-29
repo: /home/manuel/workspaces/2026-10-28/slop-computer/slop-computer
---

# slop Models in Go: Pi's Agent Directory on Geppetto Engines

On 29 October 2026, slop.computer ("slop") stopped needing Node.js to call language models. Its `sample` capability lets a hosted page ask a model a question, with tools defined by the page. Until then it ran through a Node child process that loaded the Pi SDK. It now runs in Go, through the **geppetto** inference library and a new geppetto package, `providers/pi`. That package reads the same configuration files Pi reads, so models and logins set up with Pi keep working.

The work spans two repositories:

| Repository | Change | Where |
|---|---|---|
| geppetto | `pkg/steps/ai/providers/pi`: 1,358 lines of code and 430 lines of tests; also dependency and gosec fixes | PR #442, released as **v0.13.12** |
| slop | `pkg/piworker/gepp`: 590 lines of code and 392 lines of tests; `slop serve --models pi`; an example chat app | branch `task/slop-geppetto-sample` (ticket SLOP-010) |

The report proceeds in dependency order:
1. the system before the change (§1) and the decision to use geppetto (§2);
2. Pi's configuration files (§3) and the parts of geppetto the design rests on (§4);
3. the new geppetto package (§5–7) and the new slop backend (§8–9);
4. verification (§10), the failures met (§11), and the costs and open questions (§12).

> [!summary]
> - **One seam.** slop's model calls go through one Go interface, `piworker.Backend`. The Node worker was one implementation; `gepp.Backend` is a second. Nothing above the interface changed: not the HTTP API, not the page runtime, not the admin-only policy.
> - **Pi's files, read in Go.** `providers/pi` reads `settings.json`, `models-store.json`, `models.json` and `auth.json` with Pi's own rules (merge order, credential precedence, `$ENV` and `!command` values). It maps each model's wire API to a geppetto engine. A refreshed OAuth credential is written back under a lock compatible with Pi's, so Pi stays logged in.
> - **A round loop in slop.** One geppetto engine call is one model round. slop's loop keeps text across rounds, runs page tools in parallel, offers no tools in the last round, and spends one 64k-token output budget per call. The 20-check browser suite passed three times on real models.

---

## 1. The starting point

### 1.1 What `sample` is

A slop app is an HTML page written against the claude.ai Artifact runtime contract. The page calls `await claude.use("sample")` and gets a function:

```js
const sample = await claude.use("sample");
const r = await sample([{role: "user", content: "Roll 3 dice"}], {
  tools: [{name: "roll_dice", description: "…", inputSchema: {…}, execute: ({n, sides}) => …}],
  effort: "high",
  onText: ({text}) => render(text),       // the whole answer so far
});
// r = {text, truncated, modelTierApplied, modelApplied?}
```

The contract has four properties that shape the implementation:
1. **The call is memoryless.** Input is a string, or a list of `{role, content}` text turns that ends with a user turn.
2. **Tools run in the page.** The model asks for a tool, and the page's `execute` function produces the result.
3. **Streaming is cumulative.** `onText` receives the whole answer so far, not a delta.
4. **Errors are codes.** A call rejects with a code from a fixed set: `cancelled`, `rate_limited`, `prompt_too_large`, `empty_completion`, `images_unavailable`, `upstream_error`, and others.

slop adds its own policy:
- any model and effort the server can reach may be named;
- there is no per-person budget;
- only admins may call it;
- each call writes one audit row.

### 1.2 The path of one call

```mermaid
sequenceDiagram
  participant Page as Page (web/runtime/src/sample.ts)
  participant HTTP as slop (pkg/server/rt_sample.go)
  participant BE as piworker.Backend
  participant Prov as Provider
  Page->>HTTP: POST /_rt/sample {input, modelTier, model?, effort?, tools?}
  HTTP-->>Page: SSE: call {call}
  HTTP->>BE: Sample(ctx, Request, emit, execute)
  BE->>Prov: round 1 (streamed)
  Prov-->>BE: text deltas, tool call
  BE-->>HTTP: emit(text) · execute(tool) blocks
  HTTP-->>Page: SSE: text · tool {use, name, input}
  Page->>HTTP: POST /_rt/sample/{call}/tools/{use} {value, isError}
  HTTP-->>BE: ToolResult
  BE->>Prov: round 2 with the result
  Prov-->>BE: text
  BE-->>HTTP: emit(usage) · emit(result)
  HTTP-->>Page: SSE: result
```

The HTTP handler `startSample` enforces the policy and translates events. Its checks are:
- a live view;
- a configured backend;
- `sample` declared in the app's manifest;
- the admin level;
- recorded consent.

Everything about models happens behind one interface (`pkg/piworker/backend.go`):

```go
type Backend interface {
	Models() []Model                                        // for sample.limits()
	Sample(context.Context, Request, func(Event), ExecuteTool) error
	Close() error
}
type ExecuteTool func(context.Context, Event) (ToolResult, error) // blocks until the page answers
```

`Event` has six types: `text`, `thinking`, `tool`, `usage`, `result` and `error`. `usage` is aggregated into the audit row and is never sent to the page.

### 1.3 The Node worker

The first implementation, `piworker.Client`, started `web/piworker/dist/worker.js` (442 lines of TypeScript in `main.ts`) and exchanged JSON lines with it over stdio. The worker loaded Pi's `ModelRuntime` from `@earendil-works/pi-coding-agent` 0.85.1, picked the tier models, and ran the rounds.

It worked, and a 20-check browser suite passed on it. But it has three costs:
- a Node runtime and npm packages in the server image, which had not been done yet;
- a second language at the model boundary;
- a process protocol between Go and Node to maintain.

## 2. The decision

Four options were studied:

| Option | Assessment |
|---|---|
| Keep the Node worker | Covers every Pi provider, Bedrock and Vertex included. Costs Node in the image and a cross-process protocol. |
| Write providers from scratch in Go | Means SSE parsing for four wire APIs, tool-call argument deltas, reasoning formats and OAuth renewal. geppetto already maintains all of these. |
| **geppetto engines + a Pi loader** | **Chosen.** geppetto has engines for the APIs in use, streams the events needed, keeps credentials outside settings, and links no cgo. |
| pinocchio or sessionstream | pinocchio is an application (CLI, TUI, web chat). sessionstream is a command, event and projection framework with websocket hydration. `sample` is one streamed HTTP call whose wire format the contract already fixes. Neither fits as a dependency. pinocchio's OAuth profile store informed the lock design. |

Every model in the user's `settings.json` `enabledModels` uses one of two wire APIs:
- lunaroute models use `openai-completions`;
- ChatGPT subscription models (`openai-codex`) use `openai-codex-responses`.

geppetto has engines for both, which made the choice safe for the configuration actually in use.

The loader was placed in geppetto rather than in slop, so that other geppetto applications can use a Pi login too.

## 3. Pi's agent directory

Pi keeps its configuration in `~/.pi/agent`, or in `$PI_CODING_AGENT_DIR`. The formats below were read from Pi's compiled sources (`pi-coding-agent/dist/core/model-config.d.ts`, `auth-storage.js`, `provider-composer.js`, `resolve-config-value.js`), not guessed from file contents.

### 3.1 The four files

| File | Shape | Meaning |
|---|---|---|
| `settings.json` | `{defaultProvider, defaultModel, defaultThinkingLevel, enabledModels[]}` | the user's default and the models the user cycles through |
| `models-store.json` | `{provider: {models: [ModelDef]}}` | the catalog Pi refreshed from providers |
| `models.json` | `{providers: {id: {baseUrl, api, apiKey, headers, compat, models[]}}}` | user-defined providers and overrides |
| `auth.json` | `{provider: Credential}` | one credential per provider |

A model definition carries:
- `id`, `api` and `baseUrl`;
- `reasoning` and `input` (`["text","image"]`);
- `contextWindow` and `maxTokens` (or `maxOutputTokens`);
- optional `compat` (`maxTokensField`, `supportsReasoningEffort`, `thinkingFormat`);
- optional `thinkingLevelMap`, which maps a Pi level to the provider's value, or to `null` when the level is not offered.

A credential is one of two kinds:

```ts
type Credential =
  | { type: "api_key"; key?: string; env?: Record<string, string> }
  | { type: "oauth"; access: string; refresh: string; expires: number /* ms */; [extra: string]: unknown };
```

### 3.2 Rules that matter

- **Merge order.** `models.json` overrides the store per model. A provider's `baseUrl`, `api` and `headers` in `models.json` also apply to that provider's stored models. Only the `providers` key is read: the real `models.json` on the development machine also had legacy top-level provider keys, which Pi ignores.
- **Credential precedence.** A stored `auth.json` credential comes first, then the provider's configured `apiKey` in `models.json`.
- **Configured values.** A key or header value can be:
  - `!cmd`: run through the shell, stdout used;
  - `$NAME` or `${NAME}`: an environment variable, looked up in the credential's `env` map first;
  - `$$` or `$!`: a literal `$` or `!`;
  - anything else: a literal.
- **Lunaroute.** Pi's lunaroute extension stores the gateway key as an OAuth `access` value whose "refresh" returns the same credential. In effect it is a static key.
- **Codex.** Its OAuth refresh tokens rotate: after a refresh, the previous refresh token is invalid.
- **Locking.** Pi writes `auth.json` under *proper-lockfile*:
  - the lock is a directory, `auth.json.lock`, created with `mkdir`;
  - the holder refreshes the directory's modification time;
  - another process may remove a lock whose modification time is older than its stale interval;
  - Pi uses 30 s for its asynchronous lock and the library default of 10 s for its synchronous lock.

## 4. The parts of geppetto the design uses

| Part | API | Role here |
|---|---|---|
| Turns | `turns.Turn`, `NewUserTextBlock`, `NewAssistantTextBlock`, `NewUserMultimodalBlock`, `NewToolUseBlock(WithError)`, `toolblocks.ExtractPendingToolCalls` | the conversation, and the tool calls a round left pending |
| Engines | `engine.Engine.RunInference(ctx, *Turn) (*Turn, error)` | one streamed provider request; tools are left as `tool_call` blocks, not executed |
| Per-turn config | `engine.KeyInferenceConfig` → `InferenceConfig{MaxResponseTokens, ReasoningEffort, ThinkingType, ThinkingBudget}` | the per-round output bound and the thinking level |
| Events | `events.WithEventSinks(ctx, sink)`; `EventTextDelta`, `EventReasoningDelta`, `EventProviderCallFinished{Usage, StopReason}`, `EventError` | streaming and usage |
| Tools | `tools.WithRegistry(ctx, reg)`; `ToolDefinition{Name, Description, Parameters *jsonschema.Schema}` | advertising the page's tools to the model |
| Credentials | `credentials.BearerTokenSource`, `Store`, `Refresher`, `NewRenewableBearerTokenSource`, `oauth.Client` | tokens at request time, renewal with singleflight and one replay after a 401 |
| Codex | `openaicodex.RequestTransport(Source, Options)` | the Codex route plus `Authorization` and `chatgpt-account-id` headers |

One fact determines the shape of slop's backend: **`RunInference` is exactly one model round.** geppetto's own `toolloop.RunLoop` could run rounds, but it has no hook between rounds to change `MaxResponseTokens`, and the per-call budget needs that. Its tool executor model also does not fit tools that run in a browser. slop therefore owns its loop (§9).

## 5. `providers/pi`: the catalog and values

The package's files and line counts:

```text
pkg/steps/ai/providers/pi/
  agentdir.go   176  LoadAgentDir, options, DefaultDir
  catalog.go    240  Model, Catalog, the merge
  values.go      88  $ENV / !command resolution
  authfile.go   204  Entry, the credentials.Store over auth.json, atomic writes
  lock.go       136  the proper-lockfile-compatible lock
  resolve.go    295  Resolve, credentials, headers, HasCredential, Available
  thinking.go    81  Pi level → InferenceConfig
  codex.go      138  Codex OAuth refresh and source
```

### 5.1 Loading

```go
dir, err := pi.LoadAgentDir(path,
	pi.WithEnv(os.LookupEnv),          // for $NAME values
	pi.WithCommandValues(),            // allow !cmd (off by default)
	pi.WithProviderHeaders("lunaroute", map[string]string{"lunaroute-agent": "slop", …}),
)
```

**Missing files and environment.** A missing file is treated as empty; a malformed file is an error that names the file. The library never calls `os.Getenv` itself; geppetto's glazed linter forbids it in library code. `DefaultDir(envValue)` therefore takes the variable's value from the caller.

### 5.2 The merge

`buildCatalog` folds the two model files into one map keyed by `provider/id`:

```text
for each provider, model in models-store.json:   add(model)
for each provider pc in models.json.providers:
    for each model in pc.models:                 add(model, provider defaults = pc)
    for each stored model of this provider:      apply pc.baseUrl, pc.api, pc.headers
for each model: Supported = api ∈ {openai-completions, openai-responses,
                                   openai-codex-responses, anthropic-messages,
                                   google-generative-ai}
```

`maxOutputTokens` stands in for `maxTokens` when only the former is set.

On the development machine the catalog has 222 models, and 65 of them use a supported API. The 157 Bedrock models are listed with `Supported: false`.

### 5.3 Configured values

`resolveValue` is a direct port of Pi's resolution. It differs from Pi in two ways:
- `!cmd` values require `WithCommandValues()`;
- a failing command produces the fixed message "the configured command failed". The command text is never echoed, because it may contain a secret.

## 6. `providers/pi`: from a model to an engine

### 6.1 `Resolve`

```go
func (a *AgentDir) Resolve(ctx context.Context, ref string, o ResolveOptions) (*Resolved, error)
type Resolved struct { Model Model; Settings *settings.InferenceSettings; build func(...) (engine.Engine, error) }
func (r *Resolved) Engine() (engine.Engine, error)
```

```mermaid
flowchart TD
  R["Resolve(ref, {Thinking, MaxTokens})"] --> L{catalog lookup}
  L -- unknown --> E1[ErrUnknownModel]
  L -- unsupported API --> E2[UnsupportedAPIError]
  L --> S["InferenceSettings:<br/>no temperature / top-p,<br/>Inference = thinkingConfig + MaxResponseTokens,<br/>ModelInfo.Reasoning,<br/>HTTPClient + headers"]
  S --> A{model.API}
  A -- openai-codex-responses --> C["codexSource(auth.json)<br/>openaicodex.RequestTransport<br/>→ openai_responses.NewEngine"]
  A -- openai-completions / responses --> B["credential(provider)<br/>→ BearerTokenSource<br/>→ openai / openai_responses engine"]
  A -- anthropic-messages --> D["static key → x-api-key settings<br/>or bearer source → claude engine"]
  A -- google-generative-ai --> G["static key → gemini engine"]
  style E1 fill:#f2dede,stroke:#a94442,color:#000
  style E2 fill:#f2dede,stroke:#a94442,color:#000
```

Three choices in `Resolve` need explanation:

1. **Engines are built directly, not through `StandardEngineFactory`.** The factory validates that a Responses provider has an API key or a bearer source. A Codex engine has neither: its credentials live in the transport's middleware.
2. **No temperature and no top-p.** geppetto's chat settings default the temperature to 0.7. Pi sends neither value, so both are cleared, and providers apply their own defaults, as they did under Pi.
3. **`compat.maxTokensField` is expressed through `ModelInfo.Reasoning`.** geppetto's Chat Completions builder sends `max_completion_tokens` for models it considers reasoning models and `max_tokens` otherwise. Pi's default is `max_completion_tokens`, and `maxTokensField: "max_tokens"` switches it. Setting `ModelInfo.Reasoning = (maxTokensField != "max_tokens")` reproduces Pi's choice of field. Its only other effect, dropping temperature, is moot because none is sent.

### 6.2 Credentials

```text
credential(provider):
  e := auth.json[provider]
  api_key with key       → resolveValue(key, e.env) → StaticBearerTokenSource
  oauth                   → e.access as a static key   (lunaroute: refresh returns the same credential)
  none                    → models.json providers[provider].apiKey → resolveValue → static
  otherwise               → NoCredentialError{provider}  ("log in with pi, or set apiKey in models.json")
```

Codex is the one OAuth provider with a real refresh (§7.2), so it takes its own path. Treating any other OAuth entry as a static key matches Pi's lunaroute behaviour. It also avoids a renewable source rejecting a credential whose `expires` field is stale but whose key still works.

`HasCredential(provider)` answers the same question without resolving any values: no environment lookups, no commands. `Available()` returns the supported models whose provider has a credential. It is the Go counterpart of Pi's "available models".

### 6.3 Headers

Lunaroute's gateway expects three headers that Pi's extension sends: `lunaroute-agent` and two session ids. geppetto's Chat Completions request sets only `Content-Type`, `Accept` and `Authorization`. `withHeaders` therefore wraps the HTTP client's `RoundTripper`. It adds the merged host and `models.json` headers to each request, and never overrides a header the engine set, `Authorization` in particular. A mutation test confirmed that the end-to-end test detects the loss of this transport: it fails with `expected: "slop" actual: ""`.

### 6.4 Thinking levels

Pi's levels are `off`, `minimal`, `low`, `medium`, `high` and `xhigh`. `thinkingConfig` follows pi-ai's request builders per wire API:

| API / format | level `L` | `off` |
|---|---|---|
| Chat Completions (default) | `ReasoningEffort = map[L] ?? L` if effort is supported | `map.off` if it is a string |
| Chat Completions, `thinkingFormat: zai` | `ThinkingType = enabled` (+ effort if supported) | `ThinkingType = disabled` |
| Chat Completions, `thinkingFormat: deepseek` | `ThinkingType = enabled` (+ effort if supported) | `disabled`, unless `map.off` is explicitly `null` |
| Responses, Codex | `ReasoningEffort = map[L] ?? L` | nothing |
| Anthropic, Gemini | `ThinkingBudget`: 1024, 2048, 8192, 16384 or 32768 tokens | nothing |

A level that the model's `thinkingLevelMap` marks `null` is not sent. A model without `reasoning` gets no thinking configuration at all.

## 7. `providers/pi`: writing `auth.json`

### 7.1 The lock

The file is written only to persist a refreshed OAuth credential. The write must coexist with Pi running on the same host, so the lock follows proper-lockfile's protocol:

```text
acquire():
  loop until deadline (30 s):
    mkdir(auth.json.lock)            → success: hold
    EEXIST and mtime(lock) older than 30 s → remove it, retry at once
    otherwise                        → sleep min(10 ms · 2^k, 1 s) + jitter
hold():   touch the lock; every 5 s: stat it;
          if it is gone, or its mtime is not the one we set → compromised
          else touch it again
release(): stop refreshing; remove the lock unless compromised
```

The refresh interval of 5 s is below both of Pi's stale intervals, so neither of Pi's lock modes considers a held lock stale. A lock whose modification time changes underneath its holder has been taken over by another process. The write is then abandoned, and the lock directory is left in place, because it belongs to the other process.

The update itself is a read-modify-write under the lock:

```text
update(provider, fn):
  hold the lock
  all := read auth.json                      // again: another process may have rotated a token
  fields := all[provider] as a generic map   // unknown fields survive
  fn(fields)
  if the lock is compromised → abort
  write a temp file (0600) in the same directory, fsync, rename over auth.json, fsync the directory
```

### 7.2 Codex refresh

Pi's Codex OAuth client, read from `pi-ai/dist/auth/oauth/openai-codex.js`, has:
- client id `app_EMoamEEZ73f0CkXaXp7hrann`;
- token URL `https://auth.openai.com/oauth/token`;
- the account id in the access token's `https://api.openai.com/auth.chatgpt_account_id` claim.

The package builds:
- an `oauth.Client` with `RequireReplacementRefreshToken`, because the token rotates;
- a `credentials.RenewableBearerTokenSource` over a `providerStore`, the `credentials.Store` for one `auth.json` entry;
- `codexSource`, which implements `openaicodex.UnauthorizedSource`. It returns the current bearer token and the account id decoded from it.

When the store saves a refreshed credential, it also writes the new `accountId`. The test runs this against a fake token endpoint and a fake Codex API:
- the request carries the new bearer token and `chatgpt-account-id: acc-2`;
- `auth.json` then holds the rotated refresh token.

## 8. slop's backend: choosing the model

`pkg/piworker/gepp` (590 lines) implements `piworker.Backend`. `New(Config{AgentDir, Tiers, Options})` loads the directory with lunaroute's headers and fixes the three tiers (`quick`, `default`, `complex`), as the Node worker's `init` did:

```text
preferred := Pi's default model if it is available and in enabledModels (or enabledModels is empty)
             else the first available model of enabledModels
             else the first available model
tier t := the reference given by --model-t ("provider/id[:level]" or a bare id that names one model)
          else preferred
Models() := the tier models first (each once, labelled with its tier), then every other available model
```

The thinking level of one call follows the Node worker's expression:

```text
level := request.effort                               if set
      else the level named in the model reference      (e.g. "deepseek-4.1-flash:high")
      else "off"                                       for tier quick, or when settings' default is off
      else settings.defaultThinkingLevel
```

An explicit `model` in the request is used when it is available. Otherwise the call falls back to its tier, and `modelApplied` stays empty, which tells the page that its request was not honoured.

## 9. slop's backend: the round loop

### 9.1 The loop

```go
// pkg/piworker/gepp/sample.go (condensed)
for round := 0; round < rounds; round++ {                       // rounds: MaxRounds clamped to 1..10
	if contextBytes(t) > 512<<10 { return errContext }          // tool results may not grow the prompt past 512 KiB
	perRound, err := budget.next(m.MaxTokens)                    // min(model max, what the call has left)
	engine.KeyInferenceConfig.Set(&t.Data, engine.InferenceConfig{MaxResponseTokens: &perRound})
	eng, _ := res.Engine()
	rctx := ctx
	if round < rounds-1 && len(r.Tools) > 0 {
		rctx = tools.WithRegistry(rctx, registry)                // the last round offers no tools
	}
	out, err := eng.RunInference(events.WithEventSinks(rctx, sink), t)
	…
	budget.consume(sink.output)                                  // the provider's reported completion tokens
	t = out
	calls := toolblocks.ExtractPendingToolCalls(t)
	if len(calls) == 0 || budget.remaining <= 0 {
		if strings.TrimSpace(c.visible) == "" { return errEmpty }
		emit(result{Text: c.visible, FinalText: sink.text, Truncated: sink.truncated || budget.remaining <= 0, …})
		return nil
	}
	results := c.runTools(ctx, calls)                            // all at once; results in call order
	append results to t as tool_use blocks
}
return errRounds
```

**The per-turn configuration.** The per-round bound is set in the turn's data (`engine.KeyInferenceConfig`). It overrides the engine's default field by field, so the thinking configuration from `Resolve` is kept.

**The output budget.** The budget is a cap on one call, not a quota. Each call may generate at most 65,536 tokens across its rounds, and each round may use at most the model's own maximum.

### 9.2 The sink

The sink translates one round's geppetto events into the call's events:

| geppetto event | slop event |
|---|---|
| `EventTextDelta{Delta}` | `text {text: visible, delta}`; the first delta of a round after the first gets `"\n\n"` prepended when text is already visible |
| `EventReasoningDelta{Delta}` | `thinking {text, delta}`, with the same separator rule |
| `EventProviderCallFinished{Usage, StopReason}` | `usage {input, output, cache…, model}`; `StopReason` of `length`, `max_tokens` or `incomplete` marks the round truncated |
| `EventError{ErrorString}` | remembered, then classified (§9.4) |

The text is accumulated from deltas. It cannot be taken from `EventTextDelta.Text`, because that field holds the current round's message only, while the contract's `onText` receives the whole answer across rounds. The `"\n\n"` separator reproduces the Node worker (`main.ts:280-287`) exactly, so that existing pages see the same text.

### 9.3 Page tools

```text
runTools(calls):
  every call's name must be one of the page's tools, else "Unknown page tool"
  errgroup: for each call i, concurrently:
      r := execute(ctx, Event{type: tool, toolCallId, name, input: JSON(args)})   // slop's HTTP side waits on the page
      text := r.value if it is a JSON string, else its JSON
      out[i] := isError ? NewToolUseBlockWithError(id, nil, text) : NewToolUseBlock(id, text)
```

The `execute` callback belongs to `rt_sample.go`. It registers a channel for the tool use, sends a `tool` event to the page, and waits:
- for the page's POST of the result;
- or 150 s, after which an error result goes to the model;
- or for the call's cancellation.

geppetto renders an error result to the model as `{"error": text}`, so the model can recover from a failing tool.

### 9.4 Errors and cancellation

**Cancellation.** If the page aborts, the context is cancelled and `Sample` returns `ctx.Err()` without emitting anything. The page has already rejected the call with `cancelled` and the partial text.

**Errors.** Every other error becomes one `error` event, with the visible text so far attached. Error *messages* are fixed strings: provider diagnostics never reach the page, because a provider can echo the request back in its error body. A test sends a 500 response whose body contains the prompt, and asserts that the prompt is absent from the page's message.

| Cause | Code |
|---|---|
| a 401/403-like diagnostic, or no credential | `authentication_error` |
| 429, "rate limit" | `rate_limited` |
| 413, context length | `prompt_too_large` |
| the conversation over 512 KiB | `prompt_too_large` |
| no visible text at the end | `empty_completion` |
| images on a text-only model | `images_unavailable` |
| an unknown tool, out of rounds, anything else | `upstream_error` |

### 9.5 Selecting the backend

`slop serve --models pi|pi-node|fake` selects the backend. With `--models pi`, slop loads the agent directory with `WithEnv(os.LookupEnv)` and `WithCommandValues()`: it reads the operator's own Pi configuration on the operator's own host, and Pi treats those files the same way. Without `--models`, `--pi-fake` still means the fake backend and `--pi-worker` the Node worker, so existing start scripts are unaffected.

## 10. Verification

### 10.1 Unit tests

**geppetto (`pi_test.go`, 11 tests, run with `-race`):**
- the catalog merge, including ignored top-level `models.json` keys;
- missing and malformed files;
- configured values;
- credential precedence;
- an end-to-end Chat Completions request against `httptest`, checking:
  - path and bearer token;
  - both header sources;
  - `reasoning_effort`;
  - `max_tokens` chosen by `maxTokensField`;
  - no temperature;
  - a per-turn bound;
- `auth.json` writes, keeping fields and mode 0600 and releasing the lock;
- the lock: waiting, stale, serialized and compromised cases;
- Codex refresh with rotation and write-back;
- the JWT claim;
- a table of thinking levels;
- `Available`.

**slop (`gepp_test.go`, 9 tests, run with `-race`, three times)** use a scripted Chat Completions server:
- text streaming, result and usage;
- tools over rounds, with both tool calls in flight at once (peak 2), an error result as `{"error":…}`, and the second round's reduced bound;
- the last round without tools;
- failures: unknown tool, empty completion, 429, 401, 500 with a hidden body, images on a text-only model;
- cancellation during a tool, which emits no error event;
- tier order, quick without thinking, a `:high` reference, effort winning, an explicit model, and the fallback for an unknown model;
- no models; the budget arithmetic; images joining the last user turn as a data URL.

### 10.2 The browser suite on real models

The local server ran `--models pi` with these tiers: `quick` `lunaroute/glm-5.3-flash`, `default` `lunaroute/glm-5.3`, `complex` `lunaroute/deepseek-4.1-flash`. `web/rt-conformance/run.mjs` drives the sample conformance page in Chromium through the Workshop, accepting its consent dialog. It passed **20 of 20 in three consecutive runs**, with no Node process running. The table compares the Go backend's second run with the Node backend's first run, the day before:

| Check | Go backend | Node backend |
|---|---|---|
| multi-turn: an earlier turn is remembered | `ZEPHYRINE`, 444 ms | 11,768 ms |
| one page tool | `17.25°C`, 985 ms | 9,099 ms |
| several tools in one turn | `5555 and 1517`, 691 ms | 27,024 ms |
| chained tools over several rounds | `User u-77 lives in Quillmarsh.`, 1,028 ms | 19,747 ms |
| a throwing tool | `UNAVAILABLE` after 1 try | the same |
| abort while streaming | `cancelled`, 55 characters partial | the same |
| explicit `glm-5.3-flash` | `Hi there! 👋 How can I help you today?` | the same greeting, preceded by leaked reasoning ending in `</think>` |

**Timings.** The timing differences are large, but they are not evidence about the backends: both ran through the same gateway at different times, and a direct call to `glm-5.3` in the same session took between 65 and 80 s for five output tokens.

**Leaked reasoning.** This difference is attributable. geppetto's Chat Completions stream routes `reasoning_content` deltas to reasoning events, so reasoning no longer appears in the answer text.

### 10.3 An example chat app

`web/examples/llm-chat` is a single-page chat on `sample`. It has:
- history;
- streaming;
- a model picker filled from `sample.limits()`;
- an effort picker;
- three page tools (`get_time`, `roll_dice`, `calculate`);
- Stop.

Its README gives the four commands for a local run. A Playwright check drove it against the local server.

![The example chat app inside the Workshop: a tool call, its answer, and a follow-up answered from the history.](_assets/slop-geppetto-llm-chat.png)

**A contract consequence.** The example exposed a consequence of the contract worth recording. Turns are text, and `sample` is memoryless. The first version stored only each final answer. Asked "What did you roll?", the model could not see its earlier tool call, so it rolled again and reported different numbers. The example now writes each tool call and its result into the stored assistant turn (`[tools used: roll_dice({"n":3,"sides":6}) → [6,6,1]]`). The follow-up then answered "6 6 1" without calling a tool. Any chat page on this contract has to make the same choice.

## 11. Failures met

1. **Tool calls out of order.** When text preceded several tool calls, geppetto's Chat Completions reducer emitted the `tool_call` blocks in varying order between runs. Each result stays matched to its `tool_call_id`, so this does not affect correctness, and slop's test matches results by id. It is recorded upstream as an observation.
2. **A missing build tag.** A binary built without `-tags embed` served no Workshop: `embed_none.go` looks for the Workshop on disk relative to the working directory, and the test server's working directory was elsewhere. The suite failed with `waitForSelector … iframe`.
3. **A literal byte-order mark in source.** The string escape for the UTF-8 BOM was written into source as the literal character, and the compiler rejected it with `invalid BOM in the middle of the file`.
4. **Hooks in a workspace.** geppetto's lefthook hooks failed under the workspace `go.work` (`directory prefix . does not contain modules listed in go.work`). They also failed on a staged copy older than the working tree. Commits run with `GOWORK=off` after re-staging.
5. **Pre-push checks failed on `main`'s code.** The first push of the geppetto branch was rejected by the pre-push hook:
   - `gosec` G125 in `pkg/rerank/llamacpp/internal/transport/transport.go`, for `url.JoinPath` with an unescaped element;
   - `govulncheck` findings in the Go 1.26.6 standard library, `x/net` v0.57.0 and, once those were raised, gRPC v1.82.1.

   None of this was in the new package. Skipping the hooks was refused by the session's permission policy. At the user's request, the branch fixed the findings:
   - `toolchain go1.26.10`, `x/net` v0.60.0, gRPC v1.83.1;
   - a rerank `Endpoint` that accepts only unreserved route segments and sets the path on the parsed URL. Escaping inside a loop did not satisfy gosec.

   `make gosec govulncheck lintmax test` then passed.

## 12. Costs and open questions

**Costs of the design:**
- **Provider coverage is narrower than Pi's.** Bedrock, Vertex, Mistral Conversations and Azure models are not served. The Node worker remains available as `--models pi-node` for them.
- **Fewer models listed.** The Go backend lists 43 models, the Node worker 48. Pi's built-in providers can also take keys from their own environment variables (for example `FIREWORKS_API_KEY`), which `HasCredential` does not model. Which five models differ has not been established.
- **Built-in catalog.** Pi's built-in catalog ships inside its npm package. Providers that are neither in `models-store.json` nor in `models.json` are invisible to the Go loader.
- **Static keys in settings.** The Anthropic and Gemini engines accept static keys only through settings. Those settings objects are private to one `Resolved` and are never serialized, but they hold the key.

**Operational risk.** A copy of `auth.json` on a second host holds the same rotating Codex refresh token as the original. Whichever host refreshes first invalidates the other. slop's production notes recommend a separate login per host, or API-key providers on servers.

**Open:**
- **Codex has not been run against chatgpt.com.** The refresh and request paths are tested against fake endpoints only. A live run would rotate the real token in the user's `auth.json`, and is waiting for the user's approval.
- **Release work.** `--models pi` should become the default, and the Node worker should leave the image (SLOP-010 phase 7). geppetto v0.13.12 is released and pinned in slop, so slop's branch builds with `GOWORK=off`, as its Dockerfile does.

## Important project docs

- Ticket: `slop-computer/ttmp/2026/10/29/SLOP-010--model-calls-in-go-geppetto-engines-with-a-pi-agent-dir-loader-replacing-the-node-pi-worker/`
  - design guide: `design-doc/01-intern-guide-sample-on-geppetto-with-pi-credentials.md`;
  - diary: `reference/01-diary.md`, steps 1–7.
- **geppetto:** `pkg/steps/ai/providers/pi/`; PR https://github.com/go-go-golems/geppetto/pull/442; tag `v0.13.12`.
- **slop:**
  - the backend: `pkg/piworker/gepp/` (`backend.go`, `sample.go`);
  - the HTTP side and the interface: `pkg/server/rt_sample.go`, `pkg/piworker/backend.go`;
  - the flag: `cmd/slop/cmds/serve.go` (`--models`);
  - the example: `web/examples/llm-chat/`;
  - the docs: `doc/production.md` ("Models").
- **Related vault notes:**
  - [[PROJECT REPORT - slop Artifact Runtime - Hosting the claude.ai Artifact Contract Natively - A Technical Deep Dive]], which covers the runtime and the Node-worker `sample` this work replaces;
  - [[PROJECT REPORT - Pinup on slop - A Live Design Tool Inside a Versioned Page Server - A Technical Deep Dive]].
