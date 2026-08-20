---
title: "PULP Design System and Demo Suite — Screenshot-Driven UI Engineering"
aliases:
  - ESP-56 design system
  - ESP-57 demo suite
  - PULP screenshot pipeline
tags:
  - project
  - esp32
  - esp-idf
  - eink
  - microquickjs
  - firmware
  - design-system
  - typography
status: active
type: project
created: 2026-08-20
repo: /home/manuel/code/wesen/go-go-golems/esp32-s3-m5/0114-papers3-pulp-os
---

# PULP Design System and Demo Suite — Screenshot-Driven UI Engineering

Until this week, nobody working on PULP OS could see it. The M5Stack PaperS3's e-ink panel was validated through fingerprints — hit-region counts, `pulp screen:` evidence lines, present-mode logs — which prove that screens *exist* but say nothing about whether they look right. Two tickets changed that. ESP-56 gave the toolchain eyes (a QOI framebuffer capture streamed over the same USB serial the console uses), used them to audit all sixteen screens against the one screen everyone agreed looked right, found that a single silent JavaScript defect had removed the margins from every application, and codified the visual language into facade idioms that applications cannot get wrong. ESP-57 then built the demo suite — twelve HTTP-installable applications that together exercise every surface of the JS API — and in doing so put the app-distribution platform under the most productive stress it has ever had: one device crash, one protocol trap, one policy error, one capacity ceiling, and one still-open regression, each found by an install gate rather than a user. This report covers both, because they are one method: capture, look, fix, re-capture.

> [!summary]
> - The screens became capturable: an owner-task console op streams the framebuffer as QOI; a cdc_acm-safe client decodes to PNG. Every finding below was made, and verified fixed, by looking at pixels.
> - The margin epidemic had one cause: mquickjs parses `get M() {…}` in an object literal **without accessor semantics** — `os.M` was a function object, and every `pad(0, os.M, …)` coerced to zero. Headers kept their margins because the kernel reads the global directly; app content lost them.
> - The design system now lives in the facade as idioms (`body`, `menuRow`, `button`, `keyboard`, `label`, `key`), with typographic roles stated as rules: grotesque for identity, serif for text **and controls**, symbols are keys, words are buttons, one 40-pixel grid with no private gutters.
> - A renderer bug older than the design system fell out of the audit: inverted chips had never rendered their labels, because glyph coverage was composited over an assumed white background and white ink computed to "background everywhere."
> - The demo suite (twelve apps, eleven hidden behind a visible index) installs over HTTP in one command; pushing it crashed the httpd task (stack overflow in the new manifest writer), broke on `&` in titles, exposed write-once manifests, and outgrew the directory-listing cap for the second time in two tickets.

## Why these projects exist

The design ticket exists because the operator kept seeing what the fingerprints could not: text that ignored the margin, screens whose title sat on the grid while their content did not, buttons in three unrelated styles. The instruction was precise — assess the screens as a Swiss typography designer would, using the launcher (which looked right) as the reference, and move the design into the API so it holds by construction rather than by per-app discipline.

The demo ticket exists because an API without a living exhibit decays in two directions at once: newcomers cannot see what the system can do, and maintainers cannot cheaply verify that all of it still works. Twelve small applications, each demonstrating one API area completely and readably, serve as documentation, acceptance harness, and sales demo simultaneously — and because they install exclusively over HTTP, they also regression-test the distribution pipeline every time they are deployed.

## The instrument

