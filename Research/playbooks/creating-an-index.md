---
title: "Playbook: Creating an Index for a Software Architecture Garden Entry"
slug: creating-an-index
short: "Build a textbook-style back-of-the-book index (plus glossary and notation table) for an Architecture Garden project entry, filed by how readers remember the knowledge, with anchorable entries and a link validator."
topics:
  - architecture-garden
  - documentation
  - index
  - glossary
  - obsidian
  - playbook
section_type: Playbook
created: 2026-08-14
updated: 2026-08-14
published_vault: https://parc.yolo.scapegoat.dev/
---

# Playbook: Creating an Index for a Software Architecture Garden Entry

A Garden entry explains how one repository is built. An **index** for that entry does a different job: it lets a reader who remembers *an idea* but not *where it was explained* find the exact section in seconds. A good index is the back of a well-written computer-science textbook — concept ↔ concept relationships, operations, theorems and laws, examples, counterexamples, failure modes, and alternate terminology — not a concordance of every word that appears.

This playbook is for an agent that has finished (or is finishing) an evidence-backed [[Research/Software Architecture Garden/README|Software Architecture Garden]] study and is asked to produce its index. The first worked instance is the [[Research/Software Architecture Garden/coinvault/Index of Design Patterns|CoinVault index]], with its companion [[Research/Software Architecture Garden/coinvault/Index of Design Patterns - Rationale|rationale]]; this playbook distills how that was built so the rest of the Garden can receive the same treatment consistently.

> [!summary]
> - An **index** answers *where can I read about this?*; a **glossary** answers *what does this mean?*; a **notation table** answers *what did this handle/symbol mean again?* — make them three mechanisms, not one.
> - File the index by **how readers remember the knowledge**, not how the author happened to phrase it. Add `See` redirects from every plausible alternate phrasing to the canonical entry.
> - Make every entry a **heading** so every `See` and `see only` is a clickable anchor, and so the notation table and rationale can point at a specific entry.
> - Index **ideas, not strings**: a concept need not literally occur on the linked page. Apply the **disappointed-reader test** — only link a section a reader would find substantive for that term.
> - Validate every link. Ship and run `scripts/validate_index_links.py` (this playbook) before calling an index done.
> - Keep the index honest: index the **failure modes** and the **open obligations** as carefully as the established patterns.

## 1. What this playbook is for

Use this workflow when you have a completed (or near-complete) Garden study and want to give it a durable, cross-referenceable index. The output is two files beside the study:

```text
Research/Software Architecture Garden/<project>/
├── README.md                              ← the evidence-backed study (pre-existing)
├── Index of Design Patterns.md            ← the index (this playbook)
└── Index of Design Patterns - Rationale.md ← why each term was chosen
```

Do **not** use this workflow to summarize the study, to re-explain its patterns, or to replace its prose. The index points at the study; it does not reproduce it. If you find yourself writing paragraphs of explanation, you are writing a second study, not an index.

The one rule to optimize for, which every section below serves:

> **Index the book according to how readers might remember its knowledge, not according to how the author happened to phrase it.**

A genuinely excellent technical index can almost be read independently as a terse conceptual map of the discipline. That is the target.

## 2. Three mechanisms: index, glossary, notation table

A common failure mode is to make one mechanism do three jobs. They solve different problems:

| Mechanism | Question it answers | Form in this playbook |
|---|---|---|
| **Index** | *Where in this study can I read about X?* | Locators (`§n.m` links into the study) under each entry |
| **Glossary** | *What does X mean?* | A one-sentence definition at the head of each index entry |
| **Notation table** | *What did this handle/symbol/schema mean again?* | A separate table for versioned handles, schemas, budgets, and closed vocabularies |

For a Garden entry, which is dense in versioned handles (`gec-ragopt-native/v5`), identity strings (`gec-evidence-ledger/v1;scope=run;...`), hard budgets (12 items / 18 000 runes), and closed vocabularies (epistemic grades, diagnosis classes, treatment mechanisms), the notation table is essential. A reader will frequently think "what did `gec-ragopt-native/v5` mean again?" — that is a notation-table lookup, not an alphabetic-index scan. Burying those handles in the alphabetic list makes them unfindable.

