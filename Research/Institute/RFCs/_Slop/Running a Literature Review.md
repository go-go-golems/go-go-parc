---
title: Running a Literature Review
aliases:
  - Literature Review
  - Survey Methodology
tags:
  - research
  - guidelines
  - institute
  - methodology
  - literature-review
status: active
type: guideline
created: 2026-04-03
---

# Running a Literature Review

A literature review answers the question: "What does the world already know about this?" It's the foundation for any research direction — you need to know where the frontier is before you can push past it. But a bad literature review is worse than no review at all: it gives you false confidence that you've covered the ground.

---

## When to Do a Literature Review

- **Before starting a new research direction** — to understand the state of the art and avoid reinventing existing work
- **When you hit a wall** — to find out whether others have hit the same wall and what they tried
- **When evaluating an approach** — to find prior art, known limitations, and alternatives

You do NOT need a literature review when:
- The question can be answered by building something (see [[From Question to Prototype]])
- The answer is in one specific document you already know about (just read that document)
- You're exploring an area where there is no prior art (then your prototype IS the literature)

---

## The Process

### 1. Define the scope as a question

Not "everything about topic X" but "how have people solved problem Y in context Z?"

> [!example] Too broad
> "JavaScript REPL design"

> [!example] Right scope
> "How do existing JS REPLs (Node, browser DevTools, Jupyter-like notebooks) handle persistence of let/const bindings across evaluation calls?"

A well-scoped question tells you when you're done: you're done when you can answer it.

### 2. Find sources using the tool hierarchy

Follow the [[Deep Research with Web Tools]] playbook:

1. **ChatGPT deep research** for the broad survey — submit early, let it run async
2. **Kagi search** for finding specific pages (spec documents, author blog posts, key papers)
3. **Kagi assistant** for understanding specific mechanisms with spec-level depth
4. **defuddle** for fetching and cleaning each URL
5. **Direct source reading** for source code, RFCs, and spec text

### 3. Read in passes, not linearly

Don't read every source end to end. Instead:

**First pass (triage, 30 seconds per source):** Title, abstract/intro, conclusion. Is this relevant? Keep or discard.

**Second pass (extraction, 5–10 minutes per source):** What's the key claim? What evidence supports it? What's the main technique/approach? Write 3–5 bullet points in `sources/web/<source>.md`.

**Third pass (only for the 3–5 best sources):** Deep read. Understand the argument fully. Note connections to your project.

### 4. Synthesize across sources, not within

The review document is NOT a list of paper summaries. It's a synthesis organized by *theme*:

> [!example] Wrong — source-by-source
> **Soshnikov (2010)** describes LexicalEnvironments as... 
> **Rauschmayer (2011)** explains that VariableEnvironment is...
> **TC39 spec** defines...

> [!example] Right — theme-by-theme
> Every execution context carries two scope structures: a LexicalEnvironment for `let`/`const`/`class` and a VariableEnvironment for `var` and function declarations. Dmitry Soshnikov's deep dive on ECMA-262-5 remains the most thorough non-spec explanation of how these chain together. The key insight, which Rauschmayer summarizes concisely, is that the two structures have fundamentally different persistence properties because one is backed by object properties and the other by a pure spec abstraction.

The right version weaves sources together to build understanding. The wrong version just lists what each source says.

### 5. Write the review as an article

Use the [[Writing Style for Knowledge Base Articles]] guidelines. A good literature review:

- Opens with the research question
- Traces the historical arc (how thinking about this evolved)
- Identifies the 2–3 main approaches or schools of thought
- Notes points of disagreement or open questions
- Ends with what this means for your project — the "so what"

---

## Scope Control

The biggest risk in a literature review is going too broad. Mitigations:

- **Time-box it.** A literature review should take half a day to a full day, not a week. If it's taking longer, your scope is too broad.
- **Stop when you see convergence.** When the third source tells you the same thing as the first two, you've found the consensus view. Note it and move on.
- **Save tangents for later.** When you find something interesting but off-topic, create a quick note with the URL and a one-line description, then keep going. It becomes a future research question, not a distraction.

> [!tip] The "diminishing returns" signal
> You're done when new sources are mostly confirming what you already know, and the key open questions are ones you'll need to answer by building something rather than by reading more.
