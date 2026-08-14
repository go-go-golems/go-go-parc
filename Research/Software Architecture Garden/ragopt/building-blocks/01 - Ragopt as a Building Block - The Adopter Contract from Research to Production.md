---
title: Ragopt as a Building Block — The Adopter Contract from Research to Production
aliases:
  - Ragopt adopter contract
  - Ragopt building-block study
  - Ragopt v0.0.1 consumer analysis
status: active
type: architecture-pattern-study
created: 2026-08-14
analyzed: 2026-08-14
analysis_schema: architecture-garden-v1
repository: /home/manuel/go/pkg/mod/github.com/go-go-golems/ragopt@v0.0.1 (Go module cache, read-only)
module_version: v0.0.1
module_origin_commit: 0e9c584fee2db0de34f3ebacb32c8da757023333
module_origin_evidence: module cache download info (v0.0.1.info, Origin.VCS=git)
go_module: github.com/go-go-golems/ragopt
consumers:
  - repository: /home/manuel/workspaces/2026-08-12/deploy-dev-indexer/coinvault
    pin: "github.com/go-go-golems/ragopt v0.0.1 (go.mod:17)"
  - repository: /home/manuel/workspaces/2026-08-12/deploy-dev-indexer/rag-ttc
    pin: "github.com/go-go-golems/ragopt v0.0.1 (go.mod:15)"
tags:
  - architecture-garden
  - ragopt
  - experiment-custody
  - reproducible-research
  - rag
  - adopter-contract
  - production
related_files:
  - pkg/eval/types.go
  - pkg/eval/runner.go
  - pkg/eval/resume.go
  - pkg/runstore/run.go
  - pkg/gate/evaluate.go
  - pkg/report/write.go
  - cmd/ragopt/main.go
related_notes:
  - "[[Research/Software Architecture Garden/ragopt/README|Ragopt]]"
  - "[[Research/Software Architecture Garden/ragkit/README|Ragkit]]"
  - "[[Research/Software Architecture Garden/coinvault/README|CoinVault]]"
  - "[[Research/Software Architecture Garden/rag-ttc/optimization/01 - Optimization Judging and Improvement Loops - Overview|rag-ttc — Optimization, Judging, and Improvement Loops]]"
  - "[[Research/Software Architecture Garden/Research/evaluation-loops/README|Evaluation-Loop Formalization Research]]"
---

# Ragopt as a Building Block — The Adopter Contract from Research to Production

The [[Research/Software Architecture Garden/ragopt/README|existing Ragopt Garden entry]] studies Ragopt from the inside: its candidate admission, run custody, gate algebra, and authority boundaries. This document studies it from the outside, as a **building block** — the position it actually occupies now that two products, [[Research/Software Architecture Garden/coinvault/README|CoinVault]] and [[Research/Software Architecture Garden/rag-ttc/optimization/01 - Optimization Judging and Improvement Loops - Overview|rag-ttc]], pin `v0.0.1` and drive real campaigns through it. Three lenses organize the analysis: what the kernel contributes to *reproducible research*, what a *RAG product* must build to adopt it, and what *running it in production* turns out to mean for a library that deliberately performs no effects of its own. The center of gravity is the adopter contract: measured against both consumers, the kernel's genuinely reusable core is smaller than its README suggests and the obligations it leaves to products are larger — large enough that both consumers independently rebuilt the same five subsystems around it, which is precisely the evidence the [[Research/Software Architecture Garden/Research/evaluation-loops/README|evaluation-loops research projects]] need.

