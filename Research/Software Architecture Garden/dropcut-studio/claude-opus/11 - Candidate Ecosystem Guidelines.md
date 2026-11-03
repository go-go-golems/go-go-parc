---
title: Candidate Ecosystem Guidelines
aliases:
  - dropcut-studio CAM core guideline candidates
status: candidate
type: architecture-garden-guidelines
created: 2026-10-25
analyzed: 2026-10-25
analysis_author: claude-opus-5-5
repository: /home/manuel/code/wesen/dropcut-studio
repository_commit: f3ebac2d5291b4a371bde25ae3a44d6f752cff41
tags:
  - architecture-garden
  - dropcut-studio
  - guidelines
related_notes:
  - "[[Research/Software Architecture Garden/dropcut-studio/claude-opus/README|claude-opus study — dropcut-studio CAM core]]"
  - "[[Research/Software Architecture Garden/README|Software Architecture Garden]]"
---

# Candidate Ecosystem Guidelines

This chapter condenses the study into rules that could apply beyond CAM. Each rule names the chapter that develops it, the strongest local evidence, and a Garden project where it should be compared before it becomes ecosystem guidance. Under the Garden's maturity vocabulary, all of these are **candidates**: one strong implementation, at least one plausible comparison target.

> [!summary]
> The study's rules group into four themes: keep semantic models free of serialisation state; represent gates and evidence in types; make target and plugin variation data; and enforce every declaration with a test that tries to violate it.

## 1. Semantic models and serialisation

**G1. Keep the semantic IR free of inherited state.** Every record carries the parameters it needs. *Evidence:* the non-modal `CanonicalCommand` union and the arc-as-geometry representation ([[Research/Software Architecture Garden/dropcut-studio/claude-opus/02 - Modality as a Final Compression Pass - The Non-Modal IR and Its Round-Trip Oracle|02]]). *Compare with:* sessionstream's canonical events ([[Research/Software Architecture Garden/sessionstream/designs/02 - Typed Transition Systems and Trace Algebra|sessionstream 02]]), which face the same question for event payloads.

**G2. Confine state-dependent encoding to one pure function, and keep the explicit form for comparison.** *Evidence:* `compress()` and `rawBlocks`.

**G3. Own an interpreter for any stateful output format, use it as a round-trip oracle, and pair the property with an anti-vacuity test.** State in the test what a differential oracle cannot prove. *Evidence:* `roundtrip.test.ts`, 400 + 3×120 generated programs.

## 2. Gates and evidence

**G4. Represent pipeline gates as distinct types with one minting site.** Enforce the minting boundary with lint or package exports, not comments. *Evidence and caveat:* `ValidatedProgram`, single-cast forgery ([[Research/Software Architecture Garden/dropcut-studio/claude-opus/04 - Certified Stage Types - A Brand Minted in One Place|04]]). *Compare with:* upwork-tracker's human-submission boundary, which gates an effect rather than a stage.

**G5. Report verification per check as graded evidence** — exact, sampled with resolution, not checked with reason, unverifiable with reason — and show unperformed checks on every report. *Evidence:* `CheckStatus`, permanent fixture/holder rows ([[Research/Software Architecture Garden/dropcut-studio/claude-opus/05 - Graded Evidence Certificates - Say What Was Verified and to What Resolution|05]]). *Compare with:* the dropcut controller's consecutive evidence observer ([[Research/Software Architecture Garden/dropcut-studio/designs/06 - Consecutive Evidence Observer - Completion Without Owning the Operation|designs/06]]), which distinguishes invalid from non-matching evidence for the same reason.

**G6. Upgrade a claim only with evidence produced for that claim; make the evidence type per-claim.** *Evidence:* the gouge counterexample, where one record upgraded two claims.

**G7. Let escape hatches poison the evidence they invalidate, and keep that poisoning sticky.** *Evidence:* `RawCmd` → `unverifiable`; `recertify` refuses to upgrade it.

