---
title: go-go-datadrop — Structural Guard Tests as a Genre
aliases:
  - structural guard test pattern
  - allowlist with a reason
  - verify a guard by breaking it
  - source scanning tests
tags:
  - architecture-garden
  - go-go-datadrop
  - testing
  - conventions
  - linting
status: active
type: architecture-pattern-study
pattern_maturity: established
created: 2026-07-26
analyzed: 2026-07-26
repository: /home/manuel/code/wesen/go-go-golems/go-go-datadrop
repository_commit: ef996430f8a3a63e6812d961eb2bae5d631272a0
analysis_commit: 69b82257f75a4ca236d985629dc298844128409f
source_tickets:
  - DATADROP-6
  - DATADROP-7
related_files:
  - ui/test/layers.test.ts
  - ui/test/no-raw-controls.test.ts
  - ui/test/stories.test.ts
  - ui/test/tokens-used.test.ts
  - ui/test/render-path.test.ts
  - ui/test/tour.test.ts
  - ui/test/instances.test.ts
  - ui/test/lessons.test.ts
  - ui/test/api-surface.test.ts
  - ui/biome/no-table-for-in-render.grit
  - cmd/datadrop/tree_test.go
  - pkg/cli/rows_test.go
last_reviewed: 2026-07-26
---

# Structural Guard Tests as a Genre

**Maturity: Established. The strongest candidate for ecosystem guidance in this project.**

This is the pattern the repository should be remembered for, and it is not a runtime structure. Thirteen tests, written across three tickets and several months, converged on one shape without anyone naming it. This document names it.

## 1. What problem is being solved

A codebase accumulates conventions faster than it accumulates enforcement. *Form controls come from the design system. Descriptors hold no React. Components do not fetch. Every component has a story. Only token names, never hex values.*

Each is true when written and each decays silently, because the failure of a convention is not an error — it is a file that works. The observation that started this genre is in `layers.test.ts`:

> A convention that is only written down is a convention that has already been broken somewhere nobody has looked.

The second problem is subtler. A test suite over behaviour cannot see structure. Every one of the conventions above can be violated by code that compiles, renders correctly, and passes every unit test in the repository.

## 2. The concrete shape

Thirteen tests at the analyzed commit. Nine share one shape precisely enough to call it a genre:

| Test | Invariant | Allow-list |
|---|---|---|
| `layers.test.ts` | no file imports from a layer above it; every source directory is classified | 9 reasoned exemptions |
| `no-raw-controls.test.ts` | no hand-written `<button>`, `<select>`, `<input>` outside the atoms | 6 reasoned exemptions |
| `render-path.test.ts` | nothing under `components/` names the pipeline-evaluating lookup | 3 reasoned exemptions |
| `stories.test.ts` | every component directory has a story, a barrel, and the right title prefix | — |
| `tokens-used.test.ts` | every `var(--pbui-…)` in a stylesheet names a declared token | — |
| `tour.test.ts` | the documentation rack names exactly the registered applications; nothing in the lesson layer imports a component | — |
| `instances.test.ts` | the store module exports no constructed instance; nothing outside the entry point imports a store value | — |
| `api-surface.test.ts` | the set of mutating endpoints is exactly the reviewed set; cookies are same-origin | — |
| `lessons.test.ts` | every lesson's "do it for me" action satisfies that lesson's own completion predicate | — |

The recipe, extracted:

```ts
// 1. Walk the source tree.
const files = sourceFiles(join(SRC, "components"));

// 2. Assert a structural invariant, collecting every violation rather than
//    failing on the first — the author wants the whole list.
const offenders: string[] = [];
for (const path of files) {
  const rel = relative(SRC, path);
  if (ALLOWED.some((entry) => rel.startsWith(entry.prefix))) continue;
  …
  offenders.push(`${rel}:${index + 1}  ${line.trim()}`);
}

// 3. Fail with the file, the line, and what to do instead.
expect(offenders,
  `these reach for tableFor, which evaluates the whole pipeline.\n` +
  `Use fieldsFor — it is O(steps) and safe in a render body (DR-40).\n` +
  offenders.join("\n"),
).toEqual([]);
```

And the convention that makes it survivable:

```ts
/**
 * Where a raw element is legitimate, and why. Every entry is a sentence someone
 * had to write, which is the point: an escape hatch that costs a sentence is one
 * people use honestly.
 */
const ALLOWED: Array<{ prefix: string; because: string }> = [
  { prefix: "components/atoms/",
    because: "the atoms ARE the wrappers — this is where the raw elements live" },
  { prefix: "components/molecules/FileDropZone/",
    because: "holds the only <input type=file> in the tree; it is hidden and out of " +
             "the tab order, with the Button in front of it as the tab stop" },
  …
];
```

