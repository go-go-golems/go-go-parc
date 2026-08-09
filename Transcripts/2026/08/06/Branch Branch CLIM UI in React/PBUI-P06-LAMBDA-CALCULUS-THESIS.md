---
title: "Ports as Variables, Bindings as Environments"
subtitle: "Lambda-Calculus Foundations for a Typed Presentation-Based UI and Its Binding Quotient Compiler"
author: "PBUI P06 Architecture Study"
date: "August 2026"
lang: en-US
documentclass: report
papersize: letter
classoption:
  - oneside
fontsize: 11pt
mainfont: STIX
sansfont: Inter
monofont: DejaVu Sans Mono
monofontoptions:
  - Scale=0.82
geometry:
  - margin=1in
  - headheight=15pt
colorlinks: true
linkcolor: NavyBlue
urlcolor: RoyalBlue
citecolor: ForestGreen
toc: true
toc-depth: 3
numbersections: true
secnumdepth: 3
---

# Abstract {-}

This thesis studies the relationship between the lambda calculus and a typed presentation-based user-interface architecture, with particular attention to the P06 **typed ports and binding quotient compiler**. The motivating system treats visible objects as typed, live presentations; actions can request additional typed objects from any visible surface; open components expose typed ports; identity-link declarations identify compatible ports; a compiler forms binding classes; and a runtime projects each local port onto a shared resource. The central claim of this thesis is that the lambda calculus supplies more than an analogy for such a system. It supplies a family of precise semantic decompositions.

At the syntactic level, a typed port is closely related to a free variable declaration. An open component is a term in a typing context. A directional connection is naturally modeled by typed substitution or `let`-binding. An action that awaits a second object is a partially applied function, while an active selection request is a typed continuation or algebraic effect. A registry of operations indexed by presentation type is related to dictionary passing and existential packaging of typed values.

Identity linking, however, is not ordinary beta reduction. Linking two ports asserts that two local interface occurrences refer to one binding or location. If the set of local port occurrences is \(P\), the declared links determine parallel endpoint maps \(s,t:E\rightrightarrows P\), and the compiler forms a quotient

\[
q:P\longrightarrow Q=\operatorname{coeq}(s,t).
\]

The quotient acts on *names or interface occurrences*. Semantically, environments vary contravariantly: a value assignment on binding classes, \(V^Q\), induces a compatible assignment on local ports, \(V^P\), by precomposition with \(q\). Thus a coequalizer on syntax corresponds to an equalizer-like subspace of environments. In the simply typed lambda calculus this is the semantic shape of contraction or aliasing: two variable occurrences are supplied from one source. In a stateful language, the stronger interpretation is that the ports share a location of type `Ref A`, not merely equal values of type `A`.

This distinction clarifies several design questions. A quotient determines topology but not conflict resolution. Linking two live cells with different values requires an explicit effectful merge policy. Unlinking is not an inverse quotient or inverse substitution; it requires retained provenance and a policy for initializing newly separated resources. Full widget renderings generally do not factor through the quotient because a chart and a pipeline may render the same binding differently. What factors canonically is the shared resource, binding identity, or binding-level observation. Local rendering remains an occurrence-indexed interpretation of that resource.

The thesis develops these ideas through untyped and typed lambda calculus, alpha/beta/eta equality, categorical semantics in cartesian closed categories, graph and call-by-need semantics for sharing, references and monadic state, call-by-push-value, algebraic effects, linear and session types, coalgebraic interaction machines, logical relations, and incremental lambda calculi. It proposes a small calculus for PBUI components, ports, links, resources, selection effects, and rendering observations; gives typing and operational rules; states core safety, coherence, factorization, alpha-invariance, and contextual-equivalence theorems; and outlines a Lean mechanization.

The resulting position is deliberately qualified. The lambda calculus is the correct foundation for abstraction, application, substitution, higher-order composition, typing, and contextual equivalence. It is not by itself a complete theory of mutable aliasing, dynamic graph surgery, conflict resolution, ongoing interaction, or distributed convergence. A robust PBUI architecture should therefore use a lambda-calculus core surrounded by explicit theories of names, resources, effects, coalgebras, incremental change, and categorical wiring.

# Preface {-}

The phrase “connection to the lambda calculus” can invite two opposite mistakes. The first is to regard the connection as superficial: JavaScript uses closures, therefore a React UI is “based on lambda calculus.” That observation is true but nearly useless. The second is to force every part of a user interface into one calculus and to rename engineering mechanisms with mathematical terminology. That produces vocabulary without explanatory power.

This thesis takes a stricter route. Every proposed correspondence is labeled as one of four kinds:

1. **Exact encoding.** One construct is directly represented by another, such as a pending binary action becoming a unary function after partial application.
2. **Semantic model.** A mathematical structure gives a denotation of the engineering mechanism, such as a typing context interpreting the free ports of a component.
3. **Implementation analogy.** Two mechanisms share an operational pattern but are not interchangeable, such as graph sharing and a shared reactive cell.
4. **Boundary or non-correspondence.** The lambda calculus does not determine the behavior in question, such as choosing a winner when two linked cells contain conflicting values.

The P06 design is treated as a semantic case study. The supplied JSX foundation describes every visible object as a typed, live presentation, gives left- and right-click distinct meanings, and enters a typed accept mode when an action needs another object. The P06 work adds a different but related layer: typed component ports, identity-link equations, quotient compilation, binding identities, resource projection, dynamic topology changes, and explicit merge and unlink policies. These mechanisms form the concrete substrate throughout the thesis.

# Contributions {-}

This thesis makes the following architectural and semantic contributions.

- It gives a precise correspondence between **open typed components** and lambda terms in context.
- It separates **directional connection as substitution** from **identity linking as contraction or aliasing**.
- It derives the semantic map from a port quotient \(q:P\to Q\) to compatible environments \(V^Q\to V^P\).
- It explains why P06 should quotient **port occurrences**, while maintaining persistent binding identities outside union-find representatives.
- It corrects the over-strong claim that linked ports must render the same widget. Linked ports share a resource; their local renderings may remain intentionally different.
- It relates selection and accept mode to typed continuations, partial application, evaluation contexts, and algebraic effects.
- It places read/write modes, authority, multiplicity, and update algebra in the landscape of refinement, linear, capability, and session typing.
- It proposes a compact **PBUI lambda calculus**, called \(\lambda_{\mathrm{PB}}\), with values, computations, ports, references, links, and observations.
- It states a theorem catalogue for type safety, quotient coherence, factorization, link-order invariance, alpha-renaming, contextual equivalence, and optimized-compiler refinement.
- It gives a staged mechanization and implementation plan connecting Lean specifications to a TypeScript reference interpreter and optimized binding compiler.

# Notation and reading guide {-}

The core notation is summarized below.

