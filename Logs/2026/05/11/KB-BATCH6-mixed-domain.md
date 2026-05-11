---
title: "KB Playbook Batch 6: Mixed Domain (6 Projects)"
doc-type: reference
topics: parc, knowledge-base, goja, e2ee, remarquee, capsule, geppetto
owners: manuel
created: "2026-05-11"
---

# KB Playbook Batch 6: Mixed Domain

Strategic batch targeting remaining 2/3 candidates across domains.

## Projects analyzed

1. Capsule Lab — A Sandboxed JS Capsule Runtime in the Browser (24 KB)
2. Geppetto — Open Responses and Chat Boundary Cutover (21 KB)
3. Goja REPL Hardening (14 KB)
4. Remarquee — reMarkable Toolkit (6 KB)
5. E2E Encrypted Storage Prototype (14 KB)
6. AUTODISCO — Keyhive Access Control Architecture (33 KB)

---

## Candidates pushed to 3/3

### Data-only vs host-access module split (3/3 → READY)

| Project | How it contributes |
|---------|-------------------|
| Node-like Primitives | Default-enabled data-only modules (crypto, path, timer) vs opt-in host modules (fs, os, exec) |
| Capsule Lab | Permission-locked API surface — capsules declare permissions, kernel enforces, host mediates. Same trust model: safe defaults, opt-in capabilities |
| *(implicit: goja-embedding itself)* | The goja-embedding entry documents "permission-locked API surface" and "host-mediated side effects" as core elements |

**Core insight**: Embedded JS runtimes should default to data-only operations (no side effects possible) and require explicit opt-in for host-access modules (filesystem, network, display). The host installs only the API functions the sandbox has declared permissions for.

### Reduction-ladder debugging (3/3 → READY)

| Project | How it contributes |
|---------|-------------------|
| PaperS3 WAMR | Reduction ladder from full run → load-only → empty-module → binary_freeable → reuse_const_strings=false |
| Cardputer Web Serial | smoke.html: strip everything except port-open + line-dump + one manual frame |
| Geppetto Together thinking | Shrink from full Geppetto stack → direct curl → isolate delta.reasoning vs delta.reasoning_content → identify go-openai struct loss |

**Core insight**: When debugging a complex integration, shrink the problem until the smallest toxic step is obvious. Don't debug at the level of the full stack; debug at the level of the minimal reproduction.

---

## Other candidates updated

### IIFE cell rewrite (now 3/3 → READY)

Goja REPL Hardening explicitly documents the IIFE rewrite as a core session mechanism and fixes edge cases around it. With the REPL API (Batch 3) and Goja REPL Hardening, this is now at 3/3 (REPL API, Goja REPL Hardening, and implicit in goja-execution-model).

### Envelope encryption for selective sharing (2/3)

E2E Encrypted Storage and AUTODISCO Keyhive both use envelope encryption: per-document symmetric keys wrapped per-user with asymmetric keys. Different implementations (Web Crypto API vs Keyhive WASM), same pattern.

### CRDT-local authorization (2/3)

AUTODISCO Keyhive and (potentially) the AUTODISCO Automerge architecture add authorization on top of CRDT documents. Key insight: CRDTs solve collaboration; they don't solve authorization. You need a separate access-control layer.

---

## Key patterns extracted

### Capsule Lab

- **Op-stream response pattern** — goja kernel dispatches, returns ops array, host processes ops, calls back with results
- **Permission declarations before execution** — capsule declares permissions, kernel enforces at API level
- **Real-time bridge log** — every op crossing the boundary is logged, making the boundary debuggable

### Geppetto

- **Own the normalization boundary** — don't trust third-party SDK struct models for provider-specific deltas
- **Provider-aware reasoning delta normalization** — `delta.reasoning` (OpenAI) vs `delta.reasoning_content` (Together/Qwen)
- **Chat boundary cutover** — replace library structs with app-owned types while keeping library for non-critical paths (embeddings, transcription)

### Goja REPL Hardening

- **Deleted sessions must not appear in normal reads** — soft-delete with visibility filtering
- **Durable session IDs must not depend on process-local counters** — use UUID or database-generated IDs
- **SQLite integrity settings on connection open** — `PRAGMA foreign_keys = ON` for pooled connections
- **Evaluation timeouts must cover both async and sync runaway code** — deadline-based, not just promise-timeout

### Remarquee

- **OAuth refresh with bounded retry** — transient failures don't escalate to auth re-login
- **V6 scene tree parser** — stroke colors, highlights, anchors for rmdoc rendering
- **Markdown-to-PDF-to-reMarkable pipeline** — pandoc + xelatex → PDF → rmapi upload

### E2E Encrypted Storage

- **Per-transcript symmetric key wrapped per-user** — envelope encryption for selective sharing
- **Web Crypto API without external libraries** — RSA-OAEP 2048 key generation, AES-GCM encryption
- **Server stores only ciphertext** — all encryption/decryption in browser

### AUTODISCO Keyhive

- **Mock ACL for product flow, real Keyhive for experiments** — staged implementation
- **Durable Keyhive snapshots across server restarts** — archive + signer + prekey persistence
- **Invitation as membership event ingestion** — contact cards → invite create → accept → ACL update
- **tryEncrypt WASM binding bug** — ownership issue in Rust→WASM boundary (borrow vs consume)

---

## New tribal candidates

| Concept | Seen in | Status |
|---------|---------|--------|
| Envelope encryption for selective sharing | E2E Storage, AUTODISCO Keyhive | 2/3 |
| CRDT-local authorization layer | AUTODISCO Keyhive, (future CRDT projects) | 2/3 |
| Own the normalization boundary | Geppetto, (future provider integrations) | 1/3 |
| Provider-aware reasoning delta normalization | Geppetto | 1/3 |
| Op-stream response pattern | Capsule Lab | 1/3 (also in goja-embedding) |
| OAuth refresh with bounded retry | Remarquee, Smailnail OIDC | 2/3 |
| Per-transcript key architecture | E2E Storage | 1/3 |
| WASM binding ownership bugs | AUTODISCO Keyhive (tryEncrypt), (future WASM projects) | 1/3 |
| Durable snapshot for WASM state | AUTODISCO Keyhive | 1/3 |

---

## Playbook feedback (Batch 6)

1. **The reduction-ladder debugging pattern keeps appearing.** Three projects in different domains (embedded WAMR, browser serial, API streaming) all used the same debugging approach: shrink until the smallest toxic step is obvious. This is now at 3/3 and should be a tribal entry.

2. **Large reports (33 KB) still slow things down.** The Keyhive report took as long as the other 5 combined. I extracted useful patterns but couldn't read every detail. For future batches, I should cap at 20 KB.

3. **Capsule Lab validates the goja-embedding entry perfectly.** The op-stream pattern, permission-locked API, and host-mediated side effects are exactly what goja-embedding documents. This project is a textbook instance.
