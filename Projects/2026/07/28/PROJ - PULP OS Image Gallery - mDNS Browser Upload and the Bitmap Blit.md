---
title: "PULP OS Image Gallery — mDNS, Browser Upload, and the Bitmap Blit"
aliases:
  - ESP-54 PULP Gallery
  - PULP OS image gallery
  - PaperS3 picture frame
tags:
  - project
  - esp32
  - esp-idf
  - eink
  - microquickjs
  - firmware
  - networking
status: active
type: project
created: 2026-07-28
repo: /home/manuel/code/wesen/go-go-golems/esp32-s3-m5/0114-papers3-pulp-os
---

# PULP OS Image Gallery — mDNS, Browser Upload, and the Bitmap Blit

The PaperS3 is an ESP32-S3 device with a 540×960 16-gray e-ink panel, a capacitive touch layer, an SD card slot, and a battery. It runs PULP OS, a small application operating system whose ten built-in apps are written in JavaScript and compiled to bytecode that runs on a vendored MicroQuickJS engine. ESP-54 extends PULP OS with four capabilities that turn the device into a networked picture frame: a multicast DNS hostname, a web page that converts photographs to 4-bit grayscale in the browser and uploads them to the SD card, a gallery app that displays and scrolls through those photographs, and a persistent battery indicator. This report explains how each capability works at the level of memory layout, task ownership, and the pixel pipeline, and why the design makes the choices it does.

> [!summary]
> - mDNS is a managed component, not an IDF built-in, and its lifecycle is bound to the web server, not the radio.
> - All image decode, resize, and quantization happens in the browser; the device receives a ready 4-bit packed frame and does a pure streaming copy to the SD card.
> - The display path finishes a draw operation that was declared in the core two tickets earlier but never implemented in the hardware backend — the bitmap blit is the central engineering contribution.

## Why this project exists

The operator wants to treat the e-ink tablet as a networked picture frame. Photographs live on a laptop or phone; the device has no keyboard fast enough for filenames and no decode libraries for PNG or JPEG. The realistic workflow is therefore one-directional: open a web page served by the device, drop a photograph, and have it appear on the panel. The device's job is to be reachable by name, accept a converted image, store it, and render it. None of these steps require the device to understand the source image format.

This framing determines every architectural decision. The device's scarce resources — 512 KB of internal SRAM, a single UI-owner task, a panel that takes roughly one second to fully refresh — are not spent on decode. The browser, which has gigabytes of memory and a mature canvas pipeline, performs every pixel transformation. The wire format between the two is a compact 4-bit packed representation that is also the storage format and the display format, so the device performs no conversion at any stage.

## Current project status

All four capabilities are implemented, built, and verified on hardware. The firmware compiles cleanly under ESP-IDF 5.3.4. The host test suite for the shared s3paper core passes 38,186 checks, including a new test for the bitmap draw operation. On the device, four numbered probes exercise each feature and print deterministic evidence. An operator on the same WiFi network can open `http://pulp.local`, drop a JPEG, and view it on the panel after turning the tablet sideways for landscape photographs.

The implementation lives in the `0114-papers3-pulp-os` firmware directory and the shared `components/s3paper_core`, `components/s3paper_m5`, and `components/s3paper_runtime` components. The design document, diary, and helper scripts are in the docmgr ticket `ESP-54-PULP-GALLERY`.

## Project shape

The four capabilities layer onto an existing system that was built across three prior tickets. Understanding the shape requires knowing what was already there and what ESP-54 adds.

- **ESP-51** defined the one-owner-task architecture, the POD widget tree, and the MicroQuickJS binding layer.
- **ESP-52** added the canvas widget and freehand drawing primitives.
- **ESP-53** added the connectivity layer: WiFi station mode, HTTP fetch, an embedded web server with JavaScript-defined routes, general SD file access, and the buzzer.
- **ESP-54** adds mDNS, the image upload route, the image catalog and display module, the bitmap draw operation, the gallery app, and the battery surface.

