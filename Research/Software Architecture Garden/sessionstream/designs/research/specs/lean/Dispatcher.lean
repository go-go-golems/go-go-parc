/-
  Dispatcher.lean

  Abstract transition kernel of the Bounded Asynchronous Observer
  Dispatcher with inductive invariant proofs — same Step relation as the
  Coq development (specs/coq/Dispatcher.v) and the TLA+ model:

    submitAccepted / submitDropped / submitRejected
    closeFirst / closeAgain / deliver / workerExit / waitReturn

  Proved for arbitrary capacity, item type, and run length:
    D1 queue bound            D3/D8 admitted = offered ++ queue
    D6 close at most once     D7 no queue growth after close
    D8 drain completeness     D9 wait only after worker exit
    I8 dropped monotone
-/

namespace Dispatcher

variable {Item : Type}

structure State (Item : Type) where
  queue      : List Item
  admitted   : List Item
  offered    : List Item
  dropped    : Nat
  closing    : Bool
  closeCount : Nat
  workerDone : Bool
  waited     : Bool

inductive Step (cap : Nat) : State Item → State Item → Prop where
  | submitAccepted (s : State Item) (x : Item)
      (hclosing : s.closing = false) (hcap : s.queue.length < cap) :
      Step cap s { s with queue := s.queue ++ [x], admitted := s.admitted ++ [x] }
  | submitDropped (s : State Item) (x : Item)
      (hclosing : s.closing = false) (hfull : ¬ s.queue.length < cap) :
      Step cap s { s with dropped := s.dropped + 1 }
  | submitRejected (s : State Item) (x : Item)
      (hclosing : s.closing = true) :
      Step cap s s
  | closeFirst (s : State Item) (h : s.closing = false) :
      Step cap s { s with closing := true, closeCount := s.closeCount + 1 }
  | closeAgain (s : State Item) (h : s.closing = true) :
      Step cap s s
  | deliver (s : State Item) (x : Item) (rest : List Item)
      (h : s.queue = x :: rest) :
      Step cap s { s with queue := rest, offered := s.offered ++ [x] }
  | workerExit (s : State Item) (hc : s.closing = true) (hq : s.queue = []) :
      Step cap s { s with workerDone := true }
  | waitReturn (s : State Item) (h : s.workerDone = true) :
      Step cap s { s with waited := true }

inductive Reachable (cap : Nat) : State Item → Prop where
  | init : Reachable cap ⟨[], [], [], 0, false, 0, false, false⟩
  | step {s t : State Item} : Reachable cap s → Step cap s t → Reachable cap t

/-- The invariant bundle.  The key strengthening clause is `shape`:
    the admitted history always factors as `offered ++ queue`. -/
structure Inv (cap : Nat) (s : State Item) : Prop where
  bound      : s.queue.length ≤ cap
  shape      : s.offered ++ s.queue = s.admitted
  closeOnce  : s.closeCount ≤ 1
  closedIff  : s.closing = true ↔ s.closeCount = 1
  exitMeans  : s.workerDone = true → s.closing = true ∧ s.queue = []
  waitMeans  : s.waited = true → s.workerDone = true

