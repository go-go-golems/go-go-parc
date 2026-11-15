---
title: Units Travel With Values
aliases:
  - Tagged quantities
  - Units, spaces and frames on values
  - No silent conversion
status: established
type: architecture-garden-pattern
created: 2026-11-14
tags:
  - architecture-garden
  - patterns
  - units
  - colour
  - coordinates
related_notes:
  - "[[00-overview|Agent-Operated Engines - A Pattern Language]]"
---

# Chapter 2 · Units Travel With Values

*Lengths, coordinate frames and value scales are tags on values; conversions are explicit steps chosen by declared
rules, never silent.*

Rating: ★ (a good form among several; the variations name the others; see the overview).

## Intent

Make the meaning of a number part of the value that carries it: which unit a length is in, which coordinate frame a
position refers to, which scale a sample value is on. Operations declare which tags they accept and produce; the
system inserts the conversions between them from a declared catalogue, or refuses, so that no number is read on the
wrong scale.

## Also known as

Tagged quantities, units of measure, typed coordinate spaces, colour-managed pipeline, "no naked numbers".

## Motivation

A film scan arrives as a 16-bit TIFF whose sample values are in file units, an encoded scale that is not
proportional to light. goja-cv lets an agent blur it, threshold it, measure specks on it and report positions that a
person can find in the original scan. Each step is correct on one scale only:

- A **blur** or a **contrast measurement** is physically meaningful in linear light; on encoded values it weights dark
  and bright regions differently.
- A **threshold** such as "brighter than 0.3" selects different pixels on encoded and on linear values.
- A **radius of 3** means three pixels of the scan, but the engine may compute a preview at a quarter of the
  resolution.
- A **position** measured on a cropped tile must still point at the right place in the full scan.

Without tags, the originating projects hit each of these, and none failed loudly. Two of the nine prototypes behind
goja-cv did not scale radii at export, so the full-size result differed from the approved preview. The dust
project's gold labels stored a fitted radius, about twice the speck's own, without saying so. Re-encoding tiles on
export changed which specks ranked highest.

The same problem appears wherever numbers have more than one reading:

- A **geospatial service** mixes metres, degrees and coordinate reference systems.
- A **finance system** adds amounts in different currencies, or a percentage to a fraction.
- A **robotics stack** passes poses between the robot's, the camera's and the world's frames.

## Problem

**When a number's unit, frame or scale lives only in the head of whoever wrote the code, a value read on the wrong
scale produces a plausible result instead of an error.**

## Forces

- **Convenience against correctness.** Plain numbers are easy to pass around; tags add ceremony to every call.
- **Automatic against explicit conversion.** Converting silently keeps scripts short but hides what happened;
  requiring explicit conversion is honest but verbose.
- **Kernel simplicity against kernel safety.** A kernel that assumes its input scale is simple and fast; one that
  converts for itself duplicates conversion code across kernels.
- **One canonical scale against preserving the original.** One internal scale is simple, but saving or showing results
  in the file's own units needs the original scale back.
- **Strict frames against flexible composition.** Refusing to combine values from different frames prevents
  misalignment, and blocks some combinations that a cheap step would allow.

## Solution

**Therefore: attach to every value container (an image, an array, a table, not each element) the tags that decide
how its numbers are read, on three separate axes: the unit of its lengths, the coordinate frame of its positions, and
the space (scale or encoding) of its samples. Declare the conversions between tags in one catalogue, each with its
cost and whether it loses information. Give every operation a rule: it follows its input's space, or works in a
declared space; it needs its inputs in one frame or not. Let the builder, not the kernels, satisfy the rules,
inserting lossless conversions from the catalogue as ordinary cached steps and refusing where a conversion is missing
or lossy. Numeric arguments carry declared units and are converted to the scale the engine runs at. Results are
reported in the one coordinate system every value shares.**

## Applicability

Use it when:

- the same quantity has more than one legitimate representation in the system (linear and encoded samples, metres
  and degrees, preview and full resolution);
- values cross boundaries where the reader cannot see where they came from (an agent, a saved file, another team);
- a mistake would produce a plausible but wrong result rather than a crash.

Within it, insert conversions automatically only when explicit ones would crowd every script, and scale arguments
only when the engine evaluates at more than one scale.

Do not use it when:

