# National Soil Erosion Research Laboratory — R2

## Revision summary

R2 follows the prior independent 6.9/10 score. It improves the south entrance facade, updates the material read, adds a source-informed hydraulics flume, and checks the modeled roof outline against the Purdue GIS footprint at the edge level.

The blank brick entrance wall now follows the FID 242 south perimeter line (rather than a horizontal approximation). The model restores the lab name and USDA lettering, the street-address plaque, a dark recessed entrance surround, glazed double leaves, transom, reveal returns, and a concrete approach. Dimensions and exact placement of these entrance parts remain approximate. The 2018 reference photo supports the sign, address, doorway, and blank-wall relationship, but is not an architectural elevation.

Brick, concrete, membrane roof, and glazing materials have a brighter, more legible response. Unsupported facade openings and projecting sills on the photographed south elevation were removed; the other elevations retain their modeled glazing. The two unverified floor-level strips crossing the blank photographed face were also removed. South-facing schematic benches and sample trays were moved inward so they no longer protrude through the exterior wall.

The hydraulics lab now contains a long open-channel flume with transparent sides, A-frame supports, safety rails, sensor gantry, sump, pump/control cabinet, and a console. The USDA photograph supports the equipment type. Its scale, position inside NSERL, and room arrangement are not verified.

## Source evidence

- [Purdue BuildingShapes feature service](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0), FID 242, supplies the registered footprint. The retained snapshot is in `audit/official_building_references.json`.
- [2018 visitor photo](https://ppgta.ufms.br/files/2018/02/Grupo-Purdue.jpg) shows a blank brick wall, raised “National Soil Erosion Research Laboratory” lettering, USDA identification, a recessed doorway, and the address “275 South Russell Street.” The source image is saved as `purdue_researchers_at_nserl_exterior.jpg`.
- [USDA ARS hydraulics-lab photograph K7567-11](https://www.ars.usda.gov/oc/images/photos/apr97/k7567-11/) shows a long flume with transparent side panels, supports, walkways/rails, and test instrumentation. The source image is saved as `usda_hydraulics_lab_k7567-11.jpg`.
- The roof-height split retains the R1 evidence: Indiana 2018 5-ft DSM minus interpolated bare-earth DTM. The high/low estimates remain approximate, not surveyed heights.

## Validation

`nsel_revision_r2_validation.json` records a fresh reopen in Blender 5.2.3 and a passing validation. The roof outline is compared in both directions against FID 242, sampled every 0.2 m. Maximum sampled boundary distance is approximately 0.000006 m; the roof area differs by less than 0.000001%. The close match verifies that the mesh follows the supplied GIS coordinates; it does not establish the source survey’s real-world accuracy.

The south brick panels are within 0.051 m of the registered south edge, accounting for their 0.10 m thickness. The model still separates the roof wings at an approximate west/east break: the east wall tops at 5.20 m and west at 7.32 m.

## Review images

- `nsel_revision_r2_exterior.png`
- `nsel_revision_r2_entry_detail.png`
- `nsel_revision_r2_roof_outline.png`
- `nsel_revision_r2_hydraulics_cutaway.png`

## Limitations and grading status

- The initial independent score was 6.9/10. R2 is ready for a fresh independent grade; no R2 score has been received yet, and the 8/10 target is not claimed.
- The height split comes from 5-ft DSM cells and interpolated DTM ground values. It remains approximate.
- The entrance photograph is a visitor photo, not a measured elevation. Door dimensions, exact opening depth, window schedule, and sign placement remain estimates.
- USDA evidence confirms the flume type but not its exact room location, dimensions, or adjacent circulation. Interior circulation remains schematic.
- Only the NSEL source asset and its dedicated audit/evidence were edited. The master blend, README, manifest, shared indexes, and other building assets were not changed. No commit was made.
