---
title: "OAuth 2.0 and OIDC — The Flows That Matter"
aliases:
  - oauth
  - oidc
  - authorization code
  - pkce
  - keycloak oauth flow
tags: [knowledge-base, on-ramp, oauth, oidc, security, authentication]
status: active
type: knowledge-base
created: 2026-05-11
---

# OAuth 2.0 and OIDC — The Flows That Matter

> [!summary]
> OAuth 2.0 lets a user grant a client limited access to their resources without sharing credentials. OIDC adds an identity layer on top. Of the many flows defined in the specs, we use exactly two: Authorization Code with PKCE (for browser and CLI clients) and Client Credentials (for service-to-service). This entry covers why those two, how they work, and what goes wrong when you pick the wrong one.

## The idea in one paragraph

OAuth solves the *delegation* problem: "I want this app to access my data on that service, but I don't want to give it my password." The user authenticates directly with the authorization server (Keycloak), the server issues a scoped token to the app, and the app uses that token to access the resource. The app never sees the user's password. The token is scoped (limited permissions) and short-lived (limited duration). This is the delegation model described in [[access-control-models]].

## The two flows we use

### Authorization Code with PKCE (browser + CLI)

This is the flow for any client that can open a browser. The client (our Go service or CLI tool) redirects the user to Keycloak's login page, the user authenticates, Keycloak redirects back with an authorization code, and the client exchanges the code for tokens.

```
1. Client → Browser:  Open https://keycloak/auth?redirect_uri=localhost:8080/callback&code_challenge=XYZ
2. User   → Keycloak:  Logs in with username/password
3. Keycloak → Client:  Redirect to localhost:8080/callback?code=ABC
4. Client → Keycloak:  POST /token with code=ABC & code_verifier=original_secret
5. Keycloak → Client:  { access_token, refresh_token, id_token }
```

PKCE (Proof Key for Code Exchange) prevents authorization code interception. The client generates a random `code_verifier`, hashes it to produce `code_challenge`, and sends the challenge in step 1. In step 4, the client sends the original `code_verifier`. Keycloak verifies the hash. An attacker who intercepts the code (step 3) cannot exchange it because they don't know the `code_verifier`.

From a CLI, this requires starting a localhost HTTP server on a random port to receive the callback. This is awkward but necessary — there is no secure way to do browser-based OAuth from a headless CLI without PKCE and a localhost redirect.

### Client Credentials (service-to-service)

This is the flow for a backend service that needs to call another backend service. No human user is involved. The service authenticates with its own `client_id` and `client_secret`, and receives a token scoped to its own permissions.

```
1. Service A → Keycloak:  POST /token with client_id=X & client_secret=Y & grant_type=client_credentials
2. Keycloak → Service A:  { access_token }
3. Service A → Service B:  Request with Authorization: Bearer <access_token>
4. Service B:  Validate token locally (JWKS), check scope
```

No browser redirect. No user. No PKCE. The token represents the service itself, not a user.

## The flows we do NOT use

- **Implicit flow**: Deprecated. The token is returned directly in the URL fragment, exposing it to browser history and referrer headers. Use Authorization Code with PKCE instead.

- **Resource Owner Password Credentials**: The client collects the user's username and password directly. This defeats the purpose of OAuth (the client sees the credentials). We only use this for migration scripts, never in production.

- **Device Authorization flow**: For devices with no browser (IoT, CLI on headless servers). The user visits a URL on their phone and enters a code. We haven't needed this yet, but it's the right choice for ESP32 devices that need to authenticate.

## The gotchas we've hit

**Token expiry vs refresh token rotation.** Access tokens expire (typically 5–15 minutes). Refresh tokens are long-lived but should be rotated — each use of a refresh token produces a new one, and the old one is invalidated. If a refresh token is used twice, it's been leaked, and the entire token family should be revoked. Keycloak supports this; configure it.

**Audience validation prevents cross-service token use.** A token issued for `byok-host` has `aud: ["byok-host"]`. If `wish-git` accepts this token, a user authenticated for one service can access another. Always validate `aud` (or `azp` for Keycloak) against your own client ID.

**State parameter prevents CSRF.** The `state` parameter in the authorization request is a random value that the client stores and verifies in the callback. Without it, an attacker can craft a callback URL that injects an authorization code linked to their own account, tricking the client into using the attacker's identity. Always use `state`.

## Where to go deeper

- **RFC 6749 (OAuth 2.0)** and **RFC 7636 (PKCE)** — The specs. Read them once; they're clearer than most tutorials.
- **RFC 6750 (Bearer Token Usage)** — How to present tokens in HTTP requests.
- [[Tribal/keycloak-oauth-in-go-services]] — Our implementation of these flows in Go.
- [[Fundamentals/access-control-models]] — The authn/authz/delegation model that explains *why* these flows exist.
- [[PROJ - BYOK Host - Project Report]] — Authorization Code + PKCE from both browser and CLI
- [[PROJ - Wish Git - OAuth Scoped Git over SSH for Coding Agents]] — OAuth flow feeding into SSH certificate delegation
