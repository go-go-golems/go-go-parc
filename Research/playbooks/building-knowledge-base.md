---
title: "Playbook: Building the go-go-parc Knowledge Base"
slug: "building-knowledge-base"
short: "Analyze project reports, classify concepts, and write Tribal, On-Ramp, and Fundamental entries for the go-go-parc knowledge base."
topics:
  - parc
  - knowledge-base
  - go-go-golems
  - playbook
section_type: Playbook
updated: 2026-05-11
---

# Playbook: Building the go-go-parc Knowledge Base

This playbook tells you how to take a project report from the PARC library, extract the concepts it depends on, classify those concepts, and create or update knowledge base entries. The goal is a consistent, growing library that lets any team member — human or agent — understand any project report without getting stuck on an unfamiliar concept.

---

## What the KB is for

The knowledge base has one job: **make project reports readable.**

When you open a project report about a Smalltalk VM, you should not have to stop and Google "what is an operand stack." When you open a project report about BYOK Host, you should not have to puzzle through the difference between authentication and authorization. The KB gives you the 10-minute orientation or the "how we do it" reference before you need it.

The KB does **not** replace textbooks. It does **not** replace project reports. It sits between them — the on-ramp that makes the project report accessible, the tribal entry that makes the implementation consistent.

The KB currently contains 18 entries (6 Tribal, 8 On-Ramp, 4 Fundamentals, ~107 KB total). This playbook documents how those entries were written and how future entries should be written to maintain consistent quality.

---

## The three-section KB

The knowledge base has three sections. Each one has a different purpose, a different template, and a different trigger rule.

```
go-go-parc/
  Research/
    KB/
      Tribal/          ← "How we do it" — our patterns, can't Google these
      On-Ramp/         ← "What it is, why we care" — 10-minute orientation
      Fundamentals/    ← "The textbook chapter you actually need" — theory foundations
```

### When to use each section

| Section | Purpose | Trigger | Who reads it |
|---------|---------|---------|-------------|
| **Tribal** | Our standard way of doing something | 3+ projects use the same pattern, and you can't find it in public docs | Someone implementing something |
| **On-Ramp** | Quick orientation for a lookupable concept | 5+ projects depend on this concept, and existing public docs are scattered/wrong/missing our angle | Someone reading a project report |
| **Fundamentals** | The textbook theory you actually need | A concept underlies multiple Tribal/On-Ramp entries and our projects keep getting it wrong because people don't know the theory | Someone designing or debugging something |

---

## Writing style: how to write well

The KB is only as useful as its writing quality. After writing 18 entries, we've learned what works and what doesn't. Follow these rules.

### The textbook style

Our entries follow a **Peter Norvig textbook style**: foundational first, concrete over abstract, no AI slop. The reader is capable — don't talk down to them. Don't qualify every statement with "of course" or "clearly." Let the ideas speak.

**Foundational first.** Start with the core idea before showing implementation. A reader who understands *why* a design decision was made can extend the pattern; a reader who only knows *how* copies it.

**Prose paragraphs that develop ideas.** Write in complete paragraphs that advance a thought. Avoid short, declarative sentences that feel like bullet points in disguise. A paragraph should do work — it should move the reader's understanding forward.

**Concrete over abstract.** Show real code, real error messages, real trace lines. Abstract descriptions of patterns are useful, but they land better when grounded in something the reader can see and run.

**Breaks in the rhythm.** Use code blocks, tables, and bullet points strategically to break up long passages of prose. These are part of the argument. A table comparing two approaches does work that prose cannot.

### Anti-patterns to avoid

| Anti-pattern | Example | Why it's bad | Fix |
|---|---|---|---|
| **Wandering preamble** | "In the ever-evolving landscape of modern firmware development..." | The reader learns nothing. Signals the writer doesn't trust the material. | Start with the point. |
| **Hedged non-claims** | "This approach could potentially offer certain advantages in terms of flexibility" | Says nothing while consuming words. | Be direct: "This approach offers flexibility and extensibility." |
| **Vague bullets** | "- Important concepts\\n- Key takeaways" | The reader cannot act on "important concepts." | Every bullet is a complete sentence that could stand alone. |
| **Overused qualifiers** | "Of course, it goes without saying that clearly..." | Filler that implies uncertainty. | Just say it. |
| **Philosophical throat-clearing** | "This pattern contains a profound elegance that reveals itself..." | Fills space, conveys no information. | Show the code, let reader decide. |
| **"As you can see"** | "As you can see, the result is better." | Condescending. | Just show it. |

### What good writing looks like (real examples from our KB)

**Good opening paragraph** (from access-control-models.md):

> Authentication proves who you are. Authorization decides what you can do. Delegation gives someone else limited authority to act as you. Getting these confused causes our most common security architecture mistakes.

Three sentences. Each one develops the idea. No preamble, no hedging, no filler.

**Good concrete example** (from esc-pos-thermal-printer.md):

> The pixel data must be packed as described in [[dithering-and-rasterization]]. The entire command — header + pixel data — must be sent as one continuous stream. This is the timing constraint that causes most failures.

