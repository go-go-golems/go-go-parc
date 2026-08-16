---
title: publish-vault — Index of Design Patterns (Rationale)
aliases:
  - publish-vault index rationale
  - why each publish-vault index term belongs
status: active
type: architecture-garden-index-rationale
created: 2026-08-16
analyzed: 2026-08-16
analysis_schema: architecture-garden-v1
repository: /home/manuel/workspaces/2026-08-09/publish-vault-mathjax/publish-vault
repository_commit: e02b73d4a19d82a63abb7f0a1a85299e19d5bc7d
derived_from: Research/Software Architecture Garden/publish-vault/README.md
tags:
  - architecture-garden
  - publish-vault
  - design-pattern-index
  - rationale
related_notes:
  - "[[Research/Software Architecture Garden/publish-vault/README]]"
  - "[[Research/Software Architecture Garden/publish-vault/Index of Design Patterns]]"
  - "[[Research/Software Architecture Garden/README]]"
---

# publish-vault — Index of Design Patterns (Rationale)

This is the editorial rationale for the [[Research/Software Architecture Garden/publish-vault/Index of Design Patterns|publish-vault index]]. It explains why each canonical concept belongs, what evidence grounds it, and what distinction or operational consequence would be lost if it were omitted. It is not a second architecture study.

The index spans the original July study (`560e71d`) and the newer parser pattern entry (`e02b73d`). The newer source commit in this file records the latest evidence boundary; older sections retain their own pinned provenance.

## Principles of selection

1. **Index protected invariants.** Load/read separation, atomic swap, occurrence preservation, ambiguity, and resolve-before-render belong because they state laws rather than file shapes.
2. **Index conflations that caused or can cause failures.** An occurrence is not an edge; discovery order is not identity; HTML is not an IR; a runtime snapshot is not automatically a release.
3. **Index operations readers arrive wanting to perform.** Reloading safely, resolving references, publishing images, gating content, and finding parser failures need direct access paths.
4. **Index debt and open obligations honestly.** Frontmatter disagreement, static graph divergence, repo-root drift, `@main` workflow risk, and implicit trust are as searchable as successful patterns.
5. **Point outward without flattening.** Cross-Garden correspondences use the same canonical vocabulary while stating why note links, commands, receipts, evidence occurrences, and authorization remain different objects.

## What was deliberately excluded

- Routine goldmark/GFM features (tables, task lists, footnotes) are capabilities, not project-specific patterns.
- Individual API routes and CLI flags are omitted unless they instantiate a security or lifecycle boundary.
- Math delimiter details remain in parser documentation; the Garden contribution is parser-owned context, not a math grammar.
- Every deployment environment variable and Docker layer is omitted; the durable concepts are sidecar ownership, image coordination, GitOps declaration, and shared workflow risk.
- Temporary implementation names without identity or policy weight are kept in the notation table rather than the alphabetic index.

## Per-term rationale

