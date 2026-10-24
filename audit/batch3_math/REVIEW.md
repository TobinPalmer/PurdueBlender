# Mathematical Sciences Building (MATH) — batch 3

Updated source: `modular/buildings/math_sciences.blend`  
Export collection: `Asset_math_sciences`  
Baseline copy: `audit/batch3_math/before.blend`  
Review date: 2026-10-23

## What changed

- Rebuilt the east tower elevation and the south end elevation around 81 true window openings. The two source GIS-derived wall prisms were replaced with brick panels around full-depth openings. A ray check passes through the center of all 81 openings and hits solid brick at all six control points between openings (`geometry_checks.json`).
- Added pale stone window reveals, subdivided glazing, vertical piers and a glazed east entrance. The entrance center is at local `(17.52, -13.50)` m. A Google Maps pin at 40.4261348, -86.915642 transforms to approximately `(16.42, -13.58)` m relative to the existing placement marker. That is a close contextual match for the east entrance; the Maps pin is not a surveyed coordinate.
- Kept the original official-footprint-derived structural bounds, local coordinate frame, placement marker, and overall scale. The two windowed wall panels retain their source prism bounds: east `x=16.754..17.307`, `y=-27.489..11.981`, `z=0..33.2` m; south `x=-2.303..12.924`, `y=-33.961..-33.594`, `z=0..33.2` m.
- Added nine estimated office-floor slabs, low oak library carrels, group tables, carpet, three low bookcase runs, a windowless Testing Room 352 with a desktop, and schematic third-floor elevator doors and stair flights. The library features follow Purdue's 2025 reopening article and photo. Their exact positions and dimensions are inferred because no current room plan was located.
- Set the flat penthouse roof surfaces to a dark membrane finish. Procedural brick and carpet materials remain inside the file; no external image or texture links were added.

## Evidence and registration

| Check | Status | Evidence and limits |
|---|---|---|
| Building identity | Verified | Purdue Archives identifies MATH as the 10-story Mathematical Sciences Building, in use since 1967. Google Maps lists 150 N University Street. |
| Horizontal frame | Preserved | Existing master placement origin is `[-181.119995, -126.905003]` m; no marker, rotation, or asset origin was changed. The GIS polygon feature is FID 227. |
| Footprint | Preserved | Existing GIS-derived shell and local footprint were not translated, rotated, or uniformly scaled. Only two facade wall prisms were cut and refilled around windows. GIS is a public footprint layer, not a measured survey. |
| Facade and materials | Partly verified | Purdue Statistics' Math Building photo supports red brick, pale framing, and repeated narrow windows. Exact window bay spacing, height, masonry specification, roof finish, and other elevations remain estimated or unverified. |
| Third-floor library | Partly verified | Purdue's 2022 Board plan identifies 2,884 GSF of third-floor library renovation and shows core circulation. Purdue Libraries' September 2025 article/photo documents carpet, rearranged shelves, group study, and a windowless room 352 testing room. Furniture layout is illustrative. |
| Vertical dimensions | Estimated | Purdue Archives confirms 10 stories. The existing 33.2 m wall envelope and 42.9 m maximum asset bound are not supported by a surveyed elevation. Added typical floor slabs use an estimated 3.25 m interval. |
| Interior above third floor | Unverified | Only schematic repeated floor slabs were added; upper-floor rooms, stairs, offices, equipment, and exact floor heights are not established by the available plans. |
| File integrity | Verified | Source file saved and reopened for the inspection and renders. Export remains `Asset_math_sciences`; the collection now contains 551 direct objects and 584 objects including children. No external image paths are present. |

## Source record

