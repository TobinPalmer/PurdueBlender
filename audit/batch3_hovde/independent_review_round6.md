# Hovde Hall — independent review, round 6

**Score: 7.3/10. Does not meet the 9/10 target.** I independently reopened `modular/buildings/hovde_hall.blend` in Blender 5.2.3 and inspected the round 6 exterior, entrance close-up, office cutaway, boardroom cutaway, and reopened export check. Round 6 materially improves the side windows: the east and west masonry meshes are built around four stacked rows of 13 openings, with the glazing and sash set back into the shell. The three east entry openings are also cut into the masonry. The principal remaining failure is that the portico still dominates and obscures the doors and central facade; interiors are furniture-only plan diagrams, and the asset has not been checked against the campus master or official footprint.

## Evidence checked

- `exterior_round6.png`, `portico_detail_round6.png`
- `presidential_office_round6.png`, `trustees_boardroom_round6.png`
- `final_asset_check.json`, `REVIEW_round6.md`, `round6_edit.py`, and `round6c_door_openings.py`
- Opened the saved building library independently. The check reports `Asset_hovde_hall`, 727 objects / 715 meshes, no unmaterialed meshes, and an unchanged `HOVD_Root` transform at `[-62.85, 93.0, 0]`, Z rotation `0.689754 rad`, unit scale. This verifies file/export integrity and the library root transform only; it does not verify the master placement.

## Findings and prioritized corrections

1. **Make the three doors readable from the approach.** The mesh script confirms three through-openings on the east wall, aligned to the modeled door and transom objects. In the close render, the six supports and broad limestone portico still mask most of the door leaves and their frames. The doors read as dark facade patches behind a dense stone overlay, so a viewer cannot reliably distinguish the entrance from windows. Adjust the portico depth/width and column positions against the reference photo, then show the stair-to-door relationship in a lower, clearer view. Keep dimensions estimated unless a measured elevation is found.
2. **Improve the portico-to-facade transition.** The six supports are now spaced apart, but they still read as thin, flat strips. The pediment and entablature form a heavy pale block, intersect visually with the horizontal facade courses, and cover nearby bays. Give the supports visible depth and a clearer separation from the brick wall, and reveal the facade around the entry. The cited photos support a classical center entrance, but do not support the current dimensions or exact support rhythm.
3. **Turn the interior diagrams into enclosed cutaways.** Both submitted interior images are explicitly rendered from a top-down selection that hides every room wall, ceiling, window, and most building objects. The office and boardroom show furniture, but no enclosure, door openings, circulation connections, or relation to the exterior. Add a 3/4 cutaway with wall thickness and openings, and label the plan interpretive because the sources found do not verify these room layouts.
4. **Clarify material and roof evidence.** Red brick and pale horizontal stone bands make the building identifiable, and the roof reads as a finished dark red-brown surface. The side glazing is visibly recessed in the close render. The roof remains a broad, shallow plane with a small raised cap whose shape and material are not verified by the cited ground-level sources. Shader/material slots are assigned, but the evidence packet does not establish source-matched color or roof construction.
5. **Verify placement and structural dimensions at integration.** The asset’s root transform is preserved, but the round 6 report explicitly says there was no GIS overlay. Compare the structural wall footprint, length/width, and orientation against the correct Purdue GIS feature, and check the placement marker and neighboring buildings in the linked master. Keep steps, plaza, portico, and other projections out of the wall footprint measurement.

## Category assessment

| Area | Assessment |
|---|---|
| Identity and massing | Recognizable four-story, long red-brick administration block; no current measured footprint/height comparison. |
| East/west openings | Through-openings are present in the masonry meshes; 52 glazing bays are set into those openings. Their exact cadence remains model-estimated. |
| East entrance | Three masonry voids align to modeled door/transom units, but door leaves are obscured in the submitted views. |
| Portico | Classical intent is recognizable; depth, support rhythm, facade connection, and door visibility remain weak. |
| Materials and roof | Brick/stone/glazing assignments render coherently; precise colors and roof form are not source-verified. |
| Interior | Furnished office and boardroom plan diagrams only; no enclosed interior cutaway or verified plan. |
| Export and placement | Saved file reopens; expected collection, material assignments, and root transform pass. Master/GIS placement remains unverified. |

**Decision:** revise before calling complete. Round 6 fixes the major side-wall opening problem and makes real entry voids, but it does not resolve the entry’s visual legibility, the room enclosure, or placement verification. It is below 9/10.
