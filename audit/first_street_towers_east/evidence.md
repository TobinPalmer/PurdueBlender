# First Street Towers East (FSTE) — candidate evidence and limits

**Stable ID:** `massing_first_street_towers_east_fste_c9b22d3`  
**Candidate:** `modular/buildings/massing_first_street_towers_east_fste_c9b22d3.blend`  
**Build script:** `modular/buildings/build_massing_first_street_towers_east_fste_c9b22d3.py`  
**Evidence retrieved:** 2026-10-26  
**Status:** revised standalone candidate after a 7.1/10 independent review; awaiting a fresh independent grade. Not integrated into the master blend and not committed.

## Source evidence

1. **Footprint, identity, address, floor count:** Purdue BuildingShapesZip4 FeatureServer layer 0, feature `FID=651`, `BLDG_ABBR=FSTE`, `BUILDING_N=First Street Towers Eastern`, `ADDRESS=1230 1st Street`, `NUM_LEVELS=6`, `CountOfFLO=6`, and `Extrution=52`. Query: <https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D651&outFields=%2A&returnGeometry=true&outSR=4326&f=pgeojson>. Provider: Purdue University / ArcGIS FeatureServer. Retrieved 2026-10-26. Query response declares GeoJSON coordinates in EPSG:4326 (longitude, latitude). Raw snapshot: `sources/purdue_buildingshapeszip4_fste_fid651_2026-10-26.geojson`.
2. **Exterior appearance:** Purdue University Residences, “Accommodations” page: <https://www.housing.purdue.edu/visit/conferences/accommodations.html>. Provider: Purdue University. Saved page retrieved 2026-10-26 at `sources/purdue_accommodations_2026-10-26.html`; downloaded page image at `sources/first_street_towers_exterior_official_640x360.jpg` (image URL: <https://www.housing.purdue.edu/images/_hero/first-street-towers-exterior-640x360.jpg>). The page shows the overall First Street Towers complex rather than an isolated, labeled East-tower view. The visible warm brick, regular light-framed windows, and low-slope/stepped roof silhouette are therefore useful complex-level reference, not a definitive East-only elevation.
3. **Residential details:** Purdue University Residences, “First Street Towers” page: <https://www.housing.purdue.edu/my-housing/options/residence-halls/first-street.html>. Provider: Purdue University. Saved page retrieved 2026-10-26 at `sources/purdue_residence_page_2026-10-26.html`. It supports private bathrooms, floor lounges, cluster-style living, and gives an approximate single-room size of 9 ft 8 in by 13 ft 9 in. Publicly accessible material reviewed did not provide the FSTE as-built floor plan or roof plan.
4. **Opening-day design evidence (added in this revision):** Purdue News Service, “New residence hall to open at Purdue,” published 2009-08-06: <https://www.purdue.edu/uns/x/2009b/090803FrazeeTowers.html>. Provider: Purdue University; author/source attribution includes Purdue University photo/Andrew Hancock. Saved HTML: `sources/purdue_first_street_towers_opening_2009.html`. Photo at <https://www.purdue.edu/uns/images/+2009/first-street-towers.jpg> is saved as `sources/purdue_first_street_towers_2009_exterior.jpg`. The complex-level photo visibly shows brick, light window frames, gabled/peaked roof forms, and glazed entrance/lobby treatment. It is **not labeled as a view of the East wing**, so none of its entrance position or exact roof count was attributed to FSTE.
5. **Google Street View / tower-specific plan search:** Google Maps’ directly requested panorama URL could not be opened by the available browser/search tool; the official Purdue photo gallery link redirected to a Photoshelter gallery inaccessible to the retrieval tool. Search results did not expose a current, separately labeled East-tower street-level photo or an FSTE floor plan. No Street View image or East-only plan is claimed as inspected evidence.

6. **Street frontage used only to locate the entry interpretation:** OpenStreetMap Overpass road snapshot, way `5332639`, `name=1st Street`, `highway=unclassified`, two lanes: `sources/osm_roads_near_fste_2026-10-26.json`. Provider: OpenStreetMap contributors / Overpass API. OSM base timestamp: 2026-10-26T07:54:20Z; retrieved 2026-10-26. Way: <https://www.openstreetmap.org/way/5332639>. This road line is 13.06 m from the nearest point on the Purdue GIS FSTE polygon in the local project transform. It identifies the adjacent First Street frontage, but it does not show an entrance.

