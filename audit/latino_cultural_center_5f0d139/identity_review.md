# LCC identity and site disposition review

Reviewed: 2026-10-26. No Blender files or shared project files were edited.

## Findings

### Stable ID `massing_latino_cultural_center_5f0d139` / GIS FID 743 / 600 N Russell

This asset is correctly located on the **former** Latino Cultural Center footprint, but that identity is historical. Purdue Archives identifies the 600 N Russell center as operating from 2006–2017 and says it relocated to 426 Waldron in 2017; it describes the Russell building as planned for replacement by a parking lot. The 2017 WBAA report likewise says the LCC would move and the old center would be torn down for parking (the latter was a plan at that time, not proof of completion).

More recent evidence resolves the present site use. Purdue's July 24, 2023 Board of Trustees land-sale packet identifies the 600 N Russell parcel, 0.14 acres, for sale to Lambda Iota Graduate Corp./Phi Gamma Delta, adjacent to its 640 N Russell property, for future housing improvements. Phi Gamma Delta's dated April 25, 2026 dedication report says its new Lyles Addition to 640 Russell covers the old parking lot and that the organization now owns/operates the entire west half of the 600 block as a unified fraternity property. Taken together with the former LCC's documented relocation and planned demolition, the best-supported disposition is: **the old LCC structure is no longer present; the 600 N Russell site is now incorporated into the Phi Gamma Delta property and its Lyles Addition/parking reconfiguration.** The 2026 report is direct current-use evidence; it does not explicitly name the former LCC building, so exact old-footprint overlap with the addition is not independently surveyed here.

The Purdue GIS building layer still labels FID 743 “Latino Cultural Center,” address 600 N Russell, with a 2005-era building record and an occupied flag. Treat that legacy row as stale for current identity. The audit snapshot retrieved 2026-10-22 confirms the assigned asset closely matches FID743's historic footprint (AABB center difference 1.183 m, IoU 0.8246), which establishes what the model depicts, not that it remains standing.

**Disposition:** stop this building-modeling assignment. Do not detail the asset as a current Latino Cultural Center or as the old LCC building. Parent should remove/retarget the stale FID743 building assignment after deciding whether the 2026 Phi Gamma Delta addition is included in this campus scope. Do not infer the new addition's exact shape from the old LCC massing.

### Stable ID `massing_latino_cultural_center_lcc_9cc71b3` / GIS FID 925 / 426 Waldron

Purdue's current LCC site and Purdue's Campus Map and Resources identify **426 Waldron Street** as the Latino Cultural Center. The official building layer has a separate record, FID 925, “Latino Cultural Center at Purdue,” at 426 Waldron Street. Purdue Archives says this is the LCC's post-2017 location. Thus **FID 925 is the current LCC identity**.

README already has a separate row for `massing_latino_cultural_center_lcc_9cc71b3`, assigned to Tobin, and the model's bounds are near 426 Waldron. The README's GIS crosswalk instead puts both LCC assets under FID743 and leaves FID925 unmapped; that crosswalk should be corrected by the project coordinator. I did not edit the README, the other asset, the manifest, the audit index, or any shared file.

## Source record

- Purdue Archives, “Latino Cultural Center (West Lafayette, Ind.: 2006–2017),” accessed 2026-10-26: https://archives.lib.purdue.edu/agents/corporate_entities/850
- Purdue WBAA, “Purdue Fraternity Will Turn Current Latino Center Into A Parking Lot,” 2017-03-02: https://www.wbaa.org/general-news/2017-03-02/purdue-fraternity-will-turn-current-latino-center-into-a-parking-lot
- Purdue Board of Trustees packet, “Approval to Sell Parcel at 600 North Russell Street to Lambda Iota Graduate Corp. d/b/a Phi Gamma Delta Fraternity,” dated 2023-07-24 (posted in 2023): https://www.purdue.edu/treasurer/finance/wp-content/uploads/2023/04/600-North-Russell-Street-Land-Sale-to-Phi-Gamma-Delta-B-1-24-6-11.pdf
- Phi Gamma Delta–Purdue, “FIJI House Dedication,” event dated 2026-04-25; describes the Lyles Addition, former parking-lot site, and unified property: https://purduefiji.org/fiji-house-dedication/
- Current Purdue Latino Cultural Center website, 426 Waldron Street: https://www.purdue.edu/lcc/
- Purdue Campus Map and Resources PDF, lists LCC at 426 Waldron Street: https://www.purdue.edu/campus-map/
- Purdue BuildingShapesZip4 ArcGIS FeatureServer, FID743 and FID925; service/building data retrieved 2026-10-22: https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0
- Esri World Imagery tiles for both sites were saved under this folder. The World Imagery service is a mosaic with varying source dates, so the tiles are visual context only and are not used as dated proof of demolition or construction.

## Local evidence captures

The source captures gathered for this review are in `sources/`, including the official Purdue LCC pages and map PDF, GIS query responses, official 2021 LCC exterior image, and Esri imagery tiles. Current-use conclusion relies on the dated 2023 Purdue sale record and 2026 Phi Gamma Delta dedication report rather than assuming the old GIS record is current.
