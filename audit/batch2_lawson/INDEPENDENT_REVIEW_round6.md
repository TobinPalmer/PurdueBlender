# Lawson Hall — independent R6 review

**Grade: 7.0/10 — below the 8/10 minimum.** Reviewed 2026-10-25 by reopening the exact saved asset in Blender 5.2.3 LTS. Source SHA-256 matches the requested R6 value: `2D3F2ABFCEDD19A0630CFB93EB9AC9C6473F5F99E54C4FD6B8615A6AACC9303E`.

| Rubric criterion | Score |
| --- | ---: |
| Correct identity and source-backed footprint | 1.4/2 |
| Position, orientation, and scale/dimensions | 1.4/2 |
| Evidence-backed height, floors, and roof form | 1.0/2 |
| Facade, entrances, and distinctive architecture | 1.4/2 |
| Modular export, portability, and complete evidence | 1.8/2 |
| **Total** | **7.0/10** |

## Findings

- **Identity and plan:** Purdue's first-floor plan identifies the building and supports the long north-up layout, curved Commons frontage, and south lobby projection. The saved exterior is consistent with those broad cues. Its raster registration is approximate, and this review did not independently overlay every structural wall against the GIS feature.
- **Placement and dimensions:** The existing read-only master marker record shows the expected Lawson placement, zero rotation, and unit scale; the reopened asset's root transform is identity. This validates registration of the asset marker. It does not prove surveyed facade alignment or source-backed building length and width.
- **Vertical form:** The first-floor plan supports only L1 layout and stair locations. The 10 ft Echo Spiral claim is consistent with the reopened 3.047 m mesh. The 21.30 m model maximum, shell, roof, penthouse, equipment heights, upper floors, and floor-to-floor stair continuity remain unverified.
- **Architecture and interiors:** The exterior is recognizable and includes brick/limestone bands, repeated glazing, the curved glazed Commons, and an entrance canopy. The 2024 Purdue photo is useful visual evidence for blue-gray glass but gives no measured facade specification. R6 changes only three glazing material values; it does not resolve schematic facade cadence, roof profile, or dimensions. The first-floor cutaway broadly follows the plan. The lobby spiral is still a schematic metal coil, while fixture layout and the contemporary state of the Commons wall remain uncertain.
- **Technical integrity:** Blender 5.2.3 reopened the requested source and found the expected `Asset_lawson_hall` collection with 601 objects and 598 meshes, identity root transform, no unmaterialed meshes, and no missing external images. The 16-module Commons wall and evidence package are present.

R6's glass adjustment is a modest visual change. The prior independent R4 score was 7.0/10; the same overall score is warranted because R6 changed no geometry or evidence coverage, and the full-building limitations remain.

## Evaluator and evidence files

- Executable evaluator: `audit/batch2_lawson/evaluate_r6.py` (run with Blender 5.2.3 against the saved `.blend`).
- Structured score: `audit/batch2_lawson/independent_evaluator_r6.json`.
- Inspected renders: `exterior_round6.png`, `interior_cutaway_round6.png`, `entry_lobby_round6.png`, `commons_wall_round6.png`.
- Main plan source: Purdue CS `lawson_1.pdf` and its rendered `source_floorplan.png`; source photos and articles are captured in the same audit folder. Placement evidence is in `audit/batch2_master/placement_check.json` and was treated as an existing record, not a fresh master reopen.
