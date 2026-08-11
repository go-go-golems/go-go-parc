---- MODULE Dispatcher ----
(***************************************************************************)
(* Bounded Asynchronous Observer Dispatcher -- concurrent model.           *)
(*                                                                         *)
(* Models the reference Go implementation from the Garden design           *)
(* "01 - Bounded Asynchronous Observer Dispatcher":                        *)
(*                                                                         *)
(*   - producers call TrySubmit (mutex + select/default)                   *)
(*   - one closer calls Close (mutex + closing flag + close(queue))        *)
(*   - one worker ranges over the queue and invokes the callback; the      *)
(*     callback may panic (recovered per call)                             *)
(*   - one waiter calls Wait (wg.Wait)                                     *)
(*                                                                         *)
(* The mutex is modeled explicitly (lockOwner) so that the safety of the   *)
(* submit/close race is *checked*, not assumed.  The critical-section      *)
(* decision (closing check + nonblocking send) is one atomic step because  *)
(* the Go mutex makes it atomic with respect to Close.                     *)
(*                                                                         *)
(* CONSTANT Guarded:                                                       *)
(*   TRUE  = the real design (closing checked before send)                 *)
(*   FALSE = the racy variant (no closing check): TLC must find a          *)
(*           send-after-close execution.  This is the "does the harness    *)
(*           have teeth" experiment.                                       *)
(*                                                                         *)
(* Contract mapping (design doc):                                          *)
(*   D1 QueueBound         D4 Accounting + DropOnlyWhenFull (definitional) *)
(*   D3 OrderOK            D6 CloseOnce + ClosingSticky                    *)
(*   D7 NoSendAfterClose   D8 DrainOK      D9 WaitOK                       *)
(*   D5 WorkerDeliverPanic action + Termination under fairness             *)
(*   D2 (nonblocking submit) is structural: SubmitAcquire only awaits the  *)
(*   lock, never queue space; deadlock-freedom of Spec confirms it.        *)
(***************************************************************************)
EXTENDS Integers, Sequences, FiniteSets, TLC

CONSTANTS
    Capacity,          \* queue capacity, positive
    Producers,         \* set of producer identities
    SubmitsPerProc,    \* submit attempts per producer (bounds the model)
    CloseCalls,        \* number of Close() calls the closer performs (idempotence)
    Guarded            \* TRUE = closing checked before send (the real design)

ASSUME Capacity \in Nat \ {0}
ASSUME Producers # {}
ASSUME SubmitsPerProc \in Nat \ {0}
ASSUME CloseCalls \in Nat \ {0}
ASSUME Guarded \in BOOLEAN

Procs == Producers \cup {"closer", "worker", "waiter"}

VARIABLES
    queue,            \* bounded FIFO of admitted items; closed when closing
    closing,          \* admission-closed flag (models flag AND channel closure)
    dropped,          \* overflow drop counter (monotone)
    rejected,         \* post-close rejection counter
    attempts,         \* total submit attempts (history, for Accounting)
    admitted,         \* history: accepted items in admission order
    offered,          \* history: items whose callback was invoked, in order
    panics,           \* recovered callback panics
    workerDone,       \* worker exited
    waiterDone,       \* Wait returned
    lockOwner,        \* "none" or pid: the admission mutex
    pc,               \* control location per process
    submitK,          \* attempts so far per producer
    closesDone,       \* Close calls performed so far
    current,          \* item the worker is currently offering; <<>> = none
    sendsAfterClose,  \* ERROR counter: enqueue while closing (must stay 0)
    closeCount        \* history: effective queue closes (must stay <= 1)

vars == <<queue, closing, dropped, rejected, attempts, admitted, offered,
          panics, workerDone, waiterDone, lockOwner, pc, submitK, closesDone,
          current, sendsAfterClose, closeCount>>

ItemOf(p) == <<p, submitK[p] + 1>>

Init ==
    /\ queue = <<>>
    /\ closing = FALSE
    /\ dropped = 0
    /\ rejected = 0
    /\ attempts = 0
    /\ admitted = <<>>
    /\ offered = <<>>
    /\ panics = 0
    /\ workerDone = FALSE
    /\ waiterDone = FALSE
    /\ lockOwner = "none"
    /\ pc = [p \in Procs |-> CASE p \in Producers -> "ready"
                               [] p = "closer"   -> "cready"
                               [] p = "worker"   -> "wrecv"
                               [] OTHER          -> "wait"]
    /\ submitK = [p \in Producers |-> 0]
    /\ closesDone = 0
    /\ current = <<>>
    /\ sendsAfterClose = 0
    /\ closeCount = 0

(***************************************************************************)
(* Producers                                                               *)
(***************************************************************************)

SubmitAcquire(p) ==
    /\ pc[p] = "ready"
    /\ submitK[p] < SubmitsPerProc
    /\ lockOwner = "none"                  \* awaits ONLY the mutex (D2)
    /\ lockOwner' = p
    /\ pc' = [pc EXCEPT ![p] = "submit"]
    /\ UNCHANGED <<queue, closing, dropped, rejected, attempts, admitted,
                   offered, panics, workerDone, waiterDone, submitK,
                   closesDone, current, sendsAfterClose, closeCount>>

SubmitBody(p) ==
    /\ pc[p] = "submit"
    /\ attempts' = attempts + 1
    /\ IF Guarded
       THEN \* One atomic decision under d.mu: closing check, then select/default.
            IF closing
            THEN /\ rejected' = rejected + 1
                 /\ UNCHANGED <<queue, dropped, admitted, sendsAfterClose>>
            ELSE IF Len(queue) < Capacity
                 THEN /\ queue' = Append(queue, ItemOf(p))
                      /\ admitted' = Append(admitted, ItemOf(p))
                      /\ UNCHANGED <<dropped, rejected, sendsAfterClose>>
                 ELSE /\ dropped' = dropped + 1
                      /\ UNCHANGED <<queue, admitted, rejected, sendsAfterClose>>
       ELSE \* Racy variant: no closing check before the send.
            IF Len(queue) < Capacity
            THEN /\ queue' = Append(queue, ItemOf(p))
                 /\ admitted' = Append(admitted, ItemOf(p))
                 /\ sendsAfterClose' = IF closing THEN sendsAfterClose + 1
                                                  ELSE sendsAfterClose
                 /\ UNCHANGED <<dropped, rejected>>
            ELSE /\ dropped' = dropped + 1
                 /\ UNCHANGED <<queue, admitted, rejected, sendsAfterClose>>
    /\ submitK' = [submitK EXCEPT ![p] = submitK[p] + 1]
    /\ pc' = [pc EXCEPT ![p] = "release"]
    /\ UNCHANGED <<closing, offered, panics, workerDone, waiterDone,
                   lockOwner, closesDone, current, closeCount>>

SubmitRelease(p) ==
    /\ pc[p] = "release"
    /\ lockOwner' = "none"
    /\ pc' = [pc EXCEPT ![p] = IF submitK[p] = SubmitsPerProc
                               THEN "done" ELSE "ready"]
    /\ UNCHANGED <<queue, closing, dropped, rejected, attempts, admitted,
                   offered, panics, workerDone, waiterDone, submitK,
                   closesDone, current, sendsAfterClose, closeCount>>

(***************************************************************************)
(* Closer                                                                  *)
(***************************************************************************)

CloseAcquire ==
    /\ pc["closer"] = "cready"
    /\ closesDone < CloseCalls
    /\ lockOwner = "none"
    /\ lockOwner' = "closer"
    /\ pc' = [pc EXCEPT !["closer"] = "close"]
    /\ UNCHANGED <<queue, closing, dropped, rejected, attempts, admitted,
                   offered, panics, workerDone, waiterDone, submitK,
                   closesDone, current, sendsAfterClose, closeCount>>

CloseBody ==
    /\ pc["closer"] = "close"
    /\ IF closing
       THEN UNCHANGED <<closing, closeCount>>        \* idempotent (D6)
       ELSE /\ closing' = TRUE
            /\ closeCount' = closeCount + 1
    /\ closesDone' = closesDone + 1
    /\ pc' = [pc EXCEPT !["closer"] = "crelease"]
    /\ UNCHANGED <<queue, dropped, rejected, attempts, admitted, offered,
                   panics, workerDone, waiterDone, lockOwner, submitK,
                   current, sendsAfterClose>>

CloseRelease ==
    /\ pc["closer"] = "crelease"
    /\ lockOwner' = "none"
    /\ pc' = [pc EXCEPT !["closer"] = IF closesDone = CloseCalls
                                      THEN "cdone" ELSE "cready"]
    /\ UNCHANGED <<queue, closing, dropped, rejected, attempts, admitted,
                   offered, panics, workerDone, waiterDone, submitK,
                   closesDone, current, sendsAfterClose, closeCount>>

