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

## Turn 2 - assistant (thinking)

- Message ID: `8f7b2e6e-f57c-4a8d-b48a-ea1a5120a2a7`
- Model: `gpt-5-6-pro`

<details><summary>Thinking</summary>

**Considering repo metadata**

I’m thinking about fetching repo data and README files. A web search for keywords like “widget” or “dsl” could help, but I’m also considering cloning and inspecting files directly.

**Considered repo metadata**


</details>

## Turn 3 - assistant (tool call)

- Message ID: `f208265e-5681-4e63-b49a-ccfd82cd4a7a`
- Model: `gpt-5-6-pro`

```json
{"open":[{"ref_id":"https://parc.yolo.scapegoat.dev/note/research/kb/projects/widget-dsl"},{"ref_id":"https://parc.yolo.scapegoat.dev/note/research/kb/projects/go-go-goja"},{"ref_id":"https://parc.yolo.scapegoat.dev/note/research/kb/projects/geppetto"},{"ref_id":"https://parc.yolo.scapegoat.dev/note/research/kb/projects/sessionstream"},{"ref_id":"https://github.com/go-go-golems/rag-evaluation-system"},{"ref_id":"https://github.com/go-go-golems/go-go-goja"},{"ref_id":"https://github.com/go-go-golems/geppetto"},{"ref_id":"https://github.com/go-go-golems/sessionstream"},{"ref_id":"https://github.com
```

## Turn 4 - assistant (thinking)

- Message ID: `cff5e05c-fab0-4c6e-8023-8b50cafbeb5c`

<details><summary>Thinking</summary>

**Searched the web and GitHub**


</details>

## Turn 5 - assistant (tool call)

- Message ID: `46176ec9-09e5-4952-ab61-f6f46b181c78`
- Model: `gpt-5-6-pro`

```unknown
bash -lc set -euo pipefail
mkdir -p /mnt/data/research-repos
cd /mnt/data/research-repos
for repo in rag-evaluation-system go-go-goja geppetto sessionstream react-chat; do
  if [ ! -d "$repo/.git" ]; then
    git clone --filter=blob:none --no-checkout "https://github.com/go-go-golems/$repo.git" "$repo" || echo "CLONE_FAILED:$repo"
  fi
done
for repo in rag-evaluation-system go-go-goja geppetto sessionstream react-chat; do
  if [ -d "$repo/.git" ]; then
    cd "$repo"
    git sparse-checkout init --cone >/dev/null 2>&1 || true
    git sparse-checkout set . >/dev/null 2>&1 || true
    git checkout -f >/dev/null 2>&1 || true
    echo "=== $repo ==="
    git rev-parse --abbrev-ref HEAD
    git rev-parse HEAD
    git log -1 --format='%cI %s'
    cd ..
  fi
done
```

## Turn 6 - assistant (thinking)

- Message ID: `3141df17-5dda-49a7-91c8-4c59485cd4db`

<details><summary>Thinking</summary>

**Cloned and inspected repositories in container**


</details>

## Turn 7 - assistant (thinking)

- Message ID: `3b37f3a6-88d2-40fe-a94f-f03dfe8fc2eb`

<details><summary>Thinking</summary>

**Inspected GitHub repository for widget DSL and component references**


</details>

## Turn 8 - assistant (tool call)

- Message ID: `834921cc-839e-4237-8873-a1c0b1a5c7aa`
- Model: `gpt-5-6-pro`

```json
{"search_query":[{"q":"site:parc.yolo.scapegoat.dev/note/research/kb/projects/widget-dsl widget dsl"},{"q":"site:parc.yolo.scapegoat.dev/note/research/kb/projects/go-go-goja go-go-goja"},{"q":"site:parc.yolo.scapegoat.dev/note/research/kb/projects/geppetto geppetto"},{"q":"site:parc.yolo.scapegoat.dev/note/research/kb/projects/sessionstream sessionstream"}],"response_length":"long"}
```

## Turn 9 - assistant (thinking)

- Message ID: `11d0ea90-4c01-4bb9-ac76-1e2911ad33b8`

<details><summary>Thinking</summary>

**Searched multiple sites for project information and related tools**


</details>

## Turn 10 - assistant (thinking)

- Message ID: `1d29e4fd-6810-4b10-9b9c-33a36bd17135`

<details><summary>Thinking</summary>

**Searched GitHub repositories and fetched relevant file contents**


</details>

## Turn 11 - assistant (thinking)

- Message ID: `bb39a77d-5142-4b4f-98b6-2439f2db6d3e`
- Model: `gpt-5-6-pro`

<details><summary>Thinking</summary>

**Planning report creation**

I’m outlining the report process, considering creating a detailed markdown file with a summary and citations. I’ll map repositories and review the relevant code before generating the artifact.

**Planned report creation**


</details>

## Turn 12 - assistant

