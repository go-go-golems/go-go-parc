# Judge rubric: {{ARTIFACT_KIND}} for {{PROJECT_PURPOSE_ONE_LINE}}

You are scoring {{ARTIFACT_KIND}}. Each describes one {{UNIT}} that {{WHAT_IT_IS_FOR}}. {{TWO_OR_THREE_SENTENCES_OF_CONTEXT_THE_JUDGE_NEEDS: the checking regime, limits, what "done" means}}. The purpose of each {{UNIT}} is given in `specs/`. The documents are meant to let an implementer build it.

Several documents may describe the same {{UNIT}}. Score each document on its own against its purpose, with the same standard for all. Use only the document's text. For every count, quote the passages you counted (short, verbatim quotes) so the count can be checked.

## Over-engineering items (counts)
<!-- Replace these with the families your baseline review found. Keep each one countable and quotable. -->
- **R1 invented error interface**: distinct error or status values beyond the results the algorithm naturally produces.
- **R2 state-on-error guarantees**: statements that guarantee state on error (nothing written before an error, unchanged inputs, a defined partial result).
- **R3 domain widening**: input features handled that the purpose does not need (one count per feature).
- **R4 self-guard tests**: planned tests of the design's own validation, guards or limits, rather than of its function or of the system under study.
- **R5 not-yet-existing features**: plans, tests or sections (beyond a one-line mention) that depend on features the document says do not exist yet.
- **R6 {{PROJECT_SPECIFIC_ITEM}}**: {{definition}}.
- **R7 infrastructure workaround**: does the document identify a small missing piece of infrastructure and design around it instead of proposing the change? yes/no with a quote.
- **R8 extra input configurations**: generated-input or test configurations beyond one default per entry point.
- **R9 other optional machinery**: optional components (extra oracles beyond two, generators, dispatchers, wrappers, alternate encodings, ceiling projects). One count per component.

## Fitness items (keep these: they catch a design that was simplified too far)
- **A1 implementability** (1–5): can a competent implementer build the core without guessing?
- **A2 independent check** (yes/no): is there a check of results that does not depend on the system under test?
- **A3 resource sizing** (yes/no): are inputs sized against the limits the system imposes ({{LIMIT}})?
- **A4 purpose value** (1–5): does the design still give {{WHAT_THE_UNIT_MUST_EXERCISE}} something real to work on?

## Overall
- **over_engineering** (0–10): 0 = nothing an implementer would cut, 10 = most of the document.
- **fitness** (0–10): how well the document serves its purpose.
- **justification**: one paragraph.

Return a JSON array, one object per document:
`{ "doc": "doc-X.md", "item": "<which spec>", "R1": n, "R1_quotes": [...], ..., "R7": "yes|no", "R7_quotes": [...], "A1": n, "A2": "yes|no", "A3": "yes|no", "A4": n, "over_engineering": n, "fitness": n, "justification": "..." }`
written to `scores.json` in the directory you were given.
