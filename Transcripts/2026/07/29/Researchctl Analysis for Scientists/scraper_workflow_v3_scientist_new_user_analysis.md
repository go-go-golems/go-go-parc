# Scraper Workflow V3
## Scientist and new-user analysis, implementation review, and fit assessment as the execution engine for Researchctl 2

**Repository:** `wesen/scraper`  
**Reviewed ref:** `task/benchmark-cpu-inference`  
**Reviewed head:** `202229464629e2b6d0e193ff7798b16770b3a270`  
**Review date:** 2026-07-24  
**Audience:** ML scientists, research engineers, workflow-platform engineers, and Researchctl 2 implementers  
**Companion document:** `researchctl2_rag_architecture_guide.md`

---

## 1. Review stance and scope

This document evaluates the current Scraper Workflow V3 branch as the proposed **workflow executor** beneath the clean Researchctl 2 architecture. The question is not whether Workflow V3 contains impressive engineering. It does. The question is whether its current product, scripting model, artifact model, execution identity, and Researchctl bridge serve a scientist running a large, reproducible RAG experiment program.

The assessment treats the current code as a deep prototype and asks:

1. Does it execute scientific workflows durably and correctly?
2. Does it preserve enough provenance to reconstruct computations?
3. Can it handle realistic RAG artifacts and data volumes?
4. Can an ML scientist author tasks and workflows without becoming a Go platform engineer?
5. Does it efficiently reuse shared upstream work across many experiment cases?
6. Does it separate scientific treatments from operational scheduling?
7. Does the Researchctl bridge preserve the full step and artifact chain?
8. Which parts should be retained, revised, or removed in a clean implementation?

The review covers the branch README and product guides; the Workflow V3 IR, compiler, catalog, bundles, registry, artifact store, runtime, dispatcher, isolation layer, SQLite schema, observation projection, CLI, task packages, and Researchctl runner bridge; and representative unit and integration tests.

I did **not** execute the test suite in this review environment. The branch contains extensive tests and a GitHub Actions workflow that runs `go test ./...`, but the workflow is configured for `main` pushes and pull requests, the reviewed branch had no visible pull request, and no workflow runs or combined statuses were visible for the reviewed head. Conclusions about behavior therefore come from source and test inspection, not an independently reproduced test run.

---

## 2. Executive verdict

### 2.1 One-sentence assessment

> Workflow V3 is a strong durable local workflow **kernel**, but its current artifact transport, static Go/JavaScript task-package system, lack of cross-run materialization caching, incomplete execution-environment identity, and one-workflow-per-Researchctl-attempt bridge make it a poor direct executor for a large RAG research program.

### 2.2 The important distinction

The durable engine underneath Workflow V3 is substantially cleaner than the current Researchctl prototype. It has real and useful semantics for:

- immutable compiled plans;
- exact task-bundle identities;
- transactional workflow submission;
- node dependencies;
- append-only attempts;
- lease renewal and stale-completion fencing;
- retries with typed failures;
- cancellation;
- resource-class admission;
- bounded map expansion;
- bounded reductions;
- budgets and approval gates;
- durable external-operation accounting;
- content-digest artifact references;
- deterministic, privacy-bounded operational observations;
- restricted subprocess execution with Bubblewrap and cgroup limits.

Those are excellent foundations for an executor.

The product around that kernel, however, has the wrong center of gravity for our needs. A scientist cannot simply provide Python, R, shell, Julia, a container command, or a compiled binary as a step. Workflow JavaScript can only compose task descriptors that were already embedded in statically linked Go task packages. Scalar experiment parameters are not first-class node parameters. Large inputs and outputs are read wholly into memory. Every Researchctl attempt receives its own SQLite database and artifact root. There is no global step cache or shared materialization layer. Only bounded terminal outputs are exported back to Researchctl.

For a factorial RAG study, this means repeated chunking, summarization, embedding, indexing, and retrieval work that should be shared across cases will instead be recomputed in isolated workflow runs, while many realistic artifacts will exceed the intended transport envelope.

### 2.3 Overall fit

| Capability | Current assessment | Importance for our RAG program |
|---|---:|---:|
| Durable local run/node/attempt state | **Strong** | Critical |
| Retry and stale-worker correctness | **Strong** | Critical |
| Cancellation and failure classification | **Strong** | High |
| Small-artifact integrity | **Good** | High |
| External provider-operation accounting | **Strong** | High |
| Deterministic operational observations | **Good** | High |
| Ordinary ML task authoring | **Poor** | Critical |
| Python/R/container execution | **Poor / absent as a first-class model** | Critical |
| Large artifact handling | **Poor** | Critical |
| Cross-run cache and upstream reuse | **Absent in the reviewed core** | Critical |
| Exact environment reconstruction | **Partial** | Critical |
| GPU/HPC/cloud resource model | **Weak** | High |
| Intermediate artifact export to Researchctl | **Weak** | Critical |
| Workflow portability | **Weak** | High |
| New-user experience | **Poor** | High |
| Fit as an internal kernel after refactoring | **Very good** | Critical |

### 2.4 Direct answers

**Does the approach make sense?**  
Yes, as a domain-neutral durable execution kernel that consumes a canonical plan. No, as a JavaScript-centric scientist-facing workflow product and no, as a per-attempt isolated executor with no shared materialization cache.

**Does it address experiment management?**  
It correctly does not try to own scientific hypotheses, cases, blocks, replicates, evidence, or decisions. Those belong to Researchctl. It does address operational execution well. The bridge currently loses too much of the step-level artifact chain, however, so the two systems do not yet compose into a complete reproducible research system.

**Are features confusing or overengineered?**  
Yes. Rolling registry generations, quarantine, provider-operation accounting, approval gates, budgets, dual isolation classes, a Goja authoring DSL, a Goja task runtime, bundle manifests, native module aliases, and multiple nested digests are sophisticated. Some are valuable. Together they create a large conceptual surface before the product supports the basic scientist expectation: “run this pinned Python or container step over these files and record everything.”

**Are important needs missing?**  
Yes: streaming and remote artifacts, directory/tree artifacts, global cache records, environment locks or container identities, standard command tasks, Python/R ergonomics, GPU resources, robust distributed executors, full logs, intermediate-output publication, schema registry semantics, source provenance, and export of complete retrospective workflow provenance.

**How well is it implemented?**  
The kernel is carefully implemented and unusually defensive. The boundary contracts, failure handling, SQL transactions, isolation checks, and tests show strong engineering. Product maturity is lower than code sophistication: the branch is a large recent hard cut, has no visible CI result at the reviewed head, and several core contracts are still prototype-grade for long-term interoperability.

**Could it be improved incrementally?**  
Some parts can: artifact APIs, environment records, module identities, logs, and resource requests. The scripting and integration model require a more fundamental shift.

---

## 3. The concrete RAG workload the executor must serve

The companion Researchctl 2 guide considers a scientist investigating a full RAG pipeline over a large technical corpus. The workflow includes:

```text
corpus snapshot
    |
    v
parse / normalize / deduplicate
    |
    v
chunk
    |
    +----> chunk summaries
    |
    +----> synthetic questions
    |
    v
representation construction
    |
    +----> lexical documents and BM25 index
    |
    +----> embeddings and vector index
    |
    v
query preparation
    |
    v
lexical retrieval / vector retrieval
    |
    v
fusion
    |
    v
reranking
    |
    v
context deduplication, diversification, expansion, and packing
    |
    v
answer generation and citation extraction
    |
    v
retrieval, answer, faithfulness, latency, failure, and cost evaluation
```

The scientist varies factors such as:

- parser and normalization policy;
- chunk method, size, overlap, and structural boundaries;
- summary model, prompt, length, and concurrency;
- synthetic-question model, prompt, count, and sampling parameters;
- embedding model, dimensions, normalization, batch size, and concurrency;
- lexical analyzer and BM25 parameters;
- vector-index type and construction/search parameters;
- lexical, vector, or hybrid retrieval;
- fusion method and weights;
- candidate depth and reranking method;
- context budget, diversification, parent expansion, and ordering;
- answer model, prompt, sampling, citation policy, and abstention policy;
- query concurrency, provider limits, hardware, and execution resources.

A useful executor must support two properties at the same time:

1. **Occurrence integrity:** every scientific assignment has an auditable run and attempt history.
2. **Materialization reuse:** identical upstream computations are performed once and safely reused wherever compatible.

