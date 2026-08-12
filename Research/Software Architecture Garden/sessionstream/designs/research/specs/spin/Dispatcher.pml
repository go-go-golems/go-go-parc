/*
 * Bounded asynchronous observer dispatcher: Promela protocol model.
 *
 * Run guarded:   spin -DGUARDED=1 -a Dispatcher.pml && gcc -O2 -o pan pan.c && ./pan -a
 * Run mutation:  spin -DGUARDED=0 -a Dispatcher.pml && gcc -O2 -o pan pan.c && ./pan -a
 *
 * This deliberately abstracts values and callbacks. It checks the channel /
 * lifecycle shell: submit and close serialize on one mutex token, guarded
 * admission never sends after close, and worker exit requires close + drain.
 */

#ifndef GUARDED
#define GUARDED 1
#endif

#define CAPACITY 2
#define PRODUCERS 2
#define SUBMITS 2

chan mutex = [1] of { bit };
chan queue = [CAPACITY] of { byte };
chan producerDone = [PRODUCERS] of { bit };
chan closerDone = [1] of { bit };
chan workerDone = [1] of { bit };

bool closing = false;
byte closeCount = 0;
byte admitted = 0;
byte offered = 0;
byte dropped = 0;
byte rejected = 0;
byte sendsAfterClose = 0;

proctype Producer(byte id)
{
    byte k = 0;
    bit token;

    do
    :: k < SUBMITS ->
        mutex?token;
#if GUARDED
        if
        :: closing ->
            rejected++
        :: !closing && len(queue) < CAPACITY ->
            queue!(id * SUBMITS + k);
            admitted++
        :: !closing && len(queue) == CAPACITY ->
            dropped++
        fi;
#else
        if
        :: len(queue) < CAPACITY ->
            if
            :: closing -> sendsAfterClose++
            :: !closing -> skip
            fi;
            queue!(id * SUBMITS + k);
            admitted++
        :: len(queue) == CAPACITY ->
            dropped++
        fi;
#endif
        assert(sendsAfterClose == 0);
        mutex!token;
        k++
    :: k == SUBMITS -> break
    od;
    producerDone!1
}

proctype Closer()
{
    bit token;
    mutex?token;
    if
    :: !closing ->
        closing = true;
        closeCount++
    :: closing -> skip
    fi;
    assert(closeCount <= 1);
    mutex!token;
    closerDone!1
}

proctype Worker()
{
    byte item;
    do
    :: queue?item ->
        offered++
    :: closing && len(queue) == 0 ->
        break
    od;
    assert(closing);
    assert(len(queue) == 0);
    assert(offered == admitted);
    workerDone!1
}

init
{
    bit done;
    mutex!1;
    atomic {
        run Producer(0);
        run Producer(1);
        run Closer();
        run Worker()
    }
    producerDone?done;
    producerDone?done;
    closerDone?done;
    workerDone?done;
    assert(closeCount == 1);
    assert(sendsAfterClose == 0);
    assert(offered == admitted)
}
