---
title: Makera Z1 Control — P5 Qualification, Firmware Job Semantics and the G-code Decoder
aliases:
  - Makera Z1 P5 qualification technical report
  - Z1 job lifecycle and firmware semantics
  - dropcut decode and the opcode firmware trace
tags:
  - project
  - cnc
  - go
  - gcode
  - firmware
  - evidence
status: active
type: project
created: 2026-09-14
project_started: 2026-08-11
repo: /home/manuel/workspaces/2026-08-11/cnc-control-dropcut/dropcut-studio
branch: task/cnc-control-dropcut
implementation_commit: 4d15e13
source_tickets: MZ1-016, MZ1-017
scope: P5 hardware qualification completion (job lifecycle, firmware suspend/abort semantics), the MZ1-017 G-code decoder (dictionary package, CLI, firmware opcode trace)
implementation_status: P5 closed with all changed paths live-qualified except M801 (skipped by operator decision); decoder package, CLI and firmware trace complete, Inspector UI pending
---

# Makera Z1 Control — P5 Qualification, Firmware Job Semantics and the G-code Decoder

A machine controller that refuses to claim success without machine evidence must eventually face the inverse problem: a machine that withholds evidence. The stored-program verbs of the Makera Z1 — play, suspend, resume, abort — do exactly that. The firmware accepts a command, prints nothing or prints an acknowledgement that describes an intermediate state, and finishes the real work tens of seconds later inside a motion-queue drain. This report covers the completion of staged hardware qualification (P5) for the dropcut-studio controller: the job-lifecycle investigation that surfaced the firmware's actual suspend and abort semantics, the evidence-model fixes it forced, and the follow-on work it motivated — a source-grounded G-code decoder (`dropcut decode`) whose opcode dictionary is traced handler-by-handler into the vendored firmware.

The reader should finish with three things: the complete set of firmware behaviors a host controller must model for stored programs; the design pattern that resolves commands whose textual replies cannot be captured — verification by machine observation rather than reply text; and a working CLI that decodes any G-code file against the same dialect sets the compiler targets. Every machine claim cites an archived receipt or a firmware source file. Where a property is designed but not yet exercised, the text says so.

## 1. What the previous report left open

The predecessor report ("Controller Ownership, Adapter Cutover and Hardware Qualification") ended with the spindle batch: motion, limits, alarms, unlock and observed-RPM spindle control all qualified through the single-owner controller. Two P5 items remained: the accessory outputs and the stored-program lifecycle — play a file, watch it run, suspend it mid-motion, resume it, abort it. The accessories qualified without incident (six dispatch-only operations through the current controller stack; light, spindle-fan and air verified, M801 skipped by operator decision because the auxiliary terminal wiring was never confirmed). The lifecycle became the subject of this report.

Three design properties from the earlier phases shaped everything that followed. First, job control belongs to the session that started the job; a fresh process cannot supervise a job it did not register, because operation records — including unresolved ones — are the session's own evidence. Second, a play operation deliberately never reaches a terminal phase on status alone: `Idle` never completes a program, because the firmware's idle state cannot distinguish "ended" from "never started". Third, transaction completion (the echo-sentinel exchange) is never machine fact. The lifecycle tests probed all three boundaries at once.

## 2. The evidence-chain failures found before the machine semantics

Two defects surfaced before any job-lifecycle result, both from qualification discipline rather than design review.

**The stale artifact.** The first accessory batch unknowingly ran through a gitignored binary compiled before the adapter cutover: the light toggled (the firmware accepted `M821`/`M822`), but the receipts recorded the legacy client's output format, and `spindle-fan` was rejected as an invalid choice because the old binary predated the reviewed-name rename. The diagnostic clue was in the receipts' stderr: `component=makera.Client` — a package the cutover had deleted. The batch was stopped at the first unexpected outcome per protocol, the binary was removed, and every subsequent live test ran from current source via `GOWORK=off go run` — the artifact class of failure was eliminated by eliminating the artifact.

**The dry-run that connected.** While verifying the reviewed accessory names, three `accessory … off --dry-run` invocations connected to the machine and dispatched real stop commands (`M822`, `M812`, `M9`). The action runner honored its `--dry-run` flag; the stop runner did not. No physical consequence followed — the outputs were already off — but the fix was structural: stop verbs now render intent, command and `sent=false` without opening a connection, and each stop verb supplies the exact command text a dry-run would show.

