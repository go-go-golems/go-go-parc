---
title: "Fringe Go Host Modules Walkthrough"
aliases:
  - Fringe Go Host Modules Report
  - HAIR-036 Host Modules Walkthrough
  - Goja Host Modules for Hair Booking
  - Fringe DSL Upload Testing Guide
_tags_note: "Tags use Obsidian-compatible strings; keep project-report for PARC indexing."
tags:
  - project-report
  - article
  - go
  - goja
  - dsl
  - sqlite
  - uploads
  - auth
  - server-driven-ui
status: active
type: project-report
created: 2026-05-13
repo: /home/manuel/workspaces/2026-04-21/hair-v2/hair-booking
source_tickets:
  - HAIR-036
related_docs:
  - /home/manuel/workspaces/2026-04-21/hair-v2/hair-booking/ttmp/2026/05/13/HAIR-036--go-host-modules-for-backend-driven-dsl-runtime/design-doc/01-go-host-modules-for-the-fringe-goja-dsl-runtime-db-images-and-user-context.md
  - /home/manuel/workspaces/2026-04-21/hair-v2/hair-booking/ttmp/2026/05/13/HAIR-036--go-host-modules-for-backend-driven-dsl-runtime/reference/01-diary.md
  - /home/manuel/workspaces/2026-04-21/hair-v2/hair-booking/ttmp/2026/05/13/HAIR-036--go-host-modules-for-backend-driven-dsl-runtime/tasks.md
updated: 2026-05-13
---

# Fringe Go Host Modules Walkthrough

This report explains the HAIR-036 host-module work in the Fringe hair-booking repository. It is both a project report and a walkthrough. The goal is to make the system understandable enough that a future engineer can inspect the code, run the upload smoke test, and continue the implementation without reconstructing the design from scattered commits.

The repository is:

```text
/home/manuel/workspaces/2026-04-21/hair-v2/hair-booking
```

The work described here moves the backend-driven Goja DSL runtime from a self-contained page-rendering prototype toward a host-integrated application runtime. The core idea is simple: JavaScript should continue to own application-level flow behavior, while Go should expose carefully scoped plumbing primitives for durable and privileged operations. HAIR-036 adds the first three host surfaces: SQLite access through `require("db")`, user identity through `require("host/user")`, and image upload plumbing through `require("host/images")`.

> [!summary]
> HAIR-036 adds server-side host modules to the Goja DSL runtime. JavaScript can now require `db`, `host/user`, and `host/images` while still emitting the same backend-driven DSL pages.
>
> The SQLite database is configured by Glazed serve flags, provisioned by an embedded schema, and passed into the Goja runtime as a preconfigured go-go-goja database module.
>
> The upload path is split into two operations. JavaScript creates an upload intent during page render; the browser uploads a file to a session-scoped endpoint; the browser then dispatches an `uploaded` DSL event so the Goja flow can update state and rerender.
>
> The most useful real-system test is a curl smoke test that starts the DSL, navigates to the photos page, extracts an upload URL from the page JSON, uploads a tiny image, dispatches the uploaded event, and verifies SQLite metadata.

## 1. Why host modules exist

The backend-driven DSL runtime already had a strong interaction model before HAIR-036. A Go server starts a Goja VM, loads `pkg/dslgoja/flows/intake.flow.js`, renders a page, and returns protobuf JSON `FlowState` to the browser. The browser renders the page and posts interaction events back to Go. Go dispatches those events to page-version-scoped callbacks registered by the JavaScript flow.

That model is enough for stateful navigation, but it is not enough for a real application. A production intake flow must persist drafts, attach photos, read identity, schedule work, send notifications, query availability, and create appointments. Those operations are not ordinary page-state mutations. They touch storage, databases, authentication, file systems, and external systems. JavaScript should be able to request these operations, but it should not own their low-level mechanics.

The host-module boundary gives the runtime a disciplined way to separate responsibilities.

- JavaScript owns page composition, product flow, branching, copy, and app-level state decisions.
- Go owns database connections, schema provisioning, file validation, storage keys, upload limits, user/session resolution, and host invariants.
- The browser receives data. It does not receive Goja callbacks or trusted implementation names; it receives opaque action ids and upload intents.

This is the conceptual center of HAIR-036. The host modules are not app-specific modules such as `fringe/intake.submitConsultation`. They are plumbing modules such as `db`, `host/user`, and `host/images`. Product behavior remains in JavaScript.

## 2. The system before HAIR-036

The important preexisting files are:

| File | Role |
| --- | --- |
| `pkg/dslgoja/runtime.go` | Owns `Runtime`, `FlowSession`, render/dispatch lifecycle, action registry, stale action handling, and page export. |
| `pkg/dslgoja/modules_dsl.go` | Defines the JavaScript `fringe/dsl` builder module used by flow scripts. |
| `pkg/dslgoja/flows/intake.flow.js` | The real backend-authored intake flow. It renders service, color, photos, budget, estimate, booking, and confirm pages. |
| `pkg/server/handlers_dsl.go` | HTTP handlers for start/get/event DSL endpoints. |
| `proto/fringe/dsl/v1/dsl.proto` | Protobuf transport schema for `FlowState`, `InteractionEvent`, `DslError`, `Page`, `Node`, and related messages. |
| `web/src/page-dsl/BackendDslPage.tsx` | Browser-side bridge that starts/fetches a backend flow and dispatches events. |
| `web/src/page-dsl/render.tsx` | React interpreter for DSL page JSON. |