Names the specific constraint, cross-references the preparation step, and states the consequence.

**Good gotcha** (from keycloak-oauth-in-go-services.md):

> A JWT issued for `byok-host` should not be accepted by `wish-git`. Each service validates `aud` against its own client ID. Without this check, a token issued for one service is valid for all services in the realm — a subtle privilege escalation.

Names the specific attack, the specific field, and the specific consequence.

### The most important section in every entry

**The "Common mistakes" / "The gotchas we've hit" / "What goes wrong" section.** This is what makes our KB different from every other technical reference on the internet. A Wikipedia article tells you what a concept is. Our KB tells you what happens when you get it wrong — because we got it wrong, and we're telling you so you don't have to.

Every entry must have this section. Every item in it must reference a real project and a real failure. If you can't name a specific project and a specific bug, you don't have a gotcha — you have a theoretical concern, and it belongs in a different section.

### Cross-referencing conventions

Cross-references use Obsidian `[[wikilink]]` syntax with the section path:

- From On-Ramp to Fundamental: `[[Fundamentals/signal-quantization-and-sampling]]`
- From On-Ramp to Tribal: `[[Tribal/goja-embedding-in-go]]`
- From Fundamental to On-Ramp: `[[On-Ramp/dithering-and-rasterization]]`

Use the filename without the `.md` extension. Do NOT use the title — use the kebab-case filename. This ensures links work even if titles change.

Cross-references should be **bidirectional**: if the dithering On-Ramp entry points to signal-quantization Fundamental, the signal-quantization entry should list dithering in its `## Where we use it` section. This creates a navigable graph, not a one-way street.

---

## Step 1: Read the project report

Read the full project report. As you read, list every technical concept the report depends on. Include both the explicit ones (named technologies) and the implicit ones (theoretical foundations the report assumes you know).

### What to extract

For each concept, record:

1. **Name**: What the concept is called (use the most common name, not a project-specific alias)
2. **Category**: Is this a technology we use, a pattern we follow, or a theory we depend on?
3. **Role in the project**: Why does this project need this concept? What breaks if you don't understand it?
4. **Tribal or lookupable**: Could you learn this from public docs, or is it our-specific knowledge?
5. **On-ramp angle**: If lookupable, what's missing from public docs that our projects reveal? (e.g., "ESP-IDF docs describe esp_console API, but don't show the working USB Serial/JTAG bring-up sequence")

### On-ramp extraction is not optional

A common failure mode is to extract tribal candidates eagerly and on-ramp candidates reluctantly (or not at all). This produces a KB that knows how we do things but can't help someone read our project reports.

**The test**: after analyzing each project, ask yourself:

> "If a newcomer read this project report, what would they need to Google first?"

Every answer to that question is an on-ramp candidate. The public docs for that concept probably exist, but they're either scattered (ESC/POS across 300 pages of Epson docs), wrong for our context (ESP-IDF UART docs that don't cover USB Serial/JTAG), or missing our specific angle (Keycloak docs are Java-centric, our patterns are Go-centric).

**You should produce roughly as many on-ramp candidates as tribal candidates per batch.** If you're not, you're under-extracting on-ramp material. Go back through the project and ask the newcomer question again.

### Example: Reading the SToMS3R project report

| Concept | Category | Role | Tribal? |
|---------|----------|------|---------|
| ESC/POS command set | Technology | The printer communication protocol | No — Epson docs exist, but they're 300 pages and scattered |
| Floyd-Steinberg dithering | Technology | Converting grayscale to 1-bit | No — Wikipedia covers it, but not for thermal printing |
| UART with CTS flow control | Pattern | Streaming bitmap data without gaps | Yes — our "buffer full body before UART" pattern is ours |
| Thermal paper dot gain | Theory | Why images print darker than expected | No — physics, but not documented for this specific printer |
| Signal quantization | Theory | Why dithering works at all | No — textbook signal processing |
| MSB-first bit packing | Pattern | Packing 1-bit pixels for the printer | Yes — our specific convention, easy to get wrong |
| BT.601 luminance weights | Technology | Converting color to grayscale | No — ITU standard, but our specific formula isn't in one place |

---

## Step 2: Classify each concept

Apply the decision rules to place each concept in the right section — or leave it in the project report.

### Decision rule: Where does this concept go?

```
Is it our-specific knowledge (how WE do it)?
  YES → Is it used in 3+ projects?
    YES → TRIBAL entry. Create it now.
    NO  → Note in project index: "Tribal candidate. Seen in [list]. Triggers at 3."
  
  NO → Is it lookupable (you can Google it)?
    YES → Is it used in 5+ projects?
      YES → ON-RAMP entry. Create it now.
      NO  → Note in project index: "On-ramp candidate. Seen in [list]. Triggers at 5."
    
    NO → Does it underlie 2+ Tribal or On-Ramp entries?
      YES → FUNDAMENTALS entry. Create it now.
      NO  → Leave in the project report. Not yet a KB concept.
```

### Why the thresholds are different

