---
title: "Almanach Studio — Image Blocks and Self-Contained Render Layouts"
aliases:
  - Almanach Studio Image Blocks
  - Almanach Image Block Upload Support
  - Self-Contained Almanach Render Layouts
  - Almanach ZIP Layout Bundles
  - Almanach Render Service May 8 Deep Dive
tags:
  - article
  - almanach
  - frontend
  - rendering
  - thermal-printer
  - chromedp
  - react
  - docmgr
  - zip-bundles
status: active
type: article
created: 2026-05-08
repo: /home/manuel/workspaces/2025-12-21/echo-base-documentation/esp32-s3-m5/stoms3r/cmd/almanach-render-service
---

# Almanach Studio — Image Blocks and Self-Contained Render Layouts

This report explains the Almanach Studio work completed on 2026-05-08. The work started with a broken local service workflow, moved through a custom analog-photography render, and became a feature implementation: Almanach layouts can now contain image blocks, and the web UI can upload an image into a layout as a data URL. The follow-up work added ZIP layout bundles, so a layout can be distributed as `layout.yaml` plus ordinary image files while the CLI still renders a self-contained data-URL layout internally. The report also covers the validation layouts created during the session, the docmgr diaries used to track the work, and the commits that record each stable slice.

The purpose of this article is not to record a list of commands. The goal is to explain how the render system works, why image blocks required changes in more than one place, and what a future maintainer must understand before extending the system further.

> [!summary]
> - Almanach Studio now has a first-class `image` block with URL input, local upload, caption, alt text, sizing, fit, border, and grayscale preview controls.
> - Uploaded files are embedded directly into saved layouts as `data:` URLs, which makes the CLI and headless renderer independent of the user's local filesystem.
> - ZIP layout bundles now provide the complementary authoring format: keep `layout.yaml` readable, store assets as separate files, and let the CLI inline relative image paths before rendering.
> - Rendering images safely required waiting for `<img>` elements in browser export paths and in the Go/chromedp screenshot path.
> - Example coverage now includes an embedded JPEG, an embedded SVG diagram, and a SQLite/sql.js animals ZIP bundle with relative ornamental image assets.

## Repository and ticket context

The implementation lives in the Almanach Render Service command directory:

```text
/home/manuel/workspaces/2025-12-21/echo-base-documentation/esp32-s3-m5/stoms3r/cmd/almanach-render-service
```

The first active ticket created for the image-block work is:

```text
ttmp/2026/05/08/ALMANACH-IMAGE-BLOCKS--add-almanach-image-blocks-and-upload-support/
```

The image-block ticket diary is:

```text
ttmp/2026/05/08/ALMANACH-IMAGE-BLOCKS--add-almanach-image-blocks-and-upload-support/reference/01-diary.md
```

The main commits from the session are:

| Commit | Message | Purpose |
|---|---|---|
| `dfff75c` | `Docs: track Almanach image block work` | Created the docmgr ticket, diary, tasks, changelog, and vocabulary entries. |
| `b33b930` | `Almanach: add image blocks with upload support` | Added the image block, upload editor, image-load waiting, and validation examples. |
| `f55c2e2` | `Diary: record Almanach image block implementation` | Recorded the implementation and validation details in docmgr. |
| `8fbf2f0` | `Almanach: add PicoCalc UF2 nerd card layout` | Added a technical Almanach layout based on the PicoCalc UF2 Loader article. |
| `d6a39e0` | `Diary: record PicoCalc UF2 nerd card layout` | Recorded the PicoCalc layout work and validation details in docmgr. |
| `5b39174` | `Docs: design Almanach ZIP layout bundles` | Created the ZIP-bundle ticket and design guide. |
| `0f2244e` | `Almanach: support ZIP layout bundles` | Added path-based layout loading, ZIP discovery, image asset inlining, and tests. |
| `16100ac` | `Docs: record Almanach ZIP bundle implementation` | Updated the ZIP-bundle ticket after implementation and validation. |
| `85cf9f0` | `Almanach: add SQLite animals ZIP bundle example` | Added the SQLite/sql.js animals bundle source directory, checked-in ZIP, and documentation updates. |

The work intentionally left local generated artifacts uncommitted. These include `.devctl/`, `.playwright-mcp/`, the locally built `almanach-render-service` binary, and temporary PNG screenshots. Those files are useful during the session but are not source artifacts.

## The starting point: the renderer already had two workflows

Before image blocks were added, Almanach already had two render workflows. The first workflow was interactive: run the Go service, open `/almanach`, edit the layout in the browser, and use the Studio controls. The second workflow was batch-oriented: pass a YAML or JSON layout to the CLI and let Chrome render it headlessly.

The important files are:

```text
README.md
Makefile
.devctl.yaml
renderer.go
web/almanach/src/almanach-studio.jsx
examples/layouts/
```

The web UI is served by the Go service at:

```text
http://localhost:8199/almanach
```

The health endpoint is:

```text
http://localhost:8199/health
```

The CLI render path is:

```bash
./almanach-render-service render \
  --layout ./examples/layouts/08-image-block.yaml \
  --out /tmp/almanach-image-block.png \
  --output yaml
```

