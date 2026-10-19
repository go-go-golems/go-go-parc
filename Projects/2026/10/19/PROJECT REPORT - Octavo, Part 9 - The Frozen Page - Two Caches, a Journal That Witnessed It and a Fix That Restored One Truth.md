---
title: "Octavo, Part 9: The Frozen Page — Two Caches, a Journal That Witnessed It, and a Fix That Restored One Truth"
aliases:
  - OCTAVO frozen page
  - octavo two caches bug
  - octavo page forensics
tags:
  - project
  - handheld
  - debugging
  - event-sourcing
  - observability
status: active
type: project
created: 2026-10-19
repo: /home/manuel/code/wesen/2026-10-17--octavo
ticket: OCTAVO-002
source_commit: e4a74a0
---

# Octavo, Part 9: The Frozen Page

The reader reported that some pages of the chapter do not load and that A sometimes does not open what is selected. This report follows the investigation that found the cause: a page cache in the JavaScript runtime and a page cache in the C++ process, each with its own eviction policy, and a code path that let the two disagree about which pages exist. The disagreement produced presses that were recorded in the journal but changed nothing on the screen.

By the end of this report you should understand three things: why the journal made the symptoms visible as reader behaviour before the cause was known; what observability was missing and how it was added; and the exact mechanism by which two caches with different capacities froze the reader's screen. The report closes with the fix, the reason no test had caught the defect, and the state of the project's documentation as assessed during the investigation.

The work is ticket OCTAVO-002 in the repository at `1f246af` plus its commits `d7eaa4a` (page forensics), `ada9cb2` (the assessment), `70b556f` (the scratch-to-LLM tasks) and `e4a74a0` (the fix).

## 1. Terms

- **Page.** One element tree laid out to a display list, named by its **page key**: `fnv64(layoutId + "\n" + treeText)`. The same key names the page in JavaScript, in C++ and on disk.
- **PageStore.** The C++ process's cache of laid-out pages: a least-recently-used list of 64 in memory (`kKeep = 64`), then the read-only install tree's prebuilt pages, then a writable cache directory, then the layout helper.
- **The runtime's page cache.** The JavaScript `Runtime`'s `pages` map: tree text to page, most recent last, at most 96 entries. It exists to save rebuilding a page's `spanById` index on every update.
- **`shown`.** The runtime's map of slot name to the page key it believes that slot displays. `update()` compares it against the page it is about to present to decide whether a `present` message is needed.
- **Present.** The message that tells the main thread to show a page key in a slot. It carries only the key; the C++ side resolves the key to the page through the PageStore.
- **States.** The message that carries one page's complete span states: state colour and bits (focus underline, strike, the shown variant of an `alt` pair) per span id.
- **The journal.** `events/<YYYY-MM>.jsonl` under the data directory: every event the runtime emits, appended before the screen changes. A crash or a `SIGKILL` loses nothing that was shown.
- **Folds.** Derived state updated one journal event at a time: seen and mastered cards, the last card, review boxes, open flow sessions.
- **`--log-pages`.** The page forensics this ticket added: one line per layout, present, states, GPU-page upload and eviction, and one line per button press naming the view, card, peek depth, focus id, tab and running flow.

## 2. The reports and the first hypotheses

The reader's report was concrete but came without a trace: "some pages of the chapter don't really load", "sometimes A doesn't properly go to the selected part", "weird stuff". The Anbernic RG DS Plus runs the install tree deployed at commit `09637ca`'s runtime plus `6861a67`'s prebuilt layouts — the same runtime code as the repository's head, verified by `deploy.sh`'s layout-id check.

Two structures existed to find the cause. The journal holds every event as behaviour, but it cannot hold what the *screen* showed. The app's own log held per-press latency lines, GPU timings and errors — but `run-octavo.sh` truncated it on every start, so the reading sessions' logs were gone. Only the journal had survived.

The journal showed the symptoms plainly:

| What the reader experienced | What the journal shows |
| --- | --- |
| "A doesn't go to the selected part" | oscillation between adjacent cards: `cofinite → two-origins → cofinite → sierpinski → homeomorphism → sierpinski` (2026-10-19 01:01:29–:31) |
| "pages don't really load" | `card.open` of the same card at one-second intervals: `compact-closed` six times between 22:50:41 and 22:52:24; `sheafification` three times between 01:00:09 and 01:00:19 |
| hypothesis strikes vanishing | `hypothesis.toggle T2 off:true` five times in one session (22:34, 22:36, 22:44, 22:45, 22:49) with no `off:false` between |

