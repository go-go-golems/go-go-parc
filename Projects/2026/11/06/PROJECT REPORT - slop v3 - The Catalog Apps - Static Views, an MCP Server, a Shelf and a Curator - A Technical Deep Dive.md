---
title: "slop v3: The Catalog Apps — Static Views, an MCP Server, a Shelf and a Curator — A Technical Deep Dive"
aliases:
  - SLOP3-015 report part 2
  - slop catalog apps
  - slop catalog MCP shelf curator
tags:
  - project
  - slop
  - frontend
  - static-hosting
  - mcp
  - llm
  - security
status: active
type: project
created: 2026-11-06
repo: /home/manuel/workspaces/2026-10-28/slop-computer/slop-computer
---

# slop v3: The Catalog Apps — Static Views, an MCP Server, a Shelf and a Curator — A Technical Deep Dive

The first report on this project, [[PROJECT REPORT - slop v3 - Catalog Views - Many Small Static Apps over One Catalog - A Technical Deep Dive|Catalog Views]], described a catalog of the 100 applications imported from francois and its first two interfaces, an index and a table, published as separate stores on slop's static host. This report covers the rest of the work. The catalog now has fifteen stores: twelve on the static host and three on the live host. The static views are a command palette, a contact sheet of running previews, a capability map, a printable zine with fold-and-cut layouts, a timeline with an Atom feed, a size treemap, a roulette, a text terminal and a desktop with windows. An `/agents` page describes the files and the server that programs can use. The live apps are an MCP server for agents, a shelf on which signed-in people keep and share apps, and a curator that asks a language model for recommendations.

The work is ticket SLOP3-015, pull request #35, and all of it is deployed at `https://site.slop.yolo.scapegoat.dev/catalog/` and `https://apps.slop.yolo.scapegoat.dev/catalog/`. The point of the exercise was to find out how far one can get on slop by writing small apps, and what the platform requires of an app author along the way. The findings were collected into a developer guide, `doc/building-apps.md`, in the slop-computer repository. This report explains the mechanisms behind each piece, the defects found while building them, and the measurements that decide what production still needs.

