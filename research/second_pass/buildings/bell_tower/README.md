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

## Focused depth pass — October 29, 2026

This bounded pass prioritizes the tower's actual open structure and small distinctive details rather than collecting more distant skyline duplicates. It then advances to Wetherill with unresolved four-face coverage retained. No tower geometry or score changed.

**B12 — [Four-bell close photograph](sources/alumnus_four_bells.jpg)**, 500×500, credited **Charles Jischke**, from [Purdue Alumnus, Object Permanence, item 63](https://www.purduealumnus.org/object-permanence/features/8/). Actual image downloaded and inspected. The article was readable through web research, while direct HTML retrieval returned 406; that failed request is retained in the [acquisition index](sources/reference_download_index.json). Exposure date and camera bearing/height are unknown. Photographer/publication rights remain; no open license is inferred.

This close view resolves four unequal suspended bells: a high central bell, a lower central bell, a smaller partly cropped bell at image left, and a large partly cropped bell at right. These are **image-relative positions**, not a registered compass layout or a certified assignment of bell weights. Cast raised inscription bands, rings at the shoulder, flared lips, dark hollow mouths, mounting heads and clapper hardware are visibly significant. Metal surfaces are dark bronze/green-gray with localized warm highlights and patina, rather than uniform black or polished gold. The upper suspension frame and pale horizontal supporting members are visible. Do not fabricate four identical bells on a single horizontal plane. A second opposite bearing is still needed to locate every suspension in plan.

The publication lists unequal weights of **1,200, 600, 300 and 200 lb**; those are not measured dimensions or sufficient to compute diameter by cube-root scaling. Do not put a working pendulum clock in this tower based on the same article's separate next entry: the historic mechanism is displayed in ME's Gatewood atrium, a different asset.

**B13 — [Purdue University Public Art guide](sources/purdue_public_art_guide.pdf)**, [source PDF](https://assets.simpleviewinc.com/simpleview/image/upload/v1/clients/westlafayettein/Public_Art_Size_d30f272d-3e3b-48dd-b406-7917beaaa9b6.pdf). PDF page **7** was rendered and inspected. Its Bell Tower entry credits **Sasaki Associates and Scholer Corporation**, shows a small full-height context image and locates the tower on Centennial Mall Drive. It does not provide construction elevations, a publication/capture year, or fine architectural dimensions. The guide's thumbnail adds limited silhouette context and is not a new high-detail facade survey.

### Component and opening schedule

Unlike an occupied hall, this tower needs a vertical component schedule rather than an invented story/window grid. B02, B03, B09 and B12 were inspected together for this pass. Label faces by registered site orientation in future work; the present close references do not reliably supply compass bearings for every face.

| Zone, bottom to top | Observed assembly/openings | Detail and source constraint |
| --- | --- | --- |
| Ground and plaque | Paved walk-through passage; circular bronze plaque inset beneath the tower | B03/B04 show paving joints, plaque and nearby utility/grille covers. The buried capsule is not visible exterior geometry. Landscape paving ownership remains separate. |
| Base plinths | Rougher dark-gray tapered plinths with pale stepped caps; pale rusticated masonry above | B03 shows projecting horizontal courses and weathering streaks. Keep taper, joint recesses and surface scale; do not make the base four plain white cubes. Hidden base faces are not independently verified. |
| Base arch/passage | Deep rounded masonry opening with visible soffit and an opposing opening through the tower | B03 establishes real passage depth. Record visible arch profile/spring line and transverse returns; do not fill with glazing or assume every concealed face has identical fittings. |
| Brick shaft | Long brick shaft, inset vertical fields and repeated projecting pale horizontal belts | B01/B07/B09 support recess/ledge depth and red-brown brick. These recessed fields are not conventional glazed windows. Complete belt/recess count from foot to clock box is not yet resolved in one unobstructed source. |
| Clock enclosure | Square pale panel-clad box with round dials on the photographed adjacent faces, panel joints, projecting bottom ledges and small recessed rectangular fields below dials | B02/B09 show the rim, dark hands, Roman numerals and seams. Determine remaining faces independently. Do not replace the small below-dial fields with arbitrary windows or vents; their exact function is not established. |
| Belfry lower supports | Open chamber, slender **square/rectangular** pale posts, stepped capitals/blocks and horizontal cross members | B02/B09 resolve the structural void and corner/inner members. Preserve through-views and overlapping frame depths; these are not generic round portico columns. |
| Bells and hangers | Four unequal bells at differing apparent heights, mounting hardware and visible clappers | B12 provides close surface and suspension detail. Exact 3D offsets, frame dimensions and some hidden hardware remain unresolved. |
| Belfry upper arches | Rounded open arches below a deep pale cornice/eave | B02/B09 show adjacent returns. Model arch thickness and soffit depth; no opaque wall or full glass fill across the chamber. |
| Roof and finial | Steep four-sided pyramidal roof, narrow light raised seam ribs, dark red/brown fields, bright corner edges, stepped narrow finial | B02/B09; seam/profile repetition must follow photographed roof faces, not a textured cone or ordinary campus tile hip. Exact seam count on all slopes, pitch, alloy/finish and finial dimensions remain unmeasured. |

For dial graphics, [Purdue Alumnus' clock discussion](https://www.purduealumnus.org/campus-myths-under-the-microscopes/features/) identifies **IIII** in place of IV; the actual photographed dials must still govern numeral shape, placement, rings and hands. The discussion's folklore is not a construction specification. Direct article HTML returned 406 and no saved page is claimed. Use a coherent chosen time when modeling later; photographed hand positions vary between exposures and do not imply different dial geometry.

### Dimensions, materials and construction brief

The [derived footprint notes](footprint_measurement_notes.json) preserve the input hash, method and individual exterior-ring segment lengths in metres. The raw Purdue ring was transformed from EPSG:4326 to NAD83 / UTM zone 16N (EPSG:26916) before measuring segments. These are inventory-outline constraints, not a new ground survey, clear passage dimensions, roof overhang or clock diameter. The previously recorded 160/165 ft total-height conflict remains unresolved. Sparse airborne returns and approximate published heights must not be combined into false millimetre precision.

When building is authorized: register the tower's actual plan axes; establish plinth, arch spring/crown, brick belts, clock box, belfry and roof/finial as separate vertical landmarks; preserve taper, projection and voids; lay out the clock panels and actual numeral graphics; fit the nonidentical bell arrangement from multiple bearings. Keep tower, neighboring WALC and Elliott/site installations separate. Use daylight brick/limestone and B12's bell patina observations, separating illumination, weathering and glass/dial effects. No calibrated color/roughness measurements or surveyed vertical landmark levels were found.

Remaining priority gaps: opposite-side bell suspension view, four-face base/access/lighting sequence, complete shaft belt/recess count, measured dial/arch/finial dimensions and reliable total-height reconciliation. Focused searches of architect names and institutional references produced attribution and photographs, not a dimensioned construction set. **Advance to rank 4, Wetherill**, retaining these explicit limits rather than repeatedly retrying blocked publication pages.
