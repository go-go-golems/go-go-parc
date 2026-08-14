---
title: Suite Governance and Structurally Closed Splits
aliases:
  - suitegov research project
  - Governed ground truth and split hygiene
  - Digest-minting evaluation-set governance
status: proposed
type: architecture-garden-research
created: 2026-08-14
analyzed: 2026-08-14
repositories:
  - path: /home/manuel/workspaces/2026-08-12/deploy-dev-indexer/coinvault
    commit: 10d1a8d8c5b281f78b4e73d3956be573dcc8fad1
  - path: /home/manuel/workspaces/2026-08-12/deploy-dev-indexer/rag-ttc
    commit: 0b0e420925ec9919f2e89838b23df722cb5e3b3d
  - module: github.com/go-go-golems/ragopt@v0.0.1
    source: Go module cache
applies_to:
  - "[[Research/Software Architecture Garden/coinvault/README|CoinVault]]"
  - "[[Research/Software Architecture Garden/rag-ttc/optimization/01 - Optimization Judging and Improvement Loops - Overview|rag-ttc optimization loops]]"
  - "[[Research/Software Architecture Garden/ragopt/README|Ragopt]]"
tags:
  - architecture-garden
  - research
  - evaluation
  - ground-truth-governance
  - split-hygiene
  - append-only-ledger
  - hash-chain
  - go
  - mutation-testing
related_notes:
  - "[[Research/Software Architecture Garden/Research/evaluation-loops/README|Evaluation-Loop Formalization Research]]"
  - "[[Research/Software Architecture Garden/README|Software Architecture Garden]]"
---

# Suite Governance and Structurally Closed Splits

An evaluation suite is an input to every experiment that measures against it. Editing it in place does not add data — it silently changes what every future run measures, and every comparison spanning the edit becomes meaningless with nothing to indicate so. All three repositories in this research family know this, and each protects a different fragment of the resulting law: CoinVault digest-locks its eval set, ships a sentinel where its held-out validation suite would be, and carries a reviewed-suite lock — which nothing on its experiment command path actually calls. rag-ttc built an append-only proposal ledger whose `Commit` mints a new digest-named evaluation set — and takes no reviewer identity, so a proposal's own author can commit it. Ragopt computes dual suite digests with case order participating in identity — and has no governance at all, by design.

This project asks whether the whole law can be enforced by one small package rather than three partial conventions. The answer, on the evidence below, is yes for the structural core: a chain-verified proposal ledger, a two-principal commit that mints digest-named immutable sets, typed sentinels that make closed splits unloadable, and a run-side lock verifier that closes CoinVault's enforcement gap. The prototype `suitegov` package implements all of it in standard-library Go, passes fifteen tests, and kills all six seeded mutations — after the mutation harness itself caught a lesson about redundant guards, recorded in §5.

> [!summary]
> - Suite identity is an explicit projection: a semantic digest over normalized content in which case order participates (it controls execution) while group order does not; the byte digest remains a separate identity binding exact files.
> - Ground truth evolves only through an append-only, hash-chained proposal ledger; interior tampering or deletion is an error, not a dropped-line statistic, because governance evidence has a different corruption budget than telemetry.
> - Commit is a two-principal transition: a reviewer identity distinct from every selected proposal's author mints a new digest-named immutable set; the base set is never touched. rag-ttc's existing ledger lacks exactly this check.
> - A closed split is a typed sentinel in place of the data: no code path returns suite content from it, so accidental leakage requires bypassing the API, not ignoring a flag. Opening is an explicit transition carrying promotion evidence and leaving a durable record.
> - The run-side lock verifier states the law CoinVault's command path currently fails to enforce: the suite a run measures must be, provably, a reviewed suite — a bundle-locked SHA proves *a* suite, not *the reviewed* suite.
> - Prototype status: 15/15 Go tests pass, 6/6 mutations killed (`specs/suitegov/results/`). This is checked structural evidence for one implementation, not adoption evidence.

## 1. Research question

```text
Can ground-truth governance (digest-named evaluation sets evolving only
through reviewed, append-only proposals) and split hygiene (held-out data
inaccessible by mechanism until promotion criteria open it) be enforced as
structural properties of a small reusable package, rather than as
conventions distributed across product repositories?
```

