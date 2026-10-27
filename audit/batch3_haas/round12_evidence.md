# Felix Haas Hall — round 12 roof correction

**Asset:** `modular/buildings/felix_haas_hall.blend`
**Export collection:** `Asset_felix_haas_hall`
**Final reopened SHA-256:** `0de3417c6cc3af247b2100242720d39871bc8ed188dcf06bfbb96d9bead2c067`

## Evidence reviewed

- Purdue Events, [Felix Haas Hall](https://events.purdue.edu/felix_haas_hall), official exterior photograph. It confirms the red tile roof and its broad, low-pitched profile relative to the masonry facade. The image is perspective photography with no scale, camera calibration, CRS, or elevation.
- Purdue Archives and Special Collections, [Felix Haas Hall history](https://archives.lib.purdue.edu/agents/corporate_entities/563), confirms this is the former Memorial Gymnasium, built in 1908.
- Purdue Libraries' 1922 *Purdue Debris* publication (digitized copy: [Internet Archive scan](https://archive.org/details/purduedebris1922purd/page/n133/mode/2up)) describes the original pressed-brick, Bedford-limestone-trimmed building and red-tile roof. It supports material identity, not dimensions.
- The preserved GIS shell bounds in `reopen_check_round10.json` were reused without alteration: `[-26.2203, -25.9795, 0]` to `[12.9812, 26.7597, 11.5]` m. This is the only metric envelope used here; it does not measure roof height.

## Changes

- Reduced the roof rise from the R11 unsupported `1.8×` increase (4.14 m) back to 2.30 m above the existing 11.70 m eave. The main ridge is now Z=14.00 m; the entry-roof peak is Z=13.20 m. The estimate is visually conservative against the official exterior photograph and prior roof profile; no scaled elevation or permit drawing was found, so absolute ridge height remains unverified.
- Fitted the combined roof plan bounds to the GIS shell bounds plus a uniform 0.25 m eave on all four sides. Roof shape proportions were retained during plan calibration.
- Kept the GIS shell and placement origin unchanged. Export collection remains at 919 objects / 879 meshes.

The grader referred to the entire asset's `X=19.136 m` bound as roof projection. Fresh per-object measurement shows the roof's X+ bound is 13.2312 m, exactly 0.25 m beyond the shell. The far-positive X objects are the final two entrance treads and the low stone cheek walls. The broad asset bounds are not a roof measurement.

## Verification

- Blender 5.2.3 freshly reopened the exact saved SHA above.
- `round12_validation.json` reports PASS: both roof meshes sit at the expected eaves/peaks, their XY bounds match the unchanged GIS shell plus 0.25 m, and no external image/material-image dependencies were found.
- Rendered and visually inspected `exterior_round12.png` and `entrance_round12.png` after reopening.
- Geometry used by the building and all non-roof contents remain unchanged in this round.

## Remaining uncertainty

The official photo has no camera calibration or scale, and no permit elevation was found. The GIS data does not contain a surveyed roof surface. The 2.30 m roof rise and 0.25 m eaves are explicit modeling estimates calibrated to the available footprint and visual profile, not survey measurements. The existing entrance steps extend beyond the wall footprint by design; this is independent of the roof fit.
