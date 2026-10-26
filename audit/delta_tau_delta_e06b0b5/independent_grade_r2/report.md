# Delta Tau Delta — independent regrade R2

**Score: 8.25/10 — pass** (minimum 8/10).

| Criterion | Points |
|---|---:|
| Correct identity and source-backed footprint | 2 / 2 |
| Position, orientation, and scale/dimensions | 2 / 2 |
| Evidence-backed height, floors, and roof form | 1 / 2 |
| Facade, entrances, and distinctive architecture | 1.5 / 2 |
| Modular export, portability, and complete evidence | 1.75 / 2 |

I reopened `modular/buildings/massing_delta_tau_delta_e06b0b5.blend` in Blender 4.5.15 LTS. The expected scene and collection exist; the target collection contains 85 objects. There are no modifiers or external libraries. The full scene also contains a default Cube, Camera and Light outside the target collection. The asset SHA-256 is `f1dfb1418fb4d003bb4bd3a333c2a137ed0b3f923db5876653769505aa639283`.

I directly inspected the Purdue_Delts profile image cited in the evidence snapshot. X itself returns 403 to the web fetcher, so I retrieved its displayed profile image through the public image proxy `https://unavatar.io/x/Purdue_Delts` on 2026-10-26 (400×400 pixels). It visibly includes the house and a sign reading “DELTA TAU DELTA / GAMMA LAMBDA / ... / 400 NORTHWESTERN.” The image shows red brick, multiple front-facing gables, rows of rectangular windows, a steep roof and a masonry arched entry. This resolves the identity and supports those broad architectural traits, improving the first and fourth criteria over R1. The snowy, cropped oblique view does not establish exact bay count or spacing, complete elevations, measured heights, floor count, roof pitch, chimney layout, entrance side, or the 1970 addition seam.

The six projected vertices of 2018 Indiana LiDAR feature 409940 match the reopened shell's six base vertices with symmetric nearest-vertex maximum error **0.000013 m**. The structural XY bounds agree with that source polygon in campus coordinates.

The score is **8.25**, with no deduction for the shared manifest mismatch because `modular/manifest.json` is coordinator-owned under the repository rules. The mismatch is still a required integration fix: the manifest currently says one object and retains the old bounds, while the asset now has 85 collection objects and expanded world bounds `[[310.6398, 336.5239], [60.2652, 104.3046], [0.0, 17.4]]`. Please update the manifest/index before integrating this asset. The plan preview remains roof-dominated and clipped at the north/south image edges; this accounts for the small modular-evidence deduction. Height and floor-count uncertainty remains a model limitation, but is accurately labeled in the evidence.

Reproducible artifacts in this folder: `evaluate.py`, `result.json`, and `reopen_inspection.json`.
