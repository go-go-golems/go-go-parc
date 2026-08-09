# Lean4 and HoTT comparison

- URL: https://chatgpt.com/c/6a7327dc-e21c-83ea-aecf-4e017d630f5c
- Created: 2026-08-05T12:09:37.153Z

---

> Lean4 and homotopy type theory, or maybe also, how can I implement a hott based proof engine myself? Or type engine which I guess is the same ?

I’ll separate three questions: what Lean 4 can express, what HoTT requires from a kernel, and how to build a small trusted type/proof engine from scratch.

```json
{"system1_search_query":[{"q":"site:lean-lang.org Lean 4 reference manual proof irrelevance quotient kernel dependent type theory"},{"q":"site:lean-lang.org theorem proving in lean 4 dependent type theory propositions proof irrelevance"},{"q":"Homotopy Type Theory book official PDF univalence higher inductive types"},{"q":"Cubical Type Theory paper Cohen Coquand Huber Mörtberg PDF"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 22 websites**

**Designing a proof engine**

I’m recommending a staged path: begin with dependent types and identity types, then add univalence or cubical features. I’ll separate syntax, elaboration, kernel checking, normalization, and proof search, clarifying their roles.

**Designed a proof engine**

</details>

```json
{"open":[{"ref_id":"https://agda.readthedocs.io/en/latest/language/cubical.html"},{"ref_id":"https://agda.readthedocs.io/en/latest/language/cubical-compatible.html"},{"ref_id":"https://github.com/AndrasKovacs/elaboration-zoo"},{"ref_id":"https://github.com/AndrasKovacs/smalltt"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 2 websites**

**Planning a staged implementation**

I’m separating the project into core checking, elaboration, normalization, and proof search. I’ll recommend starting with intensional dependent type theory, then choosing axiomatic univalence or full cubical computation.

**Planned a staged implementation**

</details>

## The distinction

A **type engine** and a **proof engine** are related, but not identical.

Under Curry–Howard, a proof is a term whose type is the theorem:

```text
proof : theorem
```

The **kernel/type checker** verifies that relationship. A **proof engine**—tactics, automation, unification, search—constructs the term. It can be large and buggy without compromising soundness, provided the small kernel checks its output. Lean follows exactly this architecture: tactics generate core proof terms, and the kernel checks them. citeturn921648view2

```text
source text
    ↓
parser
    ↓
elaborator + unification + tactics
    ↓
fully explicit core term
    ↓
small trusted type checker
```

So the correct first project is usually **a dependent type checker**, followed later by an elaborator and proof-search layer.

## Lean 4 versus HoTT

Lean 4 is based on dependent type theory, but its standard kernel is **not a native HoTT kernel**.

In particular:

- Lean’s proposition universe `Prop` is definitionally proof-irrelevant.
- Lean’s built-in equality has type `Eq a b : Prop`.
- Consequently, equality proofs do not retain the higher path structure that HoTT needs. citeturn921648view1turn105098search0

In HoTT, an equality

```text
p : x = y
```

is interpreted as a path. There may be different paths `p` and `q`, paths between those paths, and so forth. The HoTT book’s central additions are univalence and higher inductive types. citeturn967943search45turn967943search26

Therefore, there are three reasonable approaches:

1. **Use Lean 4 for ordinary dependent type theory**, without genuine internal HoTT.
2. **Implement a separate HoTT object language in Lean 4.** Lean is then your implementation language, not the object theory.
3. **Use a native HoTT-oriented prover**, especially Cubical Agda or Arend.

Cubical Agda provides computational univalence, path types, composition operations and higher inductive types. citeturn149466view0 Arend is explicitly based on HoTT and supports higher inductive types and cubical syntax. citeturn921648view4turn921648view5

For learning the implementation, option 2 is particularly good.

---

# Implementing your own engine

## 1. Start with a very small core theory

Do not begin with tactics, notation, implicit arguments or general inductive definitions.

A reasonable first core is:

```lean
inductive Term where
  | var    : Nat → Term
  | sort   : Nat → Term
  | pi     : Term → Term → Term
  | lam    : Term → Term
  | app    : Term → Term → Term

  | sigma  : Term → Term → Term
  | pair   : Term → Term → Term
  | fst    : Term → Term
  | snd    : Term → Term

  | nat    : Term
  | zero   : Term
  | suc    : Term → Term

  | id     : Term → Term → Term → Term
  | refl   : Term → Term
```

The binder bodies use de Bruijn indices:

```text
λ. var 0
Π (A). B
```

Your identity type must live in an ordinary universe:

```text
Id A x y : Type u
```

not in a proof-irrelevant `Prop`.

Do **not** add any of the following:

```text
UIP
axiom K
proof irrelevance for all identity proofs
equality reflection
```

Those would destroy or collapse the intended higher-dimensional interpretation.

## 2. Implement evaluation

You need definitional computation for at least:

```text
(λx. t) u       ↦ t[u/x]             β
fst (a, b)      ↦ a
snd (a, b)      ↦ b
Nat eliminators on zero and successor
J ... refl      ↦ ...
```

Avoid repeatedly substituting syntax trees during type checking. Use semantic values and closures:

```lean
inductive Value where
  | sort   : Nat → Value
  | pi     : Value → Closure → Value
  | lam    : Closure → Value
  | sigma  : Value → Closure → Value
  | pair   : Value → Value → Value
  | nat
  | zero
  | suc    : Value → Value
  | id     : Value → Value → Value → Value
  | refl   : Value → Value
  | neutral : Neutral → Value
```

A closure contains a body and its environment:

```lean
structure Closure where
  body : Term
  env  : Array Value
```

This gives you:

```lean
eval  : Env → Term → Value
quote : Nat → Value → Term
```

Then definitional equality can initially be implemented by normalization:

```lean
def conv (level : Nat) (a b : Value) : Bool :=
  quote level a == quote level b
```

This is the basic normalization-by-evaluation design. NbE is widely used to obtain normal forms and decide definitional equality in normalizing dependent type theories. citeturn921648view7

## 3. Use bidirectional type checking

Split typing into two operations:

```lean
infer : Context → Term → TypeChecker Value
check : Context → Term → Value → TypeChecker Unit
```

Some terms synthesize their types:

```text
variables
universes
applications
projections
annotated terms
```

Others are naturally checked against an expected type:

```text
lambdas
pairs
refl
```

The important cases look like this:

```text
infer Γ (f a):
    tf ← infer Γ f
    Π A B ← whnf tf
    check Γ a A
    return B(eval a)

check Γ (λ. body) expected:
    Π A B ← whnf expected
    check (Γ, A) body (B freshVariable)

check Γ (a, b) expected:
    Σ A B ← whnf expected
    check Γ a A
    check Γ b (B(eval a))

check Γ (refl x) expected:
    Id A lhs rhs ← whnf expected
    check Γ x A
    require lhs ≡ x
    require rhs ≡ x

check Γ term expected:
    actual ← infer Γ term
    require actual ≡ expected
```

Bidirectional checking makes the algorithm predictable and limits where annotations are required. There is also a general formal account showing how this approach applies across dependent type theories. citeturn921648view6

At this point, a proof is simply:

```text
check emptyContext proofTerm theoremType
```

That is already a proof checker.

## 4. Add universes carefully

Use a predicative hierarchy:

```text
Type 0 : Type 1
Type 1 : Type 2
...
```

For dependent functions:

```text
A : Type u
x : A ⊢ B x : Type v
──────────────────────────
Π x : A, B x : Type (max u v)
```

Initially, concrete natural-number levels are sufficient. Later, add symbolic levels:

```text
0
succ u
max u v
level metavariables
```

Do not use:

```text
Type : Type
```

That makes an unrestricted dependent type theory inconsistent.

## 5. Add identity elimination

For ordinary intensional identity types, add `J`:

```text
J :
  (P : Π y : A, Id A x y → Type) →
  P x (refl x) →
  Π y : A, Π p : Id A x y, P y p
```

with computation:

```text
J P d x (refl x) ↦ d
```

This is enough for basic path operations:

```text
symmetry
transitivity
transport
ap
dependent ap
```

It is not yet univalence or computational HoTT, but it is the appropriate intensional foundation.

## 6. Add an elaborator

Once fully explicit core terms work, create a separate surface syntax:

```text
fun x => x
(A : Type) -> A -> A
f _
?_goal
```

The elaborator should produce your explicit `Term`.

Its state normally contains:

```lean
structure MetaVar where
  context : Context
  type    : Value
  solution : Option Term

structure ElabState where
  metavars : Array MetaVar
  constraints : Array Constraint
```

It must handle:

- named-variable resolution;
- insertion of implicit arguments;
- metavariables and holes;
- conversion constraints;
- occurs checking;
- at least pattern-style higher-order unification;
- universe constraints.

Keep this completely outside the trusted kernel.

## 7. Add tactics last

A tactic operates on a goal such as:

```lean
structure Goal where
  context : Context
  target  : Value
  metavar : MetaVarId
```

Start with:

```text
exact t
assumption
intro
apply f
refine t
constructor
left / right
cases
induction
```

For example, `intro` should inspect the target:

```text
Goal: Π x : A, B x

intro:
    create fresh local x : A
    create subgoal B x
    solve original goal with λx. ?subgoal
```

`apply f` infers the type of `f`, introduces metavariables for its arguments and unifies its result with the goal.

This is the proof engine. It constructs terms; it does not establish their validity independently.

---

# Turning it into HoTT

There are two substantially different routes.

## Route A: axiomatic HoTT

After implementing ordinary intensional type theory, postulate univalence:

```text
Equiv A B : Type

idToEquiv : Id Universe A B → Equiv A B

univalence :
  isEquiv (idToEquiv A B)
```

You can also add each higher inductive type through constants representing:

- its point constructors;
- its path constructors;
- its induction principle;
- its computation rules.

For example:

```text
Circle : Type
base   : Circle
loop   : Id Circle base base
```

This route is much easier, but univalence can produce terms that do not computationally reduce. Higher-inductive computation may also be merely propositional rather than definitional.

It is suitable for experimenting with HoTT mathematics and proof construction, but it is not the strongest design for a computational programming language.

## Route B: cubical type theory

For genuinely computational univalence, extend the kernel with cubical primitives.

A minimal conceptual list is:

```text
Interval I
endpoints 0, 1 : I
interval operations ∧, ∨, ¬

PathP : (I → Type) → A 0 → A 1 → Type
path abstraction
path application

face formulas
partial elements
systems of compatible faces

transport
homogeneous composition
dependent composition

Glue types
higher inductive constructors
```

A path is represented roughly as a function over the interval:

```text
Path A x y ≈ { p : I → A | p 0 = x and p 1 = y }
```

The hard operation is composition: given an open box with compatible faces, produce its missing face. Cubical Agda exposes this architecture as interval/path types, partial elements, transport, homogeneous composition, Glue types and higher inductive types. citeturn149466view0 The original cubical type theory construction gives computational content to univalence and supports higher inductive types. citeturn921648view3

This is a major kernel project because conversion must understand:

- interval substitutions;
- face constraints;
- overlapping systems;
- computation of composition by the outer type constructor;
- Glue reduction;
- higher-inductive boundary equations.

Do not begin here. First make the non-cubical dependent checker solid.

---

# Recommended implementation path

Use Lean 4 as the implementation language, but represent your own theory explicitly:

```text
Lean's types
    contain
your syntax, values, environments and checker

your object-language Id
    is not
Lean.Eq
```

A good repository structure would be:

```text
MiniHoTT/
  Syntax.lean
  Levels.lean
  Value.lean
  Eval.lean
  Quote.lean
  Conversion.lean
  Check.lean
  Parser.lean
  Elaborator/
    Meta.lean
    Unify.lean
    Elab.lean
  Tactic/
    Basic.lean
  Tests/
```

The concrete progression should be:

```text
Π + universes
→ normalization
→ bidirectional checking
→ Σ + Nat
→ intensional Id + J
→ metavariables and elaboration
→ basic tactics
→ axiomatic univalence
→ cubical primitives, only if computational HoTT is the goal
```

For reference implementations, the `elaboration-zoo` project contains small dependent type-checking and elaboration implementations, while Lean’s own architecture demonstrates the separation between elaboration, tactics and a small checking kernel. citeturn149466view2turn921648view1

The central design decision is therefore:

> Build an ordinary intensional dependent type checker first. Treat proof search as an untrusted term generator. Then decide whether you need axiomatic HoTT or the much larger cubical computational kernel.


---

> What does hott buy me concretely

I’ll answer in practical terms: which proofs/programs become easier, what abstractions become possible, and where HoTT adds complexity without much payoff.

```json
{"system1_search_query":[{"q":"site:homotopytypetheory.org/book HoTT book univalence equivalence identity higher inductive types"},{"q":"site:agda.readthedocs.io cubical Agda univalence higher inductive types documentation"},{"q":"site:unimath.github.io univalence equivalence equality mathematical structures"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 12 websites**

**Clarifying HoTT benefits**

I’m distinguishing mathematical expressiveness from implementation difficulty. HoTT offers principled transport across equivalences, extensional function equality, and higher inductive types for quotients and geometric constructions, but it doesn’t automatically improve ordinary programming or automation.

**Clarified benefits of Homotopy Type Theory**

</details>

HoTT mainly buys you **principled reasoning about equivalence**. It is valuable when “these objects are structurally the same” should be enough to substitute one for the other.

## 1. Equivalence becomes substitutability

Suppose:

```text
e : A ≃ B
x : F A
```

In ordinary intensional type theory, `A ≃ B` does not imply that `A` and `B` are equal. To obtain an `F B`, you usually need to prove separately that `F` respects equivalences:

```text
mapF : A ≃ B → F A → F B
```

With univalence:

```text
ua e : A = B
transport F (ua e) x : F B
```

Any dependently typed construction automatically respects equivalence because all constructions respect equality.

A concrete mathematical example is groups:

```text
G ≅ H
P : Group → Type
p : P G
```

Univalence, together with the structure identity principle, lets an isomorphism produce the appropriate equality of structured groups, after which `p` can be transported to `P H`. This formalizes the ordinary mathematical habit of treating isomorphic structures as interchangeable. citeturn386153search1turn386153search5turn386153search20

That can reduce large amounts of library plumbing involving:

- representation-change lemmas;
- invariance-under-isomorphism proofs;
- conversions between equivalent encodings;
- repeated congruence theorems for dependent constructions.

## 2. Better abstraction boundaries

Consider two implementations of finite sets:

```text
Fin n
```

and

```text
{ k : Nat // k < n }
```

Perhaps you prove they are equivalent:

```text
finEquiv : Fin n ≃ { k : Nat // k < n }
```

In conventional dependent type theory, a construction indexed by the first representation does not automatically become a construction indexed by the second:

```text
Matrix (Fin n)
Matrix { k : Nat // k < n }
```

HoTT lets you use the equivalence as an equality and transport between them. This means a library can depend more strongly on an interface or equivalence class rather than a particular representation.

The benefit is conceptually similar to representation independence in programming languages, but it works for dependent types whose later types mention the representation itself.

There is a caveat: excessive transport can produce difficult terms. A well-designed univalent library still needs good abstractions and automation.

## 3. Natural equality of functions

HoTT validates function extensionality:

```text
(∀ x, f x = g x) → f = g
```

Thus, to establish equality of functions, you prove that they agree at every input. Univalence implies function extensionality. citeturn386153search7turn386153search20

Without it, a system may distinguish:

```text
fun x => f x
```

from `f` in situations where they are not definitionally equal, even though they behave identically. Most modern proof systems provide function extensionality somehow, so this benefit is not unique to full HoTT—but HoTT explains it as part of a unified theory of equality.

## 4. Quotients and identifications as datatypes

Higher inductive types let constructors specify not just values, but also equalities between values.

For example, a quotient can conceptually be defined by:

```text
Quotient A R

point : A → Quotient A R
glue  : R x y → point x = point y
```

Instead of representing a quotient as a raw type plus a separate equivalence relation and proving repeatedly that every operation respects that relation, the identifications are built into the type.

Similarly, you can define:

```text
Interval
Circle
Pushout A B C
Truncation A
SetQuotient A R
```

using point and path constructors. Higher inductive types support constructions such as pushouts and suspensions and allow reasoning about them by induction. citeturn386153search1turn386153search17

This is one of the most concrete potential benefits for language design: **quotients that behave like first-class datatypes**.

## 5. Synthetic topology and homotopy theory

In HoTT:

```text
x = y
```

is interpreted as a space of paths from `x` to `y`.

Then:

```text
p = q
```

is a path between paths, and this continues indefinitely.

This lets you define and calculate:

- loop spaces;
- fundamental groups;
- homotopy groups;
- coverings;
- fibrations;
- spheres and projective spaces;
- pushouts and cell complexes.

Rather than encoding topological spaces as sets equipped with open subsets, you reason directly with their homotopical structure. Higher inductive types can present spaces from points, paths and higher paths. citeturn386153search17turn386153search7

This is a major benefit for topology and higher category theory. It is not necessarily useful for proving an ordinary compiler optimization correct.

## 6. Cubical HoTT can make equivalence computational

With univalence merely added as an axiom:

```text
ua : A ≃ B → A = B
```

transporting along `ua e` may get stuck during evaluation. The term is logically valid but does not necessarily compute.

Cubical type theory gives computational rules for univalence and higher inductive types. In Cubical Agda, these features have computational meaning rather than being only postulated axioms. citeturn386153search4turn386153search13

This potentially gives executable representation changes:

```text
transport (ua booleanEquivBit) true
```

can reduce according to the supplied equivalence rather than remaining an opaque transport expression.

That matters when the type theory is intended to be both:

- a logic for proofs; and
- a programming language whose closed terms should evaluate.

## What it does **not** automatically buy you

HoTT does not inherently give better:

- theorem search;
- SMT-style automation;
- rewriting performance;
- code generation;
- termination checking;
- elaboration or type inference;
- proofs about ordinary arithmetic;
- software verification ergonomics.

Those are mostly properties of the implementation, libraries and tactics rather than the foundational theory.

HoTT can actually make several implementation problems harder:

- equality has higher structure rather than being a simple proposition;
- proof irrelevance cannot be used indiscriminately;
- dependent transports become common;
- coherence problems appear;
- normalization and conversion become significantly more complicated in a cubical kernel;
- proof search must handle paths, equivalences and higher constructors.

## For your proposed proof engine

The decision can be reduced to this:

**Use ordinary dependent type theory** when you want a small prover for programs, logic, arithmetic, induction and verified software.

**Add axiomatic univalence** when you want to experiment with equivalence-based mathematics but can tolerate transports that do not compute.

**Implement cubical type theory** when computational univalence, higher inductive types or synthetic homotopy theory are central goals.

For a first engine, HoTT would buy less than Π-types, Σ-types, inductive families, good definitional equality, metavariables and a strong elaborator. The sensible sequence is:

```text
dependent type checker
→ elaborator
→ inductive types
→ tactics
→ identity/path library
→ univalence or cubical features
```

The most practical one-sentence description is:

> HoTT lets your proof system treat equivalent representations as genuinely interchangeable and lets datatypes contain specified identifications, at the cost of a substantially more complicated equality theory and kernel.


---

> What is it useful for in practice, or could be used for in say the world of crud ecommerce apps, erp style stuff

For CRUD, ecommerce, and ERP software, **full HoTT is rarely the thing that pays off**. Most practical value comes from ordinary dependent types, refinement types, state machines, and verified migrations.

HoTT becomes relevant only in a few specialized places.

## Where advanced types help immediately

### 1. Preventing invalid business states

Instead of representing an order as one large record with nullable fields:

```text
Order {
  status: "draft" | "paid" | "shipped"
  paymentId?: PaymentId
  trackingNumber?: String
}
```

represent each state separately:

```text
DraftOrder
PaidOrder {
  payment : Payment
}
ShippedOrder {
  payment : Payment
  shipment : Shipment
}
```

Then operations have precise types:

```text
pay  : DraftOrder → Payment → PaidOrder
ship : PaidOrder → Shipment → ShippedOrder
```

It becomes impossible to call `ship` on an unpaid order without bypassing the type system.

This does not require HoTT.

### 2. Correct handling of money, units, and jurisdictions

You can prevent errors such as mixing currencies:

```text
Money USD
Money EUR

add : Money c → Money c → Money c
convert : ExchangeRate USD EUR → Money USD → Money EUR
```

Or distinguish tax contexts:

```text
Invoice jurisdiction currency
```

Then an EU VAT calculation cannot accidentally be applied to a US invoice unless there is an explicit conversion or rule.

Again, this is dependent typing, not specifically HoTT.

### 3. Validated identifiers

A generic string is often too weak:

```text
CustomerId
OrderId
InvoiceId
ProductId
```

You can go further:

```text
ExistingCustomerId dbSnapshot
AuthorizedCustomerId user action
```

This allows functions such as:

```text
refund :
  AuthorizedOrder user Refund orderId →
  Refundable orderId →
  RefundResult
```

The caller must provide evidence that the order exists, the user is authorized, and the order is refundable.

In production systems, some of that evidence will be time-sensitive, so the type cannot replace transaction isolation or runtime checks. It can still prevent large classes of internal mistakes.

### 4. Workflow correctness

ERP systems contain many state machines:

```text
purchase request
→ approved
→ purchase order
→ received
→ invoiced
→ paid
```

A typed workflow engine can express legal transitions:

```text
approve : Request Pending → Approval → Request Approved
receive : PurchaseOrder Issued → Receipt → PurchaseOrder Received
pay     : Invoice ApprovedForPayment → Payment → Invoice Paid
```

Illegal transitions become unrepresentable.

This is one of the strongest realistic applications of advanced type systems to enterprise software.

### 5. Schema migration verification

Suppose version 1 stores:

```text
Customer {
  fullName : String
}
```

and version 2 stores:

```text
Customer {
  givenName : String
  familyName : String
}
```

A migration might be typed as:

```text
migrate : CustomerV1 → Result MigrationError CustomerV2
```

You can prove properties such as:

```text
customerId (migrate x) = customerId x
email (migrate x) = email x
```

For reversible migrations:

```text
backward (forward x) = x
```

This is particularly useful in financial, accounting, inventory, and regulated systems.

## What HoTT specifically could contribute

### Equivalent representations

Suppose two services represent the same business concept differently:

```text
ServiceA.Customer
ServiceB.Client
```

You establish an equivalence:

```text
customerEquiv : ServiceA.Customer ≃ ServiceB.Client
```

HoTT’s univalence says that an equivalence can be treated like equality. In principle, constructions indexed by one representation can be transported to the other automatically.

For example:

```text
Permissions ServiceA.Customer
```

could be transported to:

```text
Permissions ServiceB.Client
```

without manually proving that every downstream construction respects the conversion.

This is theoretically attractive for:

- API versioning;
- schema evolution;
- replacing implementations;
- normalizing representations across services;
- proving adapters preserve behavior.

But there is a major qualification: in ordinary application code, explicit conversion functions are usually easier to understand, debug, serialize, and operate.

### Quotients and canonical business identity

Business systems often have multiple records representing the same real-world entity:

```text
Customer record 182
Customer record 917
```

After deduplication, both may represent the same customer.

Mathematically, you want to quotient raw records by an equivalence relation:

```text
Customer = RawCustomer / SameRealWorldEntity
```

Higher inductive types can represent such quotient structures directly.

This could be useful for:

- customer deduplication;
- product identity across suppliers;
- equivalent SKUs;
- merged accounts;
- organizational hierarchies;
- entity resolution.

However, business equivalence is usually uncertain, reversible, historical, and audit-sensitive. It is rarely a clean mathematical equivalence relation. You usually need explicit evidence:

```text
MergeDecision {
  left
  right
  confidence
  decidedBy
  timestamp
  reversible
}
```

A plain quotient would erase information the business needs.

### Verified interchangeability of modules

Imagine replacing one pricing implementation with another:

```text
oldPricing : Cart → Price
newPricing : Cart → Price
```

You prove:

```text
∀ cart, oldPricing cart = newPricing cart
```

Then the implementations are behaviorally interchangeable.

HoTT gives a broad conceptual framework for treating equivalent structures as interchangeable. But ordinary equivalence proofs, functional extensionality, module refinement, or program verification are generally sufficient.

### Complex merge and synchronization models

Distributed ERP systems frequently reconcile data from multiple sources. Pushouts and related constructions from HoTT can model “combine two systems along their shared part”:

```text
SystemA ← SharedModel → SystemB
```

A pushout describes the unified model where matching shared entities are identified.

This is intellectually relevant to:

- data integration;
- ontology merging;
- multi-master synchronization;
- federated schemas;
- model transformation.

Yet directly implementing an ERP integration as a higher inductive type would be research-oriented. Production systems still need conflict policies, provenance, retries, authorization, timestamps, and audit trails.

## The practical ranking

For ordinary enterprise applications, the return on investment is roughly:

1. Strong ordinary types.
2. Explicit domain types instead of strings and integers.
3. State-machine modeling.
4. Property-based testing.
5. Database constraints.
6. Refinement types and SMT-backed verification.
7. Dependent types for critical components.
8. Proofs of migrations, accounting rules, and authorization.
9. HoTT or cubical type theory.

HoTT is usually near the bottom because it solves a deeper problem than most CRUD systems have.

## A realistic architecture

For an ecommerce or ERP platform, a practical verified core might contain:

```text
Money and currency arithmetic
tax calculations
discount composition
inventory conservation
ledger balancing
workflow transitions
authorization decisions
schema migrations
serialization round trips
```

The outer application would remain conventional:

```text
HTTP handlers
database access
queues
UI
logging
observability
third-party APIs
```

The verified core exposes functions like:

```text
calculateInvoice :
  ValidCart →
  TaxContext →
  ExchangeRates →
  ValidInvoice
```

with proved properties:

```text
invoiceTotal =
  subtotal
  + tax
  + shipping
  - discounts

inventoryAfter + purchasedQuantity =
  inventoryBefore

totalDebits = totalCredits
```

That delivers concrete business value. HoTT is not necessary for it.

## Bottom line

In CRUD and ERP systems, HoTT’s main potential contribution is **making equivalent schemas, models, or implementations formally interchangeable** and providing principled quotient or merge constructions.

In practice, the more valuable target is usually:

> a strongly typed domain engine with verified state transitions, money calculations, permissions, and migrations—not a full HoTT engine.

A custom proof/type engine for this space should probably combine dependent or refinement types with SMT solving, rather than begin with univalence and higher paths.


---

> Let us explore ontology merging, where modeling the domain mathematically to explore it is a phase in the design of a more traditional system and its types and its APIs . In the context of industrial / manufacturing ERP

I’ll frame ontology merging as a design-time discipline, then work through a concrete ERP–MES–PLM–maintenance merge and derive conventional types and APIs from it.

```json
{"system1_search_query":[{"q":"site:isa.org ISA-95 enterprise control system integration official"},{"q":"site:reference.opcfoundation.org ISA-95 OPC UA companion specification official"},{"q":"site:industrialdigitaltwin.org Asset Administration Shell specification official submodels"},{"q":"site:iso.org ISO 15926 industrial automation integration lifecycle data official"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 13 websites**

**Mapping ontology integration**

I’m developing a concrete manufacturing example using typed graphs, shared semantic interfaces, and controlled mappings. I’ll distinguish concepts that should remain separate, such as product definitions, revisions, instances, assets, lots, and operations.

**Mapped ontology integration**

**Structuring the integration**

I’m extending the example with schema versions, provenance, and a pump spanning design, procurement, production, and maintenance. I’ll connect formal ideas to practical adapters, validation scenarios, mapping evidence, and controlled evolution.

**Structured the integration**

</details>

```json
{"system1_search_query":[{"q":"site:iso.org ISO 10303-242 managed model based 3D engineering official"},{"q":"site:industrialdigitaltwin.org AAS semanticId concept description official specification"},{"q":"site:reference.opcfoundation.org ISA-95 material definition material lot equipment official"},{"q":"site:gs1.org EPCIS 2.0 standard manufacturing traceability official"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 10 websites**

</details>

The key distinction is already visible: a pump’s design revision, purchasable item, material definition, serialized unit, installed asset, and functional position must be related—not collapsed into one “asset” record.

```json
{"system1_search_query":[{"q":"Functorial Data Migration Spivak Wisnesky paper PDF"},{"q":"categorical databases schema integration colimit ontology merging paper"},{"q":"ologs ontology logs category theory Spivak Kent paper PDF"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 18 websites**

</details>

Yes. This is a stronger application of HoTT/category-theoretic ideas than using them directly inside a CRUD runtime.

The mathematical model becomes a **design laboratory**:

```text
domain observations
        ↓
local ontologies for PLM, ERP, MES, EAM, quality
        ↓
explicit semantic alignments
        ↓
merged model plus consistency obligations
        ↓
conventional domain types, schemas, APIs, events, and tests
```

The production system can remain TypeScript, Java, C#, SQL, Kafka, REST, and so on. The formal model clarifies what those components are allowed to mean.

## The central manufacturing problem

Consider one physical pump installed in a production line.

Different systems may describe it as:

| Context | Record | What it actually denotes |
|---|---|---|
| PLM | `PUMP-2000 Rev C` | An engineering design revision |
| ERP | `Item 4711` | A purchasable, stockable or manufacturable item definition |
| Supplier catalog | `ACME-X9` | A supplier’s commercial offering |
| Inventory | `Lot L-882` | A batch of physical material or units |
| Serialization | `Serial S-1044` | One physical manufactured unit |
| EAM/CMMS | `Asset E-90017` | A maintainable physical asset record |
| MES | `Equipment EQ-44` | A logical production resource |
| Plant model | `Coolant pump position CP-4` | A functional position in the plant |
| OPC UA/AAS | node or shell | A digital representation of some aspect of the asset |

These are related, but most are **not the same thing**.

ISA-95 itself makes several of these distinctions. It separates material classes, material definitions, material lots, logical equipment, and physical assets. In particular, logical equipment can remain stable while the physical device fulfilling that role is replaced. citeturn377484search2turn377484search18

That distinction is extremely important:

```text
functional position ≠ logical equipment ≠ physical unit ≠ asset record
```

A large canonical `Asset` table usually destroys these distinctions and then recovers them through flags, nullable columns, naming conventions, and undocumented business rules.

## Start with ontology strata

A useful industrial ontology can be organized into separate strata.

### Definitions and classifications

These describe kinds of things:

```text
MaterialClass
MaterialDefinition
PartDefinition
EquipmentClass
ProcessDefinition
SkillClass
QualityCharacteristic
UnitOfMeasure
```

### Versions and configurations

These describe controlled evolution:

```text
PartRevision
DocumentRevision
BOMRevision
RoutingRevision
SoftwareRevision
ApprovedConfiguration
EffectivityRule
```

### Physical instances

These describe things that exist physically:

```text
MaterialLot
MaterialSublot
SerializedUnit
PhysicalAsset
ToolInstance
Container
ProducedBatch
```

### Functional roles and positions

These describe what something does in a context:

```text
WorkCenter
EquipmentRole
FunctionalLocation
ProductionLinePosition
StorageLocation
InspectionStation
```

### Planned activity

```text
ProductionOrder
JobOrder
OperationRequirement
MaterialRequirement
EquipmentRequirement
MaintenancePlan
InspectionPlan
```

### Actual activity

```text
WorkExecution
MaterialConsumption
MaterialProduction
EquipmentUsage
InspectionExecution
DowntimeOccurrence
MaintenanceExecution
```

### Observations

```text
Measurement
Alarm
ConditionObservation
QualityResult
MachineState
EnergyReading
```

### Information representations

```text
ERPRecord
PLMRecord
MESRecord
AASShell
OPCUANode
ExternalIdentifier
Document
```

This last stratum matters because a record is not necessarily the domain object it describes.

```text
ERP record 4711 represents a material definition
```

is different from:

```text
ERP record 4711 is the material definition
```

That distinction gives you provenance and allows several systems to represent the same underlying concept without forcing them to share identifiers.

## A mathematical model

Represent each bounded context as its own ontology:

```text
P : PLM ontology
E : ERP ontology
M : MES ontology
A : asset-management ontology
Q : quality ontology
```

Each ontology contains:

- types or objects;
- relationships;
- composition rules;
- equations;
- constraints.

For example, the PLM ontology might contain:

```text
PartDefinition
PartRevision
AssemblyOccurrence

revisionOf :
  PartRevision → PartDefinition

childRevision :
  AssemblyOccurrence → PartRevision

parentRevision :
  AssemblyOccurrence → PartRevision
```

ERP might contain:

```text
Item
PlantItem
SupplierItem
InventoryLot

plantItemOf :
  PlantItem → Item

lotOf :
  InventoryLot → PlantItem
```

MES might contain:

```text
MaterialDefinition
MaterialLot
JobOrder
MaterialActual

lotDefinition :
  MaterialLot → MaterialDefinition

usedIn :
  MaterialActual → JobOrder
```

This resembles an **olog** or categorical database schema: concepts are objects, meaningful mappings are arrows, and equations state when two paths must have the same meaning. Ologs were specifically proposed as a rigorous knowledge-representation framework that can connect local worldviews through functors. citeturn625488search2

## Merge through shared interfaces

Do not immediately merge the full ontologies. First define a small shared semantic interface:

```text
K:
  ProductDefinition
  ProductRevision
  MaterialKind
  PhysicalUnit
  Batch
  FunctionalPosition
  ProcessDefinition
  ProcessExecution
  TimeInterval
  Quantity
```

Then define mappings into the local ontologies:

```text
          PLM
         ↗
Shared K
         ↘
          ERP
```

Mathematically:

```text
K ──f──▶ PLM
│
g
│
▼
ERP
```

The pushout

```text
PLM ⊔ₖ ERP
```

is the ontology formed by gluing PLM and ERP along the concepts and relationships explicitly identified through `K`.

You can then merge MES and EAM similarly.

The useful property is that the merge is defined by **declared correspondences**, rather than by string similarity or table-name matching.

For instance:

```text
K.ProductRevision
    ↦ PLM.PartRevision

K.ProductDefinition
    ↦ ERP.Item

K.PhysicalUnit
    ↦ EAM.PhysicalAsset

K.FunctionalPosition
    ↦ MES.Equipment
```

These mappings expose an immediate issue: perhaps `MES.Equipment` denotes a logical resource in one implementation but a physical machine in another. The mapping cannot be accepted until that ambiguity is resolved.

That is exactly the sort of design failure the mathematical phase should find.

## Do not make every correspondence equality

Ontology merging requires an explicit vocabulary of correspondence kinds.

A practical relation hierarchy is:

```text
SameEntity
EquivalentRepresentation
Classifies
Instantiates
Realizes
ConformsTo
Commercializes
ManufacturedAccordingTo
InstalledAt
PlaysRole
ComposedOf
DerivedFrom
Supersedes
Replaces
PotentialMatch
```

For the pump:

```text
ERP.Item 4711
  realizes
PLM.PartRevision PUMP-2000/C
```

or perhaps:

```text
ERP.Item 4711
  commercializes
PLM.PartDefinition PUMP-2000
```

The exact relation depends on company policy. It probably should not be strict equality.

Similarly:

```text
Serial S-1044
  conformsTo
PartRevision PUMP-2000/C

Serial S-1044
  representedBy
EAM Asset E-90017

Serial S-1044
  installedAt
FunctionalPosition CP-4
  during [2025-03-12, 2026-01-17)

Serial S-2088
  installedAt
FunctionalPosition CP-4
  during [2026-01-17, ...)
```

The functional position persisted while the physical pump changed.

## Where the HoTT perspective helps

### Identifications become explicit paths

Instead of assigning one global identifier, retain local entities and add a path or witness connecting them:

```text
erp4711 ──alignment──▶ plmPump2000C
```

Multiple alignments can coexist because they may have:

- different sources;
- different validity periods;
- different assumptions;
- different transformation rules;
- different approval states.

In a business system, this should usually be represented as structured evidence rather than erased equality:

```lean
structure Alignment (A B : Type) where
  left        : A
  right       : B
  relation    : RelationKind
  validDuring : TimeInterval
  authority   : Authority
  evidence    : Evidence
  confidence  : Confidence
```

This is HoTT-inspired but intentionally more operational than a bare path.

### Different mapping routes must agree

Suppose you have:

```text
ERP Item
  → PLM PartRevision
  → MES MaterialDefinition
```

and also a direct mapping:

```text
ERP Item
  → MES MaterialDefinition
```

You want a coherence condition:

```text
erpToMes
    =
plmToMes ∘ erpToPlm
```

In conventional category theory this is a commuting triangle. In HoTT language, it is a path between two paths.

This is highly practical. It detects situations such as:

- the ERP–MES interface says item `4711` maps to MES material `M-82`;
- the ERP–PLM mapping says it corresponds to revision C;
- the PLM–MES mapping says revision C corresponds to `M-91`.

The system has three individually plausible mappings but no coherent global meaning.

You can turn the coherence condition into:

- a formal theorem;
- an integration test;
- a data-quality query;
- a CI failure;
- a reconciliation report.

### Equivalent schemas can be compared structurally

Suppose two plants model routings differently:

```text
Plant A:
  Routing → ordered list of Operations

Plant B:
  ProcessPlan → graph of ProcessSteps
```

The models may be equivalent only under conditions such as:

- the graph is acyclic;
- each step has one successor;
- there are no parallel branches.

An equivalence should contain:

```text
forward transformation
backward transformation
forward-after-backward law
backward-after-forward law
scope conditions
```

HoTT packages this as equivalence rather than merely “we wrote two mapping scripts.”

The production implementation can expose explicit adapters, while generated tests verify the round-trip laws.

## A concrete semantic core

A useful first model might contain these types:

```lean
inductive DomainType
  | productDefinition
  | productRevision
  | commercialItem
  | materialDefinition
  | materialLot
  | physicalUnit
  | maintainableAsset
  | functionalPosition
  | equipmentRole
  | processDefinition
  | jobOrder
  | workExecution
  | observation
```

Then use evidence-bearing relationships:

```lean
ConformsTo :
  PhysicalUnit → ProductRevision → Type

ClassifiedAs :
  MaterialLot → MaterialDefinition → Type

InstalledAt :
  PhysicalUnit → FunctionalPosition → TimeInterval → Type

PlaysRole :
  PhysicalUnit → EquipmentRole → TimeInterval → Type

ConsumedIn :
  MaterialLot → WorkExecution → Quantity → Type

Represents :
  SystemRecord → DomainEntity → TimeInterval → Type

Supersedes :
  ProductRevision → ProductRevision → Type
```

Using `Type` rather than Boolean values allows the witness to carry:

```text
source document
approval
measurement
mapping rule
effective date
author
confidence
```

This produces an **explainable ontology merge**. Every cross-system assertion can answer “why do we believe this?”

## Deriving conventional application types

The mathematical model should prevent the traditional implementation from creating this:

```typescript
type EntityId = string;
```

Instead, derive distinct branded identifiers:

```typescript
type PartRevisionId = Brand<string, "PartRevisionId">;
type ItemId = Brand<string, "ItemId">;
type MaterialDefinitionId = Brand<string, "MaterialDefinitionId">;
type LotId = Brand<string, "LotId">;
type SerialId = Brand<string, "SerialId">;
type AssetId = Brand<string, "AssetId">;
type FunctionalPositionId = Brand<string, "FunctionalPositionId">;
```

Then model cross-context claims explicitly:

```typescript
type EntityRef = {
  system: "PLM" | "ERP" | "MES" | "EAM" | "QMS";
  concept: string;
  localId: string;
  revision?: string;
};

type AlignmentClaim = {
  left: EntityRef;
  right: EntityRef;
  relation:
    | "SAME_ENTITY"
    | "EQUIVALENT_REPRESENTATION"
    | "REALIZES"
    | "CONFORMS_TO"
    | "CLASSIFIES"
    | "INSTALLED_AT"
    | "SUPERSEDES"
    | "POTENTIAL_MATCH";
  validTime: TimeInterval;
  recordedAt: string;
  evidence: EvidenceRef[];
  status: "PROPOSED" | "APPROVED" | "REJECTED" | "SUPERSEDED";
};
```

This is a direct compilation of the ontology’s identity discipline into an ordinary data model.

## APIs derived from competency questions

Do not begin with entity CRUD endpoints. Begin with questions that operations, engineering, quality, and maintenance need answered.

Examples:

```text
Which engineering revision was this serial number built to?

Which actual lots were consumed while producing this serialized unit?

Which approved substitute materials could satisfy this job order?

Which physical device occupied this functional position at alarm time?

Does the as-maintained configuration still conform to an approved
engineering configuration?

Which measurements support the claim that this unit passed inspection?

Why does the ERP item map to this MES material definition?
```

These produce domain APIs such as:

```text
getAsBuiltConfiguration(serialId, atTime)

traceConsumedLots(serialId)

findApprovedSubstitutions(materialRequirement, plant, atTime)

resolveInstalledAsset(functionalPositionId, atTime)

compareAsBuiltToAsMaintained(serialId, atTime)

explainAlignment(leftRef, rightRef)
```

That is substantially more useful than:

```text
GET /assets/{id}
PUT /assets/{id}
```

## Invariants produced by the model

The ontology should generate a catalog of invariants.

For example:

```text
A material lot cannot be both a material definition and an instance
of that definition.

A physical unit can conform to a revision without being identical
to that revision.

A functional position can persist when its installed physical unit changes.

Every consumed material actual must satisfy some job-order material
requirement.

Every produced serialized unit must have an as-built configuration.

Every approved ERP–MES mapping must be coherent with approved
ERP–PLM and PLM–MES mappings, where all three exist.

Quantity conversions must preserve physical dimensions.

Revision substitutions must be valid during the job order's effectivity
interval.

Mappings used for regulated records must retain provenance.
```

These can be compiled into different enforcement mechanisms:

| Formal statement | Production mechanism |
|---|---|
| Local uniqueness | database constraint |
| State transition law | domain-service validation |
| Mapping coherence | CI integration test |
| Temporal non-overlap | exclusion constraint or validator |
| Unit compatibility | typed quantity library |
| Round-trip equivalence | property-based test |
| Provenance required | API/schema requirement |
| Cross-system consistency | reconciliation job |

## Relevant industrial standards as source ontologies

The standards should be treated as reusable source models, not as one universal truth.

- **ISA-95 / IEC 62264** is useful for ERP–MES boundaries, production resources, materials, personnel, equipment, physical assets, job orders, and actuals. citeturn617853search1turn377484search22
- **STEP AP242** is useful for product definitions, assemblies, engineering structures, tools, raw materials, and product-data management. citeturn377484search0
- **Asset Administration Shell** supplies a standardized digital-twin metamodel, APIs, and domain-specific submodels. citeturn617853search18turn617853search25
- **ISO 15926** is particularly relevant for process-plant lifecycle information and reference data. citeturn617853search7turn617853search27
- **GS1 EPCIS** supplies an event-oriented vocabulary for traceability and supply-chain visibility. citeturn377484search3turn377484search7

A company ontology would align selected fragments of these standards with its local models. It should not import every concept from every standard.

## Category theory is probably more immediately useful than full HoTT

For this problem, the most direct mathematical tools are:

```text
categories       schemas or ontologies
functors         semantic mappings
natural transformations
                 comparison between mappings
limits           synchronized compatible views
colimits         merged schemas
commuting diagrams
                 integration consistency laws
set-valued functors
                 actual database instances
```

Categorical database research models a schema as a category and a database instance as a set-valued functor. Schema mappings then induce structured data migrations. This has been demonstrated in a manufacturing supply-chain integration scenario. citeturn625488academia27turn625488academia26

HoTT adds the richer interpretation:

```text
mapping equality       path between mappings
mapping coherence      higher path
schema equivalence     identity-like substitutability
ontology pushout       higher inductive gluing
```

For an initial implementation, ordinary Lean 4 is enough to:

- define the domain concepts;
- encode local ontologies;
- define mappings;
- state commuting-diagram laws;
- prove transformation properties;
- generate fixtures or validation rules.

You would not need to implement a HoTT kernel first.

## A sensible first case study

The most productive first slice is **product definition to as-built and as-maintained configuration**:

```text
PLM engineering BOM
        ↓
ERP item and manufacturing BOM
        ↓
MES material requirements and actual consumption
        ↓
serialized as-built unit
        ↓
EAM installed and replaced components
```

The target questions would be:

```text
What was designed?
What was planned?
What was actually built?
What is currently installed?
What changed?
Under which approved equivalences or substitutions?
What evidence supports each answer?
```

That slice exercises ontology merging, identity, revisioning, temporal validity, provenance, quantities, substitutions, traceability, and route coherence without attempting to model the whole enterprise at once.


---

> I do actually care a lot about the hott part. Let’s write a textbook about «  theory of erp system ontologies », with a first part grounded in lean4 and category theory, a second part on lean4 and giving more into dependent type theory, and a third part that brings it all together by tackling it with homotopy type theory as the core organizing structure.
>
> Output as markdown and pdf

```unknown
bash -lc cat /home/oai/skills/pdfs/SKILL.md
```

I’ll build a self-contained three-part textbook with ERP case studies, Lean 4 examples, diagrams, exercises, glossary, citations, and bibliography, delivered as matching Markdown and navigable PDF editions.

<details><summary>💭 Thinking</summary>

**Read PDF creation and conversion skills**

**Scoping textbook project**

I’m interpreting the request as a substantial textbook manuscript in Markdown, with a corresponding PDF and Lean 4 examples. I’m first deciding the scope, structure, and how carefully to verify the code.

**Scoped the textbook project**

**Structuring formal core**

I’m planning a compact but substantial textbook: a Lean 4 formal core for syntax, contexts, types, terms, and categorical ontology merges, paired with manufacturing and aerospace case studies.

**Structured formal core**

**Designing textbook structure**

I’m organizing the book into three parts: categorical ontology foundations, dependent types in Lean 4, and HoTT-inspired integration. A fictional industrial case study will connect diagrams, proofs, workflows, and digital-thread models.

**Designed textbook structure**

</details>

```json
{"search_query":[{"q":"site:lean-lang.org documentation Lean 4 reference manual latest 2026"},{"q":"site:github.com/leanprover/lean4 releases latest Lean 4"},{"q":"site:leanprover-community.github.io/mathlib4_docs CategoryTheory mathlib Lean 4"},{"q":"site:homotopytypetheory.org book homotopy type theory univalent foundations PDF"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 10 websites**

**Building deliverables**

I’m now moving from planning to production: drafting the manuscript, embedding self-contained diagrams and Lean examples, then converting the Markdown into a polished PDF while checking consistency and usability.

**Built deliverables**

</details>

```unknown
bash -lc which lean || true; lean --version 2>/dev/null || true; which lake || true; which pandoc; pandoc --version | head -2; which xelatex; xelatex --version | head -1; fc-list | grep -i 'Libertinus Serif' | head
```

<details><summary>💭 Thinking</summary>

**Checked Lean and document tool availability**

</details>

```json
{"search_query":[{"q":"site:github.com/leanprover/lean4/releases/tag/v4.32.2 lean 4.32.2 assets linux"},{"q":"site:lean-lang.org/doc/reference/latest/releases/v4.32.2 Lean 4.32.2"},{"q":"site:github.com/leanprover/elan releases latest elan linux"}],"response_length":"long"}
```

A continuous manufacturing case study will progress from categorical local ontologies through dependent types to homotopy pushouts and controlled truncation. Lean remains the meta-language, while workflows retain directed structure.

<details><summary>💭 Thinking</summary>

**Searched 2 websites**

</details>

```unknown
bash -lc mkdir -p /mnt/data/erp_ontology_book_work && fc-list | grep -Ei 'TeX Gyre Pagella|Libertinus|DejaVu Sans Mono|Latin Modern Roman' | head -20
```

<details><summary>💭 Thinking</summary>

**Checked available fonts and LaTeX font packages**

</details>

```unknown
bash -lc cat > /mnt/data/erp_ontology_book_work/theory_of_erp_system_ontologies.md <<'EOF'
---
title: "Theory of ERP System Ontologies"
subtitle: "Category Theory, Dependent Types, and Homotopy Type Theory for Industrial Systems"
author: "First-edition working manuscript"
date: "August 2026"
lang: en-US
documentclass: book
classoption:
  - 10pt
  - openany
geometry:
  - inner=0.9in
  - outer=0.75in
  - top=0.8in
  - bottom=0.85in
toc: true
toc-depth: 3
numbersections: true
colorlinks: true
linkcolor: MidnightBlue
urlcolor: MidnightBlue
mainfont: "DejaVu Serif"
sansfont: "DejaVu Sans"
monofont: "DejaVu Sans Mono"
monofontoptions:
  - Scale=0.82
header-includes:
  - |
    \usepackage{microtype}
    \usepackage{booktabs}
    \usepackage{longtable}
    \usepackage{array}
    \usepackage{fvextra}
    \usepackage{xcolor}
    \usepackage{fancyhdr}
    \usepackage{enumitem}
    \usepackage{amsthm}
    \usepackage{mathtools}
    \usepackage{amssymb}
    \usepackage{upquote}
    \definecolor{BookBlue}{HTML}{17365D}
    \definecolor{BookGray}{HTML}{F3F5F7}
    \fvset{breaklines=true,breakanywhere=true,fontsize=\small}
    \setlist{nosep}
    \pagestyle{fancy}
    \fancyhf{}
    \fancyhead[LE,RO]{\small\thepage}
    \fancyhead[LO]{\small\nouppercase{\rightmark}}
    \fancyhead[RE]{\small\nouppercase{\leftmark}}
    \renewcommand{\headrulewidth}{0.3pt}
    \newtheorem{definition}{Definition}[chapter]
    \newtheorem{proposition}[definition]{Proposition}
    \newtheorem{theorem}[definition]{Theorem}
    \newtheorem{principle}[definition]{Design Principle}
    \newtheorem{warning}[definition]{Warning}
---

# Preface {-}

Enterprise resource planning systems are often described as databases surrounded by workflows. That description is operationally useful but mathematically shallow. An industrial enterprise does not merely store rows. It maintains many overlapping theories of products, materials, processes, equipment, organizations, obligations, measurements, and time. Product lifecycle management, ERP, manufacturing execution, quality management, warehouse management, maintenance, supplier portals, and industrial control systems each encode a different theory of the same plant.

The hard integration failures are therefore semantic failures. A part revision is confused with a stock item. A functional position is confused with the physical asset installed there. A material definition is confused with a lot. A planned operation is confused with an execution. A record identifier is confused with the entity represented by the record. Two mappings are locally plausible but disagree when composed around a larger integration diagram.

This book develops a mathematical theory for those situations. It has three parts.

**Part I** treats an ERP landscape as a family of categories. Local ontologies are typed schemas with equations. Instances are functors. Cross-system mappings are functors. Changes of data are natural transformations. Merges are colimits, especially pushouts. This gives a precise language for the directed, compositional structure of industrial information.

**Part II** moves from external categorical models into dependent type theory and Lean 4. Business invariants become types. Valid workflows become indexed families. Quantities carry dimensions. Migrations carry proofs. Alignments carry evidence. The result is not a proposal to implement an entire ERP in a theorem prover. It is a method for designing a small verified semantic core whose consequences are exported to conventional APIs, events, database constraints, and tests.

**Part III** takes homotopy type theory seriously as an organizing structure. Ontology integration contains not only arrows but identifications, multiple witnesses of identification, and coherence between routes of identification. HoTT turns identity into a structured type of paths, equivalence into a source of identity through univalence, and ontology gluing into higher inductive constructions. Univalent categories explain how isomorphic concepts can become genuinely substitutable. Truncation explains how a rich higher semantic model can be compiled down to ordinary records without pretending that the higher structure never existed.

There is an important technical qualification. Standard Lean 4 is not a native HoTT kernel. Its `Prop` universe is proof-irrelevant, and its built-in equality is not the higher path type used by HoTT. In Part III, Lean 4 is used in two controlled ways:

1. as a metaprogramming language in which we specify an object-level HoTT calculus; and
2. as a host for axiomatic interfaces whose path type lives in `Type`, separate from `Lean.Eq`.

This distinction is maintained throughout. The book does not claim that changing notation turns ordinary Lean equality into homotopical equality.

The intended result is a theory of ontology engineering that can guide ordinary implementation. The production system may still be written in Java, C#, Kotlin, Rust, TypeScript, SQL, or a data-platform language. The mathematical phase exists to discover distinctions, invariants, equivalences, and coherence obligations before they are buried in schemas and integration code.

## Intended audience {-}

The primary audience includes enterprise architects, industrial data modelers, PLM/ERP/MES integration engineers, formal methods practitioners, and researchers in applied category theory or type theory. The reader should be comfortable with typed programming and ordinary relational data modeling. No prior category theory or HoTT is assumed, although mathematical maturity is required.

A reader focused on architecture may read Chapters 1-7, 14-15, and 24-25 first. A Lean practitioner may begin with Chapter 8. A type theorist may skim the industrial preliminaries but should not skip Chapter 6, where the identity problems are stated in domain terms.

## The running case: Asterion Drives {-}

The running example is a fictional manufacturer, Asterion Drives, which designs and manufactures configurable industrial pump and motor assemblies. It operates five plants and uses the following systems:

- a PLM system for product definitions, engineering revisions, documents, and engineering bills of material;
- an ERP system for commercial items, plant-specific planning data, procurement, production orders, inventory, and accounting;
- an MES for work schedules, job orders, material actuals, equipment actuals, genealogy, and production events;
- a QMS for inspection plans, characteristics, nonconformances, and release decisions;
- an EAM system for functional locations, assets, maintenance plans, work orders, and replacement history;
- supplier and logistics systems that exchange product, shipment, and traceability events.

Asterion's recurring question is:

> For a serialized pump operating at a customer site, what was designed, what was ordered, what was built, what was inspected, what is currently installed, and what evidence justifies every cross-system identification used in the answer?

Every major construction in the book contributes to answering this question.

## Conventions {-}

The book uses `Type` for information that may carry computationally or semantically relevant witnesses and `Prop` for proof-irrelevant assertions in ordinary Lean developments. In the HoTT part, mere propositions and sets are defined by truncation level rather than identified with Lean's `Prop`.

A phrase such as "same entity" is never accepted without a declared criterion of sameness. The book distinguishes at least the following:

- strict record identity;
- identity of a represented domain entity;
- isomorphism or equivalence of representations;
- classification or conformance;
- realization of a design by a physical unit;
- occupancy of a functional role during a time interval;
- a provisional matching claim supported by evidence.

These relations have different algebraic properties. Most are not equality.

## Status of code {-}

The ordinary Lean examples target Lean 4.32.2 syntax and a contemporaneous mathlib snapshot. This version is chosen because it was the current stable release on August 5, 2026, and it includes a kernel soundness correction released on July 28, 2026. Most examples use only core Lean features. Blocks importing `Mathlib.CategoryTheory` rely on mathlib. Blocks marked `-- schematic` emphasize a design and may require supporting definitions from earlier chapters.

The Part III interface is intentionally axiomatic. It illustrates the signature that a HoTT-aware ontology kernel should expose; it does not make Lean's kernel compute univalence or higher inductive types.

# Part I - Categorical Foundations for ERP Ontologies

# The Enterprise as a Family of Theories

## From tables to claims

An ERP landscape is not a single database distributed across products. It is a federation of local theories. Each system makes claims of a particular form and is authoritative only for some of them.

The PLM system can assert that revision `PD-2000/C` has an approved engineering bill of material. The ERP system can assert that item `4711` is planned as a manufactured item at plant `DE01`. The MES can assert that lot `L-882` was consumed by execution `EX-9003`. The EAM can assert that serialized unit `S-1044` occupied functional position `FP-CP-4` during a specified interval. These claims are related, but they do not belong to one undifferentiated type called `Entity`.

A useful first discipline is to separate five layers:

| Layer | Typical inhabitants | Central question |
|---|---|---|
| Definition | product definition, material definition, equipment class | What kind of thing is specified? |
| Version | product revision, BOM revision, routing revision | Which controlled state of a definition applies? |
| Physical instance | lot, serial, physical asset, container | Which concrete thing existed? |
| Role or position | work center, functional location, equipment role | What function was to be fulfilled? |
| Record or representation | PLM record, ERP item row, AAS shell, OPC UA node | Which information object represents something else? |

Many failed canonical models collapse two or more layers. The resulting table acquires a `type` discriminator, dozens of nullable foreign keys, and business rules that are impossible to state locally.

## Local ontologies

A **local ontology** is the formal vocabulary and law set of a bounded context. It includes:

1. entity and value types;
2. typed relationships;
3. composition rules;
4. path equations or invariants;
5. admissible instances;
6. an account of identity and representation.

For example, a small PLM ontology may include types

\[
\mathsf{ProductDefinition},\quad
\mathsf{ProductRevision},\quad
\mathsf{Occurrence},\quad
\mathsf{DocumentRevision}
\]

and functions

\[
\begin{aligned}
\mathsf{revisionOf} &: \mathsf{ProductRevision} \to \mathsf{ProductDefinition},\\
\mathsf{parent} &: \mathsf{Occurrence} \to \mathsf{ProductRevision},\\
\mathsf{child} &: \mathsf{Occurrence} \to \mathsf{ProductRevision},\\
\mathsf{specifiedBy} &: \mathsf{Occurrence} \to \mathsf{DocumentRevision}.
\end{aligned}
\]

An ERP ontology may instead include `Item`, `PlantItem`, `ProductionOrder`, and `MaterialReservation`. An MES ontology distinguishes `MaterialDefinition`, `MaterialLot`, `JobOrder`, and `MaterialActual`. The names may overlap while the meanings do not.

## Reference is not identity

A system record is an information object. A domain entity is what the record is about. The distinction can be made explicit:

```lean
inductive System
  | plm | erp | mes | qms | eam
  deriving DecidableEq, Repr

structure LocalRef where
  system   : System
  concept  : String
  localId  : String
  revision : Option String := none
  deriving DecidableEq, Repr

inductive DomainKind
  | productDefinition
  | productRevision
  | commercialItem
  | materialDefinition
  | materialLot
  | serializedUnit
  | physicalAsset
  | functionalPosition
  deriving DecidableEq, Repr

structure RepresentationClaim where
  recordRef : LocalRef
  kind      : DomainKind
  validFrom : Nat
  validTo   : Option Nat
  source    : String
```

This code is modest, but it blocks a pervasive category mistake: a `LocalRef` is not itself a product revision, lot, asset, or position. A reference can be stale, duplicated, merged, or reassigned. The represented domain entity has a different identity criterion.

## Competency questions before schemas

Ontology design should begin with **competency questions**, not entity lists. A competency question is a query the model must support with a defensible meaning. For Asterion:

1. Which engineering revision governed serial `S-1044` at release time?
2. Which lots and sublots were consumed in its production?
3. Which approved substitutions were used, and under what effectivity rule?
4. Which physical asset occupied functional position `FP-CP-4` at the time of alarm `AL-71`?
5. Does the as-maintained configuration conform to an approved engineering baseline?
6. Why does ERP item `4711` map to MES material definition `M-82`?
7. Do the direct ERP-to-MES mapping and the route through PLM agree?

These questions expose distinctions that CRUD endpoint design tends to hide. Question 4 forces time-indexed occupancy. Question 6 forces evidence-bearing alignment. Question 7 forces coherence between mappings.

## A first formal boundary

A useful semantic core can distinguish local references, domain entities, and claims:

```lean
abbrev EntityId := Nat

structure DomainEntity where
  id   : EntityId
  kind : DomainKind
  deriving DecidableEq, Repr

inductive RelationKind
  | sameEntity
  | equivalentRepresentation
  | classifies
  | conformsTo
  | realizes
  | installedAt
  | supersedes
  | potentialMatch
  deriving DecidableEq, Repr

structure AlignmentClaim where
  left       : LocalRef
  right      : LocalRef
  relation   : RelationKind
  evidence   : List String
  approvedBy : Option String
  validFrom  : Nat
  validTo    : Option Nat
```

The `relation` field is not cosmetic. It is the beginning of an algebra. `sameEntity` should be symmetric and transitive only under carefully stated temporal and scope conditions. `conformsTo` need not be symmetric. `supersedes` is directed and usually irreflexive. `potentialMatch` is epistemic and should not silently participate in substitution.

## Semantic authority

A local system is authoritative for claim types, not necessarily for entities. PLM may be authoritative for release status of a product revision. ERP may be authoritative for current inventory quantity. MES may be authoritative for material consumption actuals. EAM may be authoritative for asset installation intervals. None is globally authoritative for the pump as a whole.

This suggests a typed authority relation:

\[
\mathsf{AuthoritativeFor}(s,c,p,t)
\]

where system `s` is authoritative for claim class `c`, under plant or organizational scope `p`, during time interval `t`. Authority is itself versioned data and should be represented explicitly when integration decisions depend on it.

## Design consequences

A theory-first approach produces concrete implementation consequences:

- Separate identifiers for definitions, revisions, physical instances, roles, and records.
- Store cross-system correspondences as claims with relation kind, scope, time, status, and evidence.
- Make mapping routes explicit enough to test their coherence.
- Keep local ontologies intact instead of flattening them prematurely.
- Derive APIs from competency questions and invariants rather than from tables alone.

## Exercises

1. In a manufacturing organization familiar to you, list three concepts that are currently overloaded under one word such as "asset", "material", or "order". Separate their identity criteria.
2. For a supplier part number and an internal ERP item, classify at least four possible relationships between them. State which are symmetric.
3. Extend `AlignmentClaim` with transaction time and valid time. Explain why both are required for audit.
4. Write five competency questions for an engineering change that affects open production orders and installed assets.
5. Give an example in which two records have the same local identifier string but cannot denote the same domain entity.

# Typed Graphs, Categories, and Ologs

## Why categories appear

A typed graph contains objects and arrows. An ERP ontology already has this shape:

```text
ProductRevision --revisionOf--> ProductDefinition
       |
       +--hasOccurrence--> Occurrence --child--> ProductRevision

ProductionOrder --forItem--> PlantItem --itemOf--> Item

MaterialActual --lot--> MaterialLot --definition--> MaterialDefinition
```

A category adds two requirements:

1. arrows compose; and
2. every object has an identity arrow.

It also imposes associativity and identity laws. These requirements seem abstract, but they express a basic integration need: a chain of well-typed semantic references should itself have a stable meaning, independent of how the chain is parenthesized.

If

\[
\mathsf{lotDefinition} : \mathsf{MaterialLot} \to \mathsf{MaterialDefinition}
\]

and

\[
\mathsf{erpItem} : \mathsf{MaterialDefinition} \to \mathsf{Item},
\]

then their composite assigns an ERP item to every material lot. A path equation can require that this composite agrees with a direct `lotItem` relationship.

## Categories as presented schemas

A practical ontology category is often specified by:

- a finite set of object symbols;
- a finite set of generating arrows;
- equations between paths.

The category is then the free category on the graph, quotiented by the declared path equations. In database language, the objects resemble tables or entity types, generating arrows resemble total foreign keys, and equations resemble integrity constraints on foreign-key paths.

Consider a plant-item schema:

```text
PlantItem --itemOf--> Item
PlantItem --plantOf--> Plant
Reservation --plantItem--> PlantItem
Reservation --order--> ProductionOrder
ProductionOrder --plant--> Plant
```

A path equation can require:

\[
\mathsf{plantOf} \circ \mathsf{plantItem}
=
\mathsf{plant} \circ \mathsf{order}.
\]

Every reservation then refers to a plant item belonging to the same plant as its production order. This is not merely documentation. It is a global invariant of every valid instance of the schema.

## A pedagogical category in Lean

Mathlib contains an extensive category theory library. Before using it, it is useful to see the underlying record directly.

```lean
universe u v

structure SmallCategory where
  Obj  : Type u
  Hom  : Obj → Obj → Type v
  id   : {X : Obj} → Hom X X
  comp : {X Y Z : Obj} → Hom X Y → Hom Y Z → Hom X Z
  id_comp  : ∀ {X Y} (f : Hom X Y), comp id f = f
  comp_id  : ∀ {X Y} (f : Hom X Y), comp f id = f
  assoc    : ∀ {W X Y Z}
    (f : Hom W X) (g : Hom X Y) (h : Hom Y Z),
    comp (comp f g) h = comp f (comp g h)
```

The order chosen for `comp` here is diagrammatic: `comp f g` means first `f`, then `g`. Mathlib uses conventional notation and supplies substantial infrastructure. The pedagogical structure is useful because every field has an immediate enterprise interpretation.

- `Obj` is the type of concept symbols.
- `Hom A B` is the type of semantic transformations from concept `A` to concept `B`.
- `id` means a concept can be viewed as itself.
- `comp` gives meaning to a chain of references.
- the laws make reference chains stable.

## Ologs

An ontology log, or olog, is a category presented using controlled natural-language labels. Objects are labeled by singular indefinite noun phrases such as "a serialized pump" or "a released product revision". Arrows are labeled by functional verb phrases such as "was manufactured according to".

For example:

```text
[a serialized pump]
    --was manufactured according to-->
[a released product revision]
    --is a revision of-->
[a product definition]
```

The linguistic discipline matters. The arrow phrase must denote a function in the modeled context. "uses" is often not functional: a work execution can use many lots. One must replace it with an object representing a usage occurrence:

```text
[a material actual] --refers to--> [a material lot]
[a material actual] --belongs to--> [a work execution]
```

This reification is not bureaucratic modeling. It makes quantity, time, role, and provenance attach to the correct event.

## Functional arrows and relations

Ordinary categories model functional arrows. Industrial ontologies also contain relations. There are three common strategies:

1. **Reify the relation** as an event or association object, as with `MaterialActual`.
2. Use a category of relations rather than functions.
3. Treat a relation as a predicate-valued or type-valued profunctor.

The first strategy is usually clearest for ERP design because relational occurrences often have their own attributes. A substitution approval is not a Boolean edge between two materials; it has plant scope, effectivity, approving authority, quantity constraints, and documents.

## Paths as derived semantics

In a category, a path of arrows is itself an arrow. This turns local declarations into derived queries. From

\[
\mathsf{consumedLot} : \mathsf{MaterialActual} \to \mathsf{MaterialLot}
\]

and

\[
\mathsf{definition} : \mathsf{MaterialLot} \to \mathsf{MaterialDefinition},
\]

we obtain

\[
\mathsf{consumedDefinition}
=
\mathsf{definition} \circ \mathsf{consumedLot}.
\]

From `MaterialActual -> WorkExecution -> JobOrder -> ProductionOrder`, we obtain a trace from actual consumption to the enterprise order that motivated it. The category records this derivation without adding another primitive field.

## Path equations as semantic tests

Suppose MES offers a direct function

\[
\mathsf{productionOrderOfActual} : \mathsf{MaterialActual} \to \mathsf{ProductionOrder}
\]

while the ontology also supplies a route through work execution and job order. The equation

\[
\mathsf{productionOrderOfActual}
=
\mathsf{orderOfJob} \circ
\mathsf{jobOfExecution} \circ
\mathsf{executionOfActual}
\]

is a commuting diagram. At the data level it becomes a reconciliation query. At the API level it becomes a property test. At the formal level it is part of the schema theory.

This translation from equation to operational control is one of the main benefits of categorical modeling.

## Using mathlib

In mathlib, categories, functors, natural transformations, limits, and colimits live under `Mathlib.CategoryTheory`. A minimal import is commonly:

```lean
import Mathlib.CategoryTheory.Category.Basic
import Mathlib.CategoryTheory.Functor.Basic

open CategoryTheory

universe v u

variable (C : Type u) [Category.{v} C]

#check CategoryStruct.Hom
#check Functor
```

For a textbook-scale ontology, it is often simpler to define a finite presented schema in a domain-specific layer and interpret it into mathlib categories. Mathlib is strongest for proving general categorical results; the domain layer is strongest for readable generators, equations, diagnostics, and code generation.

## A finite ERP concept vocabulary

A direct Lean enumeration is useful for tooling:

```lean
inductive Concept
  | productDefinition
  | productRevision
  | item
  | plantItem
  | materialDefinition
  | materialLot
  | serializedUnit
  | productionOrder
  | jobOrder
  | workExecution
  | materialActual
  | functionalPosition
  | physicalAsset
  deriving DecidableEq, Repr
```

One can represent generating arrows as dependent data:

```lean
inductive Gen : Concept → Concept → Type
  | revisionOf : Gen .productRevision .productDefinition
  | itemOf : Gen .plantItem .item
  | lotDefinition : Gen .materialLot .materialDefinition
  | jobProductionOrder : Gen .jobOrder .productionOrder
  | executionJob : Gen .workExecution .jobOrder
  | actualExecution : Gen .materialActual .workExecution
  | actualLot : Gen .materialActual .materialLot
  | installedAsset : Gen .functionalPosition .physicalAsset
```

The free category generated by `Gen` contains identities and arbitrary composable paths. Path equations can then be represented as pairs of parallel paths. This provides a concrete route to an ontology compiler.

## What category theory does not decide

Category theory checks compositional form, not domain truth. It cannot decide whether ERP `Item` should align to PLM `ProductDefinition` or `ProductRevision`. That is an engineering judgment. What category theory does is force the judgment to be explicit and expose its consequences.

It also does not make every relationship invertible. `revisionOf`, `consumedIn`, and `supersedes` are directed. Treating them as identities would erase meaning. The later HoTT layer applies to identifications and equivalences, not to all arrows indiscriminately.

## Exercises

1. Draw a category presentation for a production order, its operations, material requirements, and equipment requirements. Add one path equation.
2. Explain why a many-to-many `uses` relation should usually be reified in an ERP ontology.
3. Extend `Gen` with quality inspection concepts. Identify a derived path from a measurement result to a serialized unit.
4. Find a path equation in an existing database that is currently enforced only by application code.
5. Define a `Path` inductive family for the free category generated by `Gen`, with constructors for identity, generators, and composition.
EOF
```

Part I is now drafted at roughly 9,300 words, covering functorial data migration, categorical merging, temporal identity, and the complete PLM–ERP–MES–QMS–EAM pump case study.

<details><summary>💭 Thinking</summary>

**Created and counted the ERP ontology manuscript draft**

</details>

```unknown
bash -lc cat >> /mnt/data/erp_ontology_book_work/theory_of_erp_system_ontologies.md <<'EOF'

# Part II - Dependent Type Theory and Lean 4

# Lean 4 as a Language of Certified Models

## The role of Lean in enterprise design

Lean 4 is both a functional programming language and an interactive theorem prover. For this book, it serves four roles:

1. a precise notation for domain models;
2. a checker for invariants and transformations;
3. a language for executable reference implementations;
4. a metaprogramming platform for ontology-specific tooling.

Lean is not proposed as the runtime of every enterprise transaction. Its strongest role is at the semantic center: define the model, prove critical properties, and produce artifacts that conventional systems can consume.

## Propositions as types

Under the Curry-Howard correspondence, a proposition is represented by a type and a proof by a term of that type. In Lean:

```lean
example : 2 + 2 = 4 := by decide
```

The expression after the colon is a type. The term after `:=` inhabits it. The kernel checks the term.

Business invariants can therefore become types:

```lean
structure Money (currency : String) where
  minorUnits : Int

structure BalancedEntry where
  debit  : Int
  credit : Int
  balanced : debit = credit
```

A `BalancedEntry` value cannot be constructed without a proof that its debit and credit are equal. More useful ledger models allow multiple lines and prove that total debits equal total credits, but the pattern is the same.

## `Prop` and `Type`

Lean distinguishes the proof-irrelevant universe `Prop` from the predicative hierarchy `Type u`. Proofs of the same proposition in `Prop` are definitionally irrelevant. Data in `Type` is computationally relevant unless erased for other reasons.

Use `Prop` when only truth matters:

```lean
structure ReleasedRevision where
  id       : String
  released : Prop
```

Use `Type` when the witness matters:

```lean
structure ReleaseEvidence where
  noticeId  : String
  approvedBy : String
  approvedAt : Nat

structure ReleasedRevision' where
  id       : String
  evidence : ReleaseEvidence
```

In enterprise systems, evidence often matters. A Boolean or proof-irrelevant proposition can assert that a revision is released, but an audit needs the notice, authority, and time. A useful pattern is to carry evidence in `Type` and derive a proposition from it.

## The trusted kernel boundary

Lean elaboration and tactics may be sophisticated, but the trusted kernel checks the resulting term. This supports a useful architecture:

```text
ontology DSL and imported data
        |
        v
elaboration, automation, solvers, code generators
        |
        v
explicit Lean term or proof certificate
        |
        v
small kernel check
```

An ontology compiler may contain bugs. If it generates a false proof term, the kernel should reject it. The trusted computing base is therefore smaller than the full toolchain, although external code generation and runtime integration still require ordinary assurance.

## Universes

Lean has a hierarchy:

```text
Prop
Type 0
Type 1
Type 2
...
```

A type such as `Nat` lives in `Type`. A universe containing such types lives one level higher. Universe polymorphism allows generic definitions:

```lean
universe u v

structure TypedRelation (A : Type u) (B : Type v) where
  holds : A → B → Prop
```

Most ERP models can ignore explicit universe levels until constructing generic ontology frameworks. They become relevant when a model contains types of types, categories of schemas, or object-language universes.

## Definitional and propositional equality

Lean accepts two expressions as definitionally equal when computation and built-in conversion rules reduce them to the same form. Propositional equality is expressed by `Eq` and requires a proof.

```lean
def double (n : Nat) := n + n

example : double 2 = 4 := by rfl
```

Here computation is sufficient. In contrast, a nontrivial theorem may require rewriting or induction.

Definitional equality matters for dependent models because types may compute. If a vector length or workflow state is computed from data, the type checker uses reduction when deciding compatibility.

## Structures, inductive types, and families

A Lean `structure` is a one-constructor inductive type with named fields. An `inductive` declaration can have multiple constructors and can define indexed families.

```lean
inductive OrderState
  | draft | released | inProduction | completed | cancelled
  deriving DecidableEq, Repr

structure Order (state : OrderState) where
  orderNo : String
  item    : String
  qty     : Nat
```

The type `Order .draft` differs from `Order .completed`. The state is not only a field inspected at runtime; it is part of the type.

## Theorem statements as interface laws

A reference implementation should expose laws beside functions:

```lean
structure EquivLike (A B : Type) where
  toFun    : A → B
  invFun   : B → A
  leftInv  : ∀ a, invFun (toFun a) = a
  rightInv : ∀ b, toFun (invFun b) = b
```

An adapter carrying this structure is stronger than a pair of serializers. Its consumers can rely on round-trip behavior.

For lossy migrations, the type should say so:

```lean
structure NormalizingAdapter (A B : Type) where
  encode    : A → B
  decode    : B → A
  normalize : B → B
  decodeEncode : ∀ a, decode (encode a) = a
  encodeDecode : ∀ b, encode (decode b) = normalize b
```

## Total functions and validation boundaries

Lean functions are total unless declared partial or unsafe. Enterprise inputs are not. The boundary should therefore return a sum type such as `Except`:

```lean
inductive DecodeError
  | malformed : String → DecodeError
  | unknownCode : String → DecodeError
  | invariantViolation : String → DecodeError
  deriving Repr

opaque decodeReleasedRevision :
  String → Except (List DecodeError) ReleasedRevision'
```

Once decoding succeeds, internal code can operate on a stronger type. Validation is concentrated at the boundary instead of repeated across every function.

## A project layout

A practical repository can be organized as:

```text
ErpOntology/
  Basic/
    Time.lean
    Quantity.lean
    Evidence.lean
  Domain/
    Product.lean
    Material.lean
    Process.lean
    Asset.lean
    Quality.lean
  Category/
    Schema.lean
    Mapping.lean
    Merge.lean
  Verification/
    Workflow.lean
    Migration.lean
    Coherence.lean
  Export/
    JsonSchema.lean
    SqlChecks.lean
    OpenApi.lean
  HoTT/
    Syntax.lean
    PathInterface.lean
    Pushout.lean
```

The `Export` layer should depend on the verified domain model, not the reverse.

## A note on automation

Lean's automation can discharge routine goals, but the model should not be designed around one tactic. Stable formalization uses small definitions, explicit invariants, and reusable lemmas. Automation then shortens proofs without hiding the semantic structure.

For enterprise models, decidable finite checks, simplification, linear arithmetic, and domain-specific tactics are often more useful than unrestricted theorem search.

## Exercises

1. Rewrite a Boolean `isReleased` field as evidence-carrying data plus a derived proposition.
2. Give an example of an ERP adapter that is normalizing but not invertible.
3. Explain why validation should occur when converting raw data to a refined internal type.
4. Define a structure for a certified currency conversion with a rate source and timestamp.
5. Identify which parts of an ontology toolchain must be trusted if Lean proofs are exported but generated SQL is not independently verified.

# Dependent Types for ERP Domains

## From parameters to indices

A type parameter describes a family of types. An index can constrain which constructors or values are available. In ERP design, indices can represent:

- workflow state;
- currency;
- physical dimension;
- plant or legal entity;
- product revision;
- snapshot or time;
- authorization context;
- configuration validity.

The objective is not to put every database field into a type. The objective is to move high-value distinctions into the type system so illegal combinations cannot be expressed accidentally.

## Dependent functions

A dependent function type

\[
\prod_{x:A} B(x)
\]

has a result type that depends on the input. Lean writes it as `(x : A) → B x`.

```lean
inductive Currency
  | USD | EUR | JPY
  deriving DecidableEq, Repr

structure Money (c : Currency) where
  minor : Int
  deriving Repr

def addMoney {c : Currency} (x y : Money c) : Money c :=
  ⟨x.minor + y.minor⟩
```

The currency is inferred from the arguments. `addMoney` cannot mix USD and EUR.

A conversion depends on both source and target currencies:

```lean
structure FxRate (from to : Currency) where
  numerator   : Int
  denominator : Nat
  nonzero     : denominator ≠ 0
  source      : String
  observedAt  : Nat
```

The type records the direction of the rate. Applying an EUR-to-USD rate as though it were USD-to-EUR becomes a type error.

## Dependent pairs

A dependent pair

\[
\sum_{x:A} B(x)
\]

contains a value `x : A` and a second value whose type depends on `x`. Lean represents common cases using `Sigma`, subtypes, or structures.

An existentially packaged monetary amount can be written:

```lean
abbrev SomeMoney := Sigma Money

example : SomeMoney := ⟨.EUR, ⟨1250⟩⟩
```

The package remembers the currency chosen for the amount.

For business evidence:

```lean
structure ExistingRef (Entity : Type) where
  id      : String
  entity  : Entity
  resolves : True
```

A more realistic repository lookup returns a dependent pair containing an entity and evidence that the identifier resolves in a particular snapshot.

## Refinement by subtype

A subtype `{x : A // P x}` contains a value and a proof of a predicate.

```lean
def PositiveNat := {n : Nat // 0 < n}

structure OrderLine where
  item : String
  qty  : PositiveNat
```

This removes zero and negative quantities from the internal order-line model. Whether zero is invalid depends on the domain; the point is to make the rule explicit.

For finite codes:

```lean
inductive Plant
  | DE01 | US02 | MX03
  deriving DecidableEq, Repr

structure PlantScoped (α : Type) where
  plant : Plant
  value : α
```

A stronger version indexes the value by plant rather than storing a field, preventing cross-plant confusion in signatures.

## Phantom types and branded identifiers

Distinct identifiers should have distinct types even when all serialize as strings.

```lean
structure ProductRevisionId where
  value : String
  deriving DecidableEq, Repr

structure ItemId where
  value : String
  deriving DecidableEq, Repr

structure LotId where
  value : String
  deriving DecidableEq, Repr
```

This is not yet dependent typing, but it delivers immediate value. A function expecting `LotId` cannot receive `ItemId` accidentally.

A generic brand can reduce boilerplate:

```lean
structure Id (tag : Type) where
  value : String
  deriving DecidableEq, Repr

inductive ProductRevisionTag
inductive ItemTag
inductive LotTag

abbrev ProductRevisionId' := Id ProductRevisionTag
abbrev ItemId' := Id ItemTag
abbrev LotId' := Id LotTag
```

The empty tag types exist only at compile time.

## Context-indexed entities

A concept may exist only in a context:

```lean
structure Snapshot where
  transactionNo : Nat

structure EntityAt (s : Snapshot) where
  localId : String
  payload : String
```

A proof obtained for snapshot `s` cannot silently be used for snapshot `t`. This is useful for authorization and existence evidence, though production systems must avoid making every transaction-level value cumbersome.

A more selective pattern indexes only certificates:

```lean
structure ExistsAt (s : Snapshot) (id : String) : Type where
  evidenceId : String

opaque loadEntity
  (s : Snapshot) (id : String) (h : ExistsAt s id) : EntityAt s
```

The certificate records the snapshot in which the lookup was validated.

## Indexed domain relations

Instead of a Boolean relation, use a type of witnesses:

```lean
structure ProductRevision where
  number   : String
  revision : String

structure PhysicalUnit where
  serial : String

structure BuildEvidence
    (unit : PhysicalUnit)
    (rev : ProductRevision) : Type where
  productionOrder : String
  executionId     : String
  genealogyRecord : String
  recordedAt      : Nat
```

An inhabitant of `BuildEvidence unit rev` is specific to that unit and revision. It cannot be reused to justify a different pair.

This is the basic technique behind proof-carrying ontology links.

## Invariants in constructors

A structure constructor can require invariants:

```lean
structure Interval where
  start : Nat
  stop  : Option Nat
  valid : match stop with
    | none   => True
    | some e => start < e
```

Constructing a bounded interval requires a proof that the end follows the start. Raw decoding may fail. Internal functions can then rely on interval validity.

## Avoiding over-indexing

Dependent types can make ordinary operations difficult if every volatile fact becomes an index. Useful criteria for moving a fact into the type are:

- violating it would cause a serious domain error;
- it changes less frequently than the values it classifies;
- many functions depend on it;
- it can be validated at a clear boundary;
- the resulting signatures remain usable.

Plant, currency, dimension, workflow state, and revision baseline are often good indices. Free-form status descriptions and mutable UI labels are not.

## Exercises

1. Define branded identifiers for production order, job order, and work execution. Write a function whose signature prevents mixing them.
2. Model an approved revision as a dependent pair of a revision and release evidence.
3. Create a snapshot-indexed authorization certificate. Explain how it becomes stale.
4. Choose one field in an existing ERP DTO that should become an index and one that should remain ordinary data.
5. Define a type-valued `ConformsTo` relation between a physical unit and product revision with evidence fields appropriate to your industry.

# Quantities, Units, and Dimensional Safety

## Why numbers are not quantities

ERP systems frequently store quantity as a decimal plus a unit code. Errors occur when code assumes that unit codes are compatible, treats percentages as dimensionless amounts without scale conventions, or mixes mass, count, length, and volume.

A mathematical quantity has at least:

- a dimension;
- a unit within that dimension;
- a numeric representation;
- precision and rounding rules;
- sometimes a measurement uncertainty and source.

The type system should prevent dimensionally invalid operations before numeric evaluation.

## A small dimension language

```lean
inductive BaseDim
  | mass | length | time | count | temperature | currency
  deriving DecidableEq, Repr

structure Dimension where
  exponent : BaseDim → Int
```

A mass dimension assigns exponent 1 to `mass` and 0 elsewhere. Velocity assigns 1 to length and -1 to time. A production rate may be count per time.

For a compact textbook implementation, use an inductive enumeration:

```lean
inductive Dim
  | scalar
  | mass
  | length
  | time
  | count
  | volume
  | countPerTime
  deriving DecidableEq, Repr
```

The general exponent-vector model scales better; the enumeration is easier to read.

## Units indexed by dimension

```lean
inductive Unit : Dim → Type
  | one      : Unit .scalar
  | kilogram : Unit .mass
  | gram     : Unit .mass
  | meter    : Unit .length
  | second   : Unit .time
  | piece    : Unit .count
  | liter    : Unit .volume
  | piecePerHour : Unit .countPerTime
  deriving Repr
```

A quantity carries its dimension in the type:

```lean
structure Quantity (d : Dim) where
  value : Rat
  unit  : Unit d
  deriving Repr
```

Addition requires a common dimension:

```lean
def addQuantity {d : Dim}
    (x y : Quantity d) : Quantity d :=
  -- A real implementation converts to a canonical unit first.
  x
```

Even before implementing conversion, it is impossible to add mass to length.

## Canonicalization

Arithmetic should occur in a canonical unit or normalized representation. Define:

```lean
opaque toCanonical {d : Dim} : Quantity d → Rat
opaque canonicalUnit (d : Dim) : Unit d

noncomputable def normalize {d : Dim} (q : Quantity d) : Quantity d :=
  ⟨toCanonical q, canonicalUnit d⟩
```

A theorem states preservation of physical value:

```lean
opaque samePhysicalValue {d : Dim} : Quantity d → Quantity d → Prop

axiom normalize_correct {d : Dim} (q : Quantity d) :
  samePhysicalValue (normalize q) q
```

For executable industrial code, conversion factors should use exact rationals where possible and explicit rounding when converting to storage decimals.

## Quantity roles

Equal dimensions do not imply equal business meaning. A gross mass, net mass, and tare mass share dimension but play different roles. A required quantity and consumed quantity are both counts or masses but have different semantics.

Use role indices or wrappers:

```lean
inductive QtyRole
  | required | reserved | issued | consumed | produced | scrapped
  deriving DecidableEq, Repr

structure RoleQuantity (role : QtyRole) (d : Dim) where
  quantity : Quantity d
```

A reconciliation theorem can relate roles:

\[
\mathsf{issued} = \mathsf{consumed} + \mathsf{returned} + \mathsf{scrapped}.
\]

The role is not a unit. It belongs to the process ontology.

## Currency as a separate index

Currency resembles a dimension but has time-dependent conversion and legal/accounting semantics. Treat it separately:

```lean
structure Amount (c : Currency) where
  minor : Int

structure CertifiedFx (a b : Currency) where
  convert : Amount a → Amount b
  source  : String
  validAt : Nat
```

An exchange rate is not an equivalence if rounding loses information. It may be a normalizing or approximate transformation. The type should not promise invertibility unless the law is true for the chosen representation.

## Uncertainty and measurement

Manufacturing measurements may include tolerance and uncertainty:

```lean
structure Measurement (d : Dim) where
  observed    : Quantity d
  uncertainty : Quantity d
  instrument  : String
  measuredAt  : Nat
```

A specification interval and a measurement result can produce evidence of conformance:

```lean
structure SpecRange (d : Dim) where
  lower : Quantity d
  upper : Quantity d

structure ConformanceEvidence {d : Dim}
    (spec : SpecRange d) (m : Measurement d) where
  method       : String
  calculation  : String
  acceptedBy   : String
```

A complete implementation proves that the uncertainty-aware acceptance rule holds. The witness carries the method and authority.

## BOM quantities

A BOM component quantity is indexed by the component's quantity dimension:

```lean
structure MaterialDefinition where
  id        : String
  stockDim  : Dim

structure BomComponent (parent : ProductRevision) where
  component : MaterialDefinition
  quantity  : Quantity component.stockDim
  scrapRate : Rat
```

The dependent field `quantity : Quantity component.stockDim` ensures that a material stocked in kilograms receives a mass quantity and a piece-counted component receives a count quantity.

This is a direct enterprise use of dependent records.

## Serialization boundaries

JSON Schema and OpenAPI cannot express all dependent invariants directly. Export a tagged representation:

```json
{
  "dimension": "mass",
  "value": "12.500",
  "unit": "kg"
}
```

The decoder checks that the unit belongs to the declared dimension and returns `Quantity .mass`. Database constraints can enforce valid unit-dimension combinations through reference tables and composite foreign keys.

The proof-oriented model therefore informs a conventional representation without requiring the wire format itself to be dependently typed.

## Exercises

1. Extend `Dim` and `Unit` with area and square meter. State the multiplication rule for length times length.
2. Explain why an exchange-rate conversion with rounding is not generally an equivalence.
3. Define `BomComponent` so that a material's stock dimension determines the component quantity type.
4. Model a process yield with produced, consumed, and scrapped quantities. State a conservation law.
5. Design SQL tables that enforce the unit-dimension relationship represented by `Unit : Dim → Type`.

# State-Indexed Workflows

## Status fields are weak state machines

A typical table stores a `status` column and lets service code decide which transitions are legal. This permits impossible combinations such as a completed production order without completion evidence or a shipped order without a shipment.

An indexed family represents each state with state-specific data:

```lean
inductive ProdState
  | draft
  | released
  | scheduled
  | executing
  | completed
  | cancelled
  deriving DecidableEq, Repr

structure ProductionOrder (s : ProdState) where
  orderNo : String
  item    : ItemId
  qty     : PositiveNat
```

State-specific evidence can be separate structures:

```lean
structure ReleaseEvidence where
  releasedBy : String
  releasedAt : Nat

structure ScheduleEvidence where
  jobOrderIds : List String
  scheduledAt : Nat

structure CompletionEvidence where
  executionIds : List String
  completedAt  : Nat
```

## Legal transitions as functions

```lean
structure ReleasedOrder where
  base     : ProductionOrder .released
  evidence : ReleaseEvidence

structure ScheduledOrder where
  base     : ProductionOrder .scheduled
  evidence : ScheduleEvidence

opaque release :
  ProductionOrder .draft →
  ReleaseEvidence →
  ReleasedOrder

opaque schedule :
  ReleasedOrder →
  ScheduleEvidence →
  ScheduledOrder
```

There is no `schedule : ProductionOrder .draft -> ...`. The API does not expose an illegal transition.

A generic indexed representation can store evidence by state:

```lean
inductive ProdEvidence : ProdState → Type
  | draft     : ProdEvidence .draft
  | released  : ReleaseEvidence → ProdEvidence .released
  | scheduled : ScheduleEvidence → ProdEvidence .scheduled
  | executing : String → ProdEvidence .executing
  | completed : CompletionEvidence → ProdEvidence .completed
  | cancelled : String → ProdEvidence .cancelled

structure CertifiedOrder (s : ProdState) where
  base     : ProductionOrder s
  evidence : ProdEvidence s
```

## Transition witnesses

Define a relation of legal transitions:

```lean
inductive CanTransition : ProdState → ProdState → Type
  | release  : CanTransition .draft .released
  | schedule : CanTransition .released .scheduled
  | start    : CanTransition .scheduled .executing
  | complete : CanTransition .executing .completed
  | cancelDraft : CanTransition .draft .cancelled
  | cancelReleased : CanTransition .released .cancelled
```

A transition function can be indexed by the witness:

```lean
opaque applyTransition
  {from to : ProdState} :
  CanTransition from to →
  CertifiedOrder from →
  CertifiedOrder to
```

A value of `CanTransition .completed .draft` cannot be constructed. Reopening may be a separate controlled process that creates a new order version rather than reversing history.

## State machines and events

A transition event should be typed by its source and target states:

```lean
structure TransitionEvent
    (from to : ProdState)
    (rule : CanTransition from to) where
  eventId   : String
  occurredAt : Nat
  actor     : String
  reason    : String
```

Replaying a valid sequence becomes a fold whose type tracks the current state. A database event stream is decoded into existentially packaged typed events and checked for continuity.

## Manufacturing and quality interaction

Completion may depend on quality release. Instead of a Boolean flag:

```lean
structure QualityRelease (orderNo : String) where
  inspectionIds : List String
  releasedBy    : String
  releasedAt    : Nat
```

Require it in the completion transition:

```lean
opaque complete
  (o : CertifiedOrder .executing)
  (q : QualityRelease o.base.orderNo)
  (c : CompletionEvidence) :
  CertifiedOrder .completed
```

The evidence is tied to the specific order number. A release for another order cannot be passed accidentally.

## Parallel and composite workflows

ERP processes often have parallel obligations: material availability, equipment readiness, quality plan approval, and authorization. Model readiness as a dependent record:

```lean
structure StartReadiness (o : CertifiedOrder .scheduled) where
  materialsAvailable : String
  equipmentReady     : String
  qualityPlanActive  : String
  authorization      : String
```

The `start` transition requires the whole record. More formal versions replace strings with typed evidence families.

For flexible workflows, one can define a transition system as data and prove properties such as reachability, absence of dead ends, or separation of duties. The formal model can generate a BPMN-like representation, but the proof-relevant transition relation remains the semantic source.

## Invariants across transitions

A transition should preserve stable fields:

```lean
opaque orderNoPreserved
  {from to : ProdState}
  (r : CanTransition from to)
  (o : CertifiedOrder from) :
  (applyTransition r o).base.orderNo = o.base.orderNo
```

Other fields may change under controlled rules. A quantity change after release may require a change order and produce a new version rather than an in-place transition.

## Compensations are not inverses

Enterprise workflows use compensating actions. Cancelling a goods issue is not necessarily the mathematical inverse of the issue event. It creates new ledger and inventory events that restore selected balances while preserving history.

Therefore:

```text
compensate(issue) != erase(issue)
```

A compensation is a directed morphism with laws about net effect. It should not be modeled as a path or equality. This distinction becomes crucial in Part III: HoTT paths are invertible, while operational events usually are not.

## Exercises

1. Add a `blocked` state with unblock evidence. Decide whether it is a state or an orthogonal condition.
2. Model a purchase-order approval workflow with separation-of-duties evidence.
3. Define a typed completion transition requiring both production and quality evidence.
4. Explain why a cancellation event is usually not an inverse path.
5. Propose one workflow property to prove beyond transition legality, such as eventual terminality or authorization preservation.
EOF
```

<details><summary>💭 Thinking</summary>

**Reviewed and structured Lean 4 ERP ontology manuscript content**

</details>

```unknown
bash -lc cat >> /mnt/data/erp_ontology_book_work/theory_of_erp_system_ontologies.md <<'EOF'

# Part III - Homotopy Type Theory as the Organizing Structure {-}

# From Equality to Paths

## Why ordinary equality is too thin for ontology engineering

The categorical theory developed in Part I distinguishes objects and directed arrows. The dependent type theory of Part II turns many invariants into types. Neither move, by itself, gives a satisfactory account of the following situation:

- PLM revision `PD-2000/C` and MES material definition `MAT-PD2000-C` are judged to present the same approved design content;
- the judgment was obtained by a controlled mapping rule;
- another route through ERP obtains the same judgment;
- the two routes should agree, but the evidence for their agreement matters;
- a later correction may replace one judgment without changing either local identifier.

A Boolean equality test loses the evidence. A proof-irrelevant proposition can establish that a relation holds, but it identifies all proofs of that proposition. A category can express both mapping routes, yet equality of arrows is still imposed externally as a proposition. Ontology federation needs a language in which identifications are first-class objects, their composites are visible, and agreement between composites is itself expressible.

Homotopy type theory supplies that language. Its basic move is to treat identity not as a featureless judgment but as a type of paths.

For a type `A` and terms `a b : A`, write

\[
  \mathsf{Path}_A(a,b)
\]

for the type of identifications from `a` to `b`. A term

\[
  p : \mathsf{Path}_A(a,b)
\]

is a witness that `a` and `b` are identified according to the identity structure carried by `A`.

The path type has at least the following operations:

\[
\begin{aligned}
\mathsf{refl}_a &: \mathsf{Path}_A(a,a),\\
p^{-1} &: \mathsf{Path}_A(b,a),\\
p \mathbin{\cdot} q &: \mathsf{Path}_A(a,c)
\end{aligned}
\]

when `p : Path_A(a,b)` and `q : Path_A(b,c)`. These operations satisfy unit, inverse, and associativity laws, generally up to higher paths rather than by strict definitional equality.

## A path is not every business relationship

The first discipline of an ERP-oriented HoTT is negative:

> Only an invertible semantic identification may be promoted to a path.

The following are normally directed relations, not paths:

```text
physical unit conforms to product revision
material lot is consumed in execution
asset is installed at functional position
product revision supersedes earlier revision
supplier offering commercializes product definition
record represents domain entity
```

Consumption is not invertible. Supersession is not symmetric. Installation is time-indexed and does not make the asset identical to the position. Classification does not identify an instance with its class. Treating such relations as paths would collapse distinctions that the ontology exists to preserve.

Candidate path-producing relations are narrower:

```text
lossless representation equivalence
renaming of a stable concept
isomorphism of two schema presentations
approved reversible code conversion
two certified constructions of the same semantic object
equivalence of ontology objects in a univalent universe
```

Even here, approval conditions matter. An arbitrary adapter is not an equivalence. A migration that drops a legacy field cannot produce an identity unless the field is proved semantically redundant on the admissible domain.

## Local identifiers and semantic objects

Suppose each system has a local type of records:

\[
\mathsf{PlmRevision},\quad
\mathsf{ErpItem},\quad
\mathsf{MesMaterial}.
\]

It is tempting to ask for paths directly between values of these types. That expression is ill-typed: paths compare values in one ambient type. The ontology therefore introduces a semantic universe or a family of semantic presentations.

One approach is a universe of concept presentations:

\[
\mathcal{U}_{\mathrm{ERP}} : \mathsf{Type}
\]

whose inhabitants include presentations of product revisions, material definitions, work executions, and so on. A local model is interpreted into this universe:

\[
\begin{aligned}
\llbracket-\rrbracket_{\mathrm{PLM}} &: \mathsf{PlmConcept} \to \mathcal{U}_{\mathrm{ERP}},\\
\llbracket-\rrbracket_{\mathrm{ERP}} &: \mathsf{ErpConcept} \to \mathcal{U}_{\mathrm{ERP}},\\
\llbracket-\rrbracket_{\mathrm{MES}} &: \mathsf{MesConcept} \to \mathcal{U}_{\mathrm{ERP}}.
\end{aligned}
\]

A semantic identification can then have type

\[
  \mathsf{Path}_{\mathcal{U}_{\mathrm{ERP}}}
  (\llbracket P \rrbracket_{\mathrm{PLM}},
   \llbracket M \rrbracket_{\mathrm{MES}}).
\]

A second approach keeps entity values in a higher inductive federated type. The local systems inject values into that type, and approved alignments generate paths between the injected values. Chapter 20 develops this construction.

## Path induction and transport

The elimination principle for identity says that to prove a property about every path, it is enough to prove it for reflexivity. In ordinary intensional type theory this is the `J` eliminator. In HoTT it supports the path interpretation and all derived path algebra.

The practically decisive operation is transport. For a family

\[
  F : A \to \mathsf{Type}
\]

and a path `p : Path_A(a,b)`, transport moves an inhabitant of `F a` to one of `F b`:

\[
  \mathsf{transport}_F(p) : F(a) \to F(b).
\]

In an ontology, `F` may be a family of valid queries, policy interpretations, validation rules, or configuration structures. Once two semantic concepts are identified, all well-typed dependent constructions can be transported along the identification.

For example, let

\[
  \mathsf{InspectionPlan} : \mathsf{ProductRevision} \to \mathsf{Type}.
\]

If `p : Path(r_1,r_2)`, then

\[
  \mathsf{transport}_{\mathsf{InspectionPlan}}(p)
  : \mathsf{InspectionPlan}(r_1) \to \mathsf{InspectionPlan}(r_2).
\]

The ontology designer no longer writes an unrelated conversion for each dependent construction. The identity principle provides a uniform mechanism. The hard work is moved to justifying the path.

## Paths of records versus paths of meaning

An ERP ontology should distinguish at least three identity spaces:

1. **record identity**, such as identity of two rows or API resources;
2. **referent identity**, such as identity of the physical unit represented by two records;
3. **presentation identity**, such as identity of two equivalent encodings of one semantic concept.

A QMS record and an MES record can refer to the same inspection execution without being the same record. Two JSON shapes can be equivalent presentations without referring to one particular entity. Two serial identifiers can be aliases for the same physical unit while carrying distinct issuance histories.

The distinction can be represented by separate types and maps:

\[
\begin{aligned}
\mathsf{represents} &: \mathsf{Record} \to \mathsf{Entity},\\
\mathsf{presentationOf} &: \mathsf{SchemaPresentation} \to \mathsf{SemanticConcept}.
\end{aligned}
\]

A path between records induces a path between their referents by applying `represents`, but the converse does not follow. Two records may represent one referent and remain operationally distinct. This asymmetry is a recurring design safeguard.

## A Lean-hosted path signature

Standard Lean's `Eq` lives in `Prop` and is proof-irrelevant. To discuss higher paths without confusing them with `Eq`, we expose a separate interface. The following is schematic and axiomatic:

```lean
universe u v w

namespace H

opaque Path {A : Type u} : A -> A -> Type u

opaque refl  {A : Type u} (a : A) : Path a a
opaque symm  {A : Type u} {a b : A} : Path a b -> Path b a
opaque trans {A : Type u} {a b c : A} :
  Path a b -> Path b c -> Path a c

infixr:70 " ~= " => Path
infixr:80 " <.> " => trans

opaque transport {A : Type u} (F : A -> Type v)
    {a b : A} : Path a b -> F a -> F b

opaque ap {A : Type u} {B : Type v} (f : A -> B)
    {a b : A} : Path a b -> Path (f a) (f b)

opaque apd {A : Type u} {B : A -> Type v}
    (f : (a : A) -> B a) {a b : A} (p : Path a b) :
    Path (transport B p (f a)) (f b)

end H
```

This signature does not implement HoTT. It names the operations that an object theory or a cubical backend must justify. Its value in Lean is architectural: ordinary Lean proofs can reason about syntax, typing judgments, generated obligations, and compilation of the ontology calculus, while the higher identity theory remains explicit.

## Alignment evidence before path promotion

Operational systems should not construct paths directly from heuristic matching. Introduce a staged pipeline:

\[
\mathsf{CandidateMatch}
\to \mathsf{ValidatedAlignment}
\to \mathsf{CertifiedEquivalence}
\to \mathsf{Path}.
\]

A candidate can carry similarity scores, source records, and proposed relation kinds. Validation checks typing, scope, time, authority, and round-trip behavior. Certification establishes the laws required of an equivalence. Only then may univalence, introduced in Chapter 18, promote the equivalence to a path.

A Lean model can make the stages impossible to skip:

```lean
structure Candidate (A B : Type) where
  forwardHint : A -> Option B
  source      : String
  confidence  : Nat

structure CertifiedEquiv (A B : Type) where
  toFun       : A -> B
  invFun      : B -> A
  leftInv     : forall a, invFun (toFun a) = a
  rightInv    : forall b, toFun (invFun b) = b
  scope       : String
  authority   : String
```

The equations here use Lean equality because they certify the external data of an equivalence in the host. The HoTT layer then interprets `CertifiedEquiv A B` into its own equivalence object.

## Exercises

1. Classify each relation as directed, potentially invertible, or ambiguous: `classifiedAs`, `substitutesFor`, `sameLotAs`, `installedAt`, `unitConversion`, `supersedes`, `represents`, and `renamedTo`.
2. Give an example where two records have the same referent but must not be identified as records.
3. Define a family `AuthorizedQuery : SemanticConcept -> Type` and explain what transport along a concept path should preserve.
4. Specify the evidence required before an ERP item-to-MES material mapping may be promoted to an equivalence.
5. Explain why a confidence score alone cannot inhabit a path type.

# Higher Paths and Coherence

## Equality between identifications

If paths are terms, they can themselves be compared. Given

\[
  p,q : \mathsf{Path}_A(a,b),
\]

there is a type

\[
  \mathsf{Path}_{\mathsf{Path}_A(a,b)}(p,q)
\]

of paths between paths. These are called **2-paths** or homotopies between identifications. Paths between 2-paths are 3-paths, and the hierarchy continues.

This is not decorative higher-dimensional language. Ontology integration routinely produces multiple routes between the same endpoints. A coherent federation must state how those routes agree.

## The ERP-PLM-MES triangle

Let

\[
\begin{aligned}
f &: E \to P,\\
g &: P \to M,\\
h &: E \to M
\end{aligned}
\]

be semantic mappings from ERP to PLM, PLM to MES, and directly from ERP to MES. For an ERP object `e : E`, there are two resulting MES interpretations:

\[
  g(f(e)) \quad\text{and}\quad h(e).
\]

A commuting triangle requires a family of paths

\[
  \alpha_e : \mathsf{Path}_M(g(f(e)),h(e)).
\]

In category theory, this may be expressed as equality of functors or as a natural transformation. In HoTT, the component paths are first-class, and naturality itself becomes a path equation. If `r : Path_E(e_1,e_2)`, then the following square should commute:

```text
g(f(e1))  --alpha e1-->  h(e1)
   |                       |
   | ap (g o f) r          | ap h r
   v                       v
g(f(e2))  --alpha e2-->  h(e2)
```

The coherence obligation is a 2-path between the two composites around the square.

For Asterion, this detects a concrete inconsistency. Suppose:

```text
ERP item 4711
  --erpToPlm--> product revision PD-2000/C
  --plmToMes--> MES material M-91

ERP item 4711
  --erpToMes--> MES material M-82
```

The endpoints differ. No coherence path can be constructed until one mapping is corrected or a legitimate equivalence between `M-91` and `M-82` is supplied. A dashboard may call this a reconciliation failure; the higher theory identifies it as a missing filler for a diagram.

## Squares, cubes, and enterprise-wide consistency

Three systems yield triangles. Four systems yield tetrahedral or cubic coherence problems. Add QMS to the preceding example. An inspection characteristic can be reached from a PLM drawing, from an ERP inspection plan, or from an MES operation. Pairwise mapping agreements do not guarantee global agreement.

Suppose a semantic object has presentations in systems `A`, `B`, `C`, and `D`. Pairwise alignments provide edges. Coherence among triples provides filled triangles. Agreement among those triangle fillers is a 3-dimensional condition. In large federations, merely storing pairwise crosswalks is therefore insufficient. The integration registry should record:

- endpoints and types of mappings;
- chosen composites;
- witnesses that triangles commute;
- version and validity scope of each witness;
- conflicts where a higher filler is absent.

The language of higher paths tells us exactly what is missing when the registry is not globally coherent.

## Strictness is usually the wrong demand

A common integration specification demands that two routes yield byte-for-byte identical outputs. Sometimes that is correct. Often the routes normalize data differently while preserving meaning. One path may format units in millimetres; another in metres. One may order BOM occurrences by position number; another by a stable internal key. A strict equality of serializations is too strong.

HoTT encourages a layered criterion:

\[
\text{representation equality}
\Rightarrow
\text{semantic path}
\Rightarrow
\text{observational equivalence}.
\]

The exact level depends on the consumer. A signature-verification service may require byte identity. A planning query may require only equality of normalized quantities and effectivity. An audit report may require both semantic equality and explicit provenance of the conversion.

The ontology must name the observation family under which two results are considered equal. Otherwise the word “equivalent” hides a policy decision.

## Coherence data versus coherence properties

Some coherence is operationally relevant data. A signed approval of a cross-system route, a regulatory justification, or a human adjudication should remain inspectable. Other coherence is merely a theorem derivable from canonical constructions and may be erased.

This distinction parallels Part II's separation between proof and evidence:

```lean
structure CoherenceCertificate where
  diagramId     : String
  mappingIds    : List String
  validFrom     : Nat
  validTo       : Option Nat
  approvedBy    : String
  evidenceRefs  : List String
  theoremDigest : String
```

The higher path may certify semantic agreement. The certificate records why the enterprise accepted that path at a particular time. Truncation later controls which details are exported to which boundary.

## Associativity and long mapping chains

Given paths `p : a ~= b`, `q : b ~= c`, and `r : c ~= d`, there are two bracketings:

\[
  (p \cdot q) \cdot r
  \quad\text{and}\quad
  p \cdot (q \cdot r).
\]

They are connected by an associator 2-path. In a strict data pipeline, composition may be implemented with a fixed syntax tree. Semantically, downstream conclusions should not depend on arbitrary bracketing.

The same issue appears with schema adapters. If PLM-to-ERP, ERP-to-MES, and MES-to-analytics adapters are composed, the implementation may batch or regroup stages. A coherence theorem states that regrouping does not alter the semantic result. This is one reason to keep the semantic layer distinct from concrete orchestration.

## Path groupoids and ontology identity

Every type in HoTT carries an infinity-groupoid structure: points, paths, paths between paths, and so on. For many ERP concepts, only a small fragment of this structure is required. An ontology may use:

- points for semantic concepts or entities;
- 1-paths for certified identifications;
- 2-paths for agreement of identification routes;
- possibly 3-paths for agreement among coherence proofs.

The model need not assume that arbitrary higher structure is operationally observable. Chapter 22 uses truncation to bound it.

## Homotopies between mappings

For functions `f g : A -> B`, a homotopy is a family

\[
  H : \prod_{a:A} \mathsf{Path}_B(f(a),g(a)).
\]

This is the natural notion of pointwise semantic agreement between two ontology mappings. It is especially useful for comparing:

- an old and a new transformation implementation;
- a direct mapping and a composed mapping;
- a manually curated mapping and an inferred mapping;
- two plant-specific interpretations of a corporate ontology.

A proof of homotopy can generate property tests. Each test selects an admissible source value and checks that the two implementations produce semantically related targets. The formal theorem states the universal obligation; the generated test suite supplies runtime assurance for external implementations.

## Coherence as a design deliverable

Traditional architecture diagrams show boxes and arrows. A mathematically complete integration design also states the fillers:

```text
objects       systems, concepts, schemas, data values
arrows        mappings, projections, transformations
2-cells       agreements between mapping routes
3-cells       agreements between agreement constructions
```

The practical deliverable is a **coherence catalog**. Each entry includes:

1. the diagram shape;
2. its local mappings;
3. the intended semantic equality;
4. the proof or validation method;
5. the operational enforcement mechanism;
6. the scope in time, plant, product family, and version;
7. the behavior when the filler is missing.

This catalog is more informative than a list of interfaces because it specifies how interfaces compose.

## Exercises

1. Draw the ERP-PLM-MES triangle for a material definition and state the component path required for each ERP item.
2. Extend the triangle with QMS and identify one 3-dimensional coherence obligation.
3. Give an example where byte equality is too strong but semantic path equality is appropriate.
4. Define a homotopy between an old and new unit-conversion adapter.
5. Design a database table for a coherence catalog without pretending that the table itself is the higher path.

# Univalence and Representation Independence

## Equivalence as the correct criterion for sameness of types

Two data types can carry the same information without having the same syntax. Consider two representations of a plant code:

```lean
structure PlantCodeA where
  country : String
  number  : Nat

structure PlantCodeB where
  canonical : String
```

On an admissible subset, a parser and formatter may form a reversible correspondence. In ordinary intensional type theory, an equivalence `PlantCodeA ≃ PlantCodeB` does not make the types equal. Every type-indexed construction requires a manually written transport or congruence theorem.

The univalence principle states, informally, that identity of types has the same structure as equivalence of types:

\[
  \mathsf{Path}_{\mathcal{U}}(A,B)
  \simeq
  \mathsf{Equiv}(A,B).
\]

The map from identity to equivalence is canonical: transport along a path gives an equivalence. Univalence asserts that this map is itself an equivalence. Consequently, a certified equivalence `e : Equiv(A,B)` determines a path

\[
  \mathsf{ua}(e) : \mathsf{Path}_{\mathcal{U}}(A,B).
\]

This is the central HoTT mechanism for representation independence.

## What univalence buys an ERP ontology

Suppose `F : U_ERP -> Type` assigns a dependent construction to every semantic representation. Examples include:

```text
validator for a concept
query language over a concept
policy interpretation for a concept
configuration space indexed by a revision representation
serialization family with declared semantics
proof that a report preserves traceability
```

Given `e : Equiv(A,B)`, univalence yields `ua(e) : Path(A,B)`, and transport yields

\[
  \mathsf{transport}_F(\mathsf{ua}(e)) : F(A) \to F(B).
\]

A single proof of equivalence therefore induces all structurally valid transports. This is stronger than writing one conversion function between values. It says that every construction definable from the type-theoretic interface respects the equivalence.

This does not remove engineering work. One must still prove the equivalence, choose the universe of admissible representations, and control transport at operational boundaries. The benefit is that representation invariance becomes a theorem of the foundational language rather than a repeated convention.

## A manufacturing example: ordered list and linear process graph

Plant A represents a routing as an ordered list of operations:

\[
  \mathsf{ListRouting} = \mathsf{List}(\mathsf{Operation}).
\]

Plant B represents a routing as a directed graph. Not every graph corresponds to a list. Define the refined type

\[
  \mathsf{LinearGraphRouting}
  = \{G : \mathsf{GraphRouting} \mid \mathsf{isLinear}(G)\}.
\]

There may be an equivalence

\[
  e : \mathsf{ListRouting} \simeq \mathsf{LinearGraphRouting}
\]

with forward and backward maps and round-trip laws. Univalence permits the ontology to treat these as two presentations of one routing concept. A scheduling rule indexed by the representation can be transported from one to the other.

The refinement is essential. Claiming an equivalence with all process graphs would be false because branching and parallelism contain additional structure.

## Equivalence is scope-indexed

Enterprise mappings are rarely globally equivalent. A legacy item code and a new product code may be reversible only:

- for one product family;
- after a particular effective date;
- when optional fields satisfy a normalization invariant;
- within one legal entity;
- excluding archived or merged identifiers.

The correct equivalence is therefore between refined types:

\[
  \{x:A \mid P(x)\}
  \simeq
  \{y:B \mid Q(y)\}.
\]

In a dependent formulation, the scope can be indexed:

\[
  \mathsf{EquivAt}(c,t,A,B),
\]

where `c` is a business context and `t` a valid-time interval. Univalence should be applied inside the corresponding universe of scoped concepts, not as a global assertion that the raw system types are identical.

## Structure identity principle

Mathematical structures are often records containing a carrier and operations satisfying laws. The **structure identity principle** says, under suitable univalent formulations, that isomorphic structures can be identified. For ERP ontologies this applies to objects such as:

- unit systems;
- classification taxonomies with structure-preserving equivalences;
- workflow automata;
- code systems;
- schema presentations;
- finite dimensional models;
- product-configuration algebras.

For example, a unit system can be represented by a carrier of units, dimension assignment, conversion operations, and laws. An isomorphism preserving those fields should justify identity of unit-system presentations. Downstream dimensional reasoning then becomes representation-independent.

The principle is not permission to identify merely similar structures. The isomorphism must preserve exactly the structure declared by the ontology. If regulatory metadata is part of the structure, an isomorphism that ignores it is insufficient.

## Univalence and canonical enterprise models

A conventional canonical data model chooses one privileged representation and forces every system through it. This often creates a semantic bottleneck. Univalence suggests a different architecture:

1. retain multiple local presentations;
2. certify equivalences where they genuinely exist;
3. allow constructions to transport across those equivalences;
4. select concrete normal forms only at specified boundaries.

The semantic core is therefore not necessarily a single giant schema. It is a univalent universe of presentations connected by equivalences. The enterprise can preserve local fitness while obtaining principled interoperability.

There are still reasons to choose operational canonical forms: database indexing, API stability, analytics performance, regulatory exchange, and human comprehensibility. Univalence changes the meaning of that choice. The canonical form becomes an implementation convention within an equivalence class, not an ontological declaration that every other presentation is inferior or unreal.

## Computational qualification

If univalence is merely postulated as an axiom, transport along `ua(e)` may not reduce to the expected conversion during computation. A proof can establish that the transport is equivalent to the adapter, but executable normalization may remain opaque.

Cubical type theories provide computational rules for paths, composition, Glue types, and univalence. In such a system, transport along the univalent path can compute according to the equivalence. This is attractive for an executable ontology engine.

The present book separates two goals:

- **foundational modeling**, for which an axiomatic interface is already informative;
- **computational execution**, for which a cubical kernel or translation to explicit adapters is required.

Lean 4 can host and verify the compiler from the first model to the second representation without itself becoming a cubical kernel.

## A Lean-hosted univalence signature

Extend the earlier path interface:

```lean
namespace H

structure Equiv (A : Type u) (B : Type v) where
  toFun    : A -> B
  invFun   : B -> A
  leftInv  : (a : A) -> Path (invFun (toFun a)) a
  rightInv : (b : B) -> Path (toFun (invFun b)) b

opaque idToEquiv {A B : Type u} : Path A B -> Equiv A B
opaque ua        {A B : Type u} : Equiv A B -> Path A B

opaque ua_beta {A B : Type u} (e : Equiv A B) :
  Path (idToEquiv (ua e)) e

end H
```

A complete formulation must handle universe levels and the precise coherence laws. The signature shows the intended separation: host Lean records evidence; the object-level path theory supplies the univalent identification.

## Representation independence as a testable contract

Even when the production system cannot execute higher transports directly, the univalent model generates ordinary obligations:

```text
decode(encode(x)) = x
encode(decode(y)) = y
all declared observations agree after conversion
all indexed policies are preserved
all diagram routes remain coherent
```

These become proofs for verified components and property tests for external services. The HoTT model therefore remains operationally useful even when compiled to explicit functions.

## Exercises

1. Construct the refined domains needed to make two legacy item-code formats equivalent.
2. Explain why a lossy migration cannot produce univalent identity between raw schemas.
3. List the fields that a structure-preserving equivalence of unit systems must preserve.
4. Compare a canonical-schema architecture with a univalent family-of-presentations architecture.
5. State a computational property expected of transport along `ua(e)` in a cubical implementation.
EOF
```

<details><summary>💭 Thinking</summary>

**Appended Homotopy Type Theory and ERP Ontology chapters, then checked word count**

</details>

```unknown
bash -lc cat >> /mnt/data/erp_ontology_book_work/theory_of_erp_system_ontologies.md <<'EOF'

# A Lean 4-Hosted HoTT Ontology Calculus

## Three implementation strategies

There are three distinct ways to combine Lean 4 and HoTT in this project.

### Strategy A: ordinary Lean with HoTT-inspired records

Use Lean's native types, equality, categories, and proof machinery. Represent alignment witnesses, equivalences, diagrams, and coherence certificates as ordinary structures. Compile all higher concepts to explicit data and laws.

This is the most practical strategy for immediate engineering. It supports verified transformations and design exploration, but it does not internalize higher path structure.

### Strategy B: an axiomatic HoTT interface hosted in Lean

Declare a path type in `Type`, path operations, univalence, truncations, and higher inductive constructors as opaque constants with laws. Use Lean to type-check reasoning relative to those axioms and to build compilers from the abstract model.

This is the strategy used for the examples in this part. It preserves the conceptual distinctions but does not provide computational univalence.

### Strategy C: implement an object-level cubical type theory

Define syntax, contexts, typing, evaluation, conversion, interval terms, cofibrations, systems, composition operations, Glue types, and higher inductive types. Lean verifies the implementation and metatheory. The resulting object language computes paths and univalence according to the chosen cubical calculus.

This is the strongest and most demanding strategy. It is justified when the ontology engine itself must normalize higher transports or execute higher inductive constructions.

The strategies can coexist. An enterprise design tool may begin with A, formalize its semantic specification with B, and eventually use a small C kernel for the most important computations.

## Trusted core and untrusted automation

A proof engine should have a small trusted boundary:

```text
surface ontology language
  -> parser
  -> elaborator and unifier
  -> tactics and model synthesis
  -> explicit core term
  -> small type checker
```

The elaborator may infer arguments, resolve names, solve constraints, synthesize coherence diagrams, and search for mapping routes. None of that automation should be trusted. The kernel checks the resulting term.

For ontology work, the trusted core also checks signatures of source ontologies, alignment witnesses, higher constructors, and compilation theorems. External evidence such as signed documents remains outside logical trust but is referenced by terms whose type states the required authority policy.

## A minimal object language

A conventional dependent core begins with universes, dependent functions, dependent pairs, and inductive data. A HoTT-oriented extension adds paths, equivalences, truncations, and selected higher inductive types.

A schematic syntax in Lean is:

```lean
namespace OLang

inductive Expr where
  | var      : Nat -> Expr
  | sort     : Nat -> Expr
  | pi       : Expr -> Expr -> Expr
  | lam      : Expr -> Expr
  | app      : Expr -> Expr -> Expr
  | sigma    : Expr -> Expr -> Expr
  | pair     : Expr -> Expr -> Expr
  | fst      : Expr -> Expr
  | snd      : Expr -> Expr

  | path     : Expr -> Expr -> Expr -> Expr
  | prefl    : Expr -> Expr
  | psymm    : Expr -> Expr
  | ptrans   : Expr -> Expr -> Expr
  | transport : Expr -> Expr -> Expr -> Expr

  | equiv    : Expr -> Expr -> Expr
  | ua       : Expr -> Expr

  | trunc    : Int -> Expr -> Expr
  | squash   : Int -> Expr -> Expr

  | pushout  : Expr -> Expr -> Expr -> Expr
  | inl      : Expr -> Expr
  | inr      : Expr -> Expr
  | glue     : Expr -> Expr

  | ann      : Expr -> Expr -> Expr
  deriving Repr, DecidableEq

end OLang
```

This syntax is intentionally incomplete. It omits constants, records, inductive families, interval syntax, and eliminators. The purpose is to display the trusted distinctions. In particular, `path A a b` is an object-language type and not Lean's `Eq a b`.

## Contexts and judgments

A typing context is a list of types, usually represented with de Bruijn indices or locally nameless syntax. The core judgments are:

\[
\Gamma \vdash A\;\mathsf{type},
\qquad
\Gamma \vdash t : A,
\qquad
\Gamma \vdash t \equiv u : A.
\]

The third judgment is **definitional equality** or conversion. It is a computation rule of the theory, not the path type. This distinction is critical:

- definitional equality is checked by normalization and requires no explicit term;
- path equality is an inhabitant of a type and can carry higher structure.

A kernel that reflects every path into definitional equality would lose decidable checking or collapse the intended homotopical structure.

## Bidirectional checking

The kernel can split typing into synthesis and checking:

```lean
infer : Context -> Expr -> CheckM Value
check : Context -> Expr -> Value -> CheckM Unit
```

Variables, annotations, applications, and projections synthesize types. Lambdas, pairs, reflexivity, and many higher constructors check against expected types.

The path cases include rules of the following shape:

```text
infer Gamma (path A a b):
  checkType Gamma A
  check Gamma a (eval A)
  check Gamma b (eval A)
  return Universe(levelOf A)

check Gamma (prefl a) expected:
  expected reduces to Path A x y
  check Gamma a A
  require x definitionallyEquals a
  require y definitionallyEquals a
```

Path composition checks endpoints. Transport checks a type family, a path in its base, and a source term in the family at the path source.

Univalence and higher inductive constructors are checked against their declared signatures. In an axiomatic kernel they are constants. In a cubical kernel they participate in computation.

## Normalization and conversion

For the non-cubical fragment, normalization by evaluation is a robust design. Syntax is evaluated into semantic values with closures. Neutral terms represent computations blocked by variables. Quotation converts values back to normal forms. Conversion compares quoted normal forms or uses a typed semantic equality procedure.

The value domain may include:

```lean
inductive Value where
  | universe : Nat -> Value
  | pi       : Value -> Closure -> Value
  | lam      : Closure -> Value
  | sigma    : Value -> Closure -> Value
  | pair     : Value -> Value -> Value
  | path     : Value -> Value -> Value -> Value
  | refl     : Value -> Value
  | equiv    : Value -> Value -> Value
  | trunc    : Int -> Value -> Value
  | pushout  : Value -> Value -> Value -> Value
  | inl      : Value -> Value
  | inr      : Value -> Value
  | neutral  : Neutral -> Value
```

An axiomatic `ua` remains neutral unless supplied with computation rules. A cubical implementation instead evaluates path application, transport, composition, and Glue according to the outer type constructor.

## What a cubical extension adds

A computational HoTT kernel typically introduces an interval `I` with endpoints, path abstraction and application, face formulas, partial elements, and composition operations. A conceptual signature includes:

```text
I
0, 1 : I
PathP : (I -> Type) -> A(0) -> A(1) -> Type
lambda i => t
p @ r
transport
homogeneous composition
systems of compatible faces
Glue
```

The difficult operation is composition: fill an open box whose known faces satisfy compatibility conditions. Evaluation dispatches on the type being filled. For function types it composes pointwise; for pairs it composes components dependently; for Glue it uses the equivalence data.

An ERP ontology project should not implement this merely to use sophisticated terminology. It is warranted when computational transport and gluing are central product requirements.

## An ontology declaration language

The surface language should reflect the distinction between arrows and paths. A possible syntax is:

```text
ontology PLM {
  concept ProductDefinition
  concept ProductRevision
  arrow revisionOf : ProductRevision -> ProductDefinition
}

ontology ERP {
  concept Item
  concept PlantItem
  arrow plantItemOf : PlantItem -> Item
}

interface ProductCore {
  concept Definition
  concept Revision
  arrow revisionOf : Revision -> Definition
}

interpret ProductCore into PLM {
  Definition := ProductDefinition
  Revision   := ProductRevision
  revisionOf := PLM.revisionOf
}

align equivalence
  PLM.ProductRevision
  ERP.ReleasedEngineeringItem
  within ProductFamily.PD2000
  during 2026-01-01 .. open
  by certificate CERT-914

require coherence ERP_to_MES = PLM_to_MES o ERP_to_PLM
```

The elaborator turns declarations into explicit category, functor, equivalence, path, and coherence terms. It rejects an `align equivalence` statement if only a one-way mapping is supplied.

## Metavariables and proof obligations

Ontology authors should be able to leave holes:

```text
require coherence direct = via_plm by ?proof
```

The elaborator creates a metavariable with a context and target. Tactics may try:

- reflexivity after normalization;
- functor laws;
- naturality;
- previously certified alignments;
- path algebra;
- congruence under mappings;
- bounded search through the mapping graph;
- an external solver for finite or arithmetic side conditions.

The final solution is inserted into the core term and checked. If automation fails, the unsolved goal is a precise design finding.

## Typed mapping search

A conventional integration registry searches edges by source and target names. A typed engine searches for composable morphisms and equivalences while preserving indices such as context and time.

A search result should include:

```lean
structure MappingPlan (A B : SemanticObject) where
  term          : Mapping A B
  requiredScope : Scope
  assumptions   : List Assumption
  evidence      : List EvidenceRef
  cost          : Nat
  coherence     : List CoherenceGoal
```

The engine may rank plans, but it must not silently equate paths. Distinct routes remain distinct until a coherence term is supplied.

## Proof-producing reconciliation

Given a diagram expected to commute, the engine can generate one of three results:

```text
Certified: a checked path or homotopy closes the diagram
Refuted: a checked counterexample in a finite or decidable fragment
Unknown: an explicit unsolved goal with remaining assumptions
```

This three-way result is preferable to a Boolean “mapping valid” flag. It separates logical status from operational approval.

A reconciliation service can pair the formal status with actual data counts:

```text
formal obligation: direct ~= viaPLM
checked theorem: yes
external implementation tests: 99.998% passed
counterexamples: 14 records
likely cause: implementation or source-data violation
```

The theorem validates the specified transformations. Runtime discrepancies diagnose implementation or data problems rather than ambiguity in the intended law.

## Compilation targets

The object calculus can compile to several targets:

- Lean definitions and theorem statements;
- TypeScript, Kotlin, Rust, or C# domain types;
- JSON Schema and OpenAPI;
- SQL DDL and validation queries;
- event schemas;
- mapping-registry records;
- property-based test generators;
- graph queries for coherence violations;
- documentation diagrams.

Compilation should preserve a trace from each generated artifact to the source declaration and theorem. This permits impact analysis when an ontology concept changes.

## Soundness statement

A kernel implementation should aim for a theorem such as:

\[
  \mathsf{check}(\Gamma,t,A)=\mathsf{success}
  \;\Rightarrow\;
  \Gamma \vdash t:A.
\]

For a self-hosted implementation, Lean can verify this theorem for the object calculus. The theorem does not prove that external evidence documents are truthful or that production adapters match their specifications. Those are separately modeled trust boundaries.

## Exercises

1. Extend `Expr` with path application and a pushout eliminator.
2. State the difference between definitional equality and path equality in the checker.
3. Design a metavariable goal for an ERP-PLM-MES coherence triangle.
4. Specify the trusted computing base for Strategy A, B, and C.
5. Define a typed result for mapping search that reports unresolved coherence obligations.

# The Asterion Digital Thread as a Higher Ontology

## Scope of the case study

We now assemble the three parts around one serialized pump assembly. The case spans:

```text
engineering definition and revision
commercial and plant-specific item planning
manufacturing BOM and routing
production order and MES execution
material genealogy and serialization
inspection and release
installation at a functional position
maintenance replacement and historical configuration
```

The objective is not a universal enterprise ontology. It is a coherent semantic slice that answers Asterion's central competency question with explicit evidence.

## The local theories

Let the local ontology categories be:

\[
  P, E, M, Q, A
\]

for PLM, ERP, MES, QMS, and EAM.

### PLM

Objects include:

```text
ProductDefinition
ProductRevision
AssemblyOccurrence
SpecificationCharacteristic
EngineeringDocumentRevision
```

Arrows include `revisionOf`, `parentRevision`, `childRevision`, `specifiedBy`, and `characteristicOf`.

### ERP

Objects include:

```text
Item
PlantItem
BOMAlternative
ProductionOrder
MaterialReservation
PurchaseOrderLine
```

Arrows include `plantItemOf`, `orderFor`, `requiresItem`, and `procuresItem`.

### MES

Objects include:

```text
MaterialDefinition
MaterialLot
SerializedUnit
JobOrder
WorkExecution
MaterialActual
EquipmentActual
```

Arrows include `lotOf`, `executionOf`, `consumedIn`, `producedBy`, and `usedEquipment`.

### QMS

Objects include:

```text
InspectionPlan
InspectionCharacteristic
InspectionExecution
MeasurementResult
Nonconformance
ReleaseDecision
```

Arrows include `planFor`, `measures`, `resultOf`, and `releases`.

### EAM

Objects include:

```text
FunctionalPosition
MaintainableAsset
InstallationEpisode
MaintenanceOrder
ReplacementEvent
```

Arrows include `episodeAsset`, `episodePosition`, `workOn`, and `replaces`.

Each theory retains its own identity criteria. A PLM revision is not an ERP item. A serialized MES unit is not an EAM database record. A functional position is not a physical asset.

## Shared interfaces

Asterion defines small overlap ontologies:

\[
\begin{aligned}
K_{PE} &: \text{released product semantics shared by PLM and ERP},\\
K_{EM} &: \text{planned material and order semantics shared by ERP and MES},\\
K_{PQ} &: \text{specification semantics shared by PLM and QMS},\\
K_{MA} &: \text{physical unit and equipment-role semantics shared by MES and EAM}.
\end{aligned}
\]

Each overlap has interpretation functors into its neighboring local categories. The overlaps contain only stable common concepts, not every local field.

For example, `K_PE` distinguishes:

```text
ReleasedProductRevision
CommercialPlanningIdentity
RevisionEffectivity
QuantityDimension
```

It does not claim that every ERP item is a PLM revision. Packaging items, services, overhead items, and non-engineered consumables remain outside the overlap.

## Certified equivalences

For the PD2000 product family, Asterion has a released-engineering projection from PLM revisions and a corresponding refined ERP item type:

\[
\begin{aligned}
P_R &= \{r : \mathsf{PLM.ProductRevision} \mid \mathsf{ReleasedPD2000}(r)\},\\
E_R &= \{i : \mathsf{ERP.Item} \mid \mathsf{EngineeringControlledPD2000}(i)\}.
\end{aligned}
\]

A certified equivalence

\[
  e_{PE} : P_R \simeq E_R
\]

contains the identifier conversion, revision/effectivity preservation, and round-trip laws. Univalence supplies a path between these refined presentations in the semantic universe.

No equivalence is declared between raw `ProductRevision` and raw `Item`. The scope refinement prevents an invalid global identification.

Similarly, MES material definitions are equivalent to a refined production view of ERP plant items, not to every ERP item.

## The federated homotopy colimit

The local ontologies and overlaps form a diagram `D`. The semantic federation is modeled as

\[
  \mathcal{F} = \mathsf{hocolim}(D).
\]

Every local concept maps into `F`. Approved overlap alignments generate paths. Composition laws generate higher coherence.

The key design result is that local distinctions remain visible:

```text
in_P(ProductRevision PD-2000/C)
in_E(Item 4711)
in_M(MaterialDefinition M-91)
```

while certified paths connect their refined semantic presentations. A consumer can work invariantly over `F` or choose a local presentation through a projection.

## The product-to-material coherence triangle

For an admissible ERP engineering item `i`, there are two interpretations in MES:

\[
  d(i) : \mathsf{MES.MaterialDefinition}
\]

from the direct ERP-MES mapping, and

\[
  m(p(i))
\]

through ERP-to-PLM and PLM-to-MES. A coherence homotopy supplies

\[
  \alpha_i : \mathsf{Path}(d(i),m(p(i))).
\]

The certificate for `alpha` records mapping versions and validity scope. The operational reconciliation job checks that current external implementations still realize the certified transformations.

If `d(4711)=M-82` while `m(p(4711))=M-91`, the system does not force a path. It produces a conflict object:

```lean
structure MappingConflict where
  sourceRef       : LocalRef
  directTarget    : LocalRef
  composedTarget  : LocalRef
  directMapping   : String
  composedMappings : List String
  observedAt      : Nat
  assumptions     : List String
```

The absence of a path is preserved as an actionable finding.

## From design to planned production

The released engineering structure is transformed into an ERP manufacturing structure. This mapping is generally not an equivalence: manufacturing planning may add phantom assemblies, operation scrap, alternate materials, and plant-specific procurement choices.

Represent it as a directed morphism with conformance laws:

\[
  \mathsf{plan} : \mathsf{EngineeringBOM} \to \mathsf{ManufacturingBOM}.
\]

The law does not state identity. It states that every planned component occurrence is justified by an engineering occurrence, an approved substitution, or a manufacturing-only policy object.

```text
for every planned requirement q:
  designedSource(q)
  or approvedSubstitution(q)
  or authorizedManufacturingAddition(q)
```

This distinction demonstrates the combined framework: the transformation is categorical and dependent; equivalences inside it may generate paths; the whole map remains directed.

## From plan to execution

A production order and MES job order are different operational objects but may have an equivalence of their stable planning views. Execution actuals are not equivalent to requirements. They satisfy them.

Define evidence types:

\[
\begin{aligned}
\mathsf{SatisfiesMaterial} &: \mathsf{MaterialActual} \to \mathsf{MaterialRequirement} \to \mathsf{Type},\\
\mathsf{SatisfiesEquipment} &: \mathsf{EquipmentActual} \to \mathsf{EquipmentRequirement} \to \mathsf{Type},\\
\mathsf{Produces} &: \mathsf{WorkExecution} \to \mathsf{SerializedUnit} \to \mathsf{Type}.
\end{aligned}
\]

A completed execution carries a dependent package containing its actuals and proofs that required conditions were met or that deviations were approved.

## Quality as a dependent view of design and execution

A QMS inspection characteristic is aligned with a PLM specification characteristic through an equivalence of controlled characteristic presentations. The inspection result, however, is an observation, not a path to the specification.

For a characteristic `c`, define:

\[
  \mathsf{Accepts}_c : \mathsf{Measurement}(c) \to \mathsf{Prop}
\]

or a richer evidence type when method, uncertainty, and calibration must be retained. A release decision packages the relevant results, conformance proofs, and authorized disposition of exceptions.

The PLM-ERP-MES-QMS square must commute at the characteristic level. Otherwise a job may inspect a characteristic different from the one required by the released design.

## As-built configuration

For a serialized pump `s`, the as-built configuration is a dependent tree whose nodes contain:

```text
serialized or lot-tracked component
quantity and unit evidence
source material actual
work execution
planned requirement satisfied
engineering occurrence or approved substitution
```

The tree is not merely a list of serial numbers. Its indices ensure that every component placement is meaningful for the parent configuration and time.

A projection maps the rich tree to a set-truncated traceability API. The proof of invariance shows that the API result does not depend on equivalent internal presentation choices.

## Installation and as-maintained identity

MES produces serialized unit `S-1044`. EAM record `E-90017` represents the same physical unit. This yields a referent identity path only after both representations are interpreted into the physical-unit semantic type.

The unit is installed at functional position `FP-CP-4` during interval `I_1`. Later unit `S-2088` occupies the same position during `I_2`.

```text
S-1044 != FP-CP-4
S-2088 != FP-CP-4
S-1044 != S-2088
```

The position persists; occupancy is a directed temporal relation. A query for the installed asset at time `t` returns a dependent pair containing the unit and an occupancy witness.

A maintenance replacement creates a new as-maintained configuration. It does not retroactively change the as-built configuration. A coherence theorem relates the event history to the snapshot projection.

## The central query

Asterion's core query can now be typed schematically as:

\[
\begin{aligned}
\mathsf{explainUnit} :
  &(s : \mathsf{SerializedUnit}) \to
  (t : \mathsf{Time}) \to\\
  &\mathsf{Result}\;\mathsf{QueryError}\;
  (\mathsf{DigitalThreadEvidence}(s,t)).
\end{aligned}
\]

The result contains:

```text
semantic physical-unit identity
local system references and representation paths
released design revision
planned manufacturing configuration
actual material and equipment genealogy
inspection and release evidence
functional position at time t
as-maintained configuration at time t
alignment and coherence certificates used by the derivation
```

Sensitive evidence may be propositionally truncated or access-controlled in a public view. The audit view retains full certificates.

## Derived API

A conventional API can expose:

```http
GET /serialized-units/{serial}/digital-thread?at=2026-07-01T00:00:00Z
GET /serialized-units/{serial}/as-built
GET /functional-positions/{id}/occupancy?at=...
GET /alignments/explain?left=...&right=...
GET /coherence/conflicts?diagram=product-material
```

The response includes ordinary JSON identifiers and records. Each response declares:

```text
semanticModelVersion
validTime
transactionTime
sourceSnapshotIds
mappingCertificateIds
coherenceStatus
```

The API is set-like and decidable. Its design, however, is generated from the higher model and accompanied by invariance theorems.

## Derived database structures

The operational schema separates:

```text
local_reference
semantic_entity
representation_claim
alignment_certificate
mapping_definition
coherence_certificate
mapping_conflict
installation_episode
material_actual
configuration_edge
provenance_reference
```

No single foreign key is asked to encode every kind of sameness. Temporal exclusion constraints prevent overlapping occupancy episodes where policy forbids them. Unique constraints apply only inside declared identity scopes.

## Failure scenario: revision ambiguity

Assume ERP item `4711` once referred to revision B and later to revision C without a revision-qualified key. A naive canonical model overwrites the mapping. The higher model instead indexes the equivalence by validity interval:

\[
\begin{aligned}
e_B &: E_R(I_B) \simeq P_B,\\
e_C &: E_R(I_C) \simeq P_C.
\end{aligned}
\]

A query lacking time cannot construct the required path and returns `AmbiguousEffectivity`. This is not a nuisance introduced by formalism. It is a defect already present in the business question.

## Failure scenario: non-transitive deduplication

Suppose supplier record `a` matches corporate product `b`, and `b` matches plant product `c`, but `a` and `c` differ in a regulated material attribute. A relation generated from pairwise similarity is not transitive. Quotienting it would produce an unsound identity class.

The higher model retains two paths only if separately certified and then asks for coherence with the regulated attribute observation. Failure to construct that coherence blocks quotient promotion. The ontology engine has exposed an obstruction before data is irreversibly merged.

## Success criteria

The case-study model is successful when it supports the following checked properties:

1. local ontology functors preserve declared path equations;
2. certified equivalences have explicit scope and round-trip laws;
3. every higher glue is backed by an approved certificate;
4. required mapping diagrams have coherence terms or explicit conflicts;
5. directed realization and conformance relations remain distinct from identity;
6. as-built and as-maintained projections preserve temporal provenance;
7. operational APIs factor through declared truncations;
8. generated tests connect external implementations to the formal transformations.

These criteria turn a broad “digital thread” initiative into a finite set of mathematical and engineering obligations.

## Exercises

1. Add supplier and EPCIS event ontologies to the Asterion diagram and identify new overlaps.
2. State the exact refined types needed for the PLM-ERP product-revision equivalence.
3. Design the dependent result of `installedAt(position,t)`.
4. Identify one mapping in the case study that is directed but contains internal equivalences.
5. Define a public, set-truncated view and an audit view of `DigitalThreadEvidence`.
6. Construct a conflict scenario caused by inconsistent unit dimensions rather than identifiers.

# Method, Design Principles, and Research Program

## The method in twelve steps

A disciplined ERP ontology project can proceed as follows.

1. **Select a semantic slice.** Choose a bounded digital thread or workflow, not the entire enterprise.
2. **Write competency questions.** Include time, authority, evidence, and failure cases.
3. **Build local categorical theories.** Preserve each system's distinctions and equations.
4. **Separate representations from referents.** Do not equate records with domain entities.
5. **Classify relations.** Mark arrows, candidate equivalences, temporal roles, and evidence claims.
6. **Define small overlap ontologies.** Treat them as treaties between bounded contexts.
7. **Formalize dependent invariants in Lean.** Encode units, states, revisions, scope, and provenance.
8. **Certify equivalences.** Require refined domains and round-trip laws.
9. **Construct higher gluings.** Use paths only for approved invertible identifications.
10. **State coherence fillers.** Make route agreement an explicit deliverable.
11. **Choose truncation boundaries.** Decide what APIs, databases, and analytics may observe.
12. **Generate conventional artifacts.** Produce schemas, contracts, constraints, tests, and reconciliation jobs.

The process is iterative. A failed proof often means the ontology has exposed a missing distinction or an overstrong integration claim.

## Design principles

### Preserve direction

Manufacturing is full of non-invertible processes: production, consumption, inspection, approval, replacement, and supersession. Model them as directed arrows or dependent relations. HoTT enriches identity; it does not make the world reversible.

### Earn every path

A path is a certified semantic identification. It should arise from reflexivity, path algebra, an explicit equivalence through univalence, or a declared higher constructor. Similar names and machine-learning scores generate candidates, not paths.

### Treat coherence as data and theorem

The semantic agreement can be a higher path; the enterprise approval and provenance should remain inspectable data. Store both at their appropriate layers.

### Use univalence locally

Declare universes and structures for which equivalence should imply identity. Do not univalently identify concepts under an impoverished signature. The preserved structure defines the meaning of sameness.

### Delay truncation

Retain higher distinctions during design and integration analysis. Truncate deliberately at operational boundaries after proving invariance of consumers.

### Keep the kernel small

Search, matching, diagram completion, code generation, and external solvers are untrusted automation. Require explicit checked terms at the semantic boundary.

### Compile, do not deploy the metatheory wholesale

The target system should use ordinary technologies suited to operations. Compile formal distinctions into IDs, APIs, events, constraints, tests, and audit structures. Retain a trace to the theory.

## Limits of the theory

The formal model does not eliminate organizational uncertainty. A certificate can state that an authorized engineer approved an alignment; it cannot establish that the engineer inspected the physical equipment correctly. A path can encode a chosen identity policy; it cannot make a disputed corporate policy objectively true.

The model also does not replace:

- transaction isolation;
- cybersecurity controls;
- physical calibration;
- data stewardship;
- legal interpretation;
- human exception handling;
- operational monitoring.

It clarifies assumptions and propagates their consequences.

## Open engineering questions

Several practical questions deserve experimentation:

1. What surface notation allows ontology engineers to express higher coherence without becoming type theorists?
2. Which fragments of cubical type theory are sufficient for schema equivalence and higher-inductive federation?
3. How should proof-producing mapping search interact with probabilistic entity matching?
4. How can homotopy levels be inferred or checked from declared API observations?
5. Which reconciliation queries can be generated automatically from homotopy-coherent diagrams?
6. How should ontology versions and path certificates evolve under breaking changes?
7. Can Rezk-completion techniques yield useful canonical semantic identifiers without arbitrary global representative choices?
8. How can formal proofs be linked to signed industrial evidence and regulated audit trails?
9. Which standards fragments form good overlap ontologies for particular manufacturing sectors?
10. How should counterexamples from live data refine the formal ontology?

## A proposed research prototype

A credible prototype has four components:

```text
1. Lean library
   local categories, functors, dependent domain types, laws

2. hosted HoTT specification
   Path, Equiv, univalence, pushouts, truncations, coherence

3. ontology compiler
   DSL -> core terms -> JSON Schema, SQL, API, tests

4. reconciliation runtime
   mapping registry, evidence store, diagram checks, conflict reports
```

The first case study should remain the product-to-asset digital thread. It is rich enough to exercise revisioning, identity, time, physical realization, quality, and maintenance, but bounded enough for a small team.

## Final perspective

Category theory explains how local enterprise theories compose. Dependent type theory makes their invariants explicit and checkable. Homotopy type theory supplies the missing identity discipline: identifications have witnesses, witnesses compose, competing routes require coherence, and equivalent presentations can become substitutable without selecting one absolute representation.

The resulting theory does not turn an ERP into a topological space for rhetorical effect. It recognizes a concrete fact about industrial information: the enterprise contains many presentations of related realities, and the ways those presentations are identified are structured, revisable, and compositional. A correct ontology must model not only entities and arrows but also the geometry of their agreements.
EOF
```

<details><summary>💭 Thinking</summary>

**Appended chapter 23 and removed control characters from the ontology book**

</details>

```json
{"open":[{"ref_id":"turn903319search0"},{"ref_id":"turn557654search2"},{"ref_id":"turn557654search6"},{"ref_id":"turn820282search9"},{"ref_id":"turn926908search0"},{"ref_id":"turn926908search1"},{"ref_id":"turn926908search2"},{"ref_id":"turn409486search0"},{"ref_id":"turn409486search11"},{"ref_id":"turn436722search1"},{"ref_id":"turn276570search0"},{"ref_id":"turn276570search14"},{"ref_id":"turn226214search0"},{"ref_id":"turn226214search7"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 7 websites**

</details>

```unknown
bash -lc cat >> /mnt/data/erp_ontology_book_work/theory_of_erp_system_ontologies.md <<'EOF'

# Appendix A - Lean 4 Project Setup {-}

## Toolchain

The examples were written against Lean 4.32.2. The official release note dated July 28, 2026 states that this point release corrected a kernel soundness defect, so older 4.32 releases should not be used to validate untrusted proof artifacts.

A minimal project can be created with `lake`:

```bash
mkdir erp-ontology
cd erp-ontology
lake init ErpOntology
lake build
```

For mathlib, use the project instructions current at installation time. A representative `lakefile.toml` is:

```toml
name = "ErpOntology"
version = "0.1.0"
defaultTargets = ["ErpOntology"]

[[lean_lib]]
name = "ErpOntology"

[[require]]
name = "mathlib"
git = "https://github.com/leanprover-community/mathlib4.git"
rev = "<pinned-compatible-revision>"
```

Pin both Lean and mathlib in source control. A proof artifact is reproducible only relative to its toolchain, dependency revisions, options, and axioms.

## Suggested repository structure

```text
ErpOntology/
  Core/
    Identity.lean
    Time.lean
    Quantity.lean
    Evidence.lean
  Category/
    SmallCategory.lean
    Schema.lean
    Instance.lean
    Migration.lean
    Colimit.lean
  Domain/
    PLM.lean
    ERP.lean
    MES.lean
    QMS.lean
    EAM.lean
  Alignment/
    ProductCore.lean
    MaterialCore.lean
    EquipmentCore.lean
    Coherence.lean
  Workflow/
    Production.lean
    Quality.lean
    Maintenance.lean
  HoTT/
    Signature.lean
    Syntax.lean
    Typing.lean
    Semantics.lean
    Compile.lean
  Generate/
    JsonSchema.lean
    Sql.lean
    OpenApi.lean
    Tests.lean
  CaseStudy/
    Asterion.lean
  Test/
```

The `HoTT` directory should not redefine native Lean equality by notation. Names such as `H.Path` and `H.Equiv` keep the object theory visible.

## Build discipline

A serious project should enforce:

```text
no unreviewed axioms in the ordinary verified core
explicit list of axioms used by the HoTT-hosted layer
pinned toolchain and dependency revisions
kernel rechecking in CI
generated artifact diffs
property tests for non-Lean implementations
semantic-model version embedded in outputs
```

Lean's `#print axioms theoremName` is useful for inspecting dependencies of ordinary theorems. A hosted HoTT development will intentionally report the declared path, univalence, or higher-inductive axioms unless those are implemented by a separate checked object kernel.

## Core imports

Examples using only the Lean core may begin with:

```lean
import Lean
```

Categorical examples can import targeted mathlib modules rather than all of Mathlib:

```lean
import Mathlib.CategoryTheory.Category.Basic
import Mathlib.CategoryTheory.Functor.Basic
import Mathlib.CategoryTheory.NatIso
import Mathlib.CategoryTheory.Limits.Shapes.Pullback.Basic
import Mathlib.CategoryTheory.Limits.Shapes.Pushout
```

Module names can evolve. Pinning the library makes the book's project stable even when the latest documentation changes.

## Test categories

Use four distinct test suites:

1. **kernel tests** for accepted and rejected core terms;
2. **theorem tests** for domain invariants and coherence;
3. **generation tests** comparing emitted schemas and queries with snapshots;
4. **integration tests** checking external implementations against generated laws.

A negative test is often more valuable than a positive one. Confirm that the model rejects a lot where a material definition is expected, a physical asset where a functional position is expected, and a one-way migration where an equivalence is required.

# Appendix B - A Small Category Kernel in Lean {-}

This appendix gives a small pedagogical category interface. Production work should normally use mathlib's category-theory library, but a local kernel clarifies the concepts.

```lean
universe u v

structure SmallCategory where
  Obj : Type u
  Hom : Obj -> Obj -> Type v
  id  : (A : Obj) -> Hom A A
  comp : {A B C : Obj} -> Hom A B -> Hom B C -> Hom A C
  id_comp : forall {A B} (f : Hom A B), comp (id A) f = f
  comp_id : forall {A B} (f : Hom A B), comp f (id B) = f
  assoc : forall {A B C D}
      (f : Hom A B) (g : Hom B C) (h : Hom C D),
      comp (comp f g) h = comp f (comp g h)
```

The composition order here is left-to-right for readability. State the convention prominently; many libraries use the opposite notation.

A functor preserves source, target, identities, and composition:

```lean
structure SmallFunctor (C : SmallCategory) (D : SmallCategory) where
  obj : C.Obj -> D.Obj
  map : {A B : C.Obj} -> C.Hom A B -> D.Hom (obj A) (obj B)
  map_id : forall A, map (C.id A) = D.id (obj A)
  map_comp : forall {A B C'} (f : C.Hom A B) (g : C.Hom B C'),
    map (C.comp f g) = D.comp (map f) (map g)
```

A natural transformation compares functors pointwise and satisfies naturality:

```lean
structure NatTrans {C D : SmallCategory}
    (F G : SmallFunctor C D) where
  app : (A : C.Obj) -> D.Hom (F.obj A) (G.obj A)
  naturality : forall {A B} (f : C.Hom A B),
    D.comp (F.map f) (app B) =
    D.comp (app A) (G.map f)
```

## A finite schema example

```lean
inductive PlmObj
  | productDefinition
  | productRevision
  deriving DecidableEq, Repr

inductive PlmHom : PlmObj -> PlmObj -> Type
  | idDef : PlmHom .productDefinition .productDefinition
  | idRev : PlmHom .productRevision .productRevision
  | revisionOf : PlmHom .productRevision .productDefinition
```

For larger schemas, explicitly enumerating all composites becomes inconvenient. One can define arrows as paths in a typed graph modulo equations, or use a free category construction and quotient by declared path equations. Mathlib supplies mature machinery for these constructions.

## Instances as functors

A set-valued instance assigns a Lean type to each object and a function to each arrow:

```lean
structure SetInstance (C : SmallCategory) where
  obj : C.Obj -> Type
  map : {A B : C.Obj} -> C.Hom A B -> obj A -> obj B
  map_id : forall A, map (C.id A) = id
  map_comp : forall {A B C'} (f : C.Hom A B) (g : C.Hom B C'),
    map (C.comp f g) = (map g) o (map f)
```

The functor laws are data-quality laws. `map_id` states that following an identity arrow changes nothing. `map_comp` states that the interpretation of a composed schema path agrees with composing the interpreted functions.

## Schema mappings and migration

A schema mapping is a functor. Pulling an instance back along a functor is straightforward:

```lean
def delta {C D : SmallCategory}
    (F : SmallFunctor C D) (I : SetInstance D) : SetInstance C where
  obj A := I.obj (F.obj A)
  map f := I.map (F.map f)
  map_id A := by
    -- follows from F.map_id and I.map_id
    sorry
  map_comp f g := by
    -- follows from F.map_comp and I.map_comp
    sorry
```

The `sorry` placeholders indicate short proof obligations. A checked project must remove them. Left and right data migrations require Kan-extension constructions and are better taken from a category-theory library.

## A commuting triangle as a theorem

Suppose direct and composed functions map ERP items to MES materials:

```lean
variable {ErpItem PlmRevision MesMaterial : Type}
variable (erpToPlm : ErpItem -> PlmRevision)
variable (plmToMes : PlmRevision -> MesMaterial)
variable (erpToMes : ErpItem -> MesMaterial)

class CoherentTriangle : Prop where
  commutes : forall i, erpToMes i = plmToMes (erpToPlm i)
```

This ordinary Lean theorem is already useful. Part III replaces proof-irrelevant equality with path-valued coherence when distinct witnesses and higher composition are semantically relevant.

# Appendix C - Consolidated Hosted HoTT Signature {-}

The following interface collects the principal concepts used in Part III. It is a specification boundary, not a complete implementation.

```lean
universe u v w

namespace H

opaque Path {A : Type u} : A -> A -> Type u
opaque refl  {A : Type u} (a : A) : Path a a
opaque symm  {A : Type u} {a b : A} : Path a b -> Path b a
opaque trans {A : Type u} {a b c : A} :
  Path a b -> Path b c -> Path a c

infixr:70 " ~= " => Path
infixr:80 " <.> " => trans

opaque ap {A : Type u} {B : Type v} (f : A -> B)
  {a b : A} : Path a b -> Path (f a) (f b)

opaque transport {A : Type u} (F : A -> Type v)
  {a b : A} : Path a b -> F a -> F b

structure Equiv (A : Type u) (B : Type v) where
  toFun    : A -> B
  invFun   : B -> A
  leftInv  : (a : A) -> Path (invFun (toFun a)) a
  rightInv : (b : B) -> Path (toFun (invFun b)) b

opaque idToEquiv {A B : Type u} : Path A B -> Equiv A B
opaque ua        {A B : Type u} : Equiv A B -> Path A B
opaque ua_beta   {A B : Type u} (e : Equiv A B) :
  Path (idToEquiv (ua e)) e

opaque IsProp : Type u -> Type u
opaque IsSet  : Type u -> Type u
opaque Trunc  : Int -> Type u -> Type u
opaque tr     (n : Int) {A : Type u} : A -> Trunc n A

opaque Pushout {K : Type u} {A : Type v} {B : Type w}
  (f : K -> A) (g : K -> B) : Type (max u v w)

opaque inl {K : Type u} {A : Type v} {B : Type w}
  {f : K -> A} {g : K -> B} : A -> Pushout f g

opaque inr {K : Type u} {A : Type v} {B : Type w}
  {f : K -> A} {g : K -> B} : B -> Pushout f g

opaque glue {K : Type u} {A : Type v} {B : Type w}
  {f : K -> A} {g : K -> B} (k : K) :
  Path (inl (f k)) (inr (g k))

opaque pushoutRec
  {K : Type u} {A : Type v} {B : Type w}
  {f : K -> A} {g : K -> B} {X : Type u}
  (aMap : A -> X)
  (bMap : B -> X)
  (coh : (k : K) -> Path (aMap (f k)) (bMap (g k))) :
  Pushout f g -> X

end H
```

A usable theory also requires laws for path groupoid operations, computation rules for transport, function extensionality or its derivation, truncation eliminators, pushout computation rules, and universe management. A cubical implementation replaces opaque operations with computational primitives.

## ERP-specific wrappers

Keep business evidence around path promotion:

```lean
structure Scope where
  plant         : Option String
  productFamily : Option String
  validFrom     : Nat
  validTo       : Option Nat

structure EvidenceRef where
  repository : String
  identifier : String
  digest     : String

structure AlignmentCertificate (A B : Type) where
  equivalence : H.Equiv A B
  scope       : Scope
  authority   : String
  evidence    : List EvidenceRef
  version     : String
```

The semantic path is obtained from `H.ua certificate.equivalence`. The scope and evidence are not discarded; they govern when the path may be used in an enterprise query.

# Appendix D - Glossary {-}

**Alignment.** A typed claim connecting presentations or entities across bounded contexts. Its relation kind, scope, evidence, and authority must be explicit.

**As-built configuration.** The actual component structure realized during production, including lots, serials, substitutions, and execution provenance.

**As-designed configuration.** The released engineering structure and specifications under a particular revision and effectivity context.

**As-maintained configuration.** The physical configuration at a later time after installation, replacement, repair, or modification.

**As-planned configuration.** The manufacturing and resource plan derived from design plus plant-specific policies.

**Bounded context.** A local theory with its own vocabulary, authority, and identity criteria.

**Category.** Objects and directed morphisms with identity and associative composition.

**Coherence.** Evidence that different composites or constructions agree. In HoTT, this can be a higher path.

**Colimit.** A universal construction combining a diagram. Pushouts are a central binary gluing form.

**Competency question.** A domain question the ontology must answer with defined semantics and evidence.

**Definitional equality.** Equality determined by computation in the type checker. It is not the same as an explicit path.

**Dependent pair.** A pair whose second component's type depends on the first; written `Sigma x : A, B x`.

**Dependent type.** A type parameterized or indexed by a value, enabling invariants to appear in signatures.

**Descent.** Reconstruction of global data from compatible local data and coherent transition information.

**Displayed category.** A category of structured objects built over a base category, useful for modular ontology layers.

**Entity resolution.** The process of determining which records refer to the same entity. Candidate matching is not yet equality.

**Equivalence.** A reversible map with inverse laws. Under univalence, equivalence of types corresponds to identity of types.

**Evidence.** Operationally retained information justifying a claim: documents, signatures, observations, authority, and provenance.

**Functor.** A structure-preserving mapping between categories. In categorical databases it can be a schema mapping.

**Functional position.** A persistent role or location in a plant that may be occupied by different physical assets over time.

**Higher inductive type.** A type defined by point constructors and path or higher-path constructors.

**Homotopy.** A pointwise path between functions or mappings.

**Homotopy colimit.** A colimit retaining generated paths and higher coherence rather than collapsing them to set-level equality.

**Homotopy level.** A measure of the complexity retained in identity types: proposition, set, groupoid, and higher levels.

**Identity criterion.** The declared conditions under which two presentations count as the same object for a theory.

**Instance.** An interpretation of a schema that assigns data types to objects and functions to arrows; categorically, often a set-valued functor.

**Local ontology.** The typed concepts, relations, equations, instances, and identity policy of one bounded context.

**Natural transformation.** A coherent pointwise transformation between functors.

**Olog.** An ontology log formulated using categories, where types are objects, aspects are arrows, and facts include commuting diagrams.

**Path.** A first-class identification between terms in HoTT. Paths compose and may themselves have paths.

**Physical asset.** A concrete physical device or unit, distinct from the logical equipment role or functional position it fulfills.

**Proof.** A term inhabiting a proposition or type. Proof-irrelevant logical proofs should be distinguished from retained business evidence.

**Pushout.** A merge of two objects along a shared interface. As a higher inductive type it includes source injections and glue paths.

**Quotient.** A construction adding identifications generated by a relation.

**Record identity.** Identity of information records, not necessarily identity of their referents.

**Referent.** The domain object represented by an information record.

**Reification.** Treating a relation or event as an explicit entity so it can carry time, provenance, and attributes.

**Rezk completion.** A completion of a precategory into a univalent category, making isomorphism correspond to object identity.

**Schema.** A typed theory of entities and relationships, not merely a collection of tables.

**Set truncation.** Projection to a type whose identity types are mere propositions, suitable for many operational identities.

**Structure identity principle.** The principle that equality of suitably univalent structured objects corresponds to structure-preserving isomorphism.

**Temporal scope.** The valid-time and often transaction-time interval in which a claim or alignment applies.

**Transport.** Moving dependent data or proofs along a path.

**Truncation.** A construction that limits observable higher identity structure.

**Univalence.** The principle identifying paths between types with equivalences between types.

# Appendix E - Selected Exercise Solutions {-}

## Distinguishing position and asset

A functional position has an identity based on its role in a plant structure. A physical asset has an identity based on a concrete unit, often a serial or other lifecycle identifier. Model occupancy as:

\[
  \mathsf{InstalledAt} :
  \mathsf{PhysicalAsset} \to
  \mathsf{FunctionalPosition} \to
  \mathsf{Interval} \to
  \mathsf{Type}.
\]

Replacement creates a new witness with a new asset and interval. It does not create a path between the two assets or between either asset and the position.

## A commuting material triangle

Let:

```text
p : ErpEngineeringItem -> PlmReleasedRevision
m : PlmReleasedRevision -> MesMaterialDefinition
d : ErpEngineeringItem -> MesMaterialDefinition
```

The required homotopy is:

\[
  \alpha : \prod_i \mathsf{Path}(d(i),m(p(i))).
\]

A data-quality implementation compares normalized target identifiers and semantic attributes for every admissible item. A formal implementation constructs `alpha` from certified equivalences and functor laws.

## Lossy schema migration

Suppose schema A contains `(id, hazardousMaterialCode)` and schema B contains only `id`. The projection `A -> B` is not invertible unless the admissible A-domain proves that `hazardousMaterialCode` is uniquely derivable from `id`. Without that theorem, B contains less information and no equivalence exists. The projection may still be a valid directed migration.

## Propositional truncation for authorization

An authorization decision may require only that some valid capability exists:

\[
  \lVert \mathsf{Capability}(u,a,r,s) \rVert_{-1}.
\]

This prevents the decision procedure from depending on which of several equivalent grants was found. An audit endpoint returns the untruncated capability and its evidence references.

## Pushout consumer

To define a reporting projection from `PLM sqcup_K ERP` to `ReportConcept`, provide:

```text
plmReport : PLM -> ReportConcept
erpReport : ERP -> ReportConcept
coherence : for every k : K,
  Path (plmReport(f(k))) (erpReport(g(k)))
```

The coherence term is not optional. It proves that the report gives one meaning to every concept glued by the merge.

## Preventing an invalid quotient

If candidate duplicate relation `R` is not transitive, do not form an operational quotient. Retain `R` as evidence-bearing edges, close it only under an approved policy, check that all identity-sensitive observations agree across the proposed classes, and then generate a certified equivalence relation `R*`. Quotient by `R*`, not by the raw similarity graph.

## Operational factorization

Let `q : F -> ||F||_0` be set truncation of a federated ontology. An operational query `Q : F -> Result` factors through `q` when there exists `Q0 : ||F||_0 -> Result` such that

\[
  Q = Q_0 \circ q.
\]

It is enough to show that `Q` is invariant under all paths of `F` and that `Result` is a set, using the set-truncation eliminator.

# References and Further Reading {-}

## Lean and dependent type theory

Lean FRO. *The Lean Language Reference*, latest edition. Sections “The Type System” and “Universes.” <https://lean-lang.org/doc/reference/latest/>

Lean FRO. *Lean 4.32.2 Release Notes*, July 28, 2026. <https://lean-lang.org/doc/reference/latest/releases/v4.32.2/>

The mathlib community. *Mathlib 4 Documentation*, especially `Mathlib.CategoryTheory`. <https://leanprover-community.github.io/mathlib4_docs/>

Avigad, Jeremy; de Moura, Leonardo; Kong, Soonho. *Theorem Proving in Lean 4*. <https://lean-lang.org/theorem_proving_in_lean4/>

Kovacs, Andras. *Elaboration Zoo*: small implementations of dependent type checking and elaboration. <https://github.com/AndrasKovacs/elaboration-zoo>

Martin-Lof, Per. *Intuitionistic Type Theory*. Bibliopolis, 1984.

Nordstrom, Bengt; Petersson, Kent; Smith, Jan M. *Programming in Martin-Lof's Type Theory*. Oxford University Press, 1990.

## Category theory, ologs, and categorical data

Spivak, David I. “Functorial Data Migration.” *Information and Computation* 217 (2012): 31-51. Preprint: <https://arxiv.org/abs/1009.1166>

Spivak, David I.; Kent, Robert E. “Ologs: A Categorical Framework for Knowledge Representation.” *PLoS ONE* 7(1), 2012. Preprint: <https://arxiv.org/abs/1102.1889>

Fong, Brendan; Spivak, David I. *Seven Sketches in Compositionality: An Invitation to Applied Category Theory*. Cambridge University Press, 2019. Open manuscript: <https://dspivak.net/7Sketches.pdf>

Spivak, David I.; Wisnesky, Ryan. “Relational Foundations for Functorial Data Migration.” *Proceedings of DBPL*, 2015. <https://arxiv.org/abs/1212.5303>

Mac Lane, Saunders. *Categories for the Working Mathematician*. Second edition. Springer, 1998.

Riehl, Emily. *Category Theory in Context*. Dover, 2016. <https://math.jhu.edu/~eriehl/context.pdf>

## Homotopy type theory and cubical type theory

The Univalent Foundations Program. *Homotopy Type Theory: Univalent Foundations of Mathematics*. Institute for Advanced Study, 2013. <https://homotopytypetheory.org/book/>

Cohen, Cyril; Coquand, Thierry; Huber, Simon; Mortberg, Anders. “Cubical Type Theory: A Constructive Interpretation of the Univalence Axiom.” *21st International Conference on Types for Proofs and Programs*, 2018. <https://arxiv.org/abs/1611.02108>

Coquand, Thierry; Huber, Simon; Mortberg, Anders. “On Higher Inductive Types in Cubical Type Theory.” *33rd Annual ACM/IEEE Symposium on Logic in Computer Science*, 2018. <https://arxiv.org/abs/1802.01170>

Ahrens, Benedikt; Kapulkin, Krzysztof; Shulman, Michael. “Univalent Categories and the Rezk Completion.” *Mathematical Structures in Computer Science* 25(5), 2015. <https://arxiv.org/abs/1303.0584>

Cubical Agda documentation. <https://agda.readthedocs.io/en/latest/language/cubical.html>

UniMath project. Formalization of univalent mathematics in Coq. <https://github.com/UniMath/UniMath>

## Industrial and interoperability sources

International Society of Automation. *ISA-95 Series of Standards: Enterprise-Control System Integration*. The series is also published as IEC 62264; Part 1 has a 2025 ISA edition. <https://www.isa.org/standards-and-publications/isa-standards/isa-95-standard>

OPC Foundation. *OPC UA Common Object Model for ISA-95*. The public reference includes material definitions, lots, equipment, physical assets, personnel, and related distinctions. <https://reference.opcfoundation.org/specs/OPC-10030/>

OPC Foundation. *OPC UA for ISA-95, Part 4: Job Control*. <https://reference.opcfoundation.org/specs/OPC-10031-4/full>

International Organization for Standardization. *ISO 10303-242:2025: Industrial automation systems and integration - Product data representation and exchange - Part 242: Managed model-based 3D engineering*. <https://www.iso.org/standard/84300.html>

International Organization for Standardization. *ISO 15926 series: Industrial automation systems and integration - Integration of life-cycle data for process plants including oil and gas production facilities*. <https://www.iso.org/standard/93280.html>

Industrial Digital Twin Association. *Asset Administration Shell Specifications*. The official catalog listed Release 26-01 at the time of writing. <https://industrialdigitaltwin.org/en/content-hub/aasspecifications>

Industrial Digital Twin Association. *Specification of the Asset Administration Shell, Part 1: Metamodel*, IDTA 01001. <https://industrialdigitaltwin.org/en/content-hub/aasspecifications/specification-of-the-asset-administration-shell-part-1-metamodel-idta-number-01001>

Industrial Digital Twin Association. *AAS Submodel Templates*. <https://industrialdigitaltwin.org/en/content-hub/submodels>

GS1. *EPCIS 2.0.1*, published July 1, 2025. <https://ref.gs1.org/standards/epcis/2.0.1/>

## Notes on standards use

The standards listed here are source ontologies and interoperability constraints, not one unified upper ontology. Their scopes overlap imperfectly. A project should select versioned fragments, state its interpretation functors, and preserve local terminology where the standards make different distinctions.
EOF
```

<details><summary>💭 Thinking</summary>

**Compiled and validated ERP ontology Markdown into a PDF with Lean appendices**

</details>

```unknown
bash -lc pdfinfo /mnt/data/theory_of_erp_system_ontologies.pdf | sed -n '1,30p'
python /home/oai/skills/pdfs/scripts/pdf_inspect.py /mnt/data/theory_of_erp_system_ontologies.pdf | head -120
python /home/oai/skills/pdfs/scripts/pdf_preflight.py /mnt/data/theory_of_erp_system_ontologies.pdf | head -160
```

<details><summary>💭 Thinking</summary>

**Inspected and rendered ERP ontology PDF pages**

</details>

```unknown
from PIL import Image, ImageOps, ImageDraw
from pathlib import Path
render_dir = Path('/mnt/data/erp_ontology_book_work/renders')
pages = sorted(render_dir.glob('page-*.png'))
contact_dir = Path('/mnt/data/erp_ontology_book_work/contact')
contact_dir.mkdir(exist_ok=True)
thumb_w, thumb_h = 255, 330
cols, rows = 4, 5
for batch_idx in range(0, len(pages), cols*rows):
    batch = pages[batch_idx:batch_idx+cols*rows]
    sheet = Image.new('RGB', (cols*thumb_w, rows*(thumb_h+24)), 'white')
    draw = ImageDraw.Draw(sheet)
    for i, p in enumerate(batch):
        img = Image.open(p).convert('RGB')
        img.thumbnail((thumb_w-8, thumb_h
```

<details><summary>💭 Thinking</summary>

**Created contact sheets and inspected Python's `/mnt/data` availability**

</details>

```unknown
bash -lc rm -rf /mnt/data/erp_ontology_book_work/contact && mkdir -p /mnt/data/erp_ontology_book_work/contact
for start in $(seq 1 20 142); do end=$((start+19)); [ $end -gt 142 ] && end=142; files=''; for n in $(seq $start $end); do files="$files /mnt/data/erp_ontology_book_work/renders/page-$(printf '%03d' $n).png"; done; montage $files -thumbnail 247x320 -tile 4x5 -geometry +4+24 -background white -pointsize 18 -set label '%t' /mnt/data/erp_ontology_book_work/contact/contact-$(printf '%03d' $start)-$(printf '%03d' $end).jpg; done
ls -lh /mnt/data/erp_ontology_book_work/contact
```

<details><summary>💭 Thinking</summary>

**Inspected files and created ImageMagick contact sheets**

</details>

```unknown
bash -lc rm -rf /mnt/data/* && mkdir -p /mnt/data/erp_ontology_book_work
cat > /mnt/data/erp_ontology_book_work/theory_of_erp_system_ontologies.md <<'EOF'
---
title: "Theory of ERP System Ontologies"
subtitle: "Category Theory, Dependent Types, and Homotopy Type Theory for Industrial Systems"
author: "First-edition working manuscript"
date: "August 2026"
lang: en-US
documentclass: book
classoption:
  - 10pt
  - openany
geometry:
  - inner=0.9in
  - outer=0.75in
  - top=0.8in
  - bottom=0.85in
toc: true
toc-depth: 3
numbersections: true
colorlinks: true
linkcolor: blue
urlcolor: blue
mainfont: "DejaVu Serif"
sansfont: "DejaVu Sans"
monofont: "DejaVu Sans Mono"
monofontoptions:
  - Scale=0.82
header-includes:
  - |
    \usepackage{microtype}
    \usepackage{booktabs}
    \usepackage{longtable}
    \usepackage{array}
    \usepackage{fvextra}
    \usepackage{xcolor}
    \usepackage{fancyhdr}
    \usepackage{enumitem}
    \usepackage{amsthm}
    \usepackage{mathtools}
    \usepackage{amssymb}
    \usepackage{stmaryrd}
    \usepackage{upquote}
    \definecolor{BookBlue}{HTML}{17365D}
    \definecolor{BookGray}{HTML}{F3F5F7}
    \fvset{breaklines=true,breakanywhere=true,fontsize=\small}
    \setlist{nosep}
    \pagestyle{fancy}
    \fancyhf{}
    \fancyhead[LE,RO]{\small\thepage}
    \fancyhead[LO]{\small\nouppercase{\rightmark}}
    \fancyhead[RE]{\small\nouppercase{\leftmark}}
    \renewcommand{\headrulewidth}{0.3pt}
    \newtheorem{definition}{Definition}[chapter]
    \newtheorem{proposition}[definition]{Proposition}
    \newtheorem{theorem}[definition]{Theorem}
    \newtheorem{principle}[definition]{Design Principle}
    \newtheorem{warning}[definition]{Warning}
---

# Preface {-}

Enterprise resource planning systems are often described as databases surrounded by workflows. That description is operationally useful but mathematically shallow. An industrial enterprise does not merely store rows. It maintains many overlapping theories of products, materials, processes, equipment, organizations, obligations, measurements, and time. Product lifecycle management, ERP, manufacturing execution, quality management, warehouse management, maintenance, supplier portals, and industrial control systems each encode a different theory of the same plant.

The hard integration failures are therefore semantic failures. A part revision is confused with a stock item. A functional position is confused with the physical asset installed there. A material definition is confused with a lot. A planned operation is confused with an execution. A record identifier is confused with the entity represented by the record. Two mappings are locally plausible but disagree when composed around a larger integration diagram.

This book develops a mathematical theory for those situations. It has three parts.

**Part I** treats an ERP landscape as a family of categories. Local ontologies are typed schemas with equations. Instances are functors. Cross-system mappings are functors. Changes of data are natural transformations. Merges are colimits, especially pushouts. This gives a precise language for the directed, compositional structure of industrial information.

**Part II** moves from external categorical models into dependent type theory and Lean 4. Business invariants become types. Valid workflows become indexed families. Quantities carry dimensions. Migrations carry proofs. Alignments carry evidence. The result is not a proposal to implement an entire ERP in a theorem prover. It is a method for designing a small verified semantic core whose consequences are exported to conventional APIs, events, database constraints, and tests.

**Part III** takes homotopy type theory seriously as an organizing structure. Ontology integration contains not only arrows but identifications, multiple witnesses of identification, and coherence between routes of identification. HoTT turns identity into a structured type of paths, equivalence into a source of identity through univalence, and ontology gluing into higher inductive constructions. Univalent categories explain how isomorphic concepts can become genuinely substitutable. Truncation explains how a rich higher semantic model can be compiled down to ordinary records without pretending that the higher structure never existed.

There is an important technical qualification. Standard Lean 4 is not a native HoTT kernel. Its `Prop` universe is proof-irrelevant, and its built-in equality is not the higher path type used by HoTT. In Part III, Lean 4 is used in two controlled ways:

1. as a metaprogramming language in which we specify an object-level HoTT calculus; and
2. as a host for axiomatic interfaces whose path type lives in `Type`, separate from `Lean.Eq`.

This distinction is maintained throughout. The book does not claim that changing notation turns ordinary Lean equality into homotopical equality.

The intended result is a theory of ontology engineering that can guide ordinary implementation. The production system may still be written in Java, C#, Kotlin, Rust, TypeScript, SQL, or a data-platform language. The mathematical phase exists to discover distinctions, invariants, equivalences, and coherence obligations before they are buried in schemas and integration code.

## Intended audience {-}

The primary audience includes enterprise architects, industrial data modelers, PLM/ERP/MES integration engineers, formal methods practitioners, and researchers in applied category theory or type theory. The reader should be comfortable with typed programming and ordinary relational data modeling. No prior category theory or HoTT is assumed, although mathematical maturity is required.

A reader focused on architecture may read Chapters 1-7, 14-15, and 24-25 first. A Lean practitioner may begin with Chapter 8. A type theorist may skim the industrial preliminaries but should not skip Chapter 6, where the identity problems are stated in domain terms.

## The running case: Asterion Drives {-}

The running example is a fictional manufacturer, Asterion Drives, which designs and manufactures configurable industrial pump and motor assemblies. It operates five plants and uses the following systems:

- a PLM system for product definitions, engineering revisions, documents, and engineering bills of material;
- an ERP system for commercial items, plant-specific planning data, procurement, production orders, inventory, and accounting;
- an MES for work schedules, job orders, material actuals, equipment actuals, genealogy, and production events;
- a QMS for inspection plans, characteristics, nonconformances, and release decisions;
- an EAM system for functional locations, assets, maintenance plans, work orders, and replacement history;
- supplier and logistics systems that exchange product, shipment, and traceability events.

Asterion's recurring question is:

> For a serialized pump operating at a customer site, what was designed, what was ordered, what was built, what was inspected, what is currently installed, and what evidence justifies every cross-system identification used in the answer?

Every major construction in the book contributes to answering this question.

## Conventions {-}

The book uses `Type` for information that may carry computationally or semantically relevant witnesses and `Prop` for proof-irrelevant assertions in ordinary Lean developments. In the HoTT part, mere propositions and sets are defined by truncation level rather than identified with Lean's `Prop`.

A phrase such as "same entity" is never accepted without a declared criterion of sameness. The book distinguishes at least the following:

- strict record identity;
- identity of a represented domain entity;
- isomorphism or equivalence of representations;
- classification or conformance;
- realization of a design by a physical unit;
- occupancy of a functional role during a time interval;
- a provisional matching claim supported by evidence.

These relations have different algebraic properties. Most are not equality.

## Status of code {-}

The ordinary Lean examples target Lean 4.32.2 syntax and a contemporaneous mathlib snapshot. This version is chosen because it was the current stable release on August 5, 2026, and it includes a kernel soundness correction released on July 28, 2026. Most examples use only core Lean features. Blocks importing `Mathlib.CategoryTheory` rely on mathlib. Blocks marked `-- schematic` emphasize a design and may require supporting definitions from earlier chapters.

The Part III interface is intentionally axiomatic. It illustrates the signature that a HoTT-aware ontology kernel should expose; it does not make Lean's kernel compute univalence or higher inductive types.

# Part I - Categorical Foundations for ERP Ontologies {-}

# The Enterprise as a Family of Theories

## From tables to claims

An ERP landscape is not a single database distributed across products. It is a federation of local theories. Each system makes claims of a particular form and is authoritative only for some of them.

The PLM system can assert that revision `PD-2000/C` has an approved engineering bill of material. The ERP system can assert that item `4711` is planned as a manufactured item at plant `DE01`. The MES can assert that lot `L-882` was consumed by execution `EX-9003`. The EAM can assert that serialized unit `S-1044` occupied functional position `FP-CP-4` during a specified interval. These claims are related, but they do not belong to one undifferentiated type called `Entity`.

A useful first discipline is to separate five layers:

| Layer | Typical inhabitants | Central question |
|---|---|---|
| Definition | product definition, material definition, equipment class | What kind of thing is specified? |
| Version | product revision, BOM revision, routing revision | Which controlled state of a definition applies? |
| Physical instance | lot, serial, physical asset, container | Which concrete thing existed? |
| Role or position | work center, functional location, equipment role | What function was to be fulfilled? |
| Record or representation | PLM record, ERP item row, AAS shell, OPC UA node | Which information object represents something else? |

Many failed canonical models collapse two or more layers. The resulting table acquires a `type` discriminator, dozens of nullable foreign keys, and business rules that are impossible to state locally.

## Local ontologies

A **local ontology** is the formal vocabulary and law set of a bounded context. It includes:

1. entity and value types;
2. typed relationships;
3. composition rules;
4. path equations or invariants;
5. admissible instances;
6. an account of identity and representation.

For example, a small PLM ontology may include types

$$
\mathsf{ProductDefinition},\quad
\mathsf{ProductRevision},\quad
\mathsf{Occurrence},\quad
\mathsf{DocumentRevision}
$$

and functions

$$
\begin{aligned}
\mathsf{revisionOf} &: \mathsf{ProductRevision} \to \mathsf{ProductDefinition},\\
\mathsf{parent} &: \mathsf{Occurrence} \to \mathsf{ProductRevision},\\
\mathsf{child} &: \mathsf{Occurrence} \to \mathsf{ProductRevision},\\
\mathsf{specifiedBy} &: \mathsf{Occurrence} \to \mathsf{DocumentRevision}.
\end{aligned}
$$

An ERP ontology may instead include `Item`, `PlantItem`, `ProductionOrder`, and `MaterialReservation`. An MES ontology distinguishes `MaterialDefinition`, `MaterialLot`, `JobOrder`, and `MaterialActual`. The names may overlap while the meanings do not.

## Reference is not identity

A system record is an information object. A domain entity is what the record is about. The distinction can be made explicit:

```lean
inductive System
  | plm | erp | mes | qms | eam
  deriving DecidableEq, Repr

structure LocalRef where
  system   : System
  concept  : String
  localId  : String
  revision : Option String := none
  deriving DecidableEq, Repr

inductive DomainKind
  | productDefinition
  | productRevision
  | commercialItem
  | materialDefinition
  | materialLot
  | serializedUnit
  | physicalAsset
  | functionalPosition
  deriving DecidableEq, Repr

structure RepresentationClaim where
  recordRef : LocalRef
  kind      : DomainKind
  validFrom : Nat
  validTo   : Option Nat
  source    : String
```

This code is modest, but it blocks a pervasive category mistake: a `LocalRef` is not itself a product revision, lot, asset, or position. A reference can be stale, duplicated, merged, or reassigned. The represented domain entity has a different identity criterion.

## Competency questions before schemas

Ontology design should begin with **competency questions**, not entity lists. A competency question is a query the model must support with a defensible meaning. For Asterion:

```text
Which released engineering revision governed serial S-1044?
Which actual lots were consumed in its production?
Which substitutions were used, under what authority, and during which effectivity?
Which inspection results justified release?
Which physical unit occupied functional position FP-CP-4 at alarm time?
Does the as-maintained configuration conform to an approved configuration?
Why does ERP item 4711 map to MES material definition M-91?
```

Each question forces distinctions that a CRUD-first model can postpone. “Which revision?” requires effectivity. “Which unit occupied a position?” separates role from physical instance. “Why does this map?” requires provenance and a mapping theory.

## Relation kinds

Cross-system integration needs a controlled relation vocabulary. A starting set is:

```text
SameRecord
SameReferent
EquivalentRepresentation
Classifies
Instantiates
ConformsTo
Realizes
Commercializes
InstalledAt
PlaysRole
ConsumedIn
ProducedBy
DerivedFrom
Supersedes
Replaces
PotentialMatch
```

The algebraic properties differ. `SameReferent` should be symmetric and transitive under a stable identity policy. `Supersedes` is directed. `InstalledAt` is time-indexed. `PotentialMatch` may have a confidence score and need not be transitive.

A canonical `sameAs` edge is therefore usually too weakly typed to be safe.

## Authority is part of the theory

A claim is not only true or false; it is made under an authority policy. PLM may be authoritative for released design, ERP for financial valuation, MES for actual consumption, QMS for release disposition, and EAM for installation history. The policy can be modeled as a relation

$$
  \mathsf{Authoritative}(s,c,p,t)
$$

where system `s` is authoritative for claim class `c`, under plant or organizational scope `p`, during time interval `t`. Authority itself is versioned data and should be represented explicitly when integration decisions depend on it.

## Design consequences

A theory-first approach produces concrete implementation consequences:

- Separate identifiers for definitions, revisions, physical instances, roles, and records.
- Store cross-system correspondences as claims with relation kind, scope, time, status, and evidence.
- Make mapping routes explicit enough to test their coherence.
- Keep local ontologies intact instead of flattening them prematurely.
- Derive APIs from competency questions and invariants rather than from tables alone.

## Exercises

1. In a manufacturing organization familiar to you, list three concepts overloaded under one word such as “asset,” “material,” or “order.” Separate their identity criteria.
2. Give an example where a record is deleted but the represented entity continues to exist.
3. Write five competency questions for an engineering-change process and identify the time dimension required by each.
4. Classify `approvedSubstituteFor`, `sameSerialAliasAs`, and `installedAt` by symmetry, transitivity, and temporal dependence.
5. Define an authority matrix for one PLM-ERP-MES-QMS interaction.

# Typed Graphs, Categories, and Ologs

## Typed graphs

A typed directed graph consists of nodes, arrows, and source and target functions. Nodes represent concept types. Arrows represent functional aspects or relationships after reification where necessary.

A simple PLM graph may contain:

```text
ProductRevision --revisionOf--> ProductDefinition
AssemblyOccurrence --parent--> ProductRevision
AssemblyOccurrence --child--> ProductRevision
AssemblyOccurrence --quantity--> Quantity
```

A relationship such as “a work execution consumes many lots” is not itself a function from execution to lot. Reify a consumption occurrence:

```text
MaterialActual --execution--> WorkExecution
MaterialActual --lot--> MaterialLot
MaterialActual --quantity--> Quantity
```

Reification provides an object on which time, provenance, unit, operation, and reversal information can be stored.

## Categories

A category consists of:

- a collection of objects;
- a collection of morphisms between objects;
- an identity morphism on every object;
- composition of compatible morphisms;
- identity and associativity laws.

For an ontology schema, objects are types and morphisms are meaningful functional paths. If

$$
f : A \to B, \qquad g : B \to C,
$$

then the composite $g \circ f : A \to C$ is a derived semantic path.

For example:

```text
AssemblyOccurrence --child--> ProductRevision --revisionOf--> ProductDefinition
```

has a composite “the product definition of the child revision.” The category remembers that this derivation is lawful and compositional.

## Path equations

A category can declare that two paths have the same meaning. Suppose an MES `MaterialActual` reaches a material definition through either a recorded definition or through its lot:

```text
MaterialActual --recordedDefinition--> MaterialDefinition
MaterialActual --lot--> MaterialLot --definition--> MaterialDefinition
```

The desired equation is

$$
  \mathsf{recordedDefinition}
  =
  \mathsf{definition}\circ\mathsf{lot}.
$$

Every valid data instance must respect the equation. This is more precise than documentation saying the fields “should agree.” It creates a checkable reconciliation law.

## Free categories and presented categories

A typed graph generates a **free category** whose morphisms are finite paths. An ontology adds equations between paths, yielding a category by generators and relations. This separation is useful:

```text
generators  = primitive concepts and fields
paths       = derived navigation
relations   = declared semantic agreements
```

Database schemas often expose generators but leave relations implicit in application code. Formal ontology work elevates those relations into the model.

## Ologs

An ontology log, or **olog**, presents a category using controlled natural-language labels. Objects are labeled by singular indefinite noun phrases, and arrows by functional verb phrases.

```text
[a serialized pump]
    --was manufactured according to-->
[a released product revision]
    --is a revision of-->
[a product definition]
```

The linguistic discipline matters. “Uses” is generally not functional. “Has its recorded unit of measure” may be functional in a particular bounded context. Ambiguous phrases reveal an under-specified schema.

Ologs also use commutative diagrams to express facts. The material-definition equation above becomes a diagram that must commute.

## Partiality and multiplicity

ERP relationships are often optional or many-valued. A category of total functions does not directly represent every database relation. Several techniques are available:

- use `Option B` for a partial functional relationship;
- reify a many-to-many relationship as an occurrence type;
- refine the domain to objects for which the relationship is total;
- use spans, relations, profunctors, or indexed categories for genuinely relational semantics.

For example, “released revision” can be modeled as a refined type:

$$
  \mathsf{ReleasedRevision}
  = \{r : \mathsf{ProductRevision} \mid \mathsf{Released}(r)\}.
$$

Then `approvedBOM : ReleasedRevision -> BOMRevision` can remain total if the policy guarantees one approved BOM.

## Monomorphisms, epimorphisms, and information loss

Categorical properties can diagnose mappings. Informally:

- a monomorphism behaves like an information-preserving embedding;
- an epimorphism behaves like a surjective abstraction;
- an isomorphism is a reversible structural correspondence.

A projection from a full product revision to a reporting key may be many-to-one and therefore lose information. It should not be advertised as an equivalence. A code-renaming map with a verified inverse may be an isomorphism.

## Products and pullbacks

Products combine independent information. Pullbacks combine records that agree over a shared key or semantic object.

Suppose MES executions and QMS inspections both map to production orders. Their pullback represents compatible pairs:

$$
  \mathsf{Execution}
  \times_{\mathsf{ProductionOrder}}
  \mathsf{Inspection}.
$$

A row in this pullback is not an arbitrary execution-inspection pair. Both refer to the same production order under the chosen mappings. Pullbacks therefore model typed joins with semantic constraints.

## Exercises

1. Reify the relation “a maintenance order replaces a component” so that the replacement can carry time, reason, old unit, new unit, and authorizer.
2. Write a commuting diagram for the statement that an inspection result's product revision agrees with the revision of its production order.
3. Give a partial relationship in ERP and model it both with `Option` and with a refined domain.
4. Identify an information-losing projection in a real interface and explain why it is not an isomorphism.
5. Define a pullback query combining material actuals with supplier certificates over material lots.

# Instances, Queries, and Natural Transformations

## Instances as set-valued functors

In the functorial database model, a schema is a small category $C$, and an instance is a functor

$$
  I : C \to \mathbf{Set}.
$$

For each schema object $A$, the set $I(A)$ contains current rows or identifiers of type $A$. For each arrow $f : A \to B$, the function $I(f) : I(A) \to I(B)$ interprets the relationship. Identity and composition laws ensure that schema paths behave coherently in data.

This viewpoint makes a foreign key more than a column constraint. It is the interpretation of a typed semantic arrow.

## Example instance

Let the schema contain:

```text
MaterialActual --lot--> MaterialLot --definition--> MaterialDefinition
MaterialActual --recordedDefinition--> MaterialDefinition
```

An instance assigns:

```text
I(MaterialActual)     = set of actual-consumption records
I(MaterialLot)        = set of lot records
I(MaterialDefinition) = set of MES material definitions
```

and functions between those sets. The path equation requires:

```text
for every material actual a:
  recordedDefinition(a) = definition(lot(a))
```

A violation means either corrupt data, an invalid schema equation, or a hidden temporal or contextual distinction. Formalization does not decide which; it localizes the disagreement.

## Nulls and open-world data

The category `Set` assumes total functions. Operational data often contains missing values, late-arriving events, disputed references, and unknown matches. Do not encode all uncertainty as a magic null. Distinguish:

```text
not applicable
not yet known
unknown in the source
withheld by policy
failed lookup
conflicting candidates
```

These can be modeled by sum types or explicit status records. The semantic schema may require totality at a certified boundary even if ingestion is partial.

## Queries as constructions on instances

A query maps instances to results while respecting instance transformations. Categorical constructions correspond to familiar data operations:

- products and pullbacks resemble typed joins;
- coproducts resemble tagged unions;
- limits enforce compatible families;
- colimits merge data under identifications;
- Kan extensions implement systematic data migration.

The value is not replacing SQL syntax. It is obtaining compositional semantics and laws that queries must respect.

## Natural transformations

Let $I,J : C \to \mathbf{Set}$ be two instances of the same schema. A natural transformation

$$
  \eta : I \Rightarrow J
$$

assigns a function $eta_A : I(A) \to J(A)$ to every object $A$ so that every schema arrow commutes:

$$
  J(f)(\eta_A(x)) = \eta_B(I(f)(x)).
$$

This models a structure-preserving change of an entire database instance: a migration, normalization, anonymization, or synchronization step.

If product revision identifiers are normalized, the transformation must also update occurrences, documents, and every other dependent reference so that navigation still commutes.

## Snapshot evolution

Let `I_t` be the enterprise instance at time `t`. A controlled update may be a natural transformation

$$
  I_t \Rightarrow I_{t+1}.
$$

Not every operational update is naturally total or irreversible. Deletions, corrections, and event-sourced histories may require spans, partial maps, or a category of versioned states. The natural-transformation model remains valuable as the law for updates that claim to preserve the schema.

## Provenance-aware instances

Instead of assigning plain sets, an instance can assign sets of values carrying provenance. One can work in a category of evidence-bearing records, semirings of provenance, or dependent pairs:

$$
  \sum_{x:A} \mathsf{Evidence}(x).
$$

This shifts “where did this value come from?” from a logging afterthought into the instance semantics.

## Natural joins and pullbacks

Suppose:

```text
MaterialActual -> MaterialLot
SupplierCertificate -> MaterialLot
```

Their pullback contains material-actual and certificate pairs that refer to the same lot. A dependent refinement can also require certificate validity at consumption time. The query result then carries a witness of compatibility rather than only repeated keys.

## Functor categories

For a fixed schema `C`, instances and natural transformations form a category $[C,\mathbf{Set}]$. This gives a disciplined setting for sequences of migrations:

```text
raw ingestion -> normalized instance -> certified instance -> reporting projection
```

Composition preserves the structure-preserving property. A migration pipeline can therefore be verified stage by stage.

## Exercises

1. Define a set-valued instance for a minimal product-revision schema.
2. State the naturality square for a migration that renames item identifiers.
3. Model three kinds of missing supplier-certificate data without one undifferentiated null.
4. Use a pullback to formulate “all consumed lots had a valid certificate at consumption time.”
5. Describe a database update that is not naturally modeled as a total natural transformation.

# Schema Mappings and Functorial Data Migration

## Schema mappings as functors

A schema mapping from category $C$ to category $D$ is a functor

$$
  F : C \to D.
$$

It maps objects to objects and arrows to arrows or paths while preserving identities, composition, and declared equations. A functor is stronger than a table mapping because it preserves derivations.

If a source path “material actual -> lot -> definition” equals “material actual -> recorded definition,” the image paths in the target must also agree.

## Three canonical migrations

Given a functor $F : C \to D$, categorical database theory supplies, under suitable conditions, three migration functors:

$$
  \Sigma_F \dashv \Delta_F \dashv \Pi_F.
$$

- `Delta_F` pulls a `D`-instance back to a `C`-instance by precomposition.
- `Sigma_F` is a left pushforward that tends to merge or freely add target-side data.
- `Pi_F` is a right pushforward that tends to construct compatible target records.

The adjunctions encode universal properties, which give predictable composition and comparison laws.

## Reading the migrations operationally

Suppose `C` is a plant-local material schema and `D` a corporate material schema.

- `Delta_F` can view corporate data through the local vocabulary.
- `Sigma_F` can migrate local data upward while coalescing according to the mapping.
- `Pi_F` can derive target records satisfying all source-side compatibility requirements.

These descriptions are schematic. Real implementations must account for partiality, keys, constraints, time, and evidence. The categorical formulation tells us what ideal behavior to approximate or verify.

## Mapping quality

A mapping should be evaluated along several dimensions:

| Property | Integration interpretation |
|---|---|
| type preserving | concepts are sent to concepts of the right semantic kind |
| equation preserving | source derivations remain valid in the target |
| faithful | distinct source arrows are not silently collapsed |
| full | relevant target arrows between mapped objects are represented |
| essentially surjective | target scope is covered up to isomorphism |
| invertible on scope | a certified equivalence exists for a refined domain |

Most enterprise mappings are not full equivalences. A directed interpretation can still be correct and useful.

## Direct and indirect mappings

Assume mappings:

```text
ERP -> PLM -> MES
ERP --------> MES
```

The design should state whether the direct mapping equals the composite. In ordinary category theory the condition is a commuting triangle:

$$
  F_{EM} = F_{PM} \circ F_{EP}.
$$

In data, this yields a reconciliation query. In Part III, the equality is refined to path-valued coherence that can retain multiple witnesses.

## Transformation specifications versus implementations

Separate a mapping's semantic specification from its executable implementation:

```text
semantic mapping: typed functor plus laws
implementation: SQL, ETL, service adapter, stream processor
conformance: proof or generated tests that implementation realizes mapping
```

This separation allows implementations to change without changing meaning. It also makes a mapping registry more than a list of endpoints.

## Round-trip laws

Two adapters

$$
  f : A \to B,
  \qquad
  g : B \to A
$$

form an equivalence only if round-trip laws hold on the declared domains:

$$
  g(f(a)) = a,\qquad f(g(b)) = b.
$$

Often the second law must use normalization:

$$
  f(g(b)) = \mathsf{normalize}(b).
$$

Then the equivalence is between `A` and the normalized subspace of `B`, not all of `B`.

## Exercises

1. Define a functor from an ERP item schema to a smaller reporting schema.
2. Give an example where the functor is not faithful because two relation kinds are collapsed.
3. Describe `Delta`, `Sigma`, and `Pi` for a plant-to-corporate classification mapping.
4. State a commuting triangle for a PLM-ERP-MES material mapping.
5. Refine a lossy mapping until a round-trip equivalence becomes true.

# Ontology Merging by Colimits

## Why merging is not union

Combining schemas by union preserves names but says nothing about shared meaning. Combining rows by identifier equality assumes the identity policy before it has been modeled. A semantic merge must specify the overlap.

Let `A` and `B` be local ontologies and `K` a shared interface with functors

$$
  K \xrightarrow{f} A,
  \qquad
  K \xrightarrow{g} B.
$$

The pushout

$$
  A \sqcup_K B
$$

glues `A` and `B` along the correspondences declared by `K`.

## The overlap as a treaty

The overlap ontology should be small and explicit. For PLM and ERP it might include:

```text
ProductDefinition
ReleasedProductRevision
QuantityDimension
EffectivityContext
```

It should not include every PLM document field or every ERP valuation field. `K` is a treaty about common semantics, not a replacement for either local theory.

## Universal property

The pushout has the property that any pair of maps from `A` and `B` into a target `X` that agree on `K` factors uniquely through the merge.

Operationally, a consumer of a merged ontology must provide:

1. an interpretation of `A`;
2. an interpretation of `B`;
3. evidence that both interpretations agree on the overlap.

The universal property turns “respect the mapping” into a precise contract.

## Conflicts as failures to glue

Suppose the PLM-to-MES route maps ERP item `4711` to `M-91`, while the direct ERP-to-MES mapping yields `M-82`. The merge should not guess. It should expose a conflict:

```text
same source
same intended semantic target type
different target values
no approved equivalence or coherence witness
```

The absence of a required filler is an integration finding.

## Iterated pushouts and larger diagrams

A federation of PLM, ERP, MES, QMS, and EAM can be built by repeated pushouts, but the order can obscure multiway overlap. A general colimit over a diagram records the complete gluing shape. Part III replaces ordinary colimits with homotopy colimits when identification witnesses and coherence must be retained.

## Merging data instances

Schema pushouts and data merges are separate. After constructing a merged schema, source instances must migrate into it. Duplicate resolution, conflict policies, provenance, and temporal scope affect the data-level colimit.

A sound process therefore distinguishes:

```text
schema alignment
schema merge
instance migration
entity resolution
conflict adjudication
operational projection
```

Conflating these stages makes errors difficult to explain.

## Standards as source ontologies

Industrial standards are valuable source theories:

- ISA-95 / IEC 62264 for enterprise-control integration, materials, equipment, physical assets, job orders, and actuals;
- ISO 10303-242 for product definitions, configurations, assemblies, documents, and model-based engineering;
- Asset Administration Shell for standardized digital-twin presentations, semantic identifiers, submodels, and APIs;
- ISO 15926 for process-plant lifecycle information and reference data;
- GS1 EPCIS for visibility events and traceability.

A company ontology should align versioned fragments. It should not combine every standard into one indiscriminate master model. Different standards intentionally organize different viewpoints.

## Exercises

1. Propose a minimal overlap ontology between PLM and ERP for product revisions.
2. Identify a concept that should remain local to each side of the pushout.
3. State the universal property of the merge in operational terms.
4. Design a conflict record for two incompatible material mappings.
5. Explain why importing all concepts from two standards is not the same as a semantic pushout.

# Time, Provenance, Revision, and Industrial Identity

## Identity changes with the question

Industrial entities have multiple legitimate identity criteria. A product definition persists across revisions. A revision is fixed under a change-control policy. A lot groups physical material under a production or procurement event. A serialized unit has a lifecycle identity. A functional position persists when the occupying asset changes.

The question “is this the same?” must therefore identify a type and context.

## Valid time and transaction time

A bitemporal model distinguishes:

- **valid time**: when a claim applies in the modeled world;
- **transaction time**: when the system stored or knew the claim.

A correction may change transaction-time history without changing what was valid at the earlier physical time. Alignment claims need both dimensions when audits reconstruct past decisions.

```lean
structure Interval where
  from : Nat
  to   : Option Nat

structure Bitemporal where
  valid : Interval
  recorded : Interval
```

## Revisions and effectivity

A revision identifier alone may not determine applicable content. Effectivity can depend on date, serial range, plant, customer option, regulatory regime, or production order.

Model applicability as a predicate or evidence type:

$$
  \mathsf{EffectiveFor}(r,c,t) : \mathsf{Type}
$$

rather than a Boolean field without explanation. A query that cannot establish effectivity should return an explicit ambiguity.

## Functional position versus physical asset

ISA-95-derived models distinguish logical equipment from physical assets. EAM adds functional locations or positions. A position can remain stable while a physical device is replaced.

For Asterion:

```text
S-1044 installed at FP-CP-4 during I1
S-2088 installed at FP-CP-4 during I2
```

No equality follows between the serials or between either serial and the position. The occupancy relation is temporal and directed.

## Provenance as evidence-bearing claims

A cross-system alignment should carry:

```text
source and target references
relation kind
scope and validity
mapping rule version
authority
supporting documents or observations
approval status
confidence if provisional
supersession history
```

A proof that a relation is logically admissible does not replace this business evidence. The proof can certify the shape of the claim; the evidence justifies its use in a specific enterprise context.

## Alias, merge, and replacement

Three frequently confused operations are:

- **alias**: two identifiers denote the same entity under one identity policy;
- **merge**: the enterprise decides to consolidate records or entities, often with retained history;
- **replacement**: one physical or functional participant succeeds another without identity.

A customer master-data merge may be reversible during adjudication. A component replacement is not an alias. An item-code renaming may create an alias interval while preserving both code histories.

## Event identity

An event is not only a timestamped row. Its identity may include event type, source, sequence, subject, and causal context. Duplicate ingestion should be distinguished from repeated real-world events.

A traceability ontology should therefore separate:

```text
physical occurrence
reported event
message envelope
processing attempt
corrective event
```

EPCIS-like event vocabularies are useful here, but local identity and correction policies remain necessary.

## Exercises

1. Model a revision effectivity rule involving plant and serial range.
2. Give an example where valid time and transaction time disagree.
3. Distinguish alias, merge, and replacement for an equipment-maintenance scenario.
4. Design an evidence record for a cross-system product identity claim.
5. Explain why an event-store message ID is not automatically the identity of the physical event reported.

# Case Study: Product-to-Asset Digital Thread

## The five local ontologies

Asterion models five bounded contexts:

```text
P = PLM ontology
E = ERP ontology
M = MES ontology
Q = QMS ontology
A = EAM ontology
```

Each contains its own objects, arrows, equations, and instances.

### PLM

```text
ProductDefinition
ProductRevision
AssemblyOccurrence
SpecificationCharacteristic
DocumentRevision
```

### ERP

```text
Item
PlantItem
BOMAlternative
ProductionOrder
MaterialReservation
PurchaseOrderLine
```

### MES

```text
MaterialDefinition
MaterialLot
SerializedUnit
JobOrder
WorkExecution
MaterialActual
EquipmentActual
```

### QMS

```text
InspectionPlan
InspectionCharacteristic
InspectionExecution
MeasurementResult
Nonconformance
ReleaseDecision
```

### EAM

```text
FunctionalPosition
MaintainableAsset
InstallationEpisode
MaintenanceOrder
ReplacementEvent
```

## Core distinctions

The case depends on preserving these non-equalities:

```text
ProductDefinition != ProductRevision
ProductRevision != ERP Item
MaterialDefinition != MaterialLot
Requirement != Actual
SerializedUnit != AssetRecord
PhysicalAsset != FunctionalPosition
InspectionSpecification != MeasurementResult
AsBuiltConfiguration != AsMaintainedConfiguration
```

Mappings connect the concepts, but most connections are directed relations rather than identities.

## Overlap interfaces

Asterion defines four small overlap ontologies:

```text
K_PE  released product semantics shared by PLM and ERP
K_EM  planned material and order semantics shared by ERP and MES
K_PQ  specification semantics shared by PLM and QMS
K_MA  physical-unit and equipment-role semantics shared by MES and EAM
```

Each overlap has functors into its neighboring local ontologies. The full federation diagram is the design object; a “canonical asset table” is not.

## Categorical obligations

The design records:

- path equations inside each local ontology;
- functor laws for each interpretation;
- commuting triangles for direct and indirect mappings;
- pullback conditions for compatible execution and inspection data;
- pushout interfaces for ontology merging;
- migration laws for instance transformations.

The laws become proof obligations, reconciliation queries, and integration tests.

## Example: design to production

A released PLM revision maps to an ERP engineering-controlled item under a scoped interpretation. The ERP manufacturing BOM maps to MES material requirements. Actual material lots satisfy requirements but are not identified with them.

A genealogy path is therefore a composite of different relation kinds:

```text
SerializedUnit
  <- producedBy - WorkExecution
  <- consumedIn - MaterialActual
  -> lot - MaterialLot
  -> definition - MaterialDefinition
  <- interprets - ERP PlantItem
  <- plannedFrom - PLM ProductRevision
```

The query engine must preserve the types and evidence at every step.

## Example: quality coherence

A PLM specification characteristic maps to a QMS inspection characteristic and to an MES operation parameter. The two routes should agree on dimension, nominal value, tolerance semantics, and effectivity. A commuting square catches a job that inspects the wrong characteristic revision.

## Example: installed configuration

The MES serial is aligned with the physical-unit referent represented by an EAM asset record. An installation episode connects that unit to a functional position. Replacement creates a new episode and an updated as-maintained configuration while preserving the original as-built history.

## Deliverables of Part I

The categorical phase produces:

```text
local ontology specifications
relation-kind catalog
identity-policy catalog
overlap ontologies
mapping functors
commuting-diagram obligations
instance migration plans
conflict taxonomy
competency-question suite
```

Part II now internalizes selected invariants in Lean. Part III enriches the identity and coherence layer with higher paths.

## Exercises

1. Add a supplier ontology to the diagram and define a minimal overlap with ERP and PLM.
2. Draw a commuting square for a specification characteristic shared by PLM, MES, and QMS.
3. Identify which arrows in the genealogy path are functional and which require reified occurrence types.
4. State a pullback that combines installation episodes with alarm events at the same functional position and time.
5. List three conflicts the categorical model should report rather than auto-resolve.
EOF
wc -w -l /mnt/data/erp_ontology_book_work/theory_of_erp_system_ontologies.md
```

Parts II and III are complete, covering indexed evidence, univalence, higher coherence, homotopy pushouts, and truncation. A rendering reset requires rebuilding both editions and rerunning PDF preflight.

<details><summary>💭 Thinking</summary>

**Completed, validated, and cleaned the ERP ontology manuscript PDF deliverables**

</details>

```json
{"paths":["GitHub"],"query":"release"}
```

```json
{"paths":["GitHub"],"query":"contents"}
```

# Theory of ERP System Ontologies

The first working edition is complete: **37,977 words, 26 chapters, 6 appendices, and a 186-page PDF**.

The structure follows the requested progression:

- **Part I — Categories and Local Industrial Ontologies:** categorical schemas, ologs, set-valued instances, functorial data migration, pushout-based ontology merging, standards alignment, and a Lean 4 categorical laboratory.
- **Part II — Dependent Types and Executable Domain Theories:** indexed industrial identity, evidence-bearing relations, temporal validity, workflow states, dimensional quantities, configurations, proof-carrying traceability, migrations, and API extraction.
- **Part III — Homotopy Type Theory as the Organizing Structure:** identity as paths, univalence, homotopy pushouts, higher coherence, semantic holonomy, truncation boundaries, theory change, an ERP ontology calculus, an end-to-end PLM–ERP–MES–EAM–QMS case study, and the architecture of a HoTT-oriented ontology engine.

It also includes a Lean 4 guide, consolidated ontology model skeleton, formalization workshop, exercises with selected solutions, glossary, and bibliography. The Lean fragments are pedagogical and written in current Lean 4 style; they are not represented as a single version-pinned, compiled repository.

- [Download the Markdown textbook](sandbox:/mnt/data/theory_of_erp_system_ontologies.md)
- [Download the PDF textbook](sandbox:/mnt/data/theory_of_erp_system_ontologies.pdf)

