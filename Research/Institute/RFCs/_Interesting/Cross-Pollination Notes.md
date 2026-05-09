---
title: Cross-Pollination Notes
aliases:
  - Cross-Pollination
  - Connection Notes
tags:
  - research
  - guidelines
  - institute
  - collaboration
  - culture
status: active
type: guideline
created: 2026-04-03
---

# Cross-Pollination Notes

When your work connects to someone else's project, write a short note about it. Not a formal report — a paragraph or two saying "here's what I found that might matter for your thing." This is how a research lab avoids silos.

---

## Why This Matters

The most valuable discoveries in any research lab happen at the boundaries between projects. When someone working on REPL scoping finds that the `with` statement has a spec-level limitation that also affects another team's sandboxing approach, that connection needs to be *externalized* — pulled out of one person's head and made visible to the lab.

At PARC, this happened naturally because everyone worked in the same building and ate lunch together. In a distributed lab with async workflows, it has to be intentional.

---

## What a Cross-Pollination Note Looks Like

It's a short Obsidian note — usually 100–300 words — with a specific structure:

```markdown
---
title: "[Your Project] × [Their Project] — [Connection]"
tags:
  - cross-pollination
  - your-project-tag
  - their-project-tag
created: YYYY-MM-DD
---

# [Your Project] × [Their Project] — [Connection]

**What I found:** While working on [your thing], I discovered that [specific finding].

**Why it might matter for [their project]:** [1-2 paragraphs explaining the connection. 
Be specific about what part of their work this affects and why.]

**The key artifact:** [[link to the relevant note, code, or doc]]

**What I'm not sure about:** [Any uncertainty or caveats. It's fine to say "I might be wrong 
about this — worth checking."]
```

---

## When to Write One

Write a cross-pollination note when:

- You discover a **limitation or edge case** that affects another project's approach
- You find a **library, paper, or technique** that solves a problem someone else mentioned
- Your prototype **demonstrates a pattern** that's transferable to another context
- You realize two projects are **solving the same sub-problem** independently
- A [[The Weekly Demo|demo]] sparks a connection you hadn't seen before

Don't wait until the connection is fully fleshed out. A quick note saying "I think X connects to Y because of Z — worth exploring" is more valuable than a detailed analysis that never gets written.

---

## Where They Go

Create a `Cross-Pollination/` folder at the vault root, or tag them with `#cross-pollination` and let the tag system handle discovery. The index note for cross-pollination should be a simple reverse-chronological list.

The important thing is that they're **findable by both project tags** — someone browsing either project's tag should see the connection note.

---

## The Culture Part

Cross-pollination notes work only if writing them is normalized. If the lab culture treats them as "extra work" or "not my project," they won't happen. They need to be treated as a **core research output** — as real as a design document or a prototype.

One way to reinforce this: during [[The Weekly Demo]], explicitly ask "does this connect to anything anyone else is working on?" When someone says yes, that's a cross-pollination note waiting to be written.

> [!tip] Low bar, high frequency
> A cross-pollination note that's one paragraph and slightly wrong is infinitely better than a thorough analysis that never gets written. Keep the bar low. Write them often. Correct them later.
