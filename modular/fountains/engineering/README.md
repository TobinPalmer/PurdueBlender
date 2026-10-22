# Engineering Fountain reconstruction

Open `engineering.blend`. Export collection: `Fountain_Engineering`; instance offset zero, geometry in original campus meters. Link with identity transform. `replaced_objects.json` lists exact original fountain-specific objects replaced; preserve the mall/promenades/skybridge. The original snapshot is separately retained in `original_fountain_backup.blend`.

## Evidence and placement

Primary Purdue source: https://www.purduealumnus.org/class-of-1939-water-sculpture/campus/ (retrieved 2026-10-22; saved HTML/photo). Supports 38ft structural height, historical 588 gallons/min upward jet, safety cylinder added2001, four broad curved fins and segmented low outer wall. Structural fin span is11.5824m above nominal .12m deck datum, top11.7024m; surveyed ground elevation unknown.

Position: named OSM fountain polygon way283274213, retrieved2026-10-22 via https://www.openstreetmap.org/api/0.6/way/283274213/full; revision4 dated2022-09-25, geometry2014. WGS84 converted by modular/AGENTS.md localapproximation. Polygon area267.648m², extent18.599x18.466m; centroid(-7.80423645,137.92938591). Original center(0,195) was57.602m away. New asset aligned to named polygon centroid, **not a surveyed certification**. The initial map-embed viewport center was rejected during independent review. Polygon perimeter is a plaza guide, not an independently measured sculpture plan.

No dimensioned shop drawings/floorplans were found. This sculpture has no interior building floorplan. The old Purdue UVAC sculpture page redirects to an archived-site notice. A secondary photographer page was found at https://commons.wikimedia.org/wiki/File:Purdue_Egrfountain_jc.jpg but downloading its original was rate-limited; no measurements attributed to inaccessible imagery. Fin profile/thickness/rotation, wall details, cylinder dimensions, grille, relief network, paving module and absolute elevation remain photo-derived estimates. The commissioned relief is approximated, not an exact reproduction.

## Actual simulation and limitations

Real Blender Mantaflow FLIP liquid data and mesh caches for frames1..96 at24fps, gravity9.81m/s², scale1m/unit. Longest-axis resolution192 in9x9x14m domain, meshrefinement2; relative `//cache/attempt1` directory. Data baked787s, mesh189s. Four seconds of startup, not an established steady-state or seamless loop.

Inflow13.5m/s upward fromz3.19m gives ideal ballistic apex12.48m; actual rendered late-frame mesh apex12.38–12.41m. Velocity is inferred, not a pump measurement. Historical588USgpm impliesQ=.0371m³/s and radius.0296m at13.5m/s. That bore is below this grid's .0729m cellsize. The actual simulation uses explicitly enlarged .08m radius emitter for numerical survival; **flow/discharge is not calibrated**. Ideal geometrical discharge of the enlarged emitter would be about.271m³/s (~7.3times historicalQ), although numerical FLIP flux differs. No claim of accurate hydraulics or9/10 acceptance follows from a completed bake.

Fins are liquid collision effectors. Open bottom approximates collection/drainage; the deck/grille does not model subsurface drain hydraulics, splash-waterfilm, mist, or whitewater. Surface uses clear-water transmission1/IOR1.333; no procedural mesh masquerades as simulated water. Final wall recesses/relief/paving are visual detail, not hydraulic effectors. The collision fins and inflow/domain geometry remain unchanged since the real bake. A rigid placement shift of the complete scene was tested: frame72 surface preserved43994 vertices and its centroid moved exactly with the coordinate correction.

## Verification and grading

`verification.json` records independent reopen evaluation and wet renders at24/48/72/96:5552/9892/43994/54714 surfacevertices; frame96 z.064..12.385m. `particle_verification.json` independently parses Mantaflow PB02 particles; frame96 has13653 particles. `linked_probe.json` verifies cache evaluation from a separate linked context and zero collection offset.

Five implementation/grading attempts maximum. Read `grading_attempt1.md` through `grading_attempt5.md` for the independent child's actual scores and limitations. Do not equate visual quality with measured fidelity. Stop after attempt5 even below9/10. Parent coordinator must still verify final actual master links/neighbors and visibility.

Final preview: `final_front.png`. Standalone file is saved atframe96 for a developed falling jet. Cached frames1..96 are the supported timeline. Copy the entire engineering folder, including cache, to preserve portability; the `.blend` alone is insufficient.
