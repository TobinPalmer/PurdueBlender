# Independent grade — West Lafayette Intermediate School (R3)

**Result: PASS — 8.4/10**
**Frozen asset SHA-256:** `4564b0c307b781ec5f5135e58db29fc33b35c2bd813ad011d8ff4471e24cab2b`
**Inspected independently:** 2026-10-27, Blender 5.2.3 LTS.

## Score

| Criterion | Score | Review |
| --- | ---: | --- |
| Identity and source-backed footprint | 2.0/2 | Identity/address are corroborated by the district listing; independently re-opened shell matches all 45 OSM perimeter points. Max nearest-vertex error 0.0000607 m; plan area 10,899.5491 m² vs OSM 10,899.5474 m². |
| Position, orientation, and scale | 2.0/2 | Shell remains in the source-derived campus position and orientation; shell, rather than overhang-inclusive aggregate bounds, is the footprint comparison. |
| Height, floors, and roof | 1.1/2 | Aerial supports the broad crossed wings and southeast gym cluster. Height, roof levels, and vertical profile remain estimated without measured elevations or roof plan. |
| Facade, entry, and distinctive architecture | 1.3/2 | Brick, glazing, metal panels, red steel entry, clerestory, gym trusses and red bleachers are represented from architect imagery. Facade rhythm and canopy geometry remain schematic. |
| Modular export, portability, and evidence | 2.0/2 | Exact asset reopened in a separate Blender process with expected scene/collection; 1,862 objects, procedural materials and no external image files. Evidence and source register are comprehensive. |
| **Total** | **8.4/10** | **Pass threshold: 8.0** |

## Findings and limits

I independently opened the exact frozen `.blend`, confirmed its scene and scene-linked asset collection, and inspected the exterior, entry, classroom, and gym renders. A separate geometry check transformed the raw OSM way 772742586 coordinates with the project transform and compared them to the asset's GIS shell vertices. The shell geometry and campus position are exceptionally close to the mapped polygon.

The aerial image and architect narrative support the major three-wing arrangement, central node, and southeast gym/multipurpose mass. Architect photographs support the selected exterior palette and exposed red-steel entry language. However, neither source set supplies measured elevations, a dimensioned roof plan, or an interior floor plan. The rendered entry canopy is a simplified portal compared with the architect photograph. Classroom coordinates are schematic; checking that rooms remain inside the perimeter verifies containment, not an authoritative room layout.

The OSM footprint is community mapped rather than survey certified. Exact model height, parapet levels, roof profile, facade stationing, and room positions remain unverified. These limitations reduce the vertical-form and facade scores, but the verified footprint, source-backed broad form, architecture, and portable asset clear the 8/10 gate.

No model, shared index, README, manifest, or master file was changed during this grade.
