# Branch · Branch · Interpreter Constructs Analysis

- URL: https://chatgpt.com/c/6a5e2d99-3b2c-83ea-8ce3-c9bd9dcbd4e2
- Created: 2026-07-20T14:15:53.910Z

## Turn 0 - user

- Message ID: `6e1c4772-b38f-4bf3-b3fa-350b2775820f`

Study https://github.com/go-go-golems/tiny-idp/tree/task/prod-tiny-idp and write a textbook / report / analysis about all the interesting interpreter and goja constructs introduced to properly implement this, things like serialized continuations and invocation capabilities and deterministic callback registration and many more. There is a lot of interesting novel / rigorous interpreter work in there in say pkg/idp script and workflow and such , work done as part of ttmp TINYIDP-GOJA-001 .

## Turn 1 - assistant

- Message ID: `3c76bd06-9a2f-4b8a-be21-50b8c25dcc04`
- Model: `gpt-5-6-pro`

I’ll trace the branch architecture, commit history, and TINYIDP-GOJA-001 changes across `pkg/idp`, then produce a structured technical report emphasizing concrete code references and invariants.

## Turn 2 - assistant

- Message ID: `f91b53e6-2216-4460-b731-7a6d7669da61`
- Model: `gpt-5-6-pro`



## Turn 3 - assistant

- Message ID: `731076c3-cf3b-4c95-9066-92bc543585f5`
- Model: `gpt-5-6-pro`



## Turn 4 - assistant

- Message ID: `956a18f0-d3d5-44b1-a864-a7cdd03509c4`
- Model: `gpt-5-6-pro`

The branch reveals a lambda-first workflow machine: Goja-free serialized IR uses stable callback IDs, while browser waits persist versioned continuations that resume fresh, capability-bounded invocations.

## Turn 5 - assistant

- Message ID: `96531e76-c913-404e-aca4-0fb9be504318`
- Model: `gpt-5-6-pro`



## Turn 6 - assistant

- Message ID: `4fa89fcf-6273-4218-8d91-e54c4dcc612e`
- Model: `gpt-5-6-pro`

The key enforcement pattern is now clear: deterministic registration is checked across isolated runtimes, while opaque JavaScript executes within declared schemas, budgets, capabilities, outcomes, and native-committed effects.

## Turn 7 - assistant

- Message ID: `c56e1b8f-d016-44e4-a8f2-e5a79492288e`
- Model: `gpt-5-6-pro`



## Turn 8 - assistant

- Message ID: `99940c2d-9cef-4f12-b439-74c008a3597d`
- Model: `gpt-5-6-pro`



## Turn 9 - assistant

- Message ID: `49915920-89b1-4786-a8b6-84e8af086b7d`
- Model: `gpt-5-6-pro`

The full textbook draft is complete and undergoing layout checks. It distinguishes registry determinism from callback-state determinism and implemented guarantees from residual assurance gaps.

## Turn 10 - assistant

- Message ID: `8f1fcc2f-e1cb-4e8d-ba2b-f06b180128a4`
- Model: `gpt-5-6-pro`



## Turn 11 - assistant

- Message ID: `db9830c8-3dff-41ab-bf1b-27743fe719bb`
- Model: `gpt-5-6-pro`



## Turn 12 - assistant

- Message ID: `1af3bd52-cfa1-4e6d-abff-1ee78eb7df78`
- Model: `gpt-5-6-pro`



## Turn 13 - assistant

- Message ID: `85d85c96-1032-4cc8-9510-1ad74f67e46e`
- Model: `gpt-5-6-pro`



## Turn 14 - assistant

- Message ID: `02291538-8914-4a1c-8b3e-fe1331ce80e6`
- Model: `gpt-5-6-pro`



## Turn 15 - assistant

- Message ID: `37432ffa-a605-4757-b95e-f7e6b4801dbb`
- Model: `gpt-5-6-pro`



## Turn 16 - assistant

- Message ID: `c57a49c8-d3b8-47b7-9303-b413176b52ce`
- Model: `gpt-5-6-pro`



