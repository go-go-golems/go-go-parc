---
title: Keycloak Identity Platform on Coolify
aliases:
  - Keycloak Identity Platform
  - Project Keycloak
  - auth.scapegoat.dev
tags:
  - project
  - keycloak
  - oidc
  - identity
  - authentication
  - coolify
  - hetzner
  - self-hosted
status: active
type: project
created: 2026-03-16
domain: auth.scapegoat.dev
server: 89.167.52.236
---

# Keycloak Identity Platform on Coolify

This project covers the deployment, configuration, and ongoing operation of Keycloak 26.1 as the central identity provider on the [[PROJ - Coolify Hetzner - Self-Hosted Deployment Platform|Coolify Hetzner]] server. Keycloak provides OIDC-based authentication for all services running on the `scapegoat.dev` domain — currently the smailnail MCP server, with the smailnail hosted backend next in line.

For the `smailnail`-specific shared-identity and merged-host work that now depends on this Keycloak setup, see:

- [[PROJ - Smailnail OIDC Identity and Hosted Auth]]

> [!summary]
> Keycloak runs at `https://auth.scapegoat.dev` as a Coolify-managed Docker Compose service with a PostgreSQL backing database. It currently hosts two realms:
> 1. **`smailnail`** — production realm with clients for the MCP server (`smailnail-mcp`) and automated testing (`smailnail-mcp-smoke`)
> 2. **`master`** — Keycloak's built-in admin realm
>
> A local development counterpart runs via Docker Compose in the smailnail repo with a `smailnail-dev` realm and pre-imported clients. The OIDC integration design was formalized in MCP-003, which produced the `external_oidc` auth mode used by the MCP server.

## Why Keycloak

The `scapegoat.dev` platform needs a single identity provider that can issue tokens for multiple services without each service implementing its own auth. Keycloak was chosen because:

- **Standard OIDC**: any service that can validate a JWT can consume Keycloak tokens. The MCP server uses local JWT verification (JWKS fetch + signature/issuer/audience/expiry checks) with no introspection calls back to Keycloak at request time.
- **Realm isolation**: each application gets its own realm with independent users, clients, and policies. The `smailnail` realm is completely separate from the admin `master` realm.
- **Client flexibility**: supports public clients (browser SPAs, Claude OAuth callbacks), confidential clients (service accounts for automated testing), and dynamic client registration (RFC 7591, though this hit issues with OpenAI — see below).
- **Already deployed**: Keycloak was provisioned during the initial Coolify server setup (COOLIFY-001) before any application workloads existed.

## Current deployment status

### Production instance

| Property | Value |
|----------|-------|
| URL | `https://auth.scapegoat.dev` |
| Admin console | `https://auth.scapegoat.dev/admin/` |
| Version | 26.1 |
| Mode | Production (HTTPS via Traefik) |
| Container | `keycloak-k12lm4blpo13louovn3pfsgs` |
| Coolify service directory | `/data/coolify/services/k12lm4blpo13louovn3pfsgs/` |
| Backing database | Standalone PostgreSQL container (`go1o5tbegalwy3kesshq3hcp`, port 5432) |
| TLS | Let's Encrypt via Traefik, TLSv1.3 |
| Backup frequency | Every 6 hours (Coolify built-in scheduler for PostgreSQL) |

Admin credentials are stored in the Coolify service environment file at `/data/coolify/services/k12lm4blpo13louovn3pfsgs/.env` under `SERVICE_USER_ADMIN` and `SERVICE_PASSWORD_ADMIN`.

### Local development instance

| Property | Value |
|----------|-------|
| URL | `http://127.0.0.1:18080` |
| Admin console | `http://127.0.0.1:18080/admin` |
| Admin credentials | `admin` / `admin` |
| Mode | Development (`start-dev`) |
| Realm | `smailnail-dev` (auto-imported) |
| Compose file | `docker-compose.local.yml` in the smailnail repo |
| Backing database | PostgreSQL container on port 5432 (`keycloak` / `keycloak`) |

