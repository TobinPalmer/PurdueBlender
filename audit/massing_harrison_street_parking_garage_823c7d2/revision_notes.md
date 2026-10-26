# Harrison Street Garage revision notes — 2026-10-26

## Roof evidence update

The archived Indiana current orthophoto crop was inspected at full roof detail. It visibly shows rooftop parking stalls, broad circulation aisles and direction arrows, a raised elongated central structure/open-sided area, and small roof-edge enclosures. The image service metadata describes 2022–2025 orthophotography, but does not identify the acquisition date for this crop. `roof_aerial_zoom.png` is an enlarged crop of the archived source image for review; it adds no new source data.

The builder now adds light roof-stall striping and arrows aligned to the GIS footprint's approximate principal axes, an estimated open-sided central canopy with four piers, and a northwest-edge service/stair enclosure moved away from the central feature and reduced to an estimated 6 x 9 m. The existing full-area roof deck remains the garage's parking surface; this revision does not change the GIS-derived deck ring, asset ID, scene, collection name, or campus placement.

These added dimensions and positions are visual proportions from an orthophoto, not dimensioned/as-built measurements. The pavilion's exact function, height, ramp access, and parking stall geometry remain unverified. Six total levels including one below grade remain sourced to WGI; 3.2 m floor spacing and the 17.1 m top screen remain estimates.

## Validation checkpoint

The updated builder was run with Blender 5.2.0, which rendered `renders/harrison_oblique_review.png`, `renders/harrison_elevation_review.png`, and `renders/harrison_roof_review.png`, and saved the library. The saved `.blend` was reopened with Blender 5.2.0 and inspected using `validate_blend.py`; it confirms the expected stable scene and exported collection, 549 mesh objects, six structural deck objects, roof markings, circulation arrows, the central pavilion, and four support piers. The GIS-derived deck X/Y bounds remain -361.5203 to -303.2453 m and -747.1450 to -662.7343 m. Full asset bounds are X -361.7581 to -302.9874 m, Y -747.3728 to -662.5153 m, Z -3.44 to 17.10 m; the roughly 0.25 m plan overhang comes from facade piers centered at the structural perimeter. The build contains no linked libraries or image assets and no temporary preview objects/materials. The saved render engine is `BLENDER_WORKBENCH`, avoiding the Eevee engine ID difference between Blender 4.x and 5.x. A read-only Blender 4.5.15 reopen also recognizes the saved Workbench engine; it still warns that the file was authored by Blender 5.2.

Validation outputs: `validation.json`, `validation_log.txt`, and `validation_blender_4_5_log.txt`. The prior independent grader files in the sibling `_independent_grade_r2` folder were left unchanged; the 7.4/10 result applies to the pre-revision asset and should be superseded by a fresh independent grade.
