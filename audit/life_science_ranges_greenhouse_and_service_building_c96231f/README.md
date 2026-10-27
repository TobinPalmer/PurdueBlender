# Life Science Ranges greenhouse and service building (FID 915 / LSR)

## Current candidate

- Asset: `modular/buildings/massing_life_science_ranges_greenhouse_and_service_building_c96231f.blend`
- Builder: `modular/buildings/build_massing_life_science_ranges_greenhouse_and_service_building_c96231f.py`
- Stable library collection: `Asset_massing_life_science_ranges_greenhouse_and_service_building_c96231f`
- Current asset SHA-256: `B90ADA781E76E8C7C3A08B59D95A28CD97CFA763C59D09278DDDA99781F0707E`
- Candidate GIS overlay: `previews/candidate_gis_footprint_overlay.png`
- Reproduction script and numeric results: `make_candidate_gis_overlay.py` and `candidate_gis_overlay_metrics.json`
- Full source register: `source_provenance.json`
- Current independent grade: 7.5/10; re-grade is pending after this revision.

The overlay uses the **current candidate's** seven greenhouse row rectangles and service-wing rectangle, read directly from the literal coordinates in the assigned builder. It draws those in cyan/amber over the official FID 915 polygon in magenta on the georeferenced Esri image crop. It does not use the retired massing outline. Running the overlay script regenerates the image and computes intersection-over-union (IoU) with Shapely in the project's approximate local meter coordinates. Current result: candidate union 7,705.82 m², GIS polygon 7,305.66 m², intersection 7,008.41 m², union 8,003.07 m², IoU **0.875716**. The candidate consists of eight rectangles; the GIS polygon has an outer ring and an internal ring. This is a roof/building-footprint comparison, not an as-built wall survey.

## Position and local bounds

The official feature's projected envelope midpoint defines the proposed asset placement origin **X -440.051723 m, Y -545.214899 m**. The asset geometry is local to that origin. GIS envelope bounds in asset coordinates are X `[-47.3750, 47.3750]` m, Y `[-61.0906, 61.0906]` m. The saved asset's object bounds are about X `[-47.485, 47.612]` m, Y `[-61.201, 61.201]` m, Z `[0, 7.875]` m, including small concrete curbs, coping and equipment. The proposed origin still needs to be applied and checked by the master owner; this revision does not touch the master, manifest, or placement marker.

## Height: source attribute versus model estimates

Purdue GIS FID 915 lists `NUM_LEVELS=2`, `CountOfFLO=2`, `Extrution=12`, and `Elevation=620.1`. The layer schema exposes `Extrution` as a nullable integer, but gives no field description, units, domain, vertical datum, or definition. Therefore **12 is preserved as a raw GIS attribute, not interpreted as 12 meters or any measured building height**. The two level-count fields are counts, not vertical dimensions. `Elevation=620.1` is not used as building height because its vertical units/datum are also undocumented.

All vertical dimensions in the candidate are labeled estimates. Greenhouse eaves are modeled at 3.65 m and ridges at 5.95 m; the service-wing shell is modeled at 6.8 m; the total candidate bound reaches 7.875 m with rooftop equipment. These proportions are inferred from available photographs and are not measured. No dimensioned as-built elevation or section was found in the reviewed source packet. The builder writes these distinctions into the asset collection's custom properties.

## Modeled features

Seven greenhouse roof blocks follow the visible ranges in the aerial crop, with pitched multi-span glass roofs, repeated metal frames and mullions, roof vents, gables and concrete sills. A service wing has brick, curtain wall, service doors, louvers, HVAC equipment, drainage and a sign. Interior detail includes room dividers, benches, trays, plants, grow lights and a phenotyping conveyor. Purdue's 2026 article supports the conveyor, brick-backed air-conditioning units, LED lighting and humidification technology; precise object dimensions and positions remain plausible reconstruction.

## Provenance and uncertainty

`source_provenance.json` lists every source used in this candidate with provider, exact source URL, saved snapshot, retrieval date, source publication/edit date when available, CRS, measurement method and uncertainty. Key sources are:

- Purdue BuildingShapesZip4 GIS FID 915 (`LSR`, Life Science Ranges, 180 S Russell Street), with saved layer metadata and GeoJSON snapshot. The GIS geometry anchors location and the horizontal envelope.
- Esri World Imagery crop `sources/esri_world_imagery_2026_extent.jpg`, with the EPSG:4326 crop extent recorded in both the builder and overlay metrics. Its mosaic acquisition date is unknown; use it for plan interpretation only.
- Purdue's 2022 Board project-approval packet and Exhibit A for project location, AAPF connection and greenhouse function. It is a planning exhibit, not an as-built drawing.
- Purdue's greenhouse information page/aerial and its April 27, 2026 article/photos for facility identity, current context, greenhouse materials and equipment. Photographs are unreferenced and do not establish metric dimensions.

The earlier `previews/gis_footprint_overlay.jpg` remains as historical evidence of the retired massing mismatch; it is not the current candidate overlay. Room arrangement, exact roof geometry, service-wing proportions, equipment positions and every height remain estimates. The current overlay/IoU documents the candidate's reconstructed roof blocks against the official GIS footprint; it does not verify the master placement instance.

## Review renders

- `previews/candidate_gis_footprint_overlay.png` — current candidate against GIS FID 915
- `previews/exterior_oblique.png`
- `previews/roof_plan.png`
- `previews/interior_research_bench.png`
