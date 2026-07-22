# Branch · Interpreter Constructs Analysis

- URL: https://chatgpt.com/c/6a5e1c8b-779c-83ea-80ab-cf68e7cb8e00
- Created: 2026-07-20T13:03:08.643Z

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

- Message ID: `935f70bb-d8ac-432f-840a-e9e8afb7ee28`

Research and brainstorm how having access to the goja interpreter or in fact creating our own js interpreter / compiler would influence such a design and potentially make it more usable / elegant / robust / verified / allow new software design patterns both on the implementation of the idp framework and on the side of the plugin/script writers. 

One could also imagine making the js interpreter / compiler malleable and extensible, so that one could extend it in different ways for different projects, not just tiny-idp .

Write a similar doc

## Turn 28 - assistant

- Message ID: `a249e686-304b-424b-8f5e-aac5d54c5893`
- Model: `gpt-5-6-pro`

I’ll map Goja’s extension boundaries, compare deeper integration, forked-Goja, compiler-front-end, and purpose-built runtime options, then derive Tiny-IDP patterns, cross-project architecture, risks, and a staged roadmap.

## Turn 29 - assistant

- Message ID: `2e308820-986a-4383-b4c0-18a67537aa94`
- Model: `gpt-5-6-pro`



## Turn 30 - assistant

- Message ID: `81863742-78a3-4f09-8522-6a9df3388e11`
- Model: `gpt-5-6-pro`



## Turn 31 - assistant

- Message ID: `1ea6a315-d232-42b3-b8d8-28016cbc82f7`
- Model: `gpt-5-6-pro`



## Turn 32 - assistant

- Message ID: `657cb3a7-be5d-4180-8886-c5e18f8e9b00`
- Model: `gpt-5-6-pro`



## Turn 33 - assistant

- Message ID: `87662c79-6d4c-47f9-a150-66efcfea05e3`
- Model: `gpt-5-6-pro`



## Turn 34 - assistant

- Message ID: `f5a5acd0-55e5-4460-8fb1-128fdedc7e5e`
- Model: `gpt-5-6-pro`



## Turn 35 - assistant

- Message ID: `8e23e267-f0f5-4d5b-90ec-28fdca153b55`
- Model: `gpt-5-6-pro`

The central question is whether ownership, branding, metering, resumability, finite registries, and exact codecs remain host conventions or become intrinsic semantics without creating a monolithic trusted runtime.

## Turn 36 - assistant

- Message ID: `8c07c2e4-e148-4f42-ae75-263e9e86a28e`
- Model: `gpt-5-6-pro`



## Turn 37 - assistant

- Message ID: `f526d035-6322-4176-ac5f-5309f44c2691`
- Model: `gpt-5-6-pro`



## Turn 38 - assistant

- Message ID: `3e02d68d-819d-4415-91b0-a7f5521c4d88`
- Model: `gpt-5-6-pro`



## Turn 39 - assistant

- Message ID: `46fdbb96-e1bd-48cb-880b-5e9b1cca0abd`
- Model: `gpt-5-6-pro`



## Turn 40 - assistant

- Message ID: `41699096-b737-44ad-96eb-4fefa640b3a2`
- Model: `gpt-5-6-pro`



## Turn 41 - assistant

- Message ID: `f0ba1b3e-e25f-4128-8647-f105edb2405b`
- Model: `gpt-5-6-pro`



## Turn 42 - assistant

- Message ID: `029fe331-0038-45cf-bfa5-cf65b81e9eca`
- Model: `gpt-5-6-pro`



## Turn 43 - assistant

- Message ID: `00aa1c3a-0cc6-4578-8c91-8c678638f03a`
- Model: `gpt-5-6-pro`



## Turn 44 - assistant

- Message ID: `cdcbd8b7-09b1-47ca-b004-ab8991995b84`
- Model: `gpt-5-6-pro`



## Turn 45 - assistant

- Message ID: `da9078d3-a7dd-48fa-a00e-6a4ad95174d0`
- Model: `gpt-5-6-pro`



## Turn 46 - assistant

- Message ID: `b3369116-b109-47df-9f1e-2b62b836cb36`
- Model: `gpt-5-6-pro`



## Turn 47 - assistant

- Message ID: `dd4feb82-973f-494f-b54c-ac2bd3924b3e`
- Model: `gpt-5-6-pro`



## Turn 48 - assistant

- Message ID: `2f2bb716-9f45-498d-8975-1a1fb3dbaf69`
- Model: `gpt-5-6-pro`



## Turn 49 - assistant

- Message ID: `d7c55c72-6456-47ed-b57e-7f56d10adb7f`
- Model: `gpt-5-6-pro`



