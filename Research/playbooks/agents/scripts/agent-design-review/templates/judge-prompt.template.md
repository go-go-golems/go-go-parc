Score {{N}} documents against a rubric. Work only from the files in {{JUDGE_DIR}}. Do not open any other files or repositories, and do not search for where the documents came from.

That directory contains:
- `RUBRIC.md`: the scoring rubric and output format. Read it first and follow it exactly.
- `specs/`: the purpose of each {{UNIT}}. Several documents may describe the same one.
- `docs/doc-A.md` …: the documents.

Read every document in full. For every count, quote the passages you counted. Before you finish, check by script that every quote occurs verbatim in its document (ignoring whitespace) and fix any that do not. Apply the same conventions to all documents and state them.

Write the JSON array to {{JUDGE_DIR}}/scores.json. Reply with a compact table (doc, item, every R and A item, over_engineering, fitness), your counting conventions, and one sentence on each document you found hard to score.
