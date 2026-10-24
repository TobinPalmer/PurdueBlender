# Morgan J. Burke Boilermaker Aquatic Center — R3 review-ready revision

R2 received an independent grade of **7.9/10**. This iteration addresses the reviewer’s visual notes while preserving the uncertainty around undocumented geometry. No self-grade is claimed.

## R3 changes

- Removed the oversized plaque and used direct-mounted building-name lettering, consistent with the north-approach Street View. The text size is a visual estimate because the panorama is qualitative, not calibrated.
- Improved the three-quarter street-approach view of the brick facade, glazed openings, entrance, and canopy.
- Added procedural brick relief/color variation and refined the roof-metal finish. Added 43 standing seams per estimated roof plane; this is a material/detail treatment, not evidence for a specific roof assembly.
- Refined the interior cutaway view so the representative seat bank, mezzanine, stairs, pool deck, and diving structure are easier to read without overhead roof lines. The interior layout remains schematic.

## Evidence and limits

The July 2023 [Google Street View panorama](https://www.google.com/maps/@?api=1&map_action=pano&pano=TdL92OGnlFSS8CxGuVLKDA) supports the broad north-facade arrangement, long clerestory/ribbon band, entrance canopy, and direct lettering. It does not establish measured proportions. Purdue RecWell’s [Aquatics page](https://www.purdue.edu/recwell/sports-and-programs/aquatics/index.php) and [facility fact sheet](https://purdue.edu/recwell/visit/facility/fact-sheet.php) support pool features and a mezzanine, but no dimensioned interior plan or exterior elevation was found. The [official GIS footprint](../batchC_boilermaker_aquatic_official_footprint.json) verifies horizontal boundary correspondence only.

Roof profile, eave/ridge height, exact facade bay proportions, mezzanine location, seat arrangement, and circulation remain uncertain or schematic. The model includes 300 representative seats; Purdue publishes capacity for 625. The validator does not claim survey accuracy or master-scene placement.

## Validation and review renders

`validation_r3.json` records a fresh reopen in Blender 5.2.3 and passed checks. All 70 official FID 896 footprint edges and all 70 shell perimeter segments are sampled in both directions; maximum sampled mismatch is 0.000002 m. It also verifies facade-window count, material assignments, representative seating and mezzanine, published dive-pool depth/platform elevations, and no external image dependencies.

- `aquatic_r3_north_elevation.png`
- `aquatic_r3_street_approach.png`
- `aquatic_r3_entry_sign_detail.png`
- `aquatic_r3_interior_gallery.png`

The source hash is recorded in `asset_sha256_r3.txt`. R3 is ready for independent full-building review.
