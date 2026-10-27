# Independent Alpha Epsilon Pi asset review

**Score: 7.5/10 — below the 8.0 target.** The footprint/placement and file integrity are strong; the remaining deductions are for unresolved identity, simplified facade presentation and the speculative, visually sparse interior.

| Category | Score | Reason |
|---|---:|---|
| Identity and evidence | 7.3 | Current Purdue BoilerLink address matches official GIS FID 754 address, and the roof overlay fits. GIS calls the same feature Chi Phi; the AEPi-to-building crosswalk is not conclusively resolved. |
| Placement and footprint | 9.8 | Independent comparison of the 60-vertex foundation to FID 754 yields IoU 0.99999995 and maximum corresponding vertex error under 0.000001 m. |
| Exterior form | 7.2 | Three-story brick/mansard character matches the broad 2009 AEPi photo cues, but the modeled side/rear wings and current roof are not validated by current facade imagery. |
| Facade and materials | 6.7 | Brick, trim, windows, doors and ΑΕΠ sign are present. Vertical tonal streaks dominate the brick; some side faces read as blank infill; window AC units and entry planting are not convincing at preview scale. |
| Interior | 4.6 | A representative program exists, but the preview is an overhead cutaway with suppressed partitions and small block furniture. The layout is illustrative, not sourced from a plan. |
| Technical integrity | 9.4 | Fresh-open check passes; 696 asset objects, 694 meshes, 20 materials, local coordinates, assigned parents, and no unpacked external textures. |

## Measurements and uncertainty

The model foundation exactly follows Purdue GIS FID 754 under the documented local projection: source area 569.0502295 m², asset area 569.0502174 m², IoU 0.99999995, and maximum corresponding vertex error 0.00000090 m. Placement origin is **[-948.801726, 959.296980] m**. These metrics establish geometry against FID 754; they do not resolve whether Purdue's `Chi Phi` name is stale or whether the current chapter house is at that exact footprint.

The current official BoilerLink page lists AEPi at 1051 David Ross Road. GIS FID 754 also has that address but is named Chi Phi. FID 821 is at 116 Fowler and is not used for this asset. No recent first-party image or plan directly verifies the current exterior/interior at 1051. The public Purdue AEPi photo used for style cues is dated 2009.

## Changes needed to reach 8+

1. Verify the AEPi occupancy of the 1051 David Ross roof with recent chapter or direct street imagery, or otherwise leave the crosswalk unresolved.
2. Compare current facades to imagery and refine roof profile, side/rear mass, window bays, wall material and AC placement.
3. Create a human-scale furnished interior view with visible room partitions and more convincing furniture/material detail.

Detailed metrics are in [result.json](result.json); the fresh-open snapshot is [asset_geometry_snapshot.json](asset_geometry_snapshot.json).