| Notation | Meaning |
|---|---|
| \(A,B,C\) | semantic or programming-language types |
| \(x,y,z\) | lambda-bound variables |
| \(p,r\) | local typed port occurrences |
| \(P_\tau\) | port occurrences in contract fiber \(\tau\) |
| \(E_\tau\) | identity-link declarations in contract fiber \(\tau\) |
| \(s,t:E_\tau\rightrightarrows P_\tau\) | source and target endpoint maps |
| \(q_\tau:P_\tau\to Q_\tau\) | quotient projection to binding classes |
| \(\Gamma\) | typing context or open component boundary |
| \(\rho\) | environment assigning meanings to variables or ports |
| \(\sigma\) | store assigning values to runtime locations |
| \(\ell\) | runtime location or resource identifier |
| \(M[N/x]\) | capture-avoiding substitution |
| \(\llbracket M\rrbracket\) | denotation of term or component \(M\) |
| \(M\Downarrow V\) | big-step evaluation |
| \(M\to M'\) | small-step transition |
| \(\simeq_{ctx}\) | contextual equivalence |

Readers mainly interested in API design can read Chapters 1, 5-10, 17, and 22-24. Readers interested in formal semantics should additionally read Chapters 2-4, 11-16, and 19-21. Chapter 25 gives a compact research agenda.

# Part I - The case study and the lambda-calculus lens {-}

# The PBUI and P06 problem

## Typed live presentations

The motivating interface is not organized around inert pixels. A visible email thread, event, contact, project, transcript moment, tile, or workspace is presented as a typed semantic object. The same contact may appear as an inbox sender, calendar attendee, and transcript speaker, yet each occurrence offers the same underlying contact to the interaction system. A right-click asks for actions applicable to the semantic object. A left-click either performs a default activation or, when the system is awaiting a typed argument, supplies the object to the pending interaction.

The key abstraction is therefore not merely a React component:

```ts
<P ptype="contact" value={contactId}>
  <ContactChip id={contactId} />
</P>
```

It is a judgment that one rendered occurrence offers a value under a semantic type:

\[
\textsf{occurrence } o \textsf{ presents } v:A.
\]

When a command needs a second object, the shell enters a mode that can be read informally as:

\[
\textsf{choose a currently presented inhabitant of } A.
\]

This already places the architecture near typed lambda calculus. A pending action has a missing typed argument; visible presentations are candidate values; acceptance supplies one value; and the action continues.

## From presentations to open components

P06 addresses a different scale. A chart, pipeline, table, or plugin is modeled as an **open component** whose public interface consists of typed ports. For example:

```ts
const Chart = component({
  ports: {
    document: cellPort<DocumentId>({
      semanticTag: "primary-document",
      mode: "read-write",
      authorityDomain: "workspace",
      multiplicity: "one",
      updateAlgebra: "replace",
      lifetime: "workspace",
    }),
  },
});
```

A pipeline can expose a port with the same contract. Before linking, the two ports are distinct local occurrences and may refer to different resources. An identity link declares that they should share one binding:

```ts
registry.identify(
  chart.port("document"),
  pipeline.port("document"),
  { mergePolicy: preferLeft(chart.port("document")) },
);
```

The compiler checks compatibility, forms connected components or quotient classes, assigns stable external binding identities, allocates one resource per class, and exposes a projection for each local port. Writes through either projection become visible through the other.

## Why the lambda-calculus connection matters

The engineering questions resemble classical questions in programming-language semantics:

- What is a component with unconnected ports?
- What does it mean to supply a port from another component?
- When are two names merely different representatives of one binding?
- What is preserved by renaming internal identifiers?
- When may a value or resource be duplicated, discarded, or shared?
- How are effects separated from values?
- When are an optimized compiler and a reference interpreter observationally equivalent?
- What equations may be imposed without making the system incoherent?

The lambda calculus was designed around abstraction, variables, substitution, and application. Typed variants add contexts and compositional contracts. Its operational and denotational semantics supply disciplined answers to these questions. The direct benefit to P06 is not that its implementation should look syntactically functional. The benefit is that the compiler can be designed as an elaboration from one typed language of open interfaces into another typed language of shared resources.

## The central thesis

The central thesis is:

> A typed-port PBUI is best understood as an effectful, resource-aware lambda calculus whose open terms expose port variables; directional connections elaborate to substitution; identity links elaborate to explicit contraction and shared locations; interaction requests elaborate to typed effects or continuations; and rendering is an observation interpreter over the resulting stateful machine.

The qualification “effectful, resource-aware” is essential. Pure lambda substitution alone cannot explain the persistence, aliasing, conflict, and history behavior of live bindings.

# Lambda calculus in the form needed here

## Untyped syntax

The untyped lambda calculus has three constructors:

\[
M,N ::= x \mid \lambda x.M \mid M\;N.
\]

A variable stands for an input supplied by an environment. An abstraction packages a term while binding one variable. Application supplies an argument to a function. Church used lambda-definability as part of a formal account of effective calculability; later programming-language work turned the calculus into a core language for higher-order computation (Church 1936).

The principal computation rule is beta reduction:

\[
(\lambda x.M)\;N \to_\beta M[N/x].
\]

Here \(M[N/x]\) means capture-avoiding substitution of \(N\) for free occurrences of \(x\) in \(M\).

Two additional equality principles matter throughout this thesis.

**Alpha equivalence** treats bound-variable names as irrelevant:

\[
\lambda x.M \equiv_\alpha \lambda y.M[y/x]
\]

when the renaming avoids capture.

**Eta equivalence** expresses extensionality:

\[
\lambda x.f\;x \equiv_\eta f
\]

when \(x\) is not free in \(f\).

These three equalities anticipate three PBUI concerns:

- alpha: generated port, binding, and resource names should not affect meaning;
- beta: a directional connection supplies an input and composes components;
- eta: a wrapper that merely forwards an interface should be observationally removable.

## Free variables and open terms

A term is **closed** when it has no free variables. Otherwise it is open. For example:

\[
x\;y
\]

is open in \(x\) and \(y\). A component whose document and filter ports have not yet been connected is likewise open. Its meaning depends on an environment that supplies these inputs.

This is the first exact structural correspondence:

| Lambda calculus | Typed component system |
|---|---|
| free variable | unconnected input port |
| bound variable | internally supplied or locally scoped port |
| environment | assignment of resources or values to ports |
| abstraction | packaging a component over a port |
| application/substitution | connecting an output to an input |
| closed term | component graph with all required inputs resolved |

The correspondence becomes precise only after types are added.

## Simply typed lambda calculus

Types are generated from base types and function types:

\[
A,B ::= \iota \mid A\to B.
\]

A typing context is a finite list of variable declarations:

\[
\Gamma = x_1:A_1,\ldots,x_n:A_n.
\]

A typing judgment

\[
\Gamma\vdash M:A
\]

states that term \(M\) has type \(A\) when its free variables are supplied according to \(\Gamma\).

The core rules are:

\[
\frac{x:A\in\Gamma}{\Gamma\vdash x:A}
\qquad
\frac{\Gamma,x:A\vdash M:B}{\Gamma\vdash \lambda x.M:A\to B}
\qquad
\frac{\Gamma\vdash M:A\to B\quad\Gamma\vdash N:A}{\Gamma\vdash M\;N:B}.
\]

The substitution lemma is the central compositional theorem:

\[
\frac{\Gamma,x:A\vdash M:B\qquad\Gamma\vdash N:A}
     {\Gamma\vdash M[N/x]:B}.
\]

P06's contract compatibility check is an enriched form of the premise that the supplied argument and receiving variable agree on type.

## Products, sums, existentials, and references

Real component interfaces need more than function types.

Products describe simultaneous inputs:

\[
A\times B.
\]

Sums describe tagged alternatives such as events:

\[
A+B.
\]

Existential types package values whose exact type is hidden but accompanied by operations or a runtime witness:

\[
\exists A.\;\textsf{TypeRep}(A)\times A.
\]

This is close to a heterogeneous presentation reference: “there exists a presentation type \(A\), together with its type token and value.” A TypeScript discriminated union is a finite, first-order approximation to this existential packaging.

Mutable binding resources require a reference type:

\[
\operatorname{Ref} A.
\]

A port carrying `DocumentId` is not automatically a reference. P06's projected binding resource behaves more like a value of `Ref DocumentId`: it can be read, written, observed, and shared by multiple local endpoints.

## Structural rules

Ordinary simply typed lambda calculus uses a cartesian context discipline. Variables may be:

- reordered (**exchange**);
- unused (**weakening**);
- used more than once (**contraction**).

Contraction is especially important:

\[
\frac{\Gamma,x:A,y:A\vdash M:B}
     {\Gamma,z:A\vdash M[z/x,z/y]:B}.
\]

This rule identifies two input positions with one supplied value. An identity link between two read-only value ports has exactly this static shape. For shared mutable resources, contraction must be interpreted as aliasing one reference, not copying its current contents.

Linear logic removes unrestricted weakening and contraction, making resource use explicit (Girard 1987). P06 contracts already suggest a substructural refinement: some read ports may be duplicable, some write capabilities should be exclusive, and some event tokens should be consumed exactly once.

# Syntax, semantics, and implementation

## Three levels that must remain distinct

A useful semantic account separates:

1. **Surface syntax:** React components, registry calls, JSX presentations, and user gestures.
2. **Core language:** typed subjects, ports, links, commands, effects, and interaction states.
3. **Runtime model:** resources, stores, subscriptions, DOM occurrences, and network effects.

The lambda calculus primarily organizes the core language. A React callback is already a JavaScript closure, but treating arbitrary callbacks as the semantic core makes substitution, dependencies, effects, and equality opaque.

## Operational semantics

Operational semantics specifies how configurations step:

\[
\langle M,\sigma\rangle\to\langle M',\sigma'\rangle.
\]

For PBUI, a configuration includes more than a term:

\[
\langle C,G,Q,\sigma,I,O\rangle,
\]

where:

- \(C\) is component-local state;
- \(G\) is the durable port/link graph;
- \(Q\) is the compiled binding plan;
- \(\sigma\) maps binding resources to current values;
- \(I\) is the active interaction machine;
- \(O\) is mounted occurrence state.

A user event, command, or external response produces the next configuration and possibly effects.

## Denotational semantics

Denotational semantics assigns mathematical meanings compositionally. In the simply typed lambda calculus, a context

\[
x_1:A_1,\ldots,x_n:A_n
\]

is interpreted as a product:

\[
\llbracket\Gamma\rrbracket
=
\llbracket A_1\rrbracket\times\cdots\times\llbracket A_n\rrbracket.
\]

A term is interpreted as a morphism:

\[
\llbracket\Gamma\vdash M:B\rrbracket:
\llbracket\Gamma\rrbracket\longrightarrow\llbracket B\rrbracket.
\]

Cartesian closed categories provide the products and exponentials needed to interpret products and function types. Conversely, the typed lambda calculus presents a free cartesian closed category modulo its equations; this is the Curry-Howard-Lambek connection developed in categorical logic (Lambek 1985).

For effectful PBUI computations, the codomain is not simply \(B\). A monadic account uses:

\[
\llbracket\Gamma\vdash M:B\rrbracket:
\llbracket\Gamma\rrbracket\to T\llbracket B\rrbracket,
\]

where \(T\) accounts for state, exceptions, nondeterminism, asynchronous requests, or another effect (Moggi 1991).

## Contextual equivalence

Two implementations are interchangeable when no permitted context can distinguish them:

\[
M\simeq_{ctx}N.
\]

This is stronger and more relevant than object equality. A reference graph compiler and a union-find compiler may allocate different internal representatives, yet be contextually equivalent if every public query, projection, trace, and persistence operation produces the same observable result up to permitted renaming.

Operationally based logical relations and bisimulation techniques provide methods for proving such equivalence, including in languages with local state (Pitts 1997, 2000).

# Part II - Ports, contexts, substitution, and quotients {-}

# Typed ports as variables in context

## Port occurrences, not only port kinds

A port declaration has at least two identities:

- its **contract**, such as “workspace-scoped read-write primary document cell”;
- its **occurrence**, such as `chart-17/document`.

Two occurrences may share a contract without being connected. This is analogous to two variables with the same type:

\[
x:A,\;y:A.
\]

Their shared type does not make them the same variable. Likewise, the following ports are compatible candidates for linking but remain distinct before a link is declared:

```ts
chart.document    : PrimaryDocumentCell
pipeline.document : PrimaryDocumentCell
```

A component boundary is therefore a typed context:

\[
\Gamma_C = p_1:\tau_1,\ldots,p_n:\tau_n.
\]

The contract \(\tau\) is richer than an ordinary payload type. A useful P06 contract can be written as a tuple:

\[
\tau=
(A,m,a,k,u,l),
\]

where:

- \(A\) is the payload sort;
- \(m\) is a temporal or read/write mode;
- \(a\) is an authority domain;
- \(k\) is multiplicity;
- \(u\) is an update algebra;
- \(l\) is lifetime.

The type checker for identity linking should compare the entire contract, or apply an explicitly declared compatibility relation. Equal JavaScript representations are insufficient. Two strings can represent a primary document, an event name, a derived document, or an authorization token.

## Open components as judgments

An open component with input boundary \(\Gamma\), local state \(S\), outputs \(\Delta\), and observations \(O\) can be idealized as a judgment:

\[
\Gamma\mid S\vdash C:\Delta\;!\;O.
\]

A simpler functional view is:

\[
C:\llbracket\Gamma\rrbracket\times S
\longrightarrow
T(\llbracket\Delta\rrbracket\times S\times O),
\]

where \(T\) represents effects. The component is “open” because its denotation awaits an environment for \(\Gamma\).

For a pure chart view:

\[
\textsf{document}:D,
\textsf{spec}:S
\vdash
\textsf{renderChart}:W,
\]

where \(D\) is a document identifier, \(S\) is a chart specification, and \(W\) is a widget description. In lambda notation:

\[
\lambda d:D.\lambda s:S.\;\textsf{chartWidget}(d,s).
\]

The React component is one interpreter of this open term. The binding compiler supplies part of the environment.

## Port schemas as context formation

A typed language controls which contexts are legal. P06 does the same through declarations:

```ts
const documentPort = port<DocumentId>({
  semanticTag: "primary-document",
  mode: "read-write",
  authorityDomain: "workspace",
  multiplicity: "one",
  updateAlgebra: "replace",
  lifetime: "workspace",
});
```

A context formation judgment might be:

\[
\frac{\Gamma\ \textsf{well formed}\qquad \tau\ \textsf{well formed}\qquad p\notin\operatorname{dom}(\Gamma)}
     {\Gamma,p:\tau\ \textsf{well formed}}.
\]

The condition that names are fresh is not semantically deep, but it prevents accidental capture or collision. Persistent IDs can later be alpha-renamed during import, provided all incidence relations are preserved.

## Heterogeneous registries as existential packages

A runtime registry often stores ports of many types in one collection. In type theory this is naturally existential:

\[
\exists \tau.\;\textsf{PortId}\times\textsf{Contract}(\tau)\times\textsf{PortState}(\tau).
\]

In TypeScript, a generic existential is commonly encoded by a discriminated union, a GADT-like interface, or a type token paired with an unknown value and checked eliminators:

```ts
interface SomePort {
  contract: SomeContract;
  address: PortAddress;
  value: unknown;
}

function withTypedPort<R>(
  p: SomePort,
  k: <A>(witness: Contract<A>, value: A) => R,
): R;
```

The elimination principle is more important than the storage representation. Consumers should not obtain `unknown` and cast freely; they should be forced through the contract witness. This is the typed-language analogue of opening an existential package.

## Presentation references as typed values

The generic PBUI representation

```ts
type PresentationReference<Values> = {
  [K in keyof Values]: {
    type: K;
    value: Values[K];
  }
}[keyof Values];
```

is a finite sum:

\[
\sum_{K\in\operatorname{keys}(Values)} Values(K).
\]

Each constructor carries both a type tag and a value. Selection is pattern matching over the sum. A future open-world system can replace the closed key union with first-class sort witnesses and existential packaging, preserving the same logical shape.

# Directional connection is substitution

## Supplying an input

Suppose a pipeline output computes a document:

\[
\Gamma\vdash N:D.
\]

A chart expects a document:

\[
\Gamma,d:D\vdash M:W.
\]

Connecting the output to the chart input is typed substitution:

\[
\Gamma\vdash M[N/d]:W.
\]

At an API level:

```ts
workspace.connect({
  from: pipeline.port("resultDocument"),
  to: chart.port("document"),
  via: identity<DocumentId>(),
});
```

If the source and target representations differ, `via` is a typed function:

```ts
workspace.connect({
  from: chart.port("selectedRows"),
  to: pipeline.port("filter"),
  via: selectedRowsToFilter,
});
```

In lambda notation:

\[
\lambda r:\textsf{RowSet}.\;\textsf{selectedRowsToFilter}(r).
\]

This is directional composition. It does not assert that `selectedRows` and `filter` are the same interface object.

## `let` as explicit wiring

A component graph can be rendered as nested `let` bindings:

\[
\begin{aligned}
&\textsf{let } d = \textsf{pipelineResult}(source)\textsf{ in}\\
&\textsf{let } w = \textsf{chart}(d,spec)\textsf{ in}\\
&\textsf{display}(w).
\end{aligned}
\]

The beta law explains why an intermediate wire can be eliminated extensionally:

\[
\textsf{let }x=N\textsf{ in }M
\equiv
M[N/x].
\]

An implementation may retain the wire for debugging, scheduling, incremental invalidation, or provenance. The equational semantics says that the retained wire should not change pure results.

## Typed adapters and coercion coherence

A system with automatic presentation translators resembles a language with implicit coercions. If there are multiple paths from \(A\) to \(B\), the elaborator must answer whether they are coherent:

\[
f:A\to C,\quad g:C\to B,
\qquad
h:A\to B.
\]

Should \(g\circ f\) equal \(h\)? If not, choosing a shortest or highest-priority path is an operational policy, not a proof of semantic equivalence.

P06 avoids much of this ambiguity by making identity links strict and transformed connections explicit. That is a good lambda-calculus discipline: application requires an exact argument type unless a coercion term is inserted visibly by elaboration.

## Application versus wiring diagrams

A lambda term is tree-shaped syntax, but component graphs may share subcomputations or contain feedback. A naive substitution-based compiler can duplicate a source term at each use:

\[
M[N/x]
\]

may contain several copies of \(N\). A graph compiler instead introduces a shared node:

\[
\textsf{let }x=N\textsf{ in }M.
\]

For pure values, the difference is operational. For effects or mutable references, it is semantic. Evaluating \(N\) once and sharing its result differs from evaluating it twice. P06's persistent binding resources therefore align more closely with explicit `let`, heaps, and call-by-need graph semantics than with textual substitution alone.

# Identity linking is contraction and aliasing

## The static rule

Suppose a chart and pipeline each expect a primary document:

\[
\Gamma,
 c:D,
 p:D
\vdash
M:W.
\]

Linking the two value ports to one source \(d:D\) gives:

\[
\Gamma,d:D
\vdash
M[d/c,d/p]:W.
\]

This is contraction. Two variable positions are supplied by one variable.

A typed identity link can therefore be elaborated to a substitution:

\[
\theta = [d/c,d/p].
\]

The linked component is \(M\theta\).

## Equal values versus one location

For live read-write ports, the relevant type is not merely \(D\) but \(\operatorname{Ref}D\):

\[
\Gamma,
 c:\operatorname{Ref}D,
 p:\operatorname{Ref}D
\vdash M:W.
\]

Linking supplies the same location \(\ell\):

\[
M[\ell/c,\ell/p].
\]

This creates aliasing:

\[
c=p=\ell.
\]

It is stronger than the invariant that reads happen to return equal values:

\[
!c=!p.
\]

Two distinct references can contain equal document IDs now and diverge after a write. One shared reference cannot diverge if all reads and writes go through that reference.

This gives a precise interpretation of P06's resource allocation:

```text
local port occurrence -> binding class -> runtime location -> current value
```

or mathematically:

\[
P_\tau\xrightarrow{q_\tau}Q_\tau
\xrightarrow{\ell_\tau}L_\tau
\xrightarrow{\sigma}V_\tau.
\]

## Controlled contraction

Ordinary lambda calculus allows unrestricted contraction. A port system should not.

- A read-only immutable value may be duplicated freely.
- A shared reactive cell may permit many readers and coordinated writers.
- An exclusive write capability may require one owner.
- An event token may be linear: consuming it twice is invalid.
- A replicated CRDT value may support many writers only because its merge algebra satisfies specific laws.

The contract's mode, multiplicity, authority domain, and update algebra determine whether contraction is admissible. A richer typing judgment can track a structural mode:

\[
p:!A
\]

for duplicable values, versus

\[
p:A
\]

for linear resources. Girard's linear logic and later linear type systems make this distinction explicit. P06 need not expose linear-logic syntax to users, but its compiler should embody the same resource discipline.

## Identity links as explicit alias declarations

A useful core language separates:

```text
connect p -> q via f     directional dataflow
identify p = q           shared binding / alias
```

The first elaborates to function composition or substitution. The second elaborates to a context quotient and shared location.

Confusing them causes predictable errors. A derived pipeline output should not be identified with a chart's editable primary-document cell merely because both carry `DocumentId`. A derived output is a computation result; the editable cell is an authority-bearing state location. A directional connection may be valid while identity linking is not.

# Binding classes as quotients and coequalizers

## Generating equations

Fix one compatible contract fiber \(\tau\). Let \(P_\tau\) be its local port occurrences and \(E_\tau\) its declared identity links. Each link has two endpoints:

\[
s,t:E_\tau\rightrightarrows P_\tau.
\]

The compiler forms the smallest equivalence relation \(\sim\) containing

\[
s(e)\sim t(e)
\qquad
\textsf{for every }e\in E_\tau.
\]

The set of binding classes is:

\[
Q_\tau=P_\tau/{\sim}.
\]

The projection

\[
q_\tau:P_\tau\to Q_\tau
\]

is a coequalizer in the category of sets:

\[
q_\tau\circ s=q_\tau\circ t.
\]

This is the formal statement that each declared pair receives the same binding identity.

## The universal property

Suppose an interpretation

\[
g:P_\tau\to X
\]

already respects every link:

\[
g(s(e))=g(t(e))
\qquad
\textsf{for all }e.
\]

Then there is a unique map

\[
\bar g:Q_\tau\to X
\]

such that:

\[
g=\bar g\circ q_\tau.
\]

This is not an ornamental theorem. It identifies the class of valid downstream interpreters. A persistence encoder, resource allocator, binding inspector, or authorization summary that treats linked ports identically can be implemented once per binding class.

The factorization can be rendered as:

```text
                 g
local ports P ---------> X
      |                  ^
      | q                | g-bar
      v                  |
bindings Q -------------+
```

## What should factor through the quotient?

A subtle correction is necessary. Full local widgets do not generally respect identity links. A chart document selector and a pipeline document selector may share a binding while rendering differently:

```text
chart.document     -> compact dropdown in chart toolbar
pipeline.document  -> document node in pipeline header
```

Therefore a map

\[
\textsf{render}:P_\tau\to\textsf{Widget}
\]

need not satisfy

\[
\textsf{render}(p)=\textsf{render}(r)
\]

for linked ports. It should not be forced to factor through \(Q_\tau\).

What does factor is the shared resource or binding-level observation:

\[
\textsf{resource}:P_\tau\to L_\tau,
\]

with

\[
\textsf{resource}=\bar\ell\circ q_\tau.
\]

Local rendering then depends on both the occurrence and the resource:

\[
\textsf{widget}(p)
=
\textsf{render}_p(\bar\ell(q_\tau(p))).
\]

Equivalently, rendering is a dependent family indexed by occurrences. A canonical binding-inspector widget may factor through the quotient, but ordinary component UI remains occurrence-specific.

This distinction is central to a correct PBUI semantics: **shared meaning does not imply identical appearance**.

## Union-find is not the quotient's meaning

Union-find efficiently computes equivalence classes under link insertion. Its root representatives depend on rank, path compression, declaration order, or implementation details. A root is not a durable semantic identity.

P06 should therefore distinguish:

- the extensional class \([p]\in Q_\tau\);
- an internal union-find representative;
- a stable external `BindingId` assigned by persistence policy.

Two compiler runs may produce different roots but isomorphic quotient plans. The observational contract should be invariant under renaming generated binding IDs, except where a persistence layer intentionally stabilizes them.

## Quotienting syntax, restricting models

The quotient acts covariantly on port names, but environments vary contravariantly. Let \(V_\tau\) be the set of possible port values. An environment for local ports is:

\[
\rho\in V_\tau^{P_\tau}.
\]

An environment for binding classes is:

\[
\bar\rho\in V_\tau^{Q_\tau}.
\]

Precomposition with \(q_\tau\) gives:

\[
q_\tau^*:V_\tau^{Q_\tau}\to V_\tau^{P_\tau},
\qquad
q_\tau^*(\bar\rho)=\bar\rho\circ q_\tau.
\]

Its image is exactly the compatible local environments:

\[
\operatorname{im}(q_\tau^*)
=
\{\rho\mid \rho(s(e))=\rho(t(e))\textsf{ for all }e\}.
\]

Thus the coequalizer of syntax induces an equalizer-like constraint on semantic assignments. This contravariance is one of the deepest links between P06 and lambda-calculus semantics.

# Context quotients and diagonal substitution

## A two-port example

Consider a component term:

\[
x:D,y:D\vdash M:W.
\]

The unlinked semantic environment object is:

\[
D\times D.
\]

Linking \(x\) and \(y\) produces one binding variable:

\[
z:D\vdash M[z/x,z/y]:W.
\]

Semantically, the new term is obtained by composing with the diagonal:

\[
\Delta_D:D\to D\times D,
\qquad
\Delta_D(d)=(d,d).
\]

Therefore:

\[
\llbracket M[z/x,z/y]\rrbracket
=
\llbracket M\rrbracket\circ\Delta_D.
\]

The port quotient is visible syntactically as one equivalence class. In the model, it becomes a diagonal supplying one semantic value to two input positions.

## General quotient-induced diagonals

For a finite family of ports, a quotient map

\[
q:P\to Q
\]

induces:

\[
\Delta_q:V^Q\to V^P,
\qquad
\Delta_q(\rho)=\rho\circ q.
\]

This map duplicates the value of each binding class into every local occurrence belonging to that class.

For stateful resources, replace \(V\) by a location space \(L\):

\[
\Delta_q:L^Q\to L^P.
\]

All occurrences in one class receive the same location. The store then maps locations to values:

\[
\sigma:L\to V.
\]

The observed local values are:

\[
P\xrightarrow{q}Q\xrightarrow{\ell}L\xrightarrow{\sigma}V.
\]

## Structural substitution

A substitution between contexts can be seen as a tuple of terms, one for each target variable. The link quotient defines a particularly simple substitution: each local port variable maps to its binding-class variable.

If

\[
\Gamma_P=(p:P\mid p\in P)
\]

and

\[
\Gamma_Q=(b:V\mid b\in Q),
\]

then the quotient substitution is:

\[
\theta_q(p)=q(p).
\]

Applying \(\theta_q\) to a component term closes the distinctions erased by the link relation.

This is the sense in which the P06 compiler is a **substitution compiler**. It does not merely group IDs; it elaborates an open component context into a smaller context plus an explicit structural substitution.

## Relation to free cartesian structure

Cartesian contexts support diagonals and projections:

\[
\Delta_A:A\to A\times A,
\qquad
!_A:A\to 1.
\]

These interpret contraction and weakening. An identity-link compiler selectively introduces diagonals according to explicit wiring rather than permitting every component to duplicate every resource indiscriminately.

This suggests a typed intermediate language where structural rules are explicit:

```text
copy p as (p1, p2) in M
share (p1, p2) as p in M
hide p in M
```

The compiler can then reject illegal contraction for linear or exclusive capabilities while retaining ordinary cartesian behavior for immutable values.

# Alpha equivalence, generated names, and persistent identities

## Port names as binders

Port IDs such as `chart-17/document` are operationally useful but often semantically inessential. Importing a workspace may freshen view IDs, placement IDs, link IDs, and runtime binding IDs. If incidence and contract structure are preserved, the imported graph should denote the same architecture up to renaming.

This is alpha equivalence at the graph level.

A renaming

\[
\pi:P\to P'
\]

is semantics-preserving when it is bijective within the relevant namespace and transports links and declarations:

\[
(p,r)\in E
\quad\Longleftrightarrow\quad
(\pi(p),\pi(r))\in E'.
\]

The quotient classes are then isomorphic:

\[
P/{\sim_E}\cong P'/{\sim_{E'}}.
\]