Before HAIR-036, `pkg/dslgoja/modules_dsl.go` installed an inline `require` implementation that only knew about `fringe/dsl`. That worked for the first runtime because the only JavaScript module was the page builder. Host modules require a Go-owned module registry so Go can install modules with access to Go objects such as `*sql.DB`, `BlobStore`, and user snapshots.

The runtime shape before host modules was:

```text
Runtime.StartFlow(flowID, source)
  create goja.Runtime
  install fringe/dsl
  run intake.flow.js
  call initialState() if present
  call render(ctx)
  export page JSON
```

The runtime shape after host modules is:

```text
Runtime.StartFlow(flowID, source, WithUser(user))
  create FlowSession first
  attach user snapshot to session
  create goja.Runtime
  install require registry
    fringe/dsl
    host/user
    host/images
    db, if host DB exists
  run intake.flow.js
  call initialState() if present
  call render(ctx)
  export page JSON
```

The sequencing matters. `host/user` and `host/images` are session-scoped modules. They need access to the `FlowSession`, so the session must exist before modules are installed.

## 3. The architecture after HAIR-036

The host-module architecture is a set of explicit data paths from process startup to JavaScript runtime.

```mermaid
flowchart TD
  Serve[hair-booking serve]
  Flags[Glazed flags: dsl-sqlite-path, dsl-sqlite-migrate]
  DBOpen[pkg/dslhost.OpenDB]
  Schema[pkg/dslhost/schema.sql]
  HTTP[pkg/server.NewHTTPServer]
  Store[dslFlowStore]
  Runtime[dslgoja.Runtime]
  Session[FlowSession]
  Registry[goja_nodejs require.Registry]
  DBModule[require("db")]
  UserModule[require("host/user")]
  ImagesModule[require("host/images")]
  Flow[intake.flow.js]
  Page[protobuf FlowState page JSON]

  Serve --> Flags --> DBOpen
  DBOpen --> Schema
  DBOpen --> HTTP
  HTTP --> Store --> Runtime --> Session --> Registry
  Registry --> DBModule
  Registry --> UserModule
  Registry --> ImagesModule
  DBModule --> Flow
  UserModule --> Flow
  ImagesModule --> Flow
  Flow --> Page
```

The server owns the SQLite database lifetime. The command opens the DSL SQLite database, defers its close, and passes the `*sql.DB` down into `server.ServerOptions`. The server constructs `dslFlowStore`, and `dslFlowStore` constructs `dslgoja.Runtime` with `dslgoja.WithHost(...)`. The runtime does not open databases. It receives dependencies.

This is the first rule of the implementation: host modules are installed by the runtime, but host resources are owned by the server process.

## 4. Startup configuration and SQLite provisioning

The entry point for serving the app is:

```text
cmd/hair-booking/cmds/serve.go
```

HAIR-036 adds two Glazed flags to the existing `serve` command:

```text
--dsl-sqlite-path
--dsl-sqlite-migrate
```

The default path is defined in `pkg/dslhost`:

```go
const DefaultSQLitePath = "./var/fringe-dsl.sqlite"
```

The serve settings now include the host-module DB fields:

```go
type ServeSettings struct {
    ListenHost       string `glazed:"listen-host"`
    ListenPort       int    `glazed:"listen-port"`
    DSLSQLitePath    string `glazed:"dsl-sqlite-path"`
    DSLSQLiteMigrate bool   `glazed:"dsl-sqlite-migrate"`
}
```

The command opens the host database before building the HTTP server:

```go
dslDB, err := dslhost.OpenDB(ctx, dslhost.DBOptions{
    Path:    settings.DSLSQLitePath,
    Migrate: settings.DSLSQLiteMigrate,
})
if err != nil {
    return errors.Wrap(err, "failed to open DSL SQLite database")
}
defer dslDB.Close()
```

Then it passes the database into server options:

```go
server.NewHTTPServer(serverCtx, server.ServerOptions{
    Host:             settings.ListenHost,
    Port:             settings.ListenPort,
    DSLSQLitePath:    dslDB.Path,
    DSLSQLiteMigrate: settings.DSLSQLiteMigrate,
    DSLDB:            dslDB.DB,
    Storage:          blobStore,
    // existing server dependencies...
})
```

This path is intentionally similar to the reference implementation in `/home/manuel/code/wesen/2026-05-03--goja-hosting-site`, where the Glazed `--db` flag flows into app config and then into a preconfigured go-go-goja database module. The hair-booking version keeps the existing server architecture and adds host-module dependencies to it.

### 4.1 The `pkg/dslhost` package

The new package is:

```text
pkg/dslhost/db.go
pkg/dslhost/schema.sql
pkg/dslhost/db_test.go
```

`pkg/dslhost` owns the SQLite host database lifecycle. It is small by design. Its job is not to model intake domain data. Its job is to provide a configured SQLite database with the starting host-module schema.

The main API is:

```go
type DBOptions struct {
    Path    string
    Migrate bool
}

type DBHost struct {
    DB   *sql.DB
    Path string
}

func OpenDB(ctx context.Context, opts DBOptions) (*DBHost, error)
func ProvisionSchema(ctx context.Context, db *sql.DB) error
func (h *DBHost) Close() error
```

