---
title: "Building a Knowledge Base Playbook: From 304 Project Reports to 18 Entries"
aliases:
  - KB Playbook Deep Dive
  - PARC Knowledge Base Workflow
  - Project Analysis Playbook
tags:
  - article
  - knowledge-base
  - playbook
  - parc
  - go-go-golems
  - obsidian
  - workflow
status: active
type: article
created: 2026-05-11
---

# Building a Knowledge Base Playbook: From 304 Project Reports to 18 Entries

This article is the story of how we turned 304 project reports — the accumulated working notes of a small team of research scientists building software — into a navigable knowledge base with consistent entries, cross-references, and a repeatable workflow. It covers the design decisions we made, the mistakes we caught, and the playbook we wrote so that anyone on the team (human or agent) can produce entries of the same quality.

The goal is not to sell you on our specific three-section taxonomy or our trigger rules. The goal is to show you the reasoning behind each choice, so you can adapt the approach to your own library. If you understand *why* we set the tribal threshold at three projects and the on-ramp threshold at five, you can set your own thresholds with confidence. If you understand *why* we separate "how we do it" from "what it is," you can decide whether your library needs the same split.

---

## The Problem: 304 Reports and No Way In

Our team has been writing project reports for two years. Each report captures what we built, what we learned, and what went wrong. They live in an Obsidian vault under `Projects/2026/`, organized by date. Some are 6 KB — a quick capture of a tool experiment. Others are 50 KB — a full architectural deep dive with code samples and debugging traces.

The library is a treasure chest. It is also impenetrable.

When you open a project report about a thermal printer firmware, you encounter ESC/POS commands, UART flow control, MSB-first bit packing, Floyd-Steinberg dithering, signal quantization theory, and gamma correction for dot gain. Each of these concepts is a rabbit hole. Some of them are well-documented elsewhere (Floyd-Steinberg dithering has a Wikipedia page). Some of them are ours — the specific way we pack bits for the K118 printer, the specific way we buffer the full HTTP body before writing to UART — and nobody else documents them.

The result: a new team member (or a new agent) opens a project report, hits an unfamiliar concept, stops, Googles it, reads a 300-page Epson specification, comes back confused, and gives up. The report is accurate, but it's not *readable* — you need domain knowledge that isn't in the report itself.

That's the problem a knowledge base solves. A KB entry is the ten-minute orientation you read *before* the project report, so the report itself makes sense.

---

## The Three-Section Design: Why Three, Not One

Our first instinct was a flat wiki: one directory, one type of entry, alphabetical order. This is the simplest design, and it's wrong.

The problem with a flat wiki is that "how we embed a JavaScript interpreter in Go" and "what OAuth 2.0 is" are fundamentally different kinds of knowledge. The first is *tribal* — it's our specific pattern, you can't Google it, and if we don't document it, nobody will. The second is *lookupable* — RFC 6749 exists, tutorials exist, but our angle (which flows we actually use, how we wire Keycloak, what goes wrong when you skip audience validation) is scattered across a dozen sources and missing from any single one.

If you put both in the same section, the reader doesn't know what they're getting. Is this an explanation of a public standard, or is this our internal convention? The distinction matters because it determines how you read the entry. A tribal entry is something you follow when implementing. An on-ramp entry is something you skim before reading a project report. A reader who confuses the two will either over-trust a tribal entry (treating our convention as a universal standard) or under-trust an on-ramp entry (treating a public standard as our invention).

The third section — Fundamentals — emerged later, and it emerged from a specific failure. We kept writing on-ramp entries that needed to explain *why* dithering works, *why* framing matters, *why* access control separates authentication from authorization. These explanations were too deep for an on-ramp (which should be ten minutes) but too important to leave out (without them, the on-ramp becomes a shallow list of facts). The solution: give the theory its own section. A Fundamental entry is the textbook chapter you actually need, distilled to the one key result that affects our implementations.

The three sections serve different readers at different moments:

| Section | Who reads it | When | What they need |
|---------|-------------|------|---------------|
| **Tribal** | Implementer | Before writing code | Our standard approach, our gotchas, where the code lives |
| **On-Ramp** | Newcomer | Before reading a project report | What the concept is, why we care, the key mental model |
| **Fundamental** | Designer / debugger | When the surface explanation isn't enough | The theory behind the practice, the key result, what goes wrong without it |

---

## The Trigger Rules: Why Three and Five, Not One and Ten

