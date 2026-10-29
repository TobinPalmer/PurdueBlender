# Hovde Hall exterior research — in-progress checkpoint

Research rank **6**; stable ID `hovde_hall`; model asset `modular/buildings/hovde_hall.blend`; second-pass owner **Rossen**. The existing first-pass score is 8.7/10. This checkpoint preserves research collected so far at the user's request. It is **not a prepared exterior dossier**, a modeling revision, or a visual acceptance. Continue this building before advancing to rank 7.

## Identity and location evidence

The saved [Purdue footprint](sources/purdue_footprint.json) identifies FID **618**, abbreviation **HOVD**, Frederick L. Hovde Hall of Administration, **610 Purdue Mall**, in the primary-building layer. The source geometry is EPSG:4326. Its cached-source provenance is preserved in [the shared provenance record](../../shared/location_source_provenance.json); retrieval of this copy does not establish a new survey date. The queue uses the official footprint centroid rather than changing the existing model placement.

The GIS record contains floor, elevation and extrusion attributes. Their field names alone do not establish surveyed exterior dimensions, a roof height, or a visible-floor count; do not directly turn them into model geometry without checking units and architectural evidence. The footprint also needs a visual boundary check at the adjacent Elliott Hall of Music and connecting structures before any future modeling. Keep neighboring buildings separate and resolve ownership of connections explicitly.

## Source acquisition checkpoint

[Requested sources](sources/requested_sources.json) and the [reference download index](sources/reference_download_index.json) retain URLs, providers, retrieval timestamps, HTTP failures, downloaded-file hashes and candidate image tags. The saved pages are discovery evidence; image tags are not inspected exterior photographs and do not count as viewpoint coverage.

| Source | Saved result | Remaining work |
| --- | --- | --- |
| Dave Wegiel, *Hovde Hall in Winter*, page dated July 26, 2017 | [HTML snapshot](sources/wegiel_winter.html) | Retrieve and inspect the actual building photograph; establish its face, camera position and capture date if available. Winter lighting and snow cannot establish neutral material colors. |
| Wikimedia Commons, *Frederick L Hovde Hall of Administration Purdue University 2016 01.jpg* | [File-page snapshot](sources/commons_2016.html) | Inspect the original image and attribution/license record before using it for architectural findings. A saved file page alone is not a completed photo inspection. |
| Society of Architectural Historians architectural inventory | Direct acquisition returned HTTP 403; URL retained in index | Preserve a readable citation or permitted snapshot and verify descriptions against actual exterior images. |
| Purdue Alumnus, *150 Things to Love About Purdue* | Direct acquisition returned HTTP 406; URL retained in index | Retrieve the relevant official photograph and record its credit and date separately from the page date. |
| Purdue University, *Snow Place Like Purdue* | Direct acquisition returned HTTP 403; URL retained in index | Seek a permitted accessible image or alternate official source. Do not count the failed download as photo evidence. |

The [site download index](sources/site_download_index.json) records retrieval times, URLs and SHA-256 values for aerial and elevation metadata. The actual [World Imagery export](sources/aerial_world_imagery.png) is saved with [successful wide-export parameters](sources/aerial_export_wide.json). The [initial smaller export response](sources/aerial_export.json) is also retained; do not treat it as another image or camera position. Aerial acquisition date is unverified. Roof outlines, building boundaries and neighboring context still require visual interpretation.

## LiDAR already acquired

The [state tile query](sources/lidar_delivery_tiles.json) identifies tile `in2018_29951885_12`, with acquisition date **2018-04-20**. Its [COPC metadata](sources/in2018_29951885_12.copc.metadata.json) and [crop summary](sources/lidar_crop_summary.json) accompany a portable [local LAZ crop](data/lidar/in2018_29951885_12.hovde_hall_clip.laz). The full-resolution spatial query was written as regular LAZ with COPC hierarchy removed; it is a point-cloud source, not a new building model.

The crop contains **40,551 points**, including **6,884 inside the queried footprint**. Classes are 26,760 unclassified (1), 13,770 ground (2), and 21 noise (7). There is no class-6 building classification in this crop. Class 1 must not be interpreted as confirmed roof points.

The retained compound CRS is **NAD83(HARN) / Indiana West (ftUS) + NAVD88 height — Geoid12B (ftUS)**, with horizontal EPSG:2968 and vertical EPSG:6360 identifiers in the WKT. XYZ units are **US survey feet**, conversion factor **0.30480060960121924 m/ftUS**. Ground-class points outside the footprint have median native Z 622.44 ftUS. Within the one-metre-eroded footprint, 5,490 class-1 returns have candidate heights above this local ground median of approximately **17.194 / 18.261 / 19.361 m** at p50 / p90 / p99. These statistics are **not measured eave, ridge or ornament heights**. Trees, other returns, footprint selection and local ground slope can affect them. Airborne data does not establish windows, mullions, portico detail or material colors, and 2018 data cannot prove current conditions.

## Coverage and unresolved architectural work

| Required coverage | Checkpoint status |
| --- | --- |
| Main frontage, frontal and both oblique directions | Actual photo inspection and distinct camera positions still needed |
| Side faces and rear, including Elliott connection | Unverified; resolve asset boundaries before interpreting geometry |
| Near entrance, window and signature-detail views | Not yet documented; no window or column counts accepted |
| Elevated and distant silhouette views | Seek independent cameras; page thumbnails and repeated crops do not qualify |
| Roof/aerial | Source acquired; interpretation, date and detailed roof-feature cross-check pending |
| Material/color comparisons | Pending multiple real photographs under different lighting, with neutral daylight comparisons |

Continue by inspecting the acquired source pages and their actual photographs, then seek public street-level views around all sides, additional elevations and distances, and close-ups of the entrance, openings, trim and roof edges. Record reproducible source URLs/panorama locations, dates, face and viewing direction, approximate height/distance only when supportable, and occlusion limits. Document distinctive features only after inspection. Preserve incompatible historical/current conditions separately. No models, builders, placements or master files were edited for this checkpoint.