- **Tribal at 3**: Our patterns are rare and high-value. If three projects independently arrive at the same approach, it's worth documenting before the fourth person rediscovers it.
- **On-Ramp at 5**: Lookupable concepts are, by definition, findable elsewhere. We only create an entry when the curation effort is justified by the frequency.
- **Fundamentals at 2+ KB entries**: A theory concept enters the KB when it's the "why" behind multiple practical entries. It doesn't need its own project count — it needs to be load-bearing for other KB entries.

### Classification edge cases

**When the tribal/lookupable boundary is ambiguous.** Some concepts are partially lookupable but have a strong our-specific angle (e.g., "Arduino-cli cross-compilation" — the CLI is documented, but our headless no-IDE workflow is ours). When in doubt, **default to on-ramp candidate**. The higher threshold (5 vs 3) means fewer premature entries, and you can always reclassify later if more projects reveal a tribal pattern.

**When concepts share a core insight but differ in mechanism.** Agent Enroll uses Ed25519 request signing. Wish Git uses SSH certificates. BYOK Host uses broker OAuth tokens. All three share the insight: "Keycloak authenticates humans; the Go application owns agent authorization." **Count projects that share the core insight, even if the specific mechanism differs.** Document the mechanism differences as variations in the tribal entry.

**Variation of existing entry vs new candidate.** ZK Tool's `require("obsidian")` module follows the goja-embedding pattern but with a domain-specific native module. Is this a new tribal candidate (2/3) or just a variation? The rule: **if the concept follows an existing entry's structure and only differs in the domain-specific surface, add it as a variation to the existing entry. Only create a new candidate if the code structure and gotchas are structurally different.** A native module registration pattern that reuses the same `modules.Register()` call and the same `require()` bridge is a variation, not a new entry.

### Examples of classification

| Concept | Classification | Why |
|---------|---------------|-----|
| How we embed goja in Go | Tribal | Our pattern, can't Google it, used in 52 projects |
| OAuth 2.0 + PKCE | On-Ramp | Lookupable (RFC 7636), but our angle (CLI flow, Keycloak wiring) is missing from public docs, 29 projects |
| Signal quantization theory | Fundamental | Underlies both the dithering On-Ramp entry and the ESC/POS On-Ramp entry |
| What is a stack-based VM | On-Ramp | Lookupable, 45 projects need it to read Smalltalk/interpreter reports |
| BT.601 luminance formula | On-Ramp candidate | Only 3 projects right now, not yet at 5 |
| How we do MSB-first bit packing | Tribal | Our convention, easy to get wrong, 2 projects so far (candidate) |

---

## Step 3: Write the entry (if it's ready)

Each section has its own template. **Follow the template exactly.** Consistency is what makes the KB reliable for someone who doesn't know which entry they're about to read.

**Before writing a new entry, read 2–3 existing entries to calibrate your tone and depth.** The completed entries (listed at the bottom of this playbook) serve as the quality reference.

### Tribal entry template

```markdown
---
title: "[Concept] — How We Do It"
aliases: [common alternative names, lowercase-with-dashes]
tags: [knowledge-base, tribal, relevant-tech-tags]
status: active
type: knowledge-base
created: YYYY-MM-DD
---

# [Concept] — How We Do It

> [!summary]
> One sentence: what this entry documents and why it matters.

## The pattern

What our standard approach looks like. Concrete and implementable —
not vague principles. Include code snippets, file paths, or command
examples where applicable. A new person should be able to follow this
section and produce working code.

## Why we do it this way

The tradeoffs we considered. What alternatives exist. Why we rejected
them or keep them as fallbacks. This section prevents future-us from
re-litigating the decision without new information.

## Where it lives

Which repos, packages, or directories implement this pattern today.
List actual file paths, not just repo names. This is the "go look at
the real code" section.

## Common mistakes

What goes wrong when someone tries to wing it. Be specific — include
actual error messages, wrong assumptions, or subtle bugs. This is the
section that saves the next person a day of debugging.

## Variations

When and why we deviate from the standard pattern. If a project has
a good reason to do it differently, document that reason here so the
variation doesn't get "fixed" by someone who only read The Pattern.
```

**Length target**: roughly 4–7 KB for most Tribal entries, with 7–10 KB acceptable when the entry needs real project variation, concrete gotchas, or code/path examples. Treat this as a writing target, not a hard rule. If an entry pushes past the target, pause and ask whether the concept should be split, whether examples can be tightened, or whether the extra length is justified by scar tissue the reader needs.

### On-Ramp entry template