## Turn 17 - assistant

- Message ID: `7521ec4c-47f3-4681-b9f2-f12f303a8005`
- Model: `gpt-5-6-pro`



## Turn 18 - assistant

- Message ID: `b2f671b3-2778-4b2a-95f6-0a21c1a1dbfa`
- Model: `gpt-5-6-pro`



## Turn 19 - assistant

- Message ID: `59da3a7e-1181-4ab2-815c-794c4a480b88`
- Model: `gpt-5-6-pro`



## Turn 20 - assistant

- Message ID: `85cd0766-5690-4df9-ac82-6f0682655410`
- Model: `gpt-5-6-pro`



## Turn 21 - assistant

- Message ID: `366fb36e-1004-4e04-af23-c4b0d4554d37`
- Model: `gpt-5-6-pro`



## Turn 22 - assistant

- Message ID: `3c332246-dc8b-44be-a870-990afa2b0bbf`
- Model: `gpt-5-6-pro`



## Turn 23 - assistant

- Message ID: `3b1b2d38-fcc0-4be8-85b3-d3df09b7ab53`
- Model: `gpt-5-6-pro`



## Turn 24 - assistant

- Message ID: `9bdb7e7f-d4de-4ba5-bba1-59195aa82c1e`
- Model: `gpt-5-6-pro`



## Turn 25 - assistant

- Message ID: `71d6aef6-1b62-4de3-8a13-76b8b46f5327`
- Model: `gpt-5-6-pro`



## Turn 26 - assistant

- Message ID: `7a142f71-70dd-4a7b-b6c0-2da64a8ddbcd`
- Model: `gpt-5-6-pro`

# Interpreting Identity Safely

A 12,390-word technical monograph, rendered as a 42-page report, is complete.

- [Read the PDF](sandbox:/mnt/data/tiny-idp-goja-interpreter-monograph.pdf)
- [Download the editable DOCX](sandbox:/mnt/data/tiny-idp-goja-interpreter-monograph.docx)
- [View the Markdown source](sandbox:/mnt/data/tiny-idp-goja-interpreter-monograph.md)

The analysis is pinned to branch commit `d164ae59408bdd8bc21516274b446339b1761b1e` from July 20, 2026. fileciteturn73file0L1-L3

## Central conclusion

The implementation is better understood as a **collection of deliberately small interpreters around a Go identity microkernel**, rather than as an application that happens to embed JavaScript.

The report develops that interpretation through:

- **Definition-time staging:** trusted JavaScript constructs a pure, serializable `idpprogram.Program`, while Goja closures remain confined to a runtime-local callback registry. `pkg/idpprogram` intentionally has no Goja dependency and stores callback identifiers rather than functions. fileciteturn11file0L3-L20
- **Deterministic callback linking:** the compiled source is re-executed in independently owned runtimes, and workers are accepted only when exported program data, collected program data, callback sets, schema sets, and fingerprints agree. fileciteturn35file0L97-L179
- **Invocation capabilities:** each lambda receives only declared, versioned, byte-bounded and call-bounded native operations. Promise settlement is routed back through the runtime owner, and retained capability functions lose authority when the invocation ends.
- **Transactional worker leasing:** a runtime is reusable only after a positive safety proof—valid output, no uncertain interruption, and complete asynchronous settlement. Timeouts, exceptions, malformed results, cancellation races, and late settlements cause disposal and replacement. fileciteturn37file0L42-L176
- **Serialized continuations through defunctionalization:** browser waits do not serialize a Goja Promise, closure, stack, or heap. They persist a pure-Go record containing a resume-handler label, typed public environment, generation identity, revision, bindings, and native references. fileciteturn40file0L3-L84
- **Nominal branding by Goja object identity:** lambdas, fields, actions, and secrets are represented by blank JavaScript objects recognized through host-side identity maps, rather than forgeable object properties.
- **Typed presentation and exact POST projection:** scripts select host-registered UI descriptors; Go owns HTML names, normalization, sensitivity, redisplay policy, request parsing, CSRF handling, and rendering.
- **Opaque, request-scoped secret capabilities:** passwords are native byte buffers referenced by unforgeable Goja handles, not ordinary JavaScript strings.
- **Algebraic-effect-style commits:** JavaScript returns inert effect plans. Named native committers revalidate the exact effect sequence and apply identity, credential, continuation, session, invitation, and authorization changes atomically.
- **Native evidence:** verification codes and authoritative proof state remain native; scripts receive bounded evidence projections that they cannot manufacture themselves.
- **Generation-pinned semantic time:** continuations resume under the exact retained source and program generation that created them, rather than being silently reinterpreted after hot reload.
- **A separate verification interpreter:** test JavaScript compiles data-only scenario plans, which must be materialized through finite native step registries before execution.
- **Critical evaluation:** the report distinguishes implemented guarantees from remaining concerns such as persistent module state in reused workers, declared versus behavioral nondeterminism, generation-retention alignment, key rotation, mail-delivery transaction boundaries, and unfinished assurance consolidation.

