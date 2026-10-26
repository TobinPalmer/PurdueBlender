# Independent Black Cultural Center grade

**Score: 9.0/10 — PASS** (8/10 threshold)

| Criterion | Score | Assessment |
|---|---:|---|
| Correct identity and source-backed footprint | 2.0/2 | Purdue GIS FID 645 identifies BCC at 1100 3rd Street. Its 61 unique WGS 84 ring vertices match the evaluated structural shell to 0.0000011 m maximum bidirectional nearest-vertex distance under the documented local approximation. |
| Position, orientation, and scale/dimensions | 2.0/2 | One master placement marker matches the refreshed manifest origin within 0.00002 m, with zero rotation, unit scale, and the expected relative library link. GIS and shell XY bounds match within about 0.000001 m. |
| Evidence-backed height, floors, and roof form | 1.0/2 | Official sources support multiple floors and the roof form, but the 9.06 m model height is an estimate. GIS `Extrution=24` has no resolved vertical units; no measured elevation or architectural plan was found. |
| Facade, entrances, and distinctive architecture | 2.0/2 | Purdue sources support the geometric brickwork, keyhole portal and medallions, octagonal glazed lobby, cast-stone trim, entry and balcony; the saved render shows those features. |
| Modular export, portability, and complete evidence | 2.0/2 | Current asset has 621 objects, matching the coordinator-refreshed manifest names/count. Isolated canonical rebuild reproduced the object transforms and mesh vertex data; an independently exported collection reopened with 621 objects and no cameras/lights. No external libraries, unpacked images, or unmaterialed meshes were found. |

Height and roof datums remain the main uncertainty. The old reopen snapshot in `sources/prior_reopen_validation_snapshot.json` predates the manifest refresh and reports 623; this review independently reopened the current 621-object asset and used the current 621-object manifest.

See [result.json](result.json), [evaluator](evaluate.py), direct Blender probes, independent export files, raw source snapshots, and both current and smoke-rendered views in this folder. No building or shared-index files were modified.
