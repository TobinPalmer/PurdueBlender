# Rawls Hall independent review — round 3

## Result

**Independent rating: 6.4/10.** Round 3 produces a substantially more readable first-floor overview and an exposed atrium section. The north-pane edit remains unverified as a façade improvement: the full exterior and close-up still read as dark, opaque window recesses, and the stated +0.60 m shift appears large enough to risk projecting past the exterior wall plane. No measurement shown in the evidence establishes that the moved pane lands correctly within its reveal.

| Category | Score | Review |
|---|---:|---|
| Exterior form and detail | 6.6/10 | Massing, floor bands, entrance, curved end bay, and roof skylight are clear. The repetitive façade openings remain dark flat rectangles in the exterior and close-up. The roof view is informative but details are still simplified and lack a source-matched view. |
| Materials and texturing | 6.0/10 | Brick scale and corner continuity read well at close range. Mortar remains graphic. Round 3's blue-gray glass does not read as glazing in the full-scene or close-up views, and neither view shows reflection, transparency, or interior depth. The isolated test shows a uniformly opaque flat panel, not glass behavior. |
| Interior completeness | 5.8/10 | The first-floor cutaway now communicates the main registered plan shape, curved 1062/1054 area, and 1086 classroom furniture. At whole-building scale, small core rooms, door swings/openings, and partitions are difficult to distinguish; the pale slab and thin wall strokes lack enough contrast for precise room-by-room comparison. The classroom interior has 42 table/chair pairs and carpeting but otherwise plain walls. The atrium section exposes the columns and floor bands, but does not clearly show guardrail panels, a stair, bridge, or circulation. |
| Technical integrity and placement | 7.2/10 | Independently reopened modular/buildings/rawls_hall.blend with Blender 5.2.3. It contains 722 collection objects (714 meshes), no missing external image paths, and an identity unparented asset root. The north pane and mullion objects both save at Y=+0.60 m. The 1086 wall remains unresolved: its bbox corner is 2.10 m outside the approximate shell polygon and centroid 1.27 m outside, within the disclosed 1–2 m registration uncertainty. |
| Evidence and source fit | 6.5/10 | The 2024 Purdue first-floor plan supports the layout shown in the cutaway. Purdue's 2003 archive photo and 2022 atrium image support a multilevel atrium and broad warm palette, but not exact present-day finishes, rail dimensions, current circulation, or upper-floor partitions. Google Maps is recorded as an access observation without a saved reproducible facade image. |

Overall uses the prior review's weighting (exterior 30%, materials 20%, interior 30%, technical 10%, evidence 10%): **6.41/10, rounded to 6.4/10**.

## Round 3 verification

- Reopened the saved asset directly in Blender 5.2.3. It reported 722 objects / 714 meshes in Asset_rawls_hall, no missing image dependencies, and an identity, unparented AssetRoot_rawls_hall.
- Confirmed the saved RAWL_North_Windows_Glass and RAWL_North_Windows_BronzeMullions object locations both include the +0.60 m Y shift and their assigned materials.
- Inspected exterior_round3.png, brick_glazing_closeup_round3.png, brick_course_detail_round3.png, facade_glazing_isolated_round3.png, facade_glazing_moved_test_round3.png, first_floor_plan_cutaway_round3.png, atrium_open_section_round3.png, and interior_1086_round2.png.
- Compared the cutaway against plan.png and the source/uncertainty record in round1_notes.md.

## North glazing and reveal

The pane/mullion offset is recorded as +0.60 m on world Y. The evidence note states the north glass vertices had spanned Y=20.16..20.72 while the masonry bbox reaches Y=20.79, and says the shift clears the reveal. That arithmetic implies the shifted span would be about Y=20.76..21.32 if those bounds are in the same world coordinate system: its nearest edge would just reach the wall's outer bound, while much of the assembly would extend roughly 0.53 m beyond it. The note does not provide a per-pane depth survey or reveal profile to show whether that is intended. Treat the claimed reveal fit as unverified and inspect the moved panels against a section or perpendicular façade view before keeping the offset.

Visually, exterior_round3.png retains dark brown-gray openings, and brick_glazing_closeup_round3.png shows deep, flat-looking voids with no pane highlights or interior. The isolated test is a uniformly filled opaque panel. This does not demonstrate an improved real façade glazing treatment. The facade test views show pale opaque rectangles when viewed separately, but that appearance is not carried through in the saved hero view. A next pass should verify pane geometry relative to the masonry reveal and use a controlled neutral daylight/reflective setup with visible frames and a representative close-up.

## First-floor plan and atrium views

The new top-down cutaway is the best round 3 improvement: it shows the main partition arrangement and the 1086 desk/chair field on a common plan view, and broadly follows the source diagram's overall orientation and room grouping. It is still a diagnostic render rather than a precise plan audit. In particular, the central core/washroom/stair cluster is difficult to resolve at this framing; wall strokes are fine and the transparent-looking gray slab competes with them. A closer core view with wall thickness, clear door gaps, and scale-matched source overlay would make correctness checkable.

atrium_open_section_round3.png reveals the four-level vertical structure, but the nearly empty section reads as repeated columns and horizontal floor bands. Guardrail glazing is too subtle to verify; the view contains no visible stairs, bridge, or occupied circulation. The source photo supports an atrium character reference but cannot establish these missing positions or dimensions. This is useful as a structural diagnostic, not evidence of a finished atrium interior.

## Prioritized fixes

1. Recheck north panes in a façade-normal section and measure their final surface against the actual reveal. Resolve whether the +0.60 m offset is correct; then render the saved full scene and close-up under neutral daylight so the panes visibly read as glass with frames/mullions.
2. Improve the cutaway's core legibility with a closer plan detail or source-plan overlay, clearer wall material/line weight, and visible door openings. Keep the full-floor view as a useful companion.
3. Add evidence-supported stair/bridge/circulation and make guardrail glass visible in the atrium view. Avoid inferring exact location or layout from the historical photo alone.
4. Keep the Plan1086 edge documented as unresolved until dimensioned registration evidence is available. Do not treat the centroid-in-shell check as a survey-grade placement test.
5. Reduce graphic mortar contrast and add a neutral roof/detail comparison tied to a clear source image.

This review does not certify current-condition glazing, survey-grade placement, upper-floor room layouts, or an exact current atrium configuration.
