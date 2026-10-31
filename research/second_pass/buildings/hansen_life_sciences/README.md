# Arthur G. Hansen Life Sciences Research Building — exterior second pass (#65)

**Status:** exterior research brief prepared with major face, opening, height and material gaps retained; provisional. **Phase:** research only. No Blender asset, builder, placement or master scene was changed.

## Identity, footprint and reference condition

Purdue BuildingShapes feature **FID 237** names Arthur G. Hansen Life Sciences Research Building (HANS), address **201 S University Street**. The fresh Oct. 30, 2026 EPSG:4326 query is retained at `sources/purdue_gis_fid237_2026-10-30_4326.json`; it has 26 unique ring vertices. Using the repository's approximate local-campus conversion, the ring bounds are about **59.78 × 46.05 m**, elongated east–west. These are GIS outline dimensions, not a surveyed wall or roof perimeter. The prior asset audit reports its slab reproduces this exact footprint to numerical precision; that is a consistency check against the same GIS source, not independent evidence of the building's measured size. GIS `Shape__Area=3680.15` does not agree with the ring-derived area (about 2,129 m²); do not use the field to scale the building. No matching Hansen OSM building way was found in the retained nearby OSM query; adjacent named building ways help separate context but do not verify the HANS outline.

The intended visual condition is current exterior appearance, informed by available 2018 and 2023 overhead imagery and archival exterior photos. Purdue's official historic-building database calls the facility four stories and gives dates 1983–present; a Purdue for Life history says it was completed in 1984 and renamed Hansen in 1989. These dates conflict slightly and the source page itself was available only as a public record/searchable page. The archival Purdue 2013 Building Emergency Plan is indexed as describing five occupied floors (basement plus levels 1–4), but its direct PDF URL returned 404. GIS fields `Level_=4`, `NUM_LEVELS=6`, `CountOfFLO=6`, `Elevation=619.5`, `Extrution=60`, `R=67`, `B=-13`, `F02=15`, `F03=30`, and `F04=45` are undocumented and conflict in count/meaning. The values look plausibly foot-based when compared with nearby ground and roof-surface data, but units, datum and field definitions remain unverified. Do not silently convert these into floor heights or a roof elevation.

## Viewpoint and source register

No mapped, inspectable all-side Street View walkaround was obtained for this pass. The two retained photographs are archive/event images with unknown camera coordinates and compass headings. Their similar brick/window/core composition may show the same long facade family; they are not independent face coverage. The north-up orthophotos are overhead sources, not elevations.

| View ID | Source and inspected evidence | Limits |
|---|---|---|
| HANS-ARCH-00s | Purdue Libraries eArchives, item 1116, “Hansen Hall,” assigned decade 2000s, original date undated; source extent 1 color photograph, 10×15 cm. Broad external oblique: red/pink brick wall, two tall dark vertical tower/core forms, inset horizontal dark window bands, recessed/garden-level facade, path and mature planting. Image retained as `sources/purdue_earchives_hansen_hall_2000s.jpg`; record and download links are in its JSON. | Camera side, heading, exact date and scale unknown. Trees conceal lower-left and right portions. Historical condition; not a current elevation drawing. |
| HANS-EVT-22 | Official Purdue Events location page at 201 S University St; user-submitted image was posted 2022-05-29, but image exposure date is not stated. Low-resolution 478×320 photo: pale red/pink brick, narrow dark horizontal window strips, tall dark solid vertical core/tower, recessed glazed ground-level entrance. Retained as `sources/purdue_hansen_event_photo_2022.jpg`. | Unknown station, heading and capture date; foreground tree hides the right run. User photo, not measured or authoritative architecture. Likely same facade family as HANS-ARCH-00s, so do not count as a second elevation. |
| HANS-ORT-18 | Indiana 2018 orthophoto crop, north-up, 1,600×1,600 px; request and bounds in `sources/indiana_2018_ortho_hansen_request.json`. Shows connected, low-slope roof masses and rooftop plant arrays in campus context. | Soft pixels; roof plan only. Equipment counts, parapet heights and facade cannot be measured. |
| HANS-ORT-23 | Indiana Current Imagery service crop, north-up, 1,600×1,600 px. Retained in `sources/indiana_current_ortho_hansen_1600.jpg`; corrected tile-footprint query metadata is in `sources/indiana_current_imagery_footprints_hansen_2026-10-30.json`. Tile `in2023_29971882_06`, Tippecanoe County, imagery year 2023, 6-inch pixel. Roof arrays and connected plan masses are more legible than in 2018. | The service is an annual imagery collection; tile metadata identifies 2023 source imagery, not the Oct. 30, 2026 retrieval date. Overhead, no wall elevations. |
| HANS-GIS-237 | Fresh official BuildingShapes feature query and layer metadata in `sources/purdue_gis_fid237_2026-10-30_4326.json` and `sources/purdue_gis_layer0_2026-10-30.json`. Identity, address, ring and raw attribute conflict. | Mapping polygon is not a survey; `Shape__Area` conflicts with its vertices and vertical fields are undocumented. |
| HANS-LIDAR-18 | Indiana DNR/USGS 3DEP 2018 COPC tile, targeted crop `sources/indiana_2018_copc_hansen_12m_buffer.las` plus method/statistics JSON. Quantitative surface constraint below. | No class-6 building returns. Unclassified points may be trees/equipment and are not a roof-plane fit. |
| HANS-CTX-26 | Purdue official 2026 campus map labels HANS in F9; retained PDF. Context and identity only. | Not a measured plan or elevation. |

