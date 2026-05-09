---
title: "Chrome DevTools Protocol (CDP) — Knowledge Base"
aliases:
  - CDP
  - Chrome DevTools Protocol
  - CDP Knowledge Base
tags:
  - knowledge-base
  - cdp
  - browser-automation
  - surf-cli
  - chrome
  - protocol
status: active
type: knowledge-base
created: 2026-04-11
repo: /home/manuel/code/others/llms/pi/nicobailon/surf-cli
---

# Chrome DevTools Protocol (CDP) — Knowledge Base

The Chrome DevTools Protocol (CDP) is the wire protocol that underlies all browser automation in the Surf CLI project. Every browser interaction — executing JavaScript, clicking buttons, reading network requests, capturing screenshots — flows through CDP. This document is a working reference covering the protocol's architecture, the domains Surf CLI uses, the concrete commands Surf CLI sends, and the patterns that emerge from that usage.

> [!summary]
> - CDP is a JSON-over-WebSocket protocol attached to a Chrome debugging session
> - Surf CLI uses 7 CDP domains: Runtime, Page, Network, Input, DOM, Emulation, Tracing
> - The key command is `Runtime.evaluate` — it executes JavaScript in the page context
> - The key events are `Runtime.consoleAPICalled`, `Network.requestWillBeSent`, and `Page.javascriptDialogOpening`
> - CDP powers Playwright, Puppeteer, Selenium 4, and raw CDP libraries under the hood

---

## 1. Protocol Architecture

### 1.1 What CDP Is

CDP is a JSON-RPC-over-WebSocket protocol that exposes Chrome's internal debugging APIs. When Chrome starts with `--remote-debugging-port=9222`, it opens a WebSocket server. Clients connect and send JSON commands; Chrome responds with JSON results and asynchronous event notifications.

The protocol is organized into **domains** (namespaces), each containing:
- **Commands** — request/response RPC calls
- **Events** — asynchronous push notifications
- **Types** — data structures

### 1.2 How Surf CLI Connects

Surf CLI does not use `--remote-debugging-port`. Instead, it uses the **`chrome.debugger`** API available to browser extensions. This allows CDP access without a separate port:

```
Surf CLI Go command → Unix socket → Browser Extension service worker → chrome.debugger API → CDP → Chrome tab
```

**Source**: `src/service-worker/index.ts` — the service worker holds a `CDPController` instance and bridges between the native messaging socket and CDP.

### 1.3 The CDPController

Surf CLI's TypeScript implementation lives in `src/cdp/controller.ts` (1,431 lines). It wraps `chrome.debugger.*` APIs into a higher-level interface.

**Key implementation detail**: The controller uses `chrome.debugger.sendCommand` for all CDP calls and registers a single global event listener for `chrome.debugger.onEvent` to route all incoming events.

```typescript
// src/cdp/controller.ts
export class CDPController {
  private targets = new Map<number, Debuggee>();
  private consoleMessages: Map<number, ConsoleMessage[]> = new Map();
  private networkRequests: Map<number, NetworkRequest[]> = new Map();

  async attach(tabId: number): Promise<void> {
    const target: Debuggee = { tabId };
    await chrome.debugger.attach(target, "1.3");
    this.targets.set(tabId, target);
    this.setupEventListener();  // Single global listener
  }

  private async send(tabId: number, method: string, params?: object): Promise<any> {
    const target = this.targets.get(tabId);
    return chrome.debugger.sendCommand(target, method, params);
  }
}
```

