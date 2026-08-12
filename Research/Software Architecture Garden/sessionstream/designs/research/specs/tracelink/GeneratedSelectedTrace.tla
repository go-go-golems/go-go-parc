---- MODULE GeneratedSelectedTrace ----
RunID == "tracegen-run-2"
DispatcherID == "observer-2"

VARIABLES queue, admitted, offered, current, closing, dropped,
          closeCount, exited, waited, pos

TraceData == <<
        [schema_version |-> 1, sequence |-> 1, action |-> "submit_accepted", has_action |-> TRUE, value |-> 10, has_value |-> TRUE, queue_len |-> 1, has_queue_len |-> TRUE, dropped |-> 0, has_dropped |-> TRUE, closing |-> FALSE, has_closing |-> FALSE, worker_done |-> FALSE, has_worker_done |-> FALSE, waited |-> FALSE, has_waited |-> FALSE, offered_item |-> 0, has_offered_item |-> FALSE],
        [schema_version |-> 1, sequence |-> 2, action |-> "receive", has_action |-> TRUE, value |-> 10, has_value |-> TRUE, queue_len |-> 0, has_queue_len |-> TRUE, dropped |-> 0, has_dropped |-> TRUE, closing |-> FALSE, has_closing |-> FALSE, worker_done |-> FALSE, has_worker_done |-> FALSE, waited |-> FALSE, has_waited |-> FALSE, offered_item |-> 0, has_offered_item |-> FALSE],
        [schema_version |-> 1, sequence |-> 3, action |-> "submit_accepted", has_action |-> TRUE, value |-> 20, has_value |-> TRUE, queue_len |-> 1, has_queue_len |-> TRUE, dropped |-> 0, has_dropped |-> TRUE, closing |-> FALSE, has_closing |-> FALSE, worker_done |-> FALSE, has_worker_done |-> FALSE, waited |-> FALSE, has_waited |-> FALSE, offered_item |-> 0, has_offered_item |-> FALSE],
        [schema_version |-> 1, sequence |-> 4, action |-> "submit_accepted", has_action |-> TRUE, value |-> 30, has_value |-> TRUE, queue_len |-> 2, has_queue_len |-> TRUE, dropped |-> 0, has_dropped |-> TRUE, closing |-> FALSE, has_closing |-> FALSE, worker_done |-> FALSE, has_worker_done |-> FALSE, waited |-> FALSE, has_waited |-> FALSE, offered_item |-> 0, has_offered_item |-> FALSE],
        [schema_version |-> 1, sequence |-> 5, action |-> "submit_dropped", has_action |-> TRUE, value |-> 40, has_value |-> TRUE, queue_len |-> 2, has_queue_len |-> TRUE, dropped |-> 1, has_dropped |-> TRUE, closing |-> FALSE, has_closing |-> FALSE, worker_done |-> FALSE, has_worker_done |-> FALSE, waited |-> FALSE, has_waited |-> FALSE, offered_item |-> 0, has_offered_item |-> FALSE],
        [schema_version |-> 1, sequence |-> 6, action |-> "close_effective", has_action |-> TRUE, value |-> 0, has_value |-> FALSE, queue_len |-> 2, has_queue_len |-> TRUE, dropped |-> 1, has_dropped |-> TRUE, closing |-> FALSE, has_closing |-> FALSE, worker_done |-> FALSE, has_worker_done |-> FALSE, waited |-> FALSE, has_waited |-> FALSE, offered_item |-> 0, has_offered_item |-> FALSE],
        [schema_version |-> 1, sequence |-> 7, action |-> "close_noop", has_action |-> TRUE, value |-> 0, has_value |-> FALSE, queue_len |-> 2, has_queue_len |-> TRUE, dropped |-> 1, has_dropped |-> TRUE, closing |-> FALSE, has_closing |-> FALSE, worker_done |-> FALSE, has_worker_done |-> FALSE, waited |-> FALSE, has_waited |-> FALSE, offered_item |-> 0, has_offered_item |-> FALSE],
        [schema_version |-> 1, sequence |-> 8, action |-> "submit_rejected", has_action |-> TRUE, value |-> 50, has_value |-> TRUE, queue_len |-> 2, has_queue_len |-> TRUE, dropped |-> 1, has_dropped |-> TRUE, closing |-> FALSE, has_closing |-> FALSE, worker_done |-> FALSE, has_worker_done |-> FALSE, waited |-> FALSE, has_waited |-> FALSE, offered_item |-> 0, has_offered_item |-> FALSE],
        [schema_version |-> 1, sequence |-> 9, action |-> "offered", has_action |-> TRUE, value |-> 10, has_value |-> TRUE, queue_len |-> 2, has_queue_len |-> TRUE, dropped |-> 1, has_dropped |-> TRUE, closing |-> FALSE, has_closing |-> FALSE, worker_done |-> FALSE, has_worker_done |-> FALSE, waited |-> FALSE, has_waited |-> FALSE, offered_item |-> 0, has_offered_item |-> FALSE],
        [schema_version |-> 1, sequence |-> 10, action |-> "receive", has_action |-> TRUE, value |-> 20, has_value |-> TRUE, queue_len |-> 1, has_queue_len |-> TRUE, dropped |-> 1, has_dropped |-> TRUE, closing |-> FALSE, has_closing |-> FALSE, worker_done |-> FALSE, has_worker_done |-> FALSE, waited |-> FALSE, has_waited |-> FALSE, offered_item |-> 0, has_offered_item |-> FALSE],
        [schema_version |-> 1, sequence |-> 11, action |-> "panic_recovered", has_action |-> TRUE, value |-> 20, has_value |-> TRUE, queue_len |-> 1, has_queue_len |-> TRUE, dropped |-> 1, has_dropped |-> TRUE, closing |-> FALSE, has_closing |-> FALSE, worker_done |-> FALSE, has_worker_done |-> FALSE, waited |-> FALSE, has_waited |-> FALSE, offered_item |-> 0, has_offered_item |-> FALSE],
        [schema_version |-> 1, sequence |-> 12, action |-> "receive", has_action |-> TRUE, value |-> 30, has_value |-> TRUE, queue_len |-> 0, has_queue_len |-> TRUE, dropped |-> 1, has_dropped |-> TRUE, closing |-> FALSE, has_closing |-> FALSE, worker_done |-> FALSE, has_worker_done |-> FALSE, waited |-> FALSE, has_waited |-> FALSE, offered_item |-> 0, has_offered_item |-> FALSE],
        [schema_version |-> 1, sequence |-> 13, action |-> "offered", has_action |-> TRUE, value |-> 30, has_value |-> TRUE, queue_len |-> 0, has_queue_len |-> TRUE, dropped |-> 1, has_dropped |-> TRUE, closing |-> FALSE, has_closing |-> FALSE, worker_done |-> FALSE, has_worker_done |-> FALSE, waited |-> FALSE, has_waited |-> FALSE, offered_item |-> 0, has_offered_item |-> FALSE],
        [schema_version |-> 1, sequence |-> 14, action |-> "worker_exit", has_action |-> TRUE, value |-> 0, has_value |-> FALSE, queue_len |-> 0, has_queue_len |-> TRUE, dropped |-> 1, has_dropped |-> TRUE, closing |-> FALSE, has_closing |-> FALSE, worker_done |-> FALSE, has_worker_done |-> FALSE, waited |-> FALSE, has_waited |-> FALSE, offered_item |-> 0, has_offered_item |-> FALSE],
        [schema_version |-> 1, sequence |-> 15, action |-> "wait_returned", has_action |-> TRUE, value |-> 0, has_value |-> FALSE, queue_len |-> 0, has_queue_len |-> TRUE, dropped |-> 1, has_dropped |-> TRUE, closing |-> FALSE, has_closing |-> FALSE, worker_done |-> FALSE, has_worker_done |-> FALSE, waited |-> FALSE, has_waited |-> FALSE, offered_item |-> 0, has_offered_item |-> FALSE]
    >>

TraceInstance == INSTANCE DispatcherTraceValidator
    WITH Capacity <- 2, Items <- {10, 20, 30, 40, 50}, Trace <- TraceData,
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
