---
title: "Kiln: Canonical Emission, Reliable Test Gates, and Transpose Exports"
aliases: [Kiln Canonical Emission and Reliable Validation]
tags: [article, compilers, cuda, optimization, research]
status: active
type: article
created: 2026-10-31
repo: /home/manuel/code/wesen/kiln/worktrees/passnet
ticket: KILN-005
source_revision: e0f64dc
transpose_revision: 71fb43d
compiler_revision: e35aa8c
selection_revision: 58133d1
report_revision: b8881ac4b4124bc472162a5be4071035025cebdb
---

# Kiln: Canonical Emission, Reliable Test Gates, and Transpose Exports

Kiln now emits deterministic reduction names before generating CUDA, WGSL or simulator code. Eight previously observed name-only training contrasts become exact artifact matches without source normalization, while changed computations remain distinct in fresh-process regressions. The compiler also marks previous code-generation evidence stale and rejects child-spawn failures that the test runner could previously misreport as success.

The implementation passes thirty-two compiler test files with real subprocess execution, 108 canonical-emission CUDA comparisons and 117 transpose-source CUDA comparisons. A fresh, explicitly broader codegen/3 study compiles all 240 declared artifacts. Its training phase selects unchanged Kiln: variants identical to baseline tie exactly, and every executable-changing candidate is slower. This milestone improves the reliability of optimization feedback; it does not establish a faster compiler policy.

> [!summary]
> Canonical names now connect mathematical identity, emitted code and evidence. Validation fails closed when a test process never starts. Functional transpose and input-only exports close two source/execution gaps. The fresh study retains the default rather than choosing an apparent gain from generated-name noise.

## 1. Distinguish computation identity from executable content

A mathematical kernel identity describes the computation, shapes and storage types. An executable-content identity additionally describes the emitted source, launch configuration and code-generation version. Two kernels can share the first identity while having different source text. That is appropriate when code generation changes an implementation; it is undesirable when the only difference is a compiler-generated local variable name.

The preceding v7 audit found eight baseline/region-work pairs with equal per-kernel identity lists. Their CUDA artifacts became equal after renaming the entry symbol and generated reduction indices while preserving buffers, ABI, shapes and dispatch. The exact-fingerprint harness nevertheless measured the raw artifacts separately. Small timing differences between apparently equivalent computations could then influence policy selection.

The repair belongs before source hashing. Changing measurement aliases after observing timings would modify an experiment's declared rules. Applying a general regex equivalence rule in the evaluator would also create a new correctness obligation. Instead, the compiler now generates one deterministic binding form for the affected symbols.

## 2. Keep fresh symbols for substitution and canonical names for emission

Loop IR creates globally fresh reduction variables to avoid capture when expressions are inlined. Its expression keys already normalize bound variables using their binding structure. Reusing one reduction name during expression construction would undermine the substitution machinery; that was not the defect.

The defect occurred during Kernel IR materialization. Common serial reductions and cooperative row reductions emitted the original Loop IR symbol directly. An earlier call to the fresh-symbol generator could therefore change a later exported program despite leaving its mathematical identity unchanged.

The actual pre-fix regression shows:

```cuda
// One fresh-process compilation:
for (int r0 = 0; r0 < 17; r0 += 1) {
    in0 = src0[((17 * e) + r0)];
}

// Same computation after 97 unused fresh symbols:
for (int r97 = 0; r97 < 17; r97 += 1) {
    in0 = src0[((17 * e) + r97)];
}
```

The materializer now reuses `displayNames(schedule)`, the existing structural mapping that numbers reduction binders by scheduled appearance. It creates a shallow analysis view containing that mapping, without changing cached analysis or schedules.

```text
fresh Loop IR symbols
    -> schedule and analyze using original symbols
    -> bind canonical per-kernel names during materialization
    -> Kernel IR
    -> CUDA / WGSL / simulator source
    -> source hash and evidence content ID
```

Index environments still use the original symbol as the lookup key and the canonical emitted variable as its value. That separation preserves nested bindings. Scalar temporaries keep their own naming path, and register-tiled suffixes are applied after reduction-name canonicalization. There is no post-generation source rewrite.

## 3. Validate across independent compiler processes

A same-process comparison can conceal this bug. The global expression interner may return the first alpha-equivalent expression, including its original binder spelling. A test that constructs two renamed versions in one process can therefore pass while separate policy compilations still emit different text.

The regression uses independent Node processes with fresh-counter histories of zero and 97. Five cases exercise thread mapping, cooperative row mapping, shared staging, nested reductions and tiled matrix multiplication. For each case it compares the complete exported artifact, Kernel IR and CUDA/WGSL/simulator content identities. It also compiles an actual add-one variant and requires that computation's artifact and content to remain distinct. Per-kernel simulation validates the emitted programs numerically.

