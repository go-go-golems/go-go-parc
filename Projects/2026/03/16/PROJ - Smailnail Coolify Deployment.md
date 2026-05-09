---
title: Smailnail Coolify Deployment
aliases:
  - Smailnail Coolify Deployment
  - Project Smailnail Coolify Deployment
  - smailnail-mcp Coolify
tags:
  - project
  - coolify
  - devops
  - mcp
  - keycloak
  - oidc
  - imap
  - docker
  - hetzner
  - self-hosted
status: active
type: project
created: 2026-03-16
repo: /home/manuel/workspaces/2026-03-08/update-imap-mcp/smailnail
branch: task/update-imap-mcp
server: 89.167.52.236
mcp-url: https://smailnail.mcp.scapegoat.dev/mcp
keycloak-issuer: https://auth.scapegoat.dev/realms/smailnail
dovecot-host: 89.167.52.236
---

# Smailnail Coolify Deployment

This project covers the production deployment of the `smailnail-imap-mcp` MCP server and a companion Dovecot test fixture on the [[PROJ - Coolify Hetzner - Self-Hosted Deployment Platform|Coolify Hetzner]] server, including Keycloak OIDC authentication, Docker packaging, and end-to-end validation. It is the first real application workload deployed on the Coolify platform.

> [!summary]
> Two services were deployed on the Hetzner/Coolify server at `89.167.52.236`:
> 1. **smailnail-imap-mcp**: a streamable-HTTP MCP server at `https://smailnail.mcp.scapegoat.dev/mcp` with Keycloak-backed OIDC bearer token authentication, allowing AI agents (Claude, etc.) to execute JavaScript against IMAP mailboxes
> 2. **Dovecot test fixture**: a raw-port IMAP server on the standard mail ports (143, 993, etc.) mirroring the local development fixture, used for remote end-to-end testing
>
> The work was tracked under docmgr ticket **SMAILNAIL-010** and produced 7 commits, 9 deployment scripts, a 368-line recreation guide, a 420-line OpenAI/Keycloak DCR debug guide, and a Go-based authenticated MCP smoke client.

## Why this project exists

The `smailnail-imap-mcp` MCP server exposes two tools — `executeIMAPJS` (run JavaScript against IMAP mailboxes) and `getIMAPJSDocumentation` (query embedded docs) — that make email accessible to AI agents. But until this deployment, the server only ran locally over stdio. There was no way for Claude or other remote AI tools to reach it.

For the consolidated identity and hosted-auth follow-up that came after this initial deployment, see:

- [[PROJ - Smailnail OIDC Identity and Hosted Auth]]

Getting the MCP server onto a public HTTPS endpoint required solving several problems at once:

- **Docker packaging**: the Go binary had a CGO dependency (tree-sitter JavaScript parser) that ruled out static linking, so the container image needed a glibc runtime rather than Alpine or a scratch image.
- **Authentication**: a public MCP endpoint without auth is a security problem. The server already had `external_oidc` support in its auth middleware, but it needed a real Keycloak realm and client configuration to use it.
- **Health monitoring**: Coolify runs health checks inside the container, so the runtime image needed `curl` — a lesson learned from a failed first deployment.
- **Remote testing**: validating the MCP server end-to-end required a real IMAP server reachable from the same network, not just a localhost Dovecot.
- **Reproducibility**: the deployment needed to be scriptable and documented, not a one-off series of dashboard clicks.

## Current deployment status

Both services are live and validated.

### MCP server

| Property | Value |
|----------|-------|
| Public URL | `https://smailnail.mcp.scapegoat.dev/mcp` |
| Transport | streamable HTTP |
| Container port | 3201 |
| Auth mode | `external_oidc` |
| Keycloak issuer | `https://auth.scapegoat.dev/realms/smailnail` |
| Health check path | `/.well-known/oauth-protected-resource` |
| Coolify app UUID | `fhp3mxqlfftdxdib3vxz89l3` |
| Build source | Public Git repo, branch `task/update-imap-mcp` |
| Dockerfile | `Dockerfile` (repo root) |
| Status | `running:healthy` |

Unauthenticated requests to `/mcp` correctly return HTTP 401 with a `WWW-Authenticate` header pointing to the Keycloak authorization endpoint. The `/.well-known/oauth-protected-resource` metadata endpoint is publicly accessible and returns the expected OAuth resource metadata.

### Dovecot fixture

