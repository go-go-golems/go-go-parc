# DreamCoder Tiling WM

- URL: https://chatgpt.com/c/6a7e1ebc-b9d8-83ea-98a9-45b5368db5fc
- Created: 2026-08-13T19:45:02.900Z

---

> Dreamcoder tiling wm algorithms

```json
{"system2_search_query":[{"q":"DreamCoder tiling WM algorithms"},{"q":"DreamCoder tiling wake sleep algorithm"},{"q":"DreamCoder program synthesis tiling domain algorithm"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Searched 20 websites**

</details>

I’m reading this as: **DreamCoder applied to tiling-window-manager layout algorithms**. DreamCoder itself is a program-synthesis system, not a WM.

```json
{"system1_search_query":[{"q":"\"DreamCoder\" \"tiling\" window manager"},{"q":"\"DreamCoder\" tiling layout algorithm"},{"q":"\"DreamCoder\" \"window manager\""}],"response_length":"short"}
```

<details><summary>💭 Thinking</summary>

**Inferring tiling algorithms**

I’m treating Dream Coder’s public behavior as evidence, not assuming undocumented internals. Its panes suggest a split-tree model with weighted rectangle subdivision, directional neighbor selection, swapping, collapsible hidden panes, tabbed stacks, and responsive single-column mobile layout.

**Searched 16 websites**

</details>

For the **DreamCoder at dreamcoder.ai**—the browser-based tiling WM for AI agents—the public site describes the behavior but does **not publish the exact tiling/geometry algorithm**. It supports arbitrary **tile, split, stack, swap, resize, hide/reflow, and multiple workspaces**; on mobile, panes reflow to a single column. citeturn923783view0

The implementation most naturally maps to these algorithms:

- **Layout representation:** a recursive **BSP/split tree**. Internal nodes are horizontal/vertical splits with a ratio; leaves are panes. “Stack” can be another node type holding several panes.
- **Geometry:** recursively subdivide the available rectangle according to each split node's orientation and ratio.
- **Resize:** modify the nearest ancestor split ratio rather than storing absolute pane coordinates.
- **Swap:** exchange the pane IDs at two leaves, leaving the geometry/tree intact.
- **Move pane:** remove a leaf, collapse any resulting one-child parent, then insert it adjacent to the target pane with a new H/V split.
- **Hide/reflow:** remove the hidden leaf from layout calculation and collapse redundant nodes. This matches DreamCoder's advertised hide-and-reflow behavior. citeturn923783view0
- **Directional focus (WASD):** filter panes lying in the requested direction, then rank candidates using edge distance plus perpendicular-axis overlap/center distance.
- **Responsive/mobile:** replace the desktop tree geometry with a linear vertical traversal of visible leaves; DreamCoder explicitly says phone layouts reflow to one column. citeturn923783view0

So the core tiler can be approximately:

```text
layout(node, rect):
    if node is Pane:
        pane.geometry = rect

    if node is Stack:
        each pane.geometry = rect

    if node is HSplit(r):
        left, right = split_x(rect, r)
        layout(node.a, left)
        layout(node.b, right)

    if node is VSplit(r):
        top, bottom = split_y(rect, r)
        layout(node.a, top)
        layout(node.b, bottom)
```

A classic **master/stack** algorithm like xmonad's default tiling layout is simpler, but DreamCoder's advertised arbitrary splitting, stacking, swapping and resizing makes a **persistent split-tree/BSP model** the stronger architectural fit. That's an inference from the documented behavior, not a confirmed description of DreamCoder's internal source. citeturn923783view0turn923783search3

