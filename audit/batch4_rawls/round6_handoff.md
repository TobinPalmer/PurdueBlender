# Rawls Hall round 6 handoff — 2026-10-23

## Saved asset and scope

`modular/buildings/rawls_hall.blend` was saved, then reopened in Blender 5.2.3 for a fresh technical inventory. This pass changed the brick mortar contrast and glazing material only; it did not change building geometry or placement. The 2024 first-floor plan was aligned with the plan-derived room geometry in `2024_plan_geometry_overlay_round6.png`. The master, manifest, shared scripts, and other buildings were not edited.

## Material adjustments

- Brick course/width remains 0.075 m / 0.215 m; only mortar color and mortar width were changed to reduce contrast. `brick_mortar_closeup_round6.png` shows the revised mapping. The closeup is visibly regular but is still a procedural material, not a surveyed brick-by-brick texture.
- Glazing was adjusted to cool blue-gray, transmission 0.40, roughness 0.14, IOR 1.45. The physical pane render remains reflective/opaque-looking at the chosen exterior angle; a shader change did not by itself resolve the visibility issue.

## Interior presentation and evidence limits

- `2024_plan_geometry_overlay_round6.png` places the 2024 plan behind the plan-derived first-floor layout to show alignment and make the core and Room 1086 relationship legible.
- `north_1086_room_sightline_cutaway_round6.png` is a render-only interior view within the plan-derived Room 1086 footprint. Its camera, added lights, hidden north glass, exterior masonry, and selected intervening vestibule/core walls are temporary render settings and were not saved into the asset. This image demonstrates the modeled desks and room volume, not a literal through-glass photograph or a verified current room fit-out.
- `atrium_void_clear_section_round6.png` isolates the saved columns and evidence-informed railwork to clarify the modeled atrium void. It does not establish exact present-day atrium finish or circulation.
- The saved 2024 plan supports the first-floor layout, vestibule, core, and Room 1086 general footprint. Room materials, occupied furnishings, upper-floor partitions, and atrium details remain estimates or illustrative modeling and should be labeled accordingly.
- Google Maps imagery has no reproducible capture date saved in this audit, so no date-specific satellite/Street View claim is made.
- GIS registration uncertainty remains approximately 1–2 m. The Plan1086 edge ambiguity remains unresolved; don't treat its current fit as a survey.

## Saved model checks

`round6_checks.json` records the reopened asset inventory: 722 objects (714 mesh objects) in `Asset_rawls_hall`, 824 exterior wall faces, 60 north glazing quads / 1,440 frame faces, 8 south glazing quads / 192 frame faces, no missing image dependencies, and an unparented identity root at origin. The prior round5 multi-hit ray checks remain applicable because round6 changed material values only; they are retained in the round6 JSON with that qualification.

No 9/10 rating is claimed. This pass is ready for independent review; the exterior glazing still needs review for visible pane quality and the room sightline is explicitly a cutaway.
