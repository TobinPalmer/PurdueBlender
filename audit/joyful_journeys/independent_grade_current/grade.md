# Independent Grade — Joyful Journeys

**Score: 8.0/10 — PASS for candidate.** The reviewed file is unchanged from the prior r2 grade: its SHA-256 is `0C42DE5F5392125F13F6B0DEFC0491F814602788E035477A3D2F4E7EC1D8DEC8`. At the time of grading, the manifest Z maximum was stale at 16 m; the coordinator has since corrected it to 8.76 m, matching the fresh-open measurement.

I reopened the exact asset in Blender 5.2.3. The expected scene and collection contain one `Joyful Journeys` mesh with 886 vertices and 218 faces. It has seven node materials, identity transform, no modifiers, no linked libraries, and no external image dependencies. Its reopened bounds are X `[-104.04565, -65.91480]`, Y `[2056.23877, 2078.08032]`, Z `[0, 8.76000]` m.

| Criterion | Score | Review |
| --- | ---: | --- |
| Identity and footprint | 1.8/2 | The official operator site confirms the address at the northwest corner of Lindberg/Salisbury; the 2019 guide image shows the entry number 600. OSM way 869182111 has the matching name/address, and its roof-edge outline registers on the saved Esri aerial. OSM is a roof/perimeter proxy, not a surveyed wall footprint. |
| Position and dimensions | 1.7/2 | The asset retains campus-world coordinates at identity transform. Its XY bounds match the source ring under the project's approximate local transform, and the aerial placement is visually consistent. No survey control exists, so position and dimensions remain map-level estimates. |
| Height and roof | 1.2/2 | The front gable and upper windows are photo-supported; the aerial supports a multi-facet roof. Two levels, 5.4 m eaves, and an 8.7 m peak are estimates, not measured elevations. |
| Facade and materials | 1.5/2 | Green-gray siding, light trim, dark shutters, gable windows, and covered entry reflect the available photo. The materials are solid-color shaders without siding/roof texture detail. The photo's stone accent and porch rail/columns are simplified or absent; unseen facades are schematic. |
| Portability and evidence | 1.8/2 | The expected collection reopens cleanly with no file dependencies, and the prior 8.0/10 r2 grade is verified against the exact same binary. The manifest bounds were stale during this assessment, then corrected by the coordinator to the reopened maximum Z of 8.76 m. The asset remains direct-linked in campus coordinates. No reliable interior plan was found, and the asset has no modeled interior. |

The current [Joyful Journey operator site](https://joyfuljourneywl.org/) identifies the 600 Lindberg Road location and day-service use. The saved OpenStreetMap and Esri snapshots corroborate the roof placement. The 2019 Area IV guide provides the only reviewed exterior photo; it supports visible facade cues but has no scale or north orientation. Tippecanoe County's 2014 Z-2571 case supports site/use context, not architectural measurements.

**Post-grade correction:** the coordinator updated manifest `bounds_world_m`, `exterior_bounds_world_m`, and `source_bounds_world_m` to the candidate bounds, including Z `[0, 8.76]` m. The asset remains direct-linked in campus coordinates, and no interior is modeled. Height, roof details, exact material colors, and unseen elevations remain uncertain.