## Hygienic composition

Combining independently authored components can cause name collisions. Lambda-calculus substitution avoids variable capture by alpha-renaming bound variables before substitution. Component composition needs the same hygiene:

1. allocate fresh internal component, port, and link IDs;
2. preserve exported semantic names through a module interface;
3. transport all references through the renaming;
4. compare results up to alpha equivalence rather than raw string equality.

Fiore, Plotkin, and Turi's categorical treatment of syntax with binding emphasizes that substitution and binding should be characterized independently of accidental names (Fiore, Plotkin, and Turi 1999). P06 can adopt this principle even if its implementation uses ordinary strings.

## Persistent identity is not alpha identity

Some IDs are intentionally observable. A durable binding may appear in audit logs, synchronization protocols, or saved references. The architecture therefore needs two layers:

- **structural identity:** the extensional quotient class determined by current topology;
- **persistent identity:** a stable name assigned by a policy across recompilations.

Persistent identity is not supplied by lambda calculus. It is a stateful naming policy. The policy can nevertheless be tested for alpha-invariance: renaming local port occurrences should not change the persistent matching decision except through declared anchors or lineage.

## Nominal and de Bruijn alternatives

Several implementation strategies are possible.

- **Nominal names:** human-readable stable IDs with freshness generation.
- **De Bruijn-style indices:** positions in a context, eliminating alpha conversion but making graph edits awkward.
- **Locally nameless representations:** names for free ports and indices for bound internals.
- **Unique atoms:** opaque runtime identities with separate labels.

P06's open, dynamically edited graph favors unique atoms plus readable labels. A proof model can use finite indices or quotient names to simplify alpha-equivalence reasoning.

# Beta and eta laws for component composition

## Beta as connection elimination

Suppose a component abstraction exposes an input:

\[
C=\lambda d:D.\;M.
\]

Supplying a document source \(N:D\) gives:

\[
C\;N\to_\beta M[N/d].
\]

At the component graph level, beta reduction says that an explicit application node and an inlined connection have the same pure meaning. The runtime may retain the connection for scheduling and provenance, but it should preserve denotation.

## Eta as transparent adapters

A component that only forwards an input to another component is extensionally redundant:

\[
\lambda x.\;f\;x\equiv_\eta f.
\]

A PBUI example is an adapter tile whose only behavior is to expose the same read-only document port under another local name. If the adapter adds no logging, authority boundary, timing, caching, or rendering, eta suggests it can be erased.

The side conditions matter. A wrapper that records trace entries, changes lifetime, performs authorization, or creates a fresh reference is not eta-equivalent to the wrapped component.

## Products and multi-port boundaries

A component with several inputs can be curried:

\[
A\times B\to C
\]

or:

\[
A\to(B\to C).
\]

A port schema is usually product-like because all ports are named and available simultaneously. Actions are often curried because partial application corresponds naturally to interaction:

\[
\textsf{scheduleWith}:
\textsf{Contact}	o\textsf{Slot}	o\textsf{Command}.
\]

Right-clicking a contact partially applies the first argument:

\[
\textsf{scheduleWith}(c):
\textsf{Slot}	o\textsf{Command}.
\]

The shell then enters accept mode for a `Slot`. Selecting a slot completes the application.

## Extensionality as an API test

Eta-like laws yield practical property tests:

- wrapping and immediately forwarding a pure read port should not change observations;
- grouping ports into a product and projecting them should round-trip;
- currying and uncurrying an action should preserve command traces;
- an adapter marked `identity` should behave contextually like direct wiring.

These laws are more valuable than testing implementation-specific IDs or callback counts.

# Part III - Selection, actions, effects, and shared state {-}

# Accept mode as partial application and a typed continuation

## Actions with missing arguments

The supplied PBUI foundation makes a strong interaction claim: an action may begin on one object and then request another typed object from any visible tile. This is naturally expressed by currying.

For example:

\[
\textsf{fileActionItem}:
\textsf{ActionItem}	o\textsf{Project}	o\textsf{Command}.
\]

After the user invokes the action on \(a:\textsf{ActionItem}\), the shell holds:

\[
\textsf{fileActionItem}\;a:
\textsf{Project}	o\textsf{Command}.
\]

The next click supplies a project \(p\), producing:

\[
\textsf{fileActionItem}\;a\;p.
\]

The same pattern describes scheduling a contact in a calendar slot, labeling a thread, or attaching a transcript to a message.

## The pending function interpretation

A minimal semantic state for accept mode is:

```ts
interface PendingAccept<A, R> {
  query: Query<A>;
  prompt: string;
  continueWith(value: A): R;
  abort(): R;
}
```

The continuation has type:

\[
k:A\to R.
\]

A visible occurrence offering \(v:A\) is acceptable when it satisfies the query. Clicking it applies \(k\) to \(v\). Escape invokes the abort continuation.

This yields a more precise account than “global mode.” The shell stores a typed continuation and an extensional description of values that may be supplied to it.

## Evaluation contexts and holes

An evaluation context is a term with one hole:

\[
E[-].
\]

If the system is waiting for a value of type \(A\), the interaction state can be regarded as a typed hole:

\[
E[-]:A\Rightarrow R.
\]

Selecting \(v:A\) fills the hole:

\[
E[v].
\]

This viewpoint is useful for composition. A multi-step workflow contains nested or sequenced holes. It also clarifies why the active context should own cancellation and resolution: only the context that introduced the hole may fill or discard it.

## Delimited continuations

Some interactions suspend a computation, expose the rest of the UI, and later resume after a selection. This resembles delimited control. The continuation from the selection point to the end of the workflow is captured under an interaction delimiter.

A direct-style API:

```ts
const project = await accept(ProjectQuery);
return dispatch(FileUnder(actionItem, project));
```

can be translated to continuation-passing style:

```ts
accept(ProjectQuery, project =>
  dispatch(FileUnder(actionItem, project)),
);
```

The system need not expose continuation operators publicly. The semantic model matters because it makes one-shot resolution, cancellation, stale continuation invalidation, and nested interaction scopes explicit.

## Acceptance evidence

A raw value is sometimes insufficient. The action may need evidence that the selected object satisfied the exact query and revision:

\[
\Sigma(v:A).\;\textsf{Satisfies}(v,q,r).
\]

This is a dependent pair: a value plus a proof or checkable certificate. The command kernel can validate the evidence or recheck the condition if the world has changed.

```ts
interface Accepted<A> {
  value: A;
  subjectKey: SubjectKey;
  occurrenceId: OccurrenceId;
  queryId: QueryId;
  revision: Revision;
  evidence: AcceptanceEvidence;
}
```

The lambda-calculus connection here is Curry-Howard-like: the selected value inhabits a type refined by the query. TypeScript cannot generally verify the proof statically, but the runtime can carry a certificate generated by a small trusted query evaluator.

# Presentation types, polymorphism, and dictionary passing

## Generic actions as polymorphic terms

An action such as “Inspect” applies to many presentation types. Its idealized type is:

\[
\forall A.\;\textsf{Subject}\;A\to\textsf{Command}.
\]

True parametricity would prevent the implementation from treating contacts, events, and tasks differently unless type-specific structure is passed explicitly. In practice, inspection requires a descriptor or schema dictionary:

\[
\forall A.\;\textsf{Descriptor}\;A
\to\textsf{Subject}\;A
\to\textsf{Command}.
\]

This is dictionary passing, the semantic pattern behind type classes and many generic registries.

```ts
interface Descriptor<A> {
  label(value: A): ReactNode;
  describe(value: A): unknown;
  identity(value: A): SubjectKey;
}

function inspect<A>(
  descriptor: Descriptor<A>,
  value: A,
): Command;
```

The registry maps a runtime sort witness to its dictionary.

## Parametricity as a plugin discipline

Reynolds's abstraction theorem characterizes uniform behavior of polymorphic programs through logical relations (Reynolds 1983). Applied to PBUI, parametricity suggests useful restrictions:

- a generic binding serializer should not branch on hidden payload representation;
- a generic identity-link compiler should depend on contract evidence, not application-specific values;
- a generic projection should preserve relations between equivalent resource implementations;
- a plugin that only receives an abstract `Binding<A>` cannot forge or inspect an `A` without provided operations.

TypeScript's structural type system and escape hatches do not enforce full parametricity. Library boundaries, opaque constructors, branded IDs, and code review can approximate it. A proof model can state the stronger theorem.

## Heterogeneous menus

A menu containing actions for subjects of different types can be packaged existentially:

\[
\exists A.\;\textsf{Subject}\;A
\times
\textsf{ActionSet}\;A.
\]

Opening the package reveals a type witness, subject, and actions that agree on \(A\). This is safer than storing an untyped object and a list of callbacks that perform unchecked casts.

## Type inference and principal contracts

Milner's work on polymorphic type inference showed how a language can infer principal types for a useful functional core (Milner 1978). A port graph compiler can borrow the idea of constraints and unification, but P06 contracts are not simply Hindley-Milner types.

A connection can generate constraints:

\[
A_{out}=A_{in},
\qquad
m_{out}\preceq m_{in},
\qquad
a_{out}\models a_{in},
\]

along with multiplicity and lifetime conditions. Some fields admit equality; others admit subtyping, capability entailment, or protocol compatibility. The compiler should report the solved substitution and remaining obligations rather than collapsing everything into one Boolean `compatible` result.

# State, references, and store-passing semantics

## Why pure substitution is insufficient

Consider two independent document ports:

\[
c:\operatorname{Ref}D,
\qquad
p:\operatorname{Ref}D.
\]

Suppose both currently contain `doc-A`. Pure value semantics sees equality:

\[
!c=!p=\textsf{doc-A}.
\]

Yet a write to \(c\) need not affect \(p\). P06's identity link is intended to change that future behavior. Therefore its meaning concerns locations and transitions, not just current values.

## Explicit store semantics

A stateful expression can be evaluated with a store:

\[
\langle M,\sigma\rangle\Downarrow\langle V,\sigma'\rangle.
\]

The store maps locations to values:

\[
\sigma:L\rightharpoonup V.
\]

Operations include:

\[
\textsf{read}:\operatorname{Ref}A\to A
\]

and:

\[
\textsf{write}:\operatorname{Ref}A\to A\to 1.
\]

After quotient compilation, local ports project to locations:

\[
\pi:P\to L.
\]

The link-coherence invariant is:

\[
p\sim r\Longrightarrow\pi(p)=\pi(r).
\]

It follows that all reads and writes through linked projections address the same store location.

## State monad

State can be encoded using a monad:

\[
T A = S\to(A\times S).
\]

A binding operation such as `set` has a denotation in \(T1\). A composed component has type:

\[
\llbracket\Gamma\rrbracket\to T\llbracket O\rrbracket.
\]

Moggi's computational lambda calculus separates pure values from computations through such monadic structure (Moggi 1991). For PBUI, this separation prevents a port value from being confused with an operation that reads or mutates a port.

## Local state and abstraction

A binding ID should usually be abstract. Clients receive operations, not direct access to the global store:

```ts
interface BindingProjection<A> {
  bindingId: BindingId;
  get(): A;
  set(value: A): Result<void, WriteError>;
  subscribe(listener: (value: A) => void): Unsubscribe;
}
```

Two different internal implementations can be contextually equivalent:

- one shared signal;
- a Redux path;
- a transactional cell;
- a remote replicated register.

Logical relations for local state are relevant because clients can observe behavior over time without seeing the internal location representation (Pitts and Stark 1993; Pitts 2000).

## Generativity and freshness

Creating an unlinked binding allocates a fresh location:

\[
\textsf{newRef}:A\to T(\operatorname{Ref}A).
\]

