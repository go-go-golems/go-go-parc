---
title: "Content-Addressable Blob Server: Filesystem CAS, HTTP Semantics, and k3s Operations"
aliases:
  - CAS Blob Server Deep Dive
  - Filesystem Content-Addressable Storage in Go
  - CAS-001 Technical Report
tags:
  - article
  - playbook
  - go
  - storage
  - cas
  - http
  - kubernetes
  - glazed
status: active
type: article
created: 2026-08-07
repo: /home/manuel/code/wesen/2026-08-07--cas-content-addressed-store
---

# Content-Addressable Blob Server: Filesystem CAS, HTTP Semantics, and k3s Operations

This report explains the design and implementation of the CAS blob server in `/home/manuel/code/wesen/2026-08-07--cas-content-addressed-store`. The project provides a single-node HTTP service for storing opaque byte streams by SHA-256 identity. It uses a filesystem for immutable blob bytes, SQLite for mutable logical references, the Glazed command framework for the executable interface, and Kubernetes manifests for an internal k3s deployment.

The report is written as a technical deep dive rather than a chronological changelog. It begins with the identity and durability model, then follows the upload path through filesystem installation, the HTTP contract, reference persistence, garbage collection, command lifecycle, deployment constraints, and validation evidence. The implementation guide and diary in the project ticket contain the full design record; this note extracts the durable engineering knowledge into the Obsidian vault.

> [!summary]
> - A blob is identified by `sha256:<64 lowercase hexadecimal characters>` and stored at a deterministic two-level fan-out path.
> - Uploads stream into a private temporary file, hash and count bytes, synchronize the file, and install it with an atomic hard-link operation that does not replace an existing final name.
> - SQLite stores mutable names separately from immutable bytes; garbage collection marks referenced digests and removes only old, unreferenced objects.
> - Version one is deliberately single-node and single-writer at the PVC boundary. It is not an S3-compatible or replicated object store.

## Why this report exists

The project was created from a concrete storage requirement: deploy a small internal blob service to k3s without introducing an object-storage cluster. The useful engineering question is not whether a filesystem can hold files. It is whether a service can turn an untrusted byte stream into a durable, immutable object while preserving a precise identity, exposing stable HTTP semantics, and remaining operable when references change or storage needs to be reclaimed.

The implementation chooses a narrow boundary. A client can upload bytes, retrieve them by digest, test existence through `HEAD`, delete unreferenced objects, and maintain names that point to digests. The server does not implement multipart uploads, resumable transfers, range requests, replication, erasure coding, encryption at rest, packfiles, or S3 protocol compatibility. Those omissions are part of the design. They keep the first version inspectable and make its capacity and concurrency boundaries explicit.

The project was initialized in an empty application repository. The relevant source of design evidence is the CAS-001 ticket at:

```text
/home/manuel/code/wesen/2026-08-07--cas-content-addressed-store/ttmp/2026/08/07/CAS-001--content-addressable-blob-server/
```

The primary documents are:

- `design-doc/01-cas-blob-server-design-and-intern-implementation-guide.md`
- `reference/01-implementation-diary.md`
- `playbook/01-operations-and-validation-playbook.md`
- `tasks.md`
- `changelog.md`

## 1. Content addressing is an identity contract

Content-addressable storage defines object identity as a function of content. In this implementation, the function is SHA-256 over the exact bytes received by the server:

```text
digest = "sha256:" + lowercase_hex(SHA256(bytes))
```

The `sha256:` prefix is part of the public identity. It prevents a bare hexadecimal string from losing the algorithm name and leaves room for a future algorithm namespace without changing the lexical shape of the identifier. Version one accepts only SHA-256 and only lowercase hexadecimal characters. The parser is implemented in `internal/cas/digest.go:9-37`.

The digest type is a named string:

```go
type Digest string

func (d Digest) String() string { return string(d) }

func (d Digest) Hex() string {
    return strings.TrimPrefix(string(d), "sha256:")
}
```

`ParseDigest` checks all of the following before returning a `Digest`:

- the `sha256:` prefix is present;
- exactly 64 characters follow the prefix;
- every suffix character is a lowercase hexadecimal digit;
- no slash, uppercase character, whitespace, or alternate algorithm is accepted.

This validation is repeated at storage method boundaries by `validateDigest` in `internal/cas/store.go:231-234`. HTTP handlers already parse URL values before invoking the store, but the store must still defend its own path derivation. Otherwise a future caller could pass an invalid internal value and cause a path-slicing panic or an unintended filesystem lookup.

### Digest-to-path mapping

A digest does not require a database lookup to locate its bytes. The implementation removes the algorithm prefix and uses the first two pairs of hex characters as directory names:

```text
sha256:7f83b1657ff1fc53b92dc...

<data-dir>/sha256/7f/83/7f83b1657ff1fc53b92dc...
```

The function is implemented in `internal/cas/digest.go:34-37`. The resulting layout is:

```mermaid
flowchart LR
    B[Uploaded bytes] --> H[SHA-256]
    H --> D[sha256:<64 lowercase hex>]
    D --> P[sha256/7f/83/full-hex]
    P --> F[Immutable regular file]

    style H fill:#264653,stroke:#2a9d8f,color:#fff
    style D fill:#2a9d8f,stroke:#264653,color:#fff
    style F fill:#e9c46a,stroke:#264653,color:#000
```

Two directory levels reduce the number of entries in any single directory. The layout remains directly computable, which means a read can validate a digest and open one path without consulting an object index. This property is valuable for recovery: if the reference database is lost, the object files remain addressable by digest even though their logical names are gone.

The on-disk state has three distinct parts:

```text
<data-dir>/
├── sha256/
│   └── <first-two-hex>/<next-two-hex>/<full-64-hex>
├── tmp/
│   └── upload-<random-name>
└── metadata.db
```

The `sha256` tree contains final objects. The `tmp` tree contains incomplete uploads and must not be scanned as object storage. `metadata.db` contains references, not blob contents.

## 2. The upload path establishes the durability boundary

The most important operation is `Store.Put` in `internal/cas/store.go:36-86`. Its responsibility is to ensure that the final digest path is never exposed while its contents are incomplete.

The operation proceeds in this order:

1. Validate that the configured maximum size is positive.
2. Create a private temporary file under `<data-dir>/tmp`.
3. Read the input through a `maxBytes+1` limit.
4. Write each buffer to the temporary file and the SHA-256 hash simultaneously.
5. Reject the upload if the observed byte count exceeds `maxBytes`.
6. Call `Sync` on the temporary file.
7. Close the temporary file.
8. Derive the final digest path and create its parent directories.
9. Create a hard link from the temporary file to the final path.
10. Treat an existing final path as an idempotent duplicate and discard the temporary link.
11. Synchronize the containing directory.
12. Return the digest and byte count.

The essential pseudocode is:

```text
Put(ctx, input, maxBytes):
    temp = create(dataDir/tmp/upload-random)
    defer close_and_remove(temp)

    hash = SHA256()
    count = copy_with_context(
        destination = multiwriter(temp, hash),
        source = limit(input, maxBytes + 1),
    )

    if count > maxBytes:
        return ErrTooLarge

    fsync(temp)
    close(temp)

    digest = sha256:<hash bytes as lowercase hex>
    final = path_for(dataDir, digest)
    mkdir_all(parent(final))

    if link(temp, final) fails with EEXIST:
        stat(final)
        # The object was installed by this or another writer.
    else if link fails:
        return installation error

    fsync(parent(final))
    return digest, count
```

`copyWithContext` in `internal/cas/store.go:88-113` checks `ctx.Err()` before each read. It uses a fixed 128 KiB buffer and counts bytes actually written. The context check does not interrupt a reader that is blocked inside its own `Read` method; the HTTP request body normally supplies cancellation through the request context and transport behavior. The function does ensure that cancellation observed between reads removes the temporary file through the deferred cleanup path.

### Why the final object is not written in place

Writing directly to the final digest path would allow a concurrent GET or verification pass to observe a prefix of the intended object. The temporary path keeps incomplete bytes outside the namespace that readers scan. The hard link adds one directory entry to an already synchronized file. On the target Linux filesystem, link creation is atomic with respect to directory visibility and fails when the destination exists.

