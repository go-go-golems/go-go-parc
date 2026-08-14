---
title: Evaluation-Loop Formalization Research — Shared Theory Across CoinVault, rag-ttc, and Ragopt
aliases:
  - Evaluation loops research family
  - Judge gate custody formalization program
  - Eval-loop overlap analysis
status: active
type: architecture-garden-research-index
created: 2026-08-14
tags:
  - architecture-garden
  - research
  - evaluation
  - llm-as-judge
  - experiment-custody
  - formal-methods
  - gepa
  - go
  - tla-plus
  - lean4
related_notes:
  - "[[Research/Software Architecture Garden/README|Software Architecture Garden]]"
  - "[[Research/Software Architecture Garden/coinvault/README|CoinVault]]"
  - "[[Research/Software Architecture Garden/rag-ttc/optimization/01 - Optimization Judging and Improvement Loops - Overview|rag-ttc — Optimization, Judging, and Improvement Loops]]"
  - "[[Research/Software Architecture Garden/ragopt/README|Ragopt]]"
  - "[[Research/Software Architecture Garden/ragopt/building-blocks/01 - Ragopt as a Building Block - The Adopter Contract from Research to Production|Ragopt as a Building Block]]"
  - "[[Research/Software Architecture Garden/ragkit/building-blocks/01 - Ragkit as a Building Block - Reproducible Research to Production|Ragkit as a Building Block]]"
  - "[[Research/Software Architecture Garden/sessionstream/designs/research/02 - Constraining the Go Binary - Layered Refinement from Proved Kernels to Executables|Sessionstream — Constraining the Go Binary]]"
---

# Evaluation-Loop Formalization Research

The [[Research/Software Architecture Garden/coinvault/README|CoinVault]] and [[Research/Software Architecture Garden/rag-ttc/optimization/01 - Optimization Judging and Improvement Loops - Overview|rag-ttc optimization]] Garden studies, together with the earlier [[Research/Software Architecture Garden/ragopt/README|Ragopt]] entry, describe three repositories that independently converged on one architecture for improving an LLM system under evidence: frozen instruments measure, decomposed judges witness, deterministic gates decide, hash-chained journals remember, and humans apply. The three codebases share more than vocabulary — they share invariants, several of them extracted from concrete failures (the six neutralized default-results experiments; the judge that scored every SQL-grounded claim unsupported; the baseline run killed by a transient transport error).

This research family does for that architecture what the [[Research/Software Architecture Garden/sessionstream/designs/research/01 - Proving the Bounded Asynchronous Observer Dispatcher|sessionstream research program]] did for event streaming: take each shared invariant, state it formally, design the elegant reusable API that protects it, and build checked artifacts — Go prototypes with tests, TLA+ models run through TLC, Lean statements where a proof genuinely illuminates — rather than prose alone. Each project below is worked out in its own research document with the sessionstream research conventions: `status: proposed` until artifacts exist, explicit guarantee taxonomies, mutation sensitivity as an acceptance gate, and finite evidence reported as finite evidence.

> [!summary]
> - Six overlapping theory clusters recur across CoinVault, rag-ttc, and Ragopt: frozen instrument identity, treatment-exercise witnessing, decomposed judge admission, run-custody/resume/budget algebra, constraint-first gating under an authority ladder, and digest-named suite governance with structurally closed splits.
> - Each cluster gets one research project: a design document under this directory plus checked artifacts under `specs/<slug>/`.
> - The verification toolchain available and used here: Go 1.26 (prototypes, property and race tests), TLC (bounded model checking of TLA+ specs), Lean 4 (kernel proofs where warranted). Anything not actually run is labeled unchecked.
> - The shared goal is reusable packages: candidates for extraction into Ragopt or a new shared module, each protecting one law the source repositories currently protect with bespoke code.

## The overlap analysis

The table names each overlap, the concrete evidence in all three repositories, and the law being protected. Line references are to the pinned snapshots recorded in the respective Garden entries.

