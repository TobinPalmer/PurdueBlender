# Alpha Sigma Phi (Alpha Pi) — evidence and review

**Stable asset:** `modular/buildings/massing_house_301841603_654031c.blend`  
**Asset collection:** `Asset_massing_house_301841603_654031c`  
**Purdue GIS feature:** BuildingShapesZip4 FID 763 (`Alpha Sigma Phi`, 951 David Ross Rd)  
**Retrieval date:** 2026-10-26

## Source-backed geometry

The official Purdue ArcGIS polygon is stored in both WGS84 query form and its native Web Mercator form under `sources/`. All eight ring vertices were used directly in the project’s documented lat/lon-to-campus XY approximation. Fresh-open validation finds an 0.000062 m maximum vertex discrepancy. The imagery overlay at `sources/esri_world_imagery_fid763_footprint_overlay.png` shows the GIS ring following the L-shaped roof in recent Esri aerial imagery. `Shape__Area` and `Shape__Length` are native EPSG:3857 map-space measurements, so they are not reported as ground area or length. The transformed ring area is approximately 595 m².

## Exterior and interior interpretation

The chapter-hosted history PDF states that the chapter moved into its current 951 David Ross Road house on September 4, 1966. A current Alpha Pi chapter listing also confirms the address, but did not provide a usable target-facing facade image. Recent Google Street View near 999/1001 David Ross Road (viewer imagery labeled April 2026) was consulted for current fraternity-row context. It is not a direct target-house elevation: trees and neighboring buildings obscure the target. Facade finish, window rhythm, roof parapet, canopy, and entry placement are therefore visual estimates.

Purdue Libraries indexes “The Seven houses on David Ross Road (photos),” *Purdue Alumnus*, January 1968, p. 4. I followed the official Past Issues link to the digital archive, but the scan host blocked retrieval from this session. The index entry contains no scan, caption, or house order, so this historical item cannot yet identify the 951 David Ross facade or resolve its form. Its search snapshot and exact record are documented in `sources/` and `source_provenance.json`.

The GIS feature's `Extrution=34` has no unit in the layer metadata; it is not treated as a feet measurement. Instead, the 2018 Indiana 3DEP LiDAR tile covering the exact footprint was queried in the LAS coordinate system. Within the official GIS ring it contains 1,412 unclassified surface returns and no class-6 building returns. Their median is 698.34 ft; nearby class-2 ground returns have a 665.35 ft median, yielding a 10.06 m roof-surface estimate. The 5th-to-95th roof-return range is about 2.08 m, while a plane fit is weak (`R²=0.089`), so this does not resolve roof pitch or the wall-to-roof edge. This point-cloud proxy supports the approximate vertical envelope but is not a measured wall height; its uncertainties include unclassified returns, roof-edge effects, and the 2018 collection date.

Purdue GIS also reports `NUM_LEVELS=1` and `CountOfFLO=1`, so the model's three-level window rhythm remains uncertain. The 1979 Alpha Sigma Phi chapter report describes Alpha Pi's 80-man house, a new trophy case, a new social-room floor, and a redecorated ladies' room. Its page 4 photo is captioned as a hallway in Alpha Pi at Purdue. A 1976 chapter report describes living-room carpet, dining-room drapes, and an electric sign. These are historical interior-use/material clues, not a floor plan or present-day condition record. The model now includes a representative hall, social room/trophy case, dining/kitchen, and restroom; their positions remain illustrative.

The interior is schematic. A public floorplan was not found; the GIS floorplan attribute points to a private `G:\GIS\web_pages\html_pages\SOASF.html` path. The model uses ground-floor kitchen/dining/lounge furnishings and upper-floor room partitions, beds, desks, and stairs to make a representative residence interior. Do not treat those room locations as the real Alpha Sigma Phi floor plan.

## Rebuild and checks

- `../../modular/buildings/build_massing_house_301841603_654031c.py` — deterministic asset builder; preserves the stable library ID/path/collection and direct campus coordinate frame.
- `fresh_open_validation.json` — reopened asset identity, footprint-vertex match, bounds, material list, and renders.
- `lidar_height_evidence_2018.json` — the exact 2018 Indiana 3DEP COPC tile's coordinate systems, point classification/query method, and roof/ground height estimate.
- `previews/alpha_sigma_phi_exterior.png` — exterior review render.
- `previews/alpha_sigma_phi_interior_cutaway.png` — orthographic, shadow-free, evidence-labeled illustrative ground-floor cutaway; review-only palette/labels improve readability and are not saved in the asset.
- `render_validate.py` — fresh-open render and geometry validation driver.

The source building asset is ready for an independent evaluator. This subtask did not modify the campus master, manifest, README, shared verification, or any other building asset.
