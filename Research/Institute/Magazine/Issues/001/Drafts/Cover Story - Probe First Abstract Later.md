# Probe First, Abstract Later

**How systematic investigation of live systems — before writing a single line of production code — is quietly becoming the most reliable engineering methodology of the AI age.**

*By the Editors of The Golem Review*

---

It started with a hang.

A developer pressed Ctrl-C on a local screencast server and nothing happened. The terminal sat there, cursor blinking, while orphaned ffmpeg processes continued recording into the void. The obvious fix — add a signal handler, maybe two — would have taken ten minutes. Instead, the developer spent a day asking *why*. The answer restructured the entire application.

The server wasn't just an HTTP listener. It was a runtime supervisor: it owned recording managers, preview multiplexers, telemetry collectors, and the subprocesses beneath them. Cancellation wasn't a signal-handling problem. It was an ownership problem. The Ctrl-C reached the top of the process tree but had no path downward through the layers of managers, each holding its own goroutines, locks, and child processes. A signal handler would have masked the symptom. The investigation revealed the disease.

This pattern — invest in understanding the live system before committing to an abstraction — appeared independently across a dozen projects built in a single week this April. Not as a declared methodology, but as a recurring empirical finding: the projects that probed first shipped faster, broke less, and produced architectures that aged well. The projects that jumped to implementation spent their time debugging assumptions that a thirty-minute investigation would have falsified.

The evidence is worth examining, because it cuts against two powerful currents in contemporary software culture: the bias toward shipping quickly, and the growing temptation to let AI generate the first draft of everything.

---

## I. The Browser Verb Discovery

The Surf CLI project needed to extract structured data from web pages — ChatGPT transcripts, Kagi search results, Gmail threads. The conventional approach would have been to inspect the page in DevTools, identify some CSS selectors, write Go code to query them via the Chrome DevTools Protocol, and iterate when things broke.

The team did something different. They wrote numbered JavaScript investigation scripts — `001-check-page-structure.js`, `002-find-conversation-turns.js`, `003-test-extraction-boundaries.js` — and ran them against live pages using `surf-go js` as a first-class prototyping tool. Each script asked one question of the real DOM and recorded the answer.

The payoff was immediate. Script 003 revealed that ChatGPT's interactive provider returned citation fragments ("MIT OpenCourseWare," "Mathematical Association of America") instead of actual response text. The original extraction code grabbed the globally last assistant-marked DOM node, which happened to be a citation element, not the response body. No amount of reasoning about the page structure in the abstract would have caught this — the citation nodes carried the same `data-message-author-role` attribute as real responses. Only probing the live page, with real data, surfaced the failure.

The fix required a conceptual shift: from global selection (find the last assistant node) to turn-based extraction (find conversation turn boundaries, then extract within each turn, deduplicating by message ID and keeping the longest text per ID to defeat the citation fragments). This architecture proved robust not just for ChatGPT but across providers, because it was derived from observed page behavior rather than assumed structure.

The team formalized this into a workflow: probe with numbered scripts, save probes in ticket folders, identify real selectors and readiness conditions, move logic into embedded Go scripts, expose through dual-mode commands, validate in three layers. The probes aren't throwaway scaffolding — they're preserved as regression detection tools. When ChatGPT's DOM changes (and it will), the team re-runs the numbered scripts before touching production code.

"The page may be executable but not ready" became a working rule. `document.readyState === 'complete'` is necessary but not sufficient. Each page has its own readiness condition — a specific element appearing, a loading spinner disappearing, a particular API call completing — and the only way to discover it is to watch the page load repeatedly with a probe that checks progressively stricter conditions.

---

## II. The Invariants Beneath the REPL

Halfway across the project landscape, a different kind of investigation was underway. The go-go-goja project had a JavaScript REPL service that "mostly worked." Sessions could be created, evaluated, persisted, and restored. The temptation was to add new features — richer evaluation modes, better output formatting, plugin support. Instead, the team ran a hardening pass.

The methodology was simple: enumerate the invariants the system claimed to uphold, then test whether it actually upheld them.

It didn't.

