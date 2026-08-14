---------------------------- MODULE RunCustody ----------------------------
(***************************************************************************)
(* Abstract model of the ragopt cell journal / exact-coordinate resume     *)
(* protocol (pkg/eval/runner.go execute, pkg/eval/resume.go                *)
(* loadCompletedCells, pkg/runstore/run.go AppendJSONL).                   *)
(*                                                                         *)
(* Abstractions:                                                           *)
(*   - The hash chain is represented by construction: `durable` is a       *)
(*     sequence, and a validated load returns exactly that sequence.       *)
(*     Chain *checking* (tamper detection) is exercised in the Go          *)
(*     prototype, not here; this model checks the protocol above it.       *)
(*   - AppendJSONL's fsync commit boundary is one atomic CommitCell step.  *)
(*   - A crash between the arm's external effect and the journal commit    *)
(*     loses the pending record but not the effect (at-least-once).        *)
(*   - A crash during append may leave a torn (partial) tail line, which   *)
(*     recovery truncates (truncateAndSync in resume.go).                  *)
(*                                                                         *)
(* Mutations (constants, enabled one at a time by .cfg files):             *)
(*   SkipCompletedCheck : resume ignores the durable journal and restarts  *)
(*                        the schedule from the top (models deleting the   *)
(*                        `if _, exists := completed[key]` skip).          *)
(*   SkipTailRecovery   : resume does not truncate a torn tail, so the     *)
(*                        next append concatenates onto a partial record   *)
(*                        and corrupts the journal.                        *)
(***************************************************************************)
EXTENDS Naturals, Sequences, FiniteSets

CONSTANTS SkipCompletedCheck, SkipTailRecovery

\* Two cases x two arms, in ragopt's schedule order (case-major, incumbent
\* then challenger adjacent).
Schedule == <<"c1/inc", "c1/chal", "c2/inc", "c2/chal">>
Coords == {Schedule[i] : i \in 1..Len(Schedule)}

NoCoord == "none"

VARIABLES
    durable,  \* sequence of committed coordinates (the cells.jsonl content)
    torn,     \* TRUE when the journal ends in a partial, uncommitted line
    corrupt,  \* TRUE when an append landed on an unrecovered torn tail
    effects,  \* [Coords -> Nat]: external-effect executions per coordinate
    phase,    \* "running" | "crashed" | "resumed" | "done"
    pending,  \* coordinate whose effect ran but whose commit has not
    crashes   \* number of crashes so far (bounded to 1)

vars == <<durable, torn, corrupt, effects, phase, pending, crashes>>

Range(seq) == {seq[i] : i \in 1..Len(seq)}

Init ==
    /\ durable = <<>>
    /\ torn = FALSE
    /\ corrupt = FALSE
    /\ effects = [c \in Coords |-> 0]
    /\ phase = "running"
    /\ pending = NoCoord
    /\ crashes = 0

\* The writer's next unit of work: first schedule position whose coordinate
\* is not durable. The mutation restarts from the top after resume.
NextMissing ==
    IF SkipCompletedCheck /\ phase = "resumed"
    THEN Schedule[1]
    ELSE LET missing == {i \in 1..Len(Schedule) : Schedule[i] \notin Range(durable)}
         IN IF missing = {}
            THEN NoCoord
            ELSE Schedule[CHOOSE i \in missing : \A j \in missing : i =< j]

\* The arm runs: the external effect happens before any commit exists.
ExecEffect ==
    /\ phase \in {"running", "resumed"}
    /\ pending = NoCoord
    /\ ~corrupt
    /\ NextMissing # NoCoord
    /\ effects[NextMissing] < 4  \* finite-state bound; never reached honestly
    /\ effects' = [effects EXCEPT ![NextMissing] = @ + 1]
    /\ pending' = NextMissing
    /\ UNCHANGED <<durable, torn, corrupt, phase, crashes>>

\* AppendJSONL: write + fsync is the atomic commit boundary. Appending onto
\* an unrecovered torn tail corrupts the record instead of committing it.
CommitCell ==
    /\ phase \in {"running", "resumed"}
    /\ pending # NoCoord
    /\ IF torn /\ SkipTailRecovery
       THEN /\ corrupt' = TRUE
            /\ durable' = durable
       ELSE /\ corrupt' = corrupt
            /\ durable' = Append(durable, pending)
    /\ pending' = NoCoord
    /\ UNCHANGED <<torn, effects, phase, crashes>>

\* Interruption at any point. A pending effect is lost from writer memory
\* (it will be re-executed) but its external effect already happened. The
\* torn flag over-approximates a crash mid-append.
Crash ==
    /\ phase = "running"
    /\ crashes = 0
    /\ crashes' = 1
    /\ phase' = "crashed"
    /\ pending' = NoCoord
    /\ torn' \in {TRUE, FALSE}
    /\ UNCHANGED <<durable, corrupt, effects>>

\* loadCompletedCells: recovery truncates the torn tail (unless mutated),
\* then the schedule resumes against the validated durable prefix.
Recover ==
    /\ phase = "crashed"
    /\ phase' = "resumed"
    /\ torn' = IF SkipTailRecovery THEN torn ELSE FALSE
    /\ UNCHANGED <<durable, corrupt, effects, pending, crashes>>

Finish ==
    /\ phase \in {"running", "resumed"}
    /\ pending = NoCoord
    /\ NextMissing = NoCoord
    /\ phase' = "done"
    /\ UNCHANGED <<durable, torn, corrupt, effects, pending, crashes>>

Terminating == phase = "done" /\ UNCHANGED vars

Next == ExecEffect \/ CommitCell \/ Crash \/ Recover \/ Finish \/ Terminating

Spec == Init /\ [][Next]_vars

----------------------------------------------------------------------------
(* Invariants *)

\* No coordinate is committed twice (resume.go duplicate-key rejection,
\* runner.go completed-map skip).
DurableDistinct ==
    \A i, j \in 1..Len(durable) : (i # j) => durable[i] # durable[j]

\* The sequential writer commits exactly a schedule prefix, so a resumed
\* run continues where the interrupted run stopped and the final journal
\* equals the uninterrupted journal.
DurableIsSchedulePrefix == durable = SubSeq(Schedule, 1, Len(durable))

\* No append ever lands on an unrecovered torn tail.
JournalWellFormed == ~corrupt

\* Terminal completeness: a finished run committed the whole schedule once.
CompletionExact ==
    (phase = "done") => /\ Len(durable) = Len(Schedule)
                        /\ Range(durable) = Coords

\* HONEST NON-CLAIM: this invariant is EXPECTED TO FAIL. A crash between
\* ExecEffect and CommitCell forces re-execution on resume, so external
\* effects are at-least-once, never exactly-once. TLC's counterexample is
\* the demonstration.
AtMostOnceEffects == \A c \in Coords : effects[c] =< 1

============================================================================
