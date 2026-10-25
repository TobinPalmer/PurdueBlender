# Physics Building — independent R1 grade

**Grade: 7.6/10 — below the 8/10 completion threshold.** I reopened the exact saved Blender 5.2.3 asset and independently compared the structural footprint mesh to Purdue GIS FID 273. Asset SHA-256: `e7c2bb0062b6a692b57618352f569e7910d38ecefbd688263a73cb390a5f7620`.

| Criterion | Score |
| --- | ---: |
| Identity and source-backed footprint | 2.0/2 |
| Position, orientation, and scale | 1.9/2 |
| Supported floors, height, and roof form | 1.0/2 |
| Facade, main entrance, and distinctive features | 1.4/2 |
| Materials, interior, modular export, and evidence | 1.3/2 |
| **Total** | **7.6/10** |

## Findings

- **Identity and footprint:** Purdue GIS feature FID 273 identifies PHYS at 525 Northwestern Avenue. In a fresh reopen, I compared the 33 unique XY vertices of `PHYS | GIS footprint brick envelope` with the one-ring GIS polygon after the documented project transform. The maximum nearest-vertex deviation in both directions was 0.00000054 m. This is strong agreement in the project coordinate conversion, though that conversion is approximate rather than surveyed.
- **Position and scale:** The source asset has the correct local orientation and its campus origin in the manifest, `[20.732372, 300.324127]`, agrees with the source evidence. Reopened total mesh bounds are approximately 106.446 by 120.520 m including facade relief. I did not reopen the root master or its placement marker during this independent grade.
- **Height and roof:** The model shows the photo-supported three principal stories and low red roof. Purdue GIS records `R=52.25 ft`, but also reports `NUM_LEVELS=8` and `Extrution=84`; the source record appropriately flags these conflicts. There is no measured elevation or section supporting the modeled wall height, story intervals, roof pitch, or basement-window sizes. The roof appears as a broad, nearly flat cap in the submitted NW view, and its tile detail is difficult to see.
- **Facade and entrance:** The asset adds running-bond brick, dark window bays, pale bands, the central PHYSICS panel, three glazed entry bays, steps/rails, a secondary arched portal, and a glazed skybridge. Those details broadly match the Purdue photos. The facade is still schematic: the reference windows are taller and have more framing detail, while the model repeats simple, mostly square openings. The main entrance and cornice are simplified, and the gray isolated preview omits the observed frontage and landscape context.
- **Materials, interior, and export:** Blender reopened the named asset collection with 175 objects and 173 meshes. Every mesh has material slots, there are no missing external image dependencies, and a procedural Brick Texture is connected to the masonry material's Principled Base Color. A schematic vestibule, twelve table/monitor sets, entrance stairs, and a multi-part skybridge are present. Interior rooms and floor-by-floor layouts are not source-verified. The shared manifest still records 110 objects rather than 175 and has a small vertical-bound discrepancy. The master library link has not been refreshed or checked.

## Why it did not pass

The GIS outline and placement transform are strong, and the new exterior/material work is meaningful. The supported vertical form and roof remain uncertain, the photographed facade has substantially more window/entrance detail than the current model, the interior is only schematic props, and the manifest is stale for this saved asset. These gaps justify 7.6/10 rather than a completion grade.

## Evidence inspected

- Reopen and geometry comparison: `independent_reopen_r1.json` and `independent_reopen_grade_r1.py`.
- Asset/evidence previews: `physics_building_front_nw_preview.png`, `physics_building_side_sw_preview.png`, and `physics_building_evidence.json`.
- Purdue GIS snapshot: `physics_building_fid273_gis_snapshot.json`.
- Purdue photos: `purdue_physics_official_facade.jpg`, `purdue_physics_official_entrance.jpg`, and `purdue_physics_event_2022.jpg`.
- Purdue source pages: [Physics department exterior photo](https://www.physics.purdue.edu/xia/contact.html), [Physics Building event page](https://events.purdue.edu/physics_building), [campus resources photo](https://www.physics.purdue.edu/academic-programs/undergraduate/campus_resources.html), and [Purdue GIS FID 273](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D273&outFields=*&returnGeometry=true&outSR=4326&f=pjson).
