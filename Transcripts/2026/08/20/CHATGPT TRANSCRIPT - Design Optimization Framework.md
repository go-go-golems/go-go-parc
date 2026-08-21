# Design Optimization Framework

- URL: https://chatgpt.com/c/6a87743a-a7b0-83ea-8026-ef858c7b5e7a
- Created: 2026-08-20T21:42:44.913Z

---

> Study the attached system, we have been using coinvault in production, which has gone through quite a bit of self optimization to properly optimize itself. We also extracted some of its functionality to judgekit/ragkit/ragopt/flowkit over time, and we are now interested in creating a great reusable optimization framework, with a core focus being to be able to view the optimization process, both live as it happens, planned before it runs, and the results, and optimizations done. Not only do we want to capture the thing, but we want to ground it in proper patterns (I think this is kind of similar to RL in a way, since we can have multi turn conversations and complex things like tool call and even widget generation as part of the optimization? And there's novel research on llms as judges and optimization frameworks like GEPA). We want to be able to create a whole set of different self-optimization setups based on a core compositional core set of packages / frameworks / tools so that we can cover many needs. 
>
>  Give me rundown of what we could do, what you observe, how we could reorganize things to have a propermathematical grounding (whichi makes understanding it easier).

I’ll treat this as both a codebase/architecture review and a research-grounding exercise. I’ll first map how Coinvault, JudgeKit/RAGKit/RAGOpt/FlowKit currently divide responsibility, then relate the optimization loop to established formulations (RL, bandits, search, program synthesis, LLM-as-judge, GEPA-style optimization), and finish with a concrete compositional package model and mathematical abstraction.

```unknown
bash -lc python - <<'PY'
import zipfile, os
p='/mnt/data/rag-self-improvement.zip'
with zipfile.ZipFile(p) as z:
    names=z.namelist()
    print('FILES', len(names))
    for n in names[:300]:
        print(n)
PY
```

```unknown
bash -lc python - <<'PY'
import zipfile, os, collections
p='/mnt/data/rag-self-improvement.zip'
with zipfile.ZipFile(p) as z:
    tops=collections.Counter()
    for n in z.namelist():
        top=n.split('/',1)[0]
        tops[top]+=1
    print(tops)
PY
```

```unknown
bash -lc python - <<'PY'
import zipfile,re
p='/mnt/data/rag-self-improvement.zip'
with zipfile.ZipFile(p) as z:
    for n in z.namelist():
        if 'flowkit' in n.lower(): print(n)
PY
```

```unknown
bash -lc rm -rf /mnt/data/rag-self-improvement && mkdir -p /mnt/data/rag-self-improvement && python - <<'PY'
import zipfile, os
p='/mnt/data/rag-self-improvement.zip'; out='/mnt/data/rag-self-improvement'
with zipfile.ZipFile(p) as z:
    for info in z.infolist():
        dest=os.path.realpath(os.path.join(out, info.filename))
        if not dest.startswith(os.path.realpath(out)+os.sep):
            raise RuntimeError('unsafe path '+info.filename)
    z.extractall(out)
print('extracted')
PY
find /mnt/data/rag-self-improvement -maxdepth 2 -type f | sed 's#/mnt/data/rag-self-improvement/##' | sort | head -200
```

<details><summary>💭 Thinking</summary>

**Inspected ZIP repository structure and extracted project files**

</details>

The archive is substantial: five repositories, with Coinvault and `rag-ttc` carrying most of the historical/production mass, and `ragkit`, `judgekit`, and `ragopt` looking like extracted reusable layers. One early signal is that `ragopt` already has a strong “evidence-gated optimization harness” concept—candidate snapshots, paired evaluation, gates, runstore, review/reporting—which is a useful nucleus, but it is still narrower than the general optimization substrate you’re describing.

```unknown
bash -lc cd /mnt/data/rag-self-improvement && printf '\n== coinvault dirs ==\n' && find coinvault -maxdepth 3 -type d | sed 's#^coinvault/##' | sort | head -220 && printf '\n== rag-ttc dirs ==\n' && find rag-ttc -maxdepth 3 -type d | sed 's#^rag-ttc/##' | sort | head -180 && printf '\n== judgekit dirs ==\n' && find judgekit -maxdepth 3 -type d | sed 's#^judgekit/##' | sort && printf '\n== ragopt dirs ==\n' && find ragopt -maxdepth 3 -type d | sed 's#^ragopt/##' | sort
```

```unknown
bash -lc cd /mnt/data/rag-self-improvement && for f in coinvault/README.md rag-ttc/README.md ragkit/README.md judgekit/README.md ragopt/README.md; do echo; echo '===== '$f' ====='; sed -n '1,240p' "$f"; done
```

```unknown
bash -lc cd /mnt/data/rag-self-improvement && printf '== optimization-related docs ==\n' && find coinvault/ttmp rag-ttc/ttmp judgekit/ttmp ragopt/ttmp -type f \( -name '*.md' -o -name '*.yaml' \) | grep -Ei 'optimi|feedback|judge|eval|rag|self|loop|candidate|promotion|experiment|trace' | head -220 && printf '\n== source references ==\n' && rg -n -i --glob '!**/.git' --glob '*.go' --glob '*.md' --glob '*.yaml' '(self[- ]?optim|ragopt|judgekit|candidate|promotion|gepa|feedback loop|optimization loop|optimizer|experiment)' coinvault rag-ttc ragopt judgekit | head -350
```

```unknown
bash -lc cd /mnt/data/rag-self-improvement && files=(
'coinvault/ttmp/2026/08/17/COINVAULT-045--study-self-optimization-and-exploitable-evaluator-errors/design-doc/09-structured-evaluation-and-optimization-refactor-for-coinvault.md'
'coinvault/ttmp/2026/08/17/COINVAULT-045--study-self-optimization-and-exploitable-evaluator-errors/design-doc/01-self-optimization-and-exploitable-evaluator-errors.md'
'coinvault/ttmp/2026/08/09/COINVAULT-045--align-coinvault-with-current-ragkit-ragopt-and-rag-ttc-boundaries/design-doc/02-mathematical-evidence-ledger-kernel-intern-design-and-implementation-guide.md'
'coinvault/ttmp/2026/08/09/COINVAULT-045--align-coinvault-with-current-ragkit-ragopt-and-rag-ttc-boundaries/design-doc/01-coinvault-rag-dependency-alignment-and-common-framework-plan.md'
'ragopt/ttmp/2026/08/06/RAGOPT-001--reusable-reproducible-self-optimization-harness/design-doc/01-ragopt-intern-guide-to-a-reusable-evidence-gated-optimization-harness.md'
'judgekit/ttmp/2026/08/15/JUDGEKIT-001--provider-neutral-llm-judge-framework/design-doc/01-provider-neutral-llm-judge-framework.md'
)
for f in "${files[@]}"; do echo; echo '===== '$f' ====='; sed -n '1,280p' "$f"; done
```

```unknown
bash -lc cd /mnt/data/rag-self-improvement && find judgekit/ttmp -type f | sort | head -120 && echo '--- ragkit readme ---' && sed -n '1,260p' ragkit/README.md
```

```unknown
bash -lc cd /mnt/data/rag-self-improvement && rg -n --glob 'go.mod' 'flowkit|flow' . && echo '--- ragkit flow files ---' && find ragkit/flow -maxdepth 2 -type f -print | sort | xargs -r -n1 sh -c 'echo ==== $0; sed -n "1,220p" "$0"'
```

```unknown
bash -lc cd /mnt/data/rag-self-improvement && for f in coinvault/go.mod rag-ttc/go.mod ragkit/go.mod judgekit/go.mod ragopt/go.mod; do echo ==== $f; sed -n '1,90p' $f; done
```

```unknown
bash -lc cd /mnt/data/rag-self-improvement && for f in \
 ragopt/pkg/candidate/types.go ragopt/pkg/eval/types.go ragopt/pkg/eval/runner.go ragopt/pkg/runstore/types.go ragopt/pkg/gate/evaluate.go ragopt/pkg/policy/policy.go ragopt/pkg/review/review.go \
 judgekit/spec/types.go judgekit/protocol/types.go judgekit/eval/types.go judgekit/assessment/types.go judgekit/judging/judge.go judgekit/suite/suite.go \
 coinvault/cmd/coinvault/cmds/knowledge_ragopt.go coinvault/cmd/coinvault/cmds/knowledge_ragopt_trace.go coinvault/cmd/coinvault/cmds/knowledge_ragopt_treatment.go; do 
  [ -f "$f" ] || continue; echo; echo '===== '$f' ====='; sed -n '1,320p' "$f"; 
done
```

```unknown
bash -lc cd /mnt/data/rag-self-improvement && wc -l ragopt/pkg/{candidate/types.go,eval/types.go,eval/runner.go,runstore/types.go,gate/evaluate.go,policy/policy.go,review/review.go} judgekit/{spec/*.go,protocol/*.go,eval/*.go,assessment/*.go,judging/*.go,suite/*.go} coinvault/cmd/coinvault/cmds/knowledge_ragopt*.go | sort -n | tail -40
```

```unknown
bash -lc cd /mnt/data/rag-self-improvement && echo '== ragopt symbols ==' && rg -n '^type |^const \(|^func ' ragopt/pkg/{candidate,eval,runstore,compare,gate,policy,review,report}/*.go | head -300 && echo '\n== judgekit symbols ==' && rg -n '^type |^const \(|^func ' judgekit/{spec,eval,protocol,assessment,judging,audit,calibration,suite}/*.go | head -360 && echo '\n== coinvault ragopt symbols ==' && rg -n '^type |^const \(|^func ' coinvault/cmd/coinvault/cmds/knowledge_ragopt*.go | head -360
```

<details><summary>💭 Thinking</summary>

**Inspected project architectures, documentation, dependencies, and RAG optimization code**

</details>

```unknown
fast|GEPA Reflective Prompt Evolution Can Language Models Learn to Reflective Prompt Evolution arXiv 2025|3650|arxiv.org
fast|DSPy GEPA optimizer official docs|3650|dspy.ai
fast|Language Models as Optimizers OPRO arXiv|3650|arxiv.org
fast|TextGrad automatic differentiation via text arXiv|3650|arxiv.org
fast|MIPROv2 DSPy Bayesian optimization prompts arXiv|3650|arxiv.org
fast|LLM as a judge evaluator reward hacking Goodhart optimization bias paper|3650|arxiv.org
fast|Judging LLM-as-a-Judge with MT-Bench Chatbot Arena position bias arXiv|3650|arxiv.org
fast|reward hacking language model judge optimization evaluator exploitation arxiv|3650|arxiv.org
length|medium

```

```unknown
fast|MIPROv2 Optimizing Instructions and Demonstrations for Multi-stage Language Model Programs arxiv 2024|3650|arxiv.org
fast|The Instruction Hierarchy evaluator gaming LLM judges reward hacking|3650|arxiv.org
fast|Goodhart law LLM evaluator optimization judge reward hacking benchmark 2025|3650|arxiv.org
fast|LLM evaluator overoptimization reward hacking judge hacking paper 2025|arxiv.org
fast|Scaling LLM Test-Time Compute Optimally can be more effective than scaling model parameters|3650|arxiv.org
length|medium

```

```unknown
fast|MIPROv2 Optimizing Instructions and Demonstrations for Multi-stage Language Model Programs arxiv 2024|3650|arxiv.org
fast|instruction hierarchy evaluator gaming LLM judges reward hacking|3650|arxiv.org
fast|Goodhart law LLM evaluator optimization judge reward hacking benchmark 2025|3650|arxiv.org
fast|LLM evaluator overoptimization reward hacking judge hacking paper 2025|3650|arxiv.org
fast|Scaling LLM Test-Time Compute Optimally can be more effective than scaling model parameters|3650|arxiv.org
length|medium

```

```unknown
fast|Scaling Laws for Reward Model Overoptimization arxiv Gao 2022|3650|arxiv.org
fast|Towards understanding and mitigating evaluator overfitting LLM judges optimization arxiv|3650|arxiv.org
fast|LLM judge robustness adversarial attacks evaluation scoring optimization arxiv 2024 2025|3650|arxiv.org
fast|Reward model overoptimization proxy reward true reward language models paper|3650|arxiv.org
length|medium

```

```unknown
open|turn439224academia4
open|turn439224search0
open|turn732034academia0
open|turn439224academia3
length|long

```

<details><summary>💭 Thinking</summary>

**Searched 2 websites**

</details>

```unknown
bash -lc cd /mnt/data/rag-self-improvement && for f in \
'coinvault/ttmp/2026/08/17/COINVAULT-045--study-self-optimization-and-exploitable-evaluator-errors/design-doc/09-structured-evaluation-and-optimization-refactor-for-coinvault.md' \
'coinvault/ttmp/2026/08/17/COINVAULT-045--study-self-optimization-and-exploitable-evaluator-errors/design-doc/01-self-optimization-and-exploitable-evaluator-errors.md' \
'coinvault/ttmp/2026/08/17/COINVAULT-045--study-self-optimization-and-exploitable-evaluator-errors/design-doc/02-exploitable-residual-errors-why-accurate-judges-are-unsafe-optimization-targets.md' \
'coinvault/ttmp/2026/08/09/COINVAULT-045--align-coinvault-with-current-ragkit-ragopt-and-rag-ttc-boundaries/design-doc/02-mathematical-evidence-ledger-kernel-intern-design-and-implementation-guide.md' \
'ragopt/ttmp/2026/08/06/RAGOPT-001--reusable-reproducible-self-optimization-harness/design-doc/01-ragopt-intern-guide-to-a-reusable-evidence-gated-optimization-harness.md' \
'judgekit/ttmp/2026/08/17/JUDGEKIT-001--design-and-implement-judgekit/design-doc/01-judgekit-architecture-and-implementation-guide.md'; do echo; echo ==== $f; rg -n '^#{1,4} ' "$f"; done
```

<details><summary>💭 Thinking</summary>

**Searched design document section headings**

</details>

The code and the August 17 design work already point in the right direction: you have separated **measurement** (`judgekit`) from **domain mechanics** (`ragkit`) and **experiment custody/promotion** (`ragopt`). The missing abstraction is one level above all three: a general “optimization program” model that treats prompts, tool policies, retrieval settings, flow topology, widget-generation policies, model choices, and even evaluator configurations as typed variables in a trajectory-producing system—not just as RAG candidate assets.

```unknown
bash -lc cd /mnt/data/rag-self-improvement && f='coinvault/ttmp/2026/08/17/COINVAULT-045--study-self-optimization-and-exploitable-evaluator-errors/design-doc/09-structured-evaluation-and-optimization-refactor-for-coinvault.md'; sed -n '129,232p' "$f"; sed -n '522,687p' "$f"; sed -n '821,963p' "$f"; echo '--- current self-opt risks ---'; f2='coinvault/ttmp/2026/08/17/COINVAULT-045--study-self-optimization-and-exploitable-evaluator-errors/design-doc/02-exploitable-residual-errors-why-accurate-judges-are-unsafe-optimization-targets.md'; sed -n '31,185p' "$f2"; echo '--- ragopt architecture/lifecycle ---'; f3='ragopt/ttmp/2026/08/06/RAGOPT-001--reusable-reproducible-self-optimization-harness/design-doc/01-ragopt-intern-guide-to-a-reusable-evidence-gated-optimization-harness.md'; sed -n '306,430p' "$f3"; sed -n '878,1010p' "$f3"; sed -n '1431,1484p' "$f3";
```

```unknown
bash -lc cd /mnt/data/rag-self-improvement && f='coinvault/ttmp/2026/08/09/COINVAULT-045--align-coinvault-with-current-ragkit-ragopt-and-rag-ttc-boundaries/design-doc/02-mathematical-evidence-ledger-kernel-intern-design-and-implementation-guide.md'; sed -n '327,470p' "$f"; echo '--- law tests ---'; sed -n '1324,1377p' "$f"; echo '--- judgekit conceptual model ---'; f2='judgekit/ttmp/2026/08/17/JUDGEKIT-001--design-and-implement-judgekit/design-doc/01-judgekit-architecture-and-implementation-guide.md'; sed -n '194,355p' "$f2"; sed -n '768,890p' "$f2"
```

```unknown
bash -lc cd /mnt/data/rag-self-improvement/coinvault && for d in configs/ragopt/*; do [ -d "$d" ] || continue; echo; echo ==== ${d#configs/ragopt/}; find "$d" -maxdepth 1 -type f -printf '%f\n' | sort; done | head -500
```

```unknown
bash -lc cd /mnt/data/rag-self-improvement/coinvault && for f in configs/ragopt/*/candidate.yaml; do echo; echo ==== $f; cat "$f"; done
```

```unknown
bash -lc cd /mnt/data/rag-self-improvement && echo '== optimization UI/event references ==' && rg -n -i --glob '!**/.git/**' '(ragopt|optimization|candidate|experiment|campaign|promotion)' coinvault/web coinvault/proto coinvault/internal/webchat rag-ttc/apps rag-ttc/internal/admin/tui | head -260 && echo '\n== flowkit imports ==' && rg -n 'go-go-golems/flowkit' coinvault rag-ttc ragkit --glob '*.go' | head -220
```

<details><summary>💭 Thinking</summary>

**Inspected architecture, evidence frameworks, configurations, manifests, and optimization flows**

</details>

```unknown
fast|github go-go-golems flowkit Go flow execution budget cache observer|3650|github.com
fast|site:pkg.go.dev github.com/go-go-golems/flowkit|3650|pkg.go.dev
length|medium

```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

```unknown
bash -lc go env GOPATH && ls -d $(go env GOPATH)/pkg/mod/github.com/go-go-golems/flowkit* 2>/dev/null || true && find $(go env GOPATH)/pkg/mod/github.com/go-go-golems -maxdepth 1 -type d -name 'flowkit*' -print 2>/dev/null | head
```

```json
{"paths":["GitHub"],"query":"search"}
```

<details><summary>💭 Thinking</summary>

**Checked Flowkit module cache paths**

</details>

```python3
{"path":"/GitHub/link_694554034b848191ab0db5a14b130105/search_repositories","args":{"query":"flowkit","org":"go-go-golems","per_page":10}}
```

```python3
{"path":"/GitHub/link_694554034b848191ab0db5a14b130105/fetch","args":{"url":"https://github.com/go-go-golems/flowkit/blob/main/README.md"}}
```

```python3
{"path":"/GitHub/link_694554034b848191ab0db5a14b130105/fetch","args":{"url":"https://github.com/go-go-golems/flowkit/blob/main/docs/flowkit-developer-guide.md"}}
```

```python3
{"path":"/GitHub/link_694554034b848191ab0db5a14b130105/search","args":{"query":"type Ledger","repository_name":"go-go-golems/flowkit","topn":20}}
```

<details><summary>💭 Thinking</summary>

**Reviewed Flowkit repository, README, developer guide, and ledger types**

</details>

```unknown
bash -lc cd /mnt/data/rag-self-improvement && echo '--- runstore types ---'; cat ragopt/pkg/runstore/types.go; echo '--- runstore run ---'; sed -n '1,260p' ragopt/pkg/runstore/run.go; echo '--- compare types ---'; cat ragopt/pkg/compare/types.go; echo '--- review types ---'; sed -n '1,240p' ragopt/pkg/review/review.go; echo '--- report types ---'; cat ragopt/pkg/report/types.go
```

<details><summary>💭 Thinking</summary>

**Designing the optimization framework**

I’m shaping a reusable `optkit` above `flowkit`, with `ragopt` as a domain adapter. I’m also defining an event-sourced run ledger and projector-based views for plans, lineage, scores, costs, health, and live progress.

**Designed the optimization framework**

**Refining framework boundaries**

I’m separating execution, evaluation, and optimization concerns. Existing experiments reveal the need for typed variable registries, provenance-rich measurements, adaptive campaign history, locked promotion evaluators, and generic trajectory envelopes without imposing a universal transcript.

**Refined framework boundaries**

</details>

```unknown
bash -lc cd /mnt/data/rag-self-improvement && sed -n '170,215p' coinvault/cmd/coinvault/cmds/knowledge_ragopt_case_test.go; echo '--- evaluator version refs ---'; rg -n 'evaluator-v[0-9]+|JudgeProtocol|protocol_digest|judge.*digest' coinvault/configs/ragopt coinvault/cmd/coinvault/cmds/knowledge_ragopt* coinvault/internal/knowledge | head -180
```

```unknown
bash -lc cd /mnt/data/rag-self-improvement && sed -n '184,240p' coinvault/cmd/coinvault/cmds/knowledge_ragopt_case_test.go
```

```unknown
bash -lc cd /mnt/data/rag-self-improvement && sed -n '1,220p' coinvault/cmd/coinvault/cmds/knowledge_ragopt_trace.go && echo '--- eval chat configured runner event/traces ---' && sed -n '1,280p' coinvault/internal/webchat/evalchat/configured_runner.go
```

```unknown
bash -lc cd /mnt/data/rag-self-improvement && rg -n '^type Event struct|EventName.*widget|Widget|widget' coinvault/internal/webchat/evalchat coinvault/internal/webchat coinvault/proto/coinvault/widgets --glob '*.go' --glob '*.proto' | head -220
```

<details><summary>💭 Thinking</summary>

**Synthesizing the architecture**

I’m treating the codebase as evidence for a broader optimization model. The key opportunity is a compositional framework where typed variables generate trajectories, evaluators measure them, and live, planned, lineage, and results views remain first-class.

**Mapping the package ecosystem**

I’m seeing clean boundaries already: `ragkit` supplies RAG mechanics, `judgekit` measures outputs, `flowkit` executes bounded work, and `ragopt` orchestrates experiments. The missing layer is a general campaign model coordinating adaptive optimization across domains.

**Grounding the design mathematically**

I’m using the existing evidence ledger, typed evaluator concepts, and paired optimization lifecycle as foundations. The framework should add campaign state, trajectory events, confidence-aware gates, and compositional interventions while preserving reproducibility and human promotion.

**Synthesized architecture, package ecosystem, and mathematical design foundation**

**Inspected evaluation types, heldout tests, traces, runners, and events**

</details>

```unknown
open|turn199910view0
open|turn199910view2
open|turn199910view3
open|turn740452academia0
open|turn439224academia2
length|medium

```

<details><summary>💭 Thinking</summary>

**Formalizing optimization**

I’m framing optimization as constrained, trajectory-based search: configurations induce distributions over executions, measurements produce vector objectives, and proposal algorithms update candidates from accumulated history while hard constraints remain lexicographic.

**Formalized the optimization problem**

</details>

```unknown
open|turn124026view3|44
open|turn124026view4|49
length|medium

```

<details><summary>💭 Thinking</summary>

**Expanding intervention design**

I’m allowing multi-variable patches in the core while preserving one-change experiments as an attribution policy. I’m also separating execution, measurement, domain logic, and optimization control into `flowkit`, `judgekit`, `ragkit`, and `optkit`.

**Structuring optkit**

I’m proposing `optkit` as the reusable control plane, with typed specifications, trajectories, campaigns, planning, search, selection, storage, events, projections, review, and adapters for execution and measurement.

**Defining campaign observability**

I’m making the event journal authoritative, with stable lifecycle events and projections for plan, live progress, lineage, metrics, Pareto state, evaluator epochs, costs, artifacts, rejection reasons, and promotion history.

**Planning migration**

I’m sequencing the work from vocabulary and event laws through campaign projections, live streaming, typed treatment registries, and simple search. I’m deferring advanced optimizers, online feedback, and policy-learning adapters until the foundation is stable.

**Searched 1 website**

</details>

I think there is a fairly clean architecture hiding inside what you already built. The main change I would make is to stop thinking of `ragopt` as “the optimizer” and introduce a **domain-neutral optimization algebra/control plane**—call it `optkit`—above FlowKit and beside JudgeKit. Then RAGOpt becomes one specialization of that machinery.

The important conceptual shift is this:

> **The thing being optimized is not necessarily a prompt or an answer. It is a parameterized executable system that produces trajectories.**

A trajectory can contain multiple model turns, retrieval, tool calls, retries, hidden state transitions, widgets, citations, rendered UI, costs, errors, and the final answer. Once that is the primitive, RL, GEPA, MIPRO, textual gradients, evolutionary search, coordinate descent, Bayesian optimization, and your existing human-driven Coinvault loop all become different optimizers over essentially the same substrate.

## What I see in the current system

The separation you've arrived at is already good.

| Component | What it has become | What I would preserve |
|---|---|---|
| `flowkit` | Domain-neutral execution mechanics | caching, semantic identity, retries, bounded execution, resources, metering, ledgers |
| `judgekit` | Domain-neutral measurement | construct → contract → protocol → evidence → assessment → calibration |
| `ragkit` | RAG mechanics/domain model | retrieval, chunks, evidence, representations, reranking, RAG-specific checks |
| `ragopt` | Evidence-gated RAG experimentation | candidate identity, paired evaluation, run custody, comparison, gates, review |
| Coinvault | Actual optimizing product | executable system, rich traces, product meaning, variables/treatments, policy |

FlowKit in particular is correctly scoped today: it explicitly separates semantic identity from execution policy, provides reports/ledgers, and deliberately does **not** persist workflow control state or act as a DAG scheduler. fileciteturn1file0L2-L4 That means I would resist putting optimization-campaign state into it.

The strongest observation from the Coinvault history is that you have already been running a recognizable optimization algorithm, only without naming it mathematically. The sequence of changes around result depth, comparison decomposition, comparison intent, grounding prompts, abstention/routing, source-role routing, answer policy, reranker pool, tool descriptions, etc. is basically **manual reflective coordinate descent over a structured program**.

And `ragopt` formalized an especially disciplined form of it:

$$
\|\theta' - \theta\|_0 = 1
$$

where $\theta$ is the whole Coinvault configuration and a candidate differs in exactly one coordinate/asset. Your “exactly one mutation” rule is mathematically a one-sparse intervention. That is excellent when you care about attribution: if the paired outcome moves, you have a much better causal story about why.

It just shouldn't be the universal definition of optimization.

Another strong piece is the paired incumbent/challenger evaluation. For case $i$ and repeat $r$, you're effectively measuring

$$
\Delta_{i,r}
=
m(\tau_{\theta',i,r})
-
m(\tau_{\theta,i,r})
$$

instead of comparing unrelated aggregate scores. That's a blocked/paired experimental design and is exactly the sort of rigor worth keeping.

There are also several places where the existing abstractions are now visibly at their limit. `ragopt.Outcome.Metrics map[string]float64` has lost too much semantic information; the Coinvault treatment mechanism switch keeps growing; campaign lineage is implicit in candidate directories; evaluator revisions appear inside proposer/candidate history instead of being first-class measurement epochs; and the current experiment browser is primarily a view over completed run artifacts rather than a live persistent optimization process.

## Is this RL?

**At the execution/trajectory level, yes. At the optimization-algorithm level, not necessarily.**

For a multi-turn Coinvault session, an RL/POMDP vocabulary is very natural. Let $h_t$ be everything visible to the agent at turn $t$, and let its parameterized policy be $\pi_\theta$:

$$
a_t \sim \pi_\theta(a \mid h_t)
$$

The action $a_t$ need not mean “emit text.” Its action space can contain things such as:

$$
a_t \in
\{
\text{text},
\text{tool-call},
\text{retrieval-request},
\text{widget-intent},
\text{terminate},
\dots
\}
$$

The environment then produces an observation:

$$
o_{t+1} \sim P(o \mid h_t,a_t)
$$

and an episode gives you a trajectory

$$
\tau =
(x,o_0,a_0,o_1,a_1,\ldots,o_T).
$$

That's exactly why GEPA is particularly relevant to what you're doing. GEPA explicitly optimizes from trajectories containing reasoning, tool calls, and tool outputs, uses natural-language reflection to diagnose failures and propose prompt changes, and maintains a Pareto-style evolutionary process. citeturn124026view0

But if Coinvault isn't updating model weights using a policy gradient, calling the whole framework RL would obscure more than it clarifies. Your current optimization is much closer to **constrained black-box program optimization / sequential experimental design**.

That distinction gives you a useful stack:

| Level | Mathematical lens |
|---|---|
| One Coinvault interaction | POMDP / stochastic computation |
| Complete interaction | trajectory / episode |
| JudgeKit evaluation | measurement theory / statistical instrument |
| Comparing candidates | experimental design / statistics |
| Choosing next candidate | black-box search / bandit / evolutionary optimization |
| Updating actual model weights | RL, if you eventually do it |
| Deciding whether to deploy | constrained statistical decision |

That is broad enough that RL becomes one optimizer plugin rather than the ontology of the whole library.

## A mathematical core I would standardize around

I would define an optimization campaign as something approximately like

$$
\mathcal C =
(\Theta,\mathcal D,S,M,G,A,B,H).
$$

Here:

$$
\Theta
$$

is the typed search space. A point $\theta\in\Theta$ can include prompts, model choice, retrieval parameters, rerankers, tool descriptions, routing policies, few-shot demonstrations, flow topology, widget-generation policy, or arbitrary application configuration.

$$
S_\theta
$$

is the executable system materialized from that configuration.

$$
\mathcal D
$$

is not just “the test set”; it is a collection of explicitly role-tagged distributions/splits such as development, diagnostic, calibration, selection, hidden promotion, and online shadow.

Execution produces a trajectory:

$$
\tau \sim S_\theta(x), \qquad x\sim\mathcal D.
$$

Then a suite of measurement instruments produces a vector:

$$
M(\tau)
=
\big(
m_1(\tau),\ldots,m_k(\tau)
\big).
$$

This maps almost perfectly onto JudgeKit's existing philosophy. I would make a persisted measurement substantially richer than a float:

```text
Measurement
    construct_id
    measurement_contract_id
    protocol_digest
    evaluator_identity
    episode_ref
    evidence_refs
    value
    uncertainty
    applicability
    diagnostics
```

That fixes a particularly important problem: **a score from evaluator-v8 and a score from evaluator-v10 are not necessarily measurements on the same scale**.

I'd call that a *measurement epoch*. If the protocol digest changes, either remeasure the competing candidates under the new protocol or explicitly introduce a calibration/bridge. Don't quietly put both values into the same metric series.

The expected objective is then

$$
J(\theta)
=
\mathbb E_{x,\tau}
[M(\tau)].
$$

But I would deliberately make $J$ vector-valued. Your systems have properties that should never be traded away for +0.7 points of another metric.

So optimization looks more like

$$
\max_{\theta\in\Theta_{\mathrm{valid}}}
J_{\mathrm{target}}(\theta)
$$

subject to

$$
g_j(\theta)\le 0,
\qquad j=1,\ldots,p.
$$

Authorization, citation validity, evidence containment, catastrophic regressions, cost ceilings, etc. are constraints rather than weights in one giant reward function.

That's consistent with the lexicographic gate architecture you've already converged on.

## The optimizer itself becomes remarkably small conceptually

The optimizer only needs to answer:

$$
\theta_{n+1}
\sim
q_A(\theta \mid H_n)
$$

where the history is

$$
H_n=
\{
\theta_i,
\tau_i,
M(\tau_i),
\text{critiques}_i,
\text{decisions}_i
\}_{i=1}^{n}.
$$

Now all of these fit the same interface:

| Optimizer | Meaning of $q_A$ |
|---|---|
| Human | engineer proposes next patch |
| Coordinate descent | mutate one variable |
| Random/grid | sample search space |
| Bandit | allocate more trials to promising arms |
| Bayesian optimization | fit surrogate and select acquisition optimum |
| OPRO-like | show previous solutions/scores to an LLM |
| MIPRO-like | optimize components using program-aware proposals + surrogate search |
| TextGrad-like | propagate textual critiques toward responsible variables |
| GEPA-like | reflect over trajectories, mutate, maintain Pareto population |
| RL | update/model a parameterized policy from returns |

MIPRO is particularly relevant once you move beyond one-mutation candidates because its motivation explicitly includes the **credit-assignment problem across multi-stage LM programs**. citeturn124026view1 TextGrad attacks essentially the same abstraction from another direction: treat the compound AI system as a computation graph and propagate textual feedback back toward optimizable variables. citeturn124026view2

So I wouldn't implement “the GEPA framework.” I'd implement a substrate on which GEPA is perhaps 300–1000 lines of search policy plus reflection adapters.

## I would introduce `optkit`

Something like this dependency structure:

```text
                         coinvault
                    product semantics
                 variables / constraints
                 trajectory adapters
                         │
                         ▼
                       optkit
        ┌──────────────────────────────────┐
        │ campaign / plan / events / store │
        │ candidate / patch / lineage      │
        │ optimizer / archive / Pareto     │
        │ trial / statistics / selection   │
        │ projections / review             │
        └──────────────────────────────────┘
              │                 │
              ▼                 ▼
           flowkit         adapter/judgekit
        execution/runtime       measurement
              │                 │
              └──────┬──────────┘
                     │
             domain packages
               ragkit etc.

              ragopt
        = optkit + ragkit presets,
          objectives and adapters
```

I would keep JudgeKit independent. `optkit` can define a very small `Instrument`/`Measurement` boundary, with `adapter/judgekit` translating JudgeKit assessments into that form.

Similarly, RAGKit should not become optimization-aware.

`ragopt` can eventually become the convenient RAG-specific layer: retrieval variables, RAG objective catalogs, RAG trajectory projections, paired retrieval experiments, standard gates, etc.

## The most important new abstraction: `Patch`, not `Treatment`

The Coinvault treatment switch is a symptom that “treatment mechanism” is carrying two separate concepts: **what variable may change** and **how a value is applied to the executable system**.

I would make variables first-class:

```go
type Variable interface {
    ID() VariableID
    Domain() Domain
    Apply(base Snapshot, value Value) (Snapshot, Patch, error)
}
```

Then:

$$
\theta' = \theta \oplus \delta
$$

where $\delta$ is an immutable typed `Patch`.

A current RagOpt one-mutation experiment is simply a search policy that imposes

$$
|\operatorname{support}(\delta)|=1.
$$

GEPA may modify several prompt modules. MIPRO may jointly optimize instructions/demonstrations. A topology optimizer may swap a whole subgraph. The storage/control model doesn't care.

This also gives you proper lineage:

```text
deployed-v12
   │
   ├── patch A → candidate A → rejected
   │
   ├── patch B → candidate B
   │                  │
   │                  ├── patch B1 → rejected
   │                  └── patch B2 → promoted
   │
   └──────────────────────────────→ deployed-v13
```

Each edge is an optimization fact rather than a directory naming convention.

## Make the campaign event-sourced

This is, in my view, the key to your requirement to see the process **before, during, and after**.

Don't build three observation systems.

Build one immutable campaign journal and derive three projections from it.

Your existing RunStore discipline gives you much of the right DNA: append-only active artifacts, immutable terminal artifacts, digests, resumability, native-artifact authority. Generalize that one level upward.

A generic event envelope could be:

```text
api_version
campaign_id
plan_digest
event_id
sequence
previous_digest
occurred_at

kind

candidate_id?
trial_id?
episode_id?
parent_event_id?
span_id?

artifact_refs[]
payload
digest
```

The `previous_digest` idea is especially attractive given the hash/custody patterns already present in your run cells: the optimization history can be tamper-evident and fully reconstructable.

Then define stable semantic events such as candidate proposed/materialized, trial scheduled/started/completed, trajectory observation, measurement produced, archive updated, candidate rejected, hidden set exposed, review recorded, promotion evaluated, and deployment promoted.

The payloads stay versioned and extensible. The core event vocabulary should remain small.

### “Plan before it runs” needs special treatment

An adaptive optimizer cannot tell you its complete future DAG, because later candidates depend on earlier observations.

So the pre-run plan should **not pretend to enumerate the future**.

Mathematically the plan is closer to:

$$
P =
(\Theta,\mathcal D,M,G,A,B,\text{stop})
$$

where $A$ is the future decision policy and $B$ describes the permitted resources.

The plan UI can therefore show:

```text
Baseline
  ↓
Evaluate initial population (8)
  ↓
Reflect/update archive
  ↓
┌───────────── adaptive ─────────────┐
│ propose ≤ 4 candidates / round    │
│ mini-evaluate on development set  │
│ Pareto-select                      │
│ stop after 6 rounds or $50        │
└────────────────────────────────────┘
  ↓
Full evaluation of ≤ 3 finalists
  ↓
Hidden promotion evaluation
  ↓
Human review
```

That is much more informative than an artificial workflow DAG.

You can show known nodes concretely and conditional/adaptive nodes as policies with upper/lower cost bounds.

## The same journal gives you the live UI

Coinvault already has the hard part: a canonical runtime path and rich session/event/widget infrastructure.

I would make `optkit` consume trajectory events rather than forcing Coinvault into a universal transcript structure. Define a small event taxonomy and preserve native artifacts underneath it:

```text
input
model.call
message
tool.call
tool.result
retrieval.evidence
state.transition
widget.intent
widget.rendered
constraint.check
error
episode.completed
```

For concurrency, give events both a monotonically increasing persisted sequence and parent/span relationships. You then get a deterministic total order for replay plus a causal DAG for visualization.

This has an interesting consequence for widgets. The model's “generate a widget” behavior and the actual rendered widget don't need to be conflated.

You can evaluate:

$$
\text{agent action}
=
\text{widget intent}
$$

and separately:

$$
\text{environment result}
=
\text{rendered UI artifact}.
$$

That lets an optimizer learn things like “choose a table rather than prose for this task,” while another evaluator can inspect whether the projection actually rendered valid, useful UI.

A live campaign view can consequently show candidate lineage, current episode/tool activity, recently generated critiques, cost/tokens, active measurements, constraint violations, current Pareto archive, and why the optimizer chose its latest candidate—all driven by one event stream.

## And that journal gives you a much better historical view

I would make a historical optimization result more like a **change ledger** than a benchmark report.

The useful object is:

$$
\text{deployed snapshot}
\rightarrow
\text{candidate patch}
\rightarrow
\text{evaluation evidence}
\rightarrow
\text{decision}
\rightarrow
\text{next deployed snapshot}.
$$

That answers questions that are currently painful:

“What optimizations made Coinvault what it is today?”

“Why was this routing prompt introduced?”

“What candidate beat it?”

“Which evaluator version justified that conclusion?”

“Did that evaluator subsequently turn out to have a calibration issue?”

“Which production versions descend from an experiment whose judge is now considered compromised?”

Once identities and lineage are explicit, those become graph queries.

## JudgeKit should be even more central—but never treated as the reward oracle

Your August 17 JudgeKit architecture is one of the better choices in this codebase because it recognizes that a judge is a **measurement instrument**, not truth.

That distinction becomes even more important under optimization.

The classic LLM-as-judge work found position, verbosity, self-enhancement and reasoning limitations even while showing useful agreement with human preferences. citeturn685573view1 More generally, reward-model work has demonstrated exactly the Goodhart problem you are worried about: optimize an imperfect proxy far enough and proxy reward can improve while the underlying objective deteriorates. citeturn685573view0

So I would explicitly model

$$
\hat U(\tau)
$$

as *measured/proxy utility*, while the inaccessible thing you actually care about is

$$
U(\tau).
$$

The optimization system should never lose that distinction.

That suggests three authorities:

```text
Development evaluator
      │
      │ gives dense optimizer feedback
      ▼
Optimizer

Selection / hidden evaluator
      │
      │ limited exposure
      ▼
Promotion candidate

Human / production evidence
      │
      ▼
Deployment authority
```

In other words, the system that helps you search should not necessarily be the system allowed to certify the winner.

This aligns very closely with the evaluator-exploitation work already in the Coinvault design docs.

## Data exposure should become a first-class mathematical concept

Your held-out validation checks are already good. Generalize them into dataset roles and exposure accounting.

I would model something like:

$$
\mathcal D
=
D_{\text{diagnostic}}
\cup
D_{\text{development}}
\cup
D_{\text{calibration}}
\cup
D_{\text{selection}}
\cup
D_{\text{promotion}}
\cup
D_{\text{shadow}}.
$$

Each campaign records which agent had access to what.

The optimizer can inspect diagnostic trajectories and development scores. It should have little or no access to promotion examples or their detailed feedback.

If promotion fails and you feed those exact failures into GEPA, those examples are no longer hidden. That's fine—but it should start a new campaign/validation epoch with a fresh held-out set.

This is particularly important for reflective optimizers because GEPA is deliberately very efficient at extracting lessons from a handful of rich trajectories. citeturn124026view0 The same property that makes it powerful makes leakage very valuable to the optimizer.

## Promotion should be a different algorithm from optimization

Don't let “best optimizer score” mean “deploy.”

You already mostly do this with gates.

Formally, for paired target deltas, you might require something like

$$
LCB_{1-\alpha}
\left(
E[\Delta_{\text{target}}]
\right)
>
\delta_{\min}
$$

while simultaneously requiring regression constraints such as

$$
UCB_{1-\alpha}
\left(
-\Delta_j
\right)
<
\epsilon_j.
$$

The exact frequentist/Bayesian machinery can vary. The important architectural part is that the **selection rule consumes statistical evidence but is not the search algorithm**.

Adaptive optimization also creates repeated-selection bias. If you test 300 prompt variants on the same 100 examples and report the best one, ordinary confidence intervals around that winner don't magically account for the search process. Hidden validation, exposure accounting, paired designs, and possibly sequential/multiple-testing corrections should all fit into `selection`, rather than being left to individual optimizer implementations.

## Pareto should be a first-class archive concept

A candidate $a$ dominates $b$ when it is no worse on every relevant search objective and strictly better on at least one:

$$
a \succ b
\iff
\forall k,\; J_k(a)\ge J_k(b)
\quad\land\quad
\exists k,\;J_k(a)>J_k(b).
$$

Then the optimizer maintains

$$
\mathcal P =
\{\theta :
\nexists \theta' \text{ such that } \theta' \succ \theta\}.
$$

This does not mean deployment has to use Pareto selection. Your deployment logic can still be lexicographic and conservative.

The Pareto archive is useful to **search**, especially because different candidates may contain complementary improvements. That's part of the central GEPA idea. citeturn124026view0

## Concrete changes I would make to the existing code

`ragopt.Outcome.Metrics` is the first thing I would retire. Keep a compatibility projection if necessary, but make authoritative results typed measurements with protocol identity, evidence references, missingness/applicability, uncertainty, and provenance.

`eval.RunRequest{Incumbent, Challenger}` should become a specialized `PairedTrial`, not the universal execution primitive. The general core should know about candidate sets/trials/episodes; paired incumbent/challenger remains a very important experiment strategy.

`Candidate.Mutation` should become general `Patch`. RagOpt can retain `ExactlyOneVariable` as a candidate-validation policy.

The treatment switch in `knowledge_ragopt_treatment.go` should become a product-level variable registry. Prompts, rerankers, retrieval depths, tool descriptions, routing configurations, etc. each register their domains/materializers instead of requiring an ever-larger central branch.

The existing RunStore should remain useful as the durable **trial/episode artifact store**. Put a persistent campaign event store above it rather than turning RunStore itself into an adaptive optimizer.

Evaluator identities currently implicit in candidate/proposer version history should become explicit protocol references and measurement epochs.

The current completed-run TUI can then be rebuilt over projections from the campaign journal. A plan view, live view, and retrospective view are merely different projections over the same campaign semantics.

FlowKit's own `StepReport`/ledger machinery is still the right lower-level instrumentation layer; its developer guide already treats reports and ledgers as observers over execution. fileciteturn2file0L2-L3 `optkit` should subscribe to/translate those facts rather than duplicate execution mechanics.

## Give the core laws, not just interfaces

One particularly good thing in your evidence-ledger design work is the attempt to state laws mathematically. I'd do the same for `optkit`.

The laws I would put near the top of the design document are: **replay determinism**—the persisted journal reconstructs the same campaign state; **prefix stability**—later events never rewrite prior candidate/result identity; **semantic identity invariance**—worker count, retries and scheduling don't change candidate identity; **rejection purity**—a failed candidate cannot mutate the incumbent; **measurement-epoch isolation**—different protocol digests aren't silently aggregated; **hidden-set non-interference**—proposal decisions cannot depend on data designated inaccessible to the optimizer; **budget conservation**—resource consumption can't exceed admitted campaign limits; **complete lineage**—every promoted snapshot has a path through parent, patch, evidence and decision; and **hard-gate non-compensation**—soft improvement cannot offset a violated hard constraint.

Those are much more valuable than choosing whether one Go interface has three methods or four. They tell you what every future implementation must preserve.

## How I'd migrate without rewriting what works

1. **Write the optimization vocabulary and laws first.** Define `Snapshot`, `Variable`, `Patch`, `Candidate`, `Episode`, `Trajectory`, `Measurement`, `Objective`, `Constraint`, `Trial`, `Campaign`, `Plan`, `Optimizer`, `Archive`, `Decision`, and their identities/digests. Don't add automated search yet.

2. **Put a compatibility campaign layer around current RagOpt.** One current run becomes a campaign with a paired trial; existing candidate folders become imported lineage. Current behavior should remain byte-for-byte/evidence-for-evidence equivalent where possible.

3. **Introduce the campaign journal and projections.** Make the journal authoritative for control history while RunStore/native Coinvault traces remain authoritative for heavy artifacts.

4. **Build plan/live/history UI from those projections.** Use Coinvault's existing event/session infrastructure for transport. This immediately validates whether the conceptual model is adequate before you automate optimization.

5. **Replace Coinvault's treatment switch with the variable registry.** Express the existing optimization history as typed coordinates in $\Theta$.

6. **Extract truly generic RagOpt pieces into `optkit`.** Candidate lineage, generic campaign state, Pareto/archive, statistics, event store, planning and selection belong there. RAG-specific objectives/adapters remain in `ragopt`.

7. **Implement deliberately boring optimizers first.** Manual proposal, random search, coordinate search, k-sparse search and Pareto maintenance are useful correctness tests for the abstraction.

8. **Add a GEPA-like reflective optimizer.** Reflection gets selected trajectories + JudgeKit evidence, emits diagnosis + structured patches, evaluates them on development data, and updates the archive. Every reflection/proposal is itself an immutable artifact/event.

9. **Then add MIPRO/TextGrad-style approaches where needed.** The same substrate can support surrogate-assisted multi-component search and textual credit assignment without changing Campaign/Episode/Measurement.

10. **Add actual RL only if a use case requires policy-weight updates.** By then, `Episode`, trajectory capture, rewards/measurements, budgets and promotion are already available; RL is just another producer of candidates/policies.

## What I think the end state should feel like

A user should be able to write something roughly conceptually equivalent to:

```go
campaign := opt.NewCampaign(
    opt.System(coinvaultSystem),
    opt.Space(
        Prompt("routing"),
        Prompt("grounding"),
        Int("result_limit", 4, 20),
        Choice("reranker", rerankers...),
        Choice("tool_description", toolDescriptions...),
    ),
    opt.Data(dev, calibration, hidden),
    opt.Measure(judgeSuite),
    opt.Constraints(productConstraints),
    opt.Search(gepaOptimizer),
    opt.Budget(...),
    opt.Promotion(...),
)
```

and the framework naturally knows how to represent:

```text
what can change
what cannot change
what is being attempted
why this candidate was proposed
what executions it caused
all resulting trajectories
what was measured
which measurement protocol produced it
what it cost
what the optimizer learned from it
which candidate lineage emerged
what is currently Pareto-optimal
why something was rejected
what hidden data has been consumed
why the final candidate was promoted
what deployed configuration it produced
```

That is the reusable thing.

The main architecture I would **not** choose is a generic “LLM optimizer framework” centered around prompts and scores. Coinvault has already outgrown that model. What you have is closer to a **versioned experimental control system for optimizing stochastic compound programs**. LLMs happen to make unusually powerful proposal, critique, measurement, and policy components inside it.

And that framing is broad enough to optimize RAG, multi-turn agents, tool policies, UI/widget behavior, ordinary non-LLM parameters, and eventually learned policies without changing the mathematical center of the system.


---

> walk me through the exact optimization loop that coinvault implements and use that as a way to explain th emaths to me.

I’m going to trace Coinvault’s actual production optimization path end-to-end—candidate generation, materialization, evaluation, gating, promotion, and iteration—then map each concrete step to the mathematical object it corresponds to. I’ll use the code and design docs in the archive rather than abstracting from the earlier summary.

```unknown
bash -lc rm -rf /mnt/data/rag-self-improvement && mkdir -p /mnt/data/rag-self-improvement && unzip -q /mnt/data/rag-self-improvement.zip -d /mnt/data/rag-self-improvement && find /mnt/data/rag-self-improvement -maxdepth 2 -type d | sed 's#^#/##' | head -80
```

```unknown
bash -lc cd /mnt/data/rag-self-improvement/coinvault && printf '\n-- filenames --\n' && find . -type f | grep -Ei 'ragopt|optim|treatment|candidate|eval|promotion|judge|experiment' | head -200 && printf '\n-- symbols --\n' && rg -n -i 'ragopt|treatment|candidate|incumbent|challenger|promot|optimi[sz]|gate|paired|mutation' --glob '*.go' --glob '*.md' --glob '*.yaml' --glob '*.json' | head -350
```

```unknown
bash -lc cd /mnt/data/rag-self-improvement/coinvault && find ttmp docs internal cmd -type f \( -name '*.md' -o -name '*.go' \) -print0 | xargs -0 rg -l -i 'ragopt|self[- ]?optim|optimization loop|incumbent|challenger|treatment-contract|gate-policy' | head -120
```

```unknown
bash -lc cd /mnt/data/rag-self-improvement/coinvault && for f in \
 ttmp/2026/08/07/GEC-RAG-OPT-002--scientifically-valid-continuous-rag-optimization-program/design-doc/01-intern-guide-to-scientifically-valid-gec-rag-optimization.md \
 ttmp/2026/08/07/GEC-RAG-OPT-002--scientifically-valid-continuous-rag-optimization-program/design-doc/05-evaluation-judging-and-optimization-textbook.md \
 ttmp/2026/08/17/COINVAULT-045--study-self-optimization-and-exploitable-evaluator-errors/design-doc/08-coinvault-through-the-lens-of-chapters-2-to-4.md \
 ttmp/2026/08/05/GEC-RAG-OPT-001--retrieval-optimization-reranker-eval-growth-and-benchmarked-retrieval-experiments/design-doc/02-deep-review-from-ad-hoc-retrieval-tuning-to-reproducible-self-optimization.md; do echo; echo "===== $f ====="; rg -n '^#{1,4} ' "$f" | head -160; done
```

```unknown
bash -lc cd /mnt/data/rag-self-improvement/coinvault && f='ttmp/2026/08/17/COINVAULT-045--study-self-optimization-and-exploitable-evaluator-errors/design-doc/08-coinvault-through-the-lens-of-chapters-2-to-4.md'; sed -n '132,199p' "$f"; echo '\n--- current variables ---'; sed -n '303,466p' "$f"; echo '\n--- safe architecture ---'; sed -n '644,769p' "$f"
```

```unknown
bash -lc cd /mnt/data/rag-self-improvement/coinvault && f='ttmp/2026/08/07/GEC-RAG-OPT-002--scientifically-valid-continuous-rag-optimization-program/design-doc/01-intern-guide-to-scientifically-valid-gec-rag-optimization.md'; sed -n '376,475p' "$f"; echo '\n--- textbook loop ---'; f2='ttmp/2026/08/07/GEC-RAG-OPT-002--scientifically-valid-continuous-rag-optimization-program/design-doc/05-evaluation-judging-and-optimization-textbook.md'; sed -n '175,244p' "$f2"; sed -n '284,520p' "$f2"; sed -n '566,620p' "$f2"
```

<details><summary>💭 Thinking</summary>

**Inspected CoinVault optimization files and lifecycle design documentation**

</details>

The concrete loop is narrower than “self-training”: Coinvault does **offline hypothesis → one controlled mutation → paired whole-agent execution → deterministic eligibility checks → judge measurements → lexicographic gate → reproduction → held-out validation → human/non-applying promotion plan**. The next useful step is to unpack that loop one stage at a time and show where the mathematical objects enter, because several pieces that sound like “reward” are actually constraints or validity checks.

```unknown
bash -lc cd /mnt/data/rag-self-improvement/coinvault && sed -n '1,280p' cmd/coinvault/cmds/knowledge_ragopt.go && printf '\n===== treatment =====\n' && sed -n '1,320p' cmd/coinvault/cmds/knowledge_ragopt_treatment.go && printf '\n===== gate =====\n' && sed -n '1,300p' cmd/coinvault/cmds/knowledge_ragopt_gate.go
```

```unknown
bash -lc cd /mnt/data/rag-self-improvement/coinvault && rg -n '^func .*GECRagopt|^func \(c \*KnowledgeRagoptCommand\)' cmd/coinvault/cmds/knowledge_ragopt.go cmd/coinvault/cmds/knowledge_ragopt_case.go cmd/coinvault/cmds/knowledge_ragopt_trace.go cmd/coinvault/cmds/knowledge_ragopt_contract.go cmd/coinvault/cmds/knowledge_ragopt_treatment.go | head -220
```

```unknown
bash -lc cd /mnt/data/rag-self-improvement/coinvault && sed -n '151,284p' cmd/coinvault/cmds/knowledge_ragopt.go && sed -n '330,725p' cmd/coinvault/cmds/knowledge_ragopt.go
```

```unknown
bash -lc cd /mnt/data/rag-self-improvement/ragopt && printf '%s\n' '--- package files ---' && find pkg -maxdepth 2 -type f -name '*.go' | sort && printf '%s\n' '--- candidate API ---' && sed -n '1,320p' pkg/candidate/*.go && printf '%s\n' '--- eval API symbols ---' && rg -n '^type |^func ' pkg/eval/*.go | head -240 && printf '%s\n' '--- gate/policy/compare symbols ---' && rg -n '^type |^func ' pkg/compare/*.go pkg/gate/*.go pkg/policy/*.go | head -260
```

```unknown
bash -lc cd /mnt/data/rag-self-improvement/ragopt && echo '=== eval types ==='; sed -n '1,280p' pkg/eval/types.go; echo '=== runner ==='; sed -n '1,360p' pkg/eval/runner.go; echo '=== compare types ==='; sed -n '1,180p' pkg/compare/types.go; echo '=== gate evaluate ==='; sed -n '1,390p' pkg/gate/evaluate.go; echo '=== policy ==='; sed -n '1,220p' pkg/policy/policy.go
```

```unknown
bash -lc cd /mnt/data/rag-self-improvement/coinvault && rg -n 'func gecRagoptSplit|validation.*closed|fresh-root|reproduction|reproduce|split' cmd/coinvault/cmds/knowledge_ragopt*.go | head -160 && sed -n '280,350p' cmd/coinvault/cmds/knowledge_ragopt.go && echo '\n--- candidate examples ---' && for f in configs/ragopt/grounded-answer-v2/candidate.yaml configs/ragopt/comparison-intent-v3/candidate.yaml configs/ragopt/qwen3-reranker-pool12-v1/candidate.yaml configs/ragopt/source-role-routing-v2/candidate.yaml; do echo =====$f=====; cat "$f"; done
```

```unknown
bash -lc cd /mnt/data/rag-self-improvement/coinvault && echo '=== grounded-answer-v2 gate policy ==='; cat configs/ragopt/grounded-answer-v2/shared/gate-policy.yaml; echo '\n=== grounded-answer-v2 terminal decision note ==='; sed -n '1,260p' ttmp/2026/08/07/GEC-RAG-OPT-002--scientifically-valid-continuous-rag-optimization-program/reference/31-grounded-answer-v2-terminal-decision.md; echo '\n=== comparison formulas ==='; cd /mnt/data/rag-self-improvement/ragopt && sed -n '1,350p' pkg/compare/build.go; echo '\n=== gate first 280 ==='; sed -n '1,285p' pkg/gate/evaluate.go
```

```json
{"paths":["files"]}
```

<details><summary>💭 Thinking</summary>

**Inspected RAG optimization, execution, validation, evaluation, and gate policies**

</details>

```python3
{"path":"/files/search","args":{"search_query":[{"q":"CoinVault current optimization loop candidate authoring frozen experiment identity paired execution terminal decision"},{"q":"Standard candidate lifecycle diagnose a measured failure declare one mutation feedback reproduction validation"},{"q":"grounded-answer-v2 terminal feedback decision paired faithfulness deltas"}],"top_k":10,"result_format":"snippets"}}
```

<details><summary>💭 Thinking</summary>

**Searched ZIP contents for optimization-loop guidance**

</details>

```unknown
bash -lc cd /mnt/data/rag-self-improvement/ragopt && rg -n 'func execute|scheduledCell|Incumbent|Challenger|for .*Cases|for .*repeat|schedule' pkg/eval/runner.go && sed -n '250,620p' pkg/eval/runner.go
```

```unknown
bash -lc cd /mnt/data/rag-self-improvement/ragopt && sed -n '221,315p' pkg/eval/runner.go && sed -n '1,150p' pkg/compare/types.go && sed -n '150,290p' pkg/compare/build.go
```

```unknown
bash -lc cd /mnt/data/rag-self-improvement/coinvault && sed -n '756,1085p' cmd/coinvault/cmds/knowledge_ragopt.go && echo '\n=== answer contract stages ==='; sed -n '1,330p' cmd/coinvault/cmds/knowledge_ragopt_contract.go
```

```unknown
bash -lc cd /mnt/data/rag-self-improvement/coinvault && rg -n '^func \(e \*gecRagoptCellExecutor\) Run' cmd/coinvault/cmds/knowledge_ragopt.go && sed -n '430,756p' cmd/coinvault/cmds/knowledge_ragopt.go
```

<details><summary>💭 Thinking</summary>

**Mapping the protocol**

I’m modeling the loop as human-proposed candidates, preflight checks, paired feedback trials, deterministic contract validation, judgment, lexicographic gates, diagnostics, and promotion. The current command runs feedback only; validation remains a separate conceptual phase.

**Mapped the protocol**

**Inspected evaluation scheduling, resume logic, optimization contracts, and RAGOPT execution**

</details>

Yes. The easiest way to understand the math is to ignore the word “optimizer” for a moment and follow exactly what Coinvault does today.

There are really **two loops**:

1. an **inner automated experimental loop** that evaluates one proposed change;
2. an **outer human optimization loop** that looks at the result, diagnoses the next failure, and proposes the next change.

That distinction matters. Coinvault today is not an autonomous GEPA-like optimizer generating its own descendants. It is a **human-guided, one-coordinate-at-a-time, constrained black-box optimizer over a stochastic agent program**.

## 1. Start with: what is actually being optimized?

Coinvault is not optimizing “an answer.”

It is optimizing the configuration of this whole computation:

```text
question
   ↓
answer model
   ↓
tool decision ────────────────┐
   ↓                          │
knowledge_search / SQL        │
   ↓                          │
query transformation          │
   ↓                          │
lexical + vector retrieval    │
   ↓                          │
authorization                 │
   ↓                          │
fusion / reranker             │
   ↓                          │
evidence ledger ──────────────┘
   ↓
answer model continues
   ↓
answer + citations
```

Call the entire executable Coinvault system

$$
S_\theta
$$

where $\theta$ represents its configurable parts.

From the current treatment machinery, $\theta$ is approximately:

$$
\theta =
(
d_{\text{default}},
d_{\text{forced}},
q_{\text{comparison}},
i_{\text{comparison}},
p_{\text{grounding}},
p_{\text{routing}},
p_{\text{policy}},
\rho_{\text{reranker}},
d_{\text{tool}}
)
$$

Those correspond directly to things Coinvault has actually experimented with:

```text
knowledge_tool_default_results
knowledge_tool_forced_results
knowledge_comparison_decomposition
knowledge_comparison_intent
answer_grounding_prompt
answer_routing_prompt
answer_policy_prompt
knowledge_reranker
knowledge_tool_description
```

Some coordinates are integers. Some are prompts. Some are structured plans. Some are model/configuration choices.

So $\theta$ is **not a normal real-valued vector**. It's a point in a heterogeneous product space:

$$
\Theta =
\Theta_1\times\Theta_2\times\cdots\times\Theta_k
$$

where one space might contain integers, another arbitrary text, another structured YAML, another model configurations.

That's the first important piece of mathematical grounding.

---

# 2. The outer loop starts with a failure

The actual Coinvault optimization process starts with something going wrong.

For example:

```text
Question:
Compare Morgan dollars with Peace dollars.

Observed:
retrieval found both kinds of evidence

But:
final answer made claims not entailed by that evidence
```

Coinvault then diagnoses the **earliest failing stage**.

The practical decision tree in the project is essentially:

```text
Did the proposed treatment actually execute?
        no → treatment / observability problem

Did required evidence make it through?
        no → retrieval problem

Did it choose the wrong backend/tool?
        yes → routing problem

Was the evidence adequate but answer unsupported?
        yes → generation/grounding problem

Was the answer actually correct but evaluator rejected it?
        yes → evaluator/contract problem
```

Mathematically, you can think of a trajectory as passing through components

$$
z_0
\to z_1
\to z_2
\to \dots
\to z_T
$$

and you're trying to assign observed loss $L$ to a component.

Coinvault doesn't calculate derivatives for this. Instead a human does causal diagnosis:

$$
\text{failure evidence}
\longrightarrow
\text{hypothesized responsible coordinate }j.
$$

That's why I described it earlier as a **human textual gradient**.

The “gradient” isn't

$$
\nabla_\theta L.
$$

It's something more like:

$$
g_{\text{text}}
=
\text{“retrieval succeeded; answer exceeded admitted evidence;
strengthen grounding instructions.”}
$$

That critique then tells you **which coordinate to change**.

---

# 3. Coinvault then creates exactly one mutation

Suppose the deployed/current configuration is

$$
\theta_n.
$$

The human proposes a mutation

$$
\delta_n.
$$

Coinvault/RagOpt enforces that exactly one mutable asset actually changes.

So the challenger becomes

$$
\theta'_n
=
\theta_n \oplus \delta_n
$$

with

$$
|\operatorname{support}(\delta_n)| = 1.
$$

That's the exact mathematical statement of RagOpt's `candidate must change exactly one mutable asset` invariant.

You can also describe it as Hamming distance:

$$
d_H(\theta_n,\theta'_n)=1.
$$

For `grounded-answer-v2`, for example:

```text
everything else      = identical
comparison retrieval = identical
bundle               = identical
models               = identical
authorization        = identical
evidence ledger      = identical

answer grounding prompt:
    parent → challenger version
```

So:

$$
\theta'
=
(\theta_1,\ldots,\theta_{j-1},
\theta'_j,
\theta_{j+1},\ldots,\theta_k).
$$

This is **coordinate search**.

Not gradient descent.

Not RL training.

Not yet evolutionary search.

It is basically experimentally controlled coordinate descent over a compound program.

---

# 4. The candidate also has to state a causal hypothesis

This is important.

Coinvault doesn't merely say:

> try prompt B.

The candidate includes something structurally like:

```yaml
mutation:
  asset: answer_grounding_prompt

  hypothesis:
    requiring direct clause-level entailment and adjacent citations
    will reduce unsupported comparison claims

  expected_improvement:
    metric: faithfulness
    groups:
      - feedback
      - comparison

  regression_risks:
    - answers may become too terse
    - synthesis may be omitted
    - citation density may hurt readability
```

Mathematically, this says:

> I predict that intervening on coordinate $j$, while holding the rest constant, will increase metric $m$ on population $G$.

Something like:

$$
H_1:
E[
m(S_{\theta'}(X))
-
m(S_{\theta}(X))
\mid X\in G
]
> 0.
$$

And it states anticipated side effects:

$$
E[
r_k(S_{\theta'}(X))
-
r_k(S_{\theta}(X))
]
\ge -\epsilon_k.
$$

That makes each candidate a **falsifiable intervention**, rather than just another version.

---

# 5. Before running anything, Coinvault freezes the experiment

The next part is unusually important and is one of the strongest parts of your system.

The candidate contains/fixes things like:

```text
parent snapshot
challenger snapshot
candidate digest
changed asset
locked assets

suite digest
gate-policy digest
bundle identity
source revision

answer runtime identity
judge runtime identity

retrieval policy identity
query transform identity
evidence ledger identity

provider budgets
```

Call the complete frozen experiment identity

$$
\phi.
$$

Then the experiment really means:

$$
E(\theta,\theta';D,M,G,\phi).
$$

Without $\phi$, saying:

> prompt B beat prompt A

is weak because maybe the corpus changed, or the model changed, or the judge changed, or the retrieval bundle changed.

Coinvault is saying:

$$
\theta\neq\theta'
$$

in one permitted coordinate while

$$
\phi_{\text{incumbent}}
=
\phi_{\text{challenger}}
$$

everywhere that is supposed to remain invariant.

That's what gives the experiment causal interpretability.

---

# 6. Then there is a preflight

The command currently loads and validates all of this before an evaluation run starts.

There is even a provider-free mode.

Conceptually, preflight is checking whether

$$
\theta,\theta' \in \Theta_{\mathrm{valid}}.
$$

Think of

$$
\Theta_{\mathrm{valid}}
\subseteq
\Theta
$$

as the part of parameter space you're actually allowed to experiment with.

For Coinvault this excludes things like:

```text
changing authorization
silently changing bundle identity
altering hidden evaluation data
changing multiple assets
mismatched runtime revisions
unbounded provider spend
untraceable reranker configuration
```

So before asking:

$$
\text{“is }\theta'\text{ better?”}
$$

it asks:

$$
\text{“is }\theta'\text{ even a valid experimental intervention?”}
$$

Very different question.

---

# 7. Now we get to the most RL-looking part: execute a full trajectory

For every evaluation case $x_i$, Coinvault executes both configurations.

Current RagOpt scheduling literally does:

```text
case 1:
    incumbent
    challenger

case 2:
    incumbent
    challenger

...
```

The current feedback suite has 12 cases and one repeat, so:

$$
12 \times 2 \times 1 = 24
$$

cells.

A **cell is not one LLM call**.

A cell is the entire Coinvault interaction.

That means, for one case:

$$
\tau_{i,a}
\sim
P(\tau\mid x_i,\theta_a)
$$

where

$$
a\in\{0,1\}
$$

means incumbent versus challenger.

And $\tau$ can look like:

$$
\tau =
(s_0,a_0,o_1,a_1,o_2,\ldots,a_T).
$$

For example:

```text
user question
↓
model reasoning / tool decision
↓
knowledge_search(...)
↓
retrieval results
↓
model decides another tool is needed
↓
sql_doc(...)
↓
tool result
↓
model generates final answer
↓
citations / output
```

This is exactly where an RL/POMDP mental model becomes useful.

---

# 8. The Coinvault chat can be represented as a POMDP

At time $t$, let the visible history be

$$
h_t =
(x,a_0,o_1,\ldots,o_t).
$$

The Coinvault agent acts according to a policy

$$
a_t
\sim
\pi_\theta(a\mid h_t).
$$

Its actions aren't just words.

They include:

$$
a_t \in
\{
\text{emit text},
\text{knowledge\_search},
\text{sql query},
\text{request another tool},
\text{finish}
\}.
$$

The environment responds with

$$
o_{t+1}
\sim
P(o\mid h_t,a_t).
$$

Eventually you get a trajectory

$$
\tau
=
(h_0,a_0,o_1,\ldots,a_T).
$$

So **the thing Coinvault evaluates is already an agent trajectory**, which is why your eventual generic optimizer absolutely should have trajectory as a core concept.

But an important subtlety:

Coinvault currently does **not** perform RL updates like

$$
\theta
\leftarrow
\theta+\alpha\nabla_\theta J.
$$

Instead it executes two fixed policies/configurations and experimentally selects between them.

---

# 9. Coinvault records the trajectory instead of reducing immediately to a score

During the run, the trace collector records things such as:

```text
provider calls
tool calls
knowledge searches
requested result limits
effective result limits
query-transform identities
retrieval-policy identities
reranker application
evidence admitted
SQL/tool routes
final answer
citations
token usage
terminal status
```

So Coinvault first gets

$$
\tau
$$

and only afterwards derives measurements

$$
M(\tau).
$$

This is a crucial design decision.

You do **not** want the optimization system to see only

```text
reward = 0.83
```

because then you can't diagnose why anything happened.

You want:

$$
\tau
\xrightarrow{\text{measurements}}
M.
$$

That is what enables later GEPA-style reflection.

---

# 10. The first evaluator asks: did our intervention actually happen?

This is the surprisingly subtle treatment-exercise check.

Suppose you change:

```text
default_results: 5 → 8
```

You might assume the challenger got eight results.

But the production agent can explicitly call:

```text
knowledge_search(limit=5)
```

in which case your changed default does nothing.

That's exactly a failure Coinvault encountered historically.

So Coinvault computes a predicate like

$$
E(\tau,\delta)\in\{0,1\}
$$

meaning:

> was the intended treatment actually exercised in the runtime behavior?

For default depth it looks at things like:

$$
\text{configured default},
\text{requested limit},
\text{effective limit},
\text{effective limit source}.
$$

For a prompt:

$$
E=1
$$

only if the correct prompt suffix digest was actually active.

For a reranker:

$$
E=1
$$

only if the expected reranker configuration and application are observed.

This is mathematically an **instrument/manipulation check**.

In experimental science, before concluding

$$
X \to Y
$$

you verify that your manipulation of $X$ really changed $X$.

Coinvault does exactly that.

If

$$
E(\tau,\delta)=0
$$

then the outcome is:

```text
treatment_not_exercised
```

not:

```text
candidate had no quality benefit
```

Those are fundamentally different conclusions.

---

# 11. Then deterministic contracts are applied

Next Coinvault constructs an answer contract.

For a case $x_i$ and trajectory $\tau$, think of it as

$$
C(x_i,\tau)
\in
\{0,1\}.
$$

It contains checks for things like:

```text
required route happened
forbidden route didn't happen

required evidence groups were present

citation IDs resolve to admitted evidence
knowledge evidence was cited

no unresolved runtime failures
projection completed properly

protected abstention cases behaved appropriately
```

Formally, there are multiple predicates

$$
c_1(x,\tau),
c_2(x,\tau),
\dots,
c_q(x,\tau)
$$

and

$$
C(x,\tau)
=
\bigwedge_{j=1}^{q}
c_j(x,\tau).
$$

This is one of the biggest reasons I would **not** describe Coinvault as having a simple reward function.

These are not little negative rewards.

They are validity/feasibility constraints.

If the agent uses a forbidden SQL route, you don't want:

$$
reward = quality - 0.2.
$$

You want:

$$
\text{invalid candidate behavior}.
$$

---

# 12. Only after those checks does the LLM judge run

The actual cell logic is essentially:

```text
run system
   ↓
collect trajectory
   ↓
answer contract
   ↓
treatment exercise
   ↓
any issues?
   ├── yes → don't call judge
   └── no
        ↓
      LLM judge
```

That's very good architecture.

Let the judge be an instrument

$$
J_\psi(\tau,x)
$$

where $\psi$ identifies the judge model + protocol.

It returns qualitative metrics like

$$
J_\psi(\tau,x)
=
(
F,R,A,\ldots
)
$$

where for example:

$$
F=\text{faithfulness}
$$

$$
R=\text{answer relevance}
$$

$$
A=\text{abstention judgment}.
$$

Coinvault then derives things such as unsupported-claim rate:

$$
U =
\frac{
N_{\text{statements}}-N_{\text{supported}}
}{
N_{\text{statements}}
}.
$$

So each successful cell ends up with a metric vector approximately:

$$
m_{i,a}
=
\begin{bmatrix}
F\\
R\\
U\\
\text{citation validity}\\
\text{evidence satisfaction}\\
\text{route compliance}\\
\text{provider calls}\\
\text{tokens}\\
\vdots
\end{bmatrix}.
$$

Again: **vector**, not scalar reward.

---

# 13. Failures are first-class outcomes

There's also a precedence/order for assigning a failure class.

The current code roughly says:

```text
generation contract failure
    ↓ else
treatment not exercised
    ↓ else
other contract failure:
    route / retrieval / contract
    ↓ else
judge failure
```

And execution failures/timeouts have separate classes.

So the complete outcome is closer to

$$
O(\tau)
=
(
\text{validity},
\text{failure class},
m(\tau),
\text{cost},
\text{artifacts}
).
$$

This matters because a failed cell is **not silently dropped from the experiment**.

That's critical mathematically: missing/nonvalid observations should not magically disappear and make the mean look better.

---

# 14. Then RagOpt makes the comparison paired

Now we get the most important statistic.

For case $i$:

$$
m_{i,0}
=
m(\tau_{i,\text{incumbent}})
$$

and

$$
m_{i,1}
=
m(\tau_{i,\text{challenger}}).
$$

RagOpt calculates:

$$
\Delta_i^{(m)}
=
m_{i,1}^{(m)}
-
m_{i,0}^{(m)}.
$$

So, for faithfulness:

$$
\Delta_i^{F}
=
F(\tau_{i,1})
-
F(\tau_{i,0}).
$$

This is much better than just:

$$
\bar F_{\text{challenger}}
-
\bar F_{\text{incumbent}}
$$

over unrelated samples.

Why?

Because question difficulty gets canceled out to some extent.

Imagine:

```text
easy question:
  incumbent    .95
  challenger   .97

hard question:
  incumbent    .40
  challenger   .65
```

The meaningful data are:

$$
+0.02,\quad+0.25.
$$

Not merely comparing populations whose difficulty composition could differ.

Thus the experimental unit is a pair:

$$
(x_i,\theta,\theta').
$$

---

# 15. Then Coinvault aggregates paired deltas by groups

Cases have groups such as:

```text
feedback
comparison
knowledge_only
mixed_sql_knowledge
ambiguity
protected
...
```

For group $G$, the target metric becomes:

$$
\bar{\Delta}_{G}^{(m)}
=
\frac{1}{|G|}
\sum_{i\in G}
\Delta_i^{(m)}.
$$

RagOpt also records:

$$
\text{wins}
=
|\{i:\Delta_i>0\}|
$$

$$
\text{losses}
=
|\{i:\Delta_i<0\}|
$$

and ties.

It computes cost deltas the same way:

$$
\Delta_i^{\text{tokens}}
=
T_{i,\text{candidate}}
-
T_{i,\text{incumbent}}.
$$

Same for:

$$
\Delta \text{provider calls},
\quad
\Delta \text{tool calls},
\quad
\Delta \text{latency}.
$$

---

# 16. Now comes the optimization objective—but it is lexicographic

This is probably the single most important mathematical insight about Coinvault.

It does **not** optimize something like:

$$
J =
0.4F+
0.3R-
0.1\text{cost}.
$$

Instead, the gate evaluates stages in strict order:

$$
\text{identity}
\prec
\text{hard constraints}
\prec
\text{target improvement}
\prec
\text{regressions}
\prec
\text{cost}.
$$

Meaning:

> you don't even get to consider a later phase if an earlier one fails.

So this is a **lexicographically constrained optimization problem**.

---

# 17. Concrete example: `grounded-answer-v2`

Its frozen policy is particularly illustrative.

The hard gates require:

$$
\text{all cells present}
$$

$$
\text{all challenger cells completed}
$$

$$
\text{all challenger contracts valid}
$$

$$
\text{failure rate}=0
$$

and

$$
F_i^{candidate}\ge0.80
\qquad
\forall i.
$$

Then the target is faithfulness on feedback/comparison cases:

$$
\bar{\Delta}^{F}_{\text{comparison}}
\ge 0.
$$

Then regression constraints include:

$$
\Delta_i^{F}\ge -0.20
\qquad \forall i
$$

$$
\Delta_i^{R}\ge -0.30
\qquad \forall i
$$

plus mean overall regressions:

$$
\bar{\Delta}^{F}_{all}
\ge -0.05
$$

$$
\bar{\Delta}^{R}_{all}
\ge -0.05.
$$

Only after all of that do costs get considered.

---

# 18. And the actual grounded-answer experiment shows why this matters

For its two targeted comparison cases, the challenger did extremely well.

Morgan vs. Peace:

$$
\Delta F
=
1.0000-0.4595
=
+0.5405.
$$

Gold coins vs. bars:

$$
\Delta F
=
0.9615-0.3778
\approx
+0.5838.
$$

So average targeted improvement was roughly

$$
\bar{\Delta}F
\approx
0.562.
$$

Massive success.

Relevance also improved:

$$
+0.32
$$

and

$$
+0.23.
$$

If Coinvault used a normal scalar optimizer, that candidate would look fantastic.

But it had five other real product failures:

```text
route failures
retrieval failure
projection/contract failure
```

Therefore:

$$
H(\theta')=0
$$

for the hard feasibility predicate.

And Coinvault says:

$$
\boxed{\text{reject}}
$$

even though

$$
\bar\Delta F \gg 0.
$$

This is a perfect example of constrained optimization.

---

# 19. Mathematically, Coinvault's gate looks like this

Define the feasible candidate set:

$$
\mathcal F
=
\left\{
\theta'
:
\begin{array}{l}
\text{identity valid}\\
\text{all cells complete}\\
\text{contracts valid}\\
\text{failure rate}\le f_{\max}\\
m_k(\theta')\ge b_k
\end{array}
\right\}.
$$

Then only for

$$
\theta'\in\mathcal F
$$

do you examine the target:

$$
\max_{\theta'}
J_{\text{target}}(\theta').
$$

And even that is constrained by regression budgets:

$$
\Delta_i^{(k)}
\ge
-\epsilon_k.
$$

Finally, among candidates whose quality is acceptable, cost can break ties:

$$
\min
(
\text{calls},
\text{tokens},
\text{latency}
).
$$

This is much closer to how production systems ought to be optimized than collapsing everything into one magical reward number.

---

# 20. After the gate, Coinvault writes evidence rather than changing production

The current implementation automatically builds the comparison, runs the frozen gate, and writes:

```text
gate-decision.json
promotion-review.md
promotion-plan.json
```

Crucially:

$$
\text{gate pass}
\not\Rightarrow
\text{production mutation}.
$$

There is no automatic:

```go
deploy(challenger)
```

inside the optimizer.

That's another safety boundary.

---

# 21. If a candidate fails, that result feeds the outer optimization loop

This is the actual “self-improvement” cycle.

A failure gives you diagnostic evidence:

$$
H_n
=
\{
\theta_n,
\delta_n,
\tau_n,
M_n,
F_n
\}.
$$

A human examines that history and proposes:

$$
\delta_{n+1}
=
R(H_n)
$$

where $R$ is currently a **human reflector**.

So the whole loop is:

$$
\boxed{
H_n
\xrightarrow{\text{diagnose}}
\delta_{n+1}
\xrightarrow{\text{evaluate}}
O_{n+1}
\xrightarrow{\text{update history}}
H_{n+1}
}
$$

or in plain language:

```text
inspect failures
      ↓
identify earliest responsible component
      ↓
propose smallest plausible change
      ↓
freeze experiment
      ↓
execute paired Coinvault trajectories
      ↓
verify treatment happened
      ↓
deterministic contracts
      ↓
LLM judge
      ↓
paired comparison
      ↓
gate
      ↓
inspect result
      ↓
propose next change
```

That is the actual Coinvault optimization algorithm.

---

# 22. One subtle point: the current code only automates the feedback stage

The broader protocol says:

```text
feedback
   ↓ pass
fresh-root reproduction
   ↓ pass
held-out validation
   ↓
human promotion
```

But the current Coinvault `ragopt` command explicitly allows:

```text
split = feedback
```

and refuses:

```text
split = validation
```

with validation remaining closed.

So there is an important distinction between **implemented evaluator command** and **intended optimization protocol**.

Today, automated:

```text
candidate
→ preflight
→ feedback paired run
→ gate
→ promotion evidence
```

Then operator/protocol-driven:

```text
if pass:
    run independent fresh-root reproduction

if reproduced:
    expose held-out validation through controlled process

if validation passes:
    human promotion decision
```

That's important for the framework redesign: a future campaign controller should make these stages explicit rather than relying on operator procedure.

---

# 23. What happens after a rejection is particularly interesting

Take the grounded-answer example.

The conclusion was not:

> grounding prompt failed.

The conclusion was approximately:

```text
grounding intervention worked strongly on its intended failure

BUT

whole candidate cannot promote because other independent
routing/retrieval/contract failures exist
```

That then creates the next optimization instruction:

> Freeze the newly established grounding mechanism and attack the routing/abstention failure separately.

So:

$$
\theta_{n+1}
=
\theta_n\oplus\delta_{\text{grounding}}
$$

can become the conceptual new root once that component is accepted as established evidence, and then:

$$
\theta_{n+2}
=
\theta_{n+1}
\oplus
\delta_{\text{routing}}.
$$

This is literally coordinate descent through the compound system:

```text
retrieval depth
    ↓
comparison decomposition
    ↓
comparison intent
    ↓
grounding
    ↓
abstention / routing
    ↓
source-role routing
    ↓
reranker
    ↓
...
```

Except the direction isn't chosen from a numerical gradient.

It is chosen from **failure attribution**.

---

# 24. So what optimization algorithm is Coinvault actually running?

The closest formal description is:

### Constrained sequential black-box coordinate optimization

You have an unknown stochastic objective:

$$
J(\theta)
=
E_{x,\tau\sim S_\theta(x)}
[M(\tau)].
$$

You cannot differentiate it because $\theta$ includes:

```text
prompts
YAML
tool descriptions
retrieval settings
external models
conditional tool execution
```

So you experimentally query it.

At iteration $n$:

### Diagnose

$$
j_n
=
D(H_n)
$$

chooses the coordinate thought responsible for recoverable loss.

### Propose

$$
\theta'_n
=
\theta_n
\oplus
\delta_{j_n}.
$$

### Evaluate

$$
\hat J(\theta_n),
\quad
\hat J(\theta'_n)
$$

using matched trajectories.

### Compare

$$
\hat\Delta_n
=
\hat J(\theta'_n)
-
\hat J(\theta_n).
$$

### Apply constraints

$$
\theta'_n\in\mathcal F?
$$

### Select

$$
\theta_{n+1}
=
\begin{cases}
\theta'_n, & \text{if promotion criteria pass}\\
\theta_n, & \text{otherwise}.
\end{cases}
$$

### Reflect

Use failures to choose the next intervention.

That is Coinvault in mathematical shorthand.

---

# 25. Where the RL analogy fits exactly

Now we can be precise about RL.

Within one cell, Coinvault absolutely looks like an RL environment:

$$
s_t
\rightarrow
a_t
\rightarrow
r_t/o_{t+1}.
$$

The policy is:

$$
\pi_\theta(a_t\mid h_t).
$$

You observe an entire trajectory:

$$
\tau.
$$

And eventually you can derive terminal quality:

$$
R(\tau).
$$

So the **trajectory ontology** should absolutely borrow from RL.

But the outer update is not currently:

$$
\nabla_\theta
E_{\tau\sim\pi_\theta}
[R(\tau)].
$$

Instead:

```text
human proposes alternate policy configuration
→ run A/B trajectories
→ select/reject configuration
```

So it's closer to:

$$
\text{policy search}
$$

than

$$
\text{policy-gradient RL}.
$$

You could say Coinvault performs **experimental policy improvement without learned policy gradients**.

---

# 26. And this reveals exactly where GEPA would plug in

Currently the step:

$$
H_n
\xrightarrow{\text{human}}
\delta_{n+1}
$$

is done by an engineer.

GEPA-like automation replaces that one arrow:

$$
H_n
\xrightarrow{\text{LLM reflector}}
\delta_{n+1}.
$$

The rest of Coinvault's machinery can remain conceptually unchanged.

The reflector could receive:

```text
candidate definition
failed trajectories
successful trajectories
treatment reports
contract failures
judge assessments
paired deltas
cost deltas
```

and produce:

```text
diagnosis:
  evidence is present,
  route is correct,
  unsupported comparison clauses remain

proposed coordinate:
  answer_grounding_prompt

proposed patch:
  ...

hypothesis:
  ...

expected metric:
  faithfulness

risks:
  ...
```

Then the exact same experimental apparatus tests whether the textual gradient was actually useful.

That would turn:

$$
R_{\text{human}}
$$

into

$$
R_{\text{LLM}}.
$$

---

# 27. The generic framework should therefore model this equation

If I had to reduce the entire Coinvault system to one mathematical diagram, it would be:

$$
\boxed{
\begin{aligned}
H_n
&\xrightarrow{\text{reflector}}
\delta_n \\[4pt]
\theta'_n
&=
\theta_n\oplus\delta_n,
\qquad
|\operatorname{supp}(\delta_n)|=1 \\[4pt]
\tau^{0}_{i,r}
&\sim
S_{\theta_n}(x_i) \\[4pt]
\tau^{1}_{i,r}
&\sim
S_{\theta'_n}(x_i) \\[4pt]
E_{i,r}
&=
\text{TreatmentExercised}(\tau^1,\delta_n) \\[4pt]
C^a_{i,r}
&=
\text{Contract}(x_i,\tau^a_{i,r}) \\[4pt]
m^a_{i,r}
&=
M_\psi(x_i,\tau^a_{i,r}) \\[4pt]
\Delta^m_{i,r}
&=
m^1_{i,r}-m^0_{i,r} \\[4pt]
d_n
&=
G(
E,C,\Delta,
\text{cost},
\text{policy}
) \\[4pt]
\theta_{n+1}
&=
\begin{cases}
\theta'_n,&d_n=\text{promote}\\
\theta_n,&d_n=\text{reject}
\end{cases} \\[4pt]
H_{n+1}
&=
H_n\cup
\{
\delta_n,
\tau_n,
M_n,
d_n
\}.
\end{aligned}
}
$$

That is already a remarkably complete optimization framework.

---

# 28. And it tells us what your future `optkit` primitives should be

Each line above almost directly becomes a reusable object:

| Coinvault concept | Mathematical object | Generic optimization primitive |
|---|---|---|
| Current snapshot | $\theta_n$ | `Snapshot` |
| Mutable assets | $\Theta$ | `SearchSpace` / `Variable` |
| Candidate mutation | $\delta_n$ | `Patch` |
| Candidate manifest | hypothesis/intervention | `Candidate` |
| Feedback case | $x_i$ | `Case` |
| Incumbent/challenger | $\theta,\theta'$ | `Arm` |
| Complete chat run | $\tau$ | `Episode` / `Trajectory` |
| Treatment report | $E$ | `InterventionCheck` |
| Answer contract | $C$ | `Constraint` |
| Judge score | $M_\psi$ | `Measurement` |
| Paired comparison | $\Delta$ | `Comparison` |
| Gate policy | $G$ | `SelectionPolicy` |
| Candidate history | $H_n$ | `CampaignHistory` |
| Human diagnosis | $R(H)$ | `Optimizer` / `Reflector` |
| Run artifacts | experiment observations | `EventStore` / `ArtifactStore` |

And that, I think, is the key realization: **Coinvault has already implemented most of the semantics of the generic optimization framework. They are just currently distributed across product code, RagOpt, artifact conventions, and human procedure.**

The missing layer is the one that explicitly represents:

$$
\boxed{
\text{history}
\rightarrow
\text{proposal}
\rightarrow
\text{intervention}
\rightarrow
\text{trajectory}
\rightarrow
\text{measurement}
\rightarrow
\text{selection}
\rightarrow
\text{history}
}
$$

as a persistent first-class optimization process.


---

> Based on all this, design out optkit and write out how to port coinvault and rag-ttc over to using it and what tools need to be implemented and how. Incorporate the concept of UIs for visualizing the data. You don't need to implement them, but instead describe the architecture, work, pseudocode, ascii screenshots and such, so that an intern can make the best work of it. 
>
> Use the material you gathered, but rewrite and restructure it so it actually turns into a real pedagogical design, and after writing the first draft, go back and make sure each definition and term worth defining or introducing is properly motivated and defined and then applied in a few examples. Pretend you are a student reading the text and trying to make sense of it, and then rewrite it.  Make sure to introduce concepts by motivation, definition, then concrete worked examples. Use full prose paragraphs and lists and pseudocode and maths and api signatures and diagrams. Use callouts for expanding on fundamentals or side topics
>
> Output as markdown

```unknown
bash -lc ls -lh /mnt/data/rag-self-improvement.zip && rm -rf /mnt/data/rag-self-improvement && mkdir -p /mnt/data/rag-self-improvement && unzip -q /mnt/data/rag-self-improvement.zip -d /mnt/data/rag-self-improvement && find /mnt/data/rag-self-improvement -maxdepth 2 -type d | sed 's#^/mnt/data/rag-self-improvement##' | sort | head -200
```

```unknown
bash -lc ls -ld /mnt/data/rag-self-improvement /mnt/data/rag-self-improvement/* 2>/dev/null | head -50; find /mnt/data/rag-self-improvement -maxdepth 2 -printf '%m %u %g %p\n' | head -50
```

I’ll first reconstruct the existing Coinvault and rag-ttc optimization flows, then derive a self-contained OptKit design covering APIs, invariants, storage/events, migrations, UI projections, and implementation roadmap.

```unknown
bash -lc cd /mnt/data/rag-self-improvement && for r in coinvault judgekit rag-ttc ragkit ragopt; do echo "===== $r ====="; find "$r" -maxdepth 3 -type f | sed "s#^$r/##" | sort | head -250; echo; done
```

```unknown
bash -lc cd /mnt/data/rag-self-improvement && printf '%s\n' '=== Coinvault ragopt references ==='; rg -n --hidden -g '!**/.git/**' '\bragopt\b|treatment|candidate|gate-decision|promotion-review|promotion-plan|RunStore|runstore|treatment_exercised|treatment not exercised|feedback.*validation|validation.*feedback' coinvault | head -500; printf '%s\n' '=== rag-ttc optimization references ==='; rg -n --hidden -g '!**/.git/**' '\bragopt\b|optimi|experiment|benchmark|evaluation|sweep|candidate|promotion|judge' rag-ttc | head -500
```

```unknown
bash -lc cd /mnt/data/rag-self-improvement && echo '=== coinvault ragopt files ==='; find coinvault -type f | rg 'ragopt|promotion|candidate|experiment|eval' | sort | head -400; echo '=== rag-ttc package tree ==='; find rag-ttc/pkg rag-ttc/cmd/rag-ttc/cmds rag-ttc/internal -maxdepth 4 -type f | sort | sed 's#^rag-ttc/##' | head -500; echo '=== ttmp design docs likely relevant ==='; find coinvault/ttmp rag-ttc/ttmp ragopt/ttmp judgekit/ttmp ragkit/ttmp -type f | rg -i 'ragopt|optimi|judge|experiment|evaluation|self|feedback|candidate|campaign|ledger|evidence|flow|architecture|design' | sort | head -500
```

```unknown
bash -lc cd /mnt/data/rag-self-improvement && echo '=== Coinvault ttmp ragopt/optimization docs ==='; find coinvault/ttmp -type f | rg -i 'ragopt|optim|ground|comparison|retrieval|self|judge|promotion|evidence|ledger|experiment' | sort | head -600; echo '=== Ragopt ttmp docs ==='; find ragopt/ttmp -type f | sort | head -400; echo '=== Judgekit ttmp docs ==='; find judgekit/ttmp -type f | rg -i 'design-doc|reference|README' | sort | head -300
```

```unknown
bash -lc cd /mnt/data/rag-self-improvement && for f in ragopt/README.md judgekit/README.md ragkit/README.md rag-ttc/README.md coinvault/README.md; do echo '================================================================================'; echo "$f"; sed -n '1,260p' "$f"; done
```

```unknown
bash -lc cd /mnt/data/rag-self-improvement/ragopt && for f in pkg/candidate/types.go pkg/candidate/candidate.go pkg/candidate/snapshot.go pkg/eval/types.go pkg/eval/runner.go pkg/eval/cell_chain.go pkg/compare/types.go pkg/compare/build.go pkg/gate/evaluate.go pkg/policy/policy.go pkg/runstore/types.go pkg/runstore/run.go pkg/runstore/write.go pkg/review/review.go pkg/report/types.go pkg/report/render.go; do echo '================================================================================'; echo "$f"; sed -n '1,320p' "$f"; done
```

```unknown
bash -lc cd /mnt/data/rag-self-improvement/ragopt && wc -l pkg/{candidate,eval,compare,gate,policy,runstore,review,report}/*.go | sort -n | tail -30
```

```unknown
bash -lc cd /mnt/data/rag-self-improvement/ragopt && for f in pkg/eval/types.go pkg/compare/types.go pkg/gate/evaluate.go pkg/policy/policy.go pkg/runstore/types.go pkg/review/review.go; do echo '###' $f; sed -n '1,240p' $f; done
```

```unknown
bash -lc cd /mnt/data/rag-self-improvement/coinvault/cmd/coinvault/cmds && wc -l knowledge_ragopt*.go | sort -n
```

```unknown
bash -lc cd /mnt/data/rag-self-improvement/coinvault/cmd/coinvault/cmds && echo '=== declarations in knowledge_ragopt.go ==='; rg -n '^(type|const|var|func) ' knowledge_ragopt.go knowledge_ragopt_case.go knowledge_ragopt_contract.go knowledge_ragopt_gate.go knowledge_ragopt_reranker.go knowledge_ragopt_trace.go knowledge_ragopt_treatment.go knowledge_ragopt_suite_lock.go | sed -n '1,500p'
```

```unknown
bash -lc cd /mnt/data/rag-self-improvement/coinvault/cmd/coinvault/cmds && sed -n '1,380p' knowledge_ragopt.go && sed -n '380,920p' knowledge_ragopt.go
```

```unknown
bash -lc cd /mnt/data/rag-self-improvement/coinvault/cmd/coinvault/cmds && nl -ba knowledge_ragopt.go | sed -n '145,340p'; echo '--- arm/executor ---'; nl -ba knowledge_ragopt.go | sed -n '327,730p'
```

```unknown
bash -lc cd /mnt/data/rag-self-improvement/coinvault/cmd/coinvault/cmds && nl -ba knowledge_ragopt.go | sed -n '340,620p'
```

```unknown
bash -lc cd /mnt/data/rag-self-improvement/coinvault/cmd/coinvault/cmds && nl -ba knowledge_ragopt_treatment.go | sed -n '1,280p'; echo '--- answer contract ---'; nl -ba knowledge_ragopt_contract.go | sed -n '1,350p'; echo '--- trace types/events ---'; nl -ba knowledge_ragopt_trace.go | sed -n '1,430p'
```

```unknown
bash -lc cd /mnt/data/rag-self-improvement/coinvault/cmd/coinvault/cmds && nl -ba knowledge_ragopt_trace.go | sed -n '1,190p'; nl -ba knowledge_ragopt_contract.go | sed -n '1,330p'; nl -ba knowledge_ragopt_treatment.go | sed -n '140,280p'
```

```unknown
bash -lc cd /mnt/data/rag-self-improvement/coinvault/cmd/coinvault/cmds && nl -ba knowledge_ragopt_contract.go | sed -n '1,210p'
```

```unknown
bash -lc cd /mnt/data/rag-self-improvement && for f in \
 ragopt/ttmp/2026/08/06/RAGOPT-001--reusable-reproducible-self-optimization-harness/design-doc/01-ragopt-intern-guide-to-a-reusable-evidence-gated-optimization-harness.md \
 ragopt/ttmp/2026/08/06/RAGOPT-001--reusable-reproducible-self-optimization-harness/reference/02-runstore-v1-on-disk-contract-and-recovery-guarantees.md \
 ragopt/ttmp/2026/08/06/RAGOPT-001--reusable-reproducible-self-optimization-harness/reference/04-paired-evaluation-v1-api-cell-and-resume-contract.md \
 ragopt/ttmp/2026/08/06/RAGOPT-001--reusable-reproducible-self-optimization-harness/reference/05-paired-comparison-gate-and-promotion-report-v1-contract.md; do echo '================================================================================'; echo "$f"; sed -n '1,340p' "$f"; done
```

```unknown
bash -lc cd /mnt/data/rag-self-improvement/rag-ttc && find pkg -maxdepth 3 -type d | sort; find cmd/rag-ttc/cmds -maxdepth 2 -type d | sort; find apps/admin/web/src -maxdepth 3 -type d | sort | head -200
```

```unknown
bash -lc cd /mnt/data/rag-self-improvement/rag-ttc && echo '=== tool eval files ==='; find cmd/rag-ttc/cmds/tooleval pkg/ttc/tooleval pkg/ttc/toolconfig pkg/mixedttc/agenttrace pkg/mixedttc/diagnostic -type f | sort; echo '=== experiments files ==='; find cmd/rag-ttc/cmds/experiments pkg -type f | rg 'experiment|answerquality|chunkcompare|evaluation|judge|review' | sort | head -400; echo '=== declarations ==='; rg -n '^(type|const|var|func) ' cmd/rag-ttc/cmds/tooleval pkg/ttc/tooleval pkg/ttc/toolconfig pkg/mixedttc/agenttrace pkg/mixedttc/diagnostic | sed -n '1,500p'
```

```unknown
bash -lc cd /mnt/data/rag-self-improvement/rag-ttc && nl -ba cmd/rag-ttc/cmds/tooleval/ragopt.go | sed -n '1,540p'
```

```unknown
bash -lc cd /mnt/data/rag-self-improvement/rag-ttc && nl -ba cmd/rag-ttc/cmds/tooleval/ragopt.go | sed -n '140,325p'
```

```unknown
bash -lc cd /mnt/data/rag-self-improvement/rag-ttc && sed -n '1,420p' ttmp/2026/07/30/RAG-TTC-EXP-BROWSER-001--experiment-results-browser-workspace/design-doc/01-design-experiment-results-browser.md; echo '--- queries workspace ---'; sed -n '1,320p' ttmp/2026/07/30/RAG-TTC-QUERIES-WS-001--queries-workspace-evaluation-set-browser-in-the-tui/design-doc/01-design-queries-workspace.md; echo '--- source tree relevant ---'; find apps/admin/web/src/components/pages/Workbench apps/admin/web/src/components/organisms -maxdepth 2 -type f | sort; rg -n 'experiment|evaluation|candidate|run|provenance|funnel|judge|review|query' apps/admin/web/src/components/pages apps/admin/web/src/components/organisms apps/admin/web/src/world apps/admin/web/src/model | head -500
```

The key seam is now clear: OptKit should generalize RagOpt’s immutable experiment/gate spine while preserving product-owned trajectory semantics and FlowKit’s bounded execution responsibilities.

```unknown
bash -lc cd /mnt/data/rag-self-improvement/rag-ttc && echo '=== apps/admin README ==='; sed -n '1,260p' apps/admin/README.md; echo '=== web package ==='; cat apps/admin/web/package.json; echo '=== Workbench ==='; find apps/admin/web/src/components/pages/Workbench -type f -maxdepth 2 -print -exec sed -n '1,260p' {} \;; echo '=== world types ==='; sed -n '1,420p' apps/admin/web/src/world/world.tsx; echo '=== provenance page ==='; find apps/admin/web/src/components/pages/ProvenanceWalk -type f -maxdepth 2 -print -exec sed -n '1,300p' {} \;
```

```unknown
bash -lc cd /mnt/data/rag-self-improvement/coinvault && find internal/webchat/evalchat -type f -maxdepth 2 -print | sort; rg -n '^(type|const|var|func) ' internal/webchat/evalchat | sed -n '1,400p'; find internal/webchat -maxdepth 2 -type f | rg 'session|event|observ|turn|projection|runtime' | sort | head -300
```

```unknown
bash -lc cd /mnt/data/rag-self-improvement/coinvault && sed -n '1,340p' internal/webchat/localwebchat/local_events.go; sed -n '1,340p' internal/webchat/evalchat/canonical_driver.go; sed -n '1,320p' internal/webchat/observability.go
```

```unknown
bash -lc cd /mnt/data/rag-self-improvement && for f in coinvault/go.mod rag-ttc/go.mod ragkit/go.mod ragopt/go.mod judgekit/go.mod; do echo '###' $f; rg -n 'module|flowkit|ragkit|ragopt|judgekit|sessionstream|river|opentelemetry|sqlite|bubble|cobra|glazed|geppetto|pinocchio' $f; done
```

```unknown
bash -lc cd /mnt/data/rag-self-improvement/judgekit && sed -n '1,520p' ttmp/2026/08/17/JUDGEKIT-001--design-and-implement-judgekit/design-doc/01-judgekit-architecture-and-implementation-guide.md; echo '=== core types ==='; for f in spec/construct.go spec/contract.go protocol/protocol.go eval/instance.go eval/evidence.go assessment/report.go assessment/dimension.go judging/interfaces.go suite/suite.go calibration/report.go audit/reliability.go; do echo '---' $f; sed -n '1,320p' $f; done
```

<details><summary>💭 Thinking</summary>

**Inspected RAG optimization, evaluation, UI, and package architectures**

</details>

```json
{"search_query":[{"q":"GEPA reflective prompt evolution paper arXiv 2025 compound AI systems trajectories Pareto"},{"q":"MIPROv2 DSPy paper arXiv multi-stage language model programs optimization"},{"q":"TextGrad automatic differentiation via text paper arXiv 2024"},{"q":"LLM as a Judge MT-Bench paper arXiv position bias verbosity bias"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 10 websites**

</details>

```unknown
bash -lc set -euo pipefail
cd /mnt/data/rag-self-improvement
printf '\n== Coinvault candidate dirs ==\n'
find coinvault/configs/ragopt -mindepth 1 -maxdepth 1 -type d -printf '%f\n' | sort | sed -n '1,120p'
printf '\n== rag-ttc ragopt assets ==\n'
find rag-ttc -path '*ragopt*' -maxdepth 8 -type f | sed -n '1,200p'
printf '\n== likely GEPA docs ==\n'
find rag-ttc coinvault ragopt -type f \( -iname '*gepa*' -o -iname '*optimization*' -o -iname '*self*improv*' \) | sed -n '1,240p'

```

```unknown
bash -lc set -euo pipefail
cd /mnt/data/rag-self-improvement
printf '\n== Coinvault grounded-answer-v2 files ==\n'
find coinvault/configs/ragopt/grounded-answer-v2 -maxdepth 4 -type f -print | sort
printf '\n== candidate.yaml ==\n'
sed -n '1,240p' coinvault/configs/ragopt/grounded-answer-v2/candidate.yaml
printf '\n== parent snapshot ==\n'
sed -n '1,240p' coinvault/configs/ragopt/grounded-answer-v2/parent/snapshot.yaml
printf '\n== candidate snapshot ==\n'
sed -n '1,240p' coinvault/configs/ragopt/grounded-answer-v2/candidate/snapshot.yaml
printf '\n== gate policy ==\n'
sed -n '1,280p' coinvault/configs/ragopt/grounded-answer-v2/shared/gate-policy.yaml
printf '\n== TTC candidate ==\n'
sed -n '1,240p' rag-ttc/assets/configs/ragopt/i5-combined-comparison-v1/candidate.yaml
printf '\n== TTC gate ==\n'
sed -n '1,260p' rag-ttc/assets/configs/ragopt/i5-combined-comparison-v1/shared/gate-policy.yaml

```

<details><summary>💭 Thinking</summary>

**Inspected RAG optimization documentation and configurations**

</details>

```unknown
bash -lc set -euo pipefail
cd /mnt/data/rag-self-improvement
for f in \
 coinvault/ttmp/2026/08/17/COINVAULT-045--study-self-optimization-and-exploitable-evaluator-errors/design-doc/09-structured-evaluation-and-optimization-refactor-for-coinvault.md \
 rag-ttc/ttmp/2026/08/02/RAG-TTC-GEPA-OPT-001--pragmatic-self-optimization-loop-for-ttc-rag-prompts-and-tools/design-doc/01-intern-guide-to-a-pragmatic-gepa-inspired-self-optimization-loop.md \
 ragopt/ttmp/2026/08/06/RAGOPT-001--reusable-reproducible-self-optimization-harness/design-doc/01-ragopt-intern-guide-to-a-reusable-evidence-gated-optimization-harness.md \
 rag-ttc/ttmp/2026/07/30/RAG-TTC-EXP-BROWSER-001--experiment-results-browser-workspace/design-doc/01-design-experiment-results-browser.md; do
  printf '\n\n===== %s =====\n' "$f"
  printf '%s\n' '-- headings --'
  grep -n '^#' "$f" | sed -n '1,180p'
  printf '%s\n' '-- opening --'
  sed -n '1,220p' "$f"
done

```

```unknown
bash -lc set -euo pipefail
cd /mnt/data/rag-self-improvement
f='coinvault/ttmp/2026/08/17/COINVAULT-045--study-self-optimization-and-exploitable-evaluator-errors/design-doc/09-structured-evaluation-and-optimization-refactor-for-coinvault.md'
for r in '109,230' '522,686' '686,820' '821,970'; do
  printf '\n===== lines %s =====\n' "$r"
  sed -n "${r}p" "$f"
done
printf '\n===== GEPA guide headings/opening =====\n'
g='rag-ttc/ttmp/2026/08/02/RAG-TTC-GEPA-OPT-001--pragmatic-self-optimization-loop-for-ttc-rag-prompts-and-tools/design-doc/01-intern-guide-to-a-pragmatic-gepa-inspired-self-optimization-loop.md'
grep -n '^#' "$g" | sed -n '1,220p'
sed -n '1,320p' "$g"

```

```unknown
bash -lc set -euo pipefail
cd /mnt/data/rag-self-improvement
printf '== rag-ttc admin workbench files ==\n'
find rag-ttc/apps/admin/web/src -type f | grep -Ei '(workbench|world|verb|tile|provenance|selection|funnel|evidence|hits)' | sed -n '1,240p'
printf '\n== package roots ==\n'
find rag-ttc/apps/admin/web/src -maxdepth 3 -type d | sed -n '1,180p'
printf '\n== relevant symbols ==\n'
rg -n "WorldProvider|verbSink|dispatchVerb|TileRegistry|ProvenanceWalk|selection" rag-ttc/apps/admin/web/src | sed -n '1,260p'

```

```unknown
bash -lc set -euo pipefail
cd /mnt/data/rag-self-improvement
printf '\n== world.tsx ==\n'
sed -n '1,290p' rag-ttc/apps/admin/web/src/world/world.tsx
printf '\n== registry.ts ==\n'
sed -n '1,260p' rag-ttc/apps/admin/web/src/appkit/registry.ts
printf '\n== Workbench.tsx ==\n'
sed -n '1,300p' rag-ttc/apps/admin/web/src/components/pages/Workbench/Workbench.tsx
printf '\n== ProvenanceWalk.tsx ==\n'
sed -n '1,230p' rag-ttc/apps/admin/web/src/components/pages/ProvenanceWalk/ProvenanceWalk.tsx

```

<details><summary>💭 Thinking</summary>

**Inspected optimization documents and Workbench files**

</details>

```json
{"search_query":[{"q":"site:arxiv.org/abs/2406.11695 MIPROv2 multi-stage language model programs"},{"q":"site:arxiv.org/abs/2309.03409 Optimization by PROmpting OPRO"},{"q":"site:arxiv.org/abs/2210.10760 Scaling Laws for Reward Model Overoptimization"},{"q":"site:opentelemetry.io docs traces spans events specification"}],"response_length":"long"}
```

```json
{"search_query":[{"q":"arXiv 2406.11695 MIPROv2 optimizer"},{"q":"arXiv 2507.19457 GEPA reflective prompt evolution"},{"q":"arXiv 2406.07496 TextGrad automatic differentiation via text"},{"q":"arXiv 2306.05685 Judging LLM-as-a-Judge MT-Bench Chatbot Arena"}],"response_length":"long"}
```

```json
{"open":[{"ref_id":"https://arxiv.org/abs/2406.11695"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 2 websites**

</details>

```unknown
bash -lc set -euo pipefail
cd /mnt/data/rag-self-improvement
printf '\n== ragopt package files ==\n'
find ragopt/pkg -maxdepth 2 -type f | sort
printf '\n== candidate types ==\n'
sed -n '1,320p' ragopt/pkg/candidate/types.go 2>/dev/null || true
printf '\n== eval types ==\n'
sed -n '1,360p' ragopt/pkg/eval/types.go
printf '\n== gate types/evaluate ==\n'
for f in ragopt/pkg/gate/*.go ragopt/pkg/policy/*.go; do echo "--- $f"; sed -n '1,300p' "$f"; done

```

<details><summary>💭 Thinking</summary>

**Planning evidence**

I’m outlining a study guide grounded in the attached repository, with a dedicated evidence appendix listing relevant file paths. I’ll also include paper references by title and identifier rather than embedding raw links.

**Planned evidence**

</details>

```unknown
bash -lc set -euo pipefail
cd /mnt/data/rag-self-improvement
for m in ragopt judgekit ragkit rag-ttc coinvault; do
  echo "===== $m/go.mod ====="
  sed -n '1,90p' "$m/go.mod"
done
printf '\n== judgekit tree ==\n'
find judgekit -maxdepth 3 -type f | sort | sed -n '1,260p'
printf '\n== key judgekit docs/types ==\n'
for f in judgekit/README.md judgekit/spec/*.go judgekit/protocol/*.go judgekit/assessment/*.go judgekit/suite/*.go; do
  [ -f "$f" ] || continue
  echo "--- $f"
  sed -n '1,260p' "$f"
done

```

```unknown
bash -lc set -euo pipefail
cd /mnt/data/rag-self-improvement
printf '\n== judgekit README ==\n'
sed -n '1,320p' judgekit/README.md
printf '\n== judgekit package doc files ==\n'
find judgekit -maxdepth 2 -name 'doc.go' -print -exec sh -c 'echo --- "$1"; sed -n "1,240p" "$1"' sh {} \;
printf '\n== judgekit top-level type declarations ==\n'
rg -n '^type [A-Za-z].* struct|^type [A-Za-z].* interface|^type [A-Za-z].* ' judgekit/{spec,eval,protocol,assessment,judging,audit,calibration,suite} | sed -n '1,320p'

```

```unknown
bash -lc set -euo pipefail
cd /mnt/data/rag-self-improvement
printf '\n== coinvault ragopt code headings/functions ==\n'
for f in coinvault/cmd/coinvault/cmds/knowledge_ragopt*.go; do
 echo "--- $f"
 rg -n '^type |^const |^func ' "$f" | sed -n '1,260p'
done
printf '\n== ttc ragopt code functions ==\n'
rg -n '^type |^const |^func ' rag-ttc/cmd/rag-ttc/cmds/tooleval/ragopt.go | sed -n '1,320p'

```

```unknown
bash -lc set -euo pipefail
cd /mnt/data/rag-self-improvement
printf '\n== coinvault command orchestration ==\n'
sed -n '151,460p' coinvault/cmd/coinvault/cmds/knowledge_ragopt.go
printf '\n== coinvault executor core ==\n'
sed -n '440,870p' coinvault/cmd/coinvault/cmds/knowledge_ragopt.go
printf '\n== coinvault treatment contract ==\n'
sed -n '1,285p' coinvault/cmd/coinvault/cmds/knowledge_ragopt_treatment.go
printf '\n== TTC executor/materializer ==\n'
sed -n '85,470p' rag-ttc/cmd/rag-ttc/cmds/tooleval/ragopt.go

```

```unknown
bash -lc set -euo pipefail
cd /mnt/data/rag-self-improvement
printf '== grounded-answer-v2 result references ==\n'
rg -n "0\.5405|0\.583|grounded-answer-v2|five.*fail|route failures" coinvault/ttmp/2026/08/09 coinvault/ttmp/2026/08/17 | sed -n '1,260p'
printf '\n== current ragopt run examples/directories ==\n'
find coinvault rag-ttc -type d \( -name 'ragopt-runs' -o -name 'runs' -o -name 'experiments' \) | sed -n '1,120p'

```

<details><summary>💭 Thinking</summary>

**Drafting study guide**

I’m shaping the guide around the repository’s current systems, then building toward mathematical vocabulary, architecture, APIs, runtime integration, trajectories, measurements, trials, comparisons, and search plugins.

**Drafted study guide**

</details>

One added constraint is crucial: trials must generalize beyond Coinvault’s paired comparisons to rag-ttc’s multi-arm experiments. Coinvault mutations become registered variables with domains, materializers, identities, and manipulation checks.

<details><summary>💭 Thinking</summary>

**Inspected RAG optimization, JudgeKit, Executor, and grounding architectures**

</details>

```unknown
bash -lc cat > /mnt/data/optkit-architecture-and-migration-guide.md <<'EOF'
---
title: "OptKit: A Composable Optimization Control Plane for Coinvault and RAG-TTC"
status: "Proposed design"
date: "2026-08-20"
audience:
  - interns implementing the first version
  - maintainers of Coinvault, rag-ttc, ragopt, judgekit, ragkit, and flowkit
  - reviewers responsible for evaluation validity and promotion safety
scope:
  - architecture and mathematical model
  - package and API design
  - Coinvault migration
  - rag-ttc migration
  - visualization and control-plane design
  - implementation roadmap and acceptance tests
out_of_scope:
  - production code implementation
  - automatic production deployment
  - optimization of model weights
  - final visual design or CSS
---

# OptKit: A Composable Optimization Control Plane for Coinvault and RAG-TTC

## Executive summary

Coinvault and `rag-ttc` already contain most of the ingredients of a serious optimization system. They can freeze system configurations, execute real product paths, capture rich traces, judge outputs, compare alternatives, enforce hard gates, preserve artifacts, and support human review. The difficulty is not that these capabilities are absent. The difficulty is that the **optimization process itself is not yet a first-class, reusable object**.

Today, the process is distributed across several places:

- `ragopt` owns immutable candidate bundles, exactly-one-mutation validation, paired incumbent/challenger evaluation, comparisons, gates, promotion reports, blinded review, and durable run directories.
- Coinvault owns the production-equivalent chat execution path, product cases, treatment application, intervention checks, answer contracts, runtime traces, authorization-sensitive behavior, and domain-specific judge inputs.
- `rag-ttc` owns several kinds of experiments, a tool-loop evaluator, native session traces, retrieval experiments, and a strong workbench UI architecture based on a shared selection, serializable verbs, and composable tiles.
- JudgeKit owns explicit measurement constructs, contracts, protocols, evidence, assessments, calibration, reliability probes, and evaluator suites.
- FlowKit owns bounded execution, retries, caching, resource admission, metering, reports, and ledgers.
- RagKit owns RAG-domain mechanics such as documents, chunks, retrieval, evidence, reranking, index bundles, and direct grounded-answer contracts.

The proposed `optkit` module should not replace those packages. It should provide the missing layer that makes this cycle explicit and persistent:

```text
history
   ↓
proposal
   ↓
patch to a system snapshot
   ↓
materialized executable candidate
   ↓
trials and full product trajectories
   ↓
measurements and constraints
   ↓
comparisons and archive updates
   ↓
selection or promotion decision
   ↓
new history
```

Mathematically, OptKit treats an application as a parameterized stochastic executable system

\[
S_\theta : X \rightsquigarrow \mathcal T,
\]

where \(\theta\) is a heterogeneous configuration, \(X\) is a case or task input, and \(\mathcal T\) is the space of possible trajectories. A trajectory may include model turns, retrieval, SQL, tools, retries, citations, widgets, errors, costs, and the final output. An evaluation suite maps a trajectory to a vector of typed measurements and constraint results. An optimizer proposes new patches from campaign history. A selector decides what may advance. These are separate roles.

The central architectural recommendation is:

```text
                       Product repositories
                Coinvault              rag-ttc
        variables, materializers,  variables, materializers,
        executors, constraints,     executors, constraints,
        trajectory adapters         trajectory adapters
                     \                 /
                      \               /
                       v             v
                  +-----------------------+
                  |        optkit         |
                  |-----------------------|
                  | campaign + plan       |
                  | snapshot + patch      |
                  | trial + episode       |
                  | trajectory + artifact |
                  | measure + compare     |
                  | select + archive      |
                  | optimizer plugins     |
                  | journal + projections |
                  +----+-------------+----+
                       |             |
                 +-----v----+   +----v------+
                 | FlowKit  |   | JudgeKit  |
                 | execute  |   | measure   |
                 +----------+   +-----------+
                       |
                 +-----v----+
                 | RagKit   |
                 | RAG domain|
                 +----------+
```

The design has four consequences.

First, `ragopt` should become a compatibility layer and RAG-oriented preset package rather than the universal optimization core. Its strongest current semantics should be moved or generalized into OptKit, while old candidate bundles and run directories remain importable.

Second, the core must be **event-sourced**. One append-only campaign journal should drive the pre-run plan view, the live view, and the historical result view. Heavy native traces remain immutable artifacts referenced by journal events. Rebuildable projections serve UIs and queries.

Third, a score is not a reward oracle. Measurements retain construct identity, measurement-contract identity, evaluator protocol, applicability, uncertainty, evidence references, and diagnostics. Changing a judge prompt or parser creates a new measurement epoch. Promotion uses constrained, evidence-aware decision policies rather than a single weighted score.

Fourth, product meaning remains in the product. OptKit can know that a patch changes variable `answer.grounding_prompt`; Coinvault alone knows how to apply that prompt to its canonical runtime and how to verify that the prompt actually affected the run. OptKit can know that `search.description` changed; `rag-ttc` alone knows how to materialize a safe `tool-qa.yaml` and execute its tool loop.

The recommended migration is incremental. The first useful release does not need GEPA or any autonomous optimizer. It needs a precise model, a journal, a trial runner, typed measurements, compatibility importers, and UI projections. Once manual and coordinate-search campaigns work end to end, reflective search, Pareto evolution, MIPRO-like search, bandits, and other optimizers can be added as plugins without changing the campaign substrate.

---

## How to read this document

This is both a design specification and a teaching document. It intentionally introduces every major term in the same order:

1. **Motivation:** what problem requires the concept;
2. **Definition:** the precise meaning used by OptKit;
3. **Representation:** the proposed data type or interface;
4. **Worked example:** how the concept appears in Coinvault or `rag-ttc`;
5. **Failure mode:** what goes wrong when the concept is omitted or conflated.

The document is organized into seven parts:

- **Part I** reconstructs the current systems and identifies what should be preserved.
- **Part II** builds the mathematical vocabulary from concrete execution traces upward.
- **Part III** specifies the OptKit packages, APIs, persistence model, and laws.
- **Part IV** designs the plan, live, and historical user interfaces.
- **Part V** gives the Coinvault migration in file-level detail.
- **Part VI** gives the `rag-ttc` migration, including non-paired experiment families.
- **Part VII** is the implementation handbook: tools, milestones, tests, risks, and review checklists.

Code in this document is deliberately pseudocode-like Go. It is intended to make boundaries and invariants precise, not to lock every field name before implementation.

> **Callout — What this document does not propose**
>
> OptKit is not a new model provider SDK, not a replacement for FlowKit, not a generic DAG scheduler, not a RAG library, not a judge library, and not an automatic deployment service. Its job is to represent and control optimization campaigns over executable systems.

---

# Part I — Begin with the systems that already work

## 1. The current optimization stack

### 1.1 Why start from the existing systems?

A framework designed only from research terminology will usually miss the inconvenient details that make production experiments trustworthy: exact source revisions, provider budgets, hidden-set handling, canonical execution paths, cancellation behavior, native artifacts, treatment checks, and resumption after a crash. Coinvault and `rag-ttc` already encode those lessons.

The correct strategy is therefore **semantic extraction**, not replacement:

```text
working product behavior
        ↓ identify repeated concepts
explicit reusable abstractions
        ↓ retain product adapters
same behavior, better composition
```

### 1.2 Current responsibility map

| Existing component | Current responsibility | Keep, move, or generalize? |
|---|---|---|
| FlowKit `execution` | bounded ordered work, caches, budgets, rate admission | Keep unchanged below OptKit |
| FlowKit `flow` | typed steps, retries, failure policy, batching, metering, reports, ledgers | Keep unchanged below OptKit |
| JudgeKit | constructs, measurement contracts, protocols, assessments, calibration, reliability | Keep independent; add an OptKit adapter |
| RagKit | RAG data types, retrieval, reranking, evidence, index bundles, direct contracts | Keep domain-specific and optimization-unaware |
| RagOpt `candidate` | immutable snapshots and one-mutation candidates | Generalize into OptKit snapshot/patch/candidate |
| RagOpt `eval` | paired cells and run custody | Generalize into trial/episode runtime; retain compatibility |
| RagOpt `compare` | exact paired deltas and aggregates | Move/generalize into OptKit comparison strategies |
| RagOpt `gate`/`policy` | lexicographic hard/target/regression/cost decisions | Move/generalize into OptKit selection policies |
| RagOpt `runstore` | durable immutable experiment artifacts and recovery | Reuse ideas; import old runs; put campaign journal above it |
| Coinvault | canonical product execution, cases, treatments, contracts, traces | Keep product-owned; expose adapters and registries |
| `rag-ttc` | tool-loop execution, multiple experiment families, provenance UI | Keep product-owned; expose adapters; reuse workbench shell |

### 1.3 The existing RagOpt loop

The current reusable loop is approximately:

```text
candidate.yaml + parent snapshot + child snapshot
                       ↓ strict validation
frozen suite + frozen gate policy + two product arms
                       ↓
       run every case × repeat × arm
                       ↓
      one immutable cell per matrix point
                       ↓
        exact incumbent/challenger pairing
                       ↓
 identity → hard → target → regression → cost gate
                       ↓
 promotion evidence and human review artifacts
```

This is a strong experimental harness. Its deliberate limitation is that it represents one paired candidate trial, not an adaptive campaign spanning many candidates and trial designs.

### 1.4 The existing Coinvault cell

One Coinvault cell is a complete production-equivalent agent execution:

```text
case input
   ↓
canonical HTTP / WebSocket / Sessionstream chat path
   ↓
model call
   ↓
knowledge search and/or SQL tools
   ↓
retrieval, authorization, reranking, evidence admission
   ↓
possibly more model and tool turns
   ↓
final answer and citations
   ↓
trace projection
   ↓
treatment-exercise check
   ↓
deterministic answer contract
   ↓ if valid
LLM judge
   ↓
RagOpt outcome + native artifact
```

The current treatment implementation supports concrete variables such as result depth, comparison plans, comparison intent, answer prompt suffixes, rerankers, and tool descriptions. It also verifies that a candidate's intended intervention actually occurred. A changed default result count, for example, is not considered exercised when the model explicitly supplies another limit.

### 1.5 The existing `rag-ttc` cell

A current `rag-ttc` RagOpt cell:

```text
case input
   ↓
materialize candidate assets into tool-qa.yaml and supporting files
   ↓
run chatpkg.NewRuntime against the frozen index bundle
   ↓
project native session TurnRecord into a product outcome
   ↓
run answerquality.JudgeToolLoop
   ↓
write native artifact
   ↓
project faithfulness, relevance, and product execution cost
```

Unlike Coinvault, `rag-ttc` also has other experiment families: chunker comparisons, representation experiments, index evaluations, ANN bakeoffs, retrieval diagnostics, and human review. These are not all naturally incumbent/challenger trials.

> **Worked example — Why the core cannot assume two arms**
>
> A Coinvault grounding-prompt candidate naturally compares `incumbent` against `challenger`. A chunking study may compare `markdown`, `markdown+summary`, and `markdown-heading` across the same queries. An ANN bakeoff may compare several indexes against an exact-search oracle. OptKit therefore needs a general `TrialDesign`, with paired two-arm comparison as one strategy.

---

## 2. The exact reusable seam

### 2.1 What is common?

Both product systems do the following:

1. identify a complete system configuration;
2. define what may and may not change;
3. materialize a configuration into something executable;
4. schedule cases and repetitions;
5. execute a real product runtime;
6. preserve a native trajectory and artifacts;
7. check whether the intervention took effect;
8. enforce deterministic product constraints;
9. produce typed or semi-typed measurements;
10. compare alternatives;
11. decide whether a candidate advances;
12. retain all rejected and successful evidence.

These are the semantics OptKit should own.

### 2.2 What is not common?

The following remain product-specific:

- what a Coinvault `knowledge_search` event means;
- how authorization is enforced;
- how a grounding prompt is attached to the answer runtime;
- how a TTC `tool-qa.yaml` is constructed safely;
- what counts as required evidence for a particular product case;
- how an index bundle is loaded;
- which native trace is authoritative;
- which variables are allowed in a particular campaign;
- how product deployment is performed.

A framework becomes brittle when it tries to encode those details centrally.

### 2.3 The core design rule

> **Definition — Product-owned semantics**
>
> Product-owned semantics are rules whose correctness depends on domain or runtime knowledge that the generic framework cannot validate independently. OptKit stores their identities, invokes their interfaces, and records their outputs. It does not reimplement them.

Applied to Coinvault:

```text
OptKit knows:  patch sets answer.grounding_prompt to digest X
Coinvault knows: where that prompt enters the production runtime
Coinvault proves: observed runtime suffix digest was X
```

Applied to `rag-ttc`:

```text
OptKit knows: patch sets search.description to artifact digest Y
rag-ttc knows: how to materialize a safe tool configuration
rag-ttc proves: executed runtime config digest included Y
```

---

## 3. Why not simply keep extending RagOpt?

RagOpt's name and current API describe a narrower object: a reusable, reproducible, evidence-gated RAG candidate evaluation. It has excellent invariants, but several assumptions are now too specific for the desired framework:

- the central run is paired incumbent/challenger;
- the candidate must change exactly one byte-level mutable asset;
- an outcome exposes an untyped `map[string]float64`;
- a run is terminal evidence rather than one step in a persistent adaptive campaign;
- candidate lineage beyond parent/child is implicit in directories and human diaries;
- evaluator protocol epochs are not first-class at the comparison boundary;
- planning and live campaign state are not represented;
- the optimizer that proposes a new candidate is outside the system.

The recommendation is not to discard RagOpt. It is to use it as the first concrete semantics from which OptKit is generalized.

A practical end state is:

```text
ragopt/
  compat/          import old candidate bundles and run directories
  presets/         RAG-oriented plans, variables, metrics, and gates
  paired/          convenience constructors for incumbent/challenger trials
  cmd/ragopt/      compatibility CLI delegating to OptKit
```

The reusable campaign machinery moves to `optkit`. Existing callers can migrate incrementally through adapters.

---

# Part II — Mathematical vocabulary, built from a Coinvault run

## 4. A system is a parameterized stochastic program

### 4.1 Motivation

Calling Coinvault “a prompt” loses nearly everything that matters. A result depends on prompts, model profiles, tools, retrieval settings, index contents, rerankers, authorization, evidence policies, tool outputs, runtime randomness, and possibly several model turns.

We need a term broad enough to include the whole executable object.

### 4.2 Definition

> **Definition — Parameterized system**
>
> A parameterized system is an executable program \(S_\theta\) whose behavior depends on a configuration \(\theta\). Given an input \(x\), execution produces a trajectory \(\tau\), possibly stochastically:
>
> \[
> \tau \sim S_\theta(x).
> \]

The squiggly arrow notation

\[
S_\theta : X \rightsquigarrow \mathcal T
\]

means that one input may induce a distribution over trajectories rather than one deterministic output.

### 4.3 Coinvault example

A simplified Coinvault configuration might be

\[
\theta = (
 p_{route},
 p_{ground},
 d_{default},
 d_{forced},
 q_{comparison},
 \rho_{rerank},
 d_{tool},
 m_{answer}
).
\]

These coordinates are heterogeneous:

- \(p_{route}\) and \(p_{ground}\) are text;
- \(d_{default}\) and \(d_{forced}\) are integers;
- \(q_{comparison}\) is a structured plan;
- \(\rho_{rerank}\) is a reranker configuration;
- \(d_{tool}\) is a tool-description artifact;
- \(m_{answer}\) is a model/profile identity.

### 4.4 `rag-ttc` example

A TTC configuration might contain:

\[
\theta_{ttc} = (
 p_{orchestration},
 s_{answer},
 d_{search},
 c_{chunker},
 r_{representation},
 f_{fusion},
 k_{retrieve},
 i_{index}
).
\]

Not every campaign should expose every coordinate. Safety limits and authorization rules may be fixed dimensions rather than optimizable variables.

> **Pitfall — Treating a runtime flag as the whole system identity**
>
> `default_results=8` is not a reproducible candidate by itself. The candidate also depends on corpus and index digests, model and judge identities, tool-loop version, locked prompts, source roles, and all other semantically relevant dimensions.

---

## 5. Search spaces, variables, snapshots, patches, and candidates

These terms are related but not interchangeable. This section distinguishes them carefully.

### 5.1 Search space

#### Motivation

An optimizer needs to know what it is allowed to propose. A free-form map permits invalid combinations, silently changes protected settings, and gives UIs no way to explain the available choices.

#### Definition

> **Definition — Search space**
>
> A search space \(\Theta\) is the set of valid configurations that a campaign may consider. For heterogeneous systems it is usually a constrained product:
>
> \[
> \Theta \subseteq \Theta_1 \times \Theta_2 \times \cdots \times \Theta_k.
> \]

The subset symbol matters. Not every combination of individually valid values is jointly valid.

#### Example

A campaign may expose:

```text
answer.grounding_prompt  ∈ approved text artifacts
knowledge.default_results ∈ {5, 8, 10, 12}
knowledge.reranker       ∈ {none, qwen3-pool12}
```

while enforcing:

```text
if reranker = qwen3-pool12, retrieval pool must be at least 12
answer model and authorization policy are fixed
```

### 5.2 Variable

#### Motivation

A treatment mechanism currently combines several jobs: identifying a mutable concept, validating its value, applying it to a runtime, and checking whether it was exercised. These should be explicit and composable.

#### Definition

> **Definition — Variable**
>
> A variable is a named coordinate of a search space, together with a domain, validation rules, display metadata, and product-owned materialization semantics.

A variable is not merely a string key. It should answer:

- What values are legal?
- How is a value serialized and digested?
- Can it be optimized in this campaign?
- How is it displayed and diffed?
- What other variables constrain it?
- How does the product apply it?
- How can the product verify the intervention?

#### Proposed API

```go
type VariableDefinition interface {
    ID() VariableID
    Domain() Domain
    Validate(value Value) error
    Describe(value Value) DisplayValue
}

type VariableMaterializer interface {
    Apply(
        ctx context.Context,
        base SnapshotView,
        value Value,
        workspace Workspace,
    ) (AppliedVariable, error)
}

type InterventionChecker interface {
    Check(
        ctx context.Context,
        expected AppliedVariable,
        trajectory trajectory.View,
    ) (InterventionAssessment, error)
}
```

The interfaces are split deliberately. A search-space linter can use `VariableDefinition` without importing a product runtime. Materialization and intervention checking remain product adapters.

#### Coinvault worked example: default result count

```go
type DefaultResultsVariable struct{}

func (DefaultResultsVariable) ID() VariableID {
    return "knowledge.default_results"
}

func (DefaultResultsVariable) Domain() Domain {
    return IntegerDomain{Min: 1, Max: 20, Allowed: []int{5, 8, 10, 12}}
}

func (DefaultResultsVariable) Apply(..., value Value, ...) (AppliedVariable, error) {
    // Configure the product-owned knowledge tool default.
}

func (DefaultResultsVariable) Check(..., tr trajectory.View) (InterventionAssessment, error) {
    // Verify configured default, requested limit, effective limit, and source.
    // A model-specified limit can make this intervention unexercised.
}
```

### 5.3 Snapshot

#### Motivation

A candidate must be reproducible as a whole, not only as a changed variable.

#### Definition

> **Definition — Snapshot**
>
> A snapshot is an immutable, content-addressed semantic description of one complete system configuration. It includes variable values, locked dimensions, artifact references, and the identities of external resources required to reproduce the system.

A snapshot is a point \(\theta\in\Theta\), plus enough identity to prove which point it is.

#### Proposed representation

```go
type Snapshot struct {
    APIVersion string
    ID         SnapshotID       // semantic digest
    SystemID   SystemID

    Variables  map[VariableID]ValueRef
    Dimensions map[DimensionID]DimensionValue
    Artifacts  []ArtifactRef

    ParentHint *SnapshotID       // convenience, not part of semantic identity
    Metadata   map[string]string // non-semantic display metadata
}
```

Semantic and display fields must be separated. A title or timestamp should not invalidate a cache; a prompt digest or corpus digest should.

#### Coinvault example

The existing `grounded-answer-v2` parent and challenger snapshots correctly lock comparison plans, suites, gate policy, runtime contract, source lock, treatment contract, validation suite, model identities, bundle ID, corpus digest, indexes, source roles, and tool-loop version. Only the `answer_grounding_prompt` asset changes.

### 5.4 Patch

#### Motivation

RagOpt currently represents a candidate primarily as two complete snapshots and verifies the single changed asset. A general optimizer needs a first-class change object so it can propose, validate, combine, display, and reason about changes before fully materializing a child snapshot.

#### Definition

> **Definition — Patch**
>
> A patch \(\delta\) is an immutable, typed transformation request from one snapshot to another:
>
> \[
> \theta' = \theta \oplus \delta.
> \]

Its support is the set of variables it changes:

\[
\operatorname{supp}(\delta)
= \{j : \theta'_j \neq \theta_j\}.
\]

Current RagOpt candidates impose

\[
|\operatorname{supp}(\delta)| = 1.
\]

OptKit should make that a policy, not a universal law.

#### Proposed representation

```go
type Patch struct {
    APIVersion string
    ID         PatchID
    Base       SnapshotID
    Operations []Operation
    Rationale  Rationale
    Proposer   ProposerIdentity
}

type Operation struct {
    Variable VariableID
    Kind     OperationKind // set, unset, replace-artifact, structured-edit
    Value    ValueRef
}
```

#### Worked examples

One-coordinate Coinvault patch:

```yaml
base: sha256:f666...
operations:
  - variable: answer.grounding_prompt
    kind: set
    value:
      artifact: sha256:ee276...
```

Two-coordinate reflective patch, legal only in a campaign that allows it:

```yaml
operations:
  - variable: answer.grounding_prompt
    kind: set
    value: {artifact: sha256:...}
  - variable: knowledge.tool_description
    kind: set
    value: {artifact: sha256:...}
```

### 5.5 Candidate

#### Motivation

A patch says what to change. An optimization candidate also needs a hypothesis, provenance, predicted benefits, risks, lineage, and materialization status.

#### Definition

> **Definition — Candidate**
>
> A candidate is a proposed child system together with the patch that creates it, its causal hypothesis, provenance, expected objectives, regression risks, and lineage.

#### Proposed representation

```go
type Candidate struct {
    APIVersion string
    ID         CandidateID
    Parent     SnapshotID
    Patch      PatchID
    Child      *SnapshotID

    Hypothesis          string
    ExpectedImprovement []ObjectiveExpectation
    RegressionRisks     []Risk
    EvidenceRefs        []ArtifactRef
    Proposer            ProposerIdentity
    CreatedByEvent      EventID

    Status CandidateStatus // proposed, valid, materialized, evaluating, rejected, archived, promoted
}
```

> **Worked example — `grounded-answer-v2`**
>
> The current Coinvault manifest is already an excellent candidate record. It states that direct clause-level entailment and adjacent citations should improve faithfulness on comparison cases, while identifying terseness, omitted synthesis, and citation density as risks. OptKit should preserve that information and add explicit lineage and campaign identity.

---

## 6. Cases, datasets, roles, and exposure

### 6.1 Motivation

An optimizer can overfit not only to examples but also to evaluator feedback about those examples. Reflective methods make this especially important because a rich natural-language critique can leak far more information than a scalar score.

### 6.2 Case and dataset

> **Definition — Case**
>
> A case is one stable evaluation input with a product-owned payload, group labels, and provenance.

> **Definition — Dataset**
>
> A dataset is an immutable ordered collection of cases with a semantic digest.

```go
type Case struct {
    ID       CaseID
    Groups   []GroupID
    Input    ArtifactRef
    Metadata map[string]string
}

type Dataset struct {
    ID       DatasetID
    Role     DataRole
    Cases    []CaseRef
    Digest   Digest
    Policy   ExposurePolicy
}
```

### 6.3 Data roles

OptKit should make the intended use of data explicit:

| Role | Purpose | Optimizer visibility |
|---|---|---|
| `diagnostic` | discover and localize failure modes | full trajectories and feedback allowed |
| `development` | guide proposals and search | scores and configured feedback allowed |
| `calibration` | estimate evaluator quality against human/objective labels | usually evaluator developers, not candidate proposer |
| `selection` | compare finalists with limited adaptivity | aggregate or restricted feedback |
| `promotion` | final held-out evidence | no optimizer access before final selection |
| `shadow` | monitor production-like behavior | governed by online data policy |

### 6.4 Exposure

> **Definition — Exposure**
>
> An exposure is a recorded fact that an actor or optimizer received information derived from a protected dataset or case.

```go
type Exposure struct {
    Actor       ActorID
    Dataset     DatasetID
    CaseIDs     []CaseID
    Kind        ExposureKind // input, score, critique, trajectory, aggregate
    EventID     EventID
    OccurredAt  time.Time
    ArtifactRef *ArtifactRef
}
```

This is not merely an audit log. It changes what future claims are valid. Once detailed promotion failures are fed back to an optimizer, that dataset has become development data for the next campaign.

> **Callout — Hidden-set non-interference**
>
> A proposal is valid for a campaign phase only if it depends exclusively on information that the phase's exposure policy permits. The control plane must enforce this through scoped query views rather than trusting optimizer code not to read hidden files.

---

## 7. Episodes, trajectories, spans, and events

### 7.1 Motivation

A final answer is insufficient for optimizing an agent. Two candidates may produce the same answer through very different retrieval, cost, and safety paths. A failure may happen at routing, evidence acquisition, tool parsing, projection, or generation.

### 7.2 Episode

> **Definition — Episode**
>
> An episode is one execution of one materialized system snapshot on one case under one trial assignment and repetition.

```go
type Episode struct {
    ID          EpisodeID
    TrialID     TrialID
    CandidateID CandidateID
    SnapshotID  SnapshotID
    CaseID      CaseID
    ArmID       ArmID
    Repeat      int
    Seed        *int64
    Status      EpisodeStatus
    StartedAt   time.Time
    FinishedAt  *time.Time
}
```

The current RagOpt `Cell` combines assignment, execution result, and comparison projection. OptKit should separate `Episode` identity from measurements and comparison records.

### 7.3 Trajectory

> **Definition — Trajectory**
>
> A trajectory is the ordered and causally linked record of observations, actions, operations, artifacts, and state transitions produced during an episode.

For a conversational agent:

\[
\tau = (h_0,a_0,o_1,a_1,o_2,\ldots,a_T).
\]

Here, actions can include text, retrieval, SQL, tool calls, widget intents, and termination. Observations can include tool results, admitted evidence, errors, and rendered UI artifacts.

### 7.4 Span and event

A linear log is useful for replay, but agent runtimes are concurrent and nested. OptKit should borrow the proven trace vocabulary of spans and events without requiring OpenTelemetry as the persistence format.

> **Definition — Span**
>
> A span represents an operation with a meaningful start and end, such as one model call, one tool call, one retrieval operation, or one judge invocation.

> **Definition — Trajectory event**
>
> A trajectory event is a timestamped occurrence within an episode, optionally associated with a span, such as evidence admitted, a token-usage update, a widget intent, or a terminal status.

```go
type TrajectoryEvent struct {
    APIVersion string
    EpisodeID  EpisodeID
    Sequence   uint64       // deterministic persisted order
    EventID    EventID
    Kind       EventKind
    OccurredAt time.Time

    TraceID       TraceID
    SpanID        *SpanID
    ParentSpanID  *SpanID
    LinkedSpanIDs []SpanID

    Attributes map[string]Value
    Artifacts  []ArtifactRef
    Payload    json.RawMessage
}
```

Sequence gives deterministic replay. Span relationships give causal structure. They are both needed.

### 7.5 Canonical event vocabulary

The core should standardize only broad semantic classes:

```text
input.received
model.call.started
model.call.completed
message.emitted
tool.call.started
tool.call.completed
retrieval.started
retrieval.completed
evidence.admitted
state.transition
ui.intent
ui.rendered
constraint.observed
error.observed
episode.completed
```

Products may add namespaced events:

```text
coinvault.knowledge.limit_resolved
coinvault.authorization.filtered
ragttc.chunk.fate_assigned
ragttc.index.query_completed
```

### 7.6 Coinvault worked trajectory

```text
#1  input.received
#2  model.call.started                  span=m1
#3  model.call.completed                span=m1 action=tool_call
#4  tool.call.started                    span=t1 parent=m1 tool=knowledge_search
#5  coinvault.knowledge.limit_resolved  span=t1 default=8 requested=5 effective=5 source=request
#6  retrieval.completed                 span=t1 hits=20
#7  coinvault.authorization.filtered    span=t1 removed=2
#8  evidence.admitted                   span=t1 count=5 ledger_digest=...
#9  tool.call.completed                  span=t1
#10 model.call.started                   span=m2
#11 message.emitted                      span=m2
#12 episode.completed                    status=success
```

This trace proves that a `default_results=8` treatment was not exercised because the explicit request set the effective limit to 5.

### 7.7 Widget worked trajectory

A future agent may choose to render a comparison table:

```text
#20 ui.intent
    kind=table
    semantic_role=comparison
    columns=[attribute, morgan, peace]

#21 ui.rendered
    renderer=coinvault-web/v3
    artifact=sha256:...
    validation=valid
```

The optimizer may evaluate whether the agent chose an appropriate presentation separately from whether the frontend rendered it correctly.

> **Pitfall — Storing hidden reasoning indiscriminately**
>
> A trajectory is not a mandate to store private chain-of-thought. Products should emit approved reasoning summaries, tool decisions, inputs, outputs, and observable state transitions. Redaction policy belongs in the product adapter and artifact store.

---

## 8. Intervention checks and constraints

### 8.1 Intervention check

#### Motivation

A candidate can be valid on disk but irrelevant at runtime. The changed code path may not execute, a default may be overridden, or the wrong prompt identity may be loaded.

#### Definition

> **Definition — Intervention check**
>
> An intervention check determines whether the causal change represented by a patch was actually applied and exercised in an episode.

Let

\[
I(\tau,\delta) \in \{\text{exercised},\text{not-exercised},\text{not-applicable},\text{indeterminate}\}.
\]

This is a manipulation check from experimental design.

```go
type InterventionAssessment struct {
    PatchID      PatchID
    EpisodeID    EpisodeID
    Status       InterventionStatus
    Checks       []CheckResult
    EvidenceRefs []ArtifactRef
    Diagnostics  []Diagnostic
}
```

`not-exercised` is not the same as “no quality improvement.” It means the experiment did not test the intended causal intervention for that episode.

### 8.2 Constraint

#### Motivation

Some requirements must not be traded against quality. Authorization, contract validity, evidence containment, complete artifact custody, and protected-case behavior are examples.

#### Definition

> **Definition — Constraint**
>
> A constraint is a deterministic or measured predicate that defines whether an episode, candidate, trial, or promotion is admissible.

\[
g_j(\theta,\tau,M) \le 0.
\]

Constraints can be scoped:

```text
episode constraint   one run must cite resolvable evidence
trial constraint     every expected episode must be present
candidate constraint no protected-case failure
campaign constraint  total spend must stay below ceiling
promotion constraint hidden validation must pass
```

#### Proposed API

```go
type Constraint interface {
    ID() ConstraintID
    Scope() ConstraintScope
    Evaluate(ctx context.Context, input ConstraintInput) (ConstraintResult, error)
}

type ConstraintResult struct {
    ConstraintID ConstraintID
    Subject      SubjectRef
    Passed       bool
    Applicable   bool
    Severity     Severity
    EvidenceRefs []ArtifactRef
    Diagnostics  []Diagnostic
}
```

### 8.3 Coinvault answer contract example

The current answer contract already has useful stages:

```text
generation
route
retrieval
contract
```

These should remain product-defined constraints, projected into generic `ConstraintResult` records. The product retains the detailed native report.

```text
constraint: coinvault.route.required_knowledge
subject: episode E17
passed: false
stage: route
evidence: native/outcome.json#answer_contract/checks/...
```

### 8.4 Why constraints are not negative rewards

A scalar objective such as

\[
0.6\,\text{faithfulness} + 0.4\,\text{relevance} - 0.2\,\text{route-failure}
\]

allows enough faithfulness to compensate for a forbidden route. That is not the intended product semantics.

OptKit should instead optimize

\[
\max_{\theta\in\mathcal F} J(\theta),
\]

where \(\mathcal F\) is the set of configurations satisfying hard constraints.

---

## 9. Measurements, instruments, and measurement epochs

### 9.1 Motivation

The current generic `map[string]float64` is convenient for arithmetic but cannot say what a number means, which evaluator produced it, whether it applies, or whether two numbers are comparable.

### 9.2 Construct

> **Definition — Construct**
>
> A construct is the abstract property an evaluation intends to measure, such as evidence faithfulness, answer relevance, route appropriateness, or widget usefulness.

A construct is not the score itself. Faithfulness is a property; `0.82` is one reported measurement of it under a particular operationalization.

### 9.3 Measurement contract

> **Definition — Measurement contract**
>
> A measurement contract operationalizes a construct by specifying observable inputs, evidence rules, labels, exclusions, aggregation, ranges, direction, and missingness behavior.

JudgeKit already owns this concept. OptKit should reference JudgeKit contract and protocol identities rather than duplicate them.

### 9.4 Instrument and protocol

> **Definition — Instrument**
>
> An instrument is an implementation that observes an episode or evaluation instance and produces measurements.

> **Definition — Protocol**
>
> A protocol is the complete reproducible identity of how an instrument measures: model, prompt digests, decoding, evidence ordering, parser, retry, and aggregation versions.

Changing a judge prompt, model, ordering policy, or parser changes the protocol digest.

### 9.5 Measurement

```go
type Measurement struct {
    APIVersion string
    ID         MeasurementID

    Subject       SubjectRef // episode, trial, candidate, campaign
    ConstructID   string
    ContractDigest Digest
    ProtocolDigest Digest
    InstrumentID   string

    Value          MeasurementValue
    Direction      Direction
    Applicable     bool
    MissingReason  *MissingReason
    Uncertainty    *Uncertainty

    EvidenceRefs   []ArtifactRef
    Diagnostics    []Diagnostic
    ProducedAt     time.Time
    Digest         Digest
}

type MeasurementValue struct {
    Kind        ValueKind // scalar, boolean, ordinal, categorical, vector, distribution
    Scalar      *float64
    Boolean     *bool
    Ordinal     *int
    Category    *string
    Vector      []float64
    Distribution *Distribution
}
```

A compatibility projection may still expose numeric maps:

```go
func LegacyMetrics(ms []Measurement) map[string]float64
```

but that map is derived, never authoritative.

### 9.6 Measurement epoch

#### Motivation

Suppose evaluator v8 and evaluator v10 both emit a field called `faithfulness`. If their prompts, claim extraction, evidence policy, or parser differ, averaging them produces a number with no stable interpretation.

#### Definition

> **Definition — Measurement epoch**
>
> A measurement epoch is a period or comparison domain in which a construct is measured under one compatible measurement contract and protocol identity, or under explicitly calibrated bridge protocols.

A simple rule for v1:

```text
same construct ID is not sufficient
same contract digest + same protocol digest is required for direct aggregation
```

When the protocol changes, the campaign must either:

1. remeasure all compared candidates under the new protocol;
2. retain separate series;
3. use an explicit calibration bridge approved for that comparison.

### 9.7 Worked Coinvault measurement

```yaml
subject: episode:feedback-compare-morgan-peace/challenger/0
construct_id: faithfulness
contract_digest: sha256:contract-v1
protocol_digest: sha256:judge-v8
value: {kind: scalar, scalar: 1.0}
applicable: true
evidence_refs:
  - native/outcome.json#judge/claim_assessments
```

The paired delta should record the two source measurement IDs, not merely `+0.5405`.

> **Callout — Judges measure; selectors decide**
>
> JudgeKit should never know whether a candidate is promoted. OptKit's selection layer consumes measurements, calibration reports, deterministic constraints, and exposure records. This separation prevents a judge implementation from becoming an unreviewed deployment authority.

---

## 10. Objectives, comparison, and uncertainty

### 10.1 Objective

> **Definition — Objective**
>
> An objective declares how a campaign wants a construct or derived quantity to change over a population. It references measurements but adds direction, scope, aggregation, and target semantics.

```go
type Objective struct {
    ID              ObjectiveID
    ConstructID     string
    Direction       Direction
    Population      PopulationSelector
    Aggregation     AggregationSpec
    MinimumEffect   *float64
    MeasurementRule MeasurementCompatibilityRule
}
```

A construct says what faithfulness means. An objective says “maximize mean paired faithfulness delta on comparison cases, with no per-case drop below -0.20.”

### 10.2 Vector objective

For a candidate \(\theta\), define

\[
J(\theta)
= \mathbb E_{x,\tau}\left[M(\tau)\right]
= (J_1(\theta),\ldots,J_k(\theta)).
\]

OptKit should retain this vector rather than immediately scalarizing it.

### 10.3 Paired comparison

For case \(i\), repeat \(r\), and metric \(m\):

\[
\Delta_{i,r}^{(m)}
=
M_m(\tau_{i,r}^{challenger})
-
M_m(\tau_{i,r}^{incumbent}).
\]

The group mean is

\[
\bar\Delta_G^{(m)}
=
\frac{1}{|G|}
\sum_{i\in G}
\frac{1}{R_i}
\sum_r \Delta_{i,r}^{(m)}.
\]

This is the current RagOpt design and should remain a first-class `PairedComparisonStrategy`.

### 10.4 Other comparison strategies

OptKit should support:

- independent-arm comparisons;
- repeated-measures or blocked comparisons;
- multi-arm rank tables;
- factorial effects and interactions;
- oracle-relative error;
- non-inferiority and equivalence checks;
- sequential confidence intervals;
- Pareto dominance.

The first release can implement paired and multi-arm descriptive comparison, leaving advanced inference behind interfaces.

### 10.5 Uncertainty

```go
type Uncertainty struct {
    Method          string // bootstrap, t, bayesian, exact-binomial, none
    Estimate        float64
    StandardError   *float64
    Lower           *float64
    Upper           *float64
    ConfidenceLevel *float64
    SampleSize      int
    Notes           []string
}
```

The framework must distinguish:

```text
no uncertainty computed
```

from

```text
zero uncertainty
```

They are not equivalent.

### 10.6 Adaptive-selection warning

Testing many candidates against the same development cases and reporting the largest observed improvement creates selection bias. A confidence interval computed as though the winner had been chosen in advance is too optimistic. OptKit's history and exposure records make the amount of adaptivity visible; final promotion should use fresh data or explicitly sequential procedures.

---

## 11. Trials, arms, assignments, repeats, and designs

### 11.1 Trial

> **Definition — Trial**
>
> A trial is a frozen experimental comparison among one or more candidate snapshots over a dataset according to a trial design, resource policy, and measurement suite.

```go
type Trial struct {
    ID              TrialID
    CampaignID      CampaignID
    Design          TrialDesignRef
    Candidates      []CandidateID
    Dataset         DatasetID
    MeasurementSuite MeasurementSuiteID
    ConstraintSuite ConstraintSuiteID
    ResourcePolicy  ResourcePolicyID
    Status          TrialStatus
}
```

### 11.2 Arm

> **Definition — Arm**
>
> An arm is a labeled candidate assignment within a trial. `incumbent` and `challenger` are arm roles, not candidate identities.

The same candidate might be `challenger` in one trial and `incumbent` in a later trial.

### 11.3 Assignment and repeat

```go
type Assignment struct {
    TrialID     TrialID
    ArmID       ArmID
    CandidateID CandidateID
    CaseID      CaseID
    Repeat      int
    Seed        *int64
    Block       *BlockID
}
```

The schedule is a deterministic set of assignments. Execution order may be randomized or interleaved, but the plan should record that policy.

### 11.4 Trial design interface

```go
type TrialDesign interface {
    ID() TrialDesignID
    Validate(spec TrialSpec) error
    Assign(spec TrialSpec) ([]Assignment, error)
    Comparator() ComparisonStrategy
}
```

Built-in designs for v1:

```text
paired-two-arm
multi-arm-blocked
single-candidate-diagnostic
oracle-relative
```

### 11.5 Worked examples

Coinvault grounding prompt:

```text
design: paired-two-arm
arms: incumbent, challenger
cases: feedback suite
repeats: 1
pairing key: case ID + repeat
```

TTC chunker experiment:

```text
design: multi-arm-blocked
arms: markdown, markdown+summary, markdown-heading
cases: retrieval query suite
block: query ID
metrics: MRR, Recall@1, Recall@5, nDCG@10, build time
```

---

## 12. Campaigns, plans, optimizers, archives, and selectors

### 12.1 Campaign

#### Motivation

Individual candidate directories do not fully record the adaptive process that led to a winner. We need to retain every attempted candidate, trial, critique, evaluator epoch, hidden exposure, and decision.

#### Definition

> **Definition — Campaign**
>
> A campaign is the persistent, append-only optimization process for one baseline system, search space, data policy, measurement regime, resource budget, search policy, and promotion policy.

A compact mathematical description is

\[
\mathcal C =
(\Theta,\mathcal D,S,M,G,A,B,H),
\]

where:

- \(\Theta\) is the search space;
- \(\mathcal D\) is the role-tagged data collection;
- \(S\) is the product executor/materializer;
- \(M\) is the measurement suite;
- \(G\) is the constraint and selection policy;
- \(A\) is the optimizer/search policy;
- \(B\) is the resource budget;
- \(H\) is the accumulated history.

### 12.2 Plan

#### Motivation

Before a campaign runs, an operator wants to see what will happen and what it could cost. An adaptive optimizer, however, cannot list every future candidate because later proposals depend on earlier results.

#### Definition

> **Definition — Campaign plan**
>
> A campaign plan is a frozen specification of known phases, adaptive decision policies, allowed transitions, datasets, budgets, stopping conditions, and promotion requirements. It is not necessarily a fully expanded DAG of future work.

Example:

```text
baseline verification
        ↓
initial diagnostic trial
        ↓
┌──────── adaptive search, at most 6 rounds ────────┐
│ propose ≤ 4 candidates                            │
│ mini-evaluate on development cases                │
│ update Pareto archive                             │
│ reflect from selected trajectories                │
│ stop on budget, stagnation, or target attainment  │
└───────────────────────────────────────────────────┘
        ↓
full evaluation of ≤ 3 finalists
        ↓
hidden promotion trial
        ↓
blinded human review
        ↓
manual deployment authorization
```

### 12.3 Optimizer

> **Definition — Optimizer**
>
> An optimizer is a proposal policy that maps an allowed view of campaign history to zero or more candidate proposals:
>
> \[
> \delta_{n+1} \sim q_A(\delta\mid H_n).
> \]

It does not execute candidates and does not promote them.

```go
type Optimizer interface {
    ID() OptimizerID
    Propose(ctx context.Context, req ProposalRequest) (ProposalBatch, error)
}

type ProposalRequest struct {
    Campaign     CampaignView
    Baseline     SnapshotView
    SearchSpace  SearchSpaceView
    History      HistoryView
    Archive      ArchiveView
    Budget       ProposalBudget
    AllowedData  ExposureScopedView
}
```

The `AllowedData` view is crucial. It is how hidden-set non-interference is enforced.

Built-in optimizers may include:

| Optimizer | Proposal behavior |
|---|---|
| Manual | imports a human-authored patch |
| Coordinate | enumerates or mutates one variable at a time |
| Random/grid | samples declared domains |
| Successive halving | allocates more evaluations to promising candidates |
| Bandit | allocates online or repeated trials among approved arms |
| Bayesian | proposes from a surrogate over a small mixed domain |
| Reflective | uses selected trajectories and textual feedback to propose typed patches |
| GEPA-like | reflective mutation plus a Pareto/evolutionary archive |
| MIPRO-like | jointly searches instructions/examples with surrogate-assisted evaluation |
| TextGrad-like | propagates textual critiques toward responsible variables in a computation graph |

### 12.4 Reflector

A reflector is often useful as a narrower plugin than a complete optimizer.

> **Definition — Reflector**
>
> A reflector converts selected trajectories, measurements, and diagnostics into a structured critique and proposed change targets. An optimizer decides how to use that critique.

```go
type Reflector interface {
    Reflect(ctx context.Context, packet ReflectionPacket) (Reflection, error)
}
```

This separation lets a human approve or edit a reflection before a patch is materialized.

### 12.5 Archive and Pareto frontier

> **Definition — Archive**
>
> An archive is the retained set of candidates and their evidence used by a search policy. It is not only the current winner.

Candidate \(a\) dominates \(b\) when

\[
\forall k, J_k(a) \ge J_k(b)
\quad\text{and}\quad
\exists k, J_k(a) > J_k(b),
\]

after normalizing direction and respecting feasibility. The Pareto frontier is

\[
\mathcal P =
\{a : \nexists b \text{ such that } b \succ a\}.
\]

A candidate may remain valuable because it solves a subset of cases or has lower cost, even when another candidate has a higher overall mean.

### 12.6 Selector and promotion

> **Definition — Selector**
>
> A selector consumes evidence and decides which candidates advance to another phase or become finalists. It is distinct from the optimizer.

> **Definition — Promotion policy**
>
> A promotion policy governs whether a finalist may be recommended for deployment. It can require hidden validation, calibrated evaluators, human review, and operational checks.

Current Coinvault/RagOpt gates are lexicographic selectors:

```text
identity
  ↓ only if pass
hard constraints
  ↓ only if pass
target improvement
  ↓ only if pass
regression bounds
  ↓ only if pass
cost tie-breakers
```

This should remain the default conservative pattern.

### 12.7 Complete loop

The generalized loop is:

\[
\begin{aligned}
P_n &\leftarrow A(H_n) && \text{propose patches}\\
\theta'_j &\leftarrow \theta \oplus \delta_j && \text{materialize candidates}\\
\tau_{i,j,r} &\sim S_{\theta'_j}(x_i) && \text{execute episodes}\\
I_{i,j,r} &\leftarrow I(\tau_{i,j,r},\delta_j) && \text{check intervention}\\
C_{i,j,r} &\leftarrow C(\tau_{i,j,r}) && \text{check constraints}\\
M_{i,j,r} &\leftarrow M(\tau_{i,j,r}) && \text{measure}\\
R_j &\leftarrow \operatorname{Compare}(M,C,I) && \text{summarize trial}\\
D_j &\leftarrow G(R_j,H_n) && \text{select/reject/advance}\\
H_{n+1} &\leftarrow H_n \cup \{P,\tau,I,C,M,R,D\}. && \text{append history}
\end{aligned}
\]

This equation is the conceptual center of OptKit.

---
EOF

```

```unknown
bash -lc cat >> /mnt/data/optkit-architecture-and-migration-guide.md <<'EOF'

# Part III — OptKit architecture

## 13. Design goals, non-goals, and laws

### 13.1 Design goals

OptKit should make the following operations natural:

1. describe a heterogeneous search space without importing a product runtime;
2. create immutable snapshots, patches, and candidate lineages;
3. render an honest adaptive plan before execution;
4. execute paired, multi-arm, diagnostic, and oracle-relative trials;
5. stream product trajectories while preserving native artifacts;
6. record typed measurements and deterministic constraints separately;
7. compare candidates without collapsing every objective into one score;
8. support manual, coordinate, reflective, evolutionary, and other optimizers through one proposal boundary;
9. resume after interruption without rewriting prior evidence;
10. reconstruct every plan, event, result, and decision;
11. provide stable projection APIs for web UIs, TUIs, and command-line tools;
12. import existing RagOpt candidate bundles and run directories.

### 13.2 Non-goals

The first OptKit release should explicitly exclude:

- distributed workflow scheduling across a cluster;
- arbitrary user-authored DAG execution;
- model training or policy-gradient RL;
- automatic production deployment;
- a universal scalar reward function;
- a universal product trace schema that erases native artifacts;
- prompt ownership or judge-prompt ownership;
- direct model-provider clients in the core;
- a permanent dependency on React, Bubble Tea, Cobra, Glazed, or a database driver in core model packages;
- automatic access to hidden evaluation data;
- storage of private chain-of-thought;
- backwards compatibility for every internal Go API before `v1`.

> **Callout — Why OptKit is not a workflow engine**
>
> A campaign has phases and adaptive transitions, but its semantics are optimization-specific: candidates, trials, measurements, constraints, archives, and selection. General-purpose workflow concerns such as arbitrary business process modeling should stay outside the core. FlowKit continues to execute bounded work; OptKit persists optimization control state.

### 13.3 Laws

Interfaces are useful, but laws are what make independently written implementations compose safely.

#### Law 1: deterministic replay

For a valid journal prefix \(E_{1:n}\), reducing it twice yields the same campaign state:

\[
\operatorname{Reduce}(E_{1:n})
=
\operatorname{Reduce}(E_{1:n}).
\]

More practically, replay cannot depend on wall-clock time, map iteration order, network calls, or mutable external state.

#### Law 2: prefix stability

Appending new events never changes the identity or meaning of earlier events, snapshots, measurements, or decisions.

#### Law 3: semantic identity invariance

Execution policy such as worker count, scheduling order, retry count, or UI metadata does not alter snapshot identity unless it can alter semantic output and is intentionally modeled as a dimension.

#### Law 4: rejection purity

Rejecting a candidate cannot mutate its parent snapshot, deployment state, or other candidates.

#### Law 5: complete lineage

Every materialized candidate has a path

```text
parent snapshot → patch → child snapshot → candidate
```

and every promoted deployment has a path

```text
candidate → trials → measurements → decision → approval → deployment record
```

#### Law 6: measurement-epoch isolation

Measurements from incompatible contract or protocol digests are never silently aggregated.

#### Law 7: hidden-set non-interference

An optimizer proposal may depend only on data and derived information explicitly exposed to that optimizer in the current phase.

#### Law 8: budget conservation

No successful resource admission path may exceed its declared campaign and phase ceilings. Retries and failed billable calls count according to resource policy.

#### Law 9: hard-gate non-compensation

No amount of soft-objective improvement can compensate for a failed hard constraint.

#### Law 10: native-artifact authority

A generic projection never replaces or contradicts the product-owned native artifact from which it was derived. When they differ, the projection is invalid and must be regenerated or rejected.

#### Law 11: idempotent command handling

Submitting the same command with the same idempotency key either returns the existing result or has no additional effect.

#### Law 12: terminal evidence immutability

Once an episode, trial, or decision is terminal, corrections are represented by superseding records or new epochs, not in-place edits.

---

## 14. Module and package structure

### 14.1 Repository-level dependencies

The recommended module graph is:

```text
                  +--------------------+
                  |     coinvault      |
                  +---------+----------+
                            |
                  +---------v----------+
                  |       optkit       |
                  +---+----------+-----+
                      |          |
              +-------v--+   +---v-------+
              | flowkit  |   | judgekit  |
              +----------+   +-----------+
                      |
              +-------v--+
              | ragkit   |
              +----------+

                  +--------------------+
                  |      rag-ttc       |
                  +---------+----------+
                            |
                            +---- imports optkit, flowkit,
                                 judgekit adapters, ragkit
```

`optkit` core should not import Coinvault, `rag-ttc`, RagKit, provider SDKs, or UI frameworks. An optional `optkit/adapter/judgekit` package may import JudgeKit. FlowKit may be used by `optkit/runtime`, but low-level model packages should remain standard-library-only.

### 14.2 Proposed package tree

```text
optkit/
  model/          stable IDs, digests, subjects, artifacts, common value types
  space/          variables, domains, search-space constraints, registries
  snapshot/       snapshots, patches, candidates, materialization records, lineage
  data/           cases, datasets, roles, exposure policies and records
  plan/           campaign plans, phases, adaptive nodes, budgets, stop conditions
  campaign/       commands, events, reducer, state machine, lifecycle validation
  trial/          trial specifications, designs, arms, assignments, schedules
  trajectory/     episodes, spans, trajectory events, segment manifests
  measure/        instrument boundary, typed measurements, compatibility rules
  constraint/     generic constraint results and suite orchestration
  compare/        paired, multi-arm, oracle-relative, and aggregate comparisons
  select/         lexicographic gates, phase advancement, promotion evidence
  archive/        candidate archive, Pareto frontier, lineage queries
  search/         optimizer and reflector interfaces; built-in simple optimizers
  runtime/        campaign runner, FlowKit-backed execution, retries, budgets
  store/          journal, artifact, snapshot, and projection-store interfaces
  projection/     rebuildable read models for UI and query clients
  transport/      command/query/event-stream DTOs; no HTTP dependency in core
  adapter/
    flowkit/       runtime/resource integration helpers
    judgekit/      JudgeKit reports and suites into OptKit measurements
    ragopt/        compatibility import/export
  schema/         JSON Schema generation and versioned document validation
  testing/        fake system, fake instrument, deterministic fixtures

cmd/optkit/
  validate
  plan
  run
  resume
  pause
  cancel
  inspect
  compare
  import
  export
  replay
  doctor
  serve
```

### 14.3 Package dependency direction

```text
model
  ↑
space  data  trajectory  measure  constraint
  ↑      ↑       ↑          ↑          ↑
snapshot  trial  compare  archive
     \      |      |       /
      \     v      v      /
          select
             ↑
            plan
             ↑
          campaign
             ↑
           runtime
             ↑
       product adapters
```

This diagram is conceptual rather than a literal import graph. The implementation should use a boundary test, as JudgeKit and FlowKit already do, to prevent accidental product/framework imports into core packages.

### 14.4 Why `model` must stay small

A common failure is creating a “common” package that becomes a dumping ground. `model` should contain only primitives with stable meaning across every subsystem:

```text
Digest
ArtifactRef
SubjectRef
typed IDs
Diagnostic
Actor/Proposer identity
semantic version helpers
canonical timestamp and money/resource values
```

It should not contain campaign logic, database code, product types, or convenience functions that cause dependency cycles.

---

## 15. Identity and content addressing

### 15.1 Motivation

Optimization is impossible to audit when “candidate B” or “judge v8” refers to mutable files. Existing RagOpt snapshots and run cells already use digests effectively. OptKit should make content addressing pervasive but distinguish several identities.

### 15.2 Identity classes

| Identity | Meaning | Should change when |
|---|---|---|
| byte digest | exact bytes | whitespace or formatting changes |
| semantic digest | normalized meaning | semantically relevant field changes |
| logical ID | human-facing stable name | owner intentionally renames/replaces concept |
| event ID | unique occurrence | every appended occurrence |
| lineage ID | graph node identity | candidate/patch/snapshot is new |

Both byte and semantic digests are useful. A YAML file can have a new byte digest but the same semantic digest after comment-only changes.

### 15.3 Canonical digest API

```go
type Digester interface {
    SemanticDigest() (model.Digest, error)
}

func CanonicalDigest[T any](value T) (model.Digest, error)
func ByteDigest(data []byte) model.Digest
```

Canonical encoding rules must be versioned. Never silently change how semantic digests are computed.

### 15.4 Snapshot identity input

A snapshot semantic digest should include:

```text
API version
system ID
sorted variable IDs and value digests
sorted semantic dimensions
artifact identities required for behavior
materialization schema version
```

It should exclude:

```text
display title
creation timestamp
filesystem path chosen for a temporary workspace
worker count, unless worker count changes semantics
UI annotations
```

### 15.5 External mutable resources

A URI is not enough to identify a corpus, model profile, or index. Product adapters should resolve mutable references into immutable dimensions before a plan is frozen:

```go
type Resolver interface {
    Resolve(ctx context.Context, ref ExternalRef) (ResolvedIdentity, error)
}
```

Example:

```text
input:  profile "default/gpt-5.6-luna-low"
output: provider + model + profile digest + registry digest + adapter revision
```

---

## 16. Search-space and variable registry design

### 16.1 Registry responsibilities

A product registry is the bridge between generic candidate patches and product semantics.

```go
type Registry interface {
    Get(id VariableID) (VariableDefinition, bool)
    List() []VariableDefinition
    ValidatePatch(base SnapshotView, patch Patch) error
    ValidateJoint(values map[VariableID]ValueRef) error
}
```

A registry entry should provide:

```go
type Entry struct {
    Definition          VariableDefinition
    Materializer        VariableMaterializer
    InterventionChecker InterventionChecker
    DiffRenderer        DiffRenderer
    Redactor            Redactor
    Dependencies        []VariableID
    Conflicts           []VariableID
    Tags                []string
}
```

### 16.2 Domain types

The core should provide common domains:

```text
BooleanDomain
IntegerDomain
RealDomain
CategoricalDomain
ArtifactDomain
TextArtifactDomain
StructuredArtifactDomain
ProductDomain (validation callback only in product adapter)
```

Text should normally be represented as an immutable artifact, not embedded directly in every patch and event.

### 16.3 Cross-variable constraints

```go
type SpaceConstraint interface {
    ID() string
    Validate(values map[VariableID]ValueRef) error
}
```

Examples:

```text
reranker pool size ≥ reranker top-k
forced result count ≤ maximum result count
answer schema version compatible with orchestration prompt version
ANN parameter efSearch valid for selected index backend
```

### 16.4 Locked and mutable status belong to the plan

A variable may be globally defined but locked in one campaign.

```yaml
variables:
  answer.grounding_prompt:
    mode: optimize
    domain: approved-text-artifacts
  answer.model:
    mode: locked
    value: default/gpt-5.6-luna-low
  authorization.policy:
    mode: forbidden
```

This is better than classifying variables as permanently mutable or locked in the registry.

### 16.5 Diff rendering

A UI needs domain-aware diffs:

```go
type DiffRenderer interface {
    Render(before, after ValueRef) (DiffDocument, error)
}
```

Examples:

- text prompt: line/word diff;
- integer: `5 → 8`;
- reranker config: field table;
- structured query plan: semantic tree diff;
- chunker: parameter and algorithm diff;
- model profile: resolved identity diff.

The raw bytes remain available, but the UI should not have to infer how to render every value.

---

## 17. Materialization architecture

### 17.1 Motivation

A snapshot is declarative. The product runtime needs files, structs, registries, caches, and process configuration. Materialization translates one into the other without allowing the generic framework to know product internals.

### 17.2 Definitions

> **Definition — Workspace**
>
> A workspace is an isolated directory or content-addressed environment in which a product adapter materializes an executable candidate.

> **Definition — Materialization record**
>
> A materialization record proves what snapshot was materialized, which adapter and source revision performed the work, what files or resources were produced, and what effective runtime identity resulted.

```go
type Materializer interface {
    ID() string
    Version() string
    Materialize(ctx context.Context, req MaterializeRequest) (Materialization, error)
}

type MaterializeRequest struct {
    Snapshot  SnapshotView
    Workspace Workspace
    Secrets   SecretResolver
}

type Materialization struct {
    ID              MaterializationID
    SnapshotID      SnapshotID
    AdapterIdentity AdapterIdentity
    ExecutableRef   ExecutableRef
    EffectiveConfig ArtifactRef
    Produced        []ArtifactRef
    Diagnostics     []Diagnostic
    Digest          Digest
}
```

### 17.3 Materialization must be deterministic where possible

Given the same snapshot and adapter revision, materialization should produce the same semantic effective configuration. Temporary paths may differ, so they must not enter the semantic digest.

### 17.4 Product-owned safety validation

Materialization is the last point before execution and should enforce product invariants:

```text
Coinvault:
  authorization policy unchanged
  canonical chat route selected
  source lock and bundle identities match
  prompt suffix attached in the intended position

rag-ttc:
  tool-loop safety ceilings respected
  answer schema parses
  disabled tools remain disabled
  index bundle and provider profile match the snapshot
```

### 17.5 Worked TTC materializer

The current `materializeToolConfig` writes three assets and then concatenates a hardcoded YAML configuration. The port should replace it with typed construction:

```go
type TTCSnapshotMaterializer struct {
    BaseConfig toolconfig.Config
}

func (m *TTCSnapshotMaterializer) Materialize(
    ctx context.Context,
    req optkit.MaterializeRequest,
) (optkit.Materialization, error) {
    cfg := m.BaseConfig.DeepCopy()

    cfg.Prompts.Orchestration = req.Snapshot.Artifact("agent.orchestration_prompt")
    cfg.Prompts.OutputSchema  = req.Snapshot.Artifact("agent.answer_schema")
    cfg.Tools.Search.Description = req.Snapshot.Artifact("search.description")

    if err := ttcconstraints.ValidateRuntimeConfig(cfg); err != nil {
        return optkit.Materialization{}, err
    }

    effective := canonicaljson.Marshal(cfg)
    // Write files and record all digests.
}
```

The first migration may retain the existing text generation behind this interface, but tests should lock its output. The final state should use the typed config model.

---

## 18. Runtime execution and FlowKit integration

### 18.1 Division of labor

FlowKit already solves bounded, retry-aware, cache-aware execution. OptKit should not duplicate those mechanics.

```text
OptKit decides:
  which assignments exist
  which phase they belong to
  which candidate/case is being executed
  what campaign resources apply
  what events and artifacts must be recorded

FlowKit executes:
  bounded work
  retries
  cache admission
  rate and budget admission
  batching
  metering
  per-item reports and ledgers
```

### 18.2 Executor interface

```go
type Executor interface {
    ID() string
    Execute(
        ctx context.Context,
        req EpisodeRequest,
        sink trajectory.Sink,
    ) (EpisodeResult, error)
}

type EpisodeRequest struct {
    Episode        Episode
    Materialization Materialization
    Case           data.CaseView
    ResourceHandle ResourceHandle
    NativeDir      string
}

type EpisodeResult struct {
    Status          EpisodeStatus
    NativeArtifacts []ArtifactRef
    Usage           []ResourceUsage
    TerminalSummary ArtifactRef
    Diagnostics     []Diagnostic
}
```

The executor streams observable trajectory events to `sink` and returns only terminal facts.

### 18.3 FlowKit-backed assignment step

```go
step := flow.Step[trial.Assignment, runtime.EpisodeResult]{
    Name: "optkit.execute-episode",
    Identity: flow.Identity[trial.Assignment]{
        Kind:    "optkit-episode",
        Version: "v1",
        Key: func(a trial.Assignment) ([]byte, error) {
            return canonicaljson.Marshal(struct {
                Snapshot  SnapshotID
                Case      CaseID
                Repeat    int
                Seed      *int64
                Executor  string
                DataEpoch Digest
            }{...})
        },
    },
    Policy: flow.Policy{
        Workers: plan.Execution.Workers,
        Retry:   retrySpec,
        OnError: flow.Quarantine,
    },
    Do: executeAssignment,
}
```

Whether episode execution is cacheable must be explicit. Deterministic retrieval benchmarks may be cacheable; a stochastic model episode often should not be reused unless the protocol and seed semantics make reuse valid.

### 18.4 Campaign resources

OptKit should describe named resources generically:

```yaml
resources:
  answer-provider-calls: {ceiling: 216}
  embedding-calls: {ceiling: 192}
  judge-provider-calls: {ceiling: 72}
  answer-provider-tokens: {ceiling: 1000000}
  estimated-usd: {ceiling: 50.00}
```

The product adapter maps runtime usage into these names. FlowKit performs admission and metering.

### 18.5 Attempt semantics

Every billable attempt, including a failed or retried provider call, must be recordable. Current Coinvault budget logic already recognizes uncertain provider spend. OptKit should preserve the distinction:

```text
admitted
started
provider may have billed
completed with usage
failed before provider
usage uncertain
```

A resource ledger should never infer that a failed call was free.

### 18.6 Cancellation

Campaign cancellation, phase cancellation, and episode timeout are distinct events. Successful expensive work may still need to commit its artifact after a sibling fails, matching FlowKit's existing invariant.

```go
campaign.cancel.requested
trial.cancel.requested
episode.timeout
artifact.committed-after-cancellation
```

---

## 19. Measurement and JudgeKit integration

### 19.1 Adapter boundary

JudgeKit remains authoritative for measurement structures. OptKit needs a minimal generic `Instrument` interface so deterministic metrics, human review, external benchmarks, and JudgeKit can coexist.

```go
type Instrument interface {
    ID() InstrumentID
    Protocol() ProtocolRef
    Measure(ctx context.Context, req MeasureRequest) ([]Measurement, error)
}

type MeasureRequest struct {
    Subject     SubjectRef
    Episode     trajectory.EpisodeView
    Artifacts   ArtifactResolver
    Prior       MeasurementView
}
```

### 19.2 JudgeKit adapter

```go
type JudgeKitInstrument struct {
    Suite judgekitsuite.Suite
    BuildInstance func(context.Context, MeasureRequest) (judgekiteval.Instance, error)
    Project       func(judgekitsuite.Results) ([]optmeasure.Measurement, error)
}
```

The product owns `BuildInstance`, because it decides what question, answer, evidence, required facts, and product metadata the judge may observe.

### 19.3 Deterministic instruments

Examples:

```text
citation resolver
required-route checker
retrieval metric calculator
latency/cost projector
schema validator
intervention checker
```

These may produce measurements or constraints depending on semantics. A citation-resolution rate can be a measurement; “all citations must resolve” is a constraint derived from it.

### 19.4 Measurement suites

```go
type Suite struct {
    ID          MeasurementSuiteID
    Instruments []InstrumentSpec
    Graph       DependencyGraph
    Digest      Digest
}
```

Independent instruments can run concurrently. Dependent instruments declare their inputs, like JudgeKit's evaluator suite.

### 19.5 Skipping a judge safely

Coinvault currently skips the LLM judge when deterministic contract or intervention checks fail. This is a good policy because it avoids spending judge calls on invalid episodes and prevents invalid answers from receiving misleading quality measurements.

OptKit should express this as a measurement precondition:

```yaml
instrument: coinvault.answer-judge
when:
  all_constraints_pass:
    - coinvault.generation.complete
    - coinvault.intervention.valid_or_not_applicable
    - coinvault.answer_contract.valid
on_skip:
  missing_reason: precondition_failed
```

Missing measurements must remain visible; they are not zeros and must not be dropped from denominators silently.

### 19.6 Calibration requirements

A promotion phase can require:

```yaml
measurement_requirements:
  - construct: faithfulness
    protocol: sha256:...
    calibration:
      minimum_extraction_recall: 0.90
      maximum_false_support_rate: 0.05
      maximum_ece: 0.10
      calibration_set: sha256:...
```

The first implementation may validate only protocol identity and the presence of a calibration report. The schema should support richer requirements without forcing every campaign to use them.

---

## 20. Comparison architecture

### 20.1 Comparison as a derived artifact

A comparison should be reproducible from assignments, measurement IDs, constraint results, and a comparison strategy. It is a derived artifact, not a mutable table maintained by hand.

```go
type Comparison struct {
    ID             ComparisonID
    TrialID        TrialID
    StrategyID     string
    InputsDigest   Digest
    Pairings       []Pairing
    Estimates      []Estimate
    Missing        []MissingComparison
    Diagnostics    []Diagnostic
    ArtifactRef    ArtifactRef
    Digest         Digest
}
```

### 20.2 Paired strategy

```go
type PairedStrategy struct {
    PairBy []AssignmentField // usually case ID + repeat + block
}
```

The strategy must reject duplicate pair members and retain missing incumbent/challenger cells rather than silently discarding them.

### 20.3 Multi-arm strategy

A multi-arm result may be represented as:

```go
type ArmEstimate struct {
    ArmID       ArmID
    ObjectiveID ObjectiveID
    Estimate    float64
    Uncertainty *Uncertainty
    Rank        *int
}
```

Pairwise contrasts can be derived but should not be required for every UI.

### 20.4 Cost accounting

Product execution cost and evaluation overhead should be separate dimensions:

```text
system cost:
  answer provider calls
  embedding calls
  tool calls
  runtime tokens
  latency

evaluation cost:
  judge calls
  reflector calls
  human review time
  calibration cost
```

The current `rag-ttc` adapter correctly excludes judge overhead from the product cost projection. OptKit should retain both ledgers rather than mixing them.

### 20.5 Comparison compatibility checks

Before arithmetic, the comparator validates:

```text
same compatible measurement epoch
same dataset/case identity
same trial design assumptions
expected assignments present or explicitly missing
candidate/snapshot identities match schedule
constraint status interpreted according to policy
```

---

## 21. Selection, gates, and promotion

### 21.1 Phase-ordered policy

The current RagOpt policy should become a generic ordered policy:

```go
type SelectionPolicy struct {
    ID     SelectionPolicyID
    Phases []SelectionPhase
}

type SelectionPhase struct {
    ID        string
    Mode      PhaseMode // all, any, ordered-first-failure
    Checks    []SelectionCheck
    OnPass    Transition
    OnFailure Transition
}
```

A Coinvault compatibility constructor can map the current schema:

```text
HardGates   → phases identity + hard
Target      → target phase
Regressions → regression phase
TieBreakers → cost phase
```

### 21.2 Decision record

```go
type Decision struct {
    ID             DecisionID
    Subject        SubjectRef
    PolicyDigest   Digest
    Status         DecisionStatus // advance, hold, reject, recommend-promotion
    PhaseResults   []PhaseResult
    EvidenceRefs   []ArtifactRef
    MeasurementIDs []MeasurementID
    ConstraintIDs  []ConstraintResultID
    DecidedAt      time.Time
    Actor          ActorID
    Digest         Digest
}
```

No policy should write to a production configuration directly.

### 21.3 Confidence-aware example

A promotion target may require:

\[
LCB_{1-\alpha}
\left(E[\Delta_{target}]\right)
> \delta_{min}
\]

and regressions may require:

\[
LCB_{1-\alpha}
\left(E[\Delta_j]\right)
> -\epsilon_j.
\]

For small early feedback suites, a policy may intentionally remain descriptive and require manual review. The policy must state which interpretation it uses.

### 21.4 Human review

Human review is another instrument and decision step, not a free-form note. The current RagOpt review package already supports structurally blinded queues. OptKit should generalize:

```go
type ReviewTask struct {
    ID            ReviewTaskID
    Subject       SubjectRef
    BindingPolicy ReviewBindingPolicy
    Payload       ArtifactRef
    BlindingKey   ArtifactRef // separately access-controlled
    Rubric        ArtifactRef
}
```

Review UIs must support document-bound views that do not follow ambient candidate selection when following it would unblind the reviewer. This matches the deliberate exception already present in the `rag-ttc` workbench.

### 21.5 Deployment record

OptKit can record that an external deployment happened, but deployment remains product-owned:

```go
type DeploymentRecord struct {
    Product       SystemID
    SnapshotID    SnapshotID
    DecisionID    DecisionID
    ApprovalIDs   []ApprovalID
    ExternalRef   string
    DeployedAt    time.Time
    RecordedBy    ActorID
}
```

---

## 22. Search and reflective optimization plugins

### 22.1 Start with simple optimizers

The first optimizers should be intentionally boring:

1. manual proposal import;
2. coordinate enumeration;
3. random sampling over bounded domains;
4. grid generation;
5. Pareto archive maintenance.

These exercise the architecture without adding uncertainty from a second LLM.

### 22.2 Manual optimizer

```go
type ManualOptimizer struct {
    Queue ProposalQueue
}

func (m *ManualOptimizer) Propose(ctx context.Context, req ProposalRequest) (ProposalBatch, error) {
    return m.Queue.TakeApproved(ctx, req.Campaign.ID, req.Budget.MaxCandidates)
}
```

This turns the current human loop into a first-class campaign without changing who proposes candidates.

### 22.3 Coordinate optimizer

```go
for _, variable := range searchSpace.OptimizableVariables() {
    for _, value := range variable.Domain().EnumerateOrSample() {
        if value == baseline.Value(variable.ID()) {
            continue
        }
        emit(Patch{Base: baseline.ID, Operations: []Operation{{Variable: variable.ID(), Value: value}}})
    }
}
```

A policy can select which coordinate to explore from failure diagnostics.

### 22.4 Reflective optimizer

A reflective optimizer should be decomposed into steps:

```text
select trajectories
      ↓
build bounded reflection packet
      ↓
reflector diagnoses failures and successes
      ↓
map diagnosis to allowed variables
      ↓
proposer emits typed patch operations
      ↓
static validation and policy checks
      ↓
human approval, optional
      ↓
materialize and evaluate
```

```go
type ReflectionPacket struct {
    CampaignSummary ArtifactRef
    CandidateDiffs  []ArtifactRef
    Trajectories    []RedactedTrajectoryRef
    Measurements    []MeasurementRef
    Constraints     []ConstraintResultRef
    Comparison      *ComparisonRef
    AllowedVariables []VariableDescription
    TokenBudget     int
}

type Reflection struct {
    Diagnosis       []Diagnosis
    ResponsibleVars []VariableID
    ProposedOps     []OperationProposal
    ExpectedEffects []ObjectiveExpectation
    Risks           []Risk
    EvidenceLinks   []EvidenceLink
}
```

The model must return structured variable IDs from the allowed registry. Free-form file edits are not accepted directly.

### 22.5 GEPA-like optimizer

A GEPA-style plugin can use the same substrate:

```text
1. choose a candidate from the current feasible archive
2. choose informative development trajectories
3. ask a reflector for high-level lessons
4. propose one or more typed prompt/module patches
5. run a small trial
6. update instance-level and objective-level Pareto archives
7. optionally merge complementary lineages
8. repeat until stop condition or budget
```

The core contributions OptKit must support are detailed trajectories, natural-language diagnostics, typed patches, candidate lineage, Pareto archives, and bounded adaptive planning. GEPA itself belongs in a plugin package, not the core.

### 22.6 MIPRO-like and TextGrad-like plugins

A MIPRO-like optimizer needs multi-module search, proposal generation, stochastic mini-batch evaluation, and a surrogate over program configurations. A TextGrad-like optimizer needs a computation graph connecting outputs and critiques to responsible variables. OptKit should make both possible without adopting their internal algorithms as universal semantics.

Optional interface:

```go
type ComputationGraphProvider interface {
    GraphFor(episode EpisodeID) (VariableDependencyGraph, error)
}
```

Coinvault might map:

```text
route prompt → tool selection
comparison intent → query transformation
reranker → evidence ordering
answer grounding prompt → final claims/citations
```

This graph is diagnostic metadata, not a proof of causality.

### 22.7 Optimizer state

Optimizer state should be an immutable artifact referenced by campaign events:

```text
optimizer.checkpointed
  optimizer_id
  input_history_sequence
  state_artifact
  state_digest
```

This makes resumption deterministic and keeps the campaign journal authoritative.

---

## 23. Campaign state machine

### 23.1 Why an explicit state machine?

Without one, each CLI command invents its own interpretation of “running,” “resumable,” “failed,” or “ready for promotion.” An event-sourced reducer needs a finite set of legal transitions.

### 23.2 Campaign states

```text
draft
  ↓ freeze plan
planned
  ↓ start
running ←→ paused
  ↓
awaiting-review
  ↓
completed

from running/paused:
  failed
  cancelled
```

A campaign may contain active and terminal trials while remaining globally running.

### 23.3 Candidate states

```text
proposed
  ↓ validate
valid
  ↓ materialize
materialized
  ↓ schedule
scheduled
  ↓ execute
measured
  ↓ selection
advanced | rejected | archived | finalist
  ↓ promotion
recommended | promoted
```

`archived` means retained but not currently scheduled, not deleted.

### 23.4 Trial states

```text
draft → scheduled → running → measuring → comparing → decided
                    ↘ failed / cancelled
```

### 23.5 Commands versus events

> **Definition — Command**
>
> A command requests a state transition and may be rejected.

> **Definition — Event**
>
> An event records a transition or fact that has already occurred.

```text
command: StartCampaign
validation: campaign is planned; plan digest matches
resulting event: campaign.started
```

The UI sends commands. It never writes state rows directly.

### 23.6 Reducer

```go
func Reduce(state State, event Event) (State, error) {
    switch event.Kind {
    case CampaignCreated:
        return applyCampaignCreated(state, event)
    case PlanFrozen:
        return applyPlanFrozen(state, event)
    case CandidateProposed:
        return applyCandidateProposed(state, event)
    // ...
    default:
        return State{}, ErrUnsupportedEvent
    }
}
```

Every event handler validates impossible histories. A `candidate.promoted` event before any promotion decision must fail replay.

### 23.7 Scheduler as policy interpreter

The runtime scheduler consumes campaign state and plan policies to emit commands such as `ScheduleTrial` or `RequestProposal`. It should not be hidden inside the reducer, because scheduling can involve I/O and time. The reducer remains pure.

```text
journal → reduce → current state
                    ↓
              scheduler decides
                    ↓ command
              command handler validates
                    ↓ event(s)
                 append journal
```

---

## 24. Event-sourced persistence

### 24.1 Motivation

The requested UIs need to answer three different questions:

- What is planned before execution?
- What is happening now?
- What happened, why, and what changed?

Building separate stores for these views guarantees drift. One journal plus rebuildable projections answers all three.

### 24.2 Control journal

```go
type Event struct {
    APIVersion string
    CampaignID CampaignID
    EventID    EventID
    Sequence   uint64
    PreviousDigest Digest
    OccurredAt time.Time

    Kind       EventKind
    Actor      ActorID
    CommandID  *CommandID
    IdempotencyKey *string

    CandidateID *CandidateID
    TrialID     *TrialID
    EpisodeID   *EpisodeID

    TraceID      *TraceID
    SpanID       *SpanID
    ParentEventID *EventID

    ArtifactRefs []ArtifactRef
    Payload      json.RawMessage
    Digest       Digest
}
```

The digest includes the previous digest, making the per-campaign journal tamper-evident.

### 24.3 Event catalog

The core event vocabulary should stay small and stable.

#### Campaign and plan

```text
campaign.created
plan.validated
plan.frozen
campaign.started
campaign.paused
campaign.resumed
campaign.cancel.requested
campaign.completed
campaign.failed
```

#### Candidate and archive

```text
proposal.requested
candidate.proposed
candidate.validation_failed
candidate.validated
snapshot.materialized
candidate.archived
archive.updated
candidate.rejected
candidate.advanced
candidate.finalist_selected
```

#### Trials and episodes

```text
trial.created
trial.scheduled
trial.started
episode.scheduled
episode.started
episode.trajectory_segment_committed
episode.completed
episode.failed
trial.execution_completed
```

#### Measurement and decision

```text
measurement.requested
measurement.produced
measurement.skipped
comparison.produced
selection.evaluated
promotion.review_requested
review.recorded
promotion.recommended
deployment.recorded
```

#### Resources and exposure

```text
resource.admitted
resource.consumed
resource.uncertain
budget.exhausted
data.exposed
```

### 24.4 Heavy artifacts do not belong inline

A full trajectory can contain thousands of events. The control journal should not become a multi-gigabyte payload stream. Use two layers:

```text
control journal
  small authoritative lifecycle facts
  references to immutable artifacts and trajectory segments

artifact/trajectory store
  native product traces
  compressed generic event segments
  prompts, snapshots, reports, diffs, judge assessments
```

A segment commit event proves which bytes are part of the episode:

```yaml
kind: episode.trajectory_segment_committed
episode_id: ep-17
payload:
  first_sequence: 1
  last_sequence: 250
  artifact: sha256:...
  event_count: 250
```

### 24.5 Projection store

A projection store is a cache that can be deleted and rebuilt from the journal and immutable artifacts.

```go
type Projector interface {
    Name() string
    Version() string
    Apply(ctx context.Context, tx ProjectionTx, event Event) error
}
```

Examples:

```text
campaign_overview_v1
plan_graph_v1
live_episode_table_v1
candidate_lineage_v1
measurement_series_v1
pareto_frontier_v1
promotion_ledger_v1
```

The projection version is part of its checkpoint identity.

---

## 25. Storage interfaces and initial implementations

### 25.1 Interfaces

```go
type Journal interface {
    Append(ctx context.Context, expectedSequence uint64, events ...Event) error
    Read(ctx context.Context, campaign CampaignID, after uint64, limit int) ([]Event, error)
    Head(ctx context.Context, campaign CampaignID) (JournalHead, error)
    Subscribe(ctx context.Context, campaign CampaignID, after uint64) (EventStream, error)
}

type ArtifactStore interface {
    Put(ctx context.Context, mediaType string, r io.Reader) (ArtifactRef, error)
    Open(ctx context.Context, ref ArtifactRef) (io.ReadCloser, error)
    Stat(ctx context.Context, ref ArtifactRef) (ArtifactStat, error)
}

type SnapshotStore interface {
    Put(ctx context.Context, snapshot Snapshot) error
    Get(ctx context.Context, id SnapshotID) (Snapshot, error)
}

type ProjectionStore interface {
    Transaction(ctx context.Context, fn func(ProjectionTx) error) error
    Checkpoint(ctx context.Context, projector string, campaign CampaignID) (uint64, error)
}
```

### 25.2 Initial local implementation

For development and single-host production, use:

```text
SQLite:
  journal events
  command idempotency
  projection tables
  campaign and access-control metadata

content-addressed filesystem:
  snapshots
  native artifacts
  trajectory segments
  reports and rendered diffs
```

This choice gives transactional sequence allocation and queryable read models while retaining inspectable immutable files.

### 25.3 Scalable implementation

Later:

```text
PostgreSQL:
  journal and projections

S3-compatible object storage:
  artifacts, snapshots, trajectory segments

message broker or database notifications:
  live subscriptions
```

The interfaces should make this change possible without changing campaign semantics.

### 25.4 Suggested local layout

```text
.optkit/
  optkit.db
  artifacts/
    sha256/ab/cd/<digest>
  campaigns/
    <campaign-id>/
      manifest.json
      plan.json
      journal-export.jsonl
      snapshots/
      candidates/
      trials/
      episodes/
        <episode-id>/
          trajectory.manifest.json
          native/
          summary.json
      measurements/
      comparisons/
      decisions/
      exports/
```

The database is the live journal implementation. `journal-export.jsonl` is a deterministic export, not an independently edited authority.

### 25.5 Compatibility file implementation

A file-backed journal may be useful for tests and small offline campaigns, but it must implement atomic append and sequence checks. The RagOpt run directory should be imported as events rather than used as the long-term campaign journal format.

### 25.6 Crash recovery

Recovery procedure:

```text
1. read journal head and verify digest chain
2. replay or load a verified projection checkpoint
3. identify nonterminal episodes/trials
4. inspect committed native artifacts and FlowKit cache entries
5. emit explicit recovery events
6. reschedule only assignments whose completion was not durably committed
```

No recovery path should infer completion solely from a temporary file's existence.

---

## 26. Plan schema

### 26.1 Top-level plan

```go
type Plan struct {
    APIVersion string
    ID         PlanID
    Campaign   CampaignSpec
    Baseline   SnapshotID
    SearchSpace SearchSpaceSpec
    Data       []DatasetBinding
    Phases     []Phase
    Resources  ResourcePlan
    Access     AccessPolicy
    Stop       StopPolicy
    Digest     Digest
}
```

### 26.2 Phase kinds

```text
verify-baseline
proposal
trial
adaptive-loop
selection
hidden-evaluation
human-review
promotion
monitoring
```

### 26.3 Adaptive phase

```go
type AdaptiveLoop struct {
    Optimizer        OptimizerRef
    MaxRounds        int
    MaxCandidatesPerRound int
    TrialTemplate    TrialTemplate
    ArchivePolicy    ArchivePolicy
    StopConditions   []StopCondition
    Next             PhaseID
}
```

### 26.4 Plan bounds

The planner should calculate conservative bounds:

\[
N_{episodes}^{max}
= \sum_{phases}
N_{candidates}^{max}
\cdot N_{cases}
\cdot N_{repeats}
\cdot N_{arms}.
\]

Resource bounds then derive from product-declared per-episode ceilings.

### 26.5 Example Coinvault plan

```yaml
api_version: optkit.plan/v1
campaign:
  id: coinvault-grounding-followup
  system: coinvault-admin-chat
baseline: snapshot:sha256:...

search_space:
  variables:
    answer.grounding_prompt:
      mode: optimize
      constraint: exactly-one-change
    answer.model:
      mode: locked
    authorization.policy:
      mode: forbidden

data:
  - dataset: coinvault-feedback-12
    role: development
  - dataset: coinvault-validation-v3
    role: promotion
    access: escrowed

phases:
  - id: preflight
    kind: verify-baseline
  - id: feedback
    kind: trial
    design: paired-two-arm
    dataset: coinvault-feedback-12
    repeats: 1
    measurements: coinvault-answer-suite-v1
    selection: coinvault-grounded-answer-gate-v2
  - id: reproduce
    kind: trial
    when: feedback.advance
    fresh_materialization: true
  - id: hidden
    kind: hidden-evaluation
    when: reproduce.advance
    dataset: coinvault-validation-v3
  - id: review
    kind: human-review
    blinded: true
  - id: recommend
    kind: promotion

resources:
  answer-provider-calls: {ceiling: 216}
  embedding-calls: {ceiling: 192}
  judge-provider-calls: {ceiling: 72}
  answer-provider-tokens: {ceiling: 1000000}
```

---

## 27. Command, query, and event APIs

### 27.1 Three API categories

```text
commands: request state changes
queries: read projections or immutable artifacts
event streams: observe append-only changes from a cursor
```

These should remain separate in both Go interfaces and HTTP transport.

### 27.2 Command service

```go
type CommandService interface {
    CreateCampaign(ctx context.Context, cmd CreateCampaign) (CommandResult, error)
    FreezePlan(ctx context.Context, cmd FreezePlan) (CommandResult, error)
    StartCampaign(ctx context.Context, cmd StartCampaign) (CommandResult, error)
    PauseCampaign(ctx context.Context, cmd PauseCampaign) (CommandResult, error)
    ResumeCampaign(ctx context.Context, cmd ResumeCampaign) (CommandResult, error)
    CancelCampaign(ctx context.Context, cmd CancelCampaign) (CommandResult, error)
    SubmitProposal(ctx context.Context, cmd SubmitProposal) (CommandResult, error)
    RecordReview(ctx context.Context, cmd RecordReview) (CommandResult, error)
}
```

Every command includes:

```go
type CommandHeader struct {
    CommandID      CommandID
    CampaignID     CampaignID
    Actor          ActorID
    ExpectedSeq    *uint64
    IdempotencyKey string
}
```

### 27.3 Query service

```go
type QueryService interface {
    CampaignOverview(ctx context.Context, id CampaignID) (CampaignOverview, error)
    PlanGraph(ctx context.Context, id CampaignID) (PlanGraph, error)
    CandidateLineage(ctx context.Context, id CampaignID) (CandidateGraph, error)
    LiveEpisodes(ctx context.Context, q LiveEpisodeQuery) (Page[EpisodeRow], error)
    EpisodeTimeline(ctx context.Context, id EpisodeID) (EpisodeTimeline, error)
    TrialComparison(ctx context.Context, id TrialID) (TrialComparisonView, error)
    Measurements(ctx context.Context, q MeasurementQuery) (Page[MeasurementView], error)
    PromotionLedger(ctx context.Context, id CampaignID) (PromotionLedger, error)
}
```

### 27.4 Event subscription

```text
GET /api/campaigns/{id}/events?after=812
Accept: text/event-stream
```

or WebSocket when bidirectional control is useful. Every message carries journal sequence. Reconnect resumes from the last acknowledged sequence.

### 27.5 CLI

```text
optkit plan validate plan.yaml
optkit plan render plan.yaml --format ascii
optkit campaign create --plan plan.yaml
optkit campaign start <id>
optkit campaign pause <id>
optkit campaign resume <id>
optkit campaign status <id>
optkit candidate submit <campaign> patch.yaml
optkit inspect candidate <id>
optkit inspect episode <id>
optkit compare trial <id>
optkit replay <campaign> --verify
optkit projections rebuild <campaign>
optkit import ragopt-run <path>
optkit import ragopt-candidate <path>
optkit doctor <campaign>
optkit serve --store .optkit
```

The CLI should call the same command/query services as the web server. It must not contain separate campaign logic.

---
EOF

```

<details><summary>💭 Thinking</summary>

**Drafted and appended the Part III OptKit architecture migration guide**

</details>

```unknown
bash -lc cat >> /mnt/data/optkit-architecture-and-migration-guide.md <<'EOF'

# Part IV — Visualization and operator interfaces

## 28. One journal, three temporal views

### 28.1 Motivation

The user requirement is not merely “show results.” Operators need to understand:

1. **before execution:** what is planned, what may adapt, what data and budgets are involved;
2. **during execution:** what is happening, what is blocked, what has failed, and what the optimizer is learning;
3. **after execution:** what changed, why it changed, which evidence supported it, and what was promoted.

These are three projections of the same campaign history, not three separate products.

### 28.2 Temporal projection model

```text
                        append-only campaign journal
                                     |
                    +----------------+----------------+
                    |                |                |
                    v                v                v
              plan projection   live projection  history projection
              known/adaptive    active spans,    lineage, trials,
              phases, bounds,   budgets, events  decisions, deployments
              data policy
```

The UI must never recompute authoritative identity or gate decisions in the browser. It renders server projections and follows artifact references.

### 28.3 Plan view

The plan view answers:

- What baseline is being optimized?
- Which variables are mutable, locked, or forbidden?
- Which phases are fixed and which are adaptive?
- How many candidates and episodes can be created?
- Which datasets are development, hidden, or shadow?
- Which judge protocols and calibration reports are frozen?
- What are the worst-case provider calls, tokens, and estimated cost?
- What stopping conditions exist?
- Where is human approval required?

### 28.4 Live view

The live view answers:

- Which phase and round are active?
- Which candidates are running?
- Which episodes are waiting, active, measuring, failed, or complete?
- Which model/tool/retrieval span is active in a selected episode?
- Is the treatment being exercised?
- What resources have been admitted and consumed?
- What new measurements and critiques have appeared?
- What is the current Pareto archive?
- Why did the optimizer request the most recent candidate?

### 28.5 History view

The history view answers:

- Which candidate lineage produced the deployed snapshot?
- What did each patch change?
- Which cases improved or regressed?
- Which measurement protocol produced each conclusion?
- Which hidden datasets were exposed and when?
- Why was each candidate rejected or advanced?
- Which component improvements were historically supported but not promoted as whole candidates?
- Which deployments descend from an evaluator epoch later found unreliable?

---

## 29. Reuse the `rag-ttc` workbench model

### 29.1 Existing pattern worth preserving

The `rag-ttc` admin web already has the right compositional UI model:

- a split tree of tiles;
- one shared `WorldProvider` selection;
- tiles that read shared selection rather than maintaining conflicting local copies;
- serializable verbs routed through one sink;
- a tile registry;
- document-bound tiles as an explicit escape hatch for blinded review;
- a verb trace that records user decisions.

OptKit should generalize this pattern rather than create a separate dashboard framework.

### 29.2 Optimization-world selection

```ts
export interface OptimizationSelection {
  campaignId?: string;
  phaseId?: string;
  roundId?: string;
  candidateId?: string;
  patchId?: string;
  snapshotId?: string;
  trialId?: string;
  episodeId?: string;
  caseId?: string;
  eventId?: string;
  measurementId?: string;
  constructId?: string;
  artifactDigest?: string;
  deploymentId?: string;
}
```

Selection invalidation rules matter. For example:

```text
focus another candidate
  clears trial, episode, event, and measurement selection
  preserves campaign and phase

focus another episode
  clears event and measurement selection
  preserves candidate and trial

focus a measurement
  may set construct ID and episode ID
```

These rules should have reducer tests like the current `WorldProvider` tests.

### 29.3 Serializable verbs

```ts
export type OptimizationVerb =
  | { kind: "focusCampaign"; campaignId: string }
  | { kind: "focusCandidate"; campaignId: string; candidateId: string }
  | { kind: "focusTrial"; trialId: string }
  | { kind: "focusEpisode"; episodeId: string }
  | { kind: "focusMeasurement"; measurementId: string }
  | { kind: "showPatchDiff"; patchId: string }
  | { kind: "showArtifact"; digest: string }
  | { kind: "showWhyRejected"; decisionId: string }
  | { kind: "showInLineage"; candidateId: string }
  | { kind: "compareCandidates"; left: string; right: string }
  | { kind: "pauseCampaign"; campaignId: string }
  | { kind: "resumeCampaign"; campaignId: string }
  | { kind: "cancelCampaign"; campaignId: string }
  | { kind: "recordReview"; taskId: string; payload: ReviewPayload };
```

Read-only navigation verbs update local selection. Mutating verbs call command endpoints and are traced with resulting command/event IDs.

### 29.4 Ambient versus bound tiles

Most tiles follow ambient selection. Some must be bound:

```text
ambient tile:
  follows whichever candidate/episode the operator selects

bound tile:
  pinned to a specific review task, candidate, protocol, or hidden payload
```

Blinded review tiles should be bound and should not write candidate identity into ambient selection. This prevents accidental unblinding through neighboring lineage or metric tiles.

---

## 30. UI projection contracts

### 30.1 Why explicit read models?

A UI that reads raw journal payloads or arbitrary tables becomes coupled to every internal schema. Projection contracts let backend and UI evolve independently and let TUI and web clients share semantics.

### 30.2 Campaign overview

```ts
export interface CampaignOverview {
  campaign: {
    id: string;
    name: string;
    systemId: string;
    status: CampaignStatus;
    planDigest: string;
    baselineSnapshotId: string;
    journalSequence: number;
  };
  currentPhase?: PhaseSummary;
  progress: {
    candidates: CountByStatus;
    trials: CountByStatus;
    episodes: CountByStatus;
    measurements: number;
  };
  resources: ResourceSummary[];
  alerts: AlertSummary[];
  latestEvents: EventSummary[];
}
```

### 30.3 Plan graph

```ts
export interface PlanNodeView {
  id: string;
  kind: string;
  title: string;
  status: "future" | "available" | "active" | "passed" | "failed" | "skipped";
  adaptive: boolean;
  lowerBoundEpisodes: number;
  upperBoundEpisodes?: number;
  resourceBounds: ResourceBound[];
  datasetRoles: DatasetRoleView[];
  policyRefs: ReferenceView[];
}
```

### 30.4 Candidate lineage

```ts
export interface CandidateNodeView {
  candidateId: string;
  snapshotId?: string;
  parentSnapshotId: string;
  patchId: string;
  status: CandidateStatus;
  proposer: ProposerView;
  hypothesis: string;
  changedVariables: VariableDiffSummary[];
  objectiveSummary: ObjectiveSummary[];
  constraintSummary: ConstraintSummary;
  decision?: DecisionSummary;
}
```

### 30.5 Episode timeline

```ts
export interface EpisodeTimeline {
  episode: EpisodeSummary;
  spans: SpanView[];
  events: EventView[];
  intervention: InterventionView[];
  constraints: ConstraintResultView[];
  measurements: MeasurementView[];
  nativeArtifacts: ArtifactLink[];
}
```

### 30.6 Measurement series

```ts
export interface MeasurementSeries {
  constructId: string;
  contractDigest: string;
  protocolDigest: string;
  epochLabel: string;
  points: MeasurementPoint[];
  compatibilityWarnings: CompatibilityWarning[];
}
```

The API should never merge points across protocol digests merely because the construct ID matches.

### 30.7 Pair comparison

```ts
export interface PairComparisonView {
  caseId: string;
  repeat: number;
  left: EpisodeSummary;
  right: EpisodeSummary;
  measurementDeltas: MeasurementDeltaView[];
  constraintDifferences: ConstraintDifferenceView[];
  costDeltas: ResourceDeltaView[];
  trajectoryDiff: TrajectoryDiffSummary;
}
```

---

## 31. Tile catalog

The first UI should be built from small inspectable tiles rather than one monolithic page.

| Tile | Purpose | Follows selection? |
|---|---|---|
| Campaign List | find campaigns and statuses | no / root navigation |
| Campaign Header | identity, status, current phase, alerts | campaign |
| Plan Graph | fixed and adaptive phases, bounds, policies | campaign |
| Candidate Lineage | parent/patch/child graph | campaign/candidate |
| Candidate Inspector | hypothesis, variables, risks, artifacts | candidate |
| Patch Diff | domain-aware value changes | patch |
| Trial Matrix | cases × arms × repeats with statuses | trial |
| Live Episodes | queue/running/measuring/failed rows | campaign/trial |
| Episode Timeline | spans and events | episode |
| Tool & Retrieval Trace | model/tool/retrieval details | episode |
| Evidence Ledger | admitted/cited evidence | episode |
| Widget Inspector | intent, rendered artifact, validation | episode |
| Intervention Checks | treatment applied/exercised evidence | episode/candidate |
| Constraint Results | deterministic and hard checks | episode/trial/candidate |
| Measurements | values, protocol, uncertainty, evidence | selected subject |
| Pair Comparator | synchronized two-episode comparison | pair or two candidates |
| Aggregate Comparison | group means, wins/losses, intervals | trial |
| Pareto Frontier | non-dominated candidate views | campaign/phase |
| Budget Meter | admitted, consumed, uncertain, remaining | campaign/phase |
| Dataset Exposure | who saw what and when | campaign |
| Judge Protocol | construct/contract/protocol/calibration | measurement |
| Critique/Reflection | selected evidence and proposed lessons | proposal round |
| Gate Decision | phase-ordered checks and first failure | decision |
| Review Queue | blinded human review | bound to review task |
| Promotion Ledger | decisions, approvals, deployment records | campaign |
| Artifact Browser | immutable source files and digests | artifact |
| Event Trace | raw control journal entries | campaign/subject |

Existing TTC components such as `FunnelPanel`, `HitsTable`, `EvidenceList`, and `DocumentView` can remain product-specific episode-detail tiles registered in the same shell.

---

## 32. ASCII screen: campaign plan before execution

```text
┌─ OptKit · Plan · coinvault-grounding-followup ───────────────────────────────┐
│ status: PLANNED   baseline: cv-prod-v12 / sha256:8e2a…   plan: sha256:31bc… │
│ system: coinvault-admin-chat            created by: alice                   │
├──────────────────────────────────────────────────────────────────────────────┤
│ SEARCH SPACE                                                                  │
│  optimize  answer.grounding_prompt      1 approved artifact set             │
│  locked    answer.model                 default/gpt-5.6-luna-low            │
│  locked    knowledge.comparison_intent  sha256:54f1…                         │
│  forbidden authorization.policy                                                │
├──────────────────────────────────────────────────────────────────────────────┤
│ PLAN                                                                          │
│                                                                              │
│  [1] Baseline verification                                                    │
│       12 cases × 1 repeat × 1 arm                           ≤ 12 episodes     │
│       │ PASS →                                                               │
│       v                                                                      │
│  [2] Paired feedback trial                                                    │
│       incumbent + challenger · feedback-12                  ≤ 24 episodes     │
│       │ ADVANCE →                                                            │
│       v                                                                      │
│  [3] Fresh-root reproduction                                                  │
│       independent materialization                           ≤ 24 episodes     │
│       │ ADVANCE →                                                            │
│       v                                                                      │
│  [4] Hidden promotion evaluation  🔒                                          │
│       dataset: coinvault-validation-v3 · optimizer access: NONE              │
│       │ PASS →                                                               │
│       v                                                                      │
│  [5] Blinded human review                                                     │
│       │ APPROVE →                                                            │
│       v                                                                      │
│  [6] Promotion recommendation (never auto-deploys)                            │
├──────────────────────────────────────────────────────────────────────────────┤
│ RESOURCE CEILINGS                                                            │
│ answer calls       0 / 216   embeddings 0 / 192   judge calls 0 / 72        │
│ provider tokens    0 / 1,000,000     worst-case planned episodes: 60         │
├──────────────────────────────────────────────────────────────────────────────┤
│ [v] validate  [s] start  [d] inspect digests  [e] exposure policy            │
└──────────────────────────────────────────────────────────────────────────────┘
```

The UI must visually distinguish exact work from upper bounds. An adaptive phase should display `≤`, a range, or an explicit policy rather than pretending future candidates already exist.

---

## 33. ASCII screen: live campaign

```text
┌─ OptKit · LIVE · cv-routing-and-grounding-search ─────────────────────────────┐
│ RUNNING · phase adaptive-search · round 3/6 · journal seq 8,214              │
│ budget $18.42 / $50.00 · answer calls 87/216 · judge calls 31/72             │
├───────────────┬───────────────────────────────────────┬───────────────────────┤
│ CANDIDATES    │ ACTIVE EPISODES                       │ EVENT STREAM          │
│               │                                       │                       │
│ ● C17 frontier│ ep-441 C17 case compare-morgan        │ #8214 evidence.admit  │
│   +grounding  │   model m2 ███████░  8.4s             │ #8213 retrieval.done  │
│   F +0.18     │   tool: none                          │ #8212 tool.call.done  │
│   R +0.02     │                                       │ #8211 limit.resolved  │
│               │ ep-442 C18 case schema-route          │ #8210 tool.call.start │
│ ● C18 testing │   knowledge_search ████░  3.1s        │ #8209 model.call.done │
│   +routing    │   effective results: 8 (forced)       │                       │
│               │                                       │                       │
│ ○ C19 queued  │ ep-443 C18 case protected-ambiguous   │ ALERT                 │
│   +tool desc  │   measuring: deterministic contracts │ candidate C16 rejected│
│               │                                       │ route constraint fail │
├───────────────┴───────────────────────────────────────┴───────────────────────┤
│ SELECTED: ep-442 / C18 / feedback-schema-route                               │
│                                                                              │
│ model m1 ──tool call──> knowledge_search ──retrieval──> evidence ──model m2  │
│   2.3s                       3.1s             0.4s          active            │
│                                                                              │
│ intervention: routing prompt ACTIVE ✓    source-role policy ACTIVE ✓         │
│ hard checks: generation ✓ route … retrieval … contract …                    │
├──────────────────────────────────────────────────────────────────────────────┤
│ [enter] episode  [p] pause  [c] candidate  [b] budget  [a] archive           │
└──────────────────────────────────────────────────────────────────────────────┘
```

The live screen should not display a final candidate score before measurements are complete. Intermediate values must be visibly labeled provisional.

---

## 34. ASCII screen: candidate and paired evidence

```text
┌─ Candidate C17 · grounded-answer-v2-port ─────────────────────────────────────┐
│ parent: cv-prod-v12       child: sha256:72f61…       status: REJECTED         │
│ proposer: human/ragopt-gec-phase5-evidence-only-answer-v2-evaluator-v8       │
├──────────────────────────────────────────────────────────────────────────────┤
│ HYPOTHESIS                                                                   │
│ Direct clause-level entailment and adjacent citations will reduce           │
│ unsupported comparison claims without degrading relevance.                  │
├───────────────────────────────────┬──────────────────────────────────────────┤
│ PATCH                             │ DECISION                                 │
│ answer.grounding_prompt           │ identity      PASS                       │
│   sha256:01ba… → sha256:ee276…    │ hard          FAIL                       │
│                                   │ target        not evaluated for advance  │
│ [open text diff]                  │ regression    not evaluated for advance  │
│                                   │ cost          not evaluated              │
│                                   │ first failure: 5 invalid challenger cells│
├───────────────────────────────────┴──────────────────────────────────────────┤
│ TARGET PAIRS                                                                  │
│                                                                              │
│ case                              incumbent  challenger   delta F   delta R  │
│ compare-morgan-peace                 .4595       1.0000    +.5405     +.32   │
│ compare-gold-coins-bars              .3778        .9615    +.5837     +.23   │
│                                                                              │
│ Target behavior strongly improved; whole candidate remained infeasible.     │
├──────────────────────────────────────────────────────────────────────────────┤
│ OTHER FAILURES                                                                │
│ schema-route          route.required_sql       FAIL  [compare trajectories]  │
│ protected-ambiguity   abstention.contract      FAIL  [open native artifact]  │
│ ...                                                                          │
├──────────────────────────────────────────────────────────────────────────────┤
│ Measurement epoch: faithfulness / contract 4c1… / protocol judge-v8 9a2…    │
│ [l] lineage  [t] pair timeline  [j] judge protocol  [e] evidence            │
└──────────────────────────────────────────────────────────────────────────────┘
```

This view preserves a subtle conclusion: the component intervention may be historically supported even though the complete candidate is rejected. That distinction should be representable in the archive as evidence, not left only in prose diaries.

---

## 35. ASCII screen: Pareto archive

```text
┌─ Pareto archive · adaptive-search round 4 ────────────────────────────────────┐
│ axes: faithfulness Δ ↑ · relevance Δ ↑ · provider calls Δ ↓                 │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ relevance Δ                                                                  │
│   +.20 |                  C21 ●                                               │
│   +.10 |       C17 ●                         C24 ●                            │
│    .00 | baseline ×       C18 ○ dominated                                    │
│   -.10 |                            C23 ●                                     │
│        +------------------------------------------------------------------   │
│          -.05       +.05       +.15       +.25       +.35 faithfulness Δ     │
│                                                                              │
│ Frontier                                                                    │
│ C17  grounding prompt     specialized comparison gains      cost +1.2%      │
│ C21  routing prompt       best route compliance             cost +4.0%      │
│ C23  concise answer       lowest token use                  F +.11           │
│ C24  merged C17+C21       testing; multi-variable policy exception          │
├──────────────────────────────────────────────────────────────────────────────┤
│ [enter] inspect  [m] merge proposal  [x] axis selector  [h] history          │
└──────────────────────────────────────────────────────────────────────────────┘
```

A plotted point should be visually marked infeasible, provisional, incompatible-epoch, or hidden-set evaluated. It must not look equivalent to a fully promotable candidate.

---

## 36. ASCII screen: historical deployment ledger

```text
┌─ Coinvault optimization lineage · deployed v13 ──────────────────────────────┐
│                                                                              │
│ deployed-v10                                                                │
│   │                                                                          │
│   ├─ default-results-8-v7 ── historical support ─┐                           │
│   ├─ comparison-intent-v3 ── promoted component ├─ canonical-seed-stack-v1  │
│   ├─ grounded-answer-v2 ──── supported/rejected ─┤            │              │
│   ├─ source-role-routing-v2 ─ promoted component ┘            │              │
│   │                                                           v              │
│   └─ qwen3-reranker-pool12-v1 ─ conditional evidence      deployed-v12      │
│                                                                  │           │
│                                               campaign CV-2026-08-20         │
│                                                                  │           │
│                                                          deployed-v13       │
├──────────────────────────────────────────────────────────────────────────────┤
│ Selected fact: grounded-answer-v2                                             │
│  target improvement: supported under judge protocol v8                       │
│  whole-candidate promotion: rejected due to independent route/retrieval fail │
│  descendant components: grounding clause retained in seed stack              │
│  protocol status: calibration report later superseded by v10                 │
│  action: [remeasure descendants under v10]                                   │
└──────────────────────────────────────────────────────────────────────────────┘
```

This is the view that turns years of optimization into understandable product provenance.

---

## 37. Pair and trajectory comparison

### 37.1 Motivation

Numeric deltas identify where results differ but not why. A useful pair comparator aligns both aggregate measurements and causal trajectory structure.

### 37.2 Alignment levels

```text
case and repeat
  ↓
major semantic stages
  route → retrieval → evidence → generation → render
  ↓
spans within each stage
  ↓
events and artifacts
```

### 37.3 Pair comparator layout

```text
┌─ Pair comparator · case ttc-y-005 · repeat 0 ────────────────────────────────┐
│ incumbent: snapshot A                          challenger: snapshot B          │
├────────────────────────────────┬─────────────────────────────────────────────┤
│ INCUMBENT                      │ CHALLENGER                                  │
│ model m1                       │ model m1                                    │
│  └─ search "Morgan dollar"    │  └─ search "Morgan dollar Peace dollar     │
│      5 hits                    │             composition dimensions"         │
│  └─ search "Peace dollar"     │      8 hits                                 │
│      5 hits                    │                                             │
│ model m2                       │ model m2                                    │
│ final answer                   │ final answer                                │
├────────────────────────────────┴─────────────────────────────────────────────┤
│ DIFF                                                                         │
│ search calls             2 → 1                                               │
│ admitted evidence        7 → 8                                               │
│ faithfulness          .92 → .94   +.02                                       │
│ relevance             .81 → .93   +.12                                       │
│ unsupported claims       1 → 0                                               │
│                                                                              │
│ [s] synchronized timeline  [e] evidence diff  [p] prompt diff                │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 37.4 Semantic diff adapters

Products may register diff providers:

```go
type TrajectoryDiffer interface {
    Diff(ctx context.Context, left, right trajectory.View) (TrajectoryDiff, error)
}
```

Coinvault can align knowledge calls, evidence ledger entries, and answer clauses. TTC can align retrieval hits, chunk fates, tool calls, and final citations.

The generic fallback aligns spans by kind and relative order.

---

## 38. Live streaming and backpressure

### 38.1 Snapshot plus delta

When a UI opens:

```text
1. query a projection snapshot at journal sequence N
2. subscribe to events after N
3. apply deltas or invalidate affected projections
4. reconnect from last acknowledged sequence
```

This avoids races between initial loading and live updates.

### 38.2 Event volume

Do not stream every token or large tool payload through the campaign control stream. High-volume trajectory events should be segmented. The live stream emits summaries and segment commits; a selected episode can subscribe to a dedicated trajectory feed.

### 38.3 Backpressure policy

```text
control events: never drop; resume by sequence
live usage samples: coalesce by resource and interval
span progress: keep latest state
raw token deltas: product-specific, optional, may be sampled
```

### 38.4 Provisional data

Every live projection field should carry a stability class:

```ts
type Stability = "terminal" | "provisional" | "estimated" | "unknown";
```

A partially computed mean must not look like a terminal trial result.

---

## 39. Access control, redaction, and blinding

### 39.1 Roles

Suggested control-plane roles:

| Role | Capabilities |
|---|---|
| viewer | read non-sensitive plans and aggregate results |
| operator | start, pause, resume, cancel campaigns |
| optimizer | read allowed development views and submit proposals |
| evaluator-admin | manage protocols and calibration evidence |
| reviewer | access assigned blinded review tasks |
| promoter | record promotion approval/rejection |
| auditor | read complete provenance and exposure logs |

### 39.2 Artifact access

Artifact references are not automatically readable. The API resolves them under policy:

```go
type ArtifactPolicy interface {
    Authorize(actor Actor, ref ArtifactRef, purpose Purpose) Decision
    Redact(ctx context.Context, ref ArtifactRef, policy RedactionPolicy) (ArtifactRef, error)
}
```

### 39.3 Hidden data

The plan UI may show:

```text
promotion dataset: 48 cases · digest sha256:... · escrowed
```

without exposing case IDs, inputs, trajectories, or detailed scores to the optimizer.

### 39.4 Blinded review

The review API should return opaque answer labels and a bound document:

```text
answer A
answer B
rubric
allowed evidence
```

Candidate IDs, arm labels, costs, and optimizer provenance stay in the separately protected blinding key until review is sealed.

### 39.5 Sensitive traces

Product adapters define redaction profiles:

```text
operator-summary
optimizer-development
reviewer-blinded
auditor-full
public-export
```

A reflection packet should contain only the profile authorized for the optimizer.

---

## 40. UI implementation strategy

### 40.1 Share contracts, not necessarily components

The first web implementation should live in the existing `rag-ttc/apps/admin/web` workbench because it already has the shell and interaction model. Coinvault can either consume the same projection API through its own admin surface or later extract stable UI packages.

Do not prematurely create a shared component package. First stabilize:

```text
projection DTOs
verb semantics
selection rules
tile contracts
artifact viewer contracts
```

When two products use identical contracts and visual behavior, extract the shared components.

### 40.2 Suggested front-end package layout

```text
apps/admin/web/src/optimization/
  model/
  api/
  world/
  verbs/
  registry/
  tiles/
    CampaignList/
    PlanGraph/
    CandidateLineage/
    CandidateInspector/
    TrialMatrix/
    LiveEpisodes/
    EpisodeTimeline/
    Measurements/
    PairComparator/
    ParetoFrontier/
    BudgetMeter/
    ExposureLedger/
    GateDecision/
    PromotionLedger/
  pages/
    OptimizationWorkbench/
  fixtures/
  stories/
```

### 40.3 Storybook-first tiles

Each tile should have fixtures for:

```text
empty
loading
partial/provisional
complete
failed
incompatible measurement epoch
access denied/redacted
large dataset
narrow viewport
```

### 40.4 TUI

A TUI can consume the same projections and commands. It should not parse filesystem layouts independently. The existing experiment browser can become a compatibility view backed by imported OptKit campaigns.

### 40.5 Accessibility and legibility

- Never encode pass/fail or arm identity only by color.
- Mark provisional values textually.
- Keep digests copyable and truncation reversible.
- Make keyboard navigation complete.
- Show why a control is disabled.
- Preserve a human-readable event and verb trace.
- Render large prompt/artifact diffs with line anchors.

---
EOF

```

```unknown
bash -lc cat >> /mnt/data/optkit-architecture-and-migration-guide.md <<'EOF'

# Part V — Porting Coinvault to OptKit

## 41. Migration principle: preserve the canonical runtime

The Coinvault port must not replace its evaluation path with a simplified local runner. The current evaluator deliberately submits through the canonical HTTP/WebSocket/Sessionstream path and observes the same projection consumed by the product. That behavior is one of the main reasons its evidence is trustworthy.

The migration changes orchestration and representation around the runtime:

```text
BEFORE
knowledge ragopt command
  owns candidate loading, preflight, budget, arm execution,
  trace projection, treatment switch, contracts, judge, gate, reports

AFTER
coinvault optimize command
  creates/starts OptKit campaign
       ↓
OptKit trial runtime
  schedules episodes and resources
       ↓
Coinvault adapter
  materializes snapshot
  executes canonical chat path
  emits trajectory events
  checks intervention and product constraints
  builds JudgeKit instance
       ↓
OptKit
  persists, compares, selects, projects to UI
```

The product runtime remains authoritative throughout.

---

## 42. Current Coinvault path mapped to OptKit

| Current file or concept | Current job | OptKit destination |
|---|---|---|
| `knowledge_ragopt.go` command | loads everything, runs/resumes paired evaluation, persists gate | thin product CLI + OptKit campaign plan/runner |
| `gecRagoptCellExecutor` | executes one arm/case | `coinvault/internal/optimization.Executor` implementing OptKit `Executor` |
| `gecRagoptArm` | labels incumbent/challenger | trial assignments and arm roles |
| `knowledge_ragopt_trace.go` | projects canonical events into product trace | Coinvault trajectory adapter + native artifact builder |
| `knowledge_ragopt_treatment.go` | treatment contract, mechanism validation, applicability | variable registry + per-variable intervention checkers |
| treatment mechanism switch in executor | applies prompts, plans, rerankers, limits | per-variable materializers composed into snapshot materializer |
| `knowledge_ragopt_contract.go` | generation/route/retrieval/contract checks | Coinvault `ConstraintSuite` adapter |
| `knowledge.JudgeAnswer` | claim/relevance/abstention judging | JudgeKit instrument adapter, initially wrapped for parity |
| RagOpt `Outcome.Metrics` projection | comparison values | typed OptKit measurements + legacy projection |
| `knowledge_ragopt_gate.go` | comparison/gate/report terminal artifacts | OptKit selector and promotion projections |
| hardcoded command budgets | run resource ceilings | plan resource policy with product maximum validation |
| `configs/ragopt/*` | candidate bundles | imported snapshots/patches/campaign templates; retain archive |
| source/suite lock validation | reproducibility and held-out safety | plan validation, dataset identity, resolver, exposure policy |

---

## 43. Target Coinvault optimization package

Suggested product layout:

```text
coinvault/internal/optimization/
  system.go                SystemAdapter composition root
  registry.go              variable registry
  snapshot.go              snapshot builder and product dimensions
  materialize.go           canonical runtime materializer
  executor.go              episode executor using evalchat canonical driver
  trajectory.go            LocalChatEvent → OptKit trajectory events
  artifacts.go             native artifact writer and redaction profiles
  cases.go                 case codec and dataset loader
  interventions/
    default_results.go
    forced_results.go
    comparison_plan.go
    comparison_intent.go
    prompt_suffix.go
    reranker.go
    tool_description.go
  constraints/
    generation.go
    route.go
    retrieval.go
    answer_contract.go
    protected_abstention.go
  measurement/
    judgekit_instance.go
    legacy_judge_adapter.go
    objective_catalog.go
  plans/
    compatibility.go
    defaults.go
  import/
    ragopt_candidate.go
    ragopt_run.go

coinvault/cmd/coinvault/cmds/optimization/
  plan.go
  run.go
  resume.go
  inspect.go
  serve.go
```

The existing `knowledge ragopt` command can delegate to the compatibility plan until callers migrate.

---

## 44. Coinvault system adapter

Avoid one large interface that every product must implement. Compose the adapter from focused pieces:

```go
type System struct {
    ID             optmodel.SystemID
    Registry       optspace.Registry
    SnapshotBuilder SnapshotBuilder
    Materializer   optruntime.Materializer
    Executor       optruntime.Executor
    Cases          optdata.Codec
    Constraints    optconstraint.Suite
    Measurements   optmeasure.Suite
    Differ         opttrajectory.Differ
}
```

Composition root:

```go
func NewCoinvaultOptimizationSystem(deps Dependencies) (*System, error) {
    registry := NewVariableRegistry(deps)
    constraints := NewConstraintSuite(deps)
    measurements := NewMeasurementSuite(deps)

    return &System{
        ID:              "coinvault-admin-chat",
        Registry:        registry,
        SnapshotBuilder: NewSnapshotBuilder(deps, registry),
        Materializer:    NewMaterializer(deps, registry),
        Executor:        NewExecutor(deps),
        Cases:           NewCaseCodec(),
        Constraints:     constraints,
        Measurements:    measurements,
        Differ:          NewTrajectoryDiffer(),
    }, nil
}
```

---

## 45. Replace the treatment switch with a variable registry

### 45.1 Current problem

Adding one Coinvault treatment currently requires coordinated edits across:

- YAML treatment schema/validation;
- executor mechanism branching;
- trace expectations;
- treatment observation logic;
- tests for semantic identity and applicability.

The implementation is explicit, but central branches become a scaling bottleneck and make independent plugin ownership difficult.

### 45.2 Registry shape

```go
type CoinvaultVariable struct {
    Definition   optspace.VariableDefinition
    Apply        func(context.Context, ApplyContext, optspace.Value) (AppliedEffect, error)
    Check        func(context.Context, CheckContext, AppliedEffect) (InterventionAssessment, error)
    Applicable   func(Case) bool
    Invariants   []Invariant
    Display      optspace.DiffRenderer
}
```

### 45.3 Initial registry

| Variable ID | Current mechanism | Domain | Intervention evidence |
|---|---|---|---|
| `knowledge.default_results` | `knowledge_tool_default_results` | bounded integer | configured/requested/effective limit and source |
| `knowledge.forced_results` | `knowledge_tool_forced_results` | bounded integer or disabled | server-owned force and effective limit |
| `knowledge.comparison_plan` | `knowledge_comparison_decomposition` | structured YAML artifact | expected query-transform ID and applied plan |
| `knowledge.comparison_intent` | `knowledge_comparison_intent` | structured artifact | expected intent ID and applied intent |
| `answer.grounding_prompt` | `answer_grounding_prompt` | text artifact | observed suffix digest |
| `answer.routing_prompt` | `answer_routing_prompt` | text artifact | observed routing suffix digest |
| `answer.policy_prompt` | `answer_policy_prompt` | text artifact | observed policy suffix digest |
| `knowledge.reranker` | `knowledge_reranker` | reranker config artifact | config identity, successful application, pool/result counts |
| `knowledge.tool_description` | `knowledge_tool_description` | text/structured artifact | tool description identity observed by runtime |

### 45.4 Compatibility aliasing

Old manifests refer to `answer_grounding_prompt`; new plans use `answer.grounding_prompt`. The importer owns a versioned alias map:

```go
var ragoptV1Aliases = map[string]optspace.VariableID{
    "answer_grounding_prompt":          "answer.grounding_prompt",
    "knowledge_tool_default_results":   "knowledge.default_results",
    "knowledge_tool_forced_results":    "knowledge.forced_results",
    "knowledge_comparison_decomposition": "knowledge.comparison_plan",
    // ...
}
```

Aliases are import rules, not permanent duplicate variables.

---

## 46. Coinvault snapshots

### 46.1 Snapshot builder

The builder resolves current production configuration into an immutable OptKit snapshot:

```go
type SnapshotBuilder interface {
    Capture(ctx context.Context, req CaptureRequest) (optsnapshot.Snapshot, error)
}
```

It should include:

```text
variables:
  all registry values, including locked values

dimensions:
  answer runtime identity
  judge protocol identity where frozen by plan
  bundle ID
  corpus digest
  lexical/vector index digests
  source roles
  access scopes
  query-transform and retrieval-policy versions
  evidence-ledger version
  Sessionstream/canonical driver revision
  tool-loop safety configuration
  product source revision

artifacts:
  prompt assets
  comparison plans
  runtime contract
  case suites
  source lock
```

### 46.2 Product and evaluation identity separation

The snapshot should identify the **system under test**. Judge protocol, suite, gate, and optimizer settings belong primarily to the trial or campaign plan, not the product candidate snapshot.

Current RagOpt snapshots lock evaluator and suite dimensions for reproducibility. The importer should preserve those facts, but new OptKit data should separate:

```text
system snapshot identity
trial/evaluation protocol identity
campaign search-policy identity
```

This allows the same product episode to be remeasured under a new judge without pretending the product snapshot changed.

### 46.3 Locked dimensions still matter

A plan binds resolved dimensions to the trial. If the corpus or model changes between materialization and execution, preflight fails. Separation does not mean weakening identity.

---

## 47. Coinvault materialization

### 47.1 Materialization pipeline

```text
base snapshot
  ↓ apply typed patch operations
candidate snapshot
  ↓ resolve artifacts
isolated workspace
  ↓ compose product settings
canonical effective runtime configuration
  ↓ validate source lock, bundle, auth, safety ceilings
materialization record
```

### 47.2 Prompt suffixes

Rather than branching by mechanism inside the episode executor:

```go
type PromptSuffixMaterializer struct {
    Variable  VariableID
    Slot      PromptSlot
}

func (m PromptSuffixMaterializer) Apply(ctx context.Context, ac ApplyContext, value Value) (AppliedEffect, error) {
    artifact := ac.Artifacts.MustOpen(value.Artifact)
    ac.RuntimePrompts.SetSuffix(m.Slot, artifact.Bytes())
    return AppliedEffect{
        Variable: m.Variable,
        Expected: map[string]Value{
            "prompt_slot": m.Slot,
            "suffix_digest": artifact.Digest,
        },
    }, nil
}
```

Grounding, routing, and policy prompts can share this implementation with different variable IDs and slots.

### 47.3 Result-depth variables

```go
type ResultDepthMaterializer struct {
    Mode "default" | "forced"
}
```

It updates `knowledge.ToolConfig` and records the expected semantics. The intervention checker later inspects actual knowledge-call events.

### 47.4 Reranker

The reranker materializer validates the structured config, resolves the model/profile identity, and injects the runtime adapter. It records both configured identity and expected call semantics.

### 47.5 Materialization artifact

```yaml
api_version: coinvault.materialization/v1
snapshot_id: sha256:...
adapter:
  source_revision: ...
  schema_version: v1
effective:
  answer_runtime: ...
  knowledge_config_digest: ...
  prompt_slots:
    grounding_suffix: sha256:...
  reranker: ...
validation:
  source_lock: pass
  authorization_policy: unchanged
  canonical_driver: pass
```

---

## 48. Coinvault trajectory adapter

### 48.1 Preserve the native event stream

`localwebchat.LocalChatEvent` and `evalchat.Event` are already normalized projections of the canonical Sessionstream runtime. The adapter should translate them into generic trajectory events while preserving the original payload as a native artifact reference.

```go
type TrajectoryAdapter struct {
    Sink opttrajectory.Sink
    NativeWriter NativeWriter
}

func (a *TrajectoryAdapter) Observe(event evalchat.Event) error {
    nativeRef, err := a.NativeWriter.Append(event)
    if err != nil { return err }

    for _, projected := range ProjectCoinvaultEvent(event, nativeRef) {
        if err := a.Sink.Emit(projected); err != nil { return err }
    }
    return nil
}
```

### 48.2 Event mapping

| Coinvault observation | Generic event | Product attributes |
|---|---|---|
| provider request start | `model.call.started` | provider, model, prompt/runtime IDs |
| provider completion | `model.call.completed` | usage, duration, finish class |
| tool call | `tool.call.started` | tool name, call ID, arguments artifact |
| tool result | `tool.call.completed` | success/error, result artifact |
| knowledge output | `retrieval.completed` | counts, policy IDs, reranker IDs |
| admitted evidence | `evidence.admitted` | citation, chunk/document, source role |
| visible answer | `message.emitted` | answer artifact, message ID |
| projection error | `error.observed` | class `projection` |
| terminal event | `episode.completed` | session/message/terminal status |

### 48.3 Do not flatten valuable fields

The current trace captures configured/default/forced/effective limits, query-transform ID, retrieval-policy ID, evidence-ledger ID, comparison intent, reranker application, source roles, omitted evidence, provider calls, and terminal state. Those fields should either become typed attributes or remain accessible through the native event reference.

### 48.4 Span construction

Use correlation IDs when present. Otherwise the adapter can maintain a per-episode map:

```text
provider call ID → model span
call ID → tool span
knowledge request ID → retrieval child span
```

The adapter must reject contradictory completions, matching current trace-collector tests.

### 48.5 Reasoning policy

Current tests explicitly ensure the trace collector omits reasoning. Preserve this policy. Emit observable decisions and summaries, not hidden reasoning text.

---

## 49. Coinvault intervention checkers

### 49.1 Common result

```go
type CoinvaultInterventionCheck struct {
    Name       string
    Expected   Value
    Observed   Value
    Passed     bool
    Applicable bool
    Evidence   []EventRef
}
```

### 49.2 Default results

```text
applicable when: case successfully invokes knowledge search
expected:
  configured default = candidate value
  no forced override unless locked identically
observed:
  requested limit
  effective limit
  effective limit source
status:
  exercised only when the candidate default determined effective behavior
```

### 49.3 Forced results

```text
exercised when:
  server-owned force is active
  effective limit equals forced value
  source reports forced/server policy
```

### 49.4 Prompt suffix

```text
exercised when:
  runtime prompt slot digest equals expected artifact digest
not-applicable:
  normally never; the answer runtime should always load the slot
indeterminate:
  runtime failed before prompt identity was observed
```

### 49.5 Comparison plan or intent

```text
applicable when:
  case declares comparison behavior
exercised when:
  expected plan/intent identity observed on eligible knowledge calls
```

### 49.6 Reranker

```text
applicable when:
  retrieval produced enough candidates and policy calls reranker
exercised when:
  expected config identity observed
  application succeeded
  pool and output counts satisfy configuration
```

### 49.7 Tool description

The runtime must emit the tool-description identity supplied to the model. Merely changing an asset on disk is insufficient.

---

## 50. Coinvault product constraints

### 50.1 Preserve current staged diagnosis

```text
generation
  terminal success, matching session/message, no unresolved provider/projection failure

route
  required tools used successfully, forbidden tools absent

retrieval
  required evidence groups admitted, source-role requirements met

contract
  citations resolve, evidence cited, protected abstention behavior, other answer rules
```

### 50.2 Proposed suite

```go
func NewCoinvaultConstraintSuite() optconstraint.Suite {
    return optconstraint.NewSuite(
        GenerationComplete{},
        RequiredRoute{},
        ForbiddenRoute{},
        RequiredEvidenceGroups{},
        SourceRolePolicy{},
        CitationsResolvable{},
        EvidenceCited{},
        ProtectedAbstention{},
    )
}
```

Each constraint produces its own result. A derived `FirstFailure` preserves current precedence for compatibility and concise reporting.

### 50.3 Failure class projection

Current generic failure classes can be preserved as a derived summary:

```go
func LegacyFailure(results []ConstraintResult, execution EpisodeResult) *ragopteval.Failure
```

Authoritative evidence remains the individual results and native artifact.

---

## 51. Coinvault measurements and JudgeKit

### 51.1 Parity-first adapter

Do not rewrite the judge and the campaign runtime simultaneously. First wrap current `knowledge.JudgeAnswer` as an OptKit instrument:

```go
type LegacyAnswerJudgeInstrument struct {
    Runtime *judgeGeneratorRuntime
}

func (j *LegacyAnswerJudgeInstrument) Measure(...) ([]Measurement, error) {
    score := knowledge.JudgeAnswer(...)
    return ProjectLegacyJudgeScore(score, protocolIdentity), nil
}
```

The adapter must synthesize a complete protocol identity from existing model, prompt, parser, and version fields.

### 51.2 JudgeKit-native migration

Once parity fixtures pass:

```text
Coinvault trace → JudgeKit eval.Instance
  question artifact
  final answer artifact
  knowledge and SQL EvidenceSet
  required facts
  product metadata

JudgeKit Suite
  claim extraction/support
  answer relevance
  abstention/answerability
  optional citation or style instruments

JudgeKit reports → OptKit measurements
```

### 51.3 Evidence adapter

Do not reduce knowledge evidence to `map[string]string`. Preserve:

```text
evidence ID
kind: knowledge or SQL
source role
chunk/document identity
content digest
retrieval/admission provenance
citation label
authorization status as a product assertion
```

### 51.4 Measurement names

Suggested construct IDs:

```text
answer.faithfulness
answer.relevance
answer.unsupported_claim_rate
answer.abstention_correctness
citation.resolution_rate
citation.evidence_coverage
retrieval.required_group_satisfaction
route.knowledge_used
route.sql_used
```

Deterministic route and citation facts can be measurements while corresponding policy requirements remain constraints.

### 51.5 Protocol migration rule

Every existing evaluator version becomes an explicit protocol digest. Do not compare old and new judge values directly without remeasurement or a bridge.

---

## 52. Worked port: `grounded-answer-v2`

### 52.1 Current bundle

The current bundle contains:

```text
candidate manifest
parent and child snapshots
one changed answer-grounding prompt asset
locked feedback/validation suites
comparison plans
runtime/source/treatment contracts
gate policy
resolved dimensions
```

### 52.2 Imported OptKit objects

```text
Snapshot P
  variables.answer.grounding_prompt = sha256:01ba...
  product dimensions = existing snapshot dimensions

Patch D
  base = P
  set answer.grounding_prompt = sha256:ee276...
  support size = 1
  hypothesis and risks copied from manifest

Snapshot C
  generated by applying D to P

Candidate K
  parent=P, patch=D, child=C
  proposer=human/ragopt-gec-phase5-...
```

Evaluation-specific locked assets become:

```text
Dataset feedback-12
Dataset validation-closed
ConstraintSuite coinvault-answer-contract-v1
MeasurementSuite evaluator-v8
SelectionPolicy grounded-answer-v2
```

### 52.3 Campaign plan

```text
phase 1: import/verify candidate
phase 2: paired feedback trial
phase 3: compatibility selection policy
phase 4: terminal historical result
```

Because this is historical import, no optimizer proposal is generated.

### 52.4 Episode flow

```text
assignment created
  ↓
episode.started
  ↓
Coinvault executor streams canonical trajectory
  ↓
intervention: prompt suffix digest observed
  ↓
constraints evaluated
  ↓ if valid
legacy/JudgeKit instrument produces faithfulness/relevance
  ↓
episode.completed
```

### 52.5 Comparison and decision

The two target cases produce strong faithfulness improvements, but hard constraints fail on other cases. The imported decision remains rejected. OptKit can additionally create a `ComponentEvidence` record:

```go
type ComponentEvidence struct {
    Variable     VariableID
    Value        ValueRef
    Claim        string
    SupportLevel EvidenceLevel // supported, conditional, contradicted, unknown
    TrialRefs    []TrialID
    DecisionRefs []DecisionID
}
```

This captures “the grounding component helped its target but the whole candidate was infeasible.”

---

## 53. Worked port: default-results candidate

### 53.1 Patch

```yaml
operations:
  - variable: knowledge.default_results
    kind: set
    value: 8
```

### 53.2 Static validity

```text
8 is in domain
8 ≤ maximum result limit
forced result value remains locked
only one variable changed
```

### 53.3 Runtime outcomes

Case A:

```text
model calls knowledge_search without explicit limit
effective=8, source=default
intervention=exercised
```

Case B:

```text
model calls knowledge_search(limit=5)
effective=5, source=request
intervention=not-exercised
```

Case C:

```text
case does not require knowledge search
intervention=not-applicable
```

The trial report separates all three. It must not count B as evidence that depth 8 failed to improve retrieval.

---

## 54. Coinvault campaign stages and hidden validation

### 54.1 Current protocol

The broader Coinvault process already distinguishes feedback, fresh-root reproduction, held-out validation, and human promotion, but the current command only executes the feedback split.

### 54.2 OptKit encoding

```text
feedback:
  optimizer-visible
  rich diagnostics
  candidate may be revised afterward

reproduction:
  fresh materialization from frozen snapshot
  no new proposal between first pass and reproduction

promotion:
  escrowed dataset
  optimizer cannot view cases or detailed feedback
  evaluation service returns only policy-authorized result

review:
  blinded and bound

promotion recommendation:
  manual authority
```

### 54.3 Fresh root

A fresh-root phase should require a new materialization ID and workspace, while retaining the same snapshot ID. This tests whether success depended on accidental local state.

### 54.4 Exposure event after hidden failure

If a promoter releases detailed hidden failures for a follow-up campaign:

```text
data.exposed
  actor=optimizer:gepa-v1
  dataset=coinvault-validation-v3
  kind=critique
  cases=[...]
```

The next campaign must use a new promotion set or explicitly downgrade the old set's role.

---

## 55. Coinvault UI integration

### 55.1 Control event transport

The simplest first integration is a separate OptKit HTTP/SSE or WebSocket service. Coinvault's Sessionstream remains the runtime trace source; the OptKit adapter consumes it and publishes campaign events.

Later, selected campaign events may also be projected into an existing admin event bus, but the campaign journal remains authoritative.

### 55.2 Product-specific tiles

Coinvault should register:

```text
Knowledge Call Inspector
  query, comparison intent, limits, identities, reranker, returned/admitted items

Authorization & Source Role
  filters and allowed evidence classes

Answer Contract
  staged checks and first failure

Citation/Evidence Ledger
  answer clauses, citations, admitted evidence

Canonical Session Link
  open the exact product session/message
```

### 55.3 Plan UI

Coinvault's plan panel should surface locked proof budgets and validation closure prominently. An operator should not be able to start a plan whose values differ from product-enforced ceilings.

### 55.4 Historical component ledger

The existing historical component-evidence ledger can be imported into a lineage/component-evidence projection. This is useful because Coinvault has several historically supported components that did not individually correspond to promoted whole candidates.

---

## 56. Coinvault migration phases

### Phase C0 — Characterization and schema inventory

**Work**

- Freeze golden fixtures for representative candidate bundles: result depth, prompt suffix, comparison intent, reranker, tool description.
- Freeze native artifacts and generic outcomes from fake-inference canonical runs.
- Record current failure precedence, budget behavior, source-lock checks, and terminal gate documents.
- Enumerate every current treatment mechanism and its tests.

**Exit criteria**

- A test suite can detect any behavioral change in current candidate loading, canonical event projection, treatment checks, answer contracts, judge projection, and gate output.

### Phase C1 — OptKit compatibility import

**Work**

- Implement RagOpt v1 candidate and run importers.
- Import `grounded-answer-v2` and one result-depth candidate into an OptKit fixture campaign.
- Verify snapshot, patch, assignment, episode, comparison, and decision identities.

**Exit criteria**

- The imported campaign renders the same target deltas, failures, and final decision as the original artifacts.

### Phase C2 — Product system adapter and manual campaign

**Work**

- Add `coinvault/internal/optimization` composition root.
- Wrap current cell executor behind OptKit `Executor`.
- Wrap current judge behind OptKit `Instrument`.
- Run one manually proposed paired campaign through OptKit while retaining current treatment switch.

**Exit criteria**

- Native product output and old RagOpt comparison projection match within exact/golden expectations.

### Phase C3 — Trajectory adapter and event journal

**Work**

- Translate canonical events to OptKit trajectory events.
- Segment and persist trajectories.
- Add live campaign projection and CLI inspection.
- Preserve original event payloads as native artifacts.

**Exit criteria**

- An interrupted run replays and resumes without duplicate terminal episodes.
- A selected episode can be traced from input through terminal answer.

### Phase C4 — Variable registry

**Work**

- Implement registry entries one at a time.
- Move prompt suffixes first because they share a generic materializer/checker.
- Move result-depth variables.
- Move comparison plan/intent.
- Move tool description and reranker.
- Delete each old mechanism branch after parity tests pass.

**Exit criteria**

- Adding a new variable requires a registry entry and focused implementation, not edits to a central mechanism switch.

### Phase C5 — Product constraints and typed measurements

**Work**

- Project current answer contract checks into OptKit constraints.
- Introduce objective/construct catalog.
- Wrap existing judge with complete protocol identity.
- Replace authoritative metric maps with typed measurements while retaining legacy projection.

**Exit criteria**

- UI can explain every score, protocol, missing value, hard failure, and evidence reference.

### Phase C6 — JudgeKit-native evaluation

**Work**

- Build full Coinvault JudgeKit instances and evidence sets.
- Port claim/relevance/abstention evaluation with parity fixtures.
- Add calibration and reliability artifacts.
- Establish explicit measurement epochs.

**Exit criteria**

- Candidate comparisons reject incompatible protocol mixing.
- Gate policies can require a protocol/calibration identity.

### Phase C7 — Full campaign protocol

**Work**

- Encode feedback, fresh-root reproduction, hidden evaluation, blinded review, and promotion recommendation as phases.
- Add exposure controls.
- Remove hardcoded “feedback only” orchestration from the product command; retain policy enforcement in the plan/access layer.

**Exit criteria**

- The UI shows all phases and hidden-set custody; no optimizer endpoint can access hidden payloads.

### Phase C8 — UI workspace

**Work**

- Add campaign list, plan graph, live episodes, candidate lineage, pair comparator, answer contract, and promotion ledger tiles.
- Link selected episodes to canonical Coinvault sessions.

**Exit criteria**

- Operators can plan, observe, diagnose, and review a complete campaign without reading run directories manually.

### Phase C9 — Automated search

**Work**

- Add manual and coordinate optimizers first.
- Add a reflective proposer behind human approval.
- Add a GEPA-like archive/search plugin only after exposure, protocol, and replay tests are mature.

**Exit criteria**

- Every automated proposal is a typed patch with cited trajectory evidence and can be reproduced from a recorded optimizer checkpoint.

---

## 57. Coinvault file-by-file action table

| Current path | Action | New/target path |
|---|---|---|
| `cmd/coinvault/cmds/knowledge_ragopt.go` | reduce to compatibility CLI; move orchestration | `cmd/coinvault/cmds/optimization/*`, OptKit runtime |
| `knowledge_ragopt_trace.go` | split native capture from generic projection | `internal/optimization/trajectory.go`, `artifacts.go` |
| `knowledge_ragopt_treatment.go` | replace mechanism switch with registry | `internal/optimization/registry.go`, `interventions/*` |
| `knowledge_ragopt_contract.go` | preserve logic, emit generic constraints | `internal/optimization/constraints/*` |
| `knowledge_ragopt_gate.go` | delegate to OptKit selector/report | compatibility adapter then remove |
| `knowledge_ragopt_case.go` | retain product case codec, add dataset role/provenance | `internal/optimization/cases.go` |
| `knowledge_ragopt_reranker.go` | become variable-specific parser/materializer | `interventions/reranker.go` |
| `knowledge_ragopt_suite_lock.go` | become plan/dataset resolver validation | `internal/optimization/plans`, shared OptKit data validation |
| `configs/ragopt/*` | retain as immutable archive; import | `configs/optimization/*` for new plans/snapshots |
| `internal/knowledge/judge.go` | parity adapter, then generic parts into JudgeKit | Coinvault measurement adapter + JudgeKit |
| `internal/evalchat/*` | keep canonical executor boundary | used by Coinvault OptKit executor |

---

## 58. Coinvault deprecation and compatibility policy

### 58.1 Preserve evidence, not every API

Old run directories and candidate bundles are scientific records and must remain readable. Internal Go APIs can change during migration.

### 58.2 Compatibility commands

```text
coinvault knowledge ragopt ...
  deprecated wrapper
  translates arguments into a compatibility OptKit plan

coinvault optimize import-ragopt <candidate-or-run>
  explicit historical import
```

### 58.3 Golden parity

Before deleting an old path, require:

```text
same candidate mutation detection
same canonical product behavior
same native artifact facts
same treatment/intervention status
same deterministic contract results
same judge values under same protocol
same paired deltas
same gate decision
same resource accounting
```

Differences must be documented as intentional schema or bug fixes, not accepted as “framework drift.”

---
EOF

```

```unknown
bash -lc cat >> /mnt/data/optkit-architecture-and-migration-guide.md <<'EOF'

# Part VI — Porting `rag-ttc` to OptKit

## 59. Migration principle: unify experiment semantics without forcing one experiment shape

`rag-ttc` has two kinds of optimization/evaluation work:

1. agent/tool-loop candidate evaluation, which closely resembles Coinvault's paired RagOpt trials;
2. retrieval and systems experiments, which compare multiple chunkers, representations, indexes, or ANN configurations.

The port should unify their campaign history, artifacts, measurements, and UIs while preserving distinct trial designs.

```text
                    one OptKit campaign substrate
                               |
       +-----------------------+------------------------+
       |                       |                        |
paired tool-loop trial   multi-arm retrieval trial   oracle-relative ANN trial
       |                       |                        |
chat runtime episodes     query/index episodes        exact-vs-approx episodes
```

The mistake to avoid is wrapping every study as fake `incumbent` and `challenger` pairs.

---

## 60. Current `rag-ttc` paths mapped to OptKit

| Current path or concept | Current job | OptKit destination |
|---|---|---|
| `cmd/.../tooleval/ragopt.go` | candidate loading, environment lock, paired runner | thin product command + OptKit adapter |
| `ragoptCellExecutor` | materialize config, execute tool loop, judge, write artifact | TTC executor + materializer + instrument adapters |
| `materializeToolConfig` | writes prompt/schema/search assets and hardcoded YAML | typed snapshot materializer |
| `projectChatRecord` | projects native session record | TTC trajectory and terminal projection adapter |
| `answerquality.JudgeToolLoop` | product judge | parity instrument, then JudgeKit adapter |
| `assets/configs/ragopt/i5-*` | one-mutation candidate bundle | compatibility import and plan template |
| `pkg/experiment/run.go` | immutable experiment directories | importer; compatible artifact backend ideas |
| chunk comparison experiments | multi-arm retrieval studies | `multi-arm-blocked` trial |
| representation experiments | multi-arm build/query studies | multi-arm/factorial trial |
| ANN bakeoff | approximate versus oracle comparison | `oracle-relative` trial |
| experiment browser | completed-run read-only TUI | OptKit campaign/history projection client |
| admin workbench | tile shell, shared selection, verbs | primary OptKit UI host |
| provenance tiles | one-turn retrieval/evidence inspection | product-specific episode-detail tiles |

---

## 61. Target `rag-ttc` optimization package

```text
rag-ttc/internal/optimization/
  system.go
  registry.go
  snapshot.go
  materialize.go
  executor.go
  trajectory.go
  cases.go
  constraints/
  measurements/
  trialdesigns/
    tool_loop.go
    retrieval_multiarm.go
    oracle_relative.go
  variables/
    orchestration_prompt.go
    answer_schema.go
    search_description.go
    chunker.go
    representation.go
    retrieval.go
    fusion.go
    reranker.go
    ann.go
    model_profile.go
  import/
    ragopt.go
    experiments.go

rag-ttc/cmd/rag-ttc/cmds/optimize/
  plan.go
  run.go
  resume.go
  inspect.go
  import.go
  serve.go
```

Existing experiment commands can generate an OptKit plan and delegate, preserving familiar CLI surfaces during migration.

---

## 62. `rag-ttc` variable registry

### 62.1 Tool-loop variables

| Variable ID | Current representation | Typical domain |
|---|---|---|
| `agent.orchestration_prompt` | prompt asset | text artifacts |
| `agent.answer_schema` | JSON schema asset | validated schema artifacts |
| `search.description` | YAML/text tool description | structured artifacts |
| `agent.max_provider_calls` | hardcoded/runtime setting | usually locked safety value |
| `agent.max_parallel_tools` | runtime setting | usually locked |
| `agent.reserve_final_call` | runtime setting | locked or dedicated safety campaign |
| `search.default_results` | config integer | bounded integer |
| `search.max_results_per_call` | config integer | bounded, coupled to default |
| `search.max_distinct_evidence` | config integer | bounded integer |
| `search.max_evidence_runes` | config integer | bounded integer |

### 62.2 Retrieval/index variables

| Variable ID | Meaning | Example domain |
|---|---|---|
| `index.chunker` | document segmentation algorithm/config | markdown, markdown+summary, heading-aware |
| `index.representation` | embedding/representation strategy | body, body+summary, multi-vector |
| `retrieval.bm25_top_k` | lexical pool | bounded integer |
| `retrieval.vector_top_k` | vector pool | bounded integer |
| `retrieval.fusion` | fusion algorithm/config | RRF variants, weighted fusion |
| `retrieval.reranker` | reranking config | none, cross-encoder variants |
| `retrieval.final_k` | final evidence count | bounded integer |
| `ann.backend` | exact/HNSW/etc. | categorical |
| `ann.m` | HNSW graph degree | integer domain conditional on backend |
| `ann.ef_construction` | build parameter | integer |
| `ann.ef_search` | query parameter | integer |

### 62.3 Model/profile variables

Model and embedding profile should be variables only in campaigns designed to compare them. In prompt optimization campaigns they remain locked dimensions, avoiding accidental confounding.

### 62.4 Search-space profiles

Rather than expose all variables every time, provide named profiles:

```text
ttc-tool-prompt-search-v1
  orchestration_prompt
  search_description

retrieval-depth-tuning-v1
  bm25_top_k
  vector_top_k
  final_k

chunking-study-v1
  index.chunker
  index.representation

ann-bakeoff-v1
  ann.backend
  ann.m
  ann.ef_construction
  ann.ef_search
```

---

## 63. TTC snapshots and materialization

### 63.1 Snapshot dimensions

A TTC tool-loop snapshot should capture:

```text
answer model/profile resolved identity
embedding model/profile identity
index bundle digest
corpus digest
runtime source revision
orchestration prompt artifact
answer schema artifact
search description artifact
tool safety policy
retrieval configuration
transcript policy
```

Evaluation protocol, judge profiles, and data split belong to the trial/measurement plan.

### 63.2 Typed materialization

The current hardcoded YAML is understandable but hard to extend safely. Move toward:

```go
type ToolLoopSnapshot struct {
    Model      ModelConfig
    Loop       LoopConfig
    Prompts    PromptConfig
    Tools      ToolConfig
    Transcript TranscriptConfig
}
```

```go
func (m *Materializer) Materialize(ctx context.Context, req MaterializeRequest) (Materialization, error) {
    cfg := m.LockedBase.DeepCopy()

    applyArtifact(&cfg.Prompts.OrchestrationFile, req.Snapshot, "agent.orchestration_prompt")
    applyArtifact(&cfg.Prompts.OutputSchemaFile, req.Snapshot, "agent.answer_schema")
    applyArtifact(&cfg.Tools.Search.DescriptionFile, req.Snapshot, "search.description")
    applyRetrievalVariables(&cfg.Tools.Search, req.Snapshot)

    if err := ValidateSafetyCeilings(cfg.Loop); err != nil {
        return Materialization{}, err
    }
    if err := ValidateSchemaCompatibility(cfg); err != nil {
        return Materialization{}, err
    }

    return WriteEffectiveConfig(req.Workspace, cfg)
}
```

### 63.3 Index materialization

Index-building experiments need another materializer:

```go
type IndexMaterializer interface {
    Build(ctx context.Context, snapshot SnapshotView, corpus CorpusRef, sink EventSink) (IndexArtifact, error)
}
```

Index build and query should be separate spans and resource categories. Content-addressed index artifacts allow multiple query trials to reuse one build when semantic identity matches.

### 63.4 Composite materialization

A tool-loop episode may depend on an index snapshot:

```text
agent snapshot
   references index artifact digest

index campaign
   produced that digest with full lineage
```

This creates cross-campaign provenance without forcing one giant campaign.

---

## 64. TTC trajectory adapter

### 64.1 Source

The native session `TurnRecord` already contains agent iterations, provider calls, tool calls, evidence ledger entries, answer contract, usage, and errors. Keep the session directory authoritative.

### 64.2 Mapping

```text
TurnRecord.Agent.Iterations     → model.call spans
TurnRecord.Agent.ToolCalls      → tool.call spans
TurnRecord.Agent.EvidenceLedger → evidence.admitted events
AgentResult.Answer              → message.emitted
AgentResult.Contract            → product constraint evidence
TurnRecord.Error                → error.observed
runtime status/session dir      → episode terminal/native artifact refs
```

### 64.3 Incremental versus terminal capture

The current RagOpt adapter projects after `runtime.Submit` completes. For live UIs, adapt the native agent-trace/event stream during execution when available. Until then, emit:

```text
episode.started
runtime.status snapshots
terminal trajectory segment built from TurnRecord
episode.completed
```

The schema should support both without changing terminal semantics.

### 64.4 Existing provenance UI reuse

The generic episode selection identifies the native TTC turn. Existing `FunnelPanel`, `HitsTable`, `EvidenceList`, and `DocumentView` can render directly from the product projection. They should be linked from the generic timeline and pair comparator.

---

## 65. TTC measurement migration

### 65.1 Parity-first wrapper

Wrap `answerquality.JudgeToolLoop` as an OptKit instrument. Record separate protocol identities for statement extraction and verdict judging, matching current runtime roles.

### 65.2 JudgeKit-native form

Later, build a JudgeKit evaluator suite:

```text
claim extractor
  ↓
claim support judge

answer relevance judge

citation/required-fact direct evaluators

optional tool-use appropriateness evaluator
```

Each report keeps its own protocol digest.

### 65.3 Retrieval metrics as deterministic instruments

```text
MRR
Recall@k
nDCG@k
HitRate@k
build duration
query duration
index bytes
memory estimate
```

These should use typed measurement definitions with units and directions.

Example:

```yaml
construct_id: retrieval.mrr
unit: fraction
direction: maximize
range: [0, 1]
instrument: ragkit.eval/mrr-v1
```

### 65.4 Product versus evaluation cost

Retain separate resource series:

```text
index build cost
query execution cost
answer-agent cost
judge cost
reflector/optimizer cost
```

This permits questions such as “does a more expensive index save enough answer-agent calls?”

---

## 66. TTC trial designs

### 66.1 Paired tool-loop trial

The current `i5-combined-comparison-v1` candidate remains a paired two-arm trial:

```text
same question and repeat
same index, models, runtime contract, schema, judge contract
only search.description differs
```

### 66.2 Multi-arm chunking trial

```go
type MultiArmBlockedSpec struct {
    Candidates []CandidateID
    Cases      []CaseID
    Repeats    int
    BlockBy    []string // query ID
}
```

Every query is evaluated against every chunker candidate, enabling within-query comparison.

### 66.3 Factorial retrieval trial

A campaign may study:

```text
chunker ∈ {markdown, heading-aware}
representation ∈ {body, body+summary}
reranker ∈ {none, cross-encoder}
```

This is a \(2\times2\times2\) factorial design. OptKit does not need full factorial statistics in v1, but assignments and factor metadata should be representable:

```go
type FactorAssignment struct {
    Factors map[VariableID]ValueRef
}
```

### 66.4 Oracle-relative ANN trial

For query \(q_i\):

```text
exact search result = oracle
approximate index result = candidate
```

Measure:

\[
\text{recall}_{oracle}(i)
= \frac{|N_k^{approx}(q_i) \cap N_k^{exact}(q_i)|}{k}.
\]

Also measure latency, build cost, and index size. The comparison strategy knows that one arm is an oracle reference, not an optimizable candidate.

### 66.5 Diagnostic trial

A diagnostic run may execute one snapshot across a corpus to collect trajectories and find failure clusters. It has no incumbent/challenger comparison and no promotion decision. It can feed a later proposal phase.

---

## 67. Worked port: TTC I5 combined comparison

### 67.1 Current candidate

The candidate mutates `search_description` with the hypothesis that one combined query containing all comparison subjects and requested attributes will reduce redundant search/provider calls while preserving faithfulness and relevance.

### 67.2 Imported objects

```text
parent snapshot
  search.description = parent artifact
  orchestration prompt, answer schema, runtime contract, judge contract locked
  model/index/source dimensions preserved

patch
  set search.description = candidate artifact
  support size = 1

candidate
  hypothesis, risks, selected cases copied
```

### 67.3 Trial

```yaml
design: paired-two-arm
dataset: ttc-feedback
repeats: 1
measurement_suite:
  - answer.faithfulness
  - answer.relevance
  - system.provider_calls
  - system.tool_calls
  - system.total_tokens
constraint_suite:
  - answer.contract_valid
selection_policy: imported-i5-gate
```

### 67.4 Intervention check

The TTC runtime should emit or derive the effective search-description digest supplied to the model. The intervention is exercised when that digest matches the candidate snapshot and the search tool is available. On cases with no search call, the prompt was still loaded, but the behavioral pathway may be classified separately:

```text
configuration-applied = true
behavioral-path-exercised = false
```

This two-level distinction is useful for prompt/tool-description variables.

### 67.5 Pair comparator

The UI should align search calls and show whether the challenger combined two searches into one, what evidence changed, and whether any requested comparison dimension became unsupported.

---

## 68. Worked port: chunker comparison

### 68.1 Candidate snapshots

```text
C1 index.chunker = markdown
C2 index.chunker = markdown+summary
C3 index.chunker = markdown-heading
```

Each candidate references the same corpus and representation dimensions unless intentionally varied.

### 68.2 Plan

```yaml
phase:
  kind: trial
  design: multi-arm-blocked
  candidates: [C1, C2, C3]
  dataset: ttc-retrieval-eval-v4
  repeats: 1
  measurements:
    - retrieval.mrr
    - retrieval.recall_at_1
    - retrieval.recall_at_5
    - retrieval.ndcg_at_10
    - index.chunk_count
    - index.build_duration
    - retrieval.query_duration
```

### 68.3 Execution decomposition

```text
build each unique index candidate once
         ↓
cache by snapshot/corpus/materializer identity
         ↓
execute all query assignments against each index
         ↓
aggregate metrics by arm
```

FlowKit's content-addressed caching is a natural substrate for index builds.

### 68.4 UI

The historical run-detail table from the current experiment browser becomes an `Aggregate Comparison` tile. It gains links to candidate snapshots, index-build artifacts, per-query observations, and campaign lineage.

---

## 69. Worked port: representation and chunker interaction

Suppose `markdown+summary` improves MRR only when the representation includes summary text. Treating the two settings as unrelated one-variable candidates may miss the interaction.

A factorial campaign can represent:

\[
J(c,r)
= \mu + \alpha_c + \beta_r + (\alpha\beta)_{c,r} + \epsilon.
\]

OptKit v1 need not fit this model automatically, but it should retain factor assignments and permit a future comparison plugin to estimate main effects and interactions.

The plan UI should show eight materialized combinations rather than pretending there are only two independent coordinates.

---

## 70. `rag-ttc` UI migration

### 70.1 Extend the existing workbench

Add optimization tiles to the current app registry. The same `WorldProvider` idea can be extended or a nested `OptimizationWorldProvider` can coexist with the existing turn/chunk selection.

A combined selection can link:

```text
campaign → candidate → trial → episode → native session turn → chunk/document
```

### 70.2 Recommended initial layout

```text
┌───────────────────────────────┬─────────────────────────────────┐
│ Candidate lineage             │ Trial comparison                │
│                               │                                 │
│                               ├─────────────────────────────────┤
│                               │ Episode / provenance timeline   │
│                               │                                 │
├───────────────────────────────┼─────────────────────────────────┤
│ Plan and budget               │ Document / hits / evidence      │
└───────────────────────────────┴─────────────────────────────────┘
```

Selecting a pair row updates the episode/provenance and document tiles through serializable verbs.

### 70.3 Current experiment browser

The old read-only browser should first gain an adapter that imports or reads OptKit campaign projections. Eventually it can become a TUI client of the same query service.

### 70.4 Product-specific tiles

```text
Retrieval Funnel
Chunk Fate Table
Index Build Inspector
ANN Oracle Comparator
Representation Inspector
Query Audit
Document and Evidence Views
Tool-Loop Session Inspector
```

### 70.5 Review queue

Retain the current bound review-queue behavior. It is a good example of a tile that must not follow ambient arm selection.

---

## 71. `rag-ttc` migration phases

### Phase T0 — Characterize all experiment families

**Work**

- Inventory paired tool-loop, chunk comparison, representation, index, ANN, and diagnostic experiments.
- Freeze sample run directories and current UI fixtures.
- Identify native authoritative artifacts and metric definitions.

**Exit criteria**

- Every experiment family has a documented trial design and artifact map.

### Phase T1 — Import existing RagOpt and experiment runs

**Work**

- Import `i5-combined-comparison-v1` candidate/run fixtures.
- Import one chunk-comparison run as a multi-arm campaign.
- Import one failed/crashed run, preserving partial status.

**Exit criteria**

- The OptKit aggregate table matches current `summary.md`/`results.json` values and preserves unreadable/missing artifacts explicitly.

### Phase T2 — Tool-loop OptKit adapter

**Work**

- Wrap current `ragoptCellExecutor` as an OptKit executor.
- Wrap current judge as an instrument.
- Preserve existing native session artifacts.
- Run a paired plan through OptKit.

**Exit criteria**

- Same product result, judge values, costs, and gate decision as current RagOpt.

### Phase T3 — Typed snapshot materializer

**Work**

- Replace direct hardcoded YAML concatenation behind an interface.
- Introduce typed runtime config and safety validation.
- Add effective-config artifact and digest.

**Exit criteria**

- Materializing the existing candidate produces byte-compatible or semantically identical effective config under a golden test.

### Phase T4 — Trajectory and live projection

**Work**

- Project `TurnRecord`/agent traces into OptKit events.
- Add live or terminal timeline projections.
- Link episodes to existing provenance tiles.

**Exit criteria**

- An operator can navigate from campaign candidate to exact TTC turn, tool calls, hits, evidence, and document chunks.

### Phase T5 — General trial designs

**Work**

- Implement `multi-arm-blocked` and `oracle-relative` designs.
- Port chunk comparison and ANN bakeoff.
- Use FlowKit cache identity for index builds and query execution.

**Exit criteria**

- Existing experiment commands delegate to OptKit and reproduce current metric tables.

### Phase T6 — Variable registry and search-space profiles

**Work**

- Register prompt/tool variables.
- Register retrieval/index variables.
- Add conditional constraints.
- Add domain-aware diffs.

**Exit criteria**

- New experiments are defined by plans and registry variables rather than bespoke command structs where semantics overlap.

### Phase T7 — JudgeKit and measurement epochs

**Work**

- Port answer-quality judging.
- Type retrieval metrics and units.
- Add calibration/reliability requirements for promotion campaigns.

**Exit criteria**

- UI and comparisons expose protocol identity and refuse incompatible aggregation.

### Phase T8 — Optimization workbench

**Work**

- Add campaign/plan/live/history tiles to existing workbench.
- Replace filesystem-only experiment browser data source with projection API.
- Preserve offline fixture mode for Storybook/tests.

**Exit criteria**

- Tool-loop and retrieval campaigns can be inspected through one shell.

### Phase T9 — Reflective optimization

**Work**

- Reuse prior transcript-analysis recipes as reflection-packet selectors.
- Add manual approval between reflection and patch submission.
- Later add GEPA-like archive search.

**Exit criteria**

- Reflective proposals cite exact episodes/events and can target only variables allowed by the plan.

---

## 72. `rag-ttc` file-by-file action table

| Current path | Action | Target |
|---|---|---|
| `cmd/rag-ttc/cmds/tooleval/ragopt.go` | split command, executor, materializer, measurement adapter | `internal/optimization/*`, thin command |
| `materializeToolConfig` | replace with typed snapshot materializer | `internal/optimization/materialize.go` |
| `projectChatRecord` | retain compatibility projection; add trajectory adapter | `internal/optimization/trajectory.go` |
| `answerquality.JudgeToolLoop` | wrap then port to JudgeKit | `internal/optimization/measurements/*` |
| `assets/configs/ragopt/*` | import and retain archive | new plan/candidate assets |
| `pkg/experiment/run.go` | keep for legacy producers during transition; import | OptKit store/runtime for migrated commands |
| `cmd/experiments/chunk-compare` | generate multi-arm OptKit plan | compatibility command |
| ANN/index experiment commands | generate oracle/multi-arm plans | compatibility commands |
| old experiment browser | switch to OptKit query client | TUI projection client |
| `apps/admin/web/src/world` | extend selection/verbs | optimization world or combined world |
| `apps/admin/web/src/components/pages/Workbench` | register optimization tiles | primary UI shell |
| provenance components | retain | product episode-detail tiles |

---

## 73. Cross-product reuse after both ports

Once Coinvault and `rag-ttc` use OptKit, the following can be genuinely shared:

```text
campaign and plan schemas
journal and persistence
snapshot/patch/candidate lineage
trial designs
FlowKit-backed scheduling
measurement records and JudgeKit adapter
paired and multi-arm comparison
selection policies
Pareto archive
exposure accounting
command/query/event APIs
core UI projections and generic tiles
RagOpt compatibility importer
fake-system test harness
```

The following remain separate:

```text
variable registries
materializers
canonical product executors
case codecs
product constraints
native trace adapters
JudgeKit instance builders
semantic trajectory diffing
product-specific UI tiles
deployment commands
```

This is the intended compositional boundary.

---
EOF

```

<details><summary>💭 Thinking</summary>

**Integrating architecture details**

I’m incorporating the repository’s existing adapters, workbench patterns, measurement philosophy, runtime boundaries, research references, and current draft sections into a coherent migration guide.

**Integrated architecture details**

</details>

```unknown
bash -lc wc -l -w -c /mnt/data/optkit-architecture-and-migration-guide.md && tail -n 80 /mnt/data/optkit-architecture-and-migration-guide.md
```

```unknown
bash -lc find /mnt/data/rag-self-improvement -maxdepth 3 -type d | sed 's#^/mnt/data/rag-self-improvement##' | sort | head -n 200
```

<details><summary>💭 Thinking</summary>

**Extending implementation planning**

I’m continuing with implementation tools, APIs, events, testing, operations, migration phases, worked walkthroughs, glossary material, appendices, repository evidence, references, and review checklists.

**Extended implementation planning**

**Mapped Coinvault and rag-ttc migrations to OptKit interfaces**

</details>

```unknown
bash -lc cat >> /mnt/data/optkit-architecture-and-migration-guide.md <<'EOF'
# Part VII — Implementation handbook

The preceding parts describe the target semantics. This part converts those semantics into buildable tools, package boundaries, tasks, tests, and acceptance criteria.

A common implementation failure is to begin with the optimizer algorithm. That is the wrong dependency order. A reflective optimizer is useful only after the system can reliably answer all of the following questions:

1. Which exact system snapshot was executed?
2. Which case and data epoch were used?
3. What happened during the execution?
4. Which measurement protocol produced each reported value?
5. Which candidate, parent, and patch caused the execution?
6. Which policy made the final decision?
7. Can every fact be replayed after a crash?

Therefore the implementation order is deliberately conservative:

```text
identity and schemas
        ↓
append-only journal
        ↓
materialization and execution
        ↓
trajectory and artifacts
        ↓
measurement
        ↓
comparison and selection
        ↓
query projections and UI
        ↓
manual optimizer
        ↓
automated optimizers
```

> **Callout — Control plane before search policy**
>
> The control plane is the machinery that records and coordinates optimization. The search policy is the algorithm that proposes candidates. Implementing the control plane first means that a human, coordinate search, GEPA-like reflector, or future RL optimizer can all use the same evidence and safety boundaries.

---

## 74. Deliverables: the tools that need to exist

The target should consist of one Go module and several commands or deployable entry points. They may initially live in one repository, but their responsibilities should remain distinct.

| Deliverable | Primary responsibility | Must not own |
|---|---|---|
| `optkit` Go module | domain types, laws, interfaces, local implementations | Coinvault or TTC semantics |
| `optctl` CLI | create, inspect, run, review, replay, import | long-lived scheduling state in process memory |
| `optkitd` service | persistent command/query/event API | execution of product logic inside the server binary |
| projector | derive query read models from the journal | authoritative campaign facts |
| runner worker | claim assignments and invoke product adapters | candidate proposal or promotion authority |
| measurement worker | run deterministic and JudgeKit instruments | product execution |
| optimizer worker | propose patches from campaign history | deployment |
| web/TUI client packages | render projections and submit commands | local filesystem interpretation |
| legacy importers | ingest RagOpt/Coinvault/TTC artifacts | changing source artifacts |
| doctor/linter | detect invalid plans, stores, epochs, and lineage | repairing data without an explicit command |
| fake-system harness | deterministic tests and examples | production provider dependencies |
| replay/remeasure tools | rebuild projections and measure old episodes | silently rewriting historical records |

The first development release does not need all of these as separate operating-system processes. They can be commands in one binary or goroutines in one development server. The semantic boundaries should still be represented by interfaces and event hand-offs.

### 74.1 Recommended repository name and module

```text
repository: github.com/go-go-golems/optkit
module:     github.com/go-go-golems/optkit
```

A separate repository is preferable because it enforces the dependency direction:

```text
coinvault ──┐
rag-ttc   ──┼──> optkit ──> flowkit
ragopt    ──┘       │
                    └────> optional adapter/judgekit
```

`optkit` must not import Coinvault, `rag-ttc`, RagKit, or product provider packages.

---

## 75. Proposed source tree

The following tree is deliberately more explicit than a minimal library. It shows where each concept belongs and gives an intern a place to put new code without creating an undifferentiated `internal` package.

```text
optkit/
├── go.mod
├── README.md
├── LICENSE
├── cmd/
│   ├── optctl/
│   │   └── main.go
│   ├── optkitd/
│   │   └── main.go
│   ├── optkit-projector/
│   │   └── main.go
│   └── optkit-worker/
│       └── main.go
├── identity/
│   ├── digest.go
│   ├── canonical.go
│   ├── id.go
│   └── golden_test.go
├── model/
│   ├── campaign.go
│   ├── plan.go
│   ├── snapshot.go
│   ├── patch.go
│   ├── candidate.go
│   ├── dataset.go
│   ├── trial.go
│   ├── assignment.go
│   ├── episode.go
│   ├── trajectory.go
│   ├── measurement.go
│   ├── comparison.go
│   ├── decision.go
│   ├── exposure.go
│   └── validation.go
├── space/
│   ├── registry.go
│   ├── variable.go
│   ├── domain.go
│   ├── value.go
│   ├── patch.go
│   └── builtins/
│       ├── integer.go
│       ├── choice.go
│       ├── text.go
│       ├── file.go
│       ├── json.go
│       └── composite.go
├── plan/
│   ├── compile.go
│   ├── validate.go
│   ├── budget.go
│   ├── access.go
│   └── explain.go
├── event/
│   ├── envelope.go
│   ├── kinds.go
│   ├── payloads.go
│   ├── validate.go
│   └── chain.go
├── journal/
│   ├── store.go
│   ├── memory.go
│   ├── file.go
│   ├── postgres.go
│   └── conformance_test.go
├── artifact/
│   ├── store.go
│   ├── file.go
│   ├── s3.go
│   ├── manifest.go
│   └── conformance_test.go
├── materialize/
│   ├── adapter.go
│   ├── result.go
│   └── cache.go
├── runtime/
│   ├── system.go
│   ├── runner.go
│   ├── lease.go
│   ├── scheduler.go
│   ├── retry.go
│   └── flowkit.go
├── trajectory/
│   ├── sink.go
│   ├── builder.go
│   ├── taxonomy.go
│   ├── validate.go
│   └── otelbridge/
│       ├── import.go
│       └── export.go
├── measure/
│   ├── instrument.go
│   ├── runner.go
│   ├── epoch.go
│   ├── deterministic.go
│   └── judgekit/
│       ├── adapter.go
│       └── evidence.go
├── compare/
│   ├── comparator.go
│   ├── paired.go
│   ├── multiarm.go
│   ├── oracle.go
│   ├── bootstrap.go
│   └── aggregate.go
├── selectx/
│   ├── policy.go
│   ├── lexicographic.go
│   ├── threshold.go
│   ├── human.go
│   └── explain.go
├── optimize/
│   ├── optimizer.go
│   ├── history.go
│   ├── manual.go
│   ├── coordinate.go
│   ├── random.go
│   ├── archive.go
│   └── reflect/
│       ├── packet.go
│       ├── proposer.go
│       └── validate.go
├── exposure/
│   ├── ledger.go
│   ├── policy.go
│   └── validate.go
├── project/
│   ├── projector.go
│   ├── cursor.go
│   ├── campaign.go
│   ├── plan.go
│   ├── live.go
│   ├── candidate.go
│   ├── comparison.go
│   ├── archive.go
│   └── deployment.go
├── query/
│   ├── service.go
│   ├── filters.go
│   ├── pagination.go
│   └── dto.go
├── command/
│   ├── service.go
│   ├── create_campaign.go
│   ├── submit_candidate.go
│   ├── start_trial.go
│   ├── review.go
│   ├── cancel.go
│   └── errors.go
├── transport/
│   ├── httpapi/
│   ├── sse/
│   └── websocket/
├── importx/
│   ├── ragopt/
│   ├── coinvault/
│   └── ragttc/
├── doctor/
│   ├── journal.go
│   ├── artifacts.go
│   ├── projections.go
│   ├── identity.go
│   └── report.go
├── testkit/
│   ├── fake_system.go
│   ├── fake_instrument.go
│   ├── fake_optimizer.go
│   ├── scenarios.go
│   └── assertions.go
├── examples/
│   ├── paired-prompt/
│   ├── multiarm-search/
│   ├── reflective-loop/
│   └── live-ui-fixtures/
├── schemas/
│   ├── plan-v1.schema.json
│   ├── event-v1.schema.json
│   └── export.go
└── docs/
    ├── concepts.md
    ├── adapter-guide.md
    ├── event-catalog.md
    ├── operations.md
    └── compatibility.md
```

> **Callout — Why `selectx`?**
>
> `select` is a Go keyword. The package name `selectx` makes it explicit that this package performs candidate selection, not execution scheduling.

---

## 76. Tool 1: the `optkit` Go module

### Motivation

Product repositories need a stable semantic vocabulary. Without a common module, each product will independently invent a candidate struct, run directory, event shape, score representation, and promotion process.

### Definition

The `optkit` module is a **domain-neutral optimization control-plane library**. It provides immutable value objects, interfaces, validation laws, durable event representations, comparison and selection machinery, and local reference implementations.

It does not know what a Coinvault prompt is, how TTC chunks a document, or how either product executes a conversation.

### Minimum public API for the first release

```go
package optkit

type CampaignID string
type CandidateID string
type TrialID string
type AssignmentID string
type EpisodeID string
type MeasurementID string

type Digest string

type Campaign struct {
    ID         CampaignID
    PlanDigest Digest
    CreatedAt  time.Time
}

type Snapshot struct {
    SystemKind string
    Schema     string
    Values     map[space.VariableID]space.Value
    Digest     Digest
}

type Patch struct {
    ParentDigest Digest
    Changes      []space.Change
    Digest       Digest
}

type Candidate struct {
    ID            CandidateID
    ParentSnapshot Digest
    Patch          Patch
    Snapshot       Snapshot
    Hypothesis     Hypothesis
    Provenance     Provenance
}
```

The package root should expose only the most common types. Deeper behavior should remain in focused packages.

### First worked example

```go
registry := space.NewRegistry()
registry.MustRegister(space.Int(
    "knowledge.default_results",
    space.Range(1, 20),
))
registry.MustRegister(space.Text(
    "answer.grounding_prompt",
    space.MaxBytes(64<<10),
))

parent := model.Snapshot{
    SystemKind: "coinvault-chat",
    Schema:     "coinvault.optimization.snapshot/v1",
    Values: map[space.VariableID]space.Value{
        "knowledge.default_results": space.IntValue(5),
        "answer.grounding_prompt":   space.TextValue("...") ,
    },
}

patch, err := registry.NewPatch(parent, []space.Change{{
    Variable: "knowledge.default_results",
    Before:   space.IntValue(5),
    After:    space.IntValue(8),
}})
if err != nil {
    return err
}

candidate, err := model.NewCandidate(parent, patch, model.Hypothesis{
    Claim: "Larger default result sets increase comparison evidence coverage.",
    Targets: []model.Target{{Metric: "retrieval.coverage", Group: "comparison"}},
})
```

The registry validates the type, domain, old value, and patch support. The candidate constructor derives the materialized child snapshot and its digest.

---

## 77. Tool 2: `optctl`, the operator and developer CLI

### Motivation

A UI is valuable, but a CLI is the fastest way to make every operation scriptable, testable, and usable during early development. The CLI should be a client of the same command/query APIs as the UI, not a second implementation that directly edits files.

### Definition

`optctl` is a command-line client for campaign authoring, execution, inspection, review, repair, import, and export.

### Command tree

```text
optctl
├── plan
│   ├── validate
│   ├── explain
│   ├── estimate
│   └── render
├── campaign
│   ├── create
│   ├── get
│   ├── list
│   ├── start
│   ├── pause
│   ├── resume
│   ├── cancel
│   └── export
├── candidate
│   ├── submit
│   ├── inspect
│   ├── diff
│   ├── lineage
│   └── withdraw
├── trial
│   ├── list
│   ├── inspect
│   ├── retry
│   └── cancel
├── episode
│   ├── inspect
│   ├── trace
│   ├── artifacts
│   └── remeasure
├── compare
│   ├── run
│   ├── show
│   └── export
├── review
│   ├── queue
│   ├── approve
│   ├── reject
│   └── comment
├── archive
│   ├── show
│   └── explain-dominance
├── exposure
│   ├── show
│   └── audit
├── import
│   ├── ragopt
│   ├── coinvault
│   └── rag-ttc
├── replay
│   ├── projections
│   ├── campaign
│   └── verify
├── doctor
│   ├── journal
│   ├── artifacts
│   ├── projections
│   └── all
└── serve
```

### Example session

```bash
optctl plan validate ./campaign.yaml
optctl plan explain ./campaign.yaml
optctl campaign create --plan ./campaign.yaml
optctl campaign start cmp_01J...
optctl campaign get cmp_01J... --watch
```

A useful `plan explain` output should be human-readable:

```text
Campaign: Coinvault grounded-answer experiment
System:   coinvault-chat/v1
Design:   paired incumbent/challenger
Cases:    12 feedback cases × 2 arms × 1 repeat = 24 assignments

Search space:
  answer.grounding_prompt  text, mutable, max 64 KiB

Data access:
  feedback     optimizer: allowed, detailed feedback: allowed
  validation   optimizer: denied, evaluator: allowed after reproduction

Estimated ceilings:
  answer calls      216
  embedding calls   192
  judge calls        72
  answer tokens   1,000,000

Selection order:
  1. identity and completeness
  2. hard contracts
  3. target faithfulness delta
  4. regression budgets
  5. cost tie-breakers
```

### Implementation guidance

- Use Glazed if that remains the project-standard CLI framework.
- Every mutating command should call `command.Service`.
- Every read command should call `query.Service`.
- `--local` may instantiate file-backed services in-process for development.
- `--server` should use the HTTP API.
- Machine-readable output should be available through `--output json|yaml|jsonl`.
- Do not let commands infer identities from mutable file paths after campaign creation. Resolve and persist digests first.

---

## 78. Tool 3: `optkitd`, the command/query/event service

### Motivation

A live UI, multiple workers, review queues, and crash recovery require a stable process boundary. Directly sharing a run directory over several processes is insufficient once workers can race, leases expire, or reviewers act while evaluations continue.

### Definition

`optkitd` is the **campaign control service**. It validates commands, appends authoritative events, serves query projections, and exposes an event stream. It does not execute Coinvault or TTC product code itself.

### Architectural view

```text
                  ┌──────────────────────────────┐
                  │          optkitd             │
                  │                              │
optctl ──────────▶│ command API ──▶ journal      │
web/TUI ─────────▶│ query API   ◀── projections  │
                  │ event stream ◀── journal     │
                  └──────────────┬───────────────┘
                                 │ leases / events
                ┌────────────────┼────────────────┐
                ▼                ▼                ▼
          runner worker   measurement worker  optimizer worker
                │                │                │
                ▼                ▼                ▼
           product code      JudgeKit/etc.   proposal model/human
```

### Command API sketch

```go
type Service interface {
    CreateCampaign(ctx context.Context, c CreateCampaign) (CampaignID, error)
    StartCampaign(ctx context.Context, c StartCampaign) error
    SubmitCandidate(ctx context.Context, c SubmitCandidate) (CandidateID, error)
    RecordReview(ctx context.Context, c RecordReview) error
    PauseCampaign(ctx context.Context, c PauseCampaign) error
    ResumeCampaign(ctx context.Context, c ResumeCampaign) error
    CancelCampaign(ctx context.Context, c CancelCampaign) error
}
```

Each command handler follows the same pattern:

```go
func (s *Service) Handle(ctx context.Context, cmd SubmitCandidate) error {
    state, err := s.state.LoadCampaign(ctx, cmd.CampaignID)
    if err != nil { return err }

    if err := authorize(ctx, cmd, state); err != nil { return err }
    if err := validateCandidate(cmd.Candidate, state.Plan); err != nil { return err }

    events := decideSubmitCandidate(state, cmd)
    return s.journal.Append(ctx, cmd.CampaignID, state.Version, events)
}
```

The `state.Version` argument provides optimistic concurrency. Two conflicting commands cannot both append against the same campaign version.

### Query API sketch

```go
type QueryService interface {
    Campaign(ctx context.Context, id CampaignID) (CampaignView, error)
    Campaigns(ctx context.Context, q CampaignFilter) (Page[CampaignSummary], error)
    Plan(ctx context.Context, id CampaignID) (PlanView, error)
    Live(ctx context.Context, id CampaignID) (LiveCampaignView, error)
    Candidate(ctx context.Context, id CandidateID) (CandidateView, error)
    Episode(ctx context.Context, id EpisodeID) (EpisodeView, error)
    Comparison(ctx context.Context, id ComparisonID) (ComparisonView, error)
    ReviewQueue(ctx context.Context, q ReviewFilter) (Page[ReviewItem], error)
}
```

### HTTP resource sketch

```text
POST /v1/campaigns
GET  /v1/campaigns
GET  /v1/campaigns/{campaign_id}
POST /v1/campaigns/{campaign_id}:start
POST /v1/campaigns/{campaign_id}:pause
POST /v1/campaigns/{campaign_id}:resume
POST /v1/campaigns/{campaign_id}:cancel

POST /v1/campaigns/{campaign_id}/candidates
GET  /v1/candidates/{candidate_id}
GET  /v1/candidates/{candidate_id}/lineage

GET  /v1/episodes/{episode_id}
POST /v1/episodes/{episode_id}:remeasure

GET  /v1/campaigns/{campaign_id}/events
GET  /v1/campaigns/{campaign_id}/stream

GET  /v1/reviews
POST /v1/reviews/{review_id}:approve
POST /v1/reviews/{review_id}:reject
```

### Acceptance criteria

- Every accepted command emits one or more immutable events.
- A command can be retried using an idempotency key without duplicating effects.
- Reads remain available while workers run.
- The service can restart without losing campaign state.
- The server never needs Coinvault or TTC imports.

---

## 79. Tool 4: the projector and read-model store

### Motivation

An append-only journal is ideal for correctness, but poor for direct UI queries. A campaign screen should not scan and fold 300,000 events for every refresh.

### Definition

A **projector** is a deterministic consumer that folds journal events into query-oriented read models. The journal remains authoritative; projections may be deleted and rebuilt.

Let the event stream be

\[
e_1,e_2,\ldots,e_n.
\]

A projection is a fold:

\[
V_n = f(f(\cdots f(V_0,e_1),e_2)\cdots,e_n).
\]

The fundamental law is:

\[
\operatorname{Rebuild}(e_{1:n}) = V_n.
\]

### Projector interface

```go
type Projector interface {
    Name() string
    Apply(ctx context.Context, tx Tx, envelope event.Envelope) error
    Reset(ctx context.Context, tx Tx) error
}

type CursorStore interface {
    Load(ctx context.Context, projector string) (event.Sequence, error)
    Commit(ctx context.Context, projector string, sequence event.Sequence) error
}
```

### Initial projections

| Projection | Key UI/query questions |
|---|---|
| campaign summary | state, progress, cost, current incumbent |
| plan | known/adaptive stages and ceilings |
| live activity | active assignments, recent events, worker health |
| candidate lineage | parent, patch, descendants, decisions |
| episode index | case/arm/status/cost/trace links |
| measurement matrix | metric by case/arm/protocol epoch |
| comparison | paired deltas, aggregates, uncertainty |
| archive | Pareto membership and dominance reasons |
| review queue | items awaiting human authority |
| deployment ledger | promoted snapshot → evidence → deployment |
| exposure ledger | who saw which split/evidence and when |

### Failure behavior

Projection failure must not invalidate already-accepted campaign events. Instead:

```text
journal append succeeds
        ↓
projector applies event
        ├── success → cursor advances
        └── failure → cursor stops, health alert raised
```

The operator can run:

```bash
optctl replay projections --projector comparison --from 18422
```

A projector must be idempotent at a given event ID.

---

## 80. Tool 5: runner workers

### Motivation

Product execution can be expensive, slow, provider-dependent, and differently deployed for Coinvault and TTC. The control service should therefore schedule assignments while product-specific workers execute them.

### Definition

A **runner worker** leases a pending assignment, materializes the assigned snapshot, invokes a registered product `System`, records artifacts and trajectory events, and commits an episode result.

### Worker loop

```go
for {
    lease, err := scheduler.Claim(ctx, runtime.WorkerCapabilities{
        SystemKinds: []string{"coinvault-chat/v1"},
        Labels:      map[string]string{"environment": "staging"},
    })
    if errors.Is(err, runtime.ErrNoWork) {
        backoff.Sleep(ctx)
        continue
    }
    if err != nil { return err }

    err = runAssignment(ctx, lease)
    if err != nil {
        scheduler.Fail(ctx, lease, classify(err))
        continue
    }
    scheduler.Complete(ctx, lease)
}
```

### Assignment execution

```go
func runAssignment(ctx context.Context, lease Lease) error {
    a := lease.Assignment

    materialized, err := materializer.Materialize(ctx, a.Snapshot)
    if err != nil {
        return runtime.AsConfigurationError(err)
    }

    sink := trajectory.NewJournalSink(journal, artifacts, a.EpisodeID)

    result, err := system.Execute(ctx, runtime.Request{
        Assignment:   a,
        Materialized: materialized,
        Case:         a.Case,
        Sink:         sink,
    })

    return commitEpisode(ctx, a, materialized, result, err)
}
```

### Lease semantics

A lease should contain:

```go
type Lease struct {
    ID           LeaseID
    AssignmentID AssignmentID
    WorkerID     WorkerID
    AcquiredAt   time.Time
    ExpiresAt    time.Time
    Attempt      int
    Token        string
}
```

Only the current lease token may commit a terminal assignment event. A late worker whose lease expired may still commit expensive immutable artifacts, but it must not overwrite the assignment outcome. The scheduler can attach those artifacts as orphaned/diagnostic evidence.

### FlowKit integration

Use FlowKit inside a worker or scheduler for:

- bounded execution;
- cache-aware materialization;
- retries and error classification;
- shared provider budgets;
- metering;
- per-item ledgers.

Do not use FlowKit as the persistent campaign scheduler. Its execution reports should be translated into OptKit episode/resource events.

---

## 81. Tool 6: measurement workers

### Motivation

Some measurements are deterministic and cheap. Others require LLM judges, external services, or human review. They should run independently of product execution so that old trajectories can be remeasured.

### Definition

A **measurement worker** consumes a completed episode and an instrument specification, resolves evidence from the trajectory/artifact store, executes the instrument, and appends immutable measurement records.

### Instrument API

```go
type Instrument interface {
    Descriptor() Descriptor
    RequiredEvidence() []trajectory.EvidenceSelector
    Measure(ctx context.Context, input Input) (Result, error)
}

type Descriptor struct {
    ID             InstrumentID
    ConstructID    string
    ProtocolDigest identity.Digest
    Evaluator      EvaluatorIdentity
    OutputSchema   string
    Deterministic  bool
}
```

### Pipeline

```text
completed episode
      ↓
resolve required evidence
      ↓
check applicability
      ├── not applicable → explicit NotApplicable measurement
      ├── missing evidence → MeasurementFailed/MissingEvidence
      └── available
             ↓
      run deterministic checker or JudgeKit protocol
             ↓
      persist evidence references + assessment + uncertainty
```

### JudgeKit adapter

```go
type JudgeKitInstrument struct {
    Spec     spec.Construct
    Protocol protocol.Protocol
    Judge    judging.Judge
}

func (j JudgeKitInstrument) Measure(
    ctx context.Context,
    in measure.Input,
) (measure.Result, error) {
    assessment, auditTrail, err := eval.Run(ctx, eval.Request{
        Construct: j.Spec,
        Protocol:  j.Protocol,
        Evidence:  mapEvidence(in.Evidence),
        Judge:     j.Judge,
    })
    if err != nil { return measure.Result{}, err }

    return mapAssessment(assessment, auditTrail), nil
}
```

The protocol digest is mandatory. A measurement value without a protocol identity is invalid.

### Deterministic-first sequencing

Coinvault should preserve its current sequence:

```text
treatment check
      ↓
route/retrieval/citation/contracts
      ↓ only when applicable and valid
LLM judge
```

This can be represented as an instrument dependency graph:

```yaml
instruments:
  - id: treatment-exercised
  - id: answer-contract
    depends_on: [treatment-exercised]
  - id: answer-quality-judge
    depends_on: [answer-contract]
    when: "answer-contract.status == 'pass'"
```

The dependency graph belongs to the measurement plan, not to the product executor.

---

## 82. Tool 7: optimizer workers

### Motivation

The core should support human proposals first and automated proposals later without changing campaign storage or evaluation.

### Definition

An **optimizer** reads a bounded view of campaign history and returns zero or more candidate proposals. It does not execute candidates, select winners, or deploy them.

```go
type Optimizer interface {
    ID() OptimizerIdentity
    Propose(ctx context.Context, input ProposalInput) (ProposalBatch, error)
}

type ProposalInput struct {
    Campaign       model.CampaignView
    Incumbent      model.Snapshot
    SearchSpace    space.Description
    Archive        optimize.ArchiveView
    Evidence       []EvidenceSummary
    AccessGrant    exposure.Grant
    RemainingBudget model.BudgetSnapshot
}
```

### Manual optimizer

The manual optimizer is simply an API boundary:

```go
type Manual struct{}

func (Manual) Propose(...) (ProposalBatch, error) {
    return ProposalBatch{}, optimize.ErrExternalProposalRequired
}
```

A human submits the candidate through the UI or CLI. The campaign records the human identity as proposer.

### Coordinate optimizer

```go
type Coordinate struct {
    VariableOrder []space.VariableID
    Generator     ValueGenerator
}
```

It proposes one-variable patches:

\[
|\operatorname{supp}(\delta)|=1.
\]

This is the safest first automated optimizer because it matches current RagOpt semantics and simplifies attribution.

### Reflective optimizer

A reflective optimizer should be factored into three steps:

```text
select evidence packet
        ↓
produce diagnosis
        ↓
produce typed patch proposal
```

The model must not emit an arbitrary edited repository. It emits a structured proposal whose values are validated against the registered search space.

```go
type Reflection struct {
    Diagnosis       string
    CitedEvidence   []EvidenceRef
    ResponsibleVars []space.VariableID
    ProposedChanges []space.ChangeProposal
    ExpectedEffects []model.Target
    Risks           []model.Risk
    Confidence      float64
}
```

### Mandatory proposal checks

Before candidate admission:

1. all cited evidence is accessible under the optimizer's grant;
2. every changed variable is allowed by the plan;
3. values satisfy domains;
4. patch sparsity satisfies the configured policy;
5. parent digest is current or branching is explicitly allowed;
6. expected measurements exist in the plan;
7. the candidate does not modify evaluator or hidden-data configuration;
8. proposal budget has not been exceeded.

---

## 83. Tool 8: importers for existing artifacts

### Motivation

Coinvault and TTC already have valuable runs. A migration that starts with an empty history would discard exactly the evidence the new framework is meant to preserve.

### Definition

An **importer** reads immutable legacy artifacts, translates them into OptKit events and artifacts, and records provenance back to the original path and digest. It never edits the source.

### Import mode

```bash
optctl import ragopt \
  --candidate ./configs/ragopt/candidates/grounded-answer-v2.yaml \
  --run-root ./tmp/ragopt-runs/... \
  --campaign-name imported-grounded-answer-v2
```

### Import guarantees

For each imported object, record:

```go
type LegacyProvenance struct {
    Importer        string
    ImporterVersion string
    SourceKind      string
    SourcePath      string
    SourceDigest    identity.Digest
    ImportedAt      time.Time
    Notes           []string
}
```

The importer should produce a reconciliation report:

```text
Imported candidate: cand_...
  parent snapshot: reconstructed
  patch: answer_grounding_prompt changed
  one-mutation law: pass

Imported run:
  expected cells: 24
  terminal cells: 24
  paired outcomes: 12
  measurements mapped: 72
  unmapped legacy fields: 3
  warnings:
    - judge protocol digest reconstructed from config files
    - latency clock source unavailable
```

### Importer classes

- **RagOpt importer:** candidate, suite, run cells, comparison, gate, review artifacts.
- **Coinvault importer:** native chat/session trace references and treatment reports.
- **TTC importer:** `pkg/experiment` manifests, tool-eval records, retrieval/chunking/index reports.

### Validation strategy

For imported completed runs, recompute current legacy comparisons and compare them with OptKit projections. Differences must be explained field by field before the importer is considered production-ready.

---

## 84. Tool 9: `optctl doctor` and plan linting

### Motivation

A compositional system can represent invalid combinations. Operators need a diagnostic tool that explains the exact violated law before provider calls begin.

### Definition

The doctor is a collection of read-only consistency checks over plans, journals, artifacts, projections, identities, and exposure history.

### Plan lint checks

```text
[identity]
- every referenced asset resolves to immutable bytes
- all IDs are syntactically valid
- snapshot digest recomputes

[space]
- variable IDs are unique
- defaults belong to domains
- patch-sparsity policy is satisfiable

[data]
- case IDs are unique
- dataset digests match
- hidden roles are inaccessible to proposal agents

[measurements]
- construct and protocol IDs resolve
- dependencies are acyclic
- every selection metric is produced
- protocol epochs are not implicitly mixed

[design]
- required arms exist
- paired designs share exact case/repeat blocks
- sample counts are positive

[budget]
- every external resource has a ceiling
- worst-case estimates fit campaign caps

[selection]
- hard predicates precede soft objectives
- tie-breaker metrics are available
- deployment authority is distinct when required
```

### Store doctor checks

```text
journal hash chain valid
sequence numbers contiguous or explicitly segmented
all terminal events satisfy state machine
artifact digests match bytes
all artifact references resolve
no duplicate active lease
projection cursor ≤ journal head
read models agree with replay sample
measurement protocol identities resolve
candidate lineage is acyclic
promoted snapshots have decision and review evidence
hidden-data exposure ledger has no prohibited access
```

### Example output

```text
$ optctl doctor all --campaign cmp_01J...

PASS journal.chain                  18,442 events
PASS artifacts.integrity           7,891 objects
PASS candidate.lineage             37 candidates
PASS measurement.epochs            4 epochs
WARN projection.live               23 events behind journal head
FAIL exposure.hidden-access        optimizer gepa-v1 received case val-017

Campaign is not promotable.
Suggested action:
  1. freeze campaign;
  2. mark validation epoch compromised;
  3. create a new promotion dataset epoch;
  4. retain the exposure event; do not delete it.
```

The doctor must explain corrective action but never erase incriminating events.

---

## 85. Tool 10: fake systems, fixtures, and scenario runner

### Motivation

Provider-backed tests are slow, expensive, and nondeterministic. The core cannot be tested rigorously if every scenario needs a real chat model or vector database.

### Definition

`testkit` provides deterministic fake systems, instruments, optimizers, clocks, stores, and prebuilt scenarios that exercise every state transition.

### Fake system

```go
type FakeSystem struct {
    Script func(Request) Script
}

type Script struct {
    Events []trajectory.Event
    Result runtime.Result
    Error  error
    Delay  time.Duration
}
```

### Example scenario

```go
scenario := testkit.PairedScenario{
    Cases: []model.Case{{ID: "easy"}, {ID: "hard"}},
    Incumbent: testkit.Outputs{
        "easy": {Metrics: map[string]float64{"quality": .90}},
        "hard": {Metrics: map[string]float64{"quality": .40}},
    },
    Challenger: testkit.Outputs{
        "easy": {Metrics: map[string]float64{"quality": .92}},
        "hard": {Metrics: map[string]float64{"quality": .70}},
    },
}
```

Expected paired deltas:

\[
(0.02, 0.30), \qquad \bar\Delta = 0.16.
\]

### Required fixture scenarios

1. all assignments succeed;
2. one arm missing in a pair;
3. treatment not exercised;
4. deterministic contract fails and judge is skipped;
5. judge fails after valid execution;
6. worker lease expires during an expensive call;
7. duplicate command retries;
8. journal append succeeds while projector fails;
9. protocol epoch changes without remeasurement;
10. hidden-data access violation;
11. candidate branches from stale parent;
12. two candidates are mutually nondominating;
13. materialization cache hit;
14. artifact corruption;
15. process crash between artifact commit and terminal event.

Every new core package should include tests against these fixtures where applicable.

---

## 86. Tool 11: trajectory and OpenTelemetry bridge

### Motivation

Coinvault and TTC already produce product-native traces, while infrastructure may also emit distributed traces. OptKit needs a stable optimization vocabulary without forcing products to abandon their native observability.

### Definition

The trajectory bridge maps product events and optionally OpenTelemetry spans/events into the OptKit episode taxonomy. It stores references to the native trace rather than pretending that the normalized form contains every product detail.

### Mapping example

```text
Coinvault SessionEvent                 OptKit trajectory event
──────────────────────────────────    ─────────────────────────
assistant model request               model.call.started
assistant model response              model.call.completed
knowledge_search invocation           tool.call.started
knowledge_search result               tool.call.completed
retrieval evidence ledger update      retrieval.evidence.admitted
projection block created              widget.intent.created
projection rendered                   widget.render.completed
terminal answer                       episode.output.produced
```

### Trace context

```go
type TraceLink struct {
    TraceID     string
    SpanID      string
    Provider    string
    ExternalURL string // optional and access-controlled
}
```

Each trajectory event may link to a trace context. The optimization journal does not need to duplicate all low-level logs.

### Recommended boundary

```text
OptKit event:
  semantically stable, compact, queryable

Native trace:
  product-rich, provider-specific, potentially large

Raw logs:
  operational debugging, retention-controlled
```

The UI should let a user move from a semantic episode timeline to the native trace when deeper diagnosis is needed.

---

## 87. Tool 12: replay and remeasurement

### Motivation

A major benefit of separating execution from measurement is that evaluator improvements do not always require expensive product reruns.

### Definition

**Replay** reconstructs campaign state or projections from immutable events. **Remeasurement** runs a new instrument protocol over an existing episode and records a new measurement epoch.

### Remeasurement command

```bash
optctl episode remeasure ep_01J... \
  --instrument answer-faithfulness \
  --protocol judgekit://coinvault/faithfulness/v11
```

This creates:

```text
measurement epoch v10 (historical; unchanged)
measurement epoch v11 (new records over same episodes)
```

It does not overwrite v10.

### Bridge comparison

When a protocol changes, a useful command is:

```bash
optctl compare protocol-bridge \
  --old faithfulness/v10 \
  --new faithfulness/v11 \
  --episodes @calibration-episodes
```

The result can report:

```text
n = 80 episodes
mean(new - old) = -0.04
rank correlation = 0.82
largest disagreement groups:
  comparison: 0.17 mean absolute difference
  ambiguity:  0.11 mean absolute difference
```

OptKit should not automatically declare epochs interchangeable. The bridge is evidence for a human or explicit calibration policy.

---

## 88. Core event catalog

### Motivation

Events are the durable language of the campaign. Too few event types produce opaque blobs; too many tightly coupled event types make schema evolution painful.

### Definition

An event records one immutable fact that has already happened. Event names use past tense. Commands express intent; events record accepted outcomes.

### Event envelope

```go
type Envelope struct {
    APIVersion     string
    CampaignID     model.CampaignID
    EventID        EventID
    Sequence       uint64
    PreviousDigest identity.Digest
    OccurredAt     time.Time
    Actor          Actor
    CorrelationID  string
    CausationID    string
    Kind           Kind
    PayloadSchema  string
    Payload        json.RawMessage
    ArtifactRefs   []artifact.Ref
    Digest         identity.Digest
}
```

### Campaign and plan events

| Event | Meaning |
|---|---|
| `campaign.created` | immutable plan accepted and campaign identity assigned |
| `campaign.started` | campaign allowed to schedule work |
| `campaign.paused` | no new work should be admitted |
| `campaign.resumed` | admission reopened |
| `campaign.cancel_requested` | operator requested cancellation |
| `campaign.completed` | terminal campaign outcome recorded |
| `campaign.failed` | unrecoverable control-plane failure recorded |
| `stage.opened` | a plan stage became active |
| `stage.closed` | a stage reached its terminal condition |
| `budget.reserved` | resources reserved for planned work |
| `budget.consumed` | actual resources attributed |
| `budget.released` | unused reservation returned |

### Candidate and optimization events

| Event | Meaning |
|---|---|
| `reflection.requested` | evidence packet requested from a reflector |
| `reflection.completed` | diagnosis artifact produced |
| `candidate.proposed` | typed patch and hypothesis submitted |
| `candidate.validated` | candidate passed structural/search-space checks |
| `candidate.rejected_at_admission` | proposal violated plan or access policy |
| `candidate.materialized` | child snapshot materialized and verified |
| `candidate.withdrawn` | proposer withdrew candidate before decision |
| `archive.updated` | archive membership/dominance relation changed |

### Trial and assignment events

| Event | Meaning |
|---|---|
| `trial.created` | design expanded into arms/cases/repeats |
| `assignment.scheduled` | one executable assignment made pending |
| `assignment.leased` | worker obtained exclusive lease |
| `assignment.lease_renewed` | active lease extended |
| `assignment.started` | product execution began |
| `assignment.succeeded` | terminal successful episode committed |
| `assignment.failed` | terminal failure committed |
| `assignment.cancelled` | assignment cancelled before success/failure |
| `assignment.orphaned_result_observed` | late worker produced nonauthoritative evidence |

### Episode and trajectory events

| Event | Meaning |
|---|---|
| `episode.created` | episode identity allocated |
| `episode.input.recorded` | resolved case input attached |
| `trajectory.event.recorded` | normalized semantic event appended |
| `episode.output.recorded` | final product output attached |
| `episode.artifact.attached` | native trace or output artifact linked |
| `episode.completed` | trajectory sealed for measurement |

For very high event rates, normalized trajectory events may live in a separate episode stream or artifact, with a summary event in the campaign journal. The semantic rule remains the same: the immutable reference and digest are campaign facts.

### Measurement events

| Event | Meaning |
|---|---|
| `measurement.requested` | instrument scheduled for an episode |
| `measurement.started` | instrument execution began |
| `measurement.produced` | valid measurement record committed |
| `measurement.not_applicable` | construct did not apply |
| `measurement.failed` | instrument could not produce a value |
| `measurement.epoch_opened` | protocol identity introduced for a campaign stage |
| `measurement.epoch_closed` | epoch sealed |

### Comparison, decision, and deployment events

| Event | Meaning |
|---|---|
| `comparison.requested` | comparison definition accepted |
| `comparison.produced` | deltas/aggregates/uncertainty committed |
| `selection.evaluated` | selection policy produced stage results |
| `review.requested` | human authority requested |
| `review.recorded` | signed human decision/comment committed |
| `candidate.promoted` | candidate selected as next campaign incumbent |
| `candidate.rejected` | candidate terminally rejected for the stage |
| `deployment.requested` | promotion proposed for an environment |
| `deployment.recorded` | external deployment identity linked |
| `deployment.verified` | deployed digest checked against promoted snapshot |
| `rollback.recorded` | deployment rollback linked to evidence |

### Exposure events

| Event | Meaning |
|---|---|
| `data.access_granted` | actor received permission for a role/scope |
| `data.exposed` | actual examples, labels, or detailed feedback exposed |
| `data.access_denied` | attempted prohibited access recorded |
| `validation.compromised` | hidden epoch no longer eligible for clean promotion evidence |

### Event design rules

1. Do not encode current state in the event name; record the fact.
2. Event payloads are versioned independently from the envelope.
3. Existing payload fields are never repurposed.
4. Large data belongs in artifacts with digests.
5. A terminal event never disappears.
6. Events must contain enough identity to validate replay.
7. Human decisions include actor, authority role, rationale, and policy digest.

---

## 89. Error taxonomy

### Motivation

Retries, candidate rejection, campaign failure, and measurement missingness are different outcomes. Treating them all as `error` makes recovery unsafe.

### Definition

Every operational error should map to a stable class with an explicit retry and campaign effect.

| Class | Example | Retry? | Candidate/campaign effect |
|---|---|---:|---|
| `TransientInfrastructure` | network timeout, temporary DB failure | yes, bounded | assignment remains retryable |
| `ProviderThrottled` | HTTP 429 | yes, with admission | assignment retryable; cost accounted |
| `ProviderPermanent` | invalid model name | no | assignment failed; likely plan/config error |
| `ConfigurationInvalid` | materialized prompt missing | no | candidate invalid or campaign paused |
| `CaseInvalid` | malformed test input | no | explicit data failure; do not drop silently |
| `TreatmentNotExercised` | default overridden by explicit call | normally no | measurement outcome, not infrastructure failure |
| `ContractViolation` | forbidden route or invalid citation | no | hard constraint failure |
| `MeasurementUnavailable` | required trace evidence missing | maybe after trace repair | explicit missing measurement |
| `JudgeFailed` | malformed judge output | bounded retry | measurement failed after exhaustion |
| `BudgetExhausted` | campaign cap reached | no until operator action | pause/stop according to plan |
| `LeaseLost` | worker failed to renew | no commit authority | another worker may retry |
| `ArtifactCorrupt` | digest mismatch | no automatic recompute | fail closed and alert |
| `AccessDenied` | optimizer requested hidden case | no | deny and append exposure/security event |
| `InvariantViolation` | impossible state transition | no | stop affected campaign/control plane |
| `Cancelled` | operator or parent cancellation | no | terminal cancellation semantics |

### Typed Go error

```go
type ClassifiedError interface {
    error
    Class() ErrorClass
    RetryHint() RetryHint
    SafeMessage() string
    DetailsArtifact() *artifact.Ref
}
```

Provider-specific string matching should live in product/provider adapters. The core receives typed classifications.

---

## 90. Schema and compatibility strategy

### Motivation

Optimization histories may need to remain interpretable for years. Go structs can change; persisted semantics must remain stable.

### Rules

1. Every persisted aggregate and event payload has an explicit schema URI or version string.
2. Canonical JSON is used for semantic digests where JSON is the declared representation.
3. Unknown fields are rejected for identity-bearing inputs unless the schema explicitly allows extensions.
4. Readers support a documented window of old schemas.
5. Migrations produce new artifacts/events; they do not mutate historical bytes.
6. Golden fixtures cover every digest-bearing representation.
7. A schema change that changes semantic identity requires a deliberate epoch/version bump.

### Example

```json
{
  "schema": "optkit.patch/v1",
  "parent_digest": "sha256:...",
  "changes": [
    {
      "variable": "knowledge.default_results",
      "before": {"type": "integer", "value": 5},
      "after":  {"type": "integer", "value": 8}
    }
  ]
}
```

Adding an optional human-facing note might preserve patch identity only if the note is explicitly outside the semantic digest envelope. Do not let this happen accidentally.

### Semantic versus descriptive fields

```text
semantic fields:
  affect execution or interpretation
  included in identity digest

execution-policy fields:
  workers, retries, placement
  excluded from snapshot identity
  included in run/plan identity where relevant

descriptive fields:
  labels, UI notes
  excluded from semantic identity
  versioned separately
```

This distinction should be encoded in constructors rather than left to callers.

---

## 91. Storage implementation choices

### 91.1 Local development topology

Use:

```text
file journal + file artifact store + SQLite projections
```

This supports one-command startup and reproducible examples.

```bash
optctl serve --root ./tmp/optkit-dev
```

Suggested layout:

```text
root/
├── journal/
│   └── campaigns/<campaign-id>/events-000001.jsonl
├── artifacts/
│   └── sha256/ab/cd/<digest>
├── projection.db
├── leases.db
└── server.lock
```

### 91.2 Production topology

Use:

```text
PostgreSQL journal/commands/projections
+ S3-compatible content-addressed artifacts
+ separately scalable workers
```

A simple first production schema can use:

```sql
campaign_events(
    campaign_id,
    sequence,
    event_id,
    previous_digest,
    kind,
    occurred_at,
    actor_json,
    payload_schema,
    payload_json,
    artifact_refs_json,
    digest,
    primary key(campaign_id, sequence),
    unique(event_id)
)
```

Append should be transactional with a campaign-head compare-and-swap.

### 91.3 Artifact storage

Artifacts should be content-addressed:

```text
key = sha256(canonical bytes or raw bytes, according to media type)
```

An artifact manifest contains:

```go
type Manifest struct {
    Digest      identity.Digest
    MediaType   string
    Size        int64
    Schema      string
    Compression string
    Encryption  *EncryptionDescriptor
    CreatedAt   time.Time
    Metadata    map[string]string
}
```

Secrets and sensitive traces require encryption and access policies; content addressing does not imply public readability.

---

## 92. Security, privacy, and authority boundaries

### Motivation

Optimization systems collect prompts, documents, model outputs, tool arguments, evaluation labels, and sometimes hidden validation data. They can become a concentrated data-leakage surface.

### Roles

```text
campaign-author       create plans and allowed search spaces
optimizer-agent       inspect permitted history and propose candidates
runner-worker         access executable case inputs and product runtime
measurement-worker    access evidence required by assigned instruments
reviewer              inspect selection evidence and record decisions
deployer              link approved snapshot to deployment
operator              manage infrastructure, not necessarily hidden labels
auditor                inspect immutable history and exposure ledger
```

### Capability model

An access grant should be explicit:

```go
type Grant struct {
    Actor       ActorID
    Campaign    CampaignID
    DataRoles   []model.DataRole
    Evidence    []EvidenceClass
    Operations  []Operation
    ExpiresAt   time.Time
    Constraints map[string]string
}
```

### Hidden validation rule

The optimizer may receive an aggregate pass/fail from a hidden promotion stage while being denied:

```text
case text
expected answer
case-level score
judge critique
trace details
```

If detailed hidden evidence is exposed, append `data.exposed`, mark the validation epoch compromised for future clean promotion claims, and require a new hidden epoch.

### Secret handling

- Never place provider keys in snapshots, patches, events, or UI projections.
- Materializers receive secret references through deployment configuration.
- Raw SQL/tool arguments may require redaction before general UI access.
- Artifact access uses signed/authorized retrieval, not guessable digest URLs alone.
- Reflection packets use an allowlist of evidence fields.
- Export commands default to redacted bundles.

### Human promotion authority

A selection policy may recommend promotion, but deployment-sensitive plans should require a signed human review event:

```go
type Review struct {
    Reviewer     ActorID
    Authority    string
    Decision     ReviewDecision
    Rationale    string
    EvidenceRefs []model.EvidenceRef
    PolicyDigest identity.Digest
    RecordedAt   time.Time
}
```

The deployer verifies both the review and snapshot digest.

---

## 93. Performance and scale

### Motivation

A campaign can generate many events and large traces. The design should scale without weakening semantics.

### Expected cardinalities

A useful planning envelope is:

```text
campaigns                  10²–10⁵ over system lifetime
candidates/campaign        1–10³
assignments/candidate      10–10⁵
trajectory events/episode  10–10⁴
measurements/episode       1–10²
artifacts                   potentially terabytes
```

### Scaling rules

1. Keep campaign events compact; store large trajectory streams as chunked artifacts when necessary.
2. Partition journal/projections by campaign or time.
3. Build read models incrementally.
4. Cache materialized snapshots by semantic digest.
5. Deduplicate identical assignments where the plan permits reuse.
6. Preserve original sample identity when reusing episodes.
7. Stream UI updates as summaries, then fetch detail on demand.
8. Use cursor pagination, not offset pagination, for event and episode lists.
9. Separate hot projection storage from cold artifacts.
10. Meter projection lag and worker queue depth.

### Trajectory chunking

For long agent sessions:

```text
episode
├── trajectory-summary.json
├── events-000001-001000.jsonl.zst
├── events-001001-002000.jsonl.zst
└── native-trace-ref.json
```

The episode seal records the ordered chunk digests, producing a Merkle-like immutable manifest.

### UI backpressure

A live screen should receive aggregated updates such as:

```text
assignment progress changed
candidate status changed
cost snapshot changed
recent semantic event summary
projection cursor advanced
```

It should not receive every model token or raw log line through the campaign WebSocket.

---

## 94. Observability of OptKit itself

### Motivation

The system that observes optimization also needs operational observability. Campaign evidence and infrastructure telemetry are related but not identical.

### Three layers

```text
1. Campaign journal
   semantic optimization facts; durable and user-visible

2. Distributed tracing/metrics
   service latency, worker calls, DB spans, queue depth

3. Logs
   implementation diagnostics and stack traces
```

### Correlation fields

Every service span and structured log should include when available:

```text
campaign_id
candidate_id
trial_id
assignment_id
episode_id
measurement_id
worker_id
lease_id
correlation_id
```

### Metrics

```text
optkit_journal_append_seconds
optkit_projection_lag_events
optkit_assignment_queue_depth
optkit_assignment_duration_seconds
optkit_assignment_retries_total
optkit_worker_leases_active
optkit_measurement_duration_seconds
optkit_artifact_bytes_total
optkit_budget_consumed
optkit_command_conflicts_total
optkit_hidden_access_denied_total
```

Operational metrics should not be confused with product optimization measurements. They live in different namespaces and stores.

---

## 95. Implementation milestones

The milestones below are ordered to produce usable vertical slices. Each phase should end in running code, fixtures, documentation, and a demo—not only interfaces.

### Phase O0 — Vocabulary and architecture decision records

**Goal:** freeze the minimum semantic language before implementation spreads.

**Work**

- Create repository and module.
- Write ADRs for journal authority, identity encoding, artifact store, projection model, and dependency direction.
- Implement the core glossary as Go doc comments.
- Define initial JSON schemas.
- Add a dependency-boundary test.

**Deliverables**

```text
model types without behavior
identity package skeleton
schemas/plan-v1.schema.json
schemas/event-v1.schema.json
docs/concepts.md
ADRs 001–006
```

**Exit criteria**

- A reviewer can explain snapshot, patch, candidate, assignment, episode, trajectory, measurement, comparison, decision, and campaign without product-specific examples.
- `go list -deps` confirms no product/RagKit imports.

### Phase O1 — Identity, canonicalization, and search space

**Goal:** make snapshots and patches trustworthy.

**Work**

- Implement canonical encodings and digests.
- Implement typed values and built-in domains.
- Implement registry validation.
- Implement snapshot and patch constructors.
- Add golden and property tests.

**Demo**

```bash
go run ./examples/paired-prompt identity
```

prints a stable parent snapshot digest, patch digest, and child digest.

**Exit criteria**

- Map iteration order does not alter digests.
- Invalid old values and out-of-domain new values fail closed.
- Semantic and descriptive fields are demonstrably separated.

### Phase O2 — Plan compiler and explain command

**Goal:** validate a complete campaign before execution.

**Work**

- Parse YAML/JSON plans into a compiled immutable plan.
- Resolve assets to digests.
- Validate variable, data, design, measurement, budget, and selection references.
- Implement `optctl plan validate|explain|estimate`.

**Exit criteria**

- Coinvault grounded-answer and TTC I5 plans compile.
- Invalid hidden-data access and missing metric dependencies produce clear diagnostics.

### Phase O3 — Journal, artifacts, and state fold

**Goal:** persist campaign facts and replay state.

**Work**

- Implement memory and file journal stores.
- Implement file artifact store.
- Implement event envelope/hash chain.
- Implement aggregate state fold and optimistic append.
- Implement `campaign create/start/pause/resume/cancel`.

**Exit criteria**

- Killing and restarting the process preserves state.
- Event-chain corruption is detected.
- Replaying all events yields byte-equivalent normalized state.

### Phase O4 — Assignments, workers, and fake systems

**Goal:** execute a campaign without real product dependencies.

**Work**

- Implement trial expansion and assignment scheduling.
- Implement lease store and worker loop.
- Add FlowKit execution adapter.
- Implement `testkit.FakeSystem` and failure scenarios.
- Record episodes and trajectories.

**Exit criteria**

- Paired and multi-arm fake campaigns run end to end.
- Lease expiry, retry, cancellation, and orphaned-result behavior are tested.

### Phase O5 — Measurement and comparison

**Goal:** turn episodes into typed evidence.

**Work**

- Implement instrument registry and dependency scheduling.
- Implement deterministic fake instrument.
- Implement measurement epochs.
- Implement paired and multi-arm comparators.
- Implement uncertainty/bootstrap utilities.

**Exit criteria**

- Missing arm pairs are explicit.
- Epoch mixing is rejected unless a bridge policy is supplied.
- Legacy paired arithmetic fixtures match exactly.

### Phase O6 — Selection, review, and archive

**Goal:** reproduce RagOpt's evidence-gated decision semantics.

**Work**

- Implement lexicographic selection stages.
- Implement explanations and per-predicate evidence.
- Implement review queue and signed review records.
- Implement Pareto archive and dominance explanations.

**Exit criteria**

- The `grounded-answer-v2` example passes its target stage but fails its hard stage exactly as expected.
- No cost improvement can compensate for a hard failure.

### Phase O7 — Projections, query API, and event stream

**Goal:** support live and retrospective clients.

**Work**

- Implement SQLite projection store.
- Implement core projectors.
- Implement HTTP query API and SSE/WebSocket stream.
- Add projection replay and lag health.

**Exit criteria**

- Deleting the projection DB and replaying produces equivalent views.
- A client sees assignment progress while fake workers run.

### Phase O8 — Legacy RagOpt importer and compatibility runner

**Goal:** make existing experiments visible and prove semantic parity.

**Work**

- Import candidate/suite/run/comparison/gate artifacts.
- Add reconciliation report.
- Add a compatibility runner that emits both old and new representations during shadow runs.

**Exit criteria**

- Representative Coinvault and TTC runs import with explained zero or accepted differences.
- Existing RagOpt outputs remain available during migration.

### Phase O9 — Coinvault adapter

**Goal:** run Coinvault through OptKit without changing canonical chat behavior.

**Work**

- Implement Coinvault variable registry, materializer, system adapter, trajectory adapter, instruments, and importer.
- Run shadow parity campaigns.
- Add Coinvault-specific UI tiles.

**Exit criteria**

- A current candidate produces equivalent cell outcomes, traces, measurements, and gate result.
- Canonical HTTP/sessionstream path remains authoritative.

### Phase O10 — TTC adapter

**Goal:** cover paired tool eval and one nonpaired experiment family.

**Work**

- Implement TTC variable registry, materializer, system adapters, trajectory adapter, instruments, and importer.
- Port tool-eval paired campaign.
- Port chunker or ANN multi-arm campaign.
- Integrate the workbench.

**Exit criteria**

- One paired and one multi-arm TTC campaign run through the same core.
- Existing provenance UI remains reachable.

### Phase O11 — Production service topology

**Goal:** move from local reference implementation to multiworker deployment.

**Work**

- PostgreSQL journal/projections/leases.
- S3-compatible artifact store.
- authentication/authorization.
- worker registration and capabilities.
- operational dashboards and backups.

**Exit criteria**

- rolling restart does not lose or duplicate authoritative outcomes;
- access controls pass security review;
- disaster-recovery replay is demonstrated.

### Phase O12 — Reflective optimization

**Goal:** automate the proposal step while retaining existing controls.

**Work**

- reflection packet builder;
- evidence access enforcement;
- structured proposal schema;
- human approval mode;
- coordinate and GEPA-like archive policies;
- proposal budget/accounting.

**Exit criteria**

- Every proposal cites accessible evidence and changes only registered variables.
- Disabling the optimizer leaves manual campaigns fully usable.
- Hidden validation remains inaccessible to the proposal model.

---

## 96. Suggested pull-request decomposition

Large architectural migrations fail when one pull request contains the entire new world. The following PR size is appropriate for an intern with frequent review.

### Example sequence for O1

```text
PR 1: identifier types and validation
PR 2: canonical JSON and digest fixtures
PR 3: typed scalar values
PR 4: integer/choice/text domains
PR 5: variable registry
PR 6: snapshot constructor and digest
PR 7: patch constructor and child application
PR 8: property tests and examples
PR 9: documentation pass
```

### Review rule

Each PR should answer:

1. Which law does this implement?
2. Which public API is introduced or changed?
3. Which fixtures prove compatibility?
4. What can fail, and how is it classified?
5. What is deliberately not implemented?

### Avoid horizontal scaffolding PRs

A PR containing 40 empty interfaces across 20 packages produces little testable value. Prefer a vertical slice such as:

```text
parse one plan
→ create one campaign
→ append one event
→ query one projection
```

before adding another abstraction.

---

## 97. Testing strategy

### 97.1 Unit tests

Test pure constructors and validators:

- IDs;
- canonical encoding;
- digest generation;
- domains;
- patch application;
- state transitions;
- event validation;
- aggregate arithmetic;
- selection predicates.

### 97.2 Property tests

Property tests are especially valuable for algebraic laws.

#### Patch identity

For valid patch \(\delta\):

\[
(\theta \oplus \delta) \ominus \delta = \theta
\]

when an inverse is defined.

#### Empty patch

\[
\theta \oplus \varnothing = \theta.
\]

Empty patches should normally be rejected as candidates, but the algebra can still be tested.

#### Independent patch commutation

For patches over disjoint variables:

\[
(\theta\oplus\delta_1)\oplus\delta_2
=
(\theta\oplus\delta_2)\oplus\delta_1.
\]

This law applies to snapshot values, not necessarily to materialized product artifacts if a product incorrectly introduces hidden coupling. A conformance test can detect that discrepancy.

#### Replay determinism

\[
\operatorname{Fold}(e_{1:n})
=
\operatorname{Fold}(e_{1:k}\mathbin{+}e_{k+1:n}).
\]

#### Paired-difference antisymmetry

\[
\Delta(A,B)=-\Delta(B,A).
\]

#### Pareto nondominance

Every archive member must be undominated under the configured relation.

### 97.3 Conformance suites

Every implementation of these interfaces should run the same suite:

```text
journal.Store
artifact.Store
materialize.Adapter
runtime.System
measure.Instrument
compare.Comparator
selectx.Policy
```

### 97.4 Golden tests

Keep golden bytes for:

```text
snapshot/v1
patch/v1
candidate/v1
plan/v1
event envelope/v1
measurement/v1
comparison/v1
review/v1
```

A golden change requires an explicit compatibility note.

### 97.5 Crash tests

Inject process termination at boundaries:

```text
before journal append
after journal append, before response
after artifact write, before reference event
after assignment starts, before lease renewal
after product success, before terminal event
after measurement output, before commit
during projection transaction
```

Then restart and assert the documented recovery outcome.

### 97.6 Race tests

Run `go test -race` for:

```text
journal append
lease claim/renew/complete
materialization cache
projection consumers
budget admission
in-flight deduplication
```

### 97.7 Migration parity tests

For each ported legacy fixture:

```text
legacy output
      ↓ normalize
expected semantic record
      ↑ normalize
OptKit output
```

Compare:

- arm/case/repeat identity;
- terminal status;
- treatment exercise;
- contract failures;
- judge values;
- paired deltas;
- aggregate values;
- gate stage and reasons;
- cost/resource counts;
- artifact digests where representations are preserved.

### 97.8 UI tests

Use static projection fixtures and Storybook-like stories for:

- empty campaign;
- planned campaign;
- active paired run;
- partial/missing pair;
- hard-gate rejection;
- Pareto archive;
- hidden-data redaction;
- stale projection warning;
- protocol epoch mismatch;
- deployment lineage.

End-to-end tests should exercise selection links between tiles, deep links, live updates, and review commands.

---

## 98. Documentation an intern must write with the code

Documentation is part of the implementation, not a final polish phase.

Each package should have:

1. motivation;
2. definition of its central type;
3. one minimal example;
4. one realistic Coinvault or TTC example where appropriate;
5. laws/invariants;
6. non-goals;
7. failure modes;
8. compatibility notes.

Every new event payload needs an entry in `docs/event-catalog.md` containing:

```text
purpose
producer
required fields
state transition
idempotency behavior
artifact references
redaction level
example JSON
evolution notes
```

Every adapter must provide an `ADAPTER.md` answering:

```text
What is the product system kind?
What belongs to a semantic snapshot?
What variables can change?
How are snapshots materialized?
What is the canonical execution path?
Which native trace is authoritative?
How are trajectory events normalized?
Which deterministic constraints exist?
Which JudgeKit instruments exist?
Which data roles are available?
How is deployment verified?
```

---

## 99. Architecture decision records to write

At minimum:

| ADR | Decision |
|---|---|
| ADR-001 | OptKit owns campaign semantics; products own execution semantics |
| ADR-002 | Append-only event journal is authoritative control history |
| ADR-003 | Large/native evidence uses content-addressed artifact references |
| ADR-004 | Snapshot identity excludes execution policy but includes all output-affecting product semantics |
| ADR-005 | Measurements require construct and protocol identity |
| ADR-006 | Selection is separate from optimization and deployment |
| ADR-007 | Hidden-data exposure is recorded as an irreversible fact |
| ADR-008 | FlowKit is execution substrate, not persistent scheduler |
| ADR-009 | JudgeKit is instrument layer, not a universal reward oracle |
| ADR-010 | Product UIs consume projections through shared command/query/event APIs |
| ADR-011 | Legacy imports preserve source digests and never edit source artifacts |
| ADR-012 | Automated optimizers emit typed patches, not arbitrary repository edits |

Each ADR should include context, considered alternatives, decision, consequences, and migration impact.

---

## 100. Risk register

| Risk | Why it matters | Mitigation |
|---|---|---|
| Overgeneralized core | product semantics leak into generic types or generic types become unusably abstract | require two-product examples for every promoted abstraction |
| Under-specified identity | cache reuse or comparisons become invalid | identity review checklist, golden tests, product conformance fixtures |
| Event explosion | journal and UI become noisy/slow | semantic summary events, chunked trajectory artifacts, projections |
| Judge Goodharting | optimizer exploits measurement defects | hidden promotion epochs, multiple instruments, calibration, human review |
| Data leakage | reflective optimizer sees validation labels | access grants, redacted packets, exposure journal, compromised-epoch rule |
| Migration drift | old and new paths disagree silently | dual-write/shadow runs, parity reports, fixed cutover criteria |
| Workflow-server creep | OptKit reimplements a general distributed orchestrator | keep assignment scheduler bounded to campaign semantics; use external infra when needed |
| Product runtime fork | evaluation path differs from production | adapters call canonical runtime; no simplified eval-only clone |
| Scalar reward collapse | safety/quality constraints become tradeable | typed measurements and lexicographic selection |
| Protocol epoch mixing | trends compare incompatible judge scales | mandatory protocol digest; explicit bridge/remeasurement |
| Stale UI projections | users make decisions on old data | expose cursor/head lag; review command checks current version |
| Automatic deployment | optimizer bypasses human/product authority | separate deployment records and signed review requirements |
| Unbounded cost | adaptive search consumes provider budget | plan ceilings, FlowKit admission, campaign stop policies |
| Intern abstraction overload | implementation stalls in theory | vertical milestones, fake system, concrete examples, frequent reviews |

---

## 101. Definition of done for OptKit v0.1

OptKit v0.1 is complete when all of the following are true:

### Core semantics

- Snapshots, patches, candidates, plans, trials, assignments, episodes, trajectories, measurements, comparisons, reviews, and campaigns have stable v1 schemas.
- Identity golden fixtures exist.
- Laws are documented and tested.

### Persistence

- Local journal and artifact stores survive restart.
- Journal integrity and artifact digests are verifiable.
- Projections rebuild from zero.

### Execution

- Paired and multi-arm designs execute through fake systems.
- Worker leases and retries are safe.
- FlowKit integration meters and bounds work.

### Evidence

- Deterministic instruments and JudgeKit adapter work.
- Measurement epochs are enforced.
- Paired comparisons and lexicographic gates are reproducible.

### Products

- One Coinvault feedback campaign runs in shadow mode with legacy parity.
- One TTC paired tool-eval campaign runs in shadow mode with legacy parity.
- One TTC multi-arm retrieval/indexing campaign runs through OptKit.

### UI

- Plan, live, candidate evidence, comparison, and history projections are available.
- At least one web workbench and one CLI/TUI client consume them.
- Review actions use command APIs and optimistic concurrency.

### Operations

- `doctor`, replay, import, and export commands exist.
- Hidden access is enforced and audited.
- A recovery exercise has been documented.

### Automation

- Manual and coordinate optimizers work.
- Reflective optimizer may remain experimental, but its typed proposal boundary and access controls must exist.

---

## 102. Intern onboarding path

An intern should not begin by reading every repository. Use the following sequence.

### Day 1: run one existing experiment

1. Run or inspect one Coinvault RagOpt feedback run.
2. Follow one cell from case input to native trace, contract, judge, comparison, and gate.
3. Draw the objects on paper.

Expected understanding:

```text
candidate ≠ run
run cell ≠ LLM call
episode ≠ measurement
measurement ≠ decision
gate pass ≠ deployment
```

### Day 2: inspect one TTC experiment

1. Inspect paired tool-eval.
2. Inspect a nonpaired chunking, representation, index, or ANN experiment.
3. Identify what is common and what cannot be forced into a paired shape.

### Day 3: run the OptKit fake example

1. Create a plan.
2. Start a fake campaign.
3. inspect events;
4. delete projections;
5. replay;
6. verify identical views.

### First implementation task

Implement one small vertical feature such as:

```text
candidate.proposed event
→ campaign fold
→ candidate projection
→ CLI inspect output
→ tests
```

This teaches the full command/event/projection pattern without provider complexity.

### Review cadence

The intern should receive review at each of these boundaries:

```text
schema/API
identity behavior
state transition
persistence behavior
projection/UI result
migration parity
```

A weekly architecture review should focus on whether a new concept belongs in OptKit, a product adapter, FlowKit, JudgeKit, or RagKit.

---
EOF
```

<details><summary>💭 Thinking</summary>

**Appended implementation handbook content**

</details>

```unknown
bash -lc cat >> /mnt/data/optkit-architecture-and-migration-guide.md <<'EOF'
# Part VIII — Complete worked examples

The following examples are intentionally repetitive. Each one follows the same objects from planning through execution, measurement, comparison, and decision. Repetition is useful here because it demonstrates which parts remain invariant across products and which parts belong to adapters.

---

## 103. Worked example A: porting Coinvault `grounded-answer-v2`

### 103.1 Motivation

The existing candidate is an ideal migration fixture because it demonstrates all of the important semantics:

- one prompt mutation;
- a full multi-turn/tool-using product trajectory;
- a strong target improvement;
- unrelated hard failures;
- lexicographic rejection;
- a need for human interpretation rather than scalar ranking.

### 103.2 Step 1 — register the variable

Coinvault owns this code:

```go
func RegisterVariables(r *space.Registry) {
    r.MustRegister(space.Text(
        "coinvault.answer.grounding_prompt",
        space.MaxBytes(64<<10),
        space.Materializer("coinvault.answer-prompts/v1"),
        space.Description("Instructions controlling evidence-grounded answer synthesis."),
    ))
}
```

The variable definition says what values are valid. It does not know the current prompt or how a complete Coinvault configuration is launched.

### 103.3 Step 2 — construct the parent snapshot

A product snapshot might contain:

```yaml
schema: coinvault.optimization.snapshot/v1
system_kind: coinvault-chat/v1
values:
  coinvault.answer.grounding_prompt:
    type: text-asset
    digest: sha256:parent-prompt
  coinvault.answer.routing_prompt:
    type: text-asset
    digest: sha256:routing-prompt
  coinvault.answer.policy_prompt:
    type: text-asset
    digest: sha256:policy-prompt
  coinvault.knowledge.default_results:
    type: integer
    value: 5
  coinvault.knowledge.forced_results:
    type: integer
    value: 8
  coinvault.knowledge.reranker:
    type: object
    schema: coinvault.reranker/v1
    value:
      kind: none
  coinvault.knowledge.tool_description:
    type: text-asset
    digest: sha256:tool-description
runtime_identity:
  app_revision: git:...
  bundle_digest: sha256:...
  answer_model: provider/model/revision
  embedding_model: provider/model/revision
```

The exact placement of runtime identity needs care. Fields that alter product outputs but are not candidate variables still belong in the executable snapshot or an immutable system environment reference. Worker counts and retry limits do not.

### 103.4 Step 3 — encode the patch and hypothesis

```yaml
schema: optkit.candidate/v1
candidate_id: cand_grounded_answer_v2
parent_snapshot: sha256:parent-snapshot
patch:
  schema: optkit.patch/v1
  changes:
    - variable: coinvault.answer.grounding_prompt
      before:
        type: text-asset
        digest: sha256:parent-prompt
      after:
        type: text-asset
        digest: sha256:grounded-answer-v2-prompt
hypothesis:
  claim: >-
    Requiring direct clause-level entailment and adjacent evidence citations
    will reduce unsupported claims in comparison answers.
  targets:
    - construct: answer.faithfulness
      groups: [feedback, comparison]
      direction: increase
  risks:
    - construct: answer.relevance
      failure_mode: answers may become too terse
    - construct: answer.completeness
      failure_mode: synthesis may be omitted
proposer:
  kind: human
  id: engineer@example
```

OptKit validates:

\[
|\operatorname{supp}(\delta)|=1
\]

under this campaign's patch policy.

### 103.5 Step 4 — compile the campaign plan

```yaml
schema: optkit.plan/v1
name: coinvault-grounded-answer-v2
system:
  kind: coinvault-chat/v1
  adapter: coinvault://optimization/system/v1

incumbent:
  snapshot: sha256:parent-snapshot

search_space:
  registry: coinvault://optimization/variables/v1
  allow:
    - coinvault.answer.grounding_prompt
  patch_policy:
    max_changed_variables: 1

stages:
  - id: feedback
    kind: evaluation
    data:
      dataset: coinvault://eval/feedback/v1
      role: development
    design:
      kind: paired
      arms:
        incumbent: $incumbent
        challenger: $candidate
      repeats: 1
    measurements:
      - treatment.grounding-prompt-active
      - contract.answer
      - answer.faithfulness/v10
      - answer.relevance/v10
      - answer.unsupported-claim-rate/v10
    selection: coinvault://gates/grounded-answer/v2
    on_pass: reproduce
    on_fail: stop

  - id: reproduce
    kind: evaluation
    data:
      dataset: coinvault://eval/feedback/v1
      role: reproduction
    environment:
      fresh_root: true
    design:
      kind: paired
      repeats: 1
    on_pass: validation
    on_fail: stop

  - id: validation
    kind: evaluation
    data:
      dataset: coinvault://eval/validation/epoch-3
      role: hidden-promotion
    access:
      optimizer: denied
      detailed_feedback_to_optimizer: denied
    design:
      kind: paired
      repeats: 1
    on_pass: human-review
    on_fail: stop

  - id: human-review
    kind: review
    authority: coinvault-promotion-reviewer

budgets:
  resources:
    answer.calls: 216
    embedding.calls: 192
    judge.calls: 72
    answer.tokens: 1000000

stop:
  on_budget_exhausted: pause
  on_hard_invariant_failure: stop-stage
```

The plan compiler computes the exact known feedback workload and conservative bounds for adaptive/future stages.

### 103.6 Step 5 — materialize the challenger

Coinvault's materializer receives the complete child snapshot, not only the patch.

```go
type CoinvaultMaterializer struct {
    Assets AssetResolver
    Base   BaseRuntimeConfig
    Cache  materialize.Cache
}

func (m *CoinvaultMaterializer) Materialize(
    ctx context.Context,
    s model.Snapshot,
) (materialize.Result, error) {
    grounding, err := m.Assets.Text(ctx,
        s.Value("coinvault.answer.grounding_prompt").Digest(),
    )
    if err != nil { return materialize.Result{}, err }

    cfg := m.Base.Clone()
    cfg.Answer.GroundingPromptSuffix = grounding
    cfg.Knowledge.DefaultResults = s.Int("coinvault.knowledge.default_results")
    cfg.Knowledge.ForcedResults = s.Int("coinvault.knowledge.forced_results")
    cfg.Knowledge.Reranker = decodeReranker(s.Value("coinvault.knowledge.reranker"))

    dir, manifest, err := writeImmutableRuntimeBundle(ctx, cfg)
    if err != nil { return materialize.Result{}, err }

    if err := verifyRuntimeBundle(dir, s); err != nil {
        return materialize.Result{}, err
    }

    return materialize.Result{
        SnapshotDigest: s.Digest,
        RuntimeRef:     dir,
        Manifest:       manifest,
    }, nil
}
```

The materializer must emit a manifest proving which asset digests became which runtime files/flags.

### 103.7 Step 6 — expand the paired trial

For cases \(x_1,\ldots,x_{12}\), arms \(a\in\{0,1\}\), and repeat \(r=0\), the design expands to:

\[
12\times2\times1=24
\]

assignments.

```text
assignment 001 = case feedback-001, incumbent, repeat 0
assignment 002 = case feedback-001, challenger, repeat 0
assignment 003 = case feedback-002, incumbent, repeat 0
assignment 004 = case feedback-002, challenger, repeat 0
...
```

The execution order is policy. The pairing identity is semantic. Running all incumbents first would not invalidate pairing, provided the block IDs remain exact and environment effects are handled by the design.

### 103.8 Step 7 — execute one challenger episode

The Coinvault adapter invokes the same canonical chat path used by production-facing integration:

```go
func (s *System) Execute(ctx context.Context, req runtime.Request) (runtime.Result, error) {
    collector := NewOptKitTraceCollector(req.Sink)

    response, err := s.EvalChat.Run(ctx, evalchat.Request{
        RuntimeRoot: req.Materialized.RuntimeRef,
        SessionID:   req.Assignment.EpisodeID.String(),
        UserMessage: decodeQuestion(req.Case),
        Collector:   collector,
    })
    if err != nil { return runtime.Result{}, classifyCoinvaultError(err) }

    return runtime.Result{
        Output:       artifact.FromJSON(response.FinalAnswer),
        NativeTrace:  collector.NativeTraceRef(),
        ResourceUsage: collector.Usage(),
    }, nil
}
```

A normalized trajectory might be:

```text
00:00.000 episode.input.recorded
00:00.011 model.call.started             purpose=answer-agent
00:01.492 model.call.completed           finish=tool_call
00:01.493 tool.call.started              tool=knowledge_search
00:01.494 retrieval.query.transformed    query_digest=...
00:01.620 retrieval.candidates.produced  lexical=40 vector=40
00:01.667 retrieval.reranking.completed  reranker=none
00:01.670 retrieval.evidence.admitted    count=8 ledger_digest=...
00:01.671 tool.call.completed             tool=knowledge_search
00:01.676 model.call.started              purpose=answer-agent
00:03.112 model.call.completed            finish=stop
00:03.114 episode.output.recorded         answer_digest=...
00:03.120 episode.completed
```

The native Sessionstream/chat record remains attached as authoritative product evidence.

### 103.9 Step 8 — run intervention and deterministic instruments

The first instrument verifies that the prompt was active:

```go
func GroundingPromptActive(in measure.Input) measure.Result {
    observed := in.Trajectory.Find("runtime.prompt.loaded", map[string]string{
        "slot": "answer.grounding",
    })

    expected := in.Assignment.Snapshot.
        Value("coinvault.answer.grounding_prompt").Digest()

    if observed == nil || observed.Attr("digest") != expected.String() {
        return measure.Fail("treatment_not_exercised", ...)
    }
    return measure.Pass(...)
}
```

Then the answer contract evaluates route, retrieval, evidence, citation, and runtime predicates.

```go
contract := And(
    RouteContract(caseSpec),
    RetrievalContract(caseSpec),
    EvidenceLedgerContract(caseSpec),
    CitationContract(caseSpec),
    ProjectionContract(caseSpec),
)
```

Only if the dependency policy permits does the JudgeKit-backed answer-quality instrument run.

### 103.10 Step 9 — produce typed measurements

One measurement record might be:

```json
{
  "schema": "optkit.measurement/v1",
  "measurement_id": "meas_...",
  "episode_id": "ep_...",
  "construct_id": "answer.faithfulness",
  "instrument_id": "coinvault.faithfulness-judge",
  "protocol_digest": "sha256:judge-protocol-v10",
  "value": {"kind": "scalar", "number": 0.9615},
  "uncertainty": null,
  "applicability": "applicable",
  "evidence_refs": [
    {"kind": "answer", "digest": "sha256:..."},
    {"kind": "evidence-ledger", "digest": "sha256:..."},
    {"kind": "judge-audit", "digest": "sha256:..."}
  ]
}
```

A contract failure produces a separate predicate measurement and may produce an explicit `not_applicable` answer-quality measurement rather than a fake zero.

### 103.11 Step 10 — compare exact pairs

For each case:

\[
\Delta_i^F=F_{i,candidate}-F_{i,incumbent}.
\]

For the two targeted cases:

\[
\Delta_{	ext{Morgan/Peace}}^F=1.0000-0.4595=0.5405
\]

and

\[
\Delta_{	ext{gold coins/bars}}^F=0.9615-0.3778\approx0.5838.
\]

The target aggregate is approximately:

\[
\bar\Delta^F_{target}\approx0.562.
\]

The comparison record retains the case-level deltas, not only the mean.

### 103.12 Step 11 — evaluate the lexicographic selector

```go
policy := selectx.Lexicographic{
    Stages: []selectx.Stage{
        IdentityAndCompleteness(),
        HardContracts(
            AllChallengerCellsComplete(),
            ZeroChallengerContractFailures(),
            MinPerCase("answer.faithfulness", .80),
        ),
        Target(
            MeanDeltaAtLeast("answer.faithfulness", []string{"feedback", "comparison"}, 0),
        ),
        Regressions(
            PerCaseDeltaAtLeast("answer.faithfulness", -.20),
            PerCaseDeltaAtLeast("answer.relevance", -.30),
            MeanDeltaAtLeast("answer.faithfulness", []string{"all"}, -.05),
            MeanDeltaAtLeast("answer.relevance", []string{"all"}, -.05),
        ),
        CostTieBreakers(),
    },
}
```

The candidate strongly passes the target stage but fails the hard stage because several challenger episodes violate route/retrieval/projection contracts. Evaluation stops at the first failing stage for the promotion result, while later-stage diagnostic values may still be displayed as nonauthoritative context.

### 103.13 Step 12 — render the UI

```text
┌ Coinvault / grounded-answer-v2 ───────────────────────────────────────────────┐
│ STATE: REJECTED      Stage: feedback      Candidate: cand_grounded_answer_v2 │
├───────────────────────────────────────────────────────────────────────────────┤
│ PATCH                                                                         │
│ answer.grounding_prompt    sha256:parent → sha256:grounded-v2                 │
│ changed variables: 1 / allowed 1                                              │
├───────────────────────┬───────────────────────────────────────────────────────┤
│ SELECTION STAGES      │ TARGET EVIDENCE                                       │
│ ✓ identity           │ Morgan vs Peace     faithfulness  +0.5405             │
│ ✗ hard contracts     │ Gold coins vs bars faithfulness  +0.5838             │
│ · target             │ target mean                       +0.5621             │
│ · regressions        │ relevance deltas                 +0.32, +0.23         │
│ · cost               │                                                       │
├───────────────────────┴───────────────────────────────────────────────────────┤
│ HARD FAILURES                                                                  │
│ feedback-004  forbidden route       [open episode] [compare pair]             │
│ feedback-007  missing retrieval     [open episode] [compare pair]             │
│ feedback-010  projection contract   [open episode] [compare pair]             │
│ ...                                                                           │
├───────────────────────────────────────────────────────────────────────────────┤
│ INTERPRETATION                                                                 │
│ Intended grounding mechanism improved targeted cases, but candidate is not    │
│ promotable as a complete system snapshot.                                     │
└───────────────────────────────────────────────────────────────────────────────┘
```

The UI must not render only a large red “failed.” It should preserve the distinction:

```text
treatment effect evidence: strong
promotion eligibility: failed
```

That distinction drives the next diagnosis.

### 103.14 Step 13 — produce the next optimization history

The campaign history now contains:

```text
parent snapshot
candidate patch
24 episodes
all native traces
all intervention checks
all contracts
judge measurements
paired comparison
selection explanation
human comments
```

A human reflector can now propose a routing candidate while citing the failed route episodes. A future automated reflector receives the same bounded evidence packet.

---

## 104. Worked example B: Coinvault default result depth and a non-exercised treatment

### 104.1 Motivation

This example explains why an optimization framework needs intervention checks. A configuration can change without affecting runtime behavior.

### 104.2 Candidate

\[
\delta:
\texttt{knowledge.default\_results}:5\mapsto8.
\]

The hypothesis is that more default evidence improves coverage on comparison questions.

### 104.3 Runtime behavior

Suppose the model emits:

```json
{
  "tool": "knowledge_search",
  "arguments": {"query": "Morgan Peace dollar differences", "limit": 5}
}
```

The effective result limit is therefore 5 because an explicit call argument overrides the default.

### 104.4 Intervention check

```go
type ResultLimitObservation struct {
    ConfiguredDefault int
    RequestedLimit    *int
    EffectiveLimit    int
    Source            string // "explicit", "default", "forced", ...
}
```

The checker returns:

```json
{
  "construct_id": "treatment.default-results-exercised",
  "value": {"kind": "boolean", "boolean": false},
  "diagnostics": {
    "configured_default": 8,
    "requested_limit": 5,
    "effective_limit": 5,
    "effective_source": "explicit"
  }
}
```

### 104.5 Correct interpretation

It is invalid to infer:

\[
J(8)-J(5)\approx0.
\]

The actual observation is:

\[
S_{default=8}(x)
\]

followed the same effective runtime branch as the incumbent. The intervention on the causal variable did not reach the executed mechanism.

The experiment therefore teaches:

```text
change tool-call policy or tool description,
change forced limit,
or choose cases where the default is used
```

rather than “larger result sets do not help.”

### 104.6 UI

```text
┌ Treatment inspector ───────────────────────────────────────────────┐
│ Candidate change: default_results 5 → 8                           │
│ Episode: feedback-003 / challenger                                │
├───────────────────────────────────────────────────────────────────┤
│ configured default       8                                        │
│ model requested          5                                        │
│ effective limit          5                                        │
│ effective source         explicit tool argument                    │
│ treatment exercised      NO                                       │
├───────────────────────────────────────────────────────────────────┤
│ This episode is not evidence about the effect of retrieving 8     │
│ results. The changed default was bypassed.                         │
└───────────────────────────────────────────────────────────────────┘
```

---

## 105. Worked example C: adding a GEPA-like reflective loop to Coinvault

### 105.1 Motivation

The current outer loop is human-driven. A GEPA-like optimizer automates proposal generation from rich trajectories while retaining candidate validation, paired evaluation, hidden promotion, and human deployment authority.

### 105.2 What changes and what does not

Unchanged:

```text
snapshot and patch model
Coinvault materializer
canonical product execution
trajectory capture
JudgeKit instruments
paired comparison
lexicographic selection
hidden validation
human deployment review
```

New:

```text
reflection packet selector
LLM reflector
structured candidate proposer
Pareto archive/search policy
proposal budget
```

### 105.3 Reflection packet

The packet should be small enough to inspect and must cite exact evidence.

```yaml
schema: optkit.reflection-packet/v1
campaign: cmp_...
incumbent: sha256:...
allowed_variables:
  - coinvault.answer.grounding_prompt
  - coinvault.answer.routing_prompt
  - coinvault.answer.policy_prompt
  - coinvault.knowledge.tool_description

selected_episodes:
  - episode_id: ep_route_failure_1
    reason: hard route contract failed
    evidence:
      - trajectory-window: model decision through first tool result
      - contract-report
      - incumbent/challenger pair diff
  - episode_id: ep_target_success_1
    reason: preserve successful grounding behavior
    evidence:
      - final answer
      - evidence ledger
      - judge assessment

archive_summary:
  - candidate: cand_grounded_answer_v2
    target_faithfulness_delta: 0.5621
    hard_failures: 5
  - candidate: cand_routing_v1
    target_faithfulness_delta: 0.4210
    hard_failures: 1

remaining_budget:
  proposals: 4
  answer_calls: 96
  judge_calls: 32
```

### 105.4 Reflector output

```yaml
schema: optkit.reflection/v1
diagnosis: >-
  The challenger preserves strong evidence-grounded synthesis when knowledge
  retrieval occurs, but the routing prompt still permits SQL-only resolution
  for questions whose comparison criteria require catalog knowledge.
cited_evidence:
  - ep_route_failure_1#events/4-11
  - ep_target_success_1#answer
responsible_variables:
  - coinvault.answer.routing_prompt
proposal:
  changes:
    - variable: coinvault.answer.routing_prompt
      operation: replace_asset
      value_artifact: sha256:new-routing-prompt
hypothesis:
  claim: >-
    Explicitly classifying comparison requests with mixed catalog and database
    needs will reduce forbidden SQL-only routes while preserving grounding.
  targets:
    - construct: contract.route-compliance
      groups: [comparison, mixed_sql_knowledge]
risks:
  - unnecessary knowledge calls on SQL-sufficient questions
confidence: 0.72
```

### 105.5 Proposal validation

The core checks:

```text
✓ cited episodes are development-accessible
✓ routing prompt is allowed
✓ one variable changed
✓ new asset resolves and fits size limit
✓ evaluator configuration unchanged
✓ validation examples not referenced
✓ remaining proposal/call budgets sufficient
```

Only then is the candidate admitted.

### 105.6 Archive behavior

Suppose candidate A has stronger faithfulness but more cost, while B has fewer hard failures but a smaller target improvement. Neither dominates the other:

\[
A\not\succ B,\qquad B\not\succ A.
\]

Both remain in the search archive, giving the reflector different successful behaviors to learn from. Promotion still uses the conservative lexicographic policy.

### 105.7 Live UI

```text
┌ Reflective optimization / round 3 ────────────────────────────────────────────┐
│ Budget: proposals 2/6   answer calls 128/216   judge calls 39/72             │
├───────────────────┬───────────────────────────────────────────────────────────┤
│ ARCHIVE           │ REFLECTION                                                 │
│ A grounding-v2    │ Diagnosis: routing prompt permits SQL-only resolution ... │
│ B routing-v1      │ Evidence: ep_route_failure_1 [open]                       │
│ C tool-desc-v2    │           ep_target_success_1 [open]                      │
│                   │ Proposed var: answer.routing_prompt                       │
│ Pareto: A, B      │ Confidence: 0.72                                           │
├───────────────────┴───────────────────────────────────────────────────────────┤
│ NEW CANDIDATE routing-v2                                                      │
│ status: awaiting human proposal approval                                     │
│ [view patch] [view evidence packet] [approve evaluation] [reject proposal]   │
└───────────────────────────────────────────────────────────────────────────────┘
```

In early releases, a human should approve reflective proposals before provider-backed evaluation. Later, low-risk development-stage evaluation can be automatic while promotion remains separately controlled.

---

## 106. Worked example D: porting `rag-ttc` paired tool evaluation

### 106.1 Motivation

The TTC tool-eval path resembles Coinvault enough to reuse paired trial machinery, but its product variables and trace semantics are different. This example validates that the core does not encode Coinvault assumptions.

### 106.2 Variable registry

```go
func RegisterTTCVariables(r *space.Registry) {
    r.MustRegister(space.Text("ttc.agent.system_prompt", space.MaxBytes(64<<10)))
    r.MustRegister(space.Text("ttc.tool.search.description", space.MaxBytes(16<<10)))
    r.MustRegister(space.Int("ttc.retrieval.top_k", space.Range(1, 100)))
    r.MustRegister(space.Choice("ttc.retrieval.reranker", []string{
        "none", "cross-encoder-v1", "llm-listwise-v1",
    }))
    r.MustRegister(space.JSON("ttc.agent.tool_policy", "ttc.tool-policy/v1"))
}
```

### 106.3 Materializer

The existing `materializeToolConfig` logic should be decomposed into:

```text
resolve semantic snapshot
      ↓
render typed TTC runtime config
      ↓
write immutable materialization root
      ↓
validate config with product loader
      ↓
return manifest + runtime ref
```

Avoid generating YAML through ad hoc string concatenation. Construct typed configuration values and serialize them through the canonical product codec.

```go
func (m *Materializer) Materialize(ctx context.Context, s model.Snapshot) (...) {
    cfg := ttcconfig.Config{
        Agent: ttcconfig.Agent{
            SystemPrompt: m.Assets.MustText(s.TextDigest("ttc.agent.system_prompt")),
            ToolPolicy:   decodePolicy(s.JSON("ttc.agent.tool_policy")),
        },
        Retrieval: ttcconfig.Retrieval{
            TopK:     s.Int("ttc.retrieval.top_k"),
            Reranker: s.Choice("ttc.retrieval.reranker"),
        },
    }
    // Serialize, validate through current loader, and record manifest.
}
```

### 106.4 System adapter

```go
func (s *ToolLoopSystem) Execute(
    ctx context.Context,
    req runtime.Request,
) (runtime.Result, error) {
    rt, err := chatpkg.NewRuntime(ctx, req.Materialized.RuntimeRef)
    if err != nil { return runtime.Result{}, classify(err) }

    recorder := NewTrajectoryRecorder(req.Sink)
    result, err := rt.RunToolLoop(ctx, decodeToolEvalCase(req.Case), recorder)
    if err != nil { return runtime.Result{}, classify(err) }

    return runtime.Result{
        Output:       artifact.FromJSON(result.Answer),
        NativeTrace:  recorder.NativeRecordRef(),
        ResourceUsage: recorder.Usage(),
    }, nil
}
```

The exact current canonical runtime should be called rather than duplicating tool-loop logic inside the adapter.

### 106.5 Measurements

The existing `answerquality.JudgeToolLoop` can first be wrapped as one legacy instrument:

```go
type LegacyAnswerQualityInstrument struct {
    Judge answerquality.JudgeToolLoop
}
```

Then decompose it over time into JudgeKit constructs such as:

```text
answer.correctness
answer.evidence-groundedness
tool.route-correctness
tool.argument-validity
retrieval.evidence-coverage
answer.citation-validity
```

The migration should not change values and schemas in the same cutover. First wrap, establish parity, then improve the measurement model in a new protocol epoch.

### 106.6 Paired comparison

The same exact block identity works:

\[
\Delta_{i,r}=m(\tau_{i,r,candidate})-m(\tau_{i,r,incumbent}).
\]

TTC can reuse core pair tables, win/loss counts, aggregates, and selection stages while supplying its own measurements and hard predicates.

### 106.7 UI extension

Generic tiles show campaign, patch, progress, pair deltas, and decisions. TTC-specific tiles show:

```text
retrieval candidate provenance
tool-call sequence
chunk/source preview
index/bundle identity
answer-to-source linkage
```

Shared selection means clicking a failed pair in the generic comparison tile selects the episode, which updates the TTC provenance tile without custom page wiring.

```text
┌ Pair table ──────────────────┐       ┌ TTC provenance ─────────────────────┐
│ case-17  Δquality -0.22  ◀───┼──────▶│ selected: case-17/challenger        │
│ case-18  Δquality +0.10      │       │ query → chunks → reranker → answer  │
└──────────────────────────────┘       └─────────────────────────────────────┘
```

---

## 107. Worked example E: TTC multi-arm chunking experiment

### 107.1 Motivation

This example explains why OptKit cannot define every trial as incumbent/challenger. Indexing and retrieval experiments often compare several configurations against the same corpus and query set.

### 107.2 Search space

Let:

\[
\Theta_{chunker}
=
\Theta_{kind}
\times
\Theta_{size}
\times
\Theta_{overlap}.
\]

Candidate arms:

```text
A: recursive,  500 tokens,  50 overlap
B: recursive,  800 tokens,  80 overlap
C: semantic,   target 600,  max 1000
D: heading,    max 900,     fallback recursive
```

### 107.3 Plan

```yaml
schema: optkit.plan/v1
name: ttc-chunker-comparison
system:
  kind: rag-ttc-retrieval/v1

stages:
  - id: build-indexes
    kind: materialization
    arms: [A, B, C, D]
    corpus: ttc://corpus/epoch-2026-08-01

  - id: evaluate-retrieval
    kind: evaluation
    depends_on: [build-indexes]
    data:
      dataset: ttc://retrieval-benchmark/v3
      role: development
    design:
      kind: randomized-block-multiarm
      block_by: query_id
      arms: [A, B, C, D]
      repeats: 3
    measurements:
      - retrieval.recall_at_10
      - retrieval.mrr
      - retrieval.context-redundancy
      - indexing.chunk-count
      - indexing.wall-time
      - storage.vector-bytes
    selection:
      kind: pareto-then-review
      objectives:
        maximize: [retrieval.recall_at_10, retrieval.mrr]
        minimize: [retrieval.context-redundancy, storage.vector-bytes]
      hard:
        - indexing.success_rate == 1
```

### 107.4 Assignments

For 100 queries, 4 arms, and 3 repeats:

\[
100\times4\times3=1200
\]

retrieval assignments, plus four index materializations.

The index build is an upstream reusable artifact. Each retrieval assignment references the exact index manifest digest.

### 107.5 Measurement matrix

```text
query   repeat   A recall   B recall   C recall   D recall
q001      0        1.0        1.0        0.8        1.0
q001      1        1.0        1.0        1.0        1.0
q001      2        1.0        0.8        1.0        1.0
q002      0        0.6        0.8        0.8        0.6
...
```

The comparator can compute pairwise contrasts against a designated baseline, all pairwise contrasts, or model-based arm effects. The authoritative record must state which comparison definition was used.

### 107.6 Pareto archive

Suppose:

```text
A: recall .82, MRR .61, redundancy .28, vectors 1.0 GB
B: recall .86, MRR .64, redundancy .34, vectors 0.8 GB
C: recall .88, MRR .66, redundancy .22, vectors 1.5 GB
D: recall .84, MRR .65, redundancy .19, vectors 0.9 GB
```

No single arm is best on every objective. C has the best recall/MRR but highest storage. D has low redundancy and moderate storage. Both may remain Pareto-optimal.

```text
┌ Chunking Pareto archive ──────────────────────────────────────────────────────┐
│ ARM │ recall@10 │ MRR  │ redundancy ↓ │ vectors ↓ │ STATUS                  │
├─────┼───────────┼──────┼──────────────┼───────────┼─────────────────────────┤
│ A   │ .82       │ .61  │ .28          │ 1.0 GB    │ dominated by D          │
│ B   │ .86       │ .64  │ .34          │ 0.8 GB    │ Pareto                  │
│ C   │ .88       │ .66  │ .22          │ 1.5 GB    │ Pareto                  │
│ D   │ .84       │ .65  │ .19          │ 0.9 GB    │ Pareto                  │
├───────────────────────────────────────────────────────────────────────────────┤
│ Selected B: why Pareto? lowest storage; higher recall than A.                │
│ [compare B↔C] [compare B↔D] [open failed queries]                            │
└───────────────────────────────────────────────────────────────────────────────┘
```

Deployment/promotion may still choose D because product policy prefers low redundancy and bounded storage. The archive preserves C as evidence of a different trade-off.

---

## 108. Worked example F: TTC factorial retrieval experiment

### 108.1 Motivation

One-variable-at-a-time experiments provide attribution but can miss interactions. Chunk size and retrieval depth may jointly affect quality.

Suppose variables are:

\[
K\in\{5,10\}
\]

for top-k, and

\[
R\in\{\text{none},\text{cross-encoder}\}
\]

for reranking.

A \(2\times2\) factorial design evaluates:

```text
A: k=5,  reranker=none
B: k=10, reranker=none
C: k=5,  reranker=cross-encoder
D: k=10, reranker=cross-encoder
```

### 108.2 Main and interaction effects

For outcome \(Y\), the top-k main effect is roughly:

\[
\operatorname{Effect}(K)
=
\frac{Y_B+Y_D}{2}
-
\frac{Y_A+Y_C}{2}.
\]

The reranker main effect is:

\[
\operatorname{Effect}(R)
=
\frac{Y_C+Y_D}{2}
-
\frac{Y_A+Y_B}{2}.
\]

The interaction asks whether the effect of increasing \(K\) depends on the reranker:

\[
\operatorname{Interaction}(K,R)
=
(Y_D-Y_C)-(Y_B-Y_A).
\]

A large interaction means coordinate experiments are insufficient to predict the joint candidate.

### 108.3 OptKit representation

This is still a trial design over four snapshots. No new episode or measurement concepts are needed. Only the comparator changes.

```go
type FactorialComparator struct {
    Factors []Factor
    Model   EffectModel
}
```

This demonstrates the value of separating trial design/comparison from the product executor.

---

## 109. Worked example G: remeasure old Coinvault episodes with a new judge

### 109.1 Motivation

Suppose JudgeKit faithfulness protocol v11 fixes a defect in comparison-claim decomposition. Rerunning 24 expensive Coinvault episodes is unnecessary if their answers, evidence ledgers, and audit inputs are already preserved.

### 109.2 Open a new measurement epoch

```text
measurement.epoch.opened
  construct: answer.faithfulness
  protocol: sha256:faithfulness-v11
  source episodes: feedback run 2026-08-...
```

### 109.3 Remeasure

Each v11 record references the same episode but a new protocol and judge execution.

```text
episode ep_001
  faithfulness/v10 = 0.4595
  faithfulness/v11 = 0.5120

episode ep_002
  faithfulness/v10 = 1.0000
  faithfulness/v11 = 0.9700
```

### 109.4 Recompute a comparison in the new epoch

The old decision remains historical. A new comparison can answer:

> What would the paired result be under v11?

It must not rewrite the prior gate decision. Instead it produces a new analysis linked to that historical decision.

### 109.5 UI

```text
┌ Measurement epochs ───────────────────────────────────────────────────────────┐
│ Construct: answer.faithfulness                                                │
├──────────┬──────────────┬──────────┬─────────┬────────────────────────────────┤
│ Epoch    │ Protocol     │ Episodes │ Status  │ Use                            │
├──────────┼──────────────┼──────────┼─────────┼────────────────────────────────┤
│ v10      │ sha256:aaa   │ 24       │ sealed  │ historical decision authority │
│ v11      │ sha256:bbb   │ 24       │ sealed  │ reanalysis                    │
├───────────────────────────────────────────────────────────────────────────────┤
│ Mean v11-v10: -0.04   rank correlation: .82                                  │
│ [view disagreements] [compare gate under v11]                                │
└───────────────────────────────────────────────────────────────────────────────┘
```

---

## 110. Worked example H: deployment and rollback lineage

### 110.1 Motivation

Optimization is incomplete if the evidence cannot be connected to what actually reached production.

### 110.2 Promotion record

```yaml
schema: optkit.review/v1
candidate: cand_routing_v3
snapshot: sha256:promoted-snapshot
selection_evidence: comparison_...
reviewer: alice
role: coinvault-promotion-reviewer
decision: approve
rationale: >-
  Passed feedback, fresh-root reproduction, and hidden validation with no hard
  contract failures. Cost increase is within policy.
```

### 110.3 Deployment command outside the core

Coinvault's deployment system applies the approved snapshot and returns an environment-specific deployment identity:

```text
coinvault-prod deployment cv-prod-2026-08-20.3
```

OptKit records:

```yaml
schema: optkit.deployment-record/v1
environment: coinvault-production
snapshot: sha256:promoted-snapshot
external_deployment_id: cv-prod-2026-08-20.3
applied_at: 2026-08-20T...
verification:
  observed_snapshot_digest: sha256:promoted-snapshot
  status: match
```

### 110.4 Rollback

If online evidence later requires rollback, record the rollback and its reason. Do not erase promotion history.

```text
promoted snapshot
      ↓ deployment-record
production deployment
      ↓ online incident evidence
rollback-record
      ↓
previous production snapshot
```

The history UI can now answer which optimization evidence justified a production version and why it was later reversed.

---
EOF
```

```unknown
bash -lc wc -l -w -c /mnt/data/optkit-architecture-and-migration-guide.md
```

```unknown
bash -lc grep -n -i -E 'denotational|operational semantics|Markov|POMDP|category' /mnt/data/optkit-architecture-and-migration-guide.md | head -n 50
```

```unknown
bash -lc grep '^#' /mnt/data/optkit-architecture-and-migration-guide.md | head -n 220
```

```unknown
bash -lc grep '^#' /mnt/data/optkit-architecture-and-migration-guide.md | sed -n '220,520p'
```

<details><summary>💭 Thinking</summary>

**Appended Part VIII examples and reviewed document structure and counts**

</details>

```unknown
bash -lc cat >> /mnt/data/optkit-architecture-and-migration-guide.md <<'EOF'
# Part IX — Mathematical foundations and glossary

This part gathers the mathematical ideas used throughout the design. None of them is required to write a first adapter, but together they explain why the architecture has its particular boundaries.

---

## 111. Denotational and operational views of an optimized system

### Motivation

Two engineers can describe the same Coinvault candidate in very different ways:

- “It maps a question to a distribution over answers and traces.”
- “It loaded this prompt, called this tool, retrieved these chunks, and emitted this answer.”

Both descriptions are correct, but they answer different questions.

### Definition — denotational view

A denotational view describes **what observable behavior a system means**, abstracting away implementation steps.

For a snapshot \(\theta\), write:

\[
\llbracket S_\theta\rrbracket : X \rightsquigarrow \mathcal T
\]

where \(X\) is the space of cases and \(\mathcal T\) is the space of complete trajectories. The squiggly arrow indicates stochastic behavior: the same input may yield different trajectories.

Equivalently:

\[
\llbracket S_\theta\rrbracket(x)=P_\theta(\tau\mid x).
\]

This view is useful for optimization because the objective depends on the distribution of outcomes, not on a particular Go call graph.

### Definition — operational view

An operational view describes **how execution proceeds** through states and transitions.

\[
s_0\xrightarrow{a_0/o_1}s_1
\xrightarrow{a_1/o_2}\cdots
\xrightarrow{a_T}s_{T+1}.
\]

For Coinvault, states include conversation history and runtime context; actions include text or tool calls; observations include tool results and retrieved evidence.

This view is useful for:

```text
live visualization
debugging
intervention checks
credit assignment
retry and cancellation semantics
```

### Why OptKit needs both

The snapshot and system interfaces provide the denotational boundary:

```text
case + snapshot → distribution over possible episodes
```

The trajectory journal provides the operational evidence:

```text
this exact episode followed these transitions
```

A framework that stores only final scores loses operational diagnosis. A framework that stores only low-level events lacks a stable basis for comparison and selection.

---

## 112. Stochastic kernels and compositional agent systems

### Motivation

Coinvault and TTC are compound systems. Retrieval feeds an answer model; tool calls feed later model turns; rendering follows widget intent. We need a mathematical way to say that stochastic components compose.

### Definition — Markov kernel

A Markov kernel \(K:X\rightsquigarrow Y\) assigns to every input \(x\in X\) a probability distribution over outputs in \(Y\).

For a language model:

\[
K_{LM}(h,\cdot)=P(\text{next action}\mid h).
\]

For retrieval with nondeterministic infrastructure or tie-breaking:

\[
K_R(q,\cdot)=P(\text{retrieval result}\mid q).
\]

### Composition

If

\[
K:X\rightsquigarrow Y
\]

and

\[
L:Y\rightsquigarrow Z,
\]

their composite is:

\[
(L\circ K)(x,A)
=
\int_Y L(y,A)K(x,dy).
\]

In plain language:

1. sample an intermediate \(y\) using \(K\);
2. use \(y\) to sample \(z\) using \(L\);
3. integrate over all possible intermediate values.

### Coinvault example

A simplified one-turn system is:

\[
X
\xrightsquigarrow{K_{route}}
A
\xrightsquigarrow{K_{tool}}
O
\xrightsquigarrow{K_{answer}}
Y.
\]

Changing a routing prompt changes \(K_{route}\). Changing retrieval depth changes part of \(K_{tool}\). Changing grounding instructions changes \(K_{answer}\).

This explains why a patch can have downstream effects even when only one coordinate changes.

### Multi-turn feedback

A multi-turn agent repeatedly composes its policy with an environment kernel:

\[
h_t
\xrightsquigarrow{\pi_\theta}
a_t
\xrightsquigarrow{P_{env}}
o_{t+1}
\longrightarrow h_{t+1}.
\]

The complete loop induces the trajectory distribution \(P_\theta(\tau\mid x)\).

> **Callout — Why no Markov-kernel types in the Go API?**
>
> The mathematics explains the semantics, but a public `MarkovKernel[X,Y]` interface would not automatically solve materialization, traces, errors, streaming, or provider effects. OptKit uses ordinary Go interfaces while preserving the same conceptual boundary.

---

## 113. Interventions and causal attribution

### Motivation

Optimization asks what would happen under a changed configuration. That is an intervention question, not merely a correlation question.

### Definition — intervention

A patch \(\delta\) transforms a parent snapshot:

\[
\theta'=\theta\oplus\delta.
\]

A controlled experiment attempts to estimate:

\[
E[M(\tau_{\theta'})-M(\tau_\theta)].
\]

### One-coordinate intervention

When

\[
|\operatorname{supp}(\delta)|=1,
\]

only one declared variable changes. This improves attribution but does not guarantee that every downstream behavior remains equal—the point of the experiment is to observe those downstream effects.

### Manipulation check

An intervention check verifies that the intended mechanism was exercised:

\[
I(\tau,\delta)\in\{0,1\}.
\]

For Coinvault default results, a configuration change may be bypassed by an explicit tool argument. Then \(I=0\), and the episode is not evidence about the causal effect of the intended retrieval-depth change.

### Potential-outcome interpretation

For case \(i\), imagine potential outcomes:

\[
Y_i(0),Y_i(1)
\]

under incumbent and challenger. We cannot observe both in the exact same stochastic world, but paired repeated execution estimates their difference under controlled conditions:

\[
\Delta_i=Y_i(1)-Y_i(0).
\]

Random seeds, provider drift, and temporal effects complicate this idealization. Trial design and repeats reduce, but do not eliminate, those uncertainties.

### Why the patch is not the whole causal model

Hidden product state can break attribution. For example:

```text
mutable external index
unversioned model alias
changing corpus
clock-dependent prompt
shared conversation state
```

That is why every output-affecting resource needs an immutable identity or explicit environment epoch.

---

## 114. Experimental design and statistical comparison

### Motivation

Executing candidates is not enough. How cases, arms, repeats, and stages are assigned determines what claims the results support.

### Paired design

Each block uses the same case and repeat identity for incumbent and challenger:

\[
\Delta_{i,r}=M(\tau_{i,r,1})-M(\tau_{i,r,0}).
\]

This controls for stable case difficulty.

### Multi-arm randomized block design

For arm \(a\) and block \(i\):

\[
Y_{i,a}=\mu+\alpha_a+\beta_i+\epsilon_{i,a}.
\]

Here \(\alpha_a\) is the arm effect and \(\beta_i\) captures query/case difficulty. The design need not fit this exact linear model, but it illustrates why shared blocks help.

### Repeats

Repeats estimate stochastic variability:

\[
\bar Y_{i,a}=\frac1R\sum_{r=1}^R Y_{i,a,r}.
\]

One repeat is often useful for cheap iteration but weak for uncertainty claims. Promotion stages can use more repeats or larger hidden sets.

### Bootstrap uncertainty

For paired deltas \(\Delta_1,\ldots,\Delta_n\), resample cases with replacement and recompute the aggregate. Quantiles of the bootstrap distribution approximate an interval for the case-distribution effect.

The resampling unit must match the independence structure. If several rows belong to one conversation or document, resample the higher-level cluster instead of pretending each row is independent.

### Adaptive search warning

Selecting the best of many candidates on the same development set introduces winner's-curse/selection bias. A normal confidence interval computed after selection does not account for the search over candidates.

OptKit mitigates this structurally through:

```text
separate development and promotion roles
exposure accounting
fresh-root reproduction
hidden validation epochs
explicit campaign history
```

It should not claim that these measures solve every statistical issue automatically.

---

## 115. Measurement theory

### Motivation

“Faithfulness” is not a raw property directly emitted by the program. It is an abstract construct assessed through evidence and a protocol.

### Construct

A **construct** is the property one intends to assess, such as answer faithfulness, route compliance, retrieval coverage, or usefulness.

### Operationalization

A construct is operationalized by specifying:

```text
what evidence is observed
which procedure examines it
which outputs are permitted
how outputs are interpreted
```

For faithfulness:

```text
observable evidence: answer + admitted evidence ledger
procedure: claim decomposition and support judgment
reported value: supported claim ratio or rubric score
```

### Instrument

An instrument is the executable implementation of that operationalization. A deterministic citation checker and an LLM judge are both instruments, with different error characteristics.

### Measurement error

A measured value can be modeled as:

\[
\hat M(\tau)=M^*(\tau)+\epsilon_{protocol}+\epsilon_{judge}+\epsilon_{evidence},
\]

where \(M^*\) is the idealized target and the error terms represent protocol limitations, judge variability, and incomplete evidence.

The equation is explanatory, not a claim that these errors are additive or directly identifiable in practice.

### Measurement epoch

Changing protocol \(\psi\) changes the instrument:

\[
\hat M_{\psi_1}\neq\hat M_{\psi_2}.
\]

Therefore values from different protocol digests are not silently pooled. Remeasurement or calibration supplies evidence about comparability.

### Goodhart's law in this setting

When a proxy measurement becomes the target of aggressive optimization, the optimizer may exploit defects in the proxy rather than improve the intended construct.

Structural mitigations include:

```text
multiple measurements
hard deterministic constraints
protocol calibration
trajectory review
limited optimizer access to promotion measurements
human/production evidence
```

---

## 116. Multi-objective and constrained decision theory

### Motivation

Coinvault must improve answer quality without violating authorization, citations, routing contracts, or budgets. A weighted sum can make an unsafe regression appear acceptable.

### Feasible set

Hard constraints define:

\[
\mathcal F=\{\theta:g_j(\theta)\le0\ \forall j\}.
\]

Only feasible candidates are eligible for target comparison.

### Vector objective

\[
J(\theta)=
(J_{faithfulness},J_{relevance},-J_{cost},\ldots).
\]

### Pareto dominance

Candidate \(a\) dominates \(b\) if:

\[
J_k(a)\ge J_k(b)\quad\forall k
\]

and the inequality is strict for at least one objective.

Pareto search preserves distinct trade-offs. Product selection can then apply policy preferences.

### Lexicographic decision

A lexicographic selector evaluates ordered stages:

\[
G_1\prec G_2\prec\cdots\prec G_m.
\]

A failure at stage \(j\) cannot be compensated by any result at a later stage.

Coinvault's pattern is:

```text
identity/completeness
→ hard product constraints
→ target improvement
→ regression limits
→ cost
→ human promotion
```

This is not merely a UI ordering; it is the decision semantics.

---

## 117. Event sourcing as an algebraic fold

### Motivation

Plan, live, and history screens must agree. Reconstructing them from one immutable history prevents each screen from inventing its own truth.

### Event stream

Let \(E^*\) denote finite sequences of valid events. Concatenation \(\cdot\) and the empty sequence \(\epsilon\) form a monoid:

\[
(E^*,\cdot,\epsilon).
\]

### State fold

A reducer applies events to state:

\[
\operatorname{fold}:S\times E^*\to S.
\]

It satisfies:

\[
\operatorname{fold}(s,\epsilon)=s
\]

and

\[
\operatorname{fold}(s,u\cdot v)
=
\operatorname{fold}(\operatorname{fold}(s,u),v).
\]

This is why replay can process events in chunks without changing the result.

### Projection

Each UI read model is another fold over the same stream:

\[
P_k:E^*\to V_k.
\]

Different projections answer different questions while sharing source facts.

### Prefix stability

If \(u\) is a prefix of \(u\cdot v\), then the interpretation of facts in \(u\) does not change. Later events may add a rollback or superseding decision, but do not rewrite the earlier promotion.

### Hash chain

If each event digest includes the previous event digest:

\[
d_i=H(d_{i-1},\operatorname{canonical}(e_i)),
\]

then unexpected historical mutation becomes detectable.

---

## 118. Category-theoretic perspective, kept optional

### Motivation

The architecture is compositional, and category theory provides a compact language for composition. It should clarify design laws, not dictate awkward APIs.

### Systems as morphisms

Deterministic components look like functions:

\[
X\to Y.
\]

Stochastic components look like Markov kernels:

\[
X\rightsquigarrow Y.
\]

They compose associatively, which explains why independently implemented routing, retrieval, and answer components can form one system semantics.

### Measurements as observers

A measurement instrument maps trajectories to measurement records:

\[
\mathcal T\rightsquigarrow\mathcal M.
\]

A deterministic instrument is a special case.

### Product composition

Parallel independent evaluations resemble a monoidal product:

\[
S_{\theta_1}\otimes S_{\theta_2}.
\]

In implementation terms, this supports running arms or cases concurrently while preserving their identities.

### Why OptKit is not a category-theory framework

The important engineering laws are concrete:

```text
composition preserves types
identities are stable
replay is deterministic
observers do not silently mutate execution
constraints compose explicitly
```

These can be tested directly. Category theory is useful as an explanatory backbone, but product engineers should not need to understand Kleisli categories to add a prompt variable.

---

## 119. Glossary

### Actor

A human, service, or model agent that issues commands or produces events. Actors have identities and access grants.

### Adaptive phase

A plan stage whose exact future candidates or trials depend on evidence produced during the campaign. The plan specifies the decision policy and bounds rather than pretending to know every future node.

### Arm

One system snapshot or policy assigned within a trial. In paired Coinvault trials, the arms are incumbent and challenger. In a TTC multi-arm trial, there may be four chunking configurations.

### Archive

A retained set of candidates and evidence used by an optimizer. A Pareto archive retains undominated candidates rather than only one scalar winner.

### Artifact

An immutable data object stored outside the compact event payload, identified by digest. Examples include prompts, native traces, answers, evidence ledgers, judge audits, and rendered reports.

### Assignment

The smallest scheduled executable unit: one arm, one case, one repeat, one environment specification, and one intended episode.

### Budget

A finite admitted quantity of a named resource, such as model calls, tokens, dollars, time, or proposals. Budgets are constraints on campaign execution, not after-the-fact labels.

### Campaign

The durable optimization process containing a compiled plan, candidates, trials, episodes, measurements, comparisons, decisions, resources, exposure history, and lineage.

### Candidate

A proposed child snapshot plus its parent, typed patch, hypothesis, expected effects, risks, and provenance.

### Case

One evaluable input and its metadata. A case may contain a user question, document/query pair, tool-loop task, or indexing workload.

### Command

A request to change campaign state, such as “start campaign” or “submit candidate.” A command may be rejected. Accepted commands produce events.

### Comparator

A component that transforms compatible measurements into contrasts, aggregates, uncertainty summaries, and comparison artifacts.

### Comparison

A derived statistical artifact relating arms or candidates under an explicit comparison definition. It is not raw execution evidence.

### Constraint

A predicate or bounded quantity that determines validity or eligibility. Hard constraints are not compensable by soft improvements.

### Construct

An abstract property intended to be assessed, such as faithfulness, relevance, route correctness, or evidence coverage.

### Control plane

The machinery that plans, records, coordinates, reviews, and visualizes optimization. Product runtimes remain in the data/execution plane.

### Data role

The declared purpose and access policy of a dataset, such as development, calibration, reproduction, hidden promotion, or online shadow.

### Decision

A recorded result of applying a selection policy and possibly human authority to evidence. Examples include reject, advance to reproduction, promote, or request more evidence.

### Deployment record

A link between an approved semantic snapshot and an external product deployment identity, including verification of the observed digest.

### Digest

A content-derived identifier, usually cryptographic, used to detect changed bytes and give immutable objects stable identities.

### Domain

The valid set of values for a variable, such as integers from 1 to 20, a finite model choice, or text satisfying a size/schema constraint.

### Episode

One realized execution of an assignment, including its input, normalized trajectory, output, native artifacts, resource usage, and terminal status.

### Event

An immutable fact that occurred, recorded in past tense and appended to the journal.

### Exposure

The fact that an actor received access to particular examples, labels, detailed feedback, or evidence. Exposure is irreversible historical information.

### Gate

A selection policy, often lexicographic, that evaluates evidence against ordered hard and soft criteria.

### Hypothesis

A falsifiable claim attached to a candidate describing why a patch is expected to affect specific measurements and what regressions may occur.

### Incumbent

The reference snapshot currently treated as the baseline or selected system for a campaign stage.

### Instrument

An executable procedure that operationalizes a construct over evidence and produces a typed measurement.

### Intervention check

An instrument that verifies whether the candidate's intended changed mechanism actually affected the episode's runtime path.

### Journal

The append-only authoritative sequence of campaign events.

### Lease

A time-bounded, exclusive authorization for one worker to execute or commit an assignment attempt.

### Lineage

The directed parent/patch/child relationships among snapshots and candidates, extended through decisions and deployments.

### Materialization

The product-owned process of turning a semantic snapshot into executable files, configuration, indexes, or runtime references.

### Measurement

A typed observation produced by an identified instrument/protocol over identified evidence. It includes applicability, provenance, and possibly uncertainty—not merely a float.

### Measurement contract

The specification of evidence, procedure, output space, applicability, and interpretation used to operationalize a construct.

### Measurement epoch

A period or set of measurements sharing one protocol identity and intended interpretation. Changing the protocol creates a new epoch unless a deliberate compatibility rule says otherwise.

### Objective

A measurement or derived quantity that an optimizer seeks to improve. Objectives may be vector-valued and remain subject to constraints.

### Optimizer

A policy that proposes candidates from permitted campaign history, search space, archive, and remaining budget.

### Pareto frontier

The set of candidates not dominated by another candidate under configured objectives.

### Patch

An immutable typed difference from a parent snapshot to a child snapshot.

### Plan

The immutable specification of system kind, search space, data roles, trial designs, measurements, budgets, stages, access rules, stop rules, and selection policies.

### Projection

A rebuildable query/read model derived from the journal for a particular UI or operational question.

### Promotion

A decision that advances a candidate to a more authoritative stage or makes it the next incumbent. Promotion is distinct from deployment.

### Protocol

The versioned procedure and evaluator configuration used by an instrument. Its digest is part of measurement provenance.

### Reflector

A component, human or model-based, that diagnoses trajectory/evaluation evidence and proposes responsible variables or candidate changes.

### Repeat

A repeated execution of the same case/arm block used to observe stochastic variation.

### Remeasurement

Applying a new or repeated instrument protocol to an existing sealed episode without rerunning the product system.

### Replay

Reconstructing campaign state or projections by folding the immutable journal from a known starting point.

### Search space

The typed set \(\Theta\) of valid semantic system configurations available to a campaign.

### Selector

A policy that consumes evidence and produces an advance/reject/review recommendation. It is separate from the optimizer that proposes candidates.

### Snapshot

A complete immutable semantic configuration sufficient, with its declared environment references, to identify the intended product behavior.

### Span

A bounded interval of work in a trajectory, often with parent/child causal relationships, such as one model call or tool call.

### System

A product adapter implementing execution of cases under materialized snapshots and emitting trajectories/artifacts.

### Trajectory

The ordered and causally linked observations of what happened during an episode: model calls, tool calls, retrieval, state transitions, outputs, and product-specific events.

### Trial

A designed collection of arms, cases, repeats, assignment rules, and comparison intent.

### Variable

A named typed coordinate of the search space with a domain, semantic meaning, and product materializer.

### Widget intent

An agent action requesting a structured visual representation. It is separate from the rendered widget artifact produced by the UI environment.

---
EOF
```

```unknown
bash -lc wc -l -w -c /mnt/data/optkit-architecture-and-migration-guide.md
```

The design is now complete and render-checked, including campaign-journal UI projections, remeasurement epochs, phased migrations, concrete tooling, parity tests, safety rules, worked examples, and intern-ready milestones.

# OptKit design and migration guide

[Download the complete Markdown document](sandbox:/mnt/data/optkit-design-and-migration-guide.md)

The document is a self-contained, implementation-oriented design covering:

- The mathematical model behind Coinvault’s current optimization loop: configurations, patches, trajectories, intervention checks, constraints, measurements, estimands, paired estimates, archives, and lexicographic decisions.
- A domain-neutral OptKit architecture with explicit boundaries from FlowKit, JudgeKit, RagKit, RagOpt, Coinvault, and RAG-TTC.
- Content-addressed snapshots and artifacts, event-sourced campaign history, state machines, crash recovery, budgets, exposure control, measurement epochs, and native trajectory custody.
- Go API sketches, package structure, schemas, controller pseudocode, event catalogs, identity equations, and storage layout.
- Plan, live, historical, lineage, episode, Pareto, exposure, and deployment-ancestry UIs, including ASCII wireframes and HTTP/SSE projection interfaces.
- Detailed porting plans for RagOpt, RAG-TTC, and Coinvault, including compatibility adapters, parity fixtures, migration phases, and deprecation sequencing.
- A concrete implementation inventory and phased pull-request plan suitable for an intern or small engineering team.
- Worked Coinvault, RAG-TTC, GEPA-style reflection, widget-generation, and judge-remeasurement examples.
- Testing, safety, operational runbooks, review checklists, glossary, source map, and research context.

The final reader pass consolidated the structure, added missing operational definitions, corrected cross-references, and verified that the Markdown parses successfully.


---

> make a pdf as well.

```unknown
bash -lc cat /home/oai/skills/pdfs/SKILL.md && printf '\n---FILES---\n' && ls -l /mnt/data/optkit-design-and-migration-guide.md
```

<details><summary>💭 Thinking</summary>

**Read PDF creation instructions**

</details>

I’ll render the existing Markdown into a PDF, then verify the page renders for clipping, broken math, and layout problems.

```unknown
bash -lc cat /home/oai/skills/pdfs/tasks/convert.md | sed -n '1,220p'; printf '\n---CREATE---\n'; cat /home/oai/skills/pdfs/tasks/create.md | sed -n '1,220p'
```

```unknown
bash -lc python /home/oai/skills/pdfs/scripts/md_to_pdf.py /mnt/data/optkit-design-and-migration-guide.md -o /mnt/data/optkit-design-and-migration-guide.pdf --pdf_engine xelatex
```

```unknown
bash -lc nl -ba /mnt/data/optkit-design-and-migration-guide.md | sed -n '620,660p'
```

```unknown
bash -lc grep -n '\\mathcal' /mnt/data/optkit-design-and-migration-guide.md | head -30
```

```unknown
bash -lc pandoc /mnt/data/optkit-design-and-migration-guide.md -s -t latex --resource-path /mnt/data -o /mnt/data/_optkit.tex && grep -n -C 3 '\\mathcal' /mnt/data/_optkit.tex | head -80
```

```unknown
bash -lc python - <<'PY'
from pathlib import Path
src=Path('/mnt/data/optkit-design-and-migration-guide.md').read_text()
out=[]
in_fence=False
for line in src.splitlines(True):
    stripped=line.lstrip()
    if stripped.startswith('```') or stripped.startswith('~~~'):
        in_fence=not in_fence
        out.append(line)
        continue
    if not in_fence:
        line=line.replace(r'\(', '$').replace(r'\)', '$')
        line=line.replace(r'\[', '$$').replace(r'\]', '$$')
    out.append(line)
Path('/mnt/data/_optkit_pdf.md').write_text(''.join(out))
PY
python /home/oai/skills/pdfs/scripts/md_to_pdf.py /mnt/data/_optkit_pdf.md -o /mnt/data/optkit-design-and-migration-guide.pdf --pdf_engine xelatex
```

```unknown
bash -lc fc-match 'DejaVu Sans Mono' | head -1 && fc-match 'DejaVu Serif' | head -1 && fc-match 'Noto Sans Mono' | head -1
```

```unknown
bash -lc fc-list ':charset=2500' family | head -20
```

```unknown
bash -lc sed -n '1,100p' /mnt/data/optkit-design-and-migration-guide.md
```

```unknown
bash -lc rm -f /mnt/data/optkit-design-and-migration-guide.pdf
pandoc /mnt/data/_optkit_pdf.md \
  -o /mnt/data/optkit-design-and-migration-guide.pdf \
  --pdf-engine=xelatex \
  --resource-path=/mnt/data \
  -V mainfont='Noto Sans' \
  -V sansfont='Noto Sans' \
  -V monofont='Noto Sans Mono' \
  -V geometry:margin=0.8in \
  -V fontsize=10pt
```

```unknown
bash -lc python - <<'PY'
from pathlib import Path
p=Path('/mnt/data/_optkit_pdf.md')
s=p.read_text()
repl={'✓':'[OK]','✗':'[X]','👤':'USER','↻':'RETRY'}
for a,b in repl.items(): s=s.replace(a,b)
p.write_text(s)
PY
rm -f /mnt/data/optkit-design-and-migration-guide.pdf
pandoc /mnt/data/_optkit_pdf.md \
  -o /mnt/data/optkit-design-and-migration-guide.pdf \
  --pdf-engine=xelatex \
  --resource-path=/mnt/data \
  -V mainfont='Noto Sans' \
  -V sansfont='Noto Sans' \
  -V monofont='Noto Sans Mono' \
  -V geometry:margin=0.8in \
  -V fontsize=10pt
python /home/oai/skills/pdfs/scripts/pdf_inspect.py /mnt/data/optkit-design-and-migration-guide.pdf | head -80
```

<details><summary>💭 Thinking</summary>

**Converted Markdown to PDF, fixed LaTeX glyphs, and embedded fonts**

</details>

The PDF now compiles cleanly with embedded Unicode-capable fonts and proper math handling. I’m doing the final render check across the 129 pages, especially the dense API tables, equations, and ASCII UI mockups.

```unknown
bash -lc rm -rf /mnt/data/_renders/optkit && mkdir -p /mnt/data/_renders/optkit
python /home/oai/skills/pdfs/scripts/render_pdf.py /mnt/data/optkit-design-and-migration-guide.pdf --out_dir /mnt/data/_renders/optkit --dpi 200
ls /mnt/data/_renders/optkit | wc -l
find /mnt/data/_renders/optkit -type f -printf '%f %s\n' | head
```

```unknown
bash -lc ls -lh /mnt/data/optkit-design-and-migration-guide.pdf; ls /mnt/data/_renders/optkit 2>/dev/null | wc -l; ls /mnt/data/_renders/optkit 2>/dev/null | tail
```

```unknown
bash -lc python /home/oai/skills/pdfs/scripts/render_pdf.py --help | sed -n '1,220p'
```

```unknown
bash -lc python /home/oai/skills/pdfs/scripts/render_pdf.py /mnt/data/optkit-design-and-migration-guide.pdf --out_dir /mnt/data/_renders/optkit --dpi 200 --pages 73-100
```

```unknown
bash -lc python /home/oai/skills/pdfs/scripts/render_pdf.py /mnt/data/optkit-design-and-migration-guide.pdf --out_dir /mnt/data/_renders/optkit --dpi 200 --pages 101-129
```

```unknown
bash -lc python - <<'PY'
from PIL import Image, ImageOps, ImageDraw
from pathlib import Path
files=sorted(Path('/mnt/data/_renders/optkit').glob('page-*.png'))
outdir=Path('/mnt/data/_renders/contact'); outdir.mkdir(exist_ok=True)
cols,rows=4,4
thumb_w=425
for k in range(0,len(files),cols*rows):
    batch=files[k:k+cols*rows]
    thumbs=[]
    for p in batch:
        im=Image.open(p).convert('RGB')
        ratio=thumb_w/im.width
        th=im.resize((thumb_w,int(im.height*ratio)))
        canvas=Image.new('RGB',(thumb_w,th.height+24),'white')
        canvas.paste(th,(0,24))
        d=ImageDraw.Draw(canvas); d.text((5,4),p.stem,fill='black')
        thumbs.append(canvas)
    cell_h=max(i.height for i in thumbs)
    sheet=Image.new('RGB',(cols*thumb_w,rows*cell_h),'white')
    for i,im in enumerate(thumbs):
        sheet.paste(im,((i%cols)*thumb_w,(i//cols)*cell_h))
    sheet.save(outdir/f'contact-{k//16+1:02d}.jpg',quality=88)
print(len(files), 'pages', len(list(outdir.glob('*.jpg'))), 'contact sheets')
PY
ls -lh /mnt/data/_renders/contact | head
```

```unknown
bash -lc find /mnt/data/_renders/optkit -maxdepth 1 -type f -printf '%f\n' | sort | head -100; echo COUNT=$(find /mnt/data/_renders/optkit -maxdepth 1 -type f | wc -l)
```

```unknown
bash -lc rm -rf /mnt/data/_renders/optkit_1_50 /mnt/data/_renders/optkit_51_100; mkdir -p /mnt/data/_renders/optkit_1_50 /mnt/data/_renders/optkit_51_100
python /home/oai/skills/pdfs/scripts/render_pdf.py /mnt/data/optkit-design-and-migration-guide.pdf --out_dir /mnt/data/_renders/optkit_1_50 --dpi 200 --pages 1-50
```

```unknown
bash -lc find /mnt/data/_renders/optkit_1_50 -maxdepth 1 -type f | wc -l; ls /mnt/data/_renders/optkit_1_50 | tail
```

```unknown
bash -lc rm -rf /mnt/data/_renders/optkit_41_80 /mnt/data/_renders/optkit_81_100; mkdir -p /mnt/data/_renders/optkit_41_80 /mnt/data/_renders/optkit_81_100
python /home/oai/skills/pdfs/scripts/render_pdf.py /mnt/data/optkit-design-and-migration-guide.pdf --out_dir /mnt/data/_renders/optkit_41_80 --dpi 200 --pages 41-80
```

```unknown
bash -lc python /home/oai/skills/pdfs/scripts/render_pdf.py /mnt/data/optkit-design-and-migration-guide.pdf --out_dir /mnt/data/_renders/optkit_81_100 --dpi 200 --pages 81-100
```

```unknown
bash -lc python - <<'PY'
from PIL import Image, ImageDraw
from pathlib import Path
allfiles=[]
for d in ['/mnt/data/_renders/optkit_1_50','/mnt/data/_renders/optkit_41_80','/mnt/data/_renders/optkit_81_100','/mnt/data/_renders/optkit']:
    for p in Path(d).glob('page-*.png'):
        num=int(p.stem.split('-')[1]); allfiles.append((num,p))
# dedupe by page number, latest occurrence doesn't matter
pages={n:p for n,p in allfiles}
missing=[i for i in range(1,130) if i not in pages]
print('missing',missing)
outdir=Path('/mnt/data/_renders/contact_all'); outdir.mkdir(exist_ok=True)
for old in outdir.glob('*.jpg'): old.unlink()
cols,rows=4,4; thumb_w=360
ordered=[(i,pages[i]) for i in range(1,130) if i in pages]
for k in range(0,len(ordered),16):
    batch=ordered[k:k+16]
    thumbs=[]
    for n,p in batch:
        im=Image.open(p).convert('RGB')
        ratio=thumb_w/im.width
        th=im.resize((thumb_w,int(im.height*ratio)))
        canvas=Image.new('RGB',(thumb_w,th.height+22),'white')
        canvas.paste(th,(0,22))
        d=ImageDraw.Draw(canvas); d.text((4,3),f'page {n}',fill='black')
        thumbs.append(canvas)
    cell_h=max(i.height for i in thumbs)
    sheet=Image.new('RGB',(cols*thumb_w,rows*cell_h),'white')
    for idx,im in enumerate(thumbs):
        sheet.paste(im,((idx%cols)*thumb_w,(idx//cols)*cell_h))
    sheet.save(outdir/f'contact-{k//16+1:02d}.jpg',quality=90)
print('sheets',len(list(outdir.glob('*.jpg'))))
PY
ls -1 /mnt/data/_renders/contact_all
```

```unknown
bash -lc python - <<'PY'
from PIL import Image
from pathlib import Path
for d in ['/mnt/data/_renders/optkit_1_50','/mnt/data/_renders/optkit_41_80','/mnt/data/_renders/optkit_81_100','/mnt/data/_renders/optkit']:
  for p in sorted(Path(d).glob('page-*.png')):
    try:
      im=Image.open(p); im.verify()
    except Exception as e:
      print('BAD',p,e)
PY
```

```unknown
bash -lc rm -rf /mnt/data/_renders/page40 && mkdir -p /mnt/data/_renders/page40
python /home/oai/skills/pdfs/scripts/render_pdf.py /mnt/data/optkit-design-and-migration-guide.pdf --out_dir /mnt/data/_renders/page40 --dpi 200 --pages 40
```

```unknown
bash -lc python - <<'PY'
from PIL import Image, ImageDraw
from pathlib import Path
allfiles=[]
for d in ['/mnt/data/_renders/optkit_1_50','/mnt/data/_renders/optkit_41_80','/mnt/data/_renders/optkit_81_100','/mnt/data/_renders/optkit','/mnt/data/_renders/page40']:
    for p in Path(d).glob('page-*.png'):
        num=int(p.stem.split('-')[1]); allfiles.append((num,p))
pages={n:p for n,p in allfiles}
outdir=Path('/mnt/data/_renders/contact_all'); outdir.mkdir(exist_ok=True)
for old in outdir.glob('*.jpg'): old.unlink()
cols,rows=4,4; thumb_w=360
for k in range(0,129,16):
    batch=[]
    for n in range(k+1,min(k+17,130)):
        p=pages[n]
        im=Image.open(p).convert('RGB')
        ratio=thumb_w/im.width
        th=im.resize((thumb_w,int(im.height*ratio)))
        canvas=Image.new('RGB',(thumb_w,th.height+22),'white')
        canvas.paste(th,(0,22))
        d=ImageDraw.Draw(canvas); d.text((4,3),f'page {n}',fill='black')
        batch.append(canvas)
    cell_h=max(i.height for i in batch)
    sheet=Image.new('RGB',(cols*thumb_w,rows*cell_h),'white')
    for idx,im in enumerate(batch):
        sheet.paste(im,((idx%cols)*thumb_w,(idx//cols)*cell_h))
    sheet.save(outdir/f'contact-{k//16+1:02d}.jpg',quality=90)
print('created', len(list(outdir.glob('*.jpg'))), 'sheets')
PY
```

```unknown
bash -lc rm -f /mnt/data/_optkit_pdf.md /mnt/data/_optkit.tex
rm -rf /mnt/data/_renders
ls -lh /mnt/data/optkit-design-and-migration-guide.md /mnt/data/optkit-design-and-migration-guide.pdf
```

<details><summary>💭 Thinking</summary>

**Rendered, validated, and organized 129-page PDF deliverables**

</details>

Done. The PDF is 129 pages and was render-checked after conversion.

[Download the PDF](sandbox:/mnt/data/optkit-design-and-migration-guide.pdf)

[Download the Markdown](sandbox:/mnt/data/optkit-design-and-migration-guide.md)