Started with:
```bash
cd /home/manuel/workspaces/2026-03-08/update-imap-mcp/smailnail
docker compose -f docker-compose.local.yml up -d
```

## Realms and clients

### Production: `smailnail` realm

**Issuer**: `https://auth.scapegoat.dev/realms/smailnail`
**Discovery**: `https://auth.scapegoat.dev/realms/smailnail/.well-known/openid-configuration`

This realm was created during SMAILNAIL-010 when the MCP server was deployed to Coolify.

| Client | Type | Purpose | Redirect URIs |
|--------|------|---------|---------------|
| `smailnail-mcp` | Public | OAuth client for Claude and other AI consumers connecting to the MCP server | Claude OAuth callback URIs |
| `smailnail-mcp-smoke` | Confidential (service account) | Automated smoke testing — obtains bearer tokens via client credentials grant | — |

The `smailnail-mcp` client has `standardFlowEnabled` for the authorization code flow. It's a public client because AI tools like Claude perform the OAuth flow in a browser context where a client secret can't be kept confidential.

The `smailnail-mcp-smoke` client is confidential with a client secret, used by the smoke test scripts to programmatically obtain tokens without a browser. Its secret can be retrieved from the Keycloak admin API.

#### Anonymous DCR policies

Keycloak's dynamic client registration (RFC 7591) is active on this realm with two anonymous policies:

- **Trusted Hosts**: restricts which IP addresses can register clients without a bearer token
- **Allowed Client Scopes**: restricts which scopes anonymous registrations can request

These policies caused issues with OpenAI's MCP connector (see "OpenAI DCR problem" below).

### Local development: `smailnail-dev` realm

**Issuer**: `http://127.0.0.1:18080/realms/smailnail-dev`

Imported automatically from `dev/keycloak/realm-import/smailnail-dev-realm.json` in the smailnail repo.

| Client | Type | Purpose |
|--------|------|---------|
| `smailnail-web` | Confidential | Future SPA browser login flow (redirects to `localhost:8081`) |
| `smailnail-mcp` | Public | Local MCP server OIDC validation (redirects to `localhost/*`) |

The local realm is intentionally simpler than the production one — no smoke client, no DCR policies. It exists for development iteration without touching the production Keycloak.

### MCP-003 test realm (separate workspace)

A third Keycloak configuration exists in the MCP-003 ticket workspace for testing the `external_oidc` auth mode implementation:

**Compose**: `/home/manuel/workspaces/2026-03-08/update-imap-mcp/go-go-mcp/ttmp/2026/03/09/MCP-003-KEYCLOAK-EXTERNAL-OIDC-DESIGN--*/scripts/keycloak-local/docker-compose.yml`
**Realm**: `mcp-local`
**Clients**:
- `mcp-cli-basic` (secret: `mcp-cli-basic-secret`) — basic issuer validation only
- `mcp-cli-strict` (secret: `mcp-cli-strict-secret`) — strict mode with audience (`mcp-resource`) and scope (`mcp-invoke`) enforcement

This is the test fixture that was used during the development and validation of the `external_oidc` auth provider in go-go-mcp.

## How Keycloak was deployed

Keycloak was deployed as part of the initial Coolify server setup (COOLIFY-001, Step 4 of the diary). It was provisioned through the Coolify dashboard as a managed Docker Compose service, not from a custom Dockerfile.

### Initial state

