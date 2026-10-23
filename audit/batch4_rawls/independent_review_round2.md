# Rawls Hall independent review — round 2

## Result

**Independent rating: 6.3/10.** Round 2 improves the saved asset with clearer brick scale, an estimated classroom carpet finish, and atrium color/guardrail details. It does not yet reach 9/10: the windows still render as opaque dark recesses, most of the interior remains unfinished or undocumented, and the core cutaway is not useful for checking the plan.

| Category | Score | Review |
|---|---:|---|
| Exterior form and detail | 6.6/10 | The stepped massing, repeated floor bands, entrance, curved end bay, and rooftop skylight are readable. The roof render is a useful overview, but the roof equipment and skylight structure are simplified. The many window openings appear as unlit brown-gray recesses without visible glazing or mullions, which is a prominent visual and source-fit gap. |
| Materials and texturing | 6.2/10 | Closeups show legible brick courses and continuity around the exterior corner. The brick scale reads plausible at this view, although mortar and bump remain graphic. The estimated dark carpet differentiates classroom flooring and the ochre column finish adds some warmth. Large wall surfaces remain plain, classroom tables and chairs look generic, and window glazing is not visually established. |
| Interior completeness | 5.6/10 | The eye-level classroom view has 42 table/chair pairs, visible supports, and a carpeted floor. It is still an almost empty shell beyond those furnishings. The first-floor cutaway exposes slabs and roof geometry rather than a legible room plan. The attempted core cutaway is blank/obscured, and the atrium views are dominated by slab undersides and simple repeated columns/rails; they do not verify circulation, stairs, bridges, or upper-floor rooms. |
| Technical integrity and placement | 7.2/10 | Independently reopened the saved asset in Blender 5.2.3. It contains 722 objects (714 meshes), the asset root is identity/unparented, and no missing image dependencies were reported. The saved brick material has active color/bump links, and the room furniture is visible. The 11 wall flags are now assessed against the registered plan and edge bounds. This supports leaving them unmoved for now, but does not prove full containment or survey placement; one 1086 corner reaches 2.10 m beyond the shell polygon. |
| Evidence and source fit | 6.7/10 | The saved 2024 Purdue plan supports first-floor layout; the 2003 Purdue archive photo supports historical atrium character; the 2022 image is cited as additional atrium context. The dated photo visibly shows the skylight, multilevel space, bridges/rails, stair, wood-clad volume, and warm ochre curved wall/columns. Round 2 uses some of that character, but current finishes/configuration are not established. Google Maps evidence remains a written access note, not a preserved, reproducible facade comparison. |

Overall rating uses exterior 30%, materials 20%, interior 30%, technical 10%, and evidence 10%: **6.29/10, rounded to 6.3/10**.

## Wall-edge audit

I reviewed `round2_wall_edge_review.json`, `round2_wall_flags.json`, `round2_wall_shell_top.png`, and the registered plan overlay. The flags cluster along plan perimeter/core edges rather than appearing as isolated interior partitions. The five adjacent 1062 curve pieces each exceed the shell by 0.37–0.92 m; 1054 is 0.92 m; the two 1098 segments reach 1.62–1.65 m; CoreNorth reaches 0.30 m; and NWUpperRoom reaches 1.89 m. These are consistent with the stated approximate 1–2 m registration uncertainty, so moving them based on the polygon test alone would be premature.

`RAWL_2026_Plan1086_02_00` is the closest case to the uncertainty bound: centroid is 1.27 m outside and a bounding-box corner is 2.10 m outside. The overlay supports a general plan-to-shell alignment but is not precise enough to resolve this long wall at the edge. Keep the current decision to leave all 11 walls in place provisionally, while documenting 1086 as an unresolved edge requiring a better registration or source measurement. The current check evaluates a ground-shell polygon and wall bounds, not true facade intersection, wall thickness, or actual room-side containment.

## Prioritized fixes

1. **Make the facade windows read as glazing.** Inspect the opening geometry and whether brick/wall faces occlude the pane objects. Add visible reveals, frames, mullions, and a controlled blue-gray glass response, then render one representative facade closeup. The three shader variants are visually indistinguishable in the saved tests, so material-only tuning is not sufficient evidence of a fix.
2. **Produce a correct first-floor plan/cutaway view.** Keep plan walls visible, hide overhead slabs and unrelated shell geometry selectively, and frame the whole first-floor layout. Show room 1086, 1054/1062, stair/core, toilets, and door openings against the 2024 plan so partition completeness and circulation can be checked.
3. **Complete and document the interior.** Add only evidence-supported core/stair/atrium pieces, and capture eye-level views through the core and atrium. The archived photo can guide historical palette and spatial cues, but should not be treated as proof of current room finishes or exact upper-floor layout. Clearly tag unsourced finishes as estimates.
4. **Resolve the 1086 boundary discrepancy.** Improve the GIS-to-plan registration with a reproducible, dimensioned source or better control points, then re-evaluate the full wall geometry. Keep the other ten perimeter flags documented as registration-sensitive unless better evidence identifies a specific error.
5. **Refine the close-range materials and roof evidence.** Brick is now inspectable at close range; reduce the graphic mortar contrast or show a neutral daylight comparison. Provide a source-linked roof view to support the arch/rib form and rooftop equipment before refining them.

## Saved-file verification and evidence inspected

- Reopened `modular/buildings/rawls_hall.blend` in Blender 5.2.3 by running the read-only `final_checks.py` inspection. It reported 722 objects, 714 meshes, identity root transforms, no missing image paths, and active brick node links.
- Inspected `exterior_round2.png`, `brick_glazing_closeup_round2.png`, `brick_course_detail_round2.png`, `interior_1086_round2.png`, `first_floor_cutaway_round2.png`, `core_plan_wall_cutaway_round2.png`, `interior_core_cutaway_round2.png`, `atrium_exposed_round2.png`, `atrium_section_round2.png`, `atrium_looking_up_round2.png`, and the three glass tests.
- Compared `plan.png`, `registration_overlay.png`, `round2_wall_shell_top.png`, and the JSON edge measurements.
- Inspected the preserved 2003 Purdue eArchives photo and the source/uncertainty notes in `round1_notes.md`.
- Relevant recorded sources: [Purdue Road School 2024 Rawls Hall first-floor plan](https://roadschool.purdue.edu/maps/2024%20Rawls%20Hall.pdf), [Purdue eArchives photo PPBUC03065](https://earchives.lib.purdue.edu/digital/collection/pbuildings/id/3050/), and the architect project page listed in the audit notes.

This review does not certify survey-grade placement, the exact current facade or finishes, or upper-floor room layouts. The Google Maps access notes do not include a saved image, and the historical archive image is not a current-condition survey.
