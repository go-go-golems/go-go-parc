# Go software proof architecture

- URL: https://chatgpt.com/c/6a78c8c3-f498-83ea-9ecf-5cae144a8101
- Created: 2026-08-09T18:37:58.506Z

---

> I want to prove certain properties about a software design i am working on, but the software is in go, so i was thinking that maybe we can prove things on a denotational semantic of go, and then use some code generation / cross compilation to turn some / all of the proof code into ast/static analysis tools for golang linting. It's not perfect probably, but it allows bridging significant gaps.

Yes. The useful way to think about this is **not** “prove Go itself, then somehow export the proof,” but to build a small verified semantic layer whose abstractions are deliberately chosen so they can also be computed over real Go programs. That gives you one semantics for proofs and one executable abstraction for linting.

```json
{"system1_search_query":[{"q":"site:go.dev/ref/spec Go language specification semantics statements memory model"},{"q":"site:go.dev/s/go11func go analysis API golang.org/x/tools/go/analysis official"},{"q":"site:viperproject.github.io Gobra Go verifier official"},{"q":"site:github.com viperproject gobra verifier Go official"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Searched 6 websites**

</details>

The key mathematical bridge is **abstract interpretation**: prove properties over a concrete/core semantics, then prove that a computable abstract semantics safely over-approximates it. The abstract semantics is almost exactly what your linter wants to execute. This avoids having two unrelated artifacts called “the proof” and “the analyzer.”

```json
{"system2_search_query":[{"q":"site:lean-lang.org Lean 4 code generation compiler executable official"},{"q":"site:lean-lang.org/doc/reference/latest Lean compiler code generation executable"},{"q":"site:lean-lang.org/doc/reference/latest FFI extern Lean 4"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Designing the verification path**

I’m comparing direct Go verification, a Lean-defined intermediate model, and generation from specifications. A hybrid seems strongest: prove protocol invariants in Lean, then validate Go implementations through a sound abstraction and repository-level analyzer.

**Designed the verification path**

**Searched 1 website**

</details>

Yes. I think this can be made into a fairly principled architecture, and there is an important refinement of your idea:

> **Do not try to formalize all of Go first. Formalize the semantic fragment needed to express your software design, prove an executable abstract interpreter for that fragment sound, and make the Go linter an implementation of that abstract interpreter.**

That turns the gap between theorem proving and ordinary static analysis into an explicit mathematical object rather than an informal translation.

Go is unusually amenable to this because its official tooling already exposes typed ASTs and an SSA representation intended for program analysis. `golang.org/x/tools/go/analysis` gives analyzers syntax trees, type information, source positions, and inter-package facts; `x/tools/go/ssa` gives you a typed SSA IR for function bodies. citeturn653244search2turn653244search1

## 1. I would use three semantic levels

Something like:

```text
                    Go source
                       │
                       │ parse / typecheck / SSA
                       ▼
              ┌──────────────────┐
              │   Concrete Go IR │
              │ AST / x/tools SSA│
              └────────┬─────────┘
                       │
                  extraction E
                       │
                       ▼
              ┌──────────────────┐
              │      CoreGo      │
              │ formal language  │
              └────────┬─────────┘
                       │
              concrete semantics
                       │
                       ▼
              ┌──────────────────┐
              │ semantic states  │
              │ traces / heaps / │
              │ effects / etc.   │
              └────────┬─────────┘
                       │ α
                       ▼
              ┌──────────────────┐
              │ Abstract domain  │
              │ used by analyzer │
              └────────┬─────────┘
                       │
                executable Lean
                       │
                       ▼
                  diagnostics
```

And there are different proof obligations at the two arrows.

The second arrow — **concrete semantics → abstract semantics** — is where formal methods are extremely good.

The first arrow — **real Go → CoreGo** — is the awkward engineering boundary.

That is fine. You don't have to pretend it isn't there.

---

# 2. CoreGo should not initially be "Go formalized"

Suppose your software contains things like:

```go
type Conn struct { ... }

func (c *Conn) Begin() *Tx
func (t *Tx) Commit()
func (t *Tx) Rollback()
```

and your design property is:

> Every transaction is eventually either committed or rolled back, and nothing may use a transaction after either operation.

You do **not** need a denotation for every feature of Go.

Your formal language might have only:

```lean
inductive Expr
  | call      : Var → Method → List Var → Expr
  | assign    : Var → Expr → Expr
  | branch    : Expr → Block → Block → Expr
  | return_   : Option Var → Expr
  | defer_    : Expr → Expr
  | ...
```

plus some semantic events:

```lean
inductive Event
  | begin    : TxId → Event
  | use      : TxId → Event
  | commit   : TxId → Event
  | rollback : TxId → Event
```

The denotation of a function can then be something like:

\[
\llbracket f \rrbracket :
\Sigma \to \mathcal P(\mathrm{Trace}\times\Sigma)
\]

rather than simply

\[
\Sigma\to\Sigma.
\]

The powerset is important because real programs introduce nondeterminism through control flow, external inputs, concurrency, etc.

Your property becomes a predicate over traces:

\[
Safe : Trace \to Prop.
\]

For example:

\[
\forall t,\;
Commit(t) \implies
\neg EventuallyAfter(Use(t), Commit(t))
\]

and similarly for rollback.

This is already enough to formalize many **architectural** properties.

---

# 3. Then abstract interpretation gives you the linter

This is the part I think most closely matches what you're imagining.

The concrete semantics might track:

```text
all allocated transactions
exact program state
heap
call stack
exact execution trace
...
```

Obviously a linter can't enumerate all of those.

Instead define an abstract state:

```lean
inductive TxState
  | uninit
  | active
  | closed
  | unknown

structure AbsState where
  txs : Var → TxState
```

Then:

```text
Begin:
    x ↦ active

Commit(x):
    active ↦ closed

Rollback(x):
    active ↦ closed

Use(x):
    closed → ERROR
```

Now you're doing abstract interpretation.

Mathematically, introduce:

\[
C
\]

for concrete states and

\[
A
\]

for abstract states, with abstraction/concretization maps

\[
\alpha:C\to A
\]

and

\[
\gamma:A\to\mathcal P(C).
\]

Ideally these form a Galois connection:

\[
\alpha(c)\sqsubseteq a
\quad\Longleftrightarrow\quad
c\in\gamma(a).
\]

Your concrete transition is

\[
F:C\to\mathcal P(C)
\]

and your executable static-analysis transfer function is

\[
F^\#:A\to A.
\]

The crucial theorem is:

\[
\alpha(F(c))
\sqsubseteq
F^\#(\alpha(c)).
\]

Or, in concretization form,

\[
F(\gamma(a))
\subseteq
\gamma(F^\#(a)).
\]

This little theorem is essentially the **semantic contract of the linter**.

It says:

> Whenever the concrete program can move somewhere, the abstract analyzer includes that possibility.

So your analyzer may produce false positives, but it cannot silently exclude a behavior relevant to the property you have proved.

That's the bridge you're looking for.

---

# 4. And now something very nice happens in Lean

You can define:

```lean
def transfer : Instr → AbsState → AbsState
```

as an ordinary computable Lean function.

And separately prove:

```lean
theorem transfer_sound :
  ∀ i c a,
    abstracts c a →
    step i c c' →
    abstracts c' (transfer i a)
```

The function isn't merely related to the proof.

**The function being proved correct is the analyzer.**

You have:

```text
                Lean definition

                  transfer
                 /        \
                /          \
       executable code      theorem
              │               │
              │               │
              ▼               ▼
            linter       transfer_sound
```

This is much stronger than:

```text
write theorem
     ↓
understand theorem
     ↓
manually rewrite it in Go
```

Lean is itself a compiled programming language; current Lean compiles executable definitions to native code through generated C, and exposes a C ABI for interoperability. citeturn375713search1turn375713search0

So initially I would **not transpile Lean to Go at all**.

Compile the checker.

Have a tiny Go `go/analysis.Analyzer` adapter invoke it.

That removes an entire correctness problem.

---

# 5. There are actually two different things worth proving

This distinction matters.

### A. Software-design theorem

For example:

\[
WellFormed(System)
\implies
NoCircularDependencies(System)
\]

or

\[
ProtocolConformant(System)
\implies
NoUseAfterClose(System).
\]

These are mathematical statements about your design.

### B. Analyzer soundness theorem

\[
AnalyzerAccepts(program)
\implies
WellFormed(extract(program)).
\]

Put them together:

\[
AnalyzerAccepts(p)
\implies
WellFormed(E(p))
\implies
Safe(E(p)).
\]

And eventually you want:

\[
Safe(E(p))
\implies
Safe_{Go}(p).
\]

So the full chain is:

\[
\boxed{
AnalyzerAccepts(p)
\Rightarrow
ModelProperty(E(p))
\Rightarrow
SemanticSafety(E(p))
\Rightarrow
GoSafety(p)
}
\]

That final implication is your **adequacy/refinement theorem**.

This is exactly where we should spend effort carefully.

---

# 6. The nasty part is Go → CoreGo, not the proofs

Suppose:

```go
func Foo(x *Thing) {
    defer x.Close()

    if condition {
        return
    }

    x.Work()
}
```

Your extractor has to understand Go's actual `defer` behavior.

Similarly:

```go
go f()
```

introduces concurrency.

And:

```go
select {
case x := <-a:
case y := <-b:
}
```

introduces nondeterministic synchronization.

And then you have:

```go
panic
recover
interfaces
closures
generics
maps
slices
aliasing
methods
reflection
unsafe
atomics
```

The official Go language spec and memory model are the authoritative baseline; importantly, the memory model separately specifies the conditions under which values written in one goroutine may be observed by another. citeturn210285search0turn210285search3

Trying to denotationally model **all of that immediately** would probably kill the project.

Instead:

```text
CoreGo v0
    pure expressions
    structs
    methods
    calls
    branches
    loops

CoreGo v1
    pointers / alias abstraction

CoreGo v2
    defer / panic

CoreGo v3
    goroutines / channels

CoreGo v4
    atomics / memory model
```

And unsupported constructs mean:

```text
analysis result = Unknown
```

not:

```text
pretend they don't matter
```

That distinction preserves soundness.

---

# 7. There is precedent for both sides of this idea

You don't need to invent everything from scratch.

**Featherweight Go** gives a deliberately tiny formal calculus capturing important Go features including structural interfaces, and work on it has proved semantic preservation of translations using logical relations. citeturn160935academia37turn160935search8

More directly, **Gobra** already verifies Go programs by translating annotated Go into the Viper verification infrastructure. It supports modular deductive verification and targets properties including memory safety, crash safety, race freedom, and user specifications. Its theoretical basis includes separation logic. citeturn160935search30turn160935search22

So an existing route is:

```text
Go + specifications
        ↓
      Gobra
        ↓
      Viper
        ↓
        SMT
```

That may already solve some of your problems.

But your proposal is slightly different and, for **software architecture/design invariants**, potentially more interesting:

```text
               Lean

        semantic model
             │
       prove properties
             │
      abstract semantics
             │
       prove soundness
             │
        executable
             │
             ▼
Go ──→ semantic extraction ──→ analyzer
```

You're effectively constructing a **domain-specific verifier** rather than a general-purpose Go verifier.

That can be dramatically easier.

---

# 8. I would not make "Go semantics" the center of the system

I'd turn the whole thing upside down.

Suppose you are designing some system \(D\).

Define:

\[
\mathcal D
\]

as the mathematical semantics of the **design**.

For example:

```lean
structure Component where
  provides : Finset Capability
  requires : Finset Capability

structure System where
  components : Finset Component
  edges      : Component → Component → Prop
```

You prove:

```lean
theorem acyclic_implies_initializable ...
theorem capability_confinement ...
theorem ownership_unique ...
```

Then define a relation:

\[
p \models D
\]

meaning:

> Go program `p` is an implementation/refinement of design `D`.

The linter's job is primarily to establish:

\[
p\models D.
\]

This is much easier than proving arbitrary properties of Go.

Once you establish:

\[
p\models D
\]

you inherit the theorems you've proved about \(D\).

That's the big architectural leverage.

---

# 9. This is refinement

Your software implementation and model don't need to be identical.

You want a map

\[
R : GoState \to ModelState
\]

such that Go steps are simulated by model steps:

\[
g\to_G g'
\]

implies something like

\[
R(g)\to_M^*R(g').
\]

Diagrammatically:

```text
       Go state g ─────Go─────▶ g'
          │                       │
          │ R                     │ R
          ▼                       ▼
     Model state m ───Model*───▶ m'
```

You prove that this diagram commutes, perhaps modulo stuttering.

Then:

\[
Invariant_M(m)
\]

transfers back to the implementation.

This is the same general shape used in refinement proofs, compiler-correctness proofs, protocol verification, distributed systems verification, etc.

---

# 10. Your static analyzer is itself an abstraction of that refinement relation

There's another layer:

```text
            REAL EXECUTION

           Go operational state
                  │
             abstraction
                  ▼

             MODEL STATE
                  │
             abstraction
                  ▼

          ANALYSIS DOMAIN
```

So perhaps:

\[
G \xrightarrow{\rho} M \xrightarrow{\alpha} A
\]

where:

- \(G\) = Go runtime semantics
- \(M\) = your design semantics
- \(A\) = finite static-analysis lattice.

Then your linter computes over \(A\).

This means the core mathematical architecture is:

\[
\boxed{
\text{refinement}
+
\text{abstract interpretation}
}
\]

Those two ideas fit together extremely well.

---

# 11. Category-theoretically, there is a pleasant interpretation too

Don't start the implementation here, but it clarifies the design.

Think of program fragments as morphisms.

A sequential computation

\[
f:A\to B
\]

composes with

\[
g:B\to C
\]

to give

\[
g\circ f:A\to C.
\]

Effects change the category. State computations look like Kleisli arrows:

\[
A\to State\to(B\times State).
\]

Nondeterministic computations become:

\[
A\to State\to\mathcal P(B\times State).
\]

Traced computations might be:

\[
A\to State\to\mathcal P(B\times State\times Trace).
\]

The semantics is then a compositional interpretation:

\[
\llbracket-\rrbracket :
Syntax \to Semantics.
\]

Your abstract interpreter is another interpretation:

\[
\llbracket-\rrbracket^\# :
Syntax \to AbstractSemantics.
\]

What you prove is effectively a compatibility/naturality condition:

```text
               concrete semantics
 Syntax ───────────────────────────▶ Concrete
   │                                    │
   │                                    │ α
   │                                    ▼
   └──────────────────────────────▶ Abstract
              abstract semantics
```

You want:

\[
\alpha\circ\llbracket p\rrbracket
\sqsubseteq
\llbracket p\rrbracket^\#\circ\alpha.
\]

That is a beautifully compact description of analyzer soundness.

It also tells you something practical:

> Make every syntactic construct's semantics compositional.

Then your proof decomposes by syntax.

---

# 12. We can use separation logic where Go's heap enters

As soon as your invariants say:

- this object exclusively owns that resource;
- this goroutine owns permission to modify this structure;
- calling `Close` consumes a capability;
- callers cannot alias mutable state in a certain way;

plain state predicates get unpleasant.

Separation logic gives you:

\[
P * Q
\]

meaning, informally, that \(P\) and \(Q\) hold over separable pieces of resources.

So something like:

\[
Own(x,\text{Open})
\]

can be consumed by:

\[
close(x)
\]

to produce:

\[
Own(x,\text{Closed}).
\]

This is already a major part of Gobra's approach. citeturn160935search11

For Go designs involving ownership, resource protocols, concurrency, sockets, transactions, locks, buffers, etc., I would expect this to become useful fairly quickly.

---

# 13. Concurrency deserves a separate semantic layer

I would resist putting concurrency into the first CoreGo.

Sequential Go:

\[
State\to State
\]

is comparatively manageable.

Concurrent Go is more naturally something like a labelled transition system:

\[
C \xrightarrow{e} C'
\]

where events include:

```text
spawn(g)
send(ch,v)
recv(ch,v)
lock(m)
unlock(m)
read(x,v)
write(x,v)
```

Then an execution is a trace:

\[
C_0
\xrightarrow{e_1}
C_1
\xrightarrow{e_2}
\cdots
\]

Now you can express:

- happens-before;
- race freedom;
- deadlock properties;
- channel protocols;
- ownership transfer.

The Go memory model itself specifies synchronization and visibility in happens-before terms, so you eventually have an authoritative semantics to refine against. citeturn210285search3

But I would treat that as CoreGo-Concurrent, almost a second project.

---

# 14. The coolest version is a proof-producing linter

We can go beyond a sound analyzer returning:

```text
✓ okay
```

Make it return:

```text
✓ okay
certificate: ...
```

For instance:

```lean
structure Certificate where
  states : Array AbstractState
  edges  : Array EdgeProof
```

and define:

```lean
def checkCertificate :
    Program → Certificate → Bool
```

Then prove:

\[
checkCertificate(p,c)=true
\implies
Safe(p).
\]

Now the complicated analysis can even be untrusted.

```text
                    untrusted
Go program ──▶ clever analyzer ─────────▶ certificate
     │                                      │
     │                                      ▼
     └──────────────────────────────▶ tiny checker
                                             │
                                           true
                                             │
                                             ▼
                                       theorem says
                                          SAFE
```

This is a very strong engineering pattern.

The analyzer can use:

- Go;
- graph algorithms;
- SAT;
- SMT;
- LLMs;
- heuristics;
- databases;

and none of those need to be trusted.

Only the certificate checker and its theorem matter.

For the kind of system you've been thinking about, I would seriously consider this architecture.

---

# 15. In practice I would build this repository

Something like:

```text
semgo/
│
├── lean/
│   ├── CoreGo/
│   │   ├── Syntax.lean
│   │   ├── Types.lean
│   │   ├── Semantics.lean
│   │   └── Trace.lean
│   │
│   ├── Design/
│   │   ├── Model.lean
│   │   ├── Invariants.lean
│   │   └── Theorems.lean
│   │
│   ├── Analysis/
│   │   ├── Domain.lean
│   │   ├── Transfer.lean
│   │   ├── Fixpoint.lean
│   │   └── Soundness.lean
│   │
│   └── Checker/
│       ├── Certificate.lean
│       └── Main.lean
│
├── go/
│   ├── extract/
│   │   ├── ast.go
│   │   ├── ssa.go
│   │   └── corego.go
│   │
│   ├── analyzer/
│   │   └── analyzer.go
│   │
│   └── cmd/
│       └── semgolint/
│
├── schemas/
│   └── corego.schema
│
└── test/
    ├── positive/
    └── negative/
```

The Go side uses the standard analysis framework and SSA construction. citeturn653244search2turn653244search21

---

# 16. I would make the IR language-neutral

This is important.

Don't define CoreGo as Lean constructors that only Lean knows about.

Define the conceptual schema independently:

```text
Function
BasicBlock
Instruction
Value
Type
Effect
SourceLocation
```

Then generate:

```text
schema
 ├── Go structs
 ├── Lean inductives
 ├── serializer
 └── pretty printer
```

You then get:

```text
Go source
   ↓
x/tools SSA
   ↓
CoreGo JSON/binary
   ↓
Lean checker
```

At first this means the verifier can be an external executable.

That's perfectly reasonable.

Later, if latency matters:

```text
Lean
 ↓
generated C
 ↓
C ABI
 ↓
Go/cgo
```

Lean explicitly supports exposing compiled Lean declarations through its C ABI, although its current FFI documentation warns that the interface is still evolving. citeturn375713search0

I wouldn't initially invent a Lean→Go compiler.

---

# 17. If you insist on an all-Go analyzer, use translation validation

Suppose we have proved:

```lean
def analyze : CoreGo → Result
```

and we generate:

```go
func Analyze(p CoreGo) Result
```

Now we have introduced:

\[
LeanAnalyze
\stackrel{?}{=}
GoAnalyze.
\]

Instead of proving your Lean→Go code generator correct, generate a **validator**.

For example, both produce a transfer table:

\[
T : Opcode\times AbstractState\to AbstractState.
\]

Lean emits a canonical table/specification.

Go executes the fast version.

A checker verifies the Go result satisfies the specification.

This is the classic useful distinction between:

> verified translation

and

> translation validation.

The latter is often radically cheaper.

---

# 18. This gives you different confidence levels

I would actually expose them explicitly.

```text
Level 0
ordinary Go lint rule

Level 1
linter derived from a formally specified abstract domain

Level 2
abstract transfer functions proved sound

Level 3
model property formally proved

Level 4
Go→model extraction validated

Level 5
relevant CoreGo semantics proved adequate to Go semantics
```

Then diagnostics might even say:

```text
SEM001 use-after-close

Proof coverage:
  design theorem       VERIFIED
  abstract interpreter VERIFIED
  Go extractor         TESTED
  unsafe/reflection    NOT PRESENT
```

That is much more intellectually honest than a binary label of "verified software."

---

# 19. One subtle improvement: model obligations, not just errors

Typical linters compute:

\[
Program\to List(Error).
\]

I'd make yours compute:

\[
Program\to List(Obligation).
\]

An obligation might be:

```lean
inductive Obligation
  | mustClose       : Resource → Obligation
  | mustDominate    : Node → Node → Obligation
  | mustOwn         : Value → Capability → Obligation
  | mustNotAlias    : Value → Value → Obligation
  | mustEventually  : Event → Event → Obligation
```

Then different solvers discharge them:

```text
                         ┌─ local AST solver
                         │
Go ─▶ semantics ─▶ obligations ─┼─ SSA/dataflow solver
                         │
                         ├─ SMT solver
                         │
                         └─ human proof
```

This is much closer to a theorem prover.

And it's extensible.

---

# 20. It also creates a very interesting "proof budget"

Some facts are cheaply statically decidable:

```text
package dependency DAG
interface implementation
call graph restrictions
simple ownership
dominance
```

Some require abstract interpretation:

```text
typestate
resource lifecycle
possible nil state
effect propagation
```

Some need SMT:

```text
x < len(a)
numeric invariants
relational properties
```

Some need actual proof:

```text
protocol correctness
refinement
global architectural theorem
```

So you can deliberately climb:

\[
Lint
\subset
AbstractInterpretation
\subset
SMT
\subset
InteractiveProof.
\]

And the important thing is that these don't become four unrelated systems.

They consume the **same semantic obligations**.

---

# 21. Therefore I'd slightly change your original sentence

You proposed approximately:

> prove things on a denotational semantics of Go, then cross-compile proof code into Go linting.

I'd formulate the project as:

> **Define a formal semantics for the architectural subset of Go that matters to us; prove design invariants over that semantics; derive a sound executable abstract interpretation of it; and connect real Go programs to the semantics through an SSA-based refinement/extraction layer.**

Or mathematically:

\[
\boxed{
Go
\xrightarrow{\text{extract}}
CoreGo
\xrightarrow{\llbracket-\rrbracket}
Model
\xrightarrow{\alpha}
AbstractDomain
}
\]

with proofs:

\[
\boxed{
\begin{aligned}
&\text{ModelInvariant} \Rightarrow \text{DesiredProperty}\\
&\text{AbstractAnalysis sound w.r.t. Model}\\
&\text{CoreGo extraction adequate w.r.t. relevant Go}\\
\end{aligned}
}
\]

and executable content:

\[
\boxed{
\text{Lean abstract interpreter}
\longrightarrow
\text{native checker}
\longrightarrow
\texttt{go/analysis} \text{ linter}
}
\]

That is a real formal-methods architecture rather than a hacky proof-to-lint translation.

And there's an appealing long-term progression:

```text
                  ┌───────────────────┐
                  │ Software design D │
                  └─────────┬─────────┘
                            │
                         prove
                            │
                            ▼
                    theorem corpus
                            ▲
                            │ refinement
                            │
Go source ─▶ SSA ─▶ CoreGo ─┴─▶ abstract interpretation
                                  │
                                  ▼
                            proof obligations
                              /    |     \
                           lint   SMT   certificate
```

**I think this is worth prototyping.** For the first version, I'd choose one architectural invariant from your actual Go system—something involving ownership, lifecycle, layering, or permitted transitions—and build the entire vertical slice from `go/analysis` → tiny CoreGo → Lean semantics → sound abstract analyzer → source-level diagnostic. That will tell us much more than trying to formalize Go broadly at the outset.

A very natural next step would be to take one concrete property from your software design and build that vertical slice on paper first: the mathematical model, Lean theorem shape, CoreGo instructions needed, abstract domain, and exact Go lint rule.


---

> imagine I want to give a coding agent / research agent access to lean, but they can't run it locally, so I want to run it as MCP. What tools do you think would be good (they don't have access to the remote file system, so that would be cool too maybe)

I’d design this as a **remote Lean workbench**, not merely “run `lean` over MCP.” The key is to expose proof-state, project/file, search, and build operations at the right semantic level so an agent can iterate without needing shell or filesystem access.

```json
{"system2_search_query":[{"q":"site:lean-lang.org Lean 4 language reference server LSP diagnostics InfoTree official"},{"q":"site:lean-lang.org Lean 4 Lake build project official documentation"},{"q":"site:leanprover-community.github.io mathlib4 documentation search declarations Lean official-ish"},{"q":"site:github.com/leanprover/lean4 Language Server Protocol Lean 4 repository"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Searched 3 websites**

</details>

A second design decision matters: **the remote filesystem should be versioned/transactional**. Proof agents make lots of speculative edits; “apply patch → check Lean → inspect goals → revert/commit” should be a first-class operation, not a sequence of fragile raw filesystem writes.

```json
{"system2_search_query":[{"q":"site:modelcontextprotocol.io specification tools resources prompts MCP official resources filesystem"},{"q":"site:modelcontextprotocol.io docs tools resources Model Context Protocol official"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Designing the interface**

I’m separating workspace operations, semantic Lean feedback, proof experiments, and project discovery. The core principle is to expose structured edits and diagnostics, not shell commands, while preserving reproducibility and clear failure states.

**Designed the interface**

**Searched 8 websites**

</details>

Yes. I would expose something closer to a **remote theorem-proving IDE + transactional workspace** than a remote `lean` command.

Lean already has most of the machinery you want behind its language server: diagnostics, source information, request handlers, goal-state visualization, references, etc. Lean's server architecture explicitly supports custom LSP handlers for interactive-theorem-proving functionality. citeturn288132search0turn288132search1 Lake also provides project-aware builds and runs the Lean language server in the package environment. citeturn975344search2turn975344search34

I would divide the MCP surface into four layers.

### 1. Remote workspace

This is more important than it initially looks. The agent needs a persistent working copy, but I would **not** expose arbitrary filesystem access. Give it a project-scoped virtual filesystem with snapshots.

| Tool | Purpose |
|---|---|
| `workspace.info` | Lean version, toolchain, Lake package, dependencies, current snapshot |
| `fs.tree` | Directory tree, optionally depth/glob filtered |
| `fs.read` | Read file/range |
| `fs.search` | Regex/text search across project |
| `fs.glob` | Find files |
| `fs.patch` | Apply unified/structured patch |
| `fs.write` | Create/replace file; less preferred than patch |
| `fs.mkdir` / `fs.delete` / `fs.move` | Normal file operations |
| `workspace.snapshot` | Create immutable checkpoint |
| `workspace.diff` | Diff current state against checkpoint |
| `workspace.restore` | Roll back experiments |
| `workspace.commit` | Name a successful state |

MCP Resources are actually a natural way to expose read-only files: resources have URIs and can represent files/directories, while MCP tools are intended for model-controlled actions such as writes. citeturn866437search0turn866437search2

So you could have:

```text
lean-workspace://project/Core/Semantics.lean
lean-workspace://project/lakefile.toml
lean-workspace://project/lean-toolchain
```

as resources, while edits remain tools.

The critical mutation interface would be something like:

```text
fs.patch(
  path,
  expected_revision,
  patch
)
```

returning:

```text
new_revision
diff
affected_files
```

The revision check prevents an agent from accidentally editing stale content.

---

## 2. Lean semantic/IDE tools

I would make these the main interface, rather than requiring the agent to edit a file and then call `lake build` after every change.

```text
lean.check_file
lean.goal_at
lean.hover
lean.complete
lean.definition
lean.references
lean.document_symbols
```

### `lean.check_file`

This should be the workhorse:

```text
lean.check_file({
  path: "Foo.lean"
})
```

return:

```text
status: "error"

diagnostics:
  - severity: error
    range: ...
    message: "type mismatch ..."

goals:
  - position: ...
    goal:
      context:
        - "α : Type"
        - "xs : List α"
      target: "List.reverse (List.reverse xs) = xs"

sorries:
  - range: ...

processing:
  complete: true
```

Don't just return stderr.

The agent needs **structured goals and diagnostics**.

Recent Lean versions even distinguish server-side diagnostics for unsolved goals and successfully completed propositions, which is exactly the sort of semantic signal an agent-facing API should preserve. citeturn975344search29

### `lean.goal_at`

This is probably the single most valuable tool:

```text
lean.goal_at({
  path,
  line,
  column
})
```

returns:

```text
goals:
  - hypotheses:
      n: Nat
      h: n > 0
    target:
      ∃ k, n = k + 1
```

The agent should not have to reconstruct this from compiler text.

### `lean.hover`

For:

```lean
List.map
Nat.rec
CategoryStruct.comp
```

return:

```text
fullyQualifiedName
type
docstring
sourceLocation
module
```

### `lean.definition`

Given a symbol, return its declaration and optionally the source surrounding it.

### `lean.references`

Particularly useful for research agents navigating an unfamiliar formalization. Lean already has server-side reference machinery over elaboration information. citeturn975344search38

---

# 3. Make proof experimentation a first-class API

This is where I would diverge substantially from ordinary editor MCPs.

Agents repeatedly want to ask:

> What happens if I try `simp [foo]` here?

It is wasteful to mutate the real file for that.

Give them:

```text
lean.try_tactic
```

For example:

```text
lean.try_tactic({
  path: "Proof.lean",
  position: { line: 83, column: 4 },
  tactic: "simp [List.reverse_reverse]"
})
```

return:

```text
success: true

before:
  ⊢ reverse (reverse xs) = xs

after:
  noGoals: true

messages: []
```

Or:

```text
success: true

before:
  ⊢ a + b + c = a + (b + c)

after:
  goals:
    - ⊢ ...
```

This becomes the agent equivalent of typing tactics into the Lean infoview.

Even better:

```text
lean.try_tactics({
  ...
  candidates: [
    "simp",
    "aesop",
    "omega",
    "constructor",
    "exact foo"
  ]
})
```

return each resulting goal state.

That is vastly more token-efficient than five edit/check/revert cycles.

I would also add:

```text
lean.try_term
```

so the agent can test:

```lean
fun x => ...
by
  ...
Foo.bar h
```

against the expected type of a hole.

---

# 4. Add an overlay filesystem

This is the feature I'd prioritize most highly after `goal_at`.

Let every semantic Lean operation accept an optional **overlay**:

```text
lean.check({
  path: "Foo.lean",

  overlay: {
    "Foo.lean": {
      patches: [...]
    }
  }
})
```

The files on disk remain untouched.

Conceptually:

```text
              persistent workspace
                       │
                       ▼
                 snapshot S₀
                       │
                 temporary patch
                       │
                       ▼
                 overlay S₁
                       │
              Lean elaboration
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
          success              failure
             │
          commit
             │
             ▼
       persistent S₁
```

That means an agent can search an entire proof tree without polluting the actual repository.

You could even expose:

```text
workspace.fork(snapshot)
workspace.merge(fork)
workspace.discard(fork)
```

for research agents running multiple strategies concurrently.

---

# 5. Declaration/library search needs to be much better than grep

A proof agent constantly asks:

> Is there already a theorem saying this?

So I'd expose a semantic declaration index.

```text
lean.search_declarations
```

Queries could support:

```text
name: "reverse"
text: "bijective"
module: "Mathlib.CategoryTheory"
```

But much more importantly:

```text
lean.search_type({
  pattern:
    "?f (?f ?x) = ?x"
})
```

or:

```text
lean.search_type({
  target:
    "Function.Injective f → ..."
})
```

And:

```text
lean.inspect_declaration({
  name: "List.reverse_reverse"
})
```

return:

```text
name
kind
type
universeParameters
implicitArguments
docstring
attributes
module
sourceLocation
dependencies
```

Mathlib itself exposes facilities such as `#find`/type search, so you can build on existing Lean-side machinery rather than implementing semantic matching outside Lean. citeturn975344search21

I'd probably have:

```text
lean.search_text
lean.search_name
lean.search_type
lean.inspect_decl
```

rather than one enormous search operation.

---

# 6. Give the agent a cheap "scratch Lean" environment

Something like:

```text
lean.scratch({
  imports: ["Mathlib"],
  code: """
    #check ...
    example ... := by
      ...
  """
})
```

This should create an ephemeral module with the project's exact dependency environment.

Return diagnostics, goals, and command output.

This lets the research agent test questions without creating `Scratch.lean`.

Lean's command layer already supports things like `#eval`; `#eval` can even run computations in Lean metaprogramming monads such as `MetaM` and `TermElabM` in the current elaboration environment. citeturn288132search3

I'd additionally support semantic operations directly:

```text
lean.check_term
lean.infer_type
lean.synth_instance
lean.reduce
lean.eval
```

So instead of writing:

```lean
#check Foo
#synth Group G
#reduce expression
```

the agent can ask structured questions.

---

# 7. Have a dedicated proof-completion check

Agents are prone to declaring victory because the file "compiles."

Give them:

```text
lean.verify
```

with:

```text
lean.verify({
  path: "Foo.lean",
  policy: {
    noErrors: true,
    noSorries: true,
    noUnsolvedGoals: true
  }
})
```

return:

```text
verified: true

theorems:
  Foo.bar:
    compiled: true
    containsSorry: false
    goalsRemaining: 0
```

This should be the authoritative completion criterion for your agent harness.

---

# 8. Project/build tools remain useful

I'd expose Lake, but in a constrained form:

```text
project.build
project.test
project.targets
project.dependencies
project.clean
```

rather than:

```text
shell("lake build && rm -rf ...")
```

Lake is already the project-aware layer that tracks Lean build dependencies and configures the project environment. citeturn975344search19turn975344search2

`project.build` should return diagnostics grouped by module rather than dumping terminal output.

And I'd make it possible to build one target/module:

```text
project.build({
  target: "MyProject.Semantics"
})
```

---

# 9. I would still include an escape hatch

Eventually the high-level API won't expose something a research agent needs.

So provide:

```text
lean.lsp_request
```

but perhaps only in an "advanced" capability set.

Something like:

```text
lean.lsp_request({
  method: "$/lean/rpc/call",
  params: ...
})
```

Likewise, perhaps:

```text
project.run_lake_script
```

for explicitly permitted Lake scripts.

I would **not** expose unrestricted remote shell by default.

The difference is:

```text
shell(command: string)
```

has effectively unbounded semantics.

Whereas:

```text
project.build(target)
lean.try_tactic(...)
fs.patch(...)
```

are narrow enough that:

- permissions are understandable;
- results are structured;
- operations can be audited;
- caching becomes possible;
- timeouts are meaningful;
- a malicious Lean project has less ambient authority.

---

# 10. A particularly useful tool: `lean.explain_failure`

This wouldn't necessarily use an LLM server-side.

It would aggregate semantic information:

```text
lean.explain_failure({
  path,
  diagnosticId
})
```

return:

```text
diagnostic
expectedType
actualType

relevantGoal

expression:
  elaboratedForm
  inferredType

candidateDeclarations:
  ...

sourceContext:
  ...
```

So when Lean says something terse, the client agent receives everything necessary to reason about it.

It should be **information extraction**, not another chatbot.

---

# 11. Another extremely useful one: proof-state delta

Instead of repeatedly returning a 3,000-token goal context:

```text
lean.try_tactic(...)
```

can return:

```text
goalDelta:
  removedHypotheses: []
  addedHypotheses:
    - h : P
  oldTarget:
    P ∧ Q
  newTarget:
    Q
```

This matters enormously for agent context efficiency.

With persistent IDs:

```text
goalId: g92
parentGoalId: g81
```

you effectively get:

```text
                    g₀
                  ⊢ P ∧ Q
                    │
             constructor
               /          \
             g₁            g₂
            ⊢ P           ⊢ Q
             │
           exact h
             │
             ✓
```

Now your theorem-proving agent can reason over an explicit **proof-search graph** rather than piles of source text.

That opens up some much more interesting architectures later.

---

# 12. You could expose theorem proving as state transitions

At the lowest semantic level, I'd actually like an API like:

```text
proof.start
proof.apply
proof.inspect
proof.clone
proof.undo
proof.finish
```

For example:

```text
proof.start({
  imports: ["Mathlib"],
  theorem:
    "∀ n : Nat, n + 0 = n"
})
```

returns:

```text
proofId: "p17"
stateId: "s0"

goals:
  g0:
    ⊢ ∀ n : Nat, n + 0 = n
```

then:

```text
proof.apply({
  stateId: "s0",
  tactic: "intro n"
})
```

returns:

```text
stateId: "s1"

goals:
  g1:
    n : Nat
    ⊢ n + 0 = n
```

then:

```text
proof.apply({
  stateId: "s1",
  tactic: "simp"
})
```

→

```text
stateId: "s2"
goals: []
```

This is much closer to what reinforcement-learning/theorem-search systems want.

There is already an interesting project in this direction: **Pantograph**, hosted under the Lean organization, describes itself as a machine-to-machine interaction system for Lean 4. citeturn188366search7turn188366search16

I'd study that interface carefully.

---

# 13. So I would actually have two APIs

For a **coding agent**:

```text
fs.read
fs.search
fs.patch

lean.check_file
lean.goal_at
lean.try_tactic
lean.hover
lean.definition
lean.search_type

project.build
lean.verify
```

For a **theorem-research/search agent**:

```text
proof.start
proof.inspect
proof.apply
proof.clone
proof.undo

lean.search_type
lean.inspect_decl

proof.finish
```

They can live on the same MCP server, but they're conceptually different.

The first thinks in terms of **source files**.

The second thinks in terms of:

\[
\text{proof state}
\xrightarrow{\text{tactic}}
\text{proof state}.
\]

That distinction becomes very powerful.

---

# 14. Existing Lean MCP work is worth stealing ideas from

There are already at least a couple of active projects doing versions of this. `lean-lsp-mcp` wraps Lean's LSP for MCP-based agent interaction, and LeanCTX advertises a much broader MCP-only interface including remote project operations. citeturn188366search2turn188366search0

I wouldn't necessarily adopt their API wholesale, but I'd inspect them before designing yours.

The architectural difference I'd push hardest is:

```text
existing-ish approach

Agent
  │
  ▼
 MCP
  │
  ▼
 LSP
  │
  ▼
Lean
```

versus:

```text
                     ┌──── Files / snapshots
                     │
Agent ── MCP ── Lean Workbench
                     │
                     ├──── Lean LSP
                     │
                     ├──── Lean Meta API
                     │
                     ├──── Lake
                     │
                     ├──── declaration index
                     │
                     └──── proof-state store
```

The latter gives you a **semantic service for theorem proving**.

LSP becomes one implementation component rather than the abstraction boundary.

---

## The MVP I would build

If I wanted something useful to agents immediately, my first server would expose only:

```text
workspace.info

fs.tree
fs.read
fs.search
fs.patch
workspace.diff

lean.check_file
lean.goal_at
lean.try_tactic
lean.hover
lean.inspect_decl
lean.search_type
lean.scratch
lean.verify

project.build
```

Then add transactional overlays.

Then add the stateful:

\[
proof.start / proof.apply / proof.clone
\]

API.

**That latter API is where I think this becomes substantially more interesting than "Lean on a remote machine."** You effectively turn Lean into a remotely accessible transition system whose states are proof obligations. A coding/research agent can explore that state space directly, while the source-file layer becomes a serialization of successful proofs.

And because the workspace is remote too, the same MCP server could become the execution substrate for the Go-verification project we were discussing: the agent edits `CoreGo/Semantics.lean`, asks Lean for exact proof states, searches your theorem corpus, experiments in isolated branches, and only commits the proof back into the repository once `lean.verify` certifies it. memcite


---

> inspect them, think hard.

I’ll compare the actual repos and interfaces, then separate what is already solved from what is missing for a serious agent-facing Lean service. I’ll focus on API shape, state management, filesystem/workspace semantics, proof-search ergonomics, and where MCP is the wrong abstraction boundary.

```json
{"system1_search_query":[{"q":"site:github.com lean-lsp-mcp Lean 4 MCP"},{"q":"site:github.com LeanCTX MCP Lean 4"},{"q":"site:github.com/leanprover Pantograph Lean machine-to-machine"},{"q":"site:lean-lang.org Lean Server Requests LSP RPC Lean 4"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 10 websites**

</details>

One correction already: **LeanCTX is not a Lean-theorem-prover project at all**; “Lean” there means *Lean Context*. My previous reply conflated the name with Lean 4. It is still relevant—but as a model for remote filesystem/context tooling, not as a proof backend. 

The other two are much closer to the two abstractions I suspected: `lean-lsp-mcp` is file/editor-centric, while Pantograph explicitly distinguishes Lean’s polished “presentation view” from an agent-oriented “search view.”

```json
{"click":[{"ref_id":"turn605185view3","id":91},{"ref_id":"turn605185view3","id":90},{"ref_id":"turn605185view4","id":74}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 2 websites**

</details>

```unknown
bash -lc rm -rf /tmp/lean-lsp-mcp /tmp/Pantograph /tmp/lean-ctx && git clone --depth 1 https://github.com/oOo0oOo/lean-lsp-mcp.git /tmp/lean-lsp-mcp && git clone --depth 1 --branch dev https://github.com/leanprover/Pantograph.git /tmp/Pantograph && git clone --depth 1 https://github.com/yvgude/lean-ctx.git /tmp/lean-ctx
```

<details><summary>💭 Thinking</summary>

**Cloned Lean repository sources**

</details>

A useful distinction is emerging: `lean-lsp-mcp` has already implemented several things I proposed—structured diagnostics/goals, scratch-document reuse, multi-tactic trials, code actions, verification, path confinement, HTTP transport, and even REPL acceleration. So a new project should **not** rebuild that layer unless its abstraction is intentionally different. 

The genuinely missing layer appears to be **persistent proof-search state + transactional source/workspace state + multi-agent isolation**, with Pantograph supplying much of the first and a LeanCTX-like design supplying ideas for the second.

```json
{"system2_search_query":[{"q":"site:github.com/leanprover/Pantograph \"goal.subsume\""},{"q":"site:github.com/leanprover/Pantograph metavariable coupling Pantograph"},{"q":"site:github.com/leanprover/Pantograph \"frontend.distil\""},{"q":"site:github.com/leanprover/Pantograph \"ProofState\""}],"response_length":"long"}
```

```json
{"paths":["GitHub"],"query":"contents"}
```

<details><summary>💭 Thinking</summary>

**Searched 4 websites**

</details>

```python3
{"path":"/GitHub/link_694554034b848191ab0db5a14b130105/fetch_file","args":{"repository_full_name":"oOo0oOo/lean-lsp-mcp","path":"src/lean_lsp_mcp/client_utils.py","start_line":1,"end_line":280}}
```

```json
{"paths":["GitHub"],"query":"search"}
```

```json
{"uri":"/response/turn0","query":"lean_multi_attempt"}
```

<details><summary>💭 Thinking</summary>

**Fetched Lean LSP utilities and searched GitHub for lean_multi_attempt**

</details>

```json
{"open":[{"ref_id":"https://raw.githubusercontent.com/oOo0oOo/lean-lsp-mcp/main/src/lean_lsp_mcp/server.py"},{"ref_id":"https://raw.githubusercontent.com/oOo0oOo/lean-lsp-mcp/main/src/lean_lsp_mcp/client_utils.py"},{"ref_id":"https://raw.githubusercontent.com/leanprover/Pantograph/dev/Pantograph/Protocol.lean"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

After inspecting the actual implementations, I would change the design fairly substantially.

The clean architecture is **not “Lean LSP exposed through MCP, plus some filesystem calls.”** There are really **three different semantic state spaces**, and the existing projects each illuminate a different one.

| Layer | Existing project | What it is good at | What I would do |
|---|---|---|---|
| **Source / workspace state** | LeanCTX ideas | snapshots, context-efficient reads, multi-agent state | Build our own small transactional workspace layer |
| **Presentation / elaboration state** | `lean-lsp-mcp` | files, positions, diagnostics, goals, hover, code actions, verification | Reuse heavily |
| **Proof-search state** | Pantograph | goals as machine-manipulable states, branching search, drafts, tactics | Use as the proof-search backend |

One correction first: **LeanCTX is unrelated to the Lean theorem prover.** It means “Lean Context”; it is a general coding-agent context/workspace system. I conflated the name in my previous answer. It is nevertheless interesting because it has persistent context, snapshots, multi-agent handoffs, compressed reads, etc. citeturn414604view1turn623323view3

## `lean-lsp-mcp` is already quite good

I underestimated how much it already implements.

Its current interface includes file outlines, structured diagnostics, goals at source positions, term goals, hover, declaration lookup, references, completions, scratch-code execution, multi-tactic attempts, LSP code actions, proof profiling, theorem axiom/soundness checks, local search, several theorem-search backends, and project builds. citeturn710080view0

In particular, this:

```text
lean_multi_attempt(file, position, [
    "simp",
    "aesop",
    "omega"
])
```

is already very close to the agent primitive I suggested. It can reuse either a scratch LSP document or a faster REPL environment, depending on configuration. citeturn710080view0

It also does sensible operational things: confines file operations to the project/dependency/stdlib roots, sanitizes paths, rejects symlink escapes, supports HTTP transport and authentication, and recommends containerization for stronger isolation. citeturn884841view0

So I would **not rebuild this part from scratch**.

But its abstraction is fundamentally:

\[
(\text{file},\text{line},\text{column})
\longrightarrow
\text{Lean information}.
\]

That's exactly right for a coding agent editing a `.lean` file.

It isn't quite the right abstraction for a theorem-search agent.

---

# Pantograph is the more important discovery

Pantograph explicitly makes essentially the distinction we were circling around.

Its designers distinguish:

\[
\text{Presentation View}
\qquad
\text{Search View}
\qquad
\text{Kernel View}.
\]

The presentation view is the human-written Lean source. The search view is the evolving proof trajectory. The kernel view is the metavariable-level representation. Pantograph says explicitly that Lean's LSP is primarily unsuitable for the search view, which is why Pantograph exists. citeturn414604view0

And its REPL already has primitives like:

```text
goal.start
goal.tactic
goal.continue
goal.delete
env.inspect
env.catalog
expr.echo
frontend.process
```

with explicit `stateId`s. `goal.tactic` can run tactics, provide proof expressions, introduce `have`/`let`, enter `conv` or `calc`, and turn draft expressions containing holes into explicit goals. citeturn590451view1

So this:

```text
state₀
   │ intro n
   ▼
state₁
   │ induction n
   ├─────────────┐
   ▼             ▼
state₂         state₃
   │ simp        │ ...
   ▼
state₄
```

is **not something we'd need to invent at the Lean level**.

Pantograph gives us a real proof-search transition system.

Its paper also supports extracting tactic transitions of the form

\[
(\text{goal before},\text{tactic},\text{goal after}),
\]

and has explicit support for proof sketches where `sorry` holes become individual proof goals. citeturn590451view2

This makes Pantograph a much better substrate for a **research/proof-search agent** than merely wrapping `lean_goal` and editing source repeatedly.

---

# The interesting architecture is therefore a synthesis

I would build:

```text
                         MCP facade
                             │
            ┌────────────────┼────────────────┐
            │                │                │
            ▼                ▼                ▼
    Workspace service    Lean LSP          Proof engine
                         workers             workers
            │                │                │
            │         lean-lsp-mcp-ish       │
            │           interface         Pantograph
            │                │                │
            └────────────────┴────────────────┘
                             │
                       isolated Lean
                         environment
```

The MCP layer should **not itself own implicit session state**.

This is particularly important now because MCP's July 28, 2026 specification deliberately removed protocol-level sessions and `Mcp-Session-Id`. The MCP maintainers explicitly recommend that stateful applications mint handles and have the model pass those handles back on subsequent calls. citeturn590451view0

That maps almost absurdly well onto theorem proving.

I would have explicit:

```text
workspace_id
revision_id

proof_id
state_id

environment_id
```

Rather than:

```text
"whatever state this HTTP connection currently happens to have"
```

---

# The crucial idea: make almost everything immutable

Suppose an agent starts with:

```text
workspace = W
revision  = R17
```

It makes a patch.

Don't mutate `R17`.

Produce:

```text
R17
 │
 │ patch P
 ▼
R18
```

Now another agent can simultaneously produce:

```text
       R17
      /   \
    P₁     P₂
    /       \
  R18       R19
```

Exactly the same idea applies to proof states.

Don't have:

```text
proof.current_state
proof.undo()
```

Instead:

```text
S17 ──simp─────▶ S18
 │
 ├──aesop──────▶ S19
 │
 └──rw [...]───▶ S20
```

Then "undo" is trivial:

> use `S17` again.

And parallel search is trivial:

> explore `S18`, `S19`, and `S20`.

This is much better for agents than modeling an editor's mutable cursor.

Mathematically, the MCP interface starts looking like:

\[
step :
State\times Action
\rightarrow
Result(State)
\]

rather than:

\[
Action\rightarrow IO()
\]

with mysterious hidden global state.

---

# The workspace and proof graphs should be different graphs

This is subtle but important.

A workspace graph might be:

```text
R0
│
├── patch Semantics.lean ──▶ R1
│                            │
│                            └── patch Model.lean ──▶ R3
│
└── different approach ────▶ R2
```

A proof graph pinned to `R1` might be:

```text
             P:R1:S0
             /     \
          simp    constructor
           │         │
          S1        S2
                    / \
                  S3   S4
```

So every proof state carries:

```text
workspace_revision = R1
environment         = E42
```

This is essential.

You absolutely do not want:

```text
proof state constructed against Mathlib/Project state A
               +
source files silently mutated to state B
               =
????
```

---

# The environment deserves its own identity

Pantograph has a relevant constraint here: its persistent process is started with a set of imported modules, and additional modules cannot simply be imported later into that running environment. citeturn590451view1

So I'd calculate something conceptually like:

\[
E =
H(
  lean\_toolchain,
  lake\_manifest,
  imports,
  options,
  relevant\ .olean\ files
).
\]

Not necessarily literally that exact hash implementation, but semantically that's what `environment_id` means.

Then:

```text
proof_state.environment_id == E82
```

is non-negotiable.

If the environment changes, either start another proof worker or reconstruct the proof.

This also gives you a huge caching opportunity.

Thousands of requests using:

```lean
import Mathlib
```

can share a prewarmed environment.

`lean-lsp-mcp` is already exploiting this idea with reusable scratch environments. citeturn884841view0turn710080view0

---

# The MCP surface I would now use

I would keep the advertised tool count fairly small. Something like this:

| Tool | Semantics |
|---|---|
| `workspace.open` | Create/open isolated project and return `workspace_id`, `revision_id` |
| `workspace.tree` | Compact remote tree |
| `workspace.read` | Read ranges/symbol-oriented views |
| `workspace.search` | Text/file search |
| `workspace.patch` | Atomic patch against an explicit base revision → new revision |
| `workspace.diff` | Compare revisions |
| `lean.check` | Structured LSP diagnostics for a revision |
| `lean.goal_at` | Presentation-view goal at a source position |
| `lean.inspect` | Hover/declaration/references/completion |
| `lean.search` | Local declaration/type/premise search |
| `proof.start` | Convert theorem/hole/expression into root search state |
| `proof.step` | Apply one semantic proof action |
| `proof.branch` | Evaluate several actions from one state |
| `proof.inspect` | Inspect a search state |
| `proof.materialize` | Turn successful search trajectory into source patch |
| `project.verify` | Check actual resulting source, axioms, sorries, build policy |

I would deliberately **not** expose Pantograph's entire command vocabulary as individual MCP tools.

Instead:

```text
proof.step(
  state_id,
  action = {
    kind: "tactic",
    tactic: "simp [foo]"
  }
)
```

or:

```text
action = {
  kind: "have",
  type: "P ∨ ¬P",
  name: "h"
}
```

or:

```text
action = {
  kind: "draft",
  expression: "..."
}
```

Pantograph can implement those cases internally. citeturn590451view1

That gives the MCP API a stable abstraction even if Pantograph's internal API changes.

---

# `proof.branch` may be the killer tool

For agents, I think this should be first class:

```text
proof.branch(
    state_id = "S42",
    actions = [
        tactic("simp"),
        tactic("aesop"),
        tactic("omega"),
        tactic("rw [foo]"),
        tactic("constructor")
    ]
)
```

return:

```text
[
  {
    action: "simp",
    status: "progress",
    child: "S43",
    delta: "target simplified ..."
  },
  {
    action: "aesop",
    status: "solved",
    child: "S44"
  },
  {
    action: "omega",
    status: "failed",
    diagnostic: "..."
  },
  ...
]
```

That's the proof-state analogue of `lean-lsp-mcp`'s excellent `lean_multi_attempt`, but it works against a **search state rather than a text position**. `lean_multi_attempt` already demonstrates that evaluating several candidate tactics before committing is extremely useful for an agent. citeturn710080view0

Now an LLM can perform beam search naturally:

\[
B_{n+1}
=
Top_k
\left(
\bigcup_{s\in B_n}
Actions(s)
\right).
\]

And you can put a learned value function over resulting states later.

---

# I would not actually persist raw Pantograph states as the durable representation

This was one of the more important conclusions from looking deeper.

Pantograph itself notes that distributing/pickling arbitrary tactic state is difficult, and in particular that combining proof branches executed on different machines isn't something it solves. citeturn590451view2

So externally:

```text
state_id = S8293
```

should be **our handle**, not Pantograph's raw internal ID.

Internally:

```text
S8293
  ├─ worker_id = P17
  ├─ pantograph_state = 91
  ├─ root = ...
  ├─ parent = S8288
  ├─ action = "rw [foo]"
  ├─ environment = E9
  └─ workspace_revision = R53
```

For recoverability, store the trajectory:

```text
root
intro x
constructor
simp [foo]
...
```

Then if the worker dies, you can **replay** the proof path into another compatible worker.

That is much less heroic than trying to serialize arbitrary Lean metaprogramming state.

---

# And don't distribute individual goals too aggressively

There is another trap.

Suppose:

```text
S0
├── goal g₁
└── goal g₂
```

It is tempting to send `g₁` to machine A and `g₂` to machine B.

But metavariables can couple goals.

A choice made while proving one can constrain another.

Pantograph has machinery specifically for goal continuation/resumption and search-state management because proof goals aren't always independent. citeturn590451view1

So initially I would parallelize:

\[
\text{whole proof-state alternatives}
\]

rather than:

\[
\text{arbitrary individual metavariables}.
\]

In other words:

```text
               S0
          /     |     \
      approach A B      C

         three workers
```

is safer than taking one proof state and scattering its coupled goals across machines.

You can optimize that later when independence is known.

---

# The filesystem side should use optimistic concurrency

This is where the unrelated LeanCTX gave me a useful idea.

For a remote agent, I wouldn't expose:

```text
fs.write(path, contents)
```

as the normal mutation primitive.

I'd expose:

```text
workspace.patch(
    revision = R17,
    edits = [...]
)
```

and produce:

```text
R18
```

If another agent already modified the same base and you're trying to perform a mutable update, reject it explicitly rather than silently overwriting.

Effectively:

\[
patch:R\times Patch\rightharpoonup R'.
\]

LeanCTX is interesting here because its broader design treats context/session state, snapshots and multi-agent handoffs as managed objects rather than relying purely on ordinary filesystem access. citeturn623323view3

For us, I'd go further and make source revisions immutable.

Underneath, you could implement that with:

- Git worktrees;
- overlayfs;
- copy-on-write directories;
- content-addressed blobs;
- a little Merkle filesystem.

The agent doesn't need to know.

---

# Remote files become much nicer than a conventional remote filesystem

For example:

```text
workspace.read(
  revision = "R81",
  path = "CoreGo/Semantics.lean",
  view = "outline"
)
```

could return:

```text
imports ...
namespace CoreGo

inductive Expr ...
structure State ...

def step ...

theorem step_preserves_typing ...
```

Then:

```text
view = {
  kind: "lines",
  from: 120,
  to: 180
}
```

gets the body.

Or:

```text
view = {
  kind: "declaration",
  name: "CoreGo.step_preserves_typing"
}
```

This is much more useful to an agent than making it emulate `cat`, `sed`, `find`, and `grep`.

The ordinary raw-file representation can still exist, but it shouldn't be the only semantic interface.

---

# Source editing and proof search must eventually meet again

Pantograph proving something successfully isn't enough.

Imagine the research agent discovers:

```lean
by
  induction xs <;> simp_all
```

We then need:

```text
search state
    │
    │ proof.materialize
    ▼
source patch
    │
    │ workspace.patch
    ▼
new revision R84
    │
    │ lean.check
    ▼
LSP success
    │
    │ project.verify
    ▼
verified revision
```

This final round trip through **actual source elaboration** is important.

The search view finds the proof.

The presentation view confirms that the serialized proof works where it will actually live.

So Pantograph and LSP aren't competing backends.

They form two sides of the workflow:

\[
Search
\rightarrow
Presentation
\rightarrow
Kernel.
\]

---

# Verification should be policy-driven

`lean-lsp-mcp` already exposes a useful `lean_verify` operation that checks axioms used by a theorem and can detect things such as `sorryAx` and suspicious source patterns. citeturn710080view0

I'd generalize that to:

```text
project.verify({
  revision: R84,
  policy: {
    no_errors: true,
    no_sorry: true,
    no_unsafe: true,
    allowed_axioms: [
      "propext",
      "Classical.choice",
      "Quot.sound"
    ]
  }
})
```

Then your harness has an unambiguous notion of success.

This also becomes very useful for coding agents:

> Don't tell me you've proved it; give me a `verified_revision`.

---

# Security changes substantially when Lean is remote

Lean code is not merely inert mathematical text. Tactics, metaprogramming, build machinery, etc. mean you should treat an uploaded/project workspace as executable code.

`lean-lsp-mcp` itself warns about filesystem access and powerful build/analysis capabilities and recommends container isolation when stronger boundaries are needed. citeturn884841view0

Pantograph points out another important problem: its Lean-level timeout is cooperative. A tactic that fails to cooperate can hang, and a memory-leaking tactic requires OS-level containment such as cgroups. citeturn414604view0

So a real remote service should have:

```text
MCP frontend
     │
     ▼
scheduler
     │
     ▼
sandbox
 ├── CPU limit
 ├── memory limit
 ├── wall-clock kill
 ├── process count
 ├── filesystem namespace
 └── network policy
     │
     ▼
Lean/Pantograph/LSP
```

Not:

```text
MCP → lake shell on my personal server
```

I would **not expose generic shell at all** in the first version.

---

# One more major point: don't make MCP itself too clever

The new stateless MCP architecture reinforces this. Each call should carry its durable semantic handles explicitly. citeturn590451view0

So:

```text
proof.step(
    workspace_revision = R32,
    state_id = S18,
    ...
)
```

can land on any frontend instance.

The frontend looks up:

```text
S18 → proof worker P9
```

and routes accordingly.

If P9 is dead:

```text
S18 → action log → replay on P13
```

This separates:

\[
\text{protocol state}
\]

from

\[
\text{application state}.
\]

That's exactly what you want for a scalable service.

---

# So my revised recommendation

I would **not fork `lean-lsp-mcp` and keep piling functionality into it**.

I'd build a thin orchestration service around two existing Lean-facing implementations:

```text
                        lean-workbench-mcp
                               │
       ┌───────────────────────┼───────────────────────┐
       │                       │                       │
       ▼                       ▼                       ▼
 workspace/revisions      presentation            search
       │                       │                       │
   our implementation      leanclient/           Pantograph
                           Lean LSP
       │                       │                       │
       └────────────── environment manager ───────────┘
                               │
                               ▼
                            Lake/Lean
```

`lean-lsp-mcp` is a very good reference—and potentially a reusable library/source of code—for the **presentation agent** side. Its documented feature set already solves a large part of that problem. citeturn710080view0turn884841view0

Pantograph should sit behind the **research agent** side because its abstraction was designed specifically around theorem-search trajectories rather than editor positions. citeturn414604view0turn590451view1

And the new thing worth building is really this middle layer:

\[
\boxed{
\text{versioned workspaces}
+
\text{explicit proof graphs}
+
\text{environment identity}
+
\text{sandboxed Lean workers}
}
\]

rather than yet another collection of `lean_*` MCP wrappers.

There is a pleasing formal character to it, too. Once states are immutable, the remote interface itself starts looking like a mathematical transition system:

\[
W \xrightarrow{patch} W'
\]

and

\[
P \xrightarrow{tactic} P'.
\]

The agent is traversing the product state space

\[
\boxed{
WorkspaceRevision
\times
LeanEnvironment
\times
ProofState
}
\]

and the server controls which transitions are valid.

That is the abstraction I would build around.

For the Go-formalization project we were discussing, this gets especially useful: a research agent could fork several proofs of a compiler/refinement theorem concurrently while a coding agent edits the semantic definitions on a separate workspace branch; nothing gets silently invalidated, and successful proof-search branches become actual checked source revisions only at the explicit materialization/verification boundary. memcite

