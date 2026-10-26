# Rawls Hall R9 handoff

## Review target and result

This revision addresses the R8 independent review (7.1/10), which found that most of the southeast facade read as opaque, only two panes had been demonstrated in the close-up, and the available interior/campus registration evidence remained limited. The revised standalone asset is `modular/buildings/rawls_hall.blend`.

## Changes

- Used the existing 44 modeled southeast diagonal-glass pane quads as the source of exact window positions and extents. Opened matching apertures through the two obscuring exterior shell skins and exposed the modeled panes. This changes the existing facade glazing treatment; it does not add new window positions or enlarge the source pane geometry.
- Replaced 44 full-pane bronze slab objects with 176 narrow bronze frame bars (four per existing pane) so the glazed areas are visible.
- Opened six first-floor apertures in both skins of the plan-derived Room 1086 wall, aligned to the first row of existing panes, to create a through-glass sightline into the modeled desk rows.
- Left the structural shell massing and facade pane layout intact. Did not move the plan-derived wall because no independent surveyed control justifies a shift.

## Sources and interpretation

Retrieved 2026-10-25:

- [Fink Roberts & Petrie, Rawls Hall project](https://frpinc.com/projects/rawls-hall-krannert-school-of-management/) — supports the four-storey building, entry foyer, glass-roofed atrium, and has project photographs attributed to Scholer Corp. It does not dimension the southeast openings.
- [Purdue Office of Emergency Preparedness, Rawls Hall](https://www.purdue.edu/operations/emergency-preparedness/rawl/) — describes four floors, large windows, and the open ceiling design.
- [Purdue Road School 2024 Rawls Hall plan](https://roadschool.purdue.edu/maps/2024%20Rawls%20Hall.pdf) — first-floor plan only; used by prior rounds to support the Room 1086 room layout. It does not establish upper-floor partitions or surveyed shell registration.
- [Purdue Registrar classroom database](https://www.purdue.edu/registrar/faculty-staff/scheduling/classroom-database/) — points to official room planning information, but is not a detailed floor plan.
- [Daniels School of Business IT FAQ for Rawls 1086](https://kcc.krannert.purdue.edu/Faq/Item/811) — supports the modeled room's teaching/classroom use, not exact furnishings or interior finishes.

Verified from project geometry: the pane quad positions/extents, repeated facade pattern, room 1086 plan-derived wall location, and existing interior furnishings. Inferred/estimated: the hidden facade portions are intended to be glazed based on the supplied pane geometry and public descriptions/photos; specific modern interior finishes, upper-floor circulation, and exact construction details are not claimed as verified.

## Render and reopen evidence

- `se_curtainwall_full_round9.png` shows the complete southeast facade with its four repeated rows of glazing.
- `se_curtainwall_through_glass_round9.png` shows the pane/frame and first-floor Room 1086 desk rows in one sightline.
- `round9_reopen_validation.json` is a fresh Blender 5.2.3 reopen report for the final asset. It records the exact SHA-256, scene/object counts, identity root transform, 44/44 clear exterior shell rays, 44/44 clear first-floor wall rays within the tested range, no materialless meshes, no external image files, no linked libraries, and no mesh bounds exceeding the 120 m outlier check.
- `round9_change_set.json` records the generated geometry/source basis and candidate hash.

## Remaining uncertainty

- The plan-to-shell registration is still uncertain by about 1 m based on prior project evidence. The first-floor wall was opened at the current modeled pane alignment but was not shifted without survey controls.
- Only first-floor room 1086 geometry is supported by the available plan. Upper-floor partitions and circulation remain schematic or absent.
- Interior furnishings/finishes and facade construction behind the pane geometry remain simplified or inferred.
- This is a technical/evidence update for independent review, not a claim that the building has reached the 8/10 threshold.

## Asset identity

Final path: `modular/buildings/rawls_hall.blend`

SHA-256: `5ea4dde459d6ed6a594f49bf7c30411a6ed960124c8580e3fb7832d7f91f6910`

No master scene/shared index or README was modified. No commit was created.
