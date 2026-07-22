# Handheld Vacuum Noise Causes

- URL: https://chatgpt.com/c/6a610946-7508-83ea-9689-097906907f4e
- Created: 2026-07-22T18:17:47.712Z

---

> Why are handheld vacuums so loud, how is the sound produced, how can you make quiet vacuums?

Handheld vacuums are loud because they move a large amount of air through a very small machine. To get useful suction from a compact battery-powered device, the motor and fan must spin extremely fast—often tens of thousands of revolutions per minute.

## Where the sound comes from

The main sources are:

**1. Motor and fan rotation**  
The impeller repeatedly pushes air with each blade. This creates pressure pulses at the blade-passing frequency:

\[
f = N \times \frac{\text{RPM}}{60}
\]

where \(N\) is the number of fan blades. These pulses produce the characteristic high-pitched whine.

**2. Turbulent airflow**  
Air is forced through narrow openings, filters, bends, grilles, and dust passages. Flow separation and vortices create broadband “rushing” noise. A clogged filter or partly blocked nozzle usually makes this worse.

**3. Intake and exhaust noise**  
The inlet behaves somewhat like a whistle or resonant pipe. The exhaust can produce a strong hiss because high-velocity air is discharged through a small area.

**4. Vibration**  
Motor imbalance, bearings, fan imbalance, and torque fluctuations vibrate the plastic housing. Large, thin panels can act like loudspeaker diaphragms and amplify the sound.

**5. Structural resonance**  
The body contains enclosed cavities and ducts. Certain frequencies excite these spaces, increasing specific tones rather than merely creating general airflow noise.

Handheld units often sound harsher than full-size vacuums because their small fans rotate faster, their insulation is thinner, and the motor is held close to the user’s ears.

## Why adding more suction often makes noise rise sharply

Airflow noise does not generally increase in direct proportion to speed. In many aerodynamic systems, sound power increases approximately with a high power of flow velocity. Therefore, a modest increase in fan speed can produce a much larger increase in perceived noise.

Also, “suction” involves both pressure difference and airflow. A vacuum designed to create high pressure through a narrow nozzle may be especially noisy even if its total airflow is not very large.

## How quieter vacuums can be made

A quieter design attacks both the source and the transmission path.

### Use a larger, slower fan

A larger impeller can move similar air at lower rotational speed. This reduces blade-passing frequency and turbulence. It is one reason larger vacuums can sometimes sound lower and less irritating.

The disadvantage is increased size and weight.

### Improve the impeller and ducts

Useful measures include:

- Curved or backward-swept fan blades
- Uneven blade spacing to spread tonal energy across multiple frequencies
- More clearance from nearby stationary surfaces
- Smooth, gradually expanding air passages
- Rounded duct entrances
- Fewer sharp turns and sudden changes in cross-section
- Larger exhaust openings to reduce exit velocity

Poor airflow geometry can make a powerful motor sound much louder than necessary.

### Add mufflers to the exhaust

The exhaust can pass through:

- Expansion chambers
- Perforated ducts surrounded by sound-absorbing material
- Labyrinth passages
- Quarter-wave resonators tuned to a dominant motor or fan tone
- Helmholtz resonators tuned to specific frequencies

These must be designed carefully because excessive restriction reduces airflow, increases heat, and may make the motor spin faster.

### Isolate motor vibration

The motor-fan assembly can be mounted using rubber or elastomer supports instead of being rigidly attached to the shell. Balanced impellers, better bearings, and tighter manufacturing tolerances also reduce vibration.

### Make the housing less resonant

A quiet enclosure may use:

- Thicker or ribbed plastic
- Constrained-layer damping
- Internal foam in appropriate locations
- Double-wall construction
- Smaller unsupported panel areas
- Seals that prevent air leaks and rattling joints

Simply making the housing heavier can help, but structural shape and damping are often more important than mass alone.

### Use a high-efficiency motor

A brushless DC motor generally avoids brush-contact noise and can be controlled more precisely. Better efficiency also reduces waste heat, allowing lower cooling airflow.

However, brushless motors may still produce electronic tonal noise from switching and commutation.

### Control speed intelligently

A vacuum does not always need maximum power. Pressure and airflow sensors can reduce fan speed on open surfaces and increase it only when blockage or heavy debris is detected.

A quieter “normal” setting may provide nearly the same real cleaning performance as a much louder maximum setting.

### Reduce filter pressure loss

A large, clean filter with more surface area allows air to pass at lower velocity. This reduces turbulence and prevents the motor from operating near a high-pressure, low-flow condition.

The filter must still capture fine particles, so quietness cannot come at the expense of filtration.

## The fundamental tradeoff

For a handheld vacuum, the competing goals are:

\[
\text{small size} + \text{strong suction} + \text{long runtime} + \text{low cost} + \text{low noise}
\]

It is difficult to maximize all five simultaneously. The most effective path to a genuinely quiet handheld vacuum is usually a slightly larger body, larger fan, lower rotational speed, efficient ducting, vibration isolation, and a well-designed exhaust silencer—not merely surrounding the motor with foam.


---

> Motivate category theory pullbacks based on vacuum noise as a domain

<details><summary>💭 Thinking</summary>

**Explaining pullbacks in category theory**

I’m focusing on explaining pullbacks via vacuum noise. I’ll break it down with examples, helping to illustrate how pullbacks encode agreements between system components, like motor-fan and enclosure configurations.

**Explained pullbacks in category theory**

</details>

A handheld vacuum is a useful domain for motivating **pullbacks** because it is assembled from subsystems that must agree on shared interface conditions.

## 1. The engineering problem

Suppose we are designing two parts independently:

- \(A\): possible **motor–fan designs**
- \(B\): possible **duct, filter, and muffler designs**
- \(I\): possible **airflow-interface states**

An interface state might contain:

\[
(\text{flow rate},\ \text{pressure},\ \text{port diameter},\ \text{air temperature},\ \text{dominant frequencies})
\]

Each motor–fan design produces an interface state:

\[
f:A\to I
\]

Each duct or muffler design expects, or is designed for, an interface state:

\[
g:B\to I
\]

The ordinary product \(A\times B\) contains every possible motor–muffler pairing. Most of those pairings are invalid: perhaps the motor delivers \(25\text{ L/s}\), while the muffler was designed for \(10\text{ L/s}\).

The valid assembled vacuum designs are therefore

\[
A\times_I B
=
\{(a,b)\in A\times B\mid f(a)=g(b)\}.
\]

This is the **pullback**.

## 2. The pullback square

\[
\begin{array}{ccc}
A\times_I B & \xrightarrow{\pi_B} & B\\
\downarrow{\pi_A} & & \downarrow g\\
A & \xrightarrow{f} & I
\end{array}
\]

The square commutes because a compatible assembly has one common interface state:

\[
f\circ\pi_A=g\circ\pi_B.
\]

In vacuum language:

> Looking at the selected motor’s output conditions gives the same result as looking at the selected muffler’s required input conditions.

## 3. Concrete example

Let the interface contain only airflow rate and pressure:

\[
I=\{(q,p)\}.
\]

Suppose

\[
A=
\{
a_1,a_2,a_3
\}
\]

with

\[
f(a_1)=(12,8),\qquad
f(a_2)=(18,12),\qquad
f(a_3)=(18,12).
\]

The numbers might represent litres per second and kilopascals.

Let

\[
B=
\{
b_1,b_2,b_3
\}
\]

with

\[
g(b_1)=(12,8),\qquad
g(b_2)=(18,12),\qquad
g(b_3)=(20,12).
\]

Then

\[
A\times_I B
=
\{
(a_1,b_1),
(a_2,b_2),
(a_3,b_2)
\}.
\]

The full product has nine possible combinations, but the pullback keeps only the three combinations whose interfaces agree.

This is the basic intuition:

\[
\boxed{\text{pullback}=\text{product subject to compatibility}}
\]

## 4. Why the universal property matters

Suppose \(X\) is another description of complete vacuum designs. From each complete design, we can extract:

\[
u:X\to A
\]

the motor–fan configuration, and

\[
v:X\to B
\]

the muffler configuration.

If these always agree at the interface,

\[
f\circ u=g\circ v,
\]

then there is a unique map

\[
h:X\to A\times_I B
\]

such that

\[
\pi_A\circ h=u,\qquad
\pi_B\circ h=v.
\]

In engineering terms:

> Any collection of correctly assembled vacuums can be represented uniquely as a collection of compatible motor–muffler pairs.

The pullback is not merely one possible database of valid combinations. It is the canonical one determined by the interface maps.

## 5. How this relates specifically to noise

Vacuum noise is produced by several coupled systems:

- motor electromagnetic excitation,
- fan blade-passing pressure pulses,
- turbulent duct flow,
- exhaust jets,
- structural vibration,
- housing resonances.

These systems cannot be optimized independently. A quieter fan may require a larger outlet; a muffler may introduce back pressure; back pressure may move the fan to a noisier operating point.

For example, define:

- \(A\): motor–fan designs,
- \(B\): acoustic-treatment designs,
- \(I\): operating signatures.

An operating signature could include

\[
i=(q,p,\omega,T,S),
\]

where

- \(q\) is airflow,
- \(p\) is pressure,
- \(\omega\) is rotational speed,
- \(T\) is temperature,
- \(S\) is a simplified noise spectrum.

