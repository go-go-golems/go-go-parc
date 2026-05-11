---
title: "reMarkable V6 rmdoc Scene Tree Rendering"
aliases:
  - rmdoc v6
  - remarkable v6 scene tree
  - v6 annotation rendering
  - remarquee render-v6
tags: [knowledge-base, on-ramp, remarkable, pdf, rendering, scene-tree]
status: active
type: knowledge-base
created: 2026-05-11
---

# reMarkable V6 rmdoc Scene Tree Rendering

> [!summary]
> reMarkable's newer document format stores annotations as a V6 scene tree, not just as simple stroke lists. The practical problem is not “what is a tree?” The practical problem is rendering highlights, strokes, anchors, and background PDF alignment correctly. Public docs for this format are sparse; this entry is the orientation layer for reading our Remarquee work.

## The idea in one paragraph

A V6 `rmdoc` stores a document as structured scene data: pages, drawing content, highlight information, anchors, and layout relationships. Rendering an annotated PDF means reconstructing that scene tree, interpreting its semantics, and compositing the result onto the correct page background.

## Why we care

[[PROJ - Remarquee - reMarkable Toolkit]] uses this format to render annotated documents back to PDF. Without an orientation to the scene tree, the project report is hard to read because the interesting bugs are not “PDF bugs” — they are “tree interpretation and coordinate mapping” bugs.

## What makes V6 different

The important conceptual shift is that the data is no longer just “a bag of pen strokes.” It contains richer structure:
- multiple content types,
- stroke colors,
- highlights,
- anchors and relationships,
- layout information that must be mapped back to page coordinates.

That richer structure is what makes V6 rendering more faithful, but also more fragile when you get the interpretation wrong.

## The main rendering job

The rendering pipeline is roughly:

1. load the document archive,
2. parse the V6 scene tree,
3. walk each page's scene,
4. reconstruct visible marks,
5. align them to the correct PDF background,
6. composite into an output PDF.

This is not just file conversion. It is scene reconstruction.

## The gotchas we've hit

**Scene structure carries semantics.** If you flatten the tree too early, you can lose meaning about how highlights or anchored content should be interpreted.

**Background alignment matters as much as stroke rendering.** A perfectly parsed stroke placed on the wrong page coordinate system is still a broken render.

**Highlights are not just colored strokes.** They often need different composition rules than pen lines.

**Sparse docs mean implementation becomes the reference.** In practice, project reports and working code often explain more than public documentation does.

## What to look for in our code

When reading Remarquee, focus on:
- the scene parser,
- how page-local coordinates are computed,
- how highlights differ from regular strokes,
- and how the PDF merge/composition layer expects data to arrive.

Those seams explain most rendering bugs.

## Where to go deeper

- [[PROJ - Remarquee - reMarkable Toolkit]] — the main project report
- [[PROJ - Remarquee - V6 Render Overlay Y-Placement Bug]] — a concrete failure mode in V6 rendering
- reMarkable reverse-engineering/community notes — background ecosystem context
