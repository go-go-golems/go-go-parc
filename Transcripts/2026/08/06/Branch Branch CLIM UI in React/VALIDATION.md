# Validation report

## Artifact structure

The package contains:

- one complete Markdown textbook;
- one course/study guide;
- one repository-specific PBUI integration map;
- one formal-results and proof-status index;
- one BibTeX bibliography;
- one dependency-free TypeScript reference kernel;
- one executable law suite;
- precompiled JavaScript and TypeScript declarations.

## Textbook checks

The final textbook contains:

- 30 numbered chapters;
- five appendices;
- 30 exercise sections;
- approximately 187 individual exercise prompts;
- more than 40,000 whitespace-delimited words;
- 41 bibliography entries used in the text;
- definitions, inference rules, propositions, theorems, paper proofs, and proof sketches;
- explicit sections on what can be omitted and alternative designs.

Automated structural checks verified:

- balanced Markdown code fences;
- balanced display-mathematics delimiters;
- a complete 1–30 chapter sequence;
- a complete Appendix A–E sequence;
- no empty Markdown links;
- no unfinished-work or missing-citation markers;
- no non-whitespace control characters;
- every bibliography citation key resolves to a bibliography entry;
- every bibliography entry is cited at least once.

## Companion checks

The TypeScript companion is compiled with strict settings, including:

- `strict`;
- `noUncheckedIndexedAccess`;
- `exactOptionalPropertyTypes`;
- `noImplicitOverride`;
- declaration and source-map output.

The command below completed successfully:

```bash
cd companion
npm run verify
```

It rebuilds the kernel and executes the law suite. The final test output is:

```text
semantic-interfaces reference kernel: all executable laws passed
```

## Proof status

The textbook's ordinary paper proofs and proof sketches were reviewed against their stated assumptions. They are not machine-checked. The executable law suite tests representative finite instances and is not a substitute for universal proof.

Appendix C and `FORMAL_RESULTS_INDEX.md` identify a concrete mechanization sequence for Lean, Coq, Agda, or Isabelle/HOL.
