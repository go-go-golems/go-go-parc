---
title: "Porting an Artifact Agent from claude sample() to a Real Agent Protocol"
aliases:
  - sample() to agent protocol
  - artifact agent porting playbook
tags: [article, playbook, llm-agent, artifacts, geppetto]
status: active
type: article
created: 2026-11-19
repo: /home/manuel/code/wesen/2026-11-19--homolog-workbench
---
# Porting an Artifact Agent from claude sample() to a Real Agent Protocol

A claude.ai artifact can host an agent: the page calls `claude.use("sample")`, passes JavaScript functions as tools, and the platform runs a short tool loop on the viewer's Claude account. When such an artifact becomes a self-hosted application, the agent has to move to a service the application controls. This note is the reusable procedure for that move. It records what the `sample()` contract allows, the workarounds artifacts adopt because of it, the session protocol that replaces it, and the order of work.

> [!summary]
> - `sample()` is an agent loop inside one call and memoryless across calls: history is `{role, content: string}` turns, so tool calls and results are lost unless the page writes them into text; there is no system role, a handful of rounds, and no reasoning or usage output.
> - Artifacts compensate with a leading instructions turn, a history window, tool calls folded into assistant text, a state snapshot appended to the last user turn, and result cutting. A port deletes the first three and formalises the last two.
> - The replacement keeps the tools in the page and moves the loop and the conversation to a server: sessions, a tool manifest, turns, an SSE event stream with resume, POSTed tool results, cancel.
> - An application that left claude.ai keeps only the protocol; a host that must still run unmodified artifacts (slop-computer) serves both.

This playbook is for an artifact (a claude.ai page) that has an in-page agent built on the
`sample` runtime capability and is being turned into a self-hosted application with a real
agent. It records what `sample()` can and cannot do, which workarounds artifacts use because of
it, the protocol that replaces it, and the steps of a port. It is written to be reused: the
homolog-bench workbench is the first application ported this way, and its `web/js/agent.js` is
the worked example in section 8.

Sources: the platform spec `Artifact Claude API (sample) — Spec` (runtime contract 0.2.75, written
from `sample.d.ts`, `mcp.d.ts`, `claude.d.ts`; a copy is at `/home/manuel/code/wesen/2026-11-19--homolog-workbench/ttmp/2026/11/19/HB-002--real-agent-service-for-the-workbench-geppetto-pinocchio-agentd-pi-credentials/sources/artifact-claude-api-sample-spec-0.2.75.md`), the
slop-computer re-implementation (`~/code/wesen/go-go-golems/slop-computer`, read at `ad2d739`),
the Form Skate agent design system (`form-skate-agent-design-system.zip`), and the agent-service
design in the homolog-bench ticket HB-002 (`/home/manuel/code/wesen/2026-11-19--homolog-workbench/ttmp/2026/11/19/HB-002--…/design-doc/01-agent-service-design-pinocchio-agentd-with-browser-hosted-tools.md`).

## 1. What sample() is

`sample` is a function a page obtains with `await claude.use("sample")`. One call sends a prompt
(a string, or a list of `{role, content}` turns) and resolves with the whole answer. A call may
carry page tools: JavaScript functions with a name, description and JSON schema. While the call
runs, the platform loops: it asks the model, the model may request tool calls, the page runs them
(`execute(input, {signal})`), the results go back, and the model is asked again, until it answers
or the platform's round limit forces an answer. The model, credentials and billing belong to the
platform; the viewer's own Claude account pays.

Within one call this is an agent loop. Across calls it is not, and that is the central limitation.

## 2. The limits that matter for an agent

Every row is from the spec unless marked. "Consequence" is what an agent built on it must do.

