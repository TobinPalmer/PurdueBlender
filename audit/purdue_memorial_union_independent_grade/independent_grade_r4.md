# Independent grade — Purdue Memorial Union R4

**Score: 8.0/10 — meets the 8.0 pass threshold.**

Reviewed asset SHA-256: `7e0e03969cad5846edacc38a4945f2c9021e48877c022cc79035d10e144eb480`. I independently reopened the saved asset in Blender 5.2.3; results are in `independent_reopen_r4.json`. I compared the fresh R4 views against the cited Purdue Archives 1924 photo and Purdue University 2024 exterior image, and checked the prior review and R4 source/validation record.

| Criterion | Score | Finding |
|---|---:|---|
| Identity and source-backed footprint | 1.8/2.0 | The model remains recognizable as the Purdue Memorial Union tower-and-wings complex. The supplied historic Purdue GIS phases and immutable baseline support the retained shell. Independent Blender reopen measured all 18 original wall/base bounds unchanged at 0.0 m delta; three documented bases are additive. The historical GIS match is approximate, not a current survey. |
| Placement, orientation, and scale | 1.9/2.0 | The saved asset root reopened at identity transform. The read-only master-marker record has one Placement_purdue_memorial_union at (205.75, -271.65, 0), zero rotation and unit scale, linked to the expected collection/library. This pass did not reopen the current master, so integration remains a coordinator check. |
| Evidence-backed height, floors, and roof form | 1.2/2.0 | R4 adds narrow flashing at roof intersections and retains separate low-pitch gables. The fresh south/west obliques still show very broad, largely uninterrupted blue roof planes and abrupt courtyard transitions; the roof silhouette does not yet read cleanly as the distinct wings shown in the dated references. Aggregate 29.5 m height, floor spacing, eaves, ridges and junction positions are explicitly estimates, not measured elevations. |
| Facade rhythm, entrance, and distinctive architecture | 1.6/2.0 | The south facade has arched window bays, glazed multi-tier tower openings, a framed entry, dormers supported by the 1924 photo, and new paired relief silhouettes informed by the 2024 Purdue image. Brick and slate have visible surface texture. The relief silhouettes remain far simpler than the photographed carved groups; tower mullion proportions, stone ornament, side-window rhythm and large west-wall areas remain schematic or unverified. The detailed front still reads as a simplified interpretation rather than a close facade reconstruction. |
| Modular portability and evidence/validation | 1.5/2.0 | Independent Blender 5.2.3 reopen confirms the exact requested SHA, 650 collection objects/608 meshes, identity root, no materialless meshes, no unpacked external images, and unchanged baseline wall/base bounds. R4 evidence records provenance and uncertainties. The shared manifest still reports the old 414-object unverified PMU asset without a hash or grade path, so the coordinator must refresh indexes and reopen the master before accepting integration. |

## Findings

1. Independent score: 8.0/10, narrowly meeting the requested pass threshold. This score does not mean every facade, roof, floor, or height detail is verified.
2. R4's additional roof flashing and tower relief silhouettes improve the prior model, but the broad roof planes and courtyard transitions remain the strongest visual discrepancy in current oblique/top views.
3. The paired reliefs are currently simple silhouettes rather than detailed groups like the 2024 Purdue photo; tower glazing and surrounding limestone ornament also remain schematic.
4. Before master acceptance, the coordinator must update the shared manifest/building index to the 650-object asset and this grade, reload the master, and verify the linked collection and placement marker. The existing read-only marker record alone does not prove the current master was reopened.

## Review limits

- Historic GIS features are phase-specific and were converted with the project's approximate local tangent-plane formula; they do not establish current survey precision.
- The 1924 archival and 2024 campus images differ in date and viewpoint; they support qualitative facade/massing comparison, not measured elevations or roof dimensions.
- The 29.5 m aggregate top, floor spacing, eaves, ridges and roof junctions remain estimates; no measured elevation or roof plan was found in the cited sources.
- This reviewer did not edit the asset, master blend, manifest or shared indexes.

Machine-readable scorecard: `independent_grade_r4.json`. Scoring function: `independent_evaluator_r4.py`.
