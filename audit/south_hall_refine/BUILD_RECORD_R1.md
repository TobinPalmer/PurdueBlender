# South Hall build record — R1

**Asset:** `modular/buildings/south_hall.blend`  
**Building ID / collection / local root:** `south_hall` / `Asset_south_hall` / `AssetRoot_south_hall`  
**Build/review date:** 2026-10-25  
**Final asset SHA-256:** `9a848c6140c3abc6c6a1d7c7daa9d8c176d7a0452c3c489d56672812c573c410`

## Sources and source dates

| Evidence | Provider / identifier | Date and use |
|---|---|---|
| [Purdue BuildingShapesZip4 ArcGIS feature query](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D528&outFields=*&returnGeometry=true&outSR=4326&f=geojson) | Purdue-linked campus GIS; `FID=528`, `BLDG_ABBR=SH`, GlobalID `{FBB17D8A-34ED-4E5F-BA58-43089D065963}`; `201 N Macarthur Dr` | Retrieved 2026-10-25. Geometry query returns EPSG:4326; underlying layer reports EPSG:3857 (WKID 102100). Original response is preserved in `raw_south_hall_fid528.geojson`. Feature date fields are blank. |
| [Purdue Board of Trustees, Hillenbrand Residence Hall South, Exhibit A](https://www.purdue.edu/bot/meetings/past-meetings/2023/07.%20aug/pfc/Hillenbrand%20Residence%20Hall%20South.pdf) | Purdue Administrative Operations; site plan dated 2023-07-24; source PDF metadata created 2023-07-31 | Used to distinguish the blue residential portion from the tan dining/link arm and to check the connector direction. Saved as `purdue_board_hillenbrand_south_siteplan_2023.pdf`; page image: `board_siteplan-6.png`. This sheet is not georeferenced. |
| [Purdue Residences — South Hall](https://housing.purdue.edu/my-housing/options/residence-halls/south-hall.html) | Purdue University Residences | Retrieved 2026-10-25. Confirms the new South Hall, its address, eight-story program, amenities, and connection to Hillenbrand. Used for program/context, not dimensional measurement. |
| [Purdue construction update, January 2025](https://housing.purdue.edu/news/2025_0115-construction-ambassadors-south-hill.html) | Purdue University Residences | Source describes eight floors and 252,525 sq ft and includes construction progress views. Narrative floor area is not treated as a footprint measurement. |
| [Purdue 2026 South Hall feature](https://www.housing.purdue.edu/get-reconnected/2026/03/special-feature3.html) | Purdue University Residences | Retrieved 2026-10-25. Exterior/interior reference images and current program context. Captured exterior/interior images are `purdue_southhall_exterior_construction_2026.jpg` and `purdue_southhall_mainfloor_2026.jpg`. |

## Footprint, position, and orientation

The source polygon has 83 vertices. It was converted to project-local metres using the required approximate local geographic conversion at origin `(40.4274° N, 86.9137° W)` and the unchanged placement offset `[-1091.6500244, -131.2249985]` m. The approximation is not a surveyed CRS. The projected polygon was simplified with Shapely topology-preserving tolerance 0.50 m to 53 vertices. Area changed from 3,436.52 m² to 3,434.516 m² (0.0583%); maximum source-to-simplified displacement is 0.383 m. The polygon bounds are X `[-73.376, 48.249]` m and Y `[-53.777, 23.462]` m.

The complete simplified FID 528 outline is used for the ground-floor glazed base. The reopened asset base mesh has the same 3,434.516 m² plan area and a maximum nearest-vertex difference below 0.00001 m from the simplified source outline. This is a build-transform check against the same GIS polygon, not an independent survey or proof that the GIS edge is the structural-wall line. No asset-root translation/rotation or master placement marker was changed. X is east, Y is north, and Z is up.

The registered top-down comparison is `official_footprint_vs_asset_r1.png`; the numerical check is `validation_r1.json`.

## Massing and measured/estimated heights

The 2023 plan differentiates the residential area (blue) from the tan dining/link arm. The sheet cannot be registered geographically, so the approximate split uses a local Y=5 m clip through the narrow north arm. This yields a 3,180.967 m² main residential polygon and a 253.549 m² north dining/link polygon, together matching the complete GIS footprint. The split line and endpoint are estimated (about 3 m); see `gis_partition_r1.json`.

The high residential shell is modeled on the main polygon with eight above-grade levels. GIS floor attributes `F01=621.85`, `F02=635.85`, `F03=645.85`, `F04=655.85`, `F05=665.85`, `F06=675.85`, `F07=685.85`, `F08=695.85`, and `R=705.85` yield a 14-unit first interval followed by 10-unit intervals and a 10-unit roof interval. Interpreting those relative values as feet gives a floor-to-roof difference of 84 ft (25.603 m), matching the modeled eight-floor stack: a 14 ft first interval followed by seven 10 ft intervals. The GIS does not state units or a verified vertical datum, so 25.603 m is a derived estimate, not a surveyed absolute height.

The north dining/link arm is kept to the one-storey glazed podium height (4.267 m), with its roof material visible at the top. It is not extruded to residential height. Purdue confirms a connection to Hillenbrand, and the site plan supports a northward dining/link zone; the precise off-site corridor route/endpoint is not independently georeferenced and is not extended beyond the GIS footprint in R1.

## Exterior and interior changes

- Replaced the previous unsupported 104 × 48 m rectangular slab with the complete FID 528 polygon and separated residential upper massing from the estimated low north dining/link zone.
- Added eight-level red-brown procedural brick shell, repeated dark-framed residential windows, a glazed ground-floor podium, a one-storey framed north link, a MacArthur-side entry vestibule with distinct double-leaf doors/pulls, and a supported restrained canopy. Entry position and exact vestibule/canopy dimensions are interpretive because no elevation was found.
- Darkened the roof and added subtle procedural membrane variation and low-profile 6 m seams. Public roof imagery/detail drawings were unavailable; roof finish and seam rhythm remain low-confidence visual treatment.
- Added schematic interior floor plates, nine representative Data Mine lab modules, main-floor lounge/food/game-room props, and one representative double room. Purdue supports the amenity program and publishes double-room dimensions of 11 ft 6 in × 16 ft 11 in; no room-by-room plan was found. The furniture arrangement, locations, partitions, and other room layouts are explicitly schematic and are not claimed to be measured.
- All materials are embedded/procedural; the asset has no external image dependencies.

## Validation and review views

Fresh Blender 5.2.3 reopen validation passed: 22 asset objects (21 meshes), 8 exterior objects, 13 interior objects, identity root transform, no materialless meshes, and no unpacked external images. Validation JSON SHA-256 matches the saved blend file exactly: `9a848c6140c3abc6c6a1d7c7daa9d8c176d7a0452c3c489d56672812c573c410`.

- `south_hall_human_scale_east_entry_r1.png` — human-scale entry/facade view.
- `south_hall_oblique_full_r1.png` — overall footprint and massing view.
- `south_hall_schematic_ground_floor_cutaway_r1.png` — schematic amenity modules; it is not an architectural floor plan.

## Remaining uncertainties

1. The GIS outline is authoritative campus-map evidence but not a certified survey or necessarily the structural-wall boundary.
2. The plan-to-GIS connector split is estimated and should be replaced with a georeferenced architectural/site plan if obtained; the confirmed connection route and exact endpoint remain unverified.
3. Absolute height units/datum, roof assembly, elevations, detailed facade/window schedule, entry dimensions, and floor-by-floor interior plans remain unverified.
4. The construction photo may show temporary construction conditions; only stable material and massing cues were used.