The operation does not replace an existing destination. This matters for concurrent identical uploads:

```mermaid
sequenceDiagram
    participant A as Writer A
    participant B as Writer B
    participant T as Temporary files
    participant O as Final object path

    A->>T: write and hash bytes
    B->>T: write and hash bytes
    A->>T: fsync and close
    B->>T: fsync and close
    A->>O: hard-link temp to digest path
    O-->>A: success
    B->>O: hard-link temp to same digest path
    O-->>B: EEXIST
    B->>T: remove duplicate temp
```

Both writers compute the same identity. One installs the file. The other receives an existing destination and returns the same digest after checking that the final path is present. The test `TestPutOpenAndDuplicateConcurrency` in `internal/cas/store_test.go` runs eight concurrent writers and verifies the resulting bytes.

### Size rejection and cleanup

The HTTP handler wraps the request body with `http.MaxBytesReader` in `internal/httpapi/handler.go:69-83`, while the storage layer reads at most `maxBytes+1`. The extra byte is necessary to distinguish an input of exactly the configured size from an input that exceeds it. An oversized upload is never synchronized or linked into the final object tree. The deferred cleanup closes and removes the temporary file.

The `serve` command rejects non-positive `--max-blob-bytes` during startup in `internal/commands/serve.go:49-64`. This turns a configuration error into a process startup failure rather than a request-time storage error.

## 3. Reads and deletes have explicit filesystem safety rules

`Store.Open` in `internal/cas/store.go:115-147` validates the digest, uses `Lstat`, rejects non-regular files, then opens and stats the object. The `Lstat` check is intentional. A symlink under the object namespace must not redirect a read to an arbitrary path outside the data directory.

`Store.Exists` in `internal/cas/store.go:149-161` uses the same regular-file rule. `Store.Delete` in `internal/cas/store.go:163-174` validates the digest and returns `os.ErrNotExist` when the object is absent. The HTTP layer maps that error to a JSON `404` response.

`Store.List` in `internal/cas/store.go:176-203` walks only the `sha256` tree. It validates the exact three-component fan-out shape and returns an error for malformed files rather than silently ignoring them. This behavior makes readiness and verification sensitive to unexpected files in the object tree. Temporary uploads remain outside that walk.

`Store.VerifyAll` in `internal/cas/store.go:205-229` opens every listed object, recomputes its SHA-256, and compares the computed digest with the path-derived digest. It is a full read of all object bytes and therefore belongs in explicit maintenance commands rather than a request path.

## 4. The HTTP API exposes storage semantics without exposing filesystem details

`internal/httpapi/handler.go:29-59` dispatches routes through the standard library. The service does not use a third-party router. The handlers parse and validate URL values before calling storage methods, and JSON errors deliberately omit host paths and SQL details.

### Endpoint contract

| Method | Path | Success | Meaning |
|---|---|---:|---|
| `GET` | `/healthz` | `200` | Process is serving requests. |
| `GET` | `/readyz` | `200` or `503` | Object-tree listing succeeds or fails. |
| `PUT` | `/v1/blobs` | `201` | Request bytes were stored and a digest was assigned. |
| `GET` | `/v1/blobs/{digest}` | `200` | Exact object bytes are returned. |
| `HEAD` | `/v1/blobs/{digest}` | `200` | Object metadata is returned without bytes. |
| `DELETE` | `/v1/blobs/{digest}` | `204` | An unreferenced object was removed. |
| `PUT` | `/v1/refs/{name}` | `200` | A logical name now points to an existing digest. |
| `GET` | `/v1/refs/{name}` | `200` | The current digest for a logical name is returned. |
| `DELETE` | `/v1/refs/{name}` | `204` | A logical name was removed. |

Errors use this shape:

```json
{"error":"blob not found","code":"not_found"}
```

The endpoint-specific error codes are stable identifiers such as `invalid_digest`, `too_large`, `missing_blob`, `referenced`, `unauthorized`, and `not_found`. Server-side errors are sanitized into codes such as `store_error`, `refs_error`, and `open_error`.

