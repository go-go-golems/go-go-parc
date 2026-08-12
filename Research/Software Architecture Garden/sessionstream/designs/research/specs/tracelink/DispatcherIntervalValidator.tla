---- MODULE DispatcherIntervalValidator ----
EXTENDS Integers, Sequences, FiniteSets, TLC

CONSTANTS Capacity, Items, Steps, Predecessors
ASSUME Capacity \in Nat \ {0}
ASSUME Items # {}
ASSUME IsFiniteSet(Items)

VARIABLES queue, admitted, offered, current, closing, dropped,
          closeCount, exited, waited, kernelPos, consumed

kernelVars == <<queue, admitted, offered, current, closing, dropped,
                closeCount, exited, waited, kernelPos>>
vars == Append(kernelVars, consumed)

Kernel == INSTANCE DispatcherTraceValidator
    WITH Capacity <- Capacity, Items <- Items, Trace <- <<>>,
         queue <- queue, admitted <- admitted, offered <- offered,
         current <- current, closing <- closing, dropped <- dropped,
         closeCount <- closeCount, exited <- exited, waited <- waited,
         pos <- kernelPos

StepSet == 1..Len(Steps)

Init ==
    /\ Kernel!Init
    /\ consumed = {}

Enabled(i) ==
    /\ i \in StepSet \ consumed
    /\ Predecessors[i] \subseteq consumed

Consume(i) ==
    /\ Enabled(i)
    /\ Kernel!Apply(Steps[i])
    /\ kernelPos' = kernelPos
    /\ consumed' = consumed \cup {i}

Terminal ==
    /\ consumed = StepSet
    /\ UNCHANGED vars

Next == (\E i \in StepSet : Consume(i)) \/ Terminal
Spec == Init /\ [][Next]_vars

QueueBound == Kernel!QueueBound
CloseOnce == Kernel!CloseOnce
Shape == Kernel!Shape
ExitSound == Kernel!ExitSound
WaitSound == Kernel!WaitSound

(* Search sentinel: a violation is the desired witness that every step was  *)
(* legally linearized while respecting all operation-interval predecessors. *)
NoCompleteLinearization == consumed # StepSet

====
