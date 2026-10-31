---
title: "Kiln: Whole-Region Fusion Planning, Model Proof, and Fresh Evaluation"
aliases: [Kiln Region Planning and Generated Name Evidence]
tags: [article, compilers, cuda, optimization, research]
status: active
type: article
created: 2026-10-31
repo: /home/manuel/code/wesen/kiln/worktrees/passnet
ticket: KILN-005
source_revision: 4523355
compiler_revision: 114d90b
selection_revision: cff6a69
report_revision: d3e51e3d4e351226c77f817399fb8d45bfb8a377
---

# Kiln: Whole-Region Fusion Planning, Model Proof, and Fresh Evaluation

Kiln now compares complete fusion-region alternatives rather than deciding every consumer edge independently. The planner considers keeping the producer, removing it by fusing every consumer, and retaining it while selecting the cheapest proper subset under an additive model. A linear search matches exhaustive enumeration in 280 small scenarios. Thirty compiler test files pass, and 108 CUDA fixture comparisons pass across FP32, FP16 and BF16.

The fresh experiment produces 240 qualified artifacts. Training selects `region-work` at 1.008665×, but confirmation measures 0.990099× end-to-end and 0.986548× stream elapsed relative to unchanged Kiln. All eight confirmation graphs pass correctness. The candidate is not adopted. A separate training-only audit also identifies generated-name differences that cause the exact-fingerprint harness to time apparently equivalent CUDA computations separately. That issue limits interpretation of small timing margins and becomes the next implementation priority.

> [!summary]
> This milestone establishes a locally optimal planner for a declared additive model, consolidates the compiler selection interface and experiment harness, and completes a negative fresh evaluation. It also exposes an evidence-identity problem that must be fixed before small performance differences can guide reliable optimization.

## 1. Producer removal is a joint decision

A producer kernel computes a tensor used by several consumer kernels. Fusion substitutes the producer expression into a consumer, eliminating that consumer's load of the intermediate tensor. If every consumer is substituted, the producer becomes unused and can disappear. If any consumer remains, the producer still executes and materializes its output.

An independent edge test can miss the benefit of complete fusion. Suppose the producer costs ten work units and two consumers each cost ten. Substitution makes each consumer cost fourteen. Each edge grows in isolation, but substituting both consumers costs twenty-eight instead of thirty because the producer disappears. Rejecting both edges before considering their joint effect loses this profitable model choice.

The opposite accounting error credits producer removal even when an unselected consumer still needs it. The preceding compiler milestone fixed that error in the aggregate guard. This milestone uses the same retained-producer semantics to compare complete candidate plans before mutation.

The implementation extends the existing loop-IR inliner and graph transaction system. It introduces no second graph evaluator, runtime dispatch mode or tensor execution bridge. The standard compiler policy remains unchanged.

## 2. Derive a linear search from the additive model

Let P be producer work, C_i original consumer work and F_i consumer work after substitution. For selected subset S of the direct consumers U, the affected-region work is:

\[
W(S)=\begin{cases}
\sum_i F_i,& S=U,\\
P+\sum_{i\in S}F_i+\sum_{i\notin S}C_i,& S\ne U.
\end{cases}
\]

The empty subset retains the original graph. A nonempty proper subset retains the producer and every consumer. Complete fusion removes only the producer within this local region. Consumer output shapes remain unchanged by substitution.

The declared surrogate objective adds kernel-count and materialized-output priors:

\[
J(S)=W(S)+L\,K(S)+M\,V(S).
\]

K counts kernels in the affected region, V counts their materialized output elements, and L/M are nonnegative weights in surrogate-work units. They are not measured nanoseconds. The base work estimator already weights memory accesses; M is an additional experimental prior about output materialization, not an independent physical memory model.

Every proper subset has the same kernel count and materialized output volume: the producer and all consumers remain. Its variable objective term is therefore the sum of consumer-work deltas. Selecting every negative delta minimizes that term. Complete fusion must still be evaluated separately because it removes the producer's work, one kernel and its output volume.

The search compares only three candidates:

- The empty selection preserves the original graph.
- Complete selection substitutes every consumer and removes the producer.
- The negative-delta selection minimizes the retained-producer objective.

This takes O(m) time for m consumers after proposed expressions are scheduled. The planner applies the work-growth bound before choosing a candidate. If the minimum-work proper subset fails that upper bound, every other proper subset fails too. Complete selection is checked separately. Exact ties preserve the original graph; a tie between improving complete and partial candidates prefers complete fusion.

This proof depends on the local additive model. Consumer substitutions must have independently evaluated costs, the region must have the stated liveness behavior, and no effects or alias writeback may alter the dependency model. It does not prove global compiler optimality or predict later scheduling, caching, occupancy or actual GPU latency.

