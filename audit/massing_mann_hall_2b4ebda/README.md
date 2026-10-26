# Mann Hall evidence and build record

Stable ID: `massing_mann_hall_2b4ebda`  
Assignment: Rossen (root `README.md`, massing backlog)  
Asset: `modular/buildings/massing_mann_hall_2b4ebda.blend`  
Dedicated builder: `modular/buildings/build_massing_mann_hall_2b4ebda.py`  
Export: scene `Building_massing_mann_hall_2b4ebda`, collection `Asset_massing_mann_hall_2b4ebda`, object `Mann Hall`.

## Sources archived

- **Purdue University BuildingShapesZip4 GIS**, FeatureServer layer 0, feature **FID 635**, abbreviation **MANN**, “Gerald D. and Edna E. Mann Hall,” 203 S Martin Jischke Drive. Provider: Purdue University ArcGIS service. Retrieved 2026-10-26. Native service CRS: **EPSG:3857** (`WKID 102100`). The native query and layer metadata are in `sources/purdue_building_gis_fid_635_native.json` and `sources/purdue_building_gis_layer_metadata.json`; a WGS84 query for coordinate conversion is in `sources/purdue_building_gis_fid_635.json`. The official source identifies the polygon as `BLDG Building Primary`, reports 3 levels, floor fields F02=15 ft, F03=28.8 ft, R=37 ft, and `Extrution`=35 ft. Geometry is used as the structural plan shell. The geometry area after the documented project local transform is 1,697.07 m²; GIS `Shape__Area` is 2,933.39 m² in the native Web Mercator service plane, so the field is retained as source metadata and not treated as local ground area.
- **Purdue Research Facilities page**, “Institutes and Centers at Discovery Park,” https://research.purdue.edu/about/institutes-and-centers/. Provider: Purdue University. Retrieved 2026-10-26. HTML snapshot and the page's 584×328 Mann Hall photo are archived in `sources/`. Purdue states opened 2007, address 203 S Martin Jischke Drive, and 25,000 assignable square feet. The photograph shows a glazed two-level corner, dark mullions, a red-brown vertical end panel, metal-panel wall, roof parapet/plant, and an entrance canopy.
- **Fortune Architecture**, “The Mann Building, IT Research Facility, Purdue University,” https://fortunearchitecture.com/the-mann-building-it-research-facility-purdue-university/. Retrieved 2026-10-26; page snapshot archived. The page identifies Diana M.H. Brenner as project architect and describes a two-story building plus lower level and a metal-panel west facade. These design details are used as secondary architect-source evidence. Its 49,000-sf project-size figure differs from Purdue's current 25,000 assignable-sf figure and is not used as a footprint measurement.
- **OpenStreetMap**, campus Overpass snapshot dated 2026-10-22 03:45:50 UTC, way **159752223**, `name=Mann Hall`, `building=university`. The way and its node coordinates are in `sources/osm_mann_hall_way_159752223.json`.

## Measurement and model decisions

The GIS polygon was returned in WGS84 and converted with the project's documented approximation: X=(longitude+86.9137)×111412.84×cos(40.4274°), Y=(latitude−40.4274)×111040. The resulting plan bounds are X −779.712 to −746.266 m and Y −517.957 to −457.557 m. The 40-point shell in the built mesh is a near-duplicate-cleaned copy of the official ring; the direct reopen validation finds a maximum source-ring-to-shell-base vertex distance of 0.000032 m. No whole-asset rescaling or translation was applied.

The independent OSM polygon has 96.51% IoU with the Purdue GIS polygon, 0.100 m centroid difference, 0.474° major-axis difference, and 3.72 m Hausdorff distance. The last measure is driven by local outline details and longer north/south extents in OSM; OSM is treated as a corroborating outline, not a height source.

The old generic 16 m massing mesh was replaced. The new mesh retains campus-world coordinates and the one-object manifest collection. It models the official plan shell, two visible main stories (Purdue GIS F02=4.572 m and F03=8.778 m as floor/upper-shell reference elevations), curtain-wall modules, west-facing metal-panel treatment, a brick accent, entry door/canopy, parapet, and rooftop enclosure. The overall roof screen reaches the Purdue GIS R elevation of 37 ft (11.278 m).

**Vertical uncertainty:** Fortune Architecture describes two stories plus a lower level, while Purdue GIS `NUM_LEVELS` is 3 and also supplies F02, F03, and R elevation fields. The photograph shows two visible above-grade facade bands. The model therefore shows two principal above-grade stories, omits the below-grade level, and keeps the 37-ft GIS maximum as roof-screen height. The precise floor/roof interpretation and basement extent remain unverified. No architectural floor plan/elevation file was publicly available; the GIS `Floorplans` field points to an inaccessible internal drive.

## Validation

The saved blend was reopened directly in Blender 4.5.15 LTS. `validation/reopen_validation.json` records one mesh object in the expected scene and collection; 4,028 vertices and 1,014 faces; no modifiers, external libraries, or linked dependencies; campus-frame bounds; overall height 11.278 m; and source-shell registration. Preview: `preview/mann_hall_isometric.png`. The asset's final state awaits independent grading.