Freshness is observable only through future behavior, not through a printable pointer. Two fresh cells initialized to the same value remain distinct. Import, duplicate, and unlink operations must specify whether they allocate fresh locations or preserve aliases.

# Call-by-value, call-by-name, and call-by-need

## Evaluation strategy matters

The ordinary beta rule does not determine when an argument is evaluated or whether repeated uses share work.

**Call-by-value** evaluates the argument before substitution.

**Call-by-name** substitutes an unevaluated argument and may re-evaluate it at each use.

**Call-by-need** evaluates on first demand and shares the result.

A live binding resource resembles call-by-need in one important respect: many occurrences refer through an indirection to one shared node. This does not make a PBUI binding a lazy thunk, but it makes graph semantics more faithful than tree substitution.

## Heap semantics for sharing

Launchbury's natural semantics for lazy evaluation models sharing through an explicit heap of bindings (Launchbury 1993). A judgment has a heap before and after evaluation. Ariola and Felleisen developed a call-by-need lambda calculus whose equations correspond more closely to sharing implementations than ordinary call-by-name substitution (Ariola and Felleisen 1997).

A simplified P06 runtime has the same architectural shape:

```text
port occurrence -> binding ID -> heap/resource entry -> value
```

The indirection ensures that updates or computations are shared. The comparison is an implementation analogy, not an identity of semantics: a PBUI binding can be eagerly mutable, externally synchronized, and long lived, whereas a call-by-need heap entry represents deferred computation.

## Graph reduction and common subexpressions

Suppose a document computation feeds three views. Textual substitution can produce three copies:

\[
M[N/x,N/y,N/z].
\]

A graph representation retains one node for \(N\) and three edges to it. P06's quotient graph similarly retains many port occurrences pointing to one resource.

The graph distinction becomes semantically observable when \(N\) is effectful or expensive. Therefore a component compiler should specify whether a directional connection passes:

- a value;
- a thunk;
- a stream;
- a reference;
- a computation to be rerun;
- or a memoized computation.

Payload type alone cannot answer this.

## Sharing is not equality saturation

A shared graph node means several edges point to one representation. It does not imply that arbitrary equivalent expressions are merged. Equality saturation and hash-consing are separate optimizations. Semantic subject identity, binding identity, and common-subexpression identity should remain distinct namespaces.

# Call-by-push-value as a better core for PBUI

## “A value is; a computation does”

Call-by-push-value separates value types from computation types and provides a common semantic basis for call-by-value and call-by-name (Levy 2001). The distinction is well suited to PBUI:

- a `DocumentId` is a value;
- reading a remote binding is a computation;
- a `Binding<DocumentId>` is a value that affords computations;
- dispatching a command is a computation;
- a rendered occurrence description can be a value;
- mounting, subscribing, and focusing are computations.

The surface API often obscures this distinction because JavaScript methods can perform effects at any time.

## A CBPV-inspired port model

Let \(A\) be a value type. A read operation can return a computation \(F A\), while a subscription can expose a thunked ongoing computation. A simplified signature is:

\[
\begin{aligned}
\textsf{get}&:\textsf{Binding}\;A\to F A,\\
\textsf{set}&:\textsf{Binding}\;A\to A\to F 1,\\
\textsf{watch}&:\textsf{Binding}\;A\to F(\textsf{Stream}\;A).
\end{aligned}
\]

A read-only snapshot port might carry \(A\). A live cell port carries `Binding A`. A derived stream port carries `Stream A`. The contract can distinguish these at the type level rather than through metadata strings.

## Why this improves compiler reasoning

The compiler can answer:

- whether a connection duplicates a value or a computation;
- whether linking introduces shared state;
- whether an adapter is pure;
- which edges may be reordered;
- what must be handled by an effect interpreter;
- where memoization changes behavior.

A CBPV-style intermediate representation is therefore a plausible core language for P06 plus the broader PBUI workflow system.

## Thunks, forcing, and dormant components

A component not currently mounted may still have semantic state. Its rendering computation can be thunked:

\[
U(F\;\textsf{Widget}).
\]

Mounting forces it. Virtualization can discard the rendered occurrence while retaining subject and binding values. This separation helps avoid treating React mount state as domain existence.

# Merge and unlink policies as effects

## Quotients do not choose values

Suppose two independent resources hold:

\[
\sigma(\ell_c)=\textsf{doc-A},
\qquad
\sigma(\ell_p)=\textsf{doc-B}.
\]

Adding a link says that the corresponding ports will have one future binding class. It does not determine whether the merged resource should contain `doc-A`, `doc-B`, a conflict, or another value.

A merge policy is an explicit computation:

\[
\textsf{merge}:A\times A\to T A.
\]

Examples include:

\[
\textsf{requireEqual},
\quad
\textsf{preferLeft},
\quad
\textsf{preferRight},
\quad
\textsf{join},
\quad
\textsf{askUser}.
\]

Only `join` under a declared semilattice can be expected to be associative, commutative, and idempotent. Source preference is intentionally ordered.

## Linking as a transaction

A sound link operation should be atomic:

1. validate contracts and authority;
2. calculate the candidate quotient;
3. identify resource classes affected by the merge;
4. run the merge policy;
5. allocate or retain a persistent binding identity;
6. commit topology and value changes together;
7. emit provenance and notifications.

This is an effectful command, not a pure quotient computation. Its pure portion can calculate the new equivalence relation; its effectful portion changes durable state.

## Unlinking is noninvertible

Neither substitution nor quotienting is generally invertible. From

\[
M[N/x]
\]

one cannot in general reconstruct the original \(M\) and \(N\). Likewise, after two resources have been merged and updated, the quotient does not remember their previous independent values.

An unlink policy is therefore:

\[
\textsf{split}:A\times\textsf{History}\to T(A\times A).
\]

Possible policies include:

- copy the current shared value to every new class;
- reset one or more classes;
- restore values from retained history;
- ask the user;
- reject the split.

The durable state must retain generating link edges, not only the collapsed partition, because removing one edge may or may not separate the graph.

## Provenance as explicit syntax

A reversible editor should retain a syntax tree or event history of topology changes. Quotient classes are derived semantics. This mirrors a general programming-language lesson: normalization can erase intensional structure needed for debugging, source maps, and inverse operations. Keep the source program; treat the normalized plan as a cache.

# Algebraic effects and handlers for PBUI workflows

## Reifying operations

Rather than performing interaction and binding effects directly in callbacks, define operations:

```ts
type PBUIEffect<A> =
  | SelectEffect<A>
  | ReadBindingEffect<A>
  | WriteBindingEffect<A>
  | LinkPortsEffect<A>
  | UnlinkPortsEffect<A>
  | DispatchCommandEffect<A>
  | ConfirmEffect<A>;
```

A workflow is a free program over this signature. A handler gives meaning to each operation.

Plotkin and Pretnar describe algebraic effects as operations presented by equational theories and handlers as interpretations induced through the universal property of free models (Plotkin and Pretnar 2013). The connection is especially direct for PBUI because selection, state, nondeterminism, exceptions, and I/O are all interaction effects.

## The link workflow

A link gesture can be written declaratively:

```ts
const linkDocuments = workflow(function* (source) {
  const target = yield* select(
    compatibleDocumentPorts(source),
    "Choose a document selector",
  );

  const merge = yield* resolveMergePolicy(source, target);

  return yield* linkPorts({
    source,
    target,
    merge,
  });
});
```

The production handler uses DOM occurrences, the P06 compiler, transactions, and persistence. A test handler supplies deterministic choices. A model-checking handler explores all permitted targets and merge outcomes.

## Handler laws

Handlers should satisfy explicit laws. For example:

- aborting a selection performs no link mutation;
- handling a pure return preserves its value;
- sequential writes to one binding follow the declared update algebra;
- an identity handler on commands preserves command traces;
- replaying a deterministic trace produces an observationally equivalent state.

These are equations in an effectful lambda calculus, not informal callback conventions.

## Scoped effects

“Run this workflow while a typed input context is active” is a scoped operation. The context affects a subcomputation and must be removed on completion, failure, or cancellation. Ordinary first-order algebraic effects may need extension for scoped or higher-order operations. Interaction trees or explicit state machines are another robust representation.

# Part IV - Time, behavior, change, and composition {-}

# Coalgebraic interaction and the limits of term reduction

## A UI session is potentially infinite

A lambda term is often studied through reduction toward a value or normal form. An interactive PBUI session may continue indefinitely. It receives clicks, keyboard events, repository updates, remote messages, and timer events; it emits rendered observations, commands, and effects.

A deterministic Moore-style machine can be represented as:

\[
\gamma:S\to O\times S^I,
\]

where \(S\) is state, \(O\) is current observation, and \(I\) is input. Given a state, the coalgebra reveals what the user currently sees and how every possible input selects a successor state.

For an effect-emitting Mealy-style machine:

\[
\gamma:S\to(O\times E\times S)^I.
\]

This is a better semantic form for ongoing interaction than an ordinary terminating lambda term.

## Lambda calculus still participates

Coalgebra does not replace lambda calculus. The transition and observation functions are lambda-definable functions:

\[
\textsf{observe}:S\to O,
\qquad
\textsf{step}:S\to I\to(E\times S).
\]

The lambda calculus organizes higher-order composition, while coalgebra organizes potentially unbounded behavior.

A complete PBUI semantics therefore has both inductive and coinductive aspects:

```text
inductive syntax:
  queries, commands, component declarations, effect programs

coinductive behavior:
  event traces, streams, ongoing sessions, subscriptions
```

## Bisimulation and compiler replacement

Two machines can be behaviorally equivalent even when their states differ. A relation \(R\subseteq S_1\times S_2\) is a bisimulation when related states have matching observations and corresponding inputs lead to related successor states.

P06 has an obvious candidate:

- machine 1 recomputes quotient classes with a transparent graph traversal;
- machine 2 uses union-find, stable-ID matching, and incremental caches.

The states differ internally. The desired theorem is that they are bisimilar under the public protocol:

- `bindingOf` gives corresponding classes;
- reads and writes have matching results;
- link and unlink commands produce corresponding semantic plans;
- traces differ only in explicitly hidden optimization events;
- serialization agrees up to permitted ID renaming.

## One-shot selection as a submachine

An accept operation can be modeled by states:

```text
Idle
  -> Selecting(query, continuation)
      -> Resolving(candidate)
          -> Idle with result
      -> Cancelled
          -> Idle with null
```

The invariant “resolve at most once” is a transition-system property. It is not guaranteed merely because the continuation has a function type. A linear or affine continuation type would strengthen the static model by allowing the continuation to be consumed at most once.

## Interaction trees

Interaction Trees represent recursive effectful programs as coinductive trees of visible events and continuations. They support interpreters and equivalence through weak bisimulation. A PBUI workflow language can use the same separation:

\[
\textsf{Ret}(v),
\quad
\textsf{Tau}(t),
\quad
\textsf{Vis}(e,k).
\]

The lambda-calculus part appears in the continuation \(k\), while the coinductive tree accounts for unbounded interaction. This is especially suitable for mechanizing cancellation, asynchronous tasks, and trace refinement.

# Incremental and differential lambda calculus

## Re-evaluation versus update

A presentation system repeatedly computes nearly the same observations after small changes:

- a port joins or leaves a binding class;
- a document value changes;
- one occurrence mounts or unmounts;
- a capability is revoked;
- a query parameter changes.

A naive implementation recomputes all classes, selectors, actions, and widgets. An incremental implementation transforms changes in inputs into changes in outputs.

## Derivatives of programs

Incremental lambda calculus equips each type \(A\) with a notion of change \(\Delta A\) and an update operation:

\[
\oplus_A:A\times\Delta A\to A.
\]

For a function

\[
f:A\to B,
\]

its derivative has a form such as:

\[
Df:A\to\Delta A\to\Delta B
\]

and satisfies the correctness law:

\[
f(a\oplus da)=f(a)\oplus Df(a)(da).
\]

Cai, Giarrusso, Rendel, and Ostermann give a static transformation for higher-order languages and prove correctness for families of simply typed lambda calculi (Cai et al. 2014).

## Applying the law to binding compilation

Let:

\[
\textsf{compile}:G\to Q
\]

map a port/link graph to a quotient plan. A graph edit \(dG\) should yield a plan edit:

\[
D\textsf{compile}:G\to\Delta G\to\Delta Q.
\]

Correctness requires:

\[
\textsf{compile}(G\oplus dG)
=
\textsf{compile}(G)\oplus
D\textsf{compile}(G)(dG).
\]

For link insertion, union-find approximates this derivative efficiently. For deletion, the derivative is more complex because a connected component may split. The system may recompute the affected component while still satisfying the same semantic law.

## Incremental rendering

Let:

\[
\textsf{observe}:Q\times\sigma\times O_{mount}	o U
\]

produce UI observations. Changes to one binding value should update only subscribers to its class. Changes to topology should invalidate only affected projections and their observations.

The lambda-calculus connection is important because higher-order query and rendering combinators can be incrementalized compositionally when their change actions are known. Opaque JavaScript closures force conservative invalidation.

## Normalization and staging

The quotient compiler is also a staging operation. Component and port declarations are relatively static; resource values and interactions are dynamic. The compiler partially evaluates static wiring into a runtime plan.

A staged language can distinguish:

```text
compile-time values:
  contracts, port graph, link equations, query syntax

runtime values:
  document IDs, mounted occurrences, current capabilities, user events
```

Normalization-by-evaluation and partial evaluation offer conceptual tools for producing canonical plans while preserving semantics. Again, generated binding IDs must remain outside the definitional equality used for normalization.

# Open-component composition and categorical structure

## The cartesian closed core

Simply typed lambda calculus with products corresponds to cartesian closed categories. Types are objects, terms in context are morphisms, product types interpret contexts, and function types are exponentials.

A pure open component with inputs \(\Gamma\) and output \(A\) denotes:

\[
\llbracket C\rrbracket:
\llbracket\Gamma\rrbracket\to\llbracket A\rrbracket.
\]

Sequential connection is composition. Parallel composition uses products. Abstraction and application use the exponential adjunction.

This gives a strong semantic nucleus for component APIs.

## Why cospans enter

A component can have multiple named inputs and outputs and can be composed by wiring a shared boundary. Open-system formalisms represent such systems as cospans:

\[
L(I)\longrightarrow C\longleftarrow L(O).
\]

Composing two open systems along a matching boundary uses a pushout. Structured cospans provide a categorical framework for systems with typed interfaces and compositional wiring (Baez and Courser 2020).

The lambda-calculus and cospan views emphasize different operations:

- lambda calculus: substitution, abstraction, higher-order functions;
- cospans: parallel open boundaries, network gluing, explicit topology.

A PBUI architecture benefits from both. A component can have an internal lambda-calculus semantics while the workspace graph composes component boundaries through cospans or related structures.

## Frobenius structure and wiring

Hypergraph categories equip each interface object with operations that copy, merge, create, and discard wires under specific equations. These diagrammatic operations resemble structural rules:

- copy corresponds to contraction;
- discard corresponds to weakening;
- merge corresponds to identifying wires;
- create corresponds to a unit.

For immutable information, a special commutative Frobenius structure can model undirected connectivity. For mutable state and authority, blindly applying these equations is dangerous. A write capability is not necessarily copyable or mergeable. The contract must determine which diagrammatic operations are legal.

## Pushout as coproduct plus coequalizer

In concrete categories, a pushout of

\[
X\xleftarrow{f}B\xrightarrow{g}Y
\]

can often be formed by taking the coproduct \(X+Y\) and quotienting by equations:

\[
\iota_X(f(b))\sim\iota_Y(g(b)).
\]

Thus coequalizers appear naturally in whole-component composition as well as in local port identification. The P06 quotient compiler can be regarded as one layer of a broader structured-cospan compiler.

## Models reverse some constructions