| # | Overlap | CoinVault evidence | rag-ttc evidence | Ragopt evidence | Protected law |
|---|---|---|---|---|---|
| 1 | **Frozen instrument identity** | 17-file `source-lock.yaml` incl. the judge itself; 8 snapshot dimensions cross-checked at preflight; `judgePromptVersion` in the durable cache key; `ragopt_revision` verified against `go.mod` | `validateI5Environment` hashes five of its own source files as locked snapshot dimensions; dead code retained because its digest is a dimension | exact policy **byte** digest distinct from **semantic** digest; candidate/snapshot digest recomputation on load | A measurement is attributable only when the entire apparatus — data, prompts, harness source, dependencies — is digest-identified and verified before spend. |
| 2 | **Treatment-exercise witnessing** | treatment contracts with per-mechanism exact check sets; `treatment_not_exercised` failure class; judge withheld from unattributable cells; born from six neutralized experiments | arm difference carried entirely by ragopt-injected snapshots through one shared executor | independent `Mutation` computation from parent/child bytes; declared asset must equal the computed delta | A delta is evidence about a mutation only if observed behavior proves the mutation was causally live in the challenger and absent in the incumbent. Configuration is not behavior. |
| 3 | **Decomposed judge admission** | two-step judge: extraction never sees evidence, verdicts never restate claims; faithfulness computed; nine structural rejection rules; one repair retry; witness-not-gate | JUDGE-001 origin of the same protocol; five judging subsystems all terminating in human-read artifacts; judge overhead excluded from product cost | `Outcome` validation: finite metrics, coherent flags; judge results enter only as metrics | A large untrusted producer (the judge model) is admitted through a small trusted validator; scores are computed from validated verdicts, never asked for; the judge is a witness, never a gate. |
| 4 | **Run custody, resume, budgets** | hard-locked call/token ceilings with pre-reservation and rollback; resume seeding from native artifacts; sticky budget close on unprovable provider spend; per-cell atomic native artifacts | cell accounting surfaced; experiments/ directory as run custody | hash-chained `cells.jsonl` with fsync commit boundary; exact-coordinate resume; interruption test proving resumed ≡ uninterrupted; explicit non-claims (no exactly-once effects) | Committed evidence survives interruption as a verifiable prefix; resume executes only absent exact coordinates; spend never exceeds a ceiling and unprovable spend closes the budget conservatively. |
| 5 | **Constraint-first gates and the authority ladder** | `retrievalSummaryWins` mini-gate (no regression + one improvement); gate policy with floors/targets/regressions/tie-breakers; promotion plan cannot apply | lexicographic acceptance (identity → hard → target → regressions → informational cost); every behavior-changing arrow passes through a human | pure `gate.Evaluate` with `stopAfter` short-circuit; `MissingPair` never scores zero; `review_required` + `human_apply_required` fixed | Hard constraints dominate preference; missing data keeps explicit denominators and can never improve an aggregate; decision authority, gate authority, and application authority are three different types. |
| 6 | **Suite governance and split hygiene** | digest-locked 80-question eval set with one mode per question; unknown-ID warnings; validation split replaced by a sentinel file and a hard CLI error; reviewed suite lock (currently unwired) | append-only proposal ledger whose `Commit` mints a new digest-named evaluation set; answering model may draft but never self-approve exam questions | ordered suite digest; case order participates in identity because it controls execution | Ground truth changes only through governed, reviewable, digest-minting transitions; held-out data is inaccessible by mechanism until promotion criteria open it. |

Two further overlaps are recorded but deferred rather than assigned: **server-owned citation grounding** (CoinVault's evidence ledger and projection resolution; Ragkit's hydration authority) belongs with the Ragkit study's lineage questions, and **blame-assigning stage diagnostics** (CoinVault's candidate-pool classifier) is a strong single-implementation pattern still awaiting a second occurrence to compare against.

## The research projects

Each project is one document in this directory plus artifacts under `specs/`:

```text
Research/Software Architecture Garden/Research/evaluation-loops/
├── README.md                                  (this index)
├── 01 - Frozen Instruments and Self-Digesting Preflight.md
├── 02 - Treatment-Exercise Witnesses.md
├── 03 - The Decomposed Judge Kernel.md
├── 04 - Run Custody Algebra - Chains Resume and Budgets.md
├── 05 - Constraint-First Gates and the Authority Ladder.md
├── 06 - Suite Governance and Structurally Closed Splits.md
└── specs/
    ├── instrumentlock/    (Go module)
    ├── treatment/         (Go module + TLA+)
    ├── judgekernel/       (Go module + Lean statements)
    ├── runcustody/        (TLA+ models + Go module)
    ├── gatealgebra/       (Lean proofs + Go module)
    └── suitegov/          (Go module)
```

