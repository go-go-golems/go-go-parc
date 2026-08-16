---
title: publish-vault — Index of Design Patterns
aliases:
  - publish-vault design pattern index
  - publish-vault glossary
status: active
type: architecture-garden-index
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
  - markdown
  - snapshots
  - gitops
related_notes:
  - "[[Research/Software Architecture Garden/publish-vault/README]]"
  - "[[Research/Software Architecture Garden/publish-vault/Index of Design Patterns - Rationale]]"
  - "[[Research/Software Architecture Garden/README]]"
---

# publish-vault — Index of Design Patterns

This is the back-of-the-book index for the [[Research/Software Architecture Garden/publish-vault/README|publish-vault architecture study]]. It indexes the runtime/snapshot model, publication boundary, deployment topology, architecture debt, ecosystem candidates, and the later parser/reference-resolution study.

## How to read this index

- **§1** links into [[Research/Software Architecture Garden/publish-vault/01 - Project Architecture Overview|Project Architecture Overview]].
- **§2** links into [[Research/Software Architecture Garden/publish-vault/02 - Deployment and Release Topology|Deployment and Release Topology]].
- **§3** links into [[Research/Software Architecture Garden/publish-vault/03 - Patterns Limits and Architecture Debt|Patterns, Limits, and Architecture Debt]].
- **§4** links into [[Research/Software Architecture Garden/publish-vault/04 - Candidate Ecosystem Guidelines|Candidate Ecosystem Guidelines]].
- **§5** links into [[Research/Software Architecture Garden/publish-vault/05 - Parser-Owned Structure and Typed Reference Resolution|Parser-Owned Structure and Typed Reference Resolution]].
- `See` redirects alternate reader-memory phrasings to a canonical entry. `see also` connects related concepts that must remain distinct.
- Brackets carry the Garden maturity or the current pattern-entry maturity.
- Versioned handles and closed vocabularies are in [[#Identity strings, schemas, and operational handles]].

## A

### Ambiguity-preserving reference resolution

A reference key denotes a candidate set: zero is unresolved, one is resolved, and more than one is ambiguous; discovery order is never identity. [Candidate / Documented] [[Research/Software Architecture Garden/publish-vault/05 - Parser-Owned Structure and Typed Reference Resolution#Law 3: ambiguity is a resolution result|§5.3]]. ↳ [[Research/Software Architecture Garden/devctl/05 - Declarative Plugins and Validated Dynamic Commands|devctl qualified ambiguity]]. *see also* [[#Short-path wiki-link index]], [[#Deterministic resolution]], [[#Typed reference pipeline]].

### Atomic snapshot swap

Build a complete replacement snapshot, swap it under one lock, and leave the old snapshot alive long enough for in-flight readers. [Candidate ecosystem pattern] [[Research/Software Architecture Garden/publish-vault/01 - Project Architecture Overview#The atomic snapshot model|§1.4]], [[Research/Software Architecture Garden/publish-vault/04 - Candidate Ecosystem Guidelines#Candidate 3: Atomic snapshot swap with delayed old-snapshot cleanup|§4.3]]. *see also* [[#Build-then-swap]], [[#Delayed old-snapshot cleanup]], [[#Reload reversibility]].

### Admin reload, token-or-loopback

A disabled-by-default administrative endpoint accepts either a remote bearer token or an explicitly enabled loopback caller. [Candidate ecosystem pattern] [[Research/Software Architecture Garden/publish-vault/01 - Project Architecture Overview#The admin reload endpoint|§1.8]], [[Research/Software Architecture Garden/publish-vault/04 - Candidate Ecosystem Guidelines#Candidate 6: Reload endpoint with two-mode authentication|§4.6]].

## B

### Backlink graph projection

Backlinks are a deduplicated consumer projection over resolved authored link occurrences, not the parser's occurrence model. [Candidate / Documented] [[Research/Software Architecture Garden/publish-vault/01 - Project Architecture Overview#Wiki-link resolution and backlinks|§1.3]], [[Research/Software Architecture Garden/publish-vault/05 - Parser-Owned Structure and Typed Reference Resolution#Law 2: preserve occurrences; derive edges|§5.2]]. *see also* [[#Occurrence preservation]], [[#Graph edge is not occurrence]].

### Build-then-swap

*See* [[#Atomic snapshot swap]].

## C

### Code samples create backlinks

*See* [[#Parser-owned structural context]]. (This was the invisible graph consequence of pre-pass substitution inside code.)

### Comparison principle

Similar code is not a shared pattern unless projects protect the same invariant under the same constraint. [[Research/Software Architecture Garden/publish-vault/04 - Candidate Ecosystem Guidelines#The comparison principle|§4.0]]. ↳ [[Research/Software Architecture Garden/README#How patterns become ecosystem guidelines|Garden promotion path]].

### Configuration, vault-scoped (absent)

No general version-controlled vault configuration travels with Markdown and attachments; CLI/environment configuration remains deployment-local. [Architecture debt] [[Research/Software Architecture Garden/publish-vault/03 - Patterns Limits and Architecture Debt#The absence of a general vault-scoped config file|§3.2]].

## D

### Delayed old-snapshot cleanup

Old search/vault resources close after a grace period so requests holding the previous epoch can finish. [Candidate ecosystem pattern] [[Research/Software Architecture Garden/publish-vault/01 - Project Architecture Overview#The atomic snapshot model|§1.4]], [[#Atomic snapshot swap]].

### Deterministic resolution

Resolution results must be invariant under document load order; sorting candidates does not make an ambiguous first candidate correct. [Candidate / Documented] [[Research/Software Architecture Garden/publish-vault/05 - Parser-Owned Structure and Typed Reference Resolution#Law 3: ambiguity is a resolution result|§5.3]]. *see also* [[#Ambiguity-preserving reference resolution]].

### Discovery order is not identity

*See* [[#Ambiguity-preserving reference resolution]].

## E

### Embedded SPA, build-tag controlled

An `embed` production build serves the built frontend from the Go binary while a `!embed` development build serves files from disk. [Candidate ecosystem pattern] [[Research/Software Architecture Garden/publish-vault/02 - Deployment and Release Topology#The build command and the embedded-SPA pattern|§2.5]], [[Research/Software Architecture Garden/publish-vault/04 - Candidate Ecosystem Guidelines#Candidate 4: Embedded SPA with build-tag-controlled embedding|§4.4]]. ↳ [[Research/Software Architecture Garden/go-go-datadrop/09 - Candidate Ecosystem Guidelines|third Garden occurrence]].

### Endpoint-level exclusion recheck

A consumer that bypasses the post-filter note map and reads disk directly must reapply exclusion at read time. [Candidate ecosystem pattern] [[Research/Software Architecture Garden/publish-vault/01 - Project Architecture Overview#The HTTP API and endpoint-level safety|§1.7]], [[Research/Software Architecture Garden/publish-vault/04 - Candidate Ecosystem Guidelines#Candidate 2: Single choke-point collection with load-time gating|§4.2]]. *see also* [[#Publication choke-point]].

## F

### First note wins

*See* [[#Ambiguity-preserving reference resolution]]. (The documented policy is not stable when the index is populated from Go map iteration.)

### Frontmatter, single structural split

Every transform must consume the same metadata/body boundary as the metadata parser; otherwise valid metadata can be rewritten before parsing. [Open correctness obligation] [[Research/Software Architecture Garden/publish-vault/05 - Parser-Owned Structure and Typed Reference Resolution#Frontmatter must be split once|§5.6]]. *see also* [[#Parser-owned structural context]].

## G

### GitOps target declaration

A machine-readable file maps released images to cluster repositories, manifests, and container names so release automation opens a reviewable deployment PR. [Candidate ecosystem pattern] [[Research/Software Architecture Garden/publish-vault/02 - Deployment and Release Topology#The GitOps target declaration|§2.3]], [[Research/Software Architecture Garden/publish-vault/04 - Candidate Ecosystem Guidelines#Candidate 5: Go-app plus Node-SSR sidecar, two images, GitOps target declaration|§4.5]].

### Graph edge is not occurrence

*See* [[#Occurrence preservation]].

## H

### HTML is not an internal representation

*See* [[#Typed reference pipeline]]. (Rendered HTML is output, not a server-side state protocol to parse and mutate.)

### HTML placeholder protocol

Wiki-link fields are encoded in generated `data-*` attributes and recovered by fixed-order/global regex passes. [Emergent / Architecture debt] [[Research/Software Architecture Garden/publish-vault/03 - Patterns Limits and Architecture Debt#The wiki-link placeholder approach|§3.4]], [[Research/Software Architecture Garden/publish-vault/05 - Parser-Owned Structure and Typed Reference Resolution#Law 4: resolve typed state before rendering|§5.4]].

## I

### Ignore matcher, documented subset

A root `.vault-ignore` implements last-match-wins `path.Match` behavior without `**` or nested ignore files; permissive negation is coupled to directory pruning. [Emergent, not an ecosystem candidate] [[Research/Software Architecture Garden/publish-vault/03 - Patterns Limits and Architecture Debt#The hand-rolled gitignore-subset matcher|§3.1]].

### Immutable parser output for rebuild

Vault-dependent rendering starts from stable parser output rather than previously resolved HTML, keeping target removal/restoration reversible. [Established locally] [[Research/Software Architecture Garden/publish-vault/05 - Parser-Owned Structure and Typed Reference Resolution#Reload must remain reversible|§5.6]], [[#Reload reversibility]].

## L

### Load-once, read-snapshot execution

Expensive parsing/indexing occurs during load; request handlers read a complete prepared snapshot. [Candidate ecosystem pattern] [[Research/Software Architecture Garden/publish-vault/01 - Project Architecture Overview#The two-phase execution model|§1.1]], [[Research/Software Architecture Garden/publish-vault/04 - Candidate Ecosystem Guidelines#Candidate 1: Two-phase load-once, read-snapshot execution|§4.1]].

## N

### Node SSR sidecar

A Node container owns React SSR while the Go app owns API/static delivery and falls back to client rendering if SSR fails. [Candidate ecosystem pattern when SSR is needed] [[Research/Software Architecture Garden/publish-vault/02 - Deployment and Release Topology#The container topology|§2.1]], [[Research/Software Architecture Garden/publish-vault/04 - Candidate Ecosystem Guidelines#Candidate 5: Go-app plus Node-SSR sidecar, two images, GitOps target declaration|§4.5]].

## O

### Occurrence preservation

Parsing retains every authored reference's order, kind, source span, target, heading, alias, and context; consumers choose their own projection/deduplication. [Candidate / Documented] [[Research/Software Architecture Garden/publish-vault/05 - Parser-Owned Structure and Typed Reference Resolution#Law 2: preserve occurrences; derive edges|§5.2]]. *see also* [[#Backlink graph projection]], [[#Source spans]].

## P

### Parser-owned structural context

One parser classifies prose, code, frontmatter, math, and raw HTML; extensions consume that context rather than reconstructing it independently. [Candidate / Documented] [[Research/Software Architecture Garden/publish-vault/05 - Parser-Owned Structure and Typed Reference Resolution#Law 1: parser-owned structural context|§5.1]]. *see also* [[#Protected-region law]], [[#Frontmatter, single structural split]], [[#Static renderer conformance]].

### Plain-text projection

Search/excerpt text should be rendered from the same parsed document rather than stripped by an independent Markdown regex approximation. [Proposed] [[Research/Software Architecture Garden/publish-vault/05 - Parser-Owned Structure and Typed Reference Resolution#Concrete target architecture|§5.5]].

### Protected-region law

For a transform that does not own a context, bytes in that protected context remain unchanged (or retain an explicit source mapping). [Candidate / Documented] [[Research/Software Architecture Garden/publish-vault/05 - Parser-Owned Structure and Typed Reference Resolution#Law 1: parser-owned structural context|§5.1]].

### Publication choke-point

Build one post-filter note map and make every derived consumer read it; direct filesystem consumers recheck the filter. [Candidate ecosystem pattern] [[Research/Software Architecture Garden/publish-vault/01 - Project Architecture Overview#The vault loader as the central choke point|§1.2]], [[Research/Software Architecture Garden/publish-vault/04 - Candidate Ecosystem Guidelines#Candidate 2: Single choke-point collection with load-time gating|§4.2]].

## R

### Reference resolution, typed

*See* [[#Typed reference pipeline]].

### Reload reversibility

Removing and restoring a target must move references between resolved and unresolved states without compounding prior rendered output. [Established locally / target law] [[Research/Software Architecture Garden/publish-vault/05 - Parser-Owned Structure and Typed Reference Resolution#Reload must remain reversible|§5.6]], [[#Immutable parser output for rebuild]].

### Render after resolve

*See* [[#Typed reference pipeline]].

### Repo-root discovery drift

Two copied root-finders use different sentinel paths, including one layout that does not exist in the repository. [Architecture debt] [[Research/Software Architecture Garden/publish-vault/03 - Patterns Limits and Architecture Debt#Inconsistent repo-root discovery|§3.3]].

### Reusable release workflow

Projects inherit centrally maintained GHCR build/test/publish/GitOps behavior instead of copying workflow logic. [Candidate ecosystem pattern] [[Research/Software Architecture Garden/publish-vault/02 - Deployment and Release Topology#The release workflow|§2.4]]. *see also* [[#GitOps target declaration]], [[#Shared-workflow version risk]].

## S

### Shared-workflow version risk

Referencing the reusable release workflow at `@main` coordinates updates but allows one breaking change to affect all consumers simultaneously. [Open correctness obligation] [[Research/Software Architecture Garden/publish-vault/02 - Deployment and Release Topology#What goes wrong|§2.8]].

### Short-path wiki-link index

Full slugs, basenames, titles, and progressive path suffixes support concise Obsidian links but create an ambiguous namespace. [Emergent] [[Research/Software Architecture Garden/publish-vault/01 - Project Architecture Overview#Wiki-link resolution and backlinks|§1.3]], [[#Ambiguity-preserving reference resolution]].

### Source spans

Byte ranges retain where each parsed occurrence came from so diagnostics, editors, and projections can refer to authored syntax. [Proposed] [[Research/Software Architecture Garden/publish-vault/05 - Parser-Owned Structure and Typed Reference Resolution#Law 2: preserve occurrences; derive edges|§5.2]].

### Static renderer conformance

Go/goldmark and TypeScript/marked consume one versioned fixture corpus for expected occurrences, resolution, graph edges, diagnostics, and essential HTML. [Proposed] [[Research/Software Architecture Garden/publish-vault/05 - Parser-Owned Structure and Typed Reference Resolution#Backend/static conformance is semantic|§5.6]].

### Static graph divergence

Marked renders wiki links with parser context while the static backlink graph extracts them with a global raw regex. [Architecture debt] [[Research/Software Architecture Garden/publish-vault/05 - Parser-Owned Structure and Typed Reference Resolution#Backend/static conformance is semantic|§5.6]].

### Symlink-resolved vault root

Resolve a stable git-sync symlink before load so one snapshot reads one concrete checkout. [Established locally] [[Research/Software Architecture Garden/publish-vault/01 - Project Architecture Overview#The atomic snapshot model|§1.4]].

## T

### Trust mode, explicit

A reusable Markdown engine declares whether aliases/raw HTML are escaped text, parsed inline Markdown, or trusted HTML. [Open design decision] [[Research/Software Architecture Garden/publish-vault/05 - Parser-Owned Structure and Typed Reference Resolution#Trust mode must be explicit|§5.6]].

### Two images, one release coordinate

The Go app and SSR sidecar are built/published together but need explicit compatibility/version alignment. [Emergent] [[Research/Software Architecture Garden/publish-vault/02 - Deployment and Release Topology#Two Dockerfiles and two images|§2.2]], [[Research/Software Architecture Garden/publish-vault/02 - Deployment and Release Topology#What goes wrong|§2.8]].

### Typed reference pipeline

Parse source into typed occurrences, resolve them against explicit external state, then render HTML/text and derive graph projections. [Candidate / Documented] [[Research/Software Architecture Garden/publish-vault/05 - Parser-Owned Structure and Typed Reference Resolution#Pattern statement|§5.0]], [[Research/Software Architecture Garden/publish-vault/05 - Parser-Owned Structure and Typed Reference Resolution#Law 4: resolve typed state before rendering|§5.4]].

## W

### Wiki-link placeholder approach

*See* [[#HTML placeholder protocol]].

### Widget DSL sibling-module workaround

A contract from another repository is duplicated by reference through `vault.widgets` pending a first-class namespace extension. [Emergent] [[Research/Software Architecture Garden/publish-vault/03 - Patterns Limits and Architecture Debt#The widget DSL sibling-module workaround|§3.5]].

## Identity strings, schemas, and operational handles

| Handle | Kind | Meaning | Where |
|---|---|---|---|
| `Snapshot` | runtime aggregate | Vault, search index, revision, resolved root, and build timestamp swapped as one epoch. | [[Research/Software Architecture Garden/publish-vault/01 - Project Architecture Overview#The atomic snapshot model|§1.4]], [[#Atomic snapshot swap]] |
| `v.notes` | authoritative collection | Post-filter published note map from which API/tree/search/backlinks derive. | [[Research/Software Architecture Garden/publish-vault/01 - Project Architecture Overview#The vault loader as the central choke point|§1.2]], [[#Publication choke-point]] |
| `wikiLinkIndex` | current resolver index | Single-value suffix/title map; target design is an ambiguity-preserving multimap. | [[Research/Software Architecture Garden/publish-vault/01 - Project Architecture Overview#Wiki-link resolution and backlinks|§1.3]], [[#Ambiguity-preserving reference resolution]] |
| `SourceDocument` | proposed IR | Raw source split once into frontmatter/body with body offset. | [[Research/Software Architecture Garden/publish-vault/05 - Parser-Owned Structure and Typed Reference Resolution#Concrete target architecture|§5.5]], [[#Frontmatter, single structural split]] |
| `LinkOccurrence` | proposed IR | Ordered authored reference with span, kind, target, heading, alias, and context. | [[Research/Software Architecture Garden/publish-vault/05 - Parser-Owned Structure and Typed Reference Resolution#Law 2: preserve occurrences; derive edges|§5.2]], [[#Occurrence preservation]] |
| `ResolvedLink` | proposed IR | Occurrence plus resolved/unresolved/ambiguous state, destination, heading ID, and candidates. | [[Research/Software Architecture Garden/publish-vault/05 - Parser-Owned Structure and Typed Reference Resolution#Law 4: resolve typed state before rendering|§5.4]], [[#Typed reference pipeline]] |
| `data-target`, `data-heading`, `data-raw`, `data-alias` | HTML protocol | Current placeholder transport fields; browser contracts must be separated from server-internal transport. | [[Research/Software Architecture Garden/publish-vault/05 - Parser-Owned Structure and Typed Reference Resolution#Law 4: resolve typed state before rendering|§5.4]], [[#HTML placeholder protocol]] |
| `.vault-ignore` | policy file | Root-scoped documented-subset exclusion language. | [[Research/Software Architecture Garden/publish-vault/03 - Patterns Limits and Architecture Debt#The hand-rolled gitignore-subset matcher|§3.1]], [[#Ignore matcher, documented subset]] |
| `deploy/gitops-targets.json` | release declaration | Image-to-container/manifest/repository mapping consumed by release automation. | [[Research/Software Architecture Garden/publish-vault/02 - Deployment and Release Topology#The GitOps target declaration|§2.3]], [[#GitOps target declaration]] |
| `embed` / `!embed` | build tags | Embedded production bundle versus disk-served development bundle. | [[Research/Software Architecture Garden/publish-vault/02 - Deployment and Release Topology#The build command and the embedded-SPA pattern|§2.5]], [[#Embedded SPA, build-tag controlled]] |

## Cross-reference summary

- [[#Ambiguity-preserving reference resolution]] ↳ devctl qualified dynamic-command resolution and Upwork Tracker ambiguous receipt rejection. **Correspondence, not equivalence:** parser references, commands, and receipts have different authority and candidate semantics.
- [[#Occurrence preservation]] ↳ Upwork Tracker evidence-occurrence versus content identity. **Correspondence, not equivalence:** Markdown occurrences are authored syntax, not remote evidence events.
- [[#Publication choke-point]] ↳ filtered registries and post-admission collections across the Garden. **Correspondence, not equivalence:** publication gating is not authorization.
- [[#Atomic snapshot swap]] ↳ immutable-release/snapshot vocabulary. **Correspondence, not equivalence:** a runtime snapshot epoch is not automatically a behavior-complete immutable release.
- [[#Typed reference pipeline]] ↳ explicit translation and typed intent/effect boundaries. **Correspondence, not equivalence:** resolving a note reference is not authorizing an effect.

## Related documents

- [[Research/Software Architecture Garden/publish-vault/README|Architecture Garden — publish-vault]]
- [[Research/Software Architecture Garden/publish-vault/Index of Design Patterns - Rationale|Index rationale]]
- [[Research/Software Architecture Garden/README|Software Architecture Garden]]
