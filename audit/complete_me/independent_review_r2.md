# Mechanical Engineering R2 — Independent Full-Building Review

**Review date:** 2026-10-24  
**Revision reviewed:** R2  
**Asset:** `modular/buildings/mechanical_engineering.blend`  
**Reviewer:** Independent reviewer; did not build or edit R2  
**Score:** **7.5/10**  
**Decision:** Below the project's 8.0/10 acceptance target; continue revision.

## Scorecard

| Criterion | Score | Review |
| --- | ---: | --- |
| Identity and footprint | 1.8/2.0 | The 2023 orthophoto overlay strongly supports FID 857 as the large ME complex and FID 108 as a distinct low-roof segment at its southeast edge. FID 108's relative position is credible. The project-local conversion is approximate and the footprints touch/overlap; internal connection and wall-level registration are unresolved. |
| Placement and orientation | 1.6/2.0 | The asset root remains at identity, local XY is unchanged, and the fountain-facing entrance direction remains supported by Purdue. R2 makes no read-only master-marker/library-link audit, and exact project-to-source control remains approximate. |
| Form, height, and roof | 0.9/1.5 | The FID 108 correction to about 4.2 m is supported by a same-location 2018 DSM/DTM sample and a uniform local DSM patch; excluding three unsupported upper slabs is sensible. The major FID 857 shell remains a single 18.5 m mass with a broad flat roof. Its 6×6 DSM/DTM readings span roughly 24–71 ft above terrain, but cannot reliably distinguish roof surfaces, equipment, and canopy or assign heights to specific wings. The documented mixed roof forms and wing breaks are not modeled. |
| Facade, materials, and entrance | 1.5/2.0 | R1's brick shader, punched openings, frames, stone bands, and fountain-facing arch are still supported as qualitative feature categories. The rendered long face has a highly regular repeated four-row window schedule; exact counts, opening layout across individual wings, and the portal's along-wall position remain unregistered estimates. R2 adds no facade registration. |
| Interior and circulation | 0.7/1.5 | The 2025 emergency-plan slides now provide current egress diagrams and show ME/Gatewood floor extents and vertical cores. The 2015 study adds connection and elevator context, but explicitly predates the current renovation and excludes Gatewood in its measured-area plans. R2 does not update the asset's approximate floors or partitions, and evacuation routes are not a full as-built circulation plan. |
| Technical integrity | 1.0/1.0 | Blender 5.2.3 reopens the asset and R2 validation passes. The expected export collection and identity root remain; FID 108 XY and FID 857 geometry are unchanged; unsupported FID 108 upper slabs are recoverable outside the exported collection. No new external texture dependency is introduced. |
| **Total** | **7.5/10** | **Below target** |

## Findings

R2 meaningfully resolves the broad GIS identity overlap and fixes a consequential massing error on FID 108. I inspected the 2023 orthophoto overlay: the cyan FID 108 outline lands on a compact low roof near the southeast edge of the red FID 857 complex. At FID 108's centroid, the 2018 5-ft DSM cell is 634.840 ftUS and the corresponding bare-earth DEM query is 621.070 ftUS, a 13.770-ft (4.197-m) difference. Its eight neighboring DSM cells also lie within a narrow band. This makes the new 4.20 m wall top and 4.20–4.45 m cap a defensible rounded estimate. It is still one local raster estimate, not a surveyed wall height; the overlapping polygon means the precise building-to-building connection is not proven.

The new surface data does not resolve the main complex. FID 857's reported DSM/DTM grid varies considerably by position, and the DSM contains all elevated returns rather than only roof planes. With no registered roof plan or measured elevation tying those readings to individual wings, the retained uniform 18.5 m shell remains uncertain and visibly misses Purdue's documented mixed roof types/phase breaks. The current evidence is enough to say the one-height treatment is incomplete, but not enough to choose safe wing-specific heights or pitched-roof footprints.

The R1 exterior facade remains a good visual category match, but the hero view is still dominated by a large unbroken gray roof, and the front view shows repeated identical rows across a broad face. The facades are not matched to specific GIS edges using oriented elevations. The 2025 evacuation maps improve the source record for circulation, but no current interior geometry was incorporated. A higher score needs a registered facade/roof plan or direction-identified elevation, plus a current floor plan or source-registered route/core placement.

## Priority work before a pass

1. Find a direction-registered roof/elevation source that distinguishes the 857 wings and supports roof breaks/heights; otherwise retain explicit uncertainty and do not fabricate those changes.
2. Register at least one current facade elevation/photo to a GIS edge before revising the repeated 208-window schedule or entrance's along-wall location.
3. Use a current post-renovation floor plan with a usable scale/orientation to locate stair/elevator cores and model the supported Gatewood connections. The evacuation diagrams alone are not a measured floor plan.
4. Add a read-only master marker and library-link check to close the remaining placement uncertainty without saving the master from this building task.

## Sources reviewed

- [Indiana Current Imagery service metadata](https://di-ingov.img.arcgis.com/arcgis/rest/services/DynamicWebMercator/Indiana_Current_Imagery/ImageServer?f=pjson) and the R2 saved 2023 Tippecanoe orthophoto/GIS overlay.
- [Indiana 2018 QL2 3DEP DSM tile](https://giselevationingov.s3.us-east-2.amazonaws.com/dsmoptimized/statewide/2018/SPW/5ft/in2018_30001885_12.tif) and [Indiana 2016–2020 bare-earth DEM metadata](https://www.arcgis.com/home/item.html?id=a95c857cb47649ec87b04810214b0c1c), with computations in `mechanical_engineering_lidar_r2.json`.
- [Purdue BuildingShapes FeatureServer](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0), FID 857 and FID 108 in `audit/official_building_references.json`.
- Purdue 2025 emergency-plan presentation, saved as `safety2025.pdf`, slides 11–15, dated 2025-08-21; and [Purdue 2015 ME-RAIL-HAMP study](https://engineering.purdue.edu/~frosch/Renderings/Masterplans/ME-RAIL-HAMP%20Study.pdf).
- [Purdue 2023 entrance/renovation notice](https://engineering.purdue.edu/ME/News/2023/me-building-renovation-brings-changes), [Purdue 2025 history and exterior photo](https://engineering.purdue.edu/ME/News/2025/purdues-mechanical-engineering-building-represents-more-than-a-century-of-history), and [2024 Wikimedia Commons facade photo](https://commons.wikimedia.org/wiki/File:Purdue_Mechanical_Engineering_Building.jpg).
- `mechanical_engineering_r2_validation.json`, `mechanical_engineering_r2_fid108_aerial.png`, the R1 entrance/hero renders, and `independent_review_r1.md`.

No asset, master, shared index, or other building was changed during this review.
