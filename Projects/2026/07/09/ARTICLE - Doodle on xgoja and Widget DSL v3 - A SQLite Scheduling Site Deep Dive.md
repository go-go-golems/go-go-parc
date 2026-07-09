---
title: "Doodle on xgoja and Widget DSL v3: A SQLite Scheduling Site Deep Dive"
aliases:
  - Doodle xgoja Widget DSL v3 Deep Dive
  - Doodle Scheduling Site Report
  - DOODLE-WIDGETDSL-V3 report
  - SQLite Doodle Widget DSL
  - Doodle widget.dsl v3 migration
_tags: []
tags:
  - article
  - project-report
  - xgoja
  - sqlite
  - widget-ir
  - ui-dsl
  - javascript
  - go
  - scheduling
status: active
type: article
created: 2026-07-09
repo: /home/manuel/workspaces/2026-07-03/improve-rag-evaluation-system/rag-evaluation-system
source_tickets:
  - DOODLE-1
  - DOODLE-WIDGETDSL-V3
related_commits:
  - 39e455f
---

# Doodle on xgoja and Widget DSL v3: A SQLite Scheduling Site Deep Dive

This article documents the Doodle-style scheduling site built inside `rag-evaluation-system` and the later migration that turned it from a legacy split-module Widget DSL example into a clean `widget.dsl` v3 application. The system is small enough to understand in one sitting, but it exercises the important boundaries of the stack: xgoja provider selection, SQLite persistence, planned-route HTTP handlers, Widget IR page generation, native form POSTs, the embedded React SPA, the v3 UI/data/schedule DSL namespaces, migration checking, and browser validation.

The reference implementation lives at `examples/xgoja/doodle-site`. The primary application source is `examples/xgoja/doodle-site/verbs/doodle.js`; the xgoja build spec is `examples/xgoja/doodle-site/xgoja.v2.yaml`; the relevant follow-up work is recorded in the tickets `DOODLE-1` and `DOODLE-WIDGETDSL-V3` under `ttmp/2026/07/`.

> [!summary]
> - The Doodle site is a file-backed SQLite scheduling application compiled as a custom xgoja binary. It serves a Widget IR API and an embedded React SPA from one executable.
> - The first implementation proved the product flow with legacy `ui.dsl` and `data.dsl`: create poll, list polls, vote on availability, compute tallies, and persist data across restarts.
> - The v3 migration replaced split modules with a single `widget.dsl` import, then removed raw component escape hatches by adding typed v3 UI helpers and using `widget.schedule.availabilityPoll` / `widget.schedule.pollSummary`.
> - The final Doodle source has zero legacy Widget DSL imports and zero raw component escape hatches according to the parser-backed migration checker.

## Why this project exists

The Doodle project exists to answer a concrete integration question: can a small product-shaped web application be built from xgoja modules, SQLite, the Widget DSL provider, and the React WidgetRenderer without a separate backend service or a custom React application? The answer is yes. The resulting application is not a mock page. It has persistent storage, HTTP routes, form submissions, redirects, generated Widget IR pages, and browser-validated interactions.

The project also became a migration test for `widget.dsl` v3. The original Doodle implementation used the older split modules, `ui.dsl` and `data.dsl`. That was useful when the goal was to prove the xgoja + SQLite + Widget IR path. After the v3 DSL existed, Doodle became a better test of a different property: can the same app run on the new unified authoring surface, and can it do so without compatibility shims or raw component calls?

That second question mattered because `widget.dsl` v3 had already been proven through examples, golden IR, preview galleries, Storybook regressions, and the larger `go-go-course` host migration. Doodle added another form of proof: a compact application whose source is easy to read end to end and whose behavior can be checked with a browser in less than a minute.

## Final system overview

The final Doodle site is an xgoja-generated binary. The binary embeds JavaScript source, selected Go provider modules, an SQLite database module, an Express-like HTTP provider, and static SPA assets. At runtime it creates tables if needed, seeds one poll if the database is empty, serves three Widget IR pages, and accepts two native form POSTs.

The runtime boundaries are deliberately explicit:

- `xgoja.v2.yaml` selects providers and modules.
- `verbs/doodle.js` defines the JS verb, database schema, page builders, and HTTP routes.
- `assets/public/` contains the SPA bundle rendered by `RagEvaluationSiteApp`.
- `dist/doodle-site` is the generated binary.
- `doodle.db` is the runtime SQLite file.

