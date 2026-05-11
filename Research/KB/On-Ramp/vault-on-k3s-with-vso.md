---
title: "Vault on K3s with Vault Secrets Operator"
aliases:
  - vault k3s vso
  - vault secrets operator
  - vault on k3s
  - vso secret sync
tags: [knowledge-base, on-ramp, vault, k3s, kubernetes, secrets, gitops]
status: active
type: knowledge-base
created: 2026-05-11
---

# Vault on K3s with Vault Secrets Operator

> [!summary]
> Vault Secrets Operator (VSO) lets Kubernetes applications consume ordinary `Secret` objects while Vault remains the source of truth for secret values. HashiCorp docs explain the components, but our single-node GitOps pattern — Argo CD, Kubernetes auth, VaultConnection/VaultAuth/VaultStaticSecret, and “intent in Git, values in Vault” — is the practical shape that makes the system readable.

## The idea in one paragraph

VSO is a bridge. Vault stores the secret values. Git stores the sync intent. Kubernetes workloads consume native `Secret` objects. The operator watches custom resources, authenticates to Vault, reads the configured paths, and writes standard `Secret` objects into the cluster.

## Why we care

Our K3s platform uses this as the standard secret-delivery story:
- [[PROJ - Vault on K3s - Auth and Secret Delivery Platform]]
- [[PROJ - CoinVault on K3s - First Real GitOps App]]

This matters because it removes the old `.envrc` / copied-credential / host-specific drift pattern. Apps no longer need their own secret story.

## The three objects to understand

The practical VSO model is easier if you think in three objects:

1. **VaultConnection** — where Vault lives
2. **VaultAuth** — how the operator authenticates
3. **VaultStaticSecret** — what Vault path to read and which Kubernetes `Secret` to write

That is the real operator-facing mental model.

## Why Kubernetes auth matters

In our setup, workloads do not get long-lived Vault tokens. Instead:
- Kubernetes provides a ServiceAccount identity,
- Vault validates it,
- Vault maps it to a role and policy,
- the operator reads only the allowed secret paths.

This keeps machine identity scoped to namespace + role instead of shared tokens floating around the cluster.

## The GitOps split

The key rule is:

- **secret intent in Git**
- **secret values in Vault**

A manifest in Git can safely say “sync `kv/coinvault/prod` into `coinvault-secrets`.” It must not contain the actual password. This split is the difference between a real platform pattern and a convenient leak.

## The gotchas we've hit

**VSO is eventual, not synchronous.** Updating Vault does not instantly update the pod's live environment. There is a sync cycle.

**In-cluster auth is easier to debug than ingress first.** For early smoke tests, it is often better to authenticate to Vault through the in-cluster service rather than involving DNS, TLS, and ingress all at once.

**Human auth and machine auth are different systems.** OIDC for operators and Kubernetes auth for workloads should stay separate even if they terminate in the same Vault instance.

**A successful login is not the real success criterion.** The real test is: does identity map to the correct bounded policy and secret subtree?

## The default use case

The most common path is not “every app talks to Vault.” The most common path is:
- app gets a normal Kubernetes `Secret`,
- VSO keeps it synchronized from Vault,
- app stays ignorant of Vault's API.

That is the highest-leverage adoption path because it fits ordinary Kubernetes app expectations.

## Where to go deeper

- [[PROJ - Vault on K3s - Auth and Secret Delivery Platform]] — architecture, policies, roles, smoke tests
- [[PROJ - CoinVault on K3s - First Real GitOps App]] — first real workload using the pattern
- [[Tribal/host-mediated-secret-delivery]] — the broader architectural pattern this fits into
