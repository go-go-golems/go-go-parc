# Pattern Zoo Research and Authoring Playbook

## 1. What a Pattern Zoo is

A Pattern Zoo is an evidence-backed textbook of recurring design structures found across a corpus. It is not a glossary, a list of architecture buzzwords, or a summary of each document. Its unit of organization is a reusable relationship:

```text
recurring problem
  + semantic objects
  + transformation or relation
  + laws
  + operational consequence
  + known limits
```

A good zoo lets a developer recognize one pattern under several names. It also prevents false unification by identifying terms that look alike but carry different laws.

The central research question is:

> Which small semantic or mathematical structures survive when the vocabulary, product boundary, and proposed implementation change?

## 2. Define the research contract

Before reading, write a one-paragraph contract containing:

- **Corpus:** directories, dates, projects, or document families in scope.
- **Goal:** architecture understanding, kernel design, onboarding, comparison, or implementation planning.
- **Audience:** new project developer, domain specialist, formal-methods reader, or mixed audience.
- **Evidence standard:** direct document sections, source code, executable artifact, test output, transcript context.
- **Output:** one book, several chapters, index changes, optional PDF bundle.
- **Caveat:** whether sources are generated research, peer-reviewed publications, implementation records, or speculative designs.

Example:

```text
Study four branched attempts to define RAG semantics and optimization.
Extract recurring laws despite vocabulary changes. Write for a developer who
knows software engineering but not category theory. Preserve advanced math in
separate sections. Treat generated theses as design evidence rather than proof.
```

## 3. Build a provenance-aware corpus inventory

### 3.1 Inventory fields

Create a table or structured notes with:

| Field | Purpose |
|---|---|
| Path | Supports exact citation and duplicate detection. |
| Title | Human navigation. |
| Family/branch | Prevents counting copies as independent attempts. |
| Artifact type | Transcript, thesis, report, code, test report, PDF export. |
| Created/updated | Establishes progression. |
| Scope | Identity, retrieval, optimization, jobs, release, security, etc. |
| Evidence level | Proposal, implementation description, executable evidence, verified code. |
| Relationship | Original, revision, duplicate, branch, compilation, commentary. |

### 3.2 Detect duplicates and branches

Use file sizes as a first clue, then hashes and diffs:

```bash
sha256sum path/a.md path/b.md
diff --stat path/a.md path/b.md
```

Classify:

- **byte duplicate:** one intellectual artifact in two locations;
- **revision:** mostly the same artifact with meaningful changes;
- **branch:** common base followed by a distinct proposal;
- **transcript plus artifact:** provenance record and resulting document, not independent theories;
- **independent attempt:** separate framing or derivation that converges on a law.

Repeated text establishes persistence within the archive, not independent validation.

### 3.3 Select the first reading set

Choose one primary document per independent attempt and one operational artifact where available. Prefer sections containing definitions, laws, pseudocode, counterexamples, or conclusions. Do not begin by reading every PDF export of the same Markdown.

## 4. Perform pattern-oriented reading

### 4.1 Use semantic probes

Search each document for headings and terms around:

```text
identity, equality, canonical, semantic
fact, evidence, provenance, derivation, observation
merge, union, join, deduplicate, conflict
plan, operation, interpreter, compose, tensor
outcome, failure, abstain, trace, resource
change, intervention, support, closure, invalidation, reuse
state, event, reducer, replay, idempotence
cell, coordinate, pairing, coupling, estimand
gate, constraint, Pareto, promote, eligible
validator, certificate, proof, trusted
release, activation, lease, CAS, snapshot
authorization, disclosure, noninterference
```

The probe locates material; it does not establish the pattern. Read the surrounding section completely.

### 4.2 Fill an extraction card

For each candidate pattern:

```markdown
## Candidate: <working name>

- Problem:
- Concrete example:
- Semantic objects/types:
- Operation/relation:
- Laws:
- What the laws buy operationally:
- Local names:
- Exact source headings:
- Independent sightings:
- Counterexample:
- What it must not be confused with:
- Minimal implementation:
- Optional formalism:
- Confidence/evidence status:
```

