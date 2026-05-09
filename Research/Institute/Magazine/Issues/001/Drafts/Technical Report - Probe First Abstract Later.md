# Empirical Investigation as a Prerequisite to Abstraction in Systems Software

**Technical Report GR-2026-04-001**

Manuel Odendahl
The Golem Review / Institute

April 2026

---

## Abstract

We examine six systems projects completed over a four-day period (April 8-11, 2026) spanning browser automation, JavaScript runtime infrastructure, hardware device drivers, process supervision, and AI agent behavioral analysis. Despite no shared codebase or coordinated methodology, all six projects converged on a common pattern: a structured investigation phase targeting the live running system preceded and directly shaped the production implementation. We document the specific investigation techniques employed, the categories of assumptions they falsified, the architectural decisions that followed from the findings, and the failure modes that would have resulted from skipping the investigation phase. We propose a taxonomy of probe types (behavioral, invariant, throughput, structural) and evaluate their cost-benefit characteristics across domains. We observe that in five of six cases, the investigation phase discovered at least one assumption that, if encoded into the architecture, would have produced a silent correctness bug — a defect that produces wrong results without raising errors. We further analyze the interaction between investigation methodology and AI-assisted code generation by examining quantitative behavioral data from two AI coding agents solving identical tasks, finding that the agent with a higher read-to-code ratio completed broader scope while the agent with a lower ratio produced deeper but narrower test coverage. We conclude that probe-first methodology is complementary to, not replaced by, AI code generation, and that the most valuable human contribution in AI-assisted workflows is designing probes that interrogate the live system's behavior.

---

## 1. Introduction

A recurring problem in systems software engineering is the premature commitment to abstractions that encode unverified assumptions about the target system's behavior. When the assumption holds, the abstraction is transparent. When it does not, the abstraction becomes a source of silent failure — the system produces incorrect results, drops data, or enters inconsistent states without signaling an error.

The difficulty is that these assumptions are often reasonable. A developer examining ChatGPT's DOM in a browser inspector sees nodes marked with `data-message-author-role="assistant"` and reasonably concludes that selecting the last such node yields the most recent assistant response. A developer reading the Loupedeck device's WebSocket protocol documentation sees no mention of write-rate limits and reasonably concludes that the device accepts frames at the rate the host can produce them. A developer looking at a SQLite connection pool's bootstrap code sees `PRAGMA foreign_keys = ON` and reasonably concludes that foreign key constraints are enforced. In each case, the assumption is plausible, supported by partial evidence, and wrong.

The failure mode is not a crash or an error message. It is a system that appears to work — returns data, renders frames, persists records — while silently producing incorrect results. The ChatGPT extractor returns citation fragments instead of responses. The Loupedeck device produces malformed WebSocket frames that crash the client library minutes later. The SQLite connection pool hands out connections with foreign key enforcement disabled, allowing referential integrity violations to accumulate. These are not edge cases triggered by unusual inputs. They are default behaviors triggered by normal operation.

This report examines six projects where a structured investigation phase preceded the implementation phase. In each case, we document: (a) the initial assumption that would have governed the implementation, (b) the investigation technique that tested the assumption, (c) the finding that falsified or refined it, and (d) the architectural consequence. We further document the specific technical artifacts produced during investigation (numbered scripts, SQL queries, benchmark harnesses, invariant tests) and their ongoing role as regression-detection and documentation tools.

The projects were not designed as a controlled experiment. They share a developer, a toolchain (Go, JavaScript/Goja, Chrome DevTools Protocol, SQLite, i3 IPC, USB serial), and a general approach to systems work, but they address unrelated problem domains. The convergence on investigation-first methodology is therefore emergent rather than prescribed, which strengthens the claim that the pattern has broad applicability.

The remainder of this report is organized as follows. Section 2 introduces a taxonomy of probe types with formal definitions and examples. Sections 3-8 present the six case studies in full technical detail. Section 9 synthesizes cross-cutting findings, including quantitative analysis of investigation cost and silent failure prevalence. Section 10 addresses the interaction between probe-first methodology and AI-assisted code generation, drawing on behavioral data from two AI coding agents. Section 11 discusses related work and situates these findings in the broader literature. Section 12 concludes.

---

## 2. A Taxonomy of Probe Types

We distinguish four categories of probes based on what property of the target system they interrogate. The taxonomy is not intended to be exhaustive — hybrid probes exist — but provides a vocabulary for planning investigation phases and communicating findings.

### 2.1 Behavioral Probes

Behavioral probes test the system's observable output for specific inputs. They answer questions of the form "given stimulus X, what does the system produce?" Behavioral probes operate at the interface boundary and require no access to the system's internals. They are the most common probe type in the case studies examined here.

A behavioral probe consists of three components: a stimulus (a specific input or action applied to the system), an observation (what the system produces in response), and an expectation (what the system should have produced). The probe succeeds if the observation matches the expectation and fails otherwise. Critically, the expectation need not be known in advance — exploratory behavioral probes may be designed to discover what the system does, rather than to verify a specific behavior.

**Example from Section 3:** Executing a JavaScript expression against a live ChatGPT DOM page that selects all nodes matching `[data-message-author-role="assistant"]` and returns the text content of the last such node. Stimulus: the selector query. Observation: the string "MIT OpenCourseWare". Expectation: the full assistant response (multiple paragraphs). The probe fails, revealing that the selector is not a unique discriminator for response content.

**Example from Section 8:** Executing a JavaScript readiness check against a Kagi Search page immediately after `document.readyState === 'complete'`. Stimulus: querying for `#search-results` children. Observation: zero child elements. Expectation: search result rows. The probe fails, revealing that DOM readiness does not imply content readiness.

The key property of behavioral probes is that they test the system's actual behavior, not its documented or assumed behavior. This makes them particularly valuable when documentation is incomplete, outdated, or absent — a common condition for web page DOM structures, hardware device protocols, and third-party APIs.

### 2.2 Invariant Probes

Invariant probes test whether a system's stated or implied contracts hold under specific conditions. They answer questions of the form "does property P hold after operation sequence O?" Invariant probes differ from behavioral probes in that they test a relationship between states rather than a single input-output pair. They require knowledge of the contract being tested but not necessarily access to the system's internals.

An invariant probe consists of four components: a contract (the property the system claims to maintain), a setup (an operation sequence that should preserve the contract), a check (an observation that tests whether the contract holds), and a verdict (whether the contract was preserved or violated).

**Example from Section 4:** The REPL session service claims that soft-deleted sessions are excluded from normal queries. Setup: create a session, then delete it. Check: query all sessions and examine whether the deleted session appears. Verdict: the deleted session appeared — the invariant is violated.

**Example from Section 4:** The REPL session service implies that durable session IDs are unique across processes (since they serve as primary keys in a persistent store). Setup: inspect the ID generation code path. Check: determine whether two concurrent processes would generate colliding IDs. Verdict: the ID generator uses a process-local counter initialized to zero at startup, so concurrent processes generate identical ID sequences — the invariant is violated.

Invariant probes are particularly effective for persistence and database systems, where contracts are often implicit (derived from the data model) rather than explicit (stated in documentation), and where violations are silent (no error is raised when a foreign key constraint is not enforced).

### 2.3 Throughput Probes

Throughput probes measure the system's capacity and degradation characteristics under load. They answer questions of the form "at what rate does the system begin to exhibit failure mode F?" Throughput probes differ from behavioral probes in that they test a continuous variable (rate, volume, duration) rather than a discrete input-output pair. They require a controllable load generator and a failure detector.

A throughput probe consists of four components: a workload (a parameterized load applied to the system), a sweep (a range of parameter values tested), an observation (the system's behavior at each parameter value), and a characterization (a model of the system's capacity and degradation curve).

**Example from Section 5:** Writing RGB565 display frames to a Loupedeck Live device at increasing rates, measuring the rate at which the device begins producing malformed WebSocket frames. Workload: `WriteFramebuff` + `Draw` message pairs. Sweep: 50% to 100% of theoretical maximum throughput in 5% increments. Observation: first errors at approximately 90% of maximum (32 FPS for full-screen 360x270 writes); error rate increases non-linearly above this threshold. Characterization: safe operating envelope is approximately 80% of measured maximum, with a non-linear failure curve above that threshold.

Throughput probes are particularly effective for hardware device drivers and network protocols, where capacity limits are often undocumented and degradation modes are often non-obvious (the Loupedeck device does not drop frames gracefully — it produces malformed protocol data that crashes the client library).

### 2.4 Structural Probes

Structural probes examine the system's internal organization to identify ownership relationships, dependency paths, and state management patterns. They answer questions of the form "which component owns resource R, and what happens to R when the component is terminated?" Structural probes require access to source code or runtime introspection.

A structural probe consists of three components: a question (about ownership, dependency, or state flow), a trace (following the relevant path through the code or runtime), and a finding (the actual relationship discovered).

**Example from Section 6:** Tracing `context.Context` propagation from `main()` through server construction, manager construction, and subprocess launch in the Screencast Studio codebase. Question: which context is the parent of the ffmpeg subprocess's context? Trace: the subprocess receives `exec.CommandContext` with a request-scoped context created per-API-call. Finding: the subprocess's context is a child of a dead request, not a child of the server runtime — the ownership topology is incorrect.

**Example from Section 6:** Examining the recording manager's `Stop()` method. Question: what locks are held during the subprocess wait? Trace: the method acquires a `sync.Mutex`, looks up the recording, sends SIGTERM, and calls `cmd.Wait()` while holding the mutex. Finding: any concurrent call to `Status()` or `Start()` will block on the mutex until the subprocess exits, which can take arbitrarily long — the lock discipline is incorrect.

Structural probes are the most labor-intensive probe type, as they require reading and tracing through source code. However, they are also the most effective for process management and concurrent systems, where ownership topology determines cancellation behavior and lock discipline determines deadlock potential.

### 2.5 Summary

Table 1 summarizes the probes employed across the six case studies.

| Project | Behavioral | Invariant | Throughput | Structural | Total |
|---|---|---|---|---|---|
| DOM extraction (Surf CLI, Section 3) | 7 numbered scripts | 1 (dedup correctness) | 0 | 2 (DOM tree analysis) | 10 |
| REPL session hardening (Goja, Section 4) | 0 | 5 (deletion, ID uniqueness, FK enforcement, timeout recovery, post-timeout usability) | 0 | 1 (service file responsibility audit) | 6 |
| Device driver (Loupedeck, Section 5) | 3 (protocol handshake, input events, display encoding) | 0 | 4 (full-screen FPS, single-tile FPS, 12-tile aggregate, degradation threshold) | 1 (write-path ownership) | 8 |
| Process supervision (Screencast Studio, Section 6) | 1 (Ctrl-C behavior observation) | 2 (lock-free shutdown, staged drain completion) | 0 | 3 (context ownership tree, manager lifecycle, subprocess parentage) | 6 |
| Cross-model analysis (Minitrace, Section 7) | 0 | 0 | 0 | 4 (tool frequency, file-touch patterns, build cycles, rewrite timelines) | 4 |
| Page readiness (Surf CLI, Section 8) | 5 (per-application readiness gaps) | 1 (turn-boundary extraction correctness) | 0 | 1 (completion detection mechanism) | 7 |
| **Total** | **16** | **9** | **4** | **12** | **41** |