- every value has one representation and always will; tags would be ceremony;
- the tags would have to be checked per element in a performance-critical loop; tag the container instead, and check
  once per operation;
- the domain's conversions are mostly lossy or ambiguous; then use the smallest form, with explicit conversions
  only (see Variations).

## Structure

A participant is a responsibility, not a module; in a small engine most of these are a field or a function.

| Participant | Responsibility | Needed |
| --- | --- | --- |
| **Tagged value** | A container plus its tags, one per axis the domain has: space (scale or encoding of samples; `none` for masks, labels and tables, which are read as stored), frame (the rectangle it covers in the shared coordinate system), unit (what its coordinates and lengths mean). | Always; tag only the axes that vary in your system. |
| **Conversion catalogue** | Declares each directed conversion between tags, with whether it is lossless for a given precision (encoded↔linear is lossless in float, lossy into 8 bits). Conversions may take parameters from the value's tags (a transfer curve, a transaction's date). | Always; with two spaces it is a pair of functions. Costs and a cheapest-path search only when there are more than two spaces. |
| **Operation rule** | Per operation: the space it works in (follows its receiver, physical/linear, display/encoded), whether its inputs must share a frame, the space of its result. | Always; a field in the operation's registry entry ([Chapter 1](01-self-describing-operation-registry.md)). |
| **Argument unit** | The declared unit of each numeric argument: a length, an area, a fraction of the extent, or a level read on the work space's scale. A bare number is in the declared unit. | Only when numeric arguments mean lengths or levels that could be read on more than one scale. |
| **Builder** | Resolves rules when an operation is called or a graph is built; inserts conversions, raises warnings, or refuses. | Only when conversions are inserted automatically; without it, the operation checks tags and refuses. |
| **Scale binder** | Converts argument units to the scale an evaluation runs at. | Only when the engine evaluates at more than one scale (previews, pyramids, zoom levels). |

## Collaborations

1. A source opens with tags from its file: its space from the file's declared encoding, its frame in the shared
   coordinate system. A piece opened with its origin (a tile of a larger scan) keeps the whole's coordinates.
2. The agent calls an operation. The work space comes from the rule: a physical operation (exposure, healing,
   conversion to grey) works in linear light; a display operation (drawing an overlay) works on encoded values; any
   other operation follows its receiver.
3. *Only for operations that combine inputs:* their frames must be identical, or the operation refuses (`E_FRAME`)
   with a fix that crops them to a common box. Two disjoint pieces have no common box; the fix there is to open the
   region that covers both.
4. Each input is converted to the work space by catalogue conversions, and the result back to the receiver's space.
   With a builder, the conversions are inserted as ordinary (cached) steps; without one, a mismatch is a refusal whose
   fix is the explicit conversion. *Only where mixing encodings is sometimes intended:* an `ENCODING` warning.
5. *Only when the engine evaluates at more than one scale:* the scale binder converts length arguments to the scale
   of the evaluation, and that scale is part of every cache key. A level is read on the work space's scale; for an
   operation that follows its receiver, the agent chooses that scale by choosing the receiver's space, and
   measurements report on the same scale. A physical operation's levels are in linear light, and its help says so.
6. Results report positions in the coordinate system every value shares.

## Sketch