Then the pullback selects acoustic treatments that are compatible with the actual operating state of the fan:

\[
A\times_I B.
\]

This prevents invalid reasoning such as choosing a silencer tested at low airflow and attaching it to a high-flow fan while assuming its quoted noise reduction will remain unchanged.

## 6. A second pullback: combining test data

Pullbacks also appear when collecting measurements.

Let:

- \(M\): motor telemetry records,
- \(N\): microphone recordings,
- \(T\): test timestamps.

There are maps

\[
t_M:M\to T,\qquad t_N:N\to T.
\]

Then

\[
M\times_T N
\]

contains pairs consisting of a motor record and a microphone record taken at the same time.

An element might be

\[
(\text{RPM}=72{,}000,\ \text{sound}=79\text{ dBA at }14{:}03{:}12.4).
\]

This lets an engineer correlate fan speed with acoustic peaks without accidentally pairing measurements from different test moments.

The common object does not have to be time. It could be:

- test-run identifier,
- vacuum serial number,
- nozzle configuration,
- battery voltage,
- airflow operating point.

## 7. Pullbacks as “joining on a shared key”

In the category of sets, a pullback resembles a database join.

Suppose one table contains:

| Motor design | Interface ID |
|---|---|
| M1 | Low-flow |
| M2 | High-flow |

Another contains:

| Muffler design | Interface ID |
|---|---|
| S1 | Low-flow |
| S2 | High-flow |

Their pullback over the interface identifier gives:

| Motor | Muffler | Interface |
|---|---|---|
| M1 | S1 | Low-flow |
| M2 | S2 | High-flow |

But the categorical idea is broader than a database join. Pullbacks can be formed in categories of:

- sets,
- databases,
- graphs,
- topological spaces,
- smooth models,
- probability models,
- software components.

The same compatibility pattern survives even when the objects carry richer structure.

## 8. The central motivation

Vacuum design involves independently developed components that must agree on shared physical conditions. Pullbacks formalize the operation:

\[
\text{combine two subsystem models while enforcing agreement at their interface}.
\]

Thus:

- a **product** means “choose a motor and choose a muffler”;
- a **pullback** means “choose a motor and a muffler that can actually operate together.”

That distinction is why pullbacks are fundamental in system design, data integration, constraint satisfaction, and compositional engineering.


---

> Write a full textbook chapter motivating / bringing in pullbacks for engineers, with motivation, definitions, proofs, exercises.

<details><summary>💭 Thinking</summary>

**Planning a chapter**

I’m thinking of whether to provide a full textbook chapter on a math topic, focusing on concepts like category theory, limits, and stability. I should carefully structure it and perhaps include exercises with solutions. It might take time but I’ll aim for thoroughness.

**Outlining the chapter**

I’m creating a plan for a textbook chapter on pullbacks in engineering, incorporating category theory for quiet vacuum systems. I’ll focus on motivating examples, definitions, and proofs related to compatibility equations and universal properties. It’ll be detailed!

**Planned a chapter**

</details>

I’ll build a self-contained chapter around engineering compatibility, using vacuum noise to motivate formal definitions, the universal property, proofs, worked design patterns, and graded exercises with selected solutions.

<details><summary>💭 Thinking</summary>

**Completing the outline**

I’m adding more to the chapter outline, incorporating advanced topics like database joins, graphs, and vector spaces, while including a vacuum case study to tie theory to real-world systems. I'll also cover proofs on pullbacks.

**Completed the outline**

**Refining the chapter plan**

I’m refining the chapter outline, adding exercises and brief solutions, ensuring proof details are clear. I'll also include a glossary, keep the chapter concise (around 7-9k words), and use engineering examples like vacuum systems.

**Refined the chapter plan**

</details>

The key model treats fan and airflow-path pressure–flow states as physically consistent operating points, extending beyond simple parts matching to synchronization and tolerances.

# Chapter 8  
# Pullbacks: Engineering with Compatible Interfaces

## 8.1 Purpose of this chapter

Engineering systems are rarely built by choosing components independently and placing them side by side. Components must agree on shared quantities:

- a fan and duct must operate at the same airflow and pressure;
- two mechanical substructures must have matching boundary displacements;
- connected electrical components must agree on terminal voltage and satisfy current balance;
- telemetry records must refer to the same test run and time;
- a component must satisfy the requirements attached to its interface class.

A categorical **product** represents an unrestricted choice of two components. A **pullback** represents a choice of two components together with the requirement that their shared interface descriptions agree.

The guiding interpretation is

\[
\boxed{\text{pullback}=\text{combination subject to compatibility}.}
\]

This chapter develops that idea from an engineering example, states the categorical definition, proves its main properties, and shows how pullbacks appear in physical modeling, linear algebra, requirements engineering, databases, and experimental data processing.

### Learning objectives

After completing the chapter, the reader should be able to:

1. distinguish an unrestricted product from a compatible interconnection;
2. construct pullbacks in the category of sets;
3. state and use the universal property of a pullback;
4. explain why commutativity alone is not sufficient;
5. model subsystem interconnection using shared interface variables;
6. recognize fibers, inverse images, database joins, and linear compatibility spaces as pullbacks;
7. prove uniqueness of pullbacks up to unique isomorphism;
8. use pullback pasting and preservation results;
9. model engineering tolerances without treating approximate equality as exact equality.

---

# 8.2 The motivating problem: predicting vacuum noise

Consider the design of a quiet handheld vacuum. Several subsystems contribute to its behavior:

- the motor and impeller create a pressure rise;
- the duct, filter, cyclone, nozzle, and exhaust create pressure losses;
- the impeller produces tonal and broadband aerodynamic noise;
- the airflow path attenuates some frequencies and generates additional turbulence;
- the housing converts internal pressure fluctuations and motor forces into radiated sound.

A naive design model might treat a fan design and a muffler design as independent choices:

\[
(\text{fan design},\text{muffler design}).
\]

That is not enough. A muffler tested at one flow rate cannot automatically be assigned the same acoustic performance at another flow rate. The motor, fan, filter, and exhaust must reach one common operating point.

## 8.2.1 Fan and flow-path behavior

Let:

- \(A\) be the set of motor–fan designs;
- \(B\) be the set of duct–filter–muffler designs;
- \(\mathsf Q\) be the set of possible volume flow rates;
- \(\mathsf P\) be the set of possible pressure differences.

The common aerodynamic interface is

\[
I=\mathsf Q\times \mathsf P.
\]

For each fan design \(a\in A\), let

\[
p=\Phi_a(q)
\]

be its pressure-rise curve. Define the set of feasible fan states

\[
F=
\left\{
(a,q,p)\in A\times \mathsf Q\times \mathsf P
\;\middle|\;
p=\Phi_a(q)
\right\}.
\]

There is an interface map

\[
s:F\longrightarrow I,
\qquad
s(a,q,p)=(q,p).
\]

Similarly, let

\[
p=\Psi_b(q)
\]

be the pressure-loss curve for airflow-path design \(b\in B\). Define

\[
D=
\left\{
(b,q,p)\in B\times \mathsf Q\times \mathsf P
\;\middle|\;
p=\Psi_b(q)
\right\},
\]

with interface map

\[
t:D\longrightarrow I,
\qquad
t(b,q,p)=(q,p).
\]

A physically consistent assembled vacuum requires a fan state and a duct state that report the same \(q\) and \(p\). Thus its operating states are

\[
F\times_I D
=
\left\{
(x,y)\in F\times D
\;\middle|\;
s(x)=t(y)
\right\}.
\]

An element can be written more compactly as

\[
(a,b,q,p)
\]

satisfying

\[
p=\Phi_a(q)=\Psi_b(q).
\]

This object is the **pullback** of \(s\) and \(t\).

## 8.2.2 Numerical operating-point example

Suppose a fan has the pressure curve

\[
\Phi(q)=18-0.12q^2
\]

and a duct–filter–muffler assembly has the loss curve

\[
\Psi(q)=0.06q^2,
\]

where pressure is measured in kilopascals and flow in litres per second.

Compatibility requires

\[
18-0.12q^2=0.06q^2.
\]

Therefore

\[
18=0.18q^2,
\qquad
q^2=100,
\qquad
q=10,
\]

using the physically relevant nonnegative root. The common pressure is

\[
p=0.06(10)^2=6.
\]

The assembled operating state is therefore

\[
(q,p)=(10\text{ L/s},6\text{ kPa}).
\]

The fan and muffler models cannot be evaluated independently at arbitrarily selected operating points. Their predictions must be brought to the common domain

\[
F\times_I D.
\]

## 8.2.3 Why this matters acoustically

Suppose the fan-side model produces an acoustic spectrum

\[
N_F:F\longrightarrow S,
\]

where \(S\) is a space of sound-power spectra. Suppose the duct model provides:

- a transfer operator \(H_D:D\to \operatorname{End}(S)\);
- a self-noise spectrum \(N_D:D\to S\).

The pullback projections are

\[
\pi_F:F\times_I D\to F,
\qquad
\pi_D:F\times_I D\to D.
\]

A simplified total spectrum on the assembled system can be written

\[
N_{\mathrm{total}}(x)
=
H_D\!\left(\pi_D(x)\right)
\left(
N_F\!\left(\pi_F(x)\right)
\right)
+
N_D\!\left(\pi_D(x)\right).
\]

