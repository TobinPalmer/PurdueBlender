# A. A. Potter Engineering Center exterior research

Research rank **8**, stable ID `potter_engineering`, asset `modular/buildings/potter_engineering.blend`, second-pass owner **Rossen**. First-pass score **8.0/10**, research priority **90.00**. **Prepared with gaps**, researched October 29, 2026. This is exterior research only: no model, builder, placement or master change and no second-pass visual acceptance.

## Identity and current-versus-proposed conditions

The official [Purdue facility page](https://engineering.purdue.edu/Engr/AboutUs/Facilities/PotterEngineeringCenter) / [snapshot](sources/purdue_facility.html) identifies A. A. Potter Engineering Center, **500 Central Drive**, West Lafayette. The [Purdue GIS feature](sources/purdue_footprint.json) is **FID 864**, POTR, primary building, building number 1154, EPSG:4326. The queue uses its centroid at approximately longitude **-86.912423112**, latitude **40.427537860**, project XY **[108.294, 15.308] m**. [Cached-source provenance](../../shared/location_source_provenance.json) retains source age and hash. These coordinates are not a new survey or an entrance location. Floor/elevation/extrusion fields do not independently prove exterior dimensions.

This is the low modern brick-and-precast building immediately east of WALC, with pale flat roofs and projecting brick stair towers. WALC, MSEE, BHEE, Dudley/Lambertus and other neighboring buildings remain separate assets. Do not copy the campus Bell Tower shown on the study covers into Potter or treat a neighboring roof as its own.

Purdue's [August 7, 2026 capital-plan announcement](https://www.purdue.edu/newsroom/2026/Q3/trustees-approve-10-year-capital-plan/) / [snapshot](sources/purdue_capital_plan_2026.html) describes a potential renovation of Potter's first floor and basement, including a new main entrance. It is a planning announcement, not evidence that the new exterior has been built. Its headline rendering depicts Indianapolis, not Potter. The dated 2016/2017 studies below also contain alternative designs; keep their existing-condition material distinct from proposed glazed entrances, reskinning and plaza changes.

## Source register and inspected material

[Reference download index](sources/reference_download_index.json), [site download index](sources/site_download_index.json), [panorama capture index](sources/maps_download_index.json), [extracted-photo provenance](sources/study_photo_download_index.json) and [rejected-view records](sources/context_download_index.json) preserve URLs, dates and hashes. The [PDF keyword page index](sources/pdf_page_index.json) is a navigation aid, not a claim that every drawing or page has been interpreted.

| Source | Useful evidence and date limits |
| --- | --- |
| [Purdue exterior photograph](sources/purdue_exterior.jpg) | Actual published 500×250 image from the facility page: curved brick stair tower, blank brick return, small vertical tower openings, pale rectangular canopy on supports, stair/rails and deep precast facade. Photographer, exposure date and camera coordinates unknown. Useful identification and color cross-check, not a precision dimension source. |
| [July 2016 renovation study](sources/potter_study.pdf) | **282 PDF pages**, American Structurepoint with Applied Engineering and Blundall Associates, hosted by Purdue. Cover date verified. Inspected existing-condition pages: PDF 58 / printed 46 physical analysis; PDF 59 / printed 47 real photographs; PDF 60 / printed 48 entrance-access discussion; PDF 61 / printed 49 architectural assessment; PDF 62 / printed 50 structure; PDF 64 / printed 52 civil assessment. Conceptual renderings around PDF 38–40 are proposed, not real exterior photos. |
| [November 2017 supplemental study](sources/potter_supplemental_study.pdf) | **92 PDF pages**, titled Part 2 — Food Service Options, same lead consultant with Reitano Design Group also credited. Cover verified. A supplemental option study, not a current as-built exterior survey. The filename's 2015 project number does not date its photographs to 2015. Detailed option/drawing review remains incomplete. |
| [Terrace/panel detail](sources/study_2016_terrace_panels.jpeg) | Original embedded photo bytes extracted from PDF 59, image xref 591. Leaf-off sunlit close oblique: precast relief and tiny windows, blank brick projection, terrace walls, rails and large lower glazing. Exact camera, facade registration, height and exposure date unknown; report published July 2016. |
| [Short entrance ramp](sources/study_2016_ramp.jpeg) | Same page, xref 592: winter view of brick-sided raised ramp and recessed canopy. Its precise corner remains to be registered to the plan; it is not automatically the modern main entrance. |
| [Loading-dock detail](sources/study_2016_loading_dock.jpeg) | Same page, xref 593: low concrete canopy, open service recess, ramp, yellow bollards and lower brick. Distinct from the public corner doors. Original embedded bytes retained without image edits. |
| [Overhead imagery](sources/aerial_world_imagery.png) / [successful export parameters](sources/aerial_export_wide.json) | Esri World Imagery, exact acquisition date unknown. Shows stepped flat roofs, rooftop units/vents, two rounded stair projections and adjacent assets. [Initial small export response](sources/aerial_export.json) is not a second image. |

Study chronology and directions need care. Its physical table lists 1974 construction, while Purdue's 2026 announcement dates the opening to 1977; these may describe different milestones and are retained separately. Its printed page 48 calls the main entrance southwest, while printed page 52 calls it southeast. Do not silently use those labels as identical surveyed compass directions. Register entrances against the footprint, plans and actual camera coordinates before modeling.

## Viewpoint log and facade coverage

Five distinct resolved Street View camera positions were inspected. Heights and exact facade distances are unmeasured; near/medium/far are qualitative. The source URLs' `190a`/`192a` values are not heights above ground. Repeated rotations of one panorama count once. Full URLs, panorama IDs, dates and coordinate text snapshots accompany each image.

| Capture | Resolved camera latitude, longitude | View and limitations |
| --- | --- | --- |
| [Northeast corner entrance](sources/streetview_north_entry_2017.png), Google August 2017 | 40.4279550, -86.9120840 | Medium upward oblique of curved stair tower, dark entrance recess and canopy, stair, planting and north/east returns. Trees hide most window counts. |
| [North panels/service area](sources/streetview_north_panels_service_2017.png), Google August 2017 | 40.4279291, -86.9123946 | Closer frontal/upward view of the deep precast grid and small horizontal openings. Trees and construction lift conceal several bays; temporary machinery is not architecture. |
| [Southeast corner entrance](sources/streetview_southeast_entry_2017.png), Google August 2017 | 40.4272125, -86.9120099 | Opposing upward oblique: curved brick tower, vertical slot windows, projecting canopy, broad steps/handrails and east-side panel rhythm. Fencing and nearby site work are temporary 2017 conditions. |
| [Southern distant frontage](sources/streetview_south_distant_2017.png), Google September 2017 | 40.4268254, -86.9123418 | Far, nearly frontal silhouette across the plaza; brick masses, curved tower and pale central facade. Trees obscure much of the window field and lower entrance/terrace. |
| [Northwest loading area](sources/streetview_northwest_loading_2017.png), Google August 2017 | 40.4278857, -86.9125231 | Near oblique at opposite end of north face: small windows/AC insert, brick service projection, low canopy/columns and red sloping metal enclosure below the panel wall. Vehicles, bins and nearby lifts are not permanent building features. |

Published photo and study details add near, leaf-off and winter viewpoints; overhead imagery supplies elevated roof context. Their camera stations are unknown, so the photo count is not a claim of independently measured positions. No current elevated oblique from the west/rear has been acquired. Two nearby panorama searches resolved inside WALC and were rejected rather than counted as Potter's exterior.

**Coverage:** north and east are partially observed in registered obliques; the south has a distant view and a nearer southeast return; terrace/panel and ramp photos provide additional side detail whose exact compass registration remains unresolved. Whole west-face coverage and current post-2017 openings remain incomplete. Keep these gaps visible rather than filling unseen areas with a repeated generic grid.

## Features that determine the exterior

**Massing and stair projections.** The overhead and opposing corner views show a largely rectangular low-rise block with **two rounded projecting brick stair towers**, not one cylindrical ornament pasted on a flat box. Their tall blank walls, convex outer corners, narrow vertical slot openings and adjoining straight brick returns strongly shape the silhouette. Other brick projections/returns are rectilinear; do not make every corner round. Roof planes step around taller central volumes rather than forming one featureless slab.

**Precast grid and small windows.** The pale facade panels have substantial depth: raised vertical edges, horizontal projections and deeply recessed small dark window slots/openings. The close study photo reveals shadows and surface planes that a flat texture cannot reproduce. Many apparent large grid cells contain mostly solid panel, with a much smaller horizontal window; do not turn the whole cell into glass. The study reports a nominal **5 ft 4 in panel module** and a projecting window overhang. Treat those as dated report dimensions to check against drawings/current conditions, not a fresh survey or permission to scale the whole model from one photograph.

The north close view shows repeated narrow panes, deep sill/hood relationships and at least one differing AC/louver insert. Tree occlusion prevents a trustworthy complete bay count. The lower level alternates brick piers and taller dark glazing/entry recesses, while the broad blank brick zones and stair-tower slots have a completely different pattern. A single repeated opening grid across all faces would lose the building's identity.

**Entrances and grade.** Corner entrances sit in dark recesses under pale rectangular canopies with paneled fascia and supports. Broad concrete steps, landings, straight metal rails, brick terrace/retaining walls and short ramps are part of the visible approach. The study's main-floor/grade discussion supports documenting the raised entrances, but exact current heights and which entrance is today's main entry require confirmation. Retain the depth beneath canopies and behind supports; do not flatten the portal into a painted rectangle. The loading dock has its own lower canopy, open service bay, ramp/rails and bollards; it differs from public entrances.

The northwest 2017 reference shows a **red sloped metal enclosure** under the precast/window wall. Record it as a dated service-side feature, not a red tile roof across the building. Its function and present permanence remain unverified. Construction fences, lifts, dumpsters, cars and work materials in the 2017 views are excluded from the permanent exterior checklist.

**Roof.** The actual overhead shows pale roof membrane, multiple height/plan changes, raised central volumes and grouped vents/equipment. Keep the rounded tower tops distinct from adjacent straight parapets and canopy roofs. Separate Potter roof data from WALC's red perimeter roof to the west and the large dark/white roofs of adjacent buildings. The small overhead equipment needs higher-resolution dated views or point-cloud segmentation before exact placement/type is accepted.

## Material and color matching

Compare the Purdue photo, the 2016-study sunlit/leaf-off photo, overcast 2017 street views and overhead. Consistent material groups are reddish/brown brick with fine pale joints, **warm gray/cream precast**, dark recessed glazing, pale canopy fascia, gray concrete paving/stairs and dark metal handrails. The panels appear greener/cooler in the overcast street images and lighter in sun; neither appearance is a calibrated absolute paint color. Brick shade changes with exposure and reflection. Preserve panel joints, relief, edge thickness and canopy/brick boundaries separately so shadows arise from geometry.

No calibrated material samples, measured roughness or reliable absolute sRGB values were acquired. Avoid converting facade shade into a permanent dark base color or painting all window slots opaque blue. Roof membrane, vents, doors, rails, brick and precast require separate materials. Conceptual study renderings are excluded from real-material matching.

## Footprint, elevation data and limits

The [tile query](sources/lidar_delivery_tiles.json), [COPC metadata](sources/in2018_30001885_12.copc.metadata.json) and [crop summary](sources/lidar_crop_summary.json) accompany [local LAZ data](data/lidar/in2018_30001885_12.potter_engineering_clip.laz). State acquisition date: **April 20, 2018**, tile `in2018_30001885_12`. The spatial query was downloaded at full resolution and written as regular LAZ with COPC hierarchy removed; it is source data, not a new building model.

The crop contains **43,017 points**, with **17,210 inside the footprint**. Classes: unclassified (1) **28,259**, ground (2) **14,630**, noise (7) **128**. No building class 6 is present. Compound CRS: **NAD83(HARN) / Indiana West (ftUS) + NAVD88 height — Geoid12B (ftUS)**, horizontal EPSG:2968 / vertical EPSG:6360. Native XYZ use **US survey feet**, factor **0.30480060960121924 m/ftUS**.

Outside-footprint ground median is **622.11 ftUS**. In the one-metre-eroded footprint, **14,429 class-1 returns** have candidate heights above that local median of approximately **13.414 / 18.294 / 18.782 m** at p50/p90/p99. These are not measured eave, roof or equipment heights. Class 1 can include trees/nonroof returns; distinct roof levels, grade slope, internal structures and footprint selection affect the distribution. The 2018 cloud does not establish current window positions, panel relief, materials or later equipment changes.

## Remaining evidence and future modeling checks

- Seek current photos of all faces, especially the whole west facade, loading dock, exact entrance/ramp arrangement and upper roof/equipment from elevated obliques. Move along facades at varied distances/heights; current registered street evidence here is from 2017.
- Register the study's terrace/ramp photographs to footprint corners and resolve its conflicting main-entrance direction labels. Record exposure dates where obtainable, keeping 2016/2017 study conditions separate from a present target.
- Count every panel/window bay per floor and face, including AC/louver inserts, blank cells, ground-level glass and stair slots. Measure or estimate relief profiles transparently before constructing them.
- Inspect relevant original/existing plan and facade drawings in the full studies, and compare dated real photos with any 2026 renovation changes. Proposed options and the capital plan must not be treated as completed geometry.
- Resolve ownership of site terraces, ramps, tunnel roofs and neighboring connections; preserve existing campus placement and stable asset identity. Later modeling requires matched renders and the separate independent visual reviewer specified by AGENT.md. No model grade or acceptance is implied by this dossier.

## Focused depth pass — October 29, 2026

This pass reinspected the north panel/service, southeast entry, northwest loading and leaf-off terrace photographs, plus the actual 2016 study's architectural/structural assessment text on **PDF pages 61–62 / printed pages 49–50**. It adds useful dimensions and an opening-family schedule before advancing; it does not establish a current full facade count or approve geometry.

### Dated dimensional constraints from the original study

PDF page 61 describes **5 ft 4 in-wide precast panels**, windows of about **5.4 square feet each**, and a **1 ft 4 in precast overhang above each small window**. Conventional imperial-to-metric conversions are **1.6256 m panel width**, approximately **0.5017 m² window area**, and **0.4064 m overhang**. These are dated report constraints, not a new measurement, an exact window width/height, or the US-survey-foot coordinates of the state LiDAR. Do not derive both window dimensions from the area alone.

The same page describes **seven large windows along the first story of the south face** as an exception to the small-panel openings. Treat seven as a **2016 report count**, to be reconciled with current imagery, not evidence that every face has seven bays. It also approximates the overall building as a **160 ft square** (about **48.77 m**); that is a coarse body/planning description, not exact extents including towers and canopies.

PDF page 62 discusses **four stair shafts** and the structural system; this does not mean four identical rounded exterior towers. The real exterior evidence distinguishes the rounded projections from rectilinear brick volumes. The report's shear-wall interpretation is qualified, and structural text is not a direct facade survey. Basement/mezzanine descriptions also must not be turned into extra repeating exterior floors without checking the actual grade/openings.

### Opening and component schedule

| Zone / family | Supported arrangement and geometry | Evidence and unresolved parts |
| --- | --- | --- |
| P / repetitive precast fields | Narrow modules with deep vertical returns, horizontal projections and small recessed horizontal glazing; much of each cell is solid | North close view and terrace photo, study page 61. Use nominal module/overhang as dated constraints; full row/module counts on each face remain obscured. |
| P-X / exceptions | At least one AC/louver insert interrupts the small-opening pattern near the service end | Northwest view shows a projecting unit in a window opening; do not repeat it in every module or infer it remains today. |
| S-G1–G7 / south first-story group | Seven larger openings reported along the lower south facade, contrasting with the tiny upper-panel openings | 2016 report count, partly supported by terrace-level photographs; exact current seven-opening run and widths need registration. |
| NE-T / rounded stair projection | Convex brick outer wall, straight brick return, sparse narrow vertical slot openings and a separate canopy/entry recess | North-entry photo plus overhead. Preserve curved-to-straight transitions and roof outline; complete slot count unresolved. |
| SE-T / opposing stair projection | Rounded brick outer wall with **two plainly visible narrow slots above the canopy** in the 2017 southeast view | This is a visible span, not the total slots on all tower faces. Ground/service openings beneath/around canopy are partly concealed. |
| D-NE / D-SE public corner entries | Dark recessed door planes beneath pale rectangular projecting canopies with patterned fascia/supports; broad stair/landing and rail approaches | Opposing corner sources reveal depth and different grade conditions. Actual leaf/transom pattern and current accessible approach need sharper recent evidence. |
| NW-L / loading recess | Separate low canopy and deep service opening with yellow protective bollards/rails, lower brick and ramp/dock levels | Northwest view and embedded loading photo agree. Temporary bins, vehicles, lift and fencing do not define architecture. |
| NW-R / red sloped enclosure | Red corrugated/sloped metal element below the precast wall beside loading | Strongly visible in 2017 and the study photo. Exact function/permanence/current presence unresolved; do not call it the building's roof or confidently label equipment. |
| W / whole west face | Inventory/overhead outline and partial terrace/service context only | A complete current opening/panel schedule is still unavailable; do not substitute an east or north repeat. |

### Depth, roof and material construction brief

Build no geometry during this phase. When later authorized, establish the main body and separate rounded/rectilinear brick projections from the footprint; register public entries and loading at their own grades; then lay out precast fields as deep solid modules with small glass openings. A flat gray grid or fully glazed cell pattern would be wrong even if its bay spacing matched. Keep the seven larger south openings as a distinct family pending current verification. Fit canopies, lower brick/glazing, retaining walls, steps/ramps, rails and stair slots separately, with site ownership checked.

The roof has several flat membrane levels/raised volumes, not one featureless slab; preserve tower-top and canopy outlines separately. Current equipment placement needs newer overhead/elevated evidence and roof-specific point selection. Neighboring WALC's red roofs and older brick academic wings must not enter Potter's roof/asset boundary.

The sunlit terrace study shows warm cream precast and red/brown brick; the overcast 2017 view makes the precast greener/darker. Both show recessed glass nearly black in shade, but this is not an opaque black-glass specification. Use distinct materials for panel faces/returns, fine joints, brick/mortar, dark metal, reflective glazing, canopy and roof membrane. No calibrated color/roughness or manufacturer sample was obtained. Deep geometry should create its own shadows rather than painting them permanently onto panels.

Unresolved follow-ups remain current full west and post-2017 facades, complete module/opening counts, source registration of the report's conflicting main-entrance directions, precise profiles and roof services. The 2026 capital-plan new entrance is future/proposed scope, not permission to replace the observed entrances now. **Advance to rank 9, Stanley Coulter**, retaining those targeted gaps.
