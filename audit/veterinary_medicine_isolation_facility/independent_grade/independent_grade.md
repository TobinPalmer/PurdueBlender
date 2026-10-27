# Independent grade — Veterinary Medicine Isolation Facility (VMIF)

**Score: 7.75 / 10 — below the 8.00 passing threshold.** The model exports cleanly and follows the saved GIS perimeter, but the exterior remains visually generic and key vertical/form details are unsupported.

## Criterion scores

| Criterion | Score |
|---|---:|
| Correct identity and source-backed footprint | 2.00 / 2 |
| Position, orientation, and scale/dimensions | 1.75 / 2 |
| Evidence-backed height, floors, and roof form | 1.25 / 2 |
| Facade, entrances, and distinctive architecture | 0.75 / 2 |
| Modular export, portability, and complete evidence | 2.00 / 2 |

## Findings

- The saved 12-vertex wall outline matches the captured Purdue GIS ring to **0.00000094 m** maximum vertex error. Its scene anchor exactly matches the polygon centroid.
- The feature's GIS `Shape__Area` is **849.074 m²**, while its returned coordinates produce **491.252 m²** under the documented project projection. The candidate follows the polygon coordinates without scaling; the provider conflict remains unresolved.
- GIS reports one level, but wall height interprets `Extrution=12` as feet without documented units. The flat/low-slope roof is an assumption.
- The exterior preview has no doors or windows. Materials, roof details and facade treatment are assumptions. The cutaway's eight stalls and support/mechanical spaces align with the Archives program description, but their exact locations are schematic.
- A fresh Blender 5.2.3 process reopened the file. The exported collection has 70 local mesh objects, all assigned materials, no external images, and no linked libraries.

## Files

- `evaluator.py` computes the score and findings from the fresh-open probe and source snapshot.
- `fresh_open_probe.py` reopens and measures the exported asset in Blender.
- `fresh_open_probe.json` contains the saved measurements and asset hash.
- `result.json` contains criterion-level evidence, limits and the grade.
