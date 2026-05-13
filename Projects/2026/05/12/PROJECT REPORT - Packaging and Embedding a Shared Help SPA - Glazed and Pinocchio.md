---
title: "Packaging and Embedding a Shared Help SPA — Glazed and Pinocchio Deep Dive"
aliases:
  - Glazed shared help SPA report
  - Pinocchio embedded help browser report
  - Packaging and embedding a shared SPA
  - Glazed SPA release asset workflow
tags: [project-report, glazed, pinocchio, go, spa, embed, goreleaser, github-actions, documentation, release-engineering]
status: active
type: project-report
created: 2026-05-12
repo: /home/manuel/workspaces/2026-05-12/fix-serve-http-docs/glazed
related_repos:
  - /home/manuel/workspaces/2026-05-12/fix-serve-http-docs/pinocchio
  - /home/manuel/workspaces/2026-05-12/fix-serve-http-docs/glazed
source_ticket: GLZ-SPA-RELEASE
source_issue: go-go-golems/glazed#571
related_prs:
  - https://github.com/go-go-golems/glazed/pull/574
  - https://github.com/go-go-golems/glazed/pull/575
  - https://github.com/go-go-golems/glazed/pull/576
  - https://github.com/go-go-golems/glazed/pull/577
  - https://github.com/go-go-golems/glazed/pull/578
  - https://github.com/go-go-golems/pinocchio/pull/151
release_artifact: https://github.com/go-go-golems/glazed/releases/download/v1.2.13/glazed-spa-1.2.13.tar.gz
---

# Packaging and Embedding a Shared Help SPA — Glazed and Pinocchio Deep Dive

This report explains how we turned the Glazed help browser SPA into a reusable release artifact and embedded it into Pinocchio so `pinocchio serve` can provide a local browser UI without committing JavaScript bundles to the Pinocchio repository. The goal is not only to record the commands that worked. The goal is to teach the design: what is produced, what is consumed, what must be stable between projects, why the release pipeline had to be arranged in a particular order, and what failure modes appeared once the design met GitHub Actions, GoReleaser split builds, `go:embed`, and package-filtered help APIs.

> [!summary]
> Glazed now publishes its built help browser as a versioned GitHub Release asset such as `glazed-spa-1.2.13.tar.gz`. Pinocchio reads its pinned Glazed module version from `go.mod`, downloads the matching SPA tarball, embeds it under `pkg/spa/dist/`, and serves it through the Glazed help HTTP API. The final local smoke test is: `make fetch-spa build-with-spa`, `./pinocchio serve`, `curl /api/health`, and a browser request to `/`; the validated result is a real SPA with 53 Pinocchio help sections.

## The shortest version

The final working path is compact:

```text
Glazed release v1.2.13
  -> GitHub Release asset: glazed-spa-1.2.13.tar.gz
  -> Pinocchio go.mod pins github.com/go-go-golems/glazed v1.2.13
  -> make fetch-spa downloads the matching asset
  -> pkg/spa/dist/index.html exists locally but is git-ignored
  -> go build -tags embed -o ./pinocchio ./cmd/pinocchio
  -> ./pinocchio serve exposes /api/... and the SPA at /
```

The smoke test that proved the system was working was:

```bash
cd /home/manuel/workspaces/2026-05-12/fix-serve-http-docs/pinocchio
make fetch-spa build-with-spa
./pinocchio serve --address :18893
```

In another terminal:

```bash
curl -I http://localhost:18893/
curl -s http://localhost:18893/api/health
curl -s 'http://localhost:18893/api/sections?package=pinocchio' | jq '.sections | length'
```

The expected outputs are:

```text
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
```

```json
{"ok":true,"sections":53}
```

```text
53
```

Those outputs matter because they verify three different layers. The first verifies that the SPA handler is active and serving HTML. The second verifies that the help API is loaded. The third verifies that package-filtered queries work with the package name the browser receives from `/api/packages`.

## Why this work existed

Glazed already had a browser help UI. The `glaze serve` command could start an HTTP server, expose `/api/...`, and serve a React SPA that browsed the loaded help sections. That solved Glazed's own documentation browser, but it did not solve the downstream case.

Pinocchio is also a Glazed-based CLI. It has its own embedded docs, prompt repository docs, Catter docs, and optional workspace docs. It should be able to run:

```bash
pinocchio serve
```