| Limit | Spec wording / value | Consequence for an in-page agent |
|---|---|---|
| No memory between calls | "State: None. Each call is memoryless; the page keeps any chat history itself." | The page re-sends history on every call. |
| History is text only | `input` turns are `{role: "user" \| "assistant", content: string}` | Earlier tool calls and tool results cannot be sent back as such. The model forgets what it ran unless the page writes it into text. |
| Assistant turns are marked | "Assistant turns are labelled to Claude as page-supplied" | Re-sent history is weaker evidence to the model than its own memory would be. |
| No system prompt | "There is no `system` role." Standing instructions go in a leading `user` turn | Instructions compete with conversation text and count against the input limit on every call. |
| Input size | 256 KiB (262,144 UTF-8 bytes) per call | History must be windowed and summarised by the page. |
| Rounds per call | "The platform allows a handful of rounds and forces the last to be an answer." Each round is ~5 min max | Long tasks stop mid-way; the person must say "continue". (slop-computer: 10 rounds, 65,536 output tokens per call.) |
| Tool results | ≤ 32 KB; `ctx.signal` aborts on Stop, when the call settles, or after 150 s | Results must be cut; long tools must be split or made asynchronous. |
| No thinking, no usage | `SampleResult` is `{text, truncated, modelTierApplied, modelApplied?}`; `onText` is "silent while Claude thinks" | No visible reasoning, no token or cost accounting. |
| Model choice | A tier (`quick`/`default`/`complex`) or a model the viewer can pick in chat; silent fallback | No other providers, no pinned model guarantee. |
| Text streaming only | `onText({text, delta})`; text of all rounds joined with blank lines | Tool activity is visible only because the page's own `execute` records it. |
| Consent and availability | First call asks the viewer; `use()` may resolve `null`; many "hide the feature" error codes | The page must work without the agent. |
| Network | The page cannot fetch outside hosts; backends only via the `mcp` capability | Server-side tools need an MCP connector. |
| Errors | `{code, message, text?}`; only `upstream_error` is transient; "never retry from a loop" | Error copy per code; partial text in `e.text`. |
| Caching | identical calls replay for 5 min unless `cache: false`; never with tools | Chat turns must pass `cache: false`. |

## 3. Workarounds artifacts use, and what happens to each in a port

These are the patterns found in homolog-bench (`web/js/agent.js`), the slop-computer lab agent
(`ttmp/…/SLOP3-000…/sources/lab/src/ui/views3.jsx`) and the Form Skate agent (`how-the-agent-works.md`,
`patterns.md`). A port should know which of them it can delete.

| Workaround under sample() | Why it exists | After the port |
|---|---|---|
| Instructions as the first `user` turn, re-sent every call | no system role | **Delete.** Instructions become the session's system prompt, sent once by the server. |
| History window (homolog-bench: last 16 messages; slop lab: last 8, text only) | 256 KiB input, no state | **Delete.** The server keeps full history and compacts it when needed. |
| Tool calls folded into assistant text (homolog-bench: `[I made N eval calls…]`, 300 chars of code and result each, 3,200 chars per message; Form Skate: 160-character fragments) | tool results cannot be re-sent | **Delete.** Tool-call and tool-result blocks stay in the server's history. |
| "Measure again rather than remember" in the instructions | the model loses earlier results | **Relax.** Keep it as a habit for stale state, not as a memory substitute. |
| Live state appended to the last user turn (`[Workbench state right now…]`, Form Skate `[context]`) | no other channel for state | **Keep, formalise.** It becomes the `context` field of a turn; the server attaches it to the latest user block only. |
| Result cutting (homolog-bench 4,000 chars; Form Skate 9,000) | 32 KB limit, re-reading cost | **Keep.** Small results still save tokens; the cut becomes server policy (`resultCut`) so all clients agree. |
| Approval inside `execute` (Ask / Read-only modes) | the platform has no approval concept | **Keep in the page, add protocol support.** Tools declare `mode: auto \| human`; the server marks pending calls; the page shows Run / Decline and reports `denied`. Read-only stays a page guard (editing paths throw). |
| One `AbortController` per call for Stop | cancellation is per call | **Replace** by `POST /cancel` on the session's active run. |
| Off banner when `use()` is null | no model in this view | **Keep** for the fallback path; the real service has its own availability check (`GET /models`). |
| "continue" after the round limit | handful of rounds | **Delete.** Round limits become per-agent configuration (tens of rounds), and the person can stop at any time. |

## 4. The target protocol

