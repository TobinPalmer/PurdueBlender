# Campus accuracy reference

Retrieved 2026-10-22. The official Purdue campus map at https://www.purdue.edu/campus_map/ redirects to the Purdue University ArcGIS app `d7e5d06fb5344f5fb53819c42d3e91ed`. That app explicitly configures its Campus Buildings search against https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer . Layer 0 is polygon geometry, and its public query returned 946 features without a transfer-limit flag. The raw WGS84 snapshot is preserved in `official_purdue_buildings_wgs84.json`.

`build_reference.py` converts these polygons into the **existing project's coordinate convention**, preserving interoperability: origin 40.4274 N, -86.9137 E; x east, y north, metres using 111040 m/degree latitude and 111412.84*cos(origin latitude) m/degree longitude. This is a local linear approximation, not an EPSG projected CRS. Do not independently change its origin or scale in individual assets. The converted reference includes 508 polygon features inside the project area, official codes/names/FIDs, full rings, a bounding rectangle, and a minimum-area rotated rectangle. Rings, not centroids, are the alignment target; centroid differences alone do not prove displacement because asymmetric wings and courtyards change centroids.

## Detailed building matching

| Model token | Official code |
|---|---|
| WALC | WALC |
| Beering | BRNG |
| South Hall | SH |
| Ross Ade Stadium | STDM, STDM1, STDM2, STDM3, STDM4 (review together) |
| Winifred Parker | PKRW |
| Frieda Parker | PKRF |
| Elliott | ELLT |
| University Hall | UNIV |
| Neil Armstrong | ARMS |
| Tarkington | TARK |
| Owen | OWEN |
| Mackey | MACK (polygon includes associated irregular envelope; inspect arena separately) |
| Memorial Union | PMU (PMUC separately if present) |
| Stewart | STEW |
| Hovde | HOVD |
| Class of 1950 | CL50 |
| Armory | AR |
| Mathematical Sciences | MATH |
| Haas | HAAS |

## Concrete findings

The base importer `build_campus_base.py` takes OSM footprint data, but assigns many heights using guessed categories: default university 16 m, ordinary houses 7.5 m, residence halls 28 m, Beering 48 m, or floor counts times 3.8 m. These heights are not measured evidence. The detailed generators similarly contain handcrafted dimensions; prior reports describing them as accurate are not proof of surveyed accuracy.

Current scene root anchors versus the official largest-ring centroids: MATH root (-180.62,-127.29) vs (-176.625,-130.562); HAAS root (-221.45,-64.02) vs (-223.936,-63.594); CL50 root (-115.19,-116.95) vs (-116.341,-115.994). These are review flags, not automatic translation instructions. Hovde and Armory root offsets are under 1 m, but envelope matching is still required. Hovde's generated main wall 71x21.6 m is not the same envelope as the official footprint's rotated rectangle ~70.38x24.68 m (portico, steps, and outline definitions must be checked before resizing).

## Acceptance and uncertainty

1. Compare each exterior footprint (excluding ground aprons, interior furniture, cameras, poles, vegetation, and surrounding plaza) to official rings in world coordinates. Report translation, orientation, footprint area overlap, and wall-edge errors. A mesh bounding box containing site furniture is unsuitable.
2. Distinguish a rigid placement correction from actual shell shape/size correction. Never squeeze a complex irregular shell to a bounding rectangle and call it accurate.
3. Keep source FIDs and match evidence with each asset; unresolved name matching stays unresolved. For unnamed houses, use spatial overlap/proximity and explicitly label uncertain assignments.
4. The official public campus map is stronger evidence than generated source comments or OSM, but is not a certified survey. No horizontal accuracy tolerance is documented in this service. Campus changes after its last edits may exist.
5. Official `NUM_LEVELS` is a floor-count attribute. `Extrution`, `R`, and other floor values have no verified units or accuracy here; do not use them as measured building heights. Full 3D dimensional verification needs architectural elevations, trustworthy plans, or dated LiDAR/photogrammetry with documented datum and uncertainty. Existing height defaults and invented interiors remain unverified.

This audit establishes an authoritative 2D reference and documents limitations. It does **not** certify every building or its complete dimensions as fully accurate.