**Attach error handling** (controller.ts line ~158):
```typescript
if (message.includes("Cannot access") || message.includes("Cannot attach")) {
  throw new Error(`Cannot control this page. Chrome restricts automation on chrome://, extensions, and web store pages.`);
}
```

### 1.4 CDP Version Negotiation

The controller attaches with protocol version `"1.3"`. Chrome supports protocol versions backward-incrementally. Using a stable older version (1.3) rather than the latest ensures compatibility across Chrome versions.

---

## 2. Domains Used by Surf CLI

### 2.1 Runtime Domain

The most-used domain. Exposes JavaScript execution and runtime introspection.

**CDP Specification**: https://chromedevtools.github.io/devtools-protocol/tot/Runtime/

#### Commands

**`Runtime.enable`** — Enables runtime domain reporting. Must be called before receiving console events.

**`Runtime.evaluate`** — Evaluates JavaScript expression on the global object. This is the primary mechanism for all page interaction.

```typescript
// controller.ts line ~887
await this.send(tabId, "Runtime.evaluate", {
  expression,
  returnByValue: true,    // Return primitive values directly
  awaitPromise: true,     // Wait for async results
});
```

Key parameters from the CDP spec:
- `expression` (string) — The JavaScript to evaluate
- `returnByValue` (boolean) — Return primitives directly vs. object references
- `awaitPromise` (boolean) — Wait for promises to resolve
- `contextId` (ExecutionContextId) — Evaluate in specific execution context
- `objectGroup` (string) — Named group for releasing object references
- `userGesture` (boolean) — Treat as user-initiated (enables some APIs)
- `throwOnSideEffect` (boolean) — Fail if evaluation has side effects
- `timeout` (TimeDelta) — Terminate after N milliseconds
- `replMode` (boolean) — Enable `let` re-declaration and top-level `await`
- `allowUnsafeEvalBlockedByCSP` (boolean) — Bypass CSP for unsafe-eval

**Return object**:
```typescript
{
  result: RemoteObject,       // { type, subtype, className, value, objectId, description }
  exceptionDetails?: ExceptionDetails  // { exceptionId, text, lineNumber, columnNumber, stackTrace }
}
```

**Surf CLI usage**: Every `surf-go js` command, the polling loop in the ChatGPT provider, tab readiness probing, and all DOM queries.

**`Runtime.callFunctionOn`** — Calls a function on a specific object or in a specific context. Used for more targeted invocations.

```typescript
// From CDP spec
{
  functionDeclaration: string,  // Function source
  objectId?: RemoteObjectId,    // Call on this object
  executionContextId?: ExecutionContextId,
  arguments?: CallArgument[],
  returnByValue?: boolean,
  awaitPromise?: boolean,
}
```

**`Runtime.addBinding`** — Injects a callable function into the page's global scope. When the page calls the binding, Chrome emits `Runtime.bindingCalled` events. **Deprecated** in favor of `executionContextName` parameter.

> [!important] Streaming Potential
> `Runtime.addBinding` + `Runtime.bindingCalled` events could replace the 400ms polling loop in the ChatGPT provider. The page would call `window.surfStreamHit({ text: "..." })` on each token arrival, and the extension would receive events without polling. This is the most promising path for streaming extraction.

**`Runtime.awaitPromise`** — Waits for a promise to resolve and returns its value.

**`Runtime.getProperties`** — Returns properties of an object. Useful for inspecting DOM nodes or JavaScript objects.

**`Runtime.compileScript`** — Compiles an expression for later execution.

#### Events

**`Runtime.consoleAPICalled`** — Fired when `console.log`, `console.error`, etc. are called in the page.

Surf CLI uses this for streaming extraction probes. Enable with `Runtime.enable`, then read messages via `getConsoleMessages()`.

```typescript
// controller.ts line ~229 — event routing
case "Runtime.consoleAPICalled": {
  this.consoleMessages.get(tabId)?.push({
    type: params.type || "log",
    text: this.formatConsoleArgs(params.args),
    timestamp: params.timestamp,
    url: params.context?.origin,
  });
}
```

**`Runtime.exceptionThrown`** — Fired when an unhandled exception occurs.

**`Runtime.executionContextCreated`** / **`Runtime.executionContextDestroyed`** — Fired when JavaScript execution contexts are created or destroyed. Useful for detecting when React has hydrated.

**`Runtime.bindingCalled`** — Fired when a page calls a function added via `Runtime.addBinding`. Payload: `{ name, payload: string, executionContextId }`.

---

### 2.2 Page Domain

Controls page-level operations: navigation, screenshots, dialogs, frame tree.

**CDP Specification**: https://chromedevtools.github.io/devtools-protocol/tot/Page/

#### Commands

**`Page.enable`** / **`Page.disable`** — Enable/disable page domain notifications.

**`Page.captureScreenshot`** — Captures a PNG screenshot of the current viewport.

```typescript
// From service-worker/index.ts line ~278
const chunk = await cdp.captureScreenshot(tabId);
// Returns: { data: string } — base64-encoded PNG
```

Parameters:
- `format` — `"png"` | `"jpeg"` | `"webp"`
- `quality` — JPEG quality (0-100)
- `clip` — Viewport region to capture
- `fromSurface` — Capture from compositor surface vs. view
- `captureBeyondViewport` — Capture full page

**`Page.getFrameTree`** — Returns the frame hierarchy (main frame + iframes).

```typescript
// controller.ts line ~897 — getFrames()
const result = await this.send(tabId, "Page.getFrameTree");
const frames = extractFrames(result.frameTree);
// Returns: [{ frameId, url, name, parentId }]
```

**`Page.createIsolatedWorld`** — Creates an isolated JavaScript world in a frame. Used by Surf CLI to run user scripts without polluting the page's global scope.

```typescript
// controller.ts line ~929 — evaluateInFrame()
const contextResult = await this.send(tabId, "Page.createIsolatedWorld", {
  frameId,
  worldName: "surf-isolated",
});
// Then evaluate with contextResult.executionContextId
```

**`Page.handleJavaScriptDialog`** — Accepts or dismisses a JavaScript dialog (alert, confirm, prompt).

```typescript
// controller.ts line ~657
await this.send(tabId, "Page.handleJavaScriptDialog", {
  accept: true,
  promptText: "default response",
});
```

**`Page.getLayoutMetrics`** — Returns layout viewport dimensions. Used for viewport-aware screenshot and scroll operations.

**`Page.addScriptToEvaluateOnNewDocument`** — Injects a script that runs before page scripts. Useful for setting up bindings or modifying behavior globally.

#### Events

**`Page.javascriptDialogOpening`** — Fired when a dialog appears. Surf CLI listens for this to auto-handle dialogs.

**`Page.frameStartedLoading`** / **`Page.frameStoppedLoading`** — Frame lifecycle events.

**`Page.navigatedWithinDocument`** — Fired when navigation happens within the same document (hash changes, pushState).

---

### 2.3 Network Domain

Tracks HTTP requests and responses. Essential for intercepting API calls, capturing request/response bodies, and measuring timing.

**CDP Specification**: https://chromedevtools.github.io/devtools-protocol/tot/Network/

#### Commands

**`Network.enable`** — Enables network tracking. Must be called before receiving network events.

```typescript
// controller.ts line ~648
await this.send(tabId, "Network.enable", { maxPostDataSize: 65536 });
```

**`Network.getResponseBody`** — Fetches the response body for a completed request.

```typescript
// controller.ts line ~591
const result = await this.send(tabId, "Network.getResponseBody", { requestId });
// Returns: { body: string, base64Encoded: boolean }
```

**`Network.emulateNetworkConditions`** (deprecated) — Simulates network throttling. Surf CLI uses this via `emulateNetwork()` helper.

```typescript
// controller.ts line ~686
const presets = {
  "offline": { offline: true, latency: 0, downloadThroughput: 0, uploadThroughput: 0 },
  "slow-3g": { offline: false, latency: 2000, downloadThroughput: 50000, uploadThroughput: 50000 },
  "fast-3g": { offline: false, latency: 562.5, downloadThroughput: 180000, uploadThroughput: 84375 },
  "4g": { offline: false, latency: 100, downloadThroughput: 4000000, uploadThroughput: 3000000 },
  "reset": { offline: false, latency: 0, downloadThroughput: -1, uploadThroughput: -1 },
};
```

**`Network.setCacheDisabled`** — Toggles ignoring the browser cache.

**`Network.setExtraHTTPHeaders`** — Adds custom headers to all requests.

#### Events

**`Network.requestWillBeSent`** — Fired when a request is about to be sent. Contains: `requestId`, `url`, `method`, `headers`, `postData`, `timestamp`, `type`.

**`Network.responseReceived`** — Fired when response headers are received. Contains: `requestId`, `status`, `statusText`, `headers`, `mimeType`, `timing`.

**`Network.dataReceived`** — Fired for each data chunk received.

**`Network.loadingFinished`** — Fired when a request completes. Contains: `requestId`, `timestamp`, `encodedDataLength`, `shouldReportCorbCoverage`.

**`Network.loadingFailed`** — Fired when a request fails.

Surf CLI's network tracking implementation (controller.ts lines ~321-505):
- Builds a `NetworkRequest` map per tab
- Tracks `requestWillBeSent` → `responseReceived` → `loadingFinished` lifecycle
- Lazy-fetches response bodies via `getResponseBody` on `loadingFinished`
- Has a 16KB inline body threshold (configurable)

---

### 2.4 Input Domain

Simulates user input: keyboard, mouse, touch.

**CDP Specification**: https://chromedevtools.github.io/devtools-protocol/tot/Input/

#### Commands

**`Input.dispatchMouseEvent`** — Dispatches mouse events: move, click, double-click, right-click, drag.

```typescript
// service-worker/index.ts lines 521-542
await cdp.click(tabId, x, y, "left", 1, mods);        // single click
await cdp.rightClick(tabId, x, y, mods);               // right click
await cdp.doubleClick(tabId, x, y, mods);              // double click
await cdp.tripleClick(tabId, x, y, mods);             // triple click
```

Parameters:
- `type` — `"mousePressed"` | `"mouseReleased"` | `"mouseMoved"` | `"mouseWheel"`
- `x`, `y` — Coordinates in CSS pixels (relative to viewport)
- `button` — `"left"` | `"right"` | `"middle"`
- `clickCount` — Number of clicks
- `modifiers` — Bit field: Alt=1, Ctrl=2, Meta=4, Shift=8

**`Input.dispatchKeyEvent`** — Dispatches keyboard events.

```typescript
// controller.ts parses modifiers from string like "ctrl+shift"
const MODIFIERS = { alt: 1, ctrl: 2, control: 2, meta: 4, shift: 8, ... };