For example, changing only the answer prompt should not rebuild chunks, summaries, embeddings, or indexes. Changing `top_k` should normally reuse both indexes. Changing the embedding model should reuse the parsed corpus and chunks but regenerate embeddings and vector indexes. Changing chunking should invalidate all downstream artifacts.

This produces an execution graph across the **whole study**, not merely a series of independent end-to-end runs.

---

## 4. Reconstructed current architecture

The reviewed branch has this effective architecture:

```text
workflow.js
    |
    v
Goja authoring runtime
  require("workflow")
  require(<statically registered descriptor modules>)
    |
    v
WorkflowIR
    |
    v
host-policy compiler + task catalog
    |
    v
WorkflowPlan
  - task kind/version
  - bundle digest
  - entrypoint
  - ABI
  - schemas
  - module aliases
  - resource class
  - retry policy
  - isolation policy
  - catalog/IR/plan digests
    |
    v
Workflow V3 application
    +-- SQLite operational store
    +-- local file artifact store
    +-- sealed registry / rolling registry manager
    +-- task module registry
    +-- dispatcher
    |
    v
node execution
    +-- trusted in-process Goja task
    +-- restricted Bubblewrap subprocess worker
    |
    v
output ArtifactRef values + attempts + events + external operations
    |
    v
canonical observation projection
    |
    v
optional Researchctl stdio runner bridge
```

The ownership boundary described in the branch is conceptually correct:

- Scraper owns workflow durability and execution.
- Domain packages own task semantics.
- Researchctl owns scientific evidence.
- JavaScript describes intent while Go validates and compiles it.

The difficulty is that “domain package” and “JavaScript describes intent” mean something much narrower than a new ML user will expect.

---

## 5. What a new RAG user would actually have to do

A new scientist cannot begin with a Python chunking script and a workflow file. The current extension path is approximately:

1. Create a Go package implementing `workflowv3product.TaskPackage`.
2. Embed CommonJS task source into the Go binary with `//go:embed`.
3. Define a `BundleManifest` containing task kinds, versions, entrypoints, input/output schema strings, module aliases, resource classes, retries, budget ceilings, and isolation ceilings.
4. Build a `Bundle` and expose its digest-pinned task specifications.
5. Create a descriptor module mapping friendly JavaScript factory names to task keys.
6. Declare every required host module alias.
7. For provider or database capabilities, provide trusted Go `TaskModuleFactory` implementations and external-operation descriptors.
8. Add the package to a composition root or custom binary. The stock product only knows statically compiled packages.
9. Write a workflow JavaScript file that composes those descriptors with symbolic artifact references.
10. Compile the script into a canonical plan.
11. Create input artifact files or set-input archives and a strict input manifest.
12. When using Researchctl, create a separate selector-binding JSON file and compile a `scraper-workflow-execution/v2` domain configuration.
13. Launch Researchctl with the external runner path, runner name/version, state roots, artifact roots, task-package selections, capacities, lease duration, timeouts, and cancellation grace.
14. Inspect two nested run systems: Researchctl run/attempt records and Scraper workflow/node/attempt records.

That is a platform-integration workflow, not a scientist workflow.

The stock `--task-package` flag is especially likely to mislead. It selects among packages compiled into the binary; it does not load an arbitrary package from disk, a Python wheel, an OCI image, a CWL tool, or a local script directory.

---

## 6. What Workflow V3 gets right

### 6.1 Compact durable control records

The architecture was motivated by a real failure mode in the previous workflow engine: source-bearing plans and large JSON payloads were duplicated into operation rows, causing enormous SQLite and WAL growth and violating the intended redaction boundary. Workflow V3 correctly replaces that with small typed references and content digests.

This is exactly the right architectural move for RAG. Prompts, source text, vectors, raw provider bodies, and model outputs should not be copied through every control-plane row.

### 6.2 Plan compilation pins meaningful task identities

Each task implementation is identified by:

```text
task kind
+ task version
+ bundle digest
+ entrypoint
+ ABI
```

The compiled plan also records schemas, module aliases, resource class, retry policy, catalog digest, IR digest, plan digest, and isolation policy. This is far better than a workflow graph that names an unversioned function and hopes the runtime still means the same thing later.

### 6.3 Transactional lease and attempt semantics

The runtime has a proper operational state machine:

- nodes are leased transactionally;
- attempts are append-only;
- leases have tokens and cancellation epochs;
- the executor renews leases;
- a stale or superseded worker cannot publish a completion;
- retries are represented as additional attempts;
- failures use closed classes and codes;
- resource and budget reservations are coordinated with admission;
- node completion and output publication are persisted together.

These are the semantics we want to retain.

### 6.4 Work-conserving resource classes

The dispatcher continuously fills free capacity by resource class rather than waiting for a fixed batch of heterogeneous tasks to finish. That directly addresses the earlier situation where slow generation calls prevented free embedding capacity from being replenished.

For a RAG pipeline, separate capacities such as:

```text
cpu.parse
cpu.index
provider.embedding
provider.generation
gpu.embedding
gpu.rerank
io.publish
```

are useful. The current resource model is too coarse for the final system, but the scheduler behavior is sound.

### 6.5 Bounded lazy fan-out

Maps are expanded in pages and limit both total items and materialized-ahead work. This is preferable to expanding millions of query or chunk tasks into the database at submission time.

The ordered item-manifest model also preserves deterministic logical order independently of completion order, which is important for reproducible result sets.

### 6.6 Retry-aware external-operation ledger

The external-operation model is one of the strongest and most distinctive features. Before a provider effect begins, a trusted module records an admitted operation with:

- operation kind/version;
- authority digest;
- descriptor digest;
- correlation digest;
- budget reservations;
- bounded measures.

Completion records outcome, elapsed time, failure class/code, accounting mode, and counters. Arbitrary provider text is excluded.

For RAG studies that depend on embeddings, rerankers, hosted LLMs, HTTP APIs, or instrument-like services, this creates valuable evidence about:

- how many external effects were attempted;
- which retries occurred;
- how much usage was reserved and settled;
- which operations failed or remained incomplete;
- provider-side timing boundaries;
- whether accounting was actual or conservative.

This should survive into the clean executor.

### 6.7 Privacy-bounded deterministic observations

The observation layer reads authoritative records in one read transaction, canonicalizes a bounded source snapshot, and derives retry-aware metrics and traces. It intentionally excludes task payloads, raw event bodies, artifact locators, lease capabilities, and free-form failure messages.

This is a good distinction:

```text
operational ledger       authoritative detailed state
observation projection   safe, stable summary for research records
```

### 6.8 Serious restricted-isolation engineering

The restricted executor is not a superficial subprocess wrapper. It pins the worker, launcher, Bubblewrap binary, and allowlisted tool digests; clears the environment; unshares namespaces; mounts only the required read-only bundle and inputs plus a writable output root; disables normal PATH access; applies cgroup CPU, memory, and process limits; enforces protocol and output bounds; validates output trees; and republishes verified artifacts in the parent.

The integration tests exercise malformed frames, oversized frames, environment leakage, host filesystem visibility, network access, process limits, memory limits, output validation, and cancellation. This is high-quality defensive work.

---

## 7. The fundamental mismatch: no shared materialization layer

### 7.1 Current Researchctl bridge topology

The bridge derives an opaque Workflow run key from the Researchctl run ID and attempt ID, then creates:

```text
<state-root>/<opaque-attempt-key>.db
<artifact-root>/<opaque-attempt-key>/
```

It opens a new Workflow V3 application against those paths and submits one workflow. A new Researchctl attempt receives a new attempt ID and therefore a new database and artifact root.

This has useful containment properties, but it makes every scientific run an isolated island.

### 7.2 Consequence for a RAG experiment matrix

Suppose a study has:

- three chunking policies;
- two enrichment policies;
- two embedding models;
- three retrieval families;
- three `top_k` settings;
- two answer prompts;
- three replicates.

Even when many assignments share the same corpus, chunk set, summary set, embeddings, and indexes, the current bridge has no global cache in which those materializations can be found. Each Researchctl attempt launches a distinct Workflow store and local artifact store.

The result is structurally equivalent to:

```text
for every scientific assignment:
    rebuild complete pipeline in a private workspace
```

That is the opposite of the materialization graph required by a large experiment program.

### 7.3 Why content-addressed files are not enough