A recurring categorical subtlety is variance. Gluing syntax by a colimit can correspond to compatible models described by a limit. The port quotient example made this concrete:

\[
P\to Q
\]

induces:

\[
V^Q\to V^P.
\]

The global binding environments form the compatible subspace of local assignments. This is why the paper's use of both coequalizers and pullbacks is not redundant: one acts on interface presentation, the other characterizes agreeing semantic states.

# Linear, affine, and session-typed ports

## Beyond cartesian contexts

Ordinary lambda contexts allow variables to be copied and discarded. Port contracts often demand a stricter discipline. Substructural type systems vary which structural rules are admissible:

| Discipline | Exchange | Weakening | Contraction |
|---|---:|---:|---:|
| linear | yes | no | no |
| affine | yes | yes | no |
| relevant | yes | no | yes |
| cartesian | yes | yes | yes |

A PBUI compiler can assign each port capability a structural discipline.

## Read and write capabilities

A cell can be decomposed into capabilities:

\[
\textsf{Read}\;A,
\qquad
\textsf{Write}\;A.
\]

Read capability may be duplicable:

\[
!\textsf{Read}\;A.
\]

An exclusive writer may be linear:

\[
\textsf{Write}\;A.
\]

A shared writer is safe only with an arbitration or merge protocol. The P06 `mode` field can be elaborated into these capability types rather than remaining a string checked by ad hoc conditionals.

## Multiplicity

A port with multiplicity `one`, `optional`, or `many` corresponds to different type constructors:

\[
A,
\qquad
1+A,
\qquad
\operatorname{List}A.
\]

Identity linking should preserve the intended multiplicity semantics. Identifying an optional port with a required port may require a proof that the source is always present, not merely matching payload types.

## Temporal protocol and session types

Some ports are not state cells. An event source and event sink communicate through a protocol. Session types describe sequences of sends, receives, choices, and termination. A selection workflow might have a protocol:

\[
\oplus\{
\textsf{select}:A.\textsf{done},
\textsf{cancel}:\textsf{done}
\}.
\]

A remote link transaction may follow:

```text
client -> server : ProposeLink
server -> client : Accepted | Conflict | Rejected
client -> server : ResolveConflict | Abort
server -> client : Committed | Stale
```

Two ports carrying the same payload are not identity-compatible when their session protocols differ. This reinforces the broader P06 contract.

## Authority as a linear or affine resource

Capabilities can be modeled as values that authorize operations. A one-use authorization token is affine or linear. A persistent role capability may be duplicable but revocable through an external authority system.

The type of a privileged command can require evidence:

\[
\textsf{LinkPorts}:
\textsf{CanLink}(p,q)
\multimap
\textsf{Command}.
\]

The UI may derive provisional evidence for display, but the command kernel must validate current authority at execution time.

# Part V - A core calculus for PBUI and P06 {-}

# The calculus \(\lambda_{\mathrm{PB}}\)

## Purpose and scope

This chapter proposes a small core calculus that makes the preceding correspondences executable. It is not intended to replace TypeScript as an application language. It is an intermediate semantics for validating APIs and compiler transformations.

The calculus combines:

- simply typed values and functions;
- named semantic subjects;
- typed port occurrences;
- explicit binding references;
- stateful computations;
- selection and command effects;
- graph-level link declarations;
- occurrence-level observations.

The calculus intentionally excludes CSS, layout geometry, and React reconciliation.

## Types

Let \(S\) range over semantic subject sorts and \(\tau\) over complete port contracts.

Value types are:

\[
\begin{aligned}
A,B ::={}& 1
\mid \textsf{Bool}
\mid \textsf{String}
\mid \textsf{Key}\;S
\mid \textsf{Subject}\;S\\
&\mid \textsf{Port}\;\tau
\mid \textsf{Binding}\;\tau
\mid \textsf{Ref}\;A
\mid A\times B
\mid A+B
\mid A\to C.
\end{aligned}
\]

Computation types are:

\[
C ::= F A.
\]

The notation follows the call-by-push-value distinction: values can be passed and stored; computations may read state, emit effects, or fail.

A complete contract can be represented abstractly as:

\[
\tau=\textsf{Cell}(A,m,a,k,u,l)
\]

or:

\[
\tau=\textsf{Stream}(A,dir,a,k,l).
\]

Cell and stream ports are different protocol families and cannot be identity-linked merely because their payload type \(A\) agrees.

## Values and computations

Values include:

\[
\begin{aligned}
V ::={}& x
\mid ()
\mid \lambda x:A.M
\mid (V_1,V_2)
\mid \textsf{inl}\;V
\mid \textsf{inr}\;V\\
&\mid \textsf{subject}(S,k)
\mid \textsf{port}(c,n)
\mid \textsf{binding}(b).
\end{aligned}
\]

Computations include:

\[
\begin{aligned}
M,N ::={}& \textsf{return}\;V
\mid V\;W
\mid \textsf{let}\;x\leftarrow M\;\textsf{in}\;N\\
&\mid \textsf{get}\;V
\mid \textsf{set}\;V\;W
\mid \textsf{select}\;q
\mid \textsf{dispatch}\;c\\
&\mid \textsf{link}\;p\;r\;\mu
\mid \textsf{unlink}\;e\;\nu
\mid \textsf{observe}\;o.
\end{aligned}
\]

Here \(\mu\) is a merge-policy value and \(\nu\) an unlink-policy value.

## Typing rules for state

Representative rules are:

\[
\frac{\Gamma\vdash r:\textsf{Ref}\;A}
     {\Gamma\vdash\textsf{get}\;r:F A}
\]

and:

\[
\frac{\Gamma\vdash r:\textsf{Ref}\;A
      \qquad
      \Gamma\vdash v:A}
     {\Gamma\vdash\textsf{set}\;r\;v:F1}.
\]

A binding projection is typed by the compiled plan:

\[
\frac{G\vdash p:\textsf{Port}\;\tau
      \qquad
      \textsf{compile}(G)=Q}
     {Q\vdash\textsf{project}(p):\textsf{Binding}\;\tau}.
\]

The runtime can expose a reference from the binding:

\[
\frac{Q\vdash b:\textsf{Binding}(\textsf{Cell}(A,\ldots))}
     {Q\vdash\textsf{resource}(b):\textsf{Ref}\;A}.
\]

## Typing identity links

