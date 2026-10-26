# Independent Rawls Hall review — R9

## Result

**Independent score: 7.6/10 — below the 8.0/10 completion threshold.** The review target is `modular/buildings/rawls_hall.blend`, SHA-256 `5ea4dde459d6ed6a594f49bf7c30411a6ed960124c8580e3fb7832d7f91f6910`. I reopened that exact file independently in Blender 5.2.3 and inspected the R9 southeast elevation and through-glass views, alongside the existing north and site-context views, the prior R8 review, and available Purdue/FRP reference material.

R9 resolves the concrete R8 facade defect: all 44 existing pane positions now read as glazing rather than being covered by the shell or full-pane bronze slabs. Independent ray checks confirm that all 44 pane centers clear the exterior shell and the first-floor 1086 wall. The new interior sightline helps, but it reveals a sparse, diagrammatic classroom rather than a well-supported interior. The model also has no verified upper-floor circulation, current interior finish, or master placement check.

## Scorecard

| Category | Score | Findings |
|---|---:|---|
| Exterior form and detail | 8.2/10 | The full southeast view now reads as four repeated glazed rows set into the brick elevation, and the arched roof penthouse is recognizable. The model remains repetitive and simplified at the roof edge and base; the R9 work did not add the documented fourth-floor pedestrian bridge or improve other elevations. Pane locations come from existing model geometry, not a new dimensioned facade survey. |
| Materials and texturing | 7.6/10 | Brick, light-colored bands, bronze frames and blue-gray glass are coherent and assigned. The full-elevation glass still reads dark and reflective, so transparency is clearest only in the close view. Surface detail and facade color are not verified against a dated, location-specific current photograph. |
| Interior completeness | 6.5/10 | The new through-glass view makes desks in Room 1086 visible and the openings are connected through both wall skins. The room is still a sparse schematic with a large plain overhead surface and no clear tiered seating, lectern, surrounding partitions or route to the broader atrium/core. Purdue's classroom listing describes 1086 as tiered with occupancy 136; the visible tables do not substantiate that arrangement. Upper floors and current interior finishes remain unverified. |
| Technical integrity and placement | 9.3/10 | The exact SHA reopens with 722 objects and 714 meshes, an identity asset root, 18 used materials, no materialless/invalid-slot meshes, no file-backed images or linked libraries, and no mesh-bound outliers over 120 m. All eight repaired parent inverses independently test identity. Independent BVH checks found 44/44 pane rays clear through the shell and 44/44 clear through the tested 1086 wall. This does not check the master placement marker or assembled campus position. |
| Evidence and source fit | 7.4/10 | The handoff records the R9 geometry edits, source URLs, date and uncertainty, and the independent reopen is reproducible. FRP supports the four-story building, large public foyer, arched glass roof penthouse and a fourth-floor bridge; Purdue OEP supports four floors, basement, large windows and open ceiling. The 2024 plan supports only first-floor arrangement, and Purdue's 1086 page says the room is tiered/136 capacity. R9's 44 window coordinates are inherited from the modeled pane quads, not independently surveyed against elevation imagery; plan-to-shell registration remains about 1 m uncertain. |
| **Weighted total** | **7.6/10** | **Does not meet the 8.0/10 pass threshold.** |

Weights follow the project rubric used for R8: exterior 30%, materials 20%, interior 30%, technical 10%, evidence 10%. Calculation: `8.2×0.30 + 7.6×0.20 + 6.5×0.30 + 9.3×0.10 + 7.4×0.10 = 7.65`, rounded to **7.6/10**.

## R9 change assessment