Both defects were evidence problems, not control problems: the machine behaved; the host's record of what it had done was wrong. The fixes follow one rule — receipts and error text must name the concrete facts (which component ran, which command would be sent, which check refused) instead of generic strings.

## 3. Silent play: a reply that does not exist

The first play attempt returned `dispatch outcome uncertain: stock job command produced no source-recognized outcome` and, by design, the controller held the machine with a feed hold rather than guess. The investigation proceeded through three hypotheses, each disproven by its own evidence.

1. **Unrecognized reply text.** The recognition rule expected the Player to print `playing …`. Reading the MZ1-001 hardware notes showed the stock `play` command is *silent*: it prints nothing on success and nothing on a silent refusal such as an unhomed machine. The rule was testing for a reply the firmware never sends.
2. **Read timeout.** The session's 300 ms read window was a plausible suspect for a command that makes the firmware open a file on SD. Replaced as the primary hypothesis by the next observation.
3. **Wrong evidence source.** The fix at this stage verified playback through the status report's `P:` key — a community-firmware field. The machine kept failing verification with "no machine playback evidence within 3 s" *while the square ran*, and a raw status frame finally showed why: this firmware reports `P:3,92,0` — **three** fields, not four; our parser required the optional fourth (`isPlaying`) and therefore never recognized its own machine's playback reports. The correct source was the `progress` text command all along, whose reply formats are documented in the vendored source.

The durable fix verifies a silent play from two sources, polled for a bounded window: the Player's own `progress` reply first (this machine's actual evidence channel), then the `P:` status key for firmwares that report it. A play that produces no evidence from either source is a *named refusal* — "the firmware may have silently refused" — never a silent success. The earlier claim in project notes that "stock firmware does not report P:" was wrong and is corrected here: it reports three fields; our parser was wrong, not the firmware.

## 4. Suspend and abort: commands that finish later than their replies

The decisive discovery of P5 came from the paced lifecycle test. A 100-line program of alternating 2 mm moves at 300 mm/min gave the queue real depth, and the receipts captured the firmware's behavior precisely:

| Receipt | Observation |
|---|---|
| play | 200 in 0.72 s, `job_running`, verified by `progress` evidence |
| suspend (5 s in) | 202 at 10 s: "request window ended; the operation continues" |
| status poll | **Pause, feed 0, position (−13,−10,−2), `P:45,49,19`** — 45 lines played, 49 %, the file still open: genuine mid-file suspension |
| resume | 200 in 0.08 s, `job_running`, "resume began" |
| abort (3 s later) | **no reply lines at all** — op unknown, sequence stopped |

Reading the vendored firmware source (`modules/utils/player/Player.cpp`) explained all of it. `suspend_command` prints "Suspending, waiting for queue to empty…", drains the *committed* motion queue, and only then saves position and modal state and latches suspension. The queue on this machine holds roughly forty-plus blocks; because a small file is read ahead almost entirely, "suspend" on such a file means "finish everything buffered, then pause on whatever remains unread" — on a fully-buffered file it degenerates to pausing on nothing, leaving the suspension latch set with no open file. From that state `abort_command` early-returns ("Not currently playing") without clearing the latch, and only `resume` (which restores the saved position with an `F1000` move and clears the latch even after end-of-file), a `G28`, or a reboot exits the state. This is the state the qualification hit twice, and the reason the operator's machine showed a paused light with nothing to resume.

The abort result has the same cause in a different shape. `abort_command` blocks the console handler in `wait_for_idle()` before printing its reply — so the echo sentinel of the host's two-frame batch is answered in ~0.1 s while the abort's own reply line ("Aborted playing or paused file.") arrives only after the drain, outside any sentinel-bounded collection window. An empty collection is therefore the *normal shape of a mid-motion abort*, not a refusal. The physical evidence confirmed the abort worked both times: the machine settled mid-pattern — final position (−11,−10,−2) against a start of (−15,−10,−2), and the status mode field showed the program stopped before its final `G90`. A completed file would have returned exactly to start and left absolute mode set.

