---
title: "Engineering CAD from First Principles — Chapter 20. Manufacturing, drawings and sheet metal"
aliases:
  - "Chapter 20. Manufacturing, drawings and sheet metal"
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

# Chapter 20. Manufacturing, drawings and sheet metal

[[Engineering CAD 19 - Tolerance, healing and metrology|← Chapter 19. Tolerance, healing and metrology]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 21 - Design-space search and robust optimization|Chapter 21. Design-space search and robust optimization →]]

Mathematics in this chapter: [[Mathematics - Curves and Surfaces|Curves and Surfaces]], [[Mathematics - Tolerancing, Uncertainty and Statistics|Tolerancing, Uncertainty and Statistics]] (see [[Mathematics]]).

A model that is correct as a solid is not automatically suitable for a printer, a CNC machine, a sheet-metal shop or an inspection department. Every process introduces constraints beyond the mathematical boundary of the part. This chapter follows one design through a tessellated print, an interference fit, a bent sheet and an engineering drawing to show which additional semantics the CAD system must carry.

## 20.1 Geometry is not a manufacturing plan

An exact B-rep describes boundary surfaces and their arrangement. It can say that two cylinders intersect and that a hole is exactly $5\,\mathrm{mm}$ in diameter. It does not by itself specify the printer nozzle, layer height, toolpath, cutter reach, datum system or manufacturing sequence.

A printable STL describes a triangle mesh, not a fully specified fabrication process. A 3MF package can carry units and additional print-oriented metadata, while an exact STEP file can preserve B-rep and, with suitable product structure, richer engineering data. G-code is a separate set of manufacturing instructions produced by slicing and process planning. **Exporting STL or 3MF is not the same as implementing a slicer.**

A manufacturing-oriented CAD engine should distinguish geometric claims (“this face is a circle”), process claims (“this hole is printable”), and verification claims (“this tolerance was met on a measured part”). This separation is as important as the separation of geometry and topology in Chapter 3.

## 20.2 Tessellation: how far does a chord miss an arc?

Approximate a circle of radius $R$ using $N$ equally spaced chord segments. The central angle of each chord is $2\pi/N$. The largest distance between the circle and a chord occurs at the chord midpoint and equals the **sagitta**

$$
\delta=R\left(1-\cos\frac{\pi}{N}\right).
$$

For $R=20\,\mathrm{mm}$ and $N=12$, the sagitta is approximately $0.6815\,\mathrm{mm}$. Doubling $N$ does not halve the error: for sufficiently large $N$, $1-\cos x\approx x^2/2$, so $\delta\approx R\pi^2/(2N^2)$.

A tessellation setting is therefore a way of controlling approximation cost, but it does not certify exported geometry unless the mesher supplies and verifies a real bound. Curvature varies over a general NURBS surface, making uniform segment counts inefficient. Adaptive meshing uses smaller triangles in highly curved regions and may require additional checks along trimmed edges.

## 20.3 Layered manufacturing introduces anisotropy

In fused deposition modeling (FDM), a slicer plans extruded roads in a stack of layers. A printed part can be much stronger in directions supported by continuous filament paths than in directions that depend on bonding between layers. An orientation suitable for reducing support material may be a poor orientation for a load-bearing clip.

Layer height affects the staircase approximation on sloping faces. Nozzle diameter affects the smallest practical road width and influences wall-thickness choices. Supports, bridges, infill, perimeters and cooling behavior are process decisions, not merely properties of the ideal B-rep.

JigCAD includes fit profiles, overhang inspection, print orientation, teardrop holes and simple layer-section calculations. Its code also exposes STL/3MF export. These are meaningful process-aware features, but they do not constitute complete printer-specific toolpath generation or validated physical-process simulation.

## 20.4 Work a fit-aware printed hole

Suppose a cylindrical pin has nominal diameter $5.00\,\mathrm{mm}$. You want $0.25\,\mathrm{mm}$ *radial* clearance on each side, so the requested diametral clearance is $0.50\,\mathrm{mm}$. Before print compensation, the target hole is

$$
D_{\text{target}}=5.00+2(0.25)=5.50\;\mathrm{mm}.
$$

Suppose a calibration coupon establishes that holes built using a particular material, orientation and slicer profile come out $0.12\,\mathrm{mm}$ undersized **in diameter** near this size. To target a physical $5.50\,\mathrm{mm}$ opening, a simple first-order compensation is $D_{\text{CAD}}=5.62\,\mathrm{mm}$.

This calculation is not a universal FDM correction. The actual bias depends on process, material, hole size, orientation and measurement method. The compensation should be stored as a named calibrated profile with date, printer, filament and measurement uncertainty, not silently applied to every design.

**Try it.** Use [the manufacturing clearance bench](lab:sketch?id=manufacturing) to vary the pin, radial gap and empirical hole undersize. The diagram distinguishes nominal CAD dimensions from the estimated physical opening.

%%FIG:20%%

## 20.5 What a sheet-metal flat pattern must know

A bent sheet cannot generally be flattened by simply unfolding its outer surface. The bend has finite thickness, and its layers stretch or compress differently. A common approximation models a *neutral axis* inside the sheet at radius $R+Kt$, where $R$ is the inside bend radius, $t$ is thickness and $K$ is a material/process-dependent location factor.

