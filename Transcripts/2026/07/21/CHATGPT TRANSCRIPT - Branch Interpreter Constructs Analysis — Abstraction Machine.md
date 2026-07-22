# Branch · Branch · Interpreter Constructs Analysis

- URL: https://chatgpt.com/c/6a5e8a47-4dd8-83ea-ba25-fc7fd232d819
- Created: 2026-07-20T20:51:21.153Z

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


---

> [image: sediment://file_0000000009ec81f5bd8c8a16fe917402]
> [image: sediment://file_00000000edc0822f90c46bd725210a1a]
> [image: sediment://file_0000000093c4820c9f6f5c89ef172efe]
> Based on the documents above I recorded my thoughts :
>
> [Speaker 1 - 0:01]
> All right, so I'm gonna try to talk my way through an article based on what I've been writing on, on WhatsApp this morning. The, the whole thing is about basically the step function that Sol 5.6, so OpenAI's Sol 5.6 model, um, from my perspective, and it being like one of the, the biggest jumps since I guess last year's 5.2 or maybe GPT-5. Actually, GPT-5. So GPT-5 was the first model where I felt that I could actually really refactor, uh, significant refactors, like basically not have to, to babysit, uh, I think it was like Sol at 4 at this time. Um, and 5.6 is, since the last year, kind of feels like a similar step function, and the way I can describe it for now, 'cause it's only been two, two weeks since I played with it, is that it's able to do research on its own in an almost unsupervised manner, the same way GPT-5 was able to do refactoring in an almost unsupervised manner. And it's also able to teach, or by teaching I mean it's able to synthesize pretty complex thinking workflows and patterns that it has recognized and put together in a way that makes sense outside of the scope of this pattern matching. Uh, so it means like explaining concepts up front, being able to synthesize different approaches it's taken, and like giving them names, and being able to relate them to each other, and introduce them in a way that has narrative, and like walks either a reader along, or if you create design documents and specs, uh, able to walk a model along to, to not like confront it with the whole complexity at once. I think that's obviously hard to quantify, hard to describe, um, but what I did this morning, or, or basically, um, been doing over the last two weeks is, uh, I've been basically building my own identity provider, my IDP, and I've also And, um, so I've, I've been creating this IDP, and, uh, once Sol came out, I asked it to, to ask, uh, to, to research and add, uh, static analysis and model checking, and do some research on OAuth, um, theorem proving and formal methods, and it, it did a bunch of research, which, you know, was expected. But usually when I asked previous models to do research, you could tell in the result that it was like kind of copy-pasting research together and maybe like drawing some inferences, but it would quickly go sideways, especially on like complex things like, uh, uh, like formal methods papers, and it would really depend on the kind of stuff that it found. And 5.6, on the other hand, was able, I think, to really kind of synthesize this down to a set of core ideas and kind of apply them to the code base. Uh, and, and this was my very first prompt, so I think it was pretty, pretty mediocre overall, and I would probably do it differently right now. Um, and this IDP is, is a code base that I never read, um, and I got it to build all of it and expanded it, and like kind of got it, uh, decided to, to token max and kind of just forge ahead, build something that I knew would be too complex for me to understand, but kind of see how far I could push the model. And, and Sol built something that, um, worked, right? And also looked pretty systematic in its approach, at least from the, from the few tasks and design documents that I glanced at. It, it looked like not complete madness, and I could tell it, it is doing a s- a pretty clear, uh, job without getting lost in the weeds, which is, which is already kind of fascinating, but not maybe the, the groundbreaking thing. And as I was pushing it into production, I realized that I really wanted to have a scripting layer that I was holding off on to basically allow me to say, to do something like virtual users or to do an invite mechanism that's not like hard-coded into the IDP itself, because I really want to make this like a building block, kind of Lego block system. And one thing I realized is that as it was adding all these static analysis and model checking primitives, it really refactored the code base to fundamentally, on a fundamental level, uh, to introduce objects that allowed it to do the whole tracing and assertions and invariants that the static analysis like kind of required. That's a first. I've, I've never really seen refactoring like completely overhaul the internal structure of a project to, to readapt it to, uh, a new ask without, especially without me asking it to, to do so, because I just told it to research and, and improve it, right? So the second phase of where I was now expecting something similar was adding these scripting primitives and basically make it scriptable. And obviously, scripting an IDP has the potential to just undo all these like invariants, assertions, and all of that that I had put in. In this case, it actually rejected my proposal or like rejected my, my, my naive prompt and said like, "Oh, we're not gonna turn this into a scriptable IDP." Instead, what I will, what, what we will do is, is, um, allow JavaScript to provide very tailored, uh, operators and, and, uh, uh, config options and, and potential other solutions. And I, uh, have a s- a screenshot that I put into WhatsApp of one of the pages that I heavily annotated of a whole bunch of, um- Out of that JS design document where you can really tell that it's, uh, um, taking kind of a like deeply thought out but also pragmatic approach where it first decomposes the problem into primitives, which it kind of already had because of the previous static analysis work. And I also pointed it to, um, my resource, my knowledge base, um, like the project vault that I use for agents to write up on what they did has a significant, uh, uh, m-map of concepts, uh, uh, around the widget DSL and the JavaScript APIs I've been building on. Um, so it had like a significant amount of material to, uh, decide to do, to do good, good work. But, but still I... None of that... I-it's all very messy. It, it mixes a lot of like very quality suggestions. I don't really know what it looked at, uh, but the design it came out with has a significant amount of patterns that on their own are certainly things that I, that you can, uh, uh, have seen before. But the way they were, the way they were strung together and the way the, uh, they are formalized, the way they're all integrated is, I would say, almost kind of novel. I've never really seen a code base which is that systematically abstracted out and cleanly woven together. Like, there's a lot of like little patterns in there that are really interesting, um, that now that I finally am looking at a document in more detail, I was pretty impressed with. And, uh, I have a whole bunch of screenshots which I could describe further. Um, and you can see that it never abandons this like idea of primitives being secure, of not exposing any credentials to the JavaScript, not allowing the JavaScript to do anything that's not deterministic and not double-checked and fingerprinted and audited. And, um, this is really kind of impressive. And what I did, because it is a big project, it is a big code base, I wanted to know, is it able to abstract away from the code base and really focus in on the abstraction patterns and like take a step back and say, you know, part of this work that I did is separate from IDP and is about language design. And, uh, so I asked ChatGPT Pro, which, which is really kind of fantastic to, to write a textbook about this JavaScript work that was done and, um, and to, to, to determine which contracts were, were introduced and, and what they do and how like deterministic callback registrations works and like serialized continuations. All of these patterns that are certainly in the literature, are certainly in some code bases, and are often also just like unnamed techniques. Um, like serialized continuation is basically just putting a state machine field into a database, for example, right? Um, but I wanted to see, and it, it did-- It created a really impressive textbook. I think it was... A, it was pretty long, but despite it pretty-- being pretty long, I found it very concise in the ideas that it showed and how it introduced them. So I have screenshots of that as well, um, which, which, uh, I found really like a, a fantastic textbook in a way that I've never, never seen before. Um, and the prompt for it was pretty simple. It was really like kind of, you know, build a textbook about these abstractions. Um, so I, I also have ba-basically ended up this morning doing a bunch of these researches and ended up with about 200 pages of textbook-style material, which is really interesting to read. Like, usually I get tired and I'm like, "Yeah, this is kind of getting slop, slop-like." Like I'm not feeling kind of this narrative going forward. Here, pretty much every section, and they are concise. They're not like a lot of blah, blah, blah. They're, they're, they're like, uh... It's just a lot of materials 'cause it's a, it's a big project. Uh, s- is very, very interesting. Like, none of these things are, uh, um, seem extraordinarily over-engineered. It certainly is a lot, uh, and I've... I already would have trusted 5.5 to do this much of a lot, but I wouldn't have trusted it to design so much and it being like consistent in itself. Here, everything's like very consistent, and it has survived many, many, many, uh, iterations 'cause it is an IDP. I've added all the static analysis. I've added all kinds of additional features as I went along, pushing it into production. And then I add this whole scripting layer on top, um, which it did very, very systematically. So to me, the, the interesting thing here is, uh, is it seems to... So it, it seems to be able to do math, uh, to do math. What did I say? To do research. And, um, I'm just gonna read what I put on, on WhatsApp this morning. Um, so I said, uh, "Sorry for all the abstract math rambling 'cause currently I'm r- I'm learning category theory. Um, I think my technique of asking for a language or a JS API or protocol up front has the effect of laying bare DNA machinery, both from a domain perspective, but also from a computational perspective." Um, so here I'm, I'm gonna explain a little bit. One of my prompting techniques is always to ask the LLM to create an, a language, um, which can be a YAML DSL, so something that's more declarative, or, uh, if I do want to have computational primitives like for loops and, and, uh, um, that kind of control flow stuff, um, or variable bindings, that, that, that kind of things, then I use a JavaScript API. And I've, I've spent A lot of time. I've been doing this for like three, four years now, and I've built like thousands of languages, I think, um, or generated them. So I've, I've picked up on a, on a bunch of patterns that I never really thought of giving names to, but now I'm getting there. Um, and when I say the, the inner machinery, I mean the inner machinery of the LLM, 'cause I do think LLMs are kind of abstraction machines. They're able to match patterns in the concrete. So when they look at a lot of source code, they're able to recognize certain patterns, move up an abstraction step because they have learned a certain abstraction matching patterns, and then able to manipulate that or like put it into coordination with other things, and then go back into the concrete, which is kind of the inverse of the pattern matching. And the domain perspective is that there are abstractions on the domain. So if I'm doing like a logistics application, there are going to be abstractions on the lo- logistics side, like an order and like a shipment and a refund and, uh, you know, dates like, like, uh, uh, um, paths, like plans. All of these things are kind of in the logistics domain, make a lot of sense for people who are domain experts as well. And then on the other side you have like the computational domain, the computational side of things, which is how is the computer going to do it and how... A- and usually the complexity is when these two worlds meet, right? Which is, um, you do design something in the domain perspective, and a lot of domains have like computational algorithmic aspects to it. Like cooking is very computational, for example, right? Um, but then a lot of things need detail, um, on the computational side of just like which variables are we going to use and just like purely, purely programmatic things. And, um, APIs are basically ways to bridge these two things, and I think function well for humans, function well for LLMs. And, um, being able to shift this boundary has always been, I think, a good way to reduce complexity. So, so if you look at structure and interpretation of computer programming, in the very first few pages it says if, if you have a problem and you're able to design a language to describe that problem and to describe solutions to that problem, then suddenly you don't have a problem anymore. You have like a solution, right? And so this is the approach that I take, is I let the LLM figure out kind of which abstractions are on which side of the whole thing, and then create an L- an API that combines the both, like bridges both. And now suddenly I have a very clean API, uh, which from the domain side has very clear semantics, and then on the computational side is reasonably easy to implement usually, and like kind of, uh, um, allows us when we're building the application to prompt something that goes against the API and that matches the whole thing pretty easily. Like if you-- otherwise prompts have to make the LLM bridge these huge gaps. Like if I say, you know, add a refund, add a refund workflow, it is necessary for it to bridge it all the way down to the CSS for the page that has like the refund UI now, right? And, and so it, it is extremely token intensive, a- a- and depending on the size of the model, might just not be in its capabilities to do all of these steps. Um, however, if you design an API that's just like, you know, called design workflow, and it has a little language to create forms, for example, then suddenly create a refund f- workflow is, is very easy. It's going to be like 20 lines of code with a little bit of UI widgets thrown in there. So anyway, this was an excursion about my, um, my technique of asking for language upfront. Uh, so going back to the WhatsApp stuff. Um, so, so I, I'm really using the word of computational language, uh, as well on purpose and not saying programming because I think programming is just like a distracting word. We, we really are, uh, um, trying to... Programming languages are just ways of describing how a machine can do computation. And there's, there's many of those, and they're ultimately not all that interesting. Um, but they're very distracting because we do think of programming as an activity more so than just what we're doing, which is controlling computation. Um, so, um, the second part then it, it echoes a little bit what I said before in, in WhatsApp. Uh, so what I said in WhatsApp is, so for example, this is the design of my IDP scripting layer by Saul, and this is the first screenshot that I was showing it. It has a ton of really advanced interpreter language semantics work in it, which I think is partly quite novel. Certainly nothing I've really seen in such a condensed version. It was not easy to get to this level of design. Of course, Saul did all the work at the end, but there is real magic here. I've also gotten used to a lot of these patterns over time. So by here I mean language design patterns that might maybe not even be described anywhere, but that I at that point have chunked and don't even think of, 'cause I've built thousands of these languages and I've recognized what works better and worse over time. Uh, I haven't done anything scientific. I think my approach is pretty naive so far. Um, but with Five Six being able to do research, I think we can do a language optimization loop that is not going to devolve pretty quickly. I think Five Six being able to keep research on track is really one of the, of the novel things. Uh, it, it really is doing some kind of PhD level stuff, which is breaking my brain. I don't think it's postdoc level yet [chuckles], but it, it definitely is able to do this like kind of Research that isn't entirely groundbreaking maybe. I mean, some PhDs definitely are, obviously. Um, but it is able to do this, like, pretty systematic, fundamental kind of, uh, loop that stays on track. Um, and the chain of prompts roughly, but without much more effort from my part, besides pointing it to other projects of mine was, uh, first, build an IDP. Second, add static analysis and model checking. Three, add scripting. I have no idea how IDPs work really. It's the first time I also look at the IDP itself in any kind of detail. Um, so what's interesting, um, I've long ago gotten over the vertical feeling of, "Oh God, what is even possible now?" And I can already see some cracks in the five-six shell, um, but this is the closest I've come to this vertical feeling in over a year. Um, in a way, dealing with discovering the unlocks of new models is kind of routine almost now, right? Like every t- every two months, something new comes out that, that is pretty significant. Um, and the first step, the step zero is like, "Whoa, that's, that's not bad at all," which the first demo effect. And then one, I don't really see the difference between the new model and the old model because I don't really know how to fit it into the current workflow yet. Since GPT 5, kind of everything I prompt, uh, it's been really hard for me to prompt things that don't work, and I'm really happy when I do. A- and I wrote an article about that. And then two, it's, "Oh, fuck." This means I stumble upon stuff that uncovers some of the new capabilities or, or, or on the other hand, shows that things are mostly incremental, which doesn't mean that incremental model improvement doesn't have drastic effects, right? Like I think GPT 5.4 was a real unlock because suddenly everything worked. I didn't have to like dig in, you know, every hour or so, like be careful because that amount of work would like take... would like limit what I could do in a day. And then suddenly I could just like let five things run and be pretty sure that they would be good at the end of the day versus launching five things and then basically spending the next five hours fixing one after the other, um, in minute ways. Um, then the third step in when a new model comes out is kind of like routine of discovering new models is like, "Oh, I see the cracks now." I'm st- um, which means that I'm starting to develop some like concrete prompting techniques and, and building tools to fill these cracks. Um, and I kind of know that the next model is probably going to c- to fill these cracks on its own, right? Like that it's already getting trained on exactly that. And the, the fourth step is then just like getting really proficient with the new model and, and like basically being able to prompt it blind, uh, prompt it with like my brutalist prompt. So moving on to the WhatsApp. Um, the next thing... Well, I think maybe, uh, then I show my second screenshot, which, which kind of shows the design of this IDP language, uh, again. And, um, here it has like a lot of notes on the screenshot. Uh, but what I wrote on WhatsApp is this is also saw on a similarly complex domain, um, which is reproducible RAG experiments. So this is actually a second project. Um, a- and here I can see that I kind of prompted it wrong and that, you know, that I could have caught it earlier. Um, but also this work, uh... Actually, I don't know. I think, I think we should stop here. Um, I think that was enough already. Um, and, uh... Well, and, a- and then like the mental part of all of this is I've never seen a model being like so systematic yet tasteful. Like it has a lot of taste. Everything that comes out, I'm like kind of this is really clean. It's not too much. It's not, um... It covers a lot of ground, which in the IDP case, I'm not totally against it covering a lot of security ground. Uh, but contrary to before, where you could kind of tell it's like kind of being like an architecture astronaut, here it is, it is very elegant, I, I, I find. Um, and I said it's, it's not afraid to seriously modify the core of the code to make it work properly instead of like kind of weaseling itself to a successful checklist, right? Um, so I'm not necessarily expecting anybody to understand the examples from the IDP here. That really demands this kind of like research-y work. The textbook that I've written... That I've had it right and, and maybe extracting, you know, its library. But I, I think at this point I'm also like ready to really use the pros that five-five, uh, that five-six generates to, to kind of create good documentation. It's been pretty good at like self-optimizing documentation as well. And the fact that five-six is like, "Oh bro, we're gonna first build a serious abstract fundamental layer, and then we'll rebase the existing app on top of it," that, that's kind of new and especially in, in terms of how aggressive it is, right? Um, a- and, uh... All right. They-- I, I think that's enough, and this is, uh, enough for turning this into an article.
>
>
> —-
>
> Now create a set of potential Substack posts for my gogogolems.substack.com

<details><summary>💭 Thinking</summary>

**Considering content creation**

The user asked for potential Substack posts, but didn’t provide a specific article or content. I’ll explore the referenced site to better match its tone and style before suggesting ideas.

**Considered content creation**

</details>

```json
{"search_query":[{"q":"site:gogogolems.substack.com gogogolems Substack"},{"q":"site:gogogolems.substack.com \"language\" \"LLM\""},{"q":"site:gogogolems.substack.com \"GPT-5\""},{"q":"site:gogogolems.substack.com \"programming\""}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Browsed websites and searched for posts, articles, and tools**

**Creating post concepts**

I’m focusing on potential post ideas for the user’s Substack. From their provided content, I’ll suggest a series that matches their voice: conversational, theoretical, with examples. I'll cite the previous works where needed.

**Created post concepts**

**Planning post structure**

I’ll create 8-12 post ideas in clusters, focusing on model capabilities, language-first prompting, technical case studies, and broader implications. I'll suggest titles, hooks, and structure while keeping references to the model consistent.

**Planned post structure**

**Planning post narratives**

I’m organizing a series of posts, starting with flagship ideas, like a model refusing a scripting request to preserve security. I'll outline the themes: design, research autonomy, abstraction machines, and technical deep dives on capabilities and case studies.

**Planned post narratives**

</details>

# Proposed Substack series: **Abstraction Machines**

The material contains several distinct stories that should not be compressed into one oversized article:

1. A personal report on a model capability jump.
2. A concrete identity-provider case study.
3. A general method: asking for a language before asking for an application.
4. A theory of LLMs as abstraction and synthesis machines.
5. A technical series on interpreter design, continuations, capabilities, and verification.
6. A forward-looking proposal for language-optimization loops.

A useful umbrella subtitle would be:

> **What changes when models can research systems, redesign their foundations, and teach us the abstractions they discovered?**

Below are twelve viable posts. The first six form the strongest initial sequence.

---

## 1. The First Model I Trust to Do Research Without Me

**Alternative titles**

- **GPT-5 Let Me Stop Babysitting Refactors. 5.6 Let Me Stop Babysitting Research.**
- **The Research Step Function**
- **From Unsupervised Refactoring to Unsupervised Research**

**Core thesis**

The meaningful model jump is not higher benchmark performance. It is a change in the unit of work that can be delegated.

GPT-5 crossed a threshold where you could hand off a substantial refactor without continuously steering it. Your experience with 5.6 suggests a similar threshold for research: it can collect material, identify the important abstractions, reconcile them with a real codebase, and produce a coherent technical synthesis.

**Opening**

> GPT-5 was the first model I trusted with refactors large enough that I could stop watching.  
>   
> 5.6 is the first model I have trusted with research large enough that I could stop steering every page.

**Structure**

### The first threshold: refactoring without supervision

Describe the shift from launching several agents and spending the rest of the day fixing them to launching several tasks with reasonable confidence that they will converge.

The important distinction is not that the model writes better functions. It is that it can preserve a larger set of invariants across a longer transformation.

### The second threshold: research without collage

Contrast previous research outputs with the new experience.

Earlier systems often produced something recognizably assembled from search results:

- one paper summarized correctly;
- another concept pasted beside it;
- a plausible but unstable connection between them;
- rapid degradation once the subject became mathematically or architecturally dense.

The new behavior is closer to synthesis:

- identifying a small number of governing ideas;
- applying them to the codebase;
- naming recurring patterns;
- showing how the patterns constrain one another;
- arranging them into a teachable narrative.

### The IDP experiment

Explain the intentionally extreme setup:

- build an identity provider in a domain you did not know deeply;
- add static analysis and model checking;
- push it toward production;
- add a scripting layer that could easily compromise the previous guarantees;
- ask the model to extract the interpreter and language-design ideas afterward.

### What “teaching” means here

The model did not merely describe files. It reconstructed a conceptual progression:

```text
closed outcomes
    -> native effect plans
    -> invocation capabilities
    -> explicit continuations
    -> deterministic callback registration
    -> generation-pinned resumption
    -> fail-stop runtime leasing
```

That progression is useful to a reader who has never seen the code.

### Where the claim stops

Keep this grounded:

- this is a report about a workflow threshold, not a benchmark;
- the model still has cracks;
- the research remains easier to trust when it produces inspectable code, tests, diagrams, manifests, and source-linked claims;
- “nearly unsupervised” does not mean “unaccountable.”

**Suggested image**

Use the first annotated screenshot as the central visual. Crop around the continuation requirements and package plan.

**Suggested caption**

> The moment I realized the scripting design contained a reusable interpreter architecture, not merely a set of JavaScript callbacks.

**Estimated length:** 2,500–3,500 words.

---

## 2. I Asked an AI to Make My Identity Provider Scriptable. It Refused.

**Alternative titles**

- **The Best Thing the Model Did Was Reject My Prompt**
- **How Not to Add JavaScript to an Identity Provider**
- **A Scriptable Identity Provider Is Probably the Wrong Abstraction**

**Core thesis**

The impressive result was not that the model implemented scripting. It recognized that the naive feature request would dissolve the system’s security model and replaced it with a constrained language architecture.

This is the most differentiated and concrete post in the set.

**Opening**

> I asked the model to make my identity provider scriptable. It refused.  
>   
> Not literally. It implemented the feature. But it rejected the premise that JavaScript should be allowed to become a second identity provider inside the first one.

**Structure**

### The innocent feature request

You wanted:

- virtual users;
- invitation logic;
- project-specific signup policies;
- provider customization;
- reusable Lego-like composition;
- behavior that did not have to be hard-coded into the IDP.

The obvious solution was a JavaScript host object:

```javascript
ctx.store
ctx.sql
ctx.fetch
ctx.oauth
ctx.tokens
ctx.signingKey
```

The design explicitly refused all of this.

### Why scripting could undo the previous work

The system had already been refactored around:

- assertions;
- invariants;
- protocol transitions;
- model checking;
- explicit evidence;
- typed state;
- transaction boundaries.

Exposing credentials, stores, tokens, HTTP, or signing material to JavaScript would move those invariants into arbitrary script behavior.

The scripting layer would become an alternate implementation of the IDP.

### The replacement architecture

JavaScript receives only narrow, versioned capabilities and returns members of a closed outcome algebra.

```text
JavaScript may:
  choose a policy branch
  request a host-defined lookup
  select a host-defined presentation
  construct an inert commit proposal
  name a legal continuation

JavaScript may not:
  open a database transaction
  consume a credential
  mint a token
  handle signing keys
  write an HTTP response
  persist a Goja object
```

The model did not merely add restrictions after designing a broad API. It made restrictions the organizing principle.

### Explicit continuations

Explain the key browser-boundary rule in accessible terms:

- an ordinary Promise may remain alive during one HTTP request;
- a browser interaction cannot;
- the system stores a first-order continuation record;
- the record names the next handler and carries only bounded, serializable, non-secret data;
- the next request starts a fresh invocation.

A serialized continuation is “just a state-machine field in a database” at the mechanical level. The interesting work is specifying everything that cannot cross that field.

### Deterministic callback registration

A callback ID in persisted state must resolve to the same intended code in every runtime generation.

The system therefore checks:

- source identity;
- canonical program identity;
- callback-set identity;
- schema identity;
- exact generation identity at resume time.

This is not merely module loading. It is linking executable closures to durable semantic names.

### Why this felt tasteful

Define taste behaviorally:

- it rejected ambient authority;
- it did not invent a general framework where a closed mechanism sufficed;
- it introduced abstractions only where they protected an invariant;
- it paired each abstraction with a validation pass and an implementation phase;
- it preserved the native protocol kernel;
- it still delivered the requested flexibility.

**Suggested images**

Use the first and third screenshots.

The third screenshot is particularly valuable because it shows that the architecture was tied to concrete phases and gates:

- explicit continuation domain;
- provider-owned presentation;
- signup vertical slice;
- restart and browser tests.

**Suggested caption**

> What convinced me this was not architecture astronautics: each abstraction had an implementation phase, a gate, and an end-to-end test.

**Estimated length:** 2,000–3,000 words.

---

## 3. Ask for a Language First

**Alternative titles**

- **My Highest-Leverage Prompting Technique Is to Ask for a Language**
- **Stop Asking the Model to Build the App**
- **Before You Ask for the Feature, Ask for the Language That Describes It**

**Core thesis**

Many apparently difficult application tasks become small once the right boundary language exists.

The model is being asked to bridge too many semantic layers when a prompt says only “add refunds,” “add invitations,” or “add a research experiment.” A language or API moves part of that bridge into the software itself.

**Opening**

> When I ask a model to add a refund workflow, I may be asking it to bridge the entire stack in one inference: domain policy, data structures, state transitions, validation, persistence, forms, rendering, and CSS.  
>   
> When I ask it to design the language of refund workflows first, most of that bridge becomes part of the project.

**Structure**

### Domain abstractions and computational abstractions

On the domain side:

```text
order
shipment
refund
approval
invitation
challenge
credential
experiment
retriever
evaluation
```

On the computational side:

```text
values
bindings
branches
loops
effects
state transitions
transactions
serialization
concurrency
```

An API or language is the negotiated boundary between them.

### Why direct feature prompts become token-intensive

Without a language, the model repeatedly reconstructs the bridge:

```text
“add a refund”
  -> infer the domain model
  -> find the state machine
  -> identify database operations
  -> construct validation
  -> add the form
  -> wire the route
  -> add rendering
  -> style the page
  -> write tests
```

With a language:

```javascript
workflow("refund", ({ form, order, effects }) => {
  const request = form(RefundRequest);
  return effects.refund(order.id, request.amount);
});
```

The domain operation becomes compact because the implementation already understands the computational semantics.

### YAML DSL versus JavaScript API

Use YAML when the problem is mostly declarative:

- configuration;
- finite manifests;
- schemas;
- static graphs;
- policy tables.

Use JavaScript when the problem requires:

- lexical bindings;
- reusable functions;
- branching;
- iteration;
- composition;
- asynchronous native operations.

The key is not to “use JavaScript everywhere.” It is to expose only the computational primitives the domain requires.

### Languages as complexity compression

A good language performs several kinds of compression simultaneously:

1. **Conceptual compression** — a domain idea gets one stable name.
2. **Implementation compression** — repeated infrastructure moves behind an operator.
3. **Prompt compression** — future model requests become much smaller.
4. **Verification compression** — many generated programs share one trusted implementation.
5. **Documentation compression** — examples teach both the user and the model.

### Why languages expose the model’s reasoning

Asking for an application permits the model to hide conceptual confusion inside implementation details.

Asking for a language forces decisions about:

- what the nouns are;
- what the operations are;
- where authority lives;
- which state transitions exist;
- which values persist;
- what is deterministic;
- what is an error;
- what must remain native.

This is why the technique appears to “lay bare the DNA” of both the domain and the machine.

### The resulting development loop

```text
ask for a language
    -> implement a small interpreter
    -> express real examples
    -> find awkward constructions
    -> research alternative abstractions
    -> revise the language
    -> regenerate applications and tests
```

**Suggested image**

Use the second annotated screenshot. It shows the same language-first instinct applied to a different domain: reproducible RAG experiments.

**Suggested caption**

> The same move in another domain: turn a pile of research infrastructure into a small operator language with explicit inputs, capabilities, artifacts, and reproducibility rules.

**Estimated length:** 2,500–3,500 words.

---

## 4. LLMs Are Abstraction Machines

**Alternative titles**

- **Pattern Matching Is Not the Interesting Part**
- **From Concrete Code to Abstract Machinery and Back**
- **What I Mean When I Call an LLM an Abstraction Machine**

**Core thesis**

A useful mental model is not that an LLM merely imitates code. It recognizes structures in concrete artifacts, moves to a learned abstraction, coordinates that abstraction with others, and then lowers the result back into a new concrete implementation.

The article should present this as a working hypothesis, not a settled theory of cognition.

**Opening**

> “Pattern matching” is technically true and descriptively useless. The interesting question is what kind of patterns a model can recognize, at what level of abstraction, and whether it can return from that abstraction to working code without losing the constraints it started with.

**Structure**

### The four movements

```text
concrete artifacts
    -> abstraction recognition
    -> abstraction coordination
    -> concrete reconstruction
```

In the IDP:

```text
routes, database calls, handlers, forms
    -> protocol transitions and evidence
    -> capability systems, state machines, effect plans
    -> new packages, schemas, interpreters, and tests
```

### Moving upward is not enough

Many models can propose abstractions. The difficult part is descending again:

- assigning packages;
- choosing data structures;
- preserving compatibility;
- writing migration paths;
- adding tests;
- respecting the existing codebase;
- fixing the consequences of the abstraction.

This is where architectural “slop” usually appears.

### Synthesis as coordination

The interesting design was not any individual technique:

- state machines;
- capabilities;
- schema validation;
- continuation records;
- worker pools;
- canonical hashes.

The interesting part was their coordination.

Each technique solved one failure mode and reinforced the others.

### Naming unnamed techniques

A model can also function as a conceptual compiler:

```text
implementation pattern
    -> named construct
    -> relation to literature
    -> reusable explanation
    -> transferable design pattern
```

This is what turned the codebase into textbook material.

### Why language design is a good probe

A language forces abstractions to become operational.

It is not enough to say “use capabilities.” One must define:

- what a capability value is;
- how it is obtained;
- how long it lives;
- whether it can be stored;
- what arguments it accepts;
- what results it produces;
- how it is revoked;
- what happens at a continuation boundary.

Language design reveals whether the abstraction is actually coherent.

**Estimated length:** 1,800–2,500 words.

---

## 5. The Codebase I Never Read

**Alternative titles**

- **Can You Own Software You Have Not Read?**
- **I Pushed a Model-Built Identity Provider Toward Production**
- **What Does Understanding a Codebase Mean After Agents?**

**Core thesis**

Model-generated software forces a distinction between reading every line and possessing a reliable model of the system.

The article should neither celebrate blind trust nor retreat to “humans must read everything.” It should investigate the artifacts that can substitute for line-by-line familiarity.

**Opening**

> I built an identity provider that I did not understand in the traditional sense. I had not read most of the code. I did not know the domain well when I started. And yet I could push the system through increasingly invasive changes without it immediately collapsing into incoherence.

**Structure**

### The experiment

You intentionally “token-maxed” the project:

- selected a difficult domain;
- permitted the model to build beyond your immediate comprehension;
- added formal and static-analysis requirements;
- introduced production pressure;
- later added a scripting subsystem.

The point was partly to discover the edge of model-owned complexity.

### The difference between familiarity and control

Traditional familiarity means:

- remembering important files;
- knowing historical accidents;
- recognizing conventions by feel;
- being able to debug locally.

System control may instead come from:

- explicit invariants;
- closed state-transition models;
- conformance suites;
- generated manifests;
- architectural boundaries;
- source-linked design documents;
- operational traces;
- semantic diffs;
- reproducible builds.

These are not identical forms of understanding.

### Design documents as control surfaces

A strong design document is not merely retrospective documentation. It tells future agents:

- which abstractions are intentional;
- where authority belongs;
- which shortcuts are forbidden;
- what every phase must preserve;
- how completion is tested.

It becomes part of the execution environment for future model work.

### The uncomfortable question

At what point are you supervising software rather than authoring it?

A useful answer may be:

> Ownership moves from remembering implementation details toward controlling the language, invariants, tests, and evidence by which implementation changes are accepted.

### Where this can fail

Address the difficult cases:

- a test suite can encode the wrong specification;
- generated documentation can be internally coherent but false;
- security properties can fail between modeled boundaries;
- long dependency chains remain opaque;
- production incidents require operational understanding;
- the model may optimize for passing stated gates while missing unstated intent.

The post becomes stronger by treating this as an unresolved engineering discipline.

**Estimated length:** 2,000–2,800 words.

---

## 6. From Codebase to Textbook

**Alternative titles**

- **The Model Built the System, Then Taught Me Its Design**
- **I Asked for Documentation and Got a Programming-Languages Textbook**
- **Documentation as Reverse Compilation**

**Core thesis**

A model’s most valuable post-implementation capability may be reconstructing the conceptual architecture of a system and presenting it as a sequence a human—or another model—can learn.

**Opening**

> I had a large codebase I had barely read and a scripting subsystem full of techniques I recognized only partially. I asked the model to extract the interesting interpreter ideas. By the end of the morning, I had roughly two hundred pages of textbook-style material that was more readable than the source and more precise than a conventional architecture overview.

**Structure**

### Documentation normally follows the directory tree

Most generated documentation says:

```text
this package contains X
this struct has fields Y
this function calls Z
```

That is useful reference material, but it does not teach the system.

### The textbook followed the dependency of ideas

The resulting explanation instead asked:

1. Why is scripting an identity provider dangerous?
2. Which authority must remain native?
3. How can JavaScript express policy without possessing authority?
4. How are callbacks linked to durable state?
5. What survives a browser boundary?
6. How is asynchronous work bounded?
7. When is a runtime safe to reuse?
8. How does hot reload preserve old continuations?

That ordering is pedagogical rather than structural.

### Reverse compilation

A useful metaphor:

```text
source code
  -> implementation structures
  -> architectural invariants
  -> named programming-language concepts
  -> explanatory narrative
```

The model reverse-compiled the implementation into a conceptual language.

### Documentation for humans and models

A good text serves several audiences:

- a new human maintainer;
- a reviewer;
- an operator;
- a future coding agent;
- a model asked to extend the architecture;
- a model asked to challenge the design.

This changes the economics of writing extensive internal textbooks.

### The danger of beautiful explanations

Coherence can be persuasive even when it is wrong.

A serious documentation pipeline should preserve:

- links to exact source;
- statements of what was inferred;
- distinctions between implemented and proposed behavior;
- references to tests;
- unresolved concerns;
- version and commit identity.

**Suggested image**

The first screenshot works here as well. The handwritten annotations visually show the human recognition step: noticing that apparently ordinary package planning contains interpreter machinery.

**Estimated length:** 1,800–2,500 words.

---

## 7. Serialized Continuations Are Just a Database Field—Until You Care About Invariants

**Alternative titles**

- **The Surprisingly Deep Design of a Browser Continuation**
- **How to Suspend JavaScript Without Serializing JavaScript**
- **Why My IDP Never Persists a Promise**

**Core thesis**

The low-level mechanism is simple: store the next state and resume later. The design becomes interesting when persistence, security, code generations, secret flow, replay, and browser interaction are treated rigorously.

This should be the first deeply technical article in the series.

**Opening**

> A serialized continuation can sound like programming-languages mysticism. In this system it is, at first approximation, a state-machine field in a database.  
>   
> The hard part is specifying everything else that must be true before that field is safe to trust.

**Structure**

### The naive implementation

```json
{
  "next": "signup.verify_email",
  "data": {
    "email": "alice@example.com"
  }
}
```

This looks sufficient until the questions begin.

### Which code does `signup.verify_email` identify?

A string must be bound to:

- one workflow;
- one callback registry;
- one program generation;
- one compatible input schema;
- one expected browser event;
- one permitted predecessor edge.

### Which data may survive?

Allowed:

- bounded public carry;
- stable native references;
- request-binding information;
- revision and expiry;
- evidence identifiers.

Forbidden:

- functions;
- Goja objects;
- Promises;
- credentials;
- raw challenge codes;
- HTTP objects;
- database transactions;
- capability functions.

### What prevents replay?

Explain:

- opaque handles;
- keyed hashes;
- expiry;
- revisions;
- atomic consume;
- one-time evidence;
- browser binding;
- terminal status.

### What happens after hot reload?

The continuation must not silently resume under code with different meaning.

Possible policies:

- retain the old generation;
- run an explicit migration;
- reject incompatibility safely;
- revoke the continuation.

### Why not serialize the Goja stack?

A VM snapshot would capture too much:

- engine-specific program counters;
- object identities;
- lexical environments;
- native references;
- potentially secret-bearing values;
- pending microtasks;
- runtime implementation details.

The explicit continuation is smaller precisely because it records semantic state rather than machine state.

### The compiler opportunity

A future compiler could let the author write:

```javascript
const form = await durable.present(SignupForm);
const proof = await durable.emailCode(form.email);
```

while compiling it into explicit named handlers and typed continuation frames.

This provides direct style without making VM state durable.

**Estimated length:** 3,000–4,500 words.

---

## 8. Taste Is the New Frontier

**Alternative titles**

- **Systematic, but Not an Architecture Astronaut**
- **What Model Taste Looks Like in Software Design**
- **The Difference Between More Architecture and Better Architecture**

**Core thesis**

“Taste” should not mean that the generated code resembles the author’s preferences. It means the model makes coherent trade-offs, refuses bad premises, introduces structure at the right level, and is willing to rebuild foundations rather than decorate a failing design.

**Opening**

> Models have been capable of generating elaborate architecture for a while. The problem was that they often seemed unable to tell whether the architecture was earning its keep. What surprised me about this work was not its complexity. It was its restraint.

**Define taste through observable behaviors**

### It rejected the naive abstraction

Instead of exposing the store and protocol internals to JavaScript, it narrowed the scripting problem.

### It was willing to modify the core

The model did not preserve a poor internal structure merely to minimize the diff.

It introduced the objects required for:

- tracing;
- assertions;
- model checking;
- typed outcomes;
- capability boundaries;
- explicit continuations.

### It made the abstractions pay rent

Every major abstraction had:

- a threat or failure mode;
- a validation rule;
- an implementation package;
- a test gate;
- a production integration point.

### It remained coherent across iterations

The architecture survived:

- the original IDP;
- formal-analysis additions;
- production hardening;
- scripting;
- continuation storage;
- provider integration.

### It did not confuse coverage with quality

The system covers substantial security ground, but the design does not appear to introduce arbitrary abstraction merely because more abstraction sounds sophisticated.

### Taste remains contextual

The same design could be excessive for:

- a static marketing site;
- a disposable internal script;
- a prototype with no durable state.

The identity-provider context justifies a larger assurance envelope.

**Suggested image**

Use the third screenshot, which shows the phased implementation plan and concrete gates.

**Estimated length:** 1,500–2,200 words.

---

## 9. The Five Stages of Learning a New Frontier Model

**Alternative titles**

- **Every New Model Arrives in the Same Five Acts**
- **From Demo Effect to Prompting Blind**
- **How I Actually Learn What a New Model Changes**

**Core thesis**

Your model-adoption cycle is itself a useful post. It gives readers a vocabulary for distinguishing novelty from actual workflow change.

**The five stages**

### Stage 0: “That is not bad at all”

The first-demo effect. A conspicuously good answer establishes possibility but not yet repeatability.

### Stage 1: “I cannot tell the difference”

The new capability has not been integrated into the existing workflow. Old prompting habits underuse it.

### Stage 2: “Oh, fuck”

A task unexpectedly reveals that the workable unit of delegation has changed.

This is the real unlock.

Examples:

- GPT-5: substantial refactoring without babysitting.
- 5.4: multiple parallel tasks without spending the day repairing each one.
- 5.6: sustained research and synthesis without constant steering.

### Stage 3: “I see the cracks”

Repeated use reveals the failure modes.

This is where:

- prompting techniques emerge;
- scaffolding gets built;
- evaluation tasks become concrete;
- the next generation’s training target becomes visible.

### Stage 4: Fluency

You can prompt the model “blind” because you have internalized:

- what context it needs;
- when to ask for research;
- when to ask for a language;
- how much autonomy to grant;
- where to require checkpoints;
- which outputs are reliable enough to use directly.

### The larger point

New-model adoption is not primarily about collecting tricks. It is about discovering the new stable unit of delegation.

**Estimated length:** 1,200–1,800 words.

This would work well as a shorter, highly shareable post between technical essays.

---

## 10. Toward a Language Optimization Loop

**Alternative titles**

- **What Happens When the Model Can Research the Language It Is Designing?**
- **Compilers, Agents, and the Language Optimization Loop**
- **The Next Agent Workflow Is Not Code Generation. It Is Language Evolution.**

**Core thesis**

Your language-first method has so far been largely intuitive. Better research synthesis makes it possible to turn it into a systematic optimization loop.

**Opening**

> I have generated thousands of small languages over the last several years. Most were not designed through a scientific process. I tried an API, noticed where it felt awkward, asked the model to revise it, and gradually accumulated a set of patterns I no longer consciously name.  
>   
> A model that can conduct sustained programming-languages research changes what this loop can become.

**Structure**

### The current informal loop

```text
describe the domain
    -> ask for a DSL or JS API
    -> implement examples
    -> encounter friction
    -> patch the API
    -> repeat
```

### A research-enabled loop

```text
collect representative tasks
    -> infer domain ontology
    -> propose competing languages
    -> implement small interpreters
    -> synthesize example programs
    -> measure complexity and error modes
    -> research analogous language designs
    -> revise semantics
    -> test human and model authoring
    -> promote stable constructs
```

### Possible optimization criteria

A language can be evaluated for:

- program length;
- number of concepts required;
- authority exposed;
- invalid states representable;
- quality of diagnostics;
- ease of static analysis;
- ease of model generation;
- edit locality;
- backwards compatibility;
- interpreter complexity;
- proof burden;
- performance;
- human readability.

### Model-generated language benchmarks

Create a corpus of tasks such as:

```text
add an invitation-based signup
add a refundable order cancellation
run a reproducible RAG comparison
add a two-person approval
migrate an existing durable workflow
explain why one request was denied
```

Compile or express each task in competing language designs.

Then compare:

- mistakes;
- tokens used;
- repair iterations;
- authority requested;
- size of generated implementation;
- static errors caught;
- runtime errors remaining.

### The human role

The model can optimize measurable properties, but the human still selects:

- which concepts deserve names;
- which complexity should be visible;
- which policies are non-negotiable;
- which language feels honest about the domain;
- which abstraction will remain useful after the current project.

### From Tiny-IDP to a malleable interpreter

The endpoint is not one perfect IDP scripting API. It is a compiler and interpreter substrate that projects can extend with:

- types;
- capabilities;
- effects;
- durable operations;
- verification rules;
- cost models;
- native bindings.

**Suggested image**

Use the second annotated screenshot. It demonstrates that the same package-and-language pattern is already appearing in a separate RAG experimentation system.

**Estimated length:** 2,500–3,500 words.

---

## 11. Programming Is a Distracting Word

**Alternative titles**

- **We Are Not Teaching Models to Program. We Are Designing Languages for Computation.**
- **The Problem With Calling It Programming**
- **Software Is a Collection of Computational Languages**

**Core thesis**

“Programming” overemphasizes the human activity of writing code. The more useful frame is the design of languages that describe permissible computation.

This could be a more philosophical and concise essay.

**Opening**

> “Programming” is a distracting word because it makes us think about the activity of writing instructions. The deeper activity is deciding what computations can be expressed, what they mean, and which details the author should never have to mention.

**Sections**

- Why general-purpose languages expose accidental complexity.
- How every mature framework contains smaller languages.
- Configuration files, schemas, builders, query APIs, workflow descriptions, and component trees as computational languages.
- Why models benefit disproportionately from stable domain languages.
- Why a good language can transform a difficult feature into a small description.
- The danger: every abstraction hides something, and hidden authority is worse than visible complexity.
- A language is successful when it moves complexity to a place where it can be implemented and verified once.

**Estimated length:** 1,400–2,000 words.

---

## 12. The Same Pattern in Two Domains: Identity and Reproducible RAG

**Alternative titles**

- **Why My Identity Provider and My RAG Lab Started Looking Alike**
- **From Identity Workflows to Reproducible Research Operators**
- **The Recurring Architecture of Agent-Built Systems**

**Core thesis**

The second annotated document suggests that the IDP architecture is not an isolated accident. Similar patterns appear in reproducible RAG experiments:

```text
trusted source package
canonical artifact
typed configuration
declared capabilities
fresh constrained runtime
native execution
normal domain values and evidence
```

This post should be written after documenting the RAG project in more detail.

**Potential comparison**

| Identity provider | RAG experiment system |
|---|---|
| Workflow package | Operator package |
| Callback registry | Operator registry |
| Program generation | Experiment artifact identity |
| Invocation capability | Host/provider capability |
| Continuation evidence | Evaluation evidence |
| Native commit | Native experiment execution |
| Typed outcomes | Typed result bundles |
| Generation-pinned resume | Reproducible package digest |
| Closed script runtime | Fresh constrained Goja realm |

**Central question**

Why do two very different domains converge on the same structure?

Because both need to allow experimentation while retaining native custody of the hard guarantees:

- identity security in one case;
- experimental reproducibility in the other.

The general pattern may be:

> Scripts describe bounded computation; native code owns the evidence that the computation was performed correctly.

**Suggested image**

Use the complete second screenshot as the primary image. The annotations themselves support the post’s thesis: “configurable but reproducible,” “what is a port,” “what is a host,” and which capabilities belong on which side of the boundary.

**Estimated length:** 2,500–3,500 words.

---

# Recommended initial publishing sequence

## Post 1: **I Asked an AI to Make My Identity Provider Scriptable. It Refused.**

This is the strongest opening because it has:

- a concrete story;
- a surprising reversal;
- a serious technical subject;
- visible artifacts;
- a clear lesson beyond one model release;
- enough depth to establish the quality of the series.

It demonstrates the capability before making the broader claim about 5.6.

## Post 2: **Ask for a Language First**

This extracts the reusable personal method from the case study.

The first article says: “Here is something remarkable that happened.”

The second says: “Here is the technique that created the conditions for it.”

## Post 3: **The First Model I Trust to Do Research Without Me**

Once readers have seen the evidence, the broader claim about the model step function has more weight.

## Post 4: **Serialized Continuations Are Just a Database Field—Until You Care About Invariants**

This provides the technical proof that the architectural praise is substantive rather than aesthetic.

## Post 5: **From Codebase to Textbook**

This introduces the second capability: not merely producing the design, but reverse-engineering it into an educational narrative.

## Post 6: **Toward a Language Optimization Loop**

This moves from retrospective case study to a future research program.

A coherent six-post arc is therefore:

```text
surprising case study
    -> reusable prompting method
    -> model capability thesis
    -> technical deep dive
    -> documentation and teaching
    -> future language-research loop
```

---

# Three shorter posts that can run between the major essays

These can maintain cadence without requiring a full research article.

## Taste Is the New Frontier

A 1,500-word argument defining model taste through rejection, restraint, structural coherence, and willingness to repair foundations.

## The Five Stages of Learning a New Frontier Model

A concise and shareable personal taxonomy.

## Programming Is a Distracting Word

A philosophical note connecting language design, computation, frameworks, and agent workflows.

---

# Suggested series framing

The first post could include a small editor’s note:

> This is the first in a series about a model-built identity provider, the unusual interpreter architecture that emerged inside it, and a prompting technique I have used for several years: ask for the language of the problem before asking for the solution.  
>   
> The series moves between a concrete codebase, programming-language design, model capability, and a larger question: what happens when software agents can not only implement systems, but also research, name, and teach the abstractions those systems require?

---

# Editorial principles for the series

## Keep the claims autobiographical

Prefer:

> “This is the first model I have trusted to conduct this kind of research with limited steering.”

over:

> “This is the first model capable of autonomous scientific research.”

The former is both more credible and more interesting. It identifies a real workflow threshold.

## Use the IDP as evidence, not decoration

Do not introduce ten interpreter terms before establishing the problem they solve.

The reader should first understand:

- why identity scripting is dangerous;
- why you wanted it anyway;
- why the obvious design was unacceptable.

Then introduce capabilities and continuations.

## Define “taste” operationally

Taste is otherwise too easy to dismiss. Tie it to observable choices:

- rejecting ambient authority;
- introducing a smaller language;
- altering the foundation rather than adding adapters;
- connecting every abstraction to a failure mode;
- supplying implementation phases and gates;
- preserving coherence across subsequent changes.

## Preserve the unresolved tension

The story is stronger because you have not read most of the code.

Do not hide that. Make it one of the central questions:

> What forms of evidence are sufficient to responsibly operate software whose implementation exceeds the maintainer’s line-by-line familiarity?

## Alternate narrative and technical posts

A run of six dense interpreter essays would narrow the audience. Alternate:

```text
personal observation
technical case study
general method
deep technical analysis
personal reflection
future research direction
```

---

# Strongest ready-to-use opening

For the first post:

> I asked an AI to make my identity provider scriptable. It refused.  
>   
> Not literally. It implemented the feature. But it rejected the obvious architecture. It would not expose a database, HTTP client, credential store, token service, or signing key to JavaScript. Doing so would have turned the scripting layer into a second identity provider hidden inside the first and dissolved the invariants the system had just been rebuilt to enforce.  
>   
> Instead, it designed a small language. JavaScript could select policies, invoke narrowly granted capabilities, choose host-defined presentations, and propose typed effects. Go retained custody of credentials, transactions, protocol state, browser handling, and durable evidence. Browser waits became explicit continuation records rather than suspended JavaScript heaps. Callback registration was fingerprinted across independent runtimes. A timed-out worker was destroyed rather than optimistically reused.  
>   
> None of those techniques is individually unprecedented. What surprised me was the way they were fitted together: systematically, conservatively, and without abandoning the practical feature I had asked for.  
>   
> This is an article about that design. It is also an article about the first model I have used that seems capable not merely of generating a great deal of architecture, but of exercising something uncomfortably close to architectural taste.


---

> okI do actually want a fairly expansive article about the capabilities of llm, the jump of 5.6, them being abstraction machines. It can be a bit longer, and combine 1 2 3 4 6 8 9 10, with emphasis more on 1 2 10 and using the others as illustrations and background and sections.

> Ok, I do actually want a longer article that can be a bit "rambling" (compare to my others about abstraction for example), and a combination of 1 2 3 4 6 8 9 10, with 1 2 9 10 being the most important, and the others more as like examples / side points.

<details><summary>💭 Thinking</summary>

**Considering how to write article**

The user clearly wants a longer article, possibly for a Substack post. I'll need to match their style, so I may review their prior posts for tone and content.

**Considered how to write article**

</details>

```json
{"search_query":[{"q":"site:gogogolems.substack.com abstraction gogogolems"},{"q":"site:gogogolems.substack.com \"abstraction\" \"Go Go Golems\""},{"q":"site:gogogolems.substack.com language abstraction LLM"},{"q":"site:openai.com GPT-5.6 OpenAI"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched various websites and platforms for relevant research**

**Writing article draft**

I’m planning the user’s article, keeping it informal yet coherent, using their tone. I’ll weave facts and models into sections, integrating the necessary web citations to keep it reliable.

**Wrote article draft**

**Planning article structure**

I’m thinking through how to create the article, ensuring it's informal, personal, and strays from pure technicality. I'll include my key experiences with GPT-5.6 and match the user’s tone.

**Planned article structure**

**Outlining technical patterns**

I'm focusing on how to explain the technical patterns in a simple way, making them accessible without diving too deep. I'll connect these points to language design and how abstraction shapes tasks.

**Outlined technical patterns**

</details>

```unknown
bash -lc stat /mnt/data/EC622774-75F0-4F89-AAC3-D14D0F9C2D27.jpeg /mnt/data/30800906-D7D5-43FD-9672-6238BB6A058F.jpeg /mnt/data/758620C7-4991-4C0B-9E97-36E84A43E415.jpeg
```

<details><summary>💭 Thinking</summary>

**Verified image files for article use**

</details>

I drafted this as one 7,588-word essay rather than a stitched collection of mini-posts. The five-stage model-adoption cycle provides the spine; the identity-provider case supplies the evidence; and the argument builds toward the language-optimization loop.

[Download the editable Markdown draft](sandbox:/mnt/data/abstraction-machine-gpt-5-6-substack-draft.md)

I normalized the model name to **GPT-5.6 Sol**, OpenAI’s official name for the flagship tier, while using “5.6” in the body. citeturn941125search0

---

# 5.6 and the Abstraction Machine

## On unsupervised research, architectural taste, asking for a language first, and the possibility that the next important agent loop happens above the level of code

*Editor’s note: I use “5.6” throughout for GPT-5.6 Sol.*

I asked 5.6 to make my identity provider scriptable. It more or less refused.

Not literally. It implemented the feature. But it rejected the obvious interpretation of the feature: embed JavaScript, hand it the useful internal objects, and let deployments customize the system by calling into them. Instead it designed a small constrained language in which JavaScript could make policy decisions and compose host-defined operations while Go retained custody of credentials, transactions, protocol state, browser behavior, and durable evidence.

It then implemented the interpreter machinery required to make that boundary real: explicit continuations instead of persisted Promises, invocation-scoped capabilities instead of ambient services, deterministic callback registration, canonical fingerprints, opaque secret handles, closed outcomes, native effect plans, generation-aware resumption, and fail-stop worker reuse.

This article is partly about that design. More importantly, it is about what the design made me realize about the new model: the unit of work I can delegate has moved again.

New models arrive in a fairly predictable sequence for me by now.

The zeroth stage is the demo effect: *oh, that is not bad at all*. Something works that did not work before, or it works with an ease that is conspicuous enough to make me stop for a minute. This part is exciting, but it is also the least reliable. Every model can look like a revolution if you happen to ask it exactly the right question on the first day.

The first stage is stranger: I often cannot really tell the difference between the new model and the old one. I am still using my old workflow, my old prompts, my old expectations, and my old unit of delegation. The model may be better, but I have not yet found the task shape that exposes what the improvement is *for*.

Then comes the second stage, which is the useful one: *oh, fuck*.

This is when I stumble into a task that changes the amount or kind of work I can hand over. The relevant thing is not that the model writes a nicer function or catches an extra bug. The unit of delegation changes.

GPT-5 was the first model where I felt comfortable delegating significant refactors without continuously babysitting them. Before that, I could ask for large changes, but I was usually committing myself to spending the next several hours following the model through the codebase, catching local misunderstandings, repairing half-finished migrations, and steering it back toward the original goal. GPT-5 was the first time I regularly felt I could describe a substantial structural change and let the model carry enough of the invariants through the refactor that I could review the result rather than co-pilot every intermediate edit.

There were more incremental unlocks after that. One of the meaningful ones was simply that enough things started working on the first pass that I could launch several jobs in parallel without effectively scheduling several future repair sessions for myself. That sounds like a modest improvement, but it changes the shape of a day. There is a huge difference between starting five tasks and then spending five hours fixing them one by one, and starting five tasks with a reasonable expectation that most will converge.

With 5.6, I think I have encountered another one of these changes in the unit of delegation. It is the first model I have used where research can feel almost unsupervised in the same way that refactoring started to feel almost unsupervised with GPT-5.

I do not mean that I can ask it any research question and receive truth. I do not mean that it is a replacement for subject-matter expertise, peer review, experiments, or proofs. I mean something more practical and, for my work, more consequential: I can point it at a difficult body of literature, a large unfamiliar codebase, and a broad engineering objective, and it can often keep the research loop coherent long enough to synthesize the literature into a small set of ideas, apply those ideas to the code, restructure the implementation around them, and then explain what it did in a way that teaches me the resulting system.

That entire loop is new enough that I am still trying to find words for it.

I am somewhere between stage two and stage three with 5.6 now. Stage three is when the initial vertical feeling wears off and I start seeing the cracks: which tasks make it drift, which prompts produce architecture astronautics, where the research becomes a collage, where it confuses a plausible formalism with a valid one, where it needs a tool or a constraint or an explicit intermediate artifact. That is when prompting techniques become concrete and when I start building machinery around the model. Usually, by the time I become fluent at filling those cracks, I can already imagine the next model filling several of them by itself.

But I am not there yet. I can see some cracks. I also still have a bit of the vertical feeling, which I have not had this strongly in over a year.

The best example is an identity provider I have been building.

## The identity provider I mostly did not read

An identity provider is the part of a system that decides who you are and produces the assertions the rest of the system trusts. It deals with logins, sessions, credentials, challenges, invitations, consent, tokens, protocol state, and all of the unpleasant security boundaries around those things.

I did not begin this project because I had deep expertise in identity systems. Quite the opposite. Part of the experiment was to choose a domain complicated enough that I could not quietly rely on my own background to repair the model’s work. I let the model build a great deal of the system. I pushed it toward production. I added requirements as I went. I did not read most of the code line by line.

This is obviously not a sentence I would have written approvingly about software development a few years ago.

The point was not to prove that reading code no longer matters. It was to see how far I could push a different form of ownership: one based on design documents, explicit invariants, tests, traces, model-checking artifacts, package boundaries, and repeated architectural interrogation. I wanted to know whether a model could build something too large for me to hold locally while still producing enough structure that I could develop a reliable global understanding of it.

At some point I asked it to research static analysis, model checking, formal methods, and work on OAuth protocol verification, and then to improve the system accordingly. This was deliberately broad and, in retrospect, not even an especially good prompt.

Previous models could do the research part in a recognizable way. They would find papers, summarize them, extract a few concepts, and draw plausible connections. But on difficult material you could often see the seams. The answer behaved like a stack of research notes that had been glued together. One source would be represented accurately, the next would be simplified too aggressively, and the connection between them would become increasingly decorative. If I asked it to apply the result to a real codebase, the implementation often settled for adding a layer of assertions or a few formal-looking types around the existing structure.

What surprised me here was that the model did not merely add analysis tools around the code. It refactored the codebase so that the important protocol ideas became representable in the first place.

It introduced objects and transitions that made tracing, assertions, invariants, and model checking possible. It changed the internal ontology of the project. Instead of treating the existing implementation as fixed and finding somewhere to attach the requested feature, it recognized that the request implied a different foundational representation and rebuilt toward it.

That is a very particular kind of competence. It is easy to satisfy a checklist by adding a checker at the edge. It is much harder to notice that the code does not currently contain the right objects for the checker to say anything useful, introduce those objects, move the existing application onto them, and preserve behavior while doing so.

I had seen models perform large refactors by then. I had not often seen one respond to a research prompt by changing the ontology of the application so that the researched ideas had a natural home.

Then I asked it to make the identity provider scriptable.

## I asked it to make the IDP scriptable. It more or less refused.

The request was reasonable. I wanted the identity provider to be a building block rather than one hard-coded product. I wanted to express things like virtual users, invitations, project-specific signup flows, provider behavior, policy decisions, and other forms of customization without modifying the Go implementation every time.

The naive version of this request is straightforward: embed JavaScript, give it a context object, and expose the useful parts of the application.

Something like:

```javascript
ctx.store
ctx.sql
ctx.fetch
ctx.oauth
ctx.tokens
ctx.signingKey
```

This is also a good way to undo nearly every invariant the previous work had introduced.

Once arbitrary JavaScript can open stores, issue queries, fetch network resources, inspect credentials, mint tokens, sign values, write responses, or manipulate protocol objects, the scripting layer becomes a second identity provider hidden inside the first one. Every script path now has to preserve the full security model. The native implementation may be carefully typed, traced, checked, and modeled, while the actual behavior of the deployment is determined by a dynamic program with ambient authority.

The model rejected that premise.

It did not reject the feature. It rejected the idea that “scriptable” meant “give JavaScript access to the application.” Instead it designed something closer to a small policy and workflow language implemented using JavaScript syntax.

JavaScript could receive carefully bounded inputs. It could call explicitly granted, versioned capabilities. It could select among host-defined presentation objects. It could return one member of a closed set of outcomes. It could propose an inert sequence of effects for native code to validate and commit. It could name a legal next handler at a browser boundary.

It could not own the identity provider.

The distinction sounds obvious when stated afterward, which is often the sign of a good abstraction. But it has very large consequences.

The JavaScript layer does not get credentials. It may get an opaque password handle that can be passed to a native password verifier or into a native commit operation, but it does not get a string it can log, concatenate, retain, or accidentally serialize. It does not get the raw challenge code. It may get native evidence that a challenge succeeded. It does not get an HTTP response writer. It may choose a presentation from a host-controlled registry. It does not get a SQL transaction. It may construct a typed plan that the native runtime either accepts as one named atomic operation or rejects.

There is no generic “do whatever you need” escape hatch. The language is useful because the operations are narrow enough to have stable meaning.

This is where the design started to feel less like an ordinary embedding API and more like interpreter work.

A handler is not simply a JavaScript function. It has an input schema, an output schema, a set of allowed outcomes, a set of required capabilities, a set of permitted commit effects, a timeout, a call budget, and an output budget. The callback itself exists only inside one runtime, while the serializable program stores a stable callback identifier. The runtime has to prove that the identifier resolves to the same intended callback registry across independently created workers.

The model introduced deterministic callback registration and fingerprints for the source, the canonical program, the callback set, and the schemas. This matters because a browser workflow may persist the name of a handler today and resume it tomorrow. A string such as `signup.email_verified` is not enough. The system needs to know which program generation gave that string meaning, whether the input schema is still compatible, whether the callback exists in every worker, and whether a reload changed the semantics under an already-running workflow.

The browser boundary is where the design becomes especially interesting.

An ordinary JavaScript `await` can remain alive while one HTTP request is running. A browser interaction cannot. The user may close the tab, return hours later, hit a different server instance, or resume after the process has restarted. The system cannot persist a Promise, a JavaScript closure, a Goja object graph, or an interpreter stack and pretend that this is a stable application protocol.

Instead it stores an explicit continuation record. At the simplest mechanical level, this is just a state-machine field in a database: here is the handler to invoke next, and here is the data it needs. But almost all of the interesting work lies in the constraints around that field.

The next handler must be registered in the same workflow. Its input schema must be compatible with the event that will resume it. The carried data must be serializable, bounded, and allowed to cross a durable boundary. Secrets must not leak into it. Native evidence must have been created before resumption. The continuation must expire. It must be bound to an exact program generation or have an explicit migration path. Its revision must advance atomically so that replayed requests cannot consume it twice.

The system therefore never serializes “the callback.” It serializes a first-order description of what should happen next.

This is a known programming-languages move called defunctionalization when stated abstractly: replace a function or continuation with a finite data representation and a native dispatcher. In ordinary application code it may look like nothing more exotic than storing `next_state = "verify_email"`. The interesting part is recognizing it as the same computational pattern and then rigorously defining its schema, authority, lifetime, replay behavior, and relationship to code generations.

That is the kind of synthesis I am talking about. None of the ingredients is individually unprecedented:

- state machines;
- capability-based APIs;
- schema validation;
- opaque handles;
- worker pools;
- canonical hashes;
- effect plans;
- explicit continuations;
- generation pinning;
- fail-stop cleanup.

What impressed me was how they were strung together. Each technique solved one failure mode and made the next technique possible.

The closed outcome set makes native interpretation exhaustive. The capability set prevents ambient authority. The explicit continuation prevents VM state from becoming durable. The generation fingerprint prevents old continuations from silently changing meaning. The worker owner keeps all Goja operations on one goroutine. The settlement tracker prevents a runtime with late asynchronous work from being reused. The fail-stop pool discards a worker after a timeout or uncertain interruption instead of trying to clean up a state it cannot prove safe.

This is not just “a lot of security stuff.” It is a coordinated computational model.

**[IMAGE 1 — annotated continuation requirements and package plan]**

*Suggested caption: The page where I realized the scripting proposal was actually a small interpreter architecture: explicit continuation requirements, pure program contracts, a native workflow interpreter, a constrained Goja runtime, opaque secrets, and invocation capabilities.*

## What I mean by taste

Models have been able to generate elaborate architecture for a while. Elaborate architecture is not the same thing as good architecture. In fact, one of the easiest failure modes to recognize in model-generated systems is the architecture astronaut: the model has encountered a sufficiently serious prompt and responds by producing every pattern it associates with seriousness.

This did not feel like that.

It covered a great deal of ground, especially because identity systems deserve a great deal of security attention, but the abstractions seemed to pay rent. Every major construct corresponded to a concrete failure mode. Every design phase had a gate. The plan moved from an explicit continuation store, to host-owned presentation, to a real signup vertical slice, to provider integrations and production behavior. Restartability, replay, browser flow, runtime replacement, and exact field projection were treated as things to test, not merely things to mention.

More importantly, the model was willing to seriously modify the core of the project. It did not weasel its way to a successful checklist by preserving a weak foundation and adding adapters. It first built the abstract layer it needed and then rebased the application on top of it.

That aggressiveness is part of what felt new. Previous models were often locally obedient. They optimized for making the requested change fit inside the current shape of the code, even when the current shape was the reason the change was difficult. Here the model was willing to say, in effect: the application does not yet contain the right machinery, so we will build the machinery first.

Taste is a dangerous word because it can collapse into “the model made choices I personally like.” I mean something more operational:

- it challenged the framing rather than blindly implementing it;
- it introduced a smaller language instead of exposing a larger API;
- it kept authority native and data explicit;
- it made each abstraction correspond to a validation rule and a testable boundary;
- it changed the foundation when the new requirement exposed a foundational mismatch;
- it stopped short of making the scripting language a general-purpose application runtime.

There are codebases where this would be absurdly overengineered. An identity provider is not one of them.

**[IMAGE 2 — implementation phases and gates]**

*Suggested caption: What kept the design from feeling like architecture theater was the implementation plan: each abstract mechanism had a phase, a concrete purpose, and an end-to-end gate.*

## LLMs as abstraction machines

I keep coming back to the idea that LLMs are abstraction machines.

Saying that they are pattern-matching machines is not wrong. It is just too low-resolution to be useful for the work I am doing. The interesting question is what kinds of patterns they can recognize, at what level, how they can coordinate several abstractions, and whether they can descend from the abstraction back into a working concrete system without losing the original constraints.

The movement looks roughly like this:

```text
concrete artifacts
    -> recognize a recurring structure
    -> move into an abstract representation
    -> coordinate it with other abstractions
    -> lower the result into new concrete artifacts
```

In the identity provider, the concrete artifacts were routes, forms, stores, callbacks, protocol handlers, credentials, and tests. The model moved upward into concepts such as evidence, authority, state transitions, effects, continuations, generations, and runtime ownership. It then coordinated those with programming-language patterns and lowered the result back into packages, schemas, registries, worker pools, validators, and integration tests.

Moving upward is not the difficult part by itself. Models have always been able to suggest abstractions. The difficult part is returning to the code without becoming vague.

An architecture astronaut can tell you to “use capabilities” or “model the flow as a state machine.” A useful system has to answer much less glamorous questions:

- What is the capability value?
- Who creates it?
- How is it versioned?
- Can it be retained by a closure?
- What happens after the invocation ends?
- How are Promise settlements routed back to a non-thread-safe VM?
- What can be stored in a continuation?
- What happens when a worker times out?
- How does a callback ID link to a closure in a fresh runtime?
- What happens to a continuation after a deployment?

The abstraction becomes real only when these details have one coherent answer.

This is also why I find language design to be such a strong probe of model capability. A model can write a persuasive architecture document while hiding contradictions in prose. A language forces the abstractions to become operational. The nouns need representations. The operations need signatures. The effects need interpreters. The invalid combinations need errors. The authority needs a location. The state needs a lifetime.

If the model can design a language and then implement its interpreter, it has to walk both directions on the abstraction ladder.

## Ask for a language first

One of my most reliable prompting techniques over the last several years has been to ask for a language before asking for the application.

“Language” here can mean many things. It may be a YAML DSL if the problem is mostly declarative. It may be a JavaScript API if I need bindings, functions, loops, branching, or asynchronous composition. It may be a set of Go interfaces, a widget tree, a query notation, a command language, or a small collection of typed builders.

The point is not to invent syntax for its own sake. The point is to find the boundary where domain concepts and computational concepts meet.

On the domain side, a logistics system contains things such as orders, shipments, refunds, routes, appointments, exceptions, and plans. An identity system contains identities, credentials, invitations, challenges, consent, and sessions. A RAG experiment system contains corpora, retrievers, rankers, prompts, evaluators, datasets, runs, and artifacts.

On the computational side, there are values, bindings, branches, loops, effects, state transitions, retries, transactions, serialization, concurrency, and failure.

Application complexity often accumulates at the seam between these two worlds. A domain expert says “add a refund workflow.” The implementation of that sentence may require a database state transition, permissions, a form, validation, money calculations, an audit event, a queue, a notification, a page, and CSS. A single prompt now asks the model to bridge from a high-level domain intention all the way to dozens of unrelated implementation details.

That is extremely token-intensive in a deeper sense than merely consuming context. The model has to repeatedly reconstruct the same abstraction bridge. Every new feature prompt contains a hidden request to rediscover the architecture.

If the project instead has a small language of workflows, forms, effects, and domain operations, “add a refund workflow” may become twenty lines of code. The language already contains the bridge. The model no longer needs to infer where validation belongs, how a form is rendered, how a transaction is committed, or how an error is represented. Those decisions have been made once in the interpreter.

This is why a good language changes the effective intelligence of the model. It reshapes the problem into a surface on which the model can generalize more reliably.

I wrote about this before as generalization shaping: notation, tools, code, and APIs reduce a messy problem into a smaller one with stronger regularities. The current identity-provider work feels like the same idea applied recursively. I asked the model to build a scripting language, and in doing so it exposed the computational DNA of the host application itself.

There is an old idea in computer science that if you can design a language in which the solution is easy to express, much of the original problem has disappeared. I think “programming language” can actually distract from this. Programming makes us think of an activity performed by programmers. The more fundamental thing is computational language: a way to describe which computations exist, what they mean, and which details are handled by the machine.

This matters even more with LLMs because they are, quite literally, language machines. We have spent decades building abstractions so humans can direct computers with more useful words. Now the machine that writes the instructions also benefits from those abstractions. A well-designed DSL does not only make a human programmer more productive. It gives the model a more stable semantic surface to operate on.

I have generated thousands of small languages and APIs over the last three or four years. That number sounds more systematic than the process has been. Most of it has been vibed. I try a notation, see where the model struggles, add a primitive, remove an escape hatch, move something from script to runtime, generate more examples, and gradually accumulate patterns I no longer consciously name.

Some of those patterns are obvious API design. Some come from Common Lisp, macros, interpreter design, and old-fashioned framework work. Some are specific to how LLMs respond to concepts with strong representation in the training corpus. Some are likely things I have rediscovered badly. Until now, the optimization loop has mostly depended on my own taste and on whether the generated applications feel clean.

The thing 5.6 changes is that the model can participate in the research loop around the language itself.

## From codebase to textbook

Once the identity-provider scripting layer existed, I wanted to know whether the model could step back out of the codebase and identify what had actually been built.

I asked it to study the branch and write a textbook or report about the interesting interpreter constructs: serialized continuations, invocation capabilities, deterministic callback registration, closed outcomes, secret handles, runtime leasing, generation-aware resumption, and the rest.

It produced a long monograph that was surprisingly concise at the level of ideas. It did not simply walk the directory tree and explain that one package contained workflows and another contained scripts. It reconstructed a dependency of concepts.

It began with the danger of scripting an identity provider. From there it explained why protocol authority had to remain native, why JavaScript outcomes had to be closed, why durable control flow could not be a suspended Promise, why callbacks needed stable identities, why capabilities had invocation lifetimes, why a worker could only be reused after positive evidence of quiescence, and why hot reload created semantic generations.

That is what I mean when I say the model can teach. It can synthesize a complex thinking workflow and arrange it so that the next concept is motivated by the previous one. It can give names to techniques that exist in code but may never have been named by the implementer. It can connect those techniques to a wider literature without reducing the document to a literature review.

In a way, it reverse-compiled the codebase:

```text
implementation
    -> invariants
    -> computational patterns
    -> named concepts
    -> explanatory sequence
```

I ended the morning with around two hundred pages of textbook-style material across several related investigations. Normally that amount of generated prose becomes exhausting very quickly. You can feel the entropy rise. Sections begin repeating one another, the narrative stops advancing, and the text becomes polished sludge.

This material remained interesting because each section had a job. There was simply a lot of material because the project contained a lot of machinery.

There is an obvious warning here: a beautiful explanation can be beautifully wrong. Documentation generated by the same model that wrote the code can become a self-consistent mythology. The useful version needs exact source links, implementation status, test references, distinctions between what exists and what is proposed, and explicit unresolved concerns.

But when it has those anchors, the ability to turn a large unfamiliar codebase into a readable conceptual textbook changes how ownership can work. I do not need to reconstruct the architecture from a thousand functions and a stream of diffs. I can read the narrative, inspect the source behind the load-bearing claims, and then use the document as a map for deeper review.

That matters because agentic coding is making code production much faster than code comprehension. A model that can produce both the system and an inspectable theory of the system is doing something qualitatively different from autocomplete.

## The language optimization loop

This is the part I am most interested in now.

If the model can research programming-language ideas without immediately losing the thread, then my informal “ask for a language first” technique can become a much more systematic language optimization loop.

The current loop is roughly:

```text
describe the domain
    -> ask for a DSL or JavaScript API
    -> implement a few examples
    -> notice awkwardness
    -> patch the API
    -> repeat
```

This works remarkably well, but it is artisanal. The evaluation criteria live mostly in my head. A construction feels too verbose. The model repeatedly misuses one primitive. An abstraction leaks implementation detail. A supposedly generic operator creates too much authority. A domain expert cannot read the resulting program. I change the language and try again.

A research-capable model makes a different loop possible.

Start with a corpus of representative tasks, not one feature request. For an identity system, these might include invitation signup, virtual users, account recovery, multi-factor challenge, policy denial, consent, provider selection, and migration of an in-progress browser workflow. For a RAG lab, they might include comparing retrievers, freezing a corpus, varying a prompt, evaluating with several metrics, caching provider calls, and reproducing a run months later.

Ask the model to infer the domain ontology and the computational requirements separately. Which concepts belong to the domain? Which operations are effects? Which values need stable identity? Which things are secret? Which actions are durable? Which parts need loops or branches? Which choices should remain native policy?

Then ask it to propose competing languages rather than one answer.

One design may be highly declarative and easy to analyze but awkward for complex control flow. Another may use JavaScript callbacks and be pleasant to author but expose too much dynamic behavior. A third may compile direct-style async functions into explicit state machines. A fourth may separate a pure policy language from a transactional effect language.

Implement the smallest possible interpreter for each serious candidate. Generate real programs. Have the model use the language, not merely praise it. Feed it tasks it has not seen. Ask a second model to use it. Ask a human to read the result. Collect the errors.

Now the language can be evaluated on several axes:

- How long are representative programs?
- How many concepts must an author learn?
- How often does the model request authority it does not need?
- How many invalid states can be represented?
- Which mistakes are caught statically?
- Which mistakes survive until runtime?
- How local is a change?
- How legible is a semantic diff?
- Can a program be explained from its manifest?
- Can the interpreter enforce the hard guarantees once for every program?
- How expensive is the implementation and proof burden?
- Does the language remain honest about the domain, or does it hide important complexity?

The research step then becomes part of the loop rather than something done once at the beginning. The model can search for analogous designs in workflow systems, capability languages, effect systems, durable execution frameworks, theorem provers, protocol state machines, and compiler workbenches. It can compare the candidate language to those ideas, identify missing distinctions, and propose experiments rather than merely adding fashionable terminology.

Then revise the language, rerun the corpus, and compare.

This is not just prompt optimization. It is not “find the magic phrasing that makes the model produce the right code.” The artifact being optimized is the computational language between the model and the application.

That distinction matters because prompts are ephemeral and local. A language compounds.

Once the IDP has a good workflow language, every future identity feature becomes easier. The interpreter centralizes the security properties. The examples become training material for humans and models. The compiler can infer capability use. The static analyzer can reject secrets crossing a continuation boundary. The runtime can meter host calls. The documentation generator can produce a diagram. The deployment system can show that a new version added one effect and changed one continuation schema.

The language becomes a piece of infrastructure that reshapes all later work.

There is also a peculiar possibility here: the model is simultaneously the language designer, the language user, and part of the evaluation harness.

That could be dangerous. A language optimized only for one model may become alien to humans or brittle across model generations. The model may exploit accidental cues rather than understand the semantics. It may prefer verbose forms because they resemble its training data, or compact forms that are impossible to maintain. We need human readability, independent interpreters, static checks, cross-model tests, and domain-expert review.

But it is also an extraordinary experimental setup. We can generate hundreds of representative programs, mutate them, ask models to repair them, compare error rates, measure the authority each version requests, and observe where the notation helps or hinders generalization. Language design has traditionally been expensive to test because recruiting many skilled users is difficult. Models are not substitutes for users, but they are extremely cheap additional users with interesting failure modes.

The loop could eventually operate above the level of one project.

Imagine a malleable JavaScript compiler or interpreter where a project defines:

- its value types;
- its capabilities;
- its effects;
- its durable operations;
- its secret and ownership rules;
- its cost model;
- its verification passes;
- its native bindings;
- its permitted language features.

Tiny-IDP would be one profile. A reproducible RAG laboratory would be another. A deployment orchestrator, document approval system, policy engine, or agent tool runtime could share the compiler and runtime machinery while exposing different computational worlds.

The compiler could turn a familiar JavaScript-shaped surface into a much smaller semantic intermediate representation. It could derive callback manifests, capability requirements, effect rows, continuation schemas, and resource budgets. Different backends could execute the same verified program: Goja for compatibility, a small interpreter for assurance, a symbolic backend for model checking, perhaps generated Go or WebAssembly for deployment.

The flagship feature for Tiny-IDP would be a `durable await` that looks like ordinary direct-style code to the author but compiles into the explicit continuation records the runtime already uses.

```javascript
const form = await durable.present(SignupForm);
const proof = await durable.emailCode(form.email);
return commit.signup(form, proof);
```

At each durable suspension point, the compiler performs liveness analysis. Which values are needed afterward? Can they be serialized? Are they public? Are they bounded? Are any of them capabilities, secrets, closures, Promises, native resources, or engine-specific objects? If so, compilation fails or the value must be converted into an approved native reference.

The author gets pleasant direct style. The runtime still gets a small, explicit, reviewable state machine. We improve usability without weakening the semantic boundary.

This is the direction I mean by a language optimization loop: not merely having the model generate more code, but having it research, propose, implement, use, analyze, and refine the language in which future code will be expressed.

**[IMAGE 3 — annotated reproducible RAG operator design]**

*Suggested caption: The same shape appearing in a second domain: trusted source packages, canonical artifacts, declared host capabilities, fresh constrained runtimes, typed results, and reproducibility evidence. That recurrence is what makes me think this is a general language pattern rather than an IDP-specific trick.*

## Research without collage

The research capability is what makes this feel possible now rather than merely aspirational.

In the past, I could ask a model to survey effect systems, capability security, durable workflows, and formal verification, but I had to act as the synthesis layer. I had to notice when two papers used similar words for different ideas, when an analogy was superficial, when a technique depended on a closed-world assumption that did not apply, or when the proposed application had quietly lost the original security boundary.

With 5.6, the model is better at maintaining the shape of the research question while moving across sources and then returning to the project. It is not only summarizing papers. It is deciding which ideas matter for this codebase, how they relate, and what concrete refactor would make them useful.

This is what I somewhat recklessly called “PhD-level” in conversation. I do not mean that it is producing a groundbreaking dissertation or that it should receive credentials. I mean the more ordinary but still difficult behavior of sustained technical research: map a literature, identify a tractable core, choose methods, apply them to a complicated artifact, document limitations, and keep the work coherent over many steps.

I do not think it is postdoc-level yet, if we are going to keep abusing the metaphor. I can see it overgeneralize. I can see it become too enchanted by a formalism. I can see places where the bibliography is stronger than the actual argument. I can see it benefit enormously from a human who has enough taste to reject a clean but irrelevant theory.

But the floor has moved. The model can remain inside the research loop long enough that I am no longer merely using it to retrieve and summarize material. I can use it to create a research program around a piece of software.

That changes the economics of ambitious engineering. Many ideas that were previously unreasonable for a small project—not because implementation was impossible, but because the research and synthesis cost was too high—become plausible experiments.

Static analysis for a small identity provider. Model checking for selected protocol transitions. A compiler that derives explicit continuations from JavaScript. A project-specific capability and effect system. A textbook that reverse-engineers the resulting architecture. A comparative language-design loop across two unrelated domains.

Each of these would traditionally be a substantial side project before the application itself could move forward. With a model that can keep the threads coordinated, they become things I can explore in parallel with production work.

That does not make them free. It changes which cost is scarce. Generating a great deal of coherent work becomes cheaper. Deciding what deserves to exist, defining acceptance evidence, and maintaining contact with reality become more important.

## The cracks, and why “unsupervised” cannot mean unaccountable

There is a dangerous version of this story where the conclusion is that the model can now research, architect, implement, verify, and document a system, so the human can simply stop paying attention.

That is not my conclusion.

I built a codebase I largely did not read, and that is interesting partly because it is uncomfortable. A system can have beautiful design documents, passing tests, formal-looking models, and a coherent textbook while still being wrong in ways none of those artifacts represent. Identity protocols have hostile environments, integration assumptions, operational failure modes, cryptographic boundaries, and deployment realities that do not disappear because the internal architecture is elegant.

The model can also create a self-confirming world. It writes the code, writes the tests, writes the design document, and then writes the textbook explaining why the design is good. Without independent anchors, coherence becomes a liability because it is persuasive.

The response is not to abandon the workflow. It is to make the evidence harder to fake.

That means executable conformance suites, adversarial tests, restart tests, replay tests, race detectors, browser integration, source-linked claims, canonical manifests, semantic diffs, explicit generation identities, traceable native effects, and independent review of the most security-sensitive boundaries. It means distinguishing “the model produced a plausible formal model” from “the implementation refines the model under stated assumptions.” It means retaining old generations when a continuation cannot be safely migrated rather than trusting a prose compatibility argument.

It also means treating unsupervised as a description of interaction frequency, not responsibility.

I can let the model work for several hours without steering every step. I cannot let the resulting system enter production without a theory of what evidence makes it acceptable.

This is part of why the language-first approach matters. A smaller language makes independent evidence more tractable. If arbitrary JavaScript owns the identity provider, the review surface is every possible program behavior. If JavaScript can only choose among typed capabilities and return closed outcomes, the trusted boundary is smaller. If browser workflows compile to explicit continuation graphs, they can be inspected. If effects are inert plans, native committers can enforce the transaction shape. If every artifact carries a semantic manifest, deployment review can focus on authority and state changes rather than only text diffs.

Abstraction is not an escape from verification. A good abstraction creates a place where verification can be applied once.

## Where I am in the model cycle

So, returning to the five stages.

Stage zero was immediate: 5.6 produced several outputs that were conspicuously better than what I had become used to.

Stage one was brief because ordinary coding was already working well enough that I did not initially know what the new capability changed. A better patch is still a patch.

Stage two arrived when the identity-provider research kept going. The model did not merely collect material. It altered the fundamental representation of the application, built a scripting system that rejected my naive framing, and then extracted a coherent programming-languages textbook from the result.

That was the *oh, fuck* moment. The unit of delegation had moved from implementation to research-backed system design.

I am entering stage three now. I can see the cracks. The model still needs carefully chosen artifacts. It can write too much. It can construct an elegant conceptual system faster than the empirical evidence accumulates. It needs explicit instructions to separate implemented behavior from proposals. It benefits from being asked for competing designs and falsification criteria rather than one grand synthesis. It needs independent tests and sometimes a second model or a human domain expert to challenge the result.

I am beginning to turn those cracks into techniques:

- ask for a language before an application;
- ask for multiple candidate languages before selecting one;
- force the compiler or interpreter contract to become explicit;
- maintain diaries and research artifacts so the path remains inspectable;
- require source-linked textbooks rather than detached explanations;
- use semantic manifests and end-to-end gates;
- make the model use the language it designed;
- optimize against a corpus of real tasks;
- preserve native authority around the things that cannot be delegated safely.

Stage four will be fluency: being able to prompt this kind of research and language evolution almost blindly because the workflow has become internalized. I am not there yet.

The unusual thing is that I can already see the next workflow taking shape.

It is not “ask a larger model to write a larger application.” It is something closer to:

```text
ask the model to discover the computational language of the domain
    -> implement and verify the interpreter
    -> express the application in that language
    -> observe where humans and models struggle
    -> research better abstractions
    -> evolve the language
    -> regenerate and recheck the application
```

That loop happens above the level of ordinary code generation. The code becomes one compiled artifact of a more important design activity.

## The abstraction machine

I have spent a lot of time over the last few years trying to find prompts that do not work. Since GPT-5, that has become harder in ordinary programming. The failures increasingly appear not at the level of syntax or local implementation, but at the level of framing: choosing the wrong abstraction, exposing too much authority, failing to define evidence, designing a language that does not match the domain, or optimizing the wrong thing.

5.6 seems materially better at operating in that layer.

It can look at a concrete codebase and recognize that the requested feature is actually a language-design problem. It can look at a collection of papers and identify the subset that changes the implementation. It can introduce an abstract fundamental layer, move the application onto it, and then produce a narrative that teaches the layer back to me. It can be systematic without automatically becoming maximalist. At its best, it can display something close to taste.

The deepest part of this for me is not that the model knows more programming-language terminology. It is that it can coordinate domain abstractions and computational abstractions.

A challenge in an identity system is simultaneously a human concept, a protocol event, a security boundary, a piece of evidence, a browser interaction, a durable state transition, and an input to future policy. A good language decides which of those aspects the script author sees and which the runtime owns. A good interpreter makes that division executable. A good compiler can make the convenient source form lower into the safe runtime form. A good textbook can explain why the division exists.

The model was able to move among all of these views without immediately dropping one.

That is why “abstraction machine” feels like the right phrase to me. Not because the model floats away from concrete details, but because it can move up and down the ladder: recognize patterns in the concrete, manipulate them in the abstract, and return them to the concrete as working machinery.

The next step is to make that movement itself more systematic.

I want to turn the thousands of small languages I have generated by feel into a real experimental loop. I want task corpora, competing notations, interpreters, model users, human readers, static analyses, semantic diffs, and research passes. I want to know which language shapes make models generalize cleanly, which abstractions reduce authority, which errors become impossible, and where elegance merely hides complexity.

Maybe this will devolve. Maybe 5.6 is still better at producing the appearance of a research program than at sustaining one. Maybe the cracks will become obvious once the novelty wears off. I have only been using it for a couple of weeks, and I have learned by now not to confuse the first successful project with a universal capability claim.

But this is the first time I have felt that the language optimization loop is not just a personal prompting trick. It may be a practical research method.

And that is a much larger change than writing code faster.


---

> ok, i do want you to tighten it up by a more structured approach, but I do like th emore expansive form. I do want to put the focus on 5.6 presenting a new step function and its capability to do research and synthesize, and use my idp (but you need to introduce all these things), and then go onto an exploration of what tells me it is better at resech and synthesizing and doing abstraction and such.

<details><summary>💭 Thinking</summary>

**Revising article approach**

I’m focusing on adjusting the article, keeping the user’s preferences in mind. I’ll include the updated steps and research synthesis, while verifying model names and minimizing citations in the rewrite.

**Revised article approach**

</details>

```json
{"system1_search_query":[{"q":"site:openai.com GPT-5.6 Sol OpenAI official"}],"response_length":"short"}
```

<details><summary>💭 Thinking</summary>

**Browsed OpenAI for model 5.6 details**

</details>

```unknown
bash -lc sed -n '1,260p' /mnt/data/abstraction-machine-gpt-5-6-substack-draft.md
```

<details><summary>💭 Thinking</summary>

**Inspected file content**

**Planning article structure**

I’m outlining a clear, structured article with a focus on new abstractions in research loops, defining key concepts, and integrating case studies. I’ll aim for clarity and avoid meandering.

**Planned article structure**

</details>

```unknown
bash -lc grep -n '^## ' /mnt/data/abstraction-machine-gpt-5-6-substack-draft.md && wc -w /mnt/data/abstraction-machine-gpt-5-6-substack-draft.md && sed -n '260,620p' /mnt/data/abstraction-machine-gpt-5-6-substack-draft.md
```

<details><summary>💭 Thinking</summary>

**Extracted content and drafted article on GPT-5.6 theory**

</details>

I restructured the essay around one central claim: **5.6 changes the delegable unit of work from implementation to research-backed system design.**

[Download the revised 7,570-word Substack draft](sandbox:/mnt/data/abstraction-machine-gpt-5-6-substack-revised.md)

The new progression is:

1. The step function and your five-stage model-adoption cycle.
2. A clear introduction to the identity provider and why it was a demanding experiment.
3. The static-analysis work as the first evidence: the model changed the application’s ontology rather than attaching superficial checks.
4. The scripting request as the main case study: it rejected the naive architecture and built a constrained language instead.
5. A structured account of what specifically demonstrates better research and synthesis.
6. LLMs as abstraction machines and your “ask for a language first” method.
7. The language-optimization loop as the larger implication.
8. Limits, accountability, the cracks you are beginning to see, and a return to the step-function claim.

I retained the expansive, first-person form, the technical side excursions, the five-stage framing, and the three annotated-image placements. I removed some repetition and made the interpreter details serve as evidence for the model-capability argument rather than becoming the article’s primary subject.

The draft uses **GPT-5.6 Sol**, OpenAI’s current official name for the flagship model. citeturn307672search0

# The Research Step Function

## What changed when an LLM stopped merely writing code and started redesigning the languages in which the code could be expressed

GPT-5 was the first model I trusted with a genuinely large refactor.

Before that, even when a model appeared capable of changing a substantial codebase, I still had to supervise the process closely. I could delegate a task, but not really relinquish it. I would come back to an implementation that was mostly correct and then spend hours finding the small inconsistencies: duplicated abstractions, slightly wrong assumptions, an incomplete migration, one package following the new architecture while another quietly preserved the old one.

GPT-5 changed the unit of work I could hand off.

I could ask for a significant structural change and expect the model to preserve enough context, follow consequences far enough through the codebase, and repair enough of the damage caused by its own changes that the result was recognizably a refactor rather than a pile of patches.

5.6 feels like a similar jump, but in a different dimension.

The most concise way I can describe it is this:

> GPT-5 was the first model I trusted to refactor almost unsupervised.  
> 5.6 is the first model I have trusted to research almost unsupervised.

I do not mean that it can search for papers and summarize them. Models have been able to do that for a while.

I mean that it can investigate a difficult subject, separate the important ideas from the surrounding literature, apply them to a real and messy codebase, reorganize that codebase around the resulting concepts, and then explain what it did as a coherent body of thought.

That last part matters.

The output does not merely look like research pasted together. It increasingly looks like the result of someone having formed a model of the problem.

It can identify a set of abstractions, give them names, explain how they relate, arrange them into a sequence that a reader can follow, and then move back down into implementation details without immediately losing the structure it discovered.

I have only been using it for a couple of weeks, so this is not a benchmark claim. It is a report about a change in my own workflow. I can already see cracks in it. I know from experience that the first weeks with a new model are full of both genuine discoveries and demo effects.

But this is the closest I have come in more than a year to the feeling that the boundary of what can be delegated has moved again.

The project that made this visible was an identity provider I had barely read.

---

## The codebase I deliberately did not understand

Over the last several months, I have been building my own identity provider.

“Building” is not quite the right word. I have been directing models to build it.

I did not begin with deep knowledge of OAuth, OpenID Connect, identity-provider architecture, credential storage, challenge flows, or the various protocol and security invariants involved. I was curious how far I could push the agentic workflow if I chose a domain that was both difficult and unforgiving.

So I let the project grow beyond what I could hold in my head.

This was partly deliberate. I wanted to discover what happens when a codebase becomes too large and too specialized for me to maintain through traditional line-by-line familiarity, but is still surrounded by enough structure that I can continue to direct its evolution.

The identity provider worked. More importantly, the work did not immediately look like complete madness.

The implementation appeared systematic. The design documents were consistent. New features were generally integrated into existing abstractions rather than attached as isolated mechanisms. The code survived repeated iterations as I moved it closer to production.

At some point, I asked the model to research and introduce static analysis, model checking, and ideas from formal methods around OAuth and identity protocols.

This was a deliberately broad request. I did not specify a particular theorem prover or formalism. I did not provide a detailed implementation plan. I asked it to research the area and improve the system.

Previous models could do this kind of work in a superficial sense. They could find papers, describe model checking, add a state machine, perhaps generate some assertions, and produce a document containing plausible formal-methods vocabulary.

The problem was that the result often felt assembled.

You could see where one research source ended and another began. The model might correctly summarize several techniques but fail to establish which properties they were supposed to prove, how they applied to the actual code, or what had to change structurally before those techniques became meaningful.

5.6 behaved differently.

It did not merely add a checker beside the existing implementation. It substantially reorganized the internal representation of the application so that tracing, invariants, transition validation, and assertions became natural properties of the system.

That is an important distinction.

Formal analysis is often presented as something you apply to an existing program. In practice, the program frequently has to be reshaped before it has the kinds of objects and transitions that can be analyzed cleanly.

The model recognized this without being explicitly instructed to perform a foundational rewrite.

It introduced clearer representations of state, events, outcomes, evidence, protocol transitions, and native operations. It moved responsibilities into places where assertions could be made about them. It created the objects required to state meaningful invariants.

I had asked it to add analysis.

It changed the ontology of the program so that analysis had something stable to talk about.

I had not previously seen a model make such an aggressive internal redesign, across a large codebase, in response to such a broad research request, while still keeping the project coherent.

That was the first sign that something had changed.

The second came when I asked it to make the identity provider scriptable.

---

## I asked it to make the IDP scriptable. It rejected the premise.

I wanted scripting for practical reasons.

I wanted to support things like invitation flows, virtual users, project-specific signup policies, and alternate identity-provider behavior without hard-coding every variant into the core application.

I wanted the IDP to function more like a set of Lego blocks than a single opinionated service.

The obvious implementation would have been to expose a JavaScript context containing useful host objects:

```javascript
ctx.store
ctx.sql
ctx.fetch
ctx.oauth
ctx.tokens
ctx.signingKey
```

Perhaps with some wrappers, validation, and documentation.

That would certainly have made the identity provider scriptable.

It would also have undone much of the architecture that had just been introduced.

A script with access to the database, credential state, token issuance, network clients, request objects, signing keys, or protocol internals is not merely customizing an identity provider. It is becoming a second identity provider embedded inside the first.

Every security property would then depend on arbitrary JavaScript preserving it.

The scripting API would no longer be a customization layer. It would be an alternate protocol implementation.

The model effectively refused to build that.

It did not refuse the feature. It rejected my framing of the feature.

Instead of “make the IDP scriptable,” it arrived at something closer to:

> Permit JavaScript to express narrowly bounded policy and composition while Go retains custody of protocol authority, credentials, persistence, browser handling, native evidence, and atomic effects.

That sentence is already a small language design.

JavaScript could receive typed input, invoke explicitly granted capabilities, choose among host-defined presentations, and return one of a closed set of outcomes.

It could ask the host to look something up. It could select a challenge. It could propose an effect plan. It could name a legal next handler.

It could not open a transaction, read a signing key, persist arbitrary runtime state, write an HTTP response, mint a token, consume credentials directly, or reach ambient modules.

The interesting thing was not any single restriction.

Every individual pattern had precedents:

- object capabilities;
- closed algebraic outcomes;
- state machines;
- schema validation;
- deterministic builds;
- worker isolation;
- explicit continuations;
- transactional effect plans;
- generation pinning.

The impressive part was the way they were fitted together.

Each mechanism covered a failure mode created by another mechanism.

Capabilities constrained what JavaScript could ask the host to do.

Typed schemas constrained what crossed the language boundary.

Closed outcomes constrained what kinds of control transfer the script could request.

Native effect plans prevented JavaScript from directly mutating identity state.

Explicit continuations prevented browser workflows from depending on a live JavaScript heap.

Generation fingerprints prevented durable state from silently resuming under different code.

Worker-disposal rules prevented a timed-out or ambiguously interrupted runtime from returning to the pool.

None of this was merely ornamental architecture. The design document tied the abstractions to implementation packages, validation passes, rollout phases, and end-to-end gates.

That is what made it feel tasteful rather than merely elaborate.

---

## What model taste looks like

“Taste” is an uncomfortable word to use about a model because it is easy to make it mean whatever we liked about the output.

I do not mean that the model used my preferred naming conventions or produced code that looked elegant at first glance.

I mean something more operational.

The model showed taste by refusing to preserve the wrong abstraction.

It recognized that exposing the underlying IDP machinery to JavaScript would produce a locally convenient but globally incoherent system.

It showed taste by modifying the foundations instead of weaseling its way toward a checklist.

A weaker implementation could have added a script runner, a few wrappers, some validation, and enough examples to declare the task complete. This one introduced a serious semantic boundary and then rebased the requested feature on top of it.

It showed taste by making abstractions pay rent.

The continuation mechanism existed because browser interactions cross process and time boundaries.

The capability system existed because scripts needed selective power without ambient authority.

The fingerprints existed because persisted callback names have to keep meaning the same thing.

The outcome algebra existed because “denied,” “not applicable,” “completed,” and “infrastructure error” must not collapse into arbitrary JavaScript truthiness.

The runtime pool existed because Goja runtimes are stateful and not goroutine-safe.

The worker-disposal rule existed because interruption creates uncertainty, and uncertainty is not a safe state to reuse.

The design covered a lot of ground, but each part answered a specific question.

It also remained pragmatic.

The model did not respond to “make this scriptable” by attempting to formally verify all of ECMAScript or by inventing a new language from scratch. It used JavaScript as an authoring surface while putting the important semantics into Go-owned representations.

This is the kind of distinction models have traditionally struggled with.

They have long been able to generate more architecture.

The difficult part is knowing where more architecture reduces complexity and where it merely moves it around.

---

## A serialized continuation is just a database field

One of the concepts I asked the model to explain afterward was the serialized continuation.

The term sounds more exotic than the basic mechanism.

A browser workflow reaches a point where it must wait for a user to submit a form or complete a challenge. The current HTTP request ends. The process might restart. The next request could arrive on another machine.

The application therefore stores something like:

```json
{
  "next": "signup.verify_email",
  "carry": {
    "email": "alice@example.com"
  }
}
```

At this level, a serialized continuation is basically a state-machine field in a database.

But that description hides all the important questions.

What exactly does `signup.verify_email` identify?

Is it merely a string?

Does it identify a function in the current source file? A function in any loaded module? The function associated with a particular build? A handler whose input schema matches the stored carry? A handler reachable from the state that created the continuation?

What data can cross the boundary?

Can it contain a password? A JavaScript closure? A Go pointer? A Promise? An HTTP request? A capability function? A raw verification code? A database transaction?

What prevents replay?

What happens if the same browser submits twice?

What happens after the code has been hot-reloaded?

What happens if a callback with the same name has changed meaning?

What happens if the schema changed?

The rigorous design is not the database field. It is the complete set of constraints surrounding it.

The continuation can contain bounded, serializable, schema-checked public data and references to native state.

It cannot contain JavaScript runtime objects.

The resume handler has to be registered in the same workflow.

Its input schema has to match.

The continuation carries expiry, revision, browser binding, generation identity, and native evidence references.

Advancement is atomic.

Old code generations may have to be retained so old continuations can resume under the semantics that created them.

This is a programming-languages idea, a distributed-systems idea, and a security idea at the same time.

What surprised me was that the model not only implemented this, but later reconstructed it as a teachable concept.

It could move from the concrete code to the abstract pattern and then explain why the abstraction mattered.

That is what I mean when I call these systems abstraction machines.

---

## LLMs as abstraction machines

Saying that an LLM is a pattern-matching system is technically reasonable and descriptively almost useless.

The interesting question is what kinds of patterns it can recognize, at what scale, and what it can do after recognizing them.

A useful working model is:

```text
concrete artifacts
    -> abstraction recognition
    -> abstraction coordination
    -> concrete reconstruction
```

The concrete artifacts might be:

- routes;
- structs;
- database calls;
- test cases;
- callback registries;
- request handlers;
- design notes;
- partially implemented features;
- relevant papers and existing systems.

The model recognizes patterns in them:

- state machines;
- authority boundaries;
- transactions;
- effect plans;
- event traces;
- durable continuations;
- capability passing;
- lifecycle regions.

But merely recognizing an abstraction is not enough.

Models have been proposing state machines and capability systems for years.

The difficult part is coordinating several abstractions so that they do not contradict one another.

If callbacks can survive across browser requests, their identities have to be durable.

If their identities are durable, code generations have to be tracked.

If code generations are tracked, activation has to be reproducible.

If runtimes are pooled, callbacks have to register consistently in each runtime.

If capabilities can return Promises, asynchronous work has to settle before reuse.

If execution is interrupted, the runtime may no longer be safe.

If secrets cannot enter JavaScript, form handling and effect construction have to preserve opaque native references.

This is not a list of independent features.

It is a dependency graph of ideas.

The model appears increasingly able to form and manipulate these graphs.

It can then move downward again:

- create packages;
- define interfaces;
- add validation passes;
- generate canonical hashes;
- add conformance tests;
- migrate existing code;
- produce a rollout plan.

This downward movement is where many previous generations became unreliable.

They could talk convincingly about an abstract architecture, but once they returned to implementation, the architecture degraded into wrappers and special cases.

The new behavior feels more like an ability to retain the abstraction while reconstructing the concrete system.

I am not claiming that this is how the model “really thinks.” I am describing the most useful mental model I currently have for what it can do.

---

## Ask for a language first

This connects to a prompting technique I have used for several years.

When I begin a new project or a large subsystem, I often ask the model to design a language before asking it to build the application.

Sometimes that language is a YAML DSL.

If the problem is mostly declarative—configuration, schemas, finite graphs, manifests, policy tables—YAML or another data format may be sufficient.

If the problem needs variable binding, branching, loops, composition, or asynchronous operations, I usually ask for a JavaScript API.

The important point is not the syntax.

The point is that a language forces the boundary between the domain and the machine to become explicit.

Consider a logistics application.

The domain contains concepts such as:

- order;
- shipment;
- refund;
- route;
- delivery window;
- inventory reservation.

The computational side contains concepts such as:

- variables;
- branches;
- state transitions;
- transactions;
- retries;
- persistence;
- asynchronous effects.

Most application complexity arises where these two sets meet.

If I ask a model to “add a refund workflow,” it may have to bridge all the way from the business concept of a refund to:

- database models;
- eligibility policy;
- transaction handling;
- forms;
- validation;
- routes;
- rendering;
- styling;
- tests;
- audit logging.

That is an enormous semantic distance to cross in one prompt.

The model may have enough tokens to produce all the code, but the difficulty is not only token count. It has to maintain consistency across many levels of abstraction at once.

If the application already contains a small language of workflows, forms, effects, and policies, the same request becomes much smaller:

```javascript
workflow("refund", async ({ order, form, effects }) => {
  const request = await form.present(RefundRequest);

  if (!order.refundable(request.amount)) {
    return deny("not_refundable");
  }

  return effects.commit(
    refund.create(order.id, request.amount),
    notification.sendRefundReceipt(order.customer)
  );
});
```

Now “add a refund workflow” might truly correspond to twenty lines of domain-level code.

The system already knows what a form is, what an effect is, how a transaction is committed, how validation is performed, and how a denial is rendered.

The language has compressed the implementation.

It has also compressed the prompt.

This matters enormously for agents.

A good API is not merely ergonomic for humans. It reduces the inferential distance an LLM has to cross.

It turns a request that previously required reconstructing half the application into a request that fits inside a stable domain vocabulary.

---

## Languages expose the DNA of a system

There is another reason I like asking for a language first.

It is difficult to hide conceptual confusion inside a language design.

A conventional implementation can conceal uncertainty in details. The model can keep adding handlers, helper functions, and data structures without ever stating clearly what the system believes exists.

A language forces questions such as:

- What are the nouns?
- What are the primitive operations?
- Which operations have side effects?
- Which values are durable?
- Which capabilities can be delegated?
- What is native and what is script-defined?
- What counts as success?
- What counts as denial?
- What can be retried?
- What must be atomic?
- What may cross a process boundary?
- Which errors are part of the domain?

This lays bare what I think of as the DNA of the application.

There is domain DNA: the concepts meaningful to someone who understands identity, logistics, cooking, research, or finance.

And there is computational DNA: state, control, effects, persistence, concurrency, authority, evidence, and evaluation.

An API is a bridge between the two.

Good language design moves the boundary until the remaining programs become small and honest.

Bad language design either exposes too much machine detail or hides too much domain significance.

This is why language design is such a good probe of model capability.

It is not enough for the model to produce an attractive API. The API has to lower into something implementable. It has to preserve security and operational constraints. It has to support real examples without constantly escaping into host-language hacks.

The IDP scripting layer was a particularly strong demonstration because the domain is unforgiving.

The JavaScript API could not merely feel nice.

It had to preserve the identity provider’s security model.

---

## From codebase to textbook

After the scripting work had become large enough that I could no longer see its shape from the code, I asked the model to write a textbook about it.

The prompt was not especially sophisticated.

I asked it to study the branch and explain the interesting interpreter and Goja constructs: serialized continuations, invocation capabilities, deterministic callback registration, runtime leasing, schema boundaries, native effects, and the rest of the architecture.

The result was much better than the package-by-package documentation I expected.

Most generated technical documentation follows the file tree:

- this package contains these types;
- this function calls this service;
- this module registers these callbacks;
- this struct has these fields.

That is useful reference material. It is not a textbook.

The resulting document instead followed the dependency of ideas.

It began with the danger of scripting an identity provider.

Then it explained why protocol authority must remain native.

Then it introduced typed outcomes and capabilities.

Then it showed why browser interactions require explicit continuations.

Then it explained why durable callback names require deterministic registration and generation identity.

Then it moved into asynchronous settlement, worker reuse, secret handles, effect plans, replay, hot reload, and verification.

The ordering was pedagogical.

The model did not merely summarize the implementation. It reconstructed the reasons the implementation had to take that form.

I ended up with roughly two hundred pages of textbook-style material across several reports.

Normally, generated material of that length becomes exhausting. The prose starts repeating itself. Each section restates the thesis. The document accumulates plausible filler.

This material remained surprisingly dense.

It was long because the project contained many ideas, not because each idea was padded.

That ability—to build something, then step back from it, identify the reusable concepts, name them, connect them to the literature, and teach them in an appropriate order—is part of the capability jump I am trying to describe.

The model became both implementer and reverse compiler.

It compiled research and design into code, then reverse-compiled the code into concepts.

---

## The five stages of learning a new model

I have now gone through enough model releases that the discovery process itself has become familiar.

### Stage zero: “That is not bad at all”

The first interaction produces something visibly better.

This is the demo effect. It establishes that the model can do something impressive, but not whether that ability survives repeated use.

### Stage one: “I cannot really tell the difference”

The new model enters an old workflow.

I prompt it the same way I prompted the previous model and receive somewhat better results, but the qualitative shift is not yet obvious.

Capabilities do not automatically translate into productivity. The surrounding workflow has to change.

### Stage two: “Oh, fuck”

Eventually I stumble into a task that reveals that the unit of delegation has changed.

With GPT-5, that was large refactoring.

With some later models, it was reliability: I could launch several tasks and expect most of them to finish cleanly rather than spending the rest of the day repairing each one.

With 5.6, it has been sustained research and abstraction.

This is the moment when a model stops being “better at the old thing” and begins enabling a different way of working.

### Stage three: “I see the cracks”

After enough use, the limitations become concrete.

The model may overgeneralize a research result. It may produce beautiful but insufficiently grounded documentation. It may create an internally coherent system based on one incorrect assumption. It may optimize the stated acceptance criteria while missing an unstated constraint.

This stage is useful.

Specific cracks produce specific prompting techniques, tools, tests, and guardrails.

They also show what the next generation is likely to improve.

### Stage four: fluency

Eventually I know how to use the model almost without thinking.

I know when to ask it to research first.

I know when to ask for competing designs.

I know when to ask for a language.

I know how much autonomy to grant.

I know which outputs require source verification and which I can usually accept.

At that point I can use what I call brutalist prompts: short, direct prompts that depend on a learned understanding between me, the model, and the project infrastructure.

I am still moving through the earlier stages with 5.6.

The research and synthesis capability is clear enough to change my workflow. The failure modes are only starting to become visible.

---

## Toward a language optimization loop

I have generated thousands of small languages and APIs over the last three or four years.

This sounds more systematic than it has been.

Mostly, I developed intuition.

I would ask for a DSL, try it on real examples, notice which expressions felt awkward, revise the API, and gradually accumulate patterns.

I learned to recognize when YAML was enough and when JavaScript was necessary.

I learned to prefer host-defined effects over arbitrary callbacks.

I learned that models perform much better when domain operations have explicit names.

I learned that examples often teach an API better than prose.

I learned that a good DSL should make invalid states difficult to represent without making ordinary states painful to express.

But I did not run a scientific language-design process.

The ability of 5.6 to stay on track during research suggests that this can become more systematic.

Instead of informally revising a language until it feels good, we could build an explicit optimization loop.

Start with a corpus of representative tasks.

For an identity provider:

- invitation-based signup;
- passwordless login;
- virtual users;
- email challenges;
- recovery flows;
- consent;
- provider selection;
- account linking;
- revocation;
- migration of an in-progress flow.

For a reproducible RAG system:

- swap a retriever;
- compare chunking strategies;
- run a benchmark across models;
- cache an intermediate artifact;
- declare an experiment matrix;
- preserve provenance;
- rerun under an updated provider;
- explain a result difference.

Then propose several language designs.

Implement small interpreters or compilers for them.

Have humans and models express the same task corpus in each one.

Measure:

- program length;
- number of concepts required;
- invalid programs produced;
- repair iterations;
- authority exposed;
- interpreter complexity;
- quality of diagnostics;
- static properties that can be checked;
- generated test coverage;
- ease of migration;
- semantic diff quality;
- token use;
- consistency across model runs.

Research analogous designs from programming-language literature and production systems.

Revise the language.

Repeat.

This is not automatic language invention. Human judgment remains central.

Someone still has to decide:

- which concepts deserve stable names;
- which complexity should remain visible;
- which hidden details are safe to abstract;
- which guarantees are non-negotiable;
- which syntax is honest about the domain;
- which optimizations merely game the benchmark.

But the model can now participate in the loop at a much higher level.

It can search for prior art, derive alternatives, implement them, construct examples, run experiments, explain trade-offs, and update the design without immediately losing the original research question.

This could turn language design from a sporadic act of taste into a continuous engineering process.

---

## The model is not merely writing the language

There is a further implication.

Once the system has a well-defined language, the model is no longer responsible for reconstructing the full application stack each time it performs a task.

It writes small programs in that language.

The trusted implementation moves into the interpreter, compiler, verifier, runtime, and native capabilities.

This is valuable for humans, but it may be even more valuable for models.

A model asked to modify a general codebase has enormous freedom.

It can:

- invent a new abstraction;
- bypass an old one;
- call an internal service directly;
- duplicate behavior;
- accidentally widen authority;
- persist the wrong value;
- interpret an error incorrectly;
- violate an unstated lifecycle rule.

A model writing in a constrained domain language operates inside a much smaller possibility space.

The language can encode:

- legal state transitions;
- available capabilities;
- permissible effects;
- durable value types;
- resource budgets;
- closed outcome variants;
- required evidence;
- migration rules.

This changes how we think about agent reliability.

Instead of trying only to make the model reason perfectly over an unrestricted codebase, we can redesign the environment so that a much larger fraction of incorrect reasoning becomes an invalid program.

The model improves.

The language improves.

The compiler improves.

The verifier improves.

These are complementary paths.

---

## What “research without supervision” should actually mean

There is an obvious danger in describing this as autonomous research.

A model can produce a coherent fiction.

It can synthesize an architecture around a misread paper.

It can turn one implementation detail into a grand principle.

It can generate a persuasive textbook whose claims are not fully supported by the source.

The response should not be to deny that the capability has changed. It should be to become more precise about the form of supervision.

The most useful research outputs are not isolated essays.

They are research linked to artifacts:

- source references;
- implementation diffs;
- executable examples;
- static checks;
- test suites;
- model-checking traces;
- generated manifests;
- explicit assumptions;
- unresolved questions;
- comparisons with alternative designs;
- commit-pinned documentation.

In other words, the model can do more of the intellectual work, but that work should increasingly leave behind machine-checkable evidence.

This is another reason language and compiler design are attractive.

They force research conclusions to become operational.

“Use capabilities” becomes a capability type, a runtime representation, a lifetime rule, and a verifier check.

“Use explicit continuations” becomes a continuation schema, a liveness analysis, a persistence format, and a resume protocol.

“Make execution deterministic” becomes a closed module graph, a clock policy, a scheduler, a fingerprint, and a test.

The model’s explanation is only one output.

The real product is the system that embodies the explanation.

---

## A new unit of software work

The largest change may be that the natural unit of delegation is moving upward again.

First, models wrote functions.

Then they wrote features.

Then they performed refactors.

Then they implemented projects.

Now the useful unit may increasingly be:

- investigate a domain;
- identify its governing abstractions;
- design a computational language for those abstractions;
- implement the language runtime;
- rebase the existing application onto it;
- verify the resulting boundaries;
- teach the architecture to humans and future agents;
- iterate on the language using real task corpora.

That is a very different activity from code completion.

It is closer to computational institution building.

The model is not merely filling in an implementation. It is helping decide which kinds of programs should exist inside the project at all.

This is why the jump feels larger than an improvement in coding benchmarks.

The model can increasingly participate in the creation of the semantic environment in which future coding takes place.

---

## The closest thing to the vertical feeling

I have become used to new model releases.

Every few months, something improves enough to change how I work. The shock has become routine.

There is an initial demo, a period of uncertainty, a moment of discovering the unlock, a period of finding the cracks, and eventually a new normal.

It has become difficult to recover the feeling of looking vertically upward and realizing that a class of work I considered fundamentally difficult has become ordinary.

This IDP project brought some of that feeling back.

Not because the model built a lot of code.

Models have been able to build a lot of code for some time.

Not because every idea in the architecture was unprecedented.

Most of them have names and histories.

What felt new was the combination:

- sustained research;
- structural refactoring in response to that research;
- rejection of a naive feature premise;
- synthesis of several programming-language and security patterns;
- coherent implementation across a large codebase;
- and subsequent reconstruction of the work into a readable textbook.

The model was systematic without being blindly maximalist.

It was aggressive about changing the core but conservative about authority.

It built abstractions, then used them.

It did not merely solve the problem I asked for. It changed the language in which the problem could be stated.

That is the capability I am trying to understand.

And I suspect the most important workflow it enables is not simply asking models to build more applications.

It is asking them to help us discover, test, and refine the computational languages from which those applications can be made.

