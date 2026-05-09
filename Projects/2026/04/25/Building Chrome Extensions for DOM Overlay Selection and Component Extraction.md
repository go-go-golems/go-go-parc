# Building Chrome Extensions for DOM Overlay Selection and Component Extraction

*A deep technical guide to building browser extensions that overlay web pages, visually select components, capture PNGs, and export structured manifests for design system migration.*

---

## 1. The Problem: From Visual Prototypes to Reusable Components

When you have a large HTML prototype—or a React application rendered in the browser—and you want to extract its visual components into a design system, you face a problem that no standard developer tool solves well. Browser DevTools will show you the DOM tree, but they will not let you draw boxes around visual components, name them semantically, capture their rendered appearance, and export a structured catalog that a design tool or a React generator can consume.

The gap is not a small one. A typical design system extraction workflow involves:

- Visually identifying what constitutes a "component" (a card, a navbar, a button group)
- Naming it in a way that makes sense to other humans and to code generators
- Recording its geometry, its computed styles, and its structural context
- Capturing a pixel-accurate image of how it actually renders
- Annotating the source so the mapping from original to extracted is traceable
- Iterating: some components are obvious, others are ambiguous, and the first pass is never the final one

This chapter walks through the complete architecture of a Chrome extension that solves this problem. We will build it from first principles: why a browser extension and not a script, why a fixed-position overlay and not an injected iframe, why Vite bundling and not hand-rolled concatenation, why `html2canvas` and not native screenshot APIs. Each decision has tradeoffs, and understanding them is essential if you want to adapt this pattern to your own workflow.

---

## 2. Why a Browser Extension?

The first architectural question is where the selection logic lives. Three options present themselves: a standalone web application, a Playwright/CDP script, or a browser extension. Each has a different relationship to the page being inspected.

A standalone web app can load a page in an iframe, but modern sites send `X-Frame-Options: deny` or use CSP to prevent exactly this. Even when iframing works, cross-origin restrictions prevent the parent from inspecting the child DOM. The same-origin policy, one of the security foundations of the web, makes this approach unreliable.

A Playwright or Puppeteer script with Chrome DevTools Protocol access can inspect any page programmatically. It can query selectors, compute styles, and capture screenshots. What it cannot do well is let a human interactively decide what counts as a component. Programmatic heuristics for "what is a component" are brittle. A human looking at a page can instantly see that a group of elements forms a card, or that a sidebar navigation is a single unit. A script sees only a tree of nodes. Interactive selection requires a human in the loop.

A browser extension sits in the middle. Its content script injects JavaScript directly into the page's execution context, giving it full DOM access without same-origin restrictions. The user sees the real page, interacts with it normally, and the extension overlays visual feedback on top. The extension can persist state across sessions, communicate with a popup UI, and export data. It is the right tool for this job because it combines the DOM access of a script with the interactivity of a native application.

The tradeoff is that extensions are subject to the browser extension platform's constraints: Manifest V3's content security policy, the `chrome.storage` quota, the permission model for `file://` URLs. These are manageable, but they shape the architecture in specific ways we will see throughout.

---

## 3. Manifest V3 and the Content Script Lifecycle

Chrome extensions use a manifest file to declare what they are and what they can do. Manifest V3, the current version, introduces important constraints. The content script—the code that runs inside the page—must be declared in the manifest with `matches` patterns and a `run_at` timing.

```json
{
  "manifest_version": 3,
  "name": "Pyxis Component Extractor",
  "version": "1.1.0",
  "content_scripts": [{
    "matches": ["<all_urls>"],
    "js": ["content_scripts/overlay.js"],
    "css": ["content_scripts/overlay.css"],
    "run_at": "document_end"
  }]
}
```

The `run_at: "document_end"` timing is critical. It means the content script injects after the HTML document has been parsed but before external resources (images, stylesheets, scripts) have necessarily finished loading. For a React application that uses Babel standalone to transpile JSX in the browser, this means the DOM does not yet exist when the content script runs. The React components mount later, after Babel has fetched, parsed, and executed the JSX source.

