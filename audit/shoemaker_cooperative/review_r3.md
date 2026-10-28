# Shoemaker Cooperative FID 800 — revision 3 handoff

**Asset:** `modular/buildings/massing_shoemaker_cooperative_2159ea4.blend`  
**Current asset SHA-256:** `7DC9A6D7E32C0E1E788157200D98209CEF5322F9617CFBEC144259AC1EB975EB`  
**Build:** Blender 5.2.3 LTS  
**Status:** saved, reopened, and independently graded **8.3/10 PASS** on exact SHA; pending coordinator master integration.

## Sources and what they support

- [Purdue campus building footprint service, FID 800](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0) — official campus-map footprint candidate, address 351 Northwestern Avenue, building code SOSH. The full raw feature snapshot is `source_feature_800_raw.json`. It is not a survey; the source has no published positional uncertainty. The project local transform and ring comparison method are in `evidence.json`.
- [Shoemaker Cooperative — Our Home](https://www.shoemakercooperative.com/our-home), retrieved 2026-10-28 — lists the residence at 351 Northwestern, ten rooms, shared common areas, and a “Floor Two” tour. Its exterior photo filename is dated 2016-09-29; the original image snapshot is `operator_exterior_reference.jpg`, SHA-256 `3c689855ddb7cf5e644617ec1eef749312eccb6e15a150dd275b75bedb0f880e`.
- [Purdue University Archives entry](https://archives.lib.purdue.edu/agents/corporate_entities/611) — cooperative identity and history only.

The operator photo supports two above-grade window rows, light-looking smooth walls, gable roof, dark shutters, three gable vents, corner upper porch/balcony, low basement windows, and window AC units. The image is monochrome, unscaled, partial, and not georeferenced; it does not prove paint/roof color, measurements, exact facade orientation, or the unseen roof wings. The official GIS `NUM_LEVELS=1` conflicts with the operator's second-floor gallery and two visible window levels. We retain that conflict in evidence instead of calling the modeled height measured.

## Implemented and checked

- Replaced massing shell surfaces with the full ten-vertex official FID 800 polygon while retaining the stable object, collection, scene, and file path.
- Modeled the photographed two-level gable facade, shuttered sash windows with meeting rails/sills, gable vents, window AC units, floor band/plinth, and corner balcony/porch with posts, railing and a shallow canopy.
- Added clipped pitched roof surfaces following the GIS footprint. Ridge axis follows the polygon principal direction (128.544°) as an estimate; the photo's campus orientation is unavailable.
- Added procedural plaster and asphalt surface variation and a dedicated material palette without external image dependencies.
- Added two interior floorplates, corridor, room-dividing walls and door openings. Operator text supports ten rooms and shared common rooms, but no published floor plan exists; these partitions are schematic and unverified.
- Blender 5.2.3 reopened the file. Export collection `Asset_massing_shoemaker_cooperative_2159ea4` contains one object. The source-ring points compare within 0.0000139 m under the local conversion (floating-point reprojection only; not source accuracy). Mesh: 2,692 vertices, 1,911 faces; bounds X 334.279–358.005 m, Y -59.764–-33.465 m, Z 0–10.2 m.

## Review files

- `preview_detail_r2.png` — exterior preview.
- `interior_cutaway_plan.png` — roof/floor hidden for review only, showing the schematic room/corridor geometry.
- `reopen_validation.json` — fresh-open identity, collection, mesh bounds/material and source-ring checks.
- `build_detail.py`, `build_config.json`, `render_preview.py`, `render_cutaway_plan.py` — reproducible asset build and review scripts.
- `evidence.json` and `source_owner_site_observation.json` — measurements, source metadata, evidence, edits, and unresolved uncertainty.

## Outstanding review gate

Independent exact-SHA evaluation by `/root/kappa_kappa_gamma` passed at **8.3/10** on 2026-10-28. The report is `independent_grade_codex_r3_2026-10-28.md` plus JSON. Reviewer notes: the interior plan is sparse, mesh is non-watertight (44 open/nonmanifold edges), and documented height/roof/color/orientation/interior uncertainties remain. Tobin may now consider master integration.
