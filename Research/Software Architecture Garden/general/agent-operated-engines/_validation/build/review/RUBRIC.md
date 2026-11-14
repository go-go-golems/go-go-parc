# Design review: did the pattern generate living structure?

You are reviewing several implementations of the same task, written independently by different engineers. Some read
the pattern chapter (`CHAPTER.md`) before building, some did not; you are not told which, and guessing is not part of
the job. Judge each implementation as code that people will live in and change, using the chapter as the yardstick
for which forces matter in this problem.

Pass rates say whether code works. This review asks something else, in the spirit of three writers on design:

- **Christopher Alexander** judged a design by whether it resolves the forces of its situation, whether its structure
  is adapted to the place rather than copied, and whether every part serves the whole. A pattern is generative: used
  well, it produces similar deep structure that differs in every detail.
- **Richard Gabriel** asked whether software is *habitable* (people can understand it and change it comfortably), and
  whether it grows piecemeal (each new need is a local change). He also observed that the simpler design often wins
  ("worse is better"): a pattern that adds machinery the situation does not need is teaching too much.
- **Martin Fowler** named concrete *smells*: duplicated knowledge, long functions, primitive obsession (ids or
  structured data as concatenated strings), shotgun surgery (one change touches many places), speculative generality
  (abstractions without a second user), data clumps, feature envy.

## What to do

1. Read `TASK.md` (the problem) and `CHAPTER.md` (the forces and the pattern), then every implementation directory
   (`impl-*`). Read the code, the tests, and any notes. Ignore whether you would have written it the same way.
2. Then take the **next change** in `NEXT.md` and, for each implementation, work out which files and functions it
   would touch. Do not write it; trace it.
3. Answer in the format below. Cite evidence as `impl-X/path:line` wherever you can; a claim without a place is worth
   little. Be concrete and short; no praise.

## The lenses (score each 1–5; 5 is best)

| Lens | Question |
| --- | --- |
| **forces** | Which of the chapter's forces does the code resolve (the trade-off is visible in the code, not only in comments), which are left in tension, which were never noticed? |
| **adapted** | Is the structure shaped by this task (names and parts from its domain), or a transcription of a generic sketch, with participants this task does not need? (5 = fully adapted) |
| **wholeness** | Does every part serve the whole? Count dead code, unused abstractions, ornamental layers, pattern parts with no caller. (5 = nothing dead) |
| **habitability** | Could a newcomer find where things happen and change them comfortably? Size of units, names, locality, density; neither over-compressed nor over-abstracted. |
| **growth** | For the next change in `NEXT.md`: is it a local addition, or does it touch many places? (5 = one place, no edits to the core) |
| **smells** | Fowler's smells, each with a place. (5 = none worth naming) |
| **tests** | Do the tests state the forces as laws (properties, invariants, negative controls), or only examples? |

## Across implementations

- **generativity:** which seams and participants recur across implementations (name them, and which implementations
  share them), and where do they differ in detail? Do the implementations fall into groups?
- **worse_is_better:** is there a simpler implementation that reaches the same quality with less? Name it and say what
  the others carry that it does without, and whether that extra is needed by the task.
- **chapter_lessons:** judging only from what you see in the code, what should the chapter say differently: a force
  the code shows is missing, a part the code shows is unnecessary, a trap several fell into.

## Output

Your final message must contain exactly one JSON object in a ```json fenced block:

```json
{
  "implementations": {
    "A": {
      "summary": "what this implementation is, structurally, in two sentences",
      "scores": {"forces": 0, "adapted": 0, "wholeness": 0, "habitability": 0, "growth": 0, "smells": 0, "tests": 0},
      "forces_resolved": ["force: how, with impl-A/path:line"],
      "forces_in_tension": ["force: what is unresolved, where"],
      "forces_unnoticed": ["force the chapter names that the code never addresses"],
      "dead_or_ornamental": ["impl-A/path:line: what and why"],
      "next_change_touches": ["impl-A/path: function, what changes"],
      "smells": [{"smell": "name", "where": "impl-A/path:line", "why": "one line"}],
      "best_thing": "the one decision a newcomer should copy",
      "worst_thing": "the one decision that will hurt first"
    }
  },
  "generativity": {"shared_seams": [{"seam": "name", "in": ["A", "C"]}], "groups": [["A", "C"], ["B"]], "notes": ""},
  "worse_is_better": "",
  "ranking": ["best first"],
  "chapter_lessons": [""]
}
```
