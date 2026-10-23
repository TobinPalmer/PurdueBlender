# Rawls Hall — batch 4 saved pass

## Asset and scope

Standalone library: `modular/buildings/rawls_hall.blend`, export collection `Asset_rawls_hall`. This pass does not alter the master blend, manifest, placement marker, or other assets. The detailed geometry remains in local coordinates. Existing GIS alignment uses an approximate plan registration; horizontal uncertainty is approximately 1–2 m, and is not survey accuracy.

## Sources checked

- Purdue Road School, 2024 Rawls Hall first-floor plan: https://roadschool.purdue.edu/maps/2024%20Rawls%20Hall.pdf (retrieved 2026-10-23). Used for visible first-floor room/core boundaries, door gaps, and furniture layout; plan scale is the basis for a similarity registration against the GIS footprint.
- Purdue eArchives, Jerry S. Rawls Hall interior image PPBUC03065: https://earchives.lib.purdue.edu/digital/collection/pbuildings/id/3050/ (photo date 2003-07-25; building completed 2002). Historical palette/context only; it does not verify current room finishes or later renovations. Preserved local image and metadata as `interior_reference.jpg` and `photo_metadata.json`.
- Google Maps Rawls Hall listing: 40.4237823, -86.9099567. Satellite tile displayed Airbus/Maxar ©2026 but no capture date was exposed. Street View at 357 W State St displayed May 2026 capture; the observed pano point is nearby (40.4239474, -86.9101073), and its viewing direction is not a head-on facade survey. It is a visual cross-check, not dimensioned evidence. No source screenshot was saved in this folder, so rely on this written observation as an access record, not a reproducible image artifact.

## Changes in this pass

- Rebuilt source-visible first-floor partitions from the 2024 plan, preserving passage openings and adding jamb/lintel cues. Corrected misplaced north-room/vestibule/stair groups to the plan coordinates and checked their relationship to the exterior shell.
- Repaired the *active* red-brick shader: blended X/Z and Y/Z projections by absolute surface-normal X so brick courses continue across perpendicular faces. Metric scale is 0.215 m brick width and 0.075 m course height. Removed a disconnected mapping graph from being mistaken for the active projection.
- Replaced desk support panels with four narrow legs per desk; retained chair backs and legs; subdued the wood grain so it reads closer to furniture scale.
- Preserved the existing apron correction; the refreshed exterior render shows no black apron triangles.
- Did not invent upper-floor partitions or a precise atrium shape. Those remain unverified without matching upper-floor plans or current interior evidence.

## Saved-file verification

The asset was saved and reopened for the renders. `checks.json` records 721 objects (713 meshes), expected collection/root state, no missing image dependencies, and the brick node links. `round1_validation.json` records 42 desks, 42 chairs, all 84 furniture centroids inside the GIS ground shell, identity `AssetRoot_rawls_hall`, and the 1–2 m plan registration uncertainty.

Renders: `exterior_round1.png`, `interior_1086_round1.png`, and `first_floor_cutaway_round1.png`. The room render communicates the furniture and supports at eye level. The upper-floor interior, exact current material palette, full facade detail, and survey-grade placement remain unresolved. These renders and checks support a saved improvement pass; they do not establish a 9/10 independent quality score.

## Round 2 review and additions (2026-10-23)

### Perimeter check

Reviewed all 11 wall objects flagged by the round 1 GIS-shell centroid check. Their outlying bounds follow source-plan perimeter/core edges. Ten have a maximum bounding-box corner overhang of 1.89 m or less; the remaining Plan1086 wall reaches 2.10 m at a corner, with its centroid 1.27 m outside. The registered plan and GIS shell visibly diverge at those edges, within the stated approximate 1–2 m registration uncertainty. No isolated misplacement is confirmed, so the walls were left in place. See `round2_wall_edge_review.json` and `round2_wall_shell_top.png`.

### Changes and evidence

