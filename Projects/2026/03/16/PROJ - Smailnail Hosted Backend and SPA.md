---
title: Smailnail Hosted Backend and SPA
aliases:
  - Smailnail Hosted Backend
  - Project Smailnail Hosted Backend
  - smailnaild
tags:
  - project
  - go
  - react
  - imap
  - email
  - mcp
  - coolify
  - self-hosted
  - keycloak
  - oidc
status: active
type: project
created: 2026-03-16
repo: /home/manuel/workspaces/2026-03-08/update-imap-mcp/smailnail
branch: task/update-imap-mcp
mcp-url: https://smailnail.mcp.scapegoat.dev/mcp
keycloak-issuer: https://auth.scapegoat.dev/realms/smailnail
dovecot-host: 89.167.52.236
---

# Smailnail Hosted Backend and SPA

This project extends the `smailnail` repository — a Go toolchain for IMAP mailboxes, test email generation, and a YAML-based email processing DSL — into a hosted platform. The work adds a persistent backend binary (`smailnaild`), a full React/Vite SPA embedded into the Go binary, and a production deployment of the IMAP MCP server on Coolify with Keycloak-backed OIDC authentication.

> [!summary]
> The project turned smailnail from a collection of local CLI tools into a hosted service platform, across seven docmgr tickets (SMAILNAIL-008 through SMAILNAIL-014) and 17 commits over a single weekend. The three pillars are:
> 1. **smailnaild**: a hosted Go backend with account management, encrypted IMAP credential storage, mailbox browsing, email rule management, and dry-run execution
> 2. **React SPA**: an embedded single-page application providing account setup, mailbox exploration, and rule authoring with live dry-run previews
> 3. **Coolify deployment**: production packaging of the IMAP MCP server at `smailnail.mcp.scapegoat.dev` with external OIDC authentication via Keycloak, plus a hosted Dovecot test fixture on the same Hetzner server

## Why this project exists

The `smailnail` CLI tools and the `smailnail-imap-mcp` MCP server already existed for local mail processing and AI-driven IMAP access. But several things were missing for the system to be useful beyond a single developer's machine:

- **No persistence for account configuration.** Each CLI invocation required passing IMAP credentials as flags or environment variables. There was no way to register an account once and reuse it.
- **No web interface.** Browsing mailboxes, previewing rules, and testing account connectivity all required shell commands.
- **No production endpoint for the MCP server.** Claude and other AI tools couldn't reach `smailnail-imap-mcp` over the internet — it only ran locally over stdio.
- **No credential security.** IMAP passwords were passed in plaintext. A hosted system needed encryption at rest.
- **No identity model.** Nothing tied accounts or rules to a user. Multi-tenancy required an identity layer, even if initially stubbed.

The hosted backend addresses all of these. The Coolify deployment gives the MCP server a stable public URL that AI agents can call with proper OIDC bearer tokens. And the SPA provides a self-service UI for the operations that previously required curl or CLI commands.

## Current project status

The branch (`task/update-imap-mcp`) contains 17 commits over `origin/main`, produced between the evening of 2026-03-15 and the afternoon of 2026-03-16. The backend and frontend are functional end-to-end, with integration tests verified against a local Dovecot fixture. The MCP server is deployed and authenticated on Coolify. The OIDC identity model has schema support but is not yet wired into the web session flow.

### What already works

- **smailnaild binary** with Glazed CLI, SQLite (or Postgres) persistence, and AES-GCM credential encryption
- **Full REST API**: 18 endpoints covering accounts CRUD, IMAP connection testing, mailbox listing, paginated message browsing with full message detail, rules CRUD, and rule dry-run
- **React/Vite SPA** with Redux Toolkit state management: account setup flow with test progress visualization, mailbox explorer with sidebar and message reader, rules list with status badges, rule editor with YAML DSL input, and dry-run result viewer
- **go:embed integration** with build-tag switching — the SPA is baked into the Go binary for production, but during development Vite runs independently with hot reload
- **go generate pipeline**: `pnpm build` in `ui/` followed by file copy into `embed/public/`, triggered by `go generate ./pkg/smailnaild/web/`
- **Makefile targets**: `dev-backend`, `dev-frontend`, `frontend-build`, `build-embed` for the two-process dev loop
- **Docker packaging**: multi-stage Dockerfiles for both `smailnail-imap-mcp` (deployed) and the general build
- **Local dev stack**: Docker Compose with Dovecot (test IMAP), Keycloak (OIDC provider), and PostgreSQL (Keycloak backing store)
- **Production MCP deployment**: live at `https://smailnail.mcp.scapegoat.dev/mcp` with OIDC authentication
- **Hosted Dovecot fixture**: live on Hetzner at `89.167.52.236:993` for remote end-to-end testing
- **Integration tests** at three levels: account service, rule service, and full HTTP handler flow — all gated behind `SMAILNAILD_DOVECOT_TEST=1`

