---
title: "ARTICLE: Nested-Scroller History Restoration in a React SPA — Three Fixes and the Trap They Avoided"
aliases:
  - scroll restoration nested scroller
  - PV-SCROLL-024 implementation
  - scroll restoration review fixes
tags:
  - article
  - frontend
  - react
  - routing
  - scroll-restoration
  - history-api
  - publish-vault
status: active
type: article
created: 2026-08-16
repo: /home/manuel/workspaces/2026-08-15/better-index-links/publish-vault
---

# ARTICLE: Nested-Scroller History Restoration in a React SPA — Three Fixes and the Trap They Avoided

This article documents the implementation of back/forward scroll restoration for a React single-page application whose reading position lives in a nested scroll container, not the window. The application is `publish-vault`, an Obsidian-vault publisher with a fixed app shell (`h-screen overflow-hidden`) and a nested `ScrollArea` that holds the note body. The browser's native `history.scrollRestoration` only restores window scroll, and `window.scrollY` is always zero in this layout, so the application must own restoration.

The work addressed three code-review comments on a pull request and, in doing so, hit a fourth problem that an earlier attempt had already failed on. The article explains the system, the three fixes, the fourth trap, and the model that makes the fixes correct. It is written for an engineer who will modify or review this code.

> [!summary]
> - The unit of scroll restoration is the browser history entry, not the note slug or the URL. Three review comments were symptoms of missing abstractions: storage lifetime, entry identity, and restoration readiness.
> - The fixes are: a module-level offset store that survives route unmount; a composite identity `key + "|" + hash` with a `hashchange` re-render so native fragment navigation is captured; and a restore predicate on `scrollHeight - clientHeight` (the maximum valid `scrollTop`) instead of `scrollHeight`.
> - The decisive fix was neither of the three review comments. The scroll listener had to be attached to the document in the capture phase, because the React ref passed to the hook was not an ancestor of the visible scroller. Binding to the ref silently never attached, and back navigation restored to zero.
> - Continuous save keyed by the live `window.location.hash` is what makes fragment-back work. A save-on-key-change effect alone races the heading permalink's smooth scroll and captures the post-jump position.

## Why this note exists

The triggering work was PR #21 on `go-go-golems/publish-vault`, which introduced a custom scroll-restoration hook. A code review left three comments, and an earlier attempt to address them regressed a previously working flow. A separate fundamental review (`PV-SCROLL-REVIEW-025`) diagnosed the underlying traps. This note preserves the implementation that resulted — the three fixes plus the scroller-discovery fix — so a future engineer understands why each piece exists and which ones remain open.

The reusable knowledge is the model of how React Router identity, browser history, native fragment mutation, and nested-scroll geometry interact. The specific files are the concrete instance of that model.

## The system under repair

### The app shell does not scroll

The app shell is a fixed-height, overflow-hidden layout (`VaultLayout.tsx:121`). The note body is rendered inside a `ScrollArea`, which is a thin `div` with the `retro-scroll` class and overflow styling (`ScrollArea.tsx:15-30`). The visible article scroller is this nested element, marked with a `note-scroll` class by `NotePage` at three call sites: the desktop split-pane article, the desktop no-panel article, and the mobile article (`NotePage.tsx:149,172,185`).

Because `window` never scrolls, `history.scrollRestoration = "auto"` is a no-op. The hook sets it to `"manual"` and takes ownership of restoration.

### The scroller is not a stable DOM node

`NotePage` is the `/note/*` route element, but it returns early during loading and error states. The `isLoading` branch returns a spinner before the article `ScrollArea` is rendered (`NotePage.tsx:99-106`). The scroller therefore appears and disappears as notes fetch. A hook that reads `scrollTop` at location-change time would find `null` on navigation to an uncached note, because the source scroller has already unmounted.

The hook is placed in `NotePage` before the early returns (`NotePage.tsx:65-66`) and receives `ready = !!note`. It re-binds whenever `ready` flips. This placement is correct for the within-route case but, as the first review comment observed, insufficient for route exit.

### Fragment navigation has two owners

