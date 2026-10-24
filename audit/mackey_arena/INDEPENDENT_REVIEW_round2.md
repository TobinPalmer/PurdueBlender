# Mackey Arena / SDAC — independent full-building review, round 2

**Grade: 7.9/10 — below the 8/10 acceptance threshold.** I inspected the saved `modular/buildings/mackey_arena.blend` directly in Blender 5.2.3, reopened-source validation, the R2 model views, and the 2023 orthophoto/GIS registration overlay. This is a fresh R2 assessment; the R1 score is not used in the scoring.

## Scoring

The six requested categories are each scored out of 2 (12 raw points total), then normalized to 10. The raw score is 9.5/12, or **7.9/10**.

| Category | Score |
| --- | ---: |
| Identity and footprint | 1.9/2 |
| Placement, orientation and scale | 1.8/2 |
| Height, floors and roof | 1.4/2 |
| Facades and entrances | 1.5/2 |
| Interior and circulation | 1.1/2 |
| Technical and evidence quality | 1.8/2 |
| **Normalized total** | **7.9/10** |

## Findings and evidence

### Identity and footprint — 1.9/2

The saved asset is clearly Mackey Arena and now represents the adjacent Student-Athlete Development Center (SDAC) and visible low-roof perimeter additions. Purdue Athletics and DLZ both describe the three-level SDAC, oversized practice court and three breakout shooting areas. DLZ also describes single-story perimeter additions. The R2 plan view and orthophoto overlay show the circular arena dome plus north-wing and low-roof additions in the right campus context. The Purdue BuildingShapes feature is explicitly composite: it covers the arena/additions envelope rather than providing separate surveyed footprints for each component.

### Placement, orientation and scale — 1.8/2

The overlay was inspected directly. The cyan arena-shell outline closely tracks the 2023 dome roof; the north-wing trace follows the visible roof seam, and the east-side low-roof trace sits against the visible perimeter roof segments. The manifest anchor is approximately `(-209.590, 671.837)` m, with the asset stored in local coordinates. This is strong visual/geospatial consistency evidence, but the project’s local conversion is approximate and the overlay is a registration check, not surveyed control. Some low-roof outlines are partial interpretations inside the composite GIS boundary.

### Height, floors and roof — 1.4/2

The central shell bounds in the saved-asset validation are about 27.9 m high. R2 adds a three-level SDAC with an estimated 14.3 m occupied-roof height and one-storey perimeter additions estimated at 4.6 m; its new geometry peaks at about 15.62 m including roof equipment. The three-level program is supported by the primary project sources. Exact building heights, floor datums, roof equipment and the GIS `Extrution=47` field’s units/meaning are not verified. The R2 asset therefore has plausible massing, but its vertical accuracy remains estimated.

### Facades and entrances — 1.5/2

The oblique preview reads as the arena dome and a multi-storey north wing with glazing, brick and pale bands. HNTB’s project photos support the broad red-brick, vertically articulated upper windows, large lower glazing, curved glass lobby and visible stair character. R2 adds procedural brick, glazing, bronze mullions and limestone-colored bands, and the render confirms the main masses. The render remains schematic: repeated bays are regularized, the new lobby’s exact geometry and entry dimensions are interpretive, and source photos are perspectives rather than calibrated elevations. The broad site overlay does not establish facade detail.

### Interior and circulation — 1.1/2

The arena asset includes a modeled court, two seating tiers, concourse deck, aisle stairs, scoreboard and hoops. The practice-space view shows a full-size marked hardwood court, perimeter glazing and a stair. Purdue Athletics confirms the oversized court and three breakout shooting areas. However, the practice wing’s room divisions and circulation are not sourced or modeled in detail; the three breakout areas are program-level placeholders rather than verified rooms. The single stair is illustrative and does not establish a complete route through the SDAC or between its floors. The saved views do not demonstrate locker rooms, offices, sports medicine, weight training, or other spaces documented for the broader SDAC program.

### Technical and evidence quality — 1.8/2

Direct Blender reopen found scene `Building_mackey_arena`, 391 asset objects (337 mesh objects), 25 Mackey materials, zero linked libraries and no file-backed image dependencies. `validation_r2.json` confirms 391 collection objects, 14 SDAC objects, four one-storey perimeter components, presence of the expected roof/foundation/material objects, and parenting of new components to `AssetRoot_mackey_arena`. The source package preserves the GIS feature snapshot, 2023 imagery metadata, overlay vectors, roof-trace coordinates, source links, and explicit uncertainty notes. Technical confidence is high, but the approximate geospatial conversion and interpretive, partial roof traces preclude a perfect score.

## Uncertainties and decision

- The GIS polygon is a composite additions envelope; the sub-building perimeter geometry is photo-interpreted and not survey-certified.
- SDAC and perimeter heights are estimates; exact floor elevations and roof-equipment placement are unverified.
- Photos establish architectural character, not measured facade bays, entrance dimensions or finishes.
- Practice-court orientation and breakout-room dimensions/layout are not verified by construction plans.
- SDAC room divisions and a complete interior circulation route are not modeled or evidenced.

**Decision: Fail.** The full building scores **7.9/10**, just below the required **8/10** threshold. The strongest next improvement is sourced SDAC interior/circulation detail; a measured section or elevation would also resolve the key vertical uncertainty.

## Source references

- [Purdue Athletics — Mackey Arena](https://purduesports.com/mackey-arena-2)
- [DLZ — Purdue University Mackey Arena Expansion and Renovation](https://dlz.com/projects/purdue-university-mackey-arena-expansion/)
- [HNTB — Purdue University Mackey Athletics Complex](https://www.hntb.com/projects/purdue-university-mackey-athletics-complex/)
- Indiana Geographic Information Office 2023 orthophoto tile `in2023_29971887_06`, 6-inch nominal resolution; local metadata is in `audit/mackey_arena/orthophoto_identify.json` and `orthophoto_export_metadata.json`.

