---
title: "Evolving Programs with Language Models"
subtitle: "Category Theory, Dependent Types, Formal Proof, and Homotopy for Self-Optimizing Software"
author: "An independent technical textbook for programmers"
date: "August 2026"
lang: en-US
documentclass: book
classoption:
  - oneside
  - openany
papersize: letter
fontsize: 10pt
geometry:
  - margin=0.82in
  - headheight=14pt
mainfont: "Noto Serif"
sansfont: "Noto Sans"
monofont: "DejaVu Sans Mono"
colorlinks: true
linkcolor: blue
urlcolor: blue
citecolor: blue
toc: true
toc-depth: 2
numbersections: true
secnumdepth: 3
header-includes:
  - |
    \usepackage{microtype}
    \usepackage{booktabs}
    \usepackage{longtable}
    \usepackage{array}
    \usepackage{enumitem}
    \usepackage{xcolor}
    \usepackage{fancyhdr}
    \usepackage{listings}
    \usepackage{amsmath,amssymb,mathtools}
    \usepackage{stmaryrd}
    \usepackage{tcolorbox}
    \tcbuselibrary{breakable}
    \definecolor{BookBlue}{HTML}{17365D}
    \definecolor{BookGray}{HTML}{F3F5F7}
    \definecolor{CodeGray}{HTML}{F7F7F7}
    \lstset{basicstyle=\ttfamily\footnotesize,breaklines=true,breakatwhitespace=false,columns=fullflexible,frame=single,backgroundcolor=\color{CodeGray},showstringspaces=false,keepspaces=true,upquote=true}
    \pagestyle{fancy}
    \renewcommand{\chaptermark}[1]{\markboth{Chapter \thechapter}{}}
    \fancyhf{}
    \fancyhead[L]{\small Evolving Programs with Language Models}
    \fancyhead[R]{\small \nouppercase{\leftmark}}
    \fancyfoot[C]{\thepage}
    \setlength{\parskip}{0.35em}
    \setlength{\parindent}{1.2em}
    \setlist{nosep,leftmargin=*}
    \newtcolorbox{keyidea}{colback=BookGray,colframe=BookBlue,title=Key idea,breakable}
    \newtcolorbox{warningbox}{colback=white,colframe=black!65,title=Caution,breakable}
    \newtcolorbox{definitionbox}{colback=white,colframe=BookBlue,title=Definition,breakable}
    \newtcolorbox{engineeringbox}{colback=BookGray,colframe=black!65,title=Engineering rule,breakable}
---

\frontmatter

# Preface {-}

Software has entered a regime in which a model can inspect a program, read execution traces, receive textual criticism, rewrite the source, and submit the result to an evaluator. The evaluator may include tests, static checks, proof checkers, performance counters, human ratings, or another language model. An outer loop keeps useful candidates and asks for further revisions.

This looks evolutionary, but it is not simply the genetic programming of the 1990s with a larger mutation operator. The proposed edits are conditioned on language, source code, failure traces, and an enormous body of learned programming knowledge. The object being optimized may include prompts, code, tool policies, memory layouts, routing logic, and the boundary between deterministic computation and model calls. Selection can be multi-objective. The judge can itself be learned and fallible. The resulting system is best understood as a hybrid of evolutionary search, program synthesis, program repair, counterexample-guided refinement, online experimentation, and software architecture search.

The immediate motivation for this book is DSPy's experimental `Flex` module and its use with GEPA. In the setup described by Michael Isaac in August 2026, a `Flex` module exposes its source code as the optimizable parameter. GEPA can replace the whole implementation, including its decomposition, control flow, helper functions, and internal predictor calls. Candidate code executes in a sandbox, declared output types are checked at the boundary, and failed candidates receive failure scores rather than terminating the search. The public case study reports that optimization discovered a deterministic routing layer that avoided most model calls on easy examples, reserving a model for ambiguous cases. These are reported experimental results, not general guarantees, and the interface is explicitly marked experimental in the DSPy documentation.

The goal here is not to promote one library. It is to build a durable mathematical vocabulary for this class of systems. Three bodies of mathematics are especially useful:

1. **Category theory** explains composition, interfaces, effects, routing, resource accounting, feedback, recursion, and architecture-preserving rewrites.
2. **Dependent type theory and formal proof** separate admissibility from empirical quality, package code with machine-checkable evidence, and clarify exactly where an LLM judge is not a verifier.
3. **Homotopy type theory** supplies a language for equivalence, transport across refactorings, coherent families of rewrites, and the difference between preserving rich traces and collapsing them to scalar scores. It also exposes an important mismatch: ordinary identity paths are reversible, while optimization steps are directed. Directed type theory and enriched categories are therefore needed alongside HoTT.

The book is written for programmers who are comfortable with functions, types, tests, and ordinary software architecture. It assumes no prior category theory, proof assistant experience, or algebraic topology. Each chapter introduces the mathematics through code, derives a model of reflective program evolution, and ends with exercises. Exercises labeled **Code** ask for an implementation, **Proof** ask for a mathematical argument, **Design** ask for an architecture, and **Research** ask for an open-ended investigation.

## The thesis in one page {-}

Let $X$ be an input type and $Y$ an output type. A practical model harness is rarely a pure function $X \to Y$. It may call a language model, access tools, consume money and time, fail, log traces, and sample nondeterministically. We therefore model a harness as an effectful morphism

$$
    h : X \longrightarrow T_r(Y \times \mathrm{Trace}),
$$

where $T_r$ describes computational effects and $r$ is a resource grade such as model calls, tokens, latency, money, or capabilities.

A candidate is not merely source code. It is a package

$$
  \mathrm{Candidate}(C)
  \;=\;
  \sum_{h:\mathrm{Harness}(X,Y)}
  \mathrm{Admissible}_C(h),
$$

where $C$ is a contract and $\mathrm{Admissible}_C(h)$ contains evidence for interface conformance, sandbox policy, capability restrictions, resource bounds, and any proved functional properties. Soft quality measures are kept outside this proof package:

$$
  \mathrm{score}(h) \in \mathbb{R}^k.
$$

The optimizer maintains an archive $A$ of candidates, often an antichain under Pareto dominance. Evaluation produces not only scores but traces, counterexamples, proof failures, and textual feedback. A learned proposer defines a conditional mutation kernel

