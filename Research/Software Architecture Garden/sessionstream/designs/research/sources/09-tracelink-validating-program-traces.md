[^1] <sup>2</sup>

## Validating Traces of Distributed Programs Against Specifications††thanks: This work was partly supported by a grant from Oracle Corporation.

Horatiu Cirstea 11    Markus A. Kuppe 22    Benjamin Loillier 11    Stephan Merz 11

###### Abstract

is a formal language for specifying systems, including distributed algorithms, that is supported by powerful verification tools. In this work we present a framework for relating traces of distributed programs to high-level specifications written in. The problem is reduced to a constrained model checking problem, realized using the TLC model checker. Our framework consists of an API for instrumenting Java programs in order to record traces of executions, of a collection of operators that are used for relating those traces to specifications, and of scripts for running the model checker. Crucially, traces only contain updates to specification variables rather than full values, and it is not necessary to provide values for all variables. We have applied our approach to several distributed programs, detecting discrepancies between the specifications and the implementations in all cases. We discuss reasons for these discrepancies, how to interpret the verdict produced by TLC, and how to take into account the results of trace validation for implementation development.

## 1 Introduction

Distributed systems are at the heart of modern cloud services and they are known to be error-prone, due to phenomena such as delays or failures of nodes and communication networks. Applying formal methods in the design and development of these systems can help increase the confidence in their correctness and resilience. For example, the [^16] specification language and verification tools have been successfully used in industry [^20] [^24] for designing distributed algorithms underlying modern cloud systems. and similar specification formalisms are most useful for describing and analyzing systems at high levels of abstraction, but do not provide support for checking that actual implementations of these systems are correct. Although supports a notion of refinement, formally proving a chain of refinements from a high-level design of a distributed algorithm to an actual implementation would be a daunting task, complicated by the fact that standard programming languages do not provide explicit control of the grain of atomicity of the running program. In this work, we present a lightweight approach to validating distributed programs against high-level specifications that relies on recording finite traces of program executions and leveraging the model checker TLC [^28] for comparing those traces to the state machine described in the specification. Although this approach does not provide formal correctness guarantees, even when the specification has been extensively verified, we have found it very useful for discovering and analyzing discrepancies between the runs of distributed programs and their high-level specifications, including serious bugs that had gone undetected by more traditional quality assurance techniques.

The collection of program traces relies on an instrumentation of the program in order to record information on how program operations correspond to updates of the variables representing the state of the specification, and potentially indicating the corresponding transition in the specification. We have designed a Java library that facilitates this instrumentation and can be used to produce traces in JSON format. Because the traces record the evolution of the state of the specification, our approach is easiest to apply when the specification exists prior to building the implementation, the implementor is familar with it, and uses it as a blueprint when writing the code. However, we have also used the approach in order to “reverse engineer” a specification from an existing distributed program and better understand its operation. Trace validation can also help ensure that the specification and implementation remain in sync over time because it is easy to apply it again when the specification or the implementation changes.

The main problem when instrumenting a program is to identify suitable “linearization points” at which the program completes a step that corresponds to an atomic transition of the high-level state machine. Basic guiding principles are to log an event when shared state has been updated, such as when sending or receiving messages, performing operations on locks or on stable data storage. We discuss how to account for different grain of atomicity between the specification and the implementation based on feedback from trace validation. Because data representation generally differs between the specification and the actual program, it may be difficult or impractical to compute the value of a high-level variable (or its update) corresponding to the data manipulated by the implementation. We therefore allow traces to be incomplete and only record some information about the corresponding abstract state. We reduce the problem of trace validation to one of constrained model checking and show how TLC can reconstruct missing information. This leads to a tradeoff between the precision of information recorded in the trace (and potentially of the verdict of validation) and the amount of search that TLC must perform during model checking.

The paper is organized as follows: Section 2 provides some background on and introduces our running example, both in and as a Java program. Our approach to instrumentation is described in Section 3. In Section 4 we formalize the trace validation problem, describe how we realized the approach using TLC, and discuss our experience with it. Section 5 discusses related work, and Section 6 concludes the paper and presents some perspectives for future work.

## 2 Background

### 2.1 Specifications

[^16] is a specification language based on Zermelo-Fraenkel set theory and linear-time temporal logic that has found wide use for writing high-level specifications of concurrent and distributed algorithms. It emphasizes the use of mathematical descriptions based on sets and functions for specifying data structures. is a state-based specification formalism: the state space of a system is represented using variables, and formulas are evaluated over *behaviors*, i.e., sequences of states that assign values to variables. Algorithms are described as state machines whose specifications are written in the canonical form

