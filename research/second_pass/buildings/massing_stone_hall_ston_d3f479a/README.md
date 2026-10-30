# Winthrop E. Stone Hall (STON) — bounded exterior research pass

**Queue rank:** 19 · **stable ID:** `massing_stone_hall_ston_d3f479a` · **owner:** Rossen (preserved)
**GIS match:** Purdue BuildingShapesZip4, layer 0, FID 240 (`STON`)
**Intended reference:** extant campus building, with present-day overhead context and 1959 archive photographs as dated facade evidence. This is a provisional research package with important face and dimension gaps, not a build-readiness claim.

## Findings

Stone Hall is a red-brick and light-stone academic building with a strongly ordered, nearly symmetrical entrance elevation, repeated tall vertical window openings, a narrow upper window band, and a low, plain parapet/roof silhouette. Its official footprint is an irregular, stepped outline about 57 × 60 m in the project’s approximate local frame. A new north-up IndianaMap image shows multiple roof areas and equipment, a large dark center/open-looking area, and a projecting entrance at the south edge. The GIS boundary partly follows the inner recess but contains no interior ring; the exact courtyard/void/low-roof condition is not yet resolved. Aerial edges cannot substitute for wall lines.

The best face details are the four inspected Purdue Archives photographs, including a close entrance view and two different long-elevation views. Two are dated September 14, 1959; the other two are undated. They document a repeated bay rhythm, vertical light-stone/stone-colored frames, contrasting brick, upper small windows, tall lower windows, and a formal raised entrance with three vertical portal bays and broad shallow steps. An online Purdue Events place page links an additional entrance photo but does not disclose its capture date, photographer, or reuse licence. The old photographs do not establish every present-day opening or renovation. There are no registered camera poses or dimensioned public elevations in the retained package.

## Identity, history, and source reconciliation

Purdue’s BuildingShapesZip4 FID 240 identifies `BLDG_ABBR=STON`, **Winthrop E. Stone Hall**, at **700 Mitch Daniels Blvd**. Purdue Libraries’ historic building record (record 71, local snapshot retrieved 2026-10-26) names the architect as Scholer Corporation, gives construction begin/end years 1954–1957, reports 118,984 sq ft, lists brick and stone as materials, and identifies F. A. Wilhelm Construction Company and Tonn and Black as contractors. It states that the building was originally the Home Economics Administration Building and was renamed in November 1976. The separate corporate agent record gives the same naming history. These are institutional-history records, not measured geometry. The Events page independently matches the current name and address.

The old building record’s renovation array contains an apparent date typo (“1885–1986”) while the narrative says reroofing in 1985; it also records 1989–1990 classroom work and a 1992–1993 restaurant/hotel/institutional kitchen renovation. Preserve the uncertainty: these entries do not establish exterior scope or date a facade change. The archive set labels the main photos 1959. Do not assume all 1959 details survive unchanged.

The mapped feature has one 12-unique-vertex ring in EPSG:4326. Using the project’s approximate local transform documented in `modular/AGENTS.md` (X east, Y north; origin 40.4274° N, 86.9137° W), the ring-derived polygon is about **2,218.2 m²** with a **227.9 m** perimeter and spans about **56.6 × 60.0 m**. These are calculations from a campus GIS ring, not a survey. Its stored `Shape__Area=3,834.203` and `Shape__Length=299.581` conflict with the transformed ring (area ratio about 1.73; length ratio about 1.31). The source returns WGS84 coordinates while its geometry-property metadata says metres; the retained audit therefore uses the ring for approximate plan position and excludes these inconsistent aggregate attributes.

The ring is a single polygon with no interior ring. The 2026-10-30 north-up image has been overlaid with the same ring at `audit/massing_stone_hall_ston_d3f479a/stone_hall_current_aerial_gis_overlay.png`; the unaltered orthophoto and exact export metadata/hash are in `audit/massing_stone_hall_ston_d3f479a/sources/`. The overlay indicates the boundary broadly follows the exterior roof/wall envelope, but it does not explain the dark center/open-looking region. Confirm whether it is an open court, covered atrium, or low roof with a section plan or oblique image before treating it as building floor area. No internal courtyard hole should be invented or ignored silently.

## View/source register

Stable view IDs refer to the retained files under `audit/massing_stone_hall_ston_d3f479a/sources/`. Exact SHA-256 values are listed in `source_registry.json` and can be recomputed from each retained file. The archive thumbnails are about 600 × 518 px (view 1374 is 405 × 518; view 1373 is 595 × 518); these are not full-resolution negatives. Photographer and camera location are not stated in the retained records.