```text
value Tags:    space: Space, frame: Rect in shared coordinates, unit: Unit   -- only the axes your domain has
value Value:   data, tags: Tags
value Conv:    from: Space, to: Space, lossless(precision) → bool, params(tags) → Params   -- e.g. a curve
value OpRule:  works: follows | physical | display, sameFrame: bool, result: follows | declared(Space)

apply(op, receiver, args) → Value | Refusal                    -- at call time, or when a graph node is built
  rule = op.rule(args)
  work = match rule.works:
    physical → linear
    display  → encoded
    follows  → receiver.space
  inputs = [receiver] ++ valueArgs(args)
  if rule.sameFrame:                                           -- only for operations that combine inputs
    for x in inputs[1:]:
      if x.frame ≠ receiver.frame:
        return refuse(E_FRAME, frames: [receiver.frame, x.frame], fix: "crop both to one box", where: callSite())
  if work == encoded and mixesEncodings(inputs):               -- only if mixing is sometimes intended
    warn(ENCODING, where: callSite())
  converted = []
  for x in inputs:
    c = (x.space == none) ? x : convertTo(x, work)            -- masks and tables are read as stored;
                                                              -- without a builder: refuse, fix "x.as(work)"
    if c is Refusal: return c                                 -- refusals propagate; nothing is computed
    converted = converted ++ [c]
  r = op.run(converted, args)
  return match rule.result:
    follows     → convertTo(r, receiver.space)                 -- back to what the caller had
    declared(s) → withSpace(r, s)                              -- the op is itself a conversion

convertTo(x, s, acceptLoss: false) → Value | Refusal           -- the explicit as(s) and saves pass acceptLoss
  if x.space == s: return x                                    -- no step for an identity
  path = catalogue.path(x.space, s)                            -- a direct lookup with two spaces;
                                                               -- cheapest path only with more
  if path is none: return refuse(E_SPACE, from: x.space, to: s, valid: catalogue.reachable(x.space))
  if not all(c.lossless(x.precision) for c in path) and not acceptLoss:
    return refuse(E_LOSSY, from: x.space, to: s, fix: "x.as(\"" + s + "\") converts on purpose")
  for c in path: x = c.run(x, c.params(x.tags))                -- with a lazy graph: a cached node instead
  return x

-- only when the engine evaluates at more than one scale
bindArg(arg, scale, extent) → number                           -- at evaluation time
  match arg.unit:
    length   → arg.value × scale
    area     → arg.value × scale²
    fraction → arg.value × extent                              -- extent of the receiver's frame
    level    → arg.value                                       -- on the work space's scale (step 5)

-- in use (all numbers are placeholders)
img   = open("piece.tif", origin: [X0, Y0])                    -- space from the file; frame from the origin
glow  = img.exposure(+1)                    -- converted to linear, exposed, converted back
spots = img.as("linear").peaks(radius: 3)   -- 3 length units at any scale; positions in shared coordinates
mask  = img.as("linear").above(0.05)        -- 0.05 in linear light, on the scale stats() reported
```

## Implementation notes

1. **Kernels never convert.** goja-cv's builder inserts conversion nodes and its kernels assume their declared
   space, so conversion code exists once, is cached, and appears in the graph an agent can inspect. The Editor lab
   converts inside each physical kernel (exposure and temperature convert to linear and back in their loops); every
   new kernel must remember to. Without a builder, the rule still holds: the call refuses, and the fix names `as()`.
2. **Put the space on the value, not in the caller's head.** goja-cv v1 chose the scale per call through options; v2
   made the space a property of the image, set by `cv.open` (which returns "file units") and changed only by `as()`,
   with every other operation returning its result in its receiver's space. goja-cv's lengths are document pixels
   (`DocPx`), and its frames are rectangles in document coordinates; the sketch's `length` and "shared coordinates"
   are those, renamed.
3. **Keep the axes separate, and tag only the ones that vary.** Space (how samples are scaled), frame (where a value
   lies) and unit (what a length means) fail differently and convert differently. One combined "type" tag hides which
   axis a refusal is about. A system with one coordinate system and one evaluation scale needs only the space tag;
   a ledger needs only currency.
4. **A level is read where it is measured.** A threshold could be converted between spaces through the transfer
   curve, but goja-cv deliberately reads it on the work space's scale and reports statistics on the same scale. An
   agent picks thresholds from measurements; keeping both on one scale makes the choice explicit
   (`img.as("linear")…`) and the number consistent.
5. **Areas scale with the square.** goja-cv's `DocPx2` unit scales by the square of the evaluation scale. A minimum
   area given in document pixels squared would otherwise be a hundred times too strict at one-tenth scale.
6. **Share one coordinate system and refuse mismatched extents.** In goja-cv a crop keeps document coordinates, and
   so does a tile opened with its origin; the dust project opens every tile that way, so agents, gold labels and the
   review tool share positions. Combining images whose rectangles are not identical is refused (`E_FRAME`) rather
   than resampled or padded, because resampling shifts masks against images by fractions of a pixel, which matters
   for specks three pixels wide. Domains with several coordinate systems (map projections) add reprojection to the
   conversion catalogue.
7. **Conversions may need parameters from the value.** The transfer curve between file units and linear light comes
   from the file's declared encoding, a tag. A currency conversion needs the transaction's date. Such parameters come
   from the value's tags or arguments and enter the conversion node's key; a build-time constant would be wrong for
   every value but one.