`OpenDB` does five things:

1. It normalizes the path and applies the default if the caller passes an empty path.
2. It creates the parent directory for file-backed databases.
3. It opens SQLite with `github.com/mattn/go-sqlite3`.
4. It applies SQLite pragmas: foreign keys, busy timeout, and WAL for file-backed databases.
5. It provisions the embedded schema when `Migrate` is true.

The provisioning pseudocode is:

```text
OpenDB(ctx, options):
    path = options.Path or DefaultSQLitePath
    if path is not ":memory:":
        mkdir parent directory

    db = sql.Open("sqlite3", path)
    exec PRAGMA foreign_keys = ON
    exec PRAGMA busy_timeout = 5000
    if file-backed:
        exec PRAGMA journal_mode = WAL
    ping db

    if options.Migrate:
        schema = embedded schema.sql
        exec schema

    return DBHost{DB: db, Path: path}
```

The schema creates the first host-module tables:

```sql
CREATE TABLE IF NOT EXISTS dsl_flow_sessions (...);
CREATE TABLE IF NOT EXISTS dsl_intake_drafts (...);
CREATE TABLE IF NOT EXISTS dsl_uploads (...);
CREATE TABLE IF NOT EXISTS dsl_audit_events (...);
```

The tables are intentionally plumbing tables. They do not replace the product database. They support flow sessions, drafts, upload metadata, and audit records for the Goja DSL runtime.

## 5. Runtime host configuration

The runtime host boundary lives in:

```text
pkg/dslgoja/host.go
```

It introduces a `RuntimeHost` object:

```go
type RuntimeHost struct {
    DB        *sql.DB
    DBPath    string
    BlobStore storage.BlobStore
}

func WithHost(host RuntimeHost) RuntimeOption
```

This is the dependency injection point for host modules. The runtime can still be constructed without host modules:

```go
rt := dslgoja.NewRuntime()
```

and it can be constructed with host dependencies:

```go
rt := dslgoja.NewRuntime(dslgoja.WithHost(dslgoja.RuntimeHost{
    DB:        db,
    DBPath:    path,
    BlobStore: blobStore,
}))
```

This optionality matters for tests. Many runtime tests only need the `fringe/dsl` module and should not open SQLite. Host-module tests opt into host dependencies explicitly.

The server builds the runtime in `pkg/server/handlers_dsl.go`:

```go
func newDSLFlowStore(db *sql.DB, dbPath string, blobStore storage.BlobStore) *dslFlowStore {
    runtime := dslgoja.NewRuntime(dslgoja.WithHost(dslgoja.RuntimeHost{
        DB:        db,
        DBPath:    dbPath,
        BlobStore: blobStore,
    }))
    return &dslFlowStore{
        runtime:   runtime,
        db:        db,
        blobStore: blobStore,
        sessions:  map[string]*dslgoja.FlowSession{},
    }
}
```

The runtime itself is still the owner of Goja sessions and action lifecycle. The store owns the map of active sessions and holds server-side references needed by upload handlers.

## 6. Go-owned module registration

The most important structural change is in:

```text
pkg/dslgoja/modules_dsl.go
```

Before HAIR-036, the module file installed an inline JavaScript `require` function with a private module map. That made it difficult for Go to add session-aware modules. HAIR-036 replaces that with `goja_nodejs/require.Registry`:

```go
func (rt *Runtime) installModules(vm *goja.Runtime, session *FlowSession) error {
    registry := require.NewRegistry()
    registry.RegisterNativeModule("fringe/dsl", loadFringeDSLModule)
    registry.RegisterNativeModule("host/user", loadUserModule(session))
    registry.RegisterNativeModule("host/images", loadImagesModule(session))

    if rt.host.HasDB() {
        dbModule := databasemod.New(
            databasemod.WithName("db"),
            databasemod.WithPreconfiguredDB(rt.host.DB),
            databasemod.WithConfigureEnabled(false),
        )
        registry.RegisterNativeModule(dbModule.Name(), dbModule.Loader)
    }

    registry.Enable(vm)
    return nil
}
```

This is a transitional module registry. It is not a full move to `go-go-goja/engine.NewBuilder`, but it follows the same native module loader shape. The decision keeps the current long-lived `FlowSession` runtime intact while enabling native host modules.

### 6.1 Preserving `fringe/dsl`

`fringe/dsl` is now registered as a native module whose loader evaluates the existing JavaScript builder source and assigns the returned object to `module.exports`:

```go
func loadFringeDSLModule(vm *goja.Runtime, moduleObj *goja.Object) {
    value, err := vm.RunString(dslModuleSource)
    if err != nil {
        panic(vm.ToValue(fmt.Sprintf("install fringe/dsl: %v", err)))
    }
    _ = moduleObj.Set("exports", value)
}
```

The JavaScript flow still uses the same import:

```js
const { page, n } = require("fringe/dsl");
```

This preservation is essential. Host-module work should not force the flow script to change its page-builder vocabulary.

### 6.2 Explicit `toJSON()` during page export

