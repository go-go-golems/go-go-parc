---
title: "Collage Editor - From YAML Composition to Interactive Browser Rendering"
aliases:
  - Collage DSL
  - Collage Editor
  - YAML Collage Composition
tags:
  - article
  - collage
  - yaml
  - go
  - browser
  - rendering
  - design-system
  - dsl
status: active
type: article
created: 2026-06-09
repo: /home/manuel/code/wesen/collage
---

# Collage Editor: From YAML Composition to Interactive Browser Rendering

This article documents the design and implementation of a collage composition system: a YAML-based DSL for defining layered PNG compositions, a Go CLI renderer backed by ImageMagick, and a browser-based editor that renders the same compositions interactively in the DOM. The project evolved from simple asset catalogs through a structured DSL with semantic placement grammar to a full interactive editor where layers move in real time without server round-trips.

The architecture makes a deliberate choice about where intelligence lives: the YAML file is the art-direction document, the Go backend is the source of truth for geometry resolution, and the browser editor is a presentation layer that mirrors the resolution logic without duplicating it.

> [!summary]
> - YAML is the art-direction language, not a code format. Every field serves composition intent.
> - Semantic placement (guide-based, POI-based) replaced pixel coordinates as the primary positioning model.
> - Browser rendering with individual `<img>` elements replaced ImageMagick previews for interactive editing.
> - Catalog POIs are vetted metadata, not inferred at render time.

## The Core Problem

Collage composition is hard because you are juggling multiple concerns simultaneously. You need to specify where each image goes, how large it should be, what transforms to apply, how layers relate to each other, and what the overall composition should communicate. Doing this with raw pixel coordinates works for simple cases but breaks down as compositions grow in complexity. You end up manually calculating offsets, adjusting percentages, and second-guessing whether a layer should be at `x: 325, y: 300` or `x_pct: 32.5`.

The solution is to separate positioning concerns from absolute coordinates. Instead of saying "place this image at pixel coordinates (325, 300)", you say "place this image's feet on the ground line." Instead of "scale this to 200px wide", you say "scale this to 22% of the canvas width." The system computes the actual coordinates. This is semantic placement.

## The YAML Composition DSL

The foundation is a YAML document that describes a collage. A collage is a stack of layers painted bottom-to-top onto a fixed-size canvas. Each layer places one PNG image with optional transforms. The browser editor renders each layer as an individual positioned `<img>` element inside a relative container, with an SVG overlay for bounding boxes, guides, and POI markers.

![The browser editor showing the "Intent Astronaut Portal" composition. Six layer images render as positioned `<img>` elements on a white canvas, with cyan bounding boxes and guide crosshairs overlaid as SVG. The right panel shows the layer list and inspector.](screenshot-full.png)

The YAML document below is a real composition file. Notice how every layer has a `description` that explains its role:

```yaml
title: "Intent Astronaut Portal"
canvas:
  width: 1000
  height: 1000
  background: white
layers:
  - id: astronaut
    description: >
      The astronaut is the hero. Its catalog point `feet_center` is placed
      on the ground line, making the figure independent of source resolution.
    image: classical-thumbs/19.png
    catalog_id: classical-19-astronaut
    fit_height_pct: 0.50
    place:
      point: feet_center
      at:
        guide: ground_center
```

The DSL has five families of fields:

**Identity and intent.** `id`, `description`, `label`, `note`. These are human-readable. `id` is machine-addressable; the rest describe why this layer exists in the composition.

**Source specification.** `image` (relative path to PNG), `catalog_id` (pointer to a catalog metadata entry).

**Composition-relative sizing.** `width_px`, `height_px`, `fit_width_pct`, `fit_height_pct`, `fit_pct`. These are relative to canvas dimensions, not source image dimensions. `fit_pct: 0.50` means "this layer should be 50% of the longest canvas dimension, preserving aspect ratio."

**Positioning.** Legacy `x`, `y`, `pct_x`, `pct_y`, `position` keywords. These still work but are superseded by semantic placement.

**Semantic placement grammar.** `place: { point, at, offset }`. This is the primary positioning model in new compositions.

### Composition-relative sizing

Composition-relative sizing was the first major design decision. Instead of fixing layer dimensions in source pixels (which varies by asset) or canvas pixels (which requires recalculating when canvas size changes), sizing is expressed as a fraction of the canvas.

```go
func resolveTargetSize(l dsl.Layer, imagePath string, canvas dsl.Canvas) (float64, float64) {
    srcW, srcH := getImageDimensions(imagePath)
    w, h := float64(srcW), float64(srcH)

    if l.FitPct != nil {
        target := *l.FitPct * float64(max(canvas.Width, canvas.Height))
        if w >= h {
            return target, h * target / w
        }
        return w * target / h, target
    }
    // ... fit_width_pct, fit_height_pct, width_px, height_px
    return w, h
}
```

