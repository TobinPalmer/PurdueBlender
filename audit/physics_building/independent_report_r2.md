# Physics Building — independent R2 grade

**Grade: 8.4/10 — pass.** I independently reopened the exact saved asset and checked the current manifest and root master link against Purdue GIS FID 273. Asset SHA-256: `7dc4f484c84cb0f7c5e6c5c676cf4d3e0e7fb80f434fe4862c1efd4fb342a7f5`.

| Criterion | Score |
| --- | ---: |
| Identity and source-backed footprint | 2.0/2 |
| Position, orientation, and scale | 2.0/2 |
| Supported floors, height, and roof form | 1.5/2 |
| Facade, main entrance, and distinctive features | 1.6/2 |
| Materials, interior, modular export, and evidence | 1.3/2 |
| **Total** | **8.4/10** |

## Findings

- **Identity and footprint:** Purdue GIS feature FID 273 identifies PHYS at 525 Northwestern Avenue. In a fresh Blender 5.2.3 reopen, I compared the 33 unique XY vertices of `PHYS | GIS footprint brick envelope` with the one-ring GIS polygon after the project transform. The maximum nearest-vertex deviation in both directions was 0.00000054 m.
- **Placement and scale:** The manifest campus origin matches the GIS-derived project origin. I reopened the root master without saving and checked its `Placement_physics_building` marker: its location differs from the manifest by 0.00000035 m, scale is one, rotation is zero, and it instances the expected collection from the expected asset path. The linked master collection contains the current 319 objects and is not linked directly to the scene root.
- **Height and roof:** Purdue GIS F01/F02/F03 elevations (13, 27.1, 40.15 ft) and roof datum R=52.25 ft support the model's approximate three-story datums and height. Purdue photos show a three-story brick building with a low red tiled roof. Exact wall height, roof pitch/thickness, and basement dimensions remain uncertain: GIS `NUM_LEVELS=8` and `Extrution=84` conflict with the F-level fields/photos, and no measured section was located. Asset top is about 0.17 m above the nominal R datum.
- **Facade and entrance:** The R2 render is a clear improvement over R1: taller divided sash frames, more visible brick coursing, pale horizontal bands, eave/cornice relief, a central PHYSICS panel, and three entrance bays read more clearly. The review exterior also includes Northwestern Avenue frontage elements as render-only context. A glazed skybridge and secondary arch are present. Window/door counts and dimensions, some masonry detail, the roof profile, and bridge structure remain interpretive.
- **Materials, interior, and export:** Blender reopened the saved `Asset_physics_building` collection with 319 objects and 317 meshes. The shared manifest object-name list/count and local bounds now match exactly; all meshes have material slots, there are no missing external image dependencies, and procedural Brick Texture nodes occur in the masonry and roof materials. R2 adds level-separated schematic floor plates and partitions guided by Purdue evacuation-plan functions. The interiors remain sparse and schematic rather than a verified as-built layout.

## Remaining deductions

The model passes because the source-backed footprint and campus placement are exact within the project transform, the three visible floors and approximate roof datum have GIS/photo support, and R2's facade, materials, and modular records are substantially improved and now verified in the master. The score remains below 9 because the GIS level attributes conflict, the roof geometry and some facade details are still estimated, and the interior partitioning/furnishing is schematic rather than fully verified.

## Evidence inspected

- Independent asset reopen, footprint, manifest inventory/bounds and material check: `independent_reopen_r2.json` and `independent_reopen_grade_r2.py`.
- Read-only master placement/link check: `independent_master_marker_r2.json` and `independent_master_marker_r2.py`.
- Current render views: `physics_building_front_nw_preview.png`, `physics_building_entry_detail_preview.png`, `physics_building_roof_detail_preview.png`, `physics_building_interior_cutaway_preview.png`, and `physics_building_interior_ground_plan_preview.png`.
- GIS source snapshot: `physics_building_fid273_gis_snapshot.json`.
- Purdue photo references: `purdue_physics_official_facade.jpg`, `purdue_physics_official_entrance.jpg`, and `purdue_physics_event_2022.jpg`.
- Purdue source pages: [Physics department exterior photo](https://www.physics.purdue.edu/xia/contact.html), [Physics Building event page](https://events.purdue.edu/physics_building), [campus resources entrance photo](https://www.physics.purdue.edu/academic-programs/undergraduate/campus_resources.html), [Physics Building evacuation plans](https://www.physics.purdue.edu/docs/resources/PHYS-Building-Evacuation-Routes.pdf), and [Purdue GIS FID 273](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D273&outFields=*&returnGeometry=true&outSR=4326&f=pjson).