## Turn 50 - assistant

- Message ID: `96eddb67-2054-43d3-830a-1d7f0a4f4ef6`
- Model: `gpt-5-6-pro`

The recommendation is converging on owning a typed/effect IR, verifier, and durable-control lowering, while retaining Goja as a compatibility oracle and forking only where essential.

## Turn 51 - assistant

- Message ID: `0c43514c-a952-417e-a8ba-a2908eeb8b4e`
- Model: `gpt-5-6-pro`



## Turn 52 - assistant

- Message ID: `86b09504-757d-44d4-9e57-f23552c4f39e`
- Model: `gpt-5-6-pro`



## Turn 53 - assistant

- Message ID: `55977237-f82e-41fa-bf26-1ec96bd0c660`
- Model: `gpt-5-6-pro`



## Turn 54 - assistant

- Message ID: `96da7ecf-439a-4489-ace9-d6bad45f9b9b`
- Model: `gpt-5-6-pro`



## Turn 55 - assistant

- Message ID: `84a43d41-de2e-48b2-bc74-224ca0435711`
- Model: `gpt-5-6-pro`



## Turn 56 - assistant

- Message ID: `0f31ff37-2417-4d64-8850-7f9cd8f01394`
- Model: `gpt-5-6-pro`



## Turn 57 - assistant

- Message ID: `7dc4c398-7a98-4deb-a367-c1ac72b35c31`
- Model: `gpt-5-6-pro`



## Turn 58 - assistant

- Message ID: `d7331cfc-3fb8-4be8-a913-d4aa504d6c7d`
- Model: `gpt-5-6-pro`



## Turn 59 - assistant

- Message ID: `8f5523c4-b20d-45d6-a288-e8889b99d144`
- Model: `gpt-5-6-pro`



## Turn 60 - assistant

- Message ID: `b7ad7894-1060-42e2-b705-cea0bc2cbdbc`
- Model: `gpt-5-6-pro`

The 50-page manuscript now frames Tiny-IDP as one authority-selecting “world” atop canonical MIR and versioned dialect packs. Layout defects are corrected; final artifact checks and packaging remain.

## Turn 61 - assistant

- Message ID: `13eff4b2-cf8c-491e-a1f7-81192bc416bd`
- Model: `gpt-5-6-pro`



## Turn 62 - assistant

- Message ID: `82538934-cdb0-4aa0-bcc9-b94046187f5b`
- Model: `gpt-5-6-pro`



## Turn 63 - assistant

- Message ID: `c462d6b9-2a1b-4100-ab9c-f29cc4bcc3bb`
- Model: `gpt-5-6-pro`

# Malleable JavaScript for Assurance-Oriented Systems

The second monograph is complete.

- [Read the 50-page PDF](sandbox:/mnt/data/malleable-js-interpreter-compiler-monograph.pdf)
- [Download the editable DOCX](sandbox:/mnt/data/malleable-js-interpreter-compiler-monograph.docx)
- [View the Markdown source](sandbox:/mnt/data/malleable-js-interpreter-compiler-monograph.md)

The report contains approximately 13,053 words. It is based on the same pinned Tiny-IDP branch snapshot used in the first study, including the work associated with `TINYIDP-GOJA-001`. fileciteturn5file0L1-L3

## Central conclusion

Greater control over Goja would be valuable, but **building a complete JavaScript engine should not be the first move**.

The recommended architecture is a reusable **Malleable JavaScript substrate**:

```text
standard JavaScript source syntax
        |
        v
versioned assurance-profile checker
        |
        v
typed/effect-aware compiler front end
        |
        v
small canonical semantic IR
        |
        +-- reference interpreter
        +-- Goja compute backend
        +-- generated Go backend
        +-- WebAssembly or process-isolated backend
        +-- model checker
        +-- documentation and test generators
```

Projects extend this substrate through versioned **dialects** and **worlds**:

- A **dialect** contributes types, operations, effects, resource classes, verification rules, lowering rules, diagnostics, documentation metadata, and test generators.
- A **world** selects the exact dialect versions, capabilities, entry points, limits, language profile, trust policy, and backend available to one class of plugin.
- Tiny-IDP becomes one assurance-sensitive world rather than the hard-coded owner of the compiler platform.

This separates three concerns that are currently entangled in many embedded-language systems:

```text
source-language ergonomics
semantic and verification contract
runtime implementation
```

JavaScript can remain the author-facing language even when neither JavaScript source nor Goja bytecode is the durable semantic format.

## Principal Tiny-IDP implications

