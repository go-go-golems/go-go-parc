# Branch · Branch · Interpreter Constructs Analysis

- URL: https://chatgpt.com/c/6a5e2d99-3b2c-83ea-8ce3-c9bd9dcbd4e2
- Created: 2026-07-20T14:15:53.910Z

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

> Brainstorm and design how we can extract useful generic patterns out of this incredible work in order to create a “language / scripting platform design patterns Lego blocks framework” that allows other programs (from a scriptable 3d editor to a scriptable window manager to a webapp to an scriptable/entire embedded firmware to a scriptable full OS to a scriptable compiler, even proof assistant / formal method kernel ) to benefit and reuse this work.

<details><summary>💭 Thinking</summary>

**Designing a framework**

I’m planning how to design a framework that extracts patterns from a repo. It seems like I should inspect the repo and possibly do additional research to gather relevant external patterns.

**Designed a framework**

</details>

I’ll extract Tiny-IDP’s mechanisms into a reusable pattern catalog, then design a concrete framework with composable packages, contracts, profiles, and cross-domain adaptations.

```unknown
bash -lc git -C /mnt/data/tiny-idp rev-parse --abbrev-ref HEAD && git -C /mnt/data/tiny-idp rev-parse HEAD && find /mnt/data/tiny-idp/pkg -maxdepth 2 -type f | sort | sed -n '1,240p'
```

<details><summary>💭 Thinking</summary>

**Inspected repository branch and cloned GitHub repository to container**

**Searched GitHub for relevant terms and fetched design documents**

**Designing framework and document**

I’m planning to design a framework based on repo patterns, draw from previous content, and use specific file sections. I’ll likely create a detailed markdown report with citations and examples.

**Fetched code, designed framework, and validated schema content**

**Fetched repository and GitHub file content and components**

</details>

