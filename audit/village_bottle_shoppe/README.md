# Village Bottle Shoppe asset audit

**Asset:** `modular/buildings/massing_village_bottle_shoppe_6a17e23.blend`  
**Stable ID:** `massing_village_bottle_shoppe_6a17e23`  
**Scene / collection / object:** `Building_massing_village_bottle_shoppe_6a17e23` / `Asset_massing_village_bottle_shoppe_6a17e23` / `Village Bottle Shoppe`  
**Status:** detailed exterior refined from exact-branch storefront photos; fresh-open and topology checks pass; independent grade pending.

## Identity and location

The official Village Bottle Shoppe location list includes 1832 Northwestern Avenue. An Indiana FSSA inspection report gives the same address at 40.445722, -86.920936. The Indiana statewide footprint query returns polygon `objectid=409442` from the Tippecanoe County 2018 LiDAR footprint data at that parcel. The FSSA point lies about 15 m north of the footprint centroid, consistent with an address/entrance point. The polygon's four-corner geometry aligns with the original asset outline; the closest corresponding original corner is about 0.3 m away and the largest is about 2.8 m away. The rebuilt walls follow the polygon vertices projected into campus coordinates.

## Sources

Sources were retrieved on 2026-10-26. Raw source responses and imagery are in `sources/`.

