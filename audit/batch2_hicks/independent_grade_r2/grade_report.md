# Hicks Library independent R2 grade

**Result: 8.50/10 — PASS**
**Inspected SHA-256:** `3fc4a157b3ee6ce863edcb74155c1463706f75e7b7fb9170e2849b25cde48cf0`

| Criterion | Score | Evidence summary |
| --- | ---: | --- |
| Correct identity and source-backed footprint | 2.00/2 | Purdue Campus GIS BuildingShapesZip4 identifies FID 197 as John W. Hicks Undergraduate Library at 504 Mitch Daniels Blvd. |
| Position, orientation, and scale/dimensions | 1.90/2 | The source polygon was independently transformed to the manifest local frame at placement origin [88.25, -317.24000549316406]; orientation and structural XY bounds match, with max vertex error 0.000029 m. |
| Evidence-backed height, floors, and roof form | 1.30/2 | Purdue GIS lists three levels and elevation attributes for ground floor, basement and roof/skylight; the model contains subterranean levels, roof deck, atrium and three pyramidal skylights. |
| Facade, entrances, and distinctive architecture | 1.50/2 | The exterior photo shows the same low brick cube with broad sloped masonry walls; the asset models four GIS-perimeter lofted sloped faces. |
| Modular export, portability, and complete evidence | 1.80/2 | A separate Blender 5.2.3 LTS process freshly reopened the exact requested asset SHA; expected scene and exported collection exist, with 343 objects, assigned procedural materials, and no external image dependencies. |

## Findings
- The official GIS footprint and upper sloped-wall perimeter are an exceptionally close match.
- The visual form and documented furniture categories are represented, but wall slope, height, roof verticals and interior positions remain estimates.
- Master integration should update the manifest object count; this does not change the exact asset grade.

## Limitations
- No current public floor plan or dimensioned wall section was available.
- The 2013 furnishing image documents the historical renovation, not current as-built furniture placement.
