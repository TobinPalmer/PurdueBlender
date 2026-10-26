# Hi Vine independent grade r1

**Result: 8.3/10 — PASS** (repository threshold: 8/10)

I directly reopened `modular/buildings/massing_hi_vine_dbdf0c5.blend` in Blender 5.2.0 and inspected the asset, source record, raw reference imagery, project rendering, aerial overlays, and saved model views.

| Criterion | Score | Finding |
|---|---:|---|
| Identity and footprint | 2.0/2 | Hi Vine identity is supported by named OSM feature and independent address sources. Roof-outline overlay is exceptionally close; structural wall line is not surveyed. |
| Position, orientation, dimensions | 1.8/2 | Campus XY and orientation align to street/aerial; footprint is about 42.90 × 81.32 m. The repository geographic conversion is approximate. |
| Height, floors, roof | 1.0/2 | Flat roof is supported by aerial/rendering. 19.7 m and six levels are estimates; story count conflicts across secondary sources and no measured elevation is present. |
| Facade and distinctive features | 1.7/2 | Brick/masonry rhythm, windows, retail glazing, corner glazing, and balconies are grounded in KJG design imagery but are schematic and not verified as built. |
| Modular export and evidence | 1.8/2 | Expected scene/collection and single portable mesh reopen cleanly, with no linked libraries or unpacked image dependencies. Evidence is varied and recorded. The shared manifest remains stale at 16 m. |

## Direct reopen facts

- Scene: `Building_massing_hi_vine_dbdf0c5`
- Collection: `Asset_massing_hi_vine_dbdf0c5`
- Object: `Hi Vine`, one mesh, 6,304 vertices / 1,566 faces
- Evaluated world bounds: X 482.128–525.192 m, Y -171.401–-89.911 m, Z 0–19.700 m
- Modifiers, external libraries, and unpacked external images: none

## Findings for coordinator

1. The asset passes at 8.3/10.
2. Keep height/story count explicitly estimated: no measured elevation supports 19.7 m or an exact floor count.
3. Coordinator-owned `modular/manifest.json` reports the old 16.0 m vertical bound. Refresh it to match the current 19.7 m asset when updating shared indexes.

Machine-readable rubric output and independent reopen facts are in `grade_result.json` and `direct_reopen.json`. The evaluator source is `evaluator.py`.
