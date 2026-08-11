module dispatcher_guarded

-- Bounded Asynchronous Observer Dispatcher, relational/temporal view.
-- Temporal (Alloy 6) transition model of the same contract as the TLA+ spec.
-- Here delivery is atomic (receive+offer in one step), so no in-flight item
-- exists; the shape invariant is  admitted = offered ++ queue.

open util/sequniv

sig Item {}
sig Flag {}

one sig Dispatcher {
  var queue:    seq Item,   -- bounded FIFO
  var admitted: seq Item,   -- history: accepted items in order
  var offered:  seq Item,   -- history: callbacks invoked, in order
  var dropped:  seq Item,   -- one element per overflow drop
  var rejected: seq Item,   -- one element per post-close rejection
  var panics:   seq Item,   -- one element per recovered callback panic
  var closed:   lone Flag,  -- admission closed
  var exited:   lone Flag,  -- worker exited
  var waited:   lone Flag   -- Wait returned
}

fun cap: Int { 2 }

pred isPrefixOf[pre, s: Int -> univ] {
  #pre =< #s and (all i: inds[pre] | pre[i] = s[i])
}

pred init {
  no Dispatcher.queue
  no Dispatcher.admitted
  no Dispatcher.offered
  no Dispatcher.dropped
  no Dispatcher.rejected
  no Dispatcher.panics
  no Dispatcher.closed
  no Dispatcher.exited
  no Dispatcher.waited
}

pred stutter {
  Dispatcher.queue'    = Dispatcher.queue
  Dispatcher.admitted' = Dispatcher.admitted
  Dispatcher.offered'  = Dispatcher.offered
  Dispatcher.dropped'  = Dispatcher.dropped
  Dispatcher.rejected' = Dispatcher.rejected
  Dispatcher.panics'   = Dispatcher.panics
  Dispatcher.closed'   = Dispatcher.closed
  Dispatcher.exited'   = Dispatcher.exited
  Dispatcher.waited'   = Dispatcher.waited
}

-- D2/D1: admission is open and space is available -> accept (FIFO append)
pred submitAccepted[x: Item] {
  no Dispatcher.closed
  #Dispatcher.queue < cap
  x not in elems[Dispatcher.admitted]
  Dispatcher.queue'    = add[Dispatcher.queue, x]
  Dispatcher.admitted' = add[Dispatcher.admitted, x]
  Dispatcher.offered'  = Dispatcher.offered
  Dispatcher.dropped'  = Dispatcher.dropped
  Dispatcher.rejected' = Dispatcher.rejected
  Dispatcher.panics'   = Dispatcher.panics
  Dispatcher.closed'   = Dispatcher.closed
  Dispatcher.exited'   = Dispatcher.exited
  Dispatcher.waited'   = Dispatcher.waited
}

-- D4: full queue rejects and counts the drop
pred submitDropped[x: Item] {
  no Dispatcher.closed
  #Dispatcher.queue = cap
  x not in elems[Dispatcher.admitted]
  Dispatcher.queue'    = Dispatcher.queue
  Dispatcher.admitted' = Dispatcher.admitted
  Dispatcher.offered'  = Dispatcher.offered
  Dispatcher.dropped'  = add[Dispatcher.dropped, x]
  Dispatcher.rejected' = Dispatcher.rejected
  Dispatcher.panics'   = Dispatcher.panics
  Dispatcher.closed'   = Dispatcher.closed
  Dispatcher.exited'   = Dispatcher.exited
  Dispatcher.waited'   = Dispatcher.waited
}

-- D7: closed admission rejects without state change to the queue
pred submitRejected[x: Item] {
  some Dispatcher.closed
  Dispatcher.queue'    = Dispatcher.queue
  Dispatcher.admitted' = Dispatcher.admitted
  Dispatcher.offered'  = Dispatcher.offered
  Dispatcher.dropped'  = Dispatcher.dropped
  Dispatcher.rejected' = add[Dispatcher.rejected, x]
  Dispatcher.panics'   = Dispatcher.panics
  Dispatcher.closed'   = Dispatcher.closed
  Dispatcher.exited'   = Dispatcher.exited
  Dispatcher.waited'   = Dispatcher.waited
}

-- D6: close is effective at most once; repeated closes stutter
pred closeFirst {
  no Dispatcher.closed
  Dispatcher.closed'   = Flag
  Dispatcher.queue'    = Dispatcher.queue
  Dispatcher.admitted' = Dispatcher.admitted
  Dispatcher.offered'  = Dispatcher.offered
  Dispatcher.dropped'  = Dispatcher.dropped
  Dispatcher.rejected' = Dispatcher.rejected
  Dispatcher.panics'   = Dispatcher.panics
  Dispatcher.exited'   = Dispatcher.exited
  Dispatcher.waited'   = Dispatcher.waited
}

pred closeAgain {
  some Dispatcher.closed
  stutter
}

