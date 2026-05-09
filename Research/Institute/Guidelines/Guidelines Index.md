---
title: Research Institute Guidelines
aliases:
  - Guidelines Index
  - Institute Guidelines
  - Lab Handbook
tags:
  - research
  - guidelines
  - institute
  - index
status: active
type: index
created: 2026-04-03
---

# Research Institute Guidelines

Operating guidelines for the research institute. These are the norms that define how we work — how we investigate, build, write, share, and evaluate. They are written to be concrete enough that a new researcher (human or agent) can follow them from day one, and opinionated enough that they actually shape behavior.

> [!quote] The PARC principle
> A research lab's output is not papers. It's working systems, transferable ideas, and people who understand both. Every guideline here serves that principle.

---

## The Guidelines

### How We Investigate

- [[Deep Research with Web Tools]] — Full workflow for running a deep research session with Kagi, ChatGPT deep research, defuddle, and Playwright. The playbook for answering hard questions using web tools and AI assistants.

- [[Running a Literature Review]] — How to survey a field systematically: defining scope, finding sources, reading efficiently, synthesizing across papers, and producing a review document that's useful to the team — not just a list of things you read.

- [[Evaluating a Technology Choice]] — The process for deciding between technologies (languages, engines, libraries, architectures). How to structure a comparison so the decision is traceable, the tradeoffs are explicit, and future-you understands why you chose what you chose.

### How We Build

- [[From Question to Prototype]] — The lab's core loop: identify a question that can only be answered by building something, build the smallest thing that answers it, then document what you learned. Not waterfall, not agile — research prototyping.

- [[Running a Design Session]] — How to go from a vague idea to a concrete design document in one sitting. Includes the "napkin sketch → whiteboard → structured doc" progression and how to involve both humans and agents.

- [[Code Review as Research Conversation]] — Code review in a research lab is not about style guides. It's about "does this actually test the hypothesis?" and "what would we learn if we changed X?" How to review research code differently from production code.

- [[Code Review with go-minitrace]] — Post-session analysis playbook: convert a Pi or Codex session to minitrace, run SQL queries to find churn and confusion patterns, map high-churn files to review priorities, and write evidence-based findings. The 30–60 minute review that catches what a standard diff review misses.

### How We Write

- [[Writing Style for Knowledge Base Articles]] — The article-style writing standard for all knowledge base documents. Concrete scenarios before definitions, explain before showing code, name the people behind ideas, make the so-what explicit. The quality bar for anything that goes into the vault.

- [[Writing a Design Document]] — How to write a design doc that's useful for both the author (as a thinking tool) and the reader (as a decision record). Structure, level of detail, when to write one vs when not to.

- [[Writing a Trip Report]] — What to write after attending a conference, reading a book, having a key conversation, or completing an investigation. Short, opinionated, focused on "what changed in my thinking."

### How We Share

- [[The Weekly Demo]] — Every researcher demos working software once a week. Not slides — running code. The demo is 5 minutes, the discussion is 25 minutes. How to prepare, what to show, what makes a good demo.

- [[Cross-Pollination Notes]] — When your work connects to someone else's project, write a short note explaining the connection. Not a formal report — a paragraph or two saying "here's what I found that might matter for your thing." How and when to write them.

- [[Maintaining the Knowledge Base]] — Conventions for the Obsidian vault: how notes are organized, how to link things, what goes where, when to create a new note vs extend an existing one. The gardening guide for our collective memory.

### How We Use Tools

- [[docmgr Ticket Workflow]] — How to use docmgr for research tickets: creating tickets, managing tasks, writing changelogs, relating files. The operational backbone for tracking what we're doing and what we've done.

- [[Agent-Assisted Research Patterns]] — How to work effectively with AI coding agents (pi, Claude, ChatGPT) as research collaborators. When to delegate, when to drive, how to structure prompts for research tasks, and how to verify agent-produced content.

- [[Obsidian Vault Conventions]] — Tags, folder structure, frontmatter standards, linking conventions, and the graph-view mental model. How to make the vault useful instead of just large.

### How We Evaluate

- [[Research Quality Checklist]] — The bar for "is this investigation complete?" Not a bureaucratic form — a set of honest questions: Did you test the thing you said you'd test? Did you document what didn't work? Could someone continue from where you stopped?

- [[Postmortem Template]] — When something doesn't work as expected (a prototype fails, an approach turns out to be wrong, a tool doesn't deliver), write a postmortem. Not to assign blame — to capture what the failure taught you.

---

## Why These Exist

A research lab without norms becomes either chaotic (everyone doing their own thing, nothing connects) or bureaucratic (process replaces thinking). These guidelines aim for a third path: **lightweight structure that amplifies individual judgment.**

Each guideline is:
- **Concrete** — includes exact commands, code patterns, or templates
- **Opinionated** — says "do it this way" not "here are some options"
- **Derived from experience** — every guideline exists because we hit a problem without it
- **Short enough to actually read** — if a guideline is too long to read in one sitting, it's too long

> [!tip] Contributing
> If you find yourself doing something repeatedly that isn't covered by a guideline, write one. If you find a guideline that's wrong or outdated, fix it. These are living documents, not policy.