and open a browser over its own help tree. The difficulty is that the SPA source and build pipeline belong to Glazed, not Pinocchio. We did not want to copy generated JavaScript into Pinocchio. We also did not want every downstream project to learn how to build the Glazed frontend with Dagger, Node, pnpm, Vite, and Go embed tags.

The resulting design separates ownership:

- Glazed owns the SPA source, frontend build, and release asset.
- Pinocchio owns its help content, serve command, and final binary embedding.
- The boundary between them is a versioned tarball attached to a GitHub Release.

This is a simple boundary, but it is also a strict boundary. The tarball must exist at a predictable URL. The downstream Makefile must derive that URL from the same version that Go uses in `go.mod`. The embedded filesystem must expose the same paths that the HTTP handler expects. The help API must provide package metadata that the SPA can use for filtering. Each of those requirements became visible through a specific failure.

## The architecture after the work

The final architecture has one producer and one consumer.

```mermaid
flowchart TD
    subgraph Glazed[Glazed release producer]
        WebSrc[web/ React + Vite source]
        BuildWeb[go generate ./pkg/web]
        Public[pkg/web/embed/public]
        Tar[glazed-spa.tar.gz]
        Release[GitHub Release v1.2.13]
        Asset[glazed-spa-1.2.13.tar.gz]

        WebSrc --> BuildWeb --> Public --> Tar --> Release --> Asset
    end

    subgraph Pinocchio[Pinocchio release consumer]
        GoMod[go.mod pins glazed v1.2.13]
        Fetch[make fetch-spa]
        Dist[pkg/spa/dist/]
        Embed[go build -tags embed]
        Binary[pinocchio binary]
        Serve[pinocchio serve]

        GoMod --> Fetch
        Asset --> Fetch --> Dist --> Embed --> Binary --> Serve
    end

    subgraph Runtime[Runtime HTTP behavior]
        API[/api/health, /api/packages, /api/sections]
        SPA[/ and browser routes]
        HelpStore[Glazed HelpSystem Store]

        Serve --> API
        Serve --> SPA
        API --> HelpStore
    end
```

The important property is that the SPA is not the documentation model. The documentation model remains the Glazed help store. The SPA is a renderer over `/api/...`. That means Pinocchio can load its own help pages, assign package metadata, and let the same browser UI render them. The frontend bundle does not have to be recompiled for each downstream tool.

## The conceptual model

A reusable embedded SPA has four parts:

1. **A static asset bundle.** This is the output of the frontend build: `index.html`, `site-config.js`, and hashed JS/CSS assets.
2. **A stable backend API.** The SPA needs endpoints such as `/api/packages`, `/api/sections`, and `/api/sections/{slug}`. It should not know whether the content came from Glazed, Pinocchio, JSON export, SQLite, or embedded markdown.
3. **A packaging contract.** The producer must publish the asset under a predictable name, and the consumer must derive the correct download URL.
4. **An embed contract.** The consumer must place files under a directory that `go:embed` can see and expose those files with the path root expected by the HTTP handler.

The design fails when any one of these contracts is implicit. The work in Glazed and Pinocchio made them explicit.

## The producer side: Glazed builds and publishes the SPA

Glazed has the frontend source under:

```text
/home/manuel/workspaces/2026-05-12/fix-serve-http-docs/glazed/web
```

The generated embed output lives under:

```text
/home/manuel/workspaces/2026-05-12/fix-serve-http-docs/glazed/pkg/web/embed/public
```

The Go package that serves those assets is:

```text
/home/manuel/workspaces/2026-05-12/fix-serve-http-docs/glazed/pkg/web
```

The initial idea was to create `glazed-spa.tar.gz` inside `.goreleaser.yaml` `before.hooks`. That was wrong for this repository because the release workflow uses GoReleaser's split/merge mode.

Split/merge mode changes where artifacts exist:

```text
goreleaser-linux job
  -> runs goreleaser release --split
  -> writes dist/linux/...
  -> uploads dist/ as artifact

goreleaser-darwin job
  -> runs goreleaser release --split
  -> writes dist/darwin/...
  -> uploads dist/ as artifact

goreleaser-merge job
  -> checks out a fresh worktree
  -> downloads dist artifacts
  -> runs goreleaser continue --merge
  -> publishes GitHub Release
```

`release.extra_files` is evaluated in the merge job. A tarball produced only in a split job is not present there unless we explicitly upload and copy it. The corrected design builds the SPA tarball directly in the merge job immediately before `goreleaser continue --merge`:

```yaml
- name: Build SPA release asset
  run: |
    go generate ./pkg/web
    tar czf glazed-spa.tar.gz -C pkg/web/embed/public .
```

