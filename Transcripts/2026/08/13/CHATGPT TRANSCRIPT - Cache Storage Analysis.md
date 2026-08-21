# Cache Storage Analysis

- URL: https://chatgpt.com/c/6a7e30f1-03c4-83ea-b66d-5efbc81191f0
- Created: 2026-08-13T21:02:44.113Z

---

> Review this

> also analyze alternative storage / retrieval for the cache.

<details><summary>💭 Thinking</summary>

**Assessing storage alternatives**

I’m reviewing the proposed S3-backed cache and testing its assumptions. I’ll compare direct object access, shared filesystems, databases, and packed artifacts, while checking whether environment isolation undermines cross-environment reuse.

**Assessed storage alternatives**

</details>

I’ll review the design for correctness first, then compare viable cache backends/retrieval patterns against the actual workload: ~114k immutable JSON entries, ~2.2 GB, build-only access, and Fargate. I’ll separate document-supported findings from current AWS-specific options.

```json
{"system1_search_query":[{"q":"site:docs.aws.amazon.com Amazon S3 performance request rate prefixes GET PUT latency strong consistency documentation"},{"q":"site:docs.aws.amazon.com AWS CLI s3 sync comparison size timestamp checksum mode documentation"},{"q":"site:docs.aws.amazon.com ECS Fargate EBS volume support task documentation"},{"q":"site:docs.aws.amazon.com S3 Express One Zone directory buckets low latency documentation"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Comparing retrieval patterns**

I’m narrowing the design toward direct remote reads with a local read-through cache, packed immutable snapshots, or a snapshot-plus-delta model. The main trade-off is simplicity versus startup latency, request count, and compaction complexity.

**Compared retrieval patterns**

</details>

```json
{"system1_search_query":[{"q":"site:docs.aws.amazon.com Amazon S3 Files ECS Fargate cache file system documentation"},{"q":"site:docs.aws.amazon.com Amazon S3 Files overview high performance cache sync S3 documentation"},{"q":"site:docs.aws.amazon.com ElastiCache Serverless Valkey Redis maximum item size documentation"},{"q":"site:docs.aws.amazon.com DynamoDB maximum item size 400 KB provisioned on-demand documentation"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 7 websites**

</details>

A newer AWS-native option materially changes the tradeoff set: **Amazon S3 Files** now supports Fargate and exposes S3-backed objects through a high-performance file-system cache. That deserves evaluation before building custom sync code.

```json
{"system1_search_query":[{"q":"site:docs.aws.amazon.com/AmazonS3/latest/userguide s3 files consistency synchronization writes durability import export file system Fargate"},{"q":"site:docs.aws.amazon.com/AmazonECS/latest/developerguide configure S3 Files ECS Fargate task definition volume"},{"q":"site:docs.aws.amazon.com/AmazonS3/latest/userguide S3 Files limitations file size POSIX rename atomic write"},{"q":"site:docs.aws.amazon.com/AmazonS3/latest/userguide S3 Files pricing metering high performance storage minimum"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

Two document-level issues are already clear: the design promises cross-environment reuse but initially namespaces by environment, and it rejects SQLite because of NFS hazards even though **SQLite-on-local-ephemeral-disk** is a different architecture. Those should be corrected regardless of backend choice.

```json
{"system1_search_query":[{"q":"site:sqlite.org wal network filesystem not supported documentation"},{"q":"site:sqlite.org SQLite network filesystem locking documentation"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Searched 2 websites**

</details>

The document has the right diagnosis, but I would **not approve the proposed architecture unchanged**. The EFS bottleneck analysis is solid, but there are several correctness gaps and, as of August 2026, an AWS storage option that the document does not consider: **Amazon S3 Files**.

The central observation remains valid: CoinVault is doing 114,106 small immutable cache-file accesses, and the actual abstraction is already a simple `Load`/`Store` cache over content-addressed files. fileciteturn0file0L44-L48 The current coupling of `FileCache` to `<output>/embed-cache` on EFS is also correctly identified as the architectural seam to change. fileciteturn0file0L170-L178

### Issues I would fix before implementation

| Priority | Issue | Why it matters | Recommended change |
|---|---|---|---|
| **P0** | Cross-environment reuse contradicts the proposed namespace | The requirements say dev/prod should reuse the same embedding, but the proposed `<environment>/embed-cache/` layout deliberately prevents that. fileciteturn0file0L77-L80 fileciteturn0file0L416-L423 | Either remove cross-env reuse from Phase 1 requirements, or use a shared semantic namespace from day one. |
| **P0** | Cache correctness assumes provider determinism | The design says the same key necessarily produces the same value because of “provider determinism.” fileciteturn0file0L254-L261 But the described key contains `{Model, Text}` plus step/version; the document does **not** establish that provider identity/revision is in the key. fileciteturn0file0L158-L166 | Explicitly bind provider/provider revision/model revision into the namespace, and define immutable cache semantics as **first writer wins**, not “provider is deterministic.” |
| **P0** | Existing export cannot directly seed the proposed S3 layout | `knowledge cache-export` creates a single tar+gzip object. fileciteturn0file0L198-L208 The proposed runtime expects 114k individual S3 objects. | Add an explicit restore/extract/seeding command, or don't claim the existing export directly seeds the live prefix. |
| **P1** | `aws s3 sync` semantics are misstated | The open question says sync is incremental through size/ETag comparison. fileciteturn0file0L580-L584 AWS documents the normal high-level sync comparison primarily in terms of size and modification time; checksum behavior is opt-in. citeturn889931search2turn638035search21 | Specify exactly how equality is determined, or use an application-owned content-addressed upload protocol. |
| **P1** | Startup performance claim is too strong | The document says syncing ~2.2 GB / 114k objects should take “seconds to low minutes.” fileciteturn0file0L344-L356 S3 supports high parallel request rates, but AWS explicitly recommends parallelization and says realized performance depends on workload/configuration. citeturn638035search5 | Make this a benchmark hypothesis, not a design assumption. |
| **P1** | IAM variables conflate bucket and object resources | `ListBucket` is a bucket-level permission; `GetObject`/`PutObject` are object-level permissions. AWS uses `s3:prefix` to scope listing. citeturn618656search1turn618656search3 | Use separate `bucket_arn` and `object_prefix_arn` inputs/policy statements. |
| **P1** | Sync-at-end has an unnecessary durability window | The document acknowledges that task termination before final sync loses newly computed cache entries. fileciteturn0file0L572-L574 | Prefer write-through persistence, S3 Files, or incremental remote PUTs during the build. |
| **P2** | SQLite is rejected too broadly | The rejected alternative is specifically SQLite **on EFS/NFS**. fileciteturn0file0L440-L442 SQLite itself explicitly warns about WAL/network filesystems; that objection does not apply to a SQLite DB downloaded onto Fargate ephemeral storage. citeturn700735search0turn700735search3 | Add “local SQLite snapshot backed by S3” as a separate alternative. |

One other wording problem is the claim that the cache key “already binds provider+model.” The evidence in the document only demonstrates model+text+step/version/task-prefix. fileciteturn0file0L158-L166 Unless `TaskPrefix` is explicitly defined to incorporate provider identity and immutable model revision, I would not make the stronger claim.

## Alternative storage/retrieval architectures

The workload characteristic that matters most is that a warm build appears to look up **essentially the entire cache**: the observed run has 114,106 embeddings and 114,106 effective hits. fileciteturn0file0L64-L73 That makes this different from a conventional sparse cache. A design optimized only for lazy cache misses can still end up performing 114k remote operations on every build.

| Architecture | Warm-read behavior | Code change | Durable writes | Cross-env | Assessment |
|---|---|---:|---:|---:|---|
| Current EFS | 114k network filesystem opens | None | Yes | No | **Reject** |
| Proposed S3 → ephemeral full sync | Download whole working set every task, then local reads | Medium | Only at final sync | Yes if shared | **Good baseline** |
| **S3 Files** | Mounted filesystem with persistent high-performance cache backed by S3 | Low | **Yes** | Yes | **Benchmark first** |
| Direct S3 `Cache` + local L1 | GET each uncached entry; PUT each miss | Medium/high | **Yes** | Yes | **Good simple long-term design** |
| S3 snapshot → local SQLite/packfile | Download a few large objects, then purely local lookups | High | Needs delta design | Yes | **Potential fastest warm build** |
| S3 Express One Zone | Low-latency individual object requests | Medium | Yes | Yes | Interesting if AZ-local |
| DynamoDB | One key/value request per lookup | High | Yes | Yes | Technically viable, poor fit |
| ElastiCache/Valkey | Memory-speed remote lookups | High | Cache semantics | Yes | Likely economically excessive |
| Fargate + EBS | Block filesystem | Medium | Awkward between tasks | Poor | Weak fit |

### 1. S3 Files — I would evaluate this before implementing custom sync

This is the biggest omission in the document. Amazon now supports **S3 Files volumes directly on ECS Fargate**. AWS describes S3 Files as a persistent, high-performance file system giving containers cached filesystem access to S3-backed data. citeturn336007view1turn365838search2turn365838search8

Its behavior is unusually well aligned with this exact cache. On first access to a directory, S3 Files imports directory metadata and, by default, also caches file contents smaller than **128 KiB**. Your cache objects are described as roughly 6–20 KB, so they fall squarely into that path. Unused cached data can later expire from the high-performance tier while remaining durable in S3. citeturn365838search1turn365838search6

Even more important, filesystem writes are immediately durable on S3 Files' high-performance storage and are subsequently exported to the linked S3 bucket. AWS currently uses a 60-second write-inactivity window to aggregate changes before copying them to S3. That removes the document's “task died before sync-on-end” failure mode. citeturn365838search0turn365838search3

Architecturally it could be almost trivial:

```text
S3 bucket
    ↕ automatic synchronization
Amazon S3 Files
    ↕ ECS volume mount
/mnt/embed-cache
    ↕
execution.FileCache
```

`CachedEmbedder` and potentially even `FileCache` remain completely unchanged.

There are caveats. S3 Files requires bucket versioning, meters filesystem operations with a 32-KiB minimum, and its backing-S3 rename operation is ultimately copy+delete because S3 has no atomic object rename. citeturn365838search1turn365838search9 That makes one test especially important: Flowkit's temp-file → `fsync` → rename `Store` implementation should be exercised under S3 Files before adoption. The filesystem exposes the semantics the application expects, but you should inspect resulting S3 object/version behavior too.

It also does **not** meet the literal requirement “cache reads hit local disk.” It is a network-mounted high-performance cache. I would change the requirement from a mechanism to an outcome: e.g. “warm cache access must not materially dominate build wall time.”

### 2. Direct S3 cache with a local L1

This is a stronger version of Strategy B.

`Load` would do:

```text
local ephemeral cache
        ↓ miss
S3 GET <digest>.json
        ↓ hit
validate envelope
        ↓
populate local L1
```

`Store` would write the local cache and immediately persist the object remotely. S3 is strongly read-after-write consistent. citeturn575501search1

For general-purpose S3 buckets, I would use conditional writes:

```http
If-None-Match: *
```

S3 supports this specifically to prevent overwriting an existing key. citeturn575501search0turn575501search6 That gives the content-addressed cache a much stronger invariant than “last writer happens to produce the same bytes”:

```text
missing → first successful writer owns the key
existing → immutable
```

That makes concurrency reasoning much cleaner.

The downside is important for CoinVault: if every warm build checks all 114k entries, lazy retrieval still means roughly 114k S3 GETs per fresh Fargate task. S3 can sustain high parallel request rates, especially with your hash-sharded prefixes, but you'd be converting filesystem latency into object-request latency rather than eliminating remote operations. citeturn638035search5

So I prefer this when builds inspect only part of the corpus, or as the persistent L2 beneath another cache.

### 3. S3 snapshot + local SQLite — worth serious consideration

The document currently dismisses SQLite because of SQLite-over-NFS concerns. That conclusion is correct **for EFS**. SQLite explicitly says WAL does not work across a network filesystem and advises against network filesystems where locking cannot be trusted. citeturn700735search0turn700735search3

But the architecture can instead be:

```text
S3:
  cache-snapshot.sqlite.zst
  delta/<digest>.json
           |
           | one/few large GETs
           v
Fargate ephemeral NVMe:
  cache.sqlite
           |
           v
CachedEmbedder
```

Then SQLite itself lives entirely on `/scratch`, not EFS.

This has an important workload advantage: instead of 114k S3 GETs and 114k local JSON opens, startup could download **one compressed database object**, after which all cache lookups are local indexed reads.

You could even make the snapshot immutable/read-only and collect new values separately:

```text
base.sqlite       immutable snapshot
delta.sqlite      entries created by this build
```

At completion, new values are uploaded as loose content-addressed objects. A separate compaction operation periodically produces a new immutable SQLite snapshot.

That is more engineering than Strategy A, but if the cache reaches millions of entries, I think this is a substantially more promising scaling path than copying millions of tiny files.

### 4. Compact S3 packfiles without SQLite

A variation is to retain the JSON envelope format but package objects into larger immutable shards:

```text
packs/00.pack
packs/00.idx
packs/01.pack
packs/01.idx
...
packs/ff.pack
```

The index maps:

```text
digest → pack object + byte offset + length
```

S3 supports byte-range GETs, so entries can be retrieved from large objects without fetching each complete pack. citeturn575501search23

For a full warm build, just download all 256 packs in parallel. For a partial build, use range GETs.

This gives excellent object-storage behavior but creates a custom file format and compaction protocol. I'd rank SQLite above it unless profiling demonstrates a reason to own that complexity.

### 5. S3 Express One Zone

S3 Express One Zone provides single-digit-millisecond object access and is designed for latency-sensitive workloads when storage and compute can be placed in the same AZ. citeturn365838search12turn889931search9

A direct `S3Cache` against Express therefore becomes more plausible than direct S3 Standard.

But there is a relevant semantic tradeoff: S3's `PutObject If-None-Match` conditional-write facility is documented as unsupported for directory buckets. citeturn575501search0 You would therefore need a different immutability/concurrency approach.

Because this cache is regenerable, single-AZ durability is not inherently disqualifying. The bigger issue is operational: ECS placement has to line up with the directory bucket's AZ to realize the performance benefit.

I would test it only after S3 Files/direct Standard S3.

### 6. EBS on Fargate

EBS is now supported by Linux Fargate tasks. citeturn336007view0 It initially sounds ideal: filesystem semantics, durable block storage, no 114k-object S3 traversal.

But ECS's current integration requires **a new EBS volume for each task**; an existing volume cannot simply be attached. You can seed a new volume from a snapshot. citeturn336007view0

That turns the architecture into:

```text
snapshot → new volume → task → somehow make new snapshot
```

which is substantially more lifecycle machinery than S3 and does not naturally solve cross-environment sharing. I would drop it from serious consideration.

### 7. DynamoDB / ElastiCache

DynamoDB can technically hold these entries: its item limit is 400 KB, well above the document's 6–20 KB cache-entry size. citeturn638035search11 But it adds a database abstraction, capacity/request economics, serialization, and 114k key requests per full warm build without solving the fundamental “bulk working set” observation.

ElastiCache would provide excellent request latency, but you're paying for a continuously available memory cache to accelerate a build-time cache that already has a cheap durable backing option. AWS itself positions ElastiCache as a way to cache repeatedly requested S3 data, but that seems justified here only if builds become extremely frequent. citeturn638035search33

## Recommended architecture direction

I would change the decision record from:

> Strategy A first, Strategy B later.

to:

**Benchmark S3 Files first; keep sync-to-ephemeral as the control implementation; implement direct S3 or snapshot storage only if neither meets the wall-time target.**

The experiment should compare the same 114,106-entry cache under five modes:

| Mode | What it answers |
|---|---|
| EFS `FileCache` | Current baseline |
| S3 sync → `/scratch` | How much does true local NVMe help? |
| **S3 Files → `FileCache`** | Can managed cached filesystem access remove the need for custom synchronization? |
| Direct parallel S3 GET + local L1 | Is object storage itself fast enough? |
| S3 snapshot → local SQLite | What is the achievable lower bound when remote small-object operations disappear? |

Measure total cache-stage wall time, task startup-to-first-embedding time, p50/p95 `Load`, number of S3/file operations, bytes transferred, cold versus warm behavior, two simultaneous builds, new-entry persistence after forced task termination, and resulting storage/request cost.

If **S3 Files is within roughly the same performance envelope as local ephemeral storage**, I'd choose it. It eliminates most of Phases 1, 2, and 4 of the current proposal, preserves `FileCache`, removes explicit start/end synchronization, and persists writes without depending on graceful task completion. Its Fargate integration is now a first-class ECS storage option. citeturn336007view1turn365838search2

If it is materially slower, I would choose **S3 snapshot → local SQLite plus content-addressed S3 deltas** over scaling `aws s3 sync` indefinitely. The current sync design is reasonable at 114k objects, but the document itself anticipates cache growth; object count rather than the current 2.2 GB size is likely to become its limiting dimension. fileciteturn0file0L398-L404

Finally, I would make the canonical durable key space **environment-independent**. Dev/prod separation should be an authorization or promotion concern, not part of the content identity, if “embed once, reuse everywhere” is actually a requirement. The current design explicitly postpones the outcome it says the ticket must deliver. fileciteturn0file0L75-L81