The expression is meaningful because both subsystem models are evaluated at states with the same aerodynamic interface values.

For incoherent acoustic sources, addition should be performed using linear power quantities rather than by directly adding decibel values. More elaborate models may also need phase, coherence, spatial mode, and structural-vibration information in the interface.

The important categorical point is independent of the precise acoustic model:

> The pullback creates the domain on which subsystem predictions refer to one consistent assembled state.

---

# 8.3 Minimal categorical language

A **category** consists of:

1. objects;
2. morphisms, or arrows, between objects;
3. associative composition of morphisms;
4. an identity morphism on each object.

Examples relevant to engineering include:

- **Set**: sets and functions;
- **Vect**: vector spaces and linear maps;
- **Top**: topological spaces and continuous maps;
- categories of state machines and structure-preserving maps;
- categories of schemas, records, or typed software components.

In this chapter, an arrow often means that one model exposes or reports some information.

For example,

\[
s:F\to I
\]

means that each fan-side state determines an interface state.

## 8.3.1 Commuting diagrams

A diagram commutes when every directed path with the same starting and ending objects gives the same composite morphism.

For example,

\[
\begin{array}{ccc}
P & \xrightarrow{p_B} & B\\
{\scriptstyle p_A}\downarrow && \downarrow{\scriptstyle g}\\
A & \xrightarrow{f} & C
\end{array}
\]

commutes when

\[
f\circ p_A=g\circ p_B.
\]

For every state in \(P\), extracting its \(A\)-component and then its interface gives the same result as extracting its \(B\)-component and then its interface.

## 8.3.2 Cospans

A diagram

\[
A\xrightarrow{f}C\xleftarrow{g}B
\]

is called a **cospan**.

The object \(C\) is the shared target. In an engineering model, it often represents:

- an interface-variable space;
- a type or standard;
- a requirement classification;
- a timestamp or test identifier;
- a boundary-state space.

A pullback constructs the compatible interconnection of \(A\) and \(B\) over \(C\).

---

# 8.4 Definition of a pullback

## Definition 8.1: Pullback

Given morphisms

\[
A\xrightarrow{f}C\xleftarrow{g}B,
\]

a **pullback** consists of an object \(P\) and morphisms

\[
p_A:P\to A,
\qquad
p_B:P\to B
\]

such that:

### 1. Compatibility

The square commutes:

\[
f\circ p_A=g\circ p_B.
\]

### 2. Universality

For every object \(X\) with morphisms

\[
u:X\to A,
\qquad
v:X\to B
\]

satisfying

\[
f\circ u=g\circ v,
\]

there exists a unique morphism

\[
h:X\to P
\]

such that

\[
p_A\circ h=u,
\qquad
p_B\circ h=v.
\]

The diagram is

\[
\begin{array}{ccccc}
&&X&&\\
&{\scriptstyle u}\swarrow&\downarrow{\scriptstyle h}&\searrow{\scriptstyle v}&\\
A&\xleftarrow{\ p_A\ }&P&\xrightarrow{\ p_B\ }&B\\
&{\scriptstyle f}\searrow&&\swarrow{\scriptstyle g}&\\
&&C&&
\end{array}
\]

and the pullback is commonly denoted

\[
P=A\times_C B.
\]

The map \(h\) is often written

\[
h=\langle u,v\rangle.
\]

## 8.4.1 Engineering interpretation of the universal property

The compatibility equation

\[
f\circ u=g\circ v
\]

says that the two descriptions extracted from \(X\) agree at their interface.

The universal property says that every such compatible description has exactly one representation as a state of the pullback.

Thus the pullback is:

- **complete**: it includes every compatible combination;
- **nonredundant**: it does not contain multiple indistinguishable copies of the same compatible combination;
- **canonical**: it is determined by the interface maps, not by arbitrary implementation choices.

A pullback is also described as the **terminal compatible cone** over the cospan.

---

# 8.5 Pullbacks in the category of sets

The most concrete construction occurs in **Set**.

## Proposition 8.1: Set-theoretic construction

For functions

\[
f:A\to C,
\qquad
g:B\to C,
\]

define

\[
A\times_C B
=
\left\{
(a,b)\in A\times B
\;\middle|\;
f(a)=g(b)
\right\}.
\]

Let the projections be

\[
p_A(a,b)=a,
\qquad
p_B(a,b)=b.
\]

Then \(A\times_C B\), with these projections, is a pullback.

### Proof

First, the square commutes. For every \((a,b)\in A\times_C B\),

\[
f(p_A(a,b))
=
f(a)
=
g(b)
=
g(p_B(a,b)).
\]

Now suppose a set \(X\) has functions

\[
u:X\to A,
\qquad
v:X\to B
\]

such that

\[
f\circ u=g\circ v.
\]

Define

\[
h:X\to A\times_C B
\]

by

\[
h(x)=(u(x),v(x)).
\]

This is well-defined because

\[
f(u(x))=g(v(x)),
\]

so \((u(x),v(x))\) belongs to the pullback.

The projection equations hold:

\[
p_A(h(x))=u(x),
\qquad
p_B(h(x))=v(x).
\]

To prove uniqueness, suppose \(k:X\to A\times_C B\) also satisfies

\[
p_A\circ k=u,
\qquad
p_B\circ k=v.
\]

Since an ordered pair is determined by its two components,

\[
k(x)
=
\bigl(p_A(k(x)),p_B(k(x))\bigr)
=
(u(x),v(x))
=
h(x).
\]

Therefore \(k=h\). ∎

## 8.5.1 Product versus pullback

The ordinary product is

\[
A\times B
=
\{(a,b)\mid a\in A,\ b\in B\}.
\]

The pullback is

\[
A\times_C B
=
\{(a,b)\in A\times B\mid f(a)=g(b)\}.
\]

Therefore

\[
A\times_C B\subseteq A\times B.
\]

The product permits every pairing. The pullback retains only interface-compatible pairings.

## 8.5.2 Finite example

Let

\[
A=\{a_1,a_2,a_3\},
\qquad
B=\{b_1,b_2,b_3\},
\qquad
C=\{\mathrm{low},\mathrm{high}\}.
\]

Suppose

\[
\begin{aligned}
f(a_1)&=\mathrm{low},\\
f(a_2)&=\mathrm{high},\\
f(a_3)&=\mathrm{high},
\end{aligned}
\qquad
\begin{aligned}
g(b_1)&=\mathrm{low},\\
g(b_2)&=\mathrm{high},\\
g(b_3)&=\mathrm{low}.
\end{aligned}
\]

Then

\[
A\times_C B
=
\{
(a_1,b_1),
(a_1,b_3),
(a_2,b_2),
(a_3,b_2)
\}.
\]

The ordinary product contains nine pairs. The pullback contains the four pairs with matching interface classes.

---

# 8.6 Why commutativity is not enough

A commuting square provides compatible projections, but it need not contain exactly the compatible states.

## 8.6.1 A square that is too small

Suppose

\[
A\times_C B
=
\{(a_1,b_1),(a_2,b_2)\}.
\]

Take only the subset

\[
Q=\{(a_1,b_1)\}.
\]

The projection square for \(Q\) still commutes, because every element of \(Q\) is compatible. But \(Q\) omits the compatible pair \((a_2,b_2)\).

For a test object \(X=\{*\}\) selecting \(a_2\) and \(b_2\), no map \(X\to Q\) can realize the compatible pair. The existence part of the universal property fails.

## 8.6.2 A square that is too large or redundant

Let

\[
\widetilde P=(A\times_C B)\times\{0,1\}.
\]

Define projections that ignore the last coordinate:

\[
\widetilde p_A((a,b),i)=a,
\qquad
\widetilde p_B((a,b),i)=b.
\]

The square commutes. However, a compatible pair \((a,b)\) has two representations:

\[
((a,b),0)
\quad\text{and}\quad
((a,b),1).
\]

There are therefore two different factorizing maps from \(A\times_C B\) into \(\widetilde P\). The uniqueness part of the universal property fails.

The universal property excludes both errors:

\[
\boxed{
\text{no missing compatible states and no redundant compatible states}.
}
\]

---

# 8.7 Pullbacks are unique up to unique isomorphism

A pullback may be implemented using different data structures or coordinate systems. The universal property guarantees that all correct implementations are canonically equivalent.

## Theorem 8.1: Uniqueness of pullbacks

Suppose

\[
(P,p_A,p_B)
\]

and

