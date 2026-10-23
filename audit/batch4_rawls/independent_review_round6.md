# Rawls Hall independent review — round 6

## Result

**Independent rating: 7.0/10** (weighted 6.99/10). Round 6 improves the review evidence and lowers the mortar contrast, and the saved blend reopens cleanly. The 2024 first-floor plan overlay makes the intended room layout easier to compare. The remaining score limiters are the glazing, which still reads as opaque blue panels in the visible exterior close-up, and the lack of a normal through-glass view into a source-supported room. The one room image is explicitly a render-only cutaway, with the glass and three intervening walls hidden. Exact site registration and current finish evidence remain approximate.

| Category | Score | Review |
|---|---:|---|
| Exterior form and detail | 7.7/10 | The overall massing and repeated floor/window rhythm read clearly. The south wall now has real openings, reveals, and narrow frames. The available exterior views still simplify facade transitions, the base, roof equipment, and several glazed areas; the evidence is not a full surveyed elevation check. |
| Materials and texturing | 6.6/10 | The revised close-up has plausible brick scale and reduced mortar contrast, though the procedural courses remain regular and pronounced at close range. The blue-gray glazing is visually clean, but it reads as opaque panels in the exterior renders; the round6 transmission change has not demonstrated visible interior depth. |
| Interior completeness | 6.1/10 | The overlay is useful for checking the modeled first-floor plan against the source. The sightline cutaway shows the furnished Room 1086 volume and gives a real room target, but it is not a through-glass render: the pane and three intervening source-plan partitions are hidden for the image. The room remains a sparse classroom mockup with generic tables/chairs and little visible finish or context. The atrium view clarifies the modeled void, columns, and rails, but does not show verified stairs, landings, or circulation. |
| Technical integrity and placement | 8.8/10 | I reopened the saved asset in Blender 5.2.3 LTS: 722 objects, 714 meshes, one 722-object asset collection, and no missing file-backed images were reported. The recorded root is identity and unparented. The first-floor rays intersect the expected panes and plan partitions. These checks do not resolve the approximate 1–2 m GIS registration or the Plan1086 boundary ambiguity. |
| Evidence and source fit | 6.5/10 | The 2024 plan is an appropriate source for the shown first-floor room/core boundaries and the overlay visibly relates the geometry to that plan. The handoff carefully labels the room furnishings and atrium finishes as estimates. Google Maps is documented as a visual access check, but no dated source screenshot or dimensioned survey is preserved. Historical atrium imagery supports broad character only. |

Weighted by the prior review formula (exterior 30%, materials 20%, interior 30%, technical 10%, evidence 10%): **6.99/10, rounded to 7.0/10**.

## Specific findings

- **Plan overlay:** `2024_plan_geometry_overlay_round6.png` is useful and clearly shows the drawn 2024 plan beneath the plan-derived geometry, including the Room 1086 furniture footprint and adjacent rooms/core. It is a visual registration aid; without control-point residuals or a dimensioned survey, it does not prove exact scale or placement.
- **Room sightline:** The saved model contains glass and the plan partitions, but the chosen render hides the north pane and `RAWL_2026_PlanNWVestibule_03_00`, `RAWL_2026_PlanNWVestibule_01_01`, and `RAWL_2026_Plan1086_04_00` for an illustrative cutaway. It therefore proves that a desk-filled modeled room exists behind the general north-side path, not that the pane gives a clear sightline or that these furnishings/finishes match current Room 1086.
- **Glazing:** The round6 close-up looks nearly identical in visual role to round5: cool blue, smooth, uniformly filled rectangles with dark perimeter edges. The new shader values are verified in the saved file, but the output does not visually establish recognizable glass depth or a visible occupied room behind a pane.
- **Brick:** The round6 mortar is less bright than the earlier close-ups, improving contrast. Course spacing is consistent at the stated 0.215 m width and 0.075 m height. The procedural pattern remains conspicuously uniform at close range.
- **Atrium:** The unobstructed round6 section makes the clear void, columns and three rail levels easy to read. Thin rail runs and vertical infill appear skeletal at this scale; no stair/bridge connection is shown. The source notes appropriately avoid asserting exact current atrium finishes or circulation.
- **Source limits:** The 2024 public first-floor plan supports that floor’s general layout. It does not document the exact brick/glass palette, upper-floor partition layout, current classroom fit-out, or present-day atrium details. The documented nearby Google Maps Street View is not a head-on measured facade reference, and its capture date is not reproducibly evidenced in the audit folder.
- **Technical caveat:** `round6_checks.json` carries forward round5 multi-hit rays because round6 only changed materials. That is reasonable for geometry, but the ray evidence should be described as inherited geometry checks rather than fresh round6 ray runs.

## Prioritized fixes

1. Make the saved panes read as glass in a normal exterior view and show a credible interior behind at least one pane without hiding the pane or source-supported room partitions. Add lighting/interior depth as needed; test from an ordinary exterior camera.
2. Improve the supported interior presentation with room-boundary and doorway context, and refine the generic furniture/materials only where references support it. Keep the cutaway version as a clearly labeled supplemental view.
3. Add reproducible plan registration evidence, such as named control points and residuals, and obtain a dimensioned tie or authoritative GIS transform before claiming tighter placement than the documented 1–2 m.
4. Refine close-range brick/mortar variation and the simplified facade/base/roof details against reproducible current references.
5. Keep atrium circulation and current finishes labeled unresolved until supported by plans or sufficiently clear, location-verified sources.

The asset is technically sound and the new plan overlay and cutaway improve reviewability. It does not meet a 9/10 threshold yet because the saved glass appearance and verified interior/exterior sightline remain unresolved.

## Reviewed evidence

- `audit/batch4_rawls/2024_plan_geometry_overlay_round6.png`
- `audit/batch4_rawls/north_1086_room_sightline_cutaway_round6.png`
- `audit/batch4_rawls/brick_mortar_closeup_round6.png`
- `audit/batch4_rawls/atrium_void_clear_section_round6.png`
- `audit/batch4_rawls/round6_checks.json`
- `audit/batch4_rawls/round6_handoff.md`
- `audit/batch4_rawls/round6_model_changes.json`
- `audit/batch4_rawls/plan.png`
- `audit/batch4_rawls/interior_reference.jpg`
- Prior facade context: `audit/batch4_rawls/exterior_round4.png`, `south_elevation_round5.png`, `south_glazing_closeup_round5.png`

Asset modified: **no**.
