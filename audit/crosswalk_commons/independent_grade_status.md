# Crosswalk Commons independent grade

**Status: PASS — 8.1/10** (minimum 8/10), independent evaluation completed against the saved asset and source evidence on 2026-10-26.

The evaluator, Blender probe, probe report, and full result are preserved in this folder as `independent_evaluate.py`, `independent_grade_probe.py`, `independent_grade_probe.json`, and `independent_grade_result.json`. The result contains the criterion-level scores and evidence:

| Criterion | Score |
| --- | ---: |
| Identity and source-backed footprint | 2.0/2 |
| Position, orientation, and dimensions | 2.0/2 |
| Height, floors, and roof | 1.3/2 |
| Facade, entrance, and distinctive architecture | 0.8/2 |
| Modular export, portability, and evidence | 2.0/2 |

The evaluator verified OSM way 231217849 against the mesh ground ring (maximum nearest-vertex error 0.000037 m) and independently reopened the asset in Blender 4.5.15. The asset passed. Remaining uncertainty: 9.5 m roof height and three levels are inferred from photos, not measured; the main entrance location is approximate; and the ground-floor facade only partly captures the photographed stone entry wall, dark fascia, brick piers, and broad common-area glazing. These limitations are recorded in `independent_grade_result.json` and `sources_and_assumptions.json`.
