---
title: "Host-Mediated Secret Delivery — How We Do It"
aliases:
  - host-mediated secrets
  - secret delivery
  - vault secret delivery
  - mediated credential delivery
tags: [knowledge-base, tribal, secrets, vault, security, infrastructure, agents]
status: active
type: knowledge-base
created: "2026-05-11"
---

# Host-Mediated Secret Delivery — How We Do It

> [!summary]
> Secrets are never copied to the consumer. The host fetches secrets from the authority at runtime and delivers bounded, policy-gated values to the consumer. The consumer never talks to the secret authority directly. We use this pattern across five projects spanning three domains: VM isolation (Firecracker), credential brokering (BYOK Host), and infrastructure secrets (Vault on K3s, Glazed Vault, Terraform Vault).

## The pattern

Our secret-delivery systems follow a strict three-party architecture:

```
Authority (Vault, Keycloak)  →  Host (mediator)  →  Consumer (app, VM, agent)
   stores secret values          fetches + gates         receives bounded secret
```

The key invariants:

1. **The authority is the single source of truth for secret values.** Vault stores the actual secret material. Keycloak stores the authentication state. Nothing else stores long-lived secrets.

2. **The host mediates all delivery.** The host (Vault Secrets Operator, Glazed source middleware, Terraform provider, Firecracker host, BYOK broker) decides what the consumer receives. The host enforces policy, applies scope, sets expiry, and logs access.

3. **The consumer receives only what it needs, only when it needs it.** A Kubernetes pod gets a native `Secret` object. A Firecracker VM gets a host-injected credential. A Glazed command gets a hydrated `TypeSecret` field value. A BYOK agent gets a broker-issued token. In every case, the consumer's trust boundary is narrow and explicit.

4. **Secret intent is declarative; secret values are dynamic.** The deployment manifest says "this app needs the database password from Vault path `kv/coinvault`." Vault stores the actual password. At runtime, the host fetches the password and delivers it. The manifest (intent) is in Git; the password (value) is in Vault.

## Why we do it this way

**Copying secrets creates drift and leakage.** The old state of the world had secrets in `.envrc` files, copied into CI variables, pasted into Coolify environment fields, and sometimes checked into Git by accident. Every copy was a drift risk and a leakage risk. The host-mediated pattern eliminates copies: there is one authority, and every consumer gets a fresh delivery.

**The consumer shouldn't need to know about Vault.** A Kubernetes pod shouldn't need the Vault client library. A Go CLI shouldn't need to implement token refresh. A Firecracker VM shouldn't need network access to Vault. The host absorbs the complexity of talking to the authority; the consumer receives a simple, native-format secret.

**Policy is enforced at the delivery point, not the storage point.** Vault policies define what a token *can* read. But the host adds an extra enforcement layer: the Kubernetes auth mount maps a ServiceAccount to a Vault role with bounded secret paths. The Glazed Vault middleware only hydrates `TypeSecret` fields. The BYOK broker only issues tokens for connections the user has explicitly granted. This defense in depth means a compromised consumer can only access the secrets the host chose to deliver.

**Rotation happens at the authority, not at every consumer.** When a database password rotates, you update Vault. The next delivery picks up the new value. Consumers don't need to be updated, restarted, or redeployed. This is the operational payoff of host-mediated delivery: one change point instead of N.

Alternatives we considered:
- **Direct Vault API from every consumer.** Every app needs the Vault client library, token management, and lease renewal. High coupling. Every app is a new attack surface for Vault.
- **Static secrets in environment variables.** Works for small deployments. Degrades with scale: no rotation, no audit, no scoping, no revocation. The `.envrc` drift pattern.
- **Platform-managed secrets (Coolify, Kubernetes native).** Adequate for simple cases. No cross-platform consistency. No unified audit trail. When you migrate off Coolify, the secrets story breaks.

## Where it lives

| Repo | Path | Use |
|------|------|-----|
| `2026-03-31--firecracker-vm` | `internal/vm/`, `internal/agent/` | Host injects secrets into Firecracker VM via host-mediated channel |
| `2026-04-17--byok-host` | `internal/auth/`, `internal/app/broker.go` | Broker mediates credential delivery between Keycloak and provider connections |
| `2026-03-27--hetzner-k3s` | `vault/policies/`, `vault/roles/`, `gitops/applications/vault-secrets-operator*.yaml` | VSO delivers Vault secrets as native K8s Secret objects |
| `add-vault-middleware-to-glazed/glazed` | `pkg/cmds/sources/vault.go` | Glazed source middleware hydrates TypeSecret fields from Vault |
| `terraform` (wesen) | `vault/` module | Terraform provisions Vault, AppRole, policies for machine auth |

