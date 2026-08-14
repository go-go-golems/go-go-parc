--------------------------- MODULE TreatmentCell ---------------------------
(* Abstract model of one paired-evaluation cell in the CoinVault RAGOPT     *)
(* adapter (gecRagoptCellExecutor.Run): execute the arm, assess the         *)
(* deterministic contract and the treatment-exercise report, judge only     *)
(* attributable cells, and persist a native artifact with a typed failure.  *)
(*                                                                          *)
(* The constant Guarded selects the production judge guard (judge only when *)
(* the outcome is ok, the contract holds, and an applicable treatment was   *)
(* exercised) or the mutated guard that ignores exercise. TLC must accept   *)
(* the guarded configuration and reject the mutated one via the             *)
(* JudgeAttribution invariant.                                              *)
EXTENDS Naturals

CONSTANT Guarded

VARIABLES phase, outcome, applicable, contractOK, exercised, judged,
          artifact, completed, failure

vars == <<phase, outcome, applicable, contractOK, exercised, judged,
          artifact, completed, failure>>

Outcomes == {"pending", "ok", "deadline", "infra"}
Failures == {"none", "treatment_not_exercised", "contract_failure",
             "deadline_exceeded", "canonical_execution_failure"}

TypeOK ==
  /\ phase \in {"start", "assess", "judge", "persist", "done"}
  /\ outcome \in Outcomes
  /\ applicable \in BOOLEAN
  /\ contractOK \in BOOLEAN
  /\ exercised \in BOOLEAN
  /\ judged \in BOOLEAN
  /\ artifact \in BOOLEAN
  /\ completed \in BOOLEAN
  /\ failure \in Failures

Init ==
  /\ phase = "start"
  /\ outcome = "pending"
  /\ applicable \in BOOLEAN
  /\ contractOK = FALSE
  /\ exercised = FALSE
  /\ judged = FALSE
  /\ artifact = FALSE
  /\ completed = FALSE
  /\ failure = "none"

(* The arm runs to a terminal outcome, an adapter-owned deadline, or an     *)
(* infrastructure failure.                                                  *)
Execute ==
  /\ phase = "start"
  /\ outcome' \in {"ok", "deadline", "infra"}
  /\ phase' = "assess"
  /\ UNCHANGED <<applicable, contractOK, exercised, judged, artifact,
                 completed, failure>>

(* Contract and treatment reports are computed on every path, including     *)
(* failure paths (buildGECRagoptFailureOutcome also evaluates treatment).   *)
Assess ==
  /\ phase = "assess"
  /\ contractOK' \in BOOLEAN
  /\ exercised' \in IF applicable THEN BOOLEAN ELSE {FALSE}
  /\ phase' = "judge"
  /\ UNCHANGED <<outcome, applicable, judged, artifact, completed, failure>>

JudgeEligible ==
  outcome = "ok" /\ contractOK /\ (applicable => exercised)

MutatedEligible ==
  outcome = "ok" /\ contractOK

(* The judge may or may not be invoked when eligible (judge errors exist),  *)
(* but must never be invoked when ineligible.                               *)
Judge ==
  /\ phase = "judge"
  /\ judged' \in IF (IF Guarded THEN JudgeEligible ELSE MutatedEligible)
                   THEN BOOLEAN ELSE {FALSE}
  /\ phase' = "persist"
  /\ UNCHANGED <<outcome, applicable, contractOK, exercised, artifact,
                 completed, failure>>

(* Persistence assigns the first responsible failure class and always       *)
(* writes the native artifact.                                              *)
Persist ==
  /\ phase = "persist"
  /\ artifact' = TRUE
  /\ failure' = IF outcome = "deadline" THEN "deadline_exceeded"
                ELSE IF outcome = "infra" THEN "canonical_execution_failure"
                ELSE IF ~contractOK THEN "contract_failure"
                ELSE IF applicable /\ ~exercised
                     THEN "treatment_not_exercised"
                ELSE "none"
  /\ completed' = (failure' = "none")
  /\ phase' = "done"
  /\ UNCHANGED <<outcome, applicable, contractOK, exercised, judged>>

Terminated ==
  /\ phase = "done"
  /\ UNCHANGED vars

Next == Execute \/ Assess \/ Judge \/ Persist \/ Terminated

Spec == Init /\ [][Next]_vars

-----------------------------------------------------------------------------
(* Invariants                                                               *)

(* A judge score exists only for an attributable cell: terminal success,    *)
(* valid deterministic contract, and an exercised treatment when one was    *)
(* applicable. This is the invariant the mutated guard violates.            *)
JudgeAttribution ==
  judged => (outcome = "ok" /\ contractOK /\ (applicable => exercised))

(* Every finished cell has persisted its native artifact.                   *)
ArtifactTotal ==
  (phase = "done") => artifact

(* A typed failure and completion are mutually exclusive                    *)
(* (finalizeGECRagoptOutcomeState).                                         *)
FailureNotCompleted ==
  (failure # "none") => ~completed

(* A neutralized treatment on an otherwise clean cell is named exactly      *)
(* treatment_not_exercised, never absorbed into another class.              *)
NotExercisedNamed ==
  (phase = "done" /\ outcome = "ok" /\ contractOK /\ applicable /\ ~exercised)
    => failure = "treatment_not_exercised"

=============================================================================