The four ESP-54 capabilities map onto the existing layers without introducing new concurrency models or new storage families. mDNS is a thin wrapper over a managed component, wired into the web server's lifecycle. The upload route extends the web server's existing request-slot handoff. The catalog and display module reuses the SD access discipline already established for books. The bitmap draw operation implements a contract that the core had declared but left unfinished.

## The constraint field

Three constraints shape every line of ESP-54 code. They are inherited from the prior tickets and are non-negotiable.

The first constraint is the **one-owner-task rule**. A single FreeRTOS task, pinned to core 1, owns all UI state, the JavaScript engine, and the widget arena. Every other task — the WiFi event loop, the HTTP client worker, the httpd request handler — may only post plain-old-data events to the owner's queue. They never call into JavaScript, never touch the widget arena, and never read the durable state files. This rule exists because the alternative is locks around shared UI state, and locks around UI state produce deadlocks and priority inversions on a device whose primary job is to remain responsive to touch.

The second constraint is the **int32 callback boundary**. MicroQuickJS uses a compacting garbage collector that can move pointer-tagged values during any allocation. C code therefore cannot safely hold a JavaScript closure across an allocating call. The solution, established in ESP-53, is to root closures in a JavaScript-side array named `__cbs` and store only integer indices in C. When a worker task finishes, it posts a `ModuleDone` event carrying three integers — a kind, a value, and an error. The owner looks up the callback by index and invokes it with those three integers. Strings and structured data travel through native mailbox accessors that the callback reads after it has been invoked, never through the callback arguments themselves.

The third constraint is **e-ink discipline**. Every pixel change on the panel is planned. A partial update is fast but leaves residual ghosting that accumulates. A full refresh clears ghosting but takes roughly one second and produces a visible flash. The presentation pipeline therefore diffs each new frame against the previous one, computes the damaged rectangles, and a refresh planner decides whether to issue a partial update or force a clean full. The JavaScript layer describes widget trees; the native layer decides what actually reaches the panel.

## Architecture

```mermaid
flowchart TD
    HOST["Operator browser<br/>(decode, crop, scale, quantize, pack)"]
    DEVICE["PaperS3 (ESP32-S3)"]
    subgraph FW["PULP OS firmware"]
        HTTPD["esp_http_server task<br/>GET routes + POST /images/upload"]
        OWNER["Owner task (core 1)<br/>JS engine, widget arena, catalog"]
        SD["SD card<br/>/sdcard/images/*.g4"]
        EPD["e-ink panel<br/>540x960 16-gray"]
    end
    HOST -- "POST .g4 (253 KiB)" --> HTTPD
    HTTPD -- "stream body" --> SD
    HTTPD -- "ModuleDone{Images}" --> OWNER
    OWNER -- "FrameBuilder.Bitmap" --> EPD
    OWNER -- "mDNS announce" -.-> HOST
```

The browser performs every pixel transformation and sends a 253 KiB packed frame. The httpd task streams that frame directly to the SD card, which is the one sanctioned off-owner storage write in the system. The owner task is notified through the completion mailbox, builds a single-bitmap draw frame, and presents it with a forced clean-full refresh. mDNS advertising flows in the opposite direction: the owner announces the hostname when the server starts, and the browser resolves `pulp.local` to reach the device.

## Implementation details

### The 4-bit packed grayscale frame format

The wire, storage, and display format is one structure. Defining it once and reusing it everywhere is the decision that keeps the device work trivial.

```c
struct G4Header {
    char magic[4];       // "G4IM"
    uint16_t width;      // 540 (little-endian)
    uint16_t height;     // 960
    uint8_t depth;       // 4
    uint8_t version;     // 1
    uint16_t reserved;   // 0
} __attribute__((packed));
static_assert(sizeof(G4Header) == 12, "G4 header must be 12 bytes");
```

Following the 12-byte header is the pixel data. Each byte holds two pixels: the high nibble is the even-x pixel, the low nibble is the odd-x pixel. Rows are laid out in row-major order, and each row is padded to an even byte count because two pixels share a byte. For a 540-pixel-wide frame, each row occupies 270 bytes, and the full pixel payload is 259,200 bytes — approximately 253 KiB.

