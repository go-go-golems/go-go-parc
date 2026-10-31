---
title: "PassNet and Kiln: From FX Semantics to CUDA Execution"
aliases: [Kiln PassNet First GPU Milestone]
tags: [article, compilers, cuda, pytorch, research]
status: active
type: article
created: 2026-10-30
repo: /home/manuel/code/wesen/kiln/worktrees/passnet
---

# PassNet and Kiln: From FX Semantics to CUDA Execution

The first Kiln–PassNet milestone establishes a working path from a PyTorch computation graph to Kiln-generated CUDA executed on PyTorch storage. It also establishes a separate limitation: a correct CUDA computation does not automatically become an accepted PassBench compiler pass. The original evaluator has structural matching and source-validation requirements beyond numerical correctness.

This report explains the implementation and the evidence available at commit `a52fa93`. The project remains active. There is no verified full-benchmark Kiln score or measured reusable compiler improvement yet.

## 1. Define the experimental object

A computation graph records operations and the tensors they consume. PyTorch FX represents each operation as a node with a target, positional arguments, keyword arguments and users. A compiler pass identifies a graph fragment and replaces it with another implementation. PassNet evaluates reusable passes across multiple variants of an operation pattern, rather than evaluating just one kernel on one input shape.

Kiln uses its own representations for tensors, loops, scheduling and GPU execution. Integrating the systems therefore requires both semantic translation and an execution interface. The translation must preserve tensor shapes, dtypes, broadcasting and output structure. The execution interface must preserve storage ownership and CUDA stream ordering.

Two experiments remain distinct. The reference experiment runs pinned PassNet without Kiln changes. The integration experiment uses Kiln implementations within a declared evaluation protocol. Changes to protocol must be reported explicitly because their results answer a different experimental question.

## 2. Establish source provenance before execution

The reference checkout is pinned to PassNet revision `61c64709f6d324216ae8252cec3cdc35b2dd5da5`; the Hugging Face dataset is pinned to `4f7dd9211178327c2718f1b828d83ea126186f9e`. All fourteen Parquet shards were verified against published file sizes and LFS SHA256 values. Their combined size is 966,502,583 bytes.

The Parquet schema consists of string fields `path`, `content` and `source_folder`. Materialization reconstructs files without executing them. It rejects escaping paths and conflicting duplicates, records per-file hashes and preserves source-folder attribution. The completed extraction contains 2,067,810 records and reports zero duplicate records. Independently, the Git checkout contains all 200 evaluation tasks and their 2,060 referenced graph directories.

These counts represent different units. A dataset file-content record is not a graph and a graph is not a task. Reporting file counts as workload coverage would substantially misstate the experiment.

The acquisition and materialization procedures are saved in ticket KILN-005 scripts 01 and 03. The complete inventories and compact receipts are under its sources directory. Large corpus files remain locally archived there rather than being added to Git.

## 3. Translate graph structure explicitly

`integrations/passnet/fx_export.py` exports a versioned `kiln-fx/1` structure. Each node retains its identifier, kind, target, arguments, keyword arguments and tensor metadata. Tagged references distinguish tensor dependencies from scalar strings. Tagged tuple, list and dictionary values preserve nested return structure.

`fx_import.py` resolves references and emits a normal Kiln project script. Program outputs are flattened to named outputs, while a separate manifest records the source return structure. This allows the runtime integration to reconstruct a tuple containing a list without treating both sequences as interchangeable.

The initial importer supports a limited FP32 elementwise set plus inference batch normalization and disabled dropout. Unsupported dtypes, layouts and targets raise explicit errors. These restrictions describe unfinished implementation coverage; they do not justify excluding those tasks from a full benchmark denominator.

```text
FX nodes and tensor metadata
    → validated graph interchange
    → Kiln project source
    → tensor and loop transformations
    → scheduling and CUDA emission
    → kiln-program/1 artifact
    → PyTorch storage and CUDA stream
```

The importer is independently implemented against existing Kiln APIs. No PyTorch or PassNet implementation code has been copied. Future ports must record upstream revision, file, symbol, license, semantic adaptations and validation in their corresponding diary entries.

## 4. Execute without copying tensor contents

Kiln already exposes `open_program(..., backend="cuda", allocate=False)` and `CudaProgram.launch(stream=..., scratch=..., **pointers)`. The launcher compiles emitted CUDA with NVRTC for the detected device architecture. The new `runtime.py` bridge validates input metadata, allocates outputs and per-invocation scratch through PyTorch, and passes their pointers to the existing launcher.

