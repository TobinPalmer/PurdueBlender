# Delta Zeta FID 752 — independent grade

**Reviewed asset SHA-256:** `E86CF1D70C54E93053F3224721D73D9734AB3924AB97A58927AC2D3317104509`  
**Result:** **8.3/10 — PASS** (pass threshold: 8.0)  
**Review date:** 2026-10-28  
**Mode:** Read-only review of the exact saved asset and its evidence packet. The asset file was not modified.

## Weighted score

| Category | Weight | Score | Weighted points |
|---|---:|---:|---:|
| Identity and provenance | 20% | 9.0 | 1.800 |
| Plan geometry and placement | 25% | 8.7 | 2.175 |
| Exterior silhouette and openings | 25% | 7.5 | 1.875 |
| Materials and facade | 10% | 7.9 | 0.790 |
| Interior and cutaway | 10% | 7.7 | 0.770 |
| Presentation and technical | 10% | 8.6 | 0.860 |
| **Total** | **100%** |  | **8.270 → 8.3** |

## Findings

Identity and provenance are strong. The packet ties Purdue GIS FID 752 to Delta Zeta at 825 Hilltop Drive and includes official university/chapter references, permit context, and a clear source-date record.

Plan geometry is a strength. The 11-vertex official GIS ring is used for the modeled wall base, and the saved comparison reports a 0.0000311 m maximum GIS-corner to wall-base-vertex error. Because the same source ring defines both sides of that comparison, this is a construction check rather than independent survey validation. The unnamed OSM way is appropriately treated as a secondary general check: IoU 0.893, Hausdorff 3.50 m, centroid offset 1.16 m.

The exterior communicates the brick house, centered arched entry window, double doors, stairs, lamps, and chapter marker. The current silhouette remains a simplified two-level block under a broad, shallow pale-blue roof cap. The roof form/material and story count are unresolved; Purdue GIS reports one level, while the packet appropriately labels the modeled two levels, 7.2 m eave and 9.0 m peak as estimates. Window rhythm and elevation proportions are generic.

The material separation and presentation are readable, but the bright roof and cool blue cast are visually stronger than the red-brick source description suggests. The cutaway clearly labels foyer, living room, dining room, and kitchen. The chapter article supports those room names, but not the modeled room positions, dimensions, partitions, or furniture.

Technical evidence is solid: the exact asset SHA matches the handoff and fresh-open record; that report records the stable scene and one-object collection, 2,471 vertices, 1,757 faces, no external image datablocks, and no saved cameras or lights.

## Refinements that would improve the model

- Find a direct elevation or current photo before changing roof slope, height, or story count; until then retain their estimated status.
- If a usable exterior photo is available, tune the roof and brick palette and reduce the cool blue cast.
- Refine window spacing and door proportions only with a clear elevation reference.
- Keep the room layout explicitly schematic; do not imply the model locates rooms from the source article.

The evidence and technical quality clear the 8/10 bar despite the unresolved roof and elevation details. No changes were made to the reviewed asset.
