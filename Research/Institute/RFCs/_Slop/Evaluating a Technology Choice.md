---
title: Evaluating a Technology Choice
aliases:
  - Technology Evaluation
  - Tech Choice Framework
tags:
  - research
  - guidelines
  - institute
  - evaluation
  - decision-making
status: active
type: guideline
created: 2026-04-03
---

# Evaluating a Technology Choice

Choosing between technologies (languages, engines, libraries, frameworks, protocols) is a recurring research task. The goal is not to find the "best" option in the abstract — it's to find the option that's best *for your specific situation* and to make that reasoning traceable so future-you understands the decision.

---

## The Three Questions

Every technology evaluation boils down to three questions:

1. **What are the hard constraints?** Things that are non-negotiable — "must be pure Go, no CGo" or "must support ES modules" or "must be goroutine-safe." These eliminate options immediately.

2. **What are the tradeoffs between the remaining options?** Once the hard constraints filter the field, compare the survivors along the dimensions that actually matter to your project. Not every possible dimension — just the ones that affect your work.

3. **What would make us change our mind later?** Every technology choice is conditional. Document the assumptions that make your choice correct, so that if those assumptions change, you know it's time to re-evaluate.

---

## How to Structure the Evaluation

### State the decision context

One paragraph explaining: what you're building, what role this technology plays in it, and why you're evaluating options now (not earlier, not later).

> For the go-go-goja webrepl, we need an embedded JavaScript engine that runs inside a Go HTTP server, evaluating user-submitted code cells in long-lived sessions. The engine must be embeddable without CGo (for deployment simplicity), must support enough of ES6+ for practical use, and must allow us to control the global object programmatically.

### List the hard constraints

These are pass/fail. An option that fails any hard constraint is eliminated, no matter how good it is on other dimensions.

| Constraint | Why |
|-----------|-----|
| Pure Go (no CGo) | Deployment target requires static binaries |
| `eval()`/`RunString()` API | Need to evaluate arbitrary user code at runtime |
| Programmatic global object access | Must set/get bindings between cells |

### Compare the survivors

After hard constraints eliminate options, compare what's left along **project-specific** axes. These are tradeoff dimensions, not pass/fail.

> [!warning] Avoid generic comparisons
> Don't compare on "community size," "GitHub stars," or "documentation quality" unless those genuinely affect your research. Compare on the axes that determine whether the technology works for your specific use case.

For the embedded JS engine evaluation, the relevant axes were:

| Axis | goja (Go) | QuickJS (C) | Duktape (C) |
|------|-----------|-------------|-------------|
| CGo required? | No ✓ | Yes | Yes |
| ES version | ES5.1 + extensions | ES2020 | ES5.1 |
| Thread safety | Single-goroutine per runtime | Single-thread per runtime | Single-thread per heap |
| Module loading | goja_nodejs (CommonJS) | Native ES modules | Extras/optional |
| `vm.Set()`-equivalent | `runtime.Set(name, val)` | `JS_SetPropertyStr()` | `duk_put_global_string()` |

### Make the recommendation explicit

Don't just present the data — state your choice and why:

> We chose goja because it's the only option that satisfies the "no CGo" hard constraint. This is the decisive factor. If CGo were acceptable, QuickJS would be a strong alternative due to its broader ES support. We document this because if our deployment constraint changes, QuickJS should be re-evaluated.

### Document what would change the decision

This is the most commonly omitted part and the most valuable:

> **Assumptions that make goja the right choice:**
> - We don't need ES modules (CommonJS via goja_nodejs is sufficient)
> - ES5.1 + the extensions goja provides (let/const/class/arrow functions) covers our users' needs
> - Deployment must remain CGo-free
>
> **If any of these change,** re-evaluate QuickJS (which supports ES2020 natively and has full ES module support).

---

## Anti-Patterns

**The beauty contest.** Comparing 10 options across 20 dimensions in a massive table, without stating hard constraints first. Most of those options should have been eliminated on row 1.

**The bikeshed evaluation.** Spending a week evaluating options for something that doesn't matter much. If the choice is easily reversible, pick one and move on.

**The missing "why not."** Documenting what you chose without explaining why you *didn't* choose the alternatives. The alternatives are where the reasoning lives.

**The permanent decision.** Treating a technology choice as final. Research is iterative — you should expect to re-evaluate as your understanding deepens. The document's job is to make re-evaluation efficient, not to prevent it.

---

## Where the Document Goes

Technology evaluations go in the ticket's `design-doc/` directory (since they're design decisions) and should be linked from the knowledge base if the comparison is reusable:

```
design-doc/02-embedded-js-engine-evaluation.md
reference/06-go-go-goja webrepl - Embedded JS Engine Design.md  ← the KB version
```

The design doc version includes the full evaluation with all details. The reference version distills it into an article that's useful to someone who just wants to understand the landscape and why goja was chosen.
