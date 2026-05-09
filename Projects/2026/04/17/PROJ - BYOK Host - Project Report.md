---
title: BYOK Host Project Report
aliases:
  - BYOK Host Report
  - BYOK Broker Keycloak Project Report
  - BYOK Host - Concise Project Report
tags:
  - project
  - byok
  - keycloak
  - sqlite
  - oauth
  - oidc
  - broker
  - report
status: active
type: project
created: 2026-04-18
repo: /home/manuel/code/wesen/2026-04-17--byok-host
---

# BYOK Host Project Report

This is the short version of the BYOK Host project. If you want the detailed narrative, read the technical deep dive. If you want the current state and the important boundaries, read this note.

## What it is

BYOK Host is a local broker app for browser-facing BYOK inference. It keeps the broker as the place where consent, grants, provider-key custody, and broker-issued OAuth artifacts live.

Keycloak is only the broker login system.
SQLite is the first persistent broker storage backend.
The client site still delegates through the broker with Authorization Code + PKCE.

## Current state

Working now:
- Keycloak-backed broker login
- signed broker session cookie
- `return_to` routing after login
- broker-owned consent and grant flow
- persistent users, connections, grants, auth codes, access tokens, and audit events in SQLite
- in-memory and SQLite storage backends
- browser-validated end-to-end flow
- SQLite persistence survives broker restart

Still intentionally demo-level:
- fake upstream provider
- local secret storage in SQLite
- ticket-local workspace layout

## Architecture in one line

**Keycloak authenticates the user; the broker decides what the user’s stored provider connection may be used for.**

That separation is the whole point of the project.

## Important files

- `internal/auth/keycloak/oidc.go`
- `internal/app/broker.go`
- `internal/storage/interfaces.go`
- `internal/storage/sqlite/store.go`
- `deploy/docker-compose.yaml`
- `deploy/keycloak/realm-byok.json`
- `scripts/run_tmux_keycloak_demo.sh`

## Main limitations / next steps

- replace the fake provider with a real upstream integration
- harden secret handling
- decide whether the ticket-local layout should stay or be extracted
- keep the broker boundary intact as the project grows

## See also

- [[ARTICLE - Brokered BYOK with Keycloak and SQLite - A Technical Deep Dive]]
- [[PROJ - BYOK Host - Keycloak and SQLite Broker Intern Research Guide]]
