# National Soil Erosion Research Laboratory — R1

## Revision summary

The saved model now represents a taller west roof wing and a lower east wing. This is the first source-backed roof-height revision for the asset. I preserved the assigned asset identity, local origin, collection name, and official GIS footprint. The interior remains schematic and was not revised.

The Purdue FID 242 outline measures 64.868 × 51.121 m. I registered it to the Indiana 2023 orthophoto and sampled the 2018 DSM at 25 grid positions, comparing local 5 × 5-cell medians against same-coordinate bare-earth DTM identify elevations. The west section consistently measures about 23–24 ft above interpolated ground, while the east is about 17 ft. I set the high roof to 7.32 m and the low roof to 5.20 m, with an approximate local X break at −6.49 m. The two roof surfaces together match the complete GIS footprint plan area to the reported precision.

For the lower east wing, I removed the upper facade bays that would otherwise float above the revised roof. I trimmed the corresponding wall panels and split/shifted roof coping at the height break. Rooftop fan curbs on the lower side moved with that roof. I removed the modeled entrance sign panel and lettering because their previous position intersects the reduced roof volume; I could not verify the sign’s exact facade position from a readable official elevation.

## Evidence and sources

- [Purdue BuildingShapes feature service](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0), FID 242 “Soil Erosion Lab”; retained geometry snapshot: `audit/batchC_national_soil_erosion_official_footprint.json`.
- [Indiana Current Imagery ImageServer](https://di-ingov.img.arcgis.com/arcgis/rest/services/DynamicWebMercator/Indiana_Current_Imagery/ImageServer), 2023 Tippecanoe six-inch imagery item `in2023_29971882_06`; saved raw crop, registration record, and GIS overlay are in this audit folder. The aerial confirms the roof outline and multi-wing form, but does not establish height.
- [Indiana 2018 DSM tile](https://giselevationingov.s3.us-east-2.amazonaws.com/dsmoptimized/statewide/2018/SPW/5ft/in2018_29951880_12_dsm.tif), 5 ft cells, CC0. Local tile file and SHA-256 are recorded in `nsel_lidar_height_r1.json`.
- [Indiana Statewide 3DEP Lidar Dates, tile layer 4](https://gisdata.in.gov/server/rest/services/Indiana_Statewide_3DEP_Lidar_Dates/MapServer/4), Field4 gives the tile acquisition timestamp 2018-04-20 (epoch milliseconds 1524182400000).
- [Indiana 2016–2020 bare-earth DEM ImageServer](https://di-ingov.img.arcgis.com/arcgis/rest/services/DynamicWebMercator/Indiana_2016_2020_DEM/ImageServer), used for terrain identify values at the registered grid positions.
- [USDA ARS NSERL page](https://www.ars.usda.gov/midwest-area/west-lafayette-in/national-soil-erosion-research/docs/main/) confirms the lab’s Purdue campus identity and research use. It does not document the roof profile or facade dimensions.

## Validation

`nsel_revision_r1_validation.json` records a successful fresh Blender 5.2.3 reopen. The validation confirms the lower east wall reaches 5.20 m, the west wall remains 7.32 m, the high and low roof polygons meet at the break without overlap, roof plan area matches the official FID 242 footprint, and all 9 materials have no missing external texture dependencies.

Review renders:

- `nsel_revision_r1_exterior_threequarter.png`
- `nsel_revision_r1_roof_orthographic.png`
- `nsel_revision_r1_interior_cutaway.png`

## Limits and remaining uncertainty

- DSM minus DTM is a surface-height estimate, not a surveyed wall height. The DSM uses 5 ft cells; DTM samples beneath the building are interpolated ground values. Rooftop equipment, parapets, construction since 2018, and the approximate tangent-plane registration can affect the inferred split and elevations.
- The split at X = −6.49 m follows the transition in sampled height and the orthophoto roof pattern. It is not a verified structural joint location.
- Roof parapet geometry is simplified at the split. Exact roof equipment placement and facade window positions are not established by the overhead sources.
- The official USDA entrance image was identifiable on the USDA page, but its linked image was not available at sufficient resolution for reliable facade measurements. The entrance sign position and blank elevations remain unresolved.
- Interior rooms, corridors, and circulation are still schematic. The cutaway render is a visual check only, not a source-verified interior plan.
- No master blend, README, manifest, shared index, or other building asset was edited; no commit was made.
