Properties of an execution of a computer program—particularly for 
[concurrent](https://en.wikipedia.org/wiki/Concurrent_system "Concurrent system") and [distributed 
systems](https://en.wikipedia.org/wiki/Distributed_system "Distributed system") —have long been 
formulated by giving **safety properties** ("bad things don't happen") and **liveness properties** 
("good things do happen").[^1]

A program is [totally correct](https://en.wikipedia.org/wiki/Total_correctness "Total correctness") 
with respect to a [precondition](https://en.wikipedia.org/wiki/Precondition "Precondition") 
${\displaystyle P}$ and [postcondition](https://en.wikipedia.org/wiki/Postcondition 
"Postcondition") ${\displaystyle Q}$ if any execution started in a state satisfying ${\displaystyle 
P}$ terminates in a state satisfying ${\displaystyle Q}$. Total correctness is a conjunction of a 
safety property and a liveness property:[^2]

- The safety property prohibits these "bad things": executions that start in a state satisfying 
${\displaystyle P}$ and terminate in a final state that does not satisfy ${\displaystyle Q}$. For a 
program ${\displaystyle C}$, this safety property is usually written using the [Hoare 
triple](https://en.wikipedia.org/wiki/Hoare_logic "Hoare logic") ${\displaystyle \{P\}C\{Q\}}$.
- The liveness property, the "good thing", is that execution that starts in a state satisfying 
${\displaystyle P}$ terminates.

Note that a *bad thing* is discrete,[^3] since it happens at a particular place during execution. A 
"good thing" need not be discrete, but the liveness property of termination is discrete.

Formal definitions that were ultimately proposed for safety properties [^4] and liveness properties 
[^5] demonstrated that this decomposition is not only intuitively appealing but is also complete: 
all properties of an execution are a conjunction of safety and liveness properties.[^5] Moreover, 
undertaking the decomposition can be helpful, because the formal definitions enable a proof that 
different methods must be used for verifying safety properties versus for verifying liveness 
properties.[^6] [^7]

## Safety

A safety property proscribes discrete *bad things* from occurring during an execution.[^1] A safety 
property thus characterizes what is permitted by stating what is prohibited. The requirement that 
the *bad thing* be discrete means that a *bad thing* occurring during execution necessarily occurs 
at some identifiable point.[^5]

Examples of a discrete *bad thing* that could be used to define a safety property include:[^5]

- An execution that starts in a state satisfying a given precondition terminates, but the final 
state does not satisfy the required postcondition;
- An execution of two concurrent processes, where the program counters for both processes designate 
statements within a [critical section](https://en.wikipedia.org/wiki/Critical_section "Critical 
section");
- An execution of two concurrent processes where each process is waiting for another to change 
state (known as [deadlock](https://en.wikipedia.org/wiki/Deadlock_\(computer_science\) "Deadlock 
(computer science)")).

An execution of a program can be described formally by giving the infinite sequence of program 
states that results as execution proceeds, where the last state for a terminating program is 
repeated infinitely. For a program of interest, let ${\displaystyle S}$ denote the set of possible 
program states, ${\displaystyle S^{*}}$ denote the set of finite sequences of program states, and 
${\displaystyle S^{\omega }}$ denote the set of infinite sequences of program states. The relation 
${\displaystyle \sigma \leq \tau }$ holds for sequences ${\displaystyle \sigma }$ and 
${\displaystyle \tau }$ iff ${\displaystyle \sigma }$ is a 
[prefix](https://en.wikipedia.org/wiki/Substring#Prefix "Substring") of ${\displaystyle \tau }$ or 
${\displaystyle \sigma }$ equals ${\displaystyle \tau }$.[^5]

A property of a program is the set of allowed executions.

The essential characteristic of a safety property ${\displaystyle SP}$ is: If some execution 
${\displaystyle \sigma }$ does not satisfy ${\displaystyle SP}$ then the defining *bad thing* for 
that safety property occurs at some point in ${\displaystyle \sigma }$. Notice that after such a 
*bad thing*, if further execution results in an execution ${\displaystyle \sigma ^{\prime }}$, then 
${\displaystyle \sigma ^{\prime }}$ also does not satisfy ${\displaystyle SP}$, since the *bad 
thing* in ${\displaystyle \sigma }$ also occurs in ${\displaystyle \sigma ^{\prime }}$. We take 
this inference about the irremediability of *bad things* to be the defining characteristic for 
${\displaystyle SP}$ to be a safety property. Formalizing this in predicate logic gives a formal 
definition for ${\displaystyle SP}$ being a safety property.[^5]

${\displaystyle \forall \sigma \in S^{\omega }:\sigma \notin SP\implies (\exists \beta \leq \sigma$

This formal definition for safety properties implies that if an execution ${\displaystyle \sigma }$ 
satisfies a safety property ${\displaystyle SP}$ then every prefix of ${\displaystyle \sigma }$ 
(with the last state repeated) also satisfies ${\displaystyle SP}$.

## Liveness

A liveness property prescribes *good things* for every execution or, equivalently, describes 
something that must happen during an execution.[^1] The *good thing* need not be discrete—it 
might involve an infinite number of steps. Examples of a *good thing* used to define a liveness 
property include:[^5]

- Termination of an execution that is started in a suitable state;
- Non-termination of an execution that is started in a suitable state;
- Guaranteed eventual entry to a critical section whenever entry is attempted;
- Fair access to a resource in the presence of contention.

The *good thing* in the first example is discrete but not in the others.

Producing an answer within a specified real-time bound is a safety property rather than a liveness 
property. This is because a discrete *bad thing* is being proscribed: a partial execution that 
reaches a state where the answer still has not been produced and the value of the clock (a state 
variable) violates the bound. Deadlock freedom is a safety property: the "bad thing" is a 
[deadlock](https://en.wikipedia.org/wiki/Deadlock_\(computer_science\) "Deadlock (computer 
science)") (which is discrete).

Most of the time, knowing that a program eventually does some "good thing" is not satisfactory; we 
want to know that the program performs the "good thing" within some number of steps or before some 
deadline. A property that gives a specific bound to the "good thing" is a safety property (as noted 
above), whereas the weaker property that merely asserts the bound exists is a liveness property. 
Proving such a liveness property is likely to be easier than proving the tighter safety property 
because proving the liveness property doesn't require the kind of detailed accounting that is 
required for proving the safety property.

To differ from a safety property, a liveness property ${\displaystyle LP}$ cannot rule out any 
finite prefix ${\displaystyle \alpha \in S^{*}}$ [^8] of an execution (since such an 
${\displaystyle \alpha }$ would be a "bad thing" and, thus, would be defining a safety property). 
That leads to defining a liveness property ${\displaystyle LP}$ to be a property that does not rule 
out any finite prefix.[^5]

${\displaystyle \forall \alpha \in S^{*}:(\exists \tau \in S^{\omega }:\alpha \tau \in LP)}$

This definition does not restrict a *good thing* to being discrete—the *good thing* can involve 
all of ${\displaystyle \tau }$, which is an infinite-length execution.

## History

[Lamport](https://en.wikipedia.org/wiki/Leslie_Lamport "Leslie Lamport") used the terms *safety 
property* and *liveness property* in his 1977 paper [^1] on proving the correctness of 
[multiprocess (concurrent) programs](https://en.wikipedia.org/wiki/Concurrent_computing "Concurrent 
computing"). He borrowed the terms from [Petri net theory](https://en.wikipedia.org/wiki/Petri_net 
"Petri net"), which was using the terms *liveness* and *boundedness* for describing how the 
assignment of a Petri net's "tokens" to its "places" could evolve; Petri net *safety* was a 
specific form of *boundedness*. Lamport subsequently developed a formal definition of safety for a 
NATO short course on distributed systems in Munich.[^9] It assumed that properties are invariant 
under [stuttering](https://en.wikipedia.org/wiki/Stuttering_equivalence "Stuttering equivalence"). 
The formal definition of safety given above appears in a paper by Alpern and Schneider;[^5] the 
connection between the two formalizations of safety properties appears in a paper by Alpern, 
Demers, and Schneider.[^10]

Alpern and Schneider [^5] gives the formal definition for liveness, accompanied by a proof that all 
properties can be constructed using safety properties and liveness properties. That proof was 
inspired by [Gordon Plotkin](https://en.wikipedia.org/wiki/Gordon_Plotkin "Gordon Plotkin") 's 
insight that safety properties correspond to [closed sets](https://en.wikipedia.org/wiki/Closed_set 
"Closed set") and liveness properties correspond to [dense 
sets](https://en.wikipedia.org/wiki/Dense_set "Dense set") in a natural 
[topology](https://en.wikipedia.org/wiki/Topology "Topology") on the set ${\displaystyle S^{\omega 
}}$ of infinite sequences of program states.[^11] Subsequently, Alpern and Schneider [^12] not only 
gave a [Büchi automaton](https://en.wikipedia.org/wiki/B%C3%BCchi_automaton "Büchi automaton") 
characterization for the formal definitions of safety properties and liveness properties but used 
these automata formulations to show that verification of safety properties would require an 
[invariant](https://en.wikipedia.org/wiki/Invariant_\(mathematics\)#Invariants_in_computer_science 
"Invariant (mathematics)") and verification of liveness properties would require a 
[well-foundedness argument](https://en.wikipedia.org/wiki/Well-founded_relation "Well-founded 
relation"). The correspondence between the kind of property (safety vs liveness) with kind of proof 
(invariance vs well-foundedness) was a strong argument that the decomposition of properties into 
safety and liveness (as opposed to some other partitioning) was a useful one—knowing the type of 
property to be proved dictated the type of proof that is required.

## References

[^1]: [Lamport, Leslie](https://en.wikipedia.org/wiki/Leslie_Lamport "Leslie Lamport") (March 
1977). "Proving the correctness of multiprocess programs". *[IEEE Transactions on Software 
Engineering](https://en.wikipedia.org/wiki/IEEE_Transactions_on_Software_Engineering "IEEE 
Transactions on Software Engineering")*. **SE-3** (2): 125–143. 
[doi](https://en.wikipedia.org/wiki/Doi_\(identifier\) "Doi 
(identifier)"):[10.1109/TSE.1977.229904](https://doi.org/10.1109%2FTSE.1977.229904). 
[S2CID](https://en.wikipedia.org/wiki/S2CID_\(identifier\) "S2CID (identifier)") 
[9985552](https://api.semanticscholar.org/CorpusID:9985552).

[^2]: Manna, Zohar; Pnueli, Amir (September 1974). "Axiomatic approach to total correctness of 
programs". *[Acta Informatica](https://en.wikipedia.org/wiki/Acta_Informatica "Acta Informatica")*. 
**3** (3): 243–263. [doi](https://en.wikipedia.org/wiki/Doi_\(identifier\) "Doi 
(identifier)"):[10.1007/BF00288637](https://doi.org/10.1007%2FBF00288637). 
[S2CID](https://en.wikipedia.org/wiki/S2CID_\(identifier\) "S2CID (identifier)") 
[2988073](https://api.semanticscholar.org/CorpusID:2988073).

[^3]: i.e. it has finite duration

[^4]: Alford, Mack W.; [Lamport, Leslie](https://en.wikipedia.org/wiki/Leslie_Lamport "Leslie 
Lamport"); Mullery, Geoff P. (3 April 1984). "Basic concepts". *Distributed Systems: Methods and 
Tools for Specification, An Advanced Course*. Lecture Notes in Computer Science. Vol. 190. Munich, 
Germany: [Springer Verlag](https://en.wikipedia.org/wiki/Springer_Verlag "Springer Verlag"). pp. 
7–43. [ISBN](https://en.wikipedia.org/wiki/ISBN_\(identifier\) "ISBN (identifier)") 
[3-540-15216-4](https://en.wikipedia.org/wiki/Special:BookSources/3-540-15216-4 
"Special:BookSources/3-540-15216-4").

[^5]: Alpern, Bowen; [Schneider, Fred B.](https://en.wikipedia.org/wiki/Fred_B._Schneider "Fred B. 
Schneider") (1985). "Defining liveness". *[Information Processing 
Letters](https://en.wikipedia.org/wiki/Information_Processing_Letters "Information Processing 
Letters")*. **21** (4): 181–185. [doi](https://en.wikipedia.org/wiki/Doi_\(identifier\) "Doi 
(identifier)"):[10.1016/0020-0190(85)90056-0](https://doi.org/10.1016%2F0020-0190%2885%2990056-0).

[^6]: Alpern, Bowen; [Schneider, Fred B.](https://en.wikipedia.org/wiki/Fred_B._Schneider "Fred B. 
Schneider") (1987). "Recognizing safety and liveness". *[Distributed 
Computing](https://en.wikipedia.org/wiki/Distributed_Computing_\(journal\) "Distributed Computing 
(journal)")*. **2** (3): 117–126. [doi](https://en.wikipedia.org/wiki/Doi_\(identifier\) "Doi 
(identifier)"):[10.1007/BF01782772](https://doi.org/10.1007%2FBF01782772). 
[hdl](https://en.wikipedia.org/wiki/Hdl_\(identifier\) "Hdl 
(identifier)"):[1813/6567](https://hdl.handle.net/1813%2F6567). 
[S2CID](https://en.wikipedia.org/wiki/S2CID_\(identifier\) "S2CID (identifier)") 
[9717112](https://api.semanticscholar.org/CorpusID:9717112).

[^7]: The paper [^5] received the [2018 Dijkstra 
Prize](https://en.wikipedia.org/wiki/Dijkstra_Prize "Dijkstra Prize") ("for outstanding papers on 
the principles of distributed computing whose significance and impact on the theory and/or practice 
of distributed computing have been evident for at least a decade"), for the formal decomposition 
into safety and liveness properties was crucial to future research into proving properties of 
programs.

[^8]: ${\displaystyle S^{*}}$ denotes the set of finite sequences of program states and 
${\displaystyle S^{\omega }}$ the set of infinite sequences of program states.

[^9]: Alford, Mack W.; [Lamport, Leslie](https://en.wikipedia.org/wiki/Leslie_Lamport "Leslie 
Lamport"); Mullery, Geoff P. (3 April 1984). "Basic concepts". *Distributed Systems: Methods and 
Tools for Specification, An Advanced Course*. Lecture Notes in Computer Science. Vol. 190. Munich, 
Germany: [Springer Verlag](https://en.wikipedia.org/wiki/Springer_Verlag "Springer Verlag"). pp. 
7–43. [ISBN](https://en.wikipedia.org/wiki/ISBN_\(identifier\) "ISBN (identifier)") 
[3-540-15216-4](https://en.wikipedia.org/wiki/Special:BookSources/3-540-15216-4 
"Special:BookSources/3-540-15216-4").

[^10]: Alpern, Bowen; Demers, Alan J.; [Schneider, Fred 
B.](https://en.wikipedia.org/wiki/Fred_B._Schneider "Fred B. Schneider") (November 1986). "Safety 
without stuttering". *Information Processing Letters*. **23** (4): 177–180. 
[doi](https://en.wikipedia.org/wiki/Doi_\(identifier\) "Doi 
(identifier)"):[10.1016/0020-0190(86)90132-8](https://doi.org/10.1016%2F0020-0190%2886%2990132-8). 
[hdl](https://en.wikipedia.org/wiki/Hdl_\(identifier\) "Hdl 
(identifier)"):[1813/6548](https://hdl.handle.net/1813%2F6548).

[^11]: Private communication from Plotkin to Schneider.

[^12]: Alpern, Bowen; [Schneider, Fred B.](https://en.wikipedia.org/wiki/Fred_B._Schneider "Fred B. 
Schneider") (1987). "Recognizing safety and liveness". *Distributed Computing*. **2** (3): 
117–126. [doi](https://en.wikipedia.org/wiki/Doi_\(identifier\) "Doi 
(identifier)"):[10.1007/BF01782772](https://doi.org/10.1007%2FBF01782772). 
[hdl](https://en.wikipedia.org/wiki/Hdl_\(identifier\) "Hdl 
(identifier)"):[1813/6567](https://hdl.handle.net/1813%2F6567). 
[S2CID](https://en.wikipedia.org/wiki/S2CID_\(identifier\) "S2CID (identifier)") 
[9717112](https://api.semanticscholar.org/CorpusID:9717112).
