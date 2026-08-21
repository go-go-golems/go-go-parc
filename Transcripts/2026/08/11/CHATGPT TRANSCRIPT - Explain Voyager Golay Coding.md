# Explain Voyager Golay Coding

- URL: https://chatgpt.com/c/6a7b1a64-d1b8-83ea-8f93-985b83ec2f2b
- Created: 2026-08-11T12:50:01.719Z

---

> how was the geometry of stacking spheresin twenty  four dimensions used in the data-stransmission protocols for the voyager 1 and 2 probes ?

The connection is real, but slightly indirect: Voyager did not literally transmit coordinates of 24-dimensional spheres. The relevant bridge is the **binary Golay code**, whose structure is closely related to the exceptional 24-dimensional Leech lattice. I’ll separate the communications engineering from the later geometric interpretation.

```json
{"system2_search_query":[{"q":"site:ntrs.nasa.gov Voyager Golay code telemetry 24 12 8 Voyager 1 2"},{"q":"site:jpl.nasa.gov Voyager Golay code 24 telemetry coding"},{"q":"site:ntrs.nasa.gov Voyager error correction Golay Reed Solomon convolutional code"},{"q":"site:descanso.jpl.nasa.gov Voyager telecommunications coding Golay"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Clarifying the connection**

I’m separating two related ideas: the extended Golay code supports error correction by mapping messages to distant 24-bit codewords, while the Leech lattice gives optimal sphere packing in 24 dimensions. Voyager used the former, not literal stacked spheres, transmitting protected scientific data.

**Clarified the connection**

</details>

```json
{"open":[{"ref_id":"turn679599search52"},{"ref_id":"turn679599search47"},{"ref_id":"turn679599search17"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Tracing coding history**

I’m distinguishing the geometric analogy from Voyager’s actual communications systems. The Golay code predates the Leech lattice, and the lattice was later built using related code structure; Voyager relied on error-correcting codes rather than physical sphere packing.

**Traced coding history**

**Searched 6 websites**

</details>

The important point is that **Voyager did not directly use the 24-dimensional Leech-lattice sphere packing as a transmission protocol**. It used the closely related **extended binary Golay error-correcting code**. The remarkable 24-dimensional sphere packing and the Voyager code are two manifestations of much of the same mathematics.

### 1. Twenty-four bits become a 24-dimensional space

For Voyager data protected by the Golay code, **12 information bits were encoded as a 24-bit codeword**: the extended binary Golay code is a $[24,12,8]$ code. JPL documentation describes the $(24,12)$ Golay code in its deep-space communications work, and Voyager used Golay block coding during its Jupiter/Saturn phase. The resulting 100% redundancy meant one extra transmitted bit for every information bit. citeturn675476search8turn676448view0

A 24-bit string

$$
(x_1,x_2,\ldots,x_{24}), \qquad x_i\in\{0,1\},
$$

can be regarded as a **point in a 24-dimensional binary space**. There are $2^{24}$ possible points, but the Golay encoder permits only

$$
2^{12}=4096
$$

of them as valid codewords. Those 4096 points are arranged extraordinarily far apart: any two valid codewords differ in **at least eight bit positions**. citeturn870692search3turn870692search6

That is where the sphere-packing idea enters.

### 2. The "spheres" are error neighborhoods

Instead of ordinary distance, use **Hamming distance**: count how many coordinates differ.

Around every valid Golay codeword, imagine a "sphere" containing every 24-bit string differing from it in at most three positions:

$$
d_H(r,c)\leq3.
$$

Because valid codewords are at least 8 positions apart, these radius-3 spheres **cannot overlap**.

For example, suppose codewords $A$ and $B$ are 8 bits apart. If transmission noise changes three bits of $A$, producing $R$,

$$
d(A,R)=3.
$$

Then the closest $B$ could possibly be is

$$
d(B,R)\geq8-3=5.
$$

So the receiver knows unambiguously that $A$, not $B$, was sent.

Consequently, the extended Golay code can **correct any three bit errors in a 24-bit block**. Its minimum distance of 8 also means errors involving as many as seven changed bits cannot turn one legitimate codeword directly into another legitimate one, although beyond three errors unique correction is no longer guaranteed. citeturn870692search9turn675476search0

So this is literally a packing problem—except the objects being packed are **Hamming spheres in binary space**, rather than round balls in ordinary Euclidean space.

### 3. Where the famous Leech lattice appears

This is the striking mathematical connection.

The extended Golay code can be used, together with additional parity and shifting conditions, to construct the **Leech lattice**, usually written

$$
\Lambda_{24},
$$

which lives in ordinary Euclidean $\mathbb{R}^{24}$. John Leech's construction effectively "lifts" the binary Golay structure into a lattice of real/integer coordinates. citeturn870692search5turn870692search2

If equal 24-dimensional spheres are centered at the Leech-lattice points, they give the exceptionally dense Leech packing. It is now known mathematically that this is the densest possible sphere packing in 24 dimensions. citeturn870692academia80

So there are **two related packing pictures**:

$$
\boxed{\text{Golay code}}
$$

$$
\text{4096 points in }\{0,1\}^{24}
\quad\longrightarrow\quad
\text{pack Hamming-error spheres}
$$

and

$$
\boxed{\text{Leech lattice}}
$$

$$
\text{lattice points in }\mathbb R^{24}
\quad\longrightarrow\quad
\text{pack ordinary 24-D spheres}.
$$

The extraordinary symmetry of the Golay code is part of what makes the Leech lattice extraordinary. But **Voyager's computers were doing binary coding operations, not calculating a Leech-lattice sphere packing**.

### 4. What actually happened to a Voyager transmission

For a stream protected by Golay coding, a simplified picture is

$$
\boxed{12\ {\rm data\ bits}}
\rightarrow
\boxed{24\ {\rm Golay\ bits}}
\rightarrow
\boxed{\text{convolutional encoder}}
\rightarrow
\text{radio link}
$$

and on Earth,

$$
\text{radio receiver}
\rightarrow
\boxed{\text{Viterbi convolutional decoder}}
\rightarrow
\boxed{\text{Golay decoder}}
\rightarrow
\boxed{12\ {\rm recovered\ data\ bits}}.
$$

Voyager combined Golay block coding with a **rate-$1/2$, constraint-length-7 convolutional code**. NASA documentation describes the ground side as undoing the convolutional coding with maximum-likelihood/Viterbi decoding and then performing block decoding. citeturn351943view1turn676448view2

This concatenation was valuable because the radio signal from deep space is extremely weak. The convolutional code dealt effectively with the noisy continuous radio channel, while the Golay block structure supplied an additional layer of powerful error correction.

### 5. And Voyager 2 later moved beyond Golay

The Golay arrangement was particularly important for the Jupiter and Saturn phase. For the much more distant Uranus and Neptune encounters, Voyager 2 made use of **Reed–Solomon coding**, which gave substantially less redundancy for the required reliability. JPL reports that Golay coding at Jupiter/Saturn imposed roughly 100% overhead, whereas the later Reed–Solomon scheme imposed about 20% and greatly reduced the output error rate. citeturn676448view1

So it would be misleading to say that "Voyager communicated using the 24-dimensional Leech lattice." A more accurate statement is:

> **Voyager used the $[24,12,8]$ Golay error-correcting code. The same exceptional mathematical structure underlying that code is intimately connected with the Leech lattice and its optimal packing of spheres in 24-dimensional Euclidean space.**

Historically, the direction is also interesting: **the Golay code came first; the Leech lattice was subsequently constructed using that code's structure.** Thus the sphere packing did not inspire Voyager's onboard protocol so much as reveal how geometrically exceptional the code Voyager was using really is. citeturn870692search5turn870692search6