### What is still incomplete

- **OIDC web sessions**: the schema tables (`users`, `user_external_identities`, `web_sessions`) exist and the `ResolveOrProvisionUser` function is implemented, but the browser login/session flow is not yet connected to Keycloak
- **Multi-user isolation in the API**: all API calls currently use a local default user ID (`local-user`) or an `X-Smailnail-User-ID` header for development simulation — real OIDC-backed user scoping is the next step
- **Production deployment of smailnaild itself**: only the MCP server is deployed on Coolify so far
- **Rule execution**: only dry-run mode exists — no scheduled, event-driven, or one-shot real execution
- **OpenAI MCP connector**: Keycloak dynamic client registration (RFC 7591) was investigated but hit blockers with OpenAI's rotating Azure IPs being rejected by Keycloak's trusted-hosts policy
- **UI polish**: no loading spinners during API calls, no error toasts, no responsive breakpoints

## Work phases

### Phase 1: smailnaild bootstrap — SMAILNAIL-008 (2026-03-15 evening)

**Ticket**: SMAILNAIL-008-SMAILNAILD-SQL-BOOTSTRAP-IMPLEMENTATION
**Commit**: `52e175d` — "feat(smailnail): add smailnaild sql bootstrap skeleton"

This was the foundational slice: create a new hosted binary that can start an HTTP server backed by a SQL database.

The work drew from an earlier design ticket (SMAILNAIL-003) that had laid out a full vision for deploying smailnail on Coolify with GitHub SSO and per-user IMAP configuration. Rather than implementing that entire design at once, SMAILNAIL-008 scoped down to the minimum viable skeleton.

**What was built:**

- **`cmd/smailnaild/main.go`**: a Glazed root command with help page support, following the standard `go-go-golems` CLI pattern
- **`cmd/smailnaild/commands/serve.go`**: a serve command registering Clay SQL sections for database configuration and custom `--listen-host` / `--listen-port` flags for the HTTP server. A notable early decision was renaming the server flags from `--host`/`--port` to `--listen-host`/`--listen-port` to avoid collisions with Clay SQL's own `--host`/`--port` database connection flags.
- **`pkg/smailnaild/db.go`**: database bootstrap using Clay SQL helpers. The schema starts with a baseline `app_metadata` table for version tracking, then applies incremental migrations. The default database is SQLite at `smailnaild.sqlite`, but any Clay SQL-supported backend (Postgres, MySQL) can be used via `--dsn`.
- **`pkg/smailnaild/http.go`**: a minimal Chi-based HTTP router exposing `/healthz`, `/readyz` (with database ping), and `/api/info` (returning server metadata as JSON).

Unit tests for both the database bootstrap and the HTTP surface were included from the start.

### Phase 2: Local development stack — SMAILNAIL-009 (2026-03-15 evening)

**Ticket**: SMAILNAIL-009-LOCAL-DOCKER-STACK-IMPLEMENTATION
**Commit**: `53fce48` — "feat(smailnail): add local keycloak and dovecot stack"

Before building account management, the project needed a predictable local IMAP server and an OIDC provider. This ticket added a Docker Compose stack combining both.

**What was built:**

- **`docker-compose.local.yml`** with three services:
  - **Dovecot** (`ghcr.io/spezifisch/docker-test-dovecot`): the same test fixture image used by the existing smoke tests, exposing SMTP (24), POP3 (110), IMAP (143), IMAPS (993), POP3S (995), and ManageSieve (4190). Test users `a`, `b`, `c`, `d` with password `pass`.
  - **Keycloak** (v26.1) in development mode on port 18080, with an auto-imported realm `smailnail-dev` containing two pre-configured OIDC clients: `smailnail-web` (for the future SPA login) and `smailnail-mcp` (for bearer token validation).
  - **PostgreSQL** backing Keycloak persistence.
- **`dev/keycloak/realm-import/smailnail-dev-realm.json`**: a deterministic realm export so the local Keycloak starts with known clients and configuration every time.
- **README updates** with startup/shutdown commands and verification steps (OIDC discovery curl, IMAPS reachability check).

