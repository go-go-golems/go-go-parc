## Design policy (read before designing)
<!-- Insert into the common brief, before the constraints. Each rule answers one cause found in a baseline run; delete
     rules whose cause you did not observe, and add rules for new causes. Keep each rule one or two sentences. -->
{{ONE_SENTENCE_ON_WHAT_THE_DESIGN_IS_FOR}} Everything in the design should serve that purpose, and the simplest design that serves it is the right one.
- Design for valid inputs only. Choose input specifications that generate only valid inputs. On anything else the program may fail in whatever way the platform fails (trap, exception, arbitrary result). Do not define status codes, error precedence, or guarantees about state on error unless the problem itself has a natural failure result.
- Keep the input domain as narrow as the purpose allows. Restricting what is generated is preferable to code that handles more.
- For each significant design decision, name the simplest alternative that would serve and say in one or two sentences why you chose it or why it falls short. Prefer the simplest alternative unless it fails the purpose.
- Describe only what can be built with the current repository. Work that depends on features that do not exist yet gets one line each in a short "Later" list, with no test plan.
- {{PROJECT_SPECIFIC_RULE, e.g. "A specialization constant that is a single number is a scalar parameter."}}
- Mention only the related tickets or systems this design directly exercises, one line each.
- If the repository lacks a small piece of infrastructure the design needs, propose the change in a short section instead of designing around it.
- Before relying on a language, library or loader feature, run a minimal probe and state the result.
- Each section should be as long as an implementer needs and no longer. Target {{WORDS_LOW}} to {{WORDS_HIGH}} words. Leave out measurement methodology beyond the primary metric, alternate input profiles, and tests of the design's own guards.
- Work only from the files in your worktree. Do not read other git branches, other worktrees, or other agents' tickets.