- Message ID: `56e006d5-664f-481e-b6b2-3c8d1418fd1d`
- Model: `gpt-5-6-pro`

Goja’s runtime ownership, event-loop scheduling, scoped async callbacks, and EventEmitter appear promising for streaming state; meanwhile, I’m reconstructing inaccessible PARC material from repository documentation.

## Turn 13 - assistant (thinking)

- Message ID: `aea33bf6-b3b3-4ebc-87e0-8ce2960f4a60`

<details><summary>Thinking</summary>

**Fetched project notes, metadata, and files for report creation**


</details>

## Turn 14 - assistant (thinking)

- Message ID: `c42dd5a1-b7ff-4ca8-b35d-94081b03b8ae`

<details><summary>Thinking</summary>

**Inspected files and searched repository for widget and WebSocket related terms**


</details>

## Turn 15 - assistant (thinking)

- Message ID: `185254dd-6e23-435d-a717-25b02ed3510f`

<details><summary>Thinking</summary>

**Searched and fetched files, inspected actions and schemas**


</details>

## Turn 16 - assistant (thinking)

- Message ID: `3c83400c-9ec3-4ee8-b4e8-64abf9bab0e0`

<details><summary>Thinking</summary>

**Fetched documents and inspected widgetsite integration and architecture**


</details>

## Turn 17 - assistant (thinking)

- Message ID: `a0057bbb-4cc5-4f14-9076-38135b729ce0`
- Model: `gpt-5-6-pro`

<details><summary>Thinking</summary>

**Crafting developer report**

I’m analyzing GitHub repos and project notes to generate a detailed report on extending the Widget DSL/IR renderer for chatbot support. It’ll include options, mechanics, recommendations, and diagrams.

**Crafted developer report**


</details>

## Turn 18 - assistant (thinking)

- Message ID: `75bb573b-1df8-484b-89a4-cb548056e315`

<details><summary>Thinking</summary>

**Fetched metadata, documentation, and searched code in GitHub repositories**


</details>

## Turn 19 - assistant (tool call)

- Message ID: `93289556-7a49-490e-984a-6e3df5a7f8f9`
- Model: `gpt-5-6-pro`

```unknown
bash -lc mkdir -p /mnt/data/research-src && cd /mnt/data/research-src && for r in rag-evaluation-system go-go-goja geppetto sessionstream react-chat go-go-parc; do if [ ! -d "$r/.git" ]; then git clone --depth 1 https://github.com/go-go-golems/$r.git; fi; done
```

## Turn 20 - assistant (thinking)

- Message ID: `260b1a5b-fc03-4d4b-834b-3573481032e6`

<details><summary>Thinking</summary>

**Cloned repositories with validation**


</details>

## Turn 21 - assistant (thinking)

- Message ID: `cac01e8b-bbfa-4fc4-9ec7-2a3dac936de8`

<details><summary>Thinking</summary>

**Fetched file content and searched for module and package paths**


</details>

## Turn 22 - assistant (tool call)

- Message ID: `d8b30c6a-f4b3-49b6-88ce-d170b81aa1fc`
- Model: `gpt-5-6-pro`

```json
{"open":[{"ref_id":"https://api.github.com/repos/go-go-golems/sessionstream/git/trees/main?recursive=1"}],"response_length":"long"}
```

## Turn 23 - assistant (thinking)

- Message ID: `44ccd24e-cbf6-4a0d-a413-67d825caecca`

<details><summary>Thinking</summary>

**Searched the web and GitHub for sessionstream terms**


</details>

## Turn 24 - assistant (tool call)

- Message ID: `cef37523-cf57-4606-abc3-047f9386bd1b`
- Model: `gpt-5-6-pro`

```unknown
bash -lc ls -la /mnt/data/research-src
```

## Turn 25 - assistant

- Message ID: `963431d4-a110-45c7-b3e4-9f473b1915b3`
- Model: `gpt-5-6-pro`

The likely design is a generic live-resource adapter: Widget DSL declares typed chat intent, React handles browser state, and SessionStream provides snapshot-first durable events. Schema/version/action validation remains the key gap.

## Turn 26 - assistant (thinking)

- Message ID: `eac5e793-6e3c-426a-bd3f-bf0b7973e2ef`

<details><summary>Thinking</summary>

**Listed directory contents**


</details>

## Turn 27 - assistant (thinking)

- Message ID: `50898cb9-ec99-4f9b-a529-e0172dae12aa`

<details><summary>Thinking</summary>

**Searched and fetched files and reports from GitHub repository**


</details>

## Turn 28 - assistant (tool call)

- Message ID: `95c7d5a7-82e5-43a8-b36c-a0514a562fab`
- Model: `gpt-5-6-pro`

```unknown
bash -lc true
```

## Turn 29 - assistant (thinking)

- Message ID: `34d60527-54a7-4c3b-8bfb-5838854ecf77`

<details><summary>Thinking</summary>

**Searched resource for key terms**