The replacement is a session-based agent service. The model loop and the conversation live on the
server; the tools still run in the page, because they act on page state (an editor, a realm,
a canvas). Transport is SSE for server→page events and plain POSTs for page→server actions;
SSE carries the heavy server-to-page stream, resumes with `Last-Event-ID`, passes through a Python reverse proxy as a streamed response, and lets every page action get its own HTTP status (a late tool result gets `409`).

```
POST /v1/sessions                       {agent, model?} → {id, model, limits}
POST /v1/sessions/{id}/tools/manifest   {tools: [{name, description, inputSchema, mode: "auto"|"human"}]}
POST /v1/sessions/{id}/turns            {text, context?} → 202 {turn}
GET  /v1/sessions/{id}/events           SSE; each event has id = seq; Last-Event-ID resumes
POST /v1/sessions/{id}/tools/{callId}/result   {status: "success"|"failed"|"denied", value}
POST /v1/sessions/{id}/cancel
GET  /v1/sessions/{id}                  full history for hydration (turns, blocks, usage)
GET  /v1/models                         model refs and limits, no secrets
```

Event types (names follow geppetto's chat events where one exists):

| Event | Payload | Page reaction |
|---|---|---|
| `run.started` | `{turn}` | show "Thinking" |
| `reasoning.delta` | `{delta}` | optional: show reasoning, folded |
| `text.delta` | `{delta, text}` | assign `text` to the answer bubble |
| `tool.requested` | `{callId, name, input, mode}` | run `execute` (auto) or show Run/Decline (human); POST the result |
| `tool.finished` | `{callId, status, ms}` | mark the step block |
| `usage` | `{input, output, cached, usd?}` | update the cost line |
| `compacted` | `{before, after}` | note that older steps were summarised |
| `run.finished` / `run.failed` / `run.cancelled` | `{turn, truncated?}` / `{code, message}` | idle UI; error copy per code |

Error codes keep the spec's names where the meaning is the same (`cancelled`, `invalid_request`,
`prompt_too_large`, `rate_limited`, `refused`, `empty_completion`, `upstream_error`) and add
`authentication_error` (server credential), `quota_exceeded` (budget) and `tool_timeout`.

## 5. Concept mapping

| sample() | Agent protocol |
|---|---|
| `await claude.use("sample")` | `GET /v1/models` succeeds → service available |
| one `sample(input, {tools})` call | one turn: `POST /turns`, events until `run.finished` |
| leading `user` instructions turn | agent config `systemPrompt` (server file) |
| re-sent `turns` array | server-side session history |
| text appended to last user turn | `context` field of `POST /turns` |
| `options.tools[].execute` | unchanged page function, invoked on `tool.requested` |
| `options.tools[]` metadata | `POST /tools/manifest` once per session (and after reload) |
| `onText({text, delta})` | `text.delta` event |
| `signal` / AbortController | `POST /cancel` |
| `modelTier` / `model` | session `model` ref (`pi:lunaroute/glm-5.3`, `profile:claude`) |
| `SampleResult.truncated` | `run.finished.truncated` |
| `SampleError {code, message, text}` | `run.failed {code, message}` + text already streamed |
| `sample.limits()` | `limits` in the session response |
| viewer's Claude account | operator credentials (Pi agent dir or pinocchio profile) + per-session budget |

## 6. Porting procedure

1. **Inventory the artifact's sample use.** Find every `claude.use("sample")`, every `sample(` /
   `sample.json(` call, the tools passed, the history builder, the instructions text, the state
   snapshot, the error-copy table and any approval logic. Write them down; each maps to a row in §5.
2. **Move the instructions to an agent config.** Create `configs/agent/<app>.yaml` with
   `systemPrompt: <file>.md`, default model, round limit, result cut, tool timeout and per-tool
   approval mode. Remove the "you will not remember" style instructions and any text that only
   existed to describe the history format.
3. **Turn the tools into a manifest.** Keep `execute` functions in the page unchanged. Send
   `{name, description, inputSchema, mode}` once per session. Keep tool descriptions about what the
   tool returns; they are still all the model sees of the code.
4. **Delete the history builder.** The page no longer windows or summarises; it sends only the new
   user text and the current context snapshot.
5. **Replace the call with a turn.** `POST /turns`, then consume SSE: `text.delta` → answer,
   `tool.requested` → `execute` → `POST /result`, `run.*` → idle. Keep one SSE stream per tab,
   with events for all of the tab's sessions.
