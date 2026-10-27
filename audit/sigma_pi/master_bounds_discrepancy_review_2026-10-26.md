# Sigma Pi bounds discrepancy review — 2026-10-26

## Finding

The Sigma Pi asset geometry is not shown to be misplaced or incorrectly scaled by the bounds discrepancy in `audit/rossen_master_integration_audit_2026-10-26.md`. The discrepancy is explained by stale `modular/manifest.json` metadata that still records an earlier, generic 16 m-high massing. The R5 asset was intentionally rebuilt with the official FID 776 roof-plan ring, an estimated 9.35 m wall shell, and a LiDAR-derived roof surface. Its expanded facade and entry objects also determine the outer collection bounds.

No evidence-supported geometry edit is justified. The manifest is coordinator-owned, so this note records the finding for the coordinator rather than changing shared metadata.

## Measurements

A read-only Blender 5.2.0 open of `modular/buildings/massing_house_301836568_0fbca0e.blend` measured 266 mesh objects in `Asset_massing_house_301836568_0fbca0e`. The complete collection bounds are:

| Axis | Manifest | Current asset collection | Master linked objects |
| --- | ---: | ---: | ---: |
| X (m) | -439.4377 to -419.8549 | -439.2856 to -417.9656 | -439.2856 to -417.9656 |
| Y (m) | -179.9181 to -146.6616 | -179.8259 to -146.4169 | -179.8259 to -146.4169 |
| Z (m) | 0.0000 to 16.0000 | 0.0750 to 12.5688 | 0.0750 to 12.5688 |

The current asset's extrema are accounted for by facade and entry details at the plan edges and bottom, and the roof mesh at the top. The structural shell bounds are X -439.1611 to -419.6351 m, Y -179.7059 to -146.5388 m, Z 0.25 to 9.35 m. The separate roof mesh spans X -439.1573 to -419.6893 m, Y -179.6531 to -146.5334 m, and Z 9.4868 to 12.5688 m.

The live master audit reports 266 linked scene objects and exactly the same full-collection bounds as the saved asset. The manifest still says `object_count: 1` and retains the previous bounds, so both metadata fields need coordinator reconciliation. The 0.02 m integration-audit tolerance is exceeded because this compares the new R5 asset to those stale values; it does not demonstrate an error in the asset's source registration.

## Source-backed geometry assessment

- The raw Purdue BuildingShapesZip4 snapshot identifies FID 776 as Sigma Pi, 130 Russell St. The source register and independent R5 evaluator also cite the official chapter location and Purdue Off-Campus Housing listing as identity cross-checks.
- The build reconstructs all 36 unique GIS ring vertices in the documented Purdue local approximate-meter frame. The R5 fresh-open evaluator measured a maximum nearest-vertex error of 0.000017 m. The registered current state orthophoto overlay shows the ring tracing the roof perimeter. The evidence explicitly does not claim the roof edge is the structural wall line.
- The height model uses 2018 QL2 LiDAR over the ring and nearby class-2 ground returns. The saved analysis reports 1,094 filtered, **unclassified class-1** surface returns; their p10–p90 heights are approximately 9.74–12.25 m above the local ground median. The interpolated roof reaches 12.5688 m in the saved asset. No class-6 building returns were present, and vegetation contamination cannot be ruled out. This supports an estimated roof surface and articulation, not a measured wall height or floor count.
- The current evidence therefore supports retaining the GIS roof-plan registration and LiDAR roof geometry. It does not support moving/rescaling the building to reproduce the stale manifest bounds. The 9.35 m wall height remains explicitly estimated.

## Independent grade and reopen evidence

The latest independent grade is R5, 8.1/10 PASS, for asset SHA-256 `9ce88b7bb8da63593d90ca9aaa303f2afde88433e94600e265c9361580997c1b`. Its `freeze_r5.json` records a fresh Blender 5.2.3 LTS read-only reopen. The evaluator independently opened and measured the shell and roof, confirmed the exact GIS ring match, and passed the required grade threshold. Its remaining concerns are the estimated wall/story arrangement, unclassified LiDAR roof points, and the 2004 photo's gabled roof cues not being modeled as gables. Those concerns are not resolved by forcing collection bounds to match an earlier manifest record.

## Recommended coordinator action

Refresh Sigma Pi's `object_count`, `bounds_world_m`, and any derived `exterior_bounds_world_m` / `source_bounds_world_m` in `modular/manifest.json` from the current asset after choosing the project's shared-metadata convention for counting a massing library. The root coordinator owns that shared file. Preserve the asset geometry pending stronger evidence for wall line, floor count, or a current measured roof profile.

## Evidence files

- `audit/sigma_pi/independent_grade/grade_result_r5.json`
- `audit/sigma_pi/freeze_r5.json`
- `audit/sigma_pi/accuracy_record.json`
- `audit/sigma_pi/sources/geometry_imagery_crosscheck.json`
- `audit/sigma_pi/sources/indiana_current_aerial_sigma_pi_3857_overlay.jpg`
- `audit/sigma_pi/sources/sigma_pi_lidar_surface_analysis.json`
- `audit/sigma_pi/sources/sigma_pi_lidar_roof_mesh.json`
- `audit/sigma_pi/reopen_validation.py`
- Read-only bounds measurement: Blender 5.2.0, `work/sigma_pi_bounds_audit.py` (scratch measurement script)