Eighteen such reasoned exemptions exist across three tests.

## 3. How it is woven into the rest of the application

The genre has three properties that make it more than a collection of scripts.

**It runs in the test suite that already exists.** No linter, no parser, no resolver, no plugin. `layers.test.ts` explains the choice directly: adding an ESLint configuration plus a parser plus a resolver plus a plugin, to enforce a graph that fits in a table, is a poor trade when `bun test` is already in CI and reports the offending import rather than a rule identifier.

**Some tests keep documentation and code in agreement.** `tour.test.ts` asserts that the interface's reference rack and the application registry hold the same set — so an application cannot ship without appearing in the documentation, and a documentation card cannot name an application that does not exist. `stories.test.ts` asserts that every component has been *looked at*. These are structural tests over prose, which is unusual and effective.

**Update, 2026-07-26 — the genre crossed a language boundary.** At the first analysis all thirteen instances were TypeScript running under `bun test`, which left a live objection: the genre might be an artefact of a stack with a fast runner and a filesystem-shaped module system. DATADROP-9 added four Go instances, and they behave the same way.

| Test | Invariant | Why no other layer can see it |
|---|---|---|
| `TestEveryClientVerbHasTheClientSection` | every verb that talks to a server carries `--addr` and `--token` | a verb missing the section compiles, runs, and fails at its first request against the default address regardless of `--addr` |
| `TestTheCommandSurfaceIsComplete` | the leaf set is exactly the nineteen expected verbs | a command group whose registrar was never named produces a binary that builds, tests clean, and is missing commands |
| `TestNoVerbHasBothFormatAndOutput` | `--format` names a server-side format, `--output` a client-side rendering; no verb has both | the invariant is about *meaning*; nothing structural can see it |
| `TestClientTokenIsASecret` | the credential field's type is one the framework redacts | see below — this is the interesting one |

Two differences from the TypeScript instances are worth naming.

**The Go instances walk an assembled object graph, not the source tree.** `cmd/datadrop/tree_test.go` constructs the real command tree in process and interrogates it. It lives in `package main` because that is the only package importing every command group — which is also precisely why a forgotten group is possible. The genre's essential property is not "scan the source"; it is **assert a property that no single unit can observe**, and an assembled graph serves that as well as a file walk does.

**One guard failed for the wrong reason, and that was informative.** `TestClientTokenIsASecret` was first written over the assembled Cobra flags, asserting `flag.Value.Type() == "secret"`. It failed on all eighteen verbs — because `glazed` registers `TypeString` and `TypeSecret` through the same `flagSet.String(...)` call, so the property is invisible at that layer. The test was correct in intent and wrong in layer, and had to be rewritten one level down against the section's field definition. **A structural guard that fails on every subject is usually the test's model of the system being wrong, not the system.**

Of the three guards written over the command tree, one found a real defect (a verb with both `--format` and `--output`, written by the same author twenty minutes earlier), one found a misunderstanding in its author's model of the framework, and one passed. All three outcomes are useful; the second is the one that would not have occurred had the test been written to pass.

**One rule moved to a linter, and only one.** During the analysis session a Biome plugin was added for the render-path rule, scoped to the component tree, so it fails in the editor before the test runs. The test was kept. The reasoning is in [[Research/Software Architecture Garden/go-go-datadrop/04 - The Enforced Layer Graph and the Container Panel Split|document 04]]: the linter is a fast signal, the test is the guard.

## 4. Why it works

**The allow-list-with-a-reason is the load-bearing invention.** A test with no escape hatch gets deleted the first time it is wrong. A test with a silent escape hatch accumulates exemptions nobody can evaluate. A test whose exemptions each cost a written sentence produces a list a reviewer can read and challenge — and, in practice, produces *fewer* exemptions, because writing the sentence is where an author discovers they do not have one.

`no-raw-controls.test.ts` goes further and asserts that **every allow-list entry still matches something**, so an exemption whose reason expired fails the build.

**The failure message is part of the design.** Every one of these tests fails with a file, a line, and the alternative to use. That is what makes them teaching surfaces rather than obstacles; the failure is the first time many contributors meet the convention.

**They catch a class of defect nothing else can.** Two concrete instances from this project's history:

- `stories.test.ts` was written when 22 of 24 components had no story. It has since caught two new components on the commit that introduced them.
- `tour.test.ts` fails whenever an application is registered without a documentation card, which has happened every time an application was added.

## 5. What goes wrong

**A structural test can pass while guarding nothing.** This is the genre's characteristic failure, and this project has an answer to it, applied at least eight times: **verify the guard by breaking the thing it guards.**

From the analysis session, verbatim results:

```text
break: add env.tableFor(null) to a panel        → structural guard fails, names file:line
break: make schemaAfter touch table.rows        → all three cost assertions fail
break: duplicate a help-page slug               → "claimed by both X and Y"
break: add a "# " heading to a help page body   → "the help system renders the Title"
break: unquote a colon in YAML frontmatter      → "declares slug X, which does not resolve"
break: add a fifth FilterOp without a case      → both branches fail to compile
```

The last one is not a source-scanning test but the same discipline applied to a type-level guard. Four more from DATADROP-9:

```text
break: rename a row key seq -> sequence         → names both key lists, before and after
break: remove the exit-code wrapper             → "exit code = 1, want 3" AND the prefix changes
break: silence the deprecation warning          → "no deprecation warning on stderr"
break: drop half the deprecation mapping        → "produced a JSON array, so it was not mapped"
```

The last of those is the most instructive failure in the set, because the broken output is still valid JSON containing the right data. A human eyeballing it would accept it. Only the concatenated-versus-array distinction is wrong, and that distinction is the entire subject of the deprecation the test guards.

**Not every guard was verified.** The genre is a convention, not a rule, and some of the thirteen have no recorded break. That is the honest gap: the discipline is applied by whoever remembers it.

**A textual scan cannot see through aliasing.** `render-path.test.ts` matches a distinctive identifier, and the only escape is genuinely dynamic property access, which nobody writes by accident. A rule over a less distinctive name would be weaker. During the analysis session the alternative was measured: Biome's GritQL plugins match the syntax tree — so they ignore the name in comments and strings, a real gain — but they have no symbol table, no types and no dataflow, so an alias through a differently-named binding escapes them too. Probed with three call shapes:

```ts
env.tableFor("x")                        // matched
const { tableFor } = env; tableFor("x")  // matched only by a bare-name pattern
const t = env.tableFor; t("x")           // not matched by either
```

**The genre cannot express intent.** *Meaning is never carried by colour alone* is a real rule in this project's guidelines and no test can check it. The honest response is to keep such rules in a review checklist and stop implying they are enforced — which `ui/GUIDELINES.md` does, and which its out-of-date enforcement table then partly undoes.

## 6. When should another project reuse it

Almost always, and earlier than feels justified. The cost of the first such test is about forty lines; the cost of the second is about ten, because the tree-walking helper already exists.

The signal that a project needs one: **a convention has just been stated in a review comment for the second time.** That is the moment it should become a test, because the third statement will not happen and the fourth violation will.

Non-applicability: a project small enough that one person reads every diff does not need them, and a project without a fast test runner will find the walk annoying. Both thresholds are lower than they appear — this repository's thirteen browser tests run in well under a second, and the four Go instances that assemble a whole command tree run in about 30 ms.

The Go instances also relax the applicability condition. A guard does not need a source-tree walk; it needs an assembled artefact and a property no unit can see. Any project with a registry, a plugin set, a command tree or a route table has that artefact already.

## 7. What should become ecosystem guidance

Four candidates, all developed in [[Research/Software Architecture Garden/go-go-datadrop/09 - Candidate Ecosystem Guidelines|document 09]]:

1. **A convention that has been stated twice in review should become a structural test.**
2. **Every exemption states its reason in a sentence, and a test asserts that each exemption still matches something.**
3. **A structural guard is not real until it has been broken once, and the break belongs in the commit message.**
4. **A guard's failure message names the file, the line, and the alternative.**

The third is the one most likely to be skipped and most likely to matter. A guard nobody has broken is a guard nobody has tested, and a test suite full of them provides confidence proportional to its line count rather than to its coverage.

## Related notes

- [[Research/Software Architecture Garden/go-go-datadrop/04 - The Enforced Layer Graph and the Container Panel Split]]
- [[Research/Software Architecture Garden/go-go-datadrop/06 - Executable Documentation]]
- [[Research/Software Architecture Garden/go-go-datadrop/09 - Candidate Ecosystem Guidelines]]
- [[ARTICLE - Implementing Go Analysis Linters - Glazed CLI Linter Deep Dive]]