| Property | Value |
|----------|-------|
| Host | `89.167.52.236` |
| IMAP port | 143 |
| IMAPS port | 993 |
| Other ports | 24 (LMTP), 110 (POP3), 995 (POP3S), 4190 (ManageSieve) |
| TLS | Self-signed (requires `--insecure`) |
| Test users | `a`, `b`, `c`, `d`, `rxa`, `rxb`, `rxc`, `rxd` |
| Password | `pass` (all users) |
| Image | `ghcr.io/spezifisch/docker-test-dovecot:latest` |
| Coolify service UUID | `gh32795yh1av2dpi2j6lhn6h` |
| Coolify service name | `smailnail-dovecot-fixture` |
| Status | `running:unknown` (raw TCP ports, no HTTP health check) |

The fixture uses raw host port bindings — no Traefik routing. Coolify reports `running:unknown` because there is no HTTP-style health probe for raw mail ports. Persistence is via named Docker volumes for `/home` (Maildirs) and `/etc/dovecot/ssl` (generated TLS material).

### Keycloak configuration

On the existing Keycloak instance at `https://auth.scapegoat.dev`:

| Property | Value |
|----------|-------|
| Realm | `smailnail` |
| Issuer | `https://auth.scapegoat.dev/realms/smailnail` |

Two clients are registered:

| Client | Type | Purpose |
|--------|------|---------|
| `smailnail-mcp` | Public | OAuth client for Claude and other AI consumers. Configured with Claude callback URIs, `standardFlowEnabled`. |
| `smailnail-mcp-smoke` | Confidential (service account) | Automated testing. Used by the smoke scripts to obtain bearer tokens via client credentials grant. |

## Docker packaging

### Image design

The `Dockerfile` uses a two-stage build:

**Builder stage** (`golang:1.25.8-bookworm`):
- Copies `go.mod`/`go.sum`, runs `go mod download` for layer caching
- Copies full source, builds `smailnail-imap-mcp` with `-trimpath -ldflags="-s -w"` for a stripped binary
- Targets `GOOS=linux GOARCH=amd64`

**Runtime stage** (`debian:bookworm-slim`):
- Installs `ca-certificates` (TLS to Keycloak), `curl` (Coolify health checks), `tzdata`
- Copies the compiled binary and entrypoint script
- Exposes port 3201

The Debian runtime was a deliberate choice. An early attempt with `CGO_ENABLED=0` (static linking) failed because the tree-sitter JavaScript parser — used by the MCP server's JS execution engine — requires CGO. Alpine was skipped because musl-linked CGO binaries have historically caused subtle issues; the Debian glibc runtime avoids this class of problems entirely.

Both `Dockerfile` (Coolify-facing) and `Dockerfile.smailnail-imap-mcp` (standalone) exist and are currently identical.

### Entrypoint script

`scripts/docker-entrypoint.smailnail-imap-mcp.sh` is a POSIX shell script that assembles the MCP server command entirely from environment variables:

```text
Passthrough mode:  docker run <image> mcp start --transport sse --port 9000
Default mode:      smailnail-imap-mcp mcp start --transport streamable_http --port 3201
```

**Environment variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `SMAILNAIL_MCP_TRANSPORT` | `streamable_http` | MCP transport protocol |
| `SMAILNAIL_MCP_PORT` | `3201` | Listen port |
| `SMAILNAIL_MCP_AUTH_MODE` | `none` | Auth mode (`none`, `external_oidc`) |
| `SMAILNAIL_MCP_AUTH_RESOURCE_URL` | — | OAuth protected resource URL |
| `SMAILNAIL_MCP_OIDC_ISSUER_URL` | — | Keycloak issuer URL |
| `SMAILNAIL_MCP_OIDC_DISCOVERY_URL` | — | Custom OIDC discovery URL |
| `SMAILNAIL_MCP_OIDC_AUDIENCE` | — | Expected JWT audience |
| `SMAILNAIL_MCP_OIDC_REQUIRED_SCOPES` | — | Comma-separated required scopes |
| `SMAILNAIL_MCP_INTERNAL_SERVERS` | — | Comma-separated internal MCP servers |
| `SMAILNAIL_MCP_EXTRA_ARGS` | — | Additional CLI arguments (pass-through) |

Comma-separated values (`REQUIRED_SCOPES`, `INTERNAL_SERVERS`) are split with `IFS=','` and mapped to repeated `--oidc-required-scope` or `--internal-servers` flags.

### .dockerignore

Excludes development artifacts from the build context: `.git`, `node_modules`, local SQLite databases, IDE configs, and the `ui/` frontend directory (not needed for the MCP binary).

