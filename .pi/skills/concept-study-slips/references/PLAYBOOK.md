# Concept Study Slips — Playbook

How to get from a study document to paper worth pinning on a wall. Written from
the PBUI run (`Research/Software Architecture Garden/pbui/concepts/`), which
produced seven cards and three briefings.

---

## 1. Understand what the study gives you, and what it does not

An Architecture Garden entry states each foundation as **sets → formula →
operational consequence → limit**, and pins evidence as `file:line`. That is a
complete skeleton and zero flesh: the README deliberately contains no code, no
signatures, no call examples.

So the split of labour is fixed before you start:

| From the study | From the repository |
|---|---|
| the law and its symbols | the function that implements it |
| the operational consequence | the code specimen (3–5 real lines) |
| the limit | the observed behaviour (a test assertion, a doc comment) |
| the vocabulary table | who actually calls it |

**Never source a specimen from a hypothesis document.** In the PBUI case a
"Pattern Zoo Handbook" existed with per-pattern pseudocode and worked examples —
and the study graded two of its patterns **Negative**. Lifting that pseudocode
would have reprinted, on paper, exactly the confusion the study corrects. Use
such documents for one thing only: what the industry calls the idea.

---

## 2. Pin the source and confirm it

```bash
git -C <repo> rev-parse --short HEAD
git -C <repo> log -1 --format=%cI
```

Match against the study's `repository_commit`. If they differ, either check out
the pinned commit or say plainly which commit the slips describe. Every
permalink you print must carry the full SHA, because `main` will move and a slip
on a wall lives for months.

If the repository is not available at all, stop and tell the user. The honest
alternatives — prose descriptions, ecosystem names — are worth much less, and
inventing a plausible specimen is the one unrecoverable failure here.

---

## 3. Harvest a concept

Work one concept at a time, end to end. For each, you need seven things.

### 3.1 The symbol

Start from the study's `file:line`, open it, and read the **whole function plus
its doc comment**. Doc comments in a well-kept repository carry more than the
code: the rejected alternative, the reason, and often a worked example you can
print verbatim. Two real examples from the PBUI run:

- `useAvailableApps`'s comment supplied the case *"a stage offering `["signin"]`
  inside an instance offering `["chart"]`"* — a better concrete example than
  anything composable from prose.
- `apply.ts`'s header comment supplied the trap — *"a mutation it accepts can
  still be 422'd by the server's validation pass"* — which became the briefing's
  TRAP section unchanged.

### 3.2 The specimen

Three to five lines that *are* the law. Choose the lines where the invariant is
enforced, not the signature:

```go
output := Clone(input)                      // why a failed batch is safe
for index, mutation := range mutations {    // why order matters
	applyMutation(output, mutation)
}
Validate(ctx, output, deps, limits)         // why checking is at the end
```

Read the **whole function first**, then extract. The setup lines (`const inStage
= ... new Set(...)`) are not the law; the filter that composes them is.

Rules: **tokens verbatim, layout yours.** Every identifier, operator and literal
exactly as in the source — but you may re-wrap a statement across lines to fit
~40 characters, and mark cuts `...`. Never rename an identifier to make it fit.
Three to five printed lines; if it takes more, you picked too much.

### 3.3 The observed behaviour

Prefer a test assertion — it is behaviour someone committed to keeping:

```bash
grep -rn "func Test.*<Symbol>" --include="*_test.go" <repo>          # Go
grep -rn "<Symbol>" --include="*.test.ts" --include="*.test.tsx" \
        --include="*.spec.ts" <repo>                                  # TypeScript
grep -rn "def test_.*<symbol>" --include="test_*.py" <repo>           # Python
```

If no test covers it, fall back to the doc comment's own worked example, and say
in `observed:` that it comes from the comment rather than from an assertion.

`TestFailedBatchDoesNotMutateInput` gave `document.Name` is still
`"Production"` — one concrete sentence that makes an abstract atomicity claim
checkable.

### 3.4 Who calls it

This is the step most likely to change what the slip says:

```bash
grep -rn "<Symbol>" --include="*.go" <repo>                    # note the quotes
grep -rn "<Symbol>" --include="*.go" <repo> | grep -v _test.go # real callers
```

In the PBUI run this turned up the single most useful fact on any slip:
`ApplyMutations` has **no non-test caller in the repository**. It is a library
entry point for a host server that lives elsewhere. An intern who does not know
that will search for the call site for an hour. Absence is a finding — print it.

> zsh expands a bare `--include=*.go` before grep sees it and the command fails
> with "no matches found". Always quote: `--include="*.go"`.

### 3.5 The limit

Take it from the study's **Limit:** line and sharpen it to one sentence with a
concrete substitution: "in-memory value atomicity, not storage atomicity",
"a placement is not a React mount". This is the payload of the whole exercise.

### 3.6 The discipline pair