This architecture matters because a block type is not only a React component. A block type must survive layout parsing, Studio editing, browser export, and headless screenshot capture. If one path understands the block and another path does not, the feature is incomplete.

## Recovering the local service workflow

The first task was to diagnose why `devctl` appeared broken. Running `devctl help` showed that the `devctl` binary itself was functional. The actual problem appeared when launching the Almanach service.

The first `devctl up` failure was:

```text
Error: wrapper did not report child start
```

The launch plan showed that `devctl` expected to run a local binary:

```text
/home/manuel/workspaces/2025-12-21/echo-base-documentation/esp32-s3-m5/stoms3r/cmd/almanach-render-service/almanach-render-service serve
```

That binary did not exist yet. Building it fixed the first failure:

```bash
go build -o almanach-render-service .
```

The next failure was different. The process could start, but the server exited because the port was occupied:

```text
Error: listen tcp :8199: bind: address already in use
```

`lsof -i :8199` showed an old `almanach-render-service` process still listening on the port. Killing the stale process and running `devctl down` cleared the inconsistent local supervisor state. A subsequent `devctl up` completed successfully, and the health endpoint returned:

```json
{"ok":true,"printer":"192.168.0.126","version":"dev"}
```

The stable run procedure became:

```bash
cd /home/manuel/workspaces/2025-12-21/echo-base-documentation/esp32-s3-m5/stoms3r/cmd/almanach-render-service
make build
# or: go build -o almanach-render-service .
devctl up
curl -s http://localhost:8199/health
```

The underlying lesson is simple: the `devctl` configuration supervises the binary; it does not build the binary first. A missing binary and a stale port owner can both look like supervisor failure unless the launch plan, logs, and port ownership are checked separately.

## The first custom layout exposed the missing feature

The first creative test was a layout about analog photography and large format cameras. That produced:

```text
examples/layouts/07-analog-photography.yaml
/tmp/almanach-analog-photography.png
```

The layout used existing block types: `title`, `date`, `divider`, `word`, `history`, `did`, `quote`, `reading`, and `note`. It rendered successfully:

```text
width: 384
height: 2177
bytes: 181068
artifact: /tmp/almanach-analog-photography.png
```

The limitation became visible immediately. External photos could be downloaded and displayed in a separate browser page, but there was no way to include those photos inside the Almanach layout itself. The supported block list did not include `image` or `bitmap`:

```jsx
const BLOCK_TYPES = [
  { type: "title", label: "Title", icon: Type, group: "header" },
  { type: "date", label: "Date Strip", icon: Calendar, group: "header" },
  { type: "divider", label: "Divider", icon: Minus, group: "header" },
  { type: "plan", label: "Today's Plan", icon: ListTodo, group: "daily" },
  { type: "news", label: "Top News", icon: Newspaper, group: "daily" },
  { type: "weather", label: "Weather", icon: CloudSun, group: "daily" },
  { type: "note", label: "Daily Note", icon: FileText, group: "daily" },
  { type: "habits", label: "Habit Tracker", icon: Layers, group: "tracker" },
  { type: "mood", label: "Mood & Energy", icon: Smile, group: "tracker" },
  { type: "reading", label: "Reading List", icon: BookOpen, group: "tracker" },
  { type: "reflection", label: "Daily Reflection", icon: Pencil, group: "tracker" },
  { type: "quote", label: "Quote of the Day", icon: QuoteIcon, group: "knowledge" },
  { type: "word", label: "Word of the Day", icon: BookMarked, group: "knowledge" },
  { type: "history", label: "Today in History", icon: Clock, group: "knowledge" },
  { type: "did", label: "Did You Know?", icon: Brain, group: "knowledge" },
];
```

The missing feature was not a rendering detail. It was a schema limitation. A layout could not represent an image block, so the renderer had nothing to render.

## What adding a block means in Almanach Studio

Almanach Studio keeps the block system in one large React file:

```text
web/almanach/src/almanach-studio.jsx
```

Adding a block requires updating several registries and components. The implementation must define:

1. the default shape of the block data,
2. the block metadata that makes it appear in the block library,
3. the renderer that draws it on the paper,
4. the editor that appears in the inspector,
5. the renderer registry,
6. the editor registry,
7. any export behavior required by the new DOM content.

The layout parser already provided an important mechanism. It filters imported blocks by `BLOCK_TYPES` and merges incoming data with `DEFAULTS[type]`:

```jsx
const validTypes = new Set(BLOCK_TYPES.map((b) => b.type));
const blocks = parsed.blocks
  .filter((b) => b && validTypes.has(b.type))
  .map((b) => ({
    id: b.id || uid(),
    type: b.type,
    data: b.data && typeof b.data === "object"
      ? { ...DEFAULTS[b.type], ...b.data }
      : JSON.parse(JSON.stringify(DEFAULTS[b.type])),
  }));
```

This means a new block becomes importable as soon as its type appears in `BLOCK_TYPES` and its default data appears in `DEFAULTS`. That is useful, but it also creates a failure mode: a type can become parseable before it is renderable or editable. The implementation therefore had to update all registries in the same slice.

## The image block schema

The new `image` default defines the stable data contract for layouts:

```jsx
image: {
  label: "Image Plate",
  src: "",
  alt: "Uploaded photograph",
  caption: "",
  height: 160,
  fit: "cover", // cover | contain
  border: true,
  grayscale: true,
},
```

Each field has a specific responsibility:

| Field | Purpose |
|---|---|
| `label` | Section label shown above the image. |
| `src` | Image URL or data URL. Uploaded files are stored here. |
| `alt` | Alternative text for the image element and preview. |
| `caption` | Text printed below the image. |
| `height` | Pixel height of the image area on the paper. |
| `fit` | `cover` or `contain`, passed to `object-fit`. |
| `border` | Whether to draw a rule around the image. |
| `grayscale` | Whether to apply a grayscale/contrast preview filter. |

The block metadata adds the new type to the Studio library:

```jsx
{ type: "image", label: "Image Plate", icon: ImageIcon, group: "daily" }
```

The block was placed in the `daily` group because it behaves as a content block rather than a tracker or knowledge card. That grouping is a UI decision, not a rendering requirement.

## Rendering the image block

The renderer is `ImageBlock`. It computes a bounded height, checks whether `src` is non-empty, and then renders either an `<img>` or a placeholder.

```jsx
const ImageBlock = ({ data, theme }) => {
  const height = Math.max(48, Math.min(420, Number(data.height) || 160));
  const hasImage = typeof data.src === "string" && data.src.trim().length > 0;

  return (
    <div>
      {data.label && <SectionLabel label={data.label} theme={theme} icon="▧" />}
      <div style={{
        border: data.border ? `1px solid ${theme.rule}` : "none",
        padding: data.border ? 4 : 0,
        background: theme.paper,
      }}>
        {hasImage ? (
          <img
            src={data.src}
            alt={data.alt || data.caption || "Almanach image"}
            crossOrigin={data.src.startsWith("data:") ? undefined : "anonymous"}
            style={{
              display: "block",
              width: "100%",
              height,
              objectFit: data.fit === "contain" ? "contain" : "cover",
              background: theme.paper,
              filter: data.grayscale === false ? "none" : "grayscale(100%) contrast(1.25)",
            }}
          />
        ) : (
          <div style={{
            height,
            border: `1px dashed ${theme.rule}`,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontFamily: theme.fontBody,
            fontSize: theme.fs(11),
            color: theme.muted,
            letterSpacing: "0.08em",
            textTransform: "uppercase",
          }}>
            Add an image URL or upload a file
          </div>
        )}
      </div>
      {data.caption && (
        <div style={{
          fontFamily: theme.fontBody,
          fontSize: theme.fs(10.5),
          color: theme.muted,
          textAlign: "center",
          fontStyle: "italic",
          marginTop: 5,
          lineHeight: 1.3,
        }}>
          {data.caption}
        </div>
      )}
    </div>
  );
};
```

The `height` clamp is a small but important constraint. Without it, a malformed layout could create an image with a height too small to see or tall enough to make the printed page difficult to use. The exact range, 48 to 420 pixels, is a UI constraint chosen for the current paper-width range.

The `crossOrigin` value is only set for non-`data:` sources. Data URLs are local to the document. Remote URLs may need CORS for browser-side canvas export paths. The headless Go screenshot path is less sensitive to canvas tainting because it captures the rendered page through Chrome, but the browser PNG export path clones the DOM into an SVG `foreignObject`, rasterizes it to a canvas, and then reads the canvas. Remote images can still be a correctness risk in browser-side export flows.

The grayscale option is a preview step. It does not implement true dithering. The final thermal bitmap conversion still thresholds pixels later. That distinction matters: grayscale and contrast make the on-screen preview closer to thermal output, but they do not solve photographic halftoning.

## Uploading images in the inspector

The editor is `ImageEditor`. It has a hidden file input, a visible upload button, and a `FileReader` path that stores the uploaded file directly into the layout data.

```jsx
const ImageEditor = ({ data, set }) => {
  const fileInputRef = useRef(null);

  const handleFile = async (e) => {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      set({
        ...data,
        src: String(reader.result || ""),
        alt: data.alt || file.name,
        caption: data.caption || file.name.replace(/\.[^.]+$/, ""),
      });
    };
    reader.readAsDataURL(file);
  };

  return (
    <>
      <Field label="Section Label"><TextInput value={data.label || ""} onChange={(e) => set({ ...data, label: e.target.value })} /></Field>
      <Field label="Image URL or data URL"><TextArea value={data.src || ""} onChange={(e) => set({ ...data, src: e.target.value })} placeholder="https://… or data:image/jpeg;base64,…" /></Field>
      <input ref={fileInputRef} type="file" accept="image/*" style={{ display: "none" }} onChange={handleFile} />
      <button
        type="button"
        className="btn"
        onClick={() => fileInputRef.current?.click()}
        style={{ width: "100%", justifyContent: "center", marginBottom: 12 }}
      >
        <Upload size={13} /> Upload Image
      </button>
      ...
    </>
  );
};
```

`readAsDataURL` is the key design decision. It converts the uploaded image into a string of the form:

```text
data:image/jpeg;base64,...
```

