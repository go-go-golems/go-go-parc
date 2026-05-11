---
title: "Keycloak OAuth in Go Services — How We Do It"
aliases:
  - keycloak in go
  - keycloak oauth
  - go keycloak integration
tags: [knowledge-base, tribal, keycloak, oauth, go, authentication]
status: active
type: knowledge-base
created: 2026-05-11
---

# Keycloak OAuth in Go Services — How We Do It

> [!summary]
> How we wire Keycloak as an identity provider into Go backend services: the token validation flow, the JWKS endpoint dance, the cookie-vs-header decision, and the part that always surprises newcomers — Keycloak does authentication, but our services make authorization decisions independently.

## The pattern

Our Go services do not talk to Keycloak at runtime. This is the first thing to understand, because it contradicts what most Keycloak tutorials show. The tutorials demonstrate a service that calls Keycloak's introspection endpoint on every request — a network round-trip per request, a coupling to Keycloak's availability, and a bottleneck that defeats the point of using signed tokens.

Instead, our services validate JWTs locally using Keycloak's published signing keys. The flow:

1. **Keycloak issues a signed JWT** after the user authenticates (browser redirect, CLI callback, or API credential exchange).
2. **The client presents the JWT** to our Go service in an `Authorization: Bearer <token>` header or a signed cookie.
3. **The Go service validates the JWT** using the JWKS public keys fetched from Keycloak's `/protocol/openid-connect/certs` endpoint. Keys are cached and refreshed periodically — typically every 24 hours or on kid mismatch.
4. **The Go service extracts claims** (`sub`, `email`, `realm_access.roles`, `resource_access`) and makes its own authorization decision.

Keycloak is the *identity provider*. It proves who the user is. It does not decide what the user can do — that's our service's job. This separation matters because conflating the two is the source of our most common security bugs.

```go
// KeyValidator holds cached JWKS keys
type KeyValidator struct {
    jwks     *keyfunc.JWKS
    issuer   string
    audience string
}

func (v *KeyValidator) Validate(tokenStr string) (*jwt.Token, error) {
    // All validation happens locally — no network call to Keycloak
    token, err := jwt.Parse(tokenStr, v.jwks.KeyFunc)
    if err != nil {
        return nil, fmt.Errorf("token parse: %w", err)
    }

    // Verify issuer and audience match our Keycloak realm
    claims, ok := token.Claims.(jwt.MapClaims)
    if !ok {
        return nil, errors.New("invalid claims type")
    }
    if !claims.VerifyIssuer(v.issuer, true) {
        return nil, errors.New("invalid issuer")
    }
    if !claims.VerifyAudience(v.audience, true) {
        return nil, errors.New("invalid audience")
    }

    return token, nil
}
```

## Why we do it this way

**Local JWT validation eliminates the Keycloak dependency at request time.** If Keycloak goes down, existing tokens continue to work until they expire. New logins fail, but authenticated sessions are unaffected. This is the right tradeoff for our use case: we'd rather have degraded login than total service outage.

**Keycloak is the identity provider, not the policy engine.** Our services check `realm_access.roles` and `resource_access` claims for coarse authorization (is this user an admin?), but fine-grained permissions (can this agent push to this branch?) live in our own database. Mixing these into Keycloak roles creates a coupling that makes permissions hard to audit and impossible to test locally.

**Signed cookies over server-side sessions for browser clients.** A signed cookie (`user_id + expiry + HMAC`) avoids server-side session storage, which means no Redis, no session database, no sticky routing. The tradeoff: revocation requires a short cookie lifetime (15 minutes) plus a refresh token rotation. We accept this because our services are small enough that session infrastructure would dominate the codebase.

## Where it lives

| Repo | Path | Use |
|------|------|-----|
| `2026-04-17--byok-host` | `internal/auth/` | Keycloak token validation, cookie signing, PKCE flow |
| `2026-05-01--wish-git` | `internal/auth/` | Keycloak → broker token exchange, SSH cert issuance |
| `corporate-headquarters/pinocchio` | `internal/auth/` | API key validation with Keycloak user mapping |

### Related PARC project reports

- [[PROJ - BYOK Host - Project Report]] — broker-not-proxy architecture with Keycloak authn + broker authz
- [[PROJ - Wish Git - OAuth Scoped Git over SSH for Coding Agents]] — three-credential separation (Keycloak → broker → SSH cert)
- [[PROJ - Agent Enroll - Kanban Agent Credential MVP Deep Dive]] — Keycloak for human authn, app-native agent/run authz

Also see: [[Tribal/application-native-authorization]] — the pattern of Keycloak authenticating humans while the Go application owns downstream authorization for agents and runs.

## Common mistakes

1. **Calling the introspection endpoint on every request.** Keycloak's `openid-connect/token/introspect` validates a token by checking Keycloak's database. This is correct for revocation-sensitive flows, but it makes Keycloak a runtime dependency. Use local JWKS validation instead, and accept that revoked tokens survive until expiry.

2. **Forgetting `audience` validation.** A JWT issued for client `byok-host` should not be accepted by `wish-git`. Each service validates `aud` against its own client ID. Without this check, a token issued for one service is valid for all services in the realm — a subtle privilege escalation.

3. **Treating Keycloak roles as authorization decisions.** `realm_access.roles: ["admin"]` is useful for UI rendering (show the admin panel). It is not sufficient for data authorization (can this user delete this record?). Roles are identity claims; permissions are policy decisions. Our services map roles to permissions in their own logic.

4. **Not rotating JWKS keys.** Keycloak rotates signing keys on realm key rotation. If the `kid` in a JWT doesn't match any cached key, the validator must re-fetch JWKS. Hardcoding keys or never refreshing them causes validation failures after Keycloak rotates.

5. **PKCE from a CLI tool is non-obvious.** The Authorization Code flow requires a browser redirect and a localhost callback server. From a CLI, this means: start a localhost HTTP server on a random port, open the browser to Keycloak's auth URL with `redirect_uri=http://localhost:<port>/callback`, wait for the callback, exchange the code. The PKCE `code_verifier` and `code_challenge` prevent authorization code interception. We've implemented this twice (BYOK Host, Wish Git); each time it took longer than expected because the redirect wiring is tricky.

## Variations

- **API key flow**: For machine-to-machine communication, we use long-lived API keys instead of browser OAuth. The service validates the key against a database, then looks up the associated Keycloak user for audit purposes. No JWT involved.

- **Service account flow**: For backend services that call other backend services, we use Keycloak's client credentials grant. The calling service authenticates with its own client ID and secret, receives a token, and presents it to the target service. No human user involved.
