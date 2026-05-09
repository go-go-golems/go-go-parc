# Research Option E: Meta-Compilation & Extensible Languages

**Research Goal:** Understand how modern approaches blur the boundary between languages and compilers, exploring meta-compilation, language-oriented programming, and extensible language systems.

**Date:** 2026-04-15
**Sources Collected:** 17 (9 papers, 8 web documents)

---

## 1. Executive Summary

Traditional compiler architecture treats the language as fixed and the compiler as a tool that translates that language. The approaches studied here invert or dissolve this relationship:

- **OMeta** unifies parsing and transformation into a single pattern-matching framework that operates on arbitrary data types, not just text
- **Racket's #lang system** makes language creation a first-class activity, where languages are modular components that can be composed
- **Language Workbenches (MPS)** eliminate the text-to-AST boundary entirely through projectional editing
- **COLA** (Combined Object Lambda Architecture) provides a minimal self-describing foundation for building extensible systems

These systems challenge the traditional separation between "language designer," "compiler writer," and "application programmer."

---

## 2. OMeta: Pattern Matching as a Universal Mechanism

### 2.1 Core Innovation

OMeta, developed by Alessandro Warth and Ian Piumarta at VPRI in 2007, is based on a simple but profound insight: **parsing is just pattern matching on text, and pattern matching can apply to any data structure**.

From the OMeta paper (DLS 2007):

> "OMeta is based on a variant of Parsing Expression Grammars (PEGs)—a recognition-based foundation for describing syntax—which we have extended to handle arbitrary kinds of data."

Traditional parser generators (Yacc, Bison, ANTLR) are specialized for text → AST transformation. OMeta generalizes this to:
- Characters → Tokens (lexical analysis)
- Tokens → Parse trees (parsing)
- Parse trees → Annotated trees (type checking)
- Trees → Trees (optimization)
- Trees → Code (code generation)

### 2.2 Key Technical Features

**Higher-Order Rules:**
```
ometa BasicCalc <: Parser {
  Digit = super:d -> d.ToDigit(),
  Number = Number:n Digit:d -> (n * 10 + d) | Digit,
  AddExpr = AddExpr:x '+' MulExpr:y -> (x + y) | MulExpr
}
```

Rules can inherit from other rules, be passed as arguments, and invoke each other via "foreign production invocation." This enables grammar composition and reuse.

**Semantic Predicates:**
OMeta can use host-language boolean conditions during pattern matching, allowing semantic constraints to influence parsing.

**Arbitrary Data Types:**
Unlike traditional parsers limited to character streams, OMeta patterns can match:
- Characters and strings (text parsing)
- Numbers and atoms
- Lists and trees (structural transformation)
- Graphs and objects

### 2.3 The COLA Connection

OMeta was originally implemented in **COLA** (Combined Object Lambda Architecture), described as "a self-describing language in two parts":

1. An object system for structural composition
2. A lambda calculus for behavioral description

COLA represents VPRI's attempt to find minimal, self-describing foundations for computation. As Piumarta's whitepaper notes, the goal is "intrinsic object model" where objects describe themselves.

### 2.4 Trade-offs

**Advantages:**
- Single syntax for all compiler phases
- Rapid DSL prototyping (reportedly ~26% lines of code vs. vanilla implementations)
- Grammar inheritance and composition
- No separate lexer/parser/codegen tools needed

**Limitations:**
- Performance slower than hand-optimized implementations
- Error reporting can be unclear
- Requires host language ("parasitic language" architecture)
- Memorization (packrat parsing) memory overhead

---

## 3. Parsing Expression Grammars: The Foundation

### 3.1 Recognition-Based vs. Generation-Based

Bryan Ford's 2004 POPL paper "Parsing Expression Grammars: A Recognition-Based Syntactic Foundation" introduced PEGs as an alternative to context-free grammars (CFGs).

**Key Difference:**
- **CFGs** are generative: they define how to produce valid strings
- **PEGs** are recognition-based: they define how to recognize valid strings

This seemingly minor shift has profound implications:

> "PEGs are stylistically similar to CFGs, but they interpret concatenation and alternation as operators with ordered choice and greedy matching semantics."

### 3.2 Ordered Choice and Greedy Matching

In PEGs, `A / B` means "try A first; if it fails, try B." This eliminates ambiguity—there's always a single parse result, never multiple valid parses.

