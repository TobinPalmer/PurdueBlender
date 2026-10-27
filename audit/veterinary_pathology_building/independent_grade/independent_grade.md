# Independent grade: Veterinary Pathology Building (VPTH)

**Grade: 7.70 / 10 — below the 8.00 pass threshold.** The source footprint is an excellent match, but the exported asset is not yet ready for clean linked placement in the master.

| Criterion | Score | Review |
|---|---:|---|
| Correct identity and source-backed footprint | 2.0 / 2 | Purdue GIS OBJECTID 165 and the current emergency plan identify VPTH at 725 Harrison Street. An independent Blender reopen found the converted source ring and mesh base within 0.000031 m in both directions. |
| Position, orientation, and scale/dimensions | 2.0 / 2 | The campus-frame location, polygon orientation, and plan dimensions follow the GIS ring. Exterior trim extends roughly 0.3 m beyond the wall outline. The master marker and neighboring context were outside this isolated asset review. |
| Evidence-backed height, floors, and roof form | 1.2 / 2 | Purdue's 2026 emergency plan lists the basement, floors 1–3, and attic; the historic GIS description confirms basement and attic but calls the original building two stories. The asset shows three above-grade rows and an attic/service block, but its 15.925 m top and roof form are estimates. |
| Facade, entrances, and distinctive architecture | 1.0 / 2 | The preview is complete and coherent, with brick-like texture, stone-colored bands, window surrounds, glazing, and entry portals. No usable exterior photograph or elevation was included; facade colors, window rhythm, exact entrances, and detailing remain speculative. |
| Modular export, portability, and complete evidence | 1.5 / 2 | A fresh Blender 5.2.3 process reopened the expected scene, collection, stable ID, and mesh; there are no external images or linked libraries. The geometry vertices remain in campus-wide coordinates rather than a local building frame, so a master placement marker would double-translate the model unless the source is converted first. One material slot is unused. |

## Findings

- **Convert geometry to a local frame before master linking.** The mesh base already matches the campus GIS coordinates. Store it relative to a documented anchor and have the master marker apply that anchor, or keep the asset as a direct campus-coordinate massing object until converted. Do not add the GIS anchor to the current vertex coordinates unchanged.
- **Architectural uncertainty remains.** Height, roof/attic form, brick tone, story bands, window pattern, and the three entrance positions are estimates. The interior consists of generic floor plates; no sourced room layout or tunnel connections are modeled.
- **Minor cleanup:** material slot `VPTH darker brick articulation (estimated)` has zero polygons assigned.

## Reproduction

- `evaluator.py` returns the rubric result in `grade_result.json`.
- `fresh_open_probe.py` was run against Blender 5.2.3 in a separate process; see `fresh_open_probe.json` for object counts, material assignments, asset hash, coordinate checks, and dependency scan.
- The evaluated preview is `../preview_exterior.png`; primary source notes are in `../evidence.json`.
