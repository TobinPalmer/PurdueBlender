# Psychological Sciences Building — exterior research

**Queue rank:** 24 · **stable ID:** `psychological_sciences` · **model owner:** Unassigned
**Asset:** `modular/buildings/psychological_sciences.blend`
**Pass status:** Focused exterior research saved with substantial face, opening, connection, roof, and height gaps; no modeling or model-readiness claim.

## Identity, levels, and Peirce Hall connection

Purdue identifies this as Psychological Sciences (PSYC), 703 3rd Street. The Purdue Archives subject record says the building was constructed from 1978 to 1983 and connected to the north end of Peirce Hall. A Purdue timeline places completion in 1980. The records overlap on the construction period but differ on the completion milestone; the specific opening/occupancy date remains unconfirmed.

The current Purdue Office of Emergency Preparedness plan (revision 2026-04-06) calls PSYC **four stories plus a basement**. It says the first floor has two wings, floors two and three are one wing, and the fourth floor is a locked animal-research facility. There are two stairwells, one east and one central; the eastern one has a fire chimney at its top. Fire doors connect to Peirce Hall on floors two and three. This is the strongest current level/connection description found in this pass.

Cached and newly queried Purdue GIS FID 239 both list `NUM_LEVELS=5` and `CountOfFLO=5`. Those counts are consistent with the OEP description if the basement is counted as a level. The existing detailed asset instead contains five modeled above-grade levels; that extra above-grade floor is not supported by the current OEP plan and should be resolved before a later modeling revision. The GIS floorplan attribute points to an inaccessible campus `G:\GIS\web_pages\html_pages\PSYC.html` file. No publicly viewable as-built floor/elevation plan was found.

## Current footprint and dimensional conflicts

The live Purdue GIS query retrieved 2026-10-30 returns FID 239, `BLDG_ABBR=PSYC`, occupied primary layer, and the address above. Its closed WGS84 polygon has 37 entries including the closing coordinate. Under the project’s documented local campus transform it spans approximately **77.72 m east–west by 48.69 m north–south**, with a ring area of **2,161.16 m²** and perimeter **265.13 m**. These are computations from the cached/live coordinate ring, not surveyed wall dimensions.

The same record reports `Shape__Area=3,735.78` and `Shape__Length=348.44`, labelled esri metres in the service metadata. Those stored summary fields differ materially from measurements of the coordinate ring under the project transform (about 73% larger area and 31% longer perimeter); the summary measurement basis is unresolved. Retain both raw and calculated values. The complete live feature is retained at `sources/live_feature_239_2026-10-30.geojson`; the earlier asset-audit copy is `audit/new_psyc/raw_feature_239.geojson`.

The source-massing bounds in `modular/manifest.json` match the transformed GIS polygon bounds. The active detailed asset’s manifest bounds extend about **2.6 m south** and about **0.3 m beyond the ring at the other three outer bounds**. Those differences may include modeled projections, but the audit did not register the detailed walls to the footprint or establish which projections exist on the real building. Preserve this as a discrepancy; the source model is not exterior evidence.

The GIS row has `Extrution=26` and level-elevation fields including `F02=9.3`, `F03=26.2`, and `R=36.7`, while `F01`, `F04`, and `F05` are zero. The snapshot does not establish units, vertical datum, or the meaning of incomplete fields. The previous asset used an inherited 15 m shell estimate and reaches 16.09 m with roof equipment. Neither height is independently surveyed. Do not infer floor-to-floor or roof elevations from these values without resolving the field semantics.

## Inspected exterior evidence

The following source IDs are stable in [`sources/second_pass_source_register.json`](sources/second_pass_source_register.json). Original photos are retained at full supplied resolution with EXIF and SHA-256 records.