```json
{"open":[{"ref_id":"https://api.github.com/repos/go-go-golems/tiny-idp/git/trees/task%2Fprod-tiny-idp?recursive=1"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched the web and GitHub repositories for API URL**

**Fetched file content and design documentation from repositories**

</details>

```json
{"open":[{"ref_id":"https://github.com/go-go-golems/tiny-idp/tree/task/prod-tiny-idp/pkg/idpscript"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched multiple websites for GitHub repository related to idp script**

**Fetched file content, tasks, and details from GitHub repository**

**Designing the framework**

I’m thinking about using external research to help design a framework with patterns like security, effects, and reproducible builds. I’ll explore relevant sources, then propose a reusable and flexible architecture for different programs.

**Designed the framework**

</details>


---

> This is really about both a concrete go-go-goja based framework, and also a general framework for programming language interpreter/compiler work that can be applied across languages and projects

<details><summary>💭 Thinking</summary>

The user wants to emphasize that the work involves both a concrete go-go-goja based framework and a general framework for programming language interpreter/compiler work that is applicable across different languages and projects.

</details>

The framework will have two layers: a production Goja toolkit and a language-neutral, host-governed scripting microkernel built around staged IR, scoped capabilities, explicit suspension, and native effects.

```json
{"search_query":[{"q":"site:github.com/go-go-golems/go-go-goja runtimeowner RuntimeOwner engine factory goja"},{"q":"site:github.com/google/starlark-go deterministic hermetic language design"},{"q":"site:docs.wasmtime.dev fuel epoch interruption resource limiter"},{"q":"site:mlir.llvm.org dialect interfaces operation interfaces official"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched authoritative technical sources and academic papers across platforms**

**Inspected GitHub repository, documentation, and runtimeowner implementation**

**Designing deliverables**

I’m thinking of providing a detailed design, either as a chat response or a markdown file. Since the task is broad, I’ll keep it clear and well-cited, with a solid working name for the framework.

**Designed deliverables**

</details>


---

> Feel free to also look at all the work here https://parc.yolo.scapegoat.dev/note/research/kb/projects/go-go-goja and what patterns were discovered and used there (or https://parc.yolo.scapegoat.dev/note/research/kb/projects/widget-dsl and https://parc.yolo.scapegoat.dev/note/research/kb/projects/researchctl)

<details><summary>💭 Thinking</summary>

**Designing a framework**

I’m exploring how to create a detailed design around patterns, likely including a roadmap, taxonomy, or framework. I’ll also need to reference external sites and previous work before finalizing a report.

**Designed a framework**

</details>

I’ll synthesize recurring patterns across Tiny-IDP and the related projects into reusable Go/Goja components and language-agnostic primitives, including APIs, composition rules, assurance levels, and an implementation roadmap.

```json
{"open":[{"ref_id":"https://parc.yolo.scapegoat.dev/note/research/kb/projects/go-go-goja"},{"ref_id":"https://parc.yolo.scapegoat.dev/note/research/kb/projects/widget-dsl"},{"ref_id":"https://parc.yolo.scapegoat.dev/note/research/kb/projects/researchctl"},{"ref_id":"https://github.com/go-go-golems/tiny-idp/tree/task/prod-tiny-idp"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched the web and GitHub**

</details>

```unknown
bash -lc python - <<'PY'
import requests
urls=[
'https://parc.yolo.scapegoat.dev/note/research/kb/projects/go-go-goja',
'https://parc.yolo.scapegoat.dev/note/research/kb/projects/widget-dsl',
'https://parc.yolo.scapegoat.dev/note/research/kb/projects/researchctl',
]
for u in urls:
    try:
        r=requests.get(u,timeout=20)
        print(u, r.status_code, r.headers.get('content-type'), len(r.content), r.url)
        print(r.text[:300].replace('\n',' '))
    except Exception as e:
        print(u, type(e).__name__, e)
PY
```

<details><summary>💭 Thinking</summary>

**Accessed websites via curl and wget**

</details>

```json
{"search_query":[{"q":"site:parc.yolo.scapegoat.dev/note/research/kb/projects/go-go-goja go-go-goja"},{"q":"site:parc.yolo.scapegoat.dev/note/research/kb/projects/widget-dsl widget DSL"},{"q":"site:parc.yolo.scapegoat.dev/note/research/kb/projects/researchctl researchctl"},{"q":"\"go-go-goja\" \"widget-dsl\" researchctl"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched multiple sources for Parc pages and projects**

</details>

```json
{"search_query":[{"q":"site:github.com/go-go-golems \"widget-dsl\""},{"q":"site:github.com/go-go-golems researchctl"},{"q":"github go-go-golems widget dsl"},{"q":"github go-go-golems researchctl"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched GitHub, arxiv.org, and multiple other sources**

**Searched repositories and fetched project files and documentation**

</details>

```unknown
bash -lc set -e
mkdir -p /mnt/data/pattern-research
for spec in \
  'https://github.com/go-go-golems/go-go-goja.git go-go-goja main' \
  'https://github.com/go-go-golems/researchctl.git researchctl main' \
  'https://github.com/go-go-golems/go-go-parc.git go-go-parc main' \
  'https://github.com/go-go-golems/go-go-os-frontend.git go-go-os-frontend main'
do
  set -- $spec
  url=$1; dir=$2; branch=$3
  rm -rf /mnt/data/pattern-research/$dir
  if git clone --depth 1 --branch "$branch" "$url" "/mnt/data/pattern-research/$dir" >/tmp/clone-$dir.log 2>&1; then
    printf '%-20s ' "$dir"; git -C "/mnt/data/pattern-research/$dir" rev-parse --short=12 HEAD
  else
    echo "FAILED $dir"; tail -20 /tmp/clone-$dir.log
  fi
done
```

<details><summary>💭 Thinking</summary>

**Cloned repositories for pattern research**

**Fetched and examined Goja runtime and repository files**

</details>

The design is converging on a small semantic kernel with replaceable blocks for authority, staging, IR verification, lowering, scheduling, effects, lifecycle, evidence, and assurance.

<details><summary>💭 Thinking</summary>

**Fetched article content for Designing DSLs**

</details>

```unknown
bash -lc echo noop
```

<details><summary>💭 Thinking</summary>

**Identified article sections and headings**

**Searched and fetched content for fluent builder and CRM analysis**

**Designing a reusable architecture**

I’m focusing on identifying patterns from Tiny-IDP and related projects. I’ll outline a two-layer architecture for reusable components and draft language-agnostic primitives. I plan to propose APIs, composition rules, and a roadmap.

**Accessing sources and key insights**

I’ve reviewed the GitHub repos and research documents. Key concepts relate to explicit runtime ownership, module composition, and explicit boundaries in DSL and capability designs, which will inform the framework’s architecture and reusable patterns.

**Designed reusable architecture and accessed key insights**

**Designing an architecture**

I’m focusing on creating a detailed design for the user’s request. The broad scope suggests a formal report in Markdown, possibly PDF or DOCX, that cites research and Tiny-IDP sources. I’ll finalize the format and citations while inspecting updated files for accuracy.

**Designed an architecture**

**Designed Language Platform Construction Kit and inspected code**

</details>

```unknown
bash -lc git -C /mnt/data/tiny-idp rev-parse --abbrev-ref HEAD && git -C /mnt/data/tiny-idp rev-parse HEAD && find /mnt/data/tiny-idp/pkg/idpcontinuation -maxdepth 2 -type f -printf '%P
' | sort && find /mnt/data/tiny-idp/pkg/idpscript -maxdepth 2 -type f -printf '%P
' | sort | sed -n '1,120p'
```

<details><summary>💭 Thinking</summary>

**Inspected local Git repository**

**Searched files in GitHub repository via API**

</details>

```unknown
bash -lc ls -lah /mnt/data | sed -n '1,120p'
```

<details><summary>💭 Thinking</summary>

**Listed files in /mnt/data and produced report**

</details>

The architecture will ship as three layers: a pattern language, machine-checkable block/plan specifications, and reference implementations. Activated generations freeze their runtime universe while preserving build-time extensibility.

<details><summary>💭 Thinking</summary>

**Searched and inspected GitHub repository for runSpec examples**

</details>

```unknown
bash -lc cat > /mnt/data/langblocks-framework-design.md <<'EOF'
---
title: "LangBlocks"
subtitle: "A Language and Scripting Platform Construction Kit"
author: "Architecture synthesis from Tiny-IDP, go-go-goja, Widget DSL, and researchctl"
date: "2026-07-20"
status: "Design proposal / working specification"
---

# Executive summary

This document proposes **LangBlocks**, a two-level construction kit for building rigorous scriptable systems and language platforms:

1. **A language-neutral pattern and contract framework** for interpreter, compiler, workflow, capability, effect, continuation, lifecycle, and assurance design.
2. **A concrete Go and Goja reference implementation** that extracts and composes the strongest mechanisms already present in Tiny-IDP, go-go-goja, Widget DSL, researchctl, codesign, xgoja, and related projects.

The central abstraction is not "an embedded JavaScript runtime." It is a **kernelized language platform**:

```text
untrusted or flexible authoring
        -> canonical typed intent
        -> verified executable plan
        -> bounded invocation with leased authority
        -> closed control outcome
        -> host-interpreted effects
        -> native commit, persistence, or proof checking
```

The host remains responsible for authority, lifecycle, durable state, external effects, transactions, isolation, and final acceptance. The guest language owns policy, composition, calculations, tactics, recipes, and other intentionally flexible semantics.

This architecture already appears in several forms:

- Tiny-IDP separates JavaScript definitions, runtime-local callbacks, pure-Go program IR, invocation capabilities, closed outcomes, native effect commits, and restart-safe continuations.
- go-go-goja makes runtime ownership, current-call context, lifetime context, module composition, generated runtime plans, and host services explicit.
- Widget DSL separates semantic authoring, typed Widget IR, generic engines, fixed contracts, domain presets, and target renderers.
- researchctl separates a validated research graph from a deterministic execution workbench and imports generated evidence through an explicit transition rather than silently mutating authored state.

The common pattern can support a scriptable 3D editor, window manager, web application, compiler, firmware image, operating-system service layer, or proof-assistant tactic environment because the reusable core is about **staging, authority, state lifetime, interpretation, and verification**, not about JavaScript or identity.

The proposal deliberately consists of three products:

- a **pattern language** describing reusable architectural solutions and failure modes;
- a **machine-checkable block model and planner** that resolves, type-checks, freezes, fingerprints, and explains a platform composition;
- **reference libraries and profiles**, beginning with Go and Goja but admitting Lua, WASM, Python subprocesses, custom bytecode VMs, static firmware DSLs, and proof-producing tactic languages.

The most important constitutional rule is:

> A platform may be extensible while it is being assembled, but its runtime universe is closed for each activated generation.

Capabilities, callback IDs, effect kinds, outcome kinds, schemas, continuation targets, passes, target adapters, and native modules can be contributed by blocks before activation. The linker resolves and freezes them. Request-time execution cannot invent new authority or new semantic cases.

# 1. Why this should be a construction kit, not another scripting framework

Most scripting frameworks begin with a runtime and ask how to expose application APIs. That starting point is too low-level. It encourages a large ambient module surface, direct references to host objects, callbacks with unclear lifetime, and application-specific lifecycle code spread across every module.

The work under study suggests a different starting question:

> What semantic and authority boundaries must hold regardless of the guest language?

From that question, the runtime becomes one replaceable block among many. The platform must also define:

- how source becomes canonical meaning;
- how callbacks acquire durable names;
- how runtime-local identity is separated from durable identity;
- how capabilities are selected and leased;
- how effects are proposed, checked, and committed;
- how asynchronous work settles safely;
- how browser, user, device, or external waits become durable continuations;
- how hot reload interacts with persisted state;
- how diagnostics and provenance survive lowering;
- how a worker proves it is safe to reuse;
- how a generated host declares its exact module and authority profile;
- how tests, traces, models, and proof certificates relate to the production language.

A monolithic library would obscure these separations. LangBlocks should instead expose **small blocks, composition laws, and named profiles**. Some discoveries should become Go packages. Others should remain planner rules, conformance checks, pattern cards, or assurance guidance. Frameworkizing every insight as an interface would reproduce the complexity the project is intended to remove.

## 1.1 The three deliverables

### Deliverable A: the pattern language

Each pattern card should contain:

- problem and forces;
- boundary and invariant;
- implementation shape;
- state and authority consequences;
- common failure modes;
- valid variations;
- conformance tests;
- reference implementations;
- interactions with other patterns.

Examples include **Host-Owned Runtime**, **Deterministic Callback Linker**, **Invocation Capability Lease**, **Defunctionalized Continuation**, **Closed Outcome Algebra**, **Effect Plan and Native Commit**, **Quiescence Before Reuse**, and **Engine-Contract-Preset**.

### Deliverable B: the block specification and planner

A block publishes a versioned manifest describing its ports, phases, schemas, authority, effects, state lifetime, execution requirements, determinism contract, budgets, compatibility, diagnostics, and assurance hooks. A planner composes these manifests into a frozen `PlatformPlan`.

The planner is simultaneously:

- a dependency resolver;
- a phase scheduler;
- a type checker for ports and schemas;
- an effect and capability checker;
- a lifetime checker;
- a linker for stable IDs;
- a compatibility checker;
- a canonicalizer and fingerprint generator;
- an explanation engine for the final authority surface.

### Deliverable C: reference implementations and profiles

The first implementation should be Go-native and should reuse rather than replace existing go-go-goja components. Goja is then an adapter and a set of DSL/runtime blocks. Complete profiles demonstrate useful compositions:

- trusted interactive session;
- generated application host;
- bounded policy microkernel;
- durable workflow;
- deterministic simulation laboratory;
- declarative multi-target UI;
- static embedded system;
- proof-producing extension with a small checking kernel.

# 2. The cross-project pattern inventory

## 2.1 Tiny-IDP: scripting as a policy microkernel

Tiny-IDP provides the highest-assurance reference profile. Its serializable lambda contract includes input/output schemas, allowed outcomes, required capabilities, allowed effects, timeout, capability-call budget, and output-size budget. The contract contains the callback ID, never the callback function.

The source is evaluated in isolated Goja runtimes to construct a pure program and a runtime-local callback registry. Activation compares canonical program data, schemas, callback IDs, and fingerprints across independently materialized workers. Invocation builds a frozen context from JSON-derived data, request-scoped secrets, verified evidence, and only the declared capability bindings. A result must belong to a closed outcome family. Effects are inert plans until native code validates and commits them.

Browser-spanning work is represented by pure-Go continuation records. They contain a resume-handler ID, typed carry, exact program identity, revision, binding hashes, expiry, and native secret/evidence references. They expressly exclude Goja values, functions, Promises, and goroutine-local state.

The reusable ideas are:

- definition-time versus invocation-time staging;
- runtime-independent program IR;
- stable callback names linked to VM-local closures;
- deterministic activation;
- invocation-specific capability leases;
- structured resource budgets;
- frozen host/guest boundary values;
- opaque secret and evidence handles;
- closed outcomes and effects;
- native interpretation and atomic commit;
- explicit durable continuations;
- generation-pinned resumption;
- fail-stop worker leasing.

## 2.2 go-go-goja: runtime ownership and generated hosts

go-go-goja supplies the reusable runtime substrate. A runtime owner serializes `Call` and `Post` operations onto the VM-owning loop, tracks active work, and supports idle barriers and shutdown. `runtimebridge` distinguishes a runtime lifetime context from the context of the current owner entry. Native modules can inherit request cancellation, deadlines, and tracing metadata while runtime-owned work remains linked to the runtime lifetime.

The engine uses a mutable builder followed by an immutable factory. Module selection is composed as a deterministic set algebra with safe, only, add, exclude, and custom transformations. xgoja resolves selected providers, modules, sources, commands, artifacts, and settings into an embedded runtime plan. Provider packages contribute optional phase-specific capabilities rather than implementing one mega-interface. Host services are opaque to xgoja core and carry registered cleanup functions.

The reusable ideas are:

- single-owner mutable runtime;
- startup, current-call, and lifetime contexts;
- async work off-owner and settlement on-owner;
- immutable runtime factories;
- capability-set selection algebra;
- phase-specific provider capabilities;
- explicit host-service contribution and cleanup;
- build-plan versus runtime-plan separation;
- generated, focused hosts rather than ambient mega-runtimes;
- data-only defaults and explicit host-access modules.

## 2.3 Widget DSL: semantic authoring and target-owned interpretation

Widget DSL demonstrates that the same separation applies to presentation. Authors express semantic widgets and interaction intent. The system normalizes and validates those expressions into typed Widget IR. React, Storybook, generated hosts, and server-driven applications consume the same representation.

The strongest generalization is **engine-contract-preset**:

- a generic engine owns arrangement and interaction;
- a fixed plain-data contract connects the engine to displayed units;
- a domain preset supplies vocabulary and emits configured IR.

Because Widget IR must cross a network, callbacks become data. Actions, cell renderers, and field renderers are defunctionalized into tagged `ActionSpec`, `CellSpec`, and `FieldSpec` values interpreted by a target. The work also exposes important boundary details: field order must be captured before exporting a JavaScript object to an unordered Go map; grammar verbs should be precisely typed even when the renderer's final props are extensible; semantic, serialized, and visual tests are separate test layers.

The reusable ideas are:

- intent versus target implementation;
- typed, serializable IR;
- normalization and validation before rendering;
- target-owned policy such as style and layout;
- engine-contract-preset;
- defunctionalized interaction specs;
- recipes as high-level macros over stable IR;
- explicit DSL versions and migrations;
- boundary-order preservation;
- separate semantic, IR, and target-output tests.

## 2.4 researchctl: definition, execution, evidence, and promotion

researchctl separates a side-effect-free, validated research graph from an explicit experiment execution workbench. YAML, JSON, and JavaScript authoring converge on the same Go specification and validation path. Codesign runs deterministic simulations, emits event streams and manifests, and writes artifacts. Importing those artifacts back into the research graph is a separate, reviewable transition.

This yields several general patterns:

- multiple frontends converge on one canonical model;
- loading definitions does not execute experiments;
- deterministic execution produces durable evidence;
- authored state is not silently mutated by runtime state;
- event streams and manifests are first-class outputs;
- exploratory callbacks are useful, but stable behavior should be promoted into tested native device, policy, metric, or pass families.

The last item suggests a lifecycle for language-platform functionality: begin with a callback for exploration, constrain and observe it, defunctionalize it into a data contract, and finally promote common semantics into a native or verified block.

# 3. The LangBlocks constitution

The framework should be organized around system laws rather than convenience APIs. A profile may strengthen these laws, but it must not silently weaken them.

## Law 1: one owner for mutable interpreter state

A VM, compiler session, elaborator state, renderer session, or other mutable language engine has one explicit owner. Other threads or goroutines communicate through scheduled calls, posts, messages, or isolated instances.

This law is broader than Goja. An adapter may implement ownership with an event loop, actor mailbox, OS process, WASM store, lock, or single-core firmware scheduler. The contract is explicit even when the mechanism differs.

## Law 2: raw source is never the execution contract

Source is parsed and lowered through explicit stages. The runtime consumes a verified plan, executable artifact, or checked IR rather than partially normalized author input.

```text
source -> parse -> normalize -> verify -> lower -> link -> freeze -> execute
```

A small DSL may collapse some stages internally, but the conceptual boundaries remain observable and testable.

## Law 3: extensible at build time, closed at run time

Blocks may contribute schemas, callbacks, capabilities, effects, outcomes, passes, renderers, and continuation targets during composition. Activation freezes the registries. Every request-time semantic case is therefore enumerable and can be interpreted exhaustively.

## Law 4: no ambient authority

A script receives only authority selected by its profile and bound for its scope. A module existing in the binary does not imply that every runtime or invocation can use it.

## Law 5: authority is leased, not merely exposed

Powerful operations are represented by scoped leases with an active state, owner, lifetime, budgets, cancellation, audit identity, and optional replay behavior. Retaining a function reference does not retain authority after the lease closes.

## Law 6: no raw references across lifetime boundaries

VM values, closures, pointers, file descriptors, Go objects, thread-local state, and other ephemeral references cannot enter canonical program data, durable continuations, generated manifests, or cross-process messages.

Cross-lifetime values must be one of:

- canonical inline data;
- a content-addressed immutable artifact;
- a stable host reference with an explicit resolver;
- an opaque handle whose scope does not cross the boundary.

## Law 7: scripts propose privileged effects; kernels commit them

A guest may calculate or request effects, but a domain kernel validates the effect schema, ordering, authority, invariants, transaction group, idempotency, and audit policy before changing authoritative state.

Direct host operations remain possible in lower-assurance profiles, but they are explicit capability types rather than the default semantics.

## Law 8: durable waits are explicit control-state records

A wait that outlives an invocation, process, firmware scheduling quantum, user interaction, or runtime generation becomes a versioned continuation record with a stable entry label and typed environment. The framework does not depend on serializing a VM stack or closure heap.

## Law 9: persisted meaning is generation-aware

A continuation, cached plan, proof state, incremental compiler checkpoint, or session replay has an explicit relationship to the source and semantic generation that created it. "Resume under latest code" is never an accidental default.

## Law 10: quiescence precedes reuse

A pooled runtime returns to service only after a positive safety check. No pending Promise settlement, capability task, timer, event delivery, interrupt, borrowed handle, or invocation context may remain. Failure to prove safety poisons the instance.

## Law 11: nondeterminism is named

Clock, randomness, scheduling, environment variables, file systems, networks, device input, and external services are declared sources. A profile may prohibit them, inject them as capabilities, record them for replay, or accept them. "Deterministic" is a vector of properties, not a Boolean marketing label.

## Law 12: diagnostics are typed outputs

Diagnostics have stable IDs, severity, source location, semantic path, related locations, notes, and provenance. Their ordering is deterministic. Panics and ad hoc strings are converted at a boundary into structured problems.

## Law 13: evidence import and authoritative mutation are distinct transitions

Execution can emit traces, metrics, proof terms, manifests, rendered output, or proposed patches. Promoting those outputs into authoritative state is a separate checked operation.

## Law 14: isolation is independent from capability design

A narrow API surface reduces authority, but it does not make an in-process interpreter safe against adversarial native-memory attacks, denial of service, side channels, or engine vulnerabilities. The execution envelope is a separate block: in-process trusted, WASM, subprocess, container, microVM, privilege domain, or hardware isolation.

# 4. A language-neutral abstract machine

LangBlocks can be modeled as a small staged machine. The guest-language adapter supplies compilation, instantiation, invocation, interruption, quiescence, and disposal. The host kernel supplies plan validation, authority binding, outcome interpretation, effects, durability, and generation management.

```text
BUILD PLANE
  SourceBundle
      -> FrontendResult
      -> NormalizedModel
      -> VerifiedIR
      -> LoweredPlan
      -> LinkedArtifact
      -> canonical fingerprints

ACTIVATION PLANE
  LinkedArtifact + RuntimePlan
      -> RuntimeInstance(s)
      -> DefinitionSnapshot(s)
      -> registry/fingerprint comparison
      -> ActivatedGeneration

INVOCATION PLANE
  Generation + EntryID + TypedInput
      + CapabilityLease + InvocationBudget
      -> frozen CallFrame
      -> guest invocation
      -> PortableOutcome + InvocationReport

INTERPRETATION PLANE
  PortableOutcome
      -> immediate next entry
      | terminal value
      | durable continuation
      | event emission
      | effect plan
      | typed denial/fault

COMMIT PLANE
  EffectPlan
      -> schema/authority/invariant validation
      -> transaction and/or outbox
      -> audit/evidence

DURABILITY PLANE
  ContinuationRecord + revision + generation identity
      -> compare-and-advance / consume / revoke / migrate
      -> fresh invocation

OBSERVATION PLANE
  source maps + traces + event streams + manifests
      -> diagnostics, replay, model checking, reports, evidence import
```

## 4.1 The core transition

At the most general level, a handler is interpreted as:

```text
invoke : (generation, entry, input, capability lease, budget)
      -> (outcome, trace, diagnostics)
```

The host then applies:

```text
interpret : (platform plan, outcome)
         -> next invocation
          | suspension record
          | validated effect transaction
          | terminal result
```

The language adapter never decides what an authoritative effect means. The domain kernel never needs to know how a JavaScript closure, Lua function, WASM export, proof tactic, or compiler plugin is represented internally.

## 4.2 State classes

Every value and handle should declare its state class:

| State class | Typical contents | May contain engine-native references? | Durable? |
|---|---|---:|---:|
| Source | source files, source maps | no | yes |
| Definition | builders, temporary callbacks | only inside definition instance | no |
| Canonical program | schemas, IDs, graphs, contracts | no | yes |
| Generation | activated artifacts and registries | runtime-private only | retained, not serialized as VM state |
| Runtime instance | globals, closures, module state | yes | no |
| Session | live state plus replay/checkpoint policy | profile-dependent | history/checkpoint only |
| Invocation | input, leases, secrets, pending async work | yes, scope-bound | no |
| Continuation | entry label, typed environment, references | no raw engine values | yes |
| Effect plan | inert proposed operations | stable refs only | usually yes/auditable |
| External state | database, scene, OS, theorem environment | host-owned | yes |
| Evidence | traces, events, manifests, certificates | no | yes |

The planner and codecs should reject illegal state-class crossings. This is a more useful invariant than a generic "serializable" flag because it explains *why* a value may or may not cross a boundary.

# 5. The block meta-model

A block is a reusable contribution to one or more platform phases. It is not necessarily a runtime module. A schema registry, normalization pass, IR verifier, capability provider, effect handler, continuation store, target renderer, model exporter, and diagnostic formatter are all blocks.

## 5.1 Block descriptor

A language-neutral descriptor should contain at least:

```go
type BlockDescriptor struct {
    ID            QualifiedID
    Version       Version
    Kind          BlockKind
    Phases        []Phase

    Inputs        []Port
    Outputs       []Port

    Requires      RequirementSet
    Provides      ProvisionSet

    State         StateContract
    Execution     ExecutionContract
    Determinism   DeterminismContract
    Budgets       BudgetContract
    Security      SecurityContract
    Compatibility CompatibilityContract
    Assurance     AssuranceContract
}
```

A port includes:

```go
type Port struct {
    Name         string
    Type         TypeRef
    Schema       SchemaRef
    Cardinality  Cardinality
    Lifetime     StateClass
    Encoding     EncodingRef
    Sensitivity  Sensitivity
    Mutability   Mutability
    Ownership    OwnershipMode
}
```

Requirements and provisions are namespaced and versioned:

- capabilities;
- host services;
- effect kinds;
- outcome kinds;
- schemas and IR dialects;
- callback classes;
- continuation targets;
- target adapters;
- artifact stores;
- transaction services;
- model or certificate checkers.

## 5.2 Block kinds

The initial block vocabulary should remain small but cover the complete lifecycle:

- `frontend` - parse or evaluate an authoring language;
- `normalizer` - default, canonicalize, resolve names, accumulate warnings;
- `verifier` - check structural or semantic invariants;
- `lowering-pass` - translate one IR/dialect to another;
- `linker` - resolve stable IDs and registries;
- `generator` - emit source, declarations, binaries, firmware tables, or assets;
- `language-adapter` - compile, instantiate, invoke, interrupt, quiesce, dispose;
- `runtime-module` - add guest-visible vocabulary;
- `capability-provider` - bind scoped host authority;
- `effect-handler` - validate and apply one effect family;
- `outcome-handler` - interpret one control outcome family;
- `continuation-codec` and `continuation-store`;
- `scheduler` and `execution-envelope`;
- `target` - render or execute portable IR;
- `observer` - trace, metrics, audit, provenance;
- `verifier-language` - materialize data-only scenarios or proofs;
- `migration` - transform versioned canonical state.

## 5.3 Composition checks

The planner accepts a graph only when all of the following hold:

1. block IDs and contributed semantic IDs are unique;
2. version constraints resolve exactly;
3. input ports are supplied by compatible output ports;
4. phase order is acyclic and complete;
5. required capabilities and services are provided;
6. no block requests authority prohibited by the profile;
7. a lowering pass cannot silently increase authority or sensitivity;
8. effect kinds are handled and permitted by each invoking entry;
9. outcome kinds are handled and permitted by each invoking entry;
10. continuation targets exist and accept the declared environment schema;
11. durable ports use durable encodings and contain no ephemeral handles;
12. thread-affinity and reentrancy requirements can be satisfied;
13. resource budgets are bounded where the profile requires bounds;
14. nondeterminism sources are allowed, injected, or recordable;
15. migrations cover persisted schema changes where required;
16. diagnostics and source maps can be propagated across passes;
17. the final registry order and plan encoding are canonical.

## 5.4 The freeze point

After composition, `Freeze()` produces an immutable `PlatformPlan`:

```go
type PlatformPlan struct {
    SchemaVersion string
    ProfileID     string
    Blocks        []ResolvedBlock
    PhaseGraph    []ResolvedPhase
    Registries    FrozenRegistries
    Authority     AuthorityGraph
    Lifetimes     LifetimeGraph
    Targets       []ResolvedTarget
    Fingerprints  PlanFingerprints
}
```

The plan is the semantic manifest of the platform. Generated binaries, runtime pools, firmware images, test harnesses, documentation, and formal models should all be derived from it. No runtime-global registry should be treated as authoritative after the plan is frozen.

EOF
```

<details><summary>💭 Thinking</summary>

**Created LangBlocks design proposal report and appended sections**

</details>

```unknown
bash -lc set -euo pipefail
rm -rf /mnt/data/langblocks-design-kit
mkdir -p /mnt/data/langblocks-design-kit
cat > /mnt/data/langblocks-design-kit/go.mod <<'EOF'
module example.com/langblocks-design-kit

go 1.22
EOF
cat > /mnt/data/langblocks-design-kit/model.go <<'EOF'
// Package langblocks is a compilable design scaffold for the proposed
// language-platform construction kit. It is not a production implementation.
package langblocks

import (
	"context"
	"time"
)

type QualifiedID string
type Version string
type TypeRef string
type SchemaRef string
type EncodingRef string
type GenerationID string
type EntryID string
type CapabilityID string
type EffectTypeID string
type OutcomeTypeID string
type ArtifactID string
type ContinuationHandle string

type Phase string

const (
	PhaseAuthor     Phase = "author"
	PhaseNormalize  Phase = "normalize"
	PhaseVerify     Phase = "verify"
	PhaseLower      Phase = "lower"
	PhaseLink       Phase = "link"
	PhaseActivate   Phase = "activate"
	PhaseInvoke     Phase = "invoke"
	PhaseInterpret  Phase = "interpret"
	PhaseCommit     Phase = "commit"
	PhaseResume     Phase = "resume"
	PhaseObserve    Phase = "observe"
	PhaseRetire     Phase = "retire"
)

type BlockKind string

type StateClass string

const (
	StateSource       StateClass = "source"
	StateDefinition   StateClass = "definition"
	StateCanonical    StateClass = "canonical-program"
	StateGeneration   StateClass = "generation"
	StateRuntime      StateClass = "runtime-instance"
	StateSession      StateClass = "session"
	StateInvocation   StateClass = "invocation"
	StateContinuation StateClass = "continuation"
	StateEffect       StateClass = "effect-plan"
	StateEvidence     StateClass = "evidence"
)

type Sensitivity string

const (
	SensitivityPublic    Sensitivity = "public"
	SensitivityInternal  Sensitivity = "internal"
	SensitivitySensitive Sensitivity = "sensitive"
	SensitivitySecret    Sensitivity = "secret"
)

type SourceLocation struct {
	File   string `json:"file,omitempty"`
	Line   int    `json:"line,omitempty"`
	Column int    `json:"column,omitempty"`
}

type Diagnostic struct {
	ID       string           `json:"id"`
	Severity string           `json:"severity"`
	Message  string           `json:"message"`
	Path     string           `json:"path,omitempty"`
	Location SourceLocation   `json:"location,omitempty"`
	Related  []SourceLocation `json:"related,omitempty"`
	Notes    []string         `json:"notes,omitempty"`
}

type Diagnostics []Diagnostic

type ArtifactRef struct {
	ID       ArtifactID  `json:"id"`
	Hash     string      `json:"hash"`
	Size     int64       `json:"size"`
	Type     TypeRef     `json:"type"`
	Encoding EncodingRef `json:"encoding"`
}

type PortableValue struct {
	Type        TypeRef      `json:"type"`
	Schema      SchemaRef    `json:"schema"`
	Encoding    EncodingRef  `json:"encoding"`
	Inline      []byte       `json:"inline,omitempty"`
	Artifact    *ArtifactRef `json:"artifact,omitempty"`
	Sensitivity Sensitivity  `json:"sensitivity"`
	Provenance  string       `json:"provenance,omitempty"`
}

type Port struct {
	Name        string      `json:"name"`
	Type        TypeRef     `json:"type"`
	Schema      SchemaRef   `json:"schema,omitempty"`
	Lifetime    StateClass  `json:"lifetime"`
	Encoding    EncodingRef `json:"encoding,omitempty"`
	Sensitivity Sensitivity `json:"sensitivity"`
	Cardinality string      `json:"cardinality,omitempty"`
	Mutability  string      `json:"mutability,omitempty"`
	Ownership   string      `json:"ownership,omitempty"`
}

type RequirementSet struct {
	Capabilities []CapabilityID `json:"capabilities,omitempty"`
	Effects      []EffectTypeID  `json:"effects,omitempty"`
	Outcomes     []OutcomeTypeID `json:"outcomes,omitempty"`
	Services     []QualifiedID   `json:"services,omitempty"`
	Schemas      []SchemaRef     `json:"schemas,omitempty"`
	Dialects     []TypeRef       `json:"dialects,omitempty"`
}

type ProvisionSet RequirementSet

type StateContract struct {
	Lifetime       StateClass `json:"lifetime"`
	Persistence    string     `json:"persistence"`
	Restore        string     `json:"restore,omitempty"`
	ContentAddress bool       `json:"contentAddressed,omitempty"`
}

type ExecutionContract struct {
	Ownership     string `json:"ownership"`
	ThreadAffinity string `json:"threadAffinity,omitempty"`
	Reentrancy    string `json:"reentrancy,omitempty"`
	Isolation     string `json:"isolation"`
	Quiescence    string `json:"quiescence,omitempty"`
	Cancellation  string `json:"cancellation,omitempty"`
}

type DeterminismContract struct {
	Definition  string   `json:"definition"`
	Compilation string   `json:"compilation"`
	Invocation  string   `json:"invocation"`
	Scheduling  string   `json:"scheduling"`
	Sources     []string `json:"sources,omitempty"`
}

type BudgetContract struct {
	Timeout         time.Duration `json:"timeout"`
	MaxCalls        int64         `json:"maxCalls,omitempty"`
	MaxInputBytes   int64         `json:"maxInputBytes,omitempty"`
	MaxOutputBytes  int64         `json:"maxOutputBytes,omitempty"`
	MaxMemoryBytes  int64         `json:"maxMemoryBytes,omitempty"`
	MaxInstructions int64         `json:"maxInstructions,omitempty"`
}

type SecurityContract struct {
	Trust       string   `json:"trust"`
	Authorities []string `json:"authorities,omitempty"`
	Secrets     string   `json:"secrets,omitempty"`
	Audit       string   `json:"audit,omitempty"`
}

type CompatibilityContract struct {
	PlatformRange string   `json:"platformRange,omitempty"`
	StateVersion  string   `json:"stateVersion,omitempty"`
	Migrations    []string `json:"migrations,omitempty"`
	ResumePolicy  string   `json:"resumePolicy,omitempty"`
}

type AssuranceContract struct {
	Invariants   []string `json:"invariants,omitempty"`
	Conformance  []string `json:"conformance,omitempty"`
	ModelExport  string   `json:"modelExport,omitempty"`
	Certificate  TypeRef  `json:"certificate,omitempty"`
}

type BlockDescriptor struct {
	ID            QualifiedID          `json:"id"`
	Version       Version              `json:"version"`
	Kind          BlockKind            `json:"kind"`
	Phases        []Phase              `json:"phases"`
	Inputs        []Port               `json:"inputs,omitempty"`
	Outputs       []Port               `json:"outputs,omitempty"`
	Requires      RequirementSet       `json:"requires,omitempty"`
	Provides      ProvisionSet         `json:"provides,omitempty"`
	State         StateContract        `json:"state"`
	Execution     ExecutionContract    `json:"execution"`
	Determinism   DeterminismContract  `json:"determinism"`
	Budgets       BudgetContract       `json:"budgets,omitempty"`
	Security      SecurityContract     `json:"security"`
	Compatibility CompatibilityContract `json:"compatibility,omitempty"`
	Assurance     AssuranceContract    `json:"assurance,omitempty"`
}

type ResolvedBlock struct {
	Descriptor BlockDescriptor `json:"descriptor"`
	Order      int             `json:"order"`
}

type PlanFingerprints struct {
	Source       string `json:"source,omitempty"`
	Model        string `json:"model,omitempty"`
	Schemas      string `json:"schemas,omitempty"`
	Callbacks    string `json:"callbacks,omitempty"`
	Capabilities string `json:"capabilities,omitempty"`
	Effects      string `json:"effects,omitempty"`
	Plan         string `json:"plan"`
}

type PlatformPlan struct {
	SchemaVersion string            `json:"schemaVersion"`
	ProfileID     string            `json:"profileId"`
	Blocks        []ResolvedBlock   `json:"blocks"`
	Fingerprints  PlanFingerprints  `json:"fingerprints"`
}

type SourceFile struct {
	Path    string `json:"path"`
	Content []byte `json:"content"`
}

type SourceBundle struct {
	Files []SourceFile `json:"files"`
	Entry string       `json:"entry"`
}

type CompileRequest struct {
	Plan PlatformPlan `json:"plan"`
}

type ExecutableArtifact struct {
	Ref          ArtifactRef      `json:"ref"`
	Fingerprints PlanFingerprints `json:"fingerprints"`
}

type InstancePlan struct {
	Generation GenerationID `json:"generation"`
	Plan       PlatformPlan `json:"plan"`
}

type DefinitionRequest struct {
	Compare []string `json:"compare"`
}

type CallbackRegistration struct {
	ID             string         `json:"id"`
	Class          string         `json:"class"`
	InputSchema    SchemaRef      `json:"inputSchema"`
	OutputSchema   SchemaRef      `json:"outputSchema"`
	Capabilities   []CapabilityID `json:"capabilities,omitempty"`
	Effects        []EffectTypeID `json:"effects,omitempty"`
	Outcomes       []OutcomeTypeID `json:"outcomes,omitempty"`
	SourceLocation SourceLocation `json:"sourceLocation,omitempty"`
}

type DefinitionSnapshot struct {
	Program      PortableValue          `json:"program"`
	Callbacks    []CallbackRegistration `json:"callbacks"`
	Fingerprints PlanFingerprints       `json:"fingerprints"`
}

type InvocationBudget struct {
	Timeout        time.Duration `json:"timeout"`
	CapabilityCalls int64        `json:"capabilityCalls"`
	OutputBytes    int64         `json:"outputBytes"`
}

type InvocationRequest struct {
	Generation   GenerationID      `json:"generation"`
	Entry        EntryID           `json:"entry"`
	Input        PortableValue     `json:"input"`
	Capabilities CapabilitySet     `json:"-"`
	Budget       InvocationBudget  `json:"budget"`
}

type OutcomeEnvelope struct {
	Kind         OutcomeTypeID         `json:"kind"`
	Payload      PortableValue         `json:"payload"`
	Continuation *ContinuationProposal `json:"continuation,omitempty"`
	Effects      []EffectEnvelope      `json:"effects,omitempty"`
}

type QuiescenceReport struct {
	PendingCapabilities int           `json:"pendingCapabilities"`
	PendingPromises     int           `json:"pendingPromises"`
	PendingTimers       int           `json:"pendingTimers"`
	PendingEvents       int           `json:"pendingEvents"`
	BorrowedHandles     int           `json:"borrowedHandles"`
	InterruptPending    bool          `json:"interruptPending"`
	LeaseClosed         bool          `json:"leaseClosed"`
	Diagnostics         Diagnostics   `json:"diagnostics,omitempty"`
}

type InvocationReport struct {
	StartedAt   time.Time        `json:"startedAt"`
	FinishedAt  time.Time        `json:"finishedAt"`
	Quiescence  QuiescenceReport `json:"quiescence"`
	Reusable    bool             `json:"reusable"`
	PoisonCause string           `json:"poisonCause,omitempty"`
}

type InvocationResult struct {
	Outcome OutcomeEnvelope `json:"outcome"`
	Report  InvocationReport `json:"report"`
}

type InterruptReason struct {
	Code    string `json:"code"`
	Message string `json:"message,omitempty"`
}

type AdapterDescriptor struct {
	ID                     QualifiedID `json:"id"`
	Version                Version     `json:"version"`
	SupportsAsync          bool        `json:"supportsAsync"`
	SupportsInterrupt      bool        `json:"supportsInterrupt"`
	SupportsReuse          bool        `json:"supportsReuse"`
	SupportsSourceMaps     bool        `json:"supportsSourceMaps"`
	SupportsDeterministicDefinition bool `json:"supportsDeterministicDefinition"`
}

type LanguageAdapter interface {
	Descriptor() AdapterDescriptor
	Compile(context.Context, SourceBundle, CompileRequest) (ExecutableArtifact, Diagnostics)
	Instantiate(context.Context, ExecutableArtifact, InstancePlan) (LanguageInstance, error)
}

type LanguageInstance interface {
	Materialize(context.Context, DefinitionRequest) (DefinitionSnapshot, error)
	Invoke(context.Context, InvocationRequest) (InvocationResult, error)
	Interrupt(InterruptReason) error
	Quiesce(context.Context) (QuiescenceReport, error)
	Close(context.Context) error
}

type OwnerState string

type Owner[T any] interface {
	Call(context.Context, string, func(context.Context, T) (any, error)) (any, error)
	Post(context.Context, string, func(context.Context, T)) error
	Barrier(context.Context) error
	Shutdown(context.Context) error
	State() OwnerState
}

type CapabilityDescriptor struct {
	ID             CapabilityID `json:"id"`
	Version        Version      `json:"version"`
	Input          SchemaRef    `json:"input"`
	Output         SchemaRef    `json:"output"`
	Scope          string       `json:"scope"`
	AuthorityClass string       `json:"authorityClass"`
	Determinism    string       `json:"determinism"`
	Limits         BudgetContract `json:"limits"`
}

type BindingRequest struct {
	Generation GenerationID `json:"generation"`
	Entry      EntryID      `json:"entry"`
	Scope      string       `json:"scope"`
}

type CapabilityUsage struct {
	Calls       int64 `json:"calls"`
	InputBytes  int64 `json:"inputBytes"`
	OutputBytes int64 `json:"outputBytes"`
}

type CapabilityLease interface {
	Descriptor() CapabilityDescriptor
	Invoke(context.Context, PortableValue) (PortableValue, error)
	Usage() CapabilityUsage
	Close() error
}

type CapabilityProvider interface {
	Descriptor() CapabilityDescriptor
	Bind(context.Context, BindingRequest) (CapabilityLease, error)
}

type CapabilitySet interface {
	Lookup(CapabilityID) (CapabilityLease, bool)
	Close() error
}

type EffectEnvelope struct {
	Kind    EffectTypeID `json:"kind"`
	Payload PortableValue `json:"payload"`
	IdempotencyKey string `json:"idempotencyKey,omitempty"`
}

type EffectDescriptor struct {
	ID                 EffectTypeID `json:"id"`
	Version            Version      `json:"version"`
	Payload            SchemaRef    `json:"payload"`
	TransactionFamily  string       `json:"transactionFamily"`
	Externality        string       `json:"externality"`
	Idempotency        string       `json:"idempotency"`
	Certificate        TypeRef      `json:"certificate,omitempty"`
}

type EffectContext struct {
	Generation GenerationID `json:"generation"`
	Entry      EntryID       `json:"entry"`
}

type Transaction interface {
	Commit(context.Context) error
	Rollback(context.Context) error
}

type EffectHandler interface {
	Descriptor() EffectDescriptor
	Validate(context.Context, EffectEnvelope, EffectContext) Diagnostics
	Apply(context.Context, Transaction, EffectEnvelope) error
}

type OutcomeDescriptor struct {
	ID      OutcomeTypeID `json:"id"`
	Version Version       `json:"version"`
	Payload SchemaRef     `json:"payload"`
}

type KernelAction struct {
	Kind    string        `json:"kind"`
	Payload PortableValue `json:"payload"`
}

type KernelContext struct {
	Generation GenerationID `json:"generation"`
	Entry      EntryID       `json:"entry"`
}

type OutcomeHandler interface {
	Descriptor() OutcomeDescriptor
	Interpret(context.Context, OutcomeEnvelope, KernelContext) (KernelAction, Diagnostics)
}

type ContinuationProposal struct {
	Entry       EntryID       `json:"entry"`
	Environment PortableValue `json:"environment"`
	ExpiresIn   time.Duration `json:"expiresIn"`
}

type ContinuationStatus string

type BindingDigest struct {
	Kind string `json:"kind"`
	Hash []byte `json:"hash"`
}

type DurableRef struct {
	Kind string `json:"kind"`
	ID   string `json:"id"`
}

type TerminalRecord struct {
	Kind string        `json:"kind"`
	Data PortableValue `json:"data"`
	At   time.Time     `json:"at"`
}

type ContinuationRecord struct {
	RecordVersion    uint32             `json:"recordVersion"`
	HandleHash       []byte             `json:"handleHash"`
	Generation       GenerationID       `json:"generation"`
	Entry            EntryID            `json:"entry"`
	Environment      PortableValue      `json:"environment"`
	Bindings         []BindingDigest    `json:"bindings,omitempty"`
	StableReferences []DurableRef       `json:"stableReferences,omitempty"`
	Revision         uint64             `json:"revision"`
	CreatedAt        time.Time          `json:"createdAt"`
	ExpiresAt        time.Time          `json:"expiresAt"`
	Status           ContinuationStatus `json:"status"`
	Terminal         *TerminalRecord    `json:"terminal,omitempty"`
}

type ContinuationStore interface {
	Create(context.Context, ContinuationRecord) error
	Load(context.Context, ContinuationHandle) (ContinuationRecord, error)
	CompareAndAdvance(context.Context, ContinuationHandle, uint64, ContinuationRecord) error
	Consume(context.Context, ContinuationHandle, uint64, TerminalRecord) error
	Revoke(context.Context, ContinuationHandle, string) error
	CountByGeneration(context.Context, GenerationID) (int64, error)
}
EOF
cat > /mnt/data/langblocks-design-kit/platform.example.yaml <<'EOF'
apiVersion: langblocks.dev/v1alpha1
kind: PlatformProfile
metadata:
  name: scripted-window-manager

runtime:
  adapter: goja
  lifetime: pooled-ephemeral
  isolation: in-process-operator-trusted
  owner: event-loop
  reuse:
    requireQuiescence: true
    onUncertainCleanup: discard

composition:
  modules:
    policy: only
    include:
      - lang.core@1
      - wm.intent@1
  capabilities:
    - id: wm.snapshot.read
      version: 1
      scope: invocation
      limits:
        calls: 4
        inputBytes: 4096
        outputBytes: 65536
  effects:
    - wm.window.move@1
    - wm.window.resize@1
    - wm.window.focus@1
    - wm.process.spawn@1

entries:
  - id: wm.window-created
    callbackClass: event-handler
    inputSchema: wm/event/window-created@1
    outputSchema: wm/outcome@1
    capabilities:
      - wm.snapshot.read@1
    outcomes:
      - effects@1
      - reject@1
      - fault@1
    effects:
      - wm.window.move@1
      - wm.window.resize@1
      - wm.window.focus@1
    budget:
      timeout: 20ms
      capabilityCalls: 4
      outputBytes: 32768

generation:
  activation:
    materializations: 3
    compare:
      - program
      - callbacks
      - schemas
      - modules
  hotReload: side-by-side
  retainedStatePolicy: exact-generation

observability:
  trace: structured
  manifests: true
EOF
cat > /mnt/data/langblocks-design-kit/README.md <<'EOF'
# LangBlocks design kit

This directory is a **design scaffold**, not a released framework.

It contains:

- `model.go`: compilable Go type/interface sketches for the language-neutral core;
- `platform.example.yaml`: an illustrative frozen-profile input for a scriptable window manager;
- `go.mod`: allows the scaffold to be compiled with `go test ./...`.

The complete architecture, extraction plan, pattern catalogue, profile design, and conformance strategy are in `../langblocks-framework-design.md`.
EOF
cd /mnt/data/langblocks-design-kit
gofmt -w model.go
go test ./...
cd /mnt/data
zip -qr langblocks-design-kit.zip langblocks-design-kit
ls -lh /mnt/data/langblocks-design-kit.zip /mnt/data/langblocks-design-kit/model.go /mnt/data/langblocks-design-kit/platform.example.yaml

```

<details><summary>💭 Thinking</summary>

**Created design kit and validated dependencies and files**

</details>

```json
{"paths":["GitHub"],"query":"search_repositories"}
```

```json
{"uri":"/response/turn23","query":"filename","start_line":1}
```

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

<details><summary>💭 Thinking</summary>

**Searching for descriptors in go-go-goja repository**

</details>