### Upload response

A successful upload returns JSON and a `Location` header:

```json
{"digest":"sha256:<64-lowercase-hex>","size":123}
```

The server never accepts a client-provided digest as the source of identity. It computes the digest from the body it writes. This prevents a client from claiming that bytes have an identity different from their actual content.

### Download response

The handler opens the validated digest path, sets `Content-Type: application/octet-stream`, sets `Content-Length` from the regular-file metadata, and copies the file to the response. `HEAD` performs the same lookup and metadata calculation but does not copy bytes. The implementation does not provide range requests; clients should treat downloads as complete object transfers.

### Authentication boundary

Authentication is optional at the binary configuration level. When `--auth-token` is non-empty, data routes require an `Authorization` header with the exact form `Bearer <token>`. `authorized` in `internal/httpapi/handler.go:61-67` compares equal-length byte slices using `subtle.ConstantTimeCompare`.

Health and readiness endpoints bypass authentication so Kubernetes probes can execute without access to the data Secret. This is a deliberate boundary: health endpoints disclose only liveness/readiness, while blob and reference routes are the protected data surface.

The deployment injects the token through `CAS_SERVER_AUTH_TOKEN`. Glazed's Cobra parser derives the environment prefix from the application name `cas-server`; the token is not placed in the process argument list.

## 5. References are mutable metadata, not alternate blob storage

A digest identifies immutable bytes. Users still need names such as `builds/latest` or `users/123/avatar`. Those names are mutable and are stored in SQLite by `internal/refs/store.go`.

The schema created in `refs.Open` is:

```sql
CREATE TABLE IF NOT EXISTS refs (
    name       TEXT PRIMARY KEY,
    digest     TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

The database is opened with one maximum connection, a five-second busy timeout, and WAL journal mode. The one-connection configuration matches the single-node write boundary and avoids an unnecessary local pool for this small service.

Reference names are validated in `ValidateName` at `internal/refs/store.go:33-38`. A valid name is at most 255 bytes, does not begin with `/`, does not contain `..`, and matches lowercase letters, digits, `.`, `_`, `-`, or `/`. The validation protects both API semantics and future path-oriented tooling from ambiguous names.

`Set` performs an SQLite upsert after validating the name and digest. The HTTP handler checks that the target blob exists before calling `Set` in `internal/httpapi/handler.go:156-187`:

```text
PUT /v1/refs/builds/latest
{"digest":"sha256:..."}

1. Parse and validate the reference name.
2. Decode JSON and parse the digest.
3. Ask the CAS store whether the object exists.
4. Return 409 if the object is absent.
5. Upsert the name-to-digest mapping in SQLite.
```

This check and the database update are separate operations. In version one, the service is single-replica and external GC must not run concurrently with serving writes. A future multi-process design would need a transactional mark/sweep protocol or a shared coordination mechanism to close the existence-check race.

Blob deletion checks `IsReferenced` before removing the file. A referenced object returns `409 Conflict`. This protects named content from the explicit delete endpoint. Garbage collection uses the complete mark set returned by `Marked` and has a separate grace-period rule.

## 6. Garbage collection is conservative mark-and-sweep

Objects are immutable but not necessarily reachable forever. References can be deleted or moved, so the filesystem eventually contains objects that no current name uses. The `gc` command in `internal/commands/gc.go:35-87` performs explicit collection.

The algorithm is:

```text
marked = SELECT all ref.digest values
cutoff = current_time - grace_period

for each digest found below data-dir/sha256:
    if digest in marked:
        keep
        continue

    stat object
    if modification_time > cutoff:
        keep
        continue

    delete object
