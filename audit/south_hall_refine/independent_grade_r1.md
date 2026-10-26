# South Hall R1 independent review

**Score: 7.8/10 — below the 8.0 pass threshold.**  
**Asset reviewed:** `modular/buildings/south_hall.blend`  
**SHA-256:** `9a848c6140c3abc6c6a1d7c7daa9d8c176d7a0452c3c489d56672812c573c410`  
**Fresh reopen:** Blender 5.2.3 LTS; 22 collection objects, 21 meshes, 27 materials; identity asset root; no materialless meshes or external image dependencies.

## Scorecard

| Criterion | Score | Assessment |
|---|---:|---|
| Identity, plan footprint, and local frame | 1.9/2.0 | The asset is identifiable as the new South Hall. The full 53-vertex simplified Purdue GIS FID 528 outline is retained, and the reopened base boundary overlays it to within about 2.24 µm. This confirms the build transformation against the same source boundary; it is not an independent survey or proof of the exterior wall line. Root remains identity. |
| Vertical massing, connector, and roof | 1.5/2.0 | The main residential mass reads as eight floors, and the north dining/link arm is kept low instead of being extruded to residential height. This follows the Purdue site-plan color distinction. The Y=5 m split is an estimate from a non-georeferenced plan; the 14/10-foot floor rhythm is inferred from unitless GIS fields; absolute height, roof depth, and roof construction remain unverified. |
| Exterior facade, entrance, and materials | 1.4/2.0 | Procedural brick, repeated framed glazing, glazed ground level, a recognizable entry, and a restrained textured roof establish the right broad character. The exterior remains schematic: window rhythm is very regular, the photographed tall glazed vertical bay/atrium is not clearly reproduced, and roof/eave articulation and facade variations are sparse. Construction imagery is not an elevation survey, so the precise window schedule remains unverified. |
| Interior and amenities | 0.9/1.5 | The asset contains eight floor plates and representative Data Mine labs, dining/lounge/game amenities, and one sample double room. Purdue supports those broad uses, but not their exact locations. The cutaway view reads more like scattered sample modules than a coherent ground-floor plan; repeated floor layouts, circulation, stairs/cores, partitions, and room-to-room relationships are not demonstrated. |
| Source evidence and uncertainty handling | 1.2/1.5 | Provenance is unusually clear: Purdue GIS FID 528, raw GeoJSON, the 2023 Trustees site plan, current Purdue housing pages, and 2026 imagery are retained with dates, CRS, methods, and uncertainty. The site-plan-to-GIS partition and the interpretation of GIS floor fields as feet need to remain explicitly estimated. |
| Saved file, materials, and portability | 0.9/1.0 | An independent fresh reopen confirmed the expected hash and collection, material coverage, identity root, and no external images. The very low object count for an eight-story residence hall means much of the facade/interior detail is aggregated or schematic, which limits independent inspection. |
| **Total** | **7.8/10** | **Does not meet the 8.0/10 pass threshold.** |

## Main corrections before another review

1. Make the main facade closer to the current Purdue exterior evidence: add the distinct full-height glazed bay/atrium where supported, vary window groupings and lower-level treatment, and avoid implying a precise schedule that the available photo cannot establish.
2. Make the cutaway read as an interior: show the ground-floor public spaces as a connected, legible arrangement with a clear lobby/circulation path and representative partitions/furniture. Keep every room placement labeled schematic unless an as-built plan is obtained.
3. Clarify the transition between the residential wing and the low dining connector in oblique views, while retaining the uncertainty in its estimated split and endpoint.
4. Keep roof membrane seams subtle and render a sourced parapet/equipment condition only if a current image or drawing supports it. The current flat roof profile and heights remain unverified.
5. At coordinator integration, independently reopen the complete master and verify the `Placement_south_hall` marker against the manifest; this standalone review did not inspect the master.

## Evidence and review limits

- Builder record: `BUILD_RECORD_R1.md`; builder validation: `validation_r1.json`.
- Independent fresh reopen: `independent_reopen_r1.json`, created from the exact saved asset.
- GIS overlay: `official_footprint_vs_asset_r1.png`; it verifies a generated mesh against the same GIS polygon, not an independent measured wall survey.
- Visuals inspected: `south_hall_oblique_full_r1.png`, `south_hall_human_scale_east_entry_r1.png`, and `south_hall_schematic_ground_floor_cutaway_r1.png`.
- Source snapshots inspected: `raw_south_hall_fid528.geojson`, `purdue_board_hillenbrand_south_siteplan_2023.pdf`, `purdue_southhall_exterior_construction_2026.jpg`, and `purdue_southhall_mainfloor_2026.jpg`.
- No master marker, master blend, manifest, or shared index was changed or independently validated in this asset-only review.
