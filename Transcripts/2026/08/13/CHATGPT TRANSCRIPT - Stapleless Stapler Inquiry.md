# Stapleless Stapler Inquiry

- URL: https://chatgpt.com/c/6a7e1b7d-8ee0-83ea-a949-4ab5f80da114
- Created: 2026-08-13T19:31:28.320Z

---

> What is that thing called like a stapler but it just indents / embossed the paper so it holds together?

You’re probably thinking of a **stapleless stapler** (also called a **staple-free stapler** or sometimes a **paper clincher**).

It presses/cuts and folds a tiny section of the paper into itself so the sheets stay together—no metal staple needed.

If you mean one that **only crimps/embosses the corner without cutting it**, that’s usually called a **paper crimper** or **paper embosser**.


---

> How can I mill one on my cnc? What does it look like

If you mean the **stapleless paper fastener**, the key is the punch-and-die geometry—not just squeezing the paper. I’m checking the common mechanisms so I can describe a CNC-friendly version accurately.

```json
{"system1_search_query":[{"q":"stapleless stapler mechanism punch die paper cut fold patent"},{"q":"paper clincher stapleless fastener embossed paper mechanism"}],"image_query":[{"q":"stapleless stapler mechanism punch die close up"},{"q":"paper clincher stapleless stapler mechanism"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Searched 16 websites**

**Designing serrated jaws**

I’m treating this as a no-hole crimp made by complementary serrated dies. I’d start with 8–10 parallel ribs, roughly 0.6–0.8 mm pitch, using clearance based on the paper stack—not fixed factory dimensions.

**Designed serrated jaws**

</details>

```json
{"image_query":[{"q":"Kokuyo Harinacs Press teeth die inside close up metal jaws"},{"q":"Harinacs Press disassembled crimp teeth stapleless stapler"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Searching the web**

**Refining the die geometry**

I’m modeling the mechanism as two aligned rows of intermeshing triangular teeth that fold paper into corrugated pleats. I’d prototype in aluminum, then use hardened tool steel if repeated service demands it.

**Refined the die geometry**

</details>

iturn364017image1

Yes — **this is the type you were describing**. It’s essentially a tiny **serrated crimping press**. The Kokuyo Harinacs Press uses metal teeth to deform the sheets together without cutting a hole; Kokuyo rates it for up to five sheets. citeturn989911search2turn364017image1

For a CNC version, I would **not start by machining the whole stapler**. Machine a matched pair of little dies, test them in an arbor press or toggle clamp, then build the lever housing around them.

### What the dies look like

In cross-section, think of two rows of intermeshing teeth:

```text
UPPER DIE
       /\    /\    /\    /\    /\
 _____/  \__/  \__/  \__/  \__/  \_____
                 ↓ force

 =============== PAPER =================

 _____    ____    ____    ____    ______
      \__/    \__/    \__/    \__/
LOWER DIE
```

The upper peaks go into the lower valleys. They **don't shear the paper**; they corrugate/crush the fibers into a row of tight little pleats. The commercial Harinacs leaves a crimp only about **10 mm wide**. citeturn364017image1

A reasonable **first prototype**, rather than factory dimensions, would be:

- Active crimp area: **10 × 3–4 mm**
- 9–10 teeth
- Tooth pitch: **~1.0 mm**
- Tooth height: **0.3–0.5 mm**
- Included tooth angle: **60–90°**
- Tip radius: **~0.1–0.2 mm** — don't make them knife sharp
- Upper and lower teeth offset by **½ pitch**
- Adjustable mechanical stop so the dies **cannot bottom hard against each other**

For example:

```text
10 mm total
<-------------------------------->

 /\  /\  /\  /\  /\  /\  /\  /\  /\
/  \/  \/  \/  \/  \/  \/  \/  \/  \

pitch ≈ 1.0 mm
height ≈ 0.4 mm
```

### How I'd mill it

Use two small removable die inserts, maybe **15 × 15 × 5 mm**. For a proof of concept, 6061 aluminum should let you experiment cheaply; once the geometry works, make the dies from tool steel or another harder material.

On a 3-axis mill, a **60° or 90° engraving/V cutter** makes this particularly easy. Cut parallel grooves across the upper die. Make the lower die with the same pitch, but shift the pattern by half a tooth so the ridges interleave.

The important detail is alignment. Put the dies in a carrier with **two dowel pins or linear guides** so one jaw can't slide sideways as it closes:

```text
        LONG LEVER
              \
               \________________
                                O  pivot
                                |
                       ┌────────┴────────┐
 guide pin ─────────── │   UPPER DIE     │
                       │ /\/\/\/\/\/\/\  │
                       └─────────────────┘
                            PAPER
                       ┌─────────────────┐
                       │ \/\/\/\/\/\/\/  │
                       │   LOWER DIE     │
                       └─────────────────┘
```

Add a screw-adjustable hard stop and sneak up on the closing depth. That's important: **too shallow = it doesn't hold; too deep/sharp = you've made a paper perforator.**

The commercial version uses substantial leverage to force its metal teeth into the paper, which is why the handheld body looks oversized relative to the tiny ~10 mm crimp. citeturn364017image1

If you're machining this on a typical hobby CNC, I can also give you a **dimensioned 2D die profile you can reproduce directly in Fusion 360**, including tooth pitch, depth, offsets, and an adjustable press-body design.

