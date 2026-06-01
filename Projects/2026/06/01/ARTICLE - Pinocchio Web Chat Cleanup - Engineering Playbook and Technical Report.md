---
title: "Pinocchio Web Chat Cleanup: Engineering Playbook and Technical Report"
aliases:
  - Pinocchio Web Chat Cleanup Report
  - CHATOVERLAY Cleanup Deep Dive
  - Web Chat Cleanup Engineering Playbook
  - Provider Backed Web Chat Cleanup Report
tags:
  - article
  - project-report
  - textbook
  - playbook
  - react
  - typescript
  - go
  - pinocchio
  - chat-provider
  - sessionstream
  - storybook
  - architecture
  - cleanup
status: active
type: article
created: 2026-06-01
repo: /home/manuel/workspaces/2026-05-29/chatbot-react
---

# Pinocchio Web Chat Cleanup: Engineering Playbook and Technical Report

This report explains the cleanup work done across the chat overlay, generic chat provider, and Pinocchio `cmd/web-chat` example. It is written as a technical article for a future engineer who needs to understand not only what changed, but why the changes were made, how they were sequenced, which tools made the work safe, and which rules should guide future changes.

The central result is that Pinocchio web-chat is now a provider-backed example application with a much clearer ownership model. Generic runtime mechanics live in `@go-go-golems/chat-provider`. Reusable backend mechanics live in Pinocchio `pkg/chatapp/...`. The Pinocchio web-chat command owns app-specific routes, profiles, runtime composition, renderers, styles, and frontend cards. Temporary debug apps, duplicate runtimes, misleading package names, stale route files, unused frontend files, and accidental public Go packages were removed or internalized.

> [!summary]
> - The cleanup separated reusable runtime mechanics from app-owned UI and backend policy. The provider owns sessionstream client mechanics; Pinocchio owns profile policy, runtime composition, routes, cards, and example-app structure.
> - The work was evidence-driven. Deterministic mock profiles, adapter parity tests, hydration smokes, TypeScript checks, Go tests, Storybook builds, `knip`, inventory scripts, and `docmgr` artifacts were used before deleting or moving large surfaces.
> - The final Go shape places command-owned backend code under `cmd/web-chat/internal/...`, with `main.go` reduced to Glazed/Cobra command wiring and execution delegation.
> - The final frontend shape removes debug/demo/runtime duplication and centers the production app under `src/features/web-chat`, with provider-backed state and app-owned renderers.
> - The durable rule for future work is: define ownership first, prove behavior with targeted checks, move or delete in small commits, and document the decision while the evidence is fresh.

Related notes:

- [[ARTICLE - ChatProvider Web Chat Cleanup - Provider Runtime Timeline Adapters and Example Architecture]]
- [[ARTICLE - Generic ChatProvider - From Overlay Runtime to Provider Backed Web Chat]]

## 1. Why this cleanup existed

The cleanup was not primarily a formatting pass. It addressed a structural problem: several pieces of the chat system had become similar enough to duplicate behavior while still being organized as separate implementations. The overlay runtime, Pinocchio web-chat, and downstream applications needed the same sessionstream mechanics, but they did not need the same page shell, cards, profile selector, or domain UI.

The work therefore started by identifying three categories of code:

| Category | Correct owner | Examples |
|---|---|---|
| Generic browser runtime mechanics | `@go-go-golems/chat-provider` | Session creation, WebSocket connection, snapshot hydration, live frame projection, provider-scoped registries, frontend tool result submission. |
| Reusable backend chat mechanics | Pinocchio `pkg/chatapp/...` | Server helper DTOs, frontend tool bridge, widget protobuf/plugin support, chatapp runner concepts. |
| Pinocchio web-chat application policy | `pinocchio/cmd/web-chat/...` | Profile API, runtime composition, app-specific agent-mode plugin, HTTP route assembly, export endpoints, renderers, cards, statusbar, styles. |

This ownership map was the most important design artifact. Without it, cleanup could easily produce a smaller codebase that was still conceptually confused. With it, each deletion and move had a clear test: does this code implement reusable mechanics, or does it express one application's policy?