The active design itself draws the essential line between in-request asynchronous work and browser-spanning durable control flow: ordinary `await` remains local to one invocation, while browser waits create explicit persisted continuations and later invoke a fresh handler. fileciteturn8file0L44-L91

The implementation ledger records the principal lambda-first runtime phases as complete, while cross-phase assurance consolidation and the final completion gate remain open. The report preserves that distinction rather than presenting the branch as a completed formal-verification system. fileciteturn65file0L103-L116

The PDF is the primary reading edition. The DOCX contains a static linked table of contents, verified page numbers, embedded fonts in the PDF export, 147 outline entries, and source hyperlinks pinned to the analyzed commit. Test claims in the text are attributed to repository records; the repository test suite was not independently re-executed in this environment.

## Turn 27 - user

- Message ID: `2ab9d19a-0502-4f2e-a3a6-9976e614247b`

Brainstorm and design how we can extract useful generic patterns out of this incredible work in order to create a “language / scripting platform design patterns Lego blocks framework” that allows other programs (from a scriptable 3d editor to a scriptable window manager to a webapp to an scriptable/entire embedded firmware to a scriptable full OS to a scriptable compiler, even proof assistant / formal method kernel ) to benefit and reuse this work.

## Turn 28 - assistant

- Message ID: `72b205cb-895a-42c0-b990-6a015f5012c2`
- Model: `gpt-5-6-pro`

I’ll extract Tiny-IDP’s mechanisms into a reusable pattern catalog, then design a concrete framework with composable packages, contracts, profiles, and cross-domain adaptations.

## Turn 29 - assistant

- Message ID: `b9701e0a-f53a-4d90-86a8-f8fab0b8c5a1`
- Model: `gpt-5-6-pro`



## Turn 30 - assistant

- Message ID: `183c5bb1-2c8e-4101-b9d5-07fa083623c4`
- Model: `gpt-5-6-pro`



## Turn 31 - assistant

- Message ID: `a8949af7-ce47-4a42-82f1-b52b2ec7d251`
- Model: `gpt-5-6-pro`



## Turn 32 - user

- Message ID: `2e926f59-1cb2-4d5f-b847-fbb5e2e0da80`

This is really about both a concrete go-go-goja based framework, and also a general framework for programming language interpreter/compiler work that can be applied across languages and projects

## Turn 33 - assistant

- Message ID: `00f236e0-edab-442f-ae13-bb711e2804c6`
- Model: `gpt-5-6-pro`

The framework will have two layers: a production Goja toolkit and a language-neutral, host-governed scripting microkernel built around staged IR, scoped capabilities, explicit suspension, and native effects.

## Turn 34 - assistant

- Message ID: `bfb8fd8a-4f99-48b0-9afd-5cb9e0b47f80`
- Model: `gpt-5-6-pro`



## Turn 35 - user

- Message ID: `8670057f-f78d-43a6-9859-c1ecb98f50ba`

