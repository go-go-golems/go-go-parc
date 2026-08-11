---
name: concept-study-slips
description: Turns the mathematical or architectural foundations of a study into printable thermal slips — one concept per slip, each grounded in real code from the pinned repository. Produces concept YAML files as the source of truth plus two printed forms: a long intern briefing (why it exists, who calls it, what bites) and a short study card for a chalkboard. Use when asked to make study cards, concept tickets, chalkboard slips, or an intern briefing printout from an Architecture Garden entry, a design document, or a codebase.
---

# Concept Study Slips

## Purpose

Turn each foundation of a study into something a person can pin on a wall and
learn from. A slip is worth printing only when it carries a **law**, a **real
code specimen from the pinned repository**, and an explicit **limit** — what the
law does not say. Slips without a specimen become slogans; slips without a limit
become false confidence.

Read [the full playbook](references/PLAYBOOK.md) before the first slip of a new
project. Draft concept files from
[the template](references/CONCEPT-TEMPLATE.yaml). Render and print with
`scripts/render_slips.py`.

## The two forms

Both render from **one** concept YAML file, so they cannot drift apart. Both are
printed by default.

| Form | Length | For |
|---|---|---|
| **briefing** (primary) | ~45cm | understanding a concept you do not yet know — and handing to someone new |
| **card** | ~15cm | pinning on a chalkboard once you do; recognising the same shape in another codebase |

The briefing is the form people actually learn from. Do not skip it, and do not
treat the card as the deliverable on its own.

### The briefing's sections

Emit them in this order. The five marked **required** must be present; a
concept file whose briefing lacks one is incomplete.

| # | Label | Status | Content |
|---|---|---|---|
| 1 | `WHY IT EXISTS` | **required** | the problem in the user's terms, not the code's |
| 2 | `THE WHOLE FUNCTION` | **required** | the specimen, uncut if it is short enough |
| 3 | `A DESIGN DECISION` | optional | why it was built this way, what the alternative cost |
| 4 | *(a two-sided section)* | optional | where a `kv` beats a paragraph; name it for the content |
| 5 | `WHO CALLS IT` | **required** | including "nobody in this repo, and that is the design" |
| 6 | `TRAP` | **required** | the thing that will cost someone an afternoon |
| 7 | `IF YOU ADD ONE` | **required** | a `checks` list of the steps that keep it honest |

Add a section beyond these only when the content demands it; keep the required
five recognisable, because the point of a fixed shape is that a reader knows
where to look.

## Required qualities

A concept slip must:

1. carry one law, stated as a formula or a one-line rule — not a topic heading;
2. quote code that exists at the pinned commit, verified by opening the file,
   never paraphrased and never lifted from a hypothesis document;
3. cite `file:line` for every specimen, and a permalink pinned to the commit SHA;
4. state an observed behaviour, preferably a test assertion or a doc comment
   from the source itself;
5. state the limit — the substitution the law does *not* license;
6. name the vocabulary three ways: the project-local name, **exactly one**
   neutral pattern name, and what the idea is called elsewhere;
7. report absence honestly — "no non-test caller in this repository" is a
   finding, not a gap to paper over;
8. carry a briefing with the five required sections;
9. be previewed as a PNG and looked at before any paper is spent.

## Workflow

### 1. Find and pin the source

The study is a Markdown file; its frontmatter names the repository:

```bash
grep -m3 "^repository\|^repository_commit" <study>/README.md
git -C <repo> rev-parse --short HEAD    # must match repository_commit
```

If the repo is unavailable at that commit, stop and say so. A study README
names the API and gives `file:line`, but contains no code — the specimen cannot
be invented from prose.

**Naming.** `id` is the concept's position in the study's own numbering (its
`### N.` heading), two digits, unique within one study's `concepts/` directory —
take the next free number if the study does not number them. `slug` is the
kebab-case form of the concept name. `title` is the study's own term for the
concept, uppercased; do not coin a new name.

### 2. Harvest one concept at a time

Collect the fields in [the template](references/CONCEPT-TEMPLATE.yaml). The
playbook has the recipes; the two that matter most:

```bash
grep -rn "SymbolName" --include="*.go" <repo>          # quote the glob: zsh expands it
grep -rn "SymbolName" --include="*.go" <repo> | grep -v _test.go   # real callers
```

Read the **doc comment** above the symbol before writing anything. It routinely
contains the worked example, the rejected alternative, and the reason.

### 3. Render, look, then print

```bash
scripts/render_slips.py --concepts <dir> --preview 03   # PNG — open it
scripts/render_slips.py --concepts <dir> --print 03     # then spend paper
```

| Flag | Meaning |
|---|---|
| `--concepts DIR` | directory of concept YAML files; layouts land in `DIR/layouts/` (default: cwd) |
| positional ids | `03 05` — restrict to those concepts; omit to process **every** concept in the directory |
| `--form` | `both` (default), `briefing`, or `card` |
| `--preview` | render a local PNG per layout; always do this first |
| `--print` | send to the printer through the remote service |

Neither `--preview` nor `--print` is required; without them the script only
writes layout YAML.

## Printing troubleshooting

**A print that hangs or times out almost always means the printer is out of
paper, or is off the network.** The render service reports healthy either way —
it cannot see the paper.

```bash
curl -s -m 8 https://almanach.crib.scapegoat.dev/health   # {"ok":true,...}
```

**Never blind-retry a failed print.** A queued job can land later, so each retry
is another physical copy: one measured run produced about ten slips of the same
card from repeated attempts. Diagnose first — check paper, check the health
endpoint — then print once more.

If the remote service is unreachable but the printer is on the LAN, the direct
path is the fallback (see the `almanach-printing` skill for setup, IP, and BLE
pairing):

```bash
almanach-render-service print --layout <layout>.yaml \
  --printer-ip 192.168.0.126 --feed-lines 8 \
  --web-dir ~/code/wesen/go-go-golems/almanach/web/dist
```

## Content rules

- **Specimen: 3–5 lines that *are* the law.** Read the whole function first,
  then take the lines where the invariant is enforced — not the signature and
  not the local variable setup.
- **Tokens verbatim, layout yours.** Every identifier, operator and literal
  exactly as in the source; you may re-wrap a statement to fit the width and
  mark omissions `...`. Never rename anything to make a line fit.
- **Keep code lines ≤ ~40 characters** — the strip is 384px.
- **`title`** is the study's term, uppercase. **`vocabulary.proposed`** is
  exactly one name — it is the join key across codebases, and two names in it
  defeat the purpose.

## Printer constraints

The renderer already handles all of these; the list matters when you hand-write
a layout or extend the script.

- **`\n` does not break a line inside a `text` block.** One block per code line.
- **The `brutalist` theme uppercases everything.** Code, formulas, and briefing
  prose carry `style: { textCase: none }`; labels and headers stay uppercase.
- **Math glyphs need a font override.** `∩ ⊆ ⇒ ⇀` come from
  `'DejaVu Sans', sans-serif`, not the theme's Archivo.
- **The `word` block invents a phonetic and an example** when those fields are
  absent. Set them to `""` or avoid the block.
- **`checks` needs `columns: 1`** or items break across the column gutter.
- Work themes use `bodyScale: 1`; use `feedLines: 8` for tear-off paper.

## Anti-patterns

- Quoting pseudocode from a hypothesis document (a Pattern Zoo handbook, a
  design proposal) as if it were implementation evidence. If the study itself
  grades that document unreliable, it is not evidence.
- Renaming identifiers to make a line fit.
- Dropping the limit, or shipping a card without its briefing.
- Printing before previewing, or retrying a failed print before diagnosing it.
