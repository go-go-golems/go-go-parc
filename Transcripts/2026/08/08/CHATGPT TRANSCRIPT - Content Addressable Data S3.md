# Content Addressable Data S3

- URL: https://chatgpt.com/c/6a767d1c-f044-83ea-8fe6-0e678fc5a3cc
- Created: 2026-08-08T00:49:47.707Z

---

> doing content addressable data on s3? or what's a good way to do that at scale?

Yes—S3 works well as the blob store for content-addressable storage. The main design choice is whether S3 is only immutable blob storage, or whether you also need reference counting, reachability, and garbage collection at large scale.

```json
{"system2_search_query":[{"q":"site:docs.aws.amazon.com Amazon S3 conditional writes If-None-Match content addressable checksum strong consistency"},{"q":"site:docs.aws.amazon.com Amazon S3 performance prefixes request rates no random prefix"},{"q":"site:docs.aws.amazon.com Amazon S3 checksum SHA256 object metadata multipart ETag"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Designing atomic uploads**

I’m using content-addressed keys with a cryptographic hash, then creating objects conditionally so concurrent uploads converge safely. I’m also checking checksum validation and considering verification on duplicate paths when writers aren’t fully trusted.

**Designed atomic uploads**

</details>

```json
{"system1_search_query":[{"q":"site:docs.aws.amazon.com Amazon S3 Inventory object list daily weekly Athena"},{"q":"site:docs.aws.amazon.com Amazon S3 lifecycle abort incomplete multipart uploads"},{"q":"site:docs.aws.amazon.com DynamoDB transactions conditional writes atomic counter"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Applying the upload pattern**

I’m recommending a SHA-256 content-addressed S3 key, conditional creation with checksum validation, and treating “already exists” as success. I’ll separate blob storage from metadata, use hash prefixes for distribution, and add garbage collection for unreferenced objects.

**Applied the upload pattern**

**Searched 1 website**

</details>

Yes. **S3 is a good backing store for content-addressable data**, and at large scale I’d keep the design fairly simple:

```text
logical refs / manifests  -> DynamoDB
                              |
                              v
                         content hashes
                              |
                              v
S3:
cas/sha256/7f/83/7f83b1657ff1fc...
cas/sha256/a4/12/a412...
```

For each blob, compute a SHA-256 over the exact bytes and make the digest part of the S3 key. The first few hash bytes make convenient prefixes and naturally spread traffic across S3 partitions. AWS documents at least 3,500 write-like requests/sec and 5,500 GET/HEAD requests/sec **per partitioned prefix**, with no limit on the number of prefixes; S3 also scales prefixes automatically. citeturn135574search13turn135574search11

### The important trick: conditional PUT

Don't do this:

```text
HEAD hash
if missing:
    PUT hash
```

That's an extra request and has a race.

Instead:

```text
hash = sha256(data)

key = "cas/sha256/" +
      hash[0:2] + "/" +
      hash[2:4] + "/" +
      hash

PUT s3://bucket/$key
    If-None-Match: *
    ChecksumSHA256: hash
```

`If-None-Match: *` makes the create conditional on the key not already existing. If two workers upload the same content simultaneously, one wins and the other gets a precondition failure, which you can treat as "blob already stored." S3 supports this directly, and you can even enforce conditional writes with bucket policy. citeturn135574search0turn135574search1

Also send the S3 SHA-256 checksum. S3 validates supplied checksums during upload and stores checksum information with the object, including for supported multipart-upload modes. **Don't use ETag as your content address**: its semantics vary with multipart uploads and encryption; use an explicit cryptographic digest instead. citeturn135574search4turn135574search8

S3 has strong read-after-write consistency, so once that PUT succeeds you can immediately refer to the blob without an eventual-consistency workaround. citeturn135574search17

### Then separate "blobs" from "references"

The part I would **not** try to make content-addressable in S3 is your mutable application state.

For example:

```text
DynamoDB

artifact_id = customer-123/current-model
root_hash   = sha256:923ab...
version     = 42
```

and:

```text
S3

cas/sha256/92/3a/923ab...  -> manifest
cas/sha256/f1/72/f172...   -> chunk
cas/sha256/4b/98/4b98...   -> chunk
```

That gives you Git-like semantics:

```text
mutable pointer
      |
      v
   manifest --------+
    /  |  \         |
   v   v   v        |
 blob blob manifest |
              |     |
              +-----+
```

If the logical object changes, you create new CAS objects and atomically move the DynamoDB pointer. DynamoDB conditional writes/transactions are appropriate when you need compare-and-swap or atomic updates of several metadata records. citeturn512279search8turn512279search14

I would generally **write the CAS blobs first, then commit the root/reference last**. If the process crashes halfway through, you merely have unreachable blobs; GC can remove them later. That is much easier than trying to make an S3 PUT and a DynamoDB transaction globally atomic.

### The two places where "at scale" changes the design

**Very large/streaming objects:** you don't know the CAS key until you've read the entire object. Ideally hash the bytes as they're generated and either spool them locally before the final S3 upload, or arrange for the producer to know/provide the digest. Uploading under a temporary S3 key and then copying to the hash key works but creates extra S3 I/O, so I wouldn't make that the default for huge volumes.

For multipart uploads, have a lifecycle rule abort abandoned multipart uploads so crashed writers don't leave paid-for parts around indefinitely. S3 supports lifecycle cleanup for this explicitly. citeturn512279search1

**Tiny objects:** if you're talking billions of 1–10 KB blobs, S3 requests and per-object bookkeeping can become more important than byte storage. At that point I'd consider immutable **packfiles**:

```text
pack/abc123       # e.g. 128 MB packed object

index:
hash A -> pack abc123, offset 0,       len 5843
hash B -> pack abc123, offset 5843,    len 9012
hash C -> pack abc123, offset 14855,   len 3921
```

Then retrieve blobs with S3 range reads. You trade simplicity for dramatically fewer objects/requests. I wouldn't introduce packing unless object count/request economics actually justify it.

### Garbage collection

I would avoid synchronous distributed reference counting unless the workload specifically demands immediate reclamation. A safer CAS model is:

```text
1. enumerate live roots
2. walk manifests / mark reachable hashes
3. find old unmarked blobs
4. delete after a grace period
```

For a very large bucket, S3 Inventory is useful here: AWS can generate a daily or weekly CSV/ORC/Parquet inventory of objects, and Athena can query those inventories, avoiding a giant application-driven object listing just to construct the GC candidate set. citeturn512279search0turn512279search3

So my default production architecture would be:

```text
             ┌───────────────┐
upload ─────>│ compute SHA256│
             └───────┬───────┘
                     |
                     v
             ┌────────────────────┐
             │ S3 CAS bucket      │
             │ If-None-Match: *   │
             │ sha256/ab/cd/HASH  │
             └─────────┬──────────┘
                       |
                blob durable
                       |
                       v
             ┌────────────────────┐
             │ DynamoDB           │
             │ logical ref → hash │
             └────────────────────┘

periodically:
roots -> mark reachable -> S3 Inventory -> sweep old garbage
```

**If I were building this today, I'd start with direct one-object-per-hash S3 CAS + DynamoDB refs.** That's already capable of enormous scale. I'd only add packfiles/chunking if your distribution is dominated by tiny blobs, or a Merkle/chunked layer if you specifically want block-level deduplication between similar large objects. citeturn135574search13


---

> what if i want to run something like this on my own server?

On one server, I’d usually **not** start by recreating S3. The simplest robust version is a local filesystem CAS plus a small metadata DB; only add an S3-compatible layer if you need that API or expect to grow into multiple nodes.

```json
{"system2_search_query":[{"q":"site:min.io/docs minio server erasure coding object store official docs"},{"q":"site:garagehq.deuxfleurs.fr documentation Garage S3 compatible object store official"},{"q":"site:github.com/seaweedfs/seaweedfs wiki S3 API filer volume official"},{"q":"site:docs.ceph.com radosgw s3 compatible object gateway official"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Designing the CAS**

I’m outlining a practical single-server layout: hash-addressed fan-out directories, temporary writes with atomic publication, metadata in SQLite or PostgreSQL, immutable permissions, and mark-and-sweep garbage collection. I’ll also distinguish durability, concurrency, deduplication, and when chunking becomes worthwhile.

**Designed the CAS**

</details>

```json
{"system1_search_query":[{"q":"site:garagehq.deuxfleurs.fr/documentation quick start single node Garage S3 compatible lightweight official"}],"response_length":"short"}
```

<details><summary>💭 Thinking</summary>

**Choosing a deployment**

I’m recommending a filesystem-backed CAS for one server: hash fan-out paths, atomic immutable publication, metadata in SQLite, and periodic integrity checks. I’m reserving object stores or distributed systems for multi-host durability, not basic single-machine deployment.

**Chose a deployment strategy**

**Searched 4 websites**

</details>

Absolutely. On **one server**, I’d probably skip S3 entirely and implement the CAS directly on top of the filesystem.

A solid layout is:

```text
/srv/cas/
  sha256/
    7f/
      83/
        7f83b1657ff1fc53b92dc...
    a4/
      12/
        a412...
```

Then your write path is essentially:

```text
incoming bytes
     |
     +--> SHA-256
     |
     v
/tmp/cas-upload-xyz
     |
     | finished hashing
     v
/srv/cas/sha256/7f/83/<full-sha256>
```

The key implementation detail is to **write to a temporary file first**, calculate the hash while streaming, `fsync()` it, and then atomically install it under the hash name. On Linux you can use `renameat2(..., RENAME_NOREPLACE)` or a hard-link-based create-if-absent operation so concurrent writers of identical data don't overwrite each other.

Your application API can then be very small:

```text
put(stream) -> hash
get(hash)   -> stream
exists(hash)
delete(hash)    # generally only GC calls this
```

And separately:

```text
SQLite / Postgres

refs:
    "users/123/avatar" -> sha256:abcd...
    "builds/latest"    -> sha256:1234...
```

I like keeping those two things completely separate:

```text
             mutable
       SQLite/Postgres
             |
             v
        logical refs
             |
             v
          hashes
             |
             v
        immutable CAS
             |
             v
       ext4 / XFS / ZFS
```

For a single machine, **SQLite is often enough** for the ref/index database. If multiple processes/machines will heavily mutate refs concurrently, Postgres is the natural next step.

### If you're expecting millions/billions of objects

There are two architectures I'd consider.

For normal-sized objects—say tens of KB through multi-GB—just keep **one file per hash**. Don't prematurely build anything more elaborate.

If you have enormous numbers of tiny objects, however:

```text
5 KB
2 KB
9 KB
3 KB
...
```

then individual filesystem files eventually become inefficient. At that point I'd switch to append-only packfiles:

```text
/srv/cas/packs/
    pack-000001.dat
    pack-000002.dat
    pack-000003.dat
```

with an index:

```text
hash                                      pack        offset       length
abcd...                                   000001      0            5412
ef12...                                   000001      5412         2811
9043...                                   000001      8223         9940
```

So your architecture becomes roughly:

```text
                 ┌─────────────┐
PUT ── hash ────>│ CAS index   │
                 │ SQLite/LMDB │
                 └──────┬──────┘
                        |
                hash -> location
                        |
           ┌────────────┴────────────┐
           v                         v
    loose objects                pack files
    big/new objects             small objects
```

That's very similar conceptually to what Git eventually does with loose objects → packfiles.

### If you want S3 compatibility

Then I'd avoid writing your own HTTP object storage server and put an existing system underneath your CAS API.

**SeaweedFS is particularly interesting right now.** Its current `weed mini` command runs a single-node S3 object store from one binary, and the project is explicitly designed around large numbers of files; you can later add volume servers to scale out. citeturn304677view1

For example, its documented single-node setup is basically:

```bash
AWS_ACCESS_KEY_ID=admin \
AWS_SECRET_ACCESS_KEY=... \
S3_BUCKET=cas \
weed mini -dir=/srv/storage
```

and then your CAS client continues doing:

```text
PUT cas/sha256/ab/cd/<hash>
GET cas/sha256/ab/cd/<hash>
```

SeaweedFS is probably what I'd investigate first if your workload is **lots of small blobs** and there's a reasonable chance you'll eventually go from one machine to several. citeturn304677view1

Another option is **Garage**. It's deliberately a lightweight S3-compatible distributed object store. Its design emphasizes running across ordinary machines and networks, using replication rather than erasure coding; its own documentation explicitly says extreme performance isn't its main objective. citeturn620961search0

I'd think of the choices roughly as:

| Situation | What I'd use |
|---|---|
| One server, CAS is part of my app | **Filesystem + SQLite** |
| One server but need S3 API | **SeaweedFS** |
| Huge number of small blobs | **SeaweedFS** |
| 2–10 modest machines / geographically distributed | **Garage** |
| Large serious storage cluster + block/file/object needs | **Ceph** |
| Billions of tiny CAS entries, maximum efficiency | Custom **packfiles + index** |

Ceph exposes an S3-compatible API through RADOS Gateway and is appropriate when you actually want a full distributed storage platform rather than merely a blob directory. citeturn304677view3

MinIO is worth being aware of, but its current product situation is different from the historical "just install MinIO OSS" recommendation: the current MinIO documentation focuses on AIStor, which requires a license, while referring to an AGPLv3 community server. citeturn304677view2 So for a new small self-hosted deployment I'd investigate SeaweedFS/Garage before automatically picking MinIO.

### What I would actually build

If this were **one beefy Linux box**, my version 1 would be extremely boring:

```text
NVMe / HDD array
       |
      ZFS
       |
/data/cas/sha256/xx/yy/HASH

Postgres or SQLite:
logical key -> hash
```

with:

```text
PUT:

1. create temp file
2. stream input:
       write(bytes)
       sha256.update(bytes)
3. fsync(temp)
4. digest = sha256.final()
5. atomically install temp as /cas/sha256/xx/yy/digest
   - if already exists: discard temp
6. return digest
```

Then I'd run periodic GC:

```text
all refs
   |
   v
mark hashes
   |
   v
everything in CAS
   |
   +-- marked --------> keep
   |
   +-- unmarked
          |
          +-- younger than 7 days -> keep
          |
          +-- older than 7 days --> delete
```

The grace period is important because it makes crashes and races much less dangerous.

The nice property is that **the storage layer itself almost has no database**. Given a SHA-256, you know exactly where the bytes live. Losing your metadata DB might lose human/logical names, but it doesn't make the underlying objects undecodable.

And if the single machine eventually stops being enough, you can preserve the exact same application abstraction:

```text
CAS.put()
CAS.get(hash)
CAS.has(hash)
```

and change its backing implementation from:

```text
LocalFilesystemCAS
```

to:

```text
SeaweedS3CAS
GarageS3CAS
S3CAS
```

without changing the rest of the system.

If your rough workload is, say, **object count + average object size + total TB + read/write rate**, I can sketch the storage layout I'd use and whether I'd bother with loose files, packfiles, chunking, or an object-store daemon.


---

> existing opensource?

Yes. There are several, but the best choice depends on whether you want a **generic S3-compatible object store** or a **true hash-addressed CAS API**. I’ll separate those because they solve slightly different problems.

```json
{"system2_search_query":[{"q":"official bazel-remote content addressable storage GitHub"},{"q":"official SeaweedFS S3 GitHub content addressable storage"},{"q":"official Garage S3 object store documentation"},{"q":"official BuildBarn content addressable storage GitHub"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Comparing CAS options**

I’m narrowing this to self-hosted systems that store blobs by digest. Bazel Remote, BuildBarn, OCI registries, and Perkeep are candidates, but their APIs and scalability differ, so I’m matching them to the user’s needs.

**Compared CAS options**

</details>

```json
{"system1_search_query":[{"q":"site:github.com/buildbarn bb-storage content addressable storage Buildbarn"},{"q":"site:docs.ipfs.tech content addressing CID self host Kubo"},{"q":"site:github.com/perkeep/perkeep content addressable storage"},{"q":"site:github.com/folbricht/desync casync content addressable storage casync"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Searched 11 websites**

</details>

Yes. If you mean **actual content-addressable storage**, not merely “self-hosted S3,” there are existing open-source options.

- **`bazel-remote`** — probably the closest match to the simple CAS we were describing. It exposes `PUT /cas/<sha256>`, `GET /cas/<sha256>`, `HEAD`, plus the standard Bazel Remote Execution CAS gRPC API. It stores blobs on local disk, supports zstd compression, enforces a configurable maximum size, and automatically evicts LRU data. Despite the name, you can use the CAS API independently of Bazel. citeturn863748view0  
  **I'd start here if your data is cache-like.** The caveat is important: it's designed as a cache, so eviction is part of its model.

- **BuildBarn `bb-storage`** — the more serious/scalable version of that idea. It's a dedicated CAS storage daemon implementing the Remote Execution protocol. Its local backend stores data in large files with a hash-table index rather than creating millions of filesystem files, and it supports composing/distributing storage backends. citeturn163092view1turn318983search19  
  **I'd investigate this if you're talking many TB / lots of objects / multiple servers.**

- **IPFS Kubo** — genuine CAS with CIDs, automatic chunking of large objects, Merkle DAGs, pinning, HTTP gateways, and multi-node distribution. It can run completely self-hosted; a local Kubo gateway can serve content by CID. citeturn318983search5turn163092view2  
  **Good if you actually want chunk-level dedupe/distribution.** Probably too much machinery if you only need `SHA256 -> bytes`.

- **iroh-blobs** — interesting if you're building something new rather than wanting an S3 clone. Iroh provides BLAKE3-based content-addressed blob transfer intended to scale from small blobs to very large ones. citeturn129965search0

There's also an unexpectedly useful option: **an OCI registry**. The OCI Distribution API fundamentally stores blobs addressed by digest, and the open-source `distribution/distribution` registry implements it. So you get semantics like `sha256:abc...` plus an established HTTP protocol and clients. citeturn129965search3turn129965search4 It's somewhat container-shaped, though, so I wouldn't use it unless OCI interoperability is useful.

By contrast, **Garage and SeaweedFS aren't inherently CAS**. They're open-source object stores. You'd still implement:

```text
hash = SHA256(bytes)
PUT /bucket/sha256/<hash>
```

on top of them. Garage is specifically designed as a lightweight, self-hosted, distributed S3-compatible service. citeturn163092view3

For what you've described so far, I'd narrow it to:

```text
simple, one server
       |
       +-- disposable/cache data ---> bazel-remote
       |
       +-- durable CAS -------------> IPFS/Kubo
       |                               or small custom layer
       |
       +-- huge CAS / scale-out ----> BuildBarn
       |
       +-- want S3 API -------------> Garage / SeaweedFS
                                      + hash keys yourself
```

**`bazel-remote` is particularly worth looking at first.** Its API is almost exactly the primitive we're talking about:

```http
PUT /cas/2cf24dba5fb0a30e...
<bytes>

GET /cas/2cf24dba5fb0a30e...
```

If your requirement is **durable canonical storage rather than a cache**, though, I would not choose it as-is because of its eviction-oriented design. In that case I'd look more closely at BuildBarn, Kubo, or a durable CAS built on Garage/SeaweedFS. citeturn863748view0

