---
title: "PULP Browser — Multi-Context MicroQuickJS and the Sandboxed Page Runtime"
aliases:
  - ESP-55 phases 8-10
  - PULP page browser
  - PaperS3 browser
  - PULP UI sandbox
tags:
  - project
  - esp32
  - esp-idf
  - eink
  - microquickjs
  - firmware
  - sandbox
  - browser
status: active
type: project
created: 2026-08-20
repo: /home/manuel/code/wesen/go-go-golems/esp32-s3-m5/0114-papers3-pulp-os
---

# PULP Browser — Multi-Context MicroQuickJS and the Sandboxed Page Runtime

The previous stage of this project ([[PROJ - PULP OS App Loader - Splitting the Monolith and Loading Apps as Source]]) turned PULP OS applications into source files loaded on demand, installable over HTTP — under an explicit trust model: an installed application is operator code with the operating system's full authority. Phases 8 through 10 of ticket `ESP-55-PULP-APP-LOADER` built the piece that model could not cover: executing scripts the device fetches from arbitrary web servers. The result is a browser in the literal sense — the M5Stack PaperS3 requests a URL, receives a JavaScript file, and renders it — with one structural difference from the application loader: the fetched script runs in its own MicroQuickJS context whose standard library can only draw and navigate. Every filesystem, network, storage, and system call is rejected at the engine's native-dispatch layer. This report explains the multi-context runtime that carries this, the mechanism of the sandbox, the navigation protocol between the sandboxed page and the browser, and the live-network verification, including a hostile page that was contained exactly as designed.

> [!summary]
> - The binding layer moved from file-scope singletons to per-context state (`JsCtxState`), resolved in one load through the engine's context-opaque slot; the OS context is permanent, page contexts are created per navigation and destroyed on leaving.
> - The sandbox is a second `JSSTDLibraryDef` sharing the generated ROM object table — identical atoms, so pages parse exactly like applications — with a C function table in which more than one hundred natives are one `js_ui_denied` stub.
> - A page's only outward channel is `nav`, which records a request in a native mailbox and posts a completion delivered on a later owner-loop pass — deliberately outside the page's call frame, because the handler usually destroys the context that posted it.
> - Verified live: relative navigation between served pages, a clock page producing 39 timed presents from inside the sandbox, and a hostile page (filesystem calls, then an infinite loop) killed by the 3-second deadline onto the browser's error page with the launcher one swipe away.

## Why this project exists

The application loader ended with a documented gap. Its containment — deadlines, catchable out-of-memory, path sanitation, no execution at boot — bounds how badly a broken application can behave, but not what a *malicious* one may do: an installed module can call every native the OS can. That is an acceptable contract for code the operator installs deliberately. It is not acceptable for code a device fetches from a URL, which is precisely the capability that makes an e-ink terminal broadly useful: dashboards, menus, and status boards rendered server-side by anything that can print JavaScript, with no client release cycle.