Deleted sessions could still appear in normal reads. The soft-deletion contract — "deleted sessions are hidden from normal paths" — was violated because the query filters didn't consistently exclude tombstoned records. The bug was silent. No user had complained, because session deletion was rare. But the invariant was broken, and any feature built on the assumption that deleted sessions were invisible would eventually fail in ways that would be nearly impossible to diagnose.

Durable session IDs were generated using process-local counters. Two instances of the service running simultaneously — say, during a deployment — would generate colliding IDs. Again, no one had hit this yet. The investigation was ahead of the incident.

SQLite foreign key enforcement was set once during bootstrap rather than on every pooled connection. The database connection pool could hand out connections that had never received the `PRAGMA foreign_keys = ON` statement, silently allowing referential integrity violations. The data would look fine until a join returned phantom rows or a cascade delete missed its targets.

Each of these was a subtle correctness bug — the kind that doesn't crash, doesn't log an error, and doesn't manifest until the system is under enough load or has accumulated enough state that the symptoms become indistinguishable from a dozen other possible causes.

The hardening pass also validated that synchronous timeout interruption worked within the existing runtime architecture. An earlier experiment had abandoned this approach based on incomplete results. By re-running the investigation more carefully — testing timeout behavior on both synchronous and asynchronous JavaScript execution, verifying that sessions remained usable after timeout recovery — the team confirmed that the existing architecture could support the feature without a redesign. The earlier false negative had almost caused an unnecessary rewrite.

The principle that emerged: **strengthen invariants before adding behavior.** Not because new features are bad, but because features built on weak invariants compound the weakness. Every new capability that assumes "deleted means invisible" or "IDs are unique across processes" inherits the original bug and adds its own failure surface on top.

---

## III. The Device That Panics

The Loupedeck Live is a streaming control surface — 12 touch-sensitive LCD buttons, 6 rotary knobs, and a central touch strip, all connected over USB. The protocol is a variant of WebSocket running over a serial connection. The team's goal was simple: display graphics on the buttons, respond to input events, maybe run some animations.

The first Hello World program — 200 lines of Go — worked. The second program, which tried to update all 12 buttons in rapid succession, crashed the device. Not the software. The device. It sent back malformed WebSocket frames with invalid opcodes, causing the client library to panic.

The documentation said nothing about write-rate limits. The API offered no backpressure mechanism. The device simply broke when you wrote too fast, in a way that was indistinguishable from a protocol error.

The only path forward was empirical measurement. The team built a raw benchmark mode that bypassed the rendering layer entirely and measured pure transport throughput: how many bytes per second could the device accept before it started dropping frames? The answer varied by update granularity: a full-screen write (`360x270` pixels) topped out at 36 FPS. A single tile (`90x90`) reached 320 FPS. Twelve tiled updates aggregated to 288 FPS total. These numbers existed nowhere in any specification. They could only be discovered by probing.

The benchmarks also revealed a subtler constraint: the relationship between write rate and reliability was not a clean cliff but a degradation curve. At 80% of theoretical throughput, the device was stable. At 90%, occasional frame corruption appeared. At 100%, the panics returned. The safe operating envelope was well below the theoretical maximum, and the only way to find it was to measure.

This investigation directly shaped the architecture. Rather than leaving rate-limiting to application developers ("add a 100ms sleep between draw calls"), the team built backpressure management into the package itself. A render scheduler sits between the application's draw calls and the device's transport. It uses keyed invalidation — if the same screen region is redrawn multiple times within one flush interval, only the final state is sent. A single outbound writer goroutine owns all serialized WebSocket writes, enforcing pacing at the transport layer rather than hoping every caller remembers to throttle.

The result: application code draws whenever it wants, at whatever rate it wants, and the scheduler absorbs the bursts. Animations run at a visually smooth 10-15 FPS while the transport stays well within the device's reliable envelope. None of this architecture could have been designed from first principles. It was derived from measurements of the actual hardware's behavior under actual load.

---

## IV. The Supervision Tree

Return to the hanging screencast server. The investigation that began with "why doesn't Ctrl-C work?" ended with a general pattern for CLI-launched servers that manage background work.

