---
title: REPL Semantics, Lexical Scope, and Source-to-Source Transformation
subtitle: The Foundations Behind Modern Interactive JavaScript Systems
aliases:
  - REPL Semantics Article
  - Interactive JavaScript Foundations
tags:
  - research
  - article
  - institute
  - repl
  - javascript
  - lexical-scope
  - source-transformation
  - iife
  - compiler-theory
status: draft
type: article
created: 2026-04-03
source_ticket: IIFE-01
sources:
  - "[[chatgpt-deep-research-repl-semantics-design]]"
  - "[[chatgpt-deep-research-js-repl]]"
  - "[[kagi-assistant-rpl-semantics-synthesis]]"
  - "[[kagi-assistant-js-repl-scoping-deep-dive]]"
  - "[[soshnikov-lexical-environments-es5]]"
  - "[[2ality-lexicalenv-vs-variableenv]]"
---

# REPL Semantics, Lexical Scope, and Source-to-Source Transformation

## The Foundations Behind Modern Interactive JavaScript Systems

---

*This article bridges two worlds that usually live in separate textbooks: the formal semantics of interactive evaluation, as studied in programming language theory, and the practical design of Read-Eval-Print Loops (REPLs) — the interactive programming environments that developers use every day. It is written for the engineer who wants to understand not just *how* REPLs work, but *why* the design decisions behind them matter.*

---

## 1. Opening Scene: What Happens When You Press Enter?

Consider what actually happens when you type `var x = 1` into a browser console and press Enter. The browser doesn't simply "run" this statement in isolation. It parses it, evaluates it in the context of everything you've typed before, mutates some internal state, prints `undefined` (because `var` declarations have no return value), and then waits for your next input. The next time you type `x`, the console remembers.

This seemingly simple interaction hides a profound design problem. The console must maintain the *illusion of sequential state* — each line you type builds on the last — while the underlying language specification may not cleanly support that model. In JavaScript, the ECMAScript specification defines how a single *Script* or *Module* is evaluated, but it says nothing about evaluating a sequence of separate code fragments, each with its own lexical environment, across an interactive session. The console invents that semantics itself.

The formal study of this problem — how to define the meaning of interactive, incremental evaluation — has deep roots in programming language theory. And the solutions that REPL designers have found — environment threading, store-passing, source-to-source transformation, IIFE wrapping — are all instances of well-studied semantic techniques.

Let's trace those connections.

---

## 2. The REPL as a State-Transforming Transducer

### 2.1 Beyond the Acronym

"Read-Eval-Print-Loop" is a description, not a definition. Formally, a REPL is best understood as a *state-transforming transducer*: a machine that consumes an input stream of program phrases and produces an output stream of printed results, threading a language-defined state across steps.

This state has a standard shape, drawn directly from operational semantics:

- **Environment (ρ):** A mapping from names to locations. The environment implements lexical scope — each `var`, `let`, or `function` declaration extends or modifies the current environment frame.
- **Store (σ):** A mapping from locations to values. The store handles mutation: `x = 42` updates the store at the location bound to `x` without changing the environment at all.

The environment/store split is not an implementation detail. It is a foundational concept in programming language semantics, formalized independently by Christopher Strachey in his 1967 "Fundamental Concepts in Programming Languages" lectures and by Gordon Plotkin in his 1981 "Structural Operational Semantics" framework. The split exists because *names are not locations* — a variable name like `x` refers to a memory cell, but the name itself is distinct from the cell. The environment tells you *which* cell; the store tells you what's *in* that cell.

### 2.2 The Formal Picture

In big-step operational semantics, evaluating an expression `e` in environment `ρ` and store `σ` produces a value `v` and an updated store `σ'`:

```
⟨e, ρ, σ⟩ ⇓ ⟨v, σ'⟩
```

A REPL threads this evaluation across multiple inputs. Each interactive phrase consumes the current `(ρ, σ)` pair and produces a new one:

