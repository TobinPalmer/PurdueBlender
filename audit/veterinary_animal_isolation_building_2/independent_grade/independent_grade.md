# Independent grade: Veterinary Animal Isolation Building 2

**Grade: 8.00 / 10 — pass at the 8.00 threshold.** This is a marginal pass with material unresolved evidence conflicts, not a claim of fully verified architecture.

## Criterion scores

| Criterion | Score | Basis |
|---|---:|---|
| Correct identity and source-backed footprint | 2.00 / 2 | Purdue GIS FID 942 identifies VA2; fresh-open comparison found the foundation bbox agrees with the converted polygon bbox within 0.00000067 m. The GIS area attribute conflicts with the geometry. |
| Position, orientation, and scale/dimensions | 1.75 / 2 | The recorded origin is the GIS bbox center and the long north-south orientation/dimensions match. The outer modeled envelope extends up to roughly 0.20 m past the foundation edges for facade/louver details. Campus placement in the master was outside this asset-only review. |
| Evidence-backed height, floors, and roof form | 1.25 / 2 | GIS says one level; Purdue OEP says two floors with an HVAC interstitial. Roof form and equipment arrangement have aerial support. Heights are estimates and component details are not fully established. |
| Facade, entrances, and distinctive architecture | 1.00 / 2 | The model has coherent service-building facade bands, louvers, sparse openings, and entrances, but these details lack elevation or street-view verification. |
| Modular export, portability, and complete evidence | 2.00 / 2 | Blender 5.2.3 reopened the saved asset in a clean process; expected scene/collection/ID were present, with 1,113 local meshes, 13 procedural materials, no image files, and no linked libraries. |

## Findings

- **GIS area mismatch:** the feature reports `Shape__Area=838.125 m²`, while the source polygon vertices give approximately **484.91 m²** using the asset's local tangent projection; its bounding rectangle is **526.98 m²**. The candidate correctly models the vertices directly rather than scaling to the conflicting area attribute, but the provider discrepancy remains unresolved.
- **Cutaway preview artifact:** `preview_interior_cutaway.png` has floating rooftop equipment and wall fragments because the preview script hides roof and wall shells while leaving some associated objects visible. This is specific to the cutaway rendering. The normal exterior preview and fresh-open geometry show roof-mounted items at the roof plane (a sampled unit starts at z=4.617 m against a roof plane near 4.62 m).
- **Architectural uncertainty:** no elevation evidence verifies facade materials, exact opening rhythm, entrances, actual height, HVAC type/count, or interior plan. Interior animal-care spaces are explicitly illustrative.

## Reproduction/evidence files

- `evaluator.py` computes the rubric and writes `result.json`.
- `fresh_open_probe.py` was run by Blender 5.2.3 in a separate process; its measurements and file hash are in `fresh_open_probe.json`.
- The reviewed source evidence and renders are linked in `result.json`.
