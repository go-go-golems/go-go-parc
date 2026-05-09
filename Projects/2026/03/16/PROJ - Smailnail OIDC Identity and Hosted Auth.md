---
title: Smailnail OIDC Identity and Hosted Auth
aliases:
  - Smailnail OIDC Identity
  - Smailnail Hosted Auth
  - Project Smailnail OIDC Identity and Hosted Auth
tags:
  - project
  - smailnail
  - oidc
  - keycloak
  - authentication
  - mcp
  - hosted-app
  - coolify
  - github-sso
status: active
type: project
created: 2026-03-16
repo: /home/manuel/workspaces/2026-03-08/update-imap-mcp/smailnail
branch: task/update-imap-mcp
issuer: https://auth.scapegoat.dev/realms/smailnail
app-url: https://smailnail.mcp.scapegoat.dev
mcp-url: https://smailnail.mcp.scapegoat.dev/mcp
ticket-shared-identity: SMAILNAIL-014
ticket-merged-host: SMAILNAIL-015
---

# Smailnail OIDC Identity and Hosted Auth

This note consolidates the recent OIDC and hosted-auth work across the two most important recent `smailnail` tickets:

- **SMAILNAIL-014**: shared OIDC identity across `smailnaild` and `smailnail-mcp`
- **SMAILNAIL-015**: merge the hosted web app and the hosted MCP into one server and deploy it

It is the shortest useful “where are we now?” document for the hosted auth model.

## Related notes

- [[PROJ - Smailnail Coolify Deployment]]
- [[PROJ - Keycloak Identity Platform on Coolify]]

> [!summary]
> `smailnail` now has one hosted server at `https://smailnail.mcp.scapegoat.dev` that serves:
> - the SPA
> - browser login/logout and session-backed API auth
> - the MCP HTTP endpoint at `/mcp`
> - OAuth protected-resource metadata at `/.well-known/oauth-protected-resource`
>
> Both the browser app and the MCP route trust the same Keycloak realm:
> - issuer: `https://auth.scapegoat.dev/realms/smailnail`
>
> The local application identity model is now shared across both surfaces and keyed by:
> - `(issuer, subject)`
>
> The current main operational limitation is not auth anymore. It is persistence:
> - the hosted app DB is still container-local SQLite, so redeploys wipe saved IMAP accounts.

## Why this work mattered

Originally, the hosted shape was split:

- `smailnaild` handled the SPA and browser-oriented API work
- `smailnail-imap-mcp` handled the MCP HTTP surface
- each side needed the same Keycloak issuer, the same encryption key material, and the same user/account state

That created drift risk and made the product harder to reason about. The two tickets fixed that in two stages:

1. establish one shared identity model across browser auth and bearer-token auth
2. serve both app and MCP from the same hosted binary and deployment

## The identity model

The most important design decision is that the app does **not** key users by:

- email
- GitHub username
- Keycloak username
- OAuth client id

Instead, the stable local identity key is:

- `issuer`
- `subject`

That means the app remains provider-neutral. Keycloak is the current OIDC issuer, but the local user model is not Keycloak-specific.

### What this means in practice

Browser login through `smailnaild`:

```text
browser
  -> /auth/login
  -> Keycloak authorization endpoint
  -> /auth/callback
  -> resolve/provision local user by (issuer, sub)
  -> create web session
```

MCP bearer auth:

```text
MCP client
  -> bearer token from same Keycloak realm
  -> /mcp
  -> validate JWT against issuer + JWKS
  -> resolve/provision local user by (issuer, sub)
  -> allow MCP code to use that user’s stored IMAP accounts
```

So the browser and MCP stories are finally using the same application identity.

## What was implemented in SMAILNAIL-014

The shared-identity ticket added the missing application identity layer.

### Core data model

New app-level identity/session tables were introduced for:

- `users`
- `user_external_identities`
- `web_sessions`

That established a local user record separate from raw Keycloak claims.

### Hosted web auth

`smailnaild` gained real OIDC browser login support:

- `/auth/login`
- `/auth/callback`
- `/auth/logout`
- `/api/me`

The previous `local-user` stub was replaced by session-backed resolution.

### MCP-side identity usage

The MCP route already validated OIDC tokens through `go-go-mcp`, but `smailnail` was not actually using that identity to reach user-owned data. That gap was closed so the MCP side can resolve stored IMAP accounts for the same local user model.

### Local validation

The work was validated locally against:

- local Keycloak
- local Dovecot
- shared app DB

This proved that a browser-authenticated user and a bearer-authenticated MCP request can both act on the same saved account state.

## What was implemented in SMAILNAIL-015

The merge/deployment ticket turned the architecture into a real hosted system.

### One hosted server

The production host now runs one `smailnaild` process that serves:

- `/`
- `/auth/*`
- `/api/*`
- `/mcp`
- `/.well-known/oauth-protected-resource`

This is important: one server does **not** mean one auth mechanism.

The route split is still deliberate:

- browser session auth for the SPA and `/api/*`
- bearer-token OIDC auth for `/mcp`
- public metadata for `/.well-known/oauth-protected-resource`

### Hosted deployment

The merged host is live at:

- app root: `https://smailnail.mcp.scapegoat.dev`
- MCP: `https://smailnail.mcp.scapegoat.dev/mcp`
- Keycloak issuer: `https://auth.scapegoat.dev/realms/smailnail`

This replaced the earlier split deployment shape where the MCP server was hosted separately.

