---
title: "Playbook: Extracting Tribal Knowledge into KB Entries"
aliases:
  - Tribal KB Extraction Playbook
  - KB Entry Playbook
tags:
  - playbook
  - knowledge-base
  - tribal-knowledge
  - go-go-parc
status: active
type: playbook
created: 2026-05-31
---

# Playbook: Extracting Tribal Knowledge into KB Entries

## Purpose

This playbook describes how to read project reports from the Obsidian vault, identify reusable tribal knowledge, and write it into the go-go-parc Knowledge Base at `~/code/wesen/go-go-golems/go-go-parc/Research/KB/`.

Every F-SRP ticket (F-SRP-01 through F-SRP-08) follows this same process. This playbook is the shared reference; each ticket's instruction guide provides the specific inputs and scope.

## The KB Directory Structure

```
~/code/wesen/go-go-golems/go-go-parc/Research/KB/
├── Fundamentals/    — Foundational concepts (rendering pipeline, signal quantization, access control)
├── On-Ramp/         — Getting-started guides for a technology or tool (esc-pos, wasm-from-go, crdts)
└── Tribal/          — How we do things — reusable patterns, practices, and working rules
```

**Where to put new entries:**
- **Tribal/** if the entry describes a pattern, practice, or working rule that our team has discovered and validated through multiple projects
- **On-Ramp/** if the entry is a getting-started guide for a technology that a new team member would need to understand before working in the codebase
- **Fundamentals/** if the entry covers a foundational concept that underlies multiple systems

## KB Entry Format

Every KB entry follows this structure (see existing entries for examples):

```markdown
---
title: "Entry Title — Subtitle"
aliases:
  - Alternative search term 1
  - Alternative search term 2
tags: [knowledge-base, tribal, tag1, tag2, tag3]
status: active
type: knowledge-base
created: YYYY-MM-DD
repos:
  - /path/to/primary/repo
---

# Entry Title — Subtitle

> [!summary]
> 2-4 sentence summary of the pattern and why it matters. This is the most important
> part — it's what someone reads first when deciding whether the entry is relevant.

## The pattern

Describe the pattern in prose. What is the recurring shape? When does it appear?
What problem does it solve? Include a diagram or pseudocode if the pattern has
a structural element.

## Why we do it this way

Explain the reasoning. What alternatives were tried and rejected? What failure
modes does this pattern prevent? This section is where tribal knowledge lives —
it captures the "why" that code alone doesn't express.

## Evidence

List the project reports that demonstrate this pattern, with dates and one-line
descriptions of what each report contributes:

| Report | Date | Contribution |
|---|---|---|
| ARTICLE - ... | 2026-05-23 | First instance of the pattern |
| ARTICLE - ... | 2026-05-26 | Refinement after architectural correction |

## Working rules

Numbered list of concrete, actionable rules that follow from the pattern.
These are the "always do X" and "never do Y" statements.

1. Always do X because...
2. Never do Y because...
3. When Z happens, do...

## Gotchas

Non-obvious pitfalls that someone following the pattern might hit:

1. **Gotcha name**: What goes wrong, what it looks like, how to fix it.

## Related KB entries

- `Tribal/related-entry-1.md` — relationship description
- `On-Ramp/related-entry-2.md` — relationship description
```

## The Extraction Process

### Step 1: Read the source reports

Each F-SRP ticket lists specific reports to read. Read them fully (not just summaries). As you read, take notes on:

- **The pattern**: What recurring shape do you see? What's the invariant?
- **The reasoning**: Why was this approach chosen? What was tried and rejected?
- **The failures**: What went wrong? How was it debugged?
- **The working rules**: What "always/never" rules emerge?
- **The gotchas**: What's non-obvious? What would a newcomer miss?

### Step 2: Synthesize the pattern

Write the KB entry following the format above. Key principles:

1. **Write for a new team member.** The entry should be understandable by someone who has never worked on these projects.
2. **Be concrete, not abstract.** Include specific commands, code snippets, file paths, and numbers. "Always use `BEGIN IMMEDIATE`" is better than "use transactional locking."
3. **Capture failure modes, not just successes.** The tribal knowledge is often in what went wrong and how it was fixed.
4. **Include evidence.** Link to the specific project reports that demonstrate the pattern.
5. **State working rules explicitly.** Don't bury them in prose — make them numbered and scannable.

### Step 3: Write the KB entry file

Create the file at the correct path under `~/code/wesen/go-go-golems/go-go-parc/Research/KB/`.

Use the filename convention: `kebab-case-description.md` (e.g., `esp32-wifi-image-pipeline-optimization.md`).

### Step 4: Add cross-references

Update the `## Related KB entries` section of any existing KB entries that are related to the new entry. Add a backlink from the new entry to those existing entries.

Check these existing entries for potential cross-references:

```
Tribal/sqlite-as-application-database.md
Tribal/reduction-ladder-debugging.md
Tribal/dsl-normalized-config-compiled-plan.md
Tribal/pi-extension-event-seams.md
Tribal/goja-embedding-in-go.md
Tribal/goja-execution-model.md
Tribal/bubbletea-streaming-llm-uis.md
Tribal/canonical-doc-model-across-delivery-modes.md
Tribal/browser-side-processing-for-embedded.md
On-Ramp/esc-pos-thermal-printer.md
On-Ramp/dithering-and-rasterization.md
On-Ramp/e-ink-display-driving.md
On-Ramp/web-serial-browser-to-embedded.md
On-Ramp/go-cli-with-embedded-spa.md
```

### Step 5: Commit and push

```bash
cd ~/code/wesen/go-go-golems/go-go-parc
git add Research/KB/
git commit -m "KB: add <entry-title>"
git push
```

### Step 6: Update the F-SRP ticket

- Check off the task in the ticket
- Update the ticket diary with what was done
- Update the ticket changelog

## Vault Report Reading Tips

The vault reports are at `~/code/wesen/go-go-golems/go-go-parc/Projects/YYYY/MM/DD/`. They follow two formats:

- **ARTICLE** — Durable knowledge documents with `> [!summary]` callouts, architecture diagrams, and working rules. These are the richest source of tribal knowledge.
- **PROJ** — Project reports describing what was built, why, and current status. More implementation-focused.

When reading a report:
1. Start with the `> [!summary]` callout — it captures the key takeaways.
2. Read the "Why this article/project exists" section — it explains the motivation.
3. Scan for numbered rules, "always/never" statements, and "gotcha" sections.
4. Note specific commands, code snippets, and measured numbers.

## Cross-Referencing with Existing KB Entries

Before writing a new entry, check whether an existing entry already covers part of the pattern:

```bash
ls ~/code/wesen/go-go-golems/go-go-parc/Research/KB/Tribal/
ls ~/code/wesen/go-go-golems/go-go-parc/Research/KB/On-Ramp/
ls ~/code/wesen/go-go-golems/go-go-parc/Research/KB/Fundamentals/
```

If an existing entry covers part of the pattern:
- **Extend it** if the new evidence naturally fits within the existing entry's scope
- **Create a new entry with backlinks** if the pattern is distinct enough to warrant its own document

The `aliases` field in the frontmatter is important for discoverability — add alternative names that someone might search for.

## Writing Style

- **No analogies.** The textbook-authoring skill's rule applies: explain directly, don't compare to unrelated domains.
- **No hedged non-claims.** "We generally prefer to..." is weak. "Always use X because..." is strong.
- **No vague bullet lists.** Every bullet should carry its weight. If a bullet can be removed without losing information, remove it.
- **Be opinionated.** KB entries are tribal knowledge — they capture how we do things, not a survey of all possible approaches.

## Common Pitfalls

1. **Writing a literature survey instead of tribal knowledge.** The KB is not Wikipedia. It captures how our team does things and why.
2. **Missing the failure modes.** The most valuable tribal knowledge is often "we tried X and it failed because Y." Don't just document the winning approach.
3. **Too abstract.** "Use a structured intermediate representation" is weak. "The VLM returns `StructuredPageOCR` JSON; Go code renders Markdown deterministically. The VLM never touches the final document" is strong.
4. **Missing working rules.** These are the most actionable part of a KB entry. If you can't state at least 3 "always/never" rules, you haven't extracted the pattern deeply enough.
5. **Forgetting gotchas.** The non-obvious pitfalls are exactly what makes knowledge "tribal" — it's the stuff that isn't obvious from reading the code.