The cleanup also had a second goal: make Pinocchio web-chat a good example project. An example project has a stricter responsibility than a private app. It teaches future implementers what the intended architecture is. If the example contains obsolete debug routes, duplicate runtimes, vague file names, global registries, and command internals that look like public packages, readers will copy those mistakes. The cleanup changed the example so the code layout itself communicates the intended design.

## 2. The starting state

The starting state had several overlapping problems.

First, Pinocchio web-chat had a legacy frontend runtime and a provider-backed runtime at the same time. The legacy path owned Redux state, WebSocket management, snapshot hydration, UI-event projection, and timeline state. The provider path was intended to become generic, but it still coexisted with the old implementation. That forced every feature to be reviewed twice.

Second, debug and demo code had become part of the maintenance surface. The debug route, stream-debug panel, debug recorder API, reconcile export, provider demo, and capability showcase code were useful while proving behavior. Once the provider-backed production route existed, those pieces became confusing. They gave the repository multiple apparent entrypoints and made it harder to know which path represented production.

Third, reusable backend concepts were scattered. Some mechanics belonged in Pinocchio core packages because the overlay and future clients needed them. Other mechanics were specific to the `cmd/web-chat` command and should never be imported as general-purpose packages. The old `cmd/web-chat/app`, `cmd/web-chat/profiles`, and `cmd/web-chat/mockruntime` packages looked importable, but they were command internals.

Fourth, file names and directories no longer matched responsibilities. The frontend had a `src/webchat` namespace after the app had moved toward a feature-folder design. The Go appserver had a file named `showcase_tools.go` containing production frontend-tool manifest/result endpoints. `main.go` contained command definition, HTTP static serving, mux construction, runtime composition, profile resolution, store setup, plugin setup, and HTTP server lifecycle.

The cleanup therefore needed to reduce code size, but code size was not the main metric. The stronger metric was responsibility clarity.

## 3. The architecture after cleanup

The final architecture is organized around explicit boundaries.

```mermaid
flowchart TD
  Browser[React web-chat app]
  Provider[@go-go-golems/chat-provider]
  WebChatUI[Pinocchio web-chat UI and renderers]
  Backend[cmd/web-chat backend]
  WebApp[internal/webapp]
  AppServer[internal/appserver]
  Profiles[internal/profiles]
  Runtime[internal/runtime]
  ChatApp[pkg/chatapp]
  Sessionstream[sessionstream]
  Geppetto[Geppetto runtime]

  Browser --> WebChatUI
  WebChatUI --> Provider
  Provider -->|HTTP + WebSocket| Backend
  Backend --> WebApp
  WebApp --> AppServer
  WebApp --> Profiles
  AppServer --> ChatApp
  AppServer --> Sessionstream
  AppServer --> Runtime
  Runtime --> Profiles
  Runtime --> Geppetto

  classDef app fill:#eef6ff,stroke:#2b6cb0,color:#0f172a;
  classDef reusable fill:#eefcf3,stroke:#2f855a,color:#0f172a;
  classDef runtime fill:#fff7ed,stroke:#c05621,color:#0f172a;
  class Browser,WebChatUI,Backend,WebApp,AppServer,Profiles,Runtime app;
  class Provider,ChatApp,Sessionstream reusable;
  class Geppetto runtime;
```

The browser side now has a headless provider runtime and an app-owned feature folder. The provider is responsible for protocol mechanics. Pinocchio web-chat is responsible for what the app looks like, which cards it renders, how profiles are selected, and which Pinocchio-specific timeline adapters are registered.

The Go side now has a command-owned internal package tree:

```text
cmd/web-chat/
  main.go                         # Glazed/Cobra command entrypoint
  gen_frontend.go                 # go generate frontend build hook
  README.md                       # intern-facing backend guide
  web/                            # React frontend package
  static/                         # embedded build output
  internal/
    webchatcmd/                   # command composition root
    webapp/                       # app-config.js, static UI, root mount, HTTP lifecycle
    appserver/                    # session/ws/export/frontend-tool HTTP adapter
    profiles/                     # profile API and request/profile resolution
    runtime/                      # runtime composer and canonical resolver
    middlewaredefs/               # web-chat middleware catalog
    plugins/agentmode/            # app-owned agent-mode chat plugin
    mockruntime/                  # deterministic mock parity runtime
```