The distribution is not uniform across probe types: behavioral probes dominate in web/DOM domains, invariant probes dominate in persistence domains, throughput probes appear only in the hardware domain, and structural probes are distributed across all domains. Section 9 analyzes this distribution in detail.

---

## 3. Case Study: DOM Extraction Under Structural Ambiguity

### 3.1 System Under Investigation

ChatGPT's web interface renders conversation turns as DOM subtrees within `<section>` elements carrying `data-testid` attributes of the form `conversation-turn-N`. Within each turn, message content nodes carry `data-message-author-role` attributes (`user`, `assistant`, `system`) and `data-message-id` attributes for deduplication. The interface is served as a React single-page application with dynamic rendering; the DOM structure is not documented and changes without notice across deployments.

The Surf CLI project (`/home/manuel/code/others/llms/pi/nicobailon/surf-cli`) automates interaction with multiple web applications (ChatGPT, Kagi Search, Kagi Assistant, Gmail) via the Chrome DevTools Protocol. The ChatGPT transcript extraction command (`surf-go chatgpt transcript`) must reliably extract the full text of each assistant response from the live DOM.

### 3.2 Initial Assumption

The initial extraction strategy selected the globally last DOM node matching `[data-message-author-role="assistant"]`. The assumption: the last such node in document order contains the assistant's most recent response. This assumption was supported by visual inspection of the DOM in Chrome DevTools, where the assistant's response appeared to be the final element with this attribute.

The implementation was straightforward:

```javascript
const allAssistantNodes = document.querySelectorAll(
  '[data-message-author-role="assistant"]'
);
const lastAssistant = allAssistantNodes[allAssistantNodes.length - 1];
return lastAssistant.innerText;
```

### 3.3 Investigation

Seven behavioral probes were executed against live ChatGPT pages. Probes were implemented as standalone JavaScript files, numbered sequentially, and saved in a ticket directory (`ttmp/2026/04/08/SURF-20260408-R4--surf-go-non-provider-cli-parity-architecture-and-implementation-guide/scripts/`) for reproducibility.

**Probe 001 (`chatgpt_transcript_dom_summary.js`):** Raw inventory of all message nodes in the page, reporting `data-message-author-role`, `data-message-id`, and `innerText` length for each node. Purpose: establish ground truth of what nodes exist.

**Probe 002 (`chatgpt_transcript_extract_dom.js`):** Refined extractor attempting global selection of the last assistant node. Purpose: reproduce the production extraction path and capture its exact output.

**Probe 003 (extraction validation):** Ran Probe 002 against a conversation where the assistant had provided a multi-paragraph explanation of a technical topic. Result: the extractor returned the string "MIT OpenCourseWare" — a short citation fragment — instead of the expected multi-paragraph response. This was the falsifying observation.

Inspection of the Probe 001 output for the same page revealed the cause: ChatGPT renders citation metadata as separate DOM nodes carrying the same `data-message-author-role="assistant"` attribute as the primary response. These citation nodes appear after the response body in document order and contain short text fragments (typically organization names, URLs, or publication titles). The globally-last assistant node was therefore a citation fragment, not the response body.

**Probe 004 (`chatgpt_transcript_resource_scan.js`):** Investigated whether a backend API could provide structured transcript data, bypassing the DOM entirely. Discovered the endpoint `/backend-api/conversation/<id>/textdocs`, which appears to return structured conversation data.

**Probe 005 (`chatgpt_transcript_backend_probe.js`):** Attempted to call the `/backend-api/conversation/<id>/textdocs` endpoint from page JavaScript. Result: HTTP 401 Unauthorized. The endpoint requires a bearer token that is not accessible to JavaScript running in the page context (it is stored in an HttpOnly cookie or server-side session). This avenue was abandoned; DOM extraction remained the most reliable approach.

**Probe 006 (`chatgpt_transcript_cache_scan.js`):** Examined `localStorage`, `sessionStorage`, and `IndexedDB` for cached conversation data. Result: no usable transcript data in client-side storage. Conversation content is not cached locally in a structured format.

**Probe 007 (activity trace expansion):** Investigated how reasoning models (o3, o4-mini) render their thinking traces. Found that a "Thought for N seconds" button appears in the DOM; clicking it expands an activity flyout with the full reasoning text. This required a separate extraction path:

```javascript
const thoughtButton = Array.from(section.querySelectorAll('button'))
  .find((node) => /Thought for/i.test((node.textContent || '').trim()));
if (thoughtButton) {
  thoughtButton.click();
  // Wait for activity flyout to materialize
  const activitySection = await waitForActivityFlyout(duration);
  // Attach reasoning text back to the turn
}
```

### 3.4 Finding

**The `data-message-author-role` attribute is not a unique discriminator for response content.** Citation fragments, reasoning traces, and canvas artifacts share the attribute value, differing only in text length and DOM position within the conversation turn boundary. Global selection by attribute — regardless of whether one selects the first, last, or any single node — is therefore insufficient. Extraction must operate within turn boundaries and apply a disambiguation heuristic.

A secondary finding: the backend API exists but is inaccessible from page JavaScript, and client-side storage does not contain usable transcript data. DOM extraction is the only viable approach for extension-based tools.

### 3.5 Architectural Consequence

The production extractor (`go/internal/cli/commands/scripts/chatgpt_transcript.js`) implements turn-scoped extraction with deduplication and longest-text selection:

```javascript
function extractSectionMessage(section, index) {
  const candidates = Array.from(
    section.querySelectorAll('[data-message-author-role]')
  );

  // Deduplicate by message ID, keeping longest text per ID
  const byMessageId = new Map();
  for (const node of candidates) {
    const role = node.getAttribute('data-message-author-role') || 'unknown';
    const messageId = node.getAttribute('data-message-id')
      || `${role}:${index}:${byMessageId.size}`;
    const model = node.getAttribute('data-message-model-slug') || null;
    const text = (node.innerText || '').trim();

    if (!text) continue;

    const existing = byMessageId.get(messageId);
    if (!existing || text.length > existing.text.length) {
      byMessageId.set(messageId, {
        role, model, messageId, text, textLength: text.length
      });
    }
  }

  const items = Array.from(byMessageId.values())
    .sort((a, b) => b.textLength - a.textLength);
  return items[0] || null;
}

// Top-level extraction: iterate conversation turns
const turns = document.querySelectorAll(
  'section[data-testid^="conversation-turn-"]'
);
const messages = [];
turns.forEach((section, index) => {
  const msg = extractSectionMessage(section, index);
  if (msg) messages.push(msg);
});
```

The algorithm proceeds in five steps:

1. **Select conversation turns** via `section[data-testid^="conversation-turn-"]` in DOM order.
2. **Within each turn,** find all nodes with `[data-message-author-role]`.
3. **Deduplicate by message ID** using the `data-message-id` attribute, grouping nodes that represent the same logical message.
4. **For each unique message ID, retain the node with the longest `innerText`.** This defeats citation fragments (which are short, typically under 100 characters) while preserving the full response body (which is typically thousands of characters).
5. **Skip empty nodes** (those with no text content after trimming).

This algorithm is robust to the addition of new auxiliary node types (e.g., reasoning traces from o3/o4-mini models, canvas artifacts, image captions) provided they are shorter than the primary response or carry distinct message IDs. The longest-text heuristic is simple but effective because the primary response is, by construction, much longer than any metadata fragment.

The Go command wrapper (`go/internal/cli/commands/chatgpt_transcript.go`) exposes this extraction through a dual-mode Glazed command: writer mode emits Markdown, glaze mode emits structured rows:

```go
func (c *ChatGPTTranscriptCommand) RunIntoWriter(
  ctx context.Context, w io.Writer,
  parsedLayers *layers.ParsedLayers, ps map[string]interface{},
) error

func (c *ChatGPTTranscriptCommand) RunIntoGlazeProcessor(
  ctx context.Context, gp *glazed.GlazeProcessor,
  parsedLayers *layers.ParsedLayers, ps map[string]interface{},
) error
```

Validation: the conversation that originally returned citation fragments ("MIT OpenCourseWare") now returns the full 18,933-character response through the turn-based extractor.

### 3.6 Probe Preservation

The numbered investigation scripts are preserved in the ticket directory and serve two ongoing roles:

1. **Regression detection.** When ChatGPT's DOM structure changes (a routine occurrence for web applications), the team re-runs the numbered probes before modifying production extraction code. This provides a structured way to understand what changed before deciding how to adapt.

2. **Onboarding documentation.** New contributors to the Surf CLI project can read the probes in sequence to understand the DOM structure, the failure modes, and the reasoning behind the current extraction algorithm. The probes are executable documentation — they can be run against a live page to verify that their observations still hold.

This preservation pattern — investigation scripts kept alongside production code, not discarded after the implementation phase — appeared independently in four of the six case studies.

### 3.7 Cost of Skipping Investigation

Without the probe phase, the system would have shipped with the global-last-node selector. The failure mode is silent: the extractor returns valid text (a real string from a real DOM node) that is not the intended content. No error is raised. No exception is thrown. The returned string is well-formed, non-empty, and comes from a node with the correct role attribute.

Downstream consumers — transcript databases, summary pipelines, search indexes, conversation analysis tools — would ingest citation fragments as if they were complete responses. A search for "explain linear algebra" would return a transcript entry containing "MIT OpenCourseWare" as the assistant's response. The corruption would propagate through any system that treats the extracted text as authoritative, with no automated signal to trigger detection. The bug would be discovered only when a human noticed that extracted transcripts contained short, nonsensical responses instead of the expected content — and even then, the cause would not be obvious, because the extraction code looks correct (it selects the right attribute) and the returned text is real (it exists in the DOM).

---

## 4. Case Study: Invariant Verification in Persistent Session Infrastructure

### 4.1 System Under Investigation

The go-go-goja REPL service (`/home/manuel/workspaces/2026-04-03/js-repl-smailnail/go-go-goja`) provides persistent JavaScript evaluation sessions backed by SQLite. The architecture consists of six layers:

```
user / API request
  -> replapi              (request/config parsing)
  -> replsession.Service  (lifecycle, orchestration)
  -> engine runtime owner (goja VM management)
  -> goja VM execution    (JavaScript evaluation)
  -> result shaping       (observation, snapshots)
  -> repldb / SQLite      (persistence)
```

Sessions have lifecycles (create, evaluate, persist, soft-delete), durable IDs for cross-process reference, foreign key relationships between session records and evaluation history, and configurable execution policies including timeout behavior.

### 4.2 Initial Assumptions

