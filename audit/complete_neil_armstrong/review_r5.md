# Neil Armstrong Hall — R5 LiDAR-derived wing envelopes

## Result

R5 adds three coarse solid masses to the individual source asset. Public 2018 Tippecanoe NDHM cells show a connected height surface over most of the official Purdue GIS footprint. When the cells are registered into Neil's existing local frame, they provide enough evidence for broad missing wing envelopes and approximate top heights. The asset now contains 447 collection objects; the root, existing shell objects, local origin, and master placement marker remain unchanged.

The 2018 5-ft NDHM was clipped to official GIS BuildingShapesZip4 feature 642 and divided into 14–18m, 18–20m, and 20–40m bands. Each coarse mass is limited to those registered cells outside the current modeled shell's bounding rectangle. The final cap height uses the measured median of the outside-shell NDHM samples in its band:

| Mass | NDHM samples | Median top | p10–p90 | Modeled plan area |
|---|---:|---:|---:|---:|
| Lower wing band (14–18m) | 336 | 15.78m | 15.26–17.72m | 772m² |
| Mid wing band (18–20m) | 458 | 19.48m | 18.39–19.82m | 1,087m² |
| Higher roof zone (20–40m) | 530 | 21.55m | 21.45–21.66m | 1,265m² |

The highest mask is 20–40m because the source raster has two cells above 22m; its p90 remains below 21.66m and the median used for the mass cap is 21.55m. This preserves an honest broad height zone without treating isolated cells as a tower.

## Geometry and evidence boundaries

- New meshes use the existing Purdue red-brick material and the official feature 642 outline as the GIS limit. Their cutouts preserve the polygon's open courtyard/notch.
- The current modeled shell's axis-aligned extent was subtracted only as a practical clipping aid. That rectangle is not treated as a measured wall plan; exact wall lines inside the omitted GIS area remain unknown.
- The orthophoto and the NDHM align to one connected multi-wing building footprint, supporting broad roof-mass placement. The aerial roof edge can overhang ground walls; the 5-ft raster cannot recover exact facade or roof edges.
- The added meshes are schematic mass envelopes, not floor plans or complete modeled facades. They contain no newly inferred floor slabs, windows, doors, penthouse, HVAC, or room layout. No claim is made about number of stories, accessible paths, or exact roof shape.
- The raster date range is 2017–2019, while the paired aerial is 2023. Neither confirms current construction state.

## Validation

The saved asset was reopened read-only after writing. The source still has scene `Building_neil_armstrong_hall`, collection `Asset_neil_armstrong_hall`, 447 objects, and a root at `[0, 0, 0]`. The eight original wall meshes retain bounds `[-63, 63] × [-29.689, -3.189] × [0, 19.5]m`. The three added meshes are attached to the identity root frame; every edge in each new closed envelope is shared by exactly two faces. See [validation_r5.json](validation_r5.json).

Review images:

- [Exterior oblique render](renders_r5/exterior_lidar_wings_r5.png)
- [LiDAR height mask over registered aerial](lidar_roof_height_r5.png)

The geometry remains visibly coarse. A dimensioned as-built plan/elevation or surveyed wall/roof outlines are still required before adding facade rhythms, floor layouts, or exact roof details. No changes were made to the master blend, manifest, shared files, or other buildings.
