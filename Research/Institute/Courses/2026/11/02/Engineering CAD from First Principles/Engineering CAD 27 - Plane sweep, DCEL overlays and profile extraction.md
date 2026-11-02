---
title: "Engineering CAD from First Principles — Chapter 27. Plane sweep, DCEL overlays and profile extraction"
aliases:
  - "Chapter 27. Plane sweep, DCEL overlays and profile extraction"
tags:
  - course
  - cad
  - textbook
  - jigcad
status: active
type: course
created: 2026-11-02
course: "[[Course - Engineering CAD from First Principles]]"
---

# Chapter 27. Plane sweep, DCEL overlays and profile extraction

[[Engineering CAD 26 - Predicates, constructions and symbolic perturbation|← Chapter 26. Predicates, constructions and symbolic perturbation]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 28 - Delaunay triangulation and quality refinement|Chapter 28. Delaunay triangulation and quality refinement →]]

Mathematics in this chapter: [[Mathematics - Computational Geometry|Computational Geometry]] (see [[Mathematics]]).

A sketch containing intersecting curves is not yet a collection of faces. The intersections must be found, edges split consistently, directed uses connected, and boundary cycles grouped into regions with holes. This chapter develops that pipeline for line segments and explains why it is the discrete core of both profile extraction and planar Boolean operations.

**Source basis.** de Berg et al. chapter 2 develops segment intersection, the DCEL, map overlay, and polygon Booleans in that order. We retain that dependency structure. The lab uses small, deliberately simpler computations to expose the intermediate states; it is not an implementation of the book's asymptotically efficient sweep. [[Engineering CAD B - Source Library#^ref-deberg-upload|de Berg]].

## 27.1 State the output before choosing an algorithm

Given $n$ closed segments, what counts as an intersection? A proper crossing, a shared endpoint, an endpoint on another segment, and a collinear overlap are different cases. A routine returning only an optional point cannot represent an overlap interval.

A useful result type is

```text
SegmentIntersection = Empty | Point(position, endpoint_flags)
                    | Overlap(parameter_interval_a, parameter_interval_b)
```

For an arrangement, the goal is not merely a list of intersection points. It is a subdivision in which every intersection is represented by an appropriate vertex and every edge interior is free of unresolved intersections. A shared crossing of three segments is one geometric event with three incident segments, not three unrelated pair events that happen to have nearly equal coordinates.

The brute-force strategy examines $n(n-1)/2$ pairs. This is a good reference implementation for small inputs. It is not output-sensitive: it performs quadratic work even when segments are mostly disjoint. The efficient sweep aims for $O((n+k)\log n)$ time under the problem's stated assumptions, where $k$ counts reported intersection events or resulting overlay complexity as appropriate.

## 27.2 Sweep order converts geometry into changing adjacency

Imagine a vertical line moving from left to right. Maintain an **event queue** ordered lexicographically by $(x,y)$ and a **status structure** ordering segments by where they meet the sweep line. de Berg uses a downward horizontal sweep; our rotated convention changes coordinates, not the underlying argument.

Why inspect only neighboring segments in the status? For a proper crossing between two nonvertical segments with no other event at that point, immediately before they cross they must be adjacent. If a third segment lay strictly between them arbitrarily close to the crossing, it would have to pass through the same event. Thus the crossing pair becomes adjacent at an earlier event and can be scheduled.

At a starting endpoint, insert the segment and test its neighbors. At an ending endpoint, remove it and test the pair that becomes adjacent. At a crossing, exchange the local order and test the newly adjacent pairs. The invariant is that all events strictly behind the sweep have been processed and every future crossing of currently neighboring segments has been scheduled.

This is not permission to store a comparator that changes arbitrarily while a balanced tree remains untouched. The order is defined just to one side of the current event, and the affected block must be removed and reinserted or updated in a way that preserves the tree's invariants.

## 27.3 Process an entire event, not one pair