The diary notes that all verification steps passed on first run: OIDC discovery returned a valid configuration, and the Dovecot IMAPS port was reachable.

### Phase 3: MCP Coolify deployment — SMAILNAIL-010 (2026-03-15 night through 2026-03-16)

**Ticket**: SMAILNAIL-010-MCP-COOLIFY-DEPLOYMENT
**Commits**: `ab5df7b`, `f24629d`, `6072f7c`, `3f4f29b`, `53ddf87`, `04f2762`, `39e375a`

This was the longest and most operationally complex phase: packaging the MCP server binary into a Docker image, deploying it on Coolify with OIDC authentication, standing up a hosted Dovecot test fixture on the same Hetzner server, and validating the entire flow end-to-end with an authenticated MCP client.

**Repository packaging** (`ab5df7b`):

The first step was making the MCP binary container-ready. This involved:

- Adding a `.dockerignore` to keep build context clean
- Creating `Dockerfile.smailnail-imap-mcp`: a multi-stage build using `golang:1.25.8-bookworm` for compilation and `debian:bookworm-slim` for the runtime. An early surprise was that `CGO_ENABLED=0` (static linking) failed because of a tree-sitter JavaScript dependency — the solution was to use the glibc-based Debian runtime instead of Alpine.
- Writing `scripts/docker-entrypoint.smailnail-imap-mcp.sh`: a flexible entrypoint that assembles the MCP server command from environment variables (`SMAILNAIL_MCP_TRANSPORT`, `SMAILNAIL_MCP_PORT`, `SMAILNAIL_MCP_AUTH_MODE`, OIDC configuration, etc.) with shell parameter expansion and sensible defaults.
- Updating `pkg/mcp/imapjs/server.go` to default the transport to `streamable_http` on port 3201.
- Writing deployment documentation in `docs/deployments/smailnail-imap-mcp-coolify.md`.

**Coolify application creation** (`f24629d`):

The standard root `Dockerfile` was added as the Coolify-facing build entrypoint. The Coolify app was created via the API:

- App UUID: `fhp3mxqlfftdxdib3vxz89l3`
- Domain: `https://smailnail.mcp.scapegoat.dev`
- Build pack: Dockerfile
- Exposed port: 3201

A Keycloak realm `smailnail` was created on the production Keycloak instance at `auth.scapegoat.dev` with a `smailnail-mcp` client. Environment variables were set via the Coolify API (a CLI bug was discovered where `is_build_time` vs `is_buildtime` caused failures with the CLI tool, so direct API calls were used instead).

**Health check fix** (`6072f7c`):

The first deployment failed health checks because Coolify runs health probes *inside* the container, and the slim Debian image didn't include `curl`. Both Dockerfiles were updated to install `curl` in the runtime stage. After this fix, the deployment succeeded and the app entered `running:healthy` status.

The health check path was set to `/.well-known/oauth-protected-resource` — a publicly accessible endpoint even when auth is enabled, unlike `/mcp` which correctly returns HTTP 401 with a `WWW-Authenticate` header for unauthenticated requests.

**Hosted Dovecot fixture** (`04f2762`, `39e375a`):

To enable remote end-to-end testing, a Dovecot fixture was deployed on the same Hetzner server:

