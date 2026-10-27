# Provenance Apartments 005 revision

## Identity and footprint evidence

County Area Plan Commission construction-plan sheet C1.4 identifies the apartment block between BLDG E / 144 and BLDG G / 142 as BLDG F / 143. The transformed Purdue GIS FID 506 ring overlays the central Building F roof outline in the Indiana current orthophoto without a fitted image warp. The current ImageServer catalog identifies a statewide 2025 2-foot raster and a Tippecanoe 2023 6-inch source item at this location. The official orthophoto is saved with an overlay at `indiana_current_orthophoto_2025_fid506_overlay.jpg`.

The stable `.005` identity is crosschecked against the inherited proxy's very broad bounds center: 10.84 m from FID 506, compared with 44.11 m from next-nearest FID 501 / Building E. The explicit F / 143 plan label and current imagery independently corroborate the match. The initial broad AABB is not treated as target geometry.

FID 506 still belongs to a `BLDG Building Pre-planning` layer, and its `ADDRESS` field is blank even though `BUILDING_1` contains `1509`. The plan packet is a final detailed construction/stormwater sheet, not an as-built survey or an elevation. The orthophoto shows roof/eaves, not the exterior wall line. Therefore block identity and position are defensible, and overall plan outline is strongly corroborated; exact surveyed wall registration remains approximate.

## Geometry changes

- Replaced the inherited 138.148 m by 28.382 m broad aggregate proxy with the FID 506 / Building F / 143 footprint (about 49.728 m by 19.284 m in project-local approximation).
- Kept three floors as a project-level count. Eave at 8.9 m and ridge at 11.4 m remain estimates with about ±1.5 m uncertainty; no individual Building F elevation was located.
- Retained a five-break gabled massing rhythm corroborated visually by project imagery/current roof imagery. Exact gable count, ridge positions, pitch and heights remain estimates.
- Added dark window perimeter frames/mullions, three visible accent bays, selected balcony decks/rails and two glazed entries with shallow canopies. Their features are supported by Studio M Provenance photographs, but their arrangement on Building F is schematic.

## Reopened asset

The saved `.blend` was reopened in a separate Blender 5.2.3 process and passed all checks in `reopen_validation.json`. The named scene and collection persist, the collection contains one mesh, all 32 base-ring points match the transformed GIS source within 0.000060 m numerically, facades extend beyond the base footprint as expected, estimated height is 11.4 m, there are no modifiers or external image dependencies, and the source plan/overlay evidence files are present.

Proposed replacement bounds for the coordinator's shared-manifest update: X `[-1573.2703, -1523.5427]` m; Y `[-468.0058, -447.4717]` m; Z `[0, 11.4000]` m. The base GIS ring is Y `[-466.8532, -447.5692]` m; southward façade projections add about 1.15 m to overall model bounds.

This revision is frozen for independent grading. No shared manifest/index files and no Git commits or pushes were made by this lane.
