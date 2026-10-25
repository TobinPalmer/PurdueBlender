# PMU independent grading evidence

## Asset reviewed
- Asset: `modular/buildings/purdue_memorial_union.blend`
- Export collection / scene: `Asset_purdue_memorial_union` / `Building_purdue_memorial_union`
- SHA-256 at review: `b1afa1dcffd08626c7508153b3c4d3a59cac86d605b6553d7f3477a01d972a25`
- Fresh reopen inventory: `fresh_reopen.json`; structural extents: `structural_bounds.json`; material-node inventory: `materials_inspection.json`; non-destructive renders: `oblique.png`, `south.png`, `west.png`, `top.png`.
- The individual asset reopened from disk. Its root is identity transform, and all meshes have assigned materials. It contains 414 objects (386 meshes, 7 fonts, 20 lights, 1 empty), with local aggregate bounds X [-60.75,60.75], Y [-62.35,62.35], Z [0,29.5] m. It has no external image files and no camera. Materials are procedural node materials (17 named with `PMU_` prefix); their presence does not establish source accuracy.

## Sources and method

1. **Purdue Libraries campus GIS feature layer** — [CampusBuilding layer metadata](https://mapsweb.lib.purdue.edu/arcgis/rest/services/Purdue/campus/MapServer/0), raw query snapshot `purdue_gis_query_raw.json`. Provider: Purdue Libraries GIS. Retrieved 2026-10-25. Geometry is campus-building polygon data in Web Mercator (EPSG:3857 / 102100); query response was requested as EPSG:4326. Matching name returned historical construction-phase features: OBJECTID 278 (1935–1936), 472 (1929), 482 (1938–1940), and 292 (1953–1955, PMU Club / hotel expansion). The latter is not treated as PMU main asset. Compare feature 278 and 482 against the identified structural wall/base edges in `structural_bounds.json`, not decorative aggregate bounds. Coordinates were converted from geographic degrees with the project’s approximate local tangent conversion (origin 40.4274 N, -86.9137 E; X=(lon+86.9137)*111412.84*cos(40.4274°), Y=(lat-40.4274)*111040), then offset by the PMU manifest marker (205.75, -271.65). The model shell extents are within roughly 0.5 m of the 1935–36 outline on the principal bounds; the 1938–40 outline extends about 4 m farther north. This supports an approximate historical footprint match, not a survey-grade current footprint. Source record is temporal and may represent phases/additions rather than the present building.

2. **Purdue campus map** — [official campus map PDF](https://www.purdue.edu/campus-map/graphics/campusmap.pdf). PMU is mapped at H7, near Stewart Center. This verifies general campus identity/location only; no measured orientation or dimensions were extracted from the raster map.

3. **Purdue Stories centennial feature** — [The Purdue Memorial Union turns 100](https://stories.purdue.edu/topic/the-purdue-memorial-union-turns-100/), official Purdue source. Used for broad identity/history context and linked building imagery, not dimensions.

4. **Purdue Libraries Archives** — [From the Archives: Photo Challenge](https://blogs.lib.purdue.edu/news/2017/03/27/from-the-archives-photo-challenge/), official Purdue archive post. Historical image/context supports the recognizable central tower with adjoining wings and Gothic masonry character. It does not provide a measured elevation.

5. **Purdue Board of Trustees project document** — [PMU ground-floor renovation PDF](https://www.purdue.edu/bot/meetings/past-meetings/2020/02.%20apr/pfc/pmu%20ground%20floor%20renovation.pdf), official Purdue project source, 2020. It identifies PMU ground-floor work and two exterior terraces at the south end. No equivalent modeled/current details were verified from this document.

6. **Master placement read-only inspection** — `master_marker_readonly.json`. Exactly one `Placement_purdue_memorial_union` marker points to the expected asset collection/path, with location (205.75,-271.65,0), rotation (0,0,0), scale (1,1,1). This confirms library linkage and transforms in the reviewed master data, not that all neighboring campus context is accurate. No master save occurred.

## Visual comparison and uncertainty

The controlled renders show a recognizable, roughly U/courtyard-plan Gothic campus building with central clock/tower mass, side wings, repeated brick/stone facade, crenellated turret-like features, and some interior hall/dining/stair/fireplace elements. The front tower and general massing are identifiable. The south and west facades use many simple square/rectangular window patterns where source imagery suggests stronger tall arched openings and richer entrance/masonry articulation. The pale, simple roof masses lack sufficiently source-backed silhouette/material detail. I found no building-specific raw imagery/elevation set, dimension schedule, dedicated build/evidence record, or measured height source in the provided audit/source directories at review time. The 29.5 m asset height is a model dimension only; it is not validated against a measured source. Floor count and roof form are therefore partly estimated.

The 1935–40 GIS phase polygons support the footprint but cannot validate present-day additions or floor/roof/facade accuracy. Relative structural alignment is strong, but the comparison uses an approximate project conversion and historic map data. Small residuals should not be interpreted as survey precision.