The key insight was a distinction that seems obvious in retrospect but is routinely collapsed in practice: *cancellation* is not *shutdown*. Cancellation is a context becoming done — a boolean state change. Shutdown is an orchestrated policy executed in response to that state change: stop accepting new work, signal running work to finish, wait with a timeout, escalate if necessary, summarize what happened.

A context.Context propagates cancellation. It does not propagate a shutdown policy. When the screencast server's top-level context was cancelled by Ctrl-C, the cancellation reached the HTTP server, which stopped accepting connections. But the recording manager, which held references to running ffmpeg processes, had no shutdown contract — it never received a signal to drain, and even if it had, it held a lock during its wait that would have deadlocked against the cleanup path.

The investigation produced an explicit ownership tree: CLI context owns server runtime, server runtime owns managers, managers own subprocesses. Each manager implements a `Shutdown(ctx context.Context) error` method with timeout semantics. The runtime executes a staged shutdown sequence: stop HTTP intake, cancel active work, wait for managers to drain, escalate (SIGKILL) if the drain deadline expires, emit a summary of what was stopped and what was orphaned.

The critical design rule — discovered, not assumed — is that ownership must be established at construction time. If a manager receives its parent context as a constructor argument, the ownership relationship is an invariant. If the context is passed per-request, ownership is a convention, and conventions break under pressure.

A second rule, also discovered empirically: never wait while holding a lock. The recording manager's original implementation acquired a mutex before checking subprocess status, then waited for the subprocess to exit while still holding the mutex. Any concurrent call to the manager — including the shutdown path — would deadlock on the mutex. The fix was to copy the relevant state under the lock, release the lock, then wait.

Neither of these rules is novel. Both appear in textbooks on concurrent programming. But the investigation's value was not in discovering new theory — it was in discovering exactly where the existing codebase violated known theory, and designing the fix to make future violations structurally impossible rather than merely discouraged.

---

## V. The Read-to-Code Ratio

Perhaps the most direct evidence for the probe-first methodology came from watching two AI coding agents solve the same problem.

The experiment gave MiniMax M2.7 and GPT-5.4 identical tasks: implement a sqleton-style SQL verb query loading system for the go-minitrace project. Same codebase, same requirements document, same starting state. The sessions were recorded as JSONL transcripts, converted to a queryable format, and analyzed with SQL.

The behavioral divergence was stark. GPT-5.4 read 79 files before and during implementation. MiniMax M2.7 read 24. GPT-5.4's read-to-code ratio was roughly 3:1. MiniMax's was closer to 1:2.

Both produced correct, idiomatic Go for the core task. But the outcomes diverged in two ways.

First, coverage. MiniMax wrote 2.54x more test code (1,164 lines vs. 459) with deeper boundary-condition coverage: empty inputs, nil values, Unicode BOM stripping, whitespace handling, io.Reader variants, invariant preservation, exhaustive error paths. It tested 14 cases in `parse_sql_test.go` where GPT-5.4 tested 6. The test-first approach — write a test, implement until it passes, write the next test — is itself a form of probing. Each test is a question asked of the live code: "Do you handle this case?"

Second, scope. GPT-5.4 completed both Phase 1 (parsing and loading) and Phase 2 (rendering and CLI integration). MiniMax completed only Phase 1. The analysis revealed a likely reason: MiniMax never read the requirements document. It inferred the task from context and built confidently within that inference. GPT-5.4's broader reading included the design doc, which specified both phases.

The lesson is not that reading more is always better, or that reading less is always worse. It's that the *read-to-code ratio* is a meaningful diagnostic. A low ratio in a well-understood domain (implementing a known pattern in a familiar codebase) is efficient. A low ratio in an unfamiliar domain is a gamble. MiniMax's deep test coverage partially compensated for its narrow reading — the tests themselves were probes of the implementation's behavior — but the scope gap suggests that probing the *requirements* is as important as probing the *code*.

---

## VI. The Methodology