| View ID / source | Observations supported | Limits |
| --- | --- | --- |
| **PSYC-V1** — Mickrine, Wikimedia Commons, “Psychological Sciences Building Door,” captured 2014-04-01 16:25:52 (iPhone 4S) | Close exterior glazing with large white applied building lettering; dark/reddish brick appears beside it. | Tight reflection-heavy image; it does not clearly resolve the leaf/frame, recess depth, threshold, canopy, or wall-to-door joint. Camera position/bearing and GPS are absent. The “Door” filename alone is not evidence of the complete entrance assembly. |
| **PSYC-V2** — Mickrine, Wikimedia Commons, “Purdue Psychological Sciences Sign,” captured 2014-04-01 16:31:42 (iPhone 4S) | Building name is confirmed. An oblique corner view shows red/brown brick, pale projecting vertical frame/piers and horizontal bands, and repeated rectangular multi-light window groups across visible upper and lower wall zones. The building has multiple adjoining wall runs rather than one uninterrupted flat front. | Freestanding sign blocks part of the facade; trees and perspective hide lower/window runs. Photo bearing is unregistered and no GPS is present; do not label these as north/east/south/west. Counts, frame depth, material identity and dimensions cannot be read reliably. EXIF orientation rotates the original portrait file for display. |
| **PSYC-ORT-1** — Esri World Imagery, north-up extract, `sources/current_world_imagery.jpg` | Confirms the stepped/winged plan, several low-slope-looking roof areas, a raised central roof zone and visible rooftop equipment. It helps distinguish the PSYC ring from adjoining campus roofs and contextualizes the Peirce Hall interface. | Service imagery capture date is not exposed. Aerial resolution, trees and shadows prevent current facade counts, exact roof equipment identification, roof-edge profile, heights or connector ownership. It is not a vertical survey. Extent and attribution are retained in the source register. |
| **PSYC-GIS-1** — live Purdue campus GIS FID 239, retrieved 2026-10-30 | Current official name/code, address, occupied-primary classification, polygon and five-level count. | Stored area/perimeter disagree with direct ring calculations; level units/vertical datum and the undocumented `PSYC.html` plan remain unresolved. |
| **PSYC-ARCH-1** — Purdue Archives and Special Collections records | The corporate history record supports 1978–1983 construction and north-end connection to Peirce. UA 62 photo finding aid lists a Psychology Building contact sheet (Box 90, folder 10, Aug 1980), another “view from new Psych building” set (folder 15, Mar 1981), and a Psychology Building set (folder 27, Sep 1982). A Purdue News Service photo index separately lists “New psychology Building” (MSP 19.004.084, June 1981, one photo). | These 1980–1982 contact sheets/negative records were not available as image files in this pass; they remain high-value archive retrieval leads, not inspected photos. The series PDF was search-indexed but returned 403 on direct open. |

### Partial facade schedule and construction brief

- **Facade family visible in PSYC-V2, compass side unknown:** red/brown brick wall fields separated by pale projecting vertical piers/frames, with pale horizontal bands/sills and repeated rectangular multi-light window groups. The photograph establishes the vocabulary and layered relief, but the visible crop cannot support a full bay sequence or count. Do not apply a single count to all faces.
- **Window treatment:** visible openings are rectangular, vertically proportioned and divided into multiple lights; their exact sash/mullion pattern, reveal depth, floor-specific alignment and infilled/service exceptions are unresolved. The upper and lower runs are partly visible, but the image does not identify the story level because the full building is not shown in a registered elevation.
- **Entrance:** PSYC-V1 records lettering on exterior glazing, not a measured entrance. The prior audit’s recessed entrance/canopy wording is model-side interpretation until a view shows the whole opening and its relationship to steps, landings and facade bays.
- **Massing/connection:** GIS and PSYC-ORT-1 show a stepped, multi-wing footprint. The OEP page independently distinguishes two first-floor wings from one upper wing on floors two and three, and identifies two connection doors into Peirce on those levels. Determine the real connecting wall/bridge form, floor 4 interface, and ownership of shared walls before extending facade runs between assets.
- **Roof and stair heads:** overhead imagery shows several roof zones and equipment, but no measured roof plan or equipment schedule. OEP’s east stairwell/fire-chimney note is a source-backed feature to locate; the chimney’s shape, height, materials and visibility are not documented by the inspected images. East and central exterior stair doors/terminations are also unverified.
- **Materials:** brick and pale projecting trim are visible in PSYC-V2; “concrete” or stone identity and exact color remain unverified. The spring photo has hard daylight and bare-branch shadows; the doorway image is highly reflective. No calibrated color target or current finish specification was found.

## Gaps and conflicts to preserve

