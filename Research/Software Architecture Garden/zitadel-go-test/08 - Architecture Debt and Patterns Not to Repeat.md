---
title: zitadel-go-test — Architecture Debt and Patterns Not to Repeat
aliases: [TODO ZITADEL architecture debt]
tags: [architecture-garden, zitadel-go-test, architecture-debt, oidc, gitops, postgresql]
status: active
type: architecture-pattern-study
pattern_maturity: architecture-debt
created: 2026-07-26
analyzed: 2026-07-26
repository: /home/manuel/code/wesen/2026-07-25--zitadel-go-test
repository_url: https://github.com/wesen/2026-07-25--zitadel-go-test
repository_commit: 6b64c4c2974349760e52016f153c807c44be54dc
vault_base_commit: dbb76bf21c6d3293629a36603be9feee88ac8b5b
related_files:
  - cmd/todo-demo/serve.go
  - infra/zitadel/local/terraform.tfstate
  - infra/zitadel/local/terraform.tfstate.backup
  - /home/manuel/code/wesen/2026-03-27--hetzner-k3s/gitops/applications/todo-tenant-alpha.yaml
  - /home/manuel/code/wesen/2026-03-27--hetzner-k3s/gitops/projects/prod-apps.yaml
  - /home/manuel/code/wesen/2026-03-27--hetzner-k3s/gitops/kustomize/todo-tenant/base/db-bootstrap-script-configmap.yaml
---

# Architecture Debt and Patterns Not to Repeat

A Garden entry should not convert every existing choice into a recommendation. This project contains provisional decisions, local artifacts, and defaults that failed under production acceptance. Naming them prevents future projects from copying them merely because they exist in a working repository.

> [!summary]
> - Do not store a full OIDC token context in a browser cookie; encryption does not solve size limits.
> - Do not infer isolation from database ownership, namespace separation, or policy text without direct denial tests.
> - Do not call a top-level Argo manifest GitOps-managed until a reconciler owns its creation and updates.

## Oversized stateless OIDC session

`authentication.WithCookieSession` serializes and encrypts the complete OIDC context, including tokens and UserInfo. Real ZITADEL tokens and organization claims produce a cookie larger than the practical browser limit. The server returns a successful callback and `Set-Cookie`; the browser silently declines to retain the cookie. The next protected request has no application session.

Encryption protects confidentiality and integrity. It does not reduce payload size enough to make the representation valid.

The replacement should be:

```text
browser cookie: encrypted random session identifier
PostgreSQL row: serialized OIDC context, expiry, revocation metadata
```

This keeps token material server-side, supports restart persistence, permits revocation, and keeps the cookie small. In-memory sessions are not a production substitute because pod restart and multi-replica routing would invalidate them.

## Local Terraform state in the application repository

`infra/zitadel/local/terraform.tfstate` and its backup are present in the source tree. Local development state can contain identifiers or sensitive values and should not be treated as a reusable project pattern. Production tenant state correctly uses an encrypted remote backend with a distinct key.

Future scaffolding should ignore local state by default and provide examples without checked-in operational state.

## Ambient PostgreSQL privileges

Database ownership did not imply connection isolation. New databases inherited `CONNECT` for `PUBLIC`. A role from another tenant could open a session to the peer database until bootstrap explicitly revoked that grant.

Do not repeat this sequence:

```text
create database owned by tenant
assume ownership means only owner can connect
```

Instead, define database ACL as part of creation and test it with the peer credential.

## Git presence without reconciliation ownership

New Application files under `gitops/applications` did not automatically appear in Argo CD. They needed explicit bootstrap. AppProject changes also needed explicit application in the current operational model.

Manual bootstrap is not necessarily wrong, but an undocumented bootstrap edge creates false confidence. A future ecosystem guideline should require each top-level object to identify one owner:

- parent/root Argo Application;
- cluster bootstrap command or pipeline;
- another declarative controller.

## Partial Kustomize renaming of custom resources

`namePrefix` transformed native Kubernetes references but did not understand every VSO custom-resource reference. This would have produced objects whose `vaultConnectionRef` or service-account reference named a resource that did not exist.

Do not assume Kustomize understands arbitrary CRD semantics. Either:

1. avoid unnecessary renaming inside isolated namespaces;
2. define and test explicit name-reference configuration; or
3. patch every custom reference and verify rendered output.

The tenant overlays chose the first option.

## Instance administrator as an acceptance operator

The instance administrator can create users and grants in every organization. That makes it useful for bootstrap, but it cannot prove customer-administrator isolation. A real acceptance must use organization-scoped administrators and show that cross-organization and instance operations are denied.

Synthetic users with verified placeholder addresses can test OIDC mechanics. They cannot replace invitation, email verification, factor establishment, and scoped administrator handoff.

## Configuration concentration

`serve.go` is still readable, but it combines settings schema, validation, database startup, billing construction, OIDC configuration, middleware, route declarations, and server lifecycle. This is emergent composition-root pressure.

The response should not be a generic application framework. Extract only when a coherent boundary appears—for example, a reusable PostgreSQL OIDC session adapter or a route constructor with direct tests.

## Sensitive debugging output

A diagnostic returned a full `Set-Cookie` header while only cookie attributes were needed. The cookie was encrypted, but it remained a bearer credential and had to be invalidated through key rotation.

The rule is precise: parse and redact every cookie value before a tool can emit output. Better, return only booleans and attribute names. Sanitization must happen inside the diagnostic, not after output exists.

## Deferred concerns

The following are risks or incomplete acceptance, not proven architecture failures:

- Vault Kubernetes roles currently omit explicit audiences, matching existing cluster practice but leaving a hardening opportunity.
- Administrator bootstrap awaits approved external email addresses.
- SMTP invalid, expired, and replayed challenge behavior remains incompletely tested.
- Live Stripe rollout remains blocked by legal, Tax, key, catalog, and webhook decisions.

Keeping these distinctions prevents the Garden from presenting open questions as historical incidents.
