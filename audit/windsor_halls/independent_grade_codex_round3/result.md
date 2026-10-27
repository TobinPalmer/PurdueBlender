# Windsor Halls independent grade — revision 3

**Target:** `modular/buildings/massing_windsor_halls_80aeb51.blend`  
**SHA-256:** `9985a554162b7bb9ee7d4ef8bbba888338b9e5cfeb7731c0b891aa7ee8f8b4aa`  
**Result:** **7.8/10 — does not meet the 8.0 threshold**

## Independent fresh-open check

I reopened the exact file in Blender 5.2.3 LTS. Its hash matched the requested revision. The expected scene and asset collection loaded with 196 objects (195 meshes), 29,269 mesh vertices, 16,831 faces, and 13 materials. There are no linked libraries or external image paths. Detailed probe: [fresh_open_probe.json](fresh_open_probe.json).

## Score

| Criterion | Weight | Score | Finding |
| --- | ---: | ---: | --- |
| GIS identity, shell footprint, and placement evidence | 20% | 9.9 | FIDs 63–66 are correctly identified. Fresh-open shell comparisons report IoU 0.9999984–0.9999990 and roughly 0.00003 m boundary error under the documented approximate transform. This verifies XY footprints, not heights or roofs. |
| Separate shells and master placement readiness | 10% | 9.5 | Warren, Wood, Vawter, and Dining Court remain separate. FID 66 is a separate low volume with no invented horizontal overlap. Its vertical relationship is still estimated. |
| Warren, Wood, and Vawter roof silhouettes | 20% | 6.2 | Broad roof surfaces still read as nearly flat caps. Warren and Vawter use similar small gable accents; Wood’s central gable is crowded by the roof plate behind it. Exact roof profiles are not verified by the available sources. |
| Hall-specific facade distinction | 15% | 7.1 | Wood’s central entry bay helps identify it. Warren and Vawter remain very similar in their repeated window rhythm, floor bands, and roof accents. |
| Entrance details | 10% | 6.5 | All three entries are locatable, but Warren and Vawter are minimal canopies and dark openings. Wood’s entry is more distinctive, though its pale pediment dominates and the doorway transition is sparse. |
| Materials and textures | 10% | 7.8 | Brick, trim, glazing, and slate read clearly and consistently. Brick repetition and uniform blue roof finish make the result feel procedural. |
| Schematic interior legibility | 10% | 6.8 | The residential room/lounge view is readable. The supplied Dining Court interior preview appears near-black and does not let me verify its floor, counter, or tables visually, though those objects exist in the reopened file. |
| Portability | 2.5% | 10 | Blender reopened the asset without linked libraries or external images. |
| Evidence and uncertainty disclosure | 2.5% | 9.3 | Evidence separates measured XY shells from estimated height, roof, facade, entrance, and interior details; it also documents the approximate coordinate conversion and unit uncertainty. |

## Priorities for the next iteration

1. Reshape Warren and Vawter’s broad roof caps into deliberate, distinct silhouettes. Keep roof elevations explicitly estimated without measured evidence.
2. Refine Wood’s central gable and roof junction so the entry bay reads as an intentional feature rather than an overlay against the cap.
3. Add source-supported distinction between Warren and Vawter facades, or keep conservative forms and state the remaining uncertainty.
4. Improve entrance proportions and ground transitions for all three halls while preserving the documented alignment as an estimate.
5. Regenerate the Dining Court interior preview from a camera that shows its schematic floor, counter, and tables. Keep the plan labeled schematic because a verified floor plan was not found.

This review covers revision 3 at the SHA above only. The building asset and campus master were not edited.