A content-addressed artifact store can deduplicate bytes only when executions share the same store and when the workflow knows that a prior computation is eligible for reuse. The bridge currently gives each attempt a separate root. Even in a shared root, the engine has no first-class cache record that answers:

```text
Do these exact implementation, environment, parameters, inputs,
executor semantics, secrets/provider versions, and hardware constraints
permit reuse of these verified outputs?
```

Artifact content addressing and computation caching are separate concerns.

### 7.4 Required correction

The clean system needs a workspace- or service-level materialization layer:

```text
execution occurrence
    |
    v
step occurrence ---- execution fingerprint ----> cache/materialization record
    |                                               |
    |                                               v
    +---------------------------------------> verified artifacts
```

Every new study/run still receives new occurrence records. A cache hit creates a new step occurrence with `materialized-from` provenance; it does not pretend the old run occurred again.

The executor service should use:

- a shared global or project-scoped CAS;
- a global cache index;
- independent workflow-run occurrence state;
- explicit cache compatibility policy;
- retention and reachability tracking.

---

## 8. Artifact management is prototype-scale

### 8.1 Current API

The artifact interface is effectively:

```go
Put(ctx, schema, mediaType string, body []byte) (ArtifactRef, error)
Open(ctx, ref ArtifactRef) (io.ReadCloser, error)
```

The file implementation:

- accepts the complete artifact as a byte slice;
- computes SHA-256;
- writes `objects/<digest>`;
- opens by reading the complete file with `os.ReadFile`;
- verifies the complete size and digest;
- returns a memory-backed reader.

The default maximum artifact size is 64 MiB.

The product input staging, map expansion, reduction staging, restricted isolation input/output publication, and Researchctl bridge repeatedly call whole-file read methods. The Researchctl runner defaults to a 16 MiB total output-export budget and sends artifacts as base64-encoded byte arrays in JSON frames.

### 8.2 What this supports

This is appropriate for:

- small JSON documents;
- compact manifests;
- CSV summaries;
- individual prompt/response records;
- small model-evaluation outputs;
- test fixtures.

### 8.3 What this does not support well

A serious RAG program may produce:

- multi-gigabyte normalized corpora;
- millions of chunks;
- Parquet datasets;
- embedding matrices;
- vector indexes;
- lexical indexes;
- model checkpoints;
- compressed trace archives;
- directory trees;
- large answer/evaluation tables.

These cannot reasonably be copied through repeated `[]byte` materialization, JSON base64 frames, and 16–64 MiB limits.

### 8.4 Other custody gaps

The reviewed store does not expose first-class support for:

- streaming writes and reads;
- multipart uploads;
- directory/tree artifacts;
- sparse or chunked objects;
- range reads;
- local hardlink/reflink import;
- remote object stores;
- OCI artifacts;
- artifact catalogs;
- verify/repair sweeps;
- deduplication accounting;
- retention, legal hold, redaction, or garbage collection;
- reachability from research records.

The current “content-addressed artifact root” is a useful local test implementation, not the final research data plane.

### 8.5 Concrete implementation concern

When `Put` finds that `objects/<digest>` already exists, it returns the expected reference without verifying that the existing bytes really match. A later `Open` will detect corruption, but the store can temporarily publish a reference to a corrupt preexisting object. Publication should verify existing objects or use a stronger atomic object-store contract. Directory fsync and crash consistency also deserve explicit treatment for research custody.

---

## 9. Only named terminal outputs cross the research boundary

Workflow V3 stores all node output references in `v3_node_outputs`, but the normal run snapshot and canonical observation artifact lineage expose only outputs explicitly named by the workflow plan.

The Researchctl bridge then reads those named terminal outputs into memory and emits them as `workflow-output` artifacts. Intermediate artifacts remain inside the private Workflow artifact root and are not first-class Researchctl evidence.

This is insufficient for a reproducible RAG pipeline. A final answer table is not enough to reconstruct:

- which chunk set was used;
- which summary/question artifacts were generated;
- which embedding set backed an index;
- which index snapshot was queried;
- which retrieval candidate set fed reranking;
- which context set fed answering;
- which failed or partial intermediates affected coverage.

The clean integration should publish a **retrospective execution manifest**, not just terminal files. It should enumerate every step occurrence and every material input/output edge, with policy-controlled retention of intermediate bytes.

Intermediate artifacts may be classified as:

- retained and exportable;
- retained in shared CAS but not bundled by default;
- reproducible and eligible for garbage collection;
- sensitive and access-controlled;
- transient with an explicit deletion record.

Researchctl does not need to duplicate all bytes. It does need durable identities and derivation edges.

---

## 10. Reproducibility identity: strong in some places, incomplete overall

### 10.1 What is pinned well

The compiled task identity includes the task key, source bundle digest, entrypoint, and ABI. Restricted subprocess execution additionally pins digests of the worker executable, isolation launcher, Bubblewrap executable, and allowlisted tools.

The plan pins:

- task implementations;
- port schemas;
- module aliases;
- resource classes;
- retry policies;
- budget and gate policies;
- isolation policy and executor identity;
- catalog, IR, and plan digests.

This is a strong prospective contract.

### 10.2 Workflow source is not preserved as an execution artifact

The CLI reads `workflow.js`, compiles it, and stores the plan. The plan preserves an IR digest, but the authoring source itself is not submitted as a run input or provenance artifact.

Semantic identity should be based on the normalized plan, but reproducibility packages should also retain:

- authoring source;
- source digest;
- authoring-tool version;
- source repository and commit;
- dirty-tree patch or source archive;
- compiler/runtime version.

Without this, another scientist can inspect what was executed but cannot necessarily recover the maintainable source that produced the plan.

### 10.3 Trusted host modules are not identity-complete

A task bundle declares module aliases such as `fs:input`, `fetch:public`, a provider module, or a database module. The sealed registry generation includes task implementation identities, module **alias strings**, and restricted-isolation executor digests.

`TaskModuleFactory` contains an alias, validation hook, operation descriptors, and a Go builder function, but it has no module implementation digest or version. Therefore:

- the Go implementation behind the same alias can change;
- dependency versions can change;
- host configuration can change;
- fetch, database, provider, or preprocessing semantics can change;
- the registry generation can remain the same if names and task bundles remain unchanged.

External-operation authority digests help for provider effects, but they do not generally identify every behavior of a trusted native module.

This is a material reproducibility defect. Every executable capability that can influence outputs must contribute to the execution fingerprint.

### 10.4 Host runtime and environment are not fully captured

The run does not generally identify:

- the Scraper binary digest;
- Go module/dependency lock digest;
- operating-system and kernel identity;
- locale/timezone beyond selected subprocess settings;
- CPU model and instruction capabilities;
- GPU model, count, memory, driver, runtime, and firmware;
- container or environment-lock digest;
- native-library versions;
- filesystem or database engine versions where scientifically relevant;
- secret reference versions;
- provider region and resolved model identity unless domain code records them.

Restricted tasks are much better isolated than trusted tasks, but isolation is not the same as environment reconstruction.

### 10.5 Canonical JSON is implementation-specific

`workflowv3.CanonicalJSON` calls Go's `json.Marshal`. Within the current Go model this is deterministic enough for many tests, but it is not a declared cross-language canonicalization standard. It does not establish an interoperability contract for numeric forms, Unicode normalization, or future non-Go producers.

Before treating plan and evidence digests as long-lived public identities, the clean system should adopt a specified canonicalization algorithm, domain-separated digest inputs, and golden cross-language vectors.

### 10.6 Schema strings are identifiers, not validated schemas

Artifact and port schemas are currently non-empty strings checked for equality. That is useful nominal typing, but it does not guarantee that bytes conform to a JSON Schema, Arrow schema, Protobuf descriptor, Parquet schema, or domain contract.

The clean system should distinguish:

```text
logical type ID
schema version
schema document digest
media type
validation profile
```

Domain workers should validate outputs before publication, and the resulting validation evidence should be recorded.

---

## 11. The scripting model is the wrong default for ML scientists

### 11.1 “Pure JavaScript” is descriptor composition, not ordinary scripting

The authoring runtime exposes only the `workflow` module and statically registered descriptor modules. A workflow script can create symbolic inputs, task nodes, maps, reductions, gates, outputs, budgets, and isolation policies.

It cannot simply define a Python function, shell command, notebook, R script, container step, or arbitrary executable. Task behavior must already exist in the selected task catalog.

This is a legitimate secure DSL. It should not be presented as the primary way scientists author executable workflows.