```markdown
---
title: "[Concept]"
aliases: [common alternative names, lowercase-with-dashes]
tags: [knowledge-base, on-ramp, relevant-tech-tags]
status: active
type: knowledge-base
created: YYYY-MM-DD
---

# [Concept]

> [!summary]
> One sentence: what this concept is and which of our projects use it.

## The idea in one paragraph

2–4 sentences that develop the core idea. Write complete paragraphs
that develop a thought — not short declarative sentences that feel
like bullet points in disguise. The reader should finish this
paragraph and think "I understand what this is."

## Why we care

Which of our projects use it. What breaks if you don't understand
it. The specific angle we care about — not the general-purpose
angle a textbook gives. This section answers "why should I spend
10 minutes on this."

## The [N] things to understand

Instead of a single "mental model" section, break the concept into
2–5 numbered subsections, each developing one key insight. Use
concrete examples, code snippets, or step-by-step walkthroughs.
Each subsection should be a paragraph that advances understanding,
not a bullet list of facts.

For multi-step protocols (OAuth, SSH certificates), number the
steps and show the data flow. For theoretical concepts (CRDTs),
use analogies and worked examples. For command references
(ESC/POS), use tables.

## The gotchas we've hit

Concrete mistakes from our projects. Name the project and the
specific failure. This section is what separates our On-Ramp from
a Wikipedia article — the scar tissue.

## Where to go deeper

2–5 curated links, in priority order:
1. The definitive reference (RFC, spec, standard, textbook chapter)
2. The best practical guide (blog post, tutorial, talk)
3. Our own project report that serves as a deep-dive example
4. (Optional) A related Tribal or Fundamental KB entry

Do NOT include more than 5 links. The point is curation, not
completeness.
```

**Length target**: roughly 5–7 KB for most On-Ramp entries, with 7–10 KB acceptable for protocols or concepts that need step-by-step flows, diagrams/tables, and concrete gotchas. Treat the target as a readability signal, not an enforcement rule. If the draft grows beyond the target, review whether the concept is doing too much or whether the extra explanation is genuinely helping a newcomer get unstuck.

### Fundamental entry template

```markdown
---
title: "[Theory Concept]"
aliases: [common alternative names, lowercase-with-dashes]
tags: [knowledge-base, fundamental, relevant-theory-tags]
status: active
type: knowledge-base
created: YYYY-MM-DD
---

# [Theory Concept]

> [!summary]
> One sentence: what theory this covers and which of our KB entries
it underpins.

## The core idea

2–3 sentences. The one-sentence version of the textbook chapter.
No math yet — just the intuition. If you can explain it with an
analogy, do that here.

## Why it matters to our work

Which of our Tribal and On-Ramp entries depend on this theory.
What mistakes we keep making because people don't know the theory.
This is NOT a general "why this theory is important" section —
it's "why WE need this theory in OUR library."

## The key result

The one theorem, equation, or principle from this theory that
actually affects our implementations. State it precisely, then
explain what it means in plain language. If the theory has multiple
important results, pick the ONE that our projects get wrong most
often. The rest goes in "Where to go deeper."

## The intuition behind the key result

A worked example or thought experiment that shows WHY the key
result is true, without requiring the reader to follow a formal
proof. The goal is: after reading this section, the key result
feels obvious, not surprising.

## What goes wrong when you don't know this

Concrete examples from our projects where misunderstanding this
theory caused bugs, bad designs, or wasted time. Name the project
and the specific mistake. This section is what makes a fundamental
entry different from a textbook — the textbook gives you the
theory, we give you the scar tissue.

## Where we use it

Which Tribal and On-Ramp entries this foundational concept supports.
Format: `[[Section/filename-without-ext]]` using Obsidian wikilinks.
Example: `[[Fundamentals/signal-quantization-and-sampling]]`.

## Where to go deeper

1–3 references. The textbook chapter, the original paper, or the
definitive survey. Not 20 references — the 1–3 that a motivated
reader should actually read.
```

**Length target**: roughly 6–10 KB for Fundamentals. Theory sometimes needs more space than a Tribal or On-Ramp entry because it must state the principle, show intuition, and connect several concrete project failures. The target is not a hard limit; if the entry grows beyond it, use that as a prompt to check whether it is becoming a textbook chapter or whether it is legitimately serving multiple KB entries.

---

## Step 4: Cross-reference

After creating or updating a KB entry, add cross-references in both directions:

1. **From the project report to the KB**: Add a `## Related KB entries` section at the bottom of the project report listing the relevant Tribal, On-Ramp, and Fundamental entries. Use `[[Section/filename]]` format. Also list tribal candidates with their current count.

2. **From the KB entry to the project report**: Add a `### Related PARC project reports` subsection with `[[PROJ - Full Project Name]]` wikilinks and one-line annotations.

3. **Between KB entries**: Use `[[Section/filename]]` wikilinks. If a Tribal entry depends on an On-Ramp or Fundamental entry, mention it in `## Why we do it this way` or `## Common mistakes`. If a Fundamental entry supports an On-Ramp, list it in `## Where we use it`.

**Should you actually modify the files, or just document the changes?** For your first pass through a project, document the cross-references that should be added in your intern report. For a second pass (or if you have implementation experience with the project), actually modify the PARC project reports and KB entries. Cross-referencing is the most time-consuming step — consider batching it across multiple projects before doing the file edits.

4. **From the project report to review logs**: Add a `## KB reviews` section linking to any analysis logs that have examined this project's concepts. This prevents re-analyzing the same project in the future.

These cross-references are what make the KB a *web* rather than a pile of documents. Every link should be bidirectional: if entry A links to entry B, entry B should link back to entry A.

