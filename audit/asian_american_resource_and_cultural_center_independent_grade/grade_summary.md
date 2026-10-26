# Independent AAARCC grade

**Score: 8.5/10 — PASS** (8/10 threshold)

| Criterion | Score | Evidence and limitation |
|---|---:|---|
| Correct identity and source-backed footprint | 2.0/2 | Official Purdue GIS feature 926 identifies AACC; the 20 unique WGS 84 polygon vertices match the saved GIS plinth to 0.000000231 m maximum bidirectional nearest-vertex distance. This does not establish the exact structural-wall line. |
| Position, orientation, and scale/dimensions | 1.5/2 | One master marker matches manifest XY within 0.000014 m, with zero rotation, unit scale, and the relative expected library path. House-wall/porch dimensions were inferred from photos rather than measured plans; evaluated model bounds differ from manifest bounds by at most 0.03 m. |
| Evidence-backed height, floors, and roof form | 1.0/2 | Official photos support two visible storeys and a steep gable roof. GIS fields report one floor and `Extrution=12` with no documented vertical units; 10.05 m total height and exact roof datums remain estimates. |
| Facade, entrances, and distinctive architecture | 2.0/2 | Official facility images and emergency-plan descriptions support clapboard, sash-window rhythm, porch/front entrance, sign, gable roof, accessible entry/ramp, and rear kitchen door. These appear in the current saved preview. |
| Modular export, portability, and complete evidence | 2.0/2 | Fresh reopen found 433 objects matching the current manifest. A separately exported collection reopened in Blender 4.5.15 with 433 objects and no cameras/lights; the asset has no external libraries, unpacked image dependencies, or unmaterialed meshes. |

The evaluator directly inspected the saved asset and master marker, compared the raw GIS polygon with the model plinth, checked the current manifest contract, and created/reopened an independent collection export. Height and the exact structural wall line remain uncertain. The saved builder/evidence score was not used.

Run `python evaluate.py` from this folder to reproduce `result.json`. The review changed only files in this independent audit folder.
