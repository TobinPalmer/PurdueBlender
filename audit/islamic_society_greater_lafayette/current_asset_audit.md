# Islamic Society of Greater Lafayette — Refinement Round 1

**Assigned asset:** `modular/buildings/massing_islamic_societyof_greater_lafayette_0130012.blend`  
**Exact saved SHA-256:** `57d4bdacd2dde6759bbc4892e153266ea0f4856368fa792179a002f5fe9f24fe`  
**Fresh-open:** PASS in Blender 5.2.3 LTS; see [current_asset_fresh_open.json](current_asset_fresh_open.json).

## Changes

- Preserved scene `Building_massing_islamic_societyof_greater_lafayette_0130012`, collection `Asset_massing_islamic_societyof_greater_lafayette_0130012`, stable object `Islamic Society of Greater Lafayette`, and the original 982-vertex / 747-face structure.
- Preserved the FID 771 GIS wall ring. Its 11 source vertices still match within 0.00001437 m under the documented longitude/latitude transform. The library remains in its existing campus-coordinate frame; no placement transform was introduced.
- Added a small 8 m × 6 m floor patch named `ISGL_Schematic_Interior_Open_Gathering_Space_Floor` and a visible `SCHEMATIC OPEN SPACE` annotation. Object properties state that this is a schematic placeholder, not a verified floor plan. No room partitions or named room functions are modeled.
- Replaced flat brick and roof shading with portable procedural physical-scale brick and slate-course materials, including subtle roughness variation and bump relief. No external images, linked libraries, or absolute paths were added.
- Did not alter roof planes, eaves, or openings. The available saved imagery supports the broad two-volume hipped-roof interpretation but not more exact roof edges, pitch, openings, or height.

## Previews

- Exterior: [refined_exterior_preview.png](refined_exterior_preview.png)
- Schematic roof-open view: [refined_schematic_interior_preview.png](refined_schematic_interior_preview.png)

## Source and identity caveat

The raw Purdue BuildingShapesZip4 FID 771 feature, source metadata, orthophoto material, and the labeled exterior photo remain in `audit/massing_islamic_societyof_greater_lafayette_0130012/sources/`. The source package documents retrieval date, projection, transform, measurement method, and uncertainty.

FID 771 is labeled “Muslim Student Association / 1021 FIRST ST.” The current [ISGL about page](https://isglclientprod.azurewebsites.net/about) lists “1022 1st St.” Purdue's 2022 [Ramadan event page](https://engineering.purdue.edu/GEP/events/2022/global-celebration-ramadan) links ISGL's location with Muslim Student Association activity. Together these support a strong physical-site match, but no exact formal parcel/name/address crosswalk is asserted. The GIS area attribute also conflicts with area measured from the returned ring; the wall ring remains unscaled.

## Evaluation handoff

The prior independent grade of 7.9/10 applied to SHA `c84126f5b1f549db17faa7282e449fc6de171e632b6e627062ad46379247c39b`. This refinement has not yet been independently graded. Request a new exact-hash review for SHA `57d4bdacd2dde6759bbc4892e153266ea0f4856368fa792179a002f5fe9f24fe`; do not reuse the prior score.