The module registry refactor surfaced a page export detail. The DSL builder objects contain methods such as `id(...)`, `add(...)`, and `toJSON()`. If Go exports the builder object directly and passes it to `encoding/json`, Go may see function values and fail with:

```text
json: unsupported type: func(goja.FunctionCall) goja.Value
```

The fix is in `pkg/dslgoja/runtime.go`. Before Go marshals a rendered page value, it checks for a JavaScript `toJSON()` method and calls it explicitly:

```go
func exportPageValue(vm *goja.Runtime, value goja.Value) (Page, error) {
    if value != nil && !goja.IsNull(value) && !goja.IsUndefined(value) {
        obj := value.ToObject(vm)
        if toJSON, ok := goja.AssertFunction(obj.Get("toJSON")); ok {
            jsonValue, err := toJSON(value)
            if err != nil {
                return Page{}, err
            }
            value = jsonValue
        }
    }

    exported := value.Export()
    b, err := json.Marshal(exported)
    // unmarshal into dslgoja.Page
}
```

This makes page export independent of how Goja chooses to export method-bearing objects.

## 7. The database host module

The database module is provided by `github.com/go-go-golems/go-go-goja/modules/database`. HAIR-036 registers it as `require("db")` when a host DB is configured.

The registration uses:

```go
databasemod.New(
    databasemod.WithName("db"),
    databasemod.WithPreconfiguredDB(rt.host.DB),
    databasemod.WithConfigureEnabled(false),
)
```

The important option is `WithConfigureEnabled(false)`. JavaScript receives a database interface but cannot point it at a different database. The server process owns the database connection, and the Glazed CLI flags choose its path.

A representative JavaScript use looks like this:

```js
const db = require("db");

db.exec(
  "INSERT INTO dsl_audit_events(id, kind, payload_json) VALUES (?, ?, ?)",
  "evt_1",
  "host-db-test",
  JSON.stringify({ source: "goja" }),
);

const rows = db.query(
  "SELECT kind FROM dsl_audit_events WHERE id = ?",
  "evt_1",
);
```

The runtime test in `pkg/dslgoja/host_modules_test.go` proves this path using a real SQLite database. It starts a flow where `initialState()` writes a row through `db.exec`, then `render()` reads it back through `db.query`.

The database module demonstrates the full host-module chain:

```text
CLI flag -> SQLite open/provision -> RuntimeHost.DB -> require("db") -> JS query -> SQLite row
```

That is why it was the first host module to implement.

## 8. The user host module

The user module gives JavaScript a safe identity snapshot without exposing session manager internals. The relevant files are:

```text
pkg/dslgoja/user.go
pkg/server/handlers_dsl_uploads.go
pkg/server/handlers_dsl.go
pkg/dslgoja/modules_dsl.go
```

The core data type is:

```go
type UserSnapshot struct {
    Authenticated bool              `json:"authenticated"`
    ID            string            `json:"id"`
    DisplayName   string            `json:"displayName"`
    Email         string            `json:"email,omitempty"`
    Roles         []string          `json:"roles"`
    Claims        map[string]string `json:"claims,omitempty"`
    SessionID     string            `json:"sessionId"`
}
```

The server resolves a user snapshot when starting the flow:

```go
session, result, err := h.dslFlows.runtime.StartFlow(
    r.Context(),
    flowID,
    dslgoja.DemoIntakeFlowSource,
    dslgoja.WithUser(h.dslUserSnapshot(r)),
)
```

The snapshot is derived from existing auth claims. In dev mode, it comes from the configured development user. In OIDC mode, it comes from the session manager if a valid session exists. If no claims are available, the runtime uses an anonymous guest snapshot.

The module API exposed to JS is:

```js
const user = require("host/user");

const current = user.current();
const loggedIn = user.isAuthenticated();
const isClient = user.hasRole("client");
```

The loader returns lowerCamel JavaScript objects explicitly:

```go
func loadUserModule(session *FlowSession) func(*goja.Runtime, *goja.Object) {
    return func(vm *goja.Runtime, moduleObj *goja.Object) {
        exports := moduleObj.Get("exports").(*goja.Object)
        exports.Set("current", func() map[string]any { return userSnapshotJS(session.User) })
        exports.Set("isAuthenticated", func() bool { return session.User.Authenticated })
        exports.Set("hasRole", func(role string) bool { return session.User.HasRole(role) })
    }
}
```

This explicit map conversion is necessary because Goja does not apply JSON struct tags when exporting a Go struct to JavaScript. Without explicit shaping, JavaScript would see fields such as `SessionID` instead of `sessionId`.

## 9. The images host module

The images module gives JavaScript the ability to create upload intents and inspect completed uploads. It does not upload files itself. Uploading is an HTTP operation performed by the browser against a session-scoped endpoint.

The files involved are:

```text
pkg/dslgoja/images.go
pkg/dslgoja/modules_dsl.go
pkg/dslgoja/modules_host_helpers.go
pkg/server/handlers_dsl_uploads.go
pkg/dslgoja/flows/intake.flow.js
```

### 9.1 Upload intents

An upload intent is an object generated by Go during a render. It tells the browser where and how to upload a file.