Before the repair, the first thread case fails with `exported artifacts must not depend on freshR history`, and the diff exposes r0/r97 in both the loop and address. After the repair, every case passes. This tests the compiler's executable output rather than testing a normalization helper.

## 4. Advance code generation and invalidate old evidence

The same mathematical kernel can now emit different source, so `CODEGEN_VERSION` advances from kiln-codegen/2 to kiln-codegen/3. Exported programs carry the new version. Evidence content IDs include it, and existing EvidenceStore rules mark previous-version records stale and nondecisive. A targeted regression checks the immediately preceding /2 version explicitly.

Mathematical kernel identities remain unchanged. Existing measurement records are neither retagged nor adopted as new-code evidence. The serialized program schema remains kiln-program/1 because buffer and dispatch interfaces do not change. Versioning records the source-generation boundary without inventing a new runtime ABI.

The independent fixture corpus is recompiled into 36 /3 artifacts under four region objectives. Three seeds over three structures and three dtypes produce 108 CUDA comparisons. Every comparison passes with unchanged dtype tolerances and input-immutability assertions.

## 5. Repair a validation gate exposed by the regression

The first attempt to launch the isolated workers failed for a different reason. In the restricted execution environment, spawnSync returned an error with code EPERM, empty stdout/stderr and status zero. The initial test tried to parse the empty output, producing an unexpected-end-of-JSON error. A recorded presence-only process probe captures the actual result fields.

The old Node runner checked status and signal but ignored the error field. In this environment that could label an unexecuted child as passing. The corrected acceptance condition is:

```javascript
const ok = !result.error && result.status === 0 && !result.signal;
```

Spawn errors are reported separately from process exits. The isolated regression also checks the spawn error before parsing output. A dedicated fault-injection test covers an executed success, an actual failing child and a synthetic status-zero spawn error. The last case must fail the aggregate gate.

All thirty-two compiler test files are then run with actual subprocess permission under the corrected runner. The log records their execution and successful completion. Historical status-only green output is insufficient if process creation was blocked, but this discovery does not prove that every historical run was blocked. The new run supplies direct current-state verification. The GPU receipts remain separate evidence from the Node runner.

## 6. Replay the observed failure population without rewriting history

The validation replay rebuilds only the twelve observed v7 training graphs under unchanged and region-work policies. It preserves the source corpus, numerical contract and policy definitions. Compilation reference checks stay enabled. There is no new timing, confirmation access or replacement selection.

All twenty-four artifacts compile, and every mathematical kernel identity matches its recorded prior value. Exact exported fingerprints are compared using the same serialization as the compiler driver; no regex or identifier normalization participates in the comparison.

| Training-pair property | Count |
|---|---:|
| Exact aliases before the repair | 2 |
| Known name-only contrasts | 8 |
| Known contrasts resolved into exact aliases | 8 / 8 |
| Exact aliases after canonical emission | 10 / 12 |
| Still-distinct pairs after canonical emission | 2 / 12 |

This is a repair validation on observed data, not new generalization evidence. The old /2 timing files, ranking and selected policy remain unchanged. The separate semantic-change regression checks that canonical binding does not collapse a changed computation.

## 7. Unify transpose binding and preserve view semantics

Preparing a fresh optimization population exposed an unsupported `torch.transpose` function even though tensor-method transpose already had a lowering. The importer now uses one implementation for tensor methods, the function and `aten.transpose.int`.

The shared lowering validates static integer axes, normalizes negative axes, checks the exact output shape and requires dtype preservation. Scalar transpose uses its scalar-valid axes and lowers to an identity reshape. Positional and keyword forms bind through the same argument rules, with duplicate and unsupported arguments rejected.

Transpose remains a view-semantic operation. It does not grant fresh-storage ownership to a later in-place mutation. The importer continues rejecting such a mutation unless its existing ownership conditions are met. This prevents a broader source binding from silently weakening alias correctness.

The importer suite passes twenty-five tests, including thirty-six valid binding/shape/dtype combinations plus invalid metadata, invalid axes, duplicate arguments and mutation-ownership rejection. Thirty-nine independent source programs then cover four transpose forms over batch/vector/scalar shapes and an additional batched-matmul consumer case across three dtypes. Their three-seed CUDA replay passes all 117 comparisons with unchanged checks.

No new transpose algorithm is copied from PyTorch. The binding expresses existing Kiln axis-exchange and reshape primitives. The full evaluation import audit remains 1,029 graphs and 51 complete families; this binding does not by itself increase original benchmark acceptance.

