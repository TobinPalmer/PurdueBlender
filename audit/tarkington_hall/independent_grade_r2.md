# Independent Tarkington Hall R2 grade

**Result: 5.9/10 — does not pass the 8.0 threshold**  
**Reviewed asset:** `modular/buildings/tarkington_hall.blend`  
**SHA-256:** `75aad771c9da9e454bbea76ef48852519fa58997747547f9120977e81a6aede5`  
**Fresh reopen:** Blender 5.2.3 LTS

## Scope and exact-file verification

I freshly opened the canonical library, checked its SHA, and inspected the named `Asset_tarkington_hall` export collection. The root transform is identity, the 5.6 × 4.4 m Room 118 floor is present, and the asset has valid assigned materials, no invalid indices, no non-finite meshes, no missing external images, and no external linked libraries.

The scene contains 910 objects, but `Asset_tarkington_hall` contains only 814. Ninety-six connector objects, including the two added connector shells and their windows, are linked only to `Scene Collection`, outside the named export. The supplied R2 orthophoto overlay and shell-union calculation include those objects, but the project manifest/master link exports only `Asset_tarkington_hall`. Recomputing the shell union from export-collection members gives IoU 0.630, mean boundary residual 2.22 m, P95 9.59 m, and Hausdorff 11.68 m. This is a blocking delivery defect.

## Scorecard

| Criterion | Score | Evidence |
| --- | ---: | --- |
| Identity and source-backed footprint | 1.4/2.0 | Purdue GIS feature FID 662/code TARK matches Newton Booth Tarkington Residence Hall. A georeferenced Indiana 2023 orthophoto provides independent roof-edge context. The delivered export-collection shell union has IoU 0.630, mean symmetric boundary residual 2.22 m, P95 9.59 m, and Hausdorff distance 11.68 m. The GIS outline is not documented as a surveyed wall line. |
| Position, orientation, and scale/dimensions | 1.0/2.0 | The export-collection shell centroid is about 0.49 m west and 1.65 m south of the transformed GIS centroid; axis bounds are similar. The exhaustive master audit still records position and orientation errors as unverified. No surveyed wall dimensions or measured orientation comparison were supplied. |
| Massing, floors, height, and roof form | 1.3/2.0 | The model reads as a four-arm residence hall with central core, four occupied floors, flat roof masses, and roof equipment. Purdue's emergency plan supports the four-floor program. The model height is about 19.1 m, but no measured elevation supports that value; roof/penthouse heights and the core outline remain estimates. |
| Facade, entrances, and distinctive architecture | 1.4/2.0 | The exterior render has a readable brick residence-hall form, repeated window bays, light bands, roof equipment, and a recognizable central entrance. The wing and opening revisions are visible. Most of the newly added connector structure and associated windows are absent from the exported collection. |
| Modular export, portability, and evidence | 0.8/2.0 | Fresh reopen and dependency/material checks pass; the export root is intact. However, 96 connector objects are outside the named export collection, so the master library link omits them. Source, orthophoto, room, footprint, and change evidence is extensive, but it does not compensate for the collection membership error. |
| **Total** | **5.9/10** | **Below threshold** |

## Required corrections

1. Move the intended connector shell, trim, roof, and window objects into `Asset_tarkington_hall`; reopen the canonical asset and verify the collection contains them.
2. Re-run the structural-shell union and orthophoto overlay using only objects inside the export collection. Investigate the central-core discrepancy and retain the GIS wall-versus-roof uncertainty.
3. Reopen the campus master read-only and record a direct placement-marker position/orientation check.
4. Keep the dorm-room dimensions labeled approximate and provide an additional supported interior view if the existing interiors are part of the deliverable.

## Evidence files

- Exact-file inspection: [independent_reopen_r2.json](independent_reopen_r2.json), [independent_reopen_r2.py](independent_reopen_r2.py)
- Export membership audit: [independent_membership_r2.json](independent_membership_r2.json), [grade_membership_r2.py](grade_membership_r2.py)
- Source-backed footprint metrics: [footprint_comparison_r2.json](footprint_comparison_r2.json)
- Delivered export-only footprint metrics: [footprint_export_only_r2.json](footprint_export_only_r2.json), [export-only overlay](ortho_export_only_overlay_r2.png)
- Full-scene candidate orthophoto comparison: [ortho_footprint_overlay_r2.png](ortho_footprint_overlay_r2.png), [indiana_2023_ortho_r1.png](indiana_2023_ortho_r1.png)
- Exterior and room views: [exterior_r2.png](exterior_r2.png), [room_r6.png](room_r6.png)
- Reproducible evaluator: [independent_grade_r2_evaluator.py](independent_grade_r2_evaluator.py)
- Machine-readable score: [independent_grade_r2.json](independent_grade_r2.json)

The raw Purdue GIS source identifies FID 662 / TARK and was retrieved 2026-10-22; the Indiana 2023 orthophoto was retrieved 2026-10-25. The project's local geographic conversion is approximate rather than a surveyed projection.

## Source URLs reviewed

- [Purdue campus BuildingShapesZip4 GIS layer](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0), feature FID 662 / TARK.
- [Indiana 2023 Imagery ImageServer](https://di-ingov.img.arcgis.com/arcgis/rest/services/DynamicWebMercator/Indiana_2023_Imagery/ImageServer), orthophoto evidence dated Spring 2023.
- [Purdue Tarkington Hall housing page](https://www.housing.purdue.edu/my-housing/options/residence-halls/tarkington.html), residence features and approximate room dimensions.
- [Purdue Tarkington Hall emergency plan](https://www.purdue.edu/operations/emergency-preparedness/tark/), wing organization and occupied-floor information.