### Ambiguity-preserving reference resolution — Pattern
> Index entry: [[Index of Design Patterns#Ambiguity-preserving reference resolution]].

Chosen because the current first-wins suffix index is populated from Go map iteration, making ambiguity a concrete correctness issue. It belongs because an explicit candidate-set result generalizes to commands and evidence binding while preventing discovery order from masquerading as identity.

### Atomic snapshot swap — Pattern
> Index entry: [[Index of Design Patterns#Atomic snapshot swap]].

Chosen because build-then-swap and delayed cleanup are the runtime's strongest established structure. It belongs because it explains both availability during reload and failure atomicity; omitting it reduces the runtime to a note map description.

### Admin reload, token-or-loopback — Pattern
> Index entry: [[Index of Design Patterns#Admin reload, token-or-loopback]].

Chosen because it names a reusable security boundary with two deployment modes and a disabled default. It belongs because same-host automation and remote administration require different proofs of caller locality/authority.

### Backlink graph projection — Pattern
> Index entry: [[Index of Design Patterns#Backlink graph projection]].

Chosen because PR #20 proved graph data can diverge from rendered syntax. It belongs to preserve the rule that backlinks are consumer-derived edges, not the parser's authored occurrence list.

### Comparison principle — Garden law
> Index entry: [[Index of Design Patterns#Comparison principle]].

Chosen because document 04's candidates only become guidance through cross-project invariant comparison. It belongs as the maturity discipline governing every pattern bracket in the index.

### Configuration, vault-scoped (absent) — Debt
> Index entry: [[Index of Design Patterns#Configuration, vault-scoped (absent)]].

Chosen because publishing policy does not travel with the vault except through special files. It belongs because the absence is an operational design limit, not a missing convenience.

### Delayed old-snapshot cleanup — Pattern detail
> Index entry: [[Index of Design Patterns#Delayed old-snapshot cleanup]].

Chosen because the grace period is what lets in-flight references to the prior epoch finish. It belongs separately from swap so readers searching for resource-lifetime behavior find it directly.

### Deterministic resolution — Law
> Index entry: [[Index of Design Patterns#Deterministic resolution]].

Chosen because map-order independence is a testable property. It belongs to distinguish deterministic output from an arbitrary deterministic tie-break: ambiguity remains ambiguity even after sorting.

### Embedded SPA, build-tag controlled — Pattern
> Index entry: [[Index of Design Patterns#Embedded SPA, build-tag controlled]].

Chosen because it recurs across the ecosystem and now has at least three Garden occurrences. It belongs as the reusable build/runtime boundary between production single-artifact delivery and development disk serving.

### Endpoint-level exclusion recheck — Security pattern
> Index entry: [[Index of Design Patterns#Endpoint-level exclusion recheck]].

Chosen because direct filesystem endpoints bypass the post-filter note map. It belongs to keep the exception attached to the choke-point law: bypassing the collection requires reapplying policy.

### Frontmatter, single structural split — Open obligation
> Index entry: [[Index of Design Patterns#Frontmatter, single structural split]].

Chosen because the ticket probe demonstrated valid metadata mutation. It belongs because a reader debugging YAML corruption will remember frontmatter, not the names of two splitter functions.

### GitOps target declaration — Pattern
> Index entry: [[Index of Design Patterns#GitOps target declaration]].

Chosen because it is the machine-readable bridge from image publication to a reviewable cluster PR. It belongs because the declaration, workflow, and sidecar topology are distinct concepts that should not be collapsed.

### HTML placeholder protocol — Debt/emergent mechanism
> Index entry: [[Index of Design Patterns#HTML placeholder protocol]].

Chosen because documents 03 and 05 trace its evolution from pragmatic workaround to architecture debt. It belongs because fixed-order `data-*` transport is the mechanism readers must locate before replacing regex passes.

### Ignore matcher, documented subset — Emergent limit
> Index entry: [[Index of Design Patterns#Ignore matcher, documented subset]].

Chosen because its semantics couple negation to directory pruning and explicitly omit common gitignore features. It belongs as a known limit that should not be repeated in new projects.

### Immutable parser output for rebuild — Established local law
> Index entry: [[Index of Design Patterns#Immutable parser output for rebuild]].

Chosen because reload reversibility is already correctly implemented. It belongs to prevent a typed refactor from accidentally re-resolving previously resolved HTML.

### Load-once, read-snapshot execution — Pattern
> Index entry: [[Index of Design Patterns#Load-once, read-snapshot execution]].

Chosen because it is the runtime's organizing principle and first ecosystem candidate. It belongs because every new expensive feature must decide whether it runs at load or request time.

### Node SSR sidecar — Pattern
> Index entry: [[Index of Design Patterns#Node SSR sidecar]].

Chosen because it separates JavaScript rendering from Go API/static ownership with graceful fallback. It belongs because it is reusable only where SSR is required; the applicability condition matters.

### Occurrence preservation — Pattern
> Index entry: [[Index of Design Patterns#Occurrence preservation]].

Chosen because early deduplication demonstrably erases headings and link/embed distinctions. It belongs because authored occurrences, graph edges, and content identity need different equivalence relations.

### Parser-owned structural context — Pattern
> Index entry: [[Index of Design Patterns#Parser-owned structural context]].

Chosen because recent parser bugs all arise from independent passes disagreeing about source context. It belongs as the primary law behind using goldmark extension points instead of reconstructing CommonMark boundaries.

### Plain-text projection — Proposed pattern
> Index entry: [[Index of Design Patterns#Plain-text projection]].

Chosen because search/excerpt regex stripping is a second Markdown interpretation. It belongs to show that typed parsing benefits outputs beyond HTML and graphs.

### Protected-region law — Law
> Index entry: [[Index of Design Patterns#Protected-region law]].

Chosen because it gives parser-owned context a formal invariant. It belongs so readers searching for the preservation property, not the architecture name, have an access path.

### Publication choke-point — Pattern
> Index entry: [[Index of Design Patterns#Publication choke-point]].

Chosen because one post-filter collection makes exclusion propagate to API, tree, search, and graph. It belongs as the strongest local ownership boundary and must remain distinct from authorization.

### Reload reversibility — Law
> Index entry: [[Index of Design Patterns#Reload reversibility]].

Chosen because target removal/restoration tests prove the requirement. It belongs because atomic snapshot replacement and reference re-resolution protect related but different forms of reversibility.

### Repo-root discovery drift — Debt
> Index entry: [[Index of Design Patterns#Repo-root discovery drift]].

Chosen because one copied sentinel names a directory layout that does not exist. It belongs as a concrete copy-without-verification failure, not generic code cleanup.

### Reusable release workflow — Pattern
> Index entry: [[Index of Design Patterns#Reusable release workflow]].

Chosen because shared infrastructure owns release behavior across repositories. It belongs with its version risk so centralization is not presented as cost-free.

### Shared-workflow version risk — Open obligation
> Index entry: [[Index of Design Patterns#Shared-workflow version risk]].

Chosen because `@main` coordinates upgrades and blast radius simultaneously. It belongs as the negative space of reusable workflow inheritance.

### Short-path wiki-link index — Emergent mechanism
> Index entry: [[Index of Design Patterns#Short-path wiki-link index]].

Chosen because progressive suffixes enable Obsidian convenience and create the ambiguous namespace. It belongs as the concrete mechanism beneath ambiguity-preserving resolution.

### Source spans — Proposed vocabulary
> Index entry: [[Index of Design Patterns#Source spans]].

Chosen because diagnostics and occurrence-preserving consumers need authored coordinates. It belongs as a durable IR field rather than a line-number implementation detail.

### Static renderer conformance — Proposed pattern
> Index entry: [[Index of Design Patterns#Static renderer conformance]].

Chosen because Go and TypeScript already disagree despite each using a parser for rendering. It belongs as the practical cross-runtime solution: shared semantic fixtures rather than one generated parser.

### Static graph divergence — Debt
> Index entry: [[Index of Design Patterns#Static graph divergence]].

Chosen because the marked extension and raw graph regex make HTML and backlinks disagree. It belongs as a named failure mode readers will search while debugging static builds.

### Symlink-resolved vault root — Established mechanism
> Index entry: [[Index of Design Patterns#Symlink-resolved vault root]].

Chosen because it binds a snapshot to one concrete git-sync checkout. It belongs as the filesystem identity mechanism behind atomic runtime epochs.

### Trust mode, explicit — Open design decision
> Index entry: [[Index of Design Patterns#Trust mode, explicit]].

Chosen because aliases/raw HTML currently inherit trust implicitly from `WithUnsafe`. It belongs because a reusable parser needs an explicit security contract even if publish-vault keeps trusted-vault mode.

### Two images, one release coordinate — Emergent pattern
> Index entry: [[Index of Design Patterns#Two images, one release coordinate]].

Chosen because app/SSR version skew is a named risk in an otherwise coordinated release. It belongs to distinguish two-image topology from GitOps declaration and shared workflow.

### Typed reference pipeline — Pattern
> Index entry: [[Index of Design Patterns#Typed reference pipeline]].

Chosen because parse → resolve → render is the integrated target architecture. It belongs as the canonical entry for readers remembering “HTML should not be the IR” or “resolve before rendering.”

### Widget DSL sibling-module workaround — Emergent/debt
> Index entry: [[Index of Design Patterns#Widget DSL sibling-module workaround]].

Chosen because it documents cross-project contract reuse without a shared package and a named graduation path. It belongs as an honest migration boundary, not as a promoted ecosystem rule.

## Reader-situation test

1. *“How do reloads avoid showing half-built state?”* → [[Index of Design Patterns#Atomic snapshot swap]].
2. *“Why is the old search index kept around?”* → [[Index of Design Patterns#Delayed old-snapshot cleanup]].
3. *“Where is the rule that expensive parsing cannot happen per request?”* → [[Index of Design Patterns#Load-once, read-snapshot execution]].
4. *“What makes ignored notes disappear everywhere?”* → [[Index of Design Patterns#Publication choke-point]].
5. *“What if an endpoint reads disk directly?”* → [[Index of Design Patterns#Endpoint-level exclusion recheck]].
6. *“Why did a code sample create a backlink?”* → [[Index of Design Patterns#Code samples create backlinks]] → [[Index of Design Patterns#Parser-owned structural context]].
7. *“There were two links to different headings but only one API entry.”* → [[Index of Design Patterns#Occurrence preservation]].
8. *“A backlink is not the same thing as source syntax.”* → [[Index of Design Patterns#Graph edge is not occurrence]] → [[Index of Design Patterns#Backlink graph projection]].
9. *“Why can `[[Index]]` choose a different note?”* → [[Index of Design Patterns#First note wins]] → [[Index of Design Patterns#Ambiguity-preserving reference resolution]].
10. *“Where is the phrase discovery order is not identity?”* → [[Index of Design Patterns#Discovery order is not identity]].
11. *“Why should link state not travel through `data-*`?”* → [[Index of Design Patterns#HTML is not an internal representation]] → [[Index of Design Patterns#Typed reference pipeline]].
12. *“Which frontmatter bug injected anchors into YAML?”* → [[Index of Design Patterns#Frontmatter, single structural split]].
13. *“How do Go and static TypeScript stay semantically aligned?”* → [[Index of Design Patterns#Static renderer conformance]].
14. *“What is currently wrong with the static backlink graph?”* → [[Index of Design Patterns#Static graph divergence]].
15. *“What does `SourceDocument` mean?”* → [[Index of Design Patterns#Identity strings, schemas, and operational handles]].
16. *“How is the React frontend inside the Go binary?”* → [[Index of Design Patterns#Embedded SPA, build-tag controlled]].
17. *“Why are there two production images?”* → [[Index of Design Patterns#Two images, one release coordinate]].
18. *“How does release automation know which manifest to edit?”* → [[Index of Design Patterns#GitOps target declaration]].
19. *“What risk comes from the shared workflow using `@main`?”* → [[Index of Design Patterns#Shared-workflow version risk]].
20. *“What is the known ceiling of `.vault-ignore`?”* → [[Index of Design Patterns#Ignore matcher, documented subset]].
21. *“Why does the runtime resolve the git-sync symlink?”* → [[Index of Design Patterns#Symlink-resolved vault root]].
22. *“Is wiki alias HTML trusted or escaped?”* → [[Index of Design Patterns#Trust mode, explicit]].
23. *“What is the old regex approach called?”* → [[Index of Design Patterns#Wiki-link placeholder approach]] → [[Index of Design Patterns#HTML placeholder protocol]].
24. *“Which project-local workaround awaits an upstream namespace?”* → [[Index of Design Patterns#Widget DSL sibling-module workaround]].

## How the index should grow

Add entries when a new study section establishes a reusable invariant, a named failure mode, an operational procedure, or a durable handle. Add `See` redirects when review reveals how readers actually ask for an existing concept. Do not add every parser feature or deployment flag. Re-run the link validator and reader-situation test after every structural update.

## Related documents

- [[Research/Software Architecture Garden/publish-vault/Index of Design Patterns|Index of Design Patterns]]
- [[Research/Software Architecture Garden/publish-vault/README|Architecture Garden — publish-vault]]
- [[Research/playbooks/creating-an-index|Index playbook]]
