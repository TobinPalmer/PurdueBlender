# Master build status — October 24, 2026

The current project master is `../purdue_campus_master.blend`. It links the smaller building libraries with project relative paths. The linked master workspace copy is `purdue_campus_linked.blend`.

## Current build

- 1,979 registered assets: 1,978 building assets and one campus site asset.
- 69 detailed buildings are local-coordinate linked collections. Each has a `Placement_<id>` empty in the master that supplies its XY campus position.
- The master scene has 2,225 direct objects and references 50,857 objects across its source libraries.
- 44 matching massing assets are superseded by detailed models.
- All 69 placement markers reference their expected source library paths; the root master reopens with no missing library paths.
- `purdue_campus_master_before_modular_linking.blend` preserves the former root master. Per-building world-coordinate copies are in `source_backups/buildings_world_coordinates/`.

## Accuracy status

These assembly checks confirm that assets are linked and placements are present. They do not certify architectural accuracy. The existing audit predates recent detailed assets and covers the original 1,933-asset scene. It reports 1,421 assets without an official footprint match, 397 ambiguous source matches, and 113 needing shell and height review. README acceptance grades are separate from a comprehensive geospatial audit; each completed building retains its own evidence and unresolved uncertainties. See `../audit/MASTER_AUDIT.md` and the evidence records for current limitations.

## Editing workflow

Edit one source file under `buildings/`, save it, and reopen the root master. Move a detailed building by changing its `Placement_<id>` empty. Keep its local geometry and manifest origin aligned. For new or replaced modules, update `manifest.json` and use `rebuild_linked_master.py` to refresh the linked master.

## WALC neighborhood review

October22: corrected WALC and adjacent building footprints, Hovde entrance, duplicate massing and oversized local terrain. Dudley/Lambertus now have separate libraries. See `../audit/walc_review/REVIEW.md` for per-building corrections, checks and remaining height/facade uncertainty.

## Five-building reconstruction pass

Five builders and their child reviewers improved Potter, Mechanical Engineering, BHEE, Knoy and Class of1950 with source-supported exterior/interior work. Independent ratings range4.5–7.4/10; none reached the requested9/10. See `../audit/completion_master/REVIEW.md` for exact changes and remaining work. Historical/proposal-derived interiors retain their uncertainty labels.

Second batch, October22–23: Hicks, Krannert, Lawson, Rawls and Niswonger received source-supported interiors, material work and technical repairs. Five independent child reviews rate them5.7–6.7/10; none reached9/10. See `../audit/batch2_master/REVIEW.md`. Niswonger's replacement roof height is explicitly a photographic estimate. Full current interiors and measured architectural details remain unfinished.

## October 24 active building pass

The master was reopened and saved in Blender 5.2.3 after current linked-source updates. The 69-marker integration check passes with no missing libraries or placement/path errors. Hovde Hall scored 8.7/10, Krach Leadership Center 8.1/10, Life Science Plant and Soils Laboratory 8.0/10, Lyles-Porter Hall 8.2/10, Krannert Building 8.0/10, Mackey Arena 8.0/10, Materials Science and Electrical Engineering R6 8.2/10, Math Sciences R12 8.1/10, and McCutcheon Hall R4 8.05/10. LSPS links 641 source objects, Krannert 670, Mackey 391, MSEE 1,200, Math Sciences 593, and McCutcheon 219. Their saved placement markers match their manifest origins within 0.001 m with zero rotation and unit scale. McCutcheon's placement marker remains at (-1215, -260, 0) with identity rotation/scale. Its eight occupied floors per tower are supported by Indiana CHE records; its 2017–18 LiDAR roof estimate has no vertical accuracy rating and no class-6 building returns. R4 removes unsupported tall penthouses but does not claim an as-built roof survey. LSPS floor plates match the GIS perimeter within 0.00001 m. Remaining roof, height, interior, courtyard and facade uncertainties are recorded in each building's audit. MSEE roof-monitor/height and interior circulation remain interpretive; its `Extrution` GIS field has no documented units. Math Sciences DSM/DTM indicates a roof surface near 36.9 m median and a smaller high-return zone, but the 5-ft raster cannot assign the mismatch to an exact roof component; facade direction and interior remain unverified. Mackey's composite GIS segmentation is photo-interpreted, not surveyed; height and interior circulation remain uncertain. Lambert's marker matches the manifest, but its archived volume placements remain illustrative and need source registration. Hovde GIS bounds/axis comparisons are screening checks, not surveyed wall-polygon registration; roof pitch remains unverified. The saved master backup is `../purdue_campus_master.blend1`.

Knoy Hall remains below threshold: R17–R18 scored 7.8–7.9/10, R19 scored 7.7/10, and R20–R22 scored 7.8/10; the Scribd plan lead was rejected as a 2019 student project for another address, and the model geometry remains unchanged. Mackey Arena passed at 8.0/10 in R3, and Krannert Building passed at 8.0/10 in R12. MSEE passed at 8.2/10 in R6; its latest source is synced into the saved master. Math Sciences passed at 8.1/10 in R12 and is now synced into the master. McCutcheon Hall passed at 8.05/10 in R4; its latest source is synced into the saved master. Mechanical Engineering R2 scored 7.5/10 after an evidence-supported FID108 height correction; R3 is underway. Lawson Hall remains at 7.0/10, with round 5 awaiting review. Lambert Fieldhouse reached 8.0/10, but its two volume placements remain illustrative pending coordinator review. The master file is only saved by Tobin; subagents edit only their assigned source libraries/evidence and do not commit.
