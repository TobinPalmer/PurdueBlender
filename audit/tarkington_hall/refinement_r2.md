# Tarkington Hall refinement r2

## Asset

- Canonical building library: `modular/buildings/tarkington_hall.blend`
- SHA-256 after export-membership repair: `825D57329797FD45B6EB7784C8A6011F99A575BED6A97C11ED06E098EB618EE1`
- The master campus blend was not edited.
- Candidate and original backup are retained in this evidence folder.

## Sources and method

- Purdue campus BuildingShapesZip4 GIS layer 0, feature `FID=662`, code `TARK`, source CRS EPSG:4326; raw feature snapshot: [`gis_feature_662.json`](gis_feature_662.json). Provider: [Purdue University ArcGIS FeatureServer](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0). Snapshot retrieved 2026-10-22. The geometry was transformed to the project-local meter frame using the project's documented approximate geographic conversion.
- Spring 2023 Indiana orthophoto, 6-inch imagery service: [Indiana 2023 Imagery ImageServer](https://di-ingov.img.arcgis.com/arcgis/rest/services/DynamicWebMercator/Indiana_2023_Imagery/ImageServer). Evidence image [`indiana_2023_ortho_r1.png`](indiana_2023_ortho_r1.png) covers bbox `[-86.922, 40.429, -86.918, 40.433]` in EPSG:4326; downloaded 2026-10-25.
- Housing program references: [Purdue Tarkington Hall housing page](https://www.housing.purdue.edu/my-housing/options/residence-halls/tarkington.html) and [Tarkington emergency plan](https://www.purdue.edu/operations/emergency-preparedness/tark/). The emergency plan identifies the East/West wing system and four occupied floors; the housing page describes the typical 11 ft 7 in × 16 ft 2 in room. The model's single representative Room 118 stays 5.6 × 4.4 m, matching the modeled internal room extents; the published room dimensions are approximate planning information, not a survey.

The official GIS outline is not documented as a surveyed wall-face polygon. It may follow roof edges, eaves, or another cartographic edge. I aligned the four arm shell outlines with straight mid-wing boundaries visible in both GIS and orthophoto. Metrics below therefore compare modeled shell to the mapped outline/roof proxy; they do not establish exact wall offsets. The North connector glazing rhythm follows the existing dorm window bay pattern and should be treated as extrapolated detail.

## Changes

- Locally narrowed/repositioned the NW, SW, NE, and SE structural wing meshes in X; the dimensions of the representative room and its furniture were preserved.
- Shortened the southeast wing to the asymmetric roof termination in the GIS/orthophoto evidence.
- Repositioned the 384 wing side-wall windows/sills and adjusted the horizontal width of 192 north/south end-facade openings to avoid overlaps after the footprint correction.
- Moved the eight associated roof penthouses/HVAC elements with their respective wings.
- Added two north connector bridges between the north entrance volume and the shortened wing masses, with brick shafts, limestone base/belts, roof finish, parapet, and 80 room-bay windows. These restore the connected north roof visible in the source overlay.
- Retained the existing core, courtyard features, roof elevations, floor levels, and representative dorm-room furnishings.

## Checks

Fresh Blender 5.2.3 reopen of the canonical asset succeeded. The file has 910 objects, 891 meshes, 16 used materials, zero meshes with non-finite coordinates, and zero material-less meshes. The asset root remains present and the Room 118 floor remains 5.6 × 4.4 m.

The first independent R2 review scored 5.9/10 because the 96 newly added connector meshes were linked to the scene collection but omitted from `Asset_tarkington_hall`. That export-membership defect is repaired: 48 west connector objects and 48 east connector objects are now linked only to `Asset_tarkington_hall`, retain their original parent/world matrices/materials, and have no duplicate names. The export collection now contains all 910 asset objects. The footprint extraction was rerun against this collection only; its result below includes the north bridge shell. A new independent grade is pending.

Structural-shell-to-GIS metrics, using the same shell candidate list as the prior audit plus the new north connector structural objects:

| Metric | Before r2 | After r2 |
|---|---:|---:|
| Polygon IoU | 0.487 | 0.688 |
| Mean symmetric sampled boundary residual | 5.03 m | 2.10 m |
| P95 symmetric boundary residual | 13.36 m | 9.37 m |
| Symmetric Hausdorff distance | 17.96 m | 11.34 m |
| Shell polygon area | 6,810 m² | 4,392 m² |

The reported P95/Hausdorff residuals remain high because the central/core outline and selected shell proxy still differ from the mapped outline; they should not be hidden by the improved four-wing overlay. Exact before/after calculations are in [`footprint_comparison_r1.json`](footprint_comparison_r1.json) and [`footprint_comparison_r2.json`](footprint_comparison_r2.json).

## Visual evidence and status

- [2023 orthophoto overlay, corrected shell blue / GIS red](ortho_footprint_overlay_r2.png)
- [Exterior render](exterior_r2.png)
- [Representative dorm-room cutaway](room_r6.png). Room walls are hidden in this evidence render to show the unchanged sample furniture; this is not a view saved into the library.
- [Connector export-membership audit](connector_export_membership_r3.json)
- [Canonical-file reopen validation log](verify_canonical_r3.log)
- [Correction parameters and source uncertainty](correction_r2.json)

The connector and wing form now follow the available roof footprint much more closely, but the core outline and the GIS wall-versus-roof edge meaning remain unresolved. Independent grading is pending; do not mark this building complete until a separate grader scores it at least 8/10 against source evidence.
