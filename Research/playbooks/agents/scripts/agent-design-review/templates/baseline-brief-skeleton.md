<!-- common.md for the baseline round. Keep it neutral: no simplicity instructions, so the baseline measures the
     model's own tendency. Name skills deliberately (naming two excludes the rest). Every item listed here will be
     covered at full depth, so list only what you want. "<ID>" is replaced by the item. -->
You are working in a git worktree of {{REPO_DESCRIPTION}}. Your task: create a docmgr ticket <ID> and write a design document for ONE {{UNIT}}, described below. Do not implement it. Stop after the design document is written and committed.

## Read first
- {{FILES_AND_DIRECTORIES_THAT_DEFINE_THE_CONTEXT}}
- {{HOW_RESULTS_ARE_CHECKED_AND_MEASURED}}

## Ticket and documents
- Create the ticket with `docmgr ticket create-ticket --ticket <ID> --title "<title>" --topics {{TOPICS}}`; add the design doc with `docmgr doc add --ticket <ID> --doc-type design-doc --title "<title>"`.
- Keep a short diary in the ticket's `log/`.
- Put every probe, prototype and temporary program you write in the ticket's `scripts/` directory, numbered in the order you write them (`01-name.mjs`), and commit them, so that every result in your documents can be rerun. Nothing you ran should exist only in a scratch directory or a one-off command.
- The design document should let a new intern implement the {{UNIT}}: {{SECTIONS_YOU_WANT}}.

## Constraints
- Write only inside your ticket directory. Do not modify {{PROTECTED_PATHS}}.
- When done, commit only your ticket directory with the message `<ID>: ticket and design doc for <name>`. Do not push.
- Final message: the design doc's path, the ticket path, the commit hash, and a one-paragraph summary.