## Face and opening schedule

The public images do not permit a compass-registered face schedule. Treat the following as **one photo-relative facade family**, not assigned to north/south/east/west. Read each photograph left-to-right only; no hidden symmetry or total opening count is inferred.

| Zone | Observed relationship | Confidence and unknowns |
|---|---|---|
| HANS-ARCH-00s, upper wall | Repeated horizontal dark-glazed window bands form narrow slots within red/pink brick wall zones. Two taller, darker vertical core/tower masses interrupt or frame the banded wall. | General pattern is clear in the broad oblique, but perspective, trees and resolution obscure bay count, exact band spacing, sash divisions, heads/sills and tower-wall junctions. Do not convert each visible dark strip into an exact window count. |
| HANS-EVT-22, upper wall | Similar narrow horizontal dark bands against pale red brick with a tall, mostly blank dark vertical core; relationship reinforces the facade family. | A small fraction of the wall is visible; image does not resolve repeated bays or establish a different face. |
| Both views, grade | Recessed glazed/entry-like ground level sits below the heavier upper wall; planting screens parts of the base. | Door count, exact opening sequence, level transition, base construction, canopy, stairs/ramps and accessible entry layout are not established. |
| Other long face, both ends, corners and service zones | No inspectable orthogonal evidence retained. | Unknown. Do not mirror the visible facade or assume blank ends. |

**Coverage result:** one likely facade family is documented by two unregistered, possibly same-side photographs; overhead evidence constrains plan only. The opposite long wall, both short ends, all corner returns, entrances/service doors, roof edge and current detailed condition remain unobserved. The computer-use browser helper could not launch Edge in this session and the mapped Google Street View inspection route did not yield usable imagery. The official Archives catalog points to a “Life Science Research Building Sketch, Unknown Date” (UA154, Series 1, Sub-Series 6, Item 7), but its record returned 403. These are access gaps, not proof that the material does not exist.

## Roof, massing and vertical constraints

FID237 is a broad east–west, multi-part plan. In the 2018 and 2023 north-up crops, connected roof areas read as a low-slope system with multiple mechanical arrays and local offsets; the south/upper image edge is not evidence of a particular facade. Do not copy each aerial texture mark as a unit or assign undocumented wings. The images do not distinguish parapet from wall edge at all sides, show roof levels reliably, or establish exact plant count, dimensions, screens, vents, drains, penthouse joints or roof materials.

A targeted COPC query used the fresh GIS polygon transformed from EPSG:4326 to **EPSG:2968, NAD83(HARN) / Indiana West (ftUS)**; source z is **NAVD88 height minus Geoid12B (ftUS)**. The query covered the polygon plus 12 m, at 0.5 ftUS source resolution. The retained LAS crop has 27,878 points. Within the GIS polygon eroded by 3 m, 7,268 class-1 returns have z median **682.01 ftUS**, p95 **689.74 ftUS**, p99 **696.63 ftUS**. In a 5 m exterior ring, 2,903 class-2 ground returns have median **620.45 ftUS**. Subtracting that ground median yields **18.764 m**, **21.120 m**, and **23.220 m** at the class-1 median, p95 and p99 respectively. There are zero class-6 returns inside the polygon. These are unclassified surface-height distributions, not measured roof/eave/ridge heights; trees and equipment can raise the upper tail. The numerical proximity of `Elevation=619.5` to the ground distribution and `R=67` to a plausible upper-wall/roof elevation is only a feet-based hypothesis, not a verified decoding of GIS attributes.

The earlier asset audit reports roof deck z=17.5 m, penthouse/parapet z=20.572 m and exhaust stacks z=24.147 m. These asset dimensions have not been independently established and must not be used as source evidence. The broad 2018 LiDAR distribution neither validates nor disproves each modeled roof component. No elevation, section, survey, floor datum or verified vertical control was obtained.

## Materials and signature elements

| Element | Photo-supported appearance | Limits |
|---|---|---|
| Main wall | Red/pink brick or brick-like masonry, visible in the archive and Purdue event photos. | Bond, mortar, module, joint depth, texture and exact color are unresolved; low resolution and exposure affect color. |
| Vertical cores/towers | Tall dark, relatively blank vertical masses contrasted against the brick banded wall. | Material could be dark masonry, metal/glass or shadowed recess; edges/profiles and whether both are attached towers or wall piers require closer current views. |
| Window bands | Narrow recessed horizontal strips of dark glazing. | Frame, mullion, operable sash, glazing reflectance, reveals and exact number/widths unresolved. |
| Ground level | Recessed glazed/entry-like area under the upper brick wall. | Glazing and support arrangement, entrances, signs, stairs/ramps and loading/service locations unknown. |
| Roof | Low-slope connected roof with visible rooftop arrays in overhead sources. | Covering, parapet/coping, screens, plant types, equipment count and current condition unknown. |
| Site | Path and mature landscape in archive photograph; foreground tree in event photo. | Keep vegetation/path distinct from building; no exact tree or site-item placement inferred. |

