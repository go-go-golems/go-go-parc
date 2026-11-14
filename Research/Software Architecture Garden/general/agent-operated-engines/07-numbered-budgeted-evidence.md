---
title: Numbered, Budgeted Evidence
aliases:
  - Pictures for seeing, numbers for measuring
  - Set-of-marks evidence
  - Image budget for agents
status: established
type: architecture-garden-pattern
created: 2026-11-14
tags:
  - architecture-garden
  - patterns
  - agents
  - vision
  - looks
related_notes:
  - "[[00-overview|Agent-Operated Engines - A Pattern Language]]"
---

# Chapter 7 · Numbered, Budgeted Evidence

*Pictures are for seeing and numbers for measuring; pictures carry ids, arrive in sheets, and are rationed.*

Rating: ★ (a good form among several; the variations name the others; see the overview).

## Intent

Give a vision-capable agent the pictures it needs to judge what it is looking at, without ever making it read a
measurement off a picture. Every item in a picture carries an id that matches a row of numbers delivered beside it;
many items arrive together in one sheet rather than one picture each; and the number of pictures per call and per
conversation is budgeted, with anything left out named in the reply.

## Also known as

Set-of-marks prompting, contact sheets for agents, looks with ids, an image budget.

## Motivation

Annotator agents in the dust project had to find dust specks on 1,024-pixel tiles and report their positions. The
first version of goja-cv gave them zoomed crops with rulers along the edges, and the agents read positions off the
rulers. Positions read off twice-magnified ruler crops were 5 to 10 pixels off. On one tile, 24 of 32 positions the
agents reported held nothing measurable. Agents even derived formulas such as `x = crop_x + (px − 52) / 2` to
correct for the ruler's margin. Rulers help a person; a vision model localises poorly at this scale.

goja-cv's later versions changed what pictures are for. Candidates come from a measurement (`peaks`) as rows with
ids and coordinates, and pictures show those same ids circled and numbered. The agent looks at a sheet of twelve
numbered candidates, decides which are dust by looking, and reports ids, whose coordinates it already has as
numbers. The evidence is small (two runs per side) but consistent. In a question task (find the spots, sheet them,
measure them), the agents with candidates as rows reported far fewer positions that held nothing (2 and 5 spots far
from any gold point, against 15 and 12) and located more gold points within 5 pixels (14 and 13 of 53, against 4 and
5). In longer annotator-style sessions on one tile, both versions located 9 of 13, because the helper library there
already supplied candidates as rows: the gain comes from numbers instead of ruler readings, wherever it is applied.

Pictures also cost. The model API the dust pipeline used rejects a conversation holding more than 100 images, and a
run that crosses the limit ends with nothing; the first batch of annotator runs lost runs that way. The fix was a
budget stated in the prompt ("use at most 50; prefer sheets and numbers") and sheets that hold many candidates in one
image.

The same problem appears elsewhere:

- A **UI-testing agent** clicks elements on screenshots; reading pixel positions off a screenshot misses, while
  numbered element ids map to exact selectors.
- A **document-extraction agent** checks fields on scanned pages; it should read values from text, and use crops with
  numbered boxes only to judge which box is which.
- A **map agent** marks parcels on aerial images; positions come from geometry, pictures only confirm.

## Problem

**When an agent must both see and measure, pictures alone give it imprecise numbers and an unbounded image count,
and numbers alone leave it unable to judge what they describe.**

## Forces

- **Seeing against measuring.** Models judge appearance well from pictures and read coordinates from them poorly.
- **Context against detail.** One large overview shows everything at once and loses small details when an API
  downscales it; many small crops keep detail and multiply the image count.
- **Completeness against budget.** Every picture an agent asks for is evidence, and every picture takes context and
  counts against hard limits.
- **Uniform against tailored views.** One standard view per item is predictable; the best view depends on what the
  agent is deciding (scene versus detail, colour versus contrast).
- **Delivery against attention.** Pictures the program created but did not return may matter, and delivering them
  all floods the reply.

## Solution

**Therefore: split the work between pictures and numbers. Compute positions, sizes and scores as rows with stable
ids, and return them as numbers. Draw pictures only to support judgement: mark each item with its id, matching its
row, and put many items into one sheet of small, magnified cells, with several views side by side where the decision
needs them. Never ask the agent to read a number off a picture; if it must point, it points by id. Ration pictures
per call and per conversation, state the budget to the agent, deliver every picture a call creates within the
budget, and name the ones left out.**

