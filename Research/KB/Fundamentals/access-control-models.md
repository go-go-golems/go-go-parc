---
title: "Access Control Models: Authentication, Authorization, and Delegation"
aliases:
  - auth model
  - authn authz
  - delegation
  - scoped credentials
tags: [knowledge-base, fundamental, security, access-control, authentication, authorization, delegation]
status: active
type: knowledge-base
created: 2026-05-11
---

# Access Control Models: Authentication, Authorization, and Delegation

> [!summary]
The three-part security model that underpins our Keycloak integrations, BYOK broker, Wish Git, and every system where an agent acts on behalf of a human. Authentication proves who you are. Authorization decides what you can do. Delegation gives someone else limited authority to act as you. Getting these confused causes our most common security architecture mistakes.

## The core idea

**Authentication (AuthN)**: Proving identity. "I am Manuel." Done via passwords, OAuth flows, SSH keys, certificates. The output is an identity assertion (a token, a session, a certificate).

**Authorization (AuthZ)**: Deciding permissions. "Manuel can push to this repo." Done via access control lists, role-based access control (RBAC), attribute-based access control (ABAC), or policy engines. The output is an allow/deny decision.

**Delegation**: Granting limited authority. "This agent may act as Manuel, but only for repo X, only for 30 minutes, only to push to branch Y." Done via scoped OAuth tokens, short-lived SSH certificates, or broker-issued grants. The output is a constrained credential.

These are three separate concerns. Conflating them — "if you're logged in, you can do everything" — is the most common security mistake in our projects.

## Why it matters to our work

Three of our KB entries depend on this model:

- **Tribal: Keycloak OAuth in Go Services** — We use Keycloak for authn and our own broker for authz. The separation is deliberate and non-obvious.
- **On-Ramp: OAuth 2.0 and OIDC** — OAuth is a delegation protocol. Understanding the three-part model is prerequisite to understanding why PKCE exists and what a scope means.
- **On-Ramp: OpenSSH Certificates** — SSH certificates encode authorization as `principals` and `force-command`. This is delegation via certificate extensions.

Our most common architecture mistake: using the same credential for all three. An API key that both identifies the user AND grants full access is an authn+authz conflation. A long-lived SSH key that never expires is an authz-without-delegation failure. A BYOK system where the agent receives the human's refresh token is a delegation-without-scoping failure.

## The key result

**The Principle of Least Privilege (Saltzer & Schroeder, 1975)**: Every program and every user should operate using the least set of privileges necessary to complete the job.

In the authn/authz/delegation model, this means:

1. **Authenticate to the narrowest identity** — A user authenticates once, but receives credentials scoped to the specific task.
2. **Authorize to the narrowest scope** — The system checks permissions against the specific action, not against a broad role.
3. **Delegate with the shortest lifetime** — The agent's credential expires as soon as the task is complete.

This is not just a security principle — it's an operational one. When an agent's SSH certificate expires in 5 minutes, a leaked key is harmless after 5 minutes. When an OAuth scope is `repo:push:branch:feature-123`, a compromised token can't access other repos.

## The intuition behind the key result

Think of delegation like a hotel key card. The front desk (Keycloak) verifies your identity (authn). The key card system (broker) decides which doors you can open (authz). The key card itself is the delegation — it's temporary, it's scoped to your room, and it stops working at checkout.

If the hotel gave you a master key (full admin access), any lost key compromises every room. If the key never expired, a stolen key works forever. If the key opened every door, there's no point having doors.

Our Wish Git project applies this exactly: Keycloak is the front desk, the `agent_run` table is the key card system, and the SSH certificate is the key card — scoped to one repo, one branch set, expiring in minutes.

## What goes wrong when you don't know this

1. **BYOK Host: giving agents the human's refresh token** — The tempting shortcut: "the agent needs to call the LLM API, so give it the user's API key." This is delegation without scoping. If the agent leaks the key, it has the user's full power. BYOK Host deliberately separates: Keycloak authenticates the user, the broker stores the API key, and the broker issues short-lived access tokens to the browser. The browser never sees the API key directly.

2. **Wish Git: using `authorized_keys` instead of certificates** — If you add the agent's public key to `~/.ssh/authorized_keys`, it has the same access as any human with a key on that file. No scoping, no expiry, no audit trail tied to a specific run. SSH certificates fix all three: the `principals` field scopes access, the certificate `valid_before` field sets expiry, and the certificate serial number links back to the `agent_runs` table.

3. **Any project: conflating "logged in" with "authorized"** — "The user has a valid session cookie, so they can do anything" is authn without authz. This works for personal tools. It fails the moment you have multiple permission levels (admin vs user, reader vs writer, human vs agent).

## Where we use it

- [[Tribal/keycloak-oauth-in-go-services]]
- [[Tribal/application-native-authorization]]
- [[On-Ramp/oauth-2-oidc-flows]]
- [[On-Ramp/openssh-certificates]]

### Related PARC project reports

- [[PROJ - BYOK Host - Project Report]] — delegation-without-scoping failure: giving agents human refresh tokens
- [[PROJ - Wish Git - OAuth Scoped Git over SSH for Coding Agents]] — authz-without-delegation failure: authorized_keys instead of certificates
- [[PROJ - Agent Enroll - Kanban Agent Credential MVP Deep Dive]] — three-layer credential narrowing: human → agent → run

## Where to go deeper

1. **Saltzer, J. H. & Schroeder, M. D. (1975)**. "The Protection of Information in Computer Systems." *Communications of the ACM*, 17(7). — The original least-privilege paper.
2. **RFC 6749 (OAuth 2.0)** — The authorization framework; section 1 defines the four roles (resource owner, client, authorization server, resource server) that map to our authn/authz/delegation model.
3. **Wish Git project report** in this PARC library — A worked example of the full authn→authz→delegation pipeline using Keycloak, SSH certificates, and Git hooks.