A `card.open` is written when the runtime processes the press, not when the screen changes. A reader who presses again and again and sees nothing move produces exactly this pattern: the journal runs ahead of the screen. That separation — meaning recorded, drawing not — became the working hypothesis for everything that followed.

## 3. What the host walks ruled out

The runtime's JavaScript was exonerated before the device was touched. Three walks ran the shipped device book (Topology and Sheaves, chapters 5 and 8, 17 cards) with the real typesetter:

1. **The full walk** (ticket script 01): every card, the contents, both Leitfadens; A pressed on every focusable span (66 of them); D-pad walks right and down through every page; L/R paging through the whole book; every `[[link]]` resolved. No layout error, no press that did nothing, every A went to its span's own target, every page prebuilt.
2. **The history walk** (script 02): three simulated days of reading — cards seen, one mastered through the exercise, review cards added and graded, quest hints taken, a review session left open by a quit — then a boot with `restore` and `resume`. The review resumed at its second card, the quest at hint tier 2, and every contents row opened the right target.
3. **The drop-survival walk** (script 03): drop a hypothesis, peek, pop, page away, page back, hub, back. The strike — span state `[3, 2]`, dimmed and struck — survived every step.

The 38-file test suite passed throughout. The same drop-survival sequence ran on the device through the control FIFO, with screenshots before and after: the strike survived there too, in a fresh session. The state machine was sound; the failure needed conditions a fresh session does not reach.

## 4. The observability that was missing

The investigation could not go further without seeing pages move. Three gaps:

1. The log showed that a press completed and how long it took, but not which page it presented, which states it sent, or where the focus was.
2. The log was truncated on every start, so the evidence of past sessions was destroyed by the act of looking for it.
3. Under `--dev` the dev link streams presents, states and events — but the reader's real sessions do not run under `--dev`.

The fix was `--log-pages` (commit `d7eaa4a`), on by default in `run-octavo.sh`, off with `OCTAVO_LOG_PAGES=0`. The script thread now logs one line per layout — `page set <key> <source> <ms>`, with the source among memory, prebuilt, cache and helper, or the layout error — one per present — `page present <slot> <key> anim scroll` — one per states message — `page states <key> (found, n)` — and the main thread logs every GPU page it creates (`gpu upload <key> (states zeroed)`: a fresh GPU page starts with all span states zero) and every eviction. `main.js` logs one line after each button press:

```
press A: view=read card=compact-closed peek=0 focus=compact-closed/h:T2:0 tab=aside aside
```

`run-octavo.sh` now keeps the previous session's log as `/tmp/octavo.log.1` instead of truncating it. The reader's next session was the test.

## 5. The catch

The reader read normally with the new build. On card 10 of 17, L stopped going back; after more presses the screen arrived at card 7. The log held the whole mechanism:

```
[js error] Error: present: no page 09cc5cafd18a335b
    at DeviceHost.present (js/host/device.js:52:14)
    at Runtime.present (js/core/runtime.js:422:17)
    at Runtime.update (js/core/runtime.js:462:14)
[js info] press L: view=read card=topological-space peek=0 focus=- tab=chat
page states 9a7e3ad8efd46165 (found=0, n=2)
[js error] Error: present: no page 9a7e3ad8efd46165
    at DeviceHost.present (js/host/device.js:52:14)
    at Runtime.present (js/core/runtime.js:422:17)
    at Runtime.update (js/core/runtime.js:462:14)
[js info] press L: view=read card=two-origins peek=0 focus=- tab=chat
page present top.main 2dbc97cd32ed50ff anim=page-prev scroll=0
[js info] press L: view=read card=cofinite peek=0 focus=- tab=chat
```

Read as a sequence: the reader pressed L on card 10 (presheaf). The runtime's state moved to card 9 (topological-space) and the press was journaled — but the present threw `present: no page 09cc…`. The next L moved the state to card 8 and journaled again — and threw again, and its states message found no page (`found=0`, silently dropped). The third L moved the state to card 7 (cofinite), and this time the page presented with the `page-prev` animation. The screen jumped from card 10 to card 7 across three presses; two of them had been invisible.

