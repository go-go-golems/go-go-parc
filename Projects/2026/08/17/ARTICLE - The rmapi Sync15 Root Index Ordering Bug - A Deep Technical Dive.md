---
title: "The rmapi Sync15 Root Index Ordering Bug: A Deep Technical Dive"
aliases:
  - rmapi root index sorting bug
  - reMarkable cloud 400 invalid root schema
  - sync15 root docSchema ordering
  - RMQ-0023
tags:
  - article
  - remarkable
  - rmapi
  - go
  - debugging
  - cloud-api
  - sync-protocol
status: active
type: article
created: 2026-08-17
repo: /home/manuel/workspaces/2026-08-17/remarquee-fix-root-schema/remarquee
---

# The rmapi Sync15 Root Index Ordering Bug: A Deep Technical Dive

On 2026-08-17, every write operation through `rmapi`-based tools against the reMarkable cloud began failing with HTTP 400 `{"message":"invalid root schema"}`, while every read operation continued to succeed. The failure is not in authentication, not in the document content, and not in the schema version. It is in the *ordering* of the lines inside the root index file. The cloud started enforcing an invariant — root index entries must be sorted by document ID — that the client had been violating silently for as long as the code existed. This note is a complete technical walkthrough of that failure: the protocol structure that makes ordering matter, the code path that produced unsorted output, the reason reads masked the bug, and the fix that resolves it.

This is the sibling of an earlier bug in the same protocol. That earlier failure, `400 {"message":"invalid hash"}`, came from emitting schema version 3 when the cloud expected version 4; it is documented in [[ARTICLE - The rmapi Sync15 Schema V4 Invalid Hash Bug - A Deep Technical Dive]]. The two bugs share a surface (a 400 on the final root PUT) but have distinct root causes: one is about *which schema version* is serialized, the other is about the *order of entries within* the serialized body. Reading both together gives a complete picture of the root-index write path and the two invariants the cloud now enforces on it.

> [!summary]
> - The reMarkable cloud's sync15 root index (`root.docSchema`) is a text file listing every document in the account. As of 2026-08-17, the cloud rejects it with `400 {"message":"invalid root schema"}` unless its entries are strictly ascending by document ID.
> - `rmapi`'s `HashTree.IndexReader()` serializes `t.Docs` in raw slice order with no sort. `Mirror()` (the read path) sorts `t.Docs`, but `Add()` (append) and `Remove()` (swap-delete) break that order and only re-hash — so any write after a read produces an unsorted root.
> - The bug is subtle because the *document* index path *is* canonicalized: `HashEntries()` sorts entries before hashing. The *root* path lacks that canonicalization, so the asymmetry between document and root indexing is the entire defect.
> - The fix sorts `t.Docs` at the single serialization point (`IndexReader()`), which keeps the uploaded body and the `Rehash()`-derived hash consistent by construction. Upstream fix: ddvk/rmapi#77. In `remarquee`, applied as a `go.mod` dependency bump (no application code change).

---

## 1. The failure surface

A cloud write in this protocol is a sequence of HTTP PUTs. The trace from a failing `mkdir` shows the structure precisely:

```
PUT /sync/v3/files/<hash>  rm-filename: <uuid>.metadata   -> 200 OK
PUT /sync/v3/files/<hash>  rm-filename: <uuid>.content    -> 202 Accepted
PUT /sync/v3/files/<hash>  rm-filename: <uuid>.docSchema  -> 200 OK
PUT /sync/v3/files/<hash>  rm-filename: root.docSchema   -> 400 Bad Request
  body: {"message":"invalid root schema"}
```

The first three uploads — the new document's metadata, content, and its per-document index — all succeed. The failure is on the fourth call, which uploads the *root* index: the file that describes the entire document tree to the cloud. The blob store accepted the bytes (a PUT to `/sync/v3/files/<hash>` stores any content by hash), but the cloud's root-index validator rejected them before advancing the root pointer.

Two properties of the failure follow directly from this trace and are worth stating explicitly because they ruled out most of the obvious hypotheses during triage:

- **Reads are unaffected.** A read never serializes the root index; it parses a remote one. The read path (`Mirror()`) sorts the parsed entries into the local tree, so reads never exercise the buggy serializer.
- **The document-level uploads are fine.** The `.metadata`, `.content`, and per-document `.docSchema` all return success. The defect is specific to the *root* index, not to any individual document.