This layout is deliberately ordinary. The names are descriptive. `main.go` no longer asks the reader to understand HTTP serving, runtime composition, profile registries, and signal handling before they can understand the command. The appserver package no longer hides all route groups in one large file. The profile API no longer mixes schema routes, current-profile cookies, DTO conversion, and error responses in one file.

## 4. The cleanup sequence

The work was done in phases because the risk profile changed over time. Deleting legacy code before proving provider parity would have been unsafe. Moving Go packages before writing an implementation guide would have produced a diff that was harder to review. Splitting files while changing behavior would have made validation ambiguous.

The sequence was:

| Phase | Purpose | Representative result |
|---|---|---|
| Backend reusable extraction | Move common backend mechanics into Pinocchio packages. | `pkg/chatapp/serverkit`, `pkg/chatapp/frontendtools`, `pkg/chatapp/widgets`. |
| Provider migration | Make Pinocchio web-chat use generic provider mechanics. | Provider-backed production runtime. |
| Timeline adapter unification | Prevent live projection and snapshot hydration from drifting. | Adapter API registers live and hydrate behavior together. |
| Legacy runtime deletion | Remove old Redux/WebSocket frontend path after parity evidence. | One production frontend runtime. |
| Debug/demo deletion | Remove debug app, stream debug, backend debug API, capability showcase. | Smaller route and dependency surface. |
| Frontend surface cleanup | Remove unused files, move `src/webchat` into feature folder, tighten types. | `src/features/web-chat` as canonical frontend feature boundary. |
| Go internal package refactor | Move command-owned Go code into `internal/...` and shrink `main.go`. | Thin command entrypoint plus focused internal packages. |
| README and inventory refresh | Make docs match code and preserve evidence. | Updated README, diary, changelog, inventory, reMarkable docs. |

The important property is not the exact ticket order. The important property is that each phase made the next phase safer. The deterministic mock runtime made frontend deletion safer. The adapter API made hydration parity safer. The Go implementation guide made internal package movement safer. The inventory script made cleanup claims verifiable.

## 5. Provider-backed frontend cleanup

The frontend cleanup centered on the rule that `ChatProvider` is headless. It should not decide the app shell, profile selector, statusbar, cards, or product-specific timeline rendering. Those are Pinocchio web-chat responsibilities.

The provider owns repeatable mechanics:

```text
session persistence
  -> session creation
  -> WebSocket connection
  -> subscribe
  -> snapshot hydration
  -> live frame projection
  -> tool and widget registries
  -> app-facing actions
```

Pinocchio web-chat owns application policy:

```text
profile selection
  -> app layout
  -> card renderers
  -> statusbar and export controls
  -> Pinocchio timeline adapters
  -> CSS parts and themes
  -> Storybook examples
```

This split removed the need for Pinocchio to carry a second WebSocket manager and duplicate projection logic. It also made downstream adoption clearer. CoinVault can reuse provider mechanics without becoming Pinocchio web-chat. Pinocchio web-chat can use the provider without becoming the overlay.

The frontend cleanup included several concrete changes:

- The old debug UI route and debug root were removed.
- The old Redux/WebSocket chat runtime was deleted after parity coverage existed.
- Global renderer registries were replaced with explicit renderer factories.
- Render entities were typed so card props no longer depended on broad unchecked values.
- Styles moved under `src/features/web-chat/styles` and stayed scoped under `[data-pwchat]`, `[data-part="root"]`, and `data-theme="default"`.
- Old `src/webchat` support modules moved into `src/features/web-chat`.
- Generated protobuf files were retained under `src/generated/chatapp` but excluded from `knip` unused-file noise.
- npm remained canonical for `cmd/web-chat/web`; `package-lock.json` is the lockfile for that app.

The frontend shape after cleanup is easier to reason about:

```text
cmd/web-chat/web/src/
  App.tsx
  config/
  features/web-chat/
    WebChatProviderShell/
    WebChatApp/
    ChatComposer/
    ChatHeader/
    ChatStatusbar/
    ChatTimeline/
    cards/
    extensions/pinocchio-timeline-adapters/
    styles/
    renderers.ts
    profileSelection.ts
    agentModeMarkdown.ts
  generated/chatapp/
  store/
  utils/
  ws/
```

A future frontend change should preserve this shape. If a file is reusable across applications, it should probably belong in `@go-go-golems/chat-provider` or another shared package. If it is Pinocchio-specific, it should live under `features/web-chat` or another app-owned feature namespace.

## 6. Timeline adapters as a correction to projection drift

One of the most important corrections was the unified timeline adapter API. Before this change, live event projection and snapshot hydration could be implemented separately. That created a drift risk: an entity might render correctly while streaming but fail after page reload, or it might hydrate correctly but fail during live projection.

The corrected rule is that app-owned timeline behavior is registered as one adapter. An adapter must describe live projection, hydration, or explicitly state that it only supports one side.

The intended shape is:

```ts
defineLiveAndHydrateAdapter({
  kind: "AgentMode",

  projectLive(event, context) {
    if (event.name !== "ChatAgentModeCommitted") return null;
    return {
      id: event.payload.messageId,
      kind: "AgentMode",
      payload: event.payload,
    };
  },

  hydrate(entity, context) {
    if (entity.kind !== "AgentMode") return null;
    return {
      id: entity.id,
      kind: "AgentMode",
      payload: entity.payload,
    };
  },
});
```

The exact code differs by adapter, but the invariant is stable: the registration point forces the engineer to think about both live and hydrated data. This is a design rule that should remain in place for future app-specific cards.

The adapter correction also changed how cleanup could proceed. Once adapters were unified and hydration smoke tests existed, it became safe to remove the old projectors and legacy runtime. Without this step, deletion would have removed a fallback path before proving that reload behavior was correct.

## 7. Debug and demo deletion

The debug app was removed after the production route became provider-backed and the remaining validation path was strong enough. The deletion included frontend and backend pieces:

- `src/debug-ui/**`
- `src/app/DebugUiRoot.tsx`
- route-mode logic and tests
- stream-debug panel and protocol helpers
- debug recorder and reconcile backend code
- `/api/debug/sessions/*`
- `--debug-api`
- devctl debug flag plumbing
- related dependencies such as Redux DevTools and YAML support used only by debug paths

This was not a rejection of debug tooling. It was a decision that temporary diagnostic scaffolding should not remain in the production example after it has served its purpose. The correct rule is:

- Keep diagnostic code while it is needed to prove a migration.
- Write down what it proved.
- Delete it once production tests and deterministic fixtures cover the same behavior.
- Do not let debug routes become a second app architecture.

The first commit attempt during debug removal failed because an unused Go helper remained:

```text
cmd/web-chat/app/server.go:395:6: func encodeProtoJSON is unused (unused)
```

The fix was to delete `encodeProtoJSON` and the now-unused protobuf import. This is a typical cleanup failure mode: removing a feature often leaves helper code behind. The right response is to let the compiler and linter identify the exact leftover, remove it, and rerun validation.

## 8. Go internal package refactor

The Go refactor addressed a different class of problem. The frontend had duplicate runtime mechanics; the Go command had unclear package ownership and an overloaded `main.go`.

Before the refactor, these packages existed outside `internal`:

```text
cmd/web-chat/app
cmd/web-chat/profiles
cmd/web-chat/mockruntime
```

They were not stable public APIs. They were command-specific implementation packages. Keeping them outside `internal` meant that unrelated packages in the module could import them and accidentally turn app internals into dependencies.

The first Go cleanup commit therefore performed a behavior-preserving package move:

```bash
git mv cmd/web-chat/app cmd/web-chat/internal/appserver
git mv cmd/web-chat/profiles cmd/web-chat/internal/profiles
git mv cmd/web-chat/mockruntime cmd/web-chat/internal/mockruntime
```

After imports and package names were updated, tests passed. This commit intentionally did not split files or rewrite option APIs. It changed ownership first.