### Linking between KB entries and PARC project reports

Every KB entry must link to the specific PARC project reports that use the concept. Every project report must link to the KB entries that orient its concepts. This creates a fully traceable graph: you can start from a project report, jump to the KB entry that explains a concept, and jump back to the project report that demonstrates it.

**From KB → project reports**: Add a `### Related PARC project reports` subsection under `## Where it lives` (Tribal) or at the end of `## Where to go deeper` (On-Ramp/Fundamentals). Use `[[PROJ - Full Project Name]]` wikilinks. Include a one-line annotation per link explaining what the project demonstrates about this concept.

**From project reports → KB**: Add a `## Related KB entries` section at the end of the project report. List every KB entry the project depends on, using `[[Section/filename]]` format. Also list tribal candidates that were extracted from this project but haven't yet reached the 3-project threshold — this is how the candidate tracking list gets maintained in place.

Example from a project report:
```markdown
## KB reviews

- [[KB-PLAYBOOK-TRIAL - Intern Reports for 6 Projects]] (2026-05-11) — concept extraction + classification; microVM boundary at 2/3, host-mediated secrets at 2/3

## Related KB entries

- [[Tribal/esp-idf-firmware-patterns]] — the esp_console + web UI architecture
- [[On-Ramp/esc-pos-thermal-printer]] — the GS v 0 command and timing constraint
- [[Fundamentals/signal-quantization-and-sampling]] — why dithering works

**Tribal candidates** (not yet at 3-project threshold):
- Buffer-full-body-before-UART (2/3) — read entire body before sending to printer
- MSB-first bit packing (2/3) — our specific 0x80 >> convention
```

### KB reviews: tracking what has been analyzed

When you analyze a project report (or a batch of reports) through Steps 1–5, you produce a review document. That review needs to be:

1. **Stored in the Logs directory** under `Logs/YYYY/MM/DD/`, so all reviews are in one place and date-ordered.
2. **Linked from the project report** via a `## KB reviews` section, so anyone opening the project report knows it has already been analyzed and what was found.

The `## KB reviews` section goes **before** `## Related KB entries` in the project report. It should be concise — just the wikilink, date, and a one-line summary of what the review found (especially which candidates changed count).

This serves two purposes:
- **Avoid duplicate work**: Future analysts can see which projects have already been processed and skip them (or update the existing review).
- **Audit trail**: The review links make it possible to trace from a candidate count change back to the analysis that caused it.

### The Logs directory

Review documents and analysis logs live in `Logs/YYYY/MM/DD/`, mirroring the date-based structure used in `Projects/`.

```
go-go-parc/
  Logs/
    2026/
      05/
        11/
          KB-PLAYBOOK-TRIAL - Intern Reports for 6 Projects.md
```

To add a log:

```bash
cp your-review.md \
  go-go-parc/Logs/2026/05/11/descriptive-title.md
```

Logs are not tickets and they are not KB entries. They are the working documents produced by analysts as they process project reports. They capture concept extraction tables, classification decisions, candidate counts, and playbook feedback. They are the evidence behind the KB's growth.

---

## Step 5: Update the project index

Add the project to the canonical project index document at `Projects/00-project-index-repos-and-concepts.md`. This file is the running ledger of all analyzed projects and their extracted concepts. Read the existing entries to understand the format before adding yours.

### What to add for each project

Follow the format of existing entries in the index. Each project section contains:

1. **Project name and date** — as a `###` heading
2. **Summary** — 2–3 sentences from the project report
3. **Repos** — table of repo paths with notes
4. **Tribal candidates** — bulleted list of our-specific patterns, even if only this project uses them. Include a brief description of each candidate.
5. **On-Ramp candidates** — bulleted list of lookupable concepts where our angle is missing from public docs. For each one, state what's missing (e.g., "ESP-IDF docs describe esp_console API, but not the USB Serial/JTAG bring-up sequence for ESP32-S3"). **This is not optional.** Every project that depends on a technology with sparse or misleading public docs should produce at least one on-ramp candidate.
6. **Fundamental concepts this project rests on** — bulleted list of theory concepts

### What to update in the candidate tracking tables

The file also contains running candidate tracking tables at the bottom. For each concept you extracted:

- If a KB entry already exists: add a cross-reference.
- If it's a candidate (not yet at threshold): add it to the candidate list with the running count. Check whether it's already listed — if so, increment the count.
- If it just triggered (reached threshold): note that a new KB entry was created and remove it from the candidate list.
- If a project opens a new technology domain with zero KB coverage: add a `🌐 Domain seed` flag.

### Don't create a separate index file

The canonical index is at `Projects/00-project-index-repos-and-concepts.md`. Do not create a separate index in your ticket workspace or intern report. If you need a working copy, edit the canonical file directly.

---

## The candidate tracking list

Maintain a running list of concepts that have been seen in project reports but haven't yet reached their threshold. This is how the KB grows organically rather than all at once.

### Format

