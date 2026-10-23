# Psychological Sciences Building research notes

Retrieved 2026-10-23.

## Official Purdue GIS

- Service: Purdue ArcGIS `BuildingShapes` FeatureServer layer 0: https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0
- Feature: `FID=239`, `BLDG_ABBR=PSYC`, `BUILDING_N=Psychological Sciences Building`, address 703 3rd Street, Purdue ownership.
- Native CRS: EPSG:3857 (WKID 102100 / latest WKID 3857). Snapshot query requested GeoJSON in EPSG:4326 and is retained at `raw_feature_239.geojson`.
- GIS attributes list `NUM_LEVELS=5` and `CountOfFLO=5`. These support a five-level count, not exact floor elevations, wall height, roof shape, or room plan.
- The feature's `Floorplans` field points to `G:\GIS\web_pages\html_pages\PSYC.html`; that path is not publicly accessible. It was not treated as a verified floor plan.
- Geometry comparison in this revision: visual/source continuity only. The existing massing library already retains a prior official-footprint correction. This pass did not rerun a polygon-to-wall overlay or independently measure the placement transform. The inherited placement origin is `[-106.6966,-48.2750] m` in the project local approximation (X east, Y north; geographic anchor 40.4274,-86.9137).

## Building-specific photographs and history

- Purdue Archives history: https://archives.lib.purdue.edu/agents/corporate_entities/707 — construction 1978–1983 and connection to Peirce Hall's north end. It does not establish exact connector dimensions.
- Wikimedia Commons doorway photograph: https://commons.wikimedia.org/wiki/File:Psychological_Sciences_Building_Door.JPG — building-specific doorway detail. Reviewed as a reference for the recessed entrance and brick treatment; no image pixels were imported into the asset.
- Wikimedia Commons sign photograph: https://commons.wikimedia.org/wiki/File:Purdue_Psychological_Sciences_Sign.JPG — building identification and sign reference.
- Purdue Archives photo finding aid: https://archives.lib.purdue.edu/fa/UA62_Series3.pdf — lists Psychology Building contact-sheet material dated August 1980. The corresponding archival images were not accessed or used in this revision.
- Google Maps satellite pin: https://www.google.com/maps/place/Psychological+Sciences+Building,+703+3rd+St,+West+Lafayette,+IN+47907/@40.42785,-86.916,18z/data=!3m1!1e3 — inspected 2026-10-23 for broad context; imagery date unavailable.

## Modeling choices

Brick, punched windows, and entry expression follow the available photos. The GIS count guided a fifth floor/window row within the older 15 m shell estimate. Exact floor heights are unknown, so 2.96 m spacing is illustrative. The five floor layouts, room labels, research equipment, corridors, and furniture are schematic program examples only. Stair geometry was removed because available sources do not locate the cores or support external egress. No claim is made that named labs or rooms occupy those positions in the real building.
