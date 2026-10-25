# Independent DSAI Grade 1

**Asset:** `modular/buildings/massing_hall_of_data_science_and_ai_dsai_c8a41cc.blend`  
**Collection:** `Asset_massing_hall_of_data_science_and_ai_dsai_c8a41cc`  
**Blender reopen check:** passed in Blender 5.2.3  
**Score:** **7.5/10 — below the 8/10 pass threshold**  
**SHA-256:** `2a0673e7e9ef3261ed17392190b646b56af2adcfe4cf7bfac6eac8bb90f28a19`

## Evaluator result

The criterion evaluator is implemented in `evaluate_dsai_1.py`; the returned structured result is preserved in `evaluator_result_1.json`.

| Criterion | Score | Review |
|---|---:|---|
| Correct identity and source-backed footprint | 1.9 / 2 | Correct FID 196 identity; wall ring directly follows the official GIS ring. No independent aerial overlay confirms the polygon match. |
| Position, orientation, scale/dimensions | 1.7 / 2 | The registered plan orientation and size are carried into campus coordinates. Horizontal bounds differ by under 0.2 m because trim and details protrude. No separate top-down comparison against aerial or surveyed control is saved. |
| Evidence-backed height, floors, and roof form | 1.25 / 2 | Four levels are supported; total height is explicitly estimated. The three overlapping hipped roof masses create broad, awkward roof planes, with no roof-plan/aerial evidence to support their extents. |
| Facade, entrances, distinctive architecture | 0.95 / 2 | Red masonry, limestone bands, dark windows, and tile color broadly match the photos. Entry treatment is absent; the main corner lacks its prominent stone pier; the top-storey glazing does not match the tall, dense window rhythm in the architect photo. The repeated window pattern looks generic. |
| Modular export, portability, complete evidence | 1.7 / 2 | Stable path and collection; 45 meshes are contained in the asset; the saved file reopens; evidence, raw FID 196 data, and images are in the dedicated folder. No exterior aerial/top-down or interior review view is saved, and interior positions remain schematic. |

## Iteration findings

1. Rework the three roof forms to follow discrete wing geometry and remove the broad intersections across the middle. Compare against the MSKTD exterior and, if available, a top-down aerial.
2. Add the visible formal entrance and prominent limestone corner treatment supported by the architect image.
3. Make the upper storey distinct: taller, narrower glazing with the matching limestone band above the lower brick facade.
4. Save a top-down footprint alignment view and an interior/circulation view so plan registration and the schematic communicating stair/atrium are reviewable.

This grade is based on direct comparison of `dsai_exterior_review.png` with the locally saved MSKTD/Purdue photographs and the dedicated source record. The rendered model has a credible material palette and correct registered plan footprint, but the roof and signature facade details need another iteration before it meets the project threshold.
