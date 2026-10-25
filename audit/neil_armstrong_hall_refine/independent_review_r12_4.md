# Neil Armstrong Hall — independent R12.4 review

**Grade: 7.6/10 — below the 8.0 completion threshold.** The roof outline now has useful, source-registered orthophoto evidence, and the fresh reopen/export checks pass. The asset still lacks verified wall registration and roof height/profile, and the current image comparisons show noticeable facade and canopy differences.

## Revision and file checks

I independently hashed `modular/buildings/neil_armstrong_hall.blend`: `fd6a8c7dcbdd21eab4d94ae3a9b38d72d87069260e059996ab689d432927c62e`, matching the requested R12.4 revision and `validation_r12_4.json`. The validation reports a fresh Blender 5.2.3 reopen, 445 collection objects, 415 meshes, identity root transform, material assignments on all meshes, and no external image dependencies.

The manifest’s local asset placement is `[-109.0, 400.1893310546875]` m. Prior read-only R11 review verified the master marker matches this origin with zero rotation/unit scale. This confirms the link origin, not that the building’s walls align correctly on campus.

## Criterion scores

| Criterion | Score | Evidence and deduction |
| --- | ---: | --- |
| Identity and source-backed footprint | 1.55/2 | Purdue GIS feature 642 identifies the building, and the roof/eaves trace follows the 2023 orthophoto. It does not establish structural wall/courtyard edges. |
| Position, orientation, and scale | 1.55/2 | Local origin and manifest/master marker agree. The camera photos are not heading/roll calibrated, and no wall-level GIS registration or facade stationing is shown. |
| Height, floors, and roof form | 1.40/2 | Primary sources support the level count, atrium, and folded-canopy concept; aerial imagery supports roof plan. Heights and roof warp remain inferred, and comparison views still show a materially different canopy silhouette/proportion. |
| Facade, entrances, and distinctive features | 1.30/2 | Brick, glazing, and the large canopy are recognizable. Window rhythm and wall segmentation remain generic; the courtyard view also contains an opaque blue obstruction masking part of the facade. |
| Modular export, portability, and evidence | 1.80/2 | Fresh reopen, object/material checks, stable local root, and self-contained images pass. The evidence is extensive but has no dimensioned public roof/elevation plan or verified wall registration. |
| **Total** | **7.60/10** | **Not passed** |

## Findings and next steps

1. Register the architectural walls against the correct GIS polygon or a dimensioned plan; keep the roof/eaves trace separate from the wall footprint.
2. Refine the canopy shape against multiple attributed views. Keep inferred heights and structural interpretation labeled as estimates until measured evidence is available.
3. Identify/remove the opaque courtyard obstruction, then compare facade opening cadence and canopy proportions against the source photographs.

The orthophoto supports roof/eaves plan geometry only. It does not establish wall centers, building heights, or structural interpretation. The executable evaluator and JSON result are in `independent_evaluator_r12_4.py` and `independent_grade_r12_4.json`.
