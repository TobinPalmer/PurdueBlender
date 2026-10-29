# 3. Purdue Bell Tower: exterior research

Prepared 2026-10-28, **with coverage gaps; no model changed**. Stable ID `bell_tower`, source `modular/buildings/bell_tower.blend`, future modeling owner Rossen. Old rank 23; current first-pass grade 9.3/10. Purdue GIS identifies **BELL / FID290**, 325 Centennial Mall Drive. This freestanding tower is separate from WALC, Elliott Hall of Music and the historical Heavilon Hall tower.

Purdue's [archival collection UA116](https://archives.lib.purdue.edu/repositories/2/resources/1456) identifies a roughly 160 ft tower incorporating four earlier Heavilon bells. Its [2020 anniversary announcement](https://www.purdue.edu/newsroom/archive/releases/2020/Q4/university-to-mark-25th-birthday-of-purdue-bell-tower.html) gives October 14, 1995 dedication and red brick with limestone trim. The [historical timeline](https://collections.lib.purdue.edu/timelines/puhistorical) instead lists completion October 30 and 165 ft. Preserve that distinction: **published overall height is approximately 48.8 m, with a conflicting 50.3 m timeline figure**, not a survey-controlled dimension. Do not convert a cached GIS extrusion field into a certified total height.

## Source and viewpoint log

All files were retrieved October 28, 2026. Unless supplied below, capture dates and exact camera poses are unknown. Exposure publication is October 11, 2020; the photographs can be older. Position categories are qualitative. [Download URLs, hashes and access results](sources/download_index.json) accompany the images.