### 11.2 Adding a task requires Go composition

The example task package embeds CommonJS task source inside a Go package and constructs bundle, registry, and descriptor objects in Go. The package set is assembled from statically available `TaskPackage` values. The stock command's package flag selects among those values.

For RAG research, this creates an unacceptable development cycle:

```text
edit Python/ML idea
    -> port or wrap it in CommonJS/Goja conventions
    -> define Go package metadata
    -> rebuild Go runner binary
    -> update package/bundle identities
    -> recompile workflow
    -> run experiment
```

The normal cycle should be:

```text
edit Python/R/command/container task
    -> lock environment
    -> validate task contract
    -> run study
```

### 11.3 Scalar parameters are not first-class

Task descriptor inputs must be workflow `ValueRef` objects. The plan node has artifact bindings but no canonical `parameters` object. There is no simple literal/config constructor in the reviewed DSL.

Parameters such as:

```text
chunk_size = 512
overlap = 64
summary_prompt = v3
embedding_model = text-embedding-3-large
top_k = 20
fusion_alpha = 0.5
query_concurrency = 16
```

must therefore be encoded into artifact inputs, baked into task source, or represented by distinct task implementations.

Using a canonical configuration artifact can be defensible, but forcing every scalar through external artifact preparation is awkward and obscures the difference between scientific parameters and material data inputs.

The execution plan needs a first-class canonical parameter object, with explicit roles and cache semantics.

### 11.4 TypeScript declarations provide limited safety

The generated declarations make the JavaScript API discoverable, but the generic types are largely phantom types around runtime objects. Port compatibility is ultimately checked through schema strings during Go compilation.

This is useful editor assistance, not the kind of static domain typing that justifies making the DSL central to the platform.

### 11.5 Two JavaScript layers are unnecessary

Workflow V3 uses JavaScript both to author the plan and to implement many task bundles. Researchctl and the RAG domain also have or have had their own JavaScript DSLs.

A clean system should reduce this to:

- canonical data contracts;
- optional language-specific authoring SDKs;
- ordinary executable task code;
- one generic executor protocol.

JavaScript can remain one optional authoring compiler and one optional trusted task runtime. It should not be the universal language of the platform.

---

## 12. Workflow expressiveness is specialized rather than general

The current core supports:

- static DAG tasks;
- single-source maps over ordered set manifests;
- bounded homogeneous tree reductions;
- approval gates;
- named scalar and set outputs;
- resource classes;
- retries;
- budgets;
- trusted or restricted execution.

This is enough for many internal pipelines, but several constraints matter for RAG:

### 12.1 Maps are batch manifests, not streaming collections

A map source is a complete ordered item manifest. The runtime reads and decodes that artifact, then pages database materialization. This bounds control-plane growth but does not provide streaming dataflow or backpressure over large produced datasets.

### 12.2 Reduction is homogeneous

The reduction compiler requires one output and requires its schema to match the source item schema. A reducer cannot directly turn a set of chunk artifacts into a different index artifact type. That requires a homogeneous reduction followed by another task, or a domain-specific workaround.

### 12.3 No first-class conditionals or subworkflows

The reviewed IR has no general condition node, branch, switch, loop, reusable subworkflow call, or nested workflow interface. A compiler can emit different static plans for different cases, which is often preferable scientifically, but the product should make that boundary explicit.

### 12.4 No multi-input map or join primitive

RAG evaluation often joins query sets, relevance judgments, retrieval results, answers, and judge records. The current map callback receives one symbolic item. Joins must be precomputed into one item artifact or implemented inside a domain task.

### 12.5 No general scatter/gather executor interface

The map and reduce semantics are built into this engine rather than expressed through a portable execution-plan contract that other backends could implement. That limits future Slurm, Kubernetes, Nextflow, Snakemake, or cloud-batch integration.

None of these limitations invalidate the kernel. They reinforce that the executor should consume a generic IR and expose adapter capabilities, rather than making its current DSL the scientific programming model.

---

## 13. Parallelism and resource management

### 13.1 What works

Resource classes and work-conserving dispatch solve a real problem. Transactional capacity checks are much stronger than client-side semaphores. Map expansion backpressure and retry deadlines are also useful.

### 13.2 The resource model is too coarse

A plan node requests one resource-class string. The host supplies an integer capacity for each class.

This cannot fully express:

- CPU cores;
- memory requests and limits;
- ephemeral disk;
- GPU count;
- GPU model or compute capability;
- GPU memory;
- NUMA or affinity constraints;
- accelerator partitions;
- network bandwidth class;
- provider quota pools;
- per-host data locality;
- preemptible versus guaranteed execution;
- queue/project/accounting identity;
- Slurm or Kubernetes placement requirements.

Isolation limits provide CPU time, memory, process, and output ceilings for restricted local subprocesses, but they are not a portable scheduler resource request.

For a RAG system, resource identity can be scientifically relevant. Approximate nearest-neighbor construction, quantization, GPU kernels, batching, and provider concurrency may change results as well as runtime. The executor must record both requested and realized resources.

### 13.3 Operational versus scientific parallelism

The executor should not decide whether a concurrency parameter is a treatment. Researchctl and the domain compiler must label it.

The execution plan should distinguish:

```text
scheduler.max_in_flight       operational only
embedding.batch_size          treatment or fixed scientific parameter
query.concurrency             treatment when measuring systems behavior
provider.max_connections      operational ceiling
```

The current generic resource-class mechanism does not preserve this scientific role. That is acceptable at the executor layer only if Researchctl records it and includes relevant treatment parameters in step fingerprints.

---

## 14. Failure, retry, cancellation, and recovery

### 14.1 Strong semantics

Workflow V3 correctly distinguishes node attempts from workflow runs. It records typed failures, supports retryable versus non-retryable failures, uses lease fencing, and can cancel active attempts. Budget usage is settled even on failure, with conservative handling where appropriate.

This is substantially better than workflow wrappers that simply rerun a command and overwrite a log.

### 14.2 Researchctl and Workflow attempts form a nested retry system

The composed system has:

```text
Researchctl scientific run
    |
    +-- Researchctl attempt
            |
            +-- Scraper workflow run
                    |
                    +-- node attempt(s)
                            |
                            +-- external-operation attempt(s)
```

This is defensible, but the user needs one coherent explanation and UI. “Attempt 2” is ambiguous without its level.

Recommended terms:

- **research run**: scientific occurrence;
- **executor invocation**: one invocation of the workflow executor for that run;
- **workflow run**: subordinate DAG occurrence;
- **step attempt**: technical retry of one node;
- **external operation**: provider/tool side effect.

### 14.3 Crash recovery is honest but wasteful

The runner intentionally does not adopt a workflow run created by a previous Researchctl attempt. A process crash can leave durable Scraper state, and the next Researchctl attempt creates another workflow run in another private database/root.

This avoids guessing about ambiguous side effects, but it can duplicate expensive provider calls and leave orphan state. The clean bridge should support two distinct operations:

1. **Reconnect the same executor invocation** using the same invocation ID when the parent process is merely interrupted.
2. **Create a replacement invocation** when the previous attempt has been terminally classified and must not be adopted.

External-operation records and completion keys can help determine safe recovery. The policy must be explicit rather than always “start another private workflow.”

### 14.4 Debugging evidence is too restricted

The security posture deliberately excludes arbitrary stderr and provider error text. That is appropriate for public observation projections, but operational debugging needs policy-controlled logs.

The clean executor should retain:

- stdout and stderr as bounded or chunked artifacts;
- structured task logs;
- redaction status and scanner version;
- secret-access audit records;
- failure summaries safe for general views;
- restricted access to raw diagnostics;
- digest-only records when retention is prohibited.

The current allowlisted execution path keeps only bounded stdout and discards stderr content. Restricted isolation similarly bounds/discards stderr rather than publishing a sanitized diagnostic artifact.

---

## 15. Security and isolation assessment

### 15.1 Strong points

- clear trusted versus restricted classes;
- exact restricted-executor digest;
- no shell or arbitrary executable selection in allowlisted execution;
- environment clearing;
- fixed mount topology;
- network namespace isolation;
- cgroup CPU, memory, and process controls;
- output-tree validation;
- symlink and hardlink defenses;
- protocol size limits;
- parent-side digest verification;
- secret-bearing payload exclusion from canonical observations;
- closed failure vocabulary.

