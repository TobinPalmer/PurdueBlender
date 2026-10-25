# Purdue Memorial Union — independent R2 grade

**Score: 7.9/10 — does not meet the 8.0 pass threshold.** This is an independent, criterion-level review of the saved PMU modular asset. It is a modest improvement over R1's 7.7/10, primarily from the clearer lower wing gables, corrected south wing depth, and staged tower glazing. The model still needs a roof and facade refinement pass.

## Asset and verification

- Asset: `modular/buildings/purdue_memorial_union.blend`
- Fresh reopen SHA-256: `9e68eac0b432b108dd1298b0b078f5337e2402d8063e6393f1abdb61f9667aaa`
- Collection: `Asset_purdue_memorial_union`; 577 objects, 541 mesh objects.
- Root transform: identity. All meshes have materials; no unpacked external images.
- R2 validation reports all 18 original wall/base bounds unchanged against immutable original audit bounds; 3 base pieces are additive and 5 original roof pieces were replaced with 20 R2 roof objects.
- Review evidence includes `validation_r2.json`, `independent_reopen_r2.json`, `grader_south_oblique_r2.png`, `grader_west_oblique_r2.png`, `grader_roof_r2.png`, and `south_facade_detail_r2.png`.

## Criterion scores

| Criterion | Score | Assessment |
|---|---:|---|
| Identity and source-backed footprint | 1.8/2.0 | Recognizable PMU tower-and-wing structure; the immutable historic structural baseline confirms all 18 original wall/base bounds at 0.0 m delta. The GIS is historical and approximate. |
| Placement, orientation, and scale | 1.9/2.0 | Asset root is at identity; prior read-only master marker record reports expected `(205.75, -271.65, 0)` placement, zero rotation and unit scale. Master placement was not freshly reopened for this review. |
| Evidence-backed height, floors, and roof form | 1.2/2.0 | Five lower separate wing gables and narrow eave/ridge caps improve silhouette; south roof depth is corrected. But broad slate planes still dominate, roof/courtyard transitions remain awkward, and total height, floor spacing and roof elevations remain estimates without measured elevations. |
| Facade rhythm, entrance, and distinctive architecture | 1.4/2.0 | Arched windows, stone archivolts, staged tower glazing and entry articulation are meaningful progress against the 1924 and 2024 photos, but wing openings and tower/portal details remain simplified and repetitive. |
| Modular portability and evidence/validation | 1.6/2.0 | Fresh reopen and portability checks are sound, provenance is documented, and baseline comparison is now immutable. The shared manifest still reports object count 414 while the asset has 577; a master reload is also still needed after acceptance. |
| **Total** | **7.9/10** | **Below pass threshold** |

## Findings to address

1. Refine the roof silhouette and intersections: make each wing's lower ridge and eaves read distinctly in oblique views, reduce the remaining canopy-like planes, and clean the central/courtyard junction while preserving the corrected south wing depth.
2. Compare the tower glazing proportions, south wing window rhythm, and entry stonework directly to the references; keep sculptural additions source-supported.
3. Keep total height, floor spacing, eave and ridge elevations labeled as estimates unless measured elevation evidence is found.
4. Reconcile the PMU `object_count` in the shared manifest (currently 414 versus the reopened asset's 577) and reload/check the master after the coordinator integrates the asset.

## Source and review limits

The visual comparison used the Purdue Libraries Archives photograph from 1924 and Purdue University's 2024 centenary exterior image; they show different dates and viewpoints, so their use supports qualitative architecture comparisons only. Historic GIS supports footprint/phase context, not current height or detailed roofs. Master placement relies on the existing read-only marker record; this grading pass did not edit or write the master, shared manifest, or asset.

The score and evaluator data are in `independent_grade_r2.json`; the executable scoring function is `evaluate_pmu_r2.py`. This report uses unique R2 filenames and preserves all earlier grades.
