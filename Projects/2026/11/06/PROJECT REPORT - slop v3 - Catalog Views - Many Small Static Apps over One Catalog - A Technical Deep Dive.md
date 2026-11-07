---
title: "slop v3: Catalog Views — Many Small Static Apps over One Catalog — A Technical Deep Dive"
aliases:
  - SLOP3-015 report
  - slop catalog views
  - slop static host apps
tags:
  - project
  - slop
  - frontend
  - static-hosting
  - security
status: active
type: project
created: 2026-11-06
repo: /home/manuel/workspaces/2026-10-28/slop-computer/slop-computer
---

# slop v3: Catalog Views — Many Small Static Apps over One Catalog — A Technical Deep Dive

slop v3 hosts content in **stores**, and it can put any store at a URL with one command. This report describes a small project that uses that property on purpose. It takes one body of content, the 100 listed applications imported from francois in [[PROJECT REPORT - slop v3 - Importing the francois Catalog - Real Releases, Verbatim Capabilities and Paid Access - A Technical Deep Dive|SLOP3-013]], and publishes several interfaces over it: a landing page, an editorial index, a sortable table and a device viewer. Each interface is a separate store of plain HTML on slop's static host. The model was Ramon's site, html.moldandyeast.com, which presents one library of single-file HTML artifacts through an index, a modal viewer, a search palette and a set of plain-text and JSON views for agents.

The work is ticket SLOP3-015, pull request #35. It is already deployed at `https://site.slop.yolo.scapegoat.dev/catalog/`. The code is small: 953 lines, including the test and the three scripts. The interesting part is the set of platform constraints it had to respect, and the two problems that appeared only on production.

> [!summary]
> - **A view is a store.** The catalog's data and shared code live in one store mounted at `/catalog`. Each view is another store mounted below it, at `/catalog/list` and `/catalog/table`. A new view is one HTML file plus `store.new`, `files.push`, `grant.set @guest view` and `mount.set`.
> - **The viewer cannot embed a running app.** The live shell forbids framing, and for good reason. The viewer therefore runs a free app's own HTML in an opaque-origin sandbox, adds an in-memory storage shim so that apps which read `localStorage` while starting still render, and links to the real app.
> - **Caching is part of deployment.** The static host lets browsers keep a file for 60 seconds and then use it stale for 600 more. The deploy script therefore names the shared kit by its content hash.

## 1. The model: one catalog, several interfaces

html.moldandyeast.com is built around a single index file, `/search-index.json`, describing 42 artifacts by `slug, title, description, tags, bytes, added, thumb, hash, listed`. Several interfaces read it:

| Interface | Form |
| --- | --- |
| Index | headline, sort (newest, A–Z, smallest, largest), tag filter with counts, rows with thumbnail, description, Open, Download, path and size |
| Viewer | `?open=<slug>` opens a modal with Phone, Tablet and Desktop sizes, plus Info, Copy HTML and Download |
| Search | ⌘K focuses a fuzzy search |
| Agents | `/llms.txt`, `/search-index.json`, a read-only MCP server (`search_artifacts`, `get_artifact`, `list_tags`), the same tools in the page through WebMCP, and an `/agents` page with client setup |

The architectural point is that the interfaces differ while the data does not. A new interface needs no new data model and no new server code; it needs a new way to render a file that already exists. Earlier in the session, fifteen candidate interfaces were listed for slop. This ticket builds three of them (the index, the table and the viewer) plus the shared header that switches between them. The views for agents wait for pull requests #31 and #32, which let server-side code answer HTTP requests on a mount.

## 2. The platform pieces involved

### 2.1 Stores, mounts and the two hosts

A slop store is one SQLite database with a versioned file tree (`doc/design/slop-v3.md` §4). `files.push` writes the tree and takes a snapshot, and `main` names the snapshot that is served. `mount.set` attaches a store to a host and a path. slop.yolo has two kinds of host that matter here:

- **The live host,** `apps.slop.yolo.scapegoat.dev`, runs applications. A request returns the **shell**, a page that asks the server for a view. The application then runs in an iframe on its own sandbox origin, with the `window.claude` runtime: `db`, `sample`, `room`, `user`.
- **The static host,** `site.slop.yolo.scapegoat.dev`, serves files. `serveStatic` (`pkg/doors/pages/site.go:68`) treats every request as an anonymous guest. A store is served only if `@guest` holds at least `view` on it. There are no cookies, no sessions and no runtime. Responses carry `Cache-Control: public, max-age=60, stale-while-revalidate=600`.