The next steps extracted responsibilities from `main.go`:

| Extracted package | Responsibility |
|---|---|
| `internal/webapp` | Runtime config JavaScript, static UI serving, SPA fallback, root mounting, HTTP server lifecycle. |
| `internal/runtime` | Profile runtime composer, canonical resolver, turn persistence, agent-mode sink wrapper. |
| `internal/middlewaredefs` | Middleware definition catalog and agent-mode middleware schema. |
| `internal/plugins/agentmode` | App-owned agent-mode chat plugin and timeline/UI projection. |
| `internal/webchatcmd` | Command composition root: settings decode, profile resolution, dependency assembly, appserver construction. |

The final `main.go` is intentionally small. It embeds static assets, declares the Glazed command, wires Cobra help/logging, and delegates execution:

```go
//go:embed static
var staticFS embed.FS

type Command struct {
    *cmds.CommandDescription
    staticFS fs.FS
}

func (c *Command) RunIntoWriter(ctx context.Context, parsed *values.Values, _ io.Writer) error {
    return webchatcmd.Run(ctx, parsed, c.staticFS)
}
```

The internal command runner owns the application assembly:

```go
func Run(ctx context.Context, parsed *values.Values, staticFS fs.FS) error {
    settings := decodeServerSettings(parsed)
    profileRuntime := profilebootstrap.ResolveCLIProfileRuntime(ctx, parsed)
    middlewareRegistry := middlewaredefs.NewRegistry()
    baseSettings := resolveBaseInferenceSettings(parsed)
    turnStore := serverkit.OpenTurnStore(...)

    runtimeComposer := runtime.NewProfileRuntimeComposer(
        middlewareRegistry,
        middlewarecfg.BuildDeps{Values: deps},
        baseSettings,
    ).WithTurnStore(turnStore)

    requestResolver := profiles.NewRequestResolver(...)
    runtimeResolver := runtime.NewCanonicalRuntimeResolver(requestResolver, runtimeComposer)
    server := appserver.NewServer(...)
    mux := webapp.NewMux(...)
    handler := webapp.MountRoot(settings.Root, mux, appConfigJS)
    return webapp.RunHTTPServer(ctx, httpServer, server.Close)
}
```

This is the right place for app assembly. It is not reusable library code, but it is also no longer mixed into the executable entrypoint.

## 9. Appserver and profile API decomposition

Once ownership was correct, the large files could be split by responsibility.

`internal/appserver/server.go` became a constructor/state file. Route groups moved into dedicated files:

```text
internal/appserver/
  server.go                 # Server state, NewServer, Close
  options.go                # With... options
  hydration.go              # SQLite/in-memory hydration store setup
  routes_sessions.go        # session creation, subrouting, message submission
  routes_ws.go              # WebSocket handler
  routes_exports.go         # timeline/turn/full exports
  routes_frontend_tools.go  # production frontend-tool manifest/result routes
  snapshot.go               # snapshot provider, status encoding
  response.go               # JSON helper
```

The rename from `showcase_tools.go` to `routes_frontend_tools.go` matters. File names are part of the API that the repository presents to future maintainers. A production endpoint should not live in a file whose name says showcase.

The profile API received the same treatment. `api.go` became a small dispatcher:

```go
func RegisterAPIHandlers(mux *http.ServeMux, profileRegistry gepprofiles.Registry, opts APIOptions) {
    if mux == nil || profileRegistry == nil {
        return
    }
    opts.normalize()

    registerSchemaHandlers(mux, opts)
    registerProfileHandlers(mux, profileRegistry, opts)
    if opts.EnableCurrentProfileCookieRoute {
        registerCurrentProfileHandler(mux, profileRegistry, opts)
    }
}
```

The rest of the behavior moved into files named by responsibility:

```text
internal/profiles/
  api.go                         # RegisterAPIHandlers dispatcher
  api_schemas.go                 # middleware and extension schema routes
  api_profiles.go                # profile list/detail/default routes
  api_current_profile.go         # current profile cookie route
  api_current_profile_test.go    # cookie behavior coverage
  api_models.go                  # DTO conversion helpers
  api_response.go                # JSON/error response helpers
  resolver.go                    # request/profile/runtime resolution
  types.go                       # API and resolver DTOs
  mock.go                        # mock_parity profile helpers
```