The important property is that page rendering is data-driven. The JavaScript code does not render HTML directly for the application pages. It constructs Widget IR through `widget.dsl`; the browser SPA fetches the IR and renders it with the React widget system. Native forms are the exception: form components are represented in Widget IR, but their submit behavior uses normal browser POST requests to host routes.

## xgoja build configuration

The build spec is `examples/xgoja/doodle-site/xgoja.v2.yaml`. The spec uses the v2 xgoja schema and `workspace.mode: auto`, which lets the build resolve local workspace modules during development. The relevant provider list is:

- `go-go-goja-host`, which supplies host-side facilities such as embedded files and the SQLite-backed `db` module.
- `go-go-goja-http`, which supplies the planned-route Express API and the `serve` command set.
- `rag-widget-site`, which supplies the Widget DSL module and the SPA help/assets integration.

The final module selection matters:

```yaml
runtime:
  modules:
    - provider: go-go-goja-http
      name: express
      as: express
    - provider: go-go-goja-host
      name: fs
      as: fs:assets
    - provider: go-go-goja-host
      name: db
      as: db
    - provider: rag-widget-site
      name: widget.dsl
      as: widget.dsl
```

The earlier implementation selected `ui.dsl` and `data.dsl`. The v3 migration intentionally changed this to one module: `widget.dsl`. That single import is now the top-level namespace for page construction, action creation, generic UI nodes, typed data collections, and scheduling widgets.

The SQLite module is configured as:

```yaml
config:
  driverName: sqlite3
  dataSourceName: 'file:doodle.db?_foreign_keys=on'
```

That makes persistence visible during development. Polls and votes survive server restarts because the database is not in memory. This is important for a scheduling app: persistence is not an optional detail when validating the whole product flow.

## The application model

Doodle uses four tables:

```sql
CREATE TABLE IF NOT EXISTS polls (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  slug TEXT UNIQUE,
  title TEXT NOT NULL,
  description TEXT,
  location TEXT,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS options (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  poll_id INTEGER NOT NULL,
  label TEXT NOT NULL,
  sort INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS participants (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  poll_id INTEGER NOT NULL,
  name TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS votes (
  participant_id INTEGER NOT NULL,
  option_id INTEGER NOT NULL,
  value TEXT NOT NULL,
  PRIMARY KEY (participant_id, option_id)
);
```

This schema is intentionally direct. A poll owns options. A participant belongs to one poll. A vote joins one participant to one option and stores one of three values: `yes`, `maybe`, or `no`. The result table is not persisted because it is derived from votes.

The initial seed creates a poll called `Team offsite dinner` with four candidate times and three participants. This seed is only inserted when the database has no polls. That makes the first browser load useful while preserving any data created during later manual testing.

## HTTP routes and page routes

The HTTP layer uses the planned-route Express API:

```javascript
app.get(pattern).public().handle((ctx, res) => ...)
app.post(pattern).public().handle((ctx, res) => ...)
```

The migration diary records an important discovery: the older two-argument Express form, `app.get(path, handler)`, has been removed in the local `go-go-goja` workspace and panics. Doodle therefore uses only the planned-route API.

The route set is small:

| Route | Method | Purpose |
| --- | --- | --- |
| `/` and static paths | GET | Serve embedded SPA assets through `spaFromAssetsModule` |
| `/healthz` | GET | Return `{ ok: true, site: "doodle-site" }` |
| `/api/widget/pages/index` | GET | Return the Widget IR for the poll list page |
| `/api/widget/pages/create` | GET | Return the Widget IR for the create-poll page |
| `/api/widget/pages/poll?poll=<id>` | GET | Return the Widget IR for one poll's voting/results page |
| `/api/form/create-poll` | POST | Create a poll and redirect to the poll page |
| `/api/form/cast-vote?poll=<id>` | POST | Insert a participant and votes, then redirect back to the poll page |

The SPA forwards the page query string to the Widget IR fetch. This is why `/pages/poll?poll=3` becomes `/api/widget/pages/poll?poll=3`, and the route handler can read `ctx.request.query.poll`.

## Page construction with `widget.dsl` v3

The final source imports a single module:

```javascript
const widget = require("widget.dsl");
```

The page helpers are organized around v3 namespaces:

- `widget.page(...)` creates a page builder.
- `widget.act.navigate(...)` creates navigation actions.
- `widget.ui.*` creates buttons, forms, form rows, inputs, status text, captions, inline groups, and empty states.
- `widget.data.fields(...)` and `widget.data.collection(...)` build typed tables.
- `widget.schedule.availabilityPoll(...)` renders the participant-by-slot availability matrix.
- `widget.schedule.pollSummary(...)` renders summarized counts per slot.

Doodle defines small local helpers such as `statusText`, `emptyState`, `formRow`, `textInput`, and `selectInput`, but these are only aliases around typed v3 APIs. They are not raw component builders.

The `applyPageMeta` helper attaches common navigation metadata:

```javascript
function applyPageMeta(p, id, activeNavItemId) {
  return p
    .id(id)
    .meta("activeNavItemId", activeNavItemId)
    .meta("navItems", navItems)
    .meta("maxWidth", "wide");
}
```

This keeps page metadata consistent across `index`, `create`, and `poll`. The page functions then focus on the page-specific data and sections.

## The index page

The index page queries all polls and computes top-level metrics:

- number of active polls,
- total participant responses,
- total time slots.

It renders four sections:

1. an introductory scheduling-polls section with a status node and a primary `+ New poll` navigation button;
2. a metrics section using section-level metric calls;
3. a table of polls built with `widget.data.collection`;
4. a set of navigation buttons for opening existing polls.

The table schema is declared close to the data transformation:

```javascript
const table = collectionTable(
  "polls",
  rows,
  (f) =>
    f
      .key("id", { label: "ID" })
      .primary("title", { label: "Poll" })
      .short("location", { label: "Where" })
      .count("slots", { label: "Slots" })
      .count("people", { label: "Responses" })
      .date("created", { label: "Created" }),
  { empty: "No polls yet" },
);
```

This is the v3 replacement for the older `data.dataTable` authoring style. The schema is explicit and typed by field role, while the rendered result remains normal Widget IR consumed by the existing React table renderer.

## The create page

The create page renders a native POST form through `widget.ui.form`. It has inputs for title, description, location, and one time slot per line. The form posts to `/api/form/create-poll`.

The handler parses line-separated slots, rejects an empty title or empty slot list by redirecting back to `/pages/create`, inserts the poll, inserts each option with a stable sort index, and redirects to `/pages/poll?poll=<id>`.

This design keeps mutation behavior host-native. There is no client-side state protocol and no custom JavaScript in the browser. The browser submits a form; the xgoja route mutates SQLite; the redirect causes the SPA to load the updated page state.

## The poll page

The poll page is the main scheduling screen. It performs these steps:

1. load the poll record;
2. load options, participants, and votes;
3. build a `voteMap` keyed by participant ID and option ID;
4. normalize Doodle-specific vote values into the generic schedule availability contract;
5. compute per-slot tallies and scores;
6. construct the availability matrix, summary grid, result table, and availability form.

The normalization step is important:

```javascript
function availabilityValue(value) {
  if (value === "yes") return "available";
  if (value === "no") return "unavailable";
  if (value === "maybe") return "maybe";
  return "unknown";
}
```

The database stores Doodle terms (`yes`, `maybe`, `no`) because those are the terms submitted by the native form and understood by the result scoring logic. The generic schedule widget expects `available`, `maybe`, `unavailable`, or `unknown`. The final design does not force the persistence model to change. It adapts values at the view boundary.

The schedule-facing object looks like this:

```javascript
const availabilityPoll = {
  title: poll.title,
  options: options.map((opt) => ({ id: String(opt.id), label: opt.label })),
  responses: participants.map((pt) => {
    const availability = {};
    options.forEach((opt) => {
      availability[String(opt.id)] = availabilityValue(
        (voteMap[pt.id] && voteMap[pt.id][opt.id]) || "",
      );
    });
    return { id: String(pt.id), name: pt.name, availability };
  }),
};
```

That object feeds two scheduling components:

```javascript
const availabilityGrid = widget.schedule.availabilityPoll(availabilityPoll, (b) =>
  b.readOnly(),
);

const summaryGrid = widget.schedule.pollSummary(availabilityPoll, summaryTallies);
```

The result table is still a generic data table because it contains Doodle-specific scoring and best-slot status:

- score = `yes * 2 + maybe`,
- `verdict = succeeded` for each top-scoring slot when at least one response exists,
- `verdict = pending` otherwise.

That split is the correct final state for now. The schedule widgets display reusable scheduling state. The data table displays product-specific score semantics.