Three sub-questions structure the work:

1. **Identity.** What exactly should participate in a suite's semantic digest, and why do the three repositories already agree more than their code suggests?
2. **Governance.** What is the minimal transition system under which every change to ground truth is visible as a digest change, attributable to two distinct principals, and tamper-evident after the fact?
3. **Hygiene.** What can a sentinel-based closed split actually exclude, stated without overclaiming?

## 2. Evidence in the three repositories

Every claim in this section was verified against the pinned checkouts by reading the cited code; the lock-caller and ledger-consumer claims were re-verified by grep during this project.

### 2.1 CoinVault: strong identity, closed split, unwired review lock

`LoadEvalSet` (`internal/knowledge/eval.go:56-89`) is the identity fragment: strict YAML with `KnownFields(true)`, rejection of trailing documents, an exact-version check, one-mode-per-question enforcement (`:103-115`), and a digest computed over the raw file bytes (`:87`). Note what this digest is: a **byte** digest. Reformatting a comment changes it. CoinVault accepts that coupling for the retrieval eval set; Ragopt shows the alternative below.

The closed split is the hygiene fragment. Each candidate bundle ships, in place of the held-out validation suite, the sentinel `{"api_version":"gec-validation-closed/v1","status":"closed","reason":"Feedback must pass and reproduce before the frozen held-out validation suite can be opened."}`, and `gecRagoptSplit` (`cmd/coinvault/cmds/knowledge_ragopt.go:316-326`) hard-errors on `--split validation`. Held-out leakage into the optimization loop requires forging suite bytes, not flipping a flag.

The review fragment is `gec-chat-suite-lock/v1` (`data/eval/gec-chat-v2-lock.yaml`): `review_status: approved`, `reviewed_on: 2026-08-08`, a `review_record` path, and per-split case counts plus **both** semantic and byte digests. Its validator `validateGECRagoptSuiteLock` (`cmd/coinvault/cmds/knowledge_ragopt_suite_lock.go:34-95`) checks review metadata, path confinement, byte digests against disk, strict-loads each suite through Ragopt, and compares semantic digest and case count. Grep confirms its only callers are `knowledge_ragopt_suite_lock_test.go:13` and `:43`. The `ragopt` command path pins its suite through the candidate bundle's locked-asset SHA instead — which proves the run used *a specific* suite, not that the suite was *the reviewed one*. Two further gaps: the lock has no reviewer identity field (a status and a date, but no principal), and nothing connects it to how the suite files came to change.

### 2.2 rag-ttc: the ledger, minus the reviewer

`internal/admin/feedback/judgment` is the governance fragment, and its package comment states the thesis this whole project builds on: a grade written from a UI lands in an append-only proposal log, "and nothing measures anything differently until someone commits. The commit produces a NEW evaluation set with a NEW digest, which is the point." The mechanics are careful:

- Proposals are validated **at propose time**, against the base set's judgments plus everything already pending, "not an hour later when someone commits a batch" (`judgment.go:144-191`).
- `Grade` is a pointer because absent and zero mean different things: grade 0 is explicitly irrelevant and counted; nil proposes the target be unjudged and removed from metrics entirely (`judgment.go:69-73`, `:363-371`).
- A later proposal for the same `(query, target, targetID)` supersedes an earlier pending one, so a hidden array-position rule can never decide which of two grades wins (`judgment.go:294-306`).
- `Commit` refuses to overwrite the base path (`commit.go:77-83`), validates the **result** rather than trusting individually-valid proposals (`commit.go:153-174` — the mixed-target check whose failure mode is a query silently erroring out of every metric), names missing proposal IDs instead of skipping them (`commit.go:192-201`), and records lineage in the new set's ID (`commit.go:224-233`).

Two properties are absent. First, `CommitRequest` (`commit.go:48-57`) carries base, path, and proposal IDs — no reviewer. `Proposal.Author` is recorded (`judgment.go:64`) and never compared to anything: the author of a proposal can commit it alone. Second, the fold tolerates undecodable lines by counting them as `Dropped` (`judgment.go:270-278`) — reasonable for telemetry-grade robustness, but it means a corrupted (or edited) interior record silently vanishes from pending state rather than halting governance. And the package has zero non-test consumers at the pinned commit (the only external reference is an import-rewriting migration script under `ttmp/`), so these are latent properties of a tested library, not operational incidents.

