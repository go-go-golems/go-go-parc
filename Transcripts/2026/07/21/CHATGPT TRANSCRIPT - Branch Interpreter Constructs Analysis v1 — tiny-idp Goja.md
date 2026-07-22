# Branch · Interpreter Constructs Analysis

- URL: https://chatgpt.com/c/6a5e1c8b-779c-83ea-80ab-cf68e7cb8e00
- Created: 2026-07-20T13:03:08.643Z

---

> Study https://github.com/go-go-golems/tiny-idp/tree/task/prod-tiny-idp and write a textbook / report / analysis about all the interesting interpreter and goja constructs introduced to properly implement this, things like serialized continuations and invocation capabilities and deterministic callback registration and many more. There is a lot of interesting novel / rigorous interpreter work in there in say pkg/idp script and workflow and such , work done as part of ttmp TINYIDP-GOJA-001 .

<details><summary>💭 Thinking</summary>

**Evaluating project scope**

I’m considering how to respond to a task involving a GitHub repo. The user likely wants a detailed report or analysis, possibly in markdown or PDF. I’ll clarify their preferred format.

**Evaluated project scope**

</details>

I’ll trace the branch architecture, commit history, and TINYIDP-GOJA-001 changes across `pkg/idp`, then produce a structured technical report emphasizing concrete code references and invariants.

<details><summary>💭 Thinking</summary>

**Retrieved GitHub repository metadata and fetched README file**

</details>

```unknown
bash -lc rm -rf /mnt/data/tiny-idp && git clone --branch task/prod-tiny-idp --single-branch https://github.com/go-go-golems/tiny-idp.git /mnt/data/tiny-idp && git -C /mnt/data/tiny-idp rev-parse HEAD && git -C /mnt/data/tiny-idp status --short
```

<details><summary>💭 Thinking</summary>

**Cloned branch and fetched updates**

</details>

```json
{"open":[{"ref_id":"https://api.github.com/repos/go-go-golems/tiny-idp/git/trees/task/prod-tiny-idp?recursive=1"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched the web**

**Searched GitHub repo for specific ticket content**

**Researching GitHub files**

I’m exploring how to dig deeper into a project by examining files, likely from a Git branch. I’ll gather details, focusing on specific package scripts and documentation or design analysis.

**Researched GitHub files**

**Searched files for package declarations and fetched design documents**

**Searched for package references, classes, and functions in repository**

</details>

The branch reveals a lambda-first workflow machine: Goja-free serialized IR uses stable callback IDs, while browser waits persist versioned continuations that resume fresh, capability-bounded invocations.

<details><summary>💭 Thinking</summary>

**Fetched commit metadata, diffs, and related file content**

**Evaluated Goja interpreter architecture and searched recent commits**

**Organizing file citation**

I’m planning to fetch and organize files from GitHub, keeping track of line numbers for proper citations. I'll create a markdown report, using permanent links for sources and commit references.

**Organized file citation**

**Fetched file content and calculated line count**

**Fetched and validated files and code from repository**

**Fetched value.go, providers.go, and diagnostics.go files**

**Fetched file and module content, built workflow components**

**Fetched compiler and runtime factory file content from repository**

**Fetched and analyzed files and capabilities for settlement tracking**

**Fetched continuation types and file content from repository**

**Preparing report on TINYIDP**

I’m synthesizing findings from GitHub, focusing on constructs like serialized continuations, invocation capabilities, and callback registration. The report will include precise file citations and reflect the clinical tone required.

**Preparing tiny-idp monograph**

I’m planning to write a detailed Markdown monograph analyzing TINYIDP's interpreter constructs, callback registration, and continuations. I’ll focus on code references and keep citations accurate, considering PDF output later.

**Prepared report and monograph on TINYIDP**

**Fetched files and content from GitHub for analysis and submission**

**Fetched file content from GitHub repository**

**Fetched and inspected repository files for implementation details**

**Fetched and evaluated GitHub files for advanced Goja analysis**

</details>

```unknown
bash -lc cat /home/oai/skills/pdfs/SKILL.md
```

The key enforcement pattern is now clear: deterministic registration is checked across isolated runtimes, while opaque JavaScript executes within declared schemas, budgets, capabilities, outcomes, and native-committed effects.

<details><summary>💭 Thinking</summary>

**Read skill from PDF and checked required installations**

**Fetched commit metadata and inspected go.mod for version**

</details>

```unknown
bash -lc cat > /mnt/data/tiny-idp-goja-interpreter-monograph.md <<'EOF'
---
title: "Interpreting Identity Safely"
subtitle: "A Technical Monograph on Tiny-IDP's Goja Microkernel, Explicit Continuations, Invocation Capabilities, and Assurance-Oriented Runtime"
author: "Source analysis prepared from TINYIDP-GOJA-001"
date: "2026-07-20"
lang: en-US
---

# Scope and source snapshot

