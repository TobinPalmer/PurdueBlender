# Independent Winifred Parker Hall R5 grade

**Score: 8.05/10 — passes the 8.0 threshold**
**Asset SHA-256:** 92fa120794470d93a253d04f35ca0852caea7d05982a5f4e02b285fd914045a9
**Review date (UTC):** 2026-10-26T03:36:24.765553+00:00
**Scope:** exact canonical asset, independent footprint calculation, official image sources, and read-only master placement.

## Scorecard

| Criterion | Score | Evidence and limitations |
| --- | ---: | --- |
| Identity and source-backed footprint | 1.80/2.00 | Purdue BuildingShapesZip4 FID 879 is PKRW / Winifred Parker Residence Hall at 1196 3rd Street. Independent raw-ring to actual mesh top-face comparison: IoU 0.999999901, boundary Hausdorff 0.000002 m, GIS/model areas 1842.575/1842.575 m2. The 2023 orthophoto overlay shows the source polygon and model perimeter tracking the visible roof. **Limits:** The candidate's upper shell is traced to this GIS ring, so the near-1 IoU establishes faithful transfer of that outline, not surveyed wall-face accuracy. The GIS Shape__Area field (3185.1171875 m2) conflicts with the area of its returned ring (1842.575 m2). |
| Campus placement, orientation, and scale | 1.45/1.50 | Fresh read-only master reopen confirms the expected linked collection and marker; position error 0.000000 m, zero rotation, unit scale, and no duplicate direct source link. The source polygon is 51.49 by 79.23 m; the canonical upper shell matches. **Limits:** Placement is exact relative to the manifest; the campus XY transform is approximate, not survey control. |
| Massing, floors, height, and roof | 1.20/1.50 | The model has a recognizable flat-roof mid-rise plan with a preserved internal notch/courtyard. The main shell spans z=4.2 to 20.2 m and the asset maximum is 23.40 m including rooftop masses. The 2023 aerial shows the flat roof and equipment. GIS floor-height fields F02-F05 and R support a similar mid-rise profile if their values are feet. **Limits:** GIS NUM_LEVELS=3 conflicts with CountOfFLO=6; field units are undocumented. If R=74.1 is feet, the modeled maximum is about 0.8 m taller. Rooftop services and exact floor-to-floor heights remain schematic. |
| Facade, windows, and entrances | 1.20/1.50 | The official 2021 Purdue photo supports red brick, tall narrow punched windows, restrained light trim, and glazed ground-floor retail. The asset has 158 window and 158 sill objects over five modeled bands; East facade openings are aligned to the outline, and unsupported West/North bays were removed while preserving exterior continuity. **Limits:** Only one oblique image is available. Exact window spacing and opening size lack elevations; the large bright portal/canopy visible in the diagnostic render is not measured from a plan. |
| Materials and surface finish | 0.65/1.00 | 18 used materials cover brick, limestone, roof membrane, glazing, concrete, paving, and interior finishes. Procedural brick/noise/bump shaders are present; all mesh material slots are valid. **Limits:** No image-texture nodes or photographic maps are packed in the asset. The available diagnostic render makes the roof read washed white/cyan and the repeated brick remains stylized; final daylight material response was not polished. |
| Interior and building program | 0.55/1.00 | Purdue Housing documents suites/semi-suites, shared baths, suite living rooms, a Starbucks/market at ground level, an Executive-in-Residence lobby, and TV lounges on each floor. The asset includes ground retail, lobby/reception, and a furnished sample suite with beds, desks, bath, sofa, and TV console. **Limits:** There is no complete representative resident floor or repeated TV lounge/corridor layout. The public room diagrams are expressly approximate, so room partitions and furniture positions remain illustrative. |
| Technical integrity, portability, and evidence | 1.20/1.50 | Exact SHA 92fa120794470d93a253d04f35ca0852caea7d05982a5f4e02b285fd914045a9 freshly reopened in Blender 5.2.3 LTS: 582 objects / 581 meshes, identity root, 18 used materials, no materialless meshes, invalid indices, missing images, unpacked external image dependencies, or linked libraries. The grade evidence includes raw GIS, Purdue Housing text, official 2021 exterior photo, a catalog-identified 2023 Tippecanoe six-inch orthophoto, and a separate read-only master check. **Limits:** The GIS area conflict and local coordinate approximation remain unresolved. |

## Findings

- The R5 shell correction resolves the main east-wing position/shape problem from baseline; the actual mesh outline matches Purdue GIS FID 879 and the 2023 Tippecanoe roof image.
- The fresh master marker is at the manifest origin with zero translation error, zero rotation, unit scale, and only one collection instance.
- This narrow pass is not an as-built claim: floor-count/height semantics, measured wall lines, full residential circulation, exact openings, and final rendered materials remain uncertain or schematic.
- Priority follow-up is a neutral daylight exterior render with roof services checked, plus a labeled representative resident-floor/corridor cutaway and source-backed reconciliation of the GIS area/floor fields.

## Measured results

- Purdue GIS FID 879 / PKRW: Winifred Parker Residence Hall, 1196 3rd Street.
- Upper-shell/GIS-ring IoU 0.999999901; boundary Hausdorff distance 0.000002 m.
- Master marker error 0.000000 m; zero rotation; unit scale.
- 2023 orthophoto catalog item in2023_29971885_06, Tippecanoe County, 06 in..
- Fresh export: 582 objects / 581 meshes, 18 materials, no missing external dependencies.

## Sources

- Purdue GIS BuildingShapesZip4, FID 879 / PKRW: https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0
- Purdue Housing Parker South: https://housing.purdue.edu/my-housing/options/residence-halls/parker-south.html
- Official Purdue exterior photograph, Fall 2021: https://www.purdue.edu/vpsl/news/perspectives-stories/fall-2021/_images/winifred-parker-hall.jpg
- Indiana Geographic Information Office 2023 orthophoto ImageServer: https://di-ingov.img.arcgis.com/arcgis/rest/services/DynamicWebMercator/Indiana_2023_Imagery/ImageServer

The map outline is not a surveyed wall line. GIS floor-count fields conflict; height, full resident circulation, measured facade dimensions, and roof/service details remain estimated or schematic.