```markdown
## KB Candidate Concepts

### Tribal candidates (trigger at 3 projects)

| Concept | Seen in | Status |
|---------|---------|--------|
| MSB-first bit packing | SToMS3R, Almanach | 2/3 — needs 1 more |
| Browser-side image processing | SToMS3R, Capsule Lab | 2/3 — needs 1 more |

### On-Ramp candidates (trigger at 5 projects)

| Concept | Seen in | Status |
|---------|---------|--------|
| BT.601 luminance conversion | SToMS3R, Almanach, Codebase Browser | 3/5 — needs 2 more |
| GoReleaser multi-platform builds | Glazed, Sqleton, go-minitrace | 3/5 — needs 2 more |

### Fundamental candidates (trigger when supporting 2+ KB entries)

| Concept | Supports | Status |
|---------|----------|--------|
| Sampling theory | Dithering On-Ramp, ESC/POS On-Ramp | 2/2 — ready to create |
| Access control models | Keycloak On-Ramp, SSH Certs On-Ramp | 2/2 — ready to create |
```

When a concept reaches its threshold, create the entry and remove it from the candidate list.

### Domain seeds: projects that open new technology domains

Some projects introduce technology domains that currently have zero KB coverage. Screencast Studio opens the media/GStreamer domain. These projects are hard to read because there are no existing on-ramp entries to anchor on.

The playbook's rule is "don't create entries preemptively." But a domain with zero coverage creates a cold-start problem: the project report is unreadable without orientation that doesn't exist yet.

**Domain seed flag**: When a project introduces a new technology domain with zero existing KB entries, add a `🌐 Domain seed` flag in the candidate tracking list. This signals to a human reviewer that a judgment call is needed: should we create an initial cluster of entries for this domain, or let it grow organically as more projects arrive?

```markdown
### On-Ramp candidates (trigger at 5 projects)

| Concept | Seen in | Status |
|---------|---------|--------|
| GStreamer for Go programmers | Screencast Studio | 2/5 🌐 Domain seed |
| Arduino-cli cross-compilation | uLisp PicoCalc | 2/5 🌐 Domain seed |
```

Don't automatically create entries for domain seeds. Flag them and let a reviewer decide.

---

## Quality checklist

Before submitting a KB entry, verify:

- [ ] **Correct section**: Tribal, On-Ramp, or Fundamental — not mixed
- [ ] **Template followed**: All required sections present, in order
- [ ] **Length reviewed as a target, not a rule**: Tribal usually 4–7 KB, On-Ramp usually 5–7 KB, Fundamentals usually 6–10 KB; longer entries are acceptable when the extra length carries necessary examples, gotchas, or project variation
- [ ] **Writing style**: No AI slop (see anti-pattern table above). Prose develops ideas. Concrete over abstract.
- [ ] **Gotchas section present**: Every entry has real project failures, not theoretical concerns
- [ ] **On-ramp candidates balanced with tribal candidates**: roughly equal counts per batch; if not, re-read the project with the newcomer question
- [ ] **No textbook rewriting**: On-Ramp entries link to external sources; they do not reproduce them
- [ ] **Our angle present**: Every entry explains why WE care, not just what the concept is
- [ ] **Cross-references bidirectional**: `## Where we use it` lists real KB entries; those entries link back
- [ ] **Project report links added**: KB entry has `### Related PARC project reports` with wikilinks to specific PROJ files
- [ ] **Project report updated**: Project report has `## Related KB entries` section linking back to all relevant KB entries
- [ ] **Tribal candidates listed**: Project report's `## Related KB entries` includes tribal candidates with counts (e.g., 2/3)
- [ ] **KB reviews linked**: Project report has `## KB reviews` section linking to the analysis log, so future analysts know it has been processed
- [ ] **Review log stored**: Analysis document is copied into `Logs/YYYY/MM/DD/` with a descriptive filename
- [ ] **Cross-references use filenames**: `[[Section/kebab-case-name]]`, not titles
- [ ] **Scar tissue included**: Tribal and Fundamental entries include real mistakes from real projects
- [ ] **Go-deeper list is curated**: No more than 5 links (On-Ramp) or 3 references (Fundamental)
- [ ] **Frontmatter complete**: title, aliases, tags (including `knowledge-base` and section tag), status, type, created date

---

## Anti-patterns

### Writing a textbook chapter

**Bad**: A 10-page entry on "Digital Signal Processing" that covers Fourier transforms, Z-transforms, filter design, and sampling theory.

**Good**: A 1-page On-Ramp entry on "Signal Quantization" that says: "When you reduce 256 gray levels to 2, you lose information. Dithering is the deliberate addition of noise to make that loss less visible. The key result is that properly dithered quantization converts amplitude error into high-frequency noise, which the eye barely sees. Our dithering report (DITHER-001) covers this in depth for thermal printing."

### Documenting something you just learned

If you're writing an entry about something you learned while reading the project report, you're probably the wrong person to write it. The entry should be written by (or reviewed by) someone who has implemented this concept in at least two projects. The scar-tissue sections require real scars.

