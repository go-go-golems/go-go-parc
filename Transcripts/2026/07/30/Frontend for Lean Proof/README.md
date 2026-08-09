# PBUI Mock Lean Workbench

A runnable protocol laboratory for a CLIM/Genera-inspired Lean frontend.

- **Backend:** dependency-free Go server, JSON-RPC 2.0 over WebSocket.
- **Frontend:** React + TypeScript PBUI shell.
- **Primary objects:** tagged Lean code, interactive goals, hypotheses, declarations, diagnostics, timeline steps, RPC references, tiles, and workspaces.
- **Semantics:** deliberately rule-based. This is a protocol and UI mock, not a second Lean implementation.

## What is implemented

### Tagged Lean code

The backend returns recursive `CodeWithInfos` values using `text`, `append`, and `tag` nodes. Every tag carries a v1 RPC object:

```json
{ "__rpcref": "17" }
```

The frontend turns each tagged subexpression into a typed PBUI presentation. Left-click requests an interactive popup. Right-click exposes commands such as inspect, go to definition, and add to watchlist. The inspector renders the popup's tagged type and explicit expression recursively.

### Interactive goals

`Lean.Widget.getInteractiveGoals` returns goal objects with:

- bundled local hypotheses;
- tagged types and optional let values;
- goal/context references;
- case names, metavariable IDs, and goal prefixes;
- inserted/removed goal and hypothesis flags.

The demo proof intentionally branches at `induction`, allowing the goal tile and timeline to show removed and inserted states.

### Protocol lifecycle

The client exercises:

- initialization;
- full-document `didOpen` / `didChange` / `didClose` synchronization;
- versioned replacement and incremental diagnostics plus `$/lean/fileProgress` notifications;
- `$/lean/plainGoal` fallback;
- file-scoped RPC sessions;
- ten-second keepalives;
- ref-counted v1 reference ownership across live views, inspector panes, and watchlist pins;
- reference release when a view is replaced or a pin is removed;
- stale-session recovery after document edits;
- cancellation of superseded cursor requests;
- a visible protocol trace.

### PBUI shell

The React application includes:

- typed presentations and presentation-type inheritance;
- CLIM-style accepting-values mode for `<lean.term>`;
- context-sensitive command menus;
- three workspaces (`prove`, `inspect`, and `protocol`);
- application-selectable tiles;
- source transport synchronized with goal snapshots;
- inspector, watchlist, environment, diagnostics, raw RPC, session state, and trace tiles.

## Repository layout

```text
backend/
  cmd/mocklean/          Go entry point
  internal/mock/         rule-based document analyzer and tagged-code encoder
  internal/protocol/     LSP/RPC wire structures
  internal/server/       JSON-RPC methods and reference/session management
  internal/ws/           small dependency-free RFC 6455 implementation
frontend/
  src/protocol/          JSON-RPC socket, Lean client, wire types
  src/state/             versioned workbench state and reference ownership
  src/pbui/              presentation system, accepting values, tiles
  src/components/        source, goals, timeline, inspector, trace, etc.
fixtures/Demo.lean       source used by the smoke test
scripts/                 development and end-to-end test scripts
```

## Requirements

- Go 1.23 or newer.
- Node.js 20 or newer.
- npm.

## Run in development

```bash
make install
make dev
```

Open `http://localhost:5173`. Vite runs on port 5173 and the Go mock listens on port 3210. Set `VITE_LEAN_WS_URL` to override the WebSocket endpoint.

Equivalent two-terminal commands:

```bash
cd backend
go run ./cmd/mocklean -addr :3210
```

```bash
cd frontend
npm install
npm run dev
```

## Test

```bash
make backend-check
make smoke
make protocol-smoke

# After npm install:
make test
# or all checks:
make validate
```

Both live protocol suites have no npm dependency. `make smoke` runs a compact end-to-end check. `make protocol-smoke` additionally verifies branching goal diffs, popup and go-to RPC, released-reference rejection, document-version session invalidation, reconnection, and incremental diagnostic chunks. They use Node's built-in `fetch` and `WebSocket` APIs.

## Production build

```bash
make build
make serve
```

`make serve` serves the compiled React app and `/ws` from one Go process at `http://localhost:8080`.

## Demo path

1. Move the source cursor from the theorem statement to `induction n with`.
2. Observe one removed goal and two inserted branch goals.
3. Click any identifier in a goal target to open its interactive popup.
4. Right-click a tagged term and add it to the watchlist.
5. Edit the source; the old watched term becomes stale because the document version and RPC session changed.
6. Insert `unknown_tactic` to produce a diagnostic.
7. Open the `protocol` workspace to compare `$/lean/plainGoal` with raw `InteractiveGoals` and inspect session reference counts.

## Extending toward real Lean

Keep the frontend protocol boundary. Replace `LeanMockClient`'s WebSocket transport with an Electron/Tauri/local-host bridge to a real Lean language server, or proxy LSP/RPC through a daemon. The PBUI-specific procedures can later be implemented by a Lean package using server RPC methods over `InfoTree` data.

See [PROTOCOL.md](./PROTOCOL.md) for the complete mock surface and deliberate deviations.