Feel free to also look at all the work here https://parc.yolo.scapegoat.dev/note/research/kb/projects/go-go-goja and what patterns were discovered and used there (or https://parc.yolo.scapegoat.dev/note/research/kb/projects/widget-dsl and https://parc.yolo.scapegoat.dev/note/research/kb/projects/researchctl)

## Turn 36 - assistant

- Message ID: `ef62032f-4ccf-4368-a353-01e6ad13e56a`
- Model: `gpt-5-6-pro`

I’ll synthesize recurring patterns across Tiny-IDP and the related projects into reusable Go/Goja components and language-agnostic primitives, including APIs, composition rules, assurance levels, and an implementation roadmap.

## Turn 37 - assistant

- Message ID: `51ff3fda-02f8-432a-b1a1-e57a5703792d`
- Model: `gpt-5-6-pro`



## Turn 38 - assistant

- Message ID: `d4688af0-93b0-4ab3-bbe3-464bb8a7a08c`
- Model: `gpt-5-6-pro`



## Turn 39 - assistant

- Message ID: `ae8e047d-0be8-4f98-a1c1-40256246e048`
- Model: `gpt-5-6-pro`



## Turn 40 - assistant

- Message ID: `254deb73-26db-4935-9a02-2fa0fd442869`
- Model: `gpt-5-6-pro`



## Turn 41 - assistant

- Message ID: `0e6bcbe6-43d0-4a3f-b1dd-5273af29622f`
- Model: `gpt-5-6-pro`



## Turn 42 - assistant

- Message ID: `3d7b1e55-4681-49bb-b286-a1363a2cb665`
- Model: `gpt-5-6-pro`

The design is converging on a small semantic kernel with replaceable blocks for authority, staging, IR verification, lowering, scheduling, effects, lifecycle, evidence, and assurance.

## Turn 43 - assistant

- Message ID: `3c5c5caf-f545-4920-99cc-8068c44f216c`
- Model: `gpt-5-6-pro`



## Turn 44 - assistant

- Message ID: `abf3178c-8ea8-458e-8388-a8e12cbbd8cd`
- Model: `gpt-5-6-pro`



## Turn 45 - assistant

- Message ID: `09ab1211-b926-4a6c-a77a-58495c87b825`
- Model: `gpt-5-6-pro`



## Turn 46 - assistant

- Message ID: `1e20cabd-9912-41f0-8b2f-b37aceee3fb5`
- Model: `gpt-5-6-pro`

The architecture will ship as three layers: a pattern language, machine-checkable block/plan specifications, and reference implementations. Activated generations freeze their runtime universe while preserving build-time extensibility.

## Turn 47 - assistant

- Message ID: `b9fa270e-d1d9-49f8-9dec-462dd6752289`
- Model: `gpt-5-6-pro`



## Turn 48 - assistant

- Message ID: `a8cf2998-1bb8-46ea-9f51-0636c52f8f97`
- Model: `gpt-5-6-pro`



## Turn 49 - assistant

- Message ID: `e08c8cc2-ff7e-4d69-aada-09b7fa94d998`
- Model: `gpt-5-6-pro`



## Turn 50 - assistant

- Message ID: `da713489-4762-4033-948c-c8bba16b12dd`
- Model: `gpt-5-6-pro`



## Turn 51 - assistant

- Message ID: `40a741c4-41f9-4628-82ba-10581c42f6fa`
- Model: `gpt-5-6-pro`

# Proposed extraction: **LangBlocks**

The correct extraction target is not a larger collection of Goja helpers and not a universal workflow engine. It is a **staged language-host architecture**: a family of independently composable mechanisms for authoring, compiling, activating, invoking, constraining, persisting, and verifying guest-language programs.

Tiny-IDP provides the high-assurance reference case. Its handler contract combines schemas, closed outcomes, required capabilities, permitted effects, and resource budgets while deliberately excluding the callback function itself. fileciteturn31file0L20-L38 Its invocation results belong to a closed family, and effect plans are explicitly requests that JavaScript cannot execute directly. fileciteturn32file0L11-L23 fileciteturn32file0L36-L64 Its durable continuation package explicitly excludes Goja values, functions, Promises, and goroutine-local state. fileciteturn34file0L3-L6