This creates a race condition that every content script developer must handle. If you query `document.querySelector` at injection time, you may find nothing. The solution is a retry loop combined with a `MutationObserver`. The retry loop attempts to find elements at intervals, and the observer detects when the DOM changes—when React finally mounts its components—and triggers an immediate retry.

```javascript
const observer = new MutationObserver(() => {
  if (selections.length > 0 && drawnBoxes.size < selections.length) {
    attemptDrawSelections();
  }
});
observer.observe(document.body, { childList: true, subtree: true });
```

The observer watches the entire document subtree for child list changes. This is necessary for Babel-standalone React apps, which mount in bursts as scripts execute. For server-rendered pages, the retry loop alone is sufficient because the DOM exists at `document_end`.

---

## 4. The Overlay: Fixed Positioning and Coordinate Systems

The visual overlay is the heart of the extension. It consists of a container element injected into the page, and inside it, absolutely positioned boxes and labels that track DOM elements. The design of this overlay involves two decisions that are easy to get wrong: the positioning strategy and the coordinate math.

### 4.1 Why `position: fixed`?

The overlay container uses `position: fixed` with `top: 0; left: 0; width: 100%; height: 100%`. This places it in a viewport-relative containing block that does not scroll with the document. Why fixed and not absolute? Because the overlay must stay visible as the user scrolls. If the overlay scrolled with the document, it would need to be re-positioned on every scroll event, and it would potentially be clipped by ancestor elements with `overflow: hidden`.

Fixed positioning gives the overlay its own coordinate system: the viewport. Every child element inside the overlay is positioned relative to the viewport, not the document. This is the correct choice, but it has a consequence for the coordinate math.

### 4.2 The `getBoundingClientRect()` Trap

`Element.getBoundingClientRect()` returns the size and position of an element relative to the **viewport**. The `left` and `top` values are distances from the viewport's left and top edges. This is exactly what you need for positioning a box inside a fixed overlay.

The trap is adding `window.scrollX` and `window.scrollY` to these values. This converts viewport-relative coordinates to document-relative coordinates. If you then place that box inside a fixed overlay—which is viewport-relative—the box will be offset by the scroll amount. Scroll down 200 pixels, and every box shifts 200 pixels down relative to its target element.

This is one of those bugs that is obvious once you see it but easy to introduce because "add scroll offset" feels like the right thing to do when working with DOM positioning. The correct code is simply:

```javascript
const rect = el.getBoundingClientRect();
box.style.left = rect.left + 'px';
box.style.top = rect.top + 'px';
box.style.width = rect.width + 'px';
box.style.height = rect.height + 'px';
```

No scroll offset. The `getBoundingClientRect()` values map directly to the fixed overlay's coordinate system. On every scroll event, you re-query the element's rect and update the box position. The box tracks the element perfectly because both are expressed in the same coordinate system.

### 4.3 The Visual Design

The overlay uses two visual states: a cyan border for hover (the element currently under the mouse) and a blue border for selected elements. Each selected box has a label showing the component name. The labels are positioned 24 pixels above the box and use `pointer-events: auto` so the user can click them to remove a selection.

The z-index stack is carefully managed:

| Layer | z-index | Purpose |
|-------|---------|---------|
| Page content | auto | The actual web page |
| Overlay container | 2147483646 | The fixed overlay (max - 1) |
| Labels and dialogs | 2147483647 | Must sit above overlay boxes |

The overlay container is one level below the maximum `z-index` because some pages use `2147483647` for modal backdrops. The labels and the name input dialog sit at the maximum to ensure they are always interactive.

---

## 5. Selection, Capture, and Storage

When the user clicks on an element, the extension must capture its metadata and store it. This involves four operations: generating a unique selector, extracting computed styles, serializing HTML, and persisting to storage.

### 5.1 Selector Generation

A selector is the bridge between the visual overlay and the stored data. It must be stable enough to survive page reloads but specific enough to identify exactly one element. The generation strategy uses a priority cascade:

1. **Data attributes first.** If the element has any `data-*` attribute, use it: `[data-testid="user-card"]`.
2. **ID next.** If it has an `id`, use it: `#main-nav`.
3. **Class combination.** If a class list uniquely identifies the element, use it: `div.card.primary`.
4. **nth-child fallback.** Walk up the tree and build a path: `main > section:nth-of-type(2) > div.card`.

Data attributes are preferred because they are intentionally stable. Classes change when designers refactor. IDs are reliable but many modern frameworks discourage their use. The nth-child fallback is brittle for dynamic lists but is the only option for elements with no identifying attributes.

### 5.2 Computed CSS Filtering

`window.getComputedStyle(el)` returns every computed property for an element, including inherited defaults. A typical element has over 200 properties, most of which are browser defaults (`rgba(0, 0, 0, 0)` for background, `0px` for margin, `auto` for width). Storing all of them is wasteful and noisy.

The solution is a whitelist of meaningful properties and a filter that drops default values:

```javascript
const CSS_KEYS = [
  'display', 'position', 'flexDirection', 'justifyContent', 'alignItems',
  'gap', 'padding', 'margin', 'borderRadius', 'backgroundColor', 'color',
  'fontSize', 'fontWeight', 'fontFamily', 'lineHeight', 'textAlign',
  'boxShadow', 'border', 'width', 'height', 'overflow', 'cursor'
];

for (const k of CSS_KEYS) {
  const val = computed.getPropertyValue(k);
  if (val && val !== 'normal' && val !== 'auto' && val !== '0px' && val !== 'rgba(0, 0, 0, 0)') {
    styles[k] = val;
  }
}
```

This reduces 200+ properties to a handful of meaningful ones. The filter is heuristic: some design systems use `auto` intentionally, and some use transparent backgrounds as a design choice. For a general-purpose tool, the heuristic is good enough. For a specific design system, you would tune the filter.

### 5.3 Storage with `chrome.storage.local`

Selections are persisted in `chrome.storage.local`, keyed by the page URL. This means selections for `http://localhost:8765/standalone/public/shows.html` are separate from selections for `http://localhost:8765/standalone/public/detail.html`.

The storage API is callback-based, which is awkward for modern async code. Wrapping it in Promises makes the rest of the codebase cleaner:

```javascript
export async function loadSelections() {
  return new Promise((resolve) => {
    const key = 'px_selections_' + location.href;
    chrome.storage.local.get([key], (result) => {
      resolve(result[key] || []);
    });
  });
}
```

The 5MB quota is a real constraint. Each selection stores its outer HTML (truncated to 10KB), inner HTML (5KB), computed CSS, and now a PNG data URL. A single PNG at 2× retina scale can be 50-200KB as a base64 data URL. Twenty components with PNGs could exhaust the quota. For this tool, the tradeoff is acceptable: the user exports their work before the quota fills. For a production system, you would use IndexedDB or download-to-file as the primary storage.

---

## 6. Module Architecture and the Bundler Question

The first version of the content script was a single 450-line IIFE. It worked, but it mixed concerns: DOM creation, event handling, CSS capture, storage I/O, and messaging all in one file. Adding a feature required touching multiple unrelated parts of the file, and there was no way to test individual pieces in isolation.

### 6.1 Decomposition into ES Modules

The refactor split the monolith into six modules, each with a single responsibility:

| Module | Responsibility | Key Exports |
|--------|---------------|-------------|
| `state.js` | Central reactive state store | `getState, setState, addListener` |
| `dom-overlay.js` | Visual DOM operations | `createOverlay, showHover, drawSelectedBox` |
| `capture.js` | Element metadata extraction | `captureElement, generateSelector` |
| `capture-png.js` | DOM-to-PNG rendering | `captureElementPng` |
| `storage.js` | Persistence layer | `loadSelections, saveSelections` |
| `events.js` | User input handlers | `bindEvents` |
| `messaging.js` | Chrome runtime messaging | `initMessaging` |
| `main.js` | Entry point, wires everything | — |

