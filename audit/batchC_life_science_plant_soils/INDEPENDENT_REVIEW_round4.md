# Life Science Plant and Soils Laboratory — Independent Review R4

**Score: 7.9/10 — below the 8/10 finish threshold.**

| Category | Score |
| --- | ---: |
| Identity and footprint | 1.8/2.0 |
| Placement, orientation, and scale | 1.5/2.0 |
| Height, floors, and roof evidence | 1.2/1.5 |
| Exterior and materials | 1.15/2.0 |
| Interior, program, and circulation | 1.3/1.5 |
| Technical portability and evidence | 0.95/1.0 |
| **Total** | **7.9/10** |

## Findings

- **Identity and footprint:** Purdue BuildingShapes feature FID 917 is identified as the building. R4 validation reports six 12-vertex plates matching the transformed GIS ring within 0.00001 m. The GIS polygon is a strong horizontal footprint source; that exact match does not independently establish basement extent or structural wall lines.
- **Placement, orientation, and scale:** The saved GIS/Indiana orthophoto overlay shows close agreement between the footprint and visible roof outline, including the long-axis orientation. The Google Maps place point is a plausible vicinity check. Neither is surveyed control, so geographic registration and campus placement error are not quantified.
- **Height, floors, and roof evidence:** The R4 roof preview no longer shows the four unsupported curb boxes that extended beyond the roof in R3. The eight small remaining service proxies sit on the roof, but their exact type, count, and position are not established by the orthophoto. R4 correctly preserves the mismatch between roughly 9-foot modeled floor intervals and 12-unit GIS F01–F04 intervals; the GIS vertical units and semantics are undocumented. Roof parapet/equipment details and floor elevations remain uncertain.
- **Exterior and materials:** R4 darkens the glazing, and the exterior preview retains recognizable red-brown brick bands, a glazed/panel volume, and a narrow glazed bay. The Purdue report supports attached greenhouse context, while the 2019 Street View offers only qualitative facade cues. The facade still reads as a simplified study model: repeated flat gray window/panel rectangles have little visible depth or reflection, and the entrance and facade bay spacing are not verified. The preview is useful for massing, but does not yet establish close facade matching.
- **Interior, program, and circulation:** The primary Purdue Agronomy report explicitly states that LSPS has fifteen large sample dryers, four grinding units with dust arresters, and a 1,163-square-foot walk-in climate-controlled long-term seed-storage room in the basement, completed in 2004. R4’s one room with reported area 108.05 m² is therefore program- and area-supported. Its square plan, location, B-level assignment, door, racks, and refrigeration details are schematic; the report supplies no dimensions, plan, sublevel, or circulation. The preview shows a plausible storage-room interior, but not verified room adjacency or basement circulation. The report also notes a further 790-square-foot installation began in 2008; its current status/location are unknown and omission is reasonable.
- **Technical portability and evidence:** The saved/reopened validation reports 640 export objects, 19 unique materials with connected nodes, no external image dependencies, and only the asset collection in the export; all six floor plates pass the GIS-ring comparison. The material count agrees between R4 validation and evidence at 19. However, the evidence JSON still contains `cold_room_proxy_count: 5` alongside the R4 count of one walk-in seed room. This appears to be a stale R3 field and should be reconciled; the contradictory field slightly reduces confidence in the audit record. The validation pass does not resolve the visual/source limitations above.

## Evidence checked

- Purdue Department of Agronomy, [Background Information: Facilities & Equipment, page 30](https://www.agry.purdue.edu/csrees/bg-facilities.pdf), directly supports the dryer/grinder quantities and the 1,163-square-foot basement seed-storage room. It does not supply a room plan or dimensions.
- Purdue BuildingShapesZip4 feature FID 917, local source snapshot `audit/batchC_life_science_plant_soils_official_footprint.json`, supplies the selected polygon and vertical attributes. The snapshot lists `Elevation=621.4`, `Extrution=36`, `B=-12`, `SB=-24`, and F01–F04 values at 0, 12, 24, and 36; the meanings/units are not documented in the snapshot.
- Indiana Geographic Information Office, [Current Imagery ImageServer](https://di-ingov.img.arcgis.com/arcgis/rest/services/DynamicWebMercator/Indiana_Current_Imagery/ImageServer), describes current orthophotography at nominal 6-inch resolution. The local identify response selects 2023 Tippecanoe County imagery; the saved overlay supports a visual roof-outline/orientation comparison, not survey control.
- Purdue Department of Agronomy, [Research Facilities](https://ag.purdue.edu/department/agry/research/research-facilities.html), supports the greenhouse connection/context, not exact geometry.
- [Google Maps / Street View](https://www.google.com/maps/place/Life+Science+Plant+and+Soils+Laboratory/@40.4231921,-86.9194291,163m/data=!3m2!1e3!4b1!4m6!3m5!1s0x8812e2b71ec32175:0x2dbc13bf851d0609!8m2!3d40.4231921!4d-86.9187854!16s%2Fg%2F11cnb8bwrl?entry=ttu) is recorded as August 2019 and used qualitatively for visible brick and glazing cues.

## Disposition

**Keep In progress.** R4 corrects the out-of-footprint roof curbs and replaces unsupported room boxes with one room whose area and basement program have direct Purdue support. The building remains below 8/10 because facade matching is still schematic, roof-unit layout is not identified, the GIS/model vertical interval discrepancy remains unresolved, and the basement location/circulation is not evidenced. Reconcile the stale five-room evidence field, then improve the facade from additional calibrated views or plans and seek floor/roof or basement evidence before reevaluation.