The GoReleaser config then attaches that local file with a versioned public name:

```yaml
release:
  extra_files:
    - glob: ./glazed-spa.tar.gz
      name_template: glazed-spa-{{ .Version }}.tar.gz
```

For tag `v1.2.13`, GoReleaser's `.Version` is `1.2.13`, so the asset is:

```text
glazed-spa-1.2.13.tar.gz
```

The tag keeps the leading `v`; the asset filename does not.

## Why the release asset is versioned

The asset must match the Go module version that downstream projects build against. Pinocchio's `go.mod` says:

```text
github.com/go-go-golems/glazed v1.2.13
```

That version identifies both the Go API and the expected SPA asset. If the URL were unversioned, downstream builds would have to trust mutable release state. If the asset were copied into Pinocchio, every Glazed UI change would become a Pinocchio repository change. The versioned asset keeps the boundary precise:

```text
module version:       v1.2.13
release tag:          v1.2.13
release asset file:   glazed-spa-1.2.13.tar.gz
```

The download URL contains both version forms:

```text
https://github.com/go-go-golems/glazed/releases/download/v1.2.13/glazed-spa-1.2.13.tar.gz
```

The downstream Makefile must therefore keep two variables:

```makefile
GLAZED_VERSION := v1.2.13
GLAZED_VERSION_NO_V := 1.2.13
```

That detail produced a real failure. Pinocchio first tried to fetch `glazed-spa-v1.2.13.tar.gz`, then we corrected it to strip the leading `v` only for the filename.

## The consumer side: Pinocchio fetches and embeds the SPA

Pinocchio's final consumer-side shape lives in these files:

| File | Role |
|---|---|
| `/home/manuel/workspaces/2026-05-12/fix-serve-http-docs/pinocchio/Makefile` | Defines `fetch-spa`, `clean-spa`, and `build-with-spa`. |
| `/home/manuel/workspaces/2026-05-12/fix-serve-http-docs/pinocchio/.goreleaser.yaml` | Runs `make fetch-spa` before release builds and builds with tag `embed`. |
| `/home/manuel/workspaces/2026-05-12/fix-serve-http-docs/pinocchio/pkg/spa/embed.go` | Embed-mode asset filesystem. |
| `/home/manuel/workspaces/2026-05-12/fix-serve-http-docs/pinocchio/pkg/spa/embed_none.go` | Non-embed development fallback and placeholder. |
| `/home/manuel/workspaces/2026-05-12/fix-serve-http-docs/pinocchio/pkg/spa/spa.go` | HTTP handler for `index.html`, static assets, and SPA fallback routes. |
| `/home/manuel/workspaces/2026-05-12/fix-serve-http-docs/pinocchio/cmd/pinocchio/cmds/serve.go` | Cobra serve command and HTTP server lifecycle. |
| `/home/manuel/workspaces/2026-05-12/fix-serve-http-docs/pinocchio/cmd/pinocchio/main.go` | Passes the initialized help system into the serve command. |

The Makefile reads the Glazed version directly from `go.mod`:

```makefile
GLAZED_VERSION := $(shell grep 'go-go-golems/glazed ' go.mod | head -1 | awk '{print $$2}')
GLAZED_VERSION_NO_V := $(patsubst v%,%,$(GLAZED_VERSION))
GLAZED_SPA_DIR := pkg/spa/dist

fetch-spa:
	@if [ -z "$(GLAZED_VERSION)" ]; then echo "Warning: cannot detect glazed version from go.mod, skipping SPA fetch"; exit 0; fi
	@mkdir -p $(GLAZED_SPA_DIR)
	@echo "Fetching SPA assets for glazed $(GLAZED_VERSION)..."
	@curl -sfL https://github.com/go-go-golems/glazed/releases/download/$(GLAZED_VERSION)/glazed-spa-$(GLAZED_VERSION_NO_V).tar.gz \
		| tar xz -C $(GLAZED_SPA_DIR) \
	|| (echo "Warning: SPA assets not found for glazed $(GLAZED_VERSION), building without browser UI"; rm -rf $(GLAZED_SPA_DIR))
```

The reason for parsing `go.mod` directly is not preference. In a multi-repo workspace, `go list -m` can report `(devel)` or otherwise reflect workspace state instead of the pinned module version. The release asset must match the version in the module file, so `go.mod` is the source of truth.

The final build target is intentionally narrow:

```makefile
build-with-spa: fetch-spa
	go build -tags embed -o ./pinocchio ./cmd/pinocchio
```

Earlier versions ran `go generate ./...`. That was wrong for the downstream consumer path. Pinocchio should not rebuild the Glazed SPA. It should fetch the already-built asset and compile the command that embeds it. Removing `go generate` also avoids triggering unrelated frontend build scripts in Pinocchio, such as the `cmd/web-chat` frontend generation.

## The `go:embed` root problem

The most concrete Go bug in the integration was an embedded filesystem root mismatch. The first Pinocchio embed file used this form:

```go
//go:embed dist
var Assets embed.FS
```

The SPA handler read:

```go
fs.ReadFile(Assets, "index.html")
```

Those two pieces do not agree. `//go:embed dist` preserves the `dist/` prefix. The embedded filesystem contains:

```text
dist/index.html
```

not:

```text
index.html
```

The runtime symptom was:

```text
WRN SPA handler not available, serving API only error="reading SPA assets: open index.html: file does not exist (run 'make fetch-spa' and rebuild with -tags embed)"
```

The files were present, but the handler looked at the wrong root. The corrected embed file creates a sub-filesystem rooted at `dist`:

```go
//go:build embed

package spa

import (
    "embed"
    "io/fs"
)

//go:embed dist
var embeddedAssets embed.FS

var Assets fs.FS = mustSub(embeddedAssets, "dist")

func mustSub(fsys fs.FS, dir string) fs.FS {
    sub, err := fs.Sub(fsys, dir)
    if err != nil {
        panic(err)
    }
    return sub
}
```

This gives embed mode the same root path behavior as the non-embed development fallback:

```go
os.DirFS(filepath.Join(dir, "pkg", "spa", "dist"))
```

Both modes now expose `index.html` at the root of `Assets`. That is the invariant the HTTP handler needs.

## The HTTP handler contract

The SPA handler has three responsibilities:

1. Serve `index.html` at `/`.
2. Serve real static assets when the path exists in the asset filesystem.
3. Serve `index.html` for unknown non-API browser routes so client-side routing can run.

The simplified shape is:

```go
func NewHandler() (http.Handler, error) {
    indexBytes, err := fs.ReadFile(Assets, "index.html")
    if err != nil {
        return nil, fmt.Errorf("reading SPA assets: %w", err)
    }

    fileServer := http.FileServer(http.FS(Assets))
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        cleanPath := path.Clean("/" + r.URL.Path)
        if cleanPath == "/" {
            serveSPAIndex(w, r, indexBytes)
            return
        }

        assetPath := strings.TrimPrefix(cleanPath, "/")
        if _, err := fs.Stat(Assets, assetPath); err == nil {
            fileServer.ServeHTTP(w, r)
            return
        }

        serveSPAIndex(w, r, indexBytes)
    }), nil
}
```

The Glazed help server owns the API routes. Pinocchio passes the SPA handler into Glazed's `helpserver.NewServeHandler`:

```go
handler := helpserver.NewServeHandler(
    helpserver.HandlerDeps{Store: hs.Store},
    spaHandler,
)
```

The combined handler can then route `/api/...` to the help API and browser paths to the SPA.

## The help data contract

The SPA does not render arbitrary markdown files directly. It renders sections from the help API. The relevant endpoints are:

```text
GET /api/health
GET /api/packages
GET /api/sections
GET /api/sections?package=pinocchio
GET /api/sections/{slug}
```

The browser uses package metadata to decide which sections to show. That made package assignment a correctness issue, not a display detail.

The first Glazed fix for issue #571 addressed empty sections by having `NewServeHandler` call the store's default-package assignment. In Pinocchio PR review, we made the downstream behavior explicit as well:

```go
if err := hs.Store.SetDefaultPackage(ctx, "pinocchio", ""); err != nil {
    return fmt.Errorf("assigning default help package: %w", err)
}
```

The smoke test confirmed the package-filtered path:

```bash
curl -s http://localhost:18894/api/packages
```

```json
{
  "packages": [
    {
      "name": "pinocchio",
      "displayName": "Pinocchio",
      "versions": [],
      "sectionCount": 53
    }
  ],
  "defaultPackage": "pinocchio"
}
```

Then:

```bash
curl -s 'http://localhost:18894/api/sections?package=pinocchio' | jq '.sections | length'
```

returned:

```text
53
```

This is the right test because it verifies the same filter that the browser uses after reading `/api/packages`.

## Reusing the initialized help system

