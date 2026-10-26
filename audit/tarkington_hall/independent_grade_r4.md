# Tarkington Hall — independent R4 grade

**Score: 8.0/10 — passes the 8.0 threshold.**

Exact candidate evaluated: `tarkington_hall_r4_candidate.blend`  
SHA-256: `b844a77e35ad44bf722ea0432ed40dc47a6b01fff24c095cbabf68e760f87065`

I opened the candidate in a separate Blender 5.2.3 LTS process and independently re-extracted its shell. The R4 shell follows the Purdue GIS/orthophoto four-wing outline closely: **0.9525 IoU**, **0.61 m mean symmetric boundary residual**, and **2.22 m P95**. The **8.70 m Hausdorff maximum** is a localized outlier and remains a caveat. The map ring is not documented as a surveyed wall-face boundary, so the comparison is best treated as agreement with the roof/edge proxy.

| Criterion | Score | Evidence and remaining uncertainty |
| --- | ---: | --- |
| Identity and source-backed footprint | 1.90/2.00 | Purdue FID 662/TARK and 2023 orthophoto identify the asset; the independent structural-shell overlay closely follows the four wings and core. Generalized GIS edge meaning and the localized Hausdorff outlier remain uncertain. |
| Position, orientation, and scale | 1.20/2.00 | Root transform is identity and plan bounds agree closely in the local comparison frame. The master placement marker was not freshly checked in this grading pass; the local geographic conversion is approximate. |
| Floors, height, and roof | 1.30/2.00 | Four occupied East/West wing floors are supported by Purdue’s current emergency plan. The 19.1 m roof/penthouse extent is estimated; no measured elevation was found. |
| Facade, entrance, and interior program | 1.75/2.00 | Four wings, brick facade, repeated windows, floor bands, core/entry masses, and new lobby, dining/recreation, and standard-room cutaways are present. Fine facade details and room positions remain simplified/schematic. |
| Modular export, materials, portability, and evidence | 1.85/2.00 | Exact file reopens; 1,361 objects/1,342 meshes, 329 connector objects correctly included and parented, 22 used materials, and no broken dependencies or mesh-integrity errors. Full topology and marker checks were not performed. |
| **Total** | **8.00/10** | **Pass.** |

## Independent checks

- Fresh Blender reopen, collection membership, materials, dependencies, identity root, and bounds: [`independent_grade_r4_reopen.json`](independent_grade_r4_reopen.json).
- Freshly extracted structural-shell comparison against the source GIS ring: [`independent_grade_r4_footprint.json`](independent_grade_r4_footprint.json).
- Independent top-down footprint overlay: [`independent_grade_r4_footprint_overlay.png`](independent_grade_r4_footprint_overlay.png).
- Reproducible evaluator and extraction scripts: [`independent_grade_r4_evaluator.py`](independent_grade_r4_evaluator.py), [`independent_grade_r4_reopen.py`](independent_grade_r4_reopen.py), and [`independent_grade_r4_footprint.py`](independent_grade_r4_footprint.py).

## Sources

- [Purdue GIS BuildingShapesZip4, feature FID 662 / TARK](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/662?f=pjson), EPSG:4326; snapshot retrieved 2026-10-22.
- [Indiana 2023 Imagery service](https://di-ingov.img.arcgis.com/arcgis/rest/services/DynamicWebMercator/Indiana_2023_Imagery/ImageServer); 6-inch 2023 imagery downloaded 2026-10-25.
- [Purdue Housing: Tarkington Hall](https://www.housing.purdue.edu/my-housing/options/residence-halls/tarkington.html), current room dimensions and furnishings.
- [Purdue Emergency Preparedness: Tarkington plan](https://www.purdue.edu/operations/emergency-preparedness/tark/), revised 2026-10-13; supports four occupied floors per East/West wing and central program uses.
- [Purdue University Residences: Tarkington exterior image](https://housing.purdue.edu/images/_hero/tarkington-exterior-640x360.jpg).

## Remaining uncertainty

The model passes the requested threshold, but this grade does not certify surveyed wall offsets, exact roof elevation, or measured room layouts. The coordinator should separately verify `Placement_tarkington_hall` in the complete saved master before integration.