A knowledge base with no growth constraints becomes a dumping ground. Every concept gets an entry, most entries are stubs, and the reader learns to ignore the KB because most of it isn't useful. A knowledge base with too-tight constraints never grows — nothing seems important enough to document, and the team reinvents the same patterns in silence.

The trigger rules are the compromise between these failures. The idea is simple: a concept doesn't get a KB entry until enough projects have shown they need it. The question is: what's "enough"?

For tribal entries, the answer is **three projects**. Three is low enough that we catch patterns early — before the fourth person rediscovers them — but high enough that one-off experiments don't become entries. If three projects independently arrive at the same approach, it's not a coincidence. It's a pattern worth naming.

For on-ramp entries, the answer is **five projects**. The higher threshold is deliberate. On-ramp concepts are, by definition, findable elsewhere. We only create an entry when the curation effort is justified by the frequency — when five projects need the same orientation, it's worth writing it once. Below five, a reader can Google the concept and find adequate explanations.

For fundamentals, the threshold is different: **two or more KB entries that the theory supports**. A fundamental entry doesn't need its own project count — it needs to be load-bearing for other entries. Signal quantization theory enters the KB not because three projects use it directly, but because it underlies the dithering on-ramp entry, the ESC/POS on-ramp entry, and the e-ink on-ramp entry. Without it, those entries have to re-explain the same theory in three different ways.

Why these specific numbers? They're calibrated to our library's density (304 projects, 18 distinct technology clusters). If your library has 30 projects, use lower thresholds (tribal at 2, on-ramp at 3). If it has 3,000 projects, use higher ones (tribal at 5, on-ramp at 10). The principle is: the threshold should be high enough to filter noise, low enough to catch signal before it's rediscovered.

---

## The Candidate Tracking List: Growing the KB Organically

The trigger rules create a natural question: what about the concepts that are at 2/3 or 4/5? They haven't triggered yet, but they're close. If you don't track them, the next analyst has to start from zero — re-reading the same projects, re-discovering the same candidates, and not knowing that the concept is almost ready.

The candidate tracking list is the ledger that makes the KB grow incrementally. Every time you analyze a project report, you extract concepts and add them to the list with their current count. When a concept hits its threshold, you create the entry and remove it from the list.

Here's what our tracking list looks like after eight projects:

```markdown
### Tribal candidates (trigger at 3 projects)

| Concept | Seen in | Status |
|---------|---------|--------|
| Buffer-full-body-before-UART | SToMS3R, Almanach | 2/3 |
| MSB-first bit packing for ESC/POS | SToMS3R, Almanach | 2/3 |
| goja native module registration | goja-embedding, ZK Tool, Loupedeck | 2/3 |
| SQL as first-class command source | Sqleton, Minitrace Query | 2/3 |

### On-Ramp candidates (trigger at 5 projects)

| Concept | Seen in | Status |
|---------|---------|--------|
| ESC/POS thermal printer commands | SToMS3R, Almanach, ATOM-PRINTER | 3/5 |
| GStreamer for Go programmers | Screencast Studio | 2/5 🌐 Domain seed |
```

The `🌐 Domain seed` flag is worth explaining. It marks a concept that opens a *new technology domain* with zero existing KB coverage. Screencast Studio introduces GStreamer — our library has no media entries at all. The project report is effectively unreadable without orientation that doesn't exist yet. The domain seed flag doesn't override the trigger rules; it signals to a human reviewer that a judgment call is needed: should we bootstrap a cluster of entries for this domain, or let it grow organically?

The domain seed concept came from an intern trial. We assigned six projects to an agent and asked it to follow the playbook. When it hit Screencast Studio, it correctly identified that the project report needs GStreamer orientation that doesn't exist. It also correctly followed the "don't create entries preemptively" anti-pattern and didn't write the entry. The result: a correct application of the rules, and a project report that's still unreadable. The domain seed flag is the escape valve — it acknowledges that the incremental growth model has a cold-start problem, without abandoning the model.

---

## The Writing Style: Why Textbook, Not Wiki

Most internal knowledge bases are written in what I'll call "wiki style": short paragraphs, heavy bulleting, declarative sentences, minimal context. The style is efficient for the writer — you can produce a wiki entry in ten minutes — but it's hostile to the reader. A bullet list of "important concepts" tells you nothing. A paragraph that says "OAuth is an authorization framework" is accurate and useless. The reader finishes the entry and thinks: "I still don't know what this is or why I should care."

Our KB entries use a textbook style inspired by Peter Norvig's educational writing. The key discipline:

**Foundational first.** Start with the core idea before showing implementation. A reader who understands *why* a design decision was made can extend the pattern; a reader who only knows *how* copies it.