Pinocchio's first `serve` implementation created a fresh help system inside `runServe`. That loaded the built-in docs we remembered to load there, but it did not necessarily include the same help content that the normal CLI had already loaded.

The normal startup path is:

```text
main()
  -> initRootCmd()
       creates helpSystem
       loads base docs
       registers help command
       registers serve command
  -> initAllCommands(helpSystem)
       loads configured prompt repositories
       loads repository doc directories
       registers dynamic commands
  -> rootCmd.Execute()
       runs selected subcommand
```

The serve command should use the pointer that flows through that sequence. Creating a new `help.NewHelpSystem()` inside `runServe` discards repository docs and dynamic command docs. The corrected code captures the initialized help system when the command is registered:

```go
rootCmd.AddCommand(pinocchio_cmds.NewServeCommand(helpSystem))
```

and then uses it at execution time:

```go
func NewServeCommand(hs *help.HelpSystem) *cobra.Command {
    // ...
    RunE: func(cmd *cobra.Command, args []string) error {
        return runServe(cmd.Context(), address, hs)
    },
}
```

The pointer is created before `initAllCommands`, but it is the same object. `initAllCommands(helpSystem)` mutates that object before Cobra executes `serve`, so the serve command sees the populated store.

## The release pipeline failures and what each one taught

The implementation did not fail once. It failed in several different places, and each failure exposed a separate invariant.

### Failure 1: split GoReleaser jobs do not preserve root files

The first implementation created `glazed-spa.tar.gz` in GoReleaser `before.hooks`. That looked correct until we accounted for split/merge release mode. The merge job publishes the release from a fresh checkout plus downloaded `dist` artifacts. A tarball made in a split job's root directory is not automatically present in the merge job.

The fix was to build the SPA tarball in the merge job, immediately before `goreleaser continue --merge`.

Working rule: if GoReleaser publishes an extra file during `continue --merge`, create that file in the merge job or explicitly pass it as an artifact into that job.

### Failure 2: macOS runners had no usable Dagger image driver and no pnpm

The `v1.2.10` release failed in `goreleaser-darwin`:

```text
Dagger build failed ... driver for scheme "image" was not available
falling back to local pnpm
local build also failed: pnpm not found in PATH
pkg/web/gen.go:1: running "go": exit status 1
```

The Glazed frontend generator tries Dagger first and local pnpm second. On the macOS runner, the Dagger path failed and pnpm was not installed. The fix was to install Node 22 and activate pnpm through Corepack before GoReleaser or `go generate` ran:

```yaml
- uses: actions/setup-node@v6
  with:
    node-version: '22'
- name: Enable pnpm
  run: corepack enable && corepack prepare pnpm@10.15.0 --activate
```

Working rule: if a build script has a local fallback, CI must install the fallback dependencies on every runner where the primary path can fail.

### Failure 3: setup-node pnpm caching requires pnpm before cache lookup

A review pointed out that enabling `cache: pnpm` before Corepack activated pnpm could fail because setup-node resolves the pnpm cache path during action execution. We tried splitting setup-node into two steps: setup Node, enable pnpm, then setup Node with pnpm caching.

That fixed the ordering concern but exposed the next failure.

Working rule: setup-node's package-manager cache is not just a passive optimization; it executes package-manager-specific path lookup logic.

### Failure 4: setup-node pnpm cache failed in post-job cleanup

The `v1.2.11` linux build succeeded, uploaded artifacts, and then failed during setup-node post-job cleanup:

```text
Error: Path Validation Error: Path(s) specified in the action for caching do(es) not exist, hence no cache is being saved.
```

On linux, Dagger successfully handled generation, so local pnpm did not necessarily create a store path. The setup-node cache action then tried to save a non-existent path and failed the job.

The fix was to remove pnpm caching from the release workflow. The release needs pnpm availability for correctness. It does not need pnpm cache persistence for correctness.

Working rule: do not make cache state part of release correctness when the tool being cached is only a fallback path.

### Failure 5: Fury publisher tried to publish the SPA tarball

The `v1.2.12` release published the GitHub Release and uploaded `glazed-spa-1.2.12.tar.gz`. Then the custom Fury publisher tried to upload the SPA tarball:

```text
custom publisher
publishing cmd=curl artifact=glazed-spa-1.2.12.tar.gz
curl: (26) Failed to open/read local data from file/application
```

Fury is for `.deb` and `.rpm` package artifacts. The SPA tarball belongs only on the GitHub Release. GoReleaser still passed the SPA artifact into the custom publisher path, so the command itself had to guard by file type:

```yaml
cmd: >-
  sh -c 'case "$1" in
    *.deb|*.rpm) curl -F package=@"$1" "https://$FURY_TOKEN@push.fury.io/go-go-golems/" ;;
    *) echo "skipping non-package artifact $1 for fury.io" ;;
  esac' -- "{{ .ArtifactName }}"
```

Working rule: if a custom publisher is semantically limited to package formats, encode that limit in the command even if GoReleaser `ids` are configured.

### Failure 6: the downstream asset filename used the wrong version form

Pinocchio initially fetched the wrong asset name. The tag includes `v`; the asset filename does not. The correct URL for Glazed `v1.2.13` is:

```text
https://github.com/go-go-golems/glazed/releases/download/v1.2.13/glazed-spa-1.2.13.tar.gz
```

Working rule: derive both the tag version and the filename version from `go.mod`; do not type either one by hand in release scripts.

### Failure 7: `go generate` still ran in the downstream build

`make build-with-spa` originally ran:

```makefile
go generate ./...
go build -tags embed ./...
```

That was the wrong consumer build. The downstream path should consume the prebuilt Glazed asset. It should not rebuild local frontends or run unrelated generation steps. The corrected target is:

```makefile
build-with-spa: fetch-spa
	go build -tags embed -o ./pinocchio ./cmd/pinocchio
```

Working rule: a downstream embed build should be narrower than the repository's general development build.

### Failure 8: `//go:embed dist` preserved the prefix

The final local bug was `open index.html: file does not exist`. The files were embedded under `dist/index.html`, while the handler read `index.html`. The fix was `fs.Sub`.

Working rule: make embed mode and dev fallback mode expose the same filesystem root.

## The final implementation sequence

A future downstream project can reproduce the pattern in this order.

### 1. Publish the SPA from Glazed

In Glazed:

1. Build the SPA in the GoReleaser merge job.
2. Create `glazed-spa.tar.gz` from `pkg/web/embed/public`.
3. Attach it with `name_template: glazed-spa-{{ .Version }}.tar.gz`.
4. Ensure Node and pnpm are available before any `go generate` path that can need local pnpm.
5. Keep package publishers from treating the SPA tarball as a package artifact.

The release should produce:

```text
glazed-spa-1.2.13.tar.gz
```

### 2. Fetch the asset in the downstream repo

In the downstream Makefile:

```makefile
GLAZED_VERSION := $(shell grep 'go-go-golems/glazed ' go.mod | head -1 | awk '{print $$2}')
GLAZED_VERSION_NO_V := $(patsubst v%,%,$(GLAZED_VERSION))
GLAZED_SPA_DIR := pkg/spa/dist
```

Then fetch:

```makefile
curl -sfL https://github.com/go-go-golems/glazed/releases/download/$(GLAZED_VERSION)/glazed-spa-$(GLAZED_VERSION_NO_V).tar.gz \
  | tar xz -C $(GLAZED_SPA_DIR)
```

### 3. Embed the fetched directory

In `pkg/spa/embed.go`:

```go
//go:build embed

package spa

import (
    "embed"
    "io/fs"
)

//go:embed dist
var embeddedAssets embed.FS

var Assets fs.FS = mustSub(embeddedAssets, "dist")
```

In `pkg/spa/embed_none.go`, optionally provide a development fallback that searches for `pkg/spa/dist/index.html` on disk and otherwise serves a placeholder.

### 4. Serve the initialized help system

In the CLI root, create and populate one help system:

```go
helpSystem := help.NewHelpSystem()
// load built-in docs
// load repository docs
// register dynamic commands
rootCmd.AddCommand(pinocchio_cmds.NewServeCommand(helpSystem))
```

In the serve command:

```go
func runServe(ctx context.Context, address string, hs *help.HelpSystem) error {
    if err := hs.Store.SetDefaultPackage(ctx, "pinocchio", ""); err != nil {
        return err
    }

    spaHandler, err := spa.NewHandler()
    if err != nil {
        spaHandler = nil
    }

    handler := helpserver.NewServeHandler(
        helpserver.HandlerDeps{Store: hs.Store},
        spaHandler,
    )

    return http.ListenAndServe(address, handler)
}
```

### 5. Validate with package-filtered API calls

Do not stop at `curl /api/health`. Test the package-filtered path:

```bash
curl -s http://localhost:18888/api/packages | jq .
curl -s 'http://localhost:18888/api/sections?package=pinocchio' | jq '.sections | length'
curl -I http://localhost:18888/
```

