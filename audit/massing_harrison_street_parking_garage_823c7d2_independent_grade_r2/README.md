# Independent grade: Harrison Street Parking Garage

**Score: 7.4/10 — below the repository 8/10 threshold.** The score is based on direct inspection of the archived GIS, project/source record, aerial crop, validation outputs, rendered views, and a read-only reopen of the `.blend` in Blender 4.5.15.

| Criterion | Score |
|---|---:|
| Correct identity and source-backed footprint | 2.0/2 |
| Position, orientation, and scale/dimensions | 1.7/2 |
| Evidence-backed height, floors, and roof form | 1.0/2 |
| Facade, entrances, and distinctive architecture | 1.1/2 |
| Modular export, portability, and complete evidence | 1.6/2 |

The GIS match is strong: the builder uses Purdue GIS FID 892 (`PGH`, Harrison Street Parking Garage, 719 Clinic Drive) for the structural decks, with the documented campus transform. The saved asset reopened with the expected scene and collection and 542 mesh objects. Its structural deck bounds match the GIS bounds; expanded overall bounds come from appended features beyond the footprint.

The main gap is roof evidence. The archived Indiana aerial shows active rooftop parking and a central roof feature/open area, while the model/render shows a blank concrete roof slab with a small brick block. Floor count is supported by WGI, but story spacing, total height, entrance/ramp arrangement, facade rhythm, and the stair/service core placement remain estimates or unverified. The GIS's `NUM_LEVELS=7` and `CountOfFLO=6` fields conflict and vertical units are undocumented.

The saved file reports Blender 5.2 as its writer. It reopened in 4.5.15 for geometry inspection, with a newer-file warning; the saved `BLENDER_EEVEE` engine is unavailable in 4.5.15. No asset or source changes were made during this review.

Machine-readable evaluator and evidence: `grade_result.json`, `evaluate_harrison.py`, `direct_reopen_inspection.json`.
