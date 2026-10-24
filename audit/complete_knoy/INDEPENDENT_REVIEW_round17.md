# Knoy Hall R17 — independent full-building review

**Grade: 7.8/10 — below the project’s 8.0 acceptance target.** Review date: 2026-10-24. I reopened `modular/buildings/knoy_hall.blend` in Blender 5.2.3, inspected the R17 exterior and entrance renders beside the saved Purdue Archives photo, and checked the project’s GIS, floor-plan, LiDAR, placement, and prior review evidence. The saved asset reopened with the expected scene and asset collection, 65 direct asset objects, 169 scene meshes, the R17 spandrel mesh, assigned materials, and no unpacked external images. Details are in `independent_reopen_review_r17.json`.

## Scorecard

The rubric matches the previous full-building review. The normalized score is 8.6/11 × 10 = 7.8/10.

| Category | Score | Review |
|---|---:|---|
| Identity and footprint | 1.7/2 | Building identity and stepped form are consistent with the Purdue GIS footprint and orthophoto context. These are approximate geographic comparisons, not survey control. |
| Placement, orientation, and scale | 1.6/2 | The manifest placement and local asset origin remain consistent with prior checks. No new survey control or placement measurement was added in R17. |
| Height, floors, and roof | 1.2/2 | The 2018 Gateway plan supports L1–L4 floor spacing; 3DEP gives only an indicative roof-surface range. L5 status, roof datum, penthouse dimensions, and exact equipment placement remain unresolved. |
| Exterior and entrances | 1.4/2 | R17 narrows L1–L4 window bands from 2.0 m to 1.4 m and fills the resulting strips with brick, improving the brick-to-glazing proportion. However, the archival photo shows narrow, interrupted slit-like ribbons within large brick fields; the model still reads as continuous, regular horizontal glazing bands with pale horizontal trim on every level. The uncalibrated photo does not support the new 1.4 m value as a measured dimension or its assignment to all elevations. The entrance render has recognizable brick, dark glazing, canopy and lettering, but exact scale and facade-wide correspondence remain qualitative. |
| Interior and circulation | 1.7/2 | The L1 and L2–L4 plan traces, illustrative doors, fixtures, and stair runs are inspectable. The typical plan is a planning-study drawing with about ±1 m hand-registration uncertainty; fixture symbols are interpreted proxies. No verified continuous accessible route or complete as-built interior is established. |
| Technical and evidence quality | 1.0/1 | The asset opens, expected collection/root exist, materials are assigned, R17 geometry is present, and no file-backed image dependency is unpacked. R17 validation records changes to only the two glazing meshes and one added spandrel mesh while preserving preexisting transforms. |
| **Total** | **7.8/10** | **Below target** |

## Findings

1. **The R17 change is a plausible qualitative adjustment but not a verified elevation correction.** The Purdue Archives Historic Facilities photo at `https://collections.lib.purdue.edu/campus/buildings/75` shows brick-heavy elevations with thin horizontal window strips. It is perspective imagery with no date, scale, or face registration. It supports the general slit-window / masonry relationship, but not exact 1.4 m band height, story elevations, a uniform all-sided cadence, or the same detail on every face. R17 correctly records those limitations; the grade does not treat the estimate as measured.
2. **The model remains more regular than the reference.** The full-building render has continuous window bands repeated around the stepped shell; the viewed photo has visibly varied brick masses and interrupted glazing. This is the main remaining exterior-fidelity issue. Do not change other facades without a source that identifies those faces or elevations.
3. **Height and roof remain partly uncertain.** Purdue’s Gateway study supports only the documented L1–L4 interval. The 2018 LiDAR and interpolated bare-earth comparison is a useful broad vertical check, but cannot distinguish a roof slab from a fifth occupied level or measure penthouse/parapet height. The separate GIS 48-ft attribute conflict is unresolved.
4. **Interior completeness is not equivalent to as-built verification.** The plan trace and circulation details are useful, but door positions, fixture types, stairs, and floor-to-floor route continuity retain the previously documented planning or interpretation limits.

## Decision

R17 is technically sound and makes a restrained, documented facade refinement, but the full building remains below 8/10. The saved model and R17 evidence do not justify claiming all facade elevations, L5/roof height, or complete circulation are accurate. No geometry was edited by this review.