The existing Tiny-IDP architecture is already close to a compiler-oriented runtime. `LambdaSpec` records schemas, outcomes, capabilities, effects, and resource budgets without containing the callback itself. fileciteturn17file0L20-L39

Compiler ownership would allow much of that contract to be **derived rather than repeated**:

| Current declaration | Compiler-derived property |
|---|---|
| Callback ID | Package, module, export, or lexical identity |
| Required capabilities | Reachable capability-call analysis |
| Allowed effects | Typed effect-constructor analysis |
| Allowed outcomes | Closed control-flow analysis |
| Input and output schema use | Property and constructor type checking |
| Continuation carry schema | Live-variable and region analysis |
| Source location | Precise source map and transformation provenance |
| Call and output budgets | Static estimates plus world policy |
| Compatibility metadata | Semantic-identity and continuation-schema comparison |

The host would still grant the maximum authority. Inference would not grant capabilities. It would prove that a program requests a subset of the selected world’s authority.

## Durable `await` as the flagship compiler feature

The report’s highest-value proposal is browser-spanning `await` syntax that compiles to Tiny-IDP’s existing explicit continuation machinery.

A script author could write:

```javascript
export async function signup(ctx) {
  const invitation =
    await ctx.invites.inspect(ctx.input.code);

  const form =
    await durable.form(SignupForm, {
      email: invitation.email,
    });

  const proof =
    await durable.emailCode(form.email);

  return effects.commit([
    identity.create({
      email: form.email,
      proof,
    }),
    invitation.consume(invitation.ref),
    session.establish(),
  ]);
}
```

The compiler would transform this into named handlers, typed continuation records, and explicit native suspension operations. Live-variable analysis would calculate exactly which values must survive each suspension.

The compiler would reject a program when a live value is:

- a password or raw secret;
- a capability function;
- a transaction or request resource;
- an unresolved Promise;
- an ordinary function or closure;
- a Proxy, Symbol, or cyclic object;
- an oversized public value;
- evidence that lacks an approved durable projection.

This preserves the current continuation principle. Tiny-IDP explicitly requires durable records to contain no Goja values, functions, Promises, or goroutine-local state. fileciteturn19file0L3-L5 Its continuation record instead contains stable handler identity, program and workflow identity, carry, bindings, native references, revision, expiry, and terminal state. fileciteturn19file0L56-L84

## Why VM frames should still not be serialized

Access to Goja’s interpreter internals makes VM-frame persistence technically more conceivable, but not architecturally sound.

Goja’s suspended execution context contains runtime-local values, lexical stashes, a program pointer, private environments, program counters, stacks, try frames, iterator state, and reference state. Suspension copies portions of that structure and resumption restores them into the same VM model. fileciteturn21file0L24-L111

Persisting it would bind browser workflow state to:

- one Goja implementation and version;
- internal opcode and object layouts;
- garbage-collector assumptions;
- closure and lexical-environment representation;
- pending Promise-job semantics;
- potentially reachable host functions and Go pointers;
- exact compiled instruction streams;
- opaque, difficult-to-inspect object graphs.

Interpreter access should instead inform a compiler transformation:

```text
source async function
        |
        v
control-flow graph
        |
        v
identify durable suspension points
        |
        v
liveness + type + region analysis
        |
        v
defunctionalized handlers
        |
        v
typed continuation schema
```

The durable representation remains a small application-level state machine.

## What can be built without a Goja fork

A substantial first implementation can sit above stock Goja:

- assurance-profile checking;
- module and import resolution;
- capability and effect inference;
- outcome closure;
- deterministic callback-ID generation;
- durable-`await` lowering;
- continuation-carry liveness analysis;
- secret and evidence flow checking;
- state-machine extraction;
- semantic manifests and diffs;
- structured-concurrency checks;
- source-to-source generation;
- generation-compatibility analysis;
- IDE diagnostics;
- test and documentation generation;
- lowering to a project-independent MIR.

Goja exposes a parser and AST, although its AST package explicitly warns that its interfaces remain works in progress. The report therefore recommends isolating Goja AST access behind a pinned adapter and immediately converting it to a platform-owned syntax representation. fileciteturn22file0L3-L10

## What justifies a narrow Goja fork

A fork becomes justified only for guarantees that cannot be observed reliably at the embedding boundary:

1. **Deterministic instruction fuel**

   Charge a stable semantic cost for VM instructions and size-sensitive operations. Wall time remains an emergency bound rather than the primary execution budget.

2. **Allocation and retained-heap accounting**

   Track logical allocation by runtime, module, invocation, secret, and continuation region.