These two properties are why the bug presents as "writes broken, reads fine," and why authentication, rate limiting, and individual document content were all correctly ruled out before the root index was examined.

---

## 2. The sync15 protocol: a three-level content-addressed tree

To understand why the ordering of lines in the root index matters, you need the structure of the protocol. reMarkable's sync15 is a content-addressed blob store with a three-level index.

```
Level 1: ROOT INDEX  (root.docSchema)
         one entry per DOCUMENT in the account
         <hash>:0:<DocumentID>:<subfiles>:<size>

            │  points at, per document
            ▼

Level 2: DOCUMENT INDEX  (<DocumentID>.docSchema)
         one entry per FILE inside a document
         <hash>:0:<fileID>:<subfiles>:<size>

            │  points at, per file
            ▼

Level 3: BLOBS  (the actual bytes: .metadata, .content, .pdf, .rm, ...)
```

Blobs are immutable and addressed by SHA-256 hash. Uploading the same bytes twice is a no-op because the URL is the hash. A document is a small collection of blobs (a `.metadata` JSON, a `.content` JSON, and one or more content files), described by its document index. The root index is the top-level table of contents: one line per document, giving that document's hash, ID, subfile count, and total size. The **root hash** is the SHA-256 of the serialized root index body. The cloud tracks the current root hash plus a monotonically increasing **Generation** number for optimistic concurrency: a write uploads the new root blob, then PUTs `{hash, generation}` to advance the generation.

### 2.1 The root-index wire format (schema v4)

The root index is a tiny text file. Schema 4, which is what current writes emit, has this layout:

```
4                                     <- line 1: schema version
0:.<count>:<totalSize>                <- line 2 (v4 only): summary line
<hash>:0:<DocumentID>:<subfiles>:<size>   <- one line per document
<hash>:0:<DocumentID>:<subfiles>:<size>
...
```

Line 1 is the literal string `4`. Line 2 (present only in v4) is `0:.<N>:<S>` where `N` is the document count and `S` is the sum of all document sizes. Each subsequent line is colon-separated: the document's SHA-256 hex, the file type (`0`), the document ID, the subfile count, and the total size. The root hash is `SHA-256` of this entire file, including the version line and the summary line.

The invariant the cloud began enforcing on 2026-08-17 is on the document lines: they must appear in **strictly ascending order by `DocumentID`**. An unsorted root is rejected with `400 {"message":"invalid root schema"}` on the root PUT. This is the invariant the client violates.

---

## 3. The serializer that emits slice order

The root index is produced by `HashTree.IndexReader()`. This is the function at the center of the bug. In the pinned `rmapi` fork it reads, in essence:

```go
func (t *HashTree) IndexReader() (io.Reader, error) {
    var w bytes.Buffer
    schemaVersion := SchemaVersionV4           // always v4 for writes
    w.WriteString(schemaVersion); w.WriteString("\n")

    if schemaVersion == SchemaVersionV4 {
        totalSize := int64(0)
        for _, d := range t.Docs { totalSize += d.Size }
        w.WriteString("0:." + strconv.Itoa(len(t.Docs)) + ":" +
                      strconv.FormatInt(totalSize, 10) + "\n")
    }

    for _, d := range t.Docs {                 // iterates in SLICE order, no sort
        w.WriteString(d.LineWithSchema(schemaVersion))
        w.WriteString("\n")
    }
    return bytes.NewReader(w.Bytes()), nil
}
```

There is no `sort.Slice` before the loop. `t.Docs` is emitted in whatever order the in-memory slice happens to be in. If that order is not already ascending by `DocumentID`, the emitted body is invalid and the cloud rejects it.

The root hash is derived from this same body. `HashTree.Rehash()` calls `IndexReader()`, reads its output, and SHA-256s it:

```go
func (t *HashTree) Rehash() error {
    reader, _ := t.IndexReader()
    schemaBytes, _ := io.ReadAll(reader)
    hasher := sha256.New()
    hasher.Write(schemaBytes)
    t.Hash = hex.EncodeToString(hasher.Sum(nil))
    return nil
}
```

