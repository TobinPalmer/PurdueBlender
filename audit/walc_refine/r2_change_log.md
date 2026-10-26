# WALC refinement R2

**Saved asset:** `modular/buildings/walc.blend`  
**SHA-256:** `66e77776b04dd142c8a1292ff2f297c5a4b3a9b3f676ff62243bf81376714850`  
**Blender:** 5.2.3 LTS  
**Fresh-reopen evidence:** `independent_reopen.json` (asset opened standalone; expected collection and linked library resolved)

## Edits

- Added one joined facade mesh containing 147 narrow bronze fins on longer glazed wall segments. They follow the existing segmented perimeter and create a more vertical bay rhythm. The roughly 3.2 m spacing is a visual estimate, not an as-built dimension.
- Reworked `WALC_Reference_Brick` and `WALC_Reference_Limestone` with subdued procedural color and bump variation. Updated the glazing and bronze shader response. Existing facade bands, roof shape, footprint mesh and elevations were left in place because authoritative elevations and façade construction details were not found.
- Changed the foliage library reference to the project-relative path `//../site/foliage_library/engineering_foliage_library.blend`. A standalone fresh reopen resolved it without missing-library warnings.
- Re-rendered the existing interior inspection cameras using a brighter studio light. This improves inspection visibility only; it does not claim that schematic interior geometry matches exact as-built plans.
- Kept `AssetRoot_walc` at identity transform and the source/GIS outline unchanged. The GIS ring residual remains a trace-agreement check, not a survey.

## Verification

Fresh open reported 951 collection objects, 879 meshes, 24 used materials and no materialless meshes. The cached GIS structural outline residual remains 0.0000019 m. This metric compares to the cached source trace and cannot validate actual surveyed dimensions or height. Master placement and neighbor overlap remain unverified; coordinator should review `Placement_walc` and the campus view.

## Evidence and source limits

- Purdue Chemistry's WALC page, published 2017-04-12, includes a WALC architectural rendering and classroom photography and reports 27 classrooms: <https://www.chem.purdue.edu/media/news/2017/wilmeth.html>. The page is a dated visual/program reference, not a construction drawing or elevation survey.
- Purdue's WALC emergency plan revision 2026-04-03 describes the building's floors and program: <https://www.purdue.edu/operations/emergency-preparedness/walc/>. It does not document detailed room geometry or exterior heights.
- Purdue's BuildingShapesZip4 GIS layer is represented by the project snapshot `audit/official_building_references.json`, retrieved 2026-10-22. It is used only for plan-outline trace agreement, not façade, roof, height or interior verification.
- Room lists/floor-plan sources retained in the R1 audit document are program references. No verified construction/elevation sheets were found for this pass. Exact wall heights, roof assembly, interior room shapes, materials and detailed bay spacing remain estimated or schematic.

## Renders

- `southwest.png`, `southeast.png`, `north.png`, `roof.png`: refreshed exterior inspection renders.
- `03_reading_room_reference.png` through `09_basement.png`: refreshed interior inspection views using a brighter review light.
