# Master build status — October 22, 2026

The current project master is `../purdue_campus_master.blend`. It links the smaller building libraries with project relative paths. The linked master workspace copy is `purdue_campus_linked.blend`.

## Current build

- 1,944 registered assets: 1,943 building assets and one campus site asset.
- 34 detailed buildings are local-coordinate linked collections. Each has a `Placement_<id>` empty in the master that supplies its XY campus position.
- The master scene has 2,234 direct objects and references 28,584 objects across its source libraries.
- Four matching massing blocks were unlinked where detailed models now cover Hicks, Krannert, Lawson, and Rawls.
- All 34 placement markers reference their expected source library paths; the root master reopens with no missing library paths.
- `purdue_campus_master_before_modular_linking.blend` preserves the former root master. Per-building world-coordinate copies are in `source_backups/buildings_world_coordinates/`.

## Accuracy status

These assembly checks confirm that assets are linked and placements are present. They do not certify architectural accuracy. The existing audit predates the nine new detailed assets and covers the original 1,933-asset scene. It reports 1,421 assets without an official footprint match, 397 ambiguous source matches, and 113 needing shell and height review. No building is certified. The nine new assets still need individual rows in that audit. See `../audit/MASTER_AUDIT.md` and the evidence records for the current limitations.

## Editing workflow

Edit one source file under `buildings/`, save it, and reopen the root master. Move a detailed building by changing its `Placement_<id>` empty. Keep its local geometry and manifest origin aligned. For new or replaced modules, update `manifest.json` and use `rebuild_linked_master.py` to refresh the linked master.

## WALC neighborhood review

October22: corrected WALC and adjacent building footprints, Hovde entrance, duplicate massing and oversized local terrain. Dudley/Lambertus now have separate libraries. See `../audit/walc_review/REVIEW.md` for per-building corrections, checks and remaining height/facade uncertainty.

## Five-building reconstruction pass

Five builders and their child reviewers improved Potter, Mechanical Engineering, BHEE, Knoy and Class of1950 with source-supported exterior/interior work. Independent ratings range4.5–7.4/10; none reached the requested9/10. See `../audit/completion_master/REVIEW.md` for exact changes and remaining work. Historical/proposal-derived interiors retain their uncertainty labels.

Second batch, October22–23: Hicks, Krannert, Lawson, Rawls and Niswonger received source-supported interiors, material work and technical repairs. Five independent child reviews rate them5.7–6.7/10; none reached9/10. See `../audit/batch2_master/REVIEW.md`. Niswonger's replacement roof height is explicitly a photographic estimate. Full current interiors and measured architectural details remain unfinished.
