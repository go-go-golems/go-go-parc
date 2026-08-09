# Validation record

The following checks were run in the build container on July 30, 2026 UTC.

## Go backend

Environment: Go 1.23.2, linux/amd64.

```bash
cd backend
gofmt -w ./cmd ./internal
go test ./...
go vet ./...
go test -race ./...
```

Result: all packages passed. The analyzer and tagged-code encoder unit tests passed, and the race detector reported no races.

## Compact end-to-end smoke test

Environment: Node.js 22.16.0.

```bash
node ./scripts/smoke.mjs
```

This test builds a temporary Go binary, starts it on a test port, opens a browser-compatible WebSocket, and verifies initialization, document synchronization, plain and interactive goals, recursive tagged code with a v1 `__rpcref`, interactive popups, PBUI timeline/server-model procedures, reference release, keepalive, file progress, and incremental diagnostics.

Observed result:

```json
{
  "ok": true,
  "plainGoals": 1,
  "interactiveGoals": 1,
  "timelineSteps": 15,
  "rpcReference": "1"
}
```

## Exhaustive protocol lifecycle suite

```bash
./scripts/protocol-suite.sh
```

The stronger suite additionally verifies:

- an induction snapshot with multiple displayed branch goals;
- inserted goal diff flags;
- `Lean.Widget.InteractiveDiagnostics.infoToInteractive`;
- `Lean.Widget.getGoToLocation`;
- rejection of a released RPC reference with error `-32900`;
- invalidation of the old file-scoped session after `didChange`;
- reconnection with a new string session ID;
- replacement plus incremental diagnostic chunks merged for document version 2.

Observed result:

```json
{
  "ok": true,
  "timelineSteps": 8,
  "displayedGoalsAtBranch": 3,
  "taggedReference": "1",
  "diagnosticsV1": 1,
  "diagnosticsV2Initial": 1,
  "diagnosticsV2Merged": 3,
  "incrementalChunksV2": 1,
  "sessionV1": "1",
  "sessionV2": "2"
}
```

## React/TypeScript source

The complete frontend source was checked with TypeScript 5.8.3 in strict mode using temporary ambient React declarations because the build container could not install the npm dependency tree. The source also emitted successfully to JavaScript, and every emitted JavaScript file passed `node --check`.

Result: passed.

A full `npm install && npm run build` was not executed here. The configured container registry returned `404 Not Found` for `@types/react`, and direct public-registry access timed out. Run `make install && make build` in a normal networked Node.js environment to perform the real Vite production build.