The views read one JSON file and render HTML, so they belong on the static host. Two consequences follow. They need no privileges, and they share one origin, so every view can load the shared kit and the data with same-origin `fetch` and no CORS.

### 2.2 How a path finds its store

`registry.BestMount` (`pkg/registry/mounts.go:211`) chooses among mounts. Each pattern segment scores 2 when it matches literally and 1 when it is a `:param`, and the scores are compared segment by segment, with the longer pattern winning a tie. The static host already had `/` mounted to the `boutique` store, the storefront built during the v3 cutover. The new mounts sit below it:

```
/                 → boutique        (existing storefront, covers under /_d/)
/catalog          → catalog         (landing page, kit/, data/)
/catalog/list     → catalog-list
/catalog/table    → catalog-table
```

A request for `/catalog/list/` matches `/`, `/catalog` and `/catalog/list`. The last scores `[2, 2]`, which beats `[2]` and `[]`, so `catalog-list` answers it, with an empty remainder and therefore its entry page. `/catalog/data/catalog.json` is answered by `catalog` with remainder `data/catalog.json`. No store needs an `app.json`: `Manifest.Entry` (`pkg/apps/manifest.go:86`) returns `index.html` when nothing else is named. Before the mounts were created, the deploy checked that `boutique` had no files under `catalog/`, so nothing in it is hidden by the new mounts.

### 2.3 Where the facts come from

| Fact | Source |
| --- | --- |
| id, title, description, tags, visibility, version, free or paid, capabilities, HTML size, attachments | `francois.json` in each release store, written by SLOP3-013 |
| cover image (path, width, height), featured flag | `_data/francois-catalog.json` in the `boutique` store |

The covers are served by the static host under `/_d/francois-media*/…` because the `boutique` store holds them. A catalog item can refer to its cover by a same-origin path. 94 of the 100 listed apps have one.

## 3. The constraint that shaped the viewer

The obvious way to build a device viewer is to put the running app in an iframe of the chosen size. On slop that is not possible, and the reason is a deliberate security rule. The shell on the live host answers with:

```
content-security-policy: frame-ancestors 'none'
```

and an app's sandbox origin only accepts the main and live hosts as parents (`frameOrigins`, `pkg/doors/pages/sandbox.go:62`). The shell is the page that carries the visitor's session. Its cookie is `SameSite=Strict`, but `site.` and `apps.` belong to the same registrable domain, so they count as the same site, and a framed shell would be signed in. The static host also serves stores that other people control: a `/s/:id` mount serves any store of type `site`. Allowing the static host to frame the shell would let any such page lay its own content over a signed-in shell and capture clicks meant for it. The viewer therefore had to work without the shell.

The static host offers another path. `serveStoreFile` (`site.go:159`) serves `/_s/<store>/<ref>/<path>`, the raw tree files of any store the anonymous guest may read. The measurements on production:

```
/_s/weft/main/index.html                              200 text/html; charset=utf-8, 1,042,897 B
/_s/craftkit-workbench/main/attachments/…source.zip   200 application/zip
/_s/polis/main/index.html                             404   (paid: @subscriber only since SLOP3-013)
```

A free app's HTML is therefore available on the same origin as the catalog, and a paid one is not. Opened directly in a browser, Weft's raw HTML rendered completely: code editor, live stage and parameters, with no console errors except a missing favicon. These facts are the basis of the viewer's design: preview the app's own HTML in isolation, say clearly that the runtime is absent, and link to the real app for anything else.

## 4. The catalog file

`scripts/01-build-catalog.py` reads the production server with the slop CLI's token and writes nothing to it. It produces two files. `catalog.json` holds one item per listed app:

```python
def item(fj, store, rec, apps_origin):
    art, rel = fj["artifact"], fj["release"]
    free = bool(rel.get("freeSample"))
    base = f"/_s/{urllib.parse.quote(store)}/main/"
    return {
        "id": store, "title": art.get("title") or store, "description": art.get("description") or "",
        "tags": sorted(art.get("tags") or []), "version": rel.get("version"), "free": free,
        "capabilities": sorted((rel.get("manifest") or {}).keys()),
        "bytes": (rel.get("html") or {}).get("size", 0),
        "attachments": [{…, "href": base + "attachments/" + quote(a["name"]) if free else None} …],
        "cover": cover,                                   # from boutique, or None
        "open": f"{apps_origin}/f/{urllib.parse.quote(store)}/",
        "preview": base + "index.html" if free else None,
        "download": base + "index.html" if free else None,
    }
```

