# Engineering Mall foliage and site evaluation

Reviewed render: `engineering_mall_foliage_library_review.png`, produced 2026-10-23 19:22:24 by reopening the standalone Engineering Mall patch. The current master now links that patch as `Engineering_Mall_Groundwork_Patch_Instance` at project XY (0, 0, 0); both patch and foliage library use project-relative paths.

## Revised rubric

Tree silhouette is intentionally not a grading category. Purdue planting forms change by season and individual trees vary. Grade recorded location and growth habit, distribution/density, material quality, path and lawn placement, module performance, and provenance instead. Allow visual variation when mapped placement and planting function are right.

| Category | Weight | Score |
|---|---:|---:|
| Mapped locations and OSM alignment | 20% | 9.5/10 |
| Species and growth-habit plausibility | 15% | 7.0/10 |
| Plant distribution and density | 15% | 8.3/10 |
| Materials and textures | 15% | 8.2/10 |
| Paths, turf, and plaza placement | 15% | 8.8/10 |
| Modularity and performance | 10% | 7.2/10 |
| Provenance and uncertainty records | 10% | 9.5/10 |
| **Weighted total** | **100%** | **8.4/10** |

## Evidence and limitations

Reopened patch QA found 349 mapped Arboretum plants at source XY (reported difference under 1 mm), five separately identified inferred trees, 93 OSM path ribbons, 30 turf parcels, and a 20-face plaza fill. All 354 plants are linked collection instances. The library contains 18 collection assets, nine material assets, and 76 packed images.

The source inventory does not include heights for 334 of 349 mapped plants or spread for 35; their dimensions are treated as estimates. Current visual assets are generic broadleaf, shrub, and fir proxies, so the species-specific score is lower. The rendered crowns look airy and the exposed turf is brown/desaturated. The broadleaf shared LOD2 has 148,509 faces; this geometry is stored once in the library, but repeated campus placements still increase render cost. Add lower distance LODs before broad campus-wide use.

Sources: Arboretum inventory snapshot and OpenStreetMap snapshot in this audit folder; model/material source pages and CC0 notes in `../..\modular\site\foliage_library\README.md`.
