---
title: CoreS3 Magnet Base — 3D Model Search
aliases:
  - CoreS3 Magnet Base
  - M5Stack CoreS3 magnet base search
tags:
  - project
  - 3d-printing
  - m5stack
  - cores3
  - surf
status: active
type: project
created: 2026-08-22
repo: /home/manuel/code/wesen/claw-stuff
---

# CoreS3 Magnet Base — 3D Model Search

Quick task: find an existing 3D-printable base/bottom for an M5Stack CoreS3 that lets you attach magnets, and pull the model file down locally. Searched the 3D-print platforms reachable through the `surf` CLI, found the two CoreS3-SE magnet bottoms that exist, and downloaded the cleaner one into the repo.

> [!summary]
> 1. Only the **CoreS3 SE** has off-the-shelf magnet bottoms — two of them.
> 2. The **regular CoreS3** has nothing; it would need a remix or a from-scratch base.
> 3. Downloaded botamochi's CoreS3 SE magnet bottom STL to `./3d-print/`.

## What I did

- Searched MakerWorld and Thingiverse via `surf` for CoreS3 / CoreS3 SE bottoms and bases (the term "base" was added after the first pass, per a tip).
- Compared the matches, then downloaded the single best STL into the repo's `3d-print/` folder.

## How — surf 3D model search

`surf` exposes per-platform 3D-model subcommands that call each platform's own JSON/GraphQL API from inside a logged-in browser tab rather than scraping. Search verbs:

```bash
surf makerworld models  --keyword "CoreS3 magnet"   --limit 20
surf thingiverse things --query "M5Stack CoreS3"    --per-page 20
surf printables  models --query "M5Stack CoreS3"    --limit 20
```

Fetch a single model's file list, then download:

```bash
surf thingiverse thing 7087044                       # show files + URLs
surf thingiverse download 7087044 --save-to ./3d-print/   # stream STL to disk
```

Key gotcha: each platform needs a **logged-in browser session** in the Chromium surf attaches to (socket at `~/snap/chromium/common/surf-cli/surf.sock`). Thingiverse and Printables both rejected anonymous callers; only after logging in did `surf thingiverse things` return results. Printables stayed broken the whole session (GraphQL `TypeError: Failed to fetch`), so it was never searchable here.

Another gotcha: MakerWorld **publishes no download URL for designer source STLs** even to an authenticated caller — only `.3mf` print profiles are downloadable via `surf makerworld download`. Thingiverse, by contrast, carries direct unsigned `cdn.thingiverse.com` URLs in its detail response, so `surf thingiverse download` fetches the bytes over plain HTTP with no download counter incremented.

## Results

Queries tried (both platforms, "bottom" and "base" variants): `CoreS3 magnet`, `M5Stack CoreS3`, `CoreS3 bottom`, `CoreS3 back`, `M5Stack CoreS3 back`, `CoreS3 base`, `CoreS3 SE base`, `M5Stack magnet base`, `M5CoreS3`, plus MakerWorld sorted by `downloadCount`.

### CoreS3 SE — magnet bottoms (2 found)

| Model | Platform | License | Files |
|-------|----------|---------|-------|
| **Magnet bottom part for M5Stack cores3se** — botamochi — [thing:7087044](https://www.thingiverse.com/thing:7087044) | Thingiverse | CC-BY | 1 STL; needs **4× DAISO Ø6 mm magnets** |
| M5Stack CoreS3 SE Bottom Cover. magnet attach — kaz3d — [id 1441665](https://makerworld.com/en/models/1441665) | MakerWorld | CC BY-SA | 2 STLs + 1 `.3mf` profile (id 1500574) |

### Downloaded

- `./3d-print/magnet-bottom-cores3se.stl` — 118.4 KB, botamochi, CC-BY
- Source: `surf thingiverse download 7087044 --save-to ./3d-print/`

### Regular CoreS3 (non-SE)

Nothing exists. Everything else that surfaced was the CoreS3 Lite "Bob" desk robot, older M5Stack Core/Fire/Core2 cases, or (on the "base" queries) CoreXY printer bases. The regular CoreS3 would need a remix of an SE bottom or a from-scratch base.

## Caveats

- The downloaded STL is sized for the **CoreS3 SE**, not the regular CoreS3 — verify fit before printing if you have the standard CoreS3.
- Printables was never searchable this session (auth/fetch failure); it may hold additional options once logged in.

## Next steps

- Slice and print `magnet-bottom-cores3se.stl` with 4× Ø6 mm magnets ready.
- If the device is the regular CoreS3, remix an SE bottom or model a fresh base.
- Log into Printables in surf's Chromium and retry `surf printables models --query "cores3"`.
