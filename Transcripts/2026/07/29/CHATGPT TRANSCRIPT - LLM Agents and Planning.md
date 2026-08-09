# LLM Agents and Planning

- URL: https://chatgpt.com/c/6a69f6c0-799c-83ea-93d6-f13cd199ad4a
- Created: 2026-07-29T12:49:25.408Z

---

> What if we consider llm agents to actually be planning / operations research algorithms with a magic heuristic blackbox? What are the parallels?

That is a productive framing. An LLM agent can often be understood as:

> **A classical planning, search, or control algorithm operating over a poorly specified state space, with an LLM serving as a learned heuristic, proposal distribution, transition model, or value estimator.**

The “agentic” quality often comes less from the LLM itself than from the outer loop wrapped around it.

## Core correspondence

| LLM-agent component | Planning / OR analogue |
|---|---|
| Prompt and context | Current state or belief state |
| Tool calls | Actions / control inputs |
| Tool outputs | Observations and state transitions |
| System instructions | Hard constraints, policy rules |
| User request | Objective function or terminal condition |
| Chain-of-thought plan | Candidate solution or partial plan |
| ReAct loop | Online planning with observation feedback |
| Reflection / critique | Local search, repair, or cutting-plane step |
| Memory | State estimator, belief update, or history compression |
| Multiple sampled plans | Beam search, rollout search, or scenario sampling |
| Verifier / critic | Feasibility checker or value function |
| Human approval | External constraint oracle |
| Context-window limit | Bounded working memory / truncated horizon |

A useful abstraction is:

\[
a_t \sim H_\theta(s_t, g, h_t)
\]

where \(H_\theta\) is the LLM “heuristic black box,” \(s_t\) is the represented state, \(g\) is the goal, and \(h_t\) is interaction history. The surrounding agent loop then executes the action, observes the result, updates its state, and replans.

## The LLM can occupy several classical roles

### 1. Heuristic function

In A* or best-first search, a heuristic estimates which partial solution is promising.

An LLM does something similar when it says:

- “First inspect the configuration.”
- “This error probably comes from authentication.”
- “Try these three candidate approaches.”

But unlike an A* heuristic, the LLM heuristic is generally:

- not admissible,
- not consistent,
- poorly calibrated,
- sensitive to representation,
- capable of inventing nonexistent actions.

So it resembles a powerful learned heuristic for satisficing search, not a guarantee-preserving one.

### 2. Policy or action-proposal mechanism

The LLM can be treated as a policy:

\[
\pi_\theta(a \mid s, g)
\]

It narrows a huge action space to a few plausible actions. This is particularly valuable in domains where actions are textual or combinatorial, such as:

- writing SQL,
- selecting APIs,
- editing code,
- forming search queries,
- decomposing an ambiguous task.

The outer algorithm can then reject, rank, simulate, or verify those proposals.

### 3. Approximate world model

When an agent predicts what will happen after a tool call or code modification, the LLM is acting like a transition model:

\[
\hat{T}_\theta(s' \mid s,a)
\]

This supports model-based planning, but the model is unreliable. Consequently, actual execution and observation are essential. Tool-using agents work better when they behave like model-predictive control: plan briefly, execute, observe, and replan.

### 4. Value function or critic

An LLM can score candidate plans:

\[
\hat{V}_\theta(s,g)
\]

or compare two solutions. This parallels value functions, branch-and-bound bounds, or surrogate objectives.

The weakness is that linguistic plausibility may substitute for actual utility. A plan can “sound finished” while remaining infeasible.

### 5. Problem compiler

One of the most important roles is upstream of optimization: converting an informal request into a structured problem.

For example:

> “Schedule these meetings while minimizing disruption.”

must become:

- decision variables,
- availability constraints,
- precedence constraints,
- soft preferences,
- penalties,
- a definition of “disruption.”

The LLM acts as a semantic compiler from natural language to an optimization model. Traditional OR usually assumes this model has already been specified; agents attempt to infer it.

## Parallels to specific algorithm families

### Heuristic search

Agent loops resemble best-first or beam search when they:

1. generate candidate next steps,
2. score them,
3. retain promising branches,
4. continue until a stopping condition is reached.

Tree-of-thought methods make this correspondence explicit.

### Monte Carlo tree search

Sampling several possible continuations, evaluating them, and expanding promising ones is structurally close to MCTS. The LLM provides the rollout policy and sometimes the value estimate.

The major difference is that the search tree is often implicit and encoded in prose rather than represented as a clean data structure.

### Model-predictive control

Many effective agents use a receding horizon:

1. make a short plan,
2. execute one or two actions,
3. inspect the actual result,
4. replan.

This is preferable to generating a complete long-horizon plan once, because the environment is partially observed and the LLM’s predicted transitions are unreliable.

### POMDPs

Agents rarely know the true state. They see:

- incomplete documents,
- partial tool outputs,
- hidden user preferences,
- uncertain external systems,
- compressed conversation history.

Memory and summarization therefore act as crude belief-state maintenance. The agent is solving something closer to a partially observable control problem than a fully known planning problem.

### Hierarchical task networks

“Plan → subtask → tool call” resembles hierarchical planning. The LLM selects abstract tasks and recursively refines them into executable operations.

For example:

\[
\text{Prepare report}
\rightarrow
\begin{cases}
\text{collect data}\\
\text{analyze data}\\
\text{write findings}\\
\text{verify claims}
\end{cases}
\]

The hierarchy is learned or improvised rather than manually encoded.

### Constraint programming

Tool schemas, permissions, required fields, and business rules define a feasible action set. A robust agent should distinguish:

- **hard constraints:** never violate,
- **soft constraints:** optimize where possible,
- **heuristics:** useful but expendable suggestions.

Many agent failures occur because these categories are all represented merely as text and therefore treated as negotiable.

### Local search and repair

“Reflection” often behaves like iterative improvement:

1. produce an initial solution,
2. detect defects,
3. modify a local portion,
4. repeat.

This is analogous to hill climbing, neighborhood search, or constraint repair. It can improve solutions, but repeated self-critique does not guarantee movement toward the actual objective.

### Decomposition methods

A complex task may be split into subproblems handled by different prompts or agents. This resembles:

- Benders decomposition,
- column generation,
- Lagrangian decomposition,
- distributed optimization.

The analogy is strongest when there is an explicit coordinator that combines subproblem outputs and enforces global consistency. Without one, “multi-agent systems” can become several noisy heuristics exchanging prose.

## The central difference: the optimization problem is endogenous

In classical OR, one generally begins with:

\[
\min_x f(x)
\]

subject to:

\[
g_i(x) \leq 0,\qquad h_j(x)=0.
\]

In an LLM agent, \(f\), \(g_i\), \(h_j\), the variables \(x\), and even the available actions may all be inferred during execution.

Thus the agent is simultaneously trying to:

1. identify the problem,
2. construct the state representation,
3. infer the objective,
4. infer constraints,
5. search for a solution,
6. execute the solution,
7. determine whether it succeeded.

This is much more like **adaptive problem formulation plus online approximate planning** than ordinary optimization.

## Where the analogy breaks

The black-box heuristic has several unusual pathologies.

**Representation dependence.** Equivalent states expressed differently can produce different actions.

**Nonstationarity.** Adding one observation to the context can drastically change the effective policy.

**No stable objective.** The model may optimize helpful-sounding output rather than task success.

**No inherent feasibility guarantee.** It can propose invalid API calls, impossible schedules, or contradictory plans.

**Weak state identity.** Textual descriptions can collapse distinct states or treat the same state as different ones.

**Poor uncertainty handling.** Confidence expressed linguistically is not necessarily calibrated probability.

**History contamination.** Irrelevant earlier context can alter decisions, unlike a carefully defined Markov state.

These are reasons to place verification, constraint enforcement, and state tracking outside the model.

## The engineering implication

This framing suggests that the strongest agent systems will not be “a smarter prompt.” They will be hybrid solvers:

\[
\text{Agent}
=
\text{explicit algorithm}
+
\text{LLM heuristic}
+
\text{structured state}
+
\text{hard constraints}
+
\text{external verification}.
\]

The LLM should handle the parts where learned semantic judgment is valuable:

- proposing actions,
- interpreting observations,
- generating decompositions,
- translating language into formal structure.

Conventional algorithms should handle the parts where guarantees matter:

- bookkeeping,
- constraint enforcement,
- search-tree management,
- scheduling,
- numerical optimization,
- termination,
- rollback,
- validation.

This also changes how agents should be evaluated. Rather than asking whether they appear intelligent, measure:

- feasibility rate,
- task success,
- cost or regret,
- number of tool calls,
- search efficiency,
- recovery from failed actions,
- constraint violations,
- sensitivity to state representation.

The resulting view is less mystical:

> **An LLM agent is an approximate online solver whose most distinctive component is a general-purpose learned heuristic over language-defined states and actions.**

Its power comes from the breadth of that heuristic. Its unreliability comes from treating an uncalibrated semantic predictor as though it were a planner, optimizer, world model, and verifier simultaneously.

