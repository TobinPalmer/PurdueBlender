# Zeta Psi address lead: 237 South Grant Street — 2026-10-26

**Review date:** 2026-10-26 (America/Indiana/Indianapolis)  
**Question:** Does the Columbia Alpha Chapter roll’s Tau Gamma address at 237 South Grant Street identify a current Zeta Psi building and change the Purdue GIS FID 748 / 950 David Ross crosswalk?  
**Disposition:** The chapter roll is a real address-bearing source, but it is undated and explicitly describes itself as a complete roll where inactive chapters remain visible and corrections may be submitted. The address geocodes to a Tippecanoe County parcel, but Purdue BuildingShapes has no feature at the point, the Indiana statewide footprint layer returns no building footprint over the parcel, the county assessment lists zero improvement value, and the Esri imagery export shows paved parking/vehicle stalls rather than a building. Taken together with Tau Gamma’s official 2023 report that it moved its house during 2022, 237 S Grant appears to be an older/stale address rather than a current building candidate. This does not establish where Tau Gamma moved or resolve its current occupancy at 950 David Ross.

## Source context and date limits

The Columbia University Alpha Chapter site’s [Complete Roll of Zeta Psi Chapters](https://www.columbia.edu/cu/zetapsi/chapters.htm) lists Purdue’s Tau Gamma Chapter, chartered 1968, phone 765-743-2112, and “House: 237 South Grant Street, West Lafayette, IN.” The visible introductory note says inactive chapters remain displayed while their charters are in abeyance, and invites errata/addenda so the database can be updated. The Purdue row has no inactive label, but the page provides no publication or update date and no evidence when the address was last verified. This is a chapter-hosted roll, not a dated, current Purdue occupancy record. The captured visible-source excerpt is `sources/columbia_zeta_psi_chapter_roll_excerpt_2026-10-26.txt`; direct HTTP retrieval was blocked by the site’s Cloudflare challenge, so the excerpt was captured from the browser-rendered page on the review date.

The chapter’s official 2023 report already says it moved its chapter house during 2022, without naming its new address. Therefore the undated 237 S Grant listing may predate that move.

## Address and parcel crosswalk

The ArcGIS World Geocoding Service matches “237 S Grant St, West Lafayette, IN 47906” at score 100 to (-86.910818948835, 40.421002232666). The point intersects Tippecanoe County parcel `79-07-19-401-007.000-026` (PIN `164028000862`, OBJECTID 5940025), whose county address is `237 S GRANT ST`. County assessment attributes show `CurImpAv=0` and `CurTotAV=CurLandAV=48700`; these are assessor valuation fields, not a building survey.

The same address point returns no Purdue BuildingShapes record. Querying the Indiana Geographic Information Office’s statewide building-footprint layer across the parcel extent returns zero footprints. The point/parcel crosswalk and raw queries are retained in the source snapshots and `source_register.json`. These negative results are not conclusive by themselves because GIS layers can omit structures or differ in coverage/date.

## Imagery check

An Esri World Imagery export covering the parcel and surrounding block (`sources/esri_world_imagery_237_s_grant_extent_2026-10-26.jpg`) shows the parcel area occupied by paved parking and vehicle stalls; no roof is visible over the parcel. The image service metadata attributes the mosaic to Esri, Vantor, Earthstar Geographics, and the GIS User Community, but the export does not provide the capture date for this location. The imagery is therefore evidence of visible land cover in the served mosaic, not proof of historical conditions or occupancy. Extent, attribution, method, and limitations are recorded in `sources/esri_world_imagery_237_s_grant_record_2026-10-26.json`.

## Crosswalk and modeling decision

This lead does **not** justify moving the Zeta Psi model assignment from the Purdue GIS FID 748 / 950 David Ross physical candidate to 237 S Grant. The Columbia address is most plausibly stale after the documented 2022 house move, and current imagery/footprint evidence shows no building at the mapped 237 parcel. The earlier 950 evidence remains conflicting: Chi Psi’s official July 2024 newsletter identifies 950 as its new lodge, while Tau Gamma’s exact-address social bio has no update date. No current, dated source identifies Tau Gamma’s 2024–26 facility or establishes exclusive occupancy at 950.

Keep the FID 748/950 association as a spatial candidate only and the occupant crosswalk unresolved. Separately, no model is justified at either location: 237 has no supported current building geometry, and the 950 asset still lacks sufficient identity, wall perimeter, height, roof, and facade evidence for a passing independent grade. Do not claim exclusive Zeta Psi occupancy or assign a grade on the basis of the chapter-roll address.

No model, manifest, shared tracker, or master blend was edited.