1. **All face/floor runs:** north, east, south and west are not registered to the 2014 photos; complete opening schedules, corner returns, louvers, basement openings and upper-floor exceptions remain unknown. Obtain a current orientation-registered walkaround with close, medium and distant views, including long-facade starts/ends.
2. **Peirce interface:** official records establish connection but not the bridge/door exterior geometry, floor-by-floor width, roof/facade ownership, or whether other connector segments exist. Obtain current corner/connector views and dimensioned records for both assets.
3. **Current vs historic condition:** all direct facade photos inspected date from 2014. Retrieve UA 62 box 90 folders 10, 15 and 27 and MSP 19.004.084, then compare to current views for construction completion and later changes.
4. **Roof/stairs:** no current roof plan or elevated oblique was inspected. Identify roof zones, eaves/parapets, raised mechanical screening, equipment, drainage, east stair fire chimney and central stair head. Determine heights from a surveyed elevation/point cloud with CRS, vertical datum and point-selection method.
5. **Level/height:** use the OEP’s four stories plus basement as current floor-count evidence. Reconcile it with GIS `NUM_LEVELS=5`, partial level fields and the asset’s five above-grade floors; obtain an as-built section/elevation before changing elevations.
6. **Footprint/detail bounds:** resolve stored GIS shape summaries versus its ring and overlay the detailed asset against the ring. Separate verified attached projections from modeled assumptions; preserve the approximately 2.6 m southward active-asset bound difference until sourced.
7. **Materials/detail:** verify brick bond/color, precast/stone trim identity, window/frame construction, entry glazing/lettering, sill/band profiles, roof membrane and service screens from current close-ups or project specifications.

## Sources consulted

- [Purdue Office of Emergency Preparedness — PSYC](https://www.purdue.edu/operations/emergency-preparedness/psyc/), revision 2026-04-06, retrieved 2026-10-30: four stories plus basement, wing-by-floor use, east and central stairwells, fire chimney, and Peirce connections on floors 2 and 3. Saved raw HTML: `sources/purdue_oep_psyc_2026.html`.
- [Purdue Archives — Psychological Sciences Building corporate record](https://archives.lib.purdue.edu/agents/corporate_entities/707), retrieved 2026-10-30: construction 1978–1983 and connection to the north end of Peirce Hall.
- [Purdue Historical Timeline](https://collections.lib.purdue.edu/timelines/puhistorical), Psychological Sciences Building listed as completed in 1980; milestone wording differs from the Archives construction span.
- [Purdue Archives — UA 62, Series 3 photo finding aid](https://archives.lib.purdue.edu/fa/UA62_Series3.pdf), search-indexed entries for Box 90 folders 10 (Aug 1980), 15 (Mar 1981), and 27 (Sep 1982); direct PDF open returned 403.
- [Purdue Archives — MSP19 News Service finding aid](https://archives.lib.purdue.edu/fa/MSP19_News_Service.pdf), search-indexed record `19.004.084`, “New psychology Building,” June 1981, one photo; image not inspected.
- [Mickrine — Psychological Sciences Building Door](https://commons.wikimedia.org/wiki/File:Psychological_Sciences_Building_Door.JPG), captured 2014-04-01 16:25:52; CC BY-SA 3.0. Original retained as `sources/psych_sciences_door_2014_original.jpg`.
- [Mickrine — Purdue Psychological Sciences Sign](https://commons.wikimedia.org/wiki/File:Purdue_Psychological_Sciences_Sign.JPG), captured 2014-04-01 16:31:42; CC BY-SA 3.0. Original retained as `sources/psych_sciences_sign_2014_original.jpg`.
- [Esri World Imagery](https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer), retrieved 2026-10-30; imagery capture date unknown. Attribution and exact extent are retained in `sources/current_world_imagery_provenance.json`.
- [Purdue BuildingShapes feature service](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0), live FID 239 query and earlier project snapshot; raw feature and measurement metadata retained as described above.
- Existing project context only: `audit/new_psyc/RESEARCH.md`, `QA_REPORT.md`, `evidence.json`, and `modular/manifest.json`. They identify past interpretations and asset bounds, not independent proof of real facade geometry.

## Research-only disposition

Focused exterior pass complete with major face, connector, opening, roof, and height gaps retained. No building geometry, master Blender file, placement, owner assignment, or grade was changed. The existing five-above-grade-level asset interpretation is specifically unverified against Purdue’s current four-stories-plus-basement record.
