---
title: "Engineering CAD from First Principles — Chapter 14. B-rep, STEP, meshes and manufacturing"
aliases:
  - "Chapter 14. B-rep, STEP, meshes and manufacturing"
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

# Chapter 14. B-rep, STEP, meshes and manufacturing

[[Engineering CAD 13 - Assembly constraints on rigid motions|← Chapter 13. Assembly constraints on rigid motions]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 15 - A parametric CAD compiler|Chapter 15. A parametric CAD compiler →]]

A CAD model can be exported as an analytic solid, a polygonal approximation or a manufacturing package. Those formats preserve different information. Understanding what is lost requires a mathematical model of approximation error and an explicit account of topology, units and metadata.

## 14.1 Exact boundary descriptions and sampled surfaces

An analytic B-rep face can reference a cylinder whose surface is the continuous set $S(u,v)=(r\cos u,r\sin u,v)$. A triangle mesh stores finitely many vertices and faces approximating that set. When exporting a mesh, the primary geometric quality parameter is usually **chordal or linear deflection**: how far mesh elements deviate from the modeled surface, with additional angular controls.

For a circle approximated by an inscribed regular polygon, Chapter 2 derived

$$
\varepsilon=r\left(1-\cos\frac\pi n\right).
$$

At radius $10$ mm, 32 sides have about $0.04815$ mm maximum radial deviation. Doubling the sides reduces the error by roughly four. A CAD exporter may use a more complicated adaptive mesher, but the principle remains: there is a geometric error budget that the file format itself cannot reconstruct after the original analytic surface is discarded.


%%FIG:14%%

**Try it.** [The meshing bench](lab:sketch?id=meshing) changes the number of polygon sides and plots chord error against the exact circle.

## 14.2 STL, 3MF and STEP preserve different objects

**STL** encodes triangles and their normals in a very simple representation. It does not intrinsically encode units, parametric history, analytic surfaces, feature names or assemblies. A slicer often assumes millimeters, but that assumption is external to the file.

**3MF** is a structured package with model units, mesh resources, components, metadata and extension mechanisms. Its core mesh model has topology requirements such as consistent triangle edge incidence. A 3MF file may be valid as a ZIP/XML package yet still contain an invalid or nonmanifold mesh.

**STEP** is a family of ISO product-model exchange schemas. For CAD solid exchange, it can represent exact analytic and spline geometry and topology. A basic shape writer need not carry the same rich information as an extended XDE/STEPCAF translator, which can preserve assemblies, colors, names and GD&T depending on its capabilities and configuration.

## 14.3 What Jig actually exports

Jig's [io.js](https://github.com/go-go-golems/jig/blob/main/import/jigcad/src/engine/io.js) writes binary STL, 3MF, SVG, an IR bundle, and STEP through `STEPControl_Writer`. Its STEP export builds a compound of the modeled bodies and writes their B-rep geometry, but explicitly drops Jig's parametric history and persistent names. Its 3MF exporter writes triangulated geometry, welding vertices at written coordinates and including some print metadata.

The project corrected an earlier 3MF issue in which triangles did not share welded vertices, and corrected a misleading “maximum deviation” label that had really been a mesher setting. These are important distinctions: a *requested deflection* is not necessarily a mathematically certified maximum distance from every mesh point to the exact surface.

## 14.4 Mass properties and physical accuracy

For a homogeneous solid of density $\rho$, mass is $m=\rho V$. Center of mass is

$$
c=\frac1V\iiint_\Omega x\,dV,
$$

and the inertia tensor about the origin is

$$
I=\rho\iiint_\Omega (\|x\|^2 I_3-xx^\top)\,dV.
$$

These are important for robotics, balances and mechanisms. Jig exposes useful volume and mass estimates but its issue log notes that the chosen OpenCascade WASM build did not expose the full inertia-matrix binding. An improved binding or explicit integration layer would enable richer engineering analysis.

Approximating these integrals on a mesh introduces geometric error. A valid mesh is necessary for volume integration, but error magnitude also depends on tessellation quality, conditioning and the orientation of triangles.

## 14.5 Round-trip testing as an engineering discipline

An import/export system needs more than “file written successfully.” For a part $S$, perform

$$
S\xrightarrow{\mathrm{export}}F\xrightarrow{\mathrm{import}}S'.
$$

Compare the volumes, bounding boxes, centroids, surface types, solid counts, face orientations, closure and tolerances of $S$ and $S'$. If STEP preserves analytic geometry, compare corresponding surfaces with a geometric distance measure. If mesh export is intentional, compare against a stated approximation target.

Importing existing STEP models into Jig would require not only a reader but also a model of what imported geometry means: a nonparametric body, a linked external component, or a starting shape for direct modification. Imported faces will not automatically have feature-history names from Jig scripts.

## 14.6 Manufacturing and engineering drawings

Jig's printing facilities handle orientation, overhangs, clearances and 3MF/STL export, but it is not a complete G-code slicer. A general mechanical CAD platform would also benefit from hole tables, dimensioned orthographic drawings, DXF export, section annotations, tolerance metadata and possibly sheet-metal flat patterns.

These should come after reliable geometry and interchange. Publishing a beautiful drawing of a shape whose topology is incorrect does not improve engineering trustworthiness.

> **Exercise.** A hole of diameter 4 mm is represented by a polygonal circle with 24 sides. Compute its maximum radial deviation and estimate how many sides are required for a target radial error of 0.01 mm. State what a polygon approximation cannot preserve about the original circle.

> **Careful.** Do not assume `STEPControl_Writer` automatically exports the full parametric document, product metadata, or a particular application protocol without checking the chosen schema and translator.

### Deeper study: distinguish display tessellation from quality meshing

[[Engineering CAD 28 - Delaunay triangulation and quality refinement|Chapter 28]] derives planar Delaunay triangulation and constrained refinement. [[Engineering CAD 30 - Tetrahedral quality and topology-safe simplification|Chapter 30]] then constructs a tetrahedral sliver whose circumradius–edge ratio remains acceptable while its volume collapses. A visually smooth display mesh, a boundary-preserving surface mesh and an analysis-quality tetrahedral mesh have different requirements. Export validation should state which one it checks, including units and the relationship to the original B-rep.

## Toward a reusable API

```text
ExportPolicy { format, units, geometricTolerance, metadataProfile }
ExportReport { preserved, approximated, discarded, observedError }
RoundTripReport { volumeError, areaError, topology, surfaceTypes }
MeshAudit { watertight, manifold, orientable, selfIntersections }
```

## Key points

Analytic B-reps and triangle meshes represent different geometric objects. STL generally loses units and analytic geometry; 3MF can preserve more manufacturing metadata; STEP supports rich CAD geometry and optional document attributes. Deflection settings are not automatically verified error bounds. Interchange quality requires round-trip geometric and topological tests.

## Further reading

- [OpenCascade STEP translator guide](https://occt3d.com/dev/doc/overview/html/occt_user_guides__step.html) explains basic and XDE-based exchange.
- [3MF Core Specification](https://3mf.io/wp-content/uploads/sites/106/2025/02/3MF_Core_Specification_v1.3.0.pdf) defines the package and mesh requirements.
- [JigCAD export implementation](https://github.com/go-go-golems/jig/blob/main/import/jigcad/src/engine/io.js) shows what is actually serialized.

---

[[Engineering CAD 13 - Assembly constraints on rigid motions|← Chapter 13. Assembly constraints on rigid motions]] · [[Course - Engineering CAD from First Principles|Contents]] · [[Engineering CAD 15 - A parametric CAD compiler|Chapter 15. A parametric CAD compiler →]]
