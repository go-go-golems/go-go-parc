# Widget DSL Extension Design

- URL: https://chatgpt.com/c/6a5e891a-5b18-83ea-b26b-8259c18fb307
- Created: 2026-07-20T20:46:18.942Z

---

> look at github.com/go-go-golems/rag-evaluation-system's widget DSL, and https://parc.yolo.scapegoat.dev/note/research/kb/projects/widget-dsl (and its links to project reports) and then also https://parc.yolo.scapegoat.dev/note/research/kb/projects/go-go-goja and github.com/go-go-golems/go-go-goja (its event emitter, http framework, for example), and https://parc.yolo.scapegoat.dev/note/research/kb/projects/geppetto and https://parc.yolo.scapegoat.dev/note/research/kb/projects/sessionstream (and their github repos).
>
> And github.com/go-go-golems/react-chat/
>
> What I want to do is extend widget.dsl to be able to have streaming SSE/websocket chat bot widgets with embeddable widgets too, integrated into the current widget.dsl / IR renderer approach. 
>
> Analyze, brainstorm, design, make a full report that explains everything to a new developer to the team and what different things are we could do and how they all work and such.

I’ll trace the Widget DSL/IR pipeline and related transport/session projects, then compare streaming-chat integration architectures and deliver a developer-facing design report with an implementation roadmap.

<details><summary>💭 Thinking</summary>

**Considering repo metadata**

I’m thinking about fetching repo data and README files. A web search for keywords like “widget” or “dsl” could help, but I’m also considering cloning and inspecting files directly.

**Considered repo metadata**

</details>

```json
{"open":[{"ref_id":"https://parc.yolo.scapegoat.dev/note/research/kb/projects/widget-dsl"},{"ref_id":"https://parc.yolo.scapegoat.dev/note/research/kb/projects/go-go-goja"},{"ref_id":"https://parc.yolo.scapegoat.dev/note/research/kb/projects/geppetto"},{"ref_id":"https://parc.yolo.scapegoat.dev/note/research/kb/projects/sessionstream"},{"ref_id":"https://github.com/go-go-golems/rag-evaluation-system"},{"ref_id":"https://github.com/go-go-golems/go-go-goja"},{"ref_id":"https://github.com/go-go-golems/geppetto"},{"ref_id":"https://github.com/go-go-golems/sessionstream"},{"ref_id":"https://github.com
```

<details><summary>💭 Thinking</summary>

**Searched the web and GitHub**

</details>

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

<details><summary>💭 Thinking</summary>

**Cloned and inspected repositories in container**

</details>

<details><summary>💭 Thinking</summary>

**Inspected GitHub repository for widget DSL and component references**

</details>

```json
{"search_query":[{"q":"site:parc.yolo.scapegoat.dev/note/research/kb/projects/widget-dsl widget dsl"},{"q":"site:parc.yolo.scapegoat.dev/note/research/kb/projects/go-go-goja go-go-goja"},{"q":"site:parc.yolo.scapegoat.dev/note/research/kb/projects/geppetto geppetto"},{"q":"site:parc.yolo.scapegoat.dev/note/research/kb/projects/sessionstream sessionstream"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched multiple sites for project information and related tools**

</details>

<details><summary>💭 Thinking</summary>

**Searched GitHub repositories and fetched relevant file contents**

</details>

<details><summary>💭 Thinking</summary>

**Planning report creation**

I’m outlining the report process, considering creating a detailed markdown file with a summary and citations. I’ll map repositories and review the relevant code before generating the artifact.

**Planned report creation**

</details>

Goja’s runtime ownership, event-loop scheduling, scoped async callbacks, and EventEmitter appear promising for streaming state; meanwhile, I’m reconstructing inaccessible PARC material from repository documentation.

<details><summary>💭 Thinking</summary>

**Fetched project notes, metadata, and files for report creation**

</details>

<details><summary>💭 Thinking</summary>

**Inspected files and searched repository for widget and WebSocket related terms**

</details>

<details><summary>💭 Thinking</summary>

**Searched and fetched files, inspected actions and schemas**

</details>

<details><summary>💭 Thinking</summary>

**Fetched documents and inspected widgetsite integration and architecture**

</details>

<details><summary>💭 Thinking</summary>

**Crafting developer report**

I’m analyzing GitHub repos and project notes to generate a detailed report on extending the Widget DSL/IR renderer for chatbot support. It’ll include options, mechanics, recommendations, and diagrams.

**Crafted developer report**

</details>

<details><summary>💭 Thinking</summary>

**Fetched metadata, documentation, and searched code in GitHub repositories**

</details>

```unknown
bash -lc mkdir -p /mnt/data/research-src && cd /mnt/data/research-src && for r in rag-evaluation-system go-go-goja geppetto sessionstream react-chat go-go-parc; do if [ ! -d "$r/.git" ]; then git clone --depth 1 https://github.com/go-go-golems/$r.git; fi; done
```

<details><summary>💭 Thinking</summary>

**Cloned repositories with validation**

</details>

<details><summary>💭 Thinking</summary>

**Fetched file content and searched for module and package paths**

</details>

```json
{"open":[{"ref_id":"https://api.github.com/repos/go-go-golems/sessionstream/git/trees/main?recursive=1"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched the web and GitHub for sessionstream terms**

</details>

```unknown
bash -lc ls -la /mnt/data/research-src
```

The likely design is a generic live-resource adapter: Widget DSL declares typed chat intent, React handles browser state, and SessionStream provides snapshot-first durable events. Schema/version/action validation remains the key gap.

<details><summary>💭 Thinking</summary>

**Listed directory contents**

</details>

<details><summary>💭 Thinking</summary>

**Searched and fetched files and reports from GitHub repository**

</details>

```unknown
bash -lc true
```

<details><summary>💭 Thinking</summary>

**Searched resource for key terms**

</details>

<details><summary>💭 Thinking</summary>

**Fetched report content from specified lines and onwards**

</details>

<details><summary>💭 Thinking</summary>

**Inspected React Chat setup and fetched repository files**

</details>

<details><summary>💭 Thinking</summary>

**Fetched and inspected documents and repository files for details**

</details>

<details><summary>💭 Thinking</summary>

**Reviewing architecture and reports**

I’m analyzing frontend tools, widgets, and sessionstream architecture. The reports offer insights into typed instances, versioning, actions, and event normalization, along with frontend/backend integration details.

</details>

<details><summary>💭 Thinking</summary>

**Inspected files, fetched content, and evaluated widget integration**

</details>

```json
{"search_query":[{"q":"WHATWG EventSource constructor withCredentials custom headers specification"},{"q":"MDN EventSource constructor options withCredentials headers"}],"response_length":"short"}
```

<details><summary>💭 Thinking</summary>

**Searched multiple sources for EventSource custom header specifications**

</details>

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

<details><summary>💭 Thinking</summary>

**Generated widget DSL streaming chat architecture report**

</details>

```unknown
bash -lc wc -l -w -c /mnt/data/widget-dsl-streaming-chat-architecture-report.md && sed -n '1,40p' /mnt/data/widget-dsl-streaming-chat-architecture-report.md && tail -n 30 /mnt/data/widget-dsl-streaming-chat-architecture-report.md
```

<details><summary>💭 Thinking</summary>

**Verified report file and contents**

</details>

```json
{"paths":["GitHub"],"query":"repository"}
```

```json
{"paths":["GitHub"],"query":"tree"}
```

```json
{"paths":["GitHub"],"query":"contents"}
```

```json
{"paths":["GitHub"],"query":"tree"}
```

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

