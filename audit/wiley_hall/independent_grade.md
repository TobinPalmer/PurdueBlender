# Independent grade: Harvey W. Wiley Residence Hall

**Asset:** `modular/buildings/wiley_hall.blend`  
**Reviewed SHA-256:** `80b4e00f0537b2a78956c262ea0c0afd81f2b08cc3469a8f278ff93fbf603742`  
**Result: 7.8/10 — below the 8.0 acceptance threshold.**  
**Review date:** 2026-10-25  
**Blender:** 5.2.3 LTS

## Review scope and fresh reopen

I independently opened the exact saved file in a fresh Blender 5.2.3 process. The `Asset_wiley_hall` collection contains 402 objects (386 meshes, 14 empties, and 2 text objects). `AssetRoot_wiley_hall` has identity transforms. No mesh lacks a material, and no image file is missing. The collection links the project's foliage library through a relative path that resolves. There are no saved cameras or lights in the exported collection; the attached inspection images use temporary Workbench cameras and did not alter or save the asset.

The exact hash, evaluated mesh bounds, used materials, linked libraries, image dependencies, object samples, and reopen procedure are recorded in [the reopen report](independent_reopen.json). [Oblique](oblique.png) and [top](top.png) renders provide the visual inspection views. They are Workbench previews rather than final-render-engine images.

## Identity, map fit, and architecture

Purdue's campus building GIS layer identifies the residence hall as `Harvey W. Wiley Residence Hall`, abbreviation `WILY`, `OBJECTID 290`, `buildingidlong 148`, at 500 N. Martin Jischke Drive. The returned feature has a 73-vertex ring and source area of about 9,517 m². The source layer is EPSG:3857; I queried its geometry as EPSG:4326 and applied the project's documented approximate local conversion. The converted GIS ring bounds are about 90 x 119 m.

The modeled roof bounds are about 80 x 110 m. Adding the manifest origin to those local bounds puts the modeled roof bounding-box center within about 0.5 m of the GIS ring bounding-box center. This is a useful location/identity check, but it is not a full wall-footprint overlay: the model is about 10 m smaller in each principal dimension, and the GIS ring is not certified as a surveyed wall line. Master marker alignment and neighboring buildings were outside this independent asset review.

The model reads as a three-storey brick residence hall with long wings around a courtyard, a central common block, repeated window bays, and flat roof masses. Purdue's official exterior image record describes a three-storey brick façade with colored panels and a glazed entry/stair. The main form and broad material palette are consistent with that evidence. Window bays repeat very regularly, and secondary entrance, roof, and service details remain schematic.

## Interior and materials

The asset contains a substantial interior representation: room and common-space geometry, bedroom furnishings, desks, beds, lounge areas, and finish materials. Purdue's residence page confirms standard rooms and study/support spaces, but calls its room illustration and dimensions approximate. Public sources reviewed here do not verify the model's floor-by-floor interior layout or exact furnishing arrangement, so those elements remain illustrative.

The asset uses brick, pale trim, pink/coral spandrels, glazing, and roof finishes as distinct material groups. The reopen found 147 used material datablocks, no materialless meshes, and no absent external image files. The Workbench views show the materials clearly enough to read the building, but appear flatter than a final lit render and do not establish the saved shaders' final appearance.

## Key integration issue

The exported building collection also contains a lawn surface roughly **680 x 660 m** and a road mesh roughly **139 x 165 m**. Those site meshes are much larger than Wiley Hall itself. If linked into the campus master with the entire collection, they may cover neighboring roads, landscape, and building context. Separate them, clip them to a defined local site, or confirm their master-scene interactions before integration.

There is a related shared-index inconsistency for the coordinator to check: the current manifest's `exterior_bounds_world_m` Y range is roughly 70–181 m, while the fresh roof mesh bounds translated by the current manifest placement origin are roughly 179–289 m. The model roof center agrees with the GIS ring center, so the manifest exterior bounds appear stale or based on a different object group. I did not edit the manifest or inspect the master.

## Scorecard

| Category | Score | Basis |
|---|---:|---|
| Identity, footprint, and placement evidence | 1.5/2.0 | Correct official GIS feature and close bounding-box center; modeled bounds are smaller and master placement was not reviewed. |
| Exterior massing and recognizable architecture | 1.7/2.0 | Courtyard, long residence wings, three-storey brick reading, central glazed/common zone; repetitive bays and simplified secondary details. |
| Materials and surface finish | 1.2/1.5 | Distinct materials and complete assignments; Workbench preview reads flat and final shading was not checked. |
| Interior and resident program | 1.6/2.0 | Detailed rooms and common spaces; arrangement is not verified against as-built plans. |
| Technical integrity and portability | 1.0/1.5 | Exact-SHA reopen, identity root, relative foliage link, no missing images; campus-scale site geometry inside the building library is an integration risk. |
| Evidence quality and uncertainty | 0.8/1.0 | Official image/history and exact GIS feature retained; no full polygon overlay or measured height/interior evidence. |
| **Total** | **7.8/10** | **Does not pass the 8.0 threshold.** |

## Recommended work before resubmission

1. Separate or deliberately constrain the oversized lawn and road context so the building library cannot blanket surrounding master-scene geometry.
2. Reconcile the manifest exterior-bounds record against the actual evaluated shell and placement origin; keep local bounds and site-context bounds distinct.
3. Create a GIS-to-structural-shell top-down overlay using the 73-vertex WILY ring. Resolve the approximately 10 m width/length difference using wall geometry rather than roof or landscaping extents, and record the projection uncertainty.
4. Render at least one interior view. Keep it explicitly schematic unless a dimensioned, as-built floor plan is found.
5. Have the coordinator verify `Placement_wiley_hall` and adjacent site geometry after integrating the accepted building library.

## Sources

- [Purdue Campus Building GIS layer 0](https://mapsweb.lib.purdue.edu/arcgis/rest/services/Purdue/campus/MapServer/0) — returned WILY feature `OBJECTID 290`, `buildingidlong 148`; raw query response and converted geometry are saved as [gis_query.json](gis_query.json). Retrieved 2026-10-25.
- [Wiley | Purdue University Residences](https://www.housing.purdue.edu/my-housing/options/residence-halls/wiley.html) — hall history, official address, amenities, and note that room-layout illustrations/dimensions are approximate. Retrieved 2026-10-25.
- [Wiley Hall Exterior Entrance](https://housing.purdue.edu/get-reconnected/2017/04/index.html) — Purdue Residences exterior photo page and entry image. Retrieved 2026-10-25.
- [Wiley Residence Hall, Purdue Buildings and Campus Scenes](https://earchives.lib.purdue.edu/digital/collection/pbuildings/id/2834) — Purdue Archives exterior photograph record dated 2004-06-14. Retrieved 2026-10-25.