These are image appearances rather than verified products, calibrated colors or specifications. No full-resolution, close, current material view was found.

## Evidence-led exterior brief and conflicts

Preserve the official east–west GIS plan as a placement/outline constraint with the 59.78 × 46.05 m ring bounds clearly labeled as GIS-derived. The available facade evidence describes a substantial brick upper wall organized around narrow horizontal dark window bands and tall dark vertical core/tower forms; the grade line is recessed and partly glazed. Keep these elements as one photo-relative family until a mapped source registers its compass face. Overhead imagery supports a connected low-slope roof with multiple rooftop plant groups. There is no evidence for exact four-face opening schedules, exact roof segmentation/equipment counts, vertical datums or finish specification. The historic photo does not establish today's condition; 2023 orthophoto is the latest retained overhead source.

**Discrepancy checklist against prior audit/asset records:**

- The 26-vertex official GIS shape remains the strongest plan reference, but exact agreement with the prior structural slab is not independent survey validation.
- Ring-derived area (about 2,129 m²) conflicts with GIS `Shape__Area=3680.15`; prefer the returned vertices for outline calculations and retain the attribute conflict.
- Historic sources describe four stories or five occupied floors with basement plus levels 1–4; GIS carries six-count fields. Treat floor count above grade and field semantics as unresolved.
- GIS elevation/vertical fields appear plausibly feet-based against the LiDAR distribution, but units, datum and definitions are unverified.
- Prior asset roof, parapet/penthouse and stack heights are illustrative pending elevations or survey; LiDAR class 1 is not building-only evidence.
- Existing detailed facade treatment has no inspected orthogonal current sources behind it in this pass; it must be checked against full-face photos/plans before use as factual evidence.
- 1983–present and 1984 completion records differ; 1989 renaming is separately reported. Do not conflate naming with construction.

## Specific gap and conflict register

| Priority / affected feature | Why current evidence is inadequate / tried | Evidence needed | Effect on accuracy |
|---|---|---|---|
| High — opposite long facade, ends, corners and face identity | Two archive/event images have unknown stations/headings and may show the same facade family; Street View attempt yielded no usable mapped coverage. | Mapped current daylight panorama positions with rotations along both long sides and ends; architect elevations if available. | Cannot place the observed opening/core pattern on a cardinal face or model the remaining major elevations. |
| High — floor/bay and opening schedule on all faces | Existing photos are distant and low-resolution; no facade drawing obtained; indexed BEP PDF is currently 404. | Full-resolution orthogonal photos, 2013 BEP copy, original floor/elevation drawings, or facilities plans. | Window/door counts, floor transitions and bays cannot be placed faithfully. |
| High — vertical levels and roof silhouette | 2018 COPC has no class-6 building returns; class-1 includes possible trees/equipment; roof images are plan-only. | Datum-tied survey, measured elevation/section, reliable building-class lidar or scaled plans. | Floor heights, roof edge, penthouse/tower profiles and parapet elevations remain unsupported. |
| High — dark cores/towers and facade joints | Distant images show dark forms but not material, section, offsets, top/bottom transitions or attachment. | Close current corner/oblique photographs and exterior details/elevations. | Signature massing and shadows may be substantially wrong if treated as simple flat dark strips. |
| Medium — roof plant and low-slope segmentation | Orthophotos show arrays but no verified unit identity, boundaries or precise roof level. | Current elevated roof photography, facilities roof plan or mechanical/site drawings. | Roof silhouette, screens, equipment grouping and roof material remain approximate. |
| Medium — material and color | Only two low-resolution historical/user images; no close current source or specification inspected. | Current daylight close-ups, facilities finish schedule or construction records. | Brick, core, frame, glazing and roof finish distinctions remain provisional. |
| Medium — footprint and GIS attributes | Ring and `Shape__Area` disagree; nearby OSM does not contain a target HANS footprint. | Authoritative GIS schema/metadata and surveyed site/as-built plan. | Outline bounds are useful but exact wall line, projections and vertical attribute interpretation are uncertain. |
| Medium — archive sketch and building chronology | UA154 item7 page returned 403; archive/entity and public histories differ by roughly one year. | Obtain the sketch through Purdue Archives; verify completion from dated project or dedication records. | Archive may resolve the massing and date conflict; current brief retains both reported dates. |

## Source package

`source_manifest.json` inventories retained source files with SHA-256, provider, original URL or retrieval lead, source/retrieval date, role and limitations. Web tiles and photographs are preserved unaltered where obtainable. The archive item's original photo is assigned only a decade; the Purdue Events page's 2022 date is its post date, not verified exposure. Archive sketch and emergency-plan direct retrievals failed and are logged as leads, not inspected evidence. Research only; no model, builder, placement or master scene was edited.
