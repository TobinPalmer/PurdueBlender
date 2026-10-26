# Earhart Hall asset evidence

**Asset:** `modular/buildings/massing_earhart_hall_0f14209.blend`  
**Stable ID:** `massing_earhart_hall_0f14209`  
**Validation:** Opened the saved candidate in a fresh Blender 5.2.3 process; the expected scene/asset collection, modeled interior, and dining-court components were present. No external image dependencies were found. Full details and SHA-256 are in `fresh_open_validation.json`.

## Source evidence

- Purdue Building Shapes GIS layer (feature ERHT, FID 61): queried from the official Purdue ArcGIS service. The saved feature is `sources/purdue_building_shapes_erht_2026-10-26.geojson`; layer metadata and fields are in the adjacent JSON. The actual footprint ring drives the asset's local campus-coordinate footprint.
- Purdue University Residences, Earhart Hall official page: `https://housing.purdue.edu/Residences/Assignments/Earhart.html`. Its standard double-room layout informed representative two-bed/two-desk room dimensions and contents. The saved HTML and SVG are in `sources/`.
- Dave Wegiel / Pinola Photo, “Designed by Scholer: Earhart Hall,” published 2026-10-12: `https://pinolaphoto.com/2026/10/12/designed-by-scholer-earhart-hall/`. The saved photo shows the brick residential tower, window rhythm, and glazed dining-court frontage. Saved locally in `sources/` for review.
- AECME, Purdue University Earhart Residential Renovation: `https://aecme.com/project/purdue-university-earhart-residential-renovation/`. The project description refers to renovation of floors 1–8 in the west tower.
- The Odyssey, 2015 Earhart photograph: `https://www.theodysseyonline.com/what-you-top-dorm-choice-says-about-you`. Saved locally in `sources/`; used as supplementary visual evidence for the dining entrance and exterior sign context.

## Interpretation and limits

- The source footprint and coordinates are authoritative GIS geometry; the mesh simplifies the ring with a 0.75 m tolerance. The build report records source and simplified vertex counts and final bounds.
- The service reports eight level fields (`F01`–`F08`, `CountOfFLO=10` also appears) but also has `NUM_LEVELS=10`. AECME independently describes floors 1–8 for the west tower. The modeled eight-floor, 24.75 m height is therefore an explicit estimate, not survey data. The GIS `R=81.1` field has no documented unit; conversion from feet was used as a plausibility check only.
- Window spacing, limestone accent coverage, entry canopy proportions, dining interior layout, and representative residential-room interiors are inferred from available photographs and the official room plan. They are not architectural construction drawings.
- The building is modeled as a readable exterior and representative interior for campus-scale visualization. Procedural brick/stone materials are generated in Blender; no third-party texture files are required.

## Renders

- `exterior_preview.png`: overall massing, footprint, facade, repeated windows, and dining court.
- `dining_court_entry_preview.png`: fresh-open view of the ground-floor dining entrance.
- `footprint_plot.png`: GIS ring and footprint reference visualization.