Everything else in this report depends on one capability, so it comes first. The repository already contained `components/screenshot_qoi` — a component that reads the M5GFX framebuffer and streams it as a QOI image over USB Serial/JTAG, framed by `QOI_BEGIN <len>` / `QOI_END`. ESP-56 wired it into PULP OS as a console operation (`shot`) that executes **on the owner task**, so a capture can never race a present. The host side is a capture client built on the hold-open port discipline (this host's cdc_acm asserts DTR/RTS at open; the client opens once and keeps the descriptor), with a pure-python QOI decoder and PIL for PNG output.

```mermaid
flowchart LR
    C[client: taps via console] --> D[owner task]
    D -->|shot op| Q[screenshot_qoi:\nreadPixel -> QOI encode]
    Q -->|QOI_BEGIN len ... QOI_END| U[USB serial]
    U --> P[client: decode QOI -> PNG]
    P --> R[Read the pixels.\nJudge. Fix. Re-capture.]
    style R fill:#263f2f,stroke:#61a273
```

Two integration details were earned rather than free. The component's CMake required the component name `M5Unified` (an Arduino-style checkout); PULP uses the registry component `m5stack__m5unified`, and the name had to travel to the component through an **environment variable** — IDF's requirements-expansion pass runs in a separate cmake process, so neither plain nor cache variables from the project scope reach it (two failed attempts established this). And after `source export.sh`, `python3` is the IDF virtualenv, which lacks PIL; the capture client runs under `/usr/bin/python3` explicitly.

## The audit, and the defect underneath it

Sixteen baseline captures made the pattern unmistakable and confirmed the operator's report exactly: every screen's header (title plus thick rule, built by the kernel's `chrome()`) sat at the 40-pixel margin; every screen's *content* sat at x = 0. Daily Pulp clipped glyphs at the panel edge. The launcher alone was fully correct.

That asymmetry is a stack trace if read correctly. Headers come from the kernel, which reads the global `M`. Content comes from applications, which read `os.M` — declared in the facade as an object-literal getter:

```js
var os = { get M() { return M; } };   // intended: a live view of the margin
```

mquickjs parses this syntax **without getter semantics**. The property `M` exists, and its value is the function object itself. Host verification took one throw: `typeof os.M === 'function'`. Every `pad(0, os.M, 0, os.M)` then coerced a function to an integer and produced `pad(0, 0, 0, 0)`. The host compiler accepted the syntax, so nothing failed at build; the defect was invisible until the screens were. The dialect fact sheet's "getters: yes" claim is hereby narrowed: not in object literals.

The remainder of the audit was genuine design critique, summarized as findings: two unrelated button languages (display-grotesque shouts in Dice — `2d6 d20 coin d%` — versus bracketed 12-point-serif whispers — `[ +30s ]` — in three other apps); four hand-rolled keyboards with drifting metrics; the menu-row idiom duplicated three times; and, on the positive side, the launcher's pairing (grotesque display for identity, serif for metadata, right-aligned sublabels, inverted chip for the primary action) as the system worth generalizing.

## The system, as API

The face inventory is fixed by the text engine: `xs/sm` render in the serif UI face, `md` in the serif body face, `lg` in the bold grotesque display face, `xl` in the grotesque hero size, `title` in the serif display size. The roles assigned to them are the design system:

| Role | Face | Used for |
|---|---|---|
| Identity | grotesque `lg`/`xl` | screen titles, launcher app names, hero numerals (clocks, scores) — never controls |
| Text | serif `xs/sm/md/title` | body, subtitles, metadata, hints, book titles; the typed draft in an input screen is reading text and stays serif |
| Controls | serif `md`, no brackets | every tappable action; the primary action is an inverted chip; minimum target 100×56 |
| Labels | grotesque `lg` | prompts and section headings — the small serif is reading text only |

The enforcement mechanism is the facade. `os.M` became a plain number synchronized by `os.setMargin` (kernel global, facade field, and persisted setting updated together). The idioms — `os.body(padTop)` for the content column, `os.menuRow` (launcher, Settings, and catalogs now share one row implementation), `os.button(label, fn, {w, primary, size})`, `os.buttonRow()`, `os.label(t)`, `os.keyboard(body, rows, onKey)` and `os.key(ch, fn, w)` — mean an application never touches a raw `pad()` for standard layout at all. An application needing one is now itself a finding.

Two refinements arrived from a second round of operator critique of the re-captured screens, and both became rules rather than fixes. First, the keyboard screens had kept a private 24-pixel gutter — not by taste but by arithmetic: 48-pixel keys cannot fit a ten-column row inside 40-pixel margins. Narrowing keys to 42 pixels (438 ≤ 460 available) dissolved the second gutter entirely; every text-entry screen now shares the single grid. Second, the first composition of the new action row set `,<del>` in the key face — a *word* rendered as a *symbol*. The rule that resolved it: **symbols are keys, words are buttons.** The comma stays a 42-pixel key; `delete` and `space` are serif buttons; the primary chip closes the row.

### The chip that never had a label

Re-capture exposed a renderer defect that predates every ticket in this arc: inverted chips (`SEAL`, `JOIN`) rendered as solid black slabs — verified in the baselines too. The m5 backend's `BlitCoverage` composited glyph coverage as `v = 255 − ((255 − ink) · c)/255` — ink over an assumed **white** background — and skipped runs whose value was 255 as untouched background. For white ink (255), every pixel computes to 255; every pixel is skipped; no glyphs are drawn. The fix adds a light-ink path: ink ≥ 128 composites over an assumed black background (`v = ink · c / 255`) with a 0-valued skip sentinel. The SEAL chip has a visible label for what is likely the first time on hardware. The general lesson: a blend function's implicit background assumption is part of its contract, and inverted rendering violates it silently.

## The demo suite

The suite's shape follows three constraints. Coverage: an API inventory (documented as tables in the ticket's intern guide) assigns every callable surface to exactly one demo — `d-widgets` (type and layout specimen), `d-canvas` (all five draw verbs), `d-touch` (six gestures plus a 3×3 hit grid, deliberately trapping swipe-down to document the trap rule), `d-ticker` (timers and dynamic text), `d-storage` (the async files chain as an on-screen log, plus the int32 settings store), `d-net` (station status plus a TLS chunked fetch), `d-serve` (routes registered by an app, with the resetTree lifecycle stated on screen), `d-sound`, `d-power`, `d-books`, `d-sysinfo` (engine and catalog introspection). Distribution: demos are repository files (`tools/js/demos/`) that are **not** embedded in firmware — they reach a device only through `PUT /apps/upload`, which makes every deployment a pipeline test. Launcher hygiene: eleven demos install with `"hidden": true` manifests (a one-line change made the flag effective for SD-installed entries) and are fronted by one visible index app that filters the catalog for `d-` ids — the launcher gains one row, not twelve.

Supporting the suite required teaching the upload route to carry metadata: `?title=&subtitle=&hidden=1` query fields fill the manifest, and — after the first deployment produced mangled titles that could never be corrected — the policy that metadata in the query *rewrites* an existing manifest, while a bare push still never clobbers one.

## What the install gates caught

This section is the actual yield of ESP-57 so far. Four defects and one open regression, all surfaced by deploying the suite:

1. **A device crash: stack overflow in the httpd task.** The new manifest-writing path (a 224-byte query buffer, field buffers, and a FATFS `fprintf`) pushed the task past its 4096-byte default stack; FreeRTOS's overflow check tripped and rebooted the device after the first upload. The failure initially masqueraded as "the network went away" — it was identified only when the push was repeated with the console attached and the panic streamed into the transcript. The stack is now 6144, and the diagnosis pattern (uptime reset ≈ crash; reproduce with the console open) is in the diary.
2. **The query-encoding trap.** `&` in a title (`Type & Widgets`) split the upload query and silently ate the subtitle; and because the route deliberately does not URL-decode, `%26` arrives as literal text. Resolution at both ends: the push script percent-encodes properly, and suite titles are plain ASCII — with the route's no-decode behavior now documented as a contract rather than discovered as a surprise.
3. **Write-once manifests** made metadata mistakes permanent; the rewrite-on-metadata policy fixed the model.
4. **The directory-listing cap, again.** The suite's 24 files pushed `/sdcard/apps` past the 64-entry listing cap — the same failure class that silently hid a freshly installed app in the loader ticket, at the next ceiling. Now 128, but the second occurrence upgrades "should `files.list` paginate?" from an open question to a real debt.
5. **Open: a catalog-scan regression.** After the final platform flash, boot completes with a ROM-only catalog and no scan evidence line — `scanApps` exits through one of its silent error paths. Those paths are now instrumented with prints, but the instrumented build is unflashed: the device physically dropped off USB mid-flash (a known flaky connection). The investigation is parked at the hardware, with the suspicion list recorded: the `files.list` return path, module-callback interference from the upload watcher, or FATFS state after the earlier mid-write crash.

The honest status: the suite is implemented, all twelve uploads deploy cleanly, and the index — captured on the panel — lists all eleven hidden demos with correct metadata. The per-demo captures and the guide's closing sections wait on the USB connection and the scan fix.

## Current project status

ESP-56 is complete: tooling, audit, root cause, system, refactor, and the renderer fix, all verified by after-captures; doctor clean. ESP-57 is a working suite with a verified index, four platform fixes to its credit, one open regression, and three tasks remaining (per-demo captures, guide finalization, reMarkable upload). Commits: `3844a06d…4790c808` (ESP-56), `244293f2` + `4169296f` (ESP-57), one diary step per work session throughout.

## Important project docs

- Tickets: `esp32-s3-m5/ttmp/2026/08/20/ESP-56-PULP-DESIGN-SYSTEM--*/` (audit + baseline/after captures in `sources/`) and `ESP-57-PULP-DEMO-APPS--*/` (intern guide, diary, index captures).
- Capture pipeline: `main/app_shot.cpp`, `components/screenshot_qoi/`, ESP-56 `scripts/01-pulp-shot.py`.
- Design system: `tools/js/os/10-facade.js`; the m5 renderer fix in `components/s3paper_m5/src/m5_backend.cpp` (`BlitCoverage`).
- Demo suite: `tools/js/demos/*.js`, ESP-57 `scripts/02-push-demos.sh`; upload metadata in `main/net_serve.cpp`.
- Prior arcs: [[PROJ - PULP OS App Loader - Splitting the Monolith and Loading Apps as Source]], [[PROJ - PULP Browser - Multi-Context MicroQuickJS and the Sandboxed Page Runtime]].

## Open questions

- Should `files.list` paginate or stream, now that two caps have been outgrown in a week?
- Should the deny-by-default and design-idiom rules be enforced by generators/linters rather than review (the getter defect and the gutter both shipped through review)?
- The launcher itself now overflows (16+ visible apps clip at ~13 rows) — paging, scrolling, or curation?

## Near-term next steps

- When USB returns: flash the instrumented build, read the scan error, fix, re-walk all eleven demos with captures, finalize the ESP-57 guide, upload to reMarkable.
- Fold the demo-suite push into a routine acceptance step for stdlib changes.

## Project working rule

> [!important]
> Screens are judged as pixels, not as fingerprints: capture before claiming, re-capture after fixing. And the design lives in the API — an application that needs a raw pad, a bracketed button, or a private gutter has found a missing idiom, not a workaround.

## Related KB entries

- [[Research/KB/Projects/esp32]] — the ESP32 project map
