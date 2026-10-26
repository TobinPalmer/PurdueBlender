# Independent Class of 1950 grade — revision 2

**Score: 8.5/10 — PASS** (threshold 8/10)

| Criterion | Score | Result |
|---|---:|---|
| Correct identity and source-backed footprint | 2.0/2 | GIS FID 230 identifies CL50; 29 source vertices compared with the 82-point wall-envelope base. Max source-to-model vertex distance 0.000579 m. |
| Position, orientation, and scale/dimensions | 2.0/2 | Exactly one master marker; origin matches manifest, zero rotation, unit scale, relative asset link. Footprint extent deltas are under 0.0005 m per axis. |
| Evidence-backed height, floors, and roof form | 1.0/2 | Three-floor GIS fields and low-parapet roof photos support floors/roof form. 18.9 m height remains unverified; GIS `Extrution=36` is undocumented. |
| Facade, entrances, and distinctive architecture | 2.0/2 | Purdue source text/photos support curved brick-and-glass frontage, round brick columns, pale bases/capitals, glazed upper wall, and soffit; these appear in the model views. |
| Modular export, portability, and complete evidence | 1.5/2 | Current builder package-copy/reopen passed byte-identically with 2,431 objects; no external libraries, unpacked image files, or unmaterialed meshes. Deduction for null manifest evidence pointers and Blender 4.5.15 newer-file/Eevee warning. |

The evaluator was run fresh against the current asset and manifest, with read-only asset/master probes. The builder smoke test ran from a copied project tree and wrote only inside this audit folder. No assigned building file or shared index was changed.

See [result.json](result.json), [evaluator](evaluate.py), and the `sources/`, `views/`, and probe/package logs beside this report. The nearest-vertex results describe coordinate agreement and tessellation; they are not polygon IoU or surveyed wall-error measurements.
