---
title: "Hair Booking ZITADEL Cutover: A Production Identity Migration"
aliases:
  - Hair Booking ZITADEL Migration
  - Hair Booking Authentication Cutover
  - ZITADEL Provider Broker Cutover
tags:
  - article
  - identity
  - oidc
  - oauth
  - zitadel
  - passkeys
  - kubernetes
status: active
type: article
created: 2026-08-02
repo: /home/manuel/code/wesen/2026-03-27--hetzner-k3s
---

# Hair Booking ZITADEL Cutover: A Production Identity Migration

Hair Booking moved from a dedicated Keycloak realm to a dedicated ZITADEL organization while keeping the application dependent on one OpenID Connect issuer. The migration did not copy users. It established a new identity population with Google, Apple, Facebook, password, and passkey login, then proved that the production application could create and restore its own client records from those identities.

> [!summary]
> - Hair Booking delegates provider-specific authentication to a dedicated ZITADEL organization; the application implements one authorization-code OIDC client with S256 PKCE.
> - Provider callbacks and application callbacks are different contracts. External providers return to ZITADEL at `/idps/callback`; ZITADEL returns to Hair Booking at `/auth/callback`; logout returns to `/auth/logout/callback`.
> - Production acceptance verified Facebook provisioning and re-login, password and passkey enrollment/re-login, PKCE, application logout, and denial of stylist routes to an ordinary client. Positive stylist authorization remains a separately authorized test.

## Why this migration exists

A consumer-facing booking application needs several ways to authenticate, but it should not implement Google, Apple, Facebook, password, passkey, account linking, verification, and session policy as separate application protocols. Those systems have different provider consoles, callback requirements, credential lifetimes, browser interactions, and security obligations. The application should instead depend on a single OIDC contract and let an identity broker own the provider-specific work.

The target architecture isolates Hair Booking in organization `384403604791886029` under the shared ZITADEL deployment. The organization owns its login policy, registered identity providers, and user population. Hair Booking trusts ZITADEL as issuer `https://zitadel.yolo.scapegoat.dev`; it does not trust Facebook, Apple, or Google tokens directly. This division is significant because it keeps application token validation, session issuance, and client persistence stable while provider policy changes remain in the identity layer.

The original cutover was deliberately destructive for Hair Booking only. There was no meaningful user population to migrate. Shared Keycloak infrastructure was not removed or altered because it remains an independent dependency for other applications.

## The architecture and its contracts

The migration has three callback layers. Each layer has one owner and one exact URI. Treating them as interchangeable produces redirect failures that can be difficult to diagnose because all three use HTTPS and occur in the same browser session.

```mermaid
sequenceDiagram
    participant B as Browser
    participant H as Hair Booking
    participant Z as ZITADEL organization
    participant P as Google / Apple / Facebook
    participant V as Vault + VSO

    V->>H: Runtime OIDC issuer, client ID, scopes, session settings
    B->>H: GET /auth/login
    H->>Z: Authorization Code request + S256 PKCE
    Z->>P: External-provider authorization request
    P->>Z: https://zitadel.yolo.scapegoat.dev/idps/callback
    Z->>H: https://hair-booking.yolo.scapegoat.dev/auth/callback
    H->>H: Validate code/tokens; map subject to client; set HTTP-only session
    H-->>B: Authenticated application session
```

| Contract | URI | Owner | Purpose |
|---|---|---|---|
| External-provider callback | `https://zitadel.yolo.scapegoat.dev/idps/callback` | Google, Apple, Facebook configuration | Returns provider authorization to ZITADEL. |
| Application authorization callback | `https://hair-booking.yolo.scapegoat.dev/auth/callback` | ZITADEL OIDC application | Returns the OIDC code to Hair Booking. |
| Application logout callback | `https://hair-booking.yolo.scapegoat.dev/auth/logout/callback` | ZITADEL OIDC application | Returns the browser after the ZITADEL logout flow. |

The application uses authorization code flow with `code_challenge_method=S256`. PKCE binds the authorization request to the browser that generated it. The deployed OIDC client does not require a long-lived client secret for this flow. Hair Booking validates the response, creates an HTTP-only application session, and exposes the authenticated identity through `/api/me`.

The runtime configuration is delivered without committing secret material. Vault path `kv/apps/hair-booking/prod/runtime` is synchronized by a `VaultStaticSecret` at `gitops/kustomize/hair-booking/runtime-secret.yaml`. The Deployment reads the generated Kubernetes Secret as `HAIR_BOOKING_OIDC_*` and `HAIR_BOOKING_STYLIST_ALLOWED_*` environment variables. Provider credentials live separately at `kv/apps/hair-booking/prod/zitadel-idp` and are used by the Terraform identity configuration.

