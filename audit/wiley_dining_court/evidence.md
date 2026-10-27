# Wiley Dining Court (WDCT) — asset rebuild and source evidence

## Result

- Asset: `modular/buildings/massing_wiley_dining_court_wdct_8a6c669.blend`
- Stable asset ID, scene, collection, file path and root object name preserved.
- Candidate SHA-256 (fresh-open validated): see `fresh_open_validation.json`.
- Stable root: `Wiley Dining Court (WDCT)` in `Asset_massing_wiley_dining_court_wdct_8a6c669`.
- The model now uses detailed local coordinates in meters around the proposed marker origin below. **The shared manifest currently still classifies this asset as `massing` and gives campus-world bounds.** The master coordinator must change its linking/placement entry to a detailed asset and place the `Placement_massing_wiley_dining_court_wdct_8a6c669` marker at the proposed origin before integrating this file; this task deliberately did not edit the manifest or master.

## Identity and sources

Purdue BuildingShapes feature layer FID **649**, abbreviation **WDCT**, identifies `Wiley Dinning Court`, Purdue-owned, at `498 N Martin Jischke Drive`. The underlying layer is Web Mercator (WKID 102100 / EPSG:3857); the feature request was returned in EPSG:4326. Raw response and layer metadata were retrieved 2026-10-26 in `sources/`. The GIS attribute spelling “Dinning” is preserved here as source data.

Purdue's October 2, 2008 dedication page independently says the court is just south of Wiley Hall, is freestanding, seats 500, and has a brick lodge-like exterior, large windows, and vaulted wood ceilings. Purdue Dining's current location page lists 498 **S** Martin Jischke, whereas GIS says 498 **N**; this address suffix conflict is recorded. The GIS identity, on-campus position, WDCT code, and adjacency to Wiley Hall align, so the feature match is strong. The 2008 Purdue exterior photo and Fink Roberts & Petrie project images (credit Scholer Corp.) support the gable, large glazed dining bay, brick/limestone facade, timber ceiling, dining seating, and serving-counter treatment. The project engineer lists a single-story structure with basement and 500 seats. No measured floor plan, section, or elevation was found; the interior and exact elevations remain schematic/estimated.

Each source's provider, URL, retrieval date, source date (where known), source CRS, use, limitations and snapshot hash are in `sources/source_register.json`. Source snapshots are stored under `sources/`.

## Footprint, coordinates and proposed marker

Method: transform the returned WGS84 ring with the project approximation, then simplify it by 0.30 m while preserving topology. This is a local tangent conversion, not a surveyed CRS transform:

- `X = (longitude + 86.9137) * 111412.84 * cos(radians(40.4274))`
- `Y = (latitude - 40.4274) * 111040`

The resulting GIS structural footprint is **81.63 m east-west × 46.62 m north-south**, with projected polygon area 3,052.77 m². The structural shell in the asset is built from the simplified FID 649 ring. Compared against the raw GIS ring, it has 3,048.84 m² intersection and **0.9959 polygon IoU**; world bounds differ by less than 0.016 m. The long axis is approximately east-west (about 0.11° from east-west).

The proposed placement origin is the planar centroid of the transformed GIS footprint: **X = -597.574 m, Y = 124.804 m** (approximately latitude 40.428524°, longitude -86.920746°). Geometry is local to that centroid; root transform is identity. This is a practical marker proposal, not a survey point. The aerial overlay shows the detailed shell in blue against the GIS outline in red and the old rectangular massing bounds in yellow: `previews/gis_candidate_footprint_overlay.jpg`.

The layer's `Shape__Area` attribute is 5,277.14 while area recomputed from the returned ring in the project approximation is 3,052.77 m², despite metadata labeling Shape__Area in meters. I used the returned geometry for the fit and retained the area-field discrepancy as a source limitation. The current Esri imagery tile vintage is not exposed in the tile response; the overlay provides visual context, not a dated survey.

## Height and architecture

The GIS record reports `NUM_LEVELS=3`, `CountOfFLO=3`, `Extrution=36`, `B=-14.6`, `F02=16`, and `R=35`, but exposes no field domains or units for these height values. The architect/engineer description says single story with a basement. The model represents one high-volume above-grade dining hall and does not model basement geometry. Main wall/eaves height is 6.15 m; gable roof ridge is 10.85 m and decorative crest is 11.55 m. These are visual estimates, not measured elevations. If the GIS `R=35` and `Extrution=36` values happen to be feet, they would be roughly consistent with the modeled 10.67–10.97 m ridge/extrusion; that unit interpretation is unverified.

The exterior rebuild adds a textured brick wall shell, limestone base/bands/piers, dark-framed large south glazing, gabled main dining hall, lower standing-seam service roofs, secondary windows/doors, and roof mechanical boxes. These choices follow Purdue and Scholer/FRP imagery; small-window positions, exact roof-wing geometry, and roof equipment layout are interpretive.

The interior is clearly schematic and uses only source-supported program/features: an open dining room, dining tables/chairs, a ring-like set of food-service counters, terrazzo/tile circulation, exposed vaulted oak ceiling/trusses, and pendants. Station positions, furniture counts, room boundaries, and basement layouts are not claimed to match a measured plan. The cutaway interior preview is `previews/wdct_interior_schematic.png`.

## Portability and validation

- All exterior and interior materials are procedural Blender node materials; no external image texture or absolute asset dependency is used.
- The exact saved asset was reopened in a new Blender 5.2.3 process. Scene/collection/root identities and identity root transform are verified in `fresh_open_validation.json`.
- The asset has 1,054 collection objects (1,053 mesh objects), all meshes have materials, all WDCT materials use nodes, and no external image dependencies or missing paths were found.
- The saved root remains visible in viewport/render. Preview-only visibility changes were made in memory after saving and were not written back to the library.
- Preview renders: `previews/wdct_exterior_south.png`, `previews/wdct_exterior_three_quarter.png`, and `previews/wdct_interior_schematic.png`.

## Files changed in scope

- `modular/buildings/massing_wiley_dining_court_wdct_8a6c669.blend`
- `modular/buildings/build_massing_wiley_dining_court_wdct_8a6c669.py`
- `audit/wiley_dining_court/` evidence, sources, GIS overlays, validation and previews.

No shared project files, master blend, other buildings, commits, or pushes were changed.