The current-profile route received focused tests because it preserves subtle compatibility behavior:

- A missing cookie falls back to the registry default profile.
- A qualified cookie such as `default/beta` selects the named registry and profile.
- A legacy unqualified cookie such as `beta` is still accepted against the default registry.
- POST writes a qualified cookie with `Path=/`, `Secure`, `HttpOnly`, and `SameSite=Lax`.

The future guideline is simple: if a route has compatibility behavior, write focused tests before changing its file organization or semantics.

## 10. Tools and techniques that made the cleanup safe

The cleanup used several categories of tools. Each served a different purpose.

### Repository discovery

`rg`, `find`, `go list`, and inventory scripts were used to map the actual codebase rather than relying on memory.

Typical commands:

```bash
rg -n "cmd/web-chat/(app|profiles|mockruntime)" -g '*.go'
find cmd/web-chat -maxdepth 3 -type f -name '*.go' | sort
go list ./cmd/web-chat/...
```

The inventory script recorded counts, package lists, largest files, frontend unused output, and cleanup probes. This made progress visible and gave each cleanup phase a concrete before/after record.

### Behavior-preserving moves

Large package moves used `git mv` first, then import updates, then tests. This produced reviewable diffs. A reviewer can inspect a move-only commit differently from a rewrite commit. The rule is:

```text
move first
compile second
split third
rewrite only after behavior is stable
```

### Static validation

The frontend used:

```bash
npm run typecheck
npm test
npm run lint
npm run audit:unused || true
npm run build
npm run check:storybook
```

The backend used:

```bash
go test ./cmd/web-chat/... -count=1
go test ./...
go generate ./...
golangci-lint run
go vet
```

The pre-commit hook was useful because it ran a broader validation suite than the focused command used during inner-loop development. It also exposed generated-code interactions, such as `logcopter.go` naming conflicts.

### Deterministic runtime tests

The `mock_parity` runtime was important because it made frontend/provider behavior testable without requiring an LLM provider. A deterministic profile can produce repeatable event sequences for parity tests and hydration checks. This changed deletion from a judgment call into an evidence-based operation.

### `knip` as advisory evidence

`knip` was used through `npm run audit:unused`. It exits with code `1` when it finds unused exports, so the workflow intentionally used:

```bash
npm run audit:unused || true
```

That command is not a pass/fail gate in this ticket. It is inventory evidence. The cleanup succeeded in removing unused files; remaining output is mostly unused export groups and barrels that need a separate public-surface decision.

### `docmgr`, diary, and reMarkable

The cleanup kept a ticket diary and changelog. The diary recorded commands, failures, tricky details, and review instructions. This mattered because the work spanned many commits across two repositories. The diary preserved context that commit messages alone cannot carry.

The Go internal package refactor also had a dedicated design guide uploaded to reMarkable. That was useful because package movement is easy to start and hard to review without a written target shape.

### Obsidian reports

Obsidian notes preserve the reusable lessons after the ticket is done. Ticket docs are for execution and evidence. Obsidian articles are for future learning and design memory. This note belongs to the second category.

## 11. Important failure modes observed

Cleanup work tends to fail in predictable ways. Several concrete failures or warnings appeared during this project.

### Generated logger name conflicts

After adding `internal/webapp`, `go generate` produced a package-level `log` variable in `logcopter.go`. The new files had imported `github.com/rs/zerolog/log` as `log`, causing a compile failure:

```text
cmd/web-chat/internal/webapp/logcopter.go:7:5: log already declared through import of package log ("github.com/rs/zerolog/log")
```

The fix was to alias zerolog imports as `zlog` in packages that may receive generated logcopter files.

Rule:

```go
import zlog "github.com/rs/zerolog/log"
```

Use this pattern in new command/internal packages unless the package intentionally uses the generated `log` variable.

### Deletion leaves unused helpers