```

The grace period prevents a newly uploaded but not-yet-referenced object from being deleted immediately. It also gives operators a recovery window after a process failure or a delayed reference update. The default is 168 hours.

Version one does not coordinate a separate GC process with a serving process. The operations playbook explicitly says not to run two binaries against one PVC and not to run external GC concurrently with writes. The Deployment therefore has one replica and uses `strategy: Recreate`.

A future multi-process implementation must solve these cases explicitly:

- an upload completes before its reference transaction commits;
- a reference update races with an object sweep;
- a database snapshot and filesystem snapshot represent different points in time;
- two collectors observe the same unreferenced object.

The current implementation chooses an operational single-writer rule rather than claiming a distributed coordination protocol that does not exist.

## 7. Glazed owns CLI configuration; the application owns runtime behavior

The executable entry point is `cmd/cas-server/main.go:16-66`. It constructs a Cobra root command, initializes Glazed logging, creates the `serve`, `check`, and `gc` commands, and converts each Glazed command description into a Cobra command.

The command descriptions use:

- `github.com/go-go-golems/glazed/pkg/cmds` for command interfaces and descriptions;
- `pkg/cmds/fields` for typed fields and defaults;
- `pkg/cmds/schema` for section decoding;
- `pkg/cmds/values` for parsed configuration values;
- `pkg/middlewares` and `pkg/types` for structured command output.

The separation matters. Glazed parses command-line arguments and environment values. `internal/cas`, `internal/refs`, and `internal/httpapi` do not depend on Cobra or on command parsing. This keeps storage behavior directly testable and leaves the HTTP handler usable from `httptest` without constructing a CLI.

### `serve`

`serve` accepts:

```text
--listen             default :8080
--data-dir           required
--max-blob-bytes     default 10737418240
--auth-token         optional secret
--shutdown-timeout   default 10s
```

`ServeCommand.Run` decodes values, parses the shutdown duration, applies runtime defaults, validates required configuration, creates the CAS store, opens SQLite, constructs the handler, and starts an `http.Server` with bounded header, read, write, and idle timeouts.

The process lifecycle is:

```mermaid
flowchart TD
    A[Decode Glazed values] --> B[Validate configuration]
    B --> C[Create data directories]
    C --> D[Open SQLite refs]
    D --> E[Construct HTTP handler]
    E --> F[Start http.Server]
    F --> G{SIGINT or SIGTERM?}
    G -->|no| F
    G -->|yes| H[Server.Shutdown with timeout]
    H --> I[Close refs database]
    I --> J[Exit]

    style B fill:#e76f51,stroke:#9b2226,color:#fff
    style D fill:#264653,stroke:#2a9d8f,color:#fff
    style H fill:#2a9d8f,stroke:#264653,color:#fff
```

`signal.NotifyContext` receives SIGINT and SIGTERM. A goroutine calls `Server.Shutdown` with the configured timeout. The refs database closes after `ListenAndServe` returns. The server logs a warning when no bearer token is configured.

### `check`

`check` creates the store and refs database, lists objects, and optionally recomputes every object's digest with `--verify`. It emits structured Glazed output containing the data directory, object count, verification count, and database readiness.

### `gc`

`gc` requires a data directory and parses a non-negative grace period. It returns structured counts for objects scanned and deleted. It does not run automatically in the HTTP process.

## 8. k3s deployment encodes the storage boundary

The deployment artifacts are under `/home/manuel/code/wesen/2026-08-07--cas-content-addressed-store/deploy/k8s/`. The runtime assumptions are visible in `deployment.yaml`:

- exactly one replica;
- `strategy: Recreate`;
- non-root UID/GID `65532`;
- `ReadWriteOnce` PVC;
- read-only container root filesystem;
- all Linux capabilities dropped;
- privilege escalation disabled;
- writable access only at `/var/lib/cas`;
- liveness probe at `/healthz`;
- readiness probe at `/readyz`;
- resource requests and limits;
- 30-second termination grace period.

The PVC in `deploy/k8s/pvc.yaml` requests 100 GiB and requires a cluster-specific storage class decision. The Service is ClusterIP. The NetworkPolicy currently has a broad namespace selector and must be narrowed to the actual internal callers before production deployment. The Secret example is intentionally separate from the Kustomization so a token is not committed to the repository.

The container uses a multi-stage Dockerfile:

```dockerfile
FROM golang:1.25 AS build
# download modules and compile with CGO disabled