## Original implementation findings

The original `DOODLE-1` work surfaced several practical integration details.

First, the locally available `xgoja` accepted only v2 specs. The example therefore had to use `schema: xgoja/v2`. That also meant the spec had to be structured around `providers`, `runtime.modules`, `sources`, `commands`, and `artifacts` in the v2 shape.

Second, the local `go-go-goja` workspace had already removed the older Express two-argument route API. This was not a documentation-only difference; using the old API would panic at runtime. The Doodle code therefore established the planned-route API as the correct pattern for current xgoja examples.

Third, query forwarding from SPA page routes to Widget IR API routes worked as required. This allowed `/pages/poll?poll=<id>` to remain a normal, shareable browser URL while still fetching the right Widget IR from `/api/widget/pages/poll?poll=<id>`.

Fourth, the first browser run found a stale embedded SPA bundle. The stale bundle did not know about some widgets used by the initial implementation and rendered errors such as `Unsupported cell` and `Unknown widget: FormPanel`. Rebuilding the current `packages/rag-evaluation-site` app bundle and syncing it into the Doodle assets fixed the mismatch. This was a real integration bug: API JSON correctness was not enough because the embedded frontend had to support the emitted IR.

Fifth, the original form controls had default read-only behavior unless configured otherwise. Editable forms required explicit editable input configuration. The final v3 helpers make this path easier to express from the unified DSL.

## The v3 migration

The first v3 migration step changed Doodle from split modules to the unified `widget.dsl` import. The SQLite schema, seed data, HTTP routes, native form POST flow, redirects, and page semantics stayed the same. That was intentional: the migration should test the authoring layer, not redesign the app.

The initial v3 port still contained `widget.raw.component(...)` calls for gaps in the v3 helper surface: form rows, text input, textarea input, select input, status text, and empty state. That was acceptable as a transitional checkpoint, but it was not an acceptable final demo because it meant Doodle selected `widget.dsl` while still manually emitting component nodes.

The follow-up work fixed that by extending `widget.dsl` itself. The added typed helpers were:

- `widget.ui.formRow(...)`,
- `widget.ui.textInput(...)`,
- `widget.ui.textareaInput(...)`,
- `widget.ui.selectInput(...)`,
- `widget.ui.status(...)`,
- `widget.ui.emptyState(...)`.

The TypeScript declarations in `pkg/widgetdsl/typescript.go` were updated alongside the Go module implementation in `pkg/widgetdsl/v3.go`. Doodle was then rewritten to use these typed helpers. The availability table was also upgraded from a schedule-neutral data table to `widget.schedule.availabilityPoll`, and the per-slot count display added `widget.schedule.pollSummary`.

The result is a stronger example. Doodle now demonstrates several v3 namespaces in one file without raw component construction:

- UI composition for forms and buttons,
- data collection tables for poll and result lists,
- schedule-specific rendering for availability and summary views,
- navigation actions,
- page metadata.

## Why native forms remain in the final design

Doodle keeps native form POSTs instead of converting writes into Widget DSL server actions. This is not a failure to use the DSL. It is a deliberate boundary choice for this example.

Native forms provide a clear end-to-end path:

1. Widget IR declares form structure.
2. The SPA renders the form.
3. The browser submits `application/x-www-form-urlencoded` data.
4. The xgoja host route parses `ctx.body`.
5. SQLite is updated.
6. The route redirects.
7. The SPA fetches fresh Widget IR for the redirected page.

This keeps mutation semantics observable and easy to debug. It also avoids inventing an action transport just for the example. The app still exercises Widget IR for rendering, and it still uses v3 typed components for the form controls.

## Validation performed

The implementation and migration were validated at several levels.

Build and module checks:

```bash
cd examples/xgoja/doodle-site && make build
cd examples/xgoja/doodle-site && make list-modules
```

The final module list shows `widget.dsl` rather than legacy `ui.dsl` / `data.dsl` modules.

Widget DSL and provider tests:

```bash
go test ./pkg/widgetdsl/... ./pkg/xgoja/providers/widgetsite/... -count=1
```

Migration checker:

```bash
go run ./cmd/widgetdsl-migration-checker -- examples/xgoja/doodle-site/verbs examples/xgoja/doodle-site/xgoja.v2.yaml
```

Final result:

```text
No legacy Widget DSL imports or raw component escape hatches found.
```

Browser validation covered the real application flow:

1. run the generated server on `127.0.0.1:18793`;
2. open `/pages/create`;
3. fill in a new poll;
4. submit the form;
5. arrive at `/pages/poll?poll=<new-id>`;
6. submit participant availability;
7. verify that the availability matrix, summary grid, score table, and best-slot status update;
8. check that the browser console has no new warnings or errors.

This is the right validation scope for Doodle. A JSON page smoke test can confirm that handlers return valid IR, but only the browser can prove that the embedded SPA, form behavior, redirects, schedule widgets, and table rendering work together.

## Current source map

Start with these files when reviewing or changing Doodle:

- `examples/xgoja/doodle-site/verbs/doodle.js` — application source, schema, seed data, queries, page builders, HTTP routes.
- `examples/xgoja/doodle-site/xgoja.v2.yaml` — provider and runtime module selection.
- `examples/xgoja/doodle-site/Makefile` — build, serve, and asset-sync workflow.
- `examples/xgoja/doodle-site/README.md` — run instructions and high-level description.
- `pkg/widgetdsl/v3.go` — implementation of the v3 DSL helpers used by Doodle.
- `pkg/widgetdsl/typescript.go` — TypeScript declarations for the v3 helper surface.
- `packages/rag-evaluation-site/src/scheduling/index.ts` and `packages/rag-evaluation-site/src/scheduling/types.ts` — schedule component exports and DTO contracts.
- `ttmp/2026/07/07/DOODLE-1--doodle-style-scheduling-site-on-sqlite-via-rag-widget-dsl-xgoja/` — original implementation diary and task records.
- `ttmp/2026/07/09/DOODLE-WIDGETDSL-V3--port-doodle-scheduling-example-to-widget-dsl-v3/` — v3 migration plan, diary, tasks, and changelog.

## Design decisions

### Keep persistence product-specific

The database stores `yes`, `maybe`, and `no`. The schedule widget displays `available`, `maybe`, `unavailable`, and `unknown`. The final design keeps these separate and normalizes only at render time. That prevents a generic UI contract from leaking into the storage model.

### Use a schedule widget for the availability matrix

The availability matrix is a reusable scheduling concept. It should not be rebuilt as a generic table when the schedule namespace already has a component for this shape. Moving to `widget.schedule.availabilityPoll` makes the demo more representative of the v3 scheduling layer.

### Keep the score table as a data table

The score table is product-specific. The formula `yes * 2 + maybe` is Doodle behavior, not a generic scheduling primitive. Keeping it as a `widget.data.collection` table is clearer than forcing it into the schedule namespace.

### Add typed v3 helpers instead of hiding raw calls locally

The v3 port initially exposed missing helper coverage. The correct fix was not to keep local raw wrappers in Doodle. The correct fix was to add the missing helpers to `widget.dsl` and update its TypeScript declarations. That turns the example into proof of the public API rather than proof of a compatibility escape hatch.

### Validate with a browser before calling the migration done

The stale-SPA failure in the original implementation showed that backend IR generation can pass while the actual embedded frontend fails. Doodle's acceptance criteria therefore include browser interaction, not only build and API checks.

## Remaining follow-ups

The Doodle migration is complete for its stated goal: it is a raw-free `widget.dsl` v3 scheduling example with validated create/vote flows. There are still useful follow-ups:

- Add small standalone v3 fixture examples for the new UI helpers (`formRow`, `status`, `emptyState`, text inputs, textarea, select) so they are covered outside Doodle.
- Consider a schedule-specific result component if more apps need score/best-slot result summaries.
- Consider custom labels or glyph hooks in `schedule.availabilityPoll` so product terminology like `yes/no` can be displayed without changing the generic schedule state contract.
- Keep the embedded SPA assets fresh whenever emitted Widget IR starts using newly added frontend components.

## Conclusion

Doodle is now a compact reference application for the current Widget DSL stack. It demonstrates how to build a persistent scheduling workflow with xgoja, SQLite, planned-route HTTP handlers, an embedded React SPA, and `widget.dsl` v3. It also records a practical migration path: first port the module selection and page construction, then eliminate raw component escape hatches by promoting repeated needs into typed DSL helpers, then validate the result in a real browser.

The final outcome is stronger than a documentation example because it is executable and stateful. It verifies that the DSL can support a normal application workflow: list data, create records, render detail pages, collect input, update persistence, recompute derived results, and keep navigation stable through shareable page URLs.
