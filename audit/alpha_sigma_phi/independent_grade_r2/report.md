# Alpha Sigma Phi — independent grade, round 2

**Score: 7.5/10 — below the 8/10 completion threshold.** The footprint and horizontal placement are excellent. The updated model is clearer about its unresolved assumptions, and the review cutaway is easier to read, but those presentation changes do not resolve the unsupported height, level count, facade, or room plan.

| Criterion | Score | Assessment |
| --- | ---: | --- |
| Correct identity and source-backed footprint | 2.00/2 | Purdue GIS FID 763 identifies Alpha Sigma Phi at 951 David Ross Road. Fresh-open geometry matches all 8 source vertices within 0.000062 m; the Esri aerial overlay follows the L-shaped roof plan. |
| Position, orientation, and scale/dimensions | 2.00/2 | The expected scene, collection, root, and direct campus coordinates reopen correctly. The two principal wings follow the GIS orientation; plan bounds are about 31.4 by 43.9 m. |
| Evidence-backed height, floors, and roof form | 0.75/2 | Aerial imagery supports the L-shaped roof plan and broad low-slope/flat-looking surface. No target elevation or measured height is available. GIS reports one level while the model shows three; `Extrution=34` has no documented unit. The builder now correctly marks its height as an estimate. |
| Facade, entrances, and distinctive architecture | 0.75/2 | The model has dark procedural brick, repeated framed windows, and an entry canopy/steps. The current render still looks like a generic brick residence; available Street View does not clearly show this building, so facade finish, window rhythm, and entrance location remain unverified. The cutaway is labeled schematic but does not represent a sourced floor plan. |
| Modular export, portability, and complete evidence | 2.00/2 | Fresh-open source retains its stable scene, collection, and root. The asset has 851 meshes and 9 node-based materials; the brick shader is procedural. GIS, imagery, provenance, builder, validation, and review previews are present. |

## What changed in this revision

The builder now explicitly labels the 10.36 m height and three-level arrangement as estimates, rather than inferring a unit for the GIS extrusion attribute. The interior is explicitly described as schematic. The new review-only cutaway adds labels and more legible colors. These are good evidence-handling improvements, but they do not improve the building's source-backed facade or floor-plan accuracy enough to pass.

## Needed before a passing regrade

1. Obtain a clear, target-facing Alpha Sigma Phi facade or reliable elevation/plan to resolve height and story count; do not treat GIS `Extrution=34` as feet without a source.
2. Refine roof profile, windows, and entrance only from target-specific evidence. Keep the GIS footprint intact.
3. If a real floor plan remains unavailable, continue labeling the interior illustrative; don't represent the schematic layout as verified.

The detailed criterion scores, fresh-open measurements, source paths, and asset SHA-256 are in [`result.json`](result.json); the evaluator is [`evaluate.py`](evaluate.py).
