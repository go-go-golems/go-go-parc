---
title: "OpenSSH User Certificates"
aliases:
  - ssh certificates
  - openssh certificates
  - ssh cert signing
  - ssh ca
tags: [knowledge-base, on-ramp, ssh, certificates, security, delegation]
status: active
type: knowledge-base
created: 2026-05-11
---

# OpenSSH User Certificates

> [!summary]
> OpenSSH user certificates let a Certificate Authority (CA) sign a public key, embedding identity, permissions, and expiry into the certificate itself. The SSH server validates the certificate against the CA's public key — no `authorized_keys` management, no key distribution, no manual revocation lists. We use them for scoped, short-lived agent access in Wish Git. This entry covers what they are, how they differ from `authorized_keys`, and the specific fields we use for delegation.

## The idea in one paragraph

An SSH certificate is a public key signed by a CA. The signature embeds metadata: who the key represents (`principals`), what it can do (`force-command`, `permit-*` extensions), and when it expires (`valid-before`). The SSH server trusts the CA (configured with `TrustedUserCAKeys` in `sshd_config`), so it accepts any certificate the CA signs without needing the key in `authorized_keys`. This is the difference between "I trust this specific key" and "I trust any key this CA vouches for."

## Why certificates, not authorized_keys

The `authorized_keys` file lists public keys that are allowed to log in. It works for humans: you generate a keypair once, copy the public key to the server, and you're done. It breaks for agents:

- **No scoping.** A key in `authorized_keys` has the same access as the user who owns the file. There's no way to say "this key can only push to branch `feature-123`." You'd need a separate Unix user per scope, which is unmanageable.

- **No expiry.** A key in `authorized_keys` works forever. If an agent's key is leaked, it's valid until someone manually removes it from the file.

- **No audit trail.** When a key authenticates, the SSH log shows "Accepted publickey for user manuel" — but which key? You have to correlate the key fingerprint manually.

Certificates solve all three:

```
ssh-keygen -s /path/to/ca_key \
    -I "agent-run-42" \          # Key comment / serial (audit trail)
    -n "repo:myproject" \        # Principals (scope)
    -V "+5m" \                   # Valid for 5 minutes (expiry)
    -O "force-command=/usr/local/bin/forge-hook" \  # Restrict command
    agent_key.pub
```

The `-n` principals, `-V` validity, and `-O` options are embedded in the certificate. The SSH server enforces them. The agent can't modify them (they're in the CA's signature).

## The fields we use

| Field | Flag | What it does | How we use it |
|-------|------|-------------|---------------|
| Key identity | `-I` | Comment/serial for logging | The `agent_run` UUID from our database |
| Principals | `-n` | Required identity for matching | The repository path the agent can access |
| Valid after | `-V start:end` | Certificate validity window | Start = now, End = now + 5 minutes |
| Force command | `-O force-command=...` | Restrict session to one command | `git-receive-pack` or `git-upload-pack` only |
| No-pty | `-O no-pty` | Disable interactive terminal | Always set for agent certificates |
| No-port-forwarding | `-O no-port-forwarding` | Disable port forwarding | Always set for agent certificates |

## The server-side configuration

```sshd_config
# Trust the CA — any certificate it signs is accepted
TrustedUserCAKeys /etc/ssh/ca.pub

# Map certificate principals to Unix users
# A certificate with principal "repo:myproject" maps to user "git"
AuthorizedPrincipalsFile /etc/ssh/principals/%u

# Log the certificate identity (the -I field) for audit
# (appears in auth.log as "Certificate ID: agent-run-42")
```

The `AuthorizedPrincipalsFile` maps principals to system users. A file at `/etc/ssh/principals/git` containing `repo:myproject` means: a certificate with principal `repo:myproject` can authenticate as user `git`. This is how we map certificate scope to filesystem permissions.

## The gotchas we've hit

**`-V` format is picky.** `+5m` means "5 minutes from now." `+5d` means "5 days." But `+5h30m` is invalid — use `+330m` instead. The format is documented in `sshd_config(5)` under `TIME FORMATS`.

**Principals must match exactly.** If the certificate has `-n "repo:myproject"` and the principals file has `repo:myproject`, it matches. If the certificate has `-n "myproject"` (missing the `repo:` prefix), it doesn't. This is a common typo when generating certificates programmatically.

**Certificate expiry is checked at session start, not continuously.** If a certificate expires during an active SSH session, the session continues. Expiry only prevents *new* connections. For agents, this means: if a long-running `git push` takes more than 5 minutes (the certificate lifetime), the push still completes. The certificate only gates session establishment.

**The CA private key must be protected.** Anyone with the CA private key can sign certificates for any principal. In Wish Git, the CA key is generated at server startup and held in memory only — never written to disk. This means the CA key doesn't survive a server restart, and all issued certificates become invalid. Agents re-authenticate through the browser flow to get new certificates.

## Where to go deeper

- **`ssh-keygen(1)`** — The certificate signing command and all options.
- **`sshd_config(5)`** — `TrustedUserCAKeys`, `AuthorizedPrincipalsFile`, and certificate-related options.
- **Wish Git project report** in this PARC library — A worked example of the full certificate issuance and enforcement pipeline.
- [[PROJ - Wish Git - OAuth Scoped Git over SSH for Coding Agents]] — the full three-layer enforcement architecture
- [[Fundamentals/access-control-models]] — The delegation model that explains *why* certificates are a scoped delegation mechanism.
