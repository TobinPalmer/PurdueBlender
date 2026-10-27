# Kappa Alpha Theta (Purdue Alpha Chi), FID 786

## Result

- Stable asset ID: `massing_house_301840865_cbf7de2`
- Asset: `modular/buildings/massing_house_301840865_cbf7de2.blend`
- Generator: `modular/buildings/build_kappa_alpha_theta.py`
- Saved scene: `Building_massing_house_301840865_cbf7de2`
- Export collection: `Asset_massing_house_301840865_cbf7de2`
- Anchor / local origin: projected GIS polygon centroid `(-496.885833, 343.566955, 0)` m in the repository's Purdue local XY system. All modeled building geometry is in local meters around `(0,0,0)`; the Tobin-owned master placement marker and shared manifest are synchronized and fresh-open verified.
- Geometry extent after the final plan scale: approximately `x=[-13.924,13.924]`, `y=[-17.110,16.579]`, `z=[0,13.900]` m, including entrance steps and chimney. The primary facade faces south (local `-Y`); its direction is an informed interpretation of the corner location and official photographs, not a surveyed bearing.
- Fresh-open check: Blender 5.2.3 LTS opened the saved file in a separate background process, confirmed the stable scene/collection/asset ID, and rendered `fresh_open_preview.png`. It found 430 asset objects, 429 meshes and one text object. No external texture paths are used.
- SHA-256: `20DC22E31A3FA189E258B1D22084CBBC646DBDFDC4B643C30A9510F61652BDCD`.

## Source evidence (retrieved 2026-10-27)

1. Purdue ArcGIS BuildingShapesZip4 FeatureServer, layer 0, official query for `FID=786`, requested `outSR=4326`:
   `https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D786&outFields=%2A&returnGeometry=true&outSR=4326&f=json`
   Raw response is preserved in `fid786.json`. Its attributes identify `Kappa Alpha Theta`, `BLDG_ABBR=SOKAT`, `ADDRESS=607 Russell St`, `OWNER=GREEK`, `NUM_LEVELS=1`, `Extrution=12`, and `Shape__Area=1944.0977`; the last fields conflict with public photos and are treated as legacy estimates, not observed facts. Source ring coordinate system: geographic WGS 84 / EPSG:4326 (explicit `outSR=4326`).
2. Purdue Alpha Chi chapter's official home and gallery: `https://www.kappaalphathetarho.com/our-home` (its canonical site URL resolved during retrieval as `https://www.kappaalphatheta-rho.com/our-home`). The official page's courtyard photographs include `IMG_2580.jpg` (2021-era image) and `IMG_1691.jpg`; downloaded copies are `house_2021.jpg` and `house_2019.jpg`. The courtyard view supports a multi-wing, brick building with white window trim, dark shutters, planted court and columned entrance.
3. Alpha Chi Facility Corporation official property page: `https://alphachithetas.org/facility-corporation/`. It identifies 607 N Russell as the chapter house since 1957, locates it at the corner of N Russell and W Stadium, describes a major early-1990s expansion, and calls the facility 25,000 sq ft. Its official historic property image is archived here as `official_facility_1990.jpg` and depicts brick walls, sash windows, pale trim and a columned entry.
4. Current chapter contact address: `https://purdue.kappaalphatheta.org/contact` (retrieved 2026-10-27), listing 607 N Russell St, West Lafayette, IN 47906-2826.

## GIS / coordinate method

- Converted each GIS ring point using the repository's stated approximate campus transform: `X=(longitude+86.9137)*111412.84*cos(radians(40.4274))`; `Y=(latitude-40.4274)*111040`, meters, X east / Y north. This is the project's local approximation, not a surveyed state-plane transform.
- Calculated the polygon centroid with the shoelace formula on the transformed FID 786 outer ring. Anchor is `(-496.8858331765, 343.5669554848)` m. The transformed ring bounding box is X `[-512.7260,-480.7877]`, Y `[323.9441,364.0145]`, approximately `31.94 x 40.07 m`. The shoelace area in the project-local approximation is about `1,124.6 m²`, materially different from ArcGIS `Shape__Area=1,944.1`; the asset therefore uses ring extent and centroid only, not that area field as a building-wall area.
- Existing massing source mesh center was about `(-493.776,306.642)` m, approximately `37.1 m` from this official polygon centroid. The source candidate was not a safe location proxy and its single 18.59 x 12.36 x 16 m box was replaced as the assigned asset while retaining its stable ID, file, scene and collection names.
- Plan dimensions and orientation were interpreted from the GIS envelope and official exterior/courtyard images. A three-level south bar and two-level return wings form an open courtyard; the footprint was kept inside the generalized GIS envelope and modestly enlarged in plan. The official source has no separate courtyard ring or wall-level survey. This is an estimated form, not a georeferenced photogrammetric reconstruction.

## Geometry edits and uncertainty

- Replaced the massing box with a red-brown brick, multi-wing house with white sash and lintels, charcoal shutters, repeated window bays, centered columned entry, stairs, gabled south-facing roof feature, lower return-wing roofs, chimney, chapter initials, paved courtyard, planters and small courtyard shrubs.
- The chapter's exterior photographs support the material palette, visible story count, shutters, courtyard, planted beds and columned entry. Window counts/spacing, exact plan, wing heights, roof pitches, entry bearing, chimney placement and hidden elevations are estimated. The GIS attributes' `NUM_LEVELS=1` and extrusion value are not consistent enough to validate height. Photo perspective is not a reliable dimension source.
- A sparse interior layout is included only under names prefixed `SCHEMATIC_ONLY_`; the scene custom property states `SCHEMATIC_ONLY geometry: no verified floor plan was available`. These low partitions/floor plates do not assert rooms, uses, or dimensions.
- Target for independent review: **8/10 or better** for identity/placement against FID and official sources, footprint and orientation, visible facade/story/roof form, courtyard match, material/detail and clean asset packaging. Interior-plan accuracy is not gradable as factual until a floor plan is found; it should be graded only for being clearly identified as schematic.


## Master integration

The detailed asset was synchronized into `purdue_campus_master.blend` on 2026-10-27. A separate Blender 5.2.3 fresh-open check verified its `Placement_massing_house_301840865_cbf7de2` marker against the manifest XY and library path. The full master check passed with 101/101 detailed markers and 1,938 existing linked libraries, with no missing library files; see [`../master_sync_2026-10-27.json`](../master_sync_2026-10-27.json).
