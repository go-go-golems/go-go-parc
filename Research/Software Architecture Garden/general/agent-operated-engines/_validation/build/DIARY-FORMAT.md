# How to keep DIARY.md (strict format)

Keep a diary in `DIARY.md` while you work: one step per phase of work (reading and design, each part you build,
testing, each fix after a failing test, the final check). Write each step when you finish that phase, not all at the
end. Record failures as they happen, with the exact command and error text.

```markdown
# Diary

## Goal

One or two sentences: what you are building and what this diary records.

## Step N: <descriptive step name>

One or two short paragraphs of prose (required): what you set out to do in this step, what changed, what it unlocked.

### Prompt Context

**User prompt (verbatim):** "<the exact request text, the first time it appears; later steps: (see Step 1)>"

**Assistant interpretation:** <your paraphrase of what is being asked>

**Inferred user intent:** <the outcome the requester wants>

### What I did
- Concrete actions: files created or changed, commands run.

### Why
- The reason for this design or change; name the CHAPTER.md section or implementation note that drove it.

### What worked
- Outcomes that moved the work forward.

### What didn't work
- Failures, with the exact command and the exact error text.

### What I learned
- Insights and corrected assumptions, including where CHAPTER.md helped or misled you.

### What was tricky to build
- The underlying cause, the symptoms you saw, and how you solved it (the exact steps).

### What warrants a second pair of eyes
- Correctness risks a reviewer should check.

### What should be done in the future
- Follow-ups implied by this step, or `N/A`.

### Code review instructions
- Where to start (files and key functions) and how to validate (commands, tests).
```
