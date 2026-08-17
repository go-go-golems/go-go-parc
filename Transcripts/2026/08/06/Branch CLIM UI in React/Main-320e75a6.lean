/-
P08 finite proof sketch.

This file uses only Lean's core language. It models the exact-row fragment of
selection/filter synchronization and one lossy station summary. The assembly
environment did not contain Lean, so the source is supplied as an unchecked
formal development rather than claimed as checked proof evidence.
-/

namespace P08

structure Selection where
  row7  : Bool
  row11 : Bool
  deriving DecidableEq, Repr

abbrev ExactFilter := Selection

/-- The exact filter is just the extensional selected-row set. -/
def get (source : Selection) : ExactFilter := source

/-- `put` establishes the requested exact view. -/
def put (_source : Selection) (view : ExactFilter) : Selection := view

/-- Exact consistency is equality of the two extensional row sets. -/
def Consistent (source : Selection) (view : ExactFilter) : Prop := source = view

/-- Get after put returns the requested view. -/
theorem get_put (source : Selection) (view : ExactFilter) :
    get (put source view) = view := by
  rfl

/-- Putting the current view preserves the source. -/
theorem put_get (source : Selection) :
    put source (get source) = source := by
  rfl

/-- Repeating a put with the same view is idempotent. -/
theorem put_put (source : Selection) (view : ExactFilter) :
    put (put source view) view = put source view := by
  rfl

/-- Right repair preserves a consistent target and otherwise uses `get`. -/
def repairRight (source : Selection) (view : ExactFilter) : ExactFilter :=
  if Consistent source view then view else get source

/-- Left repair preserves a consistent source and otherwise uses `put`. -/
def repairLeft (source : Selection) (view : ExactFilter) : Selection :=
  if Consistent source view then source else put source view

/-- Every right repair establishes exact consistency. -/
theorem repairRight_restores (source : Selection) (view : ExactFilter) :
    Consistent source (repairRight source view) := by
  by_cases h : Consistent source view
  · simp [repairRight, h, Consistent]
  · simp [repairRight, h, Consistent, get]

/-- Every left repair establishes exact consistency. -/
theorem repairLeft_restores (source : Selection) (view : ExactFilter) :
    Consistent (repairLeft source view) view := by
  by_cases h : Consistent source view
  · simp [repairLeft, h, Consistent] at *
  · simp [repairLeft, h, Consistent, put]

/-- A stable right state is unchanged. -/
theorem stable_right_unchanged
    (source : Selection) (view : ExactFilter)
    (h : Consistent source view) :
    repairRight source view = view := by
  simp [repairRight, h]

/-- A stable left state is unchanged. -/
theorem stable_left_unchanged
    (source : Selection) (view : ExactFilter)
    (h : Consistent source view) :
    repairLeft source view = source := by
  simp [repairLeft, h]

/-- One coarse station-summary bit for the two rows at station A. -/
structure StationSummary where
  stationA : Bool
  deriving DecidableEq, Repr

/-- The summary forgets which station-A row was selected. -/
def summarize (source : Selection) : StationSummary :=
  { stationA := source.row7 || source.row11 }

def onlyRow7 : Selection := { row7 := true, row11 := false }
def onlyRow11 : Selection := { row7 := false, row11 := true }

/-- Distinct row selections have the same coarse station summary. -/
theorem station_summary_is_ambiguous :
    onlyRow7 ≠ onlyRow11 ∧ summarize onlyRow7 = summarize onlyRow11 := by
  decide

/--
A reference cell models identity sharing without recursive setters. Both
projections are definitions over the same cell state.
-/
structure Cell (α : Type) where
  value : α

abbrev Projection (α : Type) := Cell α → α

def project {α : Type} : Projection α := fun cell => cell.value

/-- Any two projections using `project` observe the same shared value. -/
theorem identity_projections_agree {α : Type} (cell : Cell α) :
    project cell = project cell := by
  rfl

end P08