The two `present: no page` throws are the whole defect, and the trace names where: `Runtime.present`, called from `Runtime.update`, through `DeviceHost.present`. The states line with `found=0` is the companion failure: the message C++ could not resolve and silently dropped.

## 6. Two caches, one truth

Why does `present` carry only a key? Because by the time a page is presented, both sides are supposed to agree that the key names a laid-out page: the JavaScript runtime asked for the layout (through `host.set`), and the C++ PageStore answered. The present message is the pointer to that agreement.

The runtime, however, kept its own cache, and the cache had a short-circuit:

```js
let page = this.pages.get(text);
if (page) { this.pages.delete(text); this.pages.set(text, page); return page; }   // no host.set
page = this.host.set(tree, text);
```

A JavaScript cache hit returned without calling the host. The device's PageStore keeps 64 pages; the runtime's cache kept 96. In a session long enough — the reader's was 184 presses — the earlier cards' pages left the C++ store while the runtime's cache still held them. Paging back to such a card took the short-circuit path: the C++ store never re-learned the page, and `present(key)` threw.

The throw alone would cost one press. The freeze came from the second half of the mechanism, in the runtime's `present`:

```js
present(slot, page, opts) {
  if (this.shown[slot] === page.key && !(opts && opts.force)) return;
  this.shown[slot] = page.key;              // before the host call
  this.host.present(slot, page.key, opts || {});
}
```

`shown[slot]` is set before the host call. When the host call throws, the runtime believes the slot shows the new page although no present message was delivered. `update()` decides whether to present with

```js
const fresh = !this.page || page.key !== this.page.key || this.shown['top.main'] !== page.key;
```

and skips the present whenever `shown` already says the key. After the poisoned `shown`, every later update of that page was suppressed until a *different* page came through the slot — the third L in the trace, the one whose page was outside the runtime cache and therefore took the fresh `host.set` path.

