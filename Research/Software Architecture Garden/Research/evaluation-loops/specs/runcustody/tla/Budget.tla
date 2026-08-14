------------------------------- MODULE Budget -------------------------------
(***************************************************************************)
(* Abstract model of a pre-reserving budget accountant, generalizing:      *)
(*   - CoinVault's judge runtime reserveProviderCall (pre-reserve, roll    *)
(*     back on ceiling breach): cmd/coinvault/cmds/knowledge.go:2150-2171  *)
(*   - CoinVault's gecRagoptExecutionBudget (AllowAnswerRun guard, Observe *)
(*     post-hoc accounting, sticky CloseForUncertainProviderSpend):        *)
(*     cmd/coinvault/cmds/knowledge_ragopt.go:1115-1208                   *)
(*                                                                         *)
(* Each action is one mutex-guarded critical section. The point of the     *)
(* model is the *interleaving between* guard and spend: with concurrent    *)
(* workers, a check-then-spend-later design without reservation admits     *)
(* overshoot, while atomic guard+reserve keeps spend within the ceiling.   *)
(* CoinVault's answer budget is safe today because arms are sequential;    *)
(* the judge runtime pre-reserves because it may be driven concurrently.   *)
(*                                                                         *)
(* Mutations:                                                              *)
(*   NoReservation : Admit checks the ceiling but reserves nothing, so     *)
(*                   two concurrent admissions overshoot the ceiling.      *)
(*   IgnoreClose   : Admit ignores the sticky close, so work starts after  *)
(*                   spend became unprovable.                              *)
(***************************************************************************)
EXTENDS Naturals, FiniteSets

CONSTANTS MaxCalls, MaxAttempts, NoReservation, IgnoreClose

Workers == {"w1", "w2"}

VARIABLES
    spent,             \* completed provider calls
    reserved,          \* admitted-but-not-completed reservations
    closed,            \* sticky conservative close latch
    startedAfterClose, \* admissions that happened while closed (must be 0)
    pc,                \* [Workers -> {"idle","holding"}]
    attempts           \* [Workers -> Nat], bounded by MaxAttempts

vars == <<spent, reserved, closed, startedAfterClose, pc, attempts>>

Init ==
    /\ spent = 0
    /\ reserved = 0
    /\ closed = FALSE
    /\ startedAfterClose = 0
    /\ pc = [w \in Workers |-> "idle"]
    /\ attempts = [w \in Workers |-> 0]

\* One atomic admission: ceiling guard plus (unless mutated) reservation.
Admit(w) ==
    /\ pc[w] = "idle"
    /\ attempts[w] < MaxAttempts
    /\ IgnoreClose \/ ~closed
    /\ spent + (IF NoReservation THEN 0 ELSE reserved) < MaxCalls
    /\ reserved' = IF NoReservation THEN reserved ELSE reserved + 1
    /\ pc' = [pc EXCEPT ![w] = "holding"]
    /\ attempts' = [attempts EXCEPT ![w] = @ + 1]
    /\ startedAfterClose' =
           IF closed THEN startedAfterClose + 1 ELSE startedAfterClose
    /\ UNCHANGED <<spent, closed>>

\* The admitted call completes and its cost lands.
Complete(w) ==
    /\ pc[w] = "holding"
    /\ spent' = spent + 1
    /\ reserved' = IF NoReservation THEN reserved ELSE reserved - 1
    /\ pc' = [pc EXCEPT ![w] = "idle"]
    /\ UNCHANGED <<closed, startedAfterClose, attempts>>

\* The admitted call is abandoned; its reservation is rolled back.
Rollback(w) ==
    /\ pc[w] = "holding"
    /\ reserved' = IF NoReservation THEN reserved ELSE reserved - 1
    /\ pc' = [pc EXCEPT ![w] = "idle"]
    /\ UNCHANGED <<spent, closed, startedAfterClose, attempts>>

\* CloseForUncertainProviderSpend: sticky, environment-triggered at any time.
Close ==
    /\ ~closed
    /\ closed' = TRUE
    /\ UNCHANGED <<spent, reserved, startedAfterClose, pc, attempts>>

Next ==
    \/ \E w \in Workers : Admit(w) \/ Complete(w) \/ Rollback(w)
    \/ Close

Spec == Init /\ [][Next]_vars

----------------------------------------------------------------------------
(* Invariants *)

\* Completed spend never exceeds the ceiling.
SpentWithinCeiling == spent =< MaxCalls

\* Reservation accounting: outstanding admissions cannot overshoot either.
ReservationSound == spent + reserved =< MaxCalls

\* Once spend is unprovable, no further work starts.
NoStartAfterClose == startedAfterClose = 0

==============================================================================