**Prose paragraphs that develop ideas.** Each paragraph should advance the argument. Avoid short declarative sentences that feel like bullet points in disguise. A paragraph that says "Authentication proves who you are. Authorization decides what you can do. Delegation gives someone else limited authority to act as you." does more work in three sentences than a bullet list with the same content — because the sentences connect, and the reader follows the logic from one to the next.

**Concrete over abstract.** Show real code, real error messages, real project failures. The "what goes wrong when you don't know this" section is the most important part of every entry. It's what separates our KB from Wikipedia — the scar tissue. A Wikipedia article tells you what a concept is. Our KB tells you what happens when you get it wrong, because we got it wrong, and we're telling you so you don't have to.

**Breaks in the rhythm.** Code blocks, tables, and diagrams do work that prose cannot. A table comparing three authentication mechanisms side by side teaches more than three paragraphs describing each one. A code snippet showing the exact `0x80 >> (x % 8)` bit-packing expression teaches more than a sentence saying "pack bits from left to right."

Here's the difference in practice. Wiki style:

```markdown
## OAuth 2.0

OAuth 2.0 is an authorization framework. It has four flows:
- Authorization Code
- Implicit (deprecated)
- Client Credentials
- Resource Owner Password Credentials

We use Authorization Code with PKCE.
```

Textbook style:

```markdown
## The idea in one paragraph

OAuth solves the *delegation* problem: "I want this app to access my data
on that service, but I don't want to give it my password." The user
authenticates directly with the authorization server (Keycloak), the
server issues a scoped token to the app, and the app uses that token to
access the resource. The app never sees the user's password. The token
is scoped (limited permissions) and short-lived (limited duration).

## The two flows we use

We use exactly two flows: Authorization Code with PKCE (for browser and
CLI clients) and Client Credentials (for service-to-service). The other
flows defined in the spec — Implicit and Resource Owner Password — are
deprecated or insecure, and we don't use them.
```

The second version is longer, but the reader finishes it and *understands*. They know what problem OAuth solves, they know which flows we use, and they know we've deliberately excluded the others. The first version is shorter, but the reader finishes it and wonders: "Which flow do I use? Why PKCE? What's wrong with Implicit?"

The anti-patterns are as important as the patterns. Here are the ones we catch most often:

| Anti-pattern | Example | Why it fails |
|-------------|---------|-------------|
| Wandering preamble | "In the ever-evolving landscape of modern firmware development..." | The reader learns nothing. Start with the point. |
| Hedged non-claim | "This approach could potentially offer certain advantages in terms of flexibility" | Says nothing while consuming words. Be direct. |
| Vague bullets | "- Important concepts / - Key takeaways" | The reader cannot act on "important concepts." Every bullet must be a complete sentence. |
| Philosophical throat-clearing | "This pattern contains a profound elegance that reveals itself..." | Show the code. Let the reader decide if it's elegant. |

---

## The Cross-Referencing Web: Why Bidirectional Links Matter

A KB entry that doesn't link to its sources is an orphan. A project report that doesn't link to its concept explanations is a dead end. The cross-referencing convention makes the KB a navigable graph instead of a pile of documents.

The convention is simple: every link must be bidirectional. If a project report links to an on-ramp entry, the on-ramp entry must link back to the project report. If a fundamental entry supports an on-ramp entry, the on-ramp must mention the fundamental.

We use Obsidian wikilinks with the section path and the kebab-case filename:

```markdown
From project report → KB:  [[Tribal/goja-embedding-in-go]]
From KB → project report:  [[PROJ - SToMS3R - AtomS3R Lite Thermal Printer Firmware]]
From on-ramp → fundamental: [[Fundamentals/signal-quantization-and-sampling]]
```

Each link includes a one-line annotation explaining *why* you'd follow it. A bare `[[PROJ - SToMS3R]]` is navigable but doesn't tell you what the project demonstrates about the concept. An annotated link — `[[PROJ - SToMS3R - AtomS3R Lite Thermal Printer Firmware]] — Atkinson dithering + gamma 1.8 in the browser, 1-bit bitmap to K118 printer` — is self-documenting.

Project reports also list their tribal candidates with current counts:

```markdown
## Related KB entries

- [[Tribal/esp-idf-firmware-patterns]] — the esp_console + web UI architecture
- [[On-Ramp/esc-pos-thermal-printer]] — the GS v 0 command and timing constraint

**Tribal candidates** (not yet at 3-project threshold):
- Buffer-full-body-before-UART (2/3) — read entire body before sending to printer
- MSB-first bit packing (2/3) — our specific 0x80 >> convention
```