The choice of 4 bits per pixel is not arbitrary. The PaperS3 panel renders 16 gray levels. A 4-bit value indexes those levels directly with no arithmetic on the device. The browser, which has a full 8-bit-per-channel canvas, performs the 256-level-to-16-level quantization, optionally with Floyd-Steinberg dithering to preserve gradients. The device unpacks a nibble to a gray level and writes it; it never computes a luminance, never dithers, never resamples.

### Why the browser does all the image work

The decision to push decode, resize, and quantization into the browser is forced by the constraint field, not chosen for elegance. The device has approximately 220 KB of free internal SRAM at steady state. A single 540×960 frame decoded to 8-bit-per-channel RGB consumes 1.5 MB, and the intermediate buffers a JPEG decoder maintains often exceed that. Internal RAM is the wrong place to spend a megabyte on a one-time conversion, and the ESP32-S3's flash would pay a 60 to 100 KB cost for a decode library that serves a use case the browser already handles at zero device cost.

The browser path is direct. A file input feeds a `FileReader`, which produces a data URL consumed by an `Image`. The image is drawn onto an offscreen canvas sized to the panel. The operator chooses fit (contain) or fill (cover) and, for landscape source images, rotation. The page reads the canvas `ImageData`, converts each pixel to luminance using the standard `Y = (R·299 + G·587 + B·114) / 1000` weighting, optionally distributes the quantization error to neighbors via Floyd-Steinberg, reduces the result to a 0-to-15 nibble, and packs two nibbles per byte. The packed buffer is prefixed with the 12-byte header and posted as an opaque binary body.

```javascript
// The pack step, abbreviated. High nibble carries the even-x pixel.
var off = y * rowB + (x >> 1);
if ((x & 1) === 0) px[off] = g << 4; else px[off] |= g;
```

The device receives this buffer and treats it as opaque. It validates the 12-byte header on the first received chunk, streams every subsequent chunk to a file, and never interprets a pixel. This separation means the `.g4` format is a versioned contract: the `version` byte in the header exists precisely so the format can evolve without breaking stored images.

### The completion mailbox

The upload does not hand the image body to the owner task. Doing so would either flood the owner queue with chunks or require a 253 KiB contiguous buffer in internal RAM. Instead, the httpd task streams the body to the SD card itself and notifies the owner only of completion. This is the documented second sanctioned off-owner storage access: ESP-53 established the first for static-file reads, and ESP-54 establishes its mirror for image writes. Both access the SD card through the VFS layer, which is task-safe, and both are restricted to a specific directory — static files read from `/sdcard/www`, images write to `/sdcard/images`.

The handoff follows the pattern every async operation in PULP OS follows.

```
httpd task                              owner task
----------                              ----------
claim single upload slot (Busy -> 503)
open /sdcard/images/<ts>.g4 for write
for each chunk:
    httpd_req_recv -> validate header once -> fwrite
    append to catalog index
fill ImagesUploadResult mailbox {name, bytes, err}
PostModuleDone(Images, Upload, bytes, err)
                                       CallCb(received_cb, kind, bytes, err)
                                       JS callback reads images.count()
```

The single-slot design means a second concurrent upload receives an immediate 503 response. This is a deliberate trade: the PaperS3 is not a web farm, and serializing uploads eliminates correlation identifiers, mailbox sizing, and partial-write bookkeeping. The mailbox is filled before the event is posted, and the FreeRTOS queue send and receive form the memory barrier, so no locks protect the mailbox contents.

### The latent draw operation

The most interesting engineering in ESP-54 is not the network path. It is finishing a draw operation that the core had declared but never implemented.

The s3paper core defines a `DrawOp` union with kinds for every primitive the pipeline can emit: `FillRect`, `StrokeRect`, `HLine`, `VLine`, `GlyphRun`, `Bitmap`, `Line`, and `Circle`. Each kind carries a payload. The `Bitmap` payload is three fields:

```c
struct BitmapPayload {
    uint32_t data_offset;  // arena offset of pixel data
    uint32_t data_len;
    int32_t stride;        // bytes per row
};
```

The `FrameBuilder` class has methods to emit every other operation — `FillRect`, `GlyphRun`, `Circle`, and so on — but no method to emit a `Bitmap`. And the M5 hardware backend, when it encountered a `Bitmap` operation, contained this:

