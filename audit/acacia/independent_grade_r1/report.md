# Acacia independent grade (round 1)

**Result: 5.25/10 — does not meet the 8/10 pass threshold.** This review was performed against the saved asset opened directly in a fresh Blender 5.2.3 process. No asset or shared project files were changed.

## Rubric

| Criterion | Score | Basis |
|---|---:|---|
| Correct identity and source-backed footprint | 1.00/2 | GIS FID 791 and 608 Waldron identity are supported by saved Purdue/Acacia sources. The shell retains a plausible campus footprint, but its evidence record documents a GIS Shape__Area conflict and the structural outline is not reconciled with the source ring by an overlay. |
| Position, orientation, and scale/dimensions | 0.50/2 | Direct-linked coordinate convention is present, but facade bearing and porch location are explicitly estimated. No geotagged image/orthophoto overlay establishes orientation or residual position error. |
| Evidence-backed height, floors, and roof form | 1.50/2 | Official source drawings support three above-grade levels and the elevation schedule. The dark pitched roof/dormer form is visible in the source. Overall height and roof details are estimated rather than measured. |
| Facade, entrances, and distinctive architecture | 0.50/2 | Tower lettering, entry arch, porch, roof, dormers, and windows appear. The rendered front differs materially from the official photo: upper story half-timber/cream panels are modeled as brick, the gable is mostly blank, and porch/window proportions are simplified. Interior render is low-contrast and does not clearly show room detail. |
| Modular export, portability, and complete evidence | 1.75/2 | Fresh-open expected scene, collection, ID, and campus-coordinate shell verified. 489 collection objects, 483 meshes, 12 in-file materials; no missing mesh material slots, external image dependencies, or linked libraries. Source snapshots and renders are present. |

## Fresh-open facts

- Scene: `Building_massing_house_301841251_8a9a05b`
- Collection: `Asset_massing_house_301841251_8a9a05b`
- Primary mesh: `House_301841251`
- Evaluated primary bounds: X -334.714 to -315.275 m, Y 342.136 to 370.629 m, Z 0 to 9.450 m
- Primary object location and collection offset: zero
- Asset opened from `modular/buildings/massing_house_301841251_8a9a05b.blend` in Blender 5.2.3

## Required fixes before a passing regrade

1. Compare the structural shell polygon to the saved FID 791 GIS ring in a top-down overlay; explain/resolve the area and dimensions discrepancy and record the final transform and residual.
2. Verify facade bearing and position from a current aerial or geotagged reference.
3. Rebuild the photographed front elevation: cream infill panels and dark timber framing above the brick base, fuller gable framing, and source-matched entrance/porch and window rhythm.
4. Provide a legible interior render from room level or a clean cutaway; current overhead output is too pale and visually obscured to verify the rooms and finishes.

## Evidence reviewed

`audit/acacia/evidence.json`; saved Purdue GIS FID 791 state-plane and WGS84 snapshots; `audit/acacia/sources/acacia_front_porch.jpg`; `audit/acacia/sources/acacia_plan_gallery_1.jpeg`; `audit/acacia/exterior.png`; `audit/acacia/interior.png`; and fresh-open Blender inspection.
