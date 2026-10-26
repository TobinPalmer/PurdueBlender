# WALC R4 façade refinement

Date: 2026-10-25  
Asset: `modular/buildings/walc.blend`  
R3 reviewed base SHA-256: `c9ca2cfe413898780445bade8e729e22510535aed123407c4d11e5c28f53ec65`  
Final R4 SHA-256 after independent fresh reopen: `01f0ba7bd8fbdee2da267e85c8d35e327cf891d68a05cbeea5876b5b692b5dd4`

## Changes

- Replaced the R3 thin bronze facade blades with substantial brick wall fields on 29 long or visually important GIS-derived facade segments. Upper glazing bands (existing bands 4 and 6) now read as solid brick elevations with paired tall window groups, pale limestone jambs, sills and heads, and narrow bronze divisions. Ground-floor glazing remains visible between deeper brick piers aligned to the upper bay rhythm.
- Used the cached Purdue BuildingShapesZip4 FID 906 ring direction for each exterior normal. This handles concave corners locally and keeps the new cladding and frames inside the earlier R3 model envelope. The GIS roof object, traced outline and identity root were left unchanged.
- Strengthened the viewport brick/limestone/glass color separation. The existing procedural running-bond brick shader remains assigned to the brick fields; window and stone parts use the asset's existing reference materials.
- Kept the existing entrance canopy and glazed entrance composition. Its visible depth was already modeled; the available photo supports this broad form but not measured canopy dimensions. No unsupported entrance dimensions were added.
- Kept the roof and interior geometry unchanged. The official Purdue classroom-floor-plan PDF provides basement, first-, second-, and third-floor classroom arrangements and supports the modeled program categories; because the PDF was not scale-registered to this model, room positions and fit-out remain schematic and were not altered.

## Source evidence and uncertainty

- Purdue University, “[Then & Now: Wilmeth Active Learning Center](https://www.purdue.edu/newsroom/archive/purduetoday/releases/2018/Q4/then-and-now-wilmeth.html)” (2018-11-18) and the [official exterior photo](https://www.purdue.edu/uns/images/2018/pt-wilmeth-6446.jpg), retrieved 2026-10-25. The image supports red-brick wall fields, substantial piers, grouped tall rectangular windows, contrasting limestone surrounds, a distinct glazed entry, and a canopy. It does not give a measured elevation, bay schedule, window schedule, wall depth, or roof dimensions.
- Purdue, [WALC Classroom Floor Plans](https://www.purdue.edu/activelearning/walcrooms1/WALC_Classroom_FloorPlans.pdf), retrieved 2026-10-25. Compared all four published floor-plan sheets (basement and floors 1–3) as program/layout references; they were not registered to a measured survey of this asset.
- Purdue Office of Emergency Preparedness, [WALC Building Emergency Plan](https://www.purdue.edu/operations/emergency-preparedness/walc/), revision 2026-04-03; supports story count and listed program, not interior geometry.
- Facade window widths, heights, pier widths, and spacing are visual estimates made from the official exterior photo and the existing asset floor elevations. They are not survey dimensions. Roof edge/inset and level changes remain unverified against architectural drawings. The floor plans support program but not exact interior finishes/as-built partitions.
- Cached Purdue campus GIS BuildingShapesZip4 FID 906 in `audit/official_building_references.json` (retrieved 2026-10-22) was used to establish the outline winding and preserve the existing trace. It is the same source used during modeling, not independent wall-survey evidence.

## Fresh-open check

`independent_reopen_r4.py` opened the saved standalone asset in Blender 5.2.3 LTS and wrote `independent_reopen_r4.json`. The exact SHA-256 above was confirmed; `Asset_walc` contains 954 objects and 882 meshes. All mesh material slots are valid, there are no materialless meshes or missing external images, and the relative foliage library resolves. `AssetRoot_walc` retains identity transform. `WALC_Official_906_Roof` retains 156 vertices and its R3 bounds. The full R4 bounds remain inside the earlier R3 evaluated envelope. This standalone check does not verify master `Placement_walc` or nearby campus alignment.

Fresh daylight renders opened the saved file independently: `southwest_r4_daylight.png`, `southeast_r4_daylight.png`, and `north_r4_daylight.png`. The official photo snapshot is `purdue_wilmeth_2018_official.jpg`; the source floor-plan PDF is `WALC_Classroom_FloorPlans_official.pdf`.

**Scope:** only `modular/buildings/walc.blend` and WALC-specific files in `audit/walc_refine/` were changed. No master, shared files, README, or commit was touched. Independent R4 grading and master-context alignment remain for the coordinator.
