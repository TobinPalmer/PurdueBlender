# Whistler Hall evidence register

Retrieved 2026-10-26. The official FeatureServer response and its layer metadata are preserved under `sources/`.

## Identity and campus position

- **Purdue BuildingShapes FeatureServer**, layer 0, FID 84, code `WSLR`, “Roy L. Whistler Hall Of Agricultural Research,” address 170 S University Street. Geometry was requested as EPSG:4326; layer metadata reports native/latest WKID 102100/3857. Four above-grade levels are reported by `NUM_LEVELS=4` and `CountOfFLO=4`. The raw polygon and all attributes are in `sources/purdue_fid84_whistler.json`; native layer metadata is in `sources/purdue_building_layer_metadata.json`.
  - Feature query: <https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D84&outFields=*&returnGeometry=true&outSR=4326&f=pjson>
  - Layer metadata: <https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0?f=pjson>
- Purdue’s **July 2025 official campus map** lists WSLR as Whistler Hall of Agricultural Research in grid G8. It supports the identity but not wall dimensions: <https://www.purdue.edu/campus-map/graphics/campusmap.pdf>.
- Legacy source-matching evidence had incorrectly/ambiguously proposed FID 263, Forest Products Building. Its raw response is preserved as `sources/purdue_fid263_forest_products.json`; it identifies a different building (`FPRD`, 175 Marsteller Street, two levels). This crosswalk must not be reused for Whistler.

## Exterior appearance

- **Purdue Agricultural Communication, Tom Campbell**, “Indiana expected to warm up soon in January, then get colder again,” published 2015-01-08. The article caption explicitly identifies the “Whistler Hall greenhouse”; the wider downloadable photo shows the Hall behind it. The raw photo used for visual comparison is `sources/purdue_whistler_greenhouse_2015.jpg`.
  - Article and caption: <https://www.purdue.edu/newsroom/archive/releases/2015/Q1/indiana-expected-to-warm-up-soon-in-january,-then-get-colder-again.html>
  - Image: <https://www.purdue.edu/uns/images/2015/niyogi-icicles.jpg>
- The oblique winter photo supports the general red-brown masonry, horizontal light-colored bands, grouped glazing, broad upper window band, and raised gabled roof silhouette. It is not georeferenced and does not establish exact facade orientation, dimensions, or room layout. The geometry reproduces those traits schematically.

## Interior use (not a measured plan)

- Purdue Archives’ **Roy L. Whistler Hall of Agricultural Research** record says the building houses agricultural research across several fields and contains 33 labs/laboratory complexes. The result text is recorded from the Purdue Archives search result; a direct page snapshot returned HTTP 403 during retrieval. Source: <https://archives.lib.purdue.edu/agents/corporate_entities/709>.
- Purdue Agronomy Research Facilities identifies Whistler Hall (WSLR) as one of its campus buildings with offices and laboratories. Retrieved page snapshot: `sources/purdue_agronomy_facilities.html`. Source: <https://ag.purdue.edu/department/agry/research/research-facilities.html>.
- Purdue Electron Microscopy Center directions identify the Whistler S042-S062 suite at 170 S University Street and place it in the sub-basement. Retrieved page snapshot: `sources/purdue_microscopy_directions.html`. Source: <https://ag.purdue.edu/department/arge/facilities-and-research/microscopy/microscopy-directions.html>.
- These sources establish laboratory use and one sub-basement suite, not internal room geometry. The included benches, partitions, and slabs are intentionally schematic and should not be read as a floor plan.

## Measurements and uncertainties

- Project conversion, per `modular/AGENTS.md`: `X=(lon+86.9137)*111412.84*cos(radians(40.4274))`, `Y=(lat-40.4274)*111040`; X east, Y north. This is a local approximation, not a survey CRS.
- The model is centered on the midpoint of the transformed FID 84 ring bounds at world XY `[-156.3101549801, -497.0113978049]` m (approximately lon/lat `[-86.9155430497, 40.4229240328]`). Coordinator should use this as proposed placement origin; this subtask does not modify shared manifest or master placement.
- The 31-vertex source ring is used without simplification for wall perimeter and roof outline. The computed local-plan area is 2,338.37 m². Since source `Shape__Area=4,041.85` is in native EPSG:3857, compare only after the latitude scale correction: approximately 4,034.83 m², about -0.17% from the source field. This area check is approximate and is not a separate survey measurement.
- GIS reports `Extrution=17`, but the public layer schema provides no unit definition. It is not treated as a measured height. A 16.2 m roofline is an estimate guided by four recorded floors and a typical floor-to-floor allowance; the roof elevation is **not verified**.
- The old massing was a single 52.20 m × 135.94 m × 16 m block at approximately `[-146.1075, -472.7972]` XY. That is about 26.28 m from the proposed Whistler origin and substantially larger than the official Whistler ring. The prior audit’s FID 263 candidate is Forest Products, a distinct building. This replacement intentionally follows FID 84.

## Files and review

- Builder: `modular/buildings/build_massing_whistler_hall_6f6bf8d.py`
- Asset: `modular/buildings/massing_whistler_hall_6f6bf8d.blend`
- Placement/geometry measurements: `placement.json`
- Render views: `whistler_exterior.png`, `whistler_topdown.png`
- An independent grader should check the facade against the preserved Purdue photo and confirm the coordinator’s intended use of the proposed placement origin.
