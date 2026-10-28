# Alpha Phi FID 764 review handoff

Please independently grade the saved asset at `modular/buildings/massing_house_301841331_735e92f.blend` against the evidence in this folder. Completion requires a separate score of at least 8/10. The prior 5.8/10 review predates the live GIS provenance, source observation, plan comparison, refreshed interior view, and fresh-open report documented here; it is not a grade of this final revision.

## What changed

- Rebuilt the single-object asset from all 16 distinct vertices of Purdue GIS FID 764.
- Preserved the stable asset, object, collection, and scene names.
- Added an illustrative brick-colored exterior, windows, covered entry and stairs, estimated gable roof, and schematic upper bedroom cutaway.
- Repositioned interior modules inside the retained footprint after the original rectangle-fit checks revealed they had been skipped.
- Fixed a material cleanup issue so repeat builds keep stable material names.

## Review evidence

- `evidence.json` — source register, identity evidence, CRS/transform, dimensions, uncertainties, and limitations.
- `source_observation.json` — exact HUBERart Etsy drawing URL and retrieval date. The listing prohibits duplicating its image, so no copy is saved.
- `purdue_gis_fid764_2026-10-28_3857.json` and `purdue_gis_layer_0_metadata_2026-10-28.json` — fresh official ArcGIS response and layer metadata. The response exactly matches the pre-existing `source_feature_764_raw.json`; the live layer metadata and response declare WKID 102100/latestWkid 3857.
- `plan_overlay.png` and `plan_comparison.json` — source ring vs. saved structural wall-base segments. Maximum boundary vertex error is 0.000058 m and RMS error is 0.000041 m because the wall shell is constructed directly from that transformed ring. This does not independently validate the GIS ring against a current survey or aerial.
- `exterior_three_quarter.png` and `schematic_upper_rooms.png` — exterior and brighter upper-bedroom cutaway previews. The interior arrangement remains invented and schematic.
- `fresh_open_validation.json` — Blender 5.2.3 fresh-open PASS, stable names/transform, one exported object, and mesh health counts.

## Open uncertainty

The two-story interpretation conflicts with `NUM_LEVELS=1`; `Extrution=12` has undocumented units/meaning. Wall height, roof height, gable shape/direction, fenestration spacing, and interior arrangement remain estimates. The estimated roof ridge axis (53.13° from east) differs by about 42.06° from the transformed footprint ring PCA axis (11.07°); no source resolves the roof orientation. The source illustration is qualitative and does not establish current as-built conditions.

## Reproduce the build and checks

From the repository root, run these in order with Blender 5.2:

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background modular/buildings/massing_house_301841331_735e92f.blend --python audit/alpha_phi_fid764/build_detail.py
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --python audit/alpha_phi_fid764/fresh_open_validate.py
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --python audit/alpha_phi_fid764/plan_comparison_extract.py
python audit/alpha_phi_fid764/render_plan_overlay.py
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --python audit/alpha_phi_fid764/render_previews.py
```

No independent grader slot was available during this worker turn; the grade remains pending.
