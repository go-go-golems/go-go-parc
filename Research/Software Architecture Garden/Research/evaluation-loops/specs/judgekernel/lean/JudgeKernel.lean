/-
JudgeKernel.lean — kernel-checked statements of the judge admission
invariants over a faithful miniature of the Go data types.

The miniature abstracts evidence labels to Nat indices below a bound
size, reasons to a nonemptiness flag, and statement binding to the 1-based
statement number carried on the wire. `check` mirrors the order-sensitive
admission walk in admit.go; the theorems establish that a payload accepted
by the checker satisfies the structural rules, and that the computed
faithfulness numerator can never exceed its denominator.

Checked with: lean 4.33.0 (core only, no mathlib).
-/

namespace JudgeKernel

structure Verdict where
  statement      : Nat
  supported      : Bool
  evidence       : List Nat
  reasonNonempty : Bool

/-- The faithfulness numerator: supported verdicts, counted. -/
def supportedCount : List Verdict → Nat
  | [] => 0
  | v :: vs => (if v.supported then 1 else 0) + supportedCount vs

/-- Faithfulness is bounded: the numerator never exceeds the denominator,
so `supported / total ≤ 1` whenever the denominator is nonzero. -/
theorem supportedCount_le_length (vs : List Verdict) :
    supportedCount vs ≤ vs.length := by
  induction vs with
  | nil => simp [supportedCount]
  | cons v vs ih =>
    simp only [supportedCount, List.length_cons]
    cases v.supported <;> simp <;> omega

/-- Vacuity: zero verdicts have numerator zero (0/0, never a laundered 1). -/
theorem supportedCount_nil : supportedCount [] = 0 := rfl

/-- One verdict passes when it is bound to the expected 1-based statement
number, carries a nonempty reason, cites only labels inside the bound,
and — if supported — cites at least one label. -/
def verdictOK (bound index : Nat) (v : Verdict) : Bool :=
  (v.statement == index + 1) &&
  v.reasonNonempty &&
  v.evidence.all (fun e => decide (e < bound)) &&
  (!v.supported || !v.evidence.isEmpty)

/-- The order-sensitive admission walk. -/
def checkFrom (bound index : Nat) : List Verdict → Bool
  | [] => true
  | v :: vs => verdictOK bound index v && checkFrom bound (index + 1) vs

/-- Full admission: count match plus the walk from statement one. -/
def check (n bound : Nat) (vs : List Verdict) : Bool :=
  (vs.length == n) && checkFrom bound 0 vs

/-- Admission soundness, count rule: an accepted payload has exactly one
verdict per statement. -/
theorem check_length {n bound : Nat} {vs : List Verdict}
    (h : check n bound vs = true) : vs.length = n := by
  have hsplit := (Bool.and_eq_true _ _).mp h
  exact eq_of_beq hsplit.1

/-- Admission soundness, per-verdict rules: every accepted verdict has a
nonempty reason, cites only labels inside the bound, and supported
verdicts cite at least one label. -/
theorem checkFrom_sound {bound : Nat} :
    ∀ {index : Nat} {vs : List Verdict}, checkFrom bound index vs = true →
      ∀ v ∈ vs,
        v.reasonNonempty = true ∧
        (∀ e ∈ v.evidence, e < bound) ∧
        (v.supported = true → v.evidence ≠ []) := by
  intro index vs
  induction vs generalizing index with
  | nil => intro _ v hv; cases hv
  | cons w ws ih =>
    intro h v hv
    have hsplit := (Bool.and_eq_true _ _).mp h
    cases hv with
    | head =>
      have hok := hsplit.1
      have h1 := (Bool.and_eq_true _ _).mp hok
      have h2 := (Bool.and_eq_true _ _).mp h1.1
      have h3 := (Bool.and_eq_true _ _).mp h2.1
      refine ⟨h3.2, ?_, ?_⟩
      · intro e he
        exact of_decide_eq_true (List.all_eq_true.mp h2.2 e he)
      · intro hsup hnil
        have hlast := h1.2
        rw [hsup, hnil] at hlast
        simp [List.isEmpty] at hlast
    | tail _ hmem =>
      exact ih hsplit.2 v hmem

/-- Admission soundness, numbering rule: the i-th accepted verdict is bound
to statement number `index + i + 1`, so verdicts cover the statements in
order with no gaps and no duplicates. -/
theorem checkFrom_numbering {bound : Nat} :
    ∀ {index : Nat} {vs : List Verdict}, checkFrom bound index vs = true →
      ∀ i, (h : i < vs.length) → (vs[i]'h).statement = index + i + 1 := by
  intro index vs
  induction vs generalizing index with
  | nil => intro _ i h; cases h
  | cons w ws ih =>
    intro h i hi
    have hsplit := (Bool.and_eq_true _ _).mp h
    cases i with
    | zero =>
      have hok := hsplit.1
      have h1 := (Bool.and_eq_true _ _).mp hok
      have h2 := (Bool.and_eq_true _ _).mp h1.1
      have h3 := (Bool.and_eq_true _ _).mp h2.1
      have := eq_of_beq h3.1
      simpa using this
    | succ j =>
      have hj : j < ws.length := Nat.lt_of_succ_lt_succ hi
      have := ih hsplit.2 j hj
      simp only [List.getElem_cons_succ]
      omega

/-- Full-admission corollary: an accepted payload of n statements is bound
1..n in order and satisfies every per-verdict rule. -/
theorem check_sound {n bound : Nat} {vs : List Verdict}
    (h : check n bound vs = true) :
    vs.length = n ∧
    (∀ i, (hi : i < vs.length) → (vs[i]'hi).statement = i + 1) ∧
    (∀ v ∈ vs,
      v.reasonNonempty = true ∧
      (∀ e ∈ v.evidence, e < bound) ∧
      (v.supported = true → v.evidence ≠ [])) := by
  have hsplit := (Bool.and_eq_true _ _).mp h
  refine ⟨check_length h, ?_, checkFrom_sound hsplit.2⟩
  intro i hi
  have := checkFrom_numbering hsplit.2 i hi
  omega

end JudgeKernel