That string is stored in `data.src`. When the user exports the layout JSON, the image is part of the layout. When the CLI renders the layout later, it does not need access to the original file path. This makes saved layouts self-contained.

The cost is layout size. A full photograph can make a YAML or JSON layout large. The validation layout first embedded a 44KB JPEG and produced a 66KB YAML file. The final committed example uses a 320x190 grayscale JPEG compressed to about 6.7KB, producing an 11KB layout. This is an acceptable size for an example. For regular user uploads, future work should downscale and compress the image before storing it.

## Why image loading had to change

Adding `<img>` elements introduces asynchronous rendering. Text and CSS can be present before an image has decoded. If the screenshot happens too early, the image area can be empty. This is especially important because Almanach has three capture paths:

1. browser PNG export,
2. browser print/bitmap export,
3. Go/chromedp headless screenshot.

A correct implementation cannot update only one of those paths. The browser export path and headless render path must both wait for images.

The browser helper is:

```jsx
async function waitForImages(root = document) {
  const images = Array.from(root.querySelectorAll("img"));
  await Promise.all(images.map((img) => {
    if (img.complete) return Promise.resolve();
    return new Promise((resolve) => {
      img.addEventListener("load", resolve, { once: true });
      img.addEventListener("error", resolve, { once: true });
      setTimeout(resolve, 10000);
    });
  }));
}
```

The PNG export path now waits for images before cloning the paper node:

```jsx
async function exportPaperToPng(paperNode, fileName, scale = 2, themeObj) {
  if (!paperNode) throw new Error("No paper element");
  if (document.fonts && document.fonts.ready) await document.fonts.ready;
  await waitForImages(paperNode);

  const fontCss = await getInlineFontCss();
  ...
}
```

The same principle applies to print and bitmap export. Before the paper DOM is cloned and rasterized, the images must be either loaded or failed. The wait helper resolves on error because a failed image should not hang export indefinitely. A failed image should produce a visible missing-image outcome or placeholder behavior rather than block the whole operation.

The Go renderer has its own wait function because it drives Chrome through chromedp. The code in `renderer.go` waits for fonts, waits for images, then waits for two animation frames:

```go
func waitForFontsAndFramesJS() string {
	return `(async function() {
	if (document.fonts && document.fonts.ready) await document.fonts.ready;
	const images = Array.from(document.querySelectorAll('img'));
	await Promise.all(images.map(function(img) {
		if (img.complete && img.naturalWidth > 0) return Promise.resolve();
		return new Promise(function(resolve) {
			img.addEventListener('load', resolve, { once: true });
			img.addEventListener('error', resolve, { once: true });
			setTimeout(resolve, 10000);
		});
	}));
	await new Promise(function(resolve) { requestAnimationFrame(function() { requestAnimationFrame(resolve); }); });
})();`
}
```

The two animation frames are not a replacement for image waiting. They give the browser an opportunity to commit layout and paint after font and image readiness. Image waiting answers whether the resources are available; animation-frame waiting lets the DOM reflect that readiness before the screenshot runs.

## The headless render sequence

The Go renderer builds a Chrome action sequence. The relevant part of `renderer.go` is:

```go
actions := []chromedp.Action{
	chromedp.EmulateViewport(int64(opts.ViewportWidth), int64(opts.ViewportHeight)),
	chromedp.Navigate(opts.BaseURL + "/almanach"),
	chromedp.WaitVisible("body", chromedp.ByQuery),
	chromedp.Poll(`window.almanachReady === true`, nil, chromedp.WithPollingTimeout(10*time.Second)),
	chromedp.Evaluate(fmt.Sprintf(`window.almanachLoadLayout(JSON.parse(%s))`, layoutArg), nil),
	chromedp.Evaluate(waitForFontsAndFramesJS(), nil),
	chromedp.Sleep(opts.WaitAfterLoad),
	chromedp.Evaluate(captureJS, nil),
	chromedp.Evaluate(waitForFontsAndFramesJS(), nil),
}
```

The sequence has two waits. The first wait runs after loading the layout. The second wait runs after injecting capture CSS. This is important because capture CSS changes the page structure that Chrome screenshots. The final screenshot should reflect the final capture state, not the editable Studio view.

The image-block work did not change the fundamental render pipeline. It made the existing wait primitive complete enough for layouts that contain `<img>` elements.

The final capture then uses:

```go
chromedp.Screenshot(opts.Selector, &screenshotBuf, chromedp.ByQuery, chromedp.NodeVisible)
```

The default selector for CLI layout rendering is `.paper-body`. The screenshot bytes are then converted into a packed 1-bit bitmap by the existing bitmap pipeline.

## Validation layout: embedded JPEG

The first full validation artifact is:

```text
examples/layouts/08-image-block.yaml
/tmp/almanach-image-block.png
```

The layout embeds a small grayscale JPEG directly in YAML:

```yaml
- id: image-large-format
  type: image
  data:
    label: Large Format Study
    src: >-
      data:image/jpeg;base64,...
    alt: Person adjusting a vintage large format camera on a tripod
    caption: "A view camera rewards slowness: ground glass, bellows, dark cloth, breath."
    height: 190
    fit: cover
    border: true
    grayscale: true
```