go-go-goja supplies the lower runtime substrate: immutable runtime-factory construction, per-instance runtime state, single-owner scheduling, lifecycle contexts, module composition, and generated hosts. The factory freezes validated module and initializer configuration before creating live runtimes. fileciteturn24file0L32-L48 fileciteturn24file0L124-L181 The runtime owner serializes calls and posts onto the VM scheduler and handles reentrant owner calls explicitly. fileciteturn29file0L92-L135 fileciteturn29file0L138-L188 xgoja already distinguishes provider packages compiled into the binary from modules selected into the runtime surface. fileciteturn41file0L22-L44

Widget DSL and DMETA contribute intent-level authoring, typed layered IRs, target ownership, and separate semantic versus visual testing. fileciteturn12file0L24-L46 fileciteturn19file0L20-L36 researchctl contributes the separation of graph construction from execution and the explicit promotion of execution artifacts back into authoritative research state. fileciteturn13file0L35-L53 fileciteturn13file0L92-L106

Together, these support a three-tier product architecture.

```text
┌──────────────────────────────────────────────────────────┐
│ LangBlocks Specification                                 │
│ Language-independent patterns, laws, manifests, profiles │
└──────────────────────────┬───────────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────────┐
│ go-go-langkit                                             │
│ Contracts, artifacts, outcomes, effects, continuations,  │
│ generations, diagnostics, conformance; no Goja dependency│
└──────────────────────────┬───────────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────────┐
│ go-go-goja/platformkit                                    │
│ Goja compilation, collectors, callback linking, handles, │
│ Promise settlement, invocation scopes, worker leasing    │
└──────────────────────────┬───────────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────────┐
│ Domain kits                                               │
│ Identity, 3D scenes, WM layouts, webapps, firmware,       │
│ compilers, proof states, renderers, committers            │
└──────────────────────────────────────────────────────────┘
```

## 1. The language-independent framework

### LangBlocks Specification

This should be a versioned pattern language, not merely a set of essays. Each block would declare:

```yaml
id: defunctionalized-continuation
version: 1
requires:
  - stable-callback-reference
  - canonical-wire-value
  - generation-identity
  - revisioned-store
provides:
  - restart-safe-resumption
conflicts:
  - serialized-vm-heap
  - persisted-invocation-capability
invariants:
  - environment contains no backend-owned values
  - resume handler resolves in the pinned generation
  - advancement uses compare-and-swap revision
conformance:
  - continuation-roundtrip
  - stale-generation-rejection
  - duplicate-resume-rejection
```

This gives the “Lego” analogy actual engineering meaning. Blocks have typed ports, prerequisites, conflicts, invariants, and tests. They are not merely reusable package names.

A platform manifest can select blocks and be checked by a `langblocks doctor` tool. It should catch contradictions such as:

- a durable continuation containing an invocation-scoped capability;
- async native operations without a runtime-owner settlement mechanism;
- pooled runtimes without a reset or poison policy;
- deterministic-execution claims that include unrecorded clock or network capabilities;
- an “atomic” plan containing uncoordinated email or device effects;
- target-independent IR containing React, X11, GPU, or other target-specific concepts;
- hostile-script profiles relying only on an in-process interpreter boundary.

### go-go-langkit

This would be a Go implementation of the semantic blocks, while remaining independent of Goja and any other guest language.

```text
go-go-langkit/
  contract/       programs, handlers, machines, authority declarations
  value/          canonical wire values and codecs
  schema/         pluggable type and information-flow systems
  diagnostic/     stable IDs, source spans, deterministic ordering
  artifact/       source, semantic, schema, profile, link and ABI identities
  registry/       stable symbols, manifests and dependency checks
  outcome/        domain-defined closed decision families
  effect/         effect plans, policies, commit models and receipts
  continuation/   defunctionalized continuation envelopes and stores
  generation/     activation, retention, migration and retirement
  event/          commands, events, projections, snapshots and transcripts
  assurance/      profiles, composition checks and proof obligations
  conformance/    backend-independent lifecycle and boundary tests
  descriptor/     API metadata for docs, schemas and language bindings
```

