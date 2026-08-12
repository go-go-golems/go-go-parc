---- MODULE DispatcherTraceValidator ----
EXTENDS Integers, Sequences, FiniteSets, TLC

CONSTANTS Capacity, Items, Trace
ASSUME Capacity \in Nat \ {0}
ASSUME Items # {}
ASSUME IsFiniteSet(Items)

VARIABLES queue, admitted, offered, current, closing, dropped,
          closeCount, exited, waited, pos

vars == <<queue, admitted, offered, current, closing, dropped,
          closeCount, exited, waited, pos>>

Init ==
    /\ queue = <<>>
    /\ admitted = <<>>
    /\ offered = <<>>
    /\ current = <<>>
    /\ closing = FALSE
    /\ dropped = 0
    /\ closeCount = 0
    /\ exited = FALSE
    /\ waited = FALSE
    /\ pos = 1

SubmitAccepted(v) ==
    /\ ~closing
    /\ Len(queue) < Capacity
    /\ queue' = Append(queue, v)
    /\ admitted' = Append(admitted, v)
    /\ UNCHANGED <<offered, current, closing, dropped, closeCount, exited, waited>>

SubmitDropped ==
    /\ ~closing
    /\ Len(queue) = Capacity
    /\ dropped' = dropped + 1
    /\ UNCHANGED <<queue, admitted, offered, current, closing, closeCount, exited, waited>>

SubmitRejected ==
    /\ closing
    /\ UNCHANGED <<queue, admitted, offered, current, closing, dropped, closeCount, exited, waited>>

CloseEffective ==
    /\ ~closing
    /\ closing' = TRUE
    /\ closeCount' = closeCount + 1
    /\ UNCHANGED <<queue, admitted, offered, current, dropped, exited, waited>>

CloseNoop ==
    /\ closing
    /\ UNCHANGED <<queue, admitted, offered, current, closing, dropped, closeCount, exited, waited>>

Receive(v) ==
    /\ Len(queue) > 0
    /\ current = <<>>
    /\ v = Head(queue)
    /\ queue' = Tail(queue)
    /\ current' = <<v>>
    /\ UNCHANGED <<admitted, offered, closing, dropped, closeCount, exited, waited>>

Offered(v) ==
    /\ current = <<v>>
    /\ offered' = Append(offered, v)
    /\ current' = <<>>
    /\ UNCHANGED <<queue, admitted, closing, dropped, closeCount, exited, waited>>

WorkerExit ==
    /\ closing
    /\ queue = <<>>
    /\ current = <<>>
    /\ exited' = TRUE
    /\ UNCHANGED <<queue, admitted, offered, current, closing, dropped, closeCount, waited>>

WaitReturned ==
    /\ exited
    /\ waited' = TRUE
    /\ UNCHANGED <<queue, admitted, offered, current, closing, dropped, closeCount, exited>>

WorkerActions == {"receive", "offered", "panic_recovered"}
ActionMatches(e, action) ==
    \/ ~e.has_action
    \/ e.action = action
    \/ e.action = "worker" /\ action \in WorkerActions
ValueMatches(e, value) == ~e.has_value \/ e.value = value
EvidenceMatches(e) ==
    /\ (~e.has_queue_len \/ e.queue_len = Len(queue'))
    /\ (~e.has_dropped \/ e.dropped = dropped')
    /\ (~e.has_closing \/ e.closing = closing')
    /\ (~e.has_worker_done \/ e.worker_done = exited')
    /\ (~e.has_waited \/ e.waited = waited')
    /\ (~e.has_offered_item \/ (Len(offered') > 0 /\ e.offered_item = offered'[Len(offered')]))

Apply(e) ==
    /\ (\/ /\ ActionMatches(e, "submit_accepted")
            /\ \E v \in Items : ValueMatches(e, v) /\ SubmitAccepted(v)
        \/ /\ ActionMatches(e, "submit_dropped")
            /\ SubmitDropped
        \/ /\ ActionMatches(e, "submit_rejected")
            /\ SubmitRejected
        \/ /\ ActionMatches(e, "close_effective")
            /\ CloseEffective
        \/ /\ ActionMatches(e, "close_noop")
            /\ CloseNoop
        \/ /\ ActionMatches(e, "receive")
            /\ \E v \in Items : ValueMatches(e, v) /\ Receive(v)
        \/ /\ ActionMatches(e, "offered")
            /\ \E v \in Items : ValueMatches(e, v) /\ Offered(v)
        \/ /\ ActionMatches(e, "panic_recovered")
            /\ \E v \in Items : ValueMatches(e, v) /\ Offered(v)
        \/ /\ ActionMatches(e, "worker_exit")
            /\ WorkerExit
        \/ /\ ActionMatches(e, "wait_returned")
            /\ WaitReturned)
    /\ EvidenceMatches(e)

Consume ==
    /\ pos <= Len(Trace)
    /\ Apply(Trace[pos])
    /\ pos' = pos + 1

Terminal ==
    /\ pos = Len(Trace) + 1
    /\ UNCHANGED vars

Next == Consume \/ Terminal
Spec == Init /\ [][Next]_vars /\ WF_vars(Consume)

QueueBound == Len(queue) <= Capacity
CloseOnce == closeCount <= 1
Shape == admitted = offered \o current \o queue
ExitSound == exited => closing /\ queue = <<>> /\ current = <<>>
WaitSound == waited => exited
TraceConsumed == <> (pos = Len(Trace) + 1)

====
