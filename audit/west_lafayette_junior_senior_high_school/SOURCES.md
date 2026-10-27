# West Lafayette Jr./Sr. High School — evidence record

Captured 2026-10-27 UTC. Raw source snapshots and architect photographs are stored in sources/.

## Sources

| Source | What it supports | Notes |
|---|---|---|
| [OpenStreetMap way 283537867](https://www.openstreetmap.org/way/283537867) | Building identity, 34-vertex closed plan outline, building=school, building:levels=3, address and grade span | Raw API snapshot: sources/osm_way_283537867_raw.json. WGS84 coordinates transformed to the project campus frame using the origin and meter scales in modular/manifest.json. OSM is not a measured architectural survey. |
| [KJG Architecture — West Lafayette Jr./Sr. High School](https://www.kjgarchitecture.com/portfolio-1/west-lafayette-jr.%2Fsr.-high-school) | Recent additions/renovations and exterior/interior visual character | KJG lists the project as 2022 and documents the Richard Wachs Aquatic Center, James Guy Education Wing and Bob Kelly Center for Performing Arts work. Page snapshot: sources/kjg_project_page.html; downloaded project photos: sources/kjg_images/. |
| [West Lafayette Community School Corporation — Jr./Sr. High](https://www.wl.k12.in.us/jrsr) | Current school name and 1105 N Grant St address | Snapshot: sources/district_school_page.html. |
| [NCES school record](https://nces.ed.gov/ccd/schoolsearch/school_detail.asp?ID=181287002048) | Independent confirmation of school identity, address, district and grades 7–12 | Snapshot: sources/nces_school_record.html. |
| [Tippecanoe County S-4749 planning file](https://www.tippecanoe.in.gov/AgendaCenter/ViewFile/Item/7299?fileID=12113) | 2018 site plan context and aquatic-center addition planning | Snapshot: sources/tippecanoe_s4749_site_plan.pdf. This is a subdivision/site-planning file, not a building floor plan or elevation set. |

## Geometry and placement

- OSM way 283537867 is a closed polygon with 34 unique vertices.
- The 34 source points were converted from WGS84 into the campus frame (X east, Y north, Z up) from the manifest origin (40.4274, -86.9137) and project conversion scales.
- The rebuilt shell reproduces those 34 points with maximum nearest-vertex error 0.00005 m. This tiny residual is floating-point representation; OSM coordinate precision is much coarser.
- The core footprint remains in campus-world coordinates and keeps the original asset path, ID, collection and scene names. Exterior trim extends approximately 0.13 m beyond parts of the OSM wall line.
- Height is estimated, not measured. OSM tags three levels but no height. The model uses a 10.0 m wall, 10.5 m parapet and roof equipment to 11.4 m, consistent with a three-level school and the prior source envelope. No claim is made that 11.4 m is a surveyed height.
- KJG exterior images support brick, warm precast/concrete accents, a large glazed entry/curtain-wall bay, flat roof character and a planted public approach. The photo caption does not specify compass orientation; the curtain-wall bay is placed on the east street frontage as an informed but unverified placement.
- Architect photos show a library/media center, pool and performing-arts spaces, but no reliable floor plan was available to place rooms in the plan. No interior rooms are modeled. Landscaping is not added to avoid inventing site placement or duplicating master-context landscaping.

## Asset and validation

- Dedicated reproducible builder: modular/buildings/build_massing_west_lafayette_junior_senior_high_school_fa45bd1.py.
- Building asset: modular/buildings/massing_west_lafayette_junior_senior_high_school_fa45bd1.blend.
- Asset collection: Asset_massing_west_lafayette_junior_senior_high_school_fa45bd1; scene: Building_massing_west_lafayette_junior_senior_high_school_fa45bd1.
- Asset collection contains 11 mesh objects limited to the building (shell, facade bands/piers, classroom glazing/frames, entry curtain wall/canopy/doors, roof equipment). Cameras, lights and preview ground are excluded from the asset collection.
- Four Blender renders are in previews/: aerial, east, south and northwest.
- fresh_open_validate.py reopened the saved blend in background Blender and checked scene/collection contract, mesh inventory, every OSM footprint vertex and preview files. Results: validation.json; all scripted checks pass.
- Independent review is pending; no grading score is claimed yet.
