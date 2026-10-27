# Phi Mu independent grade (final five-dormer revision)

**Score: 8.75/10 — Pass**

I inspected the current Blender library after reopening it and compared the current preview directly with the preserved 1965 *Debris* page. The house photograph shows five dormers along the front roof. The revised preview also shows five. The photograph also supports the red-brick facade, two main levels, centered columned portico, and steep roof.

| Criterion | Score | Findings |
|---|---:|---|
| Identity and source-backed footprint | 2.0/2 | Purdue GIS FID 772 identifies Phi Mu at 201 Waldron St; all 18 distinct ring vertices match the base mesh within 0.1 mm rounding. |
| Position, orientation, and dimensions | 1.5/2 | Exact footprint and identity object transform retained. Portico/entry bearing is illustrative; no georeferenced facade elevation. |
| Height, floors, and roof form | 1.75/2 | Two main stories, steep roof and five dormers match the archival view. Ridge/eaves are estimates, and undocumented GIS `NUM_LEVELS=1` conflicts with the photo. |
| Facade and distinctive architecture | 1.5/2 | Brick and central classical portico are represented. Window trims are schematic and do not fully model the visible louvered shutters. |
| Modular export, portability, and evidence | 2.0/2 | Expected one-object collection reopens with identity transform and no external image paths; raw GIS and archival photo, preview and validation are present. |

The GIS service does not publish survey accuracy. The archival photo is not georeferenced, so facade bearing and exact elevations remain unverified. Model height is not a measured result.

Evaluator: `evaluate.py`; machine-readable result: `result.json`.
