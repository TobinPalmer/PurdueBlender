# Morgan J. Burke Boilermaker Aquatic Center — R6 review candidate

R5 independently remained at **7.9/10**. The review requested a visible improvement to spatial presentation, stronger building-specific interior evidence, a clearer seating/gallery view, and explicit uncertainty where roof or seating details cannot be measured. R6 focuses on the natatorium interior; no roof dimensions or campus placement are inferred.

## R6 changes

- Changed the 21 existing schematic clear-span truss meshes to a warm white painted-steel finish. Purdue Athletics facility photos and a project photo from the structural engineer show a tall natatorium with exposed light-colored steel trusses. The source imagery supports the material character, but not this model’s truss spacing, member section, geometry, or roof elevations.
- Added 15 small high-bay light blocks and two hanging black-and-gold Purdue display panels. Overhead lights and Purdue-branded displays are visible in facility photos; their positions, number, dimensions, and lighting plan are visual estimates for presentation only.
- Added a longitudinal interior camera looking past the pool deck toward the spectator bank, plus a closer pool-side seating/gallery view. The renders use a neutral world background and hide the roof and optional site context for these cutaways; the saved asset’s render visibility remains unchanged.
- Kept the optional `AQUA_R5_Context | approximate site dressing` collection separate from the building shell. It remains approximate and un-georeferenced for the master coordinator to show or hide during integration.

## Evidence and limits

Purdue Athletics’ [official facility photo gallery](https://purduesports.exposure.co/morgan-j-burke-aquatic-center) (January 2018) provides building-specific interior photographs. A facility photo on [Arsee Engineers’ athletics projects page](https://www.arsee-engineers.com/project-athletic.html) also shows the pool hall and exposed steel roof structure. Purdue’s [RecWell Aquatics page](https://www.purdue.edu/recwell/sports-and-programs/aquatics/index.php) and [facility fact sheet](https://purdue.edu/recwell/visit/facility/fact-sheet.php) support the published pool program, 625 spectator capacity, and mezzanine. The [Tnemec project profile](https://www.tnemec.com/documents/134/Boilermaker_Aquatic_Center_Profile.pdf) describes a protected steel roof deck and concrete finishes; it does not provide a roof section. The [official GIS footprint](../batchC_boilermaker_aquatic_official_footprint.json) supports horizontal outline correspondence only.

The roof profile and all eave/ridge heights remain unverified. Truss member layout, lighting layout, banner location/scale, seat arrangement, gallery geometry, and circulation remain schematic or estimated. Purdue publishes capacity for 625; the asset contains 288 representative seat blocks. GIS correspondence does not prove survey position or placement in the campus master.

## Validation and renders

`validation_r6.json` records a fresh reopen of the saved asset in Blender 5.2.3. Validation passed: all 70 FID 896 boundary edges and 70 shell segments were sampled in both directions, with 0.000002 m maximum mismatch each way. It confirms 21 truss meshes, 15 high-bay fixture blocks, 2 banner panels and 2 text objects, 288 representative seat blocks, 12 center-aisle treads, 24 split tier sections, 57 ribbon-glazing panes, 21 optional context objects, material assignment on all mesh objects, and no external image dependencies. The perimeter comparison validates local footprint correspondence only.

- `aquatic_r6_interior_longitudinal.png`
- `aquatic_r6_interior_seating_gallery.png`
- `aquatic_r5_north_elevation.png`
- `aquatic_r5_street_approach.png`

The saved asset hash is recorded in `asset_sha256_r6.txt`. R6 is ready for an independent full-building review.
