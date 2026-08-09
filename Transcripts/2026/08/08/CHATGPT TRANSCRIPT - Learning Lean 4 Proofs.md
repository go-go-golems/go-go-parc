# Learning Lean 4 Proofs

- URL: https://chatgpt.com/c/6a73d00f-ade0-83ea-9dc4-c46127297788
- Created: 2026-08-06T00:06:55.705Z

---

> I want to learn lean4 theorem proving by using this as a basis. Teach me.

<details><summary>💭 Thinking</summary>

**Designing a Lean roadmap**

I’m basing the course on the dissertation’s algebraic foundations: specifications, multisets, merges, orders, permutations, normalization, and proof certificates. I’ll begin with executable Lean patterns, then build toward the thesis’s strongest theorems.

**Designed a Lean roadmap**

</details>

```json
{"system1_search_query":[{"q":"site:lean-lang.org Lean 4 getting started installation VS Code elan official"},{"q":"site:lean-lang.org theorem proving in Lean 4 official propositions as types tactics"},{"q":"site:leanprover-community.github.io mathlib4 documentation installation Lean 4 official"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 7 websites**

</details>

```unknown
bash -lc which lake || true; which lean || true; lean --version 2>/dev/null || true
```

<details><summary>💭 Thinking</summary>

**Building the first lesson**

I’m starting with the thesis’s lawful merge operation: model each semantic identifier as a set of record variants, then prove identity, commutativity, associativity, and idempotence in Lean.

**Built the first lesson**

**Checked Lean installation and version**

</details>

# Learning Lean 4 through this thesis

We will treat the thesis as a **formalization specification**. Rather than studying disconnected toy theorems, we will progressively encode its semantic model in Lean and prove its principal claims.

I will assume you can program but are new to interactive theorem proving.

The thesis is particularly suitable because it separates its model into semantic naming, provenance state, and deterministic interpretation. fileciteturn0file0L2408-L2417 Our first target will be P03: the thesis defines evidence state as identifier-indexed sets of complete record variants and defines merge as pointwise set union. fileciteturn0file0L1589-L1611

## Course structure

| Stage | Thesis material | Lean concepts |
|---|---|---|
| 1 | Commutative, associative, idempotent merge | propositions, equality, tactics, extensionality |
| 2 | Variant-aware evidence state | structures, functions, sets, finite sets |
| 3 | Information order and least upper bounds | relations, partial orders, type classes |
| 4 | Schedule and retry independence | lists, folds, permutations, induction |
| 5 | Facts, derivations, observations | structures, namespaces, dependent invariants |
| 6 | Provenance closure | inductive predicates and graph relations |
| 7 | Least finite proof rank | recursion, well-foundedness, induction |
| 8 | Deterministic selection | sorting, total orders, deduplication |
| 9 | Canonical identity | inductive data, encoders, injectivity proofs |
| 10 | Integrated semantic kernel | API design, reusable theorem interfaces |

This order is intentional. The thesis’s merge laws are mathematically simple but expose several essential Lean techniques. Later, we will formalize the proof-rank recurrence and post-merge selection barrier. The source defines proof rank using minimum proof height and explains why unseeded cycles receive no finite rank. fileciteturn0file0L786-L801

## Setup

Install the official Lean 4 VS Code extension; the current official installer uses the extension to guide the remaining setup, while `elan` manages project-specific Lean toolchains. citeturn699938search0turn699938search22

Create a **mathlib project** using the `∀` menu in VS Code and choose **New Project**. citeturn699938search21

The official *Theorem Proving in Lean 4* book is our language reference. Its progression through propositions, equality, tactics, inductive types, structures, and type classes closely matches this course. citeturn699938search1

---

# Lesson 1: propositions, proofs, and lawful merge

## 1. A theorem is a type

In Lean, a proposition is a type. Proving the proposition means constructing a value of that type. citeturn699938search6

Start with this small theorem:

```lean
import Mathlib

example (P Q : Prop) : P ∧ Q → Q ∧ P := by
  intro h
  exact ⟨h.2, h.1⟩
```

Read it as follows:

```text
P Q : Prop
```

introduces arbitrary propositions.

```text
P ∧ Q → Q ∧ P
```

is the theorem being proved.

```lean
intro h
```

assumes evidence `h : P ∧ Q`.

```lean
h.1
```

is evidence for `P`, and `h.2` is evidence for `Q`.

```lean
⟨h.2, h.1⟩
```

constructs evidence for `Q ∧ P`.

The `by` block uses tactics. Tactics manipulate the current proof state while constructing a proof term that Lean’s kernel ultimately checks. citeturn699938search16

## 2. The thesis’s merge model

The thesis requires three central laws:

\[
a \sqcup b=b\sqcup a
\]

\[
(a\sqcup b)\sqcup c=a\sqcup(b\sqcup c)
\]

\[
a\sqcup a=a
\]

These correspond to delivery-order independence, batching independence, and duplicate/retry safety. fileciteturn0file0L764-L776

We will initially simplify the thesis’s three-component state to one record namespace.

An evidence state maps every semantic identifier to the set of complete record variants stored under that identifier:

```lean
Id → Set Record
```

Create `RagSemantics/Join.lean`:

```lean
import Mathlib

universe u v

namespace RagSemantics

/--
A simplified evidence state.

For each semantic identifier, the state stores the set of complete
record variants that claim that identifier.
-/
abbrev State (Id : Type u) (Record : Type v) :=
  Id → Set Record

/-- Pointwise union of record-variant buckets. -/
def join {Id : Type u} {Record : Type v}
    (s t : State Id Record) : State Id Record :=
  fun id => s id ∪ t id

/-- The state containing no record variants. -/
def empty {Id : Type u} {Record : Type v} :
    State Id Record :=
  fun _ => ∅
