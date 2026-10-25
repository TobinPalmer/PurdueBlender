# Independent Grade — Potter Engineering Center R3

**Score: 8.0/10 — pass at the project's 8/10 threshold**  
Asset reviewed: `modular/buildings/potter_engineering.blend`  
SHA-256: `DB9C22C8CD12012120E3A020DD0D901DB4248FEED1156F0235DDF4A2CE92DC3F`  
Review method: read-only Blender 5.2.3 reopen, independent geometry/dependency probe, direct comparison with the GIS record and available plans/photos, and visual inspection of the saved evidence. No model or shared files were changed.

## Criterion scores

| Criterion | Score | Evidence and limits |
| --- | ---: | --- |
| Correct identity and source-backed footprint | 2.0/2 | The official Purdue-linked campus GIS snapshot identifies A. A. Potter Engineering Center (POTR, feature 864). The shell's XY bounds match the GIS envelope within 2 mm after applying the manifest's placement offset. Approximate registrations of the 2016 floor plans report IoU 0.757 for the basement and 0.854–0.855 for upper plans. The GIS polygon is a campus-map reference, not a certified survey. |
| Position, orientation, and scale/dimensions | 1.8/2 | A fresh reopen confirms the local asset root at `(0,0,0)`. The manifest placement offset is `[77.400, -10.000] m`; applying it aligns the model shell to the GIS envelope. The GIS minimum rotated rectangle is 89.889° east-CCW, consistent with the modeled north-south long axis. The master collection-instance marker was not opened in this independent review and still needs coordinator confirmation. |
| Evidence-backed height, floors, and roof form | 1.3/2 | Purdue's 2016 renovation study provides floor plans, a typical window schedule, and a penthouse plan; a Purdue photo supports a broad, low roof profile. The reopened shell reaches 13.411 m and the roof 13.661 m locally. The GIS record marks height unverified; modeled elevations and penthouse height remain estimates, with no current surveyed elevation/as-built roof plan. |
| Facade, entrances, and distinctive architecture | 1.1/2 | The Purdue photo supports red brick, pale precast surrounds, repeated punched windows, and a projecting rounded brick stair tower. The model/render shows the corresponding material bands, window rhythm, and rounded tower. The recognizable exterior stair and canopy are absent from a verified facade location because the source photo bearing is unknown; the main entry presentation is incomplete. |
| Modular export, portability, and complete evidence | 1.8/2 | Blender reopened the asset with its expected `Asset_potter_engineering` collection: 500 objects, 488 meshes, root unchanged, no materialless meshes, and no missing external images. The independent roof ray checks pass at the estimated opening center and hit roof on both control sides. Source URLs, GIS feature ID, snapshot date, coordinate transform, plan method/uncertainty, photo, and validation evidence are recorded. The exterior render has not been regenerated for this exact saved revision. |

## Findings

- The widened S03 roof opening clears the sampled center ray while roof geometry remains on either side. A modeled 0.8 m route proxy fits the estimated S03 landing turn and estimated 1.2 m doorway. These are local geometric checks, not a continuous all-flight collision audit or code/accessibility certification.
- The strongest evidence is the GIS footprint match and the intact modular export. The remaining fidelity gaps are the unverified main entrance stair/canopy, estimated heights/roof details, and incomplete/currently unverified interior partitions.
- Prior Round 8 warnings about other stair/wall intersections remain unresolved or rely on historical wall-plan traces; this review does not treat those checks as cleared.

## Evidence files

- `independent_grade_probe.py` and `independent_grade_probe.json` — independently reopened Blender asset probe.
- `evaluate_potter_r3.py` and `independent_grade_r3.json` — runnable scoring function and machine-readable result.
- `SOURCE_REVIEW.md` — sources, identifiers, dates, coordinate conversion, plan-fit uncertainty, and feature limits.
- Visuals inspected: `audit/complete_potter/after.png`, `audit/batch4_potter/exterior_facade_round7_low.png`, `audit/batch4_potter/facade_detail_current.png`, `audit/batch4_potter/stairwell_circulation_round7.png`, `audit/complete_potter/interior_historic2016.png`, and current S03 schematic `s03_upper_route_schematic.png`.