Three rules are worth stating:

- **Only listed apps are included.** `craftkit-studio`, `polis` and `stackchan-pet-studio` are hidden on francois and stay hidden here, and `aasd` has no release. That leaves 100 items.
- **A paid app gets `null` for `preview`, `download` and attachment links.** The static host would refuse those URLs to an anonymous visitor anyway; the catalog simply does not advertise them.
- **`capabilities` is the list of keys of the release's capability manifest.** The table view shows them as columns.

The run reported `100 listed apps (7 for subscribers, 94 with covers), 125 tags`. The file is 87,449 bytes and is served with Brotli compression. `views.json` lists the views for the switcher, as `{id, title, path, blurb}`.

## 5. The kit

`apps/catalog/kit/views.js` defines one global, `SlopCatalog`. A view page includes it with `views.css` and calls three things:

```js
const { catalog } = await SlopCatalog.load();         // fetches catalog.json and views.json once
await SlopCatalog.header(document.querySelector("#head"), "list");   // name, count, switcher, search
SlopCatalog.viewer.bind(catalog);                     // ?open=<id> opens the viewer
```

`header` renders the view switcher from `views.json` and marks the current view with `aria-current="page"`. Its search box writes `?q=` into the address and dispatches a `catalog:search` event, which each view handles with its own filter. `/` and ⌘K focus the box. The helpers (`el`, `bytes`, `date`, `monogram`, `matches`) keep each view page short: the index is 116 lines and the table 105, CSS included.

### 5.1 The viewer's state and the address bar

The viewer keeps its state in the URL, so a link to an open app can be shared:

```js
open(item)  { u.searchParams.set("open", item.id); history.pushState({open: item.id}, "", u); this.show(item); }
close()     { if (history.state && history.state.open) history.back(); else history.replaceState(null, "", u); this.hide(); }
bind()      { addEventListener("popstate", () => this.sync()); addEventListener("keydown", Esc → close); this.sync(); }
sync()      { id = params.get("open"); item ? this.show(item) : this.hide(); }
```

Opening pushes a history entry, so Back closes the viewer. A page loaded with `?open=` has no such entry to go back to, so closing it replaces the URL instead.

### 5.2 Sizing the device

The preview must lay out as it would on the device, which means the iframe keeps the device's real CSS size. A phone is 390×844 CSS pixels, a tablet 820×1180 and a desktop 1280×800. It is then scaled down to the stage:

```js
const s = Math.min(1, (stage.clientWidth - 40) / w, (stage.clientHeight - 40) / h);
device.style.transform = `scale(${s})`;
device.style.margin = `${-(h * (1 - s)) / 2}px ${-(w * (1 - s)) / 2}px`;
```

`transform` does not change the space an element occupies in layout, so the negative margins remove the area the unscaled box would otherwise still reserve. `s` never exceeds 1, so a small preview is not enlarged. The viewer's bar shows the result, for example `1280 × 800 · 45%`.

### 5.3 The preview and its isolation

The first version set the iframe's `src` to the app's `/_s/` URL and sandboxed it with `allow-scripts allow-forms allow-modals`. The attribute that matters is the one left out: without `allow-same-origin`, the document gets an **opaque origin**. It cannot reach the catalog page through `window.parent`, and it cannot read the site host's storage, which every static site on that host shares. `referrerpolicy="no-referrer"` keeps the catalog's URL from the app.

That isolation broke some apps. Lattice Arena, which declares `db, downloads, sample, user`, rendered a blank frame at phone size. Its HTML reads storage while starting:

```
localStorage.getItem(PREFS_KEY) || '{}'
localStorage.setItem(this.key(name), JSON.stringify(…
```

In an opaque origin the `localStorage` getter throws a `SecurityError`, and the app stops before drawing anything. The error happens inside the cross-origin frame, where Playwright's console listing collects nothing (`Total messages: 0`). The diagnosis therefore came from reading the HTML.

The fix keeps the isolation and changes how the document arrives. The viewer fetches the HTML itself (same origin, so allowed), inserts two elements after `<head>`, and passes the result as `srcdoc`:

```js
const SHIM = "(" + function () {
  function mem() {
    const m = new Map();
    return { getItem: (k) => (m.has(String(k)) ? m.get(String(k)) : null),
             setItem: (k, v) => { m.set(String(k), String(v)); },
             removeItem: (k) => { m.delete(String(k)); }, clear: () => m.clear(),
             key: (i) => [...m.keys()][i] ?? null, get length() { return m.size; } };
  }
  for (const name of ["localStorage", "sessionStorage"]) {
    try { void window[name].length; } catch (e) {
      try { Object.defineProperty(window, name, { value: mem(), configurable: true }); } catch (e2) {}
    }
  }
} + ")();";

// in previewDoc(item):
const base = new URL(item.preview, location.href).href.replace(/[^/]*$/, "");
const head = `<base href="${base}"><script>${SHIM}<\/script>`;
// inserted right after the document's <head> tag; the result becomes frame.srcdoc
```

- **`<base>`** makes the app's relative URLs resolve against its own files under `/_s/<id>/main/`, as they did when the iframe pointed at the file.
- **The shim** replaces a storage object only when touching it throws. A browser that permits storage in opaque origins is left alone.
- **`window.claude` stays absent.** Apps written for claude.ai test for it. After the fix, Lattice Arena renders at phone size and says "3 robots staged. Claude is not available here, so robots use the scripted planner."

The preview quality therefore falls into three levels:

| App behaviour | Preview |
| --- | --- |
| starts without storage or the runtime (Weft, Claude.Computer) | runs fully |
| reads or writes storage while starting (Lattice Arena) | runs, with storage that lasts until the viewer closes |
| needs `window.claude` for its core | shows its own "not available" state; "Open" runs it for real |

A paid app is never previewed. The viewer shows its cover, or a monogram when there is no cover, and the note "This app is for subscribers; sign in when you open it."

## 6. The two views

**The index** (`apps/catalog-list/`) shows a headline, a sort control, and a tag bar. With 125 tags, it shows the 14 most common plus a "+111 more" toggle. Each row has a lazy-loaded cover, the title, a "subscribers" mark when the app is paid, the description, tags, and the actions View and Open ↗ with the path, size and version. Sort and tag are kept in the query string, so a filtered index can be linked.

**The table** (`apps/catalog-table/`) has one row per app. Its columns are the title with a one-line description, one column each for `sample`, `db`, `room`, `user` and `downloads` (● or ·), access, version, published date, size and attachment count. Clicking a header sorts by that column, and clicking it again reverses the order; the state is kept as `?by=&dir=`. A "needs" filter keeps only apps that declare every selected capability. A row opens the viewer, and so does Enter on a focused row. The capability columns make visible a fact the import established: all 100 apps use `sample`, and only a minority use `db`, `room` or `user`.

## 7. Deploying content, not code

The views are content. Deploying them changes stores, not the slop binary, so no image build or GitOps change is involved. `scripts/02-deploy.py` handles three stores. For each one, the dry run, which is the default, prints the plan:

```
catalog        store.new, files.push (5 changed: data/catalog.json, data/views.json, index.html, kit/views.css, kit/views.js), grant.set @guest view, mount.set site.slop.yolo.scapegoat.dev/catalog
catalog-list   store.new, files.push (1 changed: index.html), grant.set @guest view, mount.set site.slop.yolo.scapegoat.dev/catalog/list
catalog-table  store.new, files.push (1 changed: index.html), grant.set @guest view, mount.set site.slop.yolo.scapegoat.dev/catalog/table
```

With `--apply` it performs those calls. It pushes only when the tree differs from `files.ls` by path and SHA-256, the comparison SLOP3-013's importer also uses. It refuses to replace a mount that points at a different store. After the third deploy, a dry run reports `up to date` for all three stores, which shows that production matches the repository.

### 7.1 Versioned kit URLs

The second production problem was about time. After a fix to `views.js` was deployed, the browser kept running the previous version: the preview iframe still had a `src` attribute and an empty `srcdoc`. The static host's header explains it:

```
cache-control: public, max-age=60, stale-while-revalidate=600
```

A browser may use the file without asking for 60 seconds, and may then serve the stale copy for up to 600 more seconds while it checks in the background. A changed kit could therefore reach a returning visitor up to 11 minutes late. Shortening those lifetimes would affect every site on the host, which is a platform decision. Instead the deploy script gives every changed kit a new URL:

```python
KIT = ("kit/views.js", "kit/views.css")

def stamps(repo):
    out = {}
    for k in KIT:
        b = pathlib.Path(repo, "apps/catalog", k).read_bytes()
        out[f'"/catalog/{k}"'] = f'"/catalog/{k}?v={hashlib.sha256(b).hexdigest()[:12]}"'.encode()
    return out
```

