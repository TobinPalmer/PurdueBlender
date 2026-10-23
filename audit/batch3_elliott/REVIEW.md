# Elliott Hall of Music — round 3 builder handoff

Updated 2026-10-23 after addressing the second independent review. This is a builder status note, not an independent score. The third-party review is pending. Only the Elliott source library and this evidence folder were changed; the campus master, manifest, and shared building index were not edited.

## Saved source and additions

- Source: [`modular/buildings/elliott_hall_of_music.blend`](../../modular/buildings/elliott_hall_of_music.blend)
- The saved source was reopened in Blender 5.2.3. The linked export collection contains **66 mesh objects**. The 496-object hidden legacy reference collection remains excluded.
- The shell keeps the official 188-point GIS footprint. The previous 140 procedurally spaced window holes and the single inferred entry were removed by rebuilding from the preserved original interior source.
- Two true door gaps were cut through the exterior wall at the north and south sides. A ray check through each gap at 1.5 m found no wall intersection; a ray at 4 m did hit the wall. The doors are glazed double leaves with limestone jambs/lintels, black awnings and Purdue-gold fascia. Purdue explicitly identifies north/south accessible doors with black-and-gold awnings and says patrons reach main-floor seats without steps.
- Two level exterior landings, approaches, and 1.5 m-wide estimated interior route ribbons connect the documented doors toward the nearest main-floor wheelchair seating areas. The seating chart is unscaled, so the route traces, landing size, and two blue clearance pads are estimated. These route ribbons are a physical continuity proposal, not a surveyed or code-certified access plan.
- Red brick, Indiana-limestone coursework, pilasters, a red-clay tile surface and a flytower are included. SAH documents those material/architectural families; the exact band/pilaster spacing, roof surface geometry, 22.5 m roof plane, flytower position and height remain estimates. No regular window rhythm was added.
- The existing auditorium geometry remains in place: 3 seating levels, 8 sections and 5,946 estimated modeled seats. The public seating illustration supports the levels, sections and wheelchair-seat symbols, but not the model’s row spacing, coordinates, balcony heights or exact aisle geometry.

## Evidence images and checks

- [`round3_north_door.png`](round3_north_door.png) — north-side accessible door and awning.
- [`round3_south_door.png`](round3_south_door.png) — south-side accessible door and awning.
- [`round3_access_routes_top.png`](round3_access_routes_top.png) — auditorium plan view with the two estimated level route ribbons and wheelchair clear-space pads.
- [`opening_ray_check.json`](opening_ray_check.json) — confirms both door locations have a real opening through the wall shell.
- [`result_round3_accessibility.json`](result_round3_accessibility.json) — export, footprint, estimated door and route details.
- [`source_notes_round3.md`](source_notes_round3.md) — evidence and modeling assumptions for this revision.
- [`source_inventory.json`](source_inventory.json) — rebuilt source export object inventory.
- Existing interior views remain [`from_stage.png`](from_stage.png), [`from_rear.png`](from_rear.png), and [`from_balcony.png`](from_balcony.png); the interior seat and balcony geometry was preserved from the previous source.

## References and limits

- Purdue Convocations’ current accessibility guidance documents both north and south accessible entrances, the black-and-gold awnings, step-free access to main-floor seats, no elevators in Elliott, and wheelchair seating with nearby companion seats: [Accessibility](https://convocations.purdue.edu/accessibility/).
- Purdue’s directions and parking page gives the north and south accessible lots and notes a restroom by the south access door: [Directions and parking](https://convocations.purdue.edu/parking-directions-elliott-hall-of-music/).
- SAH Archipedia describes red brick and Indiana limestone, a red clay tile roof, a cubic mass with flytower and apsidal projection behind the stage, the curving entry canopy, secondary entrance enframements, stepped side-exit walls, and two sculpture groups: [Edward C. Elliott Hall of Music](https://sah-archipedia.org/buildings/IN-01-157-0079).
- Purdue’s current public seating chart indicates three seating levels, sections, and wheelchair-seat symbols; it is not a dimensioned plan: [Seating charts](https://convocations.purdue.edu/seating-charts/).
- The official GIS footprint, FID 617, supports horizontal shell registration only: [BuildingShapes FeatureServer](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0).
- Purdue’s anniversary page describes the approximately 6,000-seat proscenium auditorium and provides historical exterior imagery: [Elliott Hall of Music 75th Anniversary](https://convocations.purdue.edu/elliott-hall-of-music-75th-anniversary-1940-2015/).
- The north/south entrance count and awning colors are treated as verified from Purdue’s written guidance. No exact entry coordinates, current dimensioned facade elevation, measured access-route plan, or scaled seating plan was available in this pass. Google Maps and general photos were not used to claim dimensions or exact window spacing. Exterior opening dimensions, route alignments, and all interior registration remain estimates.

## Next review

Please independently inspect the reopened `.blend`, both door openings and awnings, the route continuity and clear-space pads, roof/flytower, facade materials, and the existing auditorium. Rate the asset against the same rubric and identify concrete remaining defects. This handoff makes no 9/10 claim.
