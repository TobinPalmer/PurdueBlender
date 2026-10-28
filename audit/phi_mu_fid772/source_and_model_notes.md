# Phi Mu — FID 772 evidence and limitations

## Identity and address

The official Purdue GIS BuildingShapesZip4 feature identifies `FID=772`, `BUILDING_N=Phi Mu`, `BLDG_ABBR=SOFM`, `OWNER=GREEK`, and `ADDRESS=201 Waldron St`. The Phi Mu Delta Epsilon chapter site also identifies its chapter house at 201 Waldron Street. These independent labels agree; no building identity or address conflict was found for the feature selected here.

Sources:

- Purdue shared BuildingShapesZip4 FeatureServer layer metadata: <https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0?f=pjson>
- Exact feature query, geographic output: <https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D772&outFields=*&returnGeometry=true&outSR=4326&f=pjson>
- Exact feature query, native projected output: <https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D772&outFields=*&returnGeometry=true&outSR=3857&f=pjson>
- Official Phi Mu Delta Epsilon chapter page: <https://purdue.phimu.org/about>
- Purdue Panhellenic roster (identity only; its accompanying chapter image is a group photograph, not a building reference): <https://www.purduepanhellenic.com/chapters-1>
- Waze listing (address cross-check; the listing image is only a low-resolution thumbnail): <https://www.waze.com/live-map/directions/phi-mu-sorority-waldron-st-201-west-lafayette?to=place.w.178979220.1789661131.4902948>

## Exterior reference

The saved 2010 WordPress chapter photo is property-specific: the post is titled “Phi Mu Pink Letters,” describes a photo taken in West Lafayette, and dedicates it to Phi Mu Delta Epsilon. The image clearly shows a red-brown brick lower facade, a light classical pediment and cornice, white columns, tall dark window bays, and centered Phi Mu letters. It is a cropped, oblique-era photo and does not document the full elevations, roof, exact orientation, current condition, or interior.

- Post: <https://cmkelham.wordpress.com/2010/08/09/phi-mu-pink-letters-201/>
- Saved image URL: <https://cmkelham.wordpress.com/wp-content/uploads/2010/08/img003.jpg>
- Local evidence copy: `source_phi_mu_purdue_2010.jpg` (1536×1024 px)

The image clearly documents only one window level on the visible brick facade. The model uses a two-level facade interpretation at coordinator direction to make the observed repeated tall-window rhythm legible across the massing. That second level is interpretative, conflicts with GIS `NUM_LEVELS=1`, and is not independently verified by this photo. The roof is a simple dark gable chosen as a restrained massing approximation; detailed roof breaks and all unseen openings remain unverified.

## GIS geometry reconciliation

The raw response snapshots and layer metadata are saved in this folder. The 4326 query returns one ring with 18 distinct vertices plus its repeated closing point. The 3857 response reports `wkid=102100`, `latestWkid=3857`; its computed area/perimeter (1385.2266 m² / 213.2383 m) match the stored `Shape__Area` / `Shape__Length` (1385.2227 / 213.2383) within GIS rounding. In the project README's local approximation at the stated campus origin, the same polygon is 26.87×40.81 m, area 801.36 m² and perimeter 162.19 m. The ~1.729 area and ~1.315 perimeter ratios are expected Web Mercator scale inflation at this latitude; they do not indicate a different footprint.

The starter mesh had 15 outline vertices, area 839.09 m² and a 5.63 m symmetric vertex-to-boundary Hausdorff mismatch from the converted GIS ring. The revised structural wall boundary uses the 18-point source ring exactly after applying the project local approximation. See `geometry_reconciliation.json` and `footprint_overlay.png`.

The outline comparison does not independently verify the asset's campus placement relative to neighboring buildings or roads. The GIS attributes include `NUM_LEVELS=1` and `Extrution=12`, but the layer has no documented unit for `Extrution`; neither field is treated as a surveyed height. The modeled 9.4 m ridge and two-level facade are estimates/interpretations. The total rendered object bounds include portico/roof overhangs and should not be confused with the structural footprint.

## Schematic interior and verification

No source-derived floor plan or interior photograph was found. The revised asset now includes a ground-floor plate, partial upper-floor panels, generic partition walls, a stair run, and modest dining/lounge/sleeping furniture. These elements are an illustrative placeholder only: room layout, room functions, stair location, furnishings, and the second level are not measured or as-built claims. The modeled second level remains in tension with GIS `NUM_LEVELS=1` and the single-level facade visible in the cropped 2010 image.

The evidence cutaway is rendered from the saved joined mesh after fresh-open. For readability it filters the render to the interior inserts and floor plates while retaining the full GIS footprint outline. It is not a separate floor-plan authority. `fresh_open_validation.json` records the saved asset hash, scene/collection/object names, mesh statistics, dimensions, materials, image dependency check, and fresh-open exterior/top/interior preview filenames. The asset remains one mesh object in the expected stable asset collection and has no external unpacked image dependencies.

Current revised asset SHA-256: `8524c009a3931f1e04ca1ed313d43be3be1cb94ff07ea99c62797841db65d861`.

Status: **awaiting independent rereview; not yet finished**. The previous 7.54/10 review applies only to SHA `77d7d6075baa1f4948e48a0a0366891e33e28e0e9daf9f6290e9828ec8584f43`. Review the exact current SHA and reassess source identity, footprint alignment, the two-level interpretation versus GIS `NUM_LEVELS=1`, roof/profile, facade orientation, and clearly schematic interior evidence.