The official feature service is the primary footprint source. OSM is used only for the named road adjacency that guides a representative entrance placement, not as an FSTE footprint or facade source. No current, tower-specific street-level image was available to verify exact facade or roof geometry. The official Purdue 2009 photo and current Purdue Housing page are the best attributable exterior/program references found, but the exterior photo depicts the complex and does not identify the East tower.

## Coordinate and footprint method

The raw feature ring has 523 non-closing vertices, is a valid polygon, and has a projected area of 1,302.2652 m². Geographic coordinates were transformed with the project’s documented local approximation: `X=(longitude + 86.9137) * 111412.84 * cos(radians(40.4274))`; `Y=(latitude - 40.4274) * 111040`; meters; origin latitude 40.4274, longitude -86.9137. This is a local approximate geographic transform, not a survey CRS.

The wall perimeter uses a 0.30 m Ramer–Douglas–Peucker simplification to remove survey-scale zigzags while preserving the main outline. Shapely planar comparison in that same local frame produced:

- Source bounds: X `[-875.1398, -837.8526]`, Y `[-316.9298, -242.5901]` m.
- Candidate structural wall bounds: same bounds to 4 decimal places.
- Candidate simplified wall area: 1,304.5785 m² (2.3133 m² / 0.1776% greater than source).
- Intersection over union: 0.992455.
- Symmetric Hausdorff distance: 0.2537 m.

Comparison details and fresh-open geometry measurements: `validation_fresh_open.json`. The comparison concerns only the structural wall outline; the window frames, floor bands, and roof parapet intentionally extend slightly beyond it.

## Modeled details and uncertainty

- The source-backed six levels are represented with six repeated residential stories and floor plates. The roof has a low deck behind two clipped pitched roof forms and brick gable ends on the longest terminal edges; the gable language is visible in Purdue's complex-level photo, while the precise East-wing roof plan and exact gable count remain unverified.
- The modeled highest roof/gable point is 23.25 m above local ground (fresh-open mesh bounds). Floor-to-floor spacing, parapet height, and gable rise are **estimates**. The `Extrution=52` field may encode a height, but the service does not document its unit or meaning, so it was not treated as measured height.
- Exterior material is a procedural warm red-brown running-bond brick texture; pale window frames, blue-gray glazing, restrained brick course bands, and dark slate tile pattern follow the visible complex-level image. The exact FSTE elevation, bay count, and material specifications are not established by the image, and remain interpretation.
- A glazed entrance with pale portal trim, canopy, and threshold is modeled on the north-facing edge nearest First Street. The selected simplified-ring segment is 13.27 m from OSM way 5332639 and its outward normal points toward that road. The entrance/lobby program is supported by Purdue Housing descriptions and the complex photo; the exact FSTE door location and design remain **estimates**, because OSM and Purdue GIS provide no door point or tower-specific entry photo. It is not copied from the complex-wide central entry in the photo.
- Repeated windows follow the straight portions of the source boundary; the precise historic bay schedule is estimated.
- Interior includes a representative 22-room cluster per story, approximate single-room modules, private-bath partitions, doors, beds, desks, wardrobes, corridor, and a shared living/dinette with seating and television. The cluster size/program is based on Purdue's 2009 description of living rooms for clusters of 22 rooms and the current housing description of single rooms/private baths around shared living/dinette areas. Room placement and furniture arrangement are **not an as-built FSTE interior plan**.
- No exterior site works, landscape, or signage were inferred from the complex-wide photo; interior furnishings are the separate schematic described above.

## Candidate validation and evidence files

- Fresh-open validation: `validation_fresh_open.json` (reopened by a separate Blender process; scene and export collection names preserved; 87 mesh objects, 13 materials, 8,481 faces, 22,407 vertices; no external texture files). Six stories and two interpreted gable ends are modeled; the representative room cluster has 22 rooms per level.
- Exterior candidate: `fste_exterior_candidate.png`.
- Entry detail: `fste_entry_detail_candidate.png` (entry placement is marked estimated above).
- GIS outline top view: `fste_footprint_top_candidate.png`.
- Representative story cutaway overview: `fste_interior_cutaway_candidate.png`.
- Interior cluster detail: `fste_interior_cluster_detail_candidate.png`.
- Source snapshots: `sources/`.
- Fresh-open validator: `fresh_open_validate.py`.
- Builder: `modular/buildings/build_massing_first_street_towers_east_fste_c9b22d3.py`.

Candidate file SHA-256 is `7f92c5bb44c8a5d1f1f5aee145003234e0fb3dd9e6e77dc18fb2dee84dfe94ae`, also recorded in `validation_fresh_open.json`. Independent visual grading is still required; this build report is not a fidelity score.