await this.send(tabId, "Input.dispatchKeyEvent", {
  type: "keyDown",        // "keyDown" | "keyUp" | "rawKeyDown" | "char"
  key: "Enter",
  code: "Enter",
  keyCode: 13,
  modifiers: 0,
});
```

Key definition table (controller.ts lines ~85-119):
```typescript
const KEY_DEFINITIONS = {
  enter: { key: "Enter", code: "Enter", keyCode: 13, text: "\r" },
  tab: { key: "Tab", code: "Tab", keyCode: 9 },
  escape: { key: "Escape", code: "Escape", keyCode: 27 },
  arrowup: { key: "ArrowUp", code: "ArrowUp", keyCode: 38 },
  // ... f1-f12, home, end, pageup, pagedown, etc.
};
```

**`Input.insertText`** — Inserts text as if typed. Bypasses keyboard layout issues.

```typescript
await this.send(tabId, "Input.insertText", { text: "hello world" });
```

#### Click Implementation Detail

The `click()` method (controller.ts ~540) dispatches two events:
```typescript
await this.send(tabId, "Input.dispatchMouseEvent", {
  type: "mousePressed",
  x, y, button: "left", clickCount: 1, modifiers,
});
await this.send(tabId, "Input.dispatchMouseEvent", {
  type: "mouseReleased",
  x, y, button: "left", clickCount: 1, modifiers,
});
```

---

### 2.5 DOM Domain

Accesses and manipulates the Document Object Model.

**CDP Specification**: https://chromedevtools.github.io/devtools-protocol/tot/DOM/

#### Commands

**`DOM.enable`** / **`DOM.disable`** — Enable/disable DOM domain.

**`DOM.getDocument`** — Returns the root DOM node.

**`DOM.querySelector`** — Finds an element by CSS selector.

```typescript
// controller.ts line ~870 — setFileInputBySelector
const doc = await this.send(tabId, "DOM.getDocument");
const queryResult = await this.send(tabId, "DOM.querySelector", {
  nodeId: doc.root.nodeId,
  selector: "input[type=file]",
});
```

**`DOM.setFileInputFiles`** — Sets files on a `<input type="file">` element.

```typescript
await this.send(tabId, "DOM.setFileInputFiles", {
  nodeId: queryResult.nodeId,
  files: ["/path/to/file.txt"],
});
```

Used by the ChatGPT provider's file upload feature.

#### Events

**`DOM.subtreeModified`** — Fired when a subtree is modified. Useful for detecting when the page updates (but Surf CLI doesn't currently use this — it uses polling instead).

**`DOM.attributeModified`** / **`DOM.attributesModified`** — Fired when attributes change.

---

### 2.6 Emulation Domain

Controls environment emulation: device metrics, geolocation, user agent, network conditions, touch, CPU throttling.

**CDP Specification**: https://chromedevtools.github.io/devtools-protocol/tot/Emulation/

#### Commands

**`Emulation.setDeviceMetricsOverride`** — Overrides screen dimensions and device pixel ratio.

```typescript
// controller.ts line ~787
await this.send(tabId, "Emulation.setDeviceMetricsOverride", {
  width: 375,              // Viewport width in pixels
  height: 812,             // Viewport height in pixels
  deviceScaleFactor: 2,    // DPR
  mobile: true,            // Emulate mobile viewport
  scale: 1,
});
```

**`Emulation.setGeolocationOverride`** — Overrides the reported geolocation.

```typescript
// controller.ts line ~710
await this.send(tabId, "Emulation.setGeolocationOverride", {
  latitude: 37.7749,
  longitude: -122.4194,
  accuracy: 1,
});
```

**`Emulation.setUserAgentOverride`** — Changes the reported User-Agent string.

```typescript
await this.send(tabId, "Emulation.setUserAgentOverride", {
  userAgent: "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) ...",
  acceptLanguage: "en-US",
  platform: "iPhone",
});
```

**`Emulation.setTouchEmulationEnabled`** — Enables or disables touch emulation.

**`Emulation.setCPUThrottlingRate`** — Throttles CPU (1 = no throttle, 2 = 2x slowdown).

**`Emulation.setDevicePostureOverride`** — Emulates foldable device posture.

---

### 2.7 Tracing / Performance Domain

Captures performance traces and metrics.

**CDP Specification**: https://chromedevtools.github.io/devtools-protocol/tot/Tracing/

#### Commands

**`Tracing.start`** / **`Tracing.end`** — Start/stop trace collection.

**`Performance.enable`** / **`Performance.disable`** — Enable/disable performance metrics reporting.

**`Performance.getMetrics`** — Returns performance metrics snapshot.

```typescript
// controller.ts line ~845
await this.send(tabId, "Performance.enable");
const result = await this.send(tabId, "Performance.getMetrics");
const metrics: Record<string, number> = {};
for (const m of result.metrics || []) {
  metrics[m.name] = m.value;
}
// Keys include: Timestamp, Documents, Frames, JSEvents, Nodes, LayoutCount, ...
```

---

## 3. Target Domain

Controls browser targets (tabs, pages, iframes, workers).

**CDP Specification**: https://chromedevtools.github.io/devtools-protocol/tot/Target/

> [!note] Surf CLI doesn't use Target domain directly
> The extension's `chrome.tabs` API manages tabs. CDP's Target domain is the protocol-level equivalent.

**Key commands**:
- **`Target.createTarget`** — Opens a new page. Returns `targetId`.
- **`Target.attachToTarget`** — Attaches CDP session to a target.
- **`Target.closeTarget`** — Closes a target.
- **`Target.getTargets`** — Lists all available targets.

Surf CLI's `tab.new` tool uses the extension API (`chrome.tabs.create`) rather than `Target.createTarget`. The CDP `Target` domain would be the lower-level alternative.

---

## 4. Fetch Domain (Not Currently Used)

Provides request interception at the HTTP layer — more powerful than Network domain for modifying requests/responses.

**CDP Specification**: https://chromedevtools.github.io/devtools-protocol/tot/Fetch/

**Key commands**:
- **`Fetch.enable`** — Enables request interception with optional patterns
- **`Fetch.requestPaused`** — Event fired when a request is intercepted
- **`Fetch.continueRequest`** — Continue the request after modification
- **`Fetch.fulfillRequest`** — Return a custom response
- **`Fetch.failRequest`** — Fail the request with an error

**Why it matters for Surf CLI**: This would be the path for intercepting the ChatGPT bearer token from the `/textdocs` request. If `Fetch.enable` is called with a pattern matching `chat.openai.com/backend-api/*`, the extension receives `Fetch.requestPaused` events containing the full request including headers. The `Authorization: Bearer <token>` header would be visible here.

**From the CDP spec**:
```
Fetch.enable patterns=[{ urlPattern: "https://chat.openai.com/backend-api/*" }]
→ Fetch.requestPaused { requestId, request: { headers: { authorization: "Bearer ..." } } }
```

This is the most viable path for the "Token Capture" research point.

---

## 5. The Service Worker Execution Pipeline

This is the full path from `surf-go js 'return document.title'` to the result appearing in the terminal.

**Source**: `src/service-worker/index.ts` lines 1930-1960

```
1.  Go command sends via Unix socket:
    { type: "EXECUTE_JAVASCRIPT", code: "return document.title", tabId: 42 }

2.  Service worker receives the message

3.  Service worker injects piHelpers (once per execution):
    await cdp.evaluateScript(tabId, PI_HELPERS_CODE)
    // PI_HELPERS_CODE = window.piHelpers = { wait, waitForSelector,
    //     waitForText, waitForHidden, getByRole }

4.  Service worker wraps user code in async IIFE:
    const expression = "(async () => {\n'use strict';\n" + message.code + "\n})()"

5.  CDP execution:
    const result = await cdp.evaluateScript(tabId, expression)
    // Uses Runtime.evaluate with awaitPromise: true

6.  Result handling:
    if (result.exceptionDetails) → return { error: formatted_exception }
    const value = result.result?.value
    const output = JSON.stringify(value, null, 2)

7.  Service worker sends back via socket:
    { value: output }

8.  Go command receives and prints to terminal
```

### 5.1 piHelpers Utilities

Injected before every execution to provide wait/selection utilities the page doesn't have natively:

```typescript
// Injected as a single minified string (service-worker/index.ts line 1935)
window.piHelpers = {
  wait(ms),                           // sleep
  waitForSelector(sel, { state, timeout }),  // wait for DOM element
  waitForText(text, { selector, timeout }),   // wait for text to appear
  waitForHidden(sel, timeout),               // wait for element to disappear
  getByRole(role, { name }),          // ARIA role selector helper
};
```

**Important**: `waitForSelector` uses a `MutationObserver` watching `document.documentElement` with `childList`, `subtree`, `attributes`, and `characterData` mutations. It polls visibility via `getComputedStyle`.

### 5.2 The IIFE Wrapper

The service worker's wrapper:
```typescript
const expression = "(async () => {\n'use strict';\n" + message.code + "\n})()";
```

**Constraint**: User code must end with an explicit `return <value>` to emit a result. Without it, the IIFE returns `undefined`.

**Constraint**: User code must not contain template literal `${...}` syntax — the outer string concatenation interpolates them. Workaround: use string concatenation instead.

### 5.3 Error Formatting

```typescript
// service-worker/index.ts ~144
function formatJavaScriptException(code, exceptionDetails) {
  // Maps CDP exceptionDetails back to line numbers in the original code
  // CDP line numbers are 0-based in the wrapped expression
  // Rewinds past the wrapper prefix to report the correct position
}
```

---

## 6. CDP in the Surf CLI Architecture

### 6.1 CDP Commands Used (Full Catalog)

| Command | Domain | Where Used |
|--------|--------|------------|
| `Runtime.enable` | Runtime | `enableConsoleTracking()`, `enableNetworkTracking()` |
| `Runtime.evaluate` | Runtime | `executeScript()`, polling loop, tab readiness, all probes |
| `Runtime.exceptionThrown` | Runtime | Event listener routing |
| `Runtime.consoleAPICalled` | Runtime | Console message collection |
| `Page.enable` | Page | `attach()`, `getFrames()` |
| `Page.getFrameTree` | Page | `getFrames()` |
| `Page.createIsolatedWorld` | Page | `evaluateInFrame()` |
| `Page.captureScreenshot` | Page | `captureScreenshot()` |
| `Page.handleJavaScriptDialog` | Page | `handleDialog()` |
| `Page.getLayoutMetrics` | Page | Screenshot viewport sizing |
| `Page.javascriptDialogOpening` | Page | Event listener |
| `Network.enable` | Network | `enableNetworkTracking()` |
| `Network.getResponseBody` | Network | `getResponseBody()`, lazy fetch on `loadingFinished` |
| `Network.emulateNetworkConditions` | Network | `emulateNetwork()` |
| `Input.dispatchMouseEvent` | Input | `click()`, `rightClick()`, `doubleClick()`, `tripleClick()`, `hover()` |
| `Input.dispatchKeyEvent` | Input | `dispatchKeyEvent()` |
| `Input.insertText` | Input | `insertText()` |
| `DOM.enable` | DOM | `setFileInputBySelector()` |
| `DOM.getDocument` | DOM | `setFileInputBySelector()` |
| `DOM.querySelector` | DOM | `setFileInputBySelector()` |
| `DOM.setFileInputFiles` | DOM | File upload |
| `Emulation.setDeviceMetricsOverride` | Emulation | `emulateDevice()`, `emulateViewport()` |
| `Emulation.setUserAgentOverride` | Emulation | `emulateDevice()` |
| `Emulation.setTouchEmulationEnabled` | Emulation | `emulateDevice()`, `emulateTouch()` |
| `Emulation.setGeolocationOverride` | Emulation | `emulateGeolocation()` |
| `Emulation.setCPUThrottlingRate` | Emulation | `emulateCPU()` |
| `Emulation.clearDeviceMetricsOverride` | Emulation | `clearDeviceEmulation()` |
| `Emulation.clearGeolocationOverride` | Emulation | `clearGeolocation()` |
| `Performance.enable` | Performance | `startPerformanceTrace()`, `getPerformanceMetrics()` |
| `Performance.getMetrics` | Performance | `getPerformanceMetrics()`, `stopPerformanceTrace()` |
| `Performance.disable` | Performance | After metrics collection |
| `Tracing.end` | Tracing | `stopPerformanceTrace()` |
| `Tracing.start` | Tracing | `startPerformanceTrace()` |

### 6.2 Message Types (Native Messaging Layer)

Above CDP sits the native messaging layer. The service worker receives these from the Go command via Unix socket:

| Message Type | CDP Command | Purpose |
|-------------|-------------|---------|
| `EXECUTE_JAVASCRIPT` | `Runtime.evaluate` | Run user JavaScript |
| `EVALUATE_IN_FRAME` | `Runtime.evaluate` + `Page.createIsolatedWorld` | Run in specific iframe |
| `CAPTURE_SCREENSHOT` | `Page.captureScreenshot` | Screenshot |
| `READ_CONSOLE_MESSAGES` | `Runtime.consoleAPICalled` (event) | Read collected console |
| `CLEAR_CONSOLE_MESSAGES` | — | Clear console buffer |
| `READ_NETWORK_REQUESTS` | `Network.*` (events) | Read collected network |
| `CLEAR_NETWORK_REQUESTS` | — | Clear network buffer |
| `CDP_COMMAND` | Any CDP command | Pass-through for arbitrary CDP |
| `GET_PAGE_TEXT` | `Runtime.evaluate` | Read page text |
| `CLICK_ELEMENT` | `Runtime.evaluate` + `Input.dispatchMouseEvent` | Click by selector |
| `TYPE_TEXT` | `Input.insertText` | Type into element |

**Source**: `src/service-worker/index.ts` — the `handleMessage()` function (around line 1930) routes all incoming message types.

---

## 7. CDP in Broader Ecosystem Context

### 7.1 Playwright

Playwright uses CDP for Chromium. It wraps CDP with a higher-level API:
- `page.evaluate()` → `Runtime.evaluate`
- `page.click()` → `Runtime.evaluate` (scrollIntoView) + `Input.dispatchMouseEvent`
- `page.waitForSelector()` → `DOM.getDocument` + `Runtime.evaluate` (MutationObserver)
- `page.screenshot()` → `Page.captureScreenshot`

Playwright is an **abstraction layer over CDP**, not an alternative to it.

### 7.2 Puppeteer

Puppeteer is the predecessor to Playwright's Chromium support. Also CDP-based, but with a thinner abstraction layer. Playwright's maintainers eventually consolidated on CDP after Puppeteer's approach diverged.

### 7.3 Selenium 4

Selenium 4 added CDP support via `driver.execute_cdp_command()`. This allows accessing CDP directly within Selenium tests, enabling features the WebDriver protocol doesn't cover (network interception, custom bindings, etc.).

### 7.4 browser-use

Notable case study: browser-use (a browser automation library for AI agents) **dropped Playwright in favor of raw CDP** in August 2025 for better performance and control.

From their writeup: *"Why we dropped Playwright and switched to raw CDP for faster, more capable browser automation."*

This validates Surf CLI's architecture: raw CDP gives full control over every aspect of browser automation, without abstraction layer overhead or capability gaps.

### 7.5 chromedp (Go)

`github.com/chromedp/cdp` and `github.com/chromedp/cdproto` are Go libraries for CDP. `cdproto` contains generated type definitions for all CDP domains.

**Relevant packages**:
- `github.com/chromedp/cdp` — low-level CDP client
- `github.com/chromedp/cdproto/runtime` — generated Runtime domain types
- `github.com/chromedp/cdproto/target` — generated Target domain types

Surf CLI uses TypeScript rather than Go for the CDP layer (in the browser extension), but the Go native host could potentially use `chromedp` if CDP access were needed server-side.

### 7.6 cdp-cli

`github.com/myers/cdp-cli` — a CLI tool providing `grep`/`tail`-friendly access to all CDP commands. Useful for manual CDP exploration.

### 7.7 Cloudflare Browser Rendering

Cloudflare's Browser Rendering product exposes CDP as an endpoint (April 2026 changelog). Clients can connect their own CDP client to control headless Chromium instances running on Cloudflare's infrastructure. This makes CDP the de facto standard for browser automation at scale.

---

## 8. Security Considerations

### 8.1 Chrome Restrictions

Chrome restricts debugger attachment on `chrome://`, extensions, and Web Store pages:

```
Cannot access this page. Chrome restricts automation on chrome://, extensions, and web store pages.
```

**Source**: controller.ts attach error handling.

### 8.2 CDP Debugger API Limitations

Research paper ([arXiv:2305.11506](https://arxiv.org/abs/2305.11506)): The Chrome Debugger API has architectural limitations on what targets an extension can attach to. Some browser surfaces (security interstitials, certain iframe contexts) cannot be automated via CDP.

### 8.3 CSP Interactions

`Runtime.evaluate` with `allowUnsafeEvalBlockedByCSP: false` (default) respects Content Security Policy. Pages with strict CSP may block `eval()` and `new Function()`. Setting `allowUnsafeEvalBlockedByCSP: true` bypasses this but requires the target to allow `unsafe-eval`.

---

## 9. Further Research Points

### 9.1 Streaming via Runtime.addBinding

**Research path**: Enable `Runtime.enable`, inject `Runtime.addBinding({ name: 'surfStream' })`, register a listener for `Runtime.bindingCalled` events. Test whether ChatGPT's token streaming calls a global function that could be intercepted.

**Evidence this matters**: The current polling loop (400ms intervals) is the primary bottleneck. A binding-based approach would be event-driven.

### 9.2 Token Capture via Fetch Domain

**Research path**: Call `Fetch.enable({ patterns: [{ urlPattern: 'https://chat.openai.com/backend-api/*' }] })` before navigating to ChatGPT. Log `Fetch.requestPaused` events to capture the `Authorization: Bearer <token>` header from any authenticated request.

**Evidence this matters**: The TR confirmed `/textdocs` returns 401 from page context. Fetch domain intercepts before the request is sent, making the header visible.

### 9.3 Network Interception for AI Provider APIs

Beyond ChatGPT token capture: the Network domain can intercept all AI provider API calls (Anthropic, Google, etc.) with full request/response bodies. This would enable:
- Automated API call logging
- Response modification/replay
- Token counting and cost tracking

---

## 10. Key Source Files

| File | Lines | Purpose |
|------|-------|---------|
| `src/cdp/controller.ts` | 1,431 | Full CDP controller implementation |
| `src/service-worker/index.ts` | ~3,200 | Service worker + message routing + EXECUTE_JAVASCRIPT handler |
| `go/internal/host/providers/chatgpt.go` | ~1,100 | Provider using CDP for ChatGPT polling |
| `go/internal/cli/commands/tab_ready.go` | ~100 | Tab readiness using Runtime.evaluate |
| `test/unit/cdp/controller.test.ts` | ~1,200 | Unit tests for CDP controller |

---

## References

- Official Spec: https://chromedevtools.github.io/devtools-protocol/
- TypeScript Definitions: https://github.com/ChromeDevTools/devtools-protocol
- Surf CLI CDP Controller: `src/cdp/controller.ts`
- Surf CLI Service Worker: `src/service-worker/index.ts`
- browser-use raw CDP migration: https://browser-use.com/posts/playwright-to-cdp
- Cloudflare Browser Rendering CDP: https://developers.cloudflare.com/browser-rendering/cdp/
- chromedp Go library: https://github.com/chromedp/cdp
- CDP security research: https://arxiv.org/abs/2305.11506

---

*This document is part of the [[TR-2026-0411-001 - ChatGPT Transcript Extraction System - Implementation and Methodology|TR-2026-0411-001]] research context. For related browser automation patterns, see [[ARTICLE - surf-go Browser Verbs - Using JS Probes to Build Reliable Web Automation]]. For probe script methodology, see [[PROJ - DOM Scraping Experiment - Web to Markdown via JS DOM Queries]].*
