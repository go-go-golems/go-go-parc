# Task: labelbook — a ledger for labels made by people, agents and detectors

Build `labelbook`, a Python 3 library (standard library only, no network, no pip installs). A team labels items
(images, text segments) with labels proposed by detectors, agents and people; reviewers accept, reject or correct them
over several rounds, and sometimes undo a decision. The team must be able to measure each source (how often its labels
are accepted), exclude everything one faulty source made, and audit any exported label. Apply the pattern described in
`CHAPTER.md`; this is the situation it is for.

Work only inside this directory. Write tests under `tests/` and run them (`python3 -m unittest discover -s tests`).
Keep `DIARY.md` as described in `DIARY-FORMAT.md`.

## Required public interface (other code will be tested against it)

Package `labelbook` (`labelbook/__init__.py` exports these names). Everything is stored under one directory as files
of JSON lines, so a new `Ledger` on the same directory sees the same state.

- `Ledger(directory)`.
- `ledger.add_label(item, label, maker, inputs=()) -> str`: records a proposed label for `item` and returns its id.
  `maker` is a dict with at least `kind` (`"person"`, `"agent"` or `"detector"`) plus identifiers such as `model`,
  `prompt`, `run`, `name`; `inputs` is a list of file paths the maker read.
- `ledger.decide(label_id, decision, actor, reason=None, new_label=None)`: `decision` is `"accept"`, `"reject"`,
  `"correct"` (with `new_label`) or `"undo"` (cancels the latest decision on that label). A missing `actor` is an error
  (`ValueError`).
- `ledger.state() -> dict`: label id → `{"item", "label", "status"}` where `status` is `"pending"`, `"accepted"`,
  `"rejected"` or `"corrected"`, and `label` is the current label (the corrected one, if corrected).
- `ledger.source_of(label_id) -> dict`: what made the label (its maker, inputs, time).
- `ledger.made_by(**query) -> list`: ids of labels whose maker matches every key of `query`.
- `ledger.acceptance(by) -> dict`: for each value of maker field `by`, the share of decided labels that were accepted
  or corrected (decided = accepted, corrected or rejected).
- `ledger.export(path)`: writes the accepted and corrected labels as a JSON list of `{"item", "label"}` to `path`.

When you are done, give a final message containing exactly one JSON object in a ```json fenced block:

```json
{
  "summary": "what you built, in three sentences",
  "files": ["paths you created"],
  "pattern_mapping": {"<participant from CHAPTER.md>": "where it is in your code"},
  "notes_applied": ["implementation notes from CHAPTER.md you applied, and how"],
  "tests": "how many tests you wrote, and the last result",
  "chapter_feedback": ["where the chapter helped, misled you or left you to guess"]
}
```
