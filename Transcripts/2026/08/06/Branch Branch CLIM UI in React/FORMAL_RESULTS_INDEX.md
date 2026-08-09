# Formal results and proof-status index

This index is a map of the mathematical spine of *Semantic Interfaces*. It distinguishes semantic definitions, proved propositions, proof sketches, executable laws, and assumptions delegated to the host application or registry.

## Status legend

| Status | Meaning |
|---|---|
| **Definition** | Introduces notation or a mathematical object; it is not a claim requiring proof. |
| **Paper proof** | A complete conventional proof at the abstraction level used in the book. |
| **Proof sketch** | Gives the decisive argument but omits routine induction or bookkeeping. |
| **Executable law** | Checked on concrete examples by the companion kernel; not a universal proof. |
| **Assumption** | A contract that the registry, predicate author, translator author, or application must establish. |
| **Mechanization target** | A theorem whose statement is suitable for a proof assistant after host-language assumptions are modeled explicitly. |

## Core semantic objects

### Tagged universe of references

For an atomic vocabulary \(A\), with JavaScript representation set \(V_a\) for each atom \(a\), the runtime universe is a tagged disjoint sum:

\[
\Omega_R = \sum_{a\in A} V_a.
\]

A reference is written \(\langle a,v\rangle\). The tag is part of the semantic value. A raw string used as a project ID and the same raw string used as a user ID are therefore different references unless an explicit identity protocol relates them.

**Location:** Chapters 5 and 10.  
**Status:** Definition.

### Type-expression grammar

The principal calculus is:

\[
\tau ::= \top
\mid \bot
\mid a
\mid \operatorname{cap}(c)
\mid \tau\lor\tau
\mid \tau\land\tau
\mid \tau\setminus\tau
\mid \operatorname{refine}(p,\theta,\tau).
\]

The public API favors base-relative difference \(\tau_1\setminus\tau_2\) rather than unrestricted complement because the base states the intended universe and behaves more predictably under plugin extension.

**Location:** Chapter 10.  
**Status:** Definition.

### Denotation

Each type expression denotes a set of tagged references relative to registry snapshot \(R\) and environment snapshot \(e\):

\[
\llbracket\tau\rrbracket^R_e \subseteq \Omega_R.
\]

Union, intersection, and difference receive their ordinary set interpretations. A named refinement intersects its base with the truth set of a registered predicate.

**Location:** Chapters 9–11.  
**Status:** Definition.

### Semantic subtyping

Environment-local semantic subtyping is set inclusion:

\[
R,e\models \tau_1\leq\tau_2
\quad\Longleftrightarrow\quad
\llbracket\tau_1\rrbracket^R_e
\subseteq
\llbracket\tau_2\rrbracket^R_e.
\]

Global subtyping quantifies over admissible environments. The distinction matters because an environment-dependent refinement may be included in another type for one snapshot without establishing a stable registry theorem.

**Location:** Chapter 11.  
**Status:** Definition.

## Proved structural results

### Key equality induces an equivalence relation

If a deterministic semantic-identity function is total on a subset \(D\subseteq\Omega_R\), equality of identity keys is reflexive, symmetric, and transitive on \(D\).

**Location:** Proposition 6.1.  
**Status:** Paper proof.  
**Mechanization value:** Low difficulty; useful as the entry theorem for a formal identity model.

### Ancestor closure is a closure operator

For a reflexive-transitive nominal declaration relation, ancestor closure is extensive, monotone, and idempotent.

**Location:** Proposition 7.1.  
**Status:** Paper proof.  
**Implementation consequence:** A reference's transitive nominal facts may be precomputed and cached as a closed bitset.

### Boolean-algebra laws

The denotational model validates commutativity, associativity, idempotence, absorption, distributivity, and the expected top/bottom laws for the supported set constructors. Smart constructors in the companion implement several of these normalizations.

**Location:** Chapters 5, 7, 10, and 25.  
**Status:** Standard set proofs plus executable examples.  
**Caveat:** Syntactic normalization is not automatically a complete decision procedure for semantic equivalence.