> [!summary]
> - Ragopt `v0.0.1` is the exact commit the existing Garden README pinned (`0e9c584f…`, verified from the module cache's origin metadata), so the README's findings transfer to what consumers actually run; the anticipated version skew does not exist.
> - What one run pins and proves is strong and verified here at v0.0.1: inputs are reloaded and digest-drift-rejected before work begins, every cell commits through an fsynced hash chain, native artifacts are re-owned inode-by-inode, resume executes only absent exact coordinates after strict chain validation, and finalization re-audits the entire run through the strict reader.
> - The kernel deliberately leaves six reproducibility obligations to products — environment identity, instrument freezing, treatment-exercise proof, spend budgets, model identity, and suite review — and both consumers independently built all of them, in ~851 (rag-ttc) versus ~3,053 (CoinVault) non-test adapter lines. The 3.6× spread is the cost of production hardening, not of Ragopt itself.
> - A live adoption failure was found: CoinVault's preflight parses the Ragopt *pseudo-version* out of `go.mod` to verify revision linkage, and rejects plain tags by design (its own test asserts `v0.1.0` must error) — but `go.mod` now pins the plain tag `v0.0.1`, so the linked-revision check cannot succeed for any candidate bundle at the current commit. Releasing the dependency broke the freeze machinery that referenced it.
> - The `report --help` two-file-atomicity overclaim recorded by the Garden README exists verbatim at v0.0.1 while `report.Write`'s own doc comment states the honest POSIX boundary; the debt shipped with the tag.
> - Ragopt's CLI is artifact-only (`candidate validate`, `compare`, `report`); execution and resume have no kernel CLI. In production the operator workflow lives entirely in product commands, which is coherent with the kernel's no-effects stance but means every adopter writes its own driver.

## Snapshot identity and evidence

| Field | Value |
|---|---|
| Studied module | `github.com/go-go-golems/ragopt@v0.0.1` from the Go module cache (read-only) |
| Origin | `v0.0.1.info`: git hash `0e9c584fee2db0de34f3ebacb32c8da757023333`, timestamp `2026-08-09T20:42:54Z` |
| Relation to prior study | Identical commit to the [[Research/Software Architecture Garden/ragopt/README|Garden README]]'s pinned snapshot — the tag was cut on the studied HEAD |
| Build/test | Copied to scratchpad (cache is read-only); `GOWORK=off go build ./...` exit 0; `GOWORK=off go test ./... -count=1` — all 9 test packages pass (`cmd/ragopt`, `commands/candidate`, `pkg/candidate`, `pkg/compare`, `pkg/eval` 1.2s, `pkg/gate`, `pkg/report`, `pkg/review`, `pkg/runstore`) |
| Size | ~9,700 Go lines total; ~6,400 non-test (largest: `pkg/eval/runner.go` 757, `pkg/report/write.go` 386, `pkg/gate/evaluate.go` 382) |
| Consumers verified | CoinVault at `10d1a8d8` (branch `task/deploy-dev-indexer`; adapter files committed, worktree dirty only on unrelated webchat credentials) and rag-ttc at `0b0e420` (clean), both in this workspace, both pinning `v0.0.1`; the workspace `go.work` contains neither ragopt nor a replace for it |
| Analysis scope | Full v0.0.1 source; consumer adapter surfaces re-read at the pinned checkouts; no live campaign executed |

The `/home/manuel/code/wesen/go-go-golems/ragopt` checkout was deliberately not read; all kernel claims below were verified against the module-cache copy that the consumers resolve.

## 1. Version identity: the tag, the pseudo-versions, and a broken freeze

The one place where "what the README studied" and "what consumers run" was expected to diverge turned out to hold a different and more instructive finding. The module cache's origin metadata proves `v0.0.1` is the README's commit, so there is no content skew. The skew is in **revision identity conventions**, and it is live:

- CoinVault's preflight verifies that the candidate bundle's `ragopt_revision` snapshot dimension equals the revision parsed from `go.mod` (`validateGECRagoptLinkedRevision`, `cmd/coinvault/cmds/knowledge_ragopt.go:1438-1447`). The parser, `ragoptRevisionFromVersion` (`:1466-1477`), takes the substring after the last `-` and requires at least 12 characters — the shape of a pseudo-version. A plain tag has no such suffix; the function errors with "does not contain a source revision", and CoinVault's own test asserts exactly that behavior for `v0.1.0` (`knowledge_ragopt_test.go:599`). Rejecting tags was a *decision*, presumably to force revision-precise pins.
- CoinVault's `go.mod:17` now pins the plain tag `v0.0.1`. Therefore `validateGECRagoptLinkedRevision` fails unconditionally at this commit — for every one of the 24 candidate bundles, before any bundle-specific check runs.
- The bundles themselves carry two generations of revision identity: the `default-results-8-v7` family records the 12-character pseudo-revision `4d410c57e242` (a 2026-08-06 Ragopt commit) in both its snapshot dimension and its `source-lock.yaml` `ragopt_commit`; newer bundles (`canonical-seed-stack-v1`, `abstention-routing-v2`, and others) record the full 40-character `3bc11dfd8928…` — a form `ragoptRevisionFromVersion` can never produce from a go.mod pseudo-version, since Go pseudo-versions embed 12-character revisions. Neither generation matches `0e9c584f…`, the commit actually running.

So three Ragopt revisions are in play (`4d410c…` in old bundles, `3bc11d…` in new bundles, `0e9c58…` actually resolved), and the check that was built to make such drift impossible is the thing that now fails closed. Failing closed is the correct failure mode — no experiment can silently run against an unverified kernel revision — but the episode is a precise, evidenced lesson for [[Research/Software Architecture Garden/Research/evaluation-loops/README|research project 01]]: **an instrument-freeze mechanism must define revision identity independently of the dependency manager's version syntax**, because tagging a release is a routine act that changes the syntax without changing the content. A digest of the module zip, or the origin hash the module cache already records, would have survived the tag; a string parse of the version did not.

## 2. Lens one: what the kernel contributes to reproducible research

### 2.1 What one run pins, verified at v0.0.1

The chain from proposal to durable evidence was re-verified in the module-cache source, and it is as strong as the README claims:

1. **Load-time identity, use-time revalidation.** `prepareRequest` (`pkg/eval/runner.go:116-197`) re-loads the suite and candidate from disk and rejects any digest drift between the caller's loaded values and the reread (`:141-143`, `:151-153`), rejects duplicate or malformed arm names, and binds suite/policy/candidate/snapshot/arm/repeat/mutation identity plus per-input digests into `RunConfig` (`:173-189`). A caller cannot run against stale in-memory state.
2. **Run custody with machine provenance.** `runstore.Create` (`pkg/runstore/run.go:70-156`) writes `config.json` (pretty), `manifest.json`, and `status.json` as individually durable artifacts; the manifest records run ID, canonical-config digest, Go version, hostname/OS/arch/CPU count, and — via `debug.ReadBuildInfo` — the consuming module's own path and version (`:137-140`). Every directory component is created and fsynced one level at a time (`mkdirAllAndSync`) so no child is published inside an unsynced parent.
3. **Arm isolation and evidence guarding.** Before each arm runs, the uncommitted native directory is cleared and protected run evidence is snapshotted; after it returns, `verifyRunEvidence` makes "arm mutated run-owned evidence" a hard error (`runner.go:326-344`). The arm's artifact inode is then replaced by a synced run-owned copy (`ownNativeArtifact`, `:391-435`) — hard links out of the run tree are broken before the digest is recorded.
4. **Commit boundary and chain.** A cell exists when `AppendJSONL` returns: one bounded compact record, fsynced, directory-synced. Each cell embeds its predecessor's digest and its own (`sealCell`), and `finalizeRun` (`:272-299`) re-audits the *entire* run through the strict reader `LoadArtifactRun` before writing the terminal summary — completion is a property the run proves about itself, not a flag the runner sets.
5. **Resume as strict re-derivation.** `loadCompletedCells` (`pkg/eval/resume.go:13-78`) truncates only a final non-newline fragment (with fsync of both file and directory, `:105-130`), strict-decodes every retained line, validates the hash chain, requires each cell to match an expected schedule coordinate and the resumed run's full semantic identity (`validateStoredCell`, `:80-103`), rejects duplicates, and re-verifies native artifacts. `runstore.Resume` (`run.go:35-66`) accepts only an active run whose canonical config digest matches exactly, and documents in its API comment that single-writer discipline is the caller's obligation.

### 2.2 The reproducibility ledger

What a completed v0.0.1 run does and does not establish:

| Claim | Status | Mechanism |
|---|---|---|
| The exact bytes of suite, policy, candidate, and every asset that the run used | **Proven, byte-replayable** | Copied into `inputs/` with digest/size verification; strict readers reject drift |
| Which cell produced which outcome at which frozen coordinate | **Proven** | Cell key = (run config, case, repeat, arm) + hash chain |
| The committed prefix survives interruption; resume adds only missing coordinates | **Proven for the journal** (tested: interruption/resume equivalence, `runner_test.go`) | Truncation recovery + exact-coordinate scheduling |
| External effects executed at most once per coordinate | **Not claimed** — at-least-once | Crash between arm effect and cell append re-runs the coordinate; the kernel says so |
| Only one writer appended to the journal | **Assumed, not enforced** | `Resume` has no inter-process lock; the doc comment transfers the obligation |
| The environment (models, indexes, harness source, dependency revisions) matched the candidate's declared dimensions | **Not checked by the kernel** | Dimensions are opaque strings; verification is a product obligation |
| The mutation was causally live in the challenger | **Not checked by the kernel** | The kernel proves the *bytes* differ (independent `Mutation` computation); behavior is a product obligation |
| Provider spend stayed within budget | **Not tracked** | `Outcome` records counts after the fact; no ceiling exists |

The top half is the kernel's genuine contribution to reproducible research, and it is substantial: run directories are self-verifying artifacts a reviewer can audit years later with `LoadArtifactRun`, on any machine, with no services running. The bottom half is the adopter contract.

### 2.3 The six obligations both consumers rebuilt

The strongest external evidence about a library is what every consumer had to build around it. Both consumers, independently and in different styles, built all six of these:

| Obligation | rag-ttc realization | CoinVault realization | Research project |
|---|---|---|---|
| Environment identity before spend | `validateI5Environment` (`cmd/rag-ttc/cmds/tooleval/ragopt.go:147-202`): five expected dimensions, five self-digested source/data files *stored as snapshot dimensions*, profile-definition digest, index-manifest and corpus digests | `validateGECRagoptEnvironment` (~180 lines): profiles, resolved runtime identity, eight dimensions, bundle byte digests, mechanism assets, linked revision, plus a *separate* 38-line `source-lock.yaml` cross-checked against a dimension | [[Research/Software Architecture Garden/Research/evaluation-loops/README|01]] |
| Instrument freezing (judge/harness source) | judge source digest is one of the five self-digested files | judge implementation among 17 source-locked files; judge prompt version in the cache key | 01, 03 |
| Treatment-exercise proof | arm difference carried entirely by ragopt-injected snapshot assets through one shared executor (`materializeToolConfig`, `ragopt.go:415`) | full treatment-contract subsystem (257 lines + 407 test) with per-mechanism exact check sets and the `treatment_not_exercised` failure class | [[Research/Software Architecture Garden/Research/evaluation-loops/README|02]] |
| Spend budgets and accounting | provider-call caps inside the product tool loop (`tool_safety` dimension `max-provider-4_parallel-tool-1_reserve-final`) | `gecRagoptExecutionBudget`: four hard ceilings, pre-reservation with rollback, sticky close on unprovable spend, resume seeding from native artifacts | 04 |
| Split governance | `lockedSplit` (`ragopt.go:250`) pins `feedback-3_validation-7_disjoint` | closed-validation sentinel file + hard CLI error; reviewed suite lock (unwired) | 06 |
| Atomic JSON publication | `writeJSONAtomic` (`ragopt.go:448`) | `writeGECRagoptJSONAtomic` (`knowledge_ragopt.go:1628-1651`) — the same temp-write/sync/rename function, written twice | 04 |

Two implementations of the same obligation with different mechanics (dimensions-as-lock versus lock-file-plus-dimension; tool-loop caps versus accountant object) are exactly the "same constraint, different shape" situation the Garden's comparison rule exists for. The constraint is confirmed; the shape is not yet standardized; that is what makes these kernel-absorption candidates rather than kernel features.

## 3. Lens two: the adopter contract for RAG products

### 3.1 What a product must implement

To run one paired experiment, a product supplies, at minimum:

1. **Two `Arm` implementations** — `Name()` plus `Run(ctx, Request) (Outcome, error)` (`pkg/eval/types.go:116-119`), receiving the case's opaque JSON input, exact repeat coordinate, a `CandidateView` of resolved run-owned assets, and a unique native directory; returning finite named metrics, coherent completion/contract/abstention flags, and a native artifact path inside the assigned directory (all enforced by `validateOutcome`, `runner.go:505-539`).
2. **A candidate bundle** — parent/child snapshots, one mutable asset, locked shared inputs (suite, policy, and whatever else the product freezes).
3. **A suite** — ordered opaque cases whose semantics only the product understands.
4. **A gate policy** — product-authored metric names, floors, target, regressions.
5. **A driver command** — Ragopt's CLI cannot execute anything (verified: `cmd/ragopt/main.go` registers exactly `candidate validate`, `compare`, and `report`); `eval.Run`/`eval.Resume` are library calls the product must wire to its own flags, engines, and credentials.
6. **Everything in §2.3** — if the product wants its results to mean anything.

### 3.2 Measured adapter surfaces

| Consumer | Non-test adapter LOC | Test LOC | Files |
|---|---|---|---|
| rag-ttc `cmd/rag-ttc/cmds/tooleval` | 851 (`ragopt.go` 475, `adapter.go` 165, `judge.go` 123, `product.go` 88) | ~240 | 4 + tests |
| CoinVault `cmd/coinvault/cmds/knowledge_ragopt*` | 3,053 (main 1,651; trace 413; contract 317; treatment 257; case, gate, reranker, suite-lock the rest) | 1,927 | 8 + tests |
| Ragopt kernel itself | ~6,400 | ~3,300 | — |

Both adapters exercise the same kernel API, so the 3.6× spread measures hardening, not integration difficulty: rag-ttc's 851 lines are close to the *minimum viable adopter* (arm, case decode, asset materialization, judge call, environment freeze, outcome projection), while CoinVault adds the strict trace collector, the deterministic answer contract, the treatment-proof subsystem, the budget accountant, and per-mechanism preflight — the production apparatus its Garden study documents. A third adopter should expect the rag-ttc number for a research posture and the CoinVault number for a production posture, minus whatever the evaluation-loops packages eventually absorb.

### 3.3 Convergent boilerplate versus genuinely product-specific code

Convergent (argues for kernel or shared-package absorption): environment/instrument freezing, treatment reporting hooks (a product-supplied `TreatmentReport` slot in the cell contract would let the kernel refuse to judge unattributable cells generically), budget accounting, split governance, the duplicated atomic-JSON writer, and case-input schema validation helpers. Genuinely product-specific (must stay out of the kernel): what an arm *does*, what metrics *mean*, trace vocabularies, contract stages, judge prompts, and every threshold. The kernel's discipline of keeping `Case.Input` and `Outcome.Metrics` opaque is correct and should survive any absorption — the extension point that is missing is not semantic interpretation but *structured slots for product-proven claims* (treatment exercised, environment verified, budget respected) that the kernel can then enforce the presence and consistency of, the way it already enforces outcome coherence.

### 3.4 Composition with Ragkit

The building-block picture is completed by what Ragopt does *not* contain: no retrieval, no chunking, no embedding, no judging. Both consumers compose it with [[Research/Software Architecture Garden/ragkit/README|Ragkit]] (retrieval primitives, index bundles, evidence types) strictly at the product layer — neither library imports the other, and Ragkit identities (bundle digests, chunk IDs) enter Ragopt only as opaque snapshot dimensions and native-artifact content. Two kernels with disjoint authority, composed by adapters, is the ecosystem's working answer to "RAG research platform": there is no framework, and the two Garden studies together document why that is a feature — each kernel's guarantees stay auditable precisely because the other's semantics never leak into it.

## 4. Lens three: running an experiment kernel in production

"Production" for Ragopt does not mean serving traffic; it means **operators run campaigns whose evidence must survive them**. Through that lens:

- **Operator workflow.** Create/execute/resume live in product CLIs (`rag-ttc tool-eval optimize`, `coinvault knowledge ragopt --resume-run …`); the kernel CLI handles the artifact half (validate a bundle, rebuild a comparison, render a report from a completed run). The split is coherent — the kernel cannot hold product credentials — but it means operational documentation, flags, and failure UX are re-invented per product.
- **Failure behavior.** An ordinary arm error becomes a durable failed cell and the campaign continues (`recordArmFailure`, `runner.go:479-503`); cancellation and deadlines propagate out with the run left active for exact resume (`:245-247`); any custody violation fails the run. These are the right defaults for long unattended campaigns, and CoinVault's per-cell deadline/termination classification builds on them rather than fighting them.
- **The single-writer boundary.** `Resume` documents that it takes no inter-process lock (`run.go:31-34`). In production this is a real exposure — a cron-driven resume racing a human's resume would interleave appends into one chain — and neither consumer has closed it. It remains the open obligation the README recorded, now with two production users.
- **Storage and retention.** Run directories accumulate under product-chosen roots (`experiments/ragopt-runs/…`, gitignored) with native artifacts that may embed sensitive product data. The kernel has no retention, redaction, or export machinery; nothing in either consumer does either. For a system whose value is durable evidence, the absence of a retention story is the largest unpriced production cost.
- **The shipped overclaim.** `report --help` at v0.0.1 still promises to "atomically write a Markdown review and JSON promotion plan" (`cmd/ragopt/commands/report/report.go:36`), while `report.Write`'s doc comment states plainly that POSIX has no two-path commit primitive and callers needing coherence must use a bundle directory (`pkg/report/write.go:13-17`). The library is honest; the CLI text is not; the tag shipped both.
- **The no-apply boundary holds.** There is no code path in v0.0.1 that mutates a product: the promotion plan's `review_required`/`human_apply_required` state is fixed, and both consumers' Garden studies confirm no apply command exists downstream either. As a production property this is the kernel's most valuable guarantee — an operator cannot mis-click a deployment out of an experiment tool.

## 5. Pattern maturity assessment

| Pattern or claim | Maturity | Evidence |
|---|---|---|
| Self-verifying run directories as the unit of reproducible research | Established | v0.0.1 runtime + strict readers + interruption test; two production consumers reading them back |
| Opaque case/metric contract with validated outcome coherence | Established | `validateOutcome` + both adapters projecting product semantics without kernel changes |
| Library-kernel-plus-product-driver CLI topology | Established | Verified kernel CLI surface; two independent product drivers |
| Environment/instrument freezing as a product obligation | Architecture debt (as a gap) / Candidate ecosystem pattern (as a mechanism) | Rebuilt twice with divergent conventions; broken revision linkage in one consumer |
| Revision identity via version-string parsing | Architecture debt | `ragoptRevisionFromVersion` rejects the tag its own dependency now uses; fails closed at CoinVault head |
| Treatment/budget/split hooks in the cell contract | Emergent | Convergent adapter code with no kernel slot; targeted by research projects 02, 04, 06 |
| Single-writer resume fencing | Open correctness obligation | Documented non-lock, unclosed by either consumer |
| Two-path report atomicity CLI claim | Architecture debt | Verbatim at v0.0.1 against the library's own honest comment |

## 6. Candidate ecosystem guidance

1. **Pin experiment kernels by content, not version syntax.** Freeze machinery that must verify a dependency's revision should record and check a content identity the toolchain preserves across tagging (module zip digest, or the origin hash in the module cache), never a substring of the version string.
2. **A kernel should expose typed slots for product-proven claims.** Treatment-exercised, environment-verified, and budget-respected are product proofs, but the *presence and shape* of those proofs is kernel-checkable, exactly as outcome coherence already is. Absorbing the slots (not the semantics) would delete the largest block of convergent adapter code.
3. **Adopters should budget by posture.** ~850 lines buys a research-grade adapter; ~3,000 buys a production-grade one. The delta is the five rebuilt subsystems, and it should shrink as the evaluation-loops packages land.
4. **An experiment kernel's production story is custody, not uptime.** Retention, redaction, and writer fencing are the production features that matter; none exist yet, and they should be designed before a third consumer multiplies the run-directory estate.

## 7. Open questions

1. Should `Cell` grow an optional, schema-versioned `ProductProofs` block (treatment report, environment attestation, budget ledger) that `finalizeRun` validates for presence-consistency, or should those remain sidecar files under `native/` with only digests in the cell? The first strengthens the journal; the second keeps `ragopt-cell/v1` stable.
2. What is the correct revision-identity fix for CoinVault's preflight — re-deriving from the module cache's origin metadata, digesting the vendored module zip, or moving the linkage entirely into the source lock? Each has a different trust ledger.
3. Which of the two environment-freeze conventions (self-digests as snapshot dimensions, rag-ttc; separate lock file cross-checked against one dimension, CoinVault) should research project 01's `instrumentlock` package canonicalize, and can it express both during migration?
4. Does the no-kernel-CLI-driver stance survive a third adopter, or does a `ragopt run` command with a plugin/exec-protocol arm become worth its trust cost once three products have written the same driver loop?
5. When run directories carry regulated product data, where does redaction live — arm-side before artifact hand-off (CoinVault's information-boundary precedent) or as a kernel export filter?

## Related studies

- [[Research/Software Architecture Garden/ragopt/README|Ragopt]] — the inside-out study of the same commit
- [[Research/Software Architecture Garden/ragkit/README|Ragkit]] — the composed retrieval kernel
- [[Research/Software Architecture Garden/coinvault/README|CoinVault]] — the production-posture consumer
- [[Research/Software Architecture Garden/rag-ttc/optimization/01 - Optimization Judging and Improvement Loops - Overview|rag-ttc — Optimization, Judging, and Improvement Loops]] — the research-posture consumer and extraction origin
- [[Research/Software Architecture Garden/Research/evaluation-loops/README|Evaluation-Loop Formalization Research]] — the six projects this study's convergent-boilerplate evidence feeds
