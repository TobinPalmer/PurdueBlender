# Independent Chi Omega massing grade

**Candidate:** `modular/buildings/massing_chi_omega_a9eb08d.blend`
**Reviewer:** independent grader subagent
**Blender:** 4.5.15 LTS
**Result:** **7.25/10 — does not pass the required 8/10**

The model reopens as a clean, self-contained massing library. Its ground perimeter matches Purdue GIS feature 781 (`Chi Omega`, 402 Waldron St) after the repository's documented WGS84-to-campus coordinate approximation. A fresh Blender comparison found 0.0001 m maximum rounded nearest-vertex error and 0.000013 m error when comparing the full perimeter in reverse winding order. The exact ring match also supports its orientation and plan dimensions, subject to the GIS source and conversion accuracy.

The Indiana orthophoto supports a multi-wing roof silhouette, and the model's four simplified roof zones capture that general reading. No source in the evidence folder verifies story count, eave height, roof peak, pitch, or exact roof boundaries. GIS has `NUM_LEVELS=1` and `Extrution=12`, but the snapshot gives no measurement definition or unit. The builder correctly labels the 7.8 m eave and 10.3 m peak as estimates.

The facade is largely unverified. The preview shows generic windows, trim, and masonry that the build script describes as illustrative. No entrance is modeled. The Purdue property memorandum and chapter address support identity/site only; the historical photo inventory points to possible archival views, but no facade photograph or elevation was retrieved and used here. Appearance alone earns no verification credit.

| Criterion | Score | Finding |
|---|---:|---|
| Identity and source-backed footprint | 2.00/2 | GIS FID 781 identity/address and transformed perimeter match |
| Position, orientation, dimensions | 2.00/2 | Campus-coordinate placement and exact polygon match |
| Height, floors, roof | 1.00/2 | General roof zones aerial-informed; vertical geometry unverified |
| Facade, entrance, distinctive architecture | 0.25/2 | Generic placeholders; no verified entrance or facade evidence |
| Modular export, portability, evidence | 2.00/2 | Reopens cleanly; no linked dependencies; source records included |
| **Total** | **7.25/10** | **Below pass threshold** |

The machine-readable rubric and evaluator output are in `result.json`; `evaluator.py` implements the returned `{score, max_score, criteria, evidence, findings}` contract. The independent reopen probe and Blender output are in `reopen_probe.json` and `blender_reopen.log`. I inspected the builder preview alongside the raw close orthophoto and the source record. The underlying snapshots and original builder validation remain in `audit/chi_omega/`.

**Required follow-up:** revise the candidate using verified facade/entrance and vertical evidence if obtainable, or keep those elements explicitly uncertain and obtain another independent grade after substantive revision. This grade does not change the candidate asset.