This is an important point for the diagnosis. The hash and the uploaded body are always *consistent with each other*: `Rehash()` hashes exactly the bytes `IndexReader()` emits. The failure is not a hash/body mismatch (that would be the "invalid hash" error from the sibling bug). The failure is that the *body itself* is invalid — unsorted — even though it is correctly hashed. The cloud validates the body's structure, not just its hash.

---

## 4. The two mutators that break the order

A freshly mirrored tree is sorted. The defect is that two mutators break that order and then only re-hash, without re-sorting. These are the only two ways the slice becomes unsorted.

### 4.1 `Add()` appends

`HashTree.Add()` puts the new document at the end of the slice:

```go
func (t *HashTree) Add(d *BlobDoc) error {
    if len(d.Files) == 0 { return errors.New("no files") }
    t.Docs = append(t.Docs, d)      // append: new doc goes to the end
    return t.Rehash()               // re-hash only; does not sort
}
```

A newly created document has a random UUID. Unless that UUID happens to sort *last* among all existing document IDs, the append leaves the slice unsorted. After `Add()`, the next `Sync()` serializes an unsorted root.

### 4.2 `Remove()` swap-deletes

`HashTree.Remove()` finds the document and moves the final element into its slot:

```go
func (t *HashTree) Remove(id string) error {
    docIndex := /* find index of id */
    if docIndex > -1 {
        length := len(t.Docs) - 1
        t.Docs[docIndex] = t.Docs[length]   // swap last into removed slot
        t.Docs = t.Docs[:length]           // truncate
        t.Rehash()                         // re-hash only; does not sort
        return nil
    }
    return fmt.Errorf("%s not found", id)
}
```

Swap-delete is an O(1) removal, but it reorders the slice. Removing `bbb` from `aaa,bbb,ccc,ddd` produces `aaa,ddd,ccc`: the last element (`ddd`) lands in the removed slot, ahead of `ccc`. After `Remove()`, the next `Sync()` serializes an unsorted root.

---

## 5. Why reads mask the bug

The reason the bug is intermittent across users, and the reason it was not caught earlier, is that the read path *does* sort. `HashTree.Mirror()` rebuilds `t.Docs` from the remote root and sorts it before assigning:

```go
// end of Mirror():
    sort.Slice(head, func(i, j int) bool { return head[i].DocumentID < head[j].DocumentID })
    t.Docs = head
    t.Generation = gen
    t.Hash = rootHash
    return nil
```

So any tree that has only ever been mirrored from the server — never locally mutated — is sorted, and a write against it would happen to succeed. The bug appears only after a local mutation (`Add` or `Remove`) disturbs the sorted order that `Mirror()` established. Whether a given user hit the bug depended on their document IDs and which operation they last performed: a user whose IDs happened to already be sorted, or who only appended IDs that sorted last, would not see it. This is the signature of an invariant violation that the cloud only began checking after the client had been shipping without checking it for a long time.

---

## 6. The asymmetry that makes the bug subtle

The most instructive part of this defect is that the *document* index path is already canonical, and the *root* index path is not. Comparing the two shows exactly where the missing sort should have lived.

The document index is hashed by `HashEntries()`:

```go
func HashEntries(entries []*Entry) (string, error) {
    sort.Slice(entries, func(i, j int) bool {
        return entries[i].DocumentID < entries[j].DocumentID
    })                                        // <-- SORTS, in place
    hasher := sha256.New()
    for _, d := range entries {
        bh, _ := hex.DecodeString(d.Hash)
        hasher.Write(bh)
    }
    return hex.EncodeToString(hasher.Sum(nil)), nil
}
```

`HashEntries()` sorts `entries` by `DocumentID` *before* hashing, as a side effect of computing the hash. `BlobDoc.AddFile()` calls `Rehash()` → `HashEntries()`, so by the time a document index is serialized by `BlobDoc.IndexReaderWithSchema()`, `d.Files` is usually already sorted — as a *side effect* of having been hashed.

The root path has no equivalent. `HashTree.Rehash()` does not call a `HashEntries`-style function that canonicalizes `t.Docs`; it SHA-256s the raw `IndexReader()` output, which is in slice order. So the root index relies on *callers* to keep `t.Docs` sorted, and two of those callers (`Add`, `Remove`) do not. The document index relies on the *hash function itself* to canonicalize, so no caller can break it.

