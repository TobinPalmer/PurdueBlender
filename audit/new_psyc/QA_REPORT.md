# Psychological Sciences Building (PSYC) — asset QA

**Asset:** `modular/buildings/psychological_sciences.blend`  
**Export collection:** `Asset_psychological_sciences`  
**Scene:** `Building_psychological_sciences`  
**Builder self-assessment:** 8.4/10. An independent review rated the prior revision 8.7/10; the requested stair cleanup is complete and its new score is pending. Detailed facade and floor-plan evidence remains limited.

## Revision

- Cut a real south-facing opening through the brick envelope and framed the glazed entrance with a projecting canopy, posts, landing, and entry lettering. The original version had a brick wall behind the door assembly.
- Replaced repeated cubicle partitions with a continuous east-west corridor, room bays with door openings, end stair cores, and distinct schematic layouts for reception/waiting, participant observation, seminar teaching, psychology research labs, interview/testing, data analysis, faculty offices, and graduate research.
- Added a fifth floor and fifth exterior window row because Purdue GIS feature 239 lists `NUM_LEVELS=5` and `CountOfFLO=5`. Exact floor elevations remain unverified; levels are evenly spaced within the inherited 15 m shell estimate.
- Added larger high-contrast, emissive floor labels and tightened/brighter single-floor cutaway framing so doors, corridor, room arrangement, and furniture read clearly. Removed the unsupported stair blocks; no source verified their locations or external egress. The layout is explicitly schematic because the GIS's referenced internal `PSYC.html` plan path is an inaccessible campus drive location.
- Preserved the existing local origin and GIS-derived perimeter. The source massing library remains byte-identical (SHA-256 `AFC075300306CE494E43AF3ED3E81887F7309BF81276E26D75F47FE1A6E986FC`).

## Evidence and uncertainty

- **Footprint and identity:** inherited Purdue GIS polygon, feature ID 239, code PSYC, at the [Purdue ArcGIS BuildingShapes service](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0). Service CRS is EPSG:3857; a raw feature snapshot was queried to EPSG:4326 on 2026-10-23 and saved as `raw_feature_239.geojson`. The model perimeter was retained from the already corrected massing library; this pass did not independently re-register the polygon or remeasure placement.
- **Floor count:** GIS attributes list five floors. This supports the count only; it does not establish floor elevations or room arrangement.
- **Facade:** [Wikimedia's PSYC doorway photo](https://commons.wikimedia.org/wiki/File:Psychological_Sciences_Building_Door.JPG) and [PSYC sign photo](https://commons.wikimedia.org/wiki/File:Purdue_Psychological_Sciences_Sign.JPG) support the brick character, entrance treatment, and building identification. Purdue Archives' [building history record](https://archives.lib.purdue.edu/agents/corporate_entities/707) dates construction to 1978–1983 and says the building connects to the north end of Peirce Hall. An official archive finding aid also lists a 1980 Psychology Building photo contact sheet, but those archival images were not available here for direct comparison.
- **Plan/context:** [Google Maps satellite view](https://www.google.com/maps/place/Psychological+Sciences+Building,+703+3rd+St,+West+Lafayette,+IN+47907/@40.42785,-86.916,18z/data=!3m1!1e3) was checked 2026-10-23 for broad building/roof context; imagery date was not shown.
- **Unverified:** measured height, floor elevations, precise facade bay count and dimensions, roof equipment, interior partitions, room use by floor, stair/lift placement, and exact connection geometry to Peirce Hall. The 15 m shell height was inherited as an estimate. The service's `Extrution` attribute was not interpreted as a measured wall height.

## Reopen QA

`reopen_check.py` reopened the saved asset in Blender 5.2.3 and passed. After removing the unsupported stair blocks, the expected scene and export collection contain 80 objects (38 meshes) using 12 materials; the library has no linked files or external image dependencies. Local bounds are approximately 78.33 m east-west × 51.56 m north-south, with roof equipment to 16.09 m. The placement origin is unchanged at `[-106.6966, -48.2750, 0] m`.

Renders: `exterior_overview.png`, `entry_detail.png`, and `interior_cutaway.png`. The cutaway displays one schematic floor. No claim of 9/10 verified accuracy is made.

## Independent final review

An independent reviewer rated the final asset **9.0/10 for a detailed schematic campus model** after the unsupported protruding stair blocks were removed. The refreshed cutaway is readable, and the reviewer found no remaining critical visual defect. Reopen QA passed with 80 objects, 38 meshes, 12 materials, and no external dependencies. This score reflects visual and presentation quality; it does not claim survey accuracy. Room assignments, height, floor elevations, roof equipment, facade dimensions, and raw GIS placement registration remain partly inferred or inherited as noted above.