- Added charcoal carpet to the two ground-slab faces registered inside classroom 1086. This is explicitly an estimated finish; the 2024 plan does not specify flooring.
- Added restrained ochre variation to the modeled atrium columns, informed by the dated 2003 Purdue eArchives interior image and Purdue Business's 2022 atrium image. These sources support the general warm palette and multi-level atrium, but do not establish today's exact finish.
- Added approximate cap/post details to the existing modeled glass atrium guardrail panels. Their placement follows the existing panel runs; upper-floor railing layout remains estimated because matching upper-floor plans were not available.
- Tuned the glass material and brick close-up presentation. The brick course remains continuous around the perpendicular corner at close scale. In the saved exterior/close-up views, the window panels still read dark and the tested shader variants did not produce a dependable visible glazing improvement; treat glazing appearance as unresolved rather than claiming a verified material match.

### Views and saved-file check

`exterior_round2.png`, `brick_glazing_closeup_round2.png`, `brick_course_detail_round2.png`, and `interior_1086_round2.png` are the useful round 2 views. The attempted core and atrium cutaways (`interior_core_cutaway_round2.png`, `atrium_exposed_round2.png`, `atrium_looking_up_round2.png`) show existing multilevel structure but are weak documentation views: floor slabs obscure the core and the views do not establish room-by-room upper-floor layouts. No unsupported partitions were added. The 2024 first-floor plan is the only plan source used for room layout.

Reopened `modular/buildings/rawls_hall.blend` in Blender 5.2.3 and ran the saved-asset checks. The asset collection contains 722 objects (714 meshes), the root remains identity/unparented, and no external image paths are missing. Round 2 edits and the unchanged wall flags are recorded in `round2_model_changes.json`. The master blend, manifest, and other building assets were not edited.

Sources and limitations for Purdue's plan, 2003 archive photo, 2022 atrium image, and Google Maps satellite/Street View access are documented above in “Sources checked.” Google Maps showed Airbus/Maxar ©2026 satellite imagery without an exposed capture date; nearby Street View showed May 2026 but was not a head-on dimensioned survey. Registration remains approximate at 1–2 m. This is a reviewable round 2 pass, not a claim of a 9/10 score.

## Round 3 pass (2026-10-23)

### Work completed

- Measured the north glazing mesh against the masonry bounds. Pane vertices were about 0.6 m behind the north façade plane. Moved the north glass and bronze mullion assemblies +0.60 m in Y and changed the glass to opaque blue-gray satin with a slight daylight lift. This is intended to make the pane assemblies visible at the modeled reveal; exact present-day tint remains unverified. See `round3_model_changes.json`, `exterior_round3.png`, and `brick_glazing_closeup_round3.png`.
- Produced `first_floor_plan_cutaway_round3.png` by selectively hiding roof, upper slabs, and unrelated shell objects while showing the first-floor plan partitions, ground-slab outline, and 1086 furniture. This makes the first-floor wall arrangement and classroom placement readable in one view. The 2024 plan remains the only source for room layout; render lighting/materials are diagnostic.
- Produced `atrium_open_section_round3.png`, showing the existing four-level atrium columns and modeled glass guardrail runs with upper slabs hidden. The 2003 Purdue archive interior and 2022 Purdue image support the general multilevel atrium/guardrail/column treatment. They do not support exact current circulation or room layouts. No stair or bridge geometry was invented from a photograph without dimensions or confirmed location.

### Plan1086 edge

No better dimensioned GIS control points were found in the saved evidence or 2024 first-floor plan. The earlier shell overlay remains approximate, with 1–2 m horizontal registration uncertainty. The Plan1086 wall remains unmoved; its 2.10 m bbox-corner overhang and 1.27 m centroid distance remain unresolved and should be checked if survey or dimensioned architectural data becomes available. The other ten wall flags remain provisional as documented in round 2.

### Verification

Reopened the saved standalone blend in Blender 5.2.3 and reran `final_checks.py`: 722 collection objects / 714 meshes, identity unparented root, no missing image dependencies, and active red-brick shader links. Round 3 edits were confined to `modular/buildings/rawls_hall.blend`; no master blend, manifest, shared script, or other asset was changed.

This is a saved round 3 candidate for independent review. The north glazing treatment needs reviewer confirmation in the full scene, and interior circulation/upper floor detail remain constrained by the available evidence.
