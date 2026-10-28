# Circle Pines FID 761 — R4 independent review handoff

## Request

Independent review is complete: **8.3/10 PASS** on the exact saved candidate SHA below. The asset remains frozen. The reviewer returned six rubric categories and documented remaining limits in `independent_regrade_codex_r4_2026-10-28.md` and `.json`.

## Candidate and validation

- Asset: `modular/buildings/massing_house_301841609_c6c9ac4.blend`
- SHA-256: `1E2048AF786DD3724A92DACCA5E59BC9C4FD33025DA9239930B72028F067EAD2`
- Stable collection: `Asset_massing_house_301841609_c6c9ac4`
- Stable object: `House_301841609`
- Fresh-open: Blender 5.2.3 LTS PASS; 1,000 vertices, 713 faces, one object, 14 materials; 44 GIS ring vertices retained; wall-base maximum XY error 0.0000305 m; no external image dependency.

## Source and claims

Purdue GIS BuildingShapes layer 0 FID 761 is the footprint and identity record (EPSG:3857; service WKID 102100/latestWkid 3857). Geometry was transformed using the repository's approximate campus-local conversion, not survey control. A Google Maps Circle Pines Street View listing shows an April 2026 panorama (pano ID `ytu8Bz_eEp2xCv9QeF0xRw`) looking across the parking apron toward the FID 761 footprint. The supplied camera point is approximately 62.77 m from the transformed GIS centroid, and its bearing to the centroid differs from pano heading by 7.93°; nearest edge distance is 42.53 m. These are approximate alignment checks, not a survey or independent Google panorama metadata response.

The single source-visible facade is modeled with red-brown brick, two visible rows of rectangular windows, a taller central glazed entry bay and a shallow light canopy. The main render and front elevation are evidence views. Only that camera-facing wall is treated as observed; other elevations remain neutral/unverified. Trees obscure most of the roof. The planar cap is a conservative placeholder, not a roof-form claim. Height is estimated at 5.75 m (5.4 m wall plus 0.35 m cap); it is not measured. GIS `NUM_LEVELS=1` conflicts with two visible window bands and remains unresolved. `Extrution=32` is not used as a height.

Interior remains a one-level 3D schematic with floor zones, partitions, circulation, step feature and furnishings; it is not an as-built plan. Upper interior is unknown. The historic 1954–55 Circle Pines archive image has no address and is not attributed to the current FID 761 structure.

## Evidence packet

- `exterior_preview.png`: oblique render of whole GIS mass and source-facing facade.
- `front_elevation_preview.png`: source-facing facade details.
- `interior_cutaway_3d.png` and `schematic_interior_plan_r2.png`: explicitly schematic interior evidence.
- `footprint_overlay.png`: GIS ring and wall-base comparison.
- `sources/google_streetview_panoid_ytu8Bz_eEp2xCv9QeF0xRw_2026-04.jpg`: saved Google Street View thumbnail.
- `streetview_target_reconciliation.json`: camera-to-FID alignment calculations and method limits.
- `source_record.json`, `evidence.json`, `visual_source_search_r4.md`, `revision_report_r4.md`, `fresh_open_validation.json`: provenance, uncertainty, edits and validation.
- `build_circle_pines.py`, `render_previews.py`, `validate_fresh_open.py`: reproducible asset/evidence scripts.

Previous exact-SHA reviews are preserved: R1 6.78/10 FAIL, R2 7.6/10 FAIL, R3 7.8/10 FAIL. R4 passed at 8.3/10 on the stated SHA.