## Matching results

### Direct matcher soundness

If direct matching succeeds with evidence \(\pi\), the source reference belongs to the requested denotation:

\[
\operatorname{matchDirect}_{R,e}(r,\tau)
=\mathsf{success}(\pi)
\Longrightarrow
r\in\llbracket\tau\rrbracket^R_e.
\]

The proof proceeds by structural induction over \(\tau\). Atom and capability cases rely on registry well-formedness; refinement cases rely on predicate correctness; the difference case relies on a decidable negative membership result rather than absence of a proof alone.

**Location:** Theorem 16.1.  
**Status:** Proof sketch.  
**Mechanization target:** Primary. It is the natural first substantial theorem for Lean, Coq, Agda, or Isabelle/HOL.

### Translated acceptance soundness

If full matching returns source \(r\), accepted reference \(r'\), requested type \(\tau\), and translator path \(P\), then \(r'\) belongs to \(\tau\), provided every edge of \(P\) satisfies its declared translator contract.

The theorem intentionally does not conclude that \(r\) directly belongs to \(\tau\). Translation is reachability, not subtyping.

**Location:** Theorem 16.2.  
**Status:** Proof sketch plus translator-contract assumptions.  
**Mechanization target:** Primary after direct matching.

### Soundness versus completeness

The companion's `isSubtype` procedure is sound for the rules it proves but intentionally incomplete. Returning `false` can mean either “the subtype relation is false” or “this restricted proof procedure did not establish it.”

A complete decision procedure is possible only after fixing a decidable fragment and explicit assumptions about atoms, capabilities, and refinements. Arbitrary JavaScript predicates prevent a general complete procedure.

**Location:** Chapters 9, 11, 13, 20–22, and companion README.  
**Status:** Scope boundary.

## Translation results

### Least-cost path

On a finite concrete translator state graph with nonnegative costs, deterministic expansion, and the usual Dijkstra invariants, removal of a target state at least tentative cost yields a minimum-cost reachable target.

**Location:** Proposition 15.1.  
**Status:** Standard proof argument specialized to the value-dependent graph explored in one snapshot.  
**Assumptions:** Finite/bounded exploration, nonnegative costs, deterministic snapshot behavior, and contract-correct translator results.

### Translation is not subtype closure

The accepted set under translators is a reachability closure:

\[
\operatorname{Acceptable}_{R,e}(\tau)
=
\{r\mid\exists r'.\;r\Rightarrow^*_{R,e}r'
\land r'\in\llbracket\tau\rrbracket^R_e\}.
\]

This relation can be partial, effectful, asynchronous, or representation-changing. It must not be inserted into the nominal subtype order.

**Location:** Chapter 15.  
**Status:** Definition and design theorem.

## Dispatch results

### Product specificity

A method signature is a product of type expressions. Signature \(S_1\) is at least as specific as \(S_2\) when every component of \(S_1\) is a semantic subtype of the corresponding component of \(S_2\).

**Location:** Chapter 17.  
**Status:** Definition.

### Unique-maximal determinism

If applicability is deterministic and the applicable method set has exactly one maximal element under specificity, correct maximal-method dispatch returns that method independently of registration order.

**Location:** Theorem 17.1.  
**Status:** Paper proof.  
**Mechanization target:** Moderate difficulty once semantic subtyping and finite applicable-method sets are defined.

### Ambiguity is semantic information

Two applicable signatures can be incomparable. A dispatcher should report multiple maximal methods, apply a documented method-combination policy, or consult an acyclic explicit preference relation. Registration order alone is not a semantic resolution rule.

**Location:** Chapter 17.  
**Status:** Design consequence of the product partial order.

## Input-context results

### At-most-once resolution

Each input-context identifier owns one continuation and can settle it at most once. Events carrying stale identifiers have no effect on the active context.

**Location:** Invariant 18.1.  
**Status:** State-machine invariant and executable law.

### Acceptance safety

Assuming matcher soundness, translator-contract soundness, commitment-time revalidation, and stale-ID rejection, successful resolution of a request for \(\tau\) returns a reference in \(\llbracket\tau\rrbracket\) for the commitment snapshot.

**Location:** Theorem 18.1.  
**Status:** Proof sketch.  
**Mechanization target:** Primary after matcher soundness; it connects the pure calculus to the operational state machine.

## Linked-subject results

### Binding coherence

Views sharing one binding cell read the same subject for each role. A subject update changes the cell, not each view independently.

**Location:** Invariant 19.1.  
**Status:** State invariant and executable law.

### Subject update preserves coherence

Updating one role in the binding cell referenced by a view preserves agreement among all views sharing that cell.

**Location:** Theorem 19.1.  
**Status:** Paper proof.

### Unlink preserves the visible subject

If unlinking first clones the old binding's subject map into a fresh binding and then reassigns the view, the view's selected subjects are unchanged at the transition boundary.

**Location:** Theorem 19.2.  
**Status:** Paper proof and executable law.

## Caching result

### Membership cache soundness

Cache reuse returns the same Boolean membership answer as reevaluation when:

1. registry and expression identities agree;
2. static facts remain valid for the same semantic identity and revision;
3. every predicate's dependency fingerprint is complete;
4. any reused translator result satisfies its declared purity and dependency contract.

The decisive assumption is dependency completeness:

\[
F_p(r,e)=F_p(r',e')\land r\approx r'
\Longrightarrow
p(r,e)=p(r',e').
\]

**Location:** Theorem 22.1.  
**Status:** Proof sketch by structural induction.  
**Mechanization target:** Valuable but host-language dependent. A proof assistant can establish the generic theorem once predicate dependency completeness is represented as an assumption or supplied proof.

## Registry and host-language assumptions

The strongest runtime theorems are conditional on the following obligations.

| Obligation | Supplied by | Typical check |
|---|---|---|
| Nominal declaration safety | Registry author and TypeScript signature | Representation assignability plus setup-time graph validation |
| No nominal cycles | Registry builder | Directed-cycle detection at `freeze()` |
| Identity determinism | Descriptor author | Property tests over one snapshot |
| Refinement purity or declared volatility | Predicate author | Review, restricted DSL, or conservative no-cache policy |
| Dependency completeness | Predicate author | Mutation/property tests and revision discipline |
| Translator postcondition | Translator author | Runtime target validation and property tests |
| Translator effect metadata | Translator author | Conservative defaults; never infer purity from syntax |
| Method applicability determinism | Registry and environment discipline | Snapshot immutability and pure applicability predicates |
| Authorization | Server or trusted command boundary | Independent reauthorization; UI evidence is not authority |

These are not defects in the mathematics. They mark the interface between the formal kernel and unverified JavaScript effects.

## Executable-law coverage

The companion law suite checks concrete instances of:

1. smart-constructor Boolean identities;
2. nominal inheritance and cycle rejection;
3. inherited static capabilities;
4. positive and negative refinement evidence;
5. cross-representation semantic identity;
6. selection of a cheaper two-edge translator path over a more expensive direct path;
7. more-specific multimethod selection;
8. context-sensitive method applicability;
9. at-most-once input-context settlement;
10. binding coherence through link, update, and unlink;
11. validity-epoch invalidation.

Run it with:

```bash
cd companion
npm test
```

Executable tests exercise implementations. They do not quantify over all registries, environments, references, or type expressions and therefore do not replace proofs.

## Suggested mechanization order

1. Define finite atoms, references, and a refinement-free type grammar.
2. Define denotation and prove Boolean laws.
3. Implement direct matching and prove soundness.
4. Add nominal closure and prove atom-case soundness.
5. Add explicit negative evidence for difference.
6. Model translators as contract-carrying relations and prove translated soundness.
7. Define the input-context transition system and prove at-most-once resolution and acceptance safety.
8. Define finite method sets and prove unique-maximal determinism.
9. Add linked-subject state and coherence preservation.
10. Introduce abstract refinement predicates with dependency-completeness hypotheses.

Appendix C of the textbook gives Lean-like declarations and a longer proof-assistant roadmap.