During debug backend deletion, the first commit attempt failed because `encodeProtoJSON` remained unused. This is the correct kind of failure. The compiler identified a leftover helper that no longer belonged to any active path.

Rule:

```text
After deleting a feature, run compile/lint before deciding the deletion is complete.
Unused helpers are part of the deleted feature unless a live caller remains.
```

### Advisory warnings should be classified

The frontend build still reports a known Vite warning for `app-config.js`, and Storybook reports runtime `eval` warnings and large chunks. These are not ignored; they are classified as non-blocking known warnings for this cleanup. That classification matters because it prevents the project from mixing real regressions with known advisory output.

Rule:

```text
Record known non-blocking warnings by exact message.
Do not let new warnings hide inside old warning categories.
```

### `internal` may break imports by design

Moving packages under `internal` is a compile-time ownership decision. If code outside `cmd/web-chat` starts needing an internal package, that is not an inconvenience to work around. It is evidence that either the caller should test through a public boundary or the reusable piece should be extracted to `pkg/chatapp/...`.

## 12. Commit discipline and documentation discipline

The cleanup used short, focused commits. Each commit had a single review purpose:

| Commit | Purpose |
|---|---|
| `e829689` | Remove debug app and debug backend. |
| `e15e234` | Add unused-audit and inventory tooling. |
| `fd438a1` | Simplify frontend surface and move support modules. |
| `986350b` | Internalize command-owned Go subpackages. |
| `9b4caa4` | Extract HTTP shell to `internal/webapp`. |
| `d1e1032` | Extract runtime, middleware, and agent-mode plugin internals. |
| `cf040ad` | Move app assembly out of `main.go`. |
| `44db06d` | Split appserver routes and rename frontend-tool routes. |
| `d47630d` | Split profile API and add cookie tests. |
| `82274c9` | Refresh web-chat README documentation. |

The corresponding overlay documentation commits kept diary and changelog entries in sync. That is not administrative overhead. It is part of making a large cleanup reviewable. When a future engineer asks why `internal/runtime` duplicates a small JSON decode helper instead of importing `middlewaredefs`, the diary gives the answer: dependency direction was more important than sharing that tiny helper.

The pattern is:

```text
implement a focused change
run focused checks
commit code
write diary with exact failures and review instructions
update changelog and task status
commit docs
continue
```

This pattern is slower than making all edits at once. It is faster than debugging an unreviewable diff.

## 13. Future guidelines

The following rules should guide future work in this system.

### Define ownership before moving code

Before moving a file, answer this question:

```text
Is this reusable runtime/library mechanics, or app-owned policy?
```

If it is reusable browser runtime mechanics, it likely belongs in `@go-go-golems/chat-provider`. If it is reusable backend chat mechanics, it likely belongs in `pkg/chatapp/...`. If it is Pinocchio web-chat app policy, it belongs under `cmd/web-chat/internal/...` or `cmd/web-chat/web/src/features/web-chat/...`.

### Do not reintroduce duplicate runtime paths

Pinocchio web-chat should not regain a second WebSocket manager, second snapshot mapper, second timeline projector stack, or debug-only app shell that competes with the production provider path. If temporary diagnostics are needed, they should be time-bounded and removed after production validation exists.

### Register live and hydration behavior together

New timeline entities should use the unified adapter API. If an entity can appear in live events and hydrated snapshots, the same adapter family should account for both paths. A live-only implementation should be explicit, not accidental.

### Keep `main.go` thin

`cmd/web-chat/main.go` should stay focused on executable and command concerns:

- static embed declaration
- Glazed command description
- Cobra root/help/logging setup
- delegation to `internal/webchatcmd`

If new app assembly code appears in `main.go`, move it into `internal/webchatcmd` or another focused internal package.

### Treat route files as part of the design

Route files should be named by production responsibility:

```text
routes_sessions.go
routes_exports.go
routes_frontend_tools.go
routes_ws.go
```

Avoid names like `showcase`, `demo`, or `debug` for production endpoints. If a route is temporary, name it temporary and write down when it can be removed.

### Keep generated code explicit

