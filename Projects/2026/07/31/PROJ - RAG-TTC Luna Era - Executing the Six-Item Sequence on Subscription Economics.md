---
title: "RAG-TTC Luna Era: Executing the Six-Item Sequence on Subscription Economics"
aliases:
  - luna sequence execution
  - rag-ttc luna era
  - LUNA-001 execution
tags:
  - project
  - rag
  - provider-engineering
  - experiments
  - reliability
  - golang
status: active
type: project
created: 2026-07-31
repo: /home/manuel/workspaces/2026-06-30/benchmark-cpu-inference/rag-ttc
---

# RAG-TTC Luna Era: Executing the Six-Item Sequence on Subscription Economics

This report documents the execution of the RAG-TTC-LUNA-001 work sequence — six dependency-ordered items that move the rag-ttc research lab onto subscription generation economics and extend its experiment space — together with two unplanned engineering threads the same afternoon forced: a four-attempt reliability campaign for the first full LLM-judge run, and the diagnosis and upstream fix of a profile-resolution regression that the lab's own configuration had inflicted on every other pinocchio user of the machine. The sequence's build phase completed entirely within the judge's gateway-occupancy window; at the time of writing, its two run-phase legs (the judged E10 series and the nine-arm luna screening bench) are executing concurrently on disjoint providers.

The through-line of the afternoon is an economics inversion. In the morning, generation on `gpt-5.6-luna` was metered and judge calls were an open question; by mid-afternoon, answer generation and all up-front representation generation run on a ChatGPT subscription at zero marginal cost, judged metrics exist for every cell, and the binding constraint of judged experiments has been measured and named: the judge's gateway, not the answerer.

> [!summary]
> - Item 1 productionized the Codex OAuth path behind a profile extension (`rag-ttc.codex@v1`): a hardened credential source, an engine wrapper that owns the mandatory per-turn `store=false` stamp, and secret-free profiles. Verified live: grounded answers on the subscription with real token accounting.
> - Items 3/5/6 landed as code with a decisive gate: the recorded E10 confirmation run replays on the new binary with `retrieval-summary.json` exactly identical — the per-channel fusion machinery, two new representation families, and two new query-strategy arms changed nothing about existing identities.
> - The judge's first full run took four attempts, each felled by a different transient transport failure; the retry classification gained three markers (`generation response is empty`, `timed out`, `network is unreachable`) and the incident sequence is itself a finding about reasoning-mode streaming reliability.
> - A separate regression — bare profile names failing everywhere outside the lab — was traced to pinocchio pinning the default registry before profile lookup, defeating geppetto's built-in cross-registry search. Fixed locally, upstreamed as pinocchio PR #191, and the same latent pattern was fixed in rag-ttc's own resolver.

## Why this sequence exists

The sequence was designed (RAG-TTC-LUNA-001 design-doc 01) around two constraints. First, provider economics: the 2026-07-31 model policy assigns answers and all up-front generation to `gpt-5.6-luna`, so making the ChatGPT-subscription path production-real *first* converts every later item from metered to free. Second, gateway discipline: the judge's first full run holds the umans GLM gateway for about an hour of verdict calls, and nothing else may contend with it — which makes the window exactly the right time for code-only and subscription-only work. The six items: (1) Codex wiring, (2) judge spot-audit tooling, (3) E10b per-channel fusion, (4) luna representation regeneration, (5) E16/E17 representation families, (6) E11 query-strategy arms.

## Item 1 — the Codex path, from smoke tool to provider layer

The morning's standalone proof (`scripts/codex-oauth-test`) became a first-class provider path in `pkg/rag/providers/geppetto/codex`, selected declaratively: a profile carrying the `rag-ttc.codex@v1` extension resolves to a codex-backed engine instead of the standard factory. Three design decisions carry the section's weight:

- **Refusal over fallback.** A profile that names the codex extension gets codex or an error — never a silent fallback to metered keys. The same rule shaped the resolver: extension parsing distinguishes "absent" (nil, use standard path) from "present but unusable" (error).
- **The engine owns the stamp.** The Codex backend rejects any Responses payload lacking an explicit `"store": false`. Rather than trusting every caller, a wrapping engine stamps the per-turn override on each inference — merge-preserving, so other per-turn OpenAI configuration survives. A forgotten stamp is impossible by construction.
- **Concurrency-safe rotation.** The credential source is mutex-guarded for parallel generation workers: eager refresh at sixty seconds before expiry, one refresh-and-replay after a 401, rotated tuples persisted atomically *before* the replay, and the rotation-aware replay path recognizes when another worker already rotated past the rejected token. The ChatGPT account id is derived from the access token's JWT claims; it is not configuration.