theorem step_preserves {cap : Nat} {s t : State Item}
    (h : Step cap s t) (ih : Inv cap s) : Inv cap t := by
  obtain ⟨hb, hsh, hc, hiff, hex, hwt⟩ := ih
  cases h with
  | submitAccepted x hclosing hcap =>
      refine ⟨?_, ?_, ?_, ?_, ?_, ?_⟩
      · show (s.queue ++ [x]).length ≤ cap
        simp [List.length_append]; omega
      · show s.offered ++ (s.queue ++ [x]) = s.admitted ++ [x]
        rw [← List.append_assoc, hsh]
      · show s.closeCount ≤ 1; exact hc
      · show s.closing = true ↔ s.closeCount = 1; exact hiff
      · show s.workerDone = true → s.closing = true ∧ s.queue ++ [x] = []
        intro hd; obtain ⟨hc2, _⟩ := hex hd
        rw [hc2] at hclosing; simp at hclosing
      · show s.waited = true → s.workerDone = true; exact hwt
  | submitDropped x hclosing hfull =>
      refine ⟨?_, ?_, ?_, ?_, ?_, ?_⟩
      · show s.queue.length ≤ cap; exact hb
      · show s.offered ++ s.queue = s.admitted; exact hsh
      · show s.closeCount ≤ 1; exact hc
      · show s.closing = true ↔ s.closeCount = 1; exact hiff
      · show s.workerDone = true → s.closing = true ∧ s.queue = []
        intro hd; obtain ⟨hc2, _⟩ := hex hd
        rw [hc2] at hclosing; simp at hclosing
      · show s.waited = true → s.workerDone = true; exact hwt
  | submitRejected x hclosing =>
      exact ⟨hb, hsh, hc, hiff, hex, hwt⟩
  | closeFirst hclosing =>
      have hc0 : s.closeCount = 0 := by
        have hn1 : s.closeCount ≠ 1 := by
          intro heq
          have htrue := hiff.mpr heq
          rw [htrue] at hclosing; simp at hclosing
        omega
      refine ⟨?_, ?_, ?_, ?_, ?_, ?_⟩
      · show s.queue.length ≤ cap; exact hb
      · show s.offered ++ s.queue = s.admitted; exact hsh
      · show s.closeCount + 1 ≤ 1; omega
      · show true = true ↔ s.closeCount + 1 = 1
        constructor
        · intro _; rw [hc0]
        · intro _; rfl
      · show s.workerDone = true → true = true ∧ s.queue = []
        intro hd; obtain ⟨_, hq2⟩ := hex hd; exact ⟨rfl, hq2⟩
      · show s.waited = true → s.workerDone = true; exact hwt
  | closeAgain hclosing =>
      exact ⟨hb, hsh, hc, hiff, hex, hwt⟩
  | deliver x rest hq =>
      refine ⟨?_, ?_, ?_, ?_, ?_, ?_⟩
      · show rest.length ≤ cap
        rw [hq] at hb; simp at hb; omega
      · show (s.offered ++ [x]) ++ rest = s.admitted
        rw [List.append_assoc]
        show s.offered ++ (x :: rest) = s.admitted
        rw [← hq]; exact hsh
      · show s.closeCount ≤ 1; exact hc
      · show s.closing = true ↔ s.closeCount = 1; exact hiff
      · show s.workerDone = true → s.closing = true ∧ rest = []
        intro hd; obtain ⟨_, hq2⟩ := hex hd
        rw [hq] at hq2; simp at hq2
      · show s.waited = true → s.workerDone = true; exact hwt
  | workerExit hcl hq =>
      refine ⟨?_, ?_, ?_, ?_, ?_, ?_⟩
      · show s.queue.length ≤ cap; exact hb
      · show s.offered ++ s.queue = s.admitted; exact hsh
      · show s.closeCount ≤ 1; exact hc
      · show s.closing = true ↔ s.closeCount = 1; exact hiff
      · show true = true → s.closing = true ∧ s.queue = []
        intro _; exact ⟨hcl, hq⟩
      · show s.waited = true → true = true
        intro _; rfl
  | waitReturn hd =>
      refine ⟨?_, ?_, ?_, ?_, ?_, ?_⟩
      · show s.queue.length ≤ cap; exact hb
      · show s.offered ++ s.queue = s.admitted; exact hsh
      · show s.closeCount ≤ 1; exact hc
      · show s.closing = true ↔ s.closeCount = 1; exact hiff
      · show s.workerDone = true → s.closing = true ∧ s.queue = []
        exact hex
      · show true = true → s.workerDone = true
        intro _; exact hd

theorem reachable_inv {cap : Nat} {s : State Item} (h : Reachable cap s) : Inv cap s := by
  induction h with
  | init =>
      exact ⟨by simp, rfl, by simp, by simp,
             fun h => by simp at h, fun h => by simp at h⟩
  | step _ hst ih => exact step_preserves hst ih

/-- Single-step monotonicity of the drop counter (I8). -/
theorem Step.dropped_mono {cap : Nat} {s t : State Item}
    (h : Step cap s t) : s.dropped ≤ t.dropped := by
  cases h <;> simp <;> omega

/-- Once closing, always closing. -/
theorem Step.closing_sticky {cap : Nat} {s t : State Item}
    (h : Step cap s t) (hc : s.closing = true) : t.closing = true := by
  cases h with
  | submitAccepted x hclosing hcap => rw [hc] at hclosing; simp at hclosing
  | submitDropped x hclosing hfull => rw [hc] at hclosing; simp at hclosing
  | closeFirst hclosing => rfl
  | submitRejected x hclosing => exact hc
  | closeAgain hclosing => exact hc
  | deliver x rest hq => exact hc
  | workerExit hcl hq => exact hc
  | waitReturn hd => exact hc

/-- No queue growth after close (D7, I2/I5): with admission closed, a step
    can only shrink or keep the queue. -/