The dependency graph is a directed acyclic graph with `state.js` at the root. `events.js` imports `state`, `dom`, and `capture` because it needs to update state, draw boxes, and extract metadata. `messaging.js` imports `state`, `dom`, and `storage` because it handles commands from the popup. No module imports another that imports it back.

State management uses a simple pub/sub pattern. `setState({ isActive: true })` merges the partial state and notifies all registered listeners. This is enough for a tool of this scale; Redux would be overkill.

### 6.2 The Bundler Problem

Here is a fact that is not obvious from the Chrome extension documentation: **content scripts do not support ES module imports**, even with `"type": "module"` in the manifest. That setting only works for background service workers. Content scripts run in the page's execution context, and their `import` statements are evaluated by the page's JavaScript engine, not the extension's. The page sees `import ./modules/state.js` and tries to load it from the page's origin, which fails.

The first instinct is to write a bash script that concatenates files and strips `import`/`export` lines with `grep`. This works for trivial cases but breaks down with namespace imports, re-exports, and any non-trivial module pattern. More importantly, it is not software engineering. It is a hack that will break silently when the module structure changes.

The correct solution is a bundler. Vite, built on Rollup, resolves module imports, tree-shakes dead code, and outputs a single IIFE that the browser can execute directly. The configuration is minimal:

```javascript
// vite.config.js
import { defineConfig } from 'vite';

export default defineConfig({
  build: {
    lib: {
      entry: 'content_scripts/main.js',
      name: 'PyxisExtractor',
      fileName: () => 'overlay.js',
      formats: ['iife'],
    },
    outDir: 'content_scripts',
    emptyOutDir: false,
  },
});
```

The `iife` format wraps everything in an immediately invoked function expression, which is what Chrome content scripts expect. The `emptyOutDir: false` setting preserves `overlay.css` and other files in the output directory. Running `npm run build` produces `overlay.js` in under a second.

The bundled file is checked into Git. This is unusual for generated artifacts, but necessary for browser extensions: when a user loads the extension unpacked in Chrome, Chrome reads files directly from disk. It does not run `npm install` or `npm run build`. The bundled file must exist in the repository.

---

## 7. PNG Capture with html2canvas

Capturing a rendered DOM element as a PNG is not trivial. The browser's native screenshot APIs capture the viewport, not individual elements. The Canvas API can draw individual elements, but it does not handle CSS: box shadows, border radii, transforms, and web fonts do not render correctly when an element is drawn to a canvas with `drawImage`.

`html2canvas` solves this by recursively traversing the DOM, parsing computed styles, and drawing each element to a canvas using the Canvas 2D API. It handles borders, backgrounds, shadows, text, and images. It is not perfect—CSS Grid, certain transforms, and SVG filters may not render identically—but it is the most reliable solution available.

### 7.1 Integration

The capture happens at selection time, not at export time. When the user clicks to select an element and enters a name, the extension immediately calls `html2canvas` on that element:

```javascript
import html2canvas from 'html2canvas';

export async function captureElementPng(el) {
  const canvas = await html2canvas(el, {
    backgroundColor: null,  // preserve transparency
    scale: 2,               // retina resolution
    logging: false,
    useCORS: true,          // allow cross-origin images
    allowTaint: true,
  });
  return canvas.toDataURL('image/png');
}
```

The `scale: 2` option doubles the canvas resolution, producing crisp PNGs on retina displays. The tradeoff is file size: a 2× PNG is approximately 4× the size of a 1× PNG. `backgroundColor: null` preserves transparency where the element has no explicit background.

The resulting data URL is stored in the selection object as `pngDataUrl`. This means PNGs persist across sessions in `chrome.storage.local`, and they are available immediately in the popup for thumbnail preview and download.

### 7.2 Bundle Size Impact

`html2canvas` adds approximately 365KB to the bundle. The extension grows from 17KB to 383KB. This is significant, but acceptable for a development tool. Alternatives were considered:

| Approach | Pros | Cons |
|----------|------|------|
| `chrome.tabs.captureVisibleTab()` | Native, fast, no library | Captures viewport only; cannot scroll to element |
| `dom-to-image` | Smaller than html2canvas | Less reliable on complex CSS |
| Custom canvas renderer | Full control | Would require reimplementing html2canvas |
| Lazy-loaded html2canvas | Smaller initial bundle | Async loading adds complexity |

For this use case, the reliability of `html2canvas` outweighs the size cost. A future optimization would lazy-load the library: import it only when the first PNG capture is requested, reducing the initial bundle to 17KB and paying the 365KB cost only when needed.

---

## 8. The Popup: Extension UI and Cross-Context Communication

The popup is the extension's control panel. It is an HTML page that opens when the user clicks the extension icon in the toolbar. It runs in its own isolated context and communicates with the content script via Chrome's message passing API.

### 8.1 Message Passing Pattern

The content script listens for messages on `chrome.runtime.onMessage`. The popup sends messages with `chrome.tabs.sendMessage`. This is the only way for the popup to communicate with the content script because they run in different execution contexts with no shared memory.

```javascript
// In popup.js
const resp = await chrome.tabs.sendMessage(tab.id, { action: 'toggle' });

// In content script (messaging.js)
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.action === 'toggle') {
    toggle();
    sendResponse({ active: isActive, count: selections.length });
  }
});
```

The pattern is request-response: the popup sends a message, the content script acts on it, and the content script sends a response. Because the popup can be closed at any time, messages should be idempotent where possible.

### 8.2 Popup Features

The popup displays the current selection count, a list of all selections with thumbnails, and action buttons:

- **Start/Stop Selecting:** Toggles the overlay's interactive mode
- **Clear:** Removes all selections on the current page
- **Export Full Manifest:** Downloads the complete selection data as JSON
- **Export Simple (LLM):** Downloads a minimal format for LLM consumption
- **Download All PNGs:** Bulk-downloads all captured PNGs
- **Import JSON:** Loads a previously exported manifest or an LLM-generated component list

Each selection in the list shows a PNG thumbnail (if captured), the component name, tag, and dimensions. Individual selections can be copied (selector) or downloaded (PNG) via icon buttons.

---

## 9. LLM Integration: Generating and Validating Component Lists

One of the most powerful patterns enabled by this architecture is the loop between an LLM and the live DOM. The workflow is:

1. The user gives an LLM the page structure (HTML, screenshot, or description)
2. The LLM suggests component names and CSS selectors in a simple JSON format
3. The user imports this JSON into the extension
4. The extension resolves each selector against the live DOM
5. Valid suggestions become real selections with blue overlay boxes
6. Invalid suggestions are counted as missing and skipped
7. The user visually validates, edits names, and discards bad suggestions

### 9.1 The Simple Format

The full manifest format includes bounding boxes, computed CSS, HTML snippets, and PNG data URLs. It is excellent for archival and export but too verbose for LLM generation. The simple format is minimal:

```json
{
  "components": [
    { "name": "ShowCard", "selector": ".show-card", "note": "Contains title, date, and image" },
    { "name": "NavBar", "selector": "nav.main-nav", "note": "Top navigation with logo" },
    { "name": "Footer", "selector": "footer", "note": "Copyright and social links" }
  ]
}
```

An LLM can generate this format from a page description or screenshot. The `note` field is optional but useful: it lets the LLM explain why it thinks something is a component, which helps the human reviewer decide whether to keep it.

### 9.2 Validation on Import

When the extension imports a simple format, it does not blindly store the components. It validates each one against the live DOM:

```javascript
for (const comp of msg.components) {
  const el = document.querySelector(comp.selector);
  if (el) {
    const data = capture.captureElement(el, comp.name);
    data.note = comp.note || '';
    newSelections.push(data);
    foundCount++;
  } else {
    missingCount++;
  }
}
```

The result is reported to the user: "Imported 5 (5 found, 2 missing)." The missing selectors are silently dropped. This is a feature, not a bug: an LLM might hallucinate selectors, or the page might have changed since the LLM saw it. The validation ensures only real, visible components become selections.

### 9.3 The Validation Loop

The complete loop looks like this:

```
LLM generates suggestions ──▶ User imports JSON ──▶ Extension validates against DOM
         ▲                                                              │
         │                                                              ▼
User reviews and refines ◀── Visual overlay shows what was found ◀── Valid components
```

This loop is more powerful than either the LLM or the extension alone. The LLM brings pattern recognition and naming at scale. The extension brings ground-truth validation against the actual rendered page. The human brings judgment about what constitutes a meaningful component.

---

## 10. Key Decisions and Their Tradeoffs

Every architectural decision in this project has an alternative. Understanding why the chosen path was taken—and what you would do differently in another context—is essential for adapting this pattern.

| Decision | Chosen | Alternative | Tradeoff |
|----------|--------|-------------|----------|
| Runtime | Browser extension | Playwright script | Extension gives interactivity; script gives CI automation |
| Overlay position | `position: fixed` | `position: absolute` on body | Fixed avoids scroll clipping; absolute would need scroll offset |
| Coordinate math | `getBoundingClientRect()` direct | `rect + scrollX/Y` | Direct is correct for fixed overlay; adding scroll double-counts |
| Module system | ES modules + Vite bundler | Single IIFE | Modules enable testing and clarity; bundler adds build step |
| Bundler | Vite | Rollup directly | Vite is faster to configure; Rollup gives more control |
| PNG capture | `html2canvas` | Native screenshot API | html2canvas captures elements; native API captures viewport only |
| Storage | `chrome.storage.local` | IndexedDB | Storage is simpler; IndexedDB has larger quota but async API |
| State management | Pub/sub in vanilla JS | Redux/MobX | Pub/sub is sufficient; Redux would be overkill |
| Selector strategy | Data attrs > ID > class > nth-child | Always use nth-child | Data attrs are stable; nth-child is brittle for dynamic content |

---

## 11. Extending the Architecture

This extension was built for a specific workflow—extracting React components from Pyxis standalone pages—but its architecture generalizes. Here are natural extensions:

**Full-page screenshot context.** Capture the entire page at selection time, not just the component. This gives designers a reference for where the component sits in the overall layout.

**Batch processing across pages.** The background script can iterate over all `px_selections_*` keys in storage and produce a project-wide catalog. This would answer questions like "how many times does ShowCard appear across all pages?"

**Source annotation.** A post-processing script could inject `data-component-name` attributes into the original HTML and JSX files. This creates a traceable link from the extracted catalog back to the source.

**React DevTools integration.** The React DevTools backend exposes component names through a global hook. Querying this hook would let the extension show "React: ShowCard" alongside the DOM tag, giving the user both the visual and the component hierarchy perspective.

**ZIP export.** Instead of individual PNG downloads, bundle the manifest and all PNGs into a single ZIP file using JSZip. This is cleaner for sharing with design teams.

**Tentative state for LLM suggestions.** LLM-generated components could be shown in a different color (yellow/orange) until the user explicitly accepts them. This would make the validation loop even more explicit.

---

## 12. What to Remember

The most important ideas in this chapter are not the specific APIs or the exact code. They are the patterns:

- **Interactive extraction requires a browser extension.** Scripts can automate; only extensions can overlay and let humans judge.
- **Fixed overlays use viewport coordinates.** `getBoundingClientRect()` gives viewport-relative values. Do not add scroll offsets unless the overlay itself scrolls.
- **Content scripts need bundlers for modules.** Chrome does not support ES module imports in content scripts. Vite bundles modules into a single IIFE that works.
- **Capture at selection time, not export time.** The element is visible and in its current state when selected. Waiting until export risks the element having changed or scrolled out of view.
- **LLMs and live DOM validation form a powerful loop.** LLMs suggest; the DOM validates; humans judge. Each layer catches errors the others would miss.

If you build something similar, start with the simplest version that works: a single content script that draws boxes. Add modules, bundlers, PNG capture, and LLM integration only when the simple version proves the concept. The architecture described here was not designed upfront; it emerged from iterating on a working prototype, fixing bugs, and responding to real usage. That is how good software is built.