- `deployments/coolify/smailnail-dovecot.compose.yaml`: the same test Dovecot image, but exposed on raw host ports (no HTTP routing — Coolify reports it as `running:unknown` since there's no HTTP health check).
- Coolify service UUID: `gh32795yh1av2dpi2j6lhn6h`
- Host: `89.167.52.236` on standard mail ports
- Validation: created a remote mailbox, stored a test message, and fetched it back using the existing `imap-tests` CLI tools.

**Authenticated MCP smoke test:**

The diary documents a complete end-to-end validation:

1. A smoke client (`smailnail-mcp-smoke`) was created in the Keycloak `smailnail` realm
2. A custom Go client (`smoke_hosted_mcp_oidc.go`) was written to perform streamable-HTTP MCP communication with bearer tokens
3. The client successfully initialized an authenticated MCP session, called `tools/list`, and then called `executeIMAPJS` which connected to the hosted Dovecot and returned `{"mailbox":"INBOX"}`

**OpenAI connector investigation:**

An additional investigation into OpenAI's MCP connector revealed issues with Keycloak's RFC 7591 dynamic client registration — OpenAI's rotating Azure IPs were being rejected by Keycloak's trusted-hosts policy, and OpenAI's scope requests didn't match Keycloak's allowed client scopes. A debug guide was written but the issue remains unresolved.

### Phase 4: Backend development — SMAILNAIL-013 (2026-03-16 morning)

**Ticket**: SMAILNAIL-013-ACCOUNT-SETUP-IMPLEMENTATION (phases 1 and 2)
**Commits**: `fb36ce5`, `cf646d5`, `15318a9`

This was the core backend implementation phase, informed by two prior research tickets:

- **SMAILNAIL-011** (OIDC identity and credentials guide): investigated how OIDC tokens flow through the existing MCP middleware, confirmed that the IMAP layer expects raw credentials (not delegated tokens), and designed a three-layer identity model: external OIDC principal -> local application user -> stored IMAP credentials.
- **SMAILNAIL-012** (Web UI/UX research): mapped user needs to product features, inspected reusable DSL/IMAP primitives, reviewed external provider constraints (Gmail OAuth, Microsoft, Apple), and concluded that the product should be a "hosted mail operations console" with four core flows: account setup, mailbox preview, rule authoring, and rule execution.

The implementation diary for SMAILNAIL-013 is detailed (17 steps) and reflects a deliberate vertical-slice approach: rather than building all repositories first, then all services, then all handlers, each feature was built end-to-end from database to HTTP.

**Schema and secrets foundations** (`fb36ce5`):

- **`pkg/smailnaild/secrets/aead.go`**: AES-GCM authenticated encryption. The `Envelope` struct stores base64-encoded ciphertext, nonce, and a logical key ID. `EncryptString()` generates a random nonce per encryption, and `DecryptString()` reverses it. The key must be exactly 32 bytes.
- **`pkg/smailnaild/secrets/config.go`**: Glazed configuration section for encryption settings. Maps `--encryption-key-base64` and `--encryption-key-id` CLI flags to a validated `Config` struct. The default key ID is `app:smailnaild-encryption-key`. Key rotation is supported by tracking which key ID was used for each encrypted value.
- **`pkg/smailnaild/accounts/types.go`**: account domain types including `AccountRow` (database representation with encrypted password field) and `IMAPAccount` (the decrypted, service-layer representation).
- **`pkg/smailnaild/rules/types.go`**: rule domain types including `RuleRow` (database) and the YAML DSL representation.
- **Database migrations v2-v5**: added `imap_accounts`, `imap_account_tests`, `rules`, and `rule_runs` tables. Each migration is a numbered step applied by `BootstrapApplicationDB()`.

**Account and rule backend** (`cf646d5`):

This single large commit added the full backend service layer:

- **`pkg/smailnaild/accounts/repository.go`**: SQLite-backed CRUD for IMAP accounts. All queries are user-scoped (`WHERE user_id = ?`). Includes `ClearDefaultForUser()` for managing the default account flag, and `CreateTest()`/`LatestTestByAccount()` for persisting account test results.
- **`pkg/smailnaild/accounts/service.go`** (783 lines): the business logic layer. Key operations:
  - `Create()`: validates input, encrypts the IMAP password using the AEAD envelope, stores the encrypted account
  - `Update()`: re-encrypts password if changed, updates account fields
  - `Test()`: performs a comprehensive read-only IMAP connection test — TLS handshake, login, mailbox selection, mailbox listing, sample fetch, and write-probe detection — returning a detailed `TestResult` with per-step pass/fail
  - `ListMailboxes()`: decrypts credentials, connects to IMAP, returns mailbox names with message counts
  - `ListMessages()`: paginated message listing with envelope data (subject, from, to, date, flags)
  - `GetMessage()`: full message fetch including text body extraction and MIME structure tree
- **`pkg/smailnaild/rules/repository.go`**: SQLite-backed CRUD for rules, including `rule_runs` tracking with cascade delete.
- **`pkg/smailnaild/rules/service.go`** (355 lines): rule management with DSL validation and dry-run execution. `DryRun()` parses the rule YAML, resolves the associated account's credentials, connects to IMAP, runs the DSL fetch engine, and returns matched count, action plan summary, and sample message rows — all without modifying anything on the server.
- **`pkg/smailnaild/http.go`** (expanded to 500+ lines): Chi router with full REST handlers. All API responses use a consistent `{data: ..., error: ...}` envelope. The `UserResolver` interface abstracts user identity extraction — the default implementation reads `X-Smailnail-User-ID` header or falls back to `local-user`.
- **`pkg/dsl/types.go`**: a small addition exposing DSL types needed by the rule service.

**Integration tests:**

Three levels of integration tests were added, all gated behind `SMAILNAILD_DOVECOT_TEST=1`:

- `pkg/smailnaild/accounts/integration_test.go`: creates an account, runs a connection test, lists mailboxes, fetches messages against the local Dovecot
- `pkg/smailnaild/rules/integration_test.go`: creates a rule, dry-runs it against a real IMAP mailbox, verifies the result shape
- `pkg/smailnaild/http_integration_test.go`: full HTTP round-trip test — creates an account via POST, tests it, lists mailboxes, fetches messages, creates a rule, dry-runs it

The diary notes a bug found and fixed during this phase: saved-rule execution in the DSL layer wasn't defaulting the output format, causing rules loaded from the database to fail. The fix was to set `format: "json"` as a fallback in the rule service before passing to the DSL engine.

**Encryption config surfacing** (`15318a9`):

Moved encryption configuration from hardcoded test values onto the Glazed command surface, so `--encryption-key-base64` and `--encryption-key-id` appear as proper CLI flags and can be set via environment variables (`SMAILNAILD_ENCRYPTION_KEY_BASE64`, `SMAILNAILD_ENCRYPTION_KEY_ID`).

### Phase 5: Frontend SPA — SMAILNAIL-013 continued (2026-03-16 late morning through afternoon)

**Commits**: `cc59315`, `b445b22`, `e6ee50b`, `e58bfe4`, `1b4f054`

The frontend was built in three rapid iterations, each adding a complete feature vertical. The UI research from SMAILNAIL-012 had already produced ASCII screen mockups and a phased implementation plan, so the frontend work was largely executing against that design.

**Account setup UI** (`cc59315`):

The initial SPA commit was the largest single addition (2,939 lines across 36 files):

- **`ui/`**: React 18 + Vite + Redux Toolkit + Bootstrap CSS. The stack was chosen for fast iteration with minimal configuration. Bootstrap provides baseline styling without a custom design system.
- **`ui/src/features/accounts/`**: the account setup flow with five views:
  - `EmptyState.tsx`: welcome screen when no accounts exist, with a call-to-action button
  - `AccountForm.tsx`: add/edit form for IMAP credentials (server, port, username, password, mailbox, TLS settings, auth kind)
  - `AccountList.tsx`: account cards with label, server info, and test status badges
  - `TestProgress.tsx`: spinner with step-by-step progress during IMAP connection tests
  - `TestResultView.tsx`: detailed test results showing pass/fail for each probe step (TCP, login, mailbox, list, fetch)
  - `AccountSetupPage.tsx`: orchestrates the account setup flow through its sub-views
- **`ui/src/api/`**: typed API client (`client.ts`) and TypeScript interfaces (`types.ts`) matching all backend JSON shapes
- **`ui/src/store/`**: Redux store with `accountsSlice` containing async thunks for all account operations
- **`pkg/smailnaild/web/`**: the Go embed infrastructure:
  - `embed.go` (build tag `embed`): uses `//go:embed` to include the built frontend at compile time
  - `embed_none.go` (build tag `!embed`): development fallback that looks for the frontend build on disk relative to the repo root, enabling `go run` to serve locally-built assets without the embed tag
  - `generate.go`: `//go:generate go run generate_build.go` directive
  - `generate_build.go` (build tag `ignore`): the build script that finds the repo root, runs `pnpm run build` in `ui/`, and copies `ui/dist/public/` to `embed/public/`
  - `spa.go`: SPA catch-all handler that serves static files from the embedded filesystem, returns 404 for API-prefixed paths, and falls back to `index.html` for all other routes (enabling client-side routing)
- **Makefile targets**: `dev-backend` (runs smailnaild on port 3001), `dev-frontend` (runs Vite on port 3000), `frontend-build`, `frontend-check`, `build-embed` (frontend build + Go build with embed tag)

**Vite dev server configuration** (`b445b22`):

Changed the default Vite dev port to 5050 and made the backend proxy target configurable through environment variables:

- `SMAILNAIL_UI_BACKEND_URL` for an explicit URL
- `SMAILNAIL_UI_BACKEND_PORT` / `SMAILNAIL_UI_BACKEND_HOST` / `SMAILNAIL_UI_BACKEND_PROTOCOL` for composed URLs
- Added `ui/.env.example` documenting all configuration options

**Mailbox explorer and account delete** (`e6ee50b`):

Added the second major UI feature — browsing the actual contents of registered IMAP accounts:

- **`ui/src/features/mailbox/MailboxExplorer.tsx`**: three-column layout with mailbox sidebar, paginated message list, and message detail pane
- **`ui/src/features/mailbox/MailboxSidebar.tsx`**: lists available mailboxes with message counts, highlights the selected one
- **`ui/src/features/mailbox/MessageList.tsx`**: paginated envelope list showing subject, sender, date, and flag badges (unread, flagged)
- **`ui/src/features/mailbox/MessageDetail.tsx`**: full message view with headers (subject, from, to, date), text body, and a collapsible MIME structure tree showing content types and sizes
- **Account delete**: inline delete confirmation in the account list (click delete, confirm, account removed)
- **`ui/src/features/mailbox/mailboxSlice.ts`**: Redux slice with thunks for mailbox listing, message listing (with pagination), and full message fetch

Clicking an account in the list now transitions to the mailbox explorer view, and a back button returns to the account list.

**Rules CRUD and dry-run** (`e58bfe4`):

The third UI feature added complete rule management:

- **`ui/src/features/rules/RuleList.tsx`**: rules table with name, status badges (active/paused/draft), last-run timestamp, matched count, and inline delete with confirmation
- **`ui/src/features/rules/RuleForm.tsx`**: create/edit form with a YAML DSL text editor, account selector dropdown (populated from the accounts list), status picker, and name/description fields
- **`ui/src/features/rules/RuleDetail.tsx`**: read-only view of a rule showing its YAML definition, metadata, and quick-action buttons (edit, dry-run, delete)
- **`ui/src/features/rules/DryRunView.tsx`**: dry-run execution with a loading spinner, then results showing matched message count, action plan summary (e.g., "Move 5 messages to Archive"), and a sample table of matched messages
- **`ui/src/features/rules/RulesPage.tsx`**: orchestrates the rules flow through list/create/edit/detail/dry-run sub-views
- **`ui/src/features/rules/rulesSlice.ts`** (233 lines): Redux slice with thunks for list, create, update, delete, and dry-run
- **`ui/src/App.tsx`**: updated with header navigation between accounts and rules views

**Null data fix** (`1b4f054`):

The backend returns `{"data": null}` instead of `{"data": []}` for empty lists. All frontend list thunks were updated with `?? []` fallback to prevent `TypeError` on `.length` access.

## Architecture

```text
Internet
  -> https://smailnail.mcp.scapegoat.dev
     -> Coolify/Traefik (Hetzner)
     -> smailnail-imap-mcp container (port 3201)
        -> OIDC token validation via Keycloak
        -> executeIMAPJS / getIMAPJSDocumentation tools
        -> Go/JavaScript runtime with require("smailnail")

Browser
  -> http://localhost:5050 (dev) or embedded SPA (production)
  -> React SPA (ui/)
     -> Redux Toolkit state management
     -> /api/* proxied to smailnaild
  -> smailnaild (Go binary, port 8080)
     -> Chi HTTP router
     -> UserResolver (X-Smailnail-User-ID header, later OIDC)
     -> Account service
        -> Repository (SQLite/Postgres via sqlx)
        -> AEAD secrets (AES-GCM encrypted IMAP passwords)
        -> IMAP client (go-imap) for testing, mailbox listing, message fetch
     -> Rule service
        -> Repository (SQLite/Postgres via sqlx)
        -> DSL parser (YAML rule definitions)
        -> Dry-run executor (connects to IMAP, runs DSL, returns matches)
     -> go:embed SPA (production) / disk fallback (development)

Hetzner server (89.167.52.236)
  -> Coolify dashboard: hq.scapegoat.dev
  -> Keycloak: auth.scapegoat.dev
     -> Realm: smailnail
     -> Clients: smailnail-mcp, smailnail-mcp-smoke
  -> Dovecot fixture: ports 143, 993 (raw TCP, no Traefik)
     -> Test users: a, b, c, d (password: pass)
```

### Database schema

The application database uses incremental migrations (currently at v6):

| Version | Tables added | Purpose |
|---------|-------------|---------|
| v1 | `app_metadata` | Version tracking |
| v2 | `imap_accounts` | IMAP account storage with encrypted password field |
| v3 | `imap_account_tests` | Connection test history per account |
| v4 | `rules` | Email processing rules (name, YAML definition, status) |
| v5 | `rule_runs` | Rule execution history (dry-run and future real runs) |
| v6 | `users`, `user_external_identities`, `web_sessions` | OIDC identity model (schema ready, not yet wired) |

All data tables include a `user_id` column for multi-tenant isolation.

### Key code locations

| Component | Path | Lines |
|-----------|------|-------|
| CLI entrypoint | `cmd/smailnaild/main.go` | 58 |
| Server command | `cmd/smailnaild/commands/serve.go` | 143 |
| HTTP router & handlers | `pkg/smailnaild/http.go` | 513 |
| Database schema | `pkg/smailnaild/db.go` | 360 |
| Account repository | `pkg/smailnaild/accounts/repository.go` | 257 |
| Account service | `pkg/smailnaild/accounts/service.go` | 783 |
| Rule repository | `pkg/smailnaild/rules/repository.go` | 175 |
| Rule service | `pkg/smailnaild/rules/service.go` | 355 |
| AEAD encryption | `pkg/smailnaild/secrets/aead.go` | 84 |
| Encryption config | `pkg/smailnaild/secrets/config.go` | 89 |
| SPA handler | `pkg/smailnaild/web/spa.go` | 61 |
| Embed infrastructure | `pkg/smailnaild/web/embed.go`, `embed_none.go` | 59 |
| Build pipeline | `pkg/smailnaild/web/generate_build.go` | 107 |
| React app shell | `ui/src/App.tsx` | 56 |
| API client | `ui/src/api/client.ts` | 185 |
| Accounts Redux slice | `ui/src/features/accounts/accountsSlice.ts` | 339 |
| Mailbox Redux slice | `ui/src/features/mailbox/mailboxSlice.ts` | 158 |
| Rules Redux slice | `ui/src/features/rules/rulesSlice.ts` | 233 |

### API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/healthz` | Health check (always 200) |
| GET | `/readyz` | Readiness check (pings database) |
| GET | `/api/info` | Server metadata |
| GET | `/api/accounts` | List user's accounts with latest test summary |
| POST | `/api/accounts` | Create account (encrypts password) |
| GET | `/api/accounts/:id` | Get single account |
| PUT | `/api/accounts/:id` | Update account (re-encrypts if password changed) |
| DELETE | `/api/accounts/:id` | Delete account |
| POST | `/api/accounts/:id/test` | Run read-only IMAP connection test |
| GET | `/api/accounts/:id/mailboxes` | List IMAP mailboxes with message counts |
| GET | `/api/accounts/:id/messages` | Paginated message list (`?mailbox=&limit=&offset=&query=&unread_only=`) |
| GET | `/api/accounts/:id/messages/:uid` | Full message detail (headers, body, MIME tree) |
| GET | `/api/rules` | List user's rules with last-run info |
| POST | `/api/rules` | Create rule (validates YAML DSL) |
| GET | `/api/rules/:id` | Get single rule |
| PUT | `/api/rules/:id` | Update rule |
| DELETE | `/api/rules/:id` | Delete rule (cascades to rule_runs) |
| POST | `/api/rules/:id/dry-run` | Execute rule against IMAP without modifications |

## Docmgr tickets

The work was tracked across seven tickets:

| Ticket | Title | Status | Purpose |
|--------|-------|--------|---------|
| SMAILNAIL-008 | smailnaild SQL bootstrap | complete | CLI skeleton, database, HTTP surface |
| SMAILNAIL-009 | Local Docker stack | complete | Dovecot + Keycloak compose for development |
| SMAILNAIL-010 | MCP Coolify deployment | complete | Docker packaging, production deployment, OIDC auth, hosted Dovecot |
| SMAILNAIL-011 | OIDC identity guide | complete | Investigation: token flow, identity model, credential storage design |
| SMAILNAIL-012 | Web UI/UX research | complete | Investigation: product scope, screen mockups, phased implementation plan |
| SMAILNAIL-013 | Account setup implementation | active | Backend services, frontend SPA, end-to-end features |
| SMAILNAIL-014 | Shared OIDC implementation | active | User/identity schema, `ResolveOrProvisionUser`, session tables |

Ticket workspaces are located at:
`/home/manuel/workspaces/2026-03-08/update-imap-mcp/go-go-mcp/ttmp/2026/03/{15,16}/SMAILNAIL-0{08..14}-*/`

## Running locally

```bash
# Start infrastructure (Dovecot + Keycloak + Postgres)
cd /home/manuel/workspaces/2026-03-08/update-imap-mcp/smailnail
docker compose -f docker-compose.local.yml up -d

# Start backend (separate terminal)
export SMAILNAILD_ENCRYPTION_KEY_BASE64="$(openssl rand -base64 32)"
go run ./cmd/smailnaild serve --encryption-key-base64 "$SMAILNAILD_ENCRYPTION_KEY_BASE64"

# Start frontend dev server (separate terminal)
cd ui && pnpm run dev
# -> http://localhost:5050 (proxies /api to localhost:8080)
```

For a production-style embedded build:

```bash
make build-embed
# Produces a single binary with the SPA baked in
./dist/smailnaild serve --encryption-key-base64 "$SMAILNAILD_ENCRYPTION_KEY_BASE64"
```

## Testing

```bash
# Unit tests only
go test ./pkg/smailnaild/...

# Integration tests (requires local Dovecot from docker-compose.local.yml)
export SMAILNAILD_ENCRYPTION_KEY_BASE64="$(openssl rand -base64 32)"
SMAILNAILD_DOVECOT_TEST=1 go test ./pkg/smailnaild/... -v

# Specific integration suites
SMAILNAILD_DOVECOT_TEST=1 go test ./pkg/smailnaild/accounts -run TestServiceAgainstLocalDovecot -v
SMAILNAILD_DOVECOT_TEST=1 go test ./pkg/smailnaild/rules -run TestDryRunAgainstLocalDovecot -v
SMAILNAILD_DOVECOT_TEST=1 go test ./pkg/smailnaild -run TestHostedHTTPFlowAgainstLocalDovecot -v
```

## Related projects

- [[PROJ - Coolify Hetzner - Self-Hosted Deployment Platform]] — the Hetzner/Coolify server hosting the MCP endpoint and Dovecot fixture
- Prior smailnail tickets (SMAILNAIL-001 through SMAILNAIL-007) cover the original CLI tools, Glazed facade migration, JavaScript module implementation, and MCP server design — these are in the `go-go-mcp` docmgr workspace

## Important project docs

- `docs/smailnaild-local-account-flow.md` — step-by-step local testing walkthrough with curl examples for every API endpoint
- `docs/deployments/smailnail-imap-mcp-coolify.md` — MCP Coolify deployment guide (container defaults, environment variables, Keycloak expectations, verification commands)
- `docs/deployments/smailnail-dovecot-coolify.md` — hosted Dovecot fixture documentation (service UUID, test users, validation commands)
- `ui/.env.example` — frontend environment variable reference

## Open questions

- **OIDC web sessions**: Should the browser login flow use Keycloak's authorization code flow with PKCE, or should the frontend get tokens from a separate login page and pass them as bearer tokens?
- **smailnaild Coolify deployment**: Should it go on the same Hetzner server, or does it need its own instance given it holds encrypted credentials?
- **Rule execution model**: Beyond dry-run — cron-scheduled execution, webhook-triggered execution, or manual one-shot from the UI?
- **YAML editor upgrade**: Should the rule form use Monaco Editor or CodeMirror for syntax highlighting and validation, or is a plain textarea sufficient for the current DSL complexity?
- **OpenAI MCP connector**: Keycloak's trusted-hosts policy blocks OpenAI's rotating Azure IPs during dynamic client registration. Options: disable trusted-hosts, use a static pre-registered client, or wait for OpenAI to support pre-registered clients.
- **MCP-to-smailnaild bridge**: Should the MCP server be able to resolve the calling user's stored accounts from smailnaild, so `executeIMAPJS` doesn't require inline credentials?

## Near-term next steps

- Wire Keycloak OIDC sessions into the smailnaild web app (SMAILNAIL-014 is in progress with schema ready)
- Deploy smailnaild itself on Coolify
- Add real rule execution (not just dry-run) with an execution log
- UI improvements: loading states, error toasts, responsive layout, YAML syntax highlighting
- Bridge MCP and smailnaild so authenticated MCP users can use their stored accounts

## Project working rule

> [!important]
> The backend and frontend are developed in tandem on the same branch (`task/update-imap-mcp`).
> Integration tests against a real Dovecot fixture are the primary correctness gate — avoid mocking IMAP.
> The `go:embed` pipeline means the frontend must build cleanly before the Go binary can ship with UI included.
> Vertical slices (database through UI for one feature) are preferred over horizontal layers (all repositories, then all services, then all handlers).
