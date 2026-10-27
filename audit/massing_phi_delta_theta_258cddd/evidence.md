# Phi Delta Theta — source and model audit

Asset: `modular/buildings/massing_phi_delta_theta_258cddd.blend`  
Stable ID: `massing_phi_delta_theta_258cddd`  
GIS identity: Purdue BuildingShapes, layer 0, FID 796 (`SOFDH`; Phi Delta Theta; 503 State St; owner category `GREEK`).  
Prepared: 2026-10-26.

## Sources and use

1. **Official Purdue BuildingShapes GIS feature.** Query: <https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D796&outFields=*&returnGeometry=true&outSR=4326&f=pjson>. Layer metadata: <https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0?f=pjson>. Retrieved 2026-10-26. Raw feature and service metadata are saved as `sources/purdue_gis_fid_796_current.json` and `sources/purdue_gis_building_shapes_metadata.json`. The returned polygon is EPSG:4326 and contains 30 non-closing ring vertices. Its feature attributes identify the chapter and street address. The shell plan was built from every non-closing polygon point.
2. **Official Purdue Phi Delta Theta chapter article and photograph.** <https://purdue-phi.net/state-street-makeover/>. The article is dated 2017-06-13 in the captured page; retrieved 2026-10-26. The archived HTML and original 2560×1440 article image are in `sources/purdue_phi_delta_state_street_makeover_2017.html` and `sources/phi_delta_state_street_front_2017.jpg`. The article identifies the house at 503 W. State Street and describes the image as outside the house during street work. The photograph supports the street-facing brick-and-light-siding composition, three visible occupied levels, classical columned portico, balcony, triangular pediment and round vent, window rhythm, and broad dark roof masses. It has no scale reference, so it does not establish measured dimensions or heights.
3. **Esri World Imagery.** XYZ tile service: <https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/20/{y}/{x}>. Eight zoom-20 tiles covering X 271135–271138 and Y 395351–395352, plus a zoom-19 context tile, were retrieved 2026-10-26. Raw tiles and `esri_world_imagery_mosaic_z20.jpg` are in `sources/`. The tile service endpoint does not expose the acquisition date. The mosaic and the GIS boundary overlay in `renders/gis_footprint_imagery_overlay.png` were used to check that the target parcel is the house in the photo, its site context, and that the photographed State Street facade faces north in the repository coordinate frame. Imagery supports footprint identity/orientation and context; it was not used for vertical dimensions.
4. **Historical chapter publication, The Scroll (1910 issue).** <https://phideltathetaarchive.com/wp-content/uploads/2012/03/1909-10_vol34_no1-5.pdf>, retrieved 2026-10-26. The saved source copy is `sources/phi_delta_theta_scroll_1910_issue.pdf`. Search-indexed material titled “Indiana Theta’s New House” refers to a 1909 project and architect Elmer E. Dunlap. This is historic context only; it does not establish that every current wing matches the original house and did not drive modeled geometry.

## Coordinate and measurement method

The official GIS ring is geographic longitude/latitude (EPSG:4326). Each point was converted to the repository’s approximate local campus coordinates, with X east, Y north, Z up:

- `X = (longitude + 86.9137) × 111412.84 × cos(radians(40.4274))`
- `Y = (latitude − 40.4274) × 111040`

This local approximation is not a surveyed projected CRS. The transformed source polygon’s axis-aligned extents are approximately X=67.5770–110.5754 m and Y=−417.5177–−392.9709 m (about 43.00 × 24.55 m). These are local transformed GIS bounds, not an independent building survey. The service metadata reports its `Shape__Area` and `Shape__Length` units as `esriMeters`; those summary attributes were not used to place or scale the mesh. No separate surveyed plan or measured height was found.

The principal wall shell uses the source polygon ring directly and is extruded at estimated levels 0.00, 3.55, 7.05, and 10.15 m. Those levels, three-story interpretation, 10.15 m eaves, roof peaks, roof pitches, and all facade detail dimensions are visual estimates from the chapter photograph; no height is reported as measured. Decorative portico elements and roof forms may extend beyond the GIS wall outline because the GIS polygon is a footprint and does not describe those projections.

## Changes and validation

- Replaced the prior coarse massing slab with the source-ring wall shell and a modular, named facade, entry, roof, and window composition. The photographed State Street frontage is modeled on the north side. The supported principal visual features are reproduced at simplified massing detail; unphotographed elevations remain schematic.
- Saved the expected `Asset_massing_phi_delta_theta_258cddd` collection in scene `Building_massing_phi_delta_theta_258cddd`; the asset remains standalone and uses only embedded materials/geometry, with no unpacked external file dependencies.
- `reopen_validation.json` records Blender 5.2.3 LTS reopen validation and asset SHA-256. The saved file reopens with 313 objects (309 meshes, 4 curve/font objects), the expected scene and collection, and no temporary render rig. The 30 base-ring vertices were compared to the transformed source ring: maximum nearest-point XY difference is 0.000016 m (float storage precision). The checks cover evaluated mesh bounds/modifiers and external image dependencies.
- The source-derived shell extents and checks are recorded in `reopen_validation.json`; render views are `renders/01_street_facade.png`, `renders/02_north_elevation.png`, `renders/03_plan.png`, and `renders/gis_footprint_imagery_overlay.png`.

## Remaining uncertainty

- GIS supports identity, plan outline, and local placement; it does not verify wall thickness, internal layout, or vertical form.
- The chapter image is oblique, dates to 2017, and lacks a dimensional reference. Floor heights, overall height, roof geometry, exact window spacing, portico proportions, materials away from the street view, and all hidden elevations remain estimated or unverified.
- World Imagery acquisition date is unavailable from the tile endpoint. Trees, construction, and image perspective obscure portions of the parcel, so the chapter image is the primary facade evidence.
- The 1910 historical publication may describe an earlier house; it is not treated as evidence that the present house’s geometry is unchanged.