At event point $p$, separate incident segments into those starting at $p$, ending at $p$, and containing $p$ in their interiors. These correspond to the grouped event sets in de Berg's algorithm. Report the point with its complete incidence list. Remove the ending and crossing segments from the status, then insert the starting and crossing segments in their just-after order. Finally inspect the neighboring segments at the boundaries of this updated block.

This handles several segments meeting at one point without contradictory pairwise swaps. Vertical segments need an explicit policy because they do not persist in the just-right status: process their intersections within the event column or use a rigorously specified symbolic sweep ordering. Collinear overlap needs interval treatment or preprocessing; the book's basic segment-intersection presentation explicitly sets overlapping segments aside.

> **Try it.** Open [the sweep-event lab](lab:sketch?id=sweep). Move through the events and enable the third segment at the central crossing. Inspect the incident-segment list at $(3,2)$ and compare the status immediately to the right. Then inspect the vertical segment at $x=1$.

The lab precomputes candidate crossings by testing all pairs, groups coordinates by a decimal key, and samples just to the right using a small offset. Those are transparent teaching shortcuts. A robust production sweep needs exact or certified event identity and one-sided ordering, not decimal rounding and a universal probe offset.

%%FIG:27%%

## 27.4 From split segments to a DCEL

Once all events on a segment are known, order them by a segment parameter $t\in[0,1]$. Consecutive distinct events define atomic edges. Share a single vertex record for a common event. Do not independently create three slightly different vertices for a three-way crossing.

Create two half-edges per atomic edge. At each vertex, order outgoing directed edges cyclically. To continue the face on the left of incoming half-edge $h$, consider its twin, which points outward from the destination, and select the immediately clockwise outgoing half-edge from that twin direction. This is `next(h)` for the face-left convention. It traces the boundary while keeping the same face to the left.

An angle computed with `atan2` is convenient for a drawing, but robust cyclic order can be built from half-plane classification and orientation predicates. Collinear outgoing edges still require a policy: duplicate coincident support is not resolved merely by sorting their angles.

Following `next` partitions the half-edges into boundary cycles. A cycle is not necessarily a face. A face with a hole has multiple boundary components; the unbounded face can also have multiple boundary cycles. De Berg's overlay algorithm explicitly adds a stage that identifies which cycles bound the same face. Skipping it is a common source of erroneous profile nesting.

## 27.5 Label the subdivision before selecting material

Suppose two input regions are $A$ and $B$. Their **overlay** is the common subdivision induced by both boundaries. Each open face of the overlay receives a pair of labels: inside or outside $A$, and inside or outside $B$.

The Boolean operation then becomes a truth-table selection:

| Face label | Union | Intersection | $A\setminus B$ | Symmetric difference |
|---|---:|---:|---:|---:|
| outside both | no | no | no | no |
| inside A only | yes | no | yes | yes |
| inside B only | yes | no | no | yes |
| inside both | yes | yes | no | no |

This separation is powerful. The difficult geometry and connectivity are shared by several operations. The final selection rule is simple. Reconstructing selected faces still requires eliminating internal boundaries between selected neighbors and preserving their exterior boundary cycles.

For a numeric example let $A=[0,4]\times[0,3]$ and $B=[2,5]\times[1,4]$. Their areas are $12$ and $9$. The common region is $[2,4]\times[1,3]$ with area $4$. The union area is $17$, the difference area is $8$, and the symmetric-difference area is $13$.

> **Try it.** Use [the labeled-overlay lab](lab:sketch?id=overlay). With shift 2, predict the four areas above, then switch operations. Move the second rectangle through contact and separation. Notice that individual elementary cells can share the same label and belong to one connected result face.

The lab uses all rectangle boundary coordinates to make an elementary rectilinear grid. It computes labels and areas exactly for this family apart from ordinary input arithmetic. It is not a general arrangement builder. Its number of grid cells must not be reported as the number of maximal connected overlay faces.

## 27.6 Profile extraction adds semantics to the arrangement

A CAD sketch can contain construction geometry, open chains, self-intersections, duplicate edges, and several nested loops. Profile extraction must decide which entities participate in the region definition and which are only references.