3. **First-class Promise-job ownership**

   Associate jobs with invocation task scopes, expose pending-job counts, enforce cancellation propagation, and prove quiescence before returning a worker to the pool.

4. **Unforgeable per-value provenance**

   Attach VM-internal origin tags such as native evidence, secret region, capability generation, schema validation, or durable-reference identity.

5. **Precise semantic tracing**

   Trace calls, branches, throws, allocations, suspension points, Promise jobs, source spans, and abstract effect operations.

6. **Stronger reset or snapshot support**

   Snapshot only frozen activation data and immutable module state—not live requests, secrets, capabilities, pending jobs, or control frames.

7. **A stable compiler-IR export**

   This is useful only when source-level rewriting proves too brittle. It should be generic enough to upstream and should not contain Tiny-IDP-specific opcodes.

The fork should remain a replaceable backend. Semantic identity, continuation identity, and verification results must not depend on Goja bytecode.

## New software-design patterns developed in the report

### Compiler-enforced object capabilities

Capabilities become typed imports rather than arbitrary properties on `ctx`. Dynamic access such as:

```javascript
ctx.cap[namespace][operation](input)
```

can be rejected or conservatively widened. Libraries cannot acquire their caller’s authority merely because they are imported. Authority must appear in their effect summary or be passed as an explicitly attenuated capability.

### Structured concurrency for embedded JavaScript

Every asynchronous operation belongs to an invocation task region. Before a handler returns, a task must be:

- awaited;
- joined through a structured combinator;
- cancelled;
- or converted into an explicitly declared host-owned delivery effect.

An ordinary Promise may not escape the invocation region.

### Typed algebraic effects

Instead of manufacturing arbitrary result objects, scripts construct typed abstract operations:

```javascript
return effects.commit([
  identity.create({ email, proof }),
  credential.bindPassword({ identity, password }),
  invitation.consume(invitation),
  session.establish({ identity }),
]);
```

Different backends can interpret the same effect sequence:

- production transaction handler;
- deterministic in-memory test model;
- trace-only simulator;
- migration adapter;
- model checker;
- generated documentation.

### Resource regions

Values receive lifetime regions such as:

```text
static
invocation
secret
transaction
continuation
```

The verifier rejects movement into a longer-lived region unless an explicit dialect operation converts the value into an approved native reference.

### Semantic hot reload

Reload compatibility is classified by semantics rather than source text alone:

- backend-only replacement;
- source-only but MIR-equivalent change;
- compatible semantic extension;
- explicit continuation migration;
- breaking change requiring old-generation retention or revocation.

### Proof-carrying activation

A compiled artifact includes a machine-checkable certificate containing:

- source and frontend identities;
- canonical MIR hash;
- world and dialect versions;
- pass-pipeline identity;
- inferred capabilities and effects;
- continuation-schema hashes;
- resource policies;
- verifier results;
- differential-test results;
- signature.

The production runtime verifies the certificate rather than trusting compiler prose.

### Semantic review diffs

Code review can report changes such as:

```text
+ imports cap.community.lookup@2
+ adds durable state signup.after_recovery
~ continuation carry 72 bytes -> 416 bytes
+ effect credential.bind-recovery@1
- denial outcome member_exists
~ maximum fuel estimate 42k -> 91k
```

This exposes authority and persistence changes that ordinary source diffs conceal.

## Verification target

The report deliberately does **not** recommend proving all of modern ECMAScript first.

The feasible target is the small MIR and verifier:

- value and resource typing;
- region safety;
- capability confinement;
- outcome closure;
- continuation type preservation;
- effect-sequence well-formedness;
- deterministic suspension semantics;
- selected lowering-pass trace preservation.

The production Goja backend, generated-Go backend, and reference interpreter can then be differentially tested against the executable semantic model.

“Verified” in the report therefore means a specific verifier, semantic component, or compiler transformation has a stated and checked property. It does not claim that arbitrary JavaScript, all native capabilities, or the complete identity provider has been formally verified.

## Recommended sequence

The concrete roadmap is:

```text
0. Define trust model and semantic contract
1. Build a pinned JavaScript front end above stock Goja
2. Prototype one durable-await transformation
3. Add task-scope and deterministic-host analysis
4. Introduce the canonical MIR and reference interpreter
5. Extract a declarative dialect SDK
6. Add narrowly measured Goja instrumentation
7. Formalize and verify the small core
8. Add isolation and alternative backends
9. Reconsider a complete engine only if it becomes a strategic product
```

The PDF is the primary reading edition. The DOCX includes a linked static contents section, internal heading navigation, source links, 207 PDF outline entries, embedded fonts, and conventional numbered references.

