# Morgan J. Burke Boilermaker Aquatic Center — R5 review candidate

R4 received an independent **7.9/10**. The reviewer still saw a repetitive hall beneath a broad roof, schematic seating/aisle rails, and too little architectural context in the gallery render. The available sources do not calibrate the roof profile or heights, so R5 focuses on material/surface variation and approximate site presentation without inventing roof dimensions or asserting master placement. No self-grade is claimed.

## R5 changes

- Carried the running-bond masonry treatment around the vertical shell to keep facade variation consistent. The brick course pattern is a visual material treatment, not a surveyed module.
- Kept visible standing seams and refined the metal surface treatment; the roof geometry remains uncertain and unchanged.
- Refined spectator seat edges and retained the schematic center aisle, with 288 representative seats, 12 aisle treads and 24 split tier sections. No as-built seating plan was found.
- Added an interior presentation with facade/window context visible behind the seating. A separate cutaway remains for pool and seating readability.
- Added a **separate, optional** `AQUA_R5_Context | approximate site dressing` collection containing a forecourt, north sidewalk, approach walk, approximate roadway edge, lawn beds and generic trees/shrubs. Purdue sources support the adjacent CoRec and nearby campus roads, while Street View supports the entrance approach. The local dressing is not georeferenced; the master can hide this collection if site roads or landscape are already modeled there.

## Sources and limits

The July 2023 [Google Street View north approach](https://www.google.com/maps/@?api=1&map_action=pano&pano=TdL92OGnlFSS8CxGuVLKDA) supports the brick facade, ribbon/clerestory glazing, canopy and direct building lettering. It is a qualitative image, not a measured elevation. Purdue’s [facility fact sheet](https://purdue.edu/recwell/visit/facility/fact-sheet.php) says the aquatic center is accessed through the CoRec control; the [official athletics page](https://purduesports.com/facilities/morgan-j.-burke-aquatic-center/12) places it just west of CoRec near Stadium Avenue and Martin Jischke Drive. The [Purdue RecWell facility map](https://www.purdue.edu/recwell/images/_maps/staticmap_aquatic.png) gives broad campus orientation but no surveyed site geometry. The [official GIS footprint](../batchC_boilermaker_aquatic_official_footprint.json) provides only the building outline.

The roof profile/heights, facade dimensions, lettering scale, interior circulation and seating arrangement remain uncertain. GIS-to-shell comparison does not validate height or master placement. The optional context collection is approximate, and it should not be treated as survey-placed campus infrastructure.

## Validation and renders

`validation_r5.json` records a fresh reopen in Blender 5.2.3 and passed checks. It confirms 70 GIS boundary edges matched against 70 shell segments in both directions, with maximum sampled discrepancy 0.000002 m. That is local footprint correspondence only. It also verifies 70 mapped masonry faces, 57 ribbon panes, 86 roof seam splines, 288 sample seats, 12 aisle treads, 24 split tier sections, 21 optional context objects, published dive-pool dimensions/platforms, material assignment, and no external image dependencies.

- `aquatic_r5_north_elevation.png`
- `aquatic_r5_street_approach.png`
- `aquatic_r5_north_masonry_detail.png`
- `aquatic_r5_entry_sign_detail.png`
- `aquatic_r5_interior_gallery.png`
- `aquatic_r5_interior_seating_aisle.png`
- `aquatic_r5_interior_architecture_context.png`

The saved asset hash is in `asset_sha256_r5.txt`. R5 is ready for an independent full-building review.