**G8. Record the direction of every approximation in a safety path, and surface non-conservative ones.** *Evidence:* conservative bull-nose versus unreported V-bit ([[Research/Software Architecture Garden/dropcut-studio/claude-opus/06 - Branch-and-Bound Spatial Queries - Tight Bounds Beat Fast Code|06]]).

**G9. Label every estimate with the model that produced it.** *Evidence:* `model: "length-over-feed"`.

## 3. Variation as data

**G10. Describe targets as capability records whose fields name properties of the target, and express the IR in intents those records can decide.** *Evidence:* `MachineProfile`, `TraverseCmd` with `ClearanceRequirement`, the configuration-only Makera backend ([[Research/Software Architecture Garden/dropcut-studio/claude-opus/03 - Capabilities as Data - Intent Commands Lowered by a Profile Record|03]]). *Compare with:* devctl's declarative plugins.

**G11. Every declared capability is consulted by at least one stage, and each decision has one authority.** *Evidence against:* `helical`, duplicated arc linearisation.

**G12. Inject plugin dispatch into the coordinator; the coordinator never imports its plugins.** *Evidence:* `RunOptions.strategies` ([[Research/Software Architecture Garden/dropcut-studio/claude-opus/08 - Strategies Produce Geometry, the Planner Owns the Gaps|08]]).

**G13. Producers emit content; one coordinator owns every transition, starts from the most conservative state it can know, and lowers margins only with proof supplied through the contract.** *Evidence:* stock-top retract floor, CAM-002's analysis of the thin `ToolpathSet`.

**G14. Make fallbacks a ladder with a diagnostic at every rung below the requested one.** *Evidence:* `entry.degraded`.

## 4. Embedded scripting

**G15. Give scripts a fresh capability object as their only interface, and make their output a serialisable declarative plan.** Document that name shadowing is not isolation. *Evidence:* `runScript`, `createScriptApi`, the `constructor` probe ([[Research/Software Architecture Garden/dropcut-studio/claude-opus/07 - Capability-Passing Script Host - Named Parameters, Boxed Units and Scope Combinators|07]]). *Compare with:* [[Research/Software Architecture Garden/go-go-goja/README|go-go-goja]] native modules.

**G16. Enforce units at runtime in untyped scripts: reject wrong units, warn on bare numbers, normalise alternate units at construction.**

**G17. Prefer scope combinators to paired start/stop calls; keep the actual state transitions in the host.**

## 5. Application state and files

**G18. Keep serialisability checks on; store large derived artifacts in an id-keyed cache with live-set GC; give per-frame state one imperative owner.** *Evidence:* the three tiers ([[Research/Software Architecture Garden/dropcut-studio/claude-opus/09 - Three-Tier Application State - Serializable Store, Artifact Cache, Imperative Clock|09]]). *Compare with:* upwork-tracker's URL state and workspace.

**G19. Version saved documents from the first release, keep the document type independent of in-memory state, and reject malformed fields before defaulting absent ones.** *Compare with:* upwork-tracker's source-state separation.

**G20. When work becomes asynchronous, fence results by generation.** An abort that nothing observes is not a fence. *Compare with:* the dropcut controller's browser intent ownership with stale-response fencing ([[Research/Software Architecture Garden/dropcut-studio/designs/07 - Browser Intent Ownership - Confirm Once and Renew Only While Held|designs/07]]).

## 6. The meta-rule

**G21. For every declared property — in a comment, a type, an option or a diagnostic code — write the test that tries to violate it.** Every debt item in [[Research/Software Architecture Garden/dropcut-studio/claude-opus/10 - Architecture Debt and Patterns Not to Repeat|chapter 10]] is a declaration whose violating test was never written. The repository's habit of documenting non-guarantees is excellent; this rule is the step that turns documented intent into enforced behaviour.

## 7. Promotion criteria

A candidate becomes an ecosystem guideline when a second Garden project demonstrates it independently, or when a second project's failure demonstrates its absence. The strongest near-term candidates for comparison are G5–G6 (graded, per-claim evidence) against sessionstream's projection-cursor work and the dropcut controller; G10–G11 (capabilities as data) against devctl; and G15 (capability-passing scripts) against go-go-goja.