The render command was:

```bash
./almanach-render-service render \
  --layout ./examples/layouts/08-image-block.yaml \
  --out /tmp/almanach-image-block.png \
  --output yaml
```

The output was:

```text
artifact: /tmp/almanach-image-block.png
bytes: 96841
format: png
height: 940
selector: .paper-body
threshold: 128
width: 384
```

The image was inspected with the image-capable `read` tool. The result showed the title, date strip, image plate, embedded photograph, caption, exposure note, divider, and validation bullets. This confirmed that the data URL survived YAML parsing, React rendering, Chrome loading, screenshot capture, and PNG output.

Two practical YAML issues appeared during this validation. First, unquoted text fields containing colons produced parse errors:

```text
yaml: line 619: mapping values are not allowed in this context
```

Second, very large base64 payloads made the example noisy. The fix was to downscale and grayscale the source image before embedding it. The source command used ImageMagick:

```bash
convert /tmp/almanach-photos/photo1.jpg \
  -resize 320x190^ \
  -gravity center \
  -extent 320x190 \
  -colorspace Gray \
  -quality 55 \
  /tmp/almanach-photos/photo-small.jpg
```

This produced a small image that still validated the feature.

## Validation layout: embedded SVG diagram

The second image-block validation happened through a more technical layout:

```text
examples/layouts/09-picocalc-uf2-nerd-card.yaml
/tmp/almanach-picocalc-uf2.png
```

The source material was the Obsidian article:

```text
/home/manuel/code/wesen/obsidian-vault/Projects/2026/05/05/ARTICLE - PicoCalc UF2 Loader - Two-Stage Bootloader Deep Dive.md
```

The resulting Almanach layout summarizes the PicoCalc UF2 Loader boot process. It includes an embedded SVG diagram as an `image` block. The diagram was hand-authored as SVG, base64-encoded, and placed in `src` as a `data:image/svg+xml;base64,...` URL.

The diagram content is a small state sequence:

```text
RESET -> KEY? -> APP
           |
           v
      BOOT2040.UF2 -> APP
```

The SVG is black-on-white line art with monospace labels. That choice was deliberate because the final output is narrow and monochrome. Fine color information would not survive the thermal-style pipeline. Text and simple rules are easier to preserve.

The layout render command was:

```bash
./almanach-render-service render \
  --layout ./examples/layouts/09-picocalc-uf2-nerd-card.yaml \
  --out /tmp/almanach-picocalc-uf2.png \
  --output yaml
```

The final output was:

```text
artifact: /tmp/almanach-picocalc-uf2.png
bytes: 151228
format: png
height: 1968
selector: .paper-body
threshold: 128
width: 384
```

This validated that the image block supports both raster data URLs and SVG data URLs. It also exposed a content-design issue with existing block semantics: `plan` rows with `done: true` are drawn as checked and struck-through. That behavior is correct for a task list but wrong for an explanatory decision tree. The fix was to set `done: false` for all decision-tree rows. The later design conclusion is that a separate non-strikethrough `steps` block may be useful.

## How the SVG diagram was generated

The SVG diagram was created by hand as a string, then encoded with Python:

```python
import base64, textwrap

svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="640" height="300" viewBox="0 0 640 300">
  <rect width="640" height="300" fill="white"/>
  <style>
    text{font-family:monospace;font-size:24px;fill:#000}
    .small{font-size:18px}
    .tiny{font-size:16px}
    .box{fill:#fff;stroke:#000;stroke-width:4}
    .arrow{stroke:#000;stroke-width:4;fill:none;marker-end:url(#a)}
  </style>
  ...
</svg>'''

data_url = "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()
wrapped = "\n".join("        " + line for line in textwrap.wrap(data_url, 100))
print(wrapped)
```

The wrapped output was inserted into YAML under `src: >-`. Wrapping is not required by the renderer, but it keeps long data URLs from producing a single very wide line in source control.

A byte-level problem appeared during one replacement attempt:

```text
yaml: control characters are not allowed
```

The cause was a bad regex replacement that inserted a control byte before the `alt:` key. The repair replaced the bad byte with a normal YAML key line. This is a reminder that generated data URLs are ordinary text, but a malformed edit can still create invalid YAML.

## ZIP layout bundles: readable layouts with separate image assets

The data-URL design is correct for saved browser uploads and for headless rendering. It makes a layout independent of local file paths and network requests at render time. The drawback appears when a layout is meant to be edited by humans or reviewed in source control: base64-encoded image payloads dominate the YAML file.

The follow-up implementation added ZIP layout bundle support to preserve the same runtime property while improving the authoring format. A bundle can now contain a normal layout file plus separate image assets:

```text
layout.zip
├── layout.yaml
└── images/
    ├── fox.png
    ├── owl.png
    └── hedgehog.png
```

The layout can refer to those assets by relative path:

```yaml
blocks:
  - id: fox
    type: image
    data:
      src: images/fox.png
      height: 56
      fit: contain
      border: false
```

The browser renderer does not receive a new asset protocol. Instead, the CLI loader rewrites relative `image.data.src` values to `data:` URLs before the layout JSON is passed to Chrome. This preserves the original image-block contract: by the time rendering begins, every local image asset needed by the page is inside the layout data.