For an oriented closed contour, the **winding number** counts signed turns around a point. The even–odd rule instead selects points crossed an odd number of times by a ray. These rules can disagree for multiply wound or self-overlapping contours. A profile API must specify its rule rather than choosing whichever polygon routine is available.

For simple disjoint nested contours, containment gives a nesting hierarchy. For touching or overlapping contours, the hierarchy alone is insufficient: the arrangement and local incidence at the contacts must be resolved first. A tangent circular hole meeting the outer boundary is exactly the kind of event where “subtract the inner loop area” does not describe all topological consequences.

For curved segments, replace line predicates and constructions with curve-specific operations while preserving the combinatorial pipeline. Curves must be split at intersections and at points required by the arrangement algorithm, such as changes of monotonicity. Coincident curve portions and tangencies are not ordinary transverse crossings. A visually dense polyline approximation cannot certify that a very small loop or near-tangent intersection was preserved.

## 27.7 Maintain a ledger of decisions

An arrangement is where numerical uncertainty becomes discrete structure. Record why two events were identified, which original curves produced an atomic edge, and which input face labels produced an output face. This is useful both for debugging and for persistent naming.

A production pipeline can expose stages:

```text
normalize participating entities
find and classify intersections
split into atomic edges
construct directed incidence
extract cycles and group them into faces
assign region labels
select result faces
validate geometry and topology
```

Do not make normalization silently snap distinct entities unless the operation's policy authorizes that change. A failure report should identify the source curve and event that could not be classified, not merely say “no valid profile.”

## 27.8 Exercises and checkpoint

> **Exercise 27.A.** For the two rectangles in §27.5, list the intersection points and the four possible face labels. Compute the Boolean areas without using a geometry library.

> **Exercise 27.B.** Construct two disjoint circles inside a rectangular boundary. Explain why traversing every boundary cycle is insufficient to identify the three bounded faces and the unbounded face correctly without assigning cycles to faces.

> **Exercise 27.C.** Build a quadratic reference arrangement for integer-coordinate segments. Add exact rational intersection points, DCEL traversal, and a point-location query. Only then replace the pairwise search with a sweep and compare outputs on the same corpus.

The checkpoint is a planar subdivision engine with inspectable event records and face labels. Preserve overlaps and degeneracies in the test suite even when the first implementation returns an explicit unsupported result for them.

> **Careful.** The sweep lab is a precomputed event inspector. Its decimal event grouping is not a production robustness technique.

## Toward a reusable API

```text
intersections(curves, arithmetic_policy) -> Events
split_at_events(curves, events) -> AtomicEdges
build_dcel(edges, cyclic_order_policy) -> Subdivision
locate(point, subdivision) -> Face | Edge | Vertex | Indeterminate
overlay(a, b) -> SubdivisionWithInputLabels
extract_profiles(subdivision, fill_rule) -> OrientedRegions
```

## Key points

The output contract must include endpoint and overlap cases. A sweep exploits changing adjacency, not arbitrary proximity. Coincident events must be processed together. Atomic edges and cyclic order determine directed connectivity. Boundary cycles must be grouped into faces before holes are interpreted. Boolean selection is simple only after the overlay geometry and labels are correct.

## Further reading

[[Engineering CAD B - Source Library#^ref-deberg-upload|de Berg et al., chapter 2, printed pp. 19–43]], is the main reading: §2.1 for sweep events, §2.2 for the DCEL, §2.3 for cycle grouping and overlay, and §2.4 for Boolean selection. The explicit overlay algorithm is on printed p. 38. Continue to chapter 6 for point location and chapter 8 for line arrangements. [[Engineering CAD B - Source Library#^ref-CGAL-arr|CGAL's arrangement manual]] is a supplementary implementation reference for geometry traits, topology, and operations on curved arrangements.

---

[[Engineering CAD 26 - Predicates, constructions and symbolic perturbation|← Chapter 26. Predicates, constructions and symbolic perturbation]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 28 - Delaunay triangulation and quality refinement|Chapter 28. Delaunay triangulation and quality refinement →]]
