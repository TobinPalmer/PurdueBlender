# Current Latino Cultural Center — build handoff

**Candidate:** `modular/buildings/massing_latino_cultural_center_lcc_9cc71b3.blend`  
**Stable ID / collection:** `massing_latino_cultural_center_lcc_9cc71b3` / `Asset_massing_latino_cultural_center_lcc_9cc71b3`  
**Current identity:** Purdue Latino Cultural Center, 426 Waldron Street, FID 925.  
**Prepared:** 2026-10-26.  
**Candidate SHA-256:** `277F47A7941B785E9ABC9D3D799CAE65BA3872F7F78CB4D2420C68A5E913310A`

## Model changes

Replaced the one-box, 16 m fallback massing with a source-based one-story house form. The library now has a GIS-derived footprint; white clapboard wing surfaces with horizontal seams; a vivid turquoise brick front; yellow trim; pink entry door; multipane windows; gray shingle roof, dormer and chimney; entry ramp, stairs and center sign. Procedural materials are self-contained; there are no external image-texture dependencies. The asset collection contains 426 objects (423 meshes and three text curves). The camera, lights and render-only context remain in separate collections and are not part of the exported asset collection.

The interior is furnished as a **schematic**, not an asserted floor plan: lounge seating, a gathering table with chairs, conference furniture, bookshelves, three computer stations, and a staff kitchenette. Purdue documents these room types and the gathering-room photograph shows a round table, chairs, warm-red walls, a blue adjoining room, and hardwood floors. No dimensioned current floor plan was found, so room locations and partition dimensions remain estimates.

## Source evidence

- **Official current identity and facade:** Purdue LCC homepage, with current address and exterior hero image; page metadata says last modified 2026-07-02, accessed 2026-10-26. Saved as `sources/purdue_lcc_current_2026-10-26.html`; the hero image is `sources/purdue_lcc_house_hero_1200x600.png`. [Purdue LCC](https://www.purdue.edu/lcc/)
- **Footprint and one-level record:** Purdue BuildingShapesZip4 ArcGIS feature service, FID 925, “Latino Cultural Center at Purdue,” 426 Waldron Street, one level; retrieved 2026-10-22. Raw query response saved as `sources/purdue_building_shapes_lcc_all.json`. Input CRS EPSG:4326; vertices converted with the project transform in `modular/AGENTS.md`. [Purdue GIS feature service](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0)
- **Facility inventory / interior evidence:** Purdue LCC facility page (last modified 2021-08-24), accessed 2026-10-26, lists the Maricela Alvarado Lounge, Gathering Room, Conference Room, ITaP lab, library, kitchen, and ramp access. The page snapshot and gathering-room photo are in `sources/`. [LCC Facility](https://www.purdue.edu/lcc/center/facility.php)
- **Current house and garden character:** Purdue College of Agriculture story dated 2023-10-11 describes a multicolored house and community garden. Its page and garden image are saved in `sources/`. [Cocina con Carina](https://ag.purdue.edu/news/2023/10/cocina-con-carina-how-a-garden-connects-agriculture-food-and-heritage.html)
- **Address cross-check:** Purdue Campus Map and Resources PDF, saved as `sources/purdue_campus_map_resources.pdf`, lists the LCC at 426 Waldron Street. [Purdue campus map](https://www.purdue.edu/campus-map/)
- **Aerial context:** Esri World Imagery FID925 tiles and service metadata are copied into `sources/`. The service is a mosaic of imagery with varying dates, so these tiles support visual context only; they do not establish a capture date.

## Geometry and validation

The asset retains the manifest's massing convention: object geometry stays in campus coordinates and the collection placement transform remains identity; there is no local-origin recentering. The GIS building polygon itself converts to approximately X `[-342.732, -324.817]` m and Y `[173.435, 183.353]` m. The replacement collection, including roof overhangs and the front approach/sign, has world bounds X `[-342.732, -324.537]` m, Y `[169.777, 183.733]` m, Z `[0.010, 7.470]` m. Eaves are modeled at 3.35 m; the main roof ridge at 5.78 m and east-wing peak at 4.92 m are estimates from imagery, not measured heights.

Fresh-open check completed with Blender 5.2.3 LTS: the saved library opens; the expected scene and collection exist; the collection has 426 objects / 423 meshes; bounds recalculate to the values above; no image-texture nodes are required. A second render from the freshly opened file is saved as `renders/lcc_426_waldron_fresh_open.png`.

Rendered views:

- `renders/lcc_426_waldron_exterior.png`
- `renders/lcc_426_waldron_aerial_cutaway.png`
- `renders/lcc_426_waldron_interior_schematic.png`
- `renders/lcc_426_waldron_fresh_open.png`

## Coordinator integration notes

- Keep the stable ID, asset path, scene name, and collection name. Relink/reload the same asset collection once in the master; do not integrate the historical FID743/600 N Russell asset as the current LCC.
- Preserve the identity placement (the library continues to use campus coordinates and identity collection transform). No master origin/marker move is proposed.
- The source polygon's converted bounds are smaller east-west than the old fallback asset. Proposed master/audit bounds should reflect the new collection extents above: particularly the eastern edge moves west from the old massing's `-320.737 m` to `-324.537 m`, and model height drops from the unsupported `16 m` to `7.47 m`. The southern bound includes the approach/ramp/sign; the GIS footprint itself begins at Y `173.435 m`.
- README crosswalk currently has the two LCC assets under FID743 and leaves FID925 without a direct crosswalk. Coordinator should map this asset to FID925 and leave the FID743 disposition for separate scope reconciliation.

No README, manifest, BUILDINGS index, TODO, master blend, old FID743 asset, or other shared files were changed. This is a reviewable candidate; independent grading remains pending.