$$
Init\land\Box[Next]_{vars}\land L.
$$

In this formula, $Init$ is a state predicate describing the possible initial states of the system, $Next$ represents the next-state relation, usually written as the disjunction of actions describing the possible state transitions, $vars$ is a tuple containing all state variables that appear in the specification, and $L$ is a temporal formula asserting liveness and fairness assumptions. A state predicate is a formula of first-order logic containing state variables, and it is evaluated over single states. A transition predicate (or, synonymously, action) is a first-order formula that may contain unprimed and primed occurrences of state variables. Such a formula is evaluated over a pair of states, with unprimed variables referring to the values before the transition and primed variables to the values after the transition. The formula $[Next]_{vars}$ holds of any pair of states $\langle s,t\rangle$ if either $Next$ holds of $\langle s,t\rangle$ (and therefore the pair represents an actual step of the system) or all variables in $vars$ evaluate to the same values in the two states (and the pair represents a stuttering step). Systematically allowing for stuttering steps enables the implementation of a system specification by a lower-level specification to be represented as validity of implication between the formulas expressing the specifications. The complementary property $L$ is used to express fairness assumptions and is at the basis of verifying liveness properties of algorithms. Since in this work we only analyze finite traces of programs, we ignore liveness properties and are interested in finite behaviors, i.e., sequences $s_{0}\dots s_{n}$ of states such that $Init$ holds of $s_{0}$ and $[Next]_{vars}$ holds for all pairs $\langle s_{i},s_{i+1}\rangle$ for $i\in 0\,..\,n-1$.