- Purdue Statistics exterior photo: <https://www.stat.purdue.edu/images/about/Math-Bldg-.jpg>. Retrieved 2026-10-23. Photo date and CRS unknown. Local copy from the earlier review is `audit/next_math/reference.jpg`.
- Purdue Board of Trustees, Libraries Study Space Renovation, Exhibit B, third-floor MATH plan, dated 2022-09-28: <https://www.purdue.edu/bot/meetings/past-meetings/2022/09.%20oct/pfc/Libraries%20Study%20Space%20Reno.pdf>. Retrieved 2026-10-23. Page image is `plan_third_floor.png`; retained PDF is `board_floorplans.pdf`.
- Purdue Libraries reopening article, dated 2025-09-09: <https://blogs.lib.purdue.edu/news/tag/general/page/6/>. Retrieved 2026-10-23. Its interior photo is `library_2025.jpg`; source page describes the new room 352 testing room and refreshed shelves, carpet, and furniture.
- Google Maps listing: <https://www.google.com/maps/place/Purdue+Mathematical+Sciences+Building/@40.4261348,-86.915642,17z/>. Retrieved 2026-10-23. Address: 150 N University St, West Lafayette, IN 47907. Pin is WGS84 at 40.4261348, -86.915642. Converted with the project's local approximation; it is about 15.5 m from the official footprint centroid and should be read as a place/entrance marker, not a surveyed centroid.
- Purdue University GIS BuildingShapes FeatureServer, FID 227: <https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0>. Cached retrieval 2026-10-22; feature survey date unknown; source CRS EPSG:4326. The local conversion uses the project origin 40.4274, -86.9137 and the approximation in `modular/AGENTS.md`.
- Purdue Archives MATH history and story count: <https://archives.lib.purdue.edu/agents/corporate_entities/672>. Accessed 2026-10-23; describes the building as a 10-story structure and records its existence from 1967.

## Visual review and scoring

`exterior_after.png` shows the east and south elevations after the openings and entrance work. `library_after.png` shows the modeled third-floor study layout. Both were rendered from the saved, reopened asset. `build.log` records the rebuild and object counts; `render.log` records the two renders.

Independent child review has not yet run because all agent slots were occupied. No score is claimed yet. The remaining evidence gaps, particularly exact upper-floor plans and measured height, should remain visible in any score.

## Follow-up revision after independent review (2026-10-23)

The first independent score remains **6.5/10**; this revision has not yet received a follow-up independent score. It should not be described as a 9/10.

### Changes and checks in this pass

- Increased neutral exterior fill and exposure and added a neutral ground plane. Reopened renders now include the overall view plus orthographic east, west, north, and south elevations (`exterior_after.png`, `exterior_east_after.png`, `exterior_west_after.png`, `exterior_north_after.png`, `exterior_south_after.png`). The main view shows the brick color and window pattern more clearly. West/north elevations remain weakly supported by source photos and visibly less articulated; they are left for review rather than guessed into detail.
- Reworked the third-floor library representation using the 2022 renovation plan: six room-boundary segments align with modeled zone divisions, with gaps preserved for inferred doorway openings. Three glass-front group-study rooms, room 352 at the southeast plan location, a shared aisle, elevators, and stair elements are shown in the saved model. The group-room exact locations/sizes, opening widths, room 352 dimensions, and furniture arrangement remain inferred because no current dimensioned as-built plan was located. `plan_layout_overlay.png` overlays the model partition segments on the original plan crop. The 2025 source confirms types of spaces and materials, but the 2022 plan predates the 2025 reopening and is used for room/core relationships only.
- Added `third_floor_core_after.png` for the full modeled third-floor/core context. In the top-down render, divisions, study rooms, shelf runs, carrels, and circulation are visible, though perspective/lighting leaves substantial hard shadows and the room remains schematic.
- Replaced the previous AABB-only footprint note with a structural-edge comparison: the official GIS FID 227 polygon boundary is sampled at at most 0.25 m against 50 source wall-prism centerlines extracted from the saved asset's source-mesh backup. The two reconstructed window walls retain the corresponding source prism bounds. GIS-to-shell median offset is 0.091 m; 87.7% of boundary samples are within 0.25 m and 92.3% within 0.50 m; P95 is 0.838 m and maximum is 1.538 m. Shell-to-GIS median is 0.092 m, P95 1.069 m, maximum 1.947 m. These are bidirectional centerline-to-boundary distances, not polygon IoU or survey accuracy; a nominal half-wall-thickness offset is expected. See `structural_edge_comparison.json` and `structural_edge_overlay.png`.
- Re-rendered from the saved `math_sciences.blend` in a separate Blender process, which reopened the file before rendering. `geometry_checks.json` also records `reopened: true`; its 81 east/south pane-center rays pass through the shell and all six wall control rays hit brick. Direct/export counts are 551/592. The model itself was saved by the builder before these checks; render scripts do not modify or save the source file.

