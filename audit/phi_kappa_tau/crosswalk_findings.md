# Phi Kappa Tau identity and placement crosswalk (FID 856)

Retrieved 2026-10-26. This is a source and assignment investigation only; no building geometry or placement was edited.

## Assignment and stable asset

- `README.md` assigns Phi Kappa Tau / FID 856 to Rossen and names `massing_phi_kappa_tau_139b9d7`.
- Manifest stable ID/path/collection/scene: `massing_phi_kappa_tau_139b9d7`, `modular/buildings/massing_phi_kappa_tau_139b9d7.blend`, `Asset_massing_phi_kappa_tau_139b9d7`, `Building_massing_phi_kappa_tau_139b9d7`.
- Fresh Blender 5.2.3 inspection: one mesh named `Phi Kappa Tau`, 28 vertices, 20.804 × 13.614 × 16.000 m. Manifest campus-world bounds: X 437.351–458.155, Y -101.180–-87.566, Z 0–16 m. The asset has identity transform; coordinates are embedded in its mesh.

## GIS FID 856

- Provider: Purdue BuildingShapes hosted feature layer, layer 0; feature identifier FID 856. Service: https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0
- Raw snapshot: `fid856_arcgis_snapshot.json`; retrieved 2026-10-26. Source CRS: Web Mercator Auxiliary Sphere (WKID 102100; latest WKID 3857). Layer metadata reports an edit timestamp of 2026-08-31 UTC; feature `last_edi_1` is a separate numeric timestamp of 2026-01-26 UTC.
- Feature attributes: `BUILDING_N=Phi Kappa Tau`, `BLDG_ABBR=SOFKT`, `ADDRESS=1307 TOWER DR`, `NUM_LEVELS=2`, `Extrution=53`, `Shape__Area=729.46875`, `Shape__Length=122.2652269`. Height/floor fields are not treated as surveyed measurements; feature units/semantics for `Extrution` remain unverified.
- Geometry conversion: transformed each 3857 ring vertex to lon/lat by inverse Web Mercator, then to project local coordinates using the published project approximation (X=(lon+86.9137)*111412.84*cos(40.4274°), Y=(lat-40.4274)*111040). Resulting bounds X -1134.384 to -1099.643; Y 591.389 to 619.673 m. This is an approximate local frame, not surveyed CRS.
- Candidate asset `massing_house_301841257_c23233c` has bounds X -1139.108 to -1098.442; Y 588.112 to 620.780 m. Its center is 2.068 m from FID 856's bbox center; footprint shape has not been checked. It is a strong spatial candidate, but the official current Phi Kappa Psi chapter contact page identifies its address as 1307 Tower Dr. Therefore the 856 label/address appears stale or crosswalk-conflicted for current fraternity ownership; it should not be assumed to be Phi Kappa Tau's current house.

## Address/identity evidence for current Phi Kappa Tau

- Official Phi Kappa Tau Lambda chapter site, home and House & Location pages: https://www.phikappataupurdue.com/ and https://www.phikappataupurdue.com/house/. Both identify the current house as 416 N Chauncey Ave. House page explicitly links address to a map and includes an exterior photo. Retrieved 2026-10-26. Snapshots: `pkt_home_page.html`, `pkt_house_page.html`; image: `pkt_house_416_chauncey.png` (SHA-256 C86DC9B68A45681E77F39719AA2368C6127306E06BF5854AE4AA43812243A0FB). Image is useful facade evidence, but its publication/source date is not stated.
- Alumni/history page maintained by the Phi Chapter alumni association: https://phikappatorque.com/torque. It says the Phi Chapter/Theta Tau house at 416 N Chauncey opened in 2002 and is now affiliated with Phi Kappa Tau Lambda Chapter. Retrieved 2026-10-26. Snapshot: `phi_chapter_alumni_page.html`.
- Purdue BuildingShapes FID 820 has `BUILDING_N=Theta Tau`, `ADDRESS=416 Chauncey`, area 593.1875 m², perimeter 110.5068 m, and polygon bounds X 587.808–600.660, Y 78.704–108.391 m using the same conversion. Raw snapshot: `fid820_arcgis_snapshot.json`. The name can be reconciled with the alumni history, while the current chapter site's address corroborates this footprint location. Its GIS vertical fields are not reliable enough to use as measurements (`Extrution=638` with no verified units/meaning).
- Official Phi Kappa Psi contact page: https://purdue.phikappapsi.com/contact, lists 1307 Tower Dr. Snapshot: `phi_kappa_psi_contact_page.html`.

## Crosswalk result and unresolved item

The evidence supports current Phi Kappa Tau at FID 820's 416 Chauncey location, with the GIS's historic Theta Tau label explained by the house transition. FID 856 is at Phi Kappa Psi's currently stated 1307 Tower address and is spatially matched to the neighboring `massing_house_301841257_c23233c` candidate. The Rossen-assigned `massing_phi_kappa_tau_139b9d7` asset is at neither site (approximate separation from FID 820 bbox center: 244 m; from FID 856 bbox center: 1714 m); an ArcGIS query around its current bbox returned no building footprint intersecting the bbox plus 5 m. No evidence has yet tied this assigned asset's current location to Phi Kappa Tau.

Do not change geometry or placement until the coordinator resolves the shared assignment/crosswalk and confirms whether the stable asset is to be re-placed to FID 820. `README.md`, manifest, audit ledger, master file, and shared crosswalks are coordinator-owned; no such files were edited here.

## Coordinator disposition and build scope (2026-10-26)

After reviewing this conflict, the coordinator directed that this Rossen assignment follows the current Phi Kappa Tau house at FID 820 / 416 N Chauncey. The stable asset identifiers remain unchanged. The previously unsubstantiated campus location embedded in the asset is corrected to the FID 820 wall ring; this is a documented placement correction authorized by the coordinator. The active proposed candidate now uses the FID 820 ring as its structural wall plan. FID 856 and the spatially coincident `massing_house_301841257_c23233c` remain a separately documented legacy label / Phi Kappa Psi address conflict; their asset files are not edited.

Additional independent official source: Tippecanoe County, Finish Living Area layer 79, parcel PIN 164023000702 for `416 N CHAUNCEY AVE`, retrieved 2026-10-26. Snapshot `county_parcel_416_chauncey.json` reports year built 2002 and FinishLivingArea 9918 sq ft. Parcel Shape_Area is parcel/lot area, not building footprint. The assessed living area does not establish the number or heights of levels.

The build script converts the raw FID 820 source ring vertices directly from EPSG:3857 into the project's documented approximate local campus coordinates. Wall height, floor elevations, roof pitch, dormer size/spacing, portico depth, entrance position within the west-facing frontage, and window sizes are estimates from the current chapter's official photos. The official photo is a facade cue only and has no publication date or dimension scale. The old alumni photo labeled “Original House” is preserved only as historical context, not used to shape the current model.