A CUDA stream orders asynchronous GPU work. Merely passing a pointer does not establish that a producer has finished or that its storage will remain alive. The bridge uses the current PyTorch stream, records input/scratch use on that stream, and preserves input/output alias buffers. Tests cover default and non-default streams for the initial elementwise workload. Multi-kernel concurrency and close-with-outstanding-work behavior require further validation.

The available execution host is bling.local, an ARM64 DGX Spark with GB10 compute capability 12.1. The tested container supplies PyTorch 2.12.0a0, Triton 3.7.0 and CUDA 13.2. The paper used A30, PyTorch 2.9.1 and CUDA 12.8. Current results therefore establish a hardware-port implementation, not exact reproduction of the paper environment.

## 5. Follow a real graph through the boundary

The first pinned task contains ReLU, inference batch normalization and dropout disabled by its arguments. Its FP32 batch-eight graph has activation shape `[1000,128]` and channel vectors of length 128. The normalization computes:

```text
activated = relu(input)
normalized = (activated - running_mean) / sqrt(running_variance + epsilon)
output = normalized * weight + bias
```

Channel vectors must broadcast along axis one. Disabled dropout returns the computed tensor unchanged; this does not imply that training dropout can be removed. Training batch normalization also requires separate semantics for statistics and updates.

The first Kiln export failed its reference check. Kiln's generic input generator supplies unconstrained random tensors, whereas running variance has a nonnegative domain. Supplying valid running-statistics example data made the original compiler check pass without disabling it. The controlled change is consistent with an input-domain failure; per-element NaN diagnostics were not archived, so the report does not claim stronger causal proof.

A separate CUDA test used nontrivial random mean, positive variance, weight and bias. It passed PyTorch comparison at rtol `1.3e-6` and atol `1e-5`, with maximum absolute error `9.5367431640625e-07`. Nontrivial runtime statistics matter: an example containing only zeros and ones could conceal an incorrect affine implementation.

## 6. Why the original evaluator still rejects the pass

The first generated pass loaded but matched nothing. The saved graph-inspection script showed that symbolic tracing canonicalizes functional batch normalization into keyword arguments and inserts dropout's `inplace=False` default. Dynamo preserves the source graph's eight positional batch-normalization arguments and omits that dropout keyword. SubgraphMatcher therefore reports zero matches even though both graphs describe the same mathematics.

An explicit FX Graph can express the observed structure. However, the unchanged PassBench AST validator rejects calls to `torch.fx.Graph` and `torch.fx.GraphModule` before matching. The exact rejection is archived in `sources/kiln-match-v2.log`.

This is a protocol boundary. Hiding those constructors in imported code would not demonstrate legitimate compliance. The remaining choices are a pattern form accepted by the original protocol or a separately documented trusted integration mode. Any modified mode must retain numerical/dtype checking and integrity defenses, and its results must remain distinct from original-protocol reproduction.

## 7. Interpret current measurements carefully

The first original Inductor reference task completed all six variants successfully. A full 200-task exploratory run is underway. Its GPU activity overlapped integration checks, so its timing output cannot support controlled final speedup claims. The correct next measurement phase isolates workloads and captures environment identity, compiler identity, warmups, raw trials and stability criteria.

The executable settings also differ across sources: paper warmups are 20, sample entry scripts use 25, and the evaluator CLI defaults to 3. The scorer defaults to slowdown exponent parameter p=0, although README prose describes squaring slowdowns. Explicit run flags and stored scoring parameters are necessary to interpret any result.

## 8. What the milestone establishes

The project has verified corpus acquisition, a typed FX boundary, first Kiln lowering and CUDA execution for a genuine task's FP32 operation structure. It has also identified why current source tracing and integrity validation prevent original-protocol acceptance. Neither result establishes full PassBench support.

Next work must resolve matching, execute the original checker/scorer or clearly declared modified protocol, implement required dtype/layout/operator coverage, and evaluate reusable compiler policies on held-out graph families. Kiln's current fusion rule in `packages/kiln/src/std/loop.js` uses `now <= was * 1.02`; altering that profitability policy is a candidate experiment only after the benchmark integration and isolated baseline are trustworthy.

The intern guide progress edition is delivered through reMarkable at `/ai/2026/10/30/KILN-005`. Source artifacts, numbered scripts and chronological evidence live in the KILN-005 ticket under `/home/manuel/code/wesen/kiln/worktrees/passnet/ttmp/2026/10/30/`. Primary references are the [PassNet paper](https://arxiv.org/abs/2605.29357), [reference repository](https://github.com/PaddlePaddle/PassNet), and [dataset](https://huggingface.co/datasets/PassNet/PassNet).
