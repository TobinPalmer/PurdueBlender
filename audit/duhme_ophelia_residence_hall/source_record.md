# Duhme (Ophelia) Residence Hall — source and model record

Retrieved and inspected: 2026-10-26. Stable building ID: `massing_duhme_ophelia_residence_hall_1bb4e9c`. The source library retains the existing path and exported collection name. Geometry remains in campus coordinates for direct linking.

## Identity and geometry evidence

- **Purdue Campus GIS ArcGIS service**, layer 0 `PuGeoDB.DBO.CampusBuilding`, query `ABBR='DUHM'`, returned as GeoJSON in WGS84/EPSG:4326. Feature `OBJECTID=229`, abbreviation `DUHM`, name `Ophelia Duhme Residence Hall`, address `209 N. Russell Street`, historic `buildingidlong=351`; source service geometry is Web Mercator / WKID 102100. Raw query response: `sources/purdue_gis_query_1.geojson`; query URL and response metadata: `sources/metadata.json`. The footprint ring was transformed with the project’s local approximation (origin latitude 40.4274, longitude -86.9137): X=(lon+86.9137)*111412.84*cos(40.4274°), Y=(lat-40.4274)*111040. The transformed roof-outline polygon bounds are X [-628.851, -561.516] m and Y [-219.112, -184.081] m, planar area 1051.623 m². GIS-native Shape.STArea is 1817.801 in its stored units and is kept separately; the native area attribute is not treated as a comparable measurement after reprojection.
- **Purdue Historic Database description** embedded in the GIS feature: four-story brick, stone, and reinforced concrete; historic central portion 42 × 32 ft, two 42 × 109 ft wings; fireproof roof; opening year 1934; dedication 1934-10-20. This supports the U-shaped plan and the material / height form, but does not provide a surveyed wall plan or roof heights. The description and identifier are preserved in the raw ArcGIS response.
- **Purdue University Archives and Special Collections**, photograph PPBUC01766, “Duhme Hall Exterior,” captured 2004-06-24; raw image `sources/purdue_archives_ppbuc01766.jpg`. The image supports red brick, steep gables, a central projecting bay, stone-trimmed entry, chimneys, and repeated vertically oriented windows. It is a photograph, not a measured elevation.
- **Purdue VPSA / CARE**, “CARE Provides Network of Support for Boilermakers,” image `duhme-sq.jpg`; source image `sources/purdue_duhme_sq.jpg`. This closer facade view supports the stone bay window, high central gable, round-headed entrance, limestone detailing, and brickwork.
- **RG Collaborative**, “Purdue University — Duhme Hall” project page, image `Image1-optimized.jpg`; saved as `sources/rgcollaborative_image1.jpg`. This is a renovated reading/living room reference only. Its page states that Duhme’s historic living room features bookcases and a stone fireplace and that oak/poplar woodwork was refinished; those details inform the schematic common room.
- **Purdue Office of Emergency Preparedness**, Duhme BEP, address 209 N Russell Street and building description; source URL and retrieval date in `sources/metadata.json`. It reports four stories, a ground floor and partial basement, resident rooms on floors 1–3, and 84 student rooms. These are program/context facts, not a publicly available floor plan.

## Changes from the original single-mesh massing

- Replaced the single rectangular prism with a continuous plan-derived U-shaped wall and foundation following the Purdue GIS ring, with a triangulation that preserves the open courtyard.
- Added a four-level red-brick exterior, stone foundation and belt courses, repeating framed windows, slate gable roofs over the central block and both wings, roof seams, chimneys, attic openings, and limestone verge details.
- Added the source-supported central projecting bay and round-headed entrance with stone surround, plaque, stair/rail approach, and exterior lanterns.
- Added schematic interior floor surfaces, a main living room/fireplace/lounge, corridor and room partitions, and representative beds, desks, wardrobes, and doors. No public floor plan was located; exact room layout and the modelled residential room arrangement are inferred and schematic.
- Added procedural brick courses with meter-based UV mapping. All model materials are internal/procedural; the saved library reports no external image texture dependencies.

## Measurements and uncertainty

- Source footprint: verified identity and plan position by a named Purdue GIS feature; transformed bounds above. The mapped roof outline is not a surveyed wall line. Decorative steps, the entry projection, roof overhangs, and corner detailing extend beyond the structural footprint by design.
- Plan shape and orientation: verified against the source feature ring; the project coordinate transform is a local approximation, not a survey CRS.
- Height: estimated. Purdue confirms four stories and historic fireproof roofing; the modeled ridge is 15.84 m. No height, roof profile, or eave survey was found.
- Facade: red brick, stone trim, gables, central bay, arched entry, and chimney locations are photograph-supported. Exact window spacing, stone band dimensions, hidden-side elevations, and renovations are approximated from the available images.
- Interior: schematic and not verified against a plan. Source room counts/program descriptions do not establish a detailed arrangement.

## Review artifacts

- `build_report.json` — collection count, bounds, materials, and dependency scan.
- `independent_grade.md` and `independent_grade.json` — independent review of the exact SHA-256 revision.
- `fresh_reopen_validation.json` — saved-library reopen and export checks.
- `exterior_candidate.png`, `front_candidate.png`, and `interior_cutaway_candidate.png` — evidence views. The interior cutaway is schematic and intended to expose modelled rooms/furnishings.
