# Ray W. Herrick Laboratories (2013) — R2 review candidate

## Scope and identity

This is Purdue GIS `FID=878`, abbreviation `HLAB`, the 2013 68,000 sq ft research building at 177 S Russell Street. It is not the adjacent historic Herrick Acoustics / `HERL` GIS `FID=246`. R2 preserves the asset collection and every retained object's existing asset-local transform, and uses the same exact 58-point local GIS footprint, with no footprint or campus-origin edits. The signed footprint area is 2,593.797198 m².

The original assigned asset and README grade (7.2/10) were left untouched. The candidate is separate: `ray_w_herrick_r2_candidate.blend`.

## Changes in this candidate

- Replaced the generic solid prism facade with punched wall panels over the exact GIS outline, modelled glazing, facade framing, brick piers, pale metal spandrels, and a graphite high-bay elevation.
- Reoriented the main entry to the documented south facade and added entry glazing, canopy, steps, walk, sign, and low planting cues.
- Added a connected schematic corridor, stairs/elevator cues, partition walls, office work surfaces, and research test-rig silhouettes. Room layouts and furniture are use-based interpretation, not surveyed as-built interior documentation.
- Added procedural brick, pale metal, graphite, glazing, aluminum, concrete, painted interior, and interior-glass materials.
- Removed one inherited over-height west/north volume that obscured the documented elevations and had no corroboration in the consulted 2013 exterior photo or 2011–12 published south/east elevations. Roof equipment remains schematic.

## Evidence and uncertainty

Sources accessed 2026-10-25:

1. Purdue News Service, “Purdue's new Herrick Labs building open for business,” 2013-10-31, with exterior photograph credited to Purdue University / Mark Simons: <https://www.purdue.edu/newsroom/archive/releases/2013/Q4/purdues-new-herrick-labs-building-open-for-business.html>. Image: <https://www.purdue.edu/uns/images/2013/herrick-newbuilding.jpg>. Local evidence copy: `source_purdue_herrick_newbuilding_2013.jpg`.
2. Purdue Herrick Laboratories, 2011–12 annual report, p. 15, including design renderings of the south and east elevations and first/second/third floor diagrams: <https://engineering.purdue.edu/Herrick/information/AnnualReports/2012%20fall.pdf>. Local page image: `source_purdue_annual_report_page15.png`.
3. Purdue Herrick visitor information, stating the main entrance faces south and visitors enter on level 2: <https://engineering.purdue.edu/Herrick/AnnualReport/information/visit>.
4. Purdue Herrick facilities page: <https://engineering.purdue.edu/Herrick/about/facilities>.
5. Official campus building-shape service, BuildingShapesZip4 layer 0, feature 878; source feature and coordinate-transform details are documented in `audit/batch_b_buildings/ray_w_herrick_laboratories_evidence.json` and its referenced raw GIS snapshot.

The official opening photo supports brick piers, light metal cladding, a glazed upper office/living-lab band, a dark graphite high-bay volume, and a south-side glazed entry. The 2011–12 annual report is a design-stage source, so it may differ from the final as-built condition. Exact wall heights, window module dimensions, door and canopy dimensions, furniture, roof equipment, room layout, and high-bay internal arrangement remain approximate. A single opening photo and design elevations do not establish every facade detail. No Google Maps imagery was treated as measured evidence.

## Validation

- Built from the assigned `.blend` in Blender 5.2.3 and saved as an isolated candidate.
- Reopened the candidate in fresh Blender background processes; the expected preview camera rendered, and the asset collection contains 80 objects with 17 used materials. The output renders came from the reopened file.
- South elevation render: `south_r2.png`; 3/4 preview render: `preview_r2.png`.
- Candidate SHA-256: `5dfe15ad317dad3661fab756b312e2d0ce2de9b64b53bb3ecb0523a93525bbbf`.
- Blender save report: GIS ring vertex count 58; signed footprint area 2,593.797198 m²; entry center local XY `[-3.6410837087, -33.9021873474]`.

This is a source-informed R2 candidate for independent grading, not a claim that the building has reached a particular quality score. During candidate authoring, the original modular building library, master scene, manifest, README, and Git history were not changed. After the standalone candidate passed, the coordinator copied it byte-for-byte into the assigned library and integrated it into the master; see the coordinator integration record below.

## Coordinator integration

The independently graded R2 candidate was copied byte-for-byte into `modular/buildings/ray_w_herrick_laboratories.blend`; its SHA-256 remains `5dfe15ad317dad3661fab756b312e2d0ce2de9b64b53bb3ecb0523a93525bbbf`. In the master, `Placement_ray_w_herrick_laboratories` matches the manifest XY origin `[-531.9590659304099, -569.0631943790936]` within 0.000031 m. The updated 80-object linked collection reopened in the full master with 69 placement markers and a project-relative library path. See `audit/master_sync_r21.json` for the saved/reopened integration check. This confirms marker agreement with the manifest, not surveyed campus placement accuracy.