![Refer to caption](https://arxiv.org/html/2404.16075v1/extracted/2404.16075v1/TLADebugger2.png)

Figure 1: Trace validation as a search for paths in the state space.

[^1]: D. Cousineau, D. Doligez, L. Lamport, S. Merz, D. Ricketts, and H. Vanzetto. TLA <sup>+</sup> Proofs. In D. Giannakopoulou and D. Méry, editors, FM 2012: Formal Methods, volume 7436 of LNCS, pages 147–154, Paris, France, 2012. Springer.

[^2]: A. J. J. Davis, M. Hirschhorn, and J. Schvimer. eXtreme Modelling in Practice. Proceedings of the VLDB Endowment, 13(9):1346–1358, May 2020.

[^3]: E. W. Dijkstra. EWD 998: Shmuel Safra’s version of termination detection. http://www.cs.utexas.edu/users/EWD/ewd09xx/EWD998.PDF, Jan. 1987.

[^4]: Y. Falcone, K. Havelund, and G. Reger. A tutorial on runtime verification. Engineering Dependable Software Systems, 34:141–175, 01 2013.

[^5]: A. Fekete. Snapshot isolation. In L. Liu and M. T. Özsu, editors, Encyclopedia of Database Systems, pages 2659–2664. Springer, 2009.

[^6]: D. Foo, A. Costea, and W.-N. Chin. Protocol Conformance with Choreographic PlusCal. In C. David and M. Sun, editors, Theoretical Aspects of Software Engineering, volume 13931, pages 126–145. 2023.

[^7]: F. Hackett, S. Hosseini, R. Costa, M. Do, and I. Beschastnikh. Compiling distributed system models with PGo. In Proceedings of the 28th ACM International Conference on Architectural Support for Programming Languages and Operating Systems, Volume 2, pages 159–175, Vancouver BC Canada, Jan. 2023. ACM.

[^8]: J. Haltermann. Bridging the verifiability gap: Why we need more from our specs and how we get it. https://conf.tlapl.us/2020/, Oct. 2020.

[^9]: K. Havelund. Using runtime analysis to guide model checking of Java programs. In G. Goos, J. Hartmanis, J. Van Leeuwen, K. Havelund, J. Penix, and W. Visser, editors, SPIN Model Checking and Software Verification, volume 1885, pages 245–264. Springer, 2000.

[^10]: H. Howard, F. Alder, E. Ashton, A. Chamayou, S. Clebsch, M. Costa, A. Delignat-Lavaud, C. Fournet, A. Jeffery, M. Kerner, F. Kounelis, M. A. Kuppe, J. Maffre, M. Russinovich, and C. M. Wintersteiger. Confidential Consortium Framework: Secure multiparty applications with confidentiality, integrity, and high availability. Proceedings of the VLDB Endowment, 17(2):225–240, Oct. 2023.

[^11]: H. Howard, E. Ashton, A. Chamayou, M. A. Kuppe, and N. Crooks. Towards smart casual verification of the Confidential Consortium Framework’s distributed protocols. In preparation, 2024.

[^12]: Y. Howard, S. Gruner, A. Gravell, C. Ferreira, and J. C. Augusto. Model-based trace-checking. arXiv:1111.2825 \[cs\], Nov. 2011.

[^13]: I. Konnov, M. Kuppe, and S. Merz. Specification and verification with the TLA <sup>+</sup> trifecta: TLC, Apalache, and TLAPS. In T. Margaria and B. Steffen, editors, Leveraging Applications of Formal Methods, Verification and Validation. Verification Principles, volume 13701, pages 88–105. Springer, 2022.

[^14]: M. A. Kuppe. Implementing a TLA <sup>+</sup> specification: EWD998Chan. https://github.com/tlaplus/Examples/pull/75, Apr. 2023.

[^15]: M. A. Kuppe. The TLA <sup>+</sup> debugger. In P. Masci, C. Bernardeschi, P. Graziani, M. Koddenbrock, and M. Palmieri, editors, Software Engineering and Formal Methods. SEFM 2022 Collocated Workshops, volume 13765, pages 174–180. Springer, 2023.

[^16]: L. Lamport. Specifying Systems. Addison-Wesley, Boston, Mass., 2002.

[^17]: L. Lamport, M. A. Kuppe, S. Merz, A. Helwer, W. Schultz, J. Hemphill, M. Ryndzionek, I. Konnov, T. H. Tran, J. Widder, J. Gray, M. Demirbas, G. Hu, G. Losa, R. Pressler, Y. Akhouayri, L. Dong, Z. Niu, L. N. X. Terry, G. Gandhi, I. DeFrain, M. Harrison, S. Raju, C. G. Mathew, F. Andriani, and L. Yvoz. TLA <sup>+</sup> examples.

[^18]: L. Lamport, J. Matthews, M. Tuttle, and Y. Yu. Specifying and verifying systems with TLA <sup>+</sup>. In Proceedings of the 10th Workshop on ACM SIGOPS European Workshop: Beyond the PC - EW10, page 45, Saint-Emilion, France, 2002. ACM Press.

[^19]: J. Nadal. Stateright. https://github.com/stateright/stateright, 2018.

[^20]: C. Newcombe, T. Rath, F. Zhang, B. Munteanu, M. Brooker, and M. Deardeuff. How Amazon Web Services uses formal methods. Communications of the ACM, 58(4):66–73, Mar. 2015.

[^21]: Z. Niu, L. Dong, Y. Zhu, and L. Chen. Verifying Zookeeper based on model-based runtime trace-checking using TLA <sup>+</sup>. In Proceedings of the 7th International Conference on Cyber Security and Information Engineering, pages 13–18, Brisbane QLD Australia, Sept. 2022. ACM.

[^22]: D. Ongaro and J. Ousterhout. In search of an understandable consensus algorithm. In 2014 USENIX Annual Technical Conference, pages 305–319, Philadelphia, PA, June 2014. USENIX Association.

[^23]: R. Pressler. Conjunction Capers: A TLA <sup>+</sup> Truffle. https://conf.tlapl.us/2020/, Sept. 2020.

[^24]: W. Schultz, S. Zhou, I. Dardik, and S. Tripakis. Design and analysis of a logless dynamic reconfiguration protocol. In Q. Bramas, V. Gramoli, and A. Milani, editors, 25th Intl. Conf. Principles of Distributed Systems (OPODIS 2021), volume 217 of LIPIcs, pages 26:1–26:16, Strasbourg, France, 2021. Schloss Dagstuhl - Leibniz-Zentrum für Informatik.

[^25]: P. Springmeyer. Spectacle. https://github.com/awakesecurity/spectacle, 2021.

[^26]: S. Tasiran, Y. Yu, B. Batson, and S. Kreider. Using formal specifications to monitor and guide simulation: Verifying the cache coherence engine of the Alpha 21364 microprocessor. In In Proceedings of the 3rd IEEE Workshop on Microprocessor Test and Verification, Common Challenges and Solutions, 2002.

[^27]: D. Wang, W. Dou, Y. Gao, C. Wu, J. Wei, and T. Huang. Model checking guided testing for distributed systems. In Proceedings of the Eighteenth European Conference on Computer Systems, pages 127–143, Rome Italy, May 2023. ACM.

[^28]: Y. Yu, P. Manolios, and L. Lamport. Model checking TLA <sup>+</sup> specifications. In L. Pierre and T. Kropf, editors, 10th IFIP WG 10.5 Conf. Correct Hardware Design and Verification Methods (CHARME’99), volume 1703 of LNCS, pages 54–66, Bad Herrenalb, Germany, 1999. Springer.
