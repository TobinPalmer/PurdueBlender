# Rawls Hall round 8 repair and reopen evidence

- Asset: `modular/buildings/rawls_hall.blend`
- Reopened saved asset SHA-256: `613174849a753f73aef4299d72223adeb0ceed01cf0fbc7aba4068d05bdf8088`
- Reopened scene/export collection: `Building_rawls_hall` / `Asset_rawls_hall` (722 objects; 714 meshes).
- No materialless meshes, external image files, linked libraries, or campus-local mesh-bound outliers were found. All image/material data remains self-contained.
- The root remains identity. The structural-shell matrix and mesh-geometry SHA-256 match the pre-edit snapshot exactly; the shell was not edited.

## Transform repair

The following six cameras and two meshes had `matrix_parent_inverse` translation `(-323.6582336426, +409.6224365234, 0)` before repair. It was reset to identity while preserving object locations and mesh vertices. Before/after full world matrices and three-axis world bounds are in `round8_final_evidence.json`.

| Object | Before world bounds X / Y / Z (m) | Reopened after bounds X / Y / Z (m) |
|---|---|---|
| `Cam_RAWL_01_North_StateSt` | -317.316 to -317.316 / 484.245 to 484.245 / 15.000 to 15.000 | 6.342 to 6.342 / 74.622 to 74.622 / 15.000 to 15.000 |
| `Cam_RAWL_02_NW_Curved_Rotunda` | -373.316 to -373.316 / 451.245 to 451.245 / 12.000 to 12.000 | -49.658 to -49.658 / 41.622 to 41.622 / 12.000 to 12.000 |
| `Cam_RAWL_03_West_GrantSt_Skywalk` | -392.316 to -392.316 / 389.245 to 389.245 / 10.000 to 10.000 | -68.658 to -68.658 / -20.378 to -20.378 / 10.000 to 10.000 |
| `Cam_RAWL_04_SE_Diagonal_Facade` | -262.316 to -262.316 / 364.245 to 364.245 / 16.000 to 16.000 | 61.342 to 61.342 / -45.378 to -45.378 / 16.000 to 16.000 |
| `Cam_RAWL_05_Roof_Arched_Penthouse` | -272.316 to -272.316 / 374.245 to 374.245 / 52.000 to 52.000 | 51.342 to 51.342 / -35.378 to -35.378 / 52.000 to 52.000 |
| `Cam_RAWL_06_Ortho_Footprint_Top` | -314.166 to -314.166 / 407.815 to 407.815 / 85.000 to 85.000 | 9.492 to 9.492 / -1.808 to -1.808 / 85.000 to 85.000 |
| `RAWL_Site_Sidewalk_Apron` | -355.004 to -273.337 / 383.396 to 432.233 / 0.012 to 0.012 | -31.346 to 50.321 / -26.226 to 22.610 / 0.012 to 0.012 |
| `RAWL_South_Windows_South_BronzeMullions` | -334.390 to -328.724 / 385.255 to 385.382 / 1.100 to 19.267 | -10.732 to -5.066 / -24.367 to -24.241 / 1.100 to 19.267 |

The sidewalk apron returned from the false bounds `X -355 to -273, Y 383 to 432` to its local apron extent `X -31.346 to 50.321, Y -26.226 to 22.610, Z 0.012`. The south bronze mullions returned from `X -334.390 to -328.724, Y 385.255 to 385.382` to `X -10.732 to -5.066, Y -24.367 to -24.241, Z 1.100 to 19.267`. Six saved cameras also returned from false world positions hundreds of metres away to their authored Rawls-local positions; exact full matrices are listed in the JSON record.

## Evidence renders

- North exterior: `north_exterior_round8.png`
- South full elevation: `south_exterior_round8.png`
- South aperture detail: `south_aperture_detail_round8.png`
- Sidewalk/apron context: `sidewalk_southwest_round8.png`

The R8 material adjustment made the existing shared architectural glass somewhat more transparent and reduced the brightness of both brick-texture mortar values by 18%; no mesh geometry changed. The south detail confirms glazing/frames at the existing eight south panes. The wider south elevation still has opaque-looking recesses beyond that limited pane group; correcting every south recess would require additional source-supported aperture geometry and was not included in this repair.

## Remaining uncertainty

- Approximate GIS/Plan1086 edge registration remains uncertain by about 1-2 m; this local conversion is not a survey-grade CRS.
- The 2024 Purdue plan supports the documented first-floor partitions. Upper-floor layouts and atrium circulation remain schematic/estimated.
- Rendered material appearance is an authored representation; no current source verifies exact facade colors or height.
- The round 8 repairs do not claim all remaining elevations are fully apertured or photographically verified.