A healthy result has:

- a nonzero section count in `/api/health`,
- a concrete package name in `/api/packages`,
- the same nonzero count through `/api/sections?package=<name>`,
- `200 OK` and HTML content at `/`.

## What changed in Glazed documentation

After the implementation worked, Glazed gained a dedicated help topic:

```text
pkg/doc/topics/30-distribute-help-browser-spa.md
```

The topic slug is:

```text
distribute-help-browser-spa
```

It documents the release asset naming, downstream Makefile, `fs.Sub` embed root, serve integration, smoke tests, and troubleshooting table. The existing `serve-help-over-http` topic was also updated to distinguish three external-consumer paths:

1. API-only mode, by passing `nil` as the SPA handler.
2. Centralized browsing, with `glaze serve --from-glazed-cmd`.
3. Standalone downstream embedding, by fetching and embedding the versioned `glazed-spa` release asset.

That distinction is important. API-only mode is still useful, but it is no longer the only recommended answer for external binaries that want their own browser UI.

## The final state

The work ended with these concrete results:

| Area | Result |
|---|---|
| Glazed issue #571 | Programmatic `NewServeHandler` no longer yields empty sections for embedded docs without package metadata. |
| Glazed release | `v1.2.13` publishes `glazed-spa-1.2.13.tar.gz`. |
| Glazed release workflow | Merge job builds the SPA tarball where GoReleaser publishes it. |
| Glazed CI setup | Node 22 and pnpm are available; pnpm caching is not part of release correctness. |
| Glazed custom publisher | Fury uploads only `.deb` and `.rpm`, not the SPA tarball. |
| Pinocchio fetch | `make fetch-spa` downloads the asset matching the pinned Glazed version. |
| Pinocchio embed | `pkg/spa/embed.go` exposes `dist/` as the filesystem root. |
| Pinocchio build | `make build-with-spa` fetches the asset and builds `./pinocchio` without `go generate`. |
| Pinocchio serve | `pinocchio serve` reuses the initialized help system and assigns package `pinocchio`. |
| Pinocchio validation | SPA root returns HTML; `/api/health` and package-filtered sections report 53 sections. |
| Glazed docs | `glaze help distribute-help-browser-spa` documents the end-to-end workflow. |

## Key implementation files

### Glazed

| Path | Why it matters |
|---|---|
| `/home/manuel/workspaces/2026-05-12/fix-serve-http-docs/glazed/.github/workflows/release.yaml` | Builds the SPA release asset in the merge job and sets up Node/pnpm for release generation. |
| `/home/manuel/workspaces/2026-05-12/fix-serve-http-docs/glazed/.goreleaser.yaml` | Publishes `glazed-spa-{{ .Version }}.tar.gz` and guards the Fury publisher. |
| `/home/manuel/workspaces/2026-05-12/fix-serve-http-docs/glazed/pkg/help/server/serve.go` | Programmatic serve handler and package assignment behavior. |
| `/home/manuel/workspaces/2026-05-12/fix-serve-http-docs/glazed/pkg/help/server/serve_test.go` | Regression tests for package/default serve behavior. |
| `/home/manuel/workspaces/2026-05-12/fix-serve-http-docs/glazed/pkg/doc/topics/25-serving-help-over-http.md` | Existing serve docs updated to point to the downstream SPA workflow. |
| `/home/manuel/workspaces/2026-05-12/fix-serve-http-docs/glazed/pkg/doc/topics/30-distribute-help-browser-spa.md` | New canonical documentation for downstream embedding. |

### Pinocchio

| Path | Why it matters |
|---|---|
| `/home/manuel/workspaces/2026-05-12/fix-serve-http-docs/pinocchio/Makefile` | Fetches the versioned SPA asset and builds `./pinocchio` with `-tags embed`. |
| `/home/manuel/workspaces/2026-05-12/fix-serve-http-docs/pinocchio/.goreleaser.yaml` | Runs `make fetch-spa` and builds release binaries with embed tags. |
| `/home/manuel/workspaces/2026-05-12/fix-serve-http-docs/pinocchio/pkg/spa/embed.go` | Embeds `dist/` and exposes it at the correct filesystem root. |
| `/home/manuel/workspaces/2026-05-12/fix-serve-http-docs/pinocchio/pkg/spa/embed_none.go` | Provides a non-embed fallback for development and diagnostics. |
| `/home/manuel/workspaces/2026-05-12/fix-serve-http-docs/pinocchio/pkg/spa/spa.go` | Serves the SPA entrypoint and static assets. |
| `/home/manuel/workspaces/2026-05-12/fix-serve-http-docs/pinocchio/cmd/pinocchio/cmds/serve.go` | Starts the HTTP server, uses the initialized help system, and assigns package metadata. |
| `/home/manuel/workspaces/2026-05-12/fix-serve-http-docs/pinocchio/cmd/pinocchio/main.go` | Passes the initialized help system into the serve command. |

