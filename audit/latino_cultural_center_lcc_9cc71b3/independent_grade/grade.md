# Independent LCC FID 925 grade

**Score: 9.0/10 — PASS**

| Criterion | Score | Evidence and findings |
|---|---:|---|
| Identity and official source match | 2.0/2 | Purdue BuildingShapesZip4 FID 925 labels the feature 'Latino Cultural Center at Purdue', code LCCP, address '426 Waldron Street'. Purdue LCC homepage snapshot gives the same address and the multicolored house, teal brick, yellow window trim, pink entrance and identifying sign. The asset depicts a one-story house-scale cultural center and contains a campus-context sign; no competing source candidate was used for the feature.  |
| Footprint, campus placement, orientation and scale | 2.0/2 | The dedicated floor mesh has 12 vertices and matches the transformed FID 925 vertices in source order; max error 1.5776327e-05 m, mean 8.1751353e-06 m. Source/model footprint bounding-box maximum edge error 4.8137153e-06 m; computed source area 162.030 m^2 and model area 162.030 m^2. Fresh-open campus-coordinate bounds [[-342.7321472167969, -324.5369873046875], [169.7769775390625, 183.73265075683594], [0.009999997913837433, 7.46999979019165]] m agree with the submitted evidence bounds; the asset retains identity placement for the massing convention. The FID 925 outline overlays the roof in the saved Esri World Imagery mosaic; this visual check is approximate because mosaic capture dates vary and are not recorded for each tile.  |
| Evidence-supported height, floors and roof | 1.5/2 | GIS attributes report 1 level and the candidate is visibly a one-story house with pitched main and secondary wing roofs. Purdue exterior imagery supports the shingled pitched roof, prominent dormer and chimney form; aerial imagery supports the roof massing. Fresh-open model top is 7.47 m, with evidence reporting a 5.78 m main ridge and 4.92 m east-wing peak. No surveyed elevation or dimensioned current plan supports the exact eave, ridge, wing-peak or chimney heights; these remain estimates. |
| Facade, materials and interior | 1.5/2 | The exterior render reproduces the current Purdue hero image's strongest cues: vivid teal masonry, yellow window surrounds, pink entry, white clapboard wing, divided windows and center sign. The saved facility source lists lounge, gathering, conference, ITaP lab, library and kitchen functions; the candidate includes those room types and the render depicts furnished activity zones. The 2023 garden source supports an on-site community garden; the candidate includes a small raised bed and planting. The interior plan and room positions are schematic because no dimensioned floor plan was found. Some specific facade/window dimensions and garden-bed placement remain inferred. |
| Modular portability and evidence completeness | 2.0/2 | Blender fresh-open read the expected scene/collection; collection contains 426 objects (423 mesh and 3 FONT text objects). Render setup is separated in sibling collections. Asset SHA-256 is 277F47A7941B785E9ABC9D3D799CAE65BA3872F7F78CB4D2420C68A5E913310A; it matches the candidate checksum in build_report.md: True. No linked libraries: True. Materials have no external image dependencies: True. The evidence folder includes raw Purdue GIS, current and historical official exterior images, facility information, garden evidence, Esri imagery tiles, and four renders with dates, source IDs and uncertainty notes.  |

## Overall findings

- No surveyed elevation or dimensioned current plan supports the exact eave, ridge, wing-peak or chimney heights; these remain estimates.
- The interior plan and room positions are schematic because no dimensioned floor plan was found. Some specific facade/window dimensions and garden-bed placement remain inferred.

## Uncertainties

- Official GIS confirms a one-level feature and footprint; no surveyed elevations or dimensioned current floor plan were available.
- Roof pitches, dormer/chimney sizes, window dimensions and exact room layout are estimates from current and historic Purdue imagery.
- The current LCC hero image has page context modified 2026-07-02; image capture date is not independently stated.