```
⟨parse(input₁), ρ₀, σ₀⟩ ⇓ ⟨v₁, ρ₁, σ₁⟩
⟨parse(input₂), ρ₁, σ₁⟩ ⇓ ⟨v₂, ρ₂, σ₂⟩
⟨parse(input₃), ρ₂, σ₂⟩ ⇓ ⟨v₃, ρ₃, σ₃⟩
...
```

Two key invariants hold:

1. **Monotonic environment extension:** ρᵢ₊₁ ⊇ ρᵢ — new bindings are added but not removed. This is what makes a REPL session feel like "one long program."
2. **Arbitrary store mutation:** σᵢ₊₁ may differ arbitrarily from σᵢ. Assignment is destructive.

This is precisely the model used in the Definition of Standard ML (Milner, Tofte, Harper, MacQueen, 1990), where a "program" is explicitly defined as a *sequence of top-level declarations* whose execution *modifies the top-level environment* (called a *basis*). The ML definition splits each interaction into parsing, elaboration (static semantics), and evaluation (dynamic semantics) — exactly the kind of multi-stage pipeline that real REPLs embody.

### 2.3 The REPL as Its Own Language

Here is a subtle but critical insight: once we formalize interactive evaluation as a semantics of *sequences*, we can treat "the REPL language" as distinct from "the batch language." A recent line of academic work argues that a REPL for a base language *L* induces a related language *R* whose "programs" are sequences of snippets, and whose meaning is the composition of snippet meanings — including effects.

This perspective explains something every developer has noticed: REPL behavior frequently *diverges* from "the language spec." Browser consoles allow `let` redeclaration across entries. Node.js REPLs break `const` semantics when top-level `await` is involved. IPython transforms `%magic` commands into function calls. In each case, the REPL is defining its own language — one optimized for interactive usability rather than strict spec compliance.

---

## 3. Environments and Stores: The Textbook Foundation

### 3.1 Essentials of Programming Languages (Friedman & Wand)

EoPL establishes the canonical environment-store separation through a series of executable interpreters. The key signature is:

```
eval-exp : Exp × Env × Store → Value × Store
```

Each subexpression evaluation returns both a value and an updated store. The store propagates left-to-right through argument lists and `begin`-sequences — a technique called *store-passing style*. For REPL-style interaction, EoPL extends the environment monotonically: each top-level definition adds a new binding to the global environment frame, with the store potentially mutated by side effects.

Why does this matter for REPL design? Because the store-passing style is exactly what a REPL does when it evaluates your input, updates the global environment, and then uses that updated environment for your next input. The textbook formalization makes the otherwise ad-hoc "REPL state" into a precise semantic object.

### 3.2 Types and Programming Languages (Pierce)

TAPL approaches the same territory through *evaluation contexts* — a form of small-step operational semantics where the "hole" `[·]` in a context `E` indicates where the next reduction step occurs:

```
E ::= [·] | E e | v E
```

With a single congruence rule:

```
e → e'
─────────────
E[e] → E[e']
```

This separates *where* evaluation happens (the context) from *what* computation occurs (the reduction rules). For REPL design, evaluation contexts are important because they make evaluation order explicit — and interactive evaluation is critically order-sensitive. When you type `x = 1; y = x + 1` into a console, you expect `x` to be updated before `y` is evaluated. Evaluation contexts are one of the cleanest formalisms for specifying this.

For languages with mutable references (TAPL Chapter 13), stores become explicit components of the reduction relation:

```
⟨e, µ⟩ → ⟨e', µ'⟩
```

where `µ` maps locations to values. The reference allocation rule generates fresh locations; dereference and assignment manipulate `µ`. Crucially, Pierce introduces *store typings* — a static approximation of the store that grows monotonically as allocation occurs — to prove type safety in the presence of mutation. This is the formal basis for understanding why a REPL must track not just the values in its store but also the *types* of those values (as ML-family REPLs do when they report inferred types).