## Routing model

Coolify routes the full host `https://smailnail.mcp.scapegoat.dev` to container port 3201 through Traefik. There is no Coolify-side path rewrite — the `/mcp` path comes from the MCP binary itself:

```text
Internet
  -> DNS: smailnail.mcp.scapegoat.dev -> 89.167.52.236
  -> Traefik v3.6 (port 443, TLS termination)
  -> Docker network -> container fhp3mxqlfftdxdib3vxz89l3-* (port 3201)
     -> /.well-known/oauth-protected-resource  -> public metadata handler
     -> /mcp                                    -> MCP HTTP handler (requires bearer token)
```

The Dovecot fixture bypasses Traefik entirely. Its ports are bound directly to the host network interface — standard for non-HTTP services on Coolify.

## Deployment chronicle

### Step 1: Repository packaging (commit `ab5df7b`)

Created the Docker build artifacts:
- `Dockerfile.smailnail-imap-mcp` (multi-stage build)
- `.dockerignore`
- `scripts/docker-entrypoint.smailnail-imap-mcp.sh`
- `docs/deployments/smailnail-imap-mcp-coolify.md`
- Updated `pkg/mcp/imapjs/server.go` to default transport to `streamable_http` on port 3201

Local validation: built the image, started a container with `external_oidc` pointed at the public Keycloak master realm, confirmed that the `/.well-known/oauth-protected-resource` endpoint returned valid metadata and `/mcp` returned 401.

**Discovery**: `CGO_ENABLED=0` failed to build due to tree-sitter. Switched to glibc-based Debian runtime.

### Step 2: Coolify app creation and Keycloak setup (commit `f24629d`)

Added the standard root `Dockerfile` as the Coolify build entrypoint. Created the Coolify app via API:

```bash
coolify app create public \
  --server-uuid cgl105090ljoxitdf7gmvbrm \
  --project-uuid n8xkgqpbjj04m4pishy3su5e \
  --environment-name production \
  --name smailnail-imap-mcp \
  --git-repository https://github.com/wesen/smailnail \
  --git-branch task/update-imap-mcp \
  --build-pack dockerfile \
  --ports-exposes 3201 \
  --domains https://smailnail.mcp.scapegoat.dev \
  --health-check-enabled \
  --health-check-path /.well-known/oauth-protected-resource
```

Created the Keycloak `smailnail` realm on `auth.scapegoat.dev` with the `smailnail-mcp` public client, configured with Claude OAuth callback URIs.

**Discovery**: The Coolify CLI `env` helper sends `is_build_time` while the API expects `is_buildtime`. Environment variables were set via direct API calls instead:

```bash
curl -s -X PATCH "https://hq.scapegoat.dev/api/v1/applications/$APP_UUID/envs" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"key":"SMAILNAIL_MCP_TRANSPORT","value":"streamable_http","is_buildtime":false,"is_preview":false}'
```

This created duplicate rows that had to be cleaned up with a dedup script.

**First deployment failed** — health checks timed out.

### Step 3: Health check fix (commit `6072f7c`)

The failure was because Coolify runs health probes *inside* the container, and `debian:bookworm-slim` doesn't include `curl`. Added `curl` to the `apt-get install` line in both Dockerfiles.

After redeployment:
- Container status: `running:healthy`
- `curl https://smailnail.mcp.scapegoat.dev/.well-known/oauth-protected-resource` returned valid JSON
- `curl -i -d '...' https://smailnail.mcp.scapegoat.dev/mcp` returned HTTP/2 401 with `WWW-Authenticate` header

### Step 4: MCP routing documentation (commits `3f4f29b`, `53ddf87`)

Documented how the `/mcp` path works — it's not a Traefik rewrite, it's the binary's own route — and explained the Coolify routing model for future reference.

### Step 5: Hosted Dovecot fixture (commits `04f2762`, `39e375a`)

Deployed a Dovecot test fixture on the same Hetzner server so that remote end-to-end tests wouldn't need to reach a developer's local machine.

Created `deployments/coolify/smailnail-dovecot.compose.yaml` — a minimal Docker Compose with the `ghcr.io/spezifisch/docker-test-dovecot` image, raw host port bindings (24, 110, 143, 993, 995, 4190), and named volumes for persistence.

The Coolify service was created by base64-encoding the compose file and posting it to the Coolify API as a Docker Compose service. Initial API issues: the `connect_to_docker_network` field was rejected and had to be removed from the payload.