When the Hetzner server was first assessed, Keycloak was already running (created during Coolify's guided setup) but with an auto-generated sslip.io domain:
```
keycloak-k12lm4blpo13louovn3pfsgs.89.167.52.236.sslip.io
```

It had no proper domain, no HTTPS routing through Traefik, and was accessible on raw ports 8080, 8443, and 9000.

### Domain assignment

The `auth.scapegoat.dev` domain was assigned by modifying the Coolify service configuration:

**Files modified on server:**

1. `/data/coolify/services/k12lm4blpo13louovn3pfsgs/.env`:
   ```
   SERVICE_FQDN=auth.scapegoat.dev
   SERVICE_URL=https://auth.scapegoat.dev
   SERVICE_URL_KEYCLOAK_8080=https://auth.scapegoat.dev
   ```

2. `/data/coolify/services/k12lm4blpo13louovn3pfsgs/docker-compose.yml`:
   Added Traefik labels for HTTPS routing:
   ```yaml
   traefik.http.routers.keycloak-https:
     rule: Host(`auth.scapegoat.dev`)
     service: keycloak
     tls:
       certResolver: letsencrypt
   ```

After the change, Traefik automatically provisioned a Let's Encrypt certificate for `auth.scapegoat.dev`. HTTPS is enforced with a 307 redirect from HTTP.

### Network security

Keycloak's native ports (8080, 8443, 9000) are blocked from external access by `DOCKER-USER` iptables rules. The only path to Keycloak from the internet is through Traefik on ports 80/443:

```
Internet -> Traefik (443) -> auth.scapegoat.dev -> Keycloak container (8080)
```

The raw 8080 port is only accessible from the Docker network and from localhost on the server itself.

### Database

Keycloak uses a standalone PostgreSQL container managed by Coolify:
- Container: `go1o5tbegalwy3kesshq3hcp`
- Internal port: 5432
- Backed up every 6 hours via Coolify's built-in database backup scheduler
- Also included in the daily platform backup script at `/data/coolify/backups/platform-backup.sh`

## OIDC integration architecture

The OIDC integration design was formalized in docmgr ticket **MCP-003** (800-line architecture guide, 740-line investigation diary). The key design decisions:

### Dual-mode auth

The go-go-mcp framework supports two auth modes, switchable via CLI flag:

| Mode | Flag | Use case |
|------|------|----------|
| `external_oidc` | `--auth-mode external_oidc` | Production: validates bearer tokens against Keycloak JWKS |
| `embedded_dev` | `--auth-mode embedded_dev` | Development: built-in password login, self-issued tokens |
| `none` | `--auth-mode none` | No authentication (default for local development) |

### Token validation in `external_oidc` mode

The MCP server validates tokens locally without calling back to Keycloak:

1. **Discovery fetch**: `GET {issuer}/.well-known/openid-configuration` to find the JWKS URI
2. **JWKS fetch**: download the signing keys, cache them with configurable refresh interval
3. **JWT verification**: for each request bearing an `Authorization: Bearer <token>`:
   - Verify signature against cached JWKS keys
   - Check `iss` (issuer) matches configured issuer URL
   - Check `aud` (audience) if `--oidc-audience` is set
   - Check `exp` (expiry) and `nbf` (not-before)
   - Check required scopes if `--oidc-required-scope` is set

This means Keycloak can be briefly unavailable without breaking active MCP sessions — only new token acquisition requires Keycloak to be up.

### CLI flags for production deployment

```bash
smailnail-imap-mcp mcp start \
  --auth-mode external_oidc \
  --oidc-issuer-url https://auth.scapegoat.dev/realms/smailnail \
  --auth-resource-url https://smailnail.mcp.scapegoat.dev/mcp
  # Optional stricter enforcement:
  # --oidc-audience smailnail-mcp \
  # --oidc-required-scope mcp:invoke
```

Audience and scope enforcement are not yet enabled in production — they will be turned on once client configuration stabilizes.

## Token acquisition flows

### For AI agents (Claude, etc.)

Claude uses the standard OAuth authorization code flow:
1. User clicks "connect" in Claude
2. Claude redirects to `https://auth.scapegoat.dev/realms/smailnail/protocol/openid-connect/auth`
3. User logs in to Keycloak
4. Keycloak redirects back to Claude's callback URI with an authorization code
5. Claude exchanges the code for an access token
6. Claude sends MCP requests with `Authorization: Bearer <token>`

The `smailnail-mcp` client's redirect URIs include Claude's OAuth callback endpoints.

### For automated testing

The smoke scripts use the client credentials grant (no browser needed):
```bash
curl -s -X POST \
  "https://auth.scapegoat.dev/realms/smailnail/protocol/openid-connect/token" \
  -d "grant_type=client_credentials" \
  -d "client_id=smailnail-mcp-smoke" \
  -d "client_secret=$CLIENT_SECRET"
```

This returns a JWT access token that the Go smoke client uses for MCP requests.

### For OpenAI's MCP connector (broken)

OpenAI uses RFC 7591 dynamic client registration:
1. OpenAI discovers the MCP server's `/.well-known/oauth-protected-resource` metadata
2. OpenAI calls Keycloak's DCR endpoint to register itself as a new client
3. **This fails** because Keycloak's anonymous DCR policies reject the request

See "OpenAI DCR problem" below.

## OpenAI DCR problem

When OpenAI's MCP connector tries to connect to `https://smailnail.mcp.scapegoat.dev/mcp`, it attempts to dynamically register itself with Keycloak. This fails due to two Keycloak anonymous DCR policies:

### Trusted Hosts policy
Keycloak checks the registering client's source IP against a trusted-hosts list. OpenAI's requests come from rotating Azure IP addresses that cannot be pre-listed. The policy returns 403 for untrusted IPs.

### Allowed Client Scopes policy
OpenAI's DCR request includes scope claims that Keycloak's policy doesn't permit for anonymous registrations. Specifically, `openid` was missing from the allowed scopes set.

### Remediation options

Three options were documented in the SMAILNAIL-010 DCR debug guide (420 lines):

| Option | Approach | Trade-off |
|--------|----------|-----------|
| **A** | Temporarily disable both policies | Fast debugging, less secure |
| **B** | Keep anonymous DCR, configure properly | Add all required scopes to allowed list, widen trusted hosts |
| **C** | Pre-register OpenAI as a static client | Most secure, requires knowing OpenAI's redirect URIs in advance |

**Likely best path**: Option C (static client) avoids the security implications of anonymous DCR entirely, but requires knowing OpenAI's expected redirect URIs and client configuration. This is unresolved.

### What works despite this

The DCR problem is specific to OpenAI's connection model. Any client that can obtain a token through normal OAuth flows works fine:
- Claude: works via authorization code flow with the `smailnail-mcp` public client
- Smoke tests: work via client credentials grant with the `smailnail-mcp-smoke` confidential client
- Any custom MCP client: works by obtaining a token from Keycloak's token endpoint

## Keycloak administration

### Accessing the admin console

```bash
# Via browser
open https://auth.scapegoat.dev/admin/

# Credentials are in the Coolify service .env on the server
ssh root@89.167.52.236 'grep SERVICE_USER_ADMIN /data/coolify/services/k12lm4blpo13louovn3pfsgs/.env'
ssh root@89.167.52.236 'grep SERVICE_PASSWORD_ADMIN /data/coolify/services/k12lm4blpo13louovn3pfsgs/.env'
```

### Useful API calls

```bash
# OIDC discovery for smailnail realm
curl -s https://auth.scapegoat.dev/realms/smailnail/.well-known/openid-configuration | jq

# JWKS (signing keys used by MCP server for token validation)
curl -s https://auth.scapegoat.dev/realms/smailnail/protocol/openid-connect/certs | jq

# Master realm discovery (admin realm)
curl -s https://auth.scapegoat.dev/realms/master/.well-known/openid-configuration | jq

# Get admin token for API calls
ADMIN_TOKEN=$(curl -s -X POST \
  "https://auth.scapegoat.dev/realms/master/protocol/openid-connect/token" \
  -d "grant_type=password" \
  -d "client_id=admin-cli" \
  -d "username=<admin-user>" \
  -d "password=<admin-pass>" | jq -r .access_token)

# List clients in smailnail realm
curl -s -H "Authorization: Bearer $ADMIN_TOKEN" \
  "https://auth.scapegoat.dev/admin/realms/smailnail/clients" | jq '.[].clientId'

# Get smoke client secret
curl -s -H "Authorization: Bearer $ADMIN_TOKEN" \
  "https://auth.scapegoat.dev/admin/realms/smailnail/clients/<client-uuid>/client-secret" | jq -r .value
```

### Service configuration on server

Key files on the Hetzner server:

| Path | Purpose |
|------|---------|
| `/data/coolify/services/k12lm4blpo13louovn3pfsgs/.env` | Service environment (admin creds, FQDN, DB connection) |
| `/data/coolify/services/k12lm4blpo13louovn3pfsgs/docker-compose.yml` | Keycloak Docker Compose with Traefik labels |
| `/data/coolify/backups/platform-backup.sh` | Daily platform backup script (includes Keycloak config) |

### Local testing workflow

The local development Keycloak is the fastest way to iterate on realm/client configuration:

```bash
# Start local stack
docker compose -f docker-compose.local.yml up -d keycloak keycloak-postgres

# Wait for health check
docker compose -f docker-compose.local.yml ps

# Verify OIDC discovery
curl -sf http://127.0.0.1:18080/realms/smailnail-dev/.well-known/openid-configuration | jq .issuer

# Admin console
open http://127.0.0.1:18080/admin  # admin / admin
```

Changes tested locally can be applied to the production realm through the Keycloak admin console or API.

## Architecture

```text
Internet
  -> DNS: auth.scapegoat.dev -> 89.167.52.236
  -> Traefik v3.6 (port 443, Let's Encrypt TLS 1.3)
  -> Keycloak 26.1 container (port 8080, Docker network only)
     -> /realms/smailnail                          (smailnail realm)
     -> /realms/smailnail/.well-known/openid-configuration  (OIDC discovery)
     -> /realms/smailnail/protocol/openid-connect/certs     (JWKS)
     -> /realms/smailnail/protocol/openid-connect/token     (token endpoint)
     -> /realms/smailnail/protocol/openid-connect/auth      (authorization endpoint)
     -> /realms/smailnail/clients-registrations/openid-connect  (DCR, RFC 7591)
     -> /admin/                                    (admin console)
  -> PostgreSQL container (port 5432, Docker network only)
     -> keycloak database
     -> backed up every 6 hours

Token consumers:
  smailnail-imap-mcp (Coolify)
     -> fetches JWKS from /realms/smailnail/.../certs
     -> validates JWT bearer tokens locally (no introspection)
     -> checks: signature, issuer, expiry

  smailnaild (future)
     -> will use authorization code flow for browser sessions
     -> will call /realms/smailnail/.../token for code exchange

Local development:
  docker-compose.local.yml
     -> Keycloak 26.1 (port 18080, dev mode)
     -> PostgreSQL (port 5432)
     -> Realm: smailnail-dev (auto-imported from JSON)
```

## Docmgr tickets

| Ticket | Title | Location | Relevance |
|--------|-------|----------|-----------|
| COOLIFY-001 | Configure Coolify on Hetzner server | `/home/manuel/code/wesen/2026-03-15--install-coolify/ttmp/2026/03/15/COOLIFY-001--*` | Initial Keycloak deployment, domain assignment, TLS, firewall |
| MCP-003 | Keycloak external OIDC design | `/home/manuel/workspaces/2026-03-08/update-imap-mcp/go-go-mcp/ttmp/2026/03/09/MCP-003-KEYCLOAK-EXTERNAL-OIDC-DESIGN--*` | OIDC auth architecture, dual-mode design, JWT validation, local testing playbook |
| SMAILNAIL-010 | MCP Coolify deployment | `/home/manuel/workspaces/2026-03-08/update-imap-mcp/go-go-mcp/ttmp/2026/03/16/SMAILNAIL-010-MCP-COOLIFY-DEPLOYMENT--*` | Production realm creation, client configuration, DCR debugging |
| SMAILNAIL-011 | OIDC identity guide | `/home/manuel/workspaces/2026-03-08/update-imap-mcp/go-go-mcp/ttmp/2026/03/16/SMAILNAIL-011-OIDC-IDENTITY-CREDENTIALS-GUIDE--*` | Identity model: external OIDC principal -> local user -> stored IMAP credentials |
| SMAILNAIL-014 | Shared OIDC implementation | `/home/manuel/workspaces/2026-03-08/update-imap-mcp/go-go-mcp/ttmp/2026/03/16/SMAILNAIL-014-SHARED-OIDC-IMPLEMENTATION--*` | Schema v6 with users/identities/sessions tables, `ResolveOrProvisionUser` |

## Related projects

- [[PROJ - Coolify Hetzner - Self-Hosted Deployment Platform]] — the Hetzner server hosting Keycloak
- [[PROJ - Smailnail Coolify Deployment]] — the MCP server and Dovecot fixture that consume Keycloak tokens
- [[PROJ - Smailnail Hosted Backend and SPA]] — the future smailnaild web app that will use Keycloak for browser login

## Important project docs

- COOLIFY-001 diary (`reference/01-diary.md`) — Step 4 covers Keycloak domain assignment and TLS configuration
- MCP-003 design doc (`design-doc/01-*.md`, 800+ lines) — complete OIDC architecture guide with pseudocode
- MCP-003 playbook (`playbooks/01-local-keycloak-external-oidc-testing-playbook.md`) — step-by-step local testing
- MCP-003 smoke scripts (`scripts/local-keycloak-smoke.sh`) — automated OIDC validation
- SMAILNAIL-010 DCR debug guide (`reference/03-openai-keycloak-dcr-debug-guide.md`, 420 lines) — OpenAI DCR failure analysis
- SMAILNAIL-010 Keycloak scripts (`scripts/create_keycloak_realm_and_mcp_client.sh`, `create_keycloak_smoke_client.sh`) — realm and client provisioning

## Open questions

- **OpenAI DCR**: Should anonymous DCR policies be loosened or should OpenAI be pre-registered as a static client? (See remediation options above)
- **smailnaild browser login**: Should the web app use authorization code flow with PKCE via the `smailnail-web` client, or a different flow?
- **Realm consolidation**: The local `smailnail-dev` realm has different clients than the production `smailnail` realm. Should they converge, or is divergence acceptable for dev/prod?
- **User management**: No end users are registered in the production `smailnail` realm yet. Should users self-register, or should registration remain admin-only?
- **Audience enforcement**: `--oidc-audience` and `--oidc-required-scope` are not yet enabled on the production MCP server. When should they be turned on?
- **Keycloak upgrades**: How should Keycloak be upgraded on the Coolify server? Coolify manages the Docker image tag, but realm exports may be needed for safety.
- **Monitoring**: Should Keycloak have its own health monitoring (Uptime Kuma, etc.) given it's a dependency for all authenticated services?

## Near-term next steps

- Resolve the OpenAI DCR issue (most likely: pre-register a static client)
- Enable audience and scope enforcement on the production MCP server
- Wire smailnaild browser login through Keycloak (SMAILNAIL-014)
- Register first end users in the production smailnail realm
- Consider exporting the production realm configuration for backup and version control
- Evaluate whether Keycloak should be SSO for the Coolify dashboard itself

## Project working rule

> [!important]
> Keycloak realm and client changes should be tested locally first using `docker-compose.local.yml` before applying to production.
> Admin credentials for the production instance live on the server in the Coolify service `.env` — never commit them to a repository.
> The OIDC architecture design in MCP-003 is the authoritative reference for how token validation works — consult it before changing auth behavior.

## KB reviews

- [[KB-BATCH8-hosted-auth]] (2026-05-11) — concept extraction + classification