### 3.3 Semantics Engineering with PLT Redex (Felleisen, Findler, Flatt)

PLT Redex provides a domain-specific language for operational semantics embedded in Racket. Its key contribution is making reduction relations executable and testable:

```racket
(define red
  (reduction-relation
   Ev #:domain p
   (--> (in-hole P (if0 0 e_1 e_2))
        (in-hole P e_1) "if0t")
   (--> (in-hole P ((λ (x t) e) v))
        (in-hole P (subst x v e)) "βv")))
```

The `in-hole` pattern performs context decomposition — splitting a term into an evaluation context and a reducible expression. This is precisely the decomposition that REPL designers perform (often implicitly) when deciding how to evaluate multi-line input or handle side effects in interactive code.

Redex also models abstract machines like CEK (Control, Environment, Kontinuation) and CESK (adding Store), where environments are explicit closures mapping variables to values. These machines are the direct ancestors of how modern JavaScript engines implement REPL contexts.

---

## 4. Lexical Scope: The Great Alignment

### 4.1 What Lexical Scope Means, Formally

A scoping discipline determines how name occurrences are resolved to bindings. In lexical (static) scope, a variable reference resolves to the nearest enclosing binding in the *program text*. In dynamic scope, it resolves to the most recent binding in the *call history*.

The formal distinction maps directly to the environment model:

- **Lexical scope:** The environment at a function's *definition site* is captured in its closure. When the function is called, free variables resolve through this captured environment.
- **Dynamic scope:** The environment at the function's *call site* is used. There is no closure capture — instead, the current call-stack environment chain is walked.

### 4.2 The "Great Scope Shift" in Lisp

The Lisp family is historically central to the dynamic-vs-lexical story. Early Lisps — including MacLisp and Interlisp — used dynamic scoping by default. The result was a practical problem: the behavior of a function could change depending on *who called it*, because variable names would resolve to whatever was bound in the calling context.

Kent Pitman's historical account notes that MacLisp used dynamic scoping in interpreted code but had a form of "lexical scoping" in compiled code that did not correspond to creating lexical closures in the way later Common Lisp users would expect. This meant the same program could behave differently in the REPL (interpreted) vs. compiled — a tension that directly motivated the standardization of lexical scope.

Scheme (1975) was the first major Lisp dialect to adopt lexical scope by default. The R7RS report explicitly characterizes Scheme as "statically scoped." Common Lisp (1984) standardized a hybrid model: **lexical variables by default**, with **dynamic ("special") variables** available by declaration. This hybrid survives because dynamic scope provides a powerful mechanism for *ambient configuration* — debugging parameters, printer controls, current I/O streams — that is especially convenient in interactive development.

### 4.3 JavaScript's Scope Model

The ECMAScript specification offers one of the most explicit modern formal environment models in any industrial language spec. It defines **Environment Records** as specification objects that associate identifiers to variables based on lexical nesting, with an `[[OuterEnv]]` link modeling the scope chain. This aligns tightly with the environment notion in operational semantics.

ECMAScript's scope evolution mirrors the broader historical trend:

- **`var` (ES1):** Function-scoped (or global-scoped at top level). Hoisted. No block scope.
- **`let`/`const` (ES6):** Block-scoped. Not hoisted in the temporal dead zone. Lexical bindings that follow exactly the textbook model.
- **Modules (ES6):** Module-scoped. Top-level `let`/`const` bindings are local to the module, not properties of the global object.

This evolution created a practical problem for REPL designers. In a script, `let x = 1; let x = 2` is a `SyntaxError`. But in a browser console, users expect to be able to re-enter `let x = 1` across separate inputs without errors. Chrome DevTools explicitly added "let and class redeclarations in the Console" as a convenience feature — effectively creating a fresh lexical environment per console entry while maintaining the illusion of a single persistent scope.

This is the REPL-as-its-own-language principle in action: the console's interaction semantics *differs* from the semantics of executing a single ECMAScript Script by the spec, and this difference is deliberate.

