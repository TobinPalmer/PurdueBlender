# Purdue Memorial Union — refinement record (round 4)

## Asset and change scope

- Modular asset: `modular/buildings/purdue_memorial_union.blend`
- Builder: `modular/buildings/build_purdue_memorial_union.py`
- Prior independent grades: [R1](independent_grade_r1.md), 7.7/10; [R2](independent_grade_r2.md), 7.9/10. R3 addresses the repeated roof-plane / junction findings and adds source-visible south-wing roof and window rhythm from the 1924 photograph.
- Export collection: `Asset_purdue_memorial_union`
- Refinement is confined to the individual PMU asset and this PMU-specific evidence folder. The master file and placement marker were not opened for writing.
- The historical GIS-supported shell, base, root origin, and current master placement were preserved. New facade pieces are local to the PMU asset and assigned PMU-specific names/materials.

## Evidence used

| Subject | Primary source | Provider and source date | Retrieved |
|---|---|---|---|
| Early south/front facade, wing openings, tower-and-wing composition | [Purdue Archives photo: PMU shortly after construction](https://blogs.lib.purdue.edu/news/2017/03/27/from-the-archives-photo-challenge/); direct image: [PPBUC00823.jpg](https://i0.wp.com/blogs.lib.purdue.edu/news/files/2017/03/PPBUC00823.jpg?fit=1111%2C639&ssl=1) | Purdue Libraries Archives; image captioned as shortly after construction, 1924 | 2026-10-25 |
| Contemporary south facade, stone tower surround, arched glazing, entry portal and sculptural side fields | [Purdue Memorial Union centennial feature](https://stories.purdue.edu/topic/the-purdue-memorial-union-turns-100/); direct image: [Hero-PMU-7R0A0670](https://stories.purdue.edu/app/uploads/2024/09/Hero-PMU-7R0A0670-1920x1080-Option2.jpg) | Purdue Stories / Purdue University; centennial feature, 2024 | 2026-10-25 |
| Historic plan footprint and phase attribution | [Purdue Libraries CampusBuilding service](https://mapsweb.lib.purdue.edu/arcgis/rest/services/Purdue/campus/MapServer/0); raw query and previous GIS comparison in `../purdue_memorial_union_independent_grade/` | Purdue Libraries GIS; historic records for 1929, 1935–36, 1938–40 and 1953–55 | 2026-10-25 |

The images were inspected as whole-building reference photographs. The early image supports the tower-and-wing massing and arched openings; the 2024 image supports the present south entry and stone tower treatment. They are not measured elevations, and they show different time periods. Photo-specific details were added as visual references, not claimed as a fully surveyed reconstruction of one date.

## Build and modeling method

- Builder reopens the existing modular blend, makes deterministic PMU-only changes, then saves the same individual asset. Reruns remove and recreate all `PMU_R1_` geometry.
- Seven south-wing window heads are given arched glazing and segmented Bedford limestone archivolts, including a fourth south-west bay visible in the 1924 archive photograph; blocking generic lintel/hood pieces are replaced. Existing wall shells and bases remain unchanged. Exterior glass uses non-emissive leaded glazing so it reads as dark glass rather than glowing opaque panels.
- The south entry receives a three-leaf glazed door, fanlight, segmented stone arch, and shallow side relief fields informed by the 2024 photograph. The tower glazing is split into lower rectangular and upper arched multi-light tiers. No unsupported statuary was added.
- The over-broad original roof pieces were replaced with five lower wing gables (north, east, west, south-west and south-east), each with separate eaves/ridge, thin ridge/eave caps and junction flashing. The R3 slate material uses a restrained procedural tile surface; no image texture dependency is added. South roofs follow the south-wing's 16 m depth instead of the old 56.5 m span into the courtyard.
- Three modest dormers on the south-west wing follow the dated 1924 archive photo. Their sizes are photo-derived estimates; no dormers were added on the opposite wing without equivalent evidence. The window and dormer count/rhythm in this area now reflects the photographed 4+3 arched bays and the three visible west-wing dormers.
- No new external image textures or linked library dependencies are used. Existing PMU material datablocks are reused.

### Geospatial method and limits

The footprint comparison remains that documented in `../purdue_memorial_union_independent_grade/source_evidence.md`: Purdue Libraries GIS building polygons returned in EPSG:4326 (service metadata advertises Web Mercator EPSG:3857 / 102100), converted to an approximate local tangent plane around 40.4274° N, -86.9137° E and compared in the PMU asset's local axes after applying the read-only manifest placement `(205.75, -271.65, 0)`. The historical 1935–36 outline was reported within roughly 0.5 m on principal bounds; that is approximate historical alignment, not survey precision or evidence for current additions. No new CRS conversion or georeferencing was used for facade imagery.

## Dimensional evidence and uncertainty

- Footprint: historical GIS phase geometry provides the strongest available support; preserve the existing structural footprint and marker placement.
- Height: the saved asset's aggregate top is a model dimension (approximately 29.5 m in the original inventory), not a verified measured building height. The structural masonry extents top out at approximately 25.5 m, with decorative details extending higher. No measured elevation/roof schedule was found in the reviewed official sources.
- Floors: visible storey bands are modeled from imagery and the existing asset; a source-backed floor/elevation schedule was not found. Treat floor count and vertical spacing as estimates.
- Roof profiles: the 1924 photograph and 2024 exterior image support slate-covered pitched wings and a taller central tower, but not measured ridge/eave elevations. New wing-roof silhouette is an explicitly labeled photo-derived estimate.
- Facade: opening and portal articulation follows the cited photographs. Detailed dimensions, concealed interior structure, and any post-2024 alterations are unverified.

## Validation and preview

- Build command: `blender --background --python modular/buildings/build_purdue_memorial_union.py`
- Fresh-reopen preview/validation command: `blender --background --python audit/purdue_memorial_union_refine/render_preview_r1.py`
- R3 preview: [south_refine_preview_r3.png](south_refine_preview_r3.png)
- R3 facade detail: [south_facade_detail_r3.png](south_facade_detail_r3.png)
- Fresh R3 review angles: [grader_south_oblique_r3.png](grader_south_oblique_r3.png), [grader_west_oblique_r3.png](grader_west_oblique_r3.png), [grader_roof_r3.png](grader_roof_r3.png)
- R3 validation report: [validation_r3.json](validation_r3.json)
- Evaluated saved file by opening it again in Blender after the build. All mesh objects have assigned materials, there are no external image dependencies, and the root is at identity.
- Structural preservation uses the original audited bounds record `../purdue_memorial_union_independent_grade/structural_bounds.json`, keyed to original asset SHA-256 `b1afa1dcffd08626c7508153b3c4d3a59cac86d605b6553d7f3477a01d972a25`. All 18 original wall/base bounds are compared directly with 1 mm tolerance. Three current wall/base pieces are additive: `PMU_Oriel_SE_Base`, `PMU_Oriel_SW_Base`, and `PMU_Tower_Base_Limestone`. Five original roof geometry objects are intentionally replaced by 20 separately named R2 gables and eave/ridge caps.
- Do not use Blender's rolling `.blend1` file as the original baseline: it is a mutable previous-save backup. `validation_r1.json` now compares against the immutable original audit record and clearly distinguishes unchanged originals from additions/replacements.
- Exact current object and mesh counts, saved-file SHA-256, bounds comparisons, and remaining dimension uncertainty are recorded in `validation_r3.json`. This evidence compares to the audited original bounds record, not the mutable `.blend1` backup.

## R4 iteration (2026-10-25)

- R4 keeps the original 18/18 audited wall/base bounds unchanged (0.0 m delta), all three prior additive base objects, the original root transform, and the existing master placement reference. It does not edit the master or shared manifest.
- Roof intersections now have separate, narrow valley flashing traces at the north cross-wing/side-wing junction. The side-wing roof surfaces again cover their full modeled wall lengths after an initial R4 test exposed unsupported bare masonry at the back ends; R4 retains the R3 estimated low gable profile and south-wing depth. Eave/ridge elevations and junction positions remain estimates. The roof mass still reads as large slate planes in overhead views; the available photos do not provide measured roof junction geometry, so this is unresolved rather than claimed as a verified roof reconstruction.
- The 2024 Purdue south-elevation photo visibly shows paired standing relief figures in stone panels flanking the tower's middle windows. R4 adds paired shallow limestone silhouettes in those locations. Their placement and grouped vertical form follow the image; fine carving details are intentionally omitted rather than invented.
- The exported collection now has 650 objects (608 meshes), with 22 R4 roof detail objects and 20 R4 relief objects. All meshes retain materials and the asset has no unpacked external image dependencies.
- Fresh reopen/validation: [validation_r4.json](validation_r4.json). Fresh evaluator renders: [south oblique](grader_south_oblique_r4.png), [west oblique](grader_west_oblique_r4.png), [roof](grader_roof_r4.png), [courtyard](grader_courtyard_r4.png). Facade detail: [south_facade_detail_r4.png). The reopened asset SHA-256 is `7e0e03969cad5846edacc38a4945f2c9021e48877c022cc79035d10e144eb480`.
- The 29.5 m aggregate top, floor spacing, roof/eave/ridge heights, and junction geometry remain estimates; no measured elevation or roof plan was found in the cited sources.

## Remaining reviewer checks

Please score the south facade/entrance, arched window rhythm, source-supported tower relief, tower/wing separation and roof silhouette against both dated sources. Keep height/floor confidence limited to the explicitly estimated values above; no quantitative elevation source is supplied.
