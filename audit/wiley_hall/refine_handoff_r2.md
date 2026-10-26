# Wiley Hall R2 handoff

**Asset:** `modular/buildings/wiley_hall.blend`  
**R1 SHA-256:** `80b4e00f0537b2a78956c262ea0c0afd81f2b08cc3469a8f278ff93fbf603742`  
**R2 SHA-256:** `8f3e904273ec680811163d8150098aa0f67f55705376df86359b8510cc3a3859`  
**R1 grade:** 7.8/10; R2 independent grade pending.

## R2 change

The 680 x 660 m lawn and three large road/parking-marking meshes were identified as campus-scale context rather than verified building shell geometry. The lawn is a flat, subdivided rectangle with 4x horizontal scale; the asphalt covers a 139 x 165 m bounding box. Neither shape is supported by the Wiley Hall wall/GIS footprint. Importing these with the building collection risks overlapping master-owned terrain and roads.

I moved four objects—`Lawn | mixed summer grass.001`, `Road | aged asphalt.001`, `Road | faded yellow.001`, and `Road | parking paint.001`—to a hidden source-only collection called `Wiley_SiteContext_NotExported`. I preserved their parent, world transform, mesh, and material; I did not delete them or alter the building root. Blender saved and freshly reopened the asset with the transforms matching within 0.1 mm. The stable export collection `Asset_wiley_hall` now contains 398 objects (382 meshes, 14 empties, two text objects); it no longer exports the four campus-scale context meshes. The entrance walk, mulch, benches, local planting, trees, exterior, and interior remain with the building asset.

## Footprint and placement evidence

The raw Purdue GIS response includes both Wiley Dining Court and Wiley Hall. `footprint_bounds_r2.py` selects the correct Harvey W. Wiley Residence Hall record explicitly: layer 0 `OBJECTID 290`, abbreviation `WILY`, `buildingidlong 148`, address 500 N. Martin Jischke Drive. The queried ring has 72 non-closure vertices. Reprojected to the project's approximate local X-east/Y-north frame, its bounds are X -640.174 to -549.848 m and Y 174.493 to 293.708 m, with center (-595.011, 234.100) m. Its approximately 5,505 m² local area is consistent with the API's 9,517 m² EPSG:3857 area after the Web Mercator latitude scale factor; those area figures use different CRSs.

The main brick-shell mesh has local XY bounds X -187.636 to -107.216 m and Y -55.215 to 55.215 m. With the existing manifest origin (-447.585, 234.070) m, its bounding-box center is (-595.011, 234.070) m, 0.00003 m east and 0.0301 m south of the GIS ring-box center. Its X/Y box is about 80.42 x 110.43 m versus the GIS ring's 90.33 x 119.22 m. This supports identity and centering but is not a full structural-wall polygon overlay, proof that the GIS ring is a surveyed wall line, or evidence to rescale the shell.

I inspected the existing master marker read-only: `Placement_wiley_hall` remains at (-447.585266, 234.070374, 0) m with identity rotation/scale and still instances the relative `Asset_wiley_hall` library. I made no placement or shared-index changes. The existing `exterior_bounds_world_m` Y interval in `modular/manifest.json` is stale relative to the fresh modeled shell bounds; the coordinator owns that shared correction after acceptance.

## Fresh reopen and views

`independent_reopen_r2.json` records a fresh Blender 5.2.3 reopen of the exact R2 SHA, identity root, 398 exported objects, 382 meshes, 142 used materials, no materialless meshes, no invalid material slots, no missing external images, and the project-relative foliage-library link resolving. `site_context_reopen_r2.json` verifies the four site objects are outside the export and their parent/world transforms are preserved. The root, export-collection name, GIS building identity, and master marker were not changed.

The fresh Workbench views are [oblique R2](oblique_r2.png) and [top R2](top_r2.png). They are inspection previews, not final-render-engine output. This revision did not add geometry, modify shaders, or verify room layout; the existing interior remains illustrative and the GIS comparison remains bounding-box based.

## Evidence files

- [R2 separation log](site_context_separation_r2.json) and [fresh membership/transform validation](site_context_reopen_r2.json)
- [R2 standalone reopen and evaluated mesh bounds](independent_reopen_r2.json), [script](independent_reopen_r2.py), and [render log](independent_reopen_r2.log)
- [Correct WILY feature and model bounds comparison](footprint_bounds_r2.json), [calculation script](footprint_bounds_r2.py), and source query [snapshot](gis_query.json)
- [Read-only master marker inspection](master_placement_r2.json)