```

This definition directly expresses the thesis model:

```text
(join s t) id = s id ∪ t id
```

There is no arrival time, writer priority, or overwrite policy in the definition.

## 3. Proving commutativity

Add:

```lean
theorem join_comm {Id : Type u} {Record : Type v}
    (s t : State Id Record) :
    join s t = join t s := by
  funext id
  ext record
  simp [join, or_comm]
```

### What happened?

The initial goal is:

```text
⊢ join s t = join t s
```

Both sides are functions. Two functions are equal when they return equal outputs for every input. Therefore:

```lean
funext id
```

introduces an arbitrary identifier and changes the goal to equality of its two buckets:

```text
⊢ join s t id = join t s id
```

Each bucket is a set. Two sets are equal when they have the same members:

```lean
ext record
```

changes the goal to:

```text
⊢ record ∈ join s t id ↔ record ∈ join t s id
```

After unfolding `join`, this is essentially:

```text
record ∈ s id ∨ record ∈ t id
    ↔
record ∈ t id ∨ record ∈ s id
```

That is exactly commutativity of logical `or`, which `simp` proves.

The paper proof says “set union is commutative.” Lean forces us to expose the extensional reasoning hidden inside that sentence.

## 4. The other laws

Add these proofs:

```lean
theorem join_assoc {Id : Type u} {Record : Type v}
    (a b c : State Id Record) :
    join (join a b) c = join a (join b c) := by
  funext id
  ext record
  simp [join, or_assoc]

theorem join_idem {Id : Type u} {Record : Type v}
    (a : State Id Record) :
    join a a = a := by
  funext id
  ext record
  simp [join]

theorem join_empty_right {Id : Type u} {Record : Type v}
    (a : State Id Record) :
    join a empty = a := by
  funext id
  ext record
  simp [join, empty]

theorem join_empty_left {Id : Type u} {Record : Type v}
    (a : State Id Record) :
    join empty a = a := by
  funext id
  ext record
  simp [join, empty]
```

At this point, Lean has machine-checked the mathematical core of thesis Theorems 7.1–7.4: commutativity, associativity, idempotence, and identity. fileciteturn0file0L1643-L1663

## 5. Deriving retry safety

A retry merges the same delta twice:

```lean
theorem retry_safe {Id : Type u} {Record : Type v}
    (state delta : State Id Record) :
    join (join state delta) delta =
      join state delta := by
  rw [join_assoc, join_idem]
```

This proof is much more abstract than the earlier ones.

Lean rewrites:

```text
(state ⊔ delta) ⊔ delta
```

using associativity into:

```text
state ⊔ (delta ⊔ delta)
```

and then uses idempotence to replace:

```text
delta ⊔ delta
```

with:

```text
delta
```

This is the formal reason exact retries do not change canonical state. The thesis later generalizes the argument to arbitrary delivery permutations, batching, and duplicate messages. fileciteturn0file0L1674-L1686

## 6. The central distinction

A mutex can ensure that two workers do not mutate memory simultaneously. It cannot prove that changing their order leaves the result unchanged.

The theorem:

```lean
join_comm
```

establishes semantic order independence.

A lock establishes safe execution.

These are different obligations. The thesis explicitly distinguishes race freedom supplied by locking from schedule independence supplied by associative, commutative, idempotent union. fileciteturn0file0L1690-L1711

## Exercise

Prove that merging three identical copies of a delta has the same result as merging one:

```lean
theorem triple_retry_safe {Id : Type u} {Record : Type v}
    (state delta : State Id Record) :
    join (join (join state delta) delta) delta =
      join state delta := by
  -- Your proof here
```

Try to solve it using only:

```lean
rw
join_assoc
join_idem
```

Reply with your proof or Lean’s exact error message. The next lesson will replace unrestricted `Set` buckets with finite variant buckets and model explicit same-ID/different-record conflicts.


---

> [image: sediment://file_00000000a9b0820db41be8b379f70b5b]

<details><summary>💭 Thinking</summary>

**Fixing conjunction syntax**

I’m reading the error as Lean interpreting `^` as exponentiation, not logical “and.” I’d write:

```lean
example (P Q : Prop) : P ∧ Q → Q ∧ P := by
  intro h
  exact ⟨h.2, h.1⟩
```

I can type `∧` with `\and` followed by a space.

**Fixed conjunction syntax**

</details>

```json
{"system2_search_query":[{"q":"site:lean-lang.org Lean 4 unicode input \\and conjunction VS Code"},{"q":"site:lean-lang.org Lean 4 conjunction notation ∧ And power ^ HPow"}],"response_length":"short"}
```

<details><summary>💭 Thinking</summary>

**Searched 4 websites**

</details>

The problem is `^`. Lean interprets it as exponentiation, so it tries—and fails—to find a power operation for propositions (`HPow Prop Prop`).

Logical “and” is `∧`, not `^`.

```lean
import Mathlib

example (P Q : Prop) : P ∧ Q → Q ∧ P := by
  intro h
  exact ⟨h.2, h.1⟩
```

In VS Code:

- Type `\and` followed by Space to produce `∧`.
- Type `\to` followed by Space to produce `→`.

You can also use the ASCII notation:

```lean
example (P Q : Prop) : P /\ Q -> Q /\ P := by
  intro h
  exact ⟨h.2, h.1⟩
```

Lean officially defines both `/\` and `∧` as conjunction, and both `->` and `→` as implication. citeturn706313search0

After `intro h`, Lean has:

```text
P Q : Prop
h : P ∧ Q
⊢ Q ∧ P
```

Here:

```lean
h.1  -- proof of P
h.2  -- proof of Q
```

So `⟨h.2, h.1⟩` constructs a proof of `Q ∧ P`.

The underline beneath `intro h` is a secondary error: Lean could not understand the theorem statement above it. Once `^` is replaced, that error should disappear.


---

> [image: sediment://file_0000000055e481f996c106641c38a749]

```unknown
from PIL import Image
img=Image.open('/mnt/data/image(20260806-124030).png')
img.size

