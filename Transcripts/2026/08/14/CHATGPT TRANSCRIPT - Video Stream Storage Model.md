# Video Stream Storage Model

- URL: https://chatgpt.com/c/6a7f3d16-8850-83ea-b3e4-9986b19dbdb4
- Created: 2026-08-14T16:07:01.321Z

---

> i am streaming in video , storing it to disk (break up streams, caching, hierarchy for handling easily cyclical buffer storage, months of storage, i need to maintain caches that I don't want to recompute thumbnails, redacted versions, processed outputs), then i want to run on kubernetes, with longhorn block storage, can have different classes of retention strategy, maybe storing data differently between metadata and cached data vs raw data.
>
> Break this down to mathematical concepts in order to create a core composable systems that can then be expanded.

I’d model this from first principles rather than from Kubernetes or Longhorn. The core should define **time, identity, derivation, retention, placement, and invariants**; Kubernetes then becomes one execution/placement backend.

<details><summary>💭 Thinking</summary>

**Structuring the architecture**

I’m organizing the system around time-indexed chunks, layered object identities, a deterministic derivation DAG, and policy-driven retention. I’m separating logical identity from content hashes so redactions, restarts, and transcodes remain manageable.

**Structured the architecture**

**Refining storage behavior**

I’m adding hot and warm execution storage, generation-aware ring buffers, and dependency-aware eviction. The design separates immutable data from authoritative metadata, using staged writes and explicit object states to support crash recovery without distributed transactions.

**Refined storage behavior**

</details>

The clean abstraction is to treat the entire system as a **time-indexed immutable object graph with lifecycle policies**.

Kubernetes, Longhorn, codecs, GPUs, filesystems, etc. should sit below that model.

## 1. Start with time as the fundamental coordinate

A camera produces a function of time:

$$
S : t \rightarrow \text{bytes}
$$

You don't want to store an infinite stream, so partition time into intervals:

$$
I_k = [t_k,t_{k+1})
$$

and define:

$$
C_k = S|_{I_k}
$$

where $C_k$ is one immutable video segment.

For fixed-duration segmentation:

$$
t_k = t_0 + k\Delta
$$

For example, $\Delta=10$ seconds.

Your first core primitive becomes:

```text
Segment {
    stream_id
    epoch
    sequence
    start_time
    end_time
    content_hash
    size
}
```

`epoch` matters because cameras restart, clocks jump, streams disconnect, etc.

So logical time becomes:

$$
(\text{stream},\text{epoch},\text{sequence})
$$

rather than relying solely on wall-clock timestamps.

This gives you the first invariant:

> **Once committed, a segment never changes.**

Everything else becomes substantially easier if this is true.

---

# 2. Separate logical identity from physical location

Do not make:

```text
/longhorn/camera17/2026/08/14/foo.mp4
```

the identity of the video.

Instead:

$$
\text{ObjectID} \neq \text{StorageLocation}
$$

For example:

```text
ObjectID = sha256(bytes)
```

or:

```text
ObjectID = (stream_id, epoch, sequence, version)
```

Usually you want both.

```text
logical_id  = (camera17, epoch42, segment9281)
content_id  = SHA256(bytes)
```

Then maintain:

$$
\text{Location}: ObjectID \rightarrow \{L_1,L_2,\ldots,L_n\}
$$

An object could therefore exist:

```text
Object abc123
   ├── /hot-volume/...
   ├── /longhorn-volume/...
   └── archive/object-store/...
```

without changing its identity.

This is critical for migrating between storage classes.

---

# 3. Model everything as an object

Don't fundamentally distinguish:

- raw video
- thumbnail
- redacted video
- transcoded video
- detection output
- metadata snapshot

at the storage layer.

They are all:

$$
O=(id,type,time,lineage,properties)
$$

For example:

```text
Object {
    id
    type

    stream_id
    time_range

    content_hash
    byte_size

    lineage
    retention_policy
    durability_policy
}
```

Types might be:

```text
RAW_SEGMENT
THUMBNAIL
REDACTED_SEGMENT
TRANSCODE
DETECTION_RESULT
MANIFEST
```

This is essentially an **algebraic data type**:

$$
Object =
Raw
\;|\;
Thumbnail
\;|\;
Redacted
\;|\;
Metadata
\;|\;\cdots
$$

That lets the storage machinery operate independently of the object type.

---

# 4. Treat processing as a DAG

This is probably the most important abstraction for your cache problem.

Suppose:

$$
R = \text{raw video}
$$

Then:

$$
T=f_{\text{thumbnail}}(R)
$$

$$
D=f_{\text{detect}}(R)
$$

$$
X=f_{\text{redact}}(R,D)
$$

Your system is a directed acyclic graph:

```text
                 ┌── thumbnail
                 │
raw segment ─────┼── detections
                 │       │
                 │       ▼
                 └──── redacted video
```

Mathematically:

$$
G=(V,E)
$$

where objects are vertices and derivation relationships are edges.

This should be explicitly stored as **lineage**.

For example:

```text
redacted123:
    function: redact
    inputs:
        - raw123
        - detections882
```

Now your storage system understands the difference between:

> "I have this file."

and:

> "I know exactly how this file came into existence."

---

# 5. Make computation itself content-addressable

You said:

> I don't want to recompute thumbnails, redacted versions, processed outputs.

Instead of asking:

```text
does thumbnail.jpg exist?
```

define the identity of a computation:

$$
K =
H(
f,
version(f),
parameters,
H(input_1),
\dots,
H(input_n)
)
$$

For example:

```text
thumbnail_key = hash(
    "thumbnail",
    "algorithm-v7",
    {"width": 512, "time": 3.2},
    raw_segment_hash
)
```

Then:

$$
Cache : K \rightarrow ObjectID
$$

This gives you **memoization at distributed-system scale**.

If:

```text
thumbnail(raw=A, width=512, algorithm=v7)
```

has already been computed, no Kubernetes pod needs to recompute it.

Change the implementation to `v8`, and naturally:

$$
K_{v7} \neq K_{v8}
$$

so cache invalidation falls naturally out of the identity model.

This removes a huge amount of cache-management complexity.

---

# 6. "Cache" should be a property, not a storage system

A thumbnail isn't intrinsically a cache.

It has properties such as:

$$
recomputable(o) \in \{true,false\}
$$

$$
cost_{compute}(o) \in \mathbb{R}_{\ge0}
$$

$$
cost_{storage}(o) \in \mathbb{R}_{\ge0}
$$

You can then ask:

$$
\text{Should I keep this artifact?}
$$

based on something like:

$$
V(o)
=
P(\text{reuse})
\times C_{\text{compute}}
-
C_{\text{storage}}
$$

A 30-byte JSON result that's expensive to compute should almost certainly be cached forever.

A 5 GB derived video that takes 100 ms to regenerate probably shouldn't.

So don't create a fixed architectural category called "the cache."

Instead let:

> **Cacheability and eviction be policy applied to immutable derived objects.**

---

# 7. Model retention independently from storage location

This distinction is essential.

Define:

$$
RetentionPolicy(o,t) \rightarrow \{keep,expire\}
$$

Separately define:

$$
PlacementPolicy(o,t) \rightarrow StorageTier
$$

Then "how long should it exist?" and "where should it live?" become separate questions.

For example:

```text
raw-video:
    retention: 90 days

thumbnail:
    retention: 365 days

metadata:
    retention: forever

redacted-video:
    retention: 3 years
```

While placement could independently be:

```text
age < 24h       -> hot
age < 30d       -> warm
age < 90d       -> cold
age >= 90d      -> archive/delete
```

Thus:

$$
Retention \perp Placement
$$

They are orthogonal dimensions.

That will save you from a lot of architectural pain later.

---

# 8. Model retention as a policy algebra

This becomes particularly useful once requirements pile up.

Suppose an object has:

```text
customer retention: 30 days
incident retention: 180 days
legal retention: 7 years
```

The effective retention deadline is simply:

$$
R(o)=\max(R_1(o),R_2(o),\dots,R_n(o))
$$

This is a **join operation** from lattice theory.

Similarly durability could have an ordering:

$$
D_0 < D_1 < D_2 < D_3
$$

where perhaps:

```text
D0 = disposable
D1 = locally recoverable
D2 = replicated
D3 = geographically durable
```

Then:

$$
D(o)=\max(D_{\text{cache}},D_{\text{customer}},D_{\text{legal}})
$$

This means independent components can add requirements without knowing about one another.

For example:

```text
base policy:
    retention = 30d
    durability = replicated

incident:
    retention >= 1y

legal hold:
    retention >= indefinitely
    durability >= archival
```

The policies **compose**.

This is a very useful mathematical foundation for a large system.

---

# 9. Your cyclic buffer is modular arithmetic

For a live buffer of $N$ slots:

$$
slot(k)=k\bmod N
$$

If each segment represents $\Delta$ seconds and you want $T$ seconds buffered:

$$
N =
\left\lceil
\frac{T}{\Delta}
\right\rceil
$$

For example:

$$
T=3600s,\quad \Delta=10s
$$

gives:

$$
N=360
$$

slots.

But **never identify an object purely by its slot number**.

Otherwise:

```text
slot 42
```

today is indistinguishable from slot 42 an hour later.

Use:

$$
SlotID=(slot,generation)
$$

where:

$$
generation =
\left\lfloor
\frac{k}{N}
\right\rfloor
$$

Thus:

```text
(42, 871)
```

and

```text
(42, 872)
```

are different objects despite occupying the same physical space.

This eliminates a class of race conditions sometimes described as the **ABA problem**.

---

# 10. Overwriting a circular buffer becomes a predicate

Instead of:

> overwrite slot 42 because the pointer wrapped

define:

$$
CanReuse(slot)=
Expired(slot)
\land
NotPinned(slot)
\land
NotReferenced(slot)
$$

Potentially:

$$
CanReuse
=
retentionExpired
\land leaseCount=0
\land legalHold=false
$$

Your cyclic buffer is therefore just a special storage allocator.

The object model doesn't know that its physical backing happens to wrap around.

That's a good abstraction boundary.

---

# 11. Use hierarchical time aggregation

You don't want one flat namespace containing billions of segments.

Build a hierarchy:

```text
Stream
 └── Day
      └── Hour
           └── Minute
                └── Segment
```

Mathematically this is a tree over nested intervals:

$$
I_{segment}
\subset
I_{minute}
\subset
I_{hour}
\subset
I_{day}
$$

A manifest might contain:

```text
HourManifest
    start: 12:00
    end:   13:00

    children:
       segment-001
       segment-002
       ...
```

Then:

```text
DayManifest
    children:
       hour-00
       hour-01
       ...
```

This gives you cheap operations such as:

```text
delete day
replicate hour
pin event
move month
verify camera/day
```

without enumerating every video frame.

---

# 12. Make the hierarchy a Merkle DAG

A particularly powerful extension is:

$$
H(parent)=
H(
H(child_1)
\Vert
H(child_2)
\Vert \dots
)
$$

Then:

```text
Day hash
 ├── Hour hash
 │    ├── Segment hash
 │    ├── Segment hash
 │    └── Segment hash
 └── Hour hash
```

This is a Merkle tree/DAG.

It gives you:

- integrity verification
- deduplication
- efficient replication comparison
- immutable manifests
- easy detection of corruption
- deterministic snapshots

Git is based on roughly this type of idea.

It's a very natural model for immutable video archives.

---

# 13. Metadata and bytes should have radically different semantics

You mentioned metadata vs cached data vs raw data.

They should not merely have different directories.

They have fundamentally different mathematical properties.

### Metadata

Small:

$$
Size \ll Video
$$

Frequently mutated.

Needs:

- indexing
- transactions
- queries
- consistency

Think relational database / key-value database.

### Video/artifacts

Huge.

Almost entirely:

$$
WriteOnceReadMany
$$

So use immutable blob semantics.

The DB might store:

```text
object_id
type
stream
time_start
time_end
hash
size

retention
durability
storage_locations

parent_dependencies
processing_key
```

while video bytes exist independently.

This creates:

```text
CONTROL PLANE
    metadata DB

DATA PLANE
    immutable blobs
```

This separation is extremely useful.

---

# 14. Have a tiny object state machine

Don't give an object dozens of procedural states.

Something along these lines is enough:

$$
Staged
\rightarrow
Committed
\rightarrow
Expired
\rightarrow
Deleted
$$

Potentially:

```text
          ┌───────────┐
          │  STAGED   │
          └─────┬─────┘
                │
                ▼
          ┌───────────┐
          │ COMMITTED │
          └─────┬─────┘
                │
                ▼
          ┌───────────┐
          │  EXPIRED  │
          └─────┬─────┘
                │
                ▼
          ┌───────────┐
          │  DELETED  │
          └───────────┘
```

Important invariant:

$$
Committed(o)
\implies
BytesExist(o)
$$

A typical write operation is therefore:

1. Write bytes to staging.
2. Finish/fsync them.
3. Calculate hash.
4. Atomically expose immutable object.
5. Commit metadata.

A crash before step 5 leaves an orphan, which a garbage collector can remove.

That's much easier than trying to make a database and filesystem participate in one distributed transaction.

---

# 15. Derivation gives you dependency-aware garbage collection

Suppose:

```text
raw-A
  │
  ├── thumbnail-B
  │
  └── detection-C
          │
          └── redacted-D
```

The lineage graph lets garbage collection reason about consequences.

For every object define:

$$
Recoverability(o)
$$

Examples:

```text
raw:
    recoverability = impossible

thumbnail:
    recoverability = cheap(raw)

detections:
    recoverability = expensive(raw, gpu)

redacted:
    recoverability = expensive(raw, detections)
```

If `raw-A` is about to disappear, the system can know:

> `thumbnail-B` is technically derived, but after A disappears B is no longer reproducible.

That's an important distinction.

So I'd explicitly model:

```text
is_required
is_recomputable_now
recompute_cost
```

rather than simply:

```text
is_cache
```

---

# 16. Processing becomes pure functions wherever possible

Aim for:

$$
output=f(inputs,parameters,codeVersion)
$$

rather than:

```text
processor:
    reads arbitrary disk state
    mutates arbitrary files
```

This is the functional-programming part of the architecture.

For example:

```text
redact(
    video_hash,
    detections_hash,
    policy_hash,
    software_version
) -> redacted_hash
```

This yields:

- deterministic caching
- easy retries
- simple Kubernetes jobs
- provenance
- reproducibility
- parallel execution

---

# 17. Idempotency handles Kubernetes retries

Kubernetes and distributed queues should be assumed to provide **at-least-once execution**.

Therefore:

$$
Job(JobKey)
$$

might run:

$$
1,2,3,\ldots
$$

times.

But you want:

$$
Effect(JobKey)=1
$$

You get this by making the computation key deterministic.

```text
JobKey =
    hash(function + version + parameters + inputs)
```

Workers can race:

```text
worker A ─┐
worker B ─┼── compute K
worker C ─┘
```

but publication is:

```text
put-if-absent(K, result)
```

The winning result becomes authoritative.

Thus:

$$
at\text{-}least\text{-}once
+
idempotency
\approx
exactly\text{-}once\ effect
$$

This is far more robust than trying to achieve true exactly-once execution.

---

# 18. Separate ownership from durability

This matters once Longhorn/Kubernetes enters the picture.

Think of each stream as having a writer:

$$
Owner(stream)=worker
$$

You might shard:

$$
shard(stream)=H(streamID)\bmod N
$$

Then:

```text
shard-0
    cameras 7, 22, 48...

shard-1
    cameras 3, 19, 97...
```

Only one logical writer owns each stream/shard at any instant.

Processors don't own the video stream. They consume immutable objects.

So the topology becomes:

```text
                    Kubernetes
                        │
              ┌─────────┴──────────┐
              │                    │
        ingestion workers     processors
              │                    │
              ▼                    ▼
       immutable segments    derived objects
              │                    │
              └────────┬───────────┘
                       ▼
                 storage layer

                       │
                       ▼
                 metadata DB
```

This keeps distributed locking out of most of your system.

---

# 19. Treat Longhorn as one implementation of a storage tier

At the core level you want something like:

$$
StorageBackend
$$

with operations approximately:

```text
put(object)
get(object)
exists(object)
delete(object)
list(...)
```

Then define:

```text
Tier HOT
Tier WARM
Tier ARCHIVE
```

For example:

```text
HOT
    local NVMe

WARM
    Longhorn-backed storage

ARCHIVE
    object/archive storage
```

or all three could initially be Longhorn volumes with different characteristics.

The important part is:

$$
Object model
\not\equiv
Longhorn model
$$

This allows storage topology to evolve without changing your processing architecture.

---

# 20. Placement becomes an optimization problem

For object $o$ and storage tier $s$, define:

$$
Cost(o,s)
=
\alpha L(o,s)
+
\beta S(o,s)
+
\gamma R(o,s)
+
\delta M(o,s)
$$

where:

- $L$ = expected access latency
- $S$ = storage cost
- $R$ = loss/risk cost
- $M$ = migration/recomputation cost

Then:

$$
Placement(o)
=
\arg\min_s Cost(o,s)
$$

subject to constraints such as:

$$
durability(s)\ge durabilityRequired(o)
$$

and:

$$
capacity(s)\ge size(o)
$$

You don't need to literally run an optimizer initially.

But designing the system as though this were the decision being made is useful.

A simple implementation can be:

```text
if age < 24h:
    HOT

elif age < 30d:
    WARM

else:
    COLD
```

without contaminating the underlying object model.

---

# 21. Capacity becomes basic dimensional analysis

For bitrate $b$:

$$
Storage =
bitrate\times time
$$

For $n$ cameras:

$$
Storage =
n b T
$$

With replication $r$:

$$
PhysicalStorage
\approx
nbrT
$$

Then introduce overhead:

$$
PhysicalStorage
=
nbrT(1+\epsilon)
$$

where $\epsilon$ includes:

- filesystem overhead
- manifests
- thumbnails
- derived outputs
- replication/snapshot overhead
- free-space safety margin

This simple equation should be present everywhere in capacity planning.

At $8\text{ Mbps}$, for example:

$$
8\text{ Mbps}\approx1\text{ MB/s}
$$

so one camera produces roughly:

$$
86.4\text{ GB/day}
$$

before accounting for replication and derived artifacts.

That makes the architecture's economics immediately apparent.

---

# 22. Four orthogonal dimensions are enough for most policies

I'd make every object carry four conceptual properties:

$$
O=(I,L,R,D)
$$

where:

### $I$: Identity

What is this?

```text
hash
stream
time
type
```

### $L$: Lineage

Where did it come from?

```text
inputs
function
parameters
software version
```

### $R$: Retention

How long must it continue to exist?

```text
expires_at
legal_hold
importance
```

### $D$: Durability

How hard must we try not to lose it?

```text
disposable
recoverable
replicated
archival
```

Then storage placement is derived from those properties rather than embedded in them.

---

# 23. Add access temperature as a fifth dimension

Eventually:

$$
A(o)=\text{expected future access rate}
$$

You can estimate something like:

$$
A(o,t)
=
f(
age,
recentReads,
eventImportance,
customerActivity
)
$$

So the full conceptual object might be:

$$
O=(I,L,R,D,A)
$$

This naturally handles:

```text
raw video from 10 minutes ago:
    high A

raw video from 85 days ago:
    low A

thumbnail from incident:
    high A

ordinary thumbnail from 85 days ago:
    very low A
```

Again:

> access temperature determines placement, not identity.

---

# 24. You can express the entire platform as six composable systems

I'd draw your core architecture as this:

```text
                        VIDEO STREAM
                             │
                             ▼
                  ┌────────────────────┐
                  │ 1. TIME PARTITION  │
                  │ stream → segments  │
                  └─────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ 2. OBJECT SYSTEM    │
                 │ immutable identity  │
                 └─────────┬───────────┘
                           │
                 ┌─────────┴───────────┐
                 ▼                     ▼
       ┌───────────────────┐   ┌───────────────────┐
       │ 3. LINEAGE GRAPH  │   │ 4. POLICY ALGEBRA│
       │ derived artifacts │   │ retention        │
       │ processing/cache  │   │ durability       │
       └─────────┬─────────┘   └─────────┬─────────┘
                 │                       │
                 └───────────┬───────────┘
                             ▼
                  ┌──────────────────────┐
                  │ 5. PLACEMENT SYSTEM │
                  │ hot/warm/cold       │
                  │ cyclic/persistent   │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │ 6. EXECUTION SYSTEM │
                  │ Kubernetes          │
                  │ workers / retries   │
                  │ migrations / GC     │
                  └──────────────────────┘
```

The critical dependency direction is:

$$
Execution
\rightarrow Placement
\rightarrow Policy/Object
$$

not:

$$
Object semantics
\rightarrow Kubernetes PVC details
$$

---

# 25. A concrete minimal model

If I were building this, I'd start with something surprisingly small:

```text
Object
{
    object_id
    content_hash

    type

    stream_id
    epoch

    time_start
    time_end

    byte_size

    computation_key?

    created_at
}
```

Then:

```text
Dependency
{
    child_object
    parent_object
}
```

Then:

```text
Location
{
    object_id
    backend
    location

    state
    verified_at
}
```

Then:

```text
Policy
{
    object_id

    retain_until
    durability_level
    access_class

    pinned
}
```

And:

```text
Computation
{
    computation_key

    operation
    version
    parameters_hash

    input_objects[]
    output_objects[]
}
```

Notice how little of this knows anything about video.

That's a desirable property.

---

# 26. Then build higher-level concepts by composition

A **ring buffer** becomes:

$$
Objects
+
finite\ capacity
+
age\ eviction
+
modular\ allocator
$$

A **video archive** becomes:

$$
Objects
+
time\ manifests
+
long\ retention
$$

A **thumbnail cache** becomes:

$$
Objects
+
lineage
+
computation\ keys
+
eviction
$$

A **redacted archive** becomes:

$$
Objects
+
lineage
+
strong\ retention
+
strong\ durability
$$

A **Kubernetes processing pipeline** becomes:

$$
ComputationGraph
+
idempotent\ jobs
+
leases
$$

A **storage tiering system** becomes:

$$
PlacementPolicy
+
ObjectLocations
+
migration
$$

These are all combinations of the same small number of primitives.

---

# 27. The mathematical concepts I'd use as the intellectual foundation

In roughly this order:

1. **Discrete time / interval partitioning** — convert streams into finite objects.
2. **Modular arithmetic** — cyclic storage and bounded buffers.
3. **Immutable values and hashing** — stable object identity.
4. **Trees and Merkle DAGs** — temporal hierarchy and integrity.
5. **Directed acyclic graphs** — processing lineage.
6. **Pure functions and memoization** — derived-artifact caching.
7. **Finite-state machines** — object lifecycle.
8. **Lattices / partial orders** — composable retention and durability requirements.
9. **Graph reachability** — dependency-aware garbage collection.
10. **Queueing theory** — processing throughput and backlog.
11. **Optimization / cost functions** — hot/warm/cold placement.
12. **Probability** — access prediction, failure risk and cache value.
13. **Consistent hashing / partitioning** — distribute streams among nodes.
14. **Idempotency / algebraic properties** — safe distributed retries.

You don't need all of the sophisticated versions initially. The main benefit is that these abstractions give you clean boundaries.

---

## One especially useful way to think about the whole system

There are really only three kinds of information:

```text
SOURCE
    Irreplaceable observations.
    Example: raw camera video.

DERIVED
    f(source/data)
    Example: thumbnails, detections, redaction.

METADATA
    Knowledge about source and derived objects.
    Example: indexes, timestamps, lineage, policy.
```

Their economics differ:

$$
Value(source)
\approx
cost\ of\ losing\ observation
$$

$$
Value(derived)
\approx
cost\ of\ recomputation
+
cost\ of\ losing\ reproducibility
$$

$$
Value(metadata)
\approx
cost\ of\ losing\ the\ ability\ to\ understand\ everything\ else
$$

This naturally suggests very different durability policies for each.

The core design principle I'd adopt is:

> **Store immutable observations and derived values; store their relationships and policies as metadata; make placement and computation consequences of that metadata.**

Once that exists, Longhorn volumes, Kubernetes nodes, local NVMe ring buffers, future object storage, GPU processors, archival tiers, and additional retention classes become replaceable implementations around a stable mathematical core.


---

> Now create a nice JS API for the system

<details><summary>💭 Thinking</summary>

**Designing the API**

I’m shaping a composable JavaScript API around streams, temporal segments, derived data, manifests, policies, placement, and verification. I’m keeping operations immutable where practical, with fluent builders and explicit versioning for reproducibility.

**Designed the API**

</details>

I’d make the public API **object-centric and declarative**: applications describe streams, derivations, policies, and storage intent; adapters handle Longhorn/Kubernetes specifics. The core API should remain usable in a single-process local deployment.

Two API choices matter here: **artifact references should be plain serializable values**, and **transforms should be declarative definitions, not closures shipped to Kubernetes**. That makes computation keys stable and lets local workers and Kubernetes workers implement the same transform contract.

I’d make it feel like an **immutable media database + build system**. The caller should mostly say what an artifact is, how it derives from others, and what policy applies—not manually move files around.

The examples below are plain modern JavaScript; a real package should ship TypeScript declarations alongside it.

## 1. Top-level API

```js
import {
  createMediaSystem,

  policy,
  retain,
  durability,
  placement,

  defineTransform,

  time,
  ring,
} from "@video/core";

import {
  postgresCatalog,
  filesystemStore,
} from "@video/storage";

import {
  kubernetesExecutor,
} from "@video/kubernetes";
```

Then initialization:

```js
const media = createMediaSystem({
  catalog: postgresCatalog({
    url: process.env.DATABASE_URL,
  }),

  stores: {
    hot: filesystemStore({
      path: "/storage/hot",
      traits: {
        latency: "hot",
        durability: "node",
      },
    }),

    warm: filesystemStore({
      // A Longhorn-backed PVC mounted here.
      path: "/storage/warm",
      traits: {
        latency: "warm",
        durability: "replicated",
      },
    }),

    archive: filesystemStore({
      path: "/storage/archive",
      traits: {
        latency: "cold",
        durability: "archival",
      },
    }),
  },

  executor: kubernetesExecutor({
    namespace: "video-processing",
  }),
});
```

The important architectural point is that **Longhorn is not part of the object model**.

To the core, `/storage/warm` is simply a store with certain properties.

---

# 2. Define policies compositionally

Raw video:

```js
const rawPolicy = policy(
  retain.for("90d"),

  durability.atLeast("replicated"),

  placement.lifecycle([
    {
      untilAge: "2h",
      keep: {
        hot: 1,
        warm: 1,
      },
    },
    {
      untilAge: "30d",
      keep: {
        warm: 1,
      },
    },
    {
      untilAge: "90d",
      keep: {
        archive: 1,
      },
    },
  ]),
);
```

Thumbnails:

```js
const thumbnailPolicy = policy(
  retain.for("1y"),

  durability.atLeast("recoverable"),

  placement.prefer("warm", "archive"),
);
```

Metadata-like derived results:

```js
const detectionPolicy = policy(
  retain.forever(),

  durability.atLeast("replicated"),

  placement.prefer("warm"),
);
```

And policies compose:

```js
const incidentPolicy = policy(
  retain.atLeast("1y"),
  durability.atLeast("archival"),
);

const effective = policy.join(
  rawPolicy,
  incidentPolicy,
);
```

Semantically:

```text
retention = max(all retention requirements)
durability = max(all durability requirements)
placement = conjunction of placement constraints/preferences
```

A legal hold becomes another overlay:

```js
const legalHold = policy(
  retain.hold("case-92817"),
  durability.atLeast("archival"),
);

await media.policies.attach(
  artifact.id,
  legalHold,
);
```

Release it later:

```js
await media.policies.releaseHold(
  "case-92817",
);
```

---

# 3. Streams are logical identities

```js
const camera = media.stream("camera/front-door");
```

That doesn't open a file.

It identifies:

$$
stream = camera/front-door
$$

Create an epoch when ingestion starts:

```js
const epoch = await camera.beginEpoch({
  source: {
    protocol: "rtsp",
    camera: "front-door",
  },
});
```

The API generates an epoch ID:

```js
epoch.id
// "01K2C..."
```

So segments are naturally identified by:

```text
(stream, epoch, sequence)
```

---

# 4. Writing immutable video segments

If your streaming layer already gives you segmented video:

```js
const segment = await epoch.commitSegment({
  sequence: 9281,

  interval: time.range(
    "2026-08-14T16:10:00.000Z",
    "2026-08-14T16:10:10.000Z",
  ),

  body: videoBuffer,

  type: "video/h264",

  metadata: {
    codec: "h264",
    width: 1920,
    height: 1080,
    keyframe: true,
  },

  policy: rawPolicy,
});
```

Returned value:

```js
{
  id: "obj_01K2...",
  hash: "sha256:f714...",
  type: "video/h264",

  stream: "camera/front-door",
  epoch: "01K2C...",
  sequence: 9281,

  interval: {
    start: "2026-08-14T16:10:00.000Z",
    end: "2026-08-14T16:10:10.000Z"
  },

  size: 10_381_992
}
```

This object is immutable.

There is deliberately no:

```js
segment.filename
```

because a segment may have:

```text
0, 1, 2, 3...
```

physical locations.

---

# 5. Physical locations are separate

You can inspect them:

```js
await media.storage.locations(segment);
```

Result:

```js
[
  {
    store: "hot",
    state: "ready",
    path: "ring/17/42/871",
  },
  {
    store: "warm",
    state: "ready",
    path: "objects/f7/14/f714...",
  },
]
```

The logical artifact didn't change when the warm replica appeared.

You generally don't move files manually.

You ask the reconciler to make reality satisfy policy:

```js
await media.storage.reconcile(segment);
```

Or run it continuously:

```js
for await (const action of media.storage.reconcileAll()) {
  console.log(action);
}
```

Possible actions:

```js
{
  action: "copy",
  artifact: "obj_123",
  from: "hot",
  to: "warm"
}
```

or:

```js
{
  action: "drop-replica",
  artifact: "obj_123",
  store: "hot"
}
```

---

# 6. Ring storage is an allocator, not retention

This distinction should appear directly in the API.

```js
const liveRing = ring({
  store: "hot",

  horizon: "2h",
  segmentDuration: "10s",

  reuseWhen: async artifact => {
    return media.storage.canDropReplica(
      artifact,
      "hot",
    );
  },
});
```

Use it for ingestion:

```js
const epoch = await camera.beginEpoch({
  allocator: liveRing,
});
```

Internally:

$$
slot(k)=k\bmod N
$$

but that doesn't leak into artifact identity.

A slot might physically look like:

```js
{
  slot: 42,
  generation: 871,
}
```

When the ring wraps:

```js
{
  slot: 42,
  generation: 872,
}
```

Same physical slot.

Different storage generation.

Different artifact.

---

# 7. Derived outputs are transforms

Here's where the API becomes particularly useful.

Define a thumbnail operation:

```js
const thumbnail = defineTransform({
  name: "thumbnail",
  version: "7",

  inputs: {
    video: "video/*",
  },

  outputs: {
    image: "image/jpeg",
  },

  parameters: {
    width: "number",
    at: "duration",
  },
});
```

Notice that this doesn't contain the implementation.

It describes the computation.

Use it:

```js
const result = await media.compute.materialize(
  thumbnail,
  {
    inputs: {
      video: segment,
    },

    params: {
      width: 512,
      at: "3s",
    },

    policy: thumbnailPolicy,
  },
);
```

Result:

```js
{
  artifact: {
    id: "obj_thumb_...",
    hash: "sha256:...",
    type: "image/jpeg",
  },

  computation: {
    key: "cmp_74f...",
  },

  cache: {
    hit: true,
  },
}
```

If it had never been computed:

```js
result.cache.hit
// false
```

The caller doesn't care.

---

# 8. Computation keys are automatic

Internally:

```text
key =
  hash(
    transform.name,
    transform.version,
    canonical(params),
    hashes(inputs)
  )
```

Conceptually:

```js
sha256({
  transform: "thumbnail",
  version: "7",

  params: {
    at: "3s",
    width: 512,
  },

  inputs: {
    video: "sha256:f714..."
  }
})
```

Therefore:

```js
await media.compute.materialize(
  thumbnail,
  {
    inputs: { video: segment },
    params: {
      width: 512,
      at: "3s",
    },
  }
);
```

100 times produces one logical computation.

Kubernetes can execute the job five times because of failures/retries, but publication remains idempotent.

---

# 9. Transform implementations are registered by workers

The coordinator shouldn't serialize arbitrary JavaScript closures into Kubernetes.

Instead a worker registers an implementation:

```js
worker.handle(thumbnail, async ctx => {
  const input = await ctx.input("video").path();

  const output = ctx.output("image", {
    extension: ".jpg",
  });

  await runFFmpeg([
    "-ss", ctx.params.at,
    "-i", input,
    "-vf", `scale=${ctx.params.width}:-1`,
    "-frames:v", "1",
    output.path,
  ]);

  return {
    image: output,
  };
});
```

The same code can run locally:

```js
await worker.runLocal();
```

or as Kubernetes workers:

```text
video-thumbnail workers
    ↓
Kubernetes jobs/pods
    ↓
Longhorn/NVMe storage
```

The transform identity remains:

```text
thumbnail@7
```

regardless of execution backend.

---

# 10. Redaction naturally becomes a DAG

Define detection:

```js
const detectPeople = defineTransform({
  name: "detect-people",
  version: "12",

  inputs: {
    video: "video/*",
  },

  outputs: {
    detections: "application/x-detections+json",
  },
});
```

Define redaction:

```js
const redact = defineTransform({
  name: "redact-video",
  version: "4",

  inputs: {
    video: "video/*",
    detections: "application/x-detections+json",
  },

  outputs: {
    video: "video/mp4",
  },

  parameters: {
    blur: "number",
  },
});
```

Use them:

```js
const detection = await media.compute.materialize(
  detectPeople,
  {
    inputs: {
      video: segment,
    },

    policy: detectionPolicy,
  },
);
```

Then:

```js
const redacted = await media.compute.materialize(
  redact,
  {
    inputs: {
      video: segment,
      detections: detection.artifact,
    },

    params: {
      blur: 24,
    },

    policy: policy(
      retain.for("3y"),
      durability.atLeast("replicated"),
    ),
  },
);
```

Your graph now exists automatically:

```text
raw segment ───────────────┐
     │                     │
     ▼                     │
detections                 │
     │                     │
     └──────────┐          │
                ▼          ▼
                redacted video
```

No separate workflow database is required to express lineage.

---

# 11. Query lineage

Upstream:

```js
await media.lineage.inputs(redacted.artifact);
```

Result:

```js
[
  segment,
  detection.artifact,
]
```

Downstream:

```js
await media.lineage.outputs(segment);
```

Could return:

```js
[
  {
    artifact: thumbnailArtifact,
    transform: "thumbnail@7",
  },
  {
    artifact: detectionArtifact,
    transform: "detect-people@12",
  },
  {
    artifact: redactedArtifact,
    transform: "redact-video@4",
  },
]
```

Full dependency graph:

```js
const graph = await media.lineage.graph(segment, {
  direction: "downstream",
  depth: Infinity,
});
```

---

# 12. Query video by time

The normal query API should understand intervals:

```js
const artifacts = await media.artifacts.find({
  stream: "camera/front-door",

  type: "video/h264",

  overlaps: time.range(
    "2026-08-14T12:00:00Z",
    "2026-08-14T13:00:00Z",
  ),
});
```

Or stream results:

```js
for await (const segment of media.artifacts.scan({
  stream: "camera/front-door",

  type: "video/h264",

  overlaps: time.day("2026-08-14"),
})) {
  // ...
}
```

Point lookup:

```js
const segment = await media.artifacts.at({
  stream: "camera/front-door",
  time: "2026-08-14T12:35:22Z",
  type: "video/h264",
});
```

---

# 13. Temporal manifests

Create immutable snapshots:

```js
const hour = await media.manifests.snapshot({
  stream: "camera/front-door",

  interval: time.hour(
    "2026-08-14T12:00:00Z"
  ),

  select: {
    type: "video/h264",
  },
});
```

Returned manifest could contain:

```js
{
  id: "manifest_...",
  hash: "sha256:...",

  interval: {
    start: "...",
    end: "...",
  },

  children: [
    "obj_001",
    "obj_002",
    "obj_003",
    // ...
  ],
}
```

Then:

```js
const day = await media.manifests.compose({
  interval: time.day("2026-08-14"),

  children: [
    hour00,
    hour01,
    hour02,
    // ...
  ],
});
```

Those manifests can be Merkle objects.

So:

```js
await media.integrity.verify(day);
```

can recursively verify the entire day.

---

# 14. Retention shouldn't directly call `rm`

Ask whether an artifact is eligible:

```js
const decision =
  await media.retention.evaluate(segment);
```

Result:

```js
{
  retain: true,

  until: "2026-11-12T16:10:00Z",

  reasons: [
    {
      policy: "raw-default",
      until: "2026-11-12T16:10:00Z",
    },
    {
      policy: "incident-182",
      until: "2027-08-14T00:00:00Z",
    },
  ],
}
```

Deletion is then:

```js
await media.artifacts.delete(segment, {
  reason: "retention-expired",
});
```

and the API rejects it if invariants aren't satisfied:

```js
RetentionViolationError:
  artifact is retained until 2027-08-14
```

There should be no casual:

```js
media.storage.rm(path)
```

in the normal API.

---

# 15. Explicitly represent recomputability

For derived artifacts:

```js
const info =
  await media.compute.recoverability(
    thumbnailArtifact,
  );
```

Could return:

```js
{
  recomputable: true,

  transform: "thumbnail@7",

  inputsAvailable: true,

  estimatedCost: {
    cpuSeconds: 0.38,
  },
}
```

After the raw segment expires:

```js
{
  recomputable: false,

  transform: "thumbnail@7",

  missingInputs: [
    "obj_raw_9281",
  ],
}
```

This gives your cache manager a much smarter model than:

```js
isCache: true
```

---

# 16. Cache eviction becomes a controller

For example:

```js
const cacheController =
  media.controllers.cache({
    stores: ["hot", "warm"],

    score: artifact => {
      return (
        artifact.stats.reuseProbability *
        artifact.stats.recomputeCost
      );
    },
  });
```

Then:

```js
await cacheController.reconcile({
  targetFreeSpace: "500GB",
});
```

The controller can preferentially evict:

```text
low reuse probability
+
cheap recomputation
+
inputs still available
```

before touching expensive or unrecoverable derived artifacts.

---

# 17. Storage migration is policy reconciliation

You shouldn't need application code like:

```js
if (age > 30days) {
  copyToArchive();
  deleteFromWarm();
}
```

Instead:

```js
await media.storage.reconcile(segment);
```

The planner can be inspected:

```js
const plan =
  await media.storage.plan(segment);
```

Example:

```js
{
  artifact: segment.id,

  current: {
    warm: 1,
  },

  desired: {
    archive: 1,
  },

  operations: [
    {
      operation: "copy",
      from: "warm",
      to: "archive",
    },
    {
      operation: "verify",
      store: "archive",
    },
    {
      operation: "drop",
      store: "warm",
    },
  ],
}
```

This is useful operationally because migrations become inspectable before execution.

---

# 18. Kubernetes jobs are similarly inspectable

```js
const computation =
  await media.compute.plan(
    thumbnail,
    {
      inputs: {
        video: segment,
      },

      params: {
        width: 512,
        at: "3s",
      },
    },
  );
```

Returns something conceptually like:

```js
{
  key: "cmp_74f...",

  transform: "thumbnail@7",

  status: "missing",

  inputs: [
    "obj_9281",
  ],

  outputs: [],

  execution: {
    preferredPool: "cpu",
  },
}
```

Then:

```js
await media.compute.materialize(computation);
```

The executor decides whether that's:

```text
same process
worker process
queue
Kubernetes Job
long-running Kubernetes worker
GPU worker
```

---

# 19. Resource requirements belong to transforms

```js
const detectPeople = defineTransform({
  name: "detect-people",
  version: "12",

  inputs: {
    video: "video/*",
  },

  outputs: {
    detections: "application/x-detections+json",
  },

  resources: {
    cpu: 2,
    memory: "4Gi",
    gpu: 1,
  },
});
```

The Kubernetes adapter can translate this into:

```text
requests/limits
node selectors
GPU resource requests
priority classes
worker pools
```

without those concepts entering your core object model.

---

# 20. Bulk processing should be AsyncIterable-based

Very natural in JavaScript:

```js
const segments = media.artifacts.scan({
  stream: "camera/front-door",
  overlaps: time.day("2026-08-14"),
  type: "video/h264",
});
```

Then:

```js
for await (const segment of segments) {
  await media.compute.materialize(
    thumbnail,
    {
      inputs: {
        video: segment,
      },

      params: {
        width: 512,
        at: "3s",
      },
    },
  );
}
```

Or concurrency helper:

```js
await media.compute.map(
  segments,
  thumbnail,
  {
    concurrency: 32,

    args: segment => ({
      inputs: {
        video: segment,
      },

      params: {
        width: 512,
        at: "3s",
      },
    }),
  },
);
```

On Kubernetes, `concurrency` could mean queued work rather than 32 promises on one machine.

---

# 21. Event subscriptions

For operational composition:

```js
for await (const event of media.events.subscribe({
  types: [
    "artifact.committed",
    "computation.completed",
    "artifact.expired",
  ],
})) {
  console.log(event);
}
```

Example:

```js
{
  type: "artifact.committed",

  artifact: {
    id: "obj_123",
    type: "video/h264",
  },

  at: "2026-08-14T16:10:10Z",
}
```

This makes it easy to build secondary systems without coupling them to ingestion.

---

# 22. A very small core interface

Internally, I would try hard to keep the real abstraction this small:

```js
media.artifacts
media.streams
media.compute
media.lineage
media.policies
media.retention
media.storage
media.manifests
media.integrity
media.events
```

And the most important operations:

```js
await media.artifacts.commit(...)
await media.artifacts.get(...)
await media.artifacts.find(...)
await media.artifacts.delete(...)

await media.compute.materialize(...)
await media.compute.plan(...)

await media.storage.reconcile(...)

await media.retention.evaluate(...)

await media.lineage.inputs(...)
await media.lineage.outputs(...)
```

Everything else can be convenience sugar.

---

# 23. Adapter interfaces should be tiny

For example, storage could fundamentally be:

```js
class ArtifactStore {
  async put(key, source) {}
  async get(key) {}
  async has(key) {}
  async delete(key) {}

  async verify(key, expectedHash) {}
}
```

Catalog:

```js
class Catalog {
  async commitArtifact(record) {}

  async getArtifact(id) {}

  async findArtifacts(query) {}

  async addLocation(id, location) {}

  async removeLocation(id, location) {}

  async addDependency(parent, child) {}
}
```

Executor:

```js
class Executor {
  async submit(computation) {}

  async status(computationKey) {}
}
```

Everything higher-level uses those.

That means you can have:

```js
createMediaSystem({
  catalog: sqliteCatalog(),
  stores: {
    hot: filesystemStore(...),
  },
  executor: localExecutor(),
});
```

for development and:

```js
createMediaSystem({
  catalog: postgresCatalog(...),

  stores: {
    hot: filesystemStore(...),
    warm: filesystemStore(...),
    archive: objectStore(...),
  },

  executor: kubernetesExecutor(...),
});
```

in production.

Same application API.

---

# 24. I would also make the raw data structures portable

An `ArtifactRef` should be JSON-safe:

```js
{
  id: "obj_01K2C...",
  hash: "sha256:...",
  type: "video/h264",

  stream: "camera/front-door",

  interval: {
    start: "2026-08-14T16:10:00.000Z",
    end: "2026-08-14T16:10:10.000Z",
  },
}
```

No methods.

No database connection.

No open file descriptor.

No class instance requirement.

So this:

```js
JSON.stringify(artifact)
```

works.

You can put it on Kafka, NATS, Redis, Postgres, Kubernetes Jobs, HTTP, etc.

Then operations are:

```js
media.artifacts.get(ref)
```

rather than:

```js
ref.fetch()
```

This is a subtle but important distributed-systems design choice.

---

# 25. End-to-end application code becomes quite small

Putting everything together:

```js
const camera =
  media.stream("camera/front-door");

const epoch =
  await camera.beginEpoch({
    allocator: ring({
      store: "hot",
      horizon: "2h",
      segmentDuration: "10s",
    }),
  });

for await (const chunk of incomingSegments) {
  const raw =
    await epoch.commitSegment({
      sequence: chunk.sequence,

      interval: chunk.interval,

      body: chunk.bytes,

      type: "video/h264",

      policy: rawPolicy,
    });

  media.compute.materialize(
    thumbnail,
    {
      inputs: {
        video: raw,
      },

      params: {
        width: 512,
        at: "3s",
      },

      policy: thumbnailPolicy,
    },
  );

  media.compute.materialize(
    detectPeople,
    {
      inputs: {
        video: raw,
      },

      policy: detectionPolicy,
    },
  );
}
```

The ingestion application doesn't contain:

```text
Longhorn logic
PVC logic
cache lookup logic
filename construction
directory rotation
retry bookkeeping
thumbnail existence checks
retention cleanup
archive migration
Kubernetes Job creation
```

Those are all consequences of the declarative model.

## The API philosophy

I would preserve these equations directly in the API design:

$$
Artifact
=
Identity
+
Time
+
Content
$$

$$
DerivedArtifact
=
Transform
+
Inputs
+
Parameters
+
Version
$$

$$
ComputationKey
=
H(Transform,Version,Inputs,Parameters)
$$

$$
EffectivePolicy
=
P_1 \sqcup P_2 \sqcup \cdots \sqcup P_n
$$

$$
DesiredPlacement
=
f(Artifact,Policy,Age,Access)
$$

$$
PhysicalLocation
\neq
ArtifactIdentity
$$

That gives you a fairly small JavaScript API while leaving room for a sophisticated system underneath.

The next useful layer would be to turn this into an **actual package skeleton**—`@video/core`, `@video/catalog-postgres`, `@video/storage-fs`, `@video/runtime-kubernetes`—with concrete JS/TypeScript interfaces, database schema, and an implementation of `materialize()` and policy reconciliation.