This report studies the `task/prod-tiny-idp` branch of `go-go-golems/tiny-idp` at commit [`d164ae59408bdd8bc21516274b446339b1761b1e`](https://github.com/go-go-golems/tiny-idp/commit/d164ae59408bdd8bc21516274b446339b1761b1e), dated 2026-07-20. The principal implementation and design sources are:

- the active lambda-first design, [`design-doc/03-lambda-first-tiny-idp-javascript-api-with-explicit-browser-continuations.md`](https://github.com/go-go-golems/tiny-idp/blob/d164ae59408bdd8bc21516274b446339b1761b1e/ttmp/2026/07/10/TINYIDP-GOJA-001--go-go-goja-identity-microkernel-scripting-layer/design-doc/03-lambda-first-tiny-idp-javascript-api-with-explicit-browser-continuations.md);
- the assurance-oriented synthesis, [`design-doc/02-assurance-oriented-core-grammar-and-codebase-refactoring-proposal.md`](https://github.com/go-go-golems/tiny-idp/blob/d164ae59408bdd8bc21516274b446339b1761b1e/ttmp/2026/07/10/TINYIDP-GOJA-001--go-go-goja-identity-microkernel-scripting-layer/design-doc/02-assurance-oriented-core-grammar-and-codebase-refactoring-proposal.md);
- the implementation ledger and status record in [`tasks.md`](https://github.com/go-go-golems/tiny-idp/blob/d164ae59408bdd8bc21516274b446339b1761b1e/ttmp/2026/07/10/TINYIDP-GOJA-001--go-go-goja-identity-microkernel-scripting-layer/tasks.md) and [`changelog.md`](https://github.com/go-go-golems/tiny-idp/blob/d164ae59408bdd8bc21516274b446339b1761b1e/ttmp/2026/07/10/TINYIDP-GOJA-001--go-go-goja-identity-microkernel-scripting-layer/changelog.md);
- the runtime-independent contract in [`pkg/idpprogram`](https://github.com/go-go-golems/tiny-idp/tree/d164ae59408bdd8bc21516274b446339b1761b1e/pkg/idpprogram);
- the Goja compiler, runtime, capability bridge, and worker pool in [`pkg/idpscript`](https://github.com/go-go-golems/tiny-idp/tree/d164ae59408bdd8bc21516274b446339b1761b1e/pkg/idpscript);
- the native Goja module in [`internal/gojamodules/tinyidp`](https://github.com/go-go-golems/tiny-idp/tree/d164ae59408bdd8bc21516274b446339b1761b1e/internal/gojamodules/tinyidp);
- durable workflow state in [`pkg/idpcontinuation`](https://github.com/go-go-golems/tiny-idp/tree/d164ae59408bdd8bc21516274b446339b1761b1e/pkg/idpcontinuation);
- typed browser projection and request-scoped secret handling in [`pkg/idpworkflow`](https://github.com/go-go-golems/tiny-idp/tree/d164ae59408bdd8bc21516274b446339b1761b1e/pkg/idpworkflow);
- the production signup integration in [`pkg/idpsignup`](https://github.com/go-go-golems/tiny-idp/tree/d164ae59408bdd8bc21516274b446339b1761b1e/pkg/idpsignup) and [`internal/fositeadapter/scripted_signup.go`](https://github.com/go-go-golems/tiny-idp/blob/d164ae59408bdd8bc21516274b446339b1761b1e/internal/fositeadapter/scripted_signup.go);
- typed policy/provider adapters, native challenge evidence, verification plans, and the assurance vocabulary.

The analysis is source-based. The repository's own ticket records extensive unit, race, conformance, and integration test runs. Those records are described where relevant, but this report does not present them as independently re-executed results.

The word *novel* is used here in the engineering sense: an unusual and rigorous synthesis within this codebase. It is not a claim of academic priority.

# Executive synthesis

The significant achievement is not that Tiny-IDP embeds JavaScript. The significant achievement is that it refuses to make JavaScript the identity provider.

The branch implements a staged interpreter architecture in which JavaScript is allowed to author and execute narrowly typed policy fragments, while Go retains protocol authority, persistence authority, secret authority, HTTP authority, and atomic commit authority. The result is best understood as four related machines:

1. **A definition-time compiler.** Trusted JavaScript registers named lambdas and serializable workflow/provider contracts. It produces a pure-Go intermediate representation plus a VM-local callback registry.
2. **An activation verifier.** The same compiled source is materialized in independent owned runtimes. Program, schema, and callback fingerprints must agree before workers are accepted.
3. **A request-time lambda interpreter.** A worker receives a frozen, JSON-derived input object and only the capabilities declared by the selected lambda. It may perform bounded in-request asynchronous work and must return one member of a closed outcome algebra.
4. **A durable native workflow interpreter.** Browser-spanning control flow is not a suspended Promise or Goja heap. It is an explicit, versioned continuation record containing a handler label, typed public carry, exact generation identity, replay revision, and native references. Go validates and advances that record, renders pages, verifies challenges, and commits effects.

The architecture can be summarized as follows:

```text
                 definition time
 trusted JS  -------------------------->  pure Program IR
     |                                          |
     | VM-local closures                       | canonical validation
     v                                          v
 callback registry  <---- fingerprint ----  activation identity
     |
     | one exclusive owned runtime
     v
 frozen invocation context + declared capabilities
     |
     | sync result or bounded Promise
     v
 closed Outcome algebra
     |
     +--> present/challenge --> durable continuation record
     |
     +--> commit -----------> native effect validator + atomic transaction
     |
     +--> complete/deny/etc -> native protocol orchestration
```

Several interpreter ideas reinforce each other:

- **Defunctionalization.** Durable continuations are represented by stable handler IDs and a schema-checked environment instead of serializing closures or stacks.
- **A runtime type-and-effect discipline.** Each lambda declares input and output schemas, allowed outcomes, required capabilities, permitted effects, timeout, call budget, and output budget.
- **Nominal branding in an untyped language.** Blank Goja objects are recognized by object identity in Go maps, making lambda, field, action, and secret handles unforgeable inside the VM.
- **Object-capability style authority.** A capability exists only because the host inserted it into one invocation, and it becomes inactive when the invocation ends.
- **Algebraic-effect style commits.** JavaScript returns inert effect plans. Native Go code validates the exact sequence and applies the effects in a named atomic operation.
- **Fail-stop worker leasing.** A runtime is returned to the pool only after a fully valid result and complete asynchronous settlement. Timeout, cancellation, exception, malformed output, or uncertain interruption causes disposal and replacement.
- **Generation-aware resumption.** A continuation is pinned to executable source plus semantic program identity. Hot reload creates a new generation rather than reinterpreting old state under new code.
- **Separate production and verification languages.** Production lambdas receive bounded policy capabilities. Verification JavaScript can only compile data-only scenarios, which are materialized against an explicit native step registry before execution.

This is a practical answer to a difficult question: how can an identity system gain expressive scripting without turning protocol correctness into a property of arbitrary script behavior?

# Part I - The interpreter problem

## 1. Why identity scripting is unusually dangerous

A general embedded language normally seeks convenience: expose services, let scripts call them, and translate values. In an identity provider, that approach collapses several distinct authorities into one dynamic layer:

- protocol validation and OAuth/OIDC state transitions;
- browser request parsing, CSRF and origin handling, cookies, redirects, and response writing;
- password, one-time-code, invitation, and signing-key handling;
- transaction boundaries and one-time consumption;
- account, credential, session, consent, and token issuance;
- policy selection and presentation customization.

If all of those become ordinary methods on a script-visible host object, the scripting API becomes an alternate identity provider. Every script path must then preserve every protocol and storage invariant. Static review becomes difficult because authority is ambient, data types are open, and errors can accidentally change security meaning.

The active design takes the opposite route. JavaScript may choose among host-defined operations and return host-defined values, but it cannot own the transition that makes an identity assertion true. The design document explicitly excludes Fosite objects, stores, SQL transactions, keys, cookies, passwords, raw codes, and network clients from the script surface. See the design's authority table and core execution model in [`design-doc/03`, sections 4-6](https://github.com/go-go-golems/tiny-idp/blob/d164ae59408bdd8bc21516274b446339b1761b1e/ttmp/2026/07/10/TINYIDP-GOJA-001--go-go-goja-identity-microkernel-scripting-layer/design-doc/03-lambda-first-tiny-idp-javascript-api-with-explicit-browser-continuations.md#L300-L531).

The central security move is therefore architectural rather than syntactic:

> Script expressiveness is permitted only inside a native envelope whose inputs, outputs, capabilities, effects, time, size, lifetime, and continuation points are explicit.

## 2. Four stages, not one interpreter

It is tempting to describe the system as "Go executes JavaScript callbacks." That misses most of the design. There are four different stages with different state and authority.

### 2.1 Stage A: definition-time evaluation

The top level of a source file executes in an isolated Goja runtime. It calls `require("tinyidp").v1`, constructs named lambdas, registers workflows/providers/tests, and exports the value returned by `A.program(...)`.

At this stage:

- Goja functions exist, but only inside the runtime's collector;
- the exported contract is data-only;
- no request, store, network, provider, or protocol object is present;
- source size and definition time are bounded;
- ambient module loading is disabled.

### 2.2 Stage B: activation materialization

A compiled `*goja.Program` is loaded into multiple independent owned runtimes. Each runtime reconstructs the program and callback registry. The host compares canonical program data and fingerprints. If one materialization differs, activation fails.

This stage is a form of reproducible linking: named callback references in the IR must resolve to the same VM-local registry in every worker.

### 2.3 Stage C: request-time invocation

For one handler invocation, the host:

- validates the JSON input against the handler's schema;
- leases one runtime exclusively;
- installs only the handler's declared capability bindings;
- creates request-scoped secret and evidence handles;
- builds and freezes a plain JavaScript context;
- invokes the named closure on the runtime owner;
- awaits a bounded Promise if returned;
- validates the resulting outcome;
- releases or destroys the worker.

### 2.4 Stage D: native transition interpretation

The JavaScript outcome is not the final protocol action. Go interprets it:

- `present` becomes a validated native page plus a durable continuation;
- `challenge` becomes a native challenge record and delivery operation;
- `commit` becomes a revalidated effect sequence and atomic transaction;
- `complete`, `deny`, `skip`, and `error` are normalized by the relevant native provider or protocol seam.

This fourth stage is what preserves the identity microkernel. The script proposes; the native transition commits.

## 3. The semantic firewall: `pkg/idpprogram`

The first hard boundary is a package with no Goja dependency. [`pkg/idpprogram/program.go`](https://github.com/go-go-golems/tiny-idp/blob/d164ae59408bdd8bc21516274b446339b1761b1e/pkg/idpprogram/program.go#L1-L57) defines a serializable `Program` containing workflows, providers, lambda specifications, schemas, capability descriptors, and tests. A lambda specification stores a callback ID, never a function.

This package is more than a DTO collection. It is the semantic firewall between two worlds:

```text
Goja world                              durable/native world
----------                              --------------------
closures                                callback IDs
objects with identity                   stable string IDs
Promises                                outcome records
host functions                          capability requirements
mutable JS state                        canonical JSON
runtime-local values                    pure Go values
```

The separation creates three useful proof obligations:

1. **Closure locality:** no Goja value can enter a `Program` or continuation.
2. **Reference totality:** every callback ID in the IR must be present in each runtime's registry.
3. **Interpretation closure:** every possible handler result belongs to a finite native outcome family.

# Part II - Definition-time language and activation

## 4. A runtime type-and-effect system

[`LambdaSpec`](https://github.com/go-go-golems/tiny-idp/blob/d164ae59408bdd8bc21516274b446339b1761b1e/pkg/idpprogram/lambda.go#L20-L39) assigns each callback a contract:

```text
LambdaSpec =
  callback identity
  + lambda kind
  + input schema
  + output schema
  + allowed outcome set
  + required capability set
  + allowed effect set
  + timeout
  + maximum capability calls
  + maximum output bytes
```

This resembles a dynamic type-and-effect system.

- The input and output schemas are value types.
- `AllowedOutcomes` is a row of legal control effects.
- `RequiredCapabilities` is the authority context.
- `AllowedEffects` is the commit-effect context.
- `Budget` is a resource effect bound.

The contract is enforced twice. [`idpprogram.Validate`](https://github.com/go-go-golems/tiny-idp/blob/d164ae59408bdd8bc21516274b446339b1761b1e/pkg/idpprogram/validate.go#L30-L258) checks it before activation. [`pkg/idpscript/codec.go`](https://github.com/go-go-golems/tiny-idp/blob/d164ae59408bdd8bc21516274b446339b1761b1e/pkg/idpscript/codec.go#L15-L38) checks actual inputs and outputs at invocation.

A useful way to read a handler declaration is:

```text
under capability environment C,
within resource budget B,
this callback maps values of schema I
into one of outcome kinds O,
whose value conforms to schema R,
and whose commit plan may contain effects E.
```

That is far more reviewable than a generic `func(ctx map[string]any) any`.

## 5. Closed schemas and information-flow labels

[`pkg/idpprogram/schema.go`](https://github.com/go-go-golems/tiny-idp/blob/d164ae59408bdd8bc21516274b446339b1761b1e/pkg/idpprogram/schema.go#L5-L46) defines a deliberately small schema language: object, string, boolean, integer, and bytes, with byte and length bounds. Object fields refer to named schemas. The validator rejects cycles and missing references.

Two design choices matter.

First, object schemas are closed by default. `Additional: false` makes unknown fields an error. This prevents a browser form, capability result, or script result from smuggling data into a handler that never declared it.

Second, fields carry a `Sensitive` marker. [`ValidatePublicJSON`](https://github.com/go-go-golems/tiny-idp/blob/d164ae59408bdd8bc21516274b446339b1761b1e/pkg/idpprogram/value.go#L41-L65) traverses a value under the destination schema and rejects sensitive fields. The same schema therefore serves two related purposes:

- structural typing for an ephemeral invocation; and
- an information-flow policy for durable public carry.

The continuation environment is not merely JSON that happens not to contain a password. It is JSON proven against a schema path that forbids sensitive fields.

## 6. The outcome algebra

[`pkg/idpprogram/outcomes.go`](https://github.com/go-go-golems/tiny-idp/blob/d164ae59408bdd8bc21516274b446339b1761b1e/pkg/idpprogram/outcomes.go#L11-L117) defines a closed sum type:

- `continue` - immediate native dispatch to another handler;
- `present` - native UI plus a durable continuation;
- `challenge` - native proof mechanism plus a durable continuation;
- `commit` - inert effect plan for native validation and transaction;
- `complete` - terminal typed value;
- `deny` - valid negative policy result;
- `skip` - explicitly inapplicable provider/branch;
- `error` - infrastructure or internal failure.

The distinctions are security-relevant. A thrown exception is not a denial. `undefined` is not a skip. A rejected credential is not an invitation to silently try a weaker factor. The design document calls out this semantic discipline directly in [`design-doc/03`](https://github.com/go-go-golems/tiny-idp/blob/d164ae59408bdd8bc21516274b446339b1761b1e/ttmp/2026/07/10/TINYIDP-GOJA-001--go-go-goja-identity-microkernel-scripting-layer/design-doc/03-lambda-first-tiny-idp-javascript-api-with-explicit-browser-continuations.md#L389-L407).

This is algebraic in the practical sense: the host performs exhaustive interpretation over a finite family. A new security-significant result requires a native enum, validation rule, interpreter branch, tests, and usually an effect or provider contract. It cannot arrive as an accidental JavaScript object shape.

## 7. Static workflow validation as finite-state analysis

A workflow is a map of handler IDs plus explicit continuation edges. The validator performs more than reference checking:

- handler and lambda IDs must agree;
- entry handlers must exist;
- every edge must name a legal source outcome;
- edge input schemas must agree with destination lambda schemas;
- all handlers must be reachable from the entry;
- schemas must be acyclic;
- capabilities and effects must be declared and versioned;
- providers must declare coherent state, replay, and revocation semantics;
- tests must target existing lambdas and legal expected outcomes.

The reachability walk is deterministic because map keys are sorted before traversal. Diagnostics are also sorted by path, diagnostic ID, and message in [`diagnostics.go`](https://github.com/go-go-golems/tiny-idp/blob/d164ae59408bdd8bc21516274b446339b1761b1e/pkg/idpprogram/diagnostics.go#L7-L47). Deterministic diagnostics matter operationally: activation systems and CI should not produce order-dependent output from Go map iteration.

The resulting `Program` is a finite, statically reviewable transition graph even though handler bodies remain dynamic. Static analysis can prove where control may resume and which effect families may be requested without interpreting arbitrary callback code.

## 8. The native module as a nominal type system

The native module in [`internal/gojamodules/tinyidp/module.go`](https://github.com/go-go-golems/tiny-idp/blob/d164ae59408bdd8bc21516274b446339b1761b1e/internal/gojamodules/tinyidp/module.go) uses a particularly effective Goja technique: blank object handles branded by VM object identity.

When `A.lambda(id, spec)` is called, the loader:

1. validates the arguments;
2. extracts the callback as a `goja.Callable`;
3. records the callable in the collector under the stable ID;
4. creates a blank JavaScript object;
5. stores `collector.lambdas[object] = id`;
6. returns the blank object to JavaScript.

Workflow registration accepts only an object present in that identity map. An attacker cannot forge a lambda by constructing `{id: "signup.start"}` because properties are irrelevant. The nominal brand is the `*goja.Object` pointer known to Go.

The same mechanism is used for:

- host-defined field descriptors;
- host-defined action descriptors;
- invocation-scoped secret handles.

This gives an untyped language several nominal types without exposing a forgeable tag or a private symbol. It also makes misuse errors local and precise: a presentation field must be the exact object returned by the module, not an object with similar data.

### 8.1 Why blank objects are stronger than frozen tagged objects

A frozen tagged object such as `{kind: "lambda", id: "x"}` is immutable but forgeable. A JavaScript `Symbol` narrows accidental collisions but can still be copied if exposed. A Go-side identity table gives the host an unforgeable membership test for the lifetime of the runtime.

The pattern can be stated generally:

```text
brand(v, T)  := hostMap[T].contains(objectIdentity(v))
```

It is a useful bridge pattern whenever an embedded language needs opaque, nominal references to host-approved declarations.

## 9. A closed CommonJS world

[`NewRuntimeFactory`](https://github.com/go-go-golems/tiny-idp/blob/d164ae59408bdd8bc21516274b446339b1761b1e/pkg/idpscript/runtime_factory.go#L40-L50) disables implicit default modules, data-only default modules, and the ambient loader. The only registered native module is `tinyidp`.

Negative tests attempt to load filesystem, process, execution, database, network, OS, and arbitrary project modules. See [`pkg/idpscript/invoke_test.go`](https://github.com/go-go-golems/tiny-idp/blob/d164ae59408bdd8bc21516274b446339b1761b1e/pkg/idpscript/invoke_test.go#L271-L290).

This is a closed-world language profile:

```text
JavaScript syntax and standard built-ins
+ require("tinyidp")
- filesystem
- process
- OS
- network
- database
- project module loader
```

The design correctly describes this as authority reduction, not a claim that hostile code is safely sandboxed in-process. The scripts are operator-trusted. The runtime profile constrains accidental and exploit-oriented authority but does not replace process isolation for adversarial code.

## 10. Deterministic callback registration

The core registration problem is subtle. A serializable program can contain the ID `signup.submitted`, but the executable closure exists only inside a specific Goja runtime. A worker pool therefore needs a reproducible linking rule:

```text
Program callback ID  <->  exact closure registered in this runtime
```

Tiny-IDP solves this by re-executing the same compiled source in every worker and checking several identities.

### 10.1 Canonical identities

[`ComputeFingerprints`](https://github.com/go-go-golems/tiny-idp/blob/d164ae59408bdd8bc21516274b446339b1761b1e/pkg/idpprogram/canonical.go#L14-L60) computes independent hashes for:

- source text;
- canonical program IR;
- sorted callback registry IDs;
- canonical schema registry.

The separate hashes answer different questions:

| Fingerprint | What it detects |
|---|---|
| Source | Any executable source change, including callback bodies |
| Program | Any semantic registration/contract change |
| Callback registry | Missing, extra, or renamed VM-local closures |
| Schemas | Host/schema drift even when callback IDs are unchanged |

### 10.2 Re-materialization checks

During compilation, [`compiler.go`](https://github.com/go-go-golems/tiny-idp/blob/d164ae59408bdd8bc21516274b446339b1761b1e/pkg/idpscript/compiler.go#L38-L78) compiles the source, loads it into an isolated runtime, validates the resulting program, computes fingerprints, and stores an immutable artifact.

During worker loading, [`runtime_factory.go`](https://github.com/go-go-golems/tiny-idp/blob/d164ae59408bdd8bc21516274b446339b1761b1e/pkg/idpscript/runtime_factory.go#L73-L188):

1. creates a fresh owned runtime;
2. installs a runtime-local collector;
3. executes the compiled program under the owner;
4. JSON-encodes `module.exports`;
5. obtains the collector's program independently;
6. requires canonical equality between the two;
7. validates the program again;
8. recomputes program, callback, and schema fingerprints;
9. compares them with the artifact;
10. requires a one-to-one callback-ID/lambda-spec set.

This is deterministic registration as an activation invariant, not as a coding convention.

### 10.3 What this does and does not prove

It proves that definition-time observable registration is reproducible across workers. It catches a program that conditionally registers different handlers based on time, random values, or runtime-dependent state if that difference reaches the program or callback registry.

It does not prove that callback behavior is deterministic for every input. A callback may intentionally depend on a declared capability, and a reused runtime may retain ordinary module state. Source identity and capability scoping make such behavior reviewable, but registration equality is not full semantic equivalence.

## 11. `module.exports` as an anti-ambiguity check

The runtime does not merely trust the collector. It also requires that `module.exports` be canonically equal to the value returned by `tinyidp.v1.program`. See [`runtime_factory.go`, lines 97-151](https://github.com/go-go-golems/tiny-idp/blob/d164ae59408bdd8bc21516274b446339b1761b1e/pkg/idpscript/runtime_factory.go#L97-L151).

This prevents several ambiguous module patterns:

- registering one program while exporting another;
- exporting an unrelated object after registration;
- relying on hidden collector side effects that are not visible in the module contract;
- accidentally omitting the program export.

The program has one authoritative public representation and one authoritative private callback registry, and activation checks that they correspond.

## 12. Immutable artifacts and defensive copies

[`Artifact`](https://github.com/go-go-golems/tiny-idp/blob/d164ae59408bdd8bc21516274b446339b1761b1e/pkg/idpscript/artifact.go#L14-L62) stores:

- source text;
- a compiled `*goja.Program` reusable by independent runtimes;
- canonical program JSON;
- fingerprints.

`Artifact.Program()` decodes a fresh copy from canonical JSON. `RuntimeImage.Program()` similarly produces a deep copy. This removes a common embedded-runtime hazard: a caller cannot mutate the activation contract after validation by retaining a map or slice reference.

The artifact is therefore a reproducible recipe for runtime images, not a live runtime itself.

EOF
```

<details><summary>💭 Thinking</summary>

**Created and drafted technical monograph with design details**

**Organizing textbook/report structure**

I’m working through the structure for a comprehensive textbook on TINYIDP, focusing on its unique constructs, including continuations and callback registration. I’ll cross-check citations carefully and use relevant files.

**Processing document output**

I’m working through the monograph’s structure, checking the references and formatting. I’ll adjust the DOCX and PDF output for styling, margins, and page size before finalizing and inspecting each page.

**Organized textbook/report structure and processed document output**

</details>

```unknown
bash -lc sed -n '1,260p' /home/oai/skills/docx/SKILL.md && printf '\n---PDF---\n' && sed -n '1,320p' /home/oai/skills/pdfs/SKILL.md
```

The full textbook draft is complete and undergoing layout checks. It distinguishes registry determinism from callback-state determinism and implemented guarantees from residual assurance gaps.

<details><summary>💭 Thinking</summary>

**Read documentation, inspected content, and analyzed images for PDF creation**

</details>

```unknown
bash -lc cp /mnt/data/_qa_docx_final/tiny-idp-goja-interpreter-monograph.pdf /mnt/data/tiny-idp-goja-interpreter-monograph.pdf
rm -rf /mnt/data/_qa_pdf_final && mkdir -p /mnt/data/_qa_pdf_final
python /home/oai/skills/pdfs/scripts/render_pdf.py /mnt/data/tiny-idp-goja-interpreter-monograph.pdf --out_dir /mnt/data/_qa_pdf_final --dpi 200
pdfinfo /mnt/data/tiny-idp-goja-interpreter-monograph.pdf | sed -n '1,40p'
python /home/oai/skills/pdfs/scripts/pdf_preflight.py /mnt/data/tiny-idp-goja-interpreter-monograph.pdf || true
python /home/oai/skills/pdfs/scripts/pdf_inspect.py /mnt/data/tiny-idp-goja-interpreter-monograph.pdf | sed -n '1,180p' || true
unzip -t /mnt/data/tiny-idp-goja-interpreter-monograph.docx | tail -5
sha256sum /mnt/data/tiny-idp-goja-interpreter-monograph.md /mnt/data/tiny-idp-goja-interpreter-monograph.docx /mnt/data/tiny-idp-goja-interpreter-monograph.pdf
ls -lh /mnt/data/tiny-idp-goja-interpreter-monograph.*

```

<details><summary>💭 Thinking</summary>

**Verified and analyzed PDF files and document details**

</details>

```json
{"paths":["GitHub"],"query":"repository"}
```

```json
{"uri":"/response/turn8","query":"pkg/idp","start_line":1}
```

```json
{"uri":"/response/turn13","query":"filename","start_line":1}
```

```json
{"uri":"/response/turn13","start_line":1,"num_lines":40}
```

```json
{"uri":"/response/turn15","start_line":160,"num_lines":220}
```

```json
{"uri":"/response/turn15","query":"Step 17","start_line":1}
```

```json
{"paths":["GitHub"],"query":"tree"}
```

```json
{"uri":"/response/turn70","query":"pkg/memorystore","start_line":1}
```

```json
{"uri":"/response/turn70","query":"package memorystore","start_line":1}
```

```json
{"uri":"/response/turn18","start_line":1,"num_lines":35}
```

```json
{"uri":"/response/turn8","query":"## 5.","start_line":1}
```

```json
{"uri":"/response/turn8","start_line":300,"num_lines":250}
```

```json
{"uri":"/response/turn8","query":"## 8.","start_line":1}
```

```json
{"uri":"/response/turn8","query":"## 9.","start_line":1}
```

```json
{"uri":"/response/turn8","query":"## 10.","start_line":1}
```

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


---

> Research and brainstorm how having access to the goja interpreter or in fact creating our own js interpreter / compiler would influence such a design and potentially make it more usable / elegant / robust / verified / allow new software design patterns both on the implementation of the idp framework and on the side of the plugin/script writers. 
>
> One could also imagine making the js interpreter / compiler malleable and extensible, so that one could extend it in different ways for different projects, not just tiny-idp .
>
> Write a similar doc

I’ll map Goja’s extension boundaries, compare deeper integration, forked-Goja, compiler-front-end, and purpose-built runtime options, then derive Tiny-IDP patterns, cross-project architecture, risks, and a staged roadmap.

```unknown
bash -lc set -e
cat /home/oai/skills/docx/SKILL.md
printf '\n---PDF SKILL---\n'
cat /home/oai/skills/pdfs/SKILL.md
printf '\n---REPO---\n'
if [ -d /mnt/data/tiny-idp/.git ]; then git -C /mnt/data/tiny-idp rev-parse --abbrev-ref HEAD; git -C /mnt/data/tiny-idp rev-parse HEAD; else echo 'repo missing'; fi
printf '\n---EXISTING REPORT---\n'
ls -lh /mnt/data/tiny-idp-goja-interpreter-monograph.* 2>/dev/null || true
printf '\n---GOJA VERSION---\n'
if [ -f /mnt/data/tiny-idp/go.mod ]; then grep -n 'goja' /mnt/data/tiny-idp/go.mod /mnt/data/tiny-idp/go.sum | head -20; fi
```

<details><summary>💭 Thinking</summary>

**Verified repo and Goja version, cloned repositories and inspected dependencies**

</details>

```json
{"search_query":[{"q":"site:github.com/go-go-golems/tiny-idp \"task/prod-tiny-idp\" TINYIDP-GOJA-001"},{"q":"site:github.com/dop251/goja README compiler parser Runtime Interrupt Promise"},{"q":"site:github.com/dop251/goja \"type Runtime\" \"Interrupt\""},{"q":"site:github.com/endojs/endo SES compartments hardened JavaScript official"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 33 webpages**

</details>

```json
{"open":[{"ref_id":"https://github.com/go-go-golems/tiny-idp/archive/refs/heads/task/prod-tiny-idp.zip"},{"ref_id":"https://github.com/dop251/goja/archive/refs/heads/master.zip"}],"response_length":"short"}
```

<details><summary>💭 Thinking</summary>

**Searched the web**

**Fetched and analyzed files and commits from GitHub repository**

</details>

```json
{"click":[{"ref_id":"turn799126view0","id":80}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched the web**

**Fetched files and content from GitHub repository**

**Planning monograph structure**

I’m outlining a monograph, aiming for around 15k words and diverse topics. It’ll cover Go ja’s architecture, public/private access, design opportunities, and potential optimizations related to parsing, concurrency, and memory checks.

**Planned monograph structure**

**Fetched Goja README content and inspected source code functions**

</details>

```json
{"find":[{"ref_id":"turn799126view3","pattern":"func Compile("},{"ref_id":"turn799126view3","pattern":"func CompileAST("},{"ref_id":"turn799126view3","pattern":"ParseFile"},{"ref_id":"turn799126view2","pattern":"type Runtime struct"},{"ref_id":"turn799126view2","pattern":"func (r *Runtime) Interrupt"},{"ref_id":"turn799126view2","pattern":"SetMaxCallStackSize"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 6 webpages**

**Fetched runtime struct, job queue data, and vm.go content**

</details>

```json
{"open":[{"ref_id":"https://github.com/dop251/goja/blob/master/vm.go"}],"response_length":"short"}
```

The central question is whether ownership, branding, metering, resumability, finite registries, and exact codecs remain host conventions or become intrinsic semantics without creating a monolithic trusted runtime.

<details><summary>💭 Thinking</summary>

**Searched the web and GitHub**

**Fetched file content and searched for function definitions in GitHub**

**Gathering external sources**

I'm considering how to fetch data from GitHub, but it seems tricky without getting full content. I’m planning to turn to external research for relevant documents on ECMAScript, continuations, and functional programming.

**Gathered external sources**

**Fetched Goja parser code for AST export**

</details>

```json
{"search_query":[{"q":"site:pkg.go.dev/github.com/dop251/goja CompileAST goja"},{"q":"site:github.com/dop251/goja \"CompileAST\""},{"q":"site:github.com/dop251/goja \"func Compile\" \"parser.ParseFile\""}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched pkg.go.dev**

**Inspected Goja promise behavior and resolved issues**

**Searched web for Goja CompileAST function**

**Fetched lines from Promise documentation section**

</details>

```json
{"find":[{"ref_id":"turn799126view2","pattern":"jobQueue"},{"ref_id":"turn799126view2","pattern":"func (r *Runtime) leave()"},{"ref_id":"turn799126view2","pattern":"ClearInterrupt"},{"ref_id":"turn799126view2","pattern":"SetAsyncContextTracker"},{"ref_id":"turn799126view2","pattern":"SetTimeSource"},{"ref_id":"turn799126view2","pattern":"SetRandSource"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched the web and GitHub**

**Planning external research**

I’m focusing on gathering primary research about various topics like Go ja internals, ECMAScript job queues, and temporal durable execution. I’ll explore papers on language design, memory limits, and compiler APIs.

**Planned external research**

**Designing interpreter architecture**

I’m working on building an interpreter with a multi-backend system. I plan to provide extension points like custom syntax, static passes, and static verification while preserving security. I'll also incorporate effects, concurrency, and capability attunement.

**Inspected Goja VM interrupt methods and searched repository**

</details>

```json
{"find":[{"ref_id":"turn799126view2","pattern":"Interrupt(v interface{})"},{"ref_id":"turn266159view0","pattern":"Interrupt(v interface{})"},{"ref_id":"turn266159view0","pattern":"ClearInterrupt()"},{"ref_id":"turn266159view0","pattern":"checkInterrupt"},{"ref_id":"turn266159view0","pattern":"interrupted"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched the web and GitHub**

</details>

```unknown
bash -lc ls -la /mnt/data | sed -n '1,120p' && find /mnt/data -maxdepth 2 -type f -printf '%p
' | sed -n '1,200p'
```

<details><summary>💭 Thinking</summary>

**Listed and inspected existing files**

</details>

```json
{"search_query":[{"q":"site:tc39.es/ecma262 execution contexts job queues host hooks ECMAScript specification"},{"q":"site:docs.temporal.io workflow deterministic constraints replay official"},{"q":"site:github.com/bazelbuild/starlark deterministic hermetic specification"},{"q":"site:docs.wasmtime.dev fuel epoch interruption resource limiter official"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched web, GitHub, docs, and papers for frameworks and tools**

**Fetched file content from GitHub repository**

</details>

```json
{"search_query":[{"q":"site:docs.racket-lang.org guide languages macros create languages Racket"},{"q":"site:plt.cs.northwestern.edu publications language-oriented programming Racket paper PDF"},{"q":"site:www2.ccs.neu.edu/racket/pubs language-oriented programming paper"},{"q":"site:github.com/nanopass/nanopass-framework README compiler passes"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched for Racket, Nanopass, eBPF, WebAssembly, and related resources**

**Searched Goja repository for CompileAST function**

</details>

```json
{"search_query":[{"q":"site:pkg.go.dev/github.com/dop251/goja CompileAST Parse Program"},{"q":"site:github.com/dop251/goja \"func CompileAST\""},{"q":"site:github.com/dop251/goja \"func Parse(\" \"CompileAST\""}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched web for library functions, references, and research papers**

**Research and platform design**

I’m planning to build a Malleable JavaScript Platform. It'll focus on creating a JS/TS-compatible frontend, thorough analysis, verified backends, and runtime kernels supporting realms, schedulers, and memory quotas. The strategy avoids an immediate full JS engine rewrite.

**Researched and designed platform**

</details>

```json
{"search_query":[{"q":"site:pkg.go.dev github.com/dop251/goja CompileAST Program SetTimeSource SetRandSource SetMaxCallStackSize"},{"q":"QuickJS official documentation JS_SetMemoryLimit JS_SetInterruptHandler bytecode version"},{"q":"Temporal official deterministic workflow replay side effect versioning documentation"},{"q":"Wasmtime official fuel epoch interruption resource limiter documentation"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched multiple websites and documentation sources for information**

**Searched GitHub repository for CompileAST function**

</details>

```unknown
bash -lc ls -la /mnt/data | sed -n '1,80p'; test -d /mnt/data/tiny-idp && echo HAS_TINY || true; test -d /mnt/data/goja && echo HAS_GOJA || true
```

<details><summary>💭 Thinking</summary>

**Checked and cloned repositories and directories**

</details>

```json
{"open":[{"ref_id":"https://api.github.com/repos/dop251/goja/git/trees/af2ceb9156d7?recursive=1"},{"ref_id":"https://api.github.com/repos/go-go-golems/tiny-idp/git/trees/d164ae59408bdd8bc21516274b446339b1761b1e?recursive=1"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched the web**

</details>

```json
{"search_query":[{"q":"site:github.com/dop251/goja \"CompileAST creates\""},{"q":"site:github.com/dop251/goja \"type instruction interface\""},{"q":"site:github.com/dop251/goja \"SetAsyncContextTracker\""},{"q":"site:github.com/dop251/goja \"func (r *Runtime) leave\" jobQueue"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched Goja internals, runtime API, and GitHub docs**

</details>

```unknown
bash -lc sed -n '1,260p' /home/oai/skills/docx/SKILL.md && printf '\n--- create/edit ---\n' && sed -n '1,260p' /home/oai/skills/docx/tasks/create_edit.md && printf '\n--- verify ---\n' && sed -n '1,300p' /home/oai/skills/docx/tasks/verify_render.md && printf '\n--- pdf ---\n' && sed -n '1,320p' /home/oai/skills/pdfs/SKILL.md
```

<details><summary>💭 Thinking</summary>

**Read doc and PDF skills**

</details>

```json
{"search_query":[{"q":"site:docs.temporal.io workflow determinism versioning replay official"},{"q":"site:docs.wasmtime.dev fuel epoch interruption resource limiter official"},{"q":"site:component-model.bytecodealliance.org WIT resources owned borrowed official"},{"q":"site:docs.ebpf.io verifier state pruning abstract interpretation official"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched multiple sources for technical documentation and papers**

**Fetched and searched Goja runtime and async code for analysis**

</details>

```unknown
bash -lc which pandoc || true; which libreoffice || true; python - <<'PY'
import docx,sys
print('python-docx',docx.__version__)
PY
```

The recommendation is converging on owning a typed/effect IR, verifier, and durable-control lowering, while retaining Goja as a compatibility oracle and forking only where essential.

<details><summary>💭 Thinking</summary>

**Checked required tools for document conversion**

**Fetched references, file content, and design documents for report**

</details>

```json
{"search_query":[{"q":"Defunctionalization at Work Danvy Nielsen official PDF abstract"},{"q":"Capability Myths Demolished official paper object capabilities"},{"q":"Effekt capability passing effect system official paper"},{"q":"Koka compiling with evidence passing effect handlers official paper"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched research papers and resources on language frameworks and compilers**

</details>

```unknown
bash -lc cat > /mnt/data/malleable-js-tiny-idp-monograph.md <<'EOF'
---
title: "Making JavaScript Malleable"
subtitle: "Compiler and Runtime Co-Design for Tiny-IDP, Durable Capability Workflows, and Reusable Embedded Language Platforms"
author: "Technical research and architecture report"
date: "2026-07-20"
lang: en-US
---

# Scope and source snapshot {.unnumbered}

This report studies a counterfactual extension of the architecture implemented in `go-go-golems/tiny-idp` under ticket `TINYIDP-GOJA-001`: what changes if the framework can modify Goja itself, or replace Goja with a JavaScript-compatible compiler and interpreter designed around Tiny-IDP's assurance requirements?

The Tiny-IDP source baseline is commit [`d164ae59408bdd8bc21516274b446339b1761b1e`](https://github.com/go-go-golems/tiny-idp/commit/d164ae59408bdd8bc21516274b446339b1761b1e), dated 2026-07-20. The Goja baseline used by that commit is [`af2ceb9156d7`](https://github.com/dop251/goja/commit/af2ceb9156d7), as recorded in Tiny-IDP's `go.mod`. The report treats the existing system as a successful first architecture, not as something to discard.

The investigation has four goals:

1. Identify which current invariants are implemented around Goja because Goja does not expose the required semantic hooks.
2. Determine what could become simpler, stronger, or statically checkable if the compiler and runtime were malleable.
3. Derive new programming models for framework implementers and script authors, especially direct-style durable workflows, typed capabilities, affine secrets, deterministic structured concurrency, replay, and migration.
4. Generalize the result into a project-neutral embedded-language platform rather than a Tiny-IDP-specific fork.

The word *verified* is used precisely. Static checking, bytecode verification, translation validation, model checking, differential testing, and machine-checked proof are different assurance levels. The recommended plan deliberately separates them.

The word *novel* is used in the engineering sense: a distinctive synthesis and application of known interpreter and programming-language techniques. It is not a claim of academic priority.

```{=openxml}
<w:p><w:r><w:br w:type="page"/></w:r></w:p>
```

# Executive synthesis {.unnumbered}

Tiny-IDP already made the decisive architectural move: JavaScript does not become the identity provider. It produces bounded policy decisions and data-only plans inside a native protocol kernel. Lambdas have schemas, allowed outcomes, capability requirements, effect permissions, time limits, call limits, and output limits. Browser waits become explicit pure-Go continuation records rather than retained Goja heaps. Runtime workers are leased exclusively and discarded after uncertain failure. These are interpreter design decisions even though most are implemented outside the interpreter.

Owning the compiler or interpreter would change the location and strength of those decisions.

Today, Tiny-IDP must infer safety from a collection of external mechanisms:

- callback identity is reconstructed by re-running module initialization in every runtime;
- nominal types are simulated with blank objects branded in Go-side identity maps;
- capabilities are ordinary native functions whose authority is revoked by host-side lifetime flags;
- execution is bounded primarily by wall-clock interruption and host-call budgets;
- pending asynchronous work is tracked by a parallel host-side settlement counter;
- immutable inputs are produced through JSON round-tripping and recursive freezing;
- result values are copied back through JSON and checked after execution;
- browser-spanning control flow is written manually as handler maps and explicit resume labels;
- static capability and effect contracts are declared separately from the body that uses them;
- the host cannot inspect or verify Goja bytecode because Goja's instruction representation is private.

A malleable runtime could make many of these properties semantic rather than conventional:

- callback IDs and durable checkpoint IDs could be assigned by the compiler;
- capabilities, secrets, evidence, and native resources could be dedicated VM value kinds with nominal type, generation, owner, and lifetime metadata;
- the compiler could infer capability and effect requirements from code and reject undeclared authority;
- instruction fuel, allocation quotas, microtask quotas, stack quotas, and host-call costs could be enforced at exact interpreter safe points;
- the scheduler could know the complete task tree instead of relying on Promise polling and a separate settlement census;
- direct-style `durable await` could compile to explicit state machines and serialized continuation frames;
- liveness analysis could prove that secrets, capabilities, closures, and other ephemeral values do not cross durable checkpoints;
- nondeterministic operations could be unavailable by default or recorded as replay events;
- hot reload could be checked against stable semantic IDs and continuation-frame schemas;
- a small typed core IR could be verified before any backend executes it;
- the same frontend and core could support Goja, a custom interpreter, WebAssembly, static Go generation, symbolic execution, and model-checking backends.

The strongest recommendation is **not** to begin by implementing all of ECMAScript. The strategic asset is the semantic seam between JavaScript authoring and trusted execution. The recommended platform is:

```text
JavaScript / TypeScript-shaped source
        |
        v
parser + source-preserving expansion
        |
        v
resolved Assured HIR
        |
        +--> type / effect / authority / sensitivity analysis
        +--> durable-control-flow lowering
        +--> determinism and migration analysis
        |
        v
small verified Core IR + manifest
        |
        +--> Goja backend, initially
        +--> custom interpreter, later
        +--> Wasm/component backend, optionally
        +--> symbolic and test backends
```

The project-neutral abstraction is a **host profile**. A profile declares value types, outcome variants, capabilities, effects, handle kinds, durability rules, resource costs, permitted nondeterminism, and native bindings. Tiny-IDP would be one profile. Other profiles could target approval workflows, deployment orchestration, policy engines, document pipelines, game logic, automation, or agent tool runtimes.

The recommended implementation sequence is:

1. Build a source analyzer and stable Assured HIR above public Goja APIs.
2. Generate callback registries, contracts, manifests, source maps, and continuation state machines at compile time.
3. Maintain a small Goja fork or upstreamable hook layer for fuel, scheduler events, allocation accounting, host-value kinds, and deterministic runtime configuration.
4. Introduce a project-neutral Core IR and verifier; execute it through a Goja adapter first.
5. Add a native Core IR interpreter for the assured subset when its semantics and workload are stable.
6. Prove selected critical properties of the Core IR, verifier, durable lowering, and effect boundary. Do not condition progress on proving full JavaScript.

This path preserves JavaScript usability while moving the trusted semantics into a smaller, explicit, reusable layer.

# Part I - What ownership of the interpreter changes

## 1. Tiny-IDP is already an interpreter architecture

A superficial description of Tiny-IDP says that Go embeds JavaScript. A more accurate description is that Tiny-IDP implements a staged language system around Goja.

At definition time, trusted source executes in an isolated runtime and registers a pure serializable program plus VM-local callbacks. At activation time, the same compiled source is materialized independently in every worker and compared against canonical fingerprints. At request time, one owned worker receives frozen inputs and an invocation-specific capability environment. The returned value is decoded into a closed native outcome family. Finally, Go interprets that outcome as presentation, challenge, commit, completion, denial, skip, or error.

`LambdaSpec` is already a dynamic type-and-effect contract. It records input and output schemas, allowed outcomes, required capabilities, allowed effects, and resource budgets; it intentionally does not contain the callback function itself. [TINY-LAMBDA] The outcome family is closed, and effect plans are inert requests that JavaScript never applies directly. [TINY-OUTCOME]

The browser continuation is already defunctionalized. It records a resume handler ID and typed carry rather than a closure. The durable record explicitly forbids Goja values, functions, Promises, and goroutine-local state, and includes executable generation identity, request binding, presentation state, secret and evidence references, revision, expiry, and status. [TINY-CONT]

The active design states the key distinction explicitly: in-request `await` may keep one HTTP request and one runtime invocation alive, but a browser boundary returns normally and persists a continuation. It also anticipates that a future compiler could transform restricted browser-spanning `await` syntax into the same explicit representation. [TINY-DESIGN]

Thus the question is not whether Tiny-IDP should become interpreter-driven. It already is. The question is whether interpreter semantics should remain encoded in host conventions or become first-class compiler and runtime mechanisms.

## 2. The current semantic envelope around stock Goja

The existing implementation obtains strong behavior through disciplined composition.

### 2.1 Closed runtime construction

The runtime factory disables implicit default modules, data modules, and the ambient loader, then registers only the Tiny-IDP module. Each runtime is independently created and populated. [TINY-RUNTIME]

### 2.2 Reproducible registration

The artifact is executed in each runtime. `module.exports` is copied through JSON, while the collector independently yields the registered program and callback registry. Canonical program equality, program fingerprints, callback fingerprints, schema fingerprints, and one-to-one callback membership are checked before a runtime is accepted. [TINY-RUNTIME]

This is a dynamic linker with reproducibility checks. It is rigorous, but it exists because callback identity is not represented in a compile-time artifact that Goja and Tiny-IDP jointly understand.

### 2.3 Exclusive ownership and fail-stop reuse

A runtime is not goroutine-safe, so Tiny-IDP wraps it in an owner and leases it exclusively. Invocation cancellation uses `Runtime.Interrupt`. The worker is marked reusable only after the result is valid and all capability settlements have completed. Any uncertain interruption, exception, malformed output, or settlement ambiguity causes disposal and replacement. [TINY-INVOKE] [TINY-POOL]

### 2.4 Invocation capabilities

Only declared capability names at exact versions are installed. Every call checks invocation lifetime, argument count, call budget, input size, output size, and context cancellation. Native work runs outside the VM, then schedules Promise settlement back through the runtime owner. A retained function becomes powerless when the invocation closes. [TINY-CAP]

### 2.5 Copy boundaries

Inputs are JSON-validated, parsed inside Goja, and recursively frozen. Results are copied back and validated against the lambda contract. These boundaries avoid exposing reflection-based Go host objects and prevent Goja values from entering durable state. [TINY-INVOKE]

Each mechanism is soundly motivated. The cost is that the framework has a shadow interpreter: Goja executes JavaScript, while Tiny-IDP separately tracks ownership, lifetime, pending work, capability authority, callback identity, schemas, outcomes, effects, and durability.

## 3. What public Goja exposes - and what it hides

Goja is unusually suitable for this work because it is written in pure Go, has a reusable compiled `Program`, exposes a parser and AST, permits custom time and random sources, supports interruption, and delegates event-loop policy to the embedder. It is also explicit that a `Runtime` is not goroutine-safe and that JavaScript objects cannot move between runtimes. [GOJA-README]

The public compiler seam is meaningful. `Parse` returns an AST and `CompileAST` compiles an AST into a runtime-independent `Program` reusable by multiple runtimes. [GOJA-COMPILE] This already permits an analyzer or source-to-source transform before Goja compilation.

The public runtime seam is narrower. An embedder can configure time, randomness, parser options, maximum call-stack depth, Promise rejection tracking, and asynchronous-context tracking. [GOJA-RUNTIME] It can interrupt a running VM. It can create native functions and Promises. It cannot, through public APIs:

- inspect or rewrite the compiled instruction stream;
- charge fuel per instruction or basic block;
- receive a callback for every allocation or object growth;
- define a new primitive or VM-level nominal value kind;
- replace the Promise job queue and its drain policy;
- enumerate all outstanding Promises or asynchronous roots;
- checkpoint a validated subset of execution state;
- attach effect, secrecy, ownership, or durability metadata to values;
- verify a `Program` against a project-specific bytecode policy.

The boundary is visible in the source. `Program` contains a private instruction slice. The VM dispatch loop repeatedly calls private `instruction.exec` methods, checking only profiler and interrupt state. [GOJA-COMPILER] [GOJA-VM] Promise jobs are appended to a private runtime queue and drained when top-level execution leaves normally; abrupt interruption clears the queue. [GOJA-PROMISE-QUEUE]

Goja also already implements in-memory suspension for generators and async functions. Its suspended `execCtx` contains the current program, environment stashes, private environment, program counter, stack base, arguments, value stack, try stack, iterator stack, and reference stack. Async functions are implemented through generator-like suspension and Promise reactions. [GOJA-ASYNC]

That implementation is evidence that Goja has the right control points internally. It is also evidence that serializing raw VM continuations would be the wrong durable abstraction. The captured state contains runtime-local values, object identity, environment pointers, iterators, references, and code positions. Persisting it would bind continuations to heap layout, engine version, bytecode layout, garbage-collector assumptions, and possibly secret-bearing objects.

### 3.1 The first major conclusion

Access to Goja internals is valuable primarily because it permits **instrumentation and semantic hooks**, not because Tiny-IDP should dump and restore Goja heaps.

The useful internal changes are:

- deterministic safe points and fuel charging in the dispatch loop;
- explicit scheduler and task-tree hooks around Promise jobs and host calls;
- project-defined VM value kinds for opaque handles;
- allocation and collection accounting;
- compiler metadata and stable semantic IDs;
- program inspection and verification;
- source-level and IR-level tracing;
- cheap realm reset or fresh-realm creation.

Durable continuation state should remain compiler-generated, first-order, typed, and independent of VM internals.

## 4. Five levels of ownership

There is no binary choice between "stock Goja" and "write a JavaScript engine." There is a useful five-level spectrum.

| Level | What is owned | Main gain | Main limitation |
|---|---|---|---|
| 0. Host wrapper | Runtime factory, modules, owner, pool, codecs | Low maintenance; current design | Safety properties remain external and partly duplicated |
| 1. Frontend/analyzer | Goja parser AST, resolver, type/effect analysis, source transform | Compile-time manifests, diagnostics, durable lowering | VM scheduling, memory, and fuel remain opaque |
| 2. Hooked Goja | Small fork or upstreamable hooks in compiler/VM/runtime | Exact fuel, task census, host values, tracing, reset | Fork maintenance and Goja internals enter TCB |
| 3. Assured Core VM | Own typed IR, verifier, interpreter; JS frontend remains | Small semantics, precise quotas, replay, proof target | Supports a deliberate JS subset, not arbitrary ECMAScript |
| 4. Full JS engine | Parser through GC, built-ins, JIT/interpreter | Total control | Enormous compatibility, security, performance, and maintenance burden |

The recommended destination is not necessarily Level 4. A strong system can combine Level 1, a narrow Level 2, and Level 3. JavaScript remains the authoring language, while the assured subset executes in a smaller machine.

# Part II - The proposed malleable JavaScript platform

## 5. Own the semantic seam, not the language brand

The strategic objective should be stated narrowly:

> Accept familiar JavaScript or TypeScript-shaped programs, compile them into an explicit project-neutral semantic core, verify that core against a versioned host profile, and execute it through one of several controlled backends.

The platform should not promise that every npm package or every metaprogramming trick will work. It should promise that supported code has clear authority, resource, durability, and replay semantics.

A possible architecture is:

```text
+------------------------------- Authoring -------------------------------+
| JavaScript | TypeScript annotations | JSDoc | project syntax extensions |
+-----------------------------------+-------------------------------------+
                                    |
                                    v
+------------------------------ Frontend --------------------------------+
| Parse | resolve names | expand trusted macros | preserve source maps     |
+-----------------------------------+-------------------------------------+
                                    |
                                    v
+---------------------------- Assured HIR -------------------------------+
| explicit bindings | nominal types | effects | capabilities | labels      |
| sensitivity | ownership | async regions | source provenance             |
+------------------+----------------+----------------+---------------------+
                   |                |                |
                   v                v                v
             static checks    durable lowering   manifest generation
                   |                |                |
                   +----------------+----------------+
                                    |
                                    v
+------------------------------ Core IR ---------------------------------+
| first-order CFG | typed values | host-call opcodes | checkpoints         |
| structured tasks | closed outcomes | explicit traps | cost annotations    |
+-----------------------------------+-------------------------------------+
                                    |
                          verifier + signer
                                    |
                                    v
+------------------------------- Bundle ---------------------------------+
| code | schemas | fingerprints | authority manifest | migrations | maps  |
+---------+--------------------------+----------------------------+--------+
          |                          |                            |
          v                          v                            v
   Goja backend               native Core VM                Wasm backend
```

This structure separates three concerns that are entangled in ordinary embedded JavaScript:

- **surface compatibility**: familiar syntax, modules, functions, promises, editor support;
- **semantic assurance**: authority, effects, lifetimes, durability, determinism, resource bounds;
- **execution technology**: Goja, a custom interpreter, Wasm, static Go, or symbolic execution.

The separation is what makes the system reusable across projects.

## 6. Host profiles as the project-neutral extension boundary

Tiny-IDP-specific semantics should not be compiled into the generic interpreter. They should be supplied by a versioned host profile.

A host profile is analogous to a typed interface description plus a semantic policy. WIT is a useful comparison: WIT defines component contracts and includes records, variants, results, functions, interfaces, worlds, and owned or borrowed resource handles, while deliberately not defining component behavior. [WIT] The proposed profile adds interpreter-specific policies that WIT does not attempt to express.

A profile should declare:

```text
Profile
  identity and semantic version
  source-language feature set
  value and schema types
  nominal handle kinds
  capability signatures and versions
  effect constructors and commit domains
  outcome variants
  sensitivity labels and flow rules
  ownership / borrowing / lifetime rules
  durable value rules
  determinism classes
  cost model and quotas
  host-call retry / idempotency semantics
  native binding identifiers
  migration rules
  diagnostic catalog
```

An illustrative profile fragment:

```yaml
profile: tinyidp.assured/v2

handles:
  PasswordSecret:
    sensitivity: secret
    ownership: affine
    durable: false
  ChallengeEvidence:
    sensitivity: restricted
    ownership: borrowed
    durable: reference-only

capabilities:
  account.lookup@1:
    input: IdentityLookup
    output: option<IdentityCandidate>
    effects: [account.read]
    determinism: recorded
    cost: 25
  password.verify@1:
    input: { subject: SubjectRef, password: PasswordSecret }
    output: VerificationResult
    effects: [credential.verify]
    determinism: native-evidence
    cost: 100

outcomes:
  - continue
  - present
  - challenge
  - commit
  - complete
  - deny
  - skip
  - error

checkpoints:
  max-public-frame-bytes: 8192
  forbid-live-labels: [secret, capability, transient]
```

Generated bindings would expose idiomatic project APIs while the profile remains language-neutral. A Tiny-IDP package could generate TypeScript declarations, Go dispatch stubs, schema codecs, documentation, test fixtures, and verifier tables from the same source.

### 6.1 Why profiles are more important than custom syntax

A custom keyword is visible but local. A profile determines what a program can mean. It makes extension auditable and portable:

- two projects can share the compiler while exposing different authority;
- a project can upgrade capability implementations without changing the language core;
- tooling can explain exactly which operations and effects a plugin requires;
- artifact fingerprints can include the profile version;
- a verifier can reject a bundle compiled for the wrong host;
- alternate backends can share the same contract.

## 7. The Assured HIR

The central design artifact should be a high-level intermediate representation, not Goja bytecode.

The Assured HIR should preserve enough structure for diagnostics and analysis while removing JavaScript ambiguity. It should include:

- resolved lexical bindings rather than name lookup;
- explicit function and closure capture sets;
- explicit records, variants, lists, options, results, and nominal handles;
- explicit conversions at dynamic boundaries;
- capability calls as distinguished nodes, not generic property calls;
- effect plans as typed constructors;
- sensitivity and ownership labels on values;
- structured task regions and cancellation edges;
- durable checkpoint labels;
- source spans and expansion provenance;
- explicit exceptional exits;
- finite outcome types.

A normalized function might look like:

```text
function signup.submitted(
    input: SignupPost,
    cap accountLookup: cap<account.lookup@1>,
    cap passwordPolicy: cap<password.policy@1>
) -> Outcome<SignupResult>
requires { account.read, password.policy }
budget { fuel: 25000, hostCost: 200, outputBytes: 8192 }
{
entry:
    email = project input.email
    existing = host.call accountLookup(email)
    branch isSome(existing), already_exists, check_password

already_exists:
    return deny("account_exists")

check_password:
    verdict = host.call passwordPolicy(input.password)
    branch verdict.accepted, propose_commit, weak_password

weak_password:
    return deny(verdict.code)

propose_commit:
    plan = effects [
        identity.create(email, input.displayName),
        credential.password.set(input.password)
    ]
    return commit(plan)
}
```

This is not intended as user syntax. It is the analyzable meaning after JavaScript features are elaborated.

### 7.1 Why not analyze ordinary Goja bytecode directly?

Goja bytecode is an implementation representation. It contains many instructions specialized for ECMAScript semantics and is private. Building project assurance directly on it would couple the verifier to Goja internals and make source-level concepts difficult to recover.

The HIR should instead be stable under backend changes. Goja code generation is one lowering. A custom Core VM is another. A symbolic interpreter is a third.

### 7.2 Small passes and many IRs

The compiler should prefer explicit small passes over a single large transformation. The Nanopass approach emphasizes many intermediate representations and small passes to reduce boilerplate and make compilers easier to understand and maintain. [NANOPASS]

A possible pass sequence is:

```text
JS AST
  -> module-normalized AST
  -> resolved AST
  -> project-expanded AST
  -> typed/effected HIR
  -> ownership-checked HIR
  -> async-region HIR
  -> durable state-machine HIR
  -> first-order Core IR
  -> verified bundle
```

Each pass should have a narrow contract and deterministic output. Important passes can use translation validation: after transformation, an independent checker validates the relation between input and output rather than trusting the transformer alone.

## 8. JavaScript compatibility profiles

A reusable platform should offer at least two authoring profiles.

### 8.1 Compatible profile

The compatible profile remains valid JavaScript or TypeScript. It uses imports, decorators, tagged builders, JSDoc, or generic functions to carry semantic metadata.

```typescript
import { workflow, cap, outcome, durable } from "@tinyidp/assured";

export const signup = workflow<SignupStart, SignupResult>({
  id: "signup",
  capabilities: [cap.account.lookup.v1, cap.mail.challenge.v1],
  effects: ["identity.create", "credential.password.set"],
  budget: { fuel: 80_000, hostCost: 500 }
}, durable(async ctx => {
  const form = await ctx.browser.present(SignupForm);
  const existing = await ctx.account.lookup({ email: form.email });
  if (existing) return outcome.deny("account_exists");

  const proof = await ctx.challenge.email({ address: form.email });
  if (!proof.verified) return outcome.deny("email_unverified");

  return outcome.commit(ctx.effects.signup({
    email: form.email,
    displayName: form.displayName,
    password: form.password,
    evidence: proof.evidence
  }));
}));
```

The function appears direct-style, but only selected awaitable operations are durable. The compiler distinguishes in-request capability calls from browser-spanning checkpoints through nominal return types.

Benefits:

- standard parsers and editor ecosystems remain usable;
- generated `.d.ts` files can provide types without designing a full parser;
- code can often be linted and unit-tested outside the production runtime;
- source remains recognizable JavaScript.

Costs:

- some semantic distinctions are encoded through APIs rather than syntax;
- TypeScript erasure means the production compiler must perform its own checks;
- dynamic features may need explicit rejection.

### 8.2 JS-shaped dialect

A dialect may add a small number of high-value forms:

```javascript
export durable async function signup(ctx: SignupContext)
  uses account.lookup@1, challenge.email@1
  commits identity.create, credential.password.set
  budget fuel 80000, host 500
{
  const form = durable await present SignupForm;
  const existing = await ctx.account.lookup({ email: form.email });
  if (existing) deny "account_exists";

  const proof = durable await challenge.email(form.email);
  commit signupAccount(form, proof);
}
```

New syntax is justified only when it exposes a semantic distinction that ordinary JavaScript hides. `durable await`, `uses`, `commits`, `budget`, exhaustive `match`, and explicit sensitivity annotations meet that threshold. Cosmetic syntax does not.

Racket's language architecture provides a useful warning: ordinary macros can extend syntax but cannot reliably restrict surrounding syntax or change its meaning; complete language variants require control over reader and expansion phases. [RACKET] A malleable JavaScript platform should likewise distinguish library combinators from true language profiles.

### 8.3 Recommended policy

Start with the compatible profile. Add dialect syntax only after several real projects demonstrate repeated semantic friction. Both profiles must lower to the same HIR and pass the same verifier.

# Part III - Direct-style durable workflows

## 9. The opportunity hidden in explicit continuations

Tiny-IDP's explicit handler map is the correct runtime contract but not necessarily the best source notation. The compiler can offer direct style without serializing the VM.

Consider a browser workflow written manually:

```javascript
const start = A.lambda("signup.start", specStart, ctx =>
  ctx.present.signup({ resume: "signup.submitted" })
);

const submitted = A.lambda("signup.submitted", specSubmitted, async ctx => {
  const found = await ctx.cap.account.lookup({ email: ctx.input.email });
  if (found) return ctx.deny("account_exists");
  return ctx.challenge.email({
    address: ctx.input.email,
    resume: "signup.email_verified",
    carry: { email: ctx.input.email, displayName: ctx.input.displayName }
  });
});

const emailVerified = A.lambda("signup.email_verified", specVerified, ctx =>
  ctx.commit.signup(/* ... */)
);
```

The explicit code is reviewable, but plugin authors manually maintain:

- handler IDs;
- edge wiring;
- carry projections;
- input schemas for each resumed handler;
- stable generation and migration identity;
- restrictions on values crossing boundaries.

A compiler can derive these while preserving the explicit runtime model.

## 10. CPS plus defunctionalization

The appropriate lowering is a combination of control-flow normalization, continuation-passing style, liveness analysis, and defunctionalization.

Defunctionalization is a whole-program transformation from higher-order functions to a first-order data type plus an apply function. [DEFUNC] Applied selectively to durable control flow, it converts "what to do after the browser returns" from an implicit continuation into a finite checkpoint label and a typed environment.

A simplified transformation:

```javascript
export const signup = durable(async ctx => {
  const form = await ctx.browser.present(SignupForm);
  const member = await ctx.account.lookup({ email: form.email });
  if (member) return ctx.deny("account_exists");
  const proof = await ctx.challenge.email(form.email);
  return ctx.commit.signup(form, proof);
});
```

becomes conceptually:

```text
handler signup#entry(startInput):
    return present(SignupForm,
        continuation = { checkpoint: signup#after-form, frame: {} })

handler signup#after-form(formInput):
    member = await-in-request account.lookup(formInput.email)
    if member:
        return deny("account_exists")
    return challenge.email(formInput.email,
        continuation = {
            checkpoint: signup#after-email,
            frame: publicProjection(formInput)
        })

handler signup#after-email(frame, challengeInput, evidenceRef):
    return commit signup(frame, evidenceRef)
```

The generated continuation record remains first-order:

```text
ContinuationFrame {
  artifact_digest
  profile_digest
  workflow_id
  function_id
  checkpoint_id
  frame_schema_digest
  public_frame
  native_references
  revision
  expiry
}
```

### 10.1 Liveness at checkpoints

The compiler computes which values are live after each durable await. Only those values need to enter the frame.

For each live value, the checker asks:

1. Is its type serializable under the profile?
2. Is its sensitivity label allowed in public carry?
3. Is it an owned or borrowed host handle?
4. May it cross a durable boundary by value, by stable native reference, or not at all?
5. Is its schema bounded?
6. Is its representation stable across compatible upgrades?

This removes the need for plugin authors to hand-copy carry objects and makes a crucial security property statically visible.

### 10.2 Stable checkpoint identity

A checkpoint ID must not be a raw bytecode offset or line number. Edits would invalidate it unpredictably. The compiler should use explicit or semantically derived labels:

```typescript
const form = await checkpoint("collect-signup-form",
  ctx.browser.present(SignupForm));
```

or a source annotation:

```javascript
/** @checkpoint signup.collect-form */
const form = await ctx.browser.present(SignupForm);
```

The artifact records:

- stable checkpoint ID;
- source location;
- frame schema;
- continuation successors;
- required resume event type;
- migration compatibility metadata.

An unlabeled checkpoint may receive a generated ID during development, but production activation should warn or reject workflows whose durable identities are not explicit.

### 10.3 Why raw Goja suspension remains wrong

Goja's generator suspension captures a complete execution context containing stack values, lexical environments, references, iterator state, try state, and a program counter. [GOJA-ASYNC] This is appropriate for in-memory JavaScript semantics. It is inappropriate for durable identity workflows because:

- a value stack can retain secrets and capabilities;
- object identity cannot be reconstructed portably;
- closures may capture arbitrary module state;
- program counters are tied to compiler output;
- iterators, proxies, and native host objects may be nonserializable;
- engine upgrades may change instruction layout;
- persisted heaps enlarge the attack and migration surface;
- audit tools cannot easily explain the state.

Compiler-generated continuation frames preserve only semantically live, policy-approved values.

## 11. Durable operations as an effect class

The language should distinguish at least three classes of asynchronous operation:

| Class | Example | Lifetime | Replay behavior |
|---|---|---|---|
| Pure/in-memory async | local Promise composition | invocation | not persisted |
| In-request host call | account lookup | HTTP invocation | result copied/recorded as policy permits |
| Durable suspension | browser form, external approval, timer | days or restarts | continuation persisted and resumed |

Ordinary `await` should not silently become durable. The awaited expression has a type such as:

```text
Promise<T>                 // in-memory
HostCall<T, effect-set>    // bounded in-request capability
Durable<T, checkpoint-k>   // compiler-lowered suspension
```

This type distinction prevents an accidental `await fetch(...)` from creating an undefined persistence model.

## 12. Direct style without hidden protocol authority

Ergonomics must not reverse the microkernel boundary. A direct-style workflow still cannot own HTTP, OAuth, credentials, transactions, or token issuance. The compiler-generated state machine returns the same closed outcomes and inert plans as the current system.

The lowering rule is:

```text
source convenience
    -> explicit outcome / checkpoint / effect IR
    -> native validation and commit
```

not:

```text
source convenience
    -> serialized arbitrary JavaScript runtime
```

This distinction is central. The compiler makes explicit continuations easier to author; it does not remove them from the architecture.

# Part IV - Capabilities, effects, handles, and secrets

## 13. From declared capabilities to inferred authority

Tiny-IDP currently requires a lambda to declare capability requirements and checks that only those bindings are installed. This is already object-capability style authority: a callback can invoke only operations represented by references given to it. Capability systems are particularly useful for least privilege and avoiding confused deputies. [OCAP]

A compiler can improve this in three ways.

### 13.1 Infer the capability set

Every host call is a distinguished HIR node. The compiler computes the required capability row:

```text
used(signup.submitted) = {
  account.lookup@1,
  password.policy@1,
  challenge.email@1
}
```

The source declaration can serve as a maximum authority budget:

```text
inferred capabilities subset-of declared capabilities
```

Unused declared authority becomes a warning or error. Undeclared use is an error. This prevents metadata drift.

### 13.2 Capability passing as the effect model

Effect systems can describe effects as capabilities required from a context rather than merely as labels attached to functions. The Effekt work demonstrates this design point and translates it to explicit capability-passing style. [EFFEKT]

For the proposed platform:

```text
Gamma ; C ; E |- expression : T
```

means that under value environment `Gamma`, capability environment `C`, and permitted commit-effect set `E`, the expression produces `T`.

A function type may carry requirements:

```text
(Input) -> Outcome<Result>
  requires { account.lookup@1, challenge.email@1 }
  proposes { identity.create, credential.password.set }
```

Compilation can elaborate implicit `ctx` property access into explicit capability parameters in HIR. This makes authority flow visible and supports attenuation.

### 13.3 Attenuation and scoped delegation

A capability can be narrowed before being passed to helper code:

```typescript
const lookupByEmail = ctx.account.lookup.attenuate({
  fields: ["subject", "status"],
  maxCalls: 1
});

return evaluateEligibility(lookupByEmail, input.email);
```

The attenuation is either a statically known wrapper or a host-created child capability with a smaller policy. Helpers can be polymorphic over a capability interface without receiving the whole invocation context.

This creates a new plugin design pattern: **authority-oriented modularity**. Functions are reusable because they state the exact powers they require.

## 14. Effects as inert, typed commands

Tiny-IDP's commit outcome already resembles an algebraic effect request. JavaScript constructs an effect plan; Go handles it in a native transaction.

A compiler can make this algebra explicit:

```typescript
return ctx.commit.atomic("signup-account", effects => {
  const subject = effects.identity.create({ email, displayName });
  effects.credential.password.set({ subject, password });
  effects.evidence.consume(emailEvidence);
  effects.continuation.consume(ctx.continuation);
});
```

The source does not execute those operations. It constructs a typed command program. The HIR might contain:

```text
commit "signup-account" {
  %subject = effect identity.create(%email, %displayName)
  effect credential.password.set(%subject, %password)
  effect evidence.consume(%emailEvidence)
  effect continuation.consume(%continuation)
}
```

The native committer verifies:

- the commit operation is allowed in this workflow slot;
- the exact effect sequence matches a registered transaction contract;
- handles belong to the invocation and generation;
- consumed resources are active and not replayed;
- all payloads satisfy schemas and sensitivity rules;
- the storage transaction is atomic.

The compiler can check the shape before runtime, while native code remains authoritative.

### 14.1 Effect handlers without general delimited control

The platform does not need to expose unrestricted algebraic effect handlers to plugin code. Internally, effect compilation techniques such as explicit capability passing or evidence passing are useful implementation models. [KOKA]

For plugin authors, a finite set of project-defined commands is safer and easier to explain. General handlers can remain a trusted language-extension feature.

## 15. VM-level nominal handles

The current identity-branding technique - blank JavaScript objects stored in Go-side identity maps - is clever and unforgeable within one runtime. A malleable VM can represent the concept directly.

```text
HostHandle {
  kind: HandleKind
  id: opaque integer or pointer
  owner: invocation / realm / generation
  lifetime: active | consumed | revoked
  sensitivity: public | restricted | secret
  transfer: nontransferable | borrowable | movable
  durability: never | native-reference-only | serializable
}
```

The VM exposes no user-constructible constructor. Property access can be disabled or restricted to safe metadata. The handle participates in equality only according to host policy. Exporting it through JSON, string coercion, reflection, or structured cloning fails.

This removes several layers:

- no identity side map for every branded object;
- no accidental enumeration or prototype behavior;
- direct kind checks in opcodes and verifier;
- direct lifetime invalidation;
- direct sensitivity propagation;
- cheaper detection of cross-runtime or cross-generation misuse.

WIT's distinction between owned and borrowed resource handles provides a useful interface analogy. A borrow is valid for one call; dropping an owned handle transfers or destroys responsibility. [WIT]

## 16. Affine secrets and evidence

Password and evidence handling can become substantially stronger if the language has affine or linear host values.

An affine value may be used at most once; a linear value must be used exactly once. Full linear typing may be too heavy for a JavaScript-facing language, but targeted affine rules are practical:

```text
PasswordSecret:
  cannot be copied
  cannot be compared by script
  cannot be converted to string or bytes
  cannot be stored in objects or arrays unless explicitly permitted
  cannot cross durable checkpoints
  cannot be returned
  may be passed to password-policy or commit constructors
  is zeroized or invalidated when invocation ends

EvidenceHandle:
  may be borrowed by policy checks
  must be consumed by an authorized commit or explicitly abandoned
  cannot be forged or serialized by value
```

The compiler performs escape analysis. The verifier checks use counts and lifetime regions. The runtime enforces owner and active-state checks.

This permits a useful source style:

```typescript
const form = await ctx.browser.present(SignupForm);
// form.password has type Secret<Password>, not string.
const verdict = await ctx.password.policy(form.password.borrow());
if (!verdict.accepted) return ctx.deny(verdict.code);

return ctx.commit.signup({
  public: form.publicFields,
  password: form.password.move(),
  evidence: emailEvidence.move()
});
```

`borrow()` and `move()` can be compiler concepts rather than actual methods. The syntax communicates ownership to authors and reviewers.

## 17. Sensitivity as an information-flow dimension

Tiny-IDP already marks sensitive schema fields and forbids them in public continuation carry. A compiler can propagate sensitivity through expressions.

A small lattice is often enough:

```text
public <= restricted <= secret
```

Operations have flow rules:

- concatenating a secret with a public string yields secret;
- hashing may produce restricted, not automatically public;
- a native redaction or tokenization capability may explicitly declassify;
- logging accepts only public values unless a trusted sink policy says otherwise;
- durable public frames accept only public values;
- diagnostics must not format secret values;
- exception objects cannot contain restricted or secret payloads.

The compiler should report paths, not generic errors:

```text
TIDP-SENS-0042: secret value `form.password`
flows into durable checkpoint `signup.email-proof`
through object field `pending.password`.
Move the secret directly into an immediate commit, or redesign the flow so
password entry occurs after the durable challenge.
```

This type of diagnostic makes the assurance model usable rather than punitive.

# Part V - Deterministic scheduling and structured concurrency

## 18. The hidden scheduler problem

Goja does not provide a browser or Node event loop. Promise jobs are maintained in a private queue and drained when top-level execution returns normally. Native Promise resolvers are not goroutine-safe; settlement must be routed onto the VM owner. [GOJA-PROMISE]

Tiny-IDP correctly adds an owner and a separate capability settlement tracker. However, the host and VM maintain overlapping notions of asynchronous state:

```text
VM: Promise jobs and async runners
Host: pending capability calls and owner queue
Pool: worker safety and replacement state
Context: deadline and cancellation state
```

A malleable runtime can unify these into one invocation scheduler.

## 19. Structured concurrency as a language rule

The runtime should not permit detached asynchronous work. Every spawned task belongs to a lexical task region or nursery.

```typescript
const result = await ctx.tasks.scope(async scope => {
  const identity = scope.start(() => ctx.account.lookup(input.email));
  const invitation = scope.start(() => ctx.invitation.inspect(input.code));
  return decide(await identity, await invitation);
});
```

The scheduler guarantees:

- child tasks are registered before they execute;
- cancellation propagates from parent to children;
- the scope cannot exit while children remain active;
- unobserved rejection is an invocation error;
- capability leases remain valid only inside the owning region;
- the worker is reusable only when the root task tree is terminal;
- task count and queued-job count are explicit quotas.

This replaces the heuristic question "have all Promises probably settled?" with a structural invariant:

```text
invocation complete iff
  root task is terminal
  and task tree has no live child
  and job queue is empty
  and no host settlement token is outstanding
```

### 19.1 Deterministic race semantics

`Promise.race` and concurrent host completions introduce order sensitivity. A deterministic profile can define tie-breaking:

- events receive monotonically increasing registration IDs;
- host completions are enqueued with recorded logical timestamps;
- equal-time events are ordered by registration ID;
- cancellation and timeout are represented as scheduled events;
- replay uses the recorded event order.

Projects that do not require replay may select a nondeterministic scheduler profile, but the choice is explicit and fingerprinted.

## 20. Deterministic sources

Goja already allows custom time and random sources. [GOJA-RUNTIME] A controlled runtime should go further:

- `Date.now`, `new Date`, and timers read a logical clock;
- randomness comes from a seeded or recorded capability;
- locale, timezone, collation, and Unicode data versions are fixed by the artifact;
- module resolution is closed and canonical;
- host-call results are classified as deterministic, recorded, native-evidence, or forbidden during replay;
- enumeration order and canonical encoding are specified;
- concurrency ordering is scheduler-defined;
- diagnostics and traces use stable IDs.

SES compartments omit ambient time and randomness by default because they can reveal authority and act as communication channels; powers are added explicitly. [SES] The same deny-by-default principle fits assured plugins.

## 21. Replay as an optional execution mode

Tiny-IDP's explicit continuations do not require replaying a whole workflow from its beginning. That is a strength. Still, deterministic traces are valuable for debugging, migration testing, and audit.

A trace could contain:

```text
InvocationStart {
  artifact, profile, handler, input_digest, budgets
}
HostCallRequested { seq, capability, input_digest, cost }
HostCallSettled   { seq, result_digest, classification }
CheckpointCreated { checkpoint, frame_digest, revision }
OutcomeReturned   { kind, value_digest }
InvocationEnd     { fuel_used, peak_heap, task_count }
```

Sensitive values are not recorded directly. The trace records hashes, stable codes, or encrypted audit payloads under native policy.

Temporal demonstrates one durable execution model: deterministic workflow code is replayed from an event-sourced history, while side effects are separated into activities. [TEMPORAL] Tiny-IDP need not adopt full replay, but it can borrow three ideas:

- classify and record nondeterminism;
- validate new code against historical traces;
- pin version decisions so old executions retain old meaning.

### 21.1 Three distinct determinisms

The report uses three terms separately:

1. **Compilation determinism**: the same source, compiler, profile, and dependencies produce the same bundle.
2. **Execution determinism**: the same bundle and same sequence of host results produce the same trace and outcome.
3. **Replay compatibility**: a newer bundle can consume an older recorded history or continuation without semantic divergence.

A system may provide the first two without the third. Hot-reload policy must say which guarantee applies.

# Part VI - Exact resource control

## 22. From timeout to a multidimensional budget

Wall-clock timeouts are necessary but insufficient. They are nondeterministic, depend on machine load, and do not distinguish computation from blocked host work. A malleable runtime can enforce a budget vector:

```text
Budget {
  instruction_fuel
  host_call_cost
  wall_deadline
  call_stack_depth
  heap_bytes
  object_count
  property_count
  string_bytes
  array_elements
  microtask_count
  live_task_count
  pending_host_calls
  output_bytes
  continuation_frame_bytes
  trace_bytes
}
```

### 22.1 Instruction fuel

Goja's dispatch loop has a central instruction fetch and `exec` call. A fork can charge fuel before each instruction or at basic-block entries. [GOJA-VM]

A cost model should distinguish:

- simple stack and arithmetic instructions;
- property lookup and prototype traversal;
- regular expressions;
- string and BigInt operations proportional to input size;
- JSON parsing and encoding;
- array growth and sorting;
- host calls with profile-defined costs.

A deterministic fuel budget gives reproducible failure. A wall deadline remains a secondary safety net for expensive native operations or runtime bugs.

Wasmtime makes the same distinction: fuel can deterministically bound execution, while epoch interruption is coarser and nondeterministic; resource limiters cover memory-like resources separately. [WASMTIME]

### 22.2 Safe points and cancellation

The interpreter should check:

- fuel;
- cancellation epoch;
- wall deadline;
- pending memory limit;
- debugger or trace requests;

at specified safe points. A safe point can occur per instruction in the interpreter and less frequently in optimized backends. Long-running built-ins must cooperate by charging work or polling safe points internally.

### 22.3 Memory accounting

Strict per-runtime memory limits are harder in Goja because values are ordinary Go allocations managed by the Go garbage collector. A small fork can implement logical accounting at object, string, backing-store, map, array, and Promise creation, but it will not perfectly attribute runtime overhead.

There are three levels:

1. **Logical quota**: count semantically relevant allocations and container growth. Cheap and useful, but approximate.
2. **Dedicated heap layer**: store guest objects in an interpreter-owned heap with explicit sizes and tracing. More work, more precise.
3. **Process isolation**: enforce operating-system memory limits around the runtime. Strongest availability boundary for hostile code.

QuickJS illustrates what a runtime-owned heap can expose: explicit memory limits, stack limits, interrupt handlers, custom allocation, and opaque native classes. It is a useful design comparison, although its serialized bytecode is engine-version dependent and should not be treated as a stable untrusted format. [QUICKJS]

### 22.4 Failure classification

Resource exhaustion must be a stable native error family:

```text
FuelExhausted
WallDeadlineExceeded
HeapLimitExceeded
StackLimitExceeded
MicrotaskLimitExceeded
HostCallBudgetExceeded
OutputLimitExceeded
ContinuationFrameLimitExceeded
```

It must never be reinterpreted as a policy denial or skip. The worker's reuse policy can depend on whether the runtime reached a known clean safe point.

# Part VII - Hot reload, generations, and migration

## 23. Semantic generation identity

Tiny-IDP currently fingerprints source, program IR, callbacks, and schemas, and pins continuations to program identity. A compiler-owned bundle can make the identity more complete:

```text
ArtifactIdentity = hash(
  source tree,
  dependency lock,
  frontend version,
  extension set,
  host profile,
  HIR schema,
  Core IR,
  verifier version,
  backend version,
  cost model,
  Unicode/locale data,
  generated bindings
)
```

Not every component needs to invalidate every kind of state. The artifact should expose both a full digest and semantic sub-digests:

- executable digest;
- workflow graph digest;
- checkpoint schema digest;
- capability/effect contract digest;
- UI descriptor digest;
- cost-model digest.

This enables precise compatibility decisions.

## 24. Compile-time continuation compatibility

Given old and new bundles, a migration checker can compare every live checkpoint:

```text
old checkpoint ID exists in new bundle
old resume event type is accepted
old frame schema is readable by new handler or has a migration
new handler does not require unavailable capabilities
new handler's effect authority is not silently broader
native reference kinds remain compatible
expiry and replay rules remain valid
```

Compatibility can be classified:

- `identical`: resume directly;
- `backward-compatible`: resume under new code after schema validation;
- `requires-migration`: execute named pure migration;
- `retain-old-generation`: old runtime must remain available;
- `revoke`: continuation cannot safely proceed.

### 24.1 Pure migration functions

A migration function should run in a stricter profile:

```typescript
export const migrateCollectFormV1toV2 = migration({
  from: "signup.collect-form@1",
  to: "signup.collect-form@2"
}, old => ({
  email: old.email,
  displayName: old.displayName,
  marketingConsent: false
}));
```

It receives only old public frame data, has no capabilities or nondeterminism, and produces the new frame schema. The compiler can prove termination only for a restricted language or enforce a small fuel budget.

### 24.2 Stable IDs as part of source design

Callback and checkpoint IDs should be explicit public API, like database schema names. Refactoring tools must preserve them unless the author intentionally creates a migration boundary.

This changes plugin development practice: source names are not just local implementation details; some are durable protocol names.

# Part VIII - New patterns for plugin authors

## 25. Typed workflow modules instead of registration side effects

Current callback registration requires executing trusted top-level JavaScript in every runtime. A compiler can extract and generate the registry without evaluating arbitrary initialization code.

Source:

```typescript
export const submitted = handler({
  id: "signup.submitted",
  input: SignupPost,
  output: SignupDecision
}, async ctx => { /* ... */ });
```

Generated manifest:

```json
{
  "callbacks": [{
    "id": "signup.submitted",
    "symbol": "module/signup.ts#submitted",
    "input": "SignupPost",
    "output": "SignupDecision",
    "capabilities": ["account.lookup@1"],
    "outcomes": ["deny", "challenge", "error"],
    "fuel": 30000
  }]
}
```

The runtime links a compile-time function index to the VM-local closure. It no longer discovers the program by top-level collector side effects. Re-execution fingerprint checks can remain as defense in depth for the Goja backend.

## 26. Exhaustive outcome handling

A typed `match` prevents accidental fallthrough among denial, skip, and error:

```typescript
return match(candidate, {
  found: value => ctx.complete.identity(value),
  notFound: () => ctx.skip("not_found"),
  disabled: reason => ctx.deny(reason),
  error: err => ctx.error(err.code)
});
```

The compiler checks exhaustiveness and that the lambda's declared outcome row contains every branch. In a custom dialect, this may use a dedicated `match` form. In compatible TypeScript, generated discriminated unions and a compiler plugin can provide the same semantics.

## 27. Capability-polymorphic helpers

Helpers should be parameterized by exact authority:

```typescript
async function findEligibleMember<C extends LookupMember & ReadPolicy>(
  cap: C,
  email: EmailAddress
): Promise<Option<Member>> requires C {
  const member = await cap.lookup(email);
  if (!member) return none;
  return (await cap.policy(member)).eligible ? some(member) : none;
}
```

The helper can be tested with a pure model capability, executed with a production capability, or symbolically interpreted. It cannot accidentally call mail, database, or commit APIs because those references are absent from its capability environment.

## 28. Deterministic nurseries

Plugin authors can perform bounded parallel reads without leaking work:

```typescript
const [member, invite] = await ctx.tasks.all({
  member: () => ctx.member.lookup(email),
  invite: () => ctx.invite.inspect(code)
}, { concurrency: 2, cancelOnError: true });
```

The profile gives `tasks.all` deterministic key order, exact call and task costs, and cancellation semantics.

## 29. Recorded nondeterminism

A workflow that genuinely needs randomness or current time uses an explicit operation:

```typescript
const bucket = await ctx.nondeterminism.recorded(
  "signup-experiment-bucket",
  source => source.randomInt(0, 99)
);
```

The result is captured in the invocation trace or durable history. Replay returns the recorded value. A reviewer can search all nondeterminism sites.

## 30. Effect-oriented transactions

Plugins can define named transaction constructors while native code owns execution:

```typescript
const signupCommit = defineCommit("signup.account@2", effects => ({
  input: SignupCommitInput,
  build(input) {
    const subject = effects.identity.create(input.profile);
    effects.credential.password.set(subject, input.password.move());
    effects.evidence.consume(input.emailEvidence.move());
    effects.session.establish(subject);
  }
}));
```

The constructor is compiled into a finite effect template. A native committer can require the exact template ID rather than accepting an arbitrary sequence.

## 31. Local simulation and explanation

Because host calls and outcomes are typed, a generated test harness can run a handler with model capabilities:

```typescript
const result = await simulate(signup, {
  input: fixtures.validSignup,
  capabilities: {
    "account.lookup@1": model.returning(null),
    "challenge.email@1": model.verified("evidence-1")
  },
  schedule: "deterministic",
  fuel: 80000
});

expect(result.outcome).toEqual("commit");
expect(result.effects).toMatchTemplate("signup.account@2");
expect(result.authorityUsed).toEqual([
  "account.lookup@1", "challenge.email@1"
]);
```

The same trace supports an explanation view:

```text
signup.submitted denied with account_exists
because account.lookup@1 returned an active candidate.
No commit effects were proposed.
Fuel used: 2,431 / 30,000.
Capabilities used: account.lookup@1 (1 call).
```

This is valuable to operators without exposing secret values.

# Part IX - New patterns for framework implementers

## 32. Generated boundary code

A profile compiler can generate:

- TypeScript declarations and editor documentation;
- Go capability dispatch tables;
- schema codecs and validators;
- nominal handle kind tables;
- outcome decoders;
- effect template validators;
- trace event definitions;
- conformance fixtures;
- documentation pages;
- source-map and diagnostic registries.

This removes handwritten drift between JavaScript APIs and Go validation.

## 33. An interpreter-independent invocation kernel

The framework should define one backend-neutral contract:

```go
type Engine interface {
    Load(ctx context.Context, bundle Bundle, profile HostProfile) (Image, error)
    NewRealm(ctx context.Context, image Image, limits Limits) (Realm, error)
    Invoke(ctx context.Context, realm Realm, request Invocation) (Result, error)
    CloseRealm(ctx context.Context, realm Realm) error
}
```

The `Invocation` contains only profile-defined values and capability tokens. The `Result` contains one verified outcome plus execution metrics and trace events. Goja-specific types never appear in this interface.

Backends can include:

- `gojaengine`: executes lowered code in Goja;
- `corevm`: interprets verified Core IR;
- `symbolic`: explores branches over abstract capability results;
- `staticgo`: generates Go for selected high-assurance deployments;
- `wasmengine`: executes a Component Model artifact with typed imports.

This architecture prevents the compiler project from becoming a Tiny-IDP package.

## 34. Realm images and state hygiene

Stock Tiny-IDP reuses workers after careful cleanup. A malleable engine can provide stronger realm semantics:

- immutable base image for built-ins and compiled modules;
- per-invocation overlay for globals and module state;
- copy-on-write or template cloning;
- explicit root set for host handles;
- deterministic destruction at invocation end;
- no cross-invocation module mutation unless a profile permits it.

This eliminates a residual class of bugs in which ordinary module state survives worker reuse. It may also make fresh realms cheap enough to prefer creation over cleanup.

## 35. First-class invariant monitors

The runtime can expose invariant hooks that are impossible to fake from script:

```text
onCapabilityCall
onHandleMove
onHandleBorrow
onCheckpoint
onEffectPlan
onTaskSpawn
onTaskComplete
onAllocation
onOutcome
onTrap
```

A profile installs monitors such as:

- no secret live at checkpoint;
- no active capability after invocation end;
- no effect outside declared transaction template;
- no unresolved task at worker release;
- every consumed evidence handle is consumed once;
- output authority does not exceed input authority;
- every host result is classified for replay.

Monitors provide runtime defense in depth even when static analysis is incomplete.

## 36. Model checking finite workflow structure

The compiled workflow graph is finite even when callback computations are dynamic. A symbolic backend can abstract capability results into finite variants and explore:

- every outcome path;
- reachability of commit;
- denial versus skip confusion;
- replay and duplicate submission paths;
- whether all presentations have legal resume handlers;
- whether every evidence path consumes or abandons evidence;
- whether sensitive fields can reach public frames;
- whether a workflow can loop without decreasing a budget or revision.

The output can be a counterexample trace using source labels.

## 37. Policy diffing

Because bundles contain inferred authority and effect manifests, deployment tooling can compare versions:

```text
signup v17 -> v18
  added capability: risk.score@1
  removed capability: invite.lookup@1
  added commit effect: audit.security-event
  checkpoint signup.collect-form frame changed compatibly
  checkpoint signup.verify-email unchanged
  maximum fuel increased 80,000 -> 95,000
  nondeterminism sites unchanged
```

This makes code review focus on semantic change rather than only text change.

# Part X - Extensibility across projects

## 38. Extension layers

A malleable platform needs a trust hierarchy. "Extensible compiler" must not mean arbitrary plugins can mutate bytecode after verification.

### Tier 0 - libraries and combinators

Ordinary source libraries built from existing profile operations. They add no authority and require no compiler trust.

Examples:

- workflow combinators;
- schema helpers;
- pure validation functions;
- finite decision tables.

### Tier 1 - checked source extensions

Macros or elaborators produce ordinary HIR plus provenance. Their output is re-typechecked, re-effect-checked, and verified. The extension cannot create privileged opcodes or suppress diagnostics.

Examples:

- a decision-table syntax;
- a form-definition DSL;
- a retry combinator that lowers to structured tasks;
- a policy rule language.

### Tier 2 - trusted profile extensions

A project adds value types, capabilities, effects, handle kinds, native bindings, and verifier rules. This changes the host profile and enters the project's trusted computing base.

Examples:

- Tiny-IDP password evidence;
- deployment-engine cluster handles;
- document-engine signing capabilities.

### Tier 3 - trusted language extensions

A language package changes parsing, core typing, lowering, or runtime opcodes. It must version and fingerprint the semantic profile and may require new proofs or conformance suites.

Examples:

- durable async syntax;
- a new ownership mode;
- a general effect-handler feature;
- SIMD or decimal arithmetic.

### Tier 4 - backend extensions

A new execution backend must demonstrate conformance to Core IR semantics and host-profile behavior. Differential tests and translation validation are mandatory before production use.

## 39. Extension capsules

Every extension should be a signed, versioned capsule:

```text
ExtensionCapsule {
  extension_id
  semantic_version
  compiler_api_version
  declared phases
  input_ir_versions
  output_ir_versions
  added syntax
  added profile entries
  proof/checker modules
  deterministic digest
  source-map policy
  conformance tests
  signer
}
```

The artifact records the exact extension set. Loading fails if the runtime or verifier cannot identify it.

## 40. No arbitrary bytecode mutators

The extension API should follow one rule:

> Untrusted extensions may generate or transform typed HIR, but only the trusted backend lowers verified Core IR to executable form.

This preserves a single assurance bottleneck. It resembles the value of an eBPF verifier: programs may be produced by varied frontends, but they enter the kernel only after a finite verifier establishes required safety properties. The Linux verifier tracks abstract register and stack state and enforces ownership-like obligations for reference-counted kernel pointers. [EBPF]

## 41. Language workbenches versus one-off forks

Racket demonstrates language-oriented programming through reader, expander, module, and tooling layers. Truffle demonstrates reusable language and tooling infrastructure around instrumentable AST interpreters. Nanopass demonstrates compiler construction through many small explicit passes. [RACKET] [TRUFFLE] [NANOPASS]

The proposed platform should borrow selectively:

- from Racket: explicit language/profile identity and phase separation;
- from Truffle: common instrumentation and tooling APIs across languages;
- from Nanopass: small transformations with explicit IR contracts;
- from WIT: language-neutral interfaces and resource handles;
- from eBPF: a mandatory load-time verifier;
- from Wasm: a compact typed core with formal semantics and multiple embeddings;
- from capability systems: authority represented by references, not ambient names.

It should not attempt to recreate their full ecosystems.

## 42. Example profiles beyond Tiny-IDP

### 42.1 Deployment orchestration

Capabilities:

```text
cluster.read
release.plan
release.apply
approval.request
secret.reference
```

Durable operations include approval, timer, rollout observation, and human intervention. Effects are deployment plans applied by native controllers.

### 42.2 Document approval and signing

Capabilities:

```text
document.read-metadata
review.request
signature.request
archive.commit
```

Handles represent documents, signing sessions, and evidence. Secret signing material never enters script.

### 42.3 Policy and entitlement engine

Capabilities:

```text
directory.lookup
entitlement.read
risk.score
```

No durable operations may be enabled. The same compiler can enforce pure or recorded policy evaluation and produce explanations.

### 42.4 Agent tool runtime

Capabilities are tools with typed arguments, cost, side-effect class, user-consent requirements, and delegation rules. Structured concurrency and trace replay become especially valuable. The runtime can forbid a tool handle from surviving beyond one agent turn.

### 42.5 Game or simulation rules

A deterministic profile supplies seeded randomness, logical time, bounded state mutations, and replay. The backend may prioritize throughput over secret handling while sharing the same core scheduler and verifier.

# Part XI - Verification strategy

## 43. Do not begin by proving JavaScript

Full ECMAScript is a large and evolving language with complex objects, coercions, proxies, iterators, regular expressions, modules, async behavior, and host hooks. Mechanized projects such as JSCert show that a trusted formal specification and a proved reference interpreter are possible, but also illustrate the scale of the work. [JSCERT] KJS similarly demonstrates executable formal semantics tested against Test262. A production project should use this work as guidance, not make full-language proof a prerequisite.

The assurance target should be layered.

## 44. Layer 1 - source conformance and rejection

The frontend defines an assured subset and rejects unsupported constructs:

- `eval` and `Function` constructors;
- dynamic module loading outside the profile resolver;
- proxies if they defeat analysis;
- weak references and finalization;
- reflective prototype mutation;
- detached Promises;
- ambient time and randomness;
- unbounded regular-expression features if cost cannot be controlled;
- dynamic property access on capability namespaces;
- values that cross checkpoints without stable types.

The subset should be tested against relevant Test262 cases and project-specific negative suites.

## 45. Layer 2 - HIR type, effect, and ownership checking

The checker establishes:

```text
- all names and host operations resolve;
- every value has a type and sensitivity label;
- capability use is within the authority row;
- commit effects are within the permitted effect row;
- affine handles are not duplicated or leaked;
- durable frames contain only permitted values;
- task regions close structurally;
- outcomes are exhaustive and legal for the slot;
- resource bounds are finite where required.
```

The checker should be a small separate module rather than incidental logic spread through the compiler.

## 46. Layer 3 - Core IR verifier

The Core verifier treats the bundle as untrusted input. It validates:

- binary/structural well-formedness;
- control-flow target validity;
- SSA or stack discipline;
- type consistency at block joins;
- handle ownership and lifetime state;
- capability and effect opcode permissions;
- checkpoint frame schemas;
- bounded stack and local counts;
- legal exception edges;
- cost annotations;
- closed outcome construction;
- source-map integrity as non-authoritative metadata.

A simplified handle-state rule:

```text
state(h) = owned(k)
---------------------------------- MOVE
move h transfers h to destination
and sets source state(h) = moved

state(h) = borrowed(k, region r)
current_region <= r
---------------------------------- USE-BORROW
host.call f(..., h, ...)

live_at_checkpoint(h) and durable(k) = false
---------------------------------- CHECKPOINT-REJECT
program is invalid
```

The verifier is analogous to eBPF verification in role, not in exact algorithm.

## 47. Layer 4 - translation validation

For difficult compiler passes, generate a certificate or relation checked by a simpler validator:

- source callback IDs correspond to HIR symbols;
- durable lowering preserves control-flow outcomes;
- liveness-derived frames contain exactly the required variables;
- capability inference matches host-call nodes;
- Goja backend code maps each Core host operation to the correct native stub;
- Wasm imports match profile signatures.

Translation validation reduces the amount of compiler code that must be trusted.

## 48. Layer 5 - formal Core semantics

The Core IR should have a small-step operational semantics covering:

- pure evaluation;
- host-call request and settlement events;
- task scheduling;
- cancellation;
- traps and resource exhaustion;
- checkpoint creation;
- outcome construction;
- handle movement and borrowing;
- effect-plan construction.

Candidate machine-checked theorems include:

1. **Type safety**: a verified program does not get stuck except at explicit host or resource traps.
2. **Authority confinement**: every host event is authorized by a capability in the function's environment and profile.
3. **Effect confinement**: every proposed commit effect belongs to the permitted effect row and transaction template.
4. **Checkpoint secrecy**: durable frames contain no values above their permitted sensitivity and no forbidden handle kinds.
5. **Handle safety**: affine handles are not used after move, consume, or revoke.
6. **Scheduler closure**: a successful invocation result implies no live child task or unresolved settlement remains.
7. **Lowering preservation**: durable-source execution corresponds to generated state-machine execution at observable boundaries.

CompCert's lesson is not that every compiler must be fully proved immediately. It is that semantic preservation can be decomposed pass by pass, and that a small formal IR creates a tractable proof boundary. [COMPCERT]

## 49. Layer 6 - backend conformance

Every backend runs:

- Core semantic test vectors;
- differential tests against a reference interpreter;
- property-based generated programs;
- fuzzed malformed bundles;
- cancellation and race schedules;
- resource exhaustion tests;
- host-call adversarial tests;
- source-map and diagnostic tests.

A native Core interpreter should initially be the reference, not the fastest backend. Goja and Wasm outputs are compared to it.

WebAssembly's SpecTec work is instructive: one source can generate rigorous specification material and executable artifacts, and a reference interpreter plus tests can reveal inconsistencies in prose and implementation. [SPECTEC]

## 50. Layer 7 - system-level protocol assurance

Language verification does not prove the IdP correct. Native protocol code, continuation stores, commit transactions, CSRF defenses, replay controls, key management, provider semantics, and HTTP integration remain separate proof and test obligations.

The language platform should make those boundaries sharper, not claim to absorb them.

# Part XII - Trusted computing base and threat model

## 51. TCB decomposition

A production Tiny-IDP deployment would trust:

```text
native OAuth/OIDC and HTTP kernel
continuation store and commit implementations
host profile definitions and native bindings
frontend parser or its validation boundary
HIR checker and Core verifier
selected backend runtime
artifact loader and signature verification
Go runtime and operating system
```

Compiler transformation passes can be outside the TCB if their output is fully checked. Source diagnostics and optimizers need not be trusted for safety.

## 52. Trusted operator code versus hostile code

The current Tiny-IDP design explicitly targets trusted deployment code, not hostile tenant code. Interpreter ownership can support a stronger hostile-code boundary, but it does not automatically provide one.

For hostile code, add:

- process or OS isolation;
- strict memory and CPU limits;
- no shared Go heap with protocol secrets;
- minimized native bindings;
- side-channel analysis;
- denial-of-service controls;
- dependency and supply-chain policy;
- stronger module signing and tenancy separation.

SES documentation likewise notes that compartments sharing one agent do not solve memory-exhaustion or availability threats. [SES]

## 53. Fork risk

A broad Goja fork can become a new monolith in the TCB. The mitigation is organizational and architectural:

- keep patches small and hook-oriented;
- upstream generic hooks where possible;
- pin exact commits and run Goja/Test262 conformance continuously;
- keep the Core verifier independent of Goja;
- avoid encoding Tiny-IDP concepts directly in Goja packages;
- make every fork-dependent feature optional behind an engine interface;
- maintain differential tests against unmodified Goja for ordinary semantics.

# Part XIII - Decision analysis

## 54. Option comparison

| Option | Usability | Assurance gain | Maintenance | Portability | Recommendation |
|---|---:|---:|---:|---:|---|
| Continue host-only Goja wrapper | Medium | Medium | Low | Medium | Maintain as baseline |
| Add AST analysis and generated manifests | High | High | Low-medium | High | Begin here |
| Thin Goja hook fork | High | High for metering/scheduler | Medium | Medium | Recommended after frontend |
| Own Assured Core interpreter | High for supported subset | Very high | Medium-high | High | Strategic target |
| Compile Core IR to Wasm | Medium-high | High | Medium-high | Very high | Optional backend |
| Replace Goja with QuickJS | Similar author experience | Better memory hooks, worse Go integration | Medium-high | Medium | Useful comparison, not primary path |
| Build full ECMAScript engine | Potentially high | Depends on implementation maturity | Extreme | Low initially | Do not start here |

## 55. What a thin Goja fork should expose

A disciplined hook proposal could include:

```go
type ExecutionObserver interface {
    BeforeInstruction(pc int, opcode Opcode, cost uint64) error
    AfterInstruction(pc int)
    OnJobEnqueue(job JobInfo) error
    OnJobStart(job JobInfo)
    OnJobEnd(job JobInfo, result JobResult)
    OnAllocate(kind AllocationKind, bytes int64) error
    OnHostValueCreate(info HostValueInfo) error
}

type RuntimePolicy struct {
    Clock             Now
    Random            RandSource
    Observer          ExecutionObserver
    JobScheduler      JobScheduler
    HostValueRegistry HostValueRegistry
    RealmPolicy       RealmPolicy
}
```

The exact API would evolve, but the principle is stable: generic embedding hooks belong in Goja; Tiny-IDP-specific capability and workflow semantics belong above them.

### 55.1 High-value first hooks

1. Instruction/basic-block fuel callback.
2. Promise job enqueue/dequeue and pending-job count.
3. Async runner/task lifecycle events.
4. VM-owned opaque host value with kind and finalizer hooks.
5. Allocation accounting for major guest structures.
6. Deterministic realm reset or clone API.
7. Read-only compiled program inspection with stable opcode metadata.
8. Compiler callback for source span and semantic annotation propagation.

## 56. What not to put in Goja

Do not add:

- Tiny-IDP outcome enums;
- password or evidence concepts;
- OAuth-specific opcodes;
- continuation database formats;
- SQL transaction semantics;
- project-specific schemas;
- arbitrary compiler plugin execution inside the VM.

Those belong in profiles, HIR, verifier rules, and native bindings.

# Part XIV - Recommended roadmap

## 57. Phase 0 - preserve and measure the baseline

Before changing semantics:

- keep the existing runtime factory, owner, pool, capability bridge, and continuation model as the reference behavior;
- add complete invocation traces and metrics around current Goja;
- construct conformance fixtures for every outcome, capability, continuation, cancellation, and worker-disposal path;
- record performance and failure behavior.

Deliverable: a reference test corpus independent of implementation internals.

## 58. Phase 1 - compiler frontend above public Goja

Use Goja's public `Parse` and `CompileAST` seam. The parser and AST are documented as works in progress, so isolate them behind an internal adapter. [GOJA-PARSER]

Build:

- module normalization;
- stable symbol and callback IDs;
- project API recognition;
- source-level capability/effect inference;
- unsupported-feature checks;
- deterministic manifest generation;
- source maps and diagnostics;
- compile-time workflow graph extraction;
- generated TypeScript declarations and Go binding tables.

Continue executing through stock Goja. Compare generated manifests to current dynamic collector output.

Deliverable: deterministic compile artifacts without a runtime fork.

## 59. Phase 2 - durable lowering

Add:

- nominal durable-operation types;
- explicit checkpoint annotations;
- liveness analysis;
- sensitivity and handle escape checks;
- state-machine generation;
- continuation-frame schemas;
- migration metadata;
- source-to-generated-handler mapping.

Execute generated handlers through the current Tiny-IDP runtime. The native continuation record remains authoritative.

Deliverable: direct-style durable workflow authoring with no VM serialization.

## 60. Phase 3 - thin Goja hook layer

Implement or upstream:

- deterministic fuel;
- job/task lifecycle observation;
- exact invocation scheduler integration;
- opaque host values;
- logical allocation quotas;
- realm state controls;
- program inspection.

Replace Promise polling and parallel settlement inference with scheduler-owned completion. Keep fail-stop worker disposal as defense in depth.

Deliverable: stronger runtime invariants and better operational diagnostics.

## 61. Phase 4 - Core IR and verifier

Define a versioned binary and textual Core IR. Implement:

- reference interpreter;
- load-time verifier;
- profile linker;
- deterministic scheduler;
- host-handle table;
- trace format;
- differential tests against Goja backend.

Initially compile only a narrow subset. Unsupported functions continue through the Goja backend if the profile permits a mixed bundle, but durable and high-assurance handlers should prefer Core IR.

Deliverable: interpreter-independent assured execution.

## 62. Phase 5 - reusable platform extraction

Move generic components into project-neutral modules:

```text
mjs/frontend
mjs/hir
mjs/coreir
mjs/verifier
mjs/runtime
mjs/profile
mjs/backend/goja
mjs/backend/corevm
mjs/testing
mjs/lsp
```

Keep Tiny-IDP in:

```text
profiles/tinyidp
bindings/tinyidp-go
packages/tinyidp-js
```

Pilot a second profile before freezing extension APIs. A deployment or document-approval workflow is a better validation than another identity use case.

## 63. Phase 6 - selective mechanization

Formalize:

- Core IR typing and small-step semantics;
- capability/effect confinement;
- checkpoint secrecy;
- handle lifetime safety;
- selected durable-lowering rules.

Use the formal model to generate or validate executable test vectors. Mechanize one critical compiler pass or verifier property at a time.

Deliverable: meaningful machine-checked assurance without attempting a full JavaScript proof.

# Part XV - Critical limitations and open questions

## 64. JavaScript dynamism versus static assurance

Dynamic property access, prototype mutation, proxies, reflection, coercion, and higher-order callbacks complicate effect and authority inference. The platform must choose among:

- reject them in assured code;
- permit them only in pure regions;
- conservatively widen authority and effects;
- lower them to a dynamic boundary with runtime checks;
- execute them only in the general Goja backend.

A mixed system needs visible boundary markers. Silent fallback would undermine review.

## 65. Memory accounting in Go

A Goja fork cannot obtain perfect per-realm memory isolation while guest values share the Go heap. Logical accounting is still useful, but hostile multi-tenant execution requires process isolation or an interpreter-owned heap.

## 66. Stable semantics across engine upgrades

Even with a stable Core IR, JavaScript frontend semantics can change with parser, Unicode, regular-expression, or standard-library upgrades. Artifacts must pin semantic dependencies, and compatibility tests must include source-level edge cases.

## 67. Cost-model stability

Fuel is deterministic only relative to a cost model and compiler version. Optimizations may change instruction counts. Budgets should be attached to semantic operations where possible and versioned with the artifact. Deployment tooling should show budget deltas.

## 68. Migration policy is a product decision

Automatic migration is not always safer than retaining old generations. Identity workflows may prefer exact-generation resumption for high-risk steps and migration for low-risk presentation changes. The compiler can classify compatibility, but native policy decides.

## 69. Extensibility can destroy compositionality

A compiler that lets extensions rewrite arbitrary trees, inspect unrelated modules, or introduce hidden authority becomes difficult to reason about. Phase separation, hygienic source provenance, restricted extension APIs, post-expansion checking, and a single Core verifier are mandatory.

## 70. Performance

A custom reference interpreter will likely be slower than Goja. That is acceptable initially if high-assurance handlers are short and host-call dominated. Performance work should follow profiles and traces, not precede semantic stability.

# Conclusion

Having access to Goja's interpreter would materially improve Tiny-IDP, but the most important improvements are not JavaScript syntax features. They are semantic hooks:

- exact execution and memory accounting;
- an owned deterministic scheduler;
- VM-level nominal handles and lifetimes;
- inspectable compiled programs;
- compiler-propagated source identity;
- clean realm lifecycle;
- first-class traces and invariant monitors.

Creating a complete JavaScript engine would provide maximum control but is not the efficient first move. The higher-leverage design is a malleable compiler platform with a JavaScript-compatible frontend, a typed and effect-aware HIR, compiler-lowered explicit continuations, a small verified Core IR, a load-time verifier, and multiple execution backends.

For Tiny-IDP, this would make the current rigorous architecture more usable without weakening it. Plugin authors could write direct-style durable workflows, receive precise authority and secrecy diagnostics, use structured concurrency, and test against model capabilities. Framework authors could replace dynamic registration discovery with generated manifests, unify async settlement with the scheduler, enforce deterministic fuel and handle lifetimes, check migrations, and model-check finite workflow structure.

Across projects, the host-profile abstraction is the decisive generalization. It turns "a Tiny-IDP Goja fork" into a reusable embedded-language workbench where each domain supplies its own types, capabilities, effects, outcomes, resources, costs, and durability rules while sharing the compiler, verifier, scheduler, trace system, tooling, and backends.

The governing design rule is:

> Make source code pleasant, make authority explicit, make durable state first-order, make executable artifacts verifiable, and keep native protocol authority outside the scripting language.

# Appendix A - Proposed Core IR sketch {.unnumbered}

```text
module tinyidp.signup@2
profile tinyidp.assured/v2

handle PasswordSecret affine secret ephemeral
handle EvidenceRef affine restricted durable-ref
handle ContinuationRef affine restricted ephemeral

capability account.lookup@1:
  (IdentityLookup) -> option<IdentityCandidate>
  effect account.read
  cost 25

function signup.submitted(
  %input: SignupPost,
  %password: PasswordSecret,
  %cont: ContinuationRef,
  cap %lookup: account.lookup@1
) -> Outcome<SignupResult>
capabilities { account.lookup@1 }
effects { identity.create, credential.password.set,
          evidence.consume, continuation.consume }
limits { fuel 30000, host 200, heap 1048576, jobs 16 }
{
block entry:
  %email = record.get %input "email"
  %candidate = host.call %lookup (%email)
  %exists = option.is_some %candidate
  br %exists block deny_exists block commit_new

block deny_exists:
  %out = outcome.deny "account_exists"
  ret %out

block commit_new:
  %plan0 = effect.begin "signup.account@2"
  %plan1, %subject = effect.append %plan0 identity.create (%input)
  %plan2 = effect.append.move %plan1 credential.password.set
             (%subject, %password)
  %plan3 = effect.append.move %plan2 continuation.consume (%cont)
  %out = outcome.commit %plan3
  ret %out
}
```

# Appendix B - Selected verifier rules {.unnumbered}

## B.1 Capability call

```text
C(capID) = capability A : I -> O ! e
Gamma(v) = I
A in permittedCapabilities(function)
e in permittedRuntimeEffects(function)
------------------------------------------------ CAP-CALL
Gamma ; C ; E |- host.call A(v) : O ! {e}
```

## B.2 Effect construction

```text
E(effectID) = effect K : I -> O
Gamma(v) = I
K in permittedCommitEffects(function)
K acceptedBy(templateID, position)
------------------------------------------------ EFFECT-APPEND
Gamma ; C ; E |- append templateID K(v) : Plan<next> ! {}
```

Effect construction is pure with respect to native state. The resulting plan is interpreted later by the native committer.

## B.3 Durable checkpoint

```text
live(pc) = {v1 ... vn}
for all vi:
  durableType(type(vi))
  sensitivity(vi) <= checkpointLimit
  ownership(vi) not-in {borrowed, capability, transient}
sizeBound(frame(v1 ... vn)) <= maxFrame
------------------------------------------------ CHECKPOINT
checkpoint k frame(v1 ... vn) is valid
```

## B.4 Affine move

```text
Gamma(h) = owned Handle<K>
------------------------------------------------ MOVE
Gamma |- move h : Handle<K>
post-state Gamma(h) = moved
```

Any later read of `h` is rejected.

## B.5 Successful invocation

```text
rootTask = terminal
liveChildren(rootTask) = empty
pendingJobs = 0
pendingSettlements = 0
outcome is well-typed and allowed
------------------------------------------------ INVOKE-SUCCESS
realm may be returned to reusable state
```

# Appendix C - Artifact manifest sketch {.unnumbered}

```json
{
  "format": "mjs.bundle/v1",
  "artifactDigest": "sha256:...",
  "sourceDigest": "sha256:...",
  "profile": {
    "id": "tinyidp.assured",
    "version": "2.1.0",
    "digest": "sha256:..."
  },
  "compiler": {
    "version": "0.8.0",
    "frontend": "goja-ast-adapter/af2ceb9156d7",
    "extensions": ["durable-async/1", "tinyidp-ui/2"]
  },
  "program": {
    "coreIrDigest": "sha256:...",
    "schemaDigest": "sha256:...",
    "checkpointDigest": "sha256:...",
    "authorityDigest": "sha256:..."
  },
  "callbacks": [
    {
      "id": "signup.submitted",
      "function": 17,
      "capabilities": ["account.lookup@1"],
      "effects": ["identity.create", "credential.password.set"],
      "outcomes": ["deny", "commit", "error"],
      "limits": {"fuel": 30000, "hostCost": 200}
    }
  ],
  "checkpoints": [
    {
      "id": "signup.collect-form",
      "frameSchema": "SignupCollectFormFrameV2",
      "resumeEvent": "SignupPostV2"
    }
  ],
  "migrations": [
    {
      "from": "signup.collect-form@1",
      "to": "signup.collect-form@2",
      "function": 41
    }
  ],
  "signatures": []
}
```

# Appendix D - Research and primary-source notes {.unnumbered}

The following sources informed the analysis. Repository links are pinned where the report depends on implementation details.

**[TINY-LAMBDA] Tiny-IDP lambda contract.** `pkg/idpprogram/lambda.go` at the analyzed commit. The type records callback identity, schemas, allowed outcomes, capability and effect sets, budgets, and source location, while excluding the callback function itself.  
<https://github.com/go-go-golems/tiny-idp/blob/d164ae59408bdd8bc21516274b446339b1761b1e/pkg/idpprogram/lambda.go>

**[TINY-OUTCOME] Tiny-IDP outcome algebra.** `pkg/idpprogram/outcomes.go`. The outcome family is closed; browser continuations and effect plans are data-only and validated against the lambda contract.  
<https://github.com/go-go-golems/tiny-idp/blob/d164ae59408bdd8bc21516274b446339b1761b1e/pkg/idpprogram/outcomes.go>

**[TINY-CONT] Tiny-IDP durable continuation record.** `pkg/idpcontinuation/types.go`. The package explicitly excludes Goja values and stores pure-Go restart-safe state.  
<https://github.com/go-go-golems/tiny-idp/blob/d164ae59408bdd8bc21516274b446339b1761b1e/pkg/idpcontinuation/types.go>

**[TINY-DESIGN] Lambda-first design with explicit browser continuations.** The active design distinguishes in-request Promises from browser continuations and anticipates compiler lowering of restricted browser-spanning await.  
<https://github.com/go-go-golems/tiny-idp/blob/d164ae59408bdd8bc21516274b446339b1761b1e/ttmp/2026/07/10/TINYIDP-GOJA-001--go-go-goja-identity-microkernel-scripting-layer/design-doc/03-lambda-first-tiny-idp-javascript-api-with-explicit-browser-continuations.md>

**[TINY-RUNTIME] Tiny-IDP runtime factory.** Closed module loader, independent runtime materialization, canonical equality, and fingerprint checks.  
<https://github.com/go-go-golems/tiny-idp/blob/d164ae59408bdd8bc21516274b446339b1761b1e/pkg/idpscript/runtime_factory.go>

**[TINY-INVOKE] Tiny-IDP invocation path.** Runtime interruption, deep-frozen JSON input, Promise handling, settlement wait, outcome decoding, and safe worker classification.  
<https://github.com/go-go-golems/tiny-idp/blob/d164ae59408bdd8bc21516274b446339b1761b1e/pkg/idpscript/invoke.go>

**[TINY-CAP] Tiny-IDP capability bridge.** Versioned bindings, call and byte budgets, lifetime revocation, owner-routed Promise settlement, and panic conversion.  
<https://github.com/go-go-golems/tiny-idp/blob/d164ae59408bdd8bc21516274b446339b1761b1e/pkg/idpscript/capabilities.go>

**[TINY-POOL] Tiny-IDP worker pool.** Exclusive leasing and fail-stop discard/replacement.  
<https://github.com/go-go-golems/tiny-idp/blob/d164ae59408bdd8bc21516274b446339b1761b1e/pkg/idpscript/pool.go>

**[GOJA-README] Goja project documentation.** Pure-Go ECMAScript runtime, runtime ownership constraints, object non-transferability, interrupt behavior, and embedder-owned event-loop policy.  
<https://github.com/dop251/goja/blob/af2ceb9156d7/README.md>

**[GOJA-COMPILE] Goja compile seam.** `Parse`, `CompileAST`, and runtime-independent `Program`.  
<https://github.com/dop251/goja/blob/af2ceb9156d7/runtime.go#L1296-L1380>

**[GOJA-PARSER] Goja parser.** The parser returns an AST, while its parser and AST interfaces are described as works in progress.  
<https://github.com/dop251/goja/blob/af2ceb9156d7/parser/parser.go>

**[GOJA-COMPILER] Goja compiler representation.** `Program` contains the private instruction representation and source mapping data.  
<https://github.com/dop251/goja/blob/af2ceb9156d7/compiler.go>

**[GOJA-VM] Goja VM dispatch and suspension.** The central dispatch loop, interrupt check, execution context, and suspension state.  
<https://github.com/dop251/goja/blob/af2ceb9156d7/vm.go>

**[GOJA-ASYNC] Goja async and generator execution.** Async functions use an async runner and generator suspension over an execution context.  
<https://github.com/dop251/goja/blob/af2ceb9156d7/func.go>

**[GOJA-PROMISE] Goja Promise implementation.** Promise runtime locality, non-goroutine-safe settlement, rejection tracking, and async-context tracking.  
<https://github.com/dop251/goja/blob/af2ceb9156d7/builtin_promise.go>

**[GOJA-PROMISE-QUEUE] Goja runtime job queue.** Promise jobs are private runtime state and are drained on normal top-level exit.  
<https://github.com/dop251/goja/blob/af2ceb9156d7/runtime.go#L2840-L2860>

**[GOJA-RUNTIME] Goja runtime configuration.** Custom random and time sources, parser options, stack limit, and async/rejection tracking.  
<https://pkg.go.dev/github.com/dop251/goja>

**[OCAP] Miller, Yee, and Shapiro, "Capability Myths Demolished."** The paper analyzes capability models and argues that pure capability systems support least privilege and avoid confused-deputy problems.  
<https://papers.agoric.com/papers/capability-myths-demolished/abstract/>

**[SES] Secure ECMAScript compartments.** SES compartments receive only expressly supplied powers and lock down shared intrinsics; the documentation also notes that same-agent compartments do not solve availability and memory-exhaustion threats.  
<https://github.com/endojs/endo/tree/master/packages/ses>

**[DEFUNC] Danvy and Nielsen, "Defunctionalization at Work."** Defunctionalization is presented as a whole-program transformation from higher-order to first-order programs.  
<https://www.brics.dk/RS/01/23/>

**[EFFEKT] Brachthaeuser, Schuster, and Ostermann, "Effects as Capabilities."** Effect types express capabilities required from context and are translated to explicit capability-passing style.  
<https://se.cs.uni-tuebingen.de/publications/brachthaeuser20effekt/>

**[KOKA] Xie and Leijen, "Generalized Evidence Passing for Effect Handlers."** A sequence of effect-handler compilation techniques culminating in efficient lower-level compilation.  
<https://www.microsoft.com/en-us/research/publication/generalized-evidence-passing-for-effect-handlers/>

**[TEMPORAL] Temporal architecture.** Durable workflows use event-sourced history; workflow code is deterministic and side-effect-free while activities own side effects.  
<https://github.com/temporalio/temporal/blob/main/docs/architecture/README.md>

**[WASMTIME] Wasmtime resource controls.** Fuel provides deterministic execution bounds; epoch interruption provides coarser interruption; stores expose resource limiters and async yielding.  
<https://docs.wasmtime.dev/api/wasmtime/struct.Store.html>

**[QUICKJS] QuickJS documentation.** Small embeddable engine with explicit runtime controls and a runtime-owned memory model.  
<https://www.bellard.org/quickjs/>

**[WIT] WebAssembly Interface Types.** WIT defines contracts, records, variants, results, interfaces, worlds, and owned or borrowed resource handles without defining component behavior.  
<https://component-model.bytecodealliance.org/design/wit.html>

**[EBPF] Linux eBPF verifier documentation.** The verifier explores abstract machine states and enforces type, memory, and reference-lifetime constraints before programs execute.  
<https://docs.kernel.org/bpf/verifier.html>

**[RACKET] Racket Guide, "Creating Languages."** Distinguishes ordinary macro extension from control over reader and language-expansion layers.  
<https://docs.racket-lang.org/guide/languages.html>

**[NANOPASS] Nanopass Framework.** Compiler construction through small passes and many intermediate representations.  
<https://nanopass.org/>

**[TRUFFLE] GraalVM Truffle Language Implementation Framework.** Reusable language and tool infrastructure built around instrumentable self-modifying AST interpreters.  
<https://www.graalvm.org/latest/graalvm-as-a-platform/language-implementation-framework/>

**[JSCERT] JSCert.** Mechanized ECMAScript 5 specification in Coq plus a proved reference interpreter tested with Test262.  
<https://jscert.org/>

**[COMPCERT] CompCert.** A compiler with machine-checked semantic-preservation proofs, decomposed across compiler passes and intermediate languages.  
<https://compcert.org/>

**[SPECTEC] WebAssembly SpecTec.** A specification toolchain designed to generate rigorous semantics, prose, and executable artifacts from a shared source.  
<https://webassembly.org/news/2025-03-27-spectec/>
EOF
wc -w /mnt/data/malleable-js-tiny-idp-monograph.md
wc -l /mnt/data/malleable-js-tiny-idp-monograph.md
ls -lh /mnt/data/malleable-js-tiny-idp-monograph.md
```

<details><summary>💭 Thinking</summary>

**Generated monograph document in Markdown format and checked Pandoc version**

</details>

```unknown
bash -lc pandoc --print-default-data-file reference.docx > /mnt/data/reference-default.docx
pandoc /mnt/data/malleable-js-tiny-idp-monograph.md \
  --from markdown+raw_attribute+fenced_divs \
  --to docx \
  --reference-doc=/mnt/data/reference-default.docx \
  --toc --toc-depth=3 --number-sections \
  --metadata toc-title='Contents' \
  -o /mnt/data/malleable-js-draft.docx
python - <<'PY'
from docx import Document
p='/mnt/data/malleable-js-draft.docx'
d=Document(p)
for i,para in enumerate(d.paragraphs[:35]):
    print(i, repr(para.text[:100]), para.style.name)
PY
```

<details><summary>💭 Thinking</summary>

**Generated DOCX with TOC and custom page breaks**

**Preparing final deliverables**

I’m focused on converting the monograph into DOCX and PDF formats, inspecting each page and making fixes. I’m fulfilling the user’s request using the provided markdown artifact and finalized deliverables.

**Prepared final deliverables**

</details>

```unknown
bash -lc cat /home/oai/skills/docx/SKILL.md && printf '\n---PDF SKILL---\n' && cat /home/oai/skills/pdfs/SKILL.md
```

<details><summary>💭 Thinking</summary>

**Inspected and patched document styles and generated references**

</details>

```unknown
bash -lc rm -rf /tmp/malleable_docx_render && mkdir -p /tmp/malleable_docx_render
python /home/oai/skills/docx/render_docx.py /mnt/data/malleable-js-tiny-idp-monograph.docx --output_dir /tmp/malleable_docx_render --emit_pdf --verbose
ls -lh /tmp/malleable_docx_render | sed -n '1,30p'
find /tmp/malleable_docx_render -maxdepth 1 -name 'page-*.png' | wc -l
```

<details><summary>💭 Thinking</summary>

**Researching sources and context**

I’m picking up from an interrupted attempt. I’ll recheck the gathered sources and possibly search for more current information—especially around Go, Tiny-IDP, and related systems—ensuring accuracy and relevance.

**Researched sources and context**

</details>

```unknown
bash -lc ls -lah /mnt/data | sed -n '1,200p' && find /mnt/data -maxdepth 2 -type f \( -iname '*goja*' -o -iname '*interpreter*' -o -iname '*malleable*' \) -printf '%p %s bytes\n' | sort
```

<details><summary>💭 Thinking</summary>

**Inspected data and searched for relevant files**

**Brainstorming interpreter design**

I’m thinking through how using or creating a custom JavaScript interpreter could improve Tiny-IDP. Expanding Goja’s functionality, or creating a new one, might simplify design, enhance extensibility, and trigger new patterns for both frameworks and plugins.

**Continuing monograph work**

I’m resuming work on the second monograph. I'll verify the partial manuscript, fill in the remaining sections, and review the comparative and architectural concepts before rendering the full versions in PDF, DOCX, and Markdown.

**Brainstormed interpreter design and continued monograph work**

</details>

```unknown
bash -lc ls -lah /mnt/data | sed -n '1,220p'; printf '\n--- candidates ---\n'; find /mnt/data -maxdepth 2 -type f \( -iname '*malleab*' -o -iname '*compiler*' -o -iname '*goja*' -o -iname '*interpreter*' -o -iname '*semantic*' \) -printf '%p\t%k KB\n' | sort
```

<details><summary>💭 Thinking</summary>

**Inspected and listed candidate files in directory**

</details>

```unknown
import os, glob, pathlib, json, textwrap, subprocess, sys, re
files = sorted(glob.glob('/mnt/data/*'))
[(os.path.basename(f), os.path.getsize(f) if os.path.isfile(f) else None) for f in files[:200]]

```

<details><summary>💭 Thinking</summary>

**Listed files and their sizes**

</details>

```unknown
bash -lc exit 42
```

The 50-page manuscript now frames Tiny-IDP as one authority-selecting “world” atop canonical MIR and versioned dialect packs. Layout defects are corrected; final artifact checks and packaging remain.

<details><summary>💭 Thinking</summary>

**Tested container command with exit code**

</details>

```json
{"paths":["GitHub"],"query":"repository"}
```

```json
{"paths":["GitHub"],"query":"fetch_file"}
```

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