> [!important] **On-Ramp exception**: You CAN write the first draft of an On-Ramp entry from fresh knowledge. On-ramp entries are precisely the ones that make project reports readable, and they're the ones newcomers encounter first. Write the draft, flag the `The gotchas we've hit` and `Why we care` sections as **needs review by someone with implementation experience**, and submit it. A reviewer with real scars will fill in what you can't.

**For Tribal and Fundamental entries**: Don't write them from fresh knowledge. Draft a skeleton (title, summary, "Where it lives" table) and hand it to someone who has built this pattern in at least two projects.

### Mixing tribal and on-ramp in one entry

**Bad**: "OAuth 2.0 with Keycloak — How It Works and How We Do It"

**Good**: Two entries:
- On-Ramp: "OAuth 2.0 and OIDC — The Flows That Matter" (what it is, why we care)
- Tribal: "Keycloak OAuth in Go Services — How We Do It" (our pattern, our code, our mistakes)

The On-Ramp entry is what you read before the project report. The Tribal entry is what you read before you write code. They serve different readers at different moments.

### Creating entries preemptively

**Bad**: Writing 30 KB entries upfront because "we'll need them."

**Good**: Let the project reports drive the KB. Read reports, extract concepts, track candidates, create entries at threshold. This ensures every entry has real demand and real examples behind it.

### Listing 20 "go deeper" links

**Bad**: A references section with 20 URLs.

**Good**: 3–5 curated links. The first is the definitive reference. The second is the best practical guide. The third is our own deep-dive. If you're tempted to add more, ask: "if someone only reads ONE link, which one should it be?" Put that one first. The rest are optional.

---

## Worked example: SToMS3R → KB entries

Here's the full workflow applied to one project report.

### Step 1: Extract concepts from the SToMS3R report

| Concept | Category | Tribal? |
|---------|----------|---------|
| ESC/POS command set | Technology | No (Epson docs exist but are 300 pages) |
| Floyd-Steinberg dithering | Technology | No (Wikipedia exists but misses thermal) |
| UART with CTS flow control | Pattern | Partially — our "buffer full body" pattern is ours |
| Thermal paper dot gain | Theory | No (physics, not documented for this printer) |
| MSB-first bit packing | Pattern | Yes (our convention) |
| BT.601 luminance weights | Technology | No (ITU standard) |
| Signal quantization | Theory | No (textbook) |

### Step 2: Classify

| Concept | Decision | Reason |
|---------|----------|--------|
| ESC/POS command set | On-Ramp candidate (3/5) | Lookupable but our angle (the 20 commands we use) is missing |
| Floyd-Steinberg dithering | On-Ramp entry **exists** | Already covered by DITHER-001 |
| UART "buffer full body" pattern | Tribal candidate (2/3) | Our pattern, SToMS3R + Almanach; needs 1 more |
| MSB-first bit packing | Tribal candidate (2/3) | Our convention; SToMS3R + Almanach; needs 1 more |
| Signal quantization | Fundamental (3/2) | Underlies dithering, ESC/POS, e-ink On-Ramps; ready to create |

### Step 3: Write entries (for the ones that are ready)

**Signal quantization** hits the Fundamental threshold (supports 3 KB entries). Write it now.

The ESC/POS entry is at 3/5 — not yet. The tribal entries are at 2/3 — not yet. They stay on the candidate list.

### Step 4: Cross-reference

Add to the SToMS3R project report:

```markdown
## Related KB entries

- [[Fundamentals/signal-quantization-and-sampling]] — why dithering works
- [[On-Ramp/dithering-and-rasterization]] — algorithms for converting grayscale to 1-bit
- Candidate: [[Tribal/msb-first-bit-packing]] (2/3)
- Candidate: [[Tribal/uart-buffer-before-stream-pattern]] (2/3)
```

### Step 5: Update the candidate list

```markdown
### Tribal candidates (trigger at 3 projects)

| Concept | Seen in | Status |
|---------|---------|--------|
| MSB-first bit packing | SToMS3R, Almanach | 2/3 |
| UART buffer-before-stream | SToMS3R, Almanach | 2/3 |
| Browser-side image processing | SToMS3R, Capsule Lab | 2/3 |

### On-Ramp candidates (trigger at 5 projects)