This is the entire bug, stated precisely: the document index canonicalizes its entries as part of hashing; the root index does not, and two mutators exploit that gap.

---

## 7. The write path from a command to the failing PUT

To make the failure concrete, follow a single `cloud mkdir` to the HTTP call that returns 400. `remarquee`'s `MkdirAll` walks the requested path and, for each missing segment, calls `rmapi`'s `ApiCtx.CreateDir`:

```go
// rmapi ApiCtx.CreateDir (simplified)
func (ctx *ApiCtx) CreateDir(parentId, name string, notify bool) (*model.Document, error) {
    id := uuid.New().String()
    // build .metadata + .content, upload each as a blob
    doc := NewBlobDoc(name, id, model.DirectoryType, parentId)
    // ... doc.AddFile(...) per file, upload doc index ...

    err = Sync(ctx.blobStorage, ctx.hashTree, func(t *HashTree) error {
        return t.Add(doc)          // <-- mutator #1: APPEND (unsorts)
    }, notify)
    return doc.ToDocument(), nil
}
```

`Sync` is the generic "mutate the local tree, then push the new root" routine:

```go
func Sync(b *BlobStorage, tree *HashTree, operation func(*HashTree) error, notify bool) error {
    for syncTry := 1; syncTry <= 10; syncTry++ {
        err := operation(tree)                              // (A) Add/Remove: unsorts + Rehash
        indexReader, _ := tree.IndexReader()                 // (B) serialize root (unsorted)
        b.UploadBlob(tree.Hash, "root.docSchema", indexReader) // (C) PUT root blob -> 400
        newGen, err := b.WriteRootIndex(tree.Hash, tree.Generation, notify) // (D) advance gen
        if err == nil { tree.Generation = newGen; break }
        if err != transport.ErrWrongGeneration { return err } // real error -> bail
        tree.Mirror(b, concurrent)                           // (E) retry on concurrent write
    }
    return saveTree(tree)
}
```

Step (C) is the `PUT /sync/v3/files/<hash>` with `rm-filename: root.docSchema` that returns 400. The body it uploads was produced in step (B) from a slice that step (A) just unsorted. `UploadDocument`, `DeleteEntry`, and `MoveEntry` all route through the same `Sync`, so `upload md`, `cloud rm`, and `cloud mv` fail identically.

---

## 8. Why "sort in the mutators" is the wrong fix

A natural first instinct is to add a sort inside `Add()` and `Remove()`. That would resolve today's symptom, but it is the wrong place to enforce the invariant, for two reasons.

First, it fixes the symptom, not the invariant. The cloud's requirement is that the *emitted body* is sorted, not that the in-memory slice is sorted. Any future code path that reorders `t.Docs` — a new mutator, a batch import, a cache deserialization that forgets to sort — reintroduces the bug. The number of mutators will always exceed the number of serializers, and new mutators will forget. Enforcing an output invariant at the output boundary (the serializer) is robust to all of them.

Second, sorting in a mutator risks a hash/body desynchronization. `Rehash()` derives the hash from `IndexReader()`'s output. If a mutator sorts, then a later code path reorders the slice before serialization, the hash (computed from one order) and the body (emitted in another) disagree — and the cloud rejects the hash. Sorting at `IndexReader()` makes `Rehash()` and the upload read the *same bytes by construction*, because `Rehash()` literally calls `IndexReader()`.

The general rule this illustrates: when an invariant is about a serialized representation — canonical ordering, deterministic encoding, the absence of trailing whitespace — enforce it at the serializer, not at each caller.

---

## 9. The fix: sort at the serialization point

The correct fix sorts `t.Docs` at the top of `IndexReader()`, before writing anything:

```go
func (t *HashTree) IndexReader() (io.Reader, error) {
    var w bytes.Buffer
    schemaVersion := SchemaVersionV4
    // ... env override ...

    // Canonical order: the cloud validates that root index entries are sorted
    // by document ID and rejects unsorted uploads with
    // 400 {"message":"invalid root schema"}.
    sort.Slice(t.Docs, func(i, j int) bool {
        return t.Docs[i].DocumentID < t.Docs[j].DocumentID
    })

    w.WriteString(schemaVersion); w.WriteString("\n")
    // ... summary line + per-doc lines, now in sorted order ...
    return bytes.NewReader(w.Bytes()), nil
}
```