```go
type UploadIntent struct {
    UploadID  string    `json:"uploadId"`
    SessionID string    `json:"sessionId"`
    Purpose   string    `json:"purpose"`
    Slot      string    `json:"slot,omitempty"`
    Method    string    `json:"method"`
    URL       string    `json:"url"`
    FieldName string    `json:"fieldName"`
    Accept    []string  `json:"accept"`
    MaxBytes  int64     `json:"maxBytes"`
    ExpiresAt time.Time `json:"expiresAt"`
}
```

JavaScript creates one like this:

```js
const images = require("host/images");

const upload = images.createUploadIntent({
  purpose: "intake-photo",
  slot: "front",
  maxBytes: 10 * 1024 * 1024,
});
```

The returned shape is lowerCamel:

```json
{
  "uploadId": "upl_...",
  "sessionId": "flow_...",
  "purpose": "intake-photo",
  "slot": "front",
  "method": "POST",
  "url": "/api/dsl/flows/flow_.../uploads/upl_...",
  "fieldName": "file",
  "accept": ["image/jpeg", "image/png", "image/webp"],
  "maxBytes": 10485760,
  "expiresAt": "2026-05-13T...Z"
}
```

The intent registry is stored on `FlowSession`:

```go
type FlowSession struct {
    UploadIntents map[string]UploadIntent
    Uploads       map[string]UploadedImage
    // existing fields...
}
```

`CreateUploadIntent` enforces the first invariants:

```text
CreateUploadIntent(options):
    purpose = options.purpose or "intake-photo"
    reject unsupported purpose
    accept = options.accept or [jpeg, png, webp]
    maxBytes = options.maxBytes, capped at 10 MB
    expiresIn = options.expiresInSeconds or 15 minutes
    id = "upl_" + uuid
    url = "/api/dsl/flows/{sessionId}/uploads/{uploadId}"
    store intent in session.UploadIntents
    return intent
```

### 9.2 Completed uploads

When a file is uploaded, the server completes the intent and records the resulting image metadata:

```go
type UploadedImage struct {
    UploadID         string
    SessionID        string
    Purpose          string
    Slot             string
    OriginalFilename string
    ContentType      string
    SizeBytes        int64
    StorageKey       string
    URL              string
    CreatedAt        time.Time
}
```

JavaScript can inspect completed uploads:

```js
const front = images.list({ purpose: "intake-photo" })
  .filter((item) => item.slot === "front")[0];

const one = images.get(uploadId);
```

The current implementation avoids re-locking the session from these module functions during render. Render already holds the session mutex. Re-entering locked helper methods from the host module caused a deadlock during testing. The module reads the session maps directly while already inside the render transaction.

This is an important runtime rule: host module functions called during render must respect the `FlowSession` lock model.

## 10. The server upload endpoint

The upload endpoint is registered in `pkg/server/http.go`:

```go
mux.HandleFunc(
    "POST /api/dsl/flows/{sessionId}/uploads/{uploadId}",
    h.handleDSLUpload,
)
```

The implementation is in:

```text
pkg/server/handlers_dsl_uploads.go
```

The handler does the following work:

```text
handleDSLUpload(request):
    sessionID = path sessionId
    uploadID = path uploadId

    session = dslFlows.get(sessionID)
    if missing:
        return DslError dsl_session_not_found

    intent = session.UploadIntent(uploadID)
    if missing:
        return DslError dsl_upload_intent_not_found

    if blobStore is nil:
        return DslError dsl_upload_storage_not_configured

    parse multipart form with intent.MaxBytes
    file = form file named intent.FieldName
    data = readValidatedPhotoUpload(file)
    enforce intent.MaxBytes
    enforce intent.Accept content-type list

    key = "dsl/{sessionID}/{uploadID}/{sanitizedFilename}"
    saved = blobStore.Save(key, data)

    image = session.CompleteUpload(uploadID, saved metadata)
    record image row in dsl_uploads if DSL DB exists

    return 201 upload metadata JSON
```

The storage key is generated by Go. Neither JavaScript nor the browser supplies the final storage key. This prevents a flow script or browser client from writing outside the intended storage namespace.

The endpoint reuses existing upload validation:

```text
pkg/server/photo_upload.go
readValidatedPhotoUpload
```

That function reads the file with a limit, rejects empty files, enforces the maximum size, and accepts only JPEG, PNG, or WebP based on detected content type.

## 11. Flow integration in `intake.flow.js`

The real flow now imports the host modules:

```js
const { page, n } = require("fringe/dsl");
const user = require("host/user");
const images = require("host/images");
```

The photos step creates upload intents for each tile:

```js
function photosStep(ctx) {
  function tile(key, label) {
    const upload = images.createUploadIntent({
      purpose: "intake-photo",
      slot: key,
    });

    const uploaded = images.list({ purpose: "intake-photo" })
      .filter(function (item) { return item.slot === key; })[0];

    return n.photoTile(label, {
      value: key,
      filled: !!ctx.state.photos[key] || !!uploaded,
      imageUrl: uploaded ? uploaded.url : undefined,
      upload: upload,
      actions: {
        uploaded: ctx.action("uploadedPhoto:" + key, function (event) {
          ctx.state.photos[key] = event.value || true;
          return render(ctx);
        }, "uploaded"),
        upload: ctx.action("uploadPhoto:" + key, function () {
          ctx.state.photos[key] = true;
          return render(ctx);
        }, "upload"),
        remove: ctx.action("removePhoto:" + key, function () {
          ctx.state.photos[key] = false;
          return render(ctx);
        }, "remove"),
      },
    }).id("photo-" + key);
  }

  // page construction continues...
}
```

