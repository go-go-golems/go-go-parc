# Designing Command Languages

## Architecture Lessons from Cobra

This is a four-chapter pedagogical textbook about the reusable software-design ideas embodied in [`spf13/cobra`](https://github.com/spf13/cobra), studied at commit [`adbc8813901bba65827259daa8e22ff94ec1f30e`](https://github.com/spf13/cobra/tree/adbc8813901bba65827259daa8e22ff94ec1f30e) from 11 July 2026.

The book is not a Cobra user guide. It uses Cobra as a worked case study in how to design an executable command language: one model with several projections, an explicit interpretation pipeline, declarative constraints that also drive assistance, and compatibility mechanisms that do not fork semantics.

## Editions

- [Print-ready PDF](Designing%20Command%20Languages%20-%20Architecture%20Lessons%20from%20Cobra.pdf)
- [Complete single-file edition](Designing%20Command%20Languages%20-%20Architecture%20Lessons%20from%20Cobra.md)
- [Chapter 1 — One Model, Many Meanings](chapters/01%20-%20One%20Model%20Many%20Meanings.md)
- [Chapter 2 — Interpreting an Invocation](chapters/02%20-%20Interpreting%20an%20Invocation.md)
- [Chapter 3 — Constraints, Guidance, and Completion](chapters/03%20-%20Constraints%20Guidance%20and%20Completion.md)
- [Chapter 4 — Evolution, Recovery, and Verification](chapters/04%20-%20Evolution%20Recovery%20and%20Verification.md)
- [Appendix A — Glossary](appendices/Appendix%20A%20-%20Glossary.md)
- [Appendix B — Selected Exercise Solutions](appendices/Appendix%20B%20-%20Selected%20Exercise%20Solutions.md)
- [Appendix C — Source Map](appendices/Appendix%20C%20-%20Source%20Map.md)
- [Editorial audit](Editorial%20Audit.md)

## Running example

All four chapters develop the same fictional program, `atlas`, a deployment-management CLI. The example grows from a three-node command tree into a model with inherited configuration, lifecycle hooks, relational flag constraints, dynamic completion, generated documentation, and compatibility aliases. Reusing one example makes the dependencies among the ideas visible.

## Reading conventions

- **Definition callouts** introduce terms before relying on them.
- **Worked examples** trace concrete invocations and code.
- **Counterexamples** show why a tempting design fails.
- **Fundamental callouts** expand on background material such as abstract syntax trees, lexical scope, partial functions, and bitmasks.
- Exercises progress from recall to design critique and implementation.
- Source links point to the pinned Cobra commit, not an unpinned branch.

## Scope

The analysis is static. It is based on Cobra source, tests, and documentation generators. The textbook distinguishes direct observations from proposed generalizations; proposed APIs such as an immutable `Finalize` pass are teaching designs, not claims about Cobra's current public API.

## Pedagogical structure

The textbook contains exactly four main chapters. Each chapter starts from a design pressure, defines the necessary vocabulary at first use, develops the `atlas` example, states laws or invariants with mathematics where useful, presents API and pseudocode sketches, examines counterexamples, and ends with exercises.

The second-pass editorial audit records 17,652 chapter words, 96 explicit definitions, 13 worked-example sections, 17 counterexample sections, 43 exercises, 26 display-math blocks, 60 Go code blocks, and 5 diagrams. The glossary repeats every introduced definition exactly once.

## Validation

Run the structural validator from the bundle root:

```bash
python scripts/validate_book.py
```

The validator checks the four-chapter constraint, required pedagogical elements, balanced code fences, glossary parity, duplicate definitions, and local links. `Editorial Audit.md` records the student-perspective revision and the concept-to-application audit.