**Validation**: used the existing `imap-tests` CLI to create a remote mailbox (`Archive`) for user `a`, store a test message with subject "Hosted Coolify Dovecot Test", and fetch it back — all against `89.167.52.236:993` with `--insecure` for the self-signed TLS certificate.

### Step 6: Authenticated MCP smoke test

This was the full end-to-end proof. Two artifacts were created:

**`smoke_hosted_mcp_oidc.go`** (~250 lines): a standalone Go program that:
1. Obtains an access token from Keycloak using the client credentials grant (the `smailnail-mcp-smoke` confidential client)
2. Opens a streamable-HTTP MCP session to `https://smailnail.mcp.scapegoat.dev/mcp` with the bearer token
3. Calls `tools/list` — verifies the expected tools are present
4. Calls `executeIMAPJS` with JavaScript that connects to the hosted Dovecot and returns `{"mailbox":"INBOX"}`

**`smoke_hosted_mcp_oidc.sh`**: a wrapper that automatically fetches the smoke client secret from Keycloak admin API and invokes the Go client.

**Result**: the full chain worked — Keycloak token acquisition, OIDC-authenticated MCP session, tool listing, JavaScript execution against hosted IMAP, and response. This validated every layer: Traefik TLS, Coolify routing, container health, MCP protocol, OIDC middleware, Keycloak token validation, and remote IMAP connectivity.

### Step 7: OpenAI connector investigation

After the smoke test succeeded with a custom client, the next goal was making the MCP endpoint work with OpenAI's built-in MCP connector. OpenAI uses RFC 7591 dynamic client registration (DCR) to register itself with the OAuth provider at connection time.

This hit multiple Keycloak policy blockers:

1. **Trusted Hosts policy**: Keycloak's anonymous DCR policy checks the registering client's IP against a trusted-hosts list. OpenAI's requests come from rotating Azure IPs that can't be pre-listed.

2. **Allowed Client Scopes policy**: OpenAI's DCR request includes scopes that Keycloak's policy doesn't permit for anonymous registrations (specifically, `openid` was missing from the allowed set).

3. **RFC 8707 audience handling** (anticipated next issue): even if DCR succeeds, OpenAI may send `resource` parameters in token requests that Keycloak doesn't yet handle.

A 420-line debug guide was written documenting the exact failure modes, Keycloak log evidence, and three remediation options:
- **Option A**: Temporarily disable Trusted Hosts and Allowed Client Scopes policies for debugging
- **Option B**: Keep anonymous DCR but properly configure both policies (add all required scopes, widen or disable trusted hosts)
- **Option C**: Avoid anonymous DCR entirely — pre-register OpenAI as a static client in Keycloak

This remains unresolved. The MCP endpoint works perfectly with any client that can obtain a token through normal OAuth flows (client credentials, authorization code) — the problem is specific to OpenAI's DCR-based connection model.

## Deployment scripts

All operational scripts are in the SMAILNAIL-010 ticket workspace at:
`/home/manuel/workspaces/2026-03-08/update-imap-mcp/go-go-mcp/ttmp/2026/03/16/SMAILNAIL-010-MCP-COOLIFY-DEPLOYMENT--deploy-smailnail-mcp-to-coolify-with-keycloak-external-oidc/scripts/`

| Script | What it does |
|--------|-------------|
| `create_coolify_mcp_app.sh` | Creates the Coolify app from the public Git repo with domain, port, and health check configuration |
| `set_coolify_mcp_envs.sh` | Sets the 5 MCP environment variables via direct Coolify API calls (workaround for CLI bug) |
| `dedupe_coolify_mcp_envs.sh` | Cleans up duplicate environment variable rows created by the API workaround |
| `create_keycloak_realm_and_mcp_client.sh` | Creates the `smailnail` Keycloak realm and the `smailnail-mcp` public client with Claude callback URIs |
| `create_keycloak_smoke_client.sh` | Creates the `smailnail-mcp-smoke` confidential service-account client for automated testing |
| `create_coolify_dovecot_service.sh` | Creates the hosted Dovecot fixture as a Coolify Docker Compose service (base64-encodes the compose YAML) |
| `smoke_hosted_dovecot.sh` | Validates hosted IMAP: creates mailbox, stores message, fetches message back |
| `smoke_hosted_mcp_oidc.sh` | Fetches Keycloak smoke client secret, invokes the Go MCP smoke client |
| `smoke_hosted_mcp_oidc.go` | Streamable-HTTP MCP client with OIDC bearer auth — full end-to-end validation |

