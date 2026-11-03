---
title: Architecture Debt and Patterns Not to Repeat
aliases:
  - dropcut-studio CAM core debt register
  - Comments that outran the code
status: active
type: architecture-garden-debt
created: 2026-10-25
analyzed: 2026-10-25
analysis_author: claude-opus-5-5
repository: /home/manuel/code/wesen/dropcut-studio
repository_remote: git@github.com:wesen/dropcut-studio.git
repository_commit: f3ebac2d5291b4a371bde25ae3a44d6f752cff41
tags:
  - architecture-garden
  - dropcut-studio
  - architecture-debt
  - open-correctness-obligation
related_files:
  - packages/compiler/src/recertify.ts
  - packages/analysis/src/checks.ts
  - packages/analysis/src/certificate.ts
  - apps/studio/src/state/compileThunk.ts
  - apps/cli/src/compile.ts
  - packages/ir/src/program.ts
  - packages/geometry/src/drop-cutter.ts
  - packages/post-rs274/src/index.ts
  - packages/planner/src/run.ts
related_notes:
  - "[[Research/Software Architecture Garden/dropcut-studio/claude-opus/05 - Graded Evidence Certificates - Say What Was Verified and to What Resolution]]"
  - "[[Research/Software Architecture Garden/dropcut-studio/claude-opus/11 - Candidate Ecosystem Guidelines]]"
---

# Architecture Debt and Patterns Not to Repeat

DROPCUT Studio is unusually explicit about its own limits. Its comments say what a check does not prove, which approximation is conservative, and which feature is not built. That honesty is the reason the debt below is easy to find: almost every item is a place where a comment, a type or a declared option promises something the code does not yet do. This chapter lists those places, ranks them by consequence, and names the general pattern each one illustrates. The analysis is at `f3ebac2`; "evidence" means a command, a test or a grep that was run for this study.

> [!summary]
> - **One open correctness obligation:** the certificate reports `PASS gouge` with no gouge computation. A pocket 13 mm into the part passes.
> - **One duplicated authority with measurable drift:** the studio's compile thunk re-implements the CLI pipeline that claims to be shared "by construction", and its render colouring is inferred from description strings.
> - **Several declared-but-unenforced contracts:** a forgeable brand described as unforgeable, a `helical` capability nothing reads, a `timeoutMs` nothing enforces, three diagnostic codes nothing emits, an abort nothing observes.
> - **One unreported non-conservative approximation:** the V-bit drop-cutter.
> - The general lesson: **a declaration is not an enforcement.** Each of these would be caught by a test that tries to violate the declared property.

## 1. Ranked register

| # | Item | Class | Consequence | Chapter |
|---|---|---|---|---|
| D1 | Gouge row upgraded without a gouge check | Open correctness obligation | False assurance on the exact failure mode the certificate exists for | 05 |
| D2 | Compile pipeline duplicated in `compileThunk.ts` | Architecture debt | CLI and app can diverge; already have in render metadata | §3 |
| D3 | V-bit CL approximation is non-conservative and unreported | Open correctness obligation (latent) | A V-bit job can gouge with a clean certificate | 06 |
| D4 | Two certificate builders; test-only helpers | Architecture debt | Drift; analysis builder names inputs nobody computes | 05 |
| D5 | Brand forgeable by a single cast; mint publicly exported | Contract overstated | Gate bypass is visible but not prevented | 04 |
| D6 | `helical` capability declared, unconsulted; arc decision made twice | Latent false contract | Wrong output once arc fitting lands | 03 |
| D7 | `timeoutMs` declared, no worker, no watchdog | Documented gap | A runaway script hangs the tab | 07 |
| D8 | `inFlight.abort()` has no effect | Latent | Stale results once compilation is asynchronous | 09 |
| D9 | Runner hard-codes spindle `"cw"` and a 12,000 rpm default | Hidden default | Silent parameter choice; fails validation on a low-speed spindle | §6 |
| D10 | `ToolpathSet` carries no clearance evidence; reversal ignores milling direction | Known limitation, designed in CAM-002 | Excess retracts; climb/conventional flips | 08 |
| D11 | Declared diagnostic codes never emitted | Dead vocabulary | Suggests checks that do not exist | §7 |

## 2. D1 — Evidence applied to a claim it does not support

