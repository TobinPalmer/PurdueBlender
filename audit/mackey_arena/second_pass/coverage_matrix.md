# Mackey Arena — facade coverage matrix (reference date: current exterior, 2023–2025)

Legend: **O** observed in at least one current photo/aerial · **E** estimated from oblique/partial evidence · **C** conflicting or era-dependent · **U** unseen.

| Element / facade | Sources (see `reference_index.json`) | Status | Notes |
| --- | --- | --- | --- |
| Dome form, ribbing, concentric seams, central cap | ortho 2023, drone_01/03/04/05, 2016_01/02, WJE, 2025 west aerial, LiDAR NDHM | O | Profile measured by LiDAR (apex 24.7 m, cap 26.0 m; r2). Rib/seam counts estimated from aerials. |
| Dome / fascia colour | 2016_01/02 (sun), drone_05 (overcast) | O / C | Copper-tan coating; hue varies with light (sunlit peach-tan vs overcast mauve-tan). 2009 photo shows earlier silver roof (pre-recoat) — not used. West aerial has a sunset cast — not used for colour. |
| Heights (ring roof, coping, fascia top, wing, penthouses, annex) | LiDAR NDHM 2018 (`sources/mackey_ndhm_2018.*`) | O (measured ±0.3-0.5 m) | Fascia underside / louvre heights are photo ratios fitted between LiDAR levels (`drum_heights_r3.py`). |
| Drum south / south-west / west / north-west | 2016_02, drone_04, 2025 west aerial, MackeyA (2009) | O (counts E) | 36 pilaster bays (10°) from the 2025 west aerial (15 pilasters visible); 5 louvre slots per slotted bay; slotted/plain pattern (2 : 1) observed S/SW/W/NW, assumed N/E. |
| Drum north | hntb_Purdue-2 (partial, behind lobby), MackeyA | E | Bays above north entrance seen with slots; exact pattern unverified. |
| Drum east | drone_01/05 (above wing roof only) | E | Only upper drum visible above the wing; slots partly seen. |
| Concourse ring S/SW/W (one storey) | 2016_02, drone_04, ortho | O | Water table, two thin limestone stripes, coping; height ≈5.8 m estimated. |
| SW (Morgan & Kate Burke) entrance | 2016_02, drone_04 | O (dims E) | Recessed glazed doors under limestone soffit, brick piers, dark letters MACKEY ARENA + sub-line. Arc span ≈26° estimated. |
| North entrance (Weist Plaza) | hntb_Purdue-2 (distant) | E | Storefront glazing with lettering; widths estimated. |
| West annex | ortho, drone_04 (edge), 2025 west aerial, LiDAR | O (west face) / E (N, S faces) | West face window groups (4 / 4 / 2 / 2 high) and door observed in the 2025 west aerial; overhanging white roof slab. |
| South block (low roof between ring and SE wing) | ortho, drone_01 | O (facade E) | South-face openings largely unseen at close range. |
| East wing — Northwestern Ave facade | drone_02/03/05, 2016_01 | O (rhythm E) | Two window tiers + attic bands; glass P towers; recessed east entrance with banner MACKEY ARENA / HOME OF PURDUE BASKETBALL and 44 / 59 pier banners (2025 signage). Bay pitch ≈4.3 m estimated. |
| East wing — SE block south & SW faces | 2016_01, drone_01 | O | Same vocabulary; window counts approximated by rhythm. |
| SDAC north wing — west (plaza) facade | hntb_Purdue-2, ortho | O (counts E) | Storefront + one tier of tall single/paired upper windows. |
| SDAC curved glass lobby | hntb_Purdue-2, ortho 2023 (roof edge) | O (plan radius E) | r3: on the convex plan bend facing the plaza (R ≈ 20 m, 40° turn); two storeys, mullion grid, slab band, deep metal fascia. |
| SDAC west-facing return between lobby and drum (x ≈ 17.3 m) | hntb_Purdue-2 (grazing) | E | Banded brick, recessed full-height glazed slot at the drum end; window positions estimated. |
| East entrance (2025 banner state) | drone_05 (close crop), drone_01 | O (widths E) | r3: four portals; 44 / MACKEY ARENA / 59 banners on separate wall segments; vertical banners on end and blade piers. 2016_01 shows the earlier curved glass bay (superseded). |
| SDAC north end (rounded) | ortho | O (plan) / U (facade) | Facade detail of the rounded north end not seen in any saved photo. |
| SDAC east facade north of y≈65 m | drone_03 (distant, dusk) | E | Same rhythm assumed. |
| Roof plan of wing (penthouses, units) | ortho | O | Four glazed penthouse/tower boxes; a few rooftop units. |
| Brees Center (NW) / Lambert Fieldhouse (S) | — | out of scope | Separate assets; not modelled here. |

## Viewpoint coverage log (r3)

| Source | Face(s) / features | Camera position / direction | Height / distance (approx.) | Perspective | Date | Limits |
| --- | --- | --- | --- | --- | --- | --- |
| 2016_02 | Drum S/SW, concourse ring, SW entrance | Geotag (-55.5, -73.8) local; fitted 90-95 m from drum centre on that bearing; looking NNE | Eye level, ~35-40 m to the concourse wall | Frontal-oblique | 2016-08 | Panorama; drum base hidden by the coping |
| 2016_01 | SE tip, east wing south half, drum SE | Geotag (85.6, -81.9); looking NW | Eye level, ~50 m | Oblique | 2016-11 | 2016 signage and east bay (superseded) |
| drone_04 | Drum SW bays, SW entrance, concourse ring | ~(-110, -150), looking NE | ~40 m high, ~130 m | Elevated oblique | 2025-01 dusk | Dark; colour unusable |
| drone_05 | East entrance, P towers, east wing, roof | ~(140, -70), looking W | ~50 m high, ~120 m | Elevated oblique | 2025-01 overcast | Tilt-shift blur at the edges |
| drone_01 / 03 | SE wing, south block / east wing length | From SE / from S along Northwestern Ave | Elevated | Oblique | 2025-01 | Distant for the north half |
| hntb_Purdue-2 | SDAC west facade, lobby, north entrance | Weist Plaza ~(15, 125), looking S | Eye level, 60-100 m | Oblique | c.2012 dusk | Lit interiors; return face at a grazing angle |
| 2025 west aerial | Drum W/SW/NW bays, west annex west face, concourse ring | ~135-165 m W of the drum, looking E | ~30-35 m high | Elevated, frontal to the west | 2025 summer sunset | Warm colour cast |
| MackeyA | Drum NW (pre-2011) | NW roof, looking SE | Elevated, ~80 m | Oblique | 2009 | Historic; drum rhythm only |
| ortho 2023 | Whole roof plan | Nadir | — | Top | 2023 | Relief displacement corrected approx. |
| LiDAR NDHM | All heights / footprints | Nadir | — | Top | 2018 | 1.5 m cells |

**Missing (not found in the r1/r2 searches; r3 did no new web search):** current daylight views of the rounded SDAC north end, the north half of the east facade at street level, the drum north/east bays at close range, and the south faces of the south blocks. These remain estimated.
