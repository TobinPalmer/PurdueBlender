# 4. R. B. Wetherill Laboratory of Chemistry: research in progress

Checkpoint 2026-10-28 local time (some download timestamps are October 29 UTC). **Partial research only; not prepared for modeling and no model changed.** Stable ID `wetherill_laboratory_of_chemistry`, asset `modular/buildings/wetherill_laboratory_of_chemistry.blend`, modeling owner Rossen. Continue here before moving to rank 5.

## Identity and defining features established so far

The building is at **560 Oval Drive**, WTHR, Purdue GIS **FID257**. Purdue's [department history](https://www.chem.purdue.edu/about_us/facts-history.html) describes a first wing completed in 1930 and subsequent expansion; its [landmark page](https://www.chem.purdue.edu/wetherill/) places construction across 1928–1955. Brown Laboratory is an adjacent separate asset, not another Wetherill wing to duplicate.

The [Purdue archival description, UA136](https://archives.lib.purdue.edu/repositories/2/resources/1483) identifies red brick with Indiana limestone and five chemistry relief subjects above the main doors: analytical balance, biological rat/leaf, inorganic periodic-table portion, organic tetrahedron, and physical phase diagram/thermodynamics equation. These are distinctive facade details that require close references; generic rectangular panels will not reproduce their appearance.

The inspected [full-resolution Purdue front photograph](sources/purdue_front.jpg), [original source](https://www.chem.purdue.edu/admissions/admissions/WTHR.JPG), shows a low ground-level upward oblique of the main entrance facade. Its capture date is unspecified. Defining observations include a tall central stone composition with Ionic-style capitals and attached columns/pilasters, multiple rectangular entrance recesses, broad steps and pale metal handrails. Larger multi-light windows sit above entrances; the uppermost window row is shorter. Stone quoin-like corner bands, belts, carved panels and engraved scientist names interrupt the brick fields. Several window-mounted air conditioners are visibly present in this photograph; their current positions must be verified rather than repeated across every bay. The projecting dark/greenish cornice differs from the pale stone trim. Complete opening counts have not yet been recorded.

## References actually collected and inspected

| Reference | Perspective / source date | Current use and limits |
| --- | --- | --- |
| [Purdue front photograph](sources/purdue_front.jpg) | Near/medium ground-level low oblique; capture date unknown | Main entrance, window/mullion patterns, limestone relief and sunlit brick/stone. One camera position, not all-face coverage. Original 6016×4016 file retained for details. |
| [Esri overhead](sources/aerial_world_imagery.png), [successful export metadata](sources/aerial_export_wide.json) | Orthographic overhead; acquisition date unknown | Perimeter roof, inset roof/service zones and nearby buildings. Initial narrow export returned no image; wider export supplied the actual saved image. |
| [Purdue elevated campus reference](../bell_tower/sources/purdue_elevated_ese.webp), [published photo essay](https://purduenews.exposure.co/happy-birthday-purdue-bell-tower) | Elevated oblique facing east-southeast; published 2020, WALC plaza still under construction | Wetherill appears behind/right of tower; useful contrasting roof/context evidence, not a complete frontal elevation or current landscape reference. |
| [Purdue history snapshot](sources/purdue_history.html) and [landmark snapshot](sources/purdue_landmark.html) | Department source pages | Identity/construction sequence; historical photo candidates identified but not yet downloaded or counted as inspected viewpoints. |

[Requested sources](sources/requested_sources.json) and [download/access index](sources/reference_download_index.json) retain original URLs, providers, resolved URLs, timestamps and hashes. The Quantum Optics page identifies another exterior-photo URL, but that photograph has not yet been downloaded/inspected. Alexander Sergeev's 1999 page was saved as a photo lead; **its AI-generated narrative is not factual evidence**, and the actual photograph has not yet been inspected here. ACS's article was readable through the web research service, but its direct download returned a small anti-bot challenge, explicitly labeled in the index. It is not a saved article snapshot. Source pages retain provider copyrights; no texture-reuse license is inferred.

## Roof and material notes

The actual overhead image shows brown/red pitched perimeter roof sections surrounding extensive flat/inset service areas, ducts and many repeated ventilation stacks. Do not create one simple hip or fit a solid roof over all interior setbacks. Segment primary roof, lower roofs, raised enclosures and service equipment separately when modeling is later authorized. The aerial's acquisition date is unknown, so every large service feature needs date reconciliation.

The front daylight photograph supports red-brown brick, light warm limestone, dark frames and a weathered greenish cornice, but not fixed measured RGB values. Facade shade, pale sky reflections and glass transparency affect color. Obtain opposite faces in multiple daylight conditions before choosing final materials; neither night views nor a single sunlit patch establishes the building-wide color.

## GIS and LiDAR already acquired

[Saved official feature](sources/purdue_footprint.json) retains FID257 in WGS84, with [shared cached-source provenance](../../shared/location_source_provenance.json). It is not a new survey. Confirm courtyard/roof offsets and attached links against this ring before deriving a simplified mass. No manifest or placement changes were made.

The [Indiana tile query](sources/lidar_delivery_tiles.json) selected **in2018_29951885_12** and **in2018_30001885_12**, dated **April 20, 2018**. Actual full-resolution COPC spatial queries produced portable [LAZ crops](data/lidar/) totaling **43,592 points**: 2,230 west-context points and 41,362 body-envelope points. The context clip has no points inside the footprint; the body clip has 23,607 inside. [Crop/source statistics and hashes](sources/lidar_crop_summary.json), tile COPC metadata and [request index](sources/site_download_index.json) are preserved.

The source compound CRS is **NAD83(HARN) / Indiana West (ftUS) + NAVD88 height, Geoid12B (ftUS)**, with full WKT retained; horizontal source EPSG2968 inside a bound CRS and vertical EPSG6360. All native axes use **US survey feet**, converted by **0.30480060960121924 m/ftUS**. Scene Z is not automatically NAVD88 elevation. Indiana's public archive is [documented as CC0](https://registry.opendata.aws/in-elevation/).

No class-6 building classification exists in these clips. Classes 1, 2 and 7 are unclassified, ground and noise. In the body tile, outside-footprint class-2 ground median is **620.0 ft NAVD88**. A 1 m eroded footprint contains 21,319 class-1 returns; p50/p90/p99 heights above that reference are **17.514 / 19.205 / 22.098 m**. These are mixed return statistics, not measured eave/ridge/floor levels. Segment roofs and roof equipment, reject non-building objects and inspect registration before using heights. Airborne cloud density cannot resolve relief carvings or facade window placement.

## Work remaining at this checkpoint

Research is **in progress**. Collect and inspect additional north, east, west and rear/service views, frontal bay sequences and several camera heights/distances. Obtain close images of all five reliefs, scientist inscriptions, cornice, entrance returns and connection to Brown without treating adjacent structures as Wetherill. Download/inspect the identified photo leads, seek recent elevated roof images, and reconcile visible equipment with the 2018 cloud. Prepare a per-face opening schedule and explicit coverage matrix after those observations. No claim of full exterior coverage, completed research or independent model acceptance is made.
