# Elliott Hall of Music — round 11 handoff

**Status: ready for independent review. No score assigned.**

## What changed

The auditorium seat fabric now uses a restrained gray palette, following Purdue Convocations' written description of gray cushioned seats in its current venue photo. The model keeps procedural fabric variation. Fresh stage-facing interior and oblique exterior views are saved as `interior_from_stage_round11.png` and `exterior_round11.png`.

## Saved-file check

Blender 5.2.3 LTS reopened `modular/buildings/elliott_hall_of_music.blend`. The Elliott collection has 135 mesh objects. No round11 temporary objects remain. North and south door objects remain present, and all three portal trim objects have zero modifiers. The exact checks are in `reopen_check_round11.py`.

## Limitations

This is a finish and evidence pass, not a complete architectural correction. I did not invent a window cadence, side-exit placement, flytower dimensions, or interior circulation measurements from non-dimensional sources. The large blank facade areas remain a fidelity gap. The official seat chart establishes three seating levels and curved blocks, not row pitch or aisle/egress dimensions. Stage, backstage, stairs and circulation remain schematic. Hovde interface and route continuity remain deferred to the Hovde owner. Do not interpret GIS polygon contact as a doorway or continuous route.

Prior footprint evidence is retained unchanged: Purdue BuildingShapes FID 617 comparison in `footprint_comparison_round9.json` reports 0.1668 m RMS / 0.2594 m max residual under an approximate conversion; this is only horizontal footprint evidence.

Source detail and caveats are recorded in `source_notes_round11.md`. Please assign a new independent score and list further source-backed changes.