### 2.3 Ragopt: identity semantics, no governance

`LoadSuite` (`pkg/eval/suite.go`) contributes the identity discipline the prototype adopts wholesale: strict JSON with unknown-field rejection; case inputs canonicalized through `json.Number` so formatting cannot alter identity; groups deduplicated and **sorted** before digesting; case IDs pattern-restricted; and a semantic digest computed by marshaling the normalized suite — in which case order participates, because `Cases` is a slice and case order drives `buildSchedule`. The `SuiteDocument` carries `Digest` and `ByteDigest` side by side. Ragopt deliberately owns none of the governance above: it freezes and measures whatever suite it is handed, which is the correct boundary for a measurement kernel and is preserved in §7.3.

### 2.4 The synthesis target

| Property | CoinVault | rag-ttc | Ragopt | `suitegov` |
|---|---|---|---|---|
| Semantic digest distinct from byte digest | partial (byte-only for eval set; both in lock) | via ragkit digest of struct | yes | yes |
| Case order in identity | n/a (YAML order unscored) | n/a | yes | yes |
| Append-only proposal ledger | no | yes (drop-tolerant) | no | yes (chain-verified) |
| Reviewer ≠ author at commit | no (no ledger) | **no** (author recorded, unchecked) | n/a | yes |
| Digest-named immutable minted sets | no (fixed filenames + lock) | new file, digest reported | n/a | yes (digest in filename, `O_EXCL`+0444) |
| Closed split by sentinel | yes | no | no | yes (typed error) |
| Open transition with evidence | no (closed forever until code change) | no | no | yes (durable open record) |
| Run-side reviewed-lock binding | validator exists, **unwired** | no | no | yes (`BindRun`) |

## 3. Formal foundations

### 3.1 Suite identity as explicit projection

Let a normalized suite be $s = (v, n, \langle c_1, \ldots, c_k \rangle)$ with schema version $v$, name $n$, and an ordered sequence of cases $c_i = (\mathit{id}_i, G_i, x_i)$, where $G_i$ is a finite set of group names (stored sorted) and $x_i$ is a canonical JSON value. Let $N$ be the normalization function (strict decode, canonical inputs, sorted groups, validated identifiers) and $H$ the SHA-256 rendering. Define

$$
I_{sem}(s) = H(\mathrm{encode}(N(s))), \qquad I_{byte}(b) = H(b).
$$

Three laws follow from the definitions and are enforced by tests:

