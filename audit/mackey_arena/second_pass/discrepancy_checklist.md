# Mackey Arena — exterior discrepancy checklist (baseline r0 vs. references)

Prepared from the r0 asset (SHA `b8d5c120…`) and its first-pass renders before any second-pass edit, then rechecked with matched baseline renders (`baseline/`). Disposition records what r1 changed.

| # | Facade / feature | Baseline r0 | Reference evidence | r1 disposition |
| --- | --- | --- | --- | --- |
| 1 | Drum wall | Full-height dark glass curtain wall with transoms between 36 white buttress pylons | Red-brick drum with 24 pale limestone pilasters; vertical slot-window groups in two of every three bays (2016_02, drone_04, MackeyA) | Rebuilt: brick drum, 24 pilasters, 6-slot groups, plain bays; base sill and top course |
| 2 | Dome | 10 stacked white concentric steps + raised cupola | Smooth shallow ribbed dome, copper-tan coating, concentric seam rings, small central cap (ortho, drones) | Rebuilt: spherical cap, 192/96/48/24 standing-seam ribs, 4 seam rings, small cap |
| 3 | Fascia | Grey concrete compression ring | Deep bronze/copper-tan fascia band with two reveal lines | Rebuilt as flared fascia band in sampled colour |
| 4 | East / north wing massing | SDAC only north of y≈63 m; east side a 4.6 m low roof; gap between SDAC and arena | Continuous ≈13–14 m brick wing along Northwestern Ave from the SE tip to the rounded north end, hugging the drum (ortho + drones) | Rebuilt from lean-corrected orthophoto trace at 14.0 m |
| 5 | East entrance | None on east; north glass pavilion with revolving doors | Recessed east entrance on Northwestern Ave with MACKEY ARENA banner and 44 / 59 pier banners; flanking glazed P towers (drone_05) | Added recess with three portals, doors, banner panel + lettering, pier banners, two flanking towers |
| 6 | Glass P towers / penthouses | Two small rooftop boxes | Four glazed tower/penthouse boxes, Purdue P on east faces (ortho, drone_01/05) | Added four towers (full-height glass on outward face) with gold P |
| 7 | SW entrance | Not modelled | Recessed SW entrance with piers, soffit and lettering (2016_02, drone_04) | Added |
| 8 | Concourse ring | Low wall only on parts; jagged traced additions | Continuous one-storey brick ring with water table and limestone stripes (S/SW/W) | Rebuilt as continuous ring + south block + west annex |
| 9 | Wing windows | Uniform grid | Storefront ground floor; alternating single/paired upper windows; SDAC third tier; attic bands on SE block | Rhythm-based openings with recesses, frames, bands |
| 10 | SDAC curved lobby | Present at east end of south face | Curved glass lobby at SDAC SW corner facing Weist Plaza (HNTB-2, ortho) | Moved: faceted two-storey glass at the SW corner |
| 11 | Colours | Grey dome, saturated red procedural brick, blue glass | Sampled: dome sRGB≈(217,195,172) sun; brick ≈(173,133,99) sun; limestone ≈(225,224,210) | Recalibrated base colours; render-sampled brick (164,127,104) vs photo (173,133,99) |
| 12 | Site props | Weist Plaza deck, seatwalls, benches, statue inside the true wing footprint | Plaza lies west of the SDAC | Furniture removed (positions unverified); statue + Pyramid of Success moved onto plaza (estimated) |

## Discrepancies found in r2 before the r3 edit (r2 renders + matched views vs sources)

| # | Feature | r2 state | Evidence | r3 disposition |
| --- | --- | --- | --- | --- |
| A | Drum height / fascia | Fascia 2.1 m (10.1–12.2), drum 5.7 m (drum : chord 0.69), louvres end at 8.45 m | Fascia : channel : louvre 0.31:0.37:1 (2025 west aerial) and 0.26:0.38:1 (drone_04); reviewer drum : chord 0.79–0.80 | Fascia underside 10.95 m, louvres 4.75–9.25 m, slot width 0.62 m |
| B | Drum brick / fascia / louvre / limestone colour | Render drum brick 194,152,119; fascia 214,171,111 (too saturated); louvre 156,156,147; limestone 230,223,203 | 2016_02 medians 173,133,99 / 188,158,112 / 150,146,132 / 224,212,188 | Separate drum brick and corrected base colours (render now 177,137,107 / 184,155,109 / 152,148,137 / 224,213,188) |
| C | East entrance composition | 3 portals; one banner across nearly the whole curve; 44 / 59 on narrow end piers | drone_05 close crop: 4 portals; 44 and 59 on their own wall segments; vertical banners on end and blade piers | Recomposed |
| D | SDAC curved lobby | In the notch between the SDAC and the drum, invisible from the plaza; plaza-facing bend was brick | hntb_Purdue-2 order (SDAC → lobby → return → drum); ortho convex roof edge at y ≈ 59–74 m | Lobby moved to the bend; return rebuilt as banded brick with a glazed slot |
| E | Evidence | 2025 west aerial and LiDAR NDHM used but not saved or indexed | — | Saved in `sources/`, indexed |

## Missing / weak evidence (searched, not found)

- No saved close photo of the SDAC rounded north end or the north half of the east facade in daylight.
- Drum north/east bays largely hidden; pattern assumed from S/SW.
- No measured heights; all heights are photo estimates (see `change_log.md`).