The same guard is applied defensively to `BlobDoc.IndexReaderWithSchema()`, sorting `d.Files` before emitting the document index. That path is normally already sorted (as a side effect of `HashEntries`), but relying on a side effect of another function is not an invariant; the one-line sort makes the emitted body canonical regardless of how it was reached.

Both sorts are in-place and idempotent: an already-sorted slice is a no-op, so they cannot disagree with `HashEntries()`'s ordering. This is the patch in ddvk/rmapi#77, and it ships two regression tests:

- `TestRootIndexIsSortedByDocumentID` — the `Add()`/append path (build a tree in non-sorted order, assert sorted output)
- `TestRootIndexSortedAfterRemove` — the `Remove()` swap-delete path, which additionally asserts `tree.Hash == sha256(body)` so the hash and body cannot silently desynchronize in future

---

## 10. Applying the fix in remarquee: a dependency bump

`remarquee` does not serialize the root index itself; it uses `rmapi` through a `go.mod` `replace` directive. The fix is therefore a dependency change, not an application code change.

The `go.mod` pin, before:

```
github.com/juruen/rmapi v0.0.25
replace github.com/juruen/rmapi => github.com/marcobarcelos/rmapi v0.0.0-20260518211546-a0d079936d46
```

The `replace` redirected the `github.com/juruen/rmapi` import path to a fork (`marcobarcelos/rmapi`) at a May 18, 2026 commit that predates the fix. The fix repoints it at the head of ddvk/rmapi#77:

```
replace github.com/juruen/rmapi => github.com/FNStudios-NI/rmapi v0.0.0-20260817154736-f295d5466978
```

Two details of this pin matter. First, ddvk/rmapi#77 is a *cross-repository* pull request: the head commit lives in the contributor's fork (`FNStudios-NI/rmapi`), not in `ddvk/rmapi`. The Go module fetcher reads from the repository named in the `replace`, so the pin must name the contributor's fork, not the base repository. Pinning `ddvk/rmapi` at the same SHA fails with "unknown revision" because the commit is not fetchable from there. Second, the pin uses an exact pseudo-version (`v0.0.0-YYYYMMDDHHMMSS-short12`), derived from the commit's UTC timestamp, rather than a branch name. A pseudo-version resolves to an immutable commit SHA, so the pin remains reproducible even if the contributor's branch is rebased or the PR is closed. proxy.golang.org caches the pseudo-version permanently, so other developers can still fetch it.

Both forks declare `module github.com/juruen/rmapi`, so the import path is unchanged and the bump is drop-in. The "always emit v4 root indexes" behavior that `remarquee` depends on is upstream ddvk behavior, not a marcobarcelos-only patch, and it is preserved in the pinned commit. No `remarquee` source file changes; only `go.mod` and `go.sum`.

---

## 11. Verification against the live cloud

After the bump, the exact reproduction from the issue succeeds:

```
$ remarquee cloud mkdir /ai/2026/08/17 --non-interactive
# previously: Error: failed to create directory: request failed with status 400
# now: exit 0; read confirms /ai/2026/08/17 exists
```

The three write paths that the bug affected each succeed:

- `cloud mkdir` (the `Add`/append path)
- a second `cloud mkdir` in the same session (`Add` after `Add`, proving the slice stays sorted across multiple writes)
- `cloud rm` (the `Remove`/swap-delete path)
- `upload md` (the full `MkdirAll` + `UploadDocument` path)

Cleanup (`cloud rm` of the test directories) left no trace, confirmed by a read. `go vet` and the `pkg/rmcloud` and `upload` test packages pass. The sort is confirmed present in the pinned source: `sort.Slice(t.Docs, ...)` at `api/sync15/tree.go:178` and `sort.Slice(d.Files, ...)` at `api/sync15/blobdoc.go:117`, with the v4-always-emit behavior intact at `api/sync15/tree.go:157`.

---

## 12. The two sibling bugs, compared

This bug and the earlier "invalid hash" bug are worth comparing directly, because they are the two invariants the cloud now enforces on the root index and they are easy to conflate.

