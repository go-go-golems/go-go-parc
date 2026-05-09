---
title: Writing Style for Knowledge Base Articles
aliases:
  - KB Writing Style
  - Article Writing Guidelines
tags:
  - research
  - guidelines
  - institute
  - writing
status: active
type: guideline
created: 2026-04-03
---

# Writing Style for Knowledge Base Articles

Every document in the knowledge base should read like a knowledgeable person explaining something to a smart colleague over coffee — not like a Wikipedia article, not like a man page, and definitely not like a bulleted list of facts.

This document defines the quality bar.

---

## The Core Principle

The purpose of a knowledge base article is to **transfer understanding**, not to record information. The difference matters: recording information produces notes that are useful to the person who wrote them. Transferring understanding produces notes that are useful to everyone, including future-you who has forgotten the context.

> [!tip] The litmus test
> Could someone who hasn't seen any of your source material read this document and come away actually *understanding* the topic — not just knowing what it says?

---

## How to Open

Start with a **concrete scenario the reader recognizes** — not a definition, not "this document covers X."

> [!example] Wrong
> This article covers JavaScript's LexicalEnvironment and VariableEnvironment and their implications for REPL design.

> [!example] Right
> Imagine you're building a JavaScript REPL — you want users to type code cell by cell, like a Jupyter notebook. You try the obvious thing: call `eval()` for each cell and let the results accumulate. It almost works. `var x = 1` in cell 1 is visible in cell 2. But `const answer = 42` vanishes between cells. This is not a bug.

The right version puts the reader in the situation, shows them the surprise, and makes them want to know why.

---

## How to Explain

**Explain before showing code.** Never drop a code block without first telling the reader what they're about to see and why it matters.

> [!example] Wrong
> ```javascript
> eval("let b = 2");
> eval("console.log(b)"); // ReferenceError
> ```

> [!example] Right
> To see this concretely, try running two separate eval calls in sequence. The first defines `b`, but the second can't find it:
> 
> ```javascript
> eval("let b = 2");
> eval("console.log(b)"); // ReferenceError: b is not defined
> ```
> 
> The name doesn't "leak" between calls because each eval gets its own fresh DeclarativeEnvironmentRecord, and the first one is discarded when the first eval returns.

The right version has three parts: setup ("try running..."), the code, and the explanation of *why* it behaves that way. The code block alone is just data; with the surrounding prose it becomes understanding.

---

## How to Build Narrative

Each section should flow from the one before it. Don't write isolated blocks — write a story.

**Use transitions that make the causal chain explicit:**
- "This is *why* the go-go-goja webrepl..."
- "The consequence for REPL design is..."
- "This distinction matters because..."
- "That brings us to the harder question..."

**Use the historical arc when you have it.** Research almost always reveals a history — ideas evolving over decades, problems solved differently in different eras. This is gold for narrative:

> The problem of keeping state between evaluations is older than JavaScript. Smalltalk solved it by making state the entire system — you'd snapshot the live object graph to a file and resume from it later. Jupyter solved it differently: a kernel is a long-running process, and state persists because the process persists. Browser DevTools took a third approach: state is tied to an execution context, which lives as long as the page does. Each choice reflects the constraints of its era.

**Name the people behind ideas:**

> The term "IIFE" was coined by Ben Alman in a 2010 blog post arguing that "Immediately-Invoked Function Expression" was clearer than "self-executing anonymous function."

> Douglas Crockford's writing on the module pattern made IIFEs culturally important in the pre-ES6 era — they were the idiomatic way to create closure-based privacy before the language had `class` or `import`.

Names add historical depth and make the content more memorable. They also make it possible to find the primary source.

---

## How to End a Section

**Make the "so what" explicit.** Don't leave the reader to infer the implication. Every section that explains a mechanism should end with what that mechanism means for the thing you're building:

> This is the reason the go-go-goja webrepl implemented the async IIFE capture-and-replay pattern instead of something simpler. The spec's design is not a bug to work around — it's a constraint to work with.

If you can't articulate the "so what," the section might not belong in the article.

---

## Structure

Every knowledge base article follows this arc:

1. **The concrete problem** — open with a scenario
2. **Why it works this way** — historical or design reasoning
3. **The mechanism in detail** — spec-level or implementation-level, with explained code
4. **The implications** — explicit "so what" for your project
5. **Key references** — short table (5–8 rows max)
6. **Further reading** — 3–5 links, each with a one-sentence description of what it adds

---

## Length

Target **600–1500 words** of body text (not counting frontmatter and reference tables). If a doc is under 400 words, it's probably a reference card, not an article. If it's over 2000 words, consider splitting it into two linked notes.

---

## What to Avoid

**Bullet-point syndrome.** If your document is 80% bullet points, rewrite it as prose. Bullets are for short reference lists, not for explanations. An explanation requires sentences that build on each other.

**"This document covers..."** openings. The reader can see from the title what the doc covers. Open with the *problem*, not the table of contents.

**Unexplained code blocks.** Every code block should have a setup sentence before it and an explanation sentence after it.

**Passive voice for decisions.** Don't write "the IIFE pattern was chosen." Write "we chose the IIFE pattern because..." — or if you're explaining someone else's decision, "the go-go-goja webrepl uses the IIFE pattern because..."

**Tables as the primary content.** A comparison table is a summary, not an explanation. The explanation goes in the prose above the table. The table is a reference aid.

---

## Using AI-Produced Sources

When incorporating material from Kagi assistant, ChatGPT deep research, or any AI tool:

- **Strip citation markers** — things like `citeturn7search8` from ChatGPT exports
- **Rewrite into your voice** — AI writing is often flat and hedging ("it's worth noting that..."). Cut the hedges, strengthen the claims where warranted
- **Verify specific claims** — spec section numbers, dates, and attributions should be checked. AI tools sometimes hallucinate these
- **Add the "so what"** — AI synthesis rarely tells you what the finding means for *your specific project*. That's your job

> [!warning]
> An article that reads like a lightly-edited AI response has failed the quality bar. The value is in your interpretation, your connections to the codebase, and your judgment about what matters — not in restating what the AI said.
