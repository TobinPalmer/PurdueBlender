# Independent grade — Purdue Memorial Union R1

**Result: 7.7 / 10 — below the 8/10 pass threshold.**

I freshly reopened the saved modular asset and verified its exact SHA-256. I compared the south, west, and roof review renders with the Purdue 1924 archival photograph, Purdue's 2024 centenary exterior photograph, and the documented historic GIS evidence. This is an independent assessment of the saved asset; I did not edit the asset or master blend.

Asset: `modular/buildings/purdue_memorial_union.blend`  
SHA-256: `9f3d804155efb70e13ba49706f7da88f61a93a30f981612ec318eca2f3cac0f6`

| Criterion | Score | Finding |
|---|---:|---|
| Identity and source-backed footprint | 1.8 / 2 | Recognizable Purdue Memorial Union tower-and-wing plan. Historic Purdue Libraries GIS and the earlier independent baseline support the main shell footprint; 18 original named wall/base bounds are unchanged within 1 mm. GIS phases are historic and approximate. |
| Placement, orientation, and scale | 1.9 / 2 | Read-only master inspection documented one PMU marker at (205.75, -271.65, 0), zero rotation, and unit scale. The individual asset root remains at identity. No current master write/reopen was performed as part of this isolated asset grade. |
| Height, floors, and roof transitions | 1.0 / 2 | The model has a taller central tower and pitched wing-roof additions, but 29.5 m total height, floor spacing, and roof elevations are explicitly estimates. Independent south, west, and roof views show broad roof planes dominating the mass, abrupt/awkward overlaps and cutouts, and weak tower-to-wing transitions. The sources are photographs, not measured elevations. |
| Facade rhythm, entrance, and distinctive details | 1.3 / 2 | R1 improves on the baseline with six arched wing windows, archivolts, a glazed arched entry, and an upper tower surround. Against the Purdue 1924 and 2024 photos, the wings remain repetitive and underspecified; the portal, relief fields, and tower glazing are schematic, the upper glazing lacks the reference's full composition, and the roof mass obscures/readably competes with the facade. |
| Modular portability and evidence/validation | 1.7 / 2 | Builder source, provenance notes, fresh-reopen validation, assigned materials, and no external image dependencies are supplied. I independently reopened the saved asset and verified SHA-256 9f3d804155efb70e13ba49706f7da88f61a93a30f981612ec318eca2f3cac0f6, root identity, and portability. Deduction: validation_r1.json compares to .blend1, but the current .blend1 is a prior R1 save rather than the original baseline; independent original-baseline comparison supports 18 unchanged wall/base bounds, not 21 preserved original bounds. Three current wall/base pieces are additive. |
| **Total** | **7.7 / 10** | **Below pass** |

## Structural-preservation check

The original audited baseline record identifies 18 named wall/base objects that are present in R1; all 18 bounds match within 1 mm. R1 contains 21 wall/base pieces because it adds `PMU_Oriel_SE_Base`, `PMU_Oriel_SW_Base`, and `PMU_Tower_Base_Limestone`. Therefore, 18 original wall/base bounds are confirmed preserved and three pieces are additive; the evidence does not support describing 21 original bounds as preserved. Two roof objects were intentionally removed/replaced as documented.

## Main reasons for the score

The footprint and placement are strong, and the facade additions are a real improvement over the prior 7.3 baseline. The remaining gap is visual and dimensional: the broad roof surfaces dominate the current views, obscure the tower/wing relationships, and have awkward joins/cutouts. The facade still reads as repeated simple blocks, and the entrance and upper tower glazing are only approximate versions of the source photographs. No measured height, floor schedule, or roof elevations are provided, so those values remain uncertain.

## Actionable findings

1. Rebuild roof masses as separate, lower-profile slate wing roofs with clear eaves, ridges, valleys, and controlled intersections; the current broad surfaces overpower the facade and look like a canopy.
2. Use a source-matched south elevation to refine the tower's multi-level glazed composition and the wing opening rhythm; reduce repeated rectangular side-wall fenestration where current imagery supports a more specific pattern.
3. Refine the main portal scale and stone surround and add only photo-supported relief/statue geometry; current entry is recognizable but schematic.
4. Keep height/floor claims labeled as estimates unless measured elevation data is added.
5. Correct validation provenance: retain an immutable pre-edit baseline or compare directly against the audited original hash and structural-bounds record; distinguish 18 unchanged original wall/base bounds from 3 added base pieces.

## Evidence and limitations

Evidence inspected in this folder: `build_evidence.md`, `validation_r1.json`, `structural_comparison_r1.json`, `independent_reopen_r1.json`, `archives_postconstruction_1924.jpg`, `official_centenary_exterior_2024.jpg`, `grader_south_oblique.png`, `grader_west_oblique.png`, and `grader_roof.png`. The two dated photos show different eras and camera views, so detail judgments are qualitative. The GIS records support an approximate historical footprint only; they do not verify height, floor elevations, current facade, interior, or roof dimensions. Review lighting may contribute to the pale slate appearance, but the roof geometry itself is clearly broad and simplified.