These scripts are intentionally hardcoded to the current deployment UUIDs and server addresses. They serve as executable documentation rather than general-purpose tooling.

## Reference documentation

Three reference documents exist in the SMAILNAIL-010 ticket workspace:

- **`reference/01-diary.md`** (738 lines): the full chronological deployment diary across 8 steps, each with prompt context, actions taken, what worked/failed, what was learned, and code review instructions.
- **`reference/02-recreate-and-verify-hosted-smailnail-mcp.md`** (368 lines): a standalone recreation guide that walks through the complete deployment from scratch — preconditions, repo-side shape, Coolify context bootstrap, Keycloak setup, app creation, env configuration, deploy, verify, and authenticated smoke. Written so someone could reproduce the deployment without reading the diary.
- **`reference/03-openai-keycloak-dcr-debug-guide.md`** (420 lines): analysis of the OpenAI MCP connector failure, including live system evidence (Keycloak logs, DCR probe results), policy state dumps, root cause stack, and three remediation options with operator playbooks.

## Problems encountered and lessons learned

### CGO and tree-sitter
**Problem**: `CGO_ENABLED=0` build failed — tree-sitter JavaScript parser requires CGO.
**Solution**: Use `debian:bookworm-slim` runtime with glibc instead of Alpine or static linking.
**Lesson**: Always check CGO dependencies before assuming static builds will work. Tree-sitter is a transitive dependency through the JavaScript execution engine.

### Coolify health checks run inside containers
**Problem**: First deployment failed health checks because `debian:bookworm-slim` doesn't include `curl`.
**Solution**: Added `curl` to the `apt-get install` line in the Dockerfile.
**Lesson**: Coolify's health check model is exec-based (runs inside the container), not probe-based (hits from outside). Every runtime image needs `curl` or `wget`.

### Coolify CLI environment variable bug
**Problem**: The `coolify` CLI sends `is_build_time` in the API payload, but the Coolify API expects `is_buildtime` (no underscore before "time"). The CLI silently fails.
**Solution**: Set environment variables via direct `curl` API calls.
**Side effect**: Manual API calls created duplicate environment variable rows that needed cleanup.
**Lesson**: The Coolify CLI is beta software with undocumented payload mismatches. Always verify environment variables via the API or dashboard after setting them.

### Coolify Docker Compose service API
**Problem**: The API for creating Docker Compose services rejected the `connect_to_docker_network` field.
**Solution**: Removed the field from the payload.
**Lesson**: Coolify's compose service API accepts base64-encoded compose YAML but is picky about extra fields. Test the API payload before scripting.

### OpenAI DCR and Keycloak policies
**Problem**: OpenAI's MCP connector uses RFC 7591 dynamic client registration, which Keycloak gates behind anonymous DCR policies. OpenAI's rotating Azure IPs fail the Trusted Hosts check, and its scope requests fail the Allowed Client Scopes check.
**Status**: Unresolved. The MCP endpoint works with any standard OAuth client.
**Lesson**: Keycloak's anonymous DCR policies are designed for controlled environments, not for arbitrary internet clients with rotating IPs. The safest path is likely pre-registering OpenAI as a static client (Option C) rather than trying to configure anonymous DCR to accept unknown registrants.

## Architecture

```text
Internet
  -> DNS: smailnail.mcp.scapegoat.dev -> 89.167.52.236
  -> Traefik v3.6 (port 443, Let's Encrypt TLS)
  -> Coolify app fhp3mxqlfftdxdib3vxz89l3 (port 3201)
     -> docker-entrypoint.sh
     -> smailnail-imap-mcp mcp start
        --transport streamable_http
        --port 3201
        --auth-mode external_oidc
        --auth-resource-url https://smailnail.mcp.scapegoat.dev/mcp
        --oidc-issuer-url https://auth.scapegoat.dev/realms/smailnail
     -> /.well-known/oauth-protected-resource  (public)
     -> /mcp                                    (bearer token required)
        -> OIDC middleware validates JWT against Keycloak JWKS
        -> MCP session handler
           -> tools/list, executeIMAPJS, getIMAPJSDocumentation

89.167.52.236 (raw TCP, no Traefik)
  -> Coolify service gh32795yh1av2dpi2j6lhn6h
  -> Dovecot container
     -> :143 IMAP, :993 IMAPS, :24 LMTP, :110 POP3, :995 POP3S, :4190 Sieve
     -> Self-signed TLS, test users a/b/c/d (pass)

auth.scapegoat.dev (existing Keycloak 26.1)
  -> Realm: smailnail
  -> Client: smailnail-mcp (public, Claude callbacks)
  -> Client: smailnail-mcp-smoke (confidential, service account)
  -> JWKS endpoint for MCP token validation
  -> Token endpoint for client credentials grants
```

