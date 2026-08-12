---- MODULE GeneratedInvalidTrace ----
RunID == "invalid-run"
DispatcherID == "observer-1"

VARIABLES queue, admitted, offered, current, closing, dropped,
          closeCount, exited, waited, pos

TraceData == <<
        [schema_version |-> 1, sequence |-> 1, action |-> "close_effective", has_action |-> TRUE, value |-> 0, has_value |-> FALSE, queue_len |-> 0, has_queue_len |-> TRUE, dropped |-> 0, has_dropped |-> TRUE, closing |-> FALSE, has_closing |-> FALSE, worker_done |-> FALSE, has_worker_done |-> FALSE, waited |-> FALSE, has_waited |-> FALSE, offered_item |-> 0, has_offered_item |-> FALSE],
        [schema_version |-> 1, sequence |-> 2, action |-> "submit_accepted", has_action |-> TRUE, value |-> 10, has_value |-> TRUE, queue_len |-> 1, has_queue_len |-> TRUE, dropped |-> 0, has_dropped |-> TRUE, closing |-> FALSE, has_closing |-> FALSE, worker_done |-> FALSE, has_worker_done |-> FALSE, waited |-> FALSE, has_waited |-> FALSE, offered_item |-> 0, has_offered_item |-> FALSE]
    >>

TraceInstance == INSTANCE DispatcherTraceValidator
    WITH Capacity <- 2, Items <- {10}, Trace <- TraceData,
         queue <- queue, admitted <- admitted, offered <- offered,
         current <- current, closing <- closing, dropped <- dropped,
         closeCount <- closeCount, exited <- exited, waited <- waited, pos <- pos

Spec == TraceInstance!Spec
QueueBound == TraceInstance!QueueBound
CloseOnce == TraceInstance!CloseOnce
Shape == TraceInstance!Shape
ExitSound == TraceInstance!ExitSound
WaitSound == TraceInstance!WaitSound
TraceConsumed == TraceInstance!TraceConsumed

====