| Concept | Seen in | Status |
|---------|---------|--------|
| ESC/POS thermal printer commands | SToMS3R, Almanach, ATOM-PRINTER | 3/5 |
| BT.601 luminance conversion | SToMS3R, Almanach, Codebase Browser | 3/5 |
```

---

## Completed KB entries (as of 2026-05-11)

These 18 entries are done. Do not recreate them. Use them as reference for style and depth when writing new entries.

### Tribal entries (7)

| Filename | Title | Size | Key projects |
|----------|-------|------|-------------|
| `goja-embedding-in-go.md` | goja: Embedding a JavaScript Interpreter in Go — How We Do It | 5.7 KB | Capsule Lab, Loupedeck, go-go-goja |
| `esp-idf-firmware-patterns.md` | ESP-IDF Firmware Patterns — How We Do It | 4.6 KB | Gnosis, SToMS3R, BLE Provision |
| `keycloak-oauth-in-go-services.md` | Keycloak OAuth in Go Services — How We Do It | 6.7 KB | BYOK Host, Wish Git, Pinocchio |
| `go-to-wasm-compilation.md` | Go → WASM: Compiling Go to WebAssembly — How We Do It | 6.0 KB | Capsule Lab, SQLide, JSON Flattener |
| `serial-protocols-from-go.md` | Serial Protocols: Talking to Hardware from Go — How We Do It | 6.2 KB | Loupedeck, Almanach, K118 |
| `sqlite-as-application-database.md` | SQLite as Application Database in Go — How We Do It | 6.5 KB | BYOK Host, Pinocchio, evtstream |
| `application-native-authorization.md` | Application-Native Authorization — How We Do It | 9.3 KB | BYOK Host, Wish Git, Agent Enroll |

### On-Ramp entries (8)

| Filename | Title | Size | Key projects |
|----------|-------|------|-------------|
| `crdts-and-local-first.md` | CRDTs and Local-First Architecture | 5.4 KB | AUTODISCO |
| `oauth-2-oidc-flows.md` | OAuth 2.0 and OIDC — The Flows That Matter | 5.4 KB | BYOK Host, Wish Git |
| `openssh-certificates.md` | OpenSSH User Certificates | 5.8 KB | Wish Git |
| `dithering-and-rasterization.md` | 1-Bit Image Dithering and Rasterization | 6.2 KB | SToMS3R, Almanach |
| `esc-pos-thermal-printer.md` | ESC/POS Thermal Printer Commands | 5.1 KB | SToMS3R, Almanach |
| `e-ink-display-driving.md` | E-Ink Display Driving | 6.3 KB | Gnosis, PaperS3 |
| `git-hooks-for-policy-enforcement.md` | Git Hooks for Policy Enforcement | 5.8 KB | Wish Git |
| `wasm-from-go.md` | WebAssembly from Go | 6.2 KB | Capsule Lab, SQLide |

### Fundamental entries (4)

| Filename | Title | Size | Supports |
|----------|-------|------|----------|
| `signal-quantization-and-sampling.md` | Signal Quantization and Sampling Theory | 6.9 KB | Dithering, ESC/POS, E-ink On-Ramps |
| `access-control-models.md` | Access Control Models: Authn, Authz, Delegation | 6.2 KB | Keycloak Tribal, OAuth/SSH On-Ramps |
| `encoding-and-framing.md` | Encoding and Framing: Turning Bytes into Messages | 6.0 KB | ESC/POS On-Ramp, Serial Tribal |
| `rendering-pipeline-fundamentals.md` | Rendering Pipeline Fundamentals | 5.6 KB | E-ink On-Ramp, ESP-IDF Tribal |

### Not yet created (still candidates)

| Concept | Section | Status |
|---------|---------|-------|
| Distributed Consistency (CAP, eventual consistency) | Fundamental | 1/2 KB entries — needs 1 more (e.g., a collaborative-editing On-Ramp) |

---

## Current directory structure

```
go-go-parc/
  Research/
    KB/
      Tribal/
        goja-embedding-in-go.md
        esp-idf-firmware-patterns.md
        keycloak-oauth-in-go-services.md
        go-to-wasm-compilation.md
        serial-protocols-from-go.md
        sqlite-as-application-database.md
        application-native-authorization.md
      On-Ramp/
        crdts-and-local-first.md
        oauth-2-oidc-flows.md
        openssh-certificates.md
        dithering-and-rasterization.md
        esc-pos-thermal-printer.md
        e-ink-display-driving.md
        git-hooks-for-policy-enforcement.md
        wasm-from-go.md
      Fundamentals/
        signal-quantization-and-sampling.md
        access-control-models.md
        encoding-and-framing.md
        rendering-pipeline-fundamentals.md
    Institute/           (existing)
    playbooks/           (existing — this playbook)
  Projects/             (existing — 304 project reports)
  Logs/                 (analysis reviews, date-structured)
    YYYY/MM/DD/         (one directory per work day)
  Attachments/          (existing)
```

---

## Growing the KB: next steps

The initial 18 entries cover the concepts identified from Batch 1 (8 projects). To grow the KB:

1. **Continue project analysis batches 2–7** — Process the remaining ~296 project reports in thematic batches (infrastructure, go-go-goja, Glazed ecosystem, embedded, agent/AI, media). Each batch updates the candidate tracking list.

2. **Check candidate counts before writing** — A concept at 2/3 Tribal or 4/5 On-Ramp is close. One more project report that uses it triggers creation.

3. **Write in textbook style** — Follow the writing rules in this playbook. Read 2–3 existing entries before writing a new one to calibrate your tone and depth.

4. **Cross-reference bidirectionally** — Every new entry must link to related entries, and those entries must link back.

5. **Store review logs and crosslink project reports** — Copy each analysis document into `Logs/YYYY/MM/DD/`. Add a `## KB reviews` section to every project report you analyzed, linking to the review log with a one-line summary of what was found. This prevents future analysts from re-analyzing the same project.

6. **Upload completed entries to reMarkable** — Bundle the full KB and upload so the team can read offline.