A critical rule is that none of these packages may contain `goja.Value`, `goja.Callable`, a Lua stack reference, a WASM memory pointer, or another runtime-owned object.

## 2. The five core algebras

The most important generalization is a set of small algebras, not one large API.

### Phase algebra

```text
source
  → parse
  → normalize
  → validate
  → compile/lower
  → link
  → activate
  → invoke
  → interpret
  → commit/persist
  → observe/verify
```

The runtime never sees raw DSL. This matches the recurring `DSL → normalized configuration → compiled plan → execute` pattern: defaults, reference resolution, and warnings belong before execution. fileciteturn14file0L16-L39

### Lifetime or region algebra

Every value and authority belongs to a lifetime:

```text
build
generation
runtime
session
invocation
async operation
durable continuation
system/external state
```

The governing law is:

> A longer-lived container cannot retain a shorter-lived authority-bearing value.

This rejects:

- a request context retained by a hardware listener;
- a capability function stored in a continuation;
- a Goja object stored in a database;
- a transaction handle retained after an invocation;
- a proof-goal pointer retained after its environment generation is unloaded.

Tiny-IDP already enforces part of this through invocation-local active flags and settlement tracking. Capability calls fail after the binding becomes inactive, and the invocation waits for pending settlements before completing. fileciteturn37file0L29-L39 fileciteturn37file0L78-L101 fileciteturn37file0L134-L203

### Authority algebra

Authority should narrow monotonically through five stages:

```text
compiled availability
  ⊇ runtime exposure
    ⊇ handler declaration
      ⊇ invocation binding
        ⊇ accepted effect
          ⊇ committed effect
```

This unifies several existing mechanisms:

- xgoja decides what provider code is compiled into a generated binary;
- its runtime plan selects which compiled modules are exposed and under which aliases; fileciteturn46file0L22-L33 fileciteturn46file0L56-L76
- a handler declares the capabilities and effects it requires;
- an invocation receives only matching capability versions;
- a native effect interpreter decides whether a proposed operation is valid;
- a transaction, kernel, hardware layer, or proof checker owns final commit authority.

This is stronger and more general than “safe modules versus unsafe modules.”

### Decision/effect algebra

Guest execution and authoritative mutation are separate judgments:

```text
invoke(handler, input, capabilities)
    → decision

interpret(decision, host state)
    → prepared transition plan

commit(prepared plan, authority)
    → receipt + new state
```

A decision controls interpreter flow. An effect requests mutation. A receipt records what the host actually accepted.

This pattern applies equally to:

- identity enrollment;
- a mesh transformation;
- a window layout operation;
- a compiler rewrite;
- a firmware actuator operation;
- a theorem declaration.

### Determinism algebra

“Deterministic” should not be one Boolean. The framework should distinguish:

- normalization determinism;
- definition and callback-registration determinism;
- execution determinism relative to inputs and capability transcript;
- scheduling determinism;
- effect determinism;
- replay determinism;
- reproducible-build identity.

Tiny-IDP already maintains separate source, program, callback-registry, and schema fingerprints rather than pretending one hash answers every identity question. fileciteturn33file0L14-L21 fileciteturn33file0L33-L60

## 3. The central reusable patterns

The design report develops 38 pattern cards. The most important initial extraction set is:

| Pattern | Purpose |
|---|---|
| Semantic firewall | Stable state contains no runtime-owned objects |
| Stable callback reference | Serializable IDs link to VM-local closures |
| Deterministic activation | Re-materialized workers must agree on contracts and registries |
| Frozen factory, live instance | Composition policy is immutable; runtime state is per-instance |
| Single-owner runtime | All VM operations cross one scheduling boundary |
| Named cancellation domains | Startup, lifetime, invocation and external-event cancellation differ |
| Invocation task group | Invocation cannot finish with unsettled host work |
| Transactional runtime lease | Uncertain workers are destroyed rather than returned |
| Invocation capability lease | Authority is explicit, versioned, bounded and revocable |
| Opaque nominal handle | Native references cannot be forged from visible properties |
| Closed decision algebra | Native host exhaustively interprets a finite result family |
| Effect plan, native interpreter | Guest proposes; native authority validates and commits |
| Defunctionalized continuation | Durable control is handler label plus typed environment |
| Generation-pinned resumption | Old state resumes under the exact semantic generation |
| Layered IR with target ownership | Universal semantics do not absorb target implementation |
| Typed presentation instance | Scripts select registered presentations rather than generating target code |
| Separate verification language | Test scripts compile to data-only scenarios |
| Explicit evidence promotion | Execution does not silently rewrite authoritative knowledge |
| Descriptor as tooling truth | Runtime API, docs, schemas and generated bindings share metadata |
| Semantic promotion ladder | Mature callbacks can become declarative or native primitives |

Runtime poisoning deserves special emphasis. Tiny-IDP marks an invocation unsafe after interruptions, invocation errors, malformed output, or failed settlement; its pool releases only safe workers and replaces discarded ones. fileciteturn36file0L42-L88 fileciteturn36file0L152-L176 fileciteturn38file0L82-L117 This should become a generic `RuntimeDisposition`, separate from the domain result:

```go
type RuntimeDisposition string

const (
    Reuse      RuntimeDisposition = "reuse"
    Destroy    RuntimeDisposition = "destroy"
    Quarantine RuntimeDisposition = "quarantine"
)
```

A valid business result does not imply that the runtime is safe to reuse.

## 4. Concrete Go/Goja framework

The current go-go-goja substrate should be preserved rather than rewritten. `RuntimeFactory.NewRuntime` already creates a VM, event loop, owner, lifetime context, runtime services, registry, modules, and initializers. fileciteturn24file0L184-L238 fileciteturn24file0L240-L291

The new layer should sit above it:

```text
go-go-goja/pkg/platformkit/
  compiler/       SourceBundle → goja.Program
  definition/     collectors and callback manifests
  activation/     materialize, canonicalize, compare and link
  invoke/         value projection, Promise bridge and task drain
  capability/     invocation leases and resource meters
  brand/          generic VM-local nominal handle registries
  pool/           exclusive leases and disposition policies
  descriptor/     module surfaces, TS declarations, docs and schemas
  testing/        Goja backend conformance vectors
```

A reusable invocation scope would own:

```go
type InvocationScope struct {
    Context       context.Context
    Active        atomic.Bool
    Capabilities  CapabilityLeaseSet
    Handles       HandleSet
    Secrets       SecretSet
    Evidence      EvidenceSet
    Tasks         TaskGroup
    Budget        ResourceMeter
    Trace         TraceSink
}
```

All invocation-installed host functions close over this scope. Closing the scope revokes retained guest references, cancels work, drains settlements, and determines runtime disposition.

The Tiny-IDP collector demonstrates how a reusable nominal-brand registry can work. It stores callback, lambda-handle, field, and action identities in host maps keyed by `*goja.Object`; JavaScript-visible properties do not define validity. fileciteturn39file0L41-L68 Its lambda builder records the callable privately and returns a blank object whose identity is registered by the host. fileciteturn39file0L122-L155 The generic pattern is not “use a Goja object pointer”; it is **opaque nominal handle backed by a host authority table**.

## 5. Assurance profiles

Not every scripting system needs Tiny-IDP’s full rigor. The framework should provide cumulative profiles.

| Profile | Intended use | Required mechanisms |
|---|---|---|
| **W — Workbench** | Trusted REPLs and local automation | Explicit lifetime, owner, close, tracing |
| **A — Application** | Scriptable apps and generated hosts | Frozen factory, module profiles, canonical boundaries, descriptors |
| **C — Contracted** | Plugins, handlers, compiler passes | Handler contracts, capabilities, outcomes, budgets, runtime disposition |
| **D — Durable** | Workflows, modal tools, jobs, proof sessions | Continuations, revisions, generations, migration and replay policy |
| **K — Kernel-adjacent** | Identity, authorization, firmware, OS policy, proof validity | Native effect validation, independent checker, evidence, minimal TCB, stronger isolation |