- **Glazing occlusion: pass.** The shell now has apertures aligned to the 44 existing southeast panes, with reveal edges, and the full-pane bronze slabs were replaced by narrow frame bars. Independent Blender BVH tests from each pane center found no shell hit within 1.2 m and no first-floor 1086 wall hit within 2.0 m. These checks establish an unobstructed sightline at the modeled pane positions; they do not prove those positions or widths match a surveyed facade.
- **Facade readability: improved.** The full southeast render clearly shows all four pane rows, avoiding the broad opaque recesses criticized in R8. From the full elevation, the glass is still dark and largely uniform; the close view is needed to read the classroom through the glazing.
- **Interior sightline: improved but incomplete.** The through-glass image shows two rows of generic desks and a plain interior volume. It does not show the tiered 1086 classroom described by Purdue, a lectern/front wall, connected stair/core circulation, or a convincing continuation into the atrium. The white semicircular/overhead surface dominates the top of the opening and obscures the room view.
- **Preserved uncertainty: appropriate.** The R9 handoff does not claim new window locations, upper-floor layout, exact facade construction, or survey-grade registration. The approximate 1 m plan-to-shell alignment remains unresolved.
- **Master placement: unreviewed.** This is a standalone-library grade. The coordinator must check `Placement_rawls_hall` against the manifest and reopen the full master before integration.

## Prioritized R10 work

1. Use the official 1086 room information and the available plan to make the sightline show a plausible tiered classroom, lectern/front wall and room boundary. Keep the 136-person capacity label tied to the source; do not infer exact seat count or dimensions from it.
2. Improve the view through the southeast panes by reducing the opaque-looking overhead occluder and showing the room behind the glazing under a normal exterior camera, while preserving the current pane and reveal geometry unless independent elevation evidence supports edits.
3. Add or verify circulation between 1086, the atrium/core and upper levels only where plans or official images support it; otherwise retain a clearly marked schematic.
4. Compare the facade and arched roof penthouse with a saved dated/identified exterior photo or architectural elevation. Record what is verified separately from the model-derived 44-pane layout.
5. Have the coordinator verify the master placement marker and surrounding campus alignment; this independent standalone review did not check them.

## Sources consulted

- [Fink Roberts & Petrie — Rawls Hall / Krannert School of Management](https://frpinc.com/projects/rawls-hall-krannert-school-of-management/) — four-story form, large entry foyer, glass-enclosed arched roof penthouse and fourth-floor pedestrian bridge.
- [Purdue Office of Emergency Preparedness — Rawls Hall](https://www.purdue.edu/operations/emergency-preparedness/rawl/) — current first-responder description of four floors plus basement, glass railings, large windows and open-ceiling design.
- [Purdue Road School 2024 — Rawls Hall first-floor plan](https://roadschool.purdue.edu/maps/2024%20Rawls%20Hall.pdf) — first-floor room layout only.
- [Purdue Daniels School IT — Rawls 1086](https://kcc.krannert.purdue.edu/Faq/Item/811) — 1086 occupancy 136 and table type tiered; does not provide dimensions or a complete interior plan.
- [Purdue Daniels School — Rawls Hall interior images](https://business.purdue.edu/news/info/Building/Rawls-interior-image.php) and [Purdue Libraries archive item 3050](https://earchives.lib.purdue.edu/digital/collection/pbuildings/id/3050/) — interior/atrium context; the archive photo is from 2003 and is not evidence of current finishes.

## Reviewed artifacts

- `modular/buildings/rawls_hall.blend` (independently reopened read-only)
- `audit/batch4_rawls/se_curtainwall_full_round9.png`
- `audit/batch4_rawls/se_curtainwall_through_glass_round9.png`
- `audit/batch4_rawls/north_exterior_round8.png`
- `audit/batch4_rawls/sidewalk_southwest_round8.png`
- `audit/batch4_rawls/round9_handoff.md` and `round9_change_set.json`
- `audit/batch4_rawls/round9_reopen_validation.json`
- `audit/batch4_rawls/independent_reopen_r9.json`
- `audit/batch4_rawls/independent_review_round8.md` and `.json`
- `audit/batch4_rawls/2024_plan_geometry_overlay_round6.png`, `atrium_void_clear_section_round6.png`, and `core_plan_detail_round7.png`

Asset modified: **no**. Master/shared files modified: **no**. Commit created: **no**.