This item is described in full in [[Research/Software Architecture Garden/dropcut-studio/claude-opus/05 - Graded Evidence Certificates - Say What Was Verified and to What Resolution|chapter 05, §7]]. In brief: `runSampledChecks` computes rapid-through-stock, rapid-below-safe-Z and spoilboard penetration; `recertify` stamps the same `verified-to-resolution` status into both `rapidCrash` and `gouge`. A 2.5D rectangular pocket cut to Z = 1 through the built-in dome (peak Z = 14) compiles with:

```text
PASS  gouge                 verified to 0.240 mm grid, 0.020 mm tolerance
```

Two tests assert the gouge pass for normal compiles (`apps/cli/src/compile.test.ts:114`, `packages/analysis/src/pipeline-certificate.test.ts:107`), so the defect is encoded as expected behaviour.

**Pattern not to repeat: fan-out of evidence.** One evidence record must not upgrade several claims. Make evidence per-claim in the type, and add a test that compiles a known-bad program and asserts the corresponding row fails.

## 3. D2 — A shared pipeline that is not shared

`apps/cli/src/compile.ts` exports `compileScript` with this header:

> Keeping the pipeline in one place — rather than duplicated between CLI and app — is what makes "the CLI and the app agree" true by construction rather than by discipline.

`apps/studio/src/state/compileThunk.ts` opens with: *runs the same pipeline the CLI runs — literally the same function.* It does not import `compileScript`. It imports `runScript`, `runPlan`, `lower`, `validate`, `emitRs274`, `emitMakera`, `runSampledChecks`, `recertify` and `estimateTime`, and calls them in the same order, with its own copies of mesh placement, tool lookup by T-number, stock conversion, the dialect branch and the time estimate.

The two copies have already diverged in what they produce. The thunk needs per-motion purposes for render colouring, and `EmittedMotion` does not carry one, so the thunk infers it from the human-readable strategy description:

```ts
purpose: m.provenance.strategyName?.includes("rough") ? "rough" : "finish",
```

The pocket strategy declares `purpose: "rough"`, but its description is `pocket 16.0x16.0 depth 14 in 7 levels, …`, which does not contain "rough", so pocket clearing is coloured as finishing. The renderer's `kindOf` maps `plunge` and `ramp` purposes to their own `MoveKind`s, but the inference only ever yields `rough` or `finish`, so `MoveKind.Plunge` and `MoveKind.Ramp` are never produced in the app.

**Repair.** Have `compileScript` return everything the app needs, including the emitted motions and run summaries it already has, and make the thunk call it and then split the result into cache and store. Carry `purpose` on `EmittedMotion` the same way `toolNumber` is carried, for the same reason the emitter comment gives: reconstructing it downstream is fiddly and easy to get subtly wrong.

**Pattern not to repeat: a comment as the only evidence of sharing.** If two composition roots must agree, one must call the other, or both must call a third function. A test that diffs CLI and app outputs for every shipped example would also catch drift.

## 4. D3 — A non-conservative approximation without a report

`makeCutterLocation` approximates a V-bit as a flat disc of the tip diameter. A cone's flanks extend outwards above the tip; a flat disc of tip radius ignores everything outside that radius. A part feature outside the tip radius but inside the cone's footprint can rise above the cone surface, so the true CL is higher than the reported one, and the planned toolpath drives the cone into the part.

The bull-nose approximation in the same file is documented as conservative and is. The V-bit comment says only *approximate … for now*. Nothing in the error budget or certificate reflects it.

**Pattern not to repeat: approximation without direction.** Every approximation in a safety path should state whether it can only leave material or can also remove too much. A non-conservative approximation should either emit a warning diagnostic when used, or make the affected certificate row `unverifiable`.

## 5. D4–D8 — Declarations without enforcement

These are smaller individually and share one shape: a type, an option or a comment states a property, and nothing checks it.