### 15.2 Limitations

The restricted implementation is Linux-specific and depends on:

- Bubblewrap;
- cgroup v2 availability and delegation;
- static worker/launcher binaries;
- local filesystem staging.

That is useful for a Linux local executor, but it is not a portable environment solution for:

- macOS developer machines;
- Windows without a Linux layer;
- Slurm clusters;
- managed Kubernetes;
- cloud batch services;
- GPU container runtimes;
- institutional HPC environments where unprivileged namespaces are disabled.

The system needs an executor-interface model in which Bubblewrap is one backend, not the universal isolation contract.

### 15.3 Trusted tasks are a larger reproducibility risk

Trusted in-process tasks run in fresh Goja runtimes with selected native modules, which limits accidental JavaScript authority. They still share the host process, dependencies, native module implementation, filesystem/runtime environment, and failure domain.

They should be limited to tiny, deterministic, first-party transforms. General scientific work should run out of process in a pinned environment.

---

## 16. Operational store versus research ledger

The SQLite schema is appropriate as an operational store. Node and run statuses must change, leases must be renewed, gates must be decided, and budgets must be settled.

It should not be described or used as the immutable research record:

- status rows are mutable;
- many foreign keys use `ON DELETE CASCADE`;
- the store supports additive in-place column migrations and backfills;
- artifact locators are local operational details;
- raw workflow state is organized for scheduling, not archival interchange.

Researchctl should ingest a terminal, validated execution manifest plus durable artifact references. The executor store may then be retained, compacted, archived, or garbage-collected according to policy.

This is an important positive boundary: Scraper does not need to become another immutable scientific ledger.

---

## 17. Implementation quality review

### 17.1 Strengths

The implementation shows a high level of care:

- unknown fields are frequently rejected;
- identities are validated before use;
- registries are sealed;
- exact implementation mismatches fail closed;
- SQL operations use transactions;
- SQLite is configured with foreign keys, WAL, full synchronization, busy timeout, and immediate transaction locking;
- stale completions are explicitly rejected;
- failure classes and codes are closed;
- maps and reductions are bounded;
- budgets have database constraints and reconciliation checks;
- external operations have admission and completion invariants;
- subprocess output and protocol sizes are bounded;
- isolation executable identities are hashed;
- output paths and filesystem types are checked;
- deterministic observation projection has source and result digests;
- tests target adverse behavior rather than only happy paths.

This is not a toy scheduler.

### 17.2 Maturity concerns

The code arrived as a large, recent hard-cut branch replacing the former site/scheduler/API/frontend stack. The branch documentation declares the previous product removed and Workflow V3 the sole lifecycle.

A hard cut can be the right design decision. It also means architecture, product surface, and operational assumptions have changed together. The absence of a visible CI result at the reviewed head matters because several integration tests require Linux-specific facilities such as static compilation, Bubblewrap, cgroup v2, and toolchain availability.

Before relying on the executor for consequential research, the project needs:

- branch-protected CI on the actual reviewed ref;
- published test matrices;
- Linux distributions and kernel configurations;
- cgroup/Bubblewrap capability probes;
- crash/power-loss tests for artifact and SQLite custody;
- large-data benchmarks;
- multi-process worker stress tests;
- long-running migration tests;
- compatibility fixtures for every public schema;
- release versioning and migration policy.

### 17.3 Specific technical concerns

1. **Canonicalization:** `json.Marshal` is called canonical without a cross-language canonicalization standard.
2. **Artifact memory:** whole-file `[]byte` APIs dominate the data path.
3. **Existing-object verification:** `Put` does not verify a preexisting object before returning its reference.
4. **Trusted module identity:** module aliases, not implementation digests, enter the registry generation.
5. **Workflow source provenance:** authoring source is not retained with the run.
6. **No computation cache:** no reviewed plan/runtime/schema object represents a reusable step materialization.
7. **Private per-attempt roots:** the Researchctl bridge prevents cross-attempt and cross-case reuse.
8. **Terminal-only artifact export:** intermediate step lineage does not cross the bridge.
9. **Static package composition:** runtime package selection is not dynamic package loading.
10. **Resource model:** resource classes are integer capacity buckets, not portable resource requests.
11. **Schema semantics:** schema strings are nominal and not tied to schema-document digests.
12. **Logs:** useful raw diagnostics are intentionally discarded rather than safely retained.
13. **Migration model:** the operational schema uses additive column detection/backfills rather than an explicit, audited migration ledger for long-lived installations.
14. **Polling density:** each active lease has a short periodic watcher, and dispatch/follow loops are polling based; this deserves scale testing.

---

## 18. Which features are overengineered or confusing?

The answer depends on level.

### 18.1 Not overengineered in the kernel

The following are justified by the problems they solve:

- lease fencing;
- append-only attempts;
- typed failure codes;
- resource-class dispatch;
- lazy maps;
- bounded reductions;
- external-operation admission/completion records;
- deterministic observations;
- exact restricted-executor identity.

### 18.2 Overexposed in the scientist-facing product

The user should not need to understand all of these before running a Python RAG pipeline:

- workflow IR versus plan;
- task key versus package version versus bundle digest;
- catalog digest;
- registry generation;
- module aliases;
- isolation maximum versus requested versus effective policy;
- isolation executor digest;
- budget account, claim, reservation, settlement, and approval gate;
- map page size and materialized-ahead limit;
- reduction fan-in and maximum levels;
- Researchctl run versus attempt versus Workflow run versus node attempt;
- separate state and artifact roots at both systems.

These concepts may remain in expert interfaces and diagnostics. The default experience should be substantially smaller.

### 18.3 Premature priorities

Rolling registry generations, quarantine, approval gates, and sophisticated budget accounting are valuable for a multi-tenant provider execution service. They have landed before:

- a standard command task;
- a Python task SDK;
- a container task;
- streaming artifacts;
- a shared cache;
- full environment capture;
- GPU resources;
- a portable remote executor.

For our RAG research platform, that is the wrong delivery order.

### 18.4 Naming confusion

The repository and product remain named “Scraper” while the branch removes the old site-oriented product and presents a generic workflow engine. A scientist will reasonably ask whether this is a web-scraping system, a workflow engine, a Researchctl runner, or a RAG execution platform.

If the kernel becomes the general Researchctl 2 executor, it should receive a neutral executor identity, even if the source code is initially extracted from this repository.

---

## 19. Needs that are not adequately addressed

### 19.1 Scientific task environments

Missing first-class support for:

- Python wheels and lockfiles;
- Conda/uv/Poetry environments;
- R environments;
- Julia projects;
- OCI images by digest;
- Nix derivations;
- compiled binaries and shared libraries;
- CUDA/ROCm runtimes;
- notebooks as recorded analyses;
- source repositories and commits.

### 19.2 Data-scale artifacts

Missing:

- streaming;
- remote CAS;
- directory/tree manifests;
- large table/index formats;
- import by path without memory copies;
- locality-aware materialization;
- retention and GC.

### 19.3 Cross-study and cross-case reuse

Missing:

- step execution fingerprints;
- global cache entries;
- compatibility policies;
- materialized-from lineage;
- cache invalidation by environment/hardware/provider identity;
- cache verification and quarantine;
- cache scope and access control.

### 19.4 Full retrospective provenance

Missing or incomplete:

- workflow source artifact;
- compiler version;
- host binary and module implementation identities;
- realized resource and hardware facts;
- environment snapshot;
- complete intermediate artifact graph;
- task logs;
- explicit cache decisions;
- standard provenance export.

### 19.5 Distributed and institutional execution

Missing first-class adapters for:

- Slurm;
- Kubernetes;
- cloud batch;
- remote agents;
- object-store staging;
- worker authentication;
- multi-tenant authorization;
- quotas by project/user;
- durable service deployments beyond shared SQLite.

### 19.6 Rich RAG data operations

The generic engine can host domain tasks, but its collection primitives do not directly cover:

- dataset joins;
- sharded Parquet/Arrow tables;
- incremental index construction;
- distributed embedding batches;
- query-result table partitions;
- many-to-many lineage;
- streaming generation;
- partial dataset reuse;
- hierarchical document/chunk/question relationships.

These should primarily be domain/compiler concerns, but the generic artifact and execution contracts must accommodate them.

---

## 20. How this should fit into Researchctl 2

### 20.1 Correct ownership

Researchctl 2 should own:

