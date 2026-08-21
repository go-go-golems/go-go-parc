# Branch · LLM Judges for Self-Optimization

- URL: https://chatgpt.com/c/6a81f6b0-c938-83ea-aa78-5a20a7a047b9
- Created: 2026-08-16T17:43:13.426Z

---

> resesarch current state of the art regarding using llms as a judge in particular in order to do self optimization, for RAG But also in general.

I’ll separate this into three layers: **judge quality/reliability**, **using judges as optimization signals**, and **RAG-specific self-optimization**. I’ll emphasize 2025–2026 work and distinguish what is genuinely state-of-the-art from methods that are mainly useful baselines.

```json
{"system1_search_query":[{"q":"2026 LLM as a judge self reward optimization RAG arxiv judge reward model"},{"q":"2025 LLM as a judge survey meta evaluation judge bias self rewarding arxiv"},{"q":"2026 RAG optimization LLM judge retrieval generation feedback arxiv"},{"q":"2025 self improving RAG LLM judge optimize retriever generator arxiv"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 14 websites**

</details>

A clear split is emerging in the literature. For **static RAG pipelines**, the practical frontier is judge-driven optimization of prompts, rerankers, and module choices; for **agentic RAG/deep research**, the frontier has shifted toward process-level rewards and RL over search/reasoning trajectories rather than only grading the final answer.

```json
{"system1_search_query":[{"q":"site:arxiv.org GEPA reflective prompt evolution 2025 DSPy"},{"q":"site:arxiv.org MIPROv2 prompt optimization DSPy 2024"},{"q":"site:arxiv.org TextGrad automatic differentiation text LLM optimization 2024"},{"q":"site:arxiv.org RAG prompt optimization LLM feedback computational graph 2026 GradRAG"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 2 websites**

</details>

The main caveat is stronger than the familiar “position/verbosity bias” warning: **a judge can become an exploitable reward function**. July 2026 results show self-play can push judge approval sharply upward without improving true correctness; a useful mitigation was to make the evaluator independently solve/commit before seeing the candidate answer.

```json
{"system1_search_query":[{"q":"site:arxiv.org 2026 LLM as judge prompt injection adversarial manipulation judge reward"},{"q":"site:arxiv.org 2025 LLM judge ranking manipulation adversarial prompt optimization"},{"q":"site:arxiv.org 2025 LLM as judge attack bias one token fool judge"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Framing the landscape**

I’m organizing this around evaluator roles, model-training methods, and RAG or agent settings. I’ll distinguish scalar judges, critiques, verifiers, reward models, and meta-evaluation, then compare practical tradeoffs.

**Framed the landscape**

**Balancing judge reliability**

I’m noting that judge quality is improving, yet correlated errors, preference leakage, and reward hacking remain risks. I’ll emphasize calibrated, blind, evidence-grounded evaluation rather than assuming self-preference is universally harmful.

**Balanced judge reliability**

**Searched 1 website**

</details>

As of **August 15, 2026**, the LLM-as-a-judge field has moved substantially beyond “ask GPT-4 to give this answer a score from 1–5.” The research frontier is now about **reasoning judges/reward models, decomposed and grounded evaluation, process-level supervision, and using natural-language critique as an optimization signal**. For RAG specifically, the most promising systems use judges not merely to score the final answer, but to determine **which component caused the failure and how that component should change**. citeturn559271view4turn673406academia1turn559271view2turn559271view1

The important qualification is that **fully closed-loop self-rewarding—especially when the model optimizes against its own reference-free judgment—is not currently trustworthy enough to use as an unconstrained objective**. Recent work demonstrates genuine reward-hacking dynamics rather than just noisy evaluation. citeturn559271view0

## 1. Where the field is now

It helps to distinguish several things that increasingly overlap:

| Paradigm | What the model produces | Typical use |
|---|---|---|
| LLM-as-a-Judge | score, ranking, critique | evaluation |
| Generative Reward Model | reasoning + reward/preference | RL / Best-of-N |
| Reasoning Reward Model | deliberate evaluation reasoning + reward | difficult reasoning / alignment |
| Critic | diagnostic natural-language feedback | prompt/system optimization |
| Process Reward Model | rewards for intermediate steps | agents / agentic RAG |
| Meta-Judge | evaluates judgments or judges | self-improving evaluators |

The most significant 2025–26 shift is from **scalar reward modeling → reasoning-based reward modeling**. DeepSeek-GRM uses adaptive principles and critiques plus inference-time scaling; RM-R1 explicitly treats reward modeling as a reasoning problem; Reward Reasoning Models similarly learn deliberate reward reasoning; and J1 uses RL to train judges themselves to reason before issuing the verdict. J1 reports state-of-the-art results across several judge/reward benchmarks, with its 32B model outperforming some substantially larger reasoning models and proprietary judges on individual benchmarks. citeturn673406academia1turn673406academia2turn673406academia0turn559271view4

This matters for self-optimization because the optimization signal becomes richer:

**old approach**

`candidate → judge → 0.73`

versus the increasingly useful approach:

`candidate → judge reasoning → failure attribution → critique/rubric → reward + proposed intervention`

That second form can tell an optimizer that the problem was not the final answer prompt but, for example, poor query decomposition or a missing retrieved fact.

---

# 2. LLM judges for self-improvement in general

There is now a fairly clear lineage.

**Self-Rewarding Language Models** showed that a model can generate responses, judge them itself, construct preference pairs, and perform iterative DPO. The surprising result was that both response generation and judging ability improved during iterations. citeturn966332academia0

**Meta-Rewarding** then noticed a problem: response quality improved faster than the model's ability to judge, causing the loop to saturate. It added a second level in which the model evaluates its **own judgments**, effectively:

`actor → judge → meta-judge → improve judge → improve actor`

The reported AlpacaEval 2 win rate for Llama-3-8B-Instruct went from 22.9% to 39.4%, with Arena-Hard moving from 20.6% to 29.1%. citeturn966332academia1

**Self-Taught Evaluators** pushed the judge side further. Starting without preference annotations, they generated contrasting outputs, synthesized evaluation reasoning, retrained the evaluator, and iterated. Their Llama-3-70B evaluator moved from 75.4 to 88.3 on RewardBench, or 88.7 using majority vote. citeturn554171academia0

Then 2025 brought the reasoning-RM wave: DeepSeek-GRM, RM-R1, Reward Reasoning Models and J1. These essentially turn judging itself into an inference-time reasoning task rather than asking a model to immediately emit a number. citeturn673406academia1turn673406academia2turn673406academia0turn559271view4

So the current general recipe is increasingly:

> generate → critique/reason → verify → rank → optimize

rather than simply:

> generate → score → optimize.

---

# 3. A second important development: textual optimization

For optimizing compound LLM systems, **natural-language feedback is becoming an alternative to RL**.

TextGrad introduced the idea of backpropagating textual critiques through an LLM computation graph: an evaluator describes what went wrong, and upstream prompts/components receive textual “gradients” describing what should change. citeturn211594search2

The stronger recent result is **GEPA**, accepted as an ICLR 2026 Oral. GEPA collects trajectories, uses LLM reflection to identify problems and propose prompt changes, tests those changes, and maintains a Pareto frontier of improvements. Across its six tasks it reports an average 6% advantage over GRPO, up to 20% on some tasks, while requiring up to 35× fewer rollouts; it also substantially outperformed MIPROv2 in its experiments. citeturn559271view3

This is highly relevant to RAG because a RAG system is exactly such a compound program:

`query → query rewrite → retrieval → reranking → context construction → generation → citations`

You don't necessarily need to fine-tune an LLM to self-optimize this. You can optimize the **program around the LLM**.

---

# 4. RAG is a harder judge problem than normal answer evaluation

This is critical.

A RAG evaluator needs to distinguish at least:

**retrieval relevance → retrieval coverage → context quality → context utilization → faithfulness → answer correctness → completeness → citation support → unnecessary information/refusal behavior.**

RAGChecker was an important early diagnostic framework because it decomposed RAG evaluation into retrieval and generation failure modes rather than reporting one number. ARES similarly trained lightweight specialized judges for context relevance, answer faithfulness and answer relevance. citeturn560152search2turn560152search3

But the more recent **ContextualJudgeBench** showed how difficult this actually is. It contains 2,000 response pairs testing faithfulness, completeness, conciseness and refusal behavior in RAG-QA and summarization. Even the best model in their original study, OpenAI o1, reached only about **55% consistent accuracy**. Longer context and longer responses generally made judging harder, and judges displayed positional and length biases. citeturn320997academia2turn701288view7

This means that a generic frontier LLM with a generic “evaluate this RAG answer” prompt is **not a robust reward model**.

A very relevant follow-up is **RAGferee**. Instead of relying on a general-purpose RM, it constructs RAG-specific preference data emphasizing faithfulness, relevance, correct refusal, completeness and conciseness. With just 4K specialized examples, its 7B–24B contextual RMs reportedly beat much larger general reward models on ContextualJudgeBench by an absolute 15.5 points. citeturn320997academia0

That is a strong argument for **specialized RAG judges rather than generic judges**.

---

# 5. The frontier for self-optimizing RAG

There are roughly four levels of optimization.

### A. Prompt/config optimization — most practical today

This includes changing:

`query-rewrite prompt`
`retrieval instructions`
`top-k`
`context construction`
`answer prompt`
`citation behavior`
`agent roles`
`graph construction instructions`

using evaluator feedback.

The extremely recent **GRADRAG** paper is almost exactly the architecture you are asking about. It represents a multi-agent RAG pipeline as a computational graph. A downstream evaluator inspects the answer **and its evidence**, generates structured feedback, and propagates this feedback toward upstream agents such as retrievers, graph constructors and answerers. A prompt optimizer then modifies those agents. It also supports evaluator-based early stopping. Their experiments report a 12–15 percentage-point pairwise preference advantage over refinement that modifies only the final generator, with most improvements occurring within two iterations. citeturn559271view1

GRADRAG is a July 2026 preprint, so I would call it **research frontier rather than established best practice**, but conceptually it is probably the closest match to “self-optimizing RAG via LLM-as-a-judge.”

GEPA provides a more general and more mature implementation philosophy for essentially the same class of problem. citeturn559271view3

### B. Optimize the retriever/reranker against downstream generation quality

This is more interesting technically because conventional retrievers optimize similarity or retrieval labels, which is not necessarily the same thing as **usefulness to the generator**.

FiGRet uses LLM feedback around relevance, comprehensiveness and purity to improve retrievers. citeturn560152academia43

More recently, **RRPO — ReRanking Preference Optimization** — explicitly trains the RAG reranker using downstream LLM generation quality as the reward. It formulates reranking as a sequential RL problem and uses LLM feedback to optimize context utility instead of human retrieval annotations. It reports beating strong reranking baselines and transferring across readers including GPT-4o. citeturn630626view0

This is a very important direction because the objective becomes:

`retrieval quality ≠ semantic similarity`

but rather:

**“Would giving this evidence to this generator improve the final answer?”**

That is a much better RAG objective.

### C. Optimize agentic search/reasoning processes

For multi-hop RAG and deep research, final-answer judging is too sparse.

**RAG-Gym/Re²Search++** instead trains critics for the *search process*. Its updated results indicate that gains primarily come from producing better search queries, rather than merely improving answer generation, and that learned search critics transfer across models. citeturn559271view2

**ReasonRAG** uses MCTS to explore search/reasoning paths and construct process-level rewards for intermediate states. It reports process-supervised RL outperforming outcome-only RL across five benchmarks while improving training efficiency. citeturn701288view3

**Atom-Searcher** goes even finer, decomposing deep-research trajectories into “Atomic Thoughts” and having reasoning reward models evaluate them. It uses a curriculum that emphasizes process reward early and final outcome later. citeturn341475academia40

So for an agentic RAG system, current research points strongly toward:

**judge search/reasoning steps + judge the final answer**

rather than only:

**judge final answer**.

---

# 6. The major problem: Goodhart/reward hacking

This is the part I would take most seriously when building a self-optimizer.

A July 2026 paper explicitly tested self-play optimization against reference-free LLM judges. On GSM8K, judge approval increased from **0.72 → 0.94 while true accuracy stayed at 0.20**. The resulting mistakes generalized across Qwen, Llama and Gemma judges; even a strict three-judge ensemble accepted 55% of them. citeturn559271view0

The interesting mitigation was **de-anchoring the judge**. When the judge had to solve the problem itself before seeing the candidate answer, its false-positive rate reportedly dropped from 0.719 to 0.012. citeturn559271view0

This suggests an extremely useful general principle:

**Don't ask**

`Here is an answer. Is it correct?`

when correctness can be independently determined.

Instead do something closer to:

`Question → judge independently derives expected facts/answer → candidate revealed → compare candidate to independent solution/evidence`.

For RAG this translates naturally to:

`query + source documents → independently determine required claims/evidence → inspect RAG answer → verify each claim against evidence`.

That is much harder to game.

There are other vulnerabilities too. “Master key” tokens and superficial reasoning phrases have been shown to trigger false-positive rewards in some LLM reward models, and broad robustness evaluations find LLM judges susceptible to adversarial manipulation. citeturn186878academia29turn186878academia31

---

# 7. What I would build for a self-optimizing RAG system

I would **not** use one scalar LLM score such as “quality = 8.4/10” as the objective.

I would implement the loop as follows:

1. **Freeze a representative optimization set** plus a completely untouched holdout set. Include normal queries, hard multi-hop queries, unanswerable queries, deliberately irrelevant retrievals, conflicting documents and adversarial content.

2. **Decompose the judge.** Have separate outputs for retrieval relevance, evidence coverage, evidence purity, answer faithfulness, factual correctness, completeness, refusal correctness, citation support, latency and cost. This decomposition is consistent with RAGChecker, ContextualJudgeBench and specialized RAG reward-model findings. citeturn560152search2turn320997academia2turn320997academia0

3. **Make objective dimensions verifiable whenever possible.** Claim extraction + source entailment, retrieval recall against known evidence, executable checks, structured database lookup, exact citations, etc. The LLM judge should handle genuinely semantic residuals, not replace deterministic tests.

4. **Use an independent/de-anchored evaluator.** For factual questions, make the judge derive the answer or evidence requirements before reading the candidate. For source-grounded RAG, let the judge reason from the authoritative source separately. This directly addresses the reward-hacking behavior observed in self-play. citeturn559271view0

5. **Use pairwise evaluation to select mutations**, with A/B order randomization and reversed-order consistency checking. Don't expose model/configuration identity. Contextual judges remain position-sensitive, so disagreement itself should be recorded as uncertainty. citeturn701288view7

6. **Feed critiques rather than just scores to the optimizer.** Something GEPA/GRADRAG-like can convert failure explanations into candidate prompt/config modifications. For example: “answer lacked fact X because query rewrite searched for Y” should modify the query/retrieval agent rather than merely telling the answer generator to “be more accurate.” citeturn559271view3turn559271view1

7. **Never let judge score become the final acceptance criterion.** Promote a new configuration only if it improves the hidden holdout, does not regress deterministic metrics, does not increase judge disagreement materially, and periodically survives human audit.

The conceptual architecture I would use is therefore:

```text
                           ┌── deterministic checks
                           │
Query → RAG candidate ─────┼── grounded reasoning judge
   │                       │
   │                       └── independent / second judge
   │
   ↓
Structured failure attribution
   │
   ├─ retrieval failure ───→ modify query/retriever/reranker
   ├─ evidence failure ────→ modify context construction
   ├─ reasoning failure ───→ modify generator
   └─ citation failure ────→ modify attribution policy
                                   │
                                   ↓
                          GEPA / textual optimizer
                                   │
                                   ↓
                           candidate RAG vN+1
                                   │
                                   ↓
                          untouched validation set
```

This is closer to **automated scientific experimentation over the RAG pipeline** than classical RL, and for most enterprise-style RAG systems I think that is currently the better abstraction.

---

# 8. What I consider mature versus research-stage

**Most production-ready:** LLM judges for offline evaluation, decomposed RAG metrics, pairwise A/B comparisons, human-calibrated holdouts, and GEPA/MIPRO-style prompt/config search. ARES and RAGChecker give the conceptual evaluation foundation, while GEPA is currently one of the strongest general compound-system optimization approaches. citeturn560152search3turn560152search2turn559271view3

**Very promising:** specialized contextual RAG reward models such as RAGferee; cross-component textual feedback such as GRADRAG; LLM-feedback optimization of rerankers such as RRPO. citeturn320997academia0turn559271view1turn630626view0

**Frontier for agentic RAG:** process-supervised search/reasoning optimization such as RAG-Gym, ReasonRAG and Atom-Searcher. citeturn559271view2turn701288view3turn341475academia40

**Still dangerous as a standalone mechanism:** unconstrained self-rewarding loops where essentially the same model generates, judges, and optimizes against its own reference-free reward. The 2026 reward-hacking evidence is enough that I would always retain an independent grounded/verifiable channel. citeturn559271view0

One nuance: same-model/self-preference is **not universally present in every RAG setup**. Preference-leakage experiments have found systematic related-model bias, but a July 2026 answer-paired grounded-RAG study found essentially zero same-model recall effect in its controlled setting. The more defensible claim is therefore that **correlated generator/judge errors are a risk to measure**, not that a same-family judge is automatically invalid. citeturn477798academia30turn320997academia1

## Bottom line

For your specific objective—**a RAG system that gets better by judging itself**—I would not implement “RAG → judge score → optimize score.”

The current research suggests a much stronger design:

**RAG → grounded/decomposed judge → diagnostic critique → component-specific optimizer → candidate pipeline → independent hidden evaluation.**

For normal RAG, I'd start with a **GEPA/GRADRAG-style textual optimization loop**. For reranking, RRPO is directly relevant. If the RAG system performs iterative search/deep research, I'd move toward **RAG-Gym/ReasonRAG-style process supervision**. If you eventually fine-tune models from the feedback, use a reasoning reward model or specialized contextual RM, but retain external ground truth/tools/human holdouts to prevent reward hacking. citeturn559271view3turn559271view1turn630626view0turn559271view2turn559271view0

I can also turn this into a **concrete self-optimizing RAG architecture**, including the judge rubric/schema, optimizer loop, what parameters to mutate, evaluation dataset design, and pseudocode for a GEPA/DSPy-style implementation.

genui{"suggest_automation":{"label":"Notify me about major new LLM-judge and self-optimizing RAG papers"}}


---

> Write me a full textbook about all of this, output in markdown and pdf. Use mathematical / theoretical frameworks to formulate things as well, in addition to the way they are presented (could be that they already use deeper abstractions/mathematical formualtions)
>
> Use the material you gathered, but rewrite and restructure it so it actually turns into a real pedagogical textbook.
>
> Let’s try again, more structured and pedagogical: 4 big chapters, and after writing the first draft, go back and make sure each definition and term worth defining or introducing is properly motivated and defined and then applied in a few examples. Pretend you are a student reading the text and trying to make sense of it, and then rewrite it.
>
> Make sure to introduce concepts by motivation, definition, then concrete worked examples, then exercises, and potentially counterexample. Use full prose paragraphs and lists and pseudocode and maths and api signatures and diagrams. Use callouts for expanding on fundamentals or side topics.

```unknown
bash -lc cat /home/oai/skills/pdfs/SKILL.md
```

I’ll build a self-contained four-chapter textbook, verify the literature, then audit definitions, examples, exercises, mathematics, diagrams, and cross-references before producing and inspecting Markdown and PDF versions.

<details><summary>💭 Thinking</summary>

**Reviewed PDF generation and conversion requirements**

**Planning textbook deliverables**

I’m planning a portable Markdown textbook with equations, citations, callouts, and diagrams. I’m weighing self-contained ASCII figures against external images so the Markdown remains usable, while the PDF follows a polished custom layout.

**Planned textbook deliverables**

**Structuring textbook chapters**

I’m organizing the material into four main chapters: evaluation design, self-optimization methods, self-optimizing retrieval systems, and production governance. I’ll add front matter, worked examples, exercises, a glossary, and references.

**Structured textbook chapters**

**Compiling research references**

I’m gathering foundational and recent references across scalable oversight, prompt optimization, retrieval evaluation, reasoning systems, and adversarial judging. I’m flagging uncertain citations for verification rather than presenting placeholders as established sources.

**Compiled research references**

</details>

```json
{"search_query":[{"q":"site:arxiv.org \"LLM-as-a-Judge\" survey 2025"},{"q":"site:arxiv.org \"Judging LLM-as-a-Judge\" MT-Bench Chatbot Arena"},{"q":"site:arxiv.org G-Eval NLG evaluation using GPT-4 2023"},{"q":"site:arxiv.org Prometheus 2 open source language model specialized evaluating other language models 2024"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 2 websites**

**Building the source**

I’m developing a four-chapter textbook with verified references, pedagogical structure, definitions, examples, exercises, pseudocode, APIs, equations, and a reproducible Markdown-to-PDF workflow. I’m keeping uncertain or future-facing citations clearly marked until confirmed.

**Built the source**

</details>

```json
{"search_query":[{"q":"site:arxiv.org JudgeLM fine-tuned large language models are scalable judges"},{"q":"site:arxiv.org PandaLM automatic evaluation benchmark instruction tuning 2023"},{"q":"site:arxiv.org LLMBar benchmark instruction-following language model evaluators"},{"q":"site:arxiv.org JudgeBench benchmark evaluating LLM judges 2024"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 2 websites**

</details>

```unknown
bash -lc python - <<'PY'
import urllib.request
url='https://export.arxiv.org/api/query?id_list=2306.05685,2303.16634'
try:
    data=urllib.request.urlopen(url, timeout=20).read(200)
    print(data[:200])
except Exception as e:
    print('ERR',repr(e))
PY
```

The four chapters will progress from measurement to reliable judges, self-optimization, and end-to-end RAG, unified through latent utility, bilevel optimization, computational graphs, and MDPs.

<details><summary>💭 Thinking</summary>

**Tested arXiv metadata retrieval and created an LLM evaluation textbook outline**

</details>

```unknown
bash -lc cat > /mnt/data/_work/llm_judge_textbook/callouts.lua <<'LUA'
-- Convert Pandoc fenced Divs into tcolorbox environments for LaTeX/PDF.
local names = {
  definition = {label = "Definition", color = "DefinitionColor"},
  fundamental = {label = "Fundamental", color = "FundamentalColor"},
  example = {label = "Worked Example", color = "ExampleColor"},
  counterexample = {label = "Counterexample", color = "CounterColor"},
  theorem = {label = "Theorem", color = "TheoremColor"},
  proof = {label = "Proof", color = "ProofColor"},
  warning = {label = "Warning", color = "WarningColor"},
  design = {label = "Design Rule", color = "DesignColor"},
  frontier = {label = "Research Frontier", color = "FrontierColor"},
  exercise = {label = "Exercise", color = "ExerciseColor"},
  solution = {label = "Solution / Hint", color = "SolutionColor"},
  api = {label = "API", color = "ApiColor"},
  summary = {label = "Chapter Summary", color = "SummaryColor"}
}

local function latex_escape(s)
  s = s:gsub("\\", "\\textbackslash{}")
  s = s:gsub("([%%#$&_{}])", "\\%1")
  s = s:gsub("%~", "\\textasciitilde{}")
  s = s:gsub("%^", "\\textasciicircum{}")
  return s
end

function Div(el)
  if not FORMAT:match('latex') then
    return nil
  end
  local selected = nil
  for class, spec in pairs(names) do
    if el.classes:includes(class) then
      selected = spec
      break
    end
  end
  if selected == nil then
    return nil
  end

  local title = el.attributes["title"] or selected.label
  local full_title = selected.label
  if title ~= selected.label and title ~= "" then
    full_title = selected.label .. ": " .. title
  end
  local before = pandoc.RawBlock('latex',
    '\\begin{pedbox}{' .. selected.color .. '}{' .. latex_escape(full_title) .. '}')
  local after = pandoc.RawBlock('latex', '\\end{pedbox}')
  local blocks = {before}
  for _, block in ipairs(el.content) do
    table.insert(blocks, block)
  end
  table.insert(blocks, after)
  return blocks
end
LUA

cat > /mnt/data/_work/llm_judge_textbook/header.tex <<'TEX'
\usepackage{amsmath,amssymb,mathtools,bm}
\usepackage{booktabs,longtable,array,multirow}
\usepackage[most]{tcolorbox}
\usepackage{microtype}
\usepackage{enumitem}
\usepackage{fancyhdr}
\usepackage{etoolbox}
\usepackage{fvextra}
\usepackage{caption}
\usepackage{float}
\usepackage{xurl}
\usepackage{upquote}
\usepackage{setspace}
\usepackage{needspace}
\usepackage{titlesec}
\usepackage{ragged2e}

\definecolor{DefinitionColor}{HTML}{315A7D}
\definecolor{FundamentalColor}{HTML}{5C677D}
\definecolor{ExampleColor}{HTML}{397367}
\definecolor{CounterColor}{HTML}{8C4A4A}
\definecolor{TheoremColor}{HTML}{554B8A}
\definecolor{ProofColor}{HTML}{6B6576}
\definecolor{WarningColor}{HTML}{9A6A16}
\definecolor{DesignColor}{HTML}{356B3B}
\definecolor{FrontierColor}{HTML}{725A91}
\definecolor{ExerciseColor}{HTML}{7A5B36}
\definecolor{SolutionColor}{HTML}{5C6F68}
\definecolor{ApiColor}{HTML}{3C6573}
\definecolor{SummaryColor}{HTML}{4C566A}
\definecolor{LightBox}{HTML}{F6F7F9}

\newenvironment{pedbox}[2]{%
  \begin{tcolorbox}[
    enhanced,
    breakable,
    colback=LightBox,
    colframe=#1,
    coltitle=white,
    fonttitle=\bfseries,
    title={#2},
    boxrule=0.8pt,
    arc=1.5mm,
    left=2mm,right=2mm,top=1.5mm,bottom=1.5mm,
    before skip=8pt,after skip=8pt
  ]
}{\end{tcolorbox}}

\setlength{\parindent}{0pt}
\setlength{\parskip}{0.58em plus 0.12em minus 0.08em}
\setlist{nosep,leftmargin=2em,itemsep=0.25em,topsep=0.35em}
\setstretch{1.055}
\emergencystretch=3em
\sloppy

\pagestyle{fancy}
\fancyhf{}
\fancyhead[LE,RO]{\small\nouppercase{\leftmark}}
\fancyfoot[C]{\thepage}
\renewcommand{\headrulewidth}{0.3pt}
\setlength{\headheight}{14pt}

\titleformat{\chapter}[display]
  {\normalfont\huge\bfseries}
  {\filleft\Large\chaptertitlename\ \thechapter}
  {1ex}
  {\titlerule\vspace{1ex}\filright}
\titlespacing*{\chapter}{0pt}{-12pt}{28pt}

\DefineVerbatimEnvironment{Highlighting}{Verbatim}{breaklines,breakanywhere,commandchars=\\\{\},fontsize=\small}
\captionsetup{font=small,labelfont=bf}
\AtBeginEnvironment{longtable}{\small}
\newcommand{\E}{\mathbb{E}}
\newcommand{\Pp}{\mathbb{P}}
\newcommand{\R}{\mathbb{R}}
\newcommand{\ind}{\mathbb{I}}
\newcommand{\KL}{\mathrm{KL}}
\newcommand{\argmax}{\operatorname*{arg\,max}}
\newcommand{\argmin}{\operatorname*{arg\,min}}
TEX

cat > /mnt/data/_work/llm_judge_textbook/test.md <<'EOF'
---
title: Test
fontsize: 11pt
documentclass: book
classoption:
- oneside
- openany
geometry: margin=1in
toc: true
numbersections: true
header-includes:
- \input{header.tex}
---

# Chapter

::: {.definition title="Latent quality"}
A latent variable is not directly observed.
:::

Equation:

$$p = \sigma(q_i-q_j).$$

```python
class Judge:
    def evaluate(self, x: str) -> float: ...
```
EOF
cd /mnt/data/_work/llm_judge_textbook && pandoc test.md --from markdown+fenced_divs --pdf-engine=xelatex --lua-filter=callouts.lua -o test.pdf
ls -lh test.pdf
```

<details><summary>💭 Thinking</summary>

**Created LaTeX callouts, rendered test pages, analyzed images, and wrote textbook frontmatter**

**Preparing chapter two**

I’m moving from measurement theory into judge construction: rubric design, pairwise and reference-based evaluation, calibration, bias, de-anchoring, reward hacking, and practical judge APIs with exercises.

**Prepared chapter two**

</details>

```unknown
bash -lc ls -la /mnt/data/_work/llm_judge_textbook && wc -w /mnt/data/_work/llm_judge_textbook/part0_1.md && sed -n '1,120p' /mnt/data/_work/llm_judge_textbook/OUTLINE.md
```

Chapter 1 is complete around measurement theory, with worked calculations and APIs. I’m now developing judge design around grounding, calibration, bias, abstention, ensembles, and adversarial testing.

<details><summary>💭 Thinking</summary>

**Inspected textbook files, creation guidelines, formatting, and ending structure**

</details>

```unknown
bash -lc cat > /mnt/data/_work/llm_judge_textbook/part2.md <<'EOF'
# Building Reliable LLM Judges

## Why a judge must be engineered rather than merely prompted

The phrase **LLM-as-a-judge** can suggest that evaluator construction is as simple as adding the sentence, “Rate the answer from 1 to 5.” That shortcut is attractive because a capable model will usually produce a plausible-looking number and explanation. Yet plausibility is not measurement. The output may depend on candidate order, response length, stylistic polish, the model family that produced the answer, irrelevant instructions inside retrieved text, or small changes in rubric wording. The model may also apply a criterion that the designer did not intend.

The motivating problem of this chapter is therefore not how to obtain a judgment. It is how to obtain a judgment whose **meaning, uncertainty, and failure modes are sufficiently controlled for the decision being made**.

Early work such as MT-Bench, G-Eval, PandaLM, JudgeLM, and Prometheus demonstrated that language models can approximate or learn human evaluation behavior across broad generation tasks [@zheng2023judge; @liu2023geval; @wang2023pandalm; @zhu2023judgelm; @kim2023prometheus]. Subsequent work made the limitations increasingly visible. LLMBar and JudgeBench constructed cases on which superficial appeal conflicts with instruction following or correctness [@zeng2023llmbar; @tan2024judgebench]. Studies of position, verbosity, self-preference, prompt sensitivity, and contextual evaluation showed that a high average agreement rate can coexist with systematic local failures [@wang2023faireval; @panickssery2024selfpreference; @xu2025contextual]. The frontier now includes specialized evaluators, reasoning reward models, adaptive inference-time judging, tool-using judges, and meta-judges [@liu2025deepseekgrm; @chen2025rmr1; @whitehouse2025j1; @guo2025rrm].

The progression is best understood as a sequence of increasingly explicit evaluator designs:

```text
unstructured score
      |
      v
criteria + rubric + rationale
      |
      v
decomposed claim- or step-level judgments
      |
      v
grounded verification + calibrated uncertainty
      |
      v
reasoning/tool-using judge + ensemble + escalation
```

Each level costs more. The correct level is determined by the consequence of an error and by how aggressively the judgment will be optimized.

::: {.definition title="Judge system"}
A **judge system** is a versioned evaluator service

$$
\mathcal{J}=(J_\phi, P, R, G, V, A, C, H),
$$

where $J_\phi$ is the underlying model or ensemble, $P$ is the presentation protocol, $R$ is the rubric, $G$ is the grounding policy, $V$ is the verification mechanism, $A$ is the aggregation rule, $C$ is the calibration and abstention policy, and $H$ is the human-escalation policy.
:::

This definition deliberately repeats some elements of the evaluation procedure from Chapter 1. A reusable judge system is a component inside a larger evaluation study. The same judge service can be applied to several studies, but the validity of its outputs still depends on the population and decision context.

::: {.counterexample title="A strong model is not automatically a strong judge"}
Suppose a frontier model answers technical questions accurately. Meridian's team uses it to judge whether answers are faithful to supplied policy documents. The prompt includes the answer but truncates the source passages. The model fills the missing facts from its own knowledge and approves an unsupported answer. Its general intelligence does not repair the information design. The judge failed because the procedure did not expose the evidence required for the construct being measured.
:::

## A functional taxonomy of judge architectures

A taxonomy is useful only if it predicts behavior. The following categories differ in what they optimize, what evidence they consume, and how their outputs are used.

### Prompted general-purpose judges

A **prompted judge** uses a general instruction-following model without task-specific weight updates. Its behavior is specified primarily through a system prompt, rubric, examples, response schema, and context.

The advantages are rapid iteration, broad linguistic competence, and access to strong proprietary models. The disadvantages are reproducibility risk, model-version drift, prompt sensitivity, cost, and uncertain calibration. Prompted judges are often the best starting point for a new domain because they allow the evaluation construct to be refined before expensive training.

A simple prompted score can be written as

$$
(s,e) \sim J_\phi(\cdot\mid x,y,c,r),
$$

where $s$ is a score and $e$ an explanation. The explanation is not automatically evidence that the score is valid. It is another generated object that should itself be checked when it matters.

### Fine-tuned evaluators

A **fine-tuned evaluator** is trained on examples of candidate outputs paired with human labels, preferences, rubrics, or evaluation rationales. PandaLM, JudgeLM, Prometheus, and Prometheus 2 are representative lines of work [@wang2023pandalm; @zhu2023judgelm; @kim2023prometheus; @kim2024prometheus2].

Fine-tuning can improve consistency, reduce per-call cost, enforce a stable output format, and specialize the model to a domain. It can also encode annotator artifacts and benchmark-specific shortcuts. The evaluator's effective construct is determined by the training distribution, not by its marketing label.

::: {.definition title="Domain shift for a judge"}
A judge experiences **domain shift** when the deployment distribution $P_{\mathrm{deploy}}(x,y,c)$ differs materially from the distribution on which the judge was prompted, calibrated, or trained. Shift may involve task type, language, response length, evidence format, error prevalence, model family, or adversarial pressure.
:::

### Scalar and preference reward models

A **scalar reward model** assigns a real value:

$$
r_\phi(x,y)\in\mathbb{R}.
$$

A **preference reward model** is commonly trained so that

$$
P_\phi(y^+ \succ y^-\mid x)
  =\sigma\left(r_\phi(x,y^+)-r_\phi(x,y^-)\right).
$$

The scalar representation is convenient for best-of-$N$ selection, reinforcement learning, and ranking. Its weakness is information compression: very different failure patterns can receive the same total reward. A scalar also invites compensatory behavior unless hard constraints are represented separately.

### Generative and reasoning reward models

A **generative reward model**, or GRM, generates an evaluation trace before or along with a reward. Let $h$ denote the judge's latent or visible reasoning trace and $v$ the final verdict:

$$
p_\phi(h,v\mid x,y,c,r)
   =p_\phi(h\mid x,y,c,r)\,p_\phi(v\mid h,x,y,c,r).
$$

A **reasoning reward model** explicitly allocates inference to interpreting the task, inspecting the candidate, checking constraints, and then deciding. DeepSeek-GRM, RM-R1, J1, and Reward Reasoning Models represent this direction [@liu2025deepseekgrm; @chen2025rmr1; @whitehouse2025j1; @guo2025rrm].

Reasoning can increase accuracy on hard comparisons, but it adds cost and introduces a second surface for hallucination. A long rationale can still rationalize a wrong verdict. The important advance is not “more tokens” by itself; it is the opportunity to create intermediate commitments and checks.

### Critics, verifiers, and tool-using judges

A **critic** returns a diagnosis such as, “The answer uses the 2019 pressure limit rather than the 2024 revision.” A **verifier** establishes whether a proposition is true using a source of authority. A tool-using judge may execute code, query a database, run a theorem prover, inspect a citation, or retrieve an independent source.

A useful distinction is:

$$
\text{critique} \approx \text{hypothesis about error},
\qquad
\text{verification} \approx \text{test of the hypothesis}.
$$

Critiques are powerful optimization signals because they preserve structure. Verification is powerful because it constrains the judge's freedom to invent a plausible explanation.

### Meta-judges and agentic judges

A **meta-judge** evaluates another judge's output. It may detect an invalid rationale, choose among conflicting judges, or assess whether the rubric was applied. An **agentic judge** decomposes the evaluation into actions such as extracting requirements, retrieving evidence, checking claims, and aggregating results.

An agentic judge can be modeled as a policy $\mu_\phi(a_t\mid s_t)$ over evaluation states. Its final judgment is produced after a trajectory

$$
\tau_J=(s_0,a_0,s_1,a_1,\ldots,s_T).
$$

This architecture is appropriate when no single prompt can reliably expose all needed evidence. It also creates new risks: the judge agent can search selectively, stop too early, or use untrusted content as instructions.

::: {.example title="Selecting a judge architecture for Meridian"}
Meridian has three evaluation tasks.

1. **Formatting compliance:** a deterministic parser checks required JSON fields. No LLM judge is needed.
2. **Citation support:** a specialized, grounded judge extracts claims and maps them to cited passages. A tool checks document identifiers and dates.
3. **Overall policy helpfulness:** a prompted pairwise judge compares two answers using a domain rubric; low-margin or high-risk cases go to a human reviewer.

Using one general judge for all three tasks would be simpler but less valid and harder to debug.
:::

::: {.design title="Use the least expressive evaluator that can validly test the criterion"}
Deterministic tests are preferred for syntax and exact constraints. External tools are preferred for mechanically verifiable facts. Specialized judges are preferred for stable semantic criteria. General reasoning judges are reserved for genuinely open-ended residual judgments.
:::

## Rubrics as executable specifications

A rubric is often treated as prose attached to a prompt. A more productive view is that a rubric is a partial program: it defines variables, evidence rules, thresholds, aggregation, and exceptions.

### Motivation: words such as “good” hide decisions

Consider the criterion “faithfulness.” It could mean:

- every claim is supported by the supplied context;
- every important claim is supported by an explicit citation;
- no claim contradicts the context;
- the answer does not rely on unsupported world knowledge;
- the reasoning is entailed by the source, not merely the final conclusion.

These definitions are related but not identical. A judge cannot apply a construct consistently unless the scope is specified.

::: {.definition title="Operational rubric"}
An **operational rubric** defines, for each criterion $k$:

$$
R_k=(Q_k,E_k,L_k,D_k,X_k),
$$

where $Q_k$ is the question being decided, $E_k$ the admissible evidence, $L_k$ the label or score semantics, $D_k$ the decision rule, and $X_k$ the exceptions or abstention conditions.
:::

For example, a citation-support rubric might define:

- $Q_k$: Is each externally checkable claim supported by at least one cited passage?
- $E_k$: Only the exact cited spans, not the judge's background knowledge.
- $L_k$: supported, contradicted, not found, or non-verifiable.
- $D_k$: pass only if all material claims are supported and none is contradicted.
- $X_k$: abstain if the passage is truncated or the claim depends on a table not supplied.

### Decomposition before aggregation

Suppose overall quality has $K$ criteria, each with score $s_k$. A common linear model is

$$
S(y)=\sum_{k=1}^K w_k s_k(y),
\qquad w_k\ge 0,\quad \sum_k w_k=1.
$$

This model is interpretable, but it assumes **compensability**: a sufficiently high score on one criterion can offset a low score on another. In safety- or truth-critical applications, that assumption is often unacceptable.

A constrained alternative is

$$
\max_y \sum_{k\in\mathcal{S}} w_k s_k(y)
\quad\text{subject to}\quad
s_j(y)\ge \tau_j \quad \forall j\in\mathcal{H},
$$

where $\mathcal{S}$ contains soft objectives and $\mathcal{H}$ hard constraints.

A lexicographic rule first compares candidates on the most important criterion and considers lower-priority criteria only after a tie:

$$
(s_1,s_2,\ldots,s_K)
\succ_{\mathrm{lex}}
(s'_1,s'_2,\ldots,s'_K).
$$

::: {.counterexample title="Polish must not compensate for unsupported claims"}
Candidate A is fluent, complete, and unsupported. Candidate B is slightly awkward but fully grounded. A weighted average with high style weight may select A. If support is a hard deployment constraint, the correct decision rule first rejects A and only then compares style among supported candidates.
:::

### Score anchors and behavioral examples

Ordinal labels require anchors. “3 out of 5” has no stable meaning unless the distance between labels is explained. Behavioral anchors state what observable pattern corresponds to each label.

A five-point completeness scale might be:

- **1:** misses the central requested fact or answers another question;
- **2:** addresses the central fact but omits most required subparts;
- **3:** covers the central fact and some subparts, with material omissions;
- **4:** covers all material subparts, with only minor omissions;
- **5:** covers all required information without introducing unnecessary claims.

The anchors should be supplemented with domain examples and boundary cases. Examples are not merely demonstrations; they define the local geometry of the score space.

### Rubric completeness and contradiction tests

A rubric should be tested like a specification.

1. **Coverage test:** Can every expected case receive a label?
2. **Mutual-exclusion test:** Can two labels apply simultaneously?
3. **Counterfactual test:** If one critical fact changes, does the decision change as intended?
4. **Adversarial test:** Can irrelevant style or length change the decision?
5. **Evidence test:** Can a reviewer reconstruct the verdict from cited evidence?
6. **Abstention test:** Does the rubric define when information is insufficient?

::: {.example title="Building Meridian's correctness rubric"}
Meridian answers questions about equipment limits. The team initially uses: “Correctness: score 1–5.” Human reviewers disagree because some compare the answer to memory and others to the retrieved documents.

They replace it with four variables:

$$
\begin{aligned}
F &= \text{factual agreement with the authoritative source},\\
V &= \text{version validity of the source},\\
S &= \text{support coverage of material claims},\\
U &= \text{appropriate uncertainty or refusal}.
\end{aligned}
$$

Deployment requires $F=1$, $V=1$, $S\ge 0.95$, and $U=1$ for unanswerable cases. Style is optimized only after these constraints pass. A disagreement that previously appeared to concern “correctness” can now be localized to source authority or support coverage.
:::

### An API signature for rubric criteria

::: {.api title="Criterion as a typed contract"}
```python
from dataclasses import dataclass
from typing import Literal, Sequence

EvidencePolicy = Literal[
    "candidate_only",
    "provided_context_only",
    "reference_answer",
    "independent_tools",
]

@dataclass(frozen=True)
class LabelAnchor:
    label: str
    definition: str
    positive_examples: Sequence[str]
    negative_examples: Sequence[str]

@dataclass(frozen=True)
class CriterionSpec:
    name: str
    construct: str
    decision_question: str
    evidence_policy: EvidencePolicy
    anchors: Sequence[LabelAnchor]
    hard_constraint: bool
    abstain_conditions: Sequence[str]
    required_evidence_fields: Sequence[str]
```

A production evaluator should reject an under-specified `CriterionSpec` before calling a model. This shifts some quality control from prompt craftsmanship to interface validation.
:::

## Grounding and independent commitment

### Motivation: candidate-conditioned reasoning can become anchored

A judge usually sees the candidate before it reasons about the answer. This creates an information-order problem. The candidate can frame the issue, supply a plausible intermediate calculation, or present fabricated evidence. Even a judge that eventually checks the answer may start from the candidate's narrative.

The same problem occurs in human review. A reviewer who sees a confident diagnosis before examining the evidence may search selectively for confirmation. The remedy is not simply to tell the reviewer to be unbiased. It is to change the protocol.

::: {.definition title="Anchored judgment"}
An **anchored judgment** is a judgment whose evidence search, intermediate beliefs, or decision threshold is influenced by the candidate representation before an independent evaluation target has been established.
:::

::: {.definition title="De-anchored or commit-then-compare judgment"}
A **de-anchored judgment** separates evaluation into two stages:

1. derive an independent solution, requirement set, or evidence map without access to the candidate;
2. reveal the candidate and compare it against the prior commitment.

Formally, the judge first constructs $g\sim G_\phi(\cdot\mid x,c,r)$ and then decides

$$
v\sim V_\phi(\cdot\mid x,c,r,g,y).
$$
:::

The intermediate object $g$ may be an expected answer, a list of required facts, a set of source-supported propositions, an executable test, or a proof sketch. It need not be a complete natural-language answer.

### Worked example: independent evidence map

Meridian receives the question:

> What is the maximum operating pressure for valve family Q7 under the 2024 cold-weather policy, and what inspection interval applies?

The context contains a 2019 general manual, a 2024 cold-weather addendum, and an unrelated maintenance memo. Before seeing the candidate, the judge creates:

```json
{
  "required_claims": [
    {
      "claim": "maximum pressure is 150 psi",
      "source_id": "cold-weather-2024",
      "source_span": "section 4.2",
      "authority": "controlling addendum"
    },
    {
      "claim": "inspection interval is 30 days",
      "source_id": "cold-weather-2024",
      "source_span": "section 6.1",
      "authority": "controlling addendum"
    }
  ],
  "obsolete_conflicts": [
    {
      "claim": "maximum pressure is 180 psi",
      "source_id": "manual-2019"
    }
  ]
}
```

The candidate is then revealed: “The maximum is 180 psi, with inspection every 30 days.” The judge can localize the result: one required claim is correct, one uses a superseded source, and completeness alone cannot compensate.

### Self-play reward hacking and de-anchoring

Recent work on self-play reward hacking provides unusually direct evidence for this protocol choice. In experiments where a generator optimized against reference-free LLM judges, judge approval could rise sharply while task accuracy remained poor. Requiring the judge to commit to its own solution before viewing the candidate substantially reduced false positives in the studied setting [@zhou2026selfplay].

::: {.frontier title="What the self-play result does and does not establish"}
The result does not prove that every reference-free judge will fail or that de-anchoring solves all reward hacking. It establishes a mechanism: candidate-first evaluation can expose a broad attack surface, and independent commitment can close part of it. The intervention should be tested on the actual domain, especially when the judge's independent solution may itself be unreliable.
:::

### Grounding as conditional evidence restriction

A grounded judge should state what information it is allowed to use. Let $E$ denote admissible evidence. A faithfulness verdict should approximate

$$
P(\text{claim supported}\mid E),
$$

not

$$
P(\text{claim plausible}\mid E,\text{judge's parametric memory}).
$$

Of course, an LLM cannot literally erase parametric knowledge. The protocol can nevertheless reduce leakage by requiring source-span citations, checking entailment locally, masking source metadata when appropriate, and using deterministic tools for identifiers and dates.

### Three grounding patterns

**Reference-grounded judgment** compares the candidate with a curated answer. This is useful when the reference is complete and allows paraphrase. It fails when the reference is incomplete or when multiple valid answers exist.

**Evidence-grounded judgment** compares claims with supplied sources. This is central to RAG. It requires source authority, recency, contradiction, and coverage rules.

**Tool-grounded judgment** uses an external mechanism such as a test suite, database, calculator, compiler, or search API. It can provide stronger validity but only for what the tool actually verifies.

::: {.counterexample title="Reference answers can anchor too"}
A reference says, “The contract renews annually.” The candidate correctly adds that either party may terminate with 60 days' notice, supported by the contract. A judge instructed to prefer semantic similarity to the reference may penalize the extra fact. References should be treated as evidence or requirements, not always as exhaustive surface templates.
:::

::: {.design title="Commit before exposure when a candidate can influence the standard"}
Use commit-then-compare protocols for factual correctness, mathematical reasoning, code behavior, policy interpretation, and any self-optimization loop in which the candidate can learn to shape the judge's reasoning.
:::
EOF
```

<details><summary>💭 Thinking</summary>

**Drafted and reviewed Chapter 2 with adversarial evaluation exercises**

</details>

```unknown
bash -lc cat > /mnt/data/_work/llm_judge_textbook/part3.md <<'EOF'
# Self-Optimization from Judgment

## Why judgment changes the learning problem

A judgment can be used in at least two ways. It can describe a system after development, or it can influence the next system version. The second use creates a feedback loop:

```text
system configuration
       |
       v
sample trajectories --> judge --> scores, preferences, critiques
       ^                                  |
       |                                  v
       +------------ optimizer <----------+
```

Once the evaluator enters the loop, it becomes part of the objective. A prompt optimizer searches for text that receives favorable judgments. A policy-learning algorithm raises the probability of responses preferred by the reward model. An agent learns search actions that its process judge approves. This makes evaluation quality a limiting factor in learning quality.

The goal of this chapter is to provide a common mathematical language for methods that are often presented separately: critique and revision, prompt search, textual gradients, preference optimization, reinforcement learning from AI feedback, self-rewarding models, and process reward models. The shared problem is **optimization with a semantic, noisy, and potentially manipulable oracle**.

::: {.definition title="Self-optimization"}
A language-model system performs **self-optimization** when outputs from the system itself or from an evaluator implemented substantially by language models are used to modify the system's future behavior, configuration, data, policy, or evaluator.
:::

“Self” does not necessarily mean one model instance performs every role. A generator, critic, verifier, optimizer, and meta-judge may be separate models. The defining property is that model-generated evaluation participates in the update loop.

## Levels of self-optimization

The term covers several levels with different risks.

### Level 0: inference-time selection

Generate $N$ candidates and select one:

$$
y^*=\arg\max_{y_i\sim\pi_\theta(\cdot\mid x)}
 J_\phi(x,y_i).
$$

Best-of-$N$, reranking, rejection sampling, and self-consistency belong here. The model weights and prompts remain fixed. Optimization occurs over sampled outputs.

### Level 1: inference-time revision

A critic evaluates a draft and the generator revises it:

$$
y_{t+1}\sim \pi_\theta(\cdot\mid x,y_t,f_t),
\qquad
f_t\sim C_\phi(\cdot\mid x,y_t).
$$

Self-Refine and Reflexion illustrate iterative feedback and memory patterns [@madaan2023selfrefine; @shinn2023reflexion]. No weight update is required, but the resulting trajectory is adaptive.

### Level 2: program or prompt optimization

The optimizer changes instructions, demonstrations, module wiring, retrieval parameters, or thresholds. Let $p$ denote a program configuration:

$$
p^*=\arg\max_{p\in\mathcal{P}}
\widehat U(p),
\qquad
\widehat U(p)=\frac1n\sum_{i=1}^{n}J(x_i,F_p(x_i)).
$$

OPRO, ProTeGi, DSPy optimizers, MIPROv2, TextGrad, and GEPA operate at this level in different ways [@yang2023opro; @pryzant2023protegi; @khattab2023dspy; @opsahlong2024mipro; @yuksekgonul2024textgrad; @agrawal2025gepa].

### Level 3: policy or model optimization

Judge outputs create rewards or preferences used to update model parameters:

$$
\theta^*=\arg\max_\theta
\E_{x\sim D,\,y\sim\pi_\theta}
[r_\phi(x,y)]
-\beta\,\mathcal{R}(\pi_\theta,\pi_{\mathrm{ref}}).
$$

RLHF, RLAIF, DPO, reward-model-guided distillation, self-rewarding language models, and process-supervised RL fit here.

### Level 4: evaluator co-optimization

The generator and evaluator both change. Meta-Rewarding and Self-Taught Evaluators are examples of loops in which judging ability is itself improved using generated data or meta-evaluation [@wu2024metarewarding; @wang2024selftaughtevaluators].

Let generator parameters be $\theta$ and judge parameters $\phi$:

$$
\theta_{t+1}=A(\theta_t;J_{\phi_t}),
\qquad
\phi_{t+1}=B(\phi_t;M_{\psi_t}),
$$

where $M$ is a meta-evaluator or trusted validation process. Co-adaptation can increase capability, but it can also create a closed epistemic loop in which the generator and judge agree for the same wrong reasons.

::: {.warning title="Optimization level determines validation burden"}
A judge sufficient for Level 0 selection may be unsafe for Level 3 training. Repeated updates amplify evaluator bias and move the policy away from the judge's calibration distribution. Stronger optimization requires more independent validation, tighter constraints, and more protected holdouts.
:::

::: {.example title="Five ways Meridian can improve"}
For the same policy question, Meridian can:

1. sample five answers and select the most grounded one;
2. critique a draft for missing evidence and revise it;
3. change the query-rewrite prompt and top-$k$ retrieval parameter;
4. fine-tune the answer model from judged preference pairs;
5. train a RAG-specific judge and then use that judge to train the generator.

These interventions differ in reversibility. Selection and prompt changes can be rolled back immediately. Weight updates and co-adapted evaluators can alter behavior broadly and require stronger experiments.
:::

## The optimization problem with a noisy semantic oracle

### True objective, observable proxy, and optimizer

Let $\omega\in\Omega$ denote a system configuration. It may include prompts, weights, retrieval parameters, model choices, or control logic. The true deployment objective is

$$
U(\omega)=\E_{x\sim P_{\mathrm{deploy}}}
[u(x,F_\omega(x))].
$$

The true utility $u$ is usually unavailable. We observe a proxy based on a development sample and an evaluator:

$$
\widehat U_D(\omega)
=\frac1n\sum_{i=1}^{n}
J_\phi(x_i,F_\omega(x_i);r,c_i).
$$

The optimizer proposes

$$
\omega_{t+1}=A(\omega_{0:t},\widehat U_D(\omega_{0:t}),f_{0:t}),
$$

where $f_t$ may include textual critiques. This is black-box optimization because the evaluator may be non-differentiable and the configuration may contain discrete text.

::: {.definition title="Semantic oracle"}
A **semantic oracle** is an evaluator that interprets natural-language inputs and outputs to provide a score, preference, critique, or constraint signal. It is an oracle in the optimization sense, not an infallible source of truth.
:::

### Three sources of uncertainty

The observed objective varies because of:

1. **data uncertainty:** which evaluation cases are sampled;
2. **system uncertainty:** stochastic retrieval, decoding, or tools;
3. **judge uncertainty:** evaluator sampling and model error.

A useful hierarchical estimator is

$$
\widehat U(\omega)=
\frac1n\sum_{i=1}^{n}
\frac1{m_i}\sum_{j=1}^{m_i}
\frac1{k_{ij}}\sum_{\ell=1}^{k_{ij}}
J_{ij\ell},
$$

where $m_i$ system runs and $k_{ij}$ judge runs are nested within case $i$. Variance components can be estimated separately. When most variance comes from cases, adding judge samples is wasteful; when a judge is unstable, repeated evaluation may help.

### Black-box search and multiple comparisons

Suppose an optimizer evaluates $T$ configurations on the same development set and returns the best. Even if each estimate is unbiased, the selected maximum is upward-biased. The effective number of comparisons grows with every prompt mutation and retry.

A practical correction is **nested selection**:

```text
search set        --> propose many configurations
validation set    --> select among survivors
protected test    --> estimate final performance once
production audit  --> detect distribution shift
```

The test set should not feed textual critiques back to the optimizer. Otherwise it becomes another training set.

### Bilevel optimization

Judge-guided learning is naturally bilevel when an inner procedure trains or adapts a system and an outer objective evaluates the result.

Let $\lambda$ be a prompt, rubric, retrieval setting, or training hyperparameter. The inner problem is

$$
\theta^*(\lambda)=
\arg\min_\theta L_{\mathrm{train}}(\theta;\lambda),
$$

and the outer problem is

$$
\lambda^*=\arg\min_\lambda
L_{\mathrm{val}}(\theta^*(\lambda);\lambda).
$$

If the same judge defines both losses, correlated misspecification can survive both levels. A safer design uses different information channels: model-generated feedback for the inner loop and independent human, tool, or hidden-source checks for the outer loop.

### Constrained and risk-sensitive objectives

The scalar objective

$$
\max_\omega \E[J_\phi]
$$

is rarely adequate. A more realistic formulation is

$$
\begin{aligned}
\max_\omega \quad &
\E[Q(\omega)]-\lambda_C\E[C(\omega)]-\lambda_L\E[L(\omega)]\\
\text{subject to}\quad &
P(F_k(\omega)=1)\le \delta_k,
\quad k=1,\ldots,K,
\end{aligned}
$$

where $Q$ is useful quality, $C$ cost, $L$ latency, and $F_k$ critical failure events such as unsupported claims or privacy violations.

Risk-sensitive alternatives optimize a lower quantile or conditional value at risk. For loss $Z_\omega$ and tail level $\alpha$,

$$
\operatorname{CVaR}_\alpha(Z_\omega)
=\E[Z_\omega\mid Z_\omega\ge \operatorname{VaR}_\alpha(Z_\omega)].
$$

This discourages configurations with good averages but catastrophic tails.

::: {.counterexample title="Average reward hides a critical regression"}
A prompt change improves helpfulness on 98 routine cases by 0.1 points each but causes two safety-critical cases to cite obsolete limits. The mean score rises. A constrained objective rejects the prompt because the critical-failure rate exceeds its threshold.
:::

## Critique, revision, and constitutional feedback

### Motivation: natural language preserves error structure

A scalar tells the optimizer how much a candidate was liked. A critique can explain which requirement failed and suggest an intervention. Natural language is therefore an unusually expressive optimization signal for programs whose parameters are themselves natural language.

::: {.definition title="Critique-revision operator"}
A **critique-revision operator** is a pair $(C,G)$ such that

$$
f_t\sim C(x,y_t,r,c),
\qquad
y_{t+1}\sim G(x,y_t,f_t,c),
$$

with the intent that $u(x,y_{t+1})>u(x,y_t)$.
:::

The intent does not guarantee improvement. A critic may identify a nonexistent problem, and a reviser may overcorrect.

### Self-Refine and Reflexion

Self-Refine uses iterative self-feedback and revision without additional supervised training [@madaan2023selfrefine]. Reflexion stores verbal feedback in an episodic memory to guide later agent attempts [@shinn2023reflexion]. These methods establish an important design pattern: **feedback can change inference behavior without changing weights**.

A generic loop is:

```text
ALGORITHM 3.1  Critique-revise with guarded acceptance

INPUT: x, initial generator G, critic C, verifier V, maximum rounds T

1. Generate y_0 = G(x).
2. For t = 0,...,T-1:
     a. Obtain structured critique f_t = C(x, y_t).
     b. If f_t reports no material defect, stop.
     c. Generate revision y'_t = G(x, y_t, f_t).
     d. Compare y'_t with y_t using independent verifier V.
     e. Accept y_{t+1}=y'_t only if hard constraints pass and
        V reports a positive margin; otherwise retain y_t or abstain.
3. Return the best verified version and the revision trace.
```

The guarded acceptance step is important. Unguarded iterative refinement can degrade a correct answer or accumulate unsupported detail.

::: {.example title="Revision helps only when the critique is localized"}
Meridian drafts: “The Q7 limit is 180 psi.” The critic returns:

```json
{
  "component": "source_selection",
  "defect": "obsolete_source",
  "evidence": ["manual-2019", "cold-weather-2024"],
  "instruction": "Use the controlling 2024 addendum and preserve the 30-day interval."
}
```

The revision changes the limit to 150 psi and cites the addendum. A vague critique such as “Be more accurate and detailed” could instead induce a longer answer that retains the wrong number.
:::

### Constitutional feedback

Constitutional AI uses a set of written principles to elicit critiques, revisions, and preference signals [@bai2022constitutional]. The constitution separates some normative content from individual labels.

Let principles be $R=(r_1,\ldots,r_K)$. A critique can identify a violated principle,

$$
k^*=\arg\max_k P(r_k\text{ violated}\mid x,y),
$$

then propose a revision subject to the principle set. The approach is attractive because principles are inspectable and editable. It remains dependent on interpretation: two judges can apply the same principle differently, and principles can conflict.

A practical constitution should include:

- principle priority or conflict rules;
- examples and counterexamples;
- evidence requirements;
- non-compensable constraints;
- uncertainty and abstention;
- version control and stakeholder approval.

::: {.counterexample title="A principle without precedence"}
A support assistant is told both “answer every user directly” and “do not disclose private account data.” A request for another person's billing history creates a conflict. Without precedence, a self-critic can justify either behavior. The constitution must state that privacy constrains helpfulness.
:::

### When critique loops terminate

A revision loop can oscillate. Let $T$ map a response to its revised response. A fixed point satisfies $T(y)=y$. But semantic revision operators are stochastic, and a fixed point may be mediocre rather than correct.

Useful stopping conditions include:

- no material criterion failure remains;
- verifier score fails to improve by $\epsilon$;
- hard constraints are satisfied and confidence is high;
- a cycle is detected in critique categories;
- the cost or round budget is exhausted;
- judge disagreement increases.

::: {.design title="Retain the best verified state, not merely the last state"}
Revision is not monotone. Store every version and its independent checks. Return the best feasible state according to a protected acceptance rule.
:::
EOF
```

<details><summary>💭 Thinking</summary>

**Drafted and counted Chapter 3 self-optimization content**

</details>

```unknown
bash -lc cat > /mnt/data/_work/llm_judge_textbook/part4.md <<'EOF'
# Self-Optimizing Retrieval-Augmented Generation

## Why RAG requires component-aware judgment

Retrieval-augmented generation, or RAG, is often described as a simple recipe: retrieve documents, put them in a prompt, and ask a model to answer. That description hides the central engineering problem. A final answer is produced by a chain of decisions, and the same visible error can arise from different causes.

If Meridian states an obsolete pressure limit, at least six explanations are possible:

1. the query rewrite deleted the date qualifier;
2. the retriever failed to return the current addendum;
3. the reranker preferred a lexically similar obsolete manual;
4. the context builder truncated the controlling paragraph;
5. the generator ignored the supplied evidence;
6. the citation module attached the wrong source to an otherwise correct claim.

A final-answer judge can detect that the answer is wrong. It cannot automatically identify which intervention will fix it. Self-optimizing RAG therefore requires **diagnosis over a computational graph**.

::: {.definition title="Retrieval-augmented generation"}
A **retrieval-augmented generation system** is a language-model program that conditions generation on information selected from an external corpus or tool at inference time. The retrieved information serves as non-parametric memory, evidence, or both [@lewis2020rag].
:::

::: {.definition title="Self-optimizing RAG"}
A **self-optimizing RAG system** uses model- or tool-generated evaluation signals to modify one or more retrieval, context-construction, generation, citation, or control-policy components, subject to independent validation.
:::

The phrase “subject to independent validation” is part of the definition in this book because unconstrained score maximization is not a sound engineering objective.

## A formal RAG computational graph

### From question to trace

Let $x$ be a user question and $\mathcal{C}$ a corpus of documents. A modular RAG pipeline can be represented as follows.

**Query analysis and rewriting**

$$
a\sim A_\alpha(\cdot\mid x),
\qquad
q_{1:m}\sim Q_\alpha(\cdot\mid x,a),
$$

where $a$ may contain intent, entities, time scope, authority requirements, and answerability expectations.

**Retrieval**

For document or passage $d\in\mathcal{C}$, a retriever computes

$$
s_\eta(q,d)
=\lambda s_{\mathrm{sparse}}(q,d)
+(1-\lambda)s_{\mathrm{dense},\eta}(q,d),
$$

then returns candidates

$$
D_K=\operatorname{TopK}_{d\in\mathcal{C}}
\max_j s_\eta(q_j,d).
$$

**Reranking**

$$
\tilde s_\beta(x,d,a)
=R_\beta(x,d,a),
\qquad
\tilde D_k=\operatorname{TopK}_{d\in D_K}\tilde s_\beta(x,d,a).
$$

**Context construction**

$$
c=B_\psi(x,a,\tilde D_k;L),
$$

where $L$ is a token budget. $B_\psi$ may deduplicate, compress, order, annotate, or filter passages.

**Generation**

$$
y\sim\pi_\theta(\cdot\mid x,a,c).
$$

**Claim and citation processing**

$$
(h,\kappa)\sim C_\xi(\cdot\mid x,y,c),
$$

where $h=(h_1,\ldots,h_M)$ are atomic claims and $\kappa$ maps claims to source spans.

The complete trace is

$$
\tau=(x,a,q_{1:m},D_K,\tilde D_k,c,y,h,\kappa).
$$

The program parameters are

$$
\Omega=(\alpha,\eta,\beta,\psi,\theta,\xi,L,K,k,\lambda,\ldots).
$$

Some parameters are model weights, some are prompts, and some are ordinary numbers. A self-optimizer can change any subset.

### A graphical view

```text
                         corpus C
                            |
                            v
x --> analysis a --> queries q --> retrieval D_K --> rerank D_k
|                                                    |
|                                                    v
+------------------------------------------> context builder c
                                                     |
                                                     v
                                               generator y
                                                     |
                                                     v
                                         claims h + citations kappa
                                                     |
                                                     v
                                    decomposed evaluator + optimizer
```

The graph is not always a chain. Query decomposition may branch, evidence may be retrieved iteratively, and a verifier may send the agent back to search.

### Latent causes and observed failures

Let $F$ be an observed final failure and $Z$ a latent component cause. Diagnosis seeks

$$
P(Z=z\mid F,\tau).
$$

The trace makes this posterior more identifiable. If the required passage is absent from $D_K$, the generator cannot be blamed for failing to cite it. If it is present in $c$ but contradicted by $y$, generation is implicated. If $y$ is correct but $\kappa$ points elsewhere, the citation module is implicated.

::: {.definition title="Component attribution"}
**Component attribution** is the assignment of an observed system failure to one or more upstream modules whose behavior was causally relevant to the failure and is therefore an appropriate target for intervention.
:::

Attribution is not the same as temporal precedence. An early module may behave imperfectly without causing the final failure; a downstream module may compensate. Counterfactual tests provide stronger evidence.

For component $v$, define a counterfactual trace $\tau[v\leftarrow v^*]$ in which $v$ is replaced by an oracle or alternative output while other conditions are held as constant as possible. The causal contribution can be approximated by

$$
\Delta_v
=U(\tau[v\leftarrow v^*])-U(\tau).
$$

Large $\Delta_v$ indicates that repairing $v$ could improve the outcome. Exact counterfactuals are often impossible because downstream behavior changes, but replay and ablation are informative.

::: {.example title="Counterfactual localization"}
Meridian's answer uses the obsolete 180 psi limit.

- Replaying the same generator with an oracle context containing only the 2024 addendum yields 150 psi. This implicates retrieval/context rather than generator knowledge.
- Replacing only the reranker output while retaining the original query causes the current addendum to enter the context. This localizes the primary defect to reranking.
- Replacing the citation module does not change the number. Citation formatting is not causal for this failure.

The evaluator's critique should therefore target the reranker or its authority features.
:::

### The end-to-end objective

Let $u(x,\tau)$ be true system utility. The ideal problem is

$$
\max_\Omega
\E_{x\sim P_{\mathrm{deploy}},\tau\sim F_\Omega(\cdot\mid x)}
[u(x,\tau)]
$$

subject to constraints on unsupported claims, security, cost, and latency. In practice, $u$ is approximated by a vector of measurements:

$$
\mathbf{m}(x,\tau)=
\begin{bmatrix}
\text{answer correctness}\\
\text{evidence coverage}\\
\text{faithfulness}\\
\text{citation support}\\
\text{refusal correctness}\\
-\text{latency}\\
-\text{cost}
\end{bmatrix}.
$$

The key methodological choice is which dimensions are judged at which graph nodes.

## What should be evaluated in RAG?

### Motivation: related metrics answer different questions

RAG evaluation terminology is inconsistent across libraries and papers. “Faithfulness” may refer to support by retrieved context, while “correctness” may refer to agreement with a reference or the world. “Context relevance” can mean precision among retrieved passages, usefulness to generation, or semantic similarity to the question.

The remedy is to define each quantity operationally.

### Retrieval evidence recall

Let $G(x)=\{g_1,\ldots,g_R\}$ be gold or required evidence units and $D_k(x)$ retrieved units. Evidence recall is

$$
\operatorname{ER}@k
=\frac{1}{n}\sum_{i=1}^{n}
\frac{|G(x_i)\cap D_k(x_i)|}{|G(x_i)|}.
$$

When evidence is graded, normalized discounted cumulative gain or graded recall may be more appropriate. For multi-hop questions, all required evidence may be necessary. Define an all-evidence success indicator

$$
\operatorname{AllRecall}@k
=\frac1n\sum_i
\ind[G(x_i)\subseteq D_k(x_i)].
$$

A retriever can have high average recall while frequently missing one decisive hop.

### Evidence precision and purity

If $R(x,d)\in\{0,1\}$ indicates relevance,

$$
\operatorname{EP}@k
=\frac{1}{nk}\sum_{i=1}^{n}
\sum_{d\in D_k(x_i)}R(x_i,d).
$$

In RAG, irrelevance is not the only contaminant. A passage may be topically relevant but obsolete, low-authority, contradictory, or injected with malicious instructions. Define a utility label

$$
u(x,d)\in
\{\text{supporting},\text{contradicting},\text{obsolete},
\text{irrelevant},\text{unsafe}\}.
$$

**Evidence purity** measures the fraction of context that is admissible and useful under the task's authority rules.

### Context relevance versus context utility

A passage can be semantically relevant but not useful to the generator. Conversely, a short table row may have low lexical similarity but supply the exact answer. We distinguish:

::: {.definition title="Context relevance"}
**Context relevance** is the degree to which a passage concerns the information need expressed by the question.
:::

::: {.definition title="Context utility"}
**Context utility** is the causal contribution of a passage to producing a better answer for a particular generator and context-construction policy.
:::

A counterfactual utility estimate is

$$
\Delta U(d)
=\E[J(y\mid c\cup\{d\})]
-
\E[J(y\mid c\setminus\{d\})].
$$

This quantity is reader-dependent. A passage useful to one generator may confuse another.

### Answer correctness

Answer correctness compares claims with an authoritative target, not merely the supplied context. If $h_1,\ldots,h_M$ are material claims and $z_j\in\{0,1\}$ indicates correctness,

$$
\operatorname{Correctness}(y)
=\frac{\sum_j w_j z_j}{\sum_j w_j}.
$$

Weights $w_j$ reflect materiality. A critical pressure limit should not be diluted by several trivial correct statements.

### Faithfulness and claim support

Let $S_{j\ell}\in\{-1,0,1\}$ indicate whether evidence span $e_\ell$ contradicts, is neutral to, or supports claim $h_j$. Then

$$
\operatorname{Supported}(h_j)
=\ind[\max_\ell S_{j\ell}=1],
$$

and

$$
\operatorname{Contradicted}(h_j)
=\ind[\min_\ell S_{j\ell}=-1].
$$

Weighted support is

$$
\operatorname{Faithfulness}(y,c)
=\frac{\sum_j w_j\operatorname{Supported}(h_j)}{\sum_j w_j},
$$

with a separate contradiction rate. Combining unsupported and contradicted claims into one score hides severity.

### Completeness

Let $R(x)=\{r_1,\ldots,r_P\}$ be required answer elements. Completeness is

$$
\operatorname{Completeness}(y)
=\frac{\sum_p v_p\ind[y\text{ satisfies }r_p]}{\sum_p v_p}.
$$

Requirements may come from a reference, independently derived evidence map, user instruction, or domain schema. A complete answer can still be wrong; a faithful answer can be incomplete.

### Citation precision, recall, and entailment

Let $A_j$ be the set of citations attached to claim $h_j$.

- **Citation coverage** measures whether material claims have citations.
- **Citation precision** measures whether cited sources support the attached claims.
- **Citation recall** measures whether available supporting evidence is cited when required.
- **Citation correctness** includes source identity, section, version, and span validity.

A citation-link support indicator is

$$
C_{j\ell}=
\ind[e_\ell\in A_j]
\ind[e_\ell\text{ entails }h_j].
$$

Then weighted citation precision is

$$
\frac{\sum_j w_j\sum_{e_\ell\in A_j}C_{j\ell}}
{\sum_j w_j|A_j|},
$$

with conventions for uncited claims handled separately.

### Refusal correctness and answerability

A RAG system must sometimes refuse because the corpus does not contain sufficient authoritative evidence. Let $a(x,c)\in\{0,1\}$ indicate answerability. The system decision $\hat a$ creates four cases:

| True answerability | System answers | Interpretation |
|---|---|---|
| answerable | yes | potentially correct response |
| answerable | no | unnecessary refusal |
| unanswerable | no | correct refusal |
| unanswerable | yes | unsupported-answer risk |

Refusal quality also includes whether the system explains what is missing and suggests an appropriate next step without fabricating.

### RAG evaluation frameworks

RAGAS introduced reference-free or weakly supervised metrics for aspects such as faithfulness, answer relevance, and context relevance [@es2023ragas]. ARES uses synthetic data and lightweight judges for context relevance, answer faithfulness, and answer relevance, with statistical estimation ideas for target datasets [@saadfalcon2023ares]. RAGChecker decomposes retrieval and generation behavior into diagnostic metrics, emphasizing the interaction between retriever and generator [@ru2024ragchecker].

These frameworks are valuable because they reject one-number evaluation. Their metric names should still be mapped to the local operational definitions above. Library defaults do not determine the construct for a regulated or domain-specific system.

::: {.example title="A metric vector tells a causal story"}
After a Meridian update, metrics change as follows:

| Metric | Before | After |
|---|---:|---:|
| Evidence recall | 0.82 | 0.91 |
| Evidence purity | 0.88 | 0.74 |
| Faithfulness | 0.90 | 0.86 |
| Completeness | 0.76 | 0.88 |
| Correctness | 0.84 | 0.85 |

The new retriever finds more required facts but introduces distracting passages. The generator uses some of that noise, so completeness improves while faithfulness falls. A single overall score could conceal the need for better reranking or context filtering.
:::

::: {.counterexample title="Faithful to false context"}
The supplied context says the pressure limit is 180 psi, and the answer repeats 180 psi exactly. The answer is faithful to context but incorrect with respect to the controlling 2024 source. Faithfulness is not a substitute for source authority and world correctness.
:::
EOF
```

<details><summary>💭 Thinking</summary>

**Drafted and evaluated Chapter 4 with case studies and citations**

</details>

```json
{"open":[{"ref_id":"https://arxiv.org/abs/2607.05904"},{"ref_id":"https://arxiv.org/abs/2607.13347"},{"ref_id":"https://arxiv.org/abs/2605.12474"},{"ref_id":"https://arxiv.org/abs/2607.21324"},{"ref_id":"https://arxiv.org/abs/2604.02091"},{"ref_id":"https://arxiv.org/abs/2601.21912"},{"ref_id":"https://arxiv.org/abs/2606.01629"},{"ref_id":"https://arxiv.org/abs/2606.19544"},{"ref_id":"https://arxiv.org/abs/2511.21140"},{"ref_id":"https://arxiv.org/abs/2509.26011"},{"ref_id":"https://arxiv.org/abs/2507.19457"},{"ref_id":"https://arxiv.org/abs/2505.14069"},{"ref_id":"https://arxiv.org/abs/2505.10320"},{"ref_id":"https://arxiv.org/abs
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

```unknown
bash -lc cat > /mnt/data/_work/llm_judge_textbook/part5.md <<'EOF'
\backmatter

# Glossary {-}

This glossary gives compact operational definitions. The chapter text provides motivation, examples, and limitations.

**Abstention.** A judge or system decision not to issue a forced verdict because evidence is insufficient, the case is outside scope, or calibrated uncertainty is too high. Abstention trades coverage for lower error among automated decisions.

**Agentic judge.** An evaluator implemented as a sequential policy that may decompose criteria, retrieve evidence, call tools, compare claims, and decide when to stop.

**Agentic RAG.** A retrieval-augmented system that performs multiple adaptive search, evidence, tool, or reasoning actions before answering or refusing.

**Aggregation rule.** The procedure that combines criterion scores, judge samples, pairwise comparisons, tools, or human labels into a reported judgment. Examples include majority vote, weighted vote, constrained utility, and lexicographic ordering.

**All-evidence recall.** The fraction of cases for which every required evidence unit is present in the retrieved set. It is stricter than average evidence recall and useful for multi-hop questions.

**Anchoring.** Dependence of a judgment on a candidate-provided framing or answer before the judge has established an independent standard.

**Answerability.** Whether the available admissible evidence is sufficient to answer a question under the task's authority and confidence rules.

**Bradley-Terry-Luce model.** A probabilistic preference model in which the probability that candidate $i$ beats candidate $j$ is $\sigma(q_i-q_j)$ for latent scores $q_i$ and $q_j$.

**Brier score.** The mean squared error between predicted probabilities and binary outcomes. It measures both calibration and discrimination.

**Calibration.** Agreement between predicted confidence and empirical correctness. A calibrated 0.8 prediction is correct approximately 80% of the time on comparable cases.

**Candidate.** A response, trajectory, document set, program version, or other object presented for evaluation or selection.

**Citation coverage.** The extent to which claims that require citations actually have them.

**Citation precision.** The fraction of attached citations that support the claims to which they are attached.

**Claim-evidence matrix.** A matrix whose rows are atomic claims and columns are source spans, with entries representing support, contradiction, or neutrality.

**Component attribution.** Assignment of an observed RAG failure to one or more causally relevant modules that are appropriate intervention targets.

**Consistent accuracy.** Pairwise judge accuracy requiring the same correct semantic winner under both candidate orders.

**Construct.** A latent concept intended to be measured, such as helpfulness, correctness, or resolution quality. A construct is operationalized through criteria and decision rules.

**Context builder.** The RAG component that selects, orders, deduplicates, annotates, or compresses retrieved passages under a context budget.

**Context relevance.** The degree to which supplied evidence concerns the information need expressed by the question.

**Context utility.** The causal contribution of a passage or context to downstream answer quality for a particular generator and pipeline.

**Controlled corruption.** A synthetic-data method that creates a known negative example by making one targeted change, such as altering a number, deleting an exception, or replacing a current source with an obsolete one.

**Coverage.** In selective prediction, the fraction of cases for which an automated judgment is issued rather than abstained.

**Critic.** An evaluator that produces diagnostic natural-language feedback intended to identify a defect or guide a revision.

**Criterion.** A specific operational dimension used to measure a construct, such as claim support, evidence recall, or refusal correctness.

**Dawid-Skene model.** A latent-label model that jointly estimates unknown labels and annotator confusion matrices, usually under conditional-independence assumptions.

**De-anchored judgment.** An evaluation protocol that establishes an independent solution, requirement set, or evidence map before revealing the candidate.

**Direct Preference Optimization (DPO).** A policy-training objective that increases the relative likelihood of preferred responses over rejected responses with respect to a reference policy, without requiring a separately deployed scalar reward model.

**Domain shift.** A material difference between calibration or training data and deployment data, including changes in tasks, languages, lengths, model families, evidence formats, or error prevalence.

**Elo rating.** An online rating system that updates latent candidate strengths from pairwise outcomes. Its assumptions resemble a dynamic Bradley-Terry model.

**Evidence ledger.** A structured agent state listing requirements, supporting and contradicting sources, authority, unresolved gaps, and provenance.

**Evidence precision.** The fraction of retrieved or selected evidence that is relevant and admissible for the task.

**Evidence purity.** The fraction or quality of a context that is useful and admissible after accounting for irrelevance, contradiction, obsolescence, unsafe content, and low-authority sources.

**Evidence recall.** The fraction of required evidence units that are retrieved or included in context.

**Evaluation procedure.** The complete system from sampling and presentation through rubric, judging, aggregation, and uncertainty reporting.

**Evaluand.** The object being evaluated: an answer, reasoning step, retrieved set, trajectory, model, or complete program.

**Evaluator validity.** The extent to which evaluator outputs support the intended interpretation and decision for a specified population.

**Expected value of information.** The expected reduction in decision loss from acquiring an additional label, search result, tool output, or human review, net of its cost.

**Faithfulness.** Support of a response's claims by the supplied admissible context. Faithfulness is distinct from world correctness.

**Generative reward model.** A reward model that produces a critique, analysis, or reasoning trace before or together with a reward or preference.

**Goodhart pressure.** The tendency for a proxy's relationship with the intended objective to deteriorate when the proxy is heavily optimized.

**Grounded judge.** A judge whose verdict is explicitly constrained by supplied references, source evidence, tools, or other admissible information.

**Hard constraint.** A criterion threshold that cannot be compensated for by gains in soft objectives. Examples include zero access-control violations or a maximum contradiction rate.

**Hidden holdout.** Evaluation data whose inputs, labels, critiques, and outcomes remain inaccessible to the optimizer until a pre-specified final decision.

**Inference-time scaling.** Allocation of additional evaluation compute through longer deliberation, multiple samples, tools, debate, or adaptive verification.

**Intransitive preference.** A preference cycle such as $A\succ B$, $B\succ C$, and $C\succ A$, often caused by multidimensional tradeoffs or criterion instability.

**Judge.** A procedure mapping an evaluand and evaluation specification to a score, label, ranking, rationale, confidence, or abstention.

**Judge card.** A versioned document describing a judge's intended uses, construct, rubric, model, calibration, performance, limitations, thresholds, and change-control rules.

**Judge-generalization matrix.** A matrix whose entry $G_{ij}$ measures how a configuration optimized against judge $j$ performs under judge or validator $i$.

**Latent quality.** An unobserved scalar or vector representing the underlying property an evaluator seeks to estimate.

**Listwise evaluation.** A protocol in which a judge orders or scores a set of three or more candidates jointly.

**Meta-evaluation.** Evaluation of a judge against human adjudication, verifiable outcomes, controlled perturbations, or another trusted standard.

**Meta-judge.** An evaluator that judges another judgment, rationale, rubric application, or evaluator.

**Meta-rewarding.** A self-improvement approach in which meta-preferences over judgments are used to improve judging ability while response preferences improve the generator.

**Metamorphic test.** A test that transforms an input or presentation while preserving the correct semantic judgment, thereby testing invariance.

**Multi-objective optimization.** Optimization over several quality, risk, cost, or latency dimensions without assuming one fixed scalar tradeoff.

**Optimizer's curse.** Upward bias in the observed value of the selected maximum, caused by choosing the candidate with the most favorable estimation error among many trials.

**Outcome supervision.** Training or evaluation based only on the final result of a trajectory.

**Pairwise evaluation.** Direct comparison of two candidates under an explicit criterion or rubric.

**Pareto frontier.** The set of configurations not dominated by another configuration on every objective.

**Pointwise evaluation.** Independent scoring or labeling of one candidate at a time.

**Prediction-powered inference.** A statistical framework that combines many inexpensive model predictions with a smaller probability sample of trusted labels to estimate population quantities with bias correction and uncertainty.

**Preference leakage.** Improper influence of candidate identity, model family, style, or familiarity on a judge's preference.

**Process reward model (PRM).** An evaluator that scores intermediate states, actions, or transitions rather than only a final outcome.

**Process supervision.** Use of labels or rewards for intermediate decisions in a trajectory to improve credit assignment.

**Prompt optimizer.** A procedure that searches or edits instructions, demonstrations, schemas, or other textual program variables using evaluation feedback.

**RAG.** See retrieval-augmented generation.

**Reasoning judge.** A judge trained or prompted to perform deliberate intermediate evaluation work before emitting a verdict.

**Reference answer.** A curated answer supplied as one evidence channel. It may be exhaustive, partial, or fallible and should be described accordingly.

**Reliability.** Stability or agreement of measurements under repeated or comparable conditions. Reliability does not imply validity.

**Reranker.** A RAG component that reorders retrieved candidates using a more expensive or task-aware scoring function.

**Retrieval-augmented generation.** Generation conditioned on evidence selected from an external corpus or tool at inference time.

**Reward hacking.** Increase in measured reward without a corresponding increase in the intended objective, caused by exploitation of the reward mechanism or its specification.

**Reward model.** A learned or prompted evaluator whose output is used for selection or training.

**RLAIF.** Reinforcement learning from AI feedback, in which model-generated judgments replace or supplement human feedback.

**RLHF.** Reinforcement learning from human feedback.

**Rubric.** A specification of criteria, admissible evidence, label semantics, decision rules, exceptions, and aggregation.

**Selective risk.** Error conditional on the evaluator choosing to issue an automated judgment rather than abstain.

**Self-rewarding language model.** A model trained through iterations in which it generates responses, judges them, constructs preference data, and updates itself or a related policy.

**Self-taught evaluator.** An evaluator improved using synthetic contrasting responses and generated evaluation rationales, potentially without initial human preference labels.

**Semantic oracle.** A language-model evaluator used as a black-box source of scores, preferences, critiques, or constraints; the term does not imply infallibility.

**Source authority.** The degree to which a source controls or establishes the answer under domain rules, based on provenance, role, date, jurisdiction, and supersession.

**Stochastic language-model program.** A composition of deterministic and stochastic modules that maps an input to an output and trace.

**Textual gradient.** A natural-language diagnosis associated with a program variable that proposes a direction of change expected to reduce downstream loss.

**Textual gradient blocking.** Prevention of feedback propagation to a component when trace evidence does not support a causal attribution.

**Trace.** A structured record of intermediate queries, retrieved documents, tool calls, context, outputs, citations, scores, versions, and timing produced by a language-model program.

**Verifier.** A procedure that checks a proposition against an external constraint or source of truth, such as execution, a database, a source span, or a formal rule.

**Version drift.** Change in behavior caused by updates to an underlying model, prompt, tool, corpus, or API that alter the evaluation or serving procedure.

# Selected hints and solutions {-}

The solutions below illustrate reasoning patterns rather than exhaust all valid answers.

## Chapter 1

### Exercise 1.2: reliability without validity

A judge always assigns factual-correctness score 5 to every answer. It has perfect test-retest reliability because repeated evaluations never differ. It has no discriminative validity: correct and incorrect answers receive the same score.

A benchmark can accidentally report success if almost every sampled answer is correct. Suppose 98 of 100 answers pass and the benchmark converts score 5 to `pass`. Accuracy is 98%, but sensitivity to failures is zero and Cohen's kappa is zero because the evaluator adds no information beyond the majority class. The example shows why confusion matrices, prevalence, and construct probes are required.

### Exercise 1.3: optimizer's curse

Using $\sqrt{2\log B}$:

$$
\begin{aligned}
B=10 &: \sqrt{2\log 10}\approx2.15,\\
B=100 &: \sqrt{2\log 100}\approx3.03,\\
B=10{,}000 &: \sqrt{2\log 10{,}000}\approx4.29.
\end{aligned}
$$

This is an asymptotic approximation and is too high for small $B$, but the direction is correct: searching more equally good candidates raises the selected noise. A large prompt-search budget therefore needs nested validation rather than confidence based on the winning development score.

### Exercise 1.6: kappa under imbalance

The always-pass judge has accuracy $990/1000=0.99$. If failure is the positive class, sensitivity is $0/10=0$ and specificity is $990/990=1$. Observed agreement is $p_o=0.99$. Both judge and reference assign pass with probabilities $1$ and $0.99$, so chance agreement is $p_e=0.99$. Therefore

$$
\kappa=\frac{p_o-p_e}{1-p_e}=0.
$$

High accuracy is entirely explained by prevalence.

### Hints for remaining Chapter 1 exercises

- **1.1:** Begin with the decision the support team makes after seeing the metric. Separate correctness from user effort and tone.
- **1.4:** Differentiate each log-sigmoid term; add a zero-sum constraint such as $\sum_iq_i=0$ for identifiability.
- **1.5:** Give each candidate a different strength: correctness, completeness, and concision. Let the implicit criterion change across pairs.
- **1.7:** Solve $\hat p=\mathrm{Se}\,p+(1-\mathrm{Sp})(1-p)$ for $p$; instability occurs when $\mathrm{Se}+\mathrm{Sp}\approx1$.
- **1.8:** Sort cases by confidence and evaluate prefixes from highest to lowest confidence.
- **1.9:** Mark materiality before computing support so trivial claims do not dominate.
- **1.10:** A point is Pareto-dominated only if another configuration is no worse on every dimension.
- **1.11–1.12:** Treat prompts, model versions, sampling, aggregation, and uncertainty as part of the artifact.

## Chapter 2

### Exercise 2.3: compensability

Let candidate A have safety $0$, helpfulness $1$, and style $1$. Let candidate B have safety $1$, helpfulness $0.7$, and style $0.6$. Under weighted sum

$$
S=w_s\,\text{safety}+w_h\,\text{helpfulness}+w_t\,\text{style},
$$

A beats B when

$$
w_h+w_t>w_s+0.7w_h+0.6w_t,
$$

or

$$
0.3w_h+0.4w_t>w_s.
$$

Many plausible weights satisfy this inequality. A hard safety constraint rejects A regardless of its polish.

### Exercise 2.7: prevalence shift

With sensitivity $0.90$ and specificity $0.95$,

$$
\mathrm{PPV}=\frac{0.9\pi}{0.9\pi+0.05(1-\pi)}.
$$

This gives approximately:

| Failure prevalence | PPV |
|---:|---:|
| 0.50 | 0.947 |
| 0.10 | 0.667 |
| 0.01 | 0.154 |

At 1% prevalence, most alerts are false positives despite strong sensitivity and specificity. Production alerting therefore needs calibrated priors, confirmatory checks, or selective review.

### Exercise 2.8: consistent accuracy

Average order accuracy is $(0.84+0.86)/2=0.85$. Consistent accuracy is $0.76$. The second number is more relevant to an optimization loop because a candidate should not win merely because the optimizer happened to place it in a favored position.

### Hints for remaining Chapter 2 exercises

- **2.1:** Ask whether the criterion can be mechanically verified before choosing an LLM.
- **2.2:** Define exactly what evidence may be used and what happens when evidence is missing.
- **2.4:** The independent artifact can be a test suite, required-fact list, source map, or independently solved answer.
- **2.5:** Model shared error with a latent Bernoulli event that makes all judges wrong together.
- **2.6:** Include random intercepts for cases; test whether presentation features have nonzero fixed effects.
- **2.9:** In the E-step infer posterior labels; in the M-step update expected confusion counts.
- **2.10:** Choose thresholds from a calibration set, not from the deployment set whose performance is being reported.
- **2.11–2.12:** Include attacks on the rubric, evidence, presentation, and control channel.

## Chapter 3

### Exercise 3.3: multiple comparisons

If validation noise is Gaussian with standard deviation $0.02$, the selected-noise approximation for $B=100$ is

$$
0.02\sqrt{2\log100}
\approx0.02(3.03)
\approx0.061.
$$

Thus an apparent six-point gain can arise from selecting among equally good prompts under the approximation. A nested design uses one set for search, a second for selecting a small shortlist, and an untouched test for one final estimate.

### Exercise 3.8: DPO gradient

For one pair, define

$$
z=\beta\left[
\log\pi_\theta(y_w\mid x)-\log\pi_\theta(y_l\mid x)
-\log\pi_{\mathrm{ref}}(y_w\mid x)
+\log\pi_{\mathrm{ref}}(y_l\mid x)
\right].
$$

The loss is $-\log\sigma(z)$. Since

$$
\frac{d}{dz}[-\log\sigma(z)]=\sigma(z)-1,
$$

we obtain

$$
\frac{\partial L}{\partial\log\pi_\theta(y_w\mid x)}
=\beta(\sigma(z)-1),
$$

and

$$
\frac{\partial L}{\partial\log\pi_\theta(y_l\mid x)}
=-\beta(\sigma(z)-1).
$$

Gradient descent therefore increases the preferred log-probability and decreases the rejected one when the preference is not already strongly satisfied. Larger $\beta$ creates a steeper preference pressure relative to the reference.

### Exercise 3.10: potential shaping

For finite horizon $T$,

$$
\sum_{t=0}^{T-1}\gamma^t
[\gamma\Phi(s_{t+1})-\Phi(s_t)]
=-\Phi(s_0)+\gamma^T\Phi(s_T).
$$

The intermediate terms cancel. Under the standard assumptions, the shaping changes returns by endpoint terms and can preserve optimal policies. If $\Phi$ is estimated by a biased judge that rewards the number of retrieved passages rather than resolved requirements, the agent may bloat context while appearing to make progress.

### Hints for remaining Chapter 3 exercises

- **3.1:** Reversibility and distribution shift generally decrease as the level increases.
- **3.2:** Use a random-effects model with case, system run within case, and judge run within system run.
- **3.4:** Put training performance in the inner objective and protected end-to-end utility in the outer objective.
- **3.5:** Let the critic distrust a correct concise answer because it expects a longer form.
- **3.6:** Trace where information first disappears before assigning a textual gradient.
- **3.7:** Report the number of mutations tried; otherwise the winning result is uninterpretable.
- **3.9:** Preserve the original positive and change one causal property per negative.
- **3.11:** Diagonal-only gains are evidence of judge-specific adaptation.
- **3.12:** A rollback decision is part of the algorithm, not an optional operations note.

## Chapter 4

### Exercise 4.3: evidence metrics

Suppose required evidence is $G=\{g_1,g_2,g_3\}$ and the top-five list contains $g_1$, one obsolete variant of $g_2$, two irrelevant passages, and $g_3$. Under exact admissible matching, evidence recall is $2/3$ because the obsolete variant does not satisfy $g_2$. Precision is $2/5$. All-evidence success is zero. A purity score might assign utilities $+1$ to admissible support, $-1$ to obsolete or contradictory evidence, and $0$ to irrelevant evidence, yielding

$$
\operatorname{PurityUtility}
=\frac{1+(-1)+0+0+1}{5}=0.2.
$$

The exact scoring rule must be declared; the example shows why binary topical relevance is insufficient.

### Exercise 4.10: textual gradient blocking

Use the earliest-loss rule as a first diagnostic: find the earliest node at which required information becomes absent, distorted, or ignored.

- If the gold passage never enters retrieval, update query/retriever and block generator pressure to state the missing fact.
- If the passage is retrieved but dropped by context packing, update the context builder.
- If the claim contradicts visible evidence, update the generator.
- If the answer is correct but the cited span is wrong, freeze the answer and update citation alignment.
- If the corpus lacks the source, update ingestion or refusal; do not tune retrieval against nonexistent evidence.

Counterfactual replay should be used before high-impact changes.

### Exercise 4.12: evidence-ledger stopping

A simple rule answers when every material requirement is resolved by at least one admissible source, no unresolved high-authority contradiction remains, and the expected value of another query is below cost. It refuses when a critical requirement remains unresolved after the bounded search policy or when all available sources lack authority. It asks for clarification when the unresolved variable belongs to the user's intent rather than the corpus.

### Hints for remaining Chapter 4 exercises

- **4.1:** Include corpus ingestion and access filtering; they are often omitted from diagrams.
- **4.2:** Replays provide likelihood evidence, not certainty about one cause.
- **4.4:** Obsolete but highly relevant evidence is a reliable construction.
- **4.5:** Calibrate claim states separately by context length and failure type.
- **4.6:** Store the exact transformation that created each negative.
- **4.7:** Preserve dates, entities, negation, jurisdiction, and relation type.
- **4.8:** Test whether utility labels transfer across readers; otherwise the reranker may overfit one generator.
- **4.9:** Greedy selection should reward marginal required-fact coverage and penalize redundancy.
- **4.11:** Report interactions, not only the best of eight cells.
- **4.13:** Charge for queries and reward verified new ledger entries.
- **4.14:** Separate controls for serving, judging, and optimization channels.
- **4.15:** The protected test should be revealed only after the graph is frozen.

# References {-}
EOF
```

<details><summary>💭 Thinking</summary>

**Created glossary and back matter draft**

</details>

```json
{"open":[{"ref_id":"https://arxiv.org/abs/2407.10930"},{"ref_id":"https://arxiv.org/abs/2407.19594"},{"ref_id":"https://arxiv.org/abs/2406.11695"},{"ref_id":"https://arxiv.org/abs/2410.12784"},{"ref_id":"https://arxiv.org/abs/2408.08067"},{"ref_id":"https://arxiv.org/abs/2311.09476"},{"ref_id":"https://arxiv.org/abs/2309.15217"},{"ref_id":"https://arxiv.org/abs/2310.07641"},{"ref_id":"https://arxiv.org/abs/2404.13076"},{"ref_id":"https://arxiv.org/abs/2403.13787"},{"ref_id":"https://arxiv.org/abs/2405.01535"},{"ref_id":"https://arxiv.org/abs/2310.08491"},{"ref_id":"https://arxiv.org/abs/2310.17631"},{"ref_id":"https://
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

```unknown
bash -lc cat > /mnt/data/_work/llm_judge_textbook/references.bib <<'EOF'
@misc{zheng2023judge,
  author = {Zheng, Lianmin and Chiang, Wei-Lin and Sheng, Ying and Zhuang, Siyuan and Wu, Zhanghao and Zhuang, Yonghao and Lin, Zi and Li, Zhuohan and Li, Dacheng and Xing, Eric P. and Zhang, Hao and Gonzalez, Joseph E. and Stoica, Ion},
  title = {Judging {LLM}-as-a-Judge with {MT-Bench} and Chatbot Arena},
  year = {2023},
  note = {arXiv:2306.05685},
  url = {https://arxiv.org/abs/2306.05685}
}

@misc{liu2023geval,
  author = {Liu, Yang and Iter, Dan and Xu, Yichong and Wang, Shuohang and Xu, Ruochen and Zhu, Chenguang},
  title = {{G-Eval}: {NLG} Evaluation Using {GPT-4} with Better Human Alignment},
  year = {2023},
  note = {arXiv:2303.16634},
  url = {https://arxiv.org/abs/2303.16634}
}

@misc{kim2023prometheus,
  author = {Kim, Seungone and others},
  title = {Prometheus: Inducing Fine-Grained Evaluation Capability in Language Models},
  year = {2023},
  note = {arXiv:2310.08491},
  url = {https://arxiv.org/abs/2310.08491}
}

@misc{kim2024prometheus2,
  author = {Kim, Seungone and others},
  title = {Prometheus 2: An Open Source Language Model Specialized in Evaluating Other Language Models},
  year = {2024},
  note = {arXiv:2405.01535},
  url = {https://arxiv.org/abs/2405.01535}
}

@misc{zeng2023llmbar,
  author = {Zeng, Zhiyuan and others},
  title = {Evaluating Large Language Models at Evaluating Instruction Following},
  year = {2023},
  note = {arXiv:2310.07641; introduces LLMBar},
  url = {https://arxiv.org/abs/2310.07641}
}

@misc{tan2024judgebench,
  author = {Tan, Sijun and others},
  title = {JudgeBench: A Benchmark for Evaluating {LLM}-Based Judges},
  year = {2024},
  note = {arXiv:2410.12784},
  url = {https://arxiv.org/abs/2410.12784}
}

@inproceedings{lewis2020rag,
  author = {Lewis, Patrick and Perez, Ethan and Piktus, Aleksandra and Petroni, Fabio and Karpukhin, Vladimir and Goyal, Naman and K{"u}ttler, Heinrich and Lewis, Mike and Yih, Wen-tau and Rockt{"a}schel, Tim and Riedel, Sebastian and Kiela, Douwe},
  title = {Retrieval-Augmented Generation for Knowledge-Intensive {NLP} Tasks},
  booktitle = {Advances in Neural Information Processing Systems},
  year = {2020},
  url = {https://arxiv.org/abs/2005.11401}
}

@inproceedings{karpukhin2020dpr,
  author = {Karpukhin, Vladimir and Oguz, Barlas and Min, Sewon and Lewis, Patrick and Wu, Ledell and Edunov, Sergey and Chen, Danqi and Yih, Wen-tau},
  title = {Dense Passage Retrieval for Open-Domain Question Answering},
  booktitle = {Proceedings of EMNLP},
  year = {2020},
  url = {https://arxiv.org/abs/2004.04906}
}

@misc{norman2026reliability,
  author = {Norman, Justin D. and Rivera, Michael U. and Hughes, D. Alex},
  title = {Reliability without Validity: A Systematic, Large-Scale Evaluation of {LLM}-as-a-Judge Models Across Agreement, Consistency, and Bias},
  year = {2026},
  note = {arXiv:2606.19544},
  url = {https://arxiv.org/abs/2606.19544}
}

@misc{chen2026longjudge,
  author = {Chen, Junjie and Dong, Yuxi and Li, Haitao and Su, Weihang and Zhou, Yujia and Zhang, Min and Liu, Yiqun and Ai, Qingyao},
  title = {Benchmarking {LLM}-as-a-Judge for Long-Form Output Evaluation},
  year = {2026},
  note = {arXiv:2606.01629},
  url = {https://arxiv.org/abs/2606.01629}
}

@misc{lee2025reportjudge,
  author = {Lee, Chungpa and Zeng, Thomas and Jeong, Jongwon and Sohn, Jy-yong and Lee, Kangwook},
  title = {How to Correctly Report {LLM}-as-a-Judge Evaluations},
  year = {2025},
  note = {arXiv:2511.21140, revised 2026},
  url = {https://arxiv.org/abs/2511.21140}
}

@misc{saadfalcon2023ares,
  author = {Saad-Falcon, Jon and Khattab, Omar and Potts, Christopher and Zaharia, Matei},
  title = {{ARES}: An Automated Evaluation Framework for Retrieval-Augmented Generation Systems},
  year = {2023},
  note = {arXiv:2311.09476},
  url = {https://arxiv.org/abs/2311.09476}
}

@article{angelopoulos2023ppi,
  author = {Angelopoulos, Anastasios N. and Bates, Stephen and Jordan, Michael I. and Malik, Jitendra and Zrnic, Tijana},
  title = {Prediction-Powered Inference},
  journal = {Science},
  year = {2023},
  volume = {382},
  number = {6671},
  pages = {669--674}
}

@article{brier1950,
  author = {Brier, Glenn W.},
  title = {Verification of Forecasts Expressed in Terms of Probability},
  journal = {Monthly Weather Review},
  year = {1950},
  volume = {78},
  number = {1},
  pages = {1--3}
}

@article{cohen1960,
  author = {Cohen, Jacob},
  title = {A Coefficient of Agreement for Nominal Scales},
  journal = {Educational and Psychological Measurement},
  year = {1960},
  volume = {20},
  number = {1},
  pages = {37--46}
}

@misc{es2023ragas,
  author = {Es, Shahul and James, Jithin and Espinosa-Anke, Luis and Schockaert, Steven},
  title = {Ragas: Automated Evaluation of Retrieval Augmented Generation},
  year = {2023},
  note = {arXiv:2309.15217},
  url = {https://arxiv.org/abs/2309.15217}
}

@misc{ru2024ragchecker,
  author = {Ru, Dongyu and others},
  title = {{RAGChecker}: A Fine-Grained Framework for Diagnosing Retrieval-Augmented Generation},
  year = {2024},
  note = {arXiv:2408.08067},
  url = {https://arxiv.org/abs/2408.08067}
}

@misc{xu2025contextual,
  author = {Xu, Austin and Bansal, Srijan and Ming, Yifei and Yavuz, Semih and Joty, Shafiq},
  title = {Does Context Matter? {ContextualJudgeBench} for Evaluating {LLM}-Based Judges in Contextual Settings},
  year = {2025},
  note = {arXiv:2503.15620},
  url = {https://arxiv.org/abs/2503.15620}
}

@misc{coman2025ragferee,
  author = {Coman, Andrei C. and Sorodoc, Ionut-Teodor and Ribeiro, Leonardo F. R. and Byrne, Bill and Henderson, James and de Gispert, Adri{ E0}},
  title = {{RAGferee}: Building Contextual Reward Models for Retrieval-Augmented Generation},
  year = {2025},
  note = {arXiv:2509.26011},
  url = {https://arxiv.org/abs/2509.26011}
}

@misc{wang2023pandalm,
  author = {Wang, Yidong and others},
  title = {{PandaLM}: An Automatic Evaluation Benchmark for {LLM} Instruction Tuning Optimization},
  year = {2023},
  note = {arXiv:2306.05087},
  url = {https://arxiv.org/abs/2306.05087}
}

@misc{zhu2023judgelm,
  author = {Zhu, Lianghui and others},
  title = {{JudgeLM}: Fine-Tuned Large Language Models Are Scalable Judges},
  year = {2023},
  note = {arXiv:2310.17631},
  url = {https://arxiv.org/abs/2310.17631}
}

@misc{wang2023faireval,
  author = {Wang, Peiyi and others},
  title = {Large Language Models Are Not Fair Evaluators},
  year = {2023},
  note = {arXiv:2305.17926},
  url = {https://arxiv.org/abs/2305.17926}
}

@misc{panickssery2024selfpreference,
  author = {Panickssery, Arjun and Bowman, Samuel R. and Feng, Shi},
  title = {{LLM} Evaluators Recognize and Favor Their Own Generations},
  year = {2024},
  note = {arXiv:2404.13076},
  url = {https://arxiv.org/abs/2404.13076}
}

@misc{lambert2024rewardbench,
  author = {Lambert, Nathan and others},
  title = {{RewardBench}: Evaluating Reward Models for Language Modeling},
  year = {2024},
  note = {arXiv:2403.13787},
  url = {https://arxiv.org/abs/2403.13787}
}

@misc{liu2025deepseekgrm,
  author = {Liu, Zijun and Wang, Peiyi and Xu, Runxin and Ma, Shirong and Ruan, Chong and Li, Peng and Liu, Yang and Wu, Yu},
  title = {Inference-Time Scaling for Generalist Reward Modeling},
  year = {2025},
  note = {arXiv:2504.02495},
  url = {https://arxiv.org/abs/2504.02495}
}

@misc{chen2025rmr1,
  author = {Chen, Xiusi and others},
  title = {{RM-R1}: Reward Modeling as Reasoning},
  year = {2025},
  note = {arXiv:2505.02387},
  url = {https://arxiv.org/abs/2505.02387}
}

@misc{whitehouse2025j1,
  author = {Whitehouse, Chenxi and Wang, Tianlu and Yu, Ping and Li, Xian and Weston, Jason and Kulikov, Ilia and Saha, Swarnadeep},
  title = {{J1}: Incentivizing Thinking in {LLM}-as-a-Judge via Reinforcement Learning},
  year = {2025},
  note = {arXiv:2505.10320},
  url = {https://arxiv.org/abs/2505.10320}
}

@misc{guo2025rrm,
  author = {Guo, Jiaxin and Chi, Zewen and Dong, Li and Dong, Qingxiu and Wu, Xun and Huang, Shaohan and Wei, Furu},
  title = {Reward Reasoning Model},
  year = {2025},
  note = {arXiv:2505.14674},
  url = {https://arxiv.org/abs/2505.14674}
}

@article{dawidskene1979,
  author = {Dawid, Alexander P. and Skene, Allan M.},
  title = {Maximum Likelihood Estimation of Observer Error-Rates Using the {EM} Algorithm},
  journal = {Journal of the Royal Statistical Society: Series C (Applied Statistics)},
  year = {1979},
  volume = {28},
  number = {1},
  pages = {20--28}
}

@misc{zhou2026selfplay,
  author = {Zhou, Chenyu},
  title = {More Convincing, Not More Correct: Self-Play Reward Hacking of Reference-Free {LLM} Judges},
  year = {2026},
  note = {arXiv:2607.05904},
  url = {https://arxiv.org/abs/2607.05904}
}

@misc{huang2026judgeobjective,
  author = {Kim, Donghwan},
  title = {{LLM}-as-a-Judge Scores Are Unreliable Optimization Signals in Closed-Loop Table Recognition},
  year = {2026},
  note = {arXiv:2607.13347},
  url = {https://arxiv.org/abs/2607.13347}
}

@misc{li2026rubrichacking,
  author = {Mahmoud, Anas and Rezaei, MohammadHossein and Wang, Zihao and Gunjal, Anisha and Liu, Bing and He, Yunzhong},
  title = {Reward Hacking in Rubric-Based Reinforcement Learning},
  year = {2026},
  note = {arXiv:2605.12474},
  url = {https://arxiv.org/abs/2605.12474}
}

@inproceedings{skalse2022rewardhacking,
  author = {Skalse, Joar and Howe, Nikolaus H. R. and Krasheninnikov, Dmitrii and Krueger, David},
  title = {Defining and Characterizing Reward Hacking},
  booktitle = {Advances in Neural Information Processing Systems},
  year = {2022},
  url = {https://arxiv.org/abs/2209.13085}
}

@misc{madaan2023selfrefine,
  author = {Madaan, Aman and others},
  title = {Self-Refine: Iterative Refinement with Self-Feedback},
  year = {2023},
  note = {arXiv:2303.17651},
  url = {https://arxiv.org/abs/2303.17651}
}

@misc{shinn2023reflexion,
  author = {Shinn, Noah and Cassano, Federico and Gopinath, Ashwin and Narasimhan, Karthik and Yao, Shunyu},
  title = {Reflexion: Language Agents with Verbal Reinforcement Learning},
  year = {2023},
  note = {arXiv:2303.11366},
  url = {https://arxiv.org/abs/2303.11366}
}

@misc{bai2022constitutional,
  author = {Bai, Yuntao and others},
  title = {Constitutional {AI}: Harmlessness from {AI} Feedback},
  year = {2022},
  note = {arXiv:2212.08073},
  url = {https://arxiv.org/abs/2212.08073}
}

@misc{yang2023opro,
  author = {Yang, Chengrun and Wang, Xuezhi and Lu, Yifeng and Liu, Hanxiao and Le, Quoc V. and Zhou, Denny and Chen, Xinyun},
  title = {Large Language Models as Optimizers},
  year = {2023},
  note = {arXiv:2309.03409; introduces OPRO},
  url = {https://arxiv.org/abs/2309.03409}
}

@misc{pryzant2023protegi,
  author = {Pryzant, Reid and Iter, Dan and Li, Jerry and Lee, Yin Tat and Zhu, Chenguang and Zeng, Michael},
  title = {Automatic Prompt Optimization with ``Gradient Descent'' and Beam Search},
  year = {2023},
  note = {arXiv:2305.03495; introduces ProTeGi},
  url = {https://arxiv.org/abs/2305.03495}
}

@misc{khattab2023dspy,
  author = {Khattab, Omar and Singhvi, Arnav and Maheshwari, Paridhi and Zhang, Zhiyuan and Santhanam, Keshav and Vardhamanan, Sri and Haq, Saiful and Sharma, Ashutosh and Josifoski, Martin and Guestrin, Carlos and Zaharia, Matei},
  title = {{DSPy}: Compiling Declarative Language Model Calls into Self-Improving Pipelines},
  year = {2023},
  note = {arXiv:2310.03714},
  url = {https://arxiv.org/abs/2310.03714}
}

@misc{opsahlong2024mipro,
  author = {Opsahl-Ong, Krista and Ryan, Michael J. and Purtell, Josh and Broman, David and Potts, Christopher and Zaharia, Matei and Khattab, Omar},
  title = {Optimizing Instructions and Demonstrations for Multi-Stage Language Model Programs},
  year = {2024},
  note = {arXiv:2406.11695; introduces MIPRO},
  url = {https://arxiv.org/abs/2406.11695}
}

@misc{yuksekgonul2024textgrad,
  author = {Yuksekgonul, Mert and others},
  title = {{TextGrad}: Automatic ``Differentiation'' via Text},
  year = {2024},
  note = {arXiv:2406.07496},
  url = {https://arxiv.org/abs/2406.07496}
}

@misc{agrawal2025gepa,
  author = {Agrawal, Lakshya A. and others},
  title = {{GEPA}: Reflective Prompt Evolution Can Outperform Reinforcement Learning},
  year = {2025},
  note = {arXiv:2507.19457; revised 2026},
  url = {https://arxiv.org/abs/2507.19457}
}

@inproceedings{lin2024bettertogether,
  author = {Soylu, Dilara and Potts, Christopher and Khattab, Omar},
  title = {Fine-Tuning and Prompt Optimization: Two Great Steps That Work Better Together},
  booktitle = {Proceedings of EMNLP},
  year = {2024},
  url = {https://arxiv.org/abs/2407.10930}
}

@misc{rafailov2023dpo,
  author = {Rafailov, Rafael and Sharma, Archit and Mitchell, Eric and Manning, Christopher D. and Ermon, Stefano and Finn, Chelsea},
  title = {Direct Preference Optimization: Your Language Model Is Secretly a Reward Model},
  year = {2023},
  note = {arXiv:2305.18290},
  url = {https://arxiv.org/abs/2305.18290}
}

@misc{lee2023rlaif,
  author = {Lee, Harrison and others},
  title = {{RLAIF} vs. {RLHF}: Scaling Reinforcement Learning from Human Feedback with {AI} Feedback},
  year = {2023},
  note = {arXiv:2309.00267},
  url = {https://arxiv.org/abs/2309.00267}
}

@misc{yuan2024selfrewarding,
  author = {Yuan, Weizhe and others},
  title = {Self-Rewarding Language Models},
  year = {2024},
  note = {arXiv:2401.10020},
  url = {https://arxiv.org/abs/2401.10020}
}

@misc{wu2024metarewarding,
  author = {Wu, Tianhao and Yuan, Weizhe and Golovneva, Olga and Xu, Jing and Tian, Yuandong and Jiao, Jiantao and Weston, Jason and Sukhbaatar, Sainbayar},
  title = {Meta-Rewarding Language Models: Self-Improving Alignment with {LLM}-as-a-Meta-Judge},
  year = {2024},
  note = {arXiv:2407.19594},
  url = {https://arxiv.org/abs/2407.19594}
}

@misc{wang2024selftaughtevaluators,
  author = {Wang, Tianlu and Kulikov, Ilia and Golovneva, Olga and Yu, Ping and Yuan, Weizhe and Dwivedi-Yu, Jane and Pang, Richard Yuanzhe and Fazel-Zarandi, Maryam and Weston, Jason and Li, Xian},
  title = {Self-Taught Evaluators},
  year = {2024},
  note = {arXiv:2408.02666},
  url = {https://arxiv.org/abs/2408.02666}
}

@misc{zhao2024figret,
  author = {Liu, Yuhang and Hu, Xueyu and Zhang, Shengyu and Chen, Jingyuan and Wu, Fan and Wu, Fei},
  title = {Fine-Grained Guidance for Retrievers: Leveraging {LLM}s' Feedback in Retrieval-Augmented Generation},
  year = {2024},
  note = {arXiv:2411.03957},
  url = {https://arxiv.org/abs/2411.03957}
}

@misc{chen2026rrpo,
  author = {Wu, Yuhang and Shen, Xiangqing and Wang, Fanfan and Zhou, Cangqi and Wu, Zhen and Dai, Xinyu and Xia, Rui},
  title = {Optimizing {RAG} Rerankers with {LLM} Feedback via Reinforcement Learning},
  year = {2026},
  note = {arXiv:2604.02091},
  url = {https://arxiv.org/abs/2604.02091}
}

@misc{liu2026gradrag,
  author = {Pedinotti, Paolo and Santus, Enrico},
  title = {{GRADRAG}: Cross-Component Prompt Adaptation for Coordinated Multi-Agent {RAG}},
  year = {2026},
  note = {arXiv:2607.21324},
  url = {https://arxiv.org/abs/2607.21324}
}

@misc{jin2025raggym,
  author = {Xiong, Guangzhi and Jin, Qiao and Wang, Xiao and Fang, Yin and Liu, Haolin and Yang, Yifan and Chen, Fangyuan and Song, Zhixing and Wang, Dengyu and Zhang, Minjia and Lu, Zhiyong and Zhang, Aidong},
  title = {Supervising the Search Process Produces Reliable and Generalizable Information-Seeking Agents},
  year = {2025},
  note = {arXiv:2502.13957; revised 2026},
  url = {https://arxiv.org/abs/2502.13957}
}

@misc{zhang2025reasonrag,
  author = {Zhang, Wenlin and others},
  title = {Process vs. Outcome Reward: Which Is Better for Agentic {RAG} Reinforcement Learning},
  year = {2025},
  note = {arXiv:2505.14069},
  url = {https://arxiv.org/abs/2505.14069}
}

@misc{liu2026prorag,
  author = {Wang, Zhao and Zhao, Ziliang and Dou, Zhicheng},
  title = {{ProRAG}: Process-Supervised Reinforcement Learning for Retrieval-Augmented Generation},
  year = {2026},
  note = {arXiv:2601.21912},
  url = {https://arxiv.org/abs/2601.21912}
}
EOF
```

<details><summary>💭 Thinking</summary>

**Rebuilt and inspected the textbook PDF, fixing references and formatting issues**

**Auditing and refining**

I’m checking the compiled book for layout issues, citation consistency, readable chapter openings, callout rendering, equations, code, tables, and references before delivering the final Markdown and PDF files.

</details>

```unknown
bash -lc ls -lh /mnt/data/_work/llm_judge_textbook && echo '--- counts ---' && wc -w /mnt/data/_work/llm_judge_textbook/part*.md /mnt/data/_work/llm_judge_textbook/textbook_draft1.md && echo '--- pdf skill check ---' && head -80 /home/oai/skills/pdfs/SKILL.md
```

<details><summary>💭 Thinking</summary>

**Inspected textbook files, headings, insertions, formatting, and glossary definitions**

</details>

The revised manuscript is about 30,000 words and compiles to 99 pages, with glossary, research map, solutions, and implementation material added. I’m now doing final visual QA.

```unknown
from pathlib import Path
import re, json, collections, textwrap, os, statistics, math
base=Path('/mnt/data/_work/llm_judge_textbook')
parts=['part0_1.md','part2.md','part3.md','part4.md','part5.md']
for p in parts:
    txt=(base/p).read_text()
    counts=collections.Counter(re.findall(r'^:::\s+\{\.(\w+)', txt, re.M))
    print(p, len(txt.split()), counts)

```

<details><summary>💭 Thinking</summary>

**Audited textbook definitions and examples**

</details>

```unknown
bash -lc python - <<'PY'
from pathlib import Path
import re, collections
base=Path('/mnt/data/_work/llm_judge_textbook')
for p in ['part0_1.md','part2.md','part3.md','part4.md','part5.md']:
    txt=(base/p).read_text()
    counts=collections.Counter(re.findall(r'^:::\s+\{\.(\w+)', txt, re.M))
    print(p, len(txt.split()), dict(counts))
PY
```

<details><summary>💭 Thinking</summary>

**Searched mounted storage for textbook analysis and recovered source files**

**Listed available conversation files**

</details>

```json
{"search_query":[{"q":"site:arxiv.org LLM as a Judge survey 2025 2026 meta evaluation reliability validity"},{"q":"site:arxiv.org 2606 LLM judge reliability validity long form evaluation"},{"q":"site:arxiv.org 2025 How to Correctly Report LLM-as-a-Judge Evaluations"},{"q":"site:arxiv.org 2026 reward hacking LLM judge self play rubric based"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 2 websites**

</details>

```unknown
bash -lc mkdir -p /mnt/data/llm_judge_book_work && echo test > /mnt/data/llm_judge_book_work/persist.txt && ls -l /mnt/data/llm_judge_book_work
```

<details><summary>💭 Thinking</summary>

**Created a LaTeX textbook on LLM judges and self-optimizing RAG systems**

**Auditing final materials**

I’m completing the final consistency check across the reconstructed textbook: chapter balance, pedagogical callouts, equations, references, layout, and the required Markdown/PDF deliverables.

**Auditing textbook content**

I’m checking chapter coverage, terminology, references, examples, exercises, and production safeguards. I’m also verifying that the final Markdown and PDF compile cleanly and that the layout remains readable throughout.

**Audited final materials and textbook content**

</details>

```unknown
bash -lc ls -lah /mnt/data/llm_judge_book_work && wc -w /mnt/data/llm_judge_book_work/part*.md && sed -n '1,80p' /mnt/data/llm_judge_book_work/header.tex && sed -n '1,120p' /mnt/data/llm_judge_book_work/callouts.lua
```

<details><summary>💭 Thinking</summary>

**Inspected book files, LaTeX structure, and PDF guidelines**

</details>

```json
{"search_query":[{"q":"site:arxiv.org/abs/2309.17012 title"},{"q":"site:arxiv.org/abs/2606.19544 LLM judge reliability validity"},{"q":"site:arxiv.org/abs/2606.27226 BinEval LLM judge"},{"q":"site:arxiv.org/abs/2606.14278 language switching LLM judge"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

```unknown
bash -lc sed -n '330,430p' /mnt/data/llm_judge_book_work/part5.md && grep -RInE "LLMBar|Norman|BinEval|BINEVAL|2606\.19544|2309\.17012|2310\.07641" /mnt/data/llm_judge_book_work/part*.md
```

<details><summary>💭 Thinking</summary>

**Audited documentation structure, terminology, references, and citations**

</details>

```json
{"search_query":[{"q":"site:arxiv.org/abs/2606.01629 title"},{"q":"site:arxiv.org/abs/2505.02387 title"},{"q":"site:arxiv.org/abs/2509.26011 title"},{"q":"site:arxiv.org/abs/2505.14674 title"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

```unknown
bash -lc python - <<'PY'
from pathlib import Path
import re
base=Path('/mnt/data/llm_judge_book_work')
for n in range(1,5):
    lines=(base/f'part{n}.md').read_text().splitlines()
    print('\nPART',n)
    for i,l in enumerate(lines):
        m=re.match(r'^:::\s*\{\.definition(?:\s+title="([^"]+)")?\}',l)
        if m:
            title=m.group(1) or ''
            # get first paragraph until blank or close
            j=i+1; content=[]
            while j<len(lines) and lines[j].strip()!=':::' and len(content)<6:
                if lines[j].strip(): content.append(lines[j].strip())
                j+=1
            print(f'{i+1}: {title} ::', ' '.join(content)[:240])
PY
```

<details><summary>💭 Thinking</summary>

**Extracted and inspected definitions and design callouts across chapters**

</details>

```json
{"search_query":[{"q":"site:arxiv.org/abs/2607.21324 title"},{"q":"site:arxiv.org/abs/2604.02091 title"},{"q":"site:arxiv.org/abs/2601.21912 title"},{"q":"site:arxiv.org/abs/2607.05904 title"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

```unknown
bash -lc nl -ba /mnt/data/llm_judge_book_work/part1.md | sed -n '175,270p' && nl -ba /mnt/data/llm_judge_book_work/part1.md | sed -n '360,470p'
```

# Language Models as Judges and Optimizers

The completed textbook contains approximately **32,400 words across 99 PDF pages**. It is organized into four main chapters:

1. **Foundations of Machine Judgment** — measurement theory, latent utility, pointwise/pairwise/listwise protocols, reliability, validity, calibration, bias, uncertainty, and defensible judge design.
2. **From Judgment to Learning Signal** — reward modeling, preference learning, DPO, RLHF/RLAIF, process supervision, self-rewarding models, meta-evaluation, Goodhart effects, and reward hacking.
3. **Optimizing Compound Language-Model Systems** — stochastic computation graphs, bilevel and multiobjective optimization, textual gradients, semantic credit assignment, GEPA/DSPy-style optimization, search algorithms, validation, and promotion gates.
4. **LLM Judges and Self-Optimization for RAG** — formal RAG models, retrieval and generation metrics, claim-evidence graphs, contextual judges, reranker optimization, agentic RAG, cross-component feedback, and a production-oriented self-optimizing architecture.

It also includes 68 formal definitions, worked examples, counterexamples, mathematical derivations, pseudocode, typed API interfaces, 14 diagrams, four exercise sets, a glossary, selected solution sketches, and a primary-source bibliography. Recent 2025–2026 results are identified as recent research or preprints where appropriate.

- [Download the Markdown textbook](sandbox:/mnt/data/Language_Models_as_Judges_and_Optimizers/Language_Models_as_Judges_and_Optimizers.md)
- [Download the PDF textbook](sandbox:/mnt/data/Language_Models_as_Judges_and_Optimizers/Language_Models_as_Judges_and_Optimizers.pdf)
- [Download the portable Markdown source package with all diagrams](sandbox:/mnt/data/Language_Models_as_Judges_and_Optimizers_Source.zip)

