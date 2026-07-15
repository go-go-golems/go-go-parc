---
title: "Playbook: Creating Project Maps of Content (MOCs)"
slug: "creating-mocs"
short: "Research a topic cluster, choose a durable home, create a navigational MOC, and cross-link the source notes without turning the MOC into another project report."
topics:
  - parc
  - knowledge-base
  - moc
  - information-architecture
  - obsidian
section_type: Playbook
updated: 2026-07-15
---

# Playbook: Creating Project Maps of Content (MOCs)

A Map of Content is a durable navigation note for a topic that spans several project reports, articles, guides, and knowledge-base entries. It is not a summary of every source note. Its job is to give a reader the shortest reliable path from a topic name to the right level of detail.

A good MOC answers four questions immediately:

1. What is this topic or body of work?
2. Which notes explain its architecture, implementation, history, and usage?
3. In what order should a newcomer read those notes?
4. Where does the topic connect to reusable patterns elsewhere in the vault?

The MOC should remain useful when new dated reports are added. Historical notes retain their original context; the MOC provides the stable current map.

## When to create a MOC

Create a MOC when a topic has enough durable material that search results stop providing a useful reading order. Practical signals include:

- At least three related notes exist across more than one date or document type.
- The topic has distinct layers, such as API, runtime, operations, results, and history.
- A reader needs to distinguish current documentation from historical or deprecated material.
- The topic connects a project repository to reusable knowledge-base patterns.
- The same topic is likely to receive more reports later.

Do not create a MOC for one isolated project report. Add a `Related notes` section to that report instead, and create the MOC when the cluster has a real navigation problem.

## Choose the MOC's home

The MOC's location should reflect its role, not the date on which it was written.

```text
go-go-parc/
  Projects/YYYY/MM/DD/    dated reports and articles
  Research/KB/
    Fundamentals/         reusable theory
    On-Ramp/              orientation to lookupable concepts
    Tribal/               recurring implementation patterns
    Projects/             durable maps for project/topic clusters
  Research/playbooks/     procedures for doing recurring work
```

Use `Research/KB/Projects/` for a project-centered or tool-centered MOC that gathers dated reports and articles. Use `Research/KB/Tribal/` when the note itself teaches a reusable implementation pattern rather than primarily indexing project material. Use `Research/playbooks/` for the procedure that explains how to create or maintain MOCs; do not put individual topic MOCs there.

Examples:

- `Research/KB/Projects/researchctl.md` maps the researchctl graph DSL, codesign runtime, experiment catalog, and implementation reports.
- `Research/KB/Projects/go-minitrace.md` maps transcript conversion, normalized SQLite querying, annotations, exports, and analysis case studies.
- `Research/KB/Tribal/dsl-normalized-config-compiled-plan.md` explains a reusable DSL architecture and is not merely a list of project reports.

Prefer one stable filename per topic, usually lowercase kebab-case: `researchctl.md`, `go-minitrace.md`, or `browser-sandbox-runtime.md`.

## Research the note cluster first

Before writing, inventory the vault and the source repository. Search broadly, then classify each result by role rather than treating every keyword hit as equally important.

```bash
rg -l -i 'topic|alias|repository-name' --glob '*.md' Projects Research
find Projects Research -type f -iname '*topic*' | sort
```

For each candidate note, record:

| Field | Question |
|---|---|
| Role | Is it history, architecture, API, operations, results, or reusable pattern? |
| Status | Is it current, historical, deprecated, or inconclusive? |
| Date | When was the report written? |
| Repository | Which source tree does it describe? |
| Relationship | What does a reader learn here that the other notes do not? |
| Link target | What exact vault filename should the wikilink use? |

Read the opening sections, summaries, headings, and `Related notes` sections of the strongest candidates. Read the repository README and the important source directories when the MOC will include an implementation map. Do not infer architecture from filenames alone.

## Define the MOC's organizing model

A MOC should impose a useful reading structure on a chronological corpus. A reliable default is:

1. **Definition:** the shortest accurate description of the topic.
2. **Architecture:** the major layers and their boundaries.
3. **Workflow:** how a user or developer moves through the system.
4. **Current implementation:** packages, commands, or repository paths.
5. **Use cases or experiment catalog:** what the system is used to do.
6. **Related notes:** links grouped by role and reading order.
7. **Boundaries:** limitations, deprecated surfaces, and open questions.

Do not organize only by filename or creation date. Dates remain useful in frontmatter and link descriptions, but a reader usually wants “start here,” “understand the runtime,” and “see the results,” not a directory listing.

When the topic has two or more distinct subsystems, name the boundary explicitly. For example, researchctl has a research-graph DSL and a codesign execution DSL; go-minitrace has archive conversion, normalized querying, human review, and portable export. Naming those layers prevents a MOC from collapsing different contracts into one vague “tool” description.

## Write the MOC

Use frontmatter that makes the note discoverable and identifies it as a durable project map:

```yaml
---
title: "<Topic> — <Short durable description>"
aliases:
  - <common name>
  - <alternate spelling>
  - <topic> MOC
tags:
  - knowledge-base
  - project
  - <topic>
status: active
type: knowledge-base
created: "YYYY-MM-DD"
repo: /absolute/path/to/repository
---
```

