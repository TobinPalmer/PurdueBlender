# Tarkington Hall R4 candidate and audit handoff

## Frozen candidate

- Candidate library: `tarkington_hall_r4_candidate.blend`
- SHA-256: `B844A77E35AD44BF722EA0432ED40DC47A6B01FFF24C095CBABF68E760F87065`
- Blender 5.2.3 LTS reopened this exact SHA in a fresh process. Validation is in [`reopen_validation_r4.json`](reopen_validation_r4.json).
- R4 is staged only in this building-specific audit folder. The canonical building library and campus master were not changed by this refinement; the canonical SHA remains the R3 SHA `825D57329797FD45B6EB7784C8A6011F99A575BED6A97C11ED06E098EB618EE1`.

## Geometry and footprint

R4 locally reworked the west/east wing shell profiles, adjusted associated openings, shortened the north connector depth, added the missing east-west core wings, widened the north pavilion, and separated the south entry pavilion from the documented lobby/core mass. The overlay [`ortho_footprint_overlay_r4.png`](ortho_footprint_overlay_r4.png) compares the corrected shell outline (blue) with the Purdue GIS outline (red) on the Spring 2023 Indiana orthophoto.

Fresh extraction was made only from meshes linked to `Asset_tarkington_hall`. The selected shell union has 5,375.67 m² area against 5,501.74 m² for Purdue GIS FID 662, IoU 0.9525, mean symmetric sampled boundary residual 0.61 m, and P95 2.22 m. The symmetric Hausdorff distance remains 8.70 m; this is a localized extreme and should be reviewed against the source overlay rather than treated as the typical residual. Full calculations and bounds are in [`footprint_comparison_r4.json`](footprint_comparison_r4.json).

**Boundary uncertainty:** Purdue GIS FID 662 is not documented as surveyed wall faces. Model profiles are fitted to straight roof edges visible in the Spring 2023 orthophoto, so the GIS outline may represent roof edges/eaves or another cartographic edge. Metrics describe agreement with that mapped proxy, not measured wall offsets. The geographic-to-local conversion is approximate.

## Program and interior evidence

The candidate includes the existing central lobby/reception/mail and Pete’s Za/SharkTank recreation areas, plus north common lounge/study/piano furnishings. The separate views are evidence cutaways: exterior shells are hidden for these renders only; the saved asset geometry is unchanged.

- [Exterior model render](exterior_r4.png)
- [Lobby/reception/mail cutaway](lobby_cutaway_r4.png)
- [Dining and recreation cutaway](dining_recreation_cutaway_r4.png)
- [Approximate standard double-room plan](standard_double_room_program_r4.png)
- [Orthophoto footprint overlay](ortho_footprint_overlay_r4.png)

A separately labeled sample double room is modeled at Purdue Housing’s approximate published dimensions, 11 ft 7 in × 16 ft 2 in (about 3.53 × 4.93 m), with two beds, desks/chairs, closets, a dresser, and a window. This is a program-based representative module; its location inside the west wing and exact furnishing coordinates are schematic because no measured room plan or surveyed room coordinates were identified. The older Room 118 asset stays as it was modeled previously and should not be mistaken for a measured room.

The 19.1 m highest roof/penthouse extent is explicitly an estimate: the sources reviewed give no measured as-built roof elevation. Four occupied floors are supported by Purdue’s Emergency Preparedness plan.

## Source records

- Purdue BuildingShapesZip4 GIS, feature FID 662 / TARK, EPSG:4326, snapshot retrieved 2026-10-22: [`gis_feature_662.json`](gis_feature_662.json); [Purdue ArcGIS feature service](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0).
- Spring 2023 Indiana 6-inch orthophoto, bbox `[-86.922, 40.429, -86.918, 40.433]`, downloaded 2026-10-25: [`indiana_2023_ortho_r1.png`](indiana_2023_ortho_r1.png); [Indiana 2023 Imagery service](https://di-ingov.img.arcgis.com/arcgis/rest/services/DynamicWebMercator/Indiana_2023_Imagery/ImageServer).
- Purdue Housing Tarkington page, accessed 2026-10-25; documents approximate standard room dimensions and room furnishings: [Tarkington Hall housing page](https://www.housing.purdue.edu/my-housing/options/residence-halls/tarkington.html). A local snapshot of its SVG room-layout illustration is [`purdue_standard_room_layout_source.svg`](purdue_standard_room_layout_source.svg).
- Purdue Emergency Preparedness Tarkington plan, accessed 2026-10-25; documents four occupied floors and central/west/east-wing programs: [Tarkington emergency plan](https://www.purdue.edu/operations/emergency-preparedness/tark/).

## Independent review handoff

R3 scored 7.2/10. R4 addresses the principal footprint mismatch and lack of central-program/room evidence. Please assign a fresh independent grader against this exact R4 SHA and the saved source/render evidence. Do not mark the building complete unless that independent grade reaches 8/10. Placement marker verification remains a separate read-only master-file check for the coordinator.