This playbook therefore produces a **hybrid index-plus-glossary** (a one-sentence definition folded into each index entry, because the task asks for both a short description *and* links) **plus a separate notation table** at the end. Keep the three jobs visibly separate even when they live in one file.

## 3. Where indexes live and how to name them

### 3.1 Location and naming

Each index lives in the project's Garden directory, beside its `README.md`:

```text
Research/Software Architecture Garden/<project>/Index of Design Patterns.md
Research/Software Architecture Garden/<project>/Index of Design Patterns - Rationale.md
```

Use the exact titles `Index of Design Patterns` and `Index of Design Patterns - Rationale` so the pair is recognizable across every project. The slug of the project directory is the Garden's existing project slug (e.g. `coinvault`, `ragopt`).

### 3.2 Frontmatter

Match the Garden entry's frontmatter discipline. Required keys:

```yaml
---
title: "<Project> — Index of Design Patterns"
aliases:
  - "<Project> design pattern index"
  - "<Project> glossary"
status: active
type: architecture-garden-index
created: YYYY-MM-DD
analyzed: YYYY-MM-DD
analysis_schema: architecture-garden-v1
repository: /absolute/path/to/repository
repository_commit: <40-char hash>      # inherited from the study
derived_from: Research/Software Architecture Garden/<project>/README.md
tags:
  - architecture-garden
  - <project>
  - design-pattern-index
  - <primary-topics>
related_notes:
  - "[[Research/Software Architecture Garden/<project>/README]]"
  - "[[Research/Software Architecture Garden/<project>/Index of Design Patterns - Rationale]]"
  - "[[Research/Software Architecture Garden/README]]"
---
```

The `derived_from` field is important: it records that the index's evidence is inherited from the study, and pins the same commit. The index never claims evidence the study did not first pin. The rationale's frontmatter mirrors this with `type: architecture-garden-index-rationale`.

### 3.3 Back-link from the study

A Garden quality criterion is that the study links back to its index. Add the index and rationale to the study's `related_notes` and to its `## Related studies` section:

```markdown
## Related studies

- [[Research/Software Architecture Garden/<project>/Index of Design Patterns|Index of Design Patterns]] — back-of-the-book index of this study's patterns and vocabulary, with a companion [[Research/Software Architecture Garden/<project>/Index of Design Patterns - Rationale|rationale]]
- [[Research/Software Architecture Garden/README|Software Architecture Garden]]
...
```

Run the Garden entry validator before and after this edit to confirm you introduced no new errors:

```bash
python3 .pi/skills/architecture-garden-analysis/scripts/validate_garden_entry.py \
  "Research/Software Architecture Garden/<project>/README.md"
```

The study's pre-existing validator errors (numbered headings the regex dislikes, a descriptive `dirty` worktree string, literal angle-bracket tags) are not yours to fix in this workflow; just confirm your *diff* adds none.

## 4. The entry anatomy

Every entry is a **heading**. This is the single most important mechanical decision, because it makes every entry an anchor.

### 4.1 Why headings, not bold paragraphs

In Obsidian, a markdown heading becomes a linkable anchor. So an entry written as:

```markdown
### Treatment-exercise proof

A measured delta counts only when the harness proves the mutation was causally live...
[[Research/.../coinvault/README#7.1 The treatment-exercise proof|§7.1]]. *see also* [[#Attribution law]].
```

lets every other entry write `*see also* [[#Treatment-exercise proof]]` and land exactly here. If entries were bold paragraphs (`**Treatment-exercise proof** — ...`), they would be unanchored, and `See`/`see also` could not be clickable. Headings also make the notation table and the rationale able to point at a specific entry (`[[Index of Design Patterns#Treatment-exercise proof]]`).