The fix generalizes the suspend pattern: **verify by machine observation, bounded in time**. After an empty abort exchange, the driver polls machine state until the drain settles — `Idle` with zero feed and no playback key — or an `Alarm` intervenes; the operation resolves as `job_aborted` on that evidence, with the reply text as a bonus when it happens to arrive in-window. The confirmation run resolved in one command; the receipts show the settled state and the mid-pattern position.

```text
three clocks that must not be conflated:
  HTTP wait window (10 s) ──▶ 202 "operation continues" ──┐
  driver evidence window (60 s) ──▶ Pause / Idle observed ─┤─── one op record
  firmware drain (queue depth × move time, measured ~20-25 s) ─┘
```

The worker window matters: the first attempt bounded the evidence wait at 30 s and the live drain took 20–25 s — one slow feed away from a false timeout. Suspend and abort now carry a 60 s window, and the 202-while-running contract covers anything the HTTP side cannot wait for.

## 5. Qualification closed

With the lifecycle resolved, P5 closed with every changed controller path carrying live evidence:

| Path | Evidence |
|---|---|
| Read-only surfaces, homing, bounded moves, work-frame moves, WCS zeroing | Batches 1–2 receipts |
| Soft-limit trip + alarm + evidence-gated unlock; E-stop refusal with halt-reason text | Batch 2–3 receipts |
| Spindle on/off with observed RPM; accessories (light, spindle-fan, air) | Batch 3 receipts |
| Filesystem scratch cycle incl. verified upload/download digests, mv, rm, empty listing | Batch 4a + close-out receipts |
| Play verified mid-run; genuine mid-file suspend with `P:` evidence; resume; abort verified by machine evidence with mid-pattern physical proof | Lifecycle receipts |
| Hold → cycle-start release (across uncertain-dispatch freezes); explicit firmware `resume` recovery (twice, operator-authorized) | Batch 4 series receipts |
| M801 auxiliary output | **skipped by operator decision** — never wiring-confirmed, never to be treated as tested |

The machine was left Idle, spindle off, TCP slot free, and the SD card cleaned of test artifacts. The controller seam for MZ1-015 (embedded JavaScript procedures) is now fully qualified: register operations, await by operation ID, treat `job_running`/`job_suspended` as settled-but-owned states, use the urgent hold path, and never resolve a stop from its reply text.

## 6. The decoder: turning firmware knowledge into a tool

The lifecycle work produced an unusual asset: a verified understanding of what every opcode on this firmware actually does, including which claimed codes do nothing. MZ1-017 turned that into a decoder, in three layers.