### Remaining evidence limits

- The 2025 article and photo do not publish current library room boundaries or exact furniture placement. The 2022 plan shows proposed/renovation geometry, not a verified current as-built layout. Group-room glass and precise room arrangement are therefore inferred.
- No dimensioned elevations or reliable measured building height were found. The 33.2 m wall height, 42.9 m maximum extent, 9 intermediate slabs, and typical floor spacing remain estimates. An ArcGIS attribute lists 12 levels, but field semantics/units are not documented in the available layer metadata and are not used as measured height evidence.
- The available exterior reference supports brick, vertical windows, and pale framing principally on the visible sides. The west and north render views expose incomplete, unverified façade detail. Do not claim the full exterior is source-verified.
- The plan overlay and GIS-edge overlay are evidence aids, not precision survey deliverables. GIS projection conversion follows the project local approximation recorded above.

### Latest evidence files

- Exterior: `exterior_after.png`, `exterior_east_after.png`, `exterior_west_after.png`, `exterior_north_after.png`, `exterior_south_after.png`
- Interior: `library_after.png`, `third_floor_core_after.png`, `plan_layout_overlay.png`
- Footprint: `structural_edge_overlay.png`, `structural_edge_comparison.json`
- Reopen and opening checks: `geometry_checks.json`; render log: `render.log`

## Third builder pass (2026-10-23; pending independent review)

This pass starts from the review's 7.0/10 findings. The asset builder retuned the saved `MATH_Photo_Brick_Metre` procedural material to show stretcher courses and lighter mortar at close range. Brick width/row height are set to .25/.078 m, and mortar size to .008 m; these are visual material estimates, not a measured masonry specification. The same shader remains assigned to the inherited shell and the reconstructed east/south wall panels. The existing east/south window and pale reveal geometry remains where supported by Purdue's exterior photo. I added no north/west window pattern because the sources do not establish one. The shell custom property records this limit.

On the third floor, the three shelf runs are moved to y=12.9/16.9/20.9 within the plan-labeled 311 library region, rather than extending into the north area. Warmed the chair/screen palette and muted the carpet to better match Purdue Libraries' 2025 photograph. Added low base trim only along the six existing 2022 plan-derived partition segments, making the room edges and inferred doorway gaps easier to read. The furniture, group-room count/locations, current partitions, and walk paths remain schematic where the 2025 source does not publish an as-built plan.

The updated `render_math.py` opened the saved asset in a fresh Blender process and rendered an overall exterior, all four elevation views, a close brick/window detail, a library cutaway, a shadow-free plan-reading diagram, and a third-floor/core context view. See `exterior_after.png`, `exterior_east_after.png`, `exterior_west_after.png`, `exterior_north_after.png`, `exterior_south_after.png`, `brick_detail_after.png`, `library_after.png`, `library_plan_diagram.png`, and `third_floor_core_after.png`. The close detail now visibly shows the procedural coursing at meter scale. The north/west images remain documentation of the current model's unsupported areas, not verified elevations; they still have large unarticulated wall runs and exposed/intermittent slab edges. Purdue's Admissions tour note confirms a pedestrian land-bridge below MATH, but does not identify or validate upper elevation openings. No facades were filled or fenestrated on that basis.

A separate Blender opening check reopened the asset after the save: `geometry_checks.json` records `reopened: true`, the expected `Asset_math_sciences` collection, 551 direct objects and 593 objects including children. All 81 east/south pane-center rays pass through the tested shell/infill positions; the six brick control rays hit brick. The check excludes the glazing/reveals and does not establish the accuracy of the assumed window schedule. `material_check_round3.log` records the saved brick node values. `build_round3.log` and `render_round3.log` record the rebuild and fresh renders.

### Current limits retained

