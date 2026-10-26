# First Street Towers West (FSTW) — standalone candidate

**Stable asset ID:** `massing_first_street_towers_west_fstw_b6c3bbe`  
**Candidate:** `modular/buildings/massing_first_street_towers_west_fstw_b6c3bbe.blend`  
**Builder:** `modular/buildings/build_massing_first_street_towers_west_fstw_b6c3bbe.py`  
**Evidence collected:** 2026-10-26  
**Status:** standalone candidate; ready for separate grading. This build did not change the master blend or shared indexes and has not been committed.

## Source evidence

1. **Footprint, identity, level count, and address:** Purdue University BuildingShapesZip4 FeatureServer layer 0, feature `FID=858`, `BLDG_ABBR=FSTW`, `BUILDING_N=First Street Towers, Western`, `ADDRESS=1270 1st Street`, `NUM_LEVELS=6`, `CountOfFLO=6`, `Extrution=49`. The query was `where=FID=858`, `outFields=*`, geometry returned in EPSG:4326, retrieved 2026-10-26: <https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D858&outFields=%2A&returnGeometry=true&outSR=4326&f=pgeojson>. Raw response: `sources/purdue_buildingshapeszip4_fstw_fid858_2026-10-26.geojson`; layer schema: `sources/purdue_buildingshapes_layer_metadata_2026-10-26.json`.
2. **Three-tower distinction:** a same-layer query captured FSTE (`FID=651`, 6 floors), FSTC (`FID=664`, 7 floors), and FSTW (`FID=858`, 6 floors) with separate footprints and IDs: `sources/purdue_first_street_towers_three_buildings_gis_2026-10-26.geojson`. FSTW was selected by exact official abbreviation/name, not inferred from a complex-wide silhouette.
3. **Independent footprint record:** OpenStreetMap way `283274997`, tagged “First Street Towers, West (FSTW),” address 1270 First Street: `sources/osm_way_283274997_fstw_2026-10-22.geojson`. This was extracted from the project’s Overpass snapshot, timestamp `2026-10-22T03:45:50Z`, preserved in `purdue_campus_buildings.json`.
4. **Exterior material and design language:** Purdue Residences, “First Street Towers” page: <https://www.housing.purdue.edu/my-housing/options/residence-halls/first-street.html>; saved as `sources/purdue_residence_page_2026-10-26.html`. The Purdue page’s complex-wide exterior hero image is <https://www.housing.purdue.edu/images/_hero/first-street-towers-exterior.jpg>, saved as `sources/purdue_first_street_towers_exterior_official.jpg` (also duplicated as `purdue_first_street_towers_exterior_hero_undated.jpg`). It supports the general connected-complex red/brown brick, pale masonry, residential-window, and gabled roof vocabulary. It does **not** unambiguously isolate a particular FSTW elevation or identify the camera direction.
5. **Close exterior detail excluded from FSTW-specific claims:** the 2019 Purdue housing image at <https://www.housing.purdue.edu/images/get-reconnected-old-images/BrianTedeschi2.JPG>, saved as `sources/purdue_first_street_towers_exterior_BrianTedeschi2_2019.jpg`, is a close view of the shared First Street Towers entry. It is not evidence for the FSTW entry location, so the model’s small courtyard-side entry is labeled illustrative rather than photo-verified.
6. **Interior use:** Purdue’s First Street page supports residential rooms arranged in clusters around a shared living/dinette area and gives an approximate single-room size of 9 ft 8 in by 13 ft 9 in. `sources/purdue_generic_residence_room_layout.svg` is the generic “Single Layout Floor Plan” illustration linked from that page, not an FSTW-specific as-built plan. `sources/purdue_first_street_towers_interior_lounge_fall2022.jpg` is a complex-level lounge reference. The building-specific partition plan is therefore schematic.

The visible public exterior reference is complex-wide, and no current FSTW-isolated street-level photo or roof plan was found. Google Street View imagery was not available as a reliable, tower-specific evidence source in this build. The facades, bay rhythm, gable roof geometry, and entry placement remain estimates. The photo supports the material palette and overall architectural family only.

## Footprint and placement

The structural perimeter is built from the official Purdue GIS feature in the project’s documented local approximation: `X=(lon+86.9137)*111412.84*cos(radians(40.4274))`; `Y=(lat-40.4274)*111040`; meters; origin longitude `-86.9137`, latitude `40.4274`. This is a campus-local approximation, not a survey CRS. The 523-vertex source ring was simplified with Ramer–Douglas–Peucker tolerance `0.28 m`; candidate wall/floor perimeter uses the resulting 68 vertices.

Fresh-open wall geometry comparison (`footprint_comparison.json`):

- Official GIS area: `1302.264 m²`; bounds X `[-1004.9239, -967.6313]`, Y `[-316.7076, -242.3680]` m.
- Candidate wall base area: `1304.578 m²`, an increase of `2.314 m²` (`0.178%`) from simplification.
- Candidate versus GIS: IoU `0.992456`; symmetric Hausdorff distance `0.2537 m`.
- OSM versus GIS: IoU `0.941541`; symmetric Hausdorff distance `1.3960 m`. OSM covers about `46.20 m²` outside the GIS perimeter, while GIS extends about `32.63 m²` outside OSM. The Purdue GIS polygon is the modeled outline; both source outlines are retained for review.

Overlay: `fstw_footprint_source_comparison.png`; rendered candidate footprint: `fstw_footprint_top_candidate.png`.

## Modeled features and uncertainty

- Six residential stories follow the official GIS attributes. Estimated floor-to-floor spacing is `3.08 m`; wall top is `18.76 m`. Estimated gable ridge rise is `3.8 m`, for a maximum roof/ridge detail height around `22.65 m`. GIS `Extrution=49` has undocumented units and meaning, so it is not treated as a measured height.
- Textured red/brown running-bond brick with pale masonry base and window surrounds, blue-gray double-light glazing, dark metal mullions, sills, restrained story courses, charcoal gabled roof slopes, ridge caps, and roof seams are built as portable procedural materials; there are no external image-texture dependencies.
- The estimated `414` repeated windows are algorithmically spaced along longer GIS perimeter segments. Exact bay count and window schedule are not documented in the public references.
- Interior floor plates and repeating room-cluster/corridor partitions are modeled for all six levels. They are a schematic residential layout, not measured interiors or an FSTW plan.
- The GIS feature’s build/occupied epoch fields indicate a 2010-era building, but no exact architectural plan or verified FSTW door arrangement was found. A small courtyard-facing entrance is an explicitly illustrative element.

## Fresh-open validation and evidence artifacts

- Fresh-open check: `fresh_open_validation.json`, produced in a separate Blender process from the saved `.blend`.
- `32` collection objects, all meshes; `19,326` vertices, `4,968` faces, `9` used materials; no external image files.
- Expected scene `Building_massing_first_street_towers_west_fstw_b6c3bbe` and collection `Asset_massing_first_street_towers_west_fstw_b6c3bbe` are present.
- Render evidence: `fstw_exterior_candidate.png`, `fstw_footprint_top_candidate.png`, `fstw_schematic_interior_candidate.png`.
- Source snapshots are kept in `sources/`. Builder and validation scripts are adjacent to this evidence report.
- The final candidate SHA-256 is recorded in `evidence.json`. Independent visual/fidelity grading is still required; this report is not a grade.