| Evidence | Provider and URL | Identifier/date/CRS | Use and limit |
|---|---|---|---|
| Store location | [Village Bottle Shoppe official site](https://villagebottleshoppe.com/) | Store locator lists 1832 Northwestern Ave | Confirms business/address, not facade geometry. Raw HTML: `sources/village_bottle_shoppe_official_site.html`. |
| Address and coordinates | [Indiana FSSA 2025 inspection report](https://www.in.gov/dA/ef5d81d4df/inspection-results-11122025.pdf?language_id=1) | 1832 Northwestern Ave; 40.445722, -86.920936 | Confirms the licensed location. Raw PDF: `sources/indiana_fssa_inspection_results_2025-11-12.pdf`. |
| Building outline | [Indiana Statewide LiDAR Derived Building Footprints service](https://gisdata.in.gov/server/rest/services/Hosted/Building_Footprints/FeatureServer/0) | `objectid=409442`; `lidaryear=2018`; source service in EPSG:3857; query geometry returned in EPSG:4326 | Footprint shape is the basis for placement and dimensions. Raw service metadata and query response: `sources/indiana_footprints_service.json`, `sources/indiana_building_footprints_nearby.json`, and `.geojson`. |
| Aerial roof context | [Esri World Imagery MapServer](https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer) | Identify result: Indiana GIO imagery, source date 2023-02-11, source `Indiana2023`, nominal resolution 0.0762 m, stated accuracy 0.15 m | Used to inspect the roof outline and immediate setting. Retrieved crop: `sources/esri_world_imagery_near_1832_northwestern.jpg`; metadata: `sources/esri_imagery_identify.json`. |
| Exact-branch storefront photographs | [Village Bottle Shoppe #4 photo listing](https://usa-stores.worldorgs.com/catalog/west-lafayette/beer-store/village-bottle-shoppe-4) | Exact address 1832 Northwestern Ave; undated user-contributed Google Business photos | Direct facade reference: red channel-letter sign, red brick wall, tan block base, dark storefront glass/frames, and broad white metal eaves. Saved images: `sources/google_business_photo_1.jpg`, `sources/google_business_photo_4.jpg`. Listing snapshot: `sources/google_business_photo_listing.html`. |
| Nearby street-level context | [Google Maps address page](https://www.google.com/maps/place/1832+Northwestern+Ave,+West+Lafayette,+IN+47906/@40.4456407,-86.9209176,654m/data=!3m2!1e3!4b1!4m6!3m5!1s0x8812fd4739ae4d1b:0x8b8294922f51b2fb!8m2!3d40.4456407!4d-86.9209176!16s%2Fg%2F11b8v68vtq) | Street View capture shown as April 2026; pano `MPyo7TuOQni3QqhSryFH6Q`, captioned `1110 Lindberg Rd` | Adjacent context only; no facade details were taken from it after finding exact-branch photos. Saved image: `sources/google_streetview_1832_northwestern_pano.jpg`. |
| County appraisal comparison, rejected for this facade | [Tippecanoe County Hi ViNE appraisal](https://tippecanoe.in.gov/DocumentCenter/View/39966/Hi-ViNE---West-Lafayette) | Report dated 2023-02-03; subject 302 Vine St, parcel `79-07-19-276-012.000-026`; PDF pp. 34–35 label “Village Bottle Shoppe space” and other tenant storefronts | The labeled space is the separate Village Bottle Shoppe tenant in the Hi ViNE mixed-use building at 302 Vine, not the #4 store at 1832 Northwestern (parcel `79-07-18-108-001.000-026`; building footprint `objectid=409442`). The PDF's subject photos and elevations were compared and deliberately not transferred. Raw report and page renders: `sources/tippecanoe_hi_vine_appraisal_2023.pdf`, `sources/hi_vine_appraisal_page-34.png`, `sources/hi_vine_appraisal_page-35.png`. |
| Parcel context | [Tippecanoe County Assessor GIS](https://www.tippecanoe.in.gov/1048/Assessor-GIS) | Parcel `79-07-18-108-001.000-026`; county feature `OBJECTID=5912327` | Address match and property context; does not define building wall geometry. Raw attributes: `sources/tippecanoe_parcel_attributes.json`. |

## Coordinate and footprint method

The source coordinates are geographic EPSG:4326. They were converted to the project's local campus approximation using the rule in `modular/AGENTS.md`, with origin latitude 40.4274 and longitude -86.9137:

```text
X = (longitude + 86.9137) * 111412.84 * cos(radians(40.4274))
Y = (latitude - 40.4274) * 111040
Z = 0 at grade
```

The footprint's projected long and short edges are approximately 26.89 m and 17.59 m. Planar area calculated from the query polygon is 472.920 m² and its perimeter is 88.956 m. The service's `SHAPE__Area=817.718` and `SHAPE__Length=116.950` attributes do not agree with those values; the service response does not document their units. They are retained as raw attributes but are not used as measured dimensions. Horizontal source imagery accuracy is reported by Esri as 0.15 m; this does not account for footprint digitizing or source-date uncertainty.

## Geometry changes

- Replaced the single coarse 8-vertex block and unsupported house-like gable with a low, one-story commercial volume that follows the four GIS footprint corners.
- Rebuilt the visible long elevation from exact-branch photographs: red brick, a tan masonry-block bay below the display windows, four dark-framed display windows, raised red “Village Bottle Shoppe” channel-letter lettering, and broad white fascia. The pictured elevation continues as brick under the sign; an unsupported front door was removed.
- Added a concealed low-pitch roof deck and four closed fascia members, matching the shallow roof edge seen in the direct storefront photo and aerial outline.
- Kept all modeled geometry in campus coordinates and kept the manifest scene, collection, object name and asset path stable.
- Mapped procedural brick and masonry courses in real-world UV units; all materials are internal to Blender, with no external image paths or library links.
- Estimated wall top at 4.20 m and fascia at 4.66 m above grade from the photos; no surveyed height source was found.
- Closed each structural/detail component before joining, then recalculated normals. Original mesh had 34 boundary edges from open wall and roof faces. Current exact asset has 0 nonmanifold, 0 wire, and 0 boundary edges (`topology_probe.json`).
- No interior was added because the available appraisal interior photo is from the different 302 Vine branch and no plan evidence ties it to this building.

The exact-branch exterior photographs are user-contributed and undated. They support the sign and visible materials but do not establish current condition, all elevations, exact window spacing, height, or roof framing. The 2023 aerial and 2018 footprint support the overall plan; those limitations remain part of the independent grade.

## Validation artifacts

- `preview_village_bottle_shoppe.png` — exterior review image generated from the saved asset.
- `topology_before.log` / `topology_after.json` — before-and-after boundary-edge counts.
- `probe_asset.py`, `baseline_probe.log` — original asset structure and bounds.
- `build_asset.py`, `build.log` — reproducible asset rebuild and build output.
- `fresh_open_verify.py`, `fresh_open_verification.json` — saved-file reopen check and stable naming/collection validation.
- `asset_sha256.txt` — exact saved asset hash checked after fresh reopen (`E5210EC34D7159932586D92059FDD010E4D235C5102898E13DF4EA797D155E83`).
