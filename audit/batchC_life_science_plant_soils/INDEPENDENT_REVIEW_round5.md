# Life Science Plant and Soils Laboratory — Independent Review R5

**Score: 7.9/10 — below the 8/10 finish threshold.**

| Category | Score |
| --- | ---: |
| Identity and footprint | 1.8/2.0 |
| Placement, orientation, and scale | 1.5/2.0 |
| Height, floors, and roof evidence | 1.2/1.5 |
| Exterior and materials | 1.2/2.0 |
| Interior, program, and circulation | 1.3/1.5 |
| Technical portability and evidence | 0.9/1.0 |
| **Total** | **7.9/10** |

## Findings

- **Identity and footprint:** The evidence identifies Purdue BuildingShapes feature FID 917. The R5 validation reports six 12-vertex floor plates matching the transformed GIS outline within 0.00001 m, a strong plan-footprint check. It does not establish the below-grade outline or wall layout independently.
- **Placement and orientation:** The saved Indiana 2023 orthophoto overlay supports the outline and long-axis orientation visually. The Google Maps point is a nearby POI check. Neither source provides surveyed control, so georeferencing error remains unquantified.
- **Vertical form and roof:** The four unsupported curbs found outside the roof outline in R3 remain removed. The eight small roof service proxies are contained on the roof and look plausible from the overhead preview, but their identities, count, and locations are not verified. The model’s roughly 9-foot story spacing still conflicts with the GIS fields’ 12-unit increments; the GIS units and field meanings are not documented.
- **Exterior and materials:** The model has red-brown brick, horizontal light-colored bands, dark glazing, and a narrow glazed volume. R5 adds one combined mesh of dark frame/transom pieces over the 76 glazing objects. The addition is present in the saved asset, but the exterior preview shows little visible improvement across most of the large gray window rectangles; only a few dark framed panes are clearly legible. The façade remains a simplified study model with shallow flat openings, minimal recess/shadow, and no verified entrance or bay spacing. The available Street View is qualitative and perspective-distorted, so further exact façade claims are not supportable from the current evidence.
- **Interior and program:** Purdue’s *Background Information: Facilities & Equipment* supports 15 large sample dryers, four grinding units with dust arresters, and one 1,163-square-foot basement walk-in climate-controlled seed room. The R5 asset contains the single room and no stale R3 cold-room boxes; the evidence count now agrees. Its square proportions, exact location, door, storage layout, and B-level assignment remain schematic because the report supplies no floor plan or dimensions. The further 790-square-foot storage installation is appropriately treated as uncertain and omitted.
- **Technical and evidence quality:** I reopened and inspected the saved asset. R5 validation reports 641 export objects, 639 meshes, 19 connected materials, no unpacked external image files, six GIS-matched plates, one frame-detail mesh, and 76 glazed façade objects. The count of one cold room is consistent with the asset and evidence. The validation’s `overall: PASS` verifies these checks; it does not mean the unresolved visual/source limitations have been resolved. The exterior preview is an elevated, dim view and does not clearly communicate the new frame detail.

## Evidence checked

- Purdue University, [BuildingShapesZip4 feature service](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0), FID 917, and local snapshot `audit/batchC_life_science_plant_soils_official_footprint.json`.
- Indiana Geographic Information Office, [Current Imagery ImageServer](https://di-ingov.img.arcgis.com/arcgis/rest/services/DynamicWebMercator/Indiana_Current_Imagery/ImageServer), with the local 2023 Tippecanoe County imagery and GIS overlay. The overlay supports a visual match, not survey control.
- Purdue Department of Agronomy, [Background Information: Facilities & Equipment, page 30](https://www.agry.purdue.edu/csrees/bg-facilities.pdf), for dryer/grinder quantities and the basement seed-storage room area/program.
- Purdue Department of Agronomy, [Research Facilities](https://ag.purdue.edu/department/agry/research/research-facilities.html), for greenhouse context; it does not establish the modeled greenhouse geometry.
- [Google Maps / Street View](https://www.google.com/maps/place/Life+Science+Plant+and+Soils+Laboratory/@40.4231921,-86.9194291,163m/data=!3m2!1e3!4b1!4m6!3m5!1s0x8812e2b71ec32175:0x2dbc13bf851d0609!8m2!3d40.4231921!4d-86.9187854!16s%2Fg%2F11cnb8bwrl?entry=ttu), recorded as August 2019, used only for qualitative brick/glazing cues.
- R5 asset and previews: `modular/buildings/life_science_plant_and_soils_laboratory.blend`, `audit/batchC_life_science_plant_soils/exterior_west_r5.png`, `roof_top_r5.png`, and `basement_cutaway_r5.png`.

## Disposition

**Keep In progress.** R5 fixes the inconsistent cold-room audit count and adds glazing frame geometry, but the facade still reads mostly as flat gray rectangles in the supplied exterior preview. The roof equipment remains illustrative, vertical intervals are unresolved, and basement placement/circulation is unsupported. A lower, brighter facade view and stronger source-backed facade detail would be the most useful next work; do not infer measured window spacing or room layout from the current references.
