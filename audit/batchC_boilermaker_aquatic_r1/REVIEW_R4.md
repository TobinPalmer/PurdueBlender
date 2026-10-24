# Morgan J. Burke Boilermaker Aquatic Center — R4 review candidate

R3 received an independent **7.8/10**. Its remaining visual issues were a uniform facade, imperceptible masonry relief, a broad featureless roof, oversized building lettering, and schematic seating/circulation. R4 addresses those specific points. No self-grade is claimed.

## R4 changes

- Corrected the facade shader projection so brick courses follow the horizontal and vertical axes of the perimeter walls. The running bond and mortar relief are now legible in the close view and carry across the full vertical masonry shell.
- Raised the roof standing-seam detail and gave it a soft silver-gray metal treatment. The roof is still an estimated form; no sourced roof section or dimension was found.
- Reduced the direct-mounted name lettering to about 4.65 model units wide and centered it over the entry. This is a visual estimate from a qualitative Street View panorama, not a measured proportion.
- Added a schematic center access stair through the spectator bank, split the concrete tiers around the aisle, and kept 288 representative seats. Small seat-edge bevels and a dedicated aisle view make the arrangement easier to read. The aisle, seating, and gallery are not an as-built layout.

## Evidence and limits

The July 2023 [Google Street View north approach](https://www.google.com/maps/@?api=1&map_action=pano&pano=TdL92OGnlFSS8CxGuVLKDA) supports the broad brick facade, long clerestory/ribbon band, entrance canopy, and direct building lettering. Its image is qualitative and not calibrated. Purdue RecWell’s [Aquatics page](https://www.purdue.edu/recwell/sports-and-programs/aquatics/index.php) and [facility fact sheet](https://purdue.edu/recwell/visit/facility/fact-sheet.php) support pool features, spectator capacity, and a mezzanine, but no dimensioned elevation or interior plan was found. The [official GIS footprint](../batchC_boilermaker_aquatic_official_footprint.json) supports horizontal correspondence only.

Roof pitch/height, exact facade bay proportions, brick course size, sign dimensions, mezzanine placement, seating count/arrangement, and circulation remain uncertain or schematic. The model shows 288 representative seats; Purdue publishes a capacity of 625. The validator does not claim survey accuracy or master placement.

## Validation and renders

`validation_r4.json` records a fresh reopen in Blender 5.2.3 and passed checks. All 70 GIS footprint edges and all 70 shell segments are sampled in both directions; maximum sampled discrepancy is 0.000002 m. Checks also confirm 70 mapped vertical masonry faces, 57 ribbon panes, 86 raised seam splines, 288 representative seats, 12 center-aisle treads, 24 split step sections, published dive-pool depth/platforms, and materials on all meshes.

- `aquatic_r4_north_elevation.png`
- `aquatic_r4_street_approach.png`
- `aquatic_r4_north_masonry_detail.png`
- `aquatic_r4_entry_sign_detail.png`
- `aquatic_r4_interior_gallery.png`
- `aquatic_r4_interior_seating_aisle.png`

The source hash is in `asset_sha256_r4.txt`. R4 is ready for an independent full-building review.