> [!summary]
> - **Most of the catalog is plain files.** Twelve of fifteen stores are static HTML on the static host, sharing one kit and one data file. Each new view cost one HTML file of 100 to 340 lines and four API calls.
> - **The runtime adds what files cannot do.** The MCP server needs server code, the shelf needs per-person storage and presence, and the curator needs a model. They run on the live host, and each one depends on a feature merged the same day: express routes and mount API policies (#31), and the visitor-privacy rules (#34).
> - **Production measurements decide the remaining work.** Every static file is cached for 60 seconds and revalidated by ETag. The 94 cover images weigh 76 MB in total, and members cannot use the curator until model access is granted to them.

## 1. What was built

The catalog's data is one file, `data/catalog.json`, produced by a build script from the release stores. Every interface reads it. Table 1 lists the stores. The line counts include HTML, CSS and JavaScript.

| Store | Host | Kind | Lines | What it shows |
|---|---|---|---:|---|
| `catalog` | static | landing page, kit, data | 640 | the shared kit (`views.js`, `views.css`), `catalog.json`, `feed.xml`, `llms.txt`, `search-index.json` |
| `catalog-list` | static | view | 120 | an editorial index with sort, tags and pages |
| `catalog-table` | static | view | 109 | a sortable table with a capability filter |
| `catalog-sheet` | static | view | 193 | a contact sheet of live previews |
| `catalog-caps` | static | view | 131 | apps by runtime capability and by combination |
| `catalog-zine` | static | view | 337 | printable pages and two fold layouts |
| `catalog-timeline` | static | view | 109 | releases per day, changelogs, the feed |
| `catalog-treemap` | static | view | 156 | area by HTML size |
| `catalog-roulette` | static | view | 135 | a random app, and apps like it or unlike it |
| `catalog-term` | static | view | 160 | a command line over the catalog |
| `catalog-desktop` | static | view | 250 | windows, a start menu and a taskbar |
| `catalog-agents` | static | view | 121 | the agents page with a live MCP console |
| `catalog-mcp` | live | actor, HTTP endpoint | 143 | a read-only MCP server |
| `catalog-shelf` | live | page | 308 | private stars, shared shelves, presence |
| `catalog-curator` | live | page and actor | 254 | model recommendations, apps of the day |

*Table 1. The fifteen stores of the catalog.*

The branch adds 8,812 lines over 70 files, of which roughly 3,200 are the apps, 335 are host tests, 490 are scripts and the rest are the ticket's guide, diary and evidence.

## 2. The kit

Every static view includes `/catalog/kit/views.js`, which provides the loader, the header with the view switcher and search box, the viewer, and helpers. Four additions in this phase are worth describing, because every view that came later depends on them.

### 2.1 The command palette

Pressing ⌘K or Ctrl K on any view opens a dialog that searches four kinds of entries: the views, the 100 apps, the 125 tags and the five capabilities. Ranking uses one function, `fuzzy(text, query)`:

```js
function fuzzy(text, q) {
  text = text.toLowerCase();
  const at = text.indexOf(q);
  if (at >= 0) return 100 + (at === 0 ? 50 : /\W/.test(text[at - 1]) ? 25 : 0) - text.length / 100;
  let score = 0, ti = 0, run = 0;
  for (const ch of q) {
    const i = text.indexOf(ch, ti);
    if (i < 0) return -1;                         // not a subsequence
    run = i === ti && ti > 0 ? run + 1 : 0;       // consecutive characters
    score += 1 + run * 2 + (i === 0 || /\W/.test(text[i - 1]) ? 3 : 0);
    ti = i + 1;
  }
  return score - text.length / 100;
}
```

A substring match always outranks a subsequence match, a prefix outranks a match at a word start, and among equals a shorter text ranks first. If the title does not match, the entry may still match when every word of the query appears in the app's id, tags, capabilities or description; it then gets the lowest positive score. The query "wft" finds Weft by subsequence, and "latice" finds the four Lattice apps. Enter opens an app in the viewer of the current page if the page has one, and otherwise on the index.

### 2.2 Pages

A hundred items is too many for one page in most views, and far too many for the contact sheet, which runs previews. `paged(items, size, hosts, redraw)` reads `?page=N` from the address, clamps it to the valid range, draws a pager into each host element, and returns the slice to render. A view calls `paged.reset()` when its filters change, which removes `?page` so that a new filter starts on page 1. The sizes are 20 for the index, 50 for the table, and 24 for the sheet (36 at phone aspect, where tiles are smaller).

### 2.3 Live previews and similarity

The viewer from the first phase previews a free app by fetching its HTML and setting it as the `srcdoc` of a sandboxed frame. The reason was explained in the first report: the live shell forbids framing, and a preview must not run with the catalog's origin. Two more views needed the same preview, so it became a helper. `live(box, item, device)` creates the frame at the device's real CSS size, scales it to fit the box with a `ResizeObserver`, and returns a `stop()` function that removes it.

`related(item, items)` ranks the other apps by similarity:

$$\text{sim}(a, b) = J(\text{tags}_a, \text{tags}_b) + \tfrac14 \, J(\text{caps}_a, \text{caps}_b), \qquad J(A, B) = \frac{|A \cap B|}{|A \cup B|}$$

The capability term is weighted down because 78 apps share the same capability set, which would otherwise dominate.

### 2.4 Events

The kit dispatches two events on `window`: `catalog:search` when the search box changes, and `catalog:viewer` when the viewer opens or closes. The contact sheet and the roulette use the second to stop their running previews while the viewer is open, so that at most one set of frames runs at a time.

## 3. The static views

Each view in this section is one HTML file. What distinguishes them is the mechanism each needed.

### 3.1 The contact sheet: a budget for running frames

The contact sheet shows every app as a tile, and the free ones run. Running 93 apps at once is impossible: their HTML totals tens of megabytes, and many run animation loops. The sheet therefore keeps a budget. An `IntersectionObserver` marks which tiles are visible (with a 100-pixel margin, and only after scrolling has been still for 150 ms). A scheduler then runs:

```text
schedule():
  if busy: return
  busy = true
  loop:
    want = visible tiles whose app is free and at most 1.5 MB, in page order, first 8
    stop every running or loading tile not in want
    next = first tile in want that is neither running nor loading
    if none: break
    await start(next)        # fetch the HTML, set srcdoc, wait for load or 4 s
  busy = false
```

The loop recomputes the wanted set on every turn, so a fast scroll during a slow load is resolved on the next turn. Starting frames one at a time keeps the network from fetching eight large documents in parallel. Apps over 1.5 MB show their cover and the label "view to run". Under `prefers-reduced-motion` the sheet starts in "Covers" mode, which runs nothing.

### 3.2 The capability map

Each app declares the runtime capabilities it uses. The map counts them and groups apps by their exact set. Table 2 shows the result for the current catalog.

| Capability set | Apps |
|---|---:|
| sample | 78 |
| sample, downloads | 9 |
| sample, downloads, db, user | 3 |
| sample, downloads, db, user, room | 2 |
| sample, downloads, db | 2 |
| sample, db | 2 |
| sample, downloads, room | 2 |
| sample, db, user, room | 1 |
| sample, db, user | 1 |

*Table 2. The nine capability sets declared by the 100 apps.*

Every app declares `sample`, because every francois app may call a model. Only 11 declare `db` and 5 declare `room`. Most of the catalog therefore uses slop as a host for a single page that may ask a model, and only a few use shared state or real-time presence. The map states what each capability gives a page on slop, including the rule from #34 that a page sees a person's name only with the `profile` scope.

### 3.3 The zine and imposition

The zine view lays the catalog out as printed pages: a cover, a contents list with page numbers, and one page per app. Pages are sized in millimetres from CSS variables, and the view writes a matching `@page { size: … }` rule, so the screen shows what the printer receives. The default size is 158 × 210 mm, the reMarkable's screen; A5, A4 and Letter are options. Exported with Chromium, the full zine is 104 pages; the cover images made the first PDF 88 MB, and Ghostscript at 150 dpi reduced it to 4.9 MB.

Two further layouts arrange the pages for folding, a task called imposition. Both take the chosen apps a part at a time: a cover, the part's apps, blank pages if the part is short, and a back cover that lists the apps by page.

**The 8-page fold** uses one landscape sheet, printed on one side, divided into a 4 × 2 grid of panels. The top row is printed upside down:

```text
  [5] [4] [3] [2]     ← rotated 180°
  [6] [7] [8] [1]
```

The order can be derived from the folding. Folding the sheet along its long axis puts each top panel behind the bottom panel in the same column, so the leaves at the outer columns are double: column 4 holds pages 1 and 2, and column 1 holds pages 6 and 5. The cut runs along the fold across the two middle columns, which separates their top and bottom halves; each half folds on its own vertical crease into a leaf, giving pages 3 and 4 from the top and 7 and 8 from the bottom. The leaves then read 1–2, 3–4, 5–6, 7–8. A page is drawn at twice the panel's size and scaled by 0.5, so the type is set larger in this layout. For the upside-down panels the transform is `translate(w, h) rotate(180deg) scale(0.5)` with origin at the top left. Transforms apply from right to left, so the page is scaled, turned about the origin into the negative quadrant, and moved back into its cell.

**The 16-page booklet** uses four landscape sheets printed on both sides, stacked, folded once and stapled. For a booklet of $n$ pages (a multiple of 4), sheet $s$, counted from the outside starting at 0, carries

$$\text{front: } (n - 2s,\; 2s + 1), \qquad \text{back: } (2s + 2,\; n - 2s - 1).$$

For $n = 16$ this gives 16 | 1 and 2 | 15 on the first sheet, and 14 | 3 and 4 | 13 on the second, which the generated PDF confirmed. Printing requires "flip on the short edge"; with the long edge, every back side is upside down.

### 3.4 The timeline and the feed

Releases have dates, versions and changelogs. The production stores hold only each app's current release, because the import in SLOP3-013 did not copy older releases into the stores. The full history, 113 releases, is in that ticket's inventory file in the repository, and the catalog build reads it with an optional `--history` argument. Four apps have more than one release; 7 of 107 published releases are updates.

The timeline shows one stacked bar per day (new apps and updates) and the releases of each day. The same data produces an Atom feed, `feed.xml`, at build time: one entry per release with a `tag:` id, a link to the viewer and to the app, and the changelog or description as the summary. The static host serves it as `text/xml`, which feed readers accept.

### 3.5 The treemap

The treemap divides a rectangle among the apps in proportion to the size of their HTML, which ranges from 9.8 MB (CraftKit Workbench) to 20 KB (Béton Brut Studio). It uses the squarified layout of Bruls, Huizing and van Wijk, which keeps cells close to square. The algorithm sorts the areas in decreasing order and adds them to a row along the shorter side of the remaining rectangle while doing so does not worsen the row's worst aspect ratio:

$$\text{worst}(R, w) = \max\left(\frac{w^2 \max R}{s^2},\; \frac{s^2}{w^2 \min R}\right), \qquad s = \sum R$$

where $R$ is the row's areas and $w$ is the side the row is laid along. When adding the next area would increase the worst ratio, the row is fixed as a strip, the rectangle shrinks by the strip, and a new row begins. The view can also group first by capability set, first tag or access, laying out the groups and then the apps inside each group. Shade encodes the number of capabilities and hatching marks subscriber apps.

The treemap made one data problem visible. Béton Brut Studio is the smallest app because its HTML loads four scripts (`core.js`, `render.js`, `presets.js`, `ide.js`) that its store does not contain. Whether the scripts were missing on slop.boutique too has not been checked.

### 3.6 The roulette, the terminal and the desktop

The roulette shows one or two random apps running, then the four most similar apps under "Like this" and the three least similar under "…but different", using `related()`. The picks are kept in the address (`?a=weft&b=…`), so a result can be sent to someone.

The terminal is a command interpreter over the catalog: `ls [tag]`, `grep words`, `find text` (fuzzy), `cat id`, `open id` (the viewer), `run id` (the real app), `tags`, `caps`, `du`, `new`, `random`, `cd view`, `history` and `clear`. Tab completes commands, ids, tags, capabilities and view names. Its first version printed class names as text. The output function accepted parts of the form `[class, text]`, and flattening the argument list with `.flat()` also flattened those pairs. Styled spans are now objects, so flattening cannot break them.

The desktop presents the apps as windows. Windows can be dragged by their title bars, resized from a corner, minimized, maximized and closed. The start menu searches with `fuzzy()`, explorer windows list app icons, and a taskbar shows the open windows. The open app windows are kept in the address. At most five app windows run; when a sixth is focused, the least recently focused running window pauses with "click to run", and minimized windows stop. Dragging over an iframe loses `pointermove` events to the frame, so the desktop sets `pointer-events: none` on all frames while a drag is in progress.

## 4. Views for agents

Ramon's site offers agents a plain-text index, a JSON index and a read-only MCP server. The catalog now has all three.

- **`llms.txt`** follows the llms.txt convention: a title, a one-paragraph summary, a section of links for agents, and one Markdown line per app with tags, runtime capabilities and access.
- **`search-index.json`** has one flat record per app, including a lower-case `text` field for simple matching, and the URL of the app's HTML for free apps.
- **The MCP server** answers at `https://apps.slop.yolo.scapegoat.dev/catalog/mcp`.

### 4.1 The server

The Model Context Protocol's Streamable HTTP transport lets a server answer each POST with a single JSON response, without a session or an event stream. This server takes that form. It is an actor written with slop's `express` module from #31:

```js
const app = require('express').app();
const catalog = require('./data/catalog.json');   // deployed with the store

app.post('/').public().handle((ctx, res) => {
  const body = ctx.body;                            // parsed JSON
  const out = Array.isArray(body) ? body.map(answer).filter(Boolean) : answer(body);
  if (out === null || (Array.isArray(out) && !out.length)) return res.status(202).end();
  res.set('Cache-Control', 'no-store').json(out);
});
```

`answer` handles `initialize` (choosing the client's protocol version if it is one of three supported, otherwise the newest), `ping`, `tools/list` and `tools/call`. There are four tools: `search_apps`, `get_app`, `list_tags` and `list_capabilities`, all annotated `readOnlyHint: true`. An unknown app is a tool result with `isError: true`, as the protocol prescribes for tool failures; an unknown method is JSON-RPC error −32601; a request containing only notifications receives `202 Accepted` with an empty body. A GET answers `405` with a short description.

### 4.2 Hosting the server

The first attempt mounted the server on the static host, next to the files. `mount.set` refused: a store that runs an actor belongs on the live host. On the live host a public route needs no session, but a public endpoint needs limits. Mounts in #31 carry an API policy, and the deploy sets this one:

```json
{"routes": ["POST /", "GET /"], "defaultMin": "public",
 "middleware": [
   {"name": "rateLimit", "config": {"per": "ip", "limit": 60, "window": "1m", "burst": 120}},
   {"name": "cors", "config": {"origins": ["https://site.slop.yolo.scapegoat.dev"]}}]}
```

Two details of the policy were not obvious. First, a policy's `defaultMin` is `view`, which would raise the public routes to `view` and give every guest a 404; it must be set to `public`. Second, CORS takes an explicit list of origins, and preflight requests are answered before the actor is built, so they cost no actor turn. The CORS entry exists so that the `/agents` page on the static host can call the server from the browser; it does so in a small console that runs `initialize` and `tools/list` and then calls a chosen tool.

The rate limiter is the token bucket whose eviction rule was corrected in #31 after review: a bucket is forgotten only once it would have refilled, so a client cannot obtain a new burst by waiting less than the refill time.

### 4.3 Verification

A host test covers the protocol on a live mount with the same API policy: initialize, the notification, the tool list, search, `get_app` found and not found, an unknown method, a batch, the CORS preflight, the allowed and a refused origin, and the GET. On production, the official Python SDK (`mcp` 2.3.0) connected, reported `slop-catalog` at protocol `2025-06-18`, listed the four tools, and called them. The browser console on the agents page received an answer in 339 ms.

## 5. The shelf

The shelf is the first catalog app that keeps data about people. Each signed-in person can star apps, privately. A person may choose to share their shelf, and shared shelves are counted into a list of apps on people's shelves. Everyone with the page open sees who else is there and which app each person is looking at.

### 5.1 The data model and its rules

| Path | Holds | Who may read | Who may write |
|---|---|---|---|
| `data/users/<id>/shelf` | `{stars: {appId: time}, share}` | that person | that person |
| `shelves/<id>` | `{apps: [ids], at}` | everyone admitted | that person (`{self}`) |

The manifest declares the second row; the first is slop's default for `data/users/<id>/`:

```json
"db": { "rules": [
  { "path": "shelves", "read": "view", "write": "owner" },
  { "path": "shelves/{self}", "write": "interact" } ] },
"user": { "scopes": ["profile"] },
"room": {}
```

The store grants `@guest view` and `@member interact`, so signed-in members may write and guests may only read. Presence carries one field, `{looking: <app id>}`. The names on screen come from `user.profiles(ids)`, which since #34 returns names only because the app declares the `profile` scope. A host test checks the boundaries between two people: Bob reads Ada's shared shelf, does not see her private one, and can write neither; a guest writes nothing.

### 5.2 Three defects

The shelf was tested on a local server with two people signed in, in two browser contexts. Three defects appeared, and each one is a general lesson for page authors.

**The page rolled back its own state.** The first version subscribed to the person's own document with `onSnapshot` and replaced its state with each snapshot. A quick sequence of stars produced several writes, and a snapshot of an earlier write could arrive after a later change had been made in the page, which undid it; the share checkbox visibly unchecked itself. Ignoring snapshots while writes were pending was not sufficient, because the initial snapshot of an empty document could arrive after the first click. The document has a single writer, the page itself, so the page now reads it once with `get()` and then writes each change in order:

```js
let saving = Promise.resolve();
function save() {
  const body = { stars: state.stars, share: state.share, at: Date.now() };
  saving = saving.then(async () => {
    await mineRef.set(body);
    if (state.share) await db.doc("shelves/" + uid).set({ apps: ids(), at: Date.now() });
    else await db.doc("shelves/" + uid).delete();
  });
}
```

Live subscriptions remain the right tool for data that other people write, here the collection of shared shelves.

**Clicks were lost.** `room.onPeers` fires whenever any participant's presence changes, and the handler rebuilt the list of apps every time. A click consists of a mousedown and a mouseup on the same element; when the list was rebuilt between them, the element was replaced and no click event fired. The handler now computes a signature of the fields it displays (each peer's id and the app it is looking at) and re-renders only when the signature changes.

**Guests were offered stars.** On production a signed-out visitor has a guest id, so the page treated them as able to keep a shelf, but the store grants guests only `view`, and their writes would have been refused. The page now asks `slop.visitor()` for `guest` and `level`, and shows a sign-in button instead of stars unless the visitor holds at least `interact`.

One difference from the claude.ai runtime also showed up: on slop, `avatarUrl` is an empty string, where the claude.ai contract promises a renderable image. Avatars are drawn as initials on the profile's `color`, which slop does provide.

## 6. The curator

The curator answers requests such as "a playful game to start from" by giving a model the whole catalog and asking it to choose. It also shows three apps of the day.

### 6.1 Who pays for a model call

A call to `sample` on slop passes three gates:

1. the app declares `sample` in its manifest;
2. the app's policy cell for `sample` is on for the visitor's audience;
3. the payer has model access and budget left this month.

The payer is the visitor. In a page that is the person viewing it; in an actor action it is the person who called the action. The design follows from this. "Ask" calls `sample` from the page, so the person asking pays for their own question. "Apps of the day" is an actor action, `today`, which the page calls when no picks are stored for the day; the first member to open the page that day pays for one call, and the result is stored in `picks/<day>` for everyone, guests included. No call is made on the store's own budget.

On production the third gate is closed for members. `llm ls` lists one access row, for `@admin`. The deploy turned the policy cell on for `@member`, but members will see "no model allowance" until model access is granted to them with `llm set @member on --budget N`. That is a decision about spending across the whole platform, and it was left to the operator.

### 6.2 The prompt and the answer

The prompt contains one line per app (id, title, the first 160 characters of the description, five tags, runtime, access), about 24 KB or 6,000 tokens, then the request, then an instruction to answer with JSON of the form `{"picks": [{"id", "why"}], "note"}` using only ids from the list. The answer is read leniently: the parser takes the text from the first `{` to the last `}`, parses it, and keeps only picks whose id exists in the catalog. If nothing usable remains, the page shows the model's text as it is. The same code, `curate.js`, is loaded by the page and required by the actor.

### 6.3 A turn ends at an await

An actor handles one event at a time, as a turn that commits its writes. When a handler awaits real I/O, such as a model call, the turn ends at the `await`, and the code after it runs in a new turn. Two members who open the page at the same moment can therefore both find no picks, both call the model, and both reach the code that stores the result. The action reads the day's document again after the call and stores its picks only if none are there yet, so the first answer is kept. Both callers still pay for their call; the check prevents inconsistent picks, not the cost.

### 6.4 Testing without a model

Locally the server ran with the `fake` backend, which answers "slop is connected." to most prompts. That answer does not parse, which exercised the fallbacks: `today` stored picks seeded by the date (a hash of the date selects three free apps), and "Ask" showed the text. A host test checks the gates and the storage: without model access the action fails; with it, picks are stored once and returned again; a guest reads them and cannot run the action. The model's real answers on production have not yet been checked, because that requires a signed-in account with model access.

## 7. Deployment as data

Fifteen stores with grants, policy cells, mounts and API policies are too many to deploy by hand. The deploy script describes each store as a record:

```python
{"store": "catalog-curator", "src": "apps/catalog-curator", "host": "live",
 "path": "/catalog/curator",
 "extra": {"data/catalog.json": "catalog.json"},
 "grants": {"@guest": "view", "@member": "interact"},
 "policy": [("sample", "member", True)]}
```

For each record it computes the difference between the wanted state and the server's state, prints a plan, and with `--apply` runs only the calls that are needed. The tree is compared by path and SHA-256 with `files.ls`; grants and policy cells by value; the mount and its API policy by inclusion, because the server fills in defaults. The criterion for a finished deployment is a second run that prints "up to date" for every store. The script also refuses to replace a mount that serves another store.

The same script deploys to a local server. `slop serve --local --llm fake` runs a server with a plain sign-in form; a device login with `SLOP_CREDENTIALS` pointing to a separate file gives the script an admin token without touching the production login. With this server, two browser contexts can sign in as two people, which is how the shelf and the curator were tested before production.

## 8. Caching and what production needs

The question of whether these apps manage caching properly was answered by measuring production. Table 3 shows the headers.

| Resource | `Cache-Control` | Validation |
|---|---|---|
| Static pages, the kit, `catalog.json`, files under `/_s/`, images under `/_d/` | `public, max-age=60, stale-while-revalidate=600` | strong ETag (the file's SHA-256); `If-None-Match` returns 304; text is compressed with zstd |
| Live shell pages, actor routes | `no-store` | — |

*Table 3. Caching on production, measured with `curl`.*

Revalidation is therefore cheap, and a browser that has seen a file never downloads it twice unchanged. Three problems remain.

1. **Images are served as uploaded.** The 94 covers total 76,310,460 bytes; the largest is 16,977,574 bytes, and the median width is 1,600 pixels. The index draws them at 360 pixels wide and the shelf at 56. Nothing on the server resizes images, so thumbnails must be produced at build time, for example at 480 and 960 pixels, and offered with `srcset`.
2. **Content-addressed URLs are revalidated anyway.** An image under `/_d/` and a kit URL with `?v=<hash>` can never change, yet the static host applies one policy to every file, so browsers check them again after 60 seconds or, at the latest, 11 minutes. Serving such URLs with `Cache-Control: public, max-age=31536000, immutable` is a small change in the server.
3. **Every rebuild changes the data.** `catalog.json` records the time it was generated, so each build differs from the last and is pushed to the four stores that ship it, even when no app changed. The timestamp should change only with the content.

The remaining items before calling the catalog production-ready are: rebuilds triggered by new releases rather than run by hand; a decision on model access for members; a favicon (the static host answers 404 for `/favicon.ico`); and the open security follow-up from earlier work, a viewer check on the sandbox's `/v/<n>/` URLs.

## 9. What this shows about slop

The project supports four statements about the platform.

- **Files carry most of the load.** Twelve of fifteen stores, including the palette, the zine with imposition, the treemap and the desktop, are plain files with no server code. On slop such a view costs one file and four calls.
- **The runtime is used where files are insufficient.** Server code was needed for the MCP endpoint, per-person storage and presence for the shelf, and a model for the curator. Each of these used a slop capability exactly as documented, and each depended on a feature merged the same day, which made the catalog the first production use of #31's express routes, API policies and rate limiter, and of #34's identity rules.
- **Costs and identities are explicit.** Whether a page sees an id or a name, and who pays for a model call, follow from the manifest, the policy matrix and the model-access rows. The curator's design followed from reading those rules, and its one production gap, model access for members, is a row that an operator decides.
- **The defects were in page code, not in the platform.** The rolled-back shelf, the lost clicks and the terminal's flattened output were all mistakes in the pages. The platform differences that mattered, the empty `avatarUrl` and guests having ids, are now documented in the developer guide.

## 10. Open questions

- Should members get model access, and with what monthly budget? Without it, the curator works only for administrators.
- Should the static host mark content-addressed URLs as immutable, or should a CDN do it?
- Should catalog rebuilds run as an actor reacting to new releases, or in continuous integration?
- Were Béton Brut Studio's four scripts missing on slop.boutique, or lost in the import?
- Would a shorter prompt (titles and tags only) give the curator answers that are as good, at a third of the cost?

## Notes on the implementation record

- **Ticket:** `ttmp/2026/11/06/SLOP3-015--catalog-views-…/` in slop-computer. The diary's steps 3 to 7 cover this report: the palette, pager, sheet, capability map and zine (step 3); the fold layouts and the second deploy (step 4); the production checks after #31–#34 and the five static views (step 5); the agents views (step 6); the shelf and the curator (step 7). Screenshots 07–24 are in `various/screenshots/`.
- **Pull request:** #35, branch `task/slop3-015-catalog-views`. Key commits: `84fb146` (palette, pager, sheet, caps, zine), `31295b9` (fold layouts), `4fe3ea9` (timeline, treemap, roulette, terminal, desktop), `4bed408` (agents and MCP), `34624d8` (shelf), `2d24b58` (curator), `a2cddbf` (developer guide).
- **Tests:** `pkg/host/catalog_views_test.go`, `catalog_mcp_test.go`, `catalog_shelf_test.go`, `catalog_curator_test.go`.
- **Scripts:** `01-build-catalog.py` (catalog, feed, llms.txt, search index), `02-deploy.py` (all fifteen stores), `03-devserve.py` (static views locally), `04-mcp-check.py` (the SDK client).
- **Production checks after #31–#34:** the SLOP3-013 verifier passed for all 103 stores on `sha-8e01dca` (95 free apps answer 200 to a guest, 8 paid apps 401).
- **Developer guide:** `doc/building-apps.md` in slop-computer.

## Related notes

- [[PROJECT REPORT - slop v3 - Catalog Views - Many Small Static Apps over One Catalog - A Technical Deep Dive]] — the first phase: the catalog file, the kit, the viewer, the index and the table.
- [[PROJECT REPORT - slop v3 - Importing the francois Catalog - Real Releases, Verbatim Capabilities and Paid Access - A Technical Deep Dive]] — where the 100 apps and their release history come from.
