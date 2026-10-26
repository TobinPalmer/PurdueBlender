# Independent grade: St. Thomas Aquinas Center R4

**Result: 8.2/10 — passes the 8.0/10 threshold.**
**Exact asset SHA-256:** `a06977c0783442a0eb7561d23e294bfc65d11546b3aa4a0c13d9c9b62f68a330`  
**Freshly reopened with:** Blender 5.2.3 LTS  
**Review scope:** saved R4 library, local GIS comparison, read-only master marker check, and exterior/interior inspection renders.

## Scorecard

| Criterion | Score | Independent evidence |
|---|---:|---|
| Correct identity and source-backed footprint | 1.9/2 | Strong match; public-map limitation retained |
| Position, orientation, and scale/dimensions | 1.9/2 | Verified within project transform; survey limitation retained |
| Evidence-backed height, floors, and roof form | 1.2/2 | Partly supported; vertical dimensions estimated |
| Facade, entrances, and distinctive architecture | 1.3/2 | Improved and legible; several details remain schematic |
| Modular export, portability, and complete evidence | 1.9/2 | Passes exact-file technical checks |
| **Total** | **8.2/10** | **Pass** |

## Measurements and checks

- A new Blender 5.2.3 process opened the exact R4 file. The named export has 1,275 objects, including 1,272 meshes; its root is identity-transform and records the correct local coordinate frame and campus origin. There are no empty meshes, materialless meshes, invalid material assignments, missing external images, or linked libraries.
- I independently polygonized the 43 horizontal base edges in `SOTAC_Stone_Foundation_and_Plinth` and compared that polygon with Purdue BuildingShapes FID 852 in the saved local projection. IoU is 0.999999957; symmetric-difference area is 0.00009285 m². This is an exact match to the map outline within rounding, not proof that the map outline is the surveyed wall line.
- A fresh read-only reopen of the campus master confirms `Placement_massing_st_thomas_aquinas_5535390` instances the correct R4 asset. Position error from the asset origin is 0.00000345 m; rotation is zero and scale is one.
- The wide and southeast exterior renders show the pitched sanctuary, cross tower, and flat-roofed connected wings meeting as one building. R4’s gable infill and flashing make the roof junction more coherent, although its transition remains a simplified estimate without a measured elevation.
- The sanctuary framing now reads as supported: 36 framing pieces form six trusses bearing on continuous wall plates. The classroom cutaway has boards, lecterns, cabinets, table groups, and stairs, but the room fit-out and partitions are schematic and repetitive.
- Four narrow vertical lines seen outside the sanctuary in the structure cutaway are named exterior downspouts at the original church corners, not stray supports. The cutaway hides their host facade, so they appear detached in that review image; a cleaner review view should hide them as well.
- The brick material is less contrasty in R4 but remains procedural and visibly stylized. The asset has 18 used procedural materials and no image texture nodes; this is portable, but the finish is not photographic.

## Remaining uncertainty

- No surveyed structural-wall outline, as-built floor plan, measured elevations, roof-pitch data, or truss drawings were found. The model’s 20.10 m upper bound includes the cross and is not a measured building height.
- Exact component joints, classroom partitions, roof-to-flat-wing flashing, and interior furnishings remain interpretive. The 2001 architect description and current parish project page verify the connected church, addition, and office/classroom program, but do not establish those measurements.
- The campus XY conversion is the project’s local approximation. The master marker agrees with that coordinate system, not with an independent survey control point.

## Sources

- [Purdue BuildingShapesZip4, FID 852](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/852) — named feature and map outline; not a wall survey.
- [OpenStreetMap way 117396617](https://www.openstreetmap.org/way/117396617) — corroborating named outline.
- [J.W. McQuiston Architecture project page](https://www.jwmcq.com/st-thomas-aquinas) — connected three-structure project, addition program, retained sanctuary, and exterior photographs.
- [St. Thomas Aquinas Project Renewal](https://www.boilercatholics.org/project-renewal) — current description of connected original church, new church addition, and office/classroom building.

## Saved evidence

- `independent_grade_r4.json` and `grade_r4_evaluator.py` — machine-readable result and runnable evaluator function.
- `independent_grade_r4_reopen.json` — fresh exact-file Blender inspection.
- `independent_grade_r4_master_marker.json` — fresh read-only master placement check.
- `footprint_match_r4.json` and `footprint_extract_r4.json` — independent mesh-outline comparison and extracted edges.
- R4 render set: north entry, southeast, top-down footprint, sanctuary cutaway, sanctuary structure, and classroom cutaway.
