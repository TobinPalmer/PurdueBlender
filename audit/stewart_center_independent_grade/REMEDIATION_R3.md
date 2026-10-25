# Stewart Center refinement R3

## Asset and fresh reopen

- Asset: `modular/buildings/stewart_center.blend`
- SHA-256: `cf2e4c541f98329bf475229d702bc48178078571ba97b1136c9c0c5c9996535d`
- Fresh Blender 5.2.3 reopen: 1,966 collection objects / 1,954 meshes; 28 materials; no materialless meshes; no missing external images.
- `AssetRoot_stewart_center` remains identity. No master asset, marker, or campus origin was changed.
- Source GIS trace remains 53 cleaned vertices / 53 structural wall objects after splitting the south recess wall around its glass opening. Exterior trace and area (10,197.4696 m²) are unchanged. The center section is modeled as a vestibule rather than opaque brick; adjoining facade wings still follow the GIS edge.
- Fresh render files: `south_entry_r3.png` and `south_oblique_r3.png`. The Blender render camera, light, and world overrides were temporary and were not saved to the asset.

## Entrance corrections

R2's facade pattern incorrectly continued as dark square brick windows behind the six-column portico, and the entrance doors were hard to distinguish. R3 modifies the recessed south GIS edge to create a 34 m wide central opening, removes the legacy solid `STEW_Portico_Back_Wall`, and builds a recessed entrance with two glazed planes, side returns, three framed double-leaf door sets, and divided transoms. This makes the vestibule and door location legible from the south. The upper wall above the portico was restored in brick with an estimated window rhythm so the footprint does not read as an open hole above the entrance.

The 2024 Purdue entrance photograph supports a stone portico, tall glazing, a prominent entrance and broad stairs; it does not provide a scale. The 34 m opening width, vestibule depth, glazing bay spacing, upper-story window sizes, and all door dimensions are visual estimates. The GIS source supplies the plan edge and the image supplies qualitative facade character; neither supports a dimensioned elevation. No change was made to estimated overall wall or roof height.

Stair handrails now consist of continuous sloped rails that extend from the lower riser to the landing. Nine posts per side are aligned to the tread profile and meet the underside of the rail. Rail height, thickness, and post spacing remain estimated from the photograph.

## Source, coordinate frame, and uncertainty

- Exterior photo: Purdue University Events, [Stewart Center](https://events.purdue.edu/stewart_center), current page, accessed 2026-10-25; image snapshot `source_purdue_entrance.jpg`; image URL `https://localist-images.azureedge.net/photos/39883225413730/card%402x/60fde77052d4337e4859dae94db6d1ee93e2f421.jpg`. The source date and camera calibration are not supplied. Used qualitatively for entrance glazing, door/portico composition, columns, and stairs.
- Footprint: Purdue GIS feature OBJECTID 615 / ABBR STEW, local snapshot `purdue_gis_feature_615.json`, spatial reference EPSG:4326/WKID 4326; retrieved 2026-10-25 (the record does not expose an imagery/source date). The existing documented local-frame transform and GIS boundary are retained. Source segment 33 is the south recess back edge; the script opens its center for the vestibule and keeps the side wings.
- Interior plans: Purdue Road School, [2024 Stewart Center Maps](https://www.roadschool.purdue.edu/maps/2024%20Stewart%20Center%20Maps.pdf), accessed 2026-10-25. No north arrow, scale, CRS, or control points; Ringel/HSSE relative offsets remain approximate and unmodified.
- History and height: Purdue Archives, [Stewart Center corporate entity](https://archives.lib.purdue.edu/agents/corporate_entities/548), accessed 2026-10-25, supports the 1954–1958 construction period, historic University Library/Fowler Hall incorporation, and three floors in the central portion. It provides no surveyed wall or roof heights. Model wall height 16.5 m and overall height 22.5 m remain estimates.
- Roof: no accessible dimensioned roof plan or elevation found. Roof shape/elevation/equipment remain estimates; no roof equipment was added from uncertain imagery.

## Validation files

- `reopen_probe.json`: fresh reopen, hash, object types and counts, root matrix, material coverage, and missing external image check.
- `structural_wall_probe.json`: per-wall bounds; 53 wall meshes include the GIS south-edge wings split around the entrance opening.
- `building_validation.json`: updated machine-readable R3 counts, source caveats, and asset measurements.
- `render_r3.py`: reproducible temporary entry and oblique review render script.
- `south_entry_r3.png`, `south_oblique_r3.png`: fresh views of the saved R3 file.

R2's 7.3/10 grade is retained as historical. The current asset is ready for a fresh independent R3 review; no R3 score is claimed yet.