The implementation lives in:

```text
layout_bundle.go
layout_bundle_test.go
cmd_render.go
cmd_inspect.go
cmd_print.go
```

The command-line flag stays the same. The meaning of `--layout` becomes broader:

```bash
./almanach-render-service render --layout daily.yaml --out daily.png
./almanach-render-service render --layout layout-bundle.zip --out daily.png
./almanach-render-service inspect --layout layout-bundle.zip --output yaml
./almanach-render-service print --layout layout-bundle.zip --dry-run --output yaml
```

The loader handles three cases:

1. no layout path: use the default generated layout,
2. standalone YAML or JSON file: parse it directly,
3. ZIP file: find the layout member, parse it, rewrite relative image sources, and then use the same normalization path as standalone files.

The ZIP loader does not extract files to disk. It opens the archive with Go's `archive/zip`, reads members in memory, and rejects path traversal-style names. A relative source such as `images/fox.png` is resolved against the layout member directory, read from the archive, assigned a MIME type, base64 encoded, and replaced with a data URL:

```text
images/fox.png
  -> data:image/png;base64,...
```

Already self-contained or remote sources are left unchanged:

```text
data:image/png;base64,...
https://example.com/image.png
http://example.com/image.png
```

The design choice is deliberately conservative. ZIP support is a CLI input format, not a new renderer capability. Chrome still sees ordinary HTML with ordinary `<img src="data:...">` elements, and the image-load waiting added for image blocks continues to apply.

## Validation layout: SQLite/sql.js animals ZIP bundle

The first realistic bundle example is the SQLite/sql.js performance card:

```text
examples/bundles/10-sqlite-browser-animals/
examples/bundles/10-sqlite-browser-animals.zip
```

The source directory contains:

```text
README.md
layout.yaml
images/fox.png
images/owl.png
images/snake.png
images/hedgehog.png
images/fish.png
```

This layout is based on the browser SQLite/sql.js performance article and uses the extracted animal banners as ornamental separators. The important difference from the earlier draft is file shape. The base64 YAML draft was roughly 77 KB and hard to review. The ZIP source layout is a normal YAML file of about 5 KB, and the image assets remain ordinary PNG files.

The checked-in ZIP rendered successfully with:

```bash
./almanach-render-service render \
  --layout ./examples/bundles/10-sqlite-browser-animals.zip \
  --out /tmp/almanach-sqlite-animals-zip-example.png \
  --output yaml
```

The observed output was:

```text
width: 384
height: 2237
bytes: 208752
artifact: /tmp/almanach-sqlite-animals-zip-example.png
```

The same bundle was also validated through `inspect` and `print --dry-run`, which matters because all three commands now share the path-based layout loader.

## Documentation workflow

The user requested that work be committed at appropriate intervals and that docmgr be used to keep a diary. The ticket `ALMANACH-IMAGE-BLOCKS` was created for the image-block work, and `ALMANACH-ZIP-BUNDLES` was created for the follow-up ZIP bundle implementation.

The diary structure records:

- the exact user prompt that started each step,
- what was changed,
- why it was changed,
- commands that worked,
- commands or renders that failed,
- tricky implementation details,
- review instructions,
- follow-up work.

The docmgr commands used included:

```bash
docmgr ticket create-ticket \
  --ticket ALMANACH-IMAGE-BLOCKS \
  --title "Add Almanach image blocks and upload support" \
  --topics almanach,frontend,rendering


docmgr doc add \
  --ticket ALMANACH-IMAGE-BLOCKS \
  --doc-type reference \
  --title "Diary"
```

The ticket initially failed docmgr doctor because the topics were not in the vocabulary. The missing topics were added:

```bash
docmgr vocab add --category topics --slug almanach --description "Almanach Render Service and Studio layout/rendering workflow"
docmgr vocab add --category topics --slug frontend --description "Frontend UI implementation and browser interaction"
docmgr vocab add --category topics --slug rendering --description "Image/page rendering, screenshot capture, and output conversion"
```

After that, doctor passed:

```text
## Doctor Report (1 findings)

### ALMANACH-IMAGE-BLOCKS

- ✅ All checks passed
```

This documentation step is part of the implementation quality. It makes the work resumable. It also records why generated artifacts were not committed, why examples were chosen, and which validation outputs were inspected.

## The implementation sequence

The implementation sequence is useful because it shows the dependencies between changes. The order was:

1. Restore the local web UI and service workflow.
2. Create a text-only analog photography layout to exercise the existing render path.
3. Confirm that image blocks were not supported.
4. Add the image block schema and block registration.
5. Add the image renderer.
6. Add the image editor and upload path.
7. Add image-load waiting in browser export paths.
8. Add image-load waiting in the Go/chromedp render path.
9. Build the frontend and run Go tests.
10. Create an embedded JPEG validation layout.
11. Render and inspect the validation PNG.
12. Commit the code and examples.
13. Create the PicoCalc UF2 nerd-card layout with an embedded SVG diagram.
14. Render and inspect the second validation PNG.
15. Commit the second example and update the diary.
16. Create the `ALMANACH-ZIP-BUNDLES` docmgr ticket and design guide.
17. Implement path-based layout loading and ZIP bundle parsing.
18. Add unit tests for standalone and ZIP layout loading.
19. Validate render, inspect, and print dry-run against a real ZIP bundle.
20. Convert the SQLite/sql.js animals layout into a ZIP-backed example and commit it.

