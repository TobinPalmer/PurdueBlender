# Life Science Plant and Soils Laboratory — Independent Review R3

**Score: 7.3/10 — below the 8/10 finish threshold.**

| Category | Score |
| --- | ---: |
| Identity and footprint | 1.8/2.0 |
| Placement, orientation, and scale | 1.4/2.0 |
| Height, floors, and roof evidence | 1.1/1.5 |
| Exterior and materials | 1.0/2.0 |
| Interior, program, and circulation | 1.0/1.5 |
| Technical portability and evidence | 1.0/1.0 |
| **Total** | **7.3/10** |

## Findings

- **Identity and footprint:** Purdue BuildingShapes feature 917 is the correct building. The ground, three upper slabs, and two newly added below-grade plates match the transformed 12-vertex GIS ring within 0.00001 m in local XY. This confirms the model reproduces the selected GIS polygon; it does not establish the as-built basement extent or surveyed structural wall line. The single selected GIS ring contains no courtyard.
- **Placement, orientation, and scale:** The new Indiana GIO 2023 orthophoto overlay is useful independent visual evidence: the GIS polygon follows the visible LSPS roof perimeter closely and confirms its long east-west axis. This materially improves the earlier unverified orientation/position assessment. The overlay is not a surveyed control comparison, and the master marker check only shows that the manifest marker equals the model author's transformed GIS bbox midpoint. The Google Maps point is a plausible vicinity check, not an authoritative building control point. Campus-scale position error therefore remains unmeasured.
- **Height, floors, and roof evidence:** The orthophoto supports a broad light-colored flat roof and multiple small roof units. However, the top preview shows four inherited rooftop boxes sitting beyond the narrow north roof projection; three visibly extend outside the roof outline. The tall dark stack at the opposite roof edge is also not corroborated by the orthophoto evidence. Eight additional units are a reasonable schematic response but their number and positions are not established. The height mismatch is now recorded honestly: modeled above-grade datums are about 9 ft apart, while the GIS F01–F04 fields differ by 12 units; GIS vertical units/semantics remain undocumented. Thus height, story intervals, roof edge details, and rooftop equipment remain unresolved.
- **Exterior and materials:** The close R3 render shows red-brown running-bond brick, floor bands, gray/glazed volume, and a distinct mass corresponding generally to the qualitative 2019 Street View description. The facade still reads as a simplified massing model: repeated blank gray window/panel rectangles, little depth at the entrance, and limited visible material contrast. The orthophoto verifies roof geometry, not facade bay placement or facade materials. No new facade evidence or facade refinement in R3 closes the prior review's main visual concern.
- **Interior, program, and circulation:** The R2 sample dryer and grinder counts remain 15 and four, respectively, and R3 adds two below-grade plates plus three B-level and two SB-level cold-room proxies. Purdue's public research-facilities page confirms attached greenhouse context. The basement cutaway shows five isolated panel boxes on open slabs, without a demonstrated corridor, room partitions, stairs, or verified relationship to source plans. The cold-storage program has source support, but the room count, dimensions, floor assignments, and locations are schematic. The 2021 report's cited PDF was not retrievable in this review, so its equipment counts could not be independently checked from the primary PDF.
- **Technical portability and evidence:** Reopen validation passes with 613 export objects, 611 meshes, 19 unique materials, and no unpacked image dependencies. All six plates match the transformed GIS ring within 0.00001 m, and the evidence/validation materials count now agrees. Source limitations are unusually clear and no master/shared files were changed.

## Evidence checked

- Purdue University GIS, BuildingShapesZip4 layer 0, FID 917: [feature service](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0). The local snapshot records the polygon and vertical attribute values.
- Indiana Geographic Information Office: [Current Imagery ImageServer](https://di-ingov.img.arcgis.com/arcgis/rest/services/DynamicWebMercator/Indiana_Current_Imagery/ImageServer). Its service metadata covers current orthophotography, and the saved identify response selects a 2023 Tippecanoe County, 6-inch image item. The local overlay is useful for roof outline/orientation, not for validating floor height or facade.
- Purdue Department of Agronomy: [Research Facilities](https://ag.purdue.edu/department/agry/research/research-facilities.html) says the Life Science Ranges greenhouse facilities are attached to the Plant and Soils Building. This supports the connection/context, not the modeled greenhouse wing's exact geometry.
- [Google Maps / Street View](https://www.google.com/maps/place/Life+Science+Plant+and+Soils+Laboratory/@40.4231921,-86.9194291,163m/data=!3m2!1e3!4b1!4m6!3m5!1s0x8812e2b71ec32175:0x2dbc13bf851d0609!8m2!3d40.4231921!4d-86.9187854!16s%2Fg%2F11cnb8bwrl?entry=ttu) is dated August 2019 in the evidence record and used only for qualitative facade cues.

## Disposition

**Keep In progress.** R3 fixes the stale material count, adds a credible independent overhead footprint/orientation check, and makes useful programmatic additions. It does not reach 8/10 because the facade remains visibly generic, rooftop elements visibly extend beyond the roof in the preview, vertical levels conflict with GIS intervals, and the new basement layout is still a schematic collection of boxes. Correct the out-of-footprint roof elements, improve a source-matched facade/entrance view, and obtain or document stronger evidence for floor heights and basement circulation before reevaluation.
