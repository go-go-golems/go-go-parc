---
title: From Question to Prototype
aliases:
  - Research Prototyping
  - Prototype-Driven Research
tags:
  - research
  - guidelines
  - institute
  - prototyping
  - methodology
status: active
type: guideline
created: 2026-04-03
---

# From Question to Prototype

The lab's core loop is not "read → think → write." It is **"ask → build → learn."** The prototype is not the deliverable — the understanding it produces is the deliverable. The prototype is the instrument.

This guideline describes how to go from a research question to a working prototype that answers it.

---

## Why Prototypes, Not Papers

A paper says "we believe X would work because of reasoning Y." A prototype says "we built X and here's what actually happened." The difference is the difference between a hypothesis and an experiment.

Xerox PARC didn't invent the GUI by writing a paper about graphical interfaces. They built the Alto, put it on every researcher's desk, and let people use it. The insights came from the building and the using — not from the theorizing.

The same pattern holds at smaller scales. When the go-go-goja webrepl team needed to understand how JavaScript scoping interacts with REPL persistence, they didn't just read the ECMA-262 spec. They built two prototypes — one in Node.js using `with(scopeProxy)`, one in Go using async IIFEs — and compared the behavior. The Node prototype taught them that `with` has a fundamental limitation (`let`/`const` bindings are invisible to it). That insight couldn't have come from reading alone.

> [!tip] The PARC test
> If your research question can be answered by building something small and running it, build it. If it can only be answered by reading and thinking, that's a literature review — use the [[Deep Research with Web Tools]] playbook instead.

---

## The Loop

### 1. State the question as a testable claim

Not "how does X work?" but "I believe X works by doing Y — let me build something to find out."

**Good research questions for prototyping:**
- "Can we make `let`/`const` persist across REPL cells using an IIFE wrapper?" → build a rewriter and test it
- "Does goja's single-goroutine constraint prevent us from serving multiple sessions?" → build a concurrent session server and measure
- "Can tree-sitter parse partial JavaScript well enough for REPL completion?" → build a completion provider and try it on real inputs

**Bad research questions for prototyping:**
- "What is the history of the IIFE pattern?" → that's a literature review
- "Which JS engine is fastest?" → that's a benchmark, not a prototype
- "Should we use REST or WebSocket?" → that's a design decision, informed by prototyping but not a prototype itself

### 2. Build the smallest thing that tests the claim

The prototype should be the **minimum amount of code** that lets you observe whether the claim holds. Not a product. Not a framework. Not something with error handling and test suites. A prototype that takes more than 2–3 days to build is too big.

For the IIFE-01 research, the Node.js prototype was ~600 lines of code across 4 files. It had no tests, minimal error handling, and a vanilla HTML+Bootstrap UI. It was enough to demonstrate the `with(scopeProxy)` approach, discover its limitations, and produce the architectural insights that shaped the Go implementation.

> [!important] The prototype is not the product
> A prototype exists to produce understanding. Once it has done that, its job is done. It may be thrown away, or it may evolve into something else, but its success is measured by what you learned — not by whether it ships.

### 3. Document what you learned

The output of the prototype loop is a **design document** or **knowledge base article** — not the code. The document should cover:

- What question you were testing
- What you built (briefly — the code is in the repo)
- What you observed — both expected and surprising behavior
- What edge cases you discovered
- What this means for the real system

Use the [[Writing Style for Knowledge Base Articles]] guidelines. The document should be readable by someone who has not seen the prototype.

### 4. Decide: continue, pivot, or done

After one prototype iteration:
- **Continue** — the question is partially answered, build the next iteration
- **Pivot** — the prototype revealed the question was wrong, reframe it
- **Done** — the question is answered, write it up and move on

Most research questions take 1–3 prototype iterations.

---

## What Makes a Good Research Prototype

**It runs.** Not "it compiles" or "it has a nice architecture." It produces observable output that you can show to someone.

**It's throwaway-safe.** If the prototype disappeared tomorrow, the knowledge it produced (captured in documentation) would survive. Don't put essential understanding only in the code.

**It tests one thing.** A prototype that tests three things at once makes it hard to know which thing produced which result. If you have three questions, consider three small prototypes.

**It has a demo.** Every prototype should be demoable in under 5 minutes. See [[The Weekly Demo]] for how demos work in the lab.

---

## Anti-Patterns

**The "framework prototype."** Building a general-purpose framework when you need to test one specific behavior. Generality is the enemy of speed in research prototyping. Hard-code things. Use string concatenation instead of templates. Skip the abstraction layer.

**The "production prototype."** Adding error handling, input validation, logging, and configuration to a prototype. These are production concerns. A prototype that crashes on bad input is fine — you control the input.

**The "secret prototype."** Building something for weeks without telling anyone or writing anything down. The lab works by sharing early and often. A half-working prototype demoed on Monday is worth more than a polished one demoed on Friday.

**The "abandoned prototype."** Building something, learning from it, and then not writing up what you learned. The understanding evaporates. The next person asks the same question and builds the same prototype. Write the document.