A layer with `fit_height_pct: 0.50` on a 1000-pixel-tall canvas will always be 500 pixels tall, regardless of the source image size. This is the key insight: sizing is relative to the composition context, not the asset.

### Semantic placement grammar

Semantic placement is a three-level grammar. A `place` block has:

- `point`: which point on this layer to anchor (e.g., `feet_center`, `center`, or a custom POI name from a catalog)
- `at`: where to place that point (a guide point, a coordinate, or another layer's point)
- `offset`: a small adjustment in pixels or percentage

```yaml
place:
  description: "Nudge the spark away from the astronaut's face."
  point: center
  at_layer:
    id: astronaut
    point: head_center
  offset:
    x_pct: 0.20
    y_pct: -0.03
```

The resolution pipeline processes these in order:
1. Resolve `at` to a destination point (canvas coordinate or layer-relative point)
2. Resolve `point` to a source offset within the layer's bounding box
3. Compute final position: `destination - source_offset + offset`

This means placement is invariant to canvas size changes. Move the ground guide from `y_pct: 0.80` to `y_pct: 0.70`, and every layer placed relative to it shifts automatically.

#### Guide points

Guide points are named anchors in the composition. They live under `guides.points` and can be absolute pixels or canvas-relative fractions.

```yaml
guides:
  points:
    upper_center:
      x_pct: 0.50
      y_pct: 0.24
      offset:
        y_pct: -0.02  # optical correction
    ground_center:
      x_pct: 0.50
      y_pct: 0.80
```

Guide offsets allow small adjustments that account for visual perception. The `upper_center` guide has a negative `y_pct` offset because optically, placing something exactly at 24% down the canvas feels too low — the correction shifts it up by 2% of the canvas height.

#### Catalog POIs

Catalog POIs (Points of Interest) are vetted metadata on assets. A catalog is a JSON file that describes reusable collage assets with properties like `title`, `description`, `tags`, and most importantly `points_of_interest`.

```json
{
  "id": "classical-19-astronaut",
  "filename": "classical-thumbs/19.png",
  "points_of_interest": {
    "head_center": { "x_pct": 0.50, "y_pct": 0.08 },
    "chest_center": { "x_pct": 0.50, "y_pct": 0.42 },
    "feet_center": { "x_pct": 0.50, "y_pct": 0.98 }
  }
}
```

These are not inferred from image analysis. They are hand-placed metadata that define semantic points on an asset. When a layer references `catalog_id`, the placement grammar can use any POI name as the `point` value. The system looks up the POI in the catalog and gets its `x_pct`/`y_pct`, then computes the layer's position relative to that point.

This means you can say "place the astronaut's feet on the ground line" and the system looks up where the feet are in the source image, then positions the layer accordingly. The layer moves correctly even if the source image dimensions change or if you swap to a different astronaut image with different proportions.

![Layer inspector showing the astronaut layer's resolved position (x: 325, y: 300), sizing (700x1000px), catalog ID, and the semantic placement grammar used to position it.](screenshot-inspector.png)

### Layer repeat patterns

A layer can define a `repeat` block to stamp multiple copies with offsets:

```yaml
- image: Stickers/s1.png
  anchor: center
  repeat:
    count: 4
    dx: 200
    dy: 0
```

The resolver expands this into four `ResolvedLayer` entries, each with its own `x`, `y`, and optional incremental rotation. This is useful for patterns like orbital rings, border decorations, and repeated elements.

## The Go CLI Renderer

The CLI is the source of truth for rendering. It parses the YAML, resolves all layers, and composites them into a PNG using ImageMagick.

The renderer does not produce one giant `convert` command. Instead, it renders each layer separately with its transforms applied, then composites each transformed layer onto the canvas using `composite`. This per-layer pipeline is simpler and more debuggable than building one massive ImageMagick command.

```go
func Render(c *dsl.Collage, layers []ResolvedLayer, outputPath string, canvasScale float64) error {
    // Create transparent canvas
    w := int(math.Round(float64(c.Canvas.Width) * canvasScale))
    h := int(math.Round(float64(c.Canvas.Height) * canvasScale))
    canvasArgs := []string{"-size", fmt.Sprintf("%dx%d", w, h), "xc:" + bg, outputPath}
    
    for _, l := range layers {
        tmpLayer := fmt.Sprintf("/tmp/collage-layer-%d.png", l.Index)
        // Transform: resize, flip, rotate
        // Write to tmpLayer
        // Composite tmpLayer onto canvasPath at computed position
    }
}
```

Each layer pipeline is:
1. Apply `resize` for scaling (capped to prevent cache exhaustion)
2. Apply `flop`/`flip` for mirroring
3. Apply `rotate` with transparent background
4. Write transformed layer to temp PNG
5. Read back temp PNG dimensions for anchor offset calculation
6. Composite onto canvas using `composite -gravity None -geometry +X+Y`

The anchor offset calculation is critical. When a layer has `anchor: center`, the `x` and `y` coordinates refer to the center of the layer, not its top-left corner. The composite command uses top-left coordinates, so the renderer converts: `composite_x = layer_x - layer_width / 2`.

### Preview scaling

The CLI supports a `--preview` flag that renders at a fraction of full resolution. `--preview 0.25` renders at 25% scale. This enables fast iteration: edit the YAML, render a preview, check composition, iterate. When satisfied, remove the flag for full-resolution output.

```bash
collage render --input examples/22-intent-astronaut-poi.yaml --preview 0.25 --out preview.png
```

### POI debug overlay

The `poi-debug` command renders an asset image with colored markers at each POI location. This validates that catalog POIs are placed correctly relative to the source image content.

```bash
collage poi-debug --catalog catalogs/demo-poi-catalog.json --image classical-19-astronaut --max-dim 1000
```

This renders the astronaut image with circles at `head_center`, `chest_center`, and `feet_center`, each labeled with its POI name.

## The Browser Editor

The browser editor was built on a different set of requirements than the CLI. The CLI is for final output and batch processing. The editor is for iterative exploration: drag layers around, see immediate visual feedback, adjust placement without re-rendering through ImageMagick.

### Architecture decision: two render paths

The project has two render paths, each optimized for its use case:

| | CLI Renderer | Browser Editor |
|---|---|---|
| **Output** | Single PNG via ImageMagick | Individual `<img>` elements in DOM |
| **Speed** | 1-2 seconds per render | Instant (layer images load in parallel) |
| **Purpose** | Final export, batch processing | Interactive editing, exploration |
| **Fidelity** | Full ImageMagick pipeline | Browser-native rendering |

The initial implementation used a single path: the browser editor called the backend's ImageMagick render after every position change. This created a 500ms+ delay after each drag. The rendering was technically correct, but the user experience was terrible — you'd drag a layer and watch it snap back to its original position while ImageMagick chugged along.

### Browser rendering with individual layer images

The fix was to render each layer as an individual positioned `<img>` element instead of a single pre-rendered bitmap. The HTML structure is:

```html
<div class="canvas-wrapper">  <!-- 1000x1000, relative positioning -->
  <img src="layer1.png" style="left: 0px; top: 0px; width: 200px;">
  <img src="layer2.png" style="left: 325px; top: 300px; width: 350px;">
  <svg> <!-- SVG overlay for bounding boxes, guides, POI markers -->
    <g><rect>...</rect><text>Layer 0</text></g>
    <g><rect>...</rect><text>Layer 1</text></g>
  </svg>
</div>
```

Each layer `<img>` has:
- `src` pointing to `/api/assets/file?path=<resolved_image_path>`
- `style.left` and `style.top` set to the resolved position
- `style.width` and `style.height` set to the resolved dimensions
- `data-layer-index` for identification
- `pointer-events: none` so the SVG overlay handles interaction

Rotation and flip are applied via CSS `transform` (rotation uses `rotate(deg)`, flip uses `scale(-1, 1)` or `scale(1, -1)`).

### Drag interaction model

Drag works by moving the `<img>` element directly, not by re-rendering the canvas. The event flow:

```
mousedown on SVG layer group
  → onLayerSelect(index)  // update state, render inspector (not canvas)
  → start drag tracking (store clientX/clientY)
  → add document mousemove listener
    → on mousemove:
      → delta = clientX - startX
      → layerImg.style.left = currentLeft + movementX
      → rect.setAttribute('x', currentX + movementX)
      → callbacks.onLayerDrag(index, cDx, cDy)
        → applyLayerOffset(index, deltaX, deltaY)  // modify YAML structure
```

Key insight: `onLayerSelect` does not call `renderCanvas` when triggered from the canvas. It only updates the inspector panel. If it did re-render the canvas, it would destroy the SVG DOM while the mousedown handler is still executing, and the drag's `document.addEventListener('mousemove', ...)` would fire on detached elements.

The `onLayerDrag` callback updates the in-memory collage structure (`place.offset.x_pct`, `place.offset.y_pct`) and the inspector. It does not call the backend. The browser renders are already live via the positioned `<img>` elements.

### Export button

When the user clicks "Export", the editor serializes the in-memory collage object to YAML via `POST /api/serialize`, then sends it to `POST /api/render/preview` with the YAML override. The backend parses the YAML and runs ImageMagick. This is the only backend render call — everything else is browser-native.

### Safe path resolution

The editor serves files through a Go HTTP server. The `SafeResolve` function prevents directory traversal attacks:

```go
func SafeResolve(root, path string) (string, error) {
    joined := filepath.Join(root, path)
    abs, _ := filepath.Abs(joined)
    if !strings.HasPrefix(abs, root) {
        return "", fmt.Errorf("path escapes root: %s", path)
    }
    return abs, nil
}
```

Critical edge case: `filepath.Join(root, "/etc/passwd")` returns `/etc/passwd` on Unix (the leading `/` makes it absolute), which does NOT have the `root` prefix. This is correctly rejected.

For asset serving, the handler allows absolute paths under the server root or the temp directory (where cached previews live). This was necessary because the resolved layer images have absolute paths from the resolver.

### Catalog loading

Catalog paths in the YAML are relative to the YAML file, not the server root. The frontend must prepend the YAML file's directory:

```typescript
const yamlDir = state.project.path.includes('/')
  ? state.project.path.substring(0, state.project.path.lastIndexOf('/'))
  : '';
const catalogUrl = yamlDir ? yamlDir + '/' + c : c;
```

This was a bug discovered during implementation — the first version passed catalog paths directly to the API, which resolved them from the server root, causing 404s.

## Design Decisions

### Why YAML, not JSON

YAML supports multi-line strings with `>` folding, making it natural to write descriptions that explain composition intent. The `description` field on every layer, guide, and placement block is not optional metadata — it is the art-direction document. JSON would require escaping newlines and quotes, making the same content awkward.

### Why not JSON-only serialization

The backend accepts a `collage` JSON object in `POST /api/serialize` and marshals it back to YAML. This round-trip preserves the intent-rich structure while allowing the frontend to work with JSON (its native format). The round-trip is lossy in one direction (JSON → YAML → JSON might reorder fields), but never lossy in the semantic sense: all placement data, offsets, and POI references survive intact.

### Why individual layer images instead of a single composite

A single pre-rendered bitmap has one advantage: pixel-perfect ImageMagick fidelity. A composite of individual `<img>` elements has two advantages: instant rendering and composability. Individual elements can be rotated, flipped, or repositioned in the browser without server round-trips. They can also be combined with CSS effects (opacity, filters) that the browser handles natively.

The tradeoff is that browser rendering may not exactly match ImageMagick output for complex blend modes or specific resize algorithms. For most collage compositions, the difference is negligible. The editor is for exploration and iteration; the CLI is for final output.

### Why catalog POIs are vetted, not inferred

Catalog POIs are manually placed points of interest on assets. They could theoretically be inferred from image analysis (face detection, object segmentation), but manual placement has advantages:

1. **Accuracy.** A person placing POIs on an astronaut image will correctly identify "feet_center" as the bottom edge of the boots, not the bottom of the image frame. Automated detection might miss details or misalign.

2. **Stability.** The POI is tied to the asset's semantic identity, not its image content. If the source image changes (new version of the astronaut), the POI can be updated without re-running analysis.

3. **Extensibility.** You can add POIs that have no visual marker but are useful for placement, like "center-of-mass" or "optical-center" or "character's eyes". These are compositional concepts, not image features.

### Why semantic placement over pixel coordinates

Semantic placement (guide-based, POI-based) replaces pixel coordinates as the primary positioning model because it makes compositions resilient to changes:

1. **Canvas size changes.** Move a guide from `y_pct: 0.80` to `y_pct: 0.70`. All layers placed relative to that guide shift automatically. With pixel coordinates, you would need to recalculate every offset.

2. **Asset swapping.** Swap the astronaut image for a different one. If the catalog has `feet_center` at the same `y_pct`, the placement is preserved. With pixel coordinates, every layer would need manual adjustment.

3. **Intent preservation.** "Place the astronaut's feet on the ground line" is compositional intent. "Place layer at (325, 720)" is an implementation detail. The former survives refactoring; the latter does not.

## Project Structure

```
collage/
├── pkg/
│   ├── dsl/collage.go        # YAML parser, DSL types, validation
│   ├── render/render.go      # ImageMagick rendering pipeline
│   ├── render/poi_debug.go   # POI debug overlay rendering
│   ├── catalog/catalog.go    # Catalog JSON loader, Index
│   └── editor/
│       ├── server.go         # HTTP server, CORS, SafeResolve
│       ├── handlers.go       # API endpoint implementations
│       ├── handlers_test.go  # 5 handler tests
│       └── safe_path_test.go # 6 path safety tests
├── cmd/
│   ├── collage/
│   │   ├── main.go           # Glazed CLI (render, inspect, poi-debug)
│   │   └── cmds/
│   │       ├── render.go     # Render command
│   │       ├── inspect.go    # Inspect command
│   │       └── poi_debug.go  # POI debug command
│   └── collage-editor/
│       └── main.go           # Editor HTTP server entrypoint
├── web/editor/
│   ├── index.html            # Editor UI shell
│   ├── src/
│   │   ├── main.ts           # Frontend wiring, state management
│   │   ├── api.ts            # API client
│   │   ├── state.ts          # State model, catalog helpers
│   │   ├── types.ts          # TypeScript types
│   │   └── components/
│   │       ├── CanvasView.ts     # Layer rendering, drag handlers
│   │       ├── LayerInspector.ts # Layer details display
│   │       └── POIEditor.ts      # POI point editor
│   └── package.json          # Vite + TypeScript
└── examples/
    ├── 02-two-layer.yaml     # Simple: two layers, center positioning
    ├── 22-intent-astronaut-poi.yaml  # Complex: guides, POIs, offsets
    └── catalogs/
        └── demo-poi-catalog.json
```

## Current Status

The project has two complete, functional components:

**CLI renderer:** Parses YAML, resolves all placement types, renders through ImageMagick. Supports `--preview` for fast iteration and `--dry-run` for inspection. Three commands: `render`, `inspect`, `poi-debug`.

**Browser editor:** HTTP backend with 7 API endpoints (project load, project save, preview render, catalog load, catalog save, POI debug, serialize). Frontend with Vite/TypeScript: browser-native layer rendering, real-time drag, layer inspector, POI editor, YAML source panel. 11 backend unit tests pass.

17 compositions in the examples directory, ranging from simple two-layer compositions to complex multi-guide arrangements with catalog POI placement.

## Open Questions

- **Browser vs ImageMagick fidelity.** The browser renders rotation and flip via CSS transforms, which may not match ImageMagick's exact output for edge cases (sub-pixel positioning, anti-aliasing). A visual comparison suite would quantify the difference.

- **Layer image loading at scale.** The current approach loads each layer image as a separate `<img>` element. For compositions with 50+ layers, this could cause network contention. A loading strategy with progressive enhancement or a preloaded sprite sheet would help.

- **Rotation handles.** The editor supports rotation in YAML but not interactive rotation in the browser. Adding SVG rotation handles (drag a handle to set rotation angle) would complete the interactive toolkit.

- **Merger of CLI and editor.** The editor is currently a separate binary (`collage-editor`). Merging it into the main CLI as `collage serve` would unify the project and simplify the command surface.

## Related Work

The project shares concepts with several domains:

- **Graphic design tools.** Figma, Affinity Designer, and Adobe Illustrator all use guide-based positioning and anchor-point placement. The DSL here is a minimal, text-based analog.

- **Declarative layout systems.** CSS Flexbox and Grid place elements relative to containers, not absolute coordinates. The DSL's composition-relative sizing (`fit_pct`) is analogous to `width: 50%`.

- **Asset management systems.** The catalog system (JSON files with POIs and metadata) is a lightweight analog of digital asset management (DAM) systems used in professional design studios.

## References

- DSL specification: `/home/manuel/code/wesen/collage/examples/SPEC.md`
- Sample composition with semantic placement: `/home/manuel/code/wesen/collage/examples/22-intent-astronaut-poi.yaml`
- Simple two-layer example: `/home/manuel/code/wesen/collage/examples/02-two-layer.yaml`
- Catalog sample: `/home/manuel/code/wesen/collage/examples/catalogs/demo-poi-catalog.json`
- Go DSL parser: `/home/manuel/code/wesen/collage/pkg/dsl/collage.go`
- ImageMagick renderer: `/home/manuel/code/wesen/collage/pkg/render/render.go`
- Catalog loader: `/home/manuel/code/wesen/collage/pkg/catalog/catalog.go`
- Browser editor server: `/home/manuel/code/wesen/collage/pkg/editor/server.go`
- Browser editor handlers: `/home/manuel/code/wesen/collage/pkg/editor/handlers.go`
- CanvasView component: `/home/manuel/code/wesen/collage/web/editor/src/components/CanvasView.ts`
- Frontend main: `/home/manuel/code/wesen/collage/web/editor/src/main.ts`
