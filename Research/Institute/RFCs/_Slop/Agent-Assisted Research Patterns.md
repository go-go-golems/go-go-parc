---
title: Agent-Assisted Research Patterns
aliases:
  - Working with AI Agents
  - Agent Research Patterns
tags:
  - research
  - guidelines
  - institute
  - agents
  - ai
  - methodology
status: active
type: guideline
created: 2026-04-03
---

# Agent-Assisted Research Patterns

AI coding agents (pi with Claude, ChatGPT, Kagi assistant) are research tools — like a library, a calculator, or a oscilloscope. They amplify what you can do but they don't replace your judgment. This guideline covers how to use them effectively.

---

## The Mental Model

Think of the agent as a **very fast, very well-read research assistant who occasionally makes things up.** It can:
- Read and summarize large amounts of text quickly
- Synthesize across multiple sources
- Generate first drafts of code and documentation
- Search the web and extract content
- Run repetitive tasks (file creation, docmgr bookkeeping, formatting)

It cannot:
- Know whether something is actually true (it can only know whether it's consistent with its training data)
- Understand your specific codebase without reading it first
- Make architectural judgments that depend on context it hasn't seen
- Tell you what matters — only you know what problem you're actually trying to solve

> [!important] The researcher drives
> The agent is the co-pilot. You decide what to investigate, what questions to ask, and whether the answers are correct. The agent accelerates the execution. If you find yourself just accepting what the agent says without verifying, you're doing it wrong.

---

## When to Use Agents

**Delegation works well for:**
- Searching the web for specific facts or URLs
- Synthesizing information from multiple sources into a structured summary
- Writing first drafts of documentation from your notes
- Generating boilerplate (docmgr commands, frontmatter, file scaffolding)
- Reading and summarizing long documents you've pointed it at
- Running Playwright automation against web tools (Kagi, ChatGPT deep research)
- Mechanical transformations (reformatting, renaming, moving files)

**Delegation works poorly for:**
- Deciding what to research (you need to know the question before the agent can help answer it)
- Evaluating whether a research finding is significant (that requires domain judgment)
- Writing the "so what" paragraph (the agent doesn't know what your project needs)
- Architecture decisions (the agent hasn't lived with your codebase)
- Catching its own errors (this is your job)

---

## Prompt Patterns That Work

### The "I'm building X, explain Y" pattern

Start with your context, then ask the specific question:

```
I'm building a persistent JS REPL backed by the goja engine in Go.

Explain why let/const declarations don't survive across separate eval() calls,
tracing through ECMA-262 §18.2.1.1 PerformEval. Include section numbers and 
a code example showing the failure.
```

This works because the context ("I'm building a persistent JS REPL") constrains the response to be relevant to your actual problem, not a generic explanation.

### The "Compare A and B along axes X, Y, Z" pattern

```
Compare goja (pure Go), QuickJS (C), and Duktape (C) as embedded JS engines for 
a REPL server. Compare along: goroutine/thread safety, module loading, eval API 
design, and ES version support. Include specific API function names.
```

Naming the comparison axes prevents the agent from choosing its own (which are usually generic).

### The "Verify and correct" pattern

After getting an AI response, use the agent to check its own work:

```
You cited ECMA-262 §B.3.5 as the section defining the with statement's deprecation. 
Navigate to tc39.es/ecma262 and find what §B.3.5 actually covers. Is the citation correct?
```

This catches the most common AI error: plausible but wrong spec section numbers.

### The "Read this then explain" pattern

Instead of asking the agent about a topic cold, point it at the actual source first:

```
Read the file at /path/to/pkg/webrepl/rewrite.go. Then explain:
1. What the rewriter does to user code
2. Why it uses an async IIFE wrapper
3. What edge cases the code handles
```

This grounds the response in the actual implementation rather than the agent's training data.

---

## Verification Practices

### Always verify spec citations

AI tools frequently hallucinate ECMA-262 section numbers — they get the concept right but cite the wrong section. For any spec reference that matters, either:
- Navigate to the actual spec URL and check (`tc39.es/ecma262`)
- Use defuddle to fetch the spec page and search for the cited section number
- Ask the agent to navigate to the spec via Playwright and confirm

### Cross-check historical claims

"Ben Alman coined IIFE in 2010" — check the actual blog post. "Crockford introduced the module pattern" — verify the date and source. These are usually right but occasionally garbled.

### Run code examples

If the agent produces a code example, run it. This sounds obvious but it's easy to skip when the code looks right. Especially true for edge-case demonstrations — those are where subtle errors hide.

### Watch for confident wrongness

The most dangerous AI output is a clearly-written, well-structured paragraph that is factually wrong. The writing quality is not a signal of accuracy. If something is important to your research, verify it against a primary source — the spec, the source code, or the official documentation.

---

## The Agent Research Session Loop

A typical session follows this pattern:

1. **Orient the agent:** Point it at the relevant code, docs, or prior notes. Let it read them.
2. **Ask the research question:** Use one of the patterns above.
3. **Read the response critically:** Does it answer the question? Are the claims verifiable?
4. **Verify the key claims:** Check spec citations, run code examples, cross-reference with primary sources.
5. **Save the raw response:** To `sources/web/` or `sources/agent/` with a header noting the date and tool.
6. **Write your document:** Using the agent response as source material but in your own voice, with your own judgment about what matters.

> [!warning] Don't skip step 6
> Raw agent output is a source, not a deliverable. It needs to go through your brain and come out as an article that reflects your understanding of the topic. See [[Writing Style for Knowledge Base Articles]].
