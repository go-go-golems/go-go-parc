---
title: The Weekly Demo
aliases:
  - Demo Day
  - Show and Tell
tags:
  - research
  - guidelines
  - institute
  - demo
  - culture
status: active
type: guideline
created: 2026-04-03
---

# The Weekly Demo

Every researcher shows working software once a week. Not slides — running code. The demo is 5 minutes, the discussion is 25 minutes. This is the heartbeat of the lab.

---

## Why Demos

Demos do four things that nothing else does:

**They force concrete progress.** It's easy to spend a week reading, thinking, and planning without producing anything observable. A weekly demo deadline means that by Thursday you need *something that runs*. This is the single most effective antidote to research drift.

**They create cross-pollination.** When you see someone demo a tree-sitter parser and you're working on REPL completion, you realize the two connect. These connections don't happen in status meetings or Slack threads. They happen when you *see the thing running*.

**They calibrate ambition.** Watching other people's demos teaches you what "a week's worth of progress" looks like. Too little and you're going too slowly. Too much and you might be building production software instead of doing research.

**They build shared vocabulary.** After seeing someone demo the IIFE rewriter three times across three weeks — first the basic wrapper, then destructuring support, then the TDZ edge cases — the whole team understands what "the rewriter" means when it comes up in conversation.

---

## Format

**5 minutes:** Show the thing. Run it live. No slides, no pre-recorded video. If it breaks during the demo, that's fine — explain what was supposed to happen and what went wrong.

**25 minutes:** Discussion. Questions. Suggestions. "Have you seen X?" "What happens if you try Y?" "This connects to my work on Z."

**Total:** 30 minutes per demo. If there are 3 researchers demoing, the session is 90 minutes. No more than 4 demos per session.

---

## What to Demo

The bar is **"it runs and you can see it do something."** That something can be small:

**Good demos:**
- "I built a REPL cell rewriter. Watch — I type `const x = 42` in cell 1, and cell 2 can see `x`. Here's the transformed source." (5 min, shows the core mechanism)
- "I connected tree-sitter to the goja parser. Here's the same code parsed by both — look at where the CST and AST differ." (5 min, shows a comparison)
- "I tried three different approaches to scope proxy and all of them hit the same wall. Let me show you the wall." (5 min, shows a *failure* — valuable!)
- "The Kagi assistant produced this synthesis. I verified the spec citations and two of them were wrong. Here's what's actually in §18.2.1.1." (5 min, shows a research finding)

**Bad demos:**
- Slides about what you plan to do next week
- A walkthrough of code that doesn't run
- A 20-minute feature tour of something you've been building for a month (break it into 4 weekly demos instead)

> [!tip] Failures are demos too
> Some of the best demos are "I tried X and it doesn't work — here's why." Showing a failure live, with the error message visible, teaches the team something real. It also prevents anyone else from trying the same thing.

---

## How to Prepare

**Thursday afternoon:** Get your thing to a demoable state. This means it runs end-to-end on at least one happy path. If you've been deep in a refactor, back up to a working state.

**Before the demo:** Write a single sentence: "Today I'll show [what the thing does]." That's your opening line. No other preparation is needed.

**During the demo:** Start with the sentence. Then do the thing. Narrate as you go: "I'm typing this code... now watch what happens when I press enter... this is the rewritten source on the right side..." Point at the interesting parts.

---

## The Discussion

The discussion is where the real value lives. The demo is the prompt; the conversation is the output.

**Good questions to ask during someone's demo:**
- "What happens if you [edge case]?" → often reveals something the researcher hadn't considered
- "Does this connect to [other project]?" → cross-pollination
- "What was the hardest part?" → reveals where the real complexity is
- "What would you build differently if you started over?" → reveals learned design insights

**The rule:** Be curious, not critical. A demo is not a code review. "That's an interesting approach — have you considered X?" is better than "you should be using X instead."

---

## Keeping a Demo Log

After each demo session, someone (rotate this role) writes a brief demo log note in the vault:

```
## Demo Session — YYYY-MM-DD

### [Researcher name]: [One-line summary]
Showed [what]. Key discussion points: [bullets]. 
Connections to: [[Other Project]], [[Other Note]].

### [Researcher name]: [One-line summary]
...
```

This builds a running history of what the lab has produced and helps newcomers get oriented.