The body should normally contain:

```markdown
# <Topic> — <Short durable description>

<One or two paragraphs defining the topic and the purpose of the map.>

> [!summary]
> - <identity or layer one>
> - <identity or layer two>
> - <important boundary>

## The core mental model

<Short prose model, optionally with a Mermaid diagram.>

## Architecture or layers

<Explain the major components and their contracts.>

## Workflow

<Give the recommended reading or operational sequence.>

## Related notes

### Current architecture
- [[Exact note filename]] — what the reader learns there.

### History and results
- [[Exact note filename]] — what the reader learns there.

## Repository map

<Only include source paths that were verified.>

## Boundaries and open questions

<Limitations, stale material, and unresolved design questions.>
```

The MOC should contain enough prose to explain why the links are grouped together, but not enough detail to compete with the linked articles. A link description should tell the reader what unique question that note answers.

Use Mermaid for one or two high-value diagrams: a system boundary, a data flow, or a reading/workflow pipeline. Do not add a diagram merely to decorate the note.

## Link correctly

Use Obsidian wikilinks for vault notes. Prefer the exact filename without `.md`, especially when the vault's titles and filenames differ:

```markdown
[[ARTICLE - go-minitrace Query Engine Migration - DuckDB to Normalized SQLite]]
[[Research/KB/Tribal/goja-embedding-in-go]]
```

For a same-topic MOC, `[[researchctl]]` or `[[go-minitrace]]` is acceptable when the basename is unique. Use a path when ambiguity is possible.

Cross-link in both directions when the relationship is important:

- The MOC links to the source article with a useful description.
- The source article links back to the MOC near its introduction or in `Related notes`.

Do not add a backlink to every incidental mention. Link the core cluster, adjacent reusable patterns, and the broader project or research context. A MOC with twenty carefully grouped links is useful; a MOC with one hundred undifferentiated links is search results in disguise.

## Handle historical and deprecated notes

A MOC should preserve history without presenting stale commands as current instructions.

Use a separate migration or deprecation note when a tool surface changed substantially. Link that note near the top of the MOC and label affected source notes clearly. Keep historical reports append-only unless the user explicitly requests a rewrite.

A link description should distinguish:

- **Current:** safe starting point for present implementation.
- **Historical:** records how the system or project looked at a particular time.
- **Deprecated:** conclusions may remain useful, but commands, APIs, or assumptions require migration.
- **Inconclusive:** evidence was collected, but the stated hypothesis was not established.

This is more useful than silently editing old prose until the historical record no longer reflects what happened.

## Validate the MOC

Before committing, validate both content and graph integrity.

```bash
# Check whitespace errors
git diff --check

# Find all wikilinks in the new MOC
rg -n '\[\[' Research/KB/Projects/<topic>.md

# Inspect the intended diff
git diff -- Research/KB/Projects/<topic>.md
```

A simple exact-basename check catches many broken links:

```bash
python3 - <<'PY'
from pathlib import Path
import re

root = Path('.')
known = {p.stem for p in root.rglob('*.md')}
path = root / 'Research/KB/Projects/<topic>.md'
links = re.findall(r'\[\[([^\]|#]+)', path.read_text())
missing = sorted({link for link in links if link not in known})
print('unresolved:', missing or 'none')
PY
```

Then verify the note manually in Obsidian reading view. Check that Mermaid renders, callouts are readable, aliases are useful, and the first screen tells a newcomer where to begin. If the MOC links to a note with a prefix such as `ARTICLE -` or `PROJECT REPORT -`, verify that the complete basename is used.

## Commit and maintain

Stage only the MOC, intentional backlink edits, and any deliberately updated navigation index. Never stage `.obsidian/workspace.json`, `.pi/`, `.ttmp.yaml`, generated exports, or unrelated vault changes merely because they appear in the worktree.

```bash
git add \
  Research/KB/Projects/<topic>.md \
  'Projects/.../related-note.md' \
  index.md

git diff --cached --check
git commit -m "docs(vault): add <topic> project map"
git push origin main
```

When a new report is created, update the MOC only if it adds a genuinely new role or reading path. Keep link descriptions short and specific. If the MOC becomes a second encyclopedia article, move durable explanations into a KB entry or article and leave the MOC as the map.

## Review checklist

- [ ] The topic has enough related material to justify a map.
- [ ] The MOC lives in `Research/KB/Projects/` for a project/topic cluster.
- [ ] The filename is stable and easy to search.
- [ ] Frontmatter includes title, aliases, tags, status, type, date, and repository when relevant.
- [ ] The opening paragraph defines the topic without repeating a source report.
- [ ] The notes are grouped by role and reading order.
- [ ] Current, historical, deprecated, and inconclusive material is distinguished.
- [ ] Core source notes link back to the MOC.
- [ ] Wikilinks resolve to exact vault note basenames.
- [ ] Repository paths and implementation claims were verified.
- [ ] The MOC contains no unrelated links or copied report-length sections.
- [ ] `git diff --check` passes.
- [ ] Only intended files are staged and committed.
