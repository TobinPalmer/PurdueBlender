# Independent grade: Phi Kappa Psi / Indiana Delta

**Result: 7.8/10 — REVISE; not accepted.**  
**Asset reviewed:** `modular/buildings/phi_kappa_psi_fid856.blend`  
**SHA-256:** `56be1525245176d5d7f64ce4560384cde8e25816f9a3627fe36c1b6b31120226`  
The hash matches the builder's fresh-open validation, so this grade applies to the current saved asset.

## Score breakdown

| Criterion | Score | Weight | Assessment |
| --- | ---: | ---: | --- |
| Identity, site evidence, and source crosswalk | 9.0 | 5% | Current chapter contact page and national chapter report independently identify 1307 Tower Drive as Indiana Delta. Purdue FID 856 has the same address and Greek ownership but a conflicting Phi Kappa Tau name; the report records this. |
| Footprint and local placement | 9.0 | 20% | The asset uses the FID 856 wall polygon and documented local centroid. Dimensions are about 34.74 × 28.28 m; the render footprint is close to these. The larger OSM outline is appropriately treated as roof/eave extent rather than ground-floor wall geometry. |
| Overall massing and roof silhouette | 7.8 | 20% | The long three-to-four-level Georgian residence and central portico are recognizable. The front reads well, but the simplified rear misses the prominent roofed/gabled central bay visible in contractor photo 3. The roof is otherwise a broad generic hip form, with roof and story heights estimated. |
| Facade composition and architectural detail | 8.0 | 20% | Front portico, pediment, balcony, columns, brick field, and repeated double-hung windows capture the main identity. The rear central bay is too blank and sparsely fenestrated compared with the source photo; fine trim, rain leaders, and some service features are generalized. |
| Materials and texture | 8.2 | 15% | Brick and roof use procedural materials with visible surface variation and no external texture dependencies. The brick pattern is somewhat regular and the photos are monochrome, so the red-brown hue is plausible but not directly color-verified from the supplied contractor images. |
| Interior | 4.5 | 15% | Interior contents are only a stair flight and rails, one foyer floor, three floor plates, a sofa, a table, and a bookcase. There are no room partitions, landings, or developed upper floors. This falls short of the available lobby/stair and lounge photographs (contractor photos 5–6) and the project's requested interior quality, even allowing for an explicitly schematic plan. |
| Asset portability and reopen integrity | 10.0 | 5% | Blender 5.2.3 fresh-open validation succeeded. The expected scene and collection exist, with 580 collection objects, 12 procedural materials, and no external image references. |

Weighted result: **7.8/10** (7.815 before rounding).

## Required revisions before acceptance

1. Refine the rear central bay from contractor photo 3: model its projecting proportions, roof/gable treatment, upper window rhythm, and lower-level openings so the rear no longer reads as a plain white box with two windows.
2. Use contractor photos 5–6 to build a recognizable entrance lobby/stair and lounge. Add a plausible stair landing/guard, foyer floor treatment, and more complete furnishings; add simple partitions or room boundaries and meaningful floor-to-floor circulation so the three upper plates do not imply empty slabs. Keep the plan labeled schematic unless a sourced floor plan is found.
3. Re-render front, rear, and at least one interior cutaway after revision, then rerun fresh-open validation and record the new asset hash. A revised grader should score that exact hash.

## Evidence reviewed

- Builder's source and measurement record: `audit/phi_kappa_psi_fid856/evidence.md`, `gis_crosswalk.json`, and `source_register.json`.
- Purdue FID 856 snapshot and aerial overlay, including the noted legacy GIS name conflict.
- C.F. Jones Group project gallery photos: front (`photo_1.jpg`), rear (`photo_3.jpg`), lounge (`photo_5.jpg`), and lobby/stair (`photo_6.jpg`), along with the contact sheet.
- Builder front, aerial, and rear renders in `audit/phi_kappa_psi_fid856/renders/`.
- `fresh_open_validation.json`, including asset SHA, evaluated bounds, collection inventory, materials, and external image references.
- Read-only Blender 5.2.3 inspection confirmed the interior consists of 23 schematic objects, mostly stair treads/rails and three floor plates, with no interior wall or room-partition objects.

No changes were made to the asset or shared project files.
