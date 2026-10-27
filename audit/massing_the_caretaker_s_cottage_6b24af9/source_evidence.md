# The Caretaker's Cottage — source and build record

**Assignment:** Rossen, confirmed in the root README.  
**Stable ID:** `massing_the_caretaker_s_cottage_6b24af9`  
**Asset/collection/scene:** `modular/buildings/massing_the_caretaker_s_cottage_6b24af9.blend`, `Asset_massing_the_caretaker_s_cottage_6b24af9`, `Building_massing_the_caretaker_s_cottage_6b24af9`.  
**Coordinates:** simple massing remains in campus coordinates (X east, Y north, Z up); no Placement marker is expected. The stable manifest bounds and OSM polygon agree in XY.

## Identity and footprint cross-check

The official library page identifies the Caretaker's Cottage at 1496 N Salisbury Street, describes it as the 1903 Grand View Cemetery groundskeeper's house, and names Bedford limestone, terracotta roof tile, double porches, three to four rooms and a root cellar. The City of West Lafayette's March 5, 2024 opening announcement independently confirms the 1903 building and its historical preservation. OSM way 953041335 carries the exact cottage name, `operator=West Lafayette Library`, `year_of_construction=1903`, and historic-building tag. Its 10 unique vertices converted with the project lon/lat approximation reproduce the manifest XY bounds to less than 0.0001 m.

The Indiana statewide 2018 LiDAR building-footprint feature objectid 433415 is a nearby independent match. It is 0.86 m from the OSM outline centroid and overlaps it at IoU 0.722. The LiDAR outline is larger (209.76 m² vs. 159.48 m²) and, in the Indiana 2022–2025 orthophoto crop, follows the visible roof edge better. I treat OSM as the wall/base footprint and Indiana LiDAR as a roof-envelope check. Neither is a cadastral or architectural survey. The target-building GIS subset contains no Caretaker's Cottage record, so I did not infer an official campus-GIS feature ID for it.

## Build changes

- Replaced the original 16 m fallback extrusion with a small one-story stone cottage: walls to 3.35 m, roof eaves about 3.48 m, and ridge about 5.55 m. Vertical values are visual estimates; there is no measured elevation or verified height attribute.
- Rebuilt the structural shell directly from the 10-point OSM outline and retained campus-world coordinates.
- Added a terracotta roof envelope from the 2018 Indiana LiDAR outline, plus three stepped hipped roof volumes to represent the multi-plane silhouette in the orthophoto and historic photograph. Main ridge alignment follows the footprint's approximately 40-degree NE–SW axis. Tile relief uses a procedural brick pattern. Roof volumes, tile scale and all pitches are interpretations, not measured geometry.
- Added a limestone rubble material, light stone trim, framed windows/door, and a broad porch with enlarged stone piers and low stone parapet sections. A separate canopy and access ramp/rails were removed because the source photo does not support their positions; porch dimensions and opening layout remain estimates.
- Used only procedural materials; there are no external image dependencies. Preview cameras/lights are in `Presentation_Only`, outside the exported asset collection.

## Validation

A fresh Blender 4.5.15 build and reopen found the required scene and collection, 71 mesh objects with materials, no modifiers, no unpacked image files, identity object transforms, and 10/10 OSM structural-ring points within a maximum 0.000058 m XY error. Evaluated bounds are 21.17 m × 22.21 m × 5.55 m; height is an estimate, not a measured value. The saved asset and four regenerated views are recorded in `reopen_validation.json` and `renders/`. Master linking and duplicate replacement remain for the coordinator to review.

## Evidence and uncertainty

Raw OSM API and Indiana ArcGIS snapshots, official library and City pages, historic exterior and porch photos, orthophoto export, source index and registration metrics are in `sources/`, `source_index.json`, and `source_registration.json`. Orthophoto coverage is documented as 2022–2025; its exact capture date at this property is unavailable. The exterior photo is captioned 2017 and is unscaled. Roof geometry, story-height, windows, entry position and porch dimensions remain estimates.