---

## 5. Source-to-Source Transformation: The Universal REPL Strategy

### 5.1 Transform, Don't Modify

A key architectural decision in REPL design is whether to handle interactive affordances by modifying the evaluator or by transforming the input. The principle "transform, don't modify" has deep roots in programming language theory:

- **Syntactic sugar elimination** (Landin, 1964): Express surface syntax in terms of a smaller core language.
- **Macro expansion** (Scheme `syntax-rules`, `syntax-case`): Rewrite program text before evaluation.
- **CPS transformation**: Convert direct-style programs into continuation-passing style.
- **Closure conversion**: Eliminate closures by making environments explicit.

In each case, the strategy is the same: rather than complicating the core evaluation rules, transform the input into a form the core rules already handle. This is exactly what REPLs do.

### 5.2 The IIFE Pattern as Source Transformation

The Immediately Invoked Function Expression (IIFE) pattern — `(function() { ... })()` — is perhaps the most famous JavaScript-specific instance of source-to-source transformation for interactive contexts.

Before `let` and `const` (ES6), JavaScript had only `var`, which is function-scoped. In a REPL or embedded scripting context, this meant every `var` declaration leaked into the global scope. The IIFE pattern was the solution: wrap each evaluation unit in a function to create a fresh scope:

```javascript
// Without IIFE: pollutes global scope
var x = 1;
var y = 2;

// With IIFE: x and y are scoped to the function
(function() {
  var x = 1;
  var y = 2;
})();
```

The IIFE is a manual source-to-source transformation. The programmer takes code that *should* be block-scoped and wraps it in a function to achieve the effect. When Go-based JavaScript REPLs like go-go-goja's WebREPL use IIFE wrapping under the hood, they are automating exactly this pattern: each input snippet is rewritten as `(function() { <snippet> })()` and evaluated in a new scope.

But this transformation has consequences. Inside the IIFE, `var` declarations are scoped to the function. `return` statements work naturally. But `this` changes (it becomes `undefined` in strict mode), `arguments` is now the IIFE's arguments object, and — most importantly — bindings from previous evaluations are *not accessible* unless explicitly passed in or attached to a shared global object.