One geppetto sharp edge surfaced: the OAuth protocol client validates a redirect URL even when only the refresh grant will ever be used. Extension lookup reads *raw* profiles (one stack level deep) because geppetto's resolution merges extensions across a profile stack but then drops them from the resolved result — a fact worth knowing before designing any extension-driven behavior.

Verification followed the standing token-accounting rule: a two-query answer-quality smoke on `ttc-live-luna-codex` produced contract-valid grounded answers with plausible usage (824 input / 57 output tokens), recorded in the run's provenance.

## Item 2 — making the audit gate cheap

The judge's numbers are unusable until a 20-verdict human audit clears them (≥90% agreement). Two pieces made that gate cheap to exercise. First, an artifact enrichment: `judge-per-query.jsonl` rows now persist full per-statement verdict records — polarity, cited evidence indices, and the model's stated reason — so audits grade from run artifacts alone; previously the reasons died with the raw responses (recoverable only from the cache). Second, `judge-audit.py`: a deterministic, seeded, stratified sampler (minimum quotas per polarity, round-robin across arms) rendering one card per verdict — question, statement, verdict with reason, and the *verbatim admitted evidence* — plus a grade-back JSONL and a scorer that reports agreement overall and split by polarity, with disagreement cards listed as the evidence base for any prompt or model change. The enrichment costs nothing retroactively: a re-judge of an unchanged run replays from cache in minutes and emits the enriched schema.

## Items 3, 5, 6 — the experiment-space extensions

**E10b (per-channel fusion)** operationalizes the chunk-lab reversal's implication: give each retrieval channel the representation population it prefers. `--lexical-representation-arm` and `--vector-representation-arm` resolve registry arms independently over one shared chunk set; BM25 indexes the lexical population, embeddings and the vector index cover the vector population, and RRF fuses without modification because fusion always operated on collapsed chunk targets. The shared-chunk-set invariant is enforced with a named refusal — a re-chunking arm (any `size-*`, `llm-chunk`) is illegal per channel, legal only as the shared arm — because divergent chunkings would break common hydration and make per-query deltas unattributable. Both generated populations draw on a single fail-closed budget whose refusal states the summed arithmetic.

**E16/E17 (new representation families)** were implemented by a subagent from a written specification while E10b was built inline — the first delegation of identity-sensitive registry code in this project. The spec pinned the conventions (Builder contract, batched machinery reuse, prompt-as-identity, call arithmetic) and the review confirmed spec-to-diff fidelity, including one judgment call the agent made correctly on its own: documents with zero chunks *error* rather than skip, matching the repo's skip-loudly ethos. E16's `raptor-lite` composes chunk-level summaries (reusing the exact `llm-summary-2sent-batch` spec, so those generations are cross-arm cache hits) with one document-level summary per document, hydrating to the document's first chunk under the admissible-evidence invariant. E17's `statements-only` and `raw+statements` index atomic factual statements — the declarative mirror of the questions arms, which serve as its designed control in the same screening run. The judge's statement-extraction prompt and E17's indexing prompt remain deliberately distinct constants: same idea, different layers, independently evolvable.

**E11 (query strategies as arms)** promoted `multi-query` and `hyde` from TUI-only strategies to experiment arms. The consequential design choice is where the rewrites run: through the cached, budgeted, retried generation path like every other spend, under their own cache identity (`ttc-query-strategy-adapter-v1` / `question-text-v1`) with the request kinds partitioning the two strategies. Ceiling arithmetic gained the per-query rewrite call and the embedded-variant items; run configs record both default prompts and the variant count, honoring the rule that prompts are experiment identity.

## The gate

Every phase of this project ends on the same question: did the refactor change wiring or identity? The answer here was obtained in the strongest available form — the recorded E10 confirmation run (148 queries × 3 arms) replayed on the post-sequence binary, and `results/retrieval-summary.json` compared structurally: **exactly equal**, every aggregate and every per-query metric, across the E10b split machinery, the E11 arms, the judge stage, and the harness extraction beneath them all. The comparison is cheap (a cached replay takes seconds of provider time) and total (it exercises chunking, representation identity, indexing, retrieval, fusion, and metric computation end to end).

## The judge run reliability campaign

The first full judged run — 444 answer cells replaying free from cache, ~850 live GLM verdict-side calls — took four attempts, and the sequence of failures is a finding in itself:

| Attempt | Died at | Error | Classification gap |
|---|---|---|---|
| 1 | statements item 308 | stream delivered 3,004 chunks of hidden reasoning, zero content → "generation response is empty" | empty responses treated as hard errors |
| 2 | statements item 3 | raw TCP `read: connection timed out` | marker list had "timeout", not "timed out" |
| 3 | verdicts item 36 | `network is unreachable` ×4 workers in one second (local VPN blip) | unreachable family unclassified |
| 4 | — (in flight) | — | — |

