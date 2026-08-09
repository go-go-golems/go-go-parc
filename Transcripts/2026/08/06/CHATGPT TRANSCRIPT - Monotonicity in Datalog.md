# Monotonicity in Datalog

- URL: https://chatgpt.com/c/6a746fff-d52c-83ea-a3ff-62692212a4b9
- Created: 2026-08-06T11:29:23.925Z

---

> [image: sediment://file_00000000deb0822f9cba5f2f8faee9f5]
> What does monotonicity refer to here?

<details><summary>💭 Thinking</summary>

**Explaining monotonicity**

I’m interpreting the definition as saying that adding input facts can only preserve or increase derived facts. Positive rules satisfy this, while `not Archived(p)` introduces non-monotonic behavior because adding an archive fact can remove `ActiveProject(p)`.

**Explained monotonicity**

</details>

Here, **monotonicity means that adding input facts cannot cause previously derived facts to disappear**.

The possible database states form a lattice ordered by set inclusion. If \(X \subseteq Y\), then \(Y\) contains at least all the facts in \(X\). The rule operator \(F_R\) is monotone when

\[
X \subseteq Y \;\Rightarrow\; F_R(X) \subseteq F_R(Y).
\]

So, applying the rules to a larger fact set produces at least everything that applying them to the smaller set produced.

This matters because the program can be evaluated by repeatedly applying its rules:

\[
\varnothing,\quad F_R(\varnothing),\quad F_R^2(\varnothing),\ldots
\]

For monotone rules, this sequence only grows until it reaches the **least fixed point**—a state where applying the rules derives nothing new.

One important detail: the displayed condition

```text
not Archived(p)
```

is not monotone with respect to `Archived`. Adding `Archived(project-17)` could make `ActiveProject(project-17)` cease to hold. Thus, the monotonicity statement applies directly to **positive Datalog rules**. Negation must be restricted—for example through stratification—or the type system must explicitly track that the expression is non-monotone in that argument.

