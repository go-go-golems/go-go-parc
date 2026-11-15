# Revision brief: chapters after the construction experiments (2026-11-14)

Agents built software from the chapters (three builds per chapter), and from the same tasks without the chapter (two
controls). Blind Opus reviewers judged all builds in the spirit of Alexander, Gabriel and Fowler. Result: chapter
builds resolve more forces and pass more hidden tests (98 % vs 88 %), but in four of six tasks the controls were
judged better adapted and more whole. Builders turned the Structure table into one module per row and copied details
of the originating projects from the sketches. Full numbers: `_validation/LOG.md`, step 9.

## Changes every chapter gets

Read `00-overview.md` first, especially "Roles, not modules" and "Pseudocode conventions".

1. **Structure table:** three columns, `Participant | Responsibility | Needed`. "Always" for the core; "only when …"
   with the condition under which the participant earns its place (concurrent callers, more than one consumer,
   agent code calling host objects, a cache shared between machines, ...). Keep the core small and honest.
2. **Sketch:** the shape only. Move anything specific to goja-cv, the Editor lab or the dust pipelines (a `require()`
   loader, receiver lookup, a JS-only translator, "decoded sources outside the cap", key salting, Go's `os.Root`
   naming) out of the sketch and into implementation notes or known uses, labelled. Numbers in a sketch are
   placeholders unless a note says where they were measured: say so next to them. Optional parts of the sketch are
   marked with a comment naming their condition.
3. **Variations:** the first one is **Smallest form**: which participants it keeps, what it gives up, when it is
   enough. Keep three or four variations in total.
4. **Applicability / Collaborations:** where a step is conditional, say so.
5. Keep the template sections and their order, the "Therefore:" paragraph standing alone, implementation notes at
   most 11 (merge to make room), Known uses real, claims about the originating projects true (check
   `/Users/manuel/code/wesen/go-go-golems/goja-cv` if unsure; never invent). Length within about 15 % of today's.
   Prose lines at most 120 characters. Plain prose, short sentences, no hype; bold leads on list items.
6. Lessons from the experiments may appear as implementation notes ("in construction experiments, builders who
   followed note 7 ..."), briefly; the chapter stays about the pattern, not about the experiment.

## Chapter-specific evidence

- Blind review (unblinded): `_validation/reviews/NN-o1.json` with `NN-o1-key.json` (which letter is a chapter build
  and which a control). `chapter_lessons`, per-implementation `worst_thing`, `forces_unnoticed`,
  `dead_or_ornamental` and `smells` are the material. Cited files live in
  `/Users/manuel/pattern-validation/reviews/NN/o1/work/impl-X/`; read them to check a claim before acting on it.
- Builders' own feedback: `_validation/builds/NN-*-build.json` (`chapter_feedback`), diaries `*-DIARY.md`.
- Apply a lesson when the evidence holds (a probe, a cited line you checked, or two builds showing it). Skip a lesson
  that is only one reviewer's taste, and say so in your report.

Do not edit any file except your chapter(s). Do not commit. Report: a list of changes (at most 15 lines), lessons you
skipped and why, and the word count before and after.