These tradeoffs are not accidental. They are the direct consequence of what formal semantics calls *binding structure preservation*: a source-to-source transformation must preserve the intended binding structure, or the transformed program will behave differently from the original. The IIFE transformation *deliberately changes* the binding structure (that's the point — it creates a new scope), but it must do so *without introducing unintended captures*.

### 5.3 What Formal Semantics Demands of a Transform

A textbook-grade correctness criterion for source transformation is **contextual equivalence**: replacing the original phrase with the transformed phrase in any program context does not change observable behavior. For REPL-specific transforms, the key invariants are:

| Invariant | What It Means | What Breaks If Violated |
|-----------|---------------|------------------------|
| **Scope hygiene** | No accidental variable capture | Unintended shadowing, name collisions |
| **Binding structure** | Lexical references resolve correctly | Undefined variables, wrong values |
| **Evaluation order** | Side effects occur in the right sequence | Race conditions, state corruption |
| **Type safety** | Transform preserves well-typedness | Type errors in transformed code |
| **Phase consistency** | Compile-time/runtime boundary respected | Meta-programming failures |

### 5.4 Hygienic Macros: The Gold Standard

The most mature industrialized form of scope-preserving source rewriting is the *hygienic macro system*. Scheme's evolution from `syntax-rules` to `syntax-case` to Racket's `syntax-parse` provides a precise technical lineage:

| System | Mechanism | Hygiene Implementation |
|--------|-----------|----------------------|
| `syntax-rules` | Pattern-based rewriting | Automatic α-renaming of pattern variables |
| `syntax-case` | Procedural transformers with pattern matching | Syntactic wraps with timestamp histories |
| `syntax-parse` (Racket) | Attribute grammars with contract-like specs | Scope sets (Flatt, 2012) |

The hygiene condition, formalized by Kohlbecker et al. (1986), states that generated identifiers that become binding instances must only bind variables generated at the same transcription step. Referential transparency means free references in macro output refer to bindings visible where the transformer was *defined*, not where it was *invoked*.

For REPL designers, hygienic macro theory provides both vocabulary and correctness criteria for any source rewriting that touches binding structure — whether it's called "macro expansion," "desugaring," "IIFE wrapping," or "interactive snippet normalization."

---

## 6. Comparative REPL Architectures

### 6.1 The Design Space

Interactive systems vary less in *whether* they have a REPL and more in *what state persists* and *how much rewriting* happens between the user's input and the language core. Five architectures span the design space:

### 6.2 Smalltalk: The Image Model

Classic Smalltalk systems collapse the distance between development time and runtime. The running system is a persistent *image* — a snapshot of all objects, classes, and compiled methods. There is no textual source transformation because the "REPL" is the live object environment itself. Methods are compiled directly into method dictionaries. Persistence is achieved by serializing the entire object memory to disk.

The Smalltalk image model represents one extreme of the design space: state is everything, transformation is nothing.

### 6.3 Common Lisp with SLIME: The Live Image Connection

The Lisp tradition, especially with editor-to-image integrations like SLIME, treats the REPL not just as a line-oriented interaction but as a control plane for *incrementally patching a running system*. Evaluation means compiling and loading new definitions into the running image.

Common Lisp's hybrid scoping model (lexical by default, dynamic via `special` declarations) directly supports this workflow. Dynamic variables provide standardized "ambient state" knobs — current package, printer controls, debugging parameters — that can be rebound without rewriting code. This is dynamic scope surviving not as a mistake but as a deliberate design choice for interactive ergonomics.

### 6.4 Python: Incremental Compilation with `codeop`

Python's REPL infrastructure is explicitly documented in the standard library. The `codeop` module provides `compile_command()`, which serves two functions: detecting whether input is complete (so the prompt should continue) and remembering `__future__` statements across compilations.

In `single` mode, Python wraps expressions to trigger `sys.displayhook` on results — a source transformation so routine it's barely noticed. Multi-line input is accumulated until `compile_command` succeeds. The `ast.PyCF_ALLOW_TOP_LEVEL_AWAIT` flag enables async constructs in interactive mode, demonstrating the "change the compilation mode" approach to extending REPL capabilities.

### 6.5 Node.js: VM Contexts and Explicit Wrapping

Node.js's REPL module exposes a `context` object whose properties appear as local variables within the REPL. Under the hood, evaluation uses the `vm` module (`vm.runInThisContext`) to compile and run code in a contextified global environment.

The key source transformations Node.js performs:

- **Top-level await wrapping:** Input containing `await` is rewritten as `async (() => { ... })()`.
- **Strict mode injection:** `"use strict"` is prepended if the REPL was started with `--strict_mode`.

Notably, Node's documentation admits a semantic compromise: REPL await "will invalidate the lexical scoping of the `const` keyword." A `const` introduced with an awaited initializer can subsequently be assigned to — a direct example of an interactive system bending lexical-binding discipline to accommodate asynchronous evaluation.

### 6.6 Jupyter Kernels: Message-Oriented Evaluation

Jupyter adopts a multi-process, message-based design. Frontends send `execute_request` messages to a kernel; the kernel publishes outputs and status over multiple ZeroMQ channels. A single kernel can service multiple frontends.

IPython (the default Python kernel) takes the transformation approach explicitly:

| User Input | Transformed Output |
|-----------|-------------------|
| `%save file.py` | `get_ipython().run_line_magic("save", "file.py")` |
| `%%sh ls` | `get_ipython().run_cell_magic("sh", "", "ls")` |
| `!ls -la` | `get_ipython().system("ls -la")` |

IPython also provides an "Autoawait" mechanism: if `await` appears at top level, IPython automatically wraps execution in an async loop. This is source-to-source transformation applied to the async problem — the same strategy Node.js uses, but at the Python level.

### 6.7 Browser DevTools Consoles

Browser consoles sit at the boundary between a standardized language (ECMAScript) and developer ergonomics. They implement:

- **`let`/`class` redeclaration across entries** — Chrome DevTools explicitly allows this, creating fresh lexical environments per entry.
- **Top-level `await`** — without requiring the code to be in a module.
- **Expression completion** — typing `1 + 2` prints `3`, but `var x = 1` prints `undefined` — the REPL distinguishes expressions from statements.

These are all instances of the REPL defining its own snippet language, distinct from the standard batch language.

---

## 7. Top-Level Await: Where Everything Collides

Top-level `await` is the point where REPL semantics, scoping rules, and transformation strategies collide most visibly. The reason is fundamental: `await` changes not only *what* is computed but *when* execution can suspend and resume. An interactive system must decide what it means to "evaluate the next input" while a previous input is suspended.

### 7.1 The ECMAScript Approach: Modules Only

ECMAScript makes top-level `await` a *module* feature. The grammar encodes this directly: scripts use `~Await` in statement lists, modules use `+Await`. Module evaluation returns a **Promise**, and the spec's module evaluation algorithms explicitly branch on whether a module contains top-level await (`[[HasTLA]]` field).

This is clean from a spec perspective, but it leaves REPLs in an awkward position: the interactive experience developers want (typing `await fetch(...)` and getting a result) doesn't correspond to any spec-defined evaluation mode for scripts.

### 7.2 How REPLs Bridge the Gap

Every system that supports interactive `await` uses one of two strategies:

1. **Change the compilation unit:** Treat REPL input as a module (or use a compiler flag like Python's `ast.PyCF_ALLOW_TOP_LEVEL_AWAIT`) to enable the async grammar.
2. **Rewrite the input:** Wrap user code in an async function (`async (() => { ... })()`) and run it in an event loop.

Both strategies have semantic costs. The wrapping approach can break `const` semantics (as Node.js admits). The module approach changes what `this` refers to and how bindings are exported. These are not implementation bugs — they are fundamental tensions between the synchronous "one line at a time" REPL model and the asynchronous "suspend and resume" evaluation model.

### 7.3 Four Design Questions

Top-level await forces REPL designers to confront four questions, each with a direct mapping to formal semantics:

1. **Step atomicity:** In a synchronous REPL, each step is atomic — it completes before the next begins. With async, a step may suspend. What happens to subsequent inputs while a previous input is suspended?

2. **Scoping:** If a snippet suspends mid-execution, when are new bindings "in scope"? Node's `const` anomaly under REPL await shows this tension concretely.

3. **Output ordering:** Should intermediate outputs stream while awaiting? Jupyter's message protocol is designed for exactly this: execute requests yield streams of outputs, and completion is a protocol-level notion.

4. **Event-loop integration:** Supporting top-level await implies an event loop is running and that evaluation can re-enter after awaited promises resolve. ECMAScript formalizes this through promise/job machinery; IPython explicitly runs code in a managed async loop.

---

## 8. Synthesis: Three Fundamental Principles

Across all the systems we've examined — from the formal models of EoPL and TAPL to the practical architectures of Node.js and Jupyter — three principles emerge:

### Principle 1: Environment-Store Separation Enables Interactive State

The environment/store split is what makes REPL state manageable. The environment grows monotonically (new bindings are added). The store mutates freely (values change). This separation means you can add new names without worrying about corrupting existing bindings, and you can update values without changing the name structure. Every REPL, from Smalltalk's live image to Jupyter's kernel state, maintains some version of this distinction.

### Principle 2: Source-to-Source Transformation Is the Universal REPL Strategy

Whether through IIFE wrapping (JavaScript), magic command rewriting (IPython), async function wrapping (Node.js), or macro expansion (Scheme), every REPL transforms user input before evaluation. This is not a hack — it is the standard engineering approach to reconciling "language semantics" with "interactive ergonomics." The formal justification is the same as for syntactic sugar elimination: define a small core semantics, then express surface features as transformations into that core.

### Principle 3: The REPL Is Its Own Language

A REPL for language *L* is not merely an interface to *L*. It defines a related language *R* whose programs are sequences of snippets, whose evaluation may involve non-standard scoping rules, and whose semantics may deliberately diverge from the batch language spec in service of interactive usability. The `let` redeclaration affordance in browser consoles, the `const` relaxation in Node's async REPL, the `%magic` commands in IPython — these are not bugs. They are features of *R*, the REPL language, which is designed for a different purpose than *L*.

---

## 9. Implications for Building Interactive JavaScript Systems

For engineers building embedded JavaScript REPLs — whether in Go, Rust, or any host language — these principles translate into concrete design guidance:

1. **Model your REPL state as `(Environment, Store)` explicitly.** Don't rely on the host language's variable bindings to track JavaScript state. Use a dedicated environment chain (for name resolution) and store (for values), just as EoPL teaches.

2. **Choose your transformation strategy deliberately.** IIFE wrapping creates a new scope per evaluation but isolates bindings. Direct global-scope evaluation shares everything but offers no isolation. Module-style evaluation gives you clean scoping but requires a module system. These are not interchangeable.

3. **Decide whether your REPL language matches your batch language.** If you want strict ECMAScript compliance, you'll need to handle the script/module distinction and reject non-standard redeclarations. If you want interactive ergonomics, you'll need to define your own snippet semantics — and document the differences.

4. **Handle `await` early in your design.** Top-level await will force decisions about event-loop integration, step atomicity, and scoping. These decisions are much easier to make before you've committed to an evaluation architecture.

5. **Test your transforms for hygiene.** Any source-to-source transformation that introduces bindings (IIFE parameters, async wrappers, module encapsulation) must be checked for accidental variable capture. The hygiene invariants from macro theory — scope hygiene, binding structure preservation, evaluation order — are your test cases.

---

## 10. Key References

| Source | Relevance |
|--------|-----------|
| Friedman & Wand, *Essentials of Programming Languages*, 3rd ed. | Environment-store model, store-passing interpreters |
| Pierce, *Types and Programming Languages* | Evaluation contexts, store typings, operational semantics |
| Felleisen et al., *Semantics Engineering with PLT Redex* | Reduction relations, executable semantics, CEK/CESK machines |
| Milner et al., *The Definition of Standard ML* (1990) | Formal treatment of interactive evaluation, basis threading |
| ECMAScript 2024 Specification | Environment Records, Script vs Module, top-level await |
| Soshnikov, "ECMA-262-5 in Detail: Lexical Environments" | Deep walkthrough of JS environment model |
| Kohlbecker et al., "Hygienic Macro Expansion" (1986) | Foundational hygiene condition for AST rewriting |
| Flatt, "Composable and Compilable Macros" (2012) | Racket scope sets model |
| Pitman, "Special Forms in Lisp" (historical) | Dynamic vs lexical scope history in Lisp |
| Krishnamurthi, *PLAI* | Accessible treatment of environment/store for interpreters |

---

## Further Reading

- **Axel Rauschmayer, "Lexical environment vs. variable environment"** — The distinction in ECMAScript between the environment used for `let`/`const` and the one used for `var`.
- **Dmitry Soshnikov, "ECMA-262-5 in Detail"** series — The most thorough public walkthrough of how ECMAScript's environment model maps to the textbook concepts.
- **Jupyter Messaging Protocol specification** — A clean example of how interactive evaluation can be formalized as a message-passing protocol.
- **Node.js `node:repl` and `node:vm` documentation** — Practical API docs that reveal the design tensions between language semantics and interactive ergonomics.
- **R7RS-large Macrological Fascicle** — The definitive specification of macro hygiene invariants, directly applicable to any REPL that performs source transformation.
