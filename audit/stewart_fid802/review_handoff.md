# Stewart Cooperative House (Purdue GIS FID 802) — review handoff

**Asset:** `modular/buildings/massing_house_1089875810_8c9b95d.blend`  
**Frozen SHA-256:** `7339F13546EF06A0530A92BEE747157F22E09D2B449496B40DE51CFF5CD2DB5E`  
**Grade:** pending independent review

## What is represented

- The 16-vertex Purdue GIS FID 802 footprint is preserved at the wall base. The top-down overlay compares the retained GIS polygon and model wall outline directly.
- The official Stewart Cooperative About page has a current photo with the named house sign and the residence in view. It qualitatively supports light masonry, dark gabled roofs, a tower-like end mass, tall windows, and an arched glazed entry. The source image has no stated date and is not a measured elevation.
- The official house-tour page refers to second- and third-floor hallways and describes basement uses. The model therefore shows three estimated above-grade stories and a schematic basement despite the GIS `NUM_LEVELS=1` value. The GIS `Extrution=12` field is undocumented and is not treated as a measured height.
- The interior previews are schematic. No dimensioned plan or current as-built interior source was found; room positions, partitions, stairs, and furniture are illustrative.

## Fresh-open checks

The asset was opened from disk with Blender 5.2.3 LTS and validated by `validate_fresh_open.py`. Scene, collection and root names match the assigned asset. It contains 11 mesh objects and no external image dependencies. The root mesh's 16 base vertices reproduce the source ring with maximum nearest-vertex error 0.0000276 m in the repository's approximate campus-local transform. This numerical agreement is not survey accuracy. The root shell has 76 non-manifold edges at open architectural boundaries and is not claimed to be watertight.

## Preview index

- `exterior_west_oblique.png`, `exterior_south_oblique.png` — exterior massing and qualitative facade study
- `roof_plan_view.png` — estimated roof volumes
- `footprint_overlay.png` — GIS/model wall-base comparison
- `interior_basement_plan.png`, `interior_ground_plan.png`, `interior_second_plan.png`, `interior_third_plan.png` — schematic story plans

Source URLs, retrieval dates, retained raw GIS response, service metadata, source snapshots, hashes, and detailed uncertainty notes are in `source_record.json` and `evidence.json`.