6. **Map errors.** Reuse the artifact's error copy for the shared codes; add copy for
   `authentication_error`, `quota_exceeded`, `tool_timeout`.
7. **Keep approval in the page.** Auto runs `execute` immediately; Ask (`mode: human`) shows the
   step with Run / Decline and posts `denied` on Decline; Read-only makes editing paths throw so the
   model receives an error it can report.
8. **Decide whether the sample path stays.** An application that no longer runs inside claude.ai
   (homolog-bench) removes it and keeps only the protocol. A host that must still run unmodified
   artifacts (slop-computer) serves both: the artifact contract for `claude.use("sample")` and the
   agent protocol for ported apps, over one model source and one budget. If a page keeps both, detect
   the service first, then `claude.use("sample")`, then show the off banner, and render the same step
   blocks on both paths.
9. **Test with a scripted engine.** The service must accept a fake engine that emits a fixed
   sequence (text, a tool request, a final answer). Drive the page with Playwright: send a turn,
   see the tool run in the page, see the answer, reload mid-run and see the stream resume, press
   Stop and see `run.cancelled`.
10. **Then test models.** Run a fixed set of the application's tasks against each candidate model
    and record rounds, tokens, cost and whether the task succeeded.

## 7. Semantics that change, and the risks they bring

- **The model now remembers its tool results.** Answers can cite earlier measurements, which is
  the point, but stale results can also be trusted after the page state changed. Keep the context
  snapshot on every turn and keep "re-measure after changes" in the instructions.
- **Cost moves from the viewer to the operator.** Budgets, per-session limits and usage display
  become necessary; under sample() the platform enforced them.
- **Credentials live on the server.** The service must bind to localhost or sit behind the
  application's own auth, and must never echo credentials (geppetto's sealed connections help).
- **Page data can steer tool calls.** This is unchanged from sample(): text in tool results is
  input to the model. Destructive actions stay behind confirmation or undo.
- **Longer runs.** With tens of rounds, a run can do much more before the person sees it. Show
  steps as they happen and keep Stop visible.
- **Two backends, one UI.** The fallback path and the protocol path must render the same step
  blocks; otherwise behaviour diverges silently.

## 8. Worked example: homolog-bench `web/js/agent.js` (state before the port)

| Element | Current code | Port |
|---|---|---|
| availability | `G.claude.use('sample')`, `sample.limits()` (`agent.js:24-35`) | replace with `GET /v1/models` (protocol only; sample path removed) |
| instructions | `rules()` as first user turn (`agent.js:109`) | `configs/agent/homolog-bench.yaml` + `system-prompt.md` |
| history | last 16 messages; eval calls summarised to 300 chars, 3,200 per message (`agent.js:100-117`) | delete (server history) |
| state | `snapshot()` appended to last user turn (`agent.js:116`) | `context` field |
| tool | one tool `eval`, result cut to 4,000 chars, errors thrown (`agent.js:121-142`) | manifest entry, `mode: auto`; later add `files.*`, `run_preset`, `jobs` |
| streaming | `onText` → `msg.text` (`agent.js:172`) | `text.delta` |
| errors | `ERR` table (`agent.js:149-160`) | reuse + new codes |
| tier | `#tier` select → `modelTier` | model select from `GET /v1/models` |

## 9. Checklist

- [ ] Inventory written (§6.1)
- [ ] Agent config and system prompt file in the application repo
- [ ] Tool manifest; `execute` unchanged
- [ ] History builder removed from the protocol path
- [ ] SSE consumer with resume (`Last-Event-ID`) and one stream per tab
- [ ] Error copy for all codes
- [ ] Approval modes (Auto / Ask / Read-only)
- [ ] Decided: protocol only (application) or both (host such as slop-computer)
- [ ] Playwright test against the scripted engine (turn, tool, reload-resume, Stop)
- [ ] Model comparison on the application's own tasks


## Related notes

- [[PROJECT REPORT - homolog-bench - From a Simulated Workbench to Real Homolog Search on the DGX Spark - A Technical Deep Dive]] — the application whose agent is the first port.
