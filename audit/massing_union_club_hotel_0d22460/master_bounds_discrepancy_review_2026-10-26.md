# Union Club Hotel master-bounds discrepancy review

Date: 2026-10-26  
Asset: `massing_union_club_hotel_0d22460`  
Owner: Rossen

## Finding

The master audit reports 28 linked scene objects, matching the manifest object count. Its calculated bounds are:

| Axis | Manifest bounds (m) | Master audit bounds (m) |
| --- | ---: | ---: |
| X | 235.514038–278.717224 | 235.514038–278.845215 |
| Y | -284.971375–-163.166000 | -284.971375–-163.166000 |
| Z | 0–21.750000 | 0–21.750000 |

Only maximum X differs, by 0.127991 m. The master audit calculates each linked scene object's `bound_box`. The earlier building reopen validation instead accumulated evaluated vertices from `MESH` objects only. The asset's 28-object collection has 27 meshes and one `FONT` curve object, `UCH_Entry_Hotel_Lettering`; its lettering is visible on the porte-cochère in the saved east-oblique preview. The curve contributes to the master audit's aggregate bound but was excluded from the mesh-only reopen measurement.

This is a manifest bounds omission, not evidence that the structural shell footprint or other modeled geometry should be rescaled. The explicit source footprint remains in `source_bounds_world_m` and the GIS shell match remains within the recorded 0.000019 m tolerance. Keep the model as-is; the shared manifest's `bounds_world_m[0][1]` should be refreshed to approximately `278.845215` m if the manifest convention is to cover all objects in the exported collection.

## Evidence

- `../rossen_master_integration_audit_2026-10-26.md`: reports the 0.128 m maximum-X difference and confirms the asset is linked.
- `../../work/rossen_master_bounds_summary.txt`: full master calculation shows expected X maximum `278.71722412109375` and actual `278.84521484375`; Y and Z bounds match.
- `reopen_validation.json`: confirms 28 collection objects, 27 meshes, the 53-vertex GIS shell match, and the mesh-only aggregate bounds.
- `independent_grade_r2.json`: confirms 28 collection objects and the object-level evidence/limits; asset SHA at grading is recorded there.
- `renders/east_oblique.png`: shows the entrance lettering on the porte-cochère fascia.

No Blender asset or shared manifest was changed during this review.
