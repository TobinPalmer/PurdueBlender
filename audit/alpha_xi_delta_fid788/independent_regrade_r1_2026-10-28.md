# Independent regrade — Alpha Xi Delta, FID 788

**Reviewed:** 2026-10-28  
**Asset:** `modular/buildings/massing_house_301841248_fe939c7.blend`  
**Verified SHA-256:** `95AAF80107165DFCF9EF43FBA15835B995F78949FCA71AF4A956715229AC989A`  
**Result:** **8.07/10 — PASS** (threshold 8.0)

This is an independent read-only review of revision 1. I preserved the earlier 7.6/10 report, which applies to the previous SHA only. I fresh-opened the exact saved file in Blender 5.2.3 LTS and confirmed the scene and collection, 37 mesh objects, stable root `House_301841248` (48 vertices), zero cameras/lights, and no image datablocks.

## Weighted score

| Category | Weight | Score / 10 | Weighted points | Evidence and limits |
|---|---:|---:|---:|---|
| Identity and provenance | 20% | 9.5 | 1.90 | GIS FID 788 identifies Alpha Xi Delta at 519 University St. The audit now records official Purdue Panhellenic and 2008 Wikimedia property references with source context; supplementary house art is distinguished as illustrative. |
| Plan geometry and placement | 25% | 9.0 | 2.25 | All 24 source ring vertices are used and the saved comparison reports 0.000016 m max symmetric vertex distance. This match is by construction using the same source ring and an approximate local conversion; it does not independently verify the survey, facade lines, or campus placement. |
| Exterior silhouette and openings | 25% | 6.5 | 1.63 | Tudor brick/cream composition, entrance, windows and three dormers read clearly and follow visible cues. The render has a conspicuous broad uncovered roof/courtyard-like gap through which interior surfaces show; the references do not establish such an opening. Roof transitions, detailed opening rhythm, height and unseen sides remain estimates. |
| Materials and facade | 10% | 8.5 | 0.85 | Brick, cream plaster, dark timber, charcoal roof and blue-gray windows now have readable contrast and broadly match the photos. Smooth procedural surfaces remain simplified. |
| Interior and cutaway clarity | 10% | 7.5 | 0.75 | The fresh-open ground-floor cutaway shows partitions and furniture and is qualified as schematic. The cutaway is sparse, has no source floor plan or measured room arrangement, and does not itself establish as-built room functions. |
| Presentation and technical | 10% | 7.0 | 0.70 | Fresh-open passed with stable scene/root, portable materials, no external images, and no saved cameras/lights. However, the live asset collection and scene contain 37 objects while the current shared manifest entry still declares `object_count: 1` and lists only the root object; coordinator integration must reconcile this contract. |
| **Total** | **100%** |  | **8.075 / 10 = 8.1/10** | **PASS** |

## Remaining limitation

The uncovered roof area is the clearest visible source-fidelity defect and should be closed or explicitly evidenced before final campus integration. Heights, roof form, window placement, interior layout and unseen elevations remain estimates. `NUM_LEVELS=1` and GIS `Extrution=12` are not treated as verified height/story evidence.

## Evidence reviewed

- `review_handoff.md`, `revision_report_r1.md`, `model_evidence.json`, `source_fid788.json`, `footprint_comparison.json`, and `footprint_overlay.svg`.
- `exterior_preview.png`, `interior_cutaway_preview.png`, `facade_reference_current.png`, and `facade_reference_2008.png`.
- Fresh-open check executed against the exact saved file in Blender 5.2.3 LTS; SHA rechecked after opening.

No asset, source, manifest, or shared project file was modified during this review.
