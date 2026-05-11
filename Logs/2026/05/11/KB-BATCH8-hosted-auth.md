---
title: "KB Playbook Batch 8: Hosted Auth / Keycloak Identity (5 Projects)"
doc-type: reference
topics: parc, knowledge-base, auth, keycloak, oidc, hosted-apps
owners: manuel
created: "2026-05-11"
---

# KB Playbook Batch 8: Hosted Auth / Keycloak Identity

## Projects analyzed

1. Smailnail OIDC Identity and Hosted Auth
2. go-go-mcp Hosted OIDC and Smailnail Delivery
3. Hair Booking — MVP Buildout, Hosted Auth, Vault, and Production Fixes
4. Smailnail Hosted Identity, Terraform, and Claude Fix
5. Keycloak Identity Platform on Coolify

---

## Candidates pushed to 3/3

### Separate human auth from machine auth (3/3 → READY)

| Project | Human auth | Machine auth |
|---------|------------|-------------|
| Vault on K3s | Keycloak OIDC for operators | Kubernetes auth for workloads |
| Terraform Vault | Keycloak OIDC for humans | AppRole for machines |
| Smailnail / go-go-mcp / Hair Booking | browser OIDC session login | bearer-token MCP client / smoke client / service accounts |

**Core insight**: humans and machines should not share one auth shape. Browser/session login, operator login, bearer-token clients, AppRole, and Kubernetes auth have different trust boundaries and different failure modes.

### What this batch reinforced

- Keycloak is repeatedly used as the human-facing identity provider.
- Machine-facing access is repeatedly separated into a different flow: confidential clients, bearer resource-server auth, AppRole, or Kubernetes auth.
- The local application identity key `(issuer, subject)` is the app-facing normalization boundary after provider auth succeeds.

---

## New / strengthened candidates

| Concept | Seen in | Status |
|---------|---------|--------|
| `(issuer, subject)` as stable local user key | Smailnail OIDC, go-go-mcp hosted OIDC, Smailnail hosted identity | covered by [[Tribal/keycloak-oauth-in-go-services]] |
| Dynamic client registration policy as production auth boundary | Keycloak platform, Smailnail hosted identity, go-go-mcp hosted OIDC | covered by [[Tribal/keycloak-oauth-in-go-services]] + [[On-Ramp/oauth-2-oidc-flows]] |
| Dedicated Keycloak realm per app | Hair Booking, Smailnail, Keycloak platform | covered by [[Tribal/keycloak-oauth-in-go-services]] |
| OIDC logout must clear provider session, not only app session | Smailnail OIDC, Hair Booking | 2/3 |

---

## Key patterns extracted

### Smailnail OIDC Identity and Hosted Auth
- shared local identity key is `(issuer, subject)`
- browser app and MCP route trust the same Keycloak realm
- hosted server serves SPA + auth routes + API + MCP from one binary

### go-go-mcp Hosted OIDC and Smailnail Delivery
- embeddable MCP server must be mountable into an existing app mux
- verified auth principal must flow through request context into tool execution
- resource server behavior (challenge, metadata, validation) is distinct from browser-client behavior

### Hair Booking
- separate Keycloak realm per app prevents auth drift from other products
- SES and Vault integration show that auth and secret delivery are adjacent but distinct concerns
- hosted auth becomes part of product runtime, not an afterthought

### Smailnail Hosted Identity, Terraform, and Claude Fix
- anonymous DCR policy can be the real production blocker, not the application server
- the first healthy MCP request is often a 401 challenge + protected-resource metadata follow-up
- Terraform no-op drift baseline matters before production auth changes

### Keycloak Identity Platform on Coolify
- Keycloak acts as central identity provider for multiple services
- local dev realm and production realm can diverge in useful ways, but only if the divergence is understood
- dynamic client registration is not just a spec feature — it is an operator policy surface

---

## Playbook feedback (Batch 8)

1. **Hosted auth is its own domain.** The project reports repeatedly describe the same structural concerns: issuer choice, bearer challenge shape, browser vs machine clients, local user normalization, and realm ownership. This is now clearly a KB cluster.

2. **A single provider can support multiple auth shapes without collapsing them.** Keycloak shows up as the human-facing issuer, but the machine side still varies appropriately (Kubernetes auth, AppRole, service-account clients, bearer resource server).

3. **Production auth bugs are often policy bugs.** The Claude/OpenAI client-registration issue is a good reminder that the real boundary can be Keycloak policy, not the app server.
