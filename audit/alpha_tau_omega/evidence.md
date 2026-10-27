# Alpha Tau Omega — FID 785

## Asset and validation

- Asset: `modular/buildings/massing_house_301840870_c45a5f4.blend`
- SHA-256 after save and fresh-open validation: `99C798326ED74F49BC635308EEAC1A962906BDFD74D71E240B4C9A8B895A78B4`
- Stable identifiers preserved: scene `Building_massing_house_301840870_c45a5f4`, collection `Asset_massing_house_301840870_c45a5f4`, root object `House_301840870`.
- Root transform remains location `(0, 0, 0)`, rotation `(0, 0, 0)`, scale `(1, 1, 1)` in campus-world coordinates. No master blend or placement marker was edited.
- Blender 5.2.3 opened the saved library in a new background process. The asset collection contained 126 objects and the named material set; no external image files or missing dependencies were found. The model uses procedural materials.
- Machine-readable check: `fresh_open_validation.json`.

## Sources and identity

All source snapshots below were retrieved on 2026-10-26 and kept under `sources/`.

1. Purdue GIS BuildingShapes feature layer, [FID 785 query](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D785%26outFields%3D*&returnGeometry=true&f=pjson), attributes `SOATO`, `Alpha Tau Omega`, `314 Russell St`; raw geometry response in `sources/purdue_gis_fid785_2026-10-26.json`, layer metadata in `sources/purdue_buildingshapes_layer_metadata.json`. The layer metadata identifies the native coordinate system as Web Mercator (EPSG:3857); this feature response is EPSG:4326. The matched property is the former 314 Russell Street house, not the current chapter address at 302 Waldron Street.
2. National Register nomination, `https://npgallery.nps.gov/GetAsset/cc869c53-05ea-4ad1-8495-b156bc7fb81b/`, saved as `sources/national_register_nomination.pdf`. This is the primary architectural description: a 2.5-story Tudor Revival residence with red brick, dressed limestone, a tower and platform porch, steep hipped roof, dormers, chimneys, nine west-facing bays, and documented principal rooms and interior features.
3. National Register historic-photo packet, `https://npgallery.nps.gov/GetAsset/bf9b5e1a-7202-4a32-81d7-1db2923d8731`, saved as `sources/nps_historic_photos.pdf`. Its historic exterior/interior photographs informed the facade composition, tower, roof, entry, windows, and documented interior cues.
4. West Lafayette historic review (2022), `https://d3n9y02raazwpg.cloudfront.net/westlafayette/400608e0-ccac-11ec-bbb4-0050569183fa-109477ba-f636-4eb6-8e84-46bf82167f28-1652195969.pdf`, saved as `sources/west_lafayette_2022_review.pdf`.
5. Official chapter history, `https://www.purdueato.org/history`, saved as `sources/purdue_ato_history.html`; used to confirm the historical 314 Russell identity and additions. The official current chapter site is `https://www.purdueato.org/` and lists 302 Waldron, so it was not used as the facade reference for this FID.
6. Esri World Imagery tiles, service `https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer`, z19, tiles x=135558–135560 and y=197667–197669; individual tile snapshots and the 3x3 context mosaic are under `sources/`. Esri does not expose the capture date in the saved tile response, so the imagery vintage is unknown. `previews/gis_candidate_footprint_overlay.jpg` overlays the official GIS outline (red) and candidate structural blocks (blue) on that imagery.

## Plan and placement comparison

Method: transform each returned EPSG:4326 vertex with the project approximation, using geographic origin `(40.4274, -86.9137)` and `X=(longitude+86.9137)*111412.84*cos(radians(40.4274))`, `Y=(latitude-40.4274)*111040`. This is an approximate local tangent conversion, not a surveyed CRS transform. Dimensions and overlap were independently recomputed from the raw feature ring with Shapely; GIS `Shape__Area` was not used because it does not agree with the transformed ring area.

| Measure | Purdue GIS ring | Modeled structural wall blocks | Result |
|---|---:|---:|---|
| X extent | -436.873 to -413.695 m | -436.875 to -413.800 m | ~23.18 m vs ~23.08 m |
| Y extent | 46.099 to 83.938 m | 46.000 to 83.700 m | ~37.84 m vs ~37.70 m |
| Area | 566.91 m² | 593.03 m² | 562.72 m² intersection; 94.2% polygon IoU |

The model has an axis-aligned approximation of the GIS outline, including the 1920 house, later connector/addition and east kitchen wing. The remaining difference is principally polygon curvature/angled corners and small boundary offsets; decorative porch, steps, garden wall and the GIS outline curb are excluded from the structural-footprint score. GIS and orthophoto support source identity, footprint location, and orientation, but neither provides reliable vertical dimensions.

## Height and facade confidence

The nomination describes a 2.5-story building and its roof/tower/chimney arrangement. The GIS feature has `NUM_LEVELS=1`, `CountOfFlo=1`, and `Extrution=12`; those fields conflict or lack documented units/meaning and are not treated as a surveyed height. Model dimensions are estimates: brick eaves about 8.65–8.95 m, principal roof ridges about 11.70–12.05 m, and highest chimney cap about 13.89 m above the model's z=0 datum. There is no authoritative elevation or section drawing in the gathered evidence, so total height and roof pitch remain unverified estimates.

Material assignment and composition follow the historical photography and nomination (brick, limestone, slate-like roof, pale dormer stucco, dark timber, leaded glazing, oak). Procedural shaders avoid asset-path dependencies. Exact brick bond/stone joint scale, window dimensions, some rear-face features, and the appearance at the current imagery date remain interpretive.

## Interior limits

The NPS nomination supports room names/features used here: foyer, formal living room, dining room, billiards room, oak stair/newel and inglenook/fireplace. It states there were 26 living quarters. No measured floor plan was found. The labeled first-floor display is therefore a schematic vignette: partition locations, room dimensions, furniture layout and bedroom layout are not claimed to be documented. Upper living quarters are explicitly labeled layout-unverified.

## Work delivered

- Replaced the single massing block with a textured brick exterior and its GIS-footprint-based wall wings, Tudor Revival roof forms, entry tower, limestone details, windows, dormers, porch/steps, kitchen wing and three chimney stacks.
- Added a source-labeled, clearly caveated schematic interior based only on named rooms and documented features.
- Saved and freshly reopened the asset; current SHA and object/dependency checks are in `fresh_open_validation.json`.
- Renders: `previews/ato_exterior_front.png`, `previews/ato_exterior_three_quarter.png`, and `previews/ato_interior_schematic.png`.
