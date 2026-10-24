# Hovde Hall — round 13 source revision

## Source-backed revision

- Added the Purdue ECE 2023 Engineering Mall aerial at `reference_engineering_mall_aerial_2023.jpg`. It confirms the broad red-tile roof and low visible roofline. The oblique view does not resolve the roof pitch, hidden ridge, hip layout, or structure, so the existing shallow 0.16 m cap remains a conservative visual approximation.
- Replaced the faceted capital leaves with smoothly subdivided, shallow acanthus-like relief and restrained midribs. The 2016 exterior photograph supports leafy classical capitals; the exact relief layout remains interpretive. No unsupported corner volutes or extra carving were added.
- Preserved the Hovde source root transform, all window/door positions, shell, and master files.

## Source-to-GIS plan comparison

`footprint_overlay_round13.py` reopens the saved source asset and compares official Purdue ArcGIS BuildingShapesZip4 feature 618 with the current `HOVD_Roof_Slab` convex-hull projection. GIS coordinates are converted through the project's approximate campus XY frame, then shifted by the saved `HOVD_Root.matrix_parent_inverse` translation to match the source-library frame.

At a 0.25 m raster step, the roof-slab footprint proxy has **0.8945 IoU** with the filled GIS polygon; GIS coverage is **0.9609** and proxy coverage **0.9282**. GIS bounds are approximately X -42.96 to 17.63 m and Y -18.96 to 48.54 m in the source-library frame. The source proxy bounds are X -43.83 to 17.73 m and Y -19.36 to 48.87 m. The 145-vertex GIS ring's long edges average 39.301° counter-clockwise from north; the source long axis is 39.52°, a 0.219° difference.

This is a roof-slab convex-hull proxy comparison, not an exact wall-polygon registration. GIS is an approximate project conversion, not survey control. The coordinator separately verified the master placement marker against the manifest; this source overlay does not replace that check.

## Reopen and preview checks

Blender 5.2.3 reopened the saved source blend. `final_asset_check_round13.json` records 760 export objects (740 meshes and 8 curves), no unmaterialed meshes, valid face indices, six smoothed capital-leaf meshes, six midrib curves, the preserved root transform, and the unchanged 0.16 m roof rise. `footprint_overlay_round13.json` records the source/GIS measurements.

- `same_angle_reference_round13.png` — entrance-centered comparison view.
- `portico_detail_round13.png` and `portico_oblique_round13.png` — portico depth, window relationship, and facade views.
- `portico_capital_close_round13.png` — revised leaf relief and midribs.
- `roof_detail_round13.png` — shallow red-tile surface checked against the 2016 facade photo and 2023 aerial.
- `footprint_overlay_round13.png` — GIS outline and source roof-slab footprint proxy.

## Remaining limits

Exact roof pitch, concealed ridge/hip form, and roof construction remain unverified. Capital carving, portico dimensions, upper window placement, and the roof-slab proxy are estimates rather than surveyed details. The current overlay does not assert exact structural wall-polygon correspondence. The master blend, placement marker, manifest, README, and other buildings were not edited.

**Ready for a fresh independent grade.**