## 8. Export complete programs that contain no kernels

The transpose fixtures revealed another implementation gap. A vector transpose with identical axes, or a scalar identity view, can optimize to an input alias. The pipeline succeeds and no GPU kernel is needed. The export caller previously interpreted the absence of kernels as absence of a compiled program, yielding the uninformative `compile failed` diagnostic.

The compiler helper now recognizes a complete input-only graph when every node is an input and every output references one of those inputs. Such a graph can have a valid program object containing zero kernels. This does not redefine the existing `hasKernels` predicate or treat a failed run as successful.

The existing exporter already represents output/input buffer aliasing. The PyTorch pointer bridge reuses the supplied tensor for that buffer, and the launcher has no kernel to dispatch. Shape and dtype remain part of the contract. Focused tests cover scalar and vector identity exports in FP32, FP16 and BF16 and verify that ordinary arithmetic programs still contain kernels.

The failed fixture directory and pre-fix compiler helper are preserved before recompilation. The repair enables those cases rather than removing them from validation.

## 9. Declare a broader fresh population after preserving failures

The first v8 selector scans its declared 4,096-task bound and fills ten reduction slots but only five of ten matrix slots. A quota-preserving retry after the transpose binding has the same matrix shortfall. Both partial directories and their failure logs remain archived.

A new explicit declaration permits the full 4,476-task official training list and raises the matrix scalar-product bound from sixteen million to sixty-four million. All other resource bounds, exact-model exclusions and category quotas remain unchanged. The broader population fills twenty sources after 2,438 inspections: twelve training and eight confirmation graphs. Its membership is `c40f81bf05839042fd845dc797a6ddb3b8665d1f3d7b27f83cc5fb4d9cc27ca5`.

This is a new population declaration before timing, not a relabeling of the failed attempts. It retains exclusion of every previous policy model/program and all evaluation-set exact models. Architecture relatives may remain, and the population is still restricted to supported FP32 computations.

Training controls match unchanged/default and expose 85 multi-consumer attempts. Twelve candidate programs and the full reference/timing procedure are frozen before confirmation compilation. All 240 artifacts qualify from `e35aa8c` under codegen/3. The remote source snapshot exactly matches `f9c899e826b0f179b58105e0aa0f31ab538b34b79ad40e3aaa2151dcf68c9624`.

## 10. Evaluate the repaired identity path

The study uses the previously defined region grammar, explicit highest-precision FP32 native reference, separate compiler arithmetic and the same complete selection procedure. The timing budget remains twenty warmups, one hundred trials and three repeats with bounded stability retries. Exact artifact aliases share measurement evidence.

Three region variants are exact baseline aliases across all twenty graphs. Other variants change only a few training graphs. All training candidates qualify. Baseline, default and the three alias variants tie exactly at 1.0. Every executable-changing candidate is slower: scalar125 scores approximately 0.99856×; launch-prior variants approximately 0.98277×; work-only/scalar100/material1 approximately 0.97471×.

The declared baseline-first tie-break therefore selects unchanged Kiln. That selection and complete training evidence are committed in `58133d1` before confirmation timing. This is the intended behavior when search finds no better reusable program: retain the existing compiler rather than prefer an identity variant because of independently measured noise.

All eight confirmation graphs pass correctness and timing qualification. Only the committed unchanged compiler is executed. Both reported ratios are exactly 1.0 because baseline and selected policy are the same executable; no confirmation artifact changes and no partial fusions are selected. This is an identity comparison, not independent evidence of an optimization gain. The negative search is complete, and no altered policy is adopted.

## 11. Remaining work and review path

Original cumulative replay coverage remains eleven complete tasks and 206 individually passing graphs. Import eligibility remains 1,029 graphs and 51 complete families. These are distinct from fixture counts and from the new internal compiler-policy study. Exact paper reproduction, remaining operation/layout/dtype support, native reduced-precision compatibility and original PassAgent evaluation remain open.

The documented PassAgent provider environment variables are absent locally and on bling.local. Only presence flags were inspected after notice; no credential values were retained. The model/endpoint or existing-configuration question is pending while compiler work continues. No external-model inference or PassAgent reproduction result is claimed.

Primary review files are `kernel.js`, `records.js`, the corrected `run-node-tests.mjs`, the isolated worker regressions, `fx_indexing.py`, `fx_import.py` and the compiler helper's input-only detection. Design 13 describes the identity contract. Scripts 217–238 preserve replay, diagnostics, fixtures, source-declaration attempts, compilation and measurement. Updated reMarkable guide delivery remains separately pending after the earlier approval-review rejection; no new delivery is claimed.