A high-assurance profile is not an assertion that an in-process interpreter safely executes hostile code. The go-go-goja runtime notes explicitly state that hard CPU limits require a process boundary. fileciteturn16file0L193-L195

## 6. Domain reuse

| Domain | Contracted computation | Capabilities | Effect plan | Durable state |
|---|---|---|---|---|
| 3D editor | Tool or operator handler | Selection, raycast, asset queries | Scene operations and undo transaction | Modal tool continuation |
| Window manager | Rule, event or command handler | Window/workspace snapshot | Focus, move, resize, map, spawn | Input mode or accept continuation |
| Webapp | Route, form or policy handler | DB query, principal, cache | DB mutation, outbox, session transition | Multi-page workflow |
| Firmware | Bounded bytecode handler | Sensor, GPIO, bus, storage | Register/device operation | Revisioned flash record |
| Full OS | Process or service extension | IPC and kernel object handles | Typed syscall/service request | Job or UI session |
| Compiler | Compiler pass | AST, symbol and analysis queries | Rewrite plan and diagnostics | Incremental work unit |
| Proof assistant | Tactic or elaborator | Goals, lemmas and environment queries | Candidate theorem/proof term | Proof-state continuation |

For a proof assistant, `DeclareTheorem` should use a **kernel-check commit model**:

```text
tactic returns candidate term
  → resolve exact environment generation
  → parse canonical term representation
  → native kernel type-checks independently
  → theorem store commits only after successful checking
```

The tactic runtime, search strategy, UI, and most of LangBlocks can remain outside the trusted computing base.

## 7. Recommended implementation order

The first slice should remain deliberately narrow:

1. Extract `ProgramContract`, `HandlerContract`, deterministic diagnostics, canonical values, artifact identities, and callback manifests into `go-go-langkit`.
2. Build the Goja definition collector, activation linker, invocation scope, capability lease, task drain, Promise bridge, and runtime disposition above the existing go-go-goja engine.
3. Rebase Tiny-IDP onto those blocks without weakening any existing invariant.
4. Add one small non-identity reference domain: a revisioned scene graph with query capabilities and a validated transform effect.
5. Add generic continuations and generation management using Tiny-IDP as the reference implementation.
6. Add Widget DSL or researchctl as a contrasting compilation-oriented consumer.
7. Implement a second backend—Starlark for a restricted language or WASM for a stronger serialized boundary—to expose accidental Goja assumptions.
8. Turn lifecycle machines and composition rules into conformance tests and model-checkable specifications.

The extraction should be rejected wherever it makes Tiny-IDP’s current invariants less explicit. Genericity is useful only when it preserves the proof obligations.

## Design artifacts

- [Full LangBlocks framework design](sandbox:/mnt/data/langblocks-framework-design.md) — 9,481 words covering the architecture, 38-pattern catalog, formal judgments, lifecycle state machines, assurance profiles, Go APIs, package layout, domain mappings, risks, and extraction sequence.
- [Core machine-readable pattern catalog](sandbox:/mnt/data/langblocks-core-patterns.yaml) — proposed pattern dependencies, conflicts, invariants, and conformance tests.
- [Scriptable 3D editor platform manifest](sandbox:/mnt/data/langblocks-scene-editor-example.yaml) — concrete example showing handlers, capabilities, effects, worker policy, continuations, presentation, and assurance composition.

The architectural thesis is:

> **Compile human intent into stable semantic contracts; instantiate runtimes under explicit profiles; lease bounded authority to named computations; require typed decisions instead of ambient mutation; interpret effects in a native kernel; represent long-lived control as versioned data; and make each transition inspectable, replayable, or independently checkable according to an explicit assurance profile.**

