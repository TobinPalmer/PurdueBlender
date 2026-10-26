# Independent Wiley Hall R2 grade

**Asset SHA-256:** `8f3e904273ec680811163d8150098aa0f67f55705376df86359b8510cc3a3859`  
**Score:** **8.3/10 — passes the 8.0 threshold**  
**Blender:** 5.2.3 LTS  
**Review date:** 2026-10-25

## Fresh reopen and scope

I freshly opened the exact saved asset SHA in a new Blender background process. `Asset_wiley_hall` contains 398 objects: 382 meshes, 14 empties, and two text objects. The root has an identity transform. All mesh objects have material assignments, material slots are valid, no mesh is empty, and there are no missing external images. The relative foliage-library link resolves.

The oversized lawn and road surfaces are retained in `Wiley_SiteContext_NotExported`, outside the export collection. The separate R2 membership/transform check shows the four context objects remain outside the 398-object export and retain their parent/world transforms. This removes the major R1 master-integration blocker.

I also reopened the current master read-only in a separate Blender process. `Placement_wiley_hall` instances the expected `Asset_wiley_hall` collection from this asset at `(-447.585266, 234.070374, 0)` m with identity rotation and scale. The check is recorded separately in [independent_grade_r2_marker.json](independent_grade_r2_marker.json); it did not save or alter the master.

## Correct GIS feature and placement

The source query includes two nearby buildings: Wiley Dining Court is `OBJECTID 282`, `WDCT`, `buildingidlong 141`; Wiley Hall is **`OBJECTID 290`, `WILY`, `buildingidlong 148`**. This review uses Wiley Hall's WILY feature only. Under the project’s approximate local X-east/Y-north transform, that GIS ring's bounding box is about 90.33 × 119.22 m, centered at `(-595.01108, 234.10049)` m.

The main modeled brick shell has local bounds about 80.42 × 110.43 m. Translated by the manifest/master placement, its bounding-box center is about `(-595.01105, 234.07040)` m—around 3 cm south of the WILY GIS bounding-box center. This supports a good source position. The shell's bounds are about 10 m smaller along each principal dimension than the GIS ring bounds. This remains a bounding-box comparison only; the GIS polygon is not established as a surveyed wall line, so the size difference should be resolved with a registered outline overlay before any rescaling.

## Visual review

The oblique and top inspection renders show a coherent three-storey brick residence hall: two long wings, a central courtyard, a lower common block, repeated window bays, pale entrance/stair accents, and flat roof masses. The overall organization is consistent with Wiley's identity and the broad official exterior references. The façade grid is repetitive and secondary entrances, roof services, and some junction details are simplified.

The asset also contains extensive interior geometry/material groups for rooms, beds, desks, lounges, and finishes. Purdue confirms standard rooms, lounges, study/support functions, and an academic center in repurposed dining space. Purdue explicitly describes the room illustrations and dimensions as approximate; the modeled floor-by-floor room arrangement and furnishings are therefore treated as illustrative. This review did not render an interior view.

The export uses 142 distinct materials with no unassigned mesh surfaces. Brick, light trim, coral/pink panels, glazing, interior finishes, and dark roof surfaces are distinguished. The used material datablocks have no image-texture nodes, so their surface appearance is represented through shader values/procedural setup rather than demonstrated photographic maps. The inspection images use Workbench shading; final-engine lighting and shader appearance are not graded here.

## Scorecard

| Category | Score | Evidence |
|---|---:|---|
| Identity, footprint, and placement evidence | 1.5/2.0 | Correct WILY 290 selected; fresh master marker confirmed; shell center about 3 cm from converted GIS bbox center. Model/GIS extents differ and no full wall polygon comparison was done. |
| Exterior massing and recognizable architecture | 1.7/2.0 | Legible courtyard residence-hall organization, three-storey wings, central common block, window bays, and entries; details remain simplified. |
| Materials and surface finish | 1.2/1.5 | 142 used materials and valid assignments; no missing images. No image-texture nodes in used materials; final-render appearance not verified. |
| Interior and resident program | 1.6/2.0 | Substantial interior/room/lounge/furnishing groups; no as-built plan confirmation and no interior render in this review. |
| Technical integrity and portability | 1.4/1.5 | Exact-SHA reopen passes; export excludes oversized context; relative foliage library resolves; root/material/dependency checks pass. |
| Evidence quality and uncertainty | 0.9/1.0 | Raw GIS, corrected feature identity, fresh asset and master reopen, context separation, and inspection images retained; wall outline, height, and interior remain uncertain. |
| **Total** | **8.3/10** | **Pass** |

## Prioritized follow-up

1. Create a registered top-down overlay of the actual structural walls against WILY `OBJECTID 290`, and compare orientation, courtyard, and polygon intersection. Do not rescale the complete model from bounding boxes alone.
2. Render one standard room and one common/support interior in the project's final renderer; keep room layout identified as illustrative without an as-built plan.
3. If photographic realism is a goal, add/check close-range brick, masonry, glazing, and roof surface detail and verify final-engine shader response.

## Evidence

- [Fresh asset reopen](independent_reopen_r2.json), [reopen script](independent_reopen_r2.py), [oblique render](oblique_r2.png), and [top render](top_r2.png).
- [Correct WILY footprint calculation](footprint_bounds_r2.json), [raw GIS query snapshot](gis_query.json), and [R2 context separation verification](site_context_reopen_r2.json).
- [Fresh read-only master marker check](independent_grade_r2_marker.json).

## Official sources

- [Purdue Housing — Wiley](https://www.housing.purdue.edu/my-housing/options/residence-halls/wiley.html): address, opening date, residential program, lounges and support/study uses; room layout illustrations are approximate.
- [Purdue Residences — Wiley Academic Success Center](https://housing.purdue.edu/get-reconnected/2017/04/index.html): the center occupies repurposed dining space and includes collaborative study, offices, and consultation rooms.
- [Purdue Campus Building GIS layer 0](https://mapsweb.lib.purdue.edu/arcgis/rest/services/Purdue/campus/MapServer/0): WILY feature `OBJECTID 290`; raw query response and transform calculation retained above.
- [Purdue Archives — Wiley Residence Hall](https://earchives.lib.purdue.edu/digital/collection/pbuildings/id/2834): official archival exterior photograph record dated 2004-06-14.
