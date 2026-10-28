# Independent review — Meredith Hall South, final first-pass revision

- **Result:** 8.075/10 (displayed as 8.08/10) — **passes** the 8.0/10 first-pass threshold. The unrounded score is above threshold.
- **Asset:** `modular/buildings/massing_meredith_hall_south_ffbc444.blend`
- **Reviewed SHA-256:** `0C53215206436F8C75ABB788F0355FCAAC15ED25FE397A9DCB25A4189359142D`
- **Review date:** 2026-10-28
- **Method:** Fresh-opened the exact saved file in Blender 5.2.3 and inspected the saved exterior, reverse exterior, level-3 plan and Purdue’s 2020 exterior photo. The saved asset was not edited.

## Score

| Criterion | Weight | Score | Weighted points |
| --- | ---: | ---: | ---: |
| Identity and provenance | 20% | 9.5/10 | 1.900 |
| Plan geometry and placement | 25% | 9.5/10 | 2.375 |
| Exterior silhouette and openings | 25% | 7.0/10 | 1.750 |
| Materials and facade | 10% | 7.5/10 | 0.750 |
| Interior / cutaway | 10% | 5.5/10 | 0.550 |
| Presentation and technical quality | 10% | 7.5/10 | 0.750 |
| **Total** | **100%** |  | **8.075/10** |

## Review notes

The revisions address the prior report’s main findings. The front preview now shows a taller west section, lower B/C wings, darker brick, glazed base/bays, a First Street canopy and columns, and east retail panels. Purdue’s 2026-10-16 emergency plan confirms west A has eight floors, middle B and east C have six each, B has a basement, and the east/C first floor has two retail food operations. The asset contains the corresponding named components, and the fresh-open check reports an 8/6/6 model with a B basement.

The official Purdue BuildingShapes feature identifies FID 410 as Virginia C. Meredith Residence Hall South. The current reopen record reports source-derived shell bounds within 0.000022 m of the transformed GIS bounds. This supports the footprint extents, but I did not independently measure every perimeter edge or verify master placement. The project’s geographic conversion remains an approximation, not survey control.

The official Purdue 2020 photo supports the red-brown brick, repeated windows, glazed vertical bay and public ground-floor character. The revised render is a stronger match. Its reverse view still shows a stack of large white triangular projections at the far west end. I could not verify those shapes from the available photo, so they remain an unresolved visual issue rather than a proven mismatch. Only one exterior photo was inspected; other facades and the exact orientation of entries/glazing remain unverified.

The interior now has corridor floors, room partitions, beds and desks across eight levels. Purdue Residences’ typical-room illustration supports the module dimensions, but the supplied plan view reads as a simplified linear corridor/room diagram. Bathroom and lounge pod locations, and the building-wide layout, are not verified by the inspected sources.

A direct fresh open in Blender 5.2.3 found the expected export collection with 56 objects, including 54 meshes and 40 named interior objects. The current reopen check reports closed shell, roofs and basement. The exterior/reverse/plan render set makes the revised asset reviewable, although the plan is low contrast and the west-end projections are distracting.

## Sources inspected

- Purdue BuildingShapes, [FID 410](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/410?f=pjson), local snapshot `audit/official_purdue_buildings_wgs84.json`.
- Purdue Newsroom, [student housing facilities opening](https://www.purdue.edu/newsroom/archive/releases/2020/Q3/student-housing-facilities-open-on-purdues-west-lafayette-campus.html), photo saved at `audit/meredith_hall_south/source_purdue_meredith_south_2020.jpg`.
- Purdue Office of Emergency Preparedness, [Meredith South emergency plan](https://www.purdue.edu/operations/emergency-preparedness/mrds/) (revision 2026-10-16).
- Mackey Mitchell Architects, [Meredith South project](https://www.mackeymitchell.com/projects/meredith-residence-hall-south/).
- Purdue University Residences, [Meredith South](https://housing.purdue.edu/my-housing/options/residence-halls/meredith-south.html), typical single-room illustration.
- MSKTD, [Meredith South Residence Hall](https://msktd.com/project/purdue-university-meredith-south-residence-hall/).

The score is a first-pass visual grade only; master integration was not part of this review. Remaining non-blocking corrections are to verify the reverse west-end projections, make both retail storefronts legible in close views, and improve the level-3 plan’s contrast/readability. The detailed score, source list, uncertainty and checks are in [`independent_grade_meredith_south_r2_2026-10-28.json`](independent_grade_meredith_south_r2_2026-10-28.json).