## Working rules for future projects

- Publish frontend bundles as versioned release assets when the producer owns the frontend and consumers own their own binaries.
- Keep Go module version, release tag, and asset filename derivation in one place. For Go tags, expect the tag to include `v` and GoReleaser `.Version` to omit it.
- Build release extra files in the GoReleaser merge job when using split/merge releases.
- Install fallback build tools explicitly on CI runners where the primary build path may fail.
- Do not make cache paths part of release correctness unless the job always creates those paths.
- Keep package publishers scoped to package artifacts; skip SPA tarballs and other non-package release assets.
- Parse `go.mod` directly when workspace mode makes `go list -m` unsuitable for release asset selection.
- Do not run broad `go generate ./...` in a downstream consumer build that should only fetch and embed a published SPA.
- Use `fs.Sub` when `//go:embed dist` must expose `dist/` as the filesystem root.
- Reuse the initialized help system in `serve` commands so dynamically loaded docs are visible.
- Test package-filtered API calls, not only health endpoints.

## Commands worth keeping

### Check the Glazed release asset

```bash
gh release view v1.2.13 \
  --repo go-go-golems/glazed \
  --json url,assets \
  --jq '{url, assets: [.assets[].name]}'
```

### Fetch and build Pinocchio with the embedded SPA

```bash
cd /home/manuel/workspaces/2026-05-12/fix-serve-http-docs/pinocchio
make fetch-spa build-with-spa
```

### Serve and validate

```bash
./pinocchio serve --address :18888
```

```bash
curl -I http://localhost:18888/
curl -s http://localhost:18888/api/health
curl -s http://localhost:18888/api/packages | jq .
curl -s 'http://localhost:18888/api/sections?package=pinocchio' | jq '.sections | length'
```

### Validate the new Glazed help topic

```bash
cd /home/manuel/workspaces/2026-05-12/fix-serve-http-docs/glazed
go test ./pkg/doc ./pkg/help/... -count=1
go run ./cmd/glaze help distribute-help-browser-spa
```

## What this pattern gives us

The final design gives downstream tools a controlled way to use the Glazed help browser without copying frontend build outputs into every repository. The producer builds once and publishes a versioned artifact. The consumer pins a module version, downloads the corresponding asset, embeds it, and serves its own help model through the shared Glazed API.

The result is not a general web packaging system. It is a focused release engineering pattern for Go CLIs that expose structured documentation through a local browser UI. It works because the responsibilities are kept separate:

- The documentation model is still Go data in the help system.
- The browser UI is still a static asset bundle.
- The release asset is the distribution boundary.
- The downstream binary owns its own help content and server command.

That separation is what made the final Pinocchio smoke test meaningful. The UI came from Glazed. The content came from Pinocchio. The binary was built by Pinocchio. The API was the shared contract between them.

## Open follow-ups

The implementation works, but there are a few useful refinements left:

- Pinocchio's release path should grow a `FETCH_SPA_REQUIRED=1` mode so missing SPA assets fail at fetch time with a clear message instead of later through `go:embed`.
- Pinocchio's general pre-commit hook still runs `go generate ./...`; that is acceptable for full repo validation, but it should remain separate from `make build-with-spa`.
- Glazed's GoReleaser config still has unrelated deprecation warnings for `snapshot.name_template` and `brews`; those should be cleaned up separately.
- A small embed-tag regression test could assert that `spa.NewHandler()` can read `index.html` after assets are fetched.
- The downstream documentation should be updated again after another project besides Pinocchio adopts the workflow, because a second consumer will show which parts are Pinocchio-specific and which parts are truly generic.

## Related notes

- [[On-Ramp/go-cli-with-embedded-spa]]
- [[Tribal/canonical-doc-model-across-delivery-modes]]
- [[ARTICLE - Separating Dagger Build Steps from Split GoReleaser Pipelines]]
- [[ARTICLE - Deploying Glazed Help Browser to Argo CD - Production Deep Dive]]