This code shows the intended separation. JavaScript decides which tiles exist, how state changes after an upload, and how the image URL affects page rendering. Go decides how the upload URL is created, how the file is validated, where the file is stored, and how upload metadata is recorded.

## 12. The real DSL upload test

The best upload test is a direct HTTP smoke against the real DSL. It does not require the frontend upload UI to be ready. It tests the actual Goja flow, actual upload intent generation, actual upload endpoint, actual blob storage path, actual SQLite metadata, and actual DSL event dispatch.

The test has five stages:

1. Start a real flow.
2. Dispatch `next` twice to reach the photos page.
3. Extract an upload URL from a `photoTile` node.
4. Upload a small image to the session-scoped upload endpoint.
5. Dispatch the tile's `uploaded` action back into the DSL and verify rerendered page state.

### 12.1 Restart backend

The host modules are backend code. Restart the backend before testing:

```bash
devctl restart hair-booking-backend
```

If the frontend upload UI is also being tested, restart web too:

```bash
devctl restart hair-booking-web
```

### 12.2 Start a real flow

```bash
START_JSON=$(curl -sS -X POST \
  http://127.0.0.1:19080/api/dsl/flows/fringe.intake.v1/start)

echo "$START_JSON" | jq '{sessionId, pageVersion, pageId: .page.id}'
```

Expected shape:

```json
{
  "sessionId": "flow_...",
  "pageVersion": 1,
  "pageId": "intake-service"
}
```

Save identifiers:

```bash
SESSION_ID=$(echo "$START_JSON" | jq -r '.sessionId')
```

### 12.3 Dispatch `next` events until photos

The photos page is the third page. The first `next` moves service to color. The second `next` moves color to photos.

Define shell helpers:

```bash
next_action() {
  jq -r '.page.shell.props.actions.next.id'
}

post_next() {
  local json="$1"
  local version action
  version=$(echo "$json" | jq -r '.pageVersion')
  action=$(echo "$json" | next_action)

  curl -sS -X POST \
    "http://127.0.0.1:19080/api/dsl/flows/$SESSION_ID/events" \
    -H 'Content-Type: application/json' \
    --data-binary "{
      \"eventId\": \"evt_$(uuidgen)\",
      \"sessionId\": \"$SESSION_ID\",
      \"pageVersion\": $version,
      \"nodeId\": \"shell.next\",
      \"nodeKind\": \"intakeShell\",
      \"actionId\": \"$action\",
      \"event\": \"next\"
    }"
}
```

Run navigation:

```bash
COLOR_JSON=$(post_next "$START_JSON")
PHOTOS_JSON=$(post_next "$COLOR_JSON")

echo "$PHOTOS_JSON" | jq '{sessionId, pageVersion, pageId: .page.id}'
```

Expected:

```json
{
  "pageId": "intake-photos"
}
```

### 12.4 Inspect upload intents

The photo tiles are children of `photo-grid`:

```bash
echo "$PHOTOS_JSON" | jq '
  .page.nodes[]
  | select(.meta.id == "photo-grid")
  | .children[]
  | {
      id: .meta.id,
      label: .props.label,
      upload: .props.upload
    }
'
```

Expected for the front tile:

```json
{
  "id": "photo-front",
  "label": "Front",
  "upload": {
    "uploadId": "upl_...",
    "sessionId": "flow_...",
    "purpose": "intake-photo",
    "slot": "front",
    "method": "POST",
    "url": "/api/dsl/flows/flow_.../uploads/upl_...",
    "fieldName": "file",
    "accept": ["image/jpeg", "image/png", "image/webp"],
    "maxBytes": 10485760,
    "expiresAt": "..."
  }
}
```

Extract the upload URL:

```bash
UPLOAD_URL=$(echo "$PHOTOS_JSON" | jq -r '
  .page.nodes[]
  | select(.meta.id == "photo-grid")
  | .children[]
  | select(.meta.id == "photo-front")
  | .props.upload.url
')

echo "$UPLOAD_URL"
```

### 12.5 Create a tiny image

Use a tiny PNG file:

```bash
python3 - <<'PY'
import base64
png = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII="
)
open("/tmp/fringe-test.png", "wb").write(png)
PY

file /tmp/fringe-test.png
```

### 12.6 Upload the image

```bash
UPLOAD_RESPONSE=$(curl -sS -X POST \
  "http://127.0.0.1:19080$UPLOAD_URL" \
  -F "file=@/tmp/fringe-test.png;type=image/png")

echo "$UPLOAD_RESPONSE" | jq .
```

Expected response:

```json
{
  "uploadId": "upl_...",
  "sessionId": "flow_...",
  "purpose": "intake-photo",
  "slot": "front",
  "originalFilename": "fringe-test.png",
  "contentType": "image/png",
  "sizeBytes": 68,
  "storageKey": "dsl/flow_.../upl_.../fringe-test.png",
  "url": "/uploads/dsl/flow_.../upl_.../fringe-test.png"
}
```

Verify the public URL:

```bash
UPLOAD_PUBLIC_URL=$(echo "$UPLOAD_RESPONSE" | jq -r '.url')
curl -I "http://127.0.0.1:19080$UPLOAD_PUBLIC_URL"
```