```

<details><summary>💭 Thinking</summary>

**Explaining Lean notation**

I’m identifying the issue as parentheses creating a product pair, not an `And` proof. I’ll recommend `exact And.intro h.2 h.1`, or angle-bracket constructor notation when the goal supplies the expected proposition.

**Explained Lean notation**

**Correcting constructor syntax**

I’m narrowing the remaining problem to the delimiters: `(h.2, h.1)` constructs a product, while `⟨h.2, h.1⟩` constructs the conjunction expected by the goal. `exact And.intro h.2 h.1` avoids Unicode entirely.

**Diagnosed Lean conjunction constructor type errors**

</details>

You fixed `∧`. The remaining problem is that you typed **ordinary parentheses**:

```lean
exact (h.2, h.1)
```

That syntax constructs a data pair. Your goal is a logical conjunction, so use Lean’s constructor brackets:

```lean
import Mathlib

example (P Q : Prop) : P ∧ Q → Q ∧ P := by
  intro h
  exact ⟨h.2, h.1⟩
```

The characters are `⟨` and `⟩`, not `(` and `)`.

An unambiguous alternative is:

```lean
example (P Q : Prop) : P ∧ Q → Q ∧ P := by
  intro h
  exact And.intro h.2 h.1
```

Here:

```lean
h.1  -- proof of P
h.2  -- proof of Q
```

Since the goal is `Q ∧ P`, `And.intro` first receives the proof of `Q`, then the proof of `P`.

You can also expose the construction step-by-step:

```lean
example (P Q : Prop) : P ∧ Q → Q ∧ P := by
  intro h
  constructor
  · exact h.2
  · exact h.1