The reader's earlier symptoms follow directly. Presses that journal but change nothing are exactly this throw with the poisoned `shown`. The paging oscillation is the reader's answer to a screen that changes on some presses and not others: press the other direction, press again, lose track of which card is shown. The five re-drops of the hypothesis are consistent with the same lost-screen confusion; a restart between them (the package state is in-memory only, and a boot's `card.open` is indistinguishable from a home press in the journal) remains the other candidate, and the kept log will show it if it happens again.

## 7. The fix

One principle fixes the mechanism: **there is one truth about which pages exist, and it lives on the host side.** The runtime's cache may save work, but it may not decide that a layout will not be asked for (commit `e4a74a0`):

1. `Runtime.set()` always calls `host.set`. The cache is now only a memo for `spanById` and the LRU position of tree texts — never a short-circuit for the layout call. The device's memory hit is a splice; the twin's WASM layout is memoized inside the module; Node's test host (`SetHost`) gained the same by-key memo so the tests stay fast.
2. `Runtime.present()` sets `shown[slot]` after the host call. A throw leaves `shown` pointing at the page that is actually displayed, and the next update re-presents.
3. The `states` native in `script.cpp` logs loudly whenever a message names a page the store does not have — the `found=0` case is a broken invariant, not a condition to swallow.

```js
set(tree, transient) {
  const text = JSON.stringify(tree);
  const page = this.host.set(tree, text, transient);     // always: the host's store keeps its LRU fresh
  if (transient) { page.spanById = new Map(page.spans.map(s => [s.id, s])); return page; }
  let cached = this.pages.get(text);
  if (cached && cached.key === page.key) {               // the same page: reuse its spanById
    this.pages.delete(text); this.pages.set(text, cached); return cached;
  }
  page.spanById = new Map(page.spans.map(s => [s.id, s]));
  this.pages.set(text, page);
  if (this.pages.size > 96) this.pages.delete(this.pages.keys().next().value);
  return page;
}
```

On the device, the reader's exact sequence — fourteen presses forward to the end of the book, fourteen back — now runs with zero throws and zero dropped states, the screen following every press. The 38-file suite and all three walk scripts stay green.

## 8. Why no test caught it

Every scripted path keeps its sessions short enough that all pages stay inside both caches. The parity runs replay button sequences from a fresh journal on both the twin and the device; the prewarm walk runs once per build; the unit tests press dozens of times, not hundreds. The defect needed a session long enough to cross the C++ store's eviction boundary *while* the runtime's cache still held the earlier pages — a real reader's evening. Two design choices hid it further: the journal records meaning, not drawing, so the symptom looked like reader behaviour; and the log was truncated on every start, so the error's stack trace never survived to be read. The lesson for the tests is not another scripted sequence but a soak walk: hundreds of presses with assertions on the log's absence of `present: no page` — now cheap to write against the forensics.

## 9. The documentation, assessed

The investigation doubled as an assessment of where to find things and what the project's writing claims. The full record is `code-and-docs-assessment.md` in the ticket; the findings that matter to a reader of this vault:

**What carried the investigation.** The whole-system report (Part 9's predecessor of 2026-10-19) proved accurate against the code at every point checked: the architecture, the host-function tables, the cache design, the journal's guarantees. The OCTAVO-001 diary's 33 steps allowed resuming the project's state in minutes, and its recorded open questions (prewarm's first-screen gap, the helper's three unreachable pages) were directly relevant. The journal-plus-folds design is the best documentation in the repository: it documents itself by construction, and it is what made the symptoms visible at all. The Node hosts made host-side reproduction of the exact shipped book a one-liner.

**What misleads.** `README.md` says the native program is "planned, not written yet" and lists `js/`, `set/`, `native/` and `dev/` as "planned" — all are implemented; the README describes the repository of the design session, not the repository that exists. No single place lists the device's paths — the install tree at `/storage/apps/octavo`, the journal and caches at `/storage/octavo`, the log, the control FIFO, the lock — so debugging runtime state requires reading three files. The report's §9.2 mentions `/storage/octavo` once, late. There is no debugging-on-the-device guide at all: what the log holds, what `stats` prints, how to press and screenshot through the FIFO, and, now, what `--log-pages` writes.

**What to write next.** The README's "What is here now" should describe the tree that exists, with the whole-system report as the map. One paths table should exist — install tree, data, log, FIFO, lock, with the note that `/tmp` is tmpfs. A debugging section should cover the journal, the log, the FIFO, `stats`, screenshots and the page forensics. The host-function table now exists in four places (`script.cpp`'s comments, `host/device.js`, the report §6.2 and the report's §7.2 host interface) and they drift; one should be canonical.

## 10. What is still open

- **The hypothesis re-drops.** The five `off:true` events in one session are consistent with the frozen-page confusion and with restarts; the package state is in-memory only, and a boot is invisible in the journal. A `boot.start` journal event — one line in `boot()` — makes every restart visible from now on.
- **`home`'s invisible re-emit.** HOLD_B re-shows the last card even when that card is already on screen: a `card.open` is journaled and nothing changes. Either no-op the case or do not re-emit.
- **Scratch to the tutor.** Sending the drawn page to the model is the designed but unbuilt "transform on ink": `ink.snapshot()` is a stub, the compass's transform is dimmed, "submit page" answers that the handheld sends text only. The pieces exist — PNG rendering and encoding on the device, base64 in the JSON body, a vision-capable `--model` — and the tasks are written.
- **Circle and ask.** Drawing over the card works (the swap's memo surface); a lasso opens the compass with an ink-region selection, but the model is told only "N strokes of ink" — nothing resolves the lasso to the spans and text underneath. For terms, hypotheses and cross-references that resolution is JavaScript-only (the rects are in the display list, the labels in the builder), and it would make "circle it and ask" work with a text-only model. The chat tab has no ink surface at all.

## 11. Key points

- A journal that records meaning, not drawing, made the symptoms visible as reader behaviour before the cause was known — and hid the difference between a processed press and a drawn one.
- Observability must survive the restart it is asked to explain: the truncated log destroyed the evidence of every real session; keeping it one generation back is one line.
- Two caches for the same objects need one eviction policy, or a rule for which one decides existence. The runtime's short-circuit (`if cached, skip the host`) let the two disagree; the fix makes the host's store the single truth and the runtime's cache a pure memo.
- Set state that claims success before the operation (`shown[slot] = key` before `host.present`) converts a transient error into a persistent one: the next update believes the work is done.
- A defect that needs a long session will not be found by short scripted runs; soak walks against the new forensics are the test to add.
- The documentation that helped was accurate, structured and current; the documentation that misled was stale, scattered or absent. The gap between the repository's writing and its code is itself a defect, and it is fixable in an afternoon.