Three things it **is**, three things it **is not**, as parallel short phrases so
they render as a two-column table. Derive the "is not" column from the study's
identity-discipline section (`X ≠ Y` lists) — that is what stops a reader
transplanting the law into a codebase where it does not hold.

### 3.7 The vocabulary triple

```yaml
local:     "ApplyMutations, Clone, Validate"      # what this repo calls it
proposed:  "graph batch transition"               # neutral name, the join key
elsewhere: "transaction, fold, batch apply"       # what the wild calls it
```

The middle row is what lets a reader match this concept against a different
codebase. It was the reason the card format was chosen over prettier ones.

---

## 4. Choose the form

| Signal | Form |
|---|---|
| "I want to study this / group concepts across codebases" | **card** |
| "explain it so someone new understands" | **briefing** |

A card is one law at a glance (~15cm). A briefing answers *why does this exist,
how does it work, who calls it, what will bite me* (~45cm). Estimate paper at
roughly **10px of strip per word**, plus block overhead; 384px wide, 203dpi, so
1150px ≈ 14.5cm. A 1000-word explanation printed raw is two metres — condensing
to ~400 words is not a nicety, it is the design.

### Card sections

`title → SYMBOLS table → law banner → DISCIPLINE (is/is not) table → vocabulary
kv → SIGHTED IN specimen → OBSERVED → limit`

### Briefing sections

Each is a label plus any of `text`, `code`, `kv`, `checks`:

1. **WHY IT EXISTS** — the problem in the user's terms, not the code's
2. **THE WHOLE FUNCTION** — the specimen, uncut if it is short enough
3. a **design-decision** section — why cloned first, why checked at the end
4. **TWO LAYERS / TABLE** — where a `kv` beats a paragraph
5. **WHO CALLS IT** — including "nobody here, and that is the design"
6. **TRAP** — the thing that will cost an afternoon
7. **IF YOU ADD/CHANGE ONE** — a `checks` list of the steps that keep it honest

---

## 5. Render, look, then print

```bash
scripts/render_slips.py --concepts <dir> --preview 03
scripts/render_slips.py --concepts <dir> --print 03
scripts/render_slips.py --concepts <dir> --form briefing --preview 03
```

**Always open the PNG.** Every formatting defect listed below was invisible in
the YAML and obvious in the preview:

| Symptom in the preview | Cause | Fix |
|---|---|---|
| code reflows into a paragraph | `\n` does not break inside a `text` block | one block per code line (the renderer does this) |
| `IF (!INSTAGE || INSTAGE.HAS(APP.ID))` | brutalist uppercases everything | `style: { textCase: none }` |
| a phonetic and an example you never wrote | the `word` block invents them | set `phonetic: ""`, `example: ""`, or avoid the block |
| checkbox text broken across the gutter | `checks` defaults to two columns | `columns: 1` |
| tofu boxes where `∩ ⊆ ⇀` should be | Archivo lacks the glyphs | `font: "'DejaVu Sans', sans-serif"` |
| a wall of shouting paragraphs | brutalist body case | prose mixed case, labels uppercase |

The remote service prints on the same LAN as the printer; a `status_code: 200`
per layout is the confirmation, and the script now echoes it.

### When a print fails

**A hang or timeout almost always means the printer is out of paper**, or is off
the network. The render service answers `{"ok":true}` either way — it cannot see
the paper. Measured failure modes from a three-agent test run:

| What you see | What it was | What to do |
|---|---|---|
| `context deadline exceeded (Client.Timeout ...)` | out of paper | reload paper, print once more |
| `/health` unreachable | service or LAN down | use the direct-IP fallback below |
| nothing prints, no error | the layout was written but `--print` not passed | re-run with `--print` |

**Never blind-retry.** Queued jobs land once paper returns, so every retry is
another physical copy — in the measured run, retries produced about ten copies of
one card. Diagnose, then print once.

Direct fallback when the remote service is down but the printer is reachable
(the `almanach-printing` skill covers setup, IP and BLE pairing):

```bash
almanach-render-service print --layout <layout>.yaml \
  --printer-ip 192.168.0.126 --feed-lines 8 \
  --web-dir ~/code/wesen/go-go-golems/almanach/web/dist
```

---

## 6. Keep the source of truth singular

One YAML per concept, both forms generated from it. A card and its briefing that
are written separately will disagree within a month, and the wall will teach the
disagreement. If a fact changes in the repo, edit the concept file and reprint —
never edit a generated layout.

Store concept files next to the study they belong to:

```text
Research/Software Architecture Garden/<project>/concepts/NN-<slug>.yaml
Research/Software Architecture Garden/<project>/concepts/layouts/   # generated
```

---

## 7. Offer styles before printing a set

Ticket layout is a matter of taste and the user is the one who will read it
daily. Print **one concept in four or five styles** and let them choose before
committing a whole set to paper. In the PBUI run the chosen style was neither
the densest nor the prettiest — it won because its IT IS / IT IS NOT table made
concepts groupable across codebases, which was the user's actual goal and was
not stated up front.
