---
title: rag-ttc — Plain Go Experiments and the Mechanism–Policy Boundary
aliases:
  - plain go experiment composition
  - mechanism policy boundary
tags:
  - architecture-garden
  - rag-ttc
  - go
  - experiments
  - composition
status: active
type: architecture-pattern-study
created: 2026-07-26
analyzed: 2026-07-26
repository: /home/manuel/workspaces/2026-06-30/benchmark-cpu-inference/rag-ttc
repository_remote: git@github.com:wesen/rag-ttc.git
repository_commit: 3583bc92cd738fe5175b2369e546794f850c7fae
repository_branch: task/ttc-live-rag-quality-experiment
repository_worktree_dirty: true
related_files:
  - cmd/rag-ttc/cmds/experiments/bakeoff.go
  - cmd/rag-ttc/cmds/experiments/answerquality/runner.go
  - cmd/rag-ttc/cmds/experiments/summaryperf/matrix.go
  - cmd/rag-ttc/cmds/experiments/summaryperf/runner.go
  - examples/06_end_to_end_experiment/main.go
---

# Plain Go Experiments and the Mechanism–Policy Boundary

An experiment answers a question by making choices. It selects a workload, chooses variants, defines prompts and schemas, establishes budgets, orders operations, and decides which measurements count as results. Hiding those choices behind a generic stage engine makes the experiment shorter but makes its meaning harder to inspect.

`rag-ttc` therefore keeps experiment policy in direct Go control flow.

## Defining mechanism and policy

A mechanism explains how an operation is performed safely and consistently. Policy explains which operation the experiment performs and why.

| Mechanism | Policy |
|---|---|
| Run at most four calls concurrently | Compare concurrency values 1, 2, 4, and 8 |
| Charge a finite generation budget | Authorize 22 generation calls for this campaign |
| Cache each successful summary | Summarize each chunk, each batch, or each whole document |
| Strictly decode one JSON value | Require exactly the requested chunk identifiers |
| Append a completed result record | Choose result columns and arm names |

Mechanisms are reusable because their invariants remain the same across experiments. Policies remain local because changing them changes the experimental question.

## Direct orchestration

A readable experiment runner should resemble:

```go
func run(ctx context.Context, cfg Settings) error {
    workload := prepare(ctx, cfg)
    providers := resolveProviders(ctx, cfg)
    indexes := buildIndexes(ctx, workload, providers)

    for _, variant := range variants(cfg) {
        output := runVariant(ctx, variant, indexes, workload)
        report := evaluate(output, workload.Judgments)
        appendCompletedResult(report)
    }

    return completeRun()
}
```

The runner names the scientific stages. The functions implement cohesive operations. There is no generic `Stage`, `Node`, `ArmExecutor`, or registry required to understand the order.

## Why the boundary matters

The backend bakeoff, answer-quality experiment, and summary-performance experiment all use embedding, caching, budgets, observations, and artifacts. They do not use those mechanisms for the same purpose.

The summary-performance experiment varies concurrency, batching, whole-document packing, and multi-turn generation. The answer-quality experiment varies retrieval and reranking arms, then validates grounded-answer contracts and optionally constructs blinded review data. A shared workflow abstraction would either expose a large option surface or force the experiments into an artificial common sequence.

Shared functions provide the correct reuse unit:

```text
experiment A ─┐
experiment B ─┼─> small reusable operation
experiment C ─┘
```

They do not require:

```text
experiment configuration -> generic workflow interpreter -> callbacks -> artifacts
```

## Glazed commands at the boundary

The commands use Glazed for CLI schemas, settings, help, and structured output. Glazed owns the operational command surface, but it does not own the experiment algorithm. Parsed settings become typed configuration; the runner then executes normal Go.

This separation gives the project both:

- ecosystem-consistent CLI behavior;
- direct, testable experimental control flow.

## Signs that policy has leaked into a package

A proposed shared API should be rejected or narrowed when it begins to contain:

- experiment arm names;
- prompt templates;
- workload selection rules;
- report column definitions;
- a registry of steps;
- conditional stage dependencies;
- TTC-specific evaluation target assumptions;
- human-review policy.

These are not inherently bad concepts. They are bad shared-package concepts because another experiment cannot reuse them without inheriting the first experiment's question.

## Signs that mechanism remains trapped in a command

Command code should be extracted when it repeatedly implements:

- cache lookup and durable item storage;
- bounded worker scheduling;
- rate and budget admission;
- provider usage aggregation;
- provider observation;
- target identity resolution;
- atomic artifact writing.

The simplification ticket uses this test to decide what moves into packages.

## Applicability

Reuse this pattern when:

- experiments change frequently;
- the scientific procedure must remain reviewable;
- shared operations have narrow contracts;
- there is no external need to serialize and remotely schedule the workflow.

Do not use it as a rejection of all workflow systems. A durable multi-process scheduler is appropriate when orchestration itself is a product requirement. `rag-ttc` does not have that requirement.

## Candidate ecosystem rule

> Share mechanisms with stable invariants. Keep experimental and product policy in direct application code until at least two consumers demonstrate the same policy contract.

## Related documents

- [[01 - Project Architecture Overview]]
- [[03 - Recoverable Bounded Execution for Expensive Work]]
- [[07 - Architecture Debt and Patterns Not to Repeat]]
- [[08 - Candidate Ecosystem Guidelines]]
