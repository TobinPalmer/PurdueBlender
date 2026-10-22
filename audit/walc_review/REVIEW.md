# WALC neighborhood correction review — October 22, 2026

The review covered every official building feature within220m of WALC's project center, plus adjacent Haas, Math, Chaney-Hale, Grissom, MSEE and Schleman assets. Three agents edited disjoint building libraries. Only the coordinating agent edited the two master files, manifest, placement records and integration scripts.

## Corrections

| Buildings | Result |
|---|---|
| WALC | Rebuilt irregular perimeter and roof from official FID906; retained compatible interior/furniture; removed four unrelated oversized terrain plates. Archived incompatible previous exterior geometry outside the export. |
| Potter, Mechanical Engineering, Brown Family Hall (BHEE) | Replaced inaccurate rectangular placeholders with official polygon envelopes, roofs and bands. ME and BHEE include both official feature components. Removed duplicate massing from master. |
| Elliott | Replaced incorrect axis-aligned envelope with official curved/stepped plan. Original detailed objects preserved in hidden reference collection; duplicate annex block removed from master. |
| Hovde | Moved entrance, portico, doors, balustrades, urns, lettering and steps from wrong narrow end to the official long-side entrance projection. Closed plaza-to-step gap. |
| Class of1950, Haas, Math | Corrected shell/roof outlines and clipped incompatible geometry. Preserved original objects in hidden reference collections. Newly exposed facades are simplified. |
| Stanley Coulter | Structural bounds already agreed within4mm; removed oversized lawn overlapping Class of1950. |
| Knoy, Bell Tower | Existing horizontal geometry passed screening; retained current libraries. Removed stale Knoy massing duplicate. |
| Railway, Brown Chemistry, Chaney-Hale, Grissom, Data Science/AI, MSEE, Peirce, Psychological Sciences, Wetherill, Schleman | Corrected simple massing to official polygon geometry. Retained original estimated heights. Railway includes both official component features. |
| Dudley and Lambertus | Replaced combined unnamed massing block with separate independently linked building libraries, using their official footprints. |
| Unnamed official FID888 | Corrected footprint; official identity remains unnamed. |

## Evidence and checks

Source: Purdue University's public campus GIS, BuildingShapesZip4 layer0, retrieved October22,2026. Raw snapshot: `../official_purdue_buildings_wgs84.json`; converted polygons: `../official_building_references.json`. Source CRS EPSG4326, converted with the project's existing local linear conversion (origin40.4274N,86.9137W; X east,Y north,metres). Source update date and surveyed accuracy are not provided.

Source service: https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0

Reopened 13 corrected massing libraries and compared projected mesh geometry with the saved source polygons: every footprint IoU exceeded0.99999 and boundary error was below0.00002m. This is agreement with the cached polygon coordinates, not real-world survey accuracy. See `massing_verification.json` for per-library FIDs and measurements.

Detailed library measurements, before/after images, repair scripts and backups are in `../walc_east/`, `../walc_north/` and `../walc_south/`. Master duplicate removal and relative-path checks are recorded in `master_reopen_check.json`. The master overhead view is `master_after_top.png`.

## Remaining uncertainty

Heights, roof elevations, facades, many interiors and site furnishings are still estimates. Rebuilt Elliott and several other shells have less architectural detail than the old invented geometry. Original geometry is recoverable from backups/reference collections. This review fixes supported plan geometry, entrance and overlap defects; it does not certify full architectural accuracy.