</details>

## Turn 30 - assistant (thinking)

- Message ID: `657166c8-06db-4da5-b1ee-2dcb914d4545`

<details><summary>Thinking</summary>

**Fetched report content from specified lines and onwards**


</details>

## Turn 31 - assistant (thinking)

- Message ID: `2060f492-f9f2-4a8b-a8d4-2836aa199b9a`

<details><summary>Thinking</summary>

**Inspected React Chat setup and fetched repository files**


</details>

## Turn 32 - assistant (thinking)

- Message ID: `b20e74ab-26a2-4f44-b2b6-ce63d422a459`

<details><summary>Thinking</summary>

**Fetched and inspected documents and repository files for details**


</details>

## Turn 33 - assistant (thinking)

- Message ID: `fd3cd329-f9f9-4bbd-96aa-00369354ff92`
- Model: `gpt-5-6-pro`

<details><summary>Thinking</summary>

**Reviewing architecture and reports**

I’m analyzing frontend tools, widgets, and sessionstream architecture. The reports offer insights into typed instances, versioning, actions, and event normalization, along with frontend/backend integration details.


</details>

## Turn 34 - assistant (thinking)

- Message ID: `a4c517b4-b9d1-401b-ba15-635107b19a5c`

<details><summary>Thinking</summary>

**Inspected files, fetched content, and evaluated widget integration**


</details>

## Turn 35 - assistant (tool call)

- Message ID: `a4d6db2e-4fac-437b-8b79-092a3db5f09f`
- Model: `gpt-5-6-pro`

```json
{"search_query":[{"q":"WHATWG EventSource constructor withCredentials custom headers specification"},{"q":"MDN EventSource constructor options withCredentials headers"}],"response_length":"short"}
```

## Turn 36 - assistant (thinking)

- Message ID: `738aa4da-7320-4dfd-a36a-eb69a50cf727`

<details><summary>Thinking</summary>

**Searched multiple sources for EventSource custom header specifications**


</details>

## Turn 37 - assistant (tool call)

- Message ID: `c8841e45-83d6-43e5-ada8-9ffb524ca3ac`
- Model: `gpt-5-6-pro`

```unknown
from pathlib import Path

report_path = Path("/mnt/data/widget-dsl-streaming-chat-architecture-report.md")

part1 = r'''# Widget DSL Streaming Chat and Embedded Widget Architecture

**Status:** Architecture analysis and implementation design  
**Audience:** New developers joining the Widget DSL, `react-chat`, `sessionstream`, Geppetto, or Goja work  
**Reviewed:** 2026-07-20  
**Primary recommendation:** Add chat as a normal Widget IR component, use `react-chat` as the browser runtime, use `sessionstream` as durable session state, and render streamed embedded widgets by recursively invoking the existing Widget IR renderer.

---

## Executive summary
```

## Turn 38 - assistant (thinking)

- Message ID: `eaf343cc-66ff-41cc-852c-171c4434a825`

<details><summary>Thinking</summary>

**Generated widget DSL streaming chat architecture report**


</details>

## Turn 39 - assistant (tool call)

- Message ID: `bdb71a15-b028-4c33-be57-a7f80c98e94a`
- Model: `gpt-5-6-pro`

```unknown
bash -lc wc -l -w -c /mnt/data/widget-dsl-streaming-chat-architecture-report.md && sed -n '1,40p' /mnt/data/widget-dsl-streaming-chat-architecture-report.md && tail -n 30 /mnt/data/widget-dsl-streaming-chat-architecture-report.md
```

## Turn 40 - assistant (thinking)

- Message ID: `09f1e7ed-0bd7-4192-9fe8-80921e94655c`

<details><summary>Thinking</summary>

**Verified report file and contents**


</details>

## Turn 41 - assistant (tool call)

- Message ID: `c24778da-8e75-45f2-860f-5049c5706abb`
- Model: `gpt-5-6-pro`

```json
{"paths":["GitHub"],"query":"repository"}
```

## Turn 42 - assistant (tool call)

- Message ID: `2e5084e4-cd3d-4f7c-94ab-69b3a9ecf298`
- Model: `gpt-5-6-pro`

```json
{"paths":["GitHub"],"query":"tree"}
```

## Turn 43 - assistant (tool call)

- Message ID: `84b56535-2ec3-43f1-b8c2-c84e813a9896`
- Model: `gpt-5-6-pro`

```json
{"paths":["GitHub"],"query":"contents"}
```

## Turn 44 - assistant (tool call)

- Message ID: `25d3abba-2f0e-4ad1-80d5-734304b77419`
- Model: `gpt-5-6-pro`

```json
{"paths":["GitHub"],"query":"tree"}
```

## Turn 45 - assistant (recap)

- Message ID: `98da2012-fa79-56cb-80b6-d4e756d2ca83`

> _Worked for 40m 24s_

## Turn 46 - assistant

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

