# Rawls Hall R10 handoff

## Target and reopen result

Refined `modular/buildings/rawls_hall.blend` after the independent R9 review scored the exact R9 asset 7.6/10. Fresh-open validation was performed in Blender 5.2.3 after saving. Final SHA-256: `d361f211a8177e234d475493d6242ad396981b7f3fed29dc57f37f54e1026d9e`.

## R10 changes

- Reshaped the existing 42 desk/chair positions in Room 1086 into six visible elevation rows. Five low carpeted platforms step up by a schematic 0.13 m per row (0.65 m total), and all 168 existing table legs were lifted to match. The count and vertical rise are modeling choices only; the available first-floor plan is not dimensioned for classroom seating or tier heights. Do not interpret the 42 modeled seats as the room capacity.
- Added a pair of simple projection surfaces and a lectern at the teaching end. Purdue's 2023 room guide lists fixed, tiered tables and a lectern and describes dual-projection equipment. Screen size, screen positions, lectern model/location and tier dimensions remain schematic, not surveyed.
- Tuned `RAWL_CurtainWall_Glass` to a lighter blue-gray color, higher roughness and more transmission in response to the R9 finding that the glazing appeared dark and reflective. This is a visual estimate; no measured facade glass specification was located.
- Preserved the modeled 44 pane quads, all pane/reveal geometry and their locations. No facade aperture or room wall locations were moved.
- Added per-object evidence notes for the new classroom geometry and existing first-floor doorway endpoints. No unsupported route to the atrium/core or upper floors was added.

## Verification

- `round10_reopen_validation.json`: fresh reopen in Blender 5.2.3; 735 scene objects, 727 meshes, identity asset root; 44/44 exterior-shell rays and 44/44 first-floor wall rays clear; no materialless meshes, external images, linked libraries or mesh bounds beyond 120 m.
- `round10_classroom_validation.json`: confirms six rows of seven existing desks, corresponding 0.13 m row elevation increments, 168/168 legs updated, five platform objects, two projection surfaces and one two-part lectern.
- `se_curtainwall_full_round10.png` and `se_curtainwall_through_glass_round10.png` rendered from the saved R10 candidate. The earlier large white semicircle is reduced to a small softbox highlight. Some glass reflection and the existing partial wall occlusion remain visible in the through-glass view; no unsupported wall geometry was moved to hide them.

## Sources and uncertainty

Retrieved 2026-10-25:

- Purdue Road School, [2024 Rawls Hall first-floor plan](https://roadschool.purdue.edu/maps/2024%20Rawls%20Hall.pdf) — supports first-floor room and shown doorway layout only. It gives no classroom riser dimensions or measured registration to the shell.
- Purdue Daniels School IT, [Rawls 1086 room listing](https://kcc.krannert.purdue.edu/Faq/Item/811) — occupancy listed as 136 and table type as tiered. Occupancy is not seat count or a geometric dimension.
- Purdue Daniels School, [RAWL 1086 Classroom Guide 2023](https://kcc.krannert.purdue.edu/Faq/Item/Download/2194) — identifies fixed tiered tables, a lectern and dual-projection equipment. Its seating diagram is not used as a surveyed position/dimension source in R10.
- FRP, [Rawls Hall project](https://frpinc.com/projects/rawls-hall-krannert-school-of-management/) — exterior building/roof-penthouse reference.
- Purdue OEP, [Rawls Hall description](https://www.purdue.edu/operations/emergency-preparedness/rawl/) — general four-floor/open-ceiling context.

The approximately 1 m plan-to-shell alignment uncertainty remains unresolved. The 44-pane pattern is inherited from the existing model, not independently surveyed from elevations. Exterior facade and penthouse remain simplified; no new evidence verifies their detailed dimensions or current finish colors. The room layout is a schematic interpretation of the first-floor plan and room guide; upper-floor partitions/circulation remain unverified. Master placement remains outside this asset review.

Asset modified: yes. Master/shared/README files modified: no. Commit created: no.