Each retry-marker addition shipped with a test, and each relaunch was cheap because everything completed is cached — attempt 3 finished the entire statements pass, so attempt 4 pays only for remaining verdicts. Two durable lessons: reasoning-mode models can stream entire responses that contain no content (the empty result is transient on retry, and a *deterministic* empty still fails loudly after the attempts cap); and substring-based transport classification accumulates by incident — each new marker earned its place with a run's corpse, which argues for eventually classifying by error type rather than message text.

## The registry-resolution regression and PR #191

Mid-afternoon, an unrelated-looking report arrived: `PINOCCHIO_PROFILE=gemini-2.5-pro` failing with "profile not found" in another repository, though `pinocchio profiles list` showed the profile. The diagnosis localized in four steps: the checkouts were clean of our changes (the code was never touched); the lab *had* changed configuration the prior evening (registering rag-ttc's `profiles.yaml` as a second registry); pinocchio takes the last-listed registry as top-of-stack default; and — the actual defect — pinocchio's `ResolveCLIProfileRuntime` pins `ResolveInput.RegistrySlug` to that default *before* setting the profile slug, which defeats geppetto's `ChainedRegistry` precedence search (built precisely for this case, activating only when the registry slug is zero). With one registry the pin was invisible; with two, every bare name outside the default registry broke. The error message itself was the smoking gun: `load profile rag-ttc/gemini-2.5-pro`.

The fix is a four-line reorder — pin the default registry only when *no* profile is named — plus the same search behavior in `profiles show`, and one test updated to the new resolve-input contract. Delivered three ways: patched and installed locally (including the discovery that the active binary lived in `~/.local/bin`, predating `go install`'s target), upstreamed as **pinocchio PR #191** from a clean worktree so none of the user's unrelated WIP rode along, and — the humbling part — the *same latent pinning pattern* found and fixed in rag-ttc's own `ResolveNamed`, which had worked only because the judge's profiles happened to live in the registry being pinned. A pre-push hook subtlety is recorded for reuse: the push-time `govulncheck` failure was a pre-existing dependency advisory, verified as such before bypassing the hook for the push.

## Status at time of writing

Complete: items 1, 2, 3, 5, 6 (code, tests, gate) and item 4's launch. In flight: judge attempt 4 (umans; verdicts pass) and the nine-arm luna screening (subscription; `markdown`, four batched summary/question arms, `llm-chunk`, `raptor-lite`, `statements-only`, `raw+statements` — ceiling stated by refusal at 8,992 calls across 5 specs, realistic spend ~700–900 calls at ~25 calls/min). Pending on their completion: screening deltas → the three-configuration E10b run and five-arm E11 run; judge completion → enriched re-judge and the human audit sheet. Pending on the user: the 20-card grading itself.

## Open questions

- Does `raptor-lite` concentrate its gains on multi-chunk-answer queries, and `statements-only` on specific-fact queries, as their hypotheses predict? The screening's per-query deltas answer both within the hour.
- Do statements beat questions (declarative vs interrogative decomposition) on the same bench — E17's control comparison?
- Should transport-error classification move from substrings to typed errors before the next long campaign?

## Important project docs

- Ticket: `rag-ttc/ttmp/2026/07/31/RAG-TTC-LUNA-001--.../` — design-doc 01 (the sequence guide), diary Steps 1–3, tasks with per-item evidence.
- Code: `pkg/rag/providers/geppetto/codex/`, `answerquality/representationarm.go`, `representations/{documents,batched,prompts}.go`, chunkcompare registry additions, `scripts/judge-audit.py` (in the ticket).
- Upstream: pinocchio PR #191 (`fix/profile-registry-chain-search`).
- Commits: `7148bd7` (item 1), `37a55c2` (item 2), `dc7e6ec` (E10b), `a8f13a6` (E16/E17), `f701327` (E11), retry hardening `aee3f12`/`52bbe2c`/`ef6b63c`, resolver fix `2d0948d`.

## Related notes

- [[PROJ - RAG-TTC LLM Judge - A Two-Step Decomposed Faithfulness Pipeline from Design to Live Run]] — the judge this sequence's window revolves around; its reliability campaign continues here.
- [[PROJ - Codex OAuth for gpt-5.6-luna - Subscription-Plan Inference Through Geppetto's OpenAI-Codex Transport]] — the smoke-tool proof item 1 productionized.
- [[PROJ - RAG-TTC Codebase Consolidation - Review-Then-Execute from 49k Lines to a Two-Track Repository]] — the seams (harness, resolver, prompt fields) every item of this sequence consumed.
- [[PROJ - RAG-TTC Chunk Lab Results - From BM25 Screening to the Hybrid Retrieval Reversal]] — the reversal E10b operationalizes and the screening method items 4–5 reuse.
- [[ARTICLE - Reproducibility Engineering - Digests, Caches, Budgets, and Provenance]] — why a digit-exact replay is the correct gate and why each judge relaunch was cheap.
