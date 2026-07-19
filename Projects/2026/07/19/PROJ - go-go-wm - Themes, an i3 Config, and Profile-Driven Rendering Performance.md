---
title: go-go-wm - Themes, an i3 Config, and Profile-Driven Rendering Performance
aliases:
  - GGWM-004
  - GGWM-005
  - GGWM-006
  - go-go-wm themes and performance
tags:
  - project
  - golang
  - window-manager
  - x11
  - performance
  - profiling
  - theming
status: active
type: project
created: 2026-07-19
repo: /home/manuel/workspaces/2026-07-18/go-go-wm/go-go-wm
---

# go-go-wm: Themes, an i3 Config, and Profile-Driven Rendering Performance

This report covers the third phase of the go-go-wm project: the day the
window manager stopped being a demonstration and started being used.
The previous two reports describe the presentation-based window manager
itself ([[PROJ - go-go-wm - Building a Presentation-Based Window Manager in Go]])
and the JavaScript scripting layer built on top of it
([[PROJ - go-go-wm - Scripting a Window Manager with an Embedded JavaScript Runtime]]).
This phase, spanning tickets GGWM-004 through GGWM-006, has a different
character. The work was driven by a person actually running the WM:
give it a light mode with real white and a dark mode; port my i3
configuration to it; explain why creating workspaces is slow; fix the
tiles that will not close; make clicking a window focus it. Each request
pulled a thread, and several of the threads ended in bugs or costs that
had been present since the first ticket but that no test had ever been
positioned to see.