Generated frontend protobuf bindings are intentionally retained. They should remain documented and excluded from unused-file cleanup until the protobuf-backed payload decoder work is implemented.

### Use `knip` as inventory, not as an automatic deletion instruction

Unused exports can mean several things:

- the export is truly dead;
- the export is an intended public surface not consumed internally;
- the export exists for Storybook, tests, or downstream packages;
- the barrel is too broad.

Investigate before deletion. Do not use `knip` as an automatic code removal tool.

### Preserve exact failure messages in diaries

Failure messages are data. They should be copied exactly into the diary when they affect the implementation. The generated `logcopter.go` conflict is a good example: the exact error explains the future rule about `zlog` aliases.

## 14. Recommended implementation sequence for future cleanup

When continuing cleanup on this codebase, use this sequence:

```text
1. Write down the ownership boundary.
2. Gather current facts with rg, go list, inventory scripts, and tests.
3. Move files with git mv before changing behavior.
4. Update imports and run focused tests.
5. Commit the move.
6. Split large files by responsibility.
7. Add tests around subtle compatibility behavior.
8. Run full frontend and Go validation.
9. Regenerate inventory.
10. Update diary, changelog, and durable docs.
```

This sequence is intentionally conservative. It avoids combining three kinds of risk in one commit. A package move, a behavior change, and a test rewrite should not happen at the same time unless the codebase is so small that review remains trivial.

## 15. Current status

At the end of this cleanup pass:

- Pinocchio web-chat uses the generic provider-backed runtime.
- The old debug app and debug backend are gone.
- The old frontend `src/webchat` namespace is gone.
- Go command internals live under `cmd/web-chat/internal/...`.
- `main.go` is a thin Glazed/Cobra command file.
- Appserver and profile APIs are split by responsibility.
- Current-profile cookie behavior has focused tests.
- README documentation reflects the new package layout.
- `CHATOVERLAY-011` tasks are complete.
- Final acceptance checks passed, with known non-blocking advisory warnings recorded.

The remaining important future work is `CHATOVERLAY-012`: standardizing WebSocket payload decoding around protobuf schemas. That work should preserve the same boundary rule. The provider should own decoder registry mechanics; Pinocchio should own app-specific decoder packs and payload schemas.

## 16. Key commands

Use these commands when reviewing or extending this cleanup.

Frontend validation:

```bash
cd /home/manuel/workspaces/2026-05-29/chatbot-react/pinocchio/cmd/web-chat/web
npm run typecheck
npm test
npm run lint
npm run audit:unused || true
npm run build
npm run check:storybook
```

Go validation:

```bash
cd /home/manuel/workspaces/2026-05-29/chatbot-react/pinocchio
go test ./cmd/web-chat/... -count=1
```

Inventory and ticket hygiene:

```bash
cd /home/manuel/workspaces/2026-05-29/chatbot-react/2026-05-29--chatbot-overlay-glm/ttmp/2026/05/31/CHATOVERLAY-011--make-pinocchio-web-chat-a-stellar-go-and-typescript-example-application
scripts/01-web-chat-inventory.py

cd /home/manuel/workspaces/2026-05-29/chatbot-react/2026-05-29--chatbot-overlay-glm
docmgr doctor --ticket CHATOVERLAY-011 --stale-after 30
```

Search for accidental old imports:

```bash
cd /home/manuel/workspaces/2026-05-29/chatbot-react/pinocchio
rg -n "cmd/web-chat/(app|profiles|mockruntime)" -g '*.go'
```

The expected result is no active old imports. Historical ticket docs may mention old paths because they describe the migration.

## 17. Closing rule

A cleanup is complete only when the new structure teaches the correct design. Passing tests is required, but it is not enough. The code layout, file names, public exports, README, ticket diary, and validation artifacts should all point to the same architecture. In this cleanup, that architecture is:

```text
provider owns browser runtime mechanics
Pinocchio packages own reusable backend mechanics
cmd/web-chat/internal owns app-specific backend policy
cmd/web-chat/web/src/features/web-chat owns app-specific frontend policy
main.go owns command wiring only
```

Future work should preserve that structure unless there is a written design that replaces it with a clearer one.