## Coolify resource IDs

| Resource | UUID | Notes |
|----------|------|-------|
| Server | `cgl105090ljoxitdf7gmvbrm` | Hetzner ubuntu-16gb-hel1-1 |
| Project | `n8xkgqpbjj04m4pishy3su5e` | — |
| MCP app | `fhp3mxqlfftdxdib3vxz89l3` | Public Git build from `wesen/smailnail` |
| Dovecot service | `gh32795yh1av2dpi2j6lhn6h` | Docker Compose service, raw ports |

## Verification commands

```bash
# MCP public metadata
curl -s https://smailnail.mcp.scapegoat.dev/.well-known/oauth-protected-resource | jq

# MCP unauthenticated (should return 401)
curl -i \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":"1","method":"tools/list","params":{}}' \
  https://smailnail.mcp.scapegoat.dev/mcp

# Hosted Dovecot IMAPS reachability
bash -lc 'exec 3<>/dev/tcp/89.167.52.236/993 && echo open && exec 3<&- && exec 3>&-'

# Hosted Dovecot fetch test
go run ./cmd/smailnail fetch-mail \
  --server 89.167.52.236 --port 993 \
  --username a --password pass \
  --insecure --output yaml

# Full authenticated MCP smoke (from ticket scripts)
cd /home/manuel/workspaces/2026-03-08/update-imap-mcp/go-go-mcp/ttmp/2026/03/16/SMAILNAIL-010-MCP-COOLIFY-DEPLOYMENT--deploy-smailnail-mcp-to-coolify-with-keycloak-external-oidc/scripts
./smoke_hosted_mcp_oidc.sh
```

## Related projects

- [[PROJ - Coolify Hetzner - Self-Hosted Deployment Platform]] — the underlying Hetzner/Coolify server, Traefik proxy, and Keycloak instance
- [[PROJ - Smailnail Hosted Backend and SPA]] — the `smailnaild` backend and React SPA (not yet deployed on Coolify)

## Important project docs

- `docs/deployments/smailnail-imap-mcp-coolify.md` — in-repo deployment guide (container defaults, env vars, Coolify app shape, Keycloak expectations, verification)
- `docs/deployments/smailnail-dovecot-coolify.md` — in-repo hosted Dovecot documentation (service UUID, ports, test users, validation commands)
- SMAILNAIL-010 ticket workspace — full diary, recreation guide, DCR debug guide, and deployment scripts (path above)

## Open questions

- **OpenAI DCR**: Should Keycloak anonymous policies be loosened, or should OpenAI be pre-registered as a static client? The static client approach is simplest but requires knowing OpenAI's redirect URIs in advance.
- **smailnaild deployment**: Should `smailnaild` (the hosted backend with SPA) go on the same Hetzner server? It would need its own Dockerfile (with `--tags embed` for the SPA), encrypted secret management, and a Keycloak client for browser-based login.
- **Dovecot fixture security**: The hosted Dovecot is on raw public ports with known test credentials (`pass`). It's fine for testing but should not be advertised or confused with a real mail server. Should it be firewalled to only accept connections from the Coolify container network?
- **Monitoring**: Should Uptime Kuma or similar monitor the MCP endpoint and Dovecot fixture?
- **TLS for Dovecot**: The fixture uses self-signed certificates. For automated testing from CI, should a Let's Encrypt certificate be provisioned, or is `--insecure` acceptable for test fixtures?

## Near-term next steps

- Resolve the OpenAI DCR issue (likely Option C: static client registration)
- Deploy `smailnaild` on Coolify alongside the MCP server
- Add Keycloak `audience` and `required-scopes` enforcement once client configuration stabilizes
- Consider adding monitoring for the MCP endpoint
- Investigate firewalling the Dovecot fixture to the Coolify container network

## Project working rule

> [!important]
> All deployment changes must be reflected in both the in-repo docs (`docs/deployments/`) and the SMAILNAIL-010 ticket diary.
> Deployment scripts in the ticket workspace are the source of truth for Coolify and Keycloak configuration — they are executable documentation, not throwaway helpers.
> The recreation guide (`reference/02-recreate-and-verify-hosted-smailnail-mcp.md`) must stay current so the deployment can be rebuilt from scratch.