## The implementation journey

The work began by establishing repository ownership. GitOps manifests and Vault delivery belong in `/home/manuel/code/wesen/2026-03-27--hetzner-k3s`; the ZITADEL tenant lives in the sibling `/home/manuel/code/wesen/terraform` repository; application protocol and session behavior live in `/home/manuel/code/wesen/hair-booking`. The ticket [[HK3S-0043]] records this boundary and the detailed diary.

The dedicated organization, project, and OIDC client were declared under `terraform/zitadel/hair-booking/envs/prod`. Google and Apple use ZITADEL provider resources appropriate to their protocols. Facebook remains a generic OAuth provider. That is a correctness decision: giving Facebook an OIDC-shaped configuration merely to obtain a UI icon would misstate the actual protocol integration.

Hair Booking was changed to generate S256 PKCE requests. The change was validated in unit tests and in the live authorization request. The production app was deployed from immutable images through GitOps rather than patched in place. This matters because a correct identity plan does not compensate for an unhealthy workload.

The rollout exposed two deployment failures that were independent of authentication. First, the private GHCR image reader could not pull the new immutable image. A dedicated `read:packages` token was stored only in the Hair Booking image-pull Vault path, then VSO refreshed the Kubernetes secret. Second, the new image started but SQLite failed with `go-sqlite3 requires cgo to work`. The root Dockerfile had built with `CGO_ENABLED=0`. Setting `CGO_ENABLED=1`, rebuilding, and deploying `ghcr.io/wesen/hair-booking:sha-dd691ce` restored the service. The incident also produced a reusable Infra Tooling preflight rule that rejects CGO-disabled Glazed builds where SQLite capability is required.

## The callback incident

The most instructive live failure was a mismatch between what had been registered in provider consoles and what ZITADEL Login V2 actually emitted. Initial provider registrations included the historical path `/oauth/v2/callback`. Browser initiation showed that Login V2 sent Google, Apple, and Facebook to `/idps/callback` instead. Google initially rejected the request; adding the exact URI corrected the flow. Apple required a Website URLs configuration for the Services ID, and Facebook required the same URI in its strict Valid OAuth Redirect URIs list.

The same pattern occurred at logout, but with the application callback rather than an external-provider callback. Hair Booking sent the browser to ZITADEL’s end-session endpoint with post-logout redirect `https://hair-booking.yolo.scapegoat.dev/auth/logout/callback`. ZITADEL rejected it as `post_logout_redirect_uri invalid` because Terraform allowed only the site root. The repair added the explicit callback to `post_logout_redirect_uris` in `zitadel_application_v2.hair_booking_web`.

A full Terraform plan also proposed unrelated `zitadel_login_texts` drift. The repair did not apply that drift. Instead, it used a resource-targeted plan that changed exactly the OIDC application allowlist. The browser then reached the normal ZITADEL logout account-selection screen, and `/api/me` returned `not-authenticated` after confirmation.

```text
if full_plan contains unrelated_drift:
    inspect the intended OIDC delta
    create targeted plan for the OIDC application only
    apply the reviewed plan
    verify browser logout and /api/me unauthenticated state
else:
    apply reviewed full plan
```

This is not a general endorsement of Terraform targeting. It was a recovery mechanism for an urgent, isolated redirect allowlist correction. The outstanding login-text drift must be investigated before a future unrestricted apply.

## What production acceptance proved

The acceptance suite used browser navigation and application API responses, not configuration inspection alone. A configuration can look correct while provider callbacks, browser storage, token exchange, or application persistence fail at runtime.

### External providers and client continuity

Google, Apple, and Facebook all appeared on the organization-scoped ZITADEL login page. Google reached its account chooser. Apple reached `appleid.apple.com` with the ZITADEL `/idps/callback` redirect. Facebook reached its OAuth page with `code_challenge_method=S256`.

A real Facebook login created the Hair Booking client for `manuel@bl0rg.net`. `/api/me` showed the ZITADEL issuer, a stable ZITADEL subject, and a persisted client ID. After logout and operator-confirmed Facebook re-login, the same client record was restored rather than duplicated. This demonstrates the identity mapping rule: the application treats the `(issuer, subject)` pair as the durable authentication identity and updates the existing client session.

### Password and passkey flows

The registration page exposes Password and Passkey as distinct ZITADEL-native choices. A passkey account was enrolled through the browser’s WebAuthn ceremony. Cookies were cleared, the account email was entered again, and ZITADEL presented `Authenticate with a passkey`; operator approval restored the original Hair Booking client.

