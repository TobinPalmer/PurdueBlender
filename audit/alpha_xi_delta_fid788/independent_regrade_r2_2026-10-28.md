# Alpha Xi Delta — independent regrade R2

**Reviewed:** 2026-10-28  
**Asset:** `modular/buildings/massing_house_301841248_fe939c7.blend`  
**Verified SHA-256:** `2F863554345DD260E2708F50225CFFD595B8C55A18E8C49E38B620698B4E30B7`  
**Result:** **8.65/10 — PASS** (project threshold: 8.0)

This is a read-only independent review of revision 2. I verified the exact SHA immediately before and during the review. I reopened the `.blend` in Blender 5.2.3 LTS and found the expected scene and named collection, one scene/collection mesh root (`House_301841248`, 18,299 vertices), no saved camera/light objects, and no missing image dependency. No Alpha Xi Delta asset or builder file was modified.

## Weighted score

| Category | Weight | Score / 10 | Weighted points | Evidence and limits |
|---|---:|---:|---:|---|
| Identity and provenance | 20% | 9.5 | 1.90 | GIS FID 788 directly names Alpha Xi Delta at 519 University St; official Purdue chapter material and a dated 2008 Purdue house image corroborate identity. Source photos support the Tudor/brick house. The auxiliary illustrated drawing is correctly treated as secondary. |
| Plan geometry and placement | 25% | 9.0 | 2.25 | Saved source ring has 24 points; source-to-root max vertex error is 0.00001569 m, and comparison bounds/area/perimeter closely agree. This is a same-source-by-construction coincidence using the project's approximate transform, not independent geodetic placement or survey validation. |
| Exterior silhouette and openings | 25% | 7.8 | 1.95 | R2 closes the previously conspicuous unsupported roof opening. The exterior reads as a substantial gabled Tudor house, with three dormers, upper timber, brick lower story, windows and a marked entry. Roof planes/transitions remain broad and simplified; exact opening rhythm, dimensions, height, and hidden elevations are not established by the sources. |
| Materials and facade | 10% | 8.5 | 0.85 | Brick, ivory/cream wall material, dark timber, slate roof, trim and blue-gray glazing form a coherent palette aligned with the saved photos. Procedural surfaces and some facade details remain stylized. |
| Interior and cutaway clarity | 10% | 7.5 | 0.75 | Cutaway is now clearly labeled “SCHEMATIC INTERIOR - NOT AN AS-BUILT PLAN” and shows partitions and furniture placeholders. It is sparse, lacks a sourced floor plan, and does not verify room count, uses or circulation. |
| Presentation and technical | 10% | 9.5 | 0.95 | Independent fresh-open confirmed the exact SHA, stable scene/collection/root, one scene and collection object matching the manifest contract, no saved cameras or lights, and no external image dependencies. Technical/packaging presentation is clean. |
| **Total** | **100%** |  | **8.65/10** | **PASS** |

## Remaining limitations

The asset is a detailed illustrative model rather than a surveyed as-built reconstruction. Roof pitch/ridge, heights, window spacing, all unseen sides, and interior arrangement remain estimated or schematic. The GIS `NUM_LEVELS=1` and `Extrution=12` fields do not resolve building height or story count; the latter is undocumented. Footprint matching is by construction and does not independently verify placement. The R2 roof closure and one-object collection contract address the two primary R1 findings.

## Evidence reviewed

- `review_handoff.md`, `revision_report_r1.md`, `revision_report_r2.md`, `model_evidence.json`, `source_fid788.json`, `footprint_comparison.json`, and `footprint_overlay.svg`.
- `exterior_preview.png`, `interior_cutaway_preview.png`, `facade_reference_current.png`, `facade_reference_2008.png`, and `illustrative_house_art.jpg` (secondary illustration only).
- `fresh_open_validation.json` plus an independent read-only Blender 5.2.3 LTS open of the exact saved SHA. Result: one scene object / one collection object, 18,299 root vertices, zero cameras/lights, zero external image dependencies.

No shared project, Alpha Xi Delta asset, or builder file was modified in this review.
