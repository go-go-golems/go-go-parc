---- MODULE GeneratedIntervalTrace ----
RunID == "tracegen-run"
DispatcherID == "observer-1"

VARIABLES queue, admitted, offered, current, closing, dropped,
          closeCount, exited, waited, kernelPos, consumed

StepData == <<
        [schema_version |-> 1, sequence |-> 1, action |-> "submit_accepted", has_action |-> TRUE, value |-> 10, has_value |-> TRUE, queue_len |-> 0, has_queue_len |-> FALSE, dropped |-> 0, has_dropped |-> FALSE, closing |-> FALSE, has_closing |-> FALSE, worker_done |-> FALSE, has_worker_done |-> FALSE, waited |-> FALSE, has_waited |-> FALSE, offered_item |-> 0, has_offered_item |-> FALSE],
        [schema_version |-> 1, sequence |-> 2, action |-> "receive", has_action |-> TRUE, value |-> 10, has_value |-> TRUE, queue_len |-> 0, has_queue_len |-> FALSE, dropped |-> 0, has_dropped |-> FALSE, closing |-> FALSE, has_closing |-> FALSE, worker_done |-> FALSE, has_worker_done |-> FALSE, waited |-> FALSE, has_waited |-> FALSE, offered_item |-> 0, has_offered_item |-> FALSE],
        [schema_version |-> 1, sequence |-> 3, action |-> "submit_accepted", has_action |-> TRUE, value |-> 20, has_value |-> TRUE, queue_len |-> 0, has_queue_len |-> FALSE, dropped |-> 0, has_dropped |-> FALSE, closing |-> FALSE, has_closing |-> FALSE, worker_done |-> FALSE, has_worker_done |-> FALSE, waited |-> FALSE, has_waited |-> FALSE, offered_item |-> 0, has_offered_item |-> FALSE],
        [schema_version |-> 1, sequence |-> 4, action |-> "submit_accepted", has_action |-> TRUE, value |-> 30, has_value |-> TRUE, queue_len |-> 0, has_queue_len |-> FALSE, dropped |-> 0, has_dropped |-> FALSE, closing |-> FALSE, has_closing |-> FALSE, worker_done |-> FALSE, has_worker_done |-> FALSE, waited |-> FALSE, has_waited |-> FALSE, offered_item |-> 0, has_offered_item |-> FALSE],
        [schema_version |-> 1, sequence |-> 5, action |-> "submit_dropped", has_action |-> TRUE, value |-> 40, has_value |-> TRUE, queue_len |-> 0, has_queue_len |-> FALSE, dropped |-> 0, has_dropped |-> FALSE, closing |-> FALSE, has_closing |-> FALSE, worker_done |-> FALSE, has_worker_done |-> FALSE, waited |-> FALSE, has_waited |-> FALSE, offered_item |-> 0, has_offered_item |-> FALSE],
        [schema_version |-> 1, sequence |-> 6, action |-> "close_effective", has_action |-> TRUE, value |-> 0, has_value |-> FALSE, queue_len |-> 0, has_queue_len |-> FALSE, dropped |-> 0, has_dropped |-> FALSE, closing |-> FALSE, has_closing |-> FALSE, worker_done |-> FALSE, has_worker_done |-> FALSE, waited |-> FALSE, has_waited |-> FALSE, offered_item |-> 0, has_offered_item |-> FALSE],
        [schema_version |-> 1, sequence |-> 7, action |-> "close_noop", has_action |-> TRUE, value |-> 0, has_value |-> FALSE, queue_len |-> 0, has_queue_len |-> FALSE, dropped |-> 0, has_dropped |-> FALSE, closing |-> FALSE, has_closing |-> FALSE, worker_done |-> FALSE, has_worker_done |-> FALSE, waited |-> FALSE, has_waited |-> FALSE, offered_item |-> 0, has_offered_item |-> FALSE],
        [schema_version |-> 1, sequence |-> 8, action |-> "submit_rejected", has_action |-> TRUE, value |-> 50, has_value |-> TRUE, queue_len |-> 0, has_queue_len |-> FALSE, dropped |-> 0, has_dropped |-> FALSE, closing |-> FALSE, has_closing |-> FALSE, worker_done |-> FALSE, has_worker_done |-> FALSE, waited |-> FALSE, has_waited |-> FALSE, offered_item |-> 0, has_offered_item |-> FALSE],
        [schema_version |-> 1, sequence |-> 9, action |-> "offered", has_action |-> TRUE, value |-> 10, has_value |-> TRUE, queue_len |-> 0, has_queue_len |-> FALSE, dropped |-> 0, has_dropped |-> FALSE, closing |-> FALSE, has_closing |-> FALSE, worker_done |-> FALSE, has_worker_done |-> FALSE, waited |-> FALSE, has_waited |-> FALSE, offered_item |-> 0, has_offered_item |-> FALSE],
        [schema_version |-> 1, sequence |-> 10, action |-> "receive", has_action |-> TRUE, value |-> 20, has_value |-> TRUE, queue_len |-> 0, has_queue_len |-> FALSE, dropped |-> 0, has_dropped |-> FALSE, closing |-> FALSE, has_closing |-> FALSE, worker_done |-> FALSE, has_worker_done |-> FALSE, waited |-> FALSE, has_waited |-> FALSE, offered_item |-> 0, has_offered_item |-> FALSE],
        [schema_version |-> 1, sequence |-> 11, action |-> "panic_recovered", has_action |-> TRUE, value |-> 20, has_value |-> TRUE, queue_len |-> 0, has_queue_len |-> FALSE, dropped |-> 0, has_dropped |-> FALSE, closing |-> FALSE, has_closing |-> FALSE, worker_done |-> FALSE, has_worker_done |-> FALSE, waited |-> FALSE, has_waited |-> FALSE, offered_item |-> 0, has_offered_item |-> FALSE],
        [schema_version |-> 1, sequence |-> 12, action |-> "receive", has_action |-> TRUE, value |-> 30, has_value |-> TRUE, queue_len |-> 0, has_queue_len |-> FALSE, dropped |-> 0, has_dropped |-> FALSE, closing |-> FALSE, has_closing |-> FALSE, worker_done |-> FALSE, has_worker_done |-> FALSE, waited |-> FALSE, has_waited |-> FALSE, offered_item |-> 0, has_offered_item |-> FALSE],
        [schema_version |-> 1, sequence |-> 13, action |-> "offered", has_action |-> TRUE, value |-> 30, has_value |-> TRUE, queue_len |-> 0, has_queue_len |-> FALSE, dropped |-> 0, has_dropped |-> FALSE, closing |-> FALSE, has_closing |-> FALSE, worker_done |-> FALSE, has_worker_done |-> FALSE, waited |-> FALSE, has_waited |-> FALSE, offered_item |-> 0, has_offered_item |-> FALSE],
        [schema_version |-> 1, sequence |-> 14, action |-> "worker_exit", has_action |-> TRUE, value |-> 0, has_value |-> FALSE, queue_len |-> 0, has_queue_len |-> FALSE, dropped |-> 0, has_dropped |-> FALSE, closing |-> FALSE, has_closing |-> FALSE, worker_done |-> FALSE, has_worker_done |-> FALSE, waited |-> FALSE, has_waited |-> FALSE, offered_item |-> 0, has_offered_item |-> FALSE],
        [schema_version |-> 1, sequence |-> 15, action |-> "wait_returned", has_action |-> TRUE, value |-> 0, has_value |-> FALSE, queue_len |-> 0, has_queue_len |-> FALSE, dropped |-> 0, has_dropped |-> FALSE, closing |-> FALSE, has_closing |-> FALSE, worker_done |-> FALSE, has_worker_done |-> FALSE, waited |-> FALSE, has_waited |-> FALSE, offered_item |-> 0, has_offered_item |-> FALSE]
    >>
