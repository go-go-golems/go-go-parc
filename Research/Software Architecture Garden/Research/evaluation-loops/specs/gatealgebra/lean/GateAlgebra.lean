/-
GateAlgebra — a small faithful model of the lexicographic constraint-domination
gate implemented in ragopt pkg/gate/evaluate.go (v0.0.1) and consumed by
CoinVault and rag-ttc.

Modeled semantics (verified against the source and its goldens):
  * a phase evaluates ALL of its checks (intra-phase totality; the hard-fail
    golden records two failures in one phase);
  * a failed phase terminates evaluation before later phases
    (inter-phase short-circuit via stopAfter);
  * tie-break checks are informational: they are constructed with
    Passed = true and can never change the status.

Theorems (all checked by `lean GateAlgebra.lean`, core Lean only, no mathlib):
  T1  sc_status_eq_strict      — short-circuit evaluation computes the same
                                 status as evaluating every phase; stopAfter is
                                 semantically inert for the verdict.
  T2  failed_phase_inert       — once a phase fails, the decision is entirely
                                 independent of every later phase; no
                                 preference content can rescue a hard failure.
  T3  strict_phase_order_irrelevant / phase_check_order_irrelevant
                               — the STATUS is invariant under reordering
                                 phases and reordering checks inside a phase
                                 (stated as append-commutation); only the
                                 transcript depends on order.
  T4  tiebreak_inert           — appending a phase whose checks all pass on the
                                 report (the tie-break phase by construction)
                                 never changes the status.
  T5  dropped_report_fails     — gate-level missing-data monotonicity: in a
                                 gate that carries the unconditional
                                 complete-pairing identity check, a report from
                                 which any pair has been dropped always fails,
                                 so data loss can never flip fail → pass.
  C1/C2 (counterexamples)      — the failure-rate check ALONE and the
                                 presence-guarded mean-delta check ALONE are
                                 NOT missing-monotone: dropping a failing pair
                                 flips each from fail to pass. The identity
                                 phase is therefore load-bearing, not
                                 redundant bookkeeping.
-/

namespace GateAlgebra

/-! ## Core algebra -/

inductive Status where
  | pass
  | fail
deriving DecidableEq, Repr

structure Check (R : Type) where
  name : String
  pred : R → Bool

structure Phase (R : Type) where
  name : String
  checks : List (Check R)

variable {R : Type}

/-- Intra-phase totality: a phase passes iff every one of its checks passes. -/
def phasePasses (r : R) (p : Phase R) : Bool :=
  p.checks.all (fun c => c.pred r)

/-- Reference evaluator: run every phase, pass iff all phases pass. -/
def evalStrict (phases : List (Phase R)) (r : R) : Status :=
  if phases.all (phasePasses r) then .pass else .fail

/-- Production-shaped evaluator: inter-phase short-circuit (ragopt stopAfter).
    Returns the status and the transcript of phase names actually evaluated. -/
def evalSC : List (Phase R) → R → Status × List String
  | [], _ => (.pass, [])
  | p :: rest, r =>
    if phasePasses r p then
      ((evalSC rest r).fst, p.name :: (evalSC rest r).snd)
    else
      (.fail, [p.name])

/-! ## T1 — short-circuit soundness: stopAfter is inert for the verdict -/

theorem sc_status_eq_strict (phases : List (Phase R)) (r : R) :
    (evalSC phases r).fst = evalStrict phases r := by
  induction phases with
  | nil => rfl
  | cons p rest ih =>
    cases h : phasePasses r p with
    | true => simp [evalSC, evalStrict, List.all_cons, h] at ih ⊢; exact ih
    | false => simp [evalSC, evalStrict, List.all_cons, h]

/-! ## T2 — a failed phase makes every later phase irrelevant -/