This distributes the candidate tracking: each project report carries its own contribution to the threshold count. The next analyst reads the report, sees the candidates, and knows to check whether their project increments any of them.

---

## The Intern Trial: What We Learned by Testing the Playbook

After writing the playbook (18 KB of rules, templates, worked examples, anti-patterns, and quality checklists), we needed to know whether it actually works for someone who doesn't already know the domain. We assigned six projects to an agent — two easy, two medium, two hard — and asked it to follow Steps 1–5.

The agent produced thorough analysis for all six projects, correctly applied the decision rules, identified 29 new tribal candidates, and found one entry that had reached threshold ("application-native authorization" at 3/3, which our initial batch of 8 projects had missed because Agent Enroll wasn't in the sample). It also followed the anti-patterns correctly: it *didn't* write a GStreamer on-ramp entry from fresh knowledge, even though the project report would benefit from one.

The trial revealed seven concrete gaps in the playbook. Here are the most important ones.

### Gap 1: Variation of existing entry vs new candidate

ZK Tool's `require("obsidian")` module follows the goja-embedding pattern but with a domain-specific native module. Is this a new tribal candidate (2/3) or just a variation to add to the existing goja entry? The playbook had no rule for this case.

The fix: if the concept follows an existing entry's structure and only differs in the domain-specific surface, add it as a variation. Only create a new candidate if the code structure and gotchas are structurally different. A native module registration that reuses the same `modules.Register()` call and the same `require()` bridge is a variation, not a new entry.

### Gap 2: Shared insight, different mechanism

Agent Enroll uses Ed25519 request signing. Wish Git uses SSH certificates. BYOK Host uses broker OAuth tokens. All three share the core insight: "Keycloak authenticates humans; the Go application owns agent authorization." But the specific mechanisms are different. Is this one pattern at 3/3, or three separate patterns at 1/3 each?

The fix: count projects that share the core insight, even if the mechanism differs. Document the mechanism differences as variations in the tribal entry. The alternative — requiring identical mechanisms — would mean no pattern ever reaches threshold, because every project implements things slightly differently.

### Gap 3: The cold-start problem for new domains

The playbook assumes incremental growth: read project reports, extract concepts, track candidates, create entries at threshold. But what happens when a project opens a completely new technology domain with zero KB coverage? The project report is unreadable without orientation that doesn't exist yet, and the trigger rules say "don't create entries preemptively."

The fix: the `🌐 Domain seed` flag. When a project introduces a new domain, flag it for human review. The reviewer decides whether to bootstrap an initial cluster of entries or let the domain grow organically. This doesn't override the trigger rules — it adds a human judgment layer for the cold-start case.

### Gap 4: Difficulty ≠ report size

Our assignment used project report size as a difficulty proxy. The intern found that this doesn't work. A 6 KB report in a familiar domain (ZK Tool) is easy. A 23 KB report in a new domain (Screencast Studio) is hard. What determines difficulty is the number of concept domains with zero existing KB coverage, not the byte count.

### Gap 5: The on-ramp fresh-knowledge exception is buried

The playbook says "don't write entries from fresh knowledge" but also says "you CAN write an on-ramp draft if someone reviews it." This exception was buried in a paragraph and easy to miss. On-ramp entries are precisely the ones that make project reports readable, and they're the ones newcomers are most likely to encounter first. The fix: promote the exception to a visible callout with an explicit review workflow.

### Gap 6: Ambiguous tribal/lookupable boundary

"Arduino-cli cross-compilation" — the CLI is documented by Arduino, but our headless no-IDE workflow is ours. The decision tree asks "is it our-specific knowledge?" and the answer is "sort of both." The fix: when in doubt, default to on-ramp candidate. The higher threshold (5 vs 3) means fewer premature entries.

### Gap 7: Step 4 ambiguity — modify files or propose changes?

The intern wasn't sure whether Step 4 (cross-referencing) meant actually editing the PARC project report files or just documenting the changes that should be made. For someone without implementation experience, proposing is safer. The fix: first pass = propose; second pass (or if experienced) = edit.

---

## The Playbook Structure: What's in the 40 KB

After incorporating the trial feedback, the playbook has seven sections. Here's what each one does and why it exists.

**What the KB is for.** One paragraph that states the KB's purpose: make project reports readable. This section prevents scope creep. If someone suggests adding a "how to set up Docker" entry, the purpose statement makes it clear: Docker setup isn't something that blocks you from reading a project report. It doesn't belong in the KB.

**The three-section KB.** The taxonomy, the trigger rules, and the classification edge cases. The edge cases section is new — it was added after the intern trial revealed three ambiguous situations (variation vs candidate, shared insight vs different mechanism, ambiguous boundary).

**Writing style.** The textbook style guide, anti-pattern table, and three real examples of good writing pulled from our own entries. This is the section that most differentiates our KB from a typical internal wiki. It's also the section that's hardest to follow — writing well is harder than writing correctly.

**Steps 1–5.** The operational workflow: read the project report, classify concepts, write entries, cross-reference, update the project index. Each step has a concrete deliverable and a worked example (the SToMS3R walkthrough).

**Candidate tracking.** The running list format and the domain seed convention. This section is the engine of incremental growth — it's what makes the KB accumulate value over time instead of requiring a single massive effort.

**Quality checklist.** Twelve items that every entry must pass before submission. The checklist includes the basics (correct section, template followed, length in range) and the subtle things (bidirectional cross-references, project report links, tribal candidates listed in the source project).

**Completed entries inventory.** A table of all 18 existing entries with filenames, sizes, and key projects. This serves two purposes: it tells new analysts what already exists (so they don't recreate it), and it provides calibration examples (read two or three before writing a new one).

---

## What We'd Do Differently

The playbook reflects lessons learned from writing 18 entries and testing them on one intern. If we were starting over, here's what we'd change.

**We'd write the playbook before the entries, not after.** Our actual sequence was: write 18 entries, then extract the playbook from what we learned, then test the playbook. The better sequence is: write the playbook from first principles, test it on one project, refine it, then use it to write all the entries. We got lucky — our entries were consistent because one person wrote all of them — but a team of five writing entries without a playbook would produce five different styles.

**We'd set up cross-referencing from the start.** Adding bidirectional links retroactively to 18 entries and 8 project reports was tedious. If we'd established the convention from the first entry, each subsequent entry would have linked forward and backward as part of the writing process, not as a separate cleanup pass.

**We'd use a link validation tool.** Obsidian wikilinks are convenient but fragile — rename a file and all its incoming links break. A simple script that checks every `[[...]]` reference against actual filenames would catch broken links before they accumulate.

**We'd track analysis coverage.** After 8 projects (out of 304), we have 18 entries and 29 tribal candidates. We don't have a coverage metric — what fraction of the library's concepts have we seen? A rough coverage tracker ("8/304 projects analyzed, ~15% of concept space covered") would tell us when to stop the initial analysis and start writing, and when to resume analysis because new domains are appearing.

---

## The Numbers

For the numerically minded, here's what the KB looks like after one round of analysis:

| Metric | Value |
|--------|-------|
| Project reports in library | 304 |
| Projects analyzed (Batch 1) | 8 |
| KB entries created | 18 |
| Total KB size | ~107 KB |
| Tribal entries | 6 (4.6–6.7 KB each) |
| On-Ramp entries | 8 (5.1–6.3 KB each) |
| Fundamental entries | 4 (5.6–6.9 KB each) |
| Tribal candidates tracked | 29 (waiting for 3-project threshold) |
| On-Ramp candidates tracked | 9 (waiting for 5-project threshold) |
| Domain seeds flagged | 2 (GStreamer, Arduino-cli) |
| New entries triggered by intern trial | 1 (application-native authorization) |
| Cross-references added | 26 bidirectional links |
| Playbook size | ~40 KB |
| Intern trial projects | 6 |
| Playbook gaps found by trial | 7 |

The library has 304 project reports and we've analyzed 8 of them — roughly 2.5% coverage. The KB will grow substantially as we process more batches. The candidate tracking list suggests we'll create another 5–10 entries when the next batch pushes candidates over their thresholds.

---

## The Core Insight

If you take one thing from this article, take this: the knowledge base is not the goal. The playbook is not the goal. The cross-references are not the goal. The goal is to make project reports readable — so that anyone on the team, past or future, human or agent, can open a report and understand what was built without getting stuck on an unfamiliar concept.

Everything else — the three sections, the trigger rules, the textbook style, the bidirectional links — is in service of that goal. If a rule makes project reports more readable, keep it. If a rule makes the KB more consistent but doesn't help readability, question it. The KB is infrastructure; the project reports are the product.

The playbook is the mechanism that makes the KB self-sustaining. Without it, every entry is a one-off decision made by whoever happens to be writing. With it, any team member can produce consistent, high-quality entries that connect to each other and to the project reports they serve. The playbook is not the point — but it's what makes the point achievable at scale.