```c
case DrawOpKind::Bitmap:
    // Explicitly unsupported in Phase 2.
    result.ops_skipped++;
    break;
```

The operation was a declared contract with no emitter and no rasterizer. This is the gap ESP-54 fills. The work has three parts.

The first part is the emitter, added to the `FrameBuilder`. It follows the `GlyphRun` pattern exactly: the pixel data is copied into the frame arena, the operation's payload records the arena offset, and the operation is clipped against the current clip stack and emitted.

```c
Status FrameBuilder::Bitmap(const Rect &bounds, const uint8_t *data,
                            uint32_t data_len, int32_t stride) {
    const Result<Rect> clipped = Intersect(bounds, CurrentClip());
    if (IsEmpty(clipped.value)) { dropped_clipped_++; return OkStatus(); }
    const Result<uint32_t> stored = arena_->PushBytes(data, data_len, 1);
    DrawOp op{};
    op.kind = DrawOpKind::Bitmap;
    op.bounds = clipped.value;
    op.clip = CurrentClip();
    op.payload.bitmap = {stored.value, data_len, stride};
    return Emit(op);
}
```

Copying the pixel data into the arena is necessary because the frame is immutable from emission through presentation. The arena is a fixed PSRAM buffer whose lifetime spans the present. Holding a pointer to the caller's buffer would risk use-after-free if the caller freed it before the panel finished refreshing. The arena's capacity, therefore, must accommodate a full image. The default runtime configuration allocates a 32 KB arena, which cannot hold a 253 KB image. ESP-54 raises the arena to 320 KB at firmware initialization, which fits a full image plus the text payloads the rest of the system emits, and leaves over five megabytes of PSRAM free.

The second part is the rasterizer, added to the M5 backend. M5GFX has no native 4-bit grayscale blit, so the rasterizer unpacks nibbles to the panel's gray levels and writes them one row at a time. The efficient path is a per-row `pushImage` call with an RGB565 scratch buffer, because `pushImage` is M5GFX's fast blit and the panel quantizes 565 internally.

```c
for (int32_t y = 0; y < h; ++y) {
    const uint8_t *s = src + y * b.stride;
    for (int32_t x = 0; x < w; ++x) {
        const uint8_t nib = (x & 1) ? (s[x >> 1] & 0x0F)
                                    : (s[x >> 1] >> 4);
        const uint8_t g = (nib * 255) / 15;     // 0..15 -> 0..255
        row[x] = M5.Display.color565(g, g, g);  // -> RGB565 gray
    }
    M5.Display.pushImage(op.bounds.x, op.bounds.y + y, w, 1, row);
}
```

The clip rect is honored because the operation carries the clip that was in force at emission time, and the per-row `pushImage` is bounded by the operation's clipped bounds. A bitmap drawn inside a canvas widget therefore cannot scribble outside that widget's frame, preserving the containment invariant that the canvas fuzzer established in ESP-52. The row scratch is allocated once in PSRAM and grown on demand, so it does not churn the heap across successive images.

The third part is the display path in the images module. When the gallery requests a display, the module reads the `.g4` file, validates the header, loads the packed pixels into a PSRAM buffer, begins a frame, emits a single `Bitmap` operation covering the full panel, finishes the frame, and presents it with `PresentIntent::CleanFull`.

```c
s3paper::FrameBuilder &fb = s3paper_runtime::FrameBuilderRef();
fb.Begin();
const s3paper::Rect full{0, 0, 540, 960};
fb.Bitmap(full, s_disp_buf, pixel_bytes, row_bytes);
const auto frame = s3paper_runtime::FinishFrame();
s3paper_runtime::PresentFramePlanned(
    frame.value, s3paper::PresentIntent::CleanFull, true);
```

The `CleanFull` intent is deliberate. A new image is the largest possible grayscale change — every pixel differs from the previous frame. A partial update on such a change produces severe ghosting. Forcing a clean full refresh spends roughly one second but produces a correct image. The gallery app reinforces this by setting `paper.refreshTurns(1)`, which tells the refresh planner to treat every present as a screen change requiring a full refresh.