Let \(\tau\equiv_{id}\tau'\) mean that the two contracts are identity-compatible. The rule is:

\[
\frac{
  G\vdash p:\textsf{Port}\;\tau
  \qquad
  G\vdash r:\textsf{Port}\;\tau'
  \qquad
  \tau\equiv_{id}\tau'
  \qquad
  \Gamma\vdash\mu:\textsf{MergePolicy}\;\tau
}{
  \Gamma;G\vdash
  \textsf{link}\;p\;r\;\mu:
  F\textsf{LinkResult}
}.
\]

The judgment prevents cross-contract identity links. A transformed connection has a different rule requiring a function or process from the source protocol to the target protocol.

## Typing selection

A query carries its result sort:

\[
q:\textsf{Query}\;A.
\]

The selection operation has type:

\[
\frac{\Gamma\vdash q:\textsf{Query}\;A}
     {\Gamma\vdash\textsf{select}\;q:F(1+A)}.
\]

The sum represents cancellation or successful selection. A proof-relevant variant returns:

\[
F(1+\Sigma(v:A).\textsf{Evidence}(q,v)).
\]

## Component judgments

A component declaration is typed as:

\[
\Gamma_{in};\Sigma_{local}
\vdash
C:
F(\Gamma_{out}\times O).
\]

The boundary contexts contain port values or capabilities, while \(\Sigma_{local}\) contains component-private state references. Composition supplies or links entries in \(\Gamma_{in}\) and routes entries from \(\Gamma_{out}\).

## Occurrences

A mounted occurrence is not a value constructor for the domain subject. It is an observation fact:

\[
\textsf{Presents}(o,s:S,\varphi),
\]

where \(\varphi\) records surface metadata such as visibility and reachability. Registering and unregistering occurrences are effects on the observation database. Selection queries range over these facts.

This separation means that unmounting a widget removes one occurrence without destroying its subject, component state, or binding.

# Compilation and operational semantics

## Source graph

A source graph is:

\[
G=(P,E,\kappa,\iota),
\]

where:

- \(P\) is a finite set of port occurrences;
- \(E\) is a finite set of explicit link declarations;
- \(\kappa:P\to\textsf{Contract}\) assigns contracts;
- \(\iota:P\to\textsf{InitialProposal}\) records current resource proposals.

Each link \(e\in E\) has endpoints \(s(e),t(e)\in P\), a merge policy, provenance, and authorization evidence.

## Compile function

The pure compiler performs:

\[
\textsf{compile}:G\to\textsf{Result}(Q,D),
\]

where \(Q\) is a semantic plan and \(D\) diagnostics.

For every contract fiber \(\tau\), it:

1. validates that each link remains within the fiber;
2. computes the equivalence closure generated by its links;
3. canonicalizes member sets for comparison;
4. matches new classes against prior persistent identities when recompiling;
5. emits a projection map \(q_\tau:P_\tau\to Q_\tau\);
6. reports merges and splits requiring runtime policy.

The compiler does not mutate resources.

## Runtime plan

A runtime plan is:

\[
R=(Q,q,b,\ell,\sigma),
\]

where:

- \(Q\) is the family of binding classes;
- \(q\) maps local ports to classes;
- \(b\) assigns stable external binding IDs;
- \(\ell\) assigns runtime locations;
- \(\sigma\) stores current values.

A projection is derived:

\[
\pi(p)=\ell(q(p)).
\]

## Reading and writing

The read transition is:

\[
\frac{\pi(p)=\ell\qquad\sigma(\ell)=v}
{\langle\textsf{getPort}\;p,R\rangle
 \to
 \langle\textsf{return}\;v,R\rangle}.
\]

The write transition is:

\[
\frac{\pi(p)=\ell\qquad\textsf{CanWrite}(p,v,R)}
{\langle\textsf{setPort}\;p\;v,R\rangle
 \to
 \langle(),R[\sigma(\ell):=v]\rangle}.
\]

If \(q(p)=q(r)\), both operations address the same location.

## Link transition

A successful link command is a transaction:

\[
\langle\textsf{link}\;p\;r\;\mu,R\rangle
\to
\langle\textsf{linked}\;b,R'\rangle.
\]

The premises include:

\[
\kappa(p)\equiv_{id}\kappa(r),
\]

current authorization, a successfully compiled candidate graph, and successful merge-policy evaluation.

If the merge policy fails, the source graph and resource state remain unchanged:

\[
\langle\textsf{link}\;p\;r\;\mu,R\rangle
\to
\langle\textsf{conflict},R\rangle.
\]

This atomicity rule is essential. A half-committed quotient would expose ports as linked while retaining incompatible resources.

## Unlink transition

Removing an explicit edge \(e\) yields a new source graph \(G-e\). The compiler recomputes affected components. If one old binding class splits into \(Q_1,\ldots,Q_n\), the unlink policy initializes a resource for each class.

For `copy-current`, if the old value is \(v\), then:

\[
\sigma'(\ell_i)=v
\qquad
\textsf{for each new class }Q_i.
\]

Other classes and resources remain unchanged.

## Selection transition

When the interaction machine is waiting on query \(q:A\), activating occurrence \(o\) succeeds only when the semantic runtime derives:

\[
\textsf{Accepts}(q,o,v,evidence).
\]

The transition resumes the stored continuation:

\[
\langle\textsf{Selecting}(q,k),\textsf{Activate}(o)\rangle
\to
\langle k(v,evidence),\textsf{Idle}\rangle.
\]

A second activation cannot reuse the consumed continuation.

# Core theorem catalogue

## Contract-fiber preservation

**Theorem 1 - Fiber preservation.** If `compile(G)` succeeds and \(q(p)=q(r)\), then:

\[
\kappa(p)\equiv_{id}\kappa(r).
\]

**Proof idea.** Every generating edge is checked for identity compatibility. The relation is closed by reflexivity, symmetry, and transitivity. Identity compatibility must itself be an equivalence relation, or the compiler must normalize contracts to a canonical identity fiber before computing closure.

This theorem prevents a quotient class from containing a document cell and a row-selection stream.

## Quotient soundness and completeness

**Theorem 2 - Quotient soundness.** Every declared link is identified:

\[
q(s(e))=q(t(e)).
\]

**Theorem 3 - Quotient completeness.** If \(q(p)=q(r)\), there is a finite path of declared links connecting \(p\) and \(r\), modulo symmetry.

For a graph-traversal compiler, completeness follows from connected-component construction. For union-find, it follows from correspondence between union operations and the generated equivalence closure.

## Projection coherence

**Theorem 4 - Linked projection coherence.** If \(q(p)=q(r)\), then:

\[
\pi(p)=\pi(r).
\]

Consequently, for every reachable store \(\sigma\):

\[
\textsf{read}(p,\sigma)=\textsf{read}(r,\sigma).
\]

**Proof.** By definition \(\pi=\ell\circ q\). Apply congruence of \(\ell\) to equality of quotient classes.

This theorem is stronger than testing synchronized dropdown values after one event. It states that aliasing is structural for every reachable state, provided all access passes through projections.

## Universal factorization

**Theorem 5 - Factorization.** Let \(g:P_\tau\to X\) respect every generated link. There exists a unique \(\bar g:Q_\tau\to X\) such that:

\[
g=\bar g\circ q_\tau.
\]

This is the coequalizer universal property. In a finite implementation:

\[
\bar g([p])=g(p)
\]

is well defined because \(g\) is constant on classes.

## Alpha-invariance

**Theorem 6 - Alpha-invariance.** Let \(\pi:P\cong P'\) be a contract-preserving renaming that transports links. Then compiled plans are isomorphic:

\[
\textsf{compile}(\pi G)\cong\pi(\textsf{compile}(G)).
\]

Public observations that do not intentionally expose generated names are equal under this isomorphism.

The proof establishes that semantic classes depend on incidence and contracts, not lexical port IDs.

## Link-order invariance

**Theorem 7 - Link-order invariance.** Reordering the declarations in \(E\) does not change the quotient relation:

\[
P/{\sim_E}
\cong
P/{\sim_{\operatorname{perm}(E)}}.
\]

Internal union-find representatives and birth ordinals may differ. The canonical semantic plan, after sorting class members and abstracting generated IDs, must agree.

## Compiler refinement

Let \(C_{ref}\) be the graph-traversal compiler and \(C_{opt}\) the union-find compiler.

**Theorem 8 - Extensional compiler equivalence.** For every well-formed finite graph \(G\):

\[
\operatorname{canon}(C_{ref}(G))
=
\operatorname{canon}(C_{opt}(G)).
\]

A production proof may be replaced initially by differential property testing over generated graphs, while a formal proof establishes the underlying union-find invariant.

## Transaction atomicity

**Theorem 9 - Failed link atomicity.** If contract, authority, compilation, or merge validation fails, then the externally visible source graph, projection map, binding values, and persistent IDs remain unchanged.

This is a safety property of the command kernel, not of quotient mathematics.

## Unlink locality

**Theorem 10 - Unlink locality.** Removing an edge can change only the connected component that contained that edge's endpoints. Every other quotient class and resource projection is unchanged.

This theorem provides the invalidation frontier for an incremental compiler.

## Copy-current value preservation

**Theorem 11 - Copy-current preservation.** Immediately after unlinking under `copy-current`, every surviving endpoint reads the same value it read immediately before the operation.

Topology may split, but no local selector unexpectedly changes document.

## Selection single resolution

**Theorem 12 - One-shot acceptance.** A selection context reaches at most one successful or cancelled terminal transition.

A proof proceeds by an invariant that only the `Selecting` state contains the continuation and every terminal transition consumes it.

## Contextual equivalence of adapters

**Theorem 13 - Transparent adapter equivalence.** A pure, total, identity-typed adapter with no observations or effects is contextually equivalent to direct connection.

The theorem fails if the adapter logs, caches observably, changes scheduling, allocates fresh references, or narrows authority.

# Logical relations and proof principles

## Why type preservation is not enough

Type preservation proves that a well-typed transition remains well typed. It does not prove that two implementations of `Binding<A>` behave alike, that persistent IDs remain abstract, or that an optimized compiler preserves observations.

Logical relations interpret each type as a relation between implementations. For a base value type \(A\), the relation may be semantic equality. For function types:

\[
f\;R_{A\to B}\;g
\]

when related inputs produce related computations. For bindings:

\[
b_1\;R_{\textsf{Binding}A}\;b_2
\]

when their permitted sequences of reads, writes, subscriptions, links, and unlinks produce related observations.

## Kripke worlds for dynamic bindings

Stateful logical relations are often indexed by worlds describing allocated locations and their correspondence. P06 needs a world containing:

- related binding IDs;
- related runtime locations;
- related values by contract;
- related topology provenance;
- freshness obligations.

A link or unlink operation extends or transforms the world. The relation must be monotone under permitted future allocation and graph evolution.

This is the right framework for proving that two internal resource implementations are contextually equivalent while hiding their locations.

## Parametric binding clients

A client polymorphic in \(A\):

\[
\forall A.\;\textsf{Binding}\;A\to F\;\textsf{Bool}
\]

cannot manufacture or compare values of \(A\) without additional operations. It can observe binding identity only if the API exposes it. Parametricity therefore informs API minimality: exposing raw value representation or unstable resource IDs destroys useful free theorems.

## Proof by structural induction

Reified query and workflow languages support induction over syntax. For each constructor, prove:

- typing preservation;
- dependency-analysis soundness;
- optimizer correctness;
- evidence-checker soundness;
- incremental derivative correctness.

Opaque JavaScript nodes terminate the induction with an explicit assumption. The system should report this boundary rather than silently treating callbacks as certified terms.

## Fixed-point induction

Recursive subtype closure, action rules, translator reachability, or link-related facts can be defined as least fixed points. Once the immediate-consequence operator is monotone, invariants can be proved by fixed-point induction.

This layer is adjacent to, not identical with, lambda-calculus reduction. A lambda language can host a Datalog-like rule fragment, and its semantics can combine initial syntax with least-fixed-point interpretation.

# Mechanization in Lean

## Minimal formalization

A first Lean development should define:

```lean
inductive Contract where
  | primaryDocument
  | rowSelection
  | filter

inductive Port : Contract -> Type where
  | chartDocument    : Port .primaryDocument
  | pipelineDocument : Port .primaryDocument
  | chartSelection   : Port .rowSelection
```

The index makes an ill-typed identity relation between `chartDocument` and `chartSelection` unstateable.

The generated link relation is an inductive proposition closed under equivalence:

```lean
inductive Linked : {c : Contract} -> Port c -> Port c -> Prop where
  | refl  : Linked p p
  | edge  : DeclaredEdge p q -> Linked p q
  | symm  : Linked p q -> Linked q p
  | trans : Linked p q -> Linked q r -> Linked p r
```

Bindings are quotients by the resulting setoid:

```lean
abbrev Binding (c : Contract) :=
  Quotient (portSetoid c)
```

## The basic quotient theorem

```lean
theorem linked_ports_same_binding
    (h : Linked p q) :
    project p = project q := by
  exact Quotient.sound h
```

The factorization theorem uses `Quotient.lift`. This formalizes the universal property for functions constant on link classes.

## Correcting the widget theorem

A simplistic theorem may define:

```lean
def f : Binding .primaryDocument -> Widget
```

and conclude that linked ports show the same widget. That theorem is appropriate only for a **canonical binding widget**. It is not the general UI theorem.

The more accurate formalization separates resource sharing from local rendering:

```lean
def resourceOfBinding : Binding c -> Resource c

def renderAt : (p : Port c) -> Resource c -> Widget

def widgetAt (p : Port c) : Widget :=
  renderAt p (resourceOfBinding (project p))
```

The main theorem is:

```lean
theorem linked_ports_same_resource
    (h : Linked p q) :
    resourceOfBinding (project p) =
      resourceOfBinding (project q)
```

No theorem requires `widgetAt p = widgetAt q`; different ports may render the shared resource differently.

## Formalizing environments

For a finite port type and value type `V`, define:

```lean
abbrev PortEnv := (p : Port c) -> V
abbrev BindingEnv := Binding c -> V

def pullbackEnv (rho : BindingEnv) : PortEnv :=
  fun p => rho (project p)
```

Then prove:

```lean
theorem pullback_respects_links
    (rho : BindingEnv)
    (h : Linked p q) :
    pullbackEnv rho p = pullbackEnv rho q
```

and the converse factorization for every port environment respecting links.

## Graph compiler correspondence

The quotient definition gives an elegant specification but is not an executable high-performance graph compiler by itself. Define a finite graph implementation and prove:

```lean
connected g p q <-> LinkedFromEdges g p q
```

then:

```lean
sameComponent referenceCompiler p q
  <-> project p = project q
```

and finally correspondence for union-find.

## Operational model

A second phase defines:

```lean
structure Runtime where
  graph      : Graph
  plan       : Plan
  store      : Store
  interaction : InteractionState
```

Commands form an inductive type. A transition relation relates runtime, command, result, and next runtime. The main invariant is that the plan agrees with the graph and linked projections share a location.

## Extraction boundary

There are three practical implementation paths:

1. prove the model and maintain a handwritten TypeScript implementation checked by differential tests;
2. extract an executable reference compiler from Lean and compare the optimized TypeScript runtime against it;
3. implement the semantic kernel in a language with stronger extraction support and expose it to TypeScript.

The first path offers the best initial cost-benefit ratio. The proof artifact defines the contract; generated test vectors and a reference interpreter provide a bridge to production.

# Part VI - Consequences for the PBUI API {-}

# A lambda-informed TypeScript API

## Separate values, references, and computations

The first API recommendation is to stop using one generic payload notion for values, live bindings, event streams, and effectful reads.

```ts
interface ValuePort<A, C extends ValueContract<A>> {
  readonly kind: "value";
  readonly contract: C;
}

interface CellPort<A, C extends CellContract<A>> {
  readonly kind: "cell";
  readonly contract: C;
}

interface StreamPort<A, C extends StreamContract<A>> {
  readonly kind: "stream";
  readonly contract: C;
}
```

A projected cell is an abstract reference:

```ts
interface BindingCell<A> {
  readonly bindingId: BindingId;
  read(signal?: AbortSignal): Promise<A>;
  write(value: A, authority: WriteAuthority): Promise<Revision>;
  subscribe(listener: (observation: CellObservation<A>) => void): Unsubscribe;
}
```

This mirrors the lambda-calculus distinction among a value \(A\), a reference `Ref A`, and an effectful computation returning \(A\).

## Open components as typed functions

A component definition should expose a typed boundary separately from its renderer:

```ts
interface OpenComponent<Inputs, Outputs, State, Observation> {
  readonly id: ComponentTypeId;
  readonly inputs: PortSchema<Inputs>;
  readonly outputs: PortSchema<Outputs>;
  readonly initialState: State;

  step(
    state: State,
    command: ComponentCommand<Inputs>,
  ): Transition<State, Outputs>;

  observe(
    state: State,
    environment: BoundEnvironment<Inputs>,
  ): Observation;
}
```

The denotational reading is:

\[
\textsf{Inputs}\times\textsf{State}
\to
T(\textsf{Outputs}\times\textsf{State}\times\textsf{Observation}).
\]

A React component consumes `Observation` and emits commands. It does not own the semantic boundary.

## Distinct wiring combinators

The API should expose at least three constructions.

### Directional pure connection

```ts
connect({
  from: source,
  to: target,
  map: pureAdapter,
});
```

Type:

\[
(A\to B)\to\textsf{Output}\;A\to\textsf{Input}\;B\to\textsf{Wire}.
\]

### Directional effectful process

```ts
route({
  from: events,
  to: commands,
  process: effectfulHandler,
});
```

Type:

\[
(A\to F B)\to\textsf{StreamOut}\;A\to\textsf{StreamIn}\;B\to\textsf{Process}.
\]

### Identity link

```ts
identify({
  left: chartDocument,
  right: pipelineDocument,
  merge: preferSource(chartDocument),
});
```

Type:

\[
\textsf{IdentityCompatible}(\tau,\tau)
\Rightarrow
\textsf{CellPort}\;\tau
\to
\textsf{CellPort}\;\tau
\to
F\textsf{LinkResult}.
\]

The identity operation is not represented as `map: x => x`; it changes alias topology and persistent state.

## Compatibility evidence

Instead of returning only a Boolean:

```ts
checkIdentityLink(left, right):
  | {
      ok: true;
      commonContract: CanonicalIdentityContract;
      proof: IdentityCompatibilityEvidence;
      requiredAuthority: CapabilityRequirement;
    }
  | {
      ok: false;
      diagnostics: readonly ContractMismatch[];
    };
```

The evidence can be consumed by `identify`, while the command kernel revalidates revisions and authority. This is a runtime approximation to passing a proof term into a typed constructor.

## Quotient plan as explicit IR

```ts
interface BindingPlan {
  readonly revision: PlanRevision;
  readonly classes: readonly BindingClass[];
  readonly projection: ReadonlyMap<PortAddress, BindingId>;
  readonly diagnostics: readonly Diagnostic[];
  readonly renaming: RenamingWitness;
}

interface BindingClass {
  readonly bindingId: BindingId;
  readonly contract: CanonicalIdentityContract;
  readonly members: readonly PortAddress[];
  readonly generatingLinks: readonly LinkId[];
  readonly lineage: BindingLineage;
}
```

The plan is a normalized intermediate representation. It should be serializable and comparable up to generated-name renaming.

## Substitution environment

A component runtime receives a bound environment:

```ts
type BoundEnvironment<Schema> = {
  readonly [K in keyof Schema]: ProjectionFor<Schema[K]>;
};
```

This is the runtime environment for the component's free port variables. Rebinding a component constructs another environment; the component need not know which other local ports share each projection.

## Selection as an effect

```ts
interface SelectionRequest<A> {
  readonly query: Query<A>;
  readonly prompt: Message;
  readonly cancellation: "allowed" | "forbidden";
}

interface SelectionEffect {
  chooseOne<A>(request: SelectionRequest<A>): Effect<SelectionOutcome<A>>;
}
```

A command requiring two objects becomes curried or workflow-based rather than embedding nested global callbacks.

## Opaque functions and proof profiles

Arbitrary lambdas remain useful but should carry an explicit classification:

```ts
const customFilter = query.opaqueWhere({
  id: "app/custom-filter-v1",
  reads: [Project.archived, Project.owner],
  purity: "claimed-pure",
  monotonicity: "unknown",
  evaluate(project, ctx) {
    return legacyPredicate(project, ctx);
  },
});
```

The compiler reports which theorems and optimizations no longer apply. A host-language lambda is not rejected; it is prevented from silently masquerading as inspectable syntax.

# Case study I - Linked chart and pipeline documents

## Initial open terms

Let the chart and pipeline have local document cells:

\[
\Gamma_C=c:\operatorname{Ref}D,
\qquad
\Gamma_P=p:\operatorname{Ref}D.
\]

Their observations are:

\[
\textsf{chartObs}:\operatorname{Ref}D\times S_C\to F O_C
\]

and:

\[
\textsf{pipelineObs}:\operatorname{Ref}D\times S_P\to F O_P.
\]

Before linking, environments assign independent locations:

\[
\rho(c)=\ell_c,
\qquad
\rho(p)=\ell_p.
\]

## Link compilation

The user declares:

\[
c\sim p.
\]

The quotient has one class:

\[
[c]=[p]=b.
\]

The compiled environment uses one location:

\[
\bar\rho(b)=\ell_b.
\]

Precomposition supplies:

\[
\rho'(c)=\rho'(p)=\ell_b.
\]

This is context contraction plus reference aliasing.

## Merge conflict

If:

\[
\sigma(\ell_c)=\textsf{doc-A},
\qquad
\sigma(\ell_p)=\textsf{doc-B},
\]

then the link declaration alone is underdetermined. A source-preference gesture may choose:

\[
\mu(\textsf{doc-A},\textsf{doc-B})=\textsf{doc-A}.
\]

The runtime creates or reuses \(\ell_b\), stores `doc-A`, then commits the new projection map.

## Distinct widgets, shared resource

The chart renders:

\[
\textsf{renderChartDocument}(\ell_b),
\]

while the pipeline renders:

\[
\textsf{renderPipelineDocument}(\ell_b).
\]

The widgets need not be equal. The invariant is:

\[
\textsf{resourceOf}(c)=\textsf{resourceOf}(p)=\ell_b.
\]

A write from either widget changes \(\sigma(\ell_b)\), causing both observations to update.

## Multiple placements

If the chart logical view has two placements, both placements render occurrences of the same chart component instance. The document port belongs to the logical instance, not to each placement. Therefore adding a placement does not add another port unless the product explicitly models placement-local selection.

The identities remain:

```text
logical component instance  -> owns semantic port
placement                    -> renders component instance
occurrence                   -> renders subject within placement
binding class                -> shared resource across ports
```

This decomposition prevents tile duplication from accidentally changing link topology.

## Unlink

Removing the only link edge splits the class into \([c]\) and \([p]\). Under `copy-current`, both new resources receive the current value:

\[
\sigma'(\ell_c')=\sigma'(\ell_p')=\sigma(\ell_b).
\]

Future writes diverge. This is not inverse beta reduction or inverse quotienting; it is a stateful graph-edit command with a specified initialization policy.

# Case study II - Typed presentation actions

## Scheduling a contact

The action has type:

\[
\textsf{schedule}:
\textsf{Contact}	o\textsf{Slot}	o F\textsf{Event}.
\]

A contact occurrence supplies the first argument. The pending workflow is:

\[
\lambda s:\textsf{Slot}.\;\textsf{schedule}\;contact\;s.
\]

The shell's query locates mounted slot occurrences. Clicking one resumes the continuation.

## Filing a task under a project

The action:

\[
\textsf{fileTask}:
\textsf{Task}	o\textsf{Project}	o F1
\]

shows how presentation-based selection and port binding share a lambda foundation without being the same subsystem.

- Selection supplies an argument to a pending computation.
- Port linking changes the environment from which a component obtains a persistent resource.

The first is episodic function application. The second is durable context transformation and aliasing.

## Cross-representation selection

A project card and project-ID token may represent the same semantic entity under different presentation sorts. A translator:

\[
\textsf{ProjectId}\rightharpoonup\textsf{Project}
\]

can let the token satisfy a query for a project. This is a partial coercion inserted before application. It should not make the two presentation sorts definitionally equal.

## Generic inspect

The action:

\[
\forall A.\;\textsf{Descriptor}\;A\to A\to F\textsf{Inspection}
\]

shows dictionary-passing polymorphism. The descriptor determines label, description, identity, and safe observation. Parametricity suggests that the generic infrastructure should not inspect arbitrary runtime fields outside the dictionary.

## Accept mode and stale worlds

Suppose a project was selectable when the query began but becomes archived before the user clicks. The continuation's input type alone does not establish freshness. The system must:

- re-evaluate the query at commit time;
- or validate revision-stamped evidence;
- or resolve to an `invalidated` outcome.

This is a temporal refinement of typed application.

# What the lambda calculus does not solve

## Conflict resolution

The lambda calculus can represent a merge function, but it does not select one. Product requirements determine whether to reject, prefer, join, retain conflict, or ask the user.

