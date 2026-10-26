# CQNW independent R2 evaluation

**Result: 8.0/10 — pass at the project minimum.** This is a narrow pass because the model is now a valid one-object export with a GIS-derived footprint, while building-specific facade and entrance evidence is still unavailable.

## Criterion scores

| Criterion | Score | Assessment |
|---|---:|---|
| Identity and source-backed footprint | 2.0/2 | Official Purdue GIS FID 647 identifies CQNW. The simplified shell boundary is within 0.42 m of all raw source vertices at the worst sampled point (0.07 m mean). |
| Position, orientation, and dimensions | 2.0/2 | The candidate is in the documented campus frame with identity object transform. The projected GIS polygon and 2023 orthophoto support its site placement, long axis, and plan. Coordinate conversion remains approximate. |
| Height, floors, and roof form | 1.5/2 | 2018 NDHM samples support the 14.9 m ridge estimate and the orthophoto supports a long gabled roof with interruptions. Ridge/eaves and the interpretation of the five-level GIS count remain uncertain. |
| Facade, entrance, and distinctive architecture | 0.5/2 | A 1928 Cary photo offers only complex-level historical context. No CQNW-specific elevation or photograph substantiates the modeled window pattern, materials, arch, or entrance placement. |
| Modular export, portability, and evidence | 2.0/2 | Fresh Blender 4.5.15 reopen finds exactly one named mesh in the expected asset collection, with no modifiers or missing external image dependencies. Source snapshots and validation records are present. |

## Findings

The asset reopened successfully with the expected scene and asset collection. The collection contains one mesh named `Cary Quadrangle Northwest (CQNW)`, evaluated bounds are approximately 1014.35 × 965.40 × 14.90 m, and object location/rotation/scale are identity. The candidate SHA-256 recorded in `result.json` identifies the exact saved file inspected.

The GIS feature provides a strong identity and footprint basis. I compared the original 112-vertex polygon from FID 647, transformed with the documented campus approximation, against the actual bottom boundary face of the reopened mesh. The maximum source-vertex-to-model-boundary distance is 0.4192 m and the mean is 0.0709 m. This reflects the stated 0.5 m simplification. The aerial overlay supports the roof plan and repeated roof interruptions, and the NDHM analysis supports a plausible overall top height; neither establishes facade details or surveyed ridge/eave heights.

The facade and entrance remain an explicit source gap. The dated 1928 photograph predates CQNW and does not identify a specific Cary building. The CQNW-specific Architect Folder 8 catalog record is a physical archive lead only. The model’s pointed arch, entrance location, window spacing, and exact facade materials therefore remain interpretations. Do not describe these as verified architectural details.

## Reproduction

`reopen_probe.py` opens the saved asset in Blender 4.5.15, evaluates the named mesh, checks transforms/modifiers/dependencies, and compares its foundation boundary with the raw GIS polygon. See `blender_probe.json` and `blender_reopen.log`. `evaluator.py` returns the required `{score, max_score, criteria, evidence, findings}` object in `result.json`.