PredecessorData == <<{}, {1}, {1}, {1, 3}, {1, 3, 4}, {1, 3, 4, 5}, {1, 3, 4, 5, 6}, {1, 3, 4, 5, 6, 7}, {1, 2}, {1, 2, 3, 4, 5, 6, 7, 8, 9}, {1, 2, 3, 4, 5, 6, 7, 8, 9, 10}, {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11}, {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12}, {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13}, {1, 3, 4, 5, 6, 7, 8}>>

IntervalInstance == INSTANCE DispatcherIntervalValidator
    WITH Capacity <- 2, Items <- {10, 20, 30, 40, 50}, Steps <- StepData,
         Predecessors <- PredecessorData,
         queue <- queue, admitted <- admitted, offered <- offered,
         current <- current, closing <- closing, dropped <- dropped,
         closeCount <- closeCount, exited <- exited, waited <- waited,
         kernelPos <- kernelPos, consumed <- consumed

Spec == IntervalInstance!Spec
QueueBound == IntervalInstance!QueueBound
CloseOnce == IntervalInstance!CloseOnce
Shape == IntervalInstance!Shape
ExitSound == IntervalInstance!ExitSound
WaitSound == IntervalInstance!WaitSound
NoCompleteLinearization == IntervalInstance!NoCompleteLinearization

====