## Dynamic graph deletion

Substitution and quotienting are generally information-losing. Efficient dynamic connectivity and provenance retention are graph-algorithm and state-model concerns.

## Distributed convergence

A replicated binding graph needs a concurrency model, causal metadata, and a CRDT or coordination protocol. Lambda terms can encode these algorithms; lambda calculus alone does not prove convergence.

## Human factors

A well-typed action can still be confusing. Selection affordances, prompt wording, focus management, error recovery, and accessible navigation require empirical evaluation and interaction design.

## Security

Types and hidden menu items do not constitute authorization. The command kernel or server must validate capabilities. A proof-carrying or capability-typed API can reduce mistakes but cannot compensate for an untrusted authority boundary.

## Performance constants

A denotationally correct compiler can be unusably slow. Union-find, dynamic connectivity, indexing, memoization, and incremental scheduling require empirical cost models. Semantic equivalence permits optimization; it does not choose the fastest implementation.

## Rendering identity

React reconciliation keys, DOM node identity, semantic subject identity, occurrence identity, and binding identity answer different questions. Lambda alpha equivalence helps with naming but does not collapse these identities.

# Research agenda

## A typed elaborator

Develop a surface DSL for component ports and compile it to \(\lambda_{\mathrm{PB}}\). The elaborator should emit:

- explicit value/computation distinctions;
- contract witnesses;
- structural substitutions;
- link equations;
- capability requirements;
- effect operations;
- source maps to TypeScript and JSX declarations.

The first theorem is elaboration type preservation.

## A reference semantics

Implement a transparent interpreter that:

- computes link closure by graph traversal;
- allocates symbolic locations;
- evaluates state and selection operations;
- records complete traces;
- exposes canonical plans independent of generated IDs.

This interpreter becomes the semantic oracle for optimized runtimes.

## Union-find and dynamic connectivity refinement

Prove or differentially test that optimized graph algorithms refine the reference quotient. Measure the point at which dynamic-connectivity structures outperform affected-component recomputation for realistic workspace graphs.

## Linear capability experiments

Prototype a contract type that distinguishes duplicable reads, exclusive writes, shared semilattice writes, and one-shot event tokens. Evaluate whether the discipline prevents meaningful bugs without overwhelming TypeScript authors.

## Call-by-push-value intermediate representation

Represent component observation and workflow code in a CBPV-inspired IR. Test whether it improves:

- effect summaries;
- worker partitioning;
- memoization safety;
- ordering diagnostics;
- static workflow preparation;
- compiler optimizations.

## Logical-relation proof

Define contextual observations for `Binding<A>` and prove equivalence between:

- one shared in-memory signal;
- a Redux-backed projection;
- a reference interpreter store.

This would validate representation independence for the runtime boundary.

## Incremental derivative

Define changes for graphs and plans, then derive or verify an update function satisfying:

\[
\textsf{compile}(G\oplus dG)
=
\textsf{compile}(G)\oplus D\textsf{compile}(G)(dG).
\]

Start with link insertion and value updates; treat deletion with affected-component recomputation.

## Interaction-tree model

Represent accept mode and multi-step commands as interaction trees. Prove one-shot resolution, cancellation safety, and refinement of the React handler to a reference trace semantics.

## Quotient-aware persistence

Specify serialization up to alpha-renaming. Prove that encode/decode preserves:

- component and port incidence;
- explicit link generators;
- quotient equivalence classes;
- resource values under declared portability policy;
- separation between logical classes and runtime binding IDs.

## Empirical user studies

Compare three interaction models:

1. dedicated modal pickers;
2. global typed accept mode;
3. query-driven command palette plus visible occurrence selection.

Measure discoverability, error rate, time to completion, understanding of shared bindings, and recovery after merge conflicts.

# Closure conversion, environments, and compiled components

## Functions are code plus an environment

A lambda abstraction can contain free variables. A runtime closure packages executable code with an environment that supplies those variables. At a conceptual level:

\[
\textsf{Closure}(A,B)
\cong
\exists E.\;E\times(E\times A\to B).
\]

The existential type hides the concrete environment representation. The closure contains:

- an environment value of some hidden type \(E\);
- a code pointer expecting that environment and the explicit argument.

Closure conversion transforms higher-order lambda terms into this explicit representation. The connection to open PBUI components is direct. A component definition is code parameterized by a port environment; a compiled component instance packages that code with projections for its currently bound ports.

```ts
interface ComponentClosure<Inputs, State, Observation> {
  readonly code: ComponentCode<Inputs, State, Observation>;
  readonly environment: BoundEnvironment<Inputs>;
  readonly state: State;
}
```

The `BoundEnvironment` is not incidental dependency injection. It is the closure environment for the component's free port variables.

## Binding compilation as environment construction

Before compilation, a component has a symbolic context:

\[
\Gamma=p_1:\tau_1,\ldots,p_n:\tau_n.
\]

The quotient compiler and resource allocator construct an environment:

\[
\rho:\Gamma\to\textsf{Resources}.
\]

A compiled component is:

\[
(C,\rho).
\]

When the user links or unlinks ports, the component code need not change. The environment changes. This suggests a clean runtime operation:

```ts
rebind(
  instance: ComponentInstance,
  nextEnvironment: BoundEnvironment<typeof instance.inputs>,
): ComponentInstance;
```

Rebinding should preserve component-local state unless the contract or product policy requires reinitialization.

## Environment sharing

Two component closures may contain references to the same binding resource in their environments:

\[
\rho_C(c)=\ell_b,
\qquad
\rho_P(p)=\ell_b.
\]

This is ordinary closure-environment sharing. The quotient compiler constructs the alias relation before closure installation. In JavaScript, both closures may capture the same signal object. In a Redux implementation, both may capture projections to one store path. The semantic requirement is representation-independent.

## Lambda lifting and explicit parameters

Lambda lifting eliminates free variables by turning them into explicit parameters. A PBUI component could similarly receive all port values as props:

```tsx
<Chart
  document={document}
  selection={selection}
  onDocumentChange={setDocument}
/>
```

This is simple and works well for small trees. It becomes awkward when bindings cross distant workspaces, change dynamically, carry authority, or need independent lifetimes. The P06 environment object is comparable to retaining closures rather than fully lambda-lifting all dependencies through every parent.

The design choice is not purely aesthetic:

- explicit props make dependencies locally visible and React-friendly;
- environment projections support dynamic graph wiring and avoid prop threading;
- a reified compiled environment can preserve inspectability that ambient global context would lose.

The strongest API combines them: the semantic compiler builds an explicit environment object, and the React adapter passes narrow projections as ordinary props or hooks.

## Explicit substitutions

Some calculi represent substitution as syntax rather than a meta-operation. A term can carry an explicit environment or substitution that is later composed and evaluated. P06's binding plan is similar: it is a first-class representation of how local port names map to global bindings.

Instead of immediately rewriting every component declaration, retain:

\[
C[\theta_q],
\]

where \(\theta_q\) is the quotient-induced substitution. Composition of wiring plans then becomes substitution composition. This representation supports:

- incremental updates;
- source-level explanations;
- debugging;
- delayed allocation;
- comparison of plans;
- proof that reassociation preserves meaning.

## Environment trimming

Closure conversion often removes environment entries not actually used by code. A component compiler can likewise analyze which declared ports affect which observations and commands. Unused projections need not trigger subscriptions or invalidations.

For a reified component language, dependency extraction is structural. For arbitrary React closures, the runtime must rely on declared dependencies or dynamic instrumentation. This is another concrete reason to keep the semantic component core inspectable.

# Lambda theories, equations, and coequalizers

## Terms modulo equations

A lambda calculus is not only a grammar of terms. It is commonly considered modulo an equational theory including alpha, beta, and possibly eta equality. A syntactic category has types as objects and equivalence classes of terms as morphisms.

This is already quotient-based mathematics:

\[
\textsf{Terms}(\Gamma,A)/{\equiv_{\beta\eta}}.
\]

The quotient identifies different syntactic expressions that the theory declares semantically equal.

P06 introduces another family of equations, not between arbitrary program terms but between interface occurrences:

\[
p=r.
\]

The binding compiler forms the congruence or equivalence closure generated by these equations. The general pattern is the same:

```text
free syntax or names
        + declared equations
        -> quotient presentation
```

## The free theory before links

Before identity links, the port context is free: each port occurrence is an independent generator in its contract fiber. A local environment may assign any suitable resource to each generator.

Adding links presents a new theory:

\[
\mathcal T_E
=
\mathcal T_P/(s(e)=t(e))_{e\in E}.
\]

Models of the quotient theory are precisely models of the original theory that satisfy the added equations. For value environments, this means assignments constant on link classes. For resource environments, it means the linked generators denote the same location.

This formulation explains the relationship between quotient syntax and compatible semantic states without relying on a particular union-find implementation.

## Coequalizers in the category of contexts

At the set level, endpoint maps are:

\[
E\rightrightarrows P.
\]

At a typed-context level, links exist only within contract fibers. The appropriate construction is therefore a coproduct of fiberwise coequalizers or a coequalizer in a slice/indexed category that preserves contract labels.

A flat untyped quotient could identify a document port with a selection port. The typed category prevents this because there is no well-typed parallel pair across different fibers.

In implementation terms, the compiler should partition by canonical identity contract before running connectivity:

```ts
for (const fiber of groupByIdentityContract(ports)) {
  compileEquivalenceClasses(fiber.ports, fiber.links);
}
```

The type-theoretic organization and the efficient implementation agree.

## Quotient categories and observational equations

The compiler's public semantics may quotient plans by generated-ID renaming:

\[
Q_1\approx_\alpha Q_2.
\]

It may also quotient adapter implementations by contextual equivalence:

\[
A_1\simeq_{ctx}A_2.
\]

These are different equations at different layers:

- link equations identify ports;
- alpha equations identify presentations differing only in fresh names;
- beta/eta equations identify program structure;
- contextual equivalence identifies implementations with the same observable behavior.

A sound architecture should state which quotient is being used whenever it says two things are “the same.”

## Coequalizers and rewrite systems

One can compute a quotient by orienting equations as rewrites toward canonical representatives. Union-find instead maintains equivalence without choosing a semantically meaningful orientation. This is appropriate for symmetric identity links.

Directional adapters should not enter the union-find relation. They are rewrite-like or morphism-like edges. If the same graph contains both:

```text
p = q                 identity equation
r -> s via f          directed transformation
```

then the compiler needs separate data structures and semantics. Treating every edge as a conversion relation destroys the universal property of the quotient and can introduce cycles with unclear meaning.

## Adding domain equations carefully

It may be tempting to identify ports whenever their current subjects have the same semantic key. That would confuse entity equality with binding equality.

```text
chart.document value    = doc-A
pipeline.document value = doc-A
```

implies equal current values, not one resource. The domain equation belongs to the value theory; the port equation belongs to the environment or location theory. P06 should only add the latter after an explicit link command or declared architecture rule.

# Curry-Howard, capabilities, and proof-relevant UI

## Propositions as types

Under the Curry-Howard correspondence, propositions are read as types and proofs as programs. A proposition that a user may link two ports can be represented as a type:

\[
\textsf{CanLink}(u,p,q,r).
\]

An inhabitant carries evidence that, at revision \(r\):

- the ports exist;
- their contracts are compatible;
- the user has authority;
- no conflicting invariant forbids the operation.

The link command can require this evidence:

\[
\textsf{link}:
\textsf{CanLink}(u,p,q,r)
\to
\textsf{MergePolicy}\;p\;q
\to
F\textsf{LinkResult}.
\]

## Evidence is not merely a Boolean

A Boolean answer loses the derivation. Proof-relevant evidence can record:

```ts
interface CanLinkEvidence {
  readonly left: PortAddress;
  readonly right: PortAddress;
  readonly canonicalContract: ContractFingerprint;
  readonly capability: CapabilityToken;
  readonly checkedAt: Revision;
  readonly premises: readonly EvidenceNode[];
}
```

This supports explanation, auditing, and stale-check detection. The evidence need not be a full theorem-prover proof term. It should be checkable by a small trusted kernel.

## Introduction and elimination

Capability evidence has constructors corresponding to introduction rules. For example:

\[
\frac{
\textsf{Compatible}(p,q)
\quad
\textsf{Authorized}(u,\textsf{Link},p,q)
\quad
\textsf{Live}(p)
\quad
\textsf{Live}(q)
}{
\textsf{CanLink}(u,p,q)
}.
\]

The command interpreter eliminates the evidence by checking its fields and using it to authorize the operation.

## Refinement types for selection

A selection query can be read as a predicate \(P:A\to\textsf{Prop}\). A successful result has a refinement type:

\[
\{x:A\mid P(x)\}.
\]

In dependent-pair notation:

\[
\Sigma(x:A).P(x).
\]

This is the formal version of “a selected project together with evidence that it is active, owned by the current user, mounted, and reachable.”

## Proof erasure and runtime checking

Some evidence is useful only during validation and can be erased before rendering. Other evidence, such as provenance and disabled-action reasons, is user-visible. A compiler can distinguish:

- computationally relevant evidence;
- audit evidence;
- explanatory evidence;
- erased static evidence.

TypeScript alone cannot prevent forged evidence in an untrusted plugin. Constructors should be hidden, and authoritative commands should recheck critical predicates at the trusted boundary.

## Capabilities as values, not global queries

An object-capability interpretation strengthens the Curry-Howard view. Authority is represented by possessing a value with operations, rather than by asking a global role database inside arbitrary component code.

```ts
interface LinkCapability {
  propose<A>(left: CellPort<A>, right: CellPort<A>): LinkProposal<A>;
}
```

A plugin that never receives this capability cannot issue link commands through the typed API. The server still validates authority, but ambient access is reduced.

## Proof-relevant affordances

An action menu can show not only that an action is available but why. A disabled action can expose the failed premise:

```text
Link document selectors
Unavailable: pipeline document is derived and read-only.
```

This improves usability and tests the semantic system: explanations should correspond to the same premises the command kernel validates.

# Recursion, normalization, and the edge of the calculus

## Strong normalization is not the product goal

The simply typed lambda calculus is strongly normalizing: every reduction sequence terminates. A real PBUI includes recursion, streams, mutable state, waiting for input, and external effects. It should not terminate as a whole.

The useful property is stratified:

- query and contract normalization should terminate;
- finite quotient compilation should terminate;
- one command transaction should terminate or explicitly await an external operation;
- an interactive session may continue indefinitely;
- a recursive rule stratum should reach a declared fixed point under its convergence assumptions.

## General recursion

A fixed-point operator has type:

\[
\textsf{fix}:(A\to A)\to A.
\]

It destroys strong normalization but permits recursive components and workflows. The architecture should keep recursive definitions reified and classified where termination or productivity matters.

## Recursive types

Trees, streams, and component graphs use recursive types:

\[
\mu X.FX
\]

for inductive structures, and:

\[
\nu X.FX
\]

for coinductive behavior. A layout split tree is inductive; an event stream is coinductive. Conflating them leads to awkward APIs.

## Fixed points in rule evaluation

Recursive semantic rules use least fixed points on lattices, not the same `fix` semantics as arbitrary general recursion. Monotonicity gives a canonical least solution. P06 connectivity is itself a closure operation: the smallest equivalence relation containing declared edges.

This closure can be computed by finite iteration because the active port graph is finite. Transfinite fixed-point theory may justify more general rule languages, but it is not a browser algorithm requirement.

## Productivity of interaction

A coalgebraic workflow can be infinite while remaining productive: it continues to reveal observations or accept events. A tight internal loop emitting no observable step is divergence. Effect systems and guarded recursion can distinguish productive waiting from accidental nontermination.

## Normal forms for plans

The compiler should produce a canonical plan for comparison:

- contracts normalized;
- class members sorted;
- link provenance sorted;
- generated IDs abstracted or deterministically assigned;
- redundant links retained in source but optionally omitted from a semantic normal form;
- resource policies represented explicitly.

Canonicalization supports differential tests and hashing. It should not erase source information needed for unlink or explanation.

## The final boundary

The lambda calculus provides principled recursion and fixed-point operators, but it does not guarantee that a chosen recursive UI rule is sensible. The architecture should expose termination, monotonicity, productivity, and resource-use classifications as separate proof obligations.

# Architectural conclusions

## The exact correspondences

Several connections are exact enough to guide implementation directly.

- An open component boundary is a typing context.
- A directional pure connection is substitution or function composition.
- A command awaiting another object is a partially applied function.
- Accept mode stores a typed continuation or effect request.
- A heterogeneous presentation is an existentially packaged typed value.
- A descriptor registry is a runtime dictionary environment.
- Link-induced sharing is structural contraction at the context level.

## The enriched correspondences

Other mechanisms require an effectful or resource-aware lambda calculus.

- A live binding is a reference, not a plain value.
- Identity linking supplies the same location to multiple free port occurrences.
- Merge and unlink are transactional effects.
- Long-running interaction is coalgebraic behavior around a lambda-definable transition core.
- Incremental evaluation is a derivative or change semantics for lambda terms and graph compilation.

## The categorical synthesis

The complete picture has three directions:

```text
syntax and wiring:
  local port occurrences --quotient/coequalizer--> binding classes

semantic environments:
  binding assignments --precomposition/diagonal--> compatible local assignments

runtime observation:
  local occurrence + shared resource --renderer--> widget
```

The first is covariant identification of names. The second is contravariant restriction to coherent environments. The third deliberately remains occurrence-indexed.

## The key design distinction

The most important result can be stated compactly:

> A P06 identity link does not say that two widgets are equal and does not merely say that two current values are equal. It says that two typed free interface occurrences are interpreted through one binding resource.

That statement connects quotient compilation, lambda contexts, contraction, store semantics, and rendering without conflating them.

## Final position

The lambda calculus should be the **internal language of PBUI composition**, but not its entire ontology.

Use it for:

- typed abstraction and application;
- contexts and substitutions;
- higher-order workflows;
- parametric generic infrastructure;
- equational reasoning;
- compiler correctness and contextual equivalence.

Add explicit theories for:

- nominal identity and freshness;
- mutable references and capabilities;
- quotient and cospan wiring;
- effect handling;
- coalgebraic interaction;
- incremental change;
- distributed reconciliation;
- human-facing rendering and accessibility.

This layered account gives P06 a firmer foundation than either callback-oriented React code or category-theoretic terminology alone. It also yields a tractable verification strategy: mechanize a small typed and effectful core, test optimized compilers against a reference semantics, and evaluate the resulting interaction patterns with users.

# Appendix A - Compact formal correspondence {-}

| PBUI/P06 construct | Lambda-calculus or semantic counterpart | Qualification |
|---|---|---|
| presentation value | typed value \(v:A\) | exact at semantic layer |
| presentation occurrence | observation offering \(v:A\) | occurrence is not the value |
| type-indexed descriptor | dictionary for \(A\) | runtime type witness required |
| generic inspect | polymorphic function with dictionary | parametric only if representation hidden |
| pending action | partially applied function | exact for missing arguments |
| accept mode | typed continuation/effect/evaluation context | cancellation adds sum/effect |
| component input port | free variable declaration | exact for open boundary |
| component | term in context | effects require enriched calculus |
| directional connection | substitution/composition | exact for pure maps |
| transformed link | typed function/process | not identity |
| identity link | contraction plus alias declaration | stateful interpretation uses references |
| binding class | quotient of port occurrences | quotient acts on names/topology |
| shared cell | runtime location for a binding class | operational resource |
| projection | environment lookup via quotient map | exact under compiled plan |
| widget renderer | occurrence-indexed observation function | need not factor through quotient |
| merge policy | effectful binary operation | not chosen by quotient |
| unlink policy | stateful graph split operation | no canonical inverse |
| generated binding ID | fresh name for a class | alpha-invariant unless persisted |
| reference compiler | denotational/reference interpreter | semantic oracle |
| union-find compiler | optimized implementation | prove refinement/contextual equivalence |
| recursive applicability | least fixed point | adjacent to lambda reduction |
| subscription/session | coalgebraic behavior | potentially infinite |
| incremental compiler | derivative/change semantics | requires change structures |

# Appendix B - A compact TypeScript sketch {-}

```ts
type Mode =
  | "read"
  | "write"
  | "read-write";

interface IdentityContract<A> {
  readonly payload: RuntimeType<A>;
  readonly semanticTag: string;
  readonly mode: Mode;
  readonly authorityDomain: string;
  readonly multiplicity: "one" | "optional" | "many";
  readonly updateAlgebra: string;
  readonly lifetime: "component" | "workspace" | "persistent";
}

interface CellPort<A> {
  readonly address: PortAddress;
  readonly contract: IdentityContract<A>;
}

interface BindingCell<A> {
  readonly bindingId: BindingId;
  read(): Promise<A>;
  write(value: A, authority: WriteAuthority): Promise<Revision>;
  subscribe(listener: (value: A) => void): Unsubscribe;
}

interface CompiledPlan {
  project<A>(port: CellPort<A>): BindingCell<A>;
  sameBinding<A>(left: CellPort<A>, right: CellPort<A>): boolean;
  factor<A, X>(
    contract: IdentityContract<A>,
    local: (port: CellPort<A>) => X,
    respects: (left: CellPort<A>, right: CellPort<A>) => boolean,
  ): ReadonlyMap<BindingId, X>;
}

interface LinkCommand<A> {
  readonly type: "LinkPorts";
  readonly left: CellPort<A>;
  readonly right: CellPort<A>;
  readonly merge: MergePolicy<A>;
  readonly evidence: IdentityCompatibilityEvidence;
}

type MergePolicy<A> =
  | { readonly type: "require-equal"; readonly equals: Eq<A> }
  | { readonly type: "prefer-left" }
  | { readonly type: "prefer-right" }
  | { readonly type: "join"; readonly algebra: JoinSemilattice<A> }
  | { readonly type: "interactive"; readonly workflow: WorkflowId };
```

The API exposes the lambda-calculus layers explicitly:

- `CellPort<A>` is a typed free interface variable;
- `CompiledPlan.project` supplies its environment entry;
- `BindingCell<A>` is an abstract reference value;
- `LinkCommand<A>` changes the environment and alias topology;
- `MergePolicy<A>` is an effectful semantic choice.

# Appendix C - Lean proof skeleton {-}

```lean
import Init

namespace PBUI

inductive Contract where
  | primaryDocument
  | rowSelection
  deriving DecidableEq, Repr

inductive Port : Contract -> Type where
  | chartDocument    : Port .primaryDocument
  | pipelineDocument : Port .primaryDocument
  | tableDocument    : Port .primaryDocument
  | chartSelection   : Port .rowSelection

inductive Linked : {c : Contract} -> Port c -> Port c -> Prop where
  | refl (p : Port c) : Linked p p
  | chart_pipeline :
      Linked Port.chartDocument Port.pipelineDocument
  | pipeline_table :
      Linked Port.pipelineDocument Port.tableDocument
  | symm : Linked p q -> Linked q p
  | trans : Linked p q -> Linked q r -> Linked p r

def portSetoid (c : Contract) : Setoid (Port c) where
  r := Linked
  iseqv := {
    refl := Linked.refl
    symm := Linked.symm
    trans := Linked.trans
  }

abbrev Binding (c : Contract) := Quotient (portSetoid c)

def project (p : Port c) : Binding c :=
  Quotient.mk (portSetoid c) p

theorem linked_same_binding
    (h : Linked p q) :
    project p = project q := by
  exact Quotient.sound h

def factor
    (g : Port c -> X)
    (respects : forall p q, Linked p q -> g p = g q) :
    Binding c -> X :=
  Quotient.lift g respects

theorem factor_commutes
    (g : Port c -> X)
    (respects : forall p q, Linked p q -> g p = g q)
    (p : Port c) :
    factor g respects (project p) = g p := by
  rfl

-- Resource-level interpretation: this is what should factor.
opaque Resource : Contract -> Type
opaque resourceOfBinding : Binding c -> Resource c

 theorem linked_same_resource
    (h : Linked p q) :
    resourceOfBinding (project p) =
      resourceOfBinding (project q) := by
  rw [linked_same_binding h]

-- Local renderers may remain different for different port occurrences.
opaque Widget : Type
opaque renderAt : (p : Port c) -> Resource c -> Widget

def widgetAt (p : Port c) : Widget :=
  renderAt p (resourceOfBinding (project p))

end PBUI
```

The absence of a theorem equating `widgetAt p` and `widgetAt q` is intentional. The formal model proves shared resource identity, not identical local appearance.

# Appendix D - Verification checklist {-}

A production P06 implementation should maintain the following executable checks.

## Static and schema checks

- Every port has a well-formed complete contract.
- Identity compatibility is reflexive, symmetric, and transitive over canonical contracts.
- Every explicit identity link has compatible endpoints.
- Every transformed connection has a typed adapter.
- Every command and policy has a codec where persistence or remote execution requires one.

## Reference semantics checks

- Connected components equal the generated equivalence closure.
- Projection is constant on every class.
- Factorization succeeds exactly for class-constant interpretations.
- Renaming local IDs preserves canonical plans.
- Link declaration order preserves canonical plans.

## Runtime checks

- Linked projections share a resource ID.
- Writes through one projection are observed through every linked projection.
- Failed links leave topology and values unchanged.
- Unlinking affects only the previous component.
- `copy-current` preserves immediate endpoint values.
- Removed components and ports cannot leave dangling links.
- Selection contexts resolve at most once.
- Stale evidence is rejected or revalidated.

## Differential checks

- Reference and union-find compilers agree on random finite graphs.
- Full recompilation and incremental update agree after random edits.
- Encode/decode preserves topology up to renaming.
- React adapter traces refine the semantic interaction machine.

## User-facing checks

- Linked state is visibly indicated without implying identical widgets.
- Merge policy and conflict are understandable before commit.
- Unlink consequences are explained.
- Keyboard and screen-reader users can identify and choose compatible ports.
- Cancellation restores focus and leaves state unchanged.

# Appendix E - Selected bibliography {-}

The bibliography emphasizes primary sources and papers that directly support the semantic constructions used in this thesis.

1. **Ariola, Zena M., and Matthias Felleisen.** “The Call-by-Need Lambda Calculus.” *Journal of Functional Programming* 7(3), 1997, pp. 265-301. [DOI](https://doi.org/10.1017/S0956796897002724).

2. **Baez, John C., and Kenny Courser.** “Structured Cospans.” *Theory and Applications of Categories* 35, 2020, pp. 1771-1822. [arXiv](https://arxiv.org/abs/1911.04630).

3. **Cai, Yufei, Paolo G. Giarrusso, Tillmann Rendel, and Klaus Ostermann.** “A Theory of Changes for Higher-Order Languages: Incrementalizing Lambda Calculi by Static Differentiation.” *PLDI 2014*, pp. 145-155. [arXiv](https://arxiv.org/abs/1312.0658).

4. **Church, Alonzo.** “An Unsolvable Problem of Elementary Number Theory.” *American Journal of Mathematics* 58(2), 1936, pp. 345-363. [JSTOR DOI](https://doi.org/10.2307/2371045).

5. **Fiore, Marcelo, Gordon Plotkin, and Daniele Turi.** “Abstract Syntax and Variable Binding.” *Proceedings of LICS 1999*, pp. 193-202. [Author PDF](https://homepages.inf.ed.ac.uk/gdp/publications/Abstract_Syn.pdf).

6. **Fong, Brendan.** “Decorated Cospans.” *Theory and Applications of Categories* 30, 2015, pp. 1096-1120. [arXiv](https://arxiv.org/abs/1502.00872).

7. **Foster, J. Nathan, Michael B. Greenwald, Jonathan T. Moore, Benjamin C. Pierce, and Alan Schmitt.** “Combinators for Bidirectional Tree Transformations: A Linguistic Approach to the View-Update Problem.” *ACM TOPLAS* 29(3), 2007. [DOI](https://doi.org/10.1145/1232420.1232424).

8. **Girard, Jean-Yves.** “Linear Logic.” *Theoretical Computer Science* 50, 1987, pp. 1-102. [DOI](https://doi.org/10.1016/0304-3975(87)90045-4).

9. **Lambek, Joachim.** “Cartesian Closed Categories and Typed Lambda-Calculi.” In *Combinators and Functional Programming Languages*, LNCS 242, 1986, pp. 136-175. [DOI](https://doi.org/10.1007/3-540-17184-3_44).

10. **Launchbury, John.** “A Natural Semantics for Lazy Evaluation.” *POPL 1993*, pp. 144-154. [DOI](https://doi.org/10.1145/158511.158618).

11. **Levy, Paul Blain.** *Call-By-Push-Value*. PhD thesis, Queen Mary and Westfield College, 2001. [Author PDF](https://pblevy.github.io/papers/thesisqmwphd.pdf).

12. **Milner, Robin.** “A Theory of Type Polymorphism in Programming.” *Journal of Computer and System Sciences* 17(3), 1978, pp. 348-375. [Author-hosted PDF](https://homepages.inf.ed.ac.uk/wadler/papers/papers-we-love/milner-type-polymorphism.pdf).

13. **Moggi, Eugenio.** “Notions of Computation and Monads.” *Information and Computation* 93(1), 1991, pp. 55-92. [DOI](https://doi.org/10.1016/0890-5401(91)90052-4).

14. **Pitts, Andrew M.** “Operationally-Based Theories of Program Equivalence.” In *Semantics and Logics of Computation*, Cambridge University Press, 1997, pp. 241-298. [Author PDF](https://www.cl.cam.ac.uk/~amp12/papers/opebtp/opebtp.pdf).

15. **Pitts, Andrew M.** “Operational Semantics and Program Equivalence.” In *Applied Semantics*, LNCS 2395, 2002, pp. 378-412. [Author PDF](https://www.cl.cam.ac.uk/~amp12/papers/opespe/opespe-lncs.pdf).

16. **Plotkin, Gordon D., and Matija Pretnar.** “Handling Algebraic Effects.” *Logical Methods in Computer Science* 9(4), 2013. [arXiv](https://arxiv.org/abs/1312.1399).

17. **Reynolds, John C.** “Types, Abstraction and Parametric Polymorphism.” In *Information Processing 83*, 1983, pp. 513-523. [Author-hosted scan](https://people.mpi-sws.org/~dreyer/tor/papers/reynolds.pdf).

18. **Wadler, Philip.** “Linear Types Can Change the World!” In *Programming Concepts and Methods*, 1990. [Author-hosted PDF](https://cs.ioc.ee/ewscs/2010/mycroft/linear-2up.pdf).

# Endnote {-}

The lambda calculus begins with a radical simplification: computation can be organized around variables, abstraction, and application. P06 begins with a different simplification: component integration can be organized around typed port occurrences, explicit link equations, binding classes, and projections. The thesis has shown that these simplifications meet at the level of contexts and environments.

A port is not merely a socket drawn on a box. It is a free typed name. A link is not merely a line. It is either a substitution, a process, or an equation, and the API must say which. A binding is not merely a group ID. It is an environment entry, often realized as a shared reference. A widget is not the binding itself. It is one local observation of a resource supplied through that binding. Once these distinctions are made, the mathematics becomes directly useful: alpha equivalence governs renaming, beta governs connection, contraction governs sharing, coequalizers govern name identification, diagonals govern coherent environments, monads and handlers govern effects, and contextual equivalence governs implementation replacement.