The trade-off: **PEGs cannot express left-recursive grammars directly** (though Warth's later work addressed this).

### 3.3 Packrat Parsing

OMeta uses packrat parsing: memoizing intermediate results to achieve linear-time parsing despite backtracking. This makes PEGs practical for real-world use.

---

## 4. Racket #lang: Language-Oriented Programming

### 4.1 Beyond Macros

Traditional macro systems extend a fixed language. Racket's `#lang` system enables **defining entirely new languages** with:
- Custom parsers (reader level)
- Custom semantics (expander level)
- Custom tooling (IDE integration)

From the Racket documentation:

> "When loading a module as a source program that starts `#lang language`, the language determines the way that the rest of the module is parsed at the reader level."

### 4.2 The Two-Level Architecture

**Reader Level:** Controls how text becomes syntax objects. A `#lang` language provides a reader that transforms source text into Racket syntax objects.

**Expander Level:** Controls how syntax objects become meaning. The module language (specified in the second sub-form of `module`) provides the semantic interpretation.

This separation enables:
- Custom surface syntax (different from Racket's S-expressions)
- Custom semantics (different evaluation rules)
- Composability (languages can extend other languages)

### 4.3 Macro-Embedding Compiler IRs

A striking application appears in Bowman & Keep's "Macro-embedding Compiler Intermediate Languages in Racket" (2022). They show how to embed a family of compiler IRs—from high-level Scheme-like languages down to x86-64 assembly—as Racket `#lang` languages.

Key insight: The same abstractions used for DSLs (pattern matching, hygiene, macro expansion) work equally well for low-level compiler infrastructure.

### 4.4 Extensible Pattern Matching

Tobin-Hochstadt's paper "Extensible Pattern Matching in an Extensible Language" (2011) demonstrates how Racket's macro system enables user-extensible pattern matching, showing the synergy between language extensibility and compiler-adjacent features.

---

## 5. Language Workbenches: JetBrains MPS

### 5.1 Projectional Editing: Eliminating Parsing

The most radical departure from tradition is **projectional editing** (also called structural editing):

> "The editor works directly with the AST, projecting it into a human-readable form. Users never edit raw text; instead, they create or modify nodes via editors tailored to each language construct."

This eliminates parsing entirely. There is no grammar, no ambiguity, no parse errors. The AST is the source of truth.

### 5.2 Implications of Projectional Editing

**Language Composition:**
Traditional parsing struggles with language composition—combining languages A and B in the same file creates grammar conflicts. Projectional editing sidesteps this: different AST node types simply have different editors.

From Martin Fowler's MPS article:

> "Because projectional editing avoids parsing, it enables seamless language composition: constructs from different languages can be freely combined within the same expression, supporting true language modularity and reuse."

**Notations Beyond Text:**
Projectional editing supports:
- Tables and spreadsheets
- Diagrams and graphs
- Mathematical notation
- Mixed textual and graphical representations

### 5.3 KernelF: An Embeddable Functional Language

KernelF, implemented in MPS, demonstrates language workbench capabilities. It's designed specifically for extension and embedding, showing how language workbenches enable "languages as libraries" rather than languages as platforms.

---

## 6. Comparative Analysis: ChatGPT Synthesis

The following synthesis from ChatGPT conversations (see `transcripts/chatgpt-ometa-racket-mps.md` and `transcripts/chatgpt-meta-compilation-language-systems.md`) provides additional structured comparison across key dimensions.

### 6.1 Extension Layer: Where Does Change Happen?

| System | Extension Point | Implication |
|--------|-----------------|-------------|
| **OMeta** | Parser/pattern engine | Grammar modifications, composition via inheritance |
| **Racket #lang** | Module reader + expander | Language choice at module boundary |
| **MPS** | Full AST/editor/tooling stack | Language definition includes projections |

The main trade-off is **which layer you want to make extensible**: parser, compiler front end, or the whole language-plus-IDE stack.

### 6.2 Tooling Burden vs. Host-Language Leverage

**OMeta** is comparatively lightweight: rapid prototyping but not a complete language packaging and IDE system.

**Racket** goes further: hooks reader and expander layers while staying inside a shared module/tool ecosystem.

**MPS** goes furthest: editor, type-system, generator, and other aspects are part of the language definition itself. The price is more up-front work—JetBrains materials emphasize that MPS language definitions can be time-consuming.

### 6.3 Compositional Safety

**Racket is strongest** because syntax objects preserve lexical information and macro expansion explicitly tracks scopes and phases.

**OMeta** is powerful but more operational: semantic actions are host-language code embedded in the grammar, and backtracking does not rewind their effects.

**MPS** sidesteps parse ambiguity but requires defining constraints, typing rules, and generators coherently.

### 6.4 User Experience by Audience

| Audience | Best Fit | Why |
|----------|----------|-----|
| Language implementers (grammar-focused) | OMeta | Close to grammars and transformations |
| Programmers (text ecosystem) | Racket #lang | Real text language, normal files, tool interop |
| Domain experts (non-text notations) | MPS | Tables, diagrams, form-like editors |

MPS's projectional editing requires a culture shift—users often need a few days to get used to it, and diff/merge requires special tooling.

---

## 7. The Philosophical Boundary: Language vs. Compiler

### 7.1 Traditional View

The traditional compiler pipeline enforces a strict separation:

```
Source Text → Lexer → Parser → AST → Semantic Analysis → IR → CodeGen → Target
     ↑                              ↑
  Language                    Compiler
  (grammar)                   (implementation)
```

The language is fixed; the compiler implements it.

### 6.2 The Meta-Compilation Challenge

The systems studied here dissolve this boundary:

**OMeta:** Language and transformation are the same mechanism (pattern matching). A "compiler" is just a series of OMeta rules.

**Racket #lang:** Languages are user-defined modules. The compiler is extensible—new languages extend the compiler itself.

**MPS:** There is no parse step; the AST is edited directly. The "language" is a projection of the AST structure.

**COLA:** The system is self-describing; objects describe their own structure and behavior.

### 7.3 Alan Kay's Question

VPRI's research agenda, articulated by Alan Kay, asks:

> "Is it really 'Complex'? Or did we just make it 'Complicated'?"

The STEPS project (2007) aimed to create "Moore's Law Software"—systems that become simpler as hardware improves, not more complex. The approaches here share this philosophy:
- OMeta: One mechanism (pattern matching) instead of separate lexer/parser/tools
- Racket: Language creation as a library feature, not a systems-programming task
- MPS: Direct AST editing instead of text → parse → AST round-trips
- COLA: Self-describing minimal foundations

---

## 8. Comparative Analysis

### 7.1 Dimension 1: Text vs. Structure

| Approach | Input | Transformation | Output |
|----------|-------|----------------|--------|
| Traditional Compiler | Text | Parse → Transform | Text/Code |
| OMeta | Text/Structure | Pattern Match | Structure |
| Racket #lang | Text (custom syntax) | Reader → Expand | Racket AST |
| MPS | Structure (projected) | Direct manipulation | Structure |

### 7.2 Dimension 2: Extensibility Mechanism

| System | Extensibility Unit | Composition Mechanism |
|--------|-------------------|----------------------|
| OMeta | Grammar rules | Inheritance, foreign invocation |
| Racket #lang | Reader + Expander modules | Module imports, macro composition |
| MPS | Language concepts + editors | Language imports, concept extension |
| COLA | Objects + lambdas | Message passing, functional composition |

### 7.3 Dimension 3: User Audience

| System | Primary User | Learning Curve | Use Case |
|--------|-------------|----------------|----------|
| OMeta | Language implementer | Moderate | DSL prototyping, compiler education |
| Racket #lang | Domain programmer | Low-Moderate | DSL creation, language research |
| MPS | Language engineer | Steep | Industrial DSLs, complex language systems |
| COLA | Systems researcher | Very Steep | Fundamental research, minimal systems |

---

## 9. Trade-offs and Research Directions

### 9.1 Performance vs. Flexibility

There's a spectrum from maximum flexibility (MPS, COLA) to maximum performance (traditional compilers):

- **OMeta** trades performance for uniformity and rapid prototyping
- **Racket** provides good performance with full extensibility through JIT compilation
- **MPS** can generate efficient code but has higher tool overhead

### 9.2 Text vs. Structure

The text/structure boundary remains contentious:

**Text Advantages:**
- Universal tool support (diff, grep, git)
- Programmer familiarity
- Plain text storage

**Structure Advantages:**
- No parse errors
- Arbitrary notations (diagrams, math)
- Language composition without conflicts

Research question: Can projectional editing be made as fluid as text editing? Current MPS user experiences suggest there's still friction.

### 9.3 The Parser Debate Revisited

The HN thread's debate about recursive descent vs. parser generators takes on new dimensions here:

- **OMeta** offers a middle ground: declarative grammars with the flexibility of hand-written parsers (PEGs don't have the conflicts that plague LR/LALR)
- **Racket** allows custom readers—hand-written or generated
- **MPS** eliminates parsing entirely

Research question: For which applications is each approach optimal?

### 9.4 Compiler as Library vs. Compiler as Framework

These systems shift the compiler from being a **framework** (external tool) to a **library** (composable component):

- **OMeta:** Pattern matching library for transformations
- **Racket:** Language creation library
- **MPS:** Language definition toolkit

This shift enables what might be called **ad-hoc language creation**: making a new language should be as easy as making a new function.

---

## 10. Synthesis: Toward a Unified View

### 10.1 The Common Thread

All these systems share a single insight: **the traditional compiler pipeline is an artifact of implementation constraints, not fundamental to compilation**.

- The lexer/parser separation existed because memory was scarce and separate passes were needed
- The text-to-AST round-trip exists because text is the storage format
- The fixed language assumption exists because compilers were expensive to write

Modern hardware and software enable new architectures:
- **OMeta:** Single-pass pattern matching on arbitrary structures
- **Racket:** Languages as composable modules
- **MPS:** Direct structure editing

### 10.2 Implications for Compiler Research

1. **Language and compiler are not separate concerns**—they form a continuum of expression mechanisms
2. **Composition is the key challenge**—language A + language B should be easier than writing language C from scratch
3. **Notational flexibility matters**—text is one projection among many possible representations
4. **Self-description enables evolution**—systems that can describe themselves can be changed by their users

### 10.3 Open Questions

1. Can performance of extensible systems match hand-optimized compilers?
2. How do we version and evolve languages when they're composed from many components?
3. What are the debugging and error-reporting challenges in highly extensible systems?
4. How do we teach these approaches? The " compilers are hard" myth may be replaced by "extensible compilers are different"

---

## 11. Source Inventory

### Papers (PDFs)

| File | Size | Description |
|------|------|-------------|
| `ometa-dls07.pdf` | 218 KB | Original OMeta paper (Warth & Piumarta, DLS 2007) |
| `ometa-dls07-slides.pdf` | 851 KB | OMeta presentation slides |
| `peg-ford-2004.pdf` | 137 KB | Bryan Ford's original PEG paper (POPL 2004) |
| `piumarta-cola-whitepaper.pdf` | 249 KB | COLA whitepaper (Piumarta) |
| `open-extensible-composition-models.pdf` | 369 KB | VPRI research on extensible composition |
| `racket-hashlang-x64.pdf` | 494 KB | Macro-embedding compiler IRs in Racket (Bowman & Keep, 2022) |
| `extensible-pattern-matching.pdf` | 120 KB | Extensible pattern matching in Racket (Tobin-Hochstadt, 2011) |
| `kernelf-reference.pdf` | 1.8 MB | KernelF reference manual (Voelter) |
| `kay-steps-2007.pdf` | 4.3 MB | STEPS 2007 Progress Report (VPRI / Alan Kay) |

### Web Resources (Markdown)

| File | Lines | Description |
|------|-------|-------------|
| `ometa-wikipedia.md` | 162 | OMeta overview and technical details |
| `racket-hash-languages.md` | 47 | Racket documentation on #lang |
| `jetbrains-mps.md` | 52 | JetBrains MPS product overview |
| `martin-fowler-mps.md` | 470 | Martin Fowler's detailed MPS case study |
| `alan-kay-talks.md` | 52 | VPRI archive of Alan Kay talks |
| `kagi-assistant-ometa.md` | 11 | Kagi synthesis on OMeta |
| `kagi-assistant-racket.md` | 11 | Kagi synthesis on Racket #lang |
| `kagi-assistant-language-workbench.md` | 11 | Kagi synthesis on language workbenches |

### ChatGPT Transcripts (Markdown & JSON)

| File | Size | Description |
|------|------|-------------|
| `chatgpt-ometa-racket-mps.md` | 5.1 KB | Synthesis: Key differences and trade-offs |
| `chatgpt-ometa-racket-mps.json` | 8.0 KB | Raw extraction with source citations |
| `chatgpt-meta-compilation-language-systems.md` | 13.6 KB | Comprehensive analysis of all 5 research areas |
| `chatgpt-meta-compilation-language-systems.json` | 16.8 KB | Raw extraction with source citations |

### Additional Resources (from base PDFs directory)

| File | Size | Description |
|------|------|-------------|
| `nanopass-framework.pdf` | 261 KB | Nanopass compiler framework |
| `ghuloum-incremental-compiler.pdf` | 582 KB | Incremental compiler construction |
| `wirth-compilers-part1.pdf` | 184 KB | Wirth's minimal compiler (Part 1) |
| `wirth-compilers-part2.pdf` | 318 KB | Wirth's minimal compiler (Part 2) |
| `engineering-a-compiler.pdf` | 7.9 MB | Modern compiler textbook (Cooper & Torczon) |
| `ometa.pdf` | 334 KB | OMeta! paper (alternate source) |

---

## 12. Bibliography

### Primary Sources

1. Warth, A., & Piumarta, I. (2007). *OMeta: An Object-Oriented Language for Pattern Matching*. DLS 2007.
2. Ford, B. (2004). *Parsing Expression Grammars: A Recognition-Based Syntactic Foundation*. POPL 2004.
3. Piumarta, I. *Combined Object-Lambda Architecture (COLA) Whitepaper*.
4. Bowman, W. J., & Keep, A. W. (2022). *Macro-embedding Compiler Intermediate Languages in Racket*. Scheme Workshop 2022.
5. Tobin-Hochstadt, S. (2011). *Extensible Pattern Matching in an Extensible Language*. arXiv:1106.2578.
6. Kay, A. (2007). *STEPS Toward the Reinvention of Programming*. VPRI Progress Report.
7. Voelter, M. *KernelF: An Embeddable and Extensible Functional Language*.
8. Piumarta, I. (2011). *Open, Extensible Composition Models*. VPRI Research Note.

### ChatGPT Syntheses (Research Session 2026-04-15)

9. ChatGPT. (2026-04-15). *OMeta vs Racket vs MPS: Key Differences and Trade-offs*. Conversation transcript. URL: https://chatgpt.com/c/69e00097-c1d0-83ea-9e6e-79999076e370
10. ChatGPT. (2026-04-15). *Meta-Compilation and Language Systems: Comprehensive Analysis*. Conversation transcript. URL: https://chatgpt.com/c/69dfffe2-475c-83ea-81bc-50980408f955

### Secondary Sources

11. Fowler, M. (2005). *A Language Workbench in Action - MPS*.
12. Racket Documentation. *Defining new #lang Languages*.
13. Wikipedia. *OMeta*.
14. JetBrains. *MPS Documentation*.

---

## 13. Research Consolidation: Key Takeaways

### For Understanding Meta-Compilation

1. **Pattern matching is fundamental**: OMeta shows that lexing, parsing, transformation, and code generation are all instances of pattern matching on structured data.

2. **Text is a projection**: Both OMeta (operating on arbitrary structures) and MPS (projectional editing) treat text as one possible view of structure, not the primary representation.

3. **Languages are composable**: Racket's #lang and MPS's language workbench approach treat languages as modular components that can be combined, not monolithic systems.

### For Challenging Traditional Views

1. **The lexer/parser/separate-tools pipeline is historical, not necessary**: Modern hardware and higher-level languages enable simpler, more unified approaches.

2. **Compiler construction can be incremental**: From Crenshaw's 1988 series to Ghuloum's 2006 paper to modern #lang systems, building compilers step-by-step is viable.

3. **Language and compiler are a continuum**: There's no sharp boundary between "using a language" and "implementing a language" in these systems.

### For Future Research Directions

1. **Performance of extensible systems**: Can these approaches achieve production compiler performance?

2. **Tooling for extensible languages**: How do we get IDE support, debugging, error messages when languages are user-defined?

3. **Education**: These approaches may make compilers more accessible, but require different mental models.

4. **Language evolution**: How do composed languages evolve when their components change?

---

*End of Research Report*