-- D3/D5: FIFO delivery; a recovered panic does not terminate delivery
pred deliverOk {
  some Dispatcher.queue
  Dispatcher.offered'  = add[Dispatcher.offered, first[Dispatcher.queue]]
  Dispatcher.queue'    = rest[Dispatcher.queue]
  Dispatcher.panics'   = Dispatcher.panics
  Dispatcher.admitted' = Dispatcher.admitted
  Dispatcher.dropped'  = Dispatcher.dropped
  Dispatcher.rejected' = Dispatcher.rejected
  Dispatcher.closed'   = Dispatcher.closed
  Dispatcher.exited'   = Dispatcher.exited
  Dispatcher.waited'   = Dispatcher.waited
}

pred deliverPanic {
  some Dispatcher.queue
  Dispatcher.offered'  = add[Dispatcher.offered, first[Dispatcher.queue]]
  Dispatcher.queue'    = rest[Dispatcher.queue]
  Dispatcher.panics'   = add[Dispatcher.panics, first[Dispatcher.queue]]
  Dispatcher.admitted' = Dispatcher.admitted
  Dispatcher.dropped'  = Dispatcher.dropped
  Dispatcher.rejected' = Dispatcher.rejected
  Dispatcher.closed'   = Dispatcher.closed
  Dispatcher.exited'   = Dispatcher.exited
  Dispatcher.waited'   = Dispatcher.waited
}

-- D8: worker exits only when the queue is closed and drained
pred workerExit {
  some Dispatcher.closed
  no Dispatcher.queue
  no Dispatcher.exited
  Dispatcher.exited'   = Flag
  Dispatcher.queue'    = Dispatcher.queue
  Dispatcher.admitted' = Dispatcher.admitted
  Dispatcher.offered'  = Dispatcher.offered
  Dispatcher.dropped'  = Dispatcher.dropped
  Dispatcher.rejected' = Dispatcher.rejected
  Dispatcher.panics'   = Dispatcher.panics
  Dispatcher.closed'   = Dispatcher.closed
  Dispatcher.waited'   = Dispatcher.waited
}

-- D9: Wait returns only after the worker exited
pred waitReturn {
  some Dispatcher.exited
  no Dispatcher.waited
  Dispatcher.waited'   = Flag
  Dispatcher.queue'    = Dispatcher.queue
  Dispatcher.admitted' = Dispatcher.admitted
  Dispatcher.offered'  = Dispatcher.offered
  Dispatcher.dropped'  = Dispatcher.dropped
  Dispatcher.rejected' = Dispatcher.rejected
  Dispatcher.panics'   = Dispatcher.panics
  Dispatcher.closed'   = Dispatcher.closed
  Dispatcher.exited'   = Dispatcher.exited
}

fact traces {
  init
  always (
    stutter
    or (some x: Item | submitAccepted[x] or submitDropped[x] or submitRejected[x])
    or closeFirst
    or closeAgain
    or deliverOk
    or deliverPanic
    or workerExit
    or waitReturn
  )
}

assert QueueBound {
  always (#Dispatcher.queue =< cap)
}

assert NoEnqueueAfterClose {
  always (some Dispatcher.closed implies #Dispatcher.queue' =< #Dispatcher.queue)
}

assert OfferedIsPrefix {
  always isPrefixOf[Dispatcher.offered, Dispatcher.admitted]
}

assert QueueIsSuffix {
  -- admitted = offered ++ queue (delivery is atomic in this model)
  always (Dispatcher.admitted = append[Dispatcher.offered, Dispatcher.queue])
}

assert DrainComplete {
  always (some Dispatcher.exited implies
    (some Dispatcher.closed
     and no Dispatcher.queue
     and Dispatcher.offered = Dispatcher.admitted))
}

assert WaitAfterExit {
  always (some Dispatcher.waited implies some Dispatcher.exited)
}

assert ClosedSticky {
  -- one-step stickiness at every step <=> the flag never flips back
  always (some Dispatcher.closed implies some Dispatcher.closed')
}

assert DropsMonotone {
  always (#Dispatcher.dropped =< #Dispatcher.dropped')
}

run ExampleLifecycle {
  eventually (
    #Dispatcher.admitted > 2
    and #Dispatcher.dropped > 0
    and #Dispatcher.panics > 0
    and #Dispatcher.rejected > 0
    and some Dispatcher.exited
    and some Dispatcher.waited
  )
} for 4 Item, 1 Flag, 6 seq, 14 steps

check QueueBound         for 4 Item, 1 Flag, 6 seq, 10 steps
check NoEnqueueAfterClose for 4 Item, 1 Flag, 6 seq, 10 steps
check OfferedIsPrefix    for 4 Item, 1 Flag, 6 seq, 10 steps
check QueueIsSuffix      for 4 Item, 1 Flag, 6 seq, 10 steps
check DrainComplete      for 4 Item, 1 Flag, 6 seq, 10 steps
check WaitAfterExit      for 4 Item, 1 Flag, 6 seq, 10 steps
check ClosedSticky       for 4 Item, 1 Flag, 6 seq, 10 steps
check DropsMonotone      for 4 Item, 1 Flag, 6 seq, 10 steps