## 3. Consolidate selection into one compiler interface

The earlier factory accepted a callback for one consumer at a time. Keeping that callback alongside a separate whole-region mechanism would create parallel interfaces for the same mutation. The current factory instead exposes one canonical callback:

```javascript
std.loop.createFusionRule({
  selectConsumers: region => std.loop.chooseFusionSubset(region, {
    launchWork: 32768,
    materializationWork: 12,
    maxWorkGrowth: 1.02
  })
});
```

The callback receives a frozen producer description and a frozen array of proposed consumer costs. It returns distinct valid indices into that array. Replacements are built before editing the graph, so every decision observes one graph state. Empty selection skips the rewrite. Selected replacements use the existing `inlineInto` function, including input remapping, coordinate substitution and fresh reduction binders.

The old singular `selectConsumer` option now fails explicitly. There is no compatibility alias. Current tests and integration callers use the region interface. Historical scripts retain their original code and remain reproducible against their pinned compiler revisions. The default factory still selects every consumer, and the standard pipeline uses its previous aggregate bound.

After mutation, ordinary dead-code elimination retains or removes the producer. The existing aggregate guard checks actual pre/post region work, including a producer that remains live, and rejection restores the transaction. The pure planner is in `packages/kiln/src/std/fusion.js`; graph mutation remains in `loop.js`.

The planner validates finite nonnegative costs and rejects overflow. It sums the chosen costs directly instead of subtracting large nearly equal totals. The returned index array is immutable. Invalid indices, duplicate selections and unknown rule options produce explicit errors.

## 4. Expose bounded region programs

The policy language gains a region kind containing an aggregate work bound and launch/materialization weights. It cannot contain either decision tree. The weights are copied into immutable closures and bounded before compilation; the integration's two-times hard aggregate work cap remains available as a final safeguard.

Existing serialized selective policies retain their meaning. Their interpreter evaluates the consumer tree over the region array and returns selected indices through the same compiler interface. This consolidates implementation without silently supporting the removed singular callback.

The experiment declares eight region models using weight pairs:

| Model | Launch work | Extra materialization work per element |
|---|---:|---:|
| Work only | 0 | 0 |
| Small launch prior | 4,096 | 0 |
| Medium launch prior | 32,768 | 0 |
| Large launch prior | 262,144 | 0 |
| Small materialization prior | 0 | 1 |
| Larger materialization prior | 0 | 12 |
| Medium mixed prior | 32,768 | 12 |
| Large mixed prior | 262,144 | 12 |

All use a 1.02 work-growth bound. Unchanged/default and scalar100/scalar125 provide four controls, yielding twelve candidates. This is a fixed grammar authored by the current Codex session from training structural evidence. It is not an external PassAgent run or a learned hardware latency model.

## 5. Validate mathematical and numerical claims separately

The pure planner is compared against independent enumeration of every subset in 280 deterministic cases with up to seven consumers. The tests vary work bounds and both priors. Explicit cases cover joint producer elimination, a genuinely partial optimum, exact ties, inadmissible complete plans, invalid inputs and overflow. The exhaustive oracle checks the objective of the chosen result rather than reproducing the linear algorithm.

Graph tests separately verify unselected consumer identity, retained producers, output structure, empty skips, rollback, repeated operands and nested reductions. Policy tests execute the region program through the real compiler. At the first boundary all thirty compiler test files and all seventy-four then-existing Python integration tests pass. Six targeted proposal tests pass after adding the new proposal-generator case.

Nine frozen independent source equations are compiled under four region objectives, producing 36 artifacts. Normal reference checking and separate elementary FP32 arithmetic remain enabled. Three seeds produce 108 CUDA comparisons across three structures and three dtypes; all pass, including unchanged-input assertions.

The independent checker has moved from ticket script 189 into shared `check_fusion_cuda.py`. Its equations, seeds and tolerances remain unchanged. No native normalization, matrix or reduction implementation is copied into Kiln for this milestone.

## 6. Freeze a fresh source population and shared procedure

The v7 selector excludes exact models and generated programs from every prior policy corpus, including v6, and excludes exact models in the full 200-task evaluation set. It uses a new declared salt while retaining the previous resource bounds and per-category quotas. Twenty sources are selected after 2,255 task inspections: six matrix and six reduction graphs for training, followed by four of each for confirmation.

Membership is `9cdb2cf0b136d36491e5a3cf9057219866531921a84b26dacfa42261467e55c1`. Exact-model exclusions are weaker than architectural independence; related architectures can remain. This is a constrained FP32 development population, not full PassNet coverage.

