# reMarkable app tech stack

- URL: https://chatgpt.com/c/6a60b9ce-18dc-83ea-a898-bd2f72caaf81
- Created: 2026-07-22T12:38:42.116Z

---

> Research Maxime rivest remarkable work (the tablet), I want to write an app where I write and then it draws maths on the side to it for example when I ask questions, and it would kind of do http calls but also rest back, what’s the tech stack, ideally I’d want go but I don’t know about layout engines on the tablet and its specs and how fast and all that. Or something like can I script and reload js into qtqml for example (I use a lot of sandboxed JS).

I’ll identify Rivest’s reMarkable project, then map the device constraints to practical stacks: native Qt/QML, Go hybrids, and sandboxed JavaScript.

```json
{"system1_search_query":[{"q":"Maxime Rivest reMarkable tablet project GitHub"},{"q":"site:github.com Maxime Rivest remarkable tablet"},{"q":"Maxime Rivest remarkable work tablet"},{"q":"reMarkable tablet Maxime Rivest"}],"image_query":[{"q":"Maxime Rivest reMarkable tablet"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 100 websites**

**Researching Qt/QML JS handling**

I’m looking into how to reload JavaScript in Qt QML, including dynamic loading with caching, and checking the sandboxing capabilities of QJSEngine. Official specs and potential limitations need attention.

**Researched Qt/QML JS handling**

**Exploring Go and Qt integration**

I’m considering ways to structure the user’s app, including using Go for backend logic and a thin QML frontend. I need to decide between math rendering options and handling layouts efficiently, while also exploring efficient communication methods.

**Explored Go and Qt integration**

</details>

```json
{"click":[{"ref_id":"turn723714view0","id":78},{"ref_id":"turn723714view0","id":81},{"ref_id":"turn723714view0","id":93},{"ref_id":"turn723714view0","id":91},{"ref_id":"turn723714view0","id":95}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 19 websites**

</details>

```unknown
bash -lc rm -rf /tmp/riddle /tmp/quill && git clone --depth 1 https://github.com/MaximeRivest/riddle.git /tmp/riddle && git clone --depth 1 https://github.com/MaximeRivest/quill.git /tmp/quill && printf '\nRIDDLE FILES\n' && find /tmp/riddle -maxdepth 2 -type f | sort | sed 's#/tmp/riddle/##' | head -80 && printf '\nQUILL FILES\n' && find /tmp/quill -maxdepth 2 -type f | sort | sed 's#/tmp/quill/##' | head -80
```

```json
{"paths":["GitHub"],"query":"contents"}
```

<details><summary>💭 Thinking</summary>

**Cloned and inspected GitHub repos**

</details>

```python3
{"path":"/GitHub/link_694554034b848191ab0db5a14b130105/fetch_file","args":{"repository_full_name":"MaximeRivest/riddle","path":"src/qtfb.rs","start_line":1,"end_line":260}}
```

<details><summary>💭 Thinking</summary>

**Fetched code files, handled citations, and retrieved Quill API**

</details>

```json
{"system1_search_query":[{"q":"site:doc.qt.io/qt-6 QJSEngine evaluate setInterrupted documentation"},{"q":"site:doc.qt.io/qt-6 QML JavaScript import external file documentation"},{"q":"site:doc.qt.io/qt-6 QQmlEngine clearComponentCache QML reload"},{"q":"site:doc.qt.io/qt-6 QML XMLHttpRequest documentation"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 39 websites**

</details>

I’m assuming you mean **reMarkable Paper Pro**, because that is the device targeted by Maxime Rivest’s work.

## What Maxime Rivest built

Rivest’s project is **Riddle**: you write on the tablet, pause, and the page is sent as an image to a vision-capable language model. The response is then converted into handwriting-like strokes and drawn back onto the display. Its pipeline is approximately:

```text
raw pen events
    ↓
stroke/page renderer
    ↓
PNG snapshot
    ↓
OpenAI-compatible /chat/completions endpoint
    ↓
streamed text
    ↓
font rasterization → skeletonization → traced strokes
    ↓
e-ink partial updates
```

Riddle is written in **Rust**, reads raw Linux input events, uses a minimal HTTP client with pure-Rust TLS, and supports OpenAI-compatible APIs including local servers. Its handwriting output is produced by rasterizing a font, thinning the bitmap with Zhang–Suen skeletonization, and tracing that skeleton into drawable strokes. citeturn157810view0turn179629view1turn585038view5

There are two display backends:

- **qtfb/AppLoad:** runs as a window alongside reMarkable’s normal software.
- **Quill takeover:** stops the normal reMarkable application and talks more directly to the vendor e-paper engine for lower latency.

Importantly, Riddle’s qtfb mode is **not a Qt Quick/QML interface**. It is a native client using a Unix `SOCK_SEQPACKET` socket and a shared-memory RGB565 framebuffer. It explicitly requests full or rectangular partial updates. fileciteturn0file0L3-L25 fileciteturn0file0L43-L63 fileciteturn0file0L181-L211

Quill exposes a small C ABI: initialize, get the framebuffer pointer, write pixels, and submit dirty rectangles. It has separate operations for low-latency monochrome updates and higher-quality color updates. fileciteturn1file0L9-L14 fileciteturn1file0L26-L47

## Hardware constraints

The Paper Pro has:

- 11.8-inch, 2160 × 1620 display at 229 ppi
- 1.8 GHz quad-core Cortex-A53
- 2 GB LPDDR4 RAM
- 64 GB storage
- 2.4/5 GHz Wi-Fi
- Custom Linux-based reMarkable OS

The portrait framebuffer used by qtfb is effectively 1620 × 2160 RGB565. citeturn957251view0 fileciteturn0file0L21-L25

That hardware is sufficient for:

- A Go application
- HTTPS and JSON processing
- PNG/SVG rasterization
- Lightweight JavaScript execution
- Stroke processing
- A modest Qt Quick UI

It is a poor target for:

- Chromium or Qt WebEngine
- Continuous full-screen animation
- A large local vision model
- Repeated full-screen color refreshes
- Heavy browser-based MathJax rendering on every edit

The main limitation is generally **the e-ink refresh strategy**, not the CPU. Fast monochrome dirty rectangles should be used for pen strokes. Slower color or quality refreshes should be restricted to static diagrams, highlights, or the math panel. Quill explicitly distinguishes these update classes. citeturn157810view2

Riddle reports around **0.9–1.1 seconds from starting its HTTP request to the first rendered response ink**, depending on the model endpoint. It deliberately waits about 2.8 seconds after writing stops before committing a page, so its full perceived interaction is closer to four seconds in that configuration. citeturn157810view0

## Recommended architecture

For your application, I would use:

```text
                    ┌─────────────────────────┐
raw evdev pen ─────▶│ Go application/daemon   │
                    │                         │
                    │ strokes + page state    │
                    │ HTTP/SSE client         │
                    │ script supervisor       │
                    │ persistence             │
                    └──────┬───────────┬──────┘
                           │           │
                    qtfb or Quill      │ HTTPS
                           │           ▼
                           │    model/backend API
                           │           │
                           │     JSON/SVG/strokes
                           ▼           │
                    Paper Pro display ◀┘
```

### First version: Go plus qtfb

This is probably the best starting point.

Use:

- **Go** for the application state, networking, event loop and scripting.
- `golang.org/x/sys/unix` for raw input, Unix sockets and memory mapping.
- **qtfb/AppLoad** as the display backend.
- A small custom immediate-mode layout rather than a general layout engine.
- Server-rendered math returned as SVG, PNG, or stroke paths.
- Unix-domain sockets only if you later divide it into multiple processes.

The qtfb protocol is small enough to reproduce in Go. You would:

1. Connect to `/tmp/qtfb.sock` using `AF_UNIX` and `SOCK_SEQPACKET`.
2. Send its initialization message.
3. Open and `mmap` the returned shared-memory framebuffer.
4. Draw RGB565 pixels into it.
5. Submit rectangular partial-update messages.

That avoids Qt entirely while retaining the safer “window within xochitl” behavior. The feasibility is an inference from Rivest’s approximately 260-line native qtfb implementation. fileciteturn0file0L68-L166

For your split-screen UI, a complete layout engine is unnecessary:

```text
┌────────────────────────────────┬──────────────┐
│                                │              │
│ handwriting / question area    │ math answer  │
│                                │ panel        │
│                                │              │
└────────────────────────────────┴──────────────┘
```

For example:

- Left 72%: input and notebook
- Right 28%: generated equations and explanations
- Only repaint the dirty stroke rectangle while writing
- Repaint the answer panel when a response arrives
- Perform an occasional quality cleanup refresh

## Moving to Quill

Once the application works, Quill is the lower-latency option.

Its API is suitable for **cgo** because it is intentionally small:

```c
quill_init();
quill_buffer();
quill_swap_mono_fast(x, y, w, h);
quill_swap_color(x, y, w, h);
```

The complication is not the API. It is cross-compiling and linking against the device/vendor environment. reMarkable provides a Yocto SDK for the Paper Pro, whose codename is `ferrari`, with an AArch64 Cortex-A53 toolchain. citeturn127927view1turn127927view4

Two sensible arrangements are:

```text
Go application ──cgo──▶ libquill.so
```

or, for easier isolation:

```text
Go application ──Unix socket──▶ tiny C/Rust display process ──▶ Quill
```

The second arrangement makes cross-compilation and crashes easier to contain.

Quill takeover should come later because it stops the normal reMarkable application, runs with elevated privileges in Riddle’s bundle, and needs careful recovery if your program crashes. Riddle’s documentation recommends keeping an SSH escape path available. citeturn157810view0

## Qt/QML is possible

reMarkable OS is Yocto-based Linux, and its main `xochitl` application is proprietary software built using Qt. The official development documentation includes Qt 6 Quick examples and states that third-party UI should use Qt Quick rather than Qt Widgets. citeturn127927view2turn127927view3

A Qt architecture could be:

```text
Qt Quick/QML shell
  ├── RowLayout / ColumnLayout
  ├── controls and answer panel
  └── native ink QQuickItem
             │
             │ Unix socket / localhost HTTP
             ▼
          Go daemon
  ├── model HTTP calls
  ├── persistence
  ├── script execution
  └── response processing
```

This makes sense when you want:

- Declarative layouts
- Rapid UI iteration
- Buttons, menus and state handling
- JavaScript for trusted presentation logic

Qt Quick provides `RowLayout`, `ColumnLayout`, `GridLayout` and related layout primitives. citeturn905770search4

However, do **not** implement the live pen renderer using QML’s JavaScript `Canvas`. Qt itself warns that large canvases and frequent updates can perform poorly. Use a custom `QQuickItem`, native framebuffer renderer, or a C++ `QQuickPaintedItem` for the ink layer. citeturn905770search9turn905770search2

I would also avoid Go-to-Qt binding libraries. A small Qt/C++ frontend talking to a Go daemon is more maintainable and less sensitive to Qt version mismatches.

## Can you reload JavaScript and QML?

Yes, for development and trusted application code.

QML can import ordinary JavaScript:

```qml
import "logic.js" as Logic
```

and ECMAScript modules using `.mjs`. QML also provides an asynchronous `XMLHttpRequest`, although putting credentials and model networking in QML is not advisable. citeturn587255search0turn587255search5

A practical development reload loop is:

1. Keep `.qml`, `.js` and `.mjs` files on the filesystem rather than compiling them into Qt resources.
2. Copy updated files using `scp` or `rsync`.
3. Watch the directory using `inotify`.
4. Destroy the current root QML objects.
5. Destroy and recreate the `QQmlEngine`.
6. Load the root QML file again.
7. Start the process with `QML_DISABLE_DISK_CACHE=1` during development.

`QQmlEngine::clearComponentCache()` exists, but old QML objects must no longer reference the cached types. Recreating the engine is more reliable, especially because imported JavaScript modules remain cached for the lifetime of the engine. citeturn905770search0turn587255search8turn905770search1turn392182search1

For production, restart-based reload is even simpler:

```text
file changed → save state → exit frontend → launcher restarts frontend
```

On this class of hardware, restarting a small QML frontend is usually preferable to building a complicated live-patching system.

## QJSEngine is not a security sandbox

This distinction matters because you mentioned sandboxed JavaScript.

`QJSEngine` can evaluate strings, load modules, expose selected native objects and interrupt runaway execution. But Qt explicitly states that this is **not an operating-system security boundary**: JavaScript runs inside the application process with the application’s privileges and shared memory. Loading remote QML or JavaScript is effectively executing application code. citeturn392182search1turn587255search6turn392182search2turn392182search5

Use QJSEngine only when the scripts are trusted.

For genuinely sandboxed scripts, use:

```text
Go supervisor
    │
    ├── launches QuickJS or another JS runtime as a child process
    ├── communicates using JSON-RPC over a Unix socket
    ├── gives scripts no direct framebuffer or API-key access
    ├── enforces request deadlines
    └── kills and recreates the process on timeout
```

Expose a narrow API such as:

```json
{
  "methods": [
    "getCurrentPage",
    "addEquation",
    "addAnnotation",
    "requestModel",
    "invalidateRectangle"
  ]
}
```

Use process-level restrictions where available: a separate unprivileged user, restricted filesystem view, `setrlimit`, syscall filtering, and memory/time limits. Do not depend on QJSEngine’s object visibility as the security boundary.

## Math rendering strategy

Do not send only prose back from the model. Use a structured response:

```json
{
  "answer": "Differentiate both sides...",
  "latex": "\\frac{dy}{dx}=2x+3",
  "placement": "right-panel",
  "display": "equation"
}
```

For diagrams:

```json
{
  "answer": "The tangent intersects here.",
  "drawing": {
    "format": "svg-paths",
    "width": 460,
    "height": 700,
    "paths": []
  }
}
```

I would render LaTeX on your backend using KaTeX, MathJax, Typst, or a TeX service and return one of:

1. **Monochrome SVG paths** — best for scaling and drawing animations.
2. **Grayscale PNG** — easiest to implement.
3. **A small equation AST** — best if you later implement a native math layout engine.

For the initial product, server-rendered SVG or PNG is the correct tradeoff. Building an on-device TeX layout system before validating the interaction would consume substantial effort without improving pen latency.

## HTTP arrangement

Keep API keys and external networking in Go:

```text
QML or renderer
   │ local Unix socket
   ▼
Go daemon
   │ HTTPS POST
   ▼
your backend / model API
   │ SSE or NDJSON stream
   ▼
Go daemon
   │ incremental answer updates
   ▼
right-side panel
```

Riddle uses an OpenAI-compatible `/chat/completions` endpoint, sends the page PNG as a base64 data URI, and processes the streaming response incrementally. citeturn585038view1

For your protocol, I would use newline-delimited JSON or SSE:

```json
{"type":"text","value":"First isolate x."}
{"type":"equation","latex":"x = \\frac{-b \\pm \\sqrt{b^2-4ac}}{2a}"}
{"type":"complete"}
```

The Go daemon should own:

- API credentials
- Request cancellation
- Retries
- Timeouts
- Streaming parsers
- Page-image compression
- Response caching
- Offline queueing

## Concrete stack recommendation

| Layer | Initial choice | Later option |
|---|---|---|
| Language | Go | Go plus small C/Rust helper |
| Display | AppLoad/qtfb | Quill takeover |
| Pen input | Raw `evdev` | Same |
| Layout | Custom fixed rectangles | Qt Quick shell |
| Math | Server-rendered SVG/PNG | Native AST renderer |
| Networking | Go `net/http`, SSE/NDJSON | Same |
| Trusted scripts | QJSEngine or embedded JS runtime | Same |
| Untrusted scripts | Separate QuickJS process | Stronger OS isolation |
| Storage | JSON/SQLite/page PNGs | Same |
| IPC | Unix-domain socket | Same |

My implementation order would be:

1. Build a pure-Go ARM64 application.
2. Reimplement the small qtfb protocol.
3. Capture and render raw pen strokes.
4. Add a fixed right-side answer panel.
5. Send page images to your backend.
6. Return structured text plus LaTeX.
7. Render math server-side and blit it into the answer panel.
8. Add process-isolated JavaScript.
9. Evaluate Qt Quick only when the interface needs more sophisticated controls.
10. Move the renderer to Quill only after the complete workflow is stable.

That keeps the first prototype small, preserves Go as the primary language, and avoids introducing Qt, cgo and vendor e-paper APIs simultaneously.