Across these projects, a common workflow crystallizes. It is not a formal methodology with named phases and gate reviews. It is a set of habits that, taken together, produce more reliable software in less total time than the alternative.

**Probe the live system before designing the abstraction.** The live system — whether it's a web page, a hardware device, a database, or a running process — knows things that documentation doesn't. Probing means asking it specific, falsifiable questions. Not "what is the page structure?" but "if I select the last `[data-message-author-role='assistant']` node, what text do I get?" Not "what's the device's throughput?" but "at what write rate do I see the first malformed frame?"

**Number your probes and keep them.** A probe is not scratchpad work to be discarded after the real code is written. It is an executable assertion about the system's behavior at a point in time. When the system changes — and it will — the probes are your first line of detection. The Surf CLI team's numbered investigation scripts serve exactly this role.

**Test invariants before adding features.** The REPL hardening pass found three classes of silent correctness bugs in a system that "mostly worked." Any feature built on top of those bugs would have inherited their failure modes. Thirty minutes of invariant testing saved weeks of future debugging.

**Measure before you optimize.** The Loupedeck team's raw benchmark mode — bypassing the renderer to measure pure transport throughput — produced numbers that no amount of profiling the Go code would have revealed. The bottleneck was the device, not the software. Optimizing Go code would have been wasted effort.

**Distinguish cancellation from shutdown.** This is a specific instance of a general rule: distinguish the *signal* from the *policy*. A context cancellation is a signal. What you do in response — drain, wait, escalate, report — is a policy. Policies need to be designed, tested, and owned by specific components. Signals just propagate.

**Separate investigation from implementation.** The probe phase and the build phase have different goals, different tools, and different success criteria. Probing succeeds when it falsifies an assumption or reveals an invariant. Building succeeds when it ships correct code. Mixing them — writing production code while still uncertain about the system's behavior — produces code that embeds unverified assumptions as structural decisions.

---

## VII. The AI-Age Argument

There is a reason this methodology matters more now than it did five years ago.

AI code generation is fast. Given a clear specification and a well-understood domain, a language model can produce correct, idiomatic code in seconds. The bottleneck is no longer typing speed or syntax recall. It is *knowing what to build* — which is to say, understanding the live system well enough to write a correct specification.

When a developer asks an AI to "extract the assistant's response from this ChatGPT page," the AI will generate plausible code that selects a plausible DOM node. If the page structure matches the AI's training data, the code works. If the page has changed — or if the training data never included the edge case where citation fragments carry the same role attribute as real responses — the code fails silently, returning confident but wrong results.

The human's role in this loop is not to write the code. It is to write the probes that validate the code's assumptions against reality. This is the work that AI cannot do for itself, because it requires access to the live system in its current state, not a statistical model of what the system probably looks like.

The cross-model transcript analysis makes this concrete. Both MiniMax M2.7 and GPT-5.4 produced correct Go code for the core parsing task. The difference was not in code quality but in *investigation quality* — how much of the surrounding system each model understood before it started building. GPT-5.4's higher read-to-code ratio correlated with broader scope completion. MiniMax's lower ratio correlated with deeper but narrower testing.

Neither model probed the live system in the way a human investigator would. Neither ran numbered experiments against the actual database, discovered edge cases through measurement, or preserved investigation scripts for regression detection. They operated on the code-as-text, not on the code-as-running-system.

This is the gap that probe-first methodology fills. Not a rejection of AI-assisted development, but a recognition that the most valuable human contribution is no longer writing code — it is *asking the right questions of the right systems at the right time*, and encoding the answers as executable, preservable artifacts.

The projects documented here — built in a single week, spanning hardware drivers, browser automation, REPL infrastructure, media pipelines, and AI behavioral analysis — are not methodologically exceptional. They are the work of a developer who, faced with uncertainty, defaults to investigation rather than assumption. The results speak for themselves: architectures that survive contact with reality, because they were derived from reality in the first place.

Probe first. Abstract later. The system already knows the answer. You just have to ask.

---

*This article draws on project reports from April 8-11, 2026, documenting work across the go-go-golems, surf-go, go-minitrace, go-go-goja, and screencast-studio projects.*