| Property | "invalid hash" (sibling) | "invalid root schema" (this bug) |
|---|---|---|
| Cloud error body | `{"message":"invalid hash"}` | `{"message":"invalid root schema"}` |
| What is wrong | Wrong schema *version* emitted (v3 instead of v4) | Wrong *entry order* within a v4 body |
| Where in `rmapi` | `IndexReader()` defaulting to v3 when `SchemaVersion` empty | `IndexReader()` not sorting `t.Docs` |
| Trigger | Empty `SchemaVersion` on a new tree | Any `Add()` or `Remove()` after a `Mirror()` |
| Reads affected | No | No |
| `remarquee` fix | Reflection: `forceSchemaV4` sets `SchemaVersion="4"` in `pkg/rmcloud/auth.go` | Dependency bump: `go.mod` `replace` → fixed fork |
| Upstream fix | ddvk/rmapi#55 (default to v4) | ddvk/rmapi#77 (sort root index) |
| Application code changed | Yes (a reflection workaround) | No |

The two fixes live in different layers because the two bugs have different relationships to `remarquee` code. The v3/v4 default was a `rmapi` behavior that `remarquee` could patch at context-creation time by reaching into unexported state, so it shipped as an application-level workaround (`forceSchemaV4`). The root ordering bug is a missing sort inside `rmapi`'s serializer that no amount of context-level setup can fix for the lifetime of a session (a sort at context creation fixes only the first write; the second `Add` re-unsorts), so it could not be patched the same way and required the dependency bump. This is why the two siblings were fixed with different mechanisms despite sharing a surface.

---

## 13. Working rules

- **Enforce output invariants at the serializer, not at each caller.** When an invariant is about a serialized representation — ordering, encoding, whitespace — put the enforcement at the single point that produces the bytes. Callers outnumber serializers and new callers will forget.
- **A hash function that canonicalizes protects all callers; a serializer that does not canonicalize betrays all callers.** The document index was safe because `HashEntries()` sorted as part of hashing; the root index was unsafe because `IndexReader()` did not. Prefer canonicalization that cannot be bypassed.
- **Reads and writes can have opposite invariants.** `Mirror()` sorted on read, which masked that the write path did not. A read path that repairs state is not evidence that the write path is correct.
- **Pin cross-repo PR heads by pseudo-version, and name the contributor's fork.** A pull request against `ddvk/rmapi` whose commits live in `FNStudios-NI/rmapi` is not fetchable from `ddvk/rmapi`. Pin the fork the commit actually lives in, by immutable pseudo-version, and leave a TODO to re-pin to the base repo once the PR merges.
- **Two 400s on the same endpoint can have different root causes.** "invalid hash" and "invalid root schema" both fail the final root PUT but address different defects. Read the error body, not just the status code.

---

## 14. Related notes

- [[ARTICLE - The rmapi Sync15 Schema V4 Invalid Hash Bug - A Deep Technical Dive]] — the sibling bug (v3/v4 schema version, "invalid hash", fixed by `forceSchemaV4`)
- [[PROJ - Remarquee - reMarkable Toolkit]] — the remarquee project note
- Issue: [go-go-golems/remarquee#23](https://github.com/go-go-golems/remarquee/issues/23)
- Upstream fix PR: [ddvk/rmapi#77](https://github.com/ddvk/rmapi/pull/77) ("fix: sort root index by document ID before serializing")
- Fix PR: [go-go-golems/remarquee#24](https://github.com/go-go-golems/remarquee/pull/24)
- Ticket: `ttmp/2026/08/17/RMQ-0023--fix-root-index-sorting-cloud-writes-fail-with-400-invalid-root-schema/` (intern design doc + investigation diary)
- Source (fix): `/home/manuel/workspaces/2026-08-17/remarquee-fix-root-schema/remarquee/go.mod` (replace directive)
- Source (context): `/home/manuel/workspaces/2026-08-17/remarquee-fix-root-schema/remarquee/pkg/rmcloud/auth.go` (`forceSchemaV4`, the sibling bug's workaround)
- Pinned fork: `$(go env GOMODCACHE)/github.com/!f!n!studios-!n!i/rmapi@v0.0.0-20260817154736-f295d5466978/api/sync15/{tree,blobdoc,common,apictx}.go`