theorem Step.closed_shrinks {cap : Nat} {s t : State Item}
    (h : Step cap s t) (hc : s.closing = true) :
    t.queue.length ≤ s.queue.length := by
  cases h with
  | submitAccepted x hclosing hcap => rw [hc] at hclosing; simp at hclosing
  | submitDropped x hclosing hfull => rw [hc] at hclosing; simp at hclosing
  | deliver x rest hq =>
      show rest.length ≤ s.queue.length
      rw [hq]; simp
  | submitRejected x hclosing => show s.queue.length ≤ s.queue.length; omega
  | closeFirst hclosing => show s.queue.length ≤ s.queue.length; omega
  | closeAgain hclosing => show s.queue.length ≤ s.queue.length; omega
  | workerExit hcl hq => show s.queue.length ≤ s.queue.length; omega
  | waitReturn hd => show s.queue.length ≤ s.queue.length; omega

inductive Steps (cap : Nat) : State Item → State Item → Prop where
  | refl (s : State Item) : Steps cap s s
  | cons {s t u : State Item} : Step cap s t → Steps cap t u → Steps cap s u

theorem Steps.dropped_mono {cap : Nat} {s t : State Item}
    (h : Steps cap s t) : s.dropped ≤ t.dropped := by
  induction h with
  | refl s => omega
  | cons hst hss ih => exact Nat.le_trans (Step.dropped_mono hst) ih

theorem Steps.closing_sticky {cap : Nat} {s t : State Item}
    (h : Steps cap s t) (hc : s.closing = true) : t.closing = true := by
  induction h with
  | refl s => exact hc
  | cons hst hss ih => exact ih (Step.closing_sticky hst hc)

theorem Steps.closed_shrinks {cap : Nat} {s t : State Item}
    (h : Steps cap s t) (hc : s.closing = true) :
    t.queue.length ≤ s.queue.length := by
  induction h with
  | refl s => omega
  | cons hst hss ih =>
      exact Nat.le_trans (ih (Step.closing_sticky hst hc))
                         (Step.closed_shrinks hst hc)

/-- D1 -/ theorem queue_bound {cap : Nat} {s : State Item}
    (h : Reachable cap s) : s.queue.length ≤ cap :=
  (reachable_inv h).bound

/-- D3 shape: admitted factors as offered ++ queue. -/
theorem admitted_factors {cap : Nat} {s : State Item}
    (h : Reachable cap s) : s.admitted = s.offered ++ s.queue :=
  (reachable_inv h).shape.symm

/-- D3: offered is always a prefix of admitted. -/
theorem offered_is_prefix {cap : Nat} {s : State Item}
    (h : Reachable cap s) : ∃ rest, s.admitted = s.offered ++ rest :=
  ⟨s.queue, admitted_factors h⟩

/-- D6, I4 -/ theorem close_once {cap : Nat} {s : State Item}
    (h : Reachable cap s) : s.closeCount ≤ 1 :=
  (reachable_inv h).closeOnce

/-- D7, I2/I5 -/ theorem no_send_after_close {cap : Nat} {s t : State Item}
    (_hr : Reachable cap s) (hst : Steps cap s t) (hc : s.closing = true) :
    t.queue.length ≤ s.queue.length :=
  Steps.closed_shrinks hst hc

/-- D8, I7: when the worker exits, everything admitted has been offered. -/
theorem drain_complete {cap : Nat} {s : State Item}
    (h : Reachable cap s) (hd : s.workerDone = true) :
    s.offered = s.admitted ∧ s.closing = true := by
  obtain ⟨hb, hsh, hc, hiff, hex, hwt⟩ := reachable_inv h
  obtain ⟨hcl, hq⟩ := hex hd
  refine ⟨?_, hcl⟩
  rw [hq] at hsh
  simp at hsh
  exact hsh

/-- D9 -/ theorem wait_after_exit {cap : Nat} {s : State Item}
    (h : Reachable cap s) (hw : s.waited = true) : s.workerDone = true :=
  (reachable_inv h).waitMeans hw

/-- I8 -/ theorem dropped_monotone {cap : Nat} {s t : State Item}
    (_hr : Reachable cap s) (hst : Steps cap s t) : s.dropped ≤ t.dropped :=
  Steps.dropped_mono hst

end Dispatcher

-- Audit: which axioms do the proofs depend on?
#print axioms Dispatcher.queue_bound
#print axioms Dispatcher.admitted_factors
#print axioms Dispatcher.drain_complete
#print axioms Dispatcher.no_send_after_close
#print axioms Dispatcher.wait_after_exit
#print axioms Dispatcher.close_once
#print axioms Dispatcher.dropped_monotone