- Exterior photo coverage is strongest for the east/south views; north/west window and facade details remain unverified. The brick color/courses are plausible and source-informed, but masonry units and mortar are not measured.
- The 2022 plan informs room/core boundaries; it predates the 2025 reopening. The 2025 text/photo confirms carpet, shelves, group-study rooms and windowless room 352, but not exact current partitions/furniture. Those features remain labeled inferred.
- The model's 33.2 m wall top, 42.9 m maximum, nine intermediate slabs, floor intervals, upper room plans and rooftop composition remain estimates. No elevation or height survey has been located.
- The previous independent review remains **7.0/10**. This pass has not received an independent score; do not report a higher rating or 9/10 yet.

New evidence source: Purdue Daily Visit Tours, MATH stop, https://ontour.admissions.purdue.edu/daily-visits/ (accessed 2026-10-23). The tour text warns about wind while walking under the land bridge. It supports the existence of a ground-level passage only.

## Round four builder pass (2026-10-23; saved-file verification complete, independent review pending)

### Changes made

- Added explicit Blender custom properties to the roof slab, penthouse base/coping/louvers and typical story slabs. These identify the profile and metric extents as estimates, retained for visual massing continuity, not measured forms. The file still carries the 10-story identity separately from estimated slab elevations, 33.2 m wall top and 42.9 m maximum extent.
- Removed clutter caused by 33 legacy illustrative library furniture objects that overlapped the newer review set. They are hidden in the standalone model viewport and renders; the baseline library floor, border and perimeter walls remain. See `legacy_interior_visibility_round4.json`. This changes only `math_sciences.blend` and is reversible by clearing those visibility flags.
- Created a plan-reading view using material/object colors and explicit 2022 room-zone labels (`library_plan_round4.png`). Its furniture and group rooms remain schematic where 2025 as-built dimensions are unpublished. The view was rendered from a newly reopened saved file.
- Reopened the saved asset for the opening check: 551 direct / 593 including child objects; the 81 tested pane-center samples are clear through the shell/infill, and all six solid-wall controls hit brick. This validates modeled openings at test points only, not their real-world schedule or glazing/reveal alignment. See `geometry_checks_round4.log`.
- Attempted a new low-angle passage view, but it framed the east entrance facade and did not show a confirmed tunnel opening. It is retained as `passage_round4.png` for troubleshooting only and is excluded from verification claims. No tunnel geometry or dimensions were invented.

### New source checks and limitations