### 4.3 Ask the counterfactual question

For every candidate ask:

> What would break if this structure or law were removed?

Examples:

- Without canonical identity, caches cannot make a defensible sameness claim.
- Without variant-preserving merge, worker timing silently decides truth.
- Without exact coordinates, missing failures change the experiment estimand.
- Without a release root, one request can mix incompatible behavior epochs.

If the answer is merely “the architecture would be less elegant,” the candidate is probably not a core pattern.

## 5. Decide whether two sightings are the same pattern

Use four tests.

### 5.1 Object correspondence

Can the semantic objects be mapped without losing their role?

```text
experiment cell coordinate <-> durable job invocation key
```

These are related identity structures, but not identical: one defines an estimand cell, the other defines an executable invocation.

### 5.2 Law correspondence

Do the operations obey the same laws?

```text
variant merge: associative, commutative, idempotent
trace concatenation: associative with identity, but usually not commutative
```

Both are monoids, but only the first is a join-semilattice. Do not flatten them into one “merge.”

### 5.3 Failure correspondence

Do they fail in the same way when the law is violated?

- Dependency closure omission permits stale reuse.
- Provenance omission prevents explanation or verification.

The graphs may share traversal code while preserving different semantics.

### 5.4 Replacement correspondence

Could one generic interface replace both without adding flags that restore the original distinction? If not, they probably belong in separate patterns or specializations.

## 6. Build the alias and collision matrix

Use four classes:

| Class | Meaning | Example |
|---|---|---|
| Alias | Same structure and law under another name. | event reducer / transition fold |
| Specialization | Same general law with domain-specific obligations. | semantic ID / release ID |
| Collision | Same word, different mathematical object. | trusted kernel / Markov kernel |
| Look-alike | Similar representation, different edge meaning or use. | dependency graph / provenance graph |

For each preferred term, preserve source-local vocabulary:

| Preferred name | Source-local names | Shared core | Difference retained |
|---|---|---|---|

This table becomes the basis of every “Names and sightings” section.

## 7. Extract the restrained kernel

### 7.1 Use the two-consumer and deletion tests

A shared nucleus is plausible when:

1. at least two consumers share the same meaning and laws;
2. centralization removes duplicate semantic authority;
3. the abstraction deletes more duplicated logic than it adds framework code;
4. domain-specific validators remain owned by their domain;
5. dependency direction stays acyclic and understandable.

### 7.2 Classify ownership

**Domain-neutral nucleus** might contain canonical encoding, typed IDs, immutable refs, terminal outcomes, reducer interfaces, or law tests.

**Domain kernel** owns meanings such as source lineage, grounding, authorization, exact experiment pairing, or release coherence.

**Infrastructure** owns queueing, retries, leases, stores, rate limits, and scheduling while obeying semantic protocols.

**Product policy** owns prompts, judges, thresholds, human decisions, and presentation meaning.

**Research formalism** may explain the design without becoming a production package.

### 7.3 Apply the implementation-pressure test

An abstraction should change at least one of:

- API shape;
- invariant;
- static analysis;
- interpreter;
- test oracle;
- admission rule;
- reuse decision.

If it changes none, keep it in the advanced explanation rather than the runtime architecture.

## 8. Design the book before drafting

### 8.1 Establish the pedagogical contract

State:

- first-day professional audience;
- no assumed advanced mathematics;
- no analogies;
- symbols introduced from examples;
- separate advanced lane;
- generated-evidence caveat.

### 8.2 Order patterns by dependency

A useful order is:

1. identity and canonical values;
2. semantic record families;
3. accumulation and selection;
4. plans and interpretation;
5. outcomes and observations;
6. change, closure, and reuse;
7. events and reducers;
8. experiments and coupling;
9. constraints and preference;
10. validators and certificates;
11. releases and activation;
12. authorization and noninterference.

This order moves from values to transformations, then state, comparison, trust, and service boundaries.

### 8.3 Maintain two reading lanes

The first-day lane answers:

- What should I do in code?
- Why does it exist?
- What breaks without it?
- Which tiny example can I hold in my head?

The advanced lane answers:

- Which mathematical structure is present?
- What are its laws?
- Which theorem or factorization supports the implementation claim?
- What additional assumptions are required?
- Where does the formal analogy stop?

The lanes must agree. A sophisticated advanced section cannot repair incorrect beginner pseudocode.

## 9. Write the mathematics so it teaches

### 9.1 Introduce symbols from values

Bad:

```text
Let C be a symmetric monoidal category enriched over V.
```

Better:

```text
Let Q be normalized queries and R be rankings. Lexical retrieval is a typed
operation lex: Q -> R. Vector retrieval is another operation vec: Q -> R.
Running both while retaining both outputs is the product/tensor operation.
```

Then name the category or monoidal structure.

### 9.2 Translate every law into an operational consequence

| Law | Operational consequence |
|---|---|
| Associativity | Regrouping stages or batches does not change the declared result. |
| Commutativity | Arrival order does not change accumulated state. |
| Idempotence | Duplicate delivery does not change accumulated state. |
| Closure idempotence | Recomputing impact after closure discovers nothing new. |
| Reducer replay | State can be reconstructed from the same valid history. |
| Functorial interpretation | Interpreting a composed plan agrees with composing interpreted stages. |
| Noninterference | Unauthorized/high-level changes cannot affect protected low-level observations. |

### 9.3 State assumptions

A reuse theorem may require:

- complete declared dependency support;
- equal external release/suite/policy identities;
- deterministic or retained stochastic inputs;
- a named observation projection;
- collision-resistance assumptions for digests.

Without assumptions, a formula can create false confidence.

### 9.4 Separate exact and approximate claims

Exact equality may be appropriate for canonical bytes, reducers, or finite scores. ANN retrieval, provider output, and empirical quality usually need refinement, tolerance, distributions, or confidence intervals. Name the observation and comparison relation.

## 10. Use source references correctly

### 10.1 Link exact headings

Prefer:

```markdown
[[path/to/thesis#7.3 Domain-separated hashes|domain-separated identity]]
```

Avoid citing only a 300-page document when one exact section supports the claim.

### 10.2 Distinguish kinds of evidence

- A transcript establishes request and design progression.
- A thesis establishes a proposed model.
- Source code establishes an implementation shape.
- Test output establishes behavior for tested cases.
- A proof establishes a theorem under stated assumptions.
- A PDF export adds no independent evidence over identical Markdown.

### 10.3 Cite contradictions and revisions

If a later document narrows an earlier abstraction, teach the correction. Pattern research should preserve evolution rather than forcing all sources into artificial agreement.

## 11. Delegate without losing synthesis quality

### 11.1 Good fan-out boundaries

Delegate by:

- independent branch;
- conceptual family;
- code versus thesis evidence;
- beginner explanation versus formal review.

Ask each worker to produce a structured brief with exact headings, aliases, laws, limits, and evidence status.

### 11.2 Avoid output collisions

Parallel agents must write distinct files:

```text
/tmp/zoo-identity.md
/tmp/zoo-state.md
/tmp/zoo-experiments.md
```

### 11.3 The parent agent owns normalization

Do not concatenate briefs without review. The parent must:

- detect duplicate source material;
- reconcile naming;
- remove repeated introductions;
- align chapter structure;
- check cross-pattern distinctions;
- validate the final mathematics and pseudocode.

## 12. Substantive review checklist

### Identity

- Does the determinism law compare separate conforming executions rather than a value with itself?
- Does sensitivity start from changed protected behavior?
- Are semantic, material, execution, and release IDs separated?

### Plans and effects

- Does an effectful interpreter use bind/Kleisli composition rather than ordinary composition?
- Is semantic tensor distinguished from runtime concurrency?
- Are dynamic regions explicitly marked as incompletely inspectable?

### Outcomes

- Do success, abstention, failure, and cancellation form a consistent sum?
- Are integrity/custody failures distinguished from domain outcomes?
- Does each observation dimension have an appropriate combine law?