- protocols and revisions;
- hypotheses and outcomes;
- cases and factor roles;
- blocks and randomization;
- assignments and replicates;
- exclusion/replacement policy;
- study stages and holdouts;
- execution occurrences;
- analysis activities;
- evidence and decisions;
- reproducibility packages.

The executor should own:

- step DAG execution;
- attempts and leases;
- task-level retries;
- scheduling and resources;
- external operations;
- working directories;
- logs;
- output verification;
- materialization cache;
- operational observations.

The RAG domain compiler should own:

- RAG pipeline semantics;
- conditional graph construction;
- RAG schemas;
- task implementations;
- domain metric projection;
- factor-to-step invalidation rules.

### 20.2 The executor should consume plans, not own the user DSL

Researchctl and the RAG compiler should emit a generic `ExecutionPlan`. Scraper-derived code should validate and execute it.

The executor does not need to evaluate `workflow.js` in the authoritative path. JavaScript, Python, YAML, or another authoring frontend can compile into the same plan, but the plan is the interface.

### 20.3 One executor service, many occurrence records

Replace the current bridge:

```text
one Researchctl attempt
    -> one private SQLite file
    -> one private artifact root
```

with:

```text
Researchctl occurrence request
    -> shared executor service
        + occurrence-state store
        + shared CAS
        + shared materialization cache
        + backend adapters
```

Each request still has a unique occurrence ID and isolated logical namespace. Shared storage does not imply semantic reuse; the cache policy decides reuse explicitly.

### 20.4 Terminal execution manifest

The executor should return a compact manifest containing:

- plan ID and digest;
- occurrence and invocation IDs;
- every step occurrence;
- attempts and failures;
- exact task/environment/executor identity;
- input and output artifact edges;
- cache disposition;
- realized resources;
- external operations;
- log artifact refs;
- final outputs;
- operational observation digest;
- terminal status.

Researchctl persists this manifest and links it to the scientific run. Large bytes remain in a verified artifact store.

---

## 21. Fundamental shift in scripting patterns

### 21.1 Current pattern

```text
Go-embedded CommonJS task source
    + Go bundle manifest
    + Go descriptor module
    + Go native modules
    + JavaScript workflow DSL
    -> Go-compiled plan
    -> Goja/Bubblewrap execution
```

### 21.2 Recommended pattern

```text
ordinary task code
  Python / R / shell / Julia / binary / container
        |
        v
small task contract
  request.json + inputs + outputs + result.json
        |
        v
canonical execution plan
        |
        v
executor backend
  local process / OCI / Slurm / Kubernetes / cloud batch / trusted Goja
```

### 21.3 Task specification example

```yaml
schemaVersion: researchctl-execution-task/v1
id: rag.chunk
implementation:
  kind: container-command
  image: ghcr.io/example/rag-steps@sha256:...
  command:
    - python
    - -m
    - rag_steps.chunk
    - --request
    - /run/request.json
source:
  repository: https://example.org/rag-study.git
  commit: 6f2d...
inputs:
  documents:
    logicalType: rag/document-set/v1
outputs:
  chunks:
    logicalType: rag/chunk-set/v1
parameters:
  method: structural
  targetTokens: 512
  overlapTokens: 64
resources:
  cpu: 4
  memoryBytes: 8589934592
  ephemeralDiskBytes: 21474836480
network:
  policy: none
cache:
  mode: exact
reproducibilityClass: deterministic-logical
```

### 21.4 File-based worker contract

```text
/run/
  request.json
  inputs/
  work/
  outputs/
  result.json
  logs/
    stdout.log
    stderr.log
  telemetry/
```

`result.json` declares outputs, observations, and terminal status. The executor verifies and imports files without serializing their contents into lifecycle messages.

### 21.5 Goja's future role

Retain Goja for:

- optional plan authoring;
- tiny trusted deterministic transforms;
- interactive inspection;
- domain-specific convenience builders.

Do not require it for general scientific execution.

---

## 22. Target executor architecture

```text
+------------------------------------------------------------------+
| Researchctl 2                                                     |
| protocol, study, assignments, scientific runs, evidence           |
+-------------------------------+----------------------------------+
                                |
                      ExecutionPlan + occurrence ID
                                |
+-------------------------------v----------------------------------+
| Executor service                                                   |
|                                                                    |
|  Plan validator       Occurrence store       Materialization cache |
|  Capability policy    Attempt/lease store    Observation projector |
|  Secret broker        Log policy             Provenance exporter   |
+-------------+----------------------+-------------------------------+
              |                      |
              v                      v
+-------------------------+   +-------------------------------------+
| Shared artifact layer   |   | Backend adapters                    |
| local CAS / S3 / OCI    |   | local / container / Slurm / K8s     |
| streams / trees / GC    |   | cloud batch / trusted Goja          |
+-------------------------+   +-------------------------------------+
```

### 22.1 Core records

```text
execution_occurrence
step_occurrence
step_attempt
materialization
cache_entry
artifact
artifact_derivation
resource_realization
external_operation
log_artifact
observation_set
terminal_execution_manifest
```

### 22.2 Separate IDs

```text
scientific run ID           Researchctl occurrence
executor invocation ID      one request to executor
workflow occurrence ID      one DAG occurrence
step occurrence ID          node in that occurrence
attempt ID                  technical try
materialization ID          reusable computation result
artifact digest             immutable bytes/tree
cache fingerprint           eligibility identity
```

### 22.3 Cache fingerprint

At minimum:

```text
implementation/source digest
+ command/entrypoint
+ environment or OCI digest
+ canonical parameters
+ exact input artifact digests
+ executor semantics version
+ relevant secret/provider reference versions
+ RNG implementation and seeds
+ relevant hardware compatibility class
+ cache-policy version
```

A task may declare `cache: disabled`, `exact`, or a named compatibility policy. Compatible reuse must be explicit and auditable.

---

## 23. Required artifact API

A replacement interface should be closer to:

```go
type ArtifactStore interface {
    BeginPut(ctx context.Context, meta Metadata) (Writer, error)
    ImportPath(ctx context.Context, path string, meta Metadata) (Ref, error)
    PutTree(ctx context.Context, root string, meta Metadata) (Ref, error)
    Open(ctx context.Context, ref Ref) (io.ReadCloser, error)
    OpenRange(ctx context.Context, ref Ref, offset, length int64) (io.ReadCloser, error)
    Materialize(ctx context.Context, ref Ref, target string, mode MaterializeMode) error
    Stat(ctx context.Context, ref Ref) (Metadata, error)
    Verify(ctx context.Context, ref Ref) error
    Delete(ctx context.Context, ref Ref, authorization DeletionAuthorization) error
}
```

Backends can include:

- local filesystem CAS;
- S3-compatible object storage;
- OCI registry;
- institutional archive;
- read-through catalog references.

A tree manifest should support directories and sharded datasets without packing everything into one in-memory archive.

---

## 24. Concrete RAG materialization behavior

For a study with many cases, the executor/cache graph should look like:

```text
corpus digest
  |
  +-- parse config A ------------------------------> document set A
  |                                                   |
  |                                                   +-- chunk config X -> chunk set AX
  |                                                   |                    |
  |                                                   |                    +-- summary config S -> summaries AXS
  |                                                   |                    +-- question config Q -> questions AXQ
  |                                                   |                    +-- embed config E1 -> embeddings AXE1
  |                                                   |                    |                       |
  |                                                   |                    |                       +-- vector index V1
  |                                                   |                    +-- lexical config L1 -> lexical index L1
  |                                                   |
  |                                                   +-- chunk config Y -> ...
  |
  +-- parse config B ------------------------------> document set B
```

Downstream query materializations then key off exact upstream artifact digests:

```text
(vector index, lexical index, query set, retrieval config)
    -> retrieval candidates

(retrieval candidates, fusion/rerank config)
    -> ranked contexts

(ranked contexts, answer prompt/model/seed)
    -> answers

(answers, judgments, evaluator config)
    -> evaluation table
```

Each scientific assignment references the materializations it used. Identical materializations may be reused by many assignments without merging their scientific occurrence records.

---

## 25. Recommended user experience

A scientist should see:

```bash
researchctl protocol validate protocol.yaml
researchctl study freeze study.yaml
researchctl study explain STUDY-ID
researchctl study run STUDY-ID --executor local
researchctl study status STUDY-ID
researchctl run inspect RUN-ID
researchctl artifact inspect sha256:...
researchctl study snapshot STUDY-ID --out analysis/
researchctl pack STUDY-ID --format workflow-run-ro-crate
```

