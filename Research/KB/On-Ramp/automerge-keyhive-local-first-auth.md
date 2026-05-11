---
title: "Automerge + Keyhive for Local-First Authorization"
aliases:
  - keyhive local-first auth
  - automerge keyhive
  - crdt access control
  - local-first authorization
tags: [knowledge-base, on-ramp, automerge, keyhive, crdt, local-first, auth]
status: active
type: knowledge-base
created: 2026-05-11
---

# Automerge + Keyhive for Local-First Authorization

> [!summary]
> CRDTs solve collaboration, not authorization. A local-first app can replicate documents offline and merge concurrent edits, but it still needs identity, invitations, delegation, revocation, and eventually encryption. Keyhive is one approach to layering those concerns onto a CRDT-based application. Public material here is sparse; this entry is mainly orientation for reading our AUTODISCO work.

## The idea in one paragraph

Automerge gives you local-first replicated documents. Keyhive gives you a model for identities, groups, invitations, delegation, and document-level access. The combination is: Automerge handles *state convergence* while Keyhive handles *who should be allowed to participate*.

## Why we care

[[PROJ - AUTODISCO - Keyhive Access Control Architecture]] starts from a working Automerge chat system and adds a real access-control layer. The important lesson is simple:

> collaboration and authorization are separate problems.

Automerge solved the first one. Keyhive is the experimental answer to the second.

## The mental model

The easiest way to think about the stack is:

- **Automerge**: who changed the document, and how do replicas converge?
- **Keyhive**: who is allowed to participate, how are they invited, and how does access change over time?

Without the second layer, a CRDT app can merge invalid or unauthorized changes just as faithfully as valid ones.

## Why this is hard

In a normal centralized app, the server decides authorization on every request. In a local-first app, clients can be offline and still mutate local state. That means the system needs a more nuanced model:
- who can issue invitations,
- how membership changes are represented,
- how revocation propagates,
- and eventually how encrypted document access is tied to membership.

This is not a small add-on. It is a second architecture.

## The staged approach we used

AUTODISCO intentionally split the work into two tracks:
1. a **mock ACL flow** for product/UI iteration,
2. a **real Keyhive path** for technical experiments.

That separation matters because the product flow (identity cards, invitations, denied states) can be designed before the cryptographic and WASM integration is perfect.

## The gotchas we've hit

**CRDTs do not imply authorization.** A merged document can still represent an invalid permission state.

**Invitation UX is not the same as invitation protocol.** A contact card and an accept button are product surfaces. Membership-event ingestion and agent/group state are protocol surfaces.

**WASM bindings can become the bottleneck.** In AUTODISCO, part of the hard work was not “how should auth work?” but “why does the WASM binding consume the wrong ownership shape?”

**Durability matters early.** If the auth state disappears on restart, the prototype never becomes operational enough to teach you anything real.

## What to look for in our implementation

When reading AUTODISCO, focus on:
- the adapter seam between mock ACL and Keyhive,
- how invitation creation and acceptance are represented,
- how durable snapshots are stored and restored,
- and how document-level auth is kept conceptually separate from CRDT replication.

Those are the seams where the project becomes legible.

## Where to go deeper

- [[PROJ - AUTODISCO - Keyhive Access Control Architecture]] — the main project report
- [[On-Ramp/crdts-and-local-first]] — the collaboration side of the architecture
- [[Fundamentals/access-control-models]] — authentication, authorization, delegation
