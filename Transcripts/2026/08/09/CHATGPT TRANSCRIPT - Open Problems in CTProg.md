# Open Problems in CT+Prog

- URL: https://chatgpt.com/c/6a78a320-73dc-83ea-886c-89585e7ae2df
- Created: 2026-08-09T15:56:38.260Z

---

> Open problems in category theory + programming, like things that need proving or so

I’ll give you research-grade examples, not vague “interesting areas”: problems where there is a concrete theorem, construction, coherence result, or completeness result still to prove.

```json
{"system1_search_query":[{"q":"site:arxiv.org category theory programming languages \"open problem\" categorical semantics"},{"q":"site:arxiv.org \"future work\" categorical semantics programming languages coherence"},{"q":"site:lmcs.episciences.org categorical semantics open problem programming languages"},{"q":"site:dl.acm.org categorical semantics programming languages open problem"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 4 websites**

</details>

A useful split is: **denotational semantics**, **type theory/coherence**, and **categorical operational semantics**. The first and third tend to produce the most recognizably “programming-language” theorems.

```json
{"system1_search_query":[{"q":"site:arxiv.org Markov categories programming semantics open problem recursion 2024 2025 2026"},{"q":"site:arxiv.org categorical semantics probabilistic programming \"open problem\" 2025 2026"},{"q":"site:arxiv.org category theory programming languages conjecture semantics 2026"},{"q":"site:arxiv.org categorical semantics differentiable programming \"open problem\" 2024 2025"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 2 websites**

**Formulating proof targets**

I’m organizing concrete research-shaped problems: commutativity for probabilistic semantics, higher-order GSOS full abstraction, coproduct-free iteration, internal ∞-categorical syntax, normalization criteria, and stronger completeness results for effect-handler semantics.

**Formulated proof targets**

</details>

Yes. There are several genuine **category theory × programming-languages problems** where the desired output is essentially “prove theorem X” rather than build another library.

1. **Is the valuations monad on `DCPO` commutative?**  
   Let \(V\) be the probabilistic valuations monad on directed-complete partial orders. The problem is to prove or disprove the appropriate categorical Fubini law, roughly
   \[
   \int_X\int_Y f(x,y)\,d\nu(y)\,d\mu(x)
   =
   \int_Y\int_X f(x,y)\,d\mu(x)\,d\nu(y).
   \]
   This matters because commutative monads give a clean semantics in which independent probabilistic computations can be reordered. Recent work still describes commutativity of the ordinary valuations monad on all `DCPO`s as open. citeturn768994search32  
   **Difficulty:** very high. **Flavor:** domain theory + probability + monads.

2. **Prove a general full-abstraction theorem for higher-order bialgebraic semantics.**  
   A 2026 categorical semantics framework gives adequate denotational models for higher-order languages. In first-order bialgebraic semantics, preservation of weak pullbacks gives a general route to full abstraction; the authors explicitly leave the corresponding higher-order theorem for future work. citeturn591760search5  
   A clean research question is:
   \[
   \text{What categorical hypotheses on }B
   \implies
   \text{denotational equality}=\text{contextual/bisimulation equality}?
   \]
   **Difficulty:** high, but unusually well-specified. **Flavor:** coalgebras + operational semantics + lambda calculus.

3. **Develop nondeterministic iteration categorically without assuming coproducts.**  
   Current categorical accounts of iteration/tests use coproducts in an essential way. Goncharov et al. explicitly say that finding the appropriate general definition without coproducts remains open. citeturn824438search12  
   You would want to propose an abstract structure \(C\) carrying an iteration operator
   \[
   (-)^* : C(X,X)\to C(X,X)
   \]
   with suitable Conway/Kleene-style laws, then prove representation or completeness results without relying on \(X+Y\).  
   **Difficulty:** medium-high. **Flavor:** categorical algebra + semantics of loops/nondeterminism.

4. **Make HoTT “eat itself.”**  
   Ordinary categories are insufficient for modelling dependent type theory internally once identity proofs themselves have higher structure. The goal is an internal theory of \(\infty\)-categories / \(\infty\)-categories-with-families strong enough to represent the syntax and semantics of the ambient type theory. A 2025 paper still notes that defining the needed internal type of \(\infty\)-categories remains open. citeturn824438search1  
   One especially concrete subproblem from earlier work is to prove **initiality of the internal syntax** as an \(\infty\)-CwF; this was left conjectural. citeturn824438academia40  
   **Difficulty:** extreme. **Flavor:** higher category theory + HoTT + proof assistants.

5. **Find general conditions guaranteeing normalization and coherence for \(\infty\)-type theories.**  
   Uemura developed normalization/coherence machinery for higher-dimensional type theories, but explicitly left finding a satisfactory general sufficient condition as future work. citeturn768994search13  
   The dream theorem looks something like:
   \[
   T\text{ satisfies categorical properties }P_1,\dots,P_n
   \quad\Longrightarrow\quad
   T\text{ has normalization + coherence}.
   \]
   This is interesting programmatically because normalization underlies type checking, definitional equality, and implementation of proof assistants.  
   **Difficulty:** extreme. **Flavor:** categorical proof theory + higher categories.

6. **Extend complete categorical semantics of effect handlers.**  
   Kura's 2026 work gives sound-and-complete categorical semantics for a particular equational theory of algebraic effect handlers, including models beyond the usual free-monad semantics. citeturn676497academia40 A strong next theorem would be to get similarly sharp completeness results for **higher-order, scoped, parameterized, or concurrent handlers**. Higher-order effect handlers now have sophisticated categorical/calculus formulations, making this a fairly concrete frontier rather than a vague suggestion. citeturn933887search17  
   For example:
   \[
   M\models t=u
   \quad\Longleftrightarrow\quad
   \text{the handler calculus proves }t=u
   \]
   for every model \(M\) in the right categorical class.  
   **Difficulty:** medium-high to high. **Flavor:** monads + algebraic theories + practical PL effects.

7. **Categorify compiler correctness for higher-order languages.**  
   Higher-order GSOS gives categorical descriptions of operational semantics using higher-order analogues of distributive laws. Earlier work explicitly proposed developing a notion of morphism between these laws so that a compiler itself could become a categorical morphism whose laws imply semantic preservation. citeturn591760search7  
   The theorem you would ultimately want is something like
   \[
   \llbracket\mathrm{compile}(p)\rrbracket_T
   =
   F(\llbracket p\rrbracket_S)
   \]
   **by abstract categorical reasoning**, rather than proving compiler correctness independently for every source language.  
   **Difficulty:** high. **Flavor:** category theory + compiler verification.

For something **actually attackable as a first research project**, I would look hardest at **#3 or a restricted version of #6**. #2 is an excellent PhD-scale semantics problem. #1 is deceptively short to state but notoriously difficult. #4–5 are deep enough that you would normally enter through a much smaller lemma rather than try to solve the headline problem immediately.

A particularly good project format would be: choose one of these, identify a deliberately restricted special case, **state the missing theorem precisely, implement all definitions in Lean/Agda/Rocq, and attempt a mechanized proof**. That gives you programming and actual new category-theoretic mathematics in the same project.


---

> Like, conjectures?

```json
{"system2_search_query":[{"q":"site:arxiv.org category theory programming languages conjecture semantics type theory categorical conjecture"},{"q":"site:arxiv.org \"conjecture\" \"category\" \"type theory\" programming languages"},{"q":"site:arxiv.org \"conjecture\" categorical semantics programming languages"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

**Identifying conjectures**

I’m interpreting the request as seeking named open conjectures at the category theory–programming languages intersection. I’m weighing examples involving probability, nondeterminism, type theory, univalence, normalization, and categorical semantics, while avoiding overclaiming their current status.

**Identified conjectures**

</details>

```json
{"system2_search_query":[{"q":"2026 \"valuations monad\" commutativity open problem DCPO"},{"q":"2025 \"valuations monad\" commutative DCPO open"},{"q":"site:arxiv.org 2026 \"V : DCPO\" commutative valuations monad"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Searched 15 websites**

</details>

Yes—if you mean **explicit mathematical statements believed true but not proved**, that is a narrower and better target. The previous list mixed those with broader open research directions.

```json
{"system2_search_query":[{"q":"\"Conjecture 6.20\" \"Topology in Synthetic Domain Theory\""},{"q":"\"sobriomorphisms\" conjecture synthetic domain theory"},{"q":"site:arxiv.org/html/2607.17292 Conjecture 6.20"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Searched 10 websites**

</details>

Exactly. You mean **conjectures: clean statements with a definite true/false answer**, rather than broad “develop a theory of X” problems.

There are some good ones at the category-theory/programming boundary, although this field has fewer universally famous named conjectures than number theory.

1. **Commutativity of the Jones–Plotkin valuation monad.**  
   Let
   \[
   V:\mathbf{DCPO}\to\mathbf{DCPO}
   \]
   be the monad of continuous valuations used to model probabilistic computation.

   The conjecture-shaped question is simply:
   \[
   \boxed{V\text{ is a commutative monad.}}
   \]

   Equivalently, prove a Fubini theorem saying that for suitable valuations \(\mu,\nu\),
   \[
   \int_X\!\int_Y f(x,y)\,d\nu\,d\mu
   =
   \int_Y\!\int_X f(x,y)\,d\mu\,d\nu.
   \]

   This has been open since the original probabilistic-powerdomain work of the late 1980s; modern work constructs smaller commutative submonads because the full statement remains unresolved. citeturn500563search6turn500563search5

   This is probably the cleanest **“prove or find a counterexample” category theory + programming conjecture** I know.

2. **Cubical conservativity conjecture.**  
   Roughly:
   \[
   \boxed{\text{Cubical type theory is conservative over ordinary HoTT.}}
   \]

   In other words, if you use the extra interval/cubical machinery that makes univalence computational and prove a statement expressible in ordinary HoTT, you should not thereby acquire genuinely new ordinary-HoTT theorems.

   A July 2026 paper explicitly calls this one of the central open problems of homotopy type theory and develops a possible route to proving it. citeturn724346academia0

   This one connects **category theory + dependent types + Agda/Lean-style proof assistants** extremely directly.

3. **Voevodsky's Initiality Conjecture.**  
   Given a dependent type theory \(T\), construct its syntactic model
   \[
   \mathcal S_T.
   \]
   The desired theorem is essentially
   \[
   \boxed{\mathcal S_T\text{ is initial in the appropriate category of models of }T.}
   \]

   Meaning: for every semantic model \(M\), there is a unique structure-preserving interpretation
   \[
   \mathcal S_T\longrightarrow M.
   \]

   It sounds almost tautological, but making “the appropriate category of models” and the uniqueness/coherence precise for serious dependent type theories is subtle. Many instances and related conjectures have been proved, but the general initiality program is still active; even 2026 work explicitly situates new results in Voevodsky's Initiality Conjecture project. citeturn716138academia12turn724346search1

4. **Escardó's nondeterminism + probability semidecidability conjecture.**  
   Individually, higher-order **may testing**, **must testing**, and **probabilistic testing** can be semidecidable. The difficult combined question asks whether analogous testing remains semidecidable when a language simultaneously has nondeterministic and probabilistic choice.

   Schematically:
   \[
   \boxed{\text{may/must probabilistic testing is semidecidable}}
   \]
   for the appropriate higher-order mixed language.

   Escardó's original work established the separate cases and made progress on the combined setting. Recent categorical/domain-theoretic work still refers to the mixed version as Escardó's conjecture and proves related special cases for probabilistic concurrency. citeturn194112search22turn340999search0

5. A very new one is a proposed **synthetic-domain-theory completeness conjecture**. Recent work formalized in Cubical Agda proposes a completeness principle intended to connect **Segal-style categorical completeness** with **chain completeness from domain theory**. citeturn666967academia12

So if you're looking for something analogous to an undergraduate being told:

> “Here is a precise statement. Nobody knows whether it's true. Go prove/disprove it.”

then **#1 is especially close to that format**:

\[
\boxed{\textbf{Conjecture: The continuous valuation monad }V\textbf{ on DCPO is commutative.}}
\]

It has a tiny statement, a very concrete programming interpretation (“does order of independent probabilistic effects matter?”), and a nontrivial category-theoretic formulation.

I can also give you **10–20 actual conjectures of this kind**, ranked from “possibly approachable by a strong undergrad” to “major PhD/open problem.”


---

> Ok

<details><summary>💭 Thinking</summary>

**Ranking conjectures**

I’m interpreting “OK” as approval to proceed. I’ll rank 10–20 explicit, currently meaningful conjectures connecting programming-language semantics, category theory, and type theory, while separating established results from genuine open problems.

**Ranked conjectures**

</details>

I’ll make the distinction strict: each item below will be a **specific proposition/open yes–no statement**, not merely “develop a theory.” I’ll also separate statements explicitly called conjectures from closely equivalent open questions.

```json
{"system1_search_query":[{"q":"site:arxiv.org category theory programming languages conjecture type theory semantics \"Conjecture\""},{"q":"site:arxiv.org \"open problem\" \"valuation monad\" DCPO commutative"},{"q":"site:arxiv.org cubical type theory conservativity conjecture HoTT"},{"q":"site:arxiv.org Voevodsky Initiality Conjecture type theory models"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 6 websites**

</details>

The strongest candidates are already emerging: probabilistic semantics has a decades-old Fubini/commutativity problem, while several 2024–26 papers state much smaller conjectures that look more plausible as thesis-sized proof projects.

```json
{"screenshot":[{"ref_id":"turn697560view0","pageno":24},{"ref_id":"turn340433view0","pageno":16},{"ref_id":"turn340433view2","pageno":60},{"ref_id":"turn340433view1","pageno":35}],"response_length":"short"}
```

<details><summary>💭 Thinking</summary>

**Searching arxiv.org**

**Ranking conjectures**

I’m ranking specific yes-or-no statements, from specialized thesis-sized questions to major problems. I’m distinguishing named conjectures from closely related open questions, and I’m avoiding vague research directions.

**Assessing candidates**

I’m narrowing this to explicit technical propositions: monad commutativity, cubical conservativity, probabilistic testing semidecidability, univalent reference-type models, and adequacy for higher-order effect handlers.

**Sharpening the list**

I’m adding five more concrete candidates: effect-handler adequacy, synthetic predomains, infinite-dimensional traced categories, and higher-container coherence. I’ll flag newer conjectures whose status may have changed.

**Ranking remaining conjectures**

I’m placing the newest, most thesis-shaped statements first, then broader foundational problems. Some are explicitly labeled conjectures; others are longstanding open questions whose exact formulations still need refinement.

**Ranked and refined the conjecture candidates**

</details>

```json
{"system1_search_query":[{"q":"site:arxiv.org 2607.17292 \"Conjecture 6.20\" synthetic predomain"},{"q":"site:arxiv.org 2511.05739 \"Conjecture E.4\" adequate"},{"q":"site:arxiv.org \"Towards Univalent Reference Types\" \"Conjecture 4.1\""},{"q":"site:arxiv.org 2503.05790 \"Conjecture 5.0.10\" container model"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

Here’s a stricter list. These are statements you can reasonably write as **“Conjecture: …”** and try to prove or refute. I’m ranking them roughly by how contained the problem looks, **not** by mathematical importance. None is genuinely an easy undergraduate problem; the first few are simply the least enormous.

1. **Synthetic predomain orthogonality conjecture — very attractive “prove/disprove” problem.**  
   For the synthetic-domain-theory notions in Xue's 2026 work:
   \[
   \boxed{
   A\text{ is a synthetic predomain}
   \iff
   A\perp(\Lambda_\omega\hookrightarrow\bar\omega).
   }
   \]
   This is literally Conjecture 6.20. The author explicitly says it **may be false**, so constructing a counterexample is a legitimate solution. Much of the surrounding development is already formalized in Cubical Agda. citeturn903661search0

   **Prerequisites:** category/type theory, domain theory, some HoTT.  
   **Why I like it:** narrow statement, brand-new, formalization exists nearby.

2. **Adequacy of recursive higher-order effect handlers.**  
   Yang defines a realizability model of the calculus \(rF^\omega_{ha}\), which has higher-order handlers and general recursion. Conjecture E.4 says, essentially,
   \[
   \boxed{
   \llbracket c\rrbracket=\texttt{true}
   \Longrightarrow
   c=\texttt{val true},
   }
   \]
   and similarly for false, for closed Boolean programs. The paper even suggests a prospective proof technique: synthetic Tait computability inside the effective topos. citeturn903661search1

   **Prerequisites:** lambda calculus, monads, realizability/topos theory.  
   **Scale:** plausible PhD-paper problem rather than a lifetime problem.

3. **Full abstraction for nonlinear stabilizer quantum programs.**  
   Booth and Comfort's Conjecture 72 is extremely clean. For well-formed programs \(c,d\) of NLSPL:
   \[
   \boxed{
   c\approx_{\mathrm{obs}}d
   \iff
   \llbracket c\rrbracket=\llbracket d\rrbracket .
   }
   \]
   Here observational equivalence means that the programs permit exactly the same possible quantum-measurement outcomes, while the denotations live in a category of relations built from stabilizer quantum mechanics. citeturn818590search0

   **Prerequisites:** symmetric monoidal categories, linear algebra/quantum information, semantics.  
   **Nice feature:** you know exactly what success looks like: prove both implications or find two programs separating them.

4. **Completeness of CCTT for comprehension categories.**  
   Najmaei, van der Weide, Ahrens and North construct *comprehension category type theory* (CCTT), prove its categorical semantics sound, and conjecture that the syntax is complete for the intended comprehension-category semantics. citeturn935448search3

   Schematically:
   \[
   \boxed{
   \Gamma\models_{\text{all CCTT models}}J
   \Longrightarrow
   \Gamma\vdash_{\mathrm{CCTT}}J.
   }
   \]

   This is very category-theoretic and very PL-theoretic: comprehension categories are categorical models of dependent types, while CCTT also incorporates type morphisms/coercive subtyping. citeturn935448search0

   **Prerequisites:** dependent type theory, fibrations/comprehension categories.  
   **Scale:** good thesis-style theorem.

5. **Higher container model is 2-coherent.**  
   Chen states:
   \[
   \boxed{
   \text{The Altenkirch–Kaposi higher container model is a 2-coherent wild CwF.}
   }
   \]
   More concretely, you have to construct the required triangle/pentagon coherences, type coherences and coherences for context extension. citeturn392898search1

   **Prerequisites:** categories with families, dependent types, higher categorical coherence.  
   **Caveat:** the 2025 paper says forthcoming work was expected on this one, so I would contact/check with the authors before choosing it as a serious project. I did not find a later primary-source proof in my search.

6. **Soundness/model-existence conjecture for univalent reference types.**  
   Sterling, Gratzer and Birkedal's Conjecture 4.1 asks for a nontrivial model of guarded HoTT in guarded cubical assemblies containing a particular small, set-reflective guarded Martin-Löf subuniverse:
   \[
   \boxed{\text{such a model exists}.}
   \]
   Establishing it would substantiate their denotational semantics of higher-order mutable references, including equations expressing permutation of allocations and representation independence. citeturn903661search2

   **Prerequisites:** toposes, cubical/guarded type theory, denotational semantics.  
   **Scale:** serious PhD problem.

7. **Uniqueness of the untyped locally final higher-order coalgebra.**  
   A 2026 categorical framework constructs a locally final coalgebra used for an adequate semantics of untyped higher-order combinatory logic, but its general theorem does not establish uniqueness in the untyped case. The authors explicitly conjecture:
   \[
   \boxed{
   \text{the locally final coalgebra is unique up to isomorphism}.
   }
   \]
   citeturn935448search1

   **Prerequisites:** coalgebras, enriched/metric categorical fixed points, operational semantics.  
   **Why interesting:** this is a rather pure category-theoretic missing theorem sitting directly inside semantics of higher-order programs.

8. **Escardó's mixed probabilistic/nondeterministic semidecidability conjecture.**  
   Roughly, when computation has **both probability and nondeterminism**, the appropriate may/must probabilistic testing properties should remain semidecidable:
   \[
   \boxed{\text{may/must probabilistic testing is semidecidable}.}
   \]
   A 2025 result on mixed powerdomains proves a related adequacy/semidecidability result for probabilistic concurrency and explicitly identifies it with progress toward Escardó's conjecture. citeturn882915search1turn935448academia5

   **Prerequisites:** domain theory, powerdomains, probability, computability.  
   **Scale:** difficult and established enough to have some historical depth.

9. **Cubical conservativity / Morita-equivalence conjecture.**  
   Kraus states it explicitly as Conjecture 6.1 in July 2026:
   \[
   \boxed{
   \text{internal theorems provable in cubical type theory are provable in book HoTT}.
   }
   \]
   More structurally, the relevant cubical and traditional formulations of HoTT should be conservative/Morita-equivalent in the appropriate sense. citeturn882915search3

   This asks whether the computational machinery behind things such as Cubical Agda gives a better *implementation* of univalence without secretly giving additional ordinary mathematical theorems. The 2026 paper proves partial machinery and proposes a route toward the conjecture. citeturn882915search2

   **Prerequisites:** serious HoTT, model/category theory, cubical type theory.  
   **Scale:** major open problem.

10. **The probabilistic powerdomain monad is commutative.**  
   The classic one:
   \[
   \boxed{
   V:\mathbf{DCPO}\to\mathbf{DCPO}
   \text{ is a commutative monad}.
   }
   \]
   This amounts to proving the Fubini equation
   \[
   \int_X\!\int_Y\chi_U(x,y)\,d\nu(y)d\xi(x)
   =
   \int_Y\!\int_X\chi_U(x,y)\,d\xi(x)d\nu(y)
   \]
   for arbitrary dcpos \(X,Y\), Scott-open \(U\subseteq X\times Y\), and continuous valuations \(\xi,\nu\). A 2026 paper still describes this as open since the probabilistic powerdomain's discovery. citeturn658257search0 Earlier categorical work likewise records that commutativity on all of `DCPO` has been open since 1989. citeturn658257search1

   **Prerequisites:** domain theory at research level, categorical monads, measure/valuation theory.  
   **Scale:** potentially brutal. The statement is much easier to understand than to attack.

### The three I would investigate first

If your goal is **“I want an open conjecture where I could potentially make actual progress rather than spend five years learning enough to understand the question,”** I'd start with **#1, #2, or #3**.

In particular, **#1 is unusually appealing**. It is literally a one-line 2026 conjecture, the author says a counterexample may exist, and the surrounding mathematics already has Cubical Agda formalization. citeturn903661search0 That means you could attack it experimentally: formalize candidate classes of types, prove the equivalence for progressively larger subclasses, and search for where one direction breaks.

If you tell me roughly how much **category theory / type theory / Lean-Agda / PL semantics** you already know, I can narrow this to **2–3 conjectures you could realistically start working toward and give you the prerequisite path plus the first lemmas that seem attackable**.


---

> Tackle #1. Output your PhD thesis as markdown and pdf

<details><summary>💭 Thinking</summary>

**Scoping the thesis**

I’m identifying item #1 as the synthetic predomain orthogonality conjecture and will first verify its source, definitions, and status. I’ll then build a rigorous Markdown thesis, clearly separating established results, reductions, and any unresolved claims.

**Scoped the thesis**

</details>

```unknown
bash -lc cat /home/oai/skills/pdfs/SKILL.md
```

I’ll reconstruct the exact conjecture from the primary source, pursue proofs and counterexamples, isolate assumptions and restricted results, then deliver a cited thesis in Markdown and PDF.

<details><summary>💭 Thinking</summary>

**Read PDF creation and conversion guidelines**

</details>

```json
{"search_query":[{"q":"site:arxiv.org 2607.17292 synthetic domain theory Conjecture 6.20 predomain orthogonality Lambda omega bar omega"},{"q":"2607.17292 GitHub Cubical Agda synthetic domain theory Xue"},{"q":"\"Conjecture 6.20\" \"synthetic predomain\""},{"q":"\"Lambda_omega\" \"bar omega\" synthetic domain theory"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 14 websites**

</details>

```unknown
bash -lc python - <<'PY'
import requests
urls=['https://zenodo.org/api/records/21442391','https://zenodo.org/records/21442391']
for u in urls:
    try:
        r=requests.get(u,timeout=30)
        print(u, r.status_code, r.url, r.headers.get('content-type'), len(r.content))
        print(r.text[:500])
    except Exception as e:
        print('ERR',u,e)
PY
```

<details><summary>💭 Thinking</summary>

**Tested Zenodo DOI access**

</details>


---

> Be honest about being able to solve it / not being able to / where you get stuck (if any) and where to look for more

<details><summary>💭 Thinking</summary>

The user wants the response to be candid about whether the selected open problem can be solved, clearly identify any points where the work gets stuck, and suggest references or directions for further research.

</details>

```json
{"open":[{"ref_id":"https://zenodo.org/doi/10.5281/zenodo.21442391"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searching the web**

</details>

```json
{"search_query":[{"q":"site:arxiv.org 2607.17292 synthetic domain theory Conjecture 6.20 predomain orthogonality"},{"q":"2607.17292 GitHub Cubical Agda Xue synthetic domain theory"},{"q":"\"Conjecture 6.20\" \"synthetic predomain\""},{"q":"\"Lambda_omega\" \"bar omega\" synthetic predomain"}],"response_length":"long"}
```

I’ll clearly distinguish proved, conditional, failed, and unresolved work, ending with the exact sticking points, relevant sources/formalization locations, and a concrete path forward.

<details><summary>💭 Thinking</summary>

**Searched 6 websites**

**Analyzing the conjecture**

I’m testing whether orthogonality to one composite inclusion can genuinely force all predomain axioms. My working concern is that right orthogonality to a single map may be too weak unless the other generators lie in its saturation.

**Analyzed the conjecture**

**Testing simple counterexamples**

I’m checking degenerate and discrete types first. Some satisfy the predomain conditions vacuously, so they don’t refute the conjecture; a meaningful counterexample likely requires analyzing the interval and completion structure more carefully.

**Tested simple counterexamples**

**Modeling ordered semantics**

I’m moving to ordered sets, where interval maps encode monotone paths. Finite simplex and spine inclusions may collapse to isomorphisms, while the infinite inclusion becomes ordinary chain completion, offering a cleaner test of the conjecture.

**Modeled ordered semantics**

</details>

```json
{"open":[{"ref_id":"turn382381search3","lineno":1000},{"ref_id":"turn382381search3","lineno":810},{"ref_id":"turn382381search3","lineno":180},{"ref_id":"turn382381search3","lineno":236},{"ref_id":"turn382381search3","lineno":638},{"ref_id":"turn382381search3","lineno":730}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

```json
{"search_query":[{"q":"https://zenodo.org/records/21442391"},{"q":"https://zenodo.org/api/records/21442391"}],"response_length":"short"}
```

<details><summary>💭 Thinking</summary>

**Searched 8 websites**

</details>

```unknown
bash -lc python - <<'PY'
import requests
u='https://zenodo.org/api/records/21442391'
r=requests.get(u,timeout=30)
print(r.status_code)
print(r.url)
print(r.text[:1000])
PY
```

<details><summary>💭 Thinking</summary>

**Tested Zenodo access and reviewed PDF instructions**

</details>

```json
{"search_query":[{"q":"\"right-orthogonal\" \"omega-spine\" synthetic domain"},{"q":"\"Λω\" \"synthetic predomain\""},{"q":"\"spine\" \"chain-complete\" synthetic domain theory"},{"q":"\"orthogonal to\" \"initial and final\" L-algebra domain"}],"response_length":"long"}
```

The source’s exact conjecture is one-way: orthogonality implies synthetic predomain; Segal and chain completeness look attainable, while Rezk completeness and thinness remain the bottlenecks.

<details><summary>💭 Thinking</summary>

**Searched 22 websites**

**Searched GitHub for Synthetic Domain Theory repositories**

</details>

```json
{"search_query":[{"q":"Runze Xue GitHub Agda synthetic domain theory"},{"q":"\"Omega.PhoaΛω\" Agda"},{"q":"\"Lattice.PhoaΛ\" Agda"},{"q":"\"zenodo.21442391\""}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 3 websites**

</details>

```unknown
bash -lc python - <<'PY'
import requests
url='https://zenodo.org/api/records/21442391'
r=requests.get(url,timeout=30)
print(r.status_code)
print(r.text[:1000])
PY
```

<details><summary>💭 Thinking</summary>

**Tested Zenodo API internet access**

</details>

```json
{"open":[{"ref_id":"turn269080academia13"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

```json
{"open":[{"ref_id":"https://arxiv.org/e-print/2607.17292"}],"response_length":"short"}
```

<details><summary>💭 Thinking</summary>

**Searching the web**

</details>

```json
{"open":[{"ref_id":"https://export.arxiv.org/e-print/2607.17292"}],"response_length":"short"}
```

<details><summary>💭 Thinking</summary>

**Searching the web**

</details>

```unknown
bash -lc cat /home/oai/skills/pdfs/SKILL.md
```

<details><summary>💭 Thinking</summary>

**Reviewed PDF guidelines and inspected paper definitions, theorems, proofs, and finite spines excerpt**

</details>

```json
{"search_query":[{"q":"Reus Streicher synthetic domain theory orthogonality complete objects predomains PDF"},{"q":"van Oosten Simpson axioms counterexamples synthetic domain theory complete objects orthogonality"},{"q":"\"well-complete\" objects synthetic domain theory orthogonal omega bar omega"},{"q":"\"L-complete\" synthetic domain theory orthogonality"}],"response_length":"long"}
```

A possible counterexample emerges for higher untruncated types in simplicial spaces; I’m checking whether the formal statement restricts \(A\) to sets, which could exclude it.

<details><summary>💭 Thinking</summary>

**Searched 10 websites**

</details>

```unknown
bash -lc pdftotext -layout /mnt/data/domains_classifying_topoi.pdf /mnt/data/domains_classifying_topoi.txt && grep -n "Theorem 9.13\|synthetic poset\|spatial.*algebra\|sequential colimit\|choice" /mnt/data/domains_classifying_topoi.txt | head -80
```

<details><summary>💭 Thinking</summary>

**Extracted theorem references and inspected spatial definitions**

</details>

```json
{"search_query":[{"q":"Pugh Sterling When is the partial map classifier a Sierpinski cone arXiv 2025"},{"q":"Riehl Shulman A type theory for synthetic infinity categories arXiv"},{"q":"Cubical Agda univalence higher inductive types paper 2019"},{"q":"Reus Streicher General synthetic domain theory logical approach PDF"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 12 websites**

**Developing the thesis**

I’m organizing the manuscript around Xue’s conjecture, separating proven implications from the unresolved converse. I’ll present the strongest defensible results, identify the Rezk and thinness gap, and provide both Markdown and PDF deliverables.

</details>

```unknown
bash -lc ls -lh /mnt/data | sed -n '1,120p'; echo '---'; command -v pandoc || true; command -v xelatex || true; command -v lualatex || true; command -v pdflatex || true; python -V
```

<details><summary>💭 Thinking</summary>

**Reviewed local PDFs, theorem sources, definitions, and OCR shape notation**

</details>

```json
{"search_query":[{"q":"\"Conjecture 6.20\" \"synthetic predomain\""},{"q":"\"Λω\" \"synthetic predomain\" Xue"},{"q":"\"Topology in Synthetic Domain Theory\" code Agda GitHub"},{"q":"arXiv 2607.17292 citations"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 16 websites**

</details>

```unknown
bash -lc python - <<'PY'
import requests
u='https://doi.org/10.5281/zenodo.21442391'
r=requests.get(u,allow_redirects=True,timeout=30)
print(r.status_code,r.url,len(r.content),r.headers.get('content-type'))
print(r.text[:500])
PY
```

<details><summary>💭 Thinking</summary>

**Tested DOI container download**

</details>

```json
{"search_query":[{"q":"site:github.com Runze Xue synthetic domain theory Agda LambdaOmega"},{"q":"site:github.com \"Omega.PhoaΛω\""},{"q":"site:github.com \"Topology in Synthetic Domain Theory\" Agda"},{"q":"site:github.com \"PhoaΛω\""}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 2 websites**

</details>

```unknown
bash -lc grep -n -i -E "synthetic poset|replete|spatial|parallel|separated|complete object|orthogonal" /mnt/data/domains_classifying_topoi.txt | sed -n '1,260p'
```

<details><summary>💭 Thinking</summary>

**Investigated synthetic posets and created a Libertinus mathematical thesis manuscript**

</details>

```unknown
bash -lc cat > /mnt/data/infinite_spine_thesis.md <<'EOF'
---
title: "Orthogonality, Infinite Spines, and Synthetic Predomains"
subtitle: "A Partial Resolution and Exact Reduction of Xue's Conjecture 6.20"
author: "Research manuscript prepared by GPT-5.6 Pro (OpenAI)"
date: "9 August 2026"
documentclass: book
classoption:
  - 11pt
  - oneside
papersize: letter
geometry:
  - inner=1.15in
  - outer=1.05in
  - top=1.05in
  - bottom=1.05in
mainfont: "Libertinus Serif"
sansfont: "Libertinus Sans"
monofont: "DejaVu Sans Mono"
mathfont: "Libertinus Math"
toc: true
toc-depth: 3
numbersections: true
secnumdepth: 3
colorlinks: true
linkcolor: ThesisNavy
urlcolor: ThesisNavy
header-includes:
  - \input{/mnt/data/infinite_spine_thesis/header.tex}
---

\frontmatter

# Status, scope, and integrity statement {-}

\statusbox{\textbf{Research status.} This is a thesis-style research manuscript, not a degree submission, not a peer-reviewed paper, and not a machine-checked formalization. It does \emph{not} claim a complete proof of Xue's Conjecture 6.20. It gives paper-level proofs of substantial consequences of the conjecture's hypothesis, reduces the unresolved part to one precise orthogonality question, proves several conditional versions, and records failed approaches and a concrete formalization programme. All claims labelled ``proved in this manuscript'' remain subject to expert review and mechanization.}

The problem addressed here was proposed by Runze Xue in *Topology in Synthetic Domain Theory and its Formalisation in Agda* (2026). In Xue's notation, the conjecture says that a type right-orthogonal to the inclusion of the infinite spine into the final lifting coalgebra is a synthetic predomain. The source itself cautions that the conjecture may be false and expects, more conservatively, that the hypothesis should at least imply Segal completeness and chain completeness.

This manuscript takes that caution literally. Its conclusions are divided into four levels.

| Level | Meaning in this manuscript |
|---|---|
| **Established source result** | A theorem or definition explicitly present in the cited literature. |
| **Paper-level deduction** | A proof supplied here from stated assumptions; not peer reviewed or machine checked. |
| **Conditional theorem** | A proof whose additional hypothesis is made explicit. |
| **Open or failed** | No valid proof or counterexample was obtained. |

The main honesty constraint is therefore simple: the unrestricted conjecture remains unresolved here. The exact point of failure is identified in Chapters 9--12.

# Abstract {-}

Let

\[
  j : \Lambda_\omega \longrightarrow \Delta^\infty \simeq \overline\omega
\]

be the canonical inclusion of the infinite directed spine into the infinite simplex/final lifting coalgebra in the synthetic-domain-theoretic setting developed by Xue. Conjecture 6.20 asserts that every type \(A\) for which precomposition

\[
  j^* : A^{\Delta^\infty} \longrightarrow A^{\Lambda_\omega}
\]

is an equivalence is a synthetic predomain: Segal complete, Rezk complete, \(\mathbb I\)-separated, and \(\omega\)-chain complete.

This manuscript proves the following at paper level, under explicit assumptions about the canonical finite-spine colimit presentations and their coherence.

First, every finite spine inclusion

\[
  j_n : \Lambda_n \hookrightarrow \Delta^n
\]

is a retract of \(j\) in the arrow category. Hence \(j\)-locality implies locality for every finite spine, and in particular Segal completeness.

Second, writing

\[
  \Lambda_\omega \xrightarrow{k} \Delta^\omega
  \xrightarrow{c} \Delta^\infty,
  \qquad j=c\circ k,
\]

mapping out of the sequential colimit presentations shows that \(j\)-locality implies \(k\)-locality. Two-out-of-three then implies \(c\)-locality, which is precisely \(\omega\)-chain completeness. More strongly,

\[
  A\perp j
  \quad\Longleftrightarrow\quad
  \bigl(A\perp c\bigr)
  \ \text{and}\ 
  \bigl(\forall n,\ A\perp j_n\bigr).
\]

Thus the infinite-spine condition is exactly the conjunction of finite categorical composition and chain convergence; it is not merely suggestive of those properties.

Third, assuming \(\mathbb I\)-separation, a cofinal even/odd subsequence argument turns chain convergence into antisymmetry. In Xue's h-set setting this supplies the Rezk component for the resulting thin Segal type. Consequently, the full conjecture reduces to one question:

\[
  \boxed{
  A\perp j \ \Longrightarrow\
  A\perp (\mathbb I_{\parallel}\to\mathbb I)
  }
\]

or, equivalently, whether the walking-parallel-pair comparison is a \(j\)-local equivalence.

Fourth, a conditional full theorem is obtained. If the evaluation map

\[
  \eta_A:A\longrightarrow \mathbb I^{\mathbb I^A},
  \qquad
  \eta_A(a)(\varphi)=\varphi(a),
\]

is an embedding---that is, open observations separate points---then \(A\) embeds in an observational algebra, hence is \(\mathbb I\)-separated. Combined with the preceding results, every observationally separated \(j\)-local type is a synthetic predomain.

No proof is found that arbitrary \(j\)-local types are observationally separated, and no valid counterexample is constructed. The most direct counterexample candidate is the \(j\)-local reflection of the walking parallel pair. The manuscript ends with a formalization blueprint for Cubical Agda or Rzk and a model-theoretic search programme in classifying topoi and realizability models.

# Contributions at a glance {-}

\resultbox{\textbf{Headline result.} Subject to the shape and colimit assumptions stated in Chapter 4, the hypothesis of Xue's Conjecture 6.20 already implies all finite Segal conditions and \(\omega\)-chain completeness. After a cofinality argument, the only genuinely unresolved property is \(\mathbb I\)-separation.}

| Question | Status reached here |
|---|---|
| Does \(A\perp j\) imply Segal completeness? | **Yes**, paper-level proof by arrow retracts. |
| Does \(A\perp j\) imply all finite spine conditions? | **Yes**, same proof. |
| Does \(A\perp j\) imply chain completeness? | **Yes**, paper-level proof by colimits and two-out-of-three. |
| Is \(j\)-locality equivalent to finite-spine locality plus chain completeness? | **Yes**, under the stated shape identifications. |
| Does \(A\perp j\) imply Rezk completeness? | **Yes after \(\mathbb I\)-separation**; not independently proved. |
| Does \(A\perp j\) imply \(\mathbb I\)-separation? | **Open here.** This is the exact remaining core. |
| Is the full conjecture proved? | **No.** |
| Is the conjecture disproved? | **No.** No validated countermodel was found. |
| Is the argument formalized? | **No.** Agda/Rzk pseudocode and proof obligations are supplied. |

# Acknowledgements and provenance {-}

The conjecture, definitions of the directed shapes, and the associated Cubical Agda development are due to Runze Xue. The broader orthogonality/repleteness viewpoint comes from synthetic domain theory, particularly work of Reus and Streicher, van Oosten and Simpson, and Sterling and Ye. The synthetic-category-theoretic reading of Segal and Rezk conditions follows Riehl--Shulman and related work. Any new argument in this manuscript should be read as a proposed proof for checking, not as an established result attributable to those authors.

\mainmatter

# Introduction

## The conjecture in one diagram

The relevant map factors through the initial lifting algebra:

\[
\begin{tikzcd}[column sep=large]
\Lambda_\omega \arrow[r,"k",hook]
  & \Delta^\omega \simeq \omega
    \arrow[r,"c",hook]
  & \Delta^\infty \simeq \overline\omega .
\end{tikzcd}
\]

The first map freely supplies all finite composites to an infinite string of composable directed edges. The second adjoins the limit point of an \(\omega\)-chain. Their composite is

\[
  j=c\circ k:\Lambda_\omega\hookrightarrow\Delta^\infty.
\]

For any type \(A\), precomposition produces

\[
  j^*:A^{\Delta^\infty}\longrightarrow A^{\Lambda_\omega}.
\]

The statement \(A\perp j\) means that every infinite spine-shaped diagram in \(A\) has a unique extension across the infinite simplex. Informally, one extension must perform two jobs simultaneously:

1. fill all finite higher simplices, thereby composing paths coherently; and
2. assign a limit to the underlying countable chain.

Xue's conjecture asks whether those jobs force not only composition and limits but also univalence/Rezk completeness and proof-irrelevance of parallel directed paths.

The first two implications are plausible because they are visibly encoded by the factorization. The last two are structurally different. They are quotient-like or separation conditions: they demand that certain distinctions disappear. The main result of this manuscript makes that distinction exact.

## Why the question matters for programming languages

Synthetic domain theory reorganizes classical domain theory so that continuity is built into the ambient logic. Instead of selecting continuous functions from all set-theoretic functions, one works in a universe where every definable map between suitable objects is already continuous. This is useful for denotational semantics because recursion, approximation, partiality, and fixed points can then be handled internally.

The interval or dominance \(\mathbb I\) plays several roles at once. Its points act like semidecidable truth values or opens; maps \(A\to\mathbb I\) act like observations on programs; and maps \(\mathbb I\to A\) generate the intrinsic information order. If a compact orthogonality condition such as \(A\perp j\) characterized predomains, it would give a single reusable interface for semantic domains:

\[
  \text{coherent composition}
  +\text{countable approximation}
  +\text{extensional order}.
\]

For formalized semantics this matters operationally. A single locality structure is easier to transport through dependent products, function spaces, and model constructions than a collection of separately managed laws. It could also make the boundary between categorical semantics and executable type theory more uniform.

The risk is equally important. If the locality condition only constructs an \(\omega\)-complete synthetic category and does not force thinness, then calling every local object a predomain would silently erase proof-relevant computational structure. Nondeterministic choices, witnesses, traces, or multiple refinement proofs could survive as parallel directed paths. Determining whether that can happen is therefore not terminological; it determines what semantic information the proposed axiom forgets.

## The result in conceptual form

Let \(\Local(f)\) denote the class of types right-orthogonal to a map \(f\). Under the canonical colimit identifications, this manuscript proves

\[
  \Local(j)
  =
  \Local(c)\cap\bigcap_{n\ge 0}\Local(j_n).
\]

The right side says exactly:

- every finite composable string has a unique coherent simplex filler; and
- every \(\omega\)-chain has a unique continuous limit extension.

Hence \(j\)-locality is a strong notion of complete Segal object. What is not present in this formula is any explicit generator that identifies parallel arrows. The walking-parallel-pair map

\[
  \rho:\mathbb I_{\parallel}\longrightarrow\mathbb I
\]

is therefore the decisive comparison. The conjecture is equivalent, after the other deductions, to the assertion that every \(j\)-local object is \(\rho\)-local. In localization language:

\[
  \rho\text{ is a }j\text{-local equivalence}.
\]

This reformulation provides both a proof strategy and a disproof strategy. A proof should derive \(\rho\)-locality from \(j\)-locality, perhaps through observational duality or a model-independent density theorem. A disproof should find a \(j\)-local object with two distinct parallel paths, or equivalently show that the \(j\)-local reflection of \(\rho\) is not invertible.

## Claims deliberately not made

This manuscript does not claim that the shape maps and colimit comparison maps have been checked against the exact names and definitional equalities in Xue's Cubical Agda repository. The associated code record is cited by Xue, but it was not available for inspection in the present environment. The proofs are therefore formulated at the invariant categorical/type-theoretic level.

It also does not infer openness merely from a failed proof. In particular, the inability to prove \(\mathbb I\)-separation is not evidence that the conjecture is false. Conversely, the absence of a counterexample is not evidence that it is true. The correct status is a reduction with conditional results.

## Organization

Chapters 2--4 reconstruct the ambient theory, shapes, and assumptions. Chapters 5--8 contain the main paper-level deductions. Chapter 9 reduces the full conjecture to \(\mathbb I\)-separation. Chapter 10 proves the observationally separated case. Chapters 11--13 document failed approaches, model tests, and counterexample searches. Chapters 14--15 give formalization plans and a research roadmap. Appendices contain expanded proofs, shape formulas, and pseudocode.

# Background: synthetic domains as local objects

## Orthogonality

Let \(f:X\to Y\) be a map in a cartesian closed type-theoretic universe. A type \(A\) is **right-orthogonal** or **local** with respect to \(f\) when precomposition is an equivalence:

\[
  f^*:A^Y\xrightarrow{\simeq}A^X,
  \qquad
  f^*(g)=g\circ f.
\]

We write \(A\perp f\), or occasionally \(f\perp A\), depending on convention. This is the special case of map orthogonality in which the right-hand map is \(A\to 1\). Internally, it says that every map \(X\to A\) extends uniquely across \(f\).

Three elementary closure principles drive most of the manuscript.

\begin{lemma}[Closure under equivalence]
If \(A\simeq B\) and \(A\perp f\), then \(B\perp f\).
\end{lemma}

\begin{lemma}[Closure under products]
If \(A_i\perp f\) for every \(i:I\), then \(\prod_{i:I}A_i\perp f\). In particular, if \(A\perp f\), then every power \(A^Z\perp f\).
\end{lemma}

\begin{proof}
Precomposition into a dependent product is computed pointwise:
\[
  \left(\prod_i A_i\right)^Y
  \simeq
  \prod_i A_i^Y
  \xrightarrow{\prod_i f^*}
  \prod_i A_i^X
  \simeq
  \left(\prod_i A_i\right)^X.
\]
A product of equivalences is an equivalence.
\end{proof}

\begin{lemma}[Arrow-retract closure]
If \(f\) is a retract of \(g\) in the arrow category and \(A\perp g\), then \(A\perp f\).
\end{lemma}

\begin{proof}
Contravariant exponentiation sends an arrow retract to a retract of restriction maps. A retract of an equivalence is an equivalence.
\end{proof}

The last lemma will turn the single infinite map \(j\) into every finite spine map \(j_n\).

## Directed paths

Fix a directed interval \(\mathbb I\) with endpoints \(0,1:\mathbb I\). For points \(x,y:A\), the directed path type is

\[
  \operatorname{hom}_A(x,y)
  :=
  \{p:\mathbb I\to A\mid p(0)=x,\ p(1)=y\}.
\]

Constant maps supply identities. Every function \(A\to B\) acts functorially on directed paths by postcomposition. The resulting relation is therefore reflexive and preserved by all definable maps.

The ambient equality type and the directed path type are distinct. Xue works, for simplicity, in an h-set fragment, so ordinary identity types are propositions. Directed hom-types need not be propositions; two different functions \(\mathbb I\to A\) can have the same endpoints. This distinction is exactly why \(\mathbb I\)-separation is a nontrivial axiom.

## Segal, Rezk, separated, and chain-complete types

Let \(\Lambda_2\hookrightarrow\Delta^2\) be the two-edge spine inclusion. A type \(A\) is **Segal** when

\[
  A^{\Delta^2}\xrightarrow{\simeq}A^{\Lambda_2}.
\]

Thus two composable paths have a unique triangular filler, whose diagonal supplies their composite. Higher finite spine conditions similarly encode coherent composites of longer strings. In the ordinary Segal argument, the binary condition generates the higher ones.

Let \(\mathbb E\) be the walking isomorphism shape. A Segal type is **Rezk complete** when it is right-orthogonal to \(\mathbb E\to 1\). This identifies categorical isomorphism with equality of objects in the directed type.

Let \(\mathbb I_{\parallel}\) be the pushout of two copies of \(\mathbb I\) along their endpoints. A map \(\mathbb I_{\parallel}\to A\) is a pair of parallel directed paths. The codiagonal

\[
  \rho:\mathbb I_{\parallel}\longrightarrow\mathbb I
\]

identifies the two copies. A type is **\(\mathbb I\)-separated** when \(A\perp\rho\). Equivalently, the endpoint map

\[
  A^{\mathbb I}\longrightarrow A\times A
\]

is an embedding. In the h-set setting, each directed hom-type is then a proposition.

A Segal, Rezk-complete, \(\mathbb I\)-separated type is a **synthetic poset**. Finally, let

\[
  c:\omega\simeq\Delta^\omega
  \hookrightarrow
  \overline\omega\simeq\Delta^\infty
\]

be the initial-to-final lifting (co)algebra inclusion. A type is **chain complete** when it is right-orthogonal to \(c\). A chain-complete synthetic poset is a **synthetic predomain**.

In symbols,

\[
\Predom(A)
:=
\Seg(A)\wedge\Rezk(A)\wedge\Sep(A)\wedge\CC(A).
\]

## Observational algebras and repleteness

For any type \(X\), its observational algebra is

\[
  \mathcal O(X):=\mathbb I^X.
\]

The product closure of right orthogonality implies that every locality property of \(\mathbb I\) is inherited by every observational algebra. This is the elementary source of many well-behaved semantic domains.

A type is **replete** when it is local with respect to every map with respect to which \(\mathbb I\) is local. Replete objects therefore lie in the smallest exponential ideal/localization class generated by \(\mathbb I\). Sterling and Ye show that spectra and spatial \(\mathbb I\)-algebras are replete in their classifying-topos framework, and consequently inherit the synthetic-poset conditions satisfied by \(\mathbb I\).

The conjecture studied here is stronger in a different direction. It asks whether locality with respect to one particular countable map \(j\) already implies enough repleteness to force all predomain conditions. The source itself warns that this may fail outside observational algebras.

# Directed simplices and spines

## Finite simplices

For \(n\ge 0\), write

\[
  \Delta^n
  =
  \{(i_1,\ldots,i_n):\mathbb I^n
    \mid i_1\ge i_2\ge\cdots\ge i_n\}.
\]

Its vertices are

\[
  v_k=(\underbrace{1,\ldots,1}_{k},
       \underbrace{0,\ldots,0}_{n-k}),
  \qquad 0\le k\le n.
\]

The finite spine \(\Lambda_n\) is the colimit of \(n\) copies of \(\mathbb I\) glued end to end. It has the same vertices but only the adjacent edges

\[
  v_0\to v_1\to\cdots\to v_n.
\]

There is a canonical inclusion

\[
  j_n:\Lambda_n\hookrightarrow\Delta^n.
\]

A map \(\Lambda_n\to A\) is an \(n\)-tuple of composable directed paths. A map \(\Delta^n\to A\) contains those paths together with all composites and higher coherence data encoded by the simplex. Right-orthogonality to \(j_n\) says this coherent extension is unique.

## The initial infinite simplex

The face-padding maps

\[
  s_n:\Delta^n\longrightarrow\Delta^{n+1},
  \qquad
  s_n(i_1,\ldots,i_n)=(i_1,\ldots,i_n,0)
\]

form a sequential diagram. Its colimit is the finite-support infinite simplex

\[
  \Delta^\omega
  \simeq
  \colim_n\Delta^n.
\]

Concretely, it consists of descending sequences in \(\mathbb I\) that become \(0\) after finitely many coordinates. Xue identifies this object with the initial algebra \(\omega\) of the lifting endofunctor.

The finite spine inclusions are compatible with the padding maps. Their colimit is

\[
  k:\Lambda_\omega\longrightarrow\Delta^\omega.
\]

The domain \(\Lambda_\omega\) may be presented as a higher inductive type with vertices \(\operatorname{step}(n)\) and an interval edge from \(\operatorname{step}(n)\) to \(\operatorname{step}(n+1)\). Equivalently, it is the colimit of the finite spines:

\[
  \Lambda_\omega\simeq\colim_n\Lambda_n.
\]

## The final infinite simplex

The full infinite simplex is

\[
  \Delta^\infty
  =
  \{s:\mathbb N\to\mathbb I
    \mid s_n\ge s_{n+1}\}.
\]

It contains \(\Delta^\omega\) by zero padding but also the non-finite points, including the all-ones limit vertex

\[
  v_\infty=(1,1,1,\ldots).
\]

Xue identifies \(\Delta^\infty\) with the final lifting coalgebra \(\overline\omega\). The inclusion

\[
  c:\Delta^\omega\hookrightarrow\Delta^\infty
\]

is the chain-completeness comparison map.

The infinite spine includes by mapping its \(n\)-th vertex to

\[
  v_n=(1^n0^\infty)
\]

and its \(n\)-th edge to the adjacent edge \(v_n\to v_{n+1}\). This gives

\[
  j:\Lambda_\omega\hookrightarrow\Delta^\infty,
  \qquad j=c\circ k.
\]

## What maps from the shapes mean

The three mapping types have different semantic content:

\[
\begin{aligned}
  A^{\Lambda_\omega}
  &\simeq \{\text{infinite composable strings in }A\},\\
  A^{\Delta^\omega}
  &\simeq \{\text{such strings with all finite composites/coherences}\},\\
  A^{\Delta^\infty}
  &\simeq \{\text{coherent strings with a continuous limit point}\}.
\end{aligned}
\]

These descriptions are schematic rather than definitions, but they explain the factorization of restriction maps:

\[
  A^{\Delta^\infty}
  \xrightarrow{c^*}
  A^{\Delta^\omega}
  \xrightarrow{k^*}
  A^{\Lambda_\omega}.
\]

The conjectural leap is from this composition-and-limit structure to path proof-irrelevance.

EOF
wc -w /mnt/data/infinite_spine_thesis.md; wc -l /mnt/data/infinite_spine_thesis.md
```

<details><summary>💭 Thinking</summary>

**Drafted infinite spine thesis with assumptions, proofs, and decomposition analysis**

</details>

```unknown
bash -lc cat >> /mnt/data/infinite_spine_thesis.md <<'EOF'
# Observational separation gives a conditional full theorem

## The double-dual evaluation map

For any type \(A\), define its observational double dual

\[
  D(A):=\mathbb I^{\mathbb I^A}.
\]

There is a canonical evaluation map

\[
  \eta_A:A\longrightarrow D(A),
  \qquad
  \eta_A(a)(\varphi)=\varphi(a).
\]

Two points \(a,b:A\) have equal images precisely when every open observation gives the same result:

\[
  \eta_A(a)=\eta_A(b)
  \quad\Longleftrightarrow\quad
  \forall\varphi:A\to\mathbb I,\ \varphi(a)=\varphi(b).
\]

Call \(A\) **observationally separated** when \(\eta_A\) is an embedding. In an h-set universe this means that open observations jointly distinguish points.

Xue's concluding discussion asks whether applying the observation functor twice can provide a useful duality between ordinary types and observational algebras. The source also notes that naive fixed-point sobriety is too restrictive: even the simplices need not be fixed by double dualization. The present argument requires only that \(\eta_A\) be an embedding, not an equivalence.

## The double dual is a predomain

Assume the interval \(\mathbb I\) is a synthetic predomain, as established in Xue's setting under the transfinite Phoa/sobriomorphism hypotheses and in the classifying-topos setting under the relevant quasi-coherence axioms.

Since right orthogonality is closed under products, every power \(\mathbb I^X\) inherits every predomain locality of \(\mathbb I\). Hence

\[
  D(A)=\mathbb I^{\mathbb I^A}
\]

is a synthetic predomain.

\begin{proposition}[Observational double dual is a predomain]\label{prop:double-dual-predom}
If \(\mathbb I\) is a synthetic predomain, then \(D(A)\) is a synthetic predomain for every \(A\).
\end{proposition}

\begin{proof}
Each defining orthogonality condition is inherited by products. The power \(\mathbb I^{\mathbb I^A}\) is an internally indexed product of copies of \(\mathbb I\).
\end{proof}

## Separation inherited from an embedding

Right orthogonality is not generally inherited by arbitrary subobjects. The walking-parallel-pair condition is special enough that a direct argument works.

\begin{lemma}[Embedded subtypes of separated types]\label{lem:embed-sep}
Let \(m:A\to B\) be an embedding of h-set types. If \(B\) is \(\mathbb I\)-separated, then \(A\) is \(\mathbb I\)-separated.
\end{lemma}

\begin{proof}
Let \(p,q:\mathbb I\to A\) have the same endpoints. Then \(m\circ p\) and \(m\circ q\) are parallel paths in \(B\). Since \(B\) is separated,
\[
  m\circ p=m\circ q.
\]
Function extensionality gives \(m(p(i))=m(q(i))\) for every \(i:\mathbb I\). Because \(m\) is an embedding, \(p(i)=q(i)\) pointwise; function extensionality gives \(p=q\). Thus each endpoint fiber of \(A^{\mathbb I}\to A\times A\) is a proposition.
\end{proof}

No extension-in-the-subobject argument is needed: \(\rho\)-locality is exactly uniqueness of parallel paths, so pointwise reflection of equality suffices.

## Conditional resolution

\begin{theorem}[Observationally separated case]\label{thm:observational-case}
Assume the shape package and assume \(\mathbb I\) is a synthetic predomain. Let \(A\) be a type such that

1. \(A\perp j\); and
2. \(\eta_A:A\to\mathbb I^{\mathbb I^A}\) is an embedding.

Then \(A\) is a synthetic predomain.
\end{theorem}

\begin{proof}
By Proposition \ref{prop:double-dual-predom}, \(D(A)\) is a synthetic predomain and hence \(\mathbb I\)-separated. By Lemma \ref{lem:embed-sep}, the embedding \(\eta_A\) makes \(A\) \(\mathbb I\)-separated.

The \(j\)-locality of \(A\) gives Segal completeness by Corollary \ref{cor:segal} and chain completeness by Theorem \ref{thm:chain-complete}. Separation plus \(j\)-locality gives Rezk completeness by Corollary \ref{cor:sep-rezk}. Therefore \(A\) satisfies all four predomain conditions.
\end{proof}

\resultbox{\textbf{Conditional full result.} Xue's conjecture is valid for every \(j\)-local type whose points are separated by maps into the interval. This includes any case where the evaluation map into the observational double dual is known to be monic.}

## Relation to spatiality and repleteness

Sterling and Ye define spatial \(\mathbb I\)-algebras and sober spectra through an observation--spectrum adjunction. They prove that spectra and spatial algebras are replete, and that under their finite quasi-coherence assumptions these objects are synthetic posets. Under countable quasi-coherence they also obtain chain completeness of the interval and hence of replete objects.

For such objects, Theorem \ref{thm:observational-case} is not needed to establish predomain structure; repleteness already transfers every locality of \(\mathbb I\). Its significance is instead diagnostic. It shows exactly which part of spatial/replete reasoning repairs the unrestricted conjecture: observations separate enough structure to rule out parallel-path ambiguity.

The conditional theorem also applies in intermediate situations where full repleteness is unavailable. An embedding into a single observational algebra is much weaker than being local for every map seen as invertible by \(\mathbb I\).

## A stronger but easier corollary

\begin{corollary}[Embedding into any synthetic poset]\label{cor:embed-poset}
Let \(A\perp j\). If there is an embedding \(m:A\to P\) into a synthetic poset \(P\), then \(A\) is a synthetic predomain.
\end{corollary}

\begin{proof}
Lemma \ref{lem:embed-sep} makes \(A\) separated. Apply Theorem \ref{thm:reduction} and the already proved Segal/chain-complete consequences.
\end{proof}

This form may be easier to use in semantics: one can embed denotations into a function space or logical-relation object known to be a synthetic poset.

## The missing observational theorem

The unrestricted conjecture would follow immediately from

\[
  A\perp j
  \quad\Longrightarrow\quad
  \eta_A\text{ is an embedding}.
\]

Call this the **observational separation principle for local types**. It is a clean intermediate conjecture, but it is not proved here.

The principle is stronger than the reduced target in one sense and more structured in another. It implies \(\mathbb I\)-separation by embedding into \(D(A)\), but \(\mathbb I\)-separation alone need not make all points observationally distinguishable. Its advantage is that it connects directly to the duality programme proposed by Xue and to spatiality/repleteness in classifying topoi.

A proof would likely need one of the following:

- a density theorem saying that the infinite spine detects distinct points of a local type through interval-valued maps;
- a Stone-style representation theorem for \(j\)-local objects;
- a construction of enough open observations from the local extension operator;
- a model-specific theorem that all \(j\)-local objects in the relevant universe are spatial or replete.

None of these is currently available in the generality required.

# Where the proof stops

## The exact unsolved lifting problem

Take a pair of parallel paths

\[
  p,q:x\rightsquigarrow y
\]

in a \(j\)-local type \(A\). To prove separation one must show \(p=q\). The \(j\)-locality hypothesis only provides unique extension for maps

\[
  \Lambda_\omega\to A.
\]

A single infinite linear chain can compose arrows and take a limit, but the data \(p,q\) are not composable with one another: both start at \(x\) and end at \(y\). Without a return path \(y\to x\), they cannot be alternated along a spine. This elementary typing obstruction is the practical reason the successful cofinal argument needs separation before it can prove antisymmetry.

The reduced problem can be written as the lifting statement

\[
\begin{tikzcd}[column sep=large,row sep=large]
\mathbb I_{\parallel} \arrow[r,"(p,q)"] \arrow[d,"\rho"']
  & A\\
\mathbb I \arrow[ur,dashed,"p=q"'] &
\end{tikzcd}
\]

for every \(j\)-local \(A\). There is no direct map of this square into the defining \(j\)-lifting square known here.

## Why constant chains do not solve it

A tempting argument is to take the constant finite chain at \(x\) and construct two extensions to \(\Delta^\infty\) whose limit transition is \(p\) or \(q\). Uniqueness would then identify them.

This construction requires a map

\[
  \ell:\Delta^\infty\to\mathbb I
\]

that is \(0\) on every finite vertex \(v_n\) but \(1\) at \(v_\infty\). Then \(p\circ\ell\) and \(q\circ\ell\) would be the desired extensions. But \(\ell\) is a discontinuous ``jump at infinity.'' Chain completeness of \(\mathbb I\) is precisely the assertion that a map out of \(\Delta^\omega\) has only its continuous extension; the constant-zero chain must extend constantly. Therefore the needed \(\ell\) is unavailable in the intended models.

The failure is instructive. The most direct uniqueness proof for parallel paths would rely on a noncontinuous test that synthetic domain theory is designed to exclude.

## Why a finite retract is unavailable

For finite spine inclusions, clamping and truncation produced an arrow retract. An analogous retraction would require maps

\[
  \mathbb I_{\parallel}\rightleftarrows\Lambda_\omega,
  \qquad
  \mathbb I\rightleftarrows\Delta^\infty
\]

that preserve the two parallel branches through the inclusion. A linear spine has no place to store two noncomposable edges with the same endpoints. Any map into the spine must either identify the branches or place them at different positions, which changes their endpoints. The arrow-retract method therefore cannot transfer locality to \(\rho\) in the same elementary way.

This is not a proof that no more elaborate arrow retract exists in the ambient homotopy theory. It is a proof that the straightforward vertex-and-edge construction used for \(j_n\) cannot work.

## Why a codiagonal construction stalls

Another standard localization technique is to obtain a quotient map as the codiagonal of a pushout of a generating cofibration. Doubling a simplex along its spine creates two top-dimensional fillers sharing the same boundary. One might hope to retract the resulting codiagonal onto \(\rho\).

At dimension two, however, the two candidate triangle retractions must agree on the shared spine. To send their diagonals to distinct parallel copies of \(\mathbb I\), they would need incompatible behavior on that common boundary. No coherent retraction was found. Higher dimensions reproduce the same mismatch: the generator controls alternative *fillers* for one composable boundary, while \(\rho\) controls alternative *one-dimensional arrows* with common endpoints.

This failed construction should be formalized before being treated as definitive. A sophisticated anodyne or join construction could circumvent the naive retraction.

## Why higher groupoids are not immediate counterexamples

A nontrivial groupoid would be an obvious object with Segal composition and nontrivial isomorphisms. But Xue explicitly restricts to h-set types for simplicity. Ordinary equality therefore has no higher loops, and a proposed counterexample must use multiple directed maps \(\mathbb I\to A\), not homotopical identity paths of \(A\).

Moreover, \(j\)-locality includes chain continuity, which fails in the ordinary simplicial nerve model with the naive infinite ordinal: a constant chain can jump to a new object at the limit. Thus the nerve of an arbitrary category cannot be imported as a counterexample without first verifying all SDT interval and continuity axioms.

## What would count as a complete solution

A complete positive solution must provide a valid derivation of \(\rho\)-locality for arbitrary \(j\)-local types, with all universe and shape assumptions stated and preferably formalized.

A complete negative solution must provide:

1. a model of the relevant ambient axioms, including the interval principles used by Xue;
2. a type \(A\) in that model with \(A\perp j\); and
3. two distinct parallel directed paths in \(A\), or another explicit failure of predomain structure.

An object that is merely Segal and chain-complete in an unrelated category is not enough. The ambient model is part of the claim.

# Failed proof attempts in detail

## Attempt 1: derive both factors from the composite directly

**Idea.** Since \(j=c\circ k\), try to use two-out-of-three to infer both \(k\)- and \(c\)-locality from \(j\)-locality.

**Failure.** Two-out-of-three requires one factor in addition to the composite. A composite equivalence does not make either factor an equivalence in general.

**Repair.** The finite-arrow-retract theorem proves each finite component of \(k\) local; the colimit theorem then proves \(k\)-locality. Only after that does two-out-of-three give \(c\)-locality. This repaired attempt becomes Chapters 5--7.

## Attempt 2: use a jump at infinity

**Idea.** Encode a parallel path as an alternative limit extension of a constant chain.

**Failure.** It requires a discontinuous characteristic map that distinguishes the limit point from all finite approximants. Such a map contradicts chain completeness of the interval.

**Lesson.** Limit uniqueness cannot identify arbitrary finite-dimensional path data unless that data can be approximated continuously along the chain.

## Attempt 3: alternate the parallel paths

**Idea.** Put \(p,q,p,q,\ldots\) on successive edges and compare even and odd cofinal subsequences.

**Failure.** Parallel paths \(p,q:x\to y\) are not composable. The target of \(p\) is not the source of \(q\).

**Repair in a special case.** If a return path \(r:y\to x\) is available and separation identifies composites appropriately, alternating paths prove antisymmetry. This becomes Theorem \ref{thm:cofinal-antisym}. It does not prove separation itself.

## Attempt 4: prove Rezk before separation

**Idea.** Apply the alternating-chain argument to an isomorphism \(p:x\to y\), \(q:y\to x\), where composites are identities by definition.

**Partial success.** Even and odd cofinal subsequences force equality of the endpoint objects, provided the shape calculations are accepted.

**Failure.** Full Rezk completeness also rules out nontrivial automorphism data over an equality. Without thin hom-types, endpoint equality alone does not identify the isomorphism with the identity. The argument therefore proves only a skeletal/antisymmetry component, not the complete Rezk lifting property.

**Repair.** Once \(\mathbb I\)-separation is assumed, automorphism ambiguity disappears and the argument proves Rezk completeness.

## Attempt 5: inherit all locality through a subobject

**Idea.** Embed \(A\) into \(D(A)\), a predomain, and claim every predomain property is inherited by subobjects.

**Failure.** Right lifting properties are generally not inherited by subobjects because fillers constructed in the ambient object may leave the subobject.

**Repair.** Use only the special fact that \(\mathbb I\)-separation is uniqueness of parallel paths. An embedding reflects pointwise equality, so this one property is inherited. Segal and chain completeness come independently from \(j\)-locality. Rezk follows from separation plus the cofinal argument.

## Attempt 6: use ordinary category nerves as counterexamples

**Idea.** The nerve of a category is local for finite spine inclusions and can have parallel arrows.

**Failure.** The map \(j\) includes a limit point. In the ordinary nerve of \(\omega+1\), a constant chain can admit many noncontinuous cocone extensions. Hence ordinary nerves are generally not \(j\)-local. The naive simplicial model also fails the intended chain-completeness axiom for the interval.

**Lesson.** Any counterexample must live in a model where all definable maps obey the intended continuity, not merely in a Segal model.

EOF
wc -w /mnt/data/infinite_spine_thesis.md
```

<details><summary>💭 Thinking</summary>

**Compiled and validated thesis PDF, fixing LaTeX, font, math, and TikZ issues**

</details>

```unknown
bash -lc rm -rf /mnt/data/infinite_spine_thesis/rendered && python /home/oai/skills/pdfs/scripts/render_pdf.py /mnt/data/infinite_spine_thesis.pdf --out_dir /mnt/data/infinite_spine_thesis/rendered --dpi 130
```

<details><summary>💭 Thinking</summary>

**Reviewed thesis PDF rendering, metadata, and draft images**

</details>

```json
{"search_query":[{"q":"Runze Xue Topology in Synthetic Domain Theory and its Formalisation in Agda Conjecture 6.20 PDF"}],"response_length":"short"}
```

Under explicit shape-colimit assumptions, infinite-spine locality decomposes exactly into Segal locality plus chain completeness. For set-types, thinness then yields Rezk completeness, isolating parallel-path uniqueness as the remaining step.

<details><summary>💭 Thinking</summary>

**Searched 8 websites**

</details>

```json
{"paths":["GitHub"],"query":"search"}
```

# Completed

I produced an **80-page thesis-style research manuscript**. It is not represented as a completed PhD degree submission, peer-reviewed publication, or verified solution. Xue’s original work presents the proposed completeness theorem as hypothetical; the manuscript preserves that status rather than manufacturing a proof. citeturn295980academia12

### Honest mathematical status

The full conjecture is **neither proved nor disproved**.

The strongest result developed in the manuscript is a paper-level argument—under explicitly listed shape, colimit, and coherence assumptions—that

\[
A\perp\bigl(\Lambda_\omega\hookrightarrow\Delta^\infty\bigr)
\]

implies:

- locality for every finite spine inclusion, hence the finite Segal conditions;
- \(\omega\)-chain completeness;
- and, more precisely,
  \[
  A\perp j
  \quad\Longleftrightarrow\quad
  \text{finite-spine locality}
  \;\land\;
  \text{\(\omega\)-chain completeness}.
  \]

The point where the attempted proof stops is **separation of parallel paths**. After the other deductions, the remaining question is reduced to

\[
\boxed{
A\perp j
\quad\Longrightarrow\quad
A\perp\rho
}
\]

where

\[
\rho:\mathbb I_{\parallel}\longrightarrow\mathbb I
\]

collapses the walking parallel pair to a single directed edge. Equivalently: does infinite-spine locality necessarily force \(\mathbb I\)-separation?

No valid proof of that implication was found. No validated counterexample was found either.

The manuscript also proves a conditional version: the conjecture follows for \(j\)-local objects whose open observations separate points, via the evaluation map

\[
A\longrightarrow \mathbb I^{\mathbb I^A}.
\]

It identifies the most useful next targets as mechanizing the retract and colimit arguments, computing the \(j\)-local reflection of the walking parallel pair, and searching for proof-relevant \(j\)-local objects in realizability or classifying-topos models.

## Files

[Download the Markdown thesis](sandbox:/mnt/data/infinite_spine_thesis.md)

[Download the typeset PDF thesis](sandbox:/mnt/data/infinite_spine_thesis.pdf)