Cross-note wiki links flow through React Router: a click becomes `navigate('/note/' + slug)`. Generated heading permalinks do not. The heading anchor handler in `noteEnhancements.ts` sets the fragment and scrolls directly:

```ts
anchor.addEventListener("click", e => {
  e.preventDefault();
  window.location.hash = id;
  heading.scrollIntoView({ behavior: "smooth", block: "start" });
});
```

This advances the browser history stack without going through React Router, so React Router's `location.key` does not change. The hook's save effect, keyed on `location.key`, would not fire for this transition, and the pre-jump offset would be lost. A third owner exists: `NoteHtml` has a 200 ms timer that scrolls to a heading on hash navigation. The fixes below address the first two; the third remains a known competing owner documented as a follow-up.

## The three review comments and their fixes

### Fix 1: persist offsets outside the route component

The original hook held the saved-offsets map in a `useRef`:

```ts
const saved = useRef<Map<string, number>>(new Map());
```

A `useRef` is destroyed when its owning component unmounts. The `/search` route is a sibling of `/note/*` (`App.tsx:78-83`), so navigating note → search unmounts `NotePage` and destroys the map. Pressing back creates a fresh, empty map, and the note scrolls to the top. Meanwhile `history.scrollRestoration` remains `"manual"`, so the browser cannot compensate.

The fix replaces the ref with a module-level store:

```ts
const savedOffsets = new Map<string, number>();
```

A module-level `Map` survives `NotePage` unmount because it is not owned by any component. It is mutated only inside effects, so server-side `renderToString` (which runs no effects) never touches it. An unmount cleanup writes the active offset for the no-trailing-event case:

```ts
useEffect(() => {
  lastKey.current = scrollKey;
  return () => {
    if (lastKey.current != null) {
      savedOffsets.set(lastKey.current, lastOffset.current);
    }
  };
}, [scrollKey]);
```

This closes the storage-lifetime dimension. The store now outlives every route whose position it remembers.

### Fix 2: include the fragment in the scroll identity

The original save effect depended only on `location.key`:

```ts
useEffect(() => { /* save under lastKey */ }, [location.key]);
```

Because heading permalinks set `window.location.hash` directly, a same-note fragment change can create a history step without changing `location.key`. The save effect never fires, and back to the unhashed state has no saved offset.

The fix introduces a composite identity and a re-render trigger:

```ts
export function scrollKeyOf(location: ScrollLocation): string {
  return `${location.key}|${location.hash}`;
}
```

A `hashchange` listener forces a re-render so the identity updates even when React Router's location does not:

```ts
useEffect(() => {
  const onHash = () => setHashTick(t => t + 1);
  window.addEventListener("hashchange", onHash);
  return () => window.removeEventListener("hashchange", onHash);
}, []);

const currentHash = typeof window !== "undefined" ? window.location.hash : "";
const scrollKey = scrollKeyOf({ ...location, hash: currentHash });
```

The save effect now depends on `scrollKey`, so a hash-only change fires it.

This composite identity is a surrogate, not a full fix. Repeated identical fragment visits (`A → A#x → A → A#x`) can still collide if the native hash navigation reuses the router key. The robust fix is router-minted per-entry keys, documented as a follow-up. The composite key addresses the review comment without that larger change.

### The non-obvious part of fix 2: continuous save

The save-on-key-change effect alone is insufficient for smooth-scroll fragment navigation. The heading permalink sets the hash, then calls `scrollIntoView({ behavior: "smooth" })`. The smooth scroll fires many events over roughly 300 ms. By the time the `hashchange` re-render fires the save effect, the smooth scroll has already updated the captured offset to the post-jump position, so the save stores the heading's position, not the reader's pre-click position.

The fix is to save continuously in the capture listener, keyed by the live hash read at event time:

```ts
const onScroll = (e: Event) => {
  const el = e.target as HTMLElement | null;
  if (el && el.classList.contains("note-scroll")) {
    const y = el.scrollTop;
    lastOffset.current = y;
    const liveHash = typeof window !== "undefined" ? window.location.hash : "";
    savedOffsets.set(`${location.key}|${liveHash}`, y);
  }
};
```

