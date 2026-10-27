# Independent Grade — Ralph & Bettye Bailey Hall

**Score: 8.1/10 — PASS for candidate.** Final status still requires coordinator integration into the master placement marker and a master fresh-open check.

The reviewed file is `modular/buildings/massing_ralph_bettye_bailey_hall_406c4db.blend`, SHA-256 `99E0F25C9028151179F7C28A98F2B358AD65B64C4F4BDBBC81F8658816F23B76`. I reopened this exact file in Blender 5.2.3. It contains the expected scene, collection, and single mesh object, with 13,408 vertices, 4,698 faces, nine materials, and 2,610 room-zone faces. All four project-relative brick image files resolve.

| Criterion | Score | Finding |
| --- | ---: | --- |
| Identity and GIS footprint | 2.0/2 | FID 411/BALY identity is supported. The shell uses all 22 unique GIS ring vertices. The local-conversion area (842.12 m²) agrees with the independent UTM cross-check (841.96 m²). The campus GIS line is not a surveyed wall trace. |
| Position, orientation, dimensions | 1.5/2 | Proposed placement is the polygon centroid `(308.0089, -22.7483)` m, while the source model is correctly local at identity transform. The final master marker is still pending integration verification; photo references do not verify true-north orientation or survey placement. |
| Height, floors, roof | 1.25/2 | Flat roof, two visible rows, and a raised entry volume are supported by the Purdue photo. The 7.5 m parapet and 10.18 m tower are estimates. GIS lists five floors, which conflicts with the two visible above-grade window rows. |
| Facade and materials | 1.75/2 | Red brick, light trim, two window rows, glazed entry, sign panel, and canopy read clearly and are largely photo-supported. Unseen sides and exact feature proportions remain generalized. |
| Interior, modularity, evidence | 1.6/2 | The file is modular and portable with its linked texture files. The interior is a flat, color-coded room diagram sourced from Purdue's first-floor plan, not 3D partitions or a walkable interior. The plan's scale, north orientation, and precise room positions remain schematic. |

Reviewed primary sources: Purdue GIS FID 411; Purdue OEP's [Bailey Hall page](https://www.purdue.edu/operations/emergency-preparedness/baly/) with current exterior photo and first-floor plan; and Purdue Archives' [historical exterior image](https://blogs.lib.purdue.edu/asc/2016/12/01/bailey-hall-and-purdues-musical-myth/). Fresh-open measurements are recorded in `fresh_open.json`; the structured rubric is in `grade.json`.

**Integration notes:** Set the master marker to the proposed origin, reopen the master, verify no duplicate massing remains and inspect the building in campus context. Keep height and interior uncertainties visible in the shared record.