The sequence matters because the browser UI and CLI renderer share the same layout data but not the same export mechanics. It is possible to make an image appear in the Studio canvas while still failing in CLI render. The validation had to include the CLI path.

## Validation commands

The main validation commands were:

```bash
go test ./...
```

```bash
cd web/almanach
npm run build
```

```bash
./almanach-render-service render \
  --layout ./examples/layouts/08-image-block.yaml \
  --out /tmp/almanach-image-block.png \
  --output yaml
```

```bash
./almanach-render-service render \
  --layout ./examples/layouts/09-picocalc-uf2-nerd-card.yaml \
  --out /tmp/almanach-picocalc-uf2.png \
  --output yaml
```

```bash
./almanach-render-service render \
  --layout ./examples/bundles/10-sqlite-browser-animals.zip \
  --out /tmp/almanach-sqlite-animals-zip-example.png \
  --output yaml
```

```bash
./almanach-render-service inspect \
  --layout ./examples/bundles/10-sqlite-browser-animals.zip \
  --output yaml
```

```bash
./almanach-render-service print \
  --layout ./examples/bundles/10-sqlite-browser-animals.zip \
  --dry-run \
  --output yaml
```

The images were inspected directly through the tool environment rather than only through the browser. This was useful because it validated the actual output file produced by the CLI renderer.

## Failure modes encountered

The session produced several concrete failure modes worth preserving.

### Missing supervised binary

`devctl up` failed when the binary did not exist:

```text
Error: wrapper did not report child start
```

The fix was to build the binary:

```bash
go build -o almanach-render-service .
```

### Stale port owner

After the binary existed, the service still failed:

```text
Error: listen tcp :8199: bind: address already in use
```

The fix was to find and kill the stale process, then clear devctl state:

```bash
lsof -i :8199
kill <pid>
devctl down
devctl up
```

### Direct image downloads returning non-images

Some direct image URLs returned HTML or XML instead of JPEG data. The session used Playwright to inspect an actual search results page, extract current image URLs, and fetch the image data in-browser. This was more reliable than guessing static CDN paths.

### YAML colon parsing

Technical prose often contains colons. In YAML, unquoted text after a key can become invalid if it contains a colon in the wrong position. The observed error was:

```text
yaml: mapping values are not allowed in this context
```

The fix was to quote those fields:

```yaml
text: "No key: set VTOR, set MSP, branch to installed app reset vector."
```

### Strikethrough semantics in `plan`

The `plan` block renders `done: true` as checked and struck-through. That is correct for task completion. It is incorrect for explanatory sequences. Decision-tree rows should use `done: false` until a separate step-list block exists.

### Data URL size

Large uploaded images make layouts large. The committed validation image was downscaled and compressed before being embedded. A future production upload path should do this automatically.

## What the system can do now

A user can now do the following in Almanach Studio:

1. Open the web UI at `http://localhost:8199/almanach`.
2. Add an `Image Plate` block.
3. Paste an image URL or upload a local image file.
4. Add caption and alt text.
5. Choose height and `cover` or `contain` fit.
6. Save the layout JSON.
7. Render the saved layout through the CLI without the original image file.

The saved layout contains the uploaded image as a data URL. That is the central browser-facing behavior. It turns uploaded local files into portable layout data.

A CLI user can also render a ZIP layout bundle. In that workflow, the editable source remains a layout file plus separate image files, while the CLI converts those relative assets into data URLs before rendering. This is the central source-control-facing behavior: review readable YAML, keep binary assets as binary assets, and still render without extracting files to disk.

The CLI can also render layouts with embedded raster or SVG data URLs. The two committed examples demonstrate both:

```text
examples/layouts/08-image-block.yaml          # embedded JPEG
examples/layouts/09-picocalc-uf2-nerd-card.yaml # embedded SVG
examples/bundles/10-sqlite-browser-animals.zip # ZIP bundle with relative PNG assets
```

## What is not implemented yet

The image block is useful, but it is not the final form of image support.

### There is no upload-time downscaling

The current upload path stores the file exactly as the browser reads it. If the user uploads a multi-megabyte photo, the layout becomes large. The next version should downscale and compress images before storing them in `src`.

A reasonable browser-side algorithm is:

```text
on image file selected:
  decode file into ImageBitmap or HTMLImageElement
  compute target width from paper width and block padding
  compute target height from requested image height
  draw image to canvas at target dimensions
  convert canvas to JPEG or PNG data URL
  store compressed data URL in block.data.src
```

The target dimensions should be based on the paper width, not the original image dimensions. For thermal output, preserving a 3000-pixel-wide photo is not useful when the final paper width is 384 pixels.

### There is no true dithering

The current image block uses CSS grayscale and contrast filters:

```jsx
filter: data.grayscale === false ? "none" : "grayscale(100%) contrast(1.25)"
```

