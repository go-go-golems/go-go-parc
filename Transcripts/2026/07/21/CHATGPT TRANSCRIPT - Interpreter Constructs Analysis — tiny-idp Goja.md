# Interpreter Constructs Analysis

- URL: https://chatgpt.com/c/6a5e08c8-8040-83ea-9d7b-750535bf03ff
- Created: 2026-07-20T11:38:48.954Z

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

</details>

<details><summary>💭 Thinking</summary>

**Searched GitHub repo for specific ticket content**

</details>

<details><summary>💭 Thinking</summary>

**Researching GitHub files**

I’m exploring how to dig deeper into a project by examining files, likely from a Git branch. I’ll gather details, focusing on specific package scripts and documentation or design analysis.

**Researched GitHub files**

</details>

<details><summary>💭 Thinking</summary>

**Searched files for package declarations and fetched design documents**

</details>

<details><summary>💭 Thinking</summary>

**Searched for package references, classes, and functions in repository**

</details>

The branch reveals a lambda-first workflow machine: Goja-free serialized IR uses stable callback IDs, while browser waits persist versioned continuations that resume fresh, capability-bounded invocations.

<details><summary>💭 Thinking</summary>

**Fetched commit metadata, diffs, and related file content**

</details>

<details><summary>💭 Thinking</summary>

**Evaluated Goja interpreter architecture and searched recent commits**

</details>

<details><summary>💭 Thinking</summary>

**Organizing file citation**

I’m planning to fetch and organize files from GitHub, keeping track of line numbers for proper citations. I'll create a markdown report, using permanent links for sources and commit references.

**Organized file citation**

</details>

<details><summary>💭 Thinking</summary>

**Fetched file content and calculated line count**

</details>

<details><summary>💭 Thinking</summary>

**Fetched and validated files and code from repository**

</details>

<details><summary>💭 Thinking</summary>

**Fetched value.go, providers.go, and diagnostics.go files**

</details>

<details><summary>💭 Thinking</summary>

**Fetched file and module content, built workflow components**

</details>

<details><summary>💭 Thinking</summary>

**Fetched compiler and runtime factory file content from repository**

</details>

<details><summary>💭 Thinking</summary>

**Fetched and analyzed files and capabilities for settlement tracking**

</details>

<details><summary>💭 Thinking</summary>

**Fetched continuation types and file content from repository**

</details>

<details><summary>💭 Thinking</summary>

**Preparing report on TINYIDP**

I’m synthesizing findings from GitHub, focusing on constructs like serialized continuations, invocation capabilities, and callback registration. The report will include precise file citations and reflect the clinical tone required.

**Preparing tiny-idp monograph**

I’m planning to write a detailed Markdown monograph analyzing TINYIDP's interpreter constructs, callback registration, and continuations. I’ll focus on code references and keep citations accurate, considering PDF output later.

**Prepared report and monograph on TINYIDP**

</details>

<details><summary>💭 Thinking</summary>

**Fetched files and content from GitHub for analysis and submission**

</details>

<details><summary>💭 Thinking</summary>

**Fetched file content from GitHub repository**

</details>

<details><summary>💭 Thinking</summary>

**Fetched and inspected repository files for implementation details**

</details>

<details><summary>💭 Thinking</summary>

**Fetched and evaluated GitHub files for advanced Goja analysis**

</details>

```unknown
bash -lc cat /home/oai/skills/pdfs/SKILL.md
```

The key enforcement pattern is now clear: deterministic registration is checked across isolated runtimes, while opaque JavaScript executes within declared schemas, budgets, capabilities, outcomes, and native-committed effects.

<details><summary>💭 Thinking</summary>

**Read skill from PDF and checked required installations**

</details>

<details><summary>💭 Thinking</summary>

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

</details>

<details><summary>💭 Thinking</summary>

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

