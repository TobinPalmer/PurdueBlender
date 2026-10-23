# Elliott Hall of Music — round 5 source and change notes

Work date: 2026-10-23. Scope was limited to `modular/buildings/elliott_hall_of_music.blend` and this evidence folder. No master, manifest, BUILDINGS index, or Hovde asset was edited.

## References

- SAH Archipedia describes the exterior as red brick with Indiana limestone banding, pilasters and ornament; it also describes red clay tile roofing, the second-story Hovde walkway, separate ground-level entries, and the main/secondary entrance features. This supports the material and feature types modeled, not their exact dimensions, count, or placement. https://sah-archipedia.org/buildings/IN-01-157-0079
- Purdue Convocations describes the north/south black-and-gold access awnings, step-free access to main-floor seats, and no elevators. https://convocations.purdue.edu/accessibility/
- Purdue Convocations’ Club Convos page describes the Hovde southeast entry, stairs/elevator to the second floor, and adjoining route into Elliott’s main lobby. It does not resolve the exact shared portal wall segment. https://convocations.purdue.edu/clubconvos/
- Purdue’s 75th-anniversary page links exterior construction photos and a panorama. The image pixels could not be inspected in this workflow, so no window count, schedule, or rhythm is claimed from those files. https://convocations.purdue.edu/elliott-hall-of-music-75th-anniversary-1940-2015/
- The shell plan remains registered to Purdue BuildingShapes Feature ID 617 (188-point polygon). It supports the horizontal outline, not facade openings or height. https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0

## Round 5 changes and checks

- Added shallow limestone belt courses and vertical pilasters to the 188-point shell. These features follow the SAH description; their count, spacing, dimensions and elevation are explicitly estimated because no measured elevation was found.
- Did not add speculative windows. Window count and placement remain unverified pending a directly inspectable photo/elevation.
- Kept the five existing shell openings. Blender BVH ray checks from outside across the shell report no hit at each aperture center; a control ray immediately above each opening hits the shell. Horizontal projection error is 0.0000–0.0006 m against the source outline. This checks the current shell mesh only; it does not verify the real-world opening locations or sizes.
- Removed the long round-4 connector endpoint. The Elliott-side upper opening remains, with a shortened conceptual landing/link that stops about 2.12 m before the current Hovde wall estimate. A visible amber terminal and two-sided “HOVDE / PENDING” review annotation identify the unresolved gap. This is not a completed connection; the Hovde-side portal is deferred to its own asset pass and joint master check. Connector height, length, section and endpoint remain estimates.
- The conceptual auditorium seating/interior was not remodeled this round. Its layout, dimensions, aisles and accessible seating coordinates remain unscaled or estimated from the available chart.
- Saved and reopened with Blender 5.2.3 LTS. The `Asset_elliott_hall_of_music` export contains 77 mesh objects. Source exterior, connector-detail, and auditorium renders are retained in this folder (`exterior_round5.png`, `hovde_gap_round5.png`, `auditorium_round5.png`); inspect with awareness that the Hovde temporary context model is not linked in these Elliott-only renders.

## Remaining limitations

Facade window schedule and surface match, belt-course/pilaster exact layout, accessible-entry dimensions/coordinates, the Hovde portal tie-in, all bridge dimensions, auditorium plan and seating registration, and vertical envelope dimensions remain estimated or unverified. The temporary gap annotation should be removed after the parent’s Hovde portal pass and joint integration verification.