The RAG domain package should provide Python-facing authoring:

```python
from researchctl_rag import pipeline

p = (
    pipeline("rag-v4")
    .documents("corpus")
    .chunk(method="structural", target_tokens=512, overlap_tokens=64)
    .summarize(model="summary-small", prompt="summary-v3")
    .embed(model="embed-large-v3", batch_size=128)
    .hybrid_retrieve(top_k=20, alpha=0.5)
    .rerank(model="cross-encoder-v2", candidates=20)
    .answer(model="answer-large", prompt="answer-v4")
    .evaluate(dataset="eval-holdout-v2")
)

p.write_execution_template("rag-pipeline.compiled.json")
```

Researchctl freezes the resulting canonical data. The executor never imports this Python SDK.

---

## 26. What to copy, refactor, or discard

### 26.1 Copy or extract with limited changes

- lease token and cancellation-epoch semantics;
- append-only node attempts;
- typed failure vocabulary;
- transactional resource admission;
- retry scheduling;
- work-conserving dispatcher;
- map paging and deterministic item keys;
- external-operation admission/completion ledger;
- budget reservation/settlement logic where needed;
- deterministic observation projection;
- restricted output-tree validation;
- executable digest helpers;
- adversarial isolation tests;
- SQLite durability configuration and reconciliation checks.

### 26.2 Refactor substantially

- artifact store into streaming/tree/remote interfaces;
- registry into a language-neutral implementation registry;
- resource classes into structured requests plus backend-specific placement;
- task bundles into source/environment/command identities;
- observation source into a complete execution manifest;
- Researchctl runner into a service/adapter with shared CAS and cache;
- isolation into backend adapters;
- plan digest into standardized canonicalization;
- logs into policy-controlled artifacts;
- schema strings into typed schema identities.

### 26.3 Remove from the authoritative path

- requirement that workflows be authored in JavaScript;
- requirement that tasks be CommonJS embedded in Go;
- stock task-package selection pretending to be dynamic loading;
- per-Researchctl-attempt private database/artifact roots;
- base64 artifact transport in runner frames;
- terminal-output-only provenance;
- trusted native module aliases without implementation identity;
- custom reducer restrictions as the only aggregation model.

### 26.4 Keep as optional advanced features

- JavaScript plan authoring;
- trusted Goja transforms;
- approval gates;
- budget gates;
- rolling registry generations;
- registry quarantine;
- provider-specific operation modules.

---

## 27. Priority roadmap

### Phase 0 — Freeze the executor boundary

1. Define a language-neutral `ExecutionPlan` schema.
2. Define occurrence, step, attempt, materialization, cache, artifact, log, and terminal-manifest schemas.
3. Specify canonicalization and domain-separated digests.
4. Define executor capability negotiation.
5. Define full provenance transfer to Researchctl.

### Phase 1 — Fix the data plane

1. Introduce streaming artifact APIs.
2. Add tree and sharded-dataset manifests.
3. Add local shared CAS.
4. Add import/materialize without whole-memory copies.
5. Add object verification and repair.
6. Remove base64 artifact payloads from lifecycle protocols.

### Phase 2 — Add ordinary task execution

1. Local command task.
2. OCI container task by digest.
3. Python task helper.
4. R and Julia command compatibility.
5. Canonical parameters.
6. Environment/source manifests.
7. stdout/stderr/log artifacts.

### Phase 3 — Add shared materialization caching

1. Exact execution fingerprints.
2. Global cache index.
3. Cache hit/miss/rejected records.
4. Materialized-from provenance.
5. Cache verification and quarantine.
6. Scope, retention, and access policy.
7. RAG invalidation acceptance tests.

### Phase 4 — Replace the Researchctl bridge

1. Shared executor service or workspace daemon.
2. Stable invocation IDs and reconnect semantics.
3. Full terminal execution manifest.
4. Intermediate artifact lineage.
5. No duplicate byte copies.
6. Clear nested retry terminology.

### Phase 5 — Structured resources and backends

1. CPU/memory/disk requests.
2. GPU model/count/memory and driver evidence.
3. Bubblewrap local backend.
4. OCI backend.
5. Slurm adapter.
6. Kubernetes or cloud-batch adapter.
7. Realized-resource provenance.

### Phase 6 — Simplify product surface

1. Make plan JSON the authoritative executor input.
2. Move JavaScript DSL to an optional SDK.
3. Move gates/budgets/registry operations to expert documentation.
4. Provide one Python-based RAG tutorial.
5. Rename/extract the generic executor from Scraper branding.

---

## 28. Required acceptance study

The executor should not be accepted based on fixture echo tasks. A final RAG acceptance study should prove:

### Scientific design

- at least 20 cases;
- at least 3 replicate assignments per finalist;
- chunking, enrichment, retrieval, answer, and concurrency factors;
- development and frozen holdout stages.

### Shared reuse

- one corpus parse reused across compatible cases;
- chunk sets reused where chunk factors match;
- summaries/questions reused where enrichment factors match;
- embedding sets reused where representation factors match;
- indexes reused across retrieval/answer cases;
- retrieval results reused across answer-prompt comparisons;
- every reuse recorded as a new occurrence with `materialized-from` provenance.

### Artifacts

- corpus and chunk datasets larger than 64 MiB;
- embedding and index artifacts larger than 1 GiB;
- tree/sharded artifacts;
- local and remote backend round trips;
- verification after process restart;
- retention and GC dry run.

### Environments

- Python container by digest;
- CPU and GPU steps;
- exact source commit;
- lockfile/image identity;
- recorded hardware and drivers;
- provider-dependent step classification.

### Failure and recovery

- worker crash;
- parent/bridge crash and reconnect;
- lease loss;
- provider timeout;
- partial external operation;
- failed cache candidate;
- corrupt artifact;
- canceled study;
- replacement run;
- no duplicate scientific replicate counting.

### Provenance

- complete step DAG;
- all input/output edges;
- logs;
- cache decisions;
- external operations;
- operational observations;
- Researchctl run link;
- portable research-object export.

---

## 29. Final scorecard

These scores assess the reviewed branch for the specific role of executing a reproducible RAG experiment program, not as a generic code-quality grade.

| Area | Score | Rationale |
|---|---:|---|
| Durable local workflow kernel | 8.5/10 | Strong leases, attempts, retries, cancellation, transactions, maps, reductions |
| Failure and stale-worker integrity | 9/10 | Explicit fencing and adversarial tests |
| External provider accounting | 8.5/10 | Sophisticated admission/completion and budget evidence |
| Small-artifact integrity | 7/10 | Digests and verification are good; existing-object and crash details remain |
| Large-artifact/data-plane fitness | 2/10 | Whole-file memory APIs, 64 MiB default, base64 bridge, no trees/remotes |
| Execution-environment reproducibility | 4/10 | Task bundles and restricted tools pinned; trusted host/runtime not fully identified |
| RAG factorial reuse | 1.5/10 | Per-attempt private stores and no generic cache/materialization model |
| Scientist task authoring | 2.5/10 | Requires static Go task-package composition and CommonJS/Goja task model |
| Workflow portability | 3/10 | Local SQLite/Goja/Bubblewrap architecture; no standard backend/task contract |
| GPU/HPC/cloud fit | 2.5/10 | String resource classes and Linux local isolation only |
| Operational observations | 8/10 | Deterministic, bounded, retry-aware, privacy-conscious |
| Full research provenance transfer | 4/10 | Plan/final outputs/observations pass through; intermediate graph and environment do not |
| New-user experience | 3/10 | Too many layers, flags, identities, and custom packages |
| Implementation discipline | 8/10 | Careful source and tests, with maturity/CI caveats |
| Potential after extraction/refactor | 9/10 | The durable kernel is a strong base for a clean executor |

---

## 30. Final recommendation

Do not discard Workflow V3. Do not adopt it unchanged.

The best path is to extract and reuse its durable kernel while replacing its public assumptions:

> Keep the state machine, leases, attempts, fencing, external-operation ledger, dispatcher, bounded fan-out, observation derivation, and adversarial isolation engineering. Replace JavaScript-centric task packaging, per-attempt storage islands, whole-byte artifact transport, terminal-only provenance, and the absence of global materialization caching.