Expected:

```text
HTTP/1.1 200 OK
```

### 12.7 Verify SQLite metadata

The default DSL database path is:

```text
./var/fringe-dsl.sqlite
```

Inspect tables:

```bash
sqlite3 ./var/fringe-dsl.sqlite '.tables'
```

Expected includes:

```text
dsl_flow_sessions
dsl_uploads
```

Inspect recent uploads:

```bash
sqlite3 ./var/fringe-dsl.sqlite \
  "SELECT id, session_id, purpose, slot, content_type, size_bytes, storage_key, public_url FROM dsl_uploads ORDER BY created_at DESC LIMIT 5;"
```

Expected row pattern:

```text
upl_...|flow_...|intake-photo|front|image/png|68|dsl/flow_...|/uploads/...
```

Inspect flow session records:

```bash
sqlite3 ./var/fringe-dsl.sqlite \
  "SELECT id, flow_id, status, current_page_id, current_page_version FROM dsl_flow_sessions ORDER BY created_at DESC LIMIT 5;"
```

Expected row pattern:

```text
flow_...|fringe.intake.v1|active|intake-service|1
```

The current implementation records the flow session at start. It does not yet update `current_page_id` and `current_page_version` after every event dispatch. That is acceptable for validating uploads, but it should be improved if SQLite becomes the durable session index.

### 12.8 Dispatch the `uploaded` event

The upload endpoint stores the image. The Goja flow state changes only when the browser dispatches the tile's `uploaded` action.

Extract the action id:

```bash
UPLOADED_ACTION_ID=$(echo "$PHOTOS_JSON" | jq -r '
  .page.nodes[]
  | select(.meta.id == "photo-grid")
  | .children[]
  | select(.meta.id == "photo-front")
  | .props.actions.uploaded.id
')

PHOTOS_VERSION=$(echo "$PHOTOS_JSON" | jq -r '.pageVersion')
```

Dispatch the uploaded event:

```bash
curl -sS -X POST \
  "http://127.0.0.1:19080/api/dsl/flows/$SESSION_ID/events" \
  -H 'Content-Type: application/json' \
  --data-binary "$(jq -n \
    --arg eventId "evt_$(uuidgen)" \
    --arg sessionId "$SESSION_ID" \
    --argjson pageVersion "$PHOTOS_VERSION" \
    --arg actionId "$UPLOADED_ACTION_ID" \
    --argjson value "$UPLOAD_RESPONSE" \
    '{
      eventId: $eventId,
      sessionId: $sessionId,
      pageVersion: $pageVersion,
      nodeId: "photo-front",
      nodeKind: "photoTile",
      actionId: $actionId,
      event: "uploaded",
      value: $value
    }')" \
  | jq '
      {
        pageVersion,
        pageId: .page.id,
        photoCount: (
          .page.nodes[]
          | select(.meta.id == "photo-count")
          | .props.children
        ),
        front: (
          .page.nodes[]
          | select(.meta.id == "photo-grid")
          | .children[]
          | select(.meta.id == "photo-front")
          | .props
        )
      }
    '
```

Expected result:

```json
{
  "pageId": "intake-photos",
  "photoCount": "1 photo angles selected",
  "front": {
    "filled": true,
    "imageUrl": "/uploads/...",
    "upload": { "uploadId": "upl_..." }
  }
}
```

This proves the complete path:

```text
Goja render
  -> upload intent in page JSON
  -> HTTP multipart upload
  -> BlobStore save
  -> SQLite dsl_uploads row
  -> uploaded DSL event
  -> Goja state update
  -> rerender with imageUrl
```

## 13. What each action does

The curl walkthrough is more than a manual test. Each action exercises a specific part of the architecture.

| Action | Code path exercised | What it proves |
| --- | --- | --- |
| `POST /api/dsl/flows/fringe.intake.v1/start` | `handleDSLStartFlow`, `Runtime.StartFlow`, `installModules`, `intake.flow.js` | The backend can create a session with host modules installed. |
| Dispatch `shell.next` from service to color | `handleDSLEvent`, `FlowSession.Dispatch`, Goja callback | Page-version-scoped action dispatch still works after host modules. |
| Dispatch `shell.next` from color to photos | Same dispatch path | The real flow reaches the photo step and rerenders. |
| Inspect `photo-grid` children | Protobuf `FlowState` page JSON | The real DSL emits `photoTile` upload intent props. |
| `curl -F file=@... $UPLOAD_URL` | `handleDSLUpload`, `readValidatedPhotoUpload`, `BlobStore.Save` | The upload endpoint validates and stores a file for a session intent. |
| Query `dsl_uploads` | `recordDSLUpload` | Upload metadata is durable in SQLite. |
| Dispatch `uploaded` event | `FlowSession.Dispatch`, `uploadedPhoto:*` callback | The flow consumes upload metadata and updates page state. |
| Inspect rerendered tile | `images.list`, `photoTile` props | Completed uploads are visible to JS on the next render. |

This table is useful when debugging. If one step fails, the failed row tells you where to look first.

## 14. Important failure modes

### 14.1 Undefined vs omitted protobuf values