FROM gcr.io/distroless/static-debian12:nonroot
# copy only the compiled binary
```

The SQLite driver is pure Go, so the build uses `CGO_ENABLED=0`. The final image contains the server binary and a non-root distroless runtime. The image build was executed successfully as `cas-server:completion` after the final code hardening.

### Backup invariant

A valid backup contains both:

```text
<data-dir>/sha256/
<data-dir>/metadata.db
```

Copying only the database loses blob bytes. Copying only the object tree loses logical names. The recommended procedure scales the Deployment to zero, obtains a consistent filesystem/CSI snapshot or file backup, runs `cas-server check --verify` against a restore directory, and then starts the replica again.

## 9. Validation was part of the implementation

The project has tests at three layers.

### Storage tests

`internal/cas/store_test.go` verifies:

- concurrent identical uploads produce one valid digest-addressed object;
- oversized uploads remove temporary files;
- corrupt object contents are detected by `VerifyAll`;
- malformed object paths are reported;
- malformed internal digest values are rejected.

`internal/refs/store_test.go` verifies reference CRUD, mark-set generation, reference detection, and name validation.

### HTTP tests

`internal/httpapi/handler_test.go` verifies:

- unauthenticated data routes are rejected when a token is configured;
- health routes remain accessible;
- PUT returns a digest and byte count;
- HEAD returns object length without body transfer;
- GET returns exact bytes;
- reference creation succeeds only for an existing object;
- deletion of a referenced object returns `409`;
- deletion of a missing object returns `404`;
- oversized bodies return `413`;
- malformed digests return `400`.

### Command and integration validation

The final validation matrix passed:

```text
go test ./...
go test -race ./...
go vet ./...
golangci-lint run ./...
glazed-lint -glazedclilint ./...
./scripts/smoke.sh
make smoke
kubectl kustomize deploy/k8s
kubectl apply --dry-run=client -f <rendered-kustomization>
docker build --tag cas-server:completion .
docmgr doctor --ticket CAS-001 --stale-after 30 --details
```

`glazed-lint -glazedclilint ./...` reported `0 issues`. `docmgr doctor` reported `All checks passed`. The smoke script starts the binary on an ephemeral local port, waits for readiness, performs an authenticated upload, downloads the returned digest, compares bytes, and runs `check --verify --output json`.

A failure in the first smoke audit exposed a script assumption: the script required `./cas-server` even when the audit built the binary elsewhere. Commit `fd3f292` changed the script to build a temporary binary automatically when `CAS_SERVER_BIN` is not set. This is a useful validation rule: a smoke script should either build its own executable or accept an explicit binary path, and the default behavior should be deterministic from a clean checkout.

## 10. Design choices and rejected alternatives

### Filesystem loose objects instead of SQLite blob payloads

SQLite stores references but not blob contents. Large byte streams remain under filesystem control, and a digest resolves directly to a regular file. Storing blobs inside SQLite would couple object storage to database page management and make large-object backup and transfer behavior less explicit.

### SQLite instead of Postgres

The deployment has one replica and one PVC. SQLite provides transactional upserts and a small operational surface without requiring a database service. Postgres becomes appropriate when references are mutated by multiple application instances or when the metadata layer needs independent availability and scaling.

### Standard `net/http` instead of a web framework

The API has a small number of routes with explicit digest and reference validation. Standard `http.Server` supplies timeouts, shutdown, request bodies, and response handling without introducing a router abstraction into the storage design. The handler remains directly testable through `httptest`.

### Optional bearer token instead of embedded OIDC or mTLS

The binary is intended for an internal network behind cluster-managed TLS. A single Secret-backed bearer token provides a small write protection boundary without requiring identity-provider integration in version one. It is not a multi-tenant authorization system and should not be treated as one.

### Loose files instead of packfiles

One file per object is appropriate for normal-sized blobs and keeps the implementation inspectable. Large populations of tiny objects can make inode consumption and directory traversal expensive. That workload justifies a packfile/index design only after measurements demonstrate the need; the storage interface leaves room for that backend without adding it prematurely.

## 11. Scaling and correctness boundaries

The service is correct within a specific deployment model:

```text
one process
one ReadWriteOnce PVC
one SQLite metadata file
one filesystem namespace
explicit GC maintenance
cluster-managed TLS
```

The following changes require architectural work rather than only changing a flag:

- multiple replicas sharing one volume;
- multiple independent writers using separate processes;
- replication across nodes;
- cross-region durability;
- billions of tiny objects;
- multipart or resumable uploads;
- client-visible range requests;
- encryption-at-rest key management;
- S3 protocol compatibility.

The `CAS` abstraction can support a future backend, but the semantics must remain explicit. An object-store backend would need to preserve digest identity, duplicate-upload behavior, reference updates, deletion protection, GC reachability, and error mapping. Replacing the filesystem with S3 does not automatically preserve those properties.

## 12. Reproduction and operator workflow

### Local server

```bash
go run ./cmd/cas-server serve \
  --listen 127.0.0.1:8080 \
  --data-dir "$PWD/.local-data" \
  --auth-token local-development-token