### Hosted validation that already passed

The merged host has been validated for:

- browser login through Keycloak
- `/api/me`
- saving an IMAP account
- mailbox listing
- message preview
- unauthenticated `/mcp` returning `401`
- authenticated MCP execution against a stored `accountId`

### Account-test hardening

There was an intermittent hosted failure on:

- `POST /api/accounts/{id}/test`

with:

- `use of closed network connection`

This was hardened by retrying one transient read-only probe failure in the account service. After redeploy, repeated hosted account-test calls succeeded.

### Logout improvement

Another important auth improvement was made afterward:

- app logout no longer only deletes the local `smailnail_session`
- it now redirects through the OIDC `end_session_endpoint`

This matters because the old logout left the Keycloak session alive, which made it look like the app “ignored” logout and logged users back in immediately.

The current behavior is now:

- clear app session
- redirect through Keycloak logout
- return to the app root

This improves provider-choice behavior on the next sign-in.

## Current production auth shape

### Browser app

`smailnaild` is an OIDC web client of the Keycloak realm.

Important values:

- issuer: `https://auth.scapegoat.dev/realms/smailnail`
- hosted auth entry: `https://smailnail.mcp.scapegoat.dev/auth/login`
- callback: `https://smailnail.mcp.scapegoat.dev/auth/callback`

### MCP route

The MCP route is an OIDC-protected resource, not a browser client.

Important values:

- resource URL: `https://smailnail.mcp.scapegoat.dev/mcp`
- metadata URL: `https://smailnail.mcp.scapegoat.dev/.well-known/oauth-protected-resource`

### Keycloak realm

Current production realm:

- `smailnail`

Currently relevant clients:

- `smailnail-web`
- `smailnail-mcp`
- `smailnail-mcp-test`

`smailnail-mcp-test` exists mainly to make direct bearer-token smoke tests easy. It is not the long-term product surface.

## GitHub SSO: what it should mean

GitHub SSO should be added as an **upstream** identity provider inside Keycloak, not as a direct auth integration inside `smailnaild`.

That means:

```text
browser
  -> smailnaild /auth/login
  -> Keycloak login page
  -> GitHub button
  -> GitHub OAuth
  -> Keycloak brokered identity
  -> smailnaild /auth/callback
```

The app still trusts the same Keycloak issuer. GitHub just becomes one login method behind that issuer.

### Key callback URL

If GitHub OAuth app setup is done in GitHub, the callback URL should be:

- `https://auth.scapegoat.dev/realms/smailnail/broker/github/endpoint`

### Correct GitHub scope

For the GitHub identity provider in Keycloak, the useful initial scope is:

- `read:user user:email`

not `read:email`.

## Provider choice, auto-login, and the confusing logout behavior

There are three sessions in play:

1. `smailnaild` app session
2. Keycloak session
3. GitHub browser session

So “I logged out of the app and got logged back in” can happen if:

- the app session was cleared
- but the Keycloak session still existed

And even after Keycloak logout, GitHub itself may still have a live session in the browser, so a GitHub login can still appear “automatic”.

### Default IdP redirector

If Keycloak has an **Identity Provider Redirector** configured in the browser flow with:

- `Default Identity Provider = github`

then users will not see the normal Keycloak login page at all. They will be sent straight to GitHub.

That is only desirable if the product explicitly wants to force GitHub.

If the product should let users choose:

- do **not** configure a default IdP redirector to `github`
- keep the Keycloak login page visible

### Desired UX shape

The correct future UX is probably:

- `Sign in` -> normal Keycloak login page, no forced provider
- `Sign in with GitHub` -> same auth flow, but with `kc_idp_hint=github`

That gives both:

- a chooser-based default path
- an explicit GitHub shortcut

## Biggest remaining issue

The main remaining ops problem is persistence.

Today the merged host is still using container-local SQLite:

- `/app/smailnaild.sqlite`

That means redeploying the app wipes:

- saved IMAP accounts
- account test history
- other hosted app state

So before real-user rollout, the next important infrastructure step is:

- persistent volume for SQLite, or
- Postgres via the Clay SQL path

This matters more than any remaining OIDC logic gap.

## Most relevant source materials

docmgr tickets:

- `SMAILNAIL-014-SHARED-OIDC-IMPLEMENTATION`
- `SMAILNAIL-015-MERGED-HOSTED-SERVER-DEPLOYMENT`

Especially useful:

- `SMAILNAIL-015` playbook:
  - hosted validation
  - GitHub SSO setup checklist

Code areas:

- `pkg/smailnaild/auth/oidc.go`
- `pkg/smailnaild/user.go`
- `pkg/smailnaild/identity/*`
- `pkg/smailnaild/accounts/service.go`
- `pkg/mcp/imapjs/server.go`
- `pkg/smailnaild/http.go`

Related project notes:

- [[PROJ - Smailnail Coolify Deployment]]
- [[PROJ - Keycloak Identity Platform on Coolify]]
- [[PROJ - Smailnail Hosted Backend and SPA]]

## Short takeaway

The hard part is done.

`smailnail` now has:

- one hosted server
- one shared OIDC identity model
- one Keycloak issuer for browser auth and MCP auth
- working hosted account storage and MCP execution against that account

The next work is mostly operational and UX:

- persist the app DB
- enable GitHub as a Keycloak broker cleanly
- decide whether login defaults to chooser or GitHub-first
