# Independent Grade — Wiley Dining Court (WDCT)

**Score: 8.0/10 — PASS for candidate.** Coordinator integration and a fresh-open check of the assembled master are still required before the building is marked finished.

Reviewed the exact current candidate `modular/buildings/massing_wiley_dining_court_wdct_8a6c669.blend`, SHA-256 `0A12600FB6D4C297CED05A5FD0382007C984180763DF3642F5AEF62E5565D16A`. A fresh Blender 5.2.3 open confirmed the stable scene and collection, 1,054 collection objects (1,053 meshes), material coverage on every mesh, and no external image dependencies.

| Criterion | Score | Finding |
| --- | ---: | --- |
| Identity and footprint | 2.0/2 | Purdue GIS FID 649/WDCT is corroborated by adjacency south of Wiley Hall. The candidate structural outline scores 0.9959 polygon IoU against the returned GIS ring, with bounds differences under 0.016 m. The GIS `Shape__Area` field conflicts with the area recomputed from the returned geometry; the footprint comparison appropriately uses the ring. |
| Position, orientation, dimensions | 1.6/2 | Candidate is local to proposed marker origin `(-597.574, 124.804)` m, with east-west long axis matching the source plan. Manifest still describes the previous world-coordinate massing asset, so marker-based integration and final master verification remain outstanding. The project conversion is approximate rather than surveyed. |
| Height and roof | 1.3/2 | The central gable and lower wings match the photo evidence. FRP describes one story plus a basement, while GIS reports three levels and has undocumented height-field units. Eaves/ridge/crest heights remain estimates; no basement geometry is included. |
| Exterior and materials | 1.7/2 | Brick, limestone, large dark-framed glazing, gable, standing-seam roof, and secondary details are recognizable. Twelve procedural node materials make the source portable. The current previews are dark and stylized; brick relief is subtle and some window/wing details are generalized. |
| Interior, modularity, evidence | 1.4/2 | The model includes dining furniture, service counters, circulation tile, timber roof structure, and pendants, consistent with Purdue's description and the architect's gallery. The interior image is dim and furniture is blocky/repetitive compared with the real images. Treat room and furniture layout as schematic, not surveyed. |

Primary references reviewed: Purdue News Service's [2008 dedication article](https://www.purdue.edu/uns/x/2008b/081001CelSautter.html), which identifies the freestanding dining court south of Wiley Hall and describes its brick/glass exterior and vaulted wood interior; and Fink Roberts & Petrie's [project page and image gallery](https://frpinc.com/projects/wiley-dining-court/), which documents the single-story structure with basement and 500-seat capacity. The official GIS feature snapshot and reprojection comparison are retained under `audit/wiley_dining_court/sources/` and `gis_comparison.json`.

**Integration gate:** change the manifest entry from direct campus-coordinate massing to local detailed placement at `(-597.574, 124.804)` m, build the placement marker, reopen the full master, and verify the updated library appears once in context. Preserve the height and source-field uncertainties.
