# Mackey Arena / SDAC — R3 source pass

R3 is a Mackey-only revision following the independent R2 7.9/10 review. It keeps the documented height estimates and existing photo-traced plan boundaries unchanged; it does not add further perimeter geometry or try to infer room divisions.

## Source-matched facade refinements

The HNTB photos were checked as directional facade evidence: [Purdue-2](https://www.hntb.com/wp-content/uploads/2019/10/Purdue-2.jpg) shows the broad ground-floor storefront, two upper brick-and-window levels, pale horizontal bands, and the curved lobby at the east end of the south frontage; [Purdue-3](https://www.hntb.com/wp-content/uploads/2019/10/Purdue-3.jpg) shows the two-storey curtain wall, entry, and stair. R3 moves the model lobby to that east/south end, leaves the upper third floor brick-and-window facade above it, adds the south-facing double-door panel, broadens the grade-level glazing, and varies upper windows between single and paired vertical openings. New meter-aligned per-face UV projection keeps the brick courses horizontal on each wall orientation. Exact bay and lobby dimensions remain schematic because the photo perspective is not a measured elevation.

The new close facade views are `after_facade_south.png` and `after_facade_detail.png`; they show the entrance location, two-floor glass lobby below the continuing upper floor, brick, ground glazing, varied upper windows and band courses. The source-to-model element mapping and limitations are itemized in `evidence_r3.json` and `R3_source_comparison.md`.

## Registration exhibit corrections

R3 corrected the orthophoto overlay to use the exact Web Mercator crop extent and pixel size in `orthophoto_export_metadata.json`, and now draws both visible low-roof traces. The exhibit includes a north arrow and a 50 m scale bar. `north_sdac_registration_detail.png` enlarges the SDAC seam and its relation to the larger red GIS composite boundary. The overlay remains a visual fit only: it does not report a survey residual, and the GIS source is still a composite envelope. Full transform, extent, aerial source, and precision limits are in `evidence_r3.json`.

The saved standalone asset was rebuilt from `build_mackey_arena_north_wing.py` and reopened in a separate Blender 5.2.3 process. `validation_r3.json` passes: 391 collection objects, 14 SDAC and 4 one-storey roof/floor components, all new parts parented to the existing root, the 3,594-face metre-UV brick mesh present, expected materials and roof/foundation objects present, and zero linked libraries. R3 did not change measured or estimated heights, the interior plan, or the previously documented court program.

---
# Mackey Arena / SDAC — R2 asset update and evidence record

This iteration updates only `modular/buildings/mackey_arena.blend` and Mackey-specific builder/evidence. It preserves the existing arena shell and its local asset origin. The new outline is not treated as a separately surveyed parcel: Purdue GIS FID 873 is a composite arena/additions envelope, so the SDAC and low-roof perimeter traces below remain photo-interpreted within that envelope.

## Current source evidence

- **Purdue Athletics**, [Mackey Arena facilities page](https://purduesports.com/facilities/mackey-arena), retrieved 2026-10-24: documents the adjacent three-level development center, oversized full-size practice court, and three breakout shooting areas.
- **DLZ**, [Purdue University Mackey Arena Expansion](https://dlz.com/projects/purdue-university-mackey-arena-expansion/), retrieved 2026-10-24: calls out the three-level SDAC and single-story additions around the arena perimeter; the project page includes a historical aerial.
- **HNTB**, [Purdue Athletics Complex exterior photo](https://www.hntb.com/wp-content/uploads/2019/10/Purdue-2.jpg) and [glazed atrium photo](https://www.hntb.com/wp-content/uploads/2019/10/Purdue-3.jpg), retrieved 2026-10-24: used to check the red-brick wing, vertical upper-level window rhythm, broad lower glazing, two-storey curved glass lobby, and visible interior stair. The photos establish architectural character, not survey dimensions.
- **Indiana Geographic Information Office**, [Indiana Current Imagery ImageServer](https://di-ingov.img.arcgis.com/arcgis/rest/services/DynamicWebMercator/Indiana_Current_Imagery/ImageServer), 2023 Tippecanoe imagery tile `in2023_29971887_06`, nominal 6-inch resolution, retrieved 2026-10-24. The downloaded, cropped frame and identify/export metadata are preserved as `indiana_orthophoto_2023.jpg`, `orthophoto_identify.json`, and `orthophoto_export_metadata.json`.
- **Purdue BuildingShapesZip4**, [FeatureServer layer 0](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0), feature FID 873 / `MACK`, WGS84 EPSG:4326. Its complete source snapshot is preserved in `mackey_footprint_source.json`.

## Plan registration and footprint interpretation

The GIS vertices use the project’s documented local approximation, `X=(longitude+86.9137)*111412.84*cos(40.4274°)`, `Y=(latitude-40.4274)*111040`, then subtract the assigned Mackey anchor `(-209.5900,671.8375)` m. For the image overlay the model-local coordinates are converted back to geographic coordinates, then Web Mercator EPSG:3857, and mapped into the ImageServer crop extent. The overlay is a visual registration check, not surveyed control. It shows the retained circular shell aligning with the 2023 dome and makes the visible north-wing roof seam and low perimeter roofs legible inside the larger GIS envelope. See `orthophoto_registration_overlay.png` and its input coordinates in `ortho_overlay_vectors.json`.

The SDAC trace in `mackey_roof_trace.json` follows the source composite’s northern lobe, simplified to eight corner points where the north-side roof seam is visible in the orthophoto. Its approximate plan bounds are X=20.25..61.37 m, Y=63.16..132.77 m in the asset frame. The separate east/southeast and west/northwest low-roof strips are traced only over visible roof segments and kept as one-storey masses, consistent with DLZ’s project description. Their room divisions and exact wall outlines are unknown; no extra perimeter additions are inferred beyond the visible strips. `mackey_roof_trace.json` preserves coordinates, derivation notes, and citations.

## Geometry and facade work

- Rebuilt an editable, flat-roofed three-level SDAC volume at estimated 14.3 m occupied-roof height, with interior floor slabs, roof membrane, limited rooftop equipment, and a photo-informed brick/stone/glass facade. The glazing bays use a wider continuous lower-level rhythm and narrower upper punched-window rhythm, based on HNTB’s project imagery. The brick material has real-scale procedural color and shallow mortar relief; glazing is translucent and the roof dark membrane rather than a blank pale cap.
- Added a segmented two-storey curved lobby glass wall with bronze mullions and a visible two-flight stair/landing. HNTB photos support the curved atrium/stair concept; the exact curvature, dimensions, and stair route remain interpretive because architectural plans were not available.
- Added two low-rise perimeter roof/floor strips (east/southeast and west/northwest traces), 4.6 m estimated one-storey height, with brick piers, glazing, bronze heads/sills and limestone-colored banding. The trace strips are partial source-visible evidence, not claims of a complete surveyed perimeter floor plan.
- Added the official full-size practice-court program and three small breakout shooting bays. The main court is 15.24 x 28.65 m; a restrained maple variation shader supports the floor. The program count is source-backed; court orientation, breakout bay dimensions, hoops, and room layout are model interpretations, not verified construction drawings.
- No undocumented canopy or additional building wings were introduced in this iteration.

## Saved-asset verification

`modular/buildings/build_mackey_arena_north_wing.py` rebuilds only the Mackey standalone asset. It removes and regenerates named `MACK_SDAC_*` / `MACK_PERIM_*` components idempotently, parents every generated component to `AssetRoot_mackey_arena`, and writes the blend file. The saved asset was reopened in a separate Blender 5.2.3 process. `validation_r2.json` records 391 collection objects, including 14 SDAC and 4 one-storey roof/floor objects, zero linked libraries, expected materials/objects present, and all added components parented to the existing root. Evaluated bounds are recorded there: existing shell X=-48.225..48.225, Y=-62.363..62.362, Z=0..27.9 m; new SDAC/perimeter geometry X=-61.042..67.369, Y=-72.409..133.195, Z=0.08..15.62 m. The added geometry’s full Z includes rooftop equipment; the occupied SDAC roof estimate remains 14.3 m and the perimeter addition estimate 4.6 m.

Saved-file inspection images:

- Exterior massing: `after_oblique.png`
- Plan footprint: `after_top.png`
- Roof-hidden practice-space view: `after_practice_interior.png` (roof is hidden only by the render script and remains in the saved asset)
- 2023 aerial registration: `orthophoto_registration_overlay.png`

## Limitations for independent grading

The GIS outline is still composite, and the photo-traced sub-footprints are not survey-certified. The approximate local projection and visual orthophoto fit support placement but do not establish sub-meter survey accuracy. The 14.3 m SDAC and 4.6 m perimeter heights are estimates; GIS `Extrution=47` has no published units/semantics. HNTB project photos support facade character but not the exact modelled bay spacing, finish color, entry dimensions, or interiors. The exact court orientation and breakout room arrangement remain unverified. Please grade those remaining limits explicitly rather than interpreting the additions as as-built survey geometry.