$$
  Q(h' \mid h,\; \tau,\; f,\; A),
$$

where $\tau$ is execution evidence and $f$ is feedback. One optimization step is a stochastic transition on optimizer state:

$$
  E : S \longrightarrow \mathcal{D}(O \times S),
$$

which is a coalgebra for the endofunctor $F(Z)=\mathcal{D}(O\times Z)$. Here $\mathcal{D}$ denotes a probability-distribution construction and $O$ records observations.

Program execution composes horizontally. Program versions evolve vertically. A rewrite is best represented by a square in a double category or by a 2-cell in a bicategory: it connects an old implementation to a new one and carries evidence that interfaces and hard invariants commute with the change. This is more informative than treating source strings as points in an unstructured search space.

At the HoTT level, implementations satisfying a contract form a type $\mathrm{Impl}(C)$. Equivalent implementations may be connected by paths, and higher paths express coherence between alternative refactoring sequences. Univalence permits properties to be transported across equivalences of representations. But an improvement relation $h \preceq h'$ is normally not invertible. HoTT therefore models semantic identity and equivalence, while directed type theory, preorder enrichment, or refinement categories model progress.

The practical conclusion is direct:

> Use models to propose semantic program transformations. Use types, capability systems, sandboxes, deterministic tests, solvers, and proof checkers to define the admissible region. Use calibrated statistical and human evaluation for the remaining soft objectives. Preserve traces and provenance. Select with explicit multi-objective policies. Never confuse a favorable judge score with a proof.

## Reading paths {-}

**The working engineer** can read Chapters 1-3, 5-8, 13-16, and 22-27.

**The category-theory reader** can read Chapters 4-12 and then 22.

**The formal-methods reader** can read Chapters 13-17 and the Lean appendix.

**The HoTT reader** can read Chapters 18-21 after Chapters 4 and 13.

**The researcher** should read the whole book, especially the explicit failure modes and open problems in Chapters 24 and 28.

## Notation {-}

| Notation | Meaning |
|---|---|
| $X,Y,Z$ | Types or schemas |
| $\mathcal{C}$ | A category |
| $f:X\to Y$ | A morphism or function |
| $T$ | An effect monad or related effect construction |
| $T_r$ | An effect indexed by resource grade $r$ |
| $\mathcal{D}(X)$ | Probability distributions or Markov kernels over $X$ |
| $\sum_{x:A}B(x)$ | Dependent sum: a value and evidence depending on it |
| $\prod_{x:A}B(x)$ | Dependent function: for each $x$, a value in $B(x)$ |
| $a =_A b$ | Identity type, interpreted homotopically as paths |
| $A \simeq B$ | Equivalence of types |
| $h \preceq h'$ | Directed refinement or no-worse relation |
| $\tau$ | Execution trace |
| $A$ | Candidate archive |
| $Q$ | Learned proposal or mutation kernel |
| $V$ | Verifier/evaluator |
| $J$ | Judge, often noisy or learned |

\mainmatter

# From Prompt Tuning to Program Evolution

## The object being optimized has changed

Early prompt optimization treats an LM call as a fixed component with a tunable string. A program might have several such calls, but its graph, control flow, and tool topology remain fixed. The optimizer selects demonstrations, edits instructions, or tunes decoding parameters. DSPy's original contribution was to make those components declarative: programmers specify signatures and compose modules, while a compiler-like optimizer searches for prompts and examples that improve a metric.

A code-optimizing module changes the search boundary. The optimizer can decide:

- how many model calls to make;
- which subproblems receive separate predictors;
- which cases can be handled by deterministic code;
- which information to compute before a model call;
- which tools to expose and when to call them;
- how to route easy and hard cases;
- what state or memory to retain;
- how to recover from errors;
- which prompt each internal component receives.

The optimized artifact is consequently an architecture, not merely a string.

This shift is visible in `dspy.Flex`. Its baseline behaves like a simple prediction module, or like an RLM when tools are available. Its optimizable parameter is a source string representing a complete module. During GEPA compilation, a code proposer receives the signature, current source, allowed primitives, tools, failing examples, outputs, and metric feedback. It returns a revised module class. Candidate parse failures and runtime failures are mapped to failure scores. The source executes in a sandbox, with predictor and tool calls bridged to the host.

The important abstraction is not "an LLM writes Python." It is:

$$
  \text{specification} + \text{evidence} + \text{proposal model}
  \longrightarrow
  \text{new implementation candidate}.
$$

The candidate is admitted or rejected by a collection of boundaries. Some boundaries are syntactic and typed. Some are logical. Some are statistical. Some are economic. Some are social.

## A minimal reflective evolution loop

The following pseudocode exposes the essential components.

```python
archive = {seed_candidate}
history = []

while budget.remaining():
    parent = select_parent(archive, history)
    evidence = evaluate(parent, training_cases)

    child_source = proposer.rewrite(
        source=parent.source,
        signature=contract.interface,
        traces=evidence.traces,
        counterexamples=evidence.counterexamples,
        feedback=evidence.feedback,
        archive=archive,
    )

    child = sandbox.build(child_source)
    if not hard_checks(child, contract):
        history.append(rejected(child, reason="inadmissible"))
        continue

    result = evaluate(child, validation_cases)
    archive = pareto_insert(archive, child, result.objectives)
    history.append(record(parent, child, evidence, result))
```

Five roles should remain conceptually distinct even when one model performs several of them:

1. **Executor**: runs the candidate on inputs.
2. **Observer**: records traces, resource use, and failures.
3. **Verifier**: checks hard, formally stated properties.
4. **Judge**: estimates soft or underspecified quality.
5. **Proposer**: generates a revision.

Collapsing these roles creates correlated failure. A model that proposes code and judges its own output may favor its own style, miss shared misconceptions, or exploit quirks in the rubric. A deterministic verifier can still be wrong because its specification is wrong, but it is auditable and repeatable in a way a stochastic judge is not.

## What "self" means

The phrase *self-evolving code* can mislead. In most contemporary systems:

- the foundation model's weights do not change;
- the outer loop is hand-written and fixed;
- the objective and sandbox are externally supplied;
- the code artifact changes, not the substrate executing the optimizer;
- human operators decide whether a candidate is deployed.

A more exact phrase is **reflective program evolution**: a program-producing system receives evidence about candidate behavior and uses a learned code model to propose revised programs. Some systems also modify the proposer prompt, memory, or search policy, producing a limited form of meta-optimization. This is still not unrestricted recursive self-improvement.

The distinction matters for safety and for theory. If the optimizer cannot modify its verifier, capability policy, or promotion gate, those components form a trusted computing base. If it can modify them, the state space and proof obligations become substantially larger.

## The four recurring transformations

The Flex location-conflation example illustrates four transformations that recur across reflective harness systems.

### Decomposition

A monolithic prediction is factored into parsing, feature computation, deterministic rules, and an ambiguity resolver. Mathematically, a morphism $h:X\to Y$ is replaced by a factorization

$$
  X \xrightarrow{f} Z \xrightarrow{g} Y.
$$

The intermediate type $Z$ makes latent structure explicit. Good decompositions expose independently testable invariants and reduce the entropy of later model calls.

### Method selection

A subproblem may be solved by plain code, a retrieval call, a symbolic solver, a small model, or a large model. The optimizer searches not only parameters but computational mechanisms. This resembles algorithm selection and mixture-of-experts routing, but the routes themselves are synthesized as source.

### Routing

Inputs are partitioned into cases. With a coproduct decomposition $X \cong X_e + X_h$, the harness has the form

$$
  [J(d),\; \ell] : X_e + X_h \longrightarrow T(Y),
$$

where $d$ is deterministic code embedded by $J$ and $\ell$ is an effectful model-backed branch. In ordinary Python this is an `if`; categorically it is a universal construction.

### Evolution

The architecture is revised in response to traces and feedback. A later candidate may introduce a new intermediate representation, merge two predictors, add a cache, or remove model calls. The mutation is semantic and context-conditioned rather than a random local edit.

## Why scalar optimization is insufficient

Suppose a candidate is evaluated on accuracy, cost, latency, security risk, and interpretability:

$$
  s(h) = (a(h),-c(h),-\ell(h),-r(h),i(h)).
$$

A weighted sum hides tradeoffs and encodes a policy in coefficients that may be unstable. A Pareto archive instead retains candidates for which no other candidate is at least as good in every objective and strictly better in one. The archive can include a high-accuracy expensive harness, a near-accurate cheap harness, and a slower proof-producing harness.

A production decision still needs policy. Pareto optimality does not tell an organization which candidate to deploy. It prevents the search algorithm from discarding meaningful alternatives prematurely.

## Exercises

1. **Concept.** List the mutable and immutable components in a code-optimizing harness you have used or can imagine. Which component is the trusted computing base?
2. **Code.** Implement the pseudocode loop with a proposer that performs rule-based source transformations rather than using an LLM. Record a complete history.
3. **Design.** Split a retrieval-augmented question-answering system into executor, observer, verifier, judge, and proposer. Identify every place where the same model is reused across roles.
4. **Proof.** Show that if $h=g\circ f$, and both $f$ and $g$ are total functions, then $h$ is total. Give a counterexample when effects include exceptions.
5. **Concept.** Explain why a source-code diff is not, by itself, evidence of semantic improvement.
6. **Design.** Define a five-dimensional score vector for a coding agent. State which dimensions are hard constraints and which are soft objectives.
7. **Research.** Compare the meanings of *self-improvement* in Promptbreeder, STOP, AlphaEvolve, Meta-Harness, and Flex. For each system, identify exactly what state is rewritten.
8. **Code.** Build a simple router that sends easy arithmetic expressions to a parser and hard natural-language questions to a model stub. Measure the model-call rate as the easy-case threshold changes.

# Anatomy of DSPy, GEPA, Flex, RLM, and Meta-Harness

## DSPy as declarative LM programming

DSPy treats language-model applications as programs assembled from typed-ish signatures and modules. A signature such as

```python
"question: str -> answer: str"
```

states the input-output interface without fixing a prompt template. A module such as `Predict`, `ChainOfThought`, `ReAct`, or `RLM` supplies an execution pattern. An optimizer compiles the program against examples and a metric by selecting instructions, demonstrations, or other parameters.

This is usefully compared to traditional compilation, but the analogy has limits. A conventional compiler preserves semantics while improving representation or performance. A DSPy optimizer searches for an implementation whose *empirical behavior* scores well on a dataset. It may change behavior on unseen inputs. The word *compiler* describes an engineering interface, not a proof of semantic preservation.

The original DSPy paper models an LM pipeline as a graph of text transformations with declarative modules and optimizable parameters. MIPRO and MIPROv2 extend prompt and demonstration search. GEPA replaces low-bandwidth scalar optimization with reflective textual feedback and Pareto-based evolutionary selection. Flex then moves source code into the parameter space.

## GEPA as reflective evolutionary search

GEPA stands for Genetic-Pareto. Its core loop can be described as follows:

1. Run a candidate system on a batch.
2. Collect system-level trajectories and metric feedback.
3. Ask a reflection model to diagnose failures and propose a mutation.
4. Evaluate the new candidate first on a small batch and, if promising, more broadly.
5. Retain candidates using a Pareto-based scheme that preserves per-instance strengths and diversity.

The GEPA paper emphasizes that natural-language reflection can carry richer information than a scalar reward. The proposition is plausible for program search: a message such as "the normalizer strips meaningful numeric branch identifiers" identifies a causal hypothesis and an edit target. A reward of $0.83$ does not.

Textual feedback is not a mathematical gradient. It does not necessarily satisfy linearity, a chain rule, local smoothness, or even consistency. It is better understood as a **semantic edit request** generated from evidence. Calling it a "text gradient" can be a productive metaphor, provided the missing calculus laws are not forgotten.

## Flex as architecture search

A Flex source string defines a module with initialization and forward behavior. The optimizer may change internal predictors, instructions, control flow, helper functions, or the ratio of Python computation to model computation. The public documentation makes several design choices explicit:

- the whole module source is one optimization parameter;
- predictors created inside the module are owned by that source and not tuned independently;
- code reflection sees whole-program inputs, outputs, and metric feedback;
- parse and runtime failures are converted to failure scores;
- generated code runs in an interpreter rather than the host process;
- declared output types are parsed and enforced at the sandbox boundary;
- the saved state contains module source, while the interpreter remains a runtime dependency;
- the API is experimental.

This yields an important software-design pattern: **optimize an implementation behind a stable interface**. The interface is fixed enough to support substitution; the implementation is intentionally fluid.

A minimal usage shape is:

```python
program = dspy.Flex(TaskSignature, tools=allowed_tools)

optimizer = dspy.GEPA(
    metric=metric_with_feedback,
    reflection_lm=strong_code_model,
    max_metric_calls=budget,
)

optimized = optimizer.compile(
    program,
    trainset=train_examples,
    valset=validation_examples,
)
```

Because the interface and serialization format are experimental, production systems should pin a DSPy version and store the generated source, evaluation dataset hashes, model identifiers, tool versions, and interpreter configuration together.

## RLM as programmable context access

A Recursive Language Model treats a long prompt as data in an external environment. Instead of placing the entire prompt in a single model context, the model writes or executes code that inspects portions, decomposes the problem, and recursively invokes a model on selected snippets.

Categorically, an RLM is not just recursion in the mathematical sense. It combines:

- an environment object containing data;
- an effect for reading selected regions;
- an effect for model invocation;
- recursive or iterative control;
- a trace of observations and subcalls.

Its type is closer to

$$
  X \times E \longrightarrow T_r(Y \times \mathrm{Trace})
$$

than to $X\to Y$. The environment $E$ is kept outside the token space and accessed through operations. This separation resembles the distinction between a store and a computation in programming-language semantics.

## Meta-Harness and persistent search memory

Meta-Harness searches over harness code using an agentic proposer that can inspect the source, scores, and raw traces of prior candidates through a filesystem. The reported ablation is theoretically revealing: in its online text-classification experiment, access to full traces substantially outperformed interfaces containing only scores or scores plus summaries.

The result should not be universalized from one study, but it supports a general information principle:

$$
  \mathrm{Trace} \xrightarrow{\text{summary}} S
  \xrightarrow{\text{score}} \mathbb{R}
$$

is a sequence of many-to-one maps. Each map discards distinctions. A proposer can only condition on information that survives. Summaries may remove the exact anomaly needed to infer a repair. Scores remove almost everything except rank or magnitude.

A persistent filesystem also changes the optimizer from a memoryless kernel to a history-dependent process. If $H_t$ is the complete history, then

$$
  Q(h_{t+1}\mid h_t)
$$

is replaced by

$$
  Q(h_{t+1}\mid h_t,H_t).
$$

The history can include negative results, which are valuable only if the proposer can retrieve and interpret them.

## The observed location-conflation transformation

The Flex case study begins with a single LM call that decides whether two place listings refer to the same physical location. The optimized code reportedly learns a pipeline with roughly this shape:

```text
raw records
    |
    v
normalize names and addresses
    |
    v
compute deterministic similarities and distance features
    |
    v
+--------------------+
| rule-based router  |
+--------------------+
   | easy        | ambiguous
   v             v
Boolean       focused LM judge
   |             |
   +------v------+
          |
       decision
```

The interesting move is not that the LLM wrote string-processing code. It is that optimization discovered a **partial evaluator**: deterministic computations settle cases for which the expensive stochastic component is unnecessary. The remaining model call receives a narrower, more structured problem.

In category-theoretic terms, the optimizer found a factorization through a feature object $Z$ and a coproduct-like decision boundary. In type-theoretic terms, it enriched the intermediate state with evidence. In information-theoretic terms, it transformed raw input into sufficient or approximately sufficient statistics for the remaining decision. In program-synthesis terms, it filled architectural holes using examples and counterexamples.

## Limits of the setup

Several limitations must be explicit.

First, held-out accuracy does not prove correctness. A synthesized normalizer may exploit dataset-specific artifacts. Second, a sandbox limits capabilities but does not make semantic behavior safe. Third, typed JSON boundaries guarantee shape, not truth. Fourth, the same metric used repeatedly during search becomes a training signal and can be overfit. Fifth, an LLM judge may contain positional, verbosity, self-preference, and style biases. Sixth, code that calls a model remains nondeterministic even when the wrapper is deterministic. Seventh, cost measurements can shift with model pricing, caching, batching, and infrastructure.

The right response is not to abandon optimization. It is to stratify evidence and make each layer explicit.

## Exercises

1. **Concept.** Draw the parameter boundary for `Predict`, MIPROv2, GEPA prompt optimization, and Flex code optimization.
2. **Code.** Create a DSPy signature and two hand-written modules with the same interface but different internal structures. Write a metric that exposes both score and textual feedback.
3. **Proof.** Explain why JSON schema validation establishes a proposition about representation but not a proposition about domain correctness.
4. **Design.** Specify the metadata needed to reproduce a Flex candidate one year later.
5. **Concept.** Give an example where a detailed trace enables a repair that no scalar score can identify.
6. **Code.** Implement a trace summarizer. Construct two distinct traces that map to the same summary but imply different fixes.
7. **Research.** Reproduce a small prompt-only versus code-plus-prompt optimization study. Use a meta-held-out test set that is never exposed during candidate selection.
8. **Design.** For an RLM-like system, identify the algebraic effects for context inspection, recursive calls, tools, exceptions, and logging.
9. **Concept.** Why is "compiler" an interface analogy rather than a semantic theorem in DSPy optimization?
10. **Proof.** If a summary map $q:T\to S$ is not injective, prove that no downstream function $g:S\to R$ can distinguish every pair of traces in $T$.

# Not Quite Genetic Programming

## Classical genetic programming

Classical genetic programming (GP), associated especially with John Koza's work, represents programs as genomes, often syntax trees. A population is evaluated by a fitness function. Selection favors fitter programs. Mutation and crossover generate descendants. Repetition searches for executable structures that solve a task.

A simplified GP loop is:

```text
initialize population of syntax trees
repeat:
    evaluate fitness
    select parents
    apply mutation and crossover
    form next population
return best individual
```

GP contributed foundational ideas that remain directly relevant: executable genomes, syntax-aware variation, population diversity, bloat control, fitness shaping, multi-objective selection, and the danger of overfitting to test cases.

Reflective LLM-based code evolution inherits this skeleton. It evaluates executable candidates, selects parents, applies variation, and retains useful descendants. The difference lies in the variation operator, the evidence channel, the searched representation, and the role of learned judges.

## Learned semantic mutation

In ordinary GP, mutation is intentionally generic: replace a subtree, perturb a constant, insert a node, or swap compatible fragments. It does not understand the task except through selection pressure.

An LLM proposer approximates a conditional distribution

$$
  Q(p'\mid p, D, \tau, f, L),
$$

where $p$ is source, $D$ is task data, $\tau$ is behavior, $f$ is criticism, and $L$ is learned prior knowledge. The prior includes programming idioms, algorithms, libraries, domain patterns, and natural-language concepts. A single proposal may perform a large coherent transformation: extract a parser, introduce a cache, replace brute force with dynamic programming, or add a verifier-backed branch.

Syntactically, that edit can be distant. Semantically, it can be local: it addresses one diagnosed failure while preserving the interface. Token edit distance is therefore a poor geometry for the search.

## High-bandwidth feedback

A scalar fitness provides ordering but little causal structure. A trace and critique can identify:

- the input region where failure occurs;
- the internal call that introduced the error;
- a violated invariant;
- an unnecessary model invocation;
- a tool result that was ignored;
- a pattern shared across failures;
- a plausible architectural remedy.

This moves the system closer to program repair and CEGIS. In CEGIS, a synthesizer proposes a candidate and a verifier returns a counterexample. The counterexample refines the next synthesis problem. In reflective evolution, the verifier may be incomplete, the feedback may be linguistic, and the proposer may be stochastic, but the information flow is similar.

The closest conceptual formula is:

$$
\begin{aligned}
  &\text{evolutionary archive} \\
  &\quad + \text{learned program synthesizer} \\
  &\quad + \text{counterexample-rich feedback} \\
  &\quad + \text{multi-objective evaluation}.
\end{aligned}
$$

## Genotype, phenotype, and trace

For a code candidate:

- the **genotype** is source, prompts, configuration, and perhaps persistent memory;
- the **phenotype** is observable behavior on an environment;
- the **developmental process** is interpretation, compilation, model sampling, and tool execution;
- the **fitness evidence** includes outputs, traces, costs, verifier results, and judge scores.

Unlike a fixed biological developmental process, the mapping from source to behavior can depend on mutable external models, APIs, tools, and data. The same genotype can produce a different phenotype after a model update. Reproducibility therefore requires versioned dependencies and recorded randomness.

The distinction also clarifies why saving only source is insufficient. The phenotype depends on the whole execution environment:

$$
  \mathrm{Behavior}
  =
  \mathrm{run}(\mathrm{source},\mathrm{model},\mathrm{tools},\mathrm{runtime},\mathrm{seed},\mathrm{input}).
$$

## Crossover, merge, and recombination

LLM systems can recombine candidates without syntax-tree crossover. GEPA includes system-aware merging of complementary lessons. A proposer can inspect two programs and write a third that combines one candidate's router with another's prompt. This is semantic recombination.

However, semantic merge is difficult to reason about. Two individually valid optimizations may interact negatively. A cache key introduced by one candidate may omit a feature required by another. A proof of each component does not automatically prove the composition unless contracts line up.

Category theory makes this failure precise: composability requires matching objects and preservation of stated laws. Dependent types can encode those laws at boundaries. A merge operator should be judged not merely by textual plausibility but by whether it constructs a term in the target candidate type.

## Quality diversity and niches

A single global best candidate encourages premature convergence. Pareto archives and quality-diversity methods preserve specialists. GEPA's per-instance Pareto selection keeps candidates that are strong on different examples. MAP-Elites preserves high-performing candidates in behaviorally defined cells.

For harness evolution, useful niche dimensions include:

- number of model calls;
- maximum context length;
- tool set;
- proof coverage;
- latency percentile;
- input-domain region;
- explanation format;
- memory footprint;
- failure-recovery strategy.

A niche archive can become an architecture library. A deployment controller may select a candidate based on current resource constraints rather than committing to one universal harness.

## LLM judges introduce a moving fitness landscape

In classic GP, fitness can be noisy, but it is often generated by an explicit simulator or test suite. In LM systems, a judge may be another model. Its output can vary with prompt order, verbosity, stylistic similarity, model version, and adversarially crafted content.

Let the latent human-relevant quality be $q(h,x)$ and the judge output be

$$
  J(h,x;\omega)=q(h,x)+b(h,x)+\epsilon_{\omega},
$$

where $b$ is systematic bias and $\epsilon$ is stochastic noise. Optimization against $J$ can increase $b$ rather than $q$. This is a Goodhart effect: the proxy becomes a target.

A learned proposer may also know the judge's habits. The search can discover judge-specific exploits even without explicit malicious intent. Robust evaluation therefore uses hidden tests, deterministic checks, multiple judges, order randomization, calibration against humans, adversarial probes, and periodic objective renewal.

## A taxonomy

| Dimension | Classical GP | Reflective LLM program evolution |
|---|---|---|
| Candidate | Usually AST/tree/program | Source, prompts, architecture, memory, tool policy |
| Mutation | Generic syntax variation | Learned semantic synthesis conditioned on evidence |
| Feedback | Mostly scalar fitness | Scores, traces, counterexamples, textual critique |
| Search prior | Grammar and operators | Pretrained code/language distribution plus constraints |
| Selection | Tournament, rank, elitism | Pareto, per-instance archive, best-of-N, agentic history use |
| Recombination | Tree or graph crossover | Model-mediated semantic merge |
| Evaluator | Tests/simulator/objective | Tests, proof tools, metrics, humans, LLM judges |
| Failure mode | Bloat, deception, overfit | Same, plus judge bias, prompt injection, tool abuse, model drift |
| Typical guarantee | Empirical fitness | Empirical fitness unless separate proof system is used |
| Closest neighboring field | Evolutionary computation | Program synthesis, repair, CEGIS, architecture search |

The best umbrella term is **reflective, language-mediated evolutionary program synthesis**. The phrase is long because the phenomenon is genuinely hybrid.

## Exercises

1. **Concept.** For a Flex candidate, identify genotype, phenotype, environment, and fitness evidence.
2. **Proof.** Construct an example where two candidates have equal scalar fitness but different Pareto vectors.
3. **Code.** Implement subtree mutation for a tiny expression language. Compare it with a hand-written semantic mutation that uses a failing example.
4. **Design.** Define behavior dimensions for a MAP-Elites archive of retrieval harnesses.
5. **Concept.** Explain why model-mediated merge is not equivalent to syntax-tree crossover.
6. **Research.** Measure whether an LLM proposer produces syntactically larger but semantically more targeted changes than random AST mutation on a repair benchmark.
7. **Design.** Create an evaluation protocol that estimates positional bias in an LLM judge.
8. **Proof.** Let $J=q+b$. Show that maximizing $J$ need not maximize $q$, even when $J$ and $q$ are positively correlated on the initial population.
9. **Concept.** In what sense is reflective evolution Lamarckian, and in what sense is that analogy misleading?
10. **Code.** Build a replay tool that reconstructs candidate behavior from source, model identifier, tool versions, seed, and input. Deliberately omit one dependency and document the divergence.

# Mathematical Warm-Up: Types, Relations, Orders, and Evidence

## Types are not merely sets

A programmer first meets a type as a collection of values accepted by an operation. Mathematics often begins with the same approximation: a type $X$ behaves like a set of possible values. A function $f:X\to Y$ assigns one output to every input.

This approximation is useful but incomplete for software. Types can also encode:

- how a value was constructed;
- what resources a computation may use;
- what proposition is known about a value;
- whether two values are definitionally or propositionally equal;
- how values vary with an index;
- whether a computation is total, partial, deterministic, or stochastic.

The progression in this book is:

```text
sets and functions
    -> categories and morphisms
    -> effectful computations
    -> dependent types and proofs
    -> identity types and homotopy
```

Each layer retains the earlier intuition but makes more structure explicit.

## Relations and preorders

A binary relation $R\subseteq X\times X$ states when two values are related. We write $xRy$.

A **preorder** is a relation $\preceq$ that is:

- reflexive: $x\preceq x$;
- transitive: $x\preceq y$ and $y\preceq z$ imply $x\preceq z$.

It need not be antisymmetric. Two distinct source programs can be mutually no worse under all measured objectives. Quotienting by mutual comparison yields a partial order when the usual conditions hold.

For candidate score vectors, define Pareto dominance for objectives to be maximized:

$$
  u \succ v
  \quad\Longleftrightarrow\quad
  \bigl(\forall i,\; u_i\ge v_i\bigr)
  \land
  \bigl(\exists j,\;u_j>v_j\bigr).
$$

The nondominated set is an antichain: no two distinct members dominate one another.

## Hard propositions and soft quantities

A central discipline of this book is to separate propositions from scores.

Examples of propositions:

- the source parses;
- every output conforms to a schema;
- no filesystem capability is available;
- every tool call is in an allowlist;
- the implementation preserves a specified invariant;
- worst-case model calls are at most three.

Examples of soft quantities:

- answer quality as estimated by humans;
- average latency;
- expected cost;
- style preference;
- benchmark accuracy;
- interpretability rating.

A proposition has evidence that can, in principle, be checked. A score supports comparison but does not inhabit a logical claim such as "correct for all inputs." Some statistical claims can be propositions once assumptions and confidence levels are made explicit, but they remain different from pointwise functional correctness.

## Evidence as a first-class value

Suppose a normalizer returns a string and evidence that the result is uppercase:

$$
  \mathrm{normalize} : (s:\mathrm{String})
  \to
  \sum_{t:\mathrm{String}} \mathrm{IsUpper}(t).
$$

The output is a pair $(t,p)$, where $p$ is a proof or certificate. Downstream code can rely on the property without rerunning the normalizer's reasoning.

In ordinary Python, a runtime approximation is:

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class UpperString:
    value: str

    def __post_init__(self) -> None:
        if self.value != self.value.upper():
            raise ValueError("not uppercase")
```

This constructor enforces an invariant dynamically. A dependent type system can express the invariant statically and retain the proof object.

## Quotients and observational equivalence

Two programs can differ syntactically while being indistinguishable under a chosen observation. Let $O$ be a set of observations and let

$$
  \llbracket - \rrbracket : P \to O
$$

map programs to behavior. Define

$$
  p \sim q \quad\Longleftrightarrow\quad
  \llbracket p\rrbracket=\llbracket q\rrbracket.
$$

The quotient $P/{\sim}$ treats observationally equivalent programs as one semantic point.

In practice, observations are finite tests, so equivalence is approximate:

$$
  p \sim_D q
  \quad\Longleftrightarrow\quad
  \forall x\in D,\; p(x)=q(x).
$$

This relation may merge programs that differ outside $D$. Reflective optimization operates on such partial observational quotients unless a stronger verifier is present.

## Resource monoids

Resources compose. If one stage costs $r$ and the next costs $s$, the pipeline costs approximately $r+s$. This suggests a commutative monoid $(R,+,0)$.

For multiple resources, take

$$
  R=\mathbb{R}_{\ge0}^{k}
$$

with componentwise addition. A grade might be

$$
  r=(\text{calls},\text{tokens},\text{dollars},\text{milliseconds}).
$$

Grades can represent upper bounds, exact symbolic costs, or expected values. Mixing those interpretations without labels is an error. A worst-case call bound composes differently from an empirical p95 latency estimate.

## Exercises

1. **Proof.** Verify that componentwise $\le$ on $\mathbb{R}^k$ is a partial order.
2. **Code.** Implement Pareto insertion and test that the archive remains an antichain.
3. **Concept.** Classify ten properties of your current software system as propositions, measurements, or judgments.
4. **Proof.** Show that agreement on a finite dataset is an equivalence relation on deterministic programs.
5. **Concept.** Explain why finite-test equivalence is usually not a congruence under arbitrary program contexts.
6. **Code.** Implement a runtime evidence wrapper for a sorted list. Prevent construction through the public API unless the invariant holds.
7. **Design.** Define a resource monoid for an agent that uses an LM, a database, and a human escalation channel.
8. **Proof.** If resource grades are upper bounds and sequential composition adds them, show that replacing a stage by a lower-grade stage cannot increase the pipeline bound.
9. **Research.** Investigate whether the objectives in a real harness are commensurable enough for a weighted sum. Compare three weighting schemes with a Pareto archive.
10. **Concept.** Give one property that can be checked syntactically, one semantically, one statistically, and one only through human judgment.

# Categories as a Language of Software Composition

## Objects, morphisms, and laws

A category $\mathcal{C}$ consists of:

1. objects $X,Y,Z,\ldots$;
2. morphisms $f:X\to Y$;
3. an identity morphism $\mathrm{id}_X:X\to X$ for every object;
4. composition: from $f:X\to Y$ and $g:Y\to Z$, a morphism $g\circ f:X\to Z$.

The laws are:

$$
  h\circ(g\circ f)=(h\circ g)\circ f
$$

and

$$
  f\circ\mathrm{id}_X=f,
  \qquad
  \mathrm{id}_Y\circ f=f.
$$

A category says less than a programming language and more than an unstructured graph. It forgets implementation details while preserving the fact that components have interfaces and compose lawfully.

The canonical example is **Set**, whose objects are sets and whose morphisms are total functions. For typed functional programming, one often imagines a category whose objects are types and whose morphisms are total, terminating functions. Real languages complicate this picture with nontermination, exceptions, state, and other effects; later chapters handle them explicitly.

## Harnesses as morphisms

A task signature defines an input object $X$ and output object $Y$. A pure harness implementation is a morphism

$$
  h:X\to Y.
$$

A pipeline

```text
Question -> RetrievedEvidence -> Draft -> CheckedAnswer
```

is a composition

$$
  X \xrightarrow{r} E
  \xrightarrow{d} A
  \xrightarrow{c} Y.
$$

Associativity means that the result does not depend on whether we first regard retrieval and drafting as one component or drafting and checking as one component. This is not an execution-order claim: the arrows still run left to right. It is a statement that parenthesization is irrelevant to the denoted composite.

Associativity supports modular optimization. A candidate rewriter can replace $d$ with $d'$ while leaving $r$ and $c$ fixed, provided the interfaces remain $E\to A$.

## Commutative diagrams as refactoring obligations

A diagram commutes when all directed paths with the same endpoints denote the same morphism. Suppose a data representation changes from $Z$ to $Z'$, with conversion $e:Z\to Z'$. An old stage $g:Z\to Y$ is replaced by $g':Z'\to Y$. The square

$$
\begin{array}{ccc}
Z & \xrightarrow{g} & Y \\
\downarrow e & & \downarrow \mathrm{id}_Y \\
Z' & \xrightarrow{g'} & Y
\end{array}
$$

commutes when

$$
  g = g'\circ e.
$$

That equation is the semantic obligation for the representation-changing refactor. A test suite samples the equation. A proof establishes it for the modeled domain. An LLM judge merely estimates whether outputs look equivalent.

For self-rewriting software, commutative diagrams are useful design documents. Every generated refactor should state what square it intends to preserve.

## Functors as structure-preserving translations

A functor $F:\mathcal{C}\to\mathcal{D}$ maps objects and morphisms while preserving identities and composition:

$$
 F(\mathrm{id}_X)=\mathrm{id}_{F(X)},
 \qquad
 F(g\circ f)=F(g)\circ F(f).
$$

Examples in software include:

- interpreting a typed syntax category into a semantic category;
- compiling a typed intermediate representation to machine code;
- mapping a deterministic function to a probabilistic computation that returns a point mass;
- turning a schema into a serializer and a function into a transported service operation.

It is tempting to call an LM optimizer a functor from specifications to implementations. Usually it is not. Optimization is stochastic, dataset-dependent, and not guaranteed to preserve composition. Optimizing $g\circ f$ jointly need not equal composing separately optimized $f$ and $g$:

$$
  \mathrm{Opt}(g\circ f)
  \ne
  \mathrm{Opt}(g)\circ\mathrm{Opt}(f).
$$

The failure is informative. Joint optimization can fuse stages, introduce shared state, or move work across a boundary. If compositional optimization is desired, it must be imposed through modular contracts and laws.

## Natural transformations as uniform implementation changes

Given functors $F,G:\mathcal{C}\to\mathcal{D}$, a natural transformation $\eta:F\Rightarrow G$ gives, for every object $X$, a morphism

$$
  \eta_X:F(X)\to G(X)
$$

such that for every $f:X\to Y$,

$$
  G(f)\circ \eta_X = \eta_Y\circ F(f).
$$

In software, naturality expresses a uniform change that commutes with all program operations. Examples include wrapping every value in a logging context or converting every schema through a consistent version adapter.

A generated family of migrations is safer when it is natural: transforming before applying an operation agrees with applying the transformed operation after migration. This is a stronger claim than "all individual examples passed."

## Universal properties and interface design

Category theory often defines structures not by their internal representation but by what maps into or out of them. This is a **universal property**. It supports representation independence.

For self-optimizing code, universal properties suggest a strategy: expose only the behavior required to compose. Let the optimizer choose the representation. A router should satisfy the eliminator for a sum type. A paired output should satisfy the projections of a product. A fold should satisfy an algebra law. The generated implementation is replaceable because clients depend on the universal interface rather than the source layout.

## Categories of specifications and implementations

It is useful to distinguish at least three categories:

- $\mathcal{S}$: specifications and refinement-preserving maps;
- $\mathcal{P}$: program syntax or typed intermediate representations;
- $\mathcal{B}$: semantic behaviors, such as functions or stochastic kernels.

An interpretation functor

$$
  \llbracket - \rrbracket:\mathcal{P}\to\mathcal{B}
$$

maps code to meaning. A candidate generator attempts to find $p\in\mathcal{P}$ whose behavior satisfies a specification $s\in\mathcal{S}$.

The key distinction is that search happens in syntax while objectives are usually stated over behavior. Many pathologies arise because the map $\llbracket-\rrbracket$ is many-to-one, discontinuous under token edits, and dependent on a runtime environment.

## Exercises

1. **Concept.** Give three categories used implicitly in a web service: schemas, pure transformations, and networked computations. State what the morphisms are.
2. **Proof.** Verify the category laws for a small category with three objects and explicitly listed arrows.
3. **Code.** Implement a generic function-composition operator and property-test associativity for pure Python functions over a finite domain.
4. **Design.** Draw a commutative square for a generated database-schema migration.
5. **Proof.** Show that the inclusion of deterministic functions into probability distributions by point masses preserves identities and composition.
6. **Concept.** Give an example where separately optimizing two stages is worse than joint optimization, and one where joint optimization breaks a modularity requirement.
7. **Design.** Define a category of API contracts. What counts as a contract-preserving morphism?
8. **Proof.** Write the naturality equation for a logging wrapper and explain the assumptions required for it to hold.
9. **Research.** Choose a compiler optimization and identify which semantic diagram it is intended to preserve. Compare its proof obligations with those of an LLM-generated rewrite.
10. **Concept.** Explain why a function from source strings to source strings is not automatically a functor.

# Products, Coproducts, Monoidal Structure, and Architecture

## Products package simultaneous information

A product $X\times Y$ comes with projections

$$
  \pi_1:X\times Y\to X,
  \qquad
  \pi_2:X\times Y\to Y.
$$

For any $f:Z\to X$ and $g:Z\to Y$, there is a unique pairing

$$
  \langle f,g\rangle:Z\to X\times Y
$$

such that $\pi_1\circ\langle f,g\rangle=f$ and $\pi_2\circ\langle f,g\rangle=g$.

In a harness, products represent records, tuples, and jointly available evidence. A feature extractor can be written

$$
  \langle \mathrm{nameFeatures},\mathrm{addressFeatures},\mathrm{distance}\rangle
  : X\to N\times A\times D.
$$

The product's universal property says any consumer of all three features can receive one canonical combined map.

## Coproducts express alternatives

A coproduct $X+Y$ comes with injections

$$
  \iota_1:X\to X+Y,
  \qquad
  \iota_2:Y\to X+Y.
$$

Given $f:X\to Z$ and $g:Y\to Z$, there is a unique case-analysis map

$$
  [f,g]:X+Y\to Z
$$

satisfying $[f,g]\circ\iota_1=f$ and $[f,g]\circ\iota_2=g$.

Routing is coproduct elimination. A well-designed router should make the branch evidence explicit:

```python
@dataclass(frozen=True)
class Settled:
    decision: bool
    reason: str

@dataclass(frozen=True)
class Ambiguous:
    features: FeatureBundle

RouteResult = Settled | Ambiguous
```

The downstream harness then consumes a sum type rather than relying on a nullable Boolean or undocumented threshold.

## Distributivity and branch-local computation

In distributive categories,

$$
  X\times(Y+Z) \cong (X\times Y)+(X\times Z).
$$

For programs, common context $X$ can be distributed into branches or factored back out. A code optimizer often performs this transformation when it moves shared parsing before a route or duplicates a small piece of context-specific logic inside each branch.

The equivalence is structural, but operational cost can differ. Duplicating computation may increase latency; factoring may retain unnecessary state. Category theory identifies semantic equivalence, while a cost-enriched model distinguishes implementations.

## Monoidal categories model parallel composition

A monoidal category has a tensor product $\otimes$ for placing systems side by side, a unit object $I$, and coherence laws. In many programming examples, $\otimes$ is a product, but it need not be.

If

$$
  f:X\to Y,
  \qquad
  g:U\to V,
$$

then

$$
  f\otimes g:X\otimes U\to Y\otimes V
$$

runs or composes the components in parallel at the abstract level.

String diagrams depict morphisms as boxes and values as wires:

```text
X ----[ f ]---- Y

U ----[ g ]---- V
```

Tensoring places diagrams vertically:

```text
X ----[ f ]---- Y
U ----[ g ]---- V
```

Sequential composition joins wires:

```text
X ----[ f ]---- Y ----[ g ]---- Z
```

String diagrams are valuable for model harnesses because they suppress source-level noise and foreground dataflow, branching, feedback, and effects.

## Symmetry, copying, and deletion

A symmetric monoidal category provides a swap

$$
  \sigma_{X,Y}:X\otimes Y\to Y\otimes X.
$$

Ordinary data can often be copied and discarded. In a cartesian monoidal category, diagonal and terminal maps provide

$$
  \Delta_X:X\to X\times X,
  \qquad
  !_X:X\to 1.
$$

Effects complicate copying. Reusing a deterministic value is harmless; duplicating an LM call can change cost and output. A string diagram must distinguish copying a value from rerunning the computation that produced it.

This is a common generated-code bug. The optimizer sees two consumers and duplicates a call expression instead of binding its result once. An effect-aware intermediate representation prevents the mistake.

## Operads and architecture grammars

An operad describes operations with multiple inputs and one output, together with substitution. It is a natural language for architecture templates:

- a `router` takes a classifier and several branch harnesses;
- a `map_reduce` takes a mapper, reducer, and chunker;
- a `verify_then_repair` node takes a generator, verifier, and repairer;
- a `committee` takes several judges and an aggregation rule.

An optimizer can search terms in a free operad generated by approved primitives. Substitution replaces one component while preserving arity and type. This is safer than unrestricted source rewriting because the grammar excludes invalid architectures by construction.

A typed operadic grammar might expose:

```text
Predict[X,Y]                 : Harness[X,Y]
Compose[Harness[X,Y],
        Harness[Y,Z]]        : Harness[X,Z]
Route[Classifier[X,K],
      Branches[K,X,Y]]       : Harness[X,Y]
Verify[Harness[X,Y],
       Predicate[X,Y]]       : Harness[X,Y]
Fallback[Harness[X,Y],
         Harness[X,Y]]       : Harness[X,Y]
```

The LLM then proposes typed terms rather than arbitrary Python. A compiler lowers the term to sandboxed code.

## Factorization as learned decomposition

A recurring optimization is to factor a morphism through an intermediate object:

$$
  h:X\to Y
  \quad\leadsto\quad
  X\xrightarrow{f}Z\xrightarrow{g}Y.
$$

The choice of $Z$ is architectural. A useful intermediate representation makes relevant distinctions while hiding irrelevant ones. In the location example, $Z$ contains normalized names, parsed addresses, distances, and similarity scores.

Factorization can reduce search complexity because $f$ and $g$ admit separate contracts. It can also increase error surfaces and interface overhead. The optimizer should be penalized for gratuitous intermediate structures unless they improve quality, cost, proofability, or reuse.

## Exercises

1. **Proof.** Use the universal property to show that pairing into a product is unique.
2. **Code.** Refactor a dictionary-returning feature extractor into typed product-like records. Make invalid partial records unrepresentable.
3. **Design.** Express a confidence router using a coproduct rather than a Boolean plus optional payload.
4. **Proof.** Write both directions of the distributivity isomorphism $X\times(Y+Z)\cong(X\times Y)+(X\times Z)$.
5. **Concept.** Give an example where copying a value is safe but copying its producing computation is not.
6. **Code.** Build a tiny typed architecture DSL with `Predict`, `Compose`, `Route`, and `Fallback` constructors.
7. **Design.** Specify an operad of approved components for a medical-information assistant. Which substitutions should be impossible?
8. **Proof.** State the type-matching conditions under which replacing a subdiagram preserves well-formedness.
9. **Research.** Compare unrestricted source proposals with grammar-constrained proposals on candidate validity and final quality.
10. **Concept.** Identify the intermediate object $Z$ in three familiar optimizations: caching, retrieval augmentation, and compiler common-subexpression elimination.

# Effects, Monads, Markov Categories, and Resource Grades

## Why $X\to Y$ is too small

A model harness can fail, sample, log, call tools, update memory, and spend resources. Treating it as a pure function hides the behavior that optimization most needs to control.

Programming-language semantics often represent an effectful computation as

$$
  X\to T(Y),
$$

where $T$ is a type constructor describing an effect. Examples include:

- partiality: $T(Y)=Y+\mathrm{Error}$;
- state: $T(Y)=S\to(Y\times S)$;
- nondeterminism: $T(Y)=\mathcal{P}(Y)$;
- probability: $T(Y)=\mathcal{D}(Y)$;
- logging: $T(Y)=Y\times W$;
- asynchronous execution: a future or task type.

A monad provides operations that compose effectful computations without manually unpacking and repacking the effect at every step.

## Monad interface

A monad consists of a type constructor $T$, a unit

$$
  \eta_X:X\to T(X),
$$

and a composition operation, often expressed as bind:

$$
  (\mathbin{\gg=}) : T(X)\times(X\to T(Y))\to T(Y).
$$

The monad laws state that unit acts as an identity and bind is associative.

In Haskell notation:

```haskell
return a >>= f       = f a
m >>= return         = m
(m >>= f) >>= g      = m >>= (\x -> f x >>= g)
```

These laws are not decorative. They justify refactoring effectful pipelines without changing meaning.

## The Kleisli category

Given a monad $T$ on $\mathcal{C}$, the Kleisli category $\mathrm{Kl}(T)$ has the same objects as $\mathcal{C}$ and morphisms

$$
  X\to Y \text{ in } \mathrm{Kl}(T)
  \quad:=\quad
  X\to T(Y) \text{ in } \mathcal{C}.
$$

Kleisli composition uses bind. This is the natural category for effectful harnesses.

A deterministic function $f:X\to Y$ embeds as

$$
  J(f)=\eta_Y\circ f:X\to T(Y).
$$

This formalizes a central optimization pattern: route some inputs through the deterministic subcategory and others through effectful model calls.

## Combining effects

A practical harness might have a type resembling

$$
  X\to
  \mathrm{State}_S(
    \mathrm{Except}_E(
      \mathcal{D}(Y\times\mathrm{Trace}))).
$$

Effect order matters. Does a failed computation retain its log? Is state rolled back after an exception? Are random samples replayable? Monad transformers, algebraic effects, or effect handlers make these choices explicit.

Generated code should not be allowed to improvise effect semantics. The runtime should supply operations such as:

```text
call_model      : Prompt -> Eff[ModelCall] Completion
call_tool       : ToolId -> Args -> Eff[ToolCall] Result
emit_trace      : Event -> Eff[Log] Unit
read_memory     : Key -> Eff[ReadMemory] Value
write_memory    : Key -> Value -> Eff[WriteMemory] Unit
abort           : Error -> Eff[Abort] Never
```

An effect handler interprets these operations. The optimizer searches over programs using them, while the host controls their meaning and permissions.

## Algebraic effects and capability control

Algebraic effects separate *what a program requests* from *how the request is handled*. A generated candidate may issue `call_tool("geocoder", args)`, but only the host handler can access the actual service.

This has three benefits:

1. capability restriction is centralized;
2. traces are complete because operations pass through handlers;
3. test interpreters can replace real services with deterministic mocks.

A sandbox without an effect discipline blocks many actions but may still expose a broad language runtime. A typed effect DSL makes allowed operations visible in the candidate's type.

## Probability and Markov categories

A stochastic model call can be interpreted as a Markov kernel

$$
  k:X\rightsquigarrow Y,
$$

assigning a distribution over outputs to each input. Markov categories provide categorical structure for probabilistic processes, including copying and discarding classical data.

Composition integrates over intermediate outcomes:

$$
  (\ell\circ k)(z\mid x)
  =\int_Y \ell(z\mid y)\,k(dy\mid x).
$$

This matters because the score of a stochastic harness is an expectation, not a fixed property of one run:

$$
  \mathbb{E}_{x\sim P,\,y\sim h(x)}[\mu(x,y)].
$$

Evaluation variance comes from both input sampling and model sampling. An optimizer that compares candidates using one rollout per input can select noise. Repeated trials, paired seeds, confidence intervals, and sequential testing become part of the semantics of selection.

## Graded monads for resources

A graded monad uses a family $T_r$ indexed by resource grades $r\in R$. Unit has grade $0$:

$$
  \eta:X\to T_0(X),
$$

and composition adds grades:

$$
  T_r(X)\times(X\to T_s(Y))\to T_{r+s}(Y).
$$

A harness type can then state an upper bound:

$$
  h:X\to T_{(2\ \mathrm{calls},\;8000\ \mathrm{tokens})}(Y).
$$

The index can be static when bounds are known, symbolic when they depend on input size, or dynamic evidence returned with the trace. Static worst-case bounds and expected empirical costs should use different constructors to avoid unsound substitution.

## Enrichment by cost

A category can be enriched over an ordered monoid of costs. Instead of merely knowing that a morphism exists, one tracks a value such as latency or error. Lawvere's view of metric spaces as enriched categories is relevant: distance behaves like the cost of moving between points, with composition governed by a triangle inequality.

For program evolution, define a semantic edit cost

$$
  d(p,q)
$$

that might combine source complexity, proof repair effort, behavioral divergence, and deployment risk. Token edit distance is one possible component, but often a poor one. An LLM proposal can be syntactically large yet semantically conservative.

## A typed effectful harness

The book's basic categorical type is now:

$$
  \mathrm{Harness}_r(X,Y)
  := X\to T_r(Y\times\mathrm{Trace}).
$$

The trace is not an afterthought. It is an observable needed by the outer optimizer. It may include model inputs and outputs, tool calls, branch choices, timing, resource consumption, verifier messages, and provenance.

A production system should redact or cryptographically protect sensitive trace fields. "Preserve full traces" is an optimization principle, not permission to violate privacy.

## Exercises

1. **Proof.** Derive Kleisli composition for the exception monad $T(Y)=Y+E$.
2. **Code.** Implement a small `Result` monad in Python and verify the monad laws over a finite test set.
3. **Design.** List the algebraic effects in a coding agent. Define a restricted handler for untrusted generated code.
4. **Concept.** Explain how effect order changes whether logs survive exceptions.
5. **Proof.** Show that grades add under three-stage composition by associativity of the resource monoid.
6. **Code.** Build a model-call effect whose test handler returns deterministic fixtures and whose production handler invokes a stubbed external service.
7. **Design.** Give separate types for worst-case call bounds and empirical expected call counts.
8. **Proof.** For finite spaces, write the matrix formula for composing two Markov kernels.
9. **Research.** Compare candidate rankings under one stochastic rollout, five rollouts, and paired common-random-number evaluation.
10. **Concept.** Why is a sandbox an operational mechanism while an effect type is a specification mechanism?
11. **Design.** Decide which trace fields must be retained for optimization and which must be redacted for privacy. State the resulting information loss.

# Recursion, Traces, Fixed Points, and Coalgebra

## Feedback in string diagrams

Some harnesses loop. A ReAct agent repeatedly observes, reasons, calls a tool, and updates state. An RLM recursively invokes a model over subcontexts. A repair harness generates code, runs tests, and revises until a budget expires.

A traced monoidal category provides an operation

$$
  \mathrm{Tr}^{U}_{X,Y}:
  \mathcal{C}(X\otimes U,Y\otimes U)
  \to
  \mathcal{C}(X,Y),
$$

which feeds the $U$ output of a component back into its $U$ input.

Diagrammatically:

```text
         +----------------------+
X ------>|          f           |------> Y
         |                  U --+--+
         +----------------------+  |
                    ^              |
                    +--------------+
```

The trace axioms formalize valid rewiring rules. They do not guarantee termination. A loop needs an additional guard, well-founded measure, or bounded iteration policy.

## Fixed points

A recursive definition seeks a fixed point of an operator $F$:

$$
  x=F(x).
$$

In denotational semantics, complete partial orders and continuity can provide least fixed points. In total dependent type theory, recursion is usually accepted only when structural termination or a decreasing measure is evident.

For generated harnesses, unrestricted self-recursion is dangerous. A safe architecture exposes bounded combinators:

```python
for step in range(max_steps):
    state = transition(state)
    if done(state):
        return finish(state)
raise BudgetExceeded(max_steps)
```

The bound is part of the contract and resource grade.

## Algebra describes construction; coalgebra describes behavior

An algebra for an endofunctor $F$ is a map

$$
  a:F(A)\to A.
$$

It folds or constructs values. A coalgebra is a map

$$
  c:S\to F(S),
$$

which unfolds observable behavior from a state.

State machines, streams, transition systems, and interactive agents are naturally coalgebraic. A deterministic optimizer iteration can be modeled as

$$
  c:S\to O\times S,
$$

where $O$ is an observation. A stochastic optimizer is

$$
  c:S\to \mathcal{D}(O\times S).
$$

The state $S$ may contain:

$$
  S = \mathrm{Archive}\times\mathrm{History}
      \times\mathrm{Budget}\times\mathrm{RNG}
      \times\mathrm{Config}.
$$

This coalgebraic view shifts attention from "the final best program" to the evolving observable process.

## Bisimulation and optimizer equivalence

Two stateful systems are bisimilar when they can match each other's observations and transitions step by step under an appropriate relation. Bisimulation is often a better equivalence for interactive harnesses than equality of final outputs.

Two agent implementations may produce the same final answer but differ in tool access, disclosure, cost, or intermediate side effects. An observation type $O$ that records only final answers is too coarse. Expanding $O$ changes the equivalence relation.

For auditability, define observations before claiming behavioral equivalence.

## Evolution as a coalgebra

Let $A_t$ be the archive and $H_t$ the history. One optimization step performs:

1. select a parent;
2. gather or retrieve evidence;
3. sample a proposal;
4. build and hard-check the candidate;
5. evaluate it;
6. update the archive and history.

This is a transition

$$
  E:S\to\mathcal{D}(O\times S).
$$

The proposal model, evaluator randomness, and dataset sampling are all included in $\mathcal{D}$. If the process is deterministic conditional on a recorded seed, the seed belongs in $S$.

A run is an unfolding:

$$
  s_0 \mapsto (o_0,s_1)
      \mapsto (o_1,s_2)
      \mapsto \cdots.
$$

A complete run log is a finite prefix of this behavior. Reproducibility means replaying the coalgebra under the same state and dependencies, not merely rerunning the final source file.

## Coinductive traces

Potentially unbounded traces are coinductive streams. In practice, traces are finite because execution is bounded, interrupted, or fails. A useful type is:

$$
  \mathrm{Trace}
  = \nu Z.\; \mathrm{Done}
    + (\mathrm{Event}\times Z),
$$

where $\nu$ indicates a greatest fixed point. A finite implementation can store a list plus termination status:

```python
@dataclass(frozen=True)
class Trace:
    events: tuple[Event, ...]
    outcome: Outcome  # success, failure, timeout, budget
```

The outcome is essential. Truncating a timeout trace and presenting it as a successful prefix destroys semantics.

## History-dependent proposal

A memoryless search uses

$$
  Q(h'\mid h,\tau,f).
$$

A persistent-search agent uses

$$
  Q(h'\mid h,\tau,f,H).
$$

History can be represented as an event-sourced log. Derived summaries, embeddings, and indexes are views of that log, not replacements for it. The raw artifacts permit new retrieval strategies and post hoc auditing.

However, unbounded history creates context and privacy problems. A categorical model does not choose the storage policy; it clarifies that summarization is a morphism that may identify distinct histories. The engineering decision is which distinctions must remain observable.

## Exercises

1. **Concept.** Identify the feedback wire in a ReAct loop and name the state carried around it.
2. **Proof.** Explain why a fixed point equation alone does not imply a terminating computation.
3. **Code.** Implement a bounded traced loop combinator that records every iteration and termination cause.
4. **Design.** Define the optimizer state $S$ for a real code-evolution experiment.
5. **Proof.** Give a bisimulation relation between two simple deterministic state machines.
6. **Concept.** Show how changing the observation type changes whether two harnesses count as equivalent.
7. **Code.** Build an event-sourced candidate history with replay and derived indexes.
8. **Research.** Compare proposer performance with raw history, summaries only, and retrieval over raw history.
9. **Design.** State a well-founded measure for a recursive decomposition harness.
10. **Proof.** For a bounded loop of at most $n$ calls, derive a static upper resource grade from the per-step grade.

# Feedback, Optics, Learners, and the "Text Gradient" Metaphor

## Forward execution and backward information

Optimization systems have a forward pass and a backward information flow:

```text
candidate --execute--> output and trace --evaluate--> score and feedback
    ^                                                     |
    |---------------------- revise ------------------------|
```

In differentiable programming, the backward signal is a derivative. In lens-like systems, a forward map is paired with an update operation. In reflective program evolution, the backward signal is a heterogeneous package of counterexamples, traces, critiques, and constraints.

The analogy is useful because it highlights compositional update. It is dangerous if it implies mathematical properties that textual feedback lacks.

## Lenses

A simple lens from a whole $S$ to a part $A$ has operations

$$
  \mathrm{get}:S\to A,
  \qquad
  \mathrm{put}:S\times A\to S.
$$

Well-behaved lenses satisfy laws such as:

- putting back what was obtained changes nothing;
- getting after putting returns the inserted part;
- consecutive puts collapse to the last one.

For source code, an AST lens can focus on a function or prompt field. A generated update through the lens changes that component while preserving the surrounding program. This is safer than asking a model to rewrite the whole file when only one component is implicated.

## Optics and modular feedback

Optics generalize lenses to richer settings. They can represent traversals, prisms for sum types, and effectful updates. In a typed harness graph, an optic can focus on a submodule while retaining the context needed to rebuild the whole.

A trace-aware optimizer can associate evidence with graph locations:

$$
  (\text{node id},\text{input},\text{output},\text{feedback}).
$$

A local proposer then receives a focused optic. A global proposer receives the entire program and can change structure. Hybrid optimization alternates local, low-risk edits with global architectural proposals.

## Learners as parameterized processes

A supervised learner can be represented by:

- parameters $P$;
- implementation $I:P\times X\to Y$;
- request or backward map that translates desired output information into an input-side signal;
- update map $U:P\times X\times Y\to P$.

Categorical accounts of backpropagation make learner composition explicit. The outer loop of harness evolution resembles a learner whose parameter is source code. But the source space is discrete and structured, and the update is generated by an LM rather than computed by a derivative.

We can write a reflective learner as

$$
  L=(P,I,R,U),
$$

with

$$
  I:P\times X\to T(Y\times\tau),
$$

$$
  R:X\times Y\times\tau\to F,
$$

$$
  U:P\times F\times H\to\mathcal{D}(P).
$$

Here $F$ is a feedback language and $H$ is history. Composition laws are not automatic; they depend on how traces and feedback are attributed to subcomponents.

## Why text feedback is not a derivative

A derivative at $p$ is local, linear to first order, and compositional through a chain rule. Textual criticism may be:

- nonlocal: "replace the architecture with retrieval";
- discontinuous: one token changes a parser grammar;
- contradictory across examples;
- underspecified;
- dependent on hidden model priors;
- impossible to add or scale coherently.

There is usually no meaningful operation $2f$ for feedback sentence $f$, no guaranteed zero feedback, and no law corresponding to

$$
  D(g\circ f)=Dg\circ Df.
$$

A safer term is **language-mediated credit assignment**.

## Feedback algebras

Although feedback is not a vector, it can have algebraic structure. Define a typed sum:

```text
Feedback =
    Counterexample(input, expected, actual)
  | ContractViolation(clause, witness)
  | ResourceOverrun(resource, observed, limit)
  | JudgeCritique(rubric, text, confidence)
  | TraceAnomaly(event_range, diagnosis)
  | ImprovementHint(target, transformation)
```

Each constructor has an interpretation. Counterexamples can be added to a test set. Contract violations reject a candidate. Resource overruns alter the Pareto vector or admissibility. Judge critiques guide proposals but do not prove anything.

This typed feedback algebra is more robust than one unstructured text field. Natural language can remain inside specific constructors.

## Credit assignment across a graph

Suppose a pipeline is $h=c\circ b\circ a$. A final failure may originate in $a$, be amplified by $b$, or be mishandled by $c$. Whole-program feedback avoids premature blame but produces a difficult search problem. Per-node feedback is easier to apply but can be wrong when interactions matter.

A practical strategy uses three levels:

1. deterministic local assertions attach exact violations to nodes;
2. trace analyzers propose causal spans;
3. a global proposer can override local attribution when architecture is implicated.

The archive should record which evidence led to each edit. This creates a causal hypothesis log, not a proof of causality.

## Exercises

1. **Proof.** State and verify the three standard lens laws for a record-field lens.
2. **Code.** Implement an AST lens that edits a Python function docstring without changing the function body.
3. **Concept.** Give three reasons a textual critique fails to be a gradient.
4. **Design.** Define a typed feedback algebra for a retrieval system.
5. **Code.** Route each feedback constructor to a different repair strategy.
6. **Proof.** Show why local updates compose safely only when their focused regions are disjoint or their interaction law is known.
7. **Research.** Compare whole-program rewriting with optic-focused rewriting on repair validity and performance.
8. **Design.** Specify how to attribute model-call cost to nodes in a composed harness.
9. **Concept.** Distinguish causal diagnosis, correlational trace evidence, and a proof of responsibility.
10. **Proof.** Identify which lens law can fail when `put` invokes an LLM and explain the operational consequence.

# Rewrites, Double Categories, and Evidence-Bearing 2-Cells

## Programs compose in two directions

Ordinary categories capture one direction of composition: connect output interfaces to input interfaces. Self-evolving software also has a version direction:

```text
old stage  ----execution----> old downstream
   |                              |
 rewrite                        rewrite
   |                              |
new stage  ----execution----> new downstream
```

A double category has objects, horizontal arrows, vertical arrows, and squares. This is a natural model when horizontal arrows are executable components and vertical arrows are refinements, migrations, or version changes.

A square says that executing then migrating agrees, exactly or approximately, with migrating then executing.

## A rewrite square

Let $h:X\to Y$ be an old harness and $h':X'\to Y'$ a new harness. Let $u:X\to X'$ and $v:Y\to Y'$ be input and output migrations. A rewrite square has boundary

$$
\begin{array}{ccc}
X & \xrightarrow{h} & Y \\
\downarrow u & \Downarrow \alpha & \downarrow v \\
X' & \xrightarrow{h'} & Y'.
\end{array}
$$

The 2-cell $\alpha$ is evidence relating the two paths:

$$
  v\circ h
  \quad\text{and}\quad
  h'\circ u.
$$

Possible meanings of $\alpha$ include:

- a proof of equality;
- a simulation relation;
- a refinement proof;
- a bounded error guarantee;
- a finite regression-test report;
- a statistical confidence statement;
- an LLM judgment.

These evidence kinds must not be conflated. The square should be labeled by its strength.

## Globular rewrites

When interfaces do not change, $u$ and $v$ are identities. The square compares two implementations of the same signature:

$$
  \alpha:h\Rightarrow h'.
$$

This resembles a 2-cell in a bicategory. Vertical composition chains rewrites. Horizontal composition places rewrites inside larger pipelines.

If

$$
  \alpha:f\Rightarrow f'
  \quad\text{and}\quad
  \beta:g\Rightarrow g',
$$

then a horizontal composite should justify

$$
  g\circ f \Rightarrow g'\circ f'.
$$

The proof is straightforward when $\alpha$ and $\beta$ are exact equalities and effects obey the needed laws. It is not straightforward for empirical improvements: two locally improved stages can compose into a worse system.

## Refinement versus equivalence

An equivalence preserves behavior in both directions under the chosen observation. A refinement is directed. For example, $h'$ may satisfy all old cases and more, use fewer capabilities, or have a tighter error bound:

$$
  h \preceq h'.
$$

Refinement evidence composes transitively. It need not be invertible. Modeling every rewrite as equality erases the direction that optimization cares about.

A useful hierarchy is:

```text
syntactic edit
    < builds and type-checks
    < preserves interface
    < passes regression suite
    < statistically improves held-out metric
    < refines a formal contract
    < is semantically equivalent
```

The order is not total, and the levels do not always imply one another without assumptions. A semantically equivalent program may be slower; a statistically better program may violate a rare hard contract.

## Proof-relevant transformation logs

A transformation log should store more than edges between version identifiers. Each edge can carry:

```python
@dataclass(frozen=True)
class RewriteEvidence:
    parent_hash: str
    child_hash: str
    proposal_context_hash: str
    interface_check: CheckResult
    capability_check: CheckResult
    proof_artifacts: tuple[ArtifactRef, ...]
    regression_report: Report
    statistical_report: Report
    judge_reports: tuple[JudgeReport, ...]
    resource_delta: ResourceVector
    rationale: str
```

This is proof-relevant graph data: different evidence for the same pair of versions remains distinguishable. That distinction becomes important in HoTT, where there may be multiple paths between the same points.

## Rewriting modulo laws

Generated architectures often differ only by category laws:

$$
  h\circ\mathrm{id}=h,
  \qquad
  (k\circ g)\circ f=k\circ(g\circ f).
$$

A term-rewriting system can normalize such expressions. More domain-specific laws include:

- two adjacent pure maps can fuse;
- repeated normalization is idempotent;
- caching after a deterministic function can move before a pure projection under a key condition;
- a verifier after a proven-correct stage may be redundant for the proved property.

Searching modulo laws reduces duplicate candidates. But orientation matters: rewrite rules must terminate or use an equality-saturation engine such as an e-graph. An LLM can propose equalities; a checker must validate them before adding them to the rewrite theory.

## Squares as promotion gates

A deployment promotion can require a square with specified evidence:

```text
Candidate source
   -> type/sandbox square
   -> formal-contract square
   -> regression square
   -> statistical-generalization square
   -> human-approval square
   -> deployable artifact
```

The gate is a composition of predicates and evidence-producing processes. The optimizer may create candidates continuously, but only artifacts inhabiting the deployment type pass.

## Exercises

1. **Design.** Draw a double-category square for an API version migration and generated implementation rewrite.
2. **Proof.** Show that exact commutative squares compose horizontally.
3. **Concept.** Explain why two empirical-improvement squares need not compose into an empirical improvement.
4. **Code.** Define a rewrite-evidence data model and store a version graph in SQLite or a graph database.
5. **Design.** Label every edge in a real CI/CD pipeline by its evidence strength.
6. **Proof.** Show that semantic equivalence is symmetric while refinement need not be.
7. **Research.** Use an e-graph to deduplicate architecture expressions generated by an LLM.
8. **Concept.** Give two distinct pieces of evidence for the same source rewrite. Why should they not be collapsed?
9. **Design.** Define a deployment type whose constructors enforce a sequence of promotion gates.
10. **Proof.** State conditions under which replacing equivalent pure subprograms inside an effectful context preserves behavior.

# Pareto Frontiers, Ordered Enrichment, and Selection Policy

## Candidate comparison is usually partial

No single score captures all relevant properties of a harness. Let

$$
  m(h)=(q,-c,-l,s,p)
$$

represent quality, negative cost, negative latency, safety, and proof coverage. Componentwise comparison creates a preorder. Most candidate pairs are incomparable.

An optimizer that always collapses this vector to one scalar makes a policy decision during search. This can be appropriate when policy is stable, but it often destroys candidates that would be preferred under a future deployment context.

## Pareto archives as antichains

A Pareto archive contains nondominated candidates. Insertion is simple:

```python
def insert(archive, candidate):
    if any(dominates(x.score, candidate.score) for x in archive):
        return archive
    survivors = [
        x for x in archive
        if not dominates(candidate.score, x.score)
    ]
    return survivors + [candidate]
```

Real archives need tolerance for noise. If scores have confidence intervals, strict componentwise comparison is unstable. Options include:

- dominance only when confidence bounds separate;
- Bayesian posterior probability of dominance;
- epsilon-dominance;
- repeated evaluation of frontier candidates;
- robust objectives such as lower confidence bounds.

## Per-instance Pareto selection

A candidate may excel on one subset of examples and fail on another. GEPA's candidate selection preserves candidates with instance-specific strengths. Formally, each candidate has a score vector over examples:

$$
  v(h)=(\mu(h,x_1),\ldots,\mu(h,x_n)).
$$

A candidate can be retained because it is best on some coordinates even if its mean is not best. This creates diversity from behavior rather than from syntax.

The danger is memorization. A specialist may exploit quirks of one training example. The archive needs held-out evaluation and perhaps clustering over semantically meaningful regions rather than individual examples.

## Ordered and enriched categories

A locally ordered category has a preorder on each hom-set $\mathcal{C}(X,Y)$, compatible with composition:

$$
  f\preceq g
  \implies
  h\circ f\circ k
  \preceq
  h\circ g\circ k.
$$

This law says refinement is substitutive. For functional correctness refinement, it can often be arranged. For empirical accuracy or latency, it generally fails: surrounding context can reverse the comparison.

This distinction identifies which objectives support modular optimization. Capability reduction is often substitutive: a component that requires fewer capabilities remains no more privileged in a fixed context. Local latency improvement may not be substitutive if it changes batching or cache behavior. Accuracy on a component dataset is rarely substitutive.

## Scalarization as a policy morphism

A scalarization is a map

$$
  \phi:\mathbb{R}^k\to\mathbb{R}.
$$

Weighted sums, lexicographic orders, constrained optimization, and utility functions are examples. The map is not neutral. It encodes tradeoffs and may identify distinct score vectors.

Keep the vector and record the scalarization used for each decision. A later audit can then distinguish "the candidate was inferior" from "the candidate was rejected under policy $\phi$ at time $t$."

## Constraints before objectives

A robust selection pipeline first restricts to admissible candidates:

$$
  \mathcal{H}_C
  =\{h\in\mathcal{H}\mid C(h)\}.
$$

It then optimizes soft objectives on $\mathcal{H}_C$.

Turning a hard safety condition into a large negative score is unsafe because enough improvement elsewhere can compensate for it. Lexicographic handling is better:

1. reject contract violations;
2. among admissible candidates, compare quality and resources;
3. use a deployment policy to select from the frontier.

## Archive pressure and complexity

Archives can grow exponentially with objectives. Practical systems use:

- epsilon grids;
- clustering;
- age limits;
- novelty thresholds;
- complexity penalties;
- deployment-relevant niches;
- proof-coverage tiers.

Complexity is not merely source length. Better measures include cyclomatic complexity, number of effects, dependency count, proof obligation count, trace entropy, and operational surface area.

## Exercises

1. **Proof.** Prove that a finite Pareto archive is an antichain under strict dominance.
2. **Code.** Extend Pareto insertion with epsilon-dominance.
3. **Design.** Choose a scalarization for a batch offline job and a latency-sensitive online service. Explain the policy difference.
4. **Proof.** Construct a context that reverses the latency ordering of two components because of batching.
5. **Concept.** Which of security capability, average accuracy, and source length are likely to be substitutive under composition?
6. **Code.** Maintain confidence intervals for stochastic candidate scores and compare candidates conservatively.
7. **Research.** Compare mean-score selection, per-instance Pareto selection, and MAP-Elites on generalization.
8. **Design.** Define an archive-pruning policy that preserves proof coverage and low-cost candidates.
9. **Proof.** Show why replacing a hard constraint by a finite penalty permits some violating candidate to win if other objectives are unbounded.
10. **Concept.** Explain scalarization as an information-losing map.

# A Categorical Model of Reflective Harness Evolution

## The execution category

Let $\mathcal{C}$ be a category of typed schemas and pure transformations. Let $T_r$ be a graded effect system combining probability, exceptions, tools, state, and traces. Define the execution category

$$
  \mathcal{H}=\mathrm{Kl}(T),
$$

whose morphisms are harnesses

$$
  h:X\to T_r(Y\times\mathrm{Trace}).
$$

Pure code embeds through $J:\mathcal{C}\to\mathcal{H}$. A synthesized router may combine $J(d)$ and an LM-backed morphism $\ell$ through coproduct elimination.

## Candidate space as a typed fiber

Fix an interface $(X,Y)$ and contract $C$. Candidate implementations live in a fiber

$$
  \mathrm{Impl}_C(X,Y)
  =
  \sum_{h\in\mathcal{H}(X,Y)}\mathrm{Admissible}_C(h).
$$

The dependent sum is essential. It does not merely say that admissible candidates exist; it packages each candidate with its own evidence.

Soft objective evaluation is a stochastic map

$$
  M:\mathrm{Impl}_C(X,Y)\times D
  \to
  \mathcal{D}(\mathbb{R}^k\times F\times E),
$$

where $D$ is an evaluation dataset, $F$ feedback, and $E$ additional evidence such as traces and counterexamples.

## The proposal kernel

The LLM proposer is modeled as

$$
  Q:
  \mathrm{Source}
  \times \mathrm{Contract}
  \times \mathrm{Evidence}
  \times \mathrm{History}
  \to
  \mathcal{D}(\mathrm{Source}).
$$

A build-and-check map attempts to lift source into the candidate fiber:

$$
  B:\mathrm{Source}\to
  \mathrm{CandidateError}+\mathrm{Impl}_C(X,Y).
$$

The proposer is allowed to be unreliable. Soundness is assigned to $B$ and its checkers, not to $Q$.

## Optimizer state and coalgebra

Let

$$
  S=
  \mathrm{Archive}
  \times\mathrm{History}
  \times\mathrm{Budget}
  \times\mathrm{Config}
  \times\mathrm{Randomness}.
$$

The outer optimizer is a coalgebra

$$
  E:S\to\mathcal{D}(O\times S).
$$

One observation $O$ records parent choice, proposal, build result, verifier result, objective vector, archive update, and consumed resources. A stopping policy maps state to either `continue` or a selected deployment artifact.

This model accommodates GEPA, Flex, Meta-Harness, AlphaEvolve-like systems, and simpler best-of-N search by changing $Q$, $M$, archive policy, and state.

## Rewrites as vertical arrows

Execution morphisms compose horizontally. Candidate rewrites form vertical arrows. Evidence-bearing squares state what is preserved. Exact refactorings, contract refinements, statistical improvements, and judge preferences are different 2-cell labels.

The structure can be summarized as:

```text
Objects:       typed schemas and contracts
Horizontal:   executable harnesses
Vertical:     representation changes or refinements
Squares:      evidence relating old and new behavior
2-level data: alternative evidence and coherence between rewrites
```

This avoids reducing evolution to a random walk over source strings.

## Architecture grammar and interpretation

Let $\mathcal{A}$ be a free typed operad or syntax category generated by approved architecture primitives. An interpretation

$$
  \llbracket-\rrbracket:\mathcal{A}\to\mathcal{H}
$$

turns architecture terms into executable harnesses. The LLM proposes terms in $\mathcal{A}$ or source that is parsed into them.

This split supports:

- type checking before execution;
- capability analysis from syntax;
- normalization modulo architecture laws;
- multiple backends;
- proof by induction on architecture terms;
- auditable diffs at the semantic-node level.

Unrestricted Python can remain an escape hatch behind a narrower, separately reviewed primitive.

## What the model does and does not guarantee

The categorical model guarantees nothing merely by being categorical. It supplies places to state laws.

Possible guarantees include:

- every candidate has the declared input/output interface;
- composition is well-typed;
- resource grades compose according to a monoid;
- only declared effects can be requested;
- rewrite evidence is retained and typed;
- exact equivalences compose lawfully;
- optimizer history is modeled explicitly.

It does not guarantee:

- the objective reflects user value;
- the judge is unbiased;
- held-out data matches deployment;
- the LLM proposer explores useful candidates;
- statistical improvement generalizes;
- the formal contract captures all safety requirements.

Mathematics clarifies assumptions; it does not remove the need to choose them.

## Worked derivation: deterministic fast path

Suppose $X$ is partitioned by a decidable predicate $p:X\to\mathrm{Bool}$. Let

$$
 X_e=\{x:X\mid p(x)=\mathrm{true}\},
 \qquad
 X_h=\{x:X\mid p(x)=\mathrm{false}\}.
$$

Assume an isomorphism $X\cong X_e+X_h$. Let

$$
 d:X_e\to Y
$$

be a proved deterministic solver and

$$
 \ell:X_h\to T_r(Y)
$$

be an LM branch. The combined harness is

$$
 h=[J(d),\ell]\circ\mathrm{split}_p.
$$

If $q=\Pr[p(x)=\mathrm{false}]$ under deployment distribution $P$, and the deterministic branch has negligible LM cost, expected LM-call cost is approximately $q r$. The optimization problem includes learning or synthesizing $p$ while preserving soundness of the easy branch.

A dangerous router optimizes $q$ alone and sends uncertain inputs to $d$. A safe router needs evidence:

$$
  \forall x,\;p(x)=\mathrm{true}
  \to \mathrm{Correct}(x,d(x)).
$$

When this proposition cannot be proved, estimate and monitor the conditional error of the fast path separately.

## Exercises

1. **Concept.** Instantiate every symbol in the model for a customer-support routing harness.
2. **Proof.** Show that build failure represented by a sum type cannot be mistaken for an admissible candidate without eliminating the sum.
3. **Code.** Implement a typed architecture AST and an interpreter that produces trace events.
4. **Design.** Define hard-check and soft-evaluation maps for a code-generating agent.
5. **Proof.** Derive the expected call cost of a two-branch router with nonzero costs in both branches.
6. **Research.** Estimate the conditional error of an optimized deterministic fast path under distribution shift.
7. **Design.** Decide which rewrite evidence forms compose automatically and which require re-evaluation.
8. **Concept.** Explain why the proposal model is intentionally placed outside the trusted soundness boundary.
9. **Code.** Serialize optimizer coalgebra state so a run can resume and replay exactly.
10. **Proof.** State sufficient conditions for the interpretation of architecture terms to preserve composition.

# Propositions as Types and Programs as Proofs

## Curry-Howard for working programmers

The Curry-Howard correspondence relates logic and type theory:

| Logic | Type theory | Programming intuition |
|---|---|---|
| proposition $P$ | type $P$ | specification |
| proof of $P$ | term $p:P$ | value satisfying the specification |
| implication $P\to Q$ | function type $P\to Q$ | transformer of evidence |
| conjunction $P\land Q$ | product $P\times Q$ | pair of proofs |
| disjunction $P\lor Q$ | sum $P+Q$ | tagged alternative |
| truth | unit type | trivial value |
| falsehood | empty type | impossible value |
| universal quantifier | dependent product | function returning evidence for each input |
| existential quantifier | dependent sum | witness packaged with evidence |

A proof checker is therefore a type checker for proof terms. This does not mean every production programming language makes all proofs explicit. It means types can be designed to carry logical content.

## Dependent function types

A dependent function type

$$
  \prod_{x:A}B(x)
$$

contains functions that, for each $x:A$, produce a value in the type $B(x)$. The result type depends on the input value.

Universal correctness can be expressed as:

$$
  \prod_{x:X}\mathrm{Correct}(x,h(x)).
$$

A term of this type is a function that gives a proof for every input. The quantifier is computational: applying the proof to a particular $x$ yields evidence for that case.

In Lean-like notation:

```lean
-- Schematic, not tied to a particular domain library.
def CorrectHarness (h : X -> Y) : Prop :=
  forall x : X, Correct x (h x)
```

## Dependent sum types

A dependent sum

$$
  \sum_{x:A}B(x)
$$

contains a witness $x:A$ paired with evidence $b:B(x)$. This is the type-theoretic existential.

A sorted vector package is:

$$
  \sum_{v:\mathrm{Vector}\;\mathbb{Z}\;n}\mathrm{Sorted}(v).
$$

A proof-carrying candidate is:

$$
  \sum_{h:\mathrm{Harness}(X,Y)}\mathrm{Admissible}_C(h).
$$

The evidence depends on the exact candidate. A proof that one source program obeys a capability policy cannot be silently attached to a different source hash.

## Equality types

For $a,b:A$, the identity type

$$
  a=_A b
$$

contains evidence that $a$ and $b$ are equal. In intensional type theory, equality is not automatically reduced to an external Boolean comparison. Proofs can be constructed by reflexivity and transformed by induction.

Program equivalence is harder than value equality. One may seek:

$$
  h=_{{X\to Y}} h',
$$

but function equality often requires function extensionality:

$$
  \left(\prod_{x:X}h(x)=h'(x)\right)
  \to h=h'.
$$

For effectful or stochastic harnesses, the relevant equality may be equality of distributions, traces, or observations rather than definitional equality of code.

## Inductive types and interpreters

A safe architecture language can be an inductive type:

```lean
inductive Harness : Type -> Type -> Type where
  | pure     : (X -> Y) -> Harness X Y
  | predict  : Signature X Y -> Harness X Y
  | compose  : Harness X Y -> Harness Y Z -> Harness X Z
  | route    : (X -> Either A B)
             -> Harness A Y -> Harness B Y -> Harness X Y
  | fallback : Harness X Y -> Harness X Y -> Harness X Y
```

Every architecture is built from approved constructors. An interpreter gives meaning:

```lean
def run : Harness X Y -> X -> Eff Y
```

Proofs proceed by induction on the architecture. For example, if every primitive respects a capability set and composition unions capabilities, one can prove a capability bound for every term.

## Proof irrelevance and proof relevance

Some systems treat all proofs of the same proposition as interchangeable. For audit trails, evidence may be proof-relevant: two certificates can have different issuers, assumptions, costs, or derivations.

Distinguish:

- the proposition that a candidate passed a test suite;
- the detailed test report witnessing that proposition;
- the cryptographic identity of the artifact tested;
- the environment in which the test ran.

Erasing proof details can be safe for execution but unsafe for governance. A deployment artifact may retain hashes and provenance even when the runtime does not inspect the proof term.

## Decidable propositions

A proposition $P$ is decidable when one can compute either evidence of $P$ or evidence of $\neg P$:

$$
  \mathrm{Decidable}(P)=P+\neg P.
$$

Examples include finite schema checks and bounded resource analyses. General semantic properties of arbitrary programs are not decidable. Rice's theorem and the halting problem prevent a universal checker for nontrivial behavior of unrestricted code.

This motivates restricted languages, bounded verification, proof-carrying annotations, and human review. The answer to undecidability is not "let the LLM decide." An LLM can suggest proofs or invariants, but the trusted checker must verify them in a decidable kernel.

## Exercises

1. **Concept.** Translate implication, conjunction, disjunction, universal quantification, and existential quantification into programming constructs.
2. **Proof.** Construct a term of type $A\to(B\to A)$.
3. **Proof.** Construct functions in both directions between $A\times(B+C)$ and $(A\times B)+(A\times C)$.
4. **Code.** Encode a small harness AST as an algebraic data type and write a total interpreter.
5. **Design.** Define the dependent-sum fields of a proof-carrying deployment artifact.
6. **Concept.** Explain why a Boolean `passed=True` is weaker than a proof term tied to an artifact hash and assumptions.
7. **Proof.** Write the type of a function that returns a sorted permutation of its input list, including both properties.
8. **Research.** Formalize one deterministic helper from an LM harness in Lean, Coq, Agda, Idris, or F*. Measure how much code is specification and proof.
9. **Concept.** Give a semantic property that is undecidable for arbitrary Python but decidable for a restricted finite-state DSL.
10. **Proof.** Explain the role of function extensionality in moving from pointwise equality to function equality.

# Contracts, Refinement Types, and Specification Layers

## A contract is layered

A realistic contract for a harness is not one predicate. It has several layers:

1. **Interface contract**: input and output schemas.
2. **Effect contract**: allowed operations and capabilities.
3. **Resource contract**: call, token, time, memory, and money bounds.
4. **Functional contract**: preconditions, postconditions, and invariants.
5. **Information-flow contract**: what data may reach which tools or models.
6. **Statistical contract**: calibrated error or risk under stated distributions.
7. **Governance contract**: provenance, review, and promotion requirements.

Only some layers are fully decidable or formally provable in a given implementation. The contract should mark which clauses are proved, tested, monitored, judged, or assumed.

## Refinement types

A refinement type narrows a base type by a predicate:

$$
  \{x:A\mid P(x)\}.
$$

Examples:

$$
  \{n:\mathbb{N}\mid n\le 3\},
$$

$$
  \{s:\mathrm{String}\mid \mathrm{ValidJSON}(s)\},
$$

$$
  \{y:Y\mid \mathrm{Post}(x,y)\}.
$$

A function with a postcondition can have type

$$
  (x:X)\to\{y:Y\mid \mathrm{Post}(x,y)\}.
$$

Liquid types restrict refinements to decidable logical fragments and discharge obligations with SMT solvers. Systems such as Synquid use refinement types not only to verify but to synthesize programs.

## Precondition and postcondition contracts

A Hoare triple

$$
  \{P\}\;c\;\{Q\}
$$

states that if precondition $P$ holds and command $c$ terminates, postcondition $Q$ holds. Total-correctness variants also establish termination.

For a harness:

$$
  \mathrm{pre}:X\to\mathrm{Prop},
$$

$$
  \mathrm{post}:\prod_{x:X}Y\to\mathrm{Prop}.
$$

The desired type is

$$
  (x:X)\to \mathrm{pre}(x)
  \to \sum_{y:Y}\mathrm{post}(x,y).
$$

This makes the precondition evidence an input and packages the output with postcondition evidence.

## Intrinsic and extrinsic verification

In an **intrinsic** representation, only well-formed or correct programs can be constructed. A typed architecture AST is intrinsic with respect to interface compatibility. A constructor for a bounded loop might require a natural number bound.

In an **extrinsic** representation, programs are ordinary syntax and a separate predicate states correctness:

$$
  \mathrm{WellTyped}(p),
  \qquad
  \mathrm{Safe}(p),
  \qquad
  \mathrm{Correct}(p).
$$

Intrinsic representations eliminate classes of invalid proposals but can constrain expressiveness. Extrinsic checks are flexible but create proof obligations after generation. A practical system uses both: an intrinsic high-level DSL with extrinsic verification of embedded code and domain properties.

## Contract refinement

A new contract $C'$ refines $C$ when every implementation satisfying $C'$ also satisfies $C$:

$$
  C'\Rightarrow C.
$$

For function contracts, refinement commonly permits weaker preconditions and stronger postconditions. If clients previously supplied inputs satisfying $P$, a replacement should not demand more. If clients expected $Q$, a replacement may guarantee more.

With effects and resources, refinement can mean:

- a subset of capabilities;
- a lower worst-case resource bound;
- a smaller set of possible errors;
- a more informative output type;
- an equal or stronger functional guarantee.

This creates a directed order on contracts and implementations.

## Specifications as search-space shapers

A specification is not only a final filter. It shapes synthesis. Refinement types decompose obligations across components. An architecture grammar excludes irrelevant structures. Counterexamples eliminate candidate regions. Resource types prevent unbounded loops from entering the search.

Compare two prompts to a proposer:

```text
Write a better solution.
```

and

```text
Construct a term of Harness[X,Y] using only Pure, Predict,
Route, and Verify. It must inhabit CallsAtMost 2 and must
produce a proof of SchemaSafe. The failing case is x0.
```

The second search problem has more information and fewer invalid outputs. Formalization serves optimization efficiency as well as correctness.

## Incomplete specifications and escape hatches

Overly narrow contracts can exclude useful solutions. A generated code system therefore needs a disciplined way to propose contract changes. The proposer may output either:

```text
ImplementationCandidate(C)
```

or

```text
ContractChangeProposal(C, C', rationale, migration, risk)
```

A contract change must not be accepted through the same automatic path as an implementation that satisfies the existing contract. It changes the problem and needs separate review.

This distinction blocks a common form of metric gaming: weakening the test or contract so the candidate appears successful.

## Exercises

1. **Design.** Write a seven-layer contract for an email-triage harness.
2. **Proof.** Show that a function with weaker precondition and stronger postcondition can substitute for one with the original contract, under standard assumptions.
3. **Code.** Implement runtime refinement types for bounded integers and validated URLs. Document what remains unchecked statically.
4. **Concept.** Give one property best encoded intrinsically and one best checked extrinsically.
5. **Design.** Define a sum type separating implementation proposals from contract-change proposals.
6. **Proof.** If capability sets are ordered by inclusion, show that requiring a subset is a refinement.
7. **Research.** Compare synthesis success and candidate validity under an unrestricted prompt, JSON schema, typed DSL, and refinement-type specification.
8. **Concept.** Explain why tests are examples of a contract but are not generally the complete contract.
9. **Code.** Generate proof obligations from a small architecture AST and discharge the decidable ones automatically.
10. **Design.** Mark each clause of a real specification as proved, tested, monitored, judged, or assumed.

# Proof-Carrying Harnesses and a Typed Intermediate Representation

## From source artifact to certified artifact

Proof-Carrying Code proposes that untrusted code arrive with a proof that it obeys a safety policy, while a small trusted checker validates the proof. The producer may use expensive theorem proving; the consumer trusts only the checker and policy.

For reflective harness evolution, define:

$$
\begin{aligned}
  \mathrm{CertifiedHarness}(C)
  = \sum_{p:\mathrm{Program}}\;&\mathrm{Typing}(p) \\
  &\times\mathrm{CapabilitySafe}_C(p) \\
  &\times\mathrm{ResourceSafe}_C(p) \\
  &\times\mathrm{FunctionalEvidence}_C(p) \\
  &\times\mathrm{Provenance}(p).
\end{aligned}
$$

Not every factor must be a full theorem. The type can distinguish proof, bounded-model-check report, signed test report, and statistical certificate. What matters is that evidence kind and assumptions are explicit.

## Why arbitrary Python is a difficult proof target

Python includes reflection, dynamic imports, mutable global state, exceptions, metaprogramming, native extensions, and an evolving runtime. Proving arbitrary generated Python safe is difficult. A sandbox reduces operational risk but does not produce a semantic proof.

A better architecture has three layers:

```text
LLM proposal
    |
    v
Typed Harness IR  --static checks/proofs--> Certified IR
    |
    v
Verified or audited compiler
    |
    v
Sandboxed executable code
```

The intermediate representation contains only approved constructs. Its interpreter or compiler is part of the trusted base.

## A sample typed IR

A compact IR might include:

```text
Pure(f)                    -- total approved function
Predict(sig, prompt_id)    -- one model call
Tool(tool_id, arg_map)     -- approved tool call
Seq(a, b)                  -- sequential composition
Pair(a, b)                 -- parallel dataflow
Route(test, left, right)   -- typed case split
Retry(policy, h)           -- bounded retry
Verify(predicate, h)       -- check output, return typed failure
Fallback(primary, backup)  -- explicit recovery
Memo(key, h)               -- policy-controlled cache
```

Each node has a typing rule, effect row, resource expression, and trace semantics. For example:

$$
  \frac{
    h_1:\mathrm{Harness}_{r_1}(X,Y)
    \quad
    h_2:\mathrm{Harness}_{r_2}(Y,Z)
  }{
    \mathrm{Seq}(h_1,h_2):
    \mathrm{Harness}_{r_1+r_2}(X,Z)
  }.
$$

A bounded retry with at most $n$ attempts multiplies a worst-case resource bound, while its expected cost requires a probabilistic failure model.

## Capability typing

Associate each term with an effect or capability set $\epsilon$:

$$
  \Gamma\vdash h:X\to Y\;!\;\epsilon.
$$

Composition unions capabilities:

$$
  \epsilon(\mathrm{Seq}(h_1,h_2))
  =\epsilon(h_1)\cup\epsilon(h_2).
$$

A deployment policy supplies an allowlist $A$. Admissibility requires

$$
  \epsilon(h)\subseteq A.
$$

Dynamic tool arguments may require additional predicates, such as domain allowlists, data-classification checks, or rate limits. Capability typing states what can be requested; handlers enforce it at runtime.

## Information-flow types

Suppose inputs contain public data $P$ and secrets $S$. A noninterference property says public outputs should not depend on secrets, except through approved declassification.

A simple security lattice might have labels

$$
  \mathrm{Public}\sqsubseteq\mathrm{Internal}
  \sqsubseteq\mathrm{Confidential}.
$$

Types track labels through transformations. A call to an external model may accept only `Public` data. A declassifier is an explicit privileged morphism with a proof obligation or human policy.

LLM-generated code is particularly likely to concatenate convenient context. Information-flow typing blocks accidental secret leakage structurally.

## Resource proofs

Resource expressions can be derived compositionally:

```text
calls(Pure)                 = 0
calls(Predict)              = 1
calls(Seq(a,b))             = calls(a) + calls(b)
calls(Route(t,a,b))         = calls(t) + max(calls(a), calls(b))
calls(Retry(n,h))           = n * calls(h)
```

For input-dependent loops or recursion, one needs size indices and termination measures. A vector of length $n$ can carry $n$ in its type. A map operation then has a call bound proportional to $n$.

Expected cost is not derivable from syntax alone unless branch probabilities are known. Keep `WorstCase r` and `Expected model r` distinct.

## Compiler and interpreter trust

Even a perfectly typed IR can be compiled incorrectly. Options include:

- execute a small verified interpreter directly;
- verify the compiler;
- validate compiled output with translation validation;
- keep the executable sandboxed and compare traces against IR semantics;
- reduce the compiler to a simple code generator with extensive property tests.

Translation validation is attractive for generated harnesses: instead of proving one optimizer or compiler correct for all time, validate each produced artifact against its IR-level meaning.

## Proof-producing proposal workflow

An LLM can contribute to proof without becoming trusted:

1. propose an IR term;
2. propose invariants, lemmas, or proof scripts;
3. run a proof assistant or solver;
4. receive exact error messages and counterexamples;
5. revise the term or proof;
6. accept only when the kernel checks.

This is proof search with an untrusted heuristic. The trusted kernel remains small.

## Exercises

1. **Design.** Define a typed IR for a tool-using research agent with no raw code escape hatch.
2. **Proof.** Derive the capability set and worst-case call bound for a nested `Route` and `Retry` term.
3. **Code.** Implement an IR type checker and interpreter. Reject mismatched composition before execution.
4. **Design.** Add information-flow labels and prevent confidential data from reaching an external predictor.
5. **Proof.** State a soundness theorem connecting the IR effect analysis to runtime handler calls.
6. **Concept.** Explain why a sandbox and proof-carrying code address different threats.
7. **Research.** Compare direct Python generation with IR generation on expressive power, candidate validity, and optimization performance.
8. **Code.** Implement translation validation for one IR node by comparing reference-interpreter and generated-code outputs over exhaustive finite inputs.
9. **Design.** Specify the trusted computing base and how each component is updated.
10. **Proof.** Explain why expected branch cost cannot be inferred from syntax without a distributional assumption.
11. **Concept.** Distinguish proof production, proof checking, and proof-certificate storage.

# Counterexample-Guided Synthesis with an LLM Proposer

## Classical CEGIS

Counterexample-Guided Inductive Synthesis addresses problems of the form

$$
  \exists p\in\mathcal{P}.\;\forall x\in X.\;\varphi(p,x).
$$

It alternates two phases:

1. **Synthesis:** find a candidate $p$ satisfying the specification on a finite sample $S\subseteq X$.
2. **Verification:** ask whether there exists $x$ such that $\neg\varphi(p,x)$. If so, add the counterexample to $S$ and repeat. If not, accept.

```text
sample S = initial examples
loop:
    p = synthesize(S)
    x = verify_or_counterexample(p)
    if no counterexample exists:
        return p
    S = S union {x}
```

When the verifier is sound and complete for the chosen domain and candidate language, termination with `p` yields a proof that $p$ satisfies the specification.

## LLM as inductive synthesizer

Replace the symbolic synthesizer with a language model:

$$
  p'\sim Q(-\mid\mathrm{spec},S,\mathrm{history},\mathrm{feedback}).
$$

The LLM can exploit broad priors and propose complex algorithms. The verifier remains symbolic, exhaustive, proof-assistant-based, or otherwise trusted. Failed proof attempts and counterexamples become high-bandwidth feedback.

This is a strong pattern because it assigns each component a suitable role:

- the LLM searches a huge structured space heuristically;
- the verifier decides a formal question in its supported fragment;
- the outer loop manages evidence and budget.

The model may repeatedly fail to find a valid program, but it cannot cause an invalid one to be certified if the checker is sound.

## From one verifier to a verifier stack

Real harnesses need a stack:

```text
parse/type verifier
capability verifier
resource verifier
functional verifier
bounded model checker
property-based testing
statistical evaluator
LLM judge
human review
```

Only the first several may produce formal counterexamples. A statistical failure is a sampled witness. A judge critique is a heuristic diagnosis. The feedback algebra should retain source and strength.

A candidate can be in one of several states:

```text
IllFormed
WellTyped
PolicyAdmissible
FormallyVerified(fragment)
EmpiricallyQualified(dataset, confidence)
HumanApproved(scope)
```

Avoid a single Boolean called `verified`.

## Counterexamples as dependent data

A counterexample should include the violated clause:

$$
  \mathrm{Counterexample}(p)
  =
  \sum_{x:X}\sum_{c:\mathrm{Clause}}
  \mathrm{Violates}(p,x,c).
$$

This package tells the proposer what failed and gives the checker evidence. For a resource violation, the witness may be a path through control flow. For information flow, it may be a taint trace. For equivalence, it is an input where outputs differ.

## Proof repair

Generated code changes can invalidate proofs. A proof-repair loop treats compiler and proof-assistant errors as structured counterexamples. The proposer can revise:

- implementation only;
- proof only;
- both implementation and proof;
- an auxiliary lemma;
- the architecture, while preserving the external contract.

The contract itself is not automatically mutable. A proposal to weaken it enters a separate governance path.

## Approximate CEGIS

Many LM tasks lack a decidable complete specification. The loop becomes approximate:

1. synthesize from current evidence;
2. search for failures using tests, fuzzing, adversarial generation, and judges;
3. add discovered failures;
4. stop under a budget and report residual uncertainty.

This resembles CEGIS but does not inherit its proof guarantee. Call it **counterexample-guided empirical synthesis** unless a formal verifier closes the universal quantifier.

A useful mixed objective is:

$$
  \text{first satisfy all decidable hard clauses, then maximize soft quality}.
$$

## Adversarial counterexample generation

An LLM can also generate tests. This introduces an adversarial game:

$$
  \min_h\max_x \mathrm{loss}(h,x).
$$

The counterexample generator searches for inputs that expose failures. The harness proposer searches for repairs. A deterministic oracle or human must adjudicate expected behavior when possible; otherwise two models can co-evolve around shared errors.

Maintain separate models, prompts, data, and hidden test sources to reduce correlated blind spots.

## A verified fast-path pattern

Consider a hybrid classifier:

```text
if proved_predicate(x):
    return proved_solver(x)
else:
    return model_solver(x)
```

The deterministic branch carries a theorem:

$$
  \forall x,\;p(x)\to \mathrm{Correct}(x,d(x)).
$$

The LLM branch is evaluated statistically. Optimization can widen $p$ only by proving the theorem for the wider region. This creates a monotone expansion of the certified fast path.

When full proofs are impossible, use a conservative runtime verifier: the deterministic branch returns either a result plus certificate or `Unknown`. Only certified results bypass the model.

## Exercises

1. **Proof.** Write the $\exists\forall$ formula for synthesizing a bounded integer function from examples and a postcondition.
2. **Code.** Implement CEGIS for a small linear-arithmetic grammar using exhaustive verification over a finite domain.
3. **Design.** Replace the synthesizer with an LLM stub and define structured feedback from the verifier.
4. **Concept.** Explain exactly which CEGIS guarantee disappears when the verifier is replaced by random testing.
5. **Proof.** Define the dependent type of a counterexample tied to a contract clause.
6. **Code.** Implement a verifier stack that returns a tagged result rather than a Boolean.
7. **Research.** Compare proof-assistant error messages, minimized counterexamples, and free-form judge critiques as repair feedback.
8. **Design.** Create a conservative certified fast path for one domain operation.
9. **Proof.** Show that widening the fast-path predicate while preserving its theorem cannot reduce the set of certified inputs.
10. **Concept.** Why should a contract-change proposal be excluded from the ordinary repair loop?
11. **Research.** Build an adversarial test generator and measure whether it finds failures not present in a static benchmark.

# Effects, Weakest Preconditions, and What Can Be Proved

## Specifications for effectful code

A postcondition for a pure function is a predicate on its output. For effectful code, specifications must account for state, exceptions, probability, and traces.

A weakest-precondition transformer maps a postcondition $Q$ to the weakest input condition required to ensure it:

$$
  \mathrm{wp}(c,Q):X\to\mathrm{Prop}.
$$

A Dijkstra monad indexes computations by such specifications. It connects monadic effect semantics with dependent verification. Systems such as F* use this approach to reason about effectful programs.

For a stateful computation, $Q$ may mention both result and final state. For exceptions, it may specify allowed errors. For logging, it may constrain trace events. For model calls, a deterministic postcondition cannot generally promise semantic correctness of an unconstrained stochastic output.

## Three proof boundaries

Separate three layers:

### Wrapper correctness

One can prove that the harness:

- validates inputs;
- calls only allowed tools;
- never exceeds a static call bound;
- handles every parser outcome;
- logs required events;
- routes certified cases correctly;
- returns a schema-conforming output or typed failure.

### Model-conditional correctness

One can prove:

$$
  \mathrm{ModelAssumption}(x,y)
  \to \mathrm{Post}(x,h(x,y)).
$$

For example, if a model returns a valid proof term, the checker accepts only a true theorem. The system is correct conditional on successful certification, not conditional on the model being honest.

### Statistical quality

Claims such as 95% accuracy are about a distribution and estimation procedure:

$$
  \Pr_{x\sim P,\,y\sim h(x)}[\mathrm{Correct}(x,y)]\ge 0.95.
$$

A finite test yields a confidence statement under sampling assumptions, not an unconditional theorem about deployment.

## Selective prediction and abstention

A safe harness can return

$$
  Y+\mathrm{Abstain}
$$

rather than pretending to solve every input. Let coverage be

$$
  \Pr[h(x)\ne\mathrm{Abstain}],
$$

and selective risk be error conditioned on answering. Optimization can trade coverage for risk. A certified branch plus an uncertain model branch can expose uncertainty explicitly.

A dependent output can carry evidence level:

```text
Result =
    Certified(value, proof)
  | Empirical(value, confidence, provenance)
  | Abstain(reason)
```

Downstream clients can require `Certified` for high-risk actions.

## Probabilistic contracts

A probabilistic contract must name:

- input distribution or uncertainty set;
- randomness sources;
- metric or event;
- confidence level;
- sample size and sampling design;
- model and tool versions;
- validity period or drift assumptions.

Without these, "95% accurate" is underspecified.

Formal probabilistic verification is possible for finite-state or analyzable stochastic systems. Frontier LMs are generally treated as black-box stochastic components, so empirical certificates dominate. The wrapper can still be formally verified.

## Resource and capability proofs with Dijkstra-style specs

A computation specification can return both postconditions and resource constraints. Schematically:

$$
  \mathrm{WP}_r(Y)
  = (Y\to\mathrm{Prop})\to X\to\mathrm{Prop}
$$

with an index $r$ or a trace predicate describing permitted effects. Sequential composition derives a combined weakest precondition. A generated term is accepted only when its inferred specification refines the required one.

In practice, one might use F*, Lean with an effect library, Coq, Dafny, Why3, Liquid Haskell, or a custom certified IR. The exact tool matters less than maintaining a small trusted checker.

## Termination and totality

A total function terminates for every input. LM harnesses often include retries and agents that can loop. Enforce termination through:

- structural recursion;
- well-founded measures;
- fuel parameters;
- timeouts represented as typed outcomes;
- bounded tool and model calls.

A timeout is not the same as a proof of termination. It is an operational cutoff. A total wrapper can always terminate by returning `BudgetExceeded`, even if the internal strategy did not solve the task.

## Noninterference and external models

Sending data to a remote model is an observable effect. A noninterference theorem for local code is invalid if the handler transmits secrets. The semantic model must include external calls and their observations.

Generated code should never construct arbitrary prompts from unlabeled context. An information-flow-aware prompt builder can require a proof that every field's label is permitted by the destination policy.

## The specification-gap theorem, informally

No amount of proof can establish an unstated requirement. If contract $C$ omits a harmful behavior $H$, a proof of $C(h)$ does not imply $\neg H(h)$.

This obvious logical fact has practical force. Formal methods shift the failure mode from "implementation violates known rules" toward "rules were incomplete or assumptions false." That is a substantial improvement, but not omniscience.

## Exercises

1. **Concept.** Separate wrapper, model-conditional, and statistical claims for a retrieval assistant.
2. **Proof.** Write a weakest-precondition rule for sequential composition.
3. **Design.** Define a typed result with certified, empirical, and abstaining cases.
4. **Code.** Implement a bounded retry that is total because it returns a typed budget error.
5. **Proof.** Show that conditional correctness of a proof-checking harness does not require trusting the model that generated the proof.
6. **Research.** Estimate selective risk as the abstention threshold varies.
7. **Design.** Write a complete probabilistic-contract statement for an LLM classifier.
8. **Concept.** Explain why a timeout is not a termination proof for the internal strategy.
9. **Proof.** Formalize the specification-gap observation as the non-derivability of $\neg H$ from $C$ without an implication $C\to\neg H$.
10. **Code.** Add information-flow labels to prompt fields and reject disallowed model destinations.
11. **Research.** Investigate a probabilistic proof assistant or model checker on a finite abstraction of a harness.

# Types as Spaces: Identity, Equivalence, and Refactoring

## The homotopy interpretation

Homotopy type theory interprets:

- a type $A$ as a space;
- a term $a:A$ as a point;
- an identity proof $p:a=_A b$ as a path from $a$ to $b$;
- an equality between identity proofs as a path between paths;
- and so on at higher dimensions.

This does not mean every software type is literally a geometric object on a screen. It means identity can carry structured information rather than collapsing to a yes/no relation.

For programs, the metaphor is compelling:

- candidate implementations are points;
- verified refactorings are paths;
- alternative refactoring sequences are paths between the same endpoints;
- coherence proofs compare those paths;
- disconnected components represent implementations with no known equivalence path under the chosen theory.

## Identity is richer than syntactic equality

Two source files can differ while implementing the same function. Syntactic equality is too strict. Finite test agreement is too weak. A semantic identity type can be chosen to express a stronger relation.

Let $\mathrm{Impl}(C)$ be implementations satisfying contract $C$. A path

$$
  p:h=_{\mathrm{Impl}(C)}h'
$$

should encode an accepted notion of sameness. Depending on the construction of $\mathrm{Impl}(C)$, this could mean:

- definitional equality in an IR;
- proof of pointwise equality;
- contextual equivalence;
- bisimulation of effectful traces;
- equality after quotienting by approved rewrite laws.

One must define the type so that its identity matches the intended semantics. HoTT does not automatically turn arbitrary Python refactorings into paths.

## Path operations

Paths have operations:

- reflexivity: $\mathrm{refl}_a:a=a$;
- inverse: if $p:a=b$, then $p^{-1}:b=a$;
- concatenation: if $p:a=b$ and $q:b=c$, then $p\cdot q:a=c$.

Refactoring equivalence behaves similarly. The no-op refactor is reflexivity. An invertible migration has a reverse. Sequential refactors concatenate.

This immediately reveals a limitation: optimization improvement is usually not invertible. A path can model equivalence between versions, but a directed claim that $h'$ is safer or better than $h$ needs additional structure.

## Path induction

The eliminator for identity types, often called path induction or the $J$ rule, says that to prove a property about all equalities, it suffices to prove it for reflexivity in a suitably dependent form.

For software, this underlies **transport**: properties attached to a representation can move along an equality. If $p:A=B$ and $x:A$, then

$$
  \mathrm{transport}(p,x):B.
$$

At the program level, a verified representation equivalence can transport data, invariants, serializers, or proofs.

## Equivalence of types

An equivalence $A\simeq B$ consists, informally, of maps in both directions that are inverse up to homotopy. A common representation is a function with contractible fibers or a quasi-inverse plus coherence.

Examples familiar to programmers include:

$$
  A\times B \simeq B\times A,
$$

$$
  A\times(B\times C)\simeq(A\times B)\times C,
$$

and, under suitable conditions,

$$
  A\times(B+C)\simeq(A\times B)+(A\times C).
$$

These are representation equivalences, not literal syntactic identity. HoTT gives a foundation in which equivalence and identity are tightly related through univalence.

## Program equivalence as a space

Instead of one Boolean relation `equivalent(p, q)`, consider a type

$$
  \mathrm{EquivProof}(p,q).
$$

It may have several inhabitants:

- an algebraic normalization proof;
- a compiler translation-validation proof;
- a bisimulation;
- a chain of trusted refactoring lemmas.

Different proofs can carry different operational meaning. A direct algebraic proof and a long chain through intermediate versions connect the same endpoints but provide different audit paths.

## Approximate paths

Empirical equivalence is not identity. Still, one can define a type of bounded approximations:

$$
  \mathrm{Approx}_{\epsilon,D}(h,h')
$$

whose inhabitants certify that behavior differs by at most $\epsilon$ under metric and dataset assumptions $D$. Such certificates do not generally have exact path algebra. Error bounds may add under composition:

$$
  \epsilon_{h,k}\le \epsilon_{h,h'}+\epsilon_{h',k}.
$$

This resembles enriched-category distance more than identity. The distinction prevents statistical similarity from being promoted to equality.

## Exercises

1. **Concept.** Interpret type, term, identity proof, and higher identity in a versioned software system.
2. **Proof.** Write the types of path reflexivity, inversion, and concatenation.
3. **Design.** Define three different notions of program identity for pure, stateful, and stochastic harnesses.
4. **Concept.** Why does HoTT not make two test-equivalent Python programs identical automatically?
5. **Proof.** Show how pointwise equality plus function extensionality yields equality of pure functions.
6. **Design.** Create a type of refactoring evidence with multiple constructors.
7. **Research.** Formalize a small refactoring, such as map fusion, in a proof assistant and inspect the resulting equality term.
8. **Proof.** Derive a triangle-style bound for composing approximate equivalence certificates.
9. **Concept.** Identify one program change that is an equivalence and one that is a directed refinement but not an equivalence.
10. **Code.** Build a graph whose edges are verified refactorings and compute connected components. Explain what the result does and does not mean semantically.

# Univalence, Transport, and Architecture Families

## The univalence principle

The univalence axiom relates identity of types to equivalence:

$$
  (A=B)\simeq(A\simeq B).
$$

Informally, equivalent types may be treated as identical for purposes of transporting constructions and proofs. This supports representation-independent mathematics.

For programmers, univalence suggests a strong version of "program to an interface." If two representations are equivalent, structures defined uniformly over one can be transported to the other rather than rebuilt ad hoc.

## Representation changes

Suppose an optimizer replaces an intermediate record:

```text
OldFeatures = (normalized_name, normalized_address, distance)
```

with

```text
NewFeatures = {
    distinctive_tokens,
    house_number,
    street_core,
    distance_bucket
}
```

A migration is not automatically an equivalence. Information may be lost. To claim $\mathrm{OldFeatures}\simeq\mathrm{NewFeatures}$, maps in both directions must preserve all relevant structure.

Often the correct relation is a quotient or refinement:

$$
  \mathrm{OldFeatures}\to\mathrm{NewFeatures}
$$

with no inverse. Univalence applies only after establishing equivalence. It should not be used as rhetoric for arbitrary schema changes.

## Transporting contracts

Let $\mathcal{H}:A\to\mathcal{U}$ be a family assigning a harness type to each architecture description $a:A$. A path $p:a=b$ induces transport

$$
  \mathrm{transport}_{\mathcal{H}}(p):
  \mathcal{H}(a)\to\mathcal{H}(b).
$$

If architecture descriptions include representation choices, a verified equivalence can transport:

- data values;
- invariants;
- component contracts;
- tests parameterized over the interface;
- proof obligations;
- serializers and adapters.

Transport is only as useful as the dependent family. If a property was tied to accidental syntax rather than semantic structure, it may not transport cleanly.

## The structure identity principle

In univalent foundations, suitably defined structured objects are equal when they are isomorphic in a structure-preserving way. For software modules, this motivates defining identity by interface-preserving equivalence rather than by memory layout or source spelling.

A module structure might include:

$$
  M=(X,Y,h,C,\pi),
$$

where $h$ is behavior, $C$ a contract, and $\pi$ evidence. An isomorphism must preserve all fields deemed semantically relevant. If cost, trace, or capability use matters, it belongs in the structure. Otherwise two modules may be identified despite operationally significant differences.

## Transport versus regeneration

A model can regenerate downstream code after an upstream representation change. Transport is different: it derives the downstream adaptation from a proved equivalence. Regeneration is heuristic and requires re-verification.

The engineering pattern is:

```text
proved equivalence available -> transport automatically
only heuristic relation known -> regenerate, then re-check
information-losing change     -> explicit migration and new obligations
```

This division can save search budget and reduce proof repair.

## Univalent libraries for optimization

Imagine a library of verified equivalences:

- record field reorderings;
- normalized sum and product representations;
- finite-map implementations under extensional equality;
- parser/printer isomorphisms;
- serialization round trips;
- data-layout transformations.

The LLM proposer can search this library and compose paths. A proof checker verifies the composition. Optimization becomes path search in a structured space rather than unrestricted source generation for representation-level changes.

## Equivalence classes and deployment diversity

Equivalent implementations may differ in performance. If identity retains only extensional output behavior, cost is external. One can define a fiber of implementations over a semantic function:

$$
  \sum_{f:X\to Y}\mathrm{Implementations}(f).
$$

The fiber over $f$ contains alternative algorithms with the same semantics. Optimization searches within the fiber for lower cost. A path in the base preserves semantics; movement in the fiber changes implementation evidence or performance.

This is a useful decomposition:

```text
semantic base: what the program computes
implementation fiber: how it computes it
objective: choose a point in the fiber
```

For stochastic or approximate systems, the base may itself be a behavioral equivalence class rather than an exact function.

## Exercises

1. **Concept.** State univalence informally and explain why it is stronger than "similar types are interchangeable."
2. **Proof.** Give an explicit equivalence between $A\times B$ and $B\times A$.
3. **Design.** For a schema change, decide whether the relation is equality, equivalence, embedding, quotient, or arbitrary migration.
4. **Proof.** Explain how a dependent property transports along a path.
5. **Research.** Use Cubical Agda, Cubical Type Theory, or another HoTT-capable system to transport a simple structure across an equivalence.
6. **Design.** Define what structure a harness isomorphism must preserve in your domain.
7. **Concept.** Contrast transport with LLM-based regeneration.
8. **Code.** Create a library of executable representation isomorphisms with round-trip property tests.
9. **Proof.** Show that composing two equivalences yields an equivalence.
10. **Design.** Separate a semantic base from an implementation fiber for a sorting component. Which objectives live in the fiber?

# Higher Paths, Rewrite Coherence, and Information Loss

## Paths between paths

Suppose two refactoring sequences transform $h$ into $k$:

$$
  p:h=k,
  \qquad
  q:h=k.
$$

A higher path

$$
  \alpha:p=q
$$

states that the two proofs or transformations are themselves coherently related.

In software terms:

```text
h --extract helper--> a --inline constant--> k

h --inline constant--> b --extract helper--> k
```

If the transformations commute, there is a square witnessing coherence. Higher-dimensional structure tracks such interactions.

## Why coherence matters

An optimizer may apply independent rewrites in different orders. Without coherence, the version graph contains duplicated endpoints, conflicting migrations, and proof-repair work. Coherence laws permit normalization of rewrite histories.

Examples:

- reordering two independent pure computations;
- transporting a proof before or after a representation equivalence;
- fusing adjacent maps in either association;
- changing prompt wording and adding deterministic preprocessing when the changes do not interact.

For effectful transformations, order often matters. A higher path should exist only when the relevant commutation law is proved.

## Higher inductive types

Higher inductive types (HITs) allow constructors not only for points but also for paths and higher paths. One can define a semantic architecture space by:

- point constructors for architecture terms;
- path constructors for approved rewrite equations;
- higher constructors for coherence among equations.

For a toy expression language:

```text
point constructors:
    Id
    Compose(f, g)

path constructors:
    left_id(f)  : Compose(Id, f) = f
    right_id(f) : Compose(f, Id) = f
    assoc(f,g,h): Compose(Compose(f,g),h)
                  = Compose(f,Compose(g,h))
```

A HIT can represent syntax modulo these laws without choosing one canonical parenthesization.

In practical tools, e-graphs and quotient types often approximate this role. HITs provide a foundational account with explicit path structure.

## Quotienting syntax by semantics

Raw source space contains enormous redundancy. Alpha-renaming, formatting, dead-code insertion, and equivalent control structures create distinct strings with similar or equal behavior. Quotienting by a semantic relation reduces the effective search space.

But a quotient erases distinctions. If source readability, proof size, cost, or security surface matters, the equivalence relation must retain those dimensions or store them in fibers over the quotient.

The design question is not "should equivalent programs be equal?" It is "equivalent with respect to which observations?"

## Truncation

Homotopy type theory has truncation operations that deliberately forget higher structure. Propositional truncation $\|A\|$ remembers only that $A$ is inhabited, not which witness exists. Set truncation forgets higher paths beyond ordinary equality.

There is a useful analogy to optimizer feedback:

```text
full trace -> structured summary -> scalar score -> pass/fail
```

Each step forgets distinctions. A scalar score is not literally propositional truncation, and the analogy should not be overextended. Both, however, are maps from richer evidence to a coarser observation.

Meta-Harness's reported trace ablation illustrates the engineering cost of premature forgetting: a proposer with raw traces can recover failure-specific structure that scores and summaries have collapsed.

## Sufficient statistics and controlled forgetting

Not every detail should be preserved. A sufficient statistic retains all information relevant to a specified inference problem. If $S(\tau)$ is sufficient for choosing the optimal repair under a model, raw trace retention is unnecessary for that decision.

The difficulty is that the future repair question is not always known. A summary sufficient for today's proposer may be insufficient for tomorrow's analysis. Event sourcing therefore retains raw evidence when privacy and cost permit, while derived summaries accelerate access.

In categorical language, one seeks a quotient with the right universal property: every relevant decision map factors through it.

## Provenance as higher structure

Two candidate artifacts can be extensionally equal but have different provenance paths. One may be hand-written and formally proved; another may be LLM-generated and only regression-tested. For governance, those paths matter.

A deployment type should therefore not quotient away all proof history. It can retain a groupoid or directed graph of derivations even when runtime behavior is identified.

## Exercises

1. **Concept.** Give two refactoring paths with the same endpoints and state whether they should be considered equal.
2. **Proof.** Draw the coherence square for two independent rewrites.
3. **Design.** Define point and path constructors for a small architecture HIT.
4. **Research.** Compare a quotient type, HIT, and e-graph as representations of programs modulo laws.
5. **Concept.** Explain the analogy and difference between trace compression and homotopy truncation.
6. **Proof.** State the factorization property that a sufficient statistic should satisfy for a class of decision functions.
7. **Code.** Build an e-graph for associativity and identity of composition, then extract a low-cost representative.
8. **Design.** Decide which provenance distinctions may be erased at runtime and which must remain for audit.
9. **Proof.** Explain why commutation of rewrites can fail in the presence of state or exceptions.
10. **Research.** Test whether full traces, structured typed feedback, and scalar scores produce different architectural diversity in an optimizer.

# Directed Refinement, Synthetic Infinity-Categories, and Search Geometry

## The invertibility mismatch

Identity paths in HoTT are invertible. If $p:a=b$, then $p^{-1}:b=a$. Optimization steps are usually directed:

$$
  h\preceq h'
$$

may mean fewer capabilities, a stronger contract, or better objective values. The reverse relation need not hold.

Therefore:

- use HoTT for identity, equivalence, transport, and coherent refactoring;
- use preorders, enriched categories, double categories, or directed type theories for refinement and improvement.

Trying to encode every improvement as equality destroys direction. Trying to encode equivalence only as a preorder destroys higher proof structure. Both are needed.

## Directed paths

A directed type theory distinguishes arrows from invertible paths. Synthetic approaches to $(\infty,1)$-categories enrich type theory so that types can carry directed morphisms while higher equivalences remain available.

For program evolution, imagine:

- points: certified candidates;
- directed 1-cells: admissible rewrites or refinements;
- 2-cells: simulations, commuting rewrite squares, or evidence transformations;
- equivalences: invertible refactorings;
- objective labels: empirical measurements on cells or points.

This is closer to the actual version graph than an undirected topological space.

## Search topology versus source distance

A search algorithm needs a notion of neighborhood. In genetic programming, syntax-tree mutation defines local moves. In gradient optimization, norm and derivative define locality. In LLM program evolution, locality is learned and semantic.

Let $d_s$ be source edit distance and $d_b$ behavioral distance. They can disagree:

- renaming every variable: large $d_s$, near-zero $d_b$;
- changing `<=` to `<`: tiny $d_s$, potentially large $d_b$;
- replacing a monolithic model call with a parser-router-model pipeline: large $d_s$, targeted $d_b$ on failing cases.

A useful search geometry combines:

$$
  d(p,q)=
  \lambda_s d_s(p,q)
  +\lambda_b d_b(p,q)
  +\lambda_c d_c(p,q)
  +\lambda_e d_e(p,q),
$$

where $d_c$ is contract/proof disruption and $d_e$ is effect or capability change. The weights are policy, not mathematical facts.

## Semantic neighborhoods

A semantic mutation should preserve a boundary while changing one hypothesis. Examples:

- keep the interface and verifier; alter routing threshold;
- keep architecture; rewrite one prompt;
- keep behavior on certified region; expand the region with a new proof;
- keep output distribution approximately fixed; reduce calls;
- keep capability set; replace an external tool with local code.

Typed optics and rewrite rules define explicit semantic neighborhoods. An LLM can propose within them. Global rewrites remain available but receive stronger re-evaluation.

## Components, barriers, and tunnels

If candidates are grouped by verified equivalence, each component contains implementations connected by safe refactors. Moving between semantic components changes behavior and requires empirical or formal revalidation.

A learned proposer can "tunnel" across source-space barriers by generating a coherent new architecture in one step. This is a major difference from local random mutation. The destination still needs evidence. Proposal competence changes reachability; it does not change validity.

## A fibrational view

A useful picture is a base space of specifications and a fiber of implementations over each specification:

```text
implementation candidates
       |       |       |
       v       v       v
    contract C0 -> contract C1 -> contract C2
```

Vertical movement within a fiber optimizes implementation while preserving contract. Movement in the base changes the contract. A fibration formalizes how implementations and proofs reindex when specifications change.

This helps separate two operations that code agents often blur:

- **implementation evolution:** search inside $\mathrm{Impl}(C)$;
- **requirement evolution:** move from $C$ to $C'$ and transport or rebuild implementations.

Requirement evolution needs governance and user intent, not only metric optimization.

## The directed unified picture

The complete mathematical object is not one ordinary category. It is a layered structure:

1. a category or operad of typed architectures;
2. a Kleisli or Markov category of effectful executions;
3. a graded enrichment for resources and capabilities;
4. a double or higher category of versions and evidence-bearing rewrites;
5. dependent fibers of implementations over contracts;
6. HoTT identity structure for equivalence and transport;
7. directed refinement structure for improvement;
8. a stochastic coalgebra for the search process.

This may seem elaborate. Each layer answers a different engineering question. Omitting a layer does not simplify reality; it usually hides a distinction.

## Exercises

1. **Concept.** Give three directed refinements that are not equivalences.
2. **Proof.** Show that mutual refinement induces an equivalence relation when the refinement relation is a preorder.
3. **Code.** Compute source and behavioral distances for several program pairs and compare rankings.
4. **Design.** Define a semantic neighborhood for safe prompt-and-router optimization.
5. **Concept.** Explain "tunneling" through source-space barriers without implying that verification is unnecessary.
6. **Research.** Embed candidate behaviors into a vector space and visualize whether LLM proposals move more semantically locally than random edits.
7. **Design.** Separate contract-fiber optimization from contract changes in an optimizer API.
8. **Proof.** State the reindexing operation needed when a contract is strengthened.
9. **Concept.** Which parts of the unified picture can be implemented today without a HoTT proof assistant?
10. **Research.** Study directed type theory or synthetic infinity-categories and propose a formalization of one version-control workflow.

# A Reference Architecture for Reflective Program Evolution

## Design goals

A production architecture should permit aggressive proposal while keeping acceptance conservative. It should support reproducibility, explicit contracts, multiple evidence kinds, resource-aware selection, and immutable deployment artifacts.

The core rule is:

> The proposer may be creative and unreliable. Every boundary that grants capability, certifies a property, or promotes a candidate must be narrow, typed, and independently checked.

## System diagram

```text
                         +-----------------------+
                         |  Contract Registry    |
                         | schemas, policies,    |
                         | proofs, objectives    |
                         +-----------+-----------+
                                     |
                                     v
+------------+   evidence   +--------+---------+    proposal   +-------------+
| Evaluation |------------->| Search Controller|------------->| LLM Proposer|
| Workers    |              +--------+---------+              +------+------+ 
+-----+------+                       |                               |
      ^                              | candidate source/IR           |
      |                              v                               |
      |                    +---------+----------+                    |
      |                    | Build and Verify   |<-------------------+
      |                    | parser, typecheck, |
      |                    | proofs, policies   |
      |                    +---------+----------+
      |                              |
      | certified candidate          v
      +----------------------+-------+----------+
                             | Sandbox Runtime  |
                             | effect handlers, |
                             | tracing, limits  |
                             +-------+----------+
                                     |
                                     v
                         +-----------+-----------+
                         | Artifact and History  |
                         | content-addressed log |
                         +-----------+-----------+
                                     |
                                     v
                         +-----------+-----------+
                         | Promotion Gate        |
                         | hidden eval, review,  |
                         | signed release        |
                         +-----------------------+
```

## Contract registry

The contract registry stores versioned definitions of:

- input and output schemas;
- allowed architecture primitives;
- effect and capability policies;
- resource limits;
- formal preconditions, postconditions, and invariants;
- statistical objectives and confidence requirements;
- judge prompts, rubrics, and calibration versions;
- promotion rules;
- data-governance and privacy policies.

Contracts are content-addressed. A candidate points to an immutable contract hash. A proposal that changes the contract produces a separate artifact and cannot masquerade as an implementation improvement.

## Proposal interface

The proposer receives a controlled view:

```python
@dataclass(frozen=True)
class ProposalRequest:
    contract: ContractView
    parent_ir: str
    parent_metrics: ScoreVector
    selected_traces: tuple[RedactedTrace, ...]
    counterexamples: tuple[Counterexample, ...]
    prior_attempts: tuple[AttemptSummary, ...]
    allowed_primitives: tuple[PrimitiveDoc, ...]
    objective_policy: ObjectivePolicy
```

The response is structured:

```python
@dataclass(frozen=True)
class Proposal:
    candidate_ir: str
    claimed_transformations: tuple[str, ...]
    expected_effects: ScoreVector | None
    proof_hints: tuple[str, ...]
    assumptions: tuple[str, ...]
```

Claims are hypotheses. They are never copied into certificates without checking.

## Build and verification boundary

The builder performs, in order:

1. parse into a typed IR;
2. reject unknown primitives;
3. infer types, effects, capabilities, and resource expressions;
4. compare inferred properties with the contract;
5. generate proof obligations;
6. invoke proof checkers, SMT solvers, or model checkers;
7. lower to executable code;
8. translation-validate or test the lowering;
9. package the artifact with evidence hashes.

The output type is explicit:

```text
BuildResult =
    Rejected(BuildError, diagnostics)
  | Certified(Candidate, EvidenceBundle)
```

No exception path should bypass this sum and insert an uncertified candidate into the archive.

## Sandbox and effect handlers

The runtime executes generated code in isolation. It supplies only typed operations. Every effect crosses a host-controlled handler that:

- validates arguments;
- enforces capability and data-label policies;
- applies quotas and timeouts;
- records a trace event;
- attaches model/tool version metadata;
- returns a typed result.

A sandbox limits consequences of a mistake. It does not justify trusting output. Use both sandboxing and verification.

## Evaluation workers

Evaluation workers should be hermetic where possible. An evaluation record includes:

```text
candidate hash
contract hash
dataset and split hash
model snapshot or provider version
sampling parameters and seeds
tool/runtime/container versions
judge version and randomized presentation
raw and redacted trace hashes
scores with uncertainty
verifier and test reports
start/end timestamps and resource measurements
```

External APIs can prevent exact replay. Record sufficient evidence to distinguish code changes from service drift.

## Search controller

The controller is the coalgebraic outer loop. It manages:

- budget accounting;
- parent selection;
- evidence retrieval;
- proposal scheduling;
- candidate deduplication;
- staged evaluation;
- archive updates;
- stopping criteria;
- periodic reevaluation of incumbents;
- quarantine of suspicious improvements.

The controller should be deterministic given recorded randomness and external responses. Its own source and configuration are versioned.

## Artifact store and provenance graph

Use content-addressed immutable artifacts. Store source/IR, compiled executable, evidence, traces, prompts, model identifiers, and data hashes. The provenance graph records:

```text
parent candidates
    -> proposal request
    -> proposal response
    -> build evidence
    -> evaluation runs
    -> archive decisions
    -> promotion decision
```

Never overwrite "the optimized program." Publish a new version and a signed pointer.

## Promotion gate

Search metrics are training signals. Promotion uses stronger evidence:

1. re-run hard checks in a clean environment;
2. evaluate on a hidden test set inaccessible to the proposer and search controller;
3. run distribution-shift and adversarial suites;
4. verify resource limits under production-like load;
5. inspect trace and judge anomalies;
6. require human approval for policy-sensitive changes;
7. sign the candidate and evidence manifest.

Production does not rewrite itself in place. New candidates deploy through canary, shadow, or staged rollout with rollback.

## Threat model

Threats include:

- accidental invalid code;
- prompt injection through traces or task data;
- generated code attempting unauthorized effects;
- metric exploitation;
- judge manipulation;
- secret leakage into prompts;
- dependency or model drift;
- poisoned historical evidence;
- archive corruption;
- contract weakening;
- human-review fatigue.

Map each threat to a boundary. "The model is capable" is not a mitigation.

## Exercises

1. **Design.** Adapt the reference architecture to a code-review assistant.
2. **Code.** Define immutable Python data classes for proposal, build, evaluation, and promotion records.
3. **Proof.** Show how a sum-typed build result prevents a rejected artifact from being consumed by a function requiring `Certified`, assuming no unsafe cast.
4. **Design.** Write a capability policy for an optimizer that may query documentation but may not modify repositories.
5. **Research.** Measure replay divergence caused by model-provider drift over one month.
6. **Concept.** Explain why the contract registry and promotion gate must not be ordinary optimizer parameters.
7. **Code.** Build a content-addressed artifact store using SHA-256 and an append-only manifest.
8. **Design.** Create a redaction policy that preserves useful trace structure while removing secrets.
9. **Proof.** State the invariant maintained by staged evaluation: every archive member has passed hard checks under its cited contract.
10. **Threat modeling.** Construct an attack tree for a candidate that tries to manipulate its LLM judge.

# LLM Judges, Measurement, and Goodhart's Law

## A judge is a measuring instrument

An LLM judge maps an evaluation context and candidate output to a score, label, preference, or critique:

$$
  J:R\times X\times Y\to\mathcal{D}(S\times F),
$$

where $R$ is a rubric, $S$ a score, and $F$ feedback. Treat it as a stochastic measuring instrument, not an oracle.

The measurement has construct validity only if it tracks the quality users care about. It has reliability only if repeated or equivalent presentations produce sufficiently stable outputs. It has calibration only if reported probabilities or score bands correspond to observed outcomes.

## Known biases

Research on LLM-as-a-judge has documented several recurring biases:

- **position bias:** preference changes when answer order changes;
- **verbosity bias:** longer answers can be favored independent of correctness;
- **self-enhancement or family bias:** a model may favor outputs resembling its own style;
- **style bias:** formatting and confidence can dominate substance;
- **limited reasoning:** the judge may fail on tasks it cannot solve;
- **reference anchoring:** an imperfect reference answer can distort evaluation;
- **inconsistency:** repeated judgments may disagree.

These findings do not make LLM judges useless. They define the controls needed for responsible use.

## Absolute scoring versus pairwise preference

Absolute scoring asks for a number or rubric category. Pairwise judging asks which of two outputs is better. Pairwise tasks are often easier, but introduce ordering effects and do not directly produce a cardinal scale.

A robust pairwise protocol:

1. blind candidate identities;
2. randomize order;
3. judge both orders for a subset or all pairs;
4. request a criterion-by-criterion decision before overall preference;
5. permit ties;
6. aggregate with a model such as Bradley-Terry, while checking fit;
7. calibrate against human judgments.

Do not use the same model's free-form rationale as independent evidence for its score. Both come from one stochastic process.

## Rubric decomposition

A rubric should separate dimensions:

```text
factual correctness
instruction compliance
completeness
relevance
clarity
safety or policy compliance
citation support
```

For each dimension, specify observable criteria and an abstention option. Some dimensions should be replaced by deterministic tools. Citation validity can be checked by retrieval and entailment procedures; schema validity by a parser; code correctness by tests and proofs.

The judge should receive only the information needed. Revealing candidate source, model identity, cost, or previous score can introduce unwanted bias unless those are explicit criteria.

## Judge calibration

Collect a human-labeled calibration set representative of deployment. Estimate:

- agreement by criterion;
- confusion matrices;
- order sensitivity;
- test-retest reliability;
- subgroup performance;
- sensitivity to verbosity and style controls;
- confidence calibration;
- failure modes on adversarial examples.

Calibration is version-specific. A model or prompt update creates a new judge instrument and requires reevaluation.

## Ensembles and correlated error

Multiple judges reduce variance only when errors are not perfectly correlated. Three prompts to the same model may offer less diversity than one model, one deterministic checker, and one human review channel.

An ensemble can aggregate:

$$
  J_1,J_2,\ldots,J_m.
$$

But majority vote can amplify shared bias. Track disagreement. High disagreement is evidence for uncertainty and can trigger escalation rather than forced consensus.

## Goodhart's law

When a measure becomes a target, it can cease to be a good measure. A useful taxonomy distinguishes:

- **regressional Goodhart:** extreme proxy values contain more noise;
- **extremal Goodhart:** optimization enters a regime where the prior proxy-quality relationship changes;
- **causal Goodhart:** intervening on the proxy breaks its relationship to the goal;
- **adversarial Goodhart:** an agent exploits the proxy.

Reflective program evolution is exposed to all four. Searching many candidates selects positive noise. Architectural changes move outside the judge's calibration distribution. A candidate can optimize surface features rather than substance. Generated content can include instructions that affect the judge.

## Judge isolation

Candidate-controlled content must be treated as data. Defenses include:

- delimit and quote candidate output;
- use a judge prompt that explicitly ignores embedded instructions;
- parse outputs into structured fields before judging;
- strip irrelevant metadata and hidden text;
- use independent deterministic checks for injection markers;
- render content through a safe canonical form;
- keep judge tools and secrets unavailable;
- test with adversarial candidate outputs.

No prompt provides a formal isolation boundary. Use process and capability isolation as well.

## Hidden objectives and rotating probes

A search process repeatedly exposed to the same judge can overfit. Keep some criteria hidden, rotate adversarial probes, and use meta-held-out evaluations. The hidden set must remain inaccessible through traces, logs, or proposal context.

A candidate that improves only on the exposed judge but not humans or hidden checks should be classified as judge overfitting, not progress.

## Proof outranks preference on formal claims

If a proposition is decidable, use a checker. An LLM judge can prioritize proof attempts, explain counterexamples, or assess readability. It should not override a failed proof or test.

Evidence precedence can be encoded:

```text
formal contradiction     -> reject
hard policy violation    -> reject
schema/type failure      -> reject
statistical uncertainty  -> quantify/escalate
judge disagreement       -> escalate or retain both
preference difference    -> optimize only among admissible candidates
```

## Exercises

1. **Design.** Write a decomposed judge rubric for technical explanations.
2. **Code.** Implement randomized pairwise judging with order reversal and disagreement tracking using a deterministic mock judge.
3. **Proof.** Show how selecting the maximum of many noisy unbiased estimates produces an upward-biased estimate of the winner's true score.
4. **Research.** Measure position and verbosity bias for two judge models on a human-labeled set.
5. **Concept.** Classify four optimizer failure examples by Goodhart type.
6. **Design.** Build an evidence-precedence lattice for a coding-agent benchmark.
7. **Code.** Detect and quarantine candidate outputs containing judge-directed instructions.
8. **Research.** Compare same-model prompt ensembles with cross-model and tool-plus-model ensembles.
9. **Proof.** Explain why correlated judge errors limit the benefit of majority voting.
10. **Design.** Specify a versioned judge-calibration report sufficient for an audit.
11. **Concept.** State one task where an LLM judge is appropriate and one where a formal checker should replace it.

# Experimental Design for Self-Optimizing Systems

## The metric is part of training

Once an optimizer repeatedly queries a metric, the evaluation set becomes training data. Calling it a validation set does not preserve independence. A rigorous experiment distinguishes:

```text
proposal/feedback set
    used to generate critiques and counterexamples
selection set
    used to compare and retain candidates
development test set
    used sparingly by researchers
final hidden test set
    used once for reported selection
meta-held-out set
    different tasks, domains, models, or time periods
live shadow set
    production-like monitoring without user impact
```

The exact split depends on data volume, but independence must be designed, not assumed.

## Nested selection

If hyperparameters, prompts, archive policies, and stopping rules are tuned, the final test must sit outside all of them. A nested protocol is:

1. inner search optimizes candidate programs;
2. middle validation selects optimizer settings;
3. outer test estimates the complete procedure.

Reporting only the best run from many optimizer configurations without correction estimates luck as skill.

## Multiple comparisons and winner's curse

Suppose $N$ candidates have true quality $q_i$ and noisy estimates

$$
  \hat q_i=q_i+\epsilon_i.
$$

Selecting $i^*=\arg\max_i\hat q_i$ favors candidates with positive noise. The more candidates evaluated, the larger the expected optimism.

Mitigations include:

- independent reevaluation of finalists;
- confidence bounds;
- sequential racing with correction;
- bootstrap selection stability;
- preregistered budgets and stopping rules;
- reporting all runs, not only the maximum;
- final hidden evaluation.

## Paired evaluation

When two candidates are tested on the same inputs and random seeds, compare paired differences:

$$
  d_i=\mu(h',x_i)-\mu(h,x_i).
$$

Pairing removes variation shared across examples. For stochastic LMs, common random numbers are not always available across different prompts or providers, but identical sampling seeds and repeated trials can still reduce variance when supported.

Report effect size and uncertainty, not only a p-value.

## Staged evaluation and racing

Evaluation is expensive. Use stages:

```text
Stage 0: parse, type, policy, proof checks
Stage 1: tiny diagnostic batch
Stage 2: larger selection batch
Stage 3: full validation with repeated samples
Stage 4: hidden final test
Stage 5: shadow or canary deployment
```

Early elimination saves budget but can discard candidates with high variance or niche strengths. Preserve a small exploration quota and occasionally re-evaluate borderline candidates.

## Distribution shift

The optimized harness learns properties of data, tools, model behavior, and evaluator. Test shifts in:

- input domain and language;
- class balance and prevalence;
- time;
- upstream data formatting;
- model version;
- tool errors and latency;
- adversarial behavior;
- cost regime;
- policy constraints.

For a routed system, monitor each branch separately. A small change in input distribution can move many cases across a threshold and sharply change error and cost.

## Ablation and causal understanding

A complex generated harness can score well for the wrong reason. Ablate:

- deterministic preprocessing;
- router;
- each predictor;
- memory and retrieval;
- textual feedback;
- full history versus summaries;
- Pareto archive versus best-only selection;
- judge versus deterministic evaluator;
- code optimization versus prompt-only optimization.

Ablation does not prove causality under all interactions, but it reveals whether claimed components are necessary in the measured setting.

## Cost and latency accounting

Record:

- input, output, and cached tokens;
- number and type of model calls;
- tool calls;
- wall-clock and CPU time;
- concurrency and batching;
- cold versus warm caches;
- retries and failures;
- price schedule and date;
- infrastructure overhead.

A claim such as "\$0.70 per thousand records" is tied to a model, provider, price, and runtime date. Preserve raw token and call counts so later readers can recompute cost.

## Reproducibility manifest

A result should include:

```yaml
candidate_hash: ...
contract_hash: ...
optimizer_commit: ...
optimizer_config_hash: ...
proposer_model: ...
execution_model: ...
judge_model: ...
dataset_hashes: ...
split_definition: ...
container_digest: ...
random_seeds: ...
tool_versions: ...
price_snapshot: ...
search_budget: ...
number_of_candidates: ...
selection_rule: ...
```

Without the number of attempted candidates and selection rule, the reported winner cannot be interpreted statistically.

## Exercises

1. **Design.** Create a five-level split protocol for a small dataset with only 1,000 examples.
2. **Proof.** For two independent normal noise estimates, compute why selecting the larger estimate creates optimism even when true qualities are equal.
3. **Code.** Implement paired bootstrap confidence intervals for candidate score differences.
4. **Research.** Compare best-of-N performance before and after independent finalist reevaluation.
5. **Design.** Define staged evaluation thresholds that account for score uncertainty.
6. **Concept.** Explain why a repeatedly queried validation set is effectively training data.
7. **Code.** Generate a complete reproducibility manifest and verify hashes before replay.
8. **Research.** Stress-test a router under shifts in class prevalence and input formatting.
9. **Design.** Plan ablations for an optimized agent with retrieval, memory, verifier, and fallback.
10. **Concept.** Distinguish price, raw resource use, and infrastructure cost.
11. **Proof.** Show why the variance of paired differences can be lower than the variance of two independent sample means when outcomes are positively correlated.

# Case Study: Location Conflation as Learned Partial Evaluation

## Reported setup

The motivating Flex article studies whether two place listings denote the same physical place. The reported experiment used 1,029 labeled pairs and a class-balanced held-out set of 240 records. Caches were disabled. A small execution model handled inference, while a stronger reflection model proposed code and instruction changes.

The article reports the following held-out results. Prices and latency are tied to the stated models and the August 2026 measurement environment.

| Program | Call penalty $\lambda$ | Accuracy | LM calls / record | Reported cost / 1k | Mean latency |
|---|---:|---:|---:|---:|---:|
| `Predict` baseline | n/a | 90.4% | 1.00 | \$0.98 | 1,924 ms |
| GEPA, prompt only | n/a | 92.5% | 1.00 | \$2.88 | 2,841 ms |
| Flex + GEPA | 0 | 95.0% | 0.25 | \$0.70 | 1,155 ms |
| Flex + GEPA | 0.05 | 94.6% | 0.17 | \$0.45 | 726 ms |
| Flex + GEPA | 0.10 | 90.8% | 0.07 | \$0.18 | 347 ms |
| Flex + GEPA | 0.20 | 91.7% | 0.08 | \$0.09 | 135 ms |
| Flex + GEPA | 0.40 | 92.1% | 0.004 | \$0.01 | 65 ms |

The article states that latency was measured under eight-way concurrency, that the $\lambda=0$ candidate routed about 75% of records through deterministic code, and that the $\lambda=0.4$ candidate invoked the model once in 240 held-out records. These figures are evidence about one experiment, not a theorem about Flex or entity resolution.

## The discovered architecture

The reported generated program can be abstracted as:

$$
  X\xrightarrow{n}N
  \xrightarrow{f}F
  \xrightarrow{r}D+A
  \xrightarrow{[d,\ell]}Y.
$$

Here:

- $X$ contains raw listing pairs;
- $N$ contains normalized names and addresses;
- $F$ contains comparison features;
- $r$ returns either a deterministic decision $D$ or an ambiguous case $A$;
- $d:D\to Y$ extracts the settled Boolean;
- $\ell:A\to T(Y)$ calls the model with focused evidence.

This is learned partial evaluation. The optimizer specializes the general model-backed computation to cases that can be decided from cheap features.

## Category-theoretic reading

### Factorization

The original one-call predictor is replaced by a factorization through explicit intermediate objects. This makes architecture visible and permits local tests.

### Coproduct routing

The result of $r$ is a sum type. The two branches share output type $Y$, so copairing $[d,\ell]$ combines them.

### Embedding pure computation

The deterministic branch enters the effectful category through $J(d)$. The full harness is:

$$
  h=[J(d),\ell]\circ r\circ f\circ n.
$$

### Resource grading

If the model branch has grade $c$ and is selected with probability $q$, the worst-case grade remains $c$ while expected grade is approximately $qc$. The $\lambda$ term changes the objective over this grade.

### Search as architecture rewrite

The move from one predictor to normalization, feature computation, router, and fallback is a vertical rewrite with empirical evidence. It is not an equivalence: behavior changed and reportedly improved on the held-out set.

## Dependent-type reading

A typed intermediate record might be:

```text
Features = {
    distinctive_name_a : Tokens,
    distinctive_name_b : Tokens,
    house_a             : Option HouseNumber,
    house_b             : Option HouseNumber,
    street_a            : StreetCore,
    street_b            : StreetCore,
    name_similarity     : UnitInterval,
    distance_meters     : Option NonnegativeFloat
}
```

The types encode bounds and missingness. A router should return evidence:

```text
RouteResult =
    Same(proof_or_reason)
  | Different(proof_or_reason)
  | Ambiguous(features)
```

In the reported system, deterministic rules are learned from data and are not formally proved domain-correct. Their "reason" is diagnostic, not a theorem. A stronger design would separate:

- **certified rules**, such as exact canonical-identifier equality;
- **empirical rules**, such as fuzzy-name thresholds;
- **ambiguous cases**, delegated to the model.

The output can expose the evidence level.

## HoTT reading

Several normalization implementations may be equivalent under a defined canonical-name semantics. Verified refactorings among them form paths. Representation changes between feature records can transport downstream functions only when an equivalence is proved.

The optimizer's threshold changes are directed, not equivalence paths. They move to a different decision function. Their evidence is statistical. HoTT organizes equivalence inside a semantic component; the Pareto/refinement structure organizes movement among behaviorally distinct components.

## The objective as a Lagrangian-like scalarization

The article describes a per-example score resembling

$$
  \max(0,\;\mathrm{correct}-\lambda\,n_{\mathrm{calls}}).
$$

This is a scalarization of correctness and call count. Sweeping $\lambda$ samples a tradeoff curve. It is related to a Lagrangian relaxation, but finite data, clipping, and discrete architectures mean standard convex duality guarantees do not apply.

A more explicit multi-objective formulation retains

$$
  (\mathrm{accuracy},-\mathrm{calls},-\mathrm{latency},-\mathrm{cost})
$$

and chooses a deployment point after search. The scalar penalty remains useful for steering proposals toward deterministic solutions.

## Failure analysis

Potential failure regions include:

- generic-word removal deletes a truly distinctive token;
- franchise-number stripping merges separate locations;
- street-type removal confuses different roads;
- geocoding distance is missing or wrong;
- thresholds encode class balance or geography of the sample;
- same-brand branch logic fails in dense venues;
- the model fallback sees too few hard examples to calibrate;
- the router becomes overconfident under language or country shift.

Each transformation needs targeted tests. Router false positives and false negatives should be measured separately from fallback errors.

## A stronger contract

A production contract could require:

```text
Interface:
  ListingPair -> DecisionWithEvidence

Hard:
  output schema valid
  no network except approved geocoder/model effects
  at most one model call
  deterministic branch emits a rule identifier
  missing data handled explicitly

Statistical:
  false-merge rate <= threshold on high-risk segments
  calibrated abstention or fallback probability
  no subgroup regression beyond tolerance

Operational:
  p95 latency and cost bounds
  trace fields redacted
  every deployed threshold linked to evaluation evidence
```

False merges may be more costly than false splits, so raw accuracy can be the wrong objective. Use domain-weighted loss and per-segment constraints.

## Reproduction protocol

A careful reproduction would:

1. preserve a final hidden set unavailable during GEPA search;
2. report the number of candidate programs evaluated;
3. rerun finalists with repeated model samples;
4. compare paired errors with McNemar or exact tests where appropriate;
5. bootstrap cost and latency uncertainty;
6. test temporal and geographic shifts;
7. ablate normalization, features, routing, and fallback;
8. manually inspect deterministic-rule errors;
9. report raw token and call counts, not only price;
10. release source, splits, hashes, and runtime manifest where permitted.

## Lessons

The case study supports a general hypothesis: when many inputs admit cheap algorithmic treatment, architecture search can outperform prompt-only search by moving computation across the code-model boundary. It does not establish that a model will reliably discover safe rules, that the rules generalize, or that call minimization should be scalarized in one particular way.

The mathematically correct description is:

> A learned proposal kernel searched factorizations and coproduct routes in an effectful program space. Empirical selection found candidates on a quality-resource frontier. Hard sandbox and interface checks constrained execution, while semantic correctness remained primarily statistical.

## Exercises

1. **Proof.** Derive the type of the combined router harness using coproduct elimination.
2. **Code.** Implement `RouteResult` as a tagged union and prohibit `None` as an implicit ambiguous state.
3. **Design.** Define a loss function where false merges cost ten times false splits.
4. **Research.** Test threshold stability across geographic regions or synthetic shifts.
5. **Proof.** Distinguish worst-case and expected model-call grades for the router.
6. **Code.** Build a certified fast path for exact canonical identifier equality and an empirical path for fuzzy matching.
7. **Design.** Specify an evidence level that downstream systems can use to decide whether human review is required.
8. **Research.** Compare a scalar call penalty sweep with direct Pareto archive search.
9. **Concept.** Identify which transformations in the generated code might be equivalences and which change semantics.
10. **Proof.** Explain why clipping the scalar score prevents a straightforward interpretation as unconstrained linear scalarization.
11. **Design.** Construct a hidden-test and meta-held-out protocol for a dataset of only 1,269 total examples.

# Case Study: Coding-Agent Harnesses and Persistent Trace Memory

## The harness is a program around the model

A coding model rarely operates alone. Its harness decides:

- which repository files to inspect;
- how to search symbols and history;
- how to plan and revise;
- when to run tests;
- how to interpret failures;
- whether to use patches or rewrite files;
- when to stop;
- what final artifact to submit.

Two systems using the same model can differ sharply because of this surrounding program.

The Flex article reports a small pilot on 12 sampled SWE-bench Pro issues: a baseline using the stated small model solved none, while an optimized Flex harness solved four after 60 metric calls. The article explicitly labels this a pilot. The sample is too small for broad performance claims, but the architectural transformation is illustrative.

Meta-Harness studies outer-loop optimization of harness code more systematically. Its proposer can inspect source, scores, and raw traces for all prior candidates through a filesystem. The paper reports gains on online text classification, retrieval-augmented mathematical reasoning, and TerminalBench-2, and an ablation in which full trace access substantially outperformed scores-only and scores-plus-summary interfaces.

## A coding harness as a coalgebra

Let state contain repository view, working tree, test results, plan, budget, and history:

$$
  S=R\times W\times T\times P\times B\times H.
$$

One agent step is

$$
  a:S\to\mathcal{D}(O\times S),
$$

where observations include tool results, model messages, patches, and test outputs. The complete harness traces this transition until success or a stopping condition.

The outer optimizer is another coalgebra whose candidates are inner coalgebras. This nesting explains the term *meta-harness*:

$$
  \text{outer state}
  \longrightarrow
  \text{distribution over revised inner transition systems}.
$$

## Architecture grammar for coding agents

A safe grammar can expose:

```text
Inspect(query, scope)
RetrieveDocs(query)
Plan(strategy)
Edit(patch)
RunCheck(check_id)
AnalyzeFailure(trace_slice)
Repair(policy)
Checkpoint
Rollback
Submit
BoundedLoop(max_steps, body)
Route(predicate, branch_a, branch_b)
```

The candidate cannot invoke arbitrary shell commands. Tool effects are typed and allowlisted. File-write effects are scoped to a workspace. Network access is separate. The submit operation requires a clean evidence bundle.

An LLM can still write patch content, but the harness architecture and capabilities remain analyzable.

## Why raw traces can matter

A scalar score such as `tests_passed = 17/20` does not reveal:

- which tests failed;
- whether compilation failed before tests;
- whether the agent edited the wrong file;
- whether a tool output contradicted the plan;
- whether the same unsuccessful approach was repeated;
- whether context selection omitted a defining symbol;
- whether the candidate reached the correct patch and then reverted it.

A summary can preserve some facts, but the proposer cannot query details that were omitted. Persistent raw traces permit new causal hypotheses and retrieval strategies.

The cost is scale. Trace stores need indexing, redaction, retention policy, and contamination controls. A poisoned or prompt-injected trace can influence future proposals. Treat history as untrusted data.

## Category-theoretic decomposition

A coding workflow can be factored:

$$
  \mathrm{Issue}
  \xrightarrow{\mathrm{localize}}
  \mathrm{Context}
  \xrightarrow{\mathrm{propose}}
  \mathrm{Patch}
  \xrightarrow{\mathrm{validate}}
  \mathrm{Result}.
$$

Generated harnesses may insert feedback loops from validation to localization or proposal. A traced monoidal diagram represents these loops. Effect handlers account for repository reads, writes, test execution, and model calls.

Local improvements do not necessarily compose. A localization stage that returns less context may be faster but starve the patch generator. The objective is system-level.

## Dependent proof obligations

A candidate patch artifact can have type:

$$
\begin{aligned}
  \sum_{p:\mathrm{Patch}}\;&\mathrm{AppliesCleanly}(p) \\
  &\times \mathrm{Builds}(p) \\
  &\times \mathrm{PassesRequiredTests}(p) \\
  &\times \mathrm{TouchesAllowedPaths}(p) \\
  &\times \mathrm{NoNewPolicyViolation}(p).
\end{aligned}
$$

Tests do not prove the issue is solved for all inputs, but they are concrete evidence. Static analyzers, type checkers, and proof tools can strengthen the package.

The harness itself can be certified for capability bounds:

$$
  \mathrm{HarnessCaps}(h)\subseteq
  \{\mathrm{ReadWorkspace},\mathrm{WriteWorkspace},\mathrm{RunApprovedChecks}\}.
$$

## HoTT and version-control paths

A repository history already resembles a directed graph of versions. Verified refactors provide equivalence paths; feature patches are directed semantic changes; merges are squares or higher cells that reconcile paths.

Two patch sequences may reach textually different but behaviorally equivalent states. A semantic merge should preserve proof and test evidence where possible. Ordinary line-based merge ignores this higher structure.

A future proof-aware version-control system could store:

- source diffs;
- typed AST transformations;
- contract changes;
- proof transport;
- test and trace evidence;
- higher coherence between commuting edits.

## Judge risks in coding benchmarks

Coding benchmarks often have deterministic test suites, which is better than a pure LLM judge. Risks remain:

- tests can be incomplete;
- candidates can overfit visible tests;
- flaky tests create noise;
- benchmark environments can differ from production;
- harnesses can exploit infrastructure quirks;
- an LLM may judge patch quality or issue resolution beyond tests.

Keep hidden tests and environment integrity outside candidate capabilities. Log every command and file access. Reject unexpected network or process behavior.

## A proposed optimization protocol

```text
1. Seed with a minimal typed coding harness.
2. Run on feedback tasks and retain full, redacted traces.
3. Convert deterministic failures into tagged counterexamples.
4. Let the proposer revise only the typed architecture or prompts.
5. Hard-check capabilities and loop bounds.
6. Evaluate on a selection task set with isolated containers.
7. Maintain a Pareto archive over solve rate, calls, tokens, time,
   failure recovery, and proof/test coverage.
8. Re-evaluate finalists on hidden repositories and held-out models.
9. Inspect trace novelty and suspicious shortcuts.
10. Promote an immutable harness version, not a live self-modifier.
```

## Exercises

1. **Design.** Encode a coding-agent harness in the architecture grammar above.
2. **Proof.** Derive a worst-case command and model-call bound for a bounded repair loop.
3. **Code.** Build a trace index that retrieves prior failures by test name, file path, and error type.
4. **Research.** Compare raw-trace retrieval with summaries on a small program-repair benchmark.
5. **Design.** Define a proof-carrying patch artifact for a statically typed repository.
6. **Concept.** Explain the nested-coalgebra view of Meta-Harness.
7. **Threat modeling.** Design a trace-poisoning attack and a defense.
8. **Proof.** State conditions under which two independent patches commute.
9. **Research.** Evaluate whether a harness optimized for one execution model transfers to held-out models.
10. **Design.** Define a suspicious-improvement detector for a coding benchmark.
11. **Concept.** Why is four successes out of twelve a useful pilot observation but not a reliable general benchmark estimate?

# A Minimal Executable Framework

## Purpose

This chapter presents a small, dependency-free Python framework. It does not call an LLM. Instead, it supplies the interfaces into which an LLM proposer or judge can be inserted. A deterministic semantic proposer makes the example reproducible.

The example evolves a routing policy for a synthetic entity-resolution task. Candidate source is JSON for a typed policy, not arbitrary Python. The builder checks invariants. Evaluation returns accuracy, call rate, and trace evidence. A Pareto archive preserves tradeoffs.

An extended, executable version of these core listings is included as a companion artifact to this book.

## Core data types

```python
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Iterable, Protocol, Sequence
import hashlib
import json
import math
import random


@dataclass(frozen=True)
class Example:
    name_similarity: float
    address_match: bool
    distance_m: float | None
    label: bool


@dataclass(frozen=True)
class Policy:
    sure_match: float
    sure_miss: float
    address_rescue: float
    near_m: float
    far_m: float


@dataclass(frozen=True)
class TraceEvent:
    kind: str
    detail: str


@dataclass(frozen=True)
class RunResult:
    prediction: bool
    model_calls: int
    events: tuple[TraceEvent, ...]


@dataclass(frozen=True)
class Score:
    accuracy: float
    negative_call_rate: float
    negative_complexity: float


@dataclass(frozen=True)
class Candidate:
    source: str
    policy: Policy
    digest: str


@dataclass(frozen=True)
class Evaluation:
    score: Score
    failures: tuple[tuple[Example, RunResult], ...]
```

## Build boundary

```python
def build_candidate(source: str) -> Candidate:
    """Parse and validate the policy DSL. Raises ValueError on rejection."""
    raw = json.loads(source)
    expected = {
        "sure_match", "sure_miss", "address_rescue", "near_m", "far_m"
    }
    if set(raw) != expected:
        raise ValueError(f"expected fields {sorted(expected)}")

    policy = Policy(**{k: float(v) for k, v in raw.items()})

    unit_fields = (
        policy.sure_match, policy.sure_miss, policy.address_rescue
    )
    if not all(0.0 <= x <= 1.0 and math.isfinite(x) for x in unit_fields):
        raise ValueError("similarity thresholds must be finite and in [0, 1]")
    if not policy.sure_miss < policy.address_rescue <= policy.sure_match:
        raise ValueError("threshold ordering is invalid")
    if not 0.0 <= policy.near_m < policy.far_m:
        raise ValueError("distance bounds are invalid")

    canonical = json.dumps(asdict(policy), sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return Candidate(source=canonical, policy=policy, digest=digest)
```

The builder is trusted. The proposer can emit malformed JSON or invalid thresholds, but those outputs do not become candidates.

## Harness execution

```python
def run(policy: Policy, ex: Example) -> RunResult:
    events: list[TraceEvent] = []
    s = ex.name_similarity

    if s >= policy.sure_match:
        if ex.address_match and (ex.distance_m is None or ex.distance_m <= policy.near_m):
            events.append(TraceEvent("route", "deterministic same"))
            return RunResult(True, 0, tuple(events))
        if ex.distance_m is not None and ex.distance_m >= policy.far_m:
            events.append(TraceEvent("route", "deterministic different: far"))
            return RunResult(False, 0, tuple(events))

    if s <= policy.sure_miss:
        events.append(TraceEvent("route", "deterministic different: low similarity"))
        return RunResult(False, 0, tuple(events))

    if ex.address_match and s >= policy.address_rescue:
        events.append(TraceEvent("route", "deterministic same: address rescue"))
        return RunResult(True, 0, tuple(events))

    # A deterministic stand-in for an LM fallback. In a real system this is
    # an effect-handler call whose arguments, result, cost, and version are traced.
    events.append(TraceEvent("route", "fallback model"))
    model_prediction = (s >= 0.66) and (
        ex.address_match or ex.distance_m is None or ex.distance_m < 250.0
    )
    return RunResult(model_prediction, 1, tuple(events))
```

## Evaluation and Pareto dominance

```python
def evaluate(candidate: Candidate, data: Sequence[Example]) -> Evaluation:
    correct = 0
    calls = 0
    failures: list[tuple[Example, RunResult]] = []

    for ex in data:
        result = run(candidate.policy, ex)
        calls += result.model_calls
        if result.prediction == ex.label:
            correct += 1
        else:
            failures.append((ex, result))

    n = max(1, len(data))
    complexity = len(candidate.source)
    score = Score(
        accuracy=correct / n,
        negative_call_rate=-(calls / n),
        negative_complexity=-float(complexity),
    )
    return Evaluation(score=score, failures=tuple(failures))


def dominates(a: Score, b: Score) -> bool:
    av = (a.accuracy, a.negative_call_rate, a.negative_complexity)
    bv = (b.accuracy, b.negative_call_rate, b.negative_complexity)
    return all(x >= y for x, y in zip(av, bv)) and any(
        x > y for x, y in zip(av, bv)
    )


def pareto_insert(
    archive: list[tuple[Candidate, Evaluation]],
    item: tuple[Candidate, Evaluation],
) -> list[tuple[Candidate, Evaluation]]:
    candidate, evaluation = item
    if any(dominates(old_eval.score, evaluation.score)
           for _, old_eval in archive):
        return archive
    kept = [
        old for old in archive
        if not dominates(evaluation.score, old[1].score)
    ]
    if all(old_candidate.digest != candidate.digest for old_candidate, _ in kept):
        kept.append(item)
    return kept
```

## A semantic proposer

The proposer examines failures and changes one meaningful threshold. It is intentionally simple, but its interface matches an LLM-backed proposer.

```python
class Proposer(Protocol):
    def propose(
        self,
        parent: Candidate,
        evidence: Evaluation,
        rng: random.Random,
    ) -> str:
        ...


class SemanticProposer:
    def propose(
        self,
        parent: Candidate,
        evidence: Evaluation,
        rng: random.Random,
    ) -> str:
        p = dict(asdict(parent.policy))

        false_positive = [
            ex for ex, result in evidence.failures
            if result.prediction and not ex.label
        ]
        false_negative = [
            ex for ex, result in evidence.failures
            if (not result.prediction) and ex.label
        ]

        if false_positive and (not false_negative or rng.random() < 0.6):
            # Be more conservative about declaring a match.
            p["sure_match"] = min(0.99, p["sure_match"] + 0.02)
            p["address_rescue"] = min(
                p["sure_match"], p["address_rescue"] + 0.02
            )
            p["far_m"] = max(p["near_m"] + 1.0, p["far_m"] - 20.0)
        elif false_negative:
            # Expand the deterministic or fallback match region.
            p["sure_match"] = max(
                p["address_rescue"], p["sure_match"] - 0.02
            )
            p["sure_miss"] = max(0.01, p["sure_miss"] - 0.02)
            p["near_m"] = min(p["far_m"] - 1.0, p["near_m"] + 20.0)
        else:
            # With no observed errors, try reducing fallback calls.
            p["sure_miss"] = min(
                p["address_rescue"] - 0.01, p["sure_miss"] + 0.01
            )
            p["address_rescue"] = max(
                p["sure_miss"] + 0.01, p["address_rescue"] - 0.01
            )

        return json.dumps(p)
```

An LLM adapter would serialize typed traces and require JSON output. The same builder remains authoritative.

## Outer loop

```python
def optimize(
    seed_source: str,
    train: Sequence[Example],
    steps: int = 100,
    random_seed: int = 0,
) -> list[tuple[Candidate, Evaluation]]:
    rng = random.Random(random_seed)
    proposer: Proposer = SemanticProposer()

    seed = build_candidate(seed_source)
    archive = [(seed, evaluate(seed, train))]

    for _ in range(steps):
        parent, parent_eval = rng.choice(archive)
        proposal_source = proposer.propose(parent, parent_eval, rng)
        try:
            child = build_candidate(proposal_source)
        except (ValueError, TypeError, json.JSONDecodeError):
            continue
        child_eval = evaluate(child, train)
        archive = pareto_insert(archive, (child, child_eval))

    return sorted(
        archive,
        key=lambda item: (
            -item[1].score.accuracy,
            -item[1].score.negative_call_rate,
            item[0].digest,
        ),
    )
```

## What the prototype demonstrates

The prototype makes several distinctions concrete:

- proposal is untrusted;
- build is a typed partial function;
- traces and failures are structured evidence;
- selection is multi-objective;
- the archive is immutable in meaning even when represented by a mutable list;
- source hashes tie evidence to artifacts;
- semantic mutation is conditioned on failure classes;
- no score is confused with a proof.

It omits sandboxing because the DSL interpreter executes trusted host code. It omits stochastic judges, persistent history, held-out promotion, and formal proofs. These are deliberate extension points.

## Extension exercises

1. **Code.** Add a `Certified` versus `Empirical` route result.
2. **Code.** Replace the deterministic fallback with a stochastic kernel and add repeated evaluation.
3. **Code.** Add an epsilon-Pareto archive with score confidence intervals.
4. **Design.** Implement an LLM proposer adapter while preserving the trusted builder.
5. **Code.** Persist every proposal and rejection in an append-only event log.
6. **Proof.** Prove that every built policy satisfies `sure_miss < address_rescue <= sure_match`.
7. **Code.** Add a hidden test set and ensure the proposer never receives its failures.
8. **Research.** Compare semantic mutation with random numeric perturbation.
9. **Design.** Replace JSON with a typed architecture AST supporting an optional model branch.
10. **Code.** Add a contract-change proposal type and route it to a separate review function.

# Proof-Assistant Sketches and a Research Agenda

## A Lean-style resource analysis

The following Lean 4 sketch models a small untyped architecture tree and computes a worst-case model-call bound. It is intentionally compact; names may require minor adjustment for a specific Lean version.

```lean
inductive Harness where
  | pure
  | predict
  | seq      (left right : Harness)
  | route    (test yes no : Harness)
  | retry    (attempts : Nat) (body : Harness)
  deriving Repr, DecidableEq

open Harness

def calls : Harness -> Nat
  | pure => 0
  | predict => 1
  | seq a b => calls a + calls b
  | route t a b => calls t + max (calls a) (calls b)
  | retry n h => n * calls h

@[simp] theorem calls_seq (a b : Harness) :
    calls (seq a b) = calls a + calls b := rfl

@[simp] theorem calls_retry (n : Nat) (h : Harness) :
    calls (retry n h) = n * calls h := rfl

def WithinBudget (limit : Nat) (h : Harness) : Prop :=
  calls h <= limit

structure Certified (limit : Nat) where
  program : Harness
  bounded : WithinBudget limit program
```

An LLM can propose `program` and a proof script for `bounded`. Lean's kernel decides whether the term inhabits `Certified limit`.

## Indexed typed architecture

A stronger encoding indexes syntax by input, output, capability, and resource types:

```text
Harness : Type -> Type -> CapabilitySet -> Resource -> Type
```

Constructors enforce interface composition:

```text
Pure    : (X -> Y) -> Harness X Y empty zero
Predict : Signature X Y -> Harness X Y {ModelCall} oneCall
Seq     : Harness X Y e1 r1
       -> Harness Y Z e2 r2
       -> Harness X Z (e1 union e2) (r1 + r2)
```

In a dependently typed language, an ill-typed composition has no constructor. An optimizer can generate syntax with holes, and elaboration exposes exact obligations.

## A proof-producing router

A certified fast path can have type:

$$
  d:
  \prod_{x:X}
  p(x)
  \to
  \sum_{y:Y}\mathrm{Correct}(x,y).
$$

The complete router is:

```text
route : (x : X) -> Decidable (p x)
      -> CertifiedResult x + NeedsModel x
```

If the decision procedure returns evidence of $p(x)$, the deterministic solver returns a proved result. Otherwise the type forces the caller into the model branch. No threshold-only heuristic can impersonate a proof without constructing the evidence.

## Proof repair loop

A proof-aware optimizer protocol is:

```text
request:
  contract
  typed IR
  current proof terms
  failed goals
  local context
  counterexamples

response:
  revised IR
  revised proof script
  claimed lemmas

trusted actions:
  elaborate
  normalize
  invoke solver
  kernel check
  extract certified artifact
```

The proof assistant's error messages are structured feedback. They are not merely negative scores.

## Research problem: a categorical semantics of semantic mutation

A learned proposal kernel does not preserve composition or equivalence by default. One research direction is to define constrained proposer classes that are functorial, lax functorial, or optic-local under stated conditions.

Questions include:

- Can proposal prompts be generated compositionally from component contracts?
- Can a model produce a rewrite square and proof object together?
- Which architecture transformations admit reusable naturality laws?
- Can semantic neighborhoods be learned while guaranteeing interface and effect preservation?

## Research problem: proof-carrying reflective evolution

Build a system in which every archive candidate inhabits a dependent candidate type. The model proposes both code and proofs; a kernel checks them. Soft objectives choose among certified candidates.

Key challenges:

- proof search cost;
- specification engineering;
- connecting real model/tool APIs to formal semantics;
- incremental proof transport across rewrites;
- keeping the trusted base small;
- presenting proof failures as useful model feedback.

## Research problem: directed HoTT for versioned software

Ordinary HoTT models equivalence well but not one-way refinement. Directed type theories and synthetic infinity-categories may model version graphs with:

- invertible refactorings;
- directed feature and contract changes;
- higher coherence of merges;
- transport of tests and proofs;
- provenance-sensitive identity.

A concrete target is a proof-aware version-control calculus rather than a fully general foundation.

## Research problem: information-preserving feedback

Meta-Harness motivates preserving raw trajectories, while privacy and cost demand compression. The formal problem is to learn or construct summaries $S(\tau)$ sufficient for classes of repair decisions.

Possible directions:

- typed trace schemas with causal spans;
- adaptive retrieval over immutable raw logs;
- information-bottleneck objectives constrained by repair performance;
- summary certificates recording omitted fields;
- privacy-preserving trace abstractions;
- counterfactual trace generation.

## Research problem: judge-resistant optimization

Develop optimization protocols that remain valid under adaptive pressure on learned judges. Components may include:

- hidden rotating judge ensembles;
- randomized rubrics and presentation;
- adversarially generated judge probes;
- deterministic claim verification;
- human calibration with active sampling;
- statistical correction for repeated search;
- anomaly detection for proxy exploitation.

The target is not an "unhackable judge." It is an evaluation process whose residual uncertainty is measured and whose failures are difficult to correlate.

## Research problem: contract evolution

Requirements change. A system that can propose contract changes may be useful, but automatic metric-based acceptance is dangerous. Research questions:

- How are stakeholder intentions represented?
- Which contract changes are conservative refinements?
- How is proof and test evidence transported?
- How are conflicting objectives negotiated?
- How is authority encoded in the type of an approval?
- Can contract diffs be explained at the semantic rather than textual level?

## Research problem: open-endedness without verifier erosion

As the mutable boundary expands, the optimizer may eventually propose changes to its own search policy, evaluator, or verifier. A stable system needs a stratified hierarchy:

```text
Level 0: task implementation
Level 1: harness architecture
Level 2: proposal and archive policy
Level 3: evaluator configuration
Level 4: contract and trusted checker
```

Changes at higher levels require stronger external authorization. The hierarchy can be represented by capabilities and universe levels of governance artifacts. Self-reference is not prohibited; it is typed and gated.

## A final synthesis

Reflective program evolution is not one algorithm. It is a software regime in which source becomes a search variable and language becomes a medium of credit assignment. The appropriate formal model is correspondingly plural:

$$
\boxed{
\begin{aligned}
&\text{Execution:} && h:X\to T_r(Y\times\mathrm{Trace}) \\
&\text{Admissibility:} && \sum_h\mathrm{Admissible}_C(h) \\
&\text{Evaluation:} && M(h,D)\in\mathcal{D}(\mathbb{R}^k\times F\times E) \\
&\text{Proposal:} && Q(h'\mid h,\tau,f,H) \\
&\text{Search:} && S\to\mathcal{D}(O\times S) \\
&\text{Versioning:} && \text{evidence-bearing squares and directed rewrites} \\
&\text{Equivalence:} && \text{paths, transport, and higher coherence}.
\end{aligned}}
$$

The model suggests an engineering constitution:

1. Fix interfaces and contracts before optimizing implementations.
2. Give untrusted proposers a typed architecture language and narrow effects.
3. Preserve evidence with provenance; do not compress everything to a score.
4. Separate hard admissibility from soft multi-objective selection.
5. Use proof checkers and deterministic tools wherever the claim is formalizable.
6. Calibrate and isolate LLM judges; expect Goodhart effects.
7. Treat search metrics as training data and reserve hidden promotion evidence.
8. Model exact refactoring, approximate similarity, and directed improvement separately.
9. Deploy immutable certified versions through explicit gates.
10. Expand the mutable boundary only when the next boundary is stronger.

## Exercises

1. **Code.** Implement and prove the call-bound theorem for the sample AST in a proof assistant.
2. **Design.** Add capability indices to the AST and state a soundness theorem.
3. **Research.** Build an LLM-driven proof repair loop for one small verified component.
4. **Concept.** Which parts of the boxed model are deterministic, stochastic, logical, and policy-dependent?
5. **Design.** Define governance types for approving changes at Levels 0-4.
6. **Research.** Formalize a semantic merge square for two independent code edits.
7. **Proof.** State the theorem needed to transport a component proof across a representation equivalence.
8. **Research.** Learn a trace summary and test whether repair performance factors through it.
9. **Design.** Specify a judge-rotation protocol resistant to adaptive overfitting.
10. **Synthesis.** Apply the complete framework to a system of your choice and identify every object, morphism, effect, grade, contract, path, refinement, coalgebra state, and evidence type.

\appendix

# Mathematical Cheat Sheet

## Category-theory patterns

| Concept | Formal shape | Software interpretation |
|---|---|---|
| Category | objects, morphisms, identity, composition | interfaces and composable components |
| Functor | $F(g\circ f)=F(g)\circ F(f)$ | structure-preserving translation or interpretation |
| Natural transformation | $G(f)\eta_X=\eta_YF(f)$ | uniform implementation or representation change |
| Product | $X\times Y$ with projections | record, tuple, simultaneous evidence |
| Coproduct | $X+Y$ with case analysis | tagged alternatives and routing |
| Monoidal product | $X\otimes Y$ | side-by-side composition or parallel dataflow |
| Monad | $X\to T(Y)$ and bind | composable effectful computation |
| Kleisli category | morphisms $X\to T(Y)$ | category of effectful harnesses |
| Graded monad | $X\to T_r(Y)$ | effect plus resource/capability index |
| Markov kernel | $X\rightsquigarrow Y$ | stochastic model-backed computation |
| Trace | $X\otimes U\to Y\otimes U$ fed back | loops, agents, recursive harnesses |
| Coalgebra | $S\to F(S)$ | observable state transition system |
| Lens/optic | focus plus update | local component rewriting |
| Enrichment | homs carry order/cost | refinement, latency, semantic distance |
| Double category | horizontal, vertical, squares | execution, versions, and rewrite evidence |
| Operad | multi-input operations and substitution | architecture grammar |

## Type-theory patterns

| Concept | Formal shape | Software interpretation |
|---|---|---|
| Function type | $A\to B$ | computation or implication |
| Product type | $A\times B$ | conjunction and pair |
| Sum type | $A+B$ | disjunction and tagged result |
| Dependent product | $\prod_{x:A}B(x)$ | universal proof or dependent function |
| Dependent sum | $\sum_{x:A}B(x)$ | witness packaged with evidence |
| Refinement type | $\{x:A\mid P(x)\}$ | value satisfying a predicate |
| Identity type | $a=_A b$ | equality proof/path |
| Equivalence | $A\simeq B$ | invertible representation change |
| Transport | along $p:A=B$ | move values/proofs across equality |
| Univalence | $(A=B)\simeq(A\simeq B)$ | equivalent representations can be identified |
| HIT | point and path constructors | syntax modulo rewrite laws |
| Truncation | forget higher structure | controlled evidence compression |
| Directed refinement | $a\preceq b$ | one-way improvement or stronger contract |

## Evidence hierarchy

```text
Untrusted claim
    |
    v
Parses / schema-valid
    |
    v
Type- and capability-valid
    |
    v
Passes deterministic checks
    |
    v
Satisfies bounded formal model
    |
    v
Kernel-checked theorem under assumptions

Orthogonal empirical axis:

single example -> test suite -> held-out estimate ->
shift evaluation -> calibrated live evidence
```

Formal and empirical evidence are not one linear scale. A proof may cover a narrow model while empirical tests cover unformalized integration behavior. Store both.

## Unified equations

Harness:

$$
  h:X\to T_r(Y\times\mathrm{Trace}).
$$

Certified candidate:

$$
  \mathrm{Candidate}_C
  =\sum_h\mathrm{Admissible}_C(h).
$$

Stochastic evaluation:

$$
  M(h,D)\in\mathcal{D}(\mathbb{R}^k\times F\times E).
$$

Proposal:

$$
  h'\sim Q(-\mid h,\tau,f,H).
$$

Outer loop:

$$
  S\to\mathcal{D}(O\times S).
$$

Pareto dominance:

$$
  u\succ v
  \iff
  (\forall i,u_i\ge v_i)\land(\exists j,u_j>v_j).
$$

Rewrite square:

$$
\begin{array}{ccc}
X & \xrightarrow{h} & Y\\
\downarrow u & \Downarrow\alpha & \downarrow v\\
X' & \xrightarrow{h'} & Y'.
\end{array}
$$

Certified fast path:

$$
  \forall x,\;p(x)\to\mathrm{Correct}(x,d(x)).
$$

# Engineering Pattern Catalog

## Stable interface, fluid implementation

**Problem.** The optimizer needs freedom to change architecture without breaking clients.

**Pattern.** Fix a typed input-output contract. Search implementations in the fiber over that contract. Enforce substitutability at the build boundary.

**Tradeoff.** A narrow interface improves safety but may hide information needed for optimization.

## Typed architecture before source

**Problem.** Unrestricted source generation produces invalid, unsafe, and difficult-to-analyze candidates.

**Pattern.** Generate a typed IR or operadic architecture term. Compile through a small trusted interpreter or compiler. Keep raw code as an audited primitive.

**Tradeoff.** The grammar limits novelty and requires language design.

## Certified fast path with model fallback

**Problem.** Many inputs can be handled cheaply, but heuristic routing can create silent errors.

**Pattern.** Let the fast path return a value plus certificate or `Unknown`. Delegate only uncertified cases to a model.

**Tradeoff.** Proof construction can reduce coverage and increase development cost.

## Hard-constraint filter before Pareto selection

**Problem.** A weighted score can compensate for safety or policy violations.

**Pattern.** Construct the admissible candidate type first. Run multi-objective optimization only inside it.

**Tradeoff.** Overly strong constraints can remove useful candidates; contract changes need a separate path.

## Typed feedback algebra

**Problem.** One free-form feedback string mixes proof failures, resource violations, and preferences.

**Pattern.** Use tagged constructors for counterexamples, contract violations, trace anomalies, judge critiques, and hints.

**Tradeoff.** Structured feedback may omit useful nuance; retain a text field inside appropriate constructors.

## Full evidence log with derived views

**Problem.** Scores and summaries discard details needed for later repairs.

**Pattern.** Store immutable raw traces and provenance where policy permits. Build summaries and indexes as reproducible views.

**Tradeoff.** Storage, privacy, and prompt-injection risk increase.

## Local optic edit, global rewrite fallback

**Problem.** Whole-program rewrites are powerful but high-risk; local edits can miss architectural problems.

**Pattern.** Default to typed, focused edits using AST optics. Escalate to global proposals when evidence implicates structure.

**Tradeoff.** Credit assignment must decide when escalation is justified.

## Staged evaluation

**Problem.** Full evaluation is expensive and noisy.

**Pattern.** Apply parse/type/proof checks, then small batches, larger paired comparisons, hidden tests, and staged deployment.

**Tradeoff.** Early racing can discard high-variance or niche candidates.

## Judge isolation and calibration

**Problem.** An adaptive optimizer exploits learned judge biases.

**Pattern.** Blind identities, randomize order, decompose rubrics, calibrate against humans, rotate hidden probes, and use deterministic checks for formal claims.

**Tradeoff.** Evaluation becomes slower and more expensive; no learned judge becomes perfectly objective.

## Proof-aware archive

**Problem.** A high-scoring candidate can have weaker evidence than a slightly lower-scoring one.

**Pattern.** Include proof coverage, evidence strength, or assurance tier in archive dimensions. Never overwrite evidence when scores change.

**Tradeoff.** Archive size grows and evidence types can be difficult to compare.

## Immutable promotion

**Problem.** Live self-modification makes rollback, audit, and attribution difficult.

**Pattern.** Search continuously but deploy immutable, signed candidate versions through canary or shadow gates.

**Tradeoff.** Adaptation is slower than direct in-place rewriting.

## Separate implementation and contract proposals

**Problem.** A system can "improve" by weakening its own tests or requirements.

**Pattern.** Use distinct sum constructors and authorization paths for implementation candidates and contract changes.

**Tradeoff.** Legitimate requirement evolution requires human or organizational governance.

## Version the evaluator

**Problem.** A changing judge or model changes the meaning of old scores.

**Pattern.** Treat evaluator, model, prompt, rubric, and price schedule as versioned instruments. Re-evaluate frontier candidates when the instrument changes.

**Tradeoff.** Historical score comparability remains limited.

## Semantic deduplication

**Problem.** Search wastes budget on formatting and law-equivalent variants.

**Pattern.** Normalize typed architecture terms, use e-graphs for validated equations, and hash canonical forms.

**Tradeoff.** An overly coarse equivalence can erase cost, security, or readability differences.

## Stratified self-reference

**Problem.** An optimizer may eventually propose changes to its own proposer, evaluator, or verifier.

**Pattern.** Assign mutation levels and increasing authorization requirements. Keep the checker for level $n$ outside the mutable authority of level $n$.

**Tradeoff.** No finite stratification captures unrestricted self-reference; choose a governance boundary.

# Selected Exercise Solutions and Hints

The following are selected solutions, not a complete answer key. Many design and research exercises admit several defensible answers.

## Chapter 1, Exercise 4: total composition and exceptions

For total $f:X\to Z$ and $g:Z\to Y$, every $x:X$ yields $f(x):Z$, then $g(f(x)):Y$. Therefore $g\circ f$ is total.

With exceptions, let $f:X\to Z+E$ and $g:Z\to Y+E$. Even if both functions are total as functions into a result type, the composed computation may return an error rather than a $Y$. If "total" means "always produces a successful $Y$," the claim fails. The Kleisli composite is still total into $Y+E$.

## Chapter 2, Exercise 10: noninjective summaries

If $q:T\to S$ is not injective, choose $t_1\ne t_2$ with $q(t_1)=q(t_2)$. For any $g:S\to R$,

$$
  g(q(t_1))=g(q(t_2)).
$$

Thus $g\circ q$ cannot distinguish $t_1$ and $t_2$. No downstream computation can recover a distinction erased by $q$ without side information.

## Chapter 3, Exercise 8: proxy maximization

Let candidates have true qualities $q(a)=0.8$ and $q(b)=0.7$. Let proxy bias be $b(a)=0$ and $b(b)=0.3$. Then $J(a)=0.8$ and $J(b)=1.0$, so maximizing $J$ chooses $b$ although its true quality is lower. Positive correlation on an initial sample does not prevent the optimizer from finding a region with large bias.

## Chapter 4, Exercise 4: finite-test equivalence

Define $p\sim_Dq$ when $p(x)=q(x)$ for all $x\in D$.

- Reflexive: $p(x)=p(x)$.
- Symmetric: if $p(x)=q(x)$, then $q(x)=p(x)$.
- Transitive: if $p(x)=q(x)$ and $q(x)=r(x)$, then $p(x)=r(x)$.

Therefore $\sim_D$ is an equivalence relation on deterministic programs defined on $D$.

It need not imply equality outside $D$.

## Chapter 4, Exercise 8: monotonic resource replacement

Suppose pipeline bound is $r_1+r_2+\cdots+r_n$ in an ordered commutative monoid whose addition is monotone. Replacing $r_i$ by $r_i'\le r_i$ gives

$$
  r_1+\cdots+r_i'+\cdots+r_n
  \le
  r_1+\cdots+r_i+\cdots+r_n.
$$

Monotonicity of addition is the required assumption.

## Chapter 5, Exercise 5: deterministic embedding

Map a function $f:X\to Y$ to the Markov kernel $J(f)$ defined by the point mass

$$
  J(f)(A\mid x)=\mathbf{1}[f(x)\in A].
$$

Identity maps to a point mass at $x$, which is the stochastic identity. Composition of point masses integrates to a point mass at $g(f(x))$, so

$$
  J(g\circ f)=J(g)\circ J(f).
$$

Hence $J$ is a functor.

## Chapter 6, Exercise 4: distributivity maps

Define

$$
  \phi:A\times(B+C)\to(A\times B)+(A\times C)
$$

by

$$
  \phi(a,\iota_1 b)=\iota_1(a,b),
  \qquad
  \phi(a,\iota_2 c)=\iota_2(a,c).
$$

Define the inverse

$$
  \psi(\iota_1(a,b))=(a,\iota_1 b),
  \qquad
  \psi(\iota_2(a,c))=(a,\iota_2 c).
$$

Case analysis shows $\psi\circ\phi=\mathrm{id}$ and $\phi\circ\psi=\mathrm{id}$.

## Chapter 7, Exercise 1: exception Kleisli composition

For $f:X\to Y+E$ and $g:Y\to Z+E$, define

$$
  (g\star f)(x)=
  \begin{cases}
  e,& f(x)=\mathrm{Error}(e),\\
  g(y),& f(x)=\mathrm{Ok}(y).
  \end{cases}
$$

This is ordinary `and_then` or bind. Associativity follows by case analysis on the earliest error.

## Chapter 7, Exercise 5: graded associativity

Let $f$ have grade $r$, $g$ grade $s$, and $h$ grade $t$. The two parenthesizations have grades

$$
  (r+s)+t
  \quad\text{and}\quad
  r+(s+t).
$$

They are equal by associativity of the resource monoid. This is why the grade structure must be a monoid or a suitable generalization.

## Chapter 8, Exercise 10: bounded loop grade

If each iteration costs at most $r$ and the loop executes at most $n$ iterations, the sequential bound is

$$
  \underbrace{r+\cdots+r}_{n\text{ times}}=nr.
$$

Add any fixed setup and teardown grades separately. If early termination is possible, $nr$ remains the worst-case bound but not the expected cost.

## Chapter 9, Exercise 1: record-field lens laws

For a record $s$ with field $a$, let `get(s)=s.a` and `put(s,a')` copy $s$ with field $a'`.

1. Get-put: `put(s, get(s)) = s`.
2. Put-get: `get(put(s,a')) = a'`.
3. Put-put: `put(put(s,a1),a2) = put(s,a2)`.

These laws fail if `put` modifies unrelated fields, normalizes nondeterministically, or invokes an LLM that rewrites surrounding code.

## Chapter 10, Exercise 2: horizontal square composition

Suppose

$$
 v\circ f=f'\circ u
$$

and

$$
 w\circ g=g'\circ v.
$$

Then

$$
 w\circ g\circ f
 =g'\circ v\circ f
 =g'\circ f'\circ u.
$$

Thus the horizontally composed square commutes. Exact equality is crucial; empirical "improvement" labels do not support this derivation.

## Chapter 11, Exercise 9: finite penalties do not enforce hard constraints

Let objective be $Q(h)-M\cdot\mathbf{1}[\neg C(h)]$ for finite penalty $M$. If $Q$ is unbounded, choose a violating candidate with $Q(h)>M+Q(h_c)$ for every admissible incumbent $h_c$. The violating candidate wins. A hard filter or infinite/lexicographic priority is required.

## Chapter 12, Exercise 5: expected router cost

Let deterministic branch cost $c_e$, model branch cost $c_h$, and model-branch probability $q$. Then

$$
  \mathbb{E}[C]=(1-q)c_e+qc_h.
$$

If routing itself costs $c_r$, add it:

$$
  c_r+(1-q)c_e+qc_h.
$$

Worst-case cost is $c_r+\max(c_e,c_h)$ when exactly one branch executes.

## Chapter 13, Exercise 2: $A\to(B\to A)$

A term is

```text
lambda a. lambda b. a
```

It ignores the $B$ witness and returns the original $A$. Logically, from $A$ one can prove $B\to A$.

## Chapter 13, Exercise 3: dependent-free distributivity

Forward:

```text
(a, Left b)  -> Left (a, b)
(a, Right c) -> Right (a, c)
```

Backward:

```text
Left (a, b)  -> (a, Left b)
Right (a, c) -> (a, Right c)
```

The functions are mutual inverses by case analysis.

## Chapter 14, Exercise 2: function-contract substitution

Suppose the old function requires $P$ and guarantees $Q$. A replacement requires $P'$ and guarantees $Q'$. Safe substitution follows if

$$
  P\Rightarrow P'
  \quad\text{and}\quad
  Q'\Rightarrow Q.
$$

The replacement accepts every old-valid input because its precondition is weaker. Its result satisfies the old expectation because its postcondition is stronger.

## Chapter 15, Exercise 2: nested resource bound

For

```text
Route(test,
      Retry(3, Predict),
      Seq(Predict, Predict))
```

and `calls(test)=0`, branch bounds are $3$ and $2$. The route executes one branch, so worst-case calls are

$$
  0+\max(3,2)=3.
$$

Adding both branch costs would be an overapproximation unless both execute.

## Chapter 16, Exercise 4: approximate verifier

Classical CEGIS accepts only when the verifier establishes that no counterexample exists in the specified domain. Random testing establishes only that no counterexample was sampled. The universal conclusion

$$
  \forall x,\varphi(p,x)
$$

is therefore unavailable. What remains is an empirical confidence statement under the sampling process.

## Chapter 16, Exercise 9: monotone certified region

Let certified set be $S_p=\{x\mid p(x)\}$. If $p(x)\Rightarrow p'(x)$ for all $x$, then $S_p\subseteq S_{p'}$. If a correctness theorem is proved for $p'$, every input previously certified remains certified, and possibly more are added.

## Chapter 17, Exercise 5: untrusted proof generator

Let the model output a term $t$ claiming type $P$. A sound kernel checks $t:P$. Acceptance depends on kernel verification, not model honesty. The model may waste time or fail to produce a proof, but cannot make a false proposition accepted unless the kernel, axioms, parser, or trusted translation is unsound.

## Chapter 18, Exercise 8: approximate path triangle

Assume behavioral distance $d$ satisfies the triangle inequality. Certificates give

$$
  d(h,h')\le\epsilon_1,
  \qquad
  d(h',k)\le\epsilon_2.
$$

Then

$$
  d(h,k)\le d(h,h')+d(h',k)
  \le\epsilon_1+\epsilon_2.
$$

The result is an enriched or metric composition law, not identity-path concatenation.

## Chapter 19, Exercise 2: swapping a product

Define $f:A\times B\to B\times A$ by $f(a,b)=(b,a)$. The same formula gives $g:B\times A\to A\times B$. Then $g(f(a,b))=(a,b)$ and $f(g(b,a))=(b,a)$. Thus $f$ is an equivalence with inverse $g$.

## Chapter 20, Exercise 6: sufficient-statistic factorization

For a class $\mathcal{G}$ of repair-decision functions $g:T\to R$, a summary $S:T\to U$ is sufficient when for every $g\in\mathcal{G}$ there exists $\bar g:U\to R$ such that

$$
  g=\bar g\circ S.
$$

Every relevant decision then factors through the summary. If no such $\bar g$ exists for some $g$, the summary discarded relevant information.

## Chapter 21, Exercise 2: mutual refinement quotient

For a preorder $\preceq$, define $a\sim b$ when $a\preceq b$ and $b\preceq a$.

- Reflexive by preorder reflexivity.
- Symmetric by definition.
- Transitive: $a\preceq b\preceq c$ gives $a\preceq c$, and $c\preceq b\preceq a$ gives $c\preceq a$.

Thus $\sim$ is an equivalence relation. The quotient is partially ordered by induced refinement.

## Chapter 22, Exercise 3: certified build result

Suppose `consume` has type

```text
Certified Candidate -> Output
```

and `build` returns

```text
Rejected Error + Certified Candidate.
```

The caller must pattern-match. In the `Rejected` branch there is no term of type `Certified Candidate` to pass to `consume`. This guarantee assumes the language has no unchecked cast or memory unsafety that can fabricate the type.

## Chapter 23, Exercise 3: winner's curse

Let $\hat q_i=q+\epsilon_i$ with independent, zero-mean noise and equal true quality. Then

$$
  \mathbb{E}[\max_i\hat q_i]
  =q+\mathbb{E}[\max_i\epsilon_i]
  >q
$$

for nondegenerate noise and $N>1$. The selected estimate is optimistic. Independent reevaluation removes the selection-conditioned noise in expectation.

## Chapter 24, Exercise 11: paired variance

For paired outcomes $X_i,Y_i$,

$$
  \mathrm{Var}(X_i-Y_i)
  =\mathrm{Var}(X_i)+\mathrm{Var}(Y_i)
   -2\mathrm{Cov}(X_i,Y_i).
$$

Positive covariance reduces variance relative to independent samples, where the covariance term is zero.

## Chapter 25, Exercise 1: router type

Let

$$
 r:X\to D+A,
 \quad d:D\to Y,
 \quad \ell:A\to T(Y).
$$

Embed $d$ as $J(d):D\to T(Y)$. Copairing gives

$$
 [J(d),\ell]:D+A\to T(Y).
$$

Therefore

$$
 [J(d),\ell]\circ r:X\to T(Y).
$$

## Chapter 25, Exercise 10: clipping

Without clipping, `correct - lambda*calls` is a linear scalarization of two per-example quantities. Applying $\max(0,-)$ introduces a nonlinear kink and identifies all negative values with zero. Aggregate behavior therefore cannot be treated as an unconstrained weighted sum with the usual linear properties.

## Chapter 26, Exercise 8: commuting patches

Sufficient conditions include:

- patches modify disjoint syntactic regions;
- neither patch changes names, types, or invariants used by the other;
- applying either patch preserves the precondition of the other;
- the build and semantic effects are independent.

Then applying $p$ followed by $q$ and $q$ followed by $p$ yields the same or provably equivalent program. Disjoint line ranges alone are not sufficient when both depend on shared semantics.

## Chapter 27, Exercise 6: threshold invariant

`build_candidate` accepts only when

$$
  \mathrm{sure\_miss}
  <\mathrm{address\_rescue}
  \le\mathrm{sure\_match}.
$$

Therefore every returned `Candidate` has a `Policy` satisfying the invariant. The proof is by inspection of the only constructor path: after parsing, the function raises on the negation and returns only in the remaining branch. In a dependently typed implementation, the return type would carry the proof explicitly.

## Chapter 28, Exercise 2: capability-index soundness statement

A suitable theorem is:

> If $h:\mathrm{Harness}\;X\;Y\;\epsilon\;r$ evaluates under handler environment $H$, then every effect event in its trace has a capability contained in $\epsilon$; and if $\epsilon\subseteq A$, the run requests no capability outside deployment allowlist $A$.

The proof proceeds by induction on the typed architecture term, assuming each primitive handler emits only its declared effect.

# Glossary

**Abstraction barrier.** An interface that hides implementation details while exposing stable operations and laws.

**Admissible candidate.** A candidate that satisfies all hard interface, policy, capability, resource, and proof requirements for a stated contract.

**Algebra.** For an endofunctor $F$, a map $F(A)\to A$; often a way to fold or interpret syntax.

**Algebraic effect.** A requested operation whose interpretation is supplied separately by an effect handler.

**Antichain.** A set of elements no two of which are comparable under a given partial order; a Pareto frontier is an antichain under dominance.

**Architecture grammar.** A typed language of permitted harness structures and substitutions.

**Artifact hash.** A content-derived identifier tying evidence to exact source, IR, data, or configuration bytes.

**Bicategory.** A category-like structure with objects, 1-cells, and 2-cells, where composition laws hold up to coherent isomorphism.

**Bisimulation.** A relation showing that two transition systems can match each other's observations and steps.

**Build boundary.** The trusted process that parses, type-checks, verifies, and packages untrusted proposals.

**Capability.** Authority to perform an effect such as reading a file, calling a tool, using a model, or accessing a network.

**Category.** Objects and composable morphisms satisfying identity and associativity laws.

**CEGIS.** Counterexample-Guided Inductive Synthesis, alternating candidate generation with verification and counterexample refinement.

**Coalgebra.** For an endofunctor $F$, a map $S\to F(S)$ describing observable stateful behavior.

**Coherence.** Laws or higher proofs ensuring that alternative compositions or transformations agree.

**Compiler, optimization sense.** A process that maps a declarative LM program to an empirically optimized implementation; unlike a conventional verified compiler, semantic preservation is not automatic.

**Congruence.** An equivalence relation preserved by surrounding program contexts or operations.

**Contract.** A versioned collection of interface, effect, resource, functional, statistical, and governance requirements.

**Contract refinement.** A directed strengthening or substitutable change to a contract.

**Coproduct.** A universal tagged sum $A+B$ supporting case analysis; the categorical form of routing alternatives.

**Counterexample.** A witness, tied to a contract clause, showing that a candidate violates a property.

**Curry-Howard correspondence.** The relation between propositions and types, proofs and programs.

**Dependent product.** A type $\prod_{x:A}B(x)$ of functions whose result type depends on the input; the type-theoretic universal quantifier.

**Dependent sum.** A type $\sum_{x:A}B(x)$ packaging a witness with evidence; the type-theoretic existential quantifier.

**Directed type theory.** Type-theoretic frameworks with noninvertible arrows in addition to equality paths.

**Dijkstra monad.** A specification-indexed monadic structure used to reason about effectful computations through weakest preconditions.

**Double category.** A structure with horizontal and vertical arrows plus squares, useful for executions, versions, and rewrite evidence.

**Effect handler.** Host-controlled interpretation of requested effects.

**Effect row or set.** A type-level record of effects a computation may request.

**Enriched category.** A category whose hom-objects carry additional structure such as order, metric, or cost.

**Equality saturation.** Optimization by representing many equivalent terms simultaneously, often in an e-graph, and extracting a preferred representative.

**Evaluator.** A system that produces metrics, traces, counterexamples, and evidence from candidate executions.

**Evidence precedence.** A policy stating which evidence kinds can reject, override, or merely influence a decision.

**Evolutionary search.** Population- or archive-based generation, evaluation, selection, and variation of candidates.

**Fiber.** In this book, the space or type of implementations lying over a fixed contract or semantic object.

**Formal proof.** A derivation checked by a trusted logical kernel under explicit assumptions.

**Functor.** A mapping between categories preserving identities and composition.

**GEPA.** Genetic-Pareto reflective optimization using natural-language feedback, trajectories, and Pareto-based candidate selection.

**Genotype.** The stored candidate representation, such as source, prompts, configuration, and memory.

**Goodhart's law.** The family of failures that occur when optimization targets a proxy measure rather than the underlying goal.

**Grade.** An index on an effectful computation representing resources, capabilities, or another compositional quantity.

**Graded monad.** A monadic family $T_r$ whose grades combine under composition.

**Harness.** Code and configuration surrounding a model, determining context, tools, control flow, memory, verification, and output handling.

**Higher inductive type.** A type defined with constructors for points, paths, and possibly higher paths.

**Higher path.** An identity between identity proofs; in software, coherence between transformation paths.

**HoTT.** Homotopy Type Theory, interpreting types as spaces and identities as paths, with principles such as univalence.

**Identity type.** The type $a=_A b$ of proofs or paths identifying two terms.

**Information flow.** How data of different security labels may influence outputs or external effects.

**Intrinsic verification.** A representation in which invalid programs are unconstructable by the available constructors.

**Judge.** A usually learned or human evaluator for soft, underspecified, or preference-based quality.

**Kleisli category.** The category whose morphisms $X\to Y$ are effectful maps $X\to T(Y)$ for a monad $T$.

**Language-mediated credit assignment.** Using natural-language analysis of evidence to propose changes; a more precise phrase than "text gradient."

**Lawvere metric.** A view of metric or cost structure as category enrichment over ordered quantities.

**Lens.** A compositional focus with operations to get and update a part of a whole, subject to laws.

**Markov category.** A categorical framework for stochastic processes and Markov kernels.

**Meta-held-out evaluation.** Testing across tasks, models, domains, or time periods outside all optimizer selection loops.

**Monad.** A structure for composing effectful computations using unit and bind while satisfying identity and associativity laws.

**Monoidal category.** A category with a tensor product for side-by-side composition and a unit object.

**Mutation kernel.** A conditional distribution over proposed candidates given parent and evidence.

**Natural transformation.** A coherent family of morphisms between functors that commutes with every source morphism.

**Noninterference.** A security property stating that protected inputs do not influence public observations except through approved declassification.

**Observation type.** The aspects of behavior used to compare systems; changing observations changes equivalence.

**Optic.** A general compositional abstraction for focusing, viewing, and updating structured data or systems.

**Operad.** A structure of multi-input operations and substitution, useful for architecture templates.

**Pareto dominance.** Componentwise no-worse comparison with strict improvement in at least one objective.

**Pareto frontier.** The nondominated set of candidates under a multi-objective order.

**Partial evaluation.** Specializing a general computation using known structure so some work becomes deterministic or precomputed.

**Path.** An identity witness in HoTT; often used here for verified equivalence or refactoring.

**Phenotype.** Observable candidate behavior after execution in a particular environment.

**Postcondition.** A property required of outputs and final state after a computation.

**Precondition.** A property required before a computation may be invoked under its contract.

**Proof-carrying code.** Untrusted code accompanied by a proof that a small trusted checker validates against a safety policy.

**Proof relevance.** Treating different proofs or evidence derivations as distinguishable data.

**Proposal model.** A model that generates revised source, architecture, prompts, or proofs.

**Propositional truncation.** A HoTT construction retaining only the fact that a type is inhabited while forgetting the witness.

**Provenance.** The derivation history and environmental metadata of an artifact and its evidence.

**Quality diversity.** Search that preserves high-performing candidates across different behavior niches rather than only one global best.

**Refinement.** A directed relation expressing stronger guarantees, fewer effects, or no-worse behavior under a specified order.

**Refinement type.** A base type restricted by a logical predicate.

**Reflection model.** A model that inspects traces and feedback to diagnose and propose changes.

**Reindexing.** Moving a dependent object or implementation along a map between specifications or indices.

**Resource monoid.** A compositional resource domain with an associative combination and zero.

**Rewrite square.** A square relating old and new implementations, interfaces, and evidence that paths commute or refine.

**RLM.** Recursive Language Model strategy that treats long context as an external programmable environment and recursively invokes models on selected parts.

**Sandbox.** An operational isolation environment restricting the consequences and capabilities of untrusted code.

**Scalarization.** A policy map from a multi-objective vector to one scalar.

**Selective prediction.** A system that can abstain, trading coverage for lower conditional risk.

**Semantic mutation.** A task-aware, evidence-conditioned program change intended to preserve boundaries while addressing behavior.

**Specification gap.** The difference between what a contract states and what stakeholders actually require.

**String diagram.** A graphical language for monoidal categories showing components as boxes and data as wires.

**Substitutivity.** The property that replacing a component by a refinement or equivalent preserves a relation in every allowed context.

**Sufficient statistic.** A summary through which every relevant inference or decision can factor.

**Trace.** Structured execution evidence including calls, branches, outputs, costs, errors, and provenance.

**Traced monoidal category.** A monoidal category with a lawful feedback operation.

**Translation validation.** Checking each compiled artifact against source semantics rather than proving the compiler globally correct.

**Trusted computing base.** Components whose correctness is assumed for the system's guarantees.

**Typed intermediate representation.** A restricted program language whose constructors encode interfaces, effects, and other invariants.

**Univalence.** The principle connecting equality of types with equivalence of types.

**Universal property.** A definition by unique mapping behavior rather than internal representation.

**Verifier.** A checker of explicit, usually hard properties; unlike a judge, it should produce sound decisions within its modeled fragment.

**Weakest precondition.** The least condition on inputs sufficient to establish a postcondition after a computation.

**Winner's curse.** Optimism in the estimated quality of a candidate selected as the maximum among many noisy estimates.
\backmatter

# Sources and Further Reading {-}

\markboth{Sources and Further Reading}{Sources and Further Reading}

## How to use this guide {-}

This book distinguishes four kinds of source:

- **Primary research** introduces an algorithm, formalism, theorem, or empirical result.
- **Official documentation** specifies the behavior of a current software system. Documentation is authoritative about an interface, but not evidence that the interface is safe, stable, or generally effective.
- **Textbooks and surveys** supply mature exposition and historical context.
- **Case-study reports** motivate hypotheses. Their measurements remain conditional on the stated data, models, prices, hardware, and evaluation protocol.

The references below are deliberately broader than the claims made in the chapters. They form a curriculum for reconstructing, criticizing, and extending the framework. Web resources were checked on August 7, 2026. Preprints should be read as provisional until independently replicated or peer reviewed.

## Chapter-to-source map {-}

| Chapters | Core reading | Purpose |
|---|---|---|
| 1-3 | LLM-01 through LLM-17; EV-01 through EV-12 | Reflective optimization, whole-harness search, and its relation to genetic programming |
| 4-6 | CAT-01 through CAT-09; TYPE-04 through TYPE-06 | Mathematical language for interfaces, composition, products, sums, and universal properties |
| 7-8 | CAT-10 through CAT-24 | Effects, resource grades, probability, feedback, fixed points, traces, and coalgebra |
| 9-12 | CAT-25 through CAT-36; LLM-03, LLM-08, LLM-09 | Textual feedback, optics, learners, rewrites, double categories, and Pareto archives |
| 13-17 | TYPE-01 through TYPE-36; SYN-01 through SYN-12 | Curry-Howard, dependent and refinement types, synthesis, proof-carrying code, and weakest preconditions |
| 18-21 | HOTT-01 through HOTT-18; CAT-37 | Identity, equivalence, univalence, higher coherence, and directed refinement |
| 22 | All groups, especially SYS-01 through SYS-20 | Production architecture and trust boundaries |
| 23-24 | EVAL-01 through EVAL-27 | LLM judges, measurement, adaptive overfitting, paired statistics, and uncertainty |
| 25 | LLM-01 through LLM-03; EVAL-12 through EVAL-17 | The Flex location-conflation report and appropriate statistical interpretation |
| 26 | LLM-07, LLM-08, LLM-12, LLM-16, LLM-22 | Harness memory, coding agents, recursive scaffolds, and meta-optimization |
| 27-28 | SYN-01 through SYN-18; TYPE-20 through TYPE-36; SYS-13 through SYS-20 | Executable implementation, proof-assistant encodings, provenance, and deployment |

## Reflective LM programs and self-optimizing harnesses {-}

**LLM-01.** Michael Isaac. ["Introducing Flex: Let the Model Write the Code"](https://www.cmpnd.ai/blog/let-the-model-write-the-code.html), cmpnd, August 5, 2026. The motivating case-study report. Read it for the concrete optimization loop, location-conflation measurements, generated routing structure, and explicit pilot caveat on coding tasks.

**LLM-02.** DSPy project. ["Flex: Optimizable Module Code"](https://dspy.ai/diving-deeper/flex/) and the [Flex API reference](https://dspy.ai/api/modules/Flex/), 2026. Official description of source code as an optimizable parameter, sandboxed execution, output-type checks, persistence, failure handling, and experimental status.

**LLM-03.** Lakshya A. Agrawal et al. ["GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning"](https://arxiv.org/abs/2507.19457), 2025. Introduces Genetic-Pareto optimization with trace-conditioned natural-language reflection and per-instance Pareto selection.

**LLM-04.** DSPy project. [GEPA documentation](https://dspy.ai/api/optimizers/GEPA/overview/) and [GEPA tutorials](https://dspy.ai/tutorials/gepa_ai_program/), 2025-2026. Useful for the operational metric interface, predictor-level and program-level feedback, trace exposure, and implementation constraints.

**LLM-05.** Omar Khattab et al. ["DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines"](https://arxiv.org/abs/2310.03714), ICLR 2024. Establishes signatures, modules, teleprompters/optimizers, and compilation of declarative LM programs.

**LLM-06.** Krista Opsahl-Ong et al. ["Optimizing Instructions and Demonstrations for Multi-Stage Language Model Programs"](https://arxiv.org/abs/2406.11695), 2024. Introduces MIPRO and studies credit assignment across multi-stage LM programs before whole-code optimization.

**LLM-07.** Alex L. Zhang, Tim Kraska, and Omar Khattab. ["Recursive Language Models"](https://arxiv.org/abs/2512.24601), 2025. Treats long context as an external programmable environment and lets a model inspect, decompose, and recursively invoke itself over selected portions.

**LLM-08.** Yoonho Lee et al. ["Meta-Harness: End-to-End Optimization of Model Harnesses"](https://arxiv.org/abs/2603.28052), 2026. Searches harness code with an agentic proposer that can inspect source, scores, raw traces, and search history; especially relevant to the information-loss discussion.

**LLM-09.** Mert Yuksekgonul et al. ["TextGrad: Automatic 'Differentiation' via Text"](https://arxiv.org/abs/2406.07496), 2024. A general framework for textual feedback propagated through compound AI computation graphs. Its quotation marks around differentiation are mathematically important.

**LLM-10.** Aman Madaan et al. ["Self-Refine: Iterative Refinement with Self-Feedback"](https://arxiv.org/abs/2303.17651), NeurIPS 2023. A basic generate-feedback-refine loop that helps isolate what later systems add: persistent archives, code mutation, richer traces, and multi-objective selection.

**LLM-11.** Noah Shinn et al. ["Reflexion: Language Agents with Verbal Reinforcement Learning"](https://arxiv.org/abs/2303.11366), NeurIPS 2023. Stores verbal reflections in episodic memory to influence later attempts; a useful precursor to trace-mediated proposal systems.

**LLM-12.** Eric Zelikman et al. ["Self-Taught Optimizer (STOP): Recursively Self-Improving Code Generation"](https://arxiv.org/abs/2310.02304), COLM 2024. Applies an LM-infused improver to its own source and explicitly examines sandbox-bypass behavior.

**LLM-13.** Chengrun Yang et al. ["Large Language Models as Optimizers"](https://arxiv.org/abs/2309.03409), ICLR 2024. Introduces Optimization by PROmpting (OPRO), where solution history and objective values condition new candidates.

**LLM-14.** Chrisantha Fernando et al. ["Promptbreeder: Self-Referential Self-Improvement via Prompt Evolution"](https://arxiv.org/abs/2309.16797), ICML 2024. Evolves task prompts and mutation prompts, making the mutation policy itself part of the search state.

**LLM-15.** Bernardino Romera-Paredes et al. ["Mathematical Discoveries from Program Search with Large Language Models"](https://doi.org/10.1038/s41586-023-06924-6), *Nature* 625, 2024. FunSearch combines an LLM proposer with executable evaluation and an evolutionary database of programs.

**LLM-16.** Alexander Novikov et al. ["AlphaEvolve: A Gemini-Powered Coding Agent for Designing Advanced Algorithms"](https://arxiv.org/abs/2506.13131), 2025. Uses code generation, automated evaluators, and an evolutionary database for algorithm discovery and systems optimization.

**LLM-17.** Yecheng Jason Ma et al. ["Eureka: Human-Level Reward Design via Coding Large Language Models"](https://arxiv.org/abs/2310.12931), ICLR 2024. Evolves executable reward code using environment feedback, illustrating a mutable evaluator-adjacent artifact.

**LLM-18.** Guanzhi Wang et al. ["Voyager: An Open-Ended Embodied Agent with Large Language Models"](https://arxiv.org/abs/2305.16291), 2023. Builds a growing executable skill library with automatic curriculum and iterative code repair.

**LLM-19.** Shunyu Yao et al. ["ReAct: Synergizing Reasoning and Acting in Language Models"](https://arxiv.org/abs/2210.03629), ICLR 2023. Introduces interleaved reasoning and tool actions, one of the common inner-loop structures that a harness optimizer may select or rewrite.

**LLM-20.** Timo Schick et al. ["Toolformer: Language Models Can Teach Themselves to Use Tools"](https://arxiv.org/abs/2302.04761), NeurIPS 2023. Studies learned placement and use of API calls, an important precursor to optimizing the code/model boundary.

**LLM-21.** Luyu Gao et al. ["PAL: Program-Aided Language Models"](https://arxiv.org/abs/2211.10435), ICML 2023. Delegates deterministic computation to generated programs, directly motivating decompositions that reserve models for semantic uncertainty.

**LLM-22.** Shunyu Yao et al. ["Tree of Thoughts: Deliberate Problem Solving with Large Language Models"](https://arxiv.org/abs/2305.10601), NeurIPS 2023. Makes search structure explicit at inference time; useful for separating inner deliberation from outer program evolution.

**LLM-23.** Zhou et al. ["Language Agent Tree Search Unifies Reasoning, Acting, and Planning in Language Models"](https://arxiv.org/abs/2310.04406), ICML 2024. Combines tree search, environment feedback, and value estimation in an agent scaffold.

**LLM-24.** Arnav Singhvi et al. ["DSPy Assertions: Computational Constraints for Self-Refining Language Model Pipelines"](https://arxiv.org/abs/2312.13382), 2023. Introduces assertions that can trigger retry and self-refinement, but does not turn empirical compliance into formal proof.

**LLM-25.** Carlos E. Jimenez et al. ["SWE-bench: Can Language Models Resolve Real-World GitHub Issues?"](https://arxiv.org/abs/2310.06770), ICLR 2024. Defines a repository-level software-engineering benchmark and highlights the need for executable grading.

**LLM-26.** John Yang et al. ["SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering"](https://arxiv.org/abs/2405.15793), NeurIPS 2024. Shows that the harness/interface around a model materially changes coding performance.

**LLM-27.** Qian Huang et al. ["AgentCoder: Multi-Agent-Based Code Generation with Iterative Testing and Optimisation"](https://arxiv.org/abs/2312.13010), 2023. A representative generate-test-repair scaffold with specialized agent roles.

**LLM-28.** Maciej Besta et al. ["Graph of Thoughts: Solving Elaborate Problems with Large Language Models"](https://arxiv.org/abs/2308.09687), AAAI 2024. Generalizes linear and tree-shaped prompting to graph-structured transformations and aggregation.

## Genetic programming, evolutionary search, and quality diversity {-}

**EV-01.** John H. Holland. *Adaptation in Natural and Artificial Systems*. University of Michigan Press, 1975; MIT Press reprint, 1992. The foundational genetic-algorithm treatment of adaptation through selection and variation.

**EV-02.** David E. Goldberg. *Genetic Algorithms in Search, Optimization, and Machine Learning*. Addison-Wesley, 1989. Standard engineering introduction to representation, fitness, selection, crossover, and mutation.

**EV-03.** John R. Koza. *Genetic Programming: On the Programming of Computers by Means of Natural Selection*. MIT Press, 1992. The classic formulation of evolving executable syntax trees.

**EV-04.** Riccardo Poli, William B. Langdon, and Nicholas F. McPhee. [*A Field Guide to Genetic Programming*](http://www.gp-field-guide.org.uk/), 2008. Open textbook covering GP representations, operators, dynamics, bloat, and evaluation.

**EV-05.** Wolfgang Banzhaf et al. *Genetic Programming: An Introduction*. Morgan Kaufmann, 1998. Broad treatment of program representations and evolutionary operators.

**EV-06.** Kenneth A. De Jong. *Evolutionary Computation: A Unified Approach*. MIT Press, 2006. A careful account of evolutionary search as stochastic adaptation rather than biological metaphor alone.

**EV-07.** Kalyanmoy Deb et al. ["A Fast and Elitist Multiobjective Genetic Algorithm: NSGA-II"](https://doi.org/10.1109/4235.996017), *IEEE Transactions on Evolutionary Computation* 6(2), 2002. Canonical non-dominated sorting and crowding-distance selection.

**EV-08.** Jean-Baptiste Mouret and Jeff Clune. ["Illuminating Search Spaces by Mapping Elites"](https://arxiv.org/abs/1504.04909), 2015. Introduces MAP-Elites and behaviorally indexed archives.

**EV-09.** Justin K. Pugh, Lisa B. Soros, and Kenneth O. Stanley. ["Quality Diversity: A New Frontier for Evolutionary Computation"](https://doi.org/10.3389/frobt.2016.00040), *Frontiers in Robotics and AI* 3, 2016. Unifies optimization and diversity preservation.

**EV-10.** Joel Lehman and Kenneth O. Stanley. ["Abandoning Objectives: Evolution Through the Search for Novelty Alone"](https://doi.org/10.1162/EVCO_a_00025), *Evolutionary Computation* 19(2), 2011. Demonstrates the limitations of a single objective in deceptive spaces.

**EV-11.** Kenneth O. Stanley and Risto Miikkulainen. ["Evolving Neural Networks Through Augmenting Topologies"](https://doi.org/10.1162/106365602320169811), *Evolutionary Computation* 10(2), 2002. NEAT is relevant because it evolves both parameters and structure while protecting innovations.

**EV-12.** Stephanie Forrest et al. ["A Genetic Programming Approach to Automated Software Repair"](https://doi.org/10.1145/1569901.1570031), GECCO 2009. Evolves source patches against test suites and exposes the specification weakness of tests.

**EV-13.** Westley Weimer et al. ["Automatically Finding Patches Using Genetic Programming"](https://doi.org/10.1109/ICSE.2009.5070536), ICSE 2009. The GenProg line is the closest classical ancestor of test-driven program mutation.

**EV-14.** Nikolaus Hansen and Andreas Ostermeier. ["Completely Derandomized Self-Adaptation in Evolution Strategies"](https://doi.org/10.1162/106365601750190398), *Evolutionary Computation* 9(2), 2001. CMA-ES illustrates adaptation of a proposal distribution, useful when comparing language-conditioned mutation to learned search policies.

**EV-15.** Anne Auger and Benjamin Doerr, editors. *Theory of Randomized Search Heuristics*. World Scientific, 2011. Mathematical tools for analyzing stochastic search, drift, and runtime.

## Program synthesis, repair, and counterexample-guided refinement {-}

**SYN-01.** Sumit Gulwani, Oleksandr Polozov, and Rishabh Singh. ["Program Synthesis"](https://doi.org/10.1561/2500000010), *Foundations and Trends in Programming Languages* 4(1-2), 2017. The standard survey of specifications, search spaces, deductive methods, and practical synthesis.

**SYN-02.** Armando Solar-Lezama. [*Program Synthesis by Sketching*](https://people.csail.mit.edu/asolar/papers/thesis.pdf), PhD thesis, UC Berkeley, 2008. Develops partial programs with holes and constraint-based completion.

**SYN-03.** Armando Solar-Lezama et al. ["Combinatorial Sketching for Finite Programs"](https://doi.org/10.1145/1168857.1168907), ASPLOS 2006. A foundational Sketch paper.

**SYN-04.** Susmit Jha et al. ["Oracle-Guided Component-Based Program Synthesis"](https://doi.org/10.1109/ICSE.2010.5489505), ICSE 2010. Gives an early explicit counterexample-guided inductive synthesis architecture.

**SYN-05.** Rajeev Alur et al. ["Syntax-Guided Synthesis"](https://ieeexplore.ieee.org/document/6679385), FMCAD 2013. Separates a semantic specification from a grammar restricting admissible implementations.

**SYN-06.** Nadia Polikarpova, Ivan Kuraj, and Armando Solar-Lezama. ["Program Synthesis from Polymorphic Refinement Types"](https://doi.org/10.1145/2908080.2908093), PLDI 2016. Synquid demonstrates proof-directed search in a refinement-typed language.

**SYN-07.** Peter-Michael Osera and Steve Zdancewic. ["Type-and-Example-Directed Program Synthesis"](https://doi.org/10.1145/2737924.2738007), PLDI 2015. Combines type structure with input-output examples to prune synthesis.

**SYN-08.** Sumit Gulwani. ["Automating String Processing in Spreadsheets Using Input-Output Examples"](https://doi.org/10.1145/1926385.1926423), POPL 2011. FlashFill is a landmark example of domain-specific synthesis with a carefully designed DSL.

**SYN-09.** Rajeev Alur et al. ["Scaling Enumerative Program Synthesis via Divide and Conquer"](https://doi.org/10.1007/978-3-662-54580-5_18), TACAS 2017. Shows how decomposition changes synthesis complexity.

**SYN-10.** Hoang Duong Thien Nguyen et al. ["SemFix: Program Repair via Semantic Analysis"](https://doi.org/10.1109/ICSE.2013.6606623), ICSE 2013. Uses symbolic execution and constraint solving to synthesize repairs.

**SYN-11.** Sergey Mechtaev, Jooyong Yi, and Abhik Roychoudhury. ["Angelix: Scalable Multiline Program Patch Synthesis via Symbolic Analysis"](https://doi.org/10.1145/2884781.2884807), ICSE 2016. Combines fault localization, symbolic reasoning, and patch synthesis.

**SYN-12.** Fan Long and Martin Rinard. ["Automatic Patch Generation by Learning Correct Code"](https://doi.org/10.1145/2837614.2837617), POPL 2016. Prophet learns a ranking model over candidate patches, illustrating the distinction between candidate generation and selection.

**SYN-13.** Johannes Bader et al. ["Getafix: Learning to Fix Bugs Automatically"](https://doi.org/10.1145/3360585), *Proceedings of the ACM on Programming Languages* 3(OOPSLA), 2019. Mines human patches into hierarchical transformation patterns.

**SYN-14.** Claire Le Goues et al. ["The ManyBugs and IntroClass Benchmarks for Automated Repair of C Programs"](https://doi.org/10.1109/TSE.2015.2454513), *IEEE Transactions on Software Engineering* 41(12), 2015. Benchmark methodology for repair systems.

**SYN-15.** Martin Monperrus. ["Automatic Software Repair: A Bibliography"](https://doi.org/10.1145/3105906), *ACM Computing Surveys* 51(1), 2018. Broad map of repair approaches and evaluation pitfalls.

**SYN-16.** Yu Pei et al. ["Automated Fixing of Programs with Contracts"](https://doi.org/10.1109/TSE.2013.19), *IEEE Transactions on Software Engineering* 40(5), 2014. Uses contracts as repair oracles, closer to the hard-admissibility layer advocated here.

**SYN-17.** Tom Schrijvers et al. ["Search Combinators"](https://doi.org/10.1017/S0956796813000091), *Journal of Functional Programming* 23(5), 2013. A compositional language for controlling search, relevant to typed optimizer policies.

**SYN-18.** Emina Torlak and Rastislav Bodik. ["Growing Solver-Aided Languages with Rosette"](https://doi.org/10.1145/2666356.2594340), Onward! 2013. Shows how host languages can expose solver-backed verification and synthesis through a disciplined semantic layer.

## Category theory, effects, probability, feedback, and rewrites {-}

**CAT-01.** Saunders Mac Lane. *Categories for the Working Mathematician*, second edition. Springer, 1998. The classical reference for categories, functors, natural transformations, adjunctions, limits, and monoidal structure.

**CAT-02.** Steve Awodey. *Category Theory*, second edition. Oxford University Press, 2010. A concise route from universal properties to categorical logic.

**CAT-03.** Emily Riehl. [*Category Theory in Context*](https://math.jhu.edu/~eriehl/context.pdf). Dover, 2016. Freely available, rigorous, and especially strong on universal constructions and adjunctions.

**CAT-04.** Brendan Fong and David I. Spivak. [*An Invitation to Applied Category Theory: Seven Sketches in Compositionality*](https://arxiv.org/abs/1803.05316). Cambridge University Press, 2019. The most directly useful applied-category-theory text for programmers.

**CAT-05.** David I. Spivak. *Category Theory for the Sciences*. MIT Press, 2014. Develops schemas, ologs, databases, and compositional modeling.

**CAT-06.** Bartosz Milewski. [*Category Theory for Programmers*](https://github.com/hmemcpy/milewski-ctfp-pdf), 2018. Programmer-oriented exposition; pair it with a formal text for proof details.

**CAT-07.** Benjamin C. Pierce. *Basic Category Theory for Computer Scientists*. MIT Press, 1991. Compact bridge between categorical concepts and programming-language semantics.

**CAT-08.** Michael Barr and Charles Wells. [*Category Theory for Computing Science*](https://www.math.mcgill.ca/triples/Barr-Wells-ctcs.pdf), third edition, 1999. Broad computer-science reference.

**CAT-09.** John C. Baez and Mike Stay. ["Physics, Topology, Logic and Computation: A Rosetta Stone"](https://arxiv.org/abs/0903.0340), 2011. Relates monoidal categories, proofs, processes, and computation through string diagrams.

**CAT-10.** Eugenio Moggi. ["Notions of Computation and Monads"](https://doi.org/10.1016/0890-5401(91)90052-4), *Information and Computation* 93(1), 1991. The foundational semantics of computational effects via monads.

**CAT-11.** Philip Wadler. ["The Essence of Functional Programming"](https://doi.org/10.1145/143165.143169), POPL 1992. Makes monadic programming concrete in a functional language.

**CAT-12.** Gordon Plotkin and John Power. ["Algebraic Operations and Generic Effects"](https://doi.org/10.1023/A:1023064908962), *Applied Categorical Structures* 11, 2003. Separates algebraic operations from handlers and models effects compositionally.

**CAT-13.** Gordon Plotkin and Matija Pretnar. ["Handling Algebraic Effects"](https://doi.org/10.2168/LMCS-9(4:23)2013), *Logical Methods in Computer Science* 9(4), 2013. A core reference for effect handlers.

**CAT-14.** Robert Atkey. ["Parameterised Notions of Computation"](https://doi.org/10.1017/S095679680800728X), *Journal of Functional Programming* 19(3-4), 2009. Introduces parameterized monads, useful when pre- and post-state indices matter.

**CAT-15.** Shin-ya Katsumata. ["Parametric Effect Monads and Semantics of Effect Systems"](https://doi.org/10.1145/2535838.2535846), POPL 2014. Connects effect systems and graded/parameterized semantic structures.

**CAT-16.** Dominic Orchard, Vilem-Benjamin Liepelt, and Harley Eades III. ["Quantitative Program Reasoning with Graded Modal Types"](https://doi.org/10.1145/3371119), *Proceedings of the ACM on Programming Languages* 3(ICFP), 2019. Develops grades as quantitative modalities.

**CAT-17.** Jean-Yves Girard. ["Linear Logic"](https://doi.org/10.1016/0304-0208(87)90045-4), *Theoretical Computer Science* 50, 1987. Foundational resource-sensitive logic.

**CAT-18.** Nick Benton. ["A Mixed Linear and Non-Linear Logic: Proofs, Terms and Models"](https://doi.org/10.1007/BFb0022861), CSL 1994. A categorical bridge between ordinary and resource-sensitive computation.

**CAT-19.** Tobias Fritz. ["A Synthetic Approach to Markov Kernels, Conditional Independence and theorems on Sufficient Statistics"](https://doi.org/10.1016/j.aim.2020.107239), *Advances in Mathematics* 370, 2020. Develops Markov categories as a compositional language for stochastic systems.

**CAT-20.** Kenta Cho and Bart Jacobs. ["Disintegration and Bayesian Inversion via String Diagrams"](https://doi.org/10.1017/S0960129518000488), *Mathematical Structures in Computer Science* 29(7), 2019. Graphical treatment of conditioning and Bayesian inversion.

**CAT-21.** Bart Jacobs. *Introduction to Coalgebra: Towards Mathematics of States and Observation*. Cambridge University Press, 2016. A systematic account of state-based and potentially infinite behavior.

**CAT-22.** Jan Rutten. ["Universal Coalgebra: A Theory of Systems"](https://doi.org/10.1016/S0304-3975(00)00056-6), *Theoretical Computer Science* 249(1), 2000. Classic survey of coalgebra, bisimulation, and final semantics.

**CAT-23.** André Joyal, Ross Street, and Dominic Verity. ["Traced Monoidal Categories"](https://doi.org/10.1017/S0305004100074338), *Mathematical Proceedings of the Cambridge Philosophical Society* 119(3), 1996. Axiomatizes feedback in monoidal categories.

**CAT-24.** Stephen L. Bloom and Zoltán Ésik. *Iteration Theories*. Springer, 1993. Algebraic laws for fixed points and iteration.

**CAT-25.** Brendan Fong, David Spivak, and Rémy Tuyéras. ["Backprop as Functor: A Compositional Perspective on Supervised Learning"](https://arxiv.org/abs/1711.10455), LICS 2019. Models learners and backpropagation compositionally.

**CAT-26.** Geoffrey Cruttwell et al. ["Categorical Foundations of Gradient-Based Learning"](https://arxiv.org/abs/2103.01931), ESOP 2022. Develops reverse derivative categories and clarifies which algebraic laws make gradients compositional.

**CAT-27.** Mitchell Riley. ["Categories of Optics"](https://arxiv.org/abs/1809.00738), 2018. A general categorical account of lenses, prisms, and related bidirectional structures.

**CAT-28.** Matthew Pickering, Jeremy Gibbons, and Nicolas Wu. ["Profunctor Optics: Modular Data Accessors"](https://doi.org/10.22152/programming-journal.org/2017/1/7), *The Art, Science, and Engineering of Programming* 1(2), 2017. Practical algebra of composable data access and updates.

**CAT-29.** David I. Spivak. ["The Operad of Wiring Diagrams: Formalizing a Graphical Language for Databases, Recursion, and Plug-and-Play Circuits"](https://arxiv.org/abs/1305.0297), 2013. Operadic syntax for composing architectures.

**CAT-30.** Michael Shulman. ["Framed Bicategories and Monoidal Fibrations"](https://www.tac.mta.ca/tac/volumes/20/18/20-18abs.html), *Theory and Applications of Categories* 20, 2008. A rigorous source for double-categorical structures and horizontal/vertical composition.

**CAT-31.** Tom Leinster. [*Basic Bicategories*](https://arxiv.org/abs/math/9810017), 1998. Compact introduction to bicategories and 2-cells.

**CAT-32.** Jean Bénabou. ["Introduction to Bicategories"](https://doi.org/10.1007/BFb0074299), 1967. Foundational source for weak two-dimensional composition.

**CAT-33.** F. William Lawvere. ["Metric Spaces, Generalized Logic, and Closed Categories"](https://www.tac.mta.ca/tac/reprints/articles/1/tr1abs.html), 1973; *Theory and Applications of Categories* reprint, 2002. The source for viewing generalized metrics as enrichment over ordered monoids.

**CAT-34.** G. M. Kelly. [*Basic Concepts of Enriched Category Theory*](https://www.tac.mta.ca/tac/reprints/articles/10/tr10abs.html), 1982; reprint 2005. Standard reference for order- and metric-enriched categories.

**CAT-35.** Peter Selinger. ["A Survey of Graphical Languages for Monoidal Categories"](https://arxiv.org/abs/0908.3347), 2011. A practical guide to string-diagram syntax and its soundness.

**CAT-36.** David I. Spivak, Patrick Schultz, and Dylan Rupel. ["String Diagrams for Traced and Compact Categories Are Oriented 1-Cobordisms"](https://arxiv.org/abs/1508.01069), 2015. Relates diagrams, systems, and behavior; useful for treating traces as semantic evidence.

**CAT-37.** Daniel R. Licata and Robert Harper. ["2-Dimensional Directed Type Theory"](https://doi.org/10.1016/j.entcs.2011.09.026), *Electronic Notes in Theoretical Computer Science* 276, 2011. A bridge from categorical directionality to a type theory of transformations.

## Dependent types, refinement, verification, and proof-carrying code {-}

**TYPE-01.** Per Martin-Löf. *Intuitionistic Type Theory*. Bibliopolis, 1984. Foundational dependent type theory.

**TYPE-02.** Bengt Nordström, Kent Petersson, and Jan M. Smith. [*Programming in Martin-Löf's Type Theory*](http://www.cse.chalmers.se/research/group/logic/book/), Oxford University Press, 1990. A programming-oriented account of constructive type theory.

**TYPE-03.** Thierry Coquand and Gérard Huet. ["The Calculus of Constructions"](https://doi.org/10.1016/0890-5401(88)90005-3), *Information and Computation* 76, 1988. A core dependent calculus underlying proof assistants.

**TYPE-04.** Haskell B. Curry and Robert Feys. *Combinatory Logic*, Volume I. North-Holland, 1958. One historical root of the propositions-as-types correspondence.

**TYPE-05.** William A. Howard. ["The Formulae-as-Types Notion of Construction"](https://doi.org/10.1016/S0049-237X(08)71941-0), written 1969, published 1980. The canonical statement of the correspondence now called Curry-Howard.

**TYPE-06.** Philip Wadler. ["Propositions as Types"](https://doi.org/10.1145/2699407), *Communications of the ACM* 58(12), 2015. Accessible modern exposition.

**TYPE-07.** Benjamin C. Pierce. *Types and Programming Languages*. MIT Press, 2002. Standard text on operational semantics and type systems.

**TYPE-08.** Robert Harper. [*Practical Foundations for Programming Languages*](https://www.cs.cmu.edu/~rwh/pfpl/), second edition, Cambridge University Press, 2016. Systematic type-theoretic account of programming languages.

**TYPE-09.** Simon Thompson. *Type Theory and Functional Programming*. Addison-Wesley, 1991. An accessible bridge from functional programs to constructive proof.

**TYPE-10.** Leonardo de Moura and Sebastian Ullrich. ["The Lean 4 Theorem Prover and Programming Language"](https://doi.org/10.1007/978-3-030-79876-5_37), CADE 2021. Describes Lean 4's kernel, elaborator, metaprogramming, and runtime.

**TYPE-11.** Lean community. [*Theorem Proving in Lean 4*](https://lean-lang.org/theorem_proving_in_lean4/) and [*Functional Programming in Lean*](https://lean-lang.org/functional_programming_in_lean/). Official, executable introductions.

**TYPE-12.** Yves Bertot and Pierre Castéran. [*Interactive Theorem Proving and Program Development: Coq'Art*](https://doi.org/10.1007/978-3-662-07964-5). Springer, 2004. Foundational Coq textbook.

**TYPE-13.** Adam Chlipala. [*Certified Programming with Dependent Types*](http://adam.chlipala.net/cpdt/). MIT Press, 2013. Proof engineering and verified programming in Coq.

**TYPE-14.** Ulf Norell. ["Dependently Typed Programming in Agda"](https://www.cse.chalmers.se/~ulfn/papers/afp08/tutorial.pdf), AFP 2008. Practical Agda introduction.

**TYPE-15.** Edwin Brady. ["Idris 2: Quantitative Type Theory in Practice"](https://doi.org/10.4230/LIPIcs.ECOOP.2021.9), ECOOP 2021. Combines dependent types with quantitative usage information.

**TYPE-16.** Niki Vazou et al. ["Refinement Types for Haskell"](https://doi.org/10.1145/2628136.2628161), ICFP 2014. Liquid Haskell integrates SMT-backed refinements with a general-purpose language.

**TYPE-17.** Patrick M. Rondon, Ming Kawaguchi, and Ranjit Jhala. ["Liquid Types"](https://doi.org/10.1145/1375581.1375602), PLDI 2008. Establishes predicate abstraction as a route to decidable refinement inference.

**TYPE-18.** Niki Vazou et al. ["Refinement Reflection: Complete Verification with SMT"](https://doi.org/10.1145/3158141), *Proceedings of the ACM on Programming Languages* 2(POPL), 2018. Makes reflected definitions available to refinement proofs.

**TYPE-19.** Nadia Polikarpova et al. Synquid, cited as SYN-06. Read from the type-theory side for proof-directed synthesis and from the synthesis side for search pruning.

**TYPE-20.** Daan Leijen. ["Koka: Programming with Row-Polymorphic Effect Types"](https://www.microsoft.com/en-us/research/publication/koka-programming-with-row-polymorphic-effect-types/), 2014. Practical effect typing with inferred effect rows.

**TYPE-21.** Daan Leijen. ["Type Directed Compilation of Row-Typed Algebraic Effects"](https://doi.org/10.1145/3009837.3009872), POPL 2017. Connects algebraic-effect typing to efficient implementation.

**TYPE-22.** Danel Ahman et al. ["Dijkstra Monads for Free"](https://arxiv.org/abs/1608.06499), POPL 2017. Derives weakest-precondition calculi from monadic semantics.

**TYPE-23.** Nikhil Swamy et al. ["Dependent Types and Multi-Monadic Effects in F*"](https://doi.org/10.1145/2837614.2837655), POPL 2016. A practical verification system for effectful programs.

**TYPE-24.** C. A. R. Hoare. ["An Axiomatic Basis for Computer Programming"](https://doi.org/10.1145/363235.363259), *Communications of the ACM* 12(10), 1969. Introduces Hoare triples.

**TYPE-25.** Robert W. Floyd. "Assigning Meanings to Programs." In *Mathematical Aspects of Computer Science*, AMS, 1967. Early inductive-assertion method.

**TYPE-26.** Edsger W. Dijkstra. ["Guarded Commands, Nondeterminacy and Formal Derivation of Programs"](https://doi.org/10.1145/360933.360975), *Communications of the ACM* 18(8), 1975. Develops weakest preconditions and calculational program derivation.

**TYPE-27.** John C. Reynolds. ["Separation Logic: A Logic for Shared Mutable Data Structures"](https://doi.org/10.1109/LICS.2002.1029817), LICS 2002. Local reasoning for heap-manipulating programs.

**TYPE-28.** Peter O'Hearn. ["Resources, Concurrency, and Local Reasoning"](https://doi.org/10.1016/j.tcs.2006.12.035), *Theoretical Computer Science* 375, 2007. Connects separation logic to resource semantics.

**TYPE-29.** Ralf Jung et al. ["Iris: Monoids and Invariants as an Orthogonal Basis for Concurrent Reasoning"](https://doi.org/10.1145/2818638), POPL 2015. A higher-order concurrent separation logic suitable for modular proof.

**TYPE-30.** George C. Necula. ["Proof-Carrying Code"](https://doi.org/10.1145/263699.263712), POPL 1997. Establishes the producer-supplies-proof, consumer-checks-proof architecture.

**TYPE-31.** Greg Morrisett et al. ["From System F to Typed Assembly Language"](https://doi.org/10.1145/289423.289462), POPL 1998. Shows how safety evidence can survive compilation to low-level code.

**TYPE-32.** Xavier Leroy. ["Formal Verification of a Realistic Compiler"](https://doi.org/10.1145/1538788.1538814), *Communications of the ACM* 52(7), 2009. Overview of CompCert and proof-preserving compilation.

**TYPE-33.** Amir Pnueli, Michael Siegel, and Eli Singerman. ["Translation Validation"](https://doi.org/10.1007/BFb0054170), TACAS 1998. Validates each translation result rather than proving the translator itself.

**TYPE-34.** K. Rustan M. Leino. ["Dafny: An Automatic Program Verifier for Functional Correctness"](https://doi.org/10.1007/978-3-642-17511-4_20), LPAR 2010. Combines contracts, SMT automation, and executable code.

**TYPE-35.** Jean-Christophe Filliâtre and Andrei Paskevich. ["Why3 - Where Programs Meet Provers"](https://doi.org/10.1007/978-3-642-37036-6_8), ESOP 2013. Intermediate verification language targeting multiple provers.

**TYPE-36.** Patrick Cousot and Radhia Cousot. ["Abstract Interpretation: A Unified Lattice Model for Static Analysis"](https://doi.org/10.1145/512950.512973), POPL 1977. The foundation for sound approximation and static analysis.

**TYPE-37.** Edmund M. Clarke, Orna Grumberg, and Doron Peled. *Model Checking*. MIT Press, 1999. Finite-state temporal verification and counterexample generation.

**TYPE-38.** Leslie Lamport. [*Specifying Systems: The TLA+ Language and Tools for Hardware and Software Engineers*](https://lamport.azurewebsites.net/tla/book.html). Addison-Wesley, 2002. State-machine specifications and refinement for concurrent systems.

**TYPE-39.** Robert Bruce Findler and Matthias Felleisen. ["Contracts for Higher-Order Functions"](https://doi.org/10.1145/581478.581484), ICFP 2002. Blame-aware run-time contracts for higher-order programs.

**TYPE-40.** Gerwin Klein et al. ["seL4: Formal Verification of an OS Kernel"](https://doi.org/10.1145/1629575.1629596), SOSP 2009. Demonstrates end-to-end machine-checked assurance at systems scale.

## Homotopy type theory, univalence, and direction {-}

**HOTT-01.** The Univalent Foundations Program. [*Homotopy Type Theory: Univalent Foundations of Mathematics*](https://homotopytypetheory.org/book/), Institute for Advanced Study, 2013. The central textbook for identity as paths, univalence, higher inductive types, and truncation.

**HOTT-02.** Martin Hofmann and Thomas Streicher. ["The Groupoid Interpretation of Type Theory"](https://doi.org/10.1090/conm/228/03319), 1998. Shows that identity proofs can carry nontrivial structure rather than collapsing to proof irrelevance.

**HOTT-03.** Steve Awodey and Michael A. Warren. ["Homotopy Theoretic Models of Identity Types"](https://doi.org/10.1017/S0305004108001783), *Mathematical Proceedings of the Cambridge Philosophical Society* 146(1), 2009. Connects intensional identity types to homotopy-theoretic path objects.

**HOTT-04.** Vladimir Voevodsky. ["Univalent Foundations of Mathematics"](https://www.math.ias.edu/vladimir/sites/math.ias.edu.vladimir/files/2014_04_29_univalent_foundations.pdf), 2014 lecture notes. Motivation and overview from the originator of the univalence program.

**HOTT-05.** Cyril Cohen, Thierry Coquand, Simon Huber, and Anders Mörtberg. ["Cubical Type Theory: A Constructive Interpretation of the Univalence Axiom"](https://arxiv.org/abs/1611.02108), TYPES 2015 / LIPIcs 2018. Gives computational content to paths and univalence.

**HOTT-06.** Thierry Coquand, Simon Huber, and Anders Mörtberg. ["On Higher Inductive Types in Cubical Type Theory"](https://arxiv.org/abs/1802.01170), LICS 2018. Computational treatment of higher inductive types.

**HOTT-07.** Benedikt Ahrens, Krzysztof Kapulkin, and Michael Shulman. ["Univalent Categories and the Rezk Completion"](https://doi.org/10.1017/S0960129514000486), *Mathematical Structures in Computer Science* 25(5), 2015. Applies univalence to categories and clarifies equality versus equivalence of objects.

**HOTT-08.** Emily Riehl and Michael Shulman. ["A Type Theory for Synthetic Infinity-Categories"](https://arxiv.org/abs/1705.07442), *Higher Structures* 1(1), 2017. Develops directed structure inside type theory using shapes and extension types.

**HOTT-09.** Daniel R. Licata and Robert Harper. "2-Dimensional Directed Type Theory," cited as CAT-37. A direct precursor for modeling transformations that are not invertible.

**HOTT-10.** Daniel R. Licata and Michael Shulman. ["Calculating the Fundamental Group of the Circle in Homotopy Type Theory"](https://doi.org/10.1109/LICS.2013.28), LICS 2013. A compact worked example of higher-inductive reasoning.

**HOTT-11.** Egbert Rijke, Michael Shulman, and Bas Spitters. ["Modalities in Homotopy Type Theory"](https://arxiv.org/abs/1706.07526), *Logical Methods in Computer Science* 16(1), 2020. Systematic treatment of reflective subuniverses and information-forgetting modalities.

**HOTT-12.** Carlo Angiuli, Robert Harper, and Todd Wilson. ["Computational Higher Type Theory I: Abstract Cubical Realizability"](https://doi.org/10.1145/2951919.2951921), POPL 2017. Computational semantics for higher-dimensional type theory.

**HOTT-13.** Guillaume Brunerie. [*On the Homotopy Groups of Spheres in Homotopy Type Theory*](https://arxiv.org/abs/1606.05916), PhD thesis, 2016. Demonstrates substantial machine-assisted mathematics inside HoTT.

**HOTT-14.** UniMath community. [UniMath library](https://github.com/UniMath/UniMath). A large Coq development based on univalent foundations, useful for studying proof engineering at scale.

**HOTT-15.** Cubical Agda community. [Cubical Agda library and documentation](https://agda.github.io/cubical/). Executable examples of paths, equivalences, univalence, and higher inductive types.

**HOTT-16.** Jonathan Sterling and Carlo Angiuli. ["Normalization for Cubical Type Theory"](https://arxiv.org/abs/2101.11479), LICS 2021. Metatheory relevant to trustworthy computation with cubical paths.

**HOTT-17.** Ulrik Buchholtz and Jonathan Weinberger. ["Synthetic Fibered (Infinity,1)-Category Theory"](https://arxiv.org/abs/2105.01724), *Higher Structures* 7(1), 2023. Develops directed categorical structures internally; useful for version graphs and indexed architecture families.

**HOTT-18.** Peter LeFanu Lumsdaine and Michael Shulman. ["Semantics of Higher Inductive Types"](https://doi.org/10.1017/S096012951700015X), *Mathematical Structures in Computer Science* 29(5), 2019. Semantic foundations for freely generated points, paths, and higher coherences.

## LLM judges, Goodhart effects, uncertainty, and experimental design {-}

**EVAL-01.** Lianmin Zheng et al. ["Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena"](https://arxiv.org/abs/2306.05685), NeurIPS 2023. Establishes common pairwise and single-answer judge protocols and documents position, verbosity, and self-enhancement biases.

**EVAL-02.** Yang Liu et al. ["G-Eval: NLG Evaluation Using GPT-4 with Better Human Alignment"](https://arxiv.org/abs/2303.16634), EMNLP 2023. Uses structured criteria and chain-of-thought-style evaluation forms.

**EVAL-03.** Peiyi Wang et al. ["Large Language Models Are Not Fair Evaluators"](https://arxiv.org/abs/2305.17926), ACL 2024. Studies order sensitivity and proposes calibration strategies.

**EVAL-04.** Rickard Stureborg et al. ["Large Language Models Are Inconsistent and Biased Evaluators"](https://arxiv.org/abs/2405.01724), 2024. Examines variability and systematic bias across evaluation settings.

**EVAL-05.** Arjun Panickssery et al. ["LLM Evaluators Recognize and Favor Their Own Generations"](https://arxiv.org/abs/2404.13076), NeurIPS 2024. Evidence for self-preference that matters when proposer and judge share a model family.

**EVAL-06.** Xinyang Yu et al. ["JudgeBench: A Benchmark for Evaluating LLM-Based Judges"](https://arxiv.org/abs/2410.12784), 2024. Tests judges on challenging pairwise comparisons and adversarial cases.

**EVAL-07.** Samuel Gehman et al. ["RealToxicityPrompts: Evaluating Neural Toxic Degeneration in Language Models"](https://arxiv.org/abs/2009.11462), Findings of EMNLP 2020. Illustrates benchmark construction for a soft but consequential property.

**EVAL-08.** David Manheim and Scott Garrabrant. ["Categorizing Variants of Goodhart's Law"](https://arxiv.org/abs/1803.04585), 2018. Distinguishes regressional, extremal, causal, and adversarial failures.

**EVAL-09.** Charles Goodhart. "Problems of Monetary Management: The U.K. Experience." In *Papers in Monetary Economics*, Reserve Bank of Australia, 1975. Historical source of Goodhart's law.

**EVAL-10.** Donald T. Campbell. "Assessing the Impact of Planned Social Change." *Evaluation and Program Planning* 2(1), 1979. Campbell's law emphasizes corruption of indicators under decision pressure.

**EVAL-11.** James E. Smith and Robert L. Winkler. ["The Optimizer's Curse: Skepticism and Postdecision Surprise in Decision Analysis"](https://doi.org/10.1287/mnsc.1050.0451), *Management Science* 52(3), 2006. Formalizes selection-induced optimism among noisy alternatives.

**EVAL-12.** Edwin B. Wilson. ["Probable Inference, the Law of Succession, and Statistical Inference"](https://doi.org/10.1080/01621459.1927.10502953), *Journal of the American Statistical Association* 22, 1927. Source of the Wilson binomial interval used in the Flex report.

**EVAL-13.** Quinn McNemar. ["Note on the Sampling Error of the Difference Between Correlated Proportions or Percentages"](https://doi.org/10.1007/BF02295996), *Psychometrika* 12, 1947. Paired binary-outcome test appropriate for comparing two classifiers on the same examples.

**EVAL-14.** Bradley Efron and Robert Tibshirani. *An Introduction to the Bootstrap*. Chapman and Hall/CRC, 1993. Standard resampling reference.

**EVAL-15.** Thomas G. Dietterich. ["Approximate Statistical Tests for Comparing Supervised Classification Learning Algorithms"](https://doi.org/10.1162/089976698300017197), *Neural Computation* 10(7), 1998. Explains dependence and variance problems in classifier comparisons.

**EVAL-16.** Janez Demšar. ["Statistical Comparisons of Classifiers over Multiple Data Sets"](https://jmlr.org/papers/v7/demsar06a.html), *Journal of Machine Learning Research* 7, 2006. Nonparametric comparison procedures across tasks.

**EVAL-17.** Yoav Benjamini and Yosef Hochberg. ["Controlling the False Discovery Rate"](https://doi.org/10.1111/j.2517-6161.1995.tb02031.x), *Journal of the Royal Statistical Society B* 57(1), 1995. Multiple-comparison control relevant to broad candidate sweeps.

**EVAL-18.** Glenn W. Brier. ["Verification of Forecasts Expressed in Terms of Probability"](https://doi.org/10.1175/1520-0493(1950)078%3C0001:VOFEIT%3E2.0.CO;2), *Monthly Weather Review* 78, 1950. Introduces the Brier score for probabilistic calibration.

**EVAL-19.** Morris H. DeGroot and Stephen E. Fienberg. ["The Comparison and Evaluation of Forecasters"](https://doi.org/10.2307/2987588), *The Statistician* 32, 1983. Calibration and refinement decomposition.

**EVAL-20.** Yonatan Geifman and Ran El-Yaniv. ["Selective Classification for Deep Neural Networks"](https://arxiv.org/abs/1705.08500), NeurIPS 2017. Formalizes risk-coverage tradeoffs for abstaining systems.

**EVAL-21.** Vladimir Vovk, Alexander Gammerman, and Glenn Shafer. *Algorithmic Learning in a Random World*. Springer, 2005. Foundational conformal prediction.

**EVAL-22.** Anastasios N. Angelopoulos and Stephen Bates. ["A Gentle Introduction to Conformal Prediction and Distribution-Free Uncertainty Quantification"](https://arxiv.org/abs/2107.07511), 2021. Practical modern tutorial.

**EVAL-23.** Cynthia Dwork et al. ["The Reusable Holdout: Preserving Validity in Adaptive Data Analysis"](https://doi.org/10.1126/science.aaa9375), *Science* 349(6248), 2015. Shows how adaptive reuse of evaluation data invalidates ordinary generalization assumptions and gives a privacy-based remedy.

**EVAL-24.** Avrim Blum and Moritz Hardt. ["The Ladder: A Reliable Leaderboard for Machine Learning Competitions"](https://arxiv.org/abs/1502.04585), ICML 2015. Introduces mechanisms limiting leaderboard overfitting.

**EVAL-25.** Daniel Russo and James Zou. ["How Much Does Your Data Exploration Overfit? Controlling Bias via Information Usage"](https://doi.org/10.1109/TIT.2019.2945779), *IEEE Transactions on Information Theory* 66(1), 2020. Information-theoretic analysis of adaptivity and selection bias.

**EVAL-26.** Peter Grünwald and A. Philip Dawid. ["Game Theory, Maximum Entropy, Minimum Discrepancy and Robust Bayesian Decision Theory"](https://doi.org/10.1214/009053604000000571), *Annals of Statistics* 32(4), 2004. Connects proper scoring rules and decision-theoretic evaluation.

**EVAL-27.** NIST. [*Artificial Intelligence Risk Management Framework (AI RMF 1.0)*](https://www.nist.gov/itl/ai-risk-management-framework), 2023. Governance framework for mapping, measuring, managing, and documenting AI risk.

## Sandboxing, capabilities, provenance, and reproducible artifacts {-}

**SYS-01.** Jerome H. Saltzer and Michael D. Schroeder. ["The Protection of Information in Computer Systems"](https://doi.org/10.1109/PROC.1975.9939), *Proceedings of the IEEE* 63(9), 1975. Source of least privilege, complete mediation, economy of mechanism, and related design principles.

**SYS-02.** Butler W. Lampson. ["Protection"](https://doi.org/10.1145/361011.361067), *Operating Systems Review* 8(1), 1974; originally 1971. Access-control matrix and protection-domain foundations.

**SYS-03.** Dorothy E. Denning. ["A Lattice Model of Secure Information Flow"](https://doi.org/10.1145/360051.360056), *Communications of the ACM* 19(5), 1976. Formal basis for information-flow policies.

**SYS-04.** Andrei Sabelfeld and Andrew C. Myers. ["Language-Based Information-Flow Security"](https://doi.org/10.1109/JSAC.2002.806121), *IEEE Journal on Selected Areas in Communications* 21(1), 2003. Survey of noninterference and language enforcement.

**SYS-05.** Mark S. Miller. [*Robust Composition: Towards a Unified Approach to Access Control and Concurrency Control*](http://www.erights.org/talks/thesis/), PhD thesis, Johns Hopkins University, 2006. Capability-oriented composition under mutual distrust.

**SYS-06.** David Wagner and Dean Tribble. ["A Security Analysis of the Combex DarpaBrowser Architecture"](http://www.erights.org/talks/browser/), 2002. Concrete object-capability analysis.

**SYS-07.** Robert Watson et al. ["Capsicum: Practical Capabilities for UNIX"](https://www.usenix.org/legacy/events/sec10/tech/full_papers/Watson.pdf), USENIX Security 2010. Capability mode and fine-grained rights for sandboxing applications.

**SYS-08.** Bennet Yee et al. ["Native Client: A Sandbox for Portable, Untrusted x86 Native Code"](https://research.google/pubs/native-client-a-sandbox-for-portable-untrusted-x86-native-code/), IEEE Symposium on Security and Privacy 2009. Software validation plus process isolation for untrusted code.

**SYS-09.** Robert Wahbe et al. ["Efficient Software-Based Fault Isolation"](https://doi.org/10.1145/168619.168635), SOSP 1993. Foundational software fault isolation.

**SYS-10.** Andreas Rossberg. ["WebAssembly Core Specification"](https://www.w3.org/TR/wasm-core-2/), W3C Recommendation. A compact, typed, sandbox-oriented bytecode semantics suitable for restricted generated components.

**SYS-11.** W3C Provenance Working Group. [*PROV-DM: The PROV Data Model*](https://www.w3.org/TR/prov-dm/), 2013. Standard vocabulary for entities, activities, agents, derivations, and attribution.

**SYS-12.** Supply-chain Levels for Software Artifacts. [SLSA specification](https://slsa.dev/spec/), OpenSSF. Defines provenance and build-integrity levels for software artifacts.

**SYS-13.** in-toto project. ["in-toto: Providing Farm-to-Table Guarantees for Bits and Bytes"](https://www.usenix.org/conference/usenixsecurity19/presentation/torres-arias), USENIX Security 2019. Cryptographically records and verifies software-supply-chain steps.

**SYS-14.** Reproducible Builds project. [Documentation and practices](https://reproducible-builds.org/docs/). Techniques for making build outputs independently reproducible.

**SYS-15.** Ross Tate et al. ["Equality Saturation: A New Approach to Optimization"](https://doi.org/10.1145/1480881.1480915), POPL 2009. Represents many equivalent rewrites simultaneously and extracts according to a cost model.

**SYS-16.** Max Willsey et al. ["egg: Fast and Extensible Equality Saturation"](https://doi.org/10.1145/3434304), *Proceedings of the ACM on Programming Languages* 5(POPL), 2021. Practical e-graphs for rewrite systems and cost-based extraction.

**SYS-17.** Chris Lattner et al. ["MLIR: Scaling Compiler Infrastructure for Domain Specific Computation"](https://doi.org/10.1109/CGO51591.2021.9370308), CGO 2021. Multi-level intermediate representations and dialects; a strong model for a typed, evolvable harness IR.

**SYS-18.** Xavier Leroy and Sandrine Blazy. ["Formal Verification of a C-Like Memory Model and Its Uses for Verifying Program Transformations"](https://doi.org/10.1007/978-3-540-71316-6_38), JAR 2008. Demonstrates the semantic precision needed to certify low-level rewrites.

**SYS-19.** Patrice Godefroid, Michael Levin, and David Molnar. ["SAGE: Whitebox Fuzzing for Security Testing"](https://doi.org/10.1145/2090147.2094081), *Communications of the ACM* 55(3), 2012. Symbolic execution and generated counterexamples as an evidence source.

**SYS-20.** Tsong Yueh Chen et al. ["Metamorphic Testing: A New Approach for Generating Next Test Cases"](https://arxiv.org/abs/2002.12543), 1998. Introduces relations among executions when exact test oracles are unavailable.

## A compact research program {-}

A reader intending to build a formally disciplined self-evolving harness can turn the literature into the following sequence:

1. Implement a small DSPy or equivalent program and make every model/tool call appear in a typed trace. Read LLM-02 through LLM-08.
2. Replace a scalar objective with a vector and maintain a non-dominated archive. Read EV-07 through EV-10.
3. Restrict candidate generation to a typed DSL or IR. Read SYN-02, SYN-05, SYN-18, and SYS-17.
4. Give the IR an effect and resource semantics. Read CAT-10 through CAT-20 and TYPE-20 through TYPE-23.
5. Make each rewrite carry machine-checkable boundary and resource evidence. Read TYPE-24 through TYPE-35.
6. Model exact semantic replacements as paths or equivalences, and one-way improvements as directed morphisms. Read HOTT-01 through HOTT-09 and CAT-33 through CAT-37.
7. Audit the evaluator as an adaptive measurement system. Read EVAL-01 through EVAL-27.
8. Promote only immutable, provenance-linked artifacts through capability-restricted deployment gates. Read SYS-01 through SYS-18.

The resulting system is not autonomous proof by statistical acclaim. It is a proof- and evidence-aware search process whose untrusted generative component is powerful precisely because the surrounding mathematical and operational boundaries are explicit.