The final bitmap converter still thresholds pixels. This can lose midtone detail in photographs. A better thermal-photo pipeline would add ordered dithering or error-diffusion dithering before packing the bitmap.

A simple ordered dithering path would look like this:

```text
for each pixel (x, y):
  gray = luminance(pixel)
  threshold = bayerMatrix[y mod n][x mod n]
  output = gray < threshold ? black : white
```

A Floyd-Steinberg path would propagate quantization error:

```text
for each pixel left-to-right, top-to-bottom:
  old = gray[x,y]
  new = old < 128 ? 0 : 255
  error = old - new
  gray[x+1,y]   += error * 7/16
  gray[x-1,y+1] += error * 3/16
  gray[x,y+1]   += error * 5/16
  gray[x+1,y+1] += error * 1/16
```

Dithering should probably live in the bitmap conversion pipeline rather than only in the React component. That would make printed output consistent across all layouts.

### There is no dedicated diagram block

The PicoCalc layout embedded an SVG diagram through the image block. That works, but YAML with base64 SVG is hard to edit by hand. ZIP bundles now provide one practical answer for raster and SVG asset files: keep the SVG as a separate member and reference it by path. A dedicated `diagram` or `code` block may still be useful if technical cards become common, because a separate SVG file still has to be authored somewhere.

A `diagram` block could accept raw SVG, Mermaid text, or a small structured graph description. Each option has tradeoffs. Raw SVG is precise. Mermaid is readable but requires rendering support. A structured graph description can be validated but requires a custom renderer.

### There is no non-strikethrough steps block

The `plan` block can express ordered rows with a left-side time label, but it is semantically tied to completion. A technical layout often needs sequence rows that are not tasks. A separate `steps` block could avoid checkbox and strikethrough behavior.

## Recommended next implementation steps

The next useful work should focus on image quality and layout authoring ergonomics.

1. Add upload-time resizing and compression in `ImageEditor`.
2. Add explicit image-load failure UI so broken URLs are visible before export.
3. Add a layout parser test for `type: image` to protect schema compatibility.
4. Add dithering to the bitmap conversion pipeline and expose a render option for threshold-only versus dithered output.
5. Add a browser-side import/export workflow for ZIP bundles if Studio should edit multi-file layouts directly.
6. Consider a `steps` block for explanatory sequences.
7. Consider a `diagram` or `code` block for technical cards.

The most important next step is upload-time resizing. It reduces layout size and makes saved JSON/YAML easier to review. Dithering is the most important print-quality improvement.

## Review guide

A reviewer should start with the source commit:

```text
b33b9301297ad35e06387447ca21f29627367006
```

Review these files first:

```text
web/almanach/src/almanach-studio.jsx
renderer.go
examples/layouts/08-image-block.yaml
examples/layouts/09-picocalc-uf2-nerd-card.yaml
examples/bundles/10-sqlite-browser-animals/layout.yaml
examples/bundles/10-sqlite-browser-animals.zip
```

In `almanach-studio.jsx`, review these symbols:

```text
DEFAULTS.image
BLOCK_TYPES entry for image
ImageBlock
ImageEditor
waitForImages
RENDERERS.image
EDITORS.image
```

In `renderer.go`, review:

```text
waitForFontsAndFramesJS
```

Then run:

```bash
go test ./...
cd web/almanach && npm run build
```

Then render the validation layouts and bundle:

```bash
./almanach-render-service render \
  --layout ./examples/layouts/08-image-block.yaml \
  --out /tmp/almanach-image-block.png \
  --output yaml

./almanach-render-service render \
  --layout ./examples/layouts/09-picocalc-uf2-nerd-card.yaml \
  --out /tmp/almanach-picocalc-uf2.png \
  --output yaml

./almanach-render-service render \
  --layout ./examples/bundles/10-sqlite-browser-animals.zip \
  --out /tmp/almanach-sqlite-animals-zip.png \
  --output yaml
```

Inspect the PNG files. The first should show a large-format camera photo inside the paper. The second should show a boot-flow SVG diagram near the top and readable technical sections below it. The third should show the SQLite/sql.js performance card with animal-banner separators loaded from the ZIP bundle.

## Closing

The session changed Almanach Studio from a text-only layout editor into a layout editor that can carry its own image assets. The follow-up ZIP work extended that design from browser-saved self-contained layouts to source-control-friendly multi-file bundles. The core implementation is small, but it crosses the important boundaries in the system: schema, editor, renderer, browser export, headless screenshot, CLI layout loading, examples, validation, and documentation.

The central design rule is now explicit: a layout that contains an uploaded image should be self-contained by render time. The user should be able to save the layout, send it through the CLI renderer, and reproduce the page without the original file path or a network fetch. Data URLs implement that rule directly. ZIP bundles implement it as a loading step: relative files are converted into data URLs before Chrome sees the document. The next improvements should preserve this rule while reducing layout size, improving 1-bit photographic output, and making multi-file authoring pleasant in the browser UI.

## Related notes

- [[ARTICLE - PicoCalc UF2 Loader - Two-Stage Bootloader Deep Dive]]
- [[ARTICLE - Almanach Render Service - YAML CLI Rendering and Reliable Thermal Printing]]
