# Alpha Xi Delta independent grade

**Score: 8.0/10 — pass**

I reopened `modular/buildings/massing_house_301841248_fe939c7.blend` in Blender and inspected the evaluated mesh, the FID 788 GIS snapshot, the 2008 geolocated photograph and metadata, and the rendered preview.

| Criterion | Score | Review |
|---|---:|---|
| Identity and source-backed footprint | 2.0/2 | Official Purdue feature FID 788 names Alpha Xi Delta at 519 University St. The 24 source ring points match the rebuilt base within 0.000016 m maximum residual. |
| Position, orientation, dimensions | 1.5/2 | The campus-coordinate mesh preserves the GIS footprint and identity transform. The oblique photo supports a southeast viewing approach, but does not establish the full facade bearing. Roof/entry projections extend slightly outside the GIS wall line. |
| Height, floors, roof | 1.0/2 | The photo partially supports multiple facade levels. It crops out the roof and gives no dimensions; the 8.2 m eaves, 12.3 m ridge, and hipped roof remain estimates. GIS `NUM_LEVELS=1` conflicts with the two-level interpretation and is undocumented. |
| Facade and distinctive features | 1.5/2 | The dark brick, stone arched entrance, horizontal band, and mullioned windows correspond to visible source details. Full facade proportions, opening rhythm, and exact entry bearing remain uncertain. |
| Modular export, portability, evidence | 2.0/2 | Reopened asset contains the expected one mesh in the expected collection, has identity transform, no external file images, and includes raw source, image metadata, preview, and validation evidence. |

See `evaluate.py`, `result.json`, and `blender_probe.json` for the evaluator and machine-readable findings.