- **D4.** `packages/analysis/src/certificate.ts` has a `buildCertificate`, `isFullyVerified` and `checkBudgetAgainstRequest` that only tests call; production uses a private builder in `validate.ts`. The analysis builder's input type has a `gougeDepth` field that production never computes. `checkBudgetAgainstRequest`, the function that would warn when a requested finish is below the error budget, is never called by the pipeline.
- **D5.** The comment on `ValidatedProgram` says forging requires *an explicit, greppable double cast*. A scratch type-check under `--strict` shows that `x as ValidatedProgram` with a single cast compiles, even from a bare `MachineProgram`. `unsafeCertify` is re-exported from `@cam/ir`'s public index.
- **D6.** `InterpolationCaps.helical` appears only in `profile.ts`. `lower()` and the emitter both decide arc expressibility independently, and neither consults it.
- **D7.** `RunOptions.timeoutMs` is documented as *enforced by the caller in a worker context*; no worker exists and no caller reads it. The README is candid about this.
- **D8.** The auto-compile middleware calls `inFlight?.abort()` on a compile thunk that never awaits and never reads its signal, so the previous compile has always finished before the abort.

**Pattern not to repeat: unenforced declarations.** An option that nothing reads is worse than no option, because callers believe they have configured something. Either enforce it, assert on it, or delete it until it can be enforced. For each declared property, the cheapest enforcement is a test that tries to violate it.

## 6. D9 — A default that should be a decision

`runPlan` starts the spindle with:

```ts
state: { mode: "cw", speed: op.spindleSpeed ?? rpm(12000) },
```

If a script declares an operation outside `withSpindle`, the program runs at 12,000 rpm without a diagnostic. On a profile whose spindle maximum is below 12,000 the compile fails validation with `spindle.outOfRange` at a speed the user never wrote. Direction is always `cw`, although the IR and two profiles support `ccw`. The project's own convention elsewhere — a bare number works *and warns* — suggests the fix: emit a warning when the default is used, and let `withSpindle` carry direction.

## 7. D11 — Dead diagnostic vocabulary

`DiagnosticCode` in `packages/ir/src/provenance.ts` declares stable codes that the UI, tests and docs key off. Three are emitted nowhere outside tests at the analysed commit:

```text
arc.radiusMismatch      arc.unsupportedPlane      gouge.detected
```

`gouge.detected` is the code D1's missing check would emit. `arc.radiusMismatch` describes a check `validate()` does not perform: `PathBuilder.arcTo` accepts any centre, and nothing verifies that the start and end points are equidistant from it. A stable code with no producer reads as evidence that a check exists. Mark such codes as reserved, or remove them until a producer lands.

## 8. Items that are not debt

Several things look like debt and are deliberate:

- **Main-thread compilation.** Documented in the README as unbuilt, with the pure core already free of DOM and React so it can move to a worker.
- **Naive time estimation.** Labelled `length-over-feed` in every result; `MachineProfile.accel` is reserved for a trapezoidal model.
- **Fixture and holder `not-checked`.** Permanently shown as unchecked; that is the certificate working as designed.
- **Conservative retract floor at stock top.** Costs cycle time and is correct until stock-aware planning (CAM-002) can prove lower links.
- **Unidiomatic drop-cutter code.** Defended in its module comment with measured numbers; it is confined to the kernel.

## 9. The common thread

The repository's best habit is writing down what a component does *not* guarantee. Its debt is concentrated where that habit stopped one step short: the comment was written, and the test that would hold the code to it was not. The four highest-value tests to add are therefore:

1. A known-gouging program must fail the gouge row (D1).
2. The app thunk and the CLI must produce identical G-code and certificates for every shipped example on every profile (D2).
3. A V-bit on a sloped part must either not gouge in simulation or produce a diagnostic (D3).
4. A lint rule must reject `as ValidatedProgram` and `unsafeCertify` outside `@cam/compiler` (D5).

## 10. Evidence and references

- Counterexample compile and certificate output, chapter 05 §7.1.
- `grep -rn "compileScript"` at `f3ebac2`: defined in `apps/cli/src/compile.ts`, used by `main.ts` and `compile.test.ts` only.
- `apps/studio/src/state/compileThunk.ts` — the `strategyName?.includes("rough")` inference.
- `packages/strategies/src/pocket.ts:146-152` — `purpose: "rough"` with a description lacking "rough".
- `packages/viewer-three/src/playback.ts` — `kindOf` mapping.
- Scratch type-check for D5, chapter 04 §4.
- `grep` over `packages apps` for `helical`, `timeoutMs`, `isFullyVerified`, `checkBudgetAgainstRequest`, and each `DiagnosticCode` literal.
- `packages/planner/src/run.ts:95` — spindle default.