The design (recorded in the ESP-55 intern guide as decision records R-MULTICTX, R-UISANDBOX, and R-PAGESCRIPT) therefore separates two axes that the single-context runtime had fused: *where a script executes* (its engine context, hence its heap, its globals, and its blast radius) and *what a script may call* (its standard library's function table). Phase 8 built the first axis, Phase 9 the second, and Phase 10 the product on top: the browser, plus a QR code on the Settings screen that hands the device's `pulp.local/apps` endpoint to a phone.

## Current project status

All three phases are implemented, committed one commit per phase with matching diary steps (17–19 in the ticket's diary), and validated on hardware over a live WiFi network against a reference page server. The built-in applications still run in the OS context exactly as before — phase 8 changed their runtime's plumbing, not their behavior, and the full regression gate (launcher fingerprint, probes, tap-walk) passed unchanged. Two new probes (27: multi-context mechanics; 28: the sandbox denial matrix, printed from inside a sandboxed page) joined the console harness. Not built, by choice: per-application contexts for the built-in apps (the machinery exists; the apps do not need it) and bytecode-format pages (the content-type switch is designed but source-only ships).

## The runtime model

### From singletons to JsCtxState

Before phase 8, the binding layer assumed one engine context. The page table, hit-region array, dynamic-text table, callback counter, home and sleep callbacks, and the page timer were file-scope globals in `main/app_js.cpp`, and thirty-odd call sites across the `js_*.cpp` translation units reached for them directly. The engine itself imposed no such limit: `JS_NewContext` takes its own arena, MicroQuickJS holds no mutable global state, and each context carries its own RAM atoms and its own single bytecode-image slot. The singleton assumption was an artifact of the bindings, and the refactor consisted of moving every one of those globals into one structure:

```c
struct JsCtxState {
    JSContext *ctx;  uint8_t *arena;  uint32_t arena_bytes;  CtxKind kind;
    PageEntry pages[12];   int32_t current_page;
    DynEntry  dyn[48];     uint32_t dyn_count;
    HitRegion hits[48];    uint32_t hit_count;
    int32_t next_cb, home_cb, sleep_image_cb;
    int64_t timer_due_us;
};
```

Two pointers name the roles: `g_os`, the permanent context holding the ROM bytecode image and every built-in application, and `g_fg`, whichever context currently owns the panel. Resolution is one indirection: the state pointer is stored in the engine's per-context opaque slot, read back by a four-line `JS_GetContextOpaque` accessor added to the vendored engine. A binding invoked by the engine already receives its `JSContext *`; `StateOf(ctx)` gives it its world.

### The ownership rules

Moving the state was mechanical. The design work was deciding who owns what, and each answer became one guard:

| Resource | Owner | Rule |
|---|---|---|
| The widget arena and panel | `g_fg` | `SwitchForeground` resets the arena (the outgoing context's widgets die by generation bump); `page.show()` from a background context *claims* the foreground — the browser's error-page path; `page.update()` from a background context is refused. |
| Gestures, ticks, dynamic text | `g_fg` | Dispatch reads the foreground's hit table, page cursor, and dyn table; callbacks run in the foreground's context. |
| Module completions (files, http, …) | The registering context | `g_module_cb` entries became `{owner, cb}`; delivery calls into the owner. Pages cannot register any (all such natives are denied), so in practice the owner is always `g_os`. |
| Web routes | `g_os`, always | Route handlers execute in the OS context regardless of what is foreground — a served page must never intercept the device's HTTP surface. |
| `resetTree()` | The calling context | Resets that context's tables; resets the shared arena only when the caller is the foreground; clears routes and completions only when the caller is the OS. |
| The home gesture | Enforced | If the foreground is not the OS and did not trap swipe-down — and a page *cannot* trap it, because `paper.home` is denied — control switches to the OS, a reclaim hook destroys the page context, and the OS home callback runs. The navigation grammar stops being a convention and becomes a property. |

Context teardown is the payoff of the model: `DestroyContext` frees the engine context and its arena in one step, which also releases every RAM atom the context ever interned — the atom-accumulation concern from the loader design simply does not exist for pages, because a page's atoms die with its context.

Probe 27 exercises the mechanics natively: a second 64 KiB context is created, a global defined inside it is invisible to the OS context (`os sees=undefined`), the callback counters advance independently, an allocation storm inside the small context raises a *catchable* out-of-memory while the OS context stays healthy, and PSRAM free space after teardown differs by zero bytes. One instructive wrinkle surfaced here: the probe initially caught the OOM exception and then crashed *reporting* it, because building the report string allocated from the still-full arena. The corrected probe collects garbage before constructing any message — a rule worth remembering wherever OOM is caught.

## The sandbox

### Mechanism: one ROM table, two function tables

MicroQuickJS dispatches native calls through an index into the context's `c_function_table`; the ROM object table (atoms, prototypes, classes) references natives by index, not by pointer. A stdlib is therefore separable into an immutable identity layer and a swappable capability layer, and the sandbox exploits exactly that. `main/js_stdlib_table_ui.c` re-emits the entire generated stdlib under preprocessor renames:

```c
static JSValue js_ui_denied(JSContext *ctx, ...) {
    return JS_ThrowTypeError(ctx, "not available to pages");
}
#define js_files_exists js_ui_denied
#define js_http_get     js_ui_denied
/* ... one hundred more: files, http, serve, wifi, mdns, images, apps,
   battery, buzzer, store, books, load, resetTree, paper.home/sleepImage/
   refreshTurns, browser.* ... */
#define js_stdlib js_stdlib_ui
#include "js_stdlib.h"
```

The properties this buys are exact. Because the ROM table — and with it the atom space — is byte-identical, a page script is the same dialect as an application module: the same compiler, the same parse, the same class IDs for `Widget` and `Page`. Because the denial replaces the function pointer, enforcement happens in the engine's call path; no JavaScript-level wrapping is involved, and there is nothing a page can reach around. What a page keeps: the full builder API (`page`, every widget factory and fluent method, canvas), `print`, `millis`, `gc`, the engine built-ins (`Math`, `JSON`, `String`, …), and `nav`. Everything else throws.

The one cost is a maintenance duty, stated at the top of the file as a rule: every native added to the stdlib is denied in pages by default; allowing one is an explicit edit to this file. The cost in flash is a second copy of the tables — accepted, against 14 MB of free flash.

### The navigation mailbox

A page needs exactly one outward capability: asking to go somewhere. `nav.go(url)`, `nav.back()`, and `nav.reload()` write a `{kind, url}` record into a native mailbox and post a `ModuleDone{Nav}` completion into the owner queue. The deferral is not an implementation convenience; it is the correctness property. The completion is delivered on a later pass of the owner loop, after the page's callback has returned — and the handler on the other side (the browser's watcher, in the OS context) typically responds by *destroying the page context that posted the request*. A direct call would tear down the stack it was executing on. The queue makes the teardown safe by construction.

```mermaid
sequenceDiagram
    participant PG as page context (sandbox)
    participant Q as owner queue
    participant BR as browser app (OS context)
    PG->>PG: user taps a row -> nav.go('clock.js')
    PG->>Q: mailbox={go,'clock.js'}; PostModuleDone(Nav)
    Note over PG: callback returns; page frame unwinds
    Q->>BR: later pass: watcher(kind=go)
    BR->>BR: re-arm watch, resolve URL against base
    BR->>BR: http.get -> cache /web/page.js
    BR->>PG: browser.run: destroy old ctx, create new, run main(ui, nav)
```

## The browser

### The page contract and the run sequence

A page is the application descriptor's sibling: one file evaluating to `({title, main(ui, nav)})`. `ui` is a small helper object (chrome, footer, tappable row) evaluated into every page context from a flash asset before the page runs — the shared cosmetic vocabulary, in plain JavaScript, costing the sandbox nothing. `nav` is the stdlib singleton described above. `browser.run(path, url)` — OS-side, denied to pages — executes the sequence:

```text
teardown previous page context
create context (96 KiB PSRAM arena, UI stdlib)  ->  kernel eval (__cbs, G)
eval page:ui-helpers                            ->  ui object
LoadInto(page script)                           ->  descriptor value
store descriptor as page-global __page          ->  roots it against the GC
driver eval: validate __page.main is a function
SwitchForeground(page context)
driver eval: __page.main(ui, nav)   [3 s deadline]
any failure at any step: teardown, foreground back to OS, error code
```

Rooting the descriptor as a context global and driving it with fixed eval strings deserves a note: the alternative — holding the descriptor `JSValue` in C locals across property reads and a native `JS_Call` — would have required manual GC rooting at every step, because the compacting collector moves pointer-tagged values. Storing it as a global and evaluating `__page.main(ui, nav)` delegates all rooting to the engine.

The browser application itself (`tools/js/apps/browser.js`, a ROM application like any other) contributes what the runtime does not: a URL keyboard with history, URL resolution (absolute, host-relative `/x`, directory-relative `x` against the current base), the fetch pipeline — `http.get(url).limit(32768)` into a cache file `/web/page.js` via the synchronous write native, then `browser.run` — and the failure surface: every error closes the page context and presents an error page whose `show()` reclaims the panel for the OS context. Caching the fetched source to a file makes the network path identical to the SD-application path; the browser adds no second loading mechanism. Remote driving completes the loop: `GET /apps/run?id=browser&url=<page url>` launches the browser onto a page in one request from a laptop.

### The QR surface

The requested `pulp.local/apps` handoff became a Settings screen. The URL is constant — mDNS makes it IP-independent — so the QR matrix (version 2, 25×25, error correction L) is precomputed by a host script and embedded as twenty-five row bitmask integers. Drawing met a real constraint: the canvas widget's command list holds 96 commands per slot, and the code's dark modules form 170 row-runs. The screen therefore run-length-encodes each row into `paint` rectangles and splits the matrix across two vertically stacked canvases at row 13 (86 and 84 commands). The same screen states whether the web server is running and prints the one-line `curl -T` push command.

## Verification

The live gate ran against `scripts/08-pulp-page-server.py` (a stdlib `http.server` seeding four demo pages) on a laptop sharing the device's network.

| Step | Evidence |
|---|---|
| Remote open: `curl "…/apps/run?id=browser&url=http://…:8123/menu.js"` | `js load: /web/page.js 571 bytes 6 ms`, foreground → page, `pulp screen: browser/…menu.js`, `/status` reports `"app":"browser"` |
| Tap a menu row → `nav.go('about.js')` (relative) | new page context, `browser/…about.js`, zero exceptions |
| Clock page: dyn text + 1 s tick inside the sandbox | **39 diff presents** over the observation window — the full present machinery works in a page context |
| Swipe-home, twice | `browser: page reclaimed (home gesture)`, launcher rebuilt |
| Hostile page: `files.remove`, `wifi.forget`, then `for(;;){}` | denials throw (no effect), loop killed at the 3 s deadline (`InternalError: interrupted`), browser error page (`page=bfail`), exactly one recorded exception, `dice.js` intact |
| Probe 28 (denial matrix, printed from inside the sandbox) | `files/http/serve/wifi/load/reset/paper/store/apps/browser` all `denied`; drawing and `nav.url()` work |
| QR screen via taps | `pulp screen: settings-web`, both canvases under the command cap, zero exceptions |

Two defects were found by the gates and fixed in place. The Settings Apps screen listed all fifteen installed applications before its action rows, pushing "Web install" below the 960-pixel panel edge — unreachable by construction; the action rows now come first. And the probe-27 report-after-OOM crash described above. Two tooling annoyances also recurred and are recorded in the diary: the hold-open console client exits silently when another instance still holds the port's advisory lock, and a `pgrep`-based wait loop matched its own command line — the same self-match trap the ESP-53 diary documented, hit again.

## What was deliberately not built

The built-in applications still share the OS context. The machinery to give each its own context exists and is exercised daily by the browser, but per-application contexts would require the `os` facade to be constructed per context (values cannot cross contexts) and cross-application calls to become native-mediated; nothing the current applications do justifies that cost. Bytecode-format pages — feasible, since each fresh page context has an unused image slot — wait for a demonstrated need for the parse-time savings; source pages load in 6 ms. The deny list is enforced by review plus the stated default-deny rule; pushing it into the stdlib generator remains the correct hardening step.

## Important project docs

- Ticket: `esp32-s3-m5/ttmp/2026/08/17/ESP-55-PULP-APP-LOADER--*/` — intern guide §6.11/§6.12 (the designs these phases implement), diary steps 17–19, gate transcripts.
- Runtime: `main/app_js_internal.h` (JsCtxState + lifecycle API), `main/app_js.cpp`; sandbox: `main/js_stdlib_table_ui.c`; page runtime: `main/js_browser.cpp`; browser app: `tools/js/apps/browser.js`; page assets: `tools/js/pages/`.
- Tools: ticket `scripts/08-pulp-page-server.py` (reference server + demo pages incl. the hostile page), `scripts/09-gen-qr.py`.
- Commits: `6002cc63` (P8) → `61dc5daf` (P9) → `bdc24837` (P10), one diary step each.
- reMarkable: `/ai/2026/08/17/ESP-55-PULP-APP-LOADER/ESP-55 Final Guide and Diary v3.pdf`.

## Open questions

- Should served pages get a capability *grant* mechanism (per-origin allowlists unlocking, say, read-only battery state), or is the draw-and-navigate contract the permanent line?
- The browser trusts `Content-Type` implicitly by ignoring it; when bytecode pages arrive, the type switch must also decide what happens to a page that lies about its format.
- Page contexts are 96 KiB by fiat; no page has come near it. Worth revisiting only with data.

## Near-term next steps

- A probe for `nav.back`/`nav.reload` delivery ordering (exercised live, not yet in the fixed harness).
- A `--wait` flag on the hold-open console client (the flock-collision silent exit cost two empty transcripts).
- Refresh the ESP-53 onboarding guide's stdlib section to mention the two-table arrangement.

## Project working rule

> [!important]
> What a script may call is a property of its context's function table, never of its source or transport. Pages draw and navigate; every other native is one stub that throws — and any new native is denied to pages until someone edits the deny file to say otherwise.

## Related KB entries

- [[PROJ - PULP OS App Loader - Splitting the Monolith and Loading Apps as Source]] — phases 0–7: the loader, catalog, and HTTP install this runtime builds on
- [[PROJ - PULP OS Image Gallery - mDNS Browser Upload and the Bitmap Blit]] — ESP-54, the preceding ticket
- [[Research/KB/Projects/esp32]] — the ESP32 project map