### The diagonal-stripe diagnosis

During verification, the operator reported diagonal stripes on the panel. The displayed image was a generated test frame whose pixel value was `(x + y) % 16` — a gradient that, by construction, increases diagonally and wraps every 16 levels. The stripes were the image content, not a rendering artifact. To confirm this, a second diagnostic image was generated with 16 strictly horizontal bands, a black square in the top-left corner, and a white cross. When that image displayed, the bands were horizontal and the square and cross were correctly placed. A stride-shear bug — the class of defect that turns horizontal bands into diagonal ones — would have sheared the bands. The rasterizer was correct; the first test image had simply been chosen to look diagonal.

### mDNS as a managed component

Multicast DNS lets the browser reach the device at `pulp.local` instead of an IP address that must be looked up through the console. In ESP-IDF versions before 5.x, mDNS was a component shipped inside the framework tree. In 5.x it moved to the Espressif component registry as `espressif/mdns`. The IDF 5.3.4 tree pinned by this firmware contains no `components/mdns` directory; only `esp_local_ctrl` and `openthread` reference it internally. The dependency must therefore be declared in the per-component manifest at `0114-papers3-pulp-os/main/idf_component.yml` and added to the `REQUIRES` list in the component CMakeLists. A root-level manifest would be ignored, which is a recurring trap documented in the project's agent instructions.

The lifecycle binds mDNS to the web server, not to the radio. The wrapper announces the `_http._tcp` service inside `ServeStart` once the listener is up, and withdraws it inside `ServeStop`. It also withdraws inside `WifiOff` and the power quiesce sequence, because a hostname advertised on a dead link produces stale records. The announce is lazy and idempotent: it defers if WiFi is not yet up, and a no-op if already announced on the same port. This means the operator never manages mDNS directly. If the server is running and the radio is up, the name resolves.

### Battery display

The battery work is the smallest of the four, and it is almost entirely surface area. The data already existed. The `PowerStatus` struct, read through M5Unified's `Power` class, carries `battery_level`, `battery_mv`, and a `charging` flag. The firmware's console status command already printed all three. What was missing was JavaScript access to the charging state and the millivolts, and a persistent indicator in the launcher chrome.

ESP-54 adds a `battery` singleton with four methods: `level()`, `mv()`, `charging()`, and `statusText()`. The first three are thin wrappers over the existing power read. The fourth returns a formatted string such as `82%` or `82% +` for charging, which the home screen displays as a dynamic text value. A dynamic text value is a widget whose string is re-evaluated on the page tick — every five seconds on the home screen — and the presentation pipeline blits it only when the string changes. The battery indicator therefore costs no polling thread and no extra panel work when the value is stable.

## Verification evidence

The four features are gated by numbered probes that print deterministic evidence. All four pass on hardware.

| Probe | Feature | Evidence |
|-------|---------|----------|
| 19 | Battery | `level=100 (ok) mv=4158 charging=0 (ok) statusText="100%" legacy=match` |
| 20 | mDNS | `status=1 (ok) host=pulp (ok) url="http://pulp.local" (ok)` |
| 21 | Images | `count=3 first="65995.g4" display=0` with log `display 65995.g4: 259200 px Ok ops=1` |
| 22 | Upload callback | `cb=registered second-busy=yes` |

The `legacy=match` in probe 19 confirms that the historical `batteryLevel()` global and the new `battery.level()` return the same value, preserving backward compatibility. The `second-busy=yes` in probe 22 confirms the single-slot completion contract: registering a second callback before the first completes throws a `module busy` error.

The host test suite passes 38,186 checks, twelve more than the prior baseline. The twelve additional checks come from a new test, `TestBitmapOp`, which emits a bitmap operation with a four-pixel-wide, two-pixel-tall payload, asserts that a fully-clipped second bitmap is dropped, and asserts that the fake backend's trace contains the operation's stride and data length. This test runs under AddressSanitizer and UndefinedBehaviorSanitizer on the host before any firmware is flashed, so the emit and clip logic is verified independently of the hardware.