theorem failed_phase_inert (p : Phase R) (rest rest' : List (Phase R)) (r : R)
    (h : phasePasses r p = false) :
    evalSC (p :: rest) r = evalSC (p :: rest') r ∧
    (evalSC (p :: rest) r).fst = .fail := by
  constructor
  · simp [evalSC, h]
  · simp [evalSC, h]

/-! ## T3 — order sensitivity: the status is order-free, the transcript is not -/

theorem strict_phase_order_irrelevant (a b : List (Phase R)) (r : R) :
    evalStrict (a ++ b) r = evalStrict (b ++ a) r := by
  simp [evalStrict, List.all_append, Bool.and_comm]

theorem phase_check_order_irrelevant (n : String) (cs ds : List (Check R)) (r : R) :
    phasePasses r ⟨n, cs ++ ds⟩ = phasePasses r ⟨n, ds ++ cs⟩ := by
  simp [phasePasses, List.all_append, Bool.and_comm]

/-- The transcript of the short-circuit evaluator DOES depend on phase order:
    with a failing phase F and a passing phase P, [F, P] evaluates one phase
    and [P, F] evaluates two. Order is diagnostic, not decisional. -/
example :
    let failing : Phase Unit := ⟨"hard", [⟨"c", fun _ => false⟩]⟩
    let passing : Phase Unit := ⟨"target", [⟨"c", fun _ => true⟩]⟩
    (evalSC [failing, passing] ()).snd = ["hard"] ∧
    (evalSC [passing, failing] ()).snd = ["target", "hard"] ∧
    (evalSC [failing, passing] ()).fst = (evalSC [passing, failing] ()).fst := by
  constructor
  · rfl
  · constructor <;> rfl

/-! ## T4 — tie-break phases are inert

ragopt constructs every tie-break check with Passed = true, so the tie-break
phase passes on every report by construction. Appending such a phase never
changes the status. -/

theorem tiebreak_inert (phases : List (Phase R)) (tb : Phase R) (r : R)
    (h : phasePasses r tb = true) :
    evalStrict (phases ++ [tb]) r = evalStrict phases r := by
  simp [evalStrict, List.all_append, List.all_cons, h]

/-- A "rescue" mutant that lets the final phase overwrite the verdict is NOT
    equivalent: concrete witness where strict fails and the mutant passes. -/
def evalRescueMutant (phases : List (Phase R)) (r : R) : Status :=
  match phases.getLast? with
  | some p => if phasePasses r p then .pass else .fail
  | none => .pass

example :
    let failing : Phase Unit := ⟨"hard", [⟨"c", fun _ => false⟩]⟩
    let tb : Phase Unit := ⟨"tie_break", [⟨"provider_calls", fun _ => true⟩]⟩
    evalStrict [failing, tb] () = .fail ∧
    evalRescueMutant [failing, tb] () = .pass := by
  constructor <;> rfl

/-! ## T5 — missing-data monotonicity at gate level

MiniReport models the denominator-relevant slice of a comparison report:
`expected` pairs are scheduled, `complete` pairs were actually joined, and
`failures` of the complete pairs carry a candidate failure. ragopt's
identity-phase check `complete_pairing` requires complete = expected; its
hard-phase failure-rate check compares failures/expected ≤ p/q, expressed here
by cross-multiplication to stay in decidable Nat arithmetic. -/

structure MiniReport where
  expected : Nat
  complete : Nat
  failures : Nat
deriving Repr

def pairingCheck (r : MiniReport) : Bool :=
  decide (r.complete = r.expected)

/-- failures / expected ≤ p / q, cross-multiplied (callers use q > 0). -/
def failureRateCheck (p q : Nat) (r : MiniReport) : Bool :=
  decide (r.failures * q ≤ p * r.expected)

def miniGate (p q : Nat) (r : MiniReport) : Bool :=
  pairingCheck r && failureRateCheck p q r

/-- Dropping one failing pair: it leaves `expected` (the schedule) unchanged. -/
def dropFailing (r : MiniReport) : MiniReport :=
  ⟨r.expected, r.complete - 1, r.failures - 1⟩

/-- T5: any report obtained by dropping a pair from a fully paired schedule
    fails the gate, whatever the failure-rate policy is. Data loss can
    therefore never flip fail → pass. -/
theorem dropped_report_fails (p q : Nat) (r : MiniReport)
    (hpos : 0 < r.expected) (hfull : r.complete = r.expected) :
    miniGate p q (dropFailing r) = false := by
  have h1 : (pairingCheck (dropFailing r)) = false := by
    simp only [pairingCheck, dropFailing]
    exact decide_eq_false (by omega)
  simp [miniGate, h1]

/-- C1: the failure-rate check ALONE is not missing-monotone. With a zero
    failure budget, a schedule of two pairs and one failing complete pair
    fails; dropping the failing pair flips the check to pass, because the
    denominator is the schedule, not the surviving data. -/
example :
    failureRateCheck 0 1 ⟨2, 2, 1⟩ = false ∧
    failureRateCheck 0 1 (dropFailing ⟨2, 2, 1⟩) = true ∧
    miniGate 0 1 (dropFailing ⟨2, 2, 1⟩) = false := by
  constructor
  · rfl
  · constructor <;> rfl

/-! ## Presence-guarded target means: the same story for deltas

MeanReport models the target phase: `sumDelta` over `count` contributing
pairs, against `expected` scheduled pairs. The target check
mean ≥ min is expressed as sumDelta ≥ min · count. -/

structure MeanReport where
  sumDelta : Int
  count : Nat
  expected : Nat
deriving Repr

def presenceCheck (r : MeanReport) : Bool :=
  decide (r.count = r.expected)

def meanDeltaCheck (minDelta : Int) (r : MeanReport) : Bool :=
  decide (minDelta * Int.ofNat r.count ≤ r.sumDelta)

def targetGate (minDelta : Int) (r : MeanReport) : Bool :=
  presenceCheck r && meanDeltaCheck minDelta r

/-- Dropping a contributing pair whose delta was `d`. -/
def dropDelta (d : Int) (r : MeanReport) : MeanReport :=
  ⟨r.sumDelta - d, r.count - 1, r.expected⟩

/-- C2: the mean-delta check ALONE is not missing-monotone: a report with
    deltas {+2, −3} fails mean ≥ 0; dropping the −3 pair flips it to pass.
    The presence check catches exactly this. -/
example :
    meanDeltaCheck 0 ⟨-1, 2, 2⟩ = false ∧
    meanDeltaCheck 0 (dropDelta (-3) ⟨-1, 2, 2⟩) = true ∧
    targetGate 0 (dropDelta (-3) ⟨-1, 2, 2⟩) = false := by
  constructor
  · rfl
  · constructor <;> rfl

/-- T5': the presence-guarded target gate has the same gate-level
    monotonicity: dropping any contributing pair from a fully present report
    fails the gate for every threshold. -/
theorem dropped_target_fails (minDelta d : Int) (r : MeanReport)
    (hpos : 0 < r.expected) (hfull : r.count = r.expected) :
    targetGate minDelta (dropDelta d r) = false := by
  have h1 : presenceCheck (dropDelta d r) = false := by
    simp only [presenceCheck, dropDelta]
    exact decide_eq_false (by omega)
  simp [targetGate, h1]

end GateAlgebra