**A dictionary package with a drift test.** `@cam/gcode-codes` holds one entry per G- and M-code — group, modality, parameters, one-sentence meaning, machine-specific notes, and *sources* (RS-274; the repository's own hardware tickets MZ1-001/006/016; `vendored <file>:<line>` for semantics read from firmware). A conformance test asserts that every code any registered machine profile claims to support has an entry, so opcode help can never silently go missing. The machine profiles describe the compiler's *emission dialect*; the dictionary describes *firmware behavior*; the drift test keeps the two honest with each other.

**A CLI that answers the three review questions headlessly.** `dropcut decode <file.nc> [-m machine] [--line N]` runs the same modal interpreter the studio uses, against the selected machine profile's dialect sets: file summary, structured `;@MKR|` header records, the census of codes used with meanings and support marks, diagnostics with line numbers, and a word-by-word decode of any single line. `dropcut codes` prints the dictionary itself. The running example is the operator's real part file (`MakeraBadge.nc`, 18,532 lines, 328 KB): 17,439 cuts, two tool changes at recorded lines, three toolpaths, sub-second parse — committed as a test fixture with its decode numbers pinned.

**The firmware trace.** The dictionary's authority is a design document that traces every code to its handler in the vendored firmware, with fifty links into the source tree. Its findings correct several standard-dialect assumptions:

- `M30` is **not** program end on this firmware — it removes a file from the SD card (Marlin heritage). Real exports end with `M02`.
- Eight codes claimed by our profiles have **no firmware handler**: G40/41/42 (cutter compensation), G43/49 (tool length — the offset exists as internal state set by the ATC module, not by the G-code), G80, G93/94. They are inert.
- The firmware *does* implement arc motion modes (G2/G3); the profile's "cannot arc" records an exporter fact, not a firmware fact.
- `M3`/`M5` are dual-purpose: spindle normally, laser when laser mode is enabled.
- The accessory codes (M7/M9 air, M811/M812 fan, M821/M822 light, M801/M802 aux, and the probe/tool-sensor/charger family) have no hardcoded dispatch at all — the Switch module binds them from `switch.*` config sections at boot, which is why the two stock config defaults genuinely disagree about what M801 drives, and why their `S` word is a raw sigma-delta byte (1–255), not a percentage.
- `M999` is the only command accepted while halted (plus a short query allow-list), clearing the halt with the warning that homing is still required — the dispatch-level mechanism behind the controller's evidence-gated `$X` unlock.
- `M331`/`M332` are mode switches (vacuum mode in/out), not output toggles.

The deep-dive sections of that document cover the mechanically interesting verbs in detail — the dual-unit dwell, offset arithmetic in `G10 L20`, the park/home split inside `G28`, `G92.4`'s register surgery, the `G53` dispatcher rewriter, and the three-clock suspend — because those are the behaviors a decode tool must not paraphrase away.

## 7. What remains

The Inspector web page specified in MZ1-017's design guide is the next implementation target: the same decode pipeline behind a browser surface, reusing the studio's CodeMirror line-highlight editor, the `viewer-three` 3D playback (whose `gcodeLine` field is the join key between text and motion), and the dictionary — with a per-entry firmware-status property so the UI can say "inert on this machine" instead of a bare meaning. Beyond it, MZ1-015 builds the embedded-JavaScript procedure runner on the now-qualified controller seam.

Two open firmware questions are recorded rather than guessed: where `M2`/`M02` program-end is actually implemented (accepted in practice, handler not located), and the `M490` subcode mapping for the 4th-axis clamp. The grbl-mode park coordinates baked into the firmware's `G28` remain deliberately untested — the host killed its own park scope for exactly the unverifiable-coordinate reasons the firmware path now confirms.

> [!summary]
> - A sentinel-bounded exchange proves dispatch, not outcome; some firmware commands finish — and reply — long after their sentinel, inside a motion-queue drain the host must observe rather than wait out.
> - Suspend means "drain the committed queue, then stop feeding"; with read-ahead buffering it degenerates on small files into a latch with no open file, which abort cannot clear but resume, G28, or reboot can.
> - Empty reply collections are structural, not exceptional, for mid-motion aborts; completion verifies by machine state, bounded in time, with the 202-while-running contract covering what a request window cannot.
> - "The firmware does not report X" is a claim about machine state during observation, not capability; this project's own parser bug was misread as a firmware limitation.
> - Machine profiles describe emission dialects; firmware dispatch is the union of module handlers — eight claimed codes are inert, M30 deletes files, and the accessory codes are born from config.
> - Artifacts and generic error strings are evidence failures: run from current source, and make every refusal name its concrete facts.

## Related notes

- [[Projects/2026/09/14/PROJ - Makera Z1 Control - Controller Ownership, Adapter Cutover and Hardware Qualification|PROJ — Makera Z1 Control: Controller Ownership, Adapter Cutover and Hardware Qualification]]
- [[Projects/2026/09/13/PROJ - Makera Z1 Control - P1 and P2 Protocol Ownership and Hardware Evidence|PROJ — Makera Z1 Control: P1 and P2 Protocol Ownership and Hardware Evidence]]
- [[Projects/2026/09/13/PROJ - Makera Z1 Control - Three Refactors for Authority Evidence and Browser Intent|PROJ — Makera Z1 Control: Three Refactors for Authority, Evidence and Browser Intent]]
- [[Projects/2026/09/12/ARTICLE - Makera Z1 Stock Firmware - Source-Grounded Command and Telemetry Reference|ARTICLE — Makera Z1 Stock Firmware: Source-Grounded Command and Telemetry Reference]]
- [[Research/Software Architecture Garden/dropcut-studio/designs/09 - Single-Owner CNC Controller - Worker Ownership Separate from Operation Evidence|Garden 09 — Single-Owner CNC Controller]]