## Applicability

Use it when:

- the agent must judge things visually and also report precise positions or measurements;
- there are many candidates to judge, more than the image budget allows one at a time;
- the transport or model API limits the number or size of images.

Do not use it when:

- the judgement is purely numeric (a threshold on a measured value); skip pictures entirely;
- items have no natural identity or position to number (a texture, a global colour cast); show one picture with a
  question, not marks;
- the agent cannot see images (a text-only model); give it the numbers and a textual description, and do not pretend
  a picture was seen.

## Structure

| Participant | Responsibility |
| --- | --- |
| **Item rows** | Measured candidates with stable ids and their numbers (position, size, scores), returned as a table. |
| **Marked view** | A picture with each item drawn and labelled by its id. |
| **Sheet** | A grid of small cells, one per item, each magnified and labelled by id, optionally with several views per item. |
| **View presets** | Named renderings for decisions (the scene, a band-pass "speck" view, a colour view). |
| **Budget** | Limits per call (count, bytes) and per conversation (count), stated in the agent's instructions. |
| **Deliverer** | Delivers the pictures a call created, in order, within the budget; names the rest by line. |

## Collaborations

1. The agent's program asks the engine for a measurement of candidates; the engine returns rows with ids, positions
   and scores. (The agent writes programs and decides; the engine measures, draws and delivers.)
2. The program filters and sorts the rows, keeping the twelve to judge first; the others stay in the rows, so a
   later sheet can show them.
3. It asks for a sheet of those rows, with two views per item (the scene and the speck view); each cell is magnified
   and labelled with the row's id.
4. The deliverer attaches the sheet to the reply and counts it against the call and conversation budgets.
5. The agent judges the cells and answers with ids; positions come from the rows, not from the picture.
6. When the agent needs detail, it zooms one window; when it is near the budget, the instructions tell it to stop
   looking and answer.

## Sketch

```text
value Item:   id, cx, cy, r, scores…                 -- numbers, from a measurement; id stable across filtering
value Sheet:  cells: [Cell(itemId, views: [View], zoom)], labels: ids

candidates = measure(peaks(view(img, "speck"), snr: 1))       -- rows with ids
keep = sortBy(candidates, -score)[0:12]                        -- the agent filters in code
sheet(keep, views: [img, view(img, "speck")], cell: 40 px, zoom: 4).look("top 12")

deliver(callPictures, budget) → (delivered, warnings)
  delivered, warnings = [], []
  for p in returnedFirst(callPictures):
    if count(delivered) < budget.perCall and bytes(delivered) + bytes(p) ≤ budget.bytes
       and session.picturesSoFar < budget.perConversation:
      delivered = delivered ++ [p]; session.picturesSoFar += 1
    else:
      warnings = warnings ++ [Warning(LOOKS, "not delivered: " ++ p.label ++ " (line " ++ p.line ++ ")",
                                      fix: "fewer cells per sheet, or a smaller zoom")]
  return delivered, warnings

-- the agent's answer cites ids; the engine maps them to numbers, and refuses ids it never showed
byId = { i.id: i for s in deliveredSheets(session) for i in s.items }   -- only what the agent actually saw
for i in answer.dust:
  if i not in byId: return refuse(E_UNKNOWN_ID, i, valid: keys(byId), hint: "cite ids from the last sheet")
labels = [byId[i] for i in answer.dust]                          -- exact cx, cy, r
```

## Implementation notes

1. **Never make a model read a number off a picture.** This is the design rule the dust project's evidence forced.
   Positions read off ruler crops were off by 5 to 10 pixels; positions from rows are exact. Rulers remain useful for
   a person reading the same picture.
2. **Ids in the picture must match ids in the rows.** goja-cv's overlays and sheets label items with the `id` field
   of the rows they were given, so "7" in the picture is the row whose id is 7, wherever it sits in the table. Relabelling in the picture (1 to 12 by
   position in the sheet) breaks the link the moment the agent filters the rows.
3. **Sheets of small magnified cells beat single zooms.** A sheet of twelve to fifteen cells costs one image; twelve
   zooms cost twelve. Each cell is a small crop shown magnified, so the sheet is many small looks in one picture, not
   one large overview (note 8). goja-cv's helper caps sheets at fifteen cells so that each cell stays large enough to
   judge after the API downscales the image; the right count depends on the API's image size limit.