Because the permalink sets the hash before it scrolls, the jump's scroll events carry the hashed identity, and the unhashed identity retains the reader's pre-click offset. This is the single invariant that makes fragment-back work, and it is not visible from the save effect alone.

### Fix 3: wait until the offset is actually scrollable

The original restore loop waited on content height:

```ts
if (scroller.scrollHeight >= offset || tries++ > 60) {
  scroller.scrollTop = offset;
  return;
}
```

The maximum valid `scrollTop` is `scrollHeight - clientHeight`, not `scrollHeight`. The predicate `scrollHeight >= offset` can be true while the offset is still unreachable, so the assignment clamps to a smaller maximum and the loop exits. Later content growth, such as asynchronously resolved embeds, is never re-applied.

The fix tests the available scroll range:

```ts
const maxScroll = scroller.scrollHeight - scroller.clientHeight;
if (maxScroll >= offset || tries++ > 60) {
  scroller.scrollTop = offset;
  return;
}
```

The 60-frame bailout remains; it is a deadline, not a readiness signal, and a follow-up would replace it with a `ResizeObserver`. For the current content, the corrected predicate is sufficient.

## The trap the three fixes did not address

The three fixes are correct, but the earlier attempt to apply them regressed cross-note back navigation to zero. The cause was a fourth problem: the scroll listener was bound to the wrong element.

### The symptom

During verification, a debug probe showed that the React ref passed to the hook (`containerRef.current`, a `div.h-full` in `NotePage`) was not an ancestor of the visible `.note-scroll`:

```text
listener.rootIsAncestor === false
```

A capture-phase listener attached to that root would never receive the scroller's scroll events, because scroll events do not bubble and the scroller was not in the root's subtree. The captured offset stayed at zero, and back navigation restored to zero.

### The cause

`NotePage` attaches its `layoutRef` to a `<div className="h-full">` that wraps the desktop and mobile layouts. Logically, the article scroller is a descendant. In the running application, the visible scroller's ancestor chain passes through a `SplitPane` (a `ResizablePanelGroup`) whose DOM is not a descendant of the `containerRef` node the effect captured. The application uses `React.StrictMode` and a lazy-then-eager `NotePage` resolution in `entry-client.tsx`, which can produce transitional or duplicate trees. The ref pointed at a `div.h-full` that was not the ancestor of the scroller the user actually saw.

### The fix

The listener is attached to the document in the capture phase, filtered by the `note-scroll` class:

```ts
document.addEventListener("scroll", onScroll, { capture: true, passive: true });
```

Scroll events do not bubble, but they traverse the capture phase, so a document-level capture listener catches every `.note-scroll` scroll regardless of which React tree renders it. The restore target is found the same way, by querying `document.documentElement` rather than the ref:

```ts
const scroller = findVisibleScroller(document.documentElement);
```

This removes the dependency on the ref's ancestry. The class filter keeps the listener scoped to article scrollers; a grep confirms only the three `NotePage` article `ScrollArea`s use the `note-scroll` class.

## The pure policy

The two pure functions are unit-tested in the node environment, because the web test runner is `environment: "node"` and supplies no DOM:

```ts
export function scrollKeyOf(location: ScrollLocation): string {
  return `${location.key}|${location.hash}`;
}

export function pickScrollAction(
  location: ScrollLocation,
  saved: Map<string, number>
): ScrollAction {
  if (!location.pathname.startsWith("/note/")) return "none";
  if (location.hash) return "hash";
  if (saved.has(scrollKeyOf(location))) return "restore";
  return "top";
}
```

The precedence is `hash > restore > top`, with `none` for non-note routes. Twelve tests cover `scrollKeyOf` (combination, same-key fragment distinction, cross-note distinction) and `pickScrollAction` (restore, top, hash-beats-restore, hash-beats-top, non-note, route prefix, key distinction, hashed-state isolation).

The pure policy is necessary but not sufficient. All three review comments involve lifecycle, history, or geometry, none of which the pure tests exercise. The hook is verified manually on the real vault.

## Verification