In the clean Researchctl 2 architecture, the executor should be almost invisible to the scientist. It should accept a canonical plan generated by the RAG compiler, run ordinary pinned scientific tools, reuse compatible materializations, and return a complete execution manifest.

The governing sentence should be:

> **Researchctl decides which scientific occurrence is required; the RAG compiler decides which computation graph realizes it; the executor runs or safely reuses each materialization and records exactly what happened.**

Workflow V3 already contains much of the hardest machinery for the final clause. It needs a cleaner data plane and a far simpler, language-neutral front door.

---

# Appendix A — Evidence map

All links below are pinned to the reviewed commit.

## Product and architecture

- [`README.md`](https://github.com/wesen/scraper/blob/202229464629e2b6d0e193ff7798b16770b3a270/README.md)
- [`pkg/doc/topics/scraper-workflow-v3-product.md`](https://github.com/wesen/scraper/blob/202229464629e2b6d0e193ff7798b16770b3a270/pkg/doc/topics/scraper-workflow-v3-product.md)
- [`pkg/doc/topics/scraper-workflow-v3-minimal-runtime.md`](https://github.com/wesen/scraper/blob/202229464629e2b6d0e193ff7798b16770b3a270/pkg/doc/topics/scraper-workflow-v3-minimal-runtime.md)
- [`pkg/doc/topics/scraper-workflow-v3-observations.md`](https://github.com/wesen/scraper/blob/202229464629e2b6d0e193ff7798b16770b3a270/pkg/doc/topics/scraper-workflow-v3-observations.md)
- [`pkg/doc/topics/scraper-researchctl-runner.md`](https://github.com/wesen/scraper/blob/202229464629e2b6d0e193ff7798b16770b3a270/pkg/doc/topics/scraper-researchctl-runner.md)

## Contracts and compilation

- [`pkg/workflowv3/types.go`](https://github.com/wesen/scraper/blob/202229464629e2b6d0e193ff7798b16770b3a270/pkg/workflowv3/types.go)
- [`pkg/workflowv3/compiler.go`](https://github.com/wesen/scraper/blob/202229464629e2b6d0e193ff7798b16770b3a270/pkg/workflowv3/compiler.go)
- [`pkg/workflowv3/canonical.go`](https://github.com/wesen/scraper/blob/202229464629e2b6d0e193ff7798b16770b3a270/pkg/workflowv3/canonical.go)
- [`pkg/workflowv3/catalog.go`](https://github.com/wesen/scraper/blob/202229464629e2b6d0e193ff7798b16770b3a270/pkg/workflowv3/catalog.go)
- [`pkg/workflowv3/bundle.go`](https://github.com/wesen/scraper/blob/202229464629e2b6d0e193ff7798b16770b3a270/pkg/workflowv3/bundle.go)
- [`pkg/workflowv3/registry.go`](https://github.com/wesen/scraper/blob/202229464629e2b6d0e193ff7798b16770b3a270/pkg/workflowv3/registry.go)
- [`pkg/gojamodules/workflow/authoring.go`](https://github.com/wesen/scraper/blob/202229464629e2b6d0e193ff7798b16770b3a270/pkg/gojamodules/workflow/authoring.go)

## Runtime and persistence

- [`pkg/workflowv3/artifacts.go`](https://github.com/wesen/scraper/blob/202229464629e2b6d0e193ff7798b16770b3a270/pkg/workflowv3/artifacts.go)
- [`pkg/workflowv3/external_operation.go`](https://github.com/wesen/scraper/blob/202229464629e2b6d0e193ff7798b16770b3a270/pkg/workflowv3/external_operation.go)
- [`pkg/workflowv3/isolation.go`](https://github.com/wesen/scraper/blob/202229464629e2b6d0e193ff7798b16770b3a270/pkg/workflowv3/isolation.go)
- [`pkg/workflowv3runtime/engine.go`](https://github.com/wesen/scraper/blob/202229464629e2b6d0e193ff7798b16770b3a270/pkg/workflowv3runtime/engine.go)
- [`pkg/workflowv3runtime/dispatcher.go`](https://github.com/wesen/scraper/blob/202229464629e2b6d0e193ff7798b16770b3a270/pkg/workflowv3runtime/dispatcher.go)
- [`pkg/workflowv3runtime/modules.go`](https://github.com/wesen/scraper/blob/202229464629e2b6d0e193ff7798b16770b3a270/pkg/workflowv3runtime/modules.go)
- [`pkg/workflowv3runtime/isolation.go`](https://github.com/wesen/scraper/blob/202229464629e2b6d0e193ff7798b16770b3a270/pkg/workflowv3runtime/isolation.go)
- [`pkg/workflowv3sqlite/schema.sql`](https://github.com/wesen/scraper/blob/202229464629e2b6d0e193ff7798b16770b3a270/pkg/workflowv3sqlite/schema.sql)
- [`pkg/workflowv3sqlite/store.go`](https://github.com/wesen/scraper/blob/202229464629e2b6d0e193ff7798b16770b3a270/pkg/workflowv3sqlite/store.go)

## Product surface and task packages

- [`pkg/workflowv3product/application.go`](https://github.com/wesen/scraper/blob/202229464629e2b6d0e193ff7798b16770b3a270/pkg/workflowv3product/application.go)
- [`pkg/workflowv3product/service.go`](https://github.com/wesen/scraper/blob/202229464629e2b6d0e193ff7798b16770b3a270/pkg/workflowv3product/service.go)
- [`pkg/workflowv3product/packages.go`](https://github.com/wesen/scraper/blob/202229464629e2b6d0e193ff7798b16770b3a270/pkg/workflowv3product/packages.go)
- [`pkg/taskpackages/cookbooklinear/package.go`](https://github.com/wesen/scraper/blob/202229464629e2b6d0e193ff7798b16770b3a270/pkg/taskpackages/cookbooklinear/package.go)
- [`pkg/cmd/workflow_v3.go`](https://github.com/wesen/scraper/blob/202229464629e2b6d0e193ff7798b16770b3a270/pkg/cmd/workflow_v3.go)

## Observations and Researchctl bridge

- [`pkg/workflowv3observations/types.go`](https://github.com/wesen/scraper/blob/202229464629e2b6d0e193ff7798b16770b3a270/pkg/workflowv3observations/types.go)
- [`pkg/workflowv3observations/project.go`](https://github.com/wesen/scraper/blob/202229464629e2b6d0e193ff7798b16770b3a270/pkg/workflowv3observations/project.go)
- [`pkg/workflowv3sqlite/observations.go`](https://github.com/wesen/scraper/blob/202229464629e2b6d0e193ff7798b16770b3a270/pkg/workflowv3sqlite/observations.go)
- [`pkg/researchrunner/types.go`](https://github.com/wesen/scraper/blob/202229464629e2b6d0e193ff7798b16770b3a270/pkg/researchrunner/types.go)
- [`pkg/researchrunner/runner.go`](https://github.com/wesen/scraper/blob/202229464629e2b6d0e193ff7798b16770b3a270/pkg/researchrunner/runner.go)
- [`cmd/scraper-workflow-runner/main.go`](https://github.com/wesen/scraper/blob/202229464629e2b6d0e193ff7798b16770b3a270/cmd/scraper-workflow-runner/main.go)

## Tests and build

- [`pkg/workflowv3runtime/isolation_integration_test.go`](https://github.com/wesen/scraper/blob/202229464629e2b6d0e193ff7798b16770b3a270/pkg/workflowv3runtime/isolation_integration_test.go)
- [`.github/workflows/push.yml`](https://github.com/wesen/scraper/blob/202229464629e2b6d0e193ff7798b16770b3a270/.github/workflows/push.yml)
- [`Makefile`](https://github.com/wesen/scraper/blob/202229464629e2b6d0e193ff7798b16770b3a270/Makefile)

---

# Appendix B — Concise decision record

## Decision

Use Workflow V3 as an implementation source for the Researchctl 2 executor kernel, not as the final scientist-facing workflow product.

## Retain

Durable scheduling, attempt/lease semantics, fencing, external-operation accounting, deterministic observations, selected map/reduction mechanisms, and restricted local isolation.

## Replace

Artifact APIs, task packaging, workflow authoring, environment identity, resource model, caching, Researchctl bridge, and provenance export.

## Primary reason

The current system optimizes the correctness of an isolated workflow occurrence. Our RAG research program additionally requires efficient, provenance-preserving reuse of large intermediate materializations across many scientific occurrences.