(***************************************************************************)
(* Worker                                                                  *)
(***************************************************************************)

WorkerReceive ==
    /\ pc["worker"] = "wrecv"
    /\ Len(queue) > 0
    /\ current' = Head(queue)
    /\ queue' = Tail(queue)
    /\ pc' = [pc EXCEPT !["worker"] = "wdeliver"]
    /\ UNCHANGED <<closing, dropped, rejected, attempts, admitted, offered,
                   panics, workerDone, waiterDone, lockOwner, submitK,
                   closesDone, sendsAfterClose, closeCount>>

WorkerDeliverOK ==
    /\ pc["worker"] = "wdeliver"
    /\ offered' = Append(offered, current)
    /\ pc' = [pc EXCEPT !["worker"] = "wrecv"]
    /\ UNCHANGED <<queue, closing, dropped, rejected, attempts, admitted,
                   panics, workerDone, waiterDone, lockOwner, current,
                   submitK, closesDone, sendsAfterClose, closeCount>>

WorkerDeliverPanic ==                    \* D5: recovered; worker continues
    /\ pc["worker"] = "wdeliver"
    /\ offered' = Append(offered, current)  \* D8: "offered" = invoked
    /\ panics' = panics + 1
    /\ pc' = [pc EXCEPT !["worker"] = "wrecv"]
    /\ UNCHANGED <<queue, closing, dropped, rejected, attempts, admitted,
                   workerDone, waiterDone, lockOwner, current, submitK,
                   closesDone, sendsAfterClose, closeCount>>