4. **Put the views the decision needs side by side.** The annotators decided best with the scene and a band-pass view
   of the same cell next to each other: the scene shows what the object is, the band-pass view shows whether it
   stands out from grain.
5. **Stretch each cell to its own range when contrast varies.** A faint speck next to a bright one disappears under one
   shared stretch; goja-cv's sheet option `stretch: "cell"` gives each cell its own.
6. **Derive the budgets from the transport, and state them in the instructions.** The conversation budget comes from
   the API's hard limit, with a margin (the dust runners' API rejects conversations with more than 100 images; the
   prompt asks for at most 50); the per-call budget from what one reply should carry; the cells per sheet from the
   image size the API keeps after downscaling, divided by the size a cell needs to stay judgeable. An agent cannot
   plan around a limit it learns about only when the run is rejected.
7. **Deliver every picture a call created, and name the ones left out.** goja-cv v1 delivered only returned pictures
   and silently dropped `x.look()` statements; v2 delivers all of them, returned ones first, up to its per-call budget
   (four pictures and 8 MiB, goja-cv's defaults), and names each omitted one by line in a `LOOKS` warning.
8. **Several small magnified looks beat one large overview.** APIs downscale large images before the model sees them,
   which erases three-pixel specks; the pi subagents handbook records the same finding for its judges. A sheet is the
   way to show several small magnified looks in one image; an uncropped overview is not.
9. **Check ids on the way back.** An agent may cite an id it was never shown: one it invented, or one from a sheet
   the budget dropped. Map answers through the items of the sheets actually delivered, and refuse other ids with the
   valid ones. Ids stay stable across sheets, so an id from an earlier delivered sheet is fine.
10. **Agents use what carries the work.** In the 39-agent study, `look` (223 calls), `sheet` (161) and `crop` (153) did
   the work; documented views and charts that were never shown in examples were never used. Put the evidence tools in
   the helpers and examples agents copy.

## Variations

- **Labelled grid instead of item marks.** Overlay a lettered grid and let the agent name cells. Works when there are
  no candidate items yet; coarser than ids.
- **Numbers only.** Return measurements without pictures. Cheapest; fails when the decision depends on appearance
  (dust versus a star in the scene).
- **Pictures with a text description.** For models without vision, or as an accessible fallback: a caption that
  states what each cell shows in words.
- **Progressive zoom.** Start with an overview sheet, then zoom only on items the agent marks as uncertain. Saves
  budget on easy items; needs the agent to follow the protocol.

## Consequences

- \+ Positions and measurements are exact, because they never pass through vision.
- \+ Many more candidates fit into a fixed image budget.
- \+ Answers by id are easy to check, merge and score against ground truth.
- \+ Budget failures become warnings the agent can act on, not lost runs.
- − Someone must produce candidates as rows first; things no measurement finds will not be in any sheet.
- − Sheets need tuning (cell size, zoom, stretch, views) per domain.
- − Budgets cap evidence; an agent near its limit must decide with less.

## Known uses

- **Set-of-Mark prompting** (Yang et al., 2023) overlays numbered marks on image regions so that a vision model can
  refer to them by number, improving visual grounding.
- **Browser-automation agents** such as Playwright's MCP server give the model an accessibility snapshot with element
  references, so actions target references instead of pixel coordinates.
- **Contact sheets** in photography and film review lay out many frames, each labelled, for comparison in one view.
- **Human labelling tools** show numbered candidates for accept/reject decisions, as the dust project's review tool
  does for people.

## Related chapters

- [Chapter 4 · Reach-Declared Region Evaluation](04-reach-declared-region-evaluation.md): zooms and sheets are window
  requests.
- [Chapter 5 · One Eval Tool over a Scripted Session](05-one-eval-tool-over-a-scripted-session.md): pictures are
  delivered in the reply.
- [Chapter 9 · Sealed Agent Run](09-sealed-agent-run.md): the conversation budget is stated in the run's prompt.
- [Chapter 10 · Gated, Calibrated Triage](10-gated-calibrated-triage.md): answers by id are scored against controls.
- Classic patterns: **Proxy** (an id stands for the exact numbers), **Flyweight** (one sheet carries many items).