| ID | Source / reference | Height, position and distance | Use and limits |
| --- | --- | --- | --- |
| B01 | [Purdue anniversary photo essay](https://purduenews.exposure.co/happy-birthday-purdue-bell-tower), [cover](sources/purdue_cover.webp) | Ground, low upward, medium oblique | Full shaft silhouette; foliage obscures base. |
| B02 | Same essay, [belfry close](sources/purdue_belfry_close.webp) | Upward close/telephoto, two adjacent upper faces | Clock, open bell chamber, cornice and roof profile. Camera compass bearing unverified. |
| B03 | Same essay, [base](sources/purdue_base_arch.webp) | Ground, near frontal through passage | Stone joints, arch depth and paving interface. Opposite base faces still need separate close views. |
| B04 | Same essay, [plaque](sources/purdue_base_plaque.webp), credited Rebecca McElhoe | Near vertical/downward detail | Circular dedication plaque and surrounding pavers. Not another tower elevation. |
| B05 | Same essay, [snowy mall](sources/purdue_snow_mall.webp) | Ground, distant mall view | Skyline proportions; snow/trees obscure materials and base. |
| B06 | Same essay, [evening upward](sources/purdue_evening_upward.webp) | Ground upward oblique, upper tower | Different upper faces and illumination; unsuitable as daylight color calibration. |
| B07 | Same essay, [moon/context](sources/purdue_moon_context.webp), credited Mark Simons | Ground, medium/far oblique | Shaft banding and roof outline; foliage obscures lower geometry. |
| B08 | Same essay, [elevated east-southeast view](sources/purdue_elevated_ese.webp) | Elevated far, source explicitly says facing east-southeast | Tower/WALC separation and top/shaft geometry. WALC plaza is under construction; not current site paving evidence. |
| B09 | [A Hazy, Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Purdue_University_Bell_Tower.jpg), [original](sources/commons_2024.jpg) | June 23, 2024, upper-tower oblique | Roof seam and finial detail, paired faces and upper trim. Unmodified original, **A Hazy, [CC BY-SA4.0](https://creativecommons.org/licenses/by-sa/4.0/)**. Lower portion outside frame/obscured. |
| B10 | [Purdue Libraries 2017 opening image](https://blogs.lib.purdue.edu/news/2017/08/02/wilmeth-active-learning-center-open-aug-7/), [shared WALC reference](../walc/sources/purdue_2017_day.jpg) | Elevated opposite context | Independent tower/WALC spatial relationship; construction-era landscaping. |
| B11 | [Esri World Imagery](sources/aerial_world_imagery.png), [successful wider export](sources/aerial_export_wide.json) | Orthographic overhead | Orientation and footprint context. Small tower and acquisition date unknown; not fine roof-detail evidence. |

The essay also contains historical drawings/construction photographs. They were identified as historical, not counted as finished exterior references. The essay and archive text were readable through the web research service, while direct HTML requests returned HTTP403; photo URLs were retrievable. The direct anniversary-article download redirected to Purdue's homepage and is explicitly labeled in the index. That response is not an article snapshot. No authentication or private archive material was accessed.

## Architectural details to preserve

From the 2024 original B09: the upper tower has a square clock enclosure with **round Roman-numeral dials**, dark hands/rings, panel seams and projecting lower ledges. Above it is an **open bell chamber**, with slim pale columns, horizontal connecting members, capital-like steps and rounded arch openings. Bells hang visibly inside; closing this volume with opaque walls would change its silhouette. The steep pyramidal roof has dark reddish-brown panels divided by bright raised seams, a pale eave/cornice and a narrow stepped finial. Do not approximate it as a smooth cone or textured red-tile roof. Brick shaft faces have vertical recessed strips and projecting horizontal stone belts. Photograph-by-photograph material warmth varies; exact physical roof alloy and stone finish were not specified.

B03/B04 resolve details unavailable in the upper views: the base passage has deep arched soffits and heavily stepped pale masonry over darker plinths; the circular inset plaque is part of the paving under the tower. These references do not prove identical detail on every hidden face. The elevated B08 helps distinguish the upper clock/belfry height from the long brick shaft. A future detail schedule should separately record base, each shaft belt, clock box, bell chamber, roof and finial rather than scaling a generic tower primitive.

Priority items for additional verification:

- Number, diameter and orientation of all four clock dials; Roman numeral style, hand shape and dial recess depth. Use a consistent displayed time if modeling static hands, while preserving physical dial details.
- Actual arrangement of the four unequal bells, suspension members, electronic clapper components and visible interior supports. Published bell count does not resolve their three-dimensional positions.
- Every shaft recess, belt projection, clock-box ledge, column/capital profile, arch spring line and roof seam count. Hidden faces need their own references; do not invent bilateral symmetry.
- Near ground/upward views from each side, passage soffits, plinth returns, plaque diameter, access panels, lighting fittings and current adjacent paving. Landscaping remains a separate ownership decision.

Daylight B02 and B09 suggest pale warm stone, variegated red-brown brick, dark dials/bells and a dark reddish-brown roof with light seams. Compare both sunlit and shaded faces; evening lighting makes the same pale surfaces yellow. No calibrated material samples, reflectance data or physical manufacturer specification were found. Avoid baking blue sky, colored floodlighting or vegetation reflections into permanent material colors.

## GIS, aerial and LiDAR data

[Saved Purdue feature](sources/purdue_footprint.json) retains the complete FID290 WGS84 ring and attributes. [Shared provenance](../../shared/location_source_provenance.json) identifies the cached repository source, not a new survey. The footprint is a rotated quadrilateral; align its edges to campus coordinates rather than treating image borders as building axes. `NUM_LEVELS=1` is an inventory attribute, not a claim that this is a conventional one-story block. Likewise `Extrution=140` is not verified overall height.

The initial tiny-site aerial request returned zero image dimensions and no image URL. It is retained as a failed response. Widening context produced the actual [1200×1200 aerial](sources/aerial_world_imagery.png); use `aerial_export_wide.json` for its extent. Source acquisition date remains unknown.

Indiana's [LiDAR date index](https://gisdata.in.gov/server/rest/services/Indiana_Statewide_3DEP_Lidar_Dates/MapServer) selects **in2018_29951885_12**, dated **April 20, 2018**. [Query result](sources/lidar_delivery_tiles.json), [COPC metadata](sources/in2018_29951885_12.copc.metadata.json), [download requests](sources/site_download_index.json), and [crop statistics](sources/lidar_crop_summary.json) are preserved. A full-resolution spatial COPC query around the footprint produced **6,938 measured points** in the portable [LAZ clip](data/lidar/in2018_29951885_12.bell_tower_clip.laz), with **379 points inside the footprint**. Source and clip SHA256 hashes are recorded; no model was reconstructed.

- Actual compound CRS: **NAD83(HARN) / Indiana West (ftUS) + NAVD88 height, Geoid12B (ftUS)**; full WKT retained. Horizontal source EPSG2968 is embedded in a bound CRS; vertical EPSG6360. All native XYZ units are **US survey feet**, factor **0.30480060960121924 m/ftUS**.
- Classes: 4,321 unclassified (1), 2,617 ground (2), no class-6 building returns. Class 1 must not be treated as a certified building class.
- Outside-footprint ground median is **622.85 ft NAVD88**. A 1 m eroded footprint contains only **135 class-1 returns**; their heights above that local median have p50/p90/p99 **33.120 / 44.993 / 47.393 m**. Tall narrow open structures are sparsely sampled: **p99 is not the finial height**, and the median is not a floor/eave level. Missing returns are not evidence that bells, arches or fine members do not exist.
- Use this cloud to investigate shaft/top levels and orientation, after checking registration and the original point distribution. It cannot determine dial graphics, carved profiles, exact bell supports or present-day lighting. The data predates the 2024 photograph and 2026 research date.

Indiana's public elevation collection is [documented as CC0](https://registry.opendata.aws/in-elevation/). Newer statewide collection plans do not prove a newer site tile exists. Reproduction uses `tools/collect_site_evidence.py bell_tower --crop` with its listed dependencies and the actual source WKT.

## Unresolved coverage

This dossier includes ground-near, ground-far, upward detail, elevated oblique, overhead and real point data. The lower tower is partly hidden in many photographs. **A complete four-face close sequence, bell/support arrangement, base-side variations, current service/lighting details and survey-controlled overall dimensions remain unresolved.** Exact camera coordinates/heights were not supplied, and a 2024 publication/capture does not prove no subsequent change.

Before modeling, obtain a walking series around the base and upper telephoto views from opposite sides, inspect roof/finial returns and reconcile the published height conflict with a reliable dimensioned source. Research preparation does not constitute a new second-pass model, a review score, or 9.9/10 acceptance.