> [!summary]
> - **Themes.** The paper-and-ink palette became one of three named
>   themes — `paper`, `light` (true `#ffffff`), `dark` (anchored on
>   i3's `#1f1f1f`) — swappable at boot, over the control socket, and
>   from JavaScript, with readability enforced by a luminance-contrast
>   test rather than by eye.
> - **The i3 port.** A real ~350-line i3 config now runs as
>   `examples/scripts/i3.js`. Making it expressible required exactly
>   three API extensions (`wm.exec`, directional `wm.focus`/`wm.move`,
>   class-based rules) plus a `--no-default-binds` flag; everything
>   else fell out of machinery that already existed.
> - **Performance.** Four rounds of profile-driven optimization took
>   workspace creation from ~600 ms of CPU each to 55 ms, boot with
>   nine pre-created workspaces from 6.2 s to effectively instant, and
>   divider-drag CPU down 3.2× — ending in zero-copy MIT-SHM shared
>   pixmaps and batched operations.
> - **Five latent bugs** were found by live use and fixed, each one a
>   case of two parties believing they owned one piece of state.

## Why this phase exists

The scripting layer's thesis was "your window manager configuration is
a JavaScript program." The test of that thesis is not an example
script; it is somebody's actual configuration. The user's i3 config —
numbered workspaces, launcher keybindings, directional focus, window
assignment by class, a dark color scheme — became the acceptance test.
Porting it exposed every place where the claim was aspirational: the
API could not spawn a process, could not focus by direction, could not
match a window's class, and the WM's built-in keybindings fought any
config that wanted the whole keyboard. Closing those gaps was ticket
GGWM-004.

Using the result exposed the next layer: things that are invisible in
scripted tests and obvious to a human — startup latency, drag lag,
tiles that would not close, clicks that did not focus. Those became
GGWM-005 (performance, with a profiler) and GGWM-006 (the upload path),
plus a series of input-path bug fixes. The pattern of this whole phase
is that **live use is a test modality of its own**, and it finds a
class of bug that neither unit tests nor scripted end-to-end tests are
aimed at.

## The theme engine

### The mechanism: a mutable palette behind an unchanged API

Every renderer in the system — title strips, bars, builtin tiles,
scripted surfaces — reads colors from package-level variables in
`pkg/draw` (`draw.Paper`, `draw.Ink`, `draw.Sel`, …) at paint time.
That made the theme mechanism nearly free: a `Theme` struct with
fourteen named slots, a registry of three themes, and `draw.SetTheme`
which reassigns the variables and rebuilds the derived accent table.
No render-path signature changed. The contract is stated on the
variable block: SetTheme may only be called from the goroutine that
owns rendering in that process, and the caller repaints afterwards.

| slot | paper | light | dark |
|---|---|---|---|
| Paper (root) | `#e9e2d0` | `#ffffff` | `#1f1f1f` |
| Pane (tiles) | `#f5f0e3` | `#ffffff` | `#262626` |
| Field (inputs) | `#fbf8ef` | `#ffffff` | `#191919` |
| Ink | `#33302a` | `#1a1a1a` | `#e6e2da` |
| Sel (accept) | `#f4e6b8` | `#f6e9a8` | `#55482a` |

`light` is deliberately pure white — the explicit user requirement was
"real white, not that off-color beige." `dark` anchors on `#1f1f1f`
because that is the background of the i3 setup this WM replaces, and
its accent tones are darkened so the light ink keeps contrast on chips
and buttons. Readability is not reviewed; it is asserted: a test
requires a luminance gap of at least 60 (0–255 scale) between Ink and
every surface and accent tone, in every theme. Adding a fourth theme
means adding a struct literal; the swap-completeness and contrast tests
pick it up with no further work.

Theme state is owned by the WM and propagated as data. The control
socket gained `{"q":"theme"}` and `{"q":"set-theme"}`; JavaScript gained
`wm.theme()` / `wm.theme("dark")` through the same Backend seam as every
other call, so it works identically from rc.js, standalone scripts, and
the REPL. A `theme.changed` broker event lets script processes in
other address spaces re-theme their own surfaces live.

![[go-go-wm-theme-dark.png]]
![[go-go-wm-theme-light.png]]
![[go-go-wm-theme-paper.png]]

### The two traps

The mechanism found two classic failure modes of mutable global
configuration. First, **init-time copies**: three tables had captured
color values at package initialization (the accent cycle, the uispec
tone map, the trace-chip tone map), so a swap changed the variables but
not the copies — the fix is that anything derived from a mutable global
must be a function, not a value. Second, **two writers**: in the rc.js
process, the WM loop swaps the palette, and the event fan — reacting to
the WM's own `theme.changed` broadcast — swapped it again from another
goroutine. Interleaved writes over fourteen variables produced a
desktop with paper surfaces and dark accent chips, caught by a
screenshot and diagnosed as a torn palette. In-process, the event
handler now only repaints; only out-of-process runtimes swap on the
event.

## Porting an i3 configuration

The port was done by hand into idiomatic rc.js rather than by writing
an i3-config parser; a parser would inherit i3's full command grammar
for the benefit of one file. The header of `examples/scripts/i3.js`
carries a line-by-line mapping table, including the rows that are
deliberately not ported (floating, scratchpad, tabbed/stacked layouts,
i3 modes, multi-output pinning).

What mapped directly is instructive, because each mapping leans on a
design decision from an earlier ticket:

- Numbered workspaces are pre-created at boot and switched by name —
  possible because workspaces are ops on a serializable tree.
- `workspace_auto_back_and_forth` is ten lines of JavaScript state on
  `wm.on("switch-workspace")` — possible because every op is emitted
  as an event.
- `assign [class="Slack"] 8` became `wm.rule({class: /Slack/,
  workspace: "8"})` — the declarative rule engine already existed; it
  only needed WM_CLASS carried on the `window.managed` event.

What could not be expressed at all became the three API extensions:

1. **`wm.exec(cmdline)`** — i3 configs are mostly launcher bindings.
   The child runs via `sh -c` in the script's own process,
   fire-and-forget, reaped. It is enabled unconditionally in rc.js (an
   rc file is exactly as trusted as an i3 config, which is nothing but
   exec lines) and gated behind `--allow-exec` elsewhere.
2. **`wm.focus(target)` / `wm.move(dir)`** — directional navigation
   needs geometry, not tree structure. `wmcore.NeighborLeaf` answers
   "which leaf is to the left" from the same `Layout()` rectangles the
   WM paints from: candidates must overlap the source on the cross
   axis, nearest edge distance wins, cross-axis center distance breaks
   ties, and a final topmost-then-leftmost rule makes the answer
   deterministic. That last rule exists because the first test run was
   flaky: an exact two-way tie was being resolved by Go's randomized
   map iteration order. Any best-of-map scan needs a total order.
3. **Class-based rules** — `manage()` reads WM_CLASS at map time onto
   the frame, the event payload, and the `windows` query; rules accept
   `title` and/or `class` patterns, all present patterns must match.

One WM-side change was forced by the shape of the thing being ported
rather than by any single line of it: a config that owns the whole
keyboard cannot coexist with built-in keybindings, because a combo
grabbed twice fires both handlers — the ported "kill window" key would
also have shut the WM down. `--no-default-binds` disables the built-in
grabs, keeping only Escape, which is modal (accept and menu
cancellation) rather than a layout binding.

## What live use found

Five bugs surfaced through actual use during this phase. They are worth
recording together because they share a root: in each, two parties
believed they owned one piece of state.

**Double-grabbed combos.** Above — two handlers on one key. The state
was the keyboard grab table.

**The keyboard that died silently.** After the first workspace switch,
every keybinding stopped working; the mouse and control socket stayed
healthy. A goroutine dump (`kill -QUIT`) proved both event loops were
idle — not a deadlock — which relocated suspicion to X server state.
The cause: the new refocus-on-switch landed on a builtin tile, whose
frame has no client window, and the focus routine called
`SetInputFocus` with window 0. Window 0 is `None`, and with input focus
None the X server discards keyboard processing entirely — including
passive grabs on the root. The fix focuses the frame window for
client-less tiles. The state was the server's input-focus register.

**The unclosable tiles.** Clicking a tile's close button appeared to do
nothing. Instrumentation showed the click was delivered, the
WM_DELETE_WINDOW message was correctly constructed, and a standalone
probe sending the identical message did close the client. The client
was in fact exiting every time — but the WM never noticed, leaving a
zombie frame on screen that looked exactly like a failed close, along
with a stream of BadWindow errors as the WM kept focusing and
configuring a dead client id. The cause is an event-dispatch subtlety:
the Destroy/Unmap handlers were connected to the root window, but after
reparenting, a client's `DestroyNotify` carries the client itself as
the event window, and xgbutil dispatches callbacks by that window. The
handlers had never fired for any client in the project's history; no
scripted test had ever killed a client and then asked whether the WM
noticed. The fix connects the handlers to each client window at manage
time and detaches them on every teardown path (X recycles window ids;
stale callbacks would fire for strangers). The state was the frame
table's belief about client liveness.

**Click-to-focus.** Clients consume their own button events, so only
the title strip could focus a tile. The standard X11 idiom fixes it: a
synchronous passive button grab on each client lets the WM see the
press first, focus the tile, and then `AllowEvents(ReplayPointer)` so
the application receives the click untouched.

**The torn palette.** Described above under themes — two goroutines
writing one palette.

## Performance, round by round

The user's report was two symptoms: workspace creation at boot took
seconds, and drag-resizing a tile lagged. The method used to answer it
is the transferable part: the WM serves Go's pprof profiler when
`GO_GO_WM_PPROF=addr` is set, and a scripted harness drives real input
(xdotool divider sweeps) while a 12-second CPU profile records. Every
claim below is a profile line, and each round's fix exposed the next
round's cost — which had been invisible under the previous one's noise.

| round | dominant cost (profile share) | fix | result |
|---|---|---|---|
| 1 | `xgraphics.convertRGBA` 33% — the library's RGBA→BGRA loop iterates column-major, missing cache on nearly every pixel | own row-major conversion (`draw.ToXImage`) | conversion ~5× cheaper |
| 1 | `draw.Fill` 26% — per-pixel `SetRGBA` calls | write one row's byte pattern, `copy()` it down the rectangle | Fill vanishes from the profile; golden tests unchanged |
| 2 | GC ~30% — every paint allocated two ~3.8 MB buffers | frames cache their RGBA and X images, dropped on resize/unmap/destroy | GC share → ~8% |
| 2 | Expose handler 27% cumulative — every `MoveResize` during a drag exposed a frame painted microseconds earlier, triggering a full re-render | content lives in the window's background pixmap; Expose becomes one server-side blit | duplicate paints gone |
| 2 | `dividerMotion` 60% cumulative — a repaint of every visible pane per X motion event | coalesce motion to ~60 Hz with a final apply on release; repaint only rect-changed frames | drag cost tracks the frame rate, not the event rate |
| 3 | `copyImage` 73% of the workspace-creation burst — the strip/content blit called `dst.Set(x, y, src.At(x, y))` per pixel, allocating a `color.Color` interface each call | clipped row copies | 344 ms → 76 ms CPU per workspace |
| 4 | the upload itself — `memmove` + syscalls under `PutImage` | MIT-SHM shared pixmaps (next section) | 76 ms → 55 ms; upload cluster gone |

Two methodological points deserve emphasis. First, round 3's cost was
found only because the question changed from wall time to CPU time:
the machine was running at load average 19–51 on 8 cores, and
measuring `utime+stime` from `/proc/<pid>/stat` around the op burst
separated the WM's real cost (load-independent) from scheduler
queueing (at one point ~85% of perceived latency). When the machine is
busy, wall time conflates your code with everyone else's. Second, the
rounds were strictly sequential — profile, fix, re-profile — because
each dominant cost hid the one below it. A single profiling pass would
have fixed the conversion and declared victory.

![[go-go-wm-theme-dark-terminals.png]]

## The upload path, and making it disappear

X11 is a client/server protocol: the WM renders into its own heap, and
the server that owns the screen is another process which cannot see
that heap. In the core protocol, pixels travel exactly one way — the
`PutImage` request, pixel data serialized onto the Unix socket. One
full-screen frame (~3.8 MB) traverses its own bytes four times:

```
frame.img (RGBA)
  │ conversion write (R/B swap)
frame.ximg (BGRA) ──write()──► socket buffer ──read()──► server buffer
                                                            │ copy
                                                         pixmap → screen
```

No pixel is computed in any of that; they are only moved. The MIT-SHM
extension removes the movement for local clients: both processes attach
the same System V shared memory segment, and `ShmCreatePixmap` makes
the pixmap *be* that segment — the server composites directly from
memory the WM wrote. Four traversals become one (the conversion write,
now parallelized across four goroutines for large surfaces).

The implementation (`pkg/xshm`) is small but every line of its
lifecycle is a deliberate choice:

```
shmid := shmget(IPC_PRIVATE, w*h*4, IPC_CREAT|0600)
data  := shmat(shmid)                 // our mapping
shm.Attach(conn, seg, shmid)          // the server maps it too
shmctl(shmid, IPC_RMID)               // mark for deletion IMMEDIATELY
shm.CreatePixmap(conn, pid, ..., seg) // the pixmap IS the segment
```

SysV segments are kernel objects that survive process death; a crashing
WM would strand 3.8 MB segments until reboot. Marking the segment for
deletion the moment both sides are attached means the kernel reclaims
it when the attachments drop, whatever the exit path — verified by
`kill -9`-ing the WM and checking `ipcs -m`. Capability detection
(`ShmQueryVersion` → `SharedPixmaps`) gates the whole path; remote
displays and servers without shared pixmaps fall back to the existing
PutImage code, and `GO_GO_WM_NO_SHM=1` forces the fallback for
debugging. Correctness was asserted by rendering the same scene through
both paths and diffing root screenshots: byte-identical.

One X11 subtlety cost real thought: a window's background-pixmap
attribute holds a server-side reference, so freeing the pixmap does not
free the shared pages until the attribute is reset. The buffer-teardown
routine resets the background to a plain pixel before destroying the
surface — the same lesson as the callback-detach fix, in resource form:
teardown lists must be complete, and a "reference" can live on the
other side of the wire.

### Batched operations

The last piece attacked frequency rather than unit cost. Creating a
workspace switches to it (prototype semantics), so pre-creating nine at
boot painted ~17 full-screen launcher tiles nobody ever saw.
`WM.ApplyBatch` applies a burst of ops with a single
reconcile-and-paint pass at the end, while still emitting every per-op
event (the trace and the rule engine observe the same history).
JavaScript reaches it through the existing escape hatch — `wm.apply`
now accepts an array — and i3.js creates its workspaces in two batches
(the adds first, because the renames need the ids the adds return).
Boot-to-nine-workspaces, 6.18 s at the start of this phase, now
completes before the control socket can answer its first poll.

Two listed optimizations were explicitly not implemented, each with a
decision record: rendering directly in BGRA (the RGBA invariant spans
golden tests, screenshot tooling, and every color literal; parallel
conversion bought the latency without touching it) and damage-based
partial repaints (today's renderers are whole-surface, and the trace —
the busiest tile — scrolls, dirtying the whole pane exactly when it
matters; a design sketch is recorded for when event volume justifies
the renderer API change).

## Cumulative results

| metric | before (start of phase) | after |
|---|---|---|
| workspace creation, CPU each | ~600 ms | 55 ms |
| boot with 9 workspaces (i3.js) | 6.18 s | < first socket poll |
| 12 s divider-drag stress, CPU samples | 7.74 s | ~2.0 s |
| GC share of profile | ~30% | marginal |
| full-frame upload | 4 traversals + chunked syscalls | 1 parallelized conversion write |
| Expose during drag | full re-render | server-side, no client work |

## Working rules this phase produced

- Anything derived from a mutable global is a function, not an
  init-time value; and a mutable global gets exactly one writer per
  process.
- Assert colors and contrast numerically (luminance gaps, pixel
  sampling) — downscaled screenshots hide both theme differences and
  torn palettes.
- Any best-of-map scan needs a total order, or it is a flaky test
  waiting to happen.
- Per-pixel loops: the inner index moves along memory, slice windows
  are hoisted, and no method is called per pixel; fills and blits are
  `copy`/`memmove` jobs.
- Buffers sized by screen area are cached on the surface that uses
  them and freed when it becomes invisible.
- Coalesce continuous input to paint cadence; apply final state on
  release.
- Profile → fix → re-profile until the top of the profile is work you
  chose to do; measure CPU seconds, not wall time, on a loaded
  machine; and attribute shared-memory segments (`ipcs -m -i`) before
  calling anything a leak.
- Every teardown path must be complete — callbacks detached, buffers
  dropped, server-side references (background pixmaps) released — and
  the lists must be maintained together.
- First synthetic keypress after an X server boots can be swallowed
  while the keymap settles: test fixtures retry; they never assert a
  single cold press.

## Current status

Tickets GGWM-004, GGWM-005, and GGWM-006 are complete and pushed
(branch `task/go-go-wm`; the sequence runs from commit `0461cee` to
`51f3684`). All unit suites pass; the two end-to-end harnesses
(`scripts/rc-smoke.sh`, `scripts/examples-smoke.sh`, nine fixtures
including i3.js booting dark with batched workspaces) pass; the shm
path is pixel-verified against its fallback and leak-checked through
`kill -9`. Each ticket carries a design document with decision records,
an implementation diary including the false leads, and — for GGWM-004
through GGWM-006 — an intern-level guide; all are bundled as PDFs on
the reMarkable under `/ai/2026/07/19/`.

## Open questions

- Directional focus stops at the workspace edge; i3 crosses outputs.
  Multi-output support as a whole (workspace pinning, per-output
  areas) remains undesigned.
- The benign-race posture for shared-pixmap writes (no
  synchronization; single-digit-millisecond paints) is fine on a bare
  server; a compositor would read more often and might justify
  escalating to `ShmPutImage` with completion events.
- The i3 port intentionally lacks floating, scratchpad, and
  tabbed/stacked layouts; whether any of them belong in a
  presentation-based WM is an open design question, not a backlog
  item.
- Damage-based repaints are sketched but wait for evidence: the
  renderer API change (returning dirty rects) should be paid for by a
  profile, not by anticipation.

## Near-term next steps

- Live the daily-driver experiment: run `startx ~/ggwm-session.sh` on
  a second VT with i3.js as the config, and let real use write the
  next ticket.
- An exit/quit affordance (`wm.quit()` or an rc-level binding) — the
  full-session setup currently leans on `pkill` from another VT.
- Fold the first-keypress keymap-settling flake into a boot-time
  readiness signal instead of per-fixture retries.

## Related notes

- [[PROJ - go-go-wm - Building a Presentation-Based Window Manager in Go]] —
  the WM itself (GGWM-001): ops-as-data, the broker, the accept
  protocol.
- [[PROJ - go-go-wm - Scripting a Window Manager with an Embedded JavaScript Runtime]] —
  the scripting layer (GGWM-002/003): runtime model, Backend seam,
  attachment points.
