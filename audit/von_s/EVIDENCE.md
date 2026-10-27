# Von's Shops building evidence

Retrieved/reviewed 2026-10-26. Assigned stable asset: `massing_von_s_d207e41`; scene `Building_massing_von_s_d207e41`; collection `Asset_massing_von_s_d207e41`; object `Von's`.

## Identity and selected structure

The assigned shape is the single retail building footprint tagged `name=Von's` in OpenStreetMap way **116427236**. The transformed eight-vertex ring and source properties are preserved in [`sources/osm_way_116427236_footprint.json`](sources/osm_way_116427236_footprint.json). Its transformed bounds, X 390.010–433.611 m and Y -416.933–-389.306 m, match the original assigned massing mesh. This identifies the correct Von's structure rather than a nearby Von's-associated property: the OSM feature is a single distinct building polygon, and the local campus snapshot has no Von's property on the neighboring building ways.

Von's official [Business Info page](https://www.vonsshops.com/business-info) lists the present bookstore at 315 W State Street, West Lafayette. The official [history page](https://www.vonsshops.com/history) describes the main building as a mixed-use property with retail departments and apartments on upper floors, and separately mentions other Von's buildings. The selected footprint is the OSM feature explicitly named “Von's” at the official storefront address; the model does not claim to cover every Von's-associated building or the former Dough Shack/Jimmy John's footprint.

## Facade and use evidence

The official [Von's Products page](https://www.vonsshops.com/products) currently publishes a storefront photograph (image `IMG_0619_edited_edited.jpg`, linked from that page; photograph date is not provided). It shows a red-brick street-corner building and a hand-painted wall sign reading “Von's Shops” with stacked department labels for books, records, gifts/cards, beads/jewelry, and T-shirts/comics. Small openings and a window air-conditioning unit are visible. These details support the warm red-brick material, the compact category mural, retail glazing, and one window AC unit in the model.

Official sources do not publish a measured elevation, construction drawings, a roof plan, or floor plans for this building. The address-level [public parcel summary for 315 W State](https://www.countyoffice.org/property-record-315-w-state-st-west-lafayette-in-47906-7a6/) reports brick exterior and a one-story assessment, while Von's official history reports apartments on upper floors in the main purchased building. The parcel summary is a secondary aggregator and may describe only part of the connected property. This conflict and the multiple connected Von's uses mean the number of floors and exact vertical boundaries cannot be treated as measured. The delivered 8.45 m parapet height, two-level facade rhythm, window sizes/locations, flat roof, and parapet are **schematic estimates**, not verified dimensions. No interior was modeled because no public plan evidence was found.

## GIS geometry and projection

- Source snapshot: `purdue_campus_buildings.json` already in the repository; Overpass OSM snapshot timestamp `2026-10-22T03:45:50Z`.
- Feature: way 116427236, tags `{building: retail, name: Von's}`.
- Source CRS: EPSG:4326 (WGS84 longitude/latitude).
- Project approximation (documented in `modular/AGENTS.md`): `X=(longitude+86.9137)*111412.84*cos(radians(40.4274))`; `Y=(latitude-40.4274)*111040`; metres; Z up.
- Measurement: transform the raw closed OSM ring without simplification. The assigned massing's eight-edge perimeter and projected bounds match the transformed ring; the actual building footprint has not been surveyed independently.

## Modeling and limits

The builder preserves the assigned file, scene, collection, and object names. It creates a joined, portable mesh with procedural UV-mapped brick, a flat roof/parapet, ground-floor retail glazing, smaller upper-story windows, the photographed department mural, and the visible window AC detail. The storefront and upper window layout is illustrative: the photo does not provide enough views to determine every opening or which upper facade bays are windows. Textured signs are modeled as geometry; no external texture/font files are required. The asset remains in campus-world coordinates.