- Purdue Daily Visit Tours warns visitors under MATH's land bridge about wind: [official tour page](https://ontour.admissions.purdue.edu/daily-visits/). It supports the pedestrian passage's existence, not its opening dimensions, bearing or supports.
- An independent street-level image by local journalist Dave Bangert shows the sheltered passage and square supports: [photo post](https://x.com/davebangert/status/1093924681659367425) (image returned by search as `https://pbs.twimg.com/media/Dy5msiGU0AEsCM0.jpg`). This supports the broad passage/support typology. The image page did not expose a reliable capture date or a view orientation in the accessible material; do not use it to locate the passage in model coordinates.
- Purdue Archives' finding aid lists two 1968 images under “Math Science West Side” (MSP19 item 19.003.102): [finding aid](https://archives.lib.purdue.edu/fa/MSP19_News_Service.pdf). This is a catalog record only; the image files were not accessible for visual inspection, so it does not verify facade pattern.
- Google Maps satellite/Street View was not available for visual inspection in this environment. The previously recorded public pin remains at 40.4261348, -86.915642 (150 N University St); it is about 15.4 m from the FID 227 footprint centroid and is only an entrance/place marker. Imagery dates vary by panel and could not be confirmed this round. Use GIS FID 227 for horizontal footprint checks; do not treat the map pin as a survey.
- Therefore north/west elevation details, exact land-bridge location/dimensions/support positions, roof/penthouse geometry, and all vertical heights remain unresolved or estimated. No unsupported facade openings were added.

### Round-four visual/check evidence

- `library_plan_round4.png` — source-labeled top-down view rendered from the saved/reopened model. It improves separation of the current modeled study furniture and plan-derived boundaries; it does not prove the 2025 as-built room layout.
- `exterior_round4.png` is a refreshed lower campus-eye angle from the saved/reopened file; it reduces the broad visible rooftop face in the review composition but does not correct or verify the roof form. `render_exterior_round4.log` records it. The full overall and four directional set was also refreshed after the visibility cleanup; `render_round4.log` records completion.
- `geometry_checks_round4.log` — reopening and ray check. `annotate_round4.log` and `hide_legacy_round4.log` record file saves. `legacy_interior_visibility_round4.json` lists the hidden duplicates.
- No new independent score is claimed. The latest independent score remains 7.2/10 from round 3; this pass is pending review.


## Round five build update (2026-10-23; independent review pending)

- Removed the unsourced east-facade gold lettering that intersected a window bay. The east portal remains at its earlier approximate, map-context location.
- Adjusted the window reveal assembly to avoid the former dark corner blocks at surround joints. The transom now sits slightly proud of the vertical mullions to keep their crossing faces from z-fighting in close views; `brick_detail_after.png` is the saved-file close-up.
- Replaced `library_after.png` with a clean top-down/cutaway render (`library_cutaway_round5.png` remains the plan-focused evidence). The dedicated view omits the perimeter shell, overhead ceiling and inferred circulation strip that had obscured the room and furniture. Room boundary placement remains based on the 2022 plan, while exact current partitions and furniture positions remain inferred from the 2025 reopening article/photo.
- The available Purdue tour page confirms a ground-level land bridge but gives no bearing, location, dimensions or supports. I found no source that registers it to this shell. No passage geometry was added.
- Saved/reopened render and opening-check runs refresh the exterior and four elevations. `geometry_checks_round5.log` reports 551 direct / 593 total export objects, 81 clear pane-center samples and six solid-brick controls. This confirms the modeled through-openings only; it does not validate the real window schedule.
- GIS footprint and local placement are preserved. The unresolved north/west elevation details, roof/penthouse profile, floor-to-floor heights, 33.2 m wall top and 42.9 m maximum remain estimated/unverified. Purdue's 10-story count is not evidence for those metric heights.
- Google Maps imagery could not be visually inspected here; only the previously recorded place pin at 40.4261348, -86.915642 is available as a context marker. The pin and its imagery dates are not treated as survey evidence. See the source limitations above.

Latest independent rating: 7.1/10 (round four). Round five is awaiting independent review; no score is claimed for this build.

## Round six sign correction (2026-10-23; saved-file verification complete)

The round-five reviewer found that the east gold lettering was still present: the earlier cleanup line in `finish_math.py` contained literal `\\n` escapes after a comment marker and therefore never executed. Round six removes the actual `MATH_Signage_East` object from the saved standalone blend. `verify_sign_round6.log` records reopening the file and confirms `sign_present: false`; the export collection remains present with 592 total objects. The four-elevation render set was refreshed from the saved file; `exterior_east_after.png` visibly has no gold lettering. GIS placement and footprint were not modified. This is a focused repair, not a new independent score; round-five review remains 6.9/10 until another reviewer evaluates it.

## Round seven source and reopen audit (2026-10-24; no geometry edits)

- `validate_round7.py` reopened only `modular/buildings/math_sciences.blend` in Blender 5.2.3. The expected `Asset_math_sciences` collection is present with **550 direct objects / 592 total objects**; the earlier round-six log labels `all_objects` as `direct_objects`, so its 592 figure is a total count, not a direct count. `MATH_Signage_East` is absent.
- The GIS FID 227 source polygon transformed to the manifest local frame has bounds X `[-18.814985, 17.872343]` m and Y `[-33.961314, 33.804897]` m. The saved structural shell bounds differ by at most **0.00434 m** per bounding edge. This is a bounding-box check; use `structural_edge_comparison.json` for the separate bidirectional polygon-edge sample comparison (median offsets about 0.092 m).
- Purdue Archives' [MATH record](https://archives.lib.purdue.edu/agents/corporate_entities/672) supports a 10-story identity. The Purdue Statistics [exterior photo](https://www.stat.purdue.edu/images/about/Math-Bldg-.jpg) is only 196 × 258 pixels and is not georeferenced; it supports light red brick, pale vertical window surrounds, repeated narrow bays, and an opening under the upper building mass, but does not identify the photographed elevation. No facade schedule or opening location was inferred from it.
- A direct [Google Maps Street View request at the recorded MATH pin](https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=40.4261348,-86.915642) returned “No Street View imagery available here” in the 2026-10-24 check. Do not use it as evidence for the elevations.
- The official GIS REST layer exposes `F01`–`F10`, `R`, `NUM_LEVELS`, and related fields as numeric fields but publishes no field descriptions or units. They do not establish measured heights. Metric wall height, floor spacing, roof/penthouse profile, and mast height stay estimates/unverified. The new machine-readable results are in `round7_validation.json`.

No new independent grade is claimed. The latest grade remains 6.9/10 (round five); the source audit verifies the local shell/plan envelope and notes the remaining evidence gap, but does not address the prior score's unresolved facade, roof, and interior findings.

## Round eight — third-floor library/core vertical alignment

The R7 grade was 7.0/10. Its review found that the library/interior cutaway and stair/elevator features were disconnected vertically. Source audit traced this to a story-index mismatch: the 2022 Purdue Board of Trustees renovation plan labels the depicted library area as third floor, while the saved library finish had been placed at z=10.645 m against the model's F03 slab top at z=6.580 m. This vertical difference is an internal consistency correction only; the building's absolute elevations and floor-to-floor spacing remain estimates.

Aligned 249 plan/library and third-floor stair/elevator objects by −4.065 m to the modeled F03 slab and added a narrow aisle carpet connector from the library through plan-labeled hall 311 toward the elevator core. The Board plan supports the route relationship but does not dimension the corridor, so its width and exact centerline are inferred. The R8 plan render shows the now-contiguous visual path; it is still a model interpretation, not an accessibility or as-built circulation certification. Top-down and oblique previews: `library_plan_round8.png` and `library_oblique_round8.png`.

Blender 5.2.3 reopened the saved standalone asset. `round8_validation.json` passes: 550 direct / 593 total export objects, 249 aligned objects, no unpacked image dependencies, the removed east sign remains absent, and the structural-shell GIS bounding edges differ by at most 0.00434 m. The F03 slab and library finish top both reopen at z=6.580 m; stairs span z=6.605–9.545 m, elevator doors z=6.685–8.885 m, and the connector z=6.582–6.600 m. This is a coordinate/footprint reopening check, not proof of metric story heights or exact interior dimensions.

Updated the dedicated build procedure `finish_math.py` to reproduce the same correction and connector while avoiding repeated vertical movement on reruns. No master, manifest, shared index, or other building files were edited. No independent R8 grade is claimed yet; the remaining facade, roof/height, north/west elevation, and as-built interior uncertainties remain as stated in Round 7.

## Round nine — brick readability, interior review view, and evidence limits

The R8 independent reviewer scored the building **7.7/10**, below the 8.0 target. R9 makes a restrained, qualitative adjustment to the embedded procedural brick material, shifting it from the pale pink campus-view appearance toward red-brown and reducing the bright mortar response. The adjustment is informed by the [Purdue Statistics exterior photo](https://www.stat.purdue.edu/images/about/Math-Bldg-.jpg); it is not a calibrated color match. A high-resolution facade view and a closer third-floor library/core oblique view were rendered from the saved asset (`exterior_brick_r9.png`, `library_oblique_round9.png`). The interior view uses temporary review colors and a review-only floor plane; these were not saved into the asset.

The R9 source search did not find a measured MATH elevation or height source, nor a new direction-identified north/west elevation image. Purdue Archives continues to support the ten-story identity only; its generic 1997 Building Drawings catalog record is not identified as MATH and did not provide drawing content. The 33.2 m shell top, 42.9 m maximum bound, floor spacing, rooftop/penthouse form, and mast therefore remain estimates. No geometry was added to the blank elevations. The 2022 plan continues to support third-floor library/core relationships, but not as-built partition positions, route dimensions, or furniture placement.

Blender 5.2.3 reopened the saved `modular/buildings/math_sciences.blend`. `round9_validation.json` passes: 550 direct / 593 total objects, the R8 shell bounds and 33.2 m top are unchanged, the third-floor connector remains present, the brick material values reopen as saved, and there are no unpacked external image dependencies. The master file, manifest, shared index, and other buildings were not edited. Full source and uncertainty notes are in `evidence_round9.json`.

No R9 self-grade is claimed. R8's independent **7.7/10** remains the latest grade until a fresh independent reviewer evaluates the R9 asset and evidence.

## Round ten — Indiana 3DEP roof-height evidence and source limits

R9's independent score was **7.8/10**. R10 adds a direct regional surface-height check without inventing floor elevations, roof outlines, openings, or current room dimensions. The Indiana GIO 3DEP tile index places this MATH footprint in 2018 tile `in2018_29951885_12`, collected on 2018-04-20. I analyzed its public 5-ft first-surface DSM together with the same-tile 2.5-ft bare-earth DTM, masking the Purdue GIS FID 227 footprint. Tile URLs, checksums, CRS, method, raster statistics, and limitations are recorded in `math_roof_dsm_r10.json`; `math_dsm_roof_height_r10.png` visualizes the broad roof plateau and a smaller high-return zone.

Within that footprint, the DSM-minus-DTM surface-height distribution is p50 **36.92 m**, p90 **40.25 m**, p95 **40.43 m**, and maximum **40.86 m** above the terrain estimate. The DTM footprint median is about 624.04 ft and nearby median is 623.81 ft; the Purdue GIS `Elevation` attribute is 623.3, although its units are undocumented. The modeled roof slab tops at 33.4 m and the current penthouse coping at 36.5 m, so the raster points to a measurable model discrepancy. The whole-footprint raster distribution does not identify which story, wall top, roof object, or penthouse surface should move. Its 5-ft cell size cannot resolve the modeled thin mast, parapet edges, or exact roof equipment; the DTM beneath the building may be interpolated. No roof or floor geometry was changed on that basis.

Indiana's 3DEP product guidance describes QL2 accuracy as a statewide standard and explicitly calls for local-area suitability checks. This pass did not have surveyed check points for MATH, and the TIFFs lack embedded vertical-unit/datum tags. Feet are corroborated by the matching local DTM and Purdue GIS `Elevation` magnitude, but the vertical datum and building-specific error were not independently surveyed. The source supports broad roof-height constraints, not a construction elevation. See the [Indiana 3DEP data products and accuracy note](https://lidar.digitalforestry.org/docs/Indiana_3DEP_Lidar_Data_Products_Data_Accuracy_and_Data_Access.pdf), [Indiana Statewide Elevation Catalog](https://registry.opendata.aws/in-elevation/), and the [GIO tile-date service](https://gisdata.in.gov/server/rest/services/Indiana_Statewide_3DEP_Lidar_Dates/MapServer).

The source inventory located two more digitized Purdue Archives records: [item 823](https://earchives.lib.purdue.edu/digital/collection/pbuildings/id/823/) is an undated black-and-white exterior photograph with no facade direction; [item 824](https://earchives.lib.purdue.edu/digital/collection/pbuildings/id/824/) is cataloged as an undated black-and-white exterior-view drawing, also without a direction. The image content was not visually inspected in this run, so neither record is used to fill north/west blank elevations or alter openings. The existing photographed facade remains the only usable direction-unspecified exterior reference.

For the interior, the public 2022 third-floor plan and 2025 Libraries article/photo continue to support room-use context and a library/core relationship, not a current measured as-built arrangement. Purdue's [Building Deputy manual](https://www.purdue.edu/operations/operations-maintenance/wp-content/uploads/sites/7/2025/12/bd-manual.pdf) says construction plans are available by facilities request and floor plans through the university's FM:S access, and warns against copying or redistributing these plans. No current as-built plan was accessed. Interior partitions, furniture positions, circulation width and stair geometry remain schematic.

Blender 5.2.3 reopened the saved Math Sciences asset. `round10_validation.json` passes: 550 direct / 593 total objects, unchanged 33.2 m shell top and R9 roof component bounds, R10 provenance annotations on the roof objects, no east sign, and no unpacked image dependencies. No master/shared files changed. The asset explicitly carries the raster evidence and the unresolved roof discrepancy, without claiming that the model's roof profile has been corrected.

No R10 self-score is claimed. R9's independent **7.8/10** remains the latest grade until a fresh independent reviewer evaluates this evidence update.

## Round eleven — inspected archive imagery and remaining evidence gaps

R10's independent score was **7.9/10**. R11 visually inspected both public Purdue eArchives image records previously recorded only as uninspected leads: [item 823, exterior photograph](https://earchives.lib.purdue.edu/digital/collection/pbuildings/id/823/) and [item 824, exterior-view drawing](https://earchives.lib.purdue.edu/digital/collection/pbuildings/id/824/). Item 823 shows an oblique corner with one largely blank masonry end wall beside a long elevation with vertically grouped windows. Item 824's undated architectural illustration shows a tall rectilinear mass, repeated vertical window bands, simpler corner bays, a glazed lower level, flat parapet, and a somewhat raised rear roof element. Both images carry the Purdue Libraries copyright notice; they remain linked by source URL rather than copied into the project.

These images now substantiate broad historical design motifs, including a blank end wall. Their original dates, compass directions, dimensional scales, and current/as-built status are unknown. They cannot safely map the depicted wall to the model's north/east/south/west views, verify present window cadence, or establish any roof elevation. No facade or roof geometry was changed.

The [Purdue Archives accession for Mathematics Library records](https://archives.lib.purdue.edu/repositories/2/accessions/2685) lists annual reports and floor plans related to the move into MATH. It is a physical 0.025-cubic-foot folder, with no restriction noted but no public scanned drawings; the dates/provenance do not establish a current as-built plan. It is now recorded as a source lead, not architectural proof. The public 2022 third-floor renovation plan and 2025 library photo remain the inspected interior references; partitions and circulation remain schematic.

The [Indiana Statewide Elevation Catalog](https://registry.opendata.aws/in-elevation/) confirms public CC0 LAS point-cloud data and the repository includes 2018 SPW/QL2 LAS tiles. The matching raw tile was not identified and analyzed in this pass. More importantly, R10's broad DSM-DTM discrepancy still cannot be assigned to the shell roof, penthouse, coping, or equipment. The archive drawing's raised roof zone is qualitative only. No roof component was moved.

`round11_validation.json` passes after reopening the unchanged R10 saved asset in Blender 5.2.3: 550 direct / 593 total objects, unchanged shell/roof/penthouse bounds, no unpacked external images, and zero R11 geometry changes. `math_source_inventory_r11.json` and `evidence_round11.json` record sources, visual observations, and limits. The master, manifest, shared indexes, and other buildings were not edited. R11 is ready for a fresh independent grade; no R11 self-score is claimed.

## Round twelve — dated and department-published facade photographs

R11's independent review scored **7.9/10**. R12 inspected a Purdue Department of Statistics image labeled “Purdue's Math Building” and a higher-resolution photo by John Feister. The photographer states the latter was taken September 26, 2009; Flickr lists an October 31, 2009 upload and all-rights-reserved status. Its 2384 × 3526 original shows a brick elevation with vertical window strips, discrete end/corner windows, a lighter lower level and a parapet/roof edge. Its EXIF DateTime says 2009-10-29, which conflicts with the photographer's capture date, and it contains no GPS. The official Statistics image has no stated capture date. The original copyrighted Flickr image was reviewed but not copied into the project.

These independent photographs strengthen the qualitative facade comparison: the saved model's vertical window groups and simpler wall/end zones match broad features visible on MATH. No camera direction maps the photographed faces to model north/east/south/west, and the official photo's capture date is also unknown. R12 therefore makes no opening or facade geometry edits. See `math_photo_inventory_r12.json` for URLs, observations and limits.

The photographs do not measure the roof. R10's 2018 DSM-DTM height conflict remains unassigned to a specific shell, penthouse, parapet or equipment component. The physical floor-plan accession from R11 remains uninspected and unscanned, and the interior remains schematic. No new measured elevation, direction-identified facade set, or current as-built interior plan was found.

Blender 5.2.3 reopened the unchanged saved asset; `round12_validation.json` passes with 550 direct / 593 total objects, unchanged shell/roof/penthouse bounds, no unpacked images and zero R12 geometry changes. `evidence_round12.json` and `source_review_round12.md` document the source work. The master and shared files were not edited. R12 is ready for a fresh independent grade; no R12 self-score is claimed.