The end-to-end flow was verified through a browser automation harness. A landscape Wikipedia article screenshot was loaded into the upload page. The page auto-detected the landscape orientation, enabled the rotate control, and drew the image rotated 90 degrees to fill the full 540-pixel canvas width. The image was uploaded, stored on the SD card, and displayed on the panel. Vision inspection of the browser preview confirmed the image filled the canvas with no letterbox bars.

## Tricky details and failure modes

Several implementation details are not obvious from the code and are worth recording.

The httpd configuration sets `max_uri_handlers` to 2, not 1. The ESP-53 web server registered a single wildcard GET handler and set the handler count to 1. Adding a POST handler without raising this count fails silently: the POST registration succeeds, but requests return "Specified method is invalid for this resource." The count must match the number of registered URI handlers.

Inline JavaScript comments using `//` are fatal when the page script is rendered as a single line. The default upload page is a C string literal whose contents become one line of JavaScript in the rendered HTML. A `//` comment therefore comments out the remainder of the entire script, producing an "Unexpected end of input" parse error and a permanently disabled upload button. Comments inside the JavaScript string must be removed or converted to `/* */` block comments that close on the same line.

The JavaScript arena, which holds the bytecode image and runtime heap, is 192 KB. It was 160 KB before ESP-54. The gallery application and the battery surface grew the compiled `pulp.js` bytecode past the 160 KB threshold, and the engine reported `InternalError: out of memory` at boot. The raise to 192 KB is safe because the arena lives in PSRAM, which has 8 MB, and the engine's measured evaluation speed is identical in PSRAM and internal RAM.

The default upload page ships as a fallback written to `/sdcard/www/index.html` when the operator mounts the static directory. A version marker, `<!--vN-->`, in the page head lets the mount logic detect and overwrite stale previous versions of the page — including the original ESP-53 placeholder — while preserving a genuinely customized operator page that lacks the marker. Without the marker, a page written by an older firmware version would persist indefinitely and serve stale JavaScript.

## Important project docs

- Firmware directory: `/home/manuel/code/wesen/go-go-golems/esp32-s3-m5/0114-papers3-pulp-os`
- Shared core: `/home/manuel/code/wesen/go-go-golems/esp32-s3-m5/components/s3paper_core`
- M5 backend: `/home/manuel/code/wesen/go-go-golems/esp32-s3-m5/components/s3paper_m5/src/m5_backend.cpp`
- Design document and diary: docmgr ticket `ESP-54-PULP-GALLERY` under `ttmp/2026/07/27/`
- Helper scripts (`.g4` generators and decoder): the ticket's `scripts/` directory
- ESP-53 system onboarding guide (prerequisite reading): `ttmp/2026/07/16/ESP-53-PULP-CONNECTIVITY--*/design-doc/02-*.md`

## Open questions

- Should the gallery display a thumbnail grid in addition to the full-screen single view? The current design shows one image at a time; a grid would require either smaller bitmap blits or a compositing pass.
- Should the catalog be promoted to a CRC-protected state file in the s3paper_storage family, matching the discipline applied to WiFi credentials? The current plain `index.txt` rescans the directory on any inconsistency, which is correct but not O(1).
- Should the device fetch images from a URL in addition to accepting uploads? The `http.get` builder and the `images.display` path are already independent; a fetch-then-display flow would compose them with no new display code.

## Near-term next steps

- Add an EXIF orientation handler to the browser upload page so portrait phone photographs that carry rotation metadata display upright without manual intervention.
- Collapse the per-row `pushImage` calls in the rasterizer into fewer, taller blits if the measured refresh time exceeds two seconds on large images.
- Add a settings-app entry that displays the `pulp.local` URL and the image count alongside the existing WiFi and serve toggles.

## Project working rule

> [!important]
> The device never interprets a source image format. Decode, resize, and quantization belong to the browser; the device receives a finished 4-bit packed frame and performs a pure streaming copy to the SD card and a pure nibble unpack to the panel.

## Related KB entries

- [[Research/KB/Projects/esp32]] — the ESP32 project map that situates this work among the firmware, display, and connectivity projects
- [[Research/KB/Tribal/browser-side-processing-for-embedded]] — the documented pattern of pushing pixel work to the host where the host is strictly better at it
