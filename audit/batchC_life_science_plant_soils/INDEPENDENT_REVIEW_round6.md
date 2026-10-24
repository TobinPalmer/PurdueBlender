# Life Science Plant and Soils Laboratory — Independent Review R6

**Score: 8.0/10 — meets the 8/10 threshold narrowly.**

| Category | Score |
| --- | ---: |
| Identity and footprint | 1.8/2.0 |
| Placement, orientation, and scale | 1.5/2.0 |
| Height, floors, and roof evidence | 1.2/1.5 |
| Exterior and materials | 1.3/2.0 |
| Interior, program, and circulation | 1.3/1.5 |
| Technical portability and evidence | 0.9/1.0 |
| **Total** | **8.0/10** |

## Findings

- **Identity and footprint:** The local Purdue BuildingShapes feature snapshot identifies FID 917 as LSPS. The validated ground, upper, and two schematic basement plates each match its transformed 12-vertex horizontal GIS ring to 0.00001 m. This is strong plan-outline evidence, but does not independently verify the structural wall layout or basement footprint.
- **Placement and orientation:** The Indiana GIO 2023 orthophoto overlay supports the long-axis direction and visual correspondence between the selected roof outline and GIS footprint. The nearby Google Maps point is only a plausibility check. Neither is surveyed control, so absolute placement error is unquantified.
- **Height and roof:** The four unsupported curb boxes remain removed. Eight service proxies are positioned within the roof outline; their count, identities, and exact locations remain illustrative. The roughly 9-foot modeled story intervals conflict with 12-unit GIS level increments whose units and semantics are undocumented. No elevation source resolves this.
- **Exterior and materials:** The updated R5 lower-angle, brighter preview materially improves the legibility of the brick coursing, bands, glazing volume, and repeated facade modules compared with the dim, elevated view in R5 review. The saved asset includes a combined frame/transom mesh across 76 glazing objects. Most light-gray facade bays are named and materialed as precast panels, not glazing; their flat appearance is consistent with that assignment, though their exact appearance and bay pattern are not verified. The result is a readable, coherent study model rather than a close facade match. The 2019 Street View supports qualitative brick/glazing cues only, not dimensions or detailed frame divisions.
- **Interior and program:** Purdue Agronomy's *Background Information: Facilities & Equipment* supports 15 large sample dryers, four grinders with dust arresters, and a 1,163-square-foot climate-controlled walk-in seed room in the basement. The asset represents those counts and one room with the reported area. Room proportions, exact location, B-level placement, door, shelving, and circulation remain schematic because the source gives no plan or dimensions. The additional 790-square-foot installation is documented as uncertain and omitted.
- **Technical and evidence quality:** I inspected the R5 saved asset and current validation: 641 exported objects, 639 meshes, 19 materials with connected nodes, no unpacked image dependencies, all six plates matching the GIS ring, one seed room, and 76 glazing panels. The main evidence record now reports one cold room rather than the superseded count of five. The updated exterior preview is lower and brighter; geometry is unchanged since the R5 review.

## Evidence checked

- Purdue University, [BuildingShapesZip4 FeatureServer](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0), FID 917, and local snapshot `audit/batchC_life_science_plant_soils_official_footprint.json`.
- Indiana Geographic Information Office, [Current Imagery ImageServer](https://di-ingov.img.arcgis.com/arcgis/rest/services/DynamicWebMercator/Indiana_Current_Imagery/ImageServer), with local 2023 Tippecanoe County imagery and GIS overlay. This supports visual outline/orientation comparison, not survey control.
- Purdue Department of Agronomy, [Background Information: Facilities & Equipment, page 30](https://www.agry.purdue.edu/csrees/bg-facilities.pdf), for equipment quantities and basement seed-room area/program.
- Purdue Department of Agronomy, [Research Facilities](https://ag.purdue.edu/department/agry/research/research-facilities.html), for greenhouse context, not exact geometry.
- [Google Maps / Street View](https://www.google.com/maps/place/Life+Science+Plant+and+Soils+Laboratory/@40.4231921,-86.9194291,163m/data=!3m2!1e3!4b1!4m6!3m5!1s0x8812e2b71ec32175:0x2dbc13bf851d0609!8m2!3d40.4231921!4d-86.9187854!16s%2Fg%2F11cnb8bwrl?entry=ttu), dated August 2019, used qualitatively.
- Current files: `modular/buildings/life_science_plant_and_soils_laboratory.blend`, `audit/batchC_life_science_plant_soils/exterior_west_r5.png`, `roof_top_r5.png`, `basement_cutaway_r5.png`, and `validation_round5.json`.

## Disposition

**Meets 8/10 narrowly.** The lower, brighter facade view improves evaluation readability enough to pass, and the building's footprint, supported program, material families, and technical asset checks are documented. The asset should retain its explicit uncertainty labels. Further detailed facade, floor-height, roof-unit, or basement-layout claims need better source material before modeling them as verified.