A password account was then registered. Cookie-only clearing was not accepted as sufficient proof because ZITADEL could restore the session without displaying the password page. The stricter test cleared cookies, local storage, session storage, and IndexedDB for both ZITADEL and Hair Booking, completed a ZITADEL logout, and retried the login. ZITADEL then displayed the explicit `/ui/v2/login/password` page. After password entry, `/api/me` returned the original client ID with an advanced update timestamp.

The rule is straightforward: a clean-client authentication test must remove all state that can satisfy the login outside the credential being tested. Browser cookies alone are not the whole state boundary.

### Stylist authorization

Authentication does not imply stylist access. Hair Booking’s current authorizer in `pkg/stylist/authorizer.go` checks an allowlist of normalized emails and subjects delivered from Vault. The ordinary Facebook client was deliberately not in that allowlist. An authenticated request to `/api/stylist/dashboard` returned HTTP 403 with `not-stylist`.

The positive stylist path remains intentionally unperformed. Granting the password test user production stylist access simply to make the test pass would modify real authorization policy. A safe completion requires a designated least-privilege stylist test identity and explicit approval.

## Branding is a separate concern

The Terraform configuration applies organization label policy and login text resources, and the Fringe logo was copied into the tenant Terraform assets. In the tested ZITADEL Login V2 deployment, however, the visible hosted pages continued to show default/TODO branding in some states, including logout. The configuration state and the rendered hosted UI therefore diverge.

This is not a callback or application-session defect. The options are to upgrade to a ZITADEL/Login V2 version that supports the required branding behavior, adopt a supported custom or self-hosted login UI, or accept the hosted default temporarily. Changing provider callbacks or inventing unsupported Terraform fields would not repair visible branding.

## Operator procedure

When changing this system, follow the order below. It prevents the common failure where a platform update is declared complete before the browser has exercised the real contract.

1. Update the dedicated ZITADEL Terraform environment and keep provider credentials in Vault.
2. Run Terraform validation and inspect the full plan. Isolate unrelated drift before applying a narrow recovery change.
3. Update provider-console redirect registrations to the exact ZITADEL external callback.
4. Deploy application changes as immutable GitOps images; do not mutate the live Deployment.
5. Verify health, Argo convergence, and the live authorization request’s issuer, organization scope, and PKCE method.
6. Use a fresh browser state for every credential type and prove client continuity with `/api/me`.
7. Test logout separately from login. It has a distinct OIDC allowlist.
8. Test both ordinary-client denial and approved-stylist access before replacing the existing authorization model.

## Evidence and reproducibility

The principal evidence is in [[HK3S-0043]]:

- `ttmp/2026/08/01/HK3S-0043--add-google-apple-facebook-password-and-passkey-login-to-hair-booking-with-zitadel/reference/01-investigation-diary.md`
- `ttmp/2026/08/01/HK3S-0043--add-google-apple-facebook-password-and-passkey-login-to-hair-booking-with-zitadel/design-doc/01-hair-booking-zitadel-identity-architecture-and-implementation-guide.md`
- `ttmp/2026/08/01/HK3S-0043--add-google-apple-facebook-password-and-passkey-login-to-hair-booking-with-zitadel/scripts/minitrace/`

The specified Pi session (`019fbe80-9da6-7241-849f-f9b51aca2f31`) was converted with go-minitrace for this report. Its sanitized session profile recorded 891 turns, 887 tool calls, 191 reads, 59 modifications, 26 creates, and 224 executes between 2026-08-01T18:05:27Z and 2026-08-02T00:17:56Z. The ticket preserves a source list and SQL query, but intentionally ignores converted archives and raw results because historical command text can contain sensitive values. Repository commits and production/API observations, rather than raw transcript command output, are the durable evidence for this report.

Key commits include Terraform branding `e4b31b1`, application PKCE `42a1108`, application CGO repair `dd691ce`, Infra Tooling guard `9fe8530`, Terraform logout callback `3acc6fe`, Hair Booking operator runbook `ff37f70`, and ticket evidence through `68633dc`.

## What remains

The identity migration is operational for the tested flows, but two deliberate follow-ups remain:

- Complete positive stylist authorization with an explicitly approved test identity, or migrate authorization to ZITADEL project-role claims and update Hair Booking to consume those claims.
- Decide whether hosted Login V2 branding is acceptable or whether an upgrade/custom login UI is required.

The old Hair Booking Keycloak resources should not be removed until the positive stylist authorization path is verified and the authorization ownership decision is explicit. The cutover preserved that discipline: identity migration changed the authentication boundary without silently changing production authorization policy.

## Related notes

- [[HK3S-0043]]
- [[PLAYBOOK - Onboarding a Source Repository to the GitOps Image Pipeline]]