Use `###` for entries (so the file's `##` section headers like "How to read this index" stay above them) and `####` for subentries. Two levels is almost always enough; a back-of-book index is not an ontology browser.

### 4.2 The parts of an entry

A complete entry has, in order:

1. **The canonical name** — the heading. Choose the name a reader is most likely to search for; file alternates as `See` redirects (§8).
2. **A one-sentence definition** (the glossary job). State what it *is*, not where it is.
3. **Locators** — `§n.m` links into the study that substantively treat the concept. Primary appearance first, further occurrences after. Use the `[[path#Heading|§n.m]]` form so the link text is short and the target is the study section.
4. **A leading `↳` cross-reference** when the pattern travels — a link into the wider Garden or a Pattern Zoo where the same invariant appears. This lets a reader see at a glance whether a pattern is local or ecosystem-wide.
5. **A trailing maturity bracket** for patterns, e.g. `[Established]`, `[Candidate ecosystem pattern]`, `[Open correctness obligation]`, taken from the study's maturity table and the Garden's [[Research/Software Architecture Garden/README#Pattern maturity vocabulary|maturity vocabulary]].
6. **`see also` links** to related-but-distinct entries, and explicit *must not be confused with* notes where a conflation is the failure mode the system was built to prevent.

Example (from the coinvault index):

```markdown
### Treatment-exercise proof

A measured delta counts only when the harness proves from the observed event
stream that the mutation was causally live in the challenger arm and absent in
the incumbent; otherwise the cell fails as `treatment_not_exercised` and the
judge is never invoked. [Candidate ecosystem pattern]
[[Research/.../coinvault/README#7.1 The treatment-exercise proof|§7.1]],
[[Research/.../coinvault/README#14. Candidate ecosystem patterns|§14.1]].
*The strongest original contribution; no second implementation yet.*
*see also* [[#Attribution law]], [[#Treatment contract]], [[#One-change-per-candidate rule]].
```

### 4.3 A `See` redirect entry

A `See` redirect has no locators of its own; it exists only to route a reader from an alternate phrasing to the canonical entry:

```markdown
### Configuration is not behavior

*See* [[#Treatment-exercise proof]]. (The recorded conclusion from six failed
`default_results 5→8` experiments that measured nothing.)
```

The parenthetical is optional but valuable: it tells a reader *why* this phrasing exists, so the redirect teaches rather than merely routes.

## 5. The workflow: build candidates while reading, finalize after

The best index is built in two stages, the way a real back-of-book index is.

### 5.1 While reading the study (capture candidates)

As you read each section of the study, ask the question the index guide recommends:

> **What are the 3–10 questions for which this section is an answer?**

Those questions are your candidate entries. Do not extract every italicized term or every noun — extract the *questions a reader would bring to this section*. For a section on the treatment-exercise proof, the candidate questions are things like "how do you prove an A/B mutation actually fired?", "what happens to a cell that can't prove its treatment fired?", "what was the failure this mechanism was born from?" — not "what does `treatment-contract.yaml` contain?".

Record candidates as you go. A scratch list is fine:

```text
INDEX: treatment-exercise proof -- §7.1, §14.1
INDEX: configuration is not behavior -- See treatment-exercise proof (§7.1)
INDEX: treatment_not_exercised -- subentry of treatment-exercise proof, §7.1
INDEX: attribution law -- §1, §11 (the governing idea)
```

Don't worry about alphabetical order, exact wording, or page ranges yet. Capture the *concept and its locator*.

### 5.2 After the study is final (build the index)

Once the study's headings are stable (so the `§` anchors won't drift), build the index:

1. **Merge synonyms.** Decide a canonical name for each concept; file the alternates as `See` redirects (§8).
2. **Write each entry** in the §4.2 anatomy. One sentence of definition, the substantive locators, the cross-reference, the maturity bracket, the `see also`.
3. **Add subentries** where an entry has more than ~5–7 undifferentiated locators or where a concept has meaningful sub-questions (§9).
4. **Build the notation table** (§10) from the versioned handles, schemas, budgets, and closed vocabularies you met.
5. **Add missing access points** — re-read the study asking "what might a reader call this who doesn't know my terminology?"
6. **Add cross-references** — `see also` between related entries, and the wider-Garden `↳` links.
7. **Remove trivial mentions** — apply the disappointed-reader test (§7) and delete any locator that sends a reader to a passing mention.
8. **Validate** with `scripts/validate_index_links.py` (§12).
9. **Read the index by itself.** It should almost look like a compressed conceptual outline of the study. If it reads like a word list, start over.

### 5.3 Write the rationale last

The rationale is the editor's marginalia. For each entry, answer two questions:

- **Chosen because** — what kind of evidence grounds it, and (for patterns) why this maturity label.
- **Belongs because** what a reader loses if the entry is omitted — the conflation it prevents, the operational consequence it carries, or the open obligation it keeps visible.

Add a short "principles of selection" section and a "what was deliberately excluded" section (an index is defined by its omissions; saying what you left out and why is part of the deliverable). Then link each rationale section back to its index entry — `> Index entry: [[Index of Design Patterns#<canonical>]].` — and validate those links too.

## 6. What to index

Index at the level of abstraction readers use. For a Garden study, the useful categories are:

| Category | Examples from the coinvault index | When to include |
|---|---|---|
| **Concepts / laws** | Attribution law, Witness/gate separation, One-change-per-candidate rule | The core. The governing ideas and the invariants. |
| **Named objects / vocabulary** | EvidenceLedger, EvalSet, Native artifact, Cell, Candidate bundle | Durable handles a reader will meet in code and receipts. |
| **Operations / procedures** | "Diagnosing a retrieval failure", "Judging an answer", "Promoting a candidate" | Readers often remember what they want to *do*, not the noun for it. Add these even if the verb never appears as a heading. |
| **Properties** | Determinism by prefix derivation, Structural validation of judge output | Named properties that carry an operational consequence. |
| **Theorems / laws (named and unnamed)** | Treatment-exercise proof (and its general-form law), Double verdict | Named results *and* memorable unnamed distinctions. Index the conclusion, not only the name. |
| **Examples / canonical problems** | "the six default-results experiments", the `grounded-answer-v2` decision | The concrete instances a reader will remember the concept by. |
| **Failure modes** | `treatment_not_exercised`, Concentration crowd-out, Golden-set rot, Under-counted spend | Under-indexed in practice; readers search for them constantly. Index them as carefully as the patterns. |
| **Architecture debt / open obligations** | Reviewed suite lock (open), Judge spend call-bounded not token-bounded, Feedback-to-corpus (designed, not built) | An index that lists only successes flatters the system. The debt and open laws belong. |
| **Closed vocabularies** | Epistemic grades, Diagnosis classes, Treatment mechanisms | The enumerated sets a reader must choose from. These usually belong in the notation table (§10). |
| **Applications / why it matters** | "Runtime citation grounding" linking production and eval | When the study says *why* something matters, index that connection. |
| **Garden-defined vocabulary** | Maturity labels, Pattern maturity assessment | Terms shared across every Garden entry; index them so the index speaks the Garden's dialect. |

What **not** to index: routine composition over upstream projects that have their own entries (link out instead), one-off identifiers with no conceptual weight, and every occurrence of a noun. The objective is *useful retrieval paths over reader effort*, not number of entries.

## 7. The disappointed-reader test

Before keeping a locator, imagine a reader deliberately looked up `Term → Subentry` and followed the reference. Would they find enough discussion at that section to justify your sending them there?

If a section only says "unlike X, Y can…" in passing, do not index it under X unless the comparison is genuinely the thing a reader wants. A locator is a promise that the linked section *teaches* the concept. Remove locators that fail the promise.

This single rule dramatically improves indexes. It is also the rule that keeps the index from becoming a concordance: a concept may appear on twenty pages but only *substantively* treated on two — index the two.

## 8. Access paths and `See` redirects

Readers rarely remember your terminology exactly. If you call something *witness/gate separation*, a reader may search "judge as witness", "judge not a gate", or "the witness-not-gate thing". A good index accommodates all of them:

```markdown
### Judge as witness, not a gate

*See* [[#Witness/gate separation]].
```

Add a `See` redirect for every plausible alternate phrasing, every reader-memory handle, and every synonym. The coinvault index carries 17 such redirects ("configuration is not behavior" → Treatment-exercise proof; "no apply command exists" → Human promotion authority; "held-out leakage (prevented)" → Held-out split, structurally closed; "under-counted spend" → Sticky close on unprovable spend). A `See` redirect is one of the strongest signals that an index was *designed* rather than *generated*.

Distinguish `See` from `see also`:

- **`See`** — the entry has no useful locators of its own; route to the canonical entry.
- **`see also`** — both entries have locators; point at related material the reader should not collapse into one.

Be careful with things that are *related* but not *synonymous*. A heap is one implementation of a priority queue; do not write "heap. *See* priority queue". Instead:

```markdown
### Heaps
...
*see also* [[#Priority queues]] (a heap is one implementation, not identical).
```

The Garden's central discipline is anti-flattening — a registry is not authority, a snapshot is not always an immutable release, configuration is not behavior, a gate pass is not promotion. Your `see also` notes are where you keep those distinctions visible.

## 9. Subentries: when and how

An entry with a long undifferentiated cloud of locators tells the reader almost nothing. The guide's rule of thumb: if an entry has more than ~5–7 undifferentiated locators, consider subentries.

Use `####` for a subentry, and make subentries answer *meaningful questions*, not grammatical decomposition. Bad subentries (`algorithm`, `example`, `property`, `theorem`) tell you little. Good subentries name the sub-question:

```markdown
### Treatment-exercise proof
...definition and locators...

#### The law, in general form
A delta between arms is evidence about a mutation only if the run proves...
[[Research/.../README#7.1 The treatment-exercise proof|§7.1]].

#### The failure it was born from
Six successive `default_results 5→8` experiments measured nothing...
[[Research/.../README#7.1 The treatment-exercise proof|§7.1]].

#### Cell failure class
`treatment_not_exercised` — the cell fails before judging when...
```

Keep hierarchy shallow — usually two levels (entry, subentry). A back-of-book index is not an ontology browser; flatten aggressively.

## 10. The notation table

Garden studies speak in versioned handles and closed vocabularies. Give them a table, not a paragraph:

```markdown
## Identity strings, schemas, and budgets

This is the index's notation table. A reader will frequently think
"what did `gec-ragopt-native/v5` mean again?" Look it up here, then follow the §-link.

| Handle / schema | Kind | Meaning | Where |
|---|---|---|---|
| `gec-evidence-ledger/v1` | identity string | EvidenceLedger policy: run-scoped, dedupe=chunk... Full form `gec-evidence-ledger/v1;scope=run;dedupe=chunk;max_items=12;max_runes=18000`. | [[...#1. The system under evaluation|§1]], [[#EvidenceLedger]] |
| `gec-ragopt-native/v5` | artifact schema | Private native artifact: full trace, per-statement verdicts... | [[...#7.5 The information boundary and the double verdict|§7.5]], [[#Native artifact]] |
| Evidence budget | budgets | 12 items / 18 000 runes per EvidenceLedger. | [[...#1. The system under evaluation|§1]], [[#EvidenceLedger]] |
| Epistemic grades | closed vocabulary | `measured | estimate | association | hypothesis`. | [[...#9. Runtime grounding: the always-on loop|§9]], [[#Epistemic grade]] |
| Treatment mechanisms (9) | closed vocabulary | default/forced result budgets; comparison decomposition/intent; grounding/routing/policy prompts; reranker; tool description. | [[...#7.1 The treatment-exercise proof|§7.1]], [[#Treatment mechanisms]] |
```

Put in the table: schema versions, identity strings, hard budgets, closed vocabularies (the enumerated sets a reader must choose from), and source-lock / cache-key components. Each row carries a `Where` column with *two* links — the `§` into the study and the `[[#Entry]]` into the alphabetic index — so a reader can go from handle → meaning → full entry → study in one path.

## 11. Cross-references and the wider Garden

An index for one Garden entry is also a node in a Garden-wide glossary. Two rules keep the set of indexes cross-referenceable rather than seventeen independent alphabets:

1. **Shared terms use the same canonical name across projects.** Concepts the Garden already recognizes — *semantic identity as explicit projection*, *exact experimental coordinates*, *constraint-first decisions*, *run custody* — should be filed under the same name in every project's index, with a `↳` link to the Pattern Zoo or the sibling entry. Do not invent a new name for a relation the Garden already has.
2. **Local names are preserved but not flattened.** A project-local name (e.g. coinvault's `EvidenceLedgerID`) gets its own entry, and the entry's `↳` link notes the Garden-wide relation it is a local instance of. Preserve the overload; state what must remain distinct.

Add a short **Cross-reference summary** at the end of the index listing the load-bearing correspondences to the Pattern Zoos, each marked as a *correspondence, not an equivalence* — the Garden's standing discipline that a registry is not authority and a snapshot is not always an immutable release.

## 12. Link validation

An Obsidian index is only as trustworthy as its links. Validate before calling it done. This playbook ships a dependency-free validator:

```text
Research/playbooks/scripts/validate_index_links.py
```

It checks every `[[...]]` link in a markdown file — intra-file `[[#Heading]]`, cross-file `[[path]]`, `[[path#anchor]]`, and the `|alias` variants — resolving targets both vault-rooted and folder-relative, and accepting files with or without `.md`. It skips links inside fenced code blocks and inline code spans, the way Obsidian renders them, so example syntax in a playbook or doc does not produce false positives; it also normalizes inline code inside anchors so a link whose heading contains a backtick-word (`` `require()` ``) still resolves. It reports broken intra-file anchors, missing files, and missing cross-file anchors separately.

Run it on the index and the rationale together:

```bash
python3 Research/playbooks/scripts/validate_index_links.py \
  "Research/Software Architecture Garden/<project>/Index of Design Patterns.md" \
  "Research/Software Architecture Garden/<project>/Index of Design Patterns - Rationale.md" \
  "Research/Software Architecture Garden/<project>/README.md"
```

Exit code 0 means every link resolves. A negative test (a temp file with a fake anchor and a fake heading) should report both problems and exit 1 — run it once to confirm the validator actually catches errors, then trust its clean pass.

Validate *iteratively*: add a batch of entries, run the validator, fix the broken anchors (usually a heading that doesn't match the link text, or a `See` target you forgot to create), repeat. Catching a missing entry when it is one edit old is far cheaper than hunting it across a finished index.

## 13. The reader-situation usability test

Once the index is drafted and validates, do the test the index guide recommends: invent 20–30 realistic reader situations and trace each to the entry that serves it. This is usability testing for the index.

Write the situations as a section in the rationale, with each arrow an actual anchor:

```markdown
1. *"There was a mechanism that proves the A/B mutation actually did something,
   not just that the config changed."* → [[Index of Design Patterns#A/B experiment, proving the mutation fired]]
   → [[Index of Design Patterns#Treatment-exercise proof]] → §7.1.
2. *"What was the phrase they coined when the default-results experiments
   measured nothing?"* → [[Index of Design Patterns#Configuration is not behavior]]
   → [[Index of Design Patterns#Treatment-exercise proof]] → §7.1.
```

The situations that needed a `See` redirect are exactly the ones where a reader remembers the *idea* but not the study's spelling — which is the case the redirects exist to serve. If a situation cannot be traced to a substantive section, either add an access path or remove a locator that fails the disappointed-reader test. The coinvault rationale carries 20 such situations; that is a reasonable size for a first index.

## 14. Common failure modes

The indexes that are least useful suffer from some combination of:

- **indexing words instead of ideas** — extracting terminology rather than questions;
- **indexing every occurrence** — a concordance, not an index;
- **hundreds of bare page-number lists** — no subentries, no compression;
- **missing synonyms** — no `See` redirects from reader-memory phrasings;
- **no inversion of relationships** — *dynamic programming → shortest paths* indexed but not *shortest paths → dynamic programming*;
- **no entries for reader tasks** — readers remember what they want to *do*; index the verbs;
- **no entries for failure cases** — failure modes and open obligations under-indexed;
- **excessively deep hierarchy** — a back-of-book index is not an ontology browser;
- **confusing related concepts with synonyms** — `See` when you mean `see also`;
- **indexing definitions but not applications** — the "why it matters" connection missing;
- **indexing theorem names but not conclusions** — a reader remembers the conclusion, not the name;
- **sending readers to passing mentions** — failing the disappointed-reader test;
- **treating auto-generated keyword extraction as a finished index.**

LLMs can produce *candidate* entries, but the conceptual access structure — which concept is canonical, what redirects to it, what subentries are meaningful — needs human (or human-equivalent agent) review. The validator can confirm links resolve; it cannot confirm the index is well-designed. That is what the reader-situation test is for.

## 15. Worked example: the CoinVault index

The first instance of this playbook is the [[Research/Software Architecture Garden/coinvault/Index of Design Patterns|CoinVault index]]. Its shape, as a concrete reference point:

- **83 `###` entries** across A–W, each a heading (anchorable), each with a one-sentence definition + `§` locators into the coinvault study + `↳` cross-Garden links + a maturity bracket + `see also`.
- **17 `See` redirects** from reader-memory phrasings ("configuration is not behavior", "judge as witness, not a gate", "no apply command exists", "under-counted spend") to canonical entries.
- **4 `####` subentries**, all under the treatment-exercise proof, each answering a meaningful sub-question (the general-form law, the failure it was born from, the cell failure class, and the evidence-admission fix).
- **A 10-row notation table** (`## Identity strings, schemas, and budgets`) covering the versioned handles (`gec-evidence-ledger/v1`, `gec-ragopt-native/v5`, `EvalSet` v3, `judgePromptVersion` v2, `<gec:sources:v1>`), the three semantic identity strings, the hard budgets, and the closed vocabularies (epistemic grades, diagnosis classes, treatment mechanisms, component-ledger statuses, eval strata, limit-resolution sources).
- **A cross-reference summary** linking the four load-bearing correspondences to the RAG Pattern Zoo, each marked *correspondence, not equivalence*.
- **A companion rationale** with 5 selection principles, a "what was deliberately excluded" section, 66 per-term justifications (each linked back to its index entry), and a 20-situation reader-situation test.
- **All links validated**: 235 intra-file + 154 cross-file links across the index, rationale, and back-linked study, every one resolving.

Read it alongside its [[Research/Software Architecture Garden/coinvault/Index of Design Patterns - Rationale|rationale]] before building the next one. The coinvault index is the calibration target.

## 16. Final checklist

Before calling an index done:

- [ ] The index and rationale live beside the study, named exactly `Index of Design Patterns.md` and `Index of Design Patterns - Rationale.md`.
- [ ] Frontmatter is complete and inherits the study's `repository_commit`; `derived_from` points at the study.
- [ ] The study back-links both files (frontmatter `related_notes` + `## Related studies`); the Garden entry validator shows no *new* errors from your edit.
- [ ] Every entry is a `###` heading (subentries `####`); every `See` and `see also` is a clickable `[[#...]]` anchor.
- [ ] Every pattern entry carries a maturity bracket from the study's maturity table.
- [ ] Every versioned handle, schema, budget, and closed vocabulary is in the notation table, not the alphabetic list.
- [ ] At least one `See` redirect exists for each concept a reader might plausibly search under a different name.
- [ ] Failure modes and open obligations are indexed as carefully as established patterns.
- [ ] The disappointed-reader test has been applied: no locator points at a passing mention.
- [ ] A cross-reference summary marks the load-bearing Garden/Pattern-Zoo correspondences as *correspondence, not equivalence*.
- [ ] `scripts/validate_index_links.py` reports PASS for the index, the rationale, and the study.
- [ ] A reader-situation test of ~20 situations is in the rationale; each traces to a substantive section.
- [ ] The rationale has a "what was deliberately excluded" section.
- [ ] Read by itself, the index resembles a compressed conceptual outline of the study — not a word list.

## Related

- [[Research/Software Architecture Garden/coinvault/Index of Design Patterns|CoinVault index]] — the worked example this playbook distills.
- [[Research/Software Architecture Garden/coinvault/Index of Design Patterns - Rationale|CoinVault index rationale]] — the editor's marginalia.
- [[Research/playbooks/creating-github-issues-and-software-design-garden-entries|Playbook: Creating GitHub Issues and Software Design Garden Entries]] — the upstream workflow that produces the study an index is built from.
- [[Research/Software Architecture Garden/README|Software Architecture Garden]] — the Garden root, its maturity vocabulary, and its evidence hierarchy.
- `Research/playbooks/scripts/validate_index_links.py` — the link validator shipped with this playbook.