| Project | Question | Primary artifacts |
|---|---|---|
| 01 Frozen instruments | What exactly does a digest-verified preflight prove, and what is the minimal reusable API for apparatus freezing and version-keyed population invalidation? | `instrumentlock` Go package with manifest/preflight/cache-key types, trust ledger, mutation tests |
| 02 Treatment-exercise witnesses | Can "the mutation was causally live" be stated as a decidable predicate over observed event traces, generalized beyond CoinVault's nine mechanisms into a product-supplied contract in Ragopt? | trace-predicate formalization, generic `TreatmentReport` API proposal, Go checker prototype, neutralized-treatment mutation tests |
| 03 Decomposed judge kernel | Which invariants of the two-step judge are structural (provable about the validator) versus empirical (properties of models), and what is the reusable kernel API? | `judgekernel` Go package (typed labels, validator, repair combinator, versioned cache), property tests, Lean statements of validator invariants |
| 04 Run custody algebra | Do hash-chained journals, exact-coordinate resume, and pre-reserving budget accountants compose into a provable safety story under interruption and concurrency? | TLA+ models checked with TLC (resume equivalence, budget never-exceed, conservative close), Go prototype with race tests |
| 05 Gate algebra and authority | What are the algebraic properties of lexicographic constraint-domination gates (short-circuit soundness, missing-data monotonicity), and how does the type system enforce the witness/gate/human authority ladder? | Lean proofs of gate laws, nominal-typed Go API, golden tests |
| 06 Suite governance | Can split hygiene and governed ground-truth evolution be enforced as information-flow properties of a small package rather than conventions? | `suitegov` Go package (proposal ledger, digest minting, split sentinels, lock verification), non-leakage statement, adoption path for CoinVault's unwired lock |

## Delivery status — 2026-08-14

All six projects delivered their documents and checked artifacts on 2026-08-14. The table records what was actually executed, per the working rules; details and full transcripts live in each document's callouts and the `specs/*/results/` directories.

| Project | Checked evidence | Headline result |
|---|---|---|
| 01 Frozen instruments | `instrumentlock` 13/13 Go tests incl. four mutation cases and a self-inclusion freeze | The worktree/binary skew is the sharpest unclosed gap in all three repositories; subset locks and sealed roots are distinct promises; population keys are disjoint by construction |
| 02 Treatment witnesses | 12/12 Go tests; TLC exhaustive pass plus a mutated config that violates `JudgeAttribution` with a four-state counterexample | Witness strength ladder (installation < consultation < determination); the v1–v6 failure is a determination gap dressed as installation success; Ragopt insertion via `pkg/treatment` + optional `Treatment *Report` |
| 03 Judge kernel | 6 Lean theorems check under core Lean 4.33 (no `sorry`); ~1.8M fuzz executions, 0 counterexamples; 6/6 mutants killed | `Admitted` is a proof-carrying value only `Admit` constructs; the kernel exports no accept/reject; rag-ttc's ancestor never validates evidence citations — the exact hole the CoinVault port closed |
| 04 Run custody | 7 TLC transcripts (protocol pass at depth 13; at-most-once violated as intended; four mutations rejected); 15 Go tests incl. `-race` and crash-at-every-point resume equivalence | CoinVault's judge budget is in the provably safe reservation class; the answer budget is safe only by the sequential-arms convention — concurrent callers overshoot in the model; the chain cannot detect truncation-to-valid-prefix without the completion gate |
| 05 Gate algebra | All Lean theorem families check; 13 Go tests; unforgeable-`Application` compile error captured; both mutants caught | `stopAfter` is semantically inert (proved); failure-rate and mean-delta checks are individually **not** missing-monotone — the unconditional `complete_pairing` identity check is the single mechanism restoring gate-level monotonicity, a must-not-refactor law; the family has three distinct decision structures, not one gate |
| 06 Suite governance | 15/15 Go tests; 6/6 mutants killed after strengthening a harness that a redundant mechanism had masked | Both source repositories structurally permit self-approval (no reviewer identity in CoinVault's lock; `Commit` takes no reviewer in rag-ttc's ledger); two-principal digest-minting commit and typed closed-split sentinels close both |

Two live defects surfaced by the companion building-block studies feed this family directly: CoinVault's `validateGECRagoptLinkedRevision` fails unconditionally now that `go.mod` pins the plain tag `v0.0.1` (fail-closed confirmation of project 01's thesis that instrument identity outlives its encoding assumptions), and rag-ttc does not compile against workspace ragkit HEAD because it still imports the extracted `ragkit/flow`/`ragkit/execution` packages.

## Working rules for this family

- Ground every claim in the pinned snapshots recorded by the source Garden entries; read the actual code before citing a symbol.
- Run what you build: Go tests (including `-race` where concurrency exists), TLC for every TLA+ model, `lean` for every Lean file. An artifact that was not executed is labeled unchecked, in the artifact and in the document.
- State the guarantee taxonomy: what each proof, model check, test, or prototype establishes and does not establish.
- Mutation sensitivity is an acceptance gate: each project must demonstrate at least one seeded violation its artifacts reject.
- Finite evidence is reported as finite evidence; a checked bounded model is not a universal proof.
- Extraction proposals name their target (Ragopt, a new shared module) and their adoption cost honestly; a package no repository adopts is a finding, not a failure.
