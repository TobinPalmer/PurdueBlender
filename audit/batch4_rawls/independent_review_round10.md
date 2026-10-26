# Independent Rawls Hall review — R10

## Result

**Independent score: 7.9/10 — below the 8.0/10 completion threshold.** I reopened the exact saved asset in Blender 5.2.3 and independently checked its hash, collection, root, materials, dependencies and pane sightlines. R10 improves the Room 1086 view by adding stepped tiers, a lectern and two projection surfaces. It does not yet make the classroom read clearly through the normal southeast exterior view: the central/front wall still blocks much of the room, the projector surfaces are not evident in the submitted close view, and reflected glare remains strong. The modeled 42 desk objects also do not represent the source guide's 62 seats.

| Category | Score | Findings |
|---|---:|---|
| Exterior form and detail | 8.2/10 | R10 retains the readable four-storey brick elevation, repeated southeast glazing and glass-roof penthouse from R9. No new exterior form or facade-detail work was made. Other elevations, the base and roof-edge transitions remain simplified; the inherited 44-pane layout is not independently surveyed. |
| Materials and texturing | 7.8/10 | The blue-gray curtain-wall material is lighter than R9, and brick/reveal variation remains coherent. In the through-glass view the pane is still strongly reflective, with a bright softbox highlight. The full elevation still reads as a repeated dark glazing grid, and the real glass specification/color has not been sourced. |
| Interior completeness | 7.1/10 | Five low platforms and six rising rows make the tiered lecture-room idea more legible. The source guide supports fixed tiered tables, a lectern and dual projectors. However, the submitted view is blocked by the large pale central/front wall, the projector panels are not clearly visible, and the modeled 42 desk objects fall short of the guide's listed 62 seats. Room boundaries and the full seating arrangement remain schematic. No verified route from 1086 into the atrium/core or upper floors is shown. |
| Technical integrity and placement | 9.3/10 | Independent Blender 5.2.3 reopen matches SHA-256 `d361f211a8177e234d475493d6242ad396981b7f3fed29dc57f37f54e1026d9e`: 735 scene/collection objects, 727 meshes, identity root, 18 used materials, no materialless or invalid-slot meshes, missing images, linked libraries or >120 m bounds outliers. Independent BVH tests found 44/44 southeast pane-center rays clear through the exterior shell and 44/44 clear through the tested Room 1086 wall. These center-ray tests do not prove the whole sightline is unobstructed from normal views. Master marker and neighborhood placement were not reviewed. |
| Evidence and source fit | 7.8/10 | The handoff preserves exact hash, source URLs, date, validation and explicit uncertainty. Purdue's 2023 guide supports fixed tiered tables, a lectern and dual projectors, and lists **62 seats**; Purdue's room page separately lists occupancy 136. Neither supplies tier-rise dimensions. The R10 tiers are appropriately labeled schematic, but the view and 42 desks do not yet communicate the cited room capacity/equipment. The 2024 plan is first-floor only; plan-to-shell registration remains uncertain by about 1 m. |
| **Weighted total** | **7.9/10** | **Does not meet the 8.0/10 pass threshold.** |

Weights follow the Rawls rubric used in R8/R9: exterior 30%, materials 20%, interior 30%, technical 10%, evidence 10%. Calculation: `8.2×0.30 + 7.8×0.20 + 7.1×0.30 + 9.3×0.10 + 7.8×0.10 = 7.86`, rounded to **7.9/10**.

## R10 assessment

- **Tiered room cue: partial pass.** Five risers and six rows are a visible improvement. Their 0.13 m rise is explicitly schematic; no dimensioned elevation was found.
- **Source match: partial.** Purdue's guide confirms tiered fixed tables, two projectors and a lectern. It also lists 62 seats. R10 has 42 desk objects; the model should not present that as a complete seat layout. The room listing's 136 is occupancy, not seat count.
- **Sightline: partial.** The remaining central wall and glare obscure the classroom in the through-glass view. The panels/teaching end need to be positioned and framed so the documented equipment reads in a normal exterior camera.
- **Facade and fenestration: unchanged.** The 44 glass panes remain visible and clear of the exterior shell, but their exact positions and widths are inherited from the model and not verified against a dimensioned elevation. The master placement marker remains unchecked.

## Prioritized R11 work

1. Rework the visible room-1086 sightline so the tiered seating, teaching wall, lectern and both projector surfaces read together through the existing glazing. Reduce only the documented camera occlusion; don't move plan-derived walls without better registration evidence.
2. Reconcile the 42 modeled desk objects with the 2023 guide's 62 seats. Use the guide's layout/photo if sufficiently legible, or keep missing positions explicitly schematic; do not infer dimensions from the 136-person occupancy figure.
3. Reduce the bright highlight and glass opacity enough to show the room in the full-elevation camera, while retaining a plausible reflective surface.
4. Preserve explicit uncertainty for the 0.13 m tiers, 1 m plan-shell offset, facade pane layout, upper floors and atrium circulation.
5. Have the coordinator verify the master marker and neighboring campus alignment before integration.

## References

- [Purdue Daniels School / ITaP — RAWL 1086 Classroom Guide (2023)](https://kcc.krannert.purdue.edu/Faq/Item/Download/2194): page 1 lists fixed tiered tables, **62 seats** and dual projectors; page 2 describes the lectern. It does not dimension the modeled tiers.
- [Purdue Daniels School — Rawls 1086 room listing](https://kcc.krannert.purdue.edu/Faq/Item/811): lists occupancy 136 and tiered tables; occupancy is not a seat count.
- [Purdue Road School — Rawls Hall first-floor plan (2024)](https://roadschool.purdue.edu/maps/2024%20Rawls%20Hall.pdf): first-floor layout only.
- [Fink Roberts & Petrie — Rawls Hall](https://frpinc.com/projects/rawls-hall-krannert-school-of-management/): four-story form, public entry foyer, glass-enclosed arched roof penthouse and fourth-floor bridge.
- [Purdue Office of Emergency Preparedness — Rawls Hall](https://www.purdue.edu/operations/emergency-preparedness/rawl/): general building floors/open-ceiling context.

Reviewed asset: `modular/buildings/rawls_hall.blend` (read-only). R10 renders: `se_curtainwall_full_round10.png`, `se_curtainwall_through_glass_round10.png`. Reopen evidence: `independent_reopen_r10.json`.

Asset modified: **no**. Master/shared files modified: **no**. Commit created: **no**.