```

### Upload and retrieve

```bash
response=$(curl -fsS -X PUT \
  -H 'Authorization: Bearer local-development-token' \
  --data-binary @artifact.bin \
  http://127.0.0.1:8080/v1/blobs)
printf '%s\n' "$response"

curl -fS \
  -H 'Authorization: Bearer local-development-token' \
  http://127.0.0.1:8080/v1/blobs/sha256:<64-lowercase-hex> \
  -o artifact.downloaded
cmp artifact.bin artifact.downloaded
```

### Check and collect

```bash
./cas-server check --data-dir /var/lib/cas --verify
./cas-server gc --data-dir /var/lib/cas --grace-period 168h --output json
./cas-server check --data-dir /var/lib/cas
```

Do not run GC concurrently with serving writes. Run a full verification before deletion. Keep the grace period long enough to cover the expected delay between uploads and reference creation.

### Deploy

```bash
docker build -t ghcr.io/wesen/cas-server:latest .
docker push ghcr.io/wesen/cas-server:latest
kubectl -n internal create secret generic cas-server-auth \
  --from-literal=token="$(openssl rand -hex 32)" \
  --dry-run=client -o yaml | kubectl apply -f -
kubectl -n internal apply -k deploy/k8s
kubectl -n internal rollout status deployment/cas-server
```

Before production rollout, set the PVC storage class, narrow the NetworkPolicy, configure ingress request timeouts for large uploads, and confirm that the backup procedure captures both SQLite and the object tree.

## 13. Working rules

The implementation supports these rules:

1. Compute identity from bytes received by the server. Never trust a client-supplied digest as the source of identity.
2. Write to a temporary file before exposing a digest path.
3. Synchronize the file before installation and synchronize the containing directory after installation.
4. Keep immutable bytes and mutable references in separate storage domains.
5. Treat reference reachability as the input to garbage collection.
6. Use a grace period for unreferenced objects.
7. Reject malformed digests and object paths before deriving filesystem paths.
8. Keep the single-writer PVC boundary visible in deployment configuration and operations documentation.
9. Test concurrent duplicate writes, oversized inputs, corrupted objects, missing deletes, auth failures, and malformed URL input.
10. Treat validation scripts as production artifacts: they must be reproducible from a clean checkout and must not depend on an accidentally present binary.

## Related project artifacts

- CAS-001 design guide: `/home/manuel/code/wesen/2026-08-07--cas-content-addressed-store/ttmp/2026/08/07/CAS-001--content-addressable-blob-server/design-doc/01-cas-blob-server-design-and-intern-implementation-guide.md`
- CAS-001 diary: `/home/manuel/code/wesen/2026-08-07--cas-content-addressed-store/ttmp/2026/08/07/CAS-001--content-addressable-blob-server/reference/01-implementation-diary.md`
- CAS-001 operations playbook: `/home/manuel/code/wesen/2026-08-07--cas-content-addressed-store/ttmp/2026/08/07/CAS-001--content-addressable-blob-server/playbook/01-operations-and-validation-playbook.md`
- Repository README: `/home/manuel/code/wesen/2026-08-07--cas-content-addressed-store/README.md`
- Project source: `/home/manuel/code/wesen/2026-08-07--cas-content-addressed-store/`