When it copies an HTML page, it replaces the quoted kit paths with the stamped ones. `serveStatic` resolves files by `r.URL.Path`, so the query string does not change which file is served; it only changes the cache key. Production now serves `views.js?v=793e71cf135a` and `views.css?v=86942171e22c`. The repository's pages keep the plain paths, so they work unchanged in the local preview and the test.

### 7.2 Latency and the loading state

The first visits showed empty pages for a second or two. Measured from the development machine, the static host answered `/catalog/list/` with a time to first byte of 0.59 s, and `/healthz` showed where the time goes: `connect 0.24 s, tls 0.37 s, ttfb 0.48 s`. Most of it is network distance, not server work. Because every view waits for `catalog.json` before rendering, each page now contains a static "Loading the catalog…" paragraph that the first render replaces.

## 8. Testing

`pkg/host/catalog_views_test.go` (`TestCatalogViewsOnStaticHost`) runs the real server in-process. It pushes the three stores from the repository's `apps/` directories, with a two-line `catalog.json`, then grants and mounts them, and checks:

- each of `/catalog/`, `/catalog/list/`, `/catalog/table/`, `/catalog/kit/views.js`, `/catalog/kit/views.css` and `/catalog/data/catalog.json` returns 200 from the right store;
- no page has `/_slop/claude.js` injected, so it stays a static page;
- both views load the kit from the catalog mount;
- `/catalog/list` without its slash returns 308 to `/catalog/list/`, which is what makes relative URLs resolve under the mount;
- removing `@guest view` from `catalog-table` turns `/catalog/table/` into a 404.

The browser behaviour (sorting, filtering, the viewer at three sizes, Esc and Back, the paid-app path) was checked with Playwright: first against a local preview server (`scripts/03-devserve.py`, which maps the mounts to the repository and passes `/_d/` and `/_s/` through to production), then on production. Three screenshots appeared to show failures that were not real: blank covers, an empty landing page, and a list still "Loading" while the viewer was open. In each case `browser_evaluate` showed the DOM was correct (images `complete` with real widths, 100 rows present), and the screenshot had been taken mid-load. Checking the DOM before concluding that something was broken avoided three wrong fixes.

## 9. What this shows about slop

The project took one session and touched no server code. That was the claim being tested: a store is the unit of content, a mount is the unit of publication, and grants decide visibility. Under those rules, "several interfaces over one catalog" is just several stores. Each view is an `index.html` of about a hundred lines. Adding a fourth view means writing that file, adding one line to `views.json` and one line to the deploy script's list.

The constraints were the useful part:

- **Not being able to frame the shell** forced an honest preview design, and the storage shim restored most of what the isolation took away without weakening it.
- **The cache lifetimes** forced content-addressed URLs, which a static site needs sooner or later anyway.
- **The paid apps' grants from SLOP3-013** meant the catalog could not leak their HTML even if it tried: the static host returns 404 to anonymous visitors.

## 10. Open questions

- **Running previews** would need an admin-only, per-mount allowance for the live shell to be framed by a named static mount. That needs its own threat model, because the static host serves pages other people control.
- **Cover thumbnails:** covers are original PNGs up to 2,736 pixels wide. slop v2 had a thumbnail service (SLOP-012) that v3 does not.
- **Views for agents:** `llms.txt`, `search-index.json`, a read-only MCP endpoint and an `/agents` page follow once #31 and #32 let an actor answer HTTP requests on a mount. The catalog could then also rebuild itself on an alarm instead of by hand.

## Notes on the implementation record

The ticket is SLOP3-015 in `slop-computer`, at `ttmp/2026/11/06/SLOP3-015--catalog-views-…/`. It holds:

- the intern guide (uploaded to reMarkable, with a second version after the fixes);
- the diary, steps 1–2;
- the scripts `01-build-catalog.py`, `02-deploy.py` and `03-devserve.py`;
- the evidence in `various/`: the catalog snapshot, the deploy logs and six screenshots.

The commits are `659f43c` (ticket and guide), `5ff4fc0` (kit, views, builder and test), `c69d4f8` (deploy, the `srcdoc` preview, loading states and versioned URLs), `8e839c0` and `a727fac`, all on branch `task/slop3-015-catalog-views`, pull request #35.

## Related notes

- [[PROJECT REPORT - slop v3 - Importing the francois Catalog - Real Releases, Verbatim Capabilities and Paid Access - A Technical Deep Dive]]
- [[PROJECT REPORT - slop v3 - Per-App Modules Part 2 - The Module Catalog, Configured Grants and an In-Memory fs - A Technical Deep Dive]]
