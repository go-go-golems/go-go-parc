# CAM Software for Z1

- URL: https://chatgpt.com/c/6a7ba132-d84c-83ea-8b77-c5e9a3c45c31
- Created: 2026-08-11T22:25:06.701Z

---

> what are features of CAM software / and especially features that users love (hobbyists) I got a makera z1 and I want to make the best CAM software for it out there. 
>
> Be exhaustive, research, give me links to software, both commercial and opensource.

I’ll break this into three layers: what the Z1 actually needs, the CAM feature set hobbyists value most, and a commercial/open-source landscape with product links and design takeaways.

```json
{"system1_search_query":[{"q":"Makera Z1 official CAM software supported post processor Makera Z1"},{"q":"site:makera.com Z1 CNC specifications software CAM"},{"q":"site:makera.com Makera CAM Z1 software"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Planning CAM research**

I’m mapping major CNC CAM options across hobbyist and commercial use, then comparing official features with community reactions. I’ll prioritize current availability, pricing, workflows, strengths, limitations, and direct links.

**Planned CAM research**

**Searched 19 websites**

</details>

The Z1 is unusually software-relevant: it has 3-axis milling, optional rotary 4th axis, probing, quick tool changes, laser, and camera/control integration. So “best CAM for it” should probably be a **Z1-aware workflow product**, not just another generic G-code generator.

```json
{"system1_search_query":[{"q":"site:autodesk.com fusion 360 manufacturing CAM features personal use CNC official"},{"q":"site:vectric.com VCarve Pro features toolpaths official"},{"q":"site:carbide3d.com Carbide Create Pro features official"},{"q":"site:inventables.com Easel Pro features CNC official"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 11 websites**

</details>

A clear pattern is emerging from hobbyist discussions: users tolerate fewer advanced strategies if the software is fast, understandable, offline/perpetual, and hard to misuse. They repeatedly praise Vectric/Estlcam/Kiri:Moto for that; Fusion is praised for power but criticized for setup and learning overhead.

```json
{"system1_search_query":[{"q":"PixelCNC official features CAM CNC software"},{"q":"CamBam official CNC CAM features"},{"q":"F-Engrave official open source V carve CNC"},{"q":"dxf2gcode official GitHub open source CAM"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Building the research plan**

I’m researching Makera Z1’s capabilities alongside commercial and open-source CAM systems. I’ll compare hobbyist-loved workflows, automation, toolpaths, usability, pricing, machine compatibility, and opportunities for a standout Z1-focused product.

</details>

```json
{"open":[{"ref_id":"turn432675view1"},{"ref_id":"turn432675view5"},{"ref_id":"turn176216view1"},{"ref_id":"turn330173search1"},{"ref_id":"turn246238search0"},{"ref_id":"turn755368search0"},{"ref_id":"turn957230search0"},{"ref_id":"turn957230search1"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 23 websites**

</details>

```json
{"open":[{"ref_id":"turn330173search0"},{"ref_id":"turn330173search2"},{"ref_id":"turn963264search1"},{"ref_id":"turn963264search0"},{"ref_id":"turn963264search6"},{"ref_id":"turn815977search2"},{"ref_id":"turn815977search3"},{"ref_id":"turn963264search3"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 6 websites**

</details>

You have a good target machine for this because the Z1 already has the hardware ingredients that make **deeply integrated CAM substantially better than generic CAM**: 3-axis milling, optional rotary axis, probing, quick tool changes, camera/software integration, laser support, and a defined machine envelope. Makera Studio already tries to combine CAM, material presets, machine control, camera monitoring, firmware, and guided workflows, so simply recreating “pocket + contour + export G-code” will not be enough. citeturn205075view2turn205075view0

My product target would be:

> **“Bambu Studio / LightBurn simplicity, Fusion-quality machining concepts, Vectric-quality 2D workflows, and Z1-native probing/simulation/control.”**

Not a mini-Mastercam. The distinguishing feature should be that a hobbyist can go from STEP/STL/DXF → trustworthy toolpath → verified setup → machining with very few opportunities to destroy a tool, stock, clamps, or spoilboard.

## 1. What hobbyists appear to love

There isn't a rigorous quantitative survey here, so I would treat this as a synthesis of product capabilities plus recurring themes in hobby-CNC discussions. Recent discussions repeatedly praise **speed, simplicity, contextual help, low setup overhead, good simulation, ownership/offline use, and the ability to escape into advanced settings when required**. Estlcam gets specific praise for contextual hover explanations with pictures; Kiri:Moto for being quick, browser-based/offline and straightforward; Vectric for making users feel less likely to make machining mistakes; Fusion for power despite a much steeper learning curve. citeturn205075view4turn205075view5turn205075view6

| What users want | What that should mean in your product |
|---|---|
| **“Just make this part.”** | Import → select stock/material → auto-recognize machinable features → suggested operations → preview → cut. |
| **Good defaults** | A new user should not need to understand chip load, optimal load, ramp angle, smoothing tolerance, linking moves, etc. before their first cut. |
| **No mystery** | Every automatic value should have a `Why?` explanation. |
| **A trustworthy preview** | Actual removed-material simulation, not merely colored toolpath lines. |
| **Safety before Start** | Collision/limit/tool-reach/clamp/zero/stock checks. |
| **Fast 2D work** | Drawing → pocket/profile/drill/V-carve should take seconds. |
| **Minimal air cutting** | Track in-process stock across every operation. |
| **Feeds & speeds that don't suck** | Machine-, cutter-, operation-, and material-specific recommendations. |
| **Reusable knowledge** | Saved tools, materials, setups, clamps and complete machining recipes. |
| **Easy workholding/setup** | Probing and coordinate setup should be integrated into the CAM project. |
| **Easy two-sided jobs** | Flip instructions + registration holes/pins + verification. |
| **Great engraving/V-carving** | Hobbyists make signs, badges, boxes, inlays, text, gifts, PCBs, etc. |
| **Great rotary** | Especially important for your Z1 because the machine offers a rotary accessory. |
| **Offline/local operation** | Don't make internet authentication a requirement to machine something. |
| **Perpetual/free-friendly licensing** | Hobby users repeatedly complain about subscription dependence; both Estlcam and new MillMage emphasize licenses that keep working. citeturn519350view6turn519350view5 |
| **Cross-platform** | Mac matters substantially in hobbyist environments; browser/local-web architectures are attractive. |
| **Undo everywhere** | Including CAM-operation changes and stock/setup changes. |
| **Templates** | “1/8″ aluminum plate,” “walnut sign,” “PCB,” “two-sided Delrin part.” |
| **Useful errors** | “Your 3 mm cutter cannot reach this 14 mm wall without the shank contacting it,” not “Toolpath failed.” |
| **Progressive complexity** | Beginner surface + advanced controls, rather than showing 48 parameters immediately. |

One telling pattern is MeshCAM's entire positioning: load the model, provide minimal input, generate G-code. Vectric similarly emphasizes immediate previews and conventional woodworking operations, while Fusion represents the opposite end of the power spectrum with 2D through simultaneous 5-axis machining, probing, stock simulation and associative CAD/CAM. citeturn473920view1turn473920view0turn519350view4

---

# 2. The full CAM feature set I would design

### Import / geometry

Your baseline should be **STEP first**, not STL first, for mechanical parts.

Support:

- STEP / BREP solids
- STL
- OBJ / 3MF
- DXF
- SVG
- PNG/JPEG/bitmap → tracing/heightmap
- Gerber + Excellon for PCB work
- eventually IGES

When a user imports geometry, automatically detect:

- units
- open contours
- duplicate lines
- tiny edges
- self-intersections
- non-manifold meshes
- holes
- pockets
- bosses
- planar faces
- chamfers
- fillets
- slots
- engraving curves

This is where an integrated CAD kernel gives you an enormous advantage. Fusion's associativity is valuable precisely because machining references remain tied to design geometry instead of becoming dumb exported meshes. citeturn519350view4

Also include lightweight CAD. Do **not** try to build SolidWorks initially. Give users the CNC-specific primitives they continually need:

- rectangle/circle/polygon
- lines/arcs/bezier
- dimensions
- text
- boolean union/subtract/intersection
- offset
- fillet/chamfer
- trim/extend
- array
- mirror
- SVG editing
- dogbones/T-bones

MillMage is a particularly interesting reference here: LightBurn carried its familiar vector editing model into CNC and added CNC-specific geometry such as dogbones/T-bones. citeturn519350view5

---

## 3. 2D / 2.5D operations: absolutely nail these

These are disproportionately important for hobby CNC.

**Core operations**

- Facing
- Outside profile
- Inside profile
- Pocket
- Rest pocket
- Slot
- Engrave/trace
- Drill
- Peck drill
- Bore
- Helical bore
- Counterbore
- Countersink
- Chamfer
- Thread mill
- V-carve
- V-carve inlay
- Fluting
- Surfacing
- Raster engraving
- Image engraving

**Toolpath controls**

- climb/conventional
- inside/outside/center
- cutter compensation
- stepdown
- stepover
- finishing allowance
- dedicated finishing pass
- spring pass
- ramp entry
- helical entry
- plunge entry
- tangential lead-in/out
- tabs
- onion skin
- corner smoothing
- stay-down linking
- minimum retraction
- inside-before-outside ordering
- automatic operation ordering
- automatic pocket island detection
- open-contour machining

Vectric is worth studying extremely closely here. VCarve combines conventional profiling/pocketing/drilling/thread milling with V-carving, inlays, moulding/fluting, and 3D rough/finish workflows, all behind an interface specifically aimed in part at small hobby CNC machines. citeturn473920view0

Also study **F-Engrave**. It is narrow, but its V-carving/inlay feature set is excellent inspiration for a hobby CAM product: text, images, DXF, V-carving, ballnose “B-carving,” straight-bit cleanup and inlays. citeturn444686view5

---

# 4. Adaptive/trochoidal roughing should be first-class

For metal on a relatively small desktop machine, this is more important than adding 25 obscure finishing strategies.

The desired behavior is approximately constant cutter engagement rather than repeatedly burying the cutter in corners. Fusion calls this adaptive clearing; Estlcam provides trochoidal milling; Onshape CAM similarly describes adaptive paths around constant chip load/cutter engagement. citeturn519350view4turn519350view6turn473920view7

For the Z1, make it absurdly simple:

**Rough Pocket → Efficient**

Then internally calculate sensible:

- radial engagement
- axial depth
- entry helix
- corner behavior
- engagement smoothing
- feed reduction for ramps
- minimum remaining island
- stock-to-leave

An expert can expand the operation and override everything.

---

# 5. Stock awareness may be one of your killer features

Maintain a **global evolving stock model**.

After operation 1, operation 2 knows what material is gone.

After tool 1, the smaller tool knows exactly which corners remain.

After setup 1, setup 2 starts from the actual remaining stock.

This enables:

- rest machining
- no repeated air cuts
- remaining-material heatmaps
- better estimated time
- automatic selection of smaller cleanup tools
- collision checking against actual stock

Onshape CAM explicitly maintains in-process stock and uses it for rest/re-machining, while MillMage already offers rest pockets. citeturn473920view7turn519350view5

I would expose this visually:

**Remaining stock**

> Red: >1.0 mm  
> Orange: 0.3–1.0 mm  
> Yellow: 0.05–0.3 mm  
> Green: finished

That makes CAM comprehensible even to someone who doesn't know CAM terminology.

---

# 6. 3D machining

Once 2.5D is excellent, add:

**Roughing**

- 3D adaptive
- offset rough
- raster rough
- rest roughing

**Finishing**

- parallel
- waterline / constant-Z
- scallop
- steep-and-shallow
- radial
- spiral
- pencil
- flat-area finishing
- contour
- projection onto surface

Important controls:

- machining boundary
- avoid boundary
- touch/avoid surfaces
- stock-to-leave
- tolerance
- smoothing
- min/max slope
- contact point boundary
- cusp-height driven stepover

Makera CAM already supports STL reliefs and STEP-based 3D pocket operations, so merely adding STL rastering would not differentiate your product. citeturn205075view1

---

# 7. The Z1 rotary axis is a major opportunity

This is one area where I would try to **massively outperform Makera's own CAM**.

Makera currently presents its built-in fourth-axis CAM primarily around rotary relief machining. citeturn205075view1

You want several distinct modes:

### Wrapped machining

User draws flat artwork and wraps it around a cylinder.

Great for:

- lettering
- logos
- rings
- ornamental cylinders

### Indexed machining — 3+1

Machine at:

- 0°
- 90°
- 180°
- 270°

Or arbitrary indexed angles.

This makes four-sided mechanical components almost trivial.

### Radial features

Feature recognition should detect:

- radial holes
- flats
- pockets
- engravings
- slots

and automatically rotate A into position.

### Continuous four-axis machining

X/Z/A or Y/Z/A simultaneous motion.

Useful for:

- sculpture
- impellers-ish geometry
- handles
- chess pieces
- jewelry
- organic models

### Rotary-specific simulation

Actually display:

- chuck
- jaws
- tailstock
- rotary stock
- cutter
- holder

Detect:

- cutter/fixture collision
- holder/chuck collision
- workpiece/chuck collision
- axis overrotation
- useless unwinding
- unreachable regions

Incidentally, the community Z1/Fusion post was updated this month specifically to reduce useless A-axis spinning, illustrating exactly why a machine-aware rotary implementation matters. citeturn205075view3

---

# 8. Tool library: make this dramatically better than typical CAM

A generic CAM tool library asks users to enter 20 cryptic numbers.

Yours should start with:

> **Which bit did you put in?**

For Makera/Z1 users, ship exact presets for every common Makera cutter.

Tool types:

- flat endmill
- ballnose
- bullnose
- tapered ball
- V-bit
- engraving cutter
- drill
- chamfer
- thread mill
- surfacing tool

Record:

- diameter
- flute count
- flute length
- total length
- stickout
- shank diameter
- holder geometry
- corner radius
- included angle
- manufacturer
- part number
- material/coating

Then have **operation presets attached to the tool**.

Example:

**3 mm 2-flute carbide — 6061 aluminum**

> Conservative  
> Normal  
> Fast

Under Advanced:

> 18,000 RPM  
> 610 mm/min  
> 0.017 mm/tooth  
> 0.75 mm DOC  
> 0.6 mm WOC

And every derived number should explain itself.

---

# 9. Build a Z1-specific feeds-and-speeds engine

This could be one of your strongest advantages over generic CAM because you know the exact machine.

Generic CAM must accommodate machines ranging from a $400 router to a $500,000 machining center.

You don't.

Therefore model:

**machine + spindle + tool + stickout + material + operation**

and generate conservative limits for:

- RPM
- chip load
- feed
- plunge feed
- ramp feed
- axial DOC
- radial WOC
- maximum engagement
- finish allowance

Add warnings such as:

> This cut is aggressive for a 2 mm cutter on a Z1.

> At this stickout, the tool may deflect excessively.

> Your flute length is 8 mm but the selected wall is 11.4 mm deep.

The interface should teach enough machining theory to create confidence without forcing users to become machinists.

---

# 10. Simulation should be treated as part of CAM, not eye candy

I would invest heavily here.

Show:

- cutter
- holder
- spindle nose if useful
- stock
- remaining stock
- finished model
- clamps
- fixture
- spoilboard
- machine envelope
- rotary chuck/tailstock

Detect:

- rapid through stock
- tool collision
- holder collision
- clamp collision
- fixture collision
- machine-travel violation
- cutter too short
- flute too short
- excessive engagement
- gouges
- uncut material
- zero below the spoilboard
- accidental full-depth profile

Fusion and Onshape both treat verification/collision checking as substantial CAM capabilities; CAMotics exists almost entirely around the value of simulating G-code before risking the actual machine. citeturn519350view4turn473920view7turn444686view7

### Then build a **Preflight** button

Before Send:

> ✓ Tool fits geometry  
> ✓ Tool reaches full depth  
> ✓ No holder collision  
> ✓ No clamp collision  
> ✓ Within Z1 travel  
> ✓ Stock dimensions match setup  
> ✓ Work zero defined  
> ⚠ Final profile will release the part  
> ⚠ Only 1.2 mm of material remains under pocket  
> ✓ Estimated runtime 18m 42s

This could be one of the features users end up loving most.

---

# 11. Setup/probing should be part of the CAM project

This is another place where traditional CAM UX is poor.

Don't merely output G-code and then make the user manually reproduce your coordinate assumptions in another application.

The project should contain:

**Workholding**

- vise
- clamps
- double-sided tape
- fixture plate
- soft jaws
- spoilboard
- rotary chuck

**Origin**

- front-left-top
- center-top
- selected model point
- fixture coordinate
- probed bore
- stored fixture origin

**Probe strategy**

- top
- corner
- XY center
- circular bore
- stock dimensions
- registration holes

Then the software executes that same setup.

Makera Studio already integrates machine control and connectivity, so this is an area where any Z1-specific competitor should go deeper rather than reverting to a generic “save NC file” workflow. citeturn205075view2

---

# 12. Camera-assisted setup could be genuinely differentiated

The Z1 software ecosystem already includes camera monitoring. citeturn205075view2

Go further.

Imagine putting scrap stock in the Z1 and seeing the live image underneath your CAM scene.

Then:

**Detect stock → overlay model → position job**

Use the camera for:

- stock boundary detection
- visual job placement
- clamp marking
- fixture recognition
- previously-cut feature registration
- PCB alignment
- printed artwork alignment
- “does reality approximately match CAM?” verification

Eventually:

> “I expected a 100 × 80 mm blank. Camera estimate is 99.8 × 79.9 mm.”

Or let the user click two known points in the camera image to register the coordinate system.

That is very close to the sort of direct physical/virtual alignment that could make desktop CNC feel dramatically more approachable.

---

# 13. Two-sided machining should be nearly automatic

This is another hobbyist pain point.

User chooses:

**Two-sided job**

Software:

1. chooses/suggests registration pins;
2. creates registration-hole toolpath;
3. machines side A;
4. gives an animated flip instruction;
5. probes/registers side B;
6. checks that the observed orientation makes sense;
7. resumes.

MeshCAM's “Quick Flip” concept is worth studying specifically because it recognizes how error-prone flipping workpieces is for inexperienced users. citeturn957230search26

---

# 14. First-class V-carving and inlays

Do not treat these as obscure woodworking operations.

Hobby users love making:

- signs
- cutting boards
- logos
- plaques
- badges
- gifts
- decorative boxes

Implement:

- V-carve
- prism carve
- V-inlay
- auto male/female inlay
- glue-gap control
- finishing allowance
- pocket-clearing with flat tool
- rest cleanup
- text-on-curve

Vectric and F-Engrave are especially worth studying here. citeturn473920view0turn444686view5

---

# 15. PCB milling

The Z1 is sufficiently precise and Makera already positions its software around PCB workflows, so I would support PCB work eventually. citeturn205075view0

Features:

- Gerber
- Excellon
- isolation routing
- board cutout
- drilling
- copper clearing
- V-bit isolation
- automatic probing grid
- warped-board height compensation
- solder-mask-ish laser workflow where applicable

Study **FlatCAM** particularly closely: it takes Gerber/Excellon, creates isolation/tooling paths and exports G-code. citeturn444686view4

---

# 16. Projects should be portable “manufacturing recipes”

Do not save merely:

`part.step`

and separately:

`part.nc`.

Invent a project package, perhaps `.zcam`.

It should contain:

```text
geometry
machine = Makera Z1 Pro
firmware compatibility
stock
material
fixture
work offset
tools
tool holders
operations
feeds/speeds
probe procedure
camera registration
simulation state
setup screenshots
estimated time
generated G-code
postprocessor version
project notes
```

Then someone sends me `phone_stand.zcam` and I get:

> Designed for Z1  
> 6061 aluminum  
> 3 mm + 1 mm endmills  
> 2 setups  
> 38 minute estimated machining time

And:

**Open → inspect → machine.**

Easel's copyable project gallery and Makera's own project ecosystem show the appeal of moving beyond isolated G-code files toward reusable complete projects. citeturn473920view4turn205075view2

---

# 17. “Beginner mode” and “Expert mode” should be the same engine

Don't build separate programs.

### Make mode

User sees:

> Material: Aluminum 6061  
> Stock: 80 × 50 × 8 mm  
> Quality: Normal  
> Tools: Auto  
>  
> **Create machining plan**

Result:

> 1. Face — 3 mm flat  
> 2. Rough pockets — 3 mm flat  
> 3. Rest machine — 1 mm flat  
> 4. Drill holes — 2 mm  
> 5. Profile — 3 mm flat  
> 6. Chamfer — 90° V-bit

Then:

**Simulate**

**Machine**

### Expert mode

Expand operation 2:

```text
Adaptive roughing
Optimal load       0.58 mm
Maximum stepdown   0.80 mm
Feed               680 mm/min
RPM                18,000
Ramp angle          3°
Stock to leave     0.15 mm
Tolerance           0.01 mm
Smoothing           0.02 mm
...
```

Same generated path.

This avoids the fatal tradeoff between “beginner CAM” and “real CAM.”

---

# 18. Contextual documentation is a feature, not documentation

Estlcam users specifically praise hovering over a parameter and getting an explanation/picture. citeturn205075view5

Copy the concept aggressively.

Hover:

**Stock to leave — 0.20 mm**

and show a tiny animation:

```text
Model surface     │
                  │
roughing stops →  │ 0.20 mm
                  │
rough cut          │
```

Then:

> Leaves material for a later finishing pass.  
> Recommended Z1/6061 range: 0.10–0.30 mm.

Every CAM option should answer:

**What is this?**

**Why would I change it?**

**What can go wrong?**

---

# 19. Don't lead with AI

AI is useful, but I would make it an adviser rather than the core path generator.

Good:

> “How should I machine this?”

> “Why is this warning appearing?”

> “Make this faster but don't increase tool load.”

> “I care more about surface finish than runtime.”

> “Why did you choose a 2 mm cutter here?”

Bad:

> Black-box AI emits 80,000 lines of motion and hopes they're safe.

Your deterministic CAM kernel, simulator and rule engine should remain authoritative.

---

# 20. Software worth studying — commercial / proprietary

These are the products I would install and deliberately copy *ideas* from.

| Software | Study it for |
|---|---|
| **[Makera CAM](https://www.makera.com/pages/makera-cam)** / Makera Studio | Your direct baseline: 2D, STEP/STL 3D work, rotary relief, laser, material presets and integrated Z1 control. citeturn205075view0turn205075view1turn205075view2 |
| **[Autodesk Fusion](https://www.autodesk.com/products/fusion-360/features)** | The reference for integrated CAD/CAM, adaptive clearing, probing, stock simulation, setup management, 3D machining and advanced multiaxis. citeturn519350view4 |
| **[Vectric VCarve](https://www.vectric.com/products/vcarve/)** | Probably the most important UI reference for approachable 2D/2.5D CNC, especially signs, V-carving, inlays and woodworking. citeturn473920view0 |
| **[Vectric Aspire](https://www.vectric.com/products/aspire/)** | VCarve philosophy plus substantially more 3D/relief creation. |
| **[Estlcam](https://www.estlcam.de/)** | Extremely good reference for compact UI, contextual help, 2.5D, trochoidal cutting and integrated control. citeturn519350view6turn205075view5 |
| **[MillMage](https://lightburnsoftware.com/blogs/news/millmage-is-here)** | Very important new competitor. LightBurn-style design + CAM + machine control; pockets, profiles, drilling, rest pockets, dogbones, custom G-code. Launched February 2026. citeturn519350view5 |
| **[DeskProto](https://www.deskproto.com/)** | “CAM for non-machinists,” straightforward 3D plus 3/4/5-axis support. Very relevant to the Z1 rotary problem. citeturn519350view7 |
| **[MeshCAM](https://www.grzsoftware.com/)** | Minimal-input “I want a part today” philosophy. Excellent UX reference. citeturn473920view1 |
| **[Carveco Maker](https://carveco.com/carveco-software-range/carveco-maker/)** | Hobby/artistic CNC, integrated vector/art creation, machining strategies and simulation. citeturn473920view2 |
| **[Carbide Create Pro](https://carbide3d.com/carbidecreate/pro/)** | Good example of gradually adding 3D capabilities without exposing full industrial-CAM complexity. citeturn473920view3 |
| **[Easel](https://easel.inventables.com/)** | Extremely simplified design→carve workflow plus community projects and broad hobby-router support. citeturn473920view4 |
| **[PixelCNC](https://deftware.org/)** | Reliefs, images, V-carving, halftones, artistic machining and particularly its built-in interactive tutorial system. citeturn473920view5 |
| **[CamBam](https://www.cambam.info/)** | Lightweight traditional CAM; reusable CAM styles are an interesting concept. citeturn815977search1turn815977search30 |
| **[Onshape CAM Studio](https://www.onshape.com/en/features/cam-studio)** | Very clean modern reference for associative cloud CAD/CAM, adaptive paths, in-process stock, machine simulation and fixture collision checking. Its standard CAM Studio is currently in beta; Advanced multiaxis remains advertised as coming soon. citeturn473920view7 |
| **[RhinoCAM](https://mecsoft.com/products/rhinocam/)** | Feature recognition and CAD-integrated 2.5/3-axis workflow. citeturn134561search3turn134561search27 |
| **[SolidCAM](https://solidcam.com/)** | Study iMachining, feeds/speeds automation, stock awareness and aggressive elimination of air cutting. citeturn134561search0turn134561search12 |
| **[Mastercam](https://www.mastercam.com/)** | Industrial benchmark: machine simulation, Dynamic Motion, multiaxis, tool libraries. Don't copy its complexity. citeturn134561search21turn134561search29 |
| **[SprutCAM X](https://sprutcam.com/sprutcam/)** | Strong reference for machine-aware simulation and four-/five-axis machining. citeturn134561search10turn134561search22 |

If you only install **seven**, I would pick **Makera Studio, Fusion, VCarve, Estlcam, MillMage, DeskProto and Kiri:Moto**.

They collectively span almost the entire product-design space you're trying to understand.

---

# 21. Open-source CAM projects to study

Some are suitable as architectural inspiration; some might provide reusable code subject to their licenses. Pay close attention to GPL/AGPL obligations before incorporating source into a proprietary product.

| Project | Why it matters |
|---|---|
| **[Kiri:Moto / Grid.Space](https://github.com/GridSpace/grid-apps)** | Probably your single most interesting open-source reference. Browser-based CNC/laser/3D-print slicer, installable locally, long-running project, MIT licensed. citeturn519350view3 |
| **[FreeCAD CAM](https://wiki.freecad.org/CAM_Workbench)** | Full open-source CAD + CAM architecture. Particularly worth studying for STEP/BREP-native workflow and post processors. The Z1 community now publishes FreeCAD support. citeturn205075view3turn444686view0 |
| **[OpenBuilds CAM](https://github.com/OpenBuilds/OpenBuilds-CAM)** / [live app](https://cam.openbuilds.com/) | Browser CAM converting DXF/SVG/bitmaps/Gerber to G-code. AGPL-3.0. citeturn444686view1 |
| **[Fabex CNC / BlenderCAM](https://github.com/vilemduha/blendercam)** | Blender-integrated CAM, especially interesting for artistic/3D work; active development and GPLv3. citeturn444686view2 |
| **[PyCAM](https://github.com/SebKuzminsky/pycam)** | Classic open-source 3-axis toolpath generator for STL/DXF/SVG; GPLv3. citeturn444686view3 |
| **[FlatCAM](https://flatcam.org/)** | PCB-specific CAM: Gerber, Excellon, isolation routing, G-code. citeturn444686view4 |
| **[F-Engrave](https://www.scorchworks.com/Fengrave/fengrave.html)** | Very worthwhile small codebase for engraving, V-carving and V-inlays; GPLv3. citeturn444686view5 |
| **[dxf2gcode](https://github.com/ltspicer/dxf2gcode)** | Focused open-source 2D DXF→G-code pipeline. citeturn444686view6 |
| **[jscut](https://github.com/tbfleming/jscut)** | Old but useful browser-based SVG/CAM architecture. It is more useful as code/history to study than as the basis of a new modern product. citeturn330173search3turn330173search6 |
| **[bCNC](https://github.com/vlachoudis/bCNC)** | Sender/control software with probing, autoleveling, editing and some CAM features. Great inspiration for the machine-control half. citeturn206684search2 |
| **[pcb2gcode](https://github.com/pcb2gcode/pcb2gcode)** | Current command-line PCB CAM; useful if PCB becomes a serious Z1 workflow. citeturn206684search1 |
| **[CAMotics](https://camotics.org/)** | Not really a CAM generator today; study its open-source 3-axis material-removal simulation architecture. GPLv2+. citeturn444686view7 |
| **[OpenCAMLib](https://github.com/aewallin/opencamlib)** | Particularly interesting to you as a developer: a C++ library focused on CAM algorithms/toolpath calculations rather than being a finished consumer app. citeturn206684search0 |

### Two repositories I would clone first

**Kiri:Moto** for product architecture/UI/toolpath generation:

[github.com/GridSpace/grid-apps](https://github.com/GridSpace/grid-apps)

It is MIT-licensed and explicitly exposes JavaScript slicing/G-code-generation APIs, which makes it especially interesting if you're considering a TypeScript/web/Electron architecture. citeturn519350view3

And:

**OpenCAMLib**

[github.com/aewallin/opencamlib](https://github.com/aewallin/opencamlib)

for lower-level CAM algorithms. citeturn206684search0

Then study **FreeCAD CAM** for BREP/STEP architecture and **CAMotics** for simulation concepts.

---

# 22. Z1-specific resources you should grab immediately

The community postprocessor/profile project is extremely useful:

**[Carvera Community Profiles — GitHub Releases](https://github.com/Carvera-Community/Carvera_Community_Profiles/releases)**

The August 5, 2026 release explicitly added **Z1 support for FreeCAD and Fusion**, plus Fusion rotary fixes and rudimentary laser support. The release also distributes profile assets for multiple CAM packages. citeturn205075view3

Makera also maintains public GitHub projects:

**[MakeraInc on GitHub](https://github.com/MakeraInc)**

Their public repositories include profiles/controllers/firmware-related projects worth examining for protocol and ecosystem understanding. citeturn176216view0

Before writing a postprocessor from scratch, I would reverse-engineer/document:

```text
Z1 G-code dialect
program start/end requirements
tool-change sequence
probing sequence
A-axis conventions
homing
work offsets
spindle control
air/cooling outputs
laser switching
file-transfer protocol
job status protocol
camera protocol
pause/resume
error reporting
```

Build a **machine-adapter layer** so your CAM kernel knows nothing about Makera-specific G-code.

Conceptually:

```text
Geometry
    ↓
CAM operation graph
    ↓
Canonical toolpath
    ↓
Machine simulation
    ↓
Machine Adapter
    ├── Makera Z1
    ├── Makera Z1 Pro
    ├── Carvera
    ├── GRBL
    └── Generic postprocessor
```

Then the Z1 is merely the machine you support exceptionally well first.

---

# 23. Where Makera appears vulnerable

This is probably the most commercially useful part of the research.

Makera's current product direction is correct: all-in-one CAM/control, material library, guided workflows, automatic paths, camera and hardware integration. citeturn205075view2

But recent Z1 owner discussions contain recurring complaints about **documentation, onboarding and software maturity/bugs**. One beta user simultaneously described Studio as much easier and more “Bambu style,” while saying the beta was still buggy. These are anecdotal reports, not a representative user survey, but they're a strong signal. citeturn205075view7

That gives you a very specific opening:

**Don't win with 100 more checkboxes. Win with reliability + explainability + depth.**

I'd define your differentiation like this:

| Makera-ish approach | Your opportunity |
|---|---|
| Auto CAM | Auto CAM **with an explainable plan** |
| Material presets | Z1-calibrated machining model |
| Basic preview | Full stock-removal + collision verification |
| Rotary relief | Full indexed + wrapped + simultaneous rotary |
| General toolpaths | Stock-aware adaptive + rest machining |
| Camera monitor | Camera setup/registration |
| Beginner UI | Beginner UI + expert escape hatch |
| Machine control | CAM/setup/probing/control as one state machine |
| Project library | Reproducible machining recipe |
| Documentation | Interactive documentation built into each parameter |
| Cloud ecosystem | Offline-first local projects |

---

# 24. The feature I would obsess over: **“Can I safely make this?”**

Rather than:

> Generate G-code

have the primary workflow be:

```text
DESIGN
   ↓
PLAN
   ↓
VERIFY
   ↓
SET UP MACHINE
   ↓
MAKE
```

### PLAN

> Aluminum 6061  
> Z1 Pro  
> 80 × 60 × 10 stock  
>  
> Suggested plan: 5 operations  
> Tools: 3  
> Time: ~26 min

### VERIFY

> ✓ Geometry machinable  
> ✓ Tools available  
> ✓ No collisions  
> ✓ Machine travel okay  
> ✓ Stock sufficient  
> ✓ Fixture clear  
> ⚠ Part becomes unsupported after Op 5 — tabs added

### SET UP

> Install 3 mm flat endmill  
> Clamp stock as shown  
>  
> **Probe stock**

Then the software performs it.

### MAKE

Live representation of:

```text
Operation 2/5
Adaptive roughing

██████████████░░░░ 74%

12:38 remaining
Tool: T3 — 3 mm flat
Feed: 680 mm/min
Spindle: 18,000 RPM
```

That experience is much more important to a hobbyist than whether you have nine varieties of morph finishing.

---

# 25. Architecture-wise, I would separate five engines

```text
┌────────────────────────────────────────────────┐
│                  Application UI                 │
├─────────┬───────────┬──────────┬───────────────┤
│Geometry │ CAM engine│ Simulator│ Setup/control │
│ kernel  │           │          │               │
├─────────┴───────────┴──────────┴───────────────┤
│              Machine capability model          │
├────────────────────────────────────────────────┤
│       Z1 adapter / generic postprocessors       │
└────────────────────────────────────────────────┘
```

The **machine capability model** is particularly important.

For example:

```json
{
  "machine": "Makera Z1",
  "axes": ["X", "Y", "Z", "A"],
  "work_envelope": "...",
  "rotary": true,
  "probe": true,
  "quick_tool_change": true,
  "camera": true,
  "laser": true
}
```

Then operations advertise requirements:

```text
Wrapped engraving:
requires rotary

Automatic zero:
requires probe

Camera registration:
requires camera
```

That architecture lets you eventually become broader than Makera without sacrificing the excellent Z1 experience.

---

# 26. My development order

I would **not** start by implementing every CAM strategy.

### V0 — prove the machine path

DXF/SVG → profile/pocket → Z1 G-code → simulator → send to machine.

Prove machine communication and coordinate conventions.

### V1 — excellent 2.5D

Ship:

- STEP/DXF/SVG
- tool library
- material library
- facing
- profile
- pocket
- adaptive
- slot
- drilling
- engraving
- chamfer
- V-carve
- tabs
- rest machining
- stock simulation
- collision/preflight
- Z1 send/control
- probing

If those features feel exceptionally good, you already have a compelling hobby product.

### V2 — make setup magical

Add:

- camera alignment
- fixture model
- clamps
- two-sided jobs
- registration
- stored fixture origins
- project recipes
- better runtime estimation

### V3 — real 3D

Add:

- 3D adaptive rough
- parallel
- contour
- scallop
- pencil
- steep/shallow
- rest finishing

### V4 — own the Z1 rotary market

Add:

- indexed A
- wrapped toolpaths
- radial features
- continuous four-axis
- chuck/tailstock simulation
- automatic rotary setup/probing

This is where you could potentially have a dramatically better Z1 workflow than most hobby CAM packages.

### V5 — ecosystem

Then:

- PCB
- laser
- plugin API
- scripting
- community recipes
- public machine profiles
- custom postprocessors
- third-party machines

---

# 27. What I would explicitly **not** do initially

Don't build a giant CAD system.

Don't make cloud login mandatory.

Don't hide the generated machining plan.

Don't default to hundreds of parameters.

Don't require users to manually write postprocessors.

Don't trust STL when STEP topology is available.

Don't separate CAM, setup and machine state into unrelated concepts.

Don't add AI before deterministic simulation.

Don't optimize for professional machinists at the expense of someone machining their first aluminum bracket.

And especially:

**don't let “simple” mean “incapable.”**

That is arguably the biggest opportunity in hobby CAM. Some products are extremely capable but intimidating; others are pleasant but hit limits quickly. Recent hobbyist discussions describe essentially that tradeoff around Fusion versus Estlcam/Vectric/Kiri:Moto. citeturn205075view4turn205075view5turn205075view6

---

# 28. If this were my product spec

I'd make the headline:

> **Import a model. See how it will be made. Make it safely.**

And I'd judge every feature against four numbers:

**Time to first valid toolpath**

Target: `<60 seconds`

**Time to understand why CAM chose something**

Target: `<10 seconds`

**Number of manual machine-setup steps**

Drive toward zero.

**Probability of a beginner doing something catastrophic**

Drive toward zero.

The last one is the most important.

Makera can build the official CAM. Fusion can build the most comprehensive one. Mastercam can build the industrial one.

Your opening is to build the **most trustworthy CAM for a desktop CNC owner**.

And because you're starting with one specific machine, you get a luxury those companies don't: **you can know almost everything about the machine in advance**—its geometry, rotary configuration, probing procedure, accessories, feeds/speeds envelope, tool library and controller behavior. That's the basis for a genuinely better user experience rather than merely another toolpath generator. The Z1 community already supplying dedicated Fusion/FreeCAD machine profiles makes that ecosystem especially feasible to prototype against now. citeturn205075view3

