---
title: "CRDTs and Local-First Architecture"
aliases:
  - crdt
  - conflict-free replicated data types
  - local-first
  - automerge
  - eventual consistency
tags: [knowledge-base, on-ramp, crdt, local-first, distributed, automerge]
status: active
type: knowledge-base
created: 2026-05-11
---

# CRDTs and Local-First Architecture

> [!summary]
> Conflict-Free Replicated Data Types let multiple writers edit the same document without a central server coordinating every change. Local-first means the app works offline and syncs when connectivity returns. This entry covers what CRDTs are (and aren't), why "merge" is the wrong mental model, and how we structure a local-first app so the CRDT handles consistency while domain code handles semantics.

## The idea in one paragraph

A CRDT is a data structure whose merge operation is **commutative**, **associative**, and **idempotent**. No matter what order changes arrive in, or how many times the same change is applied, the result is the same. This property means replicas can diverge independently and converge without coordination — no locks, no leader election, no "who wins?" conflict resolution. The CRDT guarantees *eventual consistency*; your domain code guarantees *application correctness*.

## Why we care

Our AUTODISCO project is a Discord-style chat app where every browser tab is an independent writer. The server is a relay, not an authority. If the server goes down, the browsers keep working. When the server comes back, changes sync. This is a local-first architecture, and CRDTs are the mechanism that makes it work without data loss or conflicts.

But CRDTs solve only the consistency problem. They don't know that you shouldn't send a message to an archived channel, or that a user can only edit their own messages, or that a channel name must be unique. These are domain constraints, and they live in your application code — wrapped around the CRDT, not inside it.

## The three things to understand

**1. Merge is not "combine."** When two users edit the same document simultaneously, the CRDT doesn't choose one edit over the other. It merges both. If user A inserts "Hello" at position 0 and user B inserts "World" at position 0, the result contains both words — the CRDT's internal ordering (typically based on Lamport timestamps or operation IDs) determines which appears first. There is no conflict. There is no "winner." Both edits survive.

**2. The server is a peer, not an authority.** In a CRDT-based system, the server stores and relays changes, but it doesn't validate them. The server can go down and the clients keep working. The server can come back up and sync missed changes. This is the "local-first" property: the app is fully functional without network connectivity.

**3. Domain constraints are your job.** The CRDT will faithfully merge any change you give it. If you tell it to insert a message in a non-existent channel, it will. If you tell it to delete a user who doesn't exist, it will record the deletion. The CRDT has no schema enforcement. Your domain mutation functions wrap every CRDT operation with validation:

```typescript
// Domain mutation — validates before writing to the CRDT
function sendMessage(doc: Doc, channelId: string, content: string): void {
    const channel = doc.channels[channelId];
    if (!channel) throw new Error("Channel not found");
    if (channel.archived) throw new Error("Channel is archived");

    // Now the CRDT operation is safe
    change(doc, (d) => {
        d.messages[channelId].push({
            id: nanoid(),
            content,
            author: d.currentUser,
            timestamp: Date.now(),
        });
    });
}
```

## The gotchas we've hit

**CRDTs don't enforce uniqueness.** If two users create a channel with the same name simultaneously, both channels exist after merge. The CRDT doesn't know "channel name must be unique." You need to handle this at the domain level — typically by making the channel ID the CRDT key and treating the name as a mutable property that can be corrected after merge.

**Document size grows without compaction.** A CRDT document stores every change ever made (for conflict resolution). After thousands of edits, the document can be megabytes of metadata for a few kilobytes of actual content. Automerge provides `Automerge.compact()` to prune unreachable history, but compaction must be coordinated across peers.

**IndexedDB persistence requires explicit setup.** The browser Automerge Repo needs an `IndexedDBStorageAdapter` to persist documents across tab reloads. Without it, every tab reload creates a fresh repo with no history. The setup is straightforward but easy to forget:

```typescript
const repo = new Repo({
    network: [new WebSocketClientAdapter(wsUrl)],
    storage: new IndexedDBStorageAdapter(),
    peerId: randomPeerId(),
});
```

## Where to go deeper

- **Kleppmann, M. (2017)**. *Designing Data-Intensive Applications*, Chapter 5. — The best explanation of eventual consistency and why CRDTs work, without requiring distributed systems background.
- **Automerge documentation**: <https://automerge.org/docs/> — The CRDT library we use. The "how it works" page explains the internal operation log.
- **AUTODISCO project report** in this PARC library — Our implementation of a local-first chat app with Automerge.
- [[PROJ - AUTODISCO - Automerge Discord App Architecture]] — the full project report with domain mutation helpers and IndexedDB persistence