The bend allowance over angle $\theta$ in radians is

$$
\mathrm{BA}=\theta(R+Kt).
$$

For a right-angle bend with $R=2\,\mathrm{mm}$, $t=1.5\,\mathrm{mm}$ and an assumed $K=0.4$, the bend allowance is $(\pi/2)(2+0.6)\approx4.0841\,\mathrm{mm}$. The flat blank dimension also depends on how flange dimensions are defined and the bend deductions used by the shop. This formula estimates one part of the layout; it is not a complete unfolding specification.

A serious sheet-metal feature system needs stable thickness, bend radii, flange operations, corner reliefs, bend tables and explicit flattening. It also needs to reject impossible self-intersections and bends that conflict with tooling constraints. JigCAD's general B-rep feature list does not currently describe a complete sheet-metal unfold workflow.

## 20.6 Engineering drawings and GD&T

A 3D solid supplies shape. An engineering drawing additionally communicates functional intent: dimensions, inspection datums, allowable geometric variation, materials, surface finish and process-specific notes. Orthographic projections and section views are derived from the model, but they must be formatted and annotated independently.

For example, two holes may have a nominal center distance $40\,\mathrm{mm}$ while their *position tolerance relative to a datum system* determines assembly interchangeability. A bounding-box dimension of the solid cannot communicate this. The standards system matters: ISO GPS and ASME Y14.5 provide different conventions and applicability. A CAD implementation should identify the supported standard and edition rather than inventing custom semantics for a tolerance symbol.

A useful architecture separates a `DrawingView` derived from the geometry and a `DimensionRequirement` associated with named datums and features. The drawing should invalidate its references when topology changes, rather than silently labeling the wrong hole.

## 20.7 Mesh correctness is a separate export gate

For additive manufacturing, verify that triangle orientations are consistent and that the intended solid boundary is watertight and manifold within a declared tolerance. Each undirected edge of a closed two-manifold triangulation is incident to exactly two oriented triangle edges. Duplicate vertices at identical positions need welding under a declared policy; careless welding can also collapse thin intentional gaps.

Jig's 3MF writer welds duplicate coordinates to meet mesh topology expectations. That does not by itself guarantee that every generated mesh is watertight or that every approximation error is within a specified physical tolerance. A release-quality export should run independent mesh checks and report quantities the user can interpret.

## 20.8 A process-aware part contract

A printable assembly can declare physical targets, process assumptions and geometry separately:

```text
Part: hinge-pin
geometry: pin_diameter = 5.00 mm
fit: radial_clearance = 0.25 mm
process: FDM, printer profile P, orientation Z
calibration: expected hole undersize = 0.12 mm (diametral)
result: CAD target hole diameter = 5.62 mm
validation: 3MF watertight, gap >= required, coupons measured
```

The calibration is an assumption backed by measurements, not a fact about all machines. Include uncertainty and provenance so it can be changed without silently altering the meaning of earlier manufacturing results.

> **Exercise.** Derive the sagitta formula using the radius and half-chord right triangle. How many equal segments are needed for a radius-20-mm circle if the sagitta must be at most 0.05 mm? Then calculate the bend allowance of a 90-degree bend with $R=3$, $t=2$, $K=0.4$ mm.

> **Careful.** A printing “clearance of 0.25 mm” is ambiguous unless it says radial, diametral or total gap. Ambiguous fit units can yield a factor-of-two mistake even with perfectly accurate CAD mathematics.

## Toward a reusable API

```text
TessellationPolicy { linearTolerance, angularTolerance, certifiedBound }
PrintProfile { process, calibration, nozzle, layer, materials }
FitRequirement { radialOrDiametral, nominal, min, max }
Bend { neutralAxisModel, radius, thickness, angle, flatAllowance }
Drawing { datums, views, dimensions, standard, annotations }
ExportReport { manifold, units, geometricError, lostMetadata }
```

## Key points

An exact B-rep is not a process plan. Tessellation introduces quantified approximation error. FDM dimensions and strength depend on print orientation and calibration. Radial and diametral clearances must not be confused. Sheet-metal flat patterns require a bend model. Engineering drawings communicate datum and inspection requirements beyond shape. Exports should pass independent mesh and metadata checks.

## Further reading

- [3MF Core specification](https://3mf.io/wp-content/uploads/sites/106/2025/02/3MF_Core_Specification_v1.3.0.pdf) specifies the mesh container and model units.
- [OpenCascade STEP translator guide](https://occt3d.com/dev/doc/overview/html/occt_user_guides__step.html) describes richer geometric and product-structure exchange.
- [JigCAD printing and fit API](https://github.com/go-go-golems/jig/blob/main/import/jigcad/src/engine/KERNEL-API.md) records available manufacturing features and explicit gaps.
- [JigCAD export source](https://github.com/go-go-golems/jig/blob/main/import/jigcad/src/engine/io.js) allows inspection of actual STL, STEP and 3MF output decisions.

---

[[Engineering CAD 19 - Tolerance, healing and metrology|← Chapter 19. Tolerance, healing and metrology]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 21 - Design-space search and robust optimization|Chapter 21. Design-space search and robust optimization →]]