Three implicit contracts governed the service, derived from the data model and API semantics:

1. **Soft deletion invisibility:** Soft-deleted sessions (those with a non-NULL `deleted_at` timestamp) are excluded from normal query paths. A user who deletes a session should not see it in subsequent listings.

2. **ID global uniqueness:** Durable session IDs are unique across all processes that access the same database. Since IDs serve as primary keys in a persistent store shared across potentially concurrent service instances, collisions would cause data corruption.

3. **Foreign key enforcement:** SQLite foreign key constraints are enforced on all database connections, preventing orphaned evaluation records and ensuring cascade behavior on deletion.

A fourth assumption, not derived from the data model but from prior experimentation, concerned the evaluation subsystem:

4. **Timeout non-viability:** A prior experiment using `goja_nodejs/eventloop` had concluded that synchronous timeout interruption was unreliable, suggesting that an architectural rewrite would be necessary to support evaluation timeouts.

### 4.3 Investigation

Six probes were executed, organized across three tickets: GOJA-040 (persistence correctness), GOJA-041 (evaluation control), and GOJA-042 (cleanup and refactor).

**Probe 1 (soft deletion visibility).** Create a session, set its `deleted_at` timestamp, then call the `List()` method. Expected: the deleted session is excluded from results. Observed: the deleted session appeared in the result set.

Root cause analysis: the codebase had multiple query paths for listing sessions. Some paths included a `WHERE deleted_at IS NULL` predicate; the `List()` method used for API responses did not. The inconsistency was introduced incrementally as new query paths were added without a shared predicate builder — each path constructed its own WHERE clause, and the soft-deletion filter was omitted from the newest path.

The invariant can be stated precisely:

```
If session.deleted_at is set,
then normal list/get paths must behave as if the session does not exist.
```

This invariant was violated in the most common query path.

**Probe 2 (ID uniqueness).** Inspect the ID generation code path in `pkg/replsession/service.go`. Expected: IDs are generated using a globally unique scheme (UUID, ULID, or similar). Observed: durable IDs were generated by incrementing a process-local counter initialized to zero at startup. The generation pattern was `sess-1`, `sess-2`, `sess-3`, etc.

The failure scenario: two instances of the service running simultaneously (e.g., during a deployment, in a container orchestrator, or in a development environment with multiple terminal sessions) would generate colliding IDs. The collision would not raise an error at generation time. It would manifest later as either:
- A primary key conflict on the next database write (if both instances write to the same database), or
- Silent data corruption (if sessions were created against different database files and later merged, or if the same ID was reused after a process restart).

**Probe 3 (foreign key enforcement).** Create a connection from the SQLite connection pool and execute `PRAGMA foreign_keys` to check the current state. Expected: the pragma returns `1` (enabled). Observed: the pragma returned `0` (disabled).

Root cause analysis: the `PRAGMA foreign_keys = ON` statement was executed once during the database bootstrap sequence, on the first connection opened. However, the application used a connection pool. SQLite pragmas are per-connection state — they do not persist across connections. When the pool opens a new connection (due to pool growth, connection recycling, or connection failure), the new connection inherits SQLite's default state, which is `foreign_keys = OFF`. The bootstrap pragma affected only the bootstrap connection, not subsequent pooled connections.

The consequences of unenforced foreign keys:
- Evaluation history records could reference non-existent sessions (orphaned rows).
- Deleting a session would not cascade to its evaluation history.
- Join queries between sessions and evaluations could return phantom rows.
- Data integrity would degrade over time as the orphaned row count grew, with no error or warning.

**Probe 4 (timeout interruption — synchronous code).** Execute a long-running synchronous JavaScript loop with a 100ms timeout via the actual production code path: `engine.Runtime -> Owner.Call -> rt.VM.RunString(...)`. Expected (based on prior experiment): timeout does not interrupt synchronous execution. Observed: the runtime interrupted the loop and returned a timeout error within the specified deadline.

This probe contradicted the prior experimental result. The discrepancy was traced to a critical difference: the prior experiment used the `goja_nodejs/eventloop` package, which wraps the goja runtime in an event loop with its own execution model. The production code path does not use the event loop — it calls `VM.RunString()` directly on the goja runtime, which supports interrupt-based cancellation via `VM.Interrupt()`. The prior experiment's conclusion was correct for its specific code path but was incorrectly generalized to the production code path.

The timeout mechanism works as follows:

```
evaluate code
  -> rewrite if needed
  -> run inside runtime owner
  -> start timeout watcher goroutine
  -> if context deadline fires:
       call VM.Interrupt() on the goja runtime
  -> wait for evaluation to unwind
  -> clear interrupt state on the runtime
  -> return timeout result
```

**Probe 5 (post-timeout session state).** After triggering a timeout, execute a series of evaluations that depend on session state (variable bindings, function definitions from prior evaluations). Expected: session state is corrupted by the interrupt. Observed: all state was preserved. Variable bindings from before the timeout were accessible. Function definitions remained callable. The timeout mechanism interrupts execution without corrupting the runtime's JavaScript heap.

The recovery invariant:

```
After a timed-out evaluation,
the same session must still be able to evaluate a later cell successfully.
```

This invariant was confirmed by the probe.

**Probe 6 (service file responsibility audit — structural probe).** Examine the file `pkg/replsession/service.go` to determine how many distinct responsibilities it contains. Found: lifecycle management, evaluation pipeline, persistence shaping, and observation helpers were all co-located in a single 800+ line file. While not a correctness bug, this structural finding informed the cleanup track (GOJA-042), which split the file into four:

- `service.go`: lifecycle and top-level orchestration
- `evaluate.go`: evaluation pipeline, timeout/interrupt flow
- `persistence.go`: persisted session and history shaping
- `observe.go`: summaries, snapshots, and observation helpers

This is separation of concerns without code-size reduction: the total logic volume remained similar, but the mapping between file and responsibility became reviewable.

### 4.4 Findings Summary

Three of the five invariant probes revealed violations. All three violations were silent — they produced incorrect behavior without raising errors, logging warnings, or failing tests. The two probes that tested the evaluation subsystem (timeout interruption, post-timeout state) confirmed correct behavior, contradicting a prior false negative and preventing an unnecessary architectural rewrite.

| Probe | Contract | Verdict | Consequence if undetected |
|---|---|---|---|
| Soft deletion | Deleted sessions excluded from queries | Violated | Deleted sessions visible in API responses |
| ID uniqueness | IDs unique across processes | Violated | Primary key conflicts or silent data corruption under concurrency |
| FK enforcement | Foreign keys enforced on all connections | Violated | Orphaned records, broken cascades, phantom join rows |
| Timeout interruption | Synchronous code can be interrupted | Confirmed | Unnecessary multi-week rewrite |
| Post-timeout state | Sessions usable after timeout | Confirmed | Unnecessary defensive complexity |

### 4.5 Architectural Consequences

**Soft deletion:** All query paths now use a shared query builder that prepends `deleted_at IS NULL` to the WHERE clause. The builder is the single point of entry for session queries, making it structurally impossible to construct a query that returns deleted sessions without an explicit override.

**ID generation:** Process-local counter replaced with UUID v4 generation. The new IDs are opaque, globally unique, and have no dependency on process-local state.

**Foreign key enforcement:** The `PRAGMA foreign_keys = ON` statement moved from the bootstrap sequence to a connection initialization callback registered with the pool. Every connection — whether the first or the hundredth — receives the pragma before its first use by application code.

**Evaluation timeout:** No architectural rewrite. The existing interrupt-based approach was validated as correct for the production code path. The false negative from the prior experiment was documented in the ticket diary to prevent future re-investigation.

### 4.6 Validation

```bash
go test ./pkg/repldb ./pkg/replapi ./pkg/replsession
go test ./pkg/replapi ./pkg/repl/adapters/bobatea ./pkg/repl/evaluators/javascript
go test ./...
golangci-lint run -v
```

All tests pass. The invariant probes were encoded as persistent test cases that will detect future regressions.

### 4.7 Cost Analysis

The investigation phase (six probes across three tickets) consumed approximately four hours. The most consequential finding — the false negative on timeout interruption (Probe 4) — took approximately 30 minutes to execute and validate. The architectural rewrite it prevented would have consumed an estimated two to three weeks, based on the scope of replacing the interrupt-based timeout mechanism with an alternative (process isolation, separate goroutine with channel-based cancellation, or goja_nodejs/eventloop integration).

The three correctness bugs (Probes 1-3) were each fixable in under an hour once identified. Without identification, they would have surfaced as user-facing bugs weeks or months later, with significantly higher debugging cost due to the distance between the symptom (phantom sessions, ID conflicts, orphaned records) and the root cause (missing WHERE predicate, process-local counter, per-connection pragma).

---

## 5. Case Study: Throughput Characterization of a Constrained Display Device

### 5.1 System Under Investigation

The Loupedeck Live is a USB control surface with three LCD displays (left: 60x270, main: 360x270, right: 60x270) connected over USB serial. The device presents as a CDC ACM device at `/dev/ttyACM0` (vendor `2ec2`, product `0004`). The communication protocol is a WebSocket variant running over the serial connection — referred to internally as the "mutant WebSocket" protocol, implemented in firmware version 2.x.

The display protocol uses two message types for rendering:

- **`WriteFramebuff` (type `0x10`):** Uploads RGB565 pixel data to the device's framebuffer. The message contains a 10-byte header (display ID, x, y, width, height) followed by the pixel payload. For a 90x90 tile, the payload is 16,200 bytes (90 * 90 * 2 bytes per pixel in RGB565 encoding).

- **`Draw` (type `0x0f`):** Triggers a display refresh. Each display update requires both messages in sequence: first `WriteFramebuff` to upload pixel data, then `Draw` to trigger the refresh. The device acknowledges both messages with single-byte responses (data `[1]`).

Input events arrive as unsolicited messages: button events (type `0x00`, format `[button_id, status]`), knob rotation events (type `0x01`, format `[knob_id, delta]` where delta is a signed 8-bit integer), and touch events (type `0x02`, format `[touch_id, status, x_hi, x_lo, y_hi, y_lo]`).

### 5.2 Initial Assumption