### Related PARC project reports

- [[PROJ - Firecracker VM - Guest Bring-Up, Host-Mediated Secrets, and Isolation Design]] — VM isolation: host injects secrets, VM never talks to Vault
- [[PROJ - BYOK Host - Project Report]] — credential brokering: broker issues tokens for stored provider connections
- [[PROJ - Vault on K3s - Auth and Secret Delivery Platform]] — VSO delivers K8s Secrets from Vault
- [[PROJ - Glazed Secret Redaction and Vault Bootstrap - Technical Project Report]] — Glazed Vault middleware: TypeSecret-only hydration, bootstrap parsing
- [[PROJ - Terraform Infra - Vault Platform Bring-Up, Auth Hardening, and Hair-Booking Handoff]] — Vault provisioning, AppRole, Keycloak OIDC

## Common mistakes

1. **Giving the consumer direct Vault access.** If the app has `VAULT_TOKEN` and talks to Vault directly, you've lost host-mediated delivery. The app now has unbounded access (limited only by its token's policy), and you've coupled the app to Vault's API. The fix: use VSO (Kubernetes), source middleware (Glazed), or host injection (Firecracker). The consumer should receive a native-format secret, not a Vault token.

2. **Putting secret values in Git.** Even encrypted. Even in "private" repositories. Secret intent (the path, the key name) belongs in Git. Secret values belong in Vault. If you catch yourself committing `VAULT_TOKEN` or `DATABASE_PASSWORD` to a deployment manifest, stop. The host should fetch these at runtime.

3. **Forgetting that VSO sync is eventual, not immediate.** When you update a secret in Vault, VSO detects the change and writes a new Kubernetes `Secret`. But there's a delay. If your pod starts before VSO syncs, it sees the old value. This matters for rotation scenarios: after rotating a password in Vault, you need to wait for VSO sync before restarting the consumer. Or use `VaultDynamicSecret` for immediate rotation.

4. **Using the same Vault token across services.** Each service (Kubernetes namespace, Glazed CLI invocation, Terraform run) should get its own token with its own policy. A shared token means one compromised service can read all secrets. The K3s platform uses Kubernetes auth (ServiceAccount-scoped), the Glazed middleware uses the operator's Vault token with `TypeSecret`-only hydration, and Terraform uses AppRole. Different tokens, different scopes, different failure boundaries.

5. **Not redacting secret values in debug output.** The Glazed Vault work was triggered by the discovery that `--print-parsed-fields` and `ToSerializableFieldValue` leaked raw secret values. If your framework has debug or serialization paths, ensure they go through a central redaction function. One missed path is one leaked credential.

6. **Bootstrap parsing precedence inversions.** The Glazed Vault middleware needs Vault connection settings (address, token, path) before it can hydrate application secrets. If you put Vault settings in the same source chain as application settings, you get a chicken-and-egg problem. The fix is bootstrap parsing: a mini-parse of just the `vault-settings` section, then the full parse with Vault inserted as a source middleware. If you skip this, Vault settings might not be available when the middleware tries to connect.

7. **Not testing negative policy enforcement.** It's easy to test that a valid token can read the right secrets. It's harder to test that an invalid token, or a token with the wrong policy, *cannot* read secrets. But that's the test that matters most. The Terraform Vault work includes a Go example that proves both positive and negative policy behavior. Without negative tests, a policy misconfiguration ships silently.

## Variations

- **Vault Secrets Operator** (Vault on K3s, CoinVault). The host is a Kubernetes operator. It watches `VaultStaticSecret` CRDs, fetches values from Vault using Kubernetes auth, and writes native Kubernetes `Secret` objects. Apps consume ordinary K8s secrets. The most production-ready variation.

- **Glazed source middleware** (Glazed Vault). The host is a Glazed source middleware layer. It hydrates `TypeSecret` fields from Vault using the operator's Vault token. Only declared-sensitive fields are eligible. The same `defaults → config → vault → env → args → cobra` precedence chain applies. The most framework-integrated variation.

- **Host injection into VM** (Firecracker). The host creates a Firecracker VM and injects secrets through a host-mediated channel (serial, file, or network). The VM receives secrets at boot time and never talks to Vault. The most isolated variation — the VM has no network access to the authority.

- **Credential brokering** (BYOK Host). The host is a Go broker that validates the user's Keycloak token, then issues its own scoped token for a specific stored provider connection. The agent receives a broker token, not a Keycloak token. The most agent-oriented variation. See [[Tribal/application-native-authorization]] for the full credential chain.
