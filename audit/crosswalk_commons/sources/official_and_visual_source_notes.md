# Crosswalk Commons source notes

Retrieval date: 2026-10-26. These notes summarize primary sources and the retained raw snapshots in this directory.

## Footprint and identity

- OpenStreetMap API way 231217849, `Crosswalk Commons`, address tags 925 Hilltop Drive, West Lafayette, Indiana, website `https://www.crosswalkcommons.com/`. Full way and member nodes are preserved in `osm_way_231217849_full.json`.
- OSM way timestamp: 2022-06-15T05:20:14Z. Source CRS: WGS 84 / EPSG:4326. The closed ring has 14 vertices. The project conversion is approximate: X = (longitude + 86.9137) * 111412.84 * cos(radians(40.4274)); Y = (latitude - 40.4274) * 111040.0. Resulting plan area is approximately 1,023.7 m² and bounds are X -864.262 to -798.924 m, Y 788.073 to 815.889 m. It matches the original asset's footprint extent; these are map-derived, not survey-grade measurements.
- Crosswalk Commons official contact page: `https://crosswalkcommons.com/contact-on-campus-housing-west-lafayette/`, identifies 925 Hilltop Dr, West Lafayette, IN 47906. The home page snapshot `crosswalkcommons_home_2026-10-26.html` describes the property as suite-style student housing and notes its paved parking lot. The home page itself does not provide dimensions or floor count.
- Tippecanoe County government PDF, `https://www.tippecanoe.in.gov/DocumentCenter/View/39966/Hi-ViNE---West-Lafayette`, p. 19, table of campus-proximate apartment complexes: Crosswalk Commons, 925 Hilltop Dr, year 2013, 32 units, 118 bedrooms, entertainment room. The report supports identity and approximate development date, not building geometry.

## Exterior appearance

- Crosswalk Commons official gallery, `https://crosswalkcommons.com/gallery/` (copyright 2023). Exterior stills are preserved as `exterior_stills_1_2023.jpg` through `exterior_stills_4_2023.jpg`, downloaded from the gallery's direct image links. Individual photograph dates are not stated.
- The exterior images show a three-level residential block with a low/flat roofline, beige horizontal lap siding, red-brick wall fields and pilasters, stone-clad entrance and end wall, dark horizontal fascia, a glazed ground-level common/lobby area, and repeated vertically proportioned windows. The model uses these visual observations for broad facade rhythm and materials only. Exact window size/spacing, facade orientation, entry position, floor-to-floor heights, and roof height are unverified.
- Architect project page: Design Collaborative, `https://designcollaborative.com/dc-project/purdue-university-crosswalk-commons/`. The page identifies the project in West Lafayette and describes a student-housing/community destination with shared gathering spaces. The site refused a direct local HTML request during retrieval, so no claim is made that a raw page snapshot was saved.

## Modeling decisions and uncertainty

- The model retains OSM's projected 14-point campus-coordinate outline and the stable scene, collection, and object names. It does not relocate the massing asset.
- Three visible storeys are interpreted from the official exterior images. A 9.5 m parapet top is an estimate derived from that storey count, not a measured elevation. The County report provides no story count or elevation.
- Roof is represented as a simple flat/parapet silhouette because the photos do not document rooftop equipment or a pitched roof. The exact entrance side/position is not georeferenced by the images; its small stone portal/canopy is approximate.
- The photos depict multiple facade zones; the model approximates the brick, stone, siding, metal fascia, and glazing arrangement. Fine facade details remain unverified.