```

After `constructor`, Lean splits the goal into:

```text
⊢ Q
```

and then:

```text
⊢ P
```

This third version is best for learning because the proof state shows exactly what conjunction construction requires.


---

> how do I type constructor bracket? just make a general cheatsheet for the symbols i might encounter in this domain

```json
{"system2_search_query":[{"q":"site:lean-lang.org Lean 4 unicode input abbreviations \\langle \\rangle VS Code"},{"q":"site:docs.lean-lang.org Lean 4 unicode input symbols conjunction implication forall exists"},{"q":"site:leanprover-community.github.io Lean unicode input abbreviations VS Code"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Compiling Lean symbols**

I’m organizing a compact Lean cheat sheet by Unicode entry methods and notation families: logic, types, sets, relations, algebra, collections, Greek letters, and syntax such as `⟨⟩`, `:=`, and `⊢`.

**Compiled Lean symbols**

**Searched 5 websites**

</details>

```json
{"open":[{"ref_id":"https://raw.githubusercontent.com/leanprover/vscode-lean4/master/vscode-lean4/src/abbreviation/abbreviations.json"}],"response_length":"short"}
```

<details><summary>💭 Thinking</summary>

**Searching the web**

</details>

```unknown
bash -lc git ls-remote https://github.com/leanprover/vscode-lean4.git HEAD
```

<details><summary>💭 Thinking</summary>

**Building the cheat sheet**

I’m explaining why `(h.2, h.1)` fails: parentheses create a product, while `⟨h.2, h.1⟩` uses the expected constructor, such as `And.intro`. I’ll also include join notation like `⊔` and `⊥` used in the thesis.

**Built the cheat sheet**

**Checked GitHub repository access**

</details>

# Lean 4 symbol cheatsheet

## Typing Unicode in VS Code

Type a backslash mnemonic, then press **Tab** or **Space**.

For constructor brackets, type:

```text
\<>
```

then press **Tab**. It becomes:

```text
⟨⟩
```

with the cursor placed between the brackets. The Lean 4 extension also shows input abbreviations when you hover over a Unicode symbol. To browse everything, open the command palette with `Ctrl+Shift+P` and search for **Unicode Input Abbreviations**, or use the `∀` menu. citeturn404736search7turn956833search0

Thus your proof is typed as:

```lean
exact \<>h.2, h.1
```

After converting `\<>`, it becomes:

```lean
exact ⟨h.2, h.1⟩
```

---

## Logic

Lean’s standard propositional operators and their editor shortcuts include the following. citeturn956833search3

| Symbol | Type this | ASCII alternative | Meaning |
|---|---|---|---|
| `∧` | `\and` | `/\` | and |
| `∨` | `\or` | `\/` | or |
| `¬` | `\not` or `\neg` | `Not` | not |
| `→` | `\to` | `->` | implication/function |
| `↔` | `\iff` | `<->` | if and only if |
| `∀` | `\forall` | `forall` | for every |
| `∃` | `\exists` | `Exists` | there exists |
| `True` | type directly | — | always-true proposition |
| `False` | type directly | — | impossible proposition |

Examples:

```lean
P ∧ Q
P ∨ Q
¬ P
P → Q
P ↔ Q
∀ x, P x
∃ x, P x
```

### Boolean versus propositional logic

| Propositions | Booleans |
|---|---|
| `P ∧ Q` | `a && b` |
| `P ∨ Q` | `a \|\| b` |
| `¬ P` | `!a` |

`P ∧ Q` is a mathematical proposition. `a && b` computes a `Bool`.

---

## Constructors and grouping

| Syntax | Meaning |
|---|---|
| `⟨a, b⟩` | construct the expected type |
| `(a, b)` | construct a `Prod`, an ordinary data pair |
| `(expression)` | grouping |
| `h.1` | first projection |
| `h.2` | second projection |
| `{ field := value }` | structure construction |
| `{s with field := value}` | structure update |

This distinction caused your previous error:

```lean
(h.2, h.1)    -- a Prod
⟨h.2, h.1⟩    -- constructs the expected Q ∧ P
```

For conjunction, the long form is:

```lean
And.intro h.2 h.1
```

The constructor notation is equivalent:

```lean
⟨h.2, h.1⟩
```

---

## Equality and ordering

| Symbol | Type this | Meaning |
|---|---|---|
| `=` | keyboard | propositional equality |
| `≠` | `\ne` | not equal |
| `<` | keyboard | less than |
| `>` | keyboard | greater than |
| `≤` | `\le` | less than or equal |
| `≥` | `\ge` | greater than or equal |
| `≈` | `\approx` | overloaded equivalence relation |
| `≃` | `\simeq` | equivalence/isomorphism |

Important distinctions:

```lean
x = y     -- proposition asserting equality
x == y    -- Boolean equality test, when BEq is available
```

```lean
def answer : Nat := 42
--                 ^^ definition assignment
```

`=` states equality. `:=` gives a definition its value.

---

## Sets and finite sets

| Symbol | Type this | Meaning |
|---|---|---|
| `∈` | `\in` | is a member of |
| `∉` | `\notin` | is not a member of |
| `⊆` | `\subseteq` | subset |
| `⊂` | `\subset` | strict subset, depending on context |
| `∪` | `\cup` | union |
| `∩` | `\cap` | intersection |
| `∅` | `\emptyset` | empty set |
| `\` | keyboard | set difference in some notation |
| `{x \| P x}` | keyboard | set of `x` satisfying `P x` |

Examples:

```lean
x ∈ A
x ∉ A
A ⊆ B
A ∪ B
A ∩ B
∅
{x | P x}
```

A `Set α` in Lean is essentially a predicate:

```lean
Set α = α → Prop
```

Therefore:

```lean
x ∈ A
```

means that the proposition `A x` holds.

---

## Algebra and the thesis’s merge notation

| Symbol | Type this | Typical meaning |
|---|---|---|
| `⊔` | `\sqcup` | join, supremum, merge |
| `⊓` | `\sqcap` | meet, infimum |
| `⊥` | `\bot` | bottom/empty element |
| `⊤` | `\top` | top element |
| `∘` | `\circ` | function composition |
| `×` | `\times` | product |
| `⊕` | `\oplus` | sum/direct sum |
| `∑` | `\sum` | finite or indexed sum |
| `∏` | `\prod` | finite or indexed product |

The thesis uses `⊔` for evidence-state merge and states the three central laws:

```text
a ⊔ b = b ⊔ a
(a ⊔ b) ⊔ c = a ⊔ (b ⊔ c)
a ⊔ a = a
```

These are commutativity, associativity, and idempotence. fileciteturn0file0L764-L776

In Lean, once we define suitable notation, these may look like:

```lean
theorem join_comm (a b : State) :
    a ⊔ b = b ⊔ a := by
  ...

theorem join_idem (a : State) :
    a ⊔ a = a := by
  ...
```

For our early lessons, we may use the explicit name `join a b` before introducing `⊔`.

---

## Functions and types

| Symbol/syntax | Type this | Meaning |
|---|---|---|
| `α → β` | `\to` | function from `α` to `β` |
| `λ x => t` | `\lambda` | anonymous function |
| `fun x => t` | keyboard | preferred ASCII lambda syntax |
| `α × β` | `\times` | product type |
| `:` | keyboard | “has type” |
| `Type` | keyboard | universe of data types |
| `Prop` | keyboard | universe of propositions |
| `Sort` | keyboard | general universe |

Examples:

```lean
f : α → β

fun x => x + 1

λ x => x + 1
```

The following are equivalent:

```lean
P → Q
```

and:

```lean
P -> Q
```

In theorem proving, implication is represented by a function from proofs of `P` to proofs of `Q`.

---

## Binder brackets

Brackets have different meanings in declarations:

```lean
(x : α)          -- explicit argument
{x : α}          -- implicit argument
[x : C α]        -- type-class argument
```

Example:

```lean
theorem example
    {α : Type}
    [DecidableEq α]
    (x : α) :
    x = x := by
  rfl
```

Here:

- `{α : Type}` is inferred when possible.
- `[DecidableEq α]` asks Lean to synthesize an instance.
- `(x : α)` must normally be supplied explicitly.

---

## Common punctuation

| Syntax | Meaning |
|---|---|
| `:` | has type |
| `:=` | definition body or named argument |
| `=>` | function, match, or branch body |
| `->` | ASCII function arrow |
| `.` | namespace access or field projection |
| `_` | infer this value / wildcard |
| `@f` | expose all implicit arguments of `f` |
| `|` | pattern branch or set-builder separator |
| `;` | tactic sequencing |
| `·` | proof bullet for one subgoal |
| `⊢` | “the current goal is” |

You normally do not type `⊢`. Lean displays it in the InfoView:

```text
h : P ∧ Q
⊢ Q ∧ P
```

This means:

> Given `h : P ∧ Q`, construct a proof of `Q ∧ P`.

A subgoal bullet can be typed using `\.` and appears as `·`:

```lean
example (P Q : Prop) : P ∧ Q → Q ∧ P := by
  intro h
  constructor
  · exact h.2
  · exact h.1
```

---

## Number systems and Greek letters

| Symbol | Type this |
|---|---|
| `ℕ` | `\N` |
| `ℤ` | `\Z` |
| `ℚ` | `\Q` |
| `ℝ` | `\R` |
| `α` | `\alpha` |
| `β` | `\beta` |
| `γ` | `\gamma` |
| `δ` | `\delta` |
| `ε` | `\epsilon` |
| `π` | `\pi` |
| `Δ` | `\Delta` |
| `Σ` | `\Sigma` |

Greek letters are commonly used as generic type names:

```lean
variable {α β : Type}

def compose (f : β → γ) (g : α → β) : α → γ :=
  fun x => f (g x)
```

---

## Frequent beginner traps

```lean
P ^ Q       -- wrong: ^ means exponentiation
P ∧ Q       -- logical conjunction
```

```lean
(a, b)      -- Prod pair
⟨a, b⟩      -- expected-type constructor
```

```lean
P -> Q      -- implication/function arrow
x => y      -- body of a lambda or pattern branch
```

```lean
x = y       -- equality proposition
x == y      -- Boolean comparison
```

```lean
P ∧ Q       -- propositions
p && q      -- Boolean values
```

The most useful command to remember is:

```text
Ctrl+Shift+P → Unicode Input Abbreviations
```

That removes the need to memorize uncommon symbols.


---

> what is the i mmediatie consequence operator induced by the rules R, and is it a common term in theory, and who came up with it?

```json
{"system1_search_query":[{"q":"immediate consequence operator logic programming van Emden Kowalski 1976 PDF"},{"q":"T_P operator immediate consequence operator history logic programming"},{"q":"van Emden Kowalski semantics of predicate logic as programming language immediate consequence operator"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 24 websites**

</details>

The **immediate consequence operator induced by a rule set \(R\)** is the function that takes the facts currently known and returns the facts derivable by **one application** of the rules.

Suppose rules have the form

\[
B_1 \land \cdots \land B_n \rightarrow H.
\]

For a set of known facts \(I\), define

\[
T_R(I)
=
\left\{
H \;\middle|\;
\text{some ground instance }(B_1\land\cdots\land B_n\rightarrow H)\text{ of a rule in }R,
\;B_1,\dots,B_n\in I
\right\}.
\]

“Ground” means that all variables have been replaced by concrete terms.

## Example

Let

\[
R =
\left\{
\begin{aligned}
&\operatorname{parent}(x,y)\land\operatorname{parent}(y,z)
   \rightarrow \operatorname{grandparent}(x,z),\\
&\operatorname{grandparent}(x,z)
   \rightarrow \operatorname{ancestor}(x,z)
\end{aligned}
\right\}.
\]

Start with

\[
I_0 =
\{
\operatorname{parent}(a,b),
\operatorname{parent}(b,c)
\}.
\]

One application gives

\[
T_R(I_0)
=
\{
\operatorname{grandparent}(a,c)
\}.
\]

The second rule cannot yet fire because `grandparent(a,c)` was not in the **input** \(I_0\). After another iteration:

\[
T_R(T_R(I_0))
=
\{
\operatorname{ancestor}(a,c)
\},
\]

depending on whether \(T_R\) is defined as producing only newly derivable facts or all rule conclusions. In fixed-point presentations one often uses the inflationary form

\[
F_R(I)=I\cup T_R(I),
\]

so facts accumulate:

\[
I_0,\quad F_R(I_0),\quad F_R^2(I_0),\ldots
\]

until a fixed point is reached.

That fixed point is the closure of the initial facts under the rules.

## Why it is called “immediate”

A fact is an **immediate consequence** of \(I\) when one rule application is enough, with every premise already present in \(I\).

It is not necessarily a consequence requiring several inference steps. Multi-step consequences appear by iteration:

\[
T_R^0(\varnothing),\;
T_R^1(\varnothing),\;
T_R^2(\varnothing),\ldots
\]

For definite logic programs, the least fixed point of \(T_R\) gives the program’s least Herbrand model.

## Connection to your thesis

The thesis’s proof-rank process is closely related. It starts with seed derivations, gives their outputs rank zero, and repeatedly permits a derivation once all its inputs have ranks. fileciteturn0file0L786-L801

The consolidated model explicitly describes a rank operator \(T\) on partial rank maps:

\[
R_0=\varnothing,\qquad R_{n+1}=T(R_n),
\]

and states that repeated relaxation reaches the least finite proof-rank fixed point. fileciteturn0file0L2563-L2573

So, in the thesis setting, an analogous consequence operator could be defined on sets of proved facts:

\[
T_R(I)
=
I
\cup
\left\{
\operatorname{output}(d)
\;\middle|\;
d\in R
\text{ and }
\operatorname{inputs}(d)\subseteq I
\right\}.
\]

Here:

- \(R\) is the set of derivations or inference rules;
- \(I\) is the set of facts already supported;
- \(T_R(I)\) adds every fact whose derivation premises are already supported.

The thesis does not itself use the phrase “immediate consequence operator” in the passages above; it describes the corresponding construction as repeated relaxation and a proof-rank operator.

## Is it a common theoretical term?

Yes. It is standard terminology in:

- logic programming;
- Datalog;
- deductive databases;
- fixed-point semantics;
- Horn-clause semantics;
- rule-based knowledge representation.

The notation is commonly \(T_P\), where \(P\) is a logic program. It is often called the **immediate consequence operator**, the **one-step consequence operator**, or the **van Emden–Kowalski operator**.

The basic properties usually proved are:

\[
I\subseteq J
\quad\Longrightarrow\quad
T_P(I)\subseteq T_P(J),
\]

so \(T_P\) is monotone for definite programs, and

\[
\operatorname{lfp}(T_P)
=
\bigcup_{n<\omega}T_P^n(\varnothing).
\]

The least fixed point corresponds to the least Herbrand model.

## Who introduced it?

The operator is conventionally credited to **Maarten H. van Emden and Robert A. Kowalski**, especially their paper *The Semantics of Predicate Logic as a Programming Language*, published in the *Journal of the ACM* in 1976. That paper compared operational, model-theoretic, and fixed-point semantics for logic programs and used the transformation now commonly written \(T_P\). citeturn688781search2turn688781search12turn688781search20

There was also an Edinburgh technical-report version in 1974, preceding the journal publication. citeturn688781search19

They did not invent fixed-point theory itself. Their construction builds on earlier foundations, particularly:

- Tarski’s fixed-point theorem for monotone operators on complete lattices;
- Herbrand semantics;
- Horn-clause logic;
- earlier work on program and recursive-definition semantics.

The historically precise statement is therefore:

> Van Emden and Kowalski introduced and established the standard immediate-consequence-operator formulation for definite logic-program semantics; its mathematical fixed-point machinery predates their work.

A Lean-shaped definition for the thesis model would begin approximately like this:

```lean
def immediateConsequence
    (rules : Set Derivation)
    (known : Set FactId) : Set FactId :=
  known ∪
    {fact |
      ∃ d ∈ rules,
        d.output = fact ∧
        ∀ input ∈ d.inputs, input.fact ∈ known}
```

The next useful step is to formalize this and prove monotonicity:

```lean
known₁ ⊆ known₂ →
  immediateConsequence rules known₁
    ⊆ immediateConsequence rules known₂
```


---

> how important was their paper, and walk me through a self contained lean tutorial about rule appliction

<details><summary>💭 Thinking</summary>

**Preparing the explanation**

I’m going to separate historical significance from the Lean tutorial, using the thesis for the formal development and reliable external sources for broader context. I’ll make the Lean section self-contained, especially around theorem application.

**Prepared the explanation**

</details>

```json
{"system1_search_query":[{"q":"van Emden Kowalski 1976 semantics predicate logic as a programming language original paper pdf"},{"q":"history logic programming immediate consequence operator van Emden Kowalski foundational"},{"q":"ACM van Emden Kowalski 1976 semantics predicate logic programming language citation award"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 28 websites**

</details>

```unknown
bash -lc lean --version || lake --version || echo no-lean
```

<details><summary>💭 Thinking</summary>

**Designing the Lean tutorial**

I’m choosing a simple rule representation that supports both executable examples and mathematical reasoning. I’ll explain theorem application through explicit premises, matching, and forward chaining, while keeping the formalization readable and coherent.

**Designed the Lean tutorial**

**Checked Lean environment before tutorial development**

</details>

```json
{"open":[{"ref_id":"turn160469search0"},{"ref_id":"turn160469search3"},{"ref_id":"turn160469search6"},{"ref_id":"turn160469search13"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

```unknown
bash -lc apt-cache search '^lean$|lean theorem|lean4' | head -20
```

<details><summary>💭 Thinking</summary>

**Explained Lean rule application sections**

</details>

## How important was the van Emden–Kowalski paper?

It was **foundational**. Its main contribution was not a new Prolog implementation, but a mathematical account showing how three views of a definite logic program fit together:

1. **Operational:** execute rules as a computation.
2. **Proof-theoretic:** rule execution constructs logical proofs.
3. **Fixed-point/model-theoretic:** the program denotes the least interpretation closed under its rules.

The paper explicitly defines operational and fixed-point semantics, relates them to proof theory and model theory, and explains their equivalence through standard logical completeness results. citeturn994087view0

This was important because it gave logic programs a meaning independent of implementation details such as search order. It made questions such as these mathematically precise:

- Is rule execution sound?
- Does it find every consequence it should?
- What set of facts does a recursive program ultimately define?
- Does bottom-up iteration agree with logical truth in the intended model?

The operator usually written \(T_P\) became standard enough that later literature describes it as the “ubiquitous” immediate-consequence operator. citeturn160469search6

The historical qualification is that van Emden and Kowalski did **not** single-handedly invent logic programming or Prolog. Colmerauer, Roussel, Pasero, Kowalski, and others contributed to the paradigm, and the first Prolog system was implemented in Marseille in 1972. The 1976 paper supplied one of its central semantic foundations. citeturn994087view3

---

# Lean tutorial: formalizing rule application

Create a file named `RuleApplication.lean`. Paste the following sections into it in order.

We will formalize **ground positive rules**:

\[
\{p_1,\ldots,p_n\}\longrightarrow q.
\]

“Ground” means there are no variables or substitutions yet. A rule already names its concrete premises and conclusion.

This closely matches the thesis’s simplified mathematical view of a derivation as a directed hyperedge from finitely many input facts to one output fact. fileciteturn0file0L1401-L1412

## 1. Define the possible facts

```lean
import Mathlib

namespace RuleApplication

inductive Atom where
  | parentAB
  | parentBC
  | grandparentAC
  | ancestorAC
deriving DecidableEq, Repr
```

`Atom` is a type with four possible values.

Conceptually:

```text
parentAB       means parent(a, b)
parentBC       means parent(b, c)
grandparentAC  means grandparent(a, c)
ancestorAC     means ancestor(a, c)
```

Each constructor is distinct. For example, Lean knows:

```lean
example : Atom.parentAB ≠ Atom.parentBC := by
  decide
```

`inductive` is used for a type with multiple constructors, while `structure` below will package several fields into one record. citeturn825429search23turn825429search26

## 2. Define a rule

```lean
structure Rule where
  premises : Set Atom
  conclusion : Atom
```

A value of type `Rule` has:

- a set of premises;
- one conclusion.

For example:

```lean
def grandparentRule : Rule where
  premises := {Atom.parentAB, Atom.parentBC}
  conclusion := Atom.grandparentAC

def ancestorRule : Rule where
  premises := {Atom.grandparentAC}
  conclusion := Atom.ancestorAC
```

These represent:

\[
\operatorname{parent}(a,b)\land\operatorname{parent}(b,c)
\rightarrow
\operatorname{grandparent}(a,c)
\]

and

\[
\operatorname{grandparent}(a,c)
\rightarrow
\operatorname{ancestor}(a,c).
\]

## 3. Define when a rule applies

```lean
def Applies (r : Rule) (known : Set Atom) : Prop :=
  r.premises ⊆ known
```

Read:

```lean
Applies r known
```

as:

> Every premise of `r` occurs in `known`.

A subset proof is function-like. Given an arbitrary atom and proof that it is a premise, it must return a proof that the atom is known.

In Mathlib, `Set α` is represented as a predicate `α → Prop`, which is why set membership and subset proofs behave this way. citeturn825429search4turn825429search17

For example:

```lean
def initial : Set Atom :=
  {Atom.parentAB, Atom.parentBC}

example : Applies grandparentRule initial := by
  intro atom hPremise
  simpa [grandparentRule, initial] using hPremise
```

After `intro atom hPremise`, the proof state is conceptually:

```text
atom : Atom
hPremise : atom ∈ grandparentRule.premises
⊢ atom ∈ initial
```

The two sets are identical, so the existing proof `hPremise` establishes the goal.

## 4. Define the immediate-consequence operator

```lean
def immediate
    (rules : Set Rule)
    (known : Set Atom) : Set Atom :=
  {atom |
    ∃ r ∈ rules,
      Applies r known ∧
      r.conclusion = atom}
```

This is our \(T_R\).

An atom belongs to `immediate rules known` exactly when there exists a rule such that:

1. the rule belongs to `rules`;
2. it applies to `known`;
3. its conclusion is that atom.

Notice that this operator returns **rule conclusions**. It does not automatically retain the input facts.

For accumulating facts, define:

```lean
def step
    (rules : Set Rule)
    (known : Set Atom) : Set Atom :=
  known ∪ immediate rules known
```

Thus:

\[
\operatorname{step}_R(I)=I\cup T_R(I).
\]

## 5. Prove the generic rule-application theorem

```lean
theorem apply_rule
    {rules : Set Rule}
    {known : Set Atom}
    {r : Rule}
    (hr : r ∈ rules)
    (hApplies : Applies r known) :
    r.conclusion ∈ immediate rules known := by
  change ∃ s ∈ rules,
    Applies s known ∧
    s.conclusion = r.conclusion

  exact ⟨r, hr, hApplies, rfl⟩
```

This is the central theorem of the tutorial.

The `change` command exposes what membership in `immediate` means. The goal becomes:

```text
⊢ ∃ s ∈ rules,
    Applies s known ∧
    s.conclusion = r.conclusion
```

We then construct the existential proof:

```lean
⟨r, hr, hApplies, rfl⟩
```

Its components are:

```text
r          the rule witnessing the existential
hr         proof that r belongs to rules
hApplies   proof that its premises are known
rfl        proof that its conclusion equals itself
```

This is rule application as a proof term.

We can immediately lift that result into the accumulating `step` operator:

```lean
theorem apply_rule_step
    {rules : Set Rule}
    {known : Set Atom}
    {r : Rule}
    (hr : r ∈ rules)
    (hApplies : Applies r known) :
    r.conclusion ∈ step rules known := by
  change
    r.conclusion ∈ known ∨
    r.conclusion ∈ immediate rules known

  exact Or.inr (apply_rule hr hApplies)
```

The conclusion is in the right-hand side of the union.

## 6. Define the complete rule set

```lean
def rules : Set Rule :=
  {grandparentRule, ancestorRule}
```

Prove that each rule belongs to it:

```lean
theorem grandparentRule_mem :
    grandparentRule ∈ rules := by
  simp [rules]

theorem ancestorRule_mem :
    ancestorRule ∈ rules := by
  simp [rules]
```

The `simp` tactic reduces membership in a two-element set.

## 7. Apply the first rule

First prove that the rule applies:

```lean
theorem grandparentRule_applies :
    Applies grandparentRule initial := by
  intro atom hPremise
  simpa [grandparentRule, initial] using hPremise
```

Now invoke the generic theorem:

```lean
theorem grandparent_after_one :
    Atom.grandparentAC ∈ immediate rules initial := by
  simpa [grandparentRule] using
    (apply_rule
      grandparentRule_mem
      grandparentRule_applies)
```

Read this proof as:

> The grandparent rule is in the program, and all its premises occur initially. Therefore its conclusion is an immediate consequence.

Define the accumulated first stage:

```lean
def stage1 : Set Atom :=
  step rules initial
```

Then:

```lean
theorem grandparent_in_stage1 :
    Atom.grandparentAC ∈ stage1 := by
  change
    Atom.grandparentAC ∈ initial ∨
    Atom.grandparentAC ∈ immediate rules initial

  exact Or.inr grandparent_after_one
```

So `stage1` contains:

```text
parentAB
parentBC
grandparentAC
```

## 8. Apply the second rule

The ancestor rule requires `grandparentAC`.

```lean
theorem ancestorRule_applies_stage1 :
    Applies ancestorRule stage1 := by
  intro atom hPremise

  have hAtom : atom = Atom.grandparentAC := by
    simpa [ancestorRule] using hPremise

  subst atom
  exact grandparent_in_stage1
```

Walk through this proof:

```lean
intro atom hPremise
```

gives an arbitrary premise of the ancestor rule.

Since the ancestor rule has only one premise, we establish:

```lean
have hAtom : atom = Atom.grandparentAC := by
  simpa [ancestorRule] using hPremise
```

Then:

```lean
subst atom
```

replaces `atom` by `Atom.grandparentAC`.

The remaining goal is exactly the theorem already proved:

```lean
grandparent_in_stage1
```

Now define the second accumulated stage:

```lean
def stage2 : Set Atom :=
  step rules stage1
```

Apply the rule:

```lean
theorem ancestor_in_stage2 :
    Atom.ancestorAC ∈ stage2 := by
  change
    Atom.ancestorAC ∈ stage1 ∨
    Atom.ancestorAC ∈ immediate rules stage1

  exact Or.inr <|
    by
      simpa [ancestorRule] using
        (apply_rule
          ancestorRule_mem
          ancestorRule_applies_stage1)
```

The derivation is now:

```text
parentAB ─┐
          ├─ grandparentAC ── ancestorAC
parentBC ─┘
```

The second rule cannot fire against `initial`; it fires only after `grandparentAC` has entered the accumulated state.

## 9. Define arbitrary iteration

Instead of naming every stage manually:

```lean
def iterate
    (rules : Set Rule)
    (start : Set Atom) :
    Nat → Set Atom
  | 0 => start
  | n + 1 => step rules (iterate rules start n)
```

This gives:

```text
iterate rules initial 0 = initial
iterate rules initial 1 = step rules initial
iterate rules initial 2 = step rules (step rules initial)
```

Our result can be restated as:

```lean
example :
    Atom.ancestorAC ∈ iterate rules initial 2 := by
  simpa [iterate, stage1, stage2] using
    ancestor_in_stage2
```

This is the finite iteration

\[
I_0,\quad I_1=I_0\cup T_R(I_0),\quad
I_2=I_1\cup T_R(I_1),\ldots
\]

## 10. Prove monotonicity

The central mathematical property is:

\[
I\subseteq J
\Longrightarrow
T_R(I)\subseteq T_R(J).
\]

First prove that applicability is monotone:

```lean
theorem applies_mono
    {r : Rule}
    {I J : Set Atom}
    (hIJ : I ⊆ J)
    (hApplies : Applies r I) :
    Applies r J := by
  intro atom hPremise
  exact hIJ (hApplies hPremise)
```

Interpretation:

1. `hApplies hPremise` proves that the premise is in `I`.
2. `hIJ` transfers membership from `I` to `J`.

Now prove monotonicity of the operator:

```lean
theorem immediate_mono
    {rules : Set Rule}
    {I J : Set Atom}
    (hIJ : I ⊆ J) :
    immediate rules I ⊆ immediate rules J := by
  intro atom hAtom

  change ∃ r ∈ rules,
    Applies r I ∧
    r.conclusion = atom at hAtom

  change ∃ r ∈ rules,
    Applies r J ∧
    r.conclusion = atom

  rcases hAtom with
    ⟨r, hr, hApplies, hConclusion⟩

  exact ⟨
    r,
    hr,
    applies_mono hIJ hApplies,
    hConclusion
  ⟩
```

Nothing about the rule itself changes. The same rule is still present, has the same conclusion, and remains applicable when the known set grows.

This monotonicity is what allows repeated iteration to approach a least fixed point. It depends on our rules having only **positive premises**. A negative premise such as “derive \(q\) when \(p\) is absent” would not behave monotonically.

## 11. Represent complete proof trees

Iteration describes which facts appear at each stage. We can separately define what it means for a fact to have a finite derivation.

```lean
inductive Derivable
    (rules : Set Rule)
    (seeds : Set Atom) :
    Atom → Prop where

  | seed
      {atom : Atom}
      (hSeed : atom ∈ seeds) :
      Derivable rules seeds atom

  | byRule
      {r : Rule}
      (hr : r ∈ rules)
      (hPremises :
        ∀ atom,
          atom ∈ r.premises →
          Derivable rules seeds atom) :
      Derivable rules seeds r.conclusion
```

There are two ways to construct a derivation:

```text
Derivable.seed
```

says an initial fact is derivable.

```text
Derivable.byRule
```

says a rule conclusion is derivable when every premise is derivable.

Prove the grandparent fact:

```lean
theorem grandparent_derivable :
    Derivable rules initial Atom.grandparentAC := by
  apply Derivable.byRule
    (r := grandparentRule)
    grandparentRule_mem

  intro atom hPremise

  apply Derivable.seed
  exact grandparentRule_applies hPremise
```

The proof tree has two seed leaves and one rule node.

Now prove the ancestor fact:

```lean
theorem ancestor_derivable :
    Derivable rules initial Atom.ancestorAC := by
  apply Derivable.byRule
    (r := ancestorRule)
    ancestorRule_mem

  intro atom hPremise

  have hAtom : atom = Atom.grandparentAC := by
    simpa [ancestorRule] using hPremise

  subst atom
  exact grandparent_derivable
```

This constructs the nested proof tree:

```text
seed parentAB       seed parentBC
       \               /
        grandparent rule
               |
        grandparentAC
               |
          ancestor rule
               |
          ancestorAC
```

## Two complementary semantics

We now have two views.

### Set-iteration semantics

```lean
immediate rules known
iterate rules initial n
```

This computes facts layer by layer.

### Proof-tree semantics

```lean
Derivable rules initial atom
```

This records why an individual fact follows.

The van Emden–Kowalski result is significant precisely because, for definite programs, the fixed-point, model-theoretic, and proof-oriented views coincide. citeturn994087view0

The thesis develops a related refinement: seeds receive proof rank zero, and a rule result receives one plus the maximum rank of its premises, choosing the least rank among alternate proofs. fileciteturn0file0L786-L801 Its consolidated semantics describes this as repeated application of an operator on partial rank maps until reaching a fixed point. fileciteturn0file0L2563-L2573

Close the namespace at the end of the file:

```lean
end RuleApplication
```

## First exercise

Prove that `ancestorAC` is **not** an immediate consequence of the initial facts:

```lean
theorem ancestor_not_immediate :
    Atom.ancestorAC ∉ immediate rules initial := by
  -- begin here
```

The useful first step is:

```lean
  intro h
  change ∃ r ∈ rules,
    Applies r initial ∧
    r.conclusion = Atom.ancestorAC at h
```

You then need to inspect which of the two rules supplied the existential witness.