The implementation was verified in a browser at a 1200×400 viewport, which makes the fixture note scrollable (maximum scroll 222 pixels). The test offset was 150. Three scenarios were run, each setting the scroller to 150, navigating away, and pressing back:

| Scenario | Navigation | Required result | Observed |
|---|---|---|---|
| Same-note fragment back | Click `#about-this-system` permalink, back | Restore 150 | 150 |
| Note to search back | SPA-navigate to `/search?q=welcome`, back | Restore 150 (store survives unmount) | 150 |
| Note to note back | SPA-navigate to another note, back | Restore 150 (no regression) | 150 |

The first scenario was zero before fix 2; the second was zero before fix 1; the third was zero in the earlier attempt before the document-capture-listener fix.

The build gates pass: `tsc --noEmit` clean, 38 vitest tests pass, prettier clean, vite build clean, and the lefthook pre-push hooks (web-check, gosec, lint, test) passed on push.

## What remains open

The three fixes close three of seven dimensions identified in the fundamental review. Four remain, and two carry the highest risk:

- **Navigation-type policy.** The policy is `hash > restore > top` with no knowledge of `POP` versus `PUSH`. This is wrong for the flow: land on `#heading`, scroll down to `y=900`, navigate away, press back. The correct result is `y=900`; the current policy restores the heading. The fix is a reducer driven by `useNavigationType()` where `POP + snapshot → restore` takes precedence over `fragment`.
- **Scroller discovery by class query.** `findVisibleScroller` queries `.note-scroll` and selects `clientHeight > 0`. The document-capture listener removed the binding trap, but the restore target is still found by class query. The robust fix is explicit element registration, modeled on TanStack Router's `data-scroll-restoration-id`, so the scroller is registered by id rather than discovered.
- **Composite-key collision.** `key + "|" + hash` can collide on repeated identical fragment visits. The robust fix is router-minted per-entry keys, which requires routing fragment navigation through React Router instead of `window.location.hash`.
- **Competing fragment owners.** `NoteHtml`'s 200 ms fragment scroll and the heading permalink's direct `scrollIntoView` both scroll independently of the hook. One coordinator should own restore, fragment, and top.

These are documented in `PV-SCROLL-REVIEW-025` and in the diary. They are follow-ups, not blockers for the three review comments.

## Working rules

- The unit of restoration is the history entry, not the URL. Two visits to the same URL are two entries.
- Storage lifetime must exceed the lifetime of every route whose position it stores. A module-level store outlives `NotePage`; a `useRef` does not.
- When a navigation path bypasses the router (native `window.location.hash`), the identity must include what that path changes. `scrollKey` includes the hash; a `hashchange` listener keeps it current.
- A save-on-identity-change effect races any asynchronous scroll that the identity change triggers. Save continuously, keyed by the live identity read at event time.
- The maximum valid `scrollTop` is `scrollHeight - clientHeight`. Test the available range, not the content height.
- A React ref is not guaranteed to be an ancestor of the element you want to observe. When in doubt, listen on the document in the capture phase and filter by class.
- Pure policy tests do not cover lifecycle, history, or geometry. Verify the hook on the real DOM.

## File references

| Concern | File |
|---|---|
| Implementation | `web/src/lib/scrollRestoration.ts` (commit `2e2ae67`) |
| Pure policy tests | `web/src/lib/scrollRestoration.test.ts` (12 tests) |
| Hook wiring | `web/src/components/pages/NotePage/NotePage.tsx:60-66` |
| Article scrollers | `web/src/components/pages/NotePage/NotePage.tsx:149,172,185` |
| Native fragment mutation | `web/src/components/organisms/NoteView/noteEnhancements.ts:185-203` |
| Physical scroller | `web/src/components/atoms/ScrollArea/ScrollArea.tsx:15-30` |
| Route lifetime | `web/src/App.tsx:67-101` |
| Fundamental review | `ttmp/2026/08/16/PV-SCROLL-REVIEW-025--.../design-doc/01-...md` |
| Implementation diary | `ttmp/2026/08/15/PV-SCROLL-024--.../reference/01-implementation-diary.md`, Step 3 |
| PR | https://github.com/go-go-golems/publish-vault/pull/21 |