1. **Reserialization invariance:** for byte strings $b_1 \ne b_2$ with $N(\mathrm{decode}(b_1)) = N(\mathrm{decode}(b_2))$, $I_{sem}$ agrees and $I_{byte}$ differs (`TestSemanticDigestStableAcrossReserialization`).
2. **Order sensitivity where order has meaning:** cases form a sequence, not a multiset, because case order determines execution schedules downstream (Ragopt's runner iterates suite order); permuting cases changes $I_{sem}$ (`TestSemanticDigestSensitiveToCaseOrder`).
3. **Order insensitivity where order has none:** groups are sets; permuting them leaves $I_{sem}$ fixed (`TestSemanticDigestInsensitiveToGroupOrder`).

The projection is explicit in the sense of the Garden's identity discipline: what participates (version, name, ordered cases, canonical inputs, sorted groups) and what does not (whitespace, key order, file location) is decidable from the definition, not from folklore. Collision resistance of $H$ is assumed, as everywhere in this family.

### 3.2 The governance transition system

Ledger histories are words over hash-chained records. Each record $r_j$ carries the digest of $r_{j-1}$ (empty for $j = 1$) and its own digest computed with the digest field blanked — the same sealing shape as Ragopt's evidence cells. A history is **admissible** iff every record's own digest verifies and every predecessor link matches; the fold $F$ from admissible histories to pending state is total, with two operations: a later `propose` for the same case supersedes an earlier pending one, and `withdraw` deletes by proposal ID. Only an undecodable final line is tolerated (a torn tail from a crash mid-append), and it blocks further appends until explicitly repaired.

The commit transition is where authority enters. For base set $s$, pending selection $\Delta$, and reviewer $\rho$:

$$
\mathrm{commit}(s, \Delta, \rho) \text{ is admissible iff } \forall p \in \Delta:\; \mathrm{author}(p) \neq \bot \;\wedge\; \mathrm{author}(p) \neq \rho,
$$

and its result is a new set $s'$ with $I_{sem}(s') \neq I_{sem}(s)$, validated as a whole (not proposal-by-proposal), written exclusively to a filename derived from $I_{sem}(s')$, read-only. Because the filename embeds the identity, "silently replace the reviewed set under a stable name" is not an operation the system has; the closest expressible act is minting a visibly different set. This is the **two-principal rule**: a model or human may author any number of drafts, and no draft reaches committed on one identity. It is precisely the check rag-ttc's `Commit` omits and the field CoinVault's lock schema lacks.

### 3.3 The non-leakage statement, stated honestly

Let $P$ be a process that accesses split files only through `LoadSplit`, `BindRun`, and `OpenSplit`. Then:

- $P$ cannot obtain a `SuiteDocument` for a closed split: `LoadSplit` returns a typed `*SplitClosedError` and no suite value exists to flow onward. There is no boolean to ignore; the type system offers nothing to misuse.
- $P$ cannot bind a run to a closed split: `BindRun` yields the same typed refusal.
- $P$ can open the split only through `OpenSplit`, which requires the current file to be a sentinel (a split cannot be opened twice), requires four non-empty evidence fields (feedback run, gate-decision digest, approver, record), and leaves a durable `.opened.json` record binding the evidence to the suite digest it installed.

The mechanism does **not** exclude: a human reading held-out bytes wherever they exist (an editor, version-control history, a backup); a process that bypasses the package and parses files directly; a root user replacing read-only files; or an approver supplying hollow evidence — the package checks presence and shape, and whether the evidence *suffices* is the human decision the record makes auditable. The claim is deliberately modest: accidental leakage requires bypassing the API rather than ignoring a convention, and CoinVault's stronger deployment — the held-out bytes physically absent from the candidate bundle, a sentinel at their path — is exactly the deployment this package's file shape supports.

### 3.4 The review-lock law

Let $L$ be a lock with `review_status = approved`, reviewer identity $\rho_L$, and per-split reviewed identities. The law is:

$$
\text{a run measuring suite digest } d \text{ on split } \sigma \text{ is admissible iff } \mathrm{BindRun}_L(\sigma, d) = \mathrm{ok},
$$

i.e., $\sigma$ is present and open in $L$ and $d$ equals the reviewed semantic digest. CoinVault's current command path establishes something strictly weaker: the bundle's locked-asset SHA proves the run used the bytes the bundle froze — *a* suite — while nothing proves those bytes are the suite a reviewer approved. The two statements coincide only while humans keep the bundle and the lock synchronized by hand, which is a convention, which is the thing this project exists to remove.

## 4. The `suitegov` package

### 4.1 Shape

```text
specs/suitegov/
├── go.mod            module github.com/go-go-golems/garden-research/evaluation-loops/suitegov
├── suite.go          Suite/Case, strict load, normalization, SemanticDigest / ByteDigest / Identity
├── ledger.go         hash-chained append-only proposal ledger (propose / withdraw / load-and-verify)
├── commit.go         two-principal Commit minting digest-named immutable sets
├── split.go          ClosedSentinel, SplitClosedError, OpenSplit with PromotionEvidence
├── lock.go           reviewed-suite Lock, Verify (preflight), BindRun (the missing CoinVault arrow)
├── suitegov_test.go  15 tests
├── mutate.sh         6-mutation sensitivity harness
└── results/          test.txt, mutation.txt (captured runs)
```

Standard library only. Product adapters own YAML parsing, principal authentication, and non-local storage. Nominal types (`SemanticDigest`, `ByteDigest`, `Identity`) keep the digest families from being interchanged silently — the confusion Ragopt's `policy_digest` history warns about.

### 4.2 Design decisions and their contrasts

**Chain-verified, not drop-tolerant (contra rag-ttc).** rag-ttc's fold counts undecodable lines and continues; this ledger treats an interior undecodable, tampered, or missing record as an error that halts governance, tolerating only a torn final line — and even that blocks appends until repaired. The rationale is the corruption budget: a dropped telemetry line loses one observation; a dropped governance record changes which proposals a reviewer is approving. rag-ttc's own hash-chained ancestor here is Ragopt's cell journal, which made the same strictness choice for evidence.

**Reviewer at commit, not at propose.** Authorship freedom is the point of a proposal ledger — a generation model may draft cases, an operator may propose from a UI. Authority concentrates at the single transition that changes what runs measure. Checking `author ≠ reviewer` per selected proposal (rather than per batch author set) means a mixed batch cannot smuggle the reviewer's own draft through under a colleague's.

**Digest-named minting with a doubled guard.** The minted filename embeds the semantic digest and the file is created with `O_EXCL` and mode 0444. Either layer alone prevents silent replacement for non-root users; both together survive the failure of either. §5 records how mutation testing initially mistook this redundancy for a coverage gap.

**Result validation, not proposal validation (with rag-ttc).** `Commit` re-normalizes the whole applied suite; a batch of individually valid proposals that jointly retire every case, or add a duplicate, fails at the commit boundary with a named reason. This copies rag-ttc's mixed-target lesson: the collectively-wrong batch is the failure nothing downstream reports as a governance failure.

**Sentinels replace bytes; opening is evidence-carrying.** `LoadSplit`'s closed result is a typed error, not a flagged document. `OpenSplit` extends CoinVault's mechanism (where opening validation currently requires a code change) into a governed transition: sentinel in, evidence recorded immutably, suite installed atomically by rename.

### 4.3 The preflight embedding

`Lock.Verify(root)` is written to be called where CoinVault's `validateGECRagoptEnvironment` already runs — before any spend — and `Lock.BindRun(split, observedDigest)` is the one-line law the run path then applies to the suite it actually loaded. Together they close the gap of §2.1: bundle SHA proves custody; `BindRun` proves review.

## 5. Implementation results

All commands ran from `specs/suitegov/` at the paths above; raw output is in `results/`.

```text
GOWORK=off go vet ./...        → clean
GOWORK=off go test ./... -count=1 -v
  15 tests, all PASS (identity ×4, ledger ×4, commit ×3, split ×2, lock ×2)
  ok github.com/go-go-golems/garden-research/evaluation-loops/suitegov 0.029s

./mutate.sh
  KILLED    M1-self-approval-bypass      (reviewer==author check disabled)
  KILLED    M2-minted-set-overwrite      (refuse-overwrite mechanism disabled)
  KILLED    M3-ledger-digest-skip        (own-digest verification disabled)
  KILLED    M4-ledger-chain-skip         (predecessor-link verification disabled)
  KILLED    M5-sentinel-ignore           (closed-split detection disabled)
  KILLED    M6-bind-run-skip             (reviewed-digest comparison disabled)
  PASS: all mutations killed
```

One finding from the harness itself is worth preserving. The first version of M2 removed only `O_EXCL` from the minting call — and **survived**: the file mode 0444 still made the overwriting open fail with `EACCES` for non-root users, so the re-commit test passed for the wrong reason and could not distinguish which guard was working. The mutation was rewritten to disable the *mechanism* (both `O_EXCL` and the read-only mode), and was then killed. The general rule, which transfers to every project in this family: **a mutation must disable a mechanism, not one layer of a redundantly implemented mechanism** — a surviving mutant is sometimes a redundancy discovery rather than a coverage gap, and the harness comment now records which. This mirrors, at small scale, the sessionstream program's insistence that the bridge itself needs sensitivity testing.

## 6. Guarantee taxonomy

| Evidence | Establishes | Does not establish |
|---|---|---|
| Identity tests | The semantic digest is invariant under reserialization and group order, sensitive to case order, on the tested inputs | Collision resistance; that products digest the same projection until they adopt the package |
| Chain-verified ledger + tamper/deletion tests | Interior rewriting or deletion of retained records is detected at load; a torn tail is reported and blocks appends | Signed authenticity; immutable media; protection against rewriting the *entire* chain from genesis by an actor with file access |
| Two-principal commit + M1 | No selected proposal's author can be the committing reviewer, and removing the check fails tests | That `Identity` strings correspond to authenticated principals; collusion between two real people |
| Digest-named `O_EXCL`/0444 minting + M2 | Minted sets cannot be silently replaced under POSIX semantics for non-root users; re-commit of identical content is an explicit error | Root or filesystem-level replacement; durability beyond fsync of the file itself |
| Typed sentinel + M5, evidence-carrying open | In-API access to a closed split is impossible; opening requires evidence fields and leaves a durable record; a split cannot open twice | Out-of-band byte access (VCS history, backups, humans); sufficiency of the evidence a human supplies |
| `Lock.Verify` + `BindRun` + M6 | Review metadata, byte/semantic digests, and case counts verify against disk; a run binds only to the reviewed digest of an open split | That any product currently calls it (adoption is §7); the quality of the review the lock records |
| Mutation harness (6/6 killed) | Each protected mechanism has at least one test that fails when the mechanism is disabled | Sensitivity to mutants not seeded; equivalence of this implementation to future adopters' ports |

This is checked structural evidence for one prototype implementation. Nothing here is a universal proof, an authentication system, or adoption evidence.

## 7. Adoption paths

### 7.1 CoinVault: wire the existing lock into preflight

The smallest change closes the enforcement gap with no new machinery: call `validateGECRagoptSuiteLock(ctx, repositoryRoot, "data/eval/gec-chat-v2-lock.yaml")` from `validateGECRagoptEnvironment`, then compare the candidate bundle's loaded feedback-suite semantic digest against the lock's reviewed digest — the `BindRun` law, expressible today in about ten lines against the existing validator. Two schema follow-ups: add a `reviewer` identity field to `gec-chat-suite-lock/v1` (the lock currently records a date and a record path but no principal), and record in the lock which sentinel byte digest stands for the closed validation split, so the sentinel itself becomes reviewed content. Migrating to `suitegov` proper can follow or not; the law matters more than the package.

### 7.2 rag-ttc: a reviewer for the ledger, and a first consumer

`judgment.Commit` should take a `Reviewer` identity and reject any selected proposal whose `Author` equals it — a breaking change that costs nothing while the package has zero non-test consumers, and one the package's own proposal/author vocabulary already anticipates. Separately, the drop-tolerant fold deserves one guard at the authority boundary even if telemetry-grade tolerance is kept for reads: `Commit` should refuse when `Index.Dropped > 0`, because approving a batch folded from a partially-unreadable log approves an unknown selection. Giving the ledger its first consumer (the admin grading UI it was built for) would move the pattern from tested-library to operational, which is what its Garden maturity currently lacks.

### 7.3 Ragopt: absorb nothing into the runner

The measurement kernel's boundary is correct as it stands: Ragopt freezes and measures the suite it is handed and should not gain a proposal ledger, reviewer identities, or split registries — that would merge governance authority into the evidence custodian, the exact authority-merge the Garden's studies repeatedly flag. What Ragopt could reasonably export is identity: nominal `SemanticDigest`/`ByteDigest` types and its canonicalization as a reusable function, so governance packages and products digest the same projection. A `suitegov`-shaped module belongs beside Ragopt, handing it reviewed suites, with the lock's reviewed digest recorded as a run input the same way policy bytes are today.

## 8. Decision records

**DR-1: Chain-verified ledger, torn tail only.** Considered rag-ttc's drop-tolerant fold. Rejected for governance records because a silently vanished proposal changes what a reviewer approves; retained the single-torn-tail allowance because a crash mid-append is a legitimate state that must not brick the ledger, and an explicit repair keeps the decision human. *Status: implemented in prototype.*

**DR-2: Reviewer checked per selected proposal at commit.** Considered batch-level checks (reviewer ∉ authors of batch) and propose-time review. Per-proposal at commit is strictly stronger than batch-level for mixed batches and keeps authorship cheap. *Status: implemented; mutation M1 guards it.*

**DR-3: Sentinel replaces bytes rather than gating them.** Considered encrypted or flag-gated held-out data. Absent bytes are the only variant whose failure mode is "cannot read" rather than "forgot to check"; it matches CoinVault's shipped mechanism and costs an explicit, evidence-carrying `OpenSplit`. *Status: implemented; M5 guards detection.*

**DR-4: Digest-named exclusive read-only minting.** The filename is the identity claim; `O_EXCL` and mode 0444 are redundant layers, deliberately kept after the M2 lesson. *Status: implemented; M2 (strengthened) guards the mechanism.*

**DR-5: Standard library only; identities opaque.** Authentication, YAML, and remote storage are product concerns; importing them here would couple governance to one product's stack and overstate what the package proves about principals. *Status: implemented.*

## 9. Risks and limits

- **Same-principal filesystem trust.** Everything here assumes the local filesystem is not adversarial beyond accident: root, editors, and whole-chain rewrites from genesis defeat all of it. The chain detects tampering *within* a retained history, not replacement *of* the history. Signing is future work, and claiming it prematurely would repeat the overclaim failures this Garden documents elsewhere.
- **Identity ≠ authentication.** `author-1 ≠ reviewer-1` is a string comparison. The two-principal rule is only as real as the caller's principal handling.
- **Supersede-by-case granularity.** One pending proposal per case means add-then-amend collapses to the amendment, which then fails at commit if the case is not in the base. Acceptable for review-sized batches; a composing ledger would need explicit proposal dependencies.
- **Single-writer ledger.** Like Ragopt's resume, writer exclusion is left to the operator; concurrent processes appending to one ledger file are unfenced. An adopter with multi-writer needs must add a lock file or serialize through a service.
- **Open transition is two files.** The `.opened.json` record and the renamed suite are individually durable but not one atomic publication; a crash between them leaves an evidence record for a split that still shows the sentinel — recoverable and honest (evidence without effect), but worth stating.

## 10. Open questions

1. Should the minted set embed its own provenance (base digest, ledger head, reviewer) in the file rather than only in the `CommitResult`, making every suite self-describing at the cost of digest entanglement between content and history?
2. Is a `Dropped > 0 ⇒ refuse commit` guard sufficient for rag-ttc, or should its judgment ledger migrate to chain verification outright once it has a real consumer?
3. Where should the reviewed lock live relative to candidate bundles in CoinVault — one repository-level lock the preflight cross-checks against bundle assets (proposed here), or a per-bundle lock that travels with the frozen inputs?
4. Does the two-principal rule need an n-of-m generalization for higher-stakes corpora, and does that belong in this package or in the product's review workflow?
5. Can the `OpenSplit` evidence fields be bound to Ragopt gate-decision artifacts mechanically (digest equality against `results/gate-decision.json`), turning "feedback must pass first" from prose into a checked precondition?

## 11. Working rules

- Change ground truth only through a transition that mints a new digest; an in-place edit to a measured suite is a defect, not a shortcut.
- Record authors on proposals and require a distinct reviewer at commit; no draft reaches committed on one identity.
- Treat governance-log corruption as an error and telemetry-log corruption as a statistic; do not let one discipline's tolerance leak into the other.
- Represent closed splits by absence plus a typed sentinel, never by a flag beside present data.
- Open a held-out split only through a transition that records its evidence durably before installing the data.
- Bind every run to the reviewed suite digest at preflight; custody of bytes is not proof of review.
- When a mutation survives, first ask whether the mechanism is redundant before concluding the test is missing; then mutate the mechanism, not the layer.

## Related notes

- [[Research/Software Architecture Garden/Research/evaluation-loops/README|Evaluation-Loop Formalization Research]] — the family index and overlap analysis
- [[Research/Software Architecture Garden/coinvault/README|CoinVault]] — sentinel mechanism, eval-set identity, and the unwired lock this project closes
- [[Research/Software Architecture Garden/rag-ttc/optimization/01 - Optimization Judging and Improvement Loops - Overview|rag-ttc — Optimization, Judging, and Improvement Loops]] — the proposal ledger and its zero-consumer status
- [[Research/Software Architecture Garden/ragopt/README|Ragopt]] — suite identity semantics and the measurement-kernel boundary preserved here
- [[Research/Software Architecture Garden/sessionstream/designs/research/02 - Constraining the Go Binary - Layered Refinement from Proved Kernels to Executables|Sessionstream — Constraining the Go Binary]] — the guarantee-taxonomy and mutation-sensitivity conventions this document follows
