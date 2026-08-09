# Workflow Builder Design

- URL: https://chatgpt.com/c/6a686e68-986c-83ea-b7f8-e4717c576fa0
- Created: 2026-07-28T08:55:05.360Z

---

> Look at github.com/go-go-golems/scraper  and https://parc.yolo.scapegoat.dev/note/research/kb/projects/scraper (and links) and do a deep dive analysis of the codebase, which I think might be a bit overengineered, and design a clean pragmatic workflow builder and executing framework that can easily be reused both as a go package and as a goja JS exposed library.
>
> Output a detailed extensive design and implementation guide, with all the concepts and architecture and context explained in a textbook style for a new developer joining th eproject who w  ill have to implement it (It should be a fresh from scratch design).

<details><summary>💭 Thinking</summary>

**Planning the research**

I’m going to inspect the repository, study the linked execution concepts, compare them with practical workflow-engine patterns, and then design a fresh Go core with JavaScript bindings.

**Planned the research**

</details>

I’ll inspect the repository, tests, examples, and linked research to pinpoint complexity, then design a pragmatic replacement with Go/Goja APIs, execution semantics, migration guidance, and implementation phases.

<details><summary>💭 Thinking</summary>

**Inspected go-go-golems/scraper repository**

</details>

```json
{"open":[{"ref_id":"https://parc.yolo.scapegoat.dev/note/research/kb/projects/scraper"},{"ref_id":"https://github.com/go-go-golems/scraper"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

**Fetched latest scraper repository commit**

</details>

```unknown
bash -lc rm -rf /mnt/data/scraper-repo && git clone --depth 1 https://github.com/go-go-golems/scraper.git /mnt/data/scraper-repo && cd /mnt/data/scraper-repo && git rev-parse HEAD && find . -maxdepth 3 -type f | sort | sed 's#^./##' | head -400
```

<details><summary>💭 Thinking</summary>

**Cloned and inspected scraper repository**

</details>

```json
{"open":[{"ref_id":"https://api.github.com/repos/go-go-golems/scraper/git/trees/main?recursive=1"},{"ref_id":"https://api.github.com/repos/go-go-golems/scraper/commits/main"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searching the web**

**Mapping repository structure**

I’m identifying the project’s main packages, execution types, storage layers, and bindings first. Then I’ll trace how workflows move from definition to runtime so the redesign addresses actual seams rather than assumptions.

**Mapped repository structure**

**Searched scraper repositories and fetched source files for Goja references**

</details>

```json
{"search_query":[{"q":"site:github.com/go-go-golems/scraper/tree/main/pkg/engine"},{"q":"site:github.com/go-go-golems/scraper/blob/main/pkg/engine scraper"},{"q":"site:github.com/go-go-golems/scraper/blob/main/pkg/js/runtime goja"},{"q":"site:github.com/go-go-golems/scraper/blob/main/pkg/sites/manifest"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

```json
{"open":[{"ref_id":"https://r.jina.ai/http://parc.yolo.scapegoat.dev/note/research/kb/projects/scraper"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searching ai-tldr.dev**

</details>

```unknown
bash -lc ls -l /mnt/data | sed -n '1,80p'; test -f /mnt/data/parc_scraper.html && wc -c /mnt/data/parc_scraper.html || true
```

<details><summary>💭 Thinking</summary>

**Checked downloaded file status**

</details>

The core issue is coupling durable orchestration to scraper-specific bootstrapping, storage, command generation, and Goja hosting; I’ll preserve durability as an optional layer.

The target is a restartable, auditable extraction pipeline, not a generic distributed platform. JavaScript should emit a validated data-only plan, never retaining Goja objects or runtime state.

```json
{"open":[{"ref_id":"https://github.com/go-go-golems/scraper/archive/refs/heads/main.zip"}],"response_length":"short"}
```

<details><summary>💭 Thinking</summary>

**Searching the web**

**Exploring repository access**

The repository view isn’t exposing every file directly, so I’m adjusting my approach: I’m using indexed source references and known project paths to reconstruct the architecture without relying on hidden implementation details.

**Explored repository access possibilities**

**Investigated GitHub repository fetch failures**

</details>

```json
{"open":[{"ref_id":"https://github.com/search?q=repo%3Ago-go-golems%2Fscraper+goja&type=code"},{"ref_id":"https://github.com/search?q=repo%3Ago-go-golems%2Fscraper+package+engine&type=code"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searching the web**

</details>

```json
{"search_query":[{"q":"\"Retro Obsidian Publish\" GitHub"},{"q":"\"Retro Obsidian Publish\" API note route"},{"q":"site:github.com \"Retro Obsidian Publish\""},{"q":"\"parc.yolo.scapegoat.dev\""}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 13 websites**

</details>

```json
{"open":[{"ref_id":"turn178127search0"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

**Compared repository history and changes from initial to latest commits**

**Reviewed scraper architecture, workflow APIs, runtime code, and execution context implementations**

**Assessing the project**

I’m tracing the repository’s workflow layers, persistence model, scheduler, runtime adapters, JavaScript integration, and newer facade packages. I’ll separate essential capabilities from infrastructure that can be simplified in a fresh design.

**Assessed the project**

</details>

```unknown
bash -lc rm -rf /tmp/scraper && git clone --depth=1 https://github.com/go-go-golems/scraper.git /tmp/scraper && cd /tmp/scraper && git rev-parse HEAD && find . -maxdepth 3 -type f | sort | sed -n '1,240p'
```

<details><summary>💭 Thinking</summary>

**Cloned and inspected the scraper repository**

**Reviewing Generic Scraper Engine Design**

**Continued scraper and scheduler design review, inspecting models and interfaces**

**Reviewing Goja Runner Promise Handling**

</details>

```json
{"search_query":[{"q":"site:github.com/dop251/goja README goroutine safe Runtime Interrupt Promise"},{"q":"site:pkg.go.dev/github.com/dop251/goja Runtime Interrupt Promise documentation"},{"q":"site:github.com/dop251/goja_nodejs eventloop README goja promise async"},{"q":"site:go.dev/ref/spec type parameters methods generic methods Go 1.26"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 2 websites**

**Inspected workflow runtime APIs, site registry, and submit verb coupling**

**Assessing current architecture**

I’m weighing the existing workflow facade, scheduler, SQLite store, operator services, projections, artifacts, and Goja bridge. The redesign will preserve proven execution semantics while removing duplicated boundaries, implicit coupling, and leaky engine internals.

**Assessed current architecture**

</details>

```json
{"open":[{"ref_id":"https://parc.yolo.scapegoat.dev/note/research/kb/projects/scraper"},{"ref_id":"https://github.com/go-go-golems/scraper"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

**Inspected artifact and projection stores, errors, HTTP runner, and templating security**

</details>

```json
{"open":[{"ref_id":"https://pkg.go.dev/github.com/dop251/goja"},{"ref_id":"https://pkg.go.dev/github.com/dop251/goja_nodejs/require"},{"ref_id":"https://pkg.go.dev/github.com/dop251/goja_nodejs/eventloop"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

```unknown
from pathlib import Path
out = Path("/mnt/data/scraper_workflow_framework_design.md")

parts = []

parts.append(r"""# A Clean Workflow Builder and Execution Framework for Go and Goja

## Deep codebase analysis, fresh architecture, and implementation guide

**Project examined:** `go-go-golems/scraper`  
**Research context examined:** the scraper research note mirrored in the repository under `ttmp/2026/03/23/SCRAPER-DESIGN--initial-design-for-generic-go-scraper-engine-with-embedded-javascript-and-nereval-port/`, its design document, investigation material, current embedded documentation, representative
```

<details><summary>💭 Thinking</summary>

**Built a Go and Goja workflow framework**

</details>

```unknown
from pathlib import Path
out = Path("/mnt/data/scraper_workflow_framework_design.md")
appendix = r"""

---

# Part XXX — File-by-file implementation walkthrough

This section turns the architecture into an implementation sequence. It is intentionally concrete. A new developer should be able to create the files in this order and keep the module compiling after each group.

## 168. `id.go`

Define opaque string types:

```go
type RunID string
type StepID string
type AttemptID string
type StepKey string
type QueueName string
```

Do not expose assumptions about UUID versus ULID format.

Interfaces:

```go
type IDGenerator interface {
    RunID() RunID
    StepID() Step
```

<details><summary>💭 Thinking</summary>

**Expanded the framework implementation and review guide**

</details>

```unknown
bash -lc wc -l -w -c /mnt/data/scraper_workflow_framework_design.md && sed -n '1,80p' /mnt/data/scraper_workflow_framework_design.md && tail -80 /mnt/data/scraper_workflow_framework_design.md
```

<details><summary>💭 Thinking</summary>

**Verified Markdown file structure and headings**

</details>

```unknown
from pathlib import Path
p = Path("/mnt/data/scraper_workflow_framework_design.md")
s = p.read_text(encoding="utf-8")
needle = "---\n\n## How to read this document"
toc = """---

## Contents

1. **Assessment and current system** — Parts I–IV  
   Executive verdict, historical intent, current layers, useful mechanisms, and the detailed overengineering/correctness findings.

2. **Fresh semantic design** — Parts V–VIII  
   Goals, non-goals, design laws, canonical nouns, state machines, invariants, identifiers, JSON, hashes, and graph validation.

3. **Public Go API** — Part IX  
   Raw interfaces, typed definitions and activities, builder, catalog, client, runtime convenience, and examples
```

<details><summary>💭 Thinking</summary>

**Updated scraper framework design document contents**

</details>

```json
{"paths":["GitHub"],"query":"repository"}
```

```json
{"uri":"/response/turn2","query":"diff --git"}
```

```json
{"uri":"/response/turn2","query":"pkg/engine"}
```

```json
{"uri":"/response/turn2","query":"newStepContext"}
```

```json
{"paths":["files","Dropbox"],"query":"search"}
```

```json
{"uri":"/response/turn10","start_line":1,"num_lines":100}
```

# Deliverable

[Download the complete design and implementation guide](sandbox:/mnt/data/scraper_workflow_framework_design.md)

The guide is approximately **25,000 words** and includes the codebase diagnosis, proposed public APIs, execution semantics, SQLite schema, Goja integration, dynamic-work model, testing strategy, migration plan, implementation phases, code skeletons, and definition of done.

## Overall assessment

The codebase is overengineered **as the minimum reusable workflow API**, but much of the underlying engineering is justified for the operational problems it addresses.

The current repository is no longer merely a scraper. It combines a durable workflow engine, runner registry, SQLite state machine, lease protocol, retry scheduler, queue admission, artifact handling, JavaScript site runtime, site databases, manifest loading, generated CLI commands, HTTP APIs, and operator inspection. Its own architecture documentation describes Go as owning persistence, scheduling, leases, retries, queue policy, runners, and CLI behavior, while JavaScript owns site parsing and dynamic work generation. fileciteturn50file0L23-L46

That is a coherent application architecture. It is not a clean, small workflow library.

The current `pkg/workflow` package improves usability, but it remains a facade over the lower engine. Its `StepContext` exposes the durable workflow, raw operation, lease, scheduler time, dependency resolver, records, artifacts, projections, and dynamic operation emission. Its child-step options still include runner kind, queue, deduplication key, dependencies, retry policy, site, and parent ID. fileciteturn37file0L16-L30 fileciteturn37file0L39-L104 fileciteturn37file0L181-L245 fileciteturn37file0L247-L300

The JavaScript API leaks the same scheduler representation. Site authors construct objects containing `kind`, `queue`, `dedupKey`, `dependsOn`, retry settings, script metadata, workflow overrides, site overrides, and parent IDs. Dependency results can expose artifact body text, and scripts receive generic site and scraper database modules. fileciteturn51file0L152-L198 fileciteturn51file0L200-L243 fileciteturn51file0L246-L278

For example, the Hacker News implementation manually constructs IDs and queue identities in both its submission script and execution script, then performs direct SQL writes and emits further raw operations during pagination. fileciteturn53file0L24-L54 fileciteturn54file0L3-L43 fileciteturn55file0L62-L125

## What should be retained

The durable-engine hardening should not be discarded. Several mechanisms represent real correctness requirements:

- sortable numeric timestamps for database comparisons;
- transactional state changes;
- append-only attempt history;
- scheduler-owned heartbeats;
- current-token verification before completion;
- cancellation of stale execution;
- recoverable dependency blocking;
- completion-driven worker concurrency;
- post-commit observers;
- restart-safe snapshots.

The project’s hardening report documents why these were needed: the earlier implementation could execute less concurrency than configured, failed dependencies could permanently cancel finalizers, heartbeats did not extend correctly, and a stale worker could commit after another worker had recovered the operation. fileciteturn49file0L23-L41 The resulting invariant—that completion must prove ownership of a current live lease inside the same transaction—is worth preserving in any optional multi-process adapter. fileciteturn49file0L153-L190

The project notes also establish sound product principles: workflows should be restartable and auditable; raw and intermediate artifacts should be retained where appropriate; extraction, validation, and manual correction should remain separate; provider identity must be explicit; and manual repair should be represented rather than hidden. fileciteturn14file0L24-L47 fileciteturn14file0L92-L100

## Where Workflow V3 goes too far

Workflow V3 addresses genuine defects, particularly oversized control-plane JSON, fixed-cycle scheduling, artifact custody, and weak implementation identity. However, its base vocabulary includes:

- task bundle, entrypoint, ABI, and registry identities;
- isolation ceilings;
- budget accounts and claims;
- scalar and set references;
- first-class maps and reductions;
- approval gates;
- resource classes;
- compiled plan nodes;
- attempts, leases, and cancellation state.

Those concepts appear directly in the principal type model rather than as optional operational profiles. fileciteturn58file0L7-L42 fileciteturn58file0L44-L98 fileciteturn58file0L119-L213 fileciteturn58file0L216-L320

The linked research material effectively reaches the same conclusion: a two-step transform does not automatically require a JavaScript compiler frontend, bundles, catalog digests, registry generations, leases, approval gates, transactional budgets, Bubblewrap, an external-operation ledger, and canonical evidence projection. It recommends assigning each mechanism a concrete justifying force and deferring it when that force is absent. fileciteturn36file0L12-L30 fileciteturn36file0L32-L60

## Proposed clean architecture

The proposed replacement is a new standalone module, provisionally:

```text
github.com/go-go-golems/workflow
```

Scraper imports it. The workflow module does not import scraper, Glazed, Cobra, Gin, site databases, provider implementations, or the existing engine.

Its semantic center has six concepts:

```text
Plan
TaskRef
Handler
Engine
Repository
ArtifactStore
```

### 1. One canonical data-only plan

Go and JavaScript produce exactly the same normalized `Plan`.

```go
type Plan struct {
    Schema   string
    Name     string
    Version  string
    Steps    []StepSpec
    Outputs  map[string]Ref
    Metadata map[string]string
}
```

A plan never contains Go functions, Goja objects, database handles, credentials, worker IDs, leases, open readers, or registry pointers.

There is no required builder → IR → catalog → compiled-plan hierarchy. The builder is temporary syntax; the normalized plan is the durable definition.

### 2. Dependencies follow data flow

A step input is a JSON expression containing literals and references.

```go
fetch := b.Step(
    "fetch",
    workflow.Task("http.fetch", "1"),
    map[string]any{
        "url": b.Input("/baseURL"),
    },
)

parse := b.Step(
    "parse",
    workflow.Task("hackernews.parse", "1"),
    map[string]any{
        "body": fetch.Output("/body"),
    },
)
```

Because `parse` references `fetch`, the dependency is inferred. `After(...)` exists only for ordering without data transfer.

This removes the common error of specifying an input reference and a separate dependency list that can disagree.

### 3. One small task contract

```go
type Handler interface {
    Run(context.Context, TaskContext) (Result, error)
}

type TaskContext struct {
    RunID          RunID
    StepID         StepID
    Attempt        int
    Input          json.RawMessage
    IdempotencyKey string
    Logger         *slog.Logger
    Artifacts      ArtifactStore
}
```

No repository, transaction, lease, worker identity, site DB, scraper DB, or scheduler object appears in the handler context.

Domain dependencies are ordinary constructor dependencies:

```go
type StoreStoriesHandler struct {
    Stories StoryRepository
}
```

This is more testable, makes authority visible, and prevents the generic framework from becoming a service locator.

### 4. Progressive execution levels

The same plan runs at several operational levels:

| Level | Configuration |
|---|---|
| In-memory | task registry only |
| Local durable | add SQLite repository |
| Multi-process | add leasing repository and heartbeat supervisor |
| Remote or isolated | register command, container, or remote handlers |

The default API does not require a database:

```go
result, err := engine.Run(ctx, plan, input)
```

Adding durability changes engine composition, not the authored plan.

### 5. Bounded dynamic fragments

Tasks do not mutate the repository or call `ctx.emit()`.

A successful discovery task may return a bounded `Fragment`:

```go
fragment := workflow.NewFragment()

fetch := fragment.Step(
    "fetch-next",
    workflow.Task("http.fetch", "1"),
    map[string]any{"url": nextURL},
)

fragment.Step(
    "parse-next",
    workflow.Task("hackernews.parse", "1"),
    map[string]any{"body": fetch.Output("/body")},
)
```

The engine:

- validates the local DAG;
- namespaces IDs under the parent;
- enforces depth and count limits;
- inserts the fragment atomically with parent success;
- accepts an identical duplicate idempotently;
- rejects the same dynamic ID with a different specification.

This covers pagination, OCR pages, archive members, and bounded discovery without making maps, reductions, or graph mutation mandatory concepts.

### 6. Streaming artifacts outside SQLite

```go
type ArtifactStore interface {
    Put(
        context.Context,
        ArtifactDescriptor,
        io.Reader,
    ) (ArtifactRef, error)

    Open(
        context.Context,
        ArtifactRef,
    ) (io.ReadCloser, error)

    Stat(
        context.Context,
        ArtifactRef,
    ) (ArtifactRef, error)
}
```

The repository stores only compact references containing digest, size, media type, name, and locator.

No primary artifact API accepts a whole `[]byte`, and dependency resolution never automatically loads artifact bodies.

## Simplified state model

Stored run states:

```text
pending
running
succeeded
failed
canceled
```

Stored step states:

```text
pending
running
succeeded
failed
canceled
```

The following are derived views rather than persisted states:

```text
ready
waiting
retry_wait
blocked
```

A failed dependency leaves descendants pending but visibly blocked. Retrying the failed dependency naturally reopens those descendants. This preserves the useful blocked-versus-canceled behavior without requiring recursive status-repair transitions.

Attempts remain append-only:

```text
running
succeeded
failed
interrupted
canceled
lease_lost     // distributed extension
```

## Goja boundary

The guide specifies two separate modules.

### `require("workflow")`

This is a data-only authoring module. Most of the builder can be embedded JavaScript. It constructs a plain object, calls `JSON.stringify`, and sends the bounded JSON to one native strict normalizer. The normalizer returns canonical JSON.

No JavaScript object identity, callback, closure, or runtime pointer survives compilation.

### `require("workflow/runtime")`

This is an asynchronous client over the same Go `Engine`:

```javascript
await runtime.run(plan, input);
await runtime.submit(plan, input);
await runtime.inspect(runId);
await runtime.cancel(runId);
```

It does not implement a second scheduler.

The current Goja infrastructure already has runtime factories, event loops, runtime ownership, lifetime contexts, and runtime-aware module registration. Those facilities should be used so worker goroutines perform Go work while Promise resolution is posted back through the runtime owner. fileciteturn46file0L184-L238 fileciteturn46file0L240-L292 Host environment exposure is already modeled as an opt-in module, which is the correct capability posture for workflow authoring and task profiles. fileciteturn47file0L210-L240

Production JavaScript tasks use a separate `JSModuleHandler`, preferably with a fresh owned runtime per attempt. Goja is treated as an embedded runtime, not a hostile-code sandbox.

## Implementation order

The guide defines the following pull-request sequence:

1. Plan types, strict JSON, references, and JSON Pointer.
2. Builder, diagnostics, cycle detection, and canonical digest.
3. Registry, handler contract, and typed adapter.
4. Memory repository and sequential engine.
5. Completion-driven concurrency and cancellation.
6. Retry timing and administrative repair.
7. Bounded fragment expansion.
8. Streaming artifact store.
9. Events, observers, and snapshots.
10. Goja authoring and TypeScript declarations.
11. SQLite repository and shared conformance tests.
12. Restart and fault-injection tests.
13. Goja runtime module.
14. JavaScript task handler and capability profiles.
15. Scraper HTTP and temporary legacy-JS adapters.
16. Hacker News migration.
17. Remaining sites and old-engine retirement.

The old database should remain a read-only or old-worker concern during migration. Arbitrary old operation rows should not be mechanically translated into the new schema.

## Important qualification

This was a static source and design review. I reviewed the repository, linked project notes, representative source files, tests, and the Workflow V3 research branch, but did not independently execute the test suite because the repository could not be cloned in the review environment.

The recommended first implementation unit is the plan/value/reference model and canonical fixtures. It should contain no SQLite, Goja, HTTP, CLI, or scraper code.