| ID | View and date | Evidence and limitations |
| --- | --- | --- |
| `ARCH-1371` — `stone_hall_archive_1371.jpg` | Broad, near-frontal long elevation; Purdue eArchives ID 1371; archive page says 1959-09-14 | Shows repeated tall openings separated by pale vertical piers, a smaller rectangular window row below the parapet, and a regular horizontal stone band. Trees, flagpole and distance obscure base details; exact total opening count is not reliable at thumbnail size. |
| `ARCH-1372` — `stone_hall_1959_archive_1372.jpg` | Three-quarter corner view; eArchives ID 1372; 1959-09-14 | Shows main entrance in the longer elevation, the corner turn, formal stone-framed entrance group, steps, tall windows and upper row. Establishes that the same ordered facade vocabulary continues around a second face, but no camera pose or scale. |
| `ARCH-1373` — `stone_hall_archive_1373.jpg` | Close, centered entrance; eArchives ID 1373; date not supplied | Best profile/detail evidence: central doorway/portal composition, flanking glazed bays, upper transom/window panels, pale vertical surrounds and decorative sawtooth/crest-like relief at the head. Broad stairs and side cheek walls are clear; original image is still a small scan. |
| `ARCH-1374` — `stone_hall_archive_1374.jpg` | Oblique along long wall; eArchives ID 1374; date not supplied | Shows long brick elevation with a repeated upper band and tall lower window groups bounded by pale vertical surrounds; a doorway/entry interruption appears down the run. Foreshortening and low-resolution scan prevent full count or reveal-depth measurement. |
| `ORTHO-2026-10-30` — `stone_hall_indianamap_current_2026-10-30.jpg` | Indiana Geographic Information Office Current Imagery ImageServer, EPSG:3857, export 1400 × 950 px; retrieved 2026-10-30; acquisition date absent from response | North-up view reveals plan/roof divisions, central dark area, rooftop units, site walks and the south-side entrance projection. It is a roof/site view only and cannot establish elevation, wall alignment below eaves, roof heights or current material condition. Original retained with its request parameters and SHA-256. |
| `EVENTS-PLACE` | Purdue Events Calendar place page, [Winthrop E. Stone Hall](https://events.purdue.edu/winthrop_e_stone_hall); inspected 2026-10-30 | Page identifies the address and links an entrance photo. A recent-activity item says a photo was posted 2022-05-29, but the page does not establish that the linked hero image was captured then. Image has no visible camera pose, photographer credit or reuse licence in the page record; it was not downloaded. Use only as a limited visual lead. |
| `HIST-71` | Purdue Campus Facilities and Buildings Historic Database, [record 71](https://collections.lib.purdue.edu/campus/buildings/71); retrieved 2026-10-26; saved HTML | Institutional chronology, architect/contractor/material and area facts. Not an elevation or image survey; contains the renovation-date inconsistency described above. |

The four archive image records and captured files are also linked from `purdue_historic_building_record_71.html`. Individual eArchives record IDs are 1371–1374. They are different angles, but without camera stations none can be assigned confidently to cardinal faces from the photograph alone. The IndianaMap raster is the source that orients the entrance projection to the **south**; treat this as a map-aligned reading, not a photogrammetric registration of the 1959 camera positions.

## Plan, orientation, and exterior organization

The raster’s north is up (EPSG:3857). The dominant formal entrance/step projection falls at the south side of the mapped footprint, on the 700 Mitch Daniels Boulevard approach. This aligns with the 1959 central entrance composition. Use **south formal entrance elevation** as the present working orientation. The wide ring extends roughly 57 m east–west and 60 m north–south, with a broad south-facing range and a stepped/recessed north-west portion. The exact internal plan remains unknown.

The overhead image shows:

- a south range across most of the building width, with a centered projecting entrance landing/stair aligned toward Mitch Daniels Boulevard;
- an east range extending north, with a large pale/gray roof area and multiple mechanical units;
- a west/north-west range and smaller connected roof portions that frame the dark central area;
- a large central dark region and smaller roof/recess transitions; the imagery alone does not distinguish open sky, shadow, low roof, and glazed/covered court reliably;
- several small rooftop mechanical units/vents on the east and west/north roof areas; their exact number and screens are not resolved;
- pedestrian paving and landscaped approaches around the perimeter. The Old Pump is a separate campus landmark at the building’s southeast corner, not part of the building shell.

This yields a connected, multi-part mass around a center/recess, not a justified single featureless rectangular block. However, the one-ring GIS polygon is not a floor plan. The building-side placement of each dark/gray roof region, wall junction, or internal court edge needs an oblique or plan source. Do not fill the apparent center with solid building mass, or cut it out as a courtyard, until its status is confirmed.

## Face-specific architectural schedule

Because no archive camera poses are recorded, the old-image schedules below are keyed to view rather than claiming a cardinal face. The overhead map supplies cardinal orientation only for the entrance projection and roof/site plan. Counts are visible minima or approximate runs at thumbnail resolution; hidden bays are explicitly unresolved.

### South formal entrance elevation (map-aligned; archive frontal/three-quarter views likely include it)

`ARCH-1371` provides a long, near-frontal elevation; `ARCH-1372` shows the entrance in a three-quarter view; `ARCH-1373` provides the entry close-up. The broad facade has a regular brick field interrupted by pale vertical pilasters/stone surrounds and horizontal pale belt courses. Tall, narrow rectangular openings repeat at the main occupied level; a continuous upper band contains smaller, more square openings beneath a simple projecting parapet/cornice. The 1371 frame shows at least ten individual upper openings and at least seven tall lower openings, with obscured/edge bays excluded from that minimum. Exact total count and inter-bay spacing are not calibrated.

At the main entry, three adjacent vertical portal bays are legible in `ARCH-1373`: a central door opening with tall glazing/transom above and flanking glazed/relief fields within a broad pale stone frame. Sawtooth or chevron-like ornament and a small central crest/medallion sit over the doorway; do not reduce it to a blank stone rectangle. The image does not establish the exact number of door leaves or all internal subdivisions. Broad shallow stone/concrete steps span the entry group; side cheek/retaining walls define the stair approach, with a lower landing/path continuing outward. The 1959 photos show no accessible-ramp arrangement, and the current image does not expose a complete entry close-up. Current step/rail condition is unknown.

### Long return / side elevation (`ARCH-1374`)

The oblique side view shows a long brick run under the low roof line. Repeated pale vertical pier/surround strips divide it into regular bays. Each clear lower bay has a tall narrow multi-pane window; a shorter rectangular opening sits in the band above. At least seven tall lower windows and several upper openings are visible in the image, but the far end and near entry interruption are foreshortened. One door/entry recess interrupts the window rhythm. Exact bay count, door location relative to building corners, sill/head heights, frame projection and opposite side pattern remain unknown.

### Corner elevation (`ARCH-1372`)

The two visible faces meet at a clear exterior corner. The same brick, pale pier, belt-course and upper-window palette continues around it; the main entrance lies along one face rather than wrapping the corner. The 3/4 view suggests the entrance is near the middle of a long face, but perspective and no camera pose do not define the cardinal assignment or exact station. It shows that the building is not a single uninterrupted blank wall and that the window spacing remains regular around the return. Complete adjacent-face counts are not observable.

### West / north and remaining east / rear runs

The GIS ring and current overhead roof view confirm perimeter massing and recesses but provide no wall openings. The archive image directions are unregistered; each photograph may show one of these facades, but none can be safely labeled as a particular remaining cardinal side from the local copy alone. No separate current west, north, east or rear frontal view with a pose is retained. Do not mirror the south or 1374 opening rhythm onto unseen runs. Side-specific door, service, window and infilled-opening counts remain unknown.

## Roof, materials, and signature details

The 1959 views show a low, nearly flat/parapet-like silhouette with a thin projecting edge and no visible tower, dormer or steep roof profile. The 2026 nadir image instead resolves several flat/light-gray roof fields, brown/red-toned perimeter roof strips and rooftop equipment. This is compatible with the old low silhouette but does not establish roof pitch, parapet height, or renovation history. The current raster has winter/leaf-off trees and some shadow; its acquisition year and roof surface class are not exposed in the exported response. No roof height or equipment elevations are measured.

Purdue’s historic record identifies brick and stone as construction materials. The photos support red-brown masonry wall fields, light-colored vertical piers/window surrounds and horizontal bands, and a light-colored formal entrance frame. Exact stone type, brick bond/mortar scale, sill/lintel section, roof membrane/tile identity, glazing material, sash profile and present material condition are not documented. Black-and-white 1959 images cannot establish color. The linked Purdue Events image appears to provide a contemporary entry reference but is not date- or licence-verified here; its color should not become an exact palette. Keep color/material identity at the source-supported level.

Architectural features that carry the silhouette/depth include the shallow low roof edge, stone-colored pilasters/bands, tall repeated window reveals, the raised central entrance and relief/frieze above the portals. The old pump at southeast, campus walks, trees, flagpole and people/cars are landscape/site objects. Historic photos include period vehicles and planting; none should be modeled as permanent architecture.

## Floor and height constraints

The cached GIS reports `NUM_LEVELS=6`, `CountOfFLO=6`, `Extrution=45`, `Elevation=622.4`, `B=-12`, `G=-8.2`, and `F01=3.78`, `F02=15.78`, `F03=27.78`, `F04=37.78`. The layer metadata does not define units or datum for `Extrution`, `Elevation`, or the floor fields. The existing model audit treats four F-fields as facade bands and `Extrution=45` as 45 ft = 13.716 m for visualization only. That height conversion is an assumption, not a measured roof level. The six-level count, four F entries and B/G values do not establish a six-storey facade; below-grade or datum conventions may be involved.

No public building section/elevation or point-height survey was located in the retained research. Treat total height, parapet/eave levels, floor-to-floor spacing, roof-step heights and ground grade changes as unknown. The historic 118,984 sq ft is reported gross area, not footprint area; do not use it to infer floor count or per-level plate geometry.

## Discrepancies and evidence limits for the existing asset

The existing asset audit (`audit/massing_stone_hall_ston_d3f479a/audit_note.md`, independent R2 grade file and reopen report) records that its base mesh matches the transformed 12-vertex GIS ring, the saved blend reopens without external image dependencies, the wall material scheme is brick plus light trim, and a 13.716 m height comes from interpreting the undeclared `Extrution=45` as feet. These are asset/provenance facts; the asset is not evidence of the physical building.

The R2 independent review gave 8.0/10 and specifically noted that facade proportions/openings remain photo-informed stylization, the GIS summary metrics conflict with the ring, the transform is approximate, the four visible bands do not prove six stories, and no measured top elevation was found. This dossier adds a retained current overhead tile, a GIS overlay, face-specific observations from each archive view, current-name/address/history reconciliation and a specific gap register. It does not change the asset, owner, location, grade or acceptance status.

| Issue | Evidence reconciliation | Still unknown |
| --- | --- | --- |
| GIS `Shape__Area` / `Shape__Length` vs ring metrics | Recomputed from the WGS84 ring using the project’s documented approximate campus transform; the ring-derived area/perimeter are used | Surveyed outline and original GIS metric calculation/CRS |
| Single ring vs center/open-looking overhead space | 2026 north-up roof view and overlaid mapped ring show an internal dark region without a hole in the feature | Open court vs shadow/low roof/glazing; actual void and inner wall boundary |
| Six GIS levels vs four facade bands | Raw attributes preserved; `NUM_LEVELS` and `CountOfFLO` are not accompanied by layer definitions, F01–F04 look like four separate floor fields, B/G are ambiguous | Measured sections, floor datum and face-specific story-to-window mapping |
| Historic facade vs current condition | 1959 archive shows detailed stone/brick facade; official Purdue place page links an undated entrance image, and current overhead shows roof/site | Which windows, frames, stone details and accessibility features survive today; renovation scope |
| Roof and mechanicals | Flat/low roof edge in historic photos; multiple roof areas/equipment in modern nadir tile | Heights, slopes, screens, equipment type/locations at architectural accuracy |

## Builder-facing brief within current evidence

Preserve a compact, stepped campus block with a formal central south entry facing Mitch Daniels Boulevard, a broad raised stair/landing, deep pale surround, three-bay vertical portal composition and decorative head relief. Use red-brown brick walls divided by pale vertical stone piers and belt courses. Show a regular tall-window rhythm below a smaller upper window band where supported by the reference view. Maintain the low parapet edge and multiple roof fields/equipment as an overhead composition. Treat the central dark/low roof area and internal enclosure as unresolved; retain a placeholder/gap until a floor plan, section or elevated oblique confirms whether it is open to sky. Keep the southeast Old Pump outside the building shell.

Safe constraints: official ID/address, approximate geospatial ring and orientation, 1954–57 construction history, brick/stone material families, formal entrance composition, recurring window/pier/band rhythm in the seen historic runs, low roof silhouette, and overhead placement of roof areas/equipment. Unsupported: exact cardinal assignment of each old archive view, full face counts, current window pattern, center void status, surveyed wall line, elevations, parapet/roof height, rooftop equipment schedule and step dimensions.

## Gaps and next evidence

| Item / affected face | Why unresolved and what was checked | Evidence that would resolve it | Consequence if guessed |
| --- | --- | --- | --- |
| Current walkaround and cardinal registration of archive faces | Four archive photos lack camera coordinates/bearings; only south entry position is map-aligned by nadir image | Current face-on views from known map positions/headings; archival photographer notes or photo negatives with pose/context | Facade families assigned to wrong cardinal walls; incorrect orientation of entry details |
| Full opening count by face and floor | 600 px archive copies, perspective/edge crop and trees; no elevation drawings | High-resolution facade survey, dimensioned elevations, or full current walkaround with close/mid/distant views per face | Repeated bays mirrored or invented on unseen walls |
| Central interior/open space | Dark center in overhead tile, no GIS hole; imagery cannot distinguish open courtyard from shadowed/low or glazed roof | Roof plan/section, oblique aerial, or current courtyard photographs from above and at grade | Major building volume filled or courtyard removed incorrectly |
| Vertical datums, floor count and height | GIS six-level attributes, B/G/F fields and `Extrution=45` are undefined; 45 ft is only an existing estimate | Architectural sections/elevations or survey/point cloud with vertical datum and floor labels | Wrong story count, window-band heights and roof silhouette |
| Current material, stone profiles, sash and entry details | Best inspected ground detail is 1959; online Purdue events image lacks date/licence/metadata; color cannot come from B&W scans | Dated current close-ups of brick/stone/window/door details; project renovation specifications | Historical detail/color mistakenly treated as current |
| Roof planes and equipment | New IndianaMap tile shows plan only; source response omits imagery acquisition date | Dated high-resolution oblique/roof photo, measured roof plan, current point cloud or Facilities roof records | Wrong roof edge/plant placement and silhouette |
| Stair width, step count and accessible approach | 1959 close view shows broad shallow stair but no scale; current condition unobserved | Current frontal entry photo and dimensioned site/entrance plan | Incorrect scale/depth and missing current ramp/rail arrangement |
| Southeast site feature boundary | Purdue Arboretum identifies the historic Old Pump at the southeast corner, but no measured separation line is in the map feature | Current site plan or georeferenced ground image | Landmark merged into shell or misplaced relative to entrance/site |

## Sources and retained material

- [Purdue Campus Facilities and Buildings Historic Database, Stone Hall record 71](https://collections.lib.purdue.edu/campus/buildings/71) — saved HTML, history, architect/contractor/material/area fields and archived image citations.
- [Purdue Archives corporate entity record 689](https://archives.lib.purdue.edu/agents/corporate_entities/689) — Home Economics Administration name and November 1976 renaming.
- [Purdue eArchives, Purdue Buildings and Campus Scenes](https://earchives.lib.purdue.edu/digital/collection/pbuildings/) — image records 1371–1374 and retained 600px copies; record 1371/1372 dates are 1959-09-14.
- [Purdue University Events Calendar place page](https://events.purdue.edu/winthrop_e_stone_hall) — current name/address and linked entrance image, with no verified capture date or reuse licence.
- [Purdue Arboretum Explorer: Old Pump](https://www.arboretum.purdue.edu/explorer/features/old-pump/) — identifies the pump at Stone Hall’s southeast corner; site context only.
- Official GIS feature URL and saved metadata, service layer schema, ring and source limits are retained in `audit/massing_stone_hall_ston_d3f479a/sources/source_registry.json`, `purdue_building_gis_fid240_ston_4326.json`, and `purdue_building_gis_layer_metadata.json`.
- IndianaMap original tile and export request are in `audit/massing_stone_hall_ston_d3f479a/sources/stone_hall_indianamap_current_2026-10-30.jpg` and `.json`; the separate GIS overlay is at `audit/massing_stone_hall_ston_d3f479a/stone_hall_current_aerial_gis_overlay.png`.
- Existing model diagnostic renders and validation are in the audit folder; they document the current asset only and are not real-building references.

**Pass outcome:** exterior research package saved with significant current-face, courtyard, opening-count and height gaps retained. No model, grade, owner, placement or master change is part of this pass.
