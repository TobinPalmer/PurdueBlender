# Veterinary Pathology Building — Independent Grade R2

**Score: 8.2/10 — PASS** (threshold: 8.0)

| Category | Score | Finding |
|---|---:|---|
| Identity and source-backed footprint | 2.0/2.0 | GIS OBJECTID 165 identifies VPTH at 725 Harrison Street; fresh-open geometry preserves the GIS footprint to approximately 1.4 micrometers under the saved coordinate conversion. |
| Position, orientation, and scale | 2.0/2.0 | Geometry is local around the documented campus anchor `(-162.821272, -816.256807)` m and object transform is `(0,0,0)`. The isolated asset is ready for marker-based placement. |
| Height, floors, and roof form | 1.2/2.0 | Broad floor/attic organization matches Purdue's current emergency plan, but roof profile and exact heights remain estimated. |
| Facade and entrances | 1.0/2.0 | The model reads coherently as a multi-wing institutional building; facade rhythm, materials, portal details, and colors lack photo or elevation verification. |
| Modular export, portability, and evidence | 2.0/2.0 | Fresh Blender 5.2.3 open succeeded; expected scene/collection/asset ID and single building mesh are present. All seven material slots are used, with no external image or library dependencies. |

## Overall finding

Revision 2 fixes the prior modular placement blocker: the saved building mesh is in local coordinates, and adding its documented campus anchor reconstructs the GIS location. The footprint is preserved with negligible conversion error. The asset passes the five-category rubric at 8.2/10, with significant architectural uncertainty still concentrated in the roof and facade. Generic floor plates are present, but room partitions and tunnel connections are not modeled or verified. This grade covers the isolated asset, not its master-file marker or campus context.

## Evidence files

- `grade_result.json` — criterion scores and findings.
- `fresh_open_probe.json` — independent fresh-process Blender validation and geometry checks.
- `fresh_open_probe.py` — probe used for validation.
- `evaluator.py` — scoring implementation.