\[
(P',p'_A,p'_B)
\]

are both pullbacks of

\[
A\xrightarrow{f}C\xleftarrow{g}B.
\]

Then there is a unique isomorphism

\[
\alpha:P\to P'
\]

such that

\[
p'_A\circ\alpha=p_A,
\qquad
p'_B\circ\alpha=p_B.
\]

### Proof

Because \(P\) is a compatible cone and \(P'\) is a pullback, there is a unique morphism

\[
\alpha:P\to P'
\]

satisfying

\[
p'_A\circ\alpha=p_A,
\qquad
p'_B\circ\alpha=p_B.
\]

Similarly, because \(P'\) is a compatible cone and \(P\) is a pullback, there is a unique morphism

\[
\beta:P'\to P
\]

satisfying

\[
p_A\circ\beta=p'_A,
\qquad
p_B\circ\beta=p'_B.
\]

Consider \(\beta\circ\alpha:P\to P\). Its projections are

\[
p_A\circ\beta\circ\alpha
=
p'_A\circ\alpha
=
p_A
\]

and

\[
p_B\circ\beta\circ\alpha
=
p'_B\circ\alpha
=
p_B.
\]

The identity map \(1_P:P\to P\) has the same two projection properties. By the uniqueness part of the universal property,

\[
\beta\circ\alpha=1_P.
\]

Similarly,

\[
\alpha\circ\beta=1_{P'}.
\]

Therefore \(\alpha\) and \(\beta\) are inverse isomorphisms.

The morphism \(\alpha\) is unique because any morphism preserving both pullback projections must equal the universal factorization. ∎

This theorem justifies speaking of **the** pullback even though a literal construction may not be unique.

---

# 8.8 Important special cases

## 8.8.1 Products are pullbacks over a terminal object

A **terminal object** \(1\) is an object such that every object \(X\) has exactly one morphism

\[
X\to 1.
\]

In **Set**, any one-element set is terminal.

Given the unique maps

\[
A\to 1,
\qquad
B\to 1,
\]

their pullback is the ordinary product:

\[
A\times_1 B\cong A\times B.
\]

Every pair is compatible because the two interface maps necessarily have the same value.

Thus pullbacks generalize products:

\[
\boxed{\text{product}=\text{pullback with no nontrivial compatibility condition}.}
\]

## 8.8.2 Fibers are pullbacks

Let

\[
f:A\to C
\]

and let \(c\in C\). Treat \(c\) as a function

\[
c:\{*\}\to C.
\]

The pullback

\[
A\times_C\{*\}
\]

is naturally identified with

\[
f^{-1}(c)
=
\{a\in A\mid f(a)=c\}.
\]

This is the **fiber** of \(f\) over \(c\).

In an engineering setting, a fiber might represent:

- all designs with one specified connector type;
- all operating states at a specified pressure;
- all records belonging to one test run;
- all components assigned to one certification class.

## 8.8.3 Inverse images are pullbacks

Let \(S\subseteq C\), with inclusion

\[
i:S\hookrightarrow C.
\]

Then the pullback

\[
A\times_C S
\]

is naturally identified with

\[
f^{-1}(S)
=
\{a\in A\mid f(a)\in S\}.
\]

This gives a categorical description of requirement filtering.

### Example: noise requirement

Let

\[
L:D\to \mathbb R
\]

assign a sound level to each design. Let

\[
R=(-\infty,70]\subseteq\mathbb R
\]

be the acceptable region. The compliant designs form

\[
D\times_{\mathbb R}R
\cong
\{d\in D\mid L(d)\le 70\}.
\]

A requirement check is therefore a pullback against the inclusion of the acceptable region.

---

# 8.9 Pullbacks as database joins

Suppose one table contains fan records and another contains muffler records.

The fan table has a key map

\[
k_F:F\to K,
\]

and the muffler table has a key map

\[
k_M:M\to K.
\]

Here \(K\) might contain interface identifiers such as:

- airflow class;
- connector standard;
- nominal pressure class;
- product-platform identifier.

The pullback

\[
F\times_K M
\]

consists of record pairs with equal keys:

\[
F\times_K M
=
\{(f,m)\mid k_F(f)=k_M(m)\}.
\]

This is a key-based inner join.

## 8.9.1 Example

Fan table:

| Fan | Interface |
|---|---|
| F1 | I-A |
| F2 | I-B |
| F3 | I-B |

Muffler table:

| Muffler | Interface |
|---|---|
| M1 | I-A |
| M2 | I-B |
| M3 | I-C |

The pullback contains:

| Fan | Muffler | Interface |
|---|---|---|
| F1 | M1 | I-A |
| F2 | M2 | I-B |
| F3 | M2 | I-B |

This interpretation is useful, but a physical pullback is usually richer than a catalog join. Matching interface labels does not guarantee that the assembled system has a valid pressure–flow operating point. The interface object must contain enough information to express the actual compatibility condition.

---

# 8.10 Synchronizing experimental data

Pullbacks also arise when data streams must refer to the same event.

Let:

- \(M\) be motor-controller records;
- \(N\) be microphone records;
- \(K\) be a set of synchronization keys.

Suppose

\[
k_M:M\to K,
\qquad
k_N:N\to K.
\]

A key might be

\[
(\text{test-run ID},\text{operating phase},\text{sample number}).
\]

Then

\[
M\times_K N
\]

contains pairs of motor and microphone records corresponding to the same test event.

An element might contain

\[
(\text{RPM}=68{,}000,\ \text{sound level}=76\text{ dBA})
\]

only because the two values share the same test identifier.

Without this pullback, records from different tests could be correlated accidentally.

---

# 8.11 Pullbacks of vector spaces

Pullbacks have a particularly useful form in linear algebra.

Let

\[
F:U\to W,
\qquad
G:V\to W
\]

be linear maps. Define

\[
U\times_W V
=
\{(u,v)\in U\oplus V\mid F(u)=G(v)\}.
\]

This is a vector subspace of \(U\oplus V\).

## Proposition 8.2: Linear pullback as a kernel

Define

\[
H:U\oplus V\to W
\]

by

\[
H(u,v)=F(u)-G(v).
\]

Then

\[
U\times_W V=\ker H.
\]

### Proof

A pair \((u,v)\) belongs to the pullback exactly when

\[
F(u)=G(v).
\]

This is equivalent to

\[
F(u)-G(v)=0,
\]

which is equivalent to

\[
H(u,v)=0.
\]

Therefore the pullback is precisely \(\ker H\). ∎

This yields a direct computational procedure: construct the block matrix

\[
\begin{bmatrix}F&-G\end{bmatrix}
\]

and compute its null space.

## Proposition 8.3: Dimension formula

For finite-dimensional vector spaces,

\[
\dim(U\times_W V)
=
\dim U+\dim V-\dim(\operatorname{im}F+\operatorname{im}G).
\]

### Proof

By Proposition 8.2,

\[
U\times_W V=\ker H,
\qquad
H(u,v)=F(u)-G(v).
\]

The image of \(H\) is

\[
\operatorname{im}H
=
\operatorname{im}F+\operatorname{im}G.
\]

Indeed, every value \(F(u)-G(v)\) belongs to that sum. Conversely, a vector

\[
F(u)+G(v)
\]

can be written as

\[
F(u)-G(-v),
\]

so every vector in the sum belongs to \(\operatorname{im}H\).

By rank–nullity,

\[
\dim\ker H
=
\dim(U\oplus V)-\dim\operatorname{im}H.
\]

Since

\[
\dim(U\oplus V)=\dim U+\dim V,
\]

the result follows. ∎

If

\[
\operatorname{im}F+\operatorname{im}G=W,
\]

then

\[
\dim(U\times_W V)
=
\dim U+\dim V-\dim W.
\]

---

# 8.12 Mechanical and finite-element assembly

Suppose two mechanical substructures have state spaces

\[
X_1,\qquad X_2.
\]

Let

\[
B_1:X_1\to Y,
\qquad
B_2:X_2\to Y
\]

extract their boundary displacement variables.

The kinematically compatible assembled states are

\[
X_1\times_Y X_2
=
\{(x_1,x_2)\mid B_1x_1=B_2x_2\}.
\]

This is exactly the displacement-matching condition used when assembling substructures.

If interface forces must also balance, let

\[
C_1:X_1\to Z,
\qquad
C_2:X_2\to Z
\]

extract force variables. Force balance requires

\[
C_1x_1=-C_2x_2.
\]

Both conditions can be represented using a combined interface object \(Y\oplus Z\):

\[
x_1\longmapsto (B_1x_1,C_1x_1),
\]

\[
x_2\longmapsto (B_2x_2,-C_2x_2).
\]

The pullback consists of states satisfying

\[
B_1x_1=B_2x_2
\]

and

\[
C_1x_1=-C_2x_2.
\]

The sign convention is encoded in the second interface map. Equality in a pullback does not require the raw physical quantities to have identical signs; it requires the morphisms to map them into a common convention.

---

# 8.13 Electrical and energetic ports

Suppose two components are connected through an electrical port.

For component \(A\), define a map to terminal variables:

\[
f:A\to V\times I,
\qquad
f(a)=(v_A,i_A).
\]

For component \(B\), use the opposite current orientation:

\[
g:B\to V\times I,
\qquad
g(b)=(v_B,-i_B).
\]

Then the pullback condition

\[
f(a)=g(b)
\]

means

\[
v_A=v_B,
\qquad
i_A=-i_B.
\]

These are precisely the voltage-continuity and current-balance conditions for an ideal connection.

The same pattern appears in other energy domains:

| Domain | Across variable | Through variable |
|---|---|---|
| Electrical | voltage | current |
| Translational mechanical | velocity | force |
| Rotational mechanical | angular velocity | torque |
| Hydraulic | pressure | volume flow |
| Thermal | temperature | heat flow |

A port-based model usually requires equality of an across variable and sign-adjusted equality of a through variable. Pullbacks provide the compatibility mechanism after the sign and coordinate conventions have been included in the interface maps.

---

# 8.14 The canonical-map criterion in sets

Suppose a commuting square of sets is given:

\[
\begin{array}{ccc}
P & \xrightarrow{p_B} & B\\
{\scriptstyle p_A}\downarrow && \downarrow{\scriptstyle g}\\
A & \xrightarrow{f} & C.
\end{array}
\]

Because the square commutes, there is a canonical function

\[
\chi:P\to A\times_C B
\]

defined by

\[
\chi(x)=(p_A(x),p_B(x)).
\]

## Proposition 8.4

The square is a pullback if and only if \(\chi\) is a bijection.

### Proof

Suppose the square is a pullback. The set \(A\times_C B\), with its standard projections, is also a pullback. By uniqueness of pullbacks, the canonical map \(\chi\) is an isomorphism in **Set**, hence a bijection.

Conversely, suppose \(\chi\) is a bijection. Since \(A\times_C B\) is a pullback and \(P\) is isomorphic to it by an isomorphism preserving the projections, \(P\) also satisfies the universal property. ∎

This gives a practical test:

- **surjectivity** of \(\chi\) means every compatible pair is represented;
- **injectivity** of \(\chi\) means no compatible pair is represented more than once.

---

# 8.15 Joint determination by the pullback projections

## Lemma 8.1

Let \(P\) be a pullback with projections

\[
p_A:P\to A,
\qquad
p_B:P\to B.
\]

For any two morphisms \(r,s:X\to P\), if

\[
p_A\circ r=p_A\circ s
\]

and

\[
p_B\circ r=p_B\circ s,
\]

then

\[
r=s.
\]

### Proof

Both \(r\) and \(s\) are morphisms from \(X\) to the pullback with the same prescribed composites to \(A\) and \(B\). The uniqueness clause in the universal property therefore gives \(r=s\). ∎

The two projections are said to be **jointly monic**. A pullback state is completely determined by its two subsystem descriptions.

---

# 8.16 Pulling back a monomorphism

A morphism

\[
m:B\to C
\]

is a **monomorphism** if, for all morphisms \(r,s:X\to B\),

\[
m\circ r=m\circ s
\quad\Longrightarrow\quad
r=s.
\]

In **Set**, monomorphisms are exactly injective functions.

## Theorem 8.2: Pullbacks preserve monomorphisms

Consider a pullback square

\[
\begin{array}{ccc}
P & \xrightarrow{q} & B\\
{\scriptstyle p}\downarrow && \downarrow{\scriptstyle m}\\
A & \xrightarrow{f} & C.
\end{array}
\]

If \(m\) is a monomorphism, then \(p\) is a monomorphism.

### Proof

Let

\[
r,s:X\to P
\]

satisfy

\[
p\circ r=p\circ s.
\]

By commutativity,

\[
m\circ q\circ r
=
f\circ p\circ r
=
f\circ p\circ s
=
m\circ q\circ s.
\]

Since \(m\) is monic,

\[
q\circ r=q\circ s.
\]

Now \(r\) and \(s\) have equal composites with both pullback projections \(p\) and \(q\). By Lemma 8.1,

\[
r=s.
\]

Therefore \(p\) is monic. ∎

## Engineering interpretation

Suppose \(B\hookrightarrow C\) represents an admissible subset of interface states. Pulling that subset back along \(f:A\to C\) produces the admissible subset of \(A\). The result remains a genuine subobject rather than introducing duplicate states.

---

# 8.17 Pullback pasting

Complex systems are often assembled in stages. The pullback pasting theorem makes such staged constructions compositional.

Consider a commutative diagram

\[
\begin{array}{ccccc}
X & \xrightarrow{a} & Y & \xrightarrow{b} & Z\\
{\scriptstyle u}\downarrow && \downarrow{\scriptstyle v} &&
\downarrow{\scriptstyle w}\\
A & \xrightarrow{c} & B & \xrightarrow{d} & C.
\end{array}
\]

There are two adjacent squares and one outer rectangle.

## Theorem 8.3: Pullback pasting

1. If the left square and the right square are pullbacks, then the outer rectangle is a pullback.
2. If the right square and the outer rectangle are pullbacks, then the left square is a pullback.

### Proof of part 1

Assume both inner squares are pullbacks.

Let \(T\) have morphisms

\[
r:T\to A,
\qquad
s:T\to Z
\]

satisfying

\[
d\circ c\circ r=w\circ s.
\]

Because the right square is a pullback, there is a unique morphism

\[
t:T\to Y
\]

such that

\[
v\circ t=c\circ r,
\qquad
b\circ t=s.
\]

Because the left square is a pullback, there is a unique morphism

\[
h:T\to X
\]

such that

\[
u\circ h=r,
\qquad
a\circ h=t.
\]

Then

\[
b\circ a\circ h=b\circ t=s.
\]

Thus \(h\) factors the compatible pair \((r,s)\) through the outer rectangle.

For uniqueness, suppose \(h':T\to X\) also satisfies

\[
u\circ h'=r,
\qquad
b\circ a\circ h'=s.
\]

The morphisms \(a\circ h'\) and \(t\) have the same composites to \(B\) and \(Z\):

\[
v\circ a\circ h'
=
c\circ u\circ h'
=
c\circ r
=
v\circ t,
\]

and

\[
b\circ a\circ h'=s=b\circ t.
\]

By uniqueness in the right pullback,

\[
a\circ h'=t.
\]

Now \(h'\) and \(h\) have the same composites to \(A\) and \(Y\). By uniqueness in the left pullback,

\[
h'=h.
\]

Therefore the outer rectangle is a pullback. ∎

### Proof of part 2

Assume the right square and the outer rectangle are pullbacks.

Let \(T\) have morphisms

\[
r:T\to A,
\qquad
t:T\to Y
\]

such that

\[
c\circ r=v\circ t.
\]

Then

\[
d\circ c\circ r
=
d\circ v\circ t
=
w\circ b\circ t.
\]

Since the outer rectangle is a pullback, there is a unique morphism

\[
h:T\to X
\]

such that

\[
u\circ h=r,
\qquad
b\circ a\circ h=b\circ t.
\]

We must prove

\[
a\circ h=t.
\]

The two maps \(a\circ h,t:T\to Y\) satisfy

\[
v\circ a\circ h
=
c\circ u\circ h
=
c\circ r
=
v\circ t
\]

and

\[
b\circ a\circ h=b\circ t.
\]

Since the right square is a pullback,

\[
a\circ h=t.
\]

Uniqueness follows from the outer pullback: any other \(h'\) satisfying

\[
u\circ h'=r,
\qquad
a\circ h'=t
\]

also satisfies

\[
b\circ a\circ h'=b\circ t,
\]

and therefore \(h'=h\). ∎

## Engineering interpretation

Suppose:

1. a motor model is connected to a fan model by a shaft interface;
2. the motor–fan assembly is connected to an airflow-path model by a pressure–flow interface.

If each assembly step is modeled by a pullback, the complete interconnection is also a pullback over the composite interface description. This supports modular system construction.

---

# 8.18 Constructing pullbacks from products and equalizers

An **equalizer** of two morphisms

\[
r,s:X\to Y
\]

is a morphism

\[
e:E\to X
\]

such that

\[
r\circ e=s\circ e,
\]

and such that every \(h:Z\to X\) satisfying \(r\circ h=s\circ h\) factors uniquely through \(e\).

In **Set**,

\[
E=\{x\in X\mid r(x)=s(x)\}.
\]

## Theorem 8.4

In any category with binary products and equalizers, every cospan has a pullback.

### Proof

Given

\[
A\xrightarrow{f}C\xleftarrow{g}B,
\]

form the product \(A\times B\), with projections

\[
\pi_A:A\times B\to A,
\qquad
\pi_B:A\times B\to B.
\]

Consider the two morphisms

\[
f\circ\pi_A,
\qquad
g\circ\pi_B
\]

from \(A\times B\) to \(C\).

Let

\[
e:P\to A\times B
\]

be their equalizer. Thus

\[
f\circ\pi_A\circ e
=
g\circ\pi_B\circ e.
\]

Define

\[
p_A=\pi_A\circ e,
\qquad
p_B=\pi_B\circ e.
\]

The square commutes.

Now let \(X\) have compatible morphisms

\[
u:X\to A,
\qquad
v:X\to B
\]

such that

\[
f\circ u=g\circ v.
\]

By the universal property of the product, there is a unique morphism

\[
\langle u,v\rangle:X\to A\times B
\]

such that

\[
\pi_A\circ\langle u,v\rangle=u,
\qquad
\pi_B\circ\langle u,v\rangle=v.
\]

Compatibility gives

\[
f\circ\pi_A\circ\langle u,v\rangle
=
f\circ u
=
g\circ v
=
g\circ\pi_B\circ\langle u,v\rangle.
\]

Therefore \(\langle u,v\rangle\) equalizes the two maps. By the universal property of the equalizer, it factors uniquely through \(e\):

\[
\langle u,v\rangle=e\circ h
\]

for a unique \(h:X\to P\).

It follows that

\[
p_A\circ h
=
\pi_A\circ e\circ h
=
u
\]

and similarly

\[
p_B\circ h=v.
\]

Thus \(P\) is the pullback. ∎

This theorem gives another important interpretation:

\[
\boxed{
\text{pullback}
=
\text{product followed by enforcement of an equality constraint}.
}
\]

In sets,

\[
A\times_C B
=
\operatorname{Eq}
\left(
f\circ\pi_A,\,
g\circ\pi_B
\right).
\]

In vector spaces, the equality constraint becomes a null-space computation.

---

# 8.19 Pullbacks and engineering tolerances

The ordinary pullback uses exact equality:

\[
f(a)=g(b).
\]

Physical compatibility often means agreement within tolerance rather than exact numerical equality. Writing

\[
f(a)\approx g(b)
\]

does not by itself define an ordinary pullback.

A precise model can encode tolerance as a relation.

## 8.19.1 Tolerance relation

Suppose \(C\) is a metric space with distance \(d\). Define

\[
R_\varepsilon
=
\left\{
(c_1,c_2)\in C\times C
\;\middle|\;
d(c_1,c_2)\le\varepsilon
\right\}.
\]

There is an inclusion

\[
i:R_\varepsilon\hookrightarrow C\times C.
\]

Given

\[
f:A\to C,
\qquad
g:B\to C,
\]

define

\[
(f,g):A\times B\to C\times C
\]

by

\[
(f,g)(a,b)=(f(a),g(b)).
\]

Form the pullback

\[
\begin{array}{ccc}
P_\varepsilon & \longrightarrow & R_\varepsilon\\
\downarrow && \downarrow{\scriptstyle i}\\
A\times B & \xrightarrow{(f,g)} & C\times C.
\end{array}
\]

Then

\[
P_\varepsilon
\cong
\left\{
(a,b)\in A\times B
\;\middle|\;
d(f(a),g(b))\le\varepsilon
\right\}.
\]

Exact equality has been replaced by membership in a clearly defined admissibility relation.

## 8.19.2 Engineering example

Suppose a fan outlet has measured diameter \(d_F\), a duct inlet has measured diameter \(d_D\), and assembly permits a difference of at most \(0.2\) mm.

Define

\[
R_{0.2}
=
\{(x,y)\in\mathbb R^2\mid |x-y|\le 0.2\}.
\]

The admissible fan–duct pairs are obtained by pulling this relation back along the two diameter maps.

## 8.19.3 Tolerances are multidimensional

A real interface may include

\[
(\text{diameter},\text{pressure},\text{flow},\text{temperature},\text{protocol}).
\]

Compatibility may involve:

- absolute tolerances;
- relative tolerances;
- interval overlap;
- discrete type equality;
- inequality constraints;
- nonlinear safe-operating regions.

These conditions should be represented explicitly. A scalar distance is not always appropriate.

---

# 8.20 Choosing the interface object

The quality of a pullback model depends strongly on the shared object \(C\).

## 8.20.1 Too little interface information

Suppose fan and muffler designs are mapped only to nominal flow rate:

\[
f:A\to \mathsf Q,
\qquad
g:B\to \mathsf Q.
\]

Two designs may have equal nominal flow but incompatible:

- pressures;
- temperatures;
- port geometries;
- acoustic impedances;
- structural mounting conditions.

The pullback is mathematically correct for the selected interface, but the interface is physically incomplete. It may admit false-positive combinations.

## 8.20.2 Too much interface information

At the opposite extreme, an interface can expose every internal implementation detail. This may prevent interchangeability and make independent subsystem design impossible.

An interface should contain the information required for interconnection, but not irrelevant internal state.

## 8.20.3 Coordinate and unit consistency

Equality is meaningful only after values are mapped into a common representation.

For example, one model may report:

- flow in litres per second;
- another in cubic metres per second.

The interface maps should include the unit conversion before equality is imposed.

Similarly:

- gauge and absolute pressure must be distinguished;
- current directions require a shared sign convention;
- angular position may require a shared reference frame;
- timestamps may require clock-offset correction.

A pullback does not repair inconsistent semantics. It enforces equality of whatever the maps actually report.

---

# 8.21 Pulling subsystem properties onto the assembled system

Suppose

\[
P=A\times_C B
\]

is an assembled-system object.

A property of subsystem \(A\),

\[
r_A:A\to R,
\]

becomes a property of the assembled system by composition:

\[
r_A\circ p_A:P\to R.
\]

Similarly, a property

\[
r_B:B\to S
\]

becomes

\[
r_B\circ p_B:P\to S.
\]

Thus subsystem analyses can be reused on the compatible joint domain.

## Vacuum example

Let

\[
T_F:F\to\mathbb R
\]

be fan winding temperature, and

\[
L_D:D\to\mathbb R
\]

be duct-generated sound level.

On

\[
V=F\times_I D,
\]

the corresponding assembled-system quantities are

\[
T_F\circ\pi_F
\]

and

\[
L_D\circ\pi_D.
\]

A requirement such as

\[
T_F\le T_{\max}
\quad\text{and}\quad
L_{\mathrm{total}}\le L_{\max}
\]

can then be imposed on the joint state space.

This sequence is fundamental:

1. form the compatible state space;
2. evaluate subsystem properties on it;
3. impose system-level constraints.

Evaluating subsystem properties before establishing a consistent operating state can produce invalid comparisons.

---

# 8.22 A practical pullback modeling procedure

For an engineering interconnection, the following procedure is reliable.

## Step 1: Identify the two subsystem behavior spaces

Use behavior spaces rather than merely lists of component part numbers.

A behavior space includes the subsystem’s internal choice together with relevant operating variables.

For the vacuum:

\[
F=\{(a,q,p)\mid p=\Phi_a(q)\},
\]

\[
D=\{(b,q,p)\mid p=\Psi_b(q)\}.
\]

## Step 2: Identify the common interface object

Choose the variables that must agree:

\[
I=\mathsf Q\times\mathsf P.
\]

Include units, coordinate systems, sign conventions, and relevant metadata.

## Step 3: Define the interface maps

\[
s:F\to I,
\qquad
t:D\to I.
\]

These maps should expose the same physical semantics.

## Step 4: Form the compatibility equation

\[
s(x)=t(y).
\]

In different categories this may become:

- a key-matching operation;
- a system of algebraic equations;
- a linear null-space problem;
- a nonlinear root-finding problem;
- a typed software compatibility check.

## Step 5: Construct the pullback

\[
F\times_I D.
\]

## Step 6: Verify completeness and nonredundancy

In **Set**, check that the canonical map to

\[
\{(x,y)\mid s(x)=t(y)\}
\]

is bijective.

## Step 7: Attach analyses to the joint domain

Compose subsystem properties with the pullback projections.

## Step 8: Add tolerance or uncertainty explicitly

Use an admissibility relation, interval-valued interface, stochastic model, or another structure appropriate to the application.

---

# 8.23 Computational forms

## 8.23.1 Finite sets and records

Compute the pullback as a join indexed by the shared interface value.

A hash-table implementation groups elements of \(A\) and \(B\) by their images in \(C\), then forms all pairings within each group.

## 8.23.2 Linear models

For matrices \(F\) and \(G\), compute

\[
\ker
\begin{bmatrix}
F&-G
\end{bmatrix}.
\]

The resulting basis parameterizes every compatible pair.

## 8.23.3 Nonlinear models

For differentiable maps

\[
f:A\to C,
\qquad
g:B\to C,
\]

solve

\[
r(a,b)=f(a)-g(b)=0
\]

in a common coordinate representation.

The residual Jacobian is

\[
Dr(a,b)
=
\begin{bmatrix}
Df(a)&-Dg(b)
\end{bmatrix}.
\]

Standard nonlinear equation solvers, continuation methods, or constrained optimizers can then be used.

## 8.23.4 Databases

Use a relational join on the shared key. When duplicates, null values, or bag semantics matter, the exact database category must be chosen carefully; ordinary sets model distinct records rather than duplicate-counted rows.

## 8.23.5 Software interfaces

If \(C\) is a type or protocol description, the pullback represents implementations whose exposed interface types agree. More refined models may include version negotiation, capabilities, or behavioral contracts rather than only type names.

---

# 8.24 Common modeling errors

## Error 1: Confusing a commuting square with a pullback

A commuting square shows compatibility of represented states. It does not prove that every compatible state is represented exactly once.

## Error 2: Using component catalogs instead of behavior spaces

A fan part number does not determine one pressure and flow independently of the attached system. The operating point is jointly determined.

## Error 3: Omitting interface variables

Matching flow while ignoring pressure or temperature may produce mathematically valid but physically inadequate compatibility.

## Error 4: Comparing different units or conventions

Equality between values in inconsistent units, frames, or sign conventions is meaningless.

## Error 5: Treating approximate equality as exact equality

Tolerance must be encoded as a relation or admissible region.

## Error 6: Interpreting arrows as causal arrows

A morphism \(A\to C\) need not mean that \(A\) physically causes \(C\). It may only extract, classify, or report information.

## Error 7: Adding logarithmic measurements directly

When sound levels are expressed in decibels, the underlying power or pressure quantities must be combined according to the relevant acoustic model.

## Error 8: Assuming pullbacks exist in every category

They exist in **Set**, **Vect**, and many standard engineering categories, but an arbitrary category need not have all pullbacks.

---

# 8.25 Chapter summary

A pullback begins with a cospan

\[
A\xrightarrow{f}C\xleftarrow{g}B.
\]

It constructs an object

\[
A\times_C B
\]

whose states consist of compatible \(A\)- and \(B\)-descriptions.

In sets,

\[
A\times_C B
=
\{(a,b)\mid f(a)=g(b)\}.
\]

Its universal property says that every compatible pair of descriptions factors uniquely through the pullback.

The main interpretations are:

\[
\boxed{
\begin{aligned}
\text{pullback}
&=\text{product with an agreement constraint},\\
&=\text{compatible subsystem interconnection},\\
&=\text{database join over a shared key},\\
&=\text{inverse image of a requirement region},\\
&=\text{fiber over a specified interface value},\\
&=\ker[F\ -G]\text{ in linear algebra}.
\end{aligned}
}
\]

For vacuum-noise engineering, the central pullback is not merely a list of compatible part numbers. It is the set of fan-side and flow-path states that share one pressure–flow operating point. Acoustic, thermal, and structural predictions should then be evaluated on that common state space.

---

# 8.26 Exercises

Exercises marked \(^{*}\) require a proof. Exercises marked \(^{\dagger}\) involve modeling choices for which several answers may be defensible.

## Conceptual exercises

### Exercise 8.1: Product and pullback

Let

\[
A=\{M_1,M_2,M_3\},
\qquad
B=\{S_1,S_2\},
\qquad
C=\{L,H\}.
\]

Suppose

\[
f(M_1)=L,\qquad f(M_2)=H,\qquad f(M_3)=H
\]

and

\[
g(S_1)=L,\qquad g(S_2)=H.
\]

1. List the elements of \(A\times B\).
2. List the elements of \(A\times_C B\).
3. Explain the engineering difference between the two sets.

### Exercise 8.2: Universal property in words

For the fan–duct pullback

\[
F\times_I D,
\]

translate each part of the universal property into engineering language:

1. the commutativity equation;
2. the existence of the factorizing map;
3. the uniqueness of the factorizing map.

### Exercise 8.3: Commuting but not universal

Let

\[
A=B=C=\{*\}
\]

and let all maps between them be the unique possible functions. Let

\[
P=\{0,1\}
\]

with the unique maps \(P\to A\) and \(P\to B\).

1. Show that the square commutes.
2. Show that it is not a pullback.
3. Identify which part of the universal property fails.

### Exercise 8.4\(^{*}\): Symmetry

Prove that there is a canonical isomorphism

\[
A\times_C B\cong B\times_C A.
\]

Show that in **Set** it is given by

\[
(a,b)\longmapsto(b,a).
\]

### Exercise 8.5\(^{*}\): Pullback over an identity

Given \(f:A\to C\), prove

\[
A\times_C C\cong A
\]

when the second map is \(1_C:C\to C\).

---

## Fibers and requirements

### Exercise 8.6: A fiber

Let

\[
f:\mathbb R^2\to\mathbb R,
\qquad
f(x,y)=x+y.
\]

Describe the pullback of \(f\) along the point \(3:\{*\}\to\mathbb R\). Give a one-parameter description of the resulting set.

### Exercise 8.7: Noise requirement

Let

\[
D=\{d_1,d_2,d_3,d_4\}
\]

with measured sound levels

\[
L(d_1)=68,\quad
L(d_2)=71,\quad
L(d_3)=74,\quad
L(d_4)=69.
\]

Let the acceptable region be

\[
R=(-\infty,70].
\]

Compute

\[
D\times_{\mathbb R}R.
\]

### Exercise 8.8\(^{*}\): Inverse images

Let \(i:S\hookrightarrow C\) be an inclusion and \(f:A\to C\). Prove directly from the universal property that

\[
A\times_C S
\]

is isomorphic to the inverse-image subset

\[
f^{-1}(S).
\]

---

## Vacuum operating points

### Exercise 8.9: Fan and path intersection

A fan has characteristic

\[
p_f(q)=20-0.10q^2.
\]

A flow path has pressure loss

\[
p_d(q)=2+0.10q^2.
\]

Assume \(q\ge 0\).

1. Find the compatible flow \(q\).
2. Find the common pressure \(p\).
3. Describe the corresponding pullback element.

### Exercise 8.10: Adding a restrictive filter

Replace the path model in Exercise 8.9 by

\[
p_d'(q)=2+0.15q^2.
\]

1. Find the new operating point.
2. Compare the new flow and pressure with the original values.
3. Explain why a noise measurement from the original operating point cannot automatically be reused.

### Exercise 8.11\(^{\dagger}\): Selecting the interface

A vacuum model uses only flow rate as its interface variable. List at least four situations in which equal flow rate would not be sufficient to guarantee that two subsystem states are compatible. Propose a richer interface object.

### Exercise 8.12\(^{\dagger}\): Acoustic interface

Construct an interface object suitable for connecting:

1. a motor–impeller acoustic source model;
2. an exhaust-muffler acoustic propagation model.

State which quantities must agree and which quantities should remain internal to each subsystem.

---

## Data integration

### Exercise 8.13: Telemetry pullback

Motor-controller records:

| Record | Run | Phase | RPM |
|---|---|---|---:|
| \(m_1\) | R7 | steady | 62,000 |
| \(m_2\) | R8 | steady | 71,000 |
| \(m_3\) | R7 | startup | 40,000 |

Microphone records:

| Record | Run | Phase | Level |
|---|---|---|---:|
| \(n_1\) | R7 | steady | 73 dBA |
| \(n_2\) | R7 | startup | 81 dBA |
| \(n_3\) | R9 | steady | 76 dBA |

Let the key be

\[
K=\text{Run}\times\text{Phase}.
\]

Compute the pullback of the two record sets over \(K\).

### Exercise 8.14: Duplicate representations

Suppose every synchronized record pair is stored twice, once with label “primary” and once with label “backup,” while both projections ignore the label.

Explain why the resulting data structure is not itself the pullback, even though its projection square commutes.

### Exercise 8.15: Approximate timestamp matching

Motor samples occur at times

\[
1.00,\quad 1.10,\quad 1.25
\]

seconds. Microphone samples occur at

\[
0.97,\quad 1.06,\quad 1.29
\]

seconds.

Define two timestamps to be compatible when they differ by no more than \(0.05\) seconds. List all compatible sample pairs.

Express the construction using a tolerance relation

\[
R_{0.05}\subseteq\mathbb R\times\mathbb R.
\]

---

## Linear pullbacks

### Exercise 8.16: Computing a basis

Let

\[
F:\mathbb R^3\to\mathbb R^2,
\qquad
F(x,y,z)=(x+y,z),
\]

and

\[
G:\mathbb R^2\to\mathbb R^2,
\qquad
G(u,v)=(u,u+v).
\]

Find a basis for

\[
\mathbb R^3\times_{\mathbb R^2}\mathbb R^2.
\]

Write elements in the form

\[
(x,y,z;u,v).
\]

### Exercise 8.17\(^{*}\): Dimension formula

Prove directly using rank–nullity that

\[
\dim(U\times_W V)
=
\dim U+\dim V-\dim(\operatorname{im}F+\operatorname{im}G).
\]

### Exercise 8.18: Mechanical boundary compatibility

Let

\[
B_1:\mathbb R^2\to\mathbb R,
\qquad
B_1(x_1,x_2)=x_1+2x_2,
\]

and

\[
B_2:\mathbb R^2\to\mathbb R,
\qquad
B_2(y_1,y_2)=3y_1-y_2.
\]

Find a basis for

\[
\mathbb R^2\times_{\mathbb R}\mathbb R^2.
\]

Interpret the defining equation as a boundary compatibility condition.

### Exercise 8.19: Electrical connection

Component \(A\) reports

\[
(v_A,i_A),
\]

and component \(B\) reports

\[
(v_B,i_B).
\]

Define interface maps whose pullback imposes

\[
v_A=v_B,
\qquad
i_A+i_B=0.
\]

Explain the role of the sign convention.

---

## Proof exercises

### Exercise 8.20\(^{*}\): Joint monicity

Prove that the two projections from a pullback are jointly monic.

### Exercise 8.21\(^{*}\): Pullback of a monomorphism

Prove Theorem 8.2 without using elementwise reasoning.

Then specialize the result to sets and explain it using injective functions.

### Exercise 8.22\(^{*}\): Canonical-map criterion

Let a square of sets commute. Prove directly, without using uniqueness of pullbacks up to isomorphism, that the square is a pullback if and only if

\[
x\longmapsto(p_A(x),p_B(x))
\]

is a bijection onto

\[
A\times_C B.
\]

### Exercise 8.23\(^{*}\): Product as pullback

Let \(1\) be terminal. Prove directly from the universal properties that

\[
A\times_1 B
\]

is a categorical product of \(A\) and \(B\).

### Exercise 8.24\(^{*}\): Pullback from an equalizer

Assume a category has binary products and equalizers. Reconstruct the proof that it has pullbacks, explicitly identifying all universal morphisms.

### Exercise 8.25\(^{*}\): Pasting

Prove both parts of the pullback pasting theorem. Mark exactly where each uniqueness property is used.

---

## Engineering modeling exercises

### Exercise 8.26\(^{\dagger}\): Battery and charger

Develop a pullback model for connecting a battery pack and charger. Your interface should account for at least:

- voltage;
- current;
- communication protocol;
- temperature or thermal limits.

Distinguish:

1. catalog compatibility;
2. instantaneous operating-state compatibility.

### Exercise 8.27\(^{\dagger}\): Thermal interface

Two subsystems are joined through a thermal contact. Construct interface maps that express:

- continuity of interface temperature;
- conservation of heat flow.

Explain how the sign convention should be encoded.

### Exercise 8.28\(^{\dagger}\): Requirements and uncertainty

A vacuum design has a predicted sound level represented by an interval

\[
[L_{\min},L_{\max}]
\]

rather than a single number. Formulate two different acceptance rules:

1. the complete interval must be below \(70\) dBA;
2. the interval only needs to overlap the region below \(70\) dBA.

Explain how these produce different admissibility relations.

### Exercise 8.29\(^{\dagger}\): Interface audit

Choose an engineered system composed of at least three subsystems. For every adjacent pair:

1. identify the cospan;
2. define the shared interface object;
3. state the pullback condition;
4. identify one variable whose omission would make the model unreliable;
5. explain how pullback pasting supports the full assembly.

---

# 8.27 Selected solutions and hints

## Solution to Exercise 8.1

The product is

\[
\begin{aligned}
A\times B=\{&
(M_1,S_1),(M_1,S_2),\\
&(M_2,S_1),(M_2,S_2),\\
&(M_3,S_1),(M_3,S_2)\}.
\end{aligned}
\]

Matching interface classes gives

\[
A\times_C B
=
\{
(M_1,S_1),
(M_2,S_2),
(M_3,S_2)
\}.
\]

The product lists all possible pairings. The pullback lists only pairings that agree on the interface classification.

---

## Solution to Exercise 8.3

The square commutes because every composite is the unique map to the one-element set.

It is not a pullback. Take \(X=\{*\}\) with the unique maps to \(A\) and \(B\). There are two possible factorizing maps

\[
X\to P:
\qquad
*\mapsto 0
\]

and

\[
*\mapsto 1.
\]

The uniqueness clause fails.

---

## Hint for Exercise 8.4

Use the universal property to construct

\[
\sigma:A\times_C B\to B\times_C A
\]

from the two projections in reversed order. Construct the reverse map similarly. Use uniqueness to prove that the composites are identities.

---

## Solution to Exercise 8.6

The pullback is

\[
\{(x,y)\in\mathbb R^2\mid x+y=3\}.
\]

A parameterization is

\[
(x,y)=(t,3-t),
\qquad
t\in\mathbb R.
\]

It is the fiber of \(f\) over \(3\).

---

## Solution to Exercise 8.7

The acceptable designs satisfy

\[
L(d)\le 70.
\]

Therefore

\[
D\times_{\mathbb R}R
\cong
\{d_1,d_4\}.
\]

Strictly, the pullback contains pairs

\[
(d_1,68),
\qquad
(d_4,69),
\]

but because \(R\hookrightarrow\mathbb R\) is an inclusion, it is naturally identified with the subset \(\{d_1,d_4\}\).

---

## Solution to Exercise 8.9

Compatibility requires

\[
20-0.10q^2=2+0.10q^2.
\]

Thus

\[
18=0.20q^2,
\qquad
q^2=90,
\]

so

\[
q=3\sqrt{10}\approx 9.49.
\]

The common pressure is

\[
p=2+0.10(90)=11.
\]

The pullback state may be represented as

\[
(\text{fan state at }q=3\sqrt{10},p=11,
\ \text{path state at }q=3\sqrt{10},p=11).
\]

After identifying the shared variables, it can be written simply as

\[
(\text{fan design},\text{path design},3\sqrt{10},11).
\]

---

## Solution to Exercise 8.10

The new equation is

\[
20-0.10q^2=2+0.15q^2.
\]

Therefore

\[
18=0.25q^2,
\qquad
q^2=72,
\]

and

\[
q=6\sqrt2\approx 8.49.
\]

The pressure is

\[
p=2+0.15(72)=12.8.
\]

Compared with the original system:

- flow decreases from approximately \(9.49\) to \(8.49\);
- pressure increases from \(11\) to \(12.8\).

The acoustic source spectrum, turbulent self-noise, motor loading, and attenuation may all depend on \(q\) and \(p\). A measurement at the original operating point is therefore not automatically a prediction for the modified system.

---

## Solution to Exercise 8.13

The shared key values are:

\[
k_M(m_1)=(\mathrm{R7},\mathrm{steady}),
\]

\[
k_M(m_2)=(\mathrm{R8},\mathrm{steady}),
\]

\[
k_M(m_3)=(\mathrm{R7},\mathrm{startup}),
\]

and

\[
k_N(n_1)=(\mathrm{R7},\mathrm{steady}),
\]

\[
k_N(n_2)=(\mathrm{R7},\mathrm{startup}),
\]

\[
k_N(n_3)=(\mathrm{R9},\mathrm{steady}).
\]

Hence

\[
M\times_K N
=
\{
(m_1,n_1),
(m_3,n_2)
\}.
\]

The \(m_2\) and \(n_3\) records have no matching partner.

---

## Solution to Exercise 8.15

The compatibility condition is

\[
|t_M-t_N|\le 0.05.
\]

The compatible pairs are

\[
(1.00,0.97),
\qquad
(1.10,1.06),
\qquad
(1.25,1.29).
\]

Define

\[
R_{0.05}
=
\{(s,t)\in\mathbb R^2\mid |s-t|\le 0.05\}.
\]

The approximate synchronization set is the pullback of

\[
R_{0.05}\hookrightarrow\mathbb R^2
\]

along the map that sends a motor–microphone sample pair to its pair of timestamps.

---

## Solution to Exercise 8.16

The pullback equations are

\[
x+y=u
\]

and

\[
z=u+v.
\]

Choose \(x,y,v\) freely. Then

\[
u=x+y
\]

and

\[
z=x+y+v.
\]

Thus

\[
(x,y,z;u,v)
=
x(1,0,1;1,0)
+
y(0,1,1;1,0)
+
v(0,0,1;0,1).
\]

A basis is

\[
\left\{
(1,0,1;1,0),
(0,1,1;1,0),
(0,0,1;0,1)
\right\}.
\]

The pullback has dimension \(3\).

---

## Solution to Exercise 8.18

Compatibility requires

\[
x_1+2x_2=3y_1-y_2.
\]

Solve for \(x_1\):

\[
x_1=3y_1-y_2-2x_2.
\]

Taking \(x_2,y_1,y_2\) as free variables gives

\[
(x_1,x_2;y_1,y_2)
=
x_2(-2,1;0,0)
+
y_1(3,0;1,0)
+
y_2(-1,0;0,1).
\]

A basis is

\[
\left\{
(-2,1;0,0),
(3,0;1,0),
(-1,0;0,1)
\right\}.
\]

The equation states that the displacement extracted from the first substructure equals the displacement extracted from the second.

---

## Solution to Exercise 8.19

Define

\[
f(a)=(v_A,i_A)
\]

and

\[
g(b)=(v_B,-i_B).
\]

Then

\[
f(a)=g(b)
\]

is equivalent to

\[
v_A=v_B
\]

and

\[
i_A=-i_B,
\]

or

\[
i_A+i_B=0.
\]

The negative sign converts the two component-local current orientations into one common port convention.

---

## Hint for Exercise 8.22

For the forward direction, use:

- surjectivity to construct a factorization for every compatible pair;
- injectivity to prove that the factorization is unique.

For the reverse direction:

- use the universal property with a one-element set to prove surjectivity;
- use the uniqueness clause to prove injectivity.

---

## Model answer to Exercise 8.26

Let \(B\) be the battery operating-state space and \(C\) the charger operating-state space. A possible common interface object is

\[
I=
V\times I_{\mathrm{current}}
\times P_{\mathrm{protocol}}
\times T_{\mathrm{class}}.
\]

The battery-side map might report

\[
(\text{accepted terminal voltage},
\text{accepted current},
\text{active protocol state},
\text{permitted temperature class}),
\]

while the charger-side map reports

\[
(\text{delivered terminal voltage},
\text{delivered current},
\text{active protocol state},
\text{measured temperature class}).
\]

The pullback contains charging sessions in which all four interface descriptions agree.

Catalog compatibility could use coarser objects such as:

\[
(\text{nominal voltage class},\text{connector},\text{protocol version}).
\]

Instantaneous operating compatibility requires actual values and states, including current limits, state of charge, cell temperature, and active control mode. A catalog-level pullback does not establish that every instantaneous charging state is safe.

---

## Model answer to Exercise 8.11

Equal flow rate is insufficient when the states differ in:

- static or total pressure;
- air temperature;
- port geometry;
- humidity or particle loading;
- rotational speed;
- acoustic impedance;
- flow profile or swirl;
- structural mounting condition.

A richer interface might be

\[
I=
\mathsf Q
\times\mathsf P
\times\mathsf T
\times\mathsf G
\times\mathsf Z_A,
\]

where:

- \(\mathsf Q\) is flow rate;
- \(\mathsf P\) is pressure;
- \(\mathsf T\) is temperature;
- \(\mathsf G\) describes geometry;
- \(\mathsf Z_A\) describes acoustic impedance or another reduced acoustic boundary model.

The appropriate interface should include only variables needed for the intended prediction. A model for basic airflow may use fewer variables than a model for broadband acoustic propagation.