### Change and reuse

- Does the example graph contain every edge needed to produce the claimed closure?
- Are dependency and provenance distinguished?
- Does reuse check external identities as well as support disjointness?

### Events and idempotence

- Is duplicate event detection performed before allocating/appending a new ordinal?
- Does repeated external execution have an idempotency, fencing, or reconciliation protocol?
- Is the observation boundary for “idempotent” named?

### Experiments

- Does expected-coordinate generation include every coordinate dimension?
- Are failures and missing cells retained?
- Is coupling distinguished from merely sharing a seed?

### Decisions

- Do hard constraints precede preference?
- Can missing evidence produce `Undecided`?
- Is scalarization limited to search/allocation rather than safety promotion?

### Validators

- Are set/type symbols distinguished from concrete values?
- Are soundness and completeness stated separately?
- Does the certificate say what it cannot prove?

### Releases

- Is the lease acquired atomically with resolution before reading GC-eligible children?
- Is activation a compare-and-swap transition?
- Can rollback preserve monotone control history?

### Authorization

- Does authorization dominate every disclosure path?
- Is the certificate bound to subject, release, policy, provider, epoch, and exact evidence IDs?
- Can unauthorized data influence ranking, caches, telemetry, or timing visible to the subject?

## 13. Mechanical validation

Run:

```bash
python3 .pi/skills/pattern-zoo-authoring/scripts/validate_pattern_zoo.py \
  "Transcripts/Research/09 - Example Pattern Zoo.md" \
  --expected-patterns 12
```

The validator checks:

- frontmatter presence;
- pattern count and numbering;
- required chapter sections;
- advanced-section count;
- balanced fenced code blocks;
- path-qualified wiki targets;
- exact heading anchors;
- Pandoc-hostile TeX delimiters and selected unsupported commands.

Also run a renderer if publication matters. Mechanical success does not replace substantive review.

## 14. Publication and archival hygiene

1. Link the book from the cluster note and master index.
2. Keep source artifacts in place; link rather than duplicate them.
3. Remove temporary subagent briefs unless they are deliberate research records.
4. Record generated-research caveats.
5. Render PDF before uploading.
6. If bundling to reMarkable, use the dedicated upload skill and do not verify a successful upload with extra cloud calls.
7. Review Git status and stage intentionally.

## 15. Common anti-patterns

### The glossary zoo

**Symptom:** chapters define terms but do not state laws or failure modes.

**Fix:** require problem, objects, law, operational consequence, and counterexample.

### The framework zoo

**Symptom:** every mathematical idea becomes a package or interface.

**Fix:** separate explanatory formalism from implementation pressure; apply two-consumer and deletion tests.

### The branch-voting zoo

**Symptom:** four duplicated branch exports are treated as four confirmations.

**Fix:** classify provenance and hash duplicates before synthesis.

### The advanced-only zoo

**Symptom:** the book begins with categories, fibrations, and Markov kernels without concrete values.

**Fix:** preserve the first-day lane and derive notation from one example.

### The decorative-math zoo

**Symptom:** equations restate prose but do not constrain implementation.

**Fix:** explain what refactoring, retry, reorder, reuse, or disclosure behavior each law permits or forbids.

### The universal-evidence zoo

**Symptom:** source facts, provenance, traces, experiment records, and UI evidence are flattened into one type.

**Fix:** preserve record-family distinctions and typed links.

### The structurally-valid but semantically-wrong zoo

**Symptom:** every heading and link passes, but pseudocode violates its own invariants.

**Fix:** obtain a substantive review with adversarial retry, race, missing-cell, and bypass scenarios.

## 16. Completion evidence

A Pattern Zoo is complete when you can show:

- corpus inventory and duplicate classification;
- candidate extraction and alias matrix;
- evidence for every accepted pattern;
- first-day and advanced sections for every chapter;
- exact source links;
- a restrained kernel and ownership cut;
- clean validator output;
- substantive review findings resolved;
- index integration;
- successful render/upload if requested.
