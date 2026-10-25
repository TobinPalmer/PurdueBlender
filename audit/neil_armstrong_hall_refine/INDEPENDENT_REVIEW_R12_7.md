# Neil Armstrong Hall — independent R12.7 review

**Grade: 7.65/10 (reported as 7.7/10; below the 8.0 pass threshold).** I inspected the saved R12.7 asset, independently reopened it in Blender 5.2.3, rendered fresh current-revision views, and compared those views with the cited 2016 photographs and 2023 Indiana orthophoto.

## Saved-file verification

The saved asset SHA-256 is `a85ef78d82e5c50b09fcd4fb7bc191798fad0132a9a89b84297203186f2ae549`, matching R12.7. The fresh Blender probe confirms the expected `Asset_neil_armstrong_hall` collection, 445 objects, 415 meshes, identity root transform, no unassigned/null mesh materials, and no missing external images. The canopy object has 379 vertices and 363 faces, with bounds approximately `[-70.299, 77.797] × [-7.78, 27.49] × [4.95, 21.5]` m.

## Criterion scores

| Criterion | Score | Evidence and deduction |
| --- | ---: | --- |
| Correct identity and source-backed footprint | 1.55/2 | Purdue GIS feature 642 and the attributed campus photographs identify the building. The orthophoto trace supports roof/eaves plan, but the generalized GIS shape and eaves trace do not verify the structural walls or courtyard edges. |
| Position, orientation, and scale/dimensions | 1.55/2 | The fresh asset root is at local origin; prior independent master review found the placement marker aligned with the manifest. Photo headings and roll are unavailable, and facade registration/dimensions remain unverified. |
| Evidence-backed height, floors, and roof form | 1.35/2 | Source material supports four levels, the atrium, and a folded wing-like canopy. The current canopy profile/height remains inferred from photos and a coarse LiDAR ceiling. Fresh views still show substantial canopy thickness/proportion differences and a very dark underside compared with the cited photos. |
| Facade, entrances, and distinctive architecture | 1.40/2 | The new upper glazing band and mullions are based on photo 02, the low entrance deck is restored, and the prior blue obstruction is gone from the clear comparison view. The current facades still read as broad simplified brick faces with a generic upper strip and sparse openings relative to the large curtain-wall zones visible in the 2016 photos; the canopy-to-entrance relationship remains approximate. |
| Modular export, portability, and evidence | 1.80/2 | Fresh reopen, collection/root, materials, and image dependencies pass. Evidence includes source photographs, orthophoto tracing, validation, and current-revision renders. No dimensioned as-built plan/elevation supports the remaining geometry. |
| **Total** | **7.65/10** | **Not passed** |

## Findings for the next revision

1. Keep the roof/eaves trace separate from the structural wall footprint. Find a measured plan or stronger registration for the walls and courtyard before adjusting wall geometry.
2. Refine the cantilever underside and its height profile against multiple photographs. Label inferred heights as estimates; the 21.5 m peak is not a surveyed dimension.
3. Improve the glass-to-brick facade segmentation, window cadence, and entrance/canopy transition from the source photos. The new upper band is a useful reference-based addition, but its cadence is not dimensionally registered.
4. Keep camera bearing/roll uncertainty explicit: the geotag photos are qualitative view references, not calibrated facade comparisons.

## Evidence files

- Independent Blender inventory and portability probe: `independent_probe_r12_7.json`
- Current-revision rendered views: `renders_independent_r12_7/`
- Evaluator and machine-readable grade: `independent_evaluator_r12_7.py` and `independent_grade_r12_7.json`
- Builder validation and source notes: `validation_r12_7.json`, `evidence_r12_7.json`, and `source_review_r12.md`
