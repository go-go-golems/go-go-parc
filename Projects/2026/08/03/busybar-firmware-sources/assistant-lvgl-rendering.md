---
title: "Captured source: Assistant Lvgl Rendering"
source_file: "assistant-lvgl-rendering.md"
type: source
---

# Captured source: Assistant Lvgl Rendering

Original ticket source file: `assistant-lvgl-rendering.md`.

# Kagi Assistant synthesis: LVGL rendering architecture

## Provenance

- Assistant: Kimi K2.6 (reasoning)
- Web-search mode: keep
- Research focus: LVGL 9 display objects, widget trees, screen layers, direct rendering, flush callbacks, and framebuffer ownership.
- Primary URLs consulted: <https://lvgl.io/docs/open/9.3/details/main-modules/display/setup>, <https://lvgl.io/docs/open/9.5/main-modules/display/screen_layers.html>, <https://lvgl.io/docs/open/9.5/common-widget-features/tree.html>, and <https://lvgl.io/docs/open/9.3/details/common-widget-features/basics.html>.

## Synthesis

LVGL creates an `lv_display_t` for each physical display. A display has an active screen and permanent bottom, top, and system layers. The widget tree is parent-child: the screen is the root, every widget has one parent, and a parent may have many children. The top and system layers are per-display, remain visible across active-screen changes, and are intended for overlays and system-level content.

LVGL supports partial, direct, and full render modes. Partial mode uses buffers smaller than the display and asks the flush callback to copy the rendered area. Direct mode requires display-sized buffers and renders invalidated content into its final location; with two buffers, rendered areas can be copied between buffers after flushing. Full mode redraws the entire display and can use two full-size buffers as traditional double buffering. The flush callback transfers rendered pixels to the physical controller and signals completion with `lv_display_flush_ready()`.

For a dual-display embedded device, the natural mapping is one display object, buffer set, flush callback, and layer set per physical panel. A Canvas service that creates widgets in the top layer therefore has one overlay root per display rather than one global widget tree. This is the mechanism used by the BUSY Bar firmware, which creates separate front and back LVGL displays and Canvas roots.

The key distinction for this report is between retained widget state and rendered buffers. LVGL retains widgets in a tree and invalidates regions when properties change. It then renders those widgets into display buffers. The physical display driver owns the transfer after the flush callback. A client HTTP response that confirms a retained widget update does not itself confirm physical transfer completion.