Training controls compile identically under unchanged and explicit-default modes, with 69 multi-consumer attempts in default traces. Candidate programs and the complete procedure are frozen before confirmation compilation. Shared commands now own control preparation, declaration, full compilation, remote source verification and final study verification. Numbered ticket scripts record exact invocations rather than duplicating those mechanisms.

All 240 artifacts qualify from revision `114d90b`. Remote source bytes match compilation snapshot `c7c59a00a250d8e637dcb4b400467ee41e6015818a8878ebaadc0a03d75f780c`. No candidate is filtered out. The reference uses highest-precision FP32 PyTorch matrix operations and separate compiler arithmetic from the outset. This is explicitly a modified research protocol, not native PassBench acceptance.

The timing budget remains twenty warmups, one hundred trials and three repeats, with bounded stability retries. Exact executable fingerprints share measurements. Selection maximizes the family-balanced geometric mean of synchronized end-to-end ratios relative to unchanged Kiln, with declaration-order exact ties and zero compile-cost weight.

## 7. Complete the declared evaluation

Every training candidate qualifies. `region-work` scores 1.0086653425× and ties exactly with four region variants sharing its training fingerprints. Declaration order selects the work-only program. Selection and full training evidence are committed in `cff6a69` before confirmation timing.

All eight confirmation graphs qualify. Only unchanged Kiln and the committed selection are timed.

| Quantity | Observed result |
|---|---:|
| Training selected end-to-end ratio | 1.008665× |
| Confirmation end-to-end ratio | 0.990099× |
| Confirmation stream-elapsed ratio | 0.986548× |
| Confirmation failures | 0 / 8 |
| Selected partial fusions, training / confirmation | 0 / 0 |

The end-to-end ratio corresponds to approximately one percent more elapsed time. The stream metric also regresses. One DistilBERT graph measures approximately 0.91020×, while the remaining graph ratios are near one. The result does not justify adopting this policy as a default.

No region program accepts a retained-producer proper subset on training, and the selected program accepts none on confirmation. The implemented planner can select proper subsets in its validated cases, but this measured population primarily exercises keep-versus-complete decisions. It cannot establish a speedup from accepted partial fusion.

## 8. A generated-name diagnostic limits interpretation

During training, before any confirmation timing, a separate source audit compares artifacts after a deliberately narrow normalization. It renames only the kernel entry symbol and generated r-number reduction identifiers. CUDA ABI, buffers, dispatch, shapes and the remaining source are retained. Eight selected training artifact changes then equal baseline under this comparison. Those eight cases also retain the same per-kernel identity lists, locating the discrepancy in emitted artifact source rather than a changed kernel identity.

The frozen harness uses exact fingerprints. Source that differs only in generated identifiers can therefore receive separate measurements and contribute nuisance timing contrasts to a small training margin. The diagnostic does not compare machine code or prove arbitrary semantic equivalence. It identifies a concrete class of apparently equivalent generated computations that the current exact identity misses.

The audit is training-only and descriptive. It does not change aliases, latency samples, ranking, selection or confirmation membership. Reclassifying aliases after measurements and choosing a new winner would change the experiment. The original result remains archived and the final summary carries the limitation explicitly.

The next implementation should canonicalize generated identifiers in compiler IR or emission and align artifact identities with that canonical form. The diagnostic regular expressions should not become a general-purpose production semantic-equivalence checker. Code-generation and evidence versioning must be considered together so old timings are not silently reused for changed generated sources.

This issue does not invalidate numerical acceptance or import eligibility. It limits interpretation of small performance differences between reduction-containing generated implementations. The current negative result remains negative; no improvement is claimed from the confounded training margin.

## 9. Current state and continuation

The compiler has a tested region planner, a single selection interface and a consolidated experiment harness. The fresh study is complete and negative. The default remains unchanged. Before another small-margin policy search, generated-name canonicalization and evidence identity should be fixed and validated, followed by a newly declared evaluation population.

Original replay coverage remains eleven complete tasks and 206 individually passing graphs. Import eligibility remains 1,029 graphs and 51 complete families. Original PassAgent evaluation, remaining operation/layout/dtype support, native reduced-precision compatibility and broader transformation synthesis remain open. The GB10 software environment also differs from the paper's A30 setup, so this is not an exact paper reproduction.

For review, begin with design 12, `std/fusion.js`, `fusion-region.mjs`, the current `createFusionRule` and `fusion_policy.mjs`. Scripts 203–214 preserve the execution sequence. Run script 213 with selection commit `cff6a69` to verify declarations, artifacts, reference flags, source identity and committed selection. Script 214 reconstructs the training-only naming diagnostic without altering measurements. The detailed diary records implementation, commands, assumptions, source revisions and failures.
