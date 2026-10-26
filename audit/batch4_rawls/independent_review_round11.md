# Rawls Hall R11 independent review

**Result: 8.14/10 — passes the 8.0 threshold.** Reviewed 2026-10-25. The target asset SHA-256 is `19d2ec5828daee8b2529d8b0790422b9a43a9f795b41c6fb2e6bc8c21e1ec9eb`; the exact R10 comparison asset SHA-256 is `d361f211a8177e234d475493d6242ad396981b7f3fed29dc57f37f54e1026d9e`.

## Score

| Criterion | Weight | Score | Review |
|---|---:|---:|---|
| Exterior form and detail | 30% | 8.2 | Brick, repeated southeast windows and glazed roof penthouse read well. Facade geometry is unchanged; secondary elevations, base and exact pane layout remain simplified or unverified. |
| Materials and texturing | 20% | 7.9 | Lower-glare glass makes the interior and screens easier to see than R10. Broad reflection and pane/frame occlusion still reduce clarity. Shader values are estimates. |
| Interior completeness | 30% | 7.9 | 62 chairs, 42 schematic tables, five tiers, two screens, six generic screen cues and a two-part lectern are confirmed. This supports the published seat count without claiming a verified seating layout. |
| Technical integrity and placement | 10% | 9.3 | Fresh Blender 5.2.3 LTS reopen, correct identity root, no missing materials/images/libraries, and all 16 plan/shell/glass geometry records identical to R10. Master placement is outside this review. |
| Evidence and source fit | 10% | 8.0 | Source limits and uncertainty are recorded. Purdue's guide supports 62 seats, fixed tiered tables, dual projectors and a lectern; the separate room FAQ's occupancy figure of 136 is not treated as a seat count. |

Weighted score: `8.2×0.30 + 7.9×0.20 + 7.9×0.30 + 9.3×0.10 + 8.0×0.10 = 8.14`.

## Independent reopen and comparison

I launched Blender 5.2.3 LTS in background mode and opened the saved target `.blend` directly. Its SHA matched the assigned target. The reopened scene has 761 objects (753 meshes), the `Asset_rawls_hall` collection has 761 objects, and `AssetRoot_rawls_hall` has an identity world matrix. There are no materialless meshes, invalid material slots, missing external images or linked libraries.

I separately opened the R10 baseline and compared mesh vertices, polygon indices and world transforms for all 16 named plan/shell/glass structural objects. No structural object changed, went missing or was added. The southeast curtain wall retains 44 polygons/panes. This confirms R11's interior and shader edits did not alter the R10 wall/pane geometry. The earlier R10 independent audit reports 44/44 pane-center rays clear both the exterior shell and tested 1086 wall; I did not present that as proof of all-view visibility.

The model now has 62 chair objects alongside 42 desks/tables. The Purdue 2023 RAWL 1086 guide reports 62 seats, tiered fixed tables, dual projectors and a lectern. That count match is useful, but object count alone does not show that every seat is positioned correctly. R11 retains that limitation. The 2024 Purdue plan is a first-floor plan and does not substantiate upper-floor layout, exact furniture placement or tier heights.

The saved R11 sightline matrix checked 44 panes against 45 classroom targets (42 desks, two projector surfaces and the lectern), finding 1,697 clear pane-target pairs through the tested room/exterior wall geometry. This supports that multiple interior objects are reachable through the facade from different panes; it is not an all-view proof and does not guarantee a specific camera framing.

## Visual assessment

The R11 through-glass render is a meaningful improvement over R10: the table rows, chairs and two small projector cues can be picked out. However, a pale wall/column blocks a substantial part of the view, and a broad dark reflection crosses the upper interior. The classroom remains an illustrative interior rather than a fully evidenced reconstruction. The full southeast elevation remains a clean but repetitive massing/facade treatment, with some lower-level windows reading as obstructed or opaque. No facade geometry was changed from R10.

## Main remaining work

- Reduce the remaining through-glass reflection and choose a less obstructed evidence angle, while preserving the recorded glass uncertainty.
- Improve visibility and spatial clarity of the two projection surfaces and seating in an additional view; don't imply exact projector placement without a source.
- Verify the real furniture arrangement, tier dimensions, window locations and plan-to-shell registration from better drawings or measured references.
- Verify the building's campus placement in the master blend separately.
- Keep upper-floor partitions and circulation marked unverified until a supporting plan/source is found.

## Sources checked

- [Purdue RAWL 1086 Classroom Guide (2023)](https://kcc.krannert.purdue.edu/Faq/Item/Download/2194) — Purdue search index identifies 62 seats, fixed tiered tables, dual projectors and lectern. Direct download timed out during this review.
- [Purdue Rawls 1086 room listing](https://kcc.krannert.purdue.edu/Faq/Item/811) — occupancy 136 and tiered table type; occupancy is distinct from the 62-seat guide count.
- [Purdue Road School 2024 Rawls Hall first-floor plan](https://roadschool.purdue.edu/maps/2024%20Rawls%20Hall.pdf) — opened; identifies first floor and room 1086.
- [Fink Roberts & Petrie Rawls Hall project](https://frpinc.com/projects/rawls-hall-krannert-school-of-management/) — supports four-storey building, atrium roof penthouse and fourth-floor bridge context.

Machine-readable result and reopen details: [independent_grade_r11.json](independent_grade_r11.json), [independent_reopen_r11.json](independent_reopen_r11.json). The reopen script and R10 structural signature set are saved beside them.