8. **The builder inserts only lossless conversions; lossy ones are always explicit.** In float, encoded-to-linear and
   back is effectively lossless, so goja-cv inserts it freely. Quantising to 8 or 16 bits is not; it happens only
   when a result is saved, or when the caller converts with `as()`, both of which say so in the call. Bouncing
   between spaces costs time even when lossless; the builder skips identity conversions, and a chain of physical
   operations pays one round trip per operation unless adjacent conversions are merged.
9. **Tag the data you did not produce.** The gold labels' radius was the radius of a fitted circle, about twice the
   speck's; measuring with it as the speck's radius gave a median signal-to-noise ratio of 0.86 instead of 1.56,
   until someone compared the numbers with the pictures. A field's unit and definition belong in its schema, and
   every re-encoding on the way to a dataset is a conversion with a record (see [Chapter 11](11-lineage-ledger.md)).
10. **Warn where you cannot refuse.** Mixing encodings in encoded space is sometimes intended (a display overlay).
    goja-cv raises a build-time `ENCODING` warning, reported next to the line that caused it.

## Variations

- **Smallest form: tags checked, conversions explicit.** Keep the tagged value, a conversion catalogue (often one
  pair of functions), and a rule per operation, checked when the operation is called. A mismatch is a refusal whose
  fix is the explicit `as()`; nothing is converted automatically. It gives up the builder, cached conversions and
  argument scaling, and scripts are more verbose. It is enough with two spaces and one evaluation scale, and it is
  the right form for domains where most conversions lose information. Add the builder when explicit conversions
  crowd every script, and the scale binder when previews appear.
- **Static units in the type system** (units of measure checked by the compiler). Errors before running and no
  run-time cost; needs a language that supports it, and does not cover data loaded at run time.
- **One internal space, tags only at the boundary.** Convert everything to one scale on load and back on save. The
  degenerate case of this pattern: simplest, and it breaks as soon as two internal scales are both needed (linear for
  physics, encoded for display).
- **Tags as schema metadata** for stored data, without run-time enforcement. Catches the dataset problems of note 9,
  not the computation ones.

## Consequences

- \+ A whole class of plausible-but-wrong results becomes refusals or warnings.
- \+ Preview and full-resolution results agree, because arguments mean the same at every scale.
- \+ Conversions are visible, cached and testable, instead of scattered through kernels.
- \+ Coordinates survive cropping, tiling and export, so different tools share positions.
- − Every operation needs a rule, and every new space needs catalogue entries to and from the others.
- − Inserted conversions cost time and memory; a chain that bounces between spaces pays for each bounce.
- − Agents and users must learn the vocabulary (encoded, linear, document pixels) before the refusals make sense.

## Known uses

- **F# units of measure** check physical units at compile time; Python's **Pint** and **astropy.units** attach units to
  values at run time and convert between them.
- **OpenColorIO** declares colour spaces and the conversions between them in a configuration that film and
  visual-effects pipelines share: a conversion catalogue.
- **PostgreSQL** declares every cast in a catalogue (`pg_cast`) with the context in which it may be applied
  (implicitly, on assignment, or only explicitly); the planner inserts implicit casts and refuses the rest, as the
  builder here inserts lossless conversions and refuses lossy ones.
- **GDAL and PROJ** attach coordinate reference systems to rasters and vectors and reproject between them.
- **NASA's Mars Climate Orbiter** was lost in 1999 after one team's software reported impulse in pound-force seconds
  where another expected newton seconds: the classic case of a number without its unit.

## Related chapters

- [Chapter 1 · Self-Describing Operation Registry](01-self-describing-operation-registry.md): where argument units and
  operation rules are declared.
- [Chapter 3 · Content-Keyed Lazy Graph](03-content-keyed-lazy-graph.md): inserted conversions are cached nodes.
- [Chapter 4 · Reach-Declared Region Evaluation](04-reach-declared-region-evaluation.md): reach scales with the
  evaluation like any length.
- [Chapter 6 · Repairable Errors](06-repairable-errors.md): the refusals and warnings this chapter raises.
- [Chapter 11 · Lineage Ledger](11-lineage-ledger.md): recording field definitions and encoding chains of datasets.
- Classic patterns: **Value Object** (Fowler) for tagged quantities; **Adapter** for conversion steps.