WorkerExit ==                            \* range ends: closed AND drained
    /\ pc["worker"] = "wrecv"
    /\ closing
    /\ Len(queue) = 0
    /\ workerDone' = TRUE
    /\ pc' = [pc EXCEPT !["worker"] = "wdone"]
    /\ UNCHANGED <<queue, closing, dropped, rejected, attempts, admitted,
                   offered, panics, waiterDone, lockOwner, current, submitK,
                   closesDone, sendsAfterClose, closeCount>>

(***************************************************************************)
(* Waiter                                                                  *)
(***************************************************************************)

WaitReturn ==
    /\ pc["waiter"] = "wait"
    /\ workerDone
    /\ waiterDone' = TRUE
    /\ pc' = [pc EXCEPT !["waiter"] = "done"]
    /\ UNCHANGED <<queue, closing, dropped, rejected, attempts, admitted,
                   offered, panics, workerDone, lockOwner, current, submitK,
                   closesDone, sendsAfterClose, closeCount>>

(***************************************************************************)
(* Specification                                                           *)
(***************************************************************************)

AllDone == /\ \A p \in Producers : pc[p] = "done"
           /\ pc["closer"] = "cdone"
           /\ pc["worker"] = "wdone"
           /\ pc["waiter"] = "done"

Terminal == AllDone /\ UNCHANGED vars

Next ==
    \/ \E p \in Producers :
        SubmitAcquire(p) \/ SubmitBody(p) \/ SubmitRelease(p)
    \/ CloseAcquire \/ CloseBody \/ CloseRelease
    \/ WorkerReceive \/ WorkerDeliverOK \/ WorkerDeliverPanic \/ WorkerExit
    \/ WaitReturn
    \/ Terminal

Spec == Init /\ [][Next]_vars /\ WF_vars(Next)

(***************************************************************************)
(* Invariants and properties                                               *)
(***************************************************************************)

TypeOK ==
    /\ Len(queue) \in 0..Capacity
    /\ closing \in BOOLEAN
    /\ dropped \in Nat
    /\ rejected \in Nat
    /\ lockOwner \in Procs \cup {"none"}
    /\ workerDone \in BOOLEAN
    /\ waiterDone \in BOOLEAN
    /\ closeCount \in 0..1

QueueBound == Len(queue) <= Capacity                          \* D1, I1

Accounting == Len(admitted) + dropped + rejected = attempts   \* D4

NoSendAfterClose == sendsAfterClose = 0                       \* D7, I2, I4, I5

CloseOnce == closeCount <= 1                                  \* D6, I4

OrderOK == \A i \in 1..Len(offered) : offered[i] = admitted[i] \* D3, I6

InFlight == IF pc["worker"] = "wdeliver" THEN <<current>> ELSE <<>>

QueueMatches ==  \* admitted = offered ++ in-flight ++ queue  ("N queued + 1 active")
    admitted = offered \o InFlight \o queue

DrainOK == workerDone => (closing /\ offered = admitted /\ Len(queue) = 0) \* D8, I7

WaitOK == waiterDone => workerDone                            \* D9

PanicsBounded == panics <= Len(offered)                       \* D5 accounting

WorkerHasItem == pc["worker"] = "wdeliver" => current # <<>>

ClosingSticky == [](closing => []closing)                     \* I3 (temporal)

Termination == <>AllDone   \* liveness: with a fair worker, close+drain+wait
                           \* complete.  A callback that never returns maps
                           \* to an unfair worker: bounded queue does NOT
                           \* imply bounded close latency.

=============================================================================
