# Stanley Coulter Hall exterior research — in progress

Research rank **9**, stable ID `stanley_coulter_hall`, asset `modular/buildings/stanley_coulter_hall.blend`, second-pass owner **Rossen**, first-pass grade **8.1/10**, priority **87.46**. **In progress checkpoint**, October 29, 2026. Continue this building before rank 10; this is not a prepared whole-building exterior dossier, modeling revision or second-pass visual acceptance.

## Identity and footprint

The [Purdue GIS snapshot](sources/purdue_footprint.json) identifies **FID 56**, Stanley Coulter Hall, **SC**, **640 Oval Drive**, EPSG:4326. Its centroid is approximately longitude **-86.914379112**, latitude **40.426529609**, project XY **[-57.596, -96.648] m**. [Shared provenance](../../shared/location_source_provenance.json) preserves the cached source's dates/hash. Today's retrieval is not a new footprint survey, and GIS floor/elevation fields are not independently verified facade dimensions.

The [Purdue herbarium history](https://ag.purdue.edu/department/btny/herbaria/kriebel/kriebel_history.html) / [snapshot](sources/purdue_herbarium_history.html) supplies a primary institutional history lead for the 1917 building. Confirm wing/addition chronology and shared connections with adjacent Class of 1950 Lecture Hall before future modeling. The overhead shows a courtyard and differing roof zones; a solid generic rectangular roof is not an adequate representation of the observed roof plan.

## Saved and inspected sources

[Reference acquisition index](sources/reference_download_index.json), [site acquisition index](sources/site_download_index.json), [panorama index](sources/maps_download_index.json) and [metadata/access records](sources/context_download_index.json) retain URLs, outcomes, dates and SHA-256 values. Several source pages include other image tags; these are not counted as additional inspected building views.

- [Official Purdue English entrance photo](sources/purdue_english_front.jpg), from the [department page](https://www.cla.purdue.edu/academic/english/index.html) / [snapshot](sources/purdue_english.html). Actual 956×620 photograph, inspected. Photographer and exposure date unverified; no DateTime or nested DateTimeOriginal found in this derivative. A currently maintained webpage does not establish a current exposure date.
- [Purdue archival exterior image](sources/purdue_archive_exterior.jpg), item **PPBUC01117**, [source item](https://earchives.lib.purdue.edu/digital/collection/pbuildings/id/1310/). The rendered [metadata snapshot](sources/purdue_archive_metadata.txt) and [IIIF manifest](sources/purdue_archive_manifest.json) identify the original as **undated**, digitized **December 1, 2006**. Digitization is not exposure. The image visibly differs in window treatment/color from the department photo; use it for historical comparison, not present-day color matching or an assumed 1917 elevation. Credit/copyright: Purdue University Libraries, Karnes Archives and Special Collections; rights retained in the source record.
- [South frontal panorama](sources/streetview_south_front_2019.png), Google **August 2019**, resolved camera **40.4259885, -86.9143932**, panorama `edsyJrqna9EH1j_glWMayw`. Looking north from Oval Drive, far/frontal and slightly upward; central portal and upper window groups visible, outer bays largely hidden by trees. Full URL and source date in [text snapshot](sources/streetview_south_front_2019.txt).
- [Northeast context panorama](sources/streetview_northeast_context_2017.png), Google **September 2017**, resolved camera **40.4268306, -86.9135968**, panorama `Di15z1Xw13cC4PlP0iQ8QA`. Far oblique looking southwest from the Wetherill/Central Drive path; north/east context is visible, with strong sun flare and tree occlusion. This does not verify an entire rear window schedule. [Text snapshot](sources/streetview_northeast_context_2017.txt) retains the location/date. These were the first two registered camera positions; the expansion below adds six distinct north-side positions, not rotations or crops. Camera height and exact facade distances remain unknown.
- [World Imagery overhead](sources/aerial_world_imagery.png), with [export metadata](sources/aerial_export_wide.json). The larger fallback export succeeded; [initial small export response](sources/aerial_export.json) is also retained. Actual aerial acquisition date is unknown. The inspected image shows the courtyard, reddish sloping perimeter roof sections, flat gray roof areas and small rooftop volumes/penetrations, with separate neighboring buildings.
- [Purdue August 7, 2026 capital plan](https://www.purdue.edu/newsroom/2026/Q3/trustees-approve-10-year-capital-plan/) / [snapshot](sources/purdue_capital_2026.html) includes a proposed southeast-wing mechanical-system replacement. Treat it as proposed scope, not evidence of new completed roof equipment or facade changes.

A Spring 2024 School of Languages and Cultures newsletter was located in search results but its recorded PDF URL returned **404**; the failed acquisition is in the index. Its construction update has not been inspected and is not used as proof of current exterior conditions. An east-side panorama request resolved inside a corridor and was rejected rather than counted as facade coverage.

## Observed features to investigate further

The **south entrance** is framed by two round pale stone columns with ornamental capitals, a substantial rectangular stone surround/entablature and the engraved building name. Behind them is a recessed glazed entrance with an arched upper opening/transom and stepped masonry around the arch. The stair approach, pale side walls/cheeks and straight metal handrails establish depth; this must not become a flat doorway texture. Exact profiles and dimensions remain unmeasured.

The department photo shows red/brown brick with pale stone trim/bands, dark window frames and strongly reflective glazing. Upper-level window groups are much taller and more extensively glazed than the small low basement openings; some main-level openings are grouped in threes. The facade includes distinctive pale square trim blocks and a deep dark eave with repeated supports. Trees and cropped framing prevent a complete floor-by-floor count. Do not copy the archival light-colored, denser sash pattern into the present target without resolving its era.

The overhead reveals differing roof forms and an internal courtyard. Inner courtyard elevations, side/rear window rhythms, drainpipes, vents, recessed entrances and the relationship to neighboring lecture-hall structures are not yet verified. The expanded north-side sequence below resolves several former distant-view gaps; full east, west and inner-courtyard coverage remains unverified. Color observations are qualitative: warm red/brown brick, pale cream/gray stone, dark frames, variable sky reflections and a reddish roof edge; there are no calibrated material samples or reliable absolute RGB values.

## LiDAR checkpoint

The [state tile query](sources/lidar_delivery_tiles.json), [COPC metadata](sources/in2018_29951885_12.copc.metadata.json) and [crop summary](sources/lidar_crop_summary.json) accompany [portable local LAZ data](data/lidar/in2018_29951885_12.stanley_coulter_hall_clip.laz). State acquisition date **April 20, 2018**, tile `in2018_29951885_12`; the full-resolution spatial query was written as regular LAZ with COPC hierarchy removed.

The crop contains **29,106 points**, **12,722 inside the footprint**. Classes: unclassified (1) **17,655**, ground (2) **11,329**, noise (7) **122**; no building class 6. Compound CRS **NAD83(HARN) / Indiana West (ftUS) + NAVD88 height — Geoid12B (ftUS)**, horizontal EPSG:2968 / vertical EPSG:6360. XYZ use US survey feet, factor **0.30480060960121924 m/ftUS**.

Outside-footprint ground median is **622.73 ftUS**. The one-metre-eroded footprint contains **10,268 class-1 returns**, with candidate heights above that ground median of approximately **12.485 / 14.777 / 16.331 m** at p50/p90/p99. These are not measured eave/ridge heights. Trees, courtyard/footprint interpretation and different roof levels can affect them. The cloud predates later work and cannot establish current windows, carving, materials or roof services. Segment actual roof planes and refine courtyard masks before using it for future geometry.

## Expanded research checkpoint — north wing, east-side history and plans

Eight distinct Google exterior camera positions are now preserved: the original south and northeast context cameras plus six new September 2017 positions. These are historical street-level observations, not evidence of unchanged 2026 conditions. Precise camera heights and facade distances are unknown. The `192a` URL component is not a measured camera height above ground.

| Saved view | Resolved camera latitude, longitude | Observed contribution |
| --- | --- | --- |
| [Northeast near](sources/streetview_northeast_near_2017.png) / [metadata](sources/streetview_northeast_near_2017.txt) | 40.4268637, -86.9138079 | Closer oblique of north/east corner and stairwell glazing |
| [Northeast corner detail](sources/streetview_north_east_corner_detail_2017.png) / [metadata](sources/streetview_north_east_corner_detail_2017.txt) | 40.4268691, -86.9139225 | Tall stairwell glass on returns, north entrance with pale surround/steps and black rails |
| [North close](sources/streetview_north_close_2017.png) / [metadata](sources/streetview_north_close_2017.txt) | 40.4268762, -86.9140743 | Paired main windows, differing upper panels, lower stone band and basement openings |
| [North middle](sources/streetview_north_middle_2017.png) / [metadata](sources/streetview_north_middle_2017.txt) | 40.4268755, -86.9142048 | Long repeated opening sequence, deep eave, pale sill/trim, service enclosure |
| [North service](sources/streetview_north_service_2017.png) / [metadata](sources/streetview_north_service_2017.txt) | 40.4268775, -86.9143185 | Large dark basement grilles, sunken enclosure and changes toward west end |
| [Northwest context](sources/streetview_northwest_context_2017.png) / [metadata](sources/streetview_northwest_context_2017.txt) | 40.4269163, -86.9143670 | End of north wing and adjacent modern masses; does not establish west facade or connector ownership |

The north wing has two principal stories above a pale-trimmed basement. Its repeated openings usually contain two main vertical lights with a shallow upper panel/transom, rather than the large triple groups on the formal south frontage. Some upper panels are opaque or very dark; do not make every rectangle transparent glass. Near the northeast corner, tall vertically stacked stairwell glass and the rectangular entry interrupt this rhythm. Individual openings, vents and infill differ, so a universal repeated window module would be inaccurate. The dark projecting eave, repeated pale blocks under it, thin pale window surrounds, stone basement field and parallel horizontal pale bands need separate depth and material treatment.

The service views expose large horizontal basement ventilation grilles and a low sunken enclosure with brick ends, pale coping and a pale inner wall. Its exact extent, permanent equipment and ownership must be cross-checked; bicycles, movable fencing and other temporary objects are not architectural evidence. Nearby modern concrete-clad masses must remain separate context until their boundaries and any physical connections are registered.

### Historical east-side detail and color comparison

The [Interaction Garden page](https://www.mensetmanus.net/inspiration/purdue-interaction-garden/) / [saved page](sources/interaction_garden_2004_p1.html) and [second page](https://www.mensetmanus.net/inspiration/purdue-interaction-garden/page2.shtml) / [snapshot](sources/interaction_garden_2004_p2.html) publish four inspected **300×240** photos looking toward or along Stanley Coulter's east wall:

- [Westward wall detail](sources/garden_westward_2004.jpg): paired main-story glazing, basement openings, pale belt bands, corner glazing and terrace relationship.
- [Northwest oblique](sources/garden_northwest_2004.jpg): tall stacked corner glass, lower pale-framed opening and the wall return.
- [Northward along east wall](sources/garden_northward_2004.jpg): close basement stone/recesses, lower openings and the line of the wall.
- [Southward along east wall](sources/garden_southward_2004.jpg): long facade sequence, tall corner glass and pale plinth/bands; the nearby garden walls and benches are separate site features.

The pages are dated **May 1, 2004**; exact exposure dates are unverified. The site credits most photography to Purdue landscape architect **John Collier**, with an exception for two darker rain photographs by the page author; per-image attribution for those exceptions is unresolved. Keep the visible MensetManus watermark and source credits. These are dated historical comparisons, not current window proof or calibrated color charts.

Across the department front photo, historical garden pictures and 2017 north views, brick reads as warm muted red/brown, stone as pale cream/gray, eave soffits as very dark brown, and roof edges as reddish brown. Northern frames appear pale bronze/greenish under that lighting, while southern frames look dark in the department photograph. This may involve facade/date/material differences as well as lighting and reflection. Preserve that uncertainty; do not apply one uniform black frame shader or sample shadowed glass as brick color. No absolute RGB/material values have been calibrated. Pair sunlit and shaded observations of the same face in newer references before final material selection.

A [Rick McOmber Flickr photograph](https://www.flickr.com/photos/rickm15/19049161634) / [saved source page](sources/flickr_rick_2015.html) is identified by its page as taken **April 5, 2015**, uploaded **July 13, 2015**, all rights reserved. Its direct image request returned **403**. The actual image has not been inspected or counted as a usable architectural view; retain it as a source lead only.

### Purdue plans and renovation chronology

The inspected [2022 Purdue Board of Trustees packet](sources/purdue_2022_renovation_plans.pdf), [original PDF](https://www.purdue.edu/bot/meetings/past-meetings/2022/09.%20oct/pfc/University%20Hall%20Related%20Renovations.pdf), contains **14 PDF pages**. Exhibit C is specifically Stanley Coulter: **PDF pages 12–14** show basement, first and second floors. The sheet date is September 28, 2022. Plans for University Hall and Beering on earlier pages must not be attributed to Stanley Coulter.

The north arrow and southern projecting entry on the first-floor plan align with the registered south entrance photograph. The upper plans show perimeter wings and a central rectangular space marked open below; the basement drawing contains built spaces and a central circular feature beneath that area. Thus the apparent courtyard/opening must not simply be cut as a full-depth empty hole through every level. Reconcile aerial roof segmentation, actual inner elevations and each floor before future geometry. The plans also show corner stairs and a distinct northern classroom/office strip. They clarify layout; they are not dimensioned exterior elevations or proof of current sash patterns.

The packet is an approval/proposed renovation scope with shaded affected rooms, not an as-built certification. Its 17,400 GSF Stanley Coulter scope and project-wide scheduled completion cannot establish that each exterior element was changed or complete on a particular later date. The [2026 capital-plan article](sources/purdue_capital_2026.html) schedules southeast-wing HVAC work to begin **May 2028** for roughly seven months. That is future work relative to this research date; do not add future equipment or treat it as an observed 2026 alteration.

## Facade coverage and remaining work

| Area | Supported observations | Remaining evidence needed |
| --- | --- | --- |
| South formal front | Department near portal, 2019 far frontal, undated historical comparison | Both opposing corner views; unobstructed full opening count; newer detail/color photos |
| North | Seven distinct 2017 camera positions including original northeast context; long window sequence, grilles and northeast entry | Newer condition; complete registered opening schedule; service enclosure/equipment dimensions |
| East | 2017 northeast return; four low-resolution historical garden positions | Current full elevation and opposite southeast oblique; detailed sash and surface comparisons |
| West | Only partial distant context toward northwest; plan/footprint support | Actual full west facade, southwest corner, shared-boundary/connection verification |
| Inner space/roof | Overhead and three floor plans; LiDAR crop | Actual inner elevations; courtyard floor/roof levels; current roof services; elevated obliques |

**Keep this building In progress.** Resolve west and inner-courtyard coverage, seek newer east/north imagery and additional heights/distances, and produce a source-linked opening schedule before advancing rank 10. No geometry or models were changed. This expanded checkpoint is neither a prepared whole-building dossier nor a visual acceptance.
