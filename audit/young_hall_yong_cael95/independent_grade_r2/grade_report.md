# Independent Ernest C. Young Hall review — revision 2

**Result: 8.45/10 — pass** (minimum 8/10). This review opened the saved Blender asset in a fresh Blender 5.2.3 process and compared it against the saved official GIS and Purdue archival evidence.

| Criterion | Score | Evidence summary |
| --- | ---: | --- |
| Identity and footprint | 2.00/2 | Purdue GIS FID 70 names YONG; 34 shell vertices match the official ring within 0.000032 m.
| Position, orientation, plan | 2.00/2 | The GIS polygon is used directly in the project coordinate conversion; plan bounds and vertex order agree.
| Height, floors, roof | 1.35/2 | Purdue Archives describes 10 stories; GIS reports 11 levels. R=102 is interpreted as feet without unit metadata; roof/floor heights remain estimates.
| Facade and features | 1.55/2 | Three historic Purdue photos support the long slab, pale panels, narrow repeated windows and flat roof. The current photo supports the localized brick sign wall. Entrance/full current elevations remain partly inferred.
| Export and evidence | 1.55/2 | Fresh open contains the expected collection with 21 meshes and one font; no preview EMPTY or external image dependencies. The interior is only a small schematic lobby/corridor slice, not a floor-plan reconstruction.

## Remaining uncertainties

- Official GIS level count is 11 while Purdue Archives describes 10 stories; the extra level may be a basement but the source does not say.
- GIS vertical value R=102 has no units; the model treats it as feet, so height is estimated.
- Archival facade photos are undated and show historic elevations, while the current Purdue photo is only a close crop. Exact current window spacing, entry placement, rooftop equipment, and concealed elevations are not verified.
- Interior layout remains schematic because no public floor plan was found.
- Horizontal registration uses the project’s approximate geographic conversion and lacks survey control.

The machine-readable evaluator and evidence are in `evaluate_yong_r2.py` and `result.json`.
