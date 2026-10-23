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

The round-five reviewer found that the east gold lettering was still present: the earlier cleanup line in `finish_math.py` contained literal `\\n` escapes after a comment marker and therefore never executed. Round six removes the actual `MATH_Signage_East` object from the saved standalone blend. `verify_sign_round6.log` records reopening the file and confirms `sign_present: false`, the export collection still exists, with 592 direct objects. The four-elevation render set was refreshed from the saved file; `exterior_east_after.png` visibly has no gold lettering. GIS placement and footprint were not modified. This is a focused repair, not a new independent score; round-five review remains 6.9/10 until another reviewer evaluates it.
