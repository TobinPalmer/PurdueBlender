# Purdue University Daniel Turf Center (DANL)

Stable ID: `massing_purdue_university_daniel_turf_center_e69b7da`  
Owner: Rossen (README assignment; massing-only queue item)  
Manifest asset: `modular/buildings/massing_purdue_university_daniel_turf_center_e69b7da.blend`  
Build script: `modular/buildings/build_massing_purdue_university_daniel_turf_center_e69b7da.py`

## Identity and source geometry

The asset is Purdue BuildingShapes feature **FID 208 / DANL**, “William H. Daniel Turfgrass Research & Diagnostic Court,” at **1340 Cherry Lane**. The Purdue HLA facility page independently confirms the Daniel Turf Center identity and address. The stale assignment screen's FID 855 is rejected: the campus index identifies 855 as the Old Purdue Exponent Building. TREC is a separate RecWell facility.

The FID 208 ring is retained using the modular project's approximate local coordinate transform. The resulting bounds are X −1408.480 to −1363.876 m, Y 1609.489 to 1627.130 m; the local ground-scale polygon area is approximately 677.06 m². Aerial overlay shows the ring tracking the roof projection. A measured wall line and roof overhang offset are unavailable, so the footprint is not claimed as a surveyed wall boundary.

The previous area conflict was a CRS comparison error. The source ring in native EPSG:3857 has shoelace area **1170.6289 m²**, matching `Shape__Area=1170.6211 m²` within **0.0078 m²**. The roughly 677.06 m² area comes from the latitude-corrected local ground coordinate approximation; Web Mercator area is larger at this latitude. Both measurements are retained with their CRS context.

## Form, direct evidence, and uncertainty

The attached 2011 J&D Turf visit report explicitly identifies its photograph as the Daniel Center building exterior (`sources/daniel_center_exterior_2011_janddturf.jpg`). It directly supports a long, low, single-story building with light metal cladding, a shallow gable, a centered entrance canopy, and a horizontal window band. The model uses pale metal siding and roof materials, a dark long window-band material, and a simple centered shallow-gable canopy. It does not infer individual window divisions, door geometry, or additional facade ornament.

The photographed long elevation is mapped to the south-facing long side (negative Y). This is an inference, not a compass reading from the photograph: the north-up aerial places the parking apron south of the building, and the centered 4.23 m × 2.35 m south-side GIS roof-outline bump aligns with the centered canopy/entrance in the photograph. The long GIS axis is X. The GIS roof-outline ring remains the exact plan extent; the main wall outline bridges the centered bump, and the canopy restores the exact outer extent. A surveyed wall line or eave overhang is unavailable.

The photograph supplies no calibrated dimensions, and no measured elevations were found. `Extrution=14` has undocumented units and is preserved only as an uninterpreted source value; it does **not** set the Blender height. Eave and ridge Z dimensions, band height, and canopy vertical dimensions are low-confidence visual estimates, not surveyed facts. Exact pitch, facade dimensions, compass orientation, wall line, and overhang remain uncertain. Purdue's expansion flyer and Synthesis feasibility renderings are proposals and are not used as as-built evidence.

## Evidence and validation

- `sources/`: GIS identity and native CRS queries, GIS metadata, Purdue facility page, World Imagery export and overlay, direct exterior photo, proposed expansion reference, and `source_register.json`.
- `renders/daniel_turf_center_top.png` and `renders/daniel_turf_center_oblique.png`: revised Blender preview views.
- `build_result.json`: measured plan bounds, area reconciliation, evidence and known conflicts.
- `r2_iteration_notes.md` and `r3_iteration_notes.md`: changes from independent review and supporting evidence/method for each revision.
- `reopen_check.py` and `reopen_validation.json`: separate clean-process Blender reopen validation.