The DSL event transport uses protobuf JSON. A value-less event such as `edit`, `next`, or `uploaded` without a payload must omit `value`. It must not send `value: undefined`. This issue was fixed earlier in the frontend client by explicitly constructing event JSON and only including optional fields when defined.

### 14.2 Go struct tags do not define JavaScript object keys

Goja does not export Go structs to JavaScript using JSON tags. A Go field named `UploadID` becomes visible as `UploadID`, not `uploadId`, unless the host module returns a map with the desired key. HAIR-036 uses helper functions in `pkg/dslgoja/modules_host_helpers.go` to shape host objects into lowerCamel JS API objects.

### 14.3 Session locks can deadlock host module functions

`FlowSession.Render` and `FlowSession.Dispatch` hold the session mutex while calling into Goja. A host module called during render must not call another method that tries to take the same mutex. The first `host/images.list(...)` implementation did that and caused a timeout. The fixed implementation reads session upload maps directly while already under the render transaction.

This is the current rule:

```text
If a host module is called from render or action dispatch, assume the session lock is already held.
Do not call methods that re-lock the session unless the locking model is changed.
```

### 14.4 Upload metadata requires a flow session row

`dsl_uploads.session_id` references `dsl_flow_sessions.id`. The upload handler records metadata in `dsl_uploads`, so the server must record a `dsl_flow_sessions` row when a flow starts. HAIR-036 added `recordDSLFlowSession(...)` after `h.dslFlows.put(session)`.

### 14.5 Upload success is JSON while DSL flow success is protobuf JSON

The DSL start/get/event endpoints return protobuf JSON `FlowState` or `DslError`. The upload endpoint is multipart and currently returns normalized upload metadata as plain JSON. Errors from the upload endpoint use `DslError` for consistency with the DSL API, but success metadata is not yet a protobuf message.

That is acceptable now. If upload metadata becomes part of a broader contract, define a protobuf message for it.

## 15. Tests that now protect the work

The codebase has tests at three levels.

### 15.1 SQLite provisioning tests

File:

```text
pkg/dslhost/db_test.go
```

These tests verify:

- `OpenDB(..., Migrate: true)` creates all host tables.
- `OpenDB(..., Migrate: false)` does not create schema.
- `ProvisionSchema` is idempotent.

### 15.2 Runtime host module tests

Files:

```text
pkg/dslgoja/host_modules_test.go
pkg/dslgoja/host_user_images_test.go
```

These tests verify:

- `require("fringe/dsl")` still works without host modules.
- `require("db")` works when a host DB is configured.
- `require("db")` is unavailable without a host DB.
- `require("host/user")` returns a lowerCamel user snapshot.
- `require("host/images")` creates upload intents and registers them on the session.

### 15.3 Server upload tests

File:

```text
pkg/server/handlers_dsl_uploads_test.go
```

The current server test verifies the successful upload path:

- create DSL SQLite database,
- create fake `BlobStore`,
- start a flow that creates an upload intent,
- upload a tiny JPEG-like payload to the session upload endpoint,
- verify the blob store received a file,
- verify `dsl_uploads` has metadata.

Remaining useful tests are:

- wrong session,
- unknown upload id,
- expired intent,
- invalid content type,
- oversized file.

## 16. Current status

The host-module foundation is implemented and committed. Relevant commits are:

```text
0247a51 HAIR-036 Step 1: Add Go host modules guide
0bb098a HAIR-036 Step 2: Expand server host module phases
8f5d0d2 HAIR-036 Step 3: Add DSL SQLite host module foundation
f280bee HAIR-036: record Step 3 host module commit
7b94c9c HAIR-036 Step 4: Add user and image host modules
eb1ed15 HAIR-036: record Step 4 host module commit
```

Validation passed after Step 4:

```bash
go test ./pkg/dslgoja ./pkg/server -count=1
go test ./... -count=1
```

The working tree was clean after the Step 4 commit. Separate HAIR-035 desktop UI work had been committed by a colleague and was not part of this server-side host-module slice.

## 17. What to do next

The next best step is to turn the manual upload walkthrough into a repeatable ticket script:

```text
ttmp/2026/05/13/HAIR-036--go-host-modules-for-backend-driven-dsl-runtime/scripts/01-smoke-upload.sh
```

The script should:

1. Start a real `fringe.intake.v1` flow.
2. Dispatch `next` twice to reach photos.
3. Extract the front tile upload URL and uploaded action id.
4. Create a tiny PNG.
5. Upload it with `curl -F`.
6. Query SQLite for the upload metadata row.
7. Dispatch the `uploaded` event.
8. Assert that the rerendered page has `filled: true` and an `imageUrl` for `photo-front`.

The next implementation step after that should add the remaining upload failure tests. Those tests will lock down edge-case behavior before frontend upload UI depends on it.

After upload tests are complete, the host-module system can grow in two directions:

- Add more plumbing modules, such as `host/calendar`, `host/notifications`, and `host/jobs`.
- Start using `db` from JavaScript for drafts and audit events in the real intake flow.

## 18. Working rule

Keep the host modules plumbing-oriented. Go should expose durable, validated, permission-aware operations. JavaScript should decide how those operations fit into the intake product flow. That boundary keeps the runtime extensible: new app behavior can be authored in JS, while Go continues to enforce the system-level invariants that protect data, storage, and identity.
