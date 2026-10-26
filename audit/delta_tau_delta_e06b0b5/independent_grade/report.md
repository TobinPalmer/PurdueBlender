# Independent grade: Delta Tau Delta

**Score: 7.25/10 — below the 8/10 pass threshold.** The evaluator is reproducible with `python evaluate.py`; its output is `result.json`. The asset was reopened from disk in Blender 4.5.15 LTS and the saved plan and three-quarter renders were inspected directly.

| Criterion | Score |
|---|---:|
| Correct identity and source-backed footprint | 1.75 / 2 |
| Position, orientation, and scale/dimensions | 2 / 2 |
| Evidence-backed height, floors, and roof form | 1 / 2 |
| Facade, entrances, and distinctive architecture | 1 / 2 |
| Modular export, portability, and complete evidence | 1.5 / 2 |

The reopened structural shell's six base vertices match the six projected vertices in Indiana's 2018 Tippecanoe building-footprint feature 409940 with a symmetric nearest-vertex maximum difference of **0.000013 m**. The transformed XY placement and orientation agree with the footprint. That GIS record is anonymous, and the 400 Northwestern address point is just outside the polygon, so building identity is supported by proximity plus the zoning and chapter records rather than a named feature.

Height, number of floors, and exact roof geometry remain estimates. The reviewed zoning report supports a broad Tudor Revival description, but the model's 10.4 m eaves, 15.2 m ridge, 17.4 m chimney tops, three window bands, chimney count, and roof details have no measured vertical source. The same gap affects the facade score: the photo cited is a small cropped profile image, while archived construction photos and plans are known only from inventory descriptions and were not inspected. The entry side, window rhythm, stonework, and addition seam are therefore schematic.

Blender reopened the expected scene and collection with **73 objects**, no modifiers, and no external libraries. The three-quarter preview is inspectable. The plan image clips the building's north/south extent and shows the roof rather than a useful footprint. The shared manifest still records one object and the former massing bounds; the coordinator should update it before integration.

For a fresh grade, inspect the specific archival exterior/construction images or plan records and use them to correct or simplify the roof, elevations, entrance and window placement. Fix the plan camera framing and refresh manifest object count/bounds. If no usable archival views can be obtained, retain these features as explicitly schematic and provide the coordinator with the unresolved evidence limits.
