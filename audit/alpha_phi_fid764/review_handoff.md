# Alpha Phi FID 764 review handoff

Please independently grade the current saved asset at `modular/buildings/massing_house_301841331_735e92f.blend` against the evidence in this folder. The preceding independent revision 2 score was 7.6/10. This handoff covers the roof, lighting, sign, and cutaway revisions made after that review; it is not yet independently graded.

## What changed

- Rebuilt the single-object asset from all 16 distinct vertices of Purdue GIS FID 764.
- Preserved the stable asset, object, collection, and scene names.
- Added an illustrative brick-colored exterior, windows, covered entry and stairs, and schematic interior inserts.
- Repositioned interior modules inside the retained footprint after the original rectangle-fit checks revealed they had been skipped.
- Fixed a material cleanup issue so repeat builds keep stable material names.
- Replaced the unsupported broad gable, ridge, and chimney with a low-profile roof cap following the GIS footprint perimeter. Roof type, coverage, and top height remain estimates.
- Increased neutral exterior illumination and adjusted the entry plaque glyph strokes for better sign visibility.
- Replaced the isolated bedroom render with a roof-open, full-footprint cutaway. The preview clips the exterior walls at the estimated story midpoint and displays two illustrative bedroom modules in context; it is not an as-built interior.

## Review evidence

- `evidence.json` — source register, identity evidence, CRS/transform, dimensions, uncertainties, and limitations.
- `source_observation.json` — exact HUBERart Etsy drawing URL and retrieval date. The listing prohibits duplicating its image, so no copy is saved.
- `purdue_gis_fid764_2026-10-28_3857.json` and `purdue_gis_layer_0_metadata_2026-10-28.json` — fresh official ArcGIS response and layer metadata. The response exactly matches the pre-existing `source_feature_764_raw.json`; the live layer metadata and response declare WKID 102100/latestWkid 3857.
- `plan_overlay.png` and `plan_comparison.json` — source ring vs. saved structural wall-base segments. Maximum boundary vertex error is 0.000058 m and RMS error is 0.000041 m because the wall shell is constructed directly from that transformed ring. This does not independently validate the GIS ring against a current survey or aerial.
- `exterior_three_quarter.png` and `schematic_upper_rooms.png` — brighter exterior and full-footprint roof-open cutaway. Interior arrangement remains invented and schematic.
- `fresh_open_validation.json` — Blender 5.2.3 fresh-open PASS, stable names/transform, one exported object, and updated mesh health counts.

The current mesh has 543 boundary/non-manifold edges. It remains a visual composite rather than a watertight solid.

## Open uncertainty

The two-level interpretation conflicts with `NUM_LEVELS=1`; `Extrution=12` has undocumented units/meaning. Wall height, roof cap height/type/coverage, fenestration spacing, and interior arrangement remain estimates. The low-profile roof cap has no ridge axis, avoiding an unsupported directional claim. The source illustration is qualitative and does not establish current as-built conditions.

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