> [image: sediment://file_000000009894822fa5752f0939482f75]
> [image: sediment://file_00000000a0d481f5891a705ed1fdc59b]
> Now write a detailed document that digs into each of these concepts, backed by existing research, textbooks and theory.

<details><summary>💭 Thinking</summary>

**Planning detailed document**

The user wants a detailed, researched document on specific concepts, likely involving citations from textbooks and existing theory. I’ll need to gather relevant sources, and explore prior files and external references.

**Planned a detailed document**

</details>

```unknown
bash -lc cat /home/oai/skills/docx/SKILL.md && printf '
---PDF---
' && cat /home/oai/skills/pdfs/SKILL.md
```

<details><summary>💭 Thinking</summary>

**Created document with research, citations, and source files**

</details>

<details><summary>💭 Thinking</summary>

**Gathering literature sources**

I’ll focus on collecting precise, scholarly sources like research papers, textbooks, and official publications for the user. I'll ensure citations from primary sources like DOIs, ACM, and Springer for accuracy.

**Gathered literature sources**

</details>

<details><summary>💭 Thinking</summary>

**Finding relevant literature**

I’ll gather literature that spans multiple areas like nominal branding, effect systems, and runtime typing. I’ll focus on textbooks and important research papers for citations, especially for the user’s requested concepts.

**Found relevant literature**

</details>

<details><summary>💭 Thinking</summary>

**Exploring key concepts**

I’m organizing a range of ideas like object-capability security, algebraic effect handlers, and algebraic operations, while gathering foundational references and examples on each concept for a more thorough approach.

**Explored key concepts**

</details>

```json
{"search_query":[{"q":"John C. Reynolds Definitional Interpreters for Higher-Order Programming Languages 1972 DOI"},{"q":"Danvy Nielsen Defunctionalization at Work 2001 PDF"},{"q":"Christian Queinnec continuations web servers browsers 2000 paper"},{"q":"Lucassen Gifford Polymorphic Effect Systems POPL 1988 DOI"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched for programming theories, contracts, resources, and papers**

</details>

<details><summary>💭 Thinking</summary>

**Planning document creation**

I’m planning to produce a detailed document, building upon the provided images and prior monographs, with citations and research. I’ll gather related theory, literature, and textbooks to ensure depth and accuracy.

**Gathering theoretical foundations**

I’m looking up key sources for each concept mentioned. I need to verify relevant research and theories for defunctionalization, object capabilities, algebraic effects, and other critical areas to support the detailed document.

**Planned document creation and gathered theoretical foundations**

</details>

```unknown
bash -lc ls -lah /mnt/data && echo '--- docx skill ---' && sed -n '1,240p' /home/oai/skills/docx/SKILL.md && echo '--- pdf skill ---' && sed -n '1,260p' /home/oai/skills/pdfs/SKILL.md
```

<details><summary>💭 Thinking</summary>

**Inspected files and extracted monograph content and bibliography**

</details>

```json
{"search_query":[{"q":"site:dl.acm.org \"Definitional Interpreters for Higher-Order Programming Languages\" Reynolds"},{"q":"site:brics.dk \"Defunctionalization at Work\" Danvy Nielsen"},{"q":"site:dl.acm.org \"Influence of Browsers on Evaluators\" Queinnec"},{"q":"site:springer.com \"Continuations and Web Servers\" Queinnec"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched for primary sources, DOIs, and related papers across multiple sites**

</details>

```unknown
bash -lc ls -l /mnt/data/tiny-idp-goja-interpreter-monograph.* && sed -n '1,220p' /mnt/data/tiny-idp-goja-interpreter-monograph.md
```

<details><summary>💭 Thinking</summary>

**Inspected monograph file, listed files, and generated report**

</details>

```json
{"search_query":[{"q":"Reynolds Definitional Interpreters for Higher-Order Programming Languages DOI 10.1145/800194.805852"},{"q":"Danvy Nielsen Defunctionalization at Work BRICS RS-01-23"},{"q":"Queinnec Continuations and Web Servers 2004 DOI"},{"q":"Appel Compiling with Continuations MIT Press 1992"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched academic sources from multiple libraries and repositories**

</details>

```unknown
bash -lc command -v dot || true; python - <<'PY'
import docx, matplotlib
print('python-docx', docx.__version__)
print('matplotlib', matplotlib.__version__)
PY
```

<details><summary>💭 Thinking</summary>

**Checked Graphviz installation and inspected internal navigation tool**

</details>

```json
{"search_query":[{"q":"\"Contracts for Higher-Order Functions\" Findler Felleisen DOI"},{"q":"\"Contracts for higher-order functions\" ICFP 2002 ACM"},{"q":"Findler Felleisen contracts blame 2002"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched for "Contracts for Higher-Order Functions" papers**

</details>

```unknown
bash -lc ls -l /mnt/data && echo '---' && sed -n '1,220p' /mnt/data/tiny-idp-goja-interpreter-monograph.md
```

<details><summary>💭 Thinking</summary>

**Inspected files, analyzed images, and searched for report files**

</details>

```json
{"search_query":[{"q":"site:dl.acm.org Defunctionalization at Work Danvy Nielsen 2001 DOI"},{"q":"site:dl.acm.org Polymorphic Effect Systems Lucassen Gifford 1988 DOI"},{"q":"site:dl.acm.org Contracts for Higher-Order Functions Findler Felleisen 2002 DOI"},{"q":"site:dl.acm.org Protection in Programming Languages Morris 1973 DOI"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched academic sources across multiple platforms**

</details>

```unknown
bash -lc grep -n '^@' /mnt/data/tiny-idp-interpreter-theory.bib | tail -n +1
```

<details><summary>💭 Thinking</summary>

**Inspected bibliography entries and checked software installations**

</details>

```json
{"search_query":[{"q":"\"Nix: A Safe and Policy-Free System for Software Deployment\" LISA 2004"},{"q":"\"Inheritance of Workflows\" 10.1016/S0304-3975(00)00321-2"},{"q":"\"Folding Domain-Specific Languages\" DOI"},{"q":"\"EROS: A Fast Capability System\" DOI"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched multiple platforms for metadata, references, and related content**

</details>

```unknown
bash -lc cat >> /mnt/data/tiny-idp-interpreter-theory.bib <<'EOF'
@article{plotkin2003,
  author = {Plotkin, Gordon D. and Power, John},
  title = {Algebraic Operations and Generic Effects},
  journal = {Applied Categorical Structures},
  year = {2003},
  volume = {11},
  number = {1},
  pages = {69--94},
  doi = {10.1023/A:1023064908962}
}
@inproceedings{shapiro1999,
  author = {Shapiro, Jonathan S. and Smith, Jonathan M. and Farber, David J.},
  title = {EROS: A Fast Capability System},
  booktitle = {Proceedings of the Seventeenth ACM Symposium on Operating Systems Principles},
  year = {1999},
  pages = {170--185},
  doi = {10.1145/319151.319163}
}
@book{pitts2013,
  author = {Pitts, Andrew M.},
  title = {Nominal Sets: Names and Symmetry in Computer Science},
  publisher = {Cambridge University Press},
  year = {2013},
  doi = {10.1017/CBO9781139084673}
}
@phdthesis{armstrong2003,
  author = {Armstrong, Joe},
  title = {Making Reliable Distributed Systems in the Presence of Software Errors},
  school = {Royal Institute of Technology (KTH)},
  year = {2003},
  url = {https://erlang.org/download/armstrong_thesis_2003.pdf}
}
@inproceedings{dolstra2004,
  author = {Dolstra, Eelco and de Jonge, Merijn and Visser, Eelco},
  title = {Nix: A Safe and Policy-Free System for Software Deployment},
  booktitle = {18th Large Installation System Administration Conference (LISA '04)},
  year = {2004},
  pages = {79--92},
  publisher = {USENIX Association},
  url = {https://www.usenix.org/conference/lisa-04/nix-safe-and-policy-free-system-software-deployment}
}
@article{vanderAalst2002,
  author = {van der Aalst, Wil M. P. and Basten, Twan},
  title = {Inheritance of Workflows: An Approach to Tackling Problems Related to Change},
  journal = {Theoretical Computer Science},
  year = {2002},
  volume = {270},
  number = {1--2},
  pages = {125--203},
  doi = {10.1016/S0304-3975(00)00321-2}
}
@inproceedings{gibbons2014,
  author = {Gibbons, Jeremy and Wu, Nicolas},
  title = {Folding Domain-Specific Languages: Deep and Shallow Embeddings},
  booktitle = {Proceedings of the 19th ACM SIGPLAN International Conference on Functional Programming},
  year = {2014},
  pages = {339--347},
  doi = {10.1145/2628136.2628138}
}
@book{holzmann2003,
  author = {Holzmann, Gerard J.},
  title = {The SPIN Model Checker: Primer and Reference Manual},
  publisher = {Addison-Wesley},
  year = {2003},
  isbn = {9780321228628}
}
@book{nielson2019,
  author = {Nielson, Flemming and Nielson, Hanne Riis},
  title = {Formal Methods: An Appetizer},
  publisher = {Springer},
  year = {2019},
  doi = {10.1007/978-3-030-05156-3}
}
EOF

grep -n '^@' /mnt/data/tiny-idp-interpreter-theory.bib | tail -15
```

<details><summary>💭 Thinking</summary>

**Appended bibliography, created theoretical foundations, and updated script**

</details>

# The Interpreter Theory Behind Tiny-IDP

I produced a **17,784-word literature-backed companion document** that expands the concepts marked in the photographs and connects them directly to the TINYIDP-GOJA-001 implementation.

## Files

- [Editable DOCX draft](sandbox:/mnt/data/tiny-idp-interpreter-theory-companion.docx)
- [Markdown source](sandbox:/mnt/data/tiny-idp-interpreter-theory-companion.md)
- [BibTeX bibliography](sandbox:/mnt/data/tiny-idp-interpreter-theory.bib)

The DOCX contains the full text, diagrams, equations, code mappings, and formatted author-date citations. Its table of contents was refreshed through LibreOffice after generation. A final PDF is not included in this delivery because the post-refresh DOCX and all resulting PDF pages still require a complete final visual inspection.

## Scope of the document

The report develops the implementation as a **family of small interpreters surrounding a Go-owned identity microkernel**. It treats the following as distinct but cooperating object languages:

1. a definition-time interpreter that turns JavaScript into `idpprogram.Program`;
2. a materialization and linking interpreter that reconstructs callbacks in independent Goja runtimes;
3. a request-time interpreter for bounded lambdas and invocation capabilities;
4. a durable workflow interpreter based on first-order continuation records;
5. native interpreters for presentations, challenges, effect plans, protocol decisions, and verification scenarios.

The central argument is that Tiny-IDP permits rich computation inside JavaScript while keeping the set of **authoritative meanings** finite and Go-owned.

## Concepts examined in depth

### Defunctionalization and serialized continuations

The document relates Tiny-IDP’s stable resume-handler IDs and bounded `Carry` values to Reynolds-style defunctionalization and Danvy and Nielsen’s later systematic treatment. Rather than serializing closures, stacks, Promise resolvers, or a Goja heap, the system replaces a browser-spanning continuation with:

\[
K = (\text{handler tag},\ \text{schema-checked environment},\ \text{native references})
\]

A native apply operation resolves the tag under the pinned program generation and invokes the corresponding callback. This interpretation is also compared with Queinnec’s work on continuations in Web servers. citeturn423602search5turn423602search8turn423602search2

The analysis then treats the continuation record as a security protocol in its own right: HMAC-hashed public handles, request and client digests, browser/session binding, revision, expiry, terminal state, generation identity, public carry, and separately typed secret or evidence references.

### Runtime type-and-effect discipline

`LambdaSpec` is interpreted as a dynamic judgment of the form:

\[
\Gamma;\Delta \vdash \lambda :
I \xrightarrow{\ O,\ C,\ E,\ B\ } R
\]

where:

- \(I\) and \(R\) are input and output schemas;
- \(O\) is the allowed outcome set;
- \(C\) is the required capability set;
- \(E\) is the permitted native effect set;
- \(B\) contains timeout, call-count, and output-size budgets.

The document connects this structure to effect systems, higher-order contracts, typestate, and session-typed protocol thinking. It carefully distinguishes the implementation from a statically proved JavaScript type system: the guarantees are enforced at compilation, activation, invocation, and native interpretation boundaries. citeturn423602search0turn158179search0turn255864search7turn255864search4

### Closed outcome algebra and runtime typestate

The report formalizes the outcome family:

\[
\mathcal O =
\mathrm{Continue}
+\mathrm{Present}
+\mathrm{Challenge}
+\mathrm{Commit}
+\mathrm{Complete}
+\mathrm{Deny}
+\mathrm{Skip}
+\mathrm{Error}
\]

and explains why `deny`, `skip`, and `error` cannot safely be collapsed into Boolean values, exceptions, or `undefined`.

Each outcome is legal only in certain runtime states. A `present` or `challenge` result requires a declared continuation edge; a `commit` requires one or more declared effects; other outcomes must not smuggle continuation or effect data. This creates a runtime typestate protocol for handler execution.

### Nominal branding in an untyped language

Tiny-IDP’s blank Goja objects are analyzed as process-local dynamic seals. Lambda handles, field descriptors, action descriptors, and secret handles are recognized through host-side maps keyed by Goja object identity.

A structurally identical object is not equivalent:

```javascript
const forged = {};
```

because the authority comes from freshness and identity, not object properties. The document links this to Morris’s protection mechanisms, dynamic sealing, abstract names, and nominal-set theory. citeturn337456search0turn337456search2

The report also states the boundary clearly: this is process-local unforgeability inside the VM, not cryptographic authenticity for browser or network handles.

### Object-capability-style authority

Invocation capabilities are examined using the capability-machine and object-capability literature. The effective authority of one callback is modeled as the intersection of:

\[
A_{\text{effective}}
=
A_{\text{program}}
\cap A_{\lambda}
\cap A_{\text{host}}
\cap A_{\text{invocation}}
\]

A lambda cannot dynamically acquire a service by string lookup. It receives only the capabilities declared by the program and lambda, implemented by the host, and installed for that invocation.

The document covers:

- capability version compatibility;
- byte and call budgets;
- context-bounded invocation;
- namespaced capability objects;
- Promise-based native calls;
- panic-to-rejection conversion;
- temporal revocation through the invocation’s `active` state;
- tests preventing a retained JavaScript global from reusing expired authority.

This is tied to least privilege, complete mediation, confused-deputy avoidance, and the object-capability model. citeturn814687search0turn814687search3turn337456search10turn814687search1

### Algebraic-effect-style commits

`OutcomeCommit` is interpreted as an inert command language:

\[
E ::=
\mathrm{CreateIdentity}(p)
\mid \mathrm{AttachCredential}(q)
\mid \mathrm{ConsumeInvitation}(r)
\mid \cdots
\]

JavaScript may construct this syntax, but it cannot interpret or execute it. Native Go revalidates the exact command sequence, resolves opaque secret handles, checks native evidence and protocol bindings, and applies the accepted plan through a named transaction.

The report connects this to algebraic effects and handlers while carefully avoiding the claim that Tiny-IDP implements a general algebraic-effects calculus. The useful shared property is the separation between **operation description** and **privileged interpretation**. citeturn868343search14turn868343search4turn868343search1

The signup committer is then analyzed as the linearization point for:

- continuation consumption;
- account and credential creation;
- optional invitation redemption;
- browser-session creation;
- authorization-interaction approval.

External mail delivery is treated separately using transaction and saga theory rather than being described as exactly atomic.

### Actor-like runtime ownership

Every Goja-local operation is routed through the VM’s owner scheduler. The document connects this to the actor model: one locus owns mutable runtime state, and other goroutines communicate with it through serialized calls or posts.

Promise settlement is therefore a protocol:

```text
VM owner creates Promise
        |
native goroutine performs bounded work
        |
owner.Post resolves or rejects Promise
```

The analysis also treats an acquired worker as an affine resource: it can be leased to at most one invocation and must be released once or destroyed once.

### Fail-stop worker leasing

Worker reuse is described as a commit decision. A runtime returns to the pool only after a positive safety result:

- callback execution completed;
- no uncertain interruption occurred;
- all asynchronous settlements completed;
- output was copied and decoded;
- the outcome and effects were valid;
- invocation capabilities were revoked.

Timeout, cancellation during execution, exception, malformed output, uncertain interruption ordering, or incomplete settlement causes disposal and replacement.

This is related to fail-stop processors and crash-only software. The report explains why `ClearInterrupt` is cleanup rather than rollback: it cannot prove that globals, queued reactions, closure environments, or library invariants returned to their pre-invocation state. citeturn269414search11turn269414search0

### Late-settlement containment

The Promise capability bridge is analyzed as a temporal isolation mechanism. Once an invocation ends, its capabilities become inactive. A late native completion must not settle a Promise in a worker that has been returned to another principal.

The document formalizes the rule:

\[
\neg\mathrm{active}(I)
\Rightarrow
\mathrm{settle}(I,p,x)
\text{ performs no VM-visible mutation}
\]

and explains why timed-out workers are discarded even when a callback appears to have returned a valid value near the deadline.

### Bounded pooling and backpressure

Pool capacity, timeout, output bytes, and capability-call budgets are treated as resource effects. A finite worker pool is not just an optimization; it prevents incoming request volume from creating unbounded Goja heaps and event loops.

The report distinguishes readiness from saturation: a fully busy but warmed pool can still be healthy, while a closed or empty generation cannot serve.

### Deterministic callback registration and checked linking

Callback registration is connected to separate compilation and linking theory. Every worker re-executes the same source and must reconstruct:

- the same canonical program;
- the same callback ID set;
- the same schemas;
- matching program, callback-registry, and schema fingerprints.

The report emphasizes what this does and does not prove. It establishes symbolic linkage and artifact identity. It does not prove that callback bodies are behaviorally deterministic.

### Generation-aware resumption

The document gives extensive treatment to executable generations and hot reload. A continuation is bound to both source and semantic program identity, so a later source file cannot silently reinterpret old durable state merely by reusing a handler name.

This is compared with dynamic software updating. Traditional DSU research often transforms live state and code at update points; Tiny-IDP instead uses version coexistence:

- build a fresh generation;
- warm and test it privately;
- publish it atomically for new interactions;
- retain bounded predecessors;
- route durable continuations by exact fingerprint;
- drain and close generations no longer required.

This avoids migration of Goja heaps, closures, and suspended Promises, at the cost of bounded runtime retention. citeturn659739search22turn659739search16turn659739search3

### Separate production and verification languages

The document explains that production and verification use the same JavaScript metalanguage but compile into different object languages:

| Production | Verification |
|---|---|
| `require("tinyidp").v1` | `require("tinyidp/verify")` |
| `idpprogram.Program` and callbacks | `verifyplan.Plan` |
| Request-time worker pool | Compile-only runtime |
| Bounded production capabilities | No provider, store, or driver authority |
| Workflow and native effect interpreters | Registered scenario driver and assertions |

The verification language is materialized through an explicit native step registry before the driver executes anything. Unknown step kinds and malformed or unexpected parameters fail before the first observation.

This is related to DSL design, staged interpretation, checker-centric architectures, security automata, and model-based testing. The report uses proof-carrying code only as an architectural analogy: Tiny-IDP’s tests and metadata are not formal proofs, but the producer/checker separation is similar. citeturn207871search14turn207871search4turn207871search0turn713882search0

### Assurance vocabulary and formalization

The report develops the branch’s emerging assurance grammar: stable versioned identifiers for resources, facts, obligations, steps, effects, outcomes, observations, and properties.

It explains the three non-conferring schemas:

\[
\text{configuration}
\not\Rightarrow
\text{execution}
\not\Rightarrow
\text{property proof}
\]

A configuration says what should be selected. A transition catalog describes native operations. A trace records what was actually observed. None is allowed to manufacture the authority or evidence of another.

The report then proposes a compact abstract machine and ten invariants covering:

- callback-registry integrity;
- exclusive runtime ownership;
- unsafe-worker disposal;
- capability lifetime;
- secret non-serialization;
- generation fidelity;
- one-use continuations;
- native evidence authenticity;
- named native commit authority;
- protocol-artifact issuance ordering.

It identifies appropriate uses of TLA+, Alloy, PLT Redex, linearizability checking, stateful property testing, and static authority analysis. citeturn409503search9turn409503search3turn409503search0

## Additional material

The document concludes with:

- a comparison of ten rejected alternatives;
- a detailed review checklist for secure interpreter embeddings;
- an assessment of the synthesis’s actual novelty;
- annotated reading paths through the relevant literature;
- a concept-to-code map for the repository;
- a glossary;
- a compact formal abstract machine;
- twelve proposed next research and assurance steps.

