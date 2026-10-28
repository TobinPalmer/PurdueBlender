# Alpha Xi Delta — revision 2 response

**FID 788 | Asset:** `modular/buildings/massing_house_301841248_fe939c7.blend`  
**Revision SHA-256:** `2F863554345DD260E2708F50225CFFD595B8C55A18E8C49E38B620698B4E30B7`  
**Prior independent regrade:** [8.07/10 PASS](independent_regrade_r1_2026-10-28.md), which applied to SHA `95AAF80107165DFCF9EF43FBA15835B995F78949FCA71AF4A956715229AC989A`. The earlier 7.6 report and R1 report remain unchanged.

## Responses to the R1 findings

- **Unsupported roof gap:** added a continuous dark roof field under the gabled roof wings and removed upstairs beds/headboards that had projected above the roof. The exterior preview now shows a continuous roof transition without the previous open, courtyard-like gap. Roof shape and height remain estimated because no measured elevation was found.
- **Manifest object-count discrepancy:** joined all exterior, entry, window, roof and schematic interior geometry into the stable `House_301841248` mesh. The named collection and scene each contain exactly one object, matching the current shared manifest's `object_count: 1`; no shared manifest file was edited. The one root mesh contains 18,299 vertices and 17,061 faces.
- **Interior qualification:** the ground-floor cutaway preview now carries the caption “SCHEMATIC INTERIOR - NOT AN AS-BUILT PLAN.” The root object also stores this limitation in its `interior_representation` custom property.
- **Technical cleanup:** temporary preview camera, caption and lights are removed before save. Fresh-open validation confirms one scene object/collection object, no camera/light, and no external image dependencies.

## Evidence

- Exterior: [exterior preview](exterior_preview.png)
- Ground-floor schematic: [captioned cutaway](interior_cutaway_preview.png)
- GIS outline: [footprint comparison](footprint_overlay.svg) and [metrics](footprint_comparison.json)
- Fresh-open: [Blender validation](fresh_open_validation.json)
- Source provenance and remaining estimates: [model evidence](model_evidence.json)

The saved lower shell retains the 24 GIS FID 788 outline vertices within 0.00001569 m under the project's local approximate coordinate transform. This match is by construction and is not independent survey validation. Roof, height, window spacing, unseen elevations and interior positions remain estimates or schematic.

**Review status:** request a new read-only grade for exact SHA `2F863554345DD260E2708F50225CFFD595B8C55A18E8C49E38B620698B4E30B7`.