The device accepts display updates at the rate the host can produce them. The WebSocket protocol provides no flow-control mechanism: no acknowledgment gating (acknowledgments are sent but not required before the next write), no backpressure signaling, no windowing. The protocol specification (such as it is — the device's developer documentation is minimal) does not mention write-rate limits or throughput constraints.

### 5.3 Initial Discovery

The first program written for the device — a 200-line Hello World (`cmd/loupe-feature-tester/main.go`) that filled the main display with a solid color — worked correctly. The second program, which attempted to update all 12 touch-button tiles in rapid succession, crashed the device. The crash manifested not as a clean disconnection but as protocol corruption: the device sent back WebSocket frames with invalid opcodes, causing the gorilla/websocket client library to panic.

Observed error messages:

```
websocket: bad opcode 4              # Reserved opcode (undefined in RFC 6455)
websocket: FIN not set on control     # Malformed control frame header
malformed HTTP response "\x82\x05..." # Binary data where HTTP was expected
```

These errors indicate that the device's firmware entered a state where it was no longer producing valid WebSocket frames. The binary data being sent was likely a mix of display acknowledgments and partial frame headers that the client library could not parse.

The initial workaround was ad-hoc rate limiting: inserting `time.Sleep(100 * time.Millisecond)` between draw operations during setup, and `time.Sleep(500 * time.Millisecond)` after all setup completed. This prevented the crash but was not derived from measurement — the sleep durations were guesses that happened to work for the initial program's workload.

### 5.4 Investigation

Four throughput probes were executed using a dedicated benchmark harness (`cmd/loupe-fps-bench/main.go`) that bypassed the rendering layer entirely, allowing direct measurement of transport-layer throughput. The harness configured the writer with unconstrained settings:

```go
writerOptions := loupedeck.WriterOptions{
    QueueSize:    4096,
    SendInterval: 0,  // No pacing delay
}
l, err := loupedeck.ConnectAutoWithWriterAndRenderOptions(writerOptions, nil)
```

With the renderer disabled and the writer unconstrained, every draw call went directly to the WebSocket connection, providing a clean measurement of the transport/device throughput ceiling.

**Probe 1 (full-screen FPS).** Write 360x270 RGB565 frames (194,400 bytes per frame, plus 10-byte header and protocol framing) in a tight loop, counting successful round-trips per second. Each frame requires two protocol messages: `WriteFramebuff` and `Draw`.

Result: **36 FPS stable, peaking at 37.65 FPS.** Above approximately 40 FPS, the device began returning malformed frames.

**Probe 2 (single-tile FPS).** Write 90x90 RGB565 frames (16,200 bytes per frame) in a tight loop.

Result: **approximately 320 FPS stable, peaking at 314.44 FPS.** The per-frame byte count is 12x smaller than full-screen, and the throughput increase is roughly proportional (320/36 = 8.9x), indicating that throughput is primarily byte-rate-limited rather than message-rate-limited. The gap from the expected 12x ratio is accounted for by per-message overhead (header parsing, display-region addressing, acknowledgment processing).

**Probe 3 (12-tile aggregate FPS).** Write 12 distinct 90x90 tiles in sequence (one full button bank update), measuring aggregate tile-updates per second.

Result: **approximately 288 FPS total (24 FPS per tile), peaking at 314.02 FPS total.** The 10% reduction from the single-tile maximum (288 vs. 320) indicates per-message overhead that becomes significant when messages are small and numerous.

| Scenario | Geometry | Bytes/frame | Stable FPS | Peak FPS |
|---|---|---|---|---|
| Full main display | 360x270 | 194,400 | 36 | 37.65 |
| Single tile | 90x90 | 16,200 | 320 | 314.44 |
| 12 tiles (aggregate) | 12 x 90x90 | 12 x 16,200 | 288 total | 314.02 total |

**Probe 4 (degradation threshold).** Increase write rate from 50% to 100% of the Probe 1 maximum in 5% increments, recording the error frequency at each step. This probe was implemented by controlling the inter-frame delay and counting WebSocket read errors over a 10-second window at each rate.

Result:

| Rate (% of max) | Approx. FPS | Error rate |
|---|---|---|
| 50% | 18 | 0% |
| 60% | 22 | 0% |
| 70% | 25 | 0% |
| 80% | 29 | 0% |
| 85% | 31 | 0% |
| 90% | 32 | ~0.1% |
| 95% | 34 | ~2% |
| 100% | 36 | ~8% (intermittent protocol reset) |

The degradation curve is non-linear: the device operates cleanly up to approximately 80% of maximum throughput, begins producing occasional errors at 90%, and enters a high-error-rate regime above 95%. There is no intermediate "graceful degradation" mode — the device does not drop frames or reduce quality. It either processes frames correctly or produces protocol-corrupting garbage.

### 5.5 Findings

1. **The device has no protocol-level flow control.** There is no mechanism for the device to signal the host to slow down. The failure mode is not graceful degradation but protocol corruption.

2. **The safe operating envelope is approximately 80% of measured maximum throughput.** Above this threshold, error rates increase non-linearly.

3. **Throughput is primarily byte-rate-limited.** Smaller frames can be sent at proportionally higher frame rates, indicating that the bottleneck is the serial transport bandwidth and the device's framebuffer write speed, not the protocol message processing rate.

4. **These characteristics are entirely undocumented.** The device manufacturer's documentation does not describe throughput limits, degradation behavior, or recovery procedures after protocol corruption. The only recovery from a corrupted state is to power-cycle the device.

### 5.6 Architectural Consequences

The investigation results directly shaped a three-layer architecture between application draw calls and device writes:

**Layer 1: Render scheduler with keyed invalidation.** Each display draw call is associated with a region key of the form `<display>:<x>:<y>:<width>:<height>` (e.g., `main:180:90:90:90`). The scheduler maintains a map from region key to the latest draw command for that region.

```
invalidate(regionKey, command):
    invalidations += 1
    if pending[regionKey] exists:
        coalescedReplacements += 1
    pending[regionKey] = command

on flush tick:
    if pending is empty: return
    keys = sorted(pending.keys())     # deterministic order
    commands = [pending[k] for k in keys]
    clear pending
    for cmd in commands:
        writer.enqueue(cmd)
        flushedCommands += 1
```

The "latest-wins" strategy means that if a tile is redrawn multiple times within one flush interval (e.g., during an animation), only the final state is sent to the device. This collapses bursts at the application level before they reach the transport.

Test guarantee: two successive draws to the same region produce two invalidations, at least one coalesced replacement, and exactly one flushed command containing the second image's pixel data.

**Layer 2: Single-writer goroutine.** All device writes are serialized through a single goroutine that owns the WebSocket connection. This eliminates concurrent write races and provides a single point for pacing enforcement:

```
writer loop:
    receive command from queue
    wait until send interval has elapsed since last write
    for each message in command.Messages():
        conn.WriteMessage(BinaryMessage, messageBytes)
    update WriterStats
    signal completion to caller
```

**Layer 3: Flush interval tuning.** The flush interval is set to maintain aggregate throughput at or below 80% of the measured maximum for the current workload's update granularity. For the common case of 12-tile animation (the full button bank), this produces approximately 15 FPS per tile — well within the safe envelope and visually sufficient for UI animation (human perception of smooth animation requires approximately 12-15 FPS for simple motion).

The architecture is exposed through configuration types:

```go
type WriterOptions struct {
    QueueSize    int
    SendInterval time.Duration
}

type RenderOptions struct {
    FlushInterval time.Duration
    QueueSize     int
}
```

Application code draws whenever it wants, at whatever rate the application logic produces frames, and the scheduler absorbs the bursts:

```go
// Application code — no rate limiting needed
display.Draw(animatedFrame, x, y)  // returns immediately
```

The optimization sequence derived from the investigation is:

1. Reduce update area (full screen -> per-tile)
2. Cache aggressively (precompute sprites, text, geometry before animation loop)
3. Reduce frame rate (aim for visually sufficient rate, not maximum)
4. Coalesce redundant updates (let the scheduler collapse repeated invalidations)
5. Tune writer pacing (only after workload shape is established)
6. Rebenchmark (measure actual workload, not synthetic)

### 5.7 Cost of Skipping Investigation

Without throughput characterization, the implementation would have relied on ad-hoc rate limiting — `time.Sleep` calls scattered through application code, with durations chosen by trial and error. This approach has four deficiencies:

1. **The sleep durations are guesses.** Without measurement, there is no way to know whether 100ms is too conservative (wasting 80% of available throughput) or too aggressive (still risking protocol corruption under certain workloads).

2. **The approach is uniform.** A single sleep duration cannot be correct for both full-screen writes (which need more pacing) and single-tile writes (which need less). The throughput measurements show an order-of-magnitude difference in safe frame rates between these granularities.

3. **The burden falls on application developers.** Every consumer of the library must independently discover the rate-limiting requirement, choose a sleep duration, and insert delays in the correct locations. There is no guarantee that all consumers will do this, or that they will choose safe values.

4. **The approach is fragile under composition.** When multiple application components draw to different regions concurrently (e.g., an animation loop drawing tiles and a status update drawing to the left strip), ad-hoc sleep-based rate limiting in each component does not compose — the aggregate write rate may exceed the device's capacity even if each component individually stays below its assumed limit. The scheduler's coalescing and single-writer architecture handle this automatically.

---

## 6. Case Study: Ownership Topology in a Multi-Manager Server Runtime

### 6.1 System Under Investigation

Screencast Studio is a CLI-launched local server for managing video recording sessions. The server manages recording sessions (ffmpeg video capture, parec audio capture), preview streams (live ffmpeg transcoding to MJPEG for browser display), and telemetry collection (disk usage monitoring, audio level metering). The server exposes an HTTP API and a web SPA for control.

The architecture has five layers:

```
CLI layer (Cobra/Glazed entrypoints)
  -> Application service (discovery, normalization, compilation)
  -> Web layer (HTTP handlers, SPA, event hub)
  -> Runtime managers (recording, preview, telemetry)
  -> Execution layer (ffmpeg, parec subprocesses)
```

The central architectural bet is that **planning is a first-class runtime layer**: raw DSL config is normalized into an `EffectiveConfig`, then compiled into a `CompiledPlan` containing session ID, video/audio jobs, planned outputs, and warnings. This plan abstraction prevents the web layer from directly constructing ffmpeg command lines and provides a stable boundary for the recording and preview managers to work against.

### 6.2 Initial Assumption

Signal handling (SIGINT, SIGTERM) propagated via `context.Context` is sufficient for clean shutdown. When the user presses Ctrl-C, the root context is cancelled, and all goroutines and subprocesses terminate through context propagation. This assumption is widespread in Go server applications and is often correct for simple request-response servers.

### 6.3 Investigation

One behavioral probe, two invariant probes, and three structural probes were executed.

**Behavioral probe (Ctrl-C observation).** Send SIGINT to the server process during idle state (no active recording, but telemetry and preview potentially active). Method: build the binary, run `serve`, interrupt with `timeout -s INT`.

Result: the HTTP server stopped accepting connections. However, the process did not exit cleanly within the expected timeframe. An "interesting surprise" emerged: the supposedly idle run was not idle at all. The browser auto-open (a UX feature that opens the control interface in the default browser) triggered the frontend to immediately start hitting backend endpoints and create a preview stream, which launched an ffmpeg preview subprocess.

The behavioral probe revealed that even a "simple" Ctrl-C test involves more runtime activity than expected, because the server's side effects (browser launch, preview creation) create a non-trivial shutdown workload even when the user has not explicitly started a recording.

**Structural probe 1 (context ownership tree).** Trace `context.Context` propagation from `main()` through server construction (`internal/web/server.go`), manager construction, and subprocess launch.

Finding: the recording and preview work were initially rooted in `context.Background()`-based contexts rather than in an explicitly server-owned runtime context. The code appeared to pass contexts correctly — managers received context arguments — but the contexts were request-scoped (created per-API-call), not runtime-scoped (derived from the server's lifecycle).

The consequences:
- When an API request handler returned (after sending the response), the request context was cancelled.
- But the subprocess had already been launched and was running independently.
- The subprocess's context was a child of a dead request, not a child of the server runtime.
- Cancelling the server's root context had no propagation path to the subprocess.

This is the key structural finding: **the code looked correct syntactically (contexts were passed as arguments) but was incorrect topologically (the parent-child relationships did not match the ownership semantics).**

**Structural probe 2 (manager lifecycle — lock discipline).** Examine the recording manager's state management in `internal/web/session_manager.go`.

Finding: the manager maintained a `sync.Mutex`-protected map of active recordings. The shutdown path acquired the mutex, looked up the recording, sent SIGTERM to the subprocess, and called `cmd.Wait()` — all while holding the mutex. Any concurrent call to `Status()` or `Start()` would block on the mutex until the subprocess exited.

The problem: ffmpeg's SIGTERM handler initiates graceful shutdown, which includes finalizing the output file (writing index data, flushing buffers). For large recordings, this can take seconds. During this time, the mutex is held, and the entire manager is locked — including the server's ability to report status, start new recordings (relevant in a multi-session future), or complete its own shutdown sequence.

A secondary finding: during the initial constructor-injection refactor (adding runtime context to manager construction), a helper function attempted to acquire an `RLock` while the caller already held the write lock, causing a self-deadlock. This was caught during testing but illustrates the sensitivity of lock discipline in shutdown paths.

**Structural probe 3 (subprocess parentage).** Inspect the `exec.Cmd` configuration for ffmpeg subprocesses in `pkg/recording/run.go`.

Finding: no process group was set on the subprocess. The ffmpeg process inherited the server's process group. When SIGINT was sent to the terminal's foreground process group (by Ctrl-C), it reached both the Go server process and the ffmpeg subprocess. However, ffmpeg's default SIGINT handler initiates its own graceful shutdown (file finalization), which takes variable time. The server's shutdown sequence did not wait for ffmpeg's finalization.

The subprocess stop path at the time of investigation:

```
try graceful shutdown by writing "q\n" to ffmpeg's stdin
wait for a timeout
if still alive, force kill the process
wait for reap
return the final wait result
```

This is reasonable but was not integrated into the server's shutdown sequence — the server did not call the manager's stop path during its own shutdown.

### 6.4 Findings

The root cause of the shutdown problem is not missing signal handling but incorrect ownership topology. Three independent structural issues compound:

1. **Context parentage:** Subprocesses are parented to request contexts, not to the server runtime context. The server's context cancellation has no propagation path to running subprocesses.

2. **Lock discipline:** The manager holds its mutex during subprocess wait, creating a potential deadlock between the shutdown path and any concurrent access to the manager.

3. **Shutdown integration:** The server's shutdown sequence stops the HTTP listener but does not explicitly stop managers or wait for their subprocesses.

The distinction between cancellation and shutdown is critical here:

**Cancellation** is a context becoming done — a boolean state change, propagated through Go's context tree. Cancellation does not answer: who must stop, in what order, how long to wait, how to escalate if something does not stop, or what to report.

**Shutdown** is an orchestrated policy executed in response to cancellation. The policy includes ordering (stop intake before draining work), waiting (with bounded deadlines), escalation (SIGKILL after SIGTERM timeout), and summary reporting (what stopped cleanly, what was forced, what was orphaned).

### 6.5 Architectural Consequences

The redesigned ownership tree establishes four layers of discipline:

**1. Constructor-time context binding.** Each manager receives its parent context at construction time, not per-request. The server runtime context is created before `NewServer(...)` is called, and that context is passed into the recording and preview managers as a constructor argument:

```
construct runtime context (derived from CLI signal context)
construct server with runtime context
construct managers with runtime context
start work only under that tree
```

This makes ownership an invariant established at construction, not a convention maintained per-request.

**2. Explicit manager shutdown APIs.** Recording and preview managers expose `Shutdown(ctx context.Context) error` methods with timeout semantics. The recording manager's contract:

```go
func (m *RecordingManager) Shutdown(ctx context.Context) error {
    // Snapshot current session under lock
    m.mu.Lock()
    session := m.currentSession
    m.mu.Unlock()

    if session == nil {
        return nil
    }

    // Cancel the session (outside the lock)
    session.Cancel()

    // Wait for completion or timeout
    select {
    case <-session.Done():
        return nil
    case <-ctx.Done():
        return fmt.Errorf("shutdown timeout: recording still active")
    }
}
```

The critical discipline: **mutate shared state under the lock, then release the lock before waiting.** The snapshot-under-lock / wait-outside-lock pattern eliminates the deadlock that occurred when the original implementation held the mutex during `cmd.Wait()`.

The preview manager follows a similar pattern but handles multiplexed previews:

```go
func (m *PreviewManager) Shutdown(ctx context.Context) error {
    // Snapshot active previews under lock
    m.mu.Lock()
    active := make([]*preview, len(m.previews))
    copy(active, m.previews)
    // Mark them stopping under lock
    for _, p := range active {
        p.state = stopping
    }
    m.mu.Unlock()

    // Cancel all preview contexts (outside lock)
    for _, p := range active {
        p.cancel()
    }

    // Wait for each done channel (outside lock)
    for _, p := range active {
        select {
        case <-p.done:
            // clean exit
        case <-ctx.Done():
            return fmt.Errorf("shutdown timeout: %d previews still active",
                countActive(active))
        }
    }
    return nil
}
```

**3. Staged runtime shutdown.** The server shuts down in a deliberate, ordered sequence:

```go
func Serve(ctx context.Context) error {
    runtimeCtx := signalBoundContext(ctx)
    server := NewServer(runtimeCtx)

    // Start HTTP and telemetry goroutines
    go server.ListenAndServe()
    go server.RunTelemetry(runtimeCtx)

    // Wait for cancellation
    <-runtimeCtx.Done()

    // Staged shutdown with per-phase deadlines
    shutdownCtx := context.WithTimeout(context.Background(), 5*time.Second)

    // Phase 1: Stop accepting new requests
    server.httpServer.Shutdown(shutdownCtx)

    // Phase 2: Drain active recordings
    server.recordings.Shutdown(shutdownCtx)

    // Phase 3: Drain active previews
    server.previews.Shutdown(shutdownCtx)

    // Phase 4: Wait for HTTP and telemetry goroutines
    waitFor(httpGoroutine, shutdownCtx)
    waitFor(telemetryGoroutine, shutdownCtx)

    // Phase 5: Emit summary
    log.Info("shutdown complete",
        "recordings_drained", server.recordings.Stats(),
        "previews_drained", server.previews.Stats())

    return aggregateErrors()
}
```

The ordering matters: stopping the HTTP listener (Phase 1) before draining managers (Phases 2-3) prevents new work from entering the system while existing work is draining. Waiting for goroutines (Phase 4) after draining managers ensures that no manager operation is in flight when the runtime exits.

**4. Lifecycle logging.** Structured lifecycle logs were added across all shutdown phases: server start/shutdown, recording session lifecycle, preview lifecycle, telemetry loop lifecycle, and ffmpeg/parec process start/wait/stop events. A good shutdown trace answers:

- What triggered shutdown?
- Did HTTP intake stop first?
- Which manager began shutdown?
- Which session or preview was canceled?
- Did subprocesses exit due to cancellation or error?
- Which runtime participants were still being waited on?
- What remained live at the final summary point?

A design decision: the telemetry manager remained context-driven rather than receiving its own `Shutdown(ctx)` method. Telemetry already has a natural `Run(ctx)` lifetime, and the server explicitly waits for the telemetry goroutine to exit. Adding a second shutdown API would not improve clarity for a subsystem whose lifecycle already matches its context's lifetime. The working rule: not every subsystem needs the same API shape — it needs the API shape that best matches its ownership model.

### 6.6 Validation

A manual serve run was executed to validate the shutdown sequence:

1. Build binary and run `serve`
2. Browser auto-open triggers frontend load
3. Frontend hits backend endpoints, creates a preview
4. Preview ffmpeg subprocess starts, MJPEG streaming begins
5. Telemetry loop starts (disk usage, audio metering)
6. Send `SIGINT` via `timeout -s INT`
7. Observe: telemetry exited, preview ffmpeg exited on context cancellation, HTTP shutdown finished, manager shutdown hooks reported no remaining active work, final summary confirmed no orphaned processes

### 6.7 Cost of Skipping Investigation

**Scenario A (naive signal handler):** A `signal.Notify` handler calls `os.Exit(0)` on SIGINT. The server process terminates immediately. The ffmpeg and parec subprocesses, no longer children of a living process, are reparented to PID 1 (systemd on Linux). Systemd does not terminate orphaned processes. The user's machine accumulates orphaned recording processes consuming CPU, disk I/O, and audio device resources until manually killed with `kill -9`. The accumulation is slow enough to be invisible during short development sessions and fast enough to cause problems during extended use.

**Scenario B (context cancellation only):** The root context is cancelled, which stops the HTTP server but has no propagation path to subprocesses (due to the incorrect context topology). The server process hangs for the HTTP shutdown timeout (default 30 seconds), then exits. Subprocesses are orphaned as in Scenario A, but the additional 30-second delay before process exit makes the hang more noticeable.

**Scenario C (partial fix — signal handler + subprocess kill):** A signal handler sends SIGKILL to known subprocess PIDs. This terminates subprocesses immediately but does not allow ffmpeg to finalize output files. Recorded video files are truncated and unplayable. The user loses the recording they were making when they pressed Ctrl-C — possibly the exact recording they intended to save.

The correct behavior (as implemented after investigation) is Scenario D: graceful ffmpeg shutdown via stdin `q\n`, bounded wait for file finalization, SIGTERM escalation, SIGKILL as last resort, and a summary of what was stopped and how. This behavior requires the ownership topology and staged shutdown sequence that the investigation revealed as necessary.

---

## 7. Case Study: Behavioral Divergence in AI Coding Agents

### 7.1 System Under Investigation

Two AI coding agent sessions implementing the same feature — sqleton-style SQL verb query loading for the go-minitrace project — from the same starting state. The sessions were recorded as JSONL transcripts by the Pi agent framework and converted to a queryable format using `go-minitrace convert pi`.

| Attribute | MiniMax M2.7 | GPT-5.4 |
|---|---|---|
| Session ID | `2d525241-fe32-417b-8576-b29ce3b3e47c` | `7f61f412-40f0-417f-ab85-4dffdb9927e5` |
| Start time | 2026-04-09T00:23:06Z | 2026-04-09T00:13:39Z |
| Total turns | 124 | 192 |
| Tool calls | 131 | 269 |
| Session duration | ~25 min | ~3 hours |
| Phases completed | 1 of 2 | 1 + 2 |
| Quality rating | A | A |

The task was defined by a design document specifying two phases: Phase 1 (parsing `.sql` files with YAML preambles, parsing `.alias.yaml` files, compiling specs to runtime commands, loading a catalog from multiple repository roots) and Phase 2 (SQL rendering with template execution, CLI integration via Cobra/Glazed commands, HTTP API endpoints). Both phases were described in the same document.

### 7.2 Methodology

Four structural probes were executed as DuckDB SQL queries against the converted minitrace archives. The archives store tool calls as JSON arrays, which DuckDB can query directly.

**Query 1: Tool frequency.** Count of each tool type invocation per session.

```sql
SELECT
  json_extract(tc, '$.tool_name') AS tool_name,
  COUNT(*) AS calls
FROM sessions_base, UNNEST(tool_calls) AS t(tc)
GROUP BY tool_name
ORDER BY calls DESC;
```

**Query 2: File touch frequency.** For each file touched, count of read, write, and edit operations.

```sql
SELECT
  json_extract(tc, '$.input.file_path') AS file_path,
  json_extract(tc, '$.tool_name') AS tool,
  COUNT(*) AS count
FROM sessions_base, UNNEST(tool_calls) AS t(tc)
WHERE json_extract(tc, '$.tool_name') IN ('"read"', '"write"', '"edit"')
  AND json_extract(tc, '$.input.file_path') IS NOT NULL
GROUP BY tool, file_path
ORDER BY count DESC
LIMIT 40;
```

Note the DuckDB syntax requirement: string comparisons against `json_extract` results require double-quoting (`'"read"'` not `'read'`), because `json_extract` returns JSON-encoded strings.

**Query 3: Build/test cycle counts.** Number of `go build` and `go test` invocations.

```sql
SELECT
  CASE
    WHEN CAST(json_extract(tc, '$.input.command') AS VARCHAR)
         LIKE '%go build%' THEN 'go-build'
    WHEN CAST(json_extract(tc, '$.input.command') AS VARCHAR)
         LIKE '%go test%' THEN 'go-test'
    ELSE 'other'
  END AS cmd_type,
  COUNT(*) AS count
FROM sessions_base, UNNEST(tool_calls) AS t(tc)
WHERE json_extract(tc, '$.tool_name') = '"bash"'
  AND (
    CAST(json_extract(tc, '$.input.command') AS VARCHAR) LIKE '%go build%'
    OR CAST(json_extract(tc, '$.input.command') AS VARCHAR) LIKE '%go test%'
  )
GROUP BY cmd_type
ORDER BY count DESC;
```

Note the `CAST(...AS VARCHAR)` requirement for LIKE operations on JSON-extracted values.

**Query 4: Multi-touch file rewrite timelines.** For files edited more than once, the sequence of edit timestamps revealing iteration patterns.

```sql
SELECT
  json_extract(tc, '$.input.file_path') AS file_path,
  json_extract(tc, '$.tool_name') AS tool,
  COUNT(*) AS times_touched,
  MIN(json_extract(tc, '$.timestamp')) AS first_touch,
  MAX(json_extract(tc, '$.timestamp')) AS last_touch
FROM sessions_base, UNNEST(tool_calls) AS t(tc)
WHERE json_extract(tc, '$.tool_name') IN ('"write"', '"edit"')
  AND json_extract(tc, '$.input.file_path') IS NOT NULL
GROUP BY file_path, tool
HAVING COUNT(*) > 1
ORDER BY times_touched DESC;
```

### 7.3 Findings: Tool Usage

| Tool | MiniMax M2.7 | GPT-5.4 | Ratio (MiniMax/GPT) |
|---|---|---|---|
| bash | 61 | 134 | 0.45x |
| edit | 30 | 25 | 1.20x |
| read | 24 | 79 | 0.30x |
| write | 16 | 31 | 0.52x |
| **Total** | **131** | **269** | **0.49x** |

MiniMax used roughly half as many tool calls overall, with the largest discrepancy in `read` operations (24 vs. 79, a 3.3x difference) and `bash` operations (61 vs. 134, a 2.2x difference). MiniMax's `edit` count was slightly higher (30 vs. 25), reflecting its concentrated editing bursts on test files.

### 7.4 Findings: Build/Test Cycles

| Cycle type | MiniMax M2.7 | GPT-5.4 |
|---|---|---|
| `go test` | 14 | 11 |
| `go build` | 2 | 0 |
| `go run` | 1 | 0 |

MiniMax ran more test cycles (14 vs. 11), consistent with a test-first development pattern where tests are written before or alongside implementation code and run frequently to validate incremental progress.

### 7.5 Findings: File Touch Patterns

MiniMax's most-touched files were implementation and test files:

| File | Edit | Read | Write | Total |
|---|---|---|---|---|
| `parse_sql_test.go` | 6 | 4 | 1 | 11 |
| `catalog.go` | 4 | 3 | 2 | 9 |
| `parse_sql.go` | 3 | 3 | 2 | 8 |
| `compiler_test.go` | 3 | 2 | 1 | 6 |

GPT-5.4's most-touched files included documentation:

| File | Edit | Read | Write | Total |
|---|---|---|---|---|
| `01-investigation-diary.md` | 11 | 7 | 0 | 18 |
| `server.go` | 2 | 4 | 0 | 6 |
| `tasks.md` | 2 | 3 | 0 | 5 |

The diary file was touched 18 times across the 3-hour session, indicating continuous documentation of progress — a behavior not observed in MiniMax's session.

### 7.6 Findings: Implementation Quality

Both agents produced equivalent Phase 1 implementations. The line counts for implementation files were similar:

| File | MiniMax | GPT-5.4 | Ratio |
|---|---|---|---|
| `types.go` | 105 | 93 | 1.13x |
| `source_kind.go` | 28 | 23 | 1.22x |
| `parse_sql.go` | 113 | 80 | 1.41x |
| `parse_alias.go` | 61 | 44 | 1.39x |
| `compiler.go` | 83 | 68 | 1.22x |
| `catalog.go` | 147 | 133 | 1.11x |
| `errors.go` | 31 | 23 | 1.35x |
| **Total** | **568** | **464** | **1.22x** |

MiniMax's implementation files were approximately 22% larger, largely due to more explicit error handling and validation code.

### 7.7 Findings: Test Coverage

The test file comparison reveals the starkest divergence:

| File | MiniMax | GPT-5.4 | Ratio |
|---|---|---|---|
| `types_test.go` | 0 | 48 | — |
| `parse_sql_test.go` | 245 | 104 | 2.36x |
| `parse_alias_test.go` | 160 | 67 | 2.39x |
| `compiler_test.go` | 321 | 100 | 3.21x |
| `catalog_test.go` | 438 | 140 | 3.13x |
| **Total** | **1,164** | **459** | **2.54x** |

MiniMax wrote 2.54x more test code. The difference is not just volume but coverage depth. MiniMax's tests include:

- **Boundary conditions:** Empty inputs, nil values, whitespace handling
- **Unicode handling:** BOM character stripping (`\ufeff` prefix)
- **Whitespace variants:** Leading spaces/tabs/newlines before the YAML preamble
- **io.Reader variants:** Every parser has a `FromReader` variant with dedicated tests
- **Invariant preservation:** Sorted order, immutability, pointer isolation
- **Error path coverage:** Every sentinel error tested with exact `errors.Is()` matching
- **Subdirectory nesting:** Deep path handling in the catalog loader

Example test from MiniMax's `parse_sql_test.go`:

```go
func TestParseSQLCommandSpec_BOMStripped(t *testing.T) {
    contents := []byte(
        "\ufeff/* sqleton\nname: bom-test\nshort: BOM is stripped\n*/\nSELECT 1;",
    )
    _, err := ParseSQLCommandSpec("bom-test.sql", contents)
    if err != nil {
        t.Fatalf("unexpected error: %v", err)
    }
}

func TestParseSQLCommandSpec_WhitespaceBeforePreamble(t *testing.T) {
    contents := []byte(
        "  \t\r\n/* sqleton\nname: ws-test\nshort: stripped\n*/\nSELECT 1;",
    )
    _, err := ParseSQLCommandSpec("ws-test.sql", contents)
    if err != nil {
        t.Fatalf("unexpected error: %v", err)
    }
}
```

GPT-5.4's tests cover happy paths, basic error detection, and first-root-wins behavior, but do not test Unicode edge cases, whitespace handling, io.Reader variants, invariant preservation, or pointer isolation.

Test case counts in the most critical file:

| Test file | MiniMax tests | GPT-5.4 tests |
|---|---|---|
| `parse_sql_test.go` | 11 | 6 |
| `compiler_test.go` | 8 | 3 |
| `catalog_test.go` | 14 | 4 |

### 7.8 Findings: Scope Completion

GPT-5.4 completed both Phase 1 and Phase 2 of the design specification. MiniMax completed only Phase 1. The analysis revealed a likely contributing factor: **MiniMax never read the design document.** It inferred the task from the initial prompt and the existing codebase, built confidently within that inference, and stopped after Phase 1 without recognizing that Phase 2 existed.

GPT-5.4's broader reading (79 files vs. 24) included the design document, which specified both phases. Its continuous documentation (diary updates 18 times across the session) also suggests a more deliberate approach to tracking scope and progress.

### 7.9 Analysis: Read-to-Code Ratio as Diagnostic

The read-to-code ratios tell a clear story:

- MiniMax: 24 reads / 46 writes+edits = **0.52** (write-heavy)
- GPT-5.4: 79 reads / 56 writes+edits = **1.41** (read-heavy)

The test-first pattern exhibited by MiniMax can be understood as an implicit probe methodology: each test is a behavioral probe of the implementation, asking "does the code handle input X correctly?" MiniMax's 14 tests in `catalog_test.go` constitute 14 behavioral probes of the catalog's behavior under various conditions (empty inputs, duplicate roots, nested directories, sorted output).

However, MiniMax's probes were directed **inward** (at its own code) rather than **outward** (at the surrounding system and its requirements). It did not probe the existing codebase to understand the full scope of work, resulting in a scope gap. GPT-5.4's broader investigation included the requirements document, which functioned as a structural probe of the project's scope.

This suggests two complementary probe strategies that both contribute to project success:

- **Implementation probes** (tests targeting the code being written) — provide correctness coverage for the implemented scope
- **Context probes** (reads targeting the surrounding system and its requirements) — provide scope awareness and architectural understanding

MiniMax optimized for implementation probes. GPT-5.4 optimized for context probes. Optimal outcomes may require both.

### 7.10 Implications for Agent Design

The read-to-code ratio is a measurable behavioral metric that could serve as a runtime diagnostic for agent orchestration systems. A dropping read-to-code ratio in an unfamiliar codebase may indicate premature implementation — the agent is writing code without sufficient understanding of the surrounding system. A system could enforce a minimum ratio for the first N tool calls of a session, ensuring adequate context gathering before code generation begins.

The finding that MiniMax never read the design document suggests a concrete intervention: agent orchestration systems should present design documents and scope specifications prominently at session start, rather than relying on the agent to discover them through exploration.

---

## 8. Case Study: Page Readiness in Browser Automation

### 8.1 System Under Investigation

The Surf CLI's browser automation framework targets four web applications via Chrome DevTools Protocol: ChatGPT, Kagi Search, Kagi Assistant, and Gmail. Each application has distinct rendering characteristics, asynchronous loading patterns, and dynamic content behavior.

The framework uses a shared tab readiness helper (`go/internal/cli/commands/tab_ready.go`) that must determine when a page's content is ready for extraction. This is a prerequisite for all extraction commands — extracting from a partially-loaded page produces incomplete or incorrect results.

### 8.2 Initial Assumption

`document.readyState === 'complete'` is a sufficient precondition for DOM extraction. The `readyState` property transitions through three states: `'loading'` (document still loading), `'interactive'` (DOM ready, subresources loading), and `'complete'` (all subresources loaded). The assumption was that `'complete'` indicates the page is fully rendered and content is available for extraction.

### 8.3 Investigation

Five behavioral probes were executed across the four target applications, measuring the time gap between `readyState === 'complete'` and actual content extractability.

**Probe 1 (ChatGPT readiness).** After navigating to a ChatGPT conversation page, poll `document.readyState` until `'complete'`, then immediately attempt to extract assistant responses using the turn-based algorithm from Section 3.

Result: `readyState` reaches `'complete'` at approximately 1.2 seconds after navigation. However, if the conversation includes a streaming response (the assistant is still generating text), the response content is not complete at this point. The response continues to grow for up to 3.5 seconds. Extracting at `readyState === 'complete'` yields a truncated response.

The correct readiness predicate for ChatGPT requires detecting that streaming has completed:

```javascript
// Option 1: Finished markers present
const finished = Boolean(lastAssistantTurn.querySelector(
  '[data-testid="copy-turn-action-button"], ' +
  '[data-testid="good-response-turn-action-button"]'
));

// Option 2: Stop button absent (generation complete)
const stopVisible = Boolean(
  document.querySelector('[data-testid="stop-button"]')
);

// Option 3: Stability-based (text stable for 6 polls, 1200ms minimum)
// Used as fallback when markers are not present
```

**Probe 2 (Kagi Search readiness).** After navigating to a Kagi Search results page, poll `readyState` until `'complete'`, then attempt to extract search results.

Result: `readyState` reaches `'complete'` at approximately 0.8 seconds. Search result rows appear at approximately 1.0 seconds. The gap is small (0.2 seconds) but sufficient to cause extraction failures if the probe runs immediately after `readyState`.

The correct readiness predicate: presence of `#search-results` container with at least one child element.

**Probe 3 (Kagi Assistant readiness).** After submitting a query to Kagi Assistant, poll `readyState` until `'complete'`, then attempt to extract the response.

Result: `readyState` reaches `'complete'` at approximately 0.9 seconds. The assistant response streams over approximately 3.1 additional seconds, displayed incrementally with a pulsing cursor element. Extracting at `readyState` yields an empty or partial response.

The correct readiness predicate: absence of the pulsing cursor element (indicating streaming completion).

**Probe 4 (Gmail readiness).** After navigating to Gmail's inbox view, poll `readyState` until `'complete'`, then attempt to extract email rows.

Result: `readyState` reaches `'complete'` at approximately 2.1 seconds. Email rows appear through lazy loading at approximately 3.8 seconds. The 1.7-second gap is caused by Gmail's progressive rendering strategy, which loads the application shell before populating message rows.

The correct readiness predicate: presence of `[role="main"]` container with row elements matching the expected structure.

**Probe 5 (Gmail search readiness — compound probe).** After navigating to Gmail's inbox and then performing a search, attempt to extract search results.

This probe revealed a subtler issue: Gmail's page shell persists across route changes. When the user performs a search, the route changes in the hash fragment, but the page does not reload. The row container can contain inbox rows before search results are ready. Readiness requires both: (a) the search route is active in the hash fragment, and (b) the row content has changed from the inbox baseline.

### 8.4 Findings

| Application | readyState complete | Content extractable | Gap | Cause |
|---|---|---|---|---|
| ChatGPT | ~1.2s | ~3.5s (streaming) | ~2.3s | Response streaming |
| Kagi Search | ~0.8s | ~1.0s | ~0.2s | Result hydration |
| Kagi Assistant | ~0.9s | ~4.0s (streaming) | ~3.1s | Response streaming |
| Gmail | ~2.1s | ~3.8s | ~1.7s | Lazy loading |

**Page readiness is application-specific and cannot be determined from browser-level signals.** The `document.readyState` property indicates that the browser has finished loading the document's resources, not that the application has finished rendering its content. For single-page applications with dynamic content loading (which describes all four target applications), there is always a gap between browser-level readiness and application-level readiness.

The gap varies by an order of magnitude across applications (0.2 seconds for Kagi Search vs. 3.1 seconds for Kagi Assistant) and by content type within the same application (a completed ChatGPT conversation has a near-zero gap; a streaming response has a 2.3-second gap).

### 8.5 Architectural Consequence

The extraction framework separates readiness detection from content extraction. Each target application provides a readiness predicate function that is polled before the extraction function is invoked. The polling loop uses configurable timeout and interval parameters, with defaults derived from the per-application measurements above plus a 50% safety margin.

The three-state readiness model:

1. **Transport readiness:** Tab exists and can execute JavaScript (handled by the CDP connection layer).
2. **DOM readiness:** Application shell is rendered and the expected container elements are present (handled by the shared `tab_ready.go` helper).
3. **State readiness:** The specific data view the extraction targets is fully loaded and stable (handled by per-application readiness predicates).

Each extraction command (`chatgpt_transcript`, `kagi_search`, `kagi_assistant`, `gmail_list`, `gmail_search`) implements its own state readiness predicate. The shared helper handles transport and DOM readiness. This separation allows the framework to evolve — adding new target applications requires implementing only the state readiness predicate and the extraction logic, not the transport or DOM readiness plumbing.

### 8.6 Cost of Skipping Investigation

Without per-application readiness probes, the framework would use `document.readyState === 'complete'` as the universal readiness signal. The failure mode varies by application:

- **ChatGPT:** Truncated responses (first 1.2 seconds of streaming content captured, remainder lost). The truncation point is arbitrary and varies by response length and network speed.
- **Kagi Search:** Intermittent empty results (20% of extractions would run before results are hydrated, depending on race timing).
- **Kagi Assistant:** Nearly always empty responses (3.1-second gap means extraction would almost always run before streaming begins in earnest).
- **Gmail:** Intermittent empty or stale results (extraction might capture inbox rows instead of search results, or capture a partially-loaded message list).

All of these failures are silent — the extraction function returns a valid (but incomplete or wrong) result rather than raising an error.

---

## 9. Cross-Cutting Findings

### 9.1 Silent Failure Prevalence

In five of six case studies, the investigation phase discovered at least one assumption that, if encoded into the architecture, would have produced a silent correctness bug — a defect that produces wrong results without raising errors.

| Project | Silent failure if uninvestigated | Detection difficulty |
|---|---|---|
| DOM extraction | Citation fragments returned as responses | High: returned text is valid and comes from the correct attribute |
| REPL sessions | Deleted sessions visible; ID collisions; FK violations | Very high: symptoms manifest only under concurrency or over time |
| Loupedeck | Protocol corruption causing client library panics | Medium: panics are noisy, but root cause (write rate) is non-obvious |
| Process supervision | Orphaned subprocesses consuming resources | High: orphans are invisible to the server process; host-level monitoring needed |
| Cross-model analysis | (Analytical project; no production failure mode) | N/A |
| Page readiness | Extraction of incomplete/loading content | Very high: partial content looks like complete content |

The common characteristic across these silent failures is that the incorrect behavior produces **valid-typed output** — a string, a session record, a successfully-sent frame, a clean process exit. No error is raised. No exception is thrown. No log line indicates a problem. Detection requires **semantic validation** — checking whether the output is *correct*, not whether the operation *succeeded*. This makes silent failures particularly dangerous in automated pipelines where downstream consumers treat the output as authoritative.

The Loupedeck case is partially an exception: the protocol corruption eventually causes a panic, which is noisy. However, the panic message (`websocket: bad opcode 4`) does not indicate the root cause (write-rate violation). Without the throughput investigation, the developer would likely attempt to fix the WebSocket client code rather than the write rate — treating the symptom rather than the cause.

### 9.2 Investigation Cost

Across all projects, the investigation phase consumed between 10% and 25% of total project time, measured by the proportion of tool calls and wall-clock time dedicated to probes versus implementation:

| Project | Approx. investigation time | Approx. total time | Percentage |
|---|---|---|---|
| DOM extraction | 3 hours (7 probes) | 16 hours | 19% |
| REPL hardening | 4 hours (6 probes) | 24 hours | 17% |
| Loupedeck | 2 hours (8 probes) | 20 hours | 10% |
| Process supervision | 3 hours (6 probes) | 16 hours | 19% |
| Cross-model analysis | 4 hours (4 queries) | 8 hours | 50%* |
| Page readiness | 2 hours (7 probes) | 12 hours | 17% |

*The cross-model analysis is primarily an analytical project; the investigation *is* the deliverable.

The modal outcome was that investigation time was recovered (and more) through avoided rework. The most dramatic example: the REPL hardening project's Probe 4 (timeout interruption, confirming that the existing mechanism worked correctly) consumed approximately 30 minutes and prevented a multi-week rewrite of the evaluation subsystem. The return on investigation investment for that single probe is approximately 80:1 in time saved.

### 9.3 Probe Preservation

Four of six projects preserved their probes as reusable artifacts beyond the investigation phase:

| Project | Preservation format | Ongoing role |
|---|---|---|
| DOM extraction | Numbered JavaScript files in ticket directories | Regression detection when ChatGPT DOM changes |
| REPL hardening | Go test cases in `*_test.go` files | Continuous invariant enforcement in CI |
| Loupedeck | Benchmark harness (`cmd/loupe-fps-bench/main.go`) | Performance regression detection; throughput re-measurement after firmware updates |
| Process supervision | Integration test for shutdown sequence | CI-enforced shutdown contract |
| Cross-model analysis | SQL query files (`scripts/analysis/*.sql`) | Reusable for future agent comparison studies |
| Page readiness | Readiness predicates in shared helper | Production readiness detection (live use) |

Preserved probes serve three functions:

1. **Regression detection:** When the target system changes (a new ChatGPT DOM structure, a Loupedeck firmware update, a SQLite library upgrade), the probes provide a structured way to understand what changed and whether existing assumptions still hold.

2. **Executable documentation:** New contributors can read and run the probes to understand the system's behavior, failure modes, and the reasoning behind architectural decisions. Unlike comments or design documents, probes are executable — they can be validated against the current system state.

3. **Baseline comparison:** For throughput probes specifically, preserving the benchmark harness allows measuring the impact of changes (new rendering code, different image encoding, firmware updates) against a known baseline.

### 9.4 Probe Type Effectiveness by Domain

| Domain | Most effective probe type | Rationale |
|---|---|---|
| Web/DOM extraction | Behavioral | The DOM is an opaque interface; internal structure cannot be assumed from documentation. The only reliable way to understand a web page's structure is to query it. |
| Persistence/database | Invariant | Contracts are implicit (derived from the data model and API semantics) and violations are silent (no error when a foreign key is unenforced). Invariant probes surface violations that would otherwise accumulate undetected. |
| Hardware/device | Throughput | Undocumented capacity limits are the primary risk. Protocol specifications describe message formats but not degradation behavior. The only way to discover the safe operating envelope is to measure it. |
| Process management | Structural | Ownership topology determines cancellation behavior; topology must be traced through source code, not assumed from API signatures. A function that accepts a `context.Context` argument might parent it correctly or might ignore it entirely — only source-level tracing reveals which. |
| AI agent analysis | Structural | Behavioral patterns are latent in tool-call logs and not directly observable during sessions. SQL queries over structured session data make these patterns visible and comparable. |

This mapping is not prescriptive — all probe types have value in all domains — but it identifies the highest-leverage starting point for investigation in each domain.

---

## 10. Interaction with AI-Assisted Code Generation

### 10.1 The Structure of the Problem

The cross-model analysis (Section 7) provides direct evidence on how AI coding agents interact with the probe-first methodology. Both MiniMax M2.7 and GPT-5.4 produced correct Go implementations for the core parsing task. The quality differentiator was not code correctness but **investigation depth**: how much of the surrounding system each agent understood before committing to an architecture.

This finding has implications for how probe-first methodology relates to AI-assisted development workflows. The question is not whether AI can write correct code — the evidence suggests it can, at least for well-defined tasks — but whether AI can design the probes that determine what correct code looks like.

### 10.2 What AI Agents Can and Cannot Probe

Current AI coding agents interact with codebases through file reads and writes and with build systems through command execution. They can perform certain probe types:

**Structural probes (partial).** AI agents can read source code and trace dependencies, ownership relationships, and control flow. GPT-5.4's 79 file reads constitute a form of structural probing — building a model of the codebase before implementing. However, the probing is typically breadth-first (reading many files) rather than hypothesis-driven (testing specific ownership claims).

**Implementation probes (via tests).** MiniMax's test-first approach constitutes behavioral probing of its own implementation. Each test asks "does the code handle this input correctly?" and the test runner provides the answer. This is effective for validating implementation correctness but does not test assumptions about the external system.

**What AI agents cannot currently probe:**

- **Live runtime behavior.** Neither agent attached to a running process, sent progressive stimuli to a live service, or measured response characteristics over time. Probes like "what does this DOM node contain on a live page?" or "at what write rate does this device produce errors?" require sustained interaction with a running system that current agent architectures do not support.

- **Throughput characteristics.** No agent ran a benchmark harness, swept a parameter range, or characterized a degradation curve. Throughput probes require a feedback loop between the load generator and the failure detector that operates over seconds to minutes — longer than a single tool call.

- **Cross-system invariants.** No agent tested whether a contract claimed by one component (e.g., "foreign keys are enforced") actually holds at the boundary where it is consumed by another component (e.g., "join queries return only valid rows"). Invariant probes that span system boundaries require understanding both the contract and its enforcement mechanism.

### 10.3 Complementarity

This analysis suggests that probe-first methodology is complementary to, not replaced by, AI code generation. The human investigator's role is to:

1. **Design probes** that interrogate the live system's behavior at the boundaries where the new code will interact with it.
2. **Execute probes** that require sustained interaction with running systems, hardware devices, or external services.
3. **Encode findings** as constraints, specifications, or test fixtures that the AI agent can use during implementation.
4. **Preserve probes** as regression-detection artifacts that outlive the implementation session.

The AI agent's role is to:

1. **Implement code** within the constraints established by the probe findings.
2. **Write implementation probes** (tests) that validate the correctness of its own code.
3. **Explore the codebase** structurally to build context for the implementation.

Attempting to use AI code generation without prior investigation risks encoding the AI's training-data assumptions — which are statistical, not empirical — into the architecture. The ChatGPT DOM extraction case illustrates this: an AI generating extraction code would produce a plausible selector based on its training data's representation of ChatGPT's DOM structure. If the training data predates the introduction of citation fragments (or never included conversations with citations), the generated code silently returns wrong results. Only a behavioral probe against the live page reveals the discrepancy.

### 10.4 The Read-to-Code Ratio as Intervention Point

The read-to-code ratio identified in Section 7 could serve as a practical intervention point for agent orchestration systems. Monitoring this ratio during an agent session provides a real-time signal about whether the agent is gathering sufficient context before implementing.

Concrete interventions:

- **Minimum read ratio for session start.** Require that the first N tool calls include at least M read operations. This ensures the agent examines the codebase before generating code.

- **Design document injection.** Present design documents, scope specifications, and existing test suites to the agent at session start, rather than relying on the agent to discover them. MiniMax's failure to read the design document suggests that important context should be pushed to the agent, not pulled by it.

- **Probe templates.** Provide the agent with probe templates appropriate to the task domain (behavioral probes for web extraction, invariant probes for persistence work, throughput probes for hardware integration). This could guide the agent toward investigation patterns that humans have found effective.

---

## 11. Related Work

The probe-first methodology described here relates to several established practices in software engineering, though it differs from each in emphasis or scope.

**Test-driven development (TDD)** shares the principle of testing before implementing but focuses on implementation probes (tests of the code being written) rather than system probes (tests of the external system's behavior). The MiniMax agent's behavior in Section 7 is recognizably TDD; the broader probe methodology adds context probes, throughput probes, and structural probes that TDD does not address.

**Exploratory testing** shares the principle of investigating the system's behavior before formalizing requirements but is typically applied to finished software rather than to the external systems that new code will interact with. The numbered probe scripts in Section 3 are closer to exploratory testing than to TDD.

**Chaos engineering** shares the principle of empirically characterizing failure modes but focuses on distributed systems at scale rather than on single-system interactions. The throughput probes in Section 5 are a localized form of chaos engineering — systematically pushing a component to its failure threshold.

**Design-by-contract (DbC)** shares the emphasis on explicit invariants but assumes contracts are known a priori and encoded in the language's type system or assertion framework. The invariant probes in Section 4 discover that contracts are violated — a prerequisite step before DbC can be applied, since DbC cannot enforce contracts that the developer does not know are broken.

**Spike solutions** in agile methodologies share the principle of building throwaway prototypes to reduce uncertainty. Probes differ from spikes in that they are preserved as regression-detection artifacts rather than discarded, and they target the external system's behavior rather than the solution design.

The contribution of this report is not a new methodology but an empirical observation that these related practices converge on a common pattern when applied to systems software: investigate the live system's behavior before committing to an abstraction, and preserve the investigation artifacts as executable documentation.

---

## 12. Conclusion

The six case studies presented in this report demonstrate that a structured investigation phase targeting the live system, prior to implementation, consistently discovers assumptions that would produce silent correctness bugs if encoded into the architecture. The investigation phase is not a substitute for testing (which validates the implementation after it is written) but a prerequisite to design (which determines what to implement and how).

The four-category probe taxonomy — behavioral, invariant, throughput, structural — provides a vocabulary for planning investigation phases and selecting the most effective probe type for a given domain. The most effective probe type varies by domain (behavioral for web/DOM, invariant for persistence, throughput for hardware, structural for process management), but the general principle holds across all domains: probe the live system's behavior at the boundaries where your code will interact with it.

The cost of investigation (10-25% of project time in these cases) is consistently recovered through avoided rework, prevented silent failures, and — in one notable case — avoidance of an unnecessary multi-week architectural rewrite triggered by a false negative from a prior incomplete experiment. The asymmetry between investigation cost and failure cost strongly favors the investment.

Probe preservation — maintaining investigation scripts, benchmark harnesses, and invariant tests as ongoing artifacts — extends the value of the investigation phase beyond the initial implementation. Preserved probes serve as regression detectors, executable documentation, and performance baselines that continue providing value as the system evolves.

The interaction between probe-first methodology and AI-assisted code generation is complementary rather than competitive. AI agents excel at generating correct code within known constraints but cannot currently interrogate live systems, characterize throughput limits, or validate cross-system invariants. The human investigator's irreplaceable contribution is designing and executing the probes that establish those constraints. In an era of increasingly capable AI code generation, the value of knowing what questions to ask — and having the tools to answer them empirically — is not diminished but heightened.

---

## References

1. Odendahl, M. "ARTICLE - surf-go Browser Verbs - Using JS Probes to Build Reliable Web Automation." Project report, April 10, 2026.
2. Odendahl, M. "PROJ - Surf CLI - ChatGPT Transcript Extraction." Project report, April 11, 2026.
3. Odendahl, M. "PROJ - Goja REPL Hardening." Project report, April 8, 2026.
4. Odendahl, M. "PROJ - Loupedeck Live Hello World - Serial Go Driver." Project report, April 11, 2026.
5. Odendahl, M. "ARTICLE - Loupedeck - Backpressure-Safe Go Frontend Deep Dive." Project report, April 11, 2026.
6. Odendahl, M. "ARTICLE - Loupedeck - Optimizing Button Animation FPS on a Serial WebSocket Device." Project report, April 11, 2026.
7. Odendahl, M. "ARTICLE - Loupedeck - Render Scheduler, Region Coalescing, and Display Blit Path." Project report, April 11, 2026.
8. Odendahl, M. "ARTICLE - Process Supervision and Cancellation - Designing Reliable Long-Lived Local Servers." Project report, April 10, 2026.
9. Odendahl, M. "PROJ - Screencast Studio - Architecture and Runtime Deep Dive." Project report, April 10, 2026.
10. Odendahl, M. "PROJ - Cross-Model Transcript Analysis - Minimax M2.7 vs GPT-5.4." Project report, April 9, 2026.
11. Odendahl, M. "ARTICLE - Deep Dive - Building an Interactive Attention Visualization Notebook." Project report, April 8, 2026.
12. Abnar, S. and Zuidema, W. "Quantifying Attention Flow in Transformers." Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics, 2020.
13. Meyer, B. "Applying Design by Contract." IEEE Computer, vol. 25, no. 10, pp. 40-51, 1992.
14. Beck, K. "Test-Driven Development: By Example." Addison-Wesley, 2002.
15. Basili, V.R. and Selby, R.W. "Comparing the Effectiveness of Software Testing Strategies." IEEE Transactions on Software Engineering, vol. SE-13, no. 12, pp. 1278-1296, 1987.
